# Cierre de Etapa 1 → Etapa 2 — Preguntas para dejar todo 100% definido (VTR → GHL)

> 🔒 **USO INTERNO (la agencia / la agencia) — NO compartir con el cliente.** Este documento tiene referencias al repo, verificaciones técnicas y decisiones de arquitectura. **Estado al 2026-08-18:** `cuestionario-venttur-2026-07-24.md` ya NO es la versión en blanco para mandar — es el **registro firmado por Mauricio García (2026-08-17)** con las 12 respuestas. Lo que hay que mandarle al cliente ahora es `puntos-abiertos-ronda-2-2026-08-18.md`. Este archivo es el máster de seguimiento: **A1..A11 ya están volcadas** con las respuestas del cliente; A12..A32 (Bloques B/C/D) siguen siendo verificaciones y decisiones de la agencia, pendientes.

> **Qué es esto:** el listado único y lineal de TODO lo que quedó abierto, incierto o ambiguo tras deducir la lógica actual del sistema (Etapa 1). Consolida y deduplica los "Marcadores de incertidumbre" de los 6 documentos de `01_logica_actual/` + las decisiones del doc 06. Si respondés cada `A#`, el sistema queda completamente caracterizado y podemos pasar a Etapa 3 (diseño GHL) sin supuestos.
>
> **Cómo usarlo:** completá cada `A#:` debajo de su pregunta. Algunas son decisiones tuyas (la agencia), otras hay que **consultarlas con Mauricio / el equipo de Venttur**, y otras las **verifica la agencia en el n8n/ManyChat vivo** (ahí solo confirmás el resultado). No hace falta responder en orden. Lo que no sepas todavía, dejalo marcado `PENDIENTE (consultar a X)`.
>
> **Cuando esté completo:** avisame y actualizo los 6 documentos de `01_logica_actual/` (y el `ESTADO_MIGRACION.md`) para reflejar tus respuestas, cerrando Etapa 2.

**Leyenda de responsable (tag entre corchetes):**
- `[MAURICIO/VENTTUR]` — decisión de negocio; probablemente hay que preguntarle al cliente.
- `[LA AGENCIA-VIVO]` — verificación técnica contra el n8n / ManyChat / Clientify vivo; la agencia/la agencia lo confirma (el export puede estar desactualizado).
- `[ARQUITECTURA-GHL]` — decisión de diseño para Etapa 3; la definís vos (la agencia) con criterio técnico, a veces con input del cliente.
- `[HIGIENE]` — acción de limpieza/seguridad que la agencia ejecuta; solo confirmá que estás de acuerdo / cuándo.

**Prioridad:** 🔴 bloquea el diseño de Etapa 3 · 🟡 importante, no bloqueante · 🟢 menor / recuperable.

---

## BLOQUE A — Decisiones de negocio (consultar con Mauricio / Venttur)

### Q1 🔴 `[MAURICIO/VENTTUR]` — Pipeline comercial de Clientify (2.338 deals): ¿se migra o no?
**Contexto:** Clientify tiene 6.968 contactos + **2.338 deals** en pipelines de venta ("Campaña Internados Erika" 1.024, "VENTAS EMA METODOLOGÍA" 319, etc.) que el equipo mueve **a mano** (ningún workflow n8n toca deals). La migración de *contactos* a GHL está clara; los deals son una decisión nueva y grande.
- (a) ¿Recreamos el embudo comercial post-agendamiento como **Pipeline de Opportunities en GHL**, o solo migramos los contactos y el equipo sigue gestionando la venta aparte?
- (b) Si se migra: ¿histórico completo (2.338) o solo los **Open (50) + Won (32)** y se archivan los Expired/Lost?
- (c) ¿Qué evento real dispara cada cambio de etapa hoy (para poder automatizarlo en GHL)?

**Ref:** doc 06 §B, N.1 · doc 03 §8. → actualiza doc 03, doc 06.

**A1:**

```
✅ RESPONDIDA — cuestionario cliente P10 (Mauricio, 2026-08-17).

(a) SE MIGRA. El pipeline comercial vive en GHL como Opportunities.
    Clientify deja de operar por completo ("el objetivo de la migración es
    tener todo en un solo lugar").
(b) HISTÓRICO COMPLETO: contactos + deals abiertos + ganados + perdidos.
    Textual: "Preferimos tener la data completa y limpiarla nosotros
    después, a perder información en la migración." → NO se archiva nada.
(c) Reconstrucción 1:1, SIN rediseño: "mismas etapas, mismos nombres, mismo
    orden. No queremos rediseñarlo en este momento; preferimos migrarlo
    igual y después nosotros depuramos lo que sobre desde adentro."
    → Las transiciones de etapa siguen siendo MANUALES (el equipo las mueve
    a mano, igual que hoy). No se automatiza ninguna en esta fase.

🆕 ENTREGABLE NUEVO QUE ESTA RESPUESTA CREA (la agencia):
   El cliente pide una AUDITORÍA DE MIGRABILIDAD vía la API de Clientify,
   entregada ANTES de apagar Clientify: qué es replicable y qué no
   (historial de conversaciones, archivos adjuntos, automatizaciones), para
   que ellos respalden por su cuenta lo que se pierda. Es un gate duro de
   cutover, no un nice-to-have.
```

### Q2 🔴 `[MAURICIO/VENTTUR]` — Taxonomía canónica de programas
**Contexto:** conviven varias taxonomías inconsistentes (enum Airtable, tags del clasificador, routing de rescate, links del prompt). Necesitamos UNA lista única de programas activos para modelar GHL.
- (a) ¿Cuál es la **lista canónica** de programas vigentes hoy?
- (b) ¿Siguen vigentes `Francia IA` y `Automatización - Comentarios` (están en el enum de Airtable pero ni el agente ni el nurturing los conocen)?
- (c) ¿"Estudio y Trabajo" es un programa vivo? (hoy es *código muerto*: el rescate no lo mapea y 0 leads reales lo tienen).
- (d) **Grafía canónica de cada programa:** hoy Boarding aparece con DOS grafías activas — `Boarding School` (482 leads, lo escribe el Outreach) y `Boarding IA` (437, lo escribe el agente). ¿Cuál es la oficial? (para normalizar antes de migrar).

**Ref:** doc 06 §D.1, N.5 · doc 05 §2.5 · doc 03 §5.2. → actualiza doc 01, 03, 04, 05, 06.

