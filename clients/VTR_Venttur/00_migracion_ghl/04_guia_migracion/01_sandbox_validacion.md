# 01 · Validación de sandbox — las asunciones de plataforma GHL

> ### 🔄 Estado a 2026-09-07
> **✅ Validado headless (NO necesita canal):** (a) match del upsert **por teléfono** (GHL no normaliza formato → canonicalización previa obligatoria) · (b) `dateAdded` histórico **NO** se acepta → va al CF `fecha_alta_original` (poblado 25/25 en muestra) · (h) **DND** por-contacto para el handoff · **(i) query de Contacts por custom field RESUELTO** (`filters:[{field:"customFields.<id>",operator:"eq",value:...}]` → 200; el 400 previo era de sesión) → **desbloquea despachador + barrido**.
> **🆕 Hallazgo:** operadores **`ne` / `gt` sobre custom field → 422** (no hay filtros de negación ni rango por CF; se resuelve con filtro positivo + gate en código).
> **🔴 Pendientes (necesitan nº de test / calendario personal conectado):** **B1** Contact Reply trigger · **B2** free-form <24h · **B3** template por API · **B4** URL de media de audio · **C1** disponibilidad compartida. Artefactos de juguete `ZZSBX`/`zzz` ya limpiados.

> **⭐ Deliverable #1 de la Etapa 4. Gate maestro.** Antes de tocar cualquier dato de producción, cada asunción load-bearing de la arquitectura (Etapa 3, `00_overview.md §7.10`, más las que agregan `03 §6.9/§6.2` y `05 §5`) se prueba en la **sub-cuenta GHL de sandbox**. Si una falla, el diseño ya tiene un fallback anotado; algunos fallbacks **cambian el diseño y requieren OK del cliente** (marcados 🔶). **Nada de producción se da por cerrado hasta que esta tabla esté toda en verde.**
>
> **Para quién:** la agencia (implementador). **Prerequisito:** sub-cuenta GHL creada (✅) + un Private Integration token con scopes (ver §0). **Referencia:** `03_arquitectura_ghl/00_overview.md §7.10`, y por check el doc que se cita.

---

## 0. Prerequisitos de acceso (antes de correr un solo check)

La API v2 de GHL (LeadConnector) requiere un token con scopes, no la API key v1 de la location.

- **Crear Private Integration:** `Settings → Private Integrations → Create` en la sub-cuenta. Scopes mínimos para este checklist: `contacts.readonly` · `contacts.write` · `opportunities.readonly` · `opportunities.write` · `calendars.readonly` · `calendars.write` · `calendars/events.readonly` · `calendars/events.write` · `conversations.readonly` · `conversations.write` · `conversations/message.write` · `locations/customFields.readonly` · `locations/customFields.write` · `workflows.readonly`.
- **Base URL:** `https://services.leadconnectorhq.com`
- **Headers en toda llamada:**
  ```
  Authorization: Bearer [PIT_TOKEN]
  Version: 2021-07-28
  Content-Type: application/json
  ```
- **`locationId`:** `[LOCATION_ID_SANDBOX]` (lo da la URL de la sub-cuenta o `GET /locations/`).

> ⚠️ Los nombres de endpoint que siguen son **el camino a probar**, no un hecho cerrado: parte de lo que este módulo valida es justamente que existan y se comporten como asume el diseño. Cuando un check dependa de un endpoint no documentado públicamente, se marca 🔍 y se prueba primero con un `GET` inocuo.

**Convenciones:** `[VALOR]` = completás vos · ⚠️ paso crítico · ✅ checkpoint · 🔶 el fallback cambia el diseño → **requiere OK del cliente** · 🔍 endpoint/comportamiento a confirmar antes de asumirlo.

**Modo de ejecución:** con token API → corré los checks marcados `[API]`; los `[UI]` se prueban a mano en la sub-cuenta. Sin token → todo el módulo funciona como checklist manual (los `[API]` con curl los corre el operador). **Ninguno de estos checks toca producción** — todo se prueba con contactos/citas de juguete en la sandbox.

---

## Grupo A — Identidad, datos e import (🔴 riesgo #1/#2)

### A1 · Dedup / upsert de Contacts: orden de match y no-normalización de teléfono `[API]`
**Asunción del diseño (`02 §2`, `00 §7.10a`):** el upsert deduplica por teléfono y/o email, **NO normaliza el formato del teléfono** (match string-exacto), y el comportamiento depende del setting *Allow Duplicate Contacts*. Es la premisa que hace **obligatoria la canonicalización previa** (52→521) y define el orden de resolución del merge de ~8.575 Contacts.

