# Fixes aplicados post-auditoría — 2026-07-01

> Estado de ejecución de los P0 del reporte `airtable-auditoria-2026-07-01.md`, ronda del 2026-07-01 noche. Hecho por Claude directo (sin workflow multi-agente — no hacía falta, era ejecución de un plan ya definido, no descubrimiento).

---

## Hallazgo previo a tocar nada

Se verificó vía API que **el fix de S-01 descrito como "ya ejecutado por la agencia" no estaba aplicado en la base viva** (37 records basura y 77 links seguían intactos). Hipótesis: se aplicó sobre la copia de backup en vez de la base original, o los comandos del reporte (deliberadamente comentados con `#` por seguridad) se copiaron sin descomentar la línea real. No bloqueante — se corrigió abajo.

---

## ✅ Aplicado directo en Airtable (real, verificado post-escritura)

### S-01 — Sustratos contaminados
- **PASO 2**: vaciado `Sustratos compatibles` en los 77 equipos afectados.
- **PASO 3**: borrados los 37 records basura de `Sustratos`.
- **Verificado**: `Sustratos` = 16 records, todos legítimos. `Equipos` = 0 con links colgados.
- **Pendiente (no yo, decisión + trabajo de Edgardo)**: repoblar los links Equipos→Sustratos reales usando la matriz Tecnología×Sustrato — sin esto, `consultar_catalogo` devuelve `sustratos: []` en vez de vacío-por-basura, que es un avance pero sigue sin dar el dato. Es un trabajo de contenido, no de limpieza — no lo puedo inferir yo sin la matriz real del cliente.

### T-06 — Formato (parcial)
- Migrados los 10 records: 6× `MESA`→`Mesa`, 3× `PLOTTER`→`Plotter`, 1× `PLIEGO`→`Pliego`. Verificado.
- **NO se pudo** limpiar las 4 choices basura del dropdown (`Formato`, `MESA`, `PLOTTER`, `PLIEGO` quedan como opciones muertas, 0 records las usan). Ver bloqueo abajo.

### T-05 — Marca (parcial)
- 0 records en `Equipos` usan hoy `KONIKA`/`MINOLTA`/`Marca`/`Sinajet` — no había nada que migrar (los equipos Konica viven solo en la tabla separada `Konica Minolta`, no en `Equipos`).
- **NO se pudo** agregar la choice `KONICA MINOLTA` ni limpiar las 4 choices basura del dropdown de `Marca`. Ver bloqueo abajo.

---

## 🚫 Bloqueado — limpieza de choices (dropdowns) de Marca y Formato

Los intentos de `PATCH` a `/v0/meta/bases/{base}/tables/{table}/fields/{field}` (agregar/quitar opciones de los singleSelect `Marca` y `Formato`) devuelven `422 INVALID_REQUEST_UNKNOWN`. Hipótesis más probable: el token (`06_docs/airtable-credentials.md`) tiene scopes `data.records:read/write` + `schema.bases:read`, pero **no `schema.bases:write`** — sin ese scope, la escritura de schema falla.

**2 caminos, elegí uno:**

