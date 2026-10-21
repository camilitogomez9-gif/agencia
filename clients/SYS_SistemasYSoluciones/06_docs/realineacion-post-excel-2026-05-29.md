# Re-alineación post-Excel — 2026-05-29

> **Disparador:** el cliente entregó `BASE DE PRODUCTOS.xlsx` (98 KB, 6 sheets, 164 records reales).
> **Estado anterior:** F1 ejecutada con stubs (5 equipos genéricos, marcas Mimaki/Roland inventadas).
> **Estado actual:** schema re-diseñado al catálogo real; CSVs regenerados; docs y prompt actualizados; cliente debe re-importar.

---

## Por qué este doc

Cuando una sesión futura cargue contexto sobre SYS, este archivo explica **qué cambió y por qué** entre la primera F1 (stubs) y la F1 alineada (Excel real). Incluye gaps que rompieron asunciones del Plan Maestro y decisiones tomadas para alinear.

---

## Hallazgos del Excel real (164 records, no 50 estimados)

### Sheets del Excel y mapeo a tablas Airtable

| Sheet Excel | Records reales | Tabla Airtable destino | Notas |
|---|---|---|---|
| `Equipos` | 68 | `Equipos` (parte) | Marcas reales: HUENU, DLICAN, TENETH, HANRUN, XENONS |
| `Sinajet` | 19 | `Equipos` (parte, Marca=Sinajet, Tecnología=Corte) | Tiene campo único `Tipo de Uso` que describe el uso ideal del modelo |
| `Cabezales plotters` | 10 cabezales + 6 filas FAQ | `Cabezales` (10) + `FAQs` (1 nueva: comparativa i1600 vs i3200) | El sheet tenía datos comparativos al final, separados en records nuevos |
| `Insumos Tintas y DTF` | 32 | `Insumos` (32 + 1 tinta UNIVERSAL RISO = 33) | 6 tecnologías de insumos: UV, DTF TEXTIL, DTF UV, ECOSOLVENT, SUBLIMATION, PIGMENT |
| `RISO Impresion Digital Inkjet` | 5 equipos + 1 tinta + 1 FAQ | `Equipos` (5) + `Insumos` (1) + `FAQs` (1 nueva: precios IVA) | RISO tiene su propia categoría comercial pero entra al schema unificado de Equipos |
| `Konica Minolta Impresion Digita` | 21 | **NUEVA tabla `Inventario Konica`** | Inventario de equipos USADOS refurbished, todos en PEPIRI, sin precio. Decisión: tabla separada + nueva tool `consultar_inventario_usados` |

**Total records en Airtable después de re-alineación: ~230** (sigue cabiendo en Free tier de 1000).

---

## Asunciones que se rompieron

| Asunción previa (Plan Maestro) | Realidad del Excel | Acción tomada |
|---|---|---|
| Marcas: Mimaki, Roland, Epson, Mutoh | **HUENU (36), DLICAN (16), TENETH (10), HANRUN (4), XENONS (2)** + RISO + Sinajet + Konica Minolta | Eliminé Mimaki/Roland del schema. Cambié single-select Marca a 9 opciones reales. |
| 8 tecnologías | **10**: las 8 + **Solvente** + **Corte** | Agregué Solvente y Corte a tabla Tecnologías. Actualicé prompt v2.0 → v2.1. |
| Equipos = 30-80 | **92** (68 + 19 Sinajet + 5 RISO) | Reemplazo de 5 stubs por 92 records reales. |
| Catálogo lo carga Edgardo | **Ya entregado** | Bloqueo cliente F0 → RESUELTO 2026-05-29. |
| Tabla Cabezales simple | Necesita `Gama` + `Perfil de Usuario` (info de marketing crítica para asesoramiento) | Schema actualizado. CSV con 10 records reales (EPSON, RICOH, KONICA MINOLTA). |
| Tabla Insumos simple | Necesita `Modelo de cabezal`, `Configuración de color`, `Cantidad ML/G`, `Tipo` (NEUTRAL/SOFT) | Schema actualizado. CSV con 33 records. |
| Konica Minolta = 1 línea | **21 equipos USADOS** con contadores, ubicación, stock | Nueva tabla `Inventario Konica Minolta`. Nueva tool `consultar_inventario_usados`. |
| Precios fuera de Airtable | Excel los tiene todos. Cliente edita en Airtable | Decisión: campo `Precio USD` en tablas Equipos/Cabezales/Insumos, **NO incluido en la vista "Para agente"** → el agente nunca lee precios. |
| 4 tipos de equipo (Mesa plana, Roll-to-roll, Híbrido, Compacta) | **11 tipos** incluyendo accesorios (Horno, Purificador, Plancha) | Schema actualizado. Accesorios mencionados en system prompt. |

