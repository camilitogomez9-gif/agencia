# Arquitectura GHL — Happy Flops (visión general)

> **Etapa 3 — Diseño de arquitectura.** Documento maestro que define la solución post-migración. Los documentos `01`–`07` profundizan en cada subsistema. Esta es la pieza de referencia obligatoria antes de implementar.

**Versión:** 1.0
**Fecha:** 2026-05-12
**Inputs:** `01_logica_actual/01_mapa_funcional.md` · `02_logica_validada/01_decisiones.md` · reunión Oscar 2026-05-09 · audios Oscar 2026-05-12

---

## §1. Objetivo de la arquitectura

Reemplazar Kommo + AmoCRM legacy + Airtable como source-of-truth + 6 LLMs orquestados en n8n + 4 sub-workflows redundantes de seguimiento, por una arquitectura simplificada centrada en **GoHighLevel** como CRM/canal + **n8n** como orquestador de IA + **Supabase** (ya en uso) como memoria persistente + **2 LLMs** (1 Vendedor + 1 Vision Classifier).

**Lo que no cambia:**
- El comportamiento externo de Rebeca (saludo, identificación de evento, ficha de productos, cotización, cierre, derivación humana).
- El catálogo y los precios (validados en Etapa 2).
- Las reglas críticas (sandalias solo mujeres, no revelar peso, no modificar precios, etc.).
- El stack actual de n8n y Supabase Pro (ya operativo y pagado por Oscar).

**Lo que cambia:**
- CRM: Kommo → GHL.
- Canal: salesbots Kommo (~30 nodos) → GHL Workflow Actions nativas + Conversations API.
- Catálogo: Airtable → GHL Custom Object + assets nativos.
- Pipeline: 31+ etapas → 11 etapas + 4 tags operativos.
- LLMs: 6 agentes orquestados → 1 Vendedor unificado + 1 Vision Classifier (con prompt reformulado).
- Memoria: Postgres genérico → Supabase Pro (mismo schema LangChain, sin migración).
- Seguimientos: 4 sub-workflows duplicados → 1 sistema dual (Fase 1 + Fase 2) configurable.

---

## §2. Principios de diseño

1. **Source of truth única por dominio.**
   - Estado del lead (etapa, custom data): GHL.
   - Memoria conversacional completa: Supabase.
   - Catálogo de productos: GHL Custom Object (migrado desde Airtable).
   - Configuración de reactivadores: GHL Custom Values (editable por Oscar/Rebeca sin tocar workflows).

2. **n8n orquesta IA, GHL orquesta CRM/comunicación.** Cada herramienta hace lo que mejor hace. GHL no contiene lógica de prompts; n8n no contiene estado de lead.

3. **Lógica determinística donde sea posible.** Eliminar LLMs "helper" (formato, decisión de respuesta especial) cuyo trabajo puede hacer un workflow GHL o un Code node n8n con regex.

4. **Configuración separada del código.** Lo que Oscar quiera cambiar sin desarrollo (cadencias, productos, precios, mensajes hardcoded, días de promo activos) vive en GHL Custom Values / Custom Objects, no en workflows.

5. **Fail-safe a humano.** Si la IA no resuelve, deriva a atención personalizada — siempre. Nunca "intenta de nuevo en loop".

6. **MVP cutover primero, mejoras después.** Replicar el comportamiento actual + las 2 mejoras must-have (seguimientos personalizados, prompt de visión reformulado). Métricas y promociones A/B son post-cutover (agosto-septiembre).

---

## §3. Componentes de la solución