**A2:**

```
✅ RESPONDIDA — cuestionario cliente P1 (Mauricio, 2026-08-17). ⚠️ Con residuo en (d).

(a) LISTA CANÓNICA = 8 programas, todos activos, ninguno dado de baja:
      1. Internados (Boarding School)
      2. Intercambio académico con familias
      3. Viajes educativos
      4. Educación superior
      5. Campamentos de verano
      6. Cursos de idiomas en el extranjero
      7. Pathway Alemania
      8. Gap Year / Estudia y Trabaja

(b) `Francia IA` → NO ES PROGRAMA. Es un DESTINO que atraviesa varios
    programas (intercambio, internados, cursos de idiomas, educación
    superior). Se elimina del enum. Regla nueva del cliente: los destinos
    se registran como NOTA/comentario en el contacto, NUNCA como campo
    estructurado ni como programa.
    `Automatización - Comentarios` → no figura en la lista de 8; no es un
    programa comercial. Se trata como marcador interno de origen, no como
    programa. (Resuelto por omisión — confirmación de 10 segundos pendiente.)

(c) "Estudio y Trabajo" NO es un programa aparte: es el mismo que Gap Year
    (ver A3). El código muerto del rescate se resuelve FUSIONANDO las dos
    ramas en una, no agregando la que falta.

(d) 🔴 RESIDUO — GRAFÍA CANÓNICA SIN CERRAR, Y EL PROBLEMA CRECIÓ.
    La pregunta original era "¿`Boarding School` (482 leads) o `Boarding IA`
    (437)?". El cliente no eligió entre esas dos: nombró los 8 programas
    EN ESPAÑOL Y CON OTROS NOMBRES ("Internados", "Intercambio académico con
    familias", "Campamentos de verano"). O sea que la normalización ya no es
    elegir entre dos grafías de Boarding — es RENOMBRAR EL ENUM ENTERO y
    remapear los 919 leads de Boarding + el resto de las cohortes.
    → Va a la ronda 2. Propuesta por defecto: usar los 8 nombres en español
      tal cual los escribió Mauricio como valores del single-select de GHL,
      y mantener las grafías viejas solo como alias de migración.

🚨 HALLAZGO CRÍTICO QUE ESTA RESPUESTA DESTAPA — 3 de los 8 programas NO
   EXISTEN EN EL SISTEMA. Verificado por grep exhaustivo sobre todo el
   cliente (workflows, prompt, CSVs, flows ManyChat, docs):

   | # | Programa | Enum | Link agenda | Drip nurturing | Rama rescate | Pixel |
   |---|---|---|---|---|---|---|
   | 1 | Internados | ✅ | ✅ | ✅ | ✅ | ✅ |
   | 2 | Intercambio académico | ✅ | ✅ | ✅ | ✅ | ✅ |
   | 3 | **Viajes educativos** | ❌ | ❌ | ❌ | ❌ | ❌ |
   | 4 | **Educación superior** | ❌ | ❌ | ❌ | ❌ | ❌ |
   | 5 | Campamentos de verano | ✅ | ✅ | ✅ | ✅ | ❌ |
   | 6 | Cursos de idiomas | ❌ | ✅ | ❌ | ⚠️ muerta | ❌ |
   | 7 | Pathway Alemania | ✅ | ✅ | ✅ | ✅ | ❌ |
   | 8 | Gap Year / Estudia y Trabaja | ✅ | ✅ | ✅ | ✅ | ❌ |

   "Viajes educativos" y "Educación superior" tienen CERO huella: 0 hits en
   todo el repo fuera de este cuestionario. Consecuencia hoy, en producción:
   un lead que pregunta por educación superior no matchea ningún programa →
   el agente cae al fallback `agendar-ema`, que es el link de INTERNADOS con
   RODRIGO — programa equivocado y asesor equivocado (el cliente asignó
   Educación superior a Andrés). Además no recibe rescate (cae en
   `RESCATE_PROGRAMA_NO_MAPEADO`) ni drip propio.
   → Es scope nuevo de Etapa 3, no una corrección.
```

### Q3 🟡 `[MAURICIO/VENTTUR]` — Gap Year vs "Estudiar y Trabajar": ¿dos programas o el mismo?
**Contexto:** el prompt del agente tiene entradas solapadas: "Gap Year / Estudia y trabaja" → link `Estudiar-y-Trabajar-en-Australia` con **Diego**, y "Estudiar y trabajar" (cursos de idiomas) → link `EstudiaryTrabajar_Agendar` con **Andrés**. El agente puede mandar link/experto equivocado.
- ¿Son dos programas distintos o el mismo duplicado por error? Necesitamos un mapeo **1:1 canónico: programa → link → experto**.

**Ref:** doc 06 §D.2, N.6 · doc 04 · doc 05. → actualiza doc 04, 05, 06.

**A3:**

```
✅ RESPONDIDA Y CERRADA — cuestionario cliente P1 + P2 (Mauricio, 2026-08-17).

SON EL MISMO PROGRAMA. "Gap Year" y "Estudia y Trabaja" son dos nombres
comerciales del mismo producto: cursos vocacionales tipo VET (marketing,
emprendedurismo, diseño, fotografía, cocina, enfermería, childcare),
diplomados de 6 a 8 meses con permiso de trabajo legal en el destino. Se
usan indistintamente según lo que venda mejor. En el sistema = UN solo
programa.

Asesor: ANDRÉS (los dos nombres).

⚠️ OJO — esto NO colapsa las dos entradas del prompt. El cliente separa:
   - #8 Gap Year / Estudia y Trabaja = cursos VOCACIONALES (VET) → Andrés
   - #6 Cursos de idiomas en el extranjero = programa DISTINTO → Andrés
   El prompt actual conflaciona los dos ("Estudiar y trabajar (cursos de
   idiomas)"). Se desdoblan en dos programas con dos calendarios, ambos de
   Andrés.

DIEGO SALE DEL RUTEO AUTOMÁTICO por completo: trabaja leads orgánicos y
tráfico frío que él mismo genera, fuera del flujo del agente (supervisado
por Andrés). → Todas las entradas de Diego se eliminan del prompt, del
matriz de links y del `wf-confirmacion-agenda`.
   ⇒ Esto resuelve la mitad del Hallazgo 8 (paths rotos de confirmación):
     el path de Diego no hay que arreglarlo, hay que BORRARLO. Solo queda
     por arreglar el de Andrés.

Matriz vieja (a eliminar)         → Matriz nueva
  Gap Year → Australia → Diego    → Gap Year/Estudia y Trabaja → Andrés
  Cursos idiomas → ...  → Andrés  → Cursos de idiomas → Andrés (sin cambio)
```

