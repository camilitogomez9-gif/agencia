# SYS F6 — Setup ManyChat + n8n (Integración productiva)

**Status:** guía de implementación lean · vigente desde 2026-06-02
**Aplica:** [ManyChat Standard interno 2026](../../../_core/standards/manychat-integration-pattern.md)
**Reemplaza:** patrón legacy `parte1/2/3 + respuesta_definitiva` con Bearer hardcoded.

> **Principio lean:** solo se crean fields, flows y nodos que **realmente se escriben o se leen**. Lo opcional se agrega cuando aparece la necesidad real.

---

## Resumen de cambios v0.2 → v0.3

**ManyChat:**
- Crear 4 custom fields (los del bot): `ai_msg_1`, `ai_msg_2`, `ai_msg_3`, `ai_msg_count`
- Crear 2 flows: `[LA AGENCIA] Default Reply` + `[LA AGENCIA] Responder Multi-Parte`
- Archivar campos legacy: `parte1`, `parte2`, `parte3`, `respuesta_definitiva`

**n8n:**
- Cambiar 2 Code nodes (`Normalize Payload`, `Split Respuesta`) para alinear con el nuevo contrato de payload
- Agregar 2 HTTP Request nodes (`setCustomFields`, `sendFlow`) usando credential `ManyChat - SYS`
- Cambiar el Respond final a 200 vacío

**Fuera de scope (por lean):** Flow C "Fallback Humano" (no aplica al modelo SYS — escalamiento real va por tool `notificar_lead`), campos `ai_last_intent`/`session_*`/`lead_phone`/`lead_company`/`meta_last_tool` (cruft sin escritor ni lector), `ai_should_escalate` (sin Flow C, sin uso).

---

## Pre-requisitos

- [x] `sys-agente-principal-v0.2` activo en n8n con 10 tools
- [x] System prompt v2.2 cargado en el AI Agent
- [x] Smoke tests con curl pasados (tools + memoria + log a `sys_tool_calls`)
- [ ] Acceso admin a la cuenta ManyChat de Sistemas y Soluciones (Page ID anotado)
- [ ] API Key de ManyChat obtenida (Settings → API → Generate) y guardada en `06_docs/manychat-credentials.md` (gitignored)
- [ ] Canal a conectar definido (WA / IG / FB) — recomendado arrancar por WA

---

## Fase 1 — ManyChat (custom fields + flows)

### 1.1. Crear los 4 custom fields

En **Settings → Custom Fields → +Add**:

| Campo | Tipo | Default | Quién escribe | Quién lee |
|---|---|---|---|---|
| `ai_msg_1` | Text | (vacío) | n8n (setCustomFields) | Flow B (Send Message) |
| `ai_msg_2` | Text | (vacío) | n8n | Flow B (condicional) |
| `ai_msg_3` | Text | (vacío) | n8n | Flow B (condicional) |
| `ai_msg_count` | Number | 0 | n8n | Flow B (Conditions ≥2 y ≥3) |

> Snake_case exacto, sin acentos. ManyChat es case-sensitive en algunas referencias.

### 1.2. Flow A — `[LA AGENCIA] Default Reply`

Trigger: Default Reply del canal (por ahora WA — IG/FB después, ver sección 1.5).

**Paso 1 — Action: External Request**

- **Method:** POST
- **URL:** `https://[TU-INSTANCIA-N8N]/webhook/sys-agent`
- **Headers:**
  - `Authorization: Bearer {TOKEN_LITERAL}` ← token random que vos generás (ej. `openssl rand -hex 24`). Pegarlo literal acá Y en la credential `Webhook SYS Inbound` en n8n (sección 2.2 opcional)
  - `Content-Type: application/json`
- **Body (JSON):**
  ```json
  {
    "subscriber_id": "{{Id de contacto}}",
    "channel": "wa",
    "first_name": "{{Nombre}}",
    "last_input_text": "{{Última entrada de texto}}"
  }
  ```
  - `subscriber_id` → picker System Fields → "Id de contacto"
  - `first_name` → picker System Fields → "Nombre"
  - `last_input_text` → picker System Fields → "Última entrada de texto"
  - `channel` → **literal** `"wa"` (ManyChat no expone channel como system field; hardcodear per-flow)
- **Response mapping:** vacío (no usamos respuesta sync; n8n continúa vía `sendFlow`)

**Paso 2 — Continue** (sin enviar nada; n8n dispara el flow siguiente).