```
┌──────────────────────────────────────────────────────────────────────┐
│                          WhatsApp (lead)                             │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
                             │  inbound/outbound (Meta WABA via GHL)
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       GoHighLevel (sub-account HPF)                  │
│  • Conversations Inbox (WA, IG, FB en el futuro)                     │
│  • Pipeline "IA" (11 etapas) + Tags operativos                       │
│  • Custom Fields del Contact/Opportunity (datos del lead)            │
│  • Custom Values del sub-account (configuración global)              │
│  • Custom Object "Producto" (catálogo, 5 productos × 3 eventos)      │
│  • GHL Workflows (orquestación CRM + envío de mensajes)              │
│       ├── WF-01: Inbound Router (msg → n8n)                          │
│       ├── WF-02: Re-engagement (Fase 1 + Fase 2)                     │
│       ├── WF-03: Inactivity Sweep (6m → Ventas perdidas real)        │
│       ├── WF-04: Pago detectado (transición etapas)                  │
│       ├── WF-05: Business Hours (auto-reply vacaciones)              │
│       └── WF-06: Stage transitions automáticas                       │
└─────┬──────────────────────────────────────────────────┬─────────────┘
      │                                                  │
      │ webhook outbound                                 │ Conversations API
      │ (mensaje nuevo del lead)                         │ (enviar respuesta)
      ▼                                                  ▲
┌─────────────────────────────────────────────────────┐  │
│                    n8n (orquestador IA)             │  │
│  • Inbound webhook (recibe msg desde GHL WF-01)     │  │
│  • Debouncing (Wait 30-45s + Redis o GHL native)    │  │
│  • Classifier: tipo input (texto/audio/imagen/PDF)  │  │
│  • Audio → OpenAI Whisper → texto                   │  │
│  • Imagen → Vision Classifier (gpt-4.1)             │  │
│  • Texto → Vendedor (gpt-4.1) con tools             │  │
│       └── tools: CATALOGO, COTIZADOR, ATENCION_HUM. │  │
│  • Memory: Supabase (lectura + escritura)           │  │
│  • Output → POST a GHL Conversations API ───────────┼──┘
└─────┬──────────────────────────────────────┬────────┘
      │                                      │
      │  Postgres/LangChain Memory           │  OpenAI API
      ▼                                      ▼
┌──────────────────────────────────┐  ┌───────────────────────────┐
│        Supabase Pro              │  │      OpenAI               │
│  • tabla messages (existente)    │  │  • gpt-4.1 (vendedor)     │
│  • tabla followups (tracking)    │  │  • gpt-4.1 (vision)       │
│  • tabla leads_metrics (post-MVP)│  │  • whisper-1 (audio)      │
└──────────────────────────────────┘  └───────────────────────────┘

[Notificaciones operativas]
GHL Workflow → Telegram (vía HTTP webhook a Bot la agencia):
  • imagen no clasificable
  • PDF recibido
  • comprobante de pago detectado
  • lead derivado a humano (Atención Personalizada)
```

**Eliminados:** Kommo · AmoCRM legacy v2 · 30+ salesbots Kommo · Airtable (como source of truth) · Redis (a evaluar — ver §5.3).

---

## §4. Cambios estructurales clave (resumen ejecutivo)

| Subsistema | Hoy | Post-migración |
|---|---|---|
| **CRM/canal** | Kommo (subdomain `happyflopss.kommo.com`) | GHL sub-account dedicado |
| **Canal WhatsApp** | Kommo conecta vía Meta WABA | GHL conecta vía Meta WABA (no cambia el número, sí el wrapper) |
| **Pipelines activos** | 13 (1 activo IA + 12 limbo) | 1 (Pipeline IA en GHL) + Lista "Ventas Manuales" (ex-GENERAL) |
| **Etapas del pipeline** | 31+ con sub-pipeline R1-R5 sin/con info/ap | 11 etapas + 4 tags operativos (`human_takeover`, `paused`, `re_engagement_active`, `vacaciones`) |
| **Mensajes outbound** | 30+ salesbot legacy + sendMessage directo | GHL Conversations API (Send SMS/WA Action) desde Workflows |
| **Catálogo** | Airtable (6 tablas, `bot_id` → salesbot) | GHL Custom Object "Producto" + assets nativos (foto + ficha + precio) |
| **Mensajes hardcodeados** | Pre-cargados en cada salesbot Kommo | Templates GHL + Custom Values (editables por Oscar) |
| **Agente Router** | LLM dedicado (357 líneas de prompt) que devuelve `{step}` | Eliminado. Lógica de step → GHL Workflow conditions sobre Custom Field `step_actual` o stage del Opportunity |
| **AI Agent Starter** | LLM con mensaje fijo | Mensaje fijo en GHL Workflow (sin LLM). Trigger: Conversation Started + Opportunity nueva |
| **AI Agent Main Image** | LLM que clasifica evento y devuelve imagen | LLM unificado en Vendedor (con tool `IDENTIFICAR_EVENTO`) + GHL Workflow que dispara envío del asset según `evento_detectado` |
| **AI Agent Products** | LLM que devuelve JSON de productos | Unificado en Vendedor (con tool `MOSTRAR_PRODUCTOS`) |
| **AI Agent Recolector / Recolector1** | 2 LLMs (texto / imagen) con ~95% prompt idéntico | 1 LLM "Vendedor" en n8n, con preprocesamiento de input que normaliza ambos casos |
| **Analyze image** | gpt-4o, prompt actual con problemas | Vision Classifier en n8n, gpt-4.1 + prompt reformulado (5 categorías cerradas, JSON estructurado, prohibición de evasivas) |
| **Necesita Respuesta Especial / Message a model / Formatear mensaje1** | 3-4 LLMs helper | Eliminados. División de mensajes y selección de adjuntos = lógica determinística en GHL Workflow / Code node n8n |
| **Sub-workflows seguimiento** | 4 (Rebeca, Imagen, Cotización, 7pasos) con lógicas duplicadas | 1 sistema unificado en GHL: WF-02 "Re-engagement" con 2 fases configurables |
| **Debouncing** | Redis dual 15s/50s | Único 30-45s — implementación a definir (Redis si se mantiene, o GHL Wait + collector) — ver §5.3 |
| **Horario laboral** | Code nodes en n8n + IF múltiples | GHL Business Hours nativo + WF-05 |
| **Memoria conversacional** | Postgres genérico (LangChain) | Supabase Pro (mismo schema, drop-in) |
| **Estado del lead (step, evento, productos)** | Memoria conversacional (implícito) + status_id Kommo | Custom Fields del Opportunity en GHL + memoria conversacional Supabase |
| **Notificaciones equipo** | Telegram desde n8n | Telegram desde GHL Workflow (HTTP action) |

