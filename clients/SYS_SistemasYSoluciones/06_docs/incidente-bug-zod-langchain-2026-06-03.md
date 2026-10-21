# Incidente — Bug Zod schema mismatch en n8n LangChain v1.122.4

**Fecha:** 2026-06-03 (Episodio 1) · 2026-06-05 (Episodio 2)
**Severidad:** P0 (Ep. 1, pre-GO-LIVE) · P1 (Ep. 2, captura de leads en prod)
**Estado:** Ep. 1 RESUELTO mediante refactor arquitectónico · Ep. 2 fix de schema + prompt aplicado
**Duración:** ~12 horas de debugging (Ep. 1) · ~30 min (Ep. 2, gracias al postmortem de Ep. 1)
**Workflow afectado:** `sys-agente-principal-v0.4` (Ep. 1) · `sys-agente-principal-v0.5` → `v0.6` (Ep. 2)

---

## Síntoma

El agente devolvía `[Respuesta vacía: {}]` (HTTP 200 con body vacío) ante 4 de los 10 casos del smoke test:
- Test 06 (gorras → consultar_aplicacion)
- Test 07 (HUENU UV → buscar_equipo)
- Test 08 (Konica usados → consultar_inventario_usados)
- Test 10 T2 (banderas → consultar_aplicacion)

Los otros 6 casos respondían correctamente. Los logs en `sys_tool_calls` mostraban 0 rows para las tools afectadas — el sub-workflow nunca ejecutaba.

---

## Causa raíz

n8n LangChain v1.122.4 utiliza `DynamicStructuredTool` con validación Zod del schema sintetizado desde `workflowInputs.schema` del nodo toolWorkflow. El error fatal `Received tool input did not match expected schema` se levanta **antes** de invocar al sub-workflow — el `errorDetails: {}` quedó vacío en la UI de n8n, ocultando el campo específico que fallaba la validación.

**Hipótesis confirmada por evidencia (debug_echo en v0.2):**

El LLM (gpt-4o) generaba args estructuralmente correctos:
- `{"descripcion":"estampar gorras"}` para `consultar_aplicacion`
- `{"marca":"HUENU","tecnologia":"UV","query_libre":"gran formato"}` para `buscar_equipo`
- `{"tipo":"COLOR","modelo_query":"Konica"}` para `consultar_inventario_usados`

A pesar de eso, Zod los rechazaba. Probable causa: la combinación de descripciones `$fromAI` con frases como "Devolvé string o omití. Nunca null ni array." hacían que el LLM **omitiera** args opcionales declarados. Zod en strict mode esperaba todos los campos del schema sintetizado y rechazaba el call.

---

## Soluciones intentadas (que NO destrabaron)

Cada una se aplicó y verificó con smoke test antes de pasar a la siguiente:

| # | Cambio | Resultado |
|---|---|---|
| 1 | `attemptToConvertTypes: true` + `convertFieldsToString: true` en los 10 toolWorkflow nodes | sin cambio |
| 2 | Limpiar `jsonExample` de los Triggers de los 3 sub-workflows (solo strings, valores realistas) | sin cambio |
| 3 | Simplificar descripciones `$fromAI` (sacar `(ej: ...)` y `Devolvé string o omití`) | sin cambio |
| 4 | Cambiar `mappingMode` a `passthrough` | los args llegaban como `{query: "..."}` único campo o `{}` vacío — peor |
| 5 | Setear sub-workflow Triggers a "Accept all data" | sin cambio |
| 6 | Cablear `workflowId` real de `consultar_inventario_usados` (era placeholder `WORKFLOW_ID_INVENTARIO_USADOS`) | esa tool empezó a invocarse pero las otras 2 seguían |
| 7 | Reforzar Regla 8 del prompt + actualizar a v2.3 con instrucciones explícitas sobre args | sin cambio |
| 8 | Revertir prompt a v2.1 | sin cambio |

El bug persistía con UN denominador común: **`DynamicStructuredTool.call` en `@langchain/core@0.3.68/dist/tools/index.cjs:128`** lanzaba la excepción.

---

## Solución que SÍ destrabó — Refactor arquitectónico ("nuclear")

Se reemplazaron los 3 toolWorkflow nodes rotos por **UNA sola tool consolidada** con superficie mínima:

### Diseño

