# Airtable CSVs — Import Guide (re-alineado post-Excel 2026-05-29)

> **Para:** carga del catálogo real entregado por el cliente (`BASE DE PRODUCTOS.xlsx`).
> **Encoding:** UTF-8 sin BOM. Separator: comma. Multi-values: comma-separated entre quotes dobles.
> **Generado:** 2026-05-29
> **Fuente:** parseo automático del Excel del cliente vía script (`/Users/camilo/Downloads/BASE DE PRODUCTOS.xlsx`).

---

## Resumen

11 archivos CSV listos para importar en Airtable. **8 con data real del cliente** + 3 con seeds la agencia (sustratos, aplicaciones, config mensual).

| # | Archivo | Tabla destino | Records | Origen | Linkea a |
|---|---|---|---|---|---|
| 1 | `01-tecnologias.csv` | Tecnologías | 10 | la agencia (8 + 2 derivadas del Excel) | — |
| 2 | `02-sustratos.csv` | Sustratos | 16 | la agencia (sin cambios) | Tecnologías |
| 3 | `03-lineas-de-producto.csv` | Líneas de Producto | 10 | la agencia (sin Mimaki/Roland, +Solvente/Corte) | — |
| 4 | `04-aplicaciones.csv` | Aplicaciones | 20 | la agencia (sin cambios) | Tecnologías + Sustratos |
| 5 | `05-faqs.csv` | FAQs | 12 | la agencia (10 + 2 rescatadas del Excel) | — |
| 6 | `06-representantes.csv` | Representantes | 1 | la agencia (Líneas actualizadas) | Líneas de Producto |
| 7 | `07-config-mensual.csv` | Config Mensual | 1 | la agencia (sin cambios) | — |
| 8 | `08-equipos.csv` | **Equipos** | **92** | **Cliente Excel** (68 + 19 Sinajet + 5 RISO) | Tecnologías + Líneas |
| 9 | `09-cabezales.csv` | **Cabezales** | **10** | **Cliente Excel** | — (Equipos compatibles vacío inicialmente) |
| 10 | `10-insumos.csv` | **Insumos** | **33** | **Cliente Excel** (32 + 1 tinta UNIVERSAL RISO) | Tecnologías |
| 11 | `11-inventario-konica.csv` | **Inventario Konica Minolta** (nueva tabla) | **21** | **Cliente Excel** (equipos USADOS) | — |

**Total records: ~226 distribuidos en 12 tablas.**

---

## ⚠️ Lectura obligatoria antes de importar

Este import asume que **el schema de Airtable ya está actualizado** según `realineacion-post-excel-2026-05-29.md`. Si todavía no actualizaste las tablas Equipos/Cabezales/Insumos ni creaste la tabla `Inventario Konica`, **leé primero ese doc**, hacé los cambios en UI, y después volvé acá.

### Cambios estructurales pendientes en UI (resumen)

- **Equipos**: borrar los 5 stubs ya importados; agregar campos `Cabezales hasta/incluidos/tipo`, `Datos extra`, `Tipo de Uso`, `Precio USD`; cambiar opciones `Marca` y `Formato` (single-select).
- **Cabezales**: agregar campos `Gama`, `Cabezal familia`, `Perfil de Usuario`, `Precio USD`.
- **Insumos**: agregar campos `Modelo de cabezal`, `Configuración de color`, `Cantidad ML/G`, `Tipo`, `Precio USD`.
- **NUEVA tabla**: `Inventario Konica Minolta` (schema en doc de re-alineación).
- **Líneas de Producto**: eliminar records `Mimaki` y `Roland` si existen (no aplican a la realidad del cliente).
- **Vistas "Para agente"**: ocultar campo `Precio USD` en Equipos, Cabezales, Insumos, Inventario Konica.

---

## Tipos de campos esperados (post-re-alineación)

### Tabla 1: Tecnologías (10 records)