---

## §5. Decisiones arquitectónicas críticas

### §5.1 ¿Por qué GHL Workflows como orquestador CRM en lugar de n8n para todo?

Hoy n8n hace dos cosas distintas: (1) orquesta IA (clasificación, prompts, tools) y (2) orquesta CRM (mover etapas, enviar salesbots, detectar pagos, manejar timers). En la migración, **separamos esas dos responsabilidades**:

- **GHL Workflows = orquestador de negocio.** Maneja stages, envía mensajes vía Conversations API, dispara reactivadores, aplica Business Hours, notifica al equipo. La razón: GHL ya tiene primitivas nativas para esto (Wait, Trigger by Stage, Send Message, Apply Tag), y Oscar/Rebeca pueden editarlas desde la UI sin dev.
- **n8n = orquestador de IA.** Recibe el mensaje desde GHL, llama a LLMs, gestiona memoria, devuelve el texto de la respuesta a GHL. La razón: n8n es el único lugar donde tenemos control fino sobre prompts, tools y modelos.

**Borde:** la transición de stage del Opportunity la dispara GHL (al recibir respuesta del Vendedor que contenga ciertas señales, ej. "7 DIAS DE PROMO" → mover a "Cotizada"). N8n no toca stages directamente; envía el texto + metadata, GHL decide el efecto en el pipeline.

### §5.2 ¿Por qué unificar 6 LLMs en 2?

Auditoría de Etapa 1 mostró que 4 de los 6 LLMs hacen tareas que un Vendedor único con tools puede absorber sin pérdida de calidad:

- **Router (decide `step`):** redundante — la etapa del Opportunity en GHL ya representa el step. El Vendedor decide qué hacer mirando el contexto + stage actual.
- **Starter (saluda):** mensaje fijo. No necesita LLM. GHL Workflow lo envía con un `Send Message` action al trigger "Opportunity Created".
- **Main Image (clasifica evento + envía imagen):** la clasificación de evento se hace dentro del Vendedor con una tool `IDENTIFICAR_EVENTO`. El envío de imagen lo hace GHL Workflow al detectar `Custom Field evento_detectado` actualizado.
- **Products (devuelve catálogo):** el Vendedor llama tool `MOSTRAR_PRODUCTOS(evento, productos[])` y GHL Workflow envía las fichas correspondientes del Custom Object.

Los 2 LLMs que quedan:
1. **Vendedor (gpt-4.1):** conversacional, con 3 tools (`IDENTIFICAR_EVENTO`, `MOSTRAR_PRODUCTOS`, `COTIZADOR`, `ATENCION_PERSONALIZADA`).
2. **Vision Classifier (gpt-4.1):** clasifica imágenes en 5 categorías + "comprobante de pago" + "ninguno". Prompt reformulado según §3.2 del doc de decisiones.

### §5.3 Debouncing: ¿se mantiene Redis o no?

