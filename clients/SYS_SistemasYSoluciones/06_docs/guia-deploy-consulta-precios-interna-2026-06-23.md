# SYS — Guía de deploy · Consulta de precios interna (Rodrigo)

**Fecha:** 2026-06-23
**Workflow:** `sys-agente-principal-v0.10.json` (sucesor de v0.9 vivo en prod)
**Plan completo:** `/Users/camilo/.claude/plans/bien-lo-que-vamos-snazzy-nygaard.md`

> **Importante**: esta es la Mejora #3 del mail Edgardo. Reemplaza al diseño anterior (tool del agente + prompt v2.3) que quedó superseded por uno más simple — path desviado antes del AI Agent, sin LLM, sin tool del agente.

---

## Pre-flight — datos a recolectar

Tres items, cliente:

1. **Spreadsheet ID + nombre de pestaña** del Google Sheet de precios de Rodri.
   - El ID está en la URL: `https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>/edit#gid=0` → el `<SPREADSHEET_ID>` es lo que necesitamos.
   - Nombre exacto de la pestaña que querés leer (case-sensitive).
2. **Acceso de la cuenta de servicio la agencia al sheet**. Confirmar con Rodri que comparta el sheet con el email de la cuenta Google de la agencia que está bindeada en la credencial `la agencia` (id `2a5f0S7mTtvH5XH2` en n8n). Si no querés mezclar cuentas, crear credencial Google Sheets nueva con cuenta del cliente y bindearla al nodo `Read precios Rodri`.
3. **Subscriber ID de Rodrigo en ManyChat**: entrá a su chat en ManyChat → la URL es `https://app.manychat.com/fb5013937/chat/<SUBSCRIBER_ID>` → copia ese número.

---

## Deploy paso a paso

### Paso 1 — Importar v0.10 al main vivo

1. n8n → Workflows → buscar `sys-agente-principal-v0.9` (id que ya tenés en producción).
2. Menú ⋯ → **Import from File** → seleccionar `clients/SYS_SistemasYSoluciones/03_workflows/sys-agente-principal-v0.10.json` → **Overwrite** (preserva workflowId vivo).
3. Abrir el workflow recién importado, ubicar los 8 nodos nuevos en el área de `position [-80, 256]` hacia la derecha (paralelos al flujo principal). Deberías ver:
   - `IF Es interno?`
   - `Extract keywords`
   - `Read precios Rodri`
   - `Filter + Format`
   - `setCustomFields ManyChat (interno)`
   - `sendFlow ManyChat (interno)`
   - `Log interno`
   - `Respond to Webhook (interno)`

### Paso 2 — Reemplazar 3 placeholders

**Nodo `IF Es interno?`** — abrir → en la condición `leftValue` reemplazar `<<<SUBSCRIBER_ID_RODRIGO>>>` con el ID real de Rodrigo (el de la agencia `2004316097` ya está hardcoded para testing).

**Nodo `Read precios Rodri`** — abrir:
- `documentId` → reemplazar `<<<SHEET_ID_PRECIOS_RODRI>>>` con el ID real.
- `sheetName` → reemplazar `<<<TAB_NAME>>>` con el nombre real.
- Credencial: confirmar que `la agencia` (id `2a5f0S7mTtvH5XH2`) tiene acceso. Si no, crear credencial nueva y bindearla.

### Paso 3 — Save + Activar

Save el workflow. Ya está activo en prod (el toggle de active venía del v0.9).

---

## Smoke tests (5)

### Smoke 1 — Happy path interno: la agencia consulta y recibe respuesta

Desde tu WhatsApp (subscriber `2004316097`, whitelisted) mandá al bot:
```
cuanto sale el <modelo real del sheet>
```

**Esperado:**
- Recibís en WhatsApp una respuesta tipo "Encontré X matches para 'cuanto sale el ...': 1. ... 2. ...", en ~1-2 seg.
- En n8n → Executions del main → la ejecución que correspondió debería mostrar el path `IF Es interno? = TRUE → Extract → Read → Filter → setCustomFields → sendFlow → Log → Respond`. NO debería entrar al AI Agent.
- Postgres:
  ```sql
  SELECT created_at, status, input_payload, output_payload
  FROM sys_tool_calls
  WHERE tool_name = 'consulta_precio_interno'
  ORDER BY created_at DESC LIMIT 1;
  ```
  Esperado: 1 row con status `RESOLVED`, `input_payload.query` = tu mensaje, `output_payload.matches_count` ≥ 1.
