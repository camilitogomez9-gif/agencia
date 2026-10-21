# Mejoras Post-Reunión 2026-05-21 — Análisis y Decisión Pre/Post-Migración

> **Fuente:** reunión Fathom 2026-05-21 (Oscar, Rebeca, la agencia, Juan Pablo) + documento "Buzón de quejas y sugerencias" de Rebeca.
> **Input crudo:** `00_inputs/reunion-2026-05-21-rebeca-casos.md`
> **Objetivo del doc:** (1) consolidar los puntos accionables, (2) mapearlos contra la arquitectura GHL ya diseñada en Etapa 3, (3) **decidir si se implementan antes o después de la migración**, (4) plan de acción.
> **Fecha:** 2026-05-26

---

## §0. TL;DR — La decisión

**Recomendación: implementar POST-migración, integrado al build de GHL. No tocar Kommo.**

Razón en una línea: **los 3 problemas más graves y frecuentes (loop de repetición ~30% de leads, reactivadores que no responden, y la pérdida de contexto por liberar memoria) son causados por la arquitectura que la migración justamente reemplaza.** No son bugs a parchar — son síntomas de la rigidez por etapas y de la memoria limitada. La migración a GHL + Vendedor único + memoria persistente en Supabase **los elimina por diseño, sin trabajo extra**. Parchearlos en Kommo sería pelear contra la arquitectura, trabajo descartable sobre un sistema que se apaga en ~3 meses, y riesgo sobre producción justo antes del cutover.

Las mejoras restantes (catálogo específico, vasos popote, pantuflas moño/satín, cotización formal, diseños fuera de catálogo) son **adiciones chicas que se pliegan al build de GHL** como parte de Etapa 4/5, se validan en el sandbox (Test Plan M8) antes del cutover, y se afinan con volumen real apenas migramos.

Esto coincide con lo que la agencia ya anticipó en la llamada (min 50:23): *"lo mejor es capaz que es mejor terminar la migración y después implementar estas cosas ahí en Go High Level."*

---

## §1. Puntos accionables (consolidados)

Los 9 ítems del documento de Rebeca + matices del transcript, deduplicados y con causa raíz:

| # | Problema observado | Frecuencia | Causa raíz |
|---|--------------------|-----------|------------|
| **P1** | El agente **re-pide datos y re-envía info** cuando el lead vuelve a mencionar productos, aunque ya cotizó. Cae en loop, el cliente se frustra. | ~30% de leads | **Rigidez por etapas:** cada agente de etapa re-dispara su rutina cuando detecta palabras-producto, sin ver que el dato ya está capturado. |
| **P2** | Leads en **reactivadores R1/R2/R3 (con/sin info) que el agente NO responde** cuando el cliente escribe. Rebeca cotiza a mano. | "muchos leads" | **Bug en Kommo:** variable/identificador de estado quedó mal mapeada en algún cambio de embudos. El agente debe responder en todos los reactivadores salvo los `*AP` (atención personalizada). |
| **P3** | Diseños/imágenes **que no son del catálogo** → el agente dice "qué diseño tan bonito" y sigue, aun con diseños imposibles de hacer. | Constante con imágenes | Reconocimiento de imágenes fue desactivado a propósito (generaba problemas) → fallback genérico "qué linda imagen". |
| **P4** | **Pantuflas de moño**: el cliente manda imagen de moño, pero el agente **cotiza las de satín clásicas** (variante equivocada). | Recurrente | El clasificador no distingue variante; el cotizador toma default. |
| **P5** | **Cotización formal / PDF / correo**: el agente prometió mandar PDF por email (no puede) en vez de elevar a humano. | Poco frecuente (1 caso) | Falta regla de derivación para "cotización formal". |
| **P6** | **Vasos con popote** no siempre se identifican en imágenes ni se cotizan; solo escala. | Recurrente | Vaso popote no está como categoría real del clasificador (hoy cae en "otro"/NINGUNO) pese a ser producto vendible ($35). |
| **P7** | **Solicitud de catálogo específico**: piden "el catálogo de sandalias" y el agente reenvía TODO (infografía+video) o escala. Incluye el caso del cliente que **borró el WhatsApp** y vuelve meses después sin la info. | Constante | Rigidez: no hay forma flexible de reenviar un asset puntual; + tensión: mandar solo el PDF pierde material de venta. |
| **P8** | **Reenvío de imágenes/fotos**: cuando el lead pide "fotos" (ej. pantuflas moño vs normal) el agente escala en vez de reenviar la infografía. | Recurrente | Regla actual: "no reenviar imágenes" (puesta para frenar envíos en loop) sin excepción para pedido explícito. |
| **P9** | **Ventas perdidas / memoria**: hoy se manda a "ventas perdidas" para liberar memoria; ahí el agente no responde → los que vuelven los contesta Rebeca. | Estructural | Limitación de memoria del sistema actual. |

