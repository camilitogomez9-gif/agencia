# Guía de implementación — Manejo de fechas (Facturación Sonrisas)

**Fecha:** 2026-05-24
**Workflows afectados:** `SNR | Recordatorio Ingreso Datos` (`4s8qT7TmXXsgoPuc`), `SNR | Correos Reportes Facturación` (`AfOlO59HbeD3u1nq`), `SNR | Reporte Facturación v3.2` (`XCO4kWeKbsvPnnzz`)
**Verificación previa:** `scripts/utilities/verify-sonrisas-fechas.py` → 0 días perdidos en 2026, sin colisión, 1 cierre por mes (la lógica vieja perdía 22 día-mes/año).

---

## 1. Qué cambia y por qué

**Problema:** en bordes de mes se perdían días. La clínica **no abre los domingos** (no hay datos), así que a nivel semanal no se perdía nada; la pérdida era en el borde de mes:
- El correo **mensual** salía el último día del mes, **antes** de que el primer sábado del mes siguiente cargara la cola del mes → esos días no entraban en ningún mes.
- `Trigger Borrar` limpiaba `MES CORRIENTE` el día 1 → la última semana relativa del mes saliente nunca se mostraba.
- El correo a Cecilia (`lapso`) pedía solo `Lun→Sáb` de la semana actual (6 días) reemplazando todo, y su nota describía una lógica de borde **no implementada**.

**Solución — "Mes objetivo":** el mes que el sistema está cerrando. Durante la 1ª semana de un mes nuevo el objetivo sigue siendo el mes anterior (hasta que se carga su cola). El mensual cierra "al cerrar la semana borde" (primer domingo del mes siguiente). Cecilia carga, cada sábado, **`[1° del mes objetivo .. hoy]` reemplazando todo**.

**Semanas se mantienen Lunes→Domingo** (decisión del cliente). Como el domingo no tiene datos, la semana queda completa el sábado.

---

## 2. Helper canónico (base de todos los cálculos)

Esta lógica se usa (en versión Code o expresión) en varios nodos. **Calcula el "mes objetivo" y si este sábado cierra ese mes.**

```js
const tz = 'America/Montevideo';
const now = DateTime.now().setZone(tz).startOf('day');
const jsDow = now.toJSDate().getDay();                 // 0=Dom..6=Sáb
const sat  = now.minus({ days: (jsDow + 1) % 7 });      // sábado más reciente (hoy si corre sábado)

// primer sábado en o después de una fecha (Luxon weekday: Lun=1..Dom=7, Sáb=6)
const firstSatGe = (d) => d.plus({ days: (6 - d.weekday + 7) % 7 });

const curr    = sat.startOf('month');
const prevEnd = curr.minus({ days: 1 });
const prev    = prevEnd.startOf('month');
const mesObjetivo = sat.hasSame(firstSatGe(prevEnd), 'day') ? prev : curr;   // lagea en el borde
const esFinalize  = sat.hasSame(firstSatGe(mesObjetivo.endOf('month').startOf('day')), 'day');

const M = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
const mesObjetivoNombre = M[mesObjetivo.month - 1];
```

> ⚠️ No usar el atajo `día ≤ 7`: falla en meses que empiezan domingo (re-cierra el mes anterior dos veces, p. ej. Feb-2026). La versión de arriba (con `firstSatGe`) es la correcta y verificada.

---

## 3. Workflow `SNR | Recordatorio Ingreso Datos` (correo a Cecilia)

> Trigger `Trigger Correo1` ya está OK: **Sábado 13:00**. No tocar.

### 3.1 Nodo `lapso` — reemplazar TODO el código por:

**Update 2026-06-07 — solo última semana.** Con la migración del histórico a Data Table n8n
(`SNR | Histórico Pagos`), el `Upsert Histórico tabla` es idempotente vía `_key = # Pago +
- + # Detalle Presupuesto`. Cecilia ya no necesita recargar todo el mes objetivo cada
sábado: con la última semana basta. El histórico acumulado en la Data Table cubre el resto.
`mesObjetivoNombre` / `mesObjetivoAnio` / `esFinalize` se conservan porque los Correos y el
Reporte los siguen usando para titular el período de cierre.

