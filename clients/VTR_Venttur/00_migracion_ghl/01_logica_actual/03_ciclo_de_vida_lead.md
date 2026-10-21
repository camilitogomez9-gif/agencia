# 03 — Ciclo de Vida del Lead

> **Reescrito 2026-07-24** con los inputs completos de Etapa 0 (14 workflows n8n + snapshot de datos de las 5 plataformas + 6 CSVs Airtable + system prompt del agente + schema Supabase). Supera la versión de mayo 2026, que se generó con inputs parciales y contenía errores materiales (ver más abajo / doc 06).
>
> **Fuentes primarias usadas:** análisis nodo-por-nodo de los 14 workflows JSON (`wf-venttur-main` / `[Venttur]` `k3aivKSP67S97IHn`, `Meta CAPI` `z98w2yWVEMOfifMl`, `CAPI Registro Folio` `9yCbynoKDt9hgiBq`, `Formulario Clientify` `ZB6erhWicZmDfC4I`, `Crear contacto Clientify y Airtable` `cZUNKQyZNOHy5twQ`, `Actualizar Link enviado` `gRSMjzxggA4UePjz`, `Rescate Post-Link` `mkEP1qFN7MVb9qP0`, `Confirmación de agenda` `2PSekVBxarsrnVBu`, `Seguimiento agenda` `DZlSEQS5qzX1Y01K`, `Resumen, etiquetas, seguimientos` `DyrDumQgb6S4zHsS`, `Outreach Form Meta` `CUuFxbst3iHpgeXS`, `Estado lead (Contestó)` `b52CUYEkI2Ah3Xj6`, `Estado interrumpida (barrido)` `H6qYB3Oj97bxaTCX`, `Correo Semanal` `BrFfQyDfamdUzq64`) · system prompt del agente Mauricio (`agente-venttur-system-prompt-EXTRAIDO-2026-07-24.md`) · `template-texts-canonical.md` · `manychat-flows-content-2026-07-20.md` · `supabase-queries-venttur.md` · `airtable-csvs/{leads,programas-capi,folios-capi}.csv`.

---

### Correcciones vs. versión mayo 2026

- **❌ Mayo: "Venttur no tiene agente conversacional; el sistema es reactivo (tracking + CRM + rescate)."** → **CONFIRMADO FALSO.** El corazón del sistema es un AI Agent conversacional ("Mauricio", gpt-4o, temp 0) con un system prompt de ~39K chars, memoria Postgres (Supabase, `contextWindowLength` 35) y un diagnóstico consultivo de 7 pasos. El lead atraviesa **dos capas de estado en paralelo**: la conversacional (dónde está en el diagnóstico del agente) y la operativa (qué campos tiene seteados en Airtable). Mayo solo modeló la segunda, y con datos inferidos.
- **❌ Mayo: estados inferidos sin campos reales** (S1..S11 con nombres inventados). → Ahora hay un single-select real `Estado conversación` con **4 valores confirmados** (`Activa` · `Contestó` · `Cita confirmada` · `Conversación interrumpida`) + una batería de checkboxes (`Agendan cita`, `Asistió`, `Link asesoría enviado`, `Outreach Form Meta enviado`, `Contestan 1er mensaje`, `Cualificado`) + contadores (`Toques enviados`, `Lead Score`, `Tipo lead`). El modelo de mayo se reemplaza por estos campos reales.
- **❌ Mayo: Rescate Post-Link "diseñado, no activado, vive en ManyChat"** → EN PRODUCCIÓN como workflow n8n `mkEP1qFN7MVb9qP0` (2 fases: 45 min + 24 h) + inyección de memoria sintética en Postgres.
- **❌ Mayo: Outreach proactivo WA "no implementado"** → EN PRODUCCIÓN (`CUuFxbst3iHpgeXS`), tri-toque (Touch 1/2/3) disparado desde un Google Sheets sync de Meta Lead Ads, con Lead Score/Tipo lead y 8 campos de cualificación.
- **🆕 Nuevo: Estado de lead** — 2 workflows (`b52CUYEkI2Ah3Xj6` estampa `Contestó`; `H6qYB3Oj97bxaTCX` barre y estampa `Conversación interrumpida`).
- **🆕 Nuevo: Nurturing 4-toques por programa** (6 flows ManyChat) + dispatcher n8n (`DyrDumQgb6S4zHsS`) con gate anti-doble-contacto.
- **📊 Data model ampliado:** Airtable Leads tiene **30 columnas** (mayo documentó ~9).
- **⚠️ Corrección al brief:** el campo `programa_wpp` que mayo (y el brief) asumía como discriminante CTWA **no existe** en ningún workflow — la rama CTWA del CAPI hardcodea `{Programa}='BS'`. Ver §7 y Marcadores de incertidumbre.

---

## 🆕 Validación con el cliente — 2026-08-17 (Etapa 2)

> Respuestas de **Mauricio García** (revisadas sobre el borrador de Max) al cuestionario
> `02_validacion_cliente/cuestionario-venttur-2026-07-24.md`. Lo de acá abajo **supera** al cuerpo de
> este documento donde haya conflicto. Mapeo completo a las preguntas internas en
> `02_validacion_cliente/preguntas-cierre-2026-07-24.md` (A1..A11). Lo que quedó abierto está en
> `02_validacion_cliente/puntos-abiertos-ronda-2-2026-08-18.md`.
>
> **Fecha objetivo de cutover confirmada: 15 de septiembre de 2026.**

### Lo que cambia en el ciclo de vida

**1. 🚨 Conflicto abierto en `Conversación interrumpida` / "no continuada": 24 h vs ~5 días.**

| Fuente | Definición |
|---|---|
| Sistema vivo (`wf-estado-interrumpida`, `H6qYB3Oj97bxaTCX`) | Silencio **> 24 h** sin cita |
| Cliente (definición oficial del reporte, 2026-08-17) | "deja de contestar los mensajes de seguimiento, al agotarse la secuencia completa, **aproximadamente a los 5 días**" |

Son dos definiciones distintas del mismo estado y **la que corre en producción es la de 24 h**.
Hay que decidir en Etapa 3: o el barrido se mueve a 5 días, o se aceptan dos conceptos separados
(estado operativo a 24 h ≠ métrica de reporte a 5 días). Además, la definición del cliente ancla en
"al agotarse la secuencia completa": si la secuencia se recorta al tope de 2 toques, se agota antes
y el "~5 días" deja de valer. **Hay que re-anclar la definición a la cadencia nueva.**

