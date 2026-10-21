# Decisiones Validadas — Etapa 2 (consolidación)

> **Fuente:** cruzado entre `01_logica_actual/06_redundancias_y_ambiguedades.md` (respondido por cliente), reunión con Oscar 2026-05-09, `textos_salesbots.txt`, `kommo_export.json` y `conversation_samples.json`.
> **Fecha de cierre:** 2026-05-12
> **Estado Etapa 2:** ~70% — quedan 6 decisiones pendientes (sección §3) que deben cerrarse antes de Etapa 3.

---

## §1. Decisiones CERRADAS (confirmadas por el cliente)

### Estructurales (A)

| Ítem | Decisión | Notas |
|------|----------|-------|
| A.1 Tres nodos "Confirmar Pago" | REMOVE 2 de 3 → 1 sola transición GHL | Las 3 rutas (PDF, imagen A, imagen B) ejecutan los mismos pasos |
| A.2 ~14 nodos `actualizar*` | CONSOLIDATE → 1 acción "update opportunity stage" antes de cada envío | Los nodos actualizan **el mensaje** (custom field), no el stage. Esto **cambia la interpretación arquitectónica**: en GHL el mensaje sale del workflow directamente, no de un custom field intermedio |
| A.3 `AI Agent Recolector` y `Recolector1` | UNIFY → un solo agente "Vendedor" con preprocesamiento de input | |
| A.4 Doble debouncing Redis (50s/15s) | UNIFY → único timeout (45s tentativo) | Las dos rutas eran por tipo (texto/audio vs imagen) |
| A.5 19 nodos `noOp` | REMOVE en migración | Cierres defensivos sin lógica |
| A.6 5 `stickyNote` | REMOVE estructuralmente | No transferir contenido |

### Funcionales (B)

| Ítem | Decisión | Notas |
|------|----------|-------|
| B.1 LLMs helper de formato | REMOVE `Message a model1` y `Formatear mensaje1` (división determinística). MODIFY `Message a model` y `Necesita Respuesta Especial` — siguen reglas determinísticas pero cumplen funciones adicionales que hay que extraer y mover al workflow GHL o al system prompt del Vendedor | **Cliente subrayó:** la división de mensajes es **semántica y por longitud**, no solo por chars. Una parte del prompt filtra preguntas agresivas → mover esa regla al system prompt del agente principal |
| B.2 4 sub-workflows seguimiento | MODIFY — un solo workflow GHL "Re-engagement" con conditions por etapa | **Pero:** las 4 lógicas son diferentes (no son el mismo proceso replicado) y las cadencias tienen excepciones — preservar cada cadencia y patrón de match. Los textos de re-engagement están en `textos_salesbots.txt` |
| B.3 Lógicas paralelas texto/imagen | MODIFY → Switch al inicio que bifurca por tipo y converge | |
| B.4 Horario laboral + "Foto Vacaciones" | MODIFY → usar Business Hours nativo de GHL | El mensaje se envía siempre que se está en vacaciones, no solo en respuesta a pagos |

### Infraestructura (C)

| Ítem | Decisión | Notas |
|------|----------|-------|
| C.1 Doble CRM (Kommo v4 + AmoCRM v2) | REMOVE legacy **después** del cutover. Todos los endpoints v2 tienen equivalente v4 | No tocar antes del cutover para no romper |
| C.3 Múltiples modelos LLM | MODIFY → consolidar a: 1 conversacional + 1 vision + 1 mini helper | **⚠️ Tensión con reunión:** doc 06 dice "Vision GHL nativo"; reunión dice "Claude (Anthropic) en arquitectura híbrida" — ver §3.2 |
| C.4 Pipeline IDs hardcodeados | MODIFY → usar variables/Custom Values en GHL | IDs estables históricamente |

### Datos (D)