| Columna | Tipo Airtable | Notas |
|---|---|---|
| Nombre | **Primary** — Single line text | |
| Línea principal | Single select | DTF Textil, DTF UV, UV, Sublimación, Eco-Solvente, **Solvente**, **Corte**, RISO, IDL Láser, Gran Formato |
| Descripción larga | Long text | |
| Materiales recomendados | Long text | |
| Restricciones / Limitaciones | Long text | |
| Aplicaciones típicas | Long text | |

### Tabla 2: Sustratos (16 records) — sin cambios respecto a versión anterior

(ver versión previa del README — no se modificó)

### Tabla 3: Líneas de Producto (10 records, actualizado)

| Columna | Tipo Airtable | Notas |
|---|---|---|
| Línea | **Primary** — Single line text | |
| Tipo | Single select | Marca exclusiva, Familia tecnología, Genérico |
| Descripción | Long text | |

**Records:** Sinajet, Konica Minolta IDL, RISO (Marca exclusiva); DTF Textil, DTF UV, UV, Sublimación, Eco-Solvente, **Solvente**, **Corte** (Familia tecnología).
**Eliminados:** ~~Mimaki, Roland~~ (no aplican al catálogo real del cliente).

Después del import: agregar manualmente campo `Representante asignado` (Linked → Representantes, single) y linkear cada línea a "Equipo Comercial".

### Tabla 4: Aplicaciones (20 records) — sin cambios

### Tabla 5: FAQs (12 records, +2 nuevas)

| Columna | Tipo Airtable | Notas |
|---|---|---|
| Pregunta | **Primary** — Single line text | |
| Categoría | Single select | Showroom, Financiación, Servicio Técnico, Plazos, Garantía, Llamadas, Devoluciones, Distribuidores, Otros |
| Keywords | Long text | |
| Respuesta corta | Long text | |
| Status | Single select | Activo, Revisión, Archivado |

**2 FAQs nuevas:** "¿Los precios incluyen IVA?" y "¿Diferencia entre cabezales i1600 e i3200?"

### Tabla 6: Representantes (1 record) — sin cambios estructurales

### Tabla 7: Config Mensual (1 record) — sin cambios

### Tabla 8: Equipos (92 records reales del cliente) ⚠ schema actualizado

| Columna | Tipo Airtable | Notas |
|---|---|---|
| Modelo | **Primary** — Single line text | |
| Marca | Single select | **HUENU, DLICAN, TENETH, HANRUN, XENONS, RISO, Sinajet, Konica Minolta, Otro** (NO Mimaki/Roland/Epson — esas son de Cabezales) |
| Tecnología | **Linked → Tecnologías** | Multi permitido |
| Línea de Producto | **Linked → Líneas de Producto** | Single |
| Formato | Single select | **Rollo a Rollo, Cama Plana, Híbrido, Mesa, Plotter, Cilíndrica, Pliego, Bobina, Compacta, Horno, Purificador, Plancha** (11 opciones; las últimas 3 son accesorios) |
| Ancho | **Single line text** (NO Number) | Algunos valores son combinados: "160*88", "60*90", "297*420" |
| Cabezales hasta | Number | Capacidad máxima de cabezales soportados |
| Cabezales incluidos | Number | Cantidad que viene incluida |
| Cabezales tipo | Single line text | Modelo del cabezal: I3200E, konica 512i, Ricoh G5/G6, Kyocera KJ4B, etc. |
| Datos extra | Long text | "Cuerpo reforzado", "C/ horno y purificador", "Camara opcional para HF 3040", etc. |
| Tipo de Uso | Long text | Específico para Sinajet/corte: "Etiquetas, tarjetas de visita y cajas pequeñas" |
| Descripción corta | Long text | |
| Disponibilidad zona | Multi select | CABA, GBA, Interior |
| Status | Single select | Activo, Discontinuado, Próximamente |
| **Precio USD** | Number | **NO incluir en vista "Para agente"** (regla anti-precios) |
| Notas internas | Long text | |
| Última modificación | Last modified time | Auto |

**Aplicaciones compatibles, Sustratos compatibles, Cabezales**: NO en el CSV (vienen vacíos). El cliente puede linkearlos a mano después según corresponda (es trabajo opcional).