- Verificar NO contaminación de memoria del agente:
  ```sql
  SELECT created_at, message->>'type' AS tipo
  FROM n8n_chat_histories
  WHERE session_id = 'wa_2004316097'
  ORDER BY created_at DESC LIMIT 3;
  ```
  Esperado: los 3 rows top deben ser anteriores a este smoke (el path interno NO escribe a memoria conversacional).

### Smoke 2 — Sin match

Mandá:
```
cuanto sale el equipo inexistente xyz123
```

**Esperado:**
- WhatsApp recibe: `No encontré nada que matchee "cuanto sale el equipo inexistente xyz123". Probá con otro modelo o marca.`
- Postgres: nueva row con status `NOT_FOUND`, `matches_count = 0`.

### Smoke 3 — Query ambigua (>5 matches)

Mandá una query genérica que matchee muchos rows del sheet, por ejemplo:
```
precio dtf
```

**Esperado:**
- WhatsApp recibe: `Encontré X resultados para "precio dtf", te paso los primeros 5. Afiná con marca o modelo si querés ver más.` + lista de 5.
- Postgres: status `AMBIGUOUS`, `matches_count > 5`.

### Smoke 4 — Lead externo NO accede al sheet (CRÍTICO)

Desde cualquier número que NO esté en la whitelist (un test subscriber o un lead real cualquiera), mandá:
```
cuanto sale el HUENU UV
```

**Esperado:**
- El flujo va por el `IF Es interno? = FALSE` → `IF skip?` → flujo normal del agente.
- El agente responde según Regla 1 ("no doy precios, un comercial te cotiza").
- NO se invoca `Read precios Rodri`.
- Postgres: NO hay row nueva con `tool_name = 'consulta_precio_interno'`:
  ```sql
  SELECT COUNT(*) FROM sys_tool_calls
  WHERE tool_name = 'consulta_precio_interno' AND created_at > NOW() - INTERVAL '5 minutes';
  ```
  Comparar con cuántas hiciste vos como interno. Tiene que coincidir.

### Smoke 5 — Dedup NO aplica al path interno

Desde tu WhatsApp, mandá 2 veces seguidas la MISMA consulta (ej. `precio dtf` dos veces, dentro de 1 minuto).

**Esperado:**
- AMBAS consultas procesan y devuelven respuesta. El dedup del `IF skip?` NO se aplica al path interno (porque interno se desvía ANTES de llegar al `IF skip?`).
- Postgres: 2 rows nuevas en `sys_tool_calls`, mismo session_id, ambas RESOLVED/AMBIGUOUS.

---

## Si los 5 smokes pasan

1. Notificar a Edgardo: `"Listo. Mejora #3 deployada. Rodrigo ya puede consultar precios desde su WhatsApp al bot — le devuelve hasta 5 matches del sheet en ~1 seg. Probalo vos primero si querés."`
2. Actualizar `CLAUDE.md` raíz, `CLIENT_INFO.md` de SYS, y `contexto/datos-actuales.md` con el deploy.
3. Commit del repo con los archivos nuevos.

## Rollback

Si algo rompe el flujo de leads externos (caso extremadamente improbable porque el IF nuevo es no-destructivo):

1. n8n → Workflows → buscar el main → **Import from File** → seleccionar `sys-agente-principal-v0.9.json` → **Overwrite**.
2. Vuelve al estado del 2026-06-09 en <1 minuto.

---

## Anexo: cómo ajustar después del go-live

**Agregar otro usuario interno** (ej. Edgardo):
- Editar nodo `IF Es interno?` → en `leftValue` agregar el subscriber_id al array hardcoded:
  ```
  ['<SUB_RODRIGO>', '2004316097', '<SUB_EDGARDO>']
  ```

**Cambiar formato de respuesta** (ej. agregar Stock con emoji):
- Editar nodo `Filter + Format` → función `formatRow` → ajustar el slice/loop de Object.entries.

**Cambiar el sheet de origen** (ej. Rodri lo migra a otro doc):
- Editar nodo `Read precios Rodri` → actualizar `documentId`.