**Discusión transversal (transcript):** centralizar los 4 agentes en 1 vs. mantener etapas. **Síntesis acordada:** mantener la guía/tracking por etapas (métricas, proceso estructurado de HPF) PERO con un agente flexible que maneje casos borde sin re-disparar etapa 1. → Esto es **exactamente** la arquitectura de Etapa 3 (Vendedor único + stages de GHL como tracking, no como agentes separados).

---

## §2. Mapeo contra la arquitectura GHL (Etapa 3)

Acá está el corazón del análisis. Cada problema cae en uno de 3 grupos:

### Grupo A — Ya resueltos por el diseño de la migración (cero trabajo extra; solo validar en testing)

| # | Cómo lo resuelve la arquitectura GHL | Referencia |
|---|--------------------------------------|-----------|
| **P1** Loop de repetición | El **Vendedor único** ve el contexto completo (memoria Supabase, ventana 30 msgs) + recibe inyectado `[7. CONTEXTO DEL LEAD ACTUAL]` con `cantidad_sandalias`, `codigo_postal`, `cotizacion_emitida_at`, etc. **No re-pregunta lo que ya tiene** y no hay "agentes de etapa" que se re-disparen. Las etapas pasan a ser tracking del Opportunity, no agentes con rutinas rígidas. | `04_agentes_llm.md §2.2 [7]`, `§1.1` |
| **P2** Reactivadores no responden | En GHL **no existe el bug**: WF-02 mantiene la IA activa en todos los waves de re-engagement; solo el tag `human_takeover` la pausa. No hay estados R*con/sin info mal mapeados — hay tags `re_engagement_phase_1/2` y un solo Vendedor que siempre responde si el lead escribe. | `03_workflows_ghl.md WF-02`, `01_pipeline_ghl.md` |
| **P9** Ventas perdidas / memoria | **Memoria persistente en Supabase** (decisión §3.1) elimina la necesidad de "liberar memoria". El stage **"En espera"** tiene IA **activa**: si el lead vuelve, el Vendedor lo retoma con todo el historial. Solo a 6 meses de inactividad pasa a "Ventas Perdidas Real". | `01_decisiones.md §3.1, §3.4`, `04_agentes_llm.md §4.3` |

> **Implicación clave:** estos 3 — incluido el problema #1 que afecta al ~30% de los leads — **se arreglan solos al migrar**. Cualquier esfuerzo de parchearlos en Kommo es descartable.

### Grupo B — Adiciones chicas que se pliegan al build de GHL (incrementales sobre los docs de Etapa 3/4)

