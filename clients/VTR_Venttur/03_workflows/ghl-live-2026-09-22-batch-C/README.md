# Batch C · Workflows n8n GHL · 2026-09-22

Todos los workflows creados en este batch quedan **OFF** en n8n hasta que la agencia dispare CUTOVER-2 desde la guía.

## Aplicado por Codex

### `main-venttur-ghl` v0.1 · id `1eS1Z5k898c3ATnf` · OFF

Duplicado de `k3aivKSP67S97IHn` (post Batch A) con adaptaciones al shape GHL:

**Cambios estructurales:**

1. **Webhook path nuevo**: `main-venttur-ghl-<random>` (evita colisión con el productivo).
2. **6 nodos nuevos insertados entre `Webhook` y `Responder rápido ManyChat`:**
   - `Normalize GHL Payload` (Code) — adapter que mapea payload GHL Contact Reply → shape ManyChat-like que consume el resto del workflow. Extrae `contact_id`, `phone`, `message_body`, `attribution_url`, `date_created`.
   - `Compute idempotency hash` (Code) — sha256(`contact_id + date_created + body`).
   - `Check dedup` (Postgres) — `SELECT hash FROM vtr_message_dedup WHERE hash = $1`.
   - `Is duplicate?` (IF) — si viene con hash, es duplicado.
   - `Insert dedup` (Postgres) — `INSERT ... ON CONFLICT DO NOTHING` en `vtr_message_dedup`.
   - `Exit duplicate` (RespondToWebhook) — corta la ejecución con 200/duplicate si es duplicado.
3. **Tool `elevar` reescrita** de `toolHttpRequest` (viejo) a `toolWorkflow` apuntando a `vtr-tool-elevar-ghl` (`v9XkOfL9dQtY2wyv`).
4. **Nodo `Enviar WPP`** reescrito de HTTP directo a Meta → `POST /conversations/messages` GHL con `type: WhatsApp` + `contactId` + `message` extraído del formatter.

**Los nodos Airtable existentes (Actualizar ultimo mensaje, Buscar registro, Existe, Crear registro, Crear primer contacto, Buscar si ya existe) NO se tocaron.** Siguen apuntando a la base Airtable de VTR. Watch mode post-cutover: si funcionan bien durante 4-5 días, se pueden migrar a escrituras GHL en un batch aparte. Si no, dan datos comparables con el original para debug.

**⚠️ Falta antes de flip (CUTOVER-2):**

- **Debounce +20s**: no está implementado en v0.1. La guía dice "Wait + poll `vtr_message_buffer` en cadena". El dedup ya evita processar duplicados exactos, pero no agrupa ráfagas de mensajes. Agregar Wait + logic de buffer antes de `Agente IA WPP` cuando haya tiempo. **No bloquea el cutover** — el peor caso es que el bot responde por burbuja en vez de agrupar (comportamiento pre-ManyChat buffer).
- **Test C**: shape exacto de `POST /conversations/messages` puede diferir. Confirmar en `CUTOVER-3` smoke test. Si falla, fallback a `POST /conversations/{id}/messages/template` durante primeras horas.

**Snapshot:** `main-venttur-ghl-v0.1.json` · sha256 `4b67f96708fe1dc47014b7f178da7b95ce29ef346a0b6d88e689b6acf3eef186`

### `vtr-tool-elevar-ghl` · id `v9XkOfL9dQtY2wyv` · OFF

Sub-workflow invocable desde el main (`toolWorkflow` node `elevar`).

**3 pasos secuenciales:**

1. `PUT https://services.leadconnectorhq.com/contacts/{contact_id}` body `{"dnd": true}` — pausa el bot para ese contacto en GHL.
2. `PUT /contacts/{contact_id}` body `{"assignedTo": user_id}` — asigna al userId GHL. La conversation asociada hereda la asignación (verificado en Test D · PREP-2).
3. Telegram notify al grupo `-4925599962` con `contact_id`, `user_id`, `resumen`.

**Inputs (definidos en el toolWorkflow del main):**
- `contact_id` (LLM `$fromAI`)
- `user_id` (LLM `$fromAI` — el agente elige según programa)
- `resumen` (LLM `$fromAI`)

