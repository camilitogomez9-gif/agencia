# Guía — Fix incidente Zod Episodio 2 (2026-06-05)

**Cliente:** SYS — Sistemas y Soluciones
**Workflow vivo:** `sys-agente-principal` (id en n8n; v0.5 en repo)
**Disparador:** AI Agent crashed con `Received tool input did not match expected schema` ante el mensaje `"Federico Vizcarra 1131345321 san Miguel"` en la session `wa_1686796493`.
**Plan de referencia:** `/Users/camilo/.claude/plans/el-flujo-principal-recibi-zesty-origami.md`
**Postmortem base:** `06_docs/incidente-bug-zod-langchain-2026-06-03.md` (Episodio 1 — original; Episodio 2 — este caso).

**Diagnóstico refinado (post query a sys_tool_calls):**

| Hipótesis | Evidencia | Probabilidad |
|---|---|---|
| `notificar_lead` | session `wa_1686796493` tuvo `consultar_catalogo` RESOLVED a 12:03:33 → LLM tenía equipo/aplicación de turnos previos → con nombre+tel+zona del nuevo mensaje, completó mentalmente los 4 obligatorios → invocó `notificar_lead` (11 campos LLM-exposed = la superficie de schema más amplia del workflow) → Zod rechazó | **ALTA** |
| `guardar_email` | 5 campos LLM-exposed, pero no había email en el mensaje | Baja |
| `consultar_catalogo` | blindado por refactor nuclear Episodio 1 | Descartado |

**Conclusión operativa:** este fix debe aplicarse a **AMBOS** nodos (`notificar_lead` Y `guardar_email`) en el mismo deploy. Patrón idéntico, distintas descripciones. Esto cubre la causa probable + previene Episodio 3.

---

## Resumen del fix

Doble fix preventivo (cubre ambos candidatos) + prompt + smoke + re-export.

| # | Acción | Dónde | Tiempo |
|---|---|---|---|
| Paso 0 | (Opcional) confirmar tool culpable revisando n8n Executions de `wa_1686796493` post-12:03:33 | n8n UI | 5 min |
| Paso 1A | **Limpiar descripciones `$fromAI` del nodo `notificar_lead` (11 campos)** — probable culpable | n8n UI · workflow vivo | 15 min |
| Paso 1B | Limpiar descripciones `$fromAI` del nodo `guardar_email` (5 campos) — fix preventivo | n8n UI · workflow vivo | 10 min |
| Paso 2 | Copy-paste prompt v2.1 al `systemMessage` del AI Agent | n8n UI · workflow vivo | 3 min |
| Paso 3 | Smoke E2E con curl (3 casos) | terminal | 5 min |
| Paso 4 | Re-export del workflow y commit como v0.6 | n8n → repo | 5 min |

---

## Paso 0 (opcional) — Confirmar tool culpable en n8n Executions

El query a `sys_tool_calls` ya confirmó que el sub-workflow del tool culpable **nunca ejecutó** para `wa_1686796493` (no hay row después de `consultar-catalogo` RESOLVED 12:03:33). Eso es la firma del bug Zod. Para confirmar **cuál** tool intentó:

1. Abrir el workflow vivo `sys-agente-principal` en n8n.
2. Tab "Executions" → filtrar por fecha 2026-06-05, buscar la ejecución posterior a 12:03:33 con session `wa_1686796493` que terminó en error.
3. Click → expandir el nodo "AI Agent" → tab "Logs" o "Tool calls".
4. **Lo que se debe ver:** un intento de invocación a una tool (típicamente `notificar_lead` o `guardar_email`) con args (a veces `{}` vacío) y luego el error `Received tool input did not match expected schema` antes del `output` del Agent.

**Si saltás este paso:** los Pasos 1A + 1B abajo cubren los 2 candidatos preventivamente. Es 25 min de EDITs vs el riesgo de Episodio 3 a la próxima.

---

## Paso 1A — Limpiar descripciones `$fromAI` del nodo `notificar_lead` (probable culpable)

### Ubicación en n8n

1. Abrir el workflow vivo `sys-agente-principal`.
2. Localizar el nodo `notificar_lead` (toolWorkflow, color verde, conectado al AI Agent via `ai_tool`).
3. Doble click → tab "Parameters" → sección `Workflow Inputs` (mappingMode: `defineBelow`).