| Ítem | Decisión | Notas |
|------|----------|-------|
| D.1 `bot_id` Airtable + salesbots Kommo | MODIFY → migrar catálogo a GHL Custom Objects/Files, salesbots → GHL Workflows | "Lo que sea más profesional, simple y robusto" |
| D.2 CURLs en Airtable | REMOVE — completamente obsoletos | |
| D.3 Textos re-engagement | Viven en salesbots Kommo → ya están extraídos en `textos_salesbots.txt` | Ver §2.1 abajo para mapeo |
| D.5 17 etapas R1-R5 sin/con info/ap | SIMPLIFY → 1 etapa "Re-engagement" + tags `re_engagement_wave_N` | Las distintas Rn corresponden a momentos temporales. No hay reportes que usen esta granularidad |
| D.6 `If25 == 8075544` | REMOVE — sin efecto funcional. Es el lead de Oscar; conservar referencia solo en documentación, no en flujo | |
| D.7 Workflow `nkRBXbc4G0Cn67gY` | MODIFY → reemplazar referencia por `xo1sLt9cAhFAC6k3` ("Seg. 7 pasos"). El workflow no existe | |

### Comportamiento (E)

| Ítem | Decisión | Notas |
|------|----------|-------|
| E.1 Router step_2 vs step_3 | Lead con evento+producto en mismo turno → salta step_2 → va directo a step_3. **Validado en `conversation_samples.json` (sample_1 turn 7-8)** | |
| E.2 ¿Quién mueve a ETAPA 4 (93616840)? | El nodo `ETAPA 3` del flujo `Seg. 7 pasos` | |
| E.3 `Wait2` con valor vacío | REMOVE — estaba en 1.00s, no altera lógica | |
| E.4 System prompt de `Necesita Respuesta Especial` | Extraerlo del JSON antes de Etapa 3 (tarea pendiente, ver §3) | El cliente pidió hacer esto con **todos** los system/user prompts |
| E.5 `Saludo PTE 1/2/3` | Son las 3 partes del saludo Starter (no re-engagement) | |
| E.6 Catálogo por evento | VALIDADO según tabla del doc 06 (Mandiles solo Boda, etc.) | |
| E.7 Precios | Sandalias delgadas $25 / gruesas $30 / Pantuflas $30 / Cilindros $10 / Kit anticruda $10 / Mandiles $12 / Vasos popote $35 / Bolsa $7 | **⚠️ Conflicto detectado:** `textos_salesbots.txt:7` dice "$24 PAR suela DELGADA" (no $25). Ver §3.6 |

### Simplificación agresiva (F)

| Ítem | Decisión | Notas |
|------|----------|-------|
| F.1 Pipeline GHL | Ver §2.2 — **revisado** vs propuesta original del doc 06 | |
| F.2 Eliminar AmoCRM legacy | Esperar al cutover final | |
| F.3 Consolidación LLMs | Aprobada: Router → workflow conditions; Starter, Main Image → mensajes fijos; Products → consolidado en Vendedor; Recolector1 → unificado | **⚠️** Vision Classifier: pendiente decisión modelo (ver §3.2) |

---

## §2. Decisiones tomadas en la reunión con Oscar (2026-05-09)

### §2.1 Mapeo de salesbots Kommo (de `kommo_export.json` + `textos_salesbots.txt`)

Patrón identificado:

```
E1 = Bot inicial / muestra producto (uno por producto × evento)
R1 = Re-engagement wave 1
R2 = Re-engagement wave 2 (genérico, dispara cuando lead sin producto identificado)
R3 = Re-engagement wave 3
```

Salesbots por familia de producto:

| Producto | E1 | R1 | R2 | R3 |
|----------|----|----|----|----|
| Sandalias (boda) | 20978 | 20992 | 20998 | 21006 |
| Sandalias XV | 21012 | — | — | — |
| Cilindros | 21022 | 21024 | — | 21026 |
| Mandiles | 21186 | 21194 | — | 21198 |
| Kit anticruda | 21582 | 21590 | — | 21592 |
| Pantuflas | 21596 | 21600 | — | 21602 |
| Sandalia lisa | 21620 | — | — | — |

