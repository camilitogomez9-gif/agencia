---
name: generar-subworkflows-tools-n8n
description: >
  Usar este skill cuando hay que generar los N sub-workflows de tools para un
  agente conversacional (típicamente 8-10 tools sobre Airtable + 1 de notificación).
  Se activa con frases como "generar las tools del agente X", "crear sub-workflows
  tools", "armar los JSONs de las tools", "F4 del cliente X". Genera N JSONs n8n
  importables siguiendo el patrón Trigger → Validate → Airtable → Format → Log → Return,
  más doc operativo de tools-spec. Stack: n8n + Airtable + Supabase Postgres logging.
---

# Skill: Generar Sub-workflows Tools n8n

## Descripción

Genera N sub-workflows de tools n8n siguiendo el patrón validado en SYS (Trigger → Validate → External Search → Format → Log → Return), donde:

- **Trigger**: `Execute Workflow Trigger` con `inputSource: jsonExample` (que el LLM completa via `$fromAI()`)
- **Validate**: Code JS que valida inputs y devuelve `{status: 'ERROR', _skip: true}` si faltan
- **External Search**: Airtable Search/List/Create según la tool
- **Format**: Code JS que normaliza al contrato `{status, data, message_to_agent, trace_id}`
- **Log**: Postgres Insert a `sys_tool_calls` con `queryReplacement` array
- **Return**: Set node que retorna lo formateado al main workflow

---

## Cuándo invocarlo

- F4 del Plan Maestro
- F1 (Airtable poblado) y F2 (Supabase con `sys_tool_calls`) ya están completos
- Existe spec de las tools (al menos: nombre, descripción, args, target Airtable, lógica de búsqueda)

## Cuándo NO invocarlo

- Falta el catálogo Airtable real (derivar a `migrar-excel-a-airtable-rag` primero)
- El cliente requiere tools sobre backends distintos (no Airtable) — adaptar manualmente
- Solo se quiere agregar 1 tool nueva a un set existente — usar el script ad-hoc, no este skill completo

---

## Inputs requeridos

1. **Cliente ID + nombre**
2. **Catálogo de tools a generar** (lista). Por cada una:
   - `name` (ej. `buscar_equipo`, `consultar_tecnologia`)
   - `description` (lo que el LLM lee para decidir cuándo invocarla)
   - `schema`: lista de args con `{id, type, required, description}`. **TODOS los types deben ser `string`** (regla aprendida: arrays/booleans rompen Zod).
   - `target_airtable`: Base ID + Table ID + opcional view ID
   - `lógica_de_búsqueda`: una de
     - `search-by-field` (filterByFormula simple por un field)
     - `list-with-scoring` (lista + scoring JS en Format)
     - `multi-filter` (filterByFormula compuesto)
     - `create-and-notify` (write a Airtable + Gmail + Telegram, como `notificar_lead`)
3. **Credentials IDs en n8n** (Airtable + Supabase)
4. **Hardcoded constants** del cliente (ej. `BASE_ID`, `URL_TIENDA`, `GMAIL_TO_LEAD`)

Si falta alguno, preguntar o leer de `06_docs/airtable-credentials.md` (gitignored) y `tools-spec-v1.md`.

---

## Proceso

### Paso 1 — Leer el tools-spec

Cargar `clients/{XXX}_{Nombre}/06_docs/tools-spec-v1.md` con la especificación de cada tool. Si no existe, generarlo primero desde el system prompt v2.x (extraer la sección "## HERRAMIENTAS DISPONIBLES").

### Paso 2 — Script Python generador

Por cada tool, generar el JSON con el patrón estándar. Helpers reusables:

```python
def trigger_node(tool_name, fields):
    return {
        "id": nid(tool_name, "trigger"),
        "name": "Execute Workflow Trigger",
        "type": "n8n-nodes-base.executeWorkflowTrigger",
        "typeVersion": 1.1,
        "position": pos(0),
        "parameters": {
            "inputSource": "jsonExample",
            "jsonExample": json.dumps(fields, ensure_ascii=False, indent=2)
        }
    }

def log_node(tool_name, position_x=4):
    return {
        "id": nid(tool_name, "log"),
        "name": "Log to sys_tool_calls",
        "type": "n8n-nodes-base.postgres",
        "typeVersion": 2.5,
        "position": pos(position_x),
        "credentials": {"postgres": {"id": CRED_SUPABASE, "name": "Supabase {CLIENTE}"}},
        "parameters": {
            "operation": "executeQuery",
            "query": f"""INSERT INTO sys_tool_calls (session_id, tool_name, input_payload, output_payload, status, duration_ms)
VALUES ($1, '{tool_name}', $2::jsonb, $3::jsonb, $4, $5)""",
            "options": {
                # 🔑 CRÍTICO: queryReplacement como ARRAY literal, NO CSV concat
                "queryReplacement": "={{ ["
                    "$('Execute Workflow Trigger').first().json.session_id || 'unknown', "
                    "JSON.stringify($('Execute Workflow Trigger').first().json), "
                    "JSON.stringify($json), "
                    "$json.status || 'success', "
                    "$json.duration_ms || 0"
                "] }}"
            },
            "continueOnFail": True
        }
    }

def airtable_search(tool_name, name, table_id, view_id=None, filter_formula="", limit=10, position_x=2):
    params = {
        "operation": "search",
        "base": {"__rl": True, "mode": "list", "value": BASE_ID},
        "table": {"__rl": True, "mode": "list", "value": table_id},
        "filterByFormula": filter_formula,
        "limit": limit,
        "options": {}
    }
    if view_id:
        params["view"] = {"__rl": True, "mode": "list", "value": view_id}
    return {
        "id": nid(tool_name, name.lower().replace(" ", "-")),
        "name": name,
        "type": "n8n-nodes-base.airtable",
        "typeVersion": 2.1,
        "position": pos(position_x),
        "credentials": {"airtableTokenApi": {"id": CRED_AIRTABLE, "name": "Airtable {CLIENTE}"}},
        "parameters": params
    }
```

