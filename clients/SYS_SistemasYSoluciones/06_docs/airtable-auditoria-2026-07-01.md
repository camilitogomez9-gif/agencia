# Auditoría Airtable SYS — 2026-07-01

**Contexto:** reporte pre-reunión con Edgardo. Base viva `SyS Catalogo` (`appMD3g2HWxzBaZAM`, 11 tablas, ~266 records). Snapshot API en `/private/tmp/claude-501/.../airtable-snapshot/`. Schema de referencia: `05_crm/airtable-syscatalogo-schema.md` v1.1. Contrato tool ↔ Airtable: `03_workflows/sys-tool-consultar-catalogo-v4.json` y las 8 tools de F4/F5.

**Regla de oro:** ningún fix se aplica desde este reporte. Todos los `curl` van marcados como dry-run (`# DRY-RUN`) y requieren revisión de la agencia antes de ejecutar.

---

## 1. Resumen ejecutivo

Edgardo lo dijo tal cual en el audio del 2026-07-01 14:18:

> "En el campo Sustratos compatibles de Equipos veo valores 166, 186, 320 en lugar de nombres de sustratos. En la tabla Sustratos veo esas medidas como si fueran sustratos. No entiendo cómo hacer un cambio si el linkeo está roto."

Traducción técnica: la tabla `Sustratos` se pobló durante F1 (migración post-Excel del 2026-05-29) leyendo la columna `Ancho` de Equipos como si fuera un catálogo de sustratos. Airtable autocreó 37 records fantasma con nombres numéricos ("166", "200", "90*60", "297*420", "A4", …) y los 77 links `Equipos.Sustratos compatibles` apuntan al 100% a esos fantasmas — no a los 16 sustratos reales que también están cargados. El resultado es que la tool `consultar_catalogo` le devuelve al agente "este equipo imprime sobre 166, 186 y 320" y el agente se lo pasa literal al lead.

El bug de Sustratos es la punta del iceberg. La auditoría cruzada del snapshot vs. el schema doc vs. el JSON de las tools cerró **65 findings únicos**: **7 P0** (rompen tools vivas o le dan respuestas basura al agente), **19 P1** (degradan respuestas, confunden a Edgardo o dejan tools en NOT\_FOUND falso) y **39 P2** (cosméticos, drift doc/base, choices garbage, features pendientes). El grueso de los P0/P1 es la misma familia de causas: import CSV mal mapeado en F1 + schema doc que quedó desactualizado post-realineación + tools que se cablearon antes de estabilizar los names.

**Lo más urgente para llevar a la reunión mañana** (en este orden):

1. **P0 Sustratos contaminados + links basura** (finding S-01). Es lo que Edgardo ve. Fix en 3 pasos con backup previo.
2. **P0 tool `consultar_catalogo` con field names rotos** en Aplicaciones y Konica Minolta (findings T-01, T-02, T-03). La rama `intent=aplicacion` devuelve NOT\_FOUND siempre; el inventario Konica pierde el contador de copias en el output.
3. **P0 singleSelect `Marca` con `KONIKA` + `MINOLTA` como choices separadas** (finding T-05). Filter `{Marca}="Konica Minolta"` devuelve 0.
4. **P0 Config Mensual `Líneas priorizadas` como texto libre en vez de link** (finding SD-11). Bloquea la tool `consultar_lineas_priorizadas` si el field name que espera el tool no matchea.
5. **Confirmar con Edgardo** los 8-10 decisiones que solo él puede tomar antes de tocar la base (lista al final).

**Números totales por severidad:** P0 = 7 · P1 = 19 · P2 = 39 · Total = 65.

---

## 2. Findings P0 (rompen tool viva o dan respuestas basura al agente)

### P0 · S-01 — Tabla `Sustratos` contaminada: 37 de 53 records son basura numérica y todos los links Equipos→Sustratos apuntan a esos fantasmas

**Tabla afectada:** `Sustratos` (+ colateral en `Equipos.Sustratos compatibles`).

**Qué está mal.** El primary field `Sustrato` tiene 37 records cuyo valor es un ancho o dimensión ("30", "60", "67", "130", "150", "160", "166", "180", "186", "190", "196", "200", "210", "222", "250", "320", "330", "500", "660", "100\*100", "120\*150", "130\*190", "1300\*1300", "160\*120", "160\*88", "250\*130", "297\*420", "320\*200", "330\*250", "500\*700", "60\*40", "60\*90", "700\*900", "90\*60", "900\*1200", "A3", "A4"). Los 16 sustratos canónicos esperados (Algodón, Poliéster, Nylon, Denim, Lycra, Cuero sintético, Vidrio, Metal, Madera, Acrílico, Cerámica, PVC espumado, Lona, Vinilo, Papel común, Cartulina) están presentes pero mezclados. Los 77 links `Equipos.Sustratos compatibles` apuntan el 100% a records basura; los 16 reales tienen 0 equipos linkeados.

**Evidencia.**

```
Sustratos.json → 53 records. Regex ^\d+(\s*\*\s*\d+)?$ + {A3,A4} matchea 37 records.
Los 37 basura tienen Tipo=null, "Tecnologías compatibles"=[] y "Equipos" con arrays no-vacíos.
Los 16 reales tienen Tipo poblado y "Equipos"=[] (0 links).
Muestra del primary: 200, 500, Cerámica, 186, 90*60, 250, 297*420, 222, 150, 660, 700*900,
196, A4, 160*88, Poliéster, 210, 166, Vidrio, 250*130, 160*120, 60, 500*700, 180, Lycra,
Madera, Papel común, 100*100, 330, Cuero sintético, Metal, Algodón, ...
```

**Causa raíz probable.** Durante F1, el import del Excel del cliente mapeó la columna `Ancho` (u otra columna de dimensiones) al linked field `Sustratos compatibles` de Equipos. Airtable, cuando un linked field recibe un string que no matchea un record existente, autocrea el record con ese string como primary. Los 77 Equipos que traían Ancho quedaron linkeados a 37 sustratos-fantasma en lugar de a los 16 sustratos legítimos.

**Impacto en el agente.** El nodo `Format Output` de `sys-tool-consultar-catalogo-v4.json` lee `Sustratos compatibles` y devuelve al LLM los primary values de los records linkeados. Hoy el agente le dice al lead cosas como "este equipo imprime sobre 166, 186 y 320" o "sirve para A4 y 700\*900" en lugar de "vinilo, lona y papel". Afecta al 100% de los 77 equipos con sustratos cargados (84% del catálogo de Equipos). La tabla `Sustratos` está inutilizable como catálogo hasta que se limpie.

**Fix propuesto — 3 pasos, DRY-RUN, revisar antes de ejecutar.**

