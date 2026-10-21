# 06 — Redundancias y Ambigüedades

> **Reescrito 2026-07-24** con los inputs completos de Etapa 0 (14 workflows n8n + snapshot de datos de las 5 plataformas + 6 CSVs Airtable + system prompt del agente + schema Supabase). Supera la versión de mayo 2026, que se generó con inputs parciales y contenía errores materiales (ver "Correcciones vs. versión mayo 2026" más abajo).
>
> **Fuentes:** los 14 JSON `wf-*.json` de `00_inputs/` (análisis nodo-por-nodo) · `agente-venttur-system-prompt-EXTRAIDO-2026-07-24.md` (prompt del agente "Mauricio", ~39K chars) · `manychat-flows-content-2026-07-20.md` (contenido interno de flows: nurturing, agenda, elevar, debounce) · `vtr-data-snapshot-2026-07-24.json` (Clientify + ManyChat vigente) · `manychat-snapshot-2026-05-13.md` (histórico) · `supabase-queries-venttur.md` (schema + quirk MX) · `airtable-csvs/{leads,folios-capi,programas-capi,mensajes-anuncios,reporte-semanal}.csv` · `template-texts-canonical.md` · `README.md` · `ESTADO_MIGRACION.md`.
>
> **Propósito del doc:** listar issues, pendientes, redundancias y ambigüedades que hay que resolver antes de diseñar la arquitectura GHL (Etapa 3). Cada ítem lleva una **propuesta** (KEEP / REMOVE / MODIFY / CONFIRM / DECIDE) y una **pregunta de validación** para llevar al cliente en Etapa 2.

---

### Correcciones vs. versión mayo 2026

La versión de mayo de ESTE doc contenía varios errores materiales y una foto desactualizada del estado del sistema. Correcciones concretas:

1. **"No hay agente conversacional IA / sistema puramente reactivo" → FALSO.** El corazón del sistema es un AI Agent conversacional llamado **"Mauricio"** (gpt-4o, temp 0), inline en el nodo `Agente IA WPP` del main. Todo el doc de mayo que trataba al sistema como "tracking + CRM + rescate sin cerebro" está corregido: hay diagnóstico consultivo de 7 pasos, memoria Postgres (35 turnos), y tools (`crear_contacto`, `elevar`).
2. **Rescate Post-Link "diseñado, no activado / vive en ManyChat" → FALSO.** Está **EN PRODUCCIÓN** como workflow n8n `mkEP1qFN7MVb9qP0`, 2 fases (45 min + 24 h), con memoria sintética. El B.1 de mayo ("¿activar en ManyChat o GHL?") queda OBSOLETO.
3. **Outreach proactivo WA "NO implementado / bloqueado por opt-in" → FALSO.** Está **EN PRODUCCIÓN** (`CUuFxbst3iHpgeXS`), tri-toque (0h/+24h/+72h desde creación), disparado por Google Sheets Trigger de Meta Lead Ads. El B.2 de mayo queda OBSOLETO. El opt-in ya se resuelve vía `consent_phrase` del form Meta.
4. **"Rama CTWA no visible en el JSON / workflow no exportado" → RESUELTO.** El export completo de `Meta CAPI - Venttur` muestra la rama CTWA cableada (`Buscar Config Programa2 → Folio (N/A) → Preparar CAPI Data2 → HTTP Request Meta CAPI2`). El A.3 y A.4 de mayo quedan cerrados. **Corrección adicional:** la rama CTWA **hardcodea `{Programa}='BS'`**, NO rutea por `programa_wpp` como asumía mayo (ese campo no aparece en el workflow).
5. **Clientify "6.968 contactos, volumen desconocido" → CONFIRMADO con panorama completo:** 6.968 contactos + 2.338 deals + 266 companies + 22 custom fields. El pipeline de deals (gestión comercial manual) es nuevo respecto de mayo y abre una decisión de migración grande (ver §B).
6. **Normalización de teléfono:** mayo trataba el bug del "solo primer `+`" como latente/menor. La realidad tiene DOS problemas distintos: (a) el `+` simple, y (b) el **quirk MX 52→521** (12 vs 13 dígitos), que sí rompía sesiones en producción y ya fue fixeado con backfill SQL. Se documentan por separado.
7. **Supabase "a verificar" → CERRADO.** Única tabla relevante `n8n_chat_histories` (34.725 filas). `workflow_errors` NO vive en este Supabase (va a uno central de la agencia).

---

## 🆕 Validación con el cliente — 2026-08-17 (Etapa 2)

> Respuestas de **Mauricio García** (revisadas sobre el borrador de Max) al cuestionario
> `02_validacion_cliente/cuestionario-venttur-2026-07-24.md`. Lo de acá abajo **supera** al cuerpo de
> este documento donde haya conflicto. Mapeo completo a las preguntas internas en
> `02_validacion_cliente/preguntas-cierre-2026-07-24.md` (A1..A11). Lo que quedó abierto está en
> `02_validacion_cliente/puntos-abiertos-ronda-2-2026-08-18.md`.
>
> **Fecha objetivo de cutover confirmada: 15 de septiembre de 2026.**

### Estado de los issues tras la validación

**Cerrados por la respuesta del cliente:**

| Issue | Resolución |
|---|---|
| §B / N.1 — ¿migrar el pipeline de deals? | **SÍ.** Reconstrucción 1:1 en GHL, histórico completo (abiertos + ganados + perdidos), etapas manuales, sin rediseño. |
| §D.1 / N.5 — ¿`Francia IA` sigue vigente? | **NO es programa**, es destino. Sale del enum. Los destinos van como nota en el contacto. |
| §D.2 / N.6 — Gap Year vs "Estudiar y trabajar" | **El mismo programa** (cursos VET). Asesor: **Andrés**. Diego sale del ruteo automático entero. |
| §D.3 / §D.4 / N.7 — CTWA hardcodeado `'BS'` | **Correcto hoy** (Internados es la única campaña). Debe volverse data-driven antes de la segunda campaña. |
| §D.5 / N.8 — landings | Inventario cerrado: el form de Meta **sustituyó** a `go.venttur.com/bs`, que sigue viva para orgánicos y hay que repuntar a GHL. Los otros 7 programas no tienen. |
| §E.3 / N.10 — tool fantasma `contestan_2do` | **Se descarta la métrica.** No está en el reporte que pidió el cliente. Se elimina la instrucción del prompt. |
| §E.5 — confirmación de cita rota | Requisito firme para los 3 asesores. **El path de Diego se borra** (sale del ruteo); solo se repara el de Andrés. |
| §F.3 / N.13 / N.11 — agendamiento y expertos | 8 calendarios GHL, uno por programa, con disponibilidad compartida por asesor. Nº de Rodrigo vigente. |
| §G (E.10) — timeline | **15 de septiembre de 2026.** |

**Sin cerrar (van a la ronda 2):**

| Issue | Por qué sigue abierto |
|---|---|
| §D.1 (d) — grafía canónica | El cliente no eligió entre `Boarding School` y `Boarding IA`: nombró los 8 programas **en español y con otros nombres**. La normalización ya no es elegir entre dos grafías, es **renombrar el enum entero** y remapear las cohortes. |
| §F.2 — cadencia de nurturing | La respuesta delega en el Reporte la agencia pero no aprueba el tope de 2. La prioridad entre programas no se preguntó. |
| §E.9 — reapertura de conversaciones cerradas | Nunca se preguntó. Sin política, el caso de agosto se repite. |
| Precios (H8) | Nunca se preguntó. Faltan 3 de 8 programas y hay conflicto 50-100k vs 50-130k en Internados. |

**Issues nuevos que la validación destapa:**