| # | Qué hay que agregar | Dónde | Tamaño |
|---|---------------------|-------|--------|
| **P3** Diseños fuera de catálogo | Regla en el Vendedor: si el lead manda un diseño que pide reproducir y no es del catálogo → "no reproducimos diseños externos, pero tenemos estos…" + `ATENCION_PERSONALIZADA` si insiste. (Ver §5 — decisión de alcance: clasificación de tipo vs. matching real de diseño). | `04_agentes_llm.md §2.2 [5]` + Vision | S/M |
| **P4** Pantuflas moño/satín | El catálogo (Custom Object) ya distingue `pantufla_mono_satin` / `pantufla_mono_peluche` / `pantufla_satin`. Asegurar que **COTIZADOR** tome la variante correcta y que el Vendedor confirme variante antes de cotizar. | `M3` catálogo + `COTIZADOR` | S |
| **P5** Cotización formal/PDF | Agregar a la descripción de `ATENCION_PERSONALIZADA`: *"lead pide cotización formal, PDF o por correo → derivar"*. 1 línea. | `04_agentes_llm.md §2.3 Tool 4` | XS |
| **P6** Vasos popote | Agregar **VASO_POPOTE** (y **BOLSA**) como categorías del Vision Classifier (hoy están excluidas como "otro" pese a ser vendibles). Agregar al enum de `MOSTRAR_PRODUCTOS`/`COTIZADOR`. | `04_agentes_llm.md §3.2` | S |
| **P7** Catálogo específico + cliente que borró WhatsApp | Regla en el Vendedor: si piden "el catálogo de X", preguntar *"¿tenés la info que te pasé o te la reenvío?"* y reenviar el asset puntual con `MOSTRAR_PRODUCTOS` (que puede re-dispararse sin reiniciar etapa). Cuidar la tensión de Juan Pablo: no perder el material de venta (infografía+video) cuando el pedido es inicial. | `04_agentes_llm.md §2.2 [4]` + `MOSTRAR_PRODUCTOS` | M |
| **P8** Reenvío de fotos a pedido | Excepción a "no reenviar imágenes": si el lead **pide explícitamente** una foto/infografía, reenviarla vía `MOSTRAR_PRODUCTOS`. | `04_agentes_llm.md §2.2 [4]` | S |

> Todas estas son ediciones a documentos que **ya existen**; ninguna es un proyecto nuevo. Se validan en el **Test Plan de M8** (Vendedor + Vision) antes del cutover.

### Grupo C — Bug puro de Kommo (solo si Oscar necesita alivio inmediato)

| # | Parche posible en Kommo | ¿Vale la pena? |
|---|-------------------------|----------------|
| **P2** | Encontrar la variable de estado mal mapeada en los embudos y corregirla. ~1-2 h. | **Descartable** (se va con la migración en ~semanas). Solo si el dolor es agudo HOY. |
| **P5** | Agregar la regla de "cotización formal → elevar" al prompt actual. ~30 min. | Marginal. Es 1 línea; igual hay que ponerla en GHL. |

---

## §3. La decisión: Pre vs Post-migración

### Opción PRE (implementar primero en Kommo/n8n actual)

**A favor:**
- Volumen real (100-150 msgs/día) → validación en producción inmediata.
- Alivio para Rebeca ahora (hoy contesta 100-150/día; Oscar quiere bajarla a 20-30).
- Prueba-error para "aprender" antes de comprometer GHL.

**En contra:**
- **El sistema actual se desmantela ~26 agosto.** Todo lo invertido ahí es descartable.
- **La causa raíz de P1/P7/P8 es la rigidez por etapas** — no se puede arreglar bien sin el cambio arquitectónico que *es* la migración. Parchear = pelear contra la arquitectura.
- **Riesgo sobre producción** justo antes del cutover ("podemos dar 10 pasos para atrás por querer dar 1 para adelante" — Juan Pablo).
- **Trabajo doble:** implementar en Kommo y re-implementar en GHL.
- Demora la migración (que está a 1-2 semanas de estar funcional).

### Opción POST (implementar en GHL, integrado al build) ✅ RECOMENDADA

**A favor:**
- **P1, P2, P9 (los más graves) ya están resueltos por el diseño** — costo cero.
- Las mejoras del Grupo B se construyen sobre la base flexible (Vendedor único + Vision reformulado) — **más limpio y robusto**.
- **Cero trabajo descartable.**
- GHL es una base pensada para iterar: *"se van a seguir haciendo cambios… una solución más robusta que va a soportar eso"* (la agencia, min 49:17).
- Se validan en el sandbox de M8 (Test Plan A-D) **antes** del cutover, y se afinan con volumen real **apenas migramos** (semanas, no meses).

**En contra:**
- GHL no tiene volumen real hasta el cutover → primera validación con casos curados del Test Plan, no con 150 msgs/día.
- Oscar espera un poco más para el alivio (mitigado: la migración está a semanas).

### Por qué POST gana

La pregunta de Oscar fue: *"¿implementarlo en el actual sirve como prueba-error, o no vale la pena tocar el actual?"*. La respuesta es que **no vale la pena tocar el actual**, porque:

