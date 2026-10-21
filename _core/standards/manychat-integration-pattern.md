# ManyChat ↔ n8n Integration Pattern (Standard interno 2026)

Convención canónica para todos los agentes conversacionales que usan ManyChat como gateway multi-canal (IG / WA / FB) y n8n como motor de orquestación.

**Status:** vigente desde 2026-06-02 · validado en SYS F6.
**Reemplaza:** patrón legacy `parte1/2/3 + respuesta_definitiva` con Bearer hardcodeado (NVJ, CRZ, IMP heredados).

---

## 1. Principios

1. **Namespace en custom fields.** Cada campo declara su dueño con prefijo: `ai_*`, `lead_*`, `session_*`, `meta_*`. No mezclar.
2. **Auth via n8n Credential.** Nunca Bearer hardcodeado en nodos HTTP. Usar `HTTP Header Auth` credential `ManyChat - [CLIENTE]`.
3. **Cantidad de mensajes dinámica.** El bot decide cuántas partes (1 a N), no slots fijos.
4. **Cero lógica de negocio en ManyChat.** ManyChat es solo el canal de delivery. Toda decisión (escalamiento, dedup, routing) sucede en n8n.
5. **Estado persistente en Postgres, no en ManyChat.** Custom fields solo cachean datos para UX (live chat sidebar, segmentación). La verdad vive en Supabase.

---

## 2. Convención de naming de custom fields

| Prefijo | Dueño | Ejemplos | Uso |
|---|---|---|---|
| `ai_*` | n8n / AI Agent | `ai_msg_1`, `ai_msg_2`, `ai_msg_3`, `ai_msg_count`, `ai_last_intent`, `ai_should_escalate` | Output del agente para que ManyChat lo entregue |
| `lead_*` | n8n + tools | `lead_email`, `lead_phone`, `lead_company`, `lead_country`, `lead_first_seen` | Datos del lead capturados durante la conversación |
| `session_*` | n8n session state | `session_id`, `session_started_at`, `session_channel`, `session_turn_count` | Metadata de la conversación activa |
| `meta_*` | analítica / debugging | `meta_last_tool`, `meta_last_error`, `meta_model_version` | Debugging y observabilidad |

**Reglas:**
- Snake_case, inglés, minúsculas.
- Sin acentos ni caracteres especiales (rompe la API en algunos casos).
- Nombre descriptivo, no críptico (`ai_msg_1` mejor que `m1`).
- Tipos ManyChat: `Text` para strings, `Number` para counts, `Boolean` para flags, `Date` para timestamps.

---

## 3. Schema mínimo de fields por agente (lean by default)

**Regla cardinal:** no crear ningún campo que **no tenga un escritor Y un lector concretos** en el sistema. Cada field es overhead visual en el sidebar de Live Chat y deuda futura. Si dudás, no lo crees — agregarlo después cuesta 30 segundos.

### Núcleo obligatorio (4 fields)

Todo el agente tiene exactamente estos 4:

| Field | Tipo | Escritor | Lector |
|---|---|---|---|
| `ai_msg_1` | Text | n8n `setCustomFields` | Flow B Send Message |
| `ai_msg_2` | Text | n8n `setCustomFields` | Flow B condicional |
| `ai_msg_3` | Text | n8n `setCustomFields` | Flow B condicional |
| `ai_msg_count` | Number | n8n `setCustomFields` | Flow B Conditions (≥2, ≥3) |

### Agregar solo si hay caso de uso real

Cada uno requiere justificación concreta antes de crearse:

