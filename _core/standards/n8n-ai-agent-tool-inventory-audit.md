# Estándar interno — Auditoría de inventario `ai_tool` en agentes conversacionales n8n

**Origen:** post-incidente TFO 2026-06-21 (calendar overlaps por tool rogue). Doc del incidente: `clients/TFO_TOFO/06_docs/incidente-calendar-overlaps-2026-06-21.md`.

**Aplica a:** cualquier agente conversacional la agencia implementado con `@n8n/n8n-nodes-langchain.agent` o `@n8n/n8n-nodes-langchain.agentTool` (subagentes), independiente del cliente o del nicho.

---

## Por qué este estándar existe

Los AI Agents de n8n exponen al LLM **todas** las tools que están conectadas vía `ai_tool` — sin importar si tienen `toolDescription` significativa, sin importar si están `disabled` (en algunos casos siguen siendo visibles), sin importar si quedaron como zombies de iteraciones de build pasadas. El LLM las ve, las pondera, y puede elegir invocar cualquiera.

Cuando hay **2 tools que hacen funcionalmente lo mismo** (ej. `check_disponibilidad` vía sub-workflow vs `Create an event in Google Calendar` directa), el LLM tiende a elegir la más simple. Si la simple es la "insegura" (sin chequeos, sin guards), el bug es silencioso y solo se detecta cuando el cliente reporta síntomas downstream.

Este estándar codifica el patrón "1 tool = 1 propósito explícito y único" para evitar que iteraciones de build dejen tools rogue cableadas.

---

## Regla de oro

> **Toda tool cableada al AI Agent debe tener `toolDescription` no vacía y un propósito único. Si dos tools cubren el mismo propósito, una de las dos queda desconectada. Si una tool no se usa, queda desconectada (no solo `disabled: true` — desconectada del wire `ai_tool`).**

---

## Cuándo aplicar el checklist

1. **Después de cada bump significativo de un sub-workflow** (ej. de `check_disponibilidad v1` a `v2`, de `consultar_catalogo v1` a `v2`). El bump puede dejar versiones viejas cableadas en paralelo. Auditar el inventario de tools del agente principal para verificar que solo apunta al sub-workflow nuevo.
2. **Después de consolidar funcionalidad** (ej. mover la creación de Calendar + Zoom de tools separadas a un único sub-workflow atómico). Verificar que las tools individuales que ya no se usan estén desconectadas, no solo disabled.
3. **Como auditoría rutinaria mensual** para clientes en producción con agentes conversacionales activos. Estimado: 10-15 min por cliente.
4. **Cuando un bug "supuestamente arreglado" reaparece.** Antes de bumpear el prompt por enésima vez, mirar el wiring.

---

## Checklist de auditoría (paso a paso)

### Paso 1 — Abrir el workflow en n8n y localizar el AI Agent principal

- Abrir el workflow del agente en n8n.
- Localizar el nodo `@n8n/n8n-nodes-langchain.agent` (el agente principal — usualmente llamado "Agente de Derivación", "AI Agent", "Agente Principal", o similar).
- Si el workflow tiene subagentes (`@n8n/n8n-nodes-langchain.agentTool`), repetir la auditoría para cada uno.

### Paso 2 — Listar todas las conexiones `ai_tool`

- Click sobre el AI Agent. En el canvas, ver las líneas de conexión a cada tool (color distinto a las `main`).
- Alternativamente, descargar el JSON del workflow (`Download` → guardar como `.json`) y grep:

```bash
jq '.connections | to_entries | map(select(.value.ai_tool != null)) | map({from: .key, tools: .value.ai_tool})' workflow.json
```

O más simple: buscar todas las apariciones de `"type": "ai_tool"` en el JSON y enumerar los `node` source.

### Paso 3 — Para cada tool cableada, llenar la tabla:

