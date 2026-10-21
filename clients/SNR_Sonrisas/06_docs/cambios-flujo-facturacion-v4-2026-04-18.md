# Cambios flujo facturación v3 → v4 — 2026-04-18

## Contexto

El workflow v3 (`03_workflows/sonrisas-reporte-facturacion-v3.json`) cumple su función pero acumuló complejidad:

- **3 pipelines paralelos casi idénticos** (Mes, Semana-Año, Semana-Mes) con ~30 nodos entre Summarize + Code pivot + Merge + Loop.
- **Lógica de fechas fragmentada** entre el nodo `lapso` (rango de descarga) y el nodo Set `Filtro de campos` (cálculo de semanas).
- **Bug documentado pero nunca implementado**: la doc del 2026-04-18 (v3) especifica un nodo `Filtro mes actual` para que los paths de Mes y Semana_mes descarten filas del mes anterior cuando el rango incluye la semana puente. Ese filtro nunca se agregó, con lo cual las filas de la semana puente contaminan los reportes mensuales.
- **3 `Loop Over Items` con batch=1 + Waits** (1.75s + 3.5s + 1.75s) ralentizan innecesariamente la ejecución.

v4 reescribe el flujo principal de forma radical: **9 nodos** en el flujo principal (vs. ~30 en v3), con toda la lógica de fechas centralizada en 2 Code nodes.

---

## Archivos

| Archivo | Estado |
|---|---|
| `03_workflows/sonrisas-reporte-facturacion-v3.json` | **Intacto** — se conserva como versionado histórico / backup. No se modifica. |
| `03_workflows/sonrisas-reporte-facturacion-v4.json` | **Nuevo** — workflow simplificado, en validación. Importable como workflow independiente en n8n. |

El corte de producción (reemplazar v3 por v4) lo decide el usuario después de validar v4 end-to-end.

---

## Nuevo rango de descarga

| Variable | Definición |
|---|---|
| `primerDia` | Lunes de la semana ISO que contiene el día 1 del mes corriente (Montevideo TZ). |
| `ultimoDia` | Último sábado ≤ hoy (Montevideo TZ). |

**Ejemplos:**

- Abril 2026 (1 de abril = miércoles): `primerDia = 2026-03-30` (lunes previo).
- Mayo 2026 (1 de mayo = viernes): `primerDia = 2026-04-27`.
- Cuando el día 1 cae lunes, el rango empieza ese mismo día.

**Diferencia respecto a v3:** mismo concepto que v3 (lunes ISO del día 1), pero ahora es la única definición de "inicio" — no hay variable `ultimoSabadoMesAnterior` ni "días perdidos".

**Instrucciones para Cecilia (actualizar el mail recordatorio):**

> Cargar pagos desde el **LUNES previo al día 1 del mes actual** hasta **HOY (sábado), inclusive**. Si el día 1 cae en lunes, el rango empieza ese mismo día.

El mail recordatorio (`Send a message`) ya muestra `primerDia` y `ultimoDia` calculados; el texto fijo también se actualizó para reflejar la nueva regla.

---

## Arquitectura v4

```
Trigger Reporte Semanal (domingos)
    │
    ▼
[1] lapso (Code)
    → primerDia, ultimoDia, diaUnoMes, mesCorriente, mesAnioCorriente
    │
    ▼
[2] Get row(s) in sheet
    Lee el sheet origen (Ingreso datos)
    │
    ▼
[3] Clasificar y filtrar (Code)
    - Descarta filas con fecha < primerDia
    - Descarta códigos no válidos
    - Normaliza Categoría y clase (AJUSTE / COMBO / RETIRO / OTRO)
    - Calcula mesKey, semanaAnio, semanaMes, esDelMesActual, docId
    │
    ▼
[4] Agregar 3 dimensiones (Code, 3 outputs, runOnceForAllItems)
    Mantiene 3 Maps en memoria:
      porMes        (solo esDelMesActual=true)
      porSemanaAnio (todo — incluye semana puente completa)
      porSemanaMes  (solo esDelMesActual=true)
    │
    ├──▶ Output 1 (Mes) ────┬──▶ [5a] Reporte general (GSheets global, sheet={{ Sucursal }})
    │                       └──▶ [5b] Por sucursal (GSheets, docId dinámico, sheet=año)
    │
    ├──▶ Output 2 (Semana) ─▶ [6] semana (GSheets global, sheet={{ Sucursal }})
    │
    └──▶ Output 3 (Semana_mes) ─▶ [7] Por sucursal1 (GSheets, docId dinámico, sheet="MES CORRIENTE")
```

