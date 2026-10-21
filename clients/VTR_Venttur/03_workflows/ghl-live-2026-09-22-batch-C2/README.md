# Batch C.2 · W4 · W6 · W9 · W10 (GHL) · 2026-09-22

Construidos por Codex el 2026-09-22 (sesión de continuación). **Todos OFF** hasta CUTOVER-2.
Creados por API (`POST /workflows` → inactivo por defecto). Field IDs / userIds / calendars / opciones
SINGLE_OPTIONS verificados contra la API GHL viva antes de construir.

## IDs y webhook paths

| Rol | ID n8n | Trigger | Webhook path | sha256 snapshot |
|---|---|---|---|---|
| W4 · Formulario landing → Contact GHL | `LhPSfMYtQbNcEK32` | Webhook | `vtr-form-landing-ghl-08d86c06` | `55bf2ce4…10003f` |
| W6 · Confirmación agenda GHL | `AS9ZNhY3GJDfhY3P` | Webhook | `vtr-confirmacion-agenda-ghl-a191d178` | `571892608d…0df1173` |
| W9 · Actualizar link_enviado → GHL | `TROsQ5h78baAuVOY` | Execute Workflow | — | `4a56c37c2f…b9b3578` (self-enrich) |
| W10 · Outreach Sheet → Contact GHL (ingesta) | `MbPTKvy0bq8b4YAw` | Google Sheets Trigger | — | `70595a4826…cbf6bfc` |

Scripts fuente: `00_migracion_ghl/05_ejecucion/scripts/batches-2026-09-22/vtr_batch_c2_w4_w9_w10.py`
+ `vtr_batch_c2_w6.py` (idempotentes por nombre de workflow).

## Patrón GHL (replicado del batch-C main + elevar)

- Cred header-auth **`GHL VTR (PIT)` id `YkVmaA4jlRbO1TQD`** (aporta `Authorization: Bearer <PIT>`).
- `authentication: genericCredentialType` + `genericAuthType: httpHeaderAuth`.
- `customFields: [{id, value}]` (formato confirmado en W11 `qYgeTc9PCq3TiGDn` + despachador).
- Header `Version`: **`2021-07-28`** para `/contacts/*`, **`2021-04-15`** para `/conversations/messages`.
- `LocationId: 7aXb4JCKsWV5nUyBXeSF`.

## Field IDs usados (contact custom fields, verificados en GHL)

`programa_interes`=`xK2NFqtz1DYUw3gYdn8I` (SINGLE_OPTIONS) · `atribuida_a`=`yEgBeLQNnCPkTTv8OvfX` ·
`link_enviado`=`rHzGNiesWuESPmSZyviJ` (CHECKBOX) · `folio`=`S80aYglwiVLkMsf95Ddz` ·
`fbclid`=`8REOsOHYC3boWRY74Rx5` · `agendan_cita`=`LwXu8AxMLhVGCbNmgzm2` (CHECKBOX) ·
`estado_conversacion`=`Omg1BvHmpXR0MMGsrpFh` (SINGLE_OPTIONS) · `origen`=`BEhJWnXS9SQovJTLSA2W` (="Form Meta") ·
`ad_name`=`McKjVHiSyU1IU3G1PpN1` · `platform`=`ffxBAFkCuCgBI1vo8PmS` (ig/fb) ·
`grado_escolar`=`HjNeRtIv6XHHMgFbtsaR` · `inicio_deseado`=`dUvMI4NaamfRPOF1p95q` ·
`nivel_ingles`=`uOecQsOv9i3uwMeSgEkX` (básico/intermedio/avanzado) · `fuente_lead`=`2hv0GovhSzZO3hj9cFqm` ·
`tipo_contacto`=`4sj9sWAen1PvGCkn9eCN` (Padre/Madre·Estudiante·No especificado) ·
`toques_enviados`=`ez934lu03v7nC4ZRS7LJ` · `outreach_enviado`=`wFD12kJI9fCufQmvHAGc` ·
`touch1_programado_at`=`95bG6wvWFk2ma17T4NuE`.

