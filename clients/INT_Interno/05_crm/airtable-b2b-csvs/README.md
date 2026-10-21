# Airtable B2B la agencia — CSVs de Import

**Fecha:** 2026-06-18
**Diseño base:** [planes/airtable-b2b-la agencia-estructura-2026-06-18.md](../../../../planes/airtable-b2b-la agencia-estructura-2026-06-18.md)

CSVs listos para importar a Airtable y bootstrappear la base operativa de la rama B2B de la agencia.

---

## Tablas (7) — Orden de import

El orden importa por dependencias de linked records. Importar en este orden:

| # | Archivo | Tabla | Filas seed | Dependencias |
|---|---------|-------|------------|--------------|
| 1 | `01-clientes.csv` | Clientes | 14 | → Closers (Closer asignado) |
| 2 | `02-closers.csv` | Closers | 2 | — |
| 3 | `03-developers.csv` | Developers | 2 | — |
| 4 | `04-project_managers.csv` | Project Managers | 2 | — |
| 5 | `05-proyectos.csv` | Proyectos | 35 | → Clientes, Closers, Developers, PMs, Proyectos (self) |
| 6 | `06-pagos.csv` | Pagos | 42 | → Clientes, Proyectos |
| 7 | `07-llamadas.csv` | Llamadas | 20 | → Clientes, Proyectos, Closers, Developers, PMs |

> **Orden alternativo más seguro:** 02 → 03 → 04 → 01 → 05 → 06 → 07.
> Closers/Devs/PMs primero porque Clientes los referencia en "Closer asignado".

> **Proyectos:** ya están ordenados internamente (todos los Diagnósticos primero, después Desarrollos que los referencian, después Upsells que referencian Desarrollos). Si Airtable se queja con los self-references, hacer el import en 2 pasadas: primero sin la columna "Proyecto padre", después con ella.

---

## Tabla unificada Proyecto — la decisión clave

**Diagnóstico, Desarrollo y Upsell viven en UNA sola tabla** (`Proyectos`), discriminados por el campo `Tipo` (single select). Esto resuelve el pedido del usuario de simplificar manteniendo la particularidad de cada tipo.

### Campos comunes (todos los tipos)

`ID`, `Nombre`, `Tipo`, `Cliente`, `Estado`, `Fecha inicio`, `Fecha deadline`, `Fecha cierre real`, `Ticket total`, `Moneda`, `Stack`, `Closer`, `PM`, `Developers`, `Descripcion`

### Campos especificos por tipo (quedan vacíos cuando no aplican)

| Campo | Diagnóstico | Desarrollo | Upsell |
|-------|:-----------:|:----------:|:------:|
| `Proyecto padre` | — | Diagnóstico origen | Desarrollo origen |
| `Outcome` | Avanzó / Descartado / Cobrado-no continuó | Entregado / En build | En curso / Entregado |
| `Deliverables` | — | ✓ | ✓ |
| `Hitos` | — | ✓ | — |
| `Tipo upsell` | — | — | Nueva feature / Mantenimiento / Expansión scope |

### Self-reference (Proyecto padre)

- Un **Desarrollo** puede tener un Diagnóstico padre → trazabilidad del pipeline diag→dev
- Un **Upsell** puede tener un Desarrollo padre → trazabilidad de extensiones de scope
- Un **Diagnóstico** nunca tiene padre

En Airtable se modela con un campo Linked Record que apunta a la misma tabla `Proyectos`.

---

## Configuración Airtable post-import

Lo siguiente NO viene en los CSVs — hay que configurarlo manualmente después de importar.

### Single selects (Airtable los detecta automáticamente, revisar opciones)

