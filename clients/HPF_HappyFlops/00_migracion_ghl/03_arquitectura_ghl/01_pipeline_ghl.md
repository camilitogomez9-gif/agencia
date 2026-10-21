# Pipeline GHL — Happy Flops

> **Etapa 3.** Diseño definitivo del pipeline IA en GHL: stages, transiciones, IA on/off, tags operativos.

> ⚠️ **NOMBRES EN ESPAÑOL (2026-06-19):** este doc de diseño usa nombres de stage/tag en inglés (histórico). Los nombres **reales que se crean en la UI de GHL están en español** — ver la tabla de mapeo EN→ES en `04_guia_migracion/02_pipeline_y_campos.md` (sección "Convención de idioma"). Al implementar, usar SIEMPRE los nombres en español de M2; este doc queda como referencia conceptual.

---

## §1. Pipelines en el sub-account

GHL maneja todo el embudo de cara al lead. Tenemos **1 pipeline principal automatizado + 1 pipeline manual** (residual del GENERAL de Kommo).

| Pipeline GHL | ID lógico | Origen | Propósito | IA |
|---|---|---|---|---|
| `Pipeline IA` | `pipe_ia` | Migrado del Kommo `IA (11622596)` | Embudo principal del agente automatizado | ✅ |
| `Ventas Manuales` | `pipe_manual` | Migrado del Kommo `GENERAL (9018931)` | Casos atendidos 100% por humanos (no migrados, gestión manual del equipo) | ❌ |

Los 11 pipelines LIMBO de Kommo **NO se migran** (decisión §3.3 Etapa 2).

---

## §2. Stages del Pipeline IA

11 stages secuenciales + 4 stages terminales/laterales. Reemplazan las 31+ etapas actuales de Kommo (incluyendo el sub-pipeline R1-R5 sin/con info/ap, que pasa a ser un sistema de tags + custom fields — ver §3).

| # | Stage GHL | Equivalente Kommo | IA activa | Quién la mueve | Descripción |
|---|---|---|---|---|---|
| 1 | **New Lead** | `Incoming leads` (89263340) | ✅ | Auto (Trigger: Opportunity Created) | Lead recién entrado, sin saludo aún. Permanece <1s |
| 2 | **Greeted** | `ETAPA 1` (89263344) | ✅ | WF-06 (después de Send Saludo) | Saludo enviado, esperando que el lead identifique evento |
| 3 | **Event Identified** | `ETAPA 2` (93616832) | ✅ | WF-06 (cuando Custom Field `evento_detectado` se setea) | Lead identificó evento; imagen principal enviada |
| 4 | **Products Shown** | `ETAPA 3` (93616836) | ✅ | WF-06 (cuando Custom Field `productos_mostrados` se setea) | Productos del evento enviados al lead |
| 5 | **Quoted** | `ETAPA 4` (93616840) | ✅ | WF-06 (cuando output del Vendedor contiene `7 DIAS DE PROMO`) | Cotización emitida; recolectando datos finales |
| 6 | **Awaiting Payment** | `confirmar pago` (91450360) | ⏸️ Pausada (envía 1 mensaje y se calla) | WF-04 (Vision Classifier detectó comprobante + lead NO está en Production) | Comprobante recibido, humano debe validar manualmente |
| 7 | **Payment Confirmed (no design)** | `PAGO SIN DISEÑO` (89263352) | ❌ | Manual (equipo confirma pago) | Pago confirmado, diseñadora aún no inició diseño |
| 8 | **Design In Progress** | `DISEÑO` (91246120) | ❌ | Manual (diseñadora) | Diseño enviado al lead, esperando aprobación |
| 9 | **In Production** | `en produccion` (100395519) | ⚡ Reactivada (solo Vision Classifier) | Manual (equipo, post aprobación de diseño) | Producción física en curso. IA detecta segundo pago. |
| 10 | **Awaiting Final Payment** | `pago liquidacion` (100395523) | ⏸️ Pausada | WF-04 (Vision Classifier detectó comprobante + lead EN Production) | Pago de liquidación recibido, humano valida y procede al envío |
| 11 | **Won** | `Logrado con éxito` (142) | ❌ | Manual (post-envío) | Venta completada |

### Stages terminales/laterales (no son secuenciales)