| Nombre del nodo | `type` | `toolDescription` (vacía/llena, citar 1 línea) | `disabled` | `workflowId` (si aplica) | Propósito declarado |
|-----------------|--------|------------------------------------------------|------------|---------------------------|---------------------|

### Paso 4 — Aplicar las 4 preguntas de auditoría

Para cada tool del inventario:

1. **¿Tiene `toolDescription` no vacía?**
   - Sí → OK, seguir.
   - No → ⚠️ **Zombie de bajo riesgo.** Acción: agregar descripción O desconectar.

2. **¿Su `type` es un nodo "tool-puro" de servicio externo (googleCalendarTool, zoomTool, googleSheetsTool, googleDocsTool, gmailTool, etc.) y existe en el inventario otra tool — usualmente un `toolWorkflow` — que cubre la misma funcionalidad de forma controlada (con chequeos, validaciones, logging)?**
   - Sí → 🚨 **Tool rogue crítica.** Acción: desconectar inmediatamente. La tool de servicio externo standalone le da al LLM una vía paralela sin guards.
   - No → seguir.

3. **¿Está `disabled: true` pero sigue cableada como `ai_tool`?**
   - Sí → ⚠️ **Zombie.** Acción: desconectar el wire `ai_tool`. Si el nodo está disabled, no debería estar visible para el LLM. Algunos plugins de n8n siguen exponiéndolas pese al disabled — mejor no confiar.
   - No → seguir.

4. **¿El nombre del nodo es sospechoso (`test1`, `asdf`, `registrarrrrrrr`, sufijos numéricos sin sentido)?**
   - Sí → muy probable zombie de build. Validar uso o desconectar.
   - No → seguir.

### Paso 5 — Decisión por tool

Después de las 4 preguntas, cada tool cae en una de 3 categorías:

| Categoría | Acción |
|-----------|--------|
| ✅ **LIMPIA** — tiene descripción + propósito único + uso confirmado | Dejar cableada. |
| ⚠️ **ZOMBIE** — sin descripción, o disabled, o nombre sospechoso, sin riesgo crítico | Agregar descripción O desconectar (preferir desconectar si el uso es dudoso). |
| 🚨 **ROGUE CRÍTICA** — tool de servicio externo standalone que duplica funcionalidad de un sub-workflow seguro | Desconectar **inmediatamente** + reforzar el prompt con regla absoluta prohibiendo invocarla. |

### Paso 6 — Aplicar los cambios

- **Desconectar:** click sobre la línea `ai_tool` que va de la tool al AI Agent → ❌ delete (borra solo la conexión, no el nodo).
- **NO eliminar el nodo todavía** — dejarlo huérfano en el canvas como rollback fácil.
- Re-activar el workflow, smoke test.
- Si todo OK durante 1-3 días, segunda pasada de cleanup elimina los nodos huérfanos.

### Paso 7 — Documentar la auditoría

Crear o actualizar en el cliente:
- `clients/[XXX]/06_docs/auditoria-tools-ai-agent-YYYY-MM-DD.md` con la tabla del Paso 3 + categorización + cambios aplicados.
- Si hubo cambios → export del JSON post-fix y commit al repo.

---

## Anti-patterns a evitar

### Anti-pattern 1: tool de servicio externo cableada en paralelo a un sub-workflow

❌ Mal: el AI Agent tiene cableados `check_disponibilidad` (toolWorkflow → sub-workflow con guards) **Y** `Create an event in Google Calendar` (googleCalendarTool standalone).

✅ Bien: solo `check_disponibilidad` cableado. El sub-workflow internamente usa el nodo `Create an event in Google Calendar` como paso final.

**Razón:** el LLM ve los 2 caminos y elige el directo. Las guards del sub-workflow se vuelven decorativas.

### Anti-pattern 2: tool cableada sin `toolDescription`

❌ Mal: nodo `googleCalendarTool` cableado con campo `toolDescription` vacío.