Bots de menú/saludo:

- `20982` MENU DE ENTRADA
- `21636` Saludo + "no recibimos respuesta"
- Re-engagements genéricos ("Quedan 3 días", "Mañana último día"): sin bot_id explícito en la muestra — viven dentro de los `Seg. *` sub-workflows

**Bot `23120` con precio "$29 suela GRUESA" → OBSOLETO. No aparece en lista activa de `kommo_export.json`. Se omite en la migración.**

### §2.2 Pipeline GHL revisado (supersede F.1 original)

| Etapa GHL | IA activa | Responsable | Fuente |
|-----------|-----------|-------------|--------|
| New Lead | Sí | IA | n8n trigger |
| Greeted (ETAPA 1) | Sí | IA | Starter |
| Engaged with event (ETAPA 2) | Sí | IA | Main Image |
| Showed Products (ETAPA 3) | Sí | IA | Products / Vendedor |
| Quoted (ETAPA 4) | Sí | IA | Vendedor + CALCULADORA |
| Awaiting Payment | Sí (envía recibo) → Off post-mensaje | IA + Humano | Confirmar Pago |
| **Pago sin diseño** | Off | Diseñadora | Manual |
| **Diseño enviado** | Off | Diseñadora | Manual |
| **Producción** | **Reactivada** (monitor 2do pago) | Equipo + IA | IA detecta pago liquidación |
| Awaiting Final Payment | Sí | IA + Humano | Pago liquidación |
| Won (Logrado con éxito) | Off | — | Manual |
| **En espera** (nueva) | **Sí** | IA | Lead no compró en ciclo pero puede volver |
| **Ventas perdidas real** (nueva) | **Off** | — | Movimiento manual del equipo |
| Tag `human_takeover` | Off | Humano | Atención personalizada |
| Tag `re_engagement_wave_N` | Sí | IA | R1/R2/R3 |

**Cambios vs. doc 06 F.1:**
- Las 3 etapas post-pago (sin diseño / diseño / producción) **se mantienen separadas** (decisión Oscar) — antes estaban consolidadas en "In Production".
- Se agrega "En espera" (IA activa) como etapa distinta de "Ventas perdidas real" (IA off).
- IA debe **reactivarse en "Producción"** para detectar segundo pago (liquidación).

### §2.3 Personalización de seguimientos

**Cambio arquitectónico crítico vs. estado actual:**

- **Actual:** textos hardcodeados en salesbots Kommo (D.3).
- **Post-migración:** los textos de R1/R2/R3 se **generan con LLM usando contexto** (productos cotizados, conversación previa).
- **Cadencias:** se mantienen FIJAS (no personalizar tiempos). Reunión definió **24h / 48h / 72h hasta 7 días** — esto supersede la mención de "1h/3h/24h" del doc 06 B.2, que parece referirse a delays internos de los sub-workflows técnicos, no al funnel de seguimiento de cara al cliente.
  - **⚠️ Verificar en n8n** los delays reales de los 4 sub-workflows antes de la implementación.

### §2.4 Modelo de imágenes

**Decisión Oscar (reunión 2.7):** modelo híbrido — OpenAI para conversación, Claude (Anthropic) para análisis de imágenes.

**Esto supersede la respuesta del cliente en C.3 del doc 06** ("Probemos Vision en GHL"), que se dio antes de la reunión.

