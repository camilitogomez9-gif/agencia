# SYS — Guía de implementación · Mejoras pedidas por Edgardo

**Fecha:** 2026-06-23
**Origen:** Mail Edgardo solicitando 3 mejoras (recontacto 4 días, mail a leads, consulta precios interna).
**Plan:** este doc cubre los 3 pedidos en 1 sola sesión de deploy. Asume el main `sys-agente-principal-v0.9` ya deployado y vivo.

---

## Mapeo pedido → cambio

| # | Pedido Edgardo | Implementación |
|---|---|---|
| 1 | "Recontacto a los 4 días con texto fijo" | Workflow `sys-seguimientos-leads-v2` (reemplaza v1) + vista SQL nueva |
| 2 | "Mail cuando llega contacto que deja datos" | `sys-tool-notificar-lead-v4` (TO actualizado) + `sys-tool-guardar-email-v5` (nodo Gmail nuevo) |
| 3 | "Consulta precios interna desde Google Sheets" | Tool nueva `sys-tool-consultar-precio-interno-v1` + flag `is_internal` en main + prompt v2.3 con MODO INTERNO |

---

## Pre-flight — datos a recolectar antes del deploy

Items que necesitás (preferentemente en una sola pasada con Edgardo y Rodri):

1. **Spreadsheet ID + nombre de pestaña** del Google Sheets de precios de Rodri.
   - Pedir a Edgardo: "Pasame el link del Google Sheet de precios de Rodri y el nombre exacto de la pestaña que querés que consulte el agente."
2. **Subscriber IDs en ManyChat** de Edgardo + Rodri (+ tu propio la agencia si lo querés para testing).
   - Cómo conseguirlos: en ManyChat → Audience → buscar por nombre/teléfono → click contacto → URL = `https://app.manychat.com/fb<PAGE_ID>/chat/<SUBSCRIBER_ID>`. El SUBSCRIBER_ID está en la URL.
3. **Confirmar** con Edgardo que la planilla NO contiene precios públicos (no debe leakear a leads) — sino el guard de modo interno es overkill.

---

## Deploy paso a paso

### Paso 1 — SQL (Supabase)

Ejecutar en Supabase Studio → SQL Editor:

```sql
-- Pegar el contenido de:
-- clients/SYS_SistemasYSoluciones/06_docs/supabase-schema-v3-seguimientos.sql
```

Verificar:
```sql
SELECT * FROM sys_leads_para_seguimiento LIMIT 5;
-- Debe correr sin error. Filas devueltas = leads candidatos (puede ser 0).
```

### Paso 2 — Workflow seguimientos v2

1. En n8n → Workflows → buscar `sys-seguimientos-leads-v1` → desactivar.
2. Workflows → Import from File → seleccionar `clients/SYS_SistemasYSoluciones/03_workflows/sys-seguimientos-leads-v2.json`.
3. Importa como nuevo workflow (NO overwrite — el v1 queda para rollback).
4. Abrir el v2:
   - Confirmar que el Schedule Trigger tiene cron `0 11 * * 1-5` y timezone `America/Argentina/Buenos_Aires`.
   - Verificar credentials `Supabase SYS` (`cQLxF5deDtmo4HTV`) y `ManyChat - SYS` (`E41Ucr4mYfSjuoxJ`) están bindeadas en los 4 nodos que las usan.
5. Activar el workflow.

### Paso 3 — Tool notificar_lead v4

1. n8n → buscar `sys-tool-notificar-lead-v3` (id `QI1gO4dZ5vXXo7V3`) → Import → seleccionar `sys-tool-notificar-lead-v4.json` → **overwrite** (preserva el workflowId vivo).
2. Verificar nodo `Gmail Send (emarti + marketing)`:
   - `sendTo` = `emarti@sistemasysoluciones.com, marketing@sistemasysoluciones.com`
   - `options` vacío (sin `ccList`)
   - Credencial Gmail `Gmail | la agencia®` (`5R0ScEVqcfjKYanp`) bindeada.