**2. `Cualificado` recibe definición oficial, pero cualitativa.**
Textual: *"El que continúa la conversación, contesta las preguntas del agente de manera favorable al
perfil que buscamos y muestra interés real. No basta con que responda una vez: tiene que avanzar en
el descubrimiento y encajar con el perfil."* No es computable tal cual. Propuesta: que el criterio
duro sea el checkbox `Cualificado` de Airtable y que **lo escriba el agente** al cerrar el
descubrimiento.

**3. `Asistió` sale del reporte (no del modelo).**
El cliente reporta solo **citas agendadas**; la asistencia real la mide Max por su cuenta. El campo
se conserva pero deja de alimentar el reporte semanal.

**4. La capa operativa gana una segunda vida en GHL como Opportunities.**
El pipeline comercial post-cita de Clientify (2.338 deals) se reconstruye **1:1** en GHL: mismas
etapas, mismos nombres, mismo orden, sin rediseño, con histórico completo (abiertos + ganados +
perdidos). Las transiciones **siguen siendo manuales**, igual que hoy: no se automatiza ninguna en
esta fase.

**5. El estado `Programa interés` deja de poder precargarse desde el anuncio.**
Cambio de política del cliente: el agente **no asume** el programa ni cuando el origen parece obvio.
El valor de ese campo pasa a escribirse **solo** desde el descubrimiento conversacional. La atribución
de campaña viaja por separado y no toca este campo.

**6. 🔴 Sigue abierto: qué es "Cerrada" y qué debe pasar en la reapertura.**
No se preguntó (ver abajo, "Nota sobre la versión respondida"). El caso de agosto sigue sin política:
un mensaje off-topic sobre una conversación cerrada la reabrió, le cambió el programa y disparó 5 días
de automatización. Va en la ronda 2.

---

### ⚠️ Nota sobre la versión que el cliente respondió

El cuestionario que Mauricio contestó es la **versión de 12 preguntas enviada el 2026-08-07**. El
archivo del repo se amplió a **14 preguntas el 2026-08-17** (tras el Reporte la agencia 1), agregando
*rangos de precio* y *qué significa "Cerrada"*, y reescribiendo las de seguimiento y confirmación de
cita. **Esas cuatro modificaciones nunca le llegaron al cliente.** Por eso hay respuestas que
contestan la redacción vieja, y dos temas que quedaron sin preguntar. Se resuelven en
`puntos-abiertos-ronda-2-2026-08-18.md`.


## 1. No hay un pipeline formal — hay 4 capas de estado superpuestas

Venttur **no tiene un campo único "estado" ni un pipeline CRM lineal** como HPF (31 etapas Kommo). El "estado" real de un lead es la superposición de cuatro capas, cada una en su plataforma:

| Capa | Vive en | Qué modela | ¿Automatizada? |
|------|---------|------------|----------------|
| **A. Estado conversacional del agente** | Supabase `n8n_chat_histories` + razonamiento del LLM | En qué paso del diagnóstico de 7 pasos está Mauricio con este lead | Sí (n8n + gpt-4o) |
| **B. Estado operativo del lead** | Airtable `Leads` (30 columnas) | Flags de conversión: contestó, agendó, asistió, link enviado, toques de outreach, score | Sí (n8n) |
| **C. Estado de tracking / atribución** | Airtable `Folios CAPI` + `Programas CAPI` + Meta | Si el evento Lead se disparó a Meta, con qué señales de match | Sí (n8n) |
| **D. Estado comercial (venta)** | Clientify `deals` (pipeline manual) | Etapa de la venta consultiva: agendó → asistió → seguimientos Día 1/5/10/15/20 → Won/Lost | **NO — gestión manual del equipo Venttur** (inferido, ver §5) |

La consecuencia operativa (que GHL debe resolver): **es imposible reconstruir el estado completo de un lead sin cruzar Airtable + Supabase + Clientify simultáneamente.** El único identificador que une todo es el **teléfono** (con el quirk MX 52→521, ver §6.4).

> ⚠️ INCIERTO — la capa D (pipeline comercial Clientify) se infiere como **100% manual** porque **ninguno de los 14 workflows n8n toca `deals`, `companies` ni `custom-fields` de Clientify** — solo usan contacts/tags/notes (impacto: si el equipo mueve deals a mano, la migración a GHL Opportunities requiere definir con Venttur qué evento dispara cada cambio de etapa, hoy no hay automatización que replicar).

---

## 2. Capa A — Estados conversacionales del agente "Mauricio"

Fuente: system prompt inline del nodo `Agente IA WPP` (`wf-venttur-main`). El agente corre un **diagnóstico consultivo adaptativo de 7 pasos**, apoyado en frameworks Chris Voss (empatía táctica: labeling, mirroring, preguntas calibradas) + Alex Hormozi (diagnóstico antes de prescribir) + metodología propia **EMA** (Evaluation → Match → Achieve).

**Regla rectora (confirmada, verbatim):** *"No avances automáticamente al siguiente paso si el anterior no se ha completado con claridad según tu criterio… Puedes permanecer en un mismo paso por varias interacciones si eso fortalece la conexión, claridad o confianza."* → el agente **permanece o avanza según su propio criterio de "claridad suficiente"**, no por reglas duras. Esto es un modelo de estados *blando* (no una máquina de estados determinística).

### Los 7 pasos (estados conversacionales)

