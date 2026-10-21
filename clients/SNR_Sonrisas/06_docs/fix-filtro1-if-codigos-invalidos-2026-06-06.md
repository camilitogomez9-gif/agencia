# Fix Filtro1 + IF "Códigos inválidos?" — Reporte Facturación v3.5

**Fecha:** 2026-06-06
**Workflow:** `Sonrisas | Reporte Facturación v3.5` (id `XCO4kWeKbsvPnnzz`)
**Severidad:** ALTA — el reporte aborta ante cualquier código nuevo en el Listado de Precios sin responder al webhook, y las fechas inválidas pasan silenciosas porque la rama de detección está rota.

---

## 1. Síntoma

En n8n vivo:

- `Filtro1` (Code) hace `throw new Error(...)` cuando detecta un código desconocido → la
  ejecución del workflow se aborta entera. El webhook se queda sin respuesta (ni `Respond Error`
  ni `Respond OK`), y el `errorWorkflow OBkUyb8fuo30DzA9` dispara, pero el caller no recibe la
  lista de códigos que faltan.
- El IF `Códigos inválidos?` aguas abajo tiene **las dos ramas vacías** (`main: [[], []]`).
  Aunque el `Filtro1` emitiera `_error: true`, el IF no rutea a ningún lado.

El v3.5 del repo SÍ tiene el patrón correcto (`return [{ json: { _error: true, codigos,
fechas_invalidas } }]` + IF cableado a `Respond Error` / `Clase1+Categoria`). El estado vivo
en n8n quedó desincronizado.

## 2. Causa raíz

El script `scripts/utilities/update-sonrisas-nodes.py` generaba el bloque JS de `Filtro1`
con el patrón **antiguo** (`throw new Error`), no con el patrón v3.5 (`return [{ _error: true }]`).
La última vez que Cecilia entregó un Listado de Precios actualizado, se corrió el script y
se pegó el output en n8n → pisó el patrón v3.5 vigente. Al pegar el nodo regenerado, las
conexiones del IF "Códigos inválidos?" se perdieron en el proceso.

**Causa raíz fixeada en este commit:** el script generador ahora produce el patrón v3.5
correcto (commit del 2026-06-06). La próxima regeneración no rompe.

## 3. Cómo aplicar el fix en n8n (3 pasos)

### Paso 1 — Reemplazar el JS de `Filtro1`

Abrir el nodo `Filtro1` en el workflow `Sonrisas | Reporte Facturación v3.5` y reemplazar
TODO el bloque de código por el output actualizado del script generador:

```bash
python3 scripts/utilities/update-sonrisas-nodes.py ~/Downloads/"Listado de Precios Completo.xlsx"
```

(usar el último listado que entregó Cecilia con códigos únicos y completos)

El script ahora genera el patrón v3.5: `return [{ json: { _error: true, codigos,
fechas_invalidas } }]` cuando hay desconocidos o `_fechaValida === false` en filas con
contenido. Items válidos llevan `_error: false`, `computaImporte`, `computaCantidad`.

Copiar el bloque "Filtro1" del output del script y pegarlo en el nodo. Guardar.

### Paso 2 — Re-conectar el IF `Códigos inválidos?`

El IF tiene ambas ramas vacías en producción. Cablear así:

- **Rama TRUE** (output 0, "true") → conectar a nodo `Respond Error`.
- **Rama FALSE** (output 1, "false") → conectar a **dos** nodos en paralelo:
  - `Clase1`
  - `Categoria`

(El v3.5 del repo confirma este cableado en sus `connections`.)

### Paso 3 — Smoke test

Disparar el webhook del reporte. Casos a verificar:

1. **Listado al día (códigos OK):** el reporte termina normal y responde `Respond OK`
   (`{"status":"ok"}`) por el webhook. Las pestañas `semana`, `Reporte general`, etc.
   se actualizan.
2. **Inyectar un código no listado** en una fila de prueba en `Ingreso datos` (ej. `ZZZ99`) y
   correr el reporte: la respuesta del webhook debe ser
   `{"status":"error","codigos":"ZZZ99","fechas_invalidas":[]}` (status 200). El flujo NO debe
   escribir nada en las pestañas downstream.
3. **Inyectar una fecha no parseable** (ej. texto `"asdf"` en `Fecha de recepción del pago`)
   en una fila con contenido y correr: respuesta del webhook debe traer
   `fechas_invalidas: ["fila N cod=XXXX fecha='asdf'"]` y NO escribir downstream.

Si los 3 pasan, el fix está OK.

## 4. Sincronizar v3.5 del repo con producción (opcional, recomendado)

El JSON del repo `sonrisas-reporte-facturacion-v3.5.json` está desactualizado respecto a
producción por el fix de quota del 2026-06-01:

- `Get Histórico` debería leer de la pestaña `Histórico_2M` (no `Histórico`).
- `Filtrar Histórico 2M` aparece como conexión huérfana sin nodo en el JSON (porque se
  removió en n8n cuando se deshabilitó el filtro 2M).
- `Get Histórico` tiene `main: [[]]` (dead-end) en el JSON.

Después de aplicar Paso 1+2, exportar el workflow desde n8n y reemplazar el JSON del repo
para que el repo refleje la verdad de producción.

## 5. Bugs colaterales detectados (no urgentes)

Auditoría del flujo encontró 2 nodos con el mismo anti-patrón `throw` sin captura:

- **`Generar ID Sucursal`** (nodo Code, líneas ~1078 del JSON) — `throw new Error` si
  `Sucursal no reconocida` o `No hay Document ID`. Sin `onError` ni IF downstream.
- **`Generar ID+Sheet Sucursal`** (clon del anterior, líneas ~1351) — mismo patrón.

Si alguna vez una sucursal del Loop sale con nombre inesperado, el `throw` aborta la cola
entera y el resto de sucursales no se procesan. Recomendado: convertir al patrón
`_error: true` + IF + Respond Error, o como mínimo agregarles
`onError: "continueErrorOutput"` para que la sucursal con problema se saltee y las demás
sigan.

No es urgente porque los nombres de sucursal son estables, pero es la misma deuda técnica.