```bash
# PASO 1 — Backup de Sustratos y de los links de Equipos afectados
# DRY-RUN — la agencia confirma antes de correr
curl -s "https://api.airtable.com/v0/appMD3g2HWxzBaZAM/Sustratos?pageSize=100" \
  -H "Authorization: Bearer $AIRTABLE_TOKEN_SYS" \
  > /tmp/sustratos-backup-$(date +%Y%m%d).json

curl -s "https://api.airtable.com/v0/appMD3g2HWxzBaZAM/Equipos?fields%5B%5D=Modelo&fields%5B%5D=Sustratos%20compatibles&pageSize=100" \
  -H "Authorization: Bearer $AIRTABLE_TOKEN_SYS" \
  > /tmp/equipos-sustratos-backup-$(date +%Y%m%d).json

# PASO 2 — Vaciar los 77 links Equipos.Sustratos compatibles (para que el DELETE de sustratos basura no rompa integridad)
# Loop de PATCH batches de 10, dry-run: solo imprimir los payloads antes de mandar
# DRY-RUN — construir el batch payload y revisarlo primero
# Cuando esté OK, quitar el `echo` y agregar el curl real

# PASO 3 — Borrar los 37 records basura de Sustratos
# Extraer IDs del backup con jq y borrarlos en batches de 10 (endpoint DELETE con records[])
jq -r '.records[] | select(.fields.Sustrato | test("^[0-9]+(\\s*\\*\\s*[0-9]+)?$") or . == "A3" or . == "A4") | .id' \
  /tmp/sustratos-backup-$(date +%Y%m%d).json \
  > /tmp/sustratos-basura-ids.txt

wc -l /tmp/sustratos-basura-ids.txt  # esperar 37

# DRY-RUN — recién después de confirmar que son los 37 esperados:
# xargs -n 10 sh -c 'curl -X DELETE "https://api.airtable.com/v0/appMD3g2HWxzBaZAM/Sustratos?$(printf "records%%5B%%5D=%s&" "$@" | sed s/\&$//)" -H "Authorization: Bearer $AIRTABLE_TOKEN_SYS"' _ < /tmp/sustratos-basura-ids.txt
```

**Riesgo del fix.** (a) Si se borran sustratos basura ANTES de vaciar los links en Equipos, los links quedan como refs colgadas y Airtable puede devolver `null` en lugar de un valor limpio. Por eso el paso 2 va antes del 3. (b) Los sustratos "A3" y "A4" son formatos de papel; confirmar con Edgardo si conviene renombrarlos a "Papel A3" / "Papel A4" y conservarlos, en vez de borrarlos. (c) Después del cleanup, hay que **repoblar manualmente** los links Equipos→Sustratos usando la matriz Tecnología×Sustrato del CSV `02-sustratos.csv` o el Excel original del cliente — sin ese repoblado, el agente responde `sustratos_compatibles: []` para 77 equipos.

**Depende de.** Nada — es el fix raíz. Habilita después: crear vista "Para agente" en Sustratos (finding V-03) y migrar `Aplicaciones.Sustratos típicos` a link real (finding SD-08).

---

### P0 · T-01 — `consultar_catalogo` filtra Aplicaciones por field `{Nombre}` que NO existe

**Tabla afectada:** `Aplicaciones` (tool `consultar_catalogo`).

**Qué está mal.** El nodo `Classify Intent` de `sys-tool-consultar-catalogo-v4.json` construye `filterByFormula` para intent=aplicacion con `SEARCH(..., LOWER({Nombre}))`. El primary field real de Aplicaciones es `Aplicación` (con tilde). No existe field `Nombre` en la tabla.

**Evidencia.**

```
sys-tool-consultar-catalogo-v4.json, nodo Classify Intent:
  OR(SEARCH("...", LOWER({Nombre})), SEARCH("...", LOWER(ARRAYJOIN({Sustratos tipicos}))))

00-schema.json, tabla Aplicaciones, primary field:
  id=fldKmAkUmsZsmwfoi name="Aplicación" type=multilineText

Fields totales Aplicaciones: ['Aplicación', 'Categoría', 'Tecnologías recomendadas',
  'Sustratos típicos', 'Keywords cliente', 'Equipos']. NO hay 'Nombre'.
```

**Causa raíz probable.** El schema doc primitivo mencionaba `Nombre`; F1 creó el field como `Aplicación`. La tool nunca se re-sincronizó al schema real.

**Impacto en el agente.** Cuando el LLM clasifica un turno como intent=aplicacion ("quiero imprimir remeras", "estampo gorras", "imprimo lonas"), Airtable devuelve error 422 (o 0 records) por field inexistente. `Format Output` devuelve NOT\_FOUND. El agente cae a "no encontré esa aplicación, contactá al comercial" cuando el catálogo la tiene cargada. **Toda la rama de intent=aplicacion está muerta.**

**Fix propuesto — edit del sub-workflow, NO toca Airtable.**

```
En n8n, sub-workflow sys-tool-consultar-catalogo (workflowId oQtLMujJBHlxZTTJ):
  nodo Classify Intent (Code JS)
  buscar: {Nombre}
  reemplazar: {Aplicación}
  (mismo bloque, para la rama APLICACIONES; ver también finding T-02 en el mismo edit)
Re-export como sys-tool-consultar-catalogo-v5.json y commit al repo.
```

**Riesgo del fix.** Bajo. El único punto de atención es que el file en repo debe re-exportarse post-edit y el workflowId debe preservarse (import in-place). Smoke test: mandar al webhook un turno con "quiero imprimir remeras" y confirmar que `consultar_catalogo` devuelve records de Aplicaciones (no NOT\_FOUND).

**Depende de.** T-02 (mismo edit).

---

### P0 · T-02 — `consultar_catalogo` referencia `{Sustratos tipicos}` (sin tilde); el field real es `Sustratos típicos` (con tilde)

**Tabla afectada:** `Aplicaciones` (tool `consultar_catalogo`).

**Qué está mal.** Airtable trata field names como case-and-diacritics-sensitive. `{Sustratos tipicos}` no matchea `{Sustratos típicos}` → error 422 en el `filterByFormula` de la rama APLICACIONES. Combinado con T-01, la rama nunca produce resultados.

**Evidencia.**

```
sys-tool-consultar-catalogo-v4.json:
  SEARCH("...", LOWER(ARRAYJOIN({Sustratos tipicos})))

00-schema.json, Aplicaciones:
  id=fldmR54uJ1nCWVZpW name="Sustratos típicos" type=multipleSelects
```

**Causa raíz probable.** Copy/paste del schema doc con pérdida de la tilde. Al menos 2 fields con tilde en Aplicaciones (`Aplicación`, `Sustratos típicos`) están escritos sin tilde en el nodo Classify Intent.

**Impacto en el agente.** Mismo que T-01: rama intent=aplicacion muerta.

**Fix propuesto.** Mismo edit que T-01, en el mismo nodo, en la misma pasada. `{Sustratos tipicos}` → `{Sustratos típicos}`. Verificar que el editor de n8n no escape el UTF-8 al guardar.

**Riesgo del fix.** Bajo. Testear con turno "sirvo para vinilo" e inspeccionar el filterByFormula generado (log del nodo Classify Intent).

**Depende de.** —. Va junto con T-01.

---

### P0 · T-03 — `consultar_catalogo` Format Output lee 3 fields de Konica Minolta que NO existen

**Tabla afectada:** `Konica Minolta` (tool `consultar_catalogo`).

**Qué está mal.** El nodo `Format Output` mapea items de inventario Konica leyendo `f['Descripción corta']`, `f['Tipo de Uso']`, `f['Contador de copias']`. Ninguno de esos 3 fields existe en la tabla `Konica Minolta` viva. Los fields reales son `Modelo`, `Marca`, `Tipo`, `Copias Total`, `Copias Negro`, `Copias Color`, `Accesorios`, `Estado`, `Ubicación`, `Stock`, `Precio USD`, `Notas`.

**Evidencia.**