| Paso | Estado conversacional | Objetivo | Cómo avanza / permanece | Efecto lateral (tool / campo) |
|------|----------------------|----------|--------------------------|-------------------------------|
| **1** | Conexión + nombre | Saludar, generar confianza, **capturar nombre+apellido de QUIEN ESCRIBE** (nunca del hijo/a) | Permanece hasta obtener nombre completo. Regla dura: *"SIEMPRE preguntar por el nombre… aún si busca un plan para su hijo/hija"* | Al recibir nombre+apellido → dispara tool `crear_contacto` (Clientify+Airtable), sin avisar al lead |
| **2** | Padre o estudiante | Determinar si el interés es para el lead o para un tercero (hijo/a) | Pregunta neutral: *"¿Estás buscando una experiencia para ti o para alguien más?"* | Afina el tono; alimenta `Tipo` (Padre/Madre vs Estudiante) que luego setea el dispatcher `DyrDumQgb6S4zHsS` |
| **3** | Motivación personal | Explorar el cambio de vida / razón real detrás de la consulta | Se activa ante señales de cambio, dudas o razones personales. Puede quedarse aquí varios turnos | — |
| **4** | Idioma + país | Nivel de idioma y si ya tiene un destino en mente | Pregunta abierta; no cierra destino prematuramente (Regla 5) | — |
| **5** | Cualificación (edad, escuela, intereses) | Datos duros del perfil: edad, tipo de escuela, hobbies | Por partes, con conexión emocional entre preguntas | Insumo del scoring `Cualificado` (ver §5.3) |
| **6** | Recomendación contextualizada | Mencionar el tipo de programa que ajusta (Internado / Gap Year / Pathway…) como **puente**, no como cierre | Regla 2: *"No recomiendes sin diagnóstico completo"*. Regla 3: prioriza Internado si <17 con búsqueda de estructura | Determina qué link de asesoría se enviará en el paso 7 |
| **7** | Cierre consultivo | Ofrecer la asesoría (videollamada con Rodrigo/Andrés/Diego) y **enviar el link** de agendamiento | Solo con "claridad suficiente". Regla 6: si no responde al 1er ofrecimiento, NO insiste — genera más valor y reofrece con nueva justificación. Regla 8: no repetir el link | Al enviar `promo.venttur.com/...` → el main detecta la cadena y dispara `Actualizar Link enviado` → `Link asesoría enviado = true` + arranca Rescate Post-Link |

### Tools técnicas del agente (efectos de estado)

- **`crear_contacto`** (toolWorkflow → `cZUNKQyZNOHy5twQ`): al capturar nombre+apellido. Marca `Contestan 1er mensaje = true` en Leads + crea contacto Clientify.
- **`elevar`** (toolHttpRequest → ManyChat `sendFlow` `content20250716130059_365663`): si el lead pide humano/emergencia, o repite el **mismo** mensaje 2+ veces **consecutivas e inmediatas**. Asigna la conversación a un agente humano en Live Chat.
- **`contestan_2do`**: ⚠️ INCIERTO — el prompt instruye *"Si el usuario responde a tu segundo mensaje… activa la herramienta contestan_2do"*, **pero ese tool NO existe como nodo cableado en `wf-venttur-main`** (impacto: hay una instrucción a una tool inexistente; la métrica "contestan 2do mensaje" o no se captura, o vive en otro lado no identificado — resolver antes de migrar la lógica de scoring a GHL).

### Anti-loop de infraestructura (no es un estado, pero corta el flujo conversacional)

Antes de llegar al agente, el main compara el mensaje entrante contra el último guardado en la tabla de apoyo (`Tabla apoyo (ignorar)`). **Si el texto es idéntico al anterior, el flujo se DETIENE** (nodo `Repetido?`, salida TRUE vacía) — el agente no procesa reenvíos/duplicados de ManyChat. Es distinto de la regla de elevación por repetición (esa la evalúa el LLM).

---

## 3. Capa A (pre-conversación) — Estados de outreach proactivo y nurturing

El lead puede recibir mensajes **antes de conversar**, desde dos motores automáticos. Ambos siembran **memoria sintética** en `n8n_chat_histories` para que Mauricio no re-salude ni repregunte datos cuando el lead responde.

### 3.1 Outreach Form Meta — tri-toque (workflow `CUuFxbst3iHpgeXS`, LIVE)

Leads que llenan un formulario de **Meta Lead Ads** (form "Boarding_Schools_Venttur_2026-test-2") caen en un Google Sheet; un Sheets Trigger los ingesta a Airtable (upsert por `Folio`) y un cron los procesa en 3 toques por WhatsApp/ManyChat.

| Estado | Trigger | Cadencia real (confirmada) | Efecto |
|--------|---------|----------------------------|--------|
| **Touch 1 pendiente** | Lead creado con `Touch 1 programado at = NOW()` (v4: **sin +1h**) | El cron lo levanta en el próximo ciclo tras la creación (**≈0h**) | `createSubscriber` ManyChat + `sendFlow` Touch 1 (`content20260612151152_969589`) |
| **Touch 2 pendiente** | `Toques enviados = 1` | **+24h** desde `Touch 1 programado at` | `sendFlow` Touch 2 (`content20260616231914_193459`) |
| **Touch 3 pendiente** | `Toques enviados = 2` | **+72h** desde `Touch 1 programado at` | `sendFlow` Touch 3 (`content20260616231947_185709`) |

**Guards de exclusión del cron** (`Get Leads Pendientes`): sale de la cadencia si `Agendan cita = TRUE`, `Última actividad` ≠ BLANK (=ya respondió), `Toques enviados ≥ 3`, `Origen ≠ 'Form Meta'`, o sin `Touch 1 programado at`. Cada toque incrementa `Toques enviados` (+1), setea `Outreach Form Meta enviado = true` y `Ultimo toque at`. Los 3 toques se anclan **todos** a `Touch 1 programado at` (no incremental entre toques).

### 3.2 Nurturing 4-toques por programa (6 flows ManyChat)

Disparado por el dispatcher `DyrDumQgb6S4zHsS` (ver §5.2) para leads que **NO recibieron link de asesoría**. Estructura idéntica en los 6 flows: mensaje inicial → Wait 1 día → mensaje 2 → Wait 2 días → mensaje 3 → Wait 2 días → mensaje 4 (delays **0 / 1 / 3 / 5 días** acumulados).

| Flow ManyChat | Tag/programa | `flow_ns` |
|---------------|--------------|-----------|
| Boarding School | Boarding IA | `content20250718115245_638127` |
| Pathway | Pathway IA | `content20250718121921_967738` |
| Gap year | Gap Year IA | `content20250718122822_491460` |
| Año Académico | AA Familiar IA | `content20250718123255_243860` |
| Summer Camp | Summer Camp IA | `content20250718123847_652764` |
| Lead General (fallback) | sin programa | `content20250718124216_992343` |

Contenido educativo/consultivo largo (verbatim en `manychat-flows-content-2026-07-20.md`). Son nurturing de largo plazo, no de agendamiento.

---

## 4. Capa C — Estados de tracking / atribución (Meta CAPI)

Camino paralelo, no bloqueante, disparado en cada mensaje entrante. Dos ramas según cómo entró el lead:

| Estado | Discriminante | event_id | action_source | Señales de match | Config programa |
|--------|--------------|----------|---------------|------------------|-----------------|
| **FOLIO (landing)** | msg contiene `"Folio"` | `<folio>` (dedup real vs pixel navegador) | `website` | ph+fn+ln+fbc+fbp+ip+ua | dinámica `{Programa}=<extraído>` |
| **CTWA (WhatsApp directo)** | msg NO contiene `"Folio"` | `CTWA_<phone>_<ts>` (sin dedup) | `system_generated` | solo ph+fn+ln (hasheados) | **hardcodeada `{Programa}='BS'`** |

- **`CAPI Registro Folio`** (`9yCbynoKDt9hgiBq`, LIVE): la landing `go.venttur.com` postea al webhook `capi-registro-folio-venttur` en el clic-a-WhatsApp; guarda una fila en `Folios CAPI` con `fbc`/`fbclid`/`fbp`/`ip`/`user_agent`/`Timestamp`/`Landing URL` (la "huella" de Meta). CREATE puro sin dedup.
- **`Meta CAPI`** (`z98w2yWVEMOfifMl`): cruza el folio del mensaje contra `Folios CAPI`, hashea PII con SHA-256 en JS puro, y postea el evento `Lead` a Graph API v21.0 `/{pixel_id}/events`.
- **Pixels reales** (`programas-capi.csv`, confirmado): solo **2 pixels** en 4 filas. `BS`/`BSG`/`BSC` → "Boarding IA", pixel `228398216567258` (URLs `go.venttur.com/bs`, `/bs/girls`, `/bs/cats`). `HF` → "AA Familiar IA", pixel `24520910174237152` (`go.venttur.com/hf`).
- ⚠️ INCIERTO — Summer Camp, Pathway, Gap Year **no tienen fila en `Programas CAPI`** → su tracking CAPI es incierto (probablemente sin pixel configurado, o solo entran por la rama CTWA que fuerza `BS`). No asumir que existe atribución para esos programas (impacto: si Venttur mide conversión por programa vía Meta, esos 3 programas quedan sub-atribuidos o mal atribuidos al pixel de Boarding).

---

## 5. Capa B — Estados operativos por campos Airtable reales

Fuente de verdad del embudo. La tabla `Leads` (`[AIRTABLE_TABLE_ID]`, base `[AIRTABLE_BASE_ID]`) tiene **30 columnas**. Aquí las que definen estado.

### 5.1 `Estado conversación` (single-select — set completo CONFIRMADO)

Extraído del schema embebido en los workflows `Estado lead (Contestó)` y `Estado interrumpida (barrido)`. **Los 4 valores del single-select son:**

| Valor | Quién lo setea | Cuándo | Guarda |
|-------|----------------|--------|--------|
| **`Activa`** | ⚠️ opción **definida en el select pero NO escrita por ningún workflow** — 0/3819 leads la tienen | (nominalmente: lead recién creado) | En la práctica el estado de un lead nuevo/en-conversación es **BLANK** (3628 leads en blanco), no `Activa` |
| **`Contestó`** | `Estado lead (Contestó)` `b52CUYEkI2Ah3Xj6` | Por **cada mensaje entrante** del lead | Forward-only: no pisa si terminal |
| **`Cita confirmada`** | (proceso de agenda / manual) | Lead con cita confirmada | Estado **terminal** — nunca se degrada |
| **`Conversación interrumpida`** | `Estado interrumpida (barrido)` `H6qYB3Oj97bxaTCX` | Barrido horario: `Última actividad` > 24h, sin cita, no ya interrumpido | Idempotente (auto-excluido del filtro) |

> ✅ Esto resuelve el ⚠️ del brief sobre "el set completo de valores del single-select": son exactamente estos 4, confirmados por el schema Airtable embebido en dos workflows independientes. No existe un valor `Cita agendada` en el enum — "cita agendada" se representa con el **checkbox `Agendan cita`**, no con el select.
>
> **Distribución observada en `leads.csv` (3819 leads):** `Conversación interrumpida` 168 · `Cita confirmada` 13 · `Contestó` 10 · (vacío) 3628. ⚠️ INCIERTO — el valor **`Activa` está definido en el single-select pero NO aparece en ningún lead del snapshot (0/3819)**: es el default nominal que en la práctica queda vacío o se sobrescribe de inmediato; no se pudo confirmar en qué path se estampa realmente (impacto: bajo; al migrar a GHL, el estado "abierta/activa" probablemente se representa mejor por "sin `Estado conversación` + `Última actividad` reciente" que por el valor literal `Activa`). ✅ **RESUELTO (2026-08-17, verificado por API contra el n8n vivo):** `wf-estado-lead` **está
cableado y corriendo**. El main tiene el nodo `Estampar estado (Contestó)` habilitado como 3ª rama de
`Responder rápido ManyChat`, y `b52CUYEkI2Ah3Xj6` registró **18 ejecuciones, todas exitosas**. El
`active:false` es lo normal en un sub-workflow invocado por Execute Workflow, no indica que esté
apagado. Los 10 leads con `Contestó` se explican porque **el CSV es del 2026-07-24**, anterior al
cableado — no porque el escritor falle.

> ⚠️ **Consecuencia de despliegue que hay que atender:** a medida que `Última actividad` se pueble,
> `wf-estado-interrumpida` (`H6qYB3Oj97bxaTCX`, **activo**, barrido horario) va a empezar a marcar
> leads como `Conversación interrumpida` en masa, porque su filtro exige `Última actividad` no vacía
> + más de 24 h. **Desactivarlo 48 h** y revisar el criterio antes de que el campo se llene.

**Guarda forward-only (anti-downgrade), verbatim del Code de `b52CUYEkI2Ah3Xj6`:** un lead es "terminal" si `Agendan cita === true` **O** `Estado conversación === 'Cita confirmada'`. Si es terminal, `Contestó` NO pisa el estado (se preserva el actual). Si no, se estampa `Contestó`. Si el teléfono no existe → **no-op** (el alta lo inicializa en otro workflow).

⚠️ INCIERTO — edge case: si `Agendan cita = true` pero `Estado conversación = 'Conversación interrumpida'`, la guarda **preserva** "Conversación interrumpida" en vez de subir a "Contestó" (impacto: un lead que agendó puede quedar visualmente en "interrumpida"; los dos campos pueden desincronizarse — GHL debería unificarlos en una sola etapa).

### 5.2 Checkboxes y contadores de estado