### EDITs por campo (Value column)

Para cada uno de los campos LLM-exposed (11 totales), reemplazar el value actual por el nuevo. NO tocar campos inyectados desde `Normalize Payload` (`canal`, `subscriber_id` — mantener como están).

| Campo | Descripción mínima nueva |
|---|---|
| `nombre` | `Nombre del cliente` |
| `telefono` | `Telefono del cliente` |
| `ubicacion` | `Ubicacion del cliente — ciudad o provincia` |
| `equipo_o_aplicacion` | `Equipo o aplicacion que el cliente consulta` |
| `mail` | `Email del cliente en formato xxx@xxx.xxx` |
| `empresa` | `Empresa del cliente` |
| `perfil` | `Perfil del cliente. Valores: distribuidor, pyme, emprendedor, sin_clasificar` |
| `tecnologia_interes` | `Tecnologia de interes. Valores: DTF Textil, DTF UV, UV, Sublimacion, Eco-Solvente, Solvente, RISO, IDL Laser, Gran Formato, Corte` |
| `linea_interes` | `Linea de equipos de interes` |
| `urgencia` | `Urgencia del lead. Valores: true, false` |
| `notas` | `Notas adicionales del lead` |

**Formato del Value para cada campo:**

```
={{ $fromAI('<nombre_campo>', `<descripción mínima>`, 'string') }}
```

Sacar de las descripciones originales: `"Opcional"`, `"Si no"`, `"Si no estás seguro"`, `"Si no hay contexto claro"`, ejemplos largos entre paréntesis. La obligatoriedad de los 4 datos clave (`nombre`, `telefono`, `ubicacion`, `equipo_o_aplicacion`) la enforce el sub-workflow `sys-tool-notificar-lead-v2` internamente + la Regla operativa 2 + 22 del prompt v2.1.

### Verificación de config del nodo

| Setting | Valor esperado |
|---|---|
| `mappingMode` | `Define Below` |
| Cada parámetro · Type | `string` (todos los 11) |
| Cada parámetro · Required | **OFF** (todos) |
| `Attempt to Convert Types` | **ON** |
| `Convert Fields to String` | **ON** |

---

## Paso 1B — Limpiar descripciones `$fromAI` del nodo `guardar_email` (preventivo)

**Principio del fix (del postmortem Episodio 1):** las frases `"Si no, dejar vacío"`, `"Opcional"`, `"Si no estás seguro"`, `"Si no hay contexto claro"` en las descripciones `$fromAI` hacen que el LLM **omita** el campo del JSON cuando no lo tiene claro. Zod en strict mode espera todos los campos del schema sintetizado y rechaza el call. La solución es descripciones minimalistas — el LLM siempre pasará algo (aunque sea string vacío), y el sub-workflow valida internamente.

### Ubicación en n8n

1. Abrir el workflow vivo `sys-agente-principal`.
2. Localizar el nodo `guardar_email` (toolWorkflow, color verde, conectado al AI Agent via `ai_tool`).
3. Doble click → tab "Parameters" → sección `Workflow Inputs` (mappingMode: `defineBelow`).

### EDITs por campo (Value column — el contenido del `$fromAI`)

Para cada uno de los 5 campos LLM-exposed, reemplazar el value actual por el nuevo. **NO** tocar los campos inyectados (`canal`, `subscriber_id`, `session_id` — esos referencian `Normalize Payload`, mantenerlos como están).

#### Campo `email`

**Antes:**
```
={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('email', `Email del cliente. Obligatorio. Formato estándar xxxxx@xxxxx.xxx. Validalo antes de invocar — si el cliente lo escribió mal, pedile que confirme.`, 'string') }}
```

**Después:**
```
={{ $fromAI('email', `Email del cliente en formato xxx@xxx.xxx`, 'string') }}
```

#### Campo `nombre`

**Antes:**
```
={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('nombre', `Opcional: nombre del cliente si lo conocés del contexto de la conversación. Si no, dejar vacío.`, 'string') }}
```

**Después:**
```
={{ $fromAI('nombre', `Nombre del cliente`, 'string') }}
```

#### Campo `telefono`

**Antes:**
```
={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('telefono', `Opcional: teléfono del cliente si ya lo capturaste. Si no, dejar vacío.`, 'string') }}
```

