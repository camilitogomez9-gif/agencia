# 03 · Pipelines GHL — los ~19 comerciales (verbatim) + el operativo del bot

> ### 🔄 Estado a 2026-09-07 — ✅ HECHO (por API, read-back verificado)
> **20 pipelines** creados verbatim + **`OP · Bot Venttur`** (`sezekQ4oFybMb4S5Bop1`, 10 etapas incl. **`Cualificado`**). **`Allow Duplicate Opportunity` = ON** (resuelve `OPPORTUNITY_NO_DUPLICATE`). Los 2.338 deals ya importados (ver `06`).
> **✅ `Cualificado` — criterio DETERMINADO** (dejó de ser propuesta a confirmar): lo escribe un **clasificador batch gpt-4o-mini (~8h post-conversación)**, NO el agente en tiempo real. Regla exacta (las **3**): (i) el lead ya conoce un **2º/3º idioma**; (ii) **estudia/estudió en escuela privada y bilingüe**; (iii) **cumple la edad** del programa (10-17 SummerCamp · 13-17 AñoAcadémico/Boarding · 18-30 Pathway/GapYear). Reconstruido en `vtr-clasificador-postconv-v1` (`Xmyoewwa1W5gm1fy`), representado como **tag de contacto** (fiel al checkbox Airtable). Ver `08`.
> **⚠ Caveat vigente:** el **orden** de las etapas de los pipelines comerciales no venía en el snapshot → confirmar/reordenar en la UI contra Clientify.

> **🔴 Riesgo #2.** Reconstruye en GHL las dos cosas que hoy viven separadas: los **20 pipelines comerciales de Clientify** (2.338 deals, 100% manual, el bot no los toca) replicados **1:1 verbatim**, y el **pipeline operativo del bot** (la secuencia agendó→asistió, hoy flags en Airtable). No se fusionan.
>
> **Para quién:** la agencia. **Prerequisito:** módulo `02` (custom fields de Opportunity + owners) + sandbox **A3** (`abandoned`) y **A6** (moneda) idealmente en verde. **Referencia:** `03_datos_pipeline_deals_estado.md`.
>
> **Estimado:** 4-6 hs. **Corroborado contra el snapshot 2026-07-24** (`clientify.deals[].pipeline_desc` + `pipeline_stage_desc`, extracción real).

---

## 3.1 Regla de reconstrucción (decisión del cliente P10)

*"Reconstrúyanlo tal como está hoy, lo más parecido posible. Mismas etapas, mismos nombres, mismo orden. No queremos rediseñarlo… migrarlo igual y después nosotros depuramos."*

→ **Se replican TODOS los pipelines**, incluidos los muertos, marcados `legacy`. **No se descarta ninguno** salvo orden explícito del cliente. Cada `pipeline_desc` → **1 GHL Pipeline**; cada `pipeline_stage_desc` → **1 GHL Stage**; cada deal → **1 Opportunity** (mapeo de campos en `02 §2.5` + `06`).

> **Vocabulario Clientify (para comunicar al cliente):** los *deals* de la API se llaman **"Negocios"** en la UI de Clientify (español); *companies* = **"Empresas"**; *contacts* = **"Contactos"**. Los 2.338 deals de este doc = los **2.338 Negocios** que ve Mauricio en Clientify.

> ⚠️ **El orden de las etapas NO está en el snapshot** (el `pipeline_stage` no trae índice de orden). Se toma de la **UI de Clientify** al construir cada pipeline. Donde `03_arquitectura` dio una narrativa ordenada (Operativo Internados, Operativo Pathway, VENTAS EMA, Campaña Internados Erika), se usa esa; para el resto, **confirmar el orden en Clientify** antes de crear los stages. Los stages de abajo están **verbatim** pero listados por volumen, no por orden.

---

## 3.2 El pipeline operativo del bot (reconstrucción — `03 §5`)

La única pieza de este módulo que **no es 1:1** (hoy el "funnel del bot" son flags en Airtable, no un pipeline). Se le da casa GHL-nativa porque es de donde el **reporte semanal lee "citas agendadas"** (`08`).

**Pipeline `OP · Bot Venttur` — stages (secuencial):**

`Nuevo Lead` → `Contactado` → `En diagnóstico` → **`Cualificado`** 🔶 → `Cita agendada` → `Cita confirmada` → `Asistió` → (`Ganado` ↘ `Perdido` / `Abandonado frío`)