**Pendiente (tarea la agencia #8):** investigar si el problema actual ("qué bonito diseño") es de prompt o de modelo, antes de comprometer la arquitectura híbrida (ver §3.2).

### §2.5 Memoria / historial

- **Tentativo:** borrar a 6 meses (opción A, incluido).
- **Alternativa:** indefinida (~USD 25/mes, opción B).
- **Pendiente la agencia (tarea #3):** pasar costos detallados a Oscar para decidir.

### §2.6 Features nuevas (scope add-on)

Oscar agregó 4 features que **NO estaban en el doc 06** y aparecen por primera vez en la reunión:

1. **Seguimientos personalizados con contexto** (LLM-generated) → §2.3
2. **Tracking de tiempo de cierre** (fecha contacto → fecha compra)
3. **Promociones rotativas A/B** (round-robin de leads entre promos)
4. **Modelo híbrido Claude para imágenes** → §2.4

**Decisión de scope para MVP (Etapa 3-5):**

- **MUST-HAVE (julio):** #1 (seguimientos personalizados), #4 (Claude imágenes — si la investigación lo justifica), pipeline reestructurado + "En espera"/"Ventas perdidas real".
- **NICE-TO-HAVE (post-cutover, agosto-septiembre):** #2 (métricas), #3 (A/B promos).

Razón: el cutover de Kommo es 26-agosto; el riesgo de scope creep en julio amenaza la transición. Métricas y A/B se pueden agregar iterativamente con el sistema ya estable.

---

## §3. Decisiones — estado actualizado (2026-05-12)

### 3.1 Memoria — ✅ CERRADA (Opción B con stack externo)

**Decisión:** Opción B — memoria efectivamente indefinida usando **Supabase Pro (USD 25/mes)** como Postgres administrado, manteniendo el stack n8n + LangChain Memory actual.

**Justificación (investigación web 2026-05-12):**

- **GHL nativo no resuelve el caso de 6 meses.** El bot de Conversation AI envía típicamente los últimos ~20 mensajes al LLM (no la conversación completa) y no expone TTL configurable. Para un lead que vuelve a los 5 meses con referencia a una cotización anterior, GHL nativo no recupera ese contexto.
- **La "base de datos indefinida USD 25/mes" que mencionó Oscar es casi con certeza Supabase Pro** (no es un add-on oficial de GHL). Supabase Pro = 8 GB DB + 100 GB storage + 7 días backups + Realtime + Auth + integración nativa con n8n.
- **Dimensionamiento:** 10K leads/sem × 6 meses ≈ 240K contactos activos. ~15 msgs promedio × 200 bytes = ~720 MB raw. Cómodo dentro de los 8 GB de Supabase Pro, con margen para metadata y embeddings futuros.

**Stack recomendado (Opción B):**
- GHL Unlimited (USD 297/mes) — CRM, inbox, WhatsApp BSP, opportunities, pipelines.
- n8n (ya existe) — orquestación del agente IA, mantiene LangChain Memory.
- **Supabase Pro (ya pago por Oscar, USD 25/mes)** — ya existe y está operativo. Tabla `messages` con `session_id` (varchar, formato `<telefono>_2131`) + `message` (jsonb, schema LangChain). **Sin costo adicional.**
- Redis (ya existe) — debouncing.
- WhatsApp vía GHL: USD 10/mes platform fee + passthrough Meta. Las **service conversations** (lead escribe primero) son **gratis** desde nov-2024 — aplica a la mayoría del volumen de HPF.
- (Opcional Fase 2 post-cutover) Pinecone serverless ~USD 50/mes si se quiere retrieval semántico real ("¿qué le interesó hace 5 meses?").

**Costo total estimado:** USD 407–707/mes (USD 297 GHL + USD 0 Supabase [ya pago] + USD 10 WA platform + USD 100–400 Meta passthrough).

**Schema actual de Supabase (referencia para Etapa 3):**

```
tabla: messages (o equivalente en el proyecto de Oscar)
  id         int4     — identificador de fila
  session_id varchar  — formato: "<telefono_lead>_2131" (LangChain session_id)
  message    jsonb    — schema LangChain: { type: "ai"|"human", content: "...", tool_calls: [], ... }
```

La migración de Kommo a GHL **no requiere cambios en Supabase**. El `session_id` puede mantenerse igual si el número de teléfono del lead no cambia entre plataformas. El único ajuste posible es si GHL usa un identificador de contacto distinto al teléfono para formar el `session_id`.

**Sources:** [GHL Pricing](https://www.gohighlevel.com/pricing) · [Supabase Pricing](https://supabase.com/pricing) · [GHL Conversation AI bot](https://help.gohighlevel.com/support/solutions/articles/155000001335-conversation-ai-bot-explained) · [WhatsApp service conversations free](https://ideas.gohighlevel.com/changelog/whatsapp-pricing-changes-all-service-conversation-are-now-free-of-cost)

---

### 3.2 Imágenes — ✅ CERRADA (NO migrar a Claude; reformular prompt + subir tier de modelo)

**Decisión:** **No migrar a Claude todavía.** El problema actual ("qué bonito diseño") es casi con certeza de **prompt + integración entre clasificador y agente principal**, no del proveedor.

**Veredicto técnico (investigación web 2026-05-12):**

- El escalón de calidad **dentro de OpenAI** (gpt-4o-mini 59% MMMU → gpt-4o 69% → gpt-4.1 75% → gpt-5 84%) es mucho mayor que el escalón cross-proveedor a tier comparable (gpt-4o ↔ Claude Sonnet 4 = 5 puntos). **El tier del modelo importa mucho más que el proveedor.**
- gpt-4o (modelo actual del nodo `Analyze image`) **es sobradamente capaz** de distinguir una sandalia de un cilindro de un mandil. La tarea no requiere razonamiento de frontera.
- El síntoma reportado ("qué bonito diseño, ¿continuamos?") es un **fallback conversacional típico**, no un fallo de visión. Sugiere que (a) el agente principal ignora el output del clasificador, o (b) el prompt tiene instrucciones de cortesía que pisan la identificación, o (c) el clasificador tiene criterios vagos.
- El TikToker que migró a Claude probablemente reescribió el prompt en el proceso (sesgo de atribución).

**Arquitectura recomendada post-migración:**

GHL Workflow → Webhook a n8n → OpenAI Vision API con **prompt reformulado** + modelo `gpt-4.1` (no 4o-mini, no Claude). El bot nativo de GHL para imágenes existe pero no permite control fino del prompt — necesitamos workflow externo.

**Esqueleto de prompt reformulado para el clasificador:**

```
Sos un clasificador visual de productos para HappyFlops. Tu única tarea es identificar
qué producto muestra la imagen, eligiendo una de 5 categorías exactas.

CATÁLOGO (categorías válidas — no inventés otras):
1. SANDALIA — chancla/sandalia de goma o tela, generalmente con frase bordada en la tira.
2. PANTUFLA — calzado cerrado de tela/peluche para interior.
3. CILINDRO — recipiente cilíndrico (botella/termo/vaso) con etiqueta personalizada.
4. MANDIL — delantal de cocina con estampado/bordado personalizado.
5. KIT_ANTICRUDA — bolsa o caja con varios artículos con etiqueta de evento.

REGLAS ESTRICTAS:
- Devolvé SOLO JSON válido. Sin texto adicional, sin "qué lindo", sin comentarios estéticos.
- Si la imagen no es ninguna de las 5, usá "producto": "NINGUNO".
- "confianza" 0.0 a 1.0. Si <0.6, igual elegí la más probable, no devuelvas NINGUNO por duda.
- "razon" máximo 15 palabras, descripción visual concreta (no opiniones).

FORMATO DE SALIDA:
{"producto": "...", "confianza": 0.0-1.0, "razon": "..."}
```

Parámetros: `temperature: 0`, `response_format: json_object`.

**Además, en el system prompt del Vendedor agregar:** *"Cuando recibas `{{producto_detectado}} ≠ NINGUNO`, tu primera oración DEBE confirmar el producto identificado por nombre. Prohibido usar 'qué bonito', 'qué lindo', 'me encanta' como apertura."*

**Test plan (recomendado antes de Etapa 5):**

10 imágenes reales de Oscar + 5 adversariales (mal iluminadas, fondo confuso, producto parcial). Ground truth etiquetado manualmente. Testear 4 brazos:

| Brazo | Modelo | Prompt |
|-------|--------|--------|
| A (baseline) | gpt-4o | actual |
| B (aísla prompt) | gpt-4o | reformulado |
| C (aísla modelo) | gpt-4.1 | reformulado |
| D (aísla proveedor) | claude-sonnet-4.5 | reformulado |

**Métricas:** accuracy, tasa de evasiva ("qué bonito"), confianza calibrada, latencia p50/p95, costo/imagen.

**Criterio de decisión:**
- Si **B sube accuracy >20 pp sobre A** → el problema era prompt. Implementar B en producción y cerrar el tema.
- Si **B≈A pero C >> B** → era modelo dentro de OpenAI. Implementar C.
- Solo si **C falla y D pasa** → justifica migrar a Anthropic.

**Costo estimado (5000 imgs/mes):** gpt-4.1 ≈ USD 17/mes. Claude Sonnet 4.5 ≈ USD 26/mes. Diferencia irrelevante frente al ticket de venta.

**Implicación para Oscar:** la propuesta original de la reunión ("modelo híbrido OpenAI + Claude") **se posterga**. Probamos primero la solución más simple (mismo proveedor, mejor prompt + tier). Si efectivamente falla, vamos a Claude. Esto **evita complejidad operativa innecesaria** (dos proveedores, dos credenciales, dos curvas de degradación).

**Sources:** [LLM Stats GPT-4o vs 4o-mini](https://llm-stats.com/models/compare/gpt-4o-2024-05-13-vs-gpt-4o-mini-2024-07-18) · [GPT-4.1 announcement](https://openai.com/index/gpt-4-1/) · [MMMU Benchmark](https://mmmu-benchmark.github.io/) · [GHL AI Image Response](https://help.gohighlevel.com/support/solutions/articles/155000006537-conversations-ai-bots-can-now-respond-to-images)

---

### 3.3 Pipelines LIMBO — ✅ CERRADA

**Decisión:** los 12 pipelines `LIMBO` se **archivan** (no se migran a GHL, no se mantienen activos). Solo se migra:
- Pipeline `IA` (11622596) — funnel completo del agente.
- Pipeline `GENERAL` (9018931) — gestión manual del equipo (ACTIVO MANUAL).

Los otros 11 pipelines (`SANDALIAS BODAS`, `SANDALIAS XV AÑOS`, `Cilindros`, `Mandiles`, `Kit anticrudas`, `Pantuflas`, `Sandalia lisa`, `Happyfloops`, `XV AÑOS`, `BODAS`, `Reactivadores Genericos`) **no se tienen en cuenta para la migración**.

---

### 3.4 "Ventas perdidas real" vs "En espera" — ✅ CERRADA

**Regla operativa:**

- **"En espera"** (IA activa) → estado por defecto cuando un lead no compra en el ciclo de reactivadores. La IA sigue respondiendo si el lead vuelve a escribir.
- **"Ventas perdidas real"** (IA off) → se activa **automáticamente** después de **6 meses de inactividad** del lead (sin mensajes entrantes ni salientes). Transición programada por workflow GHL.

**Implicación arquitectónica:**
- No es un movimiento manual del equipo — es una transición automática time-based. Esto simplifica la operativa: Rebeca/Oscar no tienen que decidir cuándo mover; el sistema lo hace solo.
- Necesitamos un workflow GHL "Inactivity Sweep" que corra periódicamente (ej. diario) y mueva contactos cuya `last_activity_at < now - 6 meses` desde "En espera" a "Ventas perdidas real".
- También elimina necesidad de capacitar al equipo en criterios manuales — se documenta solo la regla del sistema.

---

### 3.5 Cadencias de seguimiento — ✅ CERRADA

**Fuente:** audios de Oscar 2026-05-12.

**Arquitectura confirmada: lógica DUAL en dos fases.**

#### Fase 1 — Waves cortas (post-inactividad inmediata)

Objetivo: "obligar a la gente a contestar" con alta frecuencia justo después de que dejaron de responder.

| Wave | Delay | Bots actuales |
|------|-------|---------------|
| W1 | **1h** | Seg. Rebeca: 60864 / Seg. Imagen: 60870 / Seg. Cotización: 60878 |
| W2 | **3h** | Seg. Rebeca: 60866 / Seg. Imagen: 60872 / Seg. Cotización: 60880 |
| W3 | **5h** | Seg. Rebeca: 60868 / Seg. Imagen: 60874 / Seg. Cotización: 60882 |

> El `Wait2` con valor vacío en los 3 sub-workflows es casi con certeza **5 horas** — Oscar lo confirma en audio ("una, tres y cinco horas"). Verificar en n8n.

#### Fase 2 — Reactivadores de días (dentro de la ventana de promoción de 7 días)

Objetivo: mantener el lead activo durante los 7 días de promoción. Cadencia confirmada por Oscar (2026-05-12):

| Wave | Delay acumulado | Texto esperado |
|------|-----------------|----------------|
| R1 | **24h** (1 día) | Re-engagement contextualizado |
| R2 | **48h** (2 días) | Re-engagement contextualizado |
| R3 | **120h** (5 días) | Re-engagement + urgencia |
| R4 | **168h** (7 días) | "ÚLTIMO DÍA — APROVECHA LA PROMO" |

Manejado por `Seg. 7 pasos` (Wait 24h periódico, mueve etapas R1 CON INFO / PERDIDOS / ETAPA 3).

> **Nota:** la cadencia real es 4 waves en 7 días (no 7 waves consecutivas). Hay gaps de 3 días (entre 48h y 120h) y de 2 días (entre 120h y 168h) — intencional para no saturar.

#### Requisito crítico de flexibilidad (nuevo — audio 2)

Oscar necesita que la campaña de días (Fase 2) sea **configurable sin rediseñar el workflow**:

- Hoy puede ajustar manualmente cuántos mensajes manda en la semana (5 o 3) según el presupuesto de plantillas de Meta (WhatsApp Business cobra por template message).
- Quiere conservar esa flexibilidad en GHL: activar/desactivar días de reactivación o cambiar cuántos envíos hace en la semana sin entrar a rediseñar nada.

**Implicación arquitectónica para Etapa 3:**

La campaña de días de Fase 2 en GHL debe diseñarse como un sistema de configuración, no hardcoded. Opciones:

- **GHL Custom Values** a nivel sub-account: `re_engagement_days_active = "1,3,5,7"` — el workflow lee esa variable y salta los días no incluidos.
- **GHL Workflow con condiciones por Custom Field** del contacto: permite incluso personalizar por segmento si se quiere.
- El cambio de 5 días a 3 días debe poder hacerse en <5 minutos por Oscar o Rebeca, sin tocar el workflow.

**Resumen de la cadencia final post-migración:**

```
Lead no responde
    └── [Fase 1: waves cortas] 1h → 3h → 5h
         └── (si sigue sin responder)
              └── [Fase 2: reactivadores] 24h → 48h → 120h (día 5) → 168h (día 7 "ÚLTIMO DÍA")
                   └── (si sigue sin responder) → "En espera" (IA activa)
                        └── 6 meses sin actividad → "Ventas perdidas real" (IA off)
```

**Cadencia Fase 2 configurable:** Oscar necesita poder activar/desactivar waves R1-R4 sin rediseñar el workflow (por presupuesto de plantillas Meta). Implementar como GHL Custom Values: `re_engagement_active_waves = "R1,R2,R3,R4"` — el workflow salta los waves no listados.

---

### 3.6 Sandalias delgadas — ✅ CERRADA

**Precio confirmado:** **USD 25** (no $24 como aparece en `textos_salesbots.txt:7` ni $24 en línea 99). El texto del salesbot está obsoleto y debe actualizarse en la migración.

**Implicación:** consolidar **catálogo final 2026**:
- Sandalias delgadas: **$25**
- Sandalias gruesas: **$30**
- Pantuflas: **$30**
- Cilindros: **$10**
- Kit anticruda: **$10**
- Mandiles: **$12**
- Vasos popote: **$35**
- Bolsa personalizada: **$7**

---

### Tareas técnicas pendientes (no bloquean Etapa 3 conceptual)

- **3.7** Extraer **todos** los system/user prompts del JSON del workflow main-v2 y documentarlos (cliente lo pidió en E.4). Lista: AI Agent (Router), AI Agent Starter, AI Agent Main Image, AI Agent Products, AI Agent Recolector, Recolector1, Analyze image, Necesita Respuesta Especial, Message a model, Message a model1, Formatear mensaje1.
- **3.8** Documentar función exacta del bot `R2 GENERICO` (`bot_id` 20998): cuándo se dispara, qué texto envía, si aplica a todos los flujos o solo a leads sin producto.
- **3.9** Diseñar workflow GHL "Inactivity Sweep" para transición automática "En espera" → "Ventas perdidas real" a 6 meses (§3.4).

---

## §4. Inconsistencias detectadas y reconciliación

| # | Conflicto | Fuente A | Fuente B | Reconciliación |
|---|-----------|----------|----------|----------------|
| 4.1 | Cadencia seguimientos | Doc 06 B.2: "1h/3h/24h" | Reunión 2.1: "24h/48h/72h hasta 7 días" | Reunión gana de cara al cliente; doc 06 podría referirse a delays internos. Confirmar con 3.5 |
| 4.2 | Modelo imágenes | Doc 06 C.3: "Vision GHL" | Reunión 2.7: "Claude híbrido" | Reunión es posterior — gana. Pero 3.2 puede revertir si la investigación muestra que es problema de prompt |
| 4.3 | Pipeline post-pago | Doc 06 F.1 original: "In Production" consolidado | Reunión 2.2: 3 etapas separadas | Reunión gana → ya reflejado en §2.2 |
| 4.4 | Personalización textos | Doc 06 D.3: salesbots hardcoded | Reunión 2.1: LLM con contexto | Reunión gana → cambia arquitectura de re-engagement |
| 4.5 | Memoria | Doc 06 C.2: "REMOVE Postgres pero guardar historial" | Reunión 2.4: A o B (pendiente) | Pendiente §3.1 |
| 4.6 | Sandalias delgadas | Textos: $24 | Doc 06 E.7: $25 | Pendiente §3.6 |

---

## §5. Listo para Etapa 3 cuando…

- [x] §3.1 Memoria — Opción B (Supabase Pro USD 25/mes) ✅
- [x] §3.2 Imágenes — reformular prompt + subir a gpt-4.1, no migrar a Claude todavía ✅
- [x] §3.3 Pipelines LIMBO — archivar todos, solo migrar IA + GENERAL ✅
- [x] §3.4 "Ventas perdidas real" — automática a 6 meses de inactividad ✅
- [x] §3.6 Precio sandalias delgadas — $25 ✅
- [ ] §3.5 Mapeo funcional de los 4 sub-workflows de seguimiento + reconciliación con voluntad de Oscar (única decisión pendiente — preguntar a Oscar si conserva lógica dual waves-cortas + campaña-7d, o uniformiza)

**Tareas técnicas paralelas a Etapa 3:**
- [ ] 3.7 Extraer todos los system/user prompts del workflow main-v2
- [ ] 3.8 Documentar función del bot R2 GENERICO (20998)
- [ ] 3.9 Diseñar workflow "Inactivity Sweep" 6 meses

**Estado:** **6 de 6 decisiones bloqueantes cerradas (100%).** ✅ Etapa 2 completa.

**Pendiente antes de comenzar Etapa 3:**
- [x] Confirmar con Oscar la "memoria extra" — es Supabase Pro que ya paga. Ya existe, no hay costo adicional. ✅
- [ ] Verificar el valor de `Wait2` en n8n (debe ser 5h según Oscar)
- [ ] Test plan de imágenes §3.2 (puede correr en paralelo a Etapa 3)

**Impacto en timeline:** mantenible ~15 julio. Etapa 3 puede arrancar.