**Snapshot:** `vtr-tool-elevar-ghl.json` · sha256 `9c7418f7ff64b3559c43f0cac4aa2f85223dfcf26cb28a28f3e96bd84ddd688d`

## Bloqueantes · W4/W6/W9/W10 (construir en n8n UI antes de CUTOVER-2)

Los siguientes 4 workflows requieren edición interactiva en n8n UI (Airtable dedupes, campos custom GHL específicos, gates externos). Los construyo por API sería alto riesgo sin poder pin-data test cada nodo. **Recomendación:** Camilo o la agencia los construyen en UI a partir de las specs abajo.

---

### W4 · Formulario landing → Contact GHL

**Reemplaza:** `ZB6erhWicZmDfC4I` (Formulario Clientify · 11 nodos)

**Trigger:** Webhook (nueva URL, path `vtr-form-landing-ghl-<random>`).

**Payload esperado (idéntico al viejo webhook desde landings):**
```json
{
  "nombre": "...", "apellido": "...", "telefono": "...", "email": "...",
  "programa": "Boarding School|Internados|Idiomas|Ed. Superior|Cursos idiomas|...",
  "atribuida_a": "<slug aventurera>",  // desde landing GHL Funnel query param
  "url": "https://..."
}
```

**Nodos:**

1. **Webhook** (POST, `path: vtr-form-landing-ghl-...`)
2. **Normalize** (Code):
   - Remap: `programa = "Boarding School"` → `"Internados"` (canónico VTR).
   - `phone = normalize_E164(telefono, default_country='MX')`.
3. **POST /contacts/upsert** (HTTP node con cred `GHL VTR (PIT) YkVmaA4jlRbO1TQD`):
   - URL: `https://services.leadconnectorhq.com/contacts/upsert`
   - Body:
     ```json
     {
       "phone": "$json.phone",
       "firstName": "$json.nombre",
       "lastName": "$json.apellido",
       "email": "$json.email",
       "locationId": "7aXb4JCKsWV5nUyBXeSF",
       "customFields": [
         {"id": "<field_id_programa>", "value": "$json.programa"},
         {"id": "<field_id_atribuida_a>", "value": "$json.atribuida_a"}
       ],
       "tags": ["Form Landing", "$json.programa"]
     }
     ```
   - Headers: `Version: 2021-07-28`, `LocationId: 7aXb4JCKsWV5nUyBXeSF`
4. **Respond** (200 OK).

**Sin gate.** Idempotencia por teléfono (GHL upsert dedup nativo).

**Field IDs GHL a buscar en `06_docs/ghl-credentials.md`** o via `GET /locations/7aXb4JCKsWV5nUyBXeSF/customFields?model=contact`.

---

### W9 · Actualizar `link_enviado` → GHL

**Reemplaza:** `gRSMjzxggA4UePjz`

**Trigger:** Execute Workflow (invocado desde el main via `Execute Workflow`, o Webhook si prefiere ser directo).

**Payload esperado:** `{contact_id, programa}`

**Nodos:**

1. **Trigger** (Execute Workflow o Webhook).
2. **PUT /contacts/{contact_id}** (cred GHL PIT):
   - Body: `{"customFields": [{"id": "rHzGNiesWuESPmSZyviJ", "value": "true"}]}` (field `link_enviado`)
3. **PUT /contacts/{contact_id}/tags** (cred GHL PIT):
   - Body: `{"tags": ["LINK_ENVIADO", "$json.programa"]}`
4. **Execute Workflow** → `YB0UxwEVwzISdd54` (Rescate GHL Post-Link · ya construido)
   - Pasar `{contact_id, programa}` como input.
5. **Respond** o continuar.

**Sin gate.** Se activa post-cutover.

---

### W10 · Outreach Sheet → Contact GHL

**Reemplaza:** `CUuFxbst3iHpgeXS` (37 nodos · Outreach Form Meta v4)

**Trigger:** Google Sheets Trigger (mismo doc `1HzJVMBwnGikiI_U805N7oqcXPYE7TjEFTL1rqdcCEIU` sheet `Boarding_Schools_Venttur_2026-test-2` gid `160362675`, polling 1min, event=rowAdded).