### 1.3. Flow B — `[LA AGENCIA] Responder Multi-Parte`

Trigger: External (lo dispara n8n vía `sendFlow`).

**Pasos:**
1. **Send Message:** `{{cuf ai_msg_1}}`
2. **Action → Typing:** 1.5s
3. **Condition:** `{{cuf ai_msg_count}}` ≥ 2
   - Branch true → Send Message `{{cuf ai_msg_2}}` → Typing 1.5s → continuar
   - Branch false → END
4. **Condition:** `{{cuf ai_msg_count}}` ≥ 3
   - Branch true → Send Message `{{cuf ai_msg_3}}` → Typing 1.5s
   - Branch false → END

Después de crear, anotar el **flow_ns** desde Settings → API → Flows. Formato: `content::responder_multi_parte_XXXXXX`.

### 1.4. Archivar campos legacy

Settings → Custom Fields → archivar (no borrar):
- `parte1`, `parte2`, `parte3`, `respuesta_definitiva`

> No los borres todavía. Si rompe algo, restaurar = 1 click. Borrar definitivo en 30 días.

### 1.5. Otros canales (después de validar WA)

Cuando se conecten IG y FB:
- Duplicar Flow A (`[LA AGENCIA] Default Reply WA` → `... IG` / `... FB`)
- Cambiar el literal `"channel": "wa"` por `"ig"` / `"fb"`
- Setear como Default Reply del canal correspondiente

Flow B se comparte entre los 3 canales — no requiere duplicar.

---

## Fase 2 — n8n (workflow v0.3)

### 2.1. Crear credential `ManyChat - SYS`

n8n → **Credentials → +Add → HTTP Header Auth**:
- Name: `ManyChat - SYS`
- Header name: `Authorization`
- Header value: `Bearer {PAGE_ID}:{API_KEY}` ← pegar el Bearer literal completo

Test: `GET https://api.manychat.com/fb/page/getInfo` con esta credential debe devolver page info.

### 2.2. (Opcional) Credential `Webhook SYS Inbound`

Si querés validar que solo ManyChat llame al webhook:
- Name: `Webhook SYS Inbound`
- Header name: `Authorization`
- Header value: `Bearer {TOKEN_LITERAL}` ← el mismo que pegaste en headers del Flow A

Si lo activás, configurar el nodo Webhook (sección 2.3.A) con auth.

### 2.3. Modificar el workflow

Duplicar `sys-agente-principal-v0.2` → renombrar a `v0.3`.

#### A. Nodo `Normalize Payload` (Code JS) — REEMPLAZAR el código

```javascript
// Alinea con el contrato de Flow A (sección 1.2).
// Payload esperado: { subscriber_id, channel, first_name, last_input_text }

const body = $input.first().json.body || $input.first().json;

const channel = (body.channel || 'test').toLowerCase();     // 'wa' | 'ig' | 'fb' | 'test'
const subId = String(body.subscriber_id || body.from || 'anon');
const sessionKey = `${channel}_${subId}`;                   // sessionKey para memoria Postgres
const mensajeActual = String(body.last_input_text || body.mensaje || body.text || '').trim();

if (!mensajeActual) {
  return [{ json: { skip: true, reason: 'empty_message' } }];
}

const canalLabel = channel === 'wa' ? 'WhatsApp'
                 : channel === 'ig' ? 'Instagram'
                 : channel === 'fb' ? 'Facebook'
                 : 'Test';

return [{
  json: {
    skip: false,
    channel,
    canalLabel,
    subId,
    sessionKey,
    mensajeActual,
    firstName: body.first_name || '',
    timestamp: body.timestamp || new Date().toISOString()
  }
}];
```

Si el nodo `Postgres Chat Memory` referencia `leadIdentifier`, cambiar a `sessionKey` (rename consistente).

#### B. Nodo `Split Respuesta` (Code JS) — REEMPLAZAR el código

```javascript
// ManyChat Standard interno 2026 — naming ai_msg_*
const output = $input.first().json.output || '';
const partes = output.split(/^---\s*$/m)
                     .map(p => p.trim())
                     .filter(p => p.length > 0);

const [ai_msg_1 = '', ai_msg_2 = '', ai_msg_3 = ''] = partes.slice(0, 3);
const ai_msg_count = Math.min(partes.length, 3);

return [{
  json: {
    raw: output,
    ai_msg_1,
    ai_msg_2,
    ai_msg_3,
    ai_msg_count,
    subscriber_id: $('Normalize Payload').first().json.subId
  }
}];
```

