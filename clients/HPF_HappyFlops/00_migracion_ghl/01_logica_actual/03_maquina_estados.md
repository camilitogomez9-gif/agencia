# Máquina de Estados del Lead — Pipeline IA Happy Flops

> **Etapa 1.** Reconstrucción de las transiciones entre etapas del pipeline `IA` (ID `11622596`) gestionado por el agente. Incluye triggers exactos extraídos de los workflows.

---

## 1. Pipeline activo y pipelines paralelos

### 1.1 Pipeline operado por el agente: `IA` (11622596)

Es el **único pipeline donde corre el sistema automatizado**. El nodo `No es IA` filtra explícitamente:
```
if status_id NOT contains 11622596 → No procesa
```

### 1.2 Pipelines paralelos (legacy / manuales)

Los 12 pipelines restantes en Kommo (`GENERAL`, `SANDALIAS BODAS`, `SANDALIAS XV AÑOS`, `Cilindros`, `Mandiles`, `Kit anticrudas`, `Pantuflas`, `Sandalia lisa`, `Happyfloops`, `XV AÑOS`, `BODAS`, `Reactivadores Genericos`) **no son tocados por el agente**. Son flujos manuales del equipo o legacy. La estrategia de migración debe considerar que **solo el pipeline `IA` se migra al agente GHL**; los demás se evalúan caso por caso (probable: archivar en GHL o conservar como "vista de leads históricos").

---

## 2. Etapas del pipeline `IA` (en orden de sort)

| # | ID | Nombre Kommo | Significado funcional | ¿La toca el agente? |
|---|----|-------------|----------------------|--------------------|
| 1 | 89263340 | Incoming leads | Lead recién creado, sin procesar | ✅ Lectura (filtro de entrada) |
| 2 | 89263344 | ETAPA 1 | Saludo enviado / lead inactivo en step_1 | ✅ Sub-workflow (perdidos si no avanza) |
| 3 | 93616832 | ETAPA 2 | Imagen principal del evento enviada | ✅ Movido por Seg. Imagen |
| 4 | 93616836 | ETAPA 3 | Productos del evento mostrados | ✅ Movido por Seg. Cotización + Seg. 7pasos |
| 5 | 93616840 | ETAPA 4 | Cotización completada / lead recolectando datos | ✅ Lectura (target del check de avance) |
| 6 | 91266100 | atencion personalizada | Derivado a humano | ✅ Movido por tool ATENCION_PERSONALIZADA + side-effects |
| 7 | 91450360 | confirmar pago | Comprobante recibido, aguardando confirmación interna | ✅ Movido por detección de pago |
| 8 | 89263352 | PAGO SIN DISEÑO | Pago confirmado, no se inició diseño | ❌ Manual (humano lo mueve) |
| 9 | 91246120 | DISEÑO | En proceso de diseño | ❌ Manual |
| 10 | 100395519 | en produccion | Pedido en producción | ✅ Lectura (filtro post-pago) |
| 11 | 100395523 | pago liquidacion | Pago de liquidación recibido | ✅ Movido por detección de pago en producción |
| 12 | 91408976 | quiere comprar mas adelante | Lead frío con intención futura | ❌ Manual |
| 13 | 89263348 | COTIZACION | (¿Etapa de seguimiento adicional?) | ❌ Aparentemente legacy / sin uso confirmado |
| 14-22 | múltiples | r1/r2/r3/r4/r5 sin/con info / ap | Sub-pipeline de seguimientos automatizados | ✅ Movido por sub-workflows |
| 23-24 | 91622916/20 | sin/con informacion especial | Variantes especiales de seguimiento | ✅ Inferido desde IFs |
| 25 | 142 | Logrado con éxito | Venta cerrada | ❌ Manual |
| 26 | 143 | Ventas Perdidos | Lead descartado | ✅ Movido por sub-workflows tras 24h sin respuesta |

---

## 3. Sub-pipeline de seguimientos (R1–R5)

Las etapas `r1`–`r5` con sufijos `sin informacion`, `con informacion`, `ap` representan un sub-pipeline de **re-engagement automático** después de las etapas principales:

| ID | Nombre | Cuándo se llega |
|----|--------|----------------|
| 89263760 | r1 sin informacion | Tras 24h sin respuesta en ETAPA 1/2 (seguimiento Rebeca/Imagen sin haber dado info de evento) |
| 91408768 | r1 con informacion | Tras 24h sin respuesta en ETAPA 3 (productos mostrados, no cotizó) |
| 92033296 | r1 ap | Tras 24h sin respuesta cuando estaba en atención personalizada |
| 89263764 | r2 sin informacion | Siguiente nivel de seguimiento |
| 91408772 | r2 con informacion | Siguiente nivel |
| 92033300 | r2 ap | Siguiente nivel |
| 91606644 | R3 SIN INFORMACION | Tercera ronda |
| 91606648 | R3 CON INFORMACION | Tercera ronda |
| 92033304 | r3 ap | Tercera ronda |
| 89263768 | r4 sin informacion | Cuarta ronda |
| 91408776 | r4 con informacion | Cuarta ronda |
| 92033308 | r4 ap | Cuarta ronda |
| 91622908 | r5 sin informacion | Quinta ronda (final?) |
| 91622912 | r5 con informacion | Quinta ronda (final?) |
| 92033312 | r5 ap | Quinta ronda (final?) |
| 91622916 | sin informacion especial | Variante (uso ambiguo) |
| 91622920 | con informacion especial | Variante (uso ambiguo) |

**Patrón:** los sub-workflows promueven el lead `Rn → Rn+1` después de ciertos timers/checks, y eventualmente lo mandan a `143 (Ventas Perdidos)`. La distinción `sin info` / `con info` tracking si el lead llegó a dar datos del pedido antes de quedarse en silencio.

> ⚠️ La lógica completa de R1→R2→...→R5 no está totalmente reconstruida en el código n8n explorado. Los nodos `R1 SIN INFO` y `R1 CON INFO` están explícitos en sub-workflows, pero las transiciones a R2..R5 requieren examinar más a fondo otros sub-workflows o lógica externa (Kommo Salesbot puede estar haciendo parte). **Ver `06_redundancias_y_ambiguedades.md` ítem #5.**

---

## 4. Diagrama del flujo principal (etapas IA)

```
                                    ┌─────────────────────┐
                                    │  Incoming leads     │
                                    │      (89263340)     │
                                    └──────────┬──────────┘
                                               │
                              [Webhook Kommo dispara n8n]
                                               │
                                               ▼
                                    ┌─────────────────────┐
                                    │      ETAPA 1        │
                                    │     (89263344)      │
                                    │   Saludo enviado    │
                                    └──────────┬──────────┘
                                               │
                          [Lead identifica evento → AI Agent Main Image]
                                               │
                                               ▼
                                    ┌─────────────────────┐
                                    │      ETAPA 2        │
                                    │     (93616832)      │
                                    │ Imagen ppal enviada │
                                    └──────────┬──────────┘
                                               │
                          [Lead pide productos → AI Agent Products]
                                               │
                                               ▼
                                    ┌─────────────────────┐
                                    │      ETAPA 3        │
                                    │     (93616836)      │
                                    │ Productos mostrados │
                                    └──────────┬──────────┘
                                               │
                          [Lead da datos / cotiza → AI Agent Recolector]
                                               │
                                               ▼
                                    ┌─────────────────────┐
                                    │      ETAPA 4        │
                                    │     (93616840)      │
                                    │ Cotización emitida  │
                                    └──────────┬──────────┘
                                               │
                                               │ [Lead manda comprobante 50%]
                                               ▼
                                    ┌─────────────────────┐
                                    │   confirmar pago    │
                                    │     (91450360)      │
                                    └──────────┬──────────┘
                                               │ [Equipo valida]
                                               ▼
                                    ┌─────────────────────┐
                                    │  PAGO SIN DISEÑO    │
                                    │     (89263352)      │
                                    └──────────┬──────────┘
                                               │ [Manual]
                                               ▼
                                    ┌─────────────────────┐
                                    │       DISEÑO        │
                                    │     (91246120)      │
                                    └──────────┬──────────┘
                                               │ [Aprobado]
                                               ▼
                                    ┌─────────────────────┐
                                    │    en produccion    │
                                    │     (100395519)     │
                                    └──────────┬──────────┘
                                               │ [Lead manda 50% liquidación]
                                               ▼
                                    ┌─────────────────────┐
                                    │  pago liquidacion   │
                                    │     (100395523)     │
                                    └──────────┬──────────┘
                                               │ [Manual]
                                               ▼
                                    ┌─────────────────────┐
                                    │ Logrado con éxito   │
                                    │       (142)         │
                                    └─────────────────────┘
```

---

## 5. Transiciones automatizadas (gestionadas por n8n)

### 5.1 Transiciones desde el main workflow