| Field | Tipo | Crear cuándo |
|---|---|---|
| `ai_should_escalate` | Boolean | Si existe Flow C "Fallback Humano" con asignación a live chat agent. Si el escalamiento real es invocar una tool (`notificar_lead`, etc.), NO crear este field. |
| `ai_last_intent` | Text | Si se usa para routing en flows ManyChat o para segmentación de audiencias. Si solo es debugging, NO crear (ya está en logs Postgres). |
| `session_id` | Text | Solo si n8n ESCRIBE este field activamente. Si el `sessionKey` se deriva de `${channel}_${subscriber_id}` en n8n, NO crear. |
| `session_channel` | Text | Solo si se usa para segmentación o routing en flows. Si el canal va en el payload del External Request, NO crear. |
| `lead_email` | Text | Cuando se quiere ver el mail en sidebar de Live Chat o usarlo para flows de re-engagement. Requiere que la tool que captura emails también escriba a ManyChat. |
| `lead_phone` / `lead_company` / `lead_country` | Text | Cuando alguna tool los persiste a ManyChat. Si solo viven en Postgres/Airtable, NO crear. |
| `meta_last_tool` | Text | Casi nunca. Postgres `tool_calls` cubre observabilidad. Crear solo si alguien va a leerlo desde sidebar. |

### Opcionales por agente (ejemplos reales)

- IMP: `audio_flow_id` para disparar audios pre-grabados (escritor: n8n, lector: Flow ManyChat que envía el audio)
- SYS: ninguno extra — los 4 del núcleo alcanzan
- TFO: `lead_business_model` (escritor: tool, lector: subagente B2B / RRSS)

### Anti-patrón: campos "por si acaso"

Si creás 12 fields esperando "usarlos algún día", lo que tenés es un sidebar visualmente saturado, custom fields que nadie actualiza (data stale = peor que data ausente) y deuda técnica que luego nadie limpia. **Empezá con 4. Crecé al agregar features reales.**

---

## 4. Flujo canónico (E2E)

```
[ManyChat: Default Reply Flow]
      │
      │ (1) External Request → POST n8n webhook
      │      Body: { subscriber_id, channel, last_input_text, session_id, ... }
      ▼
[n8n: sys-agente-principal-vX]
      │
      ├─ Webhook → Normalize → Load Session State
      ├─ AI Agent (con tools) → output JSON: { msgs: [...], escalate: bool, intent: str }
      ├─ Build ManyChat Payload (Code node — JSON.stringify, NO ternarios en string)
      │
      ├─ HTTP Request: setCustomFields
      │    URL: https://api.manychat.com/fb/subscriber/setCustomFields
      │    Auth: Credential "ManyChat - [CLIENTE]" (HTTP Header Auth)
      │    Body: { subscriber_id, fields: [ ...payload ] }
      │
      ├─ HTTP Request: sendFlow
      │    URL: https://api.manychat.com/fb/sending/sendFlow
      │    Auth: misma credential
      │    Body: { subscriber_id, flow_ns: "content::responder_multi_parte" }
      │
      └─ Respond to Webhook (200 OK, body vacío — ManyChat ignora el body)
      ▼
[ManyChat: Flow "Responder Multi-Parte"]
      │
      ├─ Send Message: {{ai_msg_1}}        ← typing delay 1.5s
      ├─ Condition: {{ai_msg_count}} >= 2
      │     └─ Send Message: {{ai_msg_2}}  ← typing delay 1.5s
      ├─ Condition: {{ai_msg_count}} >= 3
      │     └─ Send Message: {{ai_msg_3}}  ← typing delay 1.5s
      └─ END
```

---

## 5. Setup ManyChat — flows

Todo el agente tiene **mínimo 2 flows obligatorios**. Flow C es opcional según modelo de escalamiento.

### 5.1. `[LA AGENCIA] Default Reply` (entry point)
- **Trigger:** Default Reply (cuando el lead manda mensaje y no matchea nada).
- **Acciones:**
  1. External Request → POST n8n webhook (Bearer Auth header)
  2. Continue (no enviar nada — n8n triggea el siguiente flow)
- **Custom fields que pasa al webhook:** `id`, `name`, `last_input_text`, `live_chat_url`, todos los `session_*` y `lead_*` actuales.

