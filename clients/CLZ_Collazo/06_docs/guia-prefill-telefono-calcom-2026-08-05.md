# Guía — Prefill del teléfono en los links de cal.com

**Fecha:** 2026-08-05
**Workflow:** `[Collazo] Agente Principal v3` (`TcxaNLAZRfduShW7`, activo, 22 nodos)
**Estado:** ✅ **pasos 1 y 2 APLICADOS en n8n vivo** (2026-08-05 18:04, vía API).
🔸 **Falta el paso 3 (ManyChat)** — hasta hacerlo el cambio es inerte: `phone_e164`
llega `null` y los links salen igual que siempre.

> Verificado en producción: la ejecución `1323321` (18:04:23, posterior al deploy, canal
> `whatsapp`) pasó por los 2 nodos con status success y `phone_e164 = null`. 22 nodos,
> conexiones intactas, workflow sigue activo. Backup previo al cambio:
> `clz-main-PRE-prefill.json` en el scratchpad de la sesión.

---

## 1. Por qué

El selector de país del campo teléfono en cal.com aparece con **bandera de Brasil**. No es
configurable: cal.com lo resuelve en runtime llamando a su endpoint `public.countryCode`,
que geolocaliza por **IP del visitante**. Verificado — desde nuestra IP devuelve `BR`, y no
cambia mandando `Accept-Language: es-UY`.

Se probaron 3 propiedades plausibles en la API v2 (`defaultCountry`, `defaultCountryCode`,
`countryCode`): **la API responde 200 y las descarta en silencio**. No quedan persistidas.
Trampa fea — parece que funcionó y no hizo nada.

**Lo que sí funciona:** prellenar el número por query string. Verificado en la página real,
tanto en links del team como personales:

```
cal.com/team/collazo-servicio/instalacion-aire?attendeePhoneNumber=%2B59891046641
```

Con eso el campo abre con **+598 y bandera de Uruguay**. Como el teléfono ahora es
**obligatorio** en los 9 event types del team, además le ahorra al cliente tipearlo.

## 2. Dónde se injerta y por qué ahí

Cadena de salida del flujo vivo:

```
AI Agent → Code in JavaScript1 → Formatear mensaje → Build ManyChat Payload → setCustomFields → sendFlow
                (limpieza links)     (LLM: parte1/2/3)      ← ACÁ
```

Se hace en **`Build ManyChat Payload`**, no en el prompt ni en `Code in JavaScript1`:

- **No en el prompt**, porque el LLM tendría que armar una URL con parámetros y encoding.
  Es exactamente el tipo de cosa que ya falló con el markdown sucio.
- **No en `Code in JavaScript1`**, porque después pasa por `Formatear mensaje`, que es un
  **LLM** (gpt-4o-mini) que parte el texto en 3. Una URL larga con query string puede
  quedar cortada al medio. Si el prefill va después del splitter, el LLM nunca ve la URL larga.

## 3. Prerrequisito en ManyChat — 🔸 LO ÚNICO QUE FALTA

El payload actual **no trae el teléfono**. `Normalize Payload` hoy extrae `subscriber_id`,
`channel`, `last_input_text`, `first_name`, `session_key`, `has_audio` — nada más.

En ManyChat → flow **Default Reply** → nodo **External Request** → body JSON, agregar:

```json
"phone": "{{phone}}"
```

> ⚠️ Verificar el nombre real del campo para contactos de WhatsApp. Si ManyChat expone
> `{{whatsapp_phone}}`, el código lo contempla igual (lee `body.phone` y `body.whatsapp_phone`).

**Limitación conocida y aceptada:** en SYS se confirmó que ManyChat a veces manda el literal
`{{phone}}` sin renderizar, de forma intermitente e irresoluble del lado de ManyChat. El código
lo contempla: al quedarse solo con dígitos eso da vacío → `phone_e164 = null` → el link se manda
**sin prefill, intacto**. O sea, el peor caso es exactamente el comportamiento de hoy. Degrada solo.

**También por diseño:** los contactos de Instagram y Facebook no tienen teléfono. En esos
canales no hay prefill y el link sale como siempre. El beneficio es solo en WhatsApp.

## 4. Paso 1 — Nodo `Normalize Payload` ✅ aplicado

Código tal como quedó en el nodo vivo (queda acá como referencia y para rollback):

```javascript
// Normalize del payload entrante desde ManyChat External Request
// Patrón canónico (manychat-integration-pattern.md)
const body = $json.body || {};
const headers = $json.headers || {};

const subscriber_id = body.subscriber_id || body.id || headers.user_id || '';
const channel = body.channel || headers['x-channel'] || 'facebook';
const last_input_text = body.last_input_text || body.pregunta || headers.pregunta || '';
const first_name = body.first_name || headers.full_name || '';
const session_key = `${channel}_${subscriber_id}`;
const has_audio = last_input_text.includes('.ogg');

// Teléfono normalizado a E.164 uruguayo (null si no se puede resolver).
// Contempla el "0" de marcado local que ya nos mordió en el broadcast del 31/07
// (+598091046641 -> +59891046641) y el literal "{{phone}}" sin renderizar de ManyChat.
function aE164UY(raw) {
  let d = String(raw || '').replace(/\D/g, '');
  if (!d) return null;
  if (d.startsWith('598')) d = d.slice(3);   // saco código de país
  d = d.replace(/^0+/, '');                  // saco el 0 de marcado local
  if (d.length < 8 || d.length > 9) return null;
  return '+598' + d;
}
const phone_e164 = aE164UY(body.phone || body.whatsapp_phone || headers.phone || '');

return [{
  json: {
    subscriber_id,
    channel,
    last_input_text,
    first_name,
    session_key,
    has_audio,
    phone_e164,
    fecha_hora_montevideo: new Date().toLocaleString('es-UY', { timeZone: 'America/Montevideo' })
  }
}];
```