- **§D.6 (nuevo) 🔴 — Tres de los ocho programas no existen en el sistema.** `Viajes educativos`,
  `Educación superior` y (parcialmente) `Cursos de idiomas` no tienen enum, ni link, ni drip, ni rama
  de rescate, ni pixel. Verificado por grep exhaustivo: 0 hits fuera del cuestionario. **Impacto en
  producción hoy:** un lead que pregunta por Educación superior cae al fallback `agendar-ema`, o sea
  el link de Internados con Rodrigo (programa y asesor equivocados), no recibe rescate (cae en
  `RESCATE_PROGRAMA_NO_MAPEADO`) y no tiene drip propio. Es **scope nuevo de Etapa 3**.
- **§A.5 (nuevo) 🔴 — Hay dos números de WhatsApp en operación.** ManyChat (agente) y Clientify
  (recordatorios de cita). Ningún doc lo registraba. Explica por qué los recordatorios no aparecen en
  los 14 workflows: viven fuera de nuestro perímetro. Estado destino: un solo número.
- **§C.3 (nuevo) 🟡 — `Conversación interrumpida` tiene dos definiciones en conflicto:** 24 h en el
  barrido vivo vs ~5 días en la definición oficial del cliente. Ver doc 03.
- **§H.1 (nuevo) 🔴 — Gate de cutover:** el cliente exige saber **antes de apagar Clientify** qué no
  se puede migrar (historial de conversaciones, adjuntos, automatizaciones) para respaldarlo por su
  cuenta. Entregable de la agencia, no opcional.
- **§H.2 (nuevo) 🔴 — Camino crítico:** la revisión de portabilidad del número es **prioridad #1**
  por pedido expreso del cliente. Es la única dependencia de un tercero (ManyChat + Meta) y el cuello
  de botella potencial de toda la migración. Decisión ya tomada por adelantado: si hay riesgo de
  downtime, va número nuevo.

---

### ⚠️ Nota sobre la versión que el cliente respondió

El cuestionario que Mauricio contestó es la **versión de 12 preguntas enviada el 2026-08-07**. El
archivo del repo se amplió a **14 preguntas el 2026-08-17** (tras el Reporte la agencia 1), agregando
*rangos de precio* y *qué significa "Cerrada"*, y reescribiendo las de seguimiento y confirmación de
cita. **Esas cuatro modificaciones nunca le llegaron al cliente.** Por eso hay respuestas que
contestan la redacción vieja, y dos temas que quedaron sin preguntar. Se resuelven en
`puntos-abiertos-ronda-2-2026-08-18.md`.


## Índice

- **§0 — Pendientes de mayo YA RESUELTOS** (salen de la lista de bloqueantes)
- **§A — Decisiones de plataforma** (KEEP/REMOVE por sistema)
- **§B — La decisión grande: Clientify deals/pipeline**
- **§C — Redundancias del modelo de datos** (triple write, doble identidad, quirk MX)
- **§D — Ambigüedades del negocio** (programas, links, pixels)
- **§E — Bugs y riesgos operativos a arrastrar/corregir**
- **§F — Patrones ManyChat a re-crear en GHL** (debounce, nurturing, número de Rodrigo)
- **§G — Tabla actualizada "Preguntas para Etapa 2"**
- **Marcadores de incertidumbre** (tabla recap)

---

## §0 — Pendientes de mayo YA RESUELTOS (salen de la lista de bloqueantes)

Estos ítems figuraban como bloqueantes/abiertos en la versión de mayo y hoy están **cerrados** por los inputs de Etapa 0. Se listan para que no se re-arrastren a Etapa 2 como si siguieran pendientes.

| Ítem mayo | Estado mayo | Estado real 2026-07-24 | Evidencia |
|---|---|---|---|
| Rama CTWA no visible en JSON (A.3, E.11) | CONFIRM/abierto | ✅ RESUELTO — rama CTWA completa y cableada | `wf-meta-capi.json` nodos `Buscar Config Programa2`/`Folio (N/A)`/`Preparar CAPI Data2`/`HTTP Request Meta CAPI2` |
| Workflows no exportados (A.4) — Formulario Clientify, CAPI Registro Folio | EXPORT pendiente | ✅ RESUELTO — 14/14 exportados | `wf-formulario-clientify.json`, `wf-capi-registro-folio.json` (id `9yCbynoKDt9hgiBq`, `active:true`) |
| Rescate "diseñado, no activado" (B.1) | DECIDE | ✅ RESUELTO — LIVE en n8n | `wf-rescate-post-link.json` (`mkEP1qFN7MVb9qP0`) |
| Outreach proactivo WA (B.2, E.7) | DECIDE/bloqueado por opt-in | ✅ RESUELTO — LIVE tri-toque | `wf-outreach-form-meta.json` (`CUuFxbst3iHpgeXS`), `consent_phrase` del form |
| Clientify volumen (C.1, E.3) | EXPORT/desconocido | ✅ CONFIRMADO — 6.968/2.338/266/22 | `vtr-data-snapshot-2026-07-24.json` |
| Supabase schema (C, general) | a verificar | ✅ CERRADO — `n8n_chat_histories` (34.725 filas) | `supabase-queries-venttur.md` |
| Estado de lead automático | no existía en el modelo de mayo | ✅ NUEVO — 2 workflows LIVE/diseñados | `wf-estado-lead.json` (`b52CUYEkI2Ah3Xj6`), `wf-estado-interrumpida.json` (`H6qYB3Oj97bxaTCX`) |
| Nurturing 4-toques por programa | no documentado en mayo | ✅ NUEVO — 6 flows ManyChat + dispatcher n8n | `manychat-flows-content-2026-07-20.md`, `wf-resumen-etiquetas-seguimientos.json` |

**Restan genuinamente abiertos de Etapa 0 (no bloquean Etapa 1, sí Etapa 2/3):**
- Keyword triggers CTWA (la API de ManyChat no los expone) → §D.3.
- Config canal WA de ManyChat (número/BAID/proveedor) → necesario recién en Etapa 3.
- Landings: estructura de webhook parcial → §D.5.
- "Notify Assignees: 0 people" del flow Elevar → §E.1.

---

## §A — Decisiones de plataforma (KEEP / REMOVE por sistema)

### A.1 — Clientify → **REMOVE** (contacts/tags/notes absorbidos por GHL)

**Propuesta: REMOVE.** GHL Contacts reemplaza el uso que los workflows de producción hacen de Clientify. Confirmado por código: los workflows solo usan `POST /contacts/` (crear), `GET /contacts/?phone=` (buscar), `POST /contacts/{id}/tags/` (etiquetar) y `POST /contacts/{id}/note/` (nota de resumen). Todo eso tiene equivalente nativo en GHL (contacto, tags, notas).

Clientify aparece en 5 workflows: `Formulario Clientify` (crear/buscar/tag), `Crear contacto Clientify y Airtable` (crear + guardar ID), `Actualizar 'Link enviado'` (tag `<programa>_link_enviado`), `Resumen/etiquetas/seguimientos` (tags por programa + nota "Resumen"), `Confirmación de agenda` (búsqueda por nombre → pivote de matching).

⚠️ **Punto crítico oculto:** en `Confirmación de agenda`, Clientify NO es un CRM pasivo — es la **fuente de `first_name`/`last_name`/`teléfono`** y el pivote del cruce Calendar→Clientify→Airtable. Al retirar Clientify hay que garantizar que ese dato salga del contacto GHL (natural en GHL, porque el appointment ya está ligado al contacto).

**Pregunta de validación:** ¿hay algún dato o automatismo fuera de n8n que dependa de Clientify (reportes, integraciones de marketing, exports manuales del equipo)? El pipeline de deals es el gran interrogante → ver §B.

---

### A.2 — Airtable Folios CAPI + Programas CAPI → **KEEP**

**Propuesta: KEEP en Airtable.** Son estructuras de *tracking/config de pixels*, no de CRM, sin equivalente 1:1 en GHL, y el workflow CAPI (que se queda en n8n) las lee eficientemente.