| Trigger en n8n | De → A | Nodo responsable |
|----------------|--------|------------------|
| AI Agent Starter envía saludo | `Incoming leads` → `ETAPA 1` (89263344) | Inferido — probablemente vía salesbot Kommo (`Saludo PTE 1` con bot_id) |
| AI Agent Main Image envía imagen | → `ETAPA 2` (93616832) | Sub-workflow Seg. Imagen, nodo `ETAPA 2` (PATCH Kommo) |
| AI Agent Products envía productos | → `ETAPA 3` (93616836) | Sub-workflow Seg. Cotización, nodo `ETAPA 3` (PATCH Kommo) |
| Recolector envía cotización con `7 DIAS DE PROMO` | → `ETAPA 4` (93616840) | Trigger `If4`/`If16` → `Execute Workflow3` (Seg. 7pasos) |
| Recolector usa tool ATENCION_PERSONALIZADA | → `atencion personalizada` (91266100) | Sub-workflow `ATENCION_PERSONALIZADA` |
| Imagen no clasificable | → `atencion personalizada` (91266100) | `ATENCION_PERSONALIZADA4` |
| PDF detectado | → `atencion personalizada` (91266100) | `ATENCION_PERSONALIZADA1` |
| Imagen detectada como pago + lead NO en producción | → `confirmar pago` (91450360) | `Confirmar Pago`, `Confirmar Pago1`, `Confirmar pago` (3 nodos redundantes) |
| Imagen detectada como pago + lead EN producción | → `pago liquidacion` (100395523) | `PAGO_LIQUIDACION` |

### 5.2 Transiciones desde sub-workflows de seguimiento

| Sub-workflow | Trigger | De → A |
|--------------|---------|--------|
| Seg. Rebeca | 24h sin respuesta + lead NO en AP | `ETAPA 1` → `Ventas Perdidos` (143) (`PERDIDOS1`) |
| Seg. Imagen | 24h sin respuesta + lead en `ETAPA 1` | → `Ventas Perdidos` (143) (`PERDIDOS1`) |
| Seg. Cotización | 24h + LLM detecta "No" | → `Ventas Perdidos` (143) (`PERDIDOS1`) |
| Seg. Cotización | 24h + lead respondió pero no avanzó | → `R1 SIN INFO` (89263760) |
| Seg. 7pasos | 24h + lead avanzó a ETAPA 4 | → `R1 CON INFO` (91408768) |
| Seg. 7pasos | Lead llegó a `100395519` (en producción) | → No hace nada (ya cerró) |
| Cualquier sub-workflow | Lead status == `91266100` (AP) | → No envía seguimiento (skip) |
| Cualquier sub-workflow | Lead status == `143` (perdidos) | → No envía seguimiento (skip) |

### 5.3 Reglas de bloqueo (status terminal para el agente)

Si el lead está en estos status, **el agente principal no responde**:

| Status | Razón | Componente que bloquea |
|--------|-------|----------------------|
| 91266100 (atencion personalizada) | Humano tomó el caso | `If9` / `If7` / `If12` (chequean este ID) |
| 91450360 (confirmar pago) | Aguardando validación humana | `If7` / `If12` |
| 92033296/300/304/308/312 (Rn ap) | Variantes de AP | `If20` |
| 143 (Ventas Perdidos) | Lead descartado | `Si está en perdidos` (`status_id == 143`) |
| Pipelines distintos a IA | Lead manual | `No es IA` (`!= 11622596`) |

---

## 6. Estados implícitos (no representados en Kommo)

El agente trackea estados internos que **no se reflejan en el pipeline**:

| Estado | Dónde se almacena | Para qué |
|--------|-------------------|----------|
| `step actual` (1/2/3/4) | Postgres Chat Memory (inferido por el Router) | Decidir qué agente despachar |
| `evento detectado` (Boda/XV/Otros) | Memoria conversacional | Filtrar Airtable, evitar repetir step_1 |
| `productos ya mostrados` | Memoria conversacional | No repetir envío de fichas |
| `cotización emitida` | Memoria conversacional + `If4`/`If6` (regex sobre output) | Detectar si ya se envió "7 DIAS DE PROMO" / "HAZ TU PEDIDO" |
| `7 pasos enviados` | Memoria + match regex | Evitar repetir mensaje de 7 pasos |
| `código postal capturado` | Memoria | No repreguntar |
| `cantidades por producto` | Memoria | Recalcular cotización si modifica |
| `tipo de sandalia` (delgada/gruesa) | Memoria | Necesario antes de cotizar |
| `mensaje anti-spam` | Redis (key=contact_id, push de mensajes) | Debouncing 50s |