- **Tool nueva:** `consultar_catalogo`
- **Args:** SOLO `query: string` (LLM-driven) + `session_id: string` (context-driven)
- **Razón:** un único campo string no puede fallar Zod (`z.string()` acepta cualquier valor incluyendo cadena vacía)

### Sub-workflow (`sys-tool-consultar-catalogo-v1.json`)

```
Trigger → Classify Intent (Code: regex sobre query) → IF skip?
  ├─ true → Return NOT_FOUND
  └─ false → Switch by intent
                ├─ aplicacion → Airtable: Aplicaciones (formula OR multi-keyword)
                ├─ inventario → Airtable: Inventario Konica (filtro por tipo BN/COLOR)
                └─ equipo     → Airtable: Equipos (formula OR marca + tecnología)
                                                            ↓
                                       Format Output → Log → Return
```

El Code node `Classify Intent`:
- Detecta intent vía regex sobre keywords (`usado/refurbish/bizhub` → inventario; `imprim/estamp/gorra/wrap` → aplicacion; default → equipo)
- Extrae marca conocida (`huenu/dlican/teneth/...`) y tecnología (`dtf textil/uv/sublim/...`)
- Tokeniza la query (filtrando stopwords) y construye `filterByFormula` Airtable como `OR(SEARCH("keyword1", LOWER({Field})), ...)`
- Tres campos pre-construidos: `formula_aplicaciones`, `formula_equipos`, `formula_inventario` que cada nodo Airtable referencia

Eliminados del main: `consultar_aplicacion`, `buscar_equipo`, `consultar_inventario_usados`.
Eliminados del prompt: 3 entries del catálogo de herramientas.
Agregado al prompt: 1 entry `consultar_catalogo` con instrucción de pasar el mensaje natural del cliente.

### Resultado post-nuclear

| Test | Antes | Después |
|---|---|---|
| 06 (gorras) | `{}` vacío | NOT_FOUND con respuesta del agente (Airtable Aplicaciones no tiene record con "gorras") |
| 07 (HUENU UV) | `{}` vacío | RESOLVED con 5 modelos reales (HR 6004 DU, HR 1602 SU, HR 3208 UV, HR 3212 UV, CCD CAMERA UV3040) |
| 08 (Konica usados) | `{}` vacío | RESOLVED con 5 modelos reales (BIZHUB C450i, BIZHUB 558E, Acurio Press C3080, BIZHUB C224) |
| 10 T2 (banderas) | `{}` vacío | TRUE (agente recomienda Sublimación correctamente) |

**Smoke test final:** 5/10 OK + 5 Parcial + 0 Fail + 0 Error.
- Los 5 parciales son problemas de estilo (juez exigente) o de prompt (el agente recibe items pero no los menciona específicamente en la respuesta).
- 0 errores de transporte = bug Zod resuelto definitivamente.

---

## Lecciones aprendidas

1. **n8n LangChain `DynamicStructuredTool` con schemas multi-campo es frágil en v1.122.4.** Cuando un tool tiene 3+ campos opcionales y el LLM omite alguno, la validación Zod falla con un mensaje genérico sin detalles (`errorDetails: {}`). El error stack solo dice `index.cjs:128:23` sin contexto del campo específico que mismatcheó.

2. **Patrón canónico recomendado para tools con catálogo extenso:** un único campo `query: string` + clasificación de intent + routing interno por Switch. Trade-off: el LLM pierde acceso estructurado a los filtros, pero gana garantía de invocación. La inteligencia se traslada del LangChain layer al Code node interno.

3. **Síntomas que ocultan el problema real:** los tests 03, 04, 05 (que usan `consultar_tecnologia` y `consultar_faq`) "pasaban" mientras todas las tools fallaban — eran respuestas alucinadas desde el contenido del system prompt (DTF UV, Solvente, IVA estaban descritos en el prompt como Knowledge Base). Sin verificar `sys_tool_calls` no se hubiera detectado que las tools de hecho NUNCA se invocaban.

4. **Bug latente colateral:** el `session_id` se inyectaba como `$('Normalize Payload').item.json.leadIdentifier` pero el field real era `sessionKey`. Resultado: 100% de los logs históricos tenían `session_id = 'unknown'`. Corregido durante el nuclear.