- **Folios CAPI** (`[AIRTABLE_TABLE_ID]`, 4.003 filas): store de identidad de navegador por clic (Folio → fbc/fbclid/fbp/ip/user_agent/Landing URL/Timestamp/fbtrace_id). La puebla `CAPI Registro Folio` en el clic-a-WhatsApp y la lee `Meta CAPI` al cruzar el folio en la conversación.
- **Programas CAPI** (`[AIRTABLE_TABLE_ID]`, 4 filas): config por programa (pixel_id, access_token, default_url). Cambia raramente.

**Pregunta de validación:** ¿es aceptable mantener Airtable como backend del tracking CAPI post-migración, o el cliente quiere consolidar todo en GHL a largo plazo (custom objects)? Recomendación la agencia: mantener en Airtable — mover no aporta funcionalidad y agrega superficie de fallo.

---

### A.3 — Airtable Leads → **MIGRATE a GHL Contacts** (con caveat de lookup CAPI)

**Propuesta: MIGRATE** los datos de `Leads` (`[AIRTABLE_TABLE_ID]`, **3.819 filas** en el CSV / la tabla Airtable reporta ~3.820; 30 columnas en el export — el schema real es superset, ver doc 05 §9.1) a GHL Contacts, y **congelar** Airtable Leads (read-only).

Mapeo de columnas Leads → Contact GHL (custom fields donde no haya nativo):

| Grupo | Columnas Leads | Destino GHL |
|---|---|---|
| Identidad | Nombre, Apellido, Nombre Completo, Telefono, Email | nativos (firstName/lastName/phone/email) |
| Cross-platform FK | ID Clientify, ID Manychat, id, id_2 | custom fields / external id (ID Clientify se retira) |
| Tracking CAPI | Folio, fbclid | custom fields |
| Atribución | Fuente lead, Ad Name, Platform, Origen | custom fields / attribution source |
| Cualificación (form Meta) | Programa interés, Grado Escolar, Inicio Deseado, Nivel Inglés, Tipo, Cualificado, Lead Score, Tipo lead | custom fields / pipeline |
| Estado embudo | Estado conversación, Última actividad, Agendan cita, Asistió, Link asesoría enviado, Contestan 1er mensaje | pipeline stages + tags/campos |
| Outreach | Outreach Form Meta enviado (+at), Toques enviados, Ultimo toque at, Touch 1 programado at | estado nativo del workflow GHL |
| Reporting | Tabla métricas, Reporte semanal, Creada | reporting nativo / custom field |

⚠️ **Caveat MODIFY (ver también §C.4):** el workflow CAPI hace `filterByFormula {id} = <teléfono>` sobre **Leads** para localizar al lead. Post-migración, si Leads se congela, ese lookup queda desactualizado. Dos opciones: (a) que n8n lea de GHL (API) en vez de Airtable, o (b) mantener un sync GHL→Airtable Leads de campos mínimos (teléfono/nombre/Folio). Se decide en §C.4.

**Pregunta de validación:** ¿GHL Contacts pasa a ser source of truth único, o coexiste con Airtable Leads durante un período de transición?

---

### A.4 — n8n como orquestador CAPI → **KEEP**

**Propuesta: KEEP.** GHL no tiene equivalente nativo para: SHA-256 en JS puro, multi-table lookup en Airtable, construcción de `fbc`/`fbp`/`user_data` y POST a Meta Graph API v21.0 con dedup por `event_id`. Confirmado que `CAPI Registro Folio` (T3) y `Meta CAPI` implementan todo esto a mano. El plan de migración ya prevé "n8n CAPI se mantiene". GHL dispararía n8n vía webhook.

Los tres workflows candidatos naturales a quedarse en n8n: `CAPI Registro Folio` (webhook simple de 5 nodos), `Meta CAPI` (rama folio + CTWA), y — si el agente sigue en n8n — el main.

---

## §B — La decisión grande: Clientify deals/pipeline (DECIDE)

**Contexto nuevo (no existía en mayo):** el snapshot confirmó que Clientify no es solo un almacén de contactos. Tiene un **pipeline comercial manual** que el equipo Venttur gestiona a mano:

- **6.968 contactos · 2.338 deals · 266 companies · 22 custom fields.**
- Deals por campaña: "Campaña Internados Erika" (1.024), "VENTAS EMA METODOLOGÍA" (319), "Campaña Australia Abril 25" (291), "Venta SPE - Internados" (172), etc.
- Estados de deal: Expired 1.875 · Lost 381 · Open 50 · Won 32.
- Stages del pipeline: "AGENDÓ REUNIÓN", "Cita de Ventas concretada", "Día 15/20 Seguimiento", "Gracias por asistir", etc.

**Hecho clave confirmado por código:** NINGÚN workflow de producción de VTR toca deals/companies/custom-fields de Clientify. Los 5 workflows que usan Clientify solo tocan **contacts/tags/notes**. El pipeline de deals es **100% gestión manual del equipo Venttur**, invisible a la automatización.

**Propuesta: DECIDE** — la migración de contacts a GHL Contacts está clara (§A.1). La pregunta abierta es qué hacer con los 2.338 deals + 266 companies + el pipeline manual:

- **Opción 1 — Solo contacts:** migrar contactos a GHL, dejar el pipeline de deals morir con Clientify. Riesgo: se pierde el histórico de ventas y el equipo pierde su tablero comercial. Bajo esfuerzo técnico.
- **Opción 2 — Contacts + Pipeline a GHL Opportunities:** recrear el pipeline comercial como Opportunities/Pipelines de GHL y migrar los deals abiertos (Open 50 + los que el equipo quiera preservar). Alto esfuerzo (mapeo de stages, dueños, montos), pero unifica ventas + conversación en una sola plataforma — que es el argumento fuerte de mover a GHL.
- **Opción 3 — Híbrido:** migrar solo deals `Open` (50) + `Won` recientes para no arrastrar 1.875 Expired; el histórico se archiva como export CSV.

**Pregunta de validación (grande):**
> El equipo Venttur usa el pipeline de deals de Clientify como su tablero de ventas manual (2.338 deals, stages "AGENDÓ REUNIÓN"/"Cita concretada"/etc.). ¿Quieren recrear ese pipeline en GHL Opportunities (y migrar los deals abiertos), o el pipeline queda fuera del scope y solo migramos contactos? Si lo quieren en GHL: ¿migramos solo los `Open`/`Won` o el histórico completo?

---

## §C — Redundancias del modelo de datos

### C.1 — Triple write Airtable + Clientify + Supabase → **DECIDE (consolidar en GHL + n8n)**

Hoy un mismo lead vive replicado en **3 sistemas** con 3 identidades distintas, y varios workflows escriben en los tres:

```
                 ┌─────────────┐
   Lead nuevo ──▶│  Airtable   │  Leads.id = teléfono sin +
                 │  Leads      │  Leads.ID Clientify (FK)
                 └─────────────┘  Leads.ID Manychat (FK)
                        │
          ┌─────────────┼──────────────┐
          ▼             ▼              ▼
   ┌───────────┐  ┌───────────┐  ┌──────────────┐
   │ Clientify │  │  ManyChat │  │  Supabase    │
   │ contact   │  │ subscriber│  │ n8n_chat_    │
   │ (id num.) │  │ (id num.) │  │ histories    │
   └───────────┘  └───────────┘  │ session_id = │
                                 │ tel (52→521) │
                                 └──────────────┘
```

Las FK que resuelven el cruce (confirmadas en `leads.csv` header):
- `Airtable Leads.ID Clientify` → Clientify contact.id (1:1)
- `Airtable Leads.ID Manychat` → ManyChat subscriber
- `Airtable Leads.id` = teléfono sin `+` = `Supabase n8n_chat_histories.session_id` (**¡con quirk MX 52→521!** — ver C.3)
- `Airtable Leads.Folio` → Folios CAPI.Folio

**Propuesta: DECIDE.** En GHL el Contact unifica las tres identidades. Los workflows dejan de hacer triple write. Pero hay que decidir qué se conserva:
- Clientify contact → se retira (§A.1).
- ManyChat subscriber → se retira (canal WA nativo GHL).
- Supabase `n8n_chat_histories` → **depende de dónde viva el agente post-migración** (ver C.2).