**`programa_interes` valores canónicos válidos (8):** Internados · Intercambio académico con familias ·
Viajes educativos · Educación superior · Campamentos de verano · Cursos de idiomas en el extranjero ·
Pathway Alemania · Gap Year / Estudia y Trabaja. Si el `programa` del form no matchea ninguno
(ej. "Francia" que es destino, no programa), NO se escribe `programa_interes` (se preserva como tag).

---

## W4 · Formulario landing → Contact GHL (`LhPSfMYtQbNcEK32`)

**Reemplaza** `ZB6erhWicZmDfC4I` (Formulario Clientify).

`Webhook → Normalize (build GHL body) → POST /contacts/upsert → Responder OK`.

- **Payload de landing** (mismo que el webhook viejo): `body.{nombre, apellidos, telefono, programa, folio, fbclid_completo, atribuida_a?, email?}`.
- **Normalize** canoniza: teléfono → `+521<10>` (formato D5), programa → uno de los 8 canónicos, arma `ghl_body` con `customFields` (folio, programa_interes si matchea, atribuida_a, fbclid) + `tags` [Form Landing, programa].
- Idempotencia por teléfono (upsert nativo GHL). Sin gate.

> **Nota folio/CAPI:** el registro del folio para Meta CAPI vive en su webhook dedicado
> `4HgMkK34xqITULM3` (path `capi-registro-folio-vtr-supabase`), mismo payload de landing.
> **La landing rebuildeada (PREP-5) debe postear a AMBOS**: W4 (contacto) + `4HgMkK34xqITULM3` (folio).
> W4 guarda `folio` como custom field de referencia, no reemplaza el registro CAPI.

## W6 · Confirmación agenda GHL (`AS9ZNhY3GJDfhY3P`)

**Reemplaza** `2PSekVBxarsrnVBu` (Confirmación agenda · 3 GCal Triggers).

`Webhook → Normalize + build msg → 1. Enviar confirmación (WhatsApp) → 2. Marcar agendan_cita=true → Responder OK`.

- **Trigger nuevo:** webhook GHL "Customer Booked Appointment" (no GCal Trigger). Path `vtr-confirmacion-agenda-ghl-a191d178`.
- **Diego BORRADO** del ruteo (D9): no hay Switch por asesor; el asesor viene en el payload.
- **Fix bug marca-antes-de-enviar:** primero envía la confirmación, DESPUÉS marca `agendan_cita=true` + `estado_conversacion="Cita confirmada"`.
- Mensaje: "asesoría" (pathway/superior) vs "cita" + fecha CDMX (luxon `DateTime`, con try/catch que degrada si falla) + link de reunión si viene.

> ✅ **Lado GHL (UI) creado por Camilo (2026-09-22):** el **GHL Workflow** con trigger *Customer Booked
> Appointment* + acción *Webhook* que POSTea a `https://[TU-INSTANCIA-N8N]/webhook/vtr-confirmacion-agenda-ghl-a191d178`.
> **Contrato del payload que ese GHL Workflow debe enviar:**
> ```json
> { "contact_id": "{{contact.id}}", "first_name": "{{contact.first_name}}",
>   "programa": "{{contact.programa_interes}}", "appointment_start": "{{appointment.start_time}}",
>   "meeting_link": "{{appointment.meeting_location}}" }
> ```
> El Normalize acepta variantes (`contactId`, `startTime`, `address`…) por robustez.
> Recordatorios pre-cita 24h + 1h = **W6b separado** (no incluido acá, decisión del cliente 18/8).

## W9 · Actualizar link_enviado → GHL (`TROsQ5h78baAuVOY`)

**Reemplaza** `gRSMjzxggA4UePjz` (Airtable).

`Execute Workflow Trigger → Preparar payloads → PUT link_enviado=true + tags → Disparar Rescate (webhook)`.

- **Input contrato:** `{contact_id, phone, programa, first_name, opportunityId?}`.
- Marca `link_enviado=true` + tags [LINK_ENVIADO, programa] en GHL.
- **Dispara el Rescate GHL** por HTTP POST a `https://[TU-INSTANCIA-N8N]/webhook/vtr-rescate-link`
  (el Rescate `YB0UxwEVwzISdd54` usa **webhook trigger**, no Execute Workflow — por eso W9 postea al webhook).
  Body: `{first_name, programa_interes, phone, contactId, opportunityId}` (shape que consume el Rescate).