| Stage | Alimentado por | Nota |
|---|---|---|
| Nuevo Lead | Contact creado (primer inbound) | |
| Contactado | el agente respondió | |
| En diagnóstico | agente en los 7 pasos | |
| **Cualificado** 🔶 | *"lo escribe el agente al cerrar el descubrimiento"* | **propuesta de la agencia — requiere OK del cliente** (`03 §5b`). El cliente lo define cualitativo (avanza + encaja con el perfil) |
| Cita agendada | flag `Agendan cita` / booking GHL Calendar (`04`) | **← el reporte semanal lee de acá** |
| Cita confirmada | confirmación enviada (`04`) | ≠ agendada; hito terminal distinto |
| Asistió | flag `Asistió` | ⚠️ **NO alimenta el reporte** (el cliente lo sacó; Max mide asistencia aparte) |
| Ganado / Perdido / Abandonado frío | terminal | |

**Guarda forward-only (n8n):** el workflow que escribe la etapa chequea el estado terminal antes de degradar (réplica del anti-downgrade de `wf-estado-lead`, `03 §5`). **No** se delega a automatizaciones de GHL.

> **Separación dura (`09 §2`):** este pipeline mueve **solo el estado del bot**. **No toca** los ~20 comerciales del §3.3. Un Contact puede tener a la vez su Opportunity operativa (bot) y Opportunities comerciales (humano) sin pisarse.
>
> **Reconciliación cita agendada/confirmada (`03 §5`):** la **etapa del pipeline** es la fuente de verdad de la cita; el custom `estado_conversacion` la **refleja**, no la gobierna. Cierra la desincronización de hoy (`Agendan cita=true` conviviendo con `Estado='Interrumpida'`).

---

## 3.3 Los 20 pipelines comerciales (verbatim del snapshot)

**Contexto duro:** 2.338 deals · **1.875 Expired (80%)** · 381 Lost · **50 Open + 32 Won = 82 vivos**. Todos migran (histórico que el cliente depura después).

### 3.3.A Tabla maestra (clasificación + ola B3)

| # | Pipeline Clientify | Deals | Vivos (Op/Won) | → Programa (`01`) | Clasificación | Ola B3 |
|---|---|---|---|---|---|---|
| 1 | **Campaña Internados Erika** | 1.024 | 4 (0/4) | Internados | nurturing legacy | ola 2 |
| 2 | **VENTAS EMA METODOLOGÍA** | 319 | 28 (27/1) | transversal | embudo pre-venta (humano) | ola 2 |
| 3 | Campaña Australia Abril 25 | 291 | 0 | Gap Year | **legacy muerto** | ola 2 |
| 4 | Venta SPE - Internados | 172 | 3 (0/3) | Internados | campaña | ola 2 |
| 5 | «sin pipeline» | 110 | 6 (0/6) | — | deals sueltos → Default GHL | ola 2 |
| 6 | Afiliación Venttur | 88 | 1 (0/1) | — (B2B) | afiliados | ola 2 |
| 7 | **Operativo Internados** | 74 | 2 (2/0) | Internados | **delivery** | ola 2 |
| 8 | Reclutamiento de escuelas | 43 | 0 | — (B2B) | **legacy muerto** | ola 2 |
| 9 | Academias Deportivas | 33 | 0 | — (nicho) | **legacy muerto** | ola 2 |
| 10 | Seguimiento | 28 | 1 (1/0) | — | genérico | ola 2 |
| 11 | **Operativo Año Académico** | 28 | 3 (3/0) | Intercambio académico | **delivery** | ola 2 |
| 12 | Viaje a Japón UP 2026 | 22 | 17 (0/17) | — | **activo** (casi todo Won) | ola 2 |
| 13 | **Operativo Summercamp** | 22 | 2 (2/0) | Campamentos | **delivery** | ola 2 |
| 14 | **Operativo Idiomas** | 22 | 0 | Cursos de idiomas ⭐ | **delivery** | ola 2 |
| 15 | **Operativo Gap Year** | 19 | 4 (4/0) | Gap Year | **delivery** | ola 2 |
| 16 | **Operativo Pathway** | 18 | 8 (8/0) | Pathway Alemania | **delivery** | ola 2 |
| 17 | **Operativo Educación superior** | 12 | 3 (3/0) | Educación superior ⭐ | **delivery** | ola 2 |
| 18 | La Garenne CDMX | 6 | 0 | — (escuela) | **legacy muerto** | ola 2 |
| 19 | La Garenne Leon | 6 | 0 | — (escuela) | **legacy muerto** | ola 2 |
| 20 | Por defecto | 1 | 0 | — | Default Clientify | ola 2 |