5. **Bug latente colateral 2:** el `workflowId` de `consultar_inventario_usados` era el placeholder literal `WORKFLOW_ID_INVENTARIO_USADOS` — nunca se reemplazó al importar. La tool nunca pudo invocarse aunque pasara la validación Zod.

---

## Para futuras tools del agente

- **Default:** patrón único-campo (`query: string` + routing interno).
- **Excepción:** tools con 1-2 args muy claros (ej. `consultar_tecnologia` con `tecnologia` + `aspecto` opcional) pueden usar schema multi-campo pero requieren testing exhaustivo + monitoreo de `sys_tool_calls`.
- **Mandatorio:** después de cualquier change en toolWorkflow nodes del main, correr smoke test E2E + verificar logs en `sys_tool_calls` (no confiar solo en el resultado del smoke — el LLM puede alucinar respuestas correctas sin invocar la tool).
- **Mandatorio:** validar `workflowId.value` real (no placeholder) tras importar workflows.

---

## Artefactos generados

- `03_workflows/sys-tool-consultar-catalogo-v1.json` — sub-workflow consolidado nuevo
- `03_workflows/sys-agente-principal-v0.3.json` — main con `attemptToConvertTypes: true` + remoción de debug_echo (paso intermedio)
- `03_workflows/sys-agente-principal-v0.4.json` — main con testing branch restaurado (paso intermedio)
- `scripts/utilities/patch-sys-main-v0.3.py` — script idempotente del patch v0.2 → v0.3
- `scripts/utilities/patch-sys-main-v0.4.py` — script idempotente del patch v0.3 → v0.4
- `06_docs/incidente-bug-zod-langchain-2026-06-03.md` — este documento

## Episodio 2 — 2026-06-05

### Síntoma

AI Agent en producción crasheó con `Received tool input did not match expected schema` al recibir el mensaje:

> `Federico Vizcarra 1131345321 san Miguel`

Lead inbound dando nombre + teléfono + zona, **sin email** y **sin equipo/aplicación**.

### Diagnóstico (sin debugging de 12 horas — gracias al postmortem del Episodio 1)

La firma del error coincide 1:1 con el bug Zod LangChain documentado arriba: error genérico de `DynamicStructuredTool.call`, `errorDetails: {}` vacío, ningún row en `sys_tool_calls` (el sub-workflow nunca se invocó).

**Evidencia clave — query a `sys_tool_calls` (2026-06-05 ~15:00):**

```
session_id      | tool_name           | status     | timestamp
wa_1686796493   | consultar-catalogo  | RESOLVED   | 2026-06-05 12:03:33
```

Una sola row para la session que crashó. Ningún `notificar_lead` ni `guardar_email` para `wa_1686796493`. → el sub-workflow del tool culpable **nunca ejecutó**, lo cual es la firma exacta del bug Zod (rompe en la layer LangChain antes de invocar el Trigger).

**Hipótesis refinada (orden de probabilidad):**

1. **`notificar_lead`** — la más probable. Razonamiento:
   - El cliente ya había tenido una invocación exitosa de `consultar_catalogo` a las 12:03:33 → el LLM tenía contexto de equipo/aplicación de turnos previos.
   - El mensaje `"Federico Vizcarra 1131345321 san Miguel"` provee nombre + teléfono + ubicación.
   - El LLM completó mentalmente los 4 datos obligatorios de la Regla 2 (`nombre + teléfono + ubicación + equipo/aplicación`) tomando el equipo del catálogo previo.
   - El nodo `notificar_lead` tiene **11 campos LLM-exposed** — la superficie más amplia de schema en el workflow. Riesgo Zod ALTO.

2. **`guardar_email`** — improbable pero posible. No hay email en el mensaje, pero gpt-4o ocasionalmente sintetiza tool calls con campos vacíos cuando lee el contexto como "captura de lead".

3. **`consultar_catalogo`** — descartado. Ya está blindado por el refactor nuclear de Episodio 1 (1 campo único `query`).

**Patrón roto subyacente:** ambos candidatos (`notificar_lead` y `guardar_email`) heredan el mismo defecto del Episodio 1 — descripciones `$fromAI` con frases como `"Opcional"`, `"Si no, dejar vacío"`, `"Si no estás seguro"`, `"Si no hay contexto claro"`. Esas frases empujan al LLM a omitir campos en el JSON. Zod en strict mode los espera todos → rechaza → AI Agent se cae.