**Tres opciones:**

- **A — Mantener Redis (status quo):** debouncing por contact_id con TTL 30-45s. n8n acumula mensajes en ráfaga, procesa solo el último. **Pro:** ya funciona. **Con:** una pieza más que mantener.
- **B — GHL native Wait + collector:** GHL Workflow "espera 30s, recolecta mensajes nuevos del contacto, envía agregado al webhook n8n". **Pro:** menos infra. **Con:** requiere validar que GHL pueda agregar mensajes en ese intervalo sin disparar el workflow varias veces.
- **C — n8n native Wait + Postgres lookup:** n8n recibe webhook, espera 30s, consulta últimos mensajes del lead en Supabase para ver si llegó algo nuevo. **Pro:** todo en una sola pieza. **Con:** N requests a Supabase por mensaje.

**Recomendación:** **A** para MVP (no romper lo que funciona) → evaluar B post-cutover si hay valor.

### §5.4 ¿Catálogo en GHL Custom Object o en Supabase?

El catálogo tiene baja cardinalidad (5 productos × 3 eventos = máx 15 combinaciones) y baja frecuencia de actualización. Dos opciones:

- **GHL Custom Object "Producto":** registros con campos (evento, producto, precio_unitario, minimo, peso, descripcion, asset_url). Pro: visible desde la UI de GHL, editable por Oscar. Con: GHL Custom Objects tienen limitaciones de asociación.
- **Supabase tabla `catalogo`:** consulta desde n8n. Pro: SQL puro, flexible. Con: Oscar no lo edita desde GHL.

**Recomendación:** **GHL Custom Object** — Oscar valora poder editar precios y descripciones desde un lugar visible. Los assets (fotos de productos) viven en GHL Files. El detalle en §02_data_model.

### §5.5 ¿IA reactivada en "Producción" para detectar 2do pago?

Sí (decisión Etapa 2). Mecanismo: el Vision Classifier sigue corriendo siempre que llega una imagen — si detecta "comprobante de pago" y el lead está en stage "Producción", GHL Workflow lo mueve a "Pago Liquidación". El Vendedor no se reactiva conversacionalmente; solo el clasificador de imágenes y el workflow.

### §5.6 "En espera" vs "Ventas perdidas real"

- **"En espera"** (IA activa): destino por defecto cuando termina la campaña de re-engagement (Fase 2, día 7) sin respuesta. La IA sigue contestando si el lead vuelve a escribir.
- **"Ventas perdidas real"** (IA off): transición automática vía WF-03 "Inactivity Sweep" cuando `last_activity_at < now - 6m` y stage = "En espera".

Implementación detallada en `07_post_venta_y_handoff.md`.

---

## §6. Mapeo de funcionalidades actuales → componentes GHL