**Después:**
```
={{ $fromAI('telefono', `Telefono del cliente`, 'string') }}
```

#### Campo `origen`

**Antes:**
```
={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('origen', `Opcional. Motivo por el cual el cliente comparte el email. Valores válidos: newsletter (pidió novedades o info por correo), derivacion (en el flujo de derivación al comercial), descuento_insumos (vino por una promo de insumos), otro (default). Si no estás seguro, dejá 'otro'.`, 'string') }}
```

**Después:**
```
={{ $fromAI('origen', `Motivo del email. Valores: newsletter, derivacion, descuento_insumos, otro`, 'string') }}
```

#### Campo `aplicacion_interes`

**Antes:**
```
={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('aplicacion_interes', `Opcional. Texto libre describiendo la aplicación o el equipo que el cliente está consultando, deducido de la conversación (ej. 'DTF textil para remeras', 'wrap vehicular', 'letreros UV gran formato', 'plotter de corte para vinilo'). Si no hay contexto claro, dejar vacío.`, 'string') }}
```

**Después:**
```
={{ $fromAI('aplicacion_interes', `Aplicación o equipo que el cliente consulta`, 'string') }}
```

### Verificación de config del nodo

Confirmar (NO editar si ya está así — pero verificar):

| Setting | Valor esperado |
|---|---|
| `mappingMode` | `Define Below` |
| Cada parámetro · Type | `string` (todos los 5 LLM-exposed) |
| Cada parámetro · Required | **OFF** (todos, incluido `email` — la obligatoriedad la enforce el sub-workflow, NO Zod) |
| `Attempt to Convert Types` | **ON** |
| `Convert Fields to String` | **ON** |

### Sub-workflow — NO tocar

`sys-tool-guardar-email-v1` (workflowId `v9HD7P2uroG4Ni3A`) tiene un nodo `Validate Input` que sigue exigiendo email no vacío con regex válido. Si llega un call sin email, devuelve `status: ERROR` con `message_to_agent: "Faltó el email..."` — el agente lo procesa controladamente. Eso es lo correcto: la obligatoriedad vive en el sub-workflow, NO en el schema Zod.

---

## Paso 2 — Copy-paste del prompt v2.1 al `systemMessage` del AI Agent

1. En el mismo workflow, doble click en el nodo `AI Agent` (azul).
2. Tab "Parameters" → campo `System Message` (textarea grande).
3. Reemplazar **todo el contenido** por el bloque comprendido entre los ` ``` ` del archivo:

   `clients/SYS_SistemasYSoluciones/04_agents/agente-sistemasysoluciones-system-prompt.md`

   (sección "## System Prompt (producción)" — del primer ` ``` ` hasta el último ` ``` `).

4. Guardar el nodo.

**Verificación rápida** (Ctrl+F dentro del campo `System Message`):
- Buscar `"guardar_email"` → debe aparecer en sección HERRAMIENTAS y en Regla 26.
- Buscar `"Regla 26"` o `"26."` → debe estar la entrada de `guardar_email` solo si hay email explícito.
- Buscar `"9 herramientas"` → debe decir 9, no 8.

---

## Paso 3 — Smoke E2E (3 casos)

### Caso A — Repetir el mensaje que rompió (debe NO romper, NO invocar tool)

```bash
curl -X POST https://[TU-INSTANCIA-N8N]/webhook/sys-agent \
  -H "Content-Type: application/json" \
  -H "key: 3d20a9487e883b259212c5e67acb380085639109e4063d53" \
  -d '{
    "channel": "test",
    "subscriber_id": "smoke-zod-fix-A",
    "last_input_text": "Federico Vizcarra 1131345321 san Miguel",
    "first_name": "Federico"
  }'
```

**Pass criteria:**
- HTTP 200 + body NO vacío.
- Respuesta del agente pide el equipo o la aplicación (Regla 22).
- `sys_tool_calls` para `subscriber_id='smoke-zod-fix-A'` está VACÍO (ningún tool call).

### Caso B — Cliente comparte email (debe invocar `guardar_email` exitosamente)

```bash
curl -X POST https://[TU-INSTANCIA-N8N]/webhook/sys-agent \
  -H "Content-Type: application/json" \
  -H "key: 3d20a9487e883b259212c5e67acb380085639109e4063d53" \
  -d '{
    "channel": "test",
    "subscriber_id": "smoke-zod-fix-B",
    "last_input_text": "Hola, mi mail es federico.test@example.com, quiero info sobre DTF textil",
    "first_name": "Federico"
  }'