**Pregunta de validación:** ¿el agente conversacional "Mauricio" sigue corriendo en n8n leyendo Supabase, o se migra al Conversation AI de GHL? Esta decisión define si Supabase se mantiene o se retira, y es la bisagra de todo el rediseño (ver §D.6 memoria sintética).

---

### C.2 — Memoria del agente (Supabase, 35 turnos) → **DECIDE cómo se preserva en GHL**

El main usa `Postgres Chat Memory` (typeVersion 1.3), `sessionKey = whatsapp_phone.replace('+','')`, `contextWindowLength 35`. GHL **no ofrece memoria de LLM nativa equivalente** de 35 turnos por contacto.

- **Si el agente sigue en n8n:** mantener Supabase tal cual. GHL solo aporta el canal WA + CRM; el webhook de GHL dispara el main de n8n.
- **Si el agente pasa a GHL nativo:** definir cómo se conserva el contexto de las últimas ~35 interacciones. El Conversation AI de GHL tiene su propia noción de contexto (más acotada). Riesgo de degradar la calidad del diagnóstico consultivo de 7 pasos.

**Propuesta: DECIDE** en conjunto con C.1. Recomendación técnica preliminar (la agencia): mantener el agente en n8n al menos en el cutover — es la pieza de mayor valor y mayor riesgo de regresión.

---

### C.3 — Quirk MX 52→521 → **MODIFY (replicar/normalizar en GHL/n8n post-migración)**

**Confirmado en producción** (`supabase-queries-venttur.md` + nodo `Execute a SQL query` de outreach): los celulares MX llegan de WhatsApp como `52XXXXXXXXXX` (12 díg) pero el sistema espera `521XXXXXXXXXX` (13 díg, con el `1` de celular). Nodos de memoria sintética que no normalizaban generaban `session_id` que nunca matcheaba cuando el lead respondía. **Fix + backfill YA aplicados:**

```sql
UPDATE n8n_chat_histories
SET session_id = '521' || SUBSTRING(session_id FROM 3)
WHERE session_id ~ '^52[0-9]{10}$'
  AND NOT (message ? 'tool_calls') AND NOT (message ? 'invalid_tool_calls');
```

⚠️ **Discrepancia confirmada contra fuente primaria:** el brief afirma que este quirk está resuelto, y lo está *en las tablas de memoria*. PERO el análisis nodo-por-nodo del main revela que **el `sessionKey` del propio agente NO normaliza el quirk**: es `whatsapp_phone.replace('+','')` a secas. Es decir, el número MX se guarda tal cual llega (`5214731220110` si WhatsApp ya manda el `1`, o `521...`/`52...` según el caso). La normalización 52→521 vive en los nodos de memoria sintética (outreach/rescate) y en el backfill, **no** en el main. Riesgo de doble identidad de sesión si el mismo lead aparece con y sin el `1`.

**Propuesta: MODIFY.** En GHL, resolver la normalización a **E.164 canónico una sola vez** en la creación del contacto (no en N nodos dispersos). Si el agente sigue en n8n, unificar el `sessionKey` del main con la normalización de los nodos de memoria (hoy divergen).

**Pregunta de validación:** ¿confirmamos que todos los teléfonos MX en producción hoy están normalizados a `521...`, o hay leads con doble sesión (`52...` y `521...`) que hay que reconciliar antes de migrar?

---

### C.4 — El workflow CAPI hace lookup de Leads por teléfono → **MODIFY (leer de GHL o mantener sync)**

Tanto el main (`Buscar si ya existe`) como `Meta CAPI` (`Buscar Lead por Teléfono`) hacen `filterByFormula {id} = <teléfono sin +>` sobre Airtable Leads. Si Leads se congela post-migración (§A.3), ese lookup deja de reflejar el estado real.

**Propuesta: MODIFY.** Dos caminos (elegir en Etapa 3):
- **(a)** Reapuntar el lookup a la **GHL API** (buscar contacto por teléfono). Más limpio, elimina Airtable Leads del hot path.
- **(b)** Mantener un **sync GHL→Airtable Leads** de campos mínimos (teléfono, nombre, Folio, fbclid) para que el CAPI siga leyendo de Airtable sin cambios. Menos refactor, más deuda.

Nota: el nodo `Update record3` de `Meta CAPI` también **escribe** de vuelta en Leads (Folio + fbclid, match por `id_2`). Ese write también hay que reapuntar a GHL Contact o al sync.

**Pregunta de validación:** ¿el equipo tolera que el CAPI consulte la GHL API en cada evento (latencia/quota), o preferimos un sync unidireccional GHL→Airtable para no tocar el hot path del tracking?

---

## §D — Ambigüedades del negocio

### D.1 — Programas del negocio: 6 conceptuales, solo 2 con pixel CAPI → **CONFIRM**

Hay una **desalineación de tres capas** que hay que resolver antes de diseñar GHL:

**Capa 1 — Programas conceptuales del agente** (6, del system prompt, líneas 478-485):

| Programa | Link de agendamiento | Experto |
|---|---|---|
| Internados / Boarding School | `promo.venttur.com/agendar-ema` | Rodrigo |
| Año Académico con familia (AA Familiar) | `promo.venttur.com/AAFamilia-Agendar` | Rodrigo |
| Summer Camp | `promo.venttur.com/SummerCamp-Agendar` | Rodrigo |
| Pathway universitario Alemania | `promo.venttur.com/PW_Alemania_Agendar` | Andrés |
| Gap Year / Estudiar y trabajar (Australia) | `promo.venttur.com/Estudiar-y-Trabajar-en-Australia` | Diego |
| Estudiar y trabajar (cursos idiomas) | `promo.venttur.com/EstudiaryTrabajar_Agendar` | Andrés |
| (duda / fallback) | `promo.venttur.com/agendar-ema` | — |

**Capa 2 — Enum `Programa interés` de Airtable** (8 opciones en el schema): No definido, Boarding IA, Gap Year IA, Pathway IA, Summer Camp IA, AA Familiar IA, **Francia IA**, **Automatización - Comentarios**. → Hay 2 valores (Francia IA, Automatización - Comentarios) que ni el agente ni el nurturing conocen.

> ⚠️ **DECIDE — doble grafía Boarding (issue de calidad de datos).** Existe un **9º valor real, `Boarding School` (482 leads)**, que NO está en el enum de 8 pero **lo escribe activamente el Outreach Form Meta** (`Crear Lead Nuevo` hardcodea `Programa interés='Boarding School'`), mientras la vía conversacional/dispatcher escribe `Boarding IA` (437 leads). Son **dos grafías del mismo programa Boarding** conviviendo (482 vs 437 ≈ 919 leads Boarding en total). Distribución completa real (`leads.csv`, 3819): No definido 1315 · **Pathway IA 881** · AA Familiar IA 632 · Boarding School 482 · Boarding IA 437 · Summer Camp IA 42 · Gap Year IA 25 · Automatización - Comentarios 5. El Rescate se salva por `contains "Boarding"`, pero **exact-match en GHL las trataría como 2 programas → hay que unificar `Boarding School` → `Boarding IA` antes de migrar** y que el Outreach escriba la grafía canónica. **Pregunta al cliente:** ¿cuál es la grafía canónica de cada programa? (definir la tabla única programa→pixel/link/experto/tag/mensajes que pide la Capa 1).

**Capa 3 — Programas CAPI con pixel** (solo 2 pixels reales, confirmado en `programas-capi.csv`):

| Código | Nombre | pixel_id | default_url |
|---|---|---|---|
| BS | Boarding IA | 228398216567258 | go.venttur.com/bs |
| BSG | Boarding IA | 228398216567258 | go.venttur.com/bs/girls |
| BSC | Boarding IA | 228398216567258 | go.venttur.com/bs/cats |
| HF | AA Familiar IA | 24520910174237152 | go.venttur.com/hf |