| Campo | Tipo | Setea | Semántica de estado |
|-------|------|-------|---------------------|
| `Contestan 1er mensaje` | checkbox | `crear_contacto` (`cZUNKQyZNOHy5twQ`) / alta formulario (false) | El lead respondió el 1er mensaje / se materializó como contacto |
| `Link asesoría enviado` | checkbox | `Actualizar Link enviado` (`gRSMjzxggA4UePjz`) | El agente envió un link `promo.venttur.com/...` → arranca Rescate. **Sin timestamp** (ver ⚠️) |
| `Agendan cita` | checkbox | `Confirmación de agenda` (`2PSekVBxarsrnVBu`) | Cita agendada (evento creado en Google Calendar de un asesor) — **guard terminal** |
| `Asistió` | checkbox | (inferido: manual / proceso de agenda) | El lead asistió a la asesoría |
| `Outreach Form Meta enviado` | checkbox | `Outreach Form Meta` (`CUuFxbst3iHpgeXS`) | Ya recibió ≥1 toque de outreach proactivo |
| `Toques enviados` | number | idem | 0/1/2/3 — máquina de estados del tri-toque |
| `Ultimo toque at` / `Touch 1 programado at` / `Outreach Form Meta enviado at` | datetime | idem | Anclas de la cadencia |
| `Última actividad` | datetime | `Estado lead (Contestó)` | Timestamp UTC del último inbound — guard del barrido interrumpida |
| `Cualificado` | checkbox | dispatcher `DyrDumQgb6S4zHsS` (solo `true`) | Lead cumple los 3 criterios de scoring (idioma + escuela + edad) |
| `Lead Score` | number | `Outreach Form Meta` | Score numérico (ej. 100) del lead de form Meta |
| `Tipo lead` | select | `Outreach Form Meta` | `hot` / `warm` / `cold` — clasificación del lead de form Meta (distribución real en `leads.csv`, 3819 leads: cold 3510 · warm 181 · hot 128) |
| `Programa interés` | single-select | `crear_contacto` / dispatcher / atribución CTWA | Boarding IA / AA Familiar IA / Summer Camp IA / Pathway IA / Gap Year IA / Francia IA / Automatización - Comentarios / No definido |
| `Tipo` | select | dispatcher / outreach | `Padre/Madre` · `Estudiante` · `No especificado` |
| `Fuente lead` | single-select | atribución CTWA (`Mensajes anuncios`) / formulario | ~22 opciones (ad-set names, Web, Facebook - Instagram, etc.) |

⚠️ INCIERTO — `Link asesoría enviado` se marca `= true` **sin escribir ningún timestamp** ("Link asesoría enviado at" no existe / no se escribe). El Rescate se ancla al momento de invocación, no a un campo fecha (impacto: en GHL conviene agregar el timestamp para segmentación y para que los Wait steps sean auditables).

> ⚠️ **Enum definido vs. datos reales de `Programa interés`.** El enum del single-select embebido en los nodos Airtable tiene 8 valores (fila de arriba). Pero en `leads.csv` (3819 leads) la distribución observada es: `No definido` 1315 · `Pathway IA` 881 · `AA Familiar IA` 632 · **`Boarding School` 482** · `Boarding IA` 437 · `Summer Camp IA` 42 · `Gap Year IA` 25 · `Automatización - Comentarios` 5. Hallazgos: (1) **DOS grafías activas del mismo programa Boarding: `Boarding School` (482) y `Boarding IA` (437).** `Boarding School` NO figura en el enum de 8 capturado del schema, pero **lo escribe activamente el Outreach Form Meta** (`Crear Lead Nuevo` hardcodea `Programa interés='Boarding School'`) → los 482 ≈ los 483 leads con `Origen='Form Meta'` (casi 1:1). La vía conversacional/dispatcher escribe `Boarding IA`. No es legado, ambas se escriben hoy. El Rescate las captura igual (matchea por `contains "Boarding"`), pero **al migrar a GHL hay que unificar `Boarding School` → `Boarding IA`** (un single-select con exact-match las trataría como 2 programas). (2) `Pathway IA` es la cohorte de programa definido más grande (881) pese a no tener pixel CAPI ni template de rescate propio. (3) `No definido` (1315, ~34%) + `Automatización - Comentarios` (5) son los que caen en `RESCATE_PROGRAMA_NO_MAPEADO`. (4) `Francia IA` está en el enum pero es residual en datos.

### 5.3 Scoring / cualificación (dispatcher `DyrDumQgb6S4zHsS`)

8 horas después de la conversación, el dispatcher lee toda la memoria Postgres, la pasa a gpt-4o-mini (temp 0) y produce 5 salidas que estampan estado:
- **`tags`** → `Programa interés` (lista cerrada: Boarding/AA Familiar/Summer Camp/Pathway/Gap Year IA).
- **`tipo`** → `Tipo` (Padre/Madre default).
- **`resumen`** → nota "Resumen" en Clientify.
- **`asesoria`** ("uno"/"cero") → **gate**: si recibió link, NO nurturea.
- **`cualificado`** ('1' solo si: sabe 2º/3º idioma + escuela privada bilingüe + rango de edad por programa) → `Cualificado = true` (solo estado positivo, nunca setea false).

> **Nota:** el "4-toques" NO vive en n8n — este dispatcher envía **un solo** `sendFlow`; la cadencia de 4 mensajes vive dentro de cada flow ManyChat (§3.2).

---

## 6. Cruce entre plataformas — cómo se une el estado

### 6.1 Foreign keys (confirmadas por los filterByFormula de los workflows)

```
Airtable Leads.id  = Airtable Leads.Telefono  = teléfono sin "+"   (primary key natural)
Airtable Leads.ID Clientify  ──1:1──►  Clientify contact.id
Airtable Leads.ID Manychat   ──────►  ManyChat subscriber_id
Airtable Leads.Folio         ──────►  Airtable Folios CAPI.Folio  ──► Meta pixel
Airtable Leads.Telefono (sin +, con quirk MX 52→521)  ──►  Supabase n8n_chat_histories.session_id
```

El **teléfono es la clave universal**. Airtable lo guarda **sin `+`**; Clientify **con `+`**; Supabase **sin `+` pero con quirk MX**.

### 6.2 Identidad múltiple del mismo lead

Un lead vive simultáneamente como: fila en `Leads` (estado operativo), fila(s) en `Folios CAPI` (tracking), contacto en Clientify (+deal manual), subscriber en ManyChat (tags + custom fields), y sesión en Supabase (memoria). No hay un ID maestro — todo se reconcilia por teléfono.

