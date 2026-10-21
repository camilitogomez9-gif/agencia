# 02 — Triggers y Eventos

> **Reescrito 2026-07-24** con los inputs completos de Etapa 0 (14 workflows n8n + snapshot de datos de las 5 plataformas + 6 CSVs Airtable + system prompt del agente + schema Supabase). Supera la versión de mayo 2026, que se generó con inputs parciales y contenía errores materiales (ver "Correcciones vs. versión mayo 2026" y doc 06).
>
> **Fuentes:** los 14 JSON de `00_inputs/wf-*.json` (análisis nodo-por-nodo); `04_agents/agente-venttur-system-prompt-EXTRAIDO-2026-07-24.md` (system prompt del agente "Mauricio", ~39K chars); `06_docs/template-texts-canonical.md` (15 textos de templates + memoria sintética); `00_inputs/manychat-flows-content-2026-07-20.md` (contenido interno de 15 flows ManyChat); `00_inputs/supabase-queries-venttur.md` (schema + quirk MX); `00_inputs/airtable-csvs/{leads,folios-capi,programas-capi,mensajes-anuncios,reporte-semanal}.csv`; `00_inputs/manychat-snapshot-2026-05-13.md` + `vtr-data-snapshot-2026-07-24.json`.

---

### Correcciones vs. versión mayo 2026

- ❌ **"El sistema no tiene agente conversacional IA; es puramente reactivo" → FALSO.** El corazón del sistema es un AI Agent conversacional ("Mauricio", gpt-4o, temp 0) que vive inline en el nodo `Agente IA WPP` del workflow principal (`k3aivKSP67S97IHn`). Toda la sección conversacional de este doc es **nueva** (categoría "Conversacional" no existía en mayo).
- ❌ **Rescate "No activado / vive en ManyChat" → FALSO.** Está **LIVE como workflow n8n** `mkEP1qFN7MVb9qP0` (Fase 1 a 45 min + Fase 2 a 24 h) con memoria sintética. El flow viejo de ManyChat quedó reemplazado.
- ❌ **Outreach proactivo WA "No implementado" → FALSO.** Está **LIVE** (`CUuFxbst3iHpgeXS`), tri-toque (Touch 1/2/3) disparado por Google Sheets Trigger + Cron, con 8 campos de cualificación, Lead Score, memoria sintética y rama de error.
- 🆕 **Triggers de ESTADO DE LEAD** (2 workflows: "Contestó" `b52CUYEkI2Ah3Xj6` + "Interrumpida" `H6qYB3Oj97bxaTCX`) — no existían en la taxonomía de mayo.
- 🆕 **Nurturing 4-toques por programa** (6 drips ManyChat, disparados por `Resumen, etiquetas, seguimientos` `DyrDumQgb6S4zHsS`) — no existía en mayo.
- 🆕 **Confirmación de agenda** (`2PSekVBxarsrnVBu`, Google Calendar trigger) y **Seguimiento agenda** (`DZlSEQS5qzX1Y01K`, 48 h) — no estaban.
- 🔧 **T2 (CTWA)**: mayo asumía ruteo por `programa_wpp`. En el JSON real la rama CTWA **hardcodea `{Programa}='BS'`** — el campo `programa_wpp` NO aparece en el workflow. Corregido.
- 🔧 **T3 (Registro folio)**: mayo tenía campos supuestos (`fbclid`, `landing_url`). El body real trae `fbclid_completo` y `url`; `fbc` se **deriva** (no llega); `ip` sale del header `x-forwarded-for`. Corregido con detalle nodo-por-nodo.
- 🔧 **Cadencia outreach**: mayo/histórico decían "+1h" para Touch 1. El JSON v4 real usa `touch1At = new Date()` (sin delay) → cadencia **0h / +24h / +72h desde creación**. Corregido.
- La taxonomía pasa de **7 triggers en 3 categorías** a **~18 triggers/eventos en 8 categorías**.

---

## 🆕 Validación con el cliente — 2026-08-17 (Etapa 2)

> Respuestas de **Mauricio García** (revisadas sobre el borrador de Max) al cuestionario
> `02_validacion_cliente/cuestionario-venttur-2026-07-24.md`. Lo de acá abajo **supera** al cuerpo de
> este documento donde haya conflicto. Mapeo completo a las preguntas internas en
> `02_validacion_cliente/preguntas-cierre-2026-07-24.md` (A1..A11). Lo que quedó abierto está en
> `02_validacion_cliente/puntos-abiertos-ronda-2-2026-08-18.md`.
>
> **Fecha objetivo de cutover confirmada: 15 de septiembre de 2026.**

### Lo que cambia en la taxonomía de triggers

**1. T2 (CTWA) — el hardcode `{Programa}='BS'` queda CONFIRMADO COMO CORRECTO, por ahora.**
Hoy Internados es la única campaña activa en Meta, así que todos los CTWA son efectivamente de
Boarding. El Hallazgo 4 baja de *"⚠️ intencional vs. bug"* a **"correcto hoy, insostenible mañana"**:
en cuanto activen la segunda campaña atribuye mal. Requisito del cliente para Etapa 3: la atribución
tiene que ser **data-driven** (una fila por programa en la tabla de config), de modo que agregar un
programa sea agregar una fila y nunca tocar un workflow.

**2. Los keyword triggers de CTWA se cierran por obsolescencia, no porque los hayamos conseguido.**
Seguimos sin tenerlos (la API de ManyChat no los expone), pero dejan de hacer falta: el cliente separó
explícitamente las dos funciones que hoy están mezcladas en ese trigger.

- **Atribución** → automática, desde el payload de referral de Meta. No le pregunta nada al lead.
- **Conversación** → el programa lo determina **lo que diga la persona**, nunca el anuncio.

→ Este pendiente de Etapa 0 queda **cerrado**.

**3. 🚨 Existe una familia de triggers fuera de nuestro perímetro: los recordatorios de cita.**
Salen de **Clientify**, desde un segundo número de WhatsApp, y por eso no aparecen en ninguno de los
14 workflows de esta taxonomía. No están documentados acá porque no los veíamos. El cliente los va a
compartir (config + textos) para replicarlos en GHL sobre el número único.

**4. La confirmación de cita pasa a ser un trigger obligatorio para los 3 asesores.**
Confirmado: todos reciben confirmación al agendar, sin importar el asesor. Combinado con A3 (Diego
sale del ruteo), el `wf-confirmacion-agenda` queda así: **el path de Diego se borra** (no se arregla),
y solo hay que reparar el de Andrés. Ver Hallazgo 8.

**5. Trigger nuevo de agendamiento: 8 calendarios GHL, uno por programa.**
Requisito duro: los calendarios de un mismo asesor **comparten disponibilidad real** (agendar
"Internados" el martes 16:00 bloquea ese horario también en "Intercambio académico" y "Campamentos").
El programa queda determinado en el momento del agendamiento, sin etiquetado manual posterior.

**6. La landing `go.venttur.com/bs` tiene que repuntar su webhook a GHL** (hoy pega a ManyChat +
Clientify). Es el único trigger de landing vivo; los otros 7 programas no tienen.

---

### ⚠️ Nota sobre la versión que el cliente respondió

El cuestionario que Mauricio contestó es la **versión de 12 preguntas enviada el 2026-08-07**. El
archivo del repo se amplió a **14 preguntas el 2026-08-17** (tras el Reporte la agencia 1), agregando
*rangos de precio* y *qué significa "Cerrada"*, y reescribiendo las de seguimiento y confirmación de
cita. **Esas cuatro modificaciones nunca le llegaron al cliente.** Por eso hay respuestas que
contestan la redacción vieja, y dos temas que quedaron sin preguntar. Se resuelven en
`puntos-abiertos-ronda-2-2026-08-18.md`.


## 0. Panorama: cómo distinguir un TRIGGER de un EVENTO INTERNO

Este doc usa dos niveles:

- **Trigger** = un punto de entrada que arranca una ejecución de workflow (webhook, cron, calendar trigger, Execute-Workflow desde un padre, Sheets Trigger). Es lo que "prende" el sistema.
- **Evento interno** = una decisión/acción disparada *dentro* de una ejecución ya corriendo (típicamente una tool que el agente decide invocar, o un handoff fire-and-forget a un sub-workflow). No es un entrypoint propio, pero es un "momento" de negocio que la migración a GHL tiene que preservar.

Ambos importan para GHL porque en GHL muchos de estos colapsan: un "Inbound Message" nativo reemplaza al webhook ManyChat + el debounce + el anti-dedup, un "Appointment Booked" reemplaza al Calendar-trigger + el cruce Clientify→Airtable, etc.

### Tabla-resumen de todos los triggers/eventos

| # | Trigger / Evento | Categoría | Origen (trigger real) | Workflow (id) | Estado |
|---|---|---|---|---|---|
| **T1** | CAPI con folio | Atribución | Execute-WF desde main (paralelo, cada mensaje) | Meta CAPI `z98w2yWVEMOfifMl` (rama folio) | LIVE (JSON export `active:false`, ver nota) |
| **T2** | CAPI CTWA (sin folio) | Atribución | Execute-WF desde main (misma llamada) | Meta CAPI `z98w2yWVEMOfifMl` (rama CTWA) | LIVE (idem) |
| **T3** | Registro de folio (landing→n8n) | Atribución | Webhook `capi-registro-folio-venttur` | CAPI Registro Folio `9yCbynoKDt9hgiBq` | **LIVE (`active:true`)** |
| **C1** | Mensaje entrante WhatsApp (→ agente Mauricio) | Conversacional | Webhook `43fa146c-…` (llamado por ManyChat) | Main `k3aivKSP67S97IHn` | **LIVE (`active:true`)** |
| **C2** | Tool `crear_contacto` (captura nombre+apellido) | Conversacional (evento interno) | AI Agent decide | sub-wf `cZUNKQyZNOHy5twQ` | LIVE (sub-wf `active:false`) |
| **C3** | Tool `elevar` (pedido humano / mensaje duplicado) | Conversacional (evento interno) | AI Agent decide | HTTP→ManyChat `sendFlow` elevar | LIVE (inline en main) |
| **C4** | Tool `contestan_2do` (2do mensaje del lead) | Conversacional (evento interno) | AI Agent decide (instruido en prompt) | ⚠️ **tool inexistente** (ver detalle) | Instruido, NO implementado |
| **CR1** | Formulario landing (→ Airtable+Clientify) | CRM | Webhook `ceebf4f6-…` | Formulario Clientify `ZB6erhWicZmDfC4I` | **LIVE (`active:true`)** |
| **O1** | Outreach Form Meta — ingestión (Sheets) | Engagement/Outreach | Google Sheets Trigger (`rowAdded`) | Outreach `CUuFxbst3iHpgeXS` (Flujo A) | **LIVE (`active:true`)** |
| **O2** | Outreach Touch 1 / 2 / 3 (tri-toque) | Engagement/Outreach | Cron (poll) + estado en Airtable | Outreach `CUuFxbst3iHpgeXS` (Flujo B) | **LIVE (`active:true`)** |
| **R1** | Rescate Post-Link Fase 1 (45 min) | Engagement/Rescate | Execute-WF desde `Actualizar link` | Rescate `mkEP1qFN7MVb9qP0` | **LIVE** (JSON export `active:false`) |
| **R2** | Rescate Post-Link Fase 2 (24 h) | Engagement/Rescate | Wait interno del mismo workflow | Rescate `mkEP1qFN7MVb9qP0` | **LIVE** (idem) |
| **N1** | Drip nurturing 4-toques por programa | Nurturing | Execute-WF `Resumen…` (post-conversación, +8h) | `DyrDumQgb6S4zHsS` → 6 flows ManyChat | LIVE (dispatcher; cadencia vive en ManyChat) |
| **S1** | Estado lead = "Contestó" (por inbound) | Estado | Execute-WF desde main (por mensaje) | `b52CUYEkI2Ah3Xj6` | Diseñado, deploy pendiente (ver nota) |
| **S2** | Estado = "Conversación interrumpida" (barrido) | Estado | Cron (cada 1 h) | `H6qYB3Oj97bxaTCX` | **LIVE (`active:true`)** |
| **A1** | Confirmación de agenda (agendó → flow Agenda) | Agendamiento | Google Calendar Trigger (eventCreated) ×3 asesores | `2PSekVBxarsrnVBu` | **LIVE (`active:true`)** |
| **A2** | Seguimiento agenda (48 h post-link sin cita) | Agendamiento | Execute-WF (nodo DISABLED en `Actualizar link`) | `DZlSEQS5qzX1Y01K` | Diseñado, hoy NO se invoca (nodo padre disabled) |
| **OP1** | Correo semanal (reporte) | Operativo/Reporting | Schedule Trigger (lunes 10h) | `BrFfQyDfamdUzq64` | Diseñado, NO en producción (modo test) |