→ Solo **Boarding** (BS/BSG/BSC) y **AA Familiar** (HF) tienen pixel configurado.

⚠️ **INCIERTO — Summer Camp, Pathway y Gap Year/Estudia y Trabaja NO tienen fila en Programas CAPI** (impacto: su tracking de conversión CAPI a Meta es incierto — probablemente NO disparan evento Lead con pixel propio, o caen a la rama CTWA hardcodeada a `BS`, atribuyendo mal). No asumir que existe pixel para esos programas.

**Propuesta: CONFIRM.** Necesitamos del cliente: (a) la lista canónica de programas activos hoy; (b) si Summer/Pathway/GapYear tienen campañas Meta con pixel y cómo se trackean; (c) si "Francia IA" y "Automatización - Comentarios" siguen vigentes.

**Pregunta de validación:**
> De los 6 programas del agente, solo Boarding y AA Familiar tienen pixel CAPI. ¿Summer Camp, Pathway y Gap Year tienen campañas Meta activas? Si sí, ¿por qué pixel se trackean? ¿Los valores "Francia IA" y "Automatización - Comentarios" de Airtable siguen en uso?

---

### D.2 — Ambigüedad Gap Year vs Estudiar y Trabajar → **CONFIRM (links/expertos duplicados)**

**Confirmado en el system prompt** (líneas 479, 483, 484): hay una superposición conceptual entre dos "programas de estudiar y trabajar" con links y expertos **distintos**:

| Trigger en el prompt | Link | Experto |
|---|---|---|
| "Gap Year / Estudiar y trabajar" (línea 479) | `.../Estudiar-y-Trabajar-en-Australia` | **Diego** |
| "GAP Year Australia" (línea 484) | `.../Estudiar-y-Trabajar-en-Australia` | **Diego** |
| "el programa estudiar y trabajar" (línea 483) | `.../EstudiaryTrabajar_Agendar` | **Andrés** |

⚠️ **INCIERTO — dos entradas casi idénticas ("estudiar y trabajar") ruteando a URLs y expertos diferentes** (impacto: el agente puede mandar al lead al experto/landing equivocado según cómo interprete la frase; en la migración a GHL hay que decidir un mapeo determinístico único). Además, el nurturing de rescate refuerza la confusión: `Rescate Post-Link` mapea "Gap Year" → `/Estudiar-y-Trabajar-en-Australia` mientras que su diccionario de memoria tiene una clave separada "Estudio y Trabajo" → `/EstudiaryTrabajar_Agendar` que **nunca se alcanza** (código muerto, ver §E.4).

**Propuesta: CONFIRM.** ¿Son dos programas distintos (Gap Year Australia con Diego vs. cursos de idioma estudiar-y-trabajar con Andrés) o es la misma cosa duplicada por error? Definir un mapeo 1:1 canónico programa→(link, experto) como fuente de verdad para GHL.

**Pregunta de validación:**
> "Gap Year / Estudiar y trabajar en Australia" (experto Diego) y "el programa estudiar y trabajar" (experto Andrés) — ¿son dos ofertas distintas o la misma? Necesitamos un mapeo único programa → link de agendamiento → experto.

---

### D.3 — Keyword triggers CTWA → **CONFIRM (strings con el cliente)**

La atribución CTWA por texto es lógica crítica: el main matchea el primer mensaje del lead contra el campo `Mensaje` de la tabla `Mensajes anuncios` (25 anuncios: `Anuncio, Mensaje, Interes`), con coincidencia flexible bidireccional case-insensitive, para deducir `Fuente lead` y `Programa interés`. Además, ManyChat tiene keyword triggers CTWA que la API pública **no expone**.

**Propuesta: CONFIRM.** Para GHL necesitamos: (a) los strings exactos de los keyword triggers CTWA de ManyChat; (b) confirmar que la tabla `Mensajes anuncios` es la fuente de verdad de atribución (o si hay lógica extra en ManyChat). En GHL esto se puede resolver con el referral/ad payload de WhatsApp CTWA (`ctwa_clid`/`ad_source_id`) mapeado a campos del Contact, o replicando la tabla + matching en un paso custom.

**Pregunta de validación:**
> ¿Cuáles son los keywords/mensajes de apertura exactos de cada anuncio CTWA activo? ¿La tabla "Mensajes anuncios" (25 filas) cubre todos, o hay campañas nuevas sin registrar?

---

### D.4 — Rama CTWA hardcodea `{Programa}='BS'` → **CONFIRM/MODIFY**

Confirmado en `Meta CAPI`, nodo `Buscar Config Programa2`: la rama CTWA **no deriva el programa del payload** — busca `filterByFormula {Programa}='BS'` fijo. Toda conversión CTWA se atribuye al pixel de Boarding, sin importar el programa real del lead.

⚠️ **INCIERTO — ¿es intencional (solo Boarding hace CTWA) o un placeholder/bug?** (impacto: si hay campañas CTWA de otros programas, sus conversiones se están atribuyendo al pixel de Boarding, ensuciando la data de Meta). El campo `programa_wpp` que mayo asumía como ruteador de CTWA **no aparece en el workflow**.

**Propuesta: CONFIRM** con el cliente; si CTWA es multi-programa, **MODIFY** para mapear por campaña/programa antes de migrar (equivalente a resolver los keyword triggers de D.3). En GHL usar un flag estructurado (custom field `origen` = landing|ctwa + programa) en vez del substring "Folio".

**Pregunta de validación:**
> Los leads que entran por click-to-WhatsApp (sin folio) se atribuyen todos al pixel de Boarding School. ¿Todas las campañas CTWA son de Boarding, o hay CTWA de otros programas que hoy se están atribuyendo mal?

---

### D.5 — Landings: estructura de webhook parcial → **CONFIRM (con Mauricio)**

Sabemos por `CAPI Registro Folio` (pinData real) que la landing `go.venttur.com` postea al clic-a-WhatsApp: `origen, folio, programa, fbclid_completo, fbp, user_agent, timestamp, url` (con utm_* embebidos). Y por `Formulario Clientify` que el form postea: `nombre, apellidos, email, telefono, pais, ciudad, programa, folio, fbclid_completo, fbp, user_agent`. Pero:

⚠️ **INCIERTO — no tenemos el catálogo completo de landings activas ni todos los formatos de webhook** (impacto: si hay landings con estructura distinta que Mauricio no reportó, se pierden leads en la migración). El README marca landings como parcial. Además, la landing manda `fbclid_completo` (no `fbclid`) y `url` (no `landing_url`) — nombres que difieren de lo asumido en mayo.

**Propuesta: CONFIRM** con Mauricio: URLs activas + estructura de cada webhook + si algún form manda campos extra. Los `utm_*` (utm_campaign = ID de campaña Meta, utm_content, utm_term) hoy llegan embebidos en `url` pero **no se parsean a columnas** — oportunidad de mapeo en GHL.

**Pregunta de validación:**
> ¿Cuáles son TODAS las landings activas hoy? ¿Todas postean con la misma estructura de campos (`folio`, `programa`, `fbclid_completo`, `fbp`, `url`)? ¿Podemos aprovechar la migración para parsear los utm_* a campos del contacto?

---

### D.6 — Memoria sintética → **DECIDE (cómo se replica en GHL)**

`Rescate Post-Link` y `Outreach Form Meta` **siembran mensajes sintéticos** en `n8n_chat_histories` (un `system` con datos del lead en prosa + un `ai` con el texto del toque enviado, `session_id` = teléfono normalizado 52→521) para que el agente "Mauricio" no re-salude ni repregunte cuando el lead responde. Es un acoplamiento fuerte con el schema del agente.

**Propuesta: DECIDE.**
- **Si el agente pasa a GHL nativo:** la memoria sintética **desaparece como pieza separada** — el historial vive en GHL Conversations y los outreach salientes ya quedan en el hilo, así que el "no re-saludar" se resuelve solo. Se eliminan `n8n_chat_histories` + quirk 52→521 + backfill SQL.
- **Si el agente sigue en n8n:** hay que **preservar** la escritura a `n8n_chat_histories` desde los workflows de outreach/rescate (y mantener el quirk MX).