**Sub-flujos preservados idénticos a v3:**

- **Trigger Correo** (lunes 9hs) → `lapso1` → `Send a message` (Gmail) → (on error) `Mensaje de error` (Telegram).
  Se duplica la lógica de `lapso` como nodo `lapso1` para mantener ramas independientes por trigger.
- **Trigger Borrar** (día 1, 13hs) → `Sheets IDs` → `Loop Over Items1` ↔ `Clear sheet` + `Wait4`.

---

## Mapeo v3 → v4

### Flujo principal

| v3 | v4 |
|---|---|
| `lapso` (Code, ~40 líneas con offsetToLastSaturday, firstSaturdayOfMonth, lastSaturdayPrevMonth, "días perdidos") | `lapso` (Code, ~8 líneas Luxon) |
| `Get row(s) in sheet` | idem |
| `Filtro` (IF, lista de códigos válidos) | Embebido dentro de `Clasificar y filtrar` como `CODIGOS_VALIDOS` Set |
| `Filtro de campos` (Set con JS para Semana / Semana_mes / Mes / Categoria normalizada) | Embebido dentro de `Clasificar y filtrar` |
| `Clase` (Set / Switch AJUSTE / COMBO / RETIRO) | Embebido dentro de `Clasificar y filtrar` como `CLASES` |
| `Pagado Mes`, `Pagado y Cantidad Mes`, `Combinar categorías`, `Combinar categorías2`, `Merge Mes`, `Loop Over Items` | `Agregar 3 dimensiones` (Output 1) |
| `Pagado Semana`, `Pagado y Cantidad Semana`, `Combinar categorías1`, `Combinar categorías4`, `Merge Semana`, `Loop Over Items2` | `Agregar 3 dimensiones` (Output 2) |
| `Pagado Semana_mes`, `Pagado y Cantidad Semana_mes`, `Combinar cats Semana_mes`, `Combinar cats Semana_mes 2`, `Merge Semana_mes`, `Loop Over Items3` | `Agregar 3 dimensiones` (Output 3) |
| `Generar ID Sucursal` / `Generar ID+Sheet Sucursal` | Embebido dentro de `Clasificar y filtrar` (campo `docId` resuelto en la fila) |
| `Reporte general` | idem |
| `Por sucursal` | idem |
| `semana` | idem |
| `Por sucursal1` (MES CORRIENTE) | idem |
| `Filtro mes actual` (**documentado pero nunca implementado**) | **Ahora sí implementado** dentro de `Agregar 3 dimensiones`: los Maps `porMes` y `porSemanaMes` solo aceptan filas con `esDelMesActual=true`. |

### Sub-flujos

| v3 | v4 |
|---|---|
| `Trigger Correo` + `lapso` compartido + `Send a message` + `Mensaje de error` | Mismo diseño. La lógica de `lapso` se duplica en `lapso1` para tener una rama independiente por trigger. |
| `Trigger Borrar` + `Sheets IDs` + `Loop Over Items1` + `Clear sheet` + `Wait4` | Idem, sin cambios. |

---

## Claves de diseño

1. **Dos Code centrales, todo el resto es I/O**
   - `lapso`: 1 item con `primerDia`, `ultimoDia`, `diaUnoMes`, `mesCorriente`, `mesAnioCorriente`. Luxon, ~8 líneas.
   - `Clasificar y filtrar`: normalización por fila. Lista de códigos, mapeo de categorías, mapeo de clases y mapeo sucursal→docId en un solo lugar.
   - `Agregar 3 dimensiones`: pivot en memoria, 3 outputs (Mes / Semana año / Semana mes).