> 🔴 **W9 no está cableado al main todavía** — ver "Hallazgo crítico" abajo.

## W10 · Outreach Sheet → Contact GHL · ingesta (`MbPTKvy0bq8b4YAw`)

**Reemplaza** `CUuFxbst3iHpgeXS` (37 nodos · solo la parte de **ingesta**; el tri-toque migró al despachador).

`Sheets Trigger → Normalize Payload → IF (_error?) → [false: Build GHL body → POST /contacts/upsert] [true: Descartar]`.

- **Sheets Trigger** idéntico al viejo (doc `1HzJVMBwnGikiI_U805N7oqcXPYE7TjEFTL1rqdcCEIU`, gid `160362675`, rowAdded, cred `xjVkf0DxxXJ7sMSa`).
- **Normalize Payload = reusado verbatim** del W10 viejo (parsePhone/splitName/deriveTipo/deriveFuente battle-tested, maneja `p:MX` + whatsapp vacío → rama `_error`).
- **Build GHL body**: mapea a valores SINGLE_OPTIONS válidos (platform ig/fb, nivel_ingles lowercase, tipo_contacto). `programa_interes="Internados"` (Outreach = Boarding School), `origen="Form Meta"`, `outreach_enviado=false`, `toques_enviados=0`. Tags [Origen: Form Meta, Internados].

---

## Validación hecha (offline · el smoke real es CUTOVER-3)

- Round-trip: los 4 GET-eados de n8n → `active=false`, triggers y webhook paths correctos.
- `node --check` de los 6 code nodes → OK.
- Lógica JS ejecutada con payloads realistas (W4 boarding + W4 Francia-sin-match + W9 + W10 válido + W6 Pathway):
  field IDs correctos, todos los valores SINGLE_OPTIONS dentro de las opciones válidas, teléfono en `+521<10>`.

---

## ✅ Refactor del main-venttur-ghl (`1eS1Z5k898c3ATnf`) — era un SCAFFOLD, ahora refactorizado a GHL

El main nuevo es un **duplicado del main ManyChat viejo** con solo 3 cosas cambiadas en Batch C.1:
entrada (Normalize GHL + dedup), salida (`Enviar WPP` → GHL `/conversations/messages`), y la tool `elevar`.
**Todo el resto sigue siendo lógica ManyChat/Airtable** apuntando a sub-workflows VIEJOS:

| Nodo del main | Apunta HOY a (viejo) | Debería apuntar a (nuevo) | Input que pasa hoy | Input que espera el nuevo |
|---|---|---|---|---|
| `Estampar estado (Contestó)` | `b52CUYEkI2Ah3Xj6` (Airtable, por teléfono) | **W11 `qYgeTc9PCq3TiGDn`** | `{telefono}` | `{contactId}` |
| `Actualizar link` | `gRSMjzxggA4UePjz` (Airtable) | **W9 `TROsQ5h78baAuVOY`** | `{id_airtable: phone, mensaje}` | `{contact_id, phone, programa, first_name}` |
| `Meta CAPI` | `z98w2yWVEMOfifMl` (viejo, lee Airtable) | **`mf7VQJelfieCDJ5r`** (Supabase) | passthrough ManyChat | passthrough |
| `Execute Workflow` (Resumen/etiquetas/seguim) | `DyrDumQgb6S4zHsS` | **clasificador `Xmyoewwa1W5gm1fy`** | `{tel, id_manychat}` | `{conversation, contactId}` |

Además residuo ManyChat/Airtable en el propio main: 7 nodos Airtable (memoria/tracking) + 1 nodo
`Settear variables` (HTTP a ManyChat, muerto en GHL). `Responder rápido ManyChat` es solo un
`respondToWebhook` (nombre leftover, inofensivo).

**Impacto al cutover si NO se re-cablea:**
- `estado_conversacion` y `link_enviado` se escriben en **Airtable, no en GHL** → el **despachador**
  (nurturing + rescate, con los templateId que cableó Camilo) **queda inerte**: sus queries a GHL
  (`estado_conversacion IN (...)`, `link_enviado=true`) no encuentran a nadie.