### Q4 🔴 `[MAURICIO/VENTTUR]` — Tracking Meta (pixels) por programa
**Contexto:** la tabla `Programas CAPI` solo tiene **2 pixels**: Boarding (`228398216567258`, para BS/BSG/BSC) y AA Familiar (`24520910174237152`, HF). Summer Camp, Pathway y Gap Year **no tienen fila ni pixel** — pese a que `Pathway IA` es la cohorte de leads más grande (881).
- (a) ¿Summer Camp / Pathway / Gap Year tienen pixel/campaña Meta propios? ¿Cómo se mide su conversión hoy?
- (b) Si no tienen pixel, ¿está bien que esos programas NO reporten conversiones a Meta, o es un gap a cerrar?

**Ref:** doc 06 §D.1, N.5 · doc 03 §4 · doc 05 §2. → actualiza doc 05, 06.

**A4:**

```
✅ RESPONDIDA — cuestionario cliente P4 (Mauricio, 2026-08-17).

(a) HOY SOLO INTERNADOS (Boarding School) tiene campaña activa en Meta.
    Ningún otro programa está corriendo pauta. Por eso Summer Camp /
    Pathway / Gap Year no tienen fila ni pixel: NO ES UN BUG, es que no
    tienen campaña que medir.
    ⚠️ Nota: el pixel de AA Familiar (`24520910174237152`) queda como
      LEGADO — existe configurado pero su programa no tiene campaña activa.

(b) NO es un gap a cerrar hoy. PERO el cliente pone un requisito de diseño
    explícito: "pedimos que el sistema se construya desde el inicio con la
    capacidad de medir conversiones por programa de forma independiente,
    para no tener que rehacerlo cuando eso pase". Van a activar campañas de
    otros programas (sin fecha ni lista confirmada).
    → Requisito para Etapa 3: la atribución CAPI tiene que ser
      DATA-DRIVEN (fila por programa en la tabla de config), no hardcodeada.
      Agregar un programa = agregar una fila, nunca tocar un workflow.
```

### Q5 🔴 `[MAURICIO/VENTTUR]` — Leads por click-to-WhatsApp (CTWA)
**Contexto:** cuando un lead entra por un anuncio click-to-WhatsApp (sin folio), el workflow CAPI **hardcodea `{Programa}='BS'`** → todos los CTWA se atribuyen al pixel de Boarding. Además, `programa_wpp` (que se creía discriminante) no se usa en ningún lado.
- (a) ¿**Todas** las campañas CTWA son de Boarding (entonces el hardcode está OK), o hay CTWA de otros programas que hoy quedan mal atribuidos?
- (b) ¿Cuáles son los **keyword triggers** exactos de CTWA en ManyChat? (la API no los expone; los necesitamos para recrear la atribución en GHL). ¿La tabla `Mensajes anuncios` es la fuente de verdad de atribución, o hay lógica extra en ManyChat?

**Ref:** doc 06 §D.3/§D.4, N.7 · doc 02 T2 · doc 05 §1. → actualiza doc 01, 02, 05, 06.

**A5:**

```
✅ RESPONDIDA — cuestionario cliente P5 (Mauricio, 2026-08-17).

(a) SÍ, hoy todos los CTWA son de Internados, porque es la única campaña
    activa. → El hardcode `{Programa}='BS'` de la rama CTWA del CAPI
    (Hallazgo 4) ES CORRECTO HOY. Baja de "⚠️ bug o intencional" a
    "correcto por ahora, insostenible a futuro": en cuanto activen la
    segunda campaña, atribuye mal. Se reemplaza por lookup data-driven
    en Etapa 3 (ver A4b).

(b) 🟢 CERRADA POR OBSOLESCENCIA, no por obtención del dato. Los keyword
    triggers de CTWA seguimos sin tenerlos (la API de ManyChat no los
    expone) — pero la respuesta del cliente los vuelve innecesarios para
    el diseño destino, porque separa explícitamente las dos funciones que
    hoy están mezcladas:

      • MEDICIÓN/ATRIBUCIÓN → automática, desde el payload de referral que
        manda Meta. Interna, no le pregunta nada al lead. No necesita
        keywords.
      • CONVERSACIÓN → el programa lo determina lo que DIGA LA PERSONA,
        no el anuncio del que vino.

🔄 CAMBIO DE POLÍTICA IMPORTANTE (no era una pregunta, es una instrucción):
   "El agente NO debe asumir el programa, ni siquiera cuando el origen
   parezca evidente. Siempre debe preguntar y hacer descubrimiento."
   Razón del cliente: alguien puede entrar por un anuncio de Internados y
   estar buscando un año académico o info para un hijo de otra edad; si el
   bot lo da por hecho, el asesor recibe un lead mal calificado.
   → Impacta el system prompt del agente (§ diagnóstico) y anula cualquier
     precarga de `Programa interés` desde el anuncio hacia la conversación.
   → Beneficio colateral que el cliente nombra: con este enfoque, activar
     campañas de programas nuevos no requiere tocar nada.
```

### Q6 🟡 `[MAURICIO/VENTTUR]` — Landings (Mauricio)
**Contexto:** solo conocemos la estructura de 2 landings por sus workflows. Mauricio controla las landings.
- (a) ¿Cuáles son **todas** las landings activas y la URL de cada una?
- (b) ¿Qué campos manda el webhook de cada una? ¿Alguna manda campos extra (email, país, ciudad) que hoy se ignoran?
- (c) Los `utm_*` (utm_campaign = ID de campaña Meta, etc.) llegan embebidos en la URL pero **no se parsean a columnas** — ¿los queremos como campos del contacto en GHL?

**Ref:** doc 06 §D.5, N.8 · doc 05 §7 (Formulario). → actualiza doc 01, 02, 05, 06.

**A6:**