```
sys-tool-consultar-catalogo-v4.json, Format Output:
  descripcion: f['Descripción corta'] || f['Descripcion corta'] || f['Descripción']
  tipo_uso: f['Tipo de Uso']
  contador_copias: f['Contador de copias'] || null

00-schema.json + KonicaMinolta.json:
  fields = ['Modelo','Marca','Tipo','Copias Total','Copias Negro','Copias Color',
            'Accesorios','Estado','Ubicación','Stock','Precio USD','Notas']
  primer record: Modelo=BIZHUB C450i, Tipo=COLOR, Copias Total=233003
```

**Causa raíz probable.** El schema doc v1.1 lista una versión anterior de la tabla con `Contador de copias`, `Tipo de Uso`, `Descripción corta`. La realineación F1 renombró a `Copias Total`, `Tipo`, `Accesorios`. La tool no se actualizó.

**Impacto en el agente.** El item que sube al LLM tiene `descripcion=''`, `tipo_uso=''`, `contador_copias=null`. El contador de copias es LA data clave para justificar precio de refurbished (un BIZHUB C450i con 233 mil copias vs 800 mil vale MUY distinto). El agente no puede diferenciar unidades y responde con specs vacías.

**Fix propuesto.**

```
En Format Output, agregar mapping específico para intent=inventario:
  descripcion: f['Accesorios'] || ''
  tipo_uso: f['Tipo'] || ''
  contador_copias: f['Copias Total'] || null
  copias_negro: f['Copias Negro'] || null
  copias_color: f['Copias Color'] || null
  estado: f['Estado'] || ''
  ubicacion: f['Ubicación'] || ''
  stock: f['Stock'] || 0
  precio_usd: f['Precio USD'] || null

Considerar separar el shape del item por intent (equipo vs inventario) para no
seguir mezclando fields de tablas distintas en la misma estructura.
```

**Riesgo del fix.** Bajo si se hace el mapping por intent. Medio si se hace un merge naïve — el shape del item cambia y el prompt del agente puede tener que ajustar cómo lo lee. Smoke test: consulta "tenés un bizhub usado" y verificar que el output incluye `contador_copias: 233003`.

**Depende de.** — (edit puntual).

---

### P0 · T-05 — singleSelect `Marca` de Equipos tiene `KONIKA` + `MINOLTA` como choices separadas; la tool filtra por `"Konica Minolta"` → 0 records

**Tabla afectada:** `Equipos` (tool `consultar_catalogo`, cualquier búsqueda por marca Konica).

**Qué está mal.** El nodo Classify Intent canoniza a `'Konica Minolta'` (BRAND\_MAP incluye `konica minolta`, `konica`, `minolta`, `bizhub` → `'Konica Minolta'`) y genera `{Marca}="Konica Minolta"`. Pero el singleSelect `Equipos.Marca` no tiene esa opción — tiene `KONIKA` (typo) y `MINOLTA` como dos choices separadas, más `SINAJET`/`Sinajet` duplicadas y `Marca`/`Otro` como choices basura.

**Evidencia.**

```
sys-tool-consultar-catalogo-v4.json, Classify Intent:
  BRAND_MAP: {'konica minolta':'Konica Minolta', 'konica':'Konica Minolta',
              'minolta':'Konica Minolta', 'bizhub':'Konica Minolta', ...}
  F_marca = (m) => `{Marca}="${esc(m)}"`

00-schema.json, Equipos.Marca (fld2ZeRByZdUGeWXf) options:
  ['HUENU','XENONS','DLICAN','HANRUN','TENETH','SINAJET','RISO',
   'KONIKA','MINOLTA','Otro','Marca','Sinajet']
```

**Causa raíz probable.** Import CSV creó choices por cada valor único encontrado (mayúsculas y con typo). Nunca se limpió post-import.

**Impacto en el agente.** Lead que dice "busco impresora Konica" o "quiero bizhub" con solo marca (sin modelo hint) → filter `{Marca}="Konica Minolta"` devuelve 0 en Equipos. La rama de inventario (tabla `Konica Minolta`) sí funciona porque la tool tiene un path aparte para intent=inventario, pero si el LLM pasa por la rama de equipos nuevos, silencio.

**Fix propuesto — 2 pasos coordinados, en la misma ventana.**

```bash
# PASO 1 — Consolidar choices del singleSelect Marca en Airtable UI (o via API meta)
# Meta patchable via https://api.airtable.com/v0/meta/bases/{baseId}/tables/{tableId}/fields/{fieldId}
# Payload deja solo: ['HUENU','XENONS','DLICAN','HANRUN','TENETH','SINAJET','RISO','KONICA MINOLTA','Otro']
# ANTES: bulk update de records con Marca='KONIKA' o 'MINOLTA' → 'KONICA MINOLTA'
#         y 'Sinajet' → 'SINAJET'. Chequear que no quedan records con Marca='Marca' (garbage).
# DRY-RUN — armar payload y revisar

# PASO 2 — Sincronizar BRAND_MAP en Classify Intent (nodo Code JS del sub-workflow)
# BRAND_MAP: {'konica minolta':'KONICA MINOLTA', 'konica':'KONICA MINOLTA', ...}
```

**Riesgo del fix.** Alto si se aplica solo uno de los 2 pasos. Si se cambia el singleSelect antes que la tool, todos los records de Konica quedan huérfanos hasta el bulk update. Si se cambia la tool antes que el singleSelect, la tool sigue devolviendo 0. Deben ir juntos, con el paso 1 dividido en (a) crear la choice `KONICA MINOLTA` primero, (b) migrar records, (c) borrar `KONIKA` y `MINOLTA` sueltas. La choice `Sinajet` (case duplicada de `SINAJET`) tiene el mismo problema en menor escala.

**Depende de.** Nada. Puede ir junto con T-06 (mismo patrón sobre `Formato`).

---

### P0 · T-06 — singleSelect `Formato` de Equipos tiene `Cilindrica` (sin tilde) y duplicados MESA/PLOTTER/PLIEGO; la tool canoniza a `Cilíndrica`

**Tabla afectada:** `Equipos` (tool `consultar_catalogo`).

**Qué está mal.** FORMAT\_MAP en Classify Intent emite `'Cilíndrica'` (con tilde) — el choice en Airtable es `Cilindrica` (sin tilde). Además el singleSelect tiene 3 duplicados case (`Mesa`+`MESA`, `Plotter`+`PLOTTER`, `Pliego`+`PLIEGO`) y el header basura `Formato`. Distribución real: Mesa=12 + MESA=6, Plotter=7 + PLOTTER=3, Pliego=0 + PLIEGO=1.

**Evidencia.**

```
sys-tool-consultar-catalogo-v4.json:
  FORMAT_MAP: {'cilindrica':'Cilíndrica', ...}

00-schema.json, Equipos.Formato (fldyFL1nkyRsfpNzk) options:
  ['Rollo a Rollo','Cama Plana','Híbrido','Mesa','Plotter','Cilindrica','Pliego',
   'Bobina','Compacta','Horno','Purificador','Plancha','Formato','MESA','PLOTTER','PLIEGO']
```

**Impacto en el agente.** (a) Lead "impresora cilíndrica" → 0 records (baja prevalencia, pero 100% de miss cuando pasa). (b) Filtros por Formato con `{Formato}=Mesa` no matchean los 6 records con `MESA` (variante del case). Bug latente: cada nuevo equipo cargado con MESA/PLOTTER/PLIEGO se queda invisible para la rama de formato.

**Fix propuesto.**