- `tipo`/`programa`/`resumen` no se pueblan en GHL → **CUTOVER-3 smoke falla** (verifica esos custom fields).
- El nuevo Rescate GHL nunca se dispara (lo dispara W9, que no está cableado).
- Meta CAPI puede seguir funcionando degradado (el path viejo lee folios de Airtable, que aún existen).

**El batch plan encuadró la migración Airtable→GHL de los nodos inline como "watch-mode", pero el
re-pointing de estos 4 Execute Workflow a los nuevos sub-workflows GHL nunca se abordó.** No es
watch-mode: los nuevos sub-workflows escriben a GHL, de lo que depende el despachador.

Además, al cablear se descubrió que el scaffold es más profundo: **14 nodos** leían campos ManyChat
crudos (`body.whatsapp_phone`, `body.id`, `id_manychat`) que el payload GHL no trae, el `Settear
variables` (ManyChat, muerto) estaba **en el camino de salida** (halt-earía el envío), y el sessionKey
de memoria era solo-dígitos (inconsistente con el `+521<10>` de rescate/despachador).

### Refactor aplicado (2026-09-22 · decisión la agencia: "refactor completo ahora" · inbound manda `contact_id`+`phone`)

Snapshot pre-refactor: `pre/main-venttur-ghl-pre-rewire.json` (sha `4b67f967…3eef186`).
Snapshot post-refactor: `main-venttur-ghl-v0.2-refactor.json` (sha `212cff6f…128e93e3`). **Sigue OFF.**
Script: `05_ejecucion/scripts/batches-2026-09-22/vtr_c2_main_refactor.py` (con validación pre-PUT).

1. **`Normalize GHL Payload` enriquecido**: emite `session_key` (+521<10>, vía `nsk()` idéntico al del
   rescate/despachador — verificado que matchea en todos los formatos GHL), `whatsapp_phone`, `id`
   (=contactId) para compat legacy, además de `contact_id`/`phone`/`wa_id`/`text`.
2. **14 refs ManyChat → `$('Normalize GHL Payload').first().json.{session_key|wa_id|id}`** (10 patrones
   string, todos matcheados y verificados; incluye memoria, tools, Airtable, guardrail, alerta).
3. **3 Execute re-apuntados a los sub-workflows GHL nuevos:**
   - `Estampar estado (Contestó)` → **W11 `qYgeTc9PCq3TiGDn`** input `{contactId}` (fire-and-forget).
   - `Actualizar link` → **W9 `TROsQ5h78baAuVOY`** input `{contact_id, phone}` (W9 auto-enriquece
     programa/first_name vía GET contact — ver W9 arriba, ahora 5 nodos).
   - `Execute Workflow` (Resumen) → **clasificador `Xmyoewwa1W5gm1fy`** (renombrado `Clasificar postconv (GHL)`),
     input `{conversation, contactId}`, **movido a per-turn**: cuelga de `Responder rápido ManyChat` vía
     nodo nuevo `Armar conversación (memoria)` (Postgres, `string_agg` sobre `n8n_chat_histories` por
     `session_key`) + concat del mensaje actual. Fire-and-forget. Antes corría solo en primer contacto.
4. **`Settear variables` (ManyChat) bypasseado**: `Normalizar burbujas → Enviar WPP` directo + nodo
   `disabled`. Crítico: sin esto el envío halt-eaba al cutover.
5. **sessionKey de memoria** → `+521<10>` desde Normalize → continuidad memoria bot↔rescate↔despachador.

### ⚠️ Deferido / flags post-refactor