> **Nota sobre `active:false` en varios JSON**: varios workflows LIVE en producción (Meta CAPI, Rescate) aparecen con `active:false` en el export que está en `00_inputs/`. Para **sub-workflows** invocados por Execute-Workflow, el flag `active` es irrelevante (corren cuando el padre los llama). Para el resto, el flag del export no prueba el estado vivo — el CLAUDE.md del proyecto documenta Rescate y Outreach como "en producción ✅". Se marca cada caso individualmente. (⚠️ INCIERTO — el estado activo real de cada workflow en el n8n vivo no es 100% deducible del export; impacto: para el corte de migración hay que confirmar en la instancia viva cuáles disparan de verdad.)

---

# CATEGORÍA A — ATRIBUCIÓN (Meta CAPI)

Tres triggers que en conjunto reconstruyen la huella de Meta (fbc/fbp/fbclid/ip/user_agent) para atribuir la conversión "Lead" server-side. Dos viven en el sub-workflow **Meta CAPI** (`z98w2yWVEMOfifMl`), uno en **CAPI Registro Folio** (`9yCbynoKDt9hgiBq`). El pixel del navegador (client-side) vive en la landing, fuera de n8n.

## T1 — CAPI con Folio (landing → WhatsApp)

**Categoría:** Atribución · **Estado:** LIVE (rama del sub-wf Meta CAPI)

### Origen / condición de activación

El main (`k3aivKSP67S97IHn`) invoca el sub-workflow Meta CAPI **en paralelo, en cada mensaje entrante** (nodo `Meta CAPI` → `executeWorkflow z98w2yWVEMOfifMl`, `waitForSubWorkflow:false`, inputs vacíos). Dentro del sub-workflow, el nodo router `contiene_folio` (IF) evalúa si `custom_fields.respuesta_definitiva` **contiene la palabra "Folio"**. Si sí → rama FOLIO (T1).

Formato esperado del texto: `... Folio: <valor> | ... Prog: <valor>)`. El folio matchea `/Folio:\s*(.+?)\s*\|/i`; el programa `/Prog:\s*([^\s)]+)/i`. Si falta cualquiera de los dos, el nodo `Extraer Folio + Hashear1` hace `throw new Error(...)` y aborta (dispara el errorWorkflow `OBkUyb8fuo30DzA9`).

> ⚠️ INCIERTO — el discriminante NO es un campo estructurado sino una búsqueda de substring "Folio" dentro de texto libre del agente (impacto: frágil; si el agente reformula, se rutea mal. En GHL conviene un flag `origen` explícito).

### Flujo (nodo por nodo, rama FOLIO)

```
[main dispara en paralelo] → Meta CAPI sub-wf → contiene_folio (IF: contains "Folio")
  └─ TRUE →
    1. Extraer Folio + Hashear1 (Code) — SHA-256 puro en JS (sin crypto/require),
       normaliza lowercase+trim, encoding UTF-8 manual. Parsea folio + Prog por regex.
       Emite: folio, programa (UPPER), hashed_phone, hashed_fn, hashed_ln, event_time (s Unix).
    2. Buscar Folio en Airtable1 (Folios CAPI [AIRTABLE_TABLE_ID], {Folio}=<folio>)
       → recupera fbc, fbclid, Timestamp, fbp, user_agent, ip, Landing URL
    3. Buscar Config Programa1 (Programas CAPI [AIRTABLE_TABLE_ID], {Programa}=<extraído>)
       → pixel_id, access_token, default_url  (DINÁMICO por programa)
    4. Buscar Lead por Teléfono (id)1 (Leads [AIRTABLE_TABLE_ID], {id}=telefono sin +)
    5. existe1 (IF: {id} notEmpty)
         ├─ TRUE → Update record3 (Leads, match id_2): Folio, id_2, fbclid → Preparar CAPI Data1
         └─ FALSE → Preparar CAPI Data1 (se manda igual a Meta aunque el lead no exista)
    6. Preparar CAPI Data1 (Code) — cruza folioData + folioLookup + config.
         fbc = folioLookup.fbc  ||  fbclid ? `fb.1.${Timestamp||Date.now()}.${fbclid}` : null
         user_data = { ph, fn, ln } + condicional fbc, fbp, client_user_agent,
                      client_ip_address = ip.split(',')[0].trim()
         event_source_url = Landing URL || default_url || ''
    7. HTTP Request Meta CAPI1 — POST graph.facebook.com/v21.0/{pixel_id}/events
         data:[{ event_name:"Lead", event_time, event_id:<folio>, action_source:"website",
                 event_source_url, user_data, custom_data:{folio} }], access_token en el body
    8. Update record2 (Folios CAPI, match Folio): fbtrace_id ← respuesta de Meta  [auditoría]
```

### Datos in / out

| Entrada | Fuente |
|---|---|
| `respuesta_definitiva` (texto con "Folio: X \| … Prog: Y)") | ManyChat custom field (vía main) |
| `whatsapp_phone`, `first_name`, `last_name`, `id` | ManyChat subscriber (vía main) |
| Folios CAPI: fbc, fbclid, Timestamp, fbp, user_agent, ip, Landing URL | Airtable (poblado por T3) |
| Programas CAPI: pixel_id, access_token, default_url | Airtable |

| Salida | Destino |
|---|---|
| Evento `Lead` (event_id=folio, action_source=website, match alto: ph+fn+ln+fbc+fbp+ip+ua) | Meta CAPI |
| `Folio`, `id_2`, `fbclid` | Airtable Leads (si el lead existe; match por `id_2`) |
| `fbtrace_id` | Airtable Folios CAPI (match por `Folio`) |

### Edge cases

- Folio o Prog no parseables → `throw` → aborta → errorWorkflow.
- Folio no existe en Folios CAPI → `alwaysOutputData:true` deja seguir; fbc/fbp/ip vienen vacíos → evento de menor calidad.
- Programa no existe en Programas CAPI → `pixel_id` undefined → 400 de Meta (no validado).
- Lead no existe en Leads → se salta el update, el evento se manda igual.
- ⚠️ INCIERTO — `Update record3` **busca por `{id}` pero matchea el update por `id_2`** (impacto: si `id`≠`id_2` en la base, el update puede no encontrar la fila esperada; no verificable sin datos reales).
- ⚠️ INCIERTO — `Timestamp` de Folios CAPI se usa crudo en `fb.1.{ts}.{fbclid}`. Meta espera ms; si estuviera en segundos, el `fbc` queda mal formado (el fallback `Date.now()` sí está en ms).

### event_id = deduplicación

`event_id = <folio>` es la clave de **deduplicación server-side** contra el evento del pixel del navegador (la landing dispara el pixel client-side con el mismo folio como `eventID`). Esto es lo que evita doble conteo.

---

## T2 — CAPI CTWA (Click-to-WhatsApp, sin folio)

**Categoría:** Atribución · **Estado:** LIVE (rama del sub-wf Meta CAPI)

> **Corrección clave vs. mayo:** mayo asumía que CTWA ruteaba por un custom field `programa_wpp` (ManyChat keyword trigger). **En el JSON real ese campo NO existe.** La rama CTWA hardcodea `{Programa}='BS'`. El ruteo dinámico por programa que mayo describía no está implementado en esta versión.

### Origen / condición

Misma invocación que T1 (el main dispara Meta CAPI en cada mensaje). En el router `contiene_folio`, si el texto **NO contiene "Folio"** → rama CTWA. Semántica: el lead entró directo a WhatsApp por un anuncio Click-to-WhatsApp, sin pasar por landing (sin folio). El Sticky Note del propio workflow lo documenta: *"Esta rama se activa cuando los leads llegan a WA por anuncio CTWA (no pasa por landing)"*.

### Flujo (rama CTWA)

```
contiene_folio → FALSE →
  A. Buscar Config Programa2 (Programas CAPI, {Programa}="BS")   ← HARDCODEADO a BS
  B. Folio (N/A) (Leads, match ID Manychat): Folio="N/A (WA)", ID Manychat=<id>, fbclid="-"
  C. Preparar CAPI Data2 (Code) — SHA-256 minificado inline.
       phone = whatsapp_phone.replace(/\D/g,'');  event_time = s Unix
       event_id = `CTWA_${phone}_${event_time}`   ← id sintético, SIN dedup real
       user_data = { ph, fn, ln }                  ← sin fbc/fbp/ip/ua
       event_source_url = config.default_url || ''
  D. HTTP Request Meta CAPI2 — POST /{pixel_id}/events
       data:[{ event_name:"Lead", event_time, event_id:"CTWA_...",
               action_source:"system_generated", event_source_url,
               user_data, custom_data:{origen:"CTWA"} }]
       (nodo TERMINAL — NO hay writeback de fbtrace_id en CTWA)
```

### Diferencias FOLIO vs CTWA (relevante para GHL)

| Aspecto | FOLIO (T1) | CTWA (T2) |
|---|---|---|
| Discriminante | msg contiene "Folio" | no contiene "Folio" |
| event_id | `<folio>` (dedup real) | `CTWA_<phone>_<ts>` (sin dedup) |
| action_source | `website` | `system_generated` |
| custom_data | `{folio}` | `{origen:"CTWA"}` |
| Señales de match | ph+fn+ln+fbc+fbp+ip+ua | solo ph+fn+ln |
| Config programa | dinámica (`{Programa}=<extraído>`) | **fija `{Programa}="BS"`** |
| Update lead | `id_2` + Folio + fbclid | `ID Manychat` + "N/A (WA)" + "-" |
| Writeback fbtrace_id | sí (Folios CAPI) | no |

