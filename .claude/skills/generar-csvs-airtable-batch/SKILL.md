---
name: generar-csvs-airtable-batch
description: >
  Usar este skill cuando hay que generar N CSVs importables a Airtable de manera
  batch (esquema definido pero data viene parcial/stub o desde un Excel parseado).
  Se activa con frases como "generar CSVs para Airtable", "armar los CSV de import",
  "necesito los CSVs para importar a la base de X", "F1 sin Excel real, solo schema".
  Diferente a `migrar-excel-a-airtable-rag` (S8): este es para casos sin Excel —
  schema-first, data minimal o seeded.
---

# Skill: Generar CSVs Importables a Airtable (Batch)

## Descripción

Genera N CSVs listos para importar a Airtable a partir de un schema definido (en `airtable-schema-v1.md` o similar). Cubre:

- 1 CSV por tabla, ordenados para import (numerados `01-`, `02-`, ...)
- Seeds estándar para tablas de catálogo (tecnologías, categorías, FAQs base)
- Header rows correctos con tipos esperables por Airtable
- README.md de import con orden estricto

Diferente a `migrar-excel-a-airtable-rag` (S8):
- S8: hay un Excel del cliente → parsea, normaliza, detecta divergencias.
- S15: NO hay Excel todavía → genera stubs + seeds para que el cliente luego complete.

---

## Cuándo invocarlo

- F1 del Plan Maestro y el cliente NO entregó Excel aún (arrancamos con stub)
- Tablas de catálogo donde la agencia tiene seeds estándar (tecnologías, categorías, FAQs comunes del nicho)
- Necesidad de tener la base poblada con data mínima para empezar testing tools antes de que el cliente termine el catálogo real

## Cuándo NO invocarlo

- Hay Excel del cliente → usar S8
- Solo 1-2 tablas con <10 records → hacer manual en UI Airtable
- Schema todavía no está definido → primero `bootstrap-agente-etapa-2` o `generar-architecture-doc`

---

## Inputs requeridos

1. **Cliente ID + nombre**
2. **Path al schema doc** (típicamente `05_crm/airtable-{cliente_id_lower}-schema.md` o el blueprint generado en F0/F1)
3. **Seeds disponibles** (si los hay): tecnologías base, FAQs base, categorías estándar del nicho

---

## Proceso

### Paso 1 — Parsear el schema

Leer el doc de schema y extraer:
- Lista de tablas (nombre, propósito)
- Por tabla: lista de campos (nombre, tipo Airtable: Single line text / Number / Single select / Multi select / Linked record / Date / Checkbox)
- Linked records: identificar tabla destino + primary field

### Paso 2 — Determinar orden de import

Reglas:
1. Tablas sin Linked records primero (catálogos puros: Tecnologías, Categorías)
2. Tablas con Linked records que apuntan a (1)
3. Tablas con dependencias en cadena más larga al final

Numerar `01-`, `02-`, ... reflejando este orden.

### Paso 3 — Generar CSV por tabla

```python
import csv

def gen_csv(out_path, headers, rows):
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(headers)
        w.writerows(rows)
```

Convenciones:
- Header row con el nombre exacto del field en Airtable
- Multi-select: valores separados por coma dentro de quotes (`"DTF Textil, Sublimación"`)
- Linked records: matchea por primary field — texto exacto del registro destino
- Single select: valor exacto del option

Path: `clients/{XXX}_{Nombre}/06_docs/airtable-csv/NN-{tabla}.csv`

### Paso 4 — Aplicar seeds estándar

Por nicho/dominio la agencia maneja seeds base. Embeber:

**Tecnologías impresión gráfica (caso SYS):**
```
Sublimación, DTF Textil, DTF UV, UV, Eco-Solvente, Solvente, RISO, IDL Láser, Corte
```

**FAQs base por nicho** (estética / consultivo / gráfico / etc.) — embeber 5-10 entradas estándar.

**Categorías producto** — depender del nicho.

Si no hay seeds para el nicho, dejar el CSV con header + 1-2 filas dummy con comentario `<EJEMPLO>`.

### Paso 5 — Generar README de import

Path: `clients/{XXX}_{Nombre}/06_docs/airtable-csv/README.md`

Contenido:

```markdown
# Import CSVs Airtable — {Cliente}

## Orden de import (estricto)

1. `01-tecnologias.csv` → tabla `Tecnologías` (sin Linked records)
2. `02-categorias.csv` → tabla `Categorías`
3. `03-marcas.csv` → tabla `Marcas`
4. `04-productos.csv` → tabla `Productos/Equipos` (linkea a Tecnologías + Categorías + Marcas)
5. ...

## Tipos de campo (verificar post-import)

| Tabla | Field | Tipo esperado |
|---|---|---|
| Tecnologías | Nombre | Single line text (primary) |
| Tecnologías | Descripción | Long text |
| Productos | Tecnologías | Multi-select linked → Tecnologías |
| Productos | Precio USD | Number (decimal, 2 places) |
| ... | ... | ... |

## Trampas conocidas Airtable

- **Number con valores `-` o `*`:** Airtable los importa como text — limpiar antes
- **Multi-select con `|` en valores:** Airtable lo trata como separador adicional — usar otra delimitación
- **Linked records:** Airtable matchea por primary field — si el texto no es EXACTO, crea registro huérfano

## Smoke test post-import

| Tabla | Records esperados |
|---|---|
| Tecnologías | ~10 |
| Categorías | ~8 |
| Productos | <<<TBD según cliente>>> |
```

### Paso 6 — Reportar al usuario

Output:
- Path del folder `airtable-csv/`
- Lista de CSVs generados con N records cada uno
- Orden de import explícito
- Sugerir: tras import, smoke test post-import (queries de count + sample row)

---

## Composición

**Invoca:** ninguno.
**Es invocado por:** F1 del Plan Maestro (cuando no hay Excel) o `bootstrap-agente-etapa-2`.
**Reemplazado por:** `migrar-excel-a-airtable-rag` (S8) cuando llega el Excel real.

---

## Notas operativas

- **Tiempo:** 15-25 min del skill.
- **Los CSVs son stubs para arrancar.** Cuando llegue el Excel real del cliente, correr S8 — los CSVs serán reemplazados.
- **Mantener seeds estándar en `_core/standards/seeds/`** si la agencia reusa entre clientes. Ej: `_core/standards/seeds/tecnologias-graficas.csv`.
- **Si una tabla pide >100 records dummy:** mejor seedeada vía Python script + Faker que escribir CSV a mano.
