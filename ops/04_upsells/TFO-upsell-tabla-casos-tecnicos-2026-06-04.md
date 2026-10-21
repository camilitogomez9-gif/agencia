# Upsell TFO — Tabla Airtable "Casos Técnicos" + tool dedicada

**Cliente:** TFO — TOFO Pizza (Mauricio García de la Vega)
**Fecha registrada:** 2026-06-04
**Status:** Diferido — proponer al cliente cuando pida métricas operativas o reporte mensual de fallas
**Disparador esperado:** cliente pregunta "¿cuántas fallas tuvimos este mes?", "¿qué máquina falla más?", o pide reporte de operaciones técnicas.

---

## Contexto

El sistema multi-agente actual de TFO tiene 4 subagentes:
- **B2B** y **RRSS** registran leads comerciales en Airtable (base `appNSuKCNtwn0Na6P`, tabla Leads, vía tool `registrar`).
- **Servicio al Cliente** y **Reposición** atienden fallas técnicas pero **NO registran nada en Airtable** — solo dejan rastro en escalamientos a Telegram (Miguel) y en ManyChat Live Chat.

En el ciclo de fix de la tool `registrar` (2026-06-04), se decidió excluir formalmente a Servicio del CRM principal para mantener la base limpia de leads comerciales. Decisión validada: separación entre CRM comercial vs operativo en MVP.

**Costo de esta decisión:** TOFO pierde visibilidad cuantitativa de:
- Cuántas fallas técnicas se atienden por mes
- Qué máquinas fallan más
- Qué tipo de fallas son recurrentes (no salió, doble cobro, congelada, etc.)
- Tiempo de resolución promedio
- Si las reposiciones se entregaron exitosamente
- Patrón de quejas por sabor/máquina

Esta info hoy queda dispersa entre logs de Telegram (Miguel) y conversaciones cerradas en ManyChat. **No es accionable para mejorar operación.**

---

## Propuesta

Crear una segunda tabla en Airtable dedicada a operación técnica + tool n8n específica para que el Agente de Servicio + Agente de Reposición puedan registrar.

### Componentes

**1. Tabla Airtable nueva: `Casos Técnicos`** (en la misma base `Panel de Control de Leads TOFO`)

Schema sugerido (~12 campos):

| Campo | Tipo | Descripción |
|-------|------|-------------|
| ID Manychat | string | Matching col para upsert |
| Fecha del caso | datetime | Auto-fillado `$now` |
| Máquina afectada | single-select | Flex Norte / Flex Sur / UAG / Plaza Patria / Estación Juárez |
| Tipo de falla | single-select | "No salió la pizza" / "Doble cobro" / "Pantalla congelada" / "Pizza fría" / "Sabor equivocado" / "Otro" |
| Descripción del caso | long text | Resumen del LLM |
| Sabor pedido | single-select | Pepperoni / Hawaiana / 4 Quesos / Nutella / Pastor |
| Monto pagado | currency | MXN |
| Evidencia (fotos) | attachments | Fotos de pantalla + ticket |
| Estado del caso | single-select | "Reportado" / "En análisis" / "Código de reposición entregado" / "Resuelto" / "Escalado a Miguel" / "Sin evidencia válida" |
| Código de reposición | string | Si aplica, el código entregado |
| Asignado a | single-select | Bot / Miguel / Mauricio |
| Tiempo de resolución | duration | Auto-calculado |

**2. Tool n8n nueva: `registrar_caso`** (separada de `registrar`)

- Tipo: `airtableTool`
- Operación: `upsert` (matching: `ID Manychat`)
- Cableada a: Agente de Servicio + Agente de Reposición
- Trigger en prompts: "Apenas se identifique una falla / al cerrar el caso / al entregar código de reposición"
- `toolDescription` rica describiendo cuándo invocar

**3. Vistas Airtable**

- "Casos abiertos hoy"
- "Casos por máquina (últimos 30 días)"
- "Códigos de reposición entregados / canjeados"
- "Casos sin evidencia válida (fraude potencial)"