**Qué probar:**
1. Setear la sub-cuenta con *Allow Duplicate Contacts* = **OFF** (`Settings → Business Profile`/`Contacts`).
2. `POST /contacts/upsert` con `{phone: "+5213312345678", firstName: "Test A"}` → guardar el `contact.id` devuelto.
3. `POST /contacts/upsert` con el **mismo** teléfono, `firstName: "Test A2"` → ¿devuelve el mismo `id` (merge) o crea otro?
4. `POST /contacts/upsert` con la **variante sin el 1**: `{phone: "+523312345678"}` (mismo número nacional, 12 díg) → ¿matchea al de 13 díg o crea un duplicado?
5. `POST /contacts/upsert` con `{email: "test@x.com", phone: "+5213312345678"}` donde el email es nuevo pero el teléfono existe → ¿gana el teléfono (merge) o crea por email?
6. Repetir el paso 3 con *Allow Duplicate Contacts* = **ON** para ver la diferencia.

**Resultado esperado (PASS):** paso 3 mergea (mismo id); **paso 4 crea un duplicado** (confirma que NO normaliza → canonicalización previa obligatoria); paso 5 documenta el orden de precedencia (esperado: teléfono manda si existe). Lo que importa cerrar: **el orden de match (email vs teléfono) y que 52/521 NO colapsan solos.**

**Si falla / hallazgos:**
- Si el paso 4 **sí** mergea (GHL normaliza MX solo) → la canonicalización sigue siendo buena práctica pero deja de ser bloqueante. **No** relajar igual: el merge entre Airtable y Clientify también depende de la forma única.
- Si el orden de match no es el asumido → ajustar el orden de carga del pre-proceso (`06`): construir la clave de dedup en el ETL con el criterio real de GHL, no al revés.

**Impacto:** load-bearing del import completo (`06`). Sin esto cerrado, los 1.855 solapados Airtable∩Clientify y los 170 de doble-variante se duplican.

---

### A2 · Fechas históricas seteables (`dateAdded` / `dateUpdated` / `lastActivity`) `[API]`
**Asunción (`02 §4/§5/§9.6`, `00 §7.10b`):** al importar, GHL **acepta valores históricos** de fecha de alta/actividad. Si no, la fecha va a un custom field (`fecha_alta_original`, `ultima_actividad`) y `dateAdded` queda estampada al momento del import.

**Qué probar:**
1. `POST /contacts/` con `{phone:"+5213311111111", dateAdded:"2024-03-15T10:00:00Z"}` 🔍 (probar el campo; puede llamarse distinto o ignorarse).
2. `GET /contacts/[id]` → ¿el `dateAdded` es 2024-03-15 o la fecha de hoy?
3. Repetir vía **import por CSV** en la UI (`Contacts → Import`): mapear una columna a "Date Added" si el importador la ofrece.

**Resultado esperado (PASS):** el `dateAdded` refleja 2024-03-15 (por API **o** por CSV, con que uno de los dos ande alcanza).

**Si falla (fallback ya en diseño):** `created` de Clientify / `Creada` de Airtable → **custom field `fecha_alta_original`** (fecha), y `last_contact`/`Última actividad` → **custom `ultima_actividad`**. `dateAdded` de GHL queda como "fecha de import" y **no se usa** para el reporte ni el barrido. → ajuste en `02`/`06` (sin OK de cliente, es interno).

**Impacto:** medio. No bloquea el canal; sí la fidelidad del histórico y el cálculo del reporte si dependiera de la antigüedad.

---

### A3 · Status `abandoned` de Opportunity seteable por API/import `[API]`
**Asunción (`03 §6.2`, `00 §7.10`):** GHL tiene status `open/won/lost/abandoned`; Clientify tiene `Expired` (**1.875 deals, 80% del total**) → mapear `Expired`→`abandoned`. Hay que confirmar que `abandoned` es seteable **por API/import**, no solo desde la UI.

**Qué probar:**
1. Crear un pipeline + stage de juguete.
2. `POST /opportunities/` con `{status:"abandoned", pipelineId, pipelineStageId, contactId, name:"deal test"}`.
3. `GET /opportunities/[id]` → ¿`status` = abandoned?
4. Probar también el **import por CSV** de opportunities: ¿el importador ofrece `abandoned` como valor de status, o solo open/won/lost?

**Resultado esperado (PASS):** `abandoned` seteable por al menos uno de los dos caminos.

**Si falla (fallback):** cargar esos 1.875 como `lost` + un **custom field `status_origen_clientify` = "Expired"** que preserva el dato real, y documentar que el reporte **no cuente `lost` histórico como perdido-comercial**. → ajuste en `03`/`06` (interno).

**Impacto:** alto en volumen (80% de los deals). No bloquea el canal; sí la fidelidad del pipeline comercial.