```bash
# PASO 1 — Bulk edit en Airtable: migrar los 10 records afectados
#   MESA (6 records: FC7090U, FC5070E, HM 3001 DU, FC9012, FC1313U, FC7090A) → Mesa
#   PLOTTER (3 records: TN48CCD, TN59CCD, TN24CCD) → Plotter
#   PLIEGO (1 record: L6 HK PRO) → Pliego

# PASO 2 — Borrar las 4 choices garbage del singleSelect Formato
#   Formato (header), MESA, PLOTTER, PLIEGO

# PASO 3 — Ajustar FORMAT_MAP: 'cilindrica' → 'Cilindrica' (sin tilde) para matchear la choice real
# DRY-RUN — coordinar los 3 pasos en la misma ventana
```

**Riesgo del fix.** Bajo si se hace en orden. La choice `Cilindrica` sin tilde es la fuente de verdad; si Edgardo prefiere agregar la tilde, hacerlo primero y después migrar el único record afectado. Consultar con Edgardo si `Cama Plana` y `Mesa` significan lo mismo (candidato a merge también) — no está claro.

**Depende de.** —.

---

### P0 · SD-11 — Config Mensual `Líneas priorizadas` documentada como Link → en live es `multilineText`. La tool `consultar_lineas_priorizadas` está LIVE.

**Tabla afectada:** `Config Mensual` (tool `consultar_lineas_priorizadas`).

**Qué está mal.** El schema doc §Tabla 11 declara `Líneas priorizadas | Link to Líneas de Producto | Multi`. En la base viva el field `fldIBxEkQ0HbivJQj` es `multilineText`. La tool `consultar_lineas_priorizadas` es una de las 8 tools live y probablemente espera el shape de un linked-record (array de IDs o de primary values), no una string.

**Evidencia.**

```
00-schema.json, ConfigMensual.'Líneas priorizadas': type=multilineText
schema doc v1.1 §Tabla 11: type=Link to Líneas de Producto | Multi
ConfigMensual.json: 1 record {Mes: '2026-05'}
```

**Impacto en el agente.** Riesgo de rotura silenciosa. Si el sub-workflow `sys-tool-consultar-lineas-priorizadas-v1.json` procesa el field como array de linked records y hoy recibe una string, el output al agente es distinto al esperado por el prompt. La tabla tiene 1 solo record (`2026-05`) — puede estar vacío el field y el bug ser latente, no activo. Si el cliente activa el flow de líneas priorizadas y carga el field como texto, el agente puede alucinar o cortar.

**Fix propuesto.**

```
1. Abrir sys-tool-consultar-lineas-priorizadas-v1.json en n8n y confirmar qué espera:
   - Si espera link (array de records): migrar el field a multipleRecordLinks apuntando a Líneas de Producto
   - Si maneja texto libre: actualizar schema doc y prompt del agente
2. Verificar con Edgardo si Config Mensual está siendo usada. Si está vacía, el bug es
   latente y se puede fixear tranquilo.
```

**Riesgo del fix.** Migrar de multilineText a multipleRecordLinks requiere crear un field nuevo, migrar valores matcheando strings contra primary de Líneas de Producto, borrar el field viejo, renombrar. Cirugía cuidadosa. Alternativa: dejar como multilineText y ajustar el sub-workflow a parsear texto separado por comas. Decidir con Edgardo cuál es más simple de mantener.

**Depende de.** Inspección previa del sub-workflow (no adjunto en este set).

---

## 3. Findings P1 (degradan respuestas o confunden a Edgardo)

### P1 · S-02 — 19 Equipos (21%) sin Marca ni Tecnología cargadas (series DF/DG/DH)

**Evidencia.** 19 records con `Marca` y `Tecnología` ausentes simultáneamente. IDs y modelos: DH 3021, DG 2513F, DF 1007-MT, DF 0906-MT, DF 0912-MT, DG 2516, DH 1816, DG 2513, DH 1816F, DG 1513F, DF 0906, DG 2518, DF 1216-MT, DF 0604, DH 2521, DH 3321, DH 1216, DG 1513, DF 0604-MT. Distribución Formato: 12 Mesa, 7 Plotter. **Hipótesis:** son TENETH por convención de series. **Fix:** confirmar con Edgardo, PATCH batch a los 19 IDs seteando `Marca='TENETH'` y `Tecnología` según modelo (probable Corte).

**Impacto en el agente.** `consultar_catalogo` devuelve estos equipos con `marca=''` y `tecnologia=null`; el agente responde specs incompletas.

### P1 · S-03 — 91 de 92 Equipos con `Descripción corta` vacía o <50 chars

**Evidencia.** 68 records con string vacío/null + 23 con 1-49 chars. Ejemplos: FC7090U (0), X4E-7703 (0), HR 6004 DU (0), CC-3110 (41), DH 3021 (30). **Fix:** Edgardo completa manualmente (~3-4h de trabajo). Punto explícito en la guía operativa.

**Impacto en el agente.** Descripción corta es LO que el LLM usa para responder features/aplicaciones al lead. Respuestas mudas o genéricas.

### P1 · S-04 — 0 links Equipos → Aplicaciones (par vacío en ambas direcciones)

**Evidencia.** `Equipos.Aplicaciones compatibles` = 0 links en los 92 records. `Aplicaciones.Equipos` = 0 links en los 20 records. Los links Equipos↔Tecnología (73) y Equipos↔Línea de Producto (76) sí están cargados. **Fix:** regenerar con script derivando de Tecnologías (para cada Equipo, para cada Aplicación que tenga la Tecnología del Equipo en su campo `Tecnologías recomendadas`, crear link). Ejecutable en una sola pasada Python + PATCH batch.

**Impacto en el agente.** Lead "¿qué equipo sirve para banners?" → intent=aplicacion busca Aplicación y ve `Equipos=[]` → NOT\_FOUND. Combinado con T-01/T-02, la rama intent=aplicacion está doblemente rota (field name incorrecto + data vacía).

### P1 · S-05 — Link Tecnologías ↔ Sustratos vacío en ambas direcciones

**Evidencia.** 0 links en las 10 tecnologías y en los 53 sustratos (incluyendo los 16 reales). **Fix:** bloqueado por cleanup de Sustratos (S-01). Post-cleanup, Edgardo linkea manualmente en 30 min.

**Impacto en el agente.** No consultado directo por `consultar_catalogo` hoy. Sí bloquea la respuesta cruzada "qué tecnologías soportan sustrato X".

### P1 · S-06 — Link Líneas de Producto ↔ Representantes vacío en ambas direcciones

**Evidencia.** 0 links / 10 líneas / 1 rep. Consistente con decisión Opción A del 2026-05-28 (CRM pausado). **Fix:** no urgente hasta reactivar upsell CRM. Documentar en guía como "preparado, no usado".

**Impacto en el agente.** `notificar_lead` no consulta esta relación (hoy manda a mail genérico). Sin impacto en tool viva.

### P1 · SD-01 — Tabla `Leads` documentada pero NO existe en la base viva

**Evidencia.** Doc §Tabla 10 lista Leads con 20 fields. Snapshot 00-schema.json enumera 11 tablas sin Leads. CLAUDE.md dice "Tabla Airtable Leads creada pero sin uso productivo" — contradice el schema real. **Fix:** confirmar con la agencia si Leads existió y fue borrada, o si nunca se creó. Actualizar schema doc para marcar como PAUSADA. Alternativa: crear tabla vacía con schema documentado para tenerla lista al reactivar upsell.

**Impacto en el agente.** Ninguno (notificar\_lead no escribe a Airtable). Impacto sobre Edgardo: si abre el doc y ve 12 tablas, no encuentra la 12ª.

