# 01 — Mapa Funcional Completo

> **Reescrito 2026-07-24** con los inputs completos de Etapa 0 (14 workflows n8n + snapshot de datos de las 5 plataformas + 6 CSVs Airtable + system prompt del agente + schema Supabase). Supera la versión de mayo 2026, que se generó con inputs parciales y contenía errores materiales (ver "Correcciones vs. versión mayo 2026" más abajo y el doc 06).
>
> **Fuentes primarias usadas:** los 14 JSON de workflow en `00_inputs/wf-*.json` (análisis nodo-por-nodo) · `04_agents/agente-venttur-system-prompt-EXTRAIDO-2026-07-24.md` (system prompt del agente Mauricio, 40.414 chars) · `00_inputs/vtr-data-snapshot-2026-07-24.json` (ManyChat 16 flows/5 tags/13 custom fields + Clientify + Supabase) · `00_inputs/manychat-flows-content-2026-07-20.md` (contenido interno de flows) · `00_inputs/supabase-queries-venttur.md` (schema + quirk MX) · `00_inputs/airtable-csvs/{leads,folios-capi,programas-capi,mensajes-anuncios,reporte-semanal}.csv` · `00_inputs/README.md` · `ESTADO_MIGRACION.md`.

### Correcciones vs. versión mayo 2026

- **❌→✅ "No hay agente conversacional IA":** FALSO. El corazón del sistema es un AI Agent conversacional llamado **"Mauricio"** (gpt-4o, temperature 0) que vive inline en el nodo `Agente IA WPP` de `wf-venttur-main.json` (systemMessage de ~39K chars), con metodología propia **EMA**, marcos Chris Voss + Alex Hormozi, memoria Postgres/Supabase y tools técnicas. Todo lo de mayo sobre "sistema puramente reactivo" era incorrecto.
- **Rescate Post-Link:** ya NO es "diseñado, no activado" ni vive en ManyChat — es el workflow n8n `wf-rescate-post-link` (`mkEP1qFN7MVb9qP0`) en producción, con memoria sintética.
- **Outreach proactivo WA:** ya NO es "no implementado" — es `wf-outreach-form-meta` (`CUuFxbst3iHpgeXS`) en producción, **tri-toque** desde Google Sheets sync de Meta Lead Ads.
- **Subsistemas nuevos que mayo no documentaba:** Estado de lead (2 workflows), Nurturing 4-toques por programa (6 flows ManyChat), Correo semanal, y los sub-workflows de agenda/resumen/seguimiento.
- **Modelo de datos ampliado:** Airtable Leads tiene **30 columnas** (mayo documentó ~9), con las FK `ID Clientify` / `ID Manychat` / `Folio` que resuelven el cruce cross-plataforma.
- **Clientify:** volumen real confirmado (6.968 contactos / 2.338 deals / 266 companies / 22 custom fields); deals/companies YA existen (mayo los daba "a verificar").
- **CAPI rama CTWA:** confirmada y cableada (mayo la daba "no visible en JSON").

---

## 🆕 Validación con el cliente — 2026-08-17 (Etapa 2)

> Respuestas de **Mauricio García** (revisadas sobre el borrador de Max) al cuestionario
> `02_validacion_cliente/cuestionario-venttur-2026-07-24.md`. Lo de acá abajo **supera** al cuerpo de
> este documento donde haya conflicto. Mapeo completo a las preguntas internas en
> `02_validacion_cliente/preguntas-cierre-2026-07-24.md` (A1..A11). Lo que quedó abierto está en
> `02_validacion_cliente/puntos-abiertos-ronda-2-2026-08-18.md`.
>
> **Fecha objetivo de cutover confirmada: 15 de septiembre de 2026.**

### Lo que cambia en el mapa funcional

**1. Taxonomía canónica: 8 programas (antes se modelaban 6 + Francia + Lead General).**

| # | Programa canónico | Asesor | Equivalente en el sistema actual |
|---|---|---|---|
| 1 | Internados (Boarding School) | Rodrigo | `Boarding IA` / `Boarding School` |
| 2 | Intercambio académico con familias | Rodrigo | `AA Familiar` |
| 3 | **Viajes educativos** | Andrés | **no existe** |
| 4 | **Educación superior** | Andrés | **no existe** |
| 5 | Campamentos de verano | Rodrigo | `Summer Camp` |
| 6 | **Cursos de idiomas en el extranjero** | Andrés | solo un link suelto en el prompt |
| 7 | Pathway Alemania | Andrés | `Pathway IA` |
| 8 | Gap Year / Estudia y Trabaja | Andrés | `Gap Year` + `Estudio y Trabajo` (fusionan) |

- **`Francia` se elimina del modelo.** Es un DESTINO, no un programa. Regla nueva: los destinos se
  guardan como **nota en el contacto**, nunca como campo estructurado.
- **3 de los 8 programas no tienen ninguna huella en el sistema** (fila 3, 4 y parcialmente 6):
  sin enum, sin drip, sin rama de rescate, sin pixel. Verificado por grep exhaustivo. Es **scope
  nuevo de Etapa 3**, no una corrección. Ver detalle en A2 del máster.
- **Diego sale del mapa de ruteo.** Trabaja leads orgánicos propios fuera del flujo del agente.

**2. 🚨 Componente que faltaba en el mapa: hay DOS números de WhatsApp en operación.**

El mapa de este doc modela un único canal WhatsApp (ManyChat). La realidad son dos:

| Número | Plataforma | Qué manda |
|---|---|---|
| A | ManyChat | El agente "Mauricio": conversación y agendamiento |
| B | **Clientify** | **Los recordatorios de cita** |

Causa: el agente nunca se pudo conectar al chat de Clientify. Efecto: el lead agenda con un número y
recibe el recordatorio desde otro. **Esto explica por qué los recordatorios de cita "existen" para el
cliente pero no aparecen en ninguno de los 14 workflows n8n** que analizamos: viven en Clientify,
fuera del perímetro que este doc mapeó. Estado destino: **un solo número** para conversación,
confirmación y recordatorios.

**3. Clientify se apaga entero y su pipeline se reconstruye en GHL.**
Migra el histórico COMPLETO (6.968 contactos + 2.338 deals abiertos/ganados/perdidos + 266
companies), con las mismas etapas, nombres y orden, sin rediseño. Las transiciones de etapa siguen
siendo manuales. Gate duro previo al apagado: auditoría de qué es replicable y qué no.

**4. Entrada de leads: las dos rutas no son paralelas.** El formulario nativo de Meta **sustituyó** a
la landing `go.venttur.com/bs` (no la complementa). La landing sigue viva al 100% para orgánicos y
hay que **repuntarla a GHL**. Los campos difieren entre rutas, así que el sistema debe tolerar leads
con datos parciales y completarlos en la conversación.

---

### ⚠️ Nota sobre la versión que el cliente respondió

El cuestionario que Mauricio contestó es la **versión de 12 preguntas enviada el 2026-08-07**. El
archivo del repo se amplió a **14 preguntas el 2026-08-17** (tras el Reporte la agencia 1), agregando
*rangos de precio* y *qué significa "Cerrada"*, y reescribiendo las de seguimiento y confirmación de
cita. **Esas cuatro modificaciones nunca le llegaron al cliente.** Por eso hay respuestas que
contestan la redacción vieja, y dos temas que quedaron sin preguntar. Se resuelven en
`puntos-abiertos-ronda-2-2026-08-18.md`.


## 1. Visión general del sistema (CORREGIDA)

Venttur Education & Travel es una consultora mexicana de movilidad académica internacional que ofrece ~6 programas conceptuales (internados/boarding, año académico con familia, summer camp, pathway Alemania, gap year / estudia y trabaja). El sistema automatizado **NO es puramente reactivo**: combina siete subsistemas que giran alrededor de un agente conversacional de IA.