**Nodos principales:**

1. **Sheets Trigger** (mismo del v4).
2. **Normalize Payload** (Code, mismo del v4 — parsePhone/splitName/deriveTipo/deriveFuente).
3. **IF (_error?)** → rama TRUE → sub-flujo webapp_errors (existente).
4. **Split In Batches (1)** → **POST /contacts/upsert** (GHL) con:
   - Dedup por teléfono (nativo GHL) + Folio (custom field).
   - Tags: `Origen: Form Meta`, `Programa: Boarding School` (o el que venga).
   - Custom fields: `Folio`, `Ad Name`, `Platform`, `Grado Escolar`, `Inicio Deseado`, `Nivel Inglés`, `Fuente lead`, `Tipo`.
5. **Carril tri-toque OFF** — el despachador `vrShEXQGGAo4FqAt` se encarga del outreach. W10 solo hace ingesta.

**Sin gate.** El carril de toques ya migró al despachador (§POST-2).

---

### W6 · Confirmación agenda GHL Calendar Webhook

> ⛔ **Gate: §PAR-E OAuth GCal → GHL (Rodrigo + Andrés).** Sin OAuth de los asesores, `conflictCheck: true` no puede activarse en los 8 calendarios y la confirmación no puede detectar overlap. Pausar la construcción hasta que Rodrigo y Andrés cierren su OAuth en `app.gohighlevel.com` → Settings → Integrations → Google.

**Reemplaza:** `2PSekVBxarsrnVBu` (Confirmación agenda · 22 nodos · camino Diego roto WON'T FIX)

**Trigger:** Webhook GHL "Customer Booked Appointment" (evento nativo GHL, no GCal Trigger).

**Nodos principales:**

1. **Webhook** (path definido en GHL Workflow que dispara el evento).
2. **Normalize** — extraer `contact_id`, `appointment_id`, `calendar_id`, `programa`, `assigned_to` (userId asesor).
3. **Route por programa** — Switch por programa/asesor a los mensajes de confirmación correctos.
   - **BORRAR** path Diego García (`Y1cWtQ0KoVhP9U1iD7MV`) — sale del ruteo automático (decisión cliente 18/8).
4. **Fix bug marca-antes-de-enviar**: en el viejo, `Agendan cita = true` se escribe antes del envío y la cadena muere después. Nuevo orden:
   - Enviar mensaje de confirmación (WhatsApp + email)
   - **Después** marcar `Agendan cita = true` (custom field GHL)
5. **Respond** al webhook.

**Detalles pendientes:**
- IDs de los 8 asesores GHL (userIds).
- Templates de confirmación por programa (variables: fecha, hora, asesor, link Zoom si aplica).
- Recordatorios pre-cita 24h + 1h (decisión cliente 18/8) — pueden ir en un W6b separado.

---

## Trabajos siguientes (POST-2 · post-cutover)

- Update el nodo `elevar` del main con el mapping correcto de programa→userId (agent decide `user_id` con criterio; documentar en prompt v2.3).
- Debounce +20s en `main-venttur-ghl` (agregar Wait + poll `vtr_message_buffer` como red doble).
- Migrar los nodos Airtable de `main-venttur-ghl` a escrituras GHL (Contact/Opportunity vía PIT) durante watch mode (4-5 días post-cutover).

## Snapshots

| Archivo | sha256 | Descripción |
|---|---|---|
| `main-venttur-ghl-v0.1.json` | `4b67f96708fe1dc47014b7f178da7b95ce29ef346a0b6d88e689b6acf3eef186` | main duplicado + adapter GHL + dedup + elevar reescrita |
| `vtr-tool-elevar-ghl.json` | `9c7418f7ff64b3559c43f0cac4aa2f85223dfcf26cb28a28f3e96bd84ddd688d` | Sub-workflow 3 pasos (dnd + assign + telegram) |

Ambos OFF. `main-venttur-ghl-v0.1` webhook path revela el path random asignado.

## Scripts fuente

- `scratchpad/vtr_batch_c_main.py` — construcción main-venttur-ghl.
- `scratchpad/vtr_batch_c_elevar.py` — construcción sub-workflow elevar + wire al main.
