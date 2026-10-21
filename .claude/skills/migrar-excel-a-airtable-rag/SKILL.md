---
name: migrar-excel-a-airtable-rag
description: >
  Usar este skill cuando el cliente entrega su catálogo en Excel/Sheets y hay
  que generar los CSVs importables a Airtable + schema doc + README de import +
  re-alineación de docs del proyecto. Se activa con frases como "el cliente
  mandó el Excel", "migrar el catálogo a Airtable", "re-alinear el proyecto
  con el catálogo real", "F1 cliente X con su xlsx". Stack: Python (openpyxl)
  + Airtable. Output: CSVs por tabla + README + lista de divergencias con
  asunciones iniciales.
---

# Skill: Migrar Excel del Cliente a Airtable RAG

## Descripción

Parsea el Excel del cliente (típicamente entregado post-F0 cuando el cliente recopila su catálogo), genera N CSVs importables a Airtable, normaliza nomenclatura (mapeo configurable de tecnologías/categorías/marcas), detecta divergencias con asunciones iniciales del Plan Maestro, y actualiza docs afectados.

**Patrón validado en SYS:** el catálogo real **casi siempre rompe asunciones** (marcas distintas, +tecnologías, +productos, precios incluidos cuando se asumía sin precios). El skill captura esto explícitamente.

---

## Cuándo invocarlo

- Cliente entregó Excel/Sheets con su catálogo
- F1 está en ejecución
- El usuario quiere "re-alinear" el proyecto al catálogo real

## Cuándo NO invocarlo

- Cliente entrega solo unas pocas filas (manual)
- Catálogo viene de un sistema legacy con API (usar conector específico)
- No hay schema Airtable definido aún — primero generar via `bootstrap-agente-etapa-2`

---

## Inputs requeridos

1. **Path al Excel del cliente** (ej. `/Users/camilo/Downloads/BASE DE PRODUCTOS.xlsx`)
2. **Cliente ID + nombre**
3. **Mapeo de normalización (si aplica):** dict de `Excel value` → `Canonical value`
   - Ej. `{"ECOSOLVENT": "Eco-Solvente", "SUBLIMATION": "Sublimación", "DTF": "DTF Textil"}`
   - Si no se provee, el skill detecta valores no estándar y pregunta al usuario

---

## Proceso

### Paso 1 — Análisis del Excel

```python
import openpyxl
wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
for name in wb.sheetnames:
    ws = wb[name]
    # contar rows reales (no incluir filas vacías)
    print(f"{name}: {real_rows} rows × {ws.max_column} cols")
    # extraer headers (primera fila)
    # extraer 3-5 filas sample
```

### Paso 2 — Identificar tablas destino en Airtable

Cada sheet del Excel mapea a una tabla Airtable. Hacer mapping inicial:
- Sheets típicos: `Equipos`, `Insumos`, `Cabezales`, `Tecnologías`, etc.
- Tablas Airtable típicas: `Productos/Equipos`, `Insumos`, `Categorías`, `FAQs`, `Representantes`, `Leads`

### Paso 3 — Detectar valores únicos y proponer normalización

Por columna sospechosa (Tecnología, Marca, Categoría), extraer valores únicos:

```python
from collections import Counter
unique_values = Counter()
for r in range(2, ws.max_row + 1):
    v = ws.cell(row=r, column=col_idx).value
    if v: unique_values[str(v).strip()] += 1
print(unique_values.most_common(20))
```

Mostrar al usuario y pedir confirmación del mapeo. Si el plan maestro asumía "8 tecnologías" y el Excel tiene "10", **flagear como divergencia**.

### Paso 4 — Generar CSVs

Script Python que recorre cada sheet y emite CSVs en `clients/{XXX}_{Nombre}/06_docs/airtable-csv/`:

```python
import csv
with open(out_path, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    w.writerow(headers)
    w.writerows(rows)
```

Convenciones:
- 1 CSV por tabla Airtable (numerados `01-tabla1.csv`, `02-tabla2.csv` para orden de import)
- Multi-values con coma separated entre quotes dobles (ej. `"DTF Textil, Sublimación"`)
- Linked records: matchea por primary field — importar la tabla referenciada PRIMERO

### Paso 5 — Generar README de import

`clients/{XXX}_{Nombre}/06_docs/airtable-csv/README.md` con:
- Orden estricto de import
- Tipos de campo esperados por columna (Single line text / Single select / Multi select / Linked record / Number / etc.)
- Notas: types problemáticos (Number con valores `-` o `*`, multi-select con valores con `|`, etc.)
- Smoke test post-import (cuentas de records esperados por tabla)

### Paso 6 — Detectar divergencias y actualizar docs

Comparar contra el Plan Maestro original. Por cada divergencia significativa, registrar en `clients/{XXX}_{Nombre}/06_docs/realineacion-post-excel-{YYYY-MM-DD}.md`:

```markdown
## Asunciones rotas

| Asunción anterior | Realidad del Excel | Acción tomada |
|---|---|---|
| Marcas: Mimaki, Roland | HUENU, DLICAN, TENETH, HANRUN, XENONS | Eliminar Mimaki/Roland, agregar marcas reales |
| 8 tecnologías | 10 (+Solvente, +Corte) | Agregar 2 tecnologías al schema + system prompt |
| ~50 productos | 92 | Schema y memoria escalan OK, no acción |
| Sin precios | Todos con USD | Decisión: cargar en campo "Precio USD" oculto al agente via vista filtrada |
```

### Paso 7 — Updatear docs afectados

Tras la re-alineación, updatear:
- `04_agents/{nombre}-system-prompt.md` — agregar tecnologías/marcas/categorías reales, versionar (v.next)
- `06_docs/tools-spec-v1.md` — actualizar enums de args (`tecnologia`, `marca`)
- `02_architecture/architecture-v2.md` — actualizar componentes + decisiones técnicas
- `CLIENT_INFO.md` — marcar bloqueos "catálogo" como resueltos

### Paso 8 — Reportar al usuario

Output:
- Lista de CSVs generados con record counts
- Tabla de divergencias detectadas con acción tomada
- Updates aplicados a docs
- Próximos pasos: import en Airtable (orden), smoke test, iterar prompt si las divergencias afectan tono/comportamiento

---

## Composición

**Invoca:** opcionalmente `iterar-prompt` si las divergencias afectan el comportamiento del agente.
**Es invocado por:** F1 del Plan Maestro.
**Precede a:** F4 (que ahora puede usar el catálogo real).

---

## Notas operativas

- **Tiempo estimado:** 1-2 horas (~30 min del skill + 30 min config import en Airtable + 30 min validación divergencias).
- **Multi-select y Linked records** son los tipos más problemáticos. Si Airtable los detecta mal al importar, el skill provee el README para corregir tipo manualmente post-import.
- **Si el Excel tiene más de 1000 records:** considerar Airtable Pro plan ($20/mes) o reducir scope (solo activos).
- **El doc de re-alineación es valioso para el cliente** (transparencia sobre qué asumimos vs realidad) y para la agencia (lecciones para próximos clientes).