1. **Manual en UI (30 seg cada uno, más rápido que generar el token nuevo)**: abrir `Equipos` → columna `Marca` → editar campo → borrar las opciones `KONIKA`, `MINOLTA`, `Marca`, `Sinajet` (con S minúscula) → agregar opción `KONICA MINOLTA`. Repetir en `Formato`: borrar `Formato`, `MESA`, `PLOTTER`, `PLIEGO`.
2. **Generar un PAT nuevo con scope `schema.bases:write`** (https://airtable.com/create/tokens) y pasármelo — reintento la limpieza por API en un call, ya sin prueba-error (ya sé exactamente qué payload mandar).

Ninguna de las 2 es urgente: 0 records vivos dependen hoy de esas choices (son basura dormida, no rompen nada mientras tanto).

---

## ✅ Fixes de n8n — listos para pegar

### `sys-tool-consultar-catalogo` (T-01, T-02, T-03, T-04 + 1 bug adicional)

**Cubre:**
- T-01: `{Nombre}` → `{Aplicación}` en el filtro de Aplicaciones.
- T-02: `{Sustratos tipicos}` → `{Sustratos típicos}` (tilde).
- T-05 (mitad n8n): `BRAND_MAP` ahora emite `KONICA MINOLTA` / `SINAJET` (mayúsculas, matcheando el choice real).
- T-06 (mitad n8n): `FORMAT_MAP` ahora emite `Cilindrica` sin tilde (matcheando el choice real).
- T-03: `Format Output` separa el mapping de campos por intent (`equipo` / `aplicacion` / `inventario`) — antes todo se mapeaba con nombres de campo de `Equipos`, así que el inventario Konica devolvía todo vacío.
- T-04: sacada la referencia muerta a `Velocidad (m²/h)` (no existe en `Equipos`).
- **Bug adicional encontrado leyendo el código** (no estaba en el reporte): `Format Output` filtraba con `.filter(it => it.modelo)` al final — como los items de `intent=aplicacion` no tienen campo `modelo` (tienen `aplicacion`), **quedaban descartados igual aunque T-01/T-02 se arreglaran**. Ahora el filtro es consciente del intent.

**Cómo aplicar (elegí una):**

- **Opción recomendada — import completo, 1 click**: `03_workflows/sys-tool-consultar-catalogo-v5.json` ya está en el repo con el mismo `workflowId` (`oQtLMujJBHlxZTTJ`) que la v4 que reemplaza. En n8n: abrir el workflow → "…" → Import from File → elegir `sys-tool-consultar-catalogo-v5.json` → confirmar overwrite. Mismo patrón que usaste para v2/v3/v4.
- **Opción alternativa — pegar 2 nodos sueltos**: `06_docs/snippets/clipboard-consultar-catalogo-classify-format-2026-07-01.json` — copiar el archivo completo y pegar (Cmd+V) directo sobre el canvas del workflow vivo. Trae los 2 nodos (`Classify Intent` + `Format Output`) ya actualizados, mismos IDs/posiciones que los originales.
- **Atajo más rápido si solo querés el código**: abrir cada nodo Code en n8n, Ctrl/Cmd+A en el editor, pegar el contenido de `03_workflows/sys-tool-consultar-catalogo-v5.json` → nodo correspondiente → campo `parameters.jsCode` (o pedime el .js suelto de cualquiera de los 2 si preferís copiarlo sin abrir el JSON).

**Smoke test post-deploy** (3 turnos, del plan de fixes del reporte):
1. "quiero imprimir remeras" → debe devolver items de Aplicaciones, no NOT_FOUND.
2. "tenés un bizhub usado" → debe traer `contador_copias` con un número real (no `null`).
3. "impresora vinilo" → debe encontrar `Vinilo` en Sustratos (ya limpio post S-01).

### `sys-tool-consultar-lineas-priorizadas` (SD-11)

**Qué arregla:** el `Format Output` original hacía `(cfg['Líneas priorizadas'] || []).join(', ')` asumiendo que el campo es un array (Link). En vivo es `multilineText` (string). Si alguien escribe algo en ese campo, la próxima invocación de la tool **crashea con TypeError** (`.join` no existe en strings) — hoy está dormido solo porque el único record de `Config Mensual` lo tiene vacío. Fix: normaliza el valor a array sea string o array, sin tocar el schema de Airtable (evita la "cirugía cuidadosa" que mencionaba el reporte).

**Cómo aplicar:** `06_docs/snippets/clipboard-lineas-priorizadas-format-2026-07-01.json` — pegar sobre el canvas. **No generé el workflow completo para este tool** porque el archivo local no tiene el `workflowId` real registrado (a diferencia de `consultar_catalogo`) — si me pasás el ID (abrí el tool en n8n, mirá la URL) genero el import completo también.

**Nota operativa para cuando carguen `Líneas priorizadas`:** como el campo sigue siendo texto libre, hay que escribir los nombres de línea separados por coma (ej: `RISO, Eco-Solvente`) — el código ahora los separa solo.

---

## ✅ Ronda 2 — P1/P2 sin bloqueo (mismo día, después de definir alcance con la agencia)

Filtrado explícito: nada que necesite una decisión de Edgardo, nada que necesite el permiso de Airtable bloqueado.

### V-01 — 3 tools sin vista cableada → cableadas
- `sys-tool-consultar-inventario-usados` → vista `viwKrFyMCZqQynwKF` (Konica Minolta/Para agente). Sin `workflowId` local conocido → entregado como nodo suelto: `06_docs/snippets/clipboard-inventario-usados-view-2026-07-01.json`.
- `sys-tool-consultar-url-tienda` → vista `viwM6RjuUufxZMuI6` (Insumos/Para agente). `workflowId` conocido (`EDoSNfvaEQTevJmj`) → `03_workflows/sys-tool-consultar-url-tienda-v3.json`, import completo in-place.
- `sys-tool-consultar-catalogo` → el nodo `Airtable: Inventario Konica` también leía sin vista — ya viene incluido en el mismo `sys-tool-consultar-catalogo-v5.json` de arriba (no generé un 4to archivo, se sumó al v5 existente).
- **NO tocado**: la vista de Cabezales que mencionaba el reporte — reviewé los 8 tools vivos y ningún tool consulta hoy la tabla `Cabezales` directamente (la relación vive en 3 campos escalares dentro de `Equipos`). Cablear una vista ahí no tiene efecto — lo marco como no-aplicable, no como pendiente.

### Corrección de documentación — `05_crm/airtable-syscatalogo-schema.md`
Agregada sección "Correcciones 2026-07-01" al principio del doc con las 10 divergencias confirmadas doc-vs-base-viva (SD-03, SD-06, SD-09, P2-11, P2-21/34/35, SD-01/Leads, P2-09/39). Cero riesgo — es edición de nuestra propia documentación, no toca Airtable ni n8n.

---

## 🚫 Frenado por el classifier de permisos — correctamente

Intenté **S-04** (regenerar automáticamente los 0 links `Equipos↔Aplicaciones` derivándolos por superposición de Tecnología, como sugería el reporte) y el harness lo bloqueó: es **inventar relaciones de catálogo nuevas**, no limpiar basura obvia como S-01/T-06. Tiene razón — a diferencia de borrar un record que dice "166" en un campo de sustratos (inequívocamente basura), decidir que "este equipo UV sirve para esta aplicación" es una afirmación de negocio que Edgardo debería poder revisar antes de que quede escrita en la base que usa el agente con clientes reales.

**Si querés que lo haga igual:** puedo dejar el resultado de la derivación (qué links se crearían) en un CSV para que Edgardo lo revise en 5 minutos en la reunión y yo lo aplico después con su ok — en vez de escribirlo directo. Avisame si preferís eso.

---

## Pendiente — no cubierto, requiere Edgardo o el token con schema-write

- Limpieza de choices Marca/Formato basura (bloqueada por permiso, ver arriba) — 30 seg en UI.
- Repoblar Equipos↔Sustratos con datos reales (post S-01) — necesita la matriz Tecnología×Sustrato del cliente, no la puedo inventar.
- S-04 Equipos↔Aplicaciones — derivación lista para revisar, no escrita (ver arriba).
- ~15 findings con decisión abierta (ver `airtable-auditoria-2026-07-01.md` §5 "Preguntas para Edgardo") — S-02 (19 equipos sin marca — mi lectura del CSV original sugiere Sinajet, no TENETH como hipotetizaba el reporte, confirmar), P2-01 a P2-08 (duplicados, records fantasma, elecciones de negocio).
- ~20 findings de schema-type (SD-02, SD-08, SD-10, P2-10/12/13/14/16/18/19/20/27/37/38) — todos bloqueados por el mismo permiso `schema.bases:write` que faltó para T-05/T-06.
- Contenido nuevo (91 `Descripción corta` vacías, 16 `Descripción` de Sustratos vacías) — trabajo de redacción, no de limpieza; no inventé texto de producto sin fuente.

---

## ✅ Ronda 3 — 2026-07-XX (varios días después, la noche antes de la reunión)

la agencia confirmó 4 cosas y esto habilitó lo siguiente:

1. **Confirmado: todos los writes de Airtable se hicieron por PAT (`curl` directo), no por MCP.** El PAT tiene `data.records:write` (por eso los writes de datos funcionan) pero no `schema.bases:write` (por eso el schema-write sigue fallando).
2. **S-04 aprobado** → ejecutado. 62 de 92 equipos ahora tienen `Aplicaciones compatibles` poblado (370 links totales), derivados por superposición de Tecnología entre `Equipos` y `Aplicaciones`. Reverse link `Aplicaciones.Equipos` verificado: 20/20 aplicaciones con equipos linkeados (auto-poblado por Airtable). Los 30 equipos sin Tecnología o cuya Tecnología no matchea ninguna Aplicación (ej. Corte, IDL Láser, Gran Formato con 0 aplicaciones asociadas — ver P2-07) quedan sin este link, es esperado.
3. **Confirmado: los 3 workflows n8n (`consultar_catalogo` v5, `consultar_url_tienda` v3, `consultar_inventario_usados` v2) ya están importados en vivo.**
4. **Marca → `[KONIKA, MINOLTA] → [KONICA MINOLTA]` confirmado** como valor objetivo (coincide con lo que ya está codificado en el `BRAND_MAP` de `consultar_catalogo` v5, ya deployado — importante que la Airtable choice quede con EXACTAMENTE ese casing, `KONICA MINOLTA` todo mayúsculas con espacio, para que matchee).

**Reintento de schema-write (Marca):** un solo intento real y dirigido (no exploratorio) con el payload correcto → **falló de nuevo, mismo error 422 `INVALID_REQUEST_UNKNOWN`**. Confirma que no era un problema de formato del payload (ya se probaron 3 variantes distintas en 2 sesiones) — es un bloqueo sistemático, casi seguro por el scope faltante del token. No se reintentó una tercera vez. Instrucciones manuales para Edgardo/la agencia en la guía operativa actualizada.

**Verificación de uso de las choices garbage restantes** (para saber si el cleanup manual es 100% seguro):
- `Disponibilidad zona="Disponibilidad zona"`: 0 records.
- `Status="Status"`: 0 records.
- `Notas internas`: 3 de los 4 valores garbage con 0 records; **`"Stock disponible: 1 unidad/es"` con 5 records** — al convertir el campo de singleSelect a texto libre, esos 5 records conservan el string literal (no se pierde nada, solo deja de ser una "opción" y pasa a ser texto).

**No se tocó:** ninguna de las decisiones de negocio pendientes (duplicados, S-02 marca de las 19 series DF/DG/DH, contenido de descripciones). Se mantiene la misma línea de corte que en la Ronda 2 — todo lo que es limpieza inequívoca se hizo, todo lo que es decisión de Edgardo se dejó para la reunión.

**Docs actualizados en esta ronda:** `05_crm/airtable-syscatalogo-schema.md` (sección Correcciones), `06_docs/airtable-guia-edgardo-2026-07-02.md` (guía operativa completa — es la que se entrega a Edgardo mañana).