```
✅ RESPONDIDA — cuestionario cliente P6 (Mauricio, 2026-08-17). Cierra un pendiente de Etapa 0.

(a) INVENTARIO REAL — y una corrección de supuesto: los dos formularios NO
    corren en paralelo. El formulario nativo de Meta SUSTITUYÓ a la landing.

    • Formulario nativo de Meta (Internados) — LO ACTIVO HOY. La campaña
      lleva ahí, no a una web.
    • `go.venttur.com/bs` (Internados) — VIVA y funcionando al 100%, manda
      a WhatsApp. Hoy sin tráfico de campaña, pero los orgánicos que caen
      entran al sistema con normalidad.
    • Los demás 7 programas: SIN landing y SIN formulario (no tienen
      campaña). Cuando activen, aplica la misma lógica.

(b) CAMPOS POR RUTA (son distintos — esto importa):
    • Form Meta: nombre completo · email · teléfono · grado escolar ·
      cuándo quiere iniciar · nivel de inglés
    • Landing bs: nombre · apellidos · email · teléfono · país · ciudad
    → Requisito del cliente: el sistema tiene que tolerar que un lead
      llegue con información PARCIAL según por dónde entró, y completar lo
      que falte durante la conversación (enlaza con el descubrimiento de A5).

(c) 🟢 ABIERTO (menor) — los `utm_*` como campos del contacto en GHL no se
    preguntaron. Va a ronda 2. Default propuesto: sí, mapearlos.

🆕 TAREAS NUEVAS QUE ESTA RESPUESTA CREA:
   1. Redirigir el flujo de `go.venttur.com/bs` a GHL en lugar de ManyChat +
      Clientify. Textual: "No debe quedar como puerta muerta después de la
      migración."
   2. Las DOS rutas de entrada tienen que quedar funcionando e
      INTERCAMBIABLES: "si mañana decidimos volver al embudo con landing, o
      correr las dos en paralelo, el sistema debe adaptarse sin rehacerse.
```

### Q7 🟡 `[MAURICIO/VENTTUR]` — Agendamiento y expertos
**Contexto:** el flujo de confirmación de cita depende de la plataforma de agendamiento y de los datos de los asesores.
- (a) ¿Qué plataforma de agendamiento se usa (Calendly / cal.com / Google Calendar / booking propio)? (define cómo se migra el trigger de confirmación a GHL Calendars).
- (b) El número directo de Rodrigo en el mensaje de confirmación es **+52 1 33 1944 2476** — ¿sigue vigente?
- (c) ¿Cada experto (Rodrigo / Andrés / Diego) tiene su propio número/calendario, o es genérico?

**Ref:** doc 02 A1 · doc 06 §F.3, N.13, N.11 · doc 04 §E. → actualiza doc 02, 04, 06.

**A7:**

```
✅ RESPONDIDA — cuestionario cliente P2 + P3 (Mauricio, 2026-08-17).

(a) PLATAFORMA: hoy los enlaces de agenda viven en CLIENTIFY y quedan
    OBSOLETOS con la migración (no existen todavía los de reemplazo).
    Destino: 8 CALENDARIOS EN GHL, UNO POR PROGRAMA (3 → Rodrigo, 5 → Andrés).
    ⇒ Esto resuelve C-20 ("¿dónde nacen realmente las citas?") por decisión
      de estado destino: nacen en GHL Calendars, nativo. La pregunta de si
      hoy nacen en Clientify o en Google Calendar deja de bloquear el
      diseño, porque el trigger de confirmación se reconstruye sobre GHL.

    ⚙️ REQUISITO TÉCNICO DURO del cliente (no es preferencia):
       — Un calendario POR PROGRAMA, no por asesor. Razón: así el sistema
         sabe el programa desde el momento del agendamiento, sin etiquetado
         manual posterior; alimenta directo la medición por programa (A4).
       — Los calendarios de UN MISMO ASESOR deben COMPARTIR DISPONIBILIDAD
         REAL. Si alguien agenda "Internados" el martes 16:00, ese bloque
         desaparece también de "Intercambio académico" y "Campamentos".
         Sin dobles reservas.

(b) ✅ +52 1 33 1944 2476 SIGUE VIGENTE. Es el que se comparte al agendar.

(c) NINGÚN asesor tiene número propio: UN SOLO NÚMERO COMPARTIDO.

🚨 DATO NUEVO Y GRAVE, que no estaba en ningún doc: HOY OPERAN CON DOS
   NÚMEROS DISTINTOS A NIVEL SISTEMA.
     • Uno en ManyChat → el agente que conversa y agenda.
     • Otro en Clientify → desde donde salen los recordatorios de cita.
   Causa: el agente nunca se pudo conectar al chat de Clientify. Efecto:
   el lead agenda con un número y recibe el recordatorio desde otro.
   → Explica por qué los recordatorios "existen" según el cliente pero no
     aparecen en ningún workflow n8n nuestro: viven en Clientify, fuera de
     nuestro perímetro de análisis.
   → Objetivo del cliente: UN SOLO NÚMERO para conversación + confirmación
     + recordatorios.
```

### Q8 🟡 `[MAURICIO/VENTTUR]` — Nurturing 4-toques por programa
**Contexto:** hay 6 drips de nurturing (Boarding/AA/Gap Year/Pathway/Summer/Lead General) con 4 mensajes a delays **0 / 1 / 3 / 5 días**, disparados solo si el lead NO recibió link de asesoría.
- (a) ¿Los 6 flows y sus tiempos siguen vigentes, o hay ajustes de mensajes/timing a incorporar?
- (b) Para un lead con interés en **varios** programas, hoy el orden de prioridad es Pathway > Summer > AA Familiar > Boarding > Gap Year — ¿es intencional o hay que definir otra prioridad?

**Ref:** doc 06 §F.2, N.12 · doc 04 §D. → actualiza doc 02, 04, 06.

**A8:**

