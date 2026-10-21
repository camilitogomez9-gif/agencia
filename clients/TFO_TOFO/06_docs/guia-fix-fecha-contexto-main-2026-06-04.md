# Guía: agregar nodo `Fechas` al main workflow TFO (Patrón Napier)

**Fecha:** 2026-06-04
**Workflow vivo:** `Agente WEB B2B y RRSS` (50 nodos, `active: true` en n8n)
**Objetivo:** que el AI Agent reciba fechas pre-resueltas en zona horaria México (CDMX) y no calcule fechas relativas ("mañana", "próximo lunes") por su cuenta. Hoy el User Message del nodo `Agente de derivacion de Lead` pasa `Fecha de hoy: {{ $now }}` — `$now` es UTC en n8n por default, así que el agente está calculando fechas con drift de 6 horas respecto a México.

---

## Topología actual del main (verificada en el JSON vivo)

```
Webhook
  → Responder rápido ManyChat            (respondToWebhook — devuelve 200 a ManyChat ASAP)
  → Code in JavaScript                   (detecta canal: TikTok / WhatsApp / Instagram / Facebook)
  → Existe?                              (Airtable: busca contacto)
  → ¿Existe?                             (IF)
      ├─ NO → Crear contacto inicial → Separamos en partes
      └─ SÍ → Separamos en partes
              → Split Out
              → Get_Audio/s
              → Transcribir audio/s
              → Aggregate
              → Analizar imágen
              → Juntar mensajes          (Set: arma `Mensaje completo`)
              → Agente de derivacion de Lead   ← AI AGENT PRINCIPAL
                  → Humanizar respuesta
                  → Settear variables
                  → Elegir canal
                  → Enviar [WhatsApp | Instagram | Facebook | TikTok]
```

El AI Agent tiene como tools: `Agente de RRSS`, `Agente de B2B`, `Agente de Servicio al Cliente`, `Agente de Reposición`, `elevar_conversacion`, `audio`, `check_disponibilidad`, `codigo_reposicion`.

---

## ¿Por qué hace falta el nodo Fechas?

El User Message vigente del `Agente de derivacion de Lead` es (verbatim del JSON):

```
=Mensaje del usuario: "{{ $json['Mensaje completo'] }}"

Fecha de hoy: {{ $now }}
```

`$now` en n8n es un `DateTime` Luxon sin zone explícita. Cuando el modelo lee "Fecha de hoy: 2026-06-05T01:00:00.000Z" (UTC), un usuario que escribe "mañana" a las 19:00 CDMX del 2026-06-04 obtiene como "mañana" → 2026-06-05 hora UTC, lo que al pasar a `check_disponibilidad` como `2026-06-05T11:00:00` puede leerse como 11:00 UTC = 05:00 CDMX (5 horas antes). Patrón validado en NPR Napier: un Code node pre-calcula `fecha_contexto` en TZ del negocio y se inyecta al User Message.

---

## Edits a aplicar en `Agente WEB B2B y RRSS` (en n8n, en vivo)

### Edit 1 — Crear nodo `Fechas` (Code)

**Insertar entre `Juntar mensajes` y `Agente de derivacion de Lead`.**

**Tipo de nodo:** `n8n-nodes-base.code`
**Nombre:** `Fechas`
**Code (copy paste exacto):**

```javascript
// Pre-procesador de fechas — TFO TOFO Pizza (CDMX)
// Adaptado del patrón Napier; cambia solo el TZ.
const TZ = 'America/Mexico_City';
const now = new Date(new Date().toLocaleString('en-US', { timeZone: TZ }));
const pad = n => String(n).padStart(2, '0');
const toISO = d => `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`;
const dnames = ['domingo','lunes','martes','miercoles','jueves','viernes','sabado'];

const ctx = {
  hoy: toISO(now),
  manana: toISO(new Date(now.getFullYear(), now.getMonth(), now.getDate()+1)),
  pasado_manana: toISO(new Date(now.getFullYear(), now.getMonth(), now.getDate()+2)),
  dia_semana_hoy: dnames[now.getDay()],
  hora_actual: `${pad(now.getHours())}:${pad(now.getMinutes())}`,
  proximos_7_dias: {}
};

for (let i = 1; i <= 7; i++) {
  const d = new Date(now.getFullYear(), now.getMonth(), now.getDate() + i);
  const n = dnames[d.getDay()];
  if (!ctx.proximos_7_dias[n]) ctx.proximos_7_dias[n] = toISO(d);
}

return [{ json: { ...$input.first().json, fecha_contexto: ctx } }];
```

