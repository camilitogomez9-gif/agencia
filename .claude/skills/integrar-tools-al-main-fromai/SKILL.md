---
name: integrar-tools-al-main-fromai
description: >
  Usar este skill cuando ya existen N sub-workflows tools (post F4) y hay que
  integrarlos al main workflow como toolWorkflow nodes con $fromAI() correctamente
  configurado. Se activa con frases como "integrar tools al main", "armar v0.2 del
  agente X", "conectar las herramientas al agente principal", "F5 cliente X". Evita
  TODOS los bugs descubiertos en SYS (schema strict, sintaxis $fromAI, types incorrectos).
  Stack: n8n LangChain. Genera v0.2 del main + doc operativo de config manual.
---

# Skill: Integrar Tools al Main con `$fromAI()` correcto

## Descripción

Genera la versión v0.2 (o vN+1) del main workflow agregando N `toolWorkflow` nodes ya configurados con `$fromAI()` que evita los 8 bugs descubiertos en SYS:

1. Schema strict de Zod (types `array`/`boolean`/`number` que rechazan inputs)
2. Sintaxis `$fromAI()` con quotes mezcladas (mismatched `"` vs `` ` ``)
3. Falta del comment `/*n8n-auto-generated-fromAI-override*/`
4. Descripciones vacías o truncadas
5. `attemptToConvertTypes: false`
6. `matchingColumns` mal seteado
7. `session_id` como `$fromAI` (debe ser expresión n8n directa del Normalize Payload)
8. `required: true` que rompe cuando el LLM omite el campo

---

## Cuándo invocarlo

- F5 del Plan Maestro
- Existen los 9 sub-workflows tools (F4 ✅) y están **Active**
- Existe main workflow v0.1 sin tools

## Cuándo NO invocarlo

- Re-integración post UI manual (usar `inspector-bugs-toolworkflow-n8n` para detectar drift sin destruir config)
- Quitar 1 tool del set existente (editar en UI directo)

---

## Inputs requeridos

1. **Main workflow JSON v0.1** (path)
2. **Lista de tools con specs** (mismo input de `generar-subworkflows-tools-n8n`):
   - Por cada tool: `name`, `description`, `schema` (args con descripción)
3. **Workflow IDs de los sub-workflows** en n8n (post-import del cliente)
   - Si no los tiene a mano: dejar placeholder `<<<COMPLETAR_WORKFLOW_ID>>>` y dar instrucción explícita al usuario para cablear via dropdown

---

## Proceso

### Paso 1 — Cargar v0.1 + agregar N toolWorkflow nodes

Por cada tool, generar un nodo con esta estructura **exacta** (las 8 reglas anti-bugs):

```python
def tool_node(name, description, workflow_id, workflow_cached_name, schema_dict):
    """
    schema_dict = {
        'arg_name': 'descripción del LLM con OBLIGATORIO o Opcional al inicio',
        ...
    }
    """
    schema = []
    value_obj = {}

    # 1. session_id como expresión directa (NO $fromAI)
    schema.append({
        "id": "session_id", "displayName": "session_id",
        "required": False, "defaultMatch": False, "display": True,
        "canBeUsedToMatch": False, "type": "string"
    })
    value_obj["session_id"] = "={{ $('Normalize Payload').item.json.leadIdentifier }}"

    # 2. Resto de args: $fromAI con la sintaxis correcta
    for arg_name, desc in schema_dict.items():
        schema.append({
            "id": arg_name, "displayName": arg_name,
            "required": False,                  # ⚠ siempre False
            "defaultMatch": False, "display": True,
            "canBeUsedToMatch": False,
            "type": "string"                     # ⚠ siempre string
        })
        # ⚠ Sintaxis CRÍTICA: backticks en desc, simple quotes en name y type, comment auto-gen
        desc_escaped = desc.replace("`", "\\`")
        value_obj[arg_name] = (
            f"={{{{ /*n8n-auto-generated-fromAI-override*/ "
            f"$fromAI('{arg_name}', `{desc_escaped}`, 'string') }}}}"
        )

    return {
        "id": nid(name),
        "name": name,
        "type": "@n8n/n8n-nodes-langchain.toolWorkflow",
        "typeVersion": 2.2,
        "position": [x_offset, y_below_agent],
        "parameters": {
            "name": name,
            "description": description,
            "workflowId": {
                "__rl": True,
                "value": workflow_id or "<<<COMPLETAR_WORKFLOW_ID>>>",
                "mode": "list",
                "cachedResultName": workflow_cached_name
            },
            "workflowInputs": {
                "mappingMode": "defineBelow",
                "value": value_obj,
                "matchingColumns": [],            # ⚠ siempre vacío
                "schema": schema,
                "attemptToConvertTypes": True,    # ⚠ siempre true
                "convertFieldsToString": False
            }
        },
        "notes": f"Cablear workflow ID via dropdown → seleccionar '{workflow_cached_name}' si está en placeholder."
    }
```

### Paso 2 — Conectar cada toolWorkflow al AI Agent

```python
for tool in tools:
    workflow["connections"][tool["name"]] = {
        "ai_tool": [[{"node": "AI Agent", "type": "ai_tool", "index": 0}]]
    }
```

### Paso 3 — Guardar v0.2

Path: `clients/{XXX}_{Nombre}/03_workflows/{cliente_lower}-agente-principal-v0.2.json`

### Paso 4 — Generar doc operativo

**Crítico:** generar `clients/{XXX}_{Nombre}/06_docs/f5-tools-fromai-config.md` con la config manual de cada tool para que el usuario pueda re-configurar si el re-import destruye algo.

Estructura del doc por cada tool:
- **Description del tool** (para campo arriba del node)
- **Tabla de parámetros From AI**: Name | Descripción para `$fromAI`
- **Campo adicional**: `session_id` con valor `={{ $('Normalize Payload').item.json.leadIdentifier }}`
- **Settings**: `Mapping Mode: Define Below`, `Attempt to Convert Types: ON`, `Convert Fields to String: OFF`
- **Notas críticas**:
  - Type de cada arg = `string` (SIEMPRE, incluso si lógicamente fuera array/boolean)
  - Required = OFF (SIEMPRE — la "obligatoriedad" la marca la palabra "OBLIGATORIO" en la descripción)
  - Sintaxis correcta: backticks en descripción, simple quotes en name y type, comment auto-gen presente

### Paso 5 — Reportar al usuario

Devolver:
- Path del v0.2 generado
- Path del doc f5-tools-fromai-config.md
- Pasos para importar (delete v0.1, import v0.2, cablear 2 creds + N workflow IDs, activar)
- Smoke test sugerido: 1 case por tool

---

## Reglas anti-bugs (las 8 lecciones SYS)

| Regla | Anti-bug |
|---|---|
| `type: string` en TODOS los schema fields | Zod rechaza arrays/booleans/numbers |
| `required: false` en TODOS | LLM puede omitir args y no debe fallar |
| `attemptToConvertTypes: true` | n8n convierte si LLM se equivoca |
| `matchingColumns: []` | El array vacío evita lógica de auto-match incorrecta |
| Sintaxis `$fromAI('name', \`desc\`, 'string')` — **simple quotes** en name/type, **backticks** en descripción | Las descripciones tienen comas, parens, comillas — solo backticks las soportan sin escape |
| Comment `/*n8n-auto-generated-fromAI-override*/` antes del `$fromAI` | n8n lo trata como "manual" sin el comment, comportamiento diferente |
| `session_id` como expresión n8n directa (no `$fromAI`) | session_id es contexto, NO decisión del LLM |
| Descripciones con `OBLIGATORIO:` o `Opcional:` al inicio + lista de valores válidos | Le dice al LLM qué pasar |

---

## Smoke test del skill

Después de importar + cablear + activar:

```bash
# Caso simple: el LLM debe invocar una tool básica
curl -X POST .../webhook/{cliente}-agent \
  -H "Content-Type: application/json" \
  -d '{"canal":"test","subscriber_id":"smoke-fromai","mensaje":"Qué es {alguna_categoria_del_cliente}?"}'
```

Verificar en Supabase:
```sql
SELECT tool_name, status FROM sys_tool_calls
WHERE session_id = 'test_smoke-fromai'
ORDER BY created_at DESC LIMIT 5;
```

Debe mostrar la tool invocada con `status='success'`.

Si NO hay registros: el LLM no invocó la tool — revisar descripción del tool.
Si hay `status='error'`: revisar el sub-workflow.
Si el webhook responde `{}` vacío: invocar `inspector-bugs-toolworkflow-n8n` para detectar drift en config.

---

## Composición

**Invoca:** ninguno.
**Precedido por:** `generar-subworkflows-tools-n8n` (S3).
**Sucedido por:** `smoke-test-agente-webhook` (S5) y, si falla, `inspector-bugs-toolworkflow-n8n` (S6).
**Es invocado por:** `bootstrap-agente-etapa-2` (S1) como paso F5.

---

## Notas operativas

- **NO re-importar tras config manual.** Si después del primer import el usuario tocó UI, el v0.2 que se genere por segunda vez destruye su trabajo. En ese caso usar `comparador-real-vs-config-toolworkflow` (S11) para detectar drift.
- **Workflow IDs como dropdown:** si no se tienen los IDs, el JSON queda con placeholder y el `cachedResultName` ayuda a que el usuario los seleccione visualmente en el dropdown de n8n.
- **typeVersion 2.2** es la testeada. Versiones distintas pueden cambiar la forma de `workflowInputs`.
- **El doc `f5-tools-fromai-config.md` es la fuente de verdad** para re-configurar manualmente. Mantenerlo actualizado.
