# Fix reconciliación Mensual vs Semanal — Reporte Facturación Sonrisas

**Fecha:** 2026-05-25
**Workflows nuevos:** `sonrisas-reporte-facturacion-v3.4.json` (endurecimiento) y
`sonrisas-reporte-facturacion-v3.5.json` (**fix permanente + filtro 2 meses**). El v3.3 queda intacto.
**Scripts:** `scripts/utilities/verify-sonrisas-reconciliacion.py` (auditoría),
`fix-sonrisas-reconciliacion-workflow.py` (v3.3→v3.4), `fix-sonrisas-historico-workflow.py` (v3.4→v3.5).

---

## 1. Síntoma

Para Sucursal × Clase, el total **mensual** no coincidía con el **semanal** (que deberían
ser idénticos). Caso reportado: **Paso Molino × AJUSTE** → mensual $2.842.940 vs semanal
$2.828.030, gap **$14.910**.

## 2. Causa raíz (confirmada con los datos del año completo)

- El total **verdadero** = **$2.842.940** = el total **mensual** → **el mensual está bien**.
- A nivel cómputo Σmes = Σsemana (son particiones del mismo conjunto). **No hay fechas
  inválidas** en el dataset (0). **No es una fila de semana faltante.**
- El 100% del descuadre está en **semanas puente** (una semana Lun–Dom que cruza el borde
  de dos meses). En 2026 la única con actividad de los dos lados es **S14** (lun 30-mar →
  dom 5-abr); los otros bordes de mes cayeron en días que la clínica no atiende.
- **Mecanismo:** "Ingreso datos" se carga por **ventana** (mes objetivo / fechas del
  recordatorio a Cecilia). La semana puente se procesa en **dos cargas**: el cierre de marzo
  la escribe completa, y la corrida de **abril, al ver solo datos de abril, sobrescribe**
  (`operation: update`) la fila S14 con su porción de abril → se pierde la porción de marzo.
  Los meses no sufren esto porque cada mes está completo dentro de su propia ventana.

**Quiebre de S14 — Paso Molino × AJUSTE:** Marzo (30-31) $14.910 + Abril (1-2) $42.795 =
$57.705. El Sheet mostraba $42.795 (solo abril) → perdió $14.910 (marzo). Exacto.

**Alcance (todas las sucursales, todas en S14):** 9 celdas pierden su porción de marzo,
≈ **$206.920** mal asignados en la vista semanal (la plata del negocio está bien; el mensual
es correcto — es integridad del reporte semanal).

| Sucursal | Clase | S14 real | Pierde (marzo) |
|---|---|---|---|
| SUY 1 Centro | AJUSTE | 113.440 | 38.145 |
| SUY 1 Centro | COMBO | 18.520 | 7.670 |
| SUY 1 Centro | OTRO | 120.820 | 60.920 |
| SUY 1 Centro | RETIRO | 30.900 | 6.480 |
| SUY 2 Paso Molino | AJUSTE | 57.705 | 14.910 |
| SUY 2 Paso Molino | OTRO | 71.660 | 41.820 |
| SUY 3 Las Piedras | AJUSTE | 36.650 | 19.125 |
| SUY 3 Las Piedras | OTRO | 24.610 | 16.460 |
| SUY 4 Lagomar | AJUSTE | 3.870 | 1.390 |

## 3. Arreglo INMEDIATO (sin tocar código, sana lo ya roto)

Cargar el **año completo** en "Ingreso datos" y correr el reporte una vez. El reporte lee
toda la hoja y sobrescribe → S14 se recalcula completo en las 9 celdas y queda sano (durable:
las cargas futuras de mayo+ no vuelven a tocar S14). Verificar con la tabla "S14 real" de §2.

## 4. Arreglo PERMANENTE — v3.5: Histórico de-duplicado

Para que **ninguna** semana puente se vuelva a romper sin depender de cómo Cecilia cargue,
el reporte agrega siempre desde el **año completo**:

- Nodos nuevos en el arranque: `Get row(s) in sheet` (ventana de Ingreso datos) →
  **`Keyear Histórico`** (agrega `_key = "# Pago" + "-" + "# Detalle Presupuesto"`) →
  **`Upsert Histórico`** (`appendOrUpdate` en pestaña `Histórico` del doc de Ingreso datos,
  match por `_key`) → **`Get Histórico`** (lee el año completo) → resto del reporte.