---

### A4 · Companies: custom fields + `assignedTo` + relación con Opportunity `[API]` `[UI]`
**Asunción a validar (`03 §4/§6.9`, `00 §7.10`):** el objeto Company de GHL acepta **custom fields arbitrarios** (sector/rfc/social) y `assignedTo`; y hay que ver si existe relación **Opportunity↔Company** directa o solo vía el Contact.

**Qué probar:**
1. `GET /locations/[loc]/customFields?model=company` 🔍 → ¿el modelo `company` admite custom fields?
2. Crear una Company (`POST /companies/` 🔍 o UI) con `name`, un custom field y `assignedTo`.
3. Crear una Opportunity y ver si se puede asociar a la Company directamente, o solo el **Contact** se asocia a la Company.

**Resultado esperado (PASS):** Company acepta CF + assignedTo; se confirma que el vínculo escuela↔deal se deriva **vía el Contact** (Contact↔Company nativo), no directo.

**Si falla (fallback ya en diseño):** los CF que Company no soporte → **nota** en la Company o se descartan; el vínculo Opportunity↔escuela se resuelve vía Contact↔Company (ya es el plan). → ajuste en `03` (interno).

**Impacto:** bajo (266 companies, son escuelas de destino ligadas a deals de delivery). No bloquea.

---

### A5 · Query de Contacts por custom field **y por teléfono** vía API `[API]`
**Asunción (`09 §8.7`, `05 §5`, `00 §7.10i`):** el **cron del despachador** y el **barrido de interrumpida** filtran Contacts por valor de custom field (`link_enviado`, `toques_enviados`, `estado_conversacion`, `cita`); y el **CAPI** resuelve el lead por **teléfono** vía la GHL API (reemplaza el lookup a Airtable Leads congelado). Sin query eficiente, ni el despachador ni el barrido ni el enganche CAPI se construyen como se describen.

**Qué probar:**
1. Crear 3 contactos con distintos valores de un custom field `link_enviado` (true/false).
2. **Por teléfono:** `GET /contacts/?locationId=[loc]&query=+5213312345678` (o el endpoint de búsqueda) → ¿devuelve el contacto exacto?
3. **Por custom field:** `POST /contacts/search` 🔍 con un filtro por `customField` = `link_enviado:true` → ¿devuelve solo los que matchean, y de forma paginable/eficiente para correr en un cron?
4. Medir: ¿se puede paginar sobre miles de contactos sin traer todo a n8n?

**Resultado esperado (PASS):** búsqueda por teléfono exacta (para CAPI) + filtro server-side por custom field paginable (para despachador/barrido).

**Si falla (fallback):**
- Si no hay filtro server-side eficiente por CF → el despachador/barrido mantiene un **índice liviano en Postgres/Supabase** (o Airtable) con `contact_id + los 4-5 flags`, actualizado por los mismos workflows que escriben los flags, y el cron lee de ahí. Es n8n-first igual; agrega una tabla de estado. → ajuste en `08`/`09`.
- Si el lookup por teléfono no es exacto → el CAPI cae al fallback (b) de `05 §5` (sync liviano GHL→Airtable solo para CAPI).

**Impacto:** alto. Es el motor del re-enganche (`09`) y del enganche CAPI (`05`).

---

### A6 · Moneda mixta (MXN + USD) en Opportunities `[API]` `[UI]`
**Asunción (`03 §6.1`):** GHL fija la moneda a **nivel location**, pero los deals de Clientify vienen en **las dos monedas mezcladas**. El diseño recomienda la opción (a): `monetaryValue` numérico + un custom field `moneda` por Opportunity (preserva el dato; el rollup pierde precisión). Hay que confirmar que GHL guarda el `monetaryValue` como número crudo sin forzar conversión por la moneda de la location.

**Qué probar:**
1. Setear la moneda de la location (`Settings → Business`) en `MXN`.
2. Crear un custom field de Opportunity `moneda` (dropdown MXN/USD).
3. `POST /opportunities/` con `{monetaryValue: 5000, customFields:[{key:"moneda", value:"USD"}]}` → `GET` → ¿el `monetaryValue` quedó en 5000 (crudo) y el custom `moneda`=USD, sin que GHL lo reinterprete como 5000 MXN ni lo convierta?

**Resultado esperado (PASS):** `monetaryValue` se preserva como número + `moneda` distingue MXN/USD (opción a). El rollup por pipeline mezclará monedas (aceptado — el cliente depura después).

**Si falla (fallback):** opción (b) — normalizar a una sola moneda con TC histórico. **Altera los montos históricos** → aunque es un ajuste interno de import, conviene avisar al cliente que sus montos quedan convertidos (no es su dato crudo). Registrar en la tabla.