| # | Subsistema | Qué hace | Workflow(s) / componente |
|---|---|---|---|
| 1 | **Agente conversacional "Mauricio"** | Atiende cada mensaje de WhatsApp, cualifica al lead con un diagnóstico de 7 pasos, asesora por programa y ofrece el link de asesoría | `wf-venttur-main` (nodo `Agente IA WPP`, gpt-4o) + memoria Supabase + tools |
| 2 | **Tracking de atribución (Meta CAPI)** | Envía eventos `Lead` server-side a Meta (Graph API v21.0) por cada mensaje, con 2 ramas: folio (landing) y CTWA (click-to-WhatsApp) | `wf-meta-capi` + `wf-capi-registro-folio` |
| 3 | **CRM / captura de leads** | Alta y dedup de leads en Airtable + sincronización con Clientify (contactos, tags, notas) | `wf-formulario-clientify` + `wf-crear-contacto-clientify-airtable` |
| 4 | **Rescate post-link** | Reengancha en 2 fases (45 min + 24 h) a leads que recibieron el link de asesoría y no agendaron; siembra memoria sintética | `wf-rescate-post-link` + `wf-actualizar-link-enviado` |
| 5 | **Outreach proactivo (Form Meta)** | Convierte leads de Meta Lead Ads (Google Sheet) en secuencia tri-toque por WhatsApp; siembra memoria sintética | `wf-outreach-form-meta` |
| 6 | **Nurturing / seguimiento** | Confirma citas agendadas, dispara drips de nurturing por programa (4 toques), recordatorio de agenda a 48 h, y clasifica/cualifica al lead post-conversación | `wf-confirmacion-agenda` + `wf-resumen-etiquetas-seguimientos` + `wf-seguimiento-agenda` + 6 flows ManyChat |
| 7 | **Estado de lead + reporting** | Estampa `Estado conversación` (Contestó / Conversación interrumpida) y produce el reporte semanal del embudo | `wf-estado-lead` + `wf-estado-interrumpida` + `wf-correo-semanal` |

El **source-of-truth operativo** del lead es la tabla **Airtable Leads** (`[AIRTABLE_TABLE_ID]`); ManyChat es el canal, Supabase es la memoria conversacional, Clientify es el CRM comercial paralelo (gestión manual del equipo Venttur), y Meta CAPI + Airtable Folios/Programas CAPI son la capa de atribución.

---

## 2. Diagrama de arquitectura (end-to-end)

```
                          FUENTES DE ENTRADA
   ┌───────────────────────┬───────────────────────┬───────────────────────────┐
   │  Landings go.venttur   │   Meta Lead Ads (form) │  WhatsApp (inbound directo │
   │  (clic-a-WhatsApp)     │                        │   / CTWA / respuesta)      │
   └───────────┬────────────┴───────────┬───────────┴───────────┬───────────────┘
               │ POST webhook            │ sync Google Sheet     │ mensaje entrante
               ▼                         ▼                       ▼
   ┌────────────────────────┐  ┌────────────────────────┐  ┌──────────────────────────┐
   │ CAPI Registro Folio     │  │  Google Sheet           │  │  ManyChat "Venttur|Agente │
   │ (9yCbynoKDt9hgiBq)      │  │  Boarding_Schools_...    │  │  de IA" (plan Pro, TZ      │
   │  → Airtable Folios CAPI  │  │        │                 │  │  Montevideo)               │
   └────────────────────────┘  │        ▼                 │  │  flow "Recibir mensajes":  │
                               │  ┌────────────────────┐  │  │  DEBOUNCE 20s → webhook n8n│
   ┌────────────────────────┐  │  │ Outreach Form Meta  │  │  └────────────┬─────────────┘
   │ Formulario Clientify    │  │  │ (CUuFxbst3iHpgeXS)  │  │               │ External Request
   │ (ZB6erhWicZmDfC4I)      │  │  │ TRI-TOQUE (0/24/72h) │  │               ▼
   │  → Airtable Leads        │  │  │ + memoria sintética  │  │  ┌──────────────────────────┐
   │  → Clientify (contacto)  │  │  └─────────┬──────────┘  │  │  wf-venttur-main            │
   └────────────────────────┘  └────────────│─────────────┘  │  (k3aivKSP67S97IHn) LIVE     │
                                            │ sendFlow WA      │  ┌───────────────────────┐  │
                                            ▼                  │  │ Responder rápido (ack)│  │
                              ┌──────────────────────┐         │  │ dedup (Tabla apoyo)   │  │
                              │      ManyChat WA      │◄────────┼──┤ atribución CTWA texto │  │
                              └──────────────────────┘  sendFlow│  │ alta lead Airtable    │  │
                                                                │  │ Whisper (audios)      │  │
   ┌──────────────────────────────────────────────────────────┼──│► Agente IA "Mauricio" │  │
   │                          MEMORIA                          │  │  (gpt-4o, temp 0)     │  │
   │  Supabase Postgres  n8n_chat_histories (34.725 filas)      │  │  + tools:             │  │
   │  session_id = teléfono sin '+' (quirk MX 52→521)          │◄─┤    crear_contacto      │  │
   │  contextWindowLength = 35 turnos                          │  │    elevar (a humano)   │  │
   └──────────────────────────────────────────────────────────┘  │  split parte1/2/3      │  │
                                                                │  └──────────┬────────────┘  │
   ┌──────────────────────┐  paralelo (fire-and-forget)          │             │ sendFlow      │
   │  Meta CAPI            │◄─────────────────────────────────────┼─────────────┘ "Enviar msj"  │
   │  (z98w2yWVEMOfifMl)   │                                       └───────────────────────────┘
   │  rama FOLIO / CTWA    │        ┌─────────────────────────── nurturing / estado ──────────┐
   │  → Graph API v21.0    │        │ wf-actualizar-link-enviado → wf-rescate-post-link (2 fases)│
   └──────────────────────┘        │ wf-confirmacion-agenda (GCal trigger) → flow "Agenda"      │
                                    │ wf-resumen-etiquetas-seguimientos (8h → LLM → drip x6)     │
   ┌──────────────────────┐        │ wf-seguimiento-agenda (48h recordatorio)                   │
   │  Clientify CRM        │◄───────┤ wf-estado-lead (Contestó) · wf-estado-interrumpida (24h)   │
   │  6.968 contactos      │        └───────────────────────────────────────────────────────────┘
   │  2.338 deals (manual) │        ┌──────────────────────┐
   └──────────────────────┘        │ wf-correo-semanal     │ (lunes 10h, lee Airtable Reporte    │
                                    │ (BrFfQyDfamdUzq64)    │  semanal → gpt-4.1-mini → Gmail)    │
   ┌──────────────────────┐        └──────────────────────┘
   │  Telegram (traza /     │  usado por rescate (chatId 6390727286), confirmación de agenda,
   │  errores / alertas)    │  y como notificación de fallo
   └──────────────────────┘
```

> ⚠️ INCIERTO — el diagrama refleja lo confirmado en los 14 JSON. No hay en `wf-venttur-main` ninguna llamada explícita al sub-workflow `wf-estado-lead` pese a que el proyecto lo describe como invocado por el main (impacto: la integración estado-lead↔main puede no estar deployada en este snapshot, o el main vivo difiere del JSON exportado).

---

## 3. Stack tecnológico (actualizado)