1. El problema #1 (el más caro, 30% de leads) **no es parcheable** en Kommo sin reconstruir Kommo en lo que GHL ya va a ser. La migración es el arreglo.
2. La ventana de alivio que ganaríamos con un parche pre-migración es de pocas semanas (la migración está a 1-2 semanas de funcional + testing).
3. El miedo explícito de Oscar — *"no quiero echar a perder el de GHL"* — se respeta exactamente al revés de como suena: lo que pone en riesgo a GHL es meter mano a Kommo y tener que portar parches a las apuradas. La ruta segura es construir GHL **una vez, bien, con estas mejoras adentro**, y validarlas en sandbox antes de prender.

---

## §4. Plan de acción

### Fase 0 — Confirmar enfoque con Oscar (esta semana)
- [ ] Enviar a Oscar el mensaje de §6 (recomendación post-migración + por qué).
- [ ] Cerrar las 2 decisiones de alcance de §5 (diseños fuera de catálogo; catálogo específico).
- [ ] **ACTION ITEM del call:** confirmar a Oscar el enfoque sandbox vs GHL → **respuesta: sandbox dentro del build de GHL (M8), no en Kommo.**

### Fase 1 — Plegar mejoras a los docs de arquitectura (antes de construir)
Editar los documentos de Etapa 3/4 para incorporar Grupo B (no son cambios de diseño, son adiciones de reglas):
- [ ] `04_agentes_llm.md §2.2 [4] y [5]` — reglas P3, P5, P7, P8 (catálogo específico, cotización formal, reenvío a pedido, diseños externos).
- [ ] `04_agentes_llm.md §3.2` — agregar VASO_POPOTE y BOLSA al Vision Classifier (P6).
- [ ] `04_agentes_llm.md §2.3 COTIZADOR` — variantes de pantufla (P4).
- [ ] `04_guia_migracion/03_custom_object_producto.md` — granularidad de pantuflas + vasos popote + bolsa en el catálogo (P4, P6).
- [ ] `04_guia_migracion/08_testing_precutover.md` — agregar casos de test para P1-P9 (validar que el loop NO ocurre, que reenvía catálogo a pedido, que eleva en cotización formal, etc.).

### Fase 2 — Construir en GHL (Etapa 5, según guía M1-M9)
- [ ] Construcción normal del sistema (ya documentada). Las mejoras del Grupo B vienen incluidas en los prompts/catálogo/Vision.

### Fase 3 — Validar en sandbox (M8) antes del cutover
- [ ] Test Plan A (Vendedor): incluir explícitamente los casos P1, P5, P7, P8.
- [ ] Test Plan B (Vision 15 imágenes): incluir P3, P4, P6 (diseño externo, pantufla moño, vaso popote).
- [ ] Criterio go/no-go: el loop de repetición (P1) **no debe ocurrir** en los casos de test.

### Fase 4 — Afinar con volumen real (post-cutover)
- [ ] Primeras 2 semanas post-cutover: monitorear los mismos 9 patrones con tráfico real y ajustar prompts (los cambios en GHL son seguros y continuos).

---

## §5. Decisiones de alcance — ✅ CERRADAS (2026-05-26)

### Decisión 1 — Diseños fuera de catálogo (P3): ✅ MVP ahora + Avanzada post-cutover

El Vision Classifier actual clasifica **qué tipo de producto** es (sandalia/pantufla/cilindro…), **no** si un diseño puntual pertenece al catálogo de HPF. Detectar "esto es una sandalia, pero NO es uno de nuestros diseños" es materialmente más difícil (requiere un set de referencia de diseños HPF o comparación por embeddings).