```
🟡 PARCIAL — cuestionario cliente P7 (Mauricio, 2026-08-17). NO alcanza para cerrar.

Respuesta textual completa: "Se deben implementar cambios — ver Reporte
la agencia - Agente WhatsApp Venttur - Agosto 2026.pdf."

⚠️ POR QUÉ NO ALCANZA — el cuestionario que el cliente respondió es la
   versión de 12 preguntas enviada el 2026-08-07. La P7 que contestó era la
   vieja ("¿siguen vigentes?"). La P7 reescrita el 2026-08-17 —la que pide
   OK explícito a bajar a máximo 2 toques globales y a priorizar el
   recordatorio de link por sobre el genérico— NUNCA LE LLEGÓ. Ver
   `puntos-abiertos-ronda-2-2026-08-18.md`.

Lo que sí se puede sostener: la respuesta delega en el Reporte la agencia 1, que
es la auditoría del propio Max. Las decisiones del 2026-08-17 (tope global
de 2, cadencia a n8n) son consistentes con lo que ese reporte recomienda.
Pero es delegación, no aprobación explícita de un cambio de política
comercial. Se pide OK por escrito antes del cutover.

(b) 🟡 ABIERTO — la prioridad entre programas cuando un lead tiene interés
    en varios (hoy: Pathway > Summer > AA Familiar > Boarding > Gap Year,
    orden aparentemente accidental) NO se preguntó. Va a ronda 2.
    Nota: con 8 programas y 3 sin drip, esta prioridad hay que redefinirla
    entera, no solo confirmarla.
```

### Q9 🟡 `[MAURICIO/VENTTUR]` — Reporte semanal (métricas)
**Contexto:** hay un workflow de "Correo semanal" que agrega métricas (leads, cualificados, tasa de conversión a cita, tasa de asistencia, "conversaciones no continuadas"). Su fuente y fórmulas exactas viven en la config de la tabla Airtable, no en el workflow.
- (a) ¿Se quiere mantener este reporte en GHL?
- (b) ¿Cómo se define exactamente **"Cualificado"**, **"Cita agendada"** y **"Conversación no continuada"** para el reporte? (necesario para reproducirlo 1:1).

**Ref:** doc 02 OP1 (Correo Semanal) · doc 05 §10. → actualiza doc 02, 05.

**A9:**

```
✅ RESPONDIDA — cuestionario cliente P11 (Mauricio, 2026-08-17). Con un conflicto a reconciliar.

(a) SÍ, se mantiene el reporte semanal.

(b) DEFINICIONES OFICIALES DEL CLIENTE (verbatim, para reproducir 1:1):

    • LEAD CALIFICADO — "El que continúa la conversación, contesta las
      preguntas del agente de manera favorable al perfil que buscamos y
      muestra interés real en el programa. No basta con que responda una
      vez: tiene que avanzar en el descubrimiento y encajar con el perfil."
      ⚠️ Es una definición CUALITATIVA. No es computable tal cual: hay que
        traducirla a un criterio duro (¿N respuestas? ¿campos completados?
        ¿el agente marca `Cualificado`?). Hoy existe el checkbox
        `Cualificado` en Airtable — proponer que ESE sea el criterio y que
        lo escriba el agente al cerrar el descubrimiento.

    • CITA = CITAS AGENDADAS, solamente. 🔻 SIMPLIFICACIÓN: las citas
      PRESENTADAS (asistencia real) SALEN del reporte — "las mide Max por
      su cuenta". → Se puede dejar de calcular la tasa de asistencia y el
      campo `Asistió` deja de alimentar el reporte (no se borra, deja de
      reportarse).

    • CONVERSACIÓN NO CONTINUADA — "Cuando el lead deja de contestar los
      mensajes de seguimiento. Se marca al agotarse la secuencia completa
      sin respuesta, aproximadamente a los 5 días."

🚨 DOS CONFLICTOS QUE ESTA DEFINICIÓN ABRE (resolver en Etapa 3, no bloqueantes):

   1. CONTRA EL SISTEMA VIVO: `wf-estado-interrumpida` (`H6qYB3Oj97bxaTCX`)
      estampa `Conversación interrumpida` a las >24 h de silencio. El
      cliente dice ~5 días. Son dos definiciones distintas del mismo
      estado, y la que corre en producción es la de 24 h.
      → O se mueve el barrido a 5 días, o se aceptan dos conceptos
        separados (interrumpida operativa 24h ≠ no continuada del reporte).

   2. CONTRA EL TOPE DE 2 TOQUES: la definición ancla en "al agotarse la
      secuencia completa (~5 días)". Si la secuencia se recorta a 2 toques,
      se agota antes y el ~5 días deja de valer. Hay que re-anclar la
      definición a la nueva cadencia.
```

### Q10 🟡 `[MAURICIO/VENTTUR]` — Métrica "contestan 2do mensaje"
**Contexto:** el prompt del agente instruye llamar a una tool `contestan_2do` **que no existe** cableada. La métrica hoy no se captura.
- ¿Importa medir "el lead respondió al 2do mensaje"? ¿La implementamos en GHL o la descartamos?

**Ref:** doc 06 §E.3, N.10 · doc 03 §2 · doc 05 §3. → actualiza doc 01, 02, 03, 05, 06.

**A10:**

```
🟡 RESUELTA POR OMISIÓN — no se preguntó, pero la respuesta a P11 la contesta de hecho.

El cliente enumeró las métricas que quiere en el reporte semanal: lead
calificado, citas agendadas, conversación no continuada. "Contestan 2do
mensaje" NO está en esa lista, y tampoco pidió agregarla.

→ PROPUESTA: DESCARTAR la métrica y eliminar la instrucción fantasma del
  system prompt (hoy el prompt manda invocar una tool `contestan_2do` que
  no existe cableada en ningún nodo — Hallazgo 3). Eliminar la instrucción
  es además una mejora en sí misma: sacar de un prompt la orden de llamar a
  una herramienta inexistente reduce ruido y riesgo de comportamiento raro.

⚠️ Nota: el campo `Contestan 1er mensaje` SÍ existe en Airtable y lo escribe
  el Outreach. No se toca. Lo que se descarta es el SEGUNDO.

Confirmación de bajo costo, va a ronda 2 como ítem 🟢.
```

### Q11 🔴 `[MAURICIO/VENTTUR]` — Timeline de la migración
**Contexto:** varias decisiones de scope dependen de la fecha objetivo.
- ¿Hay una fecha límite o ventana deseada para el cutover a GHL?

**Ref:** doc 06 §G (E.10). → actualiza ESTADO_MIGRACION.

**A11:**