| Componente | Función | Instancia / ID / credencial |
|---|---|---|
| **n8n** | Orquestador central (14 workflows) | `[TU-INSTANCIA-N8N]` (detrás de proxy Caddy) |
| **ManyChat** | Canal WhatsApp + flows de envío/nurturing/elevación | Cuenta "Venttur \| Agente de IA", plan **Pro**, TZ `America/Montevideo`. 16 flows / 5 tags / 13 custom fields. Bearer `3256256:...` (hardcodeado en varios nodos) + Header Auth cred `9OZtsIsmuVEG9l6R` |
| **Airtable** | Data hub / CRM operativo (source of truth del lead) + config CAPI | Base `[AIRTABLE_BASE_ID]` "Venttur Dashboard", cred `[N8N_CREDENTIAL_ID]`. Tablas: Leads `[AIRTABLE_TABLE_ID]`, Folios CAPI `[AIRTABLE_TABLE_ID]`, Programas CAPI `[AIRTABLE_TABLE_ID]`, Mensajes anuncios `tbl2GmzS6irT0iUBF`, Reporte semanal `tblrXIUd7CGtiZEaS`, Tabla apoyo `tblLjOtFFTn9L2Zzz` (dedup) |
| **Clientify** | CRM comercial paralelo (contactos + tags + notas + deals manuales) | API v1 `api.clientify.net`, `Authorization: Token 3822fcd1...` (hardcodeado). 6.968 contactos / 2.338 deals / 266 companies / 22 custom fields |
| **Supabase (Postgres)** | Memoria conversacional del agente | Cred n8n `Venttur` (`ihpvM7nYMdLCwWDP`), tabla `n8n_chat_histories` (34.725 filas), `session_id` = teléfono sin `+` |
| **Meta Graph API** | Conversions API (eventos Lead server-side) | **v21.0**, endpoint `/{pixel_id}/events`. 2 pixels: Boarding `228398216567258`, AA Familiar `24520910174237152` |
| **OpenAI** | gpt-4o (agente), gpt-4o-mini (split de mensajes, resumen/clasificación), whisper-1 (transcripción), gpt-4.1-mini (correo semanal) | Cred `OpenAI \| Venttur` (`ibkhdCMyhr3yqDQk`) + un API key `sk-proj-...` hardcodeado en el nodo de transcripción |
| **Google Sheets** | Bridge de Meta Lead Ads → Outreach | Doc `1HzJVMBwnGikiI_U805N7oqcXPYE7TjEFTL1rqdcCEIU`, hoja `Boarding_Schools_Venttur_2026-test-2` (gid 160362675), cred `la agencia (@gmail)` |
| **Google Calendar** | Trigger de citas agendadas (3 asesores) | Calendars `dgarcia@` / `agarcia@` / `rgarcia@venttur.com`, cred OAuth `Google Calendar \| Rodrigo` (`6idhqxfKUyIkPGON`) |
| **Telegram** | Traza de ejecución / alertas de error | Bots `NA_errores_bot` (`xvFrENrzfJPgE6Ry`) y `botla agencia`, chatId `6390727286` |
| **Gmail** | Envío del correo semanal | Cred `Gmail \| la agencia®` (`5R0ScEVqcfjKYanp`) |

> **⚠️ Seguridad para el handoff/migración:** hay secretos hardcodeados en texto plano en los JSON — API key OpenAI (`sk-proj-...`) en la transcripción, Bearer ManyChat (`3256256:...`) repetido en múltiples nodos, y Token Clientify (`3822fcd1...`) en 4+ nodos. **Rotar y mover a credenciales/env ANTES de cualquier export o handoff.** (impacto: exposición de credenciales de producción).

---

## 4. Inventario de los 14 workflows n8n

| # | Workflow | id n8n | Trigger | Propósito | Estado (JSON) | Integraciones |
|---|---|---|---|---|---|---|
| 1 | **[Venttur] (main)** | `k3aivKSP67S97IHn` | Webhook ManyChat | Orquestador del agente Mauricio | **LIVE** (`active:true`) | ManyChat · OpenAI · Airtable · Supabase · Clientify (sub) · Meta CAPI (sub) · S3 |
| 2 | **Meta CAPI - Venttur** | `z98w2yWVEMOfifMl` | Execute Workflow | Evento Lead a Meta (rama folio / CTWA) | `active:false` (export); prod per CLAUDE.md | Airtable · Meta Graph API |
| 3 | **CAPI Registro Folio** | `9yCbynoKDt9hgiBq` | Webhook (landing) | Persiste la huella fbc/fbp/fbclid/ip por clic | **LIVE** (`active:true`) | Airtable |
| 4 | **Formulario Clientify** | `ZB6erhWicZmDfC4I` | Webhook (landing form) | Alta lead Airtable + contacto+tag Clientify | **LIVE** (`active:true`) | Airtable · Clientify |
| 5 | **Actualizar 'Link enviado'** | `gRSMjzxggA4UePjz` | Execute Workflow | Marca link enviado + tag + dispara rescate | sub (`active:false`) | Airtable · Clientify · n8n |
| 6 | **Confirmación de agenda** | `2PSekVBxarsrnVBu` | 3× Google Calendar trigger | Confirma cita por WA + marca `Agendan cita` | **LIVE** (`active:true`) | GCal · Clientify · Airtable · ManyChat · Telegram |
| 7 | **Crear contacto Clientify+Airtable** | `cZUNKQyZNOHy5twQ` | Execute Workflow | Sync lead↔CRM al "contestar 1er mensaje" | sub (`active:false`) | Airtable · Clientify |
| 8 | **Resumen, etiquetas, seguimientos** | `DyrDumQgb6S4zHsS` | Execute Workflow | Clasifica/cualifica lead (LLM) + dispara drip nurturing | sub (`active:false`) | Supabase · OpenAI · Airtable · Clientify · ManyChat |
| 9 | **Seguimiento agenda** | `DZlSEQS5qzX1Y01K` | Execute Workflow | Recordatorio único a 48 h si no agendó | sub (`active:false`, stub sin limpiar) | Airtable · ManyChat |
| 10 | **Rescate Post-Link** | `mkEP1qFN7MVb9qP0` | Execute Workflow | Rescate 2 fases (45 min + 24 h) + memoria sintética | `active:false` (export); prod per CLAUDE.md | Airtable · ManyChat · Supabase · Telegram |
| 11 | **Outreach Form Meta** | `CUuFxbst3iHpgeXS` | Google Sheets trigger + Cron | Tri-toque proactivo + memoria sintética | **LIVE** (`active:true`) | Google Sheets · Airtable · ManyChat · Supabase · webapp_errors |
| 12 | **Estado lead (Contestó)** | `b52CUYEkI2Ah3Xj6` | Execute Workflow | Estampa `Estado conversación=Contestó` + `Última actividad` | sub (`active:false`, pendiente deploy) | Airtable |
| 13 | **Estado interrumpida (barrido)** | `H6qYB3Oj97bxaTCX` | Schedule (cada 1 h) | Marca `Conversación interrumpida` a >24 h de silencio | **LIVE** (`active:true`) | Airtable |
| 14 | **Correo Semanal** | `BrFfQyDfamdUzq64` | Schedule (lunes 10h) | Reporte semanal del embudo por email | `active:false` (testing, dest. de prueba) | Airtable · OpenAI · Gmail |

> Todos comparten el `errorWorkflow` global `OBkUyb8fuo30DzA9` ("webapp_errors" / registro de errores central de la agencia, que escribe a un Supabase **compartido de la agencia**, no al de este cliente).

### 4.1 Resúmenes funcionales por workflow

**1. [Venttur] main (`k3aivKSP67S97IHn`) — LIVE.** El CORE conversacional. Topología: `Webhook → Responder rápido ManyChat` (ack 200 anti-timeout) → en paralelo `Meta CAPI` (fire-and-forget) y una cadena determinística: `Buscar registro`/`Repetido?` (dedup contra "Tabla apoyo" — si el texto es idéntico al último guardado, el flujo se DETIENE) → `Tomar todos los mensajes` + `Code` (atribución CTWA por matching flexible del texto contra "Mensajes anuncios" → `Fuente lead` + `Programa interés`) → `Buscar si ya existe` / `Crear primer contacto` (alta de lead idempotente por teléfono) → `Execute Workflow "Resumen…"` → `Separamos en partes` (extrae audios) → rama Whisper (`Get_Audio → Transcribir → Aggregate`) → `Agente IA WPP` (gpt-4o, temp 0, memoria Postgres key=teléfono, tools `crear_contacto` + `elevar`) → `Formatear mensaje WPP` (gpt-4o-mini parte la respuesta en `parte1/2/3`, quita `¿`/`¡` de apertura) → `Settear variables` (custom fields ManyChat) → `Enviar WPP` (sendFlow `content20250617172539_850988` = flow "Enviar mensajes") → `Envió link?` (si el output contiene `promo.venttur.com/` → dispara `Actualizar 'Link enviado'`). Ver §5.

**2. Meta CAPI (`z98w2yWVEMOfifMl`).** Sub-workflow de atribución. Router `contiene_folio` (¿el texto contiene "Folio"?): **rama FOLIO** (extrae `Folio` + `Prog` por regex, hashea PII con SHA-256 en JS puro, cruza Folios CAPI para recuperar fbc/fbp/ip/user_agent, cruza Programas CAPI por `{Programa}` dinámico, envía evento `Lead` `action_source:website`, `event_id=folio` para dedup contra el pixel del navegador, y escribe el `fbtrace_id` de vuelta en Folios CAPI) vs **rama CTWA** (sin folio: config de programa **hardcodeada a `{Programa}='BS'`**, `event_id=CTWA_<phone>_<ts>` sin dedup, `action_source:system_generated`, solo ph/fn/ln hasheados, marca el lead `Folio='N/A (WA)'`). Endpoint `graph.facebook.com/v21.0/{pixel_id}/events`. Ver §6.