### Edge cases

- Match débil: sin fbc/fbp/ip, la atribución CTWA es de menor calidad y sin deduplicación → riesgo de sub-atribución o doble conteo.
- Teléfono vacío → `event_id = "CTWA__<ts>"` y hash de string vacío (no validado).
- ⚠️ INCIERTO — el hardcode `{Programa}='BS'` puede ser intencional (un solo pixel para todo CTWA) o un placeholder/bug (impacto: todos los eventos CTWA se atribuyen al pixel `228398216567258`, aunque el lead venga de otra campaña; en GHL hay que decidir si CTWA debe mapear por campaña, equivalente a los "keyword triggers CTWA" que mayo daba por pendientes).

---

## T3 — Registro de Folio (landing → n8n)

**Categoría:** Atribución · **Estado:** **LIVE (`active:true`)** · Workflow `9yCbynoKDt9hgiBq`

> **Corrección vs. mayo:** en mayo T3 "no tenía JSON". Ahora existe y es un webhook simple de 5 nodos. Los nombres de campo reales difieren de lo asumido: la landing manda `fbclid_completo` (no `fbclid`) y `url` (no `landing_url`); `fbc` se **deriva** (no llega); `ip` sale del header, no del body.

### Origen / condición

Webhook POST `capi-registro-folio-venttur` (URL `https://[TU-INSTANCIA-N8N]/webhook/capi-registro-folio-venttur`). Lo dispara la landing `go.venttur.com` en el **momento del clic-a-WhatsApp** (confirmado por pinData: `origin/referer = https://go.venttur.com`, request desde el in-app browser de Facebook Android `FB_IAB/FB4A`, y `body.origen="clic_whatsapp_directo"`). NO se dispara en el load de la página, sino en el clic.

Es el paso que "guarda la huella de Meta" para que T1 la reconstruya después cuando el lead menciona el folio en WhatsApp. **T3 precede a T1.**

### Flujo (5 nodos)

```
Webhook Registro Folio → ¿Folio válido? (IF: body.folio notEmpty)
   ├─ TRUE  → Extraer y Enriquecer (Code) → Guardar Folio en Airtable → Responder OK
   └─ FALSE → Responder OK   (responde {ok:true} igual, SIN guardar ni loguear el descarte)
```

**`Extraer y Enriquecer` (transformaciones reales):**
- `fbclid` = `body.fbclid_completo`; si falta, regex sobre `body.url` (`/[?&]fbclid=([^&]+)/` + `decodeURIComponent`).
- `fbc` = `body.fbc`; si falta y hay fbclid → **derivado** `'fb.1.' + ts + '.' + fbclid` (subdomainIndex fijo en `1`, sin segmento de dominio). En el pinData observado la landing NO manda fbc → se deriva.
- `fbp` = `body.fbp` tal cual (cookie `_fbp`).
- `timestamp` = `body.timestamp` (epoch **ms**) o `Date.now()`.
- `ip` = header `x-forwarded-for`, primer valor, trim (inyectado por el proxy Caddy — `via: 2.0 Caddy`).
- `body.origen` (`"clic_whatsapp_directo"`) **se descarta** (no se lee ni propaga).
- Los `utm_*` de la `url` **NO se parsean** a columnas; quedan embebidos como texto en `Landing URL`.

**`Guardar Folio en Airtable`:** `create` puro (`matchingColumns:[]` → **sin upsert/dedup**) en Folios CAPI (`[AIRTABLE_TABLE_ID]`). Escribe: Folio, fbclid, fbc, fbp, Programa, Timestamp (number), Landing URL, user_agent, ip. La columna `fbtrace_id` existe en el schema pero **no se escribe acá** (la completa T1 con la respuesta de Meta).

### Datos in / out

| Entrada (body POST) | Ejemplo (pinData real) |
|---|---|
| `folio` | `"HHFSMG"` |
| `programa` | `"BS"` |
| `fbclid_completo` | `"IwZXh0bgNhZW0BMAB…aem_N76Vsh…"` |
| `fbp` | `"fb.1.1776220969208.525268586943021851"` |
| `user_agent` | `"…Android 15… FB_IAB/FB4A…"` |
| `timestamp` | `1776220974786` (epoch ms) |
| `url` | `"https://go.venttur.com/bs?fbclid=…&utm_medium=paid&utm_source=fb&utm_campaign=120244624338100246…"` |
| `origen` | `"clic_whatsapp_directo"` (descartado) |
| header `x-forwarded-for` | `"200.68.153.32"` → `ip` |

| Salida | Destino |
|---|---|
| Fila nueva Folios CAPI (9 campos) | Airtable |
| `{ok:true}` (200) | Respuesta a la landing (siempre, incluso si falló el guardado antes del Responder) |

### Edge cases

- Folio vacío → responde `{ok:true}` sin guardar ni loguear (pérdida silenciosa).
- CREATE sin dedup → dos POST con el mismo folio crean dos filas (reintento del cliente = duplicado).
- Fallo de Airtable en la rama TRUE → aborta antes del Responder → la landing ve timeout/500 → errorWorkflow `OBkUyb8fuo30DzA9`.
- ⚠️ INCIERTO — con qué frecuencia (o si alguna vez) la landing manda `fbc`/`ip`/`fbclid` corto directamente en el body (impacto: el código tiene fallbacks, pero el único ejemplo no los trae).

---

# CATEGORÍA B — CONVERSACIONAL (agente "Mauricio")

> **Categoría enteramente nueva vs. mayo.** El sistema SÍ tiene un agente conversacional. Mauricio es el "asistente virtual estratégico de Venttur": usa frameworks Chris Voss (empatía táctica) + Alex Hormozi (diagnóstico consultivo), metodología propia EMA (Evaluation-Match-Achieve), un diagnóstico de 7 pasos, memoria Postgres (Supabase, 35 turnos) y tools técnicas. El system prompt (~39K chars) vive **inline** en el `systemMessage` del nodo `Agente IA WPP`.

## C1 — Mensaje entrante WhatsApp (→ agente Mauricio)

**Categoría:** Conversacional · **Estado:** **LIVE (`active:true`)** · Workflow principal `k3aivKSP67S97IHn`

### Origen / condición

Webhook único POST `43fa146c-53a0-4915-89ef-311b7e72a6a3` (`https://[TU-INSTANCIA-N8N]/webhook/43fa146c-…`), `responseMode:responseNode`. Lo llama **ManyChat** (External Request) en cada mensaje entrante. El body trae el subscriber completo (`id`, `first_name`, `last_name`, `whatsapp_phone`, `custom_fields.respuesta_definitiva` = texto del lead) y `headers.mensaje` (texto crudo latin1).

**Antes del webhook**, en el lado ManyChat, el flow **"Recibir mensajes"** aplica un **debounce de 20 segundos**: acumula los mensajes fragmentados del lead en `respuesta_definitiva` (merge/concat con `Last Text Input`), espera 20 s, y recién ahí llama al webhook. Es un buffer anti-fragmentación crítico (sin él, cada mensaje corto del lead sería un turno separado).

> ⚠️ INCIERTO — no hay ramas por canal IG/FB en este workflow: todo se apoya en `whatsapp_phone` (WhatsApp-only en la práctica). No confirmable si IG/FB entran por otro webhook/workflow (impacto: la migración GHL debe cubrir los otros canales si existen).

> 🔴 **DOS FUGAS SILENCIOSAS EN ESTE MISMO CAMINO (Reporte la agencia 1, agosto 2026):**
>
> 1. **`Repetido?` descarta mensajes sin responder.** Su salida TRUE es una **rama muerta**. Y el
>    comparador está desalineado: `Actualizar ultimo mensaje` **escribe** `headers.mensaje`
>    (latin1 mojibake) mientras `Repetido?` **compara** contra `respuesta_definitiva` (UTF-8) → sólo
>    dispara con texto ASCII puro. Es el mecanismo del Hallazgo 4 (*"Muchas gracias"* de Omar Montes).
>    Nota para la migración: `Meta CAPI` es rama **hermana**, no aguas abajo, así que hoy se disparan
>    eventos de conversión por turnos que el agente nunca contestó.
> 2. **`Hay audios?` es una condición imposible** (`and` + `audio[0] equals "webp"` sobre una URL de
>    S3) → la rama de transcripción **nunca corrió**. Una nota de voz pura llega al agente como
>    **string vacío**.
>
> Y el agente **no recibe ningún estado del lead**: su User Message es sólo el texto + la fecha.

### Flujo (topología real — mucho más que "webhook→agent→split")

El webhook arranca en el extremo izquierdo; el agente está a la derecha. Hay una larga cadena determinística **antes** (dedup + atribución CTWA + alta de lead + transcripción) y otra **después** (split + envío).

```
Webhook → Responder rápido ManyChat (responde 200 al instante, anti-timeout)
  ├──► Meta CAPI (Execute-WF z98w2yWVEMOfifMl, paralelo, fire-and-forget)   [T1/T2]
  └──► Buscar registro (Airtable "Tabla apoyo (ignorar)" — ledger de dedup por subscriber)
        → Existe? (IF)
            ├─ TRUE  → Repetido? (IF: Ultimo mensaje == respuesta_definitiva)
            │             ├─ TRUE  → [salida VACÍA] STOP  ← anti-loop: mismo texto que el anterior
            │             └─ FALSE → Actualizar ultimo mensaje
            └─ FALSE → Crear registro
        → Tomar todos los mensajes (Airtable "Mensajes anuncios", sin filtro)
        → Code (matching CTWA: normaliza respuesta_definitiva y la compara contra .Mensaje
                de cada anuncio, coincidencia flexible bidireccional includes())
        → Tomar fuente correcta (Airtable "Mensajes anuncios", {Mensaje}=<match>)
                → recupera .Anuncio (=Fuente lead) y .Interes (=Programa interés)
        → Buscar si ya existe (Leads, {id}=telefono sin +)
        → No existe? (IF: Nombre notExists)
            ├─ TRUE  → Crear primer contacto (Airtable Leads, determinístico):
            │           Nombre=first_name, Apellido=last_name, Telefono, ID Manychat,
            │           Fuente lead=<Anuncio>, Programa interés=<Interes>,
            │           Folio=respuesta_definitiva.match(/Folio:.../)
            │          → Execute Workflow "Resumen, etiquetas, seguimientos" (DyrDumQgb6S4zHsS)  [N1]
            └─ FALSE → (salta el alta)
        → Separamos en partes (Code: separa URLs de audio S3 del texto)
        → Hay audios? (IF)
            ├─ TRUE  → Split Out → Get_Audio/s → Transcribir (whisper-1, es) → Aggregate → Juntar mensajes
            └─ FALSE → Obtener solo texto
        → Agente IA WPP (AI Agent) ★
        → Formatear mensaje WPP (gpt-4o-mini, jsonOutput → {parte1,parte2,parte3})
        → Settear variables (HTTP ManyChat setCustomFields: parte1/2/3)
        → Enviar WPP (HTTP ManyChat sendFlow content20250617172539_850988)
        → Envió link? (IF: output contains "promo.venttur.com/")
            └─ TRUE → Actualizar link (Execute-WF gRSMjzxggA4UePjz)   [dispara R1 vía handoff]
```