### 6.3 ManyChat (cuenta "Venttur | Agente de IA", plan Pro, TZ America/Montevideo)

- 16 flows · 5 tags · 13 custom fields.
- Tags de estado relevantes: `LINK_ABANDONADO_FRIO` (tag_id 87501917), `RESCATE_PROGRAMA_NO_MAPEADO` (87501935), `seguimiento_agenda`.
- **Debounce de 20 s** en flow "Recibir mensajes" (buffer anti-fragmentación antes de llamar al webhook n8n).
- **Número directo de Rodrigo** en flow "Agenda": **+52 1 33 1944 2476** (dato de negocio a preservar).
- ⚠️ INCIERTO — flow "Elevar": `Pause all automations Forever` + `Assign conversation` + **"Notify Assignees: 0 people"** → posible bug: el equipo humano podría no enterarse de las elevaciones (impacto crítico: leads que piden humano quedarían sin atención; verificar en ManyChat con Max/Mauricio antes de migrar).

### 6.4 Supabase (memoria — `n8n_chat_histories`, 34.725 filas)

- `session_id` = teléfono sin `+`. **Quirk MX confirmado:** números `52XXXXXXXXXX` (12 díg.) deben ser `521XXXXXXXXXX` (13). Fix + backfill YA aplicados en producción.
- `message` jsonb `{type: human|ai|system}` (los `system`/`ai` sintéticos vienen de outreach/rescate).
- Tablas `documents` (0 filas, vestigio RAG) y `n8n_chat_histories_plus_backup` (2 filas) son irrelevantes. `workflow_errors` no está en este Supabase.

---

## 7. Diagrama de transiciones (actualizado)

```
                                   ┌──────────────────────────────────┐
   ENTRADA A                       │        ENTRADAS AL SISTEMA        │
                                   └──────────────────────────────────┘
   (a) Form Landing         (b) Form Meta Lead Ads      (c) CTWA (clic anuncio→WA)     (d) DM directo
        │                          │                          │                            │
        ▼                          ▼                          ▼                            ▼
  ┌────────────┐           ┌──────────────┐          ┌──────────────┐            ┌──────────────┐
  │ Lead creado│           │ Lead creado  │          │ Lead creado  │            │ Lead creado  │
  │ (Clientify │           │ Origen=Form  │          │ Folio=N/A(WA)│            │ por agente   │
  │  +Airtable)│           │ Meta,Toques=0│          │ rama CTWA CAPI│            │ crear_contacto│
  └─────┬──────┘           └──────┬───────┘          └──────┬───────┘            └──────┬───────┘
        │                         │                         │                           │
        │              ┌──── OUTREACH TRI-TOQUE ────┐       │                           │
        │              │ T1(~0h) → T2(+24h) → T3(+72h)│      │                           │
        │              │ +memoria sintética Postgres │      │                           │
        │              └──────────────┬──────────────┘      │                           │
        │                             │                     │                           │
        └─────────────┬───────────────┴─────────────────────┴───────────────────────────┘
                       ▼
          ┌────────────────────────────┐        ┌──────────────────────────────┐
          │   CONVERSACIÓN CON MAURICIO │◄───────│  Meta CAPI (evento Lead)      │
          │   Estado conversación=Activa│        │  paralelo, cada mensaje       │
          │   Diagnóstico 7 pasos       │        └──────────────────────────────┘
          └──────────────┬─────────────┘
                         │  (cada inbound → Estado=Contestó, Última actividad=now)
             ┌───────────┼───────────────────────────────┐
             ▼           ▼                                ▼
      ┌────────────┐ ┌──────────────┐            ┌──────────────────┐
      │ Pide humano│ │ Envía LINK   │            │ Silencio > 24h    │
      │  →ELEVAR   │ │ asesoría     │            │ (barrido horario) │
      │ (a humano) │ │ Link=true    │            │ Estado=Conversación│
      └────────────┘ └──────┬───────┘            │   interrumpida    │
                            │                    └──────────────────┘
              ┌─────────────┴──────────────┐
              ▼                            ▼
     ┌──────────────────┐        ┌──────────────────────┐
     │ RESCATE POST-LINK│        │ NO envió link →       │
     │ F1(+45min) chk   │        │ NURTURING 4-toques    │
     │ F2(+24h)  chk    │        │ por programa (0/1/3/5d)│
     │ +memoria sintética│       │ (gate: asesoria=cero) │
     └────────┬─────────┘        └──────────────────────┘
              │ (¿Agendan cita?)
        ┌─────┴─────┐
        ▼           ▼
  ┌──────────┐ ┌─────────────────────┐
  │ AGENDÓ   │ │ NO agenda tras F2    │
  │ Agendan  │ │ tag LINK_ABANDONADO_ │
  │ cita=true│ │ FRIO (frío, terminal)│
  └────┬─────┘ └─────────────────────┘
       ▼
  ┌────────────────────┐      ┌──────────────────────────────────────────┐
  │ CONFIRMACIÓN AGENDA │      │  CAPA D — PIPELINE COMERCIAL CLIENTIFY     │
  │ (Google Cal trigger)│─────►│  (MANUAL, inferido):                      │
  │ Estado=Cita         │      │  Solicitud de cita → AGENDÓ REUNIÓN →      │
  │  confirmada         │      │  Cita de Ventas concretada → Gracias por   │
  │ WhatsApp confirm +  │      │  asistir → Seguim. Día 1/5/10/15/20 →      │
  │ link Meet + Rodrigo │      │  Won / Lost                                │
  └────────────────────┘      └──────────────────────────────────────────┘
       │
       ▼ (post-cita)
  ┌──────────┐   ┌──────────────────────┐
  │ Asistió  │   │ Seguimiento agenda 48h│  (single-touch, si no agendó tras link)
  │ =true    │   │ flow_ns ...140983     │
  └──────────┘   └──────────────────────┘
```

**Estados de error / borde (fuera del flujo principal):**
- `RESCATE_PROGRAMA_NO_MAPEADO` — el Rescate no reconoce el `Programa interés` (Code Fase 1 mapea solo 5 programas; "Estudio y Trabajo" cae aquí y **nunca recibe rescate**).
- `link_no_identificado` — `Actualizar Link enviado` no matchea la URL (variación tipográfica) → igual marca `Link enviado` y dispara Rescate.
- CAPI fallido — regex de folio/prog no matchea → aborta → errorWorkflow.