**3. CAPI Registro Folio (`9yCbynoKDt9hgiBq`) — LIVE.** Webhook `capi-registro-folio-venttur` que la landing dispara en el clic-a-WhatsApp. 5 nodos: `Webhook → ¿Folio válido? (IF notEmpty) → Extraer y Enriquecer (Code) → Guardar Folio en Airtable (CREATE puro, sin dedup) → Responder OK`. El Code deriva `fbc = 'fb.1.'+timestamp+'.'+fbclid` (la landing NO manda fbc), parsea `fbclid` de `fbclid_completo` o de la URL, y extrae `ip` del header `x-forwarded-for`. Los `utm_*` de la URL NO se parsean a columnas (quedan embebidos en `Landing URL`). Ver §6.

**4. Formulario Clientify (`ZB6erhWicZmDfC4I`) — LIVE.** Webhook del form de landing. `Webhook → Edit Fields (normaliza nombre/apellido/telefono/etiqueta=programa) → Crear o actualizar contacto (Airtable upsert por Telefono, `Contestan 1er mensaje=false`) → Buscar Contacto Clientify (GET por phone) → [IF es vacío] crear/actualizar contacto Clientify → Actualizar ID Clientify (Airtable) → Etiquetar Contacto (tag = código de programa)`. Ignora email/pais/ciudad/folio/fbp del form (esos van por el pipeline CAPI). ⚠️ Este JSON en `00_inputs` es la versión **PRE-fix isExecuted** (la URL del tag apunta siempre a `Crear Contacto Clientify` → rompe con "Node hasn't been executed" cuando el lead ya existía). Ver §7.

**5. Actualizar 'Link enviado' (`gRSMjzxggA4UePjz`).** Sub-workflow disparado cuando el agente manda un link de asesoría. Clasifica el programa por substring del link en el texto (`LINK_MAP`: AAFamilia/SummerCamp/PW_Alemania/EstudiaryTrabajar/Australia/EMA), etiqueta el contacto Clientify `<programa>_link_enviado`, marca `Link asesoría enviado=true` en Leads (match por `id_2`=teléfono), y dispara `Rescate Post-Link` (fire-and-forget, solo el teléfono). Input `id_airtable` **contiene el teléfono** (nombre engañoso). 🐛 Bug: el tag referencia `.variable` (inexistente en el Code, que emite `.tag`) → probablemente escribe tag vacío. El nodo `Seguimiento agenda` alternativo está **DISABLED**.

**6. Confirmación de agenda (`2PSekVBxarsrnVBu`) — LIVE.** 3 Google Calendar triggers (`eventCreated`, polling 1 min) sobre `dgarcia@`/`agarcia@`/`rgarcia@venttur.com`. Filtra el evento por keywords en el título (`ASESORÍA`/`estudia`/`FAMILIA`/`SUMMER`/`Pathway Alemania`), extrae el nombre del lead del título (todo lo que sigue a `<>`), lo cruza Clientify (por nombre) → Airtable (por `ID Clientify`), marca `Agendan cita=true`, y envía la confirmación por WhatsApp (fecha/hora + link de Google Meet) vía flow ManyChat `content20250721163426_851504`. El mensaje con el **número directo de Rodrigo (+52 1 33 1944 2476)** vive dentro de ese flow ManyChat. ⚠️ Referencias rotas: los paths de Diego/Andres referencian `$('Obtener ID Manychat')` / `$('Obtener ID Manychat2')` que NO existen (solo existe `Obtener ID Manychat1`) → probablemente solo el path de Rodrigo funciona en prod. Ver §9.

**7. Crear contacto Clientify+Airtable (`cZUNKQyZNOHy5twQ`).** Sub-workflow: `trigger(id,nombre,apellido,telefono) → Airtable update Leads (Contestan 1er mensaje=true, blanquea Folio) → Clientify POST /contacts/ → Airtable update (ID Clientify)`. Match por Telefono. Es la tool `crear_contacto` del agente en su rol de "el lead contestó → materializar contacto". ⚠️ `operation:update` (NO upsert): requiere que el lead ya exista. `availableInMCP:false`. NO estampa `Estado conversación` (ese es el "EDIT B" pendiente). Ver §5.3 y §7.

**8. Resumen, etiquetas, seguimientos (`DyrDumQgb6S4zHsS`).** Sub-workflow invocado tras crear lead nuevo. `Wait 8h → lee memoria Postgres (n8n_chat_histories) → reconstruye conversación → gpt-4o-mini (5 salidas: tags[programa], tipo, resumen, asesoria[uno/cero], cualificado[1/0]) → 4 ramas paralelas: (a) Airtable Tipo; (b) tags→Clientify + Programa interés + programa_interes ManyChat + drip nurturing; (c) Cualificado=true; (d) nota "Resumen" en Clientify`. **GATE clave:** el drip de nurturing SOLO se dispara si `asesoria=='cero'` (el lead NO recibió link). Es el **dispatcher** del nurturing (dispara 1 flow ManyChat, no la cadencia de 4 toques que vive dentro de cada flow). Ver §8 y §10.

**9. Seguimiento agenda (`DZlSEQS5qzX1Y01K`).** Sub-workflow recordatorio single-touch: `trigger(telefono) → NoOp (placeholder sin limpiar) → Wait 48h → Airtable search por Telefono → IF (Agendan cita existe? → STOP) → sendFlow ManyChat content20250718124614_140983`. Copy: *"Hola [First Name] 👋 Hace unos días te compartí el enlace…"*. Sin idempotencia, sin escritura de estado. Es un mecanismo **paralelo y más simple** que el Rescate Post-Link. Token ManyChat hardcodeado.

**10. Rescate Post-Link (`mkEP1qFN7MVb9qP0`).** Sub-workflow 2 fases: `Wait 45min → Airtable 1er check → IF (ya agendó → STOP) → Code Fase 1 (routing por programa, 5 destinos) → IF (programa mapeado? no → tag RESCATE_PROGRAMA_NO_MAPEADO) → setCustomFields + sendFlow Fase 1 → Wait 24hrs → 2do check → IF (ya agendó → STOP) → Code Fase 2 → setCustomFields + sendFlow Fase 2 → tag LINK_ABANDONADO_FRIO`. En paralelo a cada envío inserta **memoria sintética** en Postgres (system prosa + ai del mensaje). ⚠️ El envío mapea 5 programas; la memoria mapea 6 (incluye 'Estudio y Trabajo' que nunca recibe rescate → código muerto). Ver §5.4.

**11. Outreach Form Meta (`CUuFxbst3iHpgeXS`) — LIVE.** Dos flujos en un workflow. FLUJO A (ingestión): `Sheets Trigger (rowAdded) → Normalize Payload → IF(_error?) → upsert Airtable por Folio (18 campos, 8 de cualificación)`. FLUJO B (cadencia): `Cron → Get Leads Pendientes (filterByFormula tri-toque anclado a Touch 1 programado at = creación) → Switch por Toques enviados → 3 ramas (createSubscriber+sendFlow Touch 1 / sendFlow Touch 2 / Touch 3) → Marcar Enviado (Toques+1) → memoria sintética`. Cadencia real **0h / +24h / +72h desde creación** (Touch 1 sin delay, linaje v4). Quirk MX 52→521 en el sessionKey de memoria. Ver §5.5.

**12. Estado lead (Contestó) (`b52CUYEkI2Ah3Xj6`).** Sub-workflow reactivo (por mensaje entrante): `trigger(telefono) → Airtable search → Code (guarda forward-only: terminal si Agendan cita=true O Estado='Cita confirmada'; si no → 'Contestó') → Airtable update (Estado conversación + Última actividad UTC)`. No-op si el lead no existe. Enum de estado: `Activa / Contestó / Cita confirmada / Conversación interrumpida`. Pendiente de deploy según docs. Ver §7.

**13. Estado interrumpida (barrido) (`H6qYB3Oj97bxaTCX`) — LIVE.** Barrido horario: `Schedule (cada 1h) → Airtable search (AND: Agendan cita≠TRUE, Estado≠Cita confirmada, Estado≠Conversación interrumpida, Última actividad<NOW-24h) → Airtable update (Estado='Conversación interrumpida', match por Telefono)`. Idempotente (el propio filtro excluye lo ya marcado). Umbral 24 h exactas.