**4. Reporte semanal automático** (opcional, +1 upsell)

Workflow n8n que el viernes a las 9am envía a Mauricio por email:
- # casos totales de la semana
- Tipo de falla más frecuente
- Máquina con más fallas
- Tiempo promedio de resolución
- % de casos con código entregado

---

## Esfuerzo estimado

| Componente | Horas | Notas |
|-----------|-------|-------|
| Diseño tabla Airtable + schema + vistas | 1h | Definir con cliente single-select values |
| Crear nueva tool n8n `registrar_caso` (sub-workflow o nodo Airtable directo) | 1h | Patrón similar a `registrar` |
| Cablear tool al Agente de Servicio + Agente de Reposición | 0.5h | Editar workflow main |
| Bump prompts v1.5: agregar sección "REGISTRO OBLIGATORIO" en Servicio y Reposición | 1.5h | Definir trigger en cascada y valores |
| Sync Google Docs (cliente) | 0.5h | Copy-paste prompts |
| Testing E2E con 5 escenarios reales | 1h | Sandbox + verificación Airtable |
| **Subtotal Casos Técnicos** | **5.5h** | |
| Reporte semanal automático (opcional) | 3h | Workflow n8n + plantilla HTML email |
| **Total con reporte** | **8.5h** | |

---

## Precio sugerido

**Opción A — Casos Técnicos solo**
- One-time: USD 350 (5.5h × USD 65/h promedio)
- Sin retainer adicional si ya está en mantenimiento.

**Opción B — Casos Técnicos + Reporte Semanal**
- One-time: USD 550 (8.5h × USD 65/h promedio)
- Reporte semanal corre solo, sin costos recurrentes adicionales.

**Opción C — Bundle con CRM Comercial existente**
- Si se renegocia el retainer mensual: incluir Casos Técnicos como mejora del paquete → no charge one-time, +USD 50/mes al retainer.

Recomendado: **Opción B** — el reporte semanal es donde el cliente realmente "ve" el ROI del registro técnico. Sin reporte, los datos quedan en Airtable y nadie los mira.

---

## Cómo presentarlo al cliente

Mensaje sugerido (cuando dispare):

> Hola Mauricio, viendo que estás preguntando por métricas operativas — actualmente el sistema atiende las fallas pero no las captura para análisis. Te propongo agregar una capa de tracking técnico:
>
> ✓ Cada falla queda registrada en Airtable: máquina, tipo, evidencia, estado de resolución
> ✓ Podés ver en vivo qué máquinas fallan más, qué tipos de error son recurrentes, tiempos de resolución
> ✓ Reporte semanal automático por email los viernes
>
> Costo: USD 550 one-time, sin recurrente. Te paso una demo con datos de la última semana cuando quieras.

---

## Riesgos / consideraciones

1. **Volumen esperado**: cuántas fallas mensuales hay hoy? Si son <10/mes, el upsell tiene poco valor inmediato (puede ser premature). Si son 50+/mes, hay caso fuerte.
2. **Sensibilidad de fraude**: los códigos de reposición + evidencia fotográfica pueden ser objeto de análisis de fraude. Verificar que el cliente lo quiera analizar (puede preferir no saber).
3. **Sincronización con CRM principal**: si un caso técnico viene de un lead que también está en la tabla Leads, hay que decidir si linkear ambas tablas (lookups) o mantenerlas independientes.
4. **Calidad de data**: depende de la consistencia del LLM al clasificar `Tipo de falla` y `Máquina afectada`. Probablemente requiera el mismo trabajo de placeholder/enum que se hizo para `Estado` en el ciclo actual.

---

## Estado del upsell

- [ ] Cliente preguntó por métricas técnicas — NO TODAVÍA
- [ ] Propuesta enviada al cliente
- [ ] Aprobación recibida
- [ ] En implementación
- [ ] Entregado