> ⭐ **`Operativo Idiomas` (14) y `Operativo Educación superior` (17)** confirman que 2 de los 3 huérfanos del bot **SÍ existen comercialmente** — el huérfano es solo del lado automatización (`10`). **`Viajes educativos` NO tiene pipeline** → es el único 100% nuevo en ambos lados (crear en `10`).
>
> **Decisión B3 — ✅ Opción A (completo, cliente 2026-09-03):** los **20 comerciales + el operativo del bot van todos el 15/9**. La columna "Ola B3" queda como referencia del análisis previo (bajo la Opción B descartada, los 20 comerciales habrían sido 2ª ola). Con A, la reconstrucción de los 2.338 deals (buena parte manual, `06 §6.3`) tiene que estar hecha **antes** del cutover → arrancar temprano.

### 3.3.B Stages verbatim — Delivery (`Operativo *`, 7 pipelines)

Etapas ricas de fulfillment. **Orden narrativo** de `03` donde existe; el resto, confirmar en Clientify.

- **Operativo Internados** (13): Envío de aplicación a la familia y revisión → Envío de aplicación a la institución → Exámenes posicionamiento → Aceptación del estudiante y recepción de facturas → PRESENTACIÓN → PRESUPUESTO ABIERTO → PRESUPUESTO PAGADO → Pago del programa → Recepción de documentos oficiales para visado → Gestión de visado → Coordinar llegada → JUNTA FAMILIA + ESCUELA → **Estudiante en destino**.
- **Operativo Pathway** (9): Enviar documentación a la escuela para pre-evaluación → Presentar ETA a estudiante y papás → Cobrar Inscripción 1 → Cobrar inscripción 2 + inscripción escuela → Recopilar documentación en físico para trámites → Traducir + Copias Certificadas de Documentos Checklist → Crear MEE (si aplica) → Cobrar Programa → **Estudiante en destino**.
- **Operativo Año Académico** (9): Recabar documentos y datos para la aplicación → Realizar aplicación → Recibir documentos de la escuela → Enviar presupuesto final → Cobrar programa → Enviar comprobante de pago a la escuela → Tramitar Visa (si aplica) → Coordinar llegada → **Estudiante en destino**.
- **Operativo Gap Year** (7): Cobrar inscripción → Enviar presupuesto final → Cobrar programa → Enviar comprobante pago a la escuela y LOO Firmado + Diploma de prepa traducido → Recepción CoE (Post Pago programa) → Cobrar y tramitar seguro OSHC → **Estudiante en destino**.
- **Operativo Summercamp** (3): Trámites Migratorios → Coordinar llegada → **Estudiante en destino**.
- **Operativo Idiomas** (4): Realizar aplicación → Cobrar programa → Tramitar visa (Si aplica) → **Estudiante en destino**.
- **Operativo Educación superior** (3): Cobro de inscripción → Tramitar visa (Si aplica) → **Estudiante en destino**.

### 3.3.C Stages verbatim — Campaña / nurturing / pre-venta (6 pipelines)

- **Campaña Internados Erika** (12, nurturing): Dejo Sus Datos → Contestó La llamada y continua seguimiento por Whatsapp → Continuó Conversación WA → Día 1 Seguimiento → Día 5 Seguimiento → Día 10 Seguimiento → Día 15 Seguimiento → Día 20 Seguimiento → Agendar Cita de Venta. → Agendar Cita Venta Cruzada → Cita de Ventas concretada → Cita Concretada de Venta Cruzada.
- **VENTAS EMA METODOLOGÍA** (12, embudo pre-venta): AA PUBLICO → PERFILAMIENTO INDIVIDUAL → AGENDÓ REUNIÓN → RE-AGENDÓ LA REUNIÓN → NO ASISTIÓ A LA REUNIÓN → ASISTIÓ A LA REUNIÓN → PRESENTACIÓN → PRESUPUESTO ABIERTO → PRESUPUESTO ENVIADO → (+ etiquetas de programa mezcladas: **SUMMER CAMP**, **IDIOMAS**, **PERDIDA DE CAMPAÑA PASADA**). ⚠️ Migrar verbatim incluidas las etiquetas de programa como stages (así están hoy).
- **Venta SPE - Internados** (6): No contesto - se envió Whatsapp → Contactar para agendar cita → Llamar de nuevo más tarde → Agendó Reunión → Seguimiento post reunión → En espera de pago - cobranza.
- **Afiliación Venttur** (7, B2B): Envió Whatsapp → Dejo sus datos → Continúo Conversación → Revisando requisitos → Agendo Videollamada → Asistió a Video Llamada → Firma de contrato.
- **Seguimiento** (3, genérico): 1er Seguimiento (1er día) → 4to Seguimiento (Mes 4) → 5to Seguimiento (Mes 6).
- **Viaje a Japón UP 2026** (2, activo): Inscripción y recepción de documentos → Viaje liquidado.

### 3.3.D Stages verbatim — Legacy muertos (0 vivos) + sueltos

Migran marcados `legacy` (instrucción del cliente); archivar es su decisión de depuración post-cutover.