**14. Correo Semanal (`BrFfQyDfamdUzq64`).** Reporte del embudo por email (**modo testing**, `active:false`, dest. `[EMAIL-AGENCIA]`, cuerpo con literal "CORRER FLUJO MANUAL"). `Schedule (lunes 10h) → Airtable search "Reporte semanal" (Created>TODAY-7) → Code (formatea fuentes desde rollup, %×100) → gpt-4.1-mini (conclusión 3 oraciones) → Gmail HTML branding propio`. **NO calcula las métricas** (las consume ya agregadas de la tabla). Ver §10.

---

## 5. Componente central: el agente "Mauricio"

Confirmado por el system prompt extraído (`agente-venttur-system-prompt-EXTRAIDO-2026-07-24.md`, 40.414 chars) y el nodo `Agente IA WPP` del main.

### 5.1 Rol e identidad

- **Nombre:** Mauricio, "asistente virtual estratégico de Venttur Education & Travel".
- **Rol:** NO vender, sino **asesorar con inteligencia emocional y táctica**; "consultor experto con mentalidad de diagnóstico y cierre consultivo, al estilo de Hormozi y Chris Voss".
- **Marcos aplicados:** Chris Voss (empatía táctica, etiquetado, preguntas calibradas — "que el otro se sienta entendido antes que convencido") + Alex Hormozi (diagnóstico profundo → prescripción con confianza).
- **Metodología propia EMA** (para internados): **E**valuation (entrevista + evaluación psicopedagógica) → **M**atch (software propio cruza >100 internados) → **A**chieve (trámites, visado, adaptación).
- **Diagnóstico de 7 pasos** para cualificar antes de recomendar programa (edad/escuela/idioma/motivación/presupuesto), con matriz de perfiles → programa sugerido.
- **Equipo experto** que menciona al cerrar: **Rodrigo** (cofundador, internados), **Andrés** (cofundador, Pathway Alemania / Gap Year / consultoría), **Diego** (hermano, estudia-y-trabaja Australia).

### 5.2 Modelo, memoria y ejecución (nodo `Agente IA WPP`)

- **Modelo:** gpt-4o, **temperature 0** (cred `OpenAI | Venttur`). El split de mensajes usa gpt-4o-mini.
- **User Message:** `Mensaje del usuario: {{ Mensaje completo }}` + `Fecha de hoy:` formateada en TZ `America/Mexico_City`.
- **Memoria:** `Postgres Chat Memory` (Supabase), `sessionKey = whatsapp_phone.replace('+','')`, **contextWindowLength = 35** turnos.
- **División de respuesta:** toda respuesta se parte en hasta 3 mensajes (`parte1/parte2/parte3`) cortando solo tras punto; se quitan `¿`/`¡` de apertura (se conservan `?`/`!` de cierre); prohibido markdown. Los flows ManyChat los envían secuenciados con cadencia humana.
- **Debounce:** el flow ManyChat "Recibir mensajes" espera **20 segundos** (buffer anti-fragmentación) antes de llamar al webhook n8n, para agrupar mensajes cortos consecutivos del lead en un solo `respuesta_definitiva`.

### 5.3 Tools del agente

| Tool | Tipo | Apunta a | Cuándo se activa (prompt) |
|---|---|---|---|
| `crear_contacto` | toolWorkflow | sub-workflow `cZUNKQyZNOHy5twQ` ("Crear contacto Clientify y Airtable") | Cuando el usuario da **nombre + apellido de quien escribe** (nunca del hijo/a). Inputs `nombre`/`apellido` por `$fromAI` + `id`/`telefono` determinísticos |
| `elevar` | toolHttpRequest (NO sub-workflow) | POST ManyChat sendFlow `content20250716130059_365663` (flow "Elevar") | Cuando el usuario pide humano/emergencia, o envía el MISMO mensaje 2+ veces **consecutivas e inmediatas** |
| `primer_registro` | toolWorkflow | sub-workflow `gyMROURqhLlYtJJU` | **DISABLED** — reemplazado por el nodo determinístico `Crear primer contacto` del main |

> ⚠️ INCIERTO — **`contestan_2do`:** el system prompt instruye explícitamente *"Si el usuario responde a tu segundo mensaje… activa la herramienta `contestan_2do`"*, pero **no existe ningún nodo/tool con ese nombre cableado en el main**. El agente tiene instrucción de invocar una tool inexistente (impacto: la métrica "contestan 2do mensaje" no se está capturando; decidir en GHL si se implementa o descarta). Nótese que Airtable Leads sí tiene el campo `Contestan 1er mensaje` (que sí escriben los flujos de contacto), no un "2do".

### 5.4 Matriz de links de asesoría (del prompt, §"Enlaces de asesoría")

| Interés del lead | Link | Experto |
|---|---|---|
| Internados / Boarding School | `promo.venttur.com/agendar-ema` | Rodrigo |
| Año Académico con familia (público) | `promo.venttur.com/AAFamilia-Agendar` | Rodrigo |
| Summer Camp | `promo.venttur.com/SummerCamp-Agendar` | Rodrigo |
| Pathway universitario Alemania | `promo.venttur.com/PW_Alemania_Agendar` | Andrés |
| Gap Year / Estudiar y trabajar | `promo.venttur.com/Estudiar-y-Trabajar-en-Australia` | Diego |
| Programa "estudiar y trabajar" (cursos idiomas) | `promo.venttur.com/EstudiaryTrabajar_Agendar` | Andrés |
| GAP Year Australia | `promo.venttur.com/Estudiar-y-Trabajar-en-Australia` | Diego |
| Duda / fallback | `promo.venttur.com/agendar-ema` | — |

> ⚠️ INCIERTO — hay **ambigüedad entre "Gap Year / Estudiar y trabajar" y "estudiar y trabajar (cursos)"**: dos entradas del prompt con links y expertos distintos (Diego→Australia vs Andrés→EstudiaryTrabajar_Agendar) que se solapan conceptualmente (impacto: al mapear programas en GHL hay que resolver con el cliente si son 1 o 2 programas y qué experto/pixel corresponde a cada uno; el Rescate/Resumen usan taxonomías levemente distintas — ver §8).

### 5.5 Reglas conversacionales clave (del prompt)

- SIEMPRE pedir nombre + apellido **de quien escribe** (no del hijo/a) antes de `crear_contacto`.
- No recomendar programa sin diagnóstico completo; priorizar internados para <17 que buscan estructura.
- Nunca dar cifra de precio suelta sin contexto/perfil ("sería irresponsable darte un número suelto").
- Enviar el link **sin markdown ni paréntesis** (ejemplos correcto/incorrecto explícitos en el prompt).
- No repetir el link de asesoría en el mismo bloque; no insistir si el usuario no respondió al primer ofrecimiento.
- Página web: enviar `venttur.com` + Instagram `@venttur_`, recalcando que la mejor info está en la asesoría.
- **Elevación por repetición:** elevar si el mismo texto llega 2+ veces consecutivas e inmediatas; NO elevar si el mismo texto reaparece NO-consecutivo (retoma días después).

---

## 6. Tracking de atribución (Meta CAPI) — detalle

*(Preservado y ampliado del doc de mayo; el hashing SHA-256 y las reglas de folio siguen vigentes.)*

### 6.1 CAPI Registro Folio (`9yCbynoKDt9hgiBq`) — la "huella" del clic

La landing `go.venttur.com` dispara un POST al webhook `capi-registro-folio-venttur` en el momento del clic-a-WhatsApp (`origen: "clic_whatsapp_directo"`). El Code node enriquece: `fbclid` (de `fbclid_completo` o regex de la URL), `fbc` **derivado** `fb.1.<timestamp_ms>.<fbclid>` (subdomainIndex fijo en 1), `fbp` tal cual, `ip` del header `x-forwarded-for`. Escritura CREATE **sin dedup** en Folios CAPI. La columna `fbtrace_id` existe en el schema pero la llena el otro workflow.

### 6.2 Meta CAPI (`z98w2yWVEMOfifMl`) — el envío del evento

Discriminante: `¿el texto contiene "Folio"?`.