- `_key` es único (15.839 filas → 15.839 claves, **0 colisiones**). El `appendOrUpdate`
  absorbe altas y **correcciones de monto**, y es **idempotente** (re-correr la misma ventana
  no duplica).
- Como el reporte ahora agrega el año completo y sobrescribe, S14 (y todo) siempre se escribe
  con el valor completo. Hereda además de v3.4: parseo de fecha robusto, abort ante fecha no
  parseable, y writes `appendOrUpdate` (crea filas de semana nuevas).

### Setup en n8n (una vez)
1. En el Sheet de **Ingreso datos** (`1RnWwaqEnGlyuUNnG4HW8jl5WoxFB7ypEm-Ey67bQkO8`), crear
   pestaña **`Histórico`** con fila de encabezados exactamente:
   `_key | # Pago | # Detalle Presupuesto | Fecha de recepción del pago | Mes de recepción del pago | Nombre Sucursal | Código Prestación | Nombre categoría | Pagado Prestación | Abono Libre`.
   Formatear `Pagado Prestación` y `Abono Libre` como número.
   **Importante:** formatear `Fecha de recepción del pago` como **texto plano** (o formato de
   fecha que muestre `yyyy-mm-dd`). El correo (v4) parsea estricto `yyyy-MM-dd`; el reporte
   (v3.5) parsea robusto, así que esto es por el correo.
2. Importar `sonrisas-reporte-facturacion-v3.5.json`. Asignar la credencial de Google Sheets
   en `Upsert Histórico` y `Get Histórico` (la exportación no trae credenciales).
3. Confirmar que `Get row(s) in sheet` quede **habilitado** (lee Ingreso datos).

### Verificación (plan de prueba en n8n)
- **Backfill:** cargar el año completo en Ingreso datos y correr → Histórico queda con ~15.839
  filas; el reporte escribe S14 completo en las 9 celdas (tabla §2).
- **Idempotencia:** correr dos veces la misma ventana → Histórico NO crece; totales iguales.
- **Puente:** cargar marzo, correr; cargar abril, correr → S14 = $57.705 (Paso Molino AJUSTE),
  no $42.795.
- **Corrección:** cambiar el monto de una fila (mismo `# Pago`+`# Detalle`) y recargar → el
  Histórico refleja el nuevo monto (no duplica).
- **Auditoría offline:** `verify-sonrisas-reconciliacion.py --csv <export> --sucursal X --clase Y`.

## 5. Correos — v4 (wireado al Histórico)

`sonrisas-correos-reportes-facturacion-v4.json`: **único cambio** sobre v3 → las dos lecturas
(`Get row(s) in sheet`, `Get row(s) in sheet1`) leen el tab **`Histórico`** en vez de
`Facturación`. Los emails Semanal y Mensual ya filtran al período actual (`Filtro7` = semana
actual, `Filtro4` = mes actual), así que ahora acotan el período **sobre datos completos**.
El pipeline Diario usa `Pagos2` (HTTP) y no se tocó. Verificado: v4 vs v3 difieren solo en
esos 2 `sheetName` (43 nodos, conexiones idénticas). Migración:
`scripts/utilities/fix-sonrisas-correos-historico.py`.

- **Dependencias:** (a) el `Histórico` debe estar poblado (lo mantiene el Reporte v3.5 al correr);
  correr el reporte antes que los correos. (b) la columna `Fecha de recepción del pago` del
  `Histórico` debe devolverse como `yyyy-mm-dd` (correos parsea estricto). Si en el futuro se
  quiere que el correo sea autónomo, agregarle la misma cadena `Keyear → Upsert → Get Histórico`.

## 6. Filtro de memoria — nodo `Filtrar Histórico 2M` (v3.5)

En instancias n8n con RAM ajustada (2 GB), cargar el año completo desde `Histórico` (~15.840 filas)
más el fan-out de 6 ramas `Summarize` agota el heap antes de que el reporte termine. Para resolverlo
sin comprometer la corrección, v3.5 incluye un nodo `Filtrar Histórico 2M` (Code) **entre**
`Get Histórico` y `Parsear y validar fecha` que descarta las filas anteriores a los 2 meses
actuales:

```
Get Histórico → Filtrar Histórico 2M → Parsear y validar fecha → …
```