### P1 · SD-02 — Equipos.`Notas internas` documentado como Long text; en vivo es `singleSelect` roto con 4 choices basura

**Evidencia.** Choices en vivo: `'Stub creado en F1. Pendiente confirmar modelo exacto con Edgardo.'`, `'Stub F1.'`, `'Notas internas'`, `'Stock disponible: 1 unidad/es'`. Ninguna es una opción real — son valores congelados como choices por import mal configurado. **Fix:** convertir field a multilineText (requiere crear field nuevo, migrar, borrar viejo, renombrar). API endpoint: `PATCH https://api.airtable.com/v0/meta/bases/appMD3g2HWxzBaZAM/tables/tblHO7kWEbFBVTWQn/fields/fldJWUkPCC2G3q3s1` con `{"type":"multilineText"}` — Airtable puede no permitir cambio de tipo directo si hay datos; fallback = field nuevo.

**Impacto en el agente.** El agente no lee este field (por doc). Impacto operativo alto: Edgardo no puede escribir notas libres, solo elegir entre 4 opciones absurdas.

### P1 · SD-03 — Equipos.`Cabezales` documentado como Link a Cabezales; en vivo son 3 fields escalares (`Cabezales hasta`, `Cabezales incluidos`, `Cabezales tipo`)

**Evidencia.** Doc §Tabla 1 línea 72 declara Link. Live no tiene multipleRecordLinks a tblroOlVU3m99DtmF. Los 3 escalares están documentados en el changelog v1.1 pero no en la sección de fields del schema. **Fix:** reescribir §Tabla 1 del schema para reflejar la realidad; eliminar la fila del Link; documentar los 3 escalares. Opcional: agregar el Link en adición si el cliente lo pide para vistas cruzadas.

**Impacto en el agente.** `consultar_catalogo` ya lee los 3 escalares — tool funciona. Impacto sobre Edgardo: espera Link, no lo encuentra. Perdida capacidad de query cruzada Cabezales→Equipos.

### P1 · SD-04 — Marca de Equipos con `KONIKA`/`MINOLTA`/`Marca`/`Sinajet` como choices basura

Ver P0 T-05. Se lista acá como P1 desde la dimensión "schema vs doc" porque el schema doc lista `HUENU, DLICAN, TENETH, HANRUN, XENONS, RISO, Sinajet, Konica Minolta, Otro`. La divergencia va junto con el fix de T-05.

### P1 · SD-05 — Formato de Equipos con `Formato`/`MESA`/`PLOTTER`/`PLIEGO` choices basura + duplicados case

Ver P0 T-06. Junto con el fix de T-06.

### P1 · SD-06 — Cabezales.`Equipos compatibles` documentado como Link; NO existe en live

**Evidencia.** Doc §Tabla 6 línea 262. Live no tiene el link. Consistente con SD-03. **Fix:** actualizar doc a la realidad (escalares) o crear el link para habilitar consultas cruzadas.

**Impacto en el agente.** Sin impacto en tool viva.

### P1 · SD-08 — Aplicaciones.`Sustratos típicos` documentado como Link a Sustratos; en vivo es `multipleSelects` con 13 choices hardcoded

**Evidencia.** Live fldmR54uJ1nCWVZpW = multipleSelects. Choices: Algodón, Poliéster, Nylon, Lycra, Cerámica, Metal, Vidrio, PVC espumado, Acrílico, Vinilo, Lona, Cartulina, Papel común. Faltan 3 canónicos (Denim, Cuero sintético, Madera). **Fix:** migrar a multipleRecordLinks apuntando a tblV7lQ9eT0gIUu9b una vez limpia la tabla Sustratos (post S-01).

**Impacto en el agente.** Sin impacto directo (consultar\_catalogo no usa la relación cruzada). Sí rompe fuente única de verdad de sustratos y drift-ea con la tabla Sustratos.

### P1 · SD-09 — Insumos.Categoría documentada con 6 choices (Tinta, Film DTF, Polvo DTF, Vinilo, Papel transfer, Otros); live tiene 3 (TINTAS, FILM, POLVO)

**Evidencia.** Divergencia case + falta de choices. Changelog v1.1 dice "Categorías reales: TINTAS, FILM, POLVO" pero la sección de fields nunca se actualizó. **Fix:** actualizar §Tabla 7 al estado real. Si el cliente agrega Vinilo/Papel transfer en el futuro, agregar choice via API.

**Impacto en el agente.** Si el prompt describe 6 categorías al LLM y hay 3, el LLM puede pasar filterByFormula con `Vinilo` que devuelve NOT\_FOUND.

### P1 · SD-10 — FAQs.Categoría documentada como singleSelect con 9 choices; en vivo es multilineText

**Evidencia.** Live fld3G3ivn10HdtyC7 = multilineText. Doc §Tabla 8 lista 9 choices. Vista "Por categoría" agrupa texto libre — funciona pero desordena.

**Fix:** migrar a singleSelect con las 9 choices documentadas. Normalizar valores actuales antes.

**Impacto en el agente.** `consultar_catalogo` filtra con FIND en texto — funciona. Pierde consistencia (Edgardo puede escribir `ServTec` vs `Servicio Técnico`).

### P1 · SD-12 — Representantes.`Líneas asignadas` documentado como Link; en vivo hay DOS fields con nombres similares (uno multipleSelects roto, otro Link real)

**Evidencia.** `Líneas asignadas` (fldKn0Iin39Ir8sjX) = multipleSelects con 13 choices basura incluyendo Mimaki, Roland, `Líneas asignadas`. `Líneas de Producto` (fldbBV7i4mxhVc7qj) = link real a tblkwadqLX3slj4JY. **Fix:** decidir con Edgardo cuál mantener; migrar records; borrar el otro. Actualizar filterByFormula del doc §Tabla 9 al nombre correcto.

**Impacto en el agente.** notificar\_lead no consulta hoy. Impacto sobre roadmap Opción B (rep-especialización) si se reactiva.

### P1 · V-01 — 6 tablas leídas por tools SIN filtro de vista

**Evidencia.** Los tools `sys-tool-consultar-aplicacion-v2`, `sys-tool-consultar-catalogo-v4` (nodos Aplicaciones + Inventario Konica), `sys-tool-consultar-inventario-usados-v1`, `sys-tool-consultar-lineas-priorizadas-v1`, `sys-tool-consultar-url-tienda-v2` leen las tablas base con `view=None`. Las vistas "Para agente" ya existen en Cabezales (`viwxsJKBiAS7FFybS`), Insumos (`viwM6RjuUufxZMuI6`), Konica Minolta (`viwKrFyMCZqQynwKF`) — están cargadas pero no cableadas. **Fix:** setear `view=<id>` en cada Airtable node afectado. Para Aplicaciones y Sustratos crear la vista primero (V-02, V-03).

**Impacto en el agente.** Si Edgardo carga un cabezal en Status="En prueba" (por ejemplo), el agente lo va a devolver como vigente. Silencioso.

### P1 · V-02 — Falta vista "Para agente / activas" en Aplicaciones

**Evidencia.** Live solo tiene "Grid view". Sin vista filtrada no hay dónde apuntar el tool (aunque quisiéramos). **Fix:** Edgardo la crea en la reunión (filter `{Status}='Activo'` — verificar que el field Status existe en Aplicaciones o crearlo). Luego cablear los tools.

