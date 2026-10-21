# Incidente: memoria sintética inservible por mismatch MX `52` vs `521`

**Fecha:** 2026-06-30
**Severidad:** P2 (degrada experiencia, no rompe el bot)
**Estado:** RESUELTO

---

## Síntoma

Leads que recibían outreach automático (Touch 1/2/3 de `outreach-form-meta-venttur-v4`) o el rescate post-link (`wf-rescate-post-link-v2`) y luego respondían por WhatsApp, **el agente principal arrancaba la conversación de cero**: se presentaba como "¡Hola! Soy Mauricio de Venttur 😊" y pedía el nombre completo, ignorando el contenido del Touch enviado y los datos del Form Meta.

Casos observados (2026-06-29 y 2026-06-30):

- **Mariangel** — respondió al Touch 1 ("Boarding School") y el agente se presentó como nuevo.
- **Mini** — respondió al Touch 3 mencionando "intercambio de verano para nadador de alto rendimiento" y el agente pidió nombre y se presentó como si fuera el primer mensaje.
- **Eduardo Verduzco Rosán Glz** — recibió Touch 1, respondió "B dia si seria para mi hijo!" (respuesta directa a la pregunta del template) y el agente saludó como nuevo.

## Causa raíz

**MX WhatsApp `1` quirk.** Para móviles mexicanos, WhatsApp Business API usa el formato `+52 1 [10 dígitos]` (13 dígitos totales) con un `1` insertado entre el código país y el número local. El número "real" no lleva ese `1`.

Implicaciones en este ecosistema:

- **Google Sheet** (`Boarding_Schools_Venttur_2026-test-2`): guarda `Telefono` en formato `52XXXXXXXXXX` (12 dígitos, **sin** el `1`).
- **Airtable Leads**: hereda el mismo formato del Sheet.
- **ManyChat → webhook `venttur-main`**: envía `whatsapp_phone = +521XXXXXXXXXX` (13 dígitos, **con** el `1`).

El nodo `Postgres Chat Memory` del main calcula `sessionKey` así:

```js
$('Responder rápido ManyChat').first().json.body.whatsapp_phone.replace('+','')
// → "521XXXXXXXXXX" (13 dígitos)
```

Mientras que los nodos `Build Memory Texts (Touch N)` del outreach y `Build Rescate Memory (Fase N)` del rescate venían usando:

```js
const sessionKey = (lead.Telefono || '').toString();        // Touch 1 / Fase 1
const sessionKey = (lead.Telefono || '').toString().replace(/[^0-9]/g, '');  // Touch 2/3 / Fase 2
```

Ninguno agregaba el `1` MX. Resultado: el outreach insertaba en `session_id = 52XXXXXXXXXX` y el main consultaba `session_id = 521XXXXXXXXXX` → **nunca match** → `Postgres Chat Memory` cargaba historial vacío → el LLM arrancaba de cero.

## Evidencia

Query de control (2026-06-30):

```sql
SELECT id, session_id, message->>'type' AS type,
       LEFT(message->>'content', 100) AS preview
FROM n8n_chat_histories
WHERE session_id = '5218444278827'   -- Eduardo en el main
ORDER BY id;
```

Devolvió **8 rows**, todos del agente main (`tool_calls` presente), id 33105-33112. Sin rastro de los rows sintéticos.

Búsqueda por nombre y teléfono parcial:

```sql
SELECT id, session_id, message->>'type' AS type, ...
FROM n8n_chat_histories
WHERE (message->>'content' ILIKE '%Eduardo%' OR message->>'content' ILIKE '%8444278827%')
  AND NOT (message ? 'tool_calls')
ORDER BY id DESC;
```

Devolvió:
- `id 33019, session_id = 528444278827, type = ai` → "Hola Eduardo, gracias por tu interés…" (Touch 1)
- `id 33018, session_id = 528444278827, type = system` → "El lead Eduardo Verduzco Rosán Glz (everduzco@grupovvr.com, tel +528444278827)…"
- `id 32506 + 32503 + 31731 + 31730, session_id = 526141966486` → otro Eduardo (Duarte)

Patrón en la tabla: leads con `session_id` de **12 dígitos** (`52XXXXXXXXXX`) tenían rows sintéticos pero **cero rows del main**. Leads con `session_id` de **13 dígitos** (`521XXXXXXXXXX`) tenían rows del main pero **cero rows sintéticos**.

## Fix aplicado

### 1) Nueva función de normalización

Agregada a los 5 nodos Code de memoria sintética:

```js
function normalizeSessionKey(phone) {
  if (!phone) return '';
  let p = phone.toString().replace(/[^0-9]/g, '');
  if (p.length === 12 && p.startsWith('52')) p = '521' + p.slice(2);
  return p;
}
```