```
✅ RESPONDIDA — cuestionario cliente P12 (Mauricio, 2026-08-17).

📅 FECHA OBJETIVO: 15 DE SEPTIEMBRE DE 2026, "a más tardar".

🔴 PRIORIDAD #1 IMPUESTA POR EL CLIENTE — REVISIÓN DE PORTABILIDAD DEL
   NÚMERO. Textual: "Les pedimos que la revisión de portabilidad sea LO
   PRIMERO que se atienda. Es el único punto que depende de un tercero
   (ManyChat) y puede convertirse en el cuello de botella de toda la
   migración. Necesitamos una respuesta rápida —viable o no— para tomar la
   decisión sin comprometer la fecha."

   Qué hay que responderles (3 cosas concretas):
     1. ¿Es viable migrar el número actual de ManyChat a GHL?
     2. ¿Qué requiere de su parte y en cuánto tiempo?
     3. Si hay que dar de alta uno nuevo: qué se pierde (historial,
        contactos, etiquetas) y cómo se maneja la transición.

   Decisión ya tomada por el cliente si la respuesta es mala: "Si la
   portabilidad no es viable o implica riesgo de downtime, preferimos
   número nuevo. Vale más eso que perder conversaciones o atorar la
   migración." → No hay que volver a consultarlo; alcanza con avisar.

⚠️ LECTURA DE RIESGO SOBRE LA FECHA (evaluación la agencia, 2026-08-18 = T-28 días).
   La fecha es agresiva contra el scope que las propias respuestas
   agrandaron, y hay 3 dependencias de terceros en el camino crítico:
     • Portabilidad del número → depende de ManyChat + Meta.
     • Migración Clientify → 6.968 contactos + 2.338 deals + 266 companies,
       sin migración automática entre Clientify y GHL (el cliente ya lo
       asume: "buena parte del trabajo será reconstrucción manual").
     • 3 programas nuevos sin ninguna infraestructura (ver A2) +
       8 calendarios con disponibilidad compartida.
   Etapas 3, 4 y 5 están todas por delante. Hay que decidir explícitamente
   si el 15/9 es cutover COMPLETO o cutover del canal + agente, con la
   migración del pipeline comercial en una segunda ola.
```

---

## BLOQUE B — Verificaciones en el sistema vivo (la agencia confirma en n8n/ManyChat/Clientify)

> Estos ítems surgen de que los **exports pueden estar desactualizados** respecto de lo que corre en producción (varios workflows figuran `active:false`, hay referencias a nodos que no existen, etc.). la agencia/la agencia lo verifica abriendo el n8n / ManyChat vivo. Anotá el resultado en cada `A#`.

### Q12 🔴 `[LA AGENCIA-VIVO]` — Flow "Elevar": ¿el equipo se entera de las elevaciones?
**Contexto:** el flow "Elevar" de ManyChat (que dispara el agente cuando un lead pide humano/emergencia) muestra **"Notify Assignees: 0 people"** en el screenshot. Si es real, los escalamientos a humano no le llegan a nadie → leads en limbo.
- ¿Es un bug de config real o un artefacto del screenshot? ¿Quién recibe hoy la notificación de elevación?

**Ref:** doc 06 §E.1, N.9 · doc 03 §6.3 · doc 04. → actualiza doc 01, 02, 03, 04, 06.

**A12:**

```
‹ escribí tu respuesta acá (reemplazá esta línea) ›
```

### Q13 🔴 `[LA AGENCIA-VIVO]` — Estado `active` real de los workflows
**Contexto:** en los exports figuran `active:false` (o modo testing): **Meta CAPI**, **Estado lead "Contestó"** (`b52CUYEkI2Ah3Xj6`), **Correo Semanal**. Pero hay evidencia de que corrieron (ej. 10 leads con `Estado=Contestó`, 168 con `interrumpida`).
- ¿Cuáles de estos están **realmente activos** en el n8n vivo hoy? (define qué dispara de verdad en el corte de migración).

**Ref:** doc 02 (active real) · doc 05 (wf-estado-lead) · doc 03 §5.1. → actualiza doc 01, 02, 03, 05.

**A13:**

```
‹ escribí tu respuesta acá (reemplazá esta línea) ›
```

### Q14 🔴 `[LA AGENCIA-VIVO]` — Confirmación de cita: ¿paths de Diego y Andrés rotos?
**Contexto:** en `wf-confirmacion-agenda`, los paths de Diego y Andrés referencian nodos que **no existen** en el export (`Obtener ID Manychat` / `...2`) — solo el path de **Rodrigo** parece consistente. Si es real, los leads que agendan con Diego/Andrés no reciben confirmación por WhatsApp.
- ¿Están rotos en el n8n vivo, o el export está viejo y en prod funcionan los 3?

**Ref:** doc 06 §E.5, N.11 · doc 02 A1 · doc 05. → actualiza doc 02, 05, 06.

**A14:**

```
‹ escribí tu respuesta acá (reemplazá esta línea) ›
```

### Q15 🟡 `[LA AGENCIA-VIVO]` — Bug de tag en Clientify (Actualizar Link enviado)
**Contexto:** `wf-actualizar-link-enviado` referencia `.variable` (inexistente; debería ser `.tag`) al etiquetar en Clientify → los contactos podrían quedar con un tag **vacío**.
- ¿Los contactos se etiquetan correctamente en Clientify, o el tag llega vacío?

**Ref:** doc 01 / doc 05 (tag Clientify). → actualiza doc 01, 05.

**A15:**

```
‹ escribí tu respuesta acá (reemplazá esta línea) ›
```

### Q16 🟡 `[LA AGENCIA-VIVO]` — ¿Dónde se calcula `Lead Score` / `Tipo lead` (hot/warm/cold)?
**Contexto:** los campos existen (real: cold 3510 · warm 181 · hot 128) pero **el cálculo no está en el workflow de outreach** — vive en otro lado (posible automation de Airtable, fórmula, o versión no capturada del workflow).
- ¿Dónde y con qué regla se calcula el scoring hot/warm/cold?

**Ref:** doc 05 §4.4 · doc 03 §5.2. → actualiza doc 03, 05.

**A16:**

```
‹ escribí tu respuesta acá (reemplazá esta línea) ›
```

### Q17 🟡 `[LA AGENCIA-VIVO]` — ¿Dónde se setea `Estado conversación = 'Cita confirmada'`?
**Contexto:** `Confirmación de agenda` solo setea `Agendan cita = true`; ningún workflow analizado escribe el valor `'Cita confirmada'` del single-select — pero 13 leads lo tienen. Ese estado es el "terminal" que protege la lógica anti-downgrade.
- ¿Qué proceso/workflow lo escribe? (manual, automation Airtable, u otro workflow).