### 5.2. `[LA AGENCIA] Responder Multi-Parte` (delivery)
- **Trigger:** External (disparado por `sendFlow` desde n8n).
- **Acciones:**
  1. Send Message `{{cuf_ai_msg_1}}` + typing delay 1.5s
  2. IF `{{cuf_ai_msg_count}}` ≥ 2 → Send `{{cuf_ai_msg_2}}` + delay 1.5s
  3. IF `{{cuf_ai_msg_count}}` ≥ 3 → Send `{{cuf_ai_msg_3}}` + delay 1.5s
- **Importante:** typing delays se configuran en el nodo "Typing", no en el Send Message.

### 5.3. (Opcional) `[LA AGENCIA] Fallback Humano`

**Crear solo si** el modelo del cliente requiere handoff a un live chat agent dentro de ManyChat. **No crear si** el escalamiento real ya está cubierto por una tool de n8n (`notificar_lead`, `escalar_a_humano`, etc.) que notifica al equipo por mail/Telegram/Slack y el agente IA sigue manejando la conversación con calidez de cierre.

- **Trigger:** External (`sendFlow` desde n8n cuando `ai_should_escalate=true`).
- **Pre-requisito:** crear el field `ai_should_escalate` (Boolean) Y declarar en este flow cualquier custom field que se setee (ej. si vas a setear `session_status`, declararlo primero en Settings → Custom Fields).
- **Acciones típicas:**
  1. Send Message "Te paso con alguien del equipo, en breve te responde."
  2. Add Tag (ej. `ESCALATED_TO_HUMAN`)
  3. (opcional) Live Chat Assignee → asignar al rep correspondiente
  4. (opcional) Set custom fields adicionales — solo los previamente declarados

---

## 6. Setup n8n — credentials

**Una credential `HTTP Header Auth` por cliente:**

- Name: `ManyChat - [CLIENTE]` (ej. `ManyChat - SYS`)
- Header name: `Authorization`
- Header value: `Bearer {{PAGE_ID}}:{{API_KEY}}` ← se setea una vez, se referencia desde todos los nodos HTTP Request.

**Nunca** poner el Bearer literal en el body o en headers inline del nodo. Si rota la key del cliente, se cambia una sola vez en la credential.

---

## 7. Patrón del Code node `Build ManyChat Payload`

Ejemplo canónico (reemplaza los ternarios concatenados en string del patrón legacy):

```javascript
// Input: $json.output del AI Agent — { msgs: ["...", "...", "..."], escalate: false }
const output = $json.output || $json.message?.content || {};
const msgs = Array.isArray(output.msgs)
  ? output.msgs
  : [output.parte1, output.parte2, output.parte3].filter(Boolean);

const fields = [
  { field_name: 'ai_msg_count', field_value: String(msgs.length) },
  { field_name: 'ai_msg_1', field_value: msgs[0] || '' },
  { field_name: 'ai_msg_2', field_value: msgs[1] || '' },
  { field_name: 'ai_msg_3', field_value: msgs[2] || '' },
];

if (output.intent) {
  fields.push({ field_name: 'ai_last_intent', field_value: output.intent });
}
if (output.escalate === true) {
  fields.push({ field_name: 'ai_should_escalate', field_value: 'true' });
}

return {
  subscriber_id: $('Webhook').first().json.body.id,
  fields,
  next_flow: output.escalate ? 'content::fallback_humano' : 'content::responder_multi_parte',
};
```

Luego en el nodo HTTP Request `setCustomFields`:
```
Body Type: JSON
JSON: ={{ { subscriber_id: $json.subscriber_id, fields: $json.fields } }}
```

Y en `sendFlow`:
```
JSON: ={{ { subscriber_id: $json.subscriber_id, flow_ns: $json.next_flow } }}
```

---

## 8. Anti-patrones a evitar