Detecta el caso MX (12 dígitos empezando con `52`) y agrega el `1` después del prefijo país. Otros países pasan limpios sin tocar.

### 2) Nodos modificados en n8n vivo

| Workflow | ID | Nodo |
|---|---|---|
| Outreach Form Meta | `CUuFxbst3iHpgeXS` | `Build Memory Texts (Touch 1)` |
| 〃 | 〃 | `Build Memory Texts (Touch 2)` |
| 〃 | 〃 | `Build Memory Texts (Touch 3)` |
| Rescate Post-Link | `mkEP1qFN7MVb9qP0` | `Build Rescate Memory (Fase 1)` |
| 〃 | 〃 | `Build Rescate Memory (Fase 2)` |

En los 2 de Rescate además se corrigió la referencia rota: `$('Get Lead')` → `$('Airtable: 1er check')` (Fase 1) y `$('Airtable: 2do check')` (Fase 2). Esa referencia hacía fallar el Code silenciosamente desde el 2026-06-23.

### 3) Migración de rows huérfanos en BD

```sql
-- Sanity check pre-migración
SELECT COUNT(*) AS total_a_migrar
FROM n8n_chat_histories
WHERE session_id ~ '^52[0-9]{10}$'
  AND NOT (message ? 'tool_calls')
  AND NOT (message ? 'invalid_tool_calls');
-- Result: 3784

-- UPDATE
UPDATE n8n_chat_histories
SET session_id = '521' || SUBSTRING(session_id FROM 3)
WHERE session_id ~ '^52[0-9]{10}$'
  AND NOT (message ? 'tool_calls')
  AND NOT (message ? 'invalid_tool_calls');

-- Confirmación post-migración (debe devolver 0)
SELECT COUNT(*) AS restantes
FROM n8n_chat_histories
WHERE session_id ~ '^52[0-9]{10}$'
  AND NOT (message ? 'tool_calls')
  AND NOT (message ? 'invalid_tool_calls');
-- Result: 0
```

**3.784 rows sintéticos** movidos de `session_id = 52XXXXXXXXXX` a `session_id = 521XXXXXXXXXX`. El filtro `NOT (message ? 'tool_calls') AND NOT (message ? 'invalid_tool_calls')` garantiza que solo se tocaron rows sintéticos — los rows de LangChain (escritos por el agente main) tienen siempre esos campos y quedan intactos.

### 4) Workflows de backfill también actualizados

- `backfill-vtr-chat-memory-v1.json` (nodo `Build Context`)
- `outreach-form-meta-backfill-v2.json` (nodo `Build Memory Texts`)

Para que cualquier nuevo backfill que se corra escriba en el sessionId correcto desde el día 1.

## Validación

El smoke test natural es esperar a un lead MX que respondió al outreach. Cuando responda, el main debe:
- NO presentarse como nuevo (no decir "¡Hola! Soy Mauricio de Venttur 😊")
- NO pedir el nombre completo (ya lo tiene del Form Meta + system message sintético)
- Responder al hilo del Touch que vio

## Lecciones aprendidas

1. **MX requiere normalización específica.** El número que un humano da y el que WhatsApp usa internamente difieren por un dígito. Cualquier sessionKey nuevo en este proyecto debe pasar por `normalizeSessionKey()` para alinearse con lo que ManyChat envía al main.

2. **El shape del jsonb de LangChain en n8n NO usa wrapper `data`.** Es flat: `{type, content, additional_kwargs, response_metadata, tool_calls?, invalid_tool_calls?}`. El shape mínimo `{type, content}` también funciona — LangChain JS hidrata los campos faltantes con defaults. Esto descartó una hipótesis inicial sobre el bug.

3. **Refs por nombre de nodo en JS son frágiles.** `$('Get Lead')` era una ref placeholder de la plantilla que nunca se ajustó a los nombres reales. n8n no falla en parse-time, falla en runtime → bug silencioso. Conviene auditar refs por nombre cada vez que se importa un Code node desde una plantilla genérica.

4. **Pre-flight con SELECT antes de UPDATE.** El COUNT del paso 1 confirmó que el UPDATE iba a tocar 3.784 rows. Si hubiera dado un número raro (cientos de miles, o cero), habría que parar y entender.

## Pendientes derivados

- [ ] Smoke test con un lead MX real (esperar evento natural)
- [ ] Si en algún momento se incorporan leads de otros países con códigos de 12 dígitos empezando con `52` (no existe hoy: `+52` es exclusivo de MX), revisar la heurística.