| Funcionalidad actual | Componente GHL/n8n nuevo |
|---|---|
| Webhook Kommo → n8n | Trigger GHL: "Inbound Message" → HTTP Action: POST a webhook n8n |
| `If25` (entity_id == 8075544, sandbox Oscar) | Custom Field `is_test_lead = true` en contacto de Oscar (sin lógica de flujo) |
| `Get_Contact` / `Get_Entity` | Datos disponibles en el payload del trigger GHL (no requiere fetch adicional) |
| `No es IA` (filtro de pipeline) | GHL Workflow Filter: `Pipeline = IA` (auto-aplica) |
| `If21` / `If20` (filtros por status válido) | GHL Workflow Filter: `Opportunity Status NOT IN [Atención Personalizada, Confirmar Pago, ...]` |
| `checkType` (texto/audio/imagen/PDF) | n8n Switch sobre `message.type` (recibido desde webhook) |
| Transcribir audio (Whisper) | n8n: OpenAI Whisper API call (sin cambios) |
| `Analyze image3` (gpt-4o) | n8n: Vision Classifier (gpt-4.1 + prompt reformulado) |
| Anti-ráfaga Redis | Redis + n8n Wait (status quo, ver §5.3) |
| LangChain Memory (Postgres) | Supabase Pro (mismo schema, mismo session_id `<telefono>_2131`) |
| `Exist_Interaction?` (lead nuevo vs reincidente) | n8n: query Supabase by session_id → empty == nuevo |
| `AI Agent Starter` | GHL Workflow: trigger "Opportunity Created" → Send Message (texto fijo) → Apply Tag `greeted` |
| `AI Agent` (Router) | **ELIMINADO.** Lógica de step → branching en GHL Workflow basado en Opportunity Stage |
| `AI Agent Main Image` | n8n: Vendedor con tool `IDENTIFICAR_EVENTO`. GHL Workflow trigger "Custom Field evento_detectado changed" → enviar imagen del Custom Object Imagen Principal |
| `AI Agent Products` | n8n: Vendedor con tool `MOSTRAR_PRODUCTOS(evento, productos[])`. GHL Workflow envía fichas según output |
| `AI Agent Recolector` + `Recolector1` | **UNIFICADOS** en Vendedor (gpt-4.1) con preprocesamiento de input (normaliza texto vs `"Te envío imagen de [producto]"`) |
| `CALCULADORA` (tool de envío) | Vendedor con tool `COTIZADOR(producto, cantidad, cp)` que llama API de paquetería o tabla hardcoded en Supabase/GHL |
| `ATENCION_PERSONALIZADA` (tool) | Vendedor con tool `ATENCION_PERSONALIZADA(motivo)` → marca Opportunity con tag `human_takeover` + notifica Telegram vía GHL HTTP action |
| `Necesita Respuesta Especial` | **ELIMINADO.** Lógica de adjuntos → regex/conditions en GHL Workflow sobre output del Vendedor |
| `Message a model` / `Message a model1` / `Formatear mensaje1` | **ELIMINADOS.** División de mensajes → GHL Workflow split por longitud + Wait 2s entre partes |
| `Envio Mensaje*` (salesbot legacy) | GHL Send WhatsApp Message action (texto plano o con asset adjunto del Custom Object) |
| Sub-workflow `Seg. Rebeca` | WF-02 Fase 1: Wave 1h, 3h, 5h (mensajes con contexto generado por Vendedor) |
| Sub-workflow `Seg. Imagen` | Idem WF-02 Fase 1 |
| Sub-workflow `Seg. Cotización` | Idem WF-02 Fase 1 |
| Sub-workflow `Seg. 7 pasos` | WF-02 Fase 2: Wave 24h, 48h, 120h, 168h (mensajes con contexto + activación configurable por Custom Value) |
| Move a `r1/r2/r3/r4/r5 sin/con info/ap` (17 etapas) | **ELIMINADO.** Estado de wave → tag `wave_R1`...`wave_R4` + Custom Field `last_re_engagement_wave` |
| Move a `Ventas Perdidos` (143) tras 24h | WF-02 transition: fin de Fase 2 → stage "En espera" |
| `PAGO SIN DISEÑO` / `DISEÑO` / `en produccion` | 3 stages separadas en pipeline GHL (decisión Oscar §2.2 reunión) |
| Detección comprobante pago (Vision) → mover stage | WF-04 "Pago detectado": trigger sobre output del Vision Classifier |
| Mensaje "Foto Vacaciones" fuera de horario | WF-05 "Vacaciones": condition `Business Hours OFF` → Send Message (texto en Custom Value `mensaje_vacaciones`) |
| Notificaciones Telegram | GHL Workflow HTTP action → Telegram Bot API |

---

## §7. Stack final y costos (referencia)

| Componente | Hoy | Post-migración | Costo mensual |
|---|---|---|---|
| CRM + canal | Kommo (~USD 50–100/mes) | GHL Unlimited | **USD 297/mes** |
| Orquestación | n8n self-hosted | n8n self-hosted (sin cambio) | USD 0 marginal |
| Memoria conversacional | Supabase Pro (ya pago) | Supabase Pro (sin cambio) | USD 25/mes (ya pago) |
| Debouncing | Redis (ya pago) | Redis (sin cambio) | USD 0 marginal |
| WhatsApp platform fee | (incluido en Kommo) | GHL WA add-on | USD 10/mes |
| Meta WABA passthrough | (incluido en Kommo) | Pago directo Meta vía GHL | ~USD 100–400/mes |
| LLM tokens (OpenAI) | gpt-4o + 4.1-mini + 5-mini | gpt-4.1 (Vendedor + Vision) + Whisper | ~USD 50–150/mes |
| **TOTAL estimado** |  |  | **USD 482–882/mes** |

> Ahorros estructurales: eliminación de 4 LLMs helper (-20% tokens), simplificación de pipeline (menos workflow executions). El costo total post-migración es comparable o levemente superior al actual, pero **deja al sistema escalable y mantenible.**

