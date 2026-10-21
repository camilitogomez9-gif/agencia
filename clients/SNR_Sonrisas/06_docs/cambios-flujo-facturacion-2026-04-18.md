# Cambios flujo facturación — 2026-04-18

## Contexto

Extensión del reporte de facturación para registrar datos por **semana del mes** (además de por semana del año y mes). Esto implica que cada sucursal tiene un sheet `MES CORRIENTE` que se actualiza semanalmente con datos agrupados por semana del mes corriente.

---

## Cambios implementados

### 1. Nuevo campo `Semana_mes` en nodo Set "Filtro de campos"

Calcula la semana del mes directamente desde la fecha de pago, con la misma lógica que `Semana` pero usando `monthStart` como referencia en lugar de `jan1`.

- Semana 1: día 1 del mes → primer domingo del mes
- Semana 2+: lunes → domingo
- Un mes puede tener hasta 6 semanas

### 2. Pipeline paralelo para semana del mes

Se duplicó el pipeline de agregación por semana-año para crear uno nuevo por semana-mes:

| Nodo original (año) | Nodo nuevo (mes) |
|---|---|
| `Pagado Semana` (group: Categoria, Sucursal, Semana) | `Pagado Semana_mes` (group: Categoria, Sucursal, Semana_mes) |
| `Pagado y Cantidad Semana` (group: Clase, Semana, Sucursal) | `Pagado y Cantidad Semana_mes` (group: Clase, Semana_mes, Sucursal) |
| `Combinar categorías1` (pivot: Semana + Sucursal) | `Combinar cats Semana_mes` (pivot: Semana_mes + Sucursal) |
| `Combinar categorías4` (pivot: Semana + Sucursal) | `Combinar cats Semana_mes 2` (pivot: Semana_mes + Sucursal) |
| Merge `Semana` (join: Semana, Sucursal) | Merge `Semana_mes` (join: Semana_mes, Sucursal) |
| `Loop Over Items2` | `Loop Over Items3` |

Los dos pipelines son completamente independientes. El pipeline de semana-mes alimenta `Generar ID+Sheet Sucursal` → `Por sucursal1`.

### 3. Limpieza mensual de MES CORRIENTE

Sub-flujo independiente de 3 nodos:
- `Schedule Trigger` (día 1 de cada mes)
- `Code node`: genera 4 items con los docIds de las 4 sucursales
- `Google Sheets Clear`: limpia el sheet `MES CORRIENTE` en cada documento

Esto evita que queden filas de meses anteriores cuando el número de semanas del mes varía (ej. mes con 5 semanas seguido de uno con 4).

### 4. Corrección del nodo `lapso` (rango de fechas para descarga)

**Problema:** las semanas del año que cruzan el cambio de mes (semanas "puente") quedaban incompletas en el sheet de semana-año porque el rango empezaba el día 1 del mes, dejando los días lunes-X del mes anterior sin capturar.

**Solución:** `primerDia` ahora apunta al **lunes de la semana del año que contiene el día 1 del mes corriente**.

```javascript
const daysBack = (firstOfMonth.getDay() + 6) % 7;
const primerDiaDate = addDays(firstOfMonth, -daysBack);
```

Esto extiende el rango entre 0 y 6 días hacia atrás según el día de semana en que empiece el mes. Para meses que empiezan el lunes, no hay cambio.

### 5. Nuevo nodo `Filtro mes actual`

Como el rango ahora puede incluir días del mes anterior (para la semana puente), se agrega un filtro que descarta items con fecha anterior al día 1 del mes corriente. Este filtro se aplica **solo** a los paths de Mes y Semana_mes, para evitar que datos del mes anterior contaminen esos reportes.

Los paths de semana-año reciben los datos sin filtrar para que la semana puente quede completa.

---

## Rango de fechas establecido

| Campo | Valor |
|---|---|
| `primerDia` | Lunes de la semana del año que contiene el 1ro del mes corriente |
| `ultimoSabado` | Último sábado ≤ hoy (Montevideo) |

Cecilia descarga desde `primerDia` hasta `ultimoSabado` cada sábado. El flujo corre el domingo (día sin datos — clínica cerrada).

---

## Workflow actualizado

`03_workflows/sonrisas-reporte-facturacion-v3.json`