3. Save. Ya está activo (la tool se invoca desde el main por workflowId).

### Paso 4 — Tool guardar_email v5

1. n8n → buscar `sys-tool-guardar-email-v4` (id `v9HD7P2uroG4Ni3A`) → Import → seleccionar `sys-tool-guardar-email-v5.json` → **overwrite**.
2. Verificar nodo nuevo `Gmail Send notif (emarti + marketing)`:
   - Ubicado entre `Append a Google Sheets` y `Format Output (saved)`.
   - `sendTo` correcto, credencial Gmail bindeada.
3. Save.

### Paso 5 — Tool consultar_precio_interno v1 (NUEVA)

1. n8n → Workflows → Import from File → `sys-tool-consultar-precio-interno-v1.json`.
2. Abrir el workflow recién importado:
   - **Nodo `Read precios (Google Sheets)`**:
     - `documentId` → reemplazar `<<<SHEET_ID_PRECIOS_RODRI>>>` con el ID real del sheet de Rodri.
     - `sheetName` → reemplazar `<<<TAB_NAME>>>` con el nombre real de la pestaña.
     - Credencial `googleSheetsOAuth2Api` = `la agencia` (`2a5f0S7mTtvH5XH2`) — si la cuenta la agencia no tiene acceso al sheet de Rodri, crear nueva credencial con cuenta del cliente y bindearla acá.
   - **Nodo `Validate + Guard whitelist`**:
     - En el código JS, reemplazar los 3 placeholders `<<<SUBSCRIBER_ID_*>>>` con los subscriber_id reales de Edgardo, Rodri, la agencia.
     - *Alternativa preferida*: setear env var en n8n `SYS_INTERNAL_SUBSCRIBERS=12345,67890,99887` (CSV) y dejar los fallbacks vacíos.
3. Copiar el `workflowId` del workflow guardado (se autogenera al primer save). Lo necesitás en el Paso 6.
4. Activar.

### Paso 6 — Main workflow v0.9 → v0.10 (edits manuales)

El main vivo necesita 2 ediciones:

**Edit A — calcular `is_internal` en el nodo Normalize/Build context**:

Ubicar el nodo Code donde se construye el contexto del turno (`Build User Message Context` o equivalente — el que arma el bloque `[CONTEXTO TURNO]`). Agregar al inicio:

```javascript
// Whitelist de subscribers internos. Mover a env var SYS_INTERNAL_SUBSCRIBERS (CSV) cuando esté disponible.
const INTERNAL_WHITELIST = (process.env.SYS_INTERNAL_SUBSCRIBERS || '')
  .split(',').map(s => s.trim()).filter(Boolean);
const INTERNAL_FALLBACK = ['<SUBSCRIBER_EDGARDO>', '<SUBSCRIBER_RODRI>', '<SUBSCRIBER_JANO>'];
const allowedInternals = INTERNAL_WHITELIST.length ? INTERNAL_WHITELIST : INTERNAL_FALLBACK;

const subId = String($json.subscriber_id || '').trim();
const isInternal = allowedInternals.includes(subId);
```

Y en el bloque que arma el `[CONTEXTO TURNO]` para inyectar al User Message, agregar la línea:

```
Modo interno: {{isInternal ? 'true' : 'false'}}
```

(o el equivalente para el formato actual del context block del main v0.9).

**Edit B — cablear la nueva Tool 10 al AI Agent**:

1. Abrir el nodo `AI Agent` del main.
2. Agregar un nuevo `toolWorkflow` node con:
   - Name: `consultar_precio_interno`
   - Description (visible al LLM): "Consulta precios reales de equipos desde la planilla interna de Rodri (Google Sheets). SOLO para uso interno. Args: query (texto libre con modelo/marca/tecnología). Devuelve hasta 5 matches con precio."
   - `workflowId.value` = id del workflow del Paso 5
   - Schema input: `{ query: string, session_id: string, subscriber_id: string }` con descripciones `$fromAI` minimalistas (anti bug Zod).