---

## §8. Roadmap MVP cutover y mejoras

### §8.1 MVP cutover (julio-agosto 2026)

Replicar el comportamiento actual + 2 mejoras must-have:

1. **Vendedor unificado** con 4 tools (eliminación de Router, Starter, Main Image, Products como LLMs separados).
2. **Vision Classifier** con prompt reformulado (fix de "qué bonito diseño").
3. **Pipeline 11 etapas + tags** (eliminación de R1-R5 granular).
4. **Re-engagement dual** (Fase 1 + Fase 2) con flexibilidad configurable.
5. **Personalización de mensajes de reactivación** con contexto de cotización.
6. **"En espera" + "Ventas perdidas real"** automática a 6 meses.
7. **IA reactivada en Producción** para detectar 2do pago.

### §8.2 Post-cutover (septiembre+ 2026)

Features que la reunión introdujo pero que NO bloquean el cutover:

1. **Tracking de tiempo de cierre por lead** (Custom Fields + tabla `leads_metrics` en Supabase).
2. **Sistema de promociones rotativas A/B** (round-robin con Custom Value `promo_activa` + métricas).
3. **Test plan de Vision Classifier** (4 brazos A/B/C/D) para validar definitivamente que no necesitamos Claude.
4. **Retrieval semántico** con Pinecone si el caso de "lead vuelve a los 5 meses" lo justifica.

### §8.3 Fuera de scope explícito

- Migrar los 12 pipelines LIMBO de Kommo (decisión: archivar todos).
- Mantener AmoCRM legacy v2 endpoints (decisión: eliminar después del cutover).
- Mantener salesbots Kommo (decisión: reemplazados por GHL Workflow actions).

---

## §9. Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| GHL es nuevo para el el equipo (curva de aprendizaje) | Alta | Medio | Reservar 1 semana de exploración + prototipos antes de la implementación oficial. Apalancarse en docs oficiales + comunidad. |
| Límite no documentado de medios en GHL (audios/imágenes) | Media | Medio | Si se alcanza, borrar conversaciones viejas de GHL (todo persiste en Supabase). Confirmar con soporte GHL antes del go-live. |
| Cambio de WhatsApp BSP impacta calidad/deliverability | Baja | Alto | Coordinar con Meta + GHL para mantener el mismo número con la nueva conexión. No cambiar número de cara al cliente. |
| Vision Classifier sigue fallando con prompt nuevo | Media | Medio | Test plan A/B/C/D (§3.2 doc decisiones) antes de cutover. Si falla, escalar a Claude Sonnet 4.5. |
| Custom Object Producto tiene limitaciones de asociación con Contact | Media | Bajo | Plan B: catálogo en Supabase, consulta por tool del Vendedor. |
| Scope creep en julio compromete cutover de agosto | Alta | Alto | Disciplinar MVP — métricas y A/B promos van post-cutover, no antes. |
| Algunos leads históricos quedan huérfanos al pasar de Kommo a GHL | Media | Medio | Estrategia de cutover paralelo (1-2 semanas overlap) + script de import de contactos activos a GHL. |

---

## §10. Lectura por documento (índice de Etapa 3)

| Documento | Contenido |
|---|---|
| `00_arquitectura_general.md` | (este) Visión completa, principios, mapeo, riesgos |
| `01_pipeline_ghl.md` | 11 etapas del pipeline IA + tags + transiciones automáticas y manuales + IA on/off por etapa |
| `02_data_model.md` | Custom Fields del Contact y Opportunity, Custom Values del sub-account, Custom Object "Producto" con schema completo |
| `03_workflows_ghl.md` | Especificación de los 6 GHL Workflows (WF-01 a WF-06) con triggers, branching y acciones |
| `04_agentes_llm.md` | Arquitectura LLMs: Vendedor (system prompt completo + 4 tools) y Vision Classifier (system prompt completo) |
| `05_reengagement.md` | Sistema dual de re-engagement: Fase 1 (1h/3h/5h) + Fase 2 configurable (24h/48h/120h/168h) |
| `06_integraciones.md` | Webhooks, schemas de payloads, API contracts entre GHL ↔ n8n ↔ Supabase ↔ OpenAI ↔ Telegram |
| `07_post_venta_y_handoff.md` | Stages post-pago, atención personalizada, "En espera", "Ventas perdidas real" automática, IA reactivada en Producción |