---

## Decisiones arquitectónicas tomadas

### D1 — Precios USD en Airtable con vista oculta al agente

**Razón:** el Excel los tiene. Cliente quiere editarlos en un solo lugar. Pero la regla "el agente NUNCA da precios" sigue vigente.

**Implementación:**
- Campo `Precio USD` (Number) en tablas Equipos, Cabezales, Insumos.
- Vista "Para agente" en cada tabla **excluye** el campo Precio USD.
- Las tools del agente leen únicamente esa vista.
- Cliente edita en la vista completa (default).

### D2 — Tabla `Inventario Konica Minolta` separada del catálogo

**Razón:** son equipos USADOS refurbished con lógica distinta (contadores de copias, ubicación física, stock variable). Mezclarlos con el catálogo de nuevos contaminaría las queries del agente.

**Implementación:**
- Tabla nueva con 21 records.
- Nueva tool `consultar_inventario_usados` (Tool 9).
- System prompt menciona la opción "tenemos equipos usados refurbished" cuando el cliente pregunta por presupuestos bajos en producción digital láser.

### D3 — Schema unificado de `Equipos` (Sinajet, RISO, HUENU/DLICAN/etc. juntos)

**Razón:** desde el lado del agente y del cliente, todos son "equipos del catálogo". Mantener tablas separadas para Sinajet/RISO crearía 6 tools en lugar de 1 (`buscar_equipo`).

**Implementación:**
- Marca y Tecnología como linked/single-select diferencian.
- Campo `Tipo de Uso` (Long text) — específico para Sinajet (cortes), vacío para resto.
- Total: 92 records en una sola tabla.

### D4 — Normalización de tecnologías (Excel → Airtable)

Mapeo aplicado por el script generador:

| Excel | Airtable |
|---|---|
| `Ecosolvente` / `ECOSOLVENT` | `Eco-Solvente` |
| `SUBLIMATION` | `Sublimación` |
| `DTF` (en Equipos) / `DTF TEXTIL` (en Insumos) | `DTF Textil` |
| `DTF UV` | `DTF UV` |
| `UV` | `UV` |
| `Solvente` | `Solvente` (NUEVO) |
| `Corte` | `Corte` (NUEVO) |
| `PIGMENT` (en insumos) | `UV` (es una tinta UV especial pigmentada, no una tecnología independiente) |
| `Inkjet` (en RISO sheet) | `RISO` |

### D5 — 2 FAQs nuevas rescatadas del Excel

1. **"¿Los precios incluyen IVA?"** → "Los precios están expresados en dólares (USD) y no incluyen IVA. La cotización final con impuestos te la pasa el equipo comercial."
2. **"¿Diferencia entre cabezales i1600 e i3200?"** → respuesta basada en las 5 filas comparativas del sheet Cabezales (boquillas, velocidad, canales, calidad, costo).

### D6 — Líneas de Producto sin Mimaki/Roland

- Eliminé Mimaki y Roland (no hay equipos de esas marcas en el catálogo real).
- Agregué Solvente y Corte como familias tecnológicas.
- Total: 10 líneas (Sinajet, Konica Minolta IDL, RISO, DTF Textil, DTF UV, UV, Sublimación, Eco-Solvente, Solvente, Corte).

---

## Cambios al schema Airtable (qué tiene que modificar el usuario en UI)

### Tablas a MODIFICAR