### P1 · V-03 — Falta vista "Para agente / activos" en Sustratos + tabla contaminada

**Evidencia.** Live solo "Grid view". Bloqueado por S-01. **Fix:** post-cleanup de Sustratos, crear la vista con filter `{Status}='Activo'`.

### P1 · V-05 — No pudimos verificar los filtros internos de las vistas críticas

**Evidencia.** La API meta pública devuelve `{id, name, type}` sin los filtros. Riesgo: alguien puede haber editado el filtro de "Para agente" y expuesto records WIP al agente. **Fix:** confirmar visualmente en la reunión con Edgardo abriendo cada una de las 4 vistas críticas (Equipos/Para agente, FAQs/Por categoría, Tecnologías/Activas, Representantes/Activos) y guardando screenshot en `05_crm/vistas-verificadas-2026-07-01.md`. Sugerencia preventiva: lock views (plan Team+).

---

## 4. P2 (cosmético y drift menor)

Tabla compacta. Fixes trivial, sin impacto en agente hoy.

| # | Tabla | Qué está mal | Fix |
|---|---|---|---|
| P2-01 | Konica Minolta | Record fantasma `Alquiler de equipos` guarda un system prompt en `Notas`. 2 duplicados de `BIZHUB C450i` (rec1EkBKf7iEwBKSU, rec8D0S2GvhB1syo8) sin diferenciador. | Borrar el pseudo-record, migrar prompt fuera. Preguntar a Edgardo si los 2 BIZHUB son unidades distintas (agregar `Serie`/`ID interno`) o duplicado. |
| P2-02 | Insumos | 6 records con primary `SOFT`×3 + `RIGID/ SOFT`×3, todos con mismos Marca+Tipo, sin diferenciador. | Borrar 4 (dejar 1 por grupo) o completar con nombre real. |
| P2-03 | Equipos | 2 records con Modelo `UV 6004` HANRUN (recJgg9eNvAa00EtU 20400 / recvHgKC1qkxUK8Z9 18050). | Preguntar a Edgardo cuál precio es correcto; borrar el otro. |
| P2-04 | Representantes | Único record `Equipo Comercial` — placeholder de la Opción A. | No es bug. Documentar en schema para que futuros auditores no lo levanten. |
| P2-05 | Sustratos, Aplicaciones, Líneas de Producto | Fields reverse con nombre genérico (`Equipos`, `Líneas de Producto`) sin contexto. | Renombrar en UI a `Equipos que lo imprimen` / `Modelos de la línea` / `Líneas que atiende`. Trivial. |
| P2-06 | Cabezales | Record DX5 (recdABp7Tkz11JBLw) con Gama, Cabezal familia y Perfil de Usuario vacíos. Los otros 9 completos. | Preguntar a Edgardo si mantener DX5 (poner "Económica"/"DX5"/"Legacy") o borrar. |
| P2-07 | Tecnologías | IDL Láser y Gran Formato con 0 Equipos linkeados. | Confirmar si Gran Formato es tecnología o solo formato transversal. Linkear IDL Láser a los 5 RISO. |
| P2-08 | Líneas de Producto | 1 línea sin Equipos linkeados. | Verificar cuál y decidir con Edgardo. |
| P2-09 | Todos los pares linked | Asimetría de naming en 5 de 7 pares reverse. | Documentar mapa en la guía; NO renombrar sin actualizar tool en paralelo. |
| P2-10 | Equipos | Choices `Status` sin `Discontinuado` + garbage `Status`. | Agregar choice + borrar garbage. Vista "Discontinuados" no puede existir sin la choice. |
| P2-11 | Konica Minolta | 22 records (doc dice 21). | Actualizar schema doc. |
| P2-12 | Cabezales | Choice `Tipo` solo tiene `Original`; faltan `Compatible`, `Repuesto`. | Agregar choices via API. Trivial. |
| P2-13 | Cabezales | `URL tienda` como multilineText (doc dice URL); `Stock disponible` como multilineText (doc dice Checkbox). | Cambiar tipos. Normalizar datos existentes. |
| P2-14 | Tecnologías | `Línea principal` documentada como singleSelect con 8 choices; en vivo es multilineText. | Migrar a singleSelect. |
| P2-15 | Aplicaciones | Falta field `Notas para asesoramiento` documentado. `Keywords cliente` es multipleSelects con 52 tags (doc dice Long text). Falta choice `Otros` en `Categoría`. | Agregar/reconvertir según decisión Edgardo. |
| P2-16 | Líneas de Producto | Choice `Tipo` sin `Genérico`. | Agregar. Trivial. |
| P2-17 | FAQs | Choice `Status` = `Activo`/`Desactivo` (typo); doc dice `Activo`/`Revisión`/`Archivado`. `Keywords` como multipleSelects con 47 tags (doc dice Long text). Una FAQ sin signo `?`. | Decidir con Edgardo; alinear a doc por trazabilidad (recomendado). |
| P2-18 | Representantes | `Backup` field documentado (Link a Representantes) NO existe. `Mail`/`Teléfono`/`Mail Gerente (copia)` como multilineText (doc dice Email/Phone). | Crear campos, cambiar tipos. Feature Opción B pendiente. |
| P2-19 | Aplicaciones | Categoría sin `Otros`. | Agregar choice si Edgardo lo pide. |
| P2-20 | Todas las tablas | Primary field como `multilineText` en vez de `singleLineText` (11/11). | Cosmético; migrar si se hace pasada de limpieza. |
| P2-21 | Cabezales, Insumos, Konica Minolta | Fields varios (`Precio USD`, `Descripción`, `Fecha última actualización`, etc.) documentados pero con nombres distintos o ausentes. | Actualizar schema doc. |
| P2-22 | Sustratos | Sustratos legítimos (los 16) con `Descripción` vacía. | Poblar. Trivial. |
| P2-23 | Vistas | Tecnologías falta vista `Por línea` y `Activas para agente` según doc. | Consolidar doc o crear vistas. Sin urgencia. |
| P2-24 | Vistas | Equipos falta vista `Discontinuados`. | Crear (después de agregar la choice Status=Discontinuado). |
| P2-25 | Vistas | Representantes.`Activos` existe pero no consumida por ninguna tool. | Marcar en guía como preparada para Opción B. |
| P2-26 | Tecnologías | Nombre de la vista `Activas` vs `Activas para agente` del doc. | Alinear doc a la realidad. |
| P2-27 | Equipos, todas | Choices garbage por header de CSV en 5 fields (`Marca`, `Formato`, `Disponibilidad zona`, `Status`, `Notas internas`). | Borrar en la misma pasada que T-05/T-06/SD-02. |
| P2-28 | Aplicaciones | Field `Notas para asesoramiento` no existe. | Confirmar con Edgardo si lo quiere. |
| P2-29 | FAQs | Vista "Por categoría" agrupa por texto libre. | Migrar Categoría a singleSelect (SD-10) y la vista se ordena sola. |
| P2-30 | Representantes | `Backup` field NO existe. | Actualizar doc o crear campo. |
| P2-31 | Aplicaciones | 3 sustratos canónicos faltantes en `Sustratos típicos` (Denim, Cuero sintético, Madera). | Se resuelve al migrar a Link (SD-08). |
| P2-32 | Todas las tablas | Vistas críticas sin lock (cualquier editor puede cambiar filtros silente). | Sugerir lock views en plan Team+. |
| P2-33 | Sustratos | Sustratos legítimos con `Tipo` incompleto. | Poblar. |
| P2-34 | Equipos | `Especificaciones técnicas` y `Imagen principal` documentados; NO existen. | Actualizar doc. Imagen principal era "Reservada v2.1". |
| P2-35 | Insumos | Link `Equipos compatibles` documentado; NO existe. `Stock disponible` (checkbox doc) NO existe (hay `Cantidad ML/G` number). | Actualizar §Tabla 7 al schema real. |
| P2-36 | Config Mensual | Es OK como tabla; solo 1 record. Config Mensual + tool consultar\_lineas\_priorizadas ver P0 SD-11 para la parte crítica. | — |
| P2-37 | Sustratos, Todas | Primary field multilineText permite line breaks en primary (riesgo cosmético en displays de linked records). | Migrar a singleLineText si se hace pasada de limpieza. |
| P2-38 | Representantes | Rename cosmético del reverse `Líneas de Producto` → `Líneas que atiende`. | Trivial UI. |
| P2-39 | Equipos, todas | Naming inconsistente en pares reverse (Sustratos.Equipos vs Equipos.Sustratos compatibles, etc.). | Documentar mapa; no renombrar sin ajustar tool. |