```js
const tz = 'America/Montevideo';
const now = DateTime.now().setZone(tz).startOf('day');
const jsDow = now.toJSDate().getDay();
const sat = now.minus({ days: (jsDow + 1) % 7 });
const primerDia = sat.minus({ days: 6 });   // domingo de la semana (7 días)
const firstSatGe = (d) => d.plus({ days: (6 - d.weekday + 7) % 7 });
const curr = sat.startOf('month');
const prevEnd = curr.minus({ days: 1 });
const prev = prevEnd.startOf('month');
const mesObjetivo = sat.hasSame(firstSatGe(prevEnd), 'day') ? prev : curr;
const esFinalize = sat.hasSame(firstSatGe(mesObjetivo.endOf('month').startOf('day')), 'day');
const M = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];

return [{
  json: {
    primerDia: primerDia.toISODate(),     // domingo de la última semana
    ultimoDia: sat.toISODate(),           // este sábado
    mesObjetivoNombre: M[mesObjetivo.month - 1],
    mesObjetivoAnio: mesObjetivo.year,
    esFinalize,
  },
}];
```

El HTML de `Send a message1` ya interpola `{{ $json.primerDia }}` y `{{ $json.ultimoDia }}` → **no cambia**.

> **Borde mes (Finalize):** si el sábado actual es el primero del mes nuevo, el rango
> cubre los últimos días del mes anterior + los primeros del nuevo (7 días corridos). El
> flujo categoriza cada fila por `Mes_de_recepcion_del_pago`, así que ambos meses quedan
> bien asignados aunque la carga sea una sola.
>
> **Si Cecilia se salta un sábado:** pierde esa semana hasta que la cargue manualmente. Si
> se quiere más margen de seguridad, cambiar `sat.minus({ days: 6 })` por
> `sat.minus({ days: 13 })` (últimos 14 días). La idempotencia del Upsert garantiza que la
> redundancia no duplica.

### 3.2 Nodo `Send a message1` — corregir el texto de la NOTA

Buscar en el HTML la frase actual:

> *"El rango arranca el lunes previo al día 1 del mes corriente para capturar la semana que cruza el cambio de mes."*

Reemplazarla por:

> *"Descargá de Dentalink el rango indicado y pegá **reemplazando todo** el contenido de la planilla. El primer sábado de cada mes el rango arranca el mes anterior, para cerrar el mes completo. (Los domingos no se incluyen: la clínica no abre.)"*

---

## 4. Workflow `SNR | Correos Reportes Facturación`

### 4.1 `Trigger Reporte Mensual` — pasar de "último día del mes" a domingos

- Cambiar la regla a: **`weeks`**, `triggerAtDay: [0]` (domingo), `triggerAtHour: 8`.

### 4.2 Agregar IF `¿Cierra el mes?` justo después del trigger mensual

Insertar un nodo **IF** entre `Trigger Reporte Mensual` y su primer nodo actual (`Get row(s) in sheet1`). Solo deja pasar en la corrida de cierre:

- Condición **boolean**, `leftValue`:
  ```
  ={{ (() => { const tz='America/Montevideo'; const now=DateTime.now().setZone(tz).startOf('day'); const jsDow=now.toJSDate().getDay(); const sat=now.minus({days:(jsDow+1)%7}); const f=(d)=>d.plus({days:(6-d.weekday+7)%7}); const curr=sat.startOf('month'); const prevEnd=curr.minus({days:1}); const prev=prevEnd.startOf('month'); const meso=sat.hasSame(f(prevEnd),'day')?prev:curr; return sat.hasSame(f(meso.endOf('month').startOf('day')),'day'); })() }}
  ```
  operador **equals** `true`.
- Salida **true** → `Get row(s) in sheet1` (resto de la rama mensual sin cambios).

### 4.3 `Filtro4` — seleccionar el MES OBJETIVO (no el mes corriente)

Reemplazar el `rightValue` (hoy devuelve el nombre del mes corriente) por:

```
={{ (() => { const tz='America/Montevideo'; const now=DateTime.now().setZone(tz).startOf('day'); const jsDow=now.toJSDate().getDay(); const sat=now.minus({days:(jsDow+1)%7}); const f=(d)=>d.plus({days:(6-d.weekday+7)%7}); const curr=sat.startOf('month'); const prevEnd=curr.minus({days:1}); const prev=prevEnd.startOf('month'); const meso=sat.hasSame(f(prevEnd),'day')?prev:curr; const M=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']; return M[meso.month-1]; })() }}
```