| Aspecto | Rama FOLIO | Rama CTWA |
|---|---|---|
| Trigger | msg contiene "Folio: X \| … Prog: Y)" | no contiene "Folio" |
| event_id | `<folio>` (dedup real vs pixel navegador) | `CTWA_<phone>_<ts>` (sin dedup) |
| action_source | `website` | `system_generated` |
| Config programa | dinámica `{Programa}=<extraído>` | **fija `{Programa}='BS'`** (hardcode) |
| Señales de match | ph+fn+ln+fbc+fbp+ip+user_agent | solo ph+fn+ln |
| Lead update Airtable | `id_2` + Folio + fbclid | `ID Manychat` + `Folio='N/A (WA)'` + `fbclid='-'` |
| Writeback fbtrace_id | sí (Folios CAPI) | no |

Endpoint: `POST graph.facebook.com/v21.0/{pixel_id}/events`, `access_token` en el body, `event_name: "Lead"`. SHA-256 implementado en JS puro (sin `crypto`) por el sandbox de n8n.

> ⚠️ INCIERTO — la rama CTWA **hardcodea `{Programa}='BS'`** y NO lee ningún `programa_wpp` dinámico (contradice la asunción de mayo). Impacto: todo lead CTWA se atribuye al pixel Boarding, sin importar el programa real; resolver antes de migrar si CTWA debe mapearse por campaña/programa.

---

## 7. CRM / captura de leads — detalle

Dos workflows escriben leads:

- **Formulario Clientify (`ZB6erhWicZmDfC4I`, LIVE):** captura del form de landing. Upsert Airtable por Telefono + alta/actualización Clientify (dedup por phone) + tag = código de programa crudo del form (ej. `BSG`). El teléfono se guarda **sin `+` en Airtable y con `+` en Clientify** (doble representación). El external id de contactos nuevos en Clientify es compuesto `programa_telefono` (ej. `BSG_524424754070`). No persiste `Programa interés` en Airtable (solo como tag Clientify). ⚠️ Este input está PRE-fix isExecuted.
- **Crear contacto Clientify+Airtable (`cZUNKQyZNOHy5twQ`, sub):** tool `crear_contacto` del agente. `update` (no upsert) por Telefono, marca `Contestan 1er mensaje=true`, blanquea `Folio`, sincroniza a Clientify y guarda `ID Clientify`. ⚠️ `availableInMCP:false` y el blanqueo de Folio no está documentado (posible artefacto).

El **estado del lead** lo mantienen: `wf-estado-lead` (Contestó, forward-only anti-downgrade) y `wf-estado-interrumpida` (Conversación interrumpida a >24 h). Enum `Estado conversación`: `Activa / Contestó / Cita confirmada / Conversación interrumpida`. La "cita confirmada/agendada" se detecta por el **checkbox `Agendan cita`** O el select `Estado='Cita confirmada'` (no existe un valor "Cita agendada" en el enum).

---

## 8. Nurturing y seguimiento — detalle

### 8.1 Dispatcher (`DyrDumQgb6S4zHsS`)

8 h post-conversación, gpt-4o-mini clasifica el historial en `tags[programa]` (lista cerrada: Boarding IA / AA Familiar IA / Summer Camp IA / Pathway IA / Gap Year IA), `tipo` (Padre/Madre \| Estudiante), `resumen`, `asesoria` (uno/cero), `cualificado` (1/0: idioma 2/3 + escuela privada bilingüe + rango de edad por programa). Con eso: escribe Tipo/Programa interés/Cualificado en Airtable, tags + nota en Clientify, y **dispara UN drip de nurturing** — pero SOLO si `asesoria=='cero'` (gate anti-doble-contacto). El Switch prioriza Pathway > Summer > AA Familiar > Boarding > Gap Year (orden probablemente no intencional). Fallback "Lead General" si no hay programa.

> 🔴 **EL GATE `asesoria=='cero'` ESTÁ ROTO POR CONSTRUCCIÓN — causa del 64% del Hallazgo 2 del
> Reporte la agencia 1.** El prompt de la Tarea 4 le da al LLM la lista cerrada de *"los únicos links para
> agendar asesorías"* y esa lista **no incluye `promo.venttur.com/agendar-ema`**, que es el link de
> Internados/Boarding School y el fallback ante duda del system prompt. Además repite
> `SPEagendar` y `Estudiar-y-Trabajar-en-Australia` dos veces cada uno, y `SPEagendar` **no existe**
> en la matriz de links del agente. Como la instrucción siguiente dice *"Cualquier otro link… debes
> devolver el valor 'cero'"*, **todo lead que recibió `agendar-ema` queda clasificado como "nunca
> recibió link" y entra al drip genérico**. No es un LLM que a veces se equivoca: es determinístico.
> Cierra el círculo con el Hallazgo 3 — las plantillas que fallan son `seg_dia_*_`**`bs`**
> (**b**oarding **s**chool), exactamente esa cohorte.
>
> **Segundo problema del mismo dispatcher:** los nodos `Interés` y `Set programa_interes`
> **sobrescriben** `Programa interés` con la etiqueta del LLM en cada corrida, sin ninguna guarda. Es
> el mecanismo del Hallazgo 5 (conversación cerrada reclasificada a "Boarding IA" y drip de 5 días) y
> la fuente de la doble grafía `Boarding School` (482 leads, lo escribe el outreach) vs
> `Boarding IA` (437, lo escribe el LLM).
>
> **Decisión tomada (2026-08-17):** la cadencia se muda a n8n (`vtr-despachador-proactivo-v1.json`),
> con tope global de 2 toques y gate por el campo real `Link asesoría enviado` de Airtable en vez de
> la inferencia del LLM. ManyChat queda como capa de envío.

### 8.2 Cadencia de nurturing (6 flows ManyChat, folder "Seguimientos")

La cadencia de 4 toques vive hoy **dentro de cada flow ManyChat**, no en n8n — **y eso cambia**: se
migra a un despachador único en n8n (ver §8.1). Estos flows quedan como capa de envío.
Estado actual: Estructura idéntica: `mensaje 1 (día 0) → Wait 1 día → mensaje 2 → Wait 2 días → mensaje 3 → Wait 2 días → mensaje 4` = delays **0 / 1 / 3 / 5 días**. Contenido educativo/nurturing de largo plazo (los 24 textos completos en `manychat-flows-content-2026-07-20.md`):

| Flow ManyChat | flow_ns | Ángulo |
|---|---|---|
| Boarding School | `content20250718115245_638127` | 3 errores al elegir escuela, "¿cómo es tu hijo?", checklist de listo |
| Año Académico (AA Familiar) | `content20250718123255_243860` | "no es el país, es tu casa" (familia anfitriona), países |
| Gap Year | `content20250718122822_491460` | "no es escapista", países que permiten estudiar+trabajar |
| Pathway | `content20250718121921_967738` | estudiar en Alemania sin colegiatura, checklist Pathway 2 años |
| Summer Camp | `content20250718123847_652764` | "¿campamento o vacaciones?", países |
| Lead General | `content20250718124216_992343` | fallback: rutas comunes, orientación (última pausa 3 días) |

### 8.3 Otros seguimientos

- **Confirmación de agenda** → flow "Agenda" (número directo de Rodrigo +52 1 33 1944 2476).
- **Seguimiento agenda** (48 h, single-touch) → flow con copy "Hace unos días te compartí el enlace…" + tag `seguimiento_agenda`.
- **Rescate Post-Link** (45 min + 24 h) → mensajes de rescate por programa + tags `RESCATE_PROGRAMA_NO_MAPEADO` / `LINK_ABANDONADO_FRIO`.

> ⚠️ INCIERTO — hay **≥3 taxonomías de programa parcialmente inconsistentes**: (a) el enum Airtable `Programa interés` (8 valores, incluye "Francia IA", "Automatización - Comentarios"); (b) las 5 tags del clasificador LLM; (c) el routing del Rescate (5 en envío / 6 en memoria, "Estudio y Trabajo" nunca recibe rescate). Impacto: al modelar pipelines/programas en GHL hay que unificar en una tabla única programa→(pixel, link, experto, mensajes, tag).

---

## 9. Confirmación de citas — detalle

`wf-confirmacion-agenda` reacciona a `eventCreated` en 3 Google Calendars (asesores Diego/Andres/Rodrigo). Cruce de identidad frágil de 3 sistemas: título del evento (parse por `<>`) → Clientify (búsqueda por nombre) → Airtable (`ID Clientify`). Marca `Agendan cita=true` y **debería** enviar confirmación WA con fecha/hora + link Google Meet.