3. Conectar `ai_tool` al AI Agent.
4. Re-exportar el workflow como `sys-agente-principal-v0.10.json` al repo.

---

## Smoke tests mínimos

### Smoke 1 — Seguimiento 4 días (happy path)

```sql
-- En Supabase Studio. Crear lead que cumple condición (5 días sin actividad):
INSERT INTO sys_session_state (session_id, etapa, datos_capturados, ultima_actividad, seguimientos_enviados)
VALUES (
  'wa_smoke_seg_4d_001',
  'diagnostico',
  '{"nombre":"Juan Carlos","equipo":"DTF textil"}'::jsonb,
  NOW() - INTERVAL '5 days',
  0
)
ON CONFLICT (session_id) DO UPDATE
  SET ultima_actividad = EXCLUDED.ultima_actividad,
      seguimientos_enviados = 0,
      etapa = EXCLUDED.etapa;
```

En n8n → workflow `sys-seguimientos-leads-v2` → Execute Workflow.

**Esperado:**
- `Get leads para seguir` retorna ≥1 fila con `session_id = 'wa_smoke_seg_4d_001'`.
- `Build mensaje fijo` produce `ai_msg_1 = "Hola, Juan, buen día. Quería dar seguimiento a nuestra última conversación..."`.
- `setCustomFields` + `sendFlow` retornan 200 OK (ManyChat).
- `Update tracking` setea `seguimientos_enviados = 1`, `etapa = 'cerrado'`.

Verificar:
```sql
SELECT seguimientos_enviados, etapa, ultima_actividad
FROM sys_session_state WHERE session_id = 'wa_smoke_seg_4d_001';
-- seguimientos_enviados=1, etapa='cerrado', ultima_actividad ≈ NOW().

SELECT * FROM sys_leads_para_seguimiento WHERE session_id = 'wa_smoke_seg_4d_001';
-- 0 filas — confirma idempotencia.
```

Cleanup: `DELETE FROM sys_session_state WHERE session_id = 'wa_smoke_seg_4d_001';`

### Smoke 2 — Seguimiento sin nombre (fallback)

Como Smoke 1 pero `datos_capturados = '{}'::jsonb`. Esperado: `ai_msg_1` arranca con `"Hola, buen día. Quería dar seguimiento..."` (sin nombre).

### Smoke 3 — Mail notificar_lead a destinatarios nuevos

En n8n → workflow `sys-tool-notificar-lead-v4` (id `QI1gO4dZ5vXXo7V3`) → Execute Workflow (pinData ya cargada).

**Esperado:**
- `Gmail Send (emarti + marketing)` retorna 200 OK.
- Verificar en bandeja de entrada de `emarti@sistemasysoluciones.com` y `marketing@sistemasysoluciones.com` que llegó el mail con asunto `🟢 Lead nuevo SyS — Smoke Test (CABA) — TOMAR CHAT`.
- Confirmar que `info@sistemasysoluciones.com` NO recibió copia.

### Smoke 4 — Mail guardar_email a destinatarios nuevos

En n8n → workflow `sys-tool-guardar-email-v5` (id `v9HD7P2uroG4Ni3A`) → Execute Workflow con pinData modificada:
```json
{
  "email": "smoke_test_v5_001@[TU-DOMINIO]",
  "nombre": "Smoke v5",
  "telefono": "1199998888",
  "aplicacion_interes": "DTF textil",
  "subscriber_id": "smoke_001",
  "session_id": "smoke_v5_001"
}
```

**Esperado:**
- `Append a Google Sheets` agrega fila al sheet "SYS - Leads (Captura Emails)".
- `Gmail Send notif (emarti + marketing)` retorna 200 OK, mail con asunto `📨 Nuevo lead dejó datos — Smoke v5`.
- `Format Output (saved)` ejecuta. Output final = `{ status: 'RESOLVED', data: { email, already_exists: false }, ... }`.