| Stage | Equivalente Kommo | IA activa | Quién la mueve | Descripción |
|---|---|---|---|---|
| **Human Takeover** | `atencion personalizada` (91266100) | ❌ | Tool `ATENCION_PERSONALIZADA` (Vendedor) o manual | Humano tomó la conversación. IA en silencio hasta que humano libere. |
| **En espera** | (nueva — antes era `r5 sin/con info` + `Ventas Perdidos` parcial) | ✅ | WF-02 al cerrar Fase 2 sin respuesta | Lead no compró en el ciclo de promo. IA sigue activa si el lead vuelve a escribir. |
| **Ventas Perdidas Real** | `Ventas Perdidos` (143) | ❌ | WF-03 "Inactivity Sweep" automático a 6 meses | Sin actividad por >6 meses. IA off. Equipo puede gestionar manualmente. |
| **Quiere comprar más adelante** | `quiere comprar mas adelante` (91408976) | ⏸️ Pausada (IA detecta y mueve, no responde proactivamente) | Vendedor lo detecta vía señal + tool específica (opcional, fase 2 post-cutover) | Lead expresó intención clara de comprar en futuro lejano (post-MVP) |

---

## §3. Tags operativos (reemplazo del sub-pipeline R1-R5)

En lugar de 17 etapas (r1/r2/r3/r4/r5 × sin info/con info/ap), usamos **tags + custom fields** que cualquier workflow puede leer.

### §3.1 Tags principales

| Tag | Se aplica cuando | Se quita cuando | Efecto |
|---|---|---|---|
| `human_takeover` | Vendedor llama tool ATENCION_PERSONALIZADA, o equipo lo aplica manualmente | Manual (equipo cierra la conversación humana) | Detiene WF-01 (no llega más al Vendedor); detiene WF-02 (no envía reactivadores); inbox marca al lead con prioridad |
| `re_engagement_phase_1` | WF-02 al iniciar Fase 1 (post último mensaje del Vendedor sin respuesta del lead) | Lead responde, o se completa Fase 1, o pasa a Fase 2 | Marcador de que está en ciclo de waves cortas |
| `re_engagement_phase_2` | WF-02 al completar Fase 1 sin respuesta | Lead responde, o se completa Fase 2 (pasa a "En espera") | Marcador de que está en ciclo de campaña 7 días |
| `paused` | Custom Field `Business Hours = OFF` + ciertas stages | Inicio de business hours | Detiene envíos automáticos no-críticos |
| `vacaciones` | Cliente seteó "estamos de vacaciones" (Custom Value global) | Cliente lo desactiva | Misma lógica que `paused` pero permanente, dispara mensaje "Foto Vacaciones" |
| `is_test_lead` | Manualmente al contacto de Oscar (entity_id 8075544 históricamente) | Manual | Si el equipo quiere segmentar pruebas. No tiene efecto en flujo. |
| `vip` | Manual | Manual | (Opcional post-MVP) Trato preferencial / SLA distinto |
| `repeat_buyer` | Auto cuando ya cerró un Won y vuelve a entrar | Nunca | Marcador para reportes y posiblemente bypassar saludo inicial |

### §3.2 Custom Fields que reemplazan información de etapa

| Custom Field | Tipo | Valores | Reemplaza |
|---|---|---|---|
| `last_re_engagement_wave` | Texto | `P1_W1`, `P1_W2`, `P1_W3`, `P2_W1`, `P2_W2`, `P2_W3`, `P2_W4` | Granularidad de R1-R5 sin/con info |
| `re_engagement_started_at` | Datetime | ISO timestamp | Saber cuándo arrancó el ciclo |
| `re_engagement_paused` | Boolean | true/false | Si Oscar pausó manualmente este lead |
| `had_information` | Boolean | true/false | Reemplaza distinción "sin info" / "con info" (true si llegó a stage Products Shown o más) |

> Estos viven en el Opportunity (no en el Contact), porque el ciclo de re-engagement aplica a un negocio específico, no a la persona.

---

## §4. Transiciones automatizadas

### §4.1 Transiciones gobernadas por WF-06 "Stage Transitions"

WF-06 es un solo workflow GHL que escucha eventos del Vendedor (output del LLM en n8n viene como response a la API call, GHL lo procesa) y mueve stages según contenido / campos actualizados.