**Reconfigurar conexiones:**
- Cambiar la salida de `Juntar mensajes` para que apunte a `Fechas` (en lugar de directamente a `Agente de derivacion de Lead`).
- Conectar la salida de `Fechas` a la entrada `main` de `Agente de derivacion de Lead`.

---

### Edit 2 — Reemplazar el User Message del `Agente de derivacion de Lead`

**Valor actual del campo `text` del nodo `Agente de derivacion de Lead` (verbatim):**

```
=Mensaje del usuario: "{{ $json['Mensaje completo'] }}"

Fecha de hoy: {{ $now }}
```

**Reemplazar por:**

```
=Mensaje del usuario: "{{ $json['Mensaje completo'] }}"

# Contexto temporal (úsalo como fuente de verdad, no calcules fechas por tu cuenta)
- Hoy: {{ $json.fecha_contexto.hoy }} ({{ $json.fecha_contexto.dia_semana_hoy }})
- Mañana: {{ $json.fecha_contexto.manana }}
- Pasado mañana: {{ $json.fecha_contexto.pasado_manana }}
- Próximo lunes: {{ $json.fecha_contexto.proximos_7_dias.lunes }}
- Próximo martes: {{ $json.fecha_contexto.proximos_7_dias.martes }}
- Próximo miércoles: {{ $json.fecha_contexto.proximos_7_dias.miercoles }}
- Próximo jueves: {{ $json.fecha_contexto.proximos_7_dias.jueves }}
- Próximo viernes: {{ $json.fecha_contexto.proximos_7_dias.viernes }}
- Hora actual CDMX: {{ $json.fecha_contexto.hora_actual }}
- Zona horaria del negocio: America/Mexico_City (UTC-6)
```

**Nota:** las expresiones usan `$json.fecha_contexto.*` directamente (sin `$('Fechas').first().json...`) porque el nodo `Fechas` queda inmediatamente upstream y el campo `Mensaje completo` que ya estaba se preserva gracias al spread `...$input.first().json` en el Code.

---

### Edit 3 — Pasar `fecha_contexto` también al `Agente de B2B` (subagente)

El `Agente de B2B` es invocado como `agentTool` por el agente principal. Su campo `text` actual es:

```
={{ $json['Mensaje completo'] }}
```

**Reemplazar por:**

```
={{ $json['Mensaje completo'] }}

# Contexto temporal (úsalo cuando agendes citas)
- Hoy: {{ $json.fecha_contexto.hoy }} ({{ $json.fecha_contexto.dia_semana_hoy }})
- Próximo lunes: {{ $json.fecha_contexto.proximos_7_dias.lunes }}
- Próximo martes: {{ $json.fecha_contexto.proximos_7_dias.martes }}
- Próximo miércoles: {{ $json.fecha_contexto.proximos_7_dias.miercoles }}
- Próximo jueves: {{ $json.fecha_contexto.proximos_7_dias.jueves }}
- Próximo viernes: {{ $json.fecha_contexto.proximos_7_dias.viernes }}
- Hora actual CDMX: {{ $json.fecha_contexto.hora_actual }}
- TZ del negocio: America/Mexico_City (UTC-6)
```

Esto asegura que cuando el agente de derivación delega a B2B para agendar, B2B también tenga las fechas reales (no improvisadas por el modelo).

---

### Edit 4 — Cablear 3 inputs nuevos al `toolWorkflow check_disponibilidad`

**Estado actual del nodo `check_disponibilidad` (verbatim del JSON):**

```json
"workflowInputs": {
  "mappingMode": "defineBelow",
  "value": {
    "fecha_hora": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('fecha_hora', ``, 'string') }}",
    "nombre": "={{ $('Webhook').item.json.body.name }}"
  },
  "schema": [
    { "id": "fecha_hora", "type": "string", ... },
    { "id": "nombre", "type": "string", ... }
  ]
}
```