**Ref:** doc 02 A1 · doc 03 §5.1. → actualiza doc 02, 03.

**A17:**

```
‹ escribí tu respuesta acá (reemplazá esta línea) ›
```

### Q18 🟡 `[LA AGENCIA-VIVO]` — Cron del Outreach: ¿cada 1 min o cada 5?
**Contexto:** el cron del tri-toque tiene `interval:[{field:minutes}]` **sin `minutesInterval`** → por default n8n lo corre **cada 1 minuto** (no cada 5, como sugiere la doc). Más carga de polling.
- Confirmar el intervalo real y si conviene fijarlo.

**Ref:** doc 02 (O2) · doc 05. → actualiza doc 02, 05.

**A18:**

```
‹ escribí tu respuesta acá (reemplazá esta línea) ›
```

### Q19 🟡 `[LA AGENCIA-VIVO]` — "Seguimiento agenda" (48h): ¿vivo o stub muerto?
**Contexto:** además del Rescate Post-Link (45min+24h, activo), existe un workflow "Seguimiento agenda" de 48h single-touch que figura `active:false` y tiene un nodo placeholder "Replace me with your logic" sin limpiar. Podrían coexistir o ser lógica muerta.
- ¿Corre en producción o es un stub/legacy? (para decidir si se consolida o se descarta en GHL).

**Ref:** doc 03 §10 (nota) · doc 02 (A2 vs R1/R2). → actualiza doc 02, 03.

**A19:**

```
‹ escribí tu respuesta acá (reemplazá esta línea) ›
```

### Q20 🟢 `[LA AGENCIA-VIVO]` — Memoria sintética del rescate: ¿se carga bien?
**Contexto:** los nodos "Build Rescate Memory" tienen refs a un nodo `$('Get Lead')` que **no existe** (el real es `Airtable: 1er check`) y usan `{{first_name}}` en vez de la convención `[first_name]`. Los inserts a Postgres tienen `onError: continueRegularOutput`, así que no abortan el rescate, pero la memoria sintética podría no cargarse.
- ¿La memoria sintética del rescate efectivamente se inserta en `n8n_chat_histories` cuando el flujo dispara?

**Ref:** doc 05 §5 (Build Rescate refs) · doc 02. → actualiza doc 02, 05.

**A20:**

```
‹ escribí tu respuesta acá (reemplazá esta línea) ›
```

### Q21 🟢 `[LA AGENCIA-VIVO]` — `crear_contacto` blanquea `Folio` + ¿es el mismo sub-workflow?
**Contexto:** dos cosas del alta de contacto: (1) `wf-crear-contacto-clientify-airtable` **blanquea el `Folio`** al materializar el contacto (comportamiento no documentado, posible artefacto que perdería tracking); (2) ese sub-workflow tiene `availableInMCP:false` e inputs planos sin `$fromAI`, así que **no está claro si es el mismo** que invoca la tool `crear_contacto` del agente.
- ¿Por qué se blanquea el Folio? ¿La tool del agente y ese sub-workflow son el mismo?

**Ref:** doc 01 / doc 05 (crear_contacto). → actualiza doc 01, 05.

**A21:**

```
‹ escribí tu respuesta acá (reemplazá esta línea) ›
```

---

## BLOQUE C — Decisiones de arquitectura GHL (la agencia + la agencia, definen el diseño de Etapa 3)

> Son las **bisagras** del rediseño. No necesitan a Mauricio (salvo indicación), pero definen todo lo demás.

### Q22 🔴 `[ARQUITECTURA-GHL]` — ¿Dónde vive el agente "Mauricio"?
**Contexto:** LA decisión más importante. El agente conversacional (gpt-4o, prompt ~39K, memoria Postgres, tools) es la pieza de mayor valor y mayor riesgo de regresión.
- ¿Se **mantiene en n8n** (con Supabase como memoria) disparado por GHL, o se **migra al Conversation AI nativo de GHL**? Esto define memoria, memoria sintética, triple write y todo el resto.
- *Recomendación técnica preliminar de la agencia:* mantenerlo en n8n al menos en el cutover.

**Ref:** doc 06 §C.1/§C.2/§D.6, N.2. → actualiza doc 01, 03, 06.

**A22:**

```
‹ escribí tu respuesta acá (reemplazá esta línea) ›
```

### Q23 🔴 `[ARQUITECTURA-GHL]` — CAPI post-migración: ¿cómo hace el lookup del lead?
**Contexto:** el workflow CAPI (que se queda en n8n) hoy busca al lead en Airtable Leads por teléfono. Si Airtable Leads se congela post-migración, ese lookup queda desactualizado.
- ¿n8n consulta la **GHL API** por teléfono, o mantenemos un **sync GHL→Airtable Leads** de campos mínimos (teléfono/nombre/Folio)?

**Ref:** doc 06 §A.3 (caveat) / §C.4, N.4. → actualiza doc 06.

**A23:**

```
‹ escribí tu respuesta acá (reemplazá esta línea) ›
```

### Q24 🔴 `[ARQUITECTURA-GHL]` — Canal WhatsApp en GHL
**Contexto:** define cómo entra/sale la conversación.
- ¿El mismo número de WhatsApp de ManyChat pasa a GHL? ¿Cuál es el número / Business Account (WABA) / proveedor de API?
- ¿Los canales Instagram/Facebook entran también (hoy el main es WhatsApp-only)?

**Ref:** doc 06 §G (E.1) · doc 02 (canales IG/FB). → actualiza doc 02, 06.

**A24:**

```
‹ escribí tu respuesta acá (reemplazá esta línea) ›
```

### Q25 🟡 `[ARQUITECTURA-GHL]` — Memoria sintética + debounce
**Contexto:** dos patrones que hay que preservar o reemplazar.
- (a) La **memoria sintética** (outreach/rescate insertan mensajes en el historial para que el agente no re-salude) — ¿se replica en GHL, o desaparece porque el historial es nativo?
- (b) El **debounce de 20 s** de ManyChat (agrupa mensajes rápidos antes de responder) — ¿cómo se replica en GHL para no fragmentar las respuestas?

**Ref:** doc 06 §D.6/§F.1. → actualiza doc 01, 06.

**A25:**