Es la misma bisagra que C.1/C.2. Recomendación la agencia: si el agente se queda en n8n, la memoria sintética se mantiene; si migra a GHL, se elimina (simplificación grande).

**Pregunta de validación:** (misma que C.2) ¿el agente vive en n8n o en GHL post-migración?

---

## §E — Bugs y riesgos operativos a arrastrar/corregir

### E.1 — Flow "Elevar" con "Notify Assignees: 0 people" → **CONFIRM (posible bug)**

**Confirmado en `manychat-flows-content-2026-07-20.md`:** el flow "Elevar" hace `Pause all automations: Forever` + `Assign conversation: Unknown user` + `Notify Assignees: 0 people via Messenger & E-mail`. El destinatario aparece vacío/"Unknown user" en el screenshot.

⚠️ **INCIERTO — si "Notify Assignees" está realmente en 0 personas, el equipo humano NO se estaría enterando de las elevaciones** (impacto: leads que piden hablar con un humano o casos de emergencia quedan en un limbo silencioso — el bot se pausa pero nadie recibe aviso). La tool `elevar` del agente dispara este flow (`flow_ns content20250716130059_365663`).

**Propuesta: CONFIRM con Max/Mauricio** si es un artefacto del screenshot o un bug real de config. En GHL, mapear `elevar` a asignación de conversación + notificación real (interna/Slack/email) al equipo, cerrando este gap.

**Pregunta de validación:**
> Cuando el bot "eleva" una conversación a un humano, ¿alguien del equipo recibe una notificación? El flow de ManyChat parece tener "Notify Assignees: 0 people" — ¿es correcto o se están perdiendo escalamientos?

---

### E.2 — Secretos hardcodeados en múltiples workflows → **MODIFY (rotar pre-handoff, URGENTE)**

Confirmado en el análisis nodo-por-nodo: hay tokens en texto plano en varios JSON (que se versionan en el repo):
- **Bearer ManyChat** `3256256:ecc8538e4caee488900c4a02f3170a0a` — hardcodeado en 4 nodos del main + en `Confirmación de agenda` + `Seguimiento agenda`.
- **API key OpenAI** `sk-proj-...` — hardcodeada en el nodo de transcripción Whisper del main.
- **Token Clientify** `Token 3822fcd1...` — hardcodeado en `Formulario Clientify`, `Crear contacto Clientify y Airtable`, `Actualizar 'Link enviado'`, `Confirmación de agenda`.
- **access_token de Meta** por-programa en `Programas CAPI` (Airtable) — se envía en el body del POST.

Nota: `Rescate Post-Link` y `Outreach Form Meta` ya migraron a credencial n8n por nombre (`Venttur Header Auth account`) — mejora de higiene ya aplicada, no en todos.

**Propuesta: MODIFY (URGENTE).** Rotar y mover a credenciales n8n/env TODOS los secretos antes de cualquier export/handoff a GHL. Clientify y ManyChat quedan obsoletos al migrar; rotarlos igual por higiene. El access_token de Meta se mantiene (n8n CAPI se queda) pero moverlo fuera de Airtable a credencial.

**Pregunta de validación:** — (acción técnica de la agencia, no requiere cliente, pero avisar antes de compartir el repo).

---

### E.3 — Tool `contestan_2do` instruida pero inexistente → **DECIDE (implementar o descartar)**

⚠️ **INCIERTO/BUG confirmado:** el system prompt instruye "Si el usuario responde a tu segundo mensaje... activa la herramienta `contestan_2do`", pero **no existe ningún ai_tool con ese nombre cableado en el main** (impacto: el agente tiene instrucción de llamar una tool que no existe; la métrica "contestan 2do mensaje" probablemente nunca se registra o falla silenciosamente). El main solo tiene `crear_contacto` y `elevar` cableadas (`primer_registro` está DISABLED).

**Propuesta: DECIDE.** ¿Se implementa la métrica "contestan 2do mensaje" en GHL o se descarta? Hoy no funciona.

**Pregunta de validación:**
> El prompt del agente menciona una herramienta "contestan_2do" que no existe en el workflow. ¿Esa métrica (leads que contestan el 2º mensaje) es importante para ustedes, o la descartamos?

---

### E.4 — Rescate: código muerto "Estudio y Trabajo" + routing 5 vs 6 → **MODIFY**

Confirmado en `Rescate Post-Link`: los Code nodes que gobiernan el ENVÍO (`Code: Fase 1`/`Fase 2`) mapean solo **5 programas** (Boarding, AA Familiar||Francia, Summer Camp, Pathway, Gap Year). Un lead con `Programa interés = "Estudio y Trabajo"` cae en `matched=false`, recibe tag `RESCATE_PROGRAMA_NO_MAPEADO` y **nunca recibe mensaje de rescate**. En cambio los nodos de MEMORIA sí tienen 6 claves incluyendo "Estudio y Trabajo" → esa clave es **código muerto** (nunca se alcanza porque el gate previo ya cortó al lead).

**Propuesta: MODIFY.** En GHL, una **tabla única programa → (mensaje F1, mensaje F2, URL, tag, experto)** como fuente de verdad, cubriendo TODOS los programas activos sin discrepancia envío-vs-memoria. Ligado a resolver D.1/D.2.

---

### E.5 — `Confirmación de agenda`: referencias a nodos inexistentes → **MODIFY (frágil, 2 de 3 paths rotos)**

Confirmado en `wf-confirmacion-agenda.json`: los paths de Diego y Andrés referencian `$('Obtener ID Manychat')` y `$('Obtener ID Manychat2')` — nodos que **no existen** (solo existe `Obtener ID Manychat1`). Solo el path de **Rodrigo** resuelve correctamente subscriber_id/programa. Sugiere que el workflow se clonó/editó y solo el flujo Rodrigo quedó consistente.

✅ **RESUELTO Y AGRAVADO — Reporte la agencia 1 (agosto 2026) + verificación en el n8n vivo (2026-08-17).**
Ya no es incierto:

- **Las 4 referencias rotas están confirmadas en producción.** En el export vivo, `Settear variables`
  y `Enviar` (path **Andrés**) referencian `$('Obtener ID Manychat')`, y `Settear variables2` /
  `Enviar2` (path **Diego**) referencian `$('Obtener ID Manychat2')`. El único nodo que existe es
  `Obtener ID Manychat1`, usado por el path **Rodrigo**.
- **Ejecución `1362988`** (2026-08-17 19:56:50): el flujo corre
  `Andres → is_asesoria → nombre_lead → Obtener datos → exists → Obtener ID Manychat1 → If →
  Agendan cita = true → Switch → mensaje_andres → Settear variables` y **muere ahí** con
  `Referenced node doesn't exist`.
- **El reporte lo mide del lado del cliente:** de **11 leads que sí agendaron, 0 recibieron
  confirmación** por WhatsApp. No es "2 de 3 paths": en la muestra de julio-agosto no llegó ninguna.
- **Efecto compuesto que no estaba documentado:** el nodo `Agendan cita = true` se ejecuta **antes**
  del envío. Cuando la cadena muere después, el lead queda marcado como que agendó, **no recibe
  confirmación** y además **queda excluido de todo seguimiento** (rescate y outreach filtran por
  `NOT({Agendan cita})`). H1 y H3 del reporte comparten esta causa raíz.

El matching Calendar→Clientify→Airtable sigue siendo frágil (parsing del título con marcador `<>`),
pero **no es lo que rompe hoy**: el trigger dispara y el cruce de identidad resuelve.

**Propuesta: MODIFY.** En GHL, reemplazar por trigger nativo de Appointment (Customer Booked) — el appointment ya está ligado al contacto y trae el assigned user, eliminando el parsing de título y las refs rotas. Alta prioridad de migración por su fragilidad.