**Lógica del filtro:**
```js
const now = DateTime.now().setZone('America/Montevideo');
const mesCorriente = M[now.month - 1];
const mesAnterior  = M[(now.month - 2 + 12) % 12];
const mesesValidos = new Set([mesCorriente, mesAnterior]);
return items.filter(item =>
  mesesValidos.has(String(item.json['Mes de recepción del pago'] ?? '').trim())
);
```

**Por qué 2 meses son suficientes:**
- El reporte sobrescribe (`appendOrUpdate`) las etiquetas de mes/semana; los meses anteriores ya
  tienen valores correctos en el Sheet desde corridas previas.
- La única semana puente en riesgo es siempre la del borde entre el mes corriente y el anterior
  → ambos meses quedan cubiertos.
- `Histórico` sigue acumulando el año completo vía `Upsert Histórico`; solo el *procesamiento*
  se acota. Si en alguna corrida futura se necesita recalcular un mes más antiguo, basta
  desactivar temporalmente el nodo `Filtrar Histórico 2M` y correr una vez con el año completo.

**En la práctica (mayo 2026):** de ~15.840 filas se procesan ~3.500–5.000 (mayo + abril), lo
que entra holgadamente en 2 GB.

## 7. Bloque Clase = solo ortodoncia (eliminar OTRO)

**Síntoma:** las columnas `cantidad OTRO` / `pagado OTRO` del bloque Clase mostraban valores
altos. En el año completo: **OTRO = $9.182.647 (4.572 filas, 42% de la facturación)**.

**Causa (no es bug):** el bloque Clase clasifica por coincidencia exacta de `Rubro` →
`ORTODONCIA AJUSTES`=AJUSTE, `ORTODONCIA INSTALACION`=COMBO, `ORTODONCIA RETIRO`=RETIRO; todo
lo demás caía en OTRO. Verificado: el nodo `Clase1` está **100% en sync** con el listado de
precios (AJUSTE 99, COMBO 36, RETIRO 15 — idénticos), así que **regenerar con el skill no
cambia nada** (y de hecho rompería: el listado nuevo perdió `C0015`, presente en datos →
`Filtro1` abortaría). El OTRO es **odontología general genuina** (restauraciones, limpiezas,
conductos, extracciones, prótesis, implantes), no un error.

**Decisión (cliente):** el bloque **Clase es ortodoncia-only**. Las filas no-ortodoncia se
descartan del bloque Clase (siguen contabilizadas en el bloque **Categoría**: GENERAL,
PROTESIS, CIRUGIA, ENDODONCIA, etc.).

**Cambios:**
1. `Clase1` (Code): el `return items.map(...)` final pasa a un `for...continue` que **descarta**
   las filas cuyo código no está en `CLASES_ORTODONCIA` (solo AJUSTE/COMBO/RETIRO pasan al
   Summarize). Constantes `CLASES_ORTODONCIA` / `noSumanCantidad` sin cambios.
2. Writers `Reporte general` y `semana`: se quitan las columnas `pagadoOTRO` y `cantidadOTRO`
   del mapeo (`value` + `schema`). Los writers `Por sucursal mes/semana` ya no las tenían.
3. **Manual (una vez):** borrar las columnas `Pagado OTRO` / `Cantidad OTRO` de las hojas de
   `Reporte general` y de la hoja semanal (`Facturación`), ya que el flujo deja de escribirlas
   y de lo contrario quedaría el valor viejo.

**Verificación (datos reales):** bloque Clase ortho = AJUSTE $10.267.758 + COMBO $757.736 +
RETIRO $1.443.640 = **$12.469.134**; no-ortho $9.182.647 sale del bloque Clase pero el total
global sigue cuadrando ($12,47M + $9,18M = $21.651.781). `node --check` OK.

**Durabilidad:** `update-sonrisas-nodes.py` (`generar_clase`) también filtra ahora, así que
una futura regeneración del nodo no reintroduce OTRO.

## 8. Clasificación 100% por código + validación de unicidad (2026-05-26)

**Decisión (cliente):** CATEGORIA y CLASE se determinan **puramente por el Código de Prestación**.
A partir del listado se arma código→categoría y código→clase (vía `Rubro`) y se hardcodea en los
nodos; en runtime sólo se hace lookup por código. Sin fallback al `Nombre categoría` de la
transacción.