**`Equipos`:**
- Cambiar opciones `Marca` (single-select): HUENU, DLICAN, TENETH, HANRUN, XENONS, RISO, Sinajet, Konica Minolta, Otro
- Cambiar opciones `Formato` (single-select): Rollo a Rollo, Cama Plana, Híbrido, Mesa, Plotter, Cilíndrica, Pliego, Bobina, Compacta, Horno, Purificador, Plancha
- Renombrar `Ancho máx (mm)` (Number) → `Ancho` (Single line text, porque hay valores como "160*88", "60*90")
- Agregar campos:
  - `Cabezales hasta` (Number)
  - `Cabezales incluidos` (Number)
  - `Cabezales tipo` (Single line text)
  - `Datos extra` (Long text)
  - `Tipo de Uso` (Long text)
  - `Precio USD` (Number)
- Eliminar campo `Velocidad (m²/h)` (sin data en Excel)
- **Borrar los 5 stubs ya importados** (DTF-STD-600, UV-STD-Cama, Sublimación-STD, RISO-Modelo-Stub, KM-IDL-Stub)

**`Cabezales`:**
- Cambiar opciones `Marca` (single-select): EPSON, RICOH, KONICA MINOLTA, OTRO
- Agregar campos:
  - `Gama` (Single select): Económica, Calidad/Precio, Industrial UV, Alta Velocidad, Premium, Otro
  - `Cabezal familia` (Single line text)
  - `Perfil de Usuario` (Long text)
  - `Precio USD` (Number)

**`Insumos`:**
- Cambiar opciones `Categoría` (single-select): TINTAS, FILM, POLVO, Vinilo, Papel transfer, Otros
- Cambiar opciones `Marca` (single-select): HANRUN, XENONS, DLICAN, RISO, Otro
- Agregar campos:
  - `Modelo de cabezal` (Single line text)
  - `Configuración de color` (Single line text)
  - `Cantidad ML/G` (Number)
  - `Tipo` (Single line text — NEUTRAL/SOFT/vacío)
  - `Precio USD` (Number)

**`FAQs`:**
- Agregar 2 records vía CSV (ya están en `05-faqs.csv` actualizado).

**`Tecnologías`:**
- Agregar 2 records: Solvente, Corte (ya están en `01-tecnologias.csv` actualizado).

**`Líneas de Producto`:**
- Eliminar records Mimaki y Roland (si están).
- Agregar Solvente y Corte (ya en `03-lineas-de-producto.csv` actualizado).

### Tablas NUEVAS a crear

**`Inventario Konica Minolta`:**
| Campo | Tipo |
|---|---|
| Modelo (primary) | Single line text |
| Marca | Single select (Konica Minolta) |
| Tipo | Single select (BN, COLOR) |
| Copias Total | Number |
| Copias Negro | Number |
| Copias Color | Number |
| Accesorios | Long text |
| Estado | Single select (Disponible, Reservado, Vendido) |
| Ubicación | Single select (PEPIRI, otros) |
| Stock | Number |
| Precio USD | Number (vacío hasta cotización) |
| Notas | Long text |

### Vistas críticas a configurar/actualizar

| Tabla | Vista | Filtro / Notas |
|---|---|---|
| `Equipos` | "Para agente" | `Status = Activo`, **excluir campo `Precio USD`** |
| `Cabezales` | "Para agente" | Sin filtro, **excluir campo `Precio USD`** |
| `Insumos` | "Para agente" | Sin filtro, **excluir campo `Precio USD`** |
| `Inventario Konica` | "Para agente" | `Estado = Disponible` AND `Stock > 0`, **incluye stock pero NO precio** |
| `Inventario Konica` | "Comercial completa" | sin filtro, todos los campos |

---

## Pasos del usuario (post-re-alineación)