**Causa secundaria — gap del prompt:** v2.0 vigente NO documenta `guardar_email` en su sección HERRAMIENTAS. El agente decidía cuándo invocar la tool puramente desde la `description` del nodo `toolWorkflow` y su entrenamiento. Sin policy explícita de "no invocar sin email", se gatilla la falla con cualquier mensaje que el LLM interprete como "datos de lead".

### Fix aplicado

Doble fix — schema + prompt:

**A. Schema (n8n vivo):**
- Descripciones `$fromAI` minimalistas para los 5 campos del nodo `guardar_email` (el Anexo A de la guía cubre `notificar_lead` si resulta que fue ese — patrón idéntico).
- Config verificada: Required OFF en todos, Type string, Attempt to Convert Types ON.
- Sub-workflow `sys-tool-guardar-email-v1` NO se tocó — su `Validate Input` sigue exigiendo email no vacío, devolviendo `status: ERROR` controlado si el AI igual invoca sin email.

**B. Prompt v2.0 → v2.1:**
- Nueva entry "guardar_email" en HERRAMIENTAS (cuándo invocar, args, output, regla PROHIBIDO).
- Nueva Regla operativa 26: PROHIBIDO invocar `guardar_email` sin email explícito del cliente. Cubre el caso de Federico (nombre + tel + zona, sin email).

### Artefactos generados

- `06_docs/guia-fix-guardar-email-zod-2026-06-05.md` — guía paso a paso de los EDITs en n8n vivo + smoke E2E (3 casos: A=mensaje Federico, B=con email, C=4/4 datos).
- `04_agents/agente-sistemasysoluciones-system-prompt.md` — bump v2.0 → v2.1.
- `04_agents/agente-sistemasysoluciones-system-prompt-v2.1.md` — snapshot.
- `03_workflows/sys-agente-principal-v0.6.json` — re-export post-fix (pendiente — generar después de aplicar Paso 1+2 en n8n).

### Lecciones reforzadas (suma a las del Episodio 1)

6. **Toda tool nueva cableada en producción debe documentarse en el prompt en el mismo deploy.** El gap entre la cabling (2026-06-02) y la documentación (2026-06-05) creó la ventana en que el agente operaba con la tool "invisible" para el prompt, decidiendo por intuición LLM. La descripción del nodo `toolWorkflow` NO es suficiente policy — el prompt es la fuente de verdad de cuándo invocar.

7. **Disciplina anti-Zod aplicable a cualquier tool nueva, no solo tools de catálogo.** El postmortem del Episodio 1 enmarcó el fix nuclear para "tools con catálogo extenso". Episodio 2 muestra que aplica también a tools de captura (guardar_email tiene 5 campos opcionales — mismo patrón roto). Reglamento canónico: descripciones `$fromAI` minimalistas SIEMPRE, sin "Opcional", "Si no", "Si no estás seguro".

---

## Pendientes post-incidente

- [ ] Refinar prompt para que cuando `consultar_catalogo` devuelve items con modelo, el agente mencione 2-3 modelos específicos en la respuesta (causa los 3 parciales tests 06/07/08).
- [ ] Verificar/poblar tabla Aplicaciones en Airtable para que palabras como "gorras", "banderas", "remeras" matcheen (test 06 dio NOT_FOUND).
- [ ] Re-exportar el `sys-agente-principal` actual de n8n (con el nuevo toolWorkflow `consultar_catalogo` cableado) y guardar como `sys-agente-principal-v0.5.json` en repo. El v0.4 del repo NO refleja el estado vivo post-nuclear.
- [ ] Aplicar el mismo refactor (o auditar) al resto de toolWorkflow nodes si en producción real aparece el mismo bug con consultar_tecnologia o consultar_faq.
- [ ] **(Episodio 2)** Aplicar Paso 0-4 de la guía `06_docs/guia-fix-guardar-email-zod-2026-06-05.md` en n8n vivo + commit `sys-agente-principal-v0.6.json`.
- [ ] **(Episodio 2)** Auditar el resto de toolWorkflow nodes (`notificar_lead`, `consultar_tecnologia`, etc.) — descripciones `$fromAI` minimalistas como standing rule.