> 🔴 **EN LA PRÁCTICA NO ENVÍA NADA.** El Reporte la agencia 1 (agosto 2026) midió **0 confirmaciones sobre
> 11 leads que sí agendaron**, y la verificación en el n8n vivo (ejecución `1362988`, 2026-08-17) lo
> confirma: la cadena llega hasta `Settear variables` y muere con `Referenced node doesn't exist` —
> 2 de los 3 paths de asesor referencian nodos que no existen (ver `06_redundancias` §E.5).
> **Peor:** `Agendan cita = true` se escribe **antes** del envío, así que el lead queda marcado como
> agendado, sin confirmación, y **excluido de todo seguimiento posterior**.

Leads NUEVOS (no pre-existentes en Airtable) tampoco reciben confirmación automática: la rama
`Crear contacto` termina en el nodo `error` y nunca se conecta al `Switch` de envío.

> ⚠️ INCIERTO — el flow ManyChat que dispara la confirmación (`content20250721163426_851504`) aparece en el snapshot ManyChat con el **nombre "Seguimiento agenda"**, mientras que el flow `content20250718124614_140983` (que dispara el workflow "Seguimiento agenda") aparece como **"Agenda"** → los nombres visibles en ManyChat parecen **cruzados** respecto de lo que cada workflow n8n dispara. Los `flow_ns` (source of truth de qué se ejecuta) son los correctos; los nombres humanos pueden haberse renombrado. Impacto: no confiar en los nombres de flow al migrar; usar los `flow_ns`.

---

## 10. Modelo de datos completo: cómo se cruzan Airtable ↔ Clientify ↔ ManyChat ↔ Supabase

Esta es la sección crítica para la migración de datos a **GHL Contacts** (FOCO 6).

### 10.1 Airtable — la fuente de verdad operativa

Base `[AIRTABLE_BASE_ID]` "Venttur Dashboard".

**Tabla Leads (`[AIRTABLE_TABLE_ID]`) — 30 columnas, 3.819 filas.** Es el registro maestro del lead.

| Columna | Rol | Notas |
|---|---|---|
| `id` | **PK** = teléfono sin `+` | clave natural; usada por casi todos los `filterByFormula` |
| `id_2` | teléfono (redundante) | usado como matchingColumn en varios updates |
| `Telefono` | teléfono sin `+` | matchingColumn de estado/rescate/seguimiento |
| `Nombre` / `Apellido` / `Nombre Completo` | identidad | |
| `Email` | contacto | poblado por form, no por el main |
| **`ID Clientify`** | **FK → Clientify contact.id (1:1)** | escrito por form + crear_contacto |
| **`ID Manychat`** | **FK → ManyChat subscriber_id** | escrito por el main al crear lead |
| **`Folio`** | **FK → Folios CAPI.Folio** | extraído del texto o `N/A (WA)` / `N/A (Form)` |
| `fbclid` | atribución | copiado de Folios CAPI |
| `Fuente lead` | campaña/anuncio | ~22 valores (ad-set names) |
| `Programa interés` | single-select | 8 en el schema capturado (Boarding IA / AA Familiar IA / Gap Year IA / Pathway IA / Summer Camp IA / Francia IA / Automatización - Comentarios / No definido) **+ `Boarding School`** — 9º valor que escribe el Outreach Form Meta (⚠️ doble grafía Boarding, ver doc 03 §5.2 y doc 06). Distribución real: No definido 1315 · Pathway IA 881 · AA Familiar IA 632 · Boarding School 482 · Boarding IA 437 · Summer Camp IA 42 · Gap Year IA 25 · Automatización - Comentarios 5 |
| `Estado conversación` | single-select | Activa / Contestó / Cita confirmada / Conversación interrumpida |
| `Última actividad` | dateTime (UTC) | estampada por wf-estado-lead |
| `Agendan cita` / `Asistió` / `Link asesoría enviado` | checkboxes | señales de embudo |
| `Contestan 1er mensaje` | checkbox | seteado por form (false) / crear_contacto (true) |
| `Origen` | Form Meta / Form Landing / CTWA … | fuente del lead — ⚠️ en `leads.csv` solo se observa `Form Meta` (483) o vacío; `Form Landing`/`CTWA` los mapea el builder de memoria sintética pero no aparecen como valores en datos reales |
| `Toques enviados` / `Ultimo toque at` / `Outreach Form Meta enviado` / `Outreach Form Meta enviado at` / `Touch 1 programado at` | estado de outreach | state-machine del tri-toque |
| `Ad Name` / `Platform` | cualificación Meta | del form |
| `Grado Escolar` / `Inicio Deseado` / `Nivel Inglés` / `Tipo` | cualificación | 8 campos-oro del form Meta |
| `Lead Score` / `Tipo lead` (hot/warm/cold) | scoring | del outreach (real: cold 3510 / warm 181 / hot 128) |
| `Creada` | timestamp | |

**Folios CAPI (`[AIRTABLE_TABLE_ID]`) — 4.003 filas** (con folios duplicados: el registro no deduplica). Store de identidad de navegador por clic: `Folio, fbclid, Programa, Timestamp, Landing URL, fbc, fbp, user_agent, ip, fbtrace_id`. FK: `Folio` ← Leads.Folio.

**Programas CAPI (`[AIRTABLE_TABLE_ID]`) — 4 filas / 4 códigos, 2 pixels.**

| Nombre del programa | Programa (código) | pixel_id | default_url |
|---|---|---|---|
| Boarding IA | BS | `228398216567258` | go.venttur.com/bs |
| Boarding IA | BSG | `228398216567258` | go.venttur.com/bs/girls |
| Boarding IA | BSC | `228398216567258` | go.venttur.com/bs/cats |
| AA Familiar IA | HF | `24520910174237152` | go.venttur.com/hf |

> ⚠️ INCIERTO — solo existen filas para BS/BSG/BSC (Boarding) y HF (AA Familiar). **Los demás programas conceptuales del agente (Summer Camp, Pathway, Gap Year / Estudia y Trabajo) NO tienen fila en Programas CAPI** → su tracking CAPI es incierto (probablemente sin pixel configurado, o caen en la rama CTWA hardcodeada a 'BS'). Impacto: no asumir que existen pixels para esos programas al migrar la atribución.

**Mensajes anuncios (`tbl2GmzS6irT0iUBF`) — 25 filas.** Mapea `Anuncio` (nombre del ad Meta) → `Mensaje` (copy de apertura CTWA) → `Interes` (programa). El main lo usa para atribución CTWA por matching flexible del primer mensaje.

**Reporte semanal (`tblrXIUd7CGtiZEaS`) — 36 filas.** Agregado ya calculado por semana: `Semana, Created, Leads, Cantidad total de leads, Cualificados, Cualificados (%), Citas agendadas, Tasa de conversión a cita, Asisten a cita, Tasa de asistencia a cita, Conversaciones no continuadas, Fuente lead Rollup (from Leads)`. Lo consume `wf-correo-semanal` (que NO calcula, solo presenta).

**Tabla apoyo (`tblLjOtFFTn9L2Zzz`) — 2.114 filas.** Ledger de dedup del main (`ID`, `Ultimo mensaje`). El cliente indicó que es descartable.

### 10.2 Clientify — CRM comercial paralelo

Volumen real: **6.968 contactos · 2.338 deals · 266 companies · 22 custom fields.**

- **Uso en producción (n8n):** SOLO contactos + tags + notas. Endpoints: `POST /contacts/`, `GET /contacts/?phone=X`, `POST /contacts/{id}/tags/`, `POST /contacts/{id}/note/`.
- **Pipeline de ventas (deals) — gestión manual del equipo Venttur, NO tocada por ningún workflow:**
  - Por campaña: "Campaña Internados Erika" (1.024), "VENTAS EMA METODOLOGÍA" (319), "Campaña Australia Abril 25" (291), "Venta SPE - Internados" (172), etc.
  - Por status: Expired 1.875, Lost 381, Open 50, Won 32.
  - Stages: "AGENDÓ REUNIÓN", "Cita de Ventas concretada", "Día 15/20 Seguimiento", "Gracias por asistir", etc.