| Trigger | Condición | Acción |
|---|---|---|
| Opportunity Created en `Pipeline IA` | siempre | Move to `New Lead` → ejecutar saludo (WF-01 Section A) → Move to `Greeted` |
| Custom Field `evento_detectado` cambia a no-vacío | stage actual = `Greeted` | Move to `Event Identified` |
| Custom Field `productos_mostrados` cambia a no-vacío | stage actual = `Event Identified` | Move to `Products Shown` |
| Mensaje saliente del Vendedor contiene `⏳(7 DIAS DE PROMO)⏳` | stage actual = `Products Shown` | Move to `Quoted` |
| Vision Classifier devuelve `payment_proof: true` | stage actual ∈ {`Quoted`, `Awaiting Payment`} | Move to `Awaiting Payment` + notificar Telegram |
| Vision Classifier devuelve `payment_proof: true` | stage actual = `In Production` | Move to `Awaiting Final Payment` + notificar Telegram |
| Tool `ATENCION_PERSONALIZADA` invocada | cualquier stage | Apply tag `human_takeover` + notificar Telegram (no mueve stage, solo pausa) |
| WF-02 termina Fase 2 sin respuesta | stage actual ∈ {`Greeted`, `Event Identified`, `Products Shown`, `Quoted`} | Move to `En espera` |

### §4.2 Transiciones manuales (responsable: humano)

| De → A | Quién | Acción esperada |
|---|---|---|
| `Awaiting Payment` → `Payment Confirmed (no design)` | Equipo de pagos | Validar comprobante en horario laboral |
| `Payment Confirmed (no design)` → `Design In Progress` | Diseñadora | Subir diseño y notificar lead |
| `Design In Progress` → `In Production` | Diseñadora / equipo | Cliente aprobó diseño, mover a producción |
| `Awaiting Final Payment` → `Won` | Equipo | Validar liquidación + agendar envío |
| `Won` → `repeat_buyer` (tag, no stage) | Auto (WF-06) al cumplir 30 días post-Won (configurable) | Marcador para campañas futuras |
| Cualquier stage → `Human Takeover` (tag) | Equipo desde inbox | Cuando el equipo quiere intervenir antes de que la IA decida hacerlo |
| `Human Takeover` (tag) → quitar tag | Equipo | Reactivar IA tras resolver |
| `En espera` → `Won` o `Ventas Perdidas Real` o cualquier stage activa | Equipo | Caso por caso |

### §4.3 Transición automática time-based: 6 meses → Ventas Perdidas Real

WF-03 "Inactivity Sweep" corre **diariamente** y busca:
```
Opportunities WHERE
  stage = "En espera"
  AND last_activity_at < now() - 180 days
```

Para cada match: Move to `Ventas Perdidas Real`. Sin envío de mensaje (el lead ya está silencioso hace meses).

---

## §5. Reglas de IA on/off por stage

Resumen consolidado: cuándo el Vendedor responde, cuándo no.

| Stage | Vendedor responde? | Vision Classifier corre? | Razón |
|---|---|---|---|
| `New Lead` | ✅ (vía saludo) | ✅ | Inicio del flujo |
| `Greeted` | ✅ | ✅ | Conversación normal |
| `Event Identified` | ✅ | ✅ | Conversación normal |
| `Products Shown` | ✅ | ✅ | Conversación normal |
| `Quoted` | ✅ | ✅ | Conversación normal — puede recibir comprobante de pago |
| `Awaiting Payment` | ❌ | ✅ | Humano valida pago. Si lead pregunta, queda en cola hasta tag `human_takeover` removido manualmente. **Excepción:** si lead manda nueva imagen y es comprobante, Vision Classifier la procesa para no perder la transición. |
| `Payment Confirmed (no design)` | ❌ | ❌ | Diseñadora maneja |
| `Design In Progress` | ❌ | ❌ | Diseñadora maneja |
| `In Production` | ❌ conversacional | ✅ (solo para detectar pago liquidación) | Decisión clave: la IA detecta el 2do pago pero NO conversa. |
| `Awaiting Final Payment` | ❌ | ✅ | Humano valida |
| `Won` | ❌ | ❌ | Cerrado |
| `Human Takeover` (tag) | ❌ | ❌ | Humano explícitamente tomó el caso |
| `En espera` | ✅ | ✅ | Lead puede volver en cualquier momento; la IA lo recibe con contexto histórico (memoria de Supabase) |
| `Ventas Perdidas Real` | ❌ | ❌ | Marcado oficialmente como perdido |

### §5.1 Mecánica técnica del "IA off"

WF-01 "Inbound Router" (que recibe el mensaje de WhatsApp y decide si llama al Vendedor en n8n) tiene este filtro al inicio:

```
IF Opportunity.stage NOT IN [
  "New Lead", "Greeted", "Event Identified", "Products Shown",
  "Quoted", "En espera"
]
OR Opportunity.tag CONTAINS "human_takeover"
  THEN: do nothing (mensaje queda en inbox para humano)
ELSE:
  forward to n8n webhook
```

Excepción para Vision Classifier: si el mensaje es imagen y stage ∈ {`Awaiting Payment`, `In Production`, `Awaiting Final Payment`}, igualmente se procesa la imagen (no la conversación). Esto se maneja en una rama separada de WF-01 que llama a un endpoint distinto de n8n: `/vision-only` (solo clasifica, no llama al Vendedor).