| Tabla | Campo | Opciones |
|-------|-------|----------|
| Clientes | Origen | Referido / Outbound / Inbound / RRSS / Evento |
| Clientes | Estado ciclo | Lead / Diagnóstico / Desarrollo / Producción / Mantenimiento / Pausado / Churn |
| Proyectos | Tipo | Diagnóstico / Desarrollo / Upsell |
| Proyectos | Estado | En curso / Pausado / Cerrado-Avanzó / Cerrado-OK / Cerrado-Descartado / Producción / Desarrollo / Mantenimiento / Propuesta |
| Proyectos | Moneda | USD / ARS / UYU / MXN / BOB / CLP |
| Proyectos | Outcome | Avanzó a desarrollo / Descartado / Cobrado-no continuó / Entregado / En build / En curso / Propuesta enviada / Pausado pendientes prod |
| Proyectos | Tipo upsell | Nueva feature / Mantenimiento / Expansión scope |
| Pagos | Tipo | Adelanto / Hito / Final / Único / Mantenimiento |
| Pagos | Moneda | USD / ARS / UYU / MXN / BOB / CLP |
| Pagos | Método | Transferencia USD / Transferencia ARS / Transferencia UYU / Transferencia MXN / USDT / Stripe / PayPal / Mercado Pago |
| Pagos | Estado | Pendiente / Cobrado / Vencido / Anulado |
| Llamadas | Tipo | Venta / Diagnóstico / Desarrollo / Seguimiento / Soporte |
| Llamadas | Área | Comercial / Técnica / Alineación / Demo / Onboarding |

### Multi-select

| Tabla | Campo | Opciones sugeridas |
|-------|-------|---------------------|
| Proyectos | Stack | n8n / Airtable / OpenAI gpt-4o / OpenAI gpt-4.1 / OpenAI gpt-4.1-mini / Whisper / Supabase / ManyChat / Chatwoot / Kommo / WhatsApp / Instagram / Facebook / Telegram / Gmail / Google Sheets / Google Calendar / Google Docs / Data Tables / Zoom / Postgres / Redis / Python / Meta CAPI / Clientify / GHL / cal.com / Chatrace / Fresha / Notion |
| Developers | Skills | n8n / prompt eng / Airtable / Python / Supabase / integraciones / ManyChat / backend / frontend / RAG / Postgres |

### Rollups y Formulas (configurar en Airtable, NO van en CSV)

**Tabla Clientes:**
- `LTV total` = Rollup sobre Pagos → SUM(Monto) WHERE Estado = "Cobrado"
- `# Proyectos` = Count de Proyectos linkeados
- `Cobrado pendiente` = Rollup sobre Pagos → SUM(Monto) WHERE Estado = "Pendiente"

**Tabla Proyectos:**
- `Cobrado real` = Rollup sobre Pagos → SUM(Monto) WHERE Estado = "Cobrado"
- `% Cobrado` = Formula → `Cobrado real / Ticket total`
- `# Llamadas` = Count de Llamadas linkeadas
- `Horas invertidas` = Rollup sobre Llamadas → SUM(Duracion min) / 60

**Tabla Closers:**
- `Tickets totales` = Rollup sobre Proyectos → SUM(Ticket total)
- `Cobrado estimado` = Formula → `Tickets totales * Comisión % / 100`
- `Cobrado real` = Rollup sobre Pagos (via Proyectos asociados) WHERE Estado = "Cobrado", luego `* Comisión %`. Para esto conviene crear un campo lookup en Pagos que traiga el Closer del Proyecto, y rollup desde el Closer.

**Tabla Developers:**
- Igual que Closers (con su comisión)
- `Proyectos activos` = Count de Proyectos WHERE Estado IN ["En curso", "Desarrollo", "En build"]

**Tabla Acquisitors:** (eliminado del modelo)

**Tabla PMs:**
- `# Proyectos activos` = Count de Proyectos asignados WHERE Estado activo
- `Cobrado estimado` = igual patrón

> **Tip para comisiones:** la fórmula simple `Tickets totales × Comisión %` paga sobre prometido. Si querés pagar solo sobre cobrado real, hay que hacer rollup desde la persona → proyectos asignados → pagos cobrados → SUM, y después multiplicar por comisión. Más fiel, evita pagar comisiones por proyectos que el cliente no terminó de pagar.

---

## Vistas sugeridas

### Clientes
- **Pipeline** — group by Estado ciclo
- **LTV ranking** — sort by LTV total DESC
- **Origen** — group by Origen
- **Cobrar pendiente** — filter Cobrado pendiente > 0