**`Agente IA WPP` (núcleo):**
- **User Message:** `Mensaje del usuario: {texto}` + `Fecha de hoy: {now en America/Mexico_City}` (formato "Wednesday 10 of April of 2026 09:30AM").
- **Modelo:** gpt-4o, **temperature 0** (cred `OpenAI | Venttur`). *(No gpt-4.1 — corrección vs. supuestos previos.)*
- **Memoria:** Postgres Chat Memory, `sessionKey = whatsapp_phone.replace('+','')`, **contextWindowLength 35** (Supabase, cred `Venttur`).
- **Tools cableadas:** `crear_contacto` (C2) y `elevar` (C3).

### Reglas de negocio del agente (del system prompt)

- **Metodología EMA** (Evaluation-Match-Achieve) + diagnóstico de 7 pasos; no recomienda programa sin diagnóstico completo (edad / escuela / idioma / motivación).
- SIEMPRE pide nombre + apellido de **quien escribe** (no del hijo/a).
- Nunca da cifra de precio sin contexto/perfil.
- No repite el link de asesoría; envía links **sin markdown/paréntesis** (regla explícita con ejemplo correcto vs. incorrecto).
- Personaliza al experto (Rodrigo / Andrés / Diego) con una línea de valor humano.
- **Regla de elevación:** eleva (tool `elevar`) si el usuario pide humano/emergencia, o si envía **el mismo mensaje dos+ veces consecutivas e inmediatas**. Si el mismo texto reaparece NO-consecutivo (retoma días después), **NO** eleva.
- Respuesta partida en hasta 3 mensajes, cortando solo tras punto, limpiando `¿`/`¡` de apertura (conserva `?`/`!` de cierre).

### Reglas de infraestructura (defensas operativas)

- **Anti-timeout:** `Responder rápido ManyChat` responde 200 de inmediato (ManyChat no espera al agente).
- **Anti-duplicado (infra):** si `respuesta_definitiva` es idéntico al último guardado en "Tabla apoyo", el nodo `Repetido?` corta el flujo (salida TRUE vacía) antes del agente. (Es distinto de la regla de elevación por repetición del prompt.)
- **Atribución CTWA por texto:** `Fuente lead`/`Programa interés` del lead se deducen matcheando el primer mensaje contra `Mensajes anuncios` (tabla de copys de anuncios).
- **Extracción de folio:** se parsea `Folio: XXX` del texto y se guarda en `Leads.Folio`.
- **Dos altas de contacto conviven:** (a) determinística (`Crear primer contacto`, nombre del perfil ManyChat, ANTES del agente); (b) agéntica (tool `crear_contacto`, nombre que el lead escribe). Duplicación de responsabilidad.

### Datos in / out

| Entrada | Fuente |
|---|---|
| `id`, `first_name`, `last_name`, `whatsapp_phone`, `respuesta_definitiva`, `headers.mensaje` | ManyChat webhook |
| `Ultimo mensaje` (dedup) | Airtable "Tabla apoyo (ignorar)" `tblLjOtFFTn9L2Zzz` |
| `Mensaje`/`Anuncio`/`Interes` | Airtable "Mensajes anuncios" `tbl2GmzS6irT0iUBF` |
| `Nombre` (existe?) | Airtable Leads `[AIRTABLE_TABLE_ID]` |
| historial | Postgres/Supabase (sessionKey=teléfono) |
| audios | S3 `manybot-files.s3.eu-central-1` |

| Salida | Destino |
|---|---|
| ledger dedup {ID, Ultimo mensaje} | Airtable "Tabla apoyo" |
| lead nuevo {Nombre, Apellido, Telefono, ID Manychat, Fuente lead, Programa interés, Folio} | Airtable Leads |
| custom fields parte1/2/3 | ManyChat |
| turnos user/assistant | Postgres/Supabase |
| (vía sub-wfs) Clientify, Meta CAPI, "Link enviado", "Resumen/etiquetas/seguimientos" | — |

### Edge cases / hallazgos

- ⚠️ **sessionKey NO normaliza el quirk MX**: es `whatsapp_phone.replace('+','')` a secas. El MX llega como `+5214731220110` y se guarda `5214731220110`. Sin strip 521→52 → **riesgo de doble identidad de sesión** si el lead aparece con/sin el "1". (Contrasta con outreach/rescate que SÍ normalizan a `521`.)
- ⚠️ Nodo `Hay audios?`: condición AND con `audio[0] equals "webp"` — parece contradictoria/rota para una URL de audio real (posible bug/filtro anti-imagen mal armado).
- ⚠️ **Secretos hardcodeados**: API key OpenAI (`sk-proj-…`) en el nodo de transcripción y Bearer ManyChat (`3256256:ecc8538e…`) repetido en 4 nodos, en vez de credenciales n8n. Rotar antes de cualquier export/handoff.
- ⚠️ El sub-workflow `Meta CAPI` se invoca con **inputs vacíos** — cómo obtiene teléfono/folio no es deducible del JSON del main.
- ⚠️ NO aparece llamada a `wf-estado-lead-venttur` (S1) desde este main, pese a que CLAUDE.md dice que el main lo invoca — posible snapshot anterior o integración fuera de este JSON.

## C2 — Tool `crear_contacto` (evento interno)

**Categoría:** Conversacional (evento interno) · **Estado:** LIVE (sub-wf `cZUNKQyZNOHy5twQ`, `active:false` esperable en sub-wf)

- **Disparo:** el AI Agent decide invocarla cuando el usuario da **nombre + apellido completos**. Inputs: `nombre=$fromAI('nombre')`, `apellido=$fromAI('apellido')`, `id=body.id`, `telefono` sin +.
- **Qué hace:** sincroniza el lead Airtable↔Clientify. (1) Airtable Leads (op `update`, match por `Telefono`): `Contestan 1er mensaje=true`, Nombre/Apellido/Telefono, y **blanquea `Folio`** (expresión vacía); (2) crea contacto en Clientify (POST `/v1/contacts/`, token hardcodeado); (3) Airtable Leads: guarda `ID Clientify`.
- ⚠️ El nodo se llama "Crear o actualizar contacto" pero la operación real es `update` (NO upsert) → depende de que la fila del lead ya exista.
- ⚠️ **`availableInMCP:false`** y trigger con inputs planos sin `$fromAI` en su propia definición → evidencia de que este sub-wf lo orquesta el main como toolWorkflow, no que sea una tool MCP separada. La hipótesis de que sea "el que estampa Estado conversación" es FALSA en esta versión (no toca ese campo; el "EDIT B" de `estado-leads-implementation-guide.md` es un cambio pendiente).
- ⚠️ INCIERTO — por qué blanquea `Folio` (¿intencional al materializar contacto o artefacto?).

## C3 — Tool `elevar` (evento interno)

**Categoría:** Conversacional (evento interno) · **Estado:** LIVE (inline en el main, `toolHttpRequest`)

- **Disparo:** el agente la invoca cuando (a) el usuario pide humano/emergencia, o (b) envía el **mismo mensaje dos+ veces consecutivas e inmediatas** (regla del prompt, líneas 345-352 / 565).
- **Qué hace:** POST ManyChat `sendFlow` `flow_ns: content20250716130059_365663` → dispara el flow **"Elevar"** de ManyChat: `Pause all automations: Forever` + `Assign conversation` + `Notify Assignees: 0 people`.
- ⚠️ **POSIBLE BUG** — el flow "Elevar" tiene `Notify Assignees: 0 people` (destinatario vacío/"Unknown user" en el screenshot). Si es real, **el equipo humano podría no enterarse de las elevaciones** (impacto: leads que piden humano quedan sin atención; revisar con Max/Mauricio antes de migrar).

## C4 — Tool `contestan_2do` (instruida, NO implementada)

**Categoría:** Conversacional (evento interno) · **Estado:** ⚠️ **Instruida en el prompt, tool INEXISTENTE**

- El system prompt (línea 343) instruye: *"Si el usuario responde a tu segundo mensaje en la conversación, activa la herramienta `contestan_2do`."* PERO **no hay ningún ai_tool con ese nombre cableado en el main**. El agente tiene instrucción de invocar una tool que no existe.
- ✅ **DECIDIDO (2026-08-17): se descarta.** La instrucción se **eliminó del system prompt v2.0** — le
  ordenaba al agente invocar una tool inexistente en cada conversación. La métrica "contestó el 2do
  mensaje" queda cubierta en GHL por el estado de conversación, no por una tool dedicada. El campo
  `Contestan 1er mensaje` de Airtable sigue existiendo y lo tocan otros workflows.

---

# CATEGORÍA C — CRM (formulario landing)

## CR1 — Formulario Landing (→ Airtable + Clientify)

**Categoría:** CRM · **Estado:** **LIVE (`active:true`)** · Workflow `ZB6erhWicZmDfC4I`

### Origen / condición

Webhook POST `ceebf4f6-1ca0-46b7-b42b-db93691e5198` (`https://[TU-INSTANCIA-N8N]/webhook/ceebf4f6-…`). Lo dispara la landing `go.venttur.com` al hacer submit del formulario (pinData: origin `go.venttur.com`, user-agent in-app de Instagram iPhone → anuncio IG → landing → submit). Sin autenticación.

### Flujo

```
Webhook → Edit Fields (normaliza) → Crear o actualizar contacto (Airtable UPSERT por Telefono)
  → Buscar Contacto Clientify (GET /contacts/?phone=+<tel>)
     → es vacío? (IF: count==0 OR results empty)
         ├─ TRUE  → Crear Contacto Clientify (POST, id compuesto "PROGRAMA_telefono")  ─┐
         └─ FALSE → Crear Contacto Clientify1 (POST, id = results[0].id)               ─┤
                                                                                        ├→ Actualizar ID Clientify (Airtable)
                                                                                        └→ Etiquetar Contacto (POST /tags/) [terminal]
```

**`Edit Fields`:** `nombre=body.nombre`, `apellido=body.apellidos`, `telefono=body.telefono.replace("+","")` (solo la 1ª ocurrencia de "+"; sin trim, sin país, sin validación), `etiqueta=body.programa` (código crudo, ej. `"BSG"`).

**`Crear o actualizar contacto`:** upsert Leads (match `Telefono`): Telefono, Nombre, Apellido, `Contestan 1er mensaje=false`. ⚠️ El campo `Programa interés` está en el schema del nodo pero **NO se mapea** → el programa del form NO se persiste en Airtable (solo vive como tag en Clientify).

### Datos in / out

| Entrada (body, pinData) | Uso |
|---|---|
| `nombre`, `apellidos`, `telefono`, `programa` (ej. "BSG") | ✅ usados |
| `email`, `pais`, `ciudad`, `folio`, `fbclid_completo`, `fbp`, `user_agent` | ⛔ recibidos pero ignorados (el tracking CAPI vive en otro workflow) |

| Salida | Destino |
|---|---|
| lead upsert {Telefono, Nombre, Apellido, Contestan 1er mensaje=false} | Airtable Leads |
| `ID Clientify` | Airtable Leads (update) |
| contacto (id compuesto `BSG_524424754070`) + tag = código de programa | Clientify |

