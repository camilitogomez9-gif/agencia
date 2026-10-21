---
name: inspector-bugs-toolworkflow-n8n
description: >
  Usar este skill cuando un agente conversacional en n8n devuelve respuestas
  vacías {}, errores "Received tool input did not match expected schema", tools que
  no se invocan, o cualquier síntoma de bug en toolWorkflow nodes. Se activa con
  frases como "el agente no responde", "tool no se invoca", "schema error en n8n",
  "diagnosticar bugs del agente X", "qué está roto en v0.2". Inspecciona via MCP de
  n8n + detecta los 8 bugs típicos descubiertos en SYS + reporta fix exacto.
---

# Skill: Inspector de Bugs Toolworkflow n8n (via MCP)

## Descripción

Inspecciona la configuración REAL de un workflow n8n (no la que asumimos en docs) vía MCP de n8n y detecta los 8 bugs típicos que causan "Received tool input did not match expected schema" o respuestas vacías `{}`.

**Bugs que detecta:**

| # | Bug | Síntoma | Fix |
|---|---|---|---|
| B1 | Schema field con `type: array`/`boolean`/`number` | Zod schema mismatch | Cambiar todos a `string` |
| B2 | `$fromAI('name', ..., 'array'|'json'|'boolean'|'number')` — tipo en el 3er arg ≠ `string` | LangChain rechaza el call | Cambiar a `'string'` |
| B3 | Comillas mezcladas en `$fromAI` (ej. `"..."` mezclado con `` `...` ``) | SyntaxError JavaScript en runtime | Reescribir con backticks consistentes |
| B4 | Descripción vacía `` ` ` `` en `$fromAI` | LLM no sabe qué pasar | Completar descripción con "OBLIGATORIO: ..." o "Opcional: ..." |
| B5 | Descripción truncada en `$fromAI` (ej. `\`Opcional: Showroom\`` cuando debería ser lista completa) | LLM elige solo el primer valor | Completar lista |
| B6 | Falta comment `/*n8n-auto-generated-fromAI-override*/` | n8n no lo trata como auto-generated | Agregar el comment |
| B7 | `required: true` en schema field | LangChain Zod rechaza si LLM omite | Cambiar a `false` (validación va en sub-workflow) |
| B8 | `matchingColumns` con valores (ej. `["session_id"]`) | Modo de auto-match incorrecto | Cambiar a `[]` vacío |

**También detecta:**
- `attemptToConvertTypes: false` (debe ser `true`)
- `session_id` configurado como `$fromAI` en lugar de expresión n8n directa (`={{ $('Normalize Payload').item.json.leadIdentifier }}`)
- workflowId con placeholder no cableado

---

## Cuándo invocarlo

- Smoke tests E2E devuelven `[Respuesta vacía: {}]` repetidamente
- Ejecuciones de n8n muestran "Received tool input did not match expected schema"
- Tool específica devuelve error silencioso
- Drift sospechoso entre lo planificado y lo que está en n8n
- Después de cualquier cambio manual del usuario en UI

## Cuándo NO invocarlo

- Cuando el agente nunca arrancó (problema de webhook / credentials de OpenAI/Postgres) — verificar manualmente primero
- Cuando el error es en el sub-workflow tool en sí (no en el toolWorkflow node del main) — inspeccionar el sub-workflow directamente
- Cuando MCP de n8n no está conectado — pedir al usuario que lo habilite primero

---

## Inputs requeridos

1. **Workflow ID** del main workflow en n8n (ej. `q9XichjIvN5oigm4`). Si no lo tiene a mano, buscar con `search_workflows` por nombre del cliente.
2. **Conexión MCP n8n activa** (verificar con un `search_workflows` previo)

---

## Proceso

### Paso 1 — Get workflow details via MCP

```python
workflow = mcp__n8n__get_workflow_details(workflowId=WID)
# Output: 50+ KB JSON con todos los nodos y configs
```

Guardar el output en tmp para procesamiento.

### Paso 2 — Filtrar nodos toolWorkflow

```python
import json, re

tools = [n for n in workflow["nodes"]
         if n.get("type") == "@n8n/n8n-nodes-langchain.toolWorkflow"]
```

### Paso 3 — Por cada tool, detectar los 8 bugs