`leftValue` sigue siendo `={{ $json.Mes }}`, operador equals.

### 4.4 `Preparar HTML ` (mensual) — `mesLabel` desde el mes objetivo

> ⚠️ El nodo se llama literalmente `Preparar HTML ` (con **espacio al final**); no confundir con `Preparar HTML 2` (semanal). `DateTime` (Luxon) está disponible en los Code nodes de n8n.

Hoy calcula `const mesLabel = \`${MESES[ahora.getMonth()]} ${ahora.getFullYear()}\`;` (mes corriente). Reemplazar ese cálculo por:

```js
// dentro de Preparar HTML, reemplazar el cálculo de mesLabel:
const tz='America/Montevideo';
const now=DateTime.now().setZone(tz).startOf('day');
const jsDow=now.toJSDate().getDay();
const sat=now.minus({days:(jsDow+1)%7});
const f=(d)=>d.plus({days:(6-d.weekday+7)%7});
const curr=sat.startOf('month');const prevEnd=curr.minus({days:1});const prev=prevEnd.startOf('month');
const meso=sat.hasSame(f(prevEnd),'day')?prev:curr;
const M=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
const mesLabel = M[meso.month-1] + ' ' + meso.year;
```

### 4.5 `Trigger Reporte Semanal` — fijar el día

- Regla: **`weeks`**, `triggerAtDay: [0]` (domingo), `triggerAtHour: 8`. La rama semanal **no cambia su lógica** (`Filtro7` ya reporta la semana recién cerrada; completa porque el domingo no tiene datos).

> Rama **Diario** (API Dentalink): sin cambios.

---

## 5. Workflow `SNR | Reporte Facturación v3.2`

### 5.1 Filtrar las ramas Mensual + Semana_mes al MES OBJETIVO (evita colisión y captura la cola)

`Semana_mes` no está calificado por mes (`"Semana 1".."Semana 5"`). En la corrida de cierre la planilla tiene 2 meses → hay que filtrar.

**Filtro a insertar** (Filter node, typeVersion 2): condición `={{ $json.Mes }}` **equals**
```
={{ (() => { const tz='America/Montevideo'; const now=DateTime.now().setZone(tz).startOf('day'); const jsDow=now.toJSDate().getDay(); const sat=now.minus({days:(jsDow+1)%7}); const f=(d)=>d.plus({days:(6-d.weekday+7)%7}); const curr=sat.startOf('month'); const prevEnd=curr.minus({days:1}); const prev=prevEnd.startOf('month'); const meso=sat.hasSame(f(prevEnd),'day')?prev:curr; const M=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']; return M[meso.month-1]; })() }}
```

**Rewiring (2 filtros):**

- **`Filtro Mes Objetivo A`** (desde `Categoria`):
  - Borrar conexiones `Categoria → Pagado Mes` y `Categoria → Pagado Semana_mes`.
  - Agregar `Categoria → Filtro Mes Objetivo A`.
  - Agregar `Filtro Mes Objetivo A → Pagado Mes` y `Filtro Mes Objetivo A → Pagado Semana_mes`.
  - **Dejar intacto** `Categoria → Pagado Semana` (semana absoluta NO se filtra).

- **`Filtro Mes Objetivo B`** (desde `Clase1`):
  - Borrar `Clase1 → Pagado y Cantidad Mes1` y `Clase1 → Pagado y Cantidad Semana_mes`.
  - Agregar `Clase1 → Filtro Mes Objetivo B`.
  - Agregar `Filtro Mes Objetivo B → Pagado y Cantidad Mes1` y `Filtro Mes Objetivo B → Pagado y Cantidad Semana_mes`.
  - **Dejar intacto** `Clase1 → Pagado y Cantidad Semana`.

### 5.2 Retimar el borrado de `MES CORRIENTE` (cambio de 1 parámetro)

`Trigger Borrar` hoy dispara el **día 1** (borra antes de que se cargue la cola del mes saliente). Cambiarlo a:
- **`months`**, `triggerAtDayOfMonth: 8`, `triggerAtHour: 1`.