### Edge cases / hallazgos

- ⚠️ **Este JSON de `00_inputs` es la versión PRE-fix.** La URL de `Etiquetar Contacto` referencia siempre `$('Crear Contacto Clientify').item.json.id` (rama de creación); cuando el lead ya existía (rama FALSE), ese nodo no corrió → error "Node hasn't been executed". El fix `isExecuted` documentado en CLAUDE.md (2026-06-06) vive en `03_workflows/formulario-clientify-venttur-v1.json`, no en este input.
- ⚠️ **NO hay nodo Telegram** (mayo asumía "→ Telegram"; este archivo termina en `Etiquetar Contacto`).
- Doble representación del teléfono: Airtable SIN "+", Clientify CON "+".
- Errores de Clientify (retryOnFail + `continueErrorOutput` con rama de error vacía) → corte silencioso sin alerta.
- ⚠️ INCIERTO — catálogo completo de códigos `body.programa` (el sample muestra "BSG"; no mapea 1:1 con el enum `Programa interés` de Airtable).

---

# CATEGORÍA D — ENGAGEMENT / OUTREACH (proactivo Form Meta)

> **LIVE. Mayo lo daba por "no implementado".** Workflow `CUuFxbst3iHpgeXS`. Dos flujos en un mismo workflow: **Flujo A** = ingestión/dedup (Sheets Trigger → upsert Airtable); **Flujo B** = tri-toque (Cron → estado en Airtable → envío → memoria sintética).

## O1 — Ingestión Outreach (Google Sheets Trigger)

**Categoría:** Engagement/Outreach · **Estado:** **LIVE (`active:true`)**

### Origen / condición

**Google Sheets Trigger** `Sheets Trigger - Form Meta Sync`, event `rowAdded`, poll `everyMinute`, `valueRender:UNFORMATTED_VALUE`, sobre el doc `1HzJVMBwnGikiI_U805N7oqcXPYE7TjEFTL1rqdcCEIU` / hoja `Boarding_Schools_Venttur_2026-test-2` (gid 160362675). El sheet es el bridge de **Meta Lead Ads** (Meta sincroniza las filas del formulario ahí).

> **Corrección vs. mayo:** el trigger es Sheets Trigger, NO un webhook receptor `vtr-form-meta-outreach`. La migración a Sheets Trigger ya está viva.

### Flujo A (ingestión)

```
Sheets Trigger → Normalize Payload (Code)
  → IF (_error?)
      ├─ TRUE  → Registrar Error Normalize (Execute-WF webapp_errors) [teléfono inválido → NO se crea lead]
      └─ FALSE → Split In Batches Flujo A → Buscar Lead Existente (OR({Folio}=id, {Telefono}=tel))
                   → ¿Lead Existe?
                       ├─ TRUE  → ¿Lead seguro actualizar? (Outreach==false AND Toques==0)
                       │             ├─ TRUE  → Actualizar Lead Existente (solo inmutables)
                       │             └─ FALSE → [loop, preserva estado]
                       └─ FALSE → Crear Lead Nuevo (Airtable UPSERT por Folio, 18 campos)
```

**`Normalize Payload` (helpers):** `stripMetaPrefix` (quita `l:`/`p:`), `splitName`, `parsePhone` (válido 10-15 díg; prioriza `whatsapp`, fallback `phone_number`), `deriveTipo` (Ad Name con PAPAS/MAMAS → `Padre/Madre`, else `No especificado`), `deriveFuente` (ig→Instagram, fb→Facebook, else `Facebook - Instagram`). **`touch1At = new Date().toISOString()` — AHORA de creación, SIN +1h.** Si teléfono inválido (ej. `whatsapp=''` + `phone_number='p:MX'`) → `_error` (NO throw).

**`Crear Lead Nuevo`** (upsert por Folio, idempotencia dura): 18 campos incl. los **8 de cualificación** (Programa interés='Boarding School', Origen='Form Meta', Folio=meta_lead_id, Fuente lead, Tipo, Ad Name, Platform, Grado Escolar, Inicio Deseado, Nivel Inglés, Toques enviados=0, Touch 1 programado at, Outreach Form Meta enviado=false, Contestan 1er mensaje=false).

## O2 — Outreach Touch 1 / 2 / 3 (tri-toque)

**Categoría:** Engagement/Outreach · **Estado:** **LIVE (`active:true`)**

### Origen / cadencia (EXACTA, confirmada en el `filterByFormula`)

**Cron** `Cron cada 5 min` → `Get Leads Pendientes` (Airtable). La cadencia se ancla TODA a `Touch 1 programado at` (= timestamp de creación del lead):

```
AND(
  {Origen}='Form Meta', NOT({Agendan cita}), {Última actividad}=BLANK(),
  {Toques enviados}<3, {Touch 1 programado at},
  OR(
    AND({Toques enviados}=0, IS_AFTER(NOW(), {Touch 1 programado at})),               → Touch 1 ≈ 0h (próximo ciclo)
    AND({Toques enviados}=1, IS_AFTER(NOW(), DATEADD({Touch 1 prog at},24,'hours'))), → Touch 2 = +24h
    AND({Toques enviados}=2, IS_AFTER(NOW(), DATEADD({Touch 1 prog at},72,'hours')))  → Touch 3 = +72h
  ))
```

> **Corrección clave:** la cadencia es **0h / +24h / +72h desde CREACIÓN** (Touch 1 sin delay), NO "+1h/+24h/+72h". El "5 min" es solo el polling del cron. Touch 2 y 3 se miden desde el MISMO ancla (no incremental entre toques).

### Flujo B

```
Cron → Get Leads Pendientes → Split In Batches (1) → Switch (por Toques enviados)
  ├─ 0 → createSubscriber ManyChat (consent_phrase del form) → ¿Subscriber OK?
  │        ├─ OK   → sendFlow Touch 1 (content20260612151152_969589) → Marcar Enviado
  │        └─ FALL → Log Error → [Registrar Error en Supabase DISABLED] → loop
  ├─ 1 → sendFlow Touch 2 (content20260616231914_193459) → Marcar Enviado2
  └─ 2 → sendFlow Touch 3 (content20260616231947_185709) → Marcar Enviado3

Marcar EnviadoN (Airtable, match id_2): Outreach enviado=true, ID Manychat,
   Toques enviados=(prev||0)+1, Ultimo toque at=$now   (NO toca Última actividad)
  → Build Memory Texts (Touch N) → [memoria sintética Postgres]
```

**Guards de exclusión del cron:** ya agendó (`Agendan cita`), ya respondió (`Última actividad` no-BLANK), `Toques>=3`, `Origen≠Form Meta`, o sin `Touch 1 programado at`.

### Textos de los toques (verbatim, de `template-texts-canonical.md`)

- **Touch 1** (`boarding_form_followup`, MARKETING es_MX): *"Hola {{first_name}}, gracias por tu interés en nuestros programas de Boarding School. Vimos que recientemente solicitaste información… ¿El programa sería para tu hijo(a) o para algún familiar?"*
- **Touch 2:** *"Hola {{first_name}}, Muchos padres nos contactan porque quieren brindarles a sus hijos una experiencia internacional… ¿Para qué edad o grado escolar estás buscando opciones?"*
- **Touch 3:** *"Hola {{first_name}}, Sabemos que elegir una experiencia educativa internacional es una decisión importante… Si aún estás explorando alternativas, responde este mensaje…"*

### Memoria sintética (post cada Marcar Enviado)

Cada toque siembra en Postgres `n8n_chat_histories`: un `system` en prosa (idempotente por session_id, "El lead …") + un `ai` con el texto del toque. **SessionKey = teléfono normalizado con quirk MX (12 díg que empiezan 52 → `521`+resto)** para matchear el sessionKey del agente principal. Objetivo: que Mauricio no re-salude ni repregunte cuando el lead responde.

### Datos in / out

| Entrada | Fuente |
|---|---|
| filas del form (id, ad_name, platform, full_name, email, phone_number/whatsapp, 3 preguntas, lead_status) | Google Sheet |
| lead existente (Folio, Toques, ID Manychat, Outreach enviado, Agendan cita, Estado, Última actividad) | Airtable Leads |
| createSubscriber `.data.id` | ManyChat |

| Salida | Destino |
|---|---|
| lead upsert (18 campos + 8 cualificación) | Airtable Leads |
| Toques enviados +1, Outreach enviado, Ultimo toque at | Airtable Leads |
| createSubscriber + sendFlow por toque | ManyChat (WhatsApp) |
| system + ai por toque (memoria sintética) | Postgres/Supabase |

### Edge cases / hallazgos

- ⚠️ INCIERTO — `Cron cada 5 min` tiene `rule.interval=[{field:'minutes'}]` **sin `minutesInterval`** → n8n corre cada **1 min** por default. El nombre dice 5 min; drift nombre vs. comportamiento (impacto: más carga de polling; no verificable solo con el JSON).
- ⚠️ Touch 2/3 usan sendFlow con `neverError` **sin `¿Subscriber OK?` posterior** → un fallo de sendFlow en 2/3 NO se detecta ni loguea, pero `Toques` igual se incrementa → **posible pérdida silenciosa de toque**.
- ⚠️ `Registrar Error en Supabase` está **DISABLED** → los fallos de createSubscriber (Touch 1) no se persisten (solo console.log).
- ⚠️ Teléfono inválido (`p:MX` + whatsapp vacío) → `_error` → `webapp_errors`; el lead NO se crea ni recibe outreach.
- ⚠️ Nodos huérfanos: 3 Code "respaldo" desconectados (uno usa sessionKey sin normalizar + `// TODO` de texto) — basura/rollback preparado.
- Nodo de mantenimiento `Execute a SQL query` (Manual Trigger): backfill one-shot `session_id` MX 52→521.

---

# CATEGORÍA E — ENGAGEMENT / RESCATE (post-link)

> **LIVE.** Workflow `mkEP1qFN7MVb9qP0`. 2 fases (45 min + 24 h) + memoria sintética. Se dispara desde `Actualizar 'Link enviado'` (`gRSMjzxggA4UePjz`), que a su vez lo llama el main cuando el output del agente contiene `promo.venttur.com/`.

## R1 — Rescate Fase 1 (45 min)

**Categoría:** Engagement/Rescate · **Estado:** **LIVE** (export `active:false`; es sub-wf)

### Origen / condición

Execute-WF desde `Actualizar 'Link enviado'` (fire-and-forget, input `{telefono}`). Cadena completa del disparo:

```
[main] Envió link? (output contains promo.venttur.com/) → Actualizar link (gRSMjzxggA4UePjz)
   → Code (clasifica programa por substring del link) → Etiquetar Contacto (Clientify tag "<prog>_link_enviado")
   → Check 'Link enviado' (Airtable: Link asesoría enviado=true)   ← SOLO el boolean, sin timestamp
   → Call 'Rescate Post-Link' (mkEP1qFN7MVb9qP0, fire-and-forget)   [R1]
   (el nodo 'Seguimiento agenda' A2 está DISABLED — no se dispara)
```

### Flujo Fase 1