**Implicación para migración:** todo este estado tiene que vivir en GHL Conversations (memoria) + Custom Values (campos del contacto/opportunity para los datos estructurados como CP, cantidades, evento).

---

## 7. Visualización de transiciones cron-style

```
T+0       Lead escribe → ETAPA 1 (saludo)
T+1h      [si no respondió] Recordatorio Rebeca PTE 1
T+1h+3h   [si no respondió] Recordatorio Rebeca PTE 2
T+~8h     [si no respondió] Recordatorio Rebeca PTE 3 (variable Wait2)
T+24h     [si no respondió] → Ventas Perdidos

T+0       Lead identifica evento → ETAPA 2 (imagen ppal enviada)
T+1h      [si no respondió] Seguimiento imagen PTE 1
T+1h+3h   [si no respondió] Seguimiento imagen PTE 2
T+~8h     [si no respondió] Seguimiento imagen PTE 3
T+24h     [si no respondió] → Ventas Perdidos

T+0       Lead pide productos → ETAPA 3 (productos mostrados)
T+1h      [si no respondió] Seguimiento cotización PTE 1
T+1h+3h   [si no respondió] Seguimiento cotización PTE 2
T+~8h     [si no respondió] Seguimiento cotización PTE 3
T+24h     [si no respondió → LLM evalúa]
            ├── "No" → Ventas Perdidos
            └── otro → R1 SIN INFO

T+0       Recolector envía 7 pasos → ETAPA 3 (también)
T+24h     [si no respondió y lead en ETAPA 4]
            └── → R1 CON INFO
          [si lead en 100395519] → No hace nada
```

---

## 8. Tabla maestra de transiciones (formato máquina)

```
TRANSITION_TABLE:
  - from: 89263340 (Incoming)
    to:   89263344 (ETAPA 1)
    trigger: webhook + AI Agent Starter (asumido por salesbot)
  - from: 89263344 (ETAPA 1)
    to:   93616832 (ETAPA 2)
    trigger: AI Agent Main Image envía imagen + sub-workflow Seg.Imagen PATCH
  - from: 93616832 (ETAPA 2)
    to:   93616836 (ETAPA 3)
    trigger: AI Agent Products + sub-workflow Seg.Cotización PATCH
  - from: 93616836 (ETAPA 3)
    to:   93616840 (ETAPA 4)
    trigger: AI Agent Recolector emite output con "7 DIAS DE PROMO"
  - from: 93616840 (ETAPA 4)
    to:   91450360 (confirmar pago)
    trigger: lead envía imagen detectada como comprobante (Es Pago == true) y lead NO en producción
  - from: cualquiera (no en producción)
    to:   91266100 (atencion personalizada)
    trigger: tool ATENCION_PERSONALIZADA (en Recolector) || imagen unclassifiable || PDF
  - from: 100395519 (en produccion)
    to:   100395523 (pago liquidacion)
    trigger: imagen detectada como comprobante + lead en producción
  - from: 89263344/93616832 (ETAPA 1/2)
    to:   143 (Ventas Perdidos)
    trigger: 24h+ sin respuesta tras último mensaje del agente
  - from: 93616836 (ETAPA 3)
    to:   89263760 (R1 SIN INFO)
    trigger: 24h sin respuesta + LLM evaluador != "No"
  - from: 93616836 (ETAPA 3)
    to:   143 (Ventas Perdidos)
    trigger: 24h sin respuesta + LLM evaluador == "No"
  - from: 93616840 (ETAPA 4)
    to:   91408768 (R1 CON INFO)
    trigger: 24h sin respuesta tras "HAZ TU PEDIDO EN 7 SENCILLOS PASOS"
```

---

## 9. Implicaciones para la migración a GHL

1. **Pipeline IA → GHL Pipeline + Opportunity Stages.** Las 31+ etapas se pueden simplificar significativamente.
2. **Sub-pipeline R1-R5 → reemplazar con tags + workflows GHL.** GHL maneja seguimientos con triggers automáticos basados en última actividad. No necesitamos 15 etapas para eso.
3. **Etapas terminales (142/143) → mantener** como estados finales del lead.
4. **AP (atención personalizada) → tag `human_takeover`** que pause los workflows automáticos.
5. **Estados implícitos → Custom Values + GHL Conversation Context.** Evento, productos mostrados, CP, cantidades.
6. **Filtros de bloqueo (No es IA, status terminal) → reemplazar con condiciones nativas de GHL Workflow.**
