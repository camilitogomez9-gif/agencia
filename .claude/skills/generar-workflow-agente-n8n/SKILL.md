---
name: generar-workflow-agente-n8n
description: >
  Usar este skill cuando hay que generar el JSON del workflow principal n8n de
  un agente conversacional para Etapa 2 — el main que recibe webhook ManyChat,
  invoca al AI Agent (gpt-4o) con Postgres Chat Memory de Supabase, y devuelve
  la respuesta dividida en partes. Se activa con frases como "generar workflow
  main para X", "crear el agente principal de X", "armar workflow v0.1 del agente".
  Stack target: n8n + OpenAI + Supabase. Genera SIN tools (esas las hace
  generar-subworkflows-tools-n8n + integrar-tools-al-main-fromai).
---

# Skill: Generar Workflow Principal n8n (v0.1, sin tools)

## Descripción

Genera el JSON importable del workflow principal `{cliente}-agente-principal-v0.1.json` con la estructura validada en SYS:

```
[Webhook (ManyChat)] → [Normalize Payload] → [IF skip?]
  ├── (true) → [Respond Skip]
  └── (false) → [Build User Message Context] → [AI Agent]
                                                  ├── ai_languageModel ← [OpenAI Chat Model gpt-4o]
                                                  └── ai_memory ← [Postgres Chat Memory] (Supabase)
                → [Split Respuesta] → [Respond to Webhook]
```

El system prompt va **inline** en el nodo AI Agent. Sin tools (esas se agregan después con `integrar-tools-al-main-fromai`).

---

## Cuándo invocarlo

- F3 del Plan Maestro Etapa 2 está lista para arrancar
- Supabase YA está configurado (F2 ✅), credencial `{Cliente} SYS` ya existe en n8n
- Existe un system prompt v2.x listo para usar
- El usuario quiere "el main listo para importar"

## Cuándo NO invocarlo

- Falta F2 (Supabase) — derivar a `setup-supabase-memoria-agente`
- El prompt es v1.x sin actualización para Etapa 2 — derivar a `/iterar-prompt`
- Hay que regenerar v0.2+ (con tools integradas) — derivar a `integrar-tools-al-main-fromai`

---

## Inputs requeridos

1. **Cliente ID + nombre** (ej. `SYS`, `Sistemas y Soluciones`)
2. **Path al system prompt v2.x** (ej. `clients/SYS_*/04_agents/...-system-prompt.md`)
3. **Credential IDs en n8n** (que el usuario tiene a mano):
   - OpenAI (compartido o específico)
   - Postgres Supabase del cliente
4. **Path del webhook** (default: `/{cliente_id_lower}-agent`)

Si alguno falta, preguntar.

---

## Proceso

### Paso 1 — Leer el system prompt
Cargar el archivo del prompt, extraer el bloque de producción (entre triple backticks bajo `## System Prompt (producción)`). Si tiene placeholders `{{NOMBRE}}` / `{{URL_TIENDA}}`, resolverlos con valores reales del CLIENT_INFO o dejarlos como expresiones a resolver en runtime.

### Paso 2 — Generar el JSON con script Python

Patrón del workflow (referencia: SYS `sys-agente-principal-v0.1.json`):

| Nodo | Tipo | Posición x (grid 240) |
|---|---|---|
| Webhook (ManyChat) | `n8n-nodes-base.webhook` typeVersion 2 | 0 |
| Normalize Payload | `n8n-nodes-base.code` typeVersion 2 | 1 |
| IF skip? | `n8n-nodes-base.if` typeVersion 2 | 2 |
| Build User Message Context | `n8n-nodes-base.code` typeVersion 2 | 3 |
| AI Agent | `@n8n/n8n-nodes-langchain.agent` typeVersion 1.7 | 4 |
| OpenAI Chat Model | `@n8n/n8n-nodes-langchain.lmChatOpenAi` typeVersion 1.2 | (4, debajo) |
| Postgres Chat Memory | `@n8n/n8n-nodes-langchain.memoryPostgresChat` typeVersion 1.3 | (4, debajo) |
| Split Respuesta | `n8n-nodes-base.code` typeVersion 2 | 5 |
| Respond to Webhook | `n8n-nodes-base.respondToWebhook` typeVersion 1.1 | 6 |
| Respond Skip | `n8n-nodes-base.respondToWebhook` typeVersion 1.1 | (3, encima) |

### Paso 3 — Configuración crítica por nodo

#### Webhook
```json
{"httpMethod": "POST", "path": "{cliente_lower}-agent", "responseMode": "responseNode"}
```

#### Normalize Payload — Code JS (extracción multi-canal):
```javascript
const body = $input.first().json.body || $input.first().json;
const canal = (body.canal || 'test').toLowerCase();
const subId = String(body.subscriber_id || body.from || 'anon');
const leadIdentifier = `${canal}_${subId}`;
const mensajeActual = String(body.mensaje || body.text || '').trim();

if (!mensajeActual) {
  return [{ json: { skip: true, reason: 'empty_message' } }];
}

const canalLabel = canal === 'whatsapp' ? 'WhatsApp'
                 : canal === 'ig' ? 'Instagram'
                 : canal === 'fb' ? 'Facebook'
                 : 'Test';

return [{
  json: { skip: false, canal, canalLabel, subId, leadIdentifier, mensajeActual,
          firstName: body.first_name || '',
          timestamp: body.timestamp || new Date().toISOString() }
}];
```

#### IF skip? — condición boolean sobre `$json.skip`