Re-ejecutar con el mismo email. **Esperado**: rama `Format Output (already exists)`, `Gmail Send` NO se invoca (no se dispara mail por duplicado).

### Smoke 5 — Precio interno con subscriber whitelisted

En n8n → workflow `sys-tool-consultar-precio-interno-v1` → Execute Workflow con pinData:
```json
{
  "query": "<modelo real del sheet de Rodri>",
  "session_id": "smoke_interno_001",
  "subscriber_id": "<SUBSCRIBER_ID_EDGARDO>"
}
```

**Esperado:**
- `Validate + Guard whitelist` → `_skip = false`.
- `Read precios (Google Sheets)` retorna N filas.
- `Filter + Format Output` → `status: RESOLVED` con items reales del sheet.

### Smoke 6 — Precio interno con subscriber NO whitelisted (guard)

Mismo pinData pero `subscriber_id = "subscriber_random_999"`.

**Esperado:**
- `Validate + Guard whitelist` → `_skip = true`, `_reason: 'not_whitelisted'`.
- Rama IF skip = true → `Return ERROR (skip)`.
- Output final: `{ status: 'ERROR', data: null, message_to_agent: 'Esta consulta es solo para uso interno...', trace_id: ... }`.
- Confirma que NO se leyeron precios.

### Smoke 7 (E2E) — Conversación interna en ManyChat

Desde la cuenta WhatsApp/IG de Edgardo o Rodri, mandar al bot:
```
hola, cuánto sale el HUENU UV?
```

**Esperado:**
- El main detecta `is_internal=true`, lo inyecta en el contexto del turno.
- El AI Agent invoca `consultar_precio_interno` con `query="HUENU UV"`.
- Respuesta del agente tutea, sin pedir datos, con precio real del sheet.

### Smoke 8 (E2E) — Conversación de lead externo NO accede a Tool 10

Desde cualquier número que NO esté en la whitelist:
```
hola, cuánto sale el HUENU UV?
```

**Esperado:**
- El AI Agent NO invoca `consultar_precio_interno` (gate del prompt v2.3 Regla 27).
- Si llegara a invocar, el sub-workflow rechaza por whitelist.
- Respuesta del agente: pide datos + dice que un comercial cotiza (Regla 1).

---

## Rollback plan

Cada cambio es reversible:

| Cambio | Rollback |
|--------|---------|
| Seguimientos v2 | Desactivar v2, reactivar v1 (workflowId `8XkICVXpp7qnAfBX` queda intacto). Reejecutar vista v2 SQL para volver a la v2 anterior (24h+7d). |
| notificar_lead v4 | Re-importar `sys-tool-notificar-lead-v3.json` con overwrite. Workflowid preservado. |
| guardar_email v5 | Re-importar `sys-tool-guardar-email-v4.json` con overwrite. |
| consultar_precio_interno v1 | Desactivar y borrar workflow. Quitar el toolWorkflow node del main. |
| Prompt v2.3 | Pegar v2.2 (backup en `agente-sistemasysoluciones-system-prompt-v2.2.md`) al systemMessage del AI Agent. |
| Main v0.10 | Re-importar `sys-agente-principal-v0.9.json` con overwrite. |

---

## Post-deploy

- Limpiar memorias de testing: `DELETE FROM sys_session_state WHERE session_id LIKE 'wa_smoke_seg_4d_%';`
- Notificar a Edgardo: "Hecho. El recontacto a 4 días arranca automáticamente con leads vivos. Los mails a `emarti@` + `marketing@` ya llegan tanto por notificar_lead como por captura de email. Para el precio interno, mandame los datos del Sheet de Rodri y los subscriber_id tuyo + Rodri para activar la tool."
- Crear archivos nuevos del repo en CLIENT_INFO.md de SYS.