**Detalle a notar:** el `workflowId.value` sigue siendo `vpLmZ299yXJrOSBv` (id del v1 vivo). El `cachedResultName` ya dice `Chequear disponibilidad | Tofo v2` pero ese es solo el label cacheado del último click — **el toolWorkflow sigue ejecutando el v1**. Hay que cambiar el `value` al ID que asigne n8n al importar el v2 (ver `guia-fix-chequear-disponibilidad-2026-06-04.md` Paso 2 y 5).

**Cambiar `workflowInputs.value` a:**

```json
{
  "fecha_hora": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('fecha_hora', ``, 'string') }}",
  "nombre": "={{ $('Webhook').item.json.body.name }}",
  "subscriber_id": "={{ $('Webhook').item.json.body.id }}",
  "canal": "={{ $('Code in JavaScript').item.json.canal }}",
  "telefono": "={{ $('Webhook').item.json.body.whatsapp_phone || '' }}"
}
```

Y agregar 3 entries al `schema` del toolWorkflow (n8n los crea automáticamente al rellenar el form, pero si los pegás como JSON, deben estar todos):

```json
{ "id": "subscriber_id", "displayName": "subscriber_id", "type": "string", "required": false, "display": true, "canBeUsedToMatch": true, "removed": false },
{ "id": "canal", "displayName": "canal", "type": "string", "required": false, "display": true, "canBeUsedToMatch": true, "removed": false },
{ "id": "telefono", "displayName": "telefono", "type": "string", "required": false, "display": true, "canBeUsedToMatch": true, "removed": false }
```

**Por qué `Code in JavaScript`:** ese nodo (verbatim del JSON vivo) ya detecta el canal correctamente:

```javascript
let canal = 'Desconocido';
if (body?.tt_username) canal = 'TikTok';
else if (body?.whatsapp_phone) canal = 'WhatsApp';
else if (body?.ig_id) canal = 'Instagram';
else if (body?.fb_id) canal = 'Facebook';
return [{ json: { canal } }];
```

Reusamos ese output en lugar de re-implementar la lógica.

**`telefono`:** sólo existe si `whatsapp_phone` viene en el webhook (los otros canales no traen teléfono). Fallback a string vacío para no romper el sub-workflow v2 (que igual acepta string vacío gracias al validador JS).

---

### Edit 5 — Apuntar el `workflowId` al v2

Cuando hayas importado el sub-workflow v2 a n8n y validado los 8 tests (ver `guia-fix-chequear-disponibilidad-2026-06-04.md`):

- En el nodo `check_disponibilidad` del main, en `workflowId.value`, reemplazar `vpLmZ299yXJrOSBv` por el ID nuevo que asigne n8n al v2.
- Guardar.

---

## Verificación rápida

Después de aplicar Edits 1-4:

1. Mandá un mensaje al webhook desde ManyChat (o desde el panel de test de n8n) con un payload que incluya `whatsapp_phone`.
2. Ejecutá el workflow paso a paso.
3. En el nodo `Fechas`, verificá que el output incluya `fecha_contexto` con:
   - `hoy` = la fecha real de hoy en CDMX (no UTC).
   - `dia_semana_hoy` en español.
   - `hora_actual` = hora real CDMX (no UTC).
4. En el nodo `Agente de derivacion de Lead`, verificá en el panel "Logs" que el User Message contenga el bloque `# Contexto temporal` con valores poblados.
5. Forzá una pregunta tipo "Quiero agendar el próximo martes a las 11" y verificá que el agente B2B llame a `check_disponibilidad` con `fecha_hora` = el martes correcto en formato ISO con offset CDMX.

---

## Referencias

- [Nodo "Pre-procesador de fechas" en Napier](../../NPR_Napier/03_workflows/sub-admin-napier-v1.json) — patrón original, línea ~1923.
- [User Message con fecha_contexto en Napier](../../NPR_Napier/03_workflows/sub-admin-napier-v1.json) — línea ~703.
- [Guía del fix del sub-workflow v2](guia-fix-chequear-disponibilidad-2026-06-04.md).
- [Plan completo](/Users/camilo/.claude/plans/users-la agencia-downloads-chequear-disponibi-frolicking-crescent.md).
