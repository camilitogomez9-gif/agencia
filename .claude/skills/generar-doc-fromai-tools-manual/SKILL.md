---
name: generar-doc-fromai-tools-manual
description: >
  Usar este skill cuando hay que generar el doc operativo `f5-tools-fromai-config.md`
  que sirve como source-of-truth para reconfigurar manualmente N toolWorkflow nodes
  en la UI de n8n (cuando re-import los rompe). Se activa con frases como "doc de
  config $fromAI", "guía manual de tools", "doc para Edgardo de la config", "armar
  guía para reconfigurar tools manualmente". Generaliza el patrón validado en SYS F5.
---

# Skill: Generar Doc Operativo Config $fromAI Manual

## Descripción

Genera el doc operativo `f5-tools-fromai-config.md` que documenta la config exacta esperada de cada toolWorkflow node del main workflow. Es el **source-of-truth para reconfigurar manualmente** cuando re-importar el JSON destruye config en n8n (limitación conocida).

Contenido del doc:
- Procedimiento general (Description del tool, Workflow Inputs settings)
- Por cada tool: tabla de parámetros From AI (name | descripción para `$fromAI`)
- Campo extra obligatorio: `session_id` con expresión n8n directa
- Reglas críticas: type=string, required=OFF, attemptToConvertTypes=ON, backticks en descripción

---

## Cuándo invocarlo

- Después de `integrar-tools-al-main-fromai` (S4) para entregar el doc al usuario
- Cuando el usuario va a re-configurar manualmente tras un re-import accidental
- Cuando se agregan/modifican tools al set existente

## Cuándo NO invocarlo

- No hay tools definidas todavía
- El cliente solo tiene 1-2 tools (overkill, hacerlo a mano)

---

## Inputs requeridos

1. **Lista de tools con specs** (igual a S3/S4): `name`, `description`, `schema` (args con descripción).
2. **Cliente ID + nombre**

---

## Proceso

### Paso 1 — Generar markdown estructurado

Por cada tool, generar una sección:

```markdown
## Tool N: `nombre_tool`

**Description del tool** (campo "Description" del toolWorkflow node):

\`\`\`
{descripción completa del tool}
\`\`\`

**Parámetros (todos type=string, required=OFF):**

| Name | Descripción para $fromAI |
|---|---|
| `arg1` | `OBLIGATORIO: descripción completa con valores válidos` |
| `arg2` | `Opcional: descripción` |

**Campo adicional (NO es From AI — es contexto):**

| Name | Value (expresión n8n directa) |
|---|---|
| `session_id` | `={{ $('Normalize Payload').item.json.leadIdentifier }}` |
```

### Paso 2 — Agregar header con procedimiento general

Al inicio del doc:
- Por qué este doc existe (re-import destruye config)
- Procedimiento por cada tool (Description → Workflow Inputs settings → 2 tipos de fields)
- Reglas críticas que el usuario debe recordar SIEMPRE

### Paso 3 — Agregar sección "Patrón general"

```markdown
## Patrón general de $fromAI correcto

Toda expresión `$fromAI` válida tiene 4 elementos invariantes:

\`\`\`js
={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('NAME', \`DESC\`, 'string') }}
\`\`\`

| Elemento | Valor correcto |
|---|---|
| Comentario | `/*n8n-auto-generated-fromAI-override*/` |
| Primer arg (name) | `'NAME'` con quotes simples |
| Segundo arg (description) | `` `DESC` `` con backticks |
| Tercer arg (type) | `'string'` con quotes simples |
```

### Paso 4 — Guardar el doc

Path: `clients/{XXX}_{Nombre}/06_docs/f5-tools-fromai-config.md`

### Paso 5 — Reportar al usuario

Output:
- Path del doc
- N tools cubiertas
- Recordatorio: este doc es source-of-truth — si se agrega/modifica una tool en UI, actualizar acá

---

## Composición

**Invocado por:** `integrar-tools-al-main-fromai` (S4) automáticamente, o standalone cuando hay drift de config.
**Relacionado:** `inspector-bugs-toolworkflow-n8n` (S6) — usa este doc como ground-truth.

---

## Notas operativas

- **Tiempo:** 10-15 min del skill.
- **Mantenerlo actualizado** es la convención. Si el usuario cambia una descripción en UI, debe reflejarlo acá.
- **El doc puede subirse a Notion** para que el cliente (Edgardo, en caso SYS) lo vea sin necesitar acceso al repo.