```
Wait: 45 min → Airtable: 1er check (Leads, {Telefono}=<tel>)
  → IF ¿ya agendó? ({Agendan cita}==true)
      ├─ TRUE  → [salida VACÍA] STOP
      └─ FALSE → Code: Fase 1 (routing por programa.includes → mensaje + mcBody)
                   → IF ¿programa mapeado? (matched)
                       ├─ TRUE  → Set Custom Fields → sendFlow Fase 1 (content20250617172539_850988)
                       │            ├─► Wait: 24 hrs [Fase 2]
                       │            └─► Build Rescate Memory (Fase 1) → Postgres (system idempotente + ai)
                       └─ FALSE → addTag RESCATE_PROGRAMA_NO_MAPEADO (87501935) [STOP, sin mensaje]
```

**Routing (Code Fase 1, `programa.includes`):** Boarding→boarding (`/agendar-ema`); `AA Familiar` **O** `Francia`→aa_familia (`/AAFamilia-Agendar`); Summer Camp→summer; Pathway→pathway; Gap Year→gap_year. **Solo 5 destinos** — sin match → `matched=false` → tag NO_MAPEADO.

## R2 — Rescate Fase 2 (24 h)

**Categoría:** Engagement/Rescate · **Estado:** **LIVE** (mismo workflow, Wait interno)

```
Wait: 24 hrs → Airtable: 2do check → IF ¿ya agendó?
  ├─ TRUE  → STOP
  └─ FALSE → Code: Fase 2 (mismo routing, mensajes de cierre/objeción) → Set Custom Fields
               → sendFlow Fase 2
                   ├─► addTag LINK_ABANDONADO_FRIO (87501917)  [lead frío, terminal]
                   └─► Build Rescate Memory (Fase 2) → Postgres (solo ai, sin system)
```

### Textos (verbatim, `template-texts-canonical.md`, por programa)

Fase 1 §4-9 y Fase 2 §10-15. Ejemplos:
- **Boarding F1:** *"Hola {{first_name}}. Noté que solicitaste el enlace para platicar sobre Boarding School, pero el registro quedó pendiente… Reserva tu espacio aquí: promo.venttur.com/agendar-ema"*
- **Boarding F2:** *"Hola {{first_name}} 👋. Noté que tu registro quedó en pausa ayer. Mandar a un hijo a un internado es un gran paso… vemos los pocos cupos que quedan…"*

### Edge cases / hallazgos (críticos para GHL)

- ⚠️ **Inconsistencia de programas 5 vs 6.** Los Code de envío (Fase 1/2) mapean **5** programas. Pero los nodos de memoria (`Build Rescate Memory`) tienen **6** claves, incluyendo **`Estudio y Trabajo`**. Consecuencia: un lead `Estudio y Trabajo` cae en `matched=false`, recibe tag `RESCATE_PROGRAMA_NO_MAPEADO` y **NUNCA recibe mensaje de rescate**; la clave 'Estudio y Trabajo' del diccionario de memoria es **código muerto**. (Nota: `template-texts-canonical.md` §8 SÍ tiene el texto "Estudio y Trabajo" preparado — el gap es en el routing de envío, no en los textos.)
- ⚠️ El check de agendamiento usa la **rama VACÍA del IF como STOP** (no hay NoOp explícito).
- ⚠️ **NO escribe estado de vuelta en Airtable** — no deja rastro "rescate enviado"; la idempotencia vive en ManyChat (tags) y Postgres, no en el CRM.
- ⚠️ `Actualizar 'Link enviado'` (`gRSMjzxggA4UePjz`) tiene un **bug probable de tagging Clientify**: el body usa `$('Code in JavaScript').item.json.variable`, pero el Code emite `tag`, no `variable` → Clientify recibiría tag vacío/undefined. El `onError` lo oculta.
- ⚠️ El campo de entrada se llama `id_airtable` pero contiene el **teléfono** (nombre engañoso).
- ⚠️ **NO existe timestamp `Link asesoría enviado at`** — solo el boolean `Link asesoría enviado=true`. Si la migración necesita medir el delay 45min/24h desde la fecha del envío, hoy no se captura.
- ⚠️ INCIERTO — `Build Rescate Memory` referencia `$('Get Lead')` (Fase 1) y placeholder `{{first_name}}` en lugar del nodo real `Airtable: 1er check` y de la convención `[first_name]` — issues menores documentados en el snapshot v2, romperán ejecuciones si el flujo dispara sin fix.

---

# CATEGORÍA F — NURTURING (drip 4-toques por programa)

## N1 — Drip nurturing por programa

**Categoría:** Nurturing · **Estado:** LIVE (dispatcher `DyrDumQgb6S4zHsS`; la cadencia vive en ManyChat)

> **Nuevo vs. mayo.** El workflow `Resumen, etiquetas, seguimientos` es el **dispatcher** post-conversación: NO contiene la cadencia de 4 toques — dispara UN `sendFlow` de ManyChat por ejecución, y la cadencia (4 mensajes a 0/1/3/5 días) vive DENTRO de cada flow de ManyChat.

### Origen / condición

Execute-WF desde el main (nodo `Execute Workflow` tras `Crear primer contacto` → lead nuevo), inputs `{tel, id_manychat}`. Espera **8 horas**, reconstruye la conversación desde Postgres, la clasifica con gpt-4o-mini (temp 0, jsonOutput) → 5 salidas: `tags` (programas), `tipo` (Padre/Madre|Estudiante), `resumen`, `asesoria` (uno|cero), `cualificado` (1|0).

### Flujo (4 ramas paralelas post-LLM)

```
Execute-WF (tel, id_manychat) → Esperar 8 horas → Postgres (SELECT message WHERE session_id=tel)
  → Obtener historial conversación → Obtener ID Clientify → OpenAI (5 tareas)
     ├─ Rama A: Edit Fields → Airtable (Tipo)
     ├─ Rama B: If (tags notEmpty)
     │     ├─ TRUE → Split Out → Loop → Etiquetar Contacto (Clientify) + Interés (Airtable) + programa_interes (ManyChat)
     │     │        + No envio link? (asesoria=='cero') → Switch por programa → sendFlow drip:
     │     │            Pathway  → content20250718121921_967738
     │     │            Summer   → content20250718123847_652764
     │     │            AA Fam   → content20250718123255_243860
     │     │            Boarding → content20250718115245_638127
     │     │            Gap Year → content20250718122822_491460
     │     └─ FALSE → No envio link? x2 → Seguimiento Lead General (content20250718124216_992343)
     ├─ Rama C: Cualificado? (=='1') → Airtable (Cualificado=true)
     └─ Rama D: If1 (ID Clientify exists) → Agregar resumen (Clientify note)
```

### GATE anti-doble-contacto (regla clave)

El drip **SOLO se dispara si `asesoria=='cero'`** (el lead NO recibió link de asesoría). Si ya recibió link, NO se envía nurturing (ni de programa ni general). La detección de "recibió link" la hace el LLM contra una whitelist de 6 URLs `promo.venttur.com/…`.

### Cadencia del drip (dentro de cada flow ManyChat, de `manychat-flows-content-2026-07-20.md`)

Estructura idéntica en los 6 flows: `Condición (Field is missing)` → mensaje 1 → `Wait 1 Day` → mensaje 2 → `Wait 2 Days` → mensaje 3 → `Wait 2 Days` → mensaje 4. Es decir **4 toques a 0 / 1 día / 3 días / 5 días**. Contenido educativo/nurturing de largo plazo (errores comunes, checklists de preparación, países disponibles, cierre suave). Textos completos en `manychat-flows-content-2026-07-20.md` §"Seguimientos de nurturing por programa".

| Programa (tag LLM) | Flow ManyChat | flow_ns |
|---|---|---|
| Boarding IA | Boarding School | content20250718115245_638127 |
| Pathway IA | Pathway | content20250718121921_967738 |
| Gap Year IA | Gap year | content20250718122822_491460 |
| AA Familiar IA | Año Académico | content20250718123255_243860 |
| Summer Camp IA | Summer Camp | content20250718123847_652764 |
| (sin tags) Lead General | Seguimiento Lead General | content20250718124216_992343 |

### Edge cases / hallazgos

- ⚠️ El `Switch` dispara **solo el PRIMER programa que matchea** (sin `allMatchingOutputs`), en orden Pathway > Summer Camp > AA Familiar > Boarding > Gap Year — un lead multi-programa recibe un único drip según esa prioridad (probablemente no intencional).
- ⚠️ El GATE lee `asesoria` del LLM (whitelist de URLs en el historial) en vez del campo booleano `Link asesoría enviado` que el mismo lead ya tiene en Airtable (¡y que el workflow incluso trae en los fields, pero no usa!). Frágil.
- ⚠️ Lista LLM = 5 programas, pero `Programa interés` de Airtable tiene 8 opciones (incluye `Francia IA`, `Automatización - Comentarios`) que este workflow nunca puede setear ni nurturear.
- ⚠️ INCIERTO — la estructura/timing real de cada flow_ns de ManyChat solo se conoce por los screenshots; requiere el export de ManyChat para 100% de fidelidad.

---

# CATEGORÍA G — ESTADO DE LEAD

> **Nuevo vs. mayo.** Dos workflows mantienen `Estado conversación` (enum: **Activa / Contestó / Cita confirmada / Conversación interrumpida**) y `Última actividad`.

## S1 — Estado "Contestó" (por inbound)

**Categoría:** Estado · **Estado:** Diseñado, deploy pendiente (ver nota) · Workflow `b52CUYEkI2Ah3Xj6`

- **Disparo:** Execute-WF desde el main, **por cada mensaje entrante** (no bloqueante, según CLAUDE.md). Input: `telefono`.
- **Flujo:** `Buscar lead` (Leads, `{Telefono}=<tel>` exacto, trae Telefono/Estado conversación/Agendan cita) → `Aplicar guarda` (Code) → `Actualizar estado`.
- **Guarda forward-only (anti-downgrade):** `terminal = Agendan cita===true OR Estado conversación==='Cita confirmada'`. Si terminal → preserva el estado actual (no pisa con "Contestó"). Si no → `Estado conversación='Contestó'`. Siempre estampa `Última actividad = new Date().toISOString()` (**UTC**). Si el lead no existe → **no-op** (no crea).
- ⚠️ **La protección "no pisar cita" NO usa un valor de estado "Cita agendada"** (ese valor no existe en el enum). Usa el checkbox `Agendan cita===true` **O** `Estado conversación==='Cita confirmada'`.
- ⚠️ INCIERTO — el JSON está `active:false` y CLAUDE.md lo lista como "pendiente de aplicar en n8n los 3 EDITs". No confirmable solo con el archivo si ya se deployó (impacto: si S1 no está vivo, `Última actividad` no se estampa por inbound → afecta el guard de O2 y el barrido de S2).
- ⚠️ Match por string **exacto** sin normalización E.164 → depende de que el main mande el teléfono idéntico al de Airtable.

## S2 — Estado "Conversación interrumpida" (barrido)

**Categoría:** Estado · **Estado:** **LIVE (`active:true`)** · Workflow `H6qYB3Oj97bxaTCX`