- **Meta CAPI: NO tocado (decisión de seguridad, investigado a fondo 2026-09-22).** El nodo del main sigue
  → viejo `z98w2yWVEMOfifMl` (fire-and-forget). **Ambos (`z98w2yWVEMOfifMl` viejo Y `mf7VQJelfieCDJ5r`
  nuevo) tienen el Trigger DESCONECTADO** → activarlos es un no-op (no dispara nada, no manda eventos
  equivocados). Es el estado seguro-pero-degradado (sin tracking de conversiones). **Hallazgos precisos
  para quien lo arregle (necesita contexto CAPI):**
  - El folio SÍ se lee bien de Supabase: `Buscar Folio en Airtable1` (nombre stale) es un **Postgres**
    node que hace `SELECT ... FROM capi_folios WHERE folio=$1` (cred `Venttur ihpvM7nYMdLCwWDP`). ✅
  - La entrada real es `contiene_folio_compacto` (IF sobre `$json.body.custom_fields.respuesta_definitiva`
    con regex de folio `[XXXXXX_BS|BSG|HF|...]`) — **shape ManyChat**, no GHL.
  - ⚠️ **Riesgo:** la rama FALSE de `contiene_folio1` conecta a `Buscar Config Programa2 → Preparar CAPI
    Data2 → HTTP Request Meta CAPI2` (`POST graph.facebook.com/v21.0/{pixel_id}/events`). Reconectar el
    trigger a ciegas puede disparar eventos de conversión **equivocados** a Meta en cada mensaje sin folio.
    Por eso NO se reconectó.
  - **Fix requerido (3 partes):** (1) re-apuntar el nodo `Meta CAPI` del main → `mf7VQJelfieCDJ5r`;
    (2) alimentarle el folio del contacto GHL (custom field `folio S80aYglwiVLkMsf95Ddz`) en un shape que
    la entrada reconozca — el main hoy manda passthrough sin folio; (3) reconectar `Trigger →
    contiene_folio_compacto` **y** auditar/guardar la rama FALSE para que no dispare eventos sin folio.
    Validar offline (no debe mandar evento sin folio válido) antes de activar.
- **Tools `crear_contacto` + `primer_registro`** siguen → sub-workflows viejos Clientify+Airtable
  (sus refs de input se arreglaron a Normalize, funcionan en watch-mode). En GHL el contacto ya existe,
  así que son redundantes; y Clientify muere en CIERRE-1 (sábado) → post-sábado `crear_contacto` fallaría.
  Watch-mode / migrar antes del sábado.
- **7 nodos Airtable inline** (memoria/tracking) siguen escribiendo a Airtable con keys GHL (watch-mode
  deliberado, plan original).

## Pendientes de este batch

- 🔴 **Meta CAPI**: fixear `mf7VQJelfieCDJ5r` (trigger desconectado) + alimentar data del lead + re-apuntar el main. Decisión de scope pendiente.
- ✅ **W6 + main inbound**: los 2 GHL Workflows inbound (*Customer Replied* → main, *Customer Booked Appointment* → W6) **creados por Camilo (2026-09-22)**. Falta verificación E2E en CUTOVER-3.
- ✅ **Tools Clientify**: resuelto por la paridad con staging (`vtr_c3_main_paridad_staging.py`): `crear_contacto` → PUT contacto GHL, `primer_registro` deshabilitado.
- 🟢 Smoke E2E real de los 4 + del main refactorizado en CUTOVER-3.

## Revisión 22/9 noche (post-paridad)

- **Main a paridad con el staging** (`batches-2026-09-22/vtr_c3_main_paridad_staging.py`, 53 nodos, OFF):
  prompt staging, `crear_contacto` → GHL, `elevar` con `contact_id` + `user_id` determinísticos,
  `cerrar_conversacion`, `[ESTADO DEL LEAD]` desde GHL. Pre: `pre/main-venttur-ghl-pre-paridad.json`.
- **Despachador · política de recontacto** (`batches-2026-09-22/vtr_post2_despachador.py --politica`, aplicada):
  mínimo 24 h entre toques (antes: 2 toques con 1 h de diferencia) + históricos sin fecha excluidos. Envío
  sigue deshabilitado; se habilita en C2 con `--habilitar-envio`. Pre: `pre/despachador-pre-post2-0f1496dd.json`.
- **`cutover-toggles.py`**: prende antes de apagar; modos `--solo-on` / `--solo-off`; los sub-workflows
  (W9, W11, clasificador, Meta CAPI) ya no se activan (corren igual inactivos; `/activate` daba error).
- Snapshot de los 20 workflows (stack nuevo + 6 viejos): `03_workflows/ghl-live-2026-09-22-post-paridad/`.