```python
for node in tools:
    name = node.get("name", "?")
    params = node.get("parameters", {})
    wi = params.get("workflowInputs", {})
    issues = []

    # B7: attemptToConvertTypes
    if not wi.get("attemptToConvertTypes"):
        issues.append(("⚠ low", "attemptToConvertTypes: false → activar"))

    # B8: matchingColumns no vacío
    if wi.get("matchingColumns"):
        issues.append(("🔴 high", f"matchingColumns: {wi['matchingColumns']} → debe ser []"))

    # Workflow ID placeholder
    wid = params.get("workflowId", {}).get("value", "")
    if "COMPLETAR" in wid:
        issues.append(("🔴 high", f"workflowId no cableado: {wid}"))

    # B1: schema con types problemáticos
    for s in wi.get("schema", []):
        if s.get("type") not in ("string",):
            issues.append(("🔴 high", f"schema['{s['id']}'].type = '{s['type']}' → debe ser 'string'"))
        if s.get("required"):
            issues.append(("⚠ med", f"schema['{s['id']}'].required = true → debe ser false (validación va al sub-workflow)"))

    # B2, B3, B4, B5, B6: inspeccionar values $fromAI
    for k, v in wi.get("value", {}).items():
        if k == "session_id":
            # Debe ser expresión n8n directa, NO $fromAI
            if "$fromAI" in v:
                issues.append(("🔴 high", f"value['session_id'] usa $fromAI → debe ser expresión: ={{ $('Normalize Payload').item.json.leadIdentifier }}"))
            continue

        # Buscar patrón $fromAI('name', `desc`, 'type')
        m = re.search(r"\$fromAI\(\s*'([^']+)'\s*,\s*([`\"'])([^`\"']*)\2\s*,\s*'([^']+)'\s*\)", v)
        if not m:
            # Patrón no matchea — posible quote mismatch
            if "$fromAI" in v:
                issues.append(("🔴 high", f"value['{k}']: sintaxis $fromAI inválida (probable quote mismatch) → reescribir con backticks"))
            continue

        arg_name, quote_type, desc, fa_type = m.groups()

        # B6: comment auto-gen
        if "/*n8n-auto-generated-fromAI-override*/" not in v:
            issues.append(("⚠ med", f"value['{k}']: falta comment /*n8n-auto-generated-fromAI-override*/"))

        # B3: quotes mezcladas
        if quote_type != "`":
            issues.append(("🔴 high", f"value['{k}']: descripción usa {quote_type} → debe usar backticks"))

        # B2: type ≠ string
        if fa_type != "string":
            issues.append(("🔴 high", f"value['{k}']: $fromAI type='{fa_type}' → debe ser 'string'"))

        # B4: descripción vacía
        if not desc.strip():
            issues.append(("⚠ med", f"value['{k}']: descripción vacía → completar con OBLIGATORIO: ... o Opcional: ..."))

        # B5: descripción truncada (heurística)
        if desc.strip() and len(desc) < 15 and "|" not in desc:
            issues.append(("⚠ med", f"value['{k}']: descripción muy corta ('{desc}'), posible truncamiento"))

    report.append({"tool": name, "issues": issues})
```

### Paso 4 — Reportar al usuario

Output estructurado:

```
ANÁLISIS DEL WORKFLOW q9XichjIvN5oigm4
═══════════════════════════════════════

Tools inspeccionadas: 9
Tools con bugs: 4

┌─ buscar_equipo (3 bugs)
│  🔴 schema['exclude_models'].type = 'array' → cambiar a 'string'
│  🔴 value['exclude_models']: $fromAI type='json' → cambiar a 'string'
│  ⚠  value['marca']: descripción vacía → completar con "Opcional: HUENU | DLICAN | ..."
│
├─ notificar_lead (1 bug)
│  🔴 value['urgencia']: $fromAI type='boolean' → cambiar a 'string'
│
├─ consultar_inventario_usados (1 bug)
│  🔴 value['tipo']: sintaxis $fromAI inválida (quote mismatch: "..." con ` al cierre)
│
└─ 9/9 attemptToConvertTypes: false → activar en todos

PRIORIDAD DE FIX:
1. 🔴 alta (5 bugs) — sin esto el agente seguirá rompiéndose
2. ⚠ media (4 bugs) — degradan el comportamiento pero no rompen
```

### Paso 5 — Generar fix exacto para cada bug

Por cada bug crítico, dar el "antes" y "después" del valor exacto a copiar/pegar en n8n:

```
buscar_equipo.exclude_models — ANTES:
={{ $fromAI('exclude_models', 'Opcional: ...', 'json') }}

buscar_equipo.exclude_models — DESPUÉS:
={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('exclude_models', `Opcional: lista comma-separated de modelos a excluir (ej: HR 1602 ES, DLI-1010)`, 'string') }}
```

---

## Composición

**Invoca:** `mcp__n8n__get_workflow_details`.
**Es invocado por:** smoke test fallido (S5), F7 troubleshooting, post-edición manual del usuario.
**Output útil para:** generar fix exacto, y opcionalmente actualizar el doc `f5-tools-fromai-config.md` con la verdad real del workflow.

---

## Notas operativas

- **NO modificar el workflow directamente.** Este skill solo INSPECCIONA y REPORTA. El usuario aplica los fixes en UI o el asistente puede generar parches via `inspector-bugs-toolworkflow-n8n` + `integrar-tools-al-main-fromai` (S4 con cuidado de no destruir config).
- **Si MCP no devuelve workflow o falla:** verificar que el workflow tenga `availableInMCP: true` en sus settings, y que el ID sea correcto.
- **El reporte se prioriza por severidad:** 🔴 high (bloquea ejecución) > ⚠ med (degrada comportamiento) > 💡 low (nice-to-have).
- **Bugs que NO detecta este skill:** errores en el sub-workflow (queryReplacement Postgres mal, credentials caídas, Airtable schema cambió). Para esos, inspeccionar las executions específicas en n8n.