---

## 8. Capa D — Pipeline comercial Clientify (gestión manual)

Volumen real confirmado: **6.968 contactos · 2.338 deals · 266 companies · 22 custom fields.**

**Pipelines de venta (deals) reales:** "Campaña Internados Erika" (1.024 deals), "VENTAS EMA METODOLOGÍA" (319), "Campaña Australia Abril 25" (291), "Venta SPE - Internados" (172), etc.
**Distribución por status:** Expired 1.875 · Lost 381 · Open 50 · Won 32.
**Stages observados:** "AGENDÓ REUNIÓN", "Cita de Ventas concretada", "Día 15/20 Seguimiento", "Gracias por asistir", y seguimientos Día 1/5/10/15/20.

**Interpretación (inferido):** este es el **embudo comercial post-agendamiento** que el equipo Venttur gestiona **a mano** en Clientify. Los workflows n8n solo escriben `contacts`/`tags`/`notes` en Clientify — **nunca `deals`/`companies`/`custom-fields`**. Por eso:

> ⚠️ INCIERTO — que el pipeline de deals sea 100% manual es una inferencia fuerte (basada en que cero workflows tocan deals) pero no está confirmada con el equipo Venttur (impacto: la migración a GHL Opportunities necesita saber qué evento real dispara cada movimiento de etapa — hoy no hay automatización que portar, solo un proceso humano a documentar con el cliente).

**Veredicto de migración:** Clientify → **REMOVE** (se absorbe en GHL CRM/Opportunities). La capa comercial (deals) se re-modela como un Pipeline GHL con stages equivalentes.

---

## 9. Campos que definen cada estado (tabla multi-fuente)

| Estado del lead | Airtable Leads | Airtable Folios/Prog CAPI | ManyChat | Supabase | Clientify |
|-----------------|----------------|---------------------------|----------|----------|-----------|
| **Lead nuevo (landing/form)** | fila creada, `Contestan 1er msg=false` | — | subscriber | — | contact creado + tag programa |
| **Lead Form Meta pendiente** | `Origen=Form Meta`, `Toques=0`, `Lead Score`, `Tipo lead` | — | (aún no) | — | — |
| **Lead CTWA** | `Folio='N/A (WA)'`, `fbclid='-'` | evento CAPI `system_generated`, pixel BS | subscriber | — | — |
| **CAPI folio enviado** | `Folio`+`fbclid` estampados | `fbtrace_id` presente en Folios CAPI | — | — | — |
| **En conversación** | `Estado conversación` BLANK (o `Contestó` si estado-lead corrió) | — | custom fields parte1/2/3 | filas human/ai | — |
| **Contestó** | `Estado conversación=Contestó`, `Última actividad` | — | — | — | — |
| **Cualificado** | `Cualificado=true`, `Tipo`, `Programa interés` | — | `programa_interes` | — | tag programa + nota Resumen |
| **Link enviado** | `Link asesoría enviado=true` | — | tag `<prog>_link_enviado` | +memoria sintética (rescate) | — |
| **En rescate** | `Agendan cita=false` (chequeado) | — | custom field msg rescate | +system/ai sintéticos | — |
| **Abandonado frío** | — | — | tag `LINK_ABANDONADO_FRIO` | — | — |
| **Interrumpida** | `Estado conversación=Conversación interrumpida` | — | — | — | — |
| **Cita agendada** | `Agendan cita=true` | — | — | — | (deal → AGENDÓ REUNIÓN, manual) |
| **Cita confirmada** | `Estado conversación=Cita confirmada` | — | flow "Agenda" (nº Rodrigo) | — | — |
| **Asistió** | `Asistió=true` | — | — | — | (deal → Cita concretada, manual) |
| **Ganado/Perdido** | — | — | — | — | deal Won/Lost (manual) |

---

## 10. Tiempos típicos del ciclo (confirmados por los workflows)

| Transición | Tiempo | Mecanismo (fuente) |
|------------|--------|--------------------|
| Landing/form → lead creado | Inmediato | Webhook / Sheets Trigger |
| Lead Form Meta → Touch 1 | **≈0h** (próximo ciclo del cron) | `Touch 1 programado at = NOW()` (v4) |
| Touch 1 → Touch 2 | **+24h** desde ancla | filterByFormula outreach |
| Touch 2 → Touch 3 | **+72h** desde ancla (no +24h más) | filterByFormula outreach |
| Nurturing por programa (4 toques) | **0 / +1d / +3d / +5d** | Waits internos del flow ManyChat |
| Mensaje entrante → estado `Contestó` | Inmediato (no bloqueante) | `Estado lead (Contestó)` |
| Silencio → `Conversación interrumpida` | **>24h**, detectado en ≤1h | Barrido horario `H6qYB3Oj97bxaTCX` |
| Link enviado → Rescate F1 | **+45 min** | Wait `mkEP1qFN7MVb9qP0` |
| Rescate F1 → F2 | **+24h** | Wait (total ~24h45m link→frío) |
| Link enviado → Seguimiento agenda | **+48h** (single-touch) | `Seguimiento agenda` `DZlSEQS5qzX1Y01K` (⚠️ ver nota) |
| Conversación → dispatcher scoring/nurturing | **+8h fijas** | Wait `DyrDumQgb6S4zHsS` |
| Cita agendada → confirmación WhatsApp | ≤1 min (polling Calendar) | `Confirmación de agenda` |

**Ciclo completo (link enviado → abandonado frío, sin respuesta):** ~24h 45m.
**Ciclo (form Meta → 3er toque, sin respuesta):** ~72h.
**Ciclo (form → cita):** variable (minutos a días).

> ⚠️ INCIERTO — coexisten DOS mecanismos post-link: Rescate Post-Link (45min+24h, activo) y "Seguimiento agenda" (48h single-touch, `active:false` + nodo placeholder "Replace me with your logic" sin limpiar → probablemente stub/legacy no productivo). No está confirmado si el de 48h corre en producción (impacto: en GHL conviene consolidar ambos en una sola secuencia de nurture post-link).

---

## 11. Propuesta de pipeline GHL

Formalizar las capas A+B+D en **un** Pipeline GHL de Opportunities con etapas explícitas, alineado a los campos reales:

```
[Nuevo Lead] → [Contactado] → [En diagnóstico] → [Cualificado] → [Link enviado / En rescate]
   → [Cita agendada] → [Cita confirmada] → [Asistió] → [En seguimiento] → [Ganado]
                                                          ↘ [Abandonado frío]  ↘ [Perdido]
```

| Etapa GHL | Equivalente actual (campo/estado real) | Trigger de entrada |
|-----------|----------------------------------------|--------------------|
| **Nuevo Lead** | Alta en `Leads` (form / CTWA / Form Meta / DM) | Contacto creado |
| **Contactado** | `Contestan 1er mensaje=true` / outreach enviado | Tool `crear_contacto` o Touch 1 |
| **En diagnóstico** | `Estado conversación` BLANK o `Contestó` (⚠️ `Activa` no se puebla en datos) + `Última actividad` reciente | Mensaje entrante (Conversations) |
| **Cualificado** | `Cualificado=true` **o** `Tipo lead ∈ {hot, warm}` (no solo `hot` — `warm` son 181 leads, la 2ª cohorte de scoring) | Score del dispatcher / form Meta |
| **Link enviado / En rescate** | `Link asesoría enviado=true` | Envío del link `promo.venttur.com/...` |
| **Cita agendada** | `Agendan cita=true` | Appointment booked (GHL Calendars) |
| **Cita confirmada** | `Estado conversación=Cita confirmada` | Appointment confirmed |
| **Asistió** | `Asistió=true` | Appointment showed |
| **En seguimiento** | deals Día 1/5/10/15/20 (Clientify manual) | Post-asistencia |
| **Ganado / Perdido** | deal Won/Lost (Clientify manual) | Decisión comercial |
| **Abandonado frío** | tag `LINK_ABANDONADO_FRIO` | Rescate F2 sin respuesta |

**Ventajas del pipeline explícito en GHL:**
1. Un solo lugar para leer el estado (no cruzar 4 plataformas por teléfono).
2. Workflows GHL disparan por cambio de etapa (nurturing, rescate, confirmación) nativamente.
3. Métricas de conversión por etapa (el `Correo Semanal` hoy consume esas cifras pre-agregadas de Airtable).
4. `Última actividad` deja de ser un campo frágil que hay que estampar a mano — GHL lo mantiene nativo → simplifica el barrido "interrumpida" y el Estado "Contestó".
5. La memoria sintética (Supabase) desaparece si el agente conversacional se migra a GHL Conversations (el historial vive nativo) — elimina el quirk 52→521 y los backfills.

**A resolver con Venttur antes de migrar (bloqueantes de diseño):**
- Confirmar que el pipeline comercial Clientify (deals) es manual y mapear qué evento dispara cada stage en GHL.
- Resolver el gap del tool `contestan_2do` (instruido pero inexistente): implementar o descartar la métrica.
- Confirmar los pixels/programas de CAPI para Summer Camp / Pathway / Gap Year (hoy sin fila en `Programas CAPI`).
- Verificar el flow "Elevar" (Notify Assignees 0 people) — riesgo de escalamientos silenciosos.
- Consolidar Rescate Post-Link + Seguimiento agenda 48h en una sola secuencia.

---

## Marcadores de incertidumbre

| Ítem | Qué falta confirmar | Impacto | Owner / cómo resolver |
|------|---------------------|---------|-----------------------|
| **Pipeline comercial Clientify manual** | Que los deals (2.338) se mueven 100% a mano; qué evento dispara cada stage | Alto — define cómo se re-modelan las Opportunities GHL y qué se automatiza | Reunión con Venttur (Max/equipo comercial) + revisar si hay automations Clientify nativas fuera de n8n |
| **Tool `contestan_2do` inexistente** | Dónde (o si) se captura "contestan 2do mensaje"; el prompt instruye una tool no cableada | Medio — métrica de embudo potencialmente perdida | Revisar ManyChat/otros workflows; decidir implementar o descartar en GHL |
| **Pixels CAPI de Summer/Pathway/Gap Year** | Si tienen pixel/atribución; hoy sin fila en `Programas CAPI`, CTWA fuerza `BS` | Medio — atribución Meta sub/mal-reportada para 3 programas | Confirmar con Venttur el setup de pixels por programa |
| **Flow "Elevar" — Notify Assignees 0 people** | Si el equipo humano recibe la notificación de elevación | Alto — leads que piden humano podrían quedar sin atención | Verificar en ManyChat con Max/Mauricio |
| **`programa_wpp` (asunción del brief/mayo)** | El campo NO existe en ningún workflow; la rama CTWA hardcodea `{Programa}='BS'` | Medio — el ruteo CTWA por programa dinámico que se asumía no existe | Confirmar si CTWA debe rutear por campaña/programa o queda mono-pixel |
| **Doble mecanismo post-link (Rescate vs Seguimiento 48h)** | Si `Seguimiento agenda` (48h, `active:false`, con placeholder) corre en prod | Bajo/medio — riesgo de doble contacto o de lógica muerta | Revisar en n8n vivo; consolidar en GHL |
| **`Link asesoría enviado` sin timestamp** | No hay "Link enviado at"; el Rescate se ancla a la invocación | Bajo — dificulta segmentación/auditoría en GHL | Agregar timestamp al migrar |
| **Edge case guarda forward-only** | `Agendan cita=true` + `Estado=Conversación interrumpida` → preserva "interrumpida" | Bajo — desincronización visual de estado | Unificar en una sola etapa de pipeline GHL |
| **"Estudio y Trabajo" sin rescate** | El Code del Rescate mapea 5 programas; ese cae en `PROGRAMA_NO_MAPEADO` y no recibe mensaje | Bajo/medio — un segmento de leads sin rescate | Definir tabla única programa→(mensaje,URL,tag) en GHL |
| **Quirk MX 52→521 en session_id** | Que no queden filas viejas (12 díg.) al migrar la memoria | Bajo — conversaciones huérfanas al cruzar por teléfono | Query §6 de `supabase-queries-venttur.md` antes de migrar |
| **Confirmación de agenda — refs rotas** | Paths de Diego/Andrés referencian nodos inexistentes; solo Rodrigo consistente | Medio — confirmaciones de cita solo funcionarían para Rodrigo | Verificar en n8n vivo; re-modelar con Appointment trigger GHL |
| **Secretos hardcodeados** | Tokens Clientify/ManyChat + API key OpenAI en claro en varios JSON | Alto (seguridad) — no arrastrar al handoff | Rotar y mover a credenciales antes de exportar/migrar |