- **Disparo:** Schedule Trigger `Cada hora` (sin `hoursInterval` explícito → default cada 1 h).
- **Flujo (3 nodos):** `Cada hora` → `Buscar inactivos` (Leads, filterByFormula) → `Marcar interrumpida` (update, `Estado conversación='Conversación interrumpida'`, match por Telefono).
- **Filtro (umbral 24 h exactas):**
  ```
  AND({Agendan cita} != TRUE(), {Estado conversación} != 'Cita confirmada',
      {Estado conversación} != 'Conversación interrumpida', {Última actividad},
      IS_BEFORE({Última actividad}, DATEADD(NOW(), -24, 'hours')))
  ```
- **Idempotencia** por auto-exclusión (`Estado != 'Conversación interrumpida'`), no por flag dedicado.
- ⚠️ **Exclusión implícita:** leads SIN `Última actividad` poblada quedan **permanentemente fuera** del barrido (el filtro exige el campo truthy). Depende de que S1 (u otro) estampe el campo.
- ⚠️ No estampa timestamp de cuándo se marcó; solo el single-select.
- ⚠️ INCIERTO — TZ del cron / del `NOW()` de Airtable (Airtable NOW() es UTC; `Última actividad` de S1 se escribe en UTC → el umbral de 24h es coherente en absoluto, pero no confirmable el offset vs. hora MX).

---

# CATEGORÍA H — AGENDAMIENTO

## A1 — Confirmación de agenda

**Categoría:** Agendamiento · **Estado:** **LIVE (`active:true`)** · Workflow `2PSekVBxarsrnVBu`

> **Corrección vs. mayo:** NO es un webhook de la plataforma de agendamiento. Son **3 Google Calendar Triggers** (uno por asesor), `eventCreated`, polling cada minuto.

### Origen / condición

`Diego` (dgarcia@venttur.com), `Andres` (agarcia@), `Rodrigo` (rgarcia@), todos `eventCreated`, misma credencial OAuth `Google Calendar | Rodrigo`. La "plataforma de agendamiento" (Calendly/cal.com/booking propio — ⚠️ INCIERTO cuál) crea el evento con link de Meet; n8n solo reacciona a la creación en el calendar del asesor. Latencia máx ~1 min.

### Flujo

```
Diego/Andres/Rodrigo (Calendar Trigger) → is_asesoria (IF: summary contains "ASESORÍA"/"estudia"/
   "FAMILIA"/"SUMMER"/"Pathway Alemania"/...)
  → nombre_lead (Code: extrae lo que sigue a "<>" en el título)
  → Obtener datos (Clientify GET /contacts?query=<nombre>)
  → exists (IF: count!=0)
      ├─ TRUE → Obtener ID Manychat1 (Airtable Leads, {ID Clientify}=results[0].id)
      │           → If (registro existe?)
      │               ├─ TRUE  → Agendan cita = true (Airtable update)
      │               └─ FALSE → Crear contacto (Airtable create, Fuente lead="Web") → error (Telegram)
      │           → Switch (por asesor .isExecuted) → mensaje_<asesor> (fecha dd/MM + link Meet)
      │           → Settear variables (ManyChat setCustomFields) → Enviar (sendFlow "Agenda" content20250721163426_851504)
      └─ FALSE → error (Telegram)
```

### Regla de negocio / dato a preservar

El flow ManyChat **"Agenda"** (content20250721163426_851504) es el que entrega la confirmación al lead e incluye el texto: *"Rodrigo se comunicará contigo por WhatsApp directamente desde el número **+52 1 33 1944 2476**"*. **El número directo de Rodrigo NO está en el JSON n8n** — vive dentro del flow de ManyChat. Dato de negocio a preservar en la migración.

### Edge cases / hallazgos (críticos)

- ⚠️ **Referencias rotas**: `Settear variables` (path Andres) referencia `$('Obtener ID Manychat')` y `Settear variables2` (path Diego) referencia `$('Obtener ID Manychat2')` — **ninguno de esos nodos existe** (solo existe `Obtener ID Manychat1`). Sugiere que **solo el path de Rodrigo funciona** en producción; los de Diego/Andres fallarían al resolver subscriber_id.
- ⚠️ **Leads NUEVOS (no pre-existentes en Airtable) NO reciben confirmación WhatsApp** — solo se crean y se avisa por Telegram (gap de cobertura).
- ⚠️ Identificación del lead = cruce frágil de 3 sistemas: título del evento (marcador `<>`) → Clientify por nombre → Airtable por ID Clientify. Cualquier cambio de naming rompe todo.
- ⚠️ Secretos hardcodeados (Bearer ManyChat, Token Clientify, chatId Telegram).
- ⚠️ NO escribe `Estado conversación='Cita confirmada'` en este workflow — solo el checkbox `Agendan cita=true`. (El estado "Cita confirmada" que S1/S2 protegen debe setearse en otro lado — ⚠️ INCIERTO dónde.)

## A2 — Seguimiento agenda (48 h)

**Categoría:** Agendamiento · **Estado:** Diseñado, **hoy NO se invoca** (nodo padre DISABLED) · Workflow `DZlSEQS5qzX1Y01K`

- **Disparo previsto:** Execute-WF desde `Actualizar 'Link enviado'` (nodo `Ejecutar seguimiento agendamiento`) — pero ese nodo está **`disabled:true`**, así que hoy no se dispara. Input: `telefono`.
- **Flujo:** `Wait 48 horas` → `Tomar datos` (Leads, {Telefono}) → `Agendo` (IF: `Agendan cita` **exists**) → si NO existe (no agendó) → `Seguimiento Agenda` (ManyChat sendFlow `content20250718124614_140983`).
- **Texto (flow ManyChat):** *"Hola [First Name] 👋 Hace unos días te compartí el enlace para agendar tu asesoría personalizada, pero vi que aún no la agendaste…"* → `Add Tag: seguimiento_agenda`.
- ⚠️ Workflow scaffoldeado sin limpiar (conserva el nodo placeholder `Replace me with your logic`, `active:false`) → parece stub/legacy.
- ⚠️ El guard depende de que Airtable **omita** el campo checkbox `Agendan cita` cuando está desmarcado (comportamiento estándar de la API, no probado por el JSON). Si viniera siempre presente, NUNCA enviaría el recordatorio.
- ⚠️ Cero idempotencia (no marca "seguimiento enviado"); token ManyChat hardcodeado.
- ⚠️ INCIERTO — este A2 (single-touch 48h) coexiste con R1/R2 (rescate 45min+24h): dos mecanismos de recordatorio distintos y paralelos para el mismo objetivo (lead con link, sin cita). Hoy solo R1/R2 está activo (A2 disabled).

---

# CATEGORÍA I — OPERATIVO / REPORTING

## OP1 — Correo semanal

**Categoría:** Operativo/Reporting · **Estado:** Diseñado, **NO en producción** (modo test) · Workflow `BrFfQyDfamdUzq64`

- **Disparo:** Schedule Trigger semanal, lunes ~10 h.
- **Flujo:** `Schedule` → `Fuente lead Rollup` (Airtable "Reporte semanal" `tblrXIUd7CGtiZEaS`, `IS_AFTER({Created}, TODAY()-7)`) → `Code` (formatea fuentes + porcentajes ×100) → `Message a model` (gpt-4.1-mini, temp 0.2, conclusión de 3 oraciones) → `Send a message` (Gmail HTML branding propio).
- **El workflow NO calcula las métricas** — las consume ya pre-agregadas desde la tabla "Reporte semanal" (rollups/fórmulas de Airtable o proceso aguas arriba, ⚠️ INCIERTO dónde). Es puramente lectura + presentación.
- ⚠️ **Modo test, no producción:** `active:false`, destinatario `[EMAIL-AGENCIA]` (la agencia, no el cliente), y el cuerpo del mail arranca con el literal **"CORRER FLUJO MANUAL"**. No hay evidencia de reportes reales enviados al cliente.
- ⚠️ **NO hay Telegram** (mayo mencionaba "email/Telegram"; el único canal es Gmail).
- ⚠️ Solo procesa la primera fila (`$input.first()`); si el filtro devuelve >1 fila, las demás se ignoran.
- Métricas presentadas: total leads → cualificados (%) → citas agendadas (% conversión) → asisten (% asistencia) + no continuadas + desglose por fuente. Relación con `reporte-semanal.csv`: el CSV es un export (subconjunto) de esa tabla.

---

# PROGRAMAS: negocio vs. atribución CAPI (referencia transversal)

Dos taxonomías de "programa" conviven y NO son 1:1. Documentarlas juntas evita confusión en la migración.

## Programas conceptuales del negocio (system prompt + links de agendamiento)

De las líneas 478-485 del system prompt (matriz de links → experto):

| Programa (interés del lead) | Link de agendamiento | Experto |
|---|---|---|
| Internados / Boarding School | `promo.venttur.com/agendar-ema` | Rodrigo |
| Gap Year / Estudiar y trabajar | `promo.venttur.com/Estudiar-y-Trabajar-en-Australia` | Diego |
| Año Académico Público (AA Familiar) | `promo.venttur.com/AAFamilia-Agendar` | Rodrigo |
| Campamentos de verano (Summer Camp) | `promo.venttur.com/SummerCamp-Agendar` | Rodrigo |
| Pathway universitario Alemania | `promo.venttur.com/PW_Alemania_Agendar` | Andrés |
| Programa "estudiar y trabajar" (cursos idiomas) | `promo.venttur.com/EstudiaryTrabajar_Agendar` | Andrés |
| GAP Year Australia | `promo.venttur.com/Estudiar-y-Trabajar-en-Australia` | Diego |
| (duda / fallback) | `promo.venttur.com/agendar-ema` | — |

> ⚠️ INCIERTO — **ambigüedad "Gap Year / Estudia y trabaja" vs "Estudiar y trabajar"**: el prompt tiene DOS entradas distintas (línea 479 "Gap Year / Estudiar y trabajar" → `/Estudiar-y-Trabajar-en-Australia` → Diego; línea 483 "programa estudiar y trabajar" → `/EstudiaryTrabajar_Agendar` → Andrés; línea 484 "GAP Year Australia" → `/Estudiar-y-Trabajar-en-Australia` → Diego). Se solapan conceptualmente pero apuntan a links y expertos distintos (impacto: el agente puede mandar el link/experto equivocado; confirmar con negocio cuál es cuál antes de migrar).

## Programas con atribución CAPI (tabla Programas CAPI — CONFIRMADO en CSV)

La tabla `Programas CAPI` tiene **4 filas = 4 códigos, pero solo 2 pixels**:

| Código | Nombre programa | pixel_id | default_url |
|---|---|---|---|
| `BS` | Boarding IA | `228398216567258` | `go.venttur.com/bs` |
| `BSG` | Boarding IA | `228398216567258` | `go.venttur.com/bs/girls` |
| `BSC` | Boarding IA | `228398216567258` | `go.venttur.com/bs/cats` |
| `HF` | AA Familiar IA | `24520910174237152` | `go.venttur.com/hf` |

> ⚠️ INCIERTO — **los demás programas del agente (Summer Camp, Pathway, Gap Year/Estudia y Trabaja) NO tienen fila en Programas CAPI** → su tracking CAPI es **incierto** (probablemente no tienen pixel configurado, o dependen de otra rama). NO asumir que existen (impacto: para esos programas, el evento Lead CAPI puede no dispararse o fallar con `pixel_id` undefined; la rama CTWA además hardcodea `BS`, así que todo CTWA se atribuye al pixel de Boarding).