### Tabla 9: Cabezales (10 records reales) ⚠ schema actualizado

| Columna | Tipo Airtable | Notas |
|---|---|---|
| Modelo | **Primary** — Single line text | DX5, XP600, Ei3200E, GEN5i, etc. |
| Marca | Single select | **EPSON, RICOH, KONICA MINOLTA, OTRO** |
| Tipo | Single select | Original, Compatible, Repuesto |
| Gama | Single select | Económica, Calidad/Precio, Industrial UV, Alta Velocidad, Premium, Otro |
| Cabezal familia | Single line text | "i3200 / i1600", "Ricoh Gen5 / Gen5i", "Ricoh Gen6 / Konica 1024A" |
| Perfil de Usuario | Long text | "Emprendedores, bajo presupuesto inicial.", "Plantas industriales de gran volumen.", etc. |
| URL tienda | URL | Vacío |
| **Precio USD** | Number | **NO incluir en vista "Para agente"** |
| Stock disponible | Checkbox | |

### Tabla 10: Insumos (33 records reales) ⚠ schema actualizado

| Columna | Tipo Airtable | Notas |
|---|---|---|
| Insumo | **Primary** — Single line text | |
| Categoría | Single select | **TINTAS, FILM, POLVO**, Vinilo, Papel transfer, Otros |
| Marca | Single select | **HANRUN, XENONS, DLICAN, RISO, Otro** |
| Tecnología | **Linked → Tecnologías** | Single |
| Modelo de cabezal | Single line text | I3200, I3200HD, XP600, RG5/G6, I1600, TOSHIBA (7110), A + B. 60*100, etc. |
| Configuración de color | Single line text | CMYK, BLANCO, VARNISH, BLANCO Y VARNISH, FLUO MAGENTA Y FLUO AMARILLO, LACA, CLEANING FLUSH, POWDER, COLORES SPOT, etc. |
| Cantidad ML/G | Number | 250, 500, 1000 |
| Tipo | Single line text | NEUTRAL, SOFT (algunos vacíos) |
| URL tienda | URL | Vacío |
| **Precio USD** | Number | **NO incluir en vista "Para agente"** |
| Descripción | Long text | |

### Tabla 11: Inventario Konica Minolta (NUEVA, 21 records)

| Columna | Tipo Airtable | Notas |
|---|---|---|
| Modelo | **Primary** — Single line text | "Acurio Press 6120", "BIZHUB 308E", etc. |
| Marca | Single select | Konica Minolta (fijo) |
| Tipo | Single select | BN, COLOR |
| Copias Total | Number | Contador acumulado |
| Copias Negro | Number | |
| Copias Color | Number | |
| Accesorios | Long text | String complejo: "TOP(Dual Scan),Printer Controller(Internal),HD,..." |
| Estado | Single select | Disponible, Reservado, Vendido |
| Ubicación | Single select | PEPIRI, Otros |
| Stock | Number | Cantidad disponible (1-17 según modelo) |
| **Precio USD** | Number | Vacío inicialmente (el comercial cotiza caso por caso) |
| Notas | Long text | |

---

## Procedimiento de import (orden estricto)

### Pre-requisitos

- [ ] Schema de las tablas actualizado en Airtable (ver `realineacion-post-excel-2026-05-29.md`)
- [ ] Tabla nueva `Inventario Konica Minolta` creada
- [ ] Los 5 stubs de Equipos eliminados (DTF-STD-600, UV-STD-Cama, etc.)
- [ ] Records `Mimaki` y `Roland` eliminados de Líneas de Producto si existen
- [ ] Records existentes de Tecnologías (8) y FAQs (10) presentes (de import previo)

### Orden de import