**Condición para que sea robusto:** cada código debe mapear a **un único Rubro**. Por eso
`update-sonrisas-nodes.py` ahora **valida ANTES de generar nada** y aborta (exit 1) si:
1. Hay **códigos duplicados** (aparecen en >1 fila — sea Rubros en conflicto o fila redundante).
   → pedir a Cecilia que deje una sola fila/Rubro por código.
2. Hay un **Rubro desconocido** (no está en `RUBRO_A_CATEGORIA`) → evita categoría `OTRO` silenciosa.

El nodo `Categoria` generado ya **no lleva** el bloque de códigos ambiguos / `resolverAmbiguo`.

**Estado del listado actual (no pasa la validación):**
- **11 duplicados:** 9 en conflicto PERIODONCIA↔PROTESIS (`P0000, P1000–P1004, P2000–P2002` — mismo
  código reusado para dos prestaciones distintas, ambas presentes en datos reales) + 2 redundantes
  (`C0014`, `RD003`, mismo Rubro repetido).
- **2 códigos facturados que faltan:** `C0015` (Extracción Diente Supernumerario, $31.740/8 filas) y
  `302` ($1.990/1 fila). Si se regenera el `Filtro` sin ellos, el reporte abortaría al verlos.

**Pendiente (bloquea regenerar):** Cecilia entrega un listado con **códigos únicos y completo**
(deduplicar los 11, agregar `C0015` y el código real de `302`). Recién ahí se regeneran los nodos
`Filtro`/`Categoria`/`Clase` (Reporte) y `Filtro`/`Categoria`/`Clase`/`Filtro3`/`Categoria1`/`Clase1`
(Correos) y se pegan en n8n. **Hasta entonces no regenerar el `Filtro`.** El workflow en vivo
conserva el `Categoria` con fallback (exacto para los 9 ambiguos) mientras tanto.

## 9. ⚠️ El filtro de memoria `Filtrar Histórico 2M` re-rompe la reconciliación de S14

**Hallazgo (2026-05-26):** `Filtrar Histórico 2M` filtra por **mes calendario**
(`Mes ∈ {mes actual, mes anterior}`). Como semanas (Lun–Dom) y meses no se alinean, **parte la
semana puente del borde lejano de la ventana**. Hoy (mayo) la ventana es {Mayo, Abril}: la S14
(Lun 30-mar → Dom 5-abr) entra por sus filas de abril pero se excluyen las de marzo, así que el
writer reescribe **S14 = $42.795 (solo abril)** en vez de **$57.705** → **vuelve el gap de
$14.910** que el Histórico había arreglado.

**No se arregla agrandando la ventana:** cualquier ventana de K meses calendario re-rompe S14 el
mes en que su lado viejo sale de la ventana y el nuevo sigue dentro (2 meses → rompe en mayo;
3 meses → rompe en junio).

**Fix correcto (requiere diseño + prueba en n8n, NO se aplica a ciegas):** ventana de lectura
**alineada a semana** (corte en lunes) para que ninguna semana-año se parta + **scope de los
writers mensuales a meses completos** (no reescribir el mes parcial del borde). Interactúa con
`Semana_mes` (semana-del-mes): `Por sucursal semana` matchea por `Nro de semana` (semana-del-mes,
no semana-año), así que datos multi-mes ya mezclan meses en esa vista. Por eso el rediseño debe
validarse corriendo en n8n contra un backfill del año completo.

**Recomendación inmediata (segura, probable solución):** **deshabilitar `Filtrar Histórico 2M`**
y procesar el **año completo** (comportamiento original, reconciliación garantizada). Con el
Histórico ahora de 8 columnas las filas son más livianas → puede que ya entre en 2 GB. Probar:
si NO hace OOM, dejarlo deshabilitado (es la solución correcta y más simple, y de paso sana S14).
Si hace OOM, recién ahí encarar el rediseño de ventana alineada a semana (con prueba).

**RESUELTO (2026-05-26):** se deshabilitó `Filtrar Histórico 2M` y se corrió el año completo
**sin OOM** (el Histórico de 8 columnas entra en 2 GB). Estado final: el reporte procesa el año
completo → reconciliación garantizada + S14 sano. `Filtrar Histórico 2M` queda **deshabilitado**
(se conserva el nodo por si en el futuro crece el dataset y hace falta el rediseño alineado a
semana). También se borraron las columnas `Pagado/Cantidad OTRO` de las hojas Reporte general y
semanal, y se limpió el `combineFilters` huérfano de `Get Histórico`.