---

## §6. Diagrama del flujo principal post-migración

```
            ┌──────────────────┐
            │   New Lead       │  (≤1s, auto a Greeted)
            └────────┬─────────┘
                     │ saludo automático
                     ▼
            ┌──────────────────┐
            │    Greeted       │ ◄────┐
            └────────┬─────────┘      │
                     │ evento detectado │
                     ▼                  │ (lead vuelve después de "En espera")
            ┌──────────────────┐      │
            │ Event Identified │ ◄────┤
            └────────┬─────────┘      │
                     │ productos pedidos │
                     ▼                  │
            ┌──────────────────┐      │
            │ Products Shown   │ ◄────┤
            └────────┬─────────┘      │
                     │ cotización emitida │
                     ▼                  │
            ┌──────────────────┐      │
            │     Quoted       │ ◄────┤
            └────────┬─────────┘      │
                     │ comprobante de pago detectado │
                     ▼                  │
            ┌──────────────────┐      │
            │ Awaiting Payment │      │
            │  (IA pausada)    │      │
            └────────┬─────────┘      │
                     │ humano valida    │
                     ▼                  │
            ┌──────────────────────┐  │
            │ Payment Confirmed    │  │
            │  (no design)         │  │
            └────────┬─────────────┘  │
                     │                  │
                     ▼                  │
            ┌──────────────────┐      │
            │ Design In        │      │
            │ Progress         │      │
            └────────┬─────────┘      │
                     │ diseño aprobado  │
                     ▼                  │
            ┌──────────────────┐      │
            │ In Production    │      │
            │ (IA: solo vision)│      │
            └────────┬─────────┘      │
                     │ comprobante de liquidación │
                     ▼                  │
            ┌──────────────────────┐  │
            │ Awaiting Final       │  │
            │   Payment            │  │
            └────────┬─────────────┘  │
                     │ humano valida    │
                     ▼                  │
            ┌──────────────────┐      │
            │      Won         │      │
            └──────────────────┘      │
                                      │
[En cualquier punto antes de Awaiting Payment, si el lead no responde:]
                                      │
            ┌──────────────────┐      │
            │ WF-02 Re-engage- │      │
            │ ment (Fase 1+2)  │      │
            └────────┬─────────┘      │
                     │ sin respuesta    │
                     ▼                  │
            ┌──────────────────┐      │
            │   En espera      ├──────┘
            │   (IA activa)    │
            └────────┬─────────┘
                     │ 6 meses sin actividad
                     ▼
            ┌──────────────────┐
            │ Ventas Perdidas  │
            │     Real         │
            └──────────────────┘

[Lateral, dispara desde cualquier stage activa:]
            ┌──────────────────┐
            │ Human Takeover   │
            │     (tag)        │
            └──────────────────┘
```

---

## §7. Diferencias con el pipeline actual de Kommo (cambios visibles)

| Aspecto | Kommo (hoy) | GHL (post-mig) |
|---|---|---|
| Cantidad de etapas | 31+ | 11 secuenciales + 4 terminales |
| Sub-pipeline R1-R5 | 17 etapas dedicadas | Eliminado → tags + custom fields |
| Etapas legacy (COTIZACION, R1-R5 sin/con info/ap) | Activas en el Kanban | Eliminadas |
| Etapa "Quiere comprar más adelante" | Existe pero sin lógica clara | Mantenida, definida como "expresión clara de intención futura" (post-MVP) |
| Distinción "sin info" / "con info" | Granular por etapa | Reducida a Custom Field `had_information: bool` |
| "Atención Personalizada" | Stage que mueve al lead fuera del flujo | Tag (`human_takeover`) — el lead conserva su stage, solo pausa IA |
| "Ventas perdidas" después de 24h sin responder | Movimiento automático directo | Movimiento a "En espera" (IA sigue activa) → 6 meses → "Ventas Perdidas Real" |
| "Confirmar pago" requiere validación humana | Sí (manual) | Sí (manual, sin cambio) |
| "Pago sin diseño" / "Diseño" / "En producción" como 3 etapas separadas | Sí | Sí (preservado, decisión Oscar §2.2 reunión) |
| Quién mueve el lead a "ETAPA 4" | Sub-workflow Seg. 7 pasos | WF-06 detectando `⏳(7 DIAS DE PROMO)⏳` en output del Vendedor |
| Reglas de bloqueo (status terminal) | IFs anidados en n8n | Filter al inicio de WF-01 |