Para cada tool:
1. Construir `trigger_node` con los `jsonExample` que declara los args
2. Construir `validate_code` específico (qué args son obligatorios)
3. Construir `airtable_node` según la `lógica_de_búsqueda`
4. Construir `format_code` específico (output al contrato `{status, data, message_to_agent, trace_id}`)
5. Agregar `log_node` estándar
6. Agregar Set node de Return
7. Conectar: Trigger → Validate → Airtable → Format → Log → Return

### Paso 3 — Caso especial: tool de escritura (`notificar_lead`)

Si `lógica_de_búsqueda = create-and-notify`, el patrón es:

```
Trigger → Validate (require nombre+tel+ubic+equipo) → IF skip?
  ├── (true) → Return ERROR
  └── (false) → Gmail Send → Telegram Send → Postgres Update session_state → Format → Log → Return
```

Adicionales:
- Gmail OAuth2 con credential placeholder `<<<COMPLETAR_GMAIL_CRED_ID>>>`
- Telegram con placeholder de chat ID
- Postgres Update con `queryReplacement` array (igual patrón que log)
- Deriva zona desde ubicación (regex CABA/GBA/Interior)
- Deriva línea desde equipo_o_aplicacion (mapping configurable)

### Paso 4 — Guardar JSONs

Path: `clients/{XXX}_{Nombre}/03_workflows/{cliente_lower}-tool-{nombre}-v1.json`

### Paso 5 — Generar doc setup F4

Crear `clients/{XXX}_{Nombre}/06_docs/f4-tools-setup.md` con:
- Tabla resumen de tools (nombre, operación, credentials requeridos)
- Pasos de import (~15 min)
- Cableo de credentials (~20 min)
- Activación (toggle Active en cada uno — CRÍTICO: sin esto el main no puede invocarlas)
- Smoke tests por tool con JSON input + resultado esperado
- Verificación de logs en `sys_tool_calls`
- Limitaciones conocidas v1 (sin sub-agente gpt-4.1-mini en `buscar_producto`, matching por keywords en `consultar_aplicacion` y `consultar_faq`, etc.)

---

## Reglas CRÍTICAS (lecciones de SYS)

| Regla | Por qué |
|---|---|
| **Todos los `type` del schema = `string`** | Zod rechaza `array`/`boolean`/`number` si el LLM no genera valores exactos. La conversión la hace el sub-workflow internamente. |
| **`queryReplacement` Postgres = array literal `={{ [A,B,C] }}`** | La sintaxis CSV concatenada (`={{ A }}, ={{ B }}`) se rompe cuando los valores tienen comas internas (JSON.stringify). |
| **`continueOnFail: true` en Log y nodos de notificación** | Si Postgres o Gmail caen, la tool debe retornar igual (no romper al agente). |
| **Contract de output uniforme** | `{status: RESOLVED | AMBIGUOUS | NOT_FOUND | ERROR, data, message_to_agent, trace_id}`. El LLM lee `status` y `message_to_agent` para guiar su respuesta. |
| **Hardcoded constants** (Opción C) | Si el plan n8n no tiene Variables UI, los IDs y URLs van hardcoded en cada workflow. Único catálogo en `06_docs/airtable-credentials.md`. |

---

## Smoke test del skill

Después de generar + el usuario importar y cablear:

1. Por cada sub-workflow, click "Execute workflow" en el editor con su JSON example.
2. Verificar que retorna el contrato esperado.
3. Query a Supabase: `SELECT tool_name, status FROM sys_tool_calls ORDER BY created_at DESC LIMIT 10;` — debe mostrar las invocaciones.

---

## Composición

**Invoca:** ninguno.
**Es invocado por:** `bootstrap-agente-etapa-2` (S1) como paso F4.
**Precede a:** `integrar-tools-al-main-fromai` (S4).
**Consume del cliente:** `06_docs/tools-spec-v1.md`, `06_docs/airtable-credentials.md`, schema Airtable.

---

## Notas operativas

- **Tiempo estimado:** 2-3h del asistente (vs 10-15h sin skill).
- **Re-importar destruye config si se modificó manualmente en UI.** NO regenerar JSON después de la primera vez sin avisar al usuario.
- **Tool de escritura (`notificar_lead`) es la más compleja** — generarla aparte si es la primera vez.
- **Sub-agente gpt-4.1-mini interno (en `buscar_producto`)** queda para v1.1 si el matching simple no alcanza.