| ❌ Antipatrón | ✅ Patrón correcto |
|---|---|
| Enviar string vacío `""` en custom fields tipo Text | Enviar `null` para vaciar (ManyChat API responde `400 Field[N] with invalid value` con `""`) |
| Enviar `String(numero)` a un field tipo Number | Enviar el número raw — ManyChat valida el tipo del field |
| Bearer hardcodeado en cada nodo HTTP | n8n Credential `HTTP Header Auth` reutilizada |
| `parte1`, `parte2`, `respuesta_definitiva` (sin prefijo) | `ai_msg_1`, `ai_msg_2`, `ai_msg_count` |
| Ternarios encadenados en string template del body JSON | Code node que arma el array `fields` y luego `JSON.stringify` |
| Lógica de routing en flows ManyChat | n8n decide qué flow disparar, ManyChat solo entrega |
| Estado de sesión en custom fields de ManyChat | Estado en Postgres (`sessions` tabla); ManyChat solo cachea `session_id` |
| Agregar campos ad-hoc sin namespace | Seguir convención `ai_*` / `lead_*` / `session_*` / `meta_*` |
| Slots fijos (`parte1-3`) sin `count` | Siempre incluir `ai_msg_count` para que ManyChat haga branching |
| No manejar fallos de la API ManyChat | `Continue on Fail` + retry + log a `bot_errors` table |

---

## 9. Migración del patrón legacy (clientes existentes)

Clientes con el patrón viejo (`parte1`/`parte2`/`parte3`/`respuesta_definitiva`):

- **NVJ Narvaja** · `parte1/2/3 + respuesta_definitiva`
- **CRZ Cereza Invest** · `parte1/2/3`
- **IMP Importadores Conectados** · `parte1/2/3`
- **SYS Sistemas y Soluciones** · `parte1/2/3 + respuesta_definitiva` (en setup, oportunidad de arrancar bien)

**Estrategia:**
- **No migrar lo que está LIVE y estable** (NVJ, CRZ, IMP). Riesgo > beneficio. Documentar como deuda técnica.
- **Aplicar el estándar desde cero en nuevos builds** (SYS F6, futuros HBV, STK, CRZ Cereza).
- **Cuando un cliente legacy necesite cambios grandes**, migrar de a poco respetando este standard.

---

## 10. Checklist de adopción (nuevo cliente o build)

### Lo mínimo (siempre)
- [ ] En ManyChat: crear **solo los 4 fields del núcleo** (`ai_msg_1/2/3/count`).
- [ ] En ManyChat: crear los **2 flows obligatorios** (`[LA AGENCIA] Default Reply`, `[LA AGENCIA] Responder Multi-Parte`).
- [ ] En n8n: crear credential `ManyChat - [CLIENTE]` (HTTP Header Auth).
- [ ] En n8n: los nodos HTTP de ManyChat referencian la credential (no Bearer inline).
- [ ] En n8n: agregar `Continue on Fail` en los 2 nodos HTTP de ManyChat.
- [ ] Alinear payload del External Request (Flow A) con lo que el Code node `Normalize Payload` realmente lee. **No agregar campos al payload que n8n no consume.**
- [ ] Documentar en architecture doc del cliente: link a este standard + lista de los fields y flows propios del cliente.

### Lo opcional (solo si justificado)
- [ ] Flow C `[LA AGENCIA] Fallback Humano` — solo si hay handoff dentro de ManyChat live chat.
- [ ] Fields extra (`lead_*`, `session_*`, `meta_*`) — solo si tienen escritor y lector concretos.
- [ ] Credential `Webhook [CLIENTE] Inbound` — solo si querés auth en el webhook entrante.

### Validación pre-GO-LIVE
- [ ] Smoke E2E: lead manda mensaje → respuesta llega particionada en 1, 2 y 3 partes (probar los 3 escenarios).
- [ ] Auditoría rápida: ¿hay algún custom field en ManyChat que **nadie escribe** o **nadie lee**? → archivar.
- [ ] Auditoría rápida: ¿el payload del External Request manda campos que `Normalize Payload` ignora? → quitar.

---

## 11. Referencias

- ManyChat API docs: https://api.manychat.com/swagger
- n8n HTTP Header Auth: https://docs.n8n.io/integrations/builtin/credentials/httprequest/
- Patrón validado en: `clients/SYS_SistemasYSoluciones/03_workflows/sys-agente-principal-v0.3.json` (F6, vigente desde 2026-06-02)
