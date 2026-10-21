# F5 — Main Workflow v0.2 con 9 Tools integradas

> **Workflow:** `clients/SYS_SistemasYSoluciones/03_workflows/sys-agente-principal-v0.2.json`
> **Fecha:** 2026-05-29
> **Alcance v0.2:** v0.1 + 9 toolWorkflow nodes conectados al AI Agent. Listo para tests E2E con tools reales.

---

## Diff v0.1 → v0.2

```
v0.1 (10 nodos):
  [Webhook] → [Normalize] → [IF skip] → [Build Context]
    → [AI Agent + Postgres Memory + gpt-4o]
    → [Split] → [Respond]

v0.2 (19 nodos = 10 + 9 tools):
  ... mismo flow principal ...
  [AI Agent] ←─── ai_tool ←─── [9 toolWorkflow nodes]
                                ├─ consultar_tecnologia
                                ├─ consultar_faq
                                ├─ consultar_lineas_priorizadas
                                ├─ consultar_url_tienda
                                ├─ buscar_equipo
                                ├─ consultar_aplicacion
                                ├─ consultar_compatibilidad
                                ├─ consultar_inventario_usados
                                └─ notificar_lead
```

Cada toolWorkflow nodes tiene:
- **name**: el nombre de la tool que el LLM ve (ej. `buscar_equipo`)
- **description**: texto que el LLM usa para decidir cuándo invocarla
- **workflowId**: placeholder `<<<COMPLETAR_WORKFLOW_ID>>>` — vos lo cableás via dropdown
- **workflowInputs.schema**: lista de campos con tipo + required — define los args válidos
- **workflowInputs.value**: cada campo tiene `={{ $fromAI('paramName', 'descripción', 'tipo') }}` — el LLM genera los valores dinámicamente desde el contexto de la conversación

> ⚠️ **Crítico:** los inputs DEBEN venir del LLM (modo "From AI"), no estáticos. Sin esto, las tools recibirían valores vacíos. El JSON v0.2 viene con `$fromAI()` ya cableado en todos los campos. Si en la UI ves valores literales (no expresiones), algo se importó mal — revisá que cada campo muestre `={{ $fromAI(...) }}` o el icono ✨.

---

## Pre-requisito CRÍTICO

**Los 9 sub-workflows tools DEBEN estar Active** (toggle Active arriba-derecha en cada uno). Si no, el AI Agent va a fallar con error "Workflow not found" o "Workflow inactive".

Verificar antes de importar v0.2:
- [ ] `sys-tool-consultar-tecnologia-v1` → Active ✅
- [ ] `sys-tool-consultar-faq-v1` → Active ✅
- [ ] `sys-tool-consultar-lineas-priorizadas-v1` → Active ✅
- [ ] `sys-tool-consultar-url-tienda-v1` → Active ✅
- [ ] `sys-tool-buscar-equipo-v1` → Active ✅
- [ ] `sys-tool-consultar-aplicacion-v1` → Active ✅
- [ ] `sys-tool-consultar-compatibilidad-v1` → Active ✅
- [ ] `sys-tool-consultar-inventario-usados-v1` → Active ✅
- [ ] `sys-tool-notificar-lead-v1` → Active ✅

---

## Paso 1 — Desactivar v0.1 + Importar v0.2 (~5 min)

1. n8n → Workflows → abrir `sys-agente-principal-v0.1` → toggle **Active = OFF** (para liberar el path `/webhook/sys-agent`).
2. Workflows → **Import from File** → seleccionar `sys-agente-principal-v0.2.json`.
3. Renombrarlo si querés mantener nombre exacto.

---

## Paso 2 — Cablear los 9 workflow IDs (~10 min)

Por cada uno de los 9 toolWorkflow nodes (los que están abajo del AI Agent):

1. Click en el nodo (ej. `consultar_tecnologia`).
2. En el panel derecho, sección **"Workflow"** → dropdown → seleccionar el sub-workflow correspondiente del nombre.
3. n8n autocompleta el workflow ID interno.
4. **Save**.

Mapeo rápido (nombre del tool node → workflow a seleccionar):

| Tool node | Sub-workflow a cablear |
|---|---|
| `consultar_tecnologia` | `sys-tool-consultar-tecnologia-v1` |
| `consultar_faq` | `sys-tool-consultar-faq-v1` |
| `consultar_lineas_priorizadas` | `sys-tool-consultar-lineas-priorizadas-v1` |
| `consultar_url_tienda` | `sys-tool-consultar-url-tienda-v1` |
| `buscar_equipo` | `sys-tool-buscar-equipo-v1` |
| `consultar_aplicacion` | `sys-tool-consultar-aplicacion-v1` |
| `consultar_compatibilidad` | `sys-tool-consultar-compatibilidad-v1` |
| `consultar_inventario_usados` | `sys-tool-consultar-inventario-usados-v1` |
| `notificar_lead` | `sys-tool-notificar-lead-v1` |