1. **En Airtable:** modificar las tablas Equipos/Cabezales/Insumos según especificación arriba (~30 min).
2. **En Airtable:** crear la tabla nueva `Inventario Konica Minolta` con su schema (~15 min).
3. **Borrar los 5 stubs ya importados** en la tabla Equipos.
4. **Re-importar los CSVs nuevos** (orden: 01 → 03 → 05 → 06 → 08 → 09 → 10 → 11):
   - `01-tecnologias.csv` (append — agrega Solvente y Corte; los 8 existentes ya están)
   - `03-lineas-de-producto.csv` (append los nuevos: Solvente, Corte; eliminar Mimaki/Roland a mano)
   - `05-faqs.csv` (append: las 2 nuevas)
   - `06-representantes.csv` (overwrite: actualiza Líneas asignadas)
   - **`08-equipos.csv`** (append: 92 records reales del cliente)
   - **`09-cabezales.csv`** (append: 10 records reales)
   - **`10-insumos.csv`** (append: 33 records)
   - **`11-inventario-konica.csv`** (append: 21 records, a la tabla nueva)
5. **Crear/ajustar vistas "Para agente"** con la columna `Precio USD` **oculta**.
6. **Actualizar `airtable-credentials.md`** con el Table ID de `Inventario Konica`.
7. **Smoke test:** abrir un equipo cualquiera (ej. `HR 1602 ES` HUENU), verificar todos los campos linkeados correctamente.

---

## Archivos del proyecto que se actualizaron (este día)

| Archivo | Cambio |
|---|---|
| `06_docs/airtable-csv/01-tecnologias.csv` | +2 records (Solvente, Corte) |
| `06_docs/airtable-csv/03-lineas-de-producto.csv` | Eliminados Mimaki/Roland, agregados Solvente/Corte |
| `06_docs/airtable-csv/05-faqs.csv` | +2 FAQs (IVA + i1600/i3200) |
| `06_docs/airtable-csv/06-representantes.csv` | Líneas asignadas actualizadas (sin Mimaki/Roland) |
| `06_docs/airtable-csv/08-equipos.csv` | **NUEVO** — 92 records reales (reemplaza 08-equipos-stub.csv eliminado) |
| `06_docs/airtable-csv/09-cabezales.csv` | **NUEVO** — 10 records reales (reemplaza 09-cabezales-stub.csv eliminado) |
| `06_docs/airtable-csv/10-insumos.csv` | **NUEVO** — 33 records reales |
| `06_docs/airtable-csv/11-inventario-konica.csv` | **NUEVO** — 21 records refurbished |
| `06_docs/airtable-csv/README.md` | Updated con nuevos tipos de campo + orden de import |
| `06_docs/realineacion-post-excel-2026-05-29.md` | **Este archivo** |
| `06_docs/tools-spec-v1.md` | Tool `buscar_equipo` actualizado + nueva Tool 9 `consultar_inventario_usados` |
| `06_docs/airtable-seeds-completos.md` | Marcado como OBSOLETO; referencia a CSVs reales |
| `06_docs/f1-migracion-airtable-log.md` | Registrada la re-alineación |
| `06_docs/airtable-credentials.md` | Placeholder para Inventario Konica Table ID |
| `04_agents/agente-sistemasysoluciones-system-prompt.md` | v2.1: +Solvente +Corte, marcas reales, FAQ IVA, inventario usados |
| `04_agents/agente-sistemasysoluciones-system-prompt-v2.1.md` | Backup v2.1 |
| `05_crm/airtable-syscatalogo-schema.md` | Tablas re-spec |
| `02_architecture/architecture-v2-2026-05.md` | 12 tablas, marcas reales, decisión precio oculto |
| `CLIENT_INFO.md` | Bloqueo "catálogo Edgardo" RESUELTO; agregada tabla 12 (Inventario Konica) |
| `CLAUDE.md` (raíz) | Estado SYS actualizado |

---

## Próximos pasos del proyecto

1. **Usuario ejecuta cambios en Airtable** (~1-2 hs según puntos 1-7 arriba).
2. **Continuar con Paso 12 del plan F1**: capturar Table IDs nuevos (Cabezales, Insumos, Inventario Konica) y completar `airtable-credentials.md`.
3. **Pasos 13-14 del plan F1**: credencial n8n + variables.
4. **F2**: setup Supabase (sin cambios respecto al plan original).
5. **F3**: workflow principal con memoria persistente.
6. **F4**: construir las **9 tools** (era 8, ahora +1 por `consultar_inventario_usados`).
7. **F5**: validar prompt v2.1 → testing → posible v2.2 según hallazgos.