2. **Un único concepto de "inicio del rango"**
   `primerDia = startOf('month').startOf('week')` en Luxon (lunes ISO del día 1). Reemplaza las 4 variables de v3 (`ultimoSabadoMesAnterior`, `primerSabadoMes`, "días perdidos", `primerLunesSemanaQueContieneDia1`).

3. **Fix del bug "semana puente contamina Mes"**
   v3 documentó el filtro pero no lo implementó. v4 lo hace al nivel de agregación: los Maps `porMes` y `porSemanaMes` solo acumulan items con `esDelMesActual=true`, mientras que `porSemanaAnio` recibe todo para que la semana puente quede completa en el sheet `SEMANA AÑO`.

4. **Convención de Semana del año preservada**
   v4 **no** adopta ISO week. Mantiene la convención actual del cliente: S1 = del 1/1 al primer domingo; luego lunes-domingo. Esto evita reenumerar sheets históricos.

5. **Semana del mes preservada**
   Semana 1 = del día 1 hasta el primer domingo del mes; siguientes lunes-domingo; última puede truncarse el último día del mes. Misma regla que v3.

6. **Sin Loops con batch=1 en el flujo principal**
   Las escrituras a Google Sheets usan `batchSize=25` por defecto (sin Wait) confiando en `retryOnFail: true`. Si Google Sheets empieza a rate-limitear, bajar `batchSize` a 10 o agregar un Wait de 1s antes de los 4 nodos de escritura.

---

## Verificación pre-producción

Antes de reemplazar v3 por v4 en n8n:

1. **Importar v4 como workflow nuevo** (no pisar v3).
2. **Ejecución manual en un domingo**
   - Verificar que `lapso` devuelve `primerDia`, `ultimoDia`, `mesCorriente` correctos (chequeo con calendario a mano).
   - Spot-check de 5 items después de `Clasificar y filtrar`: fecha, código, Categoria, Clase, Mes, Semana, Semana_mes, esDelMesActual.
   - Verificar que un item con fecha en la **semana puente** (ej. 30-abr cuando mesCorriente = mayo) tiene `esDelMesActual=false` y aparece en Output 2 (Semana año) pero NO en Output 1 (Mes) ni Output 3 (Semana_mes).
3. **Validación contra v3**
   - Correr v4 sobre los mismos datos de la última ejecución de v3.
   - Comparar totales por `(Mes, Sucursal, Categoria)` y `(Semana, Sucursal, Categoria)`.
   - Deben coincidir, excepto en la semana puente donde v4 corrige el bug (Mes y Semana_mes no deberían incluir fechas del mes anterior).
4. **Deploy gradual (opcional)**
   - Apuntar los 5 docIds destino a una copia de test por 1-2 ciclos.
   - Revertir a destinos reales tras 2 ejecuciones consecutivas correctas.
5. **Desactivar v3** en n8n solo después de validar al menos 1 ciclo semanal completo con v4.
6. **Actualizar mail recordatorio a Cecilia** con la nueva regla de rango si no la refleja.

---

## Notas operativas

- **Cuando se actualiza el Listado de Precios**, el script `scripts/utilities/update-sonrisas-nodes.py` todavía apunta a los nodos de v3 (`Filtro` y `Clase`). Para v4, el equivalente es actualizar las constantes `CODIGOS_VALIDOS` y `CLASES` dentro del Code `Clasificar y filtrar`. TODO: extender el script para emitir también el bloque para v4.
- **DocIds de sucursales**: v4 los consolida en un solo lugar (`DOC_ID_SUCURSAL` dentro de `Clasificar y filtrar`). El sub-flujo de limpieza mantiene su propio diccionario `Sheets IDs`; unificar ambos queda como TODO menor.
- **`lapso` duplicado**: la lógica vive en `lapso` (flujo principal) y `lapso1` (recordatorio). Si se cambia el cálculo de fechas, actualizar ambos nodos.