- **Campaña Australia Abril 25** (2): Se registró → Gracias por asistir. *(291 deals, todos muertos)*
- **Reclutamiento de escuelas** (1): Solicitud de cita.
- **Academias Deportivas** (3): Ingreso a la base de Datos → Leyó Correo de Presentación → Requisitos para firma de convenio.
- **La Garenne León** (3): Dejo sus datos → Dia del evento → Después del evento.
- **La Garenne CDMX** (2): Dejo sus datos → Después del evento.
- **«sin pipeline»** (110) + **Por defecto** (1, stage `Propuesta presentada`) → **1 pipeline GHL `Sin asignar / Default`** para no perder los deals (`03 §6.6`).

---

## 3.4 Deal → Opportunity (recordatorio del mapeo)

Campo por campo está en `02 §2.5` (custom fields) + `06` (import). Lo load-bearing de este módulo:

| Campo deal | → Opportunity | Nota |
|---|---|---|
| `pipeline_desc` / `pipeline_stage_desc` | `pipelineId` / `pipelineStageId` | a los reconstruidos (verbatim) |
| `status` | `status` (open/won/lost/**abandoned**) | ⚠️ `Expired`→`abandoned` — **depende de A3** |
| `amount` + `currency` | `monetaryValue` + custom `moneda` | ⚠️ mezcla MXN/USD — **depende de A6** |
| `contact*` | `contactId` | **link al Contact ya mergeado en `06`** (por teléfono canónico / email) |
| `owner_name` | `assignedTo` | mapeo de owners **confirmado en `02 §2.2`** (incl. los 2 Diegos + históricos) |
| `company` | vía **Contact↔Company** | GHL no expone Opportunity↔Company directo — **depende de A4** |

**Orden de carga (`02 §8`):** Companies → Contacts → **Opportunities** (este módulo). Los deals cuyo contacto no resuelva en el merge quedan como Opportunities sin Contact → a revisar en la auditoría de migrabilidad.

---

## 3.5 Banderas y checkpoints

> ✅ **Sandbox 2026-09-03:** `abandoned` **seteable por API** (A3 ✅) · `monetaryValue` se preserva crudo → `moneda` custom viable (A6 ✅) · Companies = endpoint **`/businesses/`** (A4, corrección). 🆕 **`OPPORTUNITY_NO_DUPLICATE`:** GHL bloquea una 2ª Opportunity para el **mismo contacto** en un pipeline → **un contacto Clientify con varios deals en el mismo pipeline colisiona al importar.** Antes del import: verificar/activar el setting **"Allow Duplicate Opportunity"** (familia de *Allow Duplicate Contacts*), o dedupear deals por contacto+pipeline. **Bloqueante del import de los 2.338 deals — resolver en `06`.**

| Bandera | Estado |
|---|---|
| `Expired`→`abandoned` seteable por API | ✅ **A3 PASÓ** — cargar `abandoned` directo (no hace falta `status_origen_clientify`) |
| Moneda mixta MXN+USD | ✅ **A6 PASÓ** — opción (a) `monetaryValue` + custom `moneda` |
| Opportunity↔Company vía Contact | **A4** — Company es `/businesses/`; el vínculo se deriva vía el Contact |
| 🆕 Opp duplicada por contacto | **`OPPORTUNITY_NO_DUPLICATE`** — activar "Allow Duplicate Opportunity" o dedupear antes del import (`06`) |
| Orden de stages | ⚠️ **confirmar en Clientify UI** (no está en el snapshot) |
| Owners de deals (incl. inactivos con deals) | **cerrado en `02 §2.2`** con el cliente antes de cargar |
| 5 pipelines 100% muertos (379 deals) | migran `legacy` por instrucción del cliente; archivar es su decisión |
| Pipeline operativo del bot ≠ 1:1 | justificado (`03 §5`); `Cualificado` 🔶 requiere OK del cliente |

✅ **Checkpoints de cierre:**
- [ ] Pipeline `OP · Bot Venttur` creado con sus 8 stages (Cualificado confirmado o marcado provisional).
- [ ] Los 20 comerciales creados con stages **verbatim** y **orden confirmado en Clientify**.
- [ ] `«sin pipeline»` + `Por defecto` → 1 pipeline `Sin asignar / Default`.
- [ ] Pipelines legacy marcados como tal (nombre o tag).
- [ ] (B3 = Opción A) los 20 comerciales + operativo del bot cargados y reconciliados **antes** del 15/9.

---

*Corroborado contra el snapshot 2026-07-24: 20 `pipeline_desc` distintos, 2.338 deals (1.875 Expired / 381 Lost / 50 Open / 32 Won), stages verbatim extraídos de `pipeline_stage_desc`. 2026-09-03.*