#### C. Agregar nodo `setCustomFields ManyChat` (HTTP Request)

Posición: después de `Split Respuesta`, antes del Respond final.

- **Method:** POST
- **URL:** `https://api.manychat.com/fb/subscriber/setCustomFields`
- **Authentication:** Generic Credential Type → HTTP Header Auth → `ManyChat - SYS`
- **Send Body:** ON · Body Type: JSON · Specify Body: Using JSON
- **JSON:**
  ```
  ={{ JSON.stringify({
    subscriber_id: $json.subscriber_id,
    fields: [
      { field_name: "ai_msg_1", field_value: $json.ai_msg_1 },
      { field_name: "ai_msg_2", field_value: $json.ai_msg_2 || null },
      { field_name: "ai_msg_3", field_value: $json.ai_msg_3 || null },
      { field_name: "ai_msg_count", field_value: $json.ai_msg_count }
    ]
  }) }}
  ```
  > ⚠️ **Importante:**
  > - `ai_msg_2`/`ai_msg_3` con `|| null` — ManyChat API rechaza string vacío `""` en fields tipo Text con error `400 Field[N] with invalid value`. Usar `null` para limpiar.
  > - `ai_msg_count` se envía como **número** (sin `String(...)`) porque está declarado tipo Number en ManyChat.
- **Settings → On Error:** Continue (Using Error Output)

#### D. Agregar nodo `sendFlow ManyChat` (HTTP Request)

Posición: después de `setCustomFields`.

- **Method:** POST
- **URL:** `https://api.manychat.com/fb/sending/sendFlow`
- **Authentication:** misma credential `ManyChat - SYS`
- **Send Body:** ON · Body Type: JSON
- **JSON:**
  ```
  ={{ JSON.stringify({
    subscriber_id: $('Split Respuesta').first().json.subscriber_id,
    flow_ns: "content::responder_multi_parte_XXXXXX"
  }) }}
  ```
  > Reemplazar `XXXXXX` con el flow_ns real anotado en 1.3.
- **Settings → On Error:** Continue

#### E. Nodo `Respond to Webhook` final

- **Respond With:** Text
- **Response Body:** vacío (o `{}`)
- **Response Code:** 200

ManyChat ignora el body de la respuesta sincrónica — solo le importa el `200 OK`.

#### F. Conexiones

```
Webhook → Normalize Payload → IF skip?
  IF skip? (true)  → Respond Skip
  IF skip? (false) → Build User Message Context → AI Agent → Split Respuesta
                                                              → setCustomFields → sendFlow → Respond to Webhook
```

### 2.4. Guardar

Path: `clients/SYS_SistemasYSoluciones/03_workflows/sys-agente-principal-v0.3.json`

---

## Fase 3 — Conectar canal WA en ManyChat

1. Settings → Channels → WhatsApp → conectar el número WA Business.
2. Verificar template inicial (mensaje de bienvenida 24h).
3. Settings → Default Reply → seleccionar `[LA AGENCIA] Default Reply` (el Flow A creado en 1.2).
4. Smoke ping: mandar mensaje al número desde un WA personal de prueba → debe llegar al webhook n8n (verificable en n8n executions).

---

## Fase 4 — Smoke tests E2E

Pre-condición: `v0.3` activo en n8n, `v0.2` desactivado.

| # | Test | Acción | Esperado | Verificación |
|---|---|---|---|---|
| 1 | **Respuesta 1 parte** | Mandar "Hola" desde WA real | Bot responde 1 mensaje con typing visible | En ManyChat Live Chat: `ai_msg_1` lleno, `ai_msg_2`/`ai_msg_3` vacíos, `ai_msg_count=1` |
| 2 | **Respuesta 3 partes** | Mandar: "Soy de una imprenta chica, qué equipo me recomendás para arrancar?" | Bot responde 3 mensajes secuenciales con delays | `ai_msg_count=3`, los 3 fields llenos |
| 3 | **Tool calling** | Mandar: "Cuánto sale la HUENU FT1604?" | Bot responde con precio de Airtable | Fila nueva en Postgres `sys_tool_calls` con `tool_name=buscar_equipo` |
| 4 | **Captura email (Tool 10)** | Llegar al cierre, mandar: "mi mail es prueba@test.com" | Bot confirma y agradece | Fila nueva en Google Sheet "SYS - Leads (Captura Emails)" con el mail |
| 5 | **Memoria cross-turn** | Turno 1: "Soy Juan de Imprenta Sol". Turno 2: "Te acordás cómo me llamo?" | Turno 2 menciona "Juan" | Tabla Postgres `n8n_chat_histories` tiene 4 filas con `session_id=wa_XXXX` |
| 6 | **Notificación lead** | Llegar a derivación con los 4 datos (nombre + tel + ubicación + equipo) | Bot confirma derivación y cierra con calidez | Mail recibido en `info@sistemasysoluciones.com` + Telegram al el equipo + fila en `sys_tool_calls` con `tool_name=notificar_lead` |