- **Veredicto de migración:** sigue siendo **REMOVE** (Clientify → GHL CRM). Los deals/companies/custom-fields son gestión comercial manual: en GHL se modelan como Opportunities/Pipelines; los contactos + tags + notas migran a GHL Contacts. Panorama completo confirmado (ya no "a verificar").

### 10.3 ManyChat — canal

subscriber_id ↔ Airtable `ID Manychat`. 13 custom fields relevantes: `respuesta_definitiva` (texto del lead que entra al agente), `parte1/parte2/parte3` (respuesta partida saliente), `mensaje_inicial_asesoria` / `mensaje_link_asesoria` (confirmación de cita), `programa_interes` / `programa_wpp` / `programa_rescate`, `agendan_cita` (bool), `ctwa_clid` / `ad_source_id` (atribución CTWA nativa), `wpp`. 5 tags: `RESCATE_PROGRAMA_NO_MAPEADO`, `LINK_ABANDONADO_FRIO`, `seguimiento_agenda`, `wpp`, `seguimiento`.

### 10.4 Supabase — memoria

Tabla única `n8n_chat_histories` (34.725 filas): `id, session_id, message (jsonb {type:human|ai|system}), created_at`. **`session_id` = teléfono sin `+`**, con el **quirk MX**: los celulares mexicanos llegan como `52XXXXXXXXXX` (12 díg) pero el sistema espera `521XXXXXXXXXX` (13 díg, con el `1` de celular). Fix + backfill ya aplicados en producción. Los mensajes `type:system` son la **memoria sintética** que siembran outreach y rescate (para que el agente no re-salude). Tablas `documents` (0 filas, vestigio RAG) y `n8n_chat_histories_plus_backup` (2 filas) son irrelevantes. `workflow_errors` NO existe acá (va al Supabase central de la agencia).

### 10.5 Diagrama de relaciones cross-plataforma

```
                         ┌──────────────────────────────┐
                         │  AIRTABLE Leads (source of     │
                         │  truth operativo, 3.819)       │
                         │  PK: id = teléfono sin '+'      │
                         └──┬──────────┬──────────┬───────┘
        FK: ID Clientify    │          │          │   FK: Folio
        (1:1)               │          │          │
                            ▼          │          ▼
              ┌──────────────────┐     │   ┌──────────────────┐
              │ CLIENTIFY contact│     │   │ AIRTABLE Folios   │
              │ id (6.968)        │     │   │ CAPI (4.003)      │
              │  + deals (manual) │     │   │  fbc/fbp/ip/ua    │
              └──────────────────┘     │   └────────┬─────────┘
                                       │            │ Programa
        FK: ID Manychat                │            ▼
        (subscriber_id)                │   ┌──────────────────┐
                            ▼          │   │ AIRTABLE Programas│
              ┌──────────────────┐     │   │ CAPI (4 → 2 pixel)│
              │ MANYCHAT          │     │   └──────────────────┘
              │ subscriber        │     │
              │ + 13 cfields/5 tag│     │  session_id = teléfono
              └──────────────────┘     │  (sin '+', quirk MX 52→521)
                                       ▼
                             ┌──────────────────────┐
                             │ SUPABASE               │
                             │ n8n_chat_histories     │
                             │ (34.725 · memoria)      │
                             └──────────────────────┘
```

**Source-of-truth por dominio:**
- **Identidad + estado operativo del lead:** Airtable Leads (se congela read-only al migrar; → GHL Contacts).
- **Memoria conversacional:** Supabase `n8n_chat_histories` (→ GHL Conversations nativo, o se mantiene si el agente sigue en n8n).
- **Canal/subscriber:** ManyChat (→ GHL WhatsApp).
- **Atribución de navegador:** Airtable Folios/Programas CAPI (se mantiene en Airtable; el plan de migración conserva n8n para el CAPI).
- **Pipeline comercial:** Clientify deals (gestión manual → GHL Opportunities).

> **Clave de reconciliación al migrar a GHL:** cada lead se une por `Airtable.id (=teléfono) = Telefono = Supabase.session_id` (con normalización MX 521), `Airtable.ID Clientify → contacto Clientify`, `Airtable.ID Manychat → subscriber ManyChat`, `Airtable.Folio → Folios CAPI`. **Normalizar todos los teléfonos a E.164 canónico (resolviendo el 521 vs 52) es prerequisito** para que GHL no duplique contactos.

---

## Marcadores de incertidumbre

| Ítem | Qué falta confirmar | Impacto | Owner / cómo resolver |
|---|---|---|---|
| Tool `contestan_2do` | El prompt la invoca pero no existe nodo/tool cableado en el main | La métrica "contestó 2do mensaje" no se captura; instrucción muerta | Confirmar en n8n vivo; decidir si se implementa o descarta en GHL |
| `wf-estado-lead` no invocado desde el main | El JSON del main no llama a `b52CUYEkI2Ah3Xj6` pese a que docs dicen que sí | El estampado "Contestó" puede no estar deployado | Auditar el main vivo vs el export |
| Rama CTWA hardcodeada a `{Programa}='BS'` | Si es intencional (1 pixel CTWA) o placeholder/bug | Todo lead CTWA se atribuye a Boarding | Confirmar con cliente el mapeo CTWA→pixel por programa |
| Pixels de Summer/Pathway/Gap Year | Programas CAPI solo tiene BS/BSG/BSC/HF | Esos programas quizá no tienen tracking CAPI | Confirmar con Meta/cliente qué pixels existen |
| Ambigüedad Gap Year vs "estudiar y trabajar" | 2 entradas del prompt con links/expertos distintos que se solapan | Mapeo de programas en GHL ambiguo | Confirmar taxonomía real de programas con el cliente |
| Nombres de flow "Agenda" ↔ "Seguimiento agenda" cruzados | El snapshot ManyChat nombra los flow_ns al revés de lo que dispara cada workflow | Confiar en el nombre lleva a error | Usar los `flow_ns`, no los nombres, al migrar |
| Flow "Elevar" — "Notify Assignees: 0 people" | Si el equipo humano se entera de las elevaciones | Escalamientos podrían perderse silenciosamente | Revisar el flow en ManyChat con Max/Mauricio |
| `Formulario Clientify` PRE-fix isExecuted | El input de migración no tiene el fix del 2026-06-06 | El tag rompe cuando el lead ya existía en Clientify | Usar `03_workflows/formulario-clientify-venttur-v1.json` (versión viva) |
| Bug tag `.variable` en Actualizar Link enviado | El body referencia `.variable` (inexistente; el Code emite `.tag`) | Clientify recibiría tag vacío | Verificar en Clientify; corregir a `.tag` al migrar |
| Referencias rotas en Confirmación de agenda | `$('Obtener ID Manychat')`/`2` no existen (solo `...1`) | Solo el path de Rodrigo funcionaría en prod | Confirmar en n8n vivo si los paths Diego/Andres están rotos |
| `contestan_2do` vs `Contestan 1er mensaje` | El schema tiene "1er mensaje" (no "2do") | Confusión de nombres al mapear campos | Aclarar semántica con el equipo |
| Blanqueo de `Folio` en `crear_contacto` | Por qué se setea Folio='' al materializar contacto | Podría perder tracking; posible artefacto | Preguntar al autor / no replicar sin confirmar |
| "Estudio y Trabajo" = código muerto en Rescate | Routing envía 5 programas, memoria mapea 6 | Ese lead nunca recibe rescate | Unificar tabla de programas en GHL |
| Cron "cada 5 min" del Outreach | El param `interval:[{field:minutes}]` sin `minutesInterval` corre cada 1 min | Cadencia real vs nombre difieren | Confirmar en n8n vivo |
| Correo semanal en modo testing | `active:false`, dest. de prueba, "CORRER FLUJO MANUAL" | Puede que nunca haya operado en prod | Validar con cliente si lo quieren en GHL |
| Secretos hardcodeados | OpenAI/ManyChat/Clientify tokens en texto plano | Exposición de credenciales | Rotar y mover a env ANTES del handoff |
| Meta CAPI `active:false` en export | El JSON exportado está inactivo; CLAUDE.md dice prod | Estado real del CAPI incierto | Confirmar en n8n vivo |
| Normalización de teléfono | El main hace `replace('+','')` sin resolver 521 vs 52 | Riesgo de doble identidad de sesión | Definir E.164 canónico AL migrar |