**Impacto:** medio (fidelidad de montos del pipeline comercial — que con B3=Opción A migra completo antes del 15/9). No bloquea el canal.

---

## Grupo B — Canal conversacional (🔴 riesgo #3)

### B1 · Contact Reply trigger de entrada (WA/IG/FB) → HTTP a n8n `[UI]` `[API]`
**Asunción (`06 §1/§3`, `08` wf1, `00 §7.10e):** existe un trigger de "mensaje entrante / cliente respondió" para **WA e IG/FB**, que dispara un **Webhook/HTTP a n8n** pasando **el cuerpo del mensaje + el contact id + el canal**. Es el path de **TODO** el inbound — sin esto no hay agente.

**Qué probar:**
1. En `Automation → Workflows`, crear un workflow con trigger **"Customer Replied"** (o "Inbound Message") filtrando por canal, y acción **Webhook** apuntando a un endpoint de prueba (webhook.site o el n8n de sandbox).
2. Mandar un WhatsApp de prueba al número de la sub-cuenta → inspeccionar el payload que llega: ¿trae `message.body`, `contactId`, `conversationId`, `channel`?
3. Repetir con un DM de **Instagram** y de **Facebook** conectados a la sub-cuenta (si están disponibles en sandbox) → ¿el mismo trigger cubre los 3 canales o hace falta uno por canal?
4. Confirmar que el trigger dispara con **cada** inbound (no solo el primero de la conversación).

**Resultado esperado (PASS):** el trigger dispara por cada inbound de WA/IG/FB y el webhook lleva cuerpo + contactId + canal → n8n puede reconstruir el `[CONTEXTO TURNO]`.

**Si falla (fallback):**
- Si el payload no trae el cuerpo → primer paso del workflow n8n hace `GET` del último mensaje de la conversación (`GET /conversations/[id]/messages`) para recuperarlo.
- Si IG/FB necesitan su propio trigger → se crean 3 workflows-trigger (WA/IG/FB) que pegan al mismo webhook n8n. No cambia la topología, solo el conteo de triggers.
- Si no existe trigger de inbound utilizable → **bloqueante duro**: sin path de entrada no hay canal. Escalar (revisar plan GHL / soporte) antes de seguir.

**Impacto:** 🔴 **bloqueante del canal entero.** Es el primero del Grupo B que hay que cerrar.

---

### B2 · Envío free-form de sesión <24h vía Conversations API `[API]`
**Asunción (`06 §4`, `00 §7.10d`):** dentro de la ventana de 24h, n8n envía **texto libre** (la respuesta dinámica del LLM, partida en N burbujas) por la Conversations API — **no** plantilla. Es el reply del agente.

**Qué probar:**
1. Que un contacto de prueba tenga una conversación WA abierta (mandó un inbound < 24h).
2. `POST /conversations/messages` con `{type:"WhatsApp", contactId, message:"texto libre de prueba 1"}` → ¿llega al WhatsApp del contacto como mensaje normal (no template)?
3. Mandar 3 en secuencia con ~1-2s de delay → confirmar que llegan como 3 burbujas (patrón multi-parte de `06 §4`).
4. Probar el mismo POST **fuera** de la ventana de 24h → confirmar que GHL/Meta lo **rechaza** (esperado: exige template) — así se conoce el borde exacto.

**Resultado esperado (PASS):** free-form llega dentro de 24h; se rechaza fuera. Confirma las **dos rutas** (`06 §4`).

**Si falla (fallback):** si GHL no expone send free-form por API dentro de ventana → usar el **canal de Conversations vía el Workflow Send Action** con el texto como variable, disparado por webhook desde n8n (menos elegante, mismo efecto). Si ni eso → reevaluar N.2 (agente en n8n) — sería el único caso que toca la decisión "agente queda en n8n". Marcar y escalar.

**Impacto:** 🔴 load-bearing del reply del agente. Sin free-form, todo mensaje del agente tendría que ser template (imposible para respuestas dinámicas).

---

### B3 · Send de Message Template Meta por API con merge params por programa `[API]`
**Asunción (`06 §4`, `09 §7`, `00 §7.10f`):** el re-enganche fuera de 24h (rescate/nurturing/outreach/recordatorios) manda **templates aprobadas** con **merge params dinámicos por programa**, disparadas **por API desde n8n** (el Workflow Send Action queda como alternativa).

**Qué probar:**
1. Tener al menos 1 template WA aprobada en la WABA de sandbox (o usar una existente).
2. Buscar el camino de envío por API: `POST /conversations/messages` con `{type:"WhatsApp", templateId/templateName, params:{...}}` 🔍 → ¿existe el envío de template por API con parámetros?
3. Si la API no lo expone: crear un **Workflow con "Send WhatsApp Template"** disparado por Webhook (inbound trigger desde n8n con `contactId` + params) → confirmar que renderiza los merge fields.
4. Confirmar que los params por programa (nombre, link de calendario, etc.) se inyectan correctamente.

**Resultado esperado (PASS):** existe **un** camino confiable (API directa **o** Workflow Send Action) para mandar template con params desde n8n.

**Si falla (fallback):** si no hay API directa, se usa el **Workflow Send Action** invocado por webhook — ya contemplado en `06 §4` como alternativa. No cambia el diseño; cambia el mecanismo de disparo (n8n → GHL workflow → template).

**Impacto:** 🔴 load-bearing de todo el re-enganche (`09`) y los recordatorios (`07`). Se cruza con `05` (WABA/templates) — coordinar.

---

### B4 · URL de media descargable del audio entrante `[UI]` `[API]`
**Asunción (`06 §6`, `00 §7.10g`):** un audio entrante de WhatsApp queda en GHL con una **URL de media descargable** que n8n baja para pasar a whisper-1. Es el **camino nuevo** que reemplaza la rama rota `Hay audios?`.

**Qué probar:**
1. Mandar una **nota de voz** de WhatsApp al número de sandbox.
2. Inspeccionar el payload del Contact Reply trigger (B1) y/o `GET /conversations/[id]/messages` → ¿el mensaje de audio trae una `attachmentUrl` / media URL?
3. Hacer `GET` a esa URL desde n8n (sandbox) → ¿devuelve el binario del audio (ogg/opus) descargable con el mismo token, o requiere auth distinta / expira?

**Resultado esperado (PASS):** hay URL descargable → n8n la baja → whisper. (El formato ogg/opus lo acepta whisper-1.)

**Si falla (fallback):** si no hay URL directa o expira → usar el endpoint de media/files de GHL para resolver el binario; si tampoco → degradar a "no transcribe, avisa que reenvíe por texto" (mejor que el string vacío de hoy). Documentar como camino nuevo a testear (`11`), no como "funciona tras migrar".

**Impacto:** medio. Hoy está roto de todos modos (nunca corrió); cualquier resultado ≥ 0 es mejora. No bloquea el cutover.

---

### B5 · Silenciar / pausar la automation por-contacto (handoff) `[API]` `[UI]`
**Asunción (`06 §5/§8`, `00 §7.10h`):** el handoff a humano (`elevar`) requiere **pausar la automation del bot para ese Contact** de forma **persistente y reversible** (equivalente al "pause forever" de ManyChat), sin frenar al resto.

**Qué probar:**
1. Opción DND: `POST/PUT /contacts/[id]` con `dnd:true` o los `dndSettings` por canal 🔍 → ¿corta los envíos automáticos a ese contacto?
2. Opción remove-from-workflow: acción "Remove from Workflow" / "Remove Contact from all workflows" → ¿lo saca de las secuencias activas?
3. Probar la **reversión**: reactivar y confirmar que el contacto vuelve al flujo normal.
4. Confirmar granularidad: que **solo** ese contacto queda pausado.

**Resultado esperado (PASS):** hay un mecanismo por-contacto, persistente y reversible (DND, remove-from-workflow, o un tag+condición que el despachador respete).

**Si falla (fallback):** si ningún mecanismo nativo sirve → un **custom field/tag `bot_pausado`** que **el despachador y el main de n8n chequean** antes de enviar (n8n-first: la pausa la respeta nuestra lógica, no la de GHL). → ajuste en `07 §5`/`08`.

**Impacto:** medio-alto. Sin esto, un lead elevado a humano seguiría recibiendo toques del bot (mala experiencia + el bug de hoy).

---

## Grupo C — Agendamiento (🟡 riesgo medio)

### C1 · Disponibilidad compartida entre los calendarios de un asesor 🔶 `[UI]`
**Asunción / requisito duro del cliente (`07 §2`, `cuestionario` P2, `00 §7.10c`):** los calendarios de un mismo asesor comparten disponibilidad real — un booking en "Internados" (martes 4pm) debe **desaparecer** de "Intercambio" y "Campamentos" del mismo asesor. **Rodrigo:** cal 1+2+3. **Andrés:** cal 4-8 (5 calendarios). GHL **no lo hace out-of-the-box.**

**Qué probar (en orden, parar en el primero que pase):**
- **(a) Calendario personal + check-for-conflicts:** conectar un Google/Outlook personal al usuario "Andrés" de sandbox; crear 2 calendarios GHL con "check for conflicts" contra ese calendario personal; agendar en el cal 1 → ¿el slot desaparece del cal 2?
- **(b) Team / Service calendars:** un mismo usuario en varios event-types de un calendario de equipo → ¿la disponibilidad se comparte nativamente entre event-types?
- Medir hasta 5 calendarios (el caso Andrés), no solo 2.

**Resultado esperado (PASS):** con (a) **o** (b), un booking en un calendario del asesor bloquea los otros del mismo asesor. **Sin dobles reservas.**

**Si falla (🔶 fallback que cambia el diseño → requiere OK del cliente):** **1 calendario por asesor con event-types por programa** (la disponibilidad se comparte porque es un solo calendario; el programa lo distingue el event-type). Cumple el objetivo real (sin dobles reservas + programa conocido al agendar) pero **contradice la instrucción literal de P2** ("un calendario por programa, no uno por asesor"). → **No se ejerce sin OK explícito del cliente** (registrar en la tabla §fin y en el doc del cliente).

**Impacto:** 🟡 alto para el modelo de calendarios (`04`/`07`). Es el punto técnico más incierto del diseño. **Probarlo temprano** — condiciona los 8 calendarios.

---

### C2 · Trigger de booking → n8n + query de appointments próximos `[UI]` `[API]`
**Asunción (`07 §3/§4`, `08` wf6, `00 §7.10j`):** el booking de un GHL Calendar **dispara un webhook/HTTP a n8n** (para la confirmación, que hoy está rota 0/11), y se pueden **leer las citas próximas por API** (para los recordatorios 24h/1h — el cron n8n que las lee es el fallback del trigger).

**Qué probar:**
1. Workflow con trigger **"Appointment / Customer Booked"** → acción Webhook a n8n → agendar una cita de prueba → ¿llega el payload con fecha/hora/asesor/contactId/calendarId?
2. `GET /calendars/events?...` (o el endpoint de appointments) 🔍 filtrando por rango de fechas → ¿devuelve las citas próximas con sus horas, para que un cron arme los recordatorios 24h/1h?
3. Confirmar que se puede leer el **estado** de la cita (agendada/cancelada/reagendada) para no mandar recordatorio de una cancelada.

**Resultado esperado (PASS):** trigger de booking dispara a n8n **y** hay query de citas próximas por API.

**Si falla (fallback):** si no hay trigger de booking → un **cron n8n** que barre las citas próximas por API cubre confirmación **y** recordatorios (el trigger es un lujo, no un requisito). Si tampoco hay query de appointments por API → **bloqueante** de confirmación+recordatorios: escalar. La confirmación también podría re-derivarse del cambio de etapa del pipeline operativo (`03 §5`) como último recurso.

**Impacto:** 🟡 alto para `07`. La confirmación hoy está rota; esto la reconstruye. Los recordatorios se construyen de cero sobre esto.

---

## Grupo D — Checks no-bloqueantes (opcionales)

### D1 · Reporting nativo de GHL sobre "citas agendadas por semana" `[UI]`
**Asunción (`08 §3`):** **el default del reporte semanal es n8n** leyendo Opportunities de GHL — **no depende del sandbox**. El reporting **nativo** de GHL sobre la etapa "Cita agendada" del pipeline operativo es solo una **alternativa**; validarlo únicamente si se prefiere sacar a n8n de ese reporte.

**Qué probar (solo si se evalúa la alternativa):** en `Reporting`/`Dashboards` de GHL, ¿se puede armar un widget de "conteo de Opportunities que entraron a la etapa **Cita agendada** por semana", exportable/programable por email?

**Resultado esperado:** si cubre la métrica exacta, es candidato; si no, se queda el default n8n. **Cualquier resultado es aceptable** — no bloquea nada (el default n8n siempre funciona).

**Impacto:** ninguno sobre el cutover. Se registra para no dejar el flag del diseño sin resolver.

---

## Tabla de resultados (llenar durante la corrida)

| Check | Asunción (1 línea) | Doc | Resultado (2026-09-03) | Evidencia | Fallback aplicado |
|---|---|---|---|---|---|
| A1 | Upsert: orden match + no-normaliza teléfono | 02 | ✅ **PASS** | upsert mismo tel → mismo id; `+5213300000001` vs `+523300000001` → **2 contactos** (NO normaliza) | canonicalización previa **obligatoria** (`06`) |
| A2 | Fechas históricas seteables | 02 | ✅ **FAIL-esperado** | `POST /contacts/` con `dateAdded` → **422 "should not exist"** | **custom `fecha_alta_original`** (`02`) |
| A3 | `abandoned` seteable API | 03 | ✅ **PASS** | opp `status:abandoned` → GET confirma abandoned | — |
| A4 | Company: CF + rel. Opp | 03 | ⚠️ **PASS c/corrección** | endpoint es **`/businesses/`** (no `/companies/`→404); create OK; **CF `model=company`→422** | CF de business → nota/descarte; Opp↔Company vía Contact |
| A5 | Query Contacts por CF y por teléfono | 09/05 | 🟡 **PARCIAL** | teléfono ✅ (`POST /contacts/search`, filtro anidado `{group,filters}`+`contains`); **CF ✗ (400)** | por CF → **índice Postgres** (`08`/`09`) o hallar sintaxis CF |
| A6 | Moneda mixta MXN+USD | 03 | ✅ **PASS** | opp `monetaryValue:5000` → GET conserva 5000 crudo | opción (a): custom `moneda` |
| B1 | Contact Reply trigger WA/IG/FB → n8n | 06 | ⬜ **MANUAL** | requiere inbound real + workflow en UI | — |
| B2 | Free-form <24h por API | 06 | 🟡 **PARCIAL** | Conversations API alcanzable (200); **envío NO ejecutado** (manda WA real) | pendiente: nº de test + OK |
| B3 | Send template Meta por API | 06/09 | 🟡 **PARCIAL** | idem B2 + requiere template aprobada | pendiente: template + nº de test |
| B4 | URL de media del audio | 06 | ⬜ **MANUAL** | requiere nota de voz entrante | — |
| B5 | Pausar automation por-contacto | 06 | ✅ **PASS** | `PUT /contacts/{id}` `dnd:true` → GET `dnd=true` | — |
| C1 | Disponibilidad compartida por asesor | 07 | ⬜ **MANUAL** | UI + calendario personal (0 calendarios aún) | 1-cal-por-asesor 🔶 |
| C2 | Trigger booking + query appointments | 07 | ✅ **PASS (endpoint)** | `GET /calendars/events` existe; pide `userId`/`calendarId`/`groupId` + rango epoch-ms | cron n8n (fallback trigger) |
| D1 | Reporting nativo GHL (opcional) | 08 | ⬜ opcional | default = n8n; no bloquea | — |

**Leyenda:** PASS (se sostiene) · FAIL-esperado (no se sostiene → fallback ya diseñado) · PARCIAL (anda con salvedad) · MANUAL (requiere UI/inbound/envío).

**Resumen corrida 2026-09-03:** de los 13 bloqueantes → **6 PASS** (A1, A3, A4*, A6, B5, C2-endpoint) + **A2 FAIL-esperado** (confirma el fallback) · **A5 PARCIAL** (teléfono ✅, CF ✗) · **B2/B3 PARCIAL** (no se envió nada) · **B1/B4/C1 MANUAL**. **Ningún resultado invalida la topología** — todos caen en fallbacks ya previstos en el diseño. *(A4 con corrección de endpoint: `/businesses/`.)*

### Hallazgos operativos de la corrida (load-bearing para la ejecución)

1. ⚠️ **`User-Agent` obligatorio.** La API de GHL responde **Cloudflare 1010 (`browser_signature_banned`)** al UA por defecto de las librerías (python-urllib, etc.). Hay que mandar un UA normal (browser-like). **Afecta a cualquier nodo HTTP Request de n8n que pegue a GHL en crudo** + a los scripts de import. (n8n suele mandar su propio UA; verificar por nodo.)
2. **Companies = endpoint `/businesses/`** (v2), NO `/companies/` (404). GET/POST OK. Custom fields sobre business **no** soportados (`model=company`→422). → `03 §4`/`06`.
3. **Búsqueda de Contacts:** `POST /contacts/search` con filtro **anidado** `{"group":"AND","filters":[{"field","operator":"contains","value"}]}`. El `GET ?query=` y el filtro plano **no** matchean fiable. **Filtro por custom field dio 400** (sin resolver) → si no se halla la sintaxis, el despachador usa el **índice Postgres** (fallback ya en `08`/`09`).
4. 🆕 **`OPPORTUNITY_NO_DUPLICATE`:** GHL bloquea una 2ª opp para el **mismo contacto** en un pipeline (probado: 2ª opp para el mismo contacto → 400; para otro contacto → 201). **Impacto en el import de 2.338 deals:** un contacto Clientify con varios deals en el mismo pipeline colisiona. Probable **setting "Allow Duplicate Opportunity"** a activar (familia de *Allow Duplicate Contacts*). → **resolver en `03`/`06` antes del import.**
5. **`dateAdded` no seteable por API** (422) — el import histórico de fecha de alta va a `fecha_alta_original` (custom). *(Queda por probar si el import por CSV de la UI lo admite; el camino API está cerrado.)*
6. ✅ **Capacidad de creación por PIT (probado 2026-09-03, artefactos borrados):** **API-creables** — custom fields, custom values, **tags** (create+delete), **pipelines** (piden `stages[].position` numérico — NO son solo-UI), **calendarios** (create+delete), **businesses**, contacts, opportunities. **Users:** creables pero el `POST /users/` pide el `companyId` correcto (el de la location, `WbuYAfjKqOU9k7R5t9RL`) + emails reales → la mayoría de la estructura se construye por API sin tocar la UI. **Solo-UI / manual:** conexión de la WABA (`05`), conexión de los calendarios personales de los asesores para la disponibilidad compartida (C1), y el toggle de settings tipo "Allow Duplicate Opportunity"/"Allow Duplicate Contacts".
7. ✅ **n8n API (`[TU-INSTANCIA-N8N]`) accesible** — `GET /api/v1/workflows` → 200 con `N8N_BASE_URL`+`N8N_API_KEY` del `.env`. Se pueden crear/leer/actualizar workflows por API (header `X-N8N-API-KEY`, + el mismo UA por prolijidad).

### Artefactos de juguete creados (limpiar antes de producción)
Contactos `cjO6zKlRaeHdpPPwlIop`, `J4eBGuKUUOVrdLmbQv85`; opps `crTmU3qpJGierj4aTbpL`, `rn5FzWTlxjxcc3mcyoLe`; custom field contacto `zzz sbx flag` (`3MXRp9h0yBuiJTUxfGSg`); business `ZZSBX Escuela`. Prefijo `ZZSBX`/`zzz`. **No los borré** (política anti-delete) — si esta sub-cuenta es la que va a producción, borrarlos a mano o avisame y los elimino.

---

## Fallbacks que requieren OK del cliente (🔶)

Solo **C1** puede caer en un fallback que contradice una instrucción explícita del cliente:

| Check | Instrucción del cliente | Fallback técnico | Qué pedirle al cliente |
|---|---|---|---|
| C1 | "Un calendario por programa (8), NO uno por asesor" (P2) | 1 calendario por **asesor** con event-types por programa | Que acepte 1-cal-por-asesor **si** (a)/(b) no logran disponibilidad compartida entre 8 calendarios independientes. El objetivo real (sin dobles reservas + programa conocido al agendar) se cumple igual. |

Los demás fallbacks (A2, A3, A4, A5, B2, B3, B4, B5) son **internos** (custom field en vez de campo nativo, tabla de índice en Postgres, Workflow Send Action en vez de API directa) — no cambian lo que el cliente ve ni tocan una decisión suya, así que **no requieren su OK**, solo quedan registrados.

---

## Qué desbloquea cada check (mapa a los módulos)

| Si pasa… | Se desbloquea |
|---|---|
| A1, A2, A3, A4, A5, A6 | `06` (pre-proceso + import de datos) y el `03` (pipelines/opportunities) |
| A5 (query por CF) | `08` (despachador) y `09` (barrido de interrumpida) |
| A5 (query por teléfono) | `09`/`05` (enganche CAPI→Contact) |
| B1 | `07` (main / canal de entrada — **el path de todo el inbound**) |
| B2 | `07` (reply free-form del agente) |
| B3 | `09` (re-enganche) + `07`/`04` (recordatorios y confirmación por template) |
| B4 | `07` (transcripción de audio — camino nuevo) |
| B5 | `07 §handoff` |
| C1 | `04` (los 8 calendarios / o el fallback 1-por-asesor) |
| C2 | `04` (confirmación + recordatorios) |

> **Regla del gate:** un módulo aguas abajo **no se construye para producción** hasta que sus checks estén en verde (o con el fallback aplicado y, si es 🔶, con OK del cliente). Los módulos `02` (custom fields base) y `03`/`05` (crear pipelines/templates vacíos) se pueden **empezar en paralelo** al sandbox porque no dependen de estos comportamientos; lo que espera al verde es la **carga de datos** y el **cableado de lógica**.

---

## Nota de ejecución (acceso API)

Este módulo está escrito para correr **con o sin** acceso API a la sandbox:
- **Con Private Integration token:** los checks `[API]` se corren con curl/n8n y se pegan las respuestas como evidencia; los `[UI]` se hacen a mano. Si me pasás el token (`[PIT_TOKEN]` + `[LOCATION_ID_SANDBOX]`), ejecuto los automatizables y lleno la tabla.
- **Sin token:** el operador corre los `[API]` con curl y los `[UI]` en la interfaz; la tabla se llena igual.

---

*Corroborado contra `03_arquitectura_ghl/00_overview.md §7.10` + banderas de `02 §9`, `03 §6`, `05 §7`, `06 §8`, `07 §6`, `09 §8`. Los endpoints marcados 🔍 se confirman en la corrida — este módulo existe precisamente para eso. 2026-09-02.*