---

## 5. Preguntas para Edgardo en la reunión

Decisiones que solo él puede tomar. Llevalas escritas para no perder tiempo.

1. **Sustratos basura (37 records numéricos).** ¿Los borramos o los recuperamos como "anchos válidos" en una tabla aparte (nueva tabla `Anchos` o un field `Ancho aceptado` en Sustratos reales)? Nuestra recomendación: borrar. Los anchos ya viven en `Equipos.Ancho`.
2. **`A3` y `A4` en Sustratos.** ¿Son papeles legítimos que hay que renombrar (`Papel A3`, `Papel A4`) o basura del import? Recomendación: renombrar y linkear a Equipos que trabajen esos formatos.
3. **Series DF/DG/DH sin Marca.** ¿Son todos TENETH? ¿Qué Tecnología va con cada uno (Corte, otro)?
4. **Konica Minolta.** El registro `Alquiler de equipos` con prompt en `Notas` — ¿lo movemos afuera y borramos el record? ¿Los 2 BIZHUB C450i (rec1EkBKf7iEwBKSU, rec8D0S2GvhB1syo8) son 2 unidades físicas o duplicado?
5. **Equipo `UV 6004` HANRUN duplicado con 2 precios (20400 vs 18050).** ¿Cuál es correcto? ¿Borramos el otro?
6. **6 records `SOFT`/`RIGID SOFT` en Insumos** — ¿son duplicados de la misma tinta o insumos distintos que quedaron sin diferenciador? ¿Los borramos o los completamos?
7. **`Aplicaciones.Equipos` (par de link vacío).** ¿Podés completar el mapeo aplicación↔equipo desde el Excel original? Alternativa: derivamos automáticamente por Tecnología.
8. **Representantes.** ¿Sigue vigente Opción A (sin especialización) o querés arrancar a mapear reps por línea de producto? ¿Sumamos reps individuales (hoy hay 1 record `Equipo Comercial`)?
9. **Choices duplicados MESA/PLOTTER/PLIEGO + KONIKA/MINOLTA/Sinajet.** OK a consolidar (migrar records + eliminar duplicados)?
10. **`Notas internas` como singleSelect roto.** OK a migrar a texto libre?
11. **`Cilíndrica` vs `Cilindrica` (sin tilde).** ¿Cuál preferís? El único record afectado se migra.
12. **Tabla `Leads`.** ¿La creamos vacía ahora para tenerla lista si reactivás CRM, o la dejamos afuera y la creamos cuando activemos el upsell?
13. **Vista `Discontinuados` en Equipos.** ¿La usás o no la necesitás? (Requiere agregar la choice `Discontinuado` al singleSelect `Status`.)
14. **`Descripción corta` vacía en 91 equipos.** ¿Podés completarla vos manualmente (~3-4h) o preferís que armemos un template y las cargues por batch?

---

## 6. Plan de fixes recomendado

Orden y tiempo estimado. Cada fase termina con smoke test antes de pasar a la siguiente.

**Fase 0 — Backup (10 min).** `curl` de las 11 tablas + copia de los 2 sub-workflows críticos (`consultar-catalogo-v4`, `consultar-lineas-priorizadas`). Guardar en `/tmp/airtable-backup-2026-07-01/`.

**Fase 1 — P0 Sustratos (2-3 h).**
1. Vaciar los 77 links `Equipos.Sustratos compatibles`.
2. Borrar los 37 records basura de Sustratos.
3. Confirmar en Airtable que quedan los 16 legítimos.
4. Repoblar links usando la matriz Tecnología×Sustrato del CSV original (Edgardo asiste). [PENDIENTE]
5. Smoke test: consulta al webhook "¿la HR 6004 UV imprime sobre vinilo?" y verificar que el output tiene "vinilo" no "166". [PENDIENTE]

**Fase 2 — P0 Tools rotos (30 min).**
1. Edit `sys-tool-consultar-catalogo-v4.json`: fixes T-01 (`{Nombre}` → `{Aplicación}`), T-02 (`{Sustratos tipicos}` → `{Sustratos típicos}`), T-03 (mapping específico intent=inventario con `Copias Total`, `Tipo`, `Accesorios`).
2. Re-export como v5, preservar workflowId, import in-place.
3. Smoke: 3 turnos — "quiero imprimir remeras" (rama aplicación), "tenés un bizhub usado" (rama inventario), "impresora vinilo" (rama sustrato).

**Fase 3 — P0 Marca/Formato consolidados (1 h).**
1. Bulk update de Equipos con Marca=`KONIKA`/`MINOLTA` → `KONICA MINOLTA`; `Sinajet` → `SINAJET`; Formato `MESA`/`PLOTTER`/`PLIEGO` → `Mesa`/`Plotter`/`Pliego`.
2. Editar el singleSelect vía API meta: dejar solo choices canónicas.
3. Actualizar BRAND\_MAP y FORMAT\_MAP en Classify Intent.
4. Smoke: "quiero konica minolta", "impresora mesa", "cilíndrica".

**Fase 4 — P0 Config Mensual (variable).**
1. Inspeccionar sub-workflow `consultar-lineas-priorizadas` (no adjunto en este set).
2. Decidir link vs texto libre con Edgardo.
3. Aplicar según decisión.

**Fase 5 — P1 tools sin vista (30 min).**
1. Cablear `view=<id>` en los nodos afectados (finding V-01). Aplicaciones y Sustratos requieren crear la vista primero (V-02, V-03).

**Fase 6 — P1 data completeness (Edgardo, ~5 h asincrónicas).**
1. Completar 19 Equipos DF/DG/DH con Marca/Tecnología.
2. Completar 91 `Descripción corta`.
3. Poblar links `Equipos.Aplicaciones compatibles` (script derivador).

**Fase 7 — P2 cleanup cosmético (2 h).** Duplicados, choices garbage sobrantes, renames de reverse, vista `Discontinuados`, ajustes de schema doc. Todo lo de la tabla P2.

**Fase 8 — Guía operativa para Edgardo (1 h).** Doc separado con: cómo agregar un equipo, cómo agregar una FAQ, cómo mover a "Para agente", mapa de reverse links, checklist de campos obligatorios.

Total estimado con Edgardo colaborando: ~1 día calendario para Fase 0-3 + Fase 5 (bloqueantes), asincrónico Fase 6, ~2 semanas más para Fase 7-8.