Así el borrado ocurre **después** del cierre del mes (primer domingo, día ≤ 7) y **antes** de la primera escritura del mes nuevo (segundo domingo, día ≥ 8). La última semana del mes saliente queda visible entre el cierre y el día 8.

### 5.3 `Trigger Reporte Semanal` — fijar el día

- Regla: **`weeks`**, `triggerAtDay: [0]` (domingo), `triggerAtHour: 6` (después de la carga del sábado).

### 5.4 `Por sucursal mes` — tab por año del MES OBJETIVO (arregla borde de año)

Cambiar el `sheetName` de `={{ $now.year.format('es') }}` a:
```
={{ (() => { const tz='America/Montevideo'; const now=DateTime.now().setZone(tz).startOf('day'); const jsDow=now.toJSDate().getDay(); const sat=now.minus({days:(jsDow+1)%7}); const f=(d)=>d.plus({days:(6-d.weekday+7)%7}); const curr=sat.startOf('month'); const prevEnd=curr.minus({days:1}); const prev=prevEnd.startOf('month'); const meso=sat.hasSame(f(prevEnd),'day')?prev:curr; return String(meso.year); })() }}
```
(En enero, diciembre se escribe al tab del año correcto.)

### 5.5 `Detectar semana puente` — eliminar (código muerto)

El flag `esSemanaPuente` se calcula pero nadie lo usa (su única conexión, `→ Get row(s) in sheet`, lo ignora). Eliminar el nodo y conectar `Trigger Reporte Semanal → Get row(s) in sheet` directo (y `Webhook → Get row(s) in sheet`).

---

## 6. La regla de carga para Cecilia (resumen del correo)

El correo del sábado calcula y muestra el rango. Cecilia **descarga de Dentalink ese rango exacto y lo pega reemplazando todo** en la planilla "Ingreso datos":

| Caso | Rango (lo calcula el correo) — **vigente desde 2026-06-07** |
|---|---|
| Cualquier sábado | `domingo anterior → hoy (sábado)` (7 días corridos) |

> **Cambio 2026-06-07 (post-migración a Data Table).** Antes el rango era `[1° del mes
> objetivo → hoy]` y Cecilia recargaba todo el mes cada sábado. Con el histórico ahora en
> la Data Table `SNR | Histórico Pagos` y `appendOrUpdate` idempotente, la última semana
> alcanza — el resto del mes ya está acumulado en el histórico. Borde de mes: como el
> rango son 7 días corridos, una semana que cruza meses se carga completa en una sola vez
> y el flujo categoriza cada fila por su `Mes_de_recepcion_del_pago`.

No incluye domingos (la clínica no abre). No requiere que Cecilia aplique ninguna regla: copia las fechas del correo.

---

## 7. Verificación post-implementación

1. **Simulación (ya corre):** `python3 scripts/utilities/verify-sonrisas-fechas.py` → debe decir "0 días perdidos".
2. **Recordatorio:** ejecutar el flujo (MCP `execute_workflow` o botón) un sábado normal y un primer-sábado de mes; confirmar que el rango del correo coincide con la tabla §6.
3. **Cierre mensual:** en el primer domingo de un mes, confirmar que sale el correo mensual del **mes anterior** (`mesLabel` = mes anterior) y que su total = suma de TODOS los días de ese mes (incluida la última semana).
4. **Sin colisión:** en esa misma corrida, revisar `MES CORRIENTE`: las filas `Semana N` corresponden solo al mes que cierra (no mezcladas con el mes nuevo).
5. **Semana borde:** la semana absoluta que cruza el mes debe incluir los días de ambos meses.
6. **Coherencia:** para un mes ya cerrado, los montos del correo mensual = los de la planilla del Reporte = Dentalink.
7. **Borrado:** confirmar que `MES CORRIENTE` se limpia el día 8 (no el 1) y que el mes nuevo se escribe desde el 2º domingo.

---

## 8. Rollback

Cada workflow se versiona antes de editar (export del JSON actual a `03_workflows/*-vN.json`). Si algo falla, reimportar la versión previa. Los triggers viejos: Reporte semanal `weeks@12`, Borrar `months@13` (día 1), Correo mensual `months` (último día), Recordatorio sin cambios.