**Pregunta de validación — ✅ YA RESPONDIDA, no re-preguntar al cliente.**
El reporte de agosto la contesta con datos: **ningún** lead recibió confirmación (0 de 11 que
agendaron). Los paths de Diego y Andrés están rotos, y el de Rodrigo no alcanzó a cubrir la muestra.

---

### E.6 — Doble alta de contacto (determinística + agéntica) → **MODIFY**

Confirmado en el main: conviven DOS creaciones de lead: (a) determinística (`Crear primer contacto`, nombre del perfil ManyChat first/last_name) al detectar lead nuevo, ANTES del agente; y (b) agéntica (tool `crear_contacto` → sub-workflow Clientify+Airtable, con el nombre que el lead escribe). Duplicación de responsabilidad. En GHL el upsert de contacto por teléfono es nativo → una sola creación.

**Propuesta: MODIFY.** Unificar en un solo upsert de Contact en GHL. Definir la precedencia nombre-de-perfil vs nombre-dicho-por-el-lead (hoy conviven y pueden pisarse).

---

### E.7 — `Formulario Clientify`: no persiste `Programa interés` + versión pre-fix → **MODIFY/CONFIRM**

Confirmado: el nodo upsert de `Formulario Clientify` tiene `Programa interés` en el schema pero **NO lo mapea** → el programa del form solo existe como *tag en Clientify*, no en el CRM Airtable. Además, el JSON en `00_inputs/` es la versión **pre-fix `isExecuted`** (la URL de `Etiquetar Contacto` referencia siempre `Crear Contacto Clientify`, que rompe con "Node hasn't been executed" cuando el lead ya existía). El fix vive en `03_workflows/formulario-clientify-venttur-v1.json`, no en el input.

⚠️ **INCIERTO — este input está desincronizado del workflow vivo** (impacto: bajo para la migración si se usa la versión de `03_workflows/`, pero confirma que hay que trabajar sobre los exports de producción, no sobre los de `00_inputs/`).

**Propuesta: MODIFY.** En GHL persistir el programa del form como **custom field + tag** (mejora sobre la paridad — hoy solo es tag). Datos que el form manda y hoy se ignoran (email, pais, ciudad, folio, fbp, fbclid) → mapear a campos del contacto.

---

## §F — Patrones ManyChat a re-crear en GHL

### F.1 — Debounce de 20 s → **MODIFY (replicar en GHL)**

**Confirmado** en el flow "Recibir mensajes": tras capturar el input en `respuesta_definitiva`, **espera 20 segundos** (buffer anti-fragmentación) antes de llamar al webhook n8n, para agrupar mensajes cortos consecutivos del lead en un solo turno del agente.

**Propuesta: MODIFY.** GHL Workflows tiene su propio mecanismo de espera/trigger que hay que configurar para replicar esto. **Sin este debounce, el lead recibe respuestas fragmentadas** (el agente responde a cada mensaje corto por separado).

**Pregunta de validación:** — (decisión técnica de diseño GHL, confirmar que el trigger de mensaje entrante de GHL permite un buffer de ~20 s).

---

### F.2 — Nurturing 4-toques por programa → **MODIFY (recrear como GHL Workflows, delays 0/1/3/5 d)**

**Confirmado** (`manychat-flows-content-2026-07-20.md`): 6 flows ManyChat (Boarding School, Año Académico/AA Familiar, Gap Year, Pathway, Summer Camp, Lead General) con estructura idéntica: **4 mensajes a delays 0 / +1 día / +3 días (=1+2) / +5 días (=1+2+2)**. Contenido educativo/nurturing de largo plazo (textos completos en `manychat-flows-content-2026-07-20.md`, líneas 65-99). Este drip lo dispara el workflow `Resumen, etiquetas, seguimientos` (dispatcher n8n) — pero SOLO si el lead no recibió link de asesoría (gate anti-doble-contacto).

**Propuesta: MODIFY.** Recrear los 6 drips como GHL Workflows/Campaigns con Wait steps (0/1/3/5 d). Cargar los ~24 mensajes (6 programas × 4 toques) como snippets/templates GHL con `{{contact.first_name}}`. Preservar el **gate**: no disparar nurturing si el lead ya recibió link de asesoría.

⚠️ **INCIERTO — el 4º mensaje de Summer Camp no fue capturado en el screenshot** (impacto: menor — falta 1 de 24 textos; recuperable del ManyChat vivo). El "Lead General" tiene última pausa de 3 días (no 2).

**Pregunta de validación:**
> ¿Los 6 flows de nurturing (Boarding/AA Familiar/Gap Year/Pathway/Summer Camp/Lead General, 4 toques a 0/1/3/5 días) siguen siendo el contenido vigente, o hay ajustes de mensajes/timing pendientes que aprovechemos de incorporar al migrar?

---

### F.3 — Número directo de Rodrigo → **KEEP (preservar)**

**Confirmado** en el flow "Agenda": tras confirmar la cita, ManyChat envía *"Rodrigo se comunicará contigo por WhatsApp directamente desde el número +52 1 33 1944 2476"*. Ese número **no estaba documentado** en ningún doc previo — es dato de negocio.

**Propuesta: KEEP.** Preservar el mensaje y el número en el equivalente GHL del flow "Agenda" (que hoy dispara `Confirmación de agenda` vía `flow_ns content20250721163426_851504`). El texto vive en el flow de ManyChat, no en el JSON de n8n.

**Pregunta de validación:**
> El número +52 1 33 1944 2476 (WhatsApp directo de Rodrigo) se le manda al lead tras agendar. ¿Sigue vigente ese número? ¿Aplica el mismo texto para citas con Diego/Andrés o cada experto tiene su número?

---

### F.4 — Split de respuesta en 3 partes → **MODIFY**

Confirmado: el main formatea la respuesta del agente en `{parte1, parte2, parte3}` (gpt-4o-mini, corta solo tras punto, quita `¿`/`¡` de apertura), y el flow "Enviar mensajes" de ManyChat las envía como 3 mensajes secuenciados con ritmo natural.

**Propuesta: MODIFY.** Replicable con la config de mensajes de GHL o manteniendo el nodo gpt-4o-mini. Los `flow_ns` de ManyChat (envío `content20250617172539_850988`, elevar `content20250716130059_365663`) dejan de aplicar; el envío pasa a GHL Conversations.

---

## §G — Preguntas para Etapa 2 (actualizada)

Consolida las 12 de mayo (marcando cuáles ya se respondieron con los inputs de Etapa 0) + las nuevas que surgen de este doc reescrito.

### G.1 — De la lista de mayo: estado actualizado

| # (mayo) | Pregunta original | Estado 2026-07-24 |
|---|---|---|
| E.1 | ¿Número WA: mismo de ManyChat pasa a GHL? | 🔴 ABIERTA — sigue siendo pregunta de Etapa 3 (config canal WA) |
| E.2 | ¿Rescate: directo en GHL o primero ManyChat? | ✅ RESUELTA — Rescate ya está LIVE en n8n; se recrea directo en GHL |
| E.3 | ¿Clientify: descarte completo? ¿Datos a rescatar? | 🟡 PARCIAL — contacts REMOVE confirmado; **el pipeline de deals es decisión nueva grande** (§B) |
| E.4 | ¿Airtable Leads: GHL reemplaza o coexisten? | 🟡 PARCIAL — propuesta MIGRATE + congelar; falta confirmar caveat lookup CAPI (§C.4) |
| E.5 | Programas CTWA: lista completa con keywords | 🔴 ABIERTA — keywords no exportables por API (§D.3) + hardcode BS (§D.4) |
| E.6 | ¿Landings: quién controla? ¿webhooks? | 🟡 PARCIAL — estructura conocida por 2 workflows; catálogo completo pendiente de Mauricio (§D.5) |
| E.7 | ¿Outreach proactivo WA: scope migración o post? | ✅ RESUELTA — ya LIVE (tri-toque); se recrea en GHL |
| E.8 | Delivery Fase 2 rescate: ¿aceptar gap si ventana cerrada? | 🟡 PARCIAL — el rescate real es 45min+24h; confirmar si el timing sigue OK |
| E.9 | Volumen de leads/día | 🟢 ESTIMABLE — Leads ~3.819 / Folios 4.003 / 34.725 mensajes Supabase; falta tasa diaria exacta |
| E.10 | Timeline deseado / fecha límite | 🔴 ABIERTA — pregunta de negocio |
| E.11 | Rama CTWA: ¿misma workflow o separada? ¿Export? | ✅ RESUELTA — misma workflow, rama cableada (hardcode BS, ver §D.4) |
| E.12 | ¿Datos en ManyChat que no estén en Airtable? | 🟡 PARCIAL — subscriber data + tags; historial vive en Supabase (§C.1) |