**Tip:** el `cachedResultName` ya está seteado con el nombre exacto, así que en el dropdown debería aparecer pre-seleccionado o sugerido.

---

## Paso 3 — Reverificar credenciales del main (mismo que v0.1)

- Nodo `OpenAI Chat Model (gpt-4o)` → credencial `OpenAI la agencia` (o como se llame).
- Nodo `Postgres Chat Memory` → credencial `Supabase SYS`.

Si v0.1 tenía esto cableado, v0.2 debería heredarlo. Verificar de todos modos.

---

## Paso 4 — Activar v0.2

Toggle **Active = ON**. El webhook queda disponible en:

```
https://[TU-INSTANCIA-N8N]/webhook/sys-agent
```

(Mismo path que v0.1 — por eso desactivamos v0.1 antes).

---

## Paso 5 — Smoke tests E2E (con tools reales)

### Test E2E-1 — Tool `consultar_tecnologia`

```bash
curl -X POST https://[TU-INSTANCIA-N8N]/webhook/sys-agent \
  -H "Content-Type: application/json" \
  -d '{
    "canal": "test",
    "subscriber_id": "e2e-001",
    "mensaje": "Qué es DTF UV?"
  }'
```

**Esperado:**
- El AI Agent invoca `consultar_tecnologia(tecnologia="DTF UV")`.
- Respuesta integra natural la descripción de DTF UV (objetos rígidos, film + barniz, sin calor).
- Logs en Supabase: nueva fila en `sys_tool_calls` con `tool_name='consultar-tecnologia'`.

### Test E2E-2 — Tool `consultar_aplicacion` → `buscar_equipo` (encadenado)

```bash
curl -X POST https://[TU-INSTANCIA-N8N]/webhook/sys-agent \
  -H "Content-Type: application/json" \
  -d '{
    "canal": "test",
    "subscriber_id": "e2e-002",
    "mensaje": "Necesito estampar gorras y mochilas, qué me conviene?"
  }'
```

**Esperado:**
- AI invoca `consultar_aplicacion(descripcion="estampar gorras y mochilas")` → devuelve DTF Textil.
- Posiblemente también invoca `buscar_equipo(tecnologia="DTF Textil")` para mencionar un modelo.
- Respuesta integra ambas: recomienda DTF Textil + opcionalmente un equipo.
- 2 filas en `sys_tool_calls`.

### Test E2E-3 — Tool `consultar_faq`

```bash
curl -X POST https://[TU-INSTANCIA-N8N]/webhook/sys-agent \
  -H "Content-Type: application/json" \
  -d '{
    "canal": "test",
    "subscriber_id": "e2e-003",
    "mensaje": "Hacen cuotas?"
  }'
```

**Esperado:**
- AI invoca `consultar_faq(pregunta_usuario="Hacen cuotas?", categoria_hint="Financiación")`.
- Respuesta usa el texto de la FAQ ("Sí, ofrecemos financiación...") y ofrece derivar al comercial.

### Test E2E-4 — Tool `notificar_lead` (write)

```bash
# Setup: 3 turnos previos con e2e-004
curl -X POST https://[TU-INSTANCIA-N8N]/webhook/sys-agent \
  -H "Content-Type: application/json" \
  -d '{"canal": "test", "subscriber_id": "e2e-004", "mensaje": "Quiero presupuesto de una impresora UV"}'

curl -X POST https://[TU-INSTANCIA-N8N]/webhook/sys-agent \
  -H "Content-Type: application/json" \
  -d '{"canal": "test", "subscriber_id": "e2e-004", "mensaje": "Soy Test E2E, 11-9999-0000, CABA"}'

curl -X POST https://[TU-INSTANCIA-N8N]/webhook/sys-agent \
  -H "Content-Type: application/json" \
  -d '{"canal": "test", "subscriber_id": "e2e-004", "mensaje": "tu-mail-personal@gmail.com"}'
```

**Esperado en el último turno:**
- AI invoca `notificar_lead(nombre="Test E2E", telefono="11-9999-0000", ubicacion="CABA", mail="tu-mail-personal@gmail.com", equipo_o_aplicacion="impresora UV")`.
- Mail recibido en `info@sistemasysoluciones.com`.
- Mensaje Telegram en el chat configurado.
- Fila en Supabase `sys_session_state` con `etapa = 'derivado'`.
- Respuesta del agente: confirma derivación + cierre con calidez.

### Test E2E-5 — Tool `consultar_inventario_usados`

