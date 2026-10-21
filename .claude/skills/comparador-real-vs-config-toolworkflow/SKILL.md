---
name: comparador-real-vs-config-toolworkflow
description: >
  Usar este skill cuando hay sospecha de drift entre lo que está REAL en n8n y
  lo que ESPERAMOS según docs locales (`f5-tools-fromai-config.md`, `tools-spec-v1.md`).
  Se activa con frases como "comparar config real vs esperada", "detectar drift",
  "qué cambió en el agente", "validar que la config esté como dice el doc". Útil
  cuando el usuario configuró tools manualmente y no se sabe qué quedó mal vs OK.
---

# Skill: Comparador Drift Config Real vs Esperada

## Descripción

Compara la configuración REAL de los toolWorkflow nodes en n8n (vía MCP) contra lo que ESPERAMOS según el doc `f5-tools-fromai-config.md`. Reporta drift por tool y por field con ✓/✗.

Diferente a `inspector-bugs-toolworkflow-n8n` (S6):
- S6 detecta **bugs absolutos** (sintaxis mal, types problemáticos, etc.) sin necesitar comparar con docs.
- S11 detecta **drift** entre lo que decidimos en docs y lo que está en n8n.

---

## Cuándo invocarlo

- Después de que el usuario hizo cambios manuales en UI
- Antes de un release a producción
- Después de un incidente para verificar que la config quedó alineada
- Cuando hay sospecha de que "alguien tocó algo"

## Cuándo NO invocarlo

- No hay doc `f5-tools-fromai-config.md` aún (correr `generar-doc-fromai-tools-manual` primero)
- Drift conocido y aceptado (no tiene sentido reportar lo obvio)

---

## Inputs requeridos

1. **Workflow ID** del main en n8n
2. **Path al doc esperado** (default: `clients/{XXX}_*/06_docs/f5-tools-fromai-config.md`)

---

## Proceso

### Paso 1 — Get workflow details via MCP n8n

```python
workflow = mcp__n8n__get_workflow_details(workflowId=WID)
```

### Paso 2 — Parsear el doc esperado

Leer `f5-tools-fromai-config.md` y construir dict:
```python
expected = {
    "consultar_tecnologia": {
        "description": "Consulta ficha técnica...",
        "fields": {
            "tecnologia": "OBLIGATORIO: nombre exacto...",
            "aspecto": "Opcional: descripcion | ..."
        }
    },
    ...
}
```

### Paso 3 — Comparar tool por tool

Por cada tool en el workflow real:
- ✓/✗ Description matchea
- ✓/✗ Cantidad de fields matchea
- ✓/✗ Cada field name está en esperado
- ✓/✗ Type es `string`
- ✓/✗ Required es `false`
- ✓/✗ Descripción de `$fromAI` matchea (al menos al 80% por keyword match — no exact)
- ✓/✗ Comment auto-gen presente
- ✓/✗ `session_id` con expresión n8n correcta

### Paso 4 — Reporte de drift

```
COMPARACIÓN REAL vs ESPERADA
═══════════════════════════════════════

✓ consultar_tecnologia: OK
✓ consultar_faq: OK
⚠ buscar_equipo: 2 diffs
   - field 'tecnologia' descripción cambió:
     Esperado: "Opcional: DTF Textil | DTF UV | UV | Sublimación | Eco-Solvente | Solvente | RISO | IDL Láser | Corte"
     Real:     "Opcional: DTF Textil | UV | Sublimación"  ← TRUNCADA
   - field 'exclude_models' falta comment auto-generated
✗ notificar_lead: 1 BUG
   - field 'urgencia' type='boolean' (debe ser 'string')

RESUMEN: 7/9 OK | 1 con diffs menores | 1 con bug crítico
```

### Paso 5 — Sugerir acción

- ✓ tool OK → ninguna acción
- ⚠ diffs menores → recomendar actualizar el doc esperado o reconfigurar en UI según preferencia
- ✗ bugs críticos → derivar a `inspector-bugs-toolworkflow-n8n` (S6) para fix exacto

---

## Composición

**Invoca:** `mcp__n8n__get_workflow_details`.
**Es invocado por:** F7 testing, post-edición manual, pre-release.
**Si detecta bugs:** derivar a S6.

---

## Notas operativas

- **Tiempo:** 5-10 min del skill.
- **El "ground truth" es el doc, NO n8n.** Si el doc no está al día, los drift detectados pueden ser falsos positivos. Mantener el doc actualizado es responsabilidad del usuario tras cada cambio aceptado.
- **Descripción match al 80% por keyword** es heurística — no penaliza diferencias menores de redacción, sí penaliza truncamientos.