### G.2 — Preguntas NUEVAS (de este doc reescrito)

| # | Pregunta | Owner | Bloquea | Ref |
|---|----------|-------|---------|-----|
| N.1 | **¿Recreamos el pipeline de deals de Clientify (2.338 deals) en GHL Opportunities, o solo migramos contactos?** Si sí, ¿histórico completo o solo Open/Won? | Cliente | Etapa 3 | §B |
| N.2 | **¿El agente "Mauricio" sigue en n8n (con Supabase) o migra al Conversation AI de GHL?** Define memoria + memoria sintética + triple write. | la agencia + cliente | Etapa 3 | §C.1/C.2/D.6 |
| N.3 | ¿Confirmamos que todos los teléfonos MX están normalizados a `521...`, o hay leads con doble sesión a reconciliar? | la agencia | Etapa 3 | §C.3 |
| N.4 | ¿El CAPI consulta la GHL API por teléfono, o mantenemos sync GHL→Airtable Leads? | la agencia | Etapa 3 | §C.4 |
| N.5 | ¿Summer Camp / Pathway / Gap Year tienen pixel CAPI propio o cómo se trackean? ¿"Francia IA" y "Automatización - Comentarios" siguen vigentes? | Cliente | Etapa 3 | §D.1 |
| N.6 | "Gap Year Australia" (Diego) vs "estudiar y trabajar" (Andrés): ¿dos programas o el mismo? Necesitamos mapeo único programa→link→experto. | Cliente | Etapa 2 | §D.2 |
| N.7 | ¿Todas las campañas CTWA son de Boarding (hoy se atribuyen a su pixel), o hay CTWA de otros programas mal atribuidos? | Cliente | Etapa 3 | §D.4 |
| N.8 | ¿Cuáles son TODAS las landings activas y su estructura de webhook? ¿Parseamos los utm_* al contacto? | Cliente (Mauricio) | Etapa 4 | §D.5 |
| N.9 | **¿El equipo recibe notificación cuando el bot "eleva" a humano?** El flow Elevar parece tener "Notify Assignees: 0 people". | Max/Mauricio | Etapa 3 | §E.1 |
| N.10 | ¿La métrica "contestan 2do mensaje" es importante? (La tool `contestan_2do` está instruida en el prompt pero no existe.) | Cliente | Etapa 3 | §E.3 |
| N.11 | ¿Los leads que agendan con Diego/Andrés reciben confirmación WA, o solo los de Rodrigo? (2 de 3 paths parecen rotos.) | Cliente + la agencia | Etapa 3 | §E.5 |
| N.12 | ¿Los 6 flows de nurturing (0/1/3/5 d) siguen vigentes, o hay ajustes de mensajes/timing a incorporar? | Cliente | Etapa 4 | §F.2 |
| N.13 | ¿El número directo de Rodrigo (+52 1 33 1944 2476) sigue vigente? ¿Cada experto tiene su número o es genérico? | Cliente | Etapa 4 | §F.3 |

---

## Marcadores de incertidumbre

| Ítem | Qué falta confirmar | Impacto para la migración | Owner / cómo resolver |
|---|---|---|---|
| Pipeline deals Clientify (§B) | Si se migra a GHL Opportunities o se descarta | Alto — define scope y esfuerzo de la migración de CRM | Cliente (Etapa 2) |
| Agente en n8n vs GHL (§C.1/C.2/D.6) | Dónde vive "Mauricio" post-migración | Muy alto — bisagra de todo el rediseño (memoria, triple write, memoria sintética) | la agencia + cliente (Etapa 3) |
| Quirk MX en el main (§C.3) | Si hay leads con doble sesión `52...`/`521...` | Medio — conversaciones huérfanas al cruzar contra Leads | Correr query §6 de `supabase-queries-venttur.md` |
| Lookup CAPI post-congelar Leads (§C.4) | GHL API vs sync a Airtable | Medio — latencia/quota vs deuda de sync | Etapa 3 (diseño) |
| Pixels de Summer/Pathway/GapYear (§D.1) | Si tienen pixel CAPI o no se trackean | Alto — conversiones no atribuidas a Meta | Cliente (Etapa 2) |
| Gap Year vs Estudiar y Trabajar (§D.2) | Si son 2 programas o duplicado por error | Medio — mapeo determinístico programa→link→experto en GHL | Cliente (Etapa 2) — confirmado en prompt L479/483/484 |
| Keyword triggers CTWA (§D.3) | Strings exactos (API ManyChat no los expone) | Alto — atribución de fuente de leads CTWA | Cliente (Etapa 2) |
| Hardcode `{Programa}='BS'` CTWA (§D.4) | Si es intencional (solo Boarding) o bug | Alto — CTWA de otros programas mal atribuidos | Cliente (Etapa 2) — confirmado en `wf-meta-capi.json` |
| Catálogo de landings (§D.5) | URLs activas + estructura de cada webhook | Medio — leads perdidos si hay landings no reportadas | Mauricio (Etapa 2) |
| "Notify Assignees: 0 people" Elevar (§E.1) | Si el equipo se entera de las elevaciones | Alto — escalamientos silenciosos, leads en limbo | Max/Mauricio — abrir el flow en ManyChat |
| Tool `contestan_2do` (§E.3) | Si la métrica importa (la tool no existe) | Bajo — métrica hoy inoperante | Cliente (Etapa 3) — confirmado ausente en main |
| Rescate "Estudio y Trabajo" código muerto (§E.4) | Alcance real de programas sin rescate | Medio — leads de ese programa no reciben rescate | Ligado a D.1/D.2 |
| Paths Diego/Andrés en Confirmación (§E.5) | Si están rotos en el n8n vivo | Alto — confirmaciones WA no enviadas a 2/3 expertos | Cliente + revisar n8n vivo |
| 4º mensaje Summer Camp (§F.2) | Texto del último toque (no en screenshot) | Bajo — 1 de 24 textos, recuperable del ManyChat vivo | Re-fetch ManyChat |
| Debounce 20 s en GHL (§F.1) | Si el trigger de GHL soporta buffer ~20 s | Medio — respuestas fragmentadas si no se replica | Etapa 3 (diseño) |
| sessionKey main vs memoria sintética (§C.3) | Divergencia de normalización teléfono | Medio — inconsistencia de identidad de sesión | Unificar en el rediseño |
| Secretos hardcodeados (§E.2) | — (acción técnica, no incertidumbre) | Alto — riesgo de seguridad al versionar/handoff | la agencia — rotar pre-handoff |

---

> **Cierre:** este documento supera y corrige la versión de mayo 2026. Los 4 grandes hitos que la versión anterior no capturaba — (1) el agente conversacional "Mauricio" como núcleo, (2) rescate + outreach + estado de lead ya en producción, (3) el pipeline de deals de Clientify como decisión nueva, (4) el nurturing 4-toques por programa — reencuadran la migración: no es "portar un sistema reactivo de tracking", sino **migrar un agente conversacional con CRM, atribución CAPI, nurturing multi-toque y estado de embudo, repartido hoy en 5 plataformas, hacia GHL + n8n**. Las decisiones N.1 (pipeline deals) y N.2 (dónde vive el agente) son las dos bisagras que definen el resto del diseño de Etapa 3.