```bash
curl -X POST https://[TU-INSTANCIA-N8N]/webhook/sys-agent \
  -H "Content-Type: application/json" \
  -d '{
    "canal": "test",
    "subscriber_id": "e2e-005",
    "mensaje": "Tienen equipos Konica usados? Mi presupuesto es bajo"
  }'
```

**Esperado:**
- AI invoca `consultar_inventario_usados()`.
- Respuesta lista 2-3 modelos refurbished disponibles + ofrece coordinar visita al showroom PEPIRI.

---

## Paso 6 — Verificar logs y métricas en Supabase

```sql
-- Tool calls de hoy
SELECT tool_name, status, COUNT(*) as cantidad
FROM sys_tool_calls
WHERE created_at >= CURRENT_DATE
GROUP BY tool_name, status
ORDER BY cantidad DESC;

-- Sesiones activas hoy
SELECT * FROM sys_sesiones_activas_hoy;

-- Performance tools 24h
SELECT * FROM sys_tool_metrics_24h;

-- Verificar que e2e-004 quedó como derivado
SELECT session_id, etapa, datos_capturados, ultima_actividad
FROM sys_session_state
WHERE session_id = 'test_e2e-004';
```

---

## Troubleshooting

### Error "Workflow with ID X is inactive"
El sub-workflow correspondiente NO está activo. Volver al Paso "Pre-requisito CRÍTICO" y activar todos.

### "consultar_tecnologia" devuelve NOT_FOUND para tecnologías que existen
El parámetro `tecnologia` que pasó el LLM no matchea exactamente con el primary field en Airtable. Casos típicos:
- "Eco-solvente" vs "Eco-Solvente" (case sensitivity)
- "DTF" vs "DTF Textil"

Si pasa seguido, agregar al system prompt v2.1 ejemplos de los valores válidos.

### El LLM NO invoca tools cuando debería
Verificar:
- El nodo toolWorkflow tiene `description` clara (revisarlo en el panel).
- El sub-workflow está activo.
- El prompt v2.1 instruye claramente cuándo usar cada tool (ver sección "HERRAMIENTAS DISPONIBLES" del prompt).

### `notificar_lead` falla con "Faltó capturar X"
El LLM invocó sin uno de los 4 obligatorios. Esto es **comportamiento correcto** — la tool valida bloqueante. El AI debería leer el `message_to_agent: "Faltó capturar X"` y pedir ese dato al cliente antes de reintentar.

### Latencia alta (>15s)
Normal en E2E si el LLM invoca 2 tools encadenadas (cada una suma ~1-2s + el tiempo de razonamiento del agente). Si supera 25s consistentemente, revisar:
- Performance Airtable (si hay >100 records en una tabla, Search puede tardar).
- OpenAI rate limits (`429 Too Many Requests`).

### Mail no llega en `notificar_lead`
- Verificar credencial Gmail SYS (puede no estar creada todavía).
- Spam folder.
- Logs en n8n del nodo Gmail Send (`continueOnFail: true` significa que NO falla la tool aunque Gmail falle).

---

## Validación final F4+F5 (checklist)

- [ ] 9 sub-workflows tools Active
- [ ] v0.1 desactivado, v0.2 importado y Active
- [ ] 9 workflow IDs cableados en los toolWorkflow nodes
- [ ] Smoke E2E-1 (consultar_tecnologia) → respuesta usa info real de Airtable
- [ ] Smoke E2E-2 (consultar_aplicacion → buscar_equipo encadenado) → recomienda DTF Textil + opcionalmente equipo
- [ ] Smoke E2E-3 (consultar_faq) → respuesta usa FAQ real
- [ ] Smoke E2E-4 (notificar_lead 3-turn) → mail + Telegram + state update
- [ ] Smoke E2E-5 (consultar_inventario_usados) → lista equipos Konica refurbished
- [ ] Logs en `sys_tool_calls` muestran filas de cada tool invocada

Cuando todos pasen ✅, F4 + F5 están completas y arrancamos **F6 — Integración ManyChat** (configurar Custom Fields + Flows + External Request en ManyChat para que llame al webhook desde IG/WA/FB reales).

---

## Próximo: F6 — Integración ManyChat

- Custom Fields a crear en ManyChat (parte1, parte2, parte3, agent_state)
- Flow "Default Reply" → External Request al webhook
- Flow "Responder Multi-Parte" que el webhook trigger-ea con `setCustomFields + sendFlow`
- Routing por canal (FB/IG vs WA endpoints distintos)
- Smoke test desde IG/WA/FB real

Cuando vos lo digas, te paso el setup de F6 (es 100% trabajo en UI de ManyChat — no genero JSON allá).