---

## Anexo A — Schema documentado vs base viva (11 tablas)

| Tabla | Cambios detectados |
|---|---|
| **Tecnologías** | ✅ Casi al día. `Línea principal` es multilineText (doc: singleSelect 8 choices). Vista `Por línea` falta. |
| **Equipos** | ❌ `Cabezales` (doc: Link) → 3 escalares. `Notas internas` (doc: Long text) → singleSelect roto. `Especificaciones técnicas` + `Imagen principal` documentados, NO existen. `Velocidad (m²/h)` NO existe (tool lo lee). Choices garbage en Marca/Formato/Status/Notas internas/Disponibilidad zona (KONIKA, MINOLTA, MESA duplicado, PLOTTER duplicado, etc.). Vista `Discontinuados` falta. |
| **Líneas de Producto** | ⚠️ Choice `Tipo` sin `Genérico`. 1 línea sin equipos linkeados. |
| **Aplicaciones** | ❌ `Sustratos típicos` (doc: Link) → multipleSelects con 13 choices hardcoded, faltan 3 canónicos. `Keywords cliente` (doc: Long text) → multipleSelects con 52 tags. `Notas para asesoramiento` documentado, NO existe. Categoría sin choice `Otros`. Field `Nombre` documentado por tool, primary real es `Aplicación`. Vista `Para agente` falta. |
| **Sustratos** | ❌❌ 37/53 records basura (P0). Primary field multilineText (doc: singleLineText). Vista `Para agente` falta. Descripciones vacías. |
| **Cabezales** | ⚠️ `Equipos compatibles` (doc: Link) NO existe. `Tipo` sin choices `Compatible`/`Repuesto`. `URL tienda` (doc: URL) → multilineText. `Stock disponible` (doc: Checkbox) → multilineText. Record DX5 con Gama/Familia/Perfil vacíos. |
| **Insumos** | ❌ 6 records duplicados basura (SOFT×3 + RIGID SOFT×3). `Categoría` con 3 choices reales (TINTAS/FILM/POLVO) vs 6 documentados. `Equipos compatibles` (doc: Link) NO existe. `Stock disponible` (doc: Checkbox) NO existe (hay `Cantidad ML/G` number). |
| **Konica Minolta** | ⚠️ 22 records (doc: 21). Record fantasma `Alquiler de equipos` con prompt. 2 BIZHUB C450i duplicados. Tool lee 3 fields que no existen (P0 T-03). |
| **FAQs** | ⚠️ `Categoría` (doc: singleSelect 9 choices) → multilineText. `Keywords` (doc: Long text) → multipleSelects 47 tags. `Status` = `Activo`/`Desactivo` (typo) en vez de 3 estados documentados. |
| **Representantes** | ⚠️ `Líneas asignadas` (doc: Link) → multipleSelects roto + hay OTRO field `Líneas de Producto` que sí es link (dos fields confusos). `Backup` documentado, NO existe. `Mail`/`Teléfono`/`Mail Gerente` como texto libre en vez de tipos validados. `Activos` vista existe pero no consumida (Opción A). |
| **Config Mensual** | ❌ `Líneas priorizadas` (doc: Link multi) → multilineText. Tool `consultar_lineas_priorizadas` LIVE (P0 SD-11). |
| **Leads** | ❌ Documentada pero NO existe (P1 SD-01). |

Leyenda: ✅ OK · ⚠️ drift menor · ❌ bug bloqueante o divergencia mayor.

---

## Anexo B — Contrato tool ↔ Airtable

Matriz "tool X lee field Y de tabla Z; estado ok/roto".

| Tool | Tabla | Field(s) que lee | Estado |
|---|---|---|---|
| `consultar_catalogo` (Classify Intent) | Aplicaciones | `{Nombre}` | ❌ ROTO — field no existe (P0 T-01) |
| `consultar_catalogo` (Classify Intent) | Aplicaciones | `{Sustratos tipicos}` | ❌ ROTO — falta tilde (P0 T-02) |
| `consultar_catalogo` (Classify Intent) | Equipos | `{Marca}="Konica Minolta"` | ❌ ROTO — choice no existe (P0 T-05) |
| `consultar_catalogo` (Classify Intent) | Equipos | `{Formato}="Cilíndrica"` | ❌ ROTO — choice sin tilde (P0 T-06) |
| `consultar_catalogo` (Classify Intent) | Equipos | `{Modelo}`, otros filtros | ✅ OK (con reservas por MESA/PLOTTER dupes) |
| `consultar_catalogo` (Format Output) | Equipos | `Modelo`, `Marca`, `Tecnología`, `Formato`, `Línea de Producto`, `Ancho`, `Descripción corta`, `Aplicaciones compatibles`, `Sustratos compatibles`, `Cabezales incluidos`, `Cabezales tipo`, `Datos extra`, `Tipo de Uso`, `Disponibilidad zona` | ⚠️ Sustratos compatibles devuelve basura (P0 S-01); `Aplicaciones compatibles` vacío (P1 S-04); Descripción corta vacía (P1 S-03) |
| `consultar_catalogo` (Format Output) | Equipos | `Velocidad (m²/h)` | ❌ ROTO — field no existe (P1 T-04) |
| `consultar_catalogo` (Format Output) | Konica Minolta | `Descripción corta`, `Tipo de Uso`, `Contador de copias` | ❌ ROTO — fields no existen (P0 T-03) |
| `consultar_catalogo` (Airtable Search) | Equipos | vista `viwCUJCvUbuDFXKqA` | ✅ OK |
| `consultar_catalogo` (Airtable Search) | Aplicaciones | view=None | ⚠️ falta vista (P1 V-01, V-02) |
| `consultar_catalogo` (Airtable Search) | Konica Minolta | view=None | ⚠️ falta cablear `viwKrFyMCZqQynwKF` (P1 V-01) |
| `consultar_aplicacion-v2` | Aplicaciones | view=None + probable filtro con field name | ⚠️ falta vista + heredar posibles bugs de T-01/T-02 (revisar) |
| `consultar_inventario_usados-v1` | Konica Minolta | view=None | ⚠️ falta cablear vista |
| `consultar_lineas_priorizadas-v1` | Config Mensual | `{Activo}=TRUE()` + `Líneas priorizadas` | ❌ potencial ROTO — field es multilineText no Link (P0 SD-11) |
| `consultar_url_tienda-v2` | Insumos | view=None | ⚠️ falta cablear |
| `consultar_tecnologia-v2` | Tecnologías | view=`viwTcatfyam1NzJTp` (Activas) | ✅ OK |
| `consultar_compatibilidad` | Equipos, Sustratos | linked records | ❌ herencia S-01 (Sustratos basura) |
| `consultar_faq` | FAQs | vista + filtro Status | ✅ OK, con reserva sobre confirmar filtro real de la vista |
| `notificar_lead` | Airtable | — (no escribe a Airtable, mail + Telegram) | ✅ OK; roadmap Opción B usaría Representantes.`Líneas asignadas` roto (SD-12) |
| `guardar_email` | Google Sheets + Supabase | — | ✅ OK (no toca Airtable) |

Leyenda: ✅ funciona · ⚠️ funciona degradado o con datos malos · ❌ NOT\_FOUND falso, error o output basura.

---

Reporte grabado en `/Users/camilo/Downloads/camilo-workspace/clients/SYS_SistemasYSoluciones/06_docs/airtable-auditoria-2026-07-01.md`.