✅ Bien: descripción explícita tipo `"Úsala SOLO si check_disponibilidad falla con error técnico. NUNCA como atajo."` — y mejor desconectarla del todo.

**Razón:** sin descripción, el LLM la prueba por curiosidad. Con descripción restrictiva, al menos tiene chance de respetarla.

### Anti-pattern 3: tools con sufijos numéricos sin documentar

❌ Mal: `registrar`, `registrar1`, `registrar2`, `registrarrrrrrr` cableados todos.

✅ Bien: un solo `registrar` cableado, los duplicados eliminados o desconectados.

**Razón:** confusión del LLM + drift de comportamiento + búsqueda exponencial.

### Anti-pattern 4: confiar en `disabled: true` para "ocultar" tools

❌ Mal: dejar `disabled: true` la tool zombie pero seguir cableada como `ai_tool`.

✅ Bien: desconectar el wire `ai_tool`. Si querés mantener el nodo como referencia futura, dejalo en el canvas pero sin conexión al AI Agent.

**Razón:** algunos plugins de n8n no respetan `disabled` en el listado expuesto al LLM. Mejor garantizar invisibilidad cortando el wire.

---

## Belt-and-suspenders: regla en el prompt

Para tools especialmente críticas (creación de citas, envío de mensajes externos, pagos, escalamiento), agregar al **§0 REGLAS ABSOLUTAS** del prompt una regla explícita:

> **REGLA ABSOLUTA #N — La ÚNICA tool autorizada para [propósito] es `[tool_canonica]`.** PROHIBIDO invocar cualquier otra tool que toque [servicio externo] directamente, aunque aparezca en tu lista de tools disponibles.

Esto es la segunda defensa. Si la cirugía de n8n falla o un build futuro re-introduce el rogue, el prompt mismo sigue cumpliendo.

Ejemplo aplicado: TFO B2B v1.15 REGLA #4 (calendar) — ver `clients/TFO_TOFO/04_agents/agente-tofo-b2b-system-prompt.md`.

---

## Plantilla del reporte de auditoría

```markdown
# Auditoría de inventario `ai_tool` — [Cliente XXX] — YYYY-MM-DD

**Workflow auditado:** [nombre del workflow] (id [...], vivo en n8n)
**Auditor:** [nombre]
**Snapshot pre-auditoría:** clients/XXX/03_workflows/[nombre]-snapshot-YYYY-MM-DD.json

## Inventario por agente

### [Agente Principal / Nombre]

| # | Tool | Type | Descripción | Disabled | Categoría | Acción |
|---|------|------|-------------|----------|-----------|--------|
| 1 | ... | ... | ... | ... | ✅/⚠️/🚨 | ... |

### [Subagente 1]

(idem)

## Cambios aplicados

| # | Acción | Tool | Razón |
|---|--------|------|-------|
| 1 | Desconectar `ai_tool` | [nombre] | [rogue / zombie / etc.] |

## Smoke post-fix

- [ ] Workflow re-activado sin errores
- [ ] 1 turno de smoke con lead simulado pasa OK
- [ ] Inventario post-fix coincide con plan
- [ ] JSON exportado y commiteado al repo

## Follow-up

- [ ] Eliminación completa de nodos desconectados (segunda pasada, post-72hs)
- [ ] Actualizar prompt con REGLA ABSOLUTA si aplica
- [ ] CLAUDE.md actualizado
```

---

## Referencias

- Incidente fundacional: `clients/TFO_TOFO/06_docs/incidente-calendar-overlaps-2026-06-21.md`
- Guía manual aplicada: `clients/TFO_TOFO/06_docs/guia-fix-tools-rogue-calendar-2026-06-21.md`
- Estándar relacionado: `_core/standards/n8n-data-references.md` (referencias `$('NodeName')` vs `$json`).
- Estándar relacionado: `_core/standards/manychat-integration-pattern.md` (naming canónico de custom fields).