> Test 6 (escalamiento via Flow C) **eliminado** — no aplica al modelo SYS. El "escalamiento real" es la tool `notificar_lead`, cubierto por el test 6 nuevo.

---

## Fase 5 — Activación productiva

- [ ] Activar `sys-agente-principal-v0.3` (toggle Active = ON)
- [ ] Desactivar `v0.2` (mantener como backup importable)
- [ ] Verificar en ManyChat que WA tiene Default Reply → Flow A
- [ ] 1 hora de monitoring intensivo: revisar `n8n executions` + `sys_tool_calls` + `sys_messages` cada 10 min
- [ ] Avisar al Gerente Sistemas y Soluciones que el agente está vivo en WA
- [ ] `/sync-status-cliente-3-docs SYS` → marcar `F6 ✅ · WA en producción` (IG/FB pendientes)

---

## Rollback

1. Toggle `v0.3` Active = OFF en n8n.
2. Toggle `v0.2` Active = ON.
3. (Opcional) ManyChat Default Reply WA → cambiar temporalmente a "Send Message: Estamos atendiendo manualmente, te respondemos en breve" — solo si el problema afecta UX del lead.
4. Investigar logs en n8n executions + ManyChat API errors en los 2 nodos HTTP.

---

## Errores comunes

| Error | Causa | Fix |
|---|---|---|
| ManyChat API responde `401 Unauthorized` | Bearer mal formado en credential | Verificar formato `{PAGE_ID}:{API_KEY}` |
| `400 - Field[N] with invalid value` en setCustomFields | String vacío `""` en field Text (ManyChat lo rechaza) | Usar `|| null` para vaciar; o construir array dinámicamente solo con fields no-vacíos |
| `400 - invalid value` en `ai_msg_count` | Enviado como string `"2"` cuando el field es Number | Sacar el `String(...)` y enviar el número raw |
| `flow_ns invalid` en sendFlow | ID del flow mal copiado | Re-copiar desde Settings → API → Flows |
| Subscriber recibe `{{cuf ai_msg_1}}` literal | Campo no existe en ManyChat o se usó nombre incorrecto | Verificar nombre exacto en Settings → Custom Fields |
| Solo llega `ai_msg_1`, ignora `ai_msg_2/3` | Flow B sin Condition correcta | Revisar Conditions ≥2 y ≥3 en Flow B |
| Webhook responde pero ManyChat no entrega mensaje | `setCustomFields` o `sendFlow` falló silenciosamente (Continue on Fail) | Ver execution en n8n → revisar branch de error de los 2 nodos HTTP |
| Mensaje del lead llega vacío a n8n | `last_input_text` mapeado al campo equivocado en Flow A | Volver al picker, elegir System Field "Última entrada de texto" |
| Webhook responde `400 empty_message` | `last_input_text` vacío o no enviado | Inspeccionar el JSON del External Request en ManyChat |

---

## Próximos pasos post-F6

- F7: ejecutar `testing-guide-v6.md` completo (18 casos simples + 16 flujos)
- F8: producción + onboarding Edgardo + runbook final + GO-LIVE
- IG + FB: replicar Flow A con `"channel": "ig"` / `"fb"` cuando los canales estén conectados (sección 1.5)
- Si el rep quiere ver `lead_email` en el sidebar de Live Chat: agregar el campo a ManyChat + extender Tool 10 para escribirlo también ahí (no en scope inicial)

---

## Referencias

- [ManyChat Standard interno 2026](../../../_core/standards/manychat-integration-pattern.md)
- [Architecture v2 SYS](../02_architecture/architecture-v2-2026-05.md) — decisión #7
- [System prompt v2.2](../04_agents/agente-sistemasysoluciones-system-prompt.md)
- ManyChat API: https://api.manychat.com/swagger