```

**Pass criteria:**
- HTTP 200 + body con respuesta del agente.
- `sys_tool_calls` para `subscriber_id='smoke-zod-fix-B'` tiene una row con `tool_name='guardar_email'` y `status='RESOLVED'`.
- Google Sheet `SYS - Leads (Captura Emails)` tiene una fila nueva con el email.

### Caso C — Lead con 4/4 datos (debe invocar `notificar_lead` o pedir email)

```bash
curl -X POST https://[TU-INSTANCIA-N8N]/webhook/sys-agent \
  -H "Content-Type: application/json" \
  -H "key: 3d20a9487e883b259212c5e67acb380085639109e4063d53" \
  -d '{
    "channel": "test",
    "subscriber_id": "smoke-zod-fix-C",
    "last_input_text": "Soy Federico Vizcarra, tel 1131345321, escribo desde San Miguel, busco DTF textil para remeras",
    "first_name": "Federico"
  }'
```

**Pass criteria:**
- HTTP 200.
- Comportamiento aceptable: el agente o (a) invoca `notificar_lead` (4/4 obligatorios — nombre, telefono, ubicacion, equipo_o_aplicacion=DTF textil) o (b) pide el mail con la frase del punto 4. Cualquiera de las 2 es correcta.
- Si invocó `notificar_lead`, fila en `sys_tool_calls` con `tool_name='notificar_lead'`, `status='RESOLVED'`.

### Logs a verificar

Después de los 3 casos, en n8n Executions:
- 3 ejecuciones nuevas, todas con status `success` (verde).
- NINGUNA muestra `Received tool input did not match expected schema`.

---

## Paso 4 — Re-export y commit

1. En n8n: tres puntos del workflow `sys-agente-principal` → "Download" → guardar JSON.
2. Copiar el JSON a:
   ```
   clients/SYS_SistemasYSoluciones/03_workflows/sys-agente-principal-v0.6.json
   ```
3. Git commit con mensaje:
   ```
   sync(SYS): fix Zod incident #2 — guardar_email schema + prompt v2.1
   ```
4. Correr `/cliente-sync SYS` para que `/contexto-sync` regenere `contexto/datos-actuales.md`.

---

## Anexo A — Auditoría preventiva del resto de las tools

Después de aplicar Pasos 1A + 1B, ejecutar la misma limpieza de descripciones `$fromAI` en los nodos:

- `consultar_tecnologia` (2 campos: `tecnologia`, `aspecto`)
- `consultar_compatibilidad` (3 campos: `tipo_consulta`, `equipo`, `elemento`)
- `consultar_faq` (2 campos: `pregunta_usuario`, `categoria_hint`)
- `consultar_url_tienda` (2 campos: `producto`, `categoria`)
- `consultar_lineas_priorizadas` (0 campos — exento)

Regla estándar: descripciones de 5-12 palabras, sin "Opcional", "Si no", "Si no estás seguro", "(ej: ...)", "Nunca null ni array". Required: OFF en todos. Type: string siempre. `consultar_catalogo` ya está blindado (fix nuclear Episodio 1) — NO tocar.

Esta auditoría hace standing rule el patrón anti-Zod, no solo reactivo al Episodio 2.

---

## Anexo B — Validación del fix (checklist)

- [ ] Paso 0 hecho (opcional) — identificada la tool real en n8n Executions
- [ ] Paso 1A hecho — 11 campos editados en `notificar_lead`
- [ ] Paso 1B hecho — 5 campos editados en `guardar_email`
- [ ] Paso 2 hecho — systemMessage v2.1 pegado
- [ ] Paso 3 hecho — Casos A, B, C pasan
- [ ] Paso 4 hecho — workflow v0.6 commiteado en repo
- [ ] Postmortem actualizado — sección "Episodio 2" agregada
- [ ] CLAUDE.md actualizado — prompt v2.0 → v2.1
- [ ] (Opcional, recomendado) Anexo A ejecutado — resto de tools auditadas
- [ ] `/cliente-sync SYS` corrido