```
‹ escribí tu respuesta acá (reemplazá esta línea) ›
```

### Q26 🟡 `[ARQUITECTURA-GHL]` — Consolidación del triple-write
**Contexto:** hoy cada lead se escribe en Airtable + Clientify + Supabase, reconciliado solo por teléfono. En GHL el Contact unifica las 3 identidades.
- ¿Qué se conserva y qué se elimina? (ligado a Q22 y Q23).

**Ref:** doc 06 §C.1. → actualiza doc 01, 06.

**A26:**

```
‹ escribí tu respuesta acá (reemplazá esta línea) ›
```

---

## BLOQUE D — Acciones de limpieza / higiene (la agencia ejecuta; confirmá OK)

> No son preguntas de negocio: son cosas que hay que **corregir/limpiar** durante la migración. Confirmá que estás de acuerdo (y cuándo, si aplica).

### Q27 🔴 `[HIGIENE]` — Rotar secretos hardcodeados (URGENTE)
**Contexto:** hay tokens en texto plano en varios workflows: access_token de Meta (en Airtable Programas CAPI), Bearer de ManyChat (`3256256:…`), token de Clientify (`3822fcd1…`) y una API key de OpenAI en una transcripción. Riesgo de seguridad al versionar/entregar.
- ¿OK a rotarlos y moverlos a credenciales/env **antes** de cualquier export/handoff? (Clientify/ManyChat quedan obsoletos igual, pero conviene rotar por higiene).

**Ref:** doc 06 §E.2 · Marcadores de los 6 docs. → actualiza doc 05, 06.

**A27:**

```
‹ escribí tu respuesta acá (reemplazá esta línea) ›
```

### Q28 🟡 `[HIGIENE]` — Normalizar la doble grafía Boarding + limpieza de enum
**Contexto:** 482 leads con `Boarding School` vs 437 con `Boarding IA` (mismo programa, dos grafías). Al migrar a un single-select GHL con exact-match, hay que unificarlos a la grafía canónica (ver Q2d).
- ¿OK a normalizar `Boarding School` → grafía canónica en la migración de datos?

**Ref:** doc 03 §5.2 · doc 05 §2.5 · doc 06 §D.1. → actualiza doc 03, 05, 06.

**A28:**

```
‹ escribí tu respuesta acá (reemplazá esta línea) ›
```

### Q29 🟡 `[HIGIENE]` — Reconciliar el schema real de Airtable Leads
**Contexto:** el CSV export tiene **30 columnas**, pero los workflows escriben campos que **no vienen en ese CSV** (`Contestan 1er mensaje`, `Cualificado`). El schema real de la base es un superset. Antes de mapear a GHL Contacts hay que reconciliar el header real.
- ¿OK a exportar el schema completo de Airtable Leads (todos los campos) para el mapping definitivo?

**Ref:** doc 05 §9.1 (nota) · doc 06 §A.3. → actualiza doc 01, 05, 06.

**A29:**

```
‹ escribí tu respuesta acá (reemplazá esta línea) ›
```

### Q30 🟡 `[HIGIENE]` — Unificar tabla de programas (rescate/nurturing/links/pixels)
**Contexto:** el rescate mapea 5 programas en el envío pero 6 en memoria ("Estudio y Trabajo" nunca recibe rescate); el regex de folio difiere entre el main y el CAPI (folios con "-" no persisten en Leads pero sí generan evento CAPI). Todo esto se resuelve con una **tabla única programa → (mensaje F1, mensaje F2, URL, tag, experto, pixel)**.
- ¿OK a construir esa tabla única como fuente de verdad en GHL (depende de Q2/Q3/Q4)?

**Ref:** doc 06 §E.4 · doc 02/05 (regex folio) · doc 04. → actualiza doc 02, 04, 05, 06.

**A30:**

```
‹ escribí tu respuesta acá (reemplazá esta línea) ›
```

### Q31 🟢 `[HIGIENE]` — Recuperar textos faltantes de nurturing
**Contexto:** los textos del **4º toque** de los drips de **AA Familiar** y **Summer Camp** no quedaron capturados en los screenshots (2 de 24 mensajes).
- ¿OK a re-abrir esos 2 flows en el editor de ManyChat para copiar los textos exactos antes de recrearlos en GHL?

**Ref:** doc 04 §D / Marcadores · doc 06 §F.2. → actualiza doc 04.

**A31:**

```
‹ escribí tu respuesta acá (reemplazá esta línea) ›
```

### Q32 🟢 `[HIGIENE]` — Formulario Clientify: versión y campos ignorados
**Contexto:** (1) el JSON del formulario en `00_inputs` es una versión **pre-fix** (rompe el tag cuando el lead ya existía en Clientify) — hay que usar la versión viva `03_workflows/formulario-clientify-venttur-v1.json`; (2) el formulario **no persiste `Programa interés`** en Airtable (solo el tag en Clientify) e ignora email/país/ciudad/folio/fbp del form.
- ¿OK a que en GHL el formulario persista programa como campo + tag, y a mapear los campos hoy ignorados?

**Ref:** doc 06 §E.7 · doc 01/05. → actualiza doc 01, 05, 06.

**A32:**

```
‹ escribí tu respuesta acá (reemplazá esta línea) ›
```

---

## Checklist de cierre

Cuando `A1`–`A32` estén completas (o marcadas como diferidas con criterio), Etapa 2 queda cerrada y podemos entrar a Etapa 3 (diseño de arquitectura GHL). Las **dos bisagras** que más definen el diseño son **Q1 (pipeline de deals)** y **Q22 (dónde vive el agente)** — si solo pudieras responder dos, que sean esas.

| Bloque | Preguntas | Quién responde principalmente |
|--------|-----------|-------------------------------|
| A — Negocio | Q1–Q11 | Mauricio / Venttur |
| B — Sistema vivo | Q12–Q21 | la agencia (verifica) + puntualmente Mauricio |
| C — Arquitectura GHL | Q22–Q26 | la agencia + la agencia (Q24 con cliente) |
| D — Higiene | Q27–Q32 | la agencia ejecuta (la agencia aprueba) |

> **Al terminar:** pasame este doc completo y actualizo los 6 documentos de `01_logica_actual/` + `ESTADO_MIGRACION.md` con las respuestas, marcando cada `⚠️ INCIERTO` resuelto.