---

# MODELO DE DATOS Y FK QUE CRUZAN PLATAFORMAS (referencia)

> **Ampliado vs. mayo** (que documentaba ~9 columnas de Leads). La tabla Airtable Leads tiene **30 columnas**.

**Airtable Leads — 30 columnas:** `id`, `id_2`, `Link asesoría enviado`, `Asistió`, `Agendan cita`, `Programa interés`, `Inicio Deseado`, `Tipo`, `Grado Escolar`, `Nivel Inglés`, `Creada`, `ID Clientify`, `ID Manychat`, `Nombre Completo`, `Email`, `Fuente lead`, `Folio`, `fbclid`, `Estado conversación`, `Última actividad`, `Outreach Form Meta enviado`, `Outreach Form Meta enviado at`, `Origen`, `Toques enviados`, `Ultimo toque at`, `Ad Name`, `Platform`, `Touch 1 programado at`, `Lead Score`, `Tipo lead`.

**Claves foráneas que resuelven el cruce entre plataformas:**

| Relación | Clave |
|---|---|
| Airtable Leads.`ID Clientify` → Clientify contact.id | 1:1 |
| Airtable Leads.`ID Manychat` → ManyChat subscriber | 1:1 |
| Airtable Leads.`id` (= teléfono sin +) → Supabase `n8n_chat_histories.session_id` | ⚠️ **con quirk MX 52→521** (el main NO normaliza; outreach/rescate SÍ) |
| Airtable Leads.`Folio` → Folios CAPI.`Folio` | 1:1 (nexo con Meta CAPI) |

**Supabase:** solo `n8n_chat_histories` importa (34.725 filas; `session_id`=teléfono sin +; `message` jsonb `{type:human|ai|system}`; `contextWindowLength` 35). `documents` (0 filas, vestigio RAG) y `n8n_chat_histories_plus_backup` (2 filas) son irrelevantes. `workflow_errors` **no existe** en este Supabase (va a un Supabase central de la agencia).

**ManyChat:** cuenta "Venttur | Agente de IA", plan Pro, TZ America/Montevideo. **16 flows** (vigente; en mayo había 14 → **+3** flows nuevos de Outreach [Touch 1/2/3] y **−1** flow viejo "Rescate Post-Link" de ManyChat, reemplazado por el workflow n8n: 14 + 3 − 1 = 16), 5 tags, 13 custom fields.

**Clientify (volumen real confirmado):** 6968 contactos / 2338 deals / 266 companies / 22 custom fields. Pipeline de deals real: "Campaña Internados Erika" (1024), "VENTAS EMA METODOLOGÍA" (319), "Campaña Australia Abril 25" (291), "Venta SPE - Internados" (172). Status: Expired 1875, Lost 381, Open 50, Won 32. **Los workflows de producción usan Clientify SOLO para contacts/tags/notes — NO usan deals/companies/custom-fields** (esos son gestión comercial manual del equipo). Veredicto de migración: **REMOVE** (absorbido por GHL Contacts), pero con panorama completo.

---

# MAPA DE DEPENDENCIAS ENTRE TRIGGERS (actualizado)

```
   ┌─────────────────────────── FLUJO DE ATRIBUCIÓN ───────────────────────────┐
   │                                                                            │
 T3 (Registro Folio, landing→n8n) ──precede──► T1 (CAPI con Folio, en cada msg)│
   │                                                                            │
 (lead CTWA, sin landing) ─────────────────────► T2 (CAPI CTWA, en cada msg)    │
   └────────────────────────────────────────────────────────────────────────────┘

   ┌─────────────────────────── FLUJO CONVERSACIONAL ──────────────────────────┐
   │  ManyChat "Recibir mensajes" (debounce 20s) ──► C1 (webhook main / agente) │
   │     C1 ├─► [paralelo] T1/T2 (Meta CAPI, fire-and-forget)                   │
   │        ├─► [paralelo] S1 (Estado "Contestó")  [⚠ deploy pendiente]         │
   │        ├─► crea lead nuevo ──► N1 (Resumen…, +8h) ──► drip nurturing (0/1/3/5d) │
   │        ├─► C2 crear_contacto / C3 elevar / C4 contestan_2do (⚠ inexistente)│
   │        └─► output con link ──► "Actualizar link" ──► R1 (45min) ──► R2 (+24h)│
   │                                    (A2 seguimiento-48h: nodo DISABLED)     │
   └────────────────────────────────────────────────────────────────────────────┘

   ┌─────────────────────────── FLUJO CRM / OUTREACH ──────────────────────────┐
   │  Landing form ──► CR1 (Airtable + Clientify)                              │
   │  Meta Lead Ads ─► Google Sheet ─► O1 (ingestión) ──► [Airtable state]      │
   │                                    Cron ─► O2 (Touch 1/2/3: 0h/+24h/+72h)  │
   └────────────────────────────────────────────────────────────────────────────┘

   ┌─────────────────────────── ESTADO / AGENDA / REPORTING ───────────────────┐
   │  S2 (barrido interrumpida, cron 1h) ◄── depende de "Última actividad" (S1)  │
   │  Plataforma agenda ─► Google Calendar ─► A1 (confirmación) ─► "Agendan cita"│
   │  Schedule lunes 10h ─► OP1 (correo semanal, ⚠ modo test)                   │
   └────────────────────────────────────────────────────────────────────────────┘
```

Relaciones clave:
- **T3 → T1**: primero se registra el folio (clic-a-WA), después el lead lo menciona en WhatsApp y se cierra la atribución.
- **C1 → N1 → drip**: solo para leads nuevos, y el drip solo si NO recibieron link (gate `asesoria=='cero'`).
- **C1 (output con link) → R1 → R2**: rescate a los leads que recibieron link pero no agendaron.
- **S1 → S2**: el barrido de "interrumpida" depende de que "Contestó"/`Última actividad` se esté estampando (⚠️ S1 deploy pendiente).
- **A1 → `Agendan cita`**: apaga R1/R2/A2 (los guards de rescate chequean `Agendan cita`).
- **N1, R1/R2, O2 escriben memoria sintética** a `n8n_chat_histories` para que C1 (agente) no re-salude.

---

## Marcadores de incertidumbre

| Ítem | Qué falta confirmar | Impacto | Owner / cómo resolver |
|---|---|---|---|
| Estado `active` real de cada workflow | Varios export tienen `active:false` (Meta CAPI, Rescate, S1) pese a estar "en producción" | Definir qué dispara de verdad en el corte de migración | Confirmar en la instancia viva de n8n (`[TU-INSTANCIA-N8N]`) |
| Tool `contestan_2do` | Instruida en prompt (línea 343), pero NO existe como nodo | La métrica "contestó 2do mensaje" probablemente nunca se registra | Decidir en GHL: implementar o descartar; revisar con la agencia |
| Hardcode `{Programa}='BS'` en CTWA (T2) | ¿Intencional (1 pixel) o placeholder/bug? | Todo CTWA se atribuye al pixel Boarding (228398216567258) | Confirmar con cliente si CTWA debe mapear por campaña |
| Programas sin fila en Programas CAPI | Summer Camp / Pathway / Gap Year no tienen pixel | Su evento Lead CAPI puede no dispararse o fallar | Confirmar con Max/Mauricio qué pixels existen |
| Ambigüedad "Gap Year/Estudia-trabaja" vs "Estudiar y trabajar" | Dos entradas del prompt con links y expertos distintos que se solapan | El agente puede mandar link/experto equivocado | Confirmar taxonomía real con negocio |
| Rescate: 5 programas (envío) vs 6 (memoria) | "Estudio y Trabajo" nunca recibe mensaje de rescate (código muerto) | Leads "Estudio y Trabajo" con link no se rescatan | Fijar tabla única programa→(msg F1, F2, URL, tag) en GHL |
| `contiene_folio` = substring "Folio" en texto libre | Frágil; depende de que el agente lo escriba literal | Ruteo folio-vs-CTWA puede fallar | Flag estructurado `origen` (landing\|ctwa) en GHL |
| `Update record3` (T1): busca por `{id}`, matchea por `id_2` | Si `id≠id_2` en la base, el update falla | Lead puede quedar sin Folio/fbclid estampado | Revisar datos reales de Leads |
| Formato `Timestamp` en Folios CAPI (ms vs s) | Usado crudo en `fb.1.{ts}.{fbclid}` | Si estuviera en s, el `fbc` queda mal formado para Meta | Inspeccionar valores reales del CSV Folios CAPI |
| `Cron cada 5 min` (O2) sin `minutesInterval` | n8n corre cada 1 min por default | Más carga de polling que el nombre sugiere | Confirmar/fijar el intervalo en n8n |
| Touch 2/3 sin `¿Subscriber OK?` | Fallo de sendFlow no se detecta pero Toques igual +1 | Posible pérdida silenciosa de toque | Agregar validación/log (o resolver nativo en GHL) |
| S1 (Estado "Contestó") deploy | `active:false` + CLAUDE.md "pendiente aplicar los 3 EDITs" | Si no está vivo, `Última actividad` no se estampa → afecta O2 y S2 | Confirmar en n8n vivo |
| Flow "Elevar" `Notify Assignees: 0 people` | ¿Bug o config incompleta? | El equipo humano podría no enterarse de elevaciones | Revisar en ManyChat con Max/Mauricio |
| A1: paths Diego/Andres con refs a nodos inexistentes | `$('Obtener ID Manychat')`/`...2` no existen | Probablemente solo Rodrigo confirma citas OK en prod | Verificar en n8n vivo si esos paths están rotos |
| A1: dónde se setea `Estado conversación='Cita confirmada'` | A1 solo setea `Agendan cita=true` | El estado terminal que S1/S2 protegen puede no poblarse | Rastrear qué workflow lo escribe |
| Plataforma de agendamiento (A1) | ¿Calendly / cal.com / booking propio? | Define cómo se migra el trigger en GHL Calendars | Confirmar con cliente |
| A2 vs R1/R2 coexistencia | A2 (48h) está disabled; R1/R2 (45min+24h) activo | Consolidar en GHL o mantener duplicado | Definir en Etapa 3 |
| Canales IG/FB | El main es WhatsApp-only (`whatsapp_phone`) | ¿IG/FB entran por otro webhook? | Confirmar arquitectura multi-canal |
| Secretos hardcodeados | OpenAI `sk-proj-…`, Bearer ManyChat `3256256:…`, Token Clientify `3822fcd1…` | Riesgo de seguridad en export/handoff | **Rotar y mover a credenciales antes de migrar** |
| Métricas de "Reporte semanal" (OP1) | Dónde se agregan (rollups Airtable u otro proceso) | El trabajo real de migrar el reporte está aguas arriba, no en OP1 | Inspeccionar config de la tabla Reporte semanal |
| Filas MX viejas en Supabase (52 de 12 díg) | Query §6 detecta si quedan | Conversaciones huérfanas al cruzar contra Leads.Telefono | Correr query §6 antes de migrar; normalizar 52→521 |