## 5. Paso 2 — Nodo `Build ManyChat Payload` ✅ aplicado

Código tal como quedó en el nodo vivo:

```javascript
// Toma las 3 partes y arma el payload canónico para ManyChat
// (manychat-integration-pattern.md §7)
const raw = $json.message?.content || $json.content || $json;
let parts = raw;
if (typeof raw === 'string') {
  try { parts = JSON.parse(raw); } catch (e) { parts = { parte1: raw, parte2: '', parte3: '' }; }
}

// Prefill del teléfono en los links de cal.com.
// El país del selector lo resuelve cal.com por IP del visitante (devuelve BR) y no hay
// setting para forzarlo; prellenando el número, el selector queda en UY.
// Va DESPUÉS del splitter para que el LLM nunca manipule la URL larga.
const tel = $('Normalize Payload').first().json.phone_e164;

function prefillCalcom(t) {
  if (!tel || !t) return t;
  return String(t).replace(
    /\b((?:https?:\/\/)?cal\.com\/[^\s<>()"']*[^\s<>()"'.,;:!?])/gi,
    (url) => /[?&]attendeePhoneNumber=/i.test(url) ? url
      : url + (url.includes('?') ? '&' : '?') +
        'attendeePhoneNumber=' + encodeURIComponent(tel)
  );
}

const msgs = [parts.parte1, parts.parte2, parts.parte3]
  .map(prefillCalcom)
  .filter(p => p && String(p).trim().length > 0);

const fields = [
  { field_name: 'ai_msg_count', field_value: msgs.length },   // ← número real, sin String()
  { field_name: 'ai_msg_1', field_value: msgs[0] || null },
  { field_name: 'ai_msg_2', field_value: msgs[1] || null },
  { field_name: 'ai_msg_3', field_value: msgs[2] || null }
];

const subscriber_id = $('Normalize Payload').first().json.subscriber_id;

return [{
  json: {
    subscriber_id,
    fields,
    next_flow: 'content20260629215149_084952'
  }
}];
```

## 6. Verificación

Validado con 14 casos en Node fuera de n8n (`test-nodos-clz.js`, 14/14), incluyendo:
teléfono con 0 de marcado local, literal `{{phone}}`, sin teléfono, link en cualquiera de las
3 partes, mensaje sin links, `ai_msg_count` sigue siendo number, y el fallback de string plano.

**Smoke en producción** (desde WhatsApp, con un número real):

| # | Qué mandar | Qué esperar |
|---|---|---|
| S1 | "quiero instalar un aire" | Llega el link con `?attendeePhoneNumber=%2B598...` al final |
| S2 | Abrir ese link y elegir horario | Campo teléfono con **bandera UY** y el número ya cargado |
| S3 | "hola" (sin pedir servicio) | Mensaje normal, sin parámetros raros |
| S4 | Lo mismo desde **Instagram** | Link sin parámetro (esperado: IG no tiene teléfono) |
| S5 | Completar una reserva de prueba | Llega a cal.com con teléfono y documento; borrarla después |

## 7. Rollback

Los dos nodos son Code puros, sin dependencias. Para revertir, sacar el bloque `aE164UY` +
`phone_e164` de `Normalize Payload` y el bloque `tel`/`prefillCalcom` + el `.map(prefillCalcom)`
de `Build ManyChat Payload`. Nada más los referencia.

El JSON del workflow tal como estaba antes del cambio quedó en el scratchpad de la sesión
(`clz-main-live.json`, export del 2026-08-05 17:31).

## 8. Contexto relacionado

Los 9 event types del team (`Collazo Servicio Técnico`, id `256131`) recibieron el mismo día la
réplica de los formularios de los eventos personales: campos por servicio, documento,
confirmación del costo de $750, **teléfono visible y obligatorio**, y `notes`/`guests` ocultos.
El prompt vivo ya entrega los 9 links del team.

Dos puntos abiertos de esa tanda:

- `desmontaje-de-calefon` y `desmontaje-instalacion-de-calefon` no tienen contraparte en los
  eventos personales. Se les asumió el set de calefón (marca, material, documento, confirmación).
  **Están en uso real** — el prompt los entrega.
- `mantenimiento-aire-acondicionado` pregunta *"cantidad de aires a **instalar**"*. Es un typo
  heredado del evento personal; se replicó tal cual en vez de corregirlo unilateralmente.