### Proyectos
- **Por tipo** — group by Tipo (Diagnóstico / Desarrollo / Upsell)
- **Activos** — filter Estado != "Cerrado-*" / "Producción" / "Mantenimiento"
- **Riesgo deadline** — filter Deadline < TODAY + 30d AND % Cobrado < 50
- **En producción** — filter Estado = "Producción"
- **Pipeline diag→dev** — filter Tipo = "Diagnóstico", group by Outcome
- **Upsells abiertos** — filter Tipo = "Upsell" AND Estado != "Entregado"

### Pagos
- **Cobrar este mes** — filter Estado = "Pendiente" AND Fecha emisión < TODAY
- **Cobrado este mes** — filter Estado = "Cobrado" AND Fecha cobro IS THIS MONTH
- **Por proyecto** — group by Proyecto
- **Vencidos** — filter Estado = "Vencido"

### Llamadas
- **Última semana** — sort by Fecha DESC, filter Fecha > TODAY - 7d
- **Por tipo** — group by Tipo
- **Sin Fathom** — filter Fathom URL IS EMPTY (recordatorio de cargar grabaciones)

---

## Interfaces sugeridas

1. **Dashboard ejecutivo** — KPIs: LTV total Σ, Cobrado este mes, Pipeline valor, # proyectos activos, distribución por tipo
2. **CRM Comercial** — vista Clientes pipeline + drill-down a proyectos
3. **PM Board** — proyectos activos del PM logueado + sus llamadas próximas
4. **Cobranzas** — pagos pendientes/vencidos + acción rápida marcar cobrado
5. **Comisiones** — vista por persona con tickets totales, cobrado estimado vs real, gap

---

## Notas sobre el seed data

- **14 clientes reales** del workspace (CLAUDE.md) con sus códigos: IMP, SNR, SYS, VTR, CLZ, NPR, HPF, NVJ, TFO, DLK, HBV, STK, CRZ.
- **35 proyectos**: 14 diagnósticos + 14 desarrollos + 7 upsells.
- **42 pagos** con estados realistas (cobrados, pendientes, vencidos donde corresponde).
- **20 llamadas** ejemplo distribuidas en los proyectos más activos. Los Fathom URLs están vacíos — completar a medida.
- **Equipo:** la agencia + JP (cada uno cumple varios roles: closer, dev, PM). Si crece el equipo, agregar filas en 02/03/04.
- **Emails y teléfonos:** quedaron en blanco salvo donde están confirmados en CLAUDE.md. Completar con datos reales en Airtable.
- **Comisiones default:** Closer 30%, Developer 40%, PM 10%. Ajustar al contrato real.

---

## Cómo importar a Airtable

### Opción A — UI Airtable

1. Crear base nueva: "la agencia B2B Ops"
2. Por cada CSV (en orden 02→03→04→01→05→06→07):
   - Add or import → CSV file
   - Subir el archivo
   - Confirmar el mapeo de columnas (Airtable detecta tipos)
   - Para campos linked, después de importar las tablas referenciadas, editar el campo y convertirlo a "Link to another record" apuntando a la tabla correcta
3. Validar relaciones cliqueando un proyecto → ver cliente linkeado correctamente

### Opción B — Airtable API + script

Si querés automatizar (recomendado para re-imports limpios):

```bash
# Ya tenés un patrón validado en el workspace:
# Replicar lógica idempotente (upsert por ID) con esta estructura
```

---

## Próximos pasos

1. **Crear base en Airtable** "la agencia B2B Ops"
2. **Importar CSVs** en orden (UI o script)
3. **Configurar single/multi selects, rollups, fórmulas** según las tablas arriba
4. **Crear vistas** sugeridas
5. **Diseñar interfaces** (1-2 al inicio: dashboard + CRM)
6. **Validar** con casos de uso reales:
   - ¿Cuánto le tengo que pagar a la agencia este mes en comisión?
   - ¿Qué proyectos están en riesgo de deadline?
   - ¿Cuál es el LTV promedio por origen de cliente?
7. **Iterar** — agregar campos faltantes a medida que aparecen necesidades