1. **`01-tecnologias.csv`** — `Append`. Agrega los 2 nuevos (Solvente, Corte). Los 8 originales ya están → Airtable los detectará como duplicados por primary; aceptar.
2. **`03-lineas-de-producto.csv`** — `Append`. Misma lógica.
3. **`05-faqs.csv`** — `Append`. Agrega 2 nuevas FAQs.
4. **`06-representantes.csv`** — actualizar manualmente el record existente "Equipo Comercial" con las nuevas Líneas asignadas (no es un append nuevo, es un update).
5. **`08-equipos.csv`** — `Append` o `Create new` si la tabla está vacía después de borrar stubs. **92 records reales.**
6. **`09-cabezales.csv`** — `Append`. 10 records.
7. **`10-insumos.csv`** — `Append`. 33 records.
8. **`11-inventario-konica.csv`** — `Append` a la tabla **Inventario Konica Minolta** (NUEVA). 21 records.

### Después del import

- Verificar conteos: Equipos=92, Cabezales=10, Insumos=33, Inventario Konica=21.
- Configurar vista "Para agente" en Equipos/Cabezales/Insumos/Inventario Konica → ocultar `Precio USD`.
- Para Equipos: opcional linkear `Aplicaciones compatibles` + `Sustratos compatibles` por record (trabajo manual; el agente puede operar sin esto en F1, son refinamientos).
- Capturar Table ID de `Inventario Konica Minolta` y agregarlo a `airtable-credentials.md`.

---

## Reglas de Airtable CSV import (recordatorio)

1. **Primary field** es obligatorio y único. Duplicados → Airtable mergea/saltea según config.
2. **Linked records** se matchean por primary field value. Si no encuentra match, **crea record nuevo automáticamente** (cuidado: importar tabla referenciada primero).
3. **Multi-values**: comma-separated entre quotes dobles. Ej: `"DTF Textil, Sublimación"`.
4. **Single/Multi select**: si la opción no existe, Airtable la crea automáticamente. Verificar spelling para no duplicar.
5. **Checkbox**: `true`, `TRUE`, `1`, `checked` → marcado.
6. **Number**: sin separadores de miles; decimal con `.` (punto).
7. **Long text con saltos de línea**: encerrar entre quotes dobles; escapar quotes internas con `""`.
8. **Attachment**: NO se puede importar desde CSV.

---

## Smoke test post-import

- [ ] Equipos: 92 records. Spot check: abrir `HR 1602 ES` (HUENU) → ver Marca=HUENU, Tecnología=Eco-Solvente, Cabezales tipo=I3200E, Ancho=166, Precio USD=5350.
- [ ] Equipos: filtrar por Marca=Sinajet → debería mostrar 19 records.
- [ ] Equipos: filtrar por Tecnología=Corte → debería mostrar 29 records (19 Sinajet + 10 TENETH).
- [ ] Cabezales: spot check `Ei3200E` → Gama=Calidad/Precio, Cabezal familia="i3200 / i1600", Precio USD=1829.95.
- [ ] Insumos: 33 records. Spot check `Xenons UV i3200 Series White` → Categoría=TINTAS, Marca=XENONS, Configuración de color="BLANCO Y VARNISH", Cantidad=1000.
- [ ] Inventario Konica: 21 records. Spot check `BIZHUB 450i` → Stock=17, Estado=Disponible, Ubicación=PEPIRI.
- [ ] FAQs: 12 records. Verificar que las 2 nuevas (IVA y i1600/i3200) estén Activo.
- [ ] Vista "Para agente" en Equipos: el campo Precio USD NO debe ser visible.

---

## Si algo sale mal

- **Linked field crea Tecnologías duplicadas**: import 08-equipos hizo "DTF Textil" como nuevo en vez de matchear. Borrar la duplicada y revisar que la columna del CSV tenga exactamente el primary field value.
- **Single select no acepta valor del CSV**: probablemente un typo. Ej. "HUENU" vs "Huenu". Verificar case.
- **`Configuración de color` con coma interna no se importa bien**: Airtable lo parsea como multi-value. Reimportar con el campo como `Long text` en lugar de `Single line text`.
- **Inventario Konica falla al importar**: verificar que la tabla NUEVA esté creada con los campos correctos antes de importar.