#### Build User Message Context — Code JS (inyectar [CONTEXTO TURNO]):
```javascript
const data = $input.first().json;
const fecha = new Date().toLocaleString('es-AR', { timeZone: 'America/Argentina/Buenos_Aires' });
const contextoTurno = `[CONTEXTO TURNO]
- Canal: ${data.canalLabel}
- Fecha y hora actual: ${fecha}
- Perfil del lead (si se conoce): sin clasificar
- Etapa actual: bienvenida
- Datos ya capturados: {}
- Productos ya mostrados: ninguno

[MENSAJE DEL USUARIO]
${data.mensajeActual}`;
return [{ json: { ...data, userMessage: contextoTurno } }];
```

#### OpenAI Chat Model
```json
{"model": "gpt-4o", "options": {"temperature": 0.4, "maxTokens": 1500}, "credentials": {"openAiApi": {"id": "<<<CRED_ID>>>"}}}
```

#### Postgres Chat Memory
```json
{"sessionIdType": "customKey",
 "sessionKey": "={{ $('Normalize Payload').item.json.leadIdentifier }}",
 "tableName": "n8n_chat_histories",
 "contextWindowLength": 20,
 "credentials": {"postgres": {"id": "<<<SUPABASE_CRED_ID>>>", "name": "Supabase {CLIENTE}"}}}
```

#### AI Agent
```json
{"promptType": "define",
 "text": "={{ $json.userMessage }}",
 "options": {
   "systemMessage": "<<<PROMPT INLINE>>>",
   "maxIterations": 5,
   "returnIntermediateSteps": false
 }}
```

#### Split Respuesta — Code JS (ManyChat Standard interno 2026):
```javascript
// Convención: ver _core/standards/manychat-integration-pattern.md
const output = $input.first().json.output || '';
const partes = output.split(/^---\s*$/m)
                     .map(p => p.trim())
                     .filter(p => p.length > 0);
const [ai_msg_1 = '', ai_msg_2 = '', ai_msg_3 = ''] = partes.slice(0, 3);
return [{ json: { raw: output, ai_msg_1, ai_msg_2, ai_msg_3, ai_msg_count: partes.length } }];
```

#### Respond to Webhook (rama OK):
```json
{"respondWith": "json",
 "responseBody": "={{ JSON.stringify({ ok: true, raw: $json.raw, ai_msg_1: $json.ai_msg_1, ai_msg_2: $json.ai_msg_2, ai_msg_3: $json.ai_msg_3, ai_msg_count: $json.ai_msg_count }) }}"}
```

> ⚠️ **Naming:** usar prefijo `ai_*` (no `parte1/2/3` del patrón legacy). Ver [ManyChat Standard interno 2026](../../../_core/standards/manychat-integration-pattern.md) sección 2.

#### Respond Skip (rama skip):
```json
{"respondWith": "json",
 "responseBody": "={{ JSON.stringify({ ok: true, skipped: true, reason: $json.reason }) }}"}
```

### Paso 4 — Conexiones

```
Webhook → Normalize
Normalize → IF skip?
IF skip? main[0] (true) → Respond Skip
IF skip? main[1] (false) → Build Context
Build Context → AI Agent (main)
OpenAI Chat Model → AI Agent (ai_languageModel)
Postgres Chat Memory → AI Agent (ai_memory)
AI Agent → Split Respuesta
Split Respuesta → Respond to Webhook
```

### Paso 5 — Guardar JSON

Path: `clients/{XXX}_{Nombre}/03_workflows/{cliente_lower}-agente-principal-v0.1.json`

### Paso 6 — Generar doc setup

Crear `clients/{XXX}_{Nombre}/06_docs/f3-workflow-principal-setup.md` con:
- Diagrama del flow
- Pasos de import + cableo de credenciales (2 placeholders)
- 5 smoke tests con curl:
  1. Apertura ("Hola")
  2. Cotización directa (Regla 21)
  3. Memoria turno 2 con mismo subscriber_id
  4. SELECT en `n8n_chat_histories` para verificar memoria persistente
  5. Sub_id distinto = memoria aislada
- Limitaciones v0.1 (sin tools, sin ManyChat real, sin lookup state)
- Troubleshooting de errores típicos (credentials no cableadas, Postgres connect refused, OpenAI invalid_api_key)

---

## Smoke test (validación del skill)

Después de importar en n8n + cablear 2 credenciales + activar:

```bash
curl -X POST https://[TU-INSTANCIA-N8N]/webhook/{cliente_lower}-agent \
  -H "Content-Type: application/json" \
  -d '{"canal":"test","subscriber_id":"smoke-001","mensaje":"Hola"}'
```

**Esperado:** respuesta JSON con `raw`, `ai_msg_1`, `ai_msg_2`, `ai_msg_3` y `ai_msg_count >= 1`.

---

## Composición

**Invoca:** ninguno (genera solo).

**Es invocado por:** `bootstrap-agente-etapa-2` (S1) como sub-paso opcional si las creds Supabase ya están listas.

**Precede a:** `generar-subworkflows-tools-n8n` (S3) + `integrar-tools-al-main-fromai` (S4).

---

## Notas operativas

- **NO regenerar** el JSON después de que el usuario haya hecho config manual en UI (el re-import borra config). Si hay que cambiar algo después de la primera vez, editar en UI o usar `inspector-bugs-toolworkflow-n8n` para detectar drift.
- **El prompt va INLINE** en el JSON. Si el prompt es muy largo (>50 KB), considerar moverlo a un Google Docs y leerlo con HTTP Request node (patrón CRZ).
- **Path del webhook por convención:** `{cliente_id_lower}-agent` (ej. `sys-agent`, `crz-agent`).
- **typeVersion del AI Agent es 1.7** (estable). Otras versiones pueden cambiar la forma del JSON.
- **`maxIterations: 5`** es seguro. Subir solo si se valida que el agente encadena muchas tools.