- **✅ MVP (SE INTEGRA YA en la creación de flujos GHL — etapa actual):** regla conversacional — *"no reproducimos diseños externos; estos son los nuestros: …"*. Sin matching real. Resuelve el 90% del dolor (evita prometer diseños imposibles) con costo bajo. Forma parte del build inicial y se valida en el Test Plan M8 antes del cutover (NO es post-cutover).
- **✅ Avanzada (DESPUÉS de migración estable):** matching real contra catálogo HPF, una vez completados migración + testing + cutover y con todo estable. Se hace **junto con los demás cambios ya pendientes** (métricas #2, A/B promos #3 de `01_decisiones.md §2.6`). Se evalúa con el Test Plan §3.2 (no migramos a Claude por defecto; primero corremos los 4 brazos).

> **Decisión + aclaración del usuario (2026-05-26):** "El MVP lo incorporamos ya en el proceso de migración, en la creación de los nuevos flujos en GoHighLevel. Luego de completar migración + testing + cutover y con todo estable, avanzamos con la opción avanzada."

### Decisión 2 — Catálogo específico vs material de venta completo (P7): ✅ Recomendación aprobada — SE INTEGRA YA en el build

Tensión señalada por Juan Pablo: si mandás solo el PDF del catálogo, perdés la infografía + video que venden.
- **✅ Aprobado e integrado en la creación de flujos GHL (etapa actual):** la regla "preguntar ¿tenés la info o te la reenvío?" aplica **solo cuando el lead ya tuvo la info** (cliente que volvió / borró WhatsApp — distinguido por contexto de memoria / `customer_status` / historial). Para un pedido **inicial** de catálogo, mandar el material de venta completo como hoy.

> **Decisión + aclaración del usuario (2026-05-26):** "Avanzamos con tu recomendación, incorporando la implementación dentro del proceso de creación de los flujos en GoHighLevel para que al terminar esa parte de la migración ya esté incorporado."

---

## §5b. Aplicación en los docs de arquitectura (Fase 1 — hecho 2026-05-26)

Grupo B (versión MVP) plegado a los documentos del build de GHL:

- `03_arquitectura_ghl/04_agentes_llm.md` — reglas P3 (MVP), P4, P5, P7, P8 en el system prompt del Vendedor + VASO_POPOTE/BOLSA en el Vision Classifier (P6).
- `04_guia_migracion/03_custom_object_producto.md` — granularidad de pantuflas (clásica/moño satín/moño peluche), vasos popote y bolsa en el catálogo (P4, P6).
- `04_guia_migracion/08_testing_precutover.md` — casos de test P1-P9 en el Test Plan pre-cutover.

Marcadas con `(Mejora 2026-05-21)` para trazabilidad.

---

## §6. Mensaje sugerido para Oscar

> Oscar, analizamos todo lo que trajo Rebeca (excelente el documento) y acá va la recomendación.
>
> La mayoría de los casos que vimos — sobre todo el más frecuente, que el agente vuelve a pedir datos que ya tenía (te afecta como al 30% de los leads) — **no son errores sueltos para parchar: son consecuencia de cómo está armado el sistema actual por etapas rígidas y con memoria limitada.** La migración a GoHighLevel justamente cambia eso: un solo agente que ve toda la conversación + memoria que no se borra. Así que esos casos **se arreglan solos al migrar**, sin trabajo extra.
>
> El resto (vasos con popote, pantuflas de moño, cotización formal por PDF, pedir un catálogo puntual, diseños que no son nuestros) son ajustes chicos que **metemos directamente en el build de GoHighLevel** y los probamos en un entorno de prueba antes de prender, y los afinamos con tráfico real apenas migramos.
>
> Mi recomendación es **no tocar el sistema actual de Kommo** (se apaga en agosto, sería trabajo que tiramos y arriesga lo que ya funciona) y meter todas estas mejoras en GoHighLevel, que está a 1-2 semanas de estar funcional. Construimos una vez, bien, con todo esto adentro.
>
> Dos cosas para definir: (1) en los diseños "que no son nuestros", para el arranque hacemos que el agente diga "no reproducimos diseños externos, estos son los nuestros" — el reconocimiento que compara contra tu catálogo real lo evaluamos después; (2) cuando piden "el catálogo", si es un cliente que ya lo tuvo le preguntamos si quiere que se lo reenviemos, y si es nuevo le mandamos todo el material como ahora.

---

## §7. Impacto en el estado de la migración

- **No cambia el timeline** (~15 julio target). Las mejoras del Grupo B son incrementales sobre los docs existentes.
- **No reabre Etapa 2/3.** Confirma y extiende decisiones ya tomadas (Vendedor único, Vision reformulado, memoria persistente).
- **Agrega tareas a Etapa 4** (plegar Grupo B a los docs) y a M8 (casos de test P1-P9).
- **Reafirma §3.2** (no migrar a Claude por defecto; correr Test Plan primero) frente al nuevo pedido de Oscar de evaluar Claude para imágenes.
