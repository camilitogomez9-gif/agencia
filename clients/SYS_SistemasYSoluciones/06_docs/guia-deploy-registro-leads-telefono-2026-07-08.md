# Guía de deploy — Registro de leads gated por teléfono (2026-07-08)

**Cliente:** SYS · **Origen:** reunión Jimena + Edgardo 2026-07-08 (accionable "Registro de leads").
**Objetivo:** que un lead NUNCA se registre en la planilla sin un teléfono válido. El número sale determinístico de ManyChat; si ManyChat manda `{{phone}}` sin resolver, el agente pide el número al lead y registra ese (y puede pedir el correo en el mismo turno).

---

## 0. Qué cambia y por qué (resumen)

El prompt v2.5 (vivo) ya describía este comportamiento, pero la **implementación no lo hacía cumplir**: el nodo tool pasaba el teléfono por `$fromAI` (lo copiaba el LLM) y el sub-workflow registraba al lead con solo el nombre, sin exigir teléfono. Este deploy alinea implementación + prompt.

| # | Pieza | Cambio | Cómo se entrega |
|---|-------|--------|-----------------|
| 1 | Sub-workflow `registrar_datos_lead` | Gate por teléfono: coalesce ManyChat→chat, valida numérico, `REJECTED` si no hay número | JSON importable (in-place) |
| 2 | Main — nodo tool `registrar_datos_lead` | `telefono_webhook` determinístico + `telefono` (chat) por `$fromAI` | Clipboard + edits paso a paso |
| 3 | Main — nodo `Build User Message Context` | Línea nueva `Teléfono del lead` en el `[CONTEXTO TURNO]` | Reemplazo de jsCode |
| 4 | System prompt | v2.5 → v2.6 (Regla 26 + contexto + ficha tool) | Copy/paste al Google Doc + backup |
| 5 | Google Sheets | Sin cambio estructural (la columna `telefono` ya existe) | — |

**Orden recomendado:** 1 → 3 → 2 → 4. (El sub-workflow y el Build Context no rompen nada solos; el nodo tool es el que activa el flujo nuevo; el prompt cierra el círculo.) Hacer todo en una ventana y correr los smoke tests al final.

---

## 1. Sub-workflow `registrar_datos_lead` → v2 (import in-place)

> ⚠️ **Actualización 2026-07-10:** apareció un bug en producción en este mismo sub-workflow (nodo `IF lead existe?`, no en `Validate Input`). Ver **§9 Errata post-deploy** al final de esta guía. El archivo vigente para importar hoy es **`sys-tool-registrar-datos-lead-v3.json`** (v2 queda como referencia histórica, ya no se recomienda importarla desde cero).

Archivo: `clients/SYS_SistemasYSoluciones/03_workflows/sys-tool-registrar-datos-lead-v2.json`
Preserva el `workflowId` `v9HD7P2uroG4Ni3A` → al importarlo **sobreescribe el workflow vivo in-place**, sin tocar el cableado del main.

**Pasos:**
1. En n8n abrir el workflow `registrar_datos_lead` (id `v9HD7P2uroG4Ni3A`).
2. Menú "⋯" → **Import from File** → elegir `sys-tool-registrar-datos-lead-v2.json` → confirmar overwrite.
3. Verificar que quede `active` (n8n a veces lo apaga al importar).

**Qué hace distinto el v2 (nodo `Validate Input`):**
- Resuelve el teléfono por coalesce: `telefono_webhook` (determinístico, ManyChat) → `telefono` (lo que el lead escribió). Descarta `{{phone}}` y todo lo no-numérico (mínimo 6 dígitos).
- **Sin teléfono válido → devuelve `status: "REJECTED"`, `reason: "telefono_invalido"` y no escribe nada** (ni Sheets ni state). No corta el flujo del agente.
- Con teléfono válido → sigue el flujo normal (upsert por `subscriber_id`, notif solo en alta nueva).
- El nodo `Return ERROR (faltan datos)` se renombró a `Return REJECTED / ERROR` y ahora propaga el status real (REJECTED o ERROR) en vez de hardcodear ERROR.

**Verificación rápida (Pin Data ya viene cargado):** ejecutar el workflow a mano con el Pin Data del trigger (trae `telefono_webhook: "5491122334455"`) → debe terminar en `RESOLVED`. Después probar un input sin teléfono (borrar `telefono_webhook` y `telefono` del pin) → debe terminar en `REJECTED`.

---

## 2. Main — nodo tool `registrar_datos_lead` (EDIT en producción)

> El main es producción (memoria, webhooks, credenciales). NO se pre-edita el JSON completo. Se edita el nodo en la UI. Dos vías; elegí una.

### Vía A — Reemplazo por clipboard (recomendada, más rápida)

Archivo: `06_docs/snippets/clipboard-registrar-datos-lead-node-2026-07-08.json`

1. En el main, ubicar el nodo toolWorkflow que apunta a `v9HD7P2uroG4Ni3A` (hoy se llama `guardar_email` o `registrar_datos_lead` según si ya se aplicó el rename del 2026-06-24). **Anotá a qué está conectado** (sale un cable `ai_tool` hacia el nodo `AI Agent`).
2. Copiar TODO el contenido de `clipboard-registrar-datos-lead-node-2026-07-08.json` y pegarlo (Cmd/Ctrl+V) en el canvas del main. Aparece el nodo `registrar_datos_lead` ya corregido.
3. Borrar el nodo viejo.
4. Arrastrar el cable `ai_tool` del nodo nuevo `registrar_datos_lead` al `AI Agent` (mismo puerto que tenía el viejo).
5. Verificar credenciales: el nodo toolWorkflow no tiene credenciales propias (usa el sub-workflow). Confirmar que `workflowId` = `v9HD7P2uroG4Ni3A`.

### Vía B — Editar el nodo existente campo por campo

Si preferís no reemplazar el nodo:

1. **Nombre del nodo** → `registrar_datos_lead` (si estaba como `guardar_email`).
2. **Description** → reemplazar por (texto exacto):
   > Registra al lead en la base de captura (Google Sheets) apenas hay un teléfono válido, y lo enriquece (upsert por subscriber_id) cuando llega el correo. El teléfono se resuelve solo: primero el de ManyChat (determinístico, ya cableado en telefono_webhook), y como fallback el que el lead escribió en el chat (arg telefono). NO pases el número del canal vos: solo pasá 'telefono' si el lead escribió su número en la conversación. Si la tool devuelve REJECTED reason=telefono_invalido, todavía no hay número: pedíselo al lead y volvé a invocar cuando lo tenga. already_exists=true → no lo menciones, seguí natural. Es independiente de notificar_lead.
3. En **Workflow Inputs** (la tabla de mapeo de campos):
   - Campo `telefono` → cambiar la expresión a:
     ```
     ={{ $fromAI('telefono', `Teléfono que el LEAD ESCRIBIÓ en el chat (solo dígitos, con o sin +). Dejá vacío si el lead no escribió un número, o si el número ya vino por ManyChat.`, 'string') }}
     ```
   - **Agregar un campo nuevo** `telefono_webhook` con la expresión (determinística, NO `$fromAI`):
     ```
     ={{ $('Normalize Payload').item.json.phone }}
     ```
   - Dejar `email`, `nombre`, `aplicacion_interes`, `origen` como estaban (`$fromAI`), y `canal`/`subscriber_id`/`session_id` como estaban (determinísticos desde `Normalize Payload`).

**Clave conceptual:** `telefono_webhook` es determinístico (n8n lo toma directo del webhook, el LLM no lo ve). `telefono` es agéntico (el LLM solo lo llena si el lead escribió el número). El sub-workflow prioriza el webhook y cae al chat.

---

## 3. Main — nodo `Build User Message Context` (EDIT en producción)

Archivo con el código: `06_docs/snippets/build-user-message-context-v2.6.js`

1. En el main, abrir el nodo Code `Build User Message Context`.
2. Seleccionar todo el `jsCode` (Cmd/Ctrl+A) y reemplazarlo por el contenido completo de `build-user-message-context-v2.6.js`.
3. Guardar.

**Qué agrega:** una línea `- Teléfono del lead: <número>` en el `[CONTEXTO TURNO]` cuando hay un número válido (de ManyChat o escrito por el lead), o `- Teléfono del lead: NO disponible (...)` cuando no. Usa el MISMO criterio de validación que el sub-workflow, así prompt, contexto y tool coinciden. También endurece la línea "Número del canal" existente para que no muestre `{{phone}}` literal.

> Nota de robustez: si el main vivo (v2.5-era) renombró `Build User Message Context`, aplicá el mismo reemplazo de jsCode sobre el nodo que construye el `[CONTEXTO TURNO]` (el que arma la variable `userMessage`). El código referencia `Normalize Payload`, `Parse datos del mensaje` y `Get session_state` por nombre — confirmá que esos 3 nodos existen con esos nombres (son los del fix re-saludo v0.9). Si alguno cambió de nombre, ajustá la referencia.

---

## 4. System prompt v2.5 → v2.6 (Google Doc + backup)

Fuente de verdad versionada: `04_agents/agente-sistemasysoluciones-system-prompt.md` (v2.6). Backup del vivo previo: `agente-sistemasysoluciones-system-prompt-v2.5.md`.

1. Abrir el Google Doc del prompt (el que lee el nodo `Get a document` del main).
2. Reemplazar su contenido por el bloque `## System Prompt (producción)` de `agente-sistemasysoluciones-system-prompt.md` (desde `Versión: v2.6` hasta el final).
3. Sincronizar el **set-node `backup`** del main (el fallback inline si Google Docs falla): pegar el mismo texto v2.6 en su campo de valor.

**Qué cambió en el prompt (v2.6):**
- `USO DEL CONTEXTO DEL TURNO`: documenta la línea `Teléfono del lead` (reemplaza la referencia a `{{TELEFONO}}` que el contexto nunca proveía así).
- Ficha de `registrar_datos_lead`: teléfono con dos fuentes (determinística ManyChat / agéntica chat) + status `REJECTED`.
- Regla operativa 26 reescrita: teléfono numérico = condición necesaria; guard de intención para no registrar un simple "hola" aunque el canal traiga el número.

---

## 5. Google Sheets — sin cambios estructurales

La planilla `SYS - Leads (Captura Emails)` (`15OrQ-uI_x5rAorjkMpz_V_TvFxVf31nsDfTjm9oUqsc`, hoja `Emails`) ya tiene las 9 columnas que usa el sub-workflow: `timestamp, email, nombre, telefono, canal, subscriber_id, session_id, aplicacion_interes, origen`. **No hay que tocar la estructura.** El único cambio observable: a partir de ahora no se agregan filas sin `telefono`. Las filas históricas sin teléfono quedan como están (no se limpian en este deploy).

---

## 6. Smoke tests (E2E contra el webhook o WhatsApp de prueba)

Correr después de aplicar 1-4. Verificar en la planilla `Emails` y en Postgres `sys_tool_calls`.

| # | Escenario | Input | Esperado |
|---|-----------|-------|----------|
| **S1** | WhatsApp con número real + interés | Lead WA (ManyChat manda phone real) dice "hola, busco un plotter de 1.60" y luego da su nombre | `Teléfono del lead: <n>` en contexto → agente invoca `registrar_datos_lead` → `RESOLVED` → fila nueva en Sheets con `telefono` poblado. |
| **S2** | ManyChat manda `{{phone}}` | Simular webhook con `phone: "{{phone}}"`, lead da nombre + pregunta por un equipo | Contexto muestra `Teléfono del lead: NO disponible` → agente PIDE el número (puede pedir mail en el mismo turno) → NO registra todavía. |
| **S3** | S2 + el lead escribe el número | Continúa S2: lead responde "1122334455 y juan@mail.com" | `Parse datos del mensaje` captura el número → contexto lo muestra → agente invoca tool con `telefono` (chat) → `RESOLVED` → fila con teléfono + mail. |
| **S4** | Solo saludo | Lead WA con phone real dice solo "hola" | Agente NO registra (guard de intención). `sys_tool_calls` sin `registrar-datos-lead` para ese turno. |
| **S5** | Invocación sin teléfono (defensa) | Forzar (o dejar que el LLM intente) una invocación sin número | Sub-workflow devuelve `REJECTED` / `telefono_invalido`, no escribe fila. Query lo confirma. |
| **S6** | Enriquecimiento (upsert) | Lead ya registrado (S1) vuelve y da el mail | Re-invocación → `already_exists=true`, fila actualizada sin duplicar, `telefono` intacto. |

**Queries de verificación (Postgres `Supabase SYS` id `cQLxF5deDtmo4HTV`):**
```sql
-- Últimas invocaciones de registrar-datos-lead con su status
SELECT created_at,
       input_payload->>'telefono'          AS tel_chat,
       input_payload->>'telefono_webhook'  AS tel_webhook,
       output_payload->>'status'           AS status,
       output_payload->>'reason'           AS reason
FROM sys_tool_calls
WHERE tool_name = 'registrar-datos-lead'
ORDER BY created_at DESC
LIMIT 20;

-- Ratio REJECTED (proxy de cuán seguido ManyChat manda {{phone}} sin resolver)
SELECT output_payload->>'status' AS status, count(*)
FROM sys_tool_calls
WHERE tool_name = 'registrar-datos-lead'
  AND created_at > now() - interval '48 hours'
GROUP BY 1;
```

**Verificación en la planilla:** ninguna fila nueva debe quedar con `telefono` vacío. Filtrar la hoja `Emails` por `telefono` vacío entre las filas creadas post-deploy → debe dar 0.

---

## 7. Rollback

- **Sub-workflow:** re-importar `sys-tool-registrar-datos-lead-v1.json` (mismo `workflowId`, overwrite). Vuelve al criterio viejo (registra con nombre solo).
- **Main tool node:** volver la expresión de `telefono` a `={{ $fromAI('telefono', 'Teléfono del cliente', 'string') }}` y borrar `telefono_webhook` del mapeo + schema.
- **Build Context:** el nodo Code guarda versiones; si no, el jsCode v0.9 está en `03_workflows/sys-agente-principal-v0.9.json`.
- **Prompt:** pegar de nuevo el bloque de `agente-sistemasysoluciones-system-prompt-v2.5.md` al Google Doc + set-node `backup`.

---

## 8. Decisión abierta para la agencia (flag)

El comportamiento implementado registra un lead cuando hay **teléfono válido Y señal de interés** (nombre, pregunta por equipo, pide cotización o contacto). Agregué el guard "señal de interés" — que NO estaba explícito en el prompt v2.5 — para evitar que cada "hola" de WhatsApp (que ya trae número) registre + dispare el mail a emarti/marketing. Es la interpretación que mejor honra el objetivo de Edgardo de filtrar basura. **Si preferís registro puro por teléfono (sin el guard de interés), avisame y saco esa condición de la Regla 26** — el resto del deploy no cambia.

---

## 9. Errata post-deploy — bug de tipo en `IF lead existe?` (2026-07-10)

**Qué pasó:** en producción, al re-invocar `registrar_datos_lead` para un lead que ya tenía fila en la planilla (rama UPDATE — la que corre `Lookup lead existente` → `IF lead existe?`), n8n tiró:

```
Wrong type: '1531778764' is a number but was expecting a string [condition 0, item 0]
Try either:
Enabling 'Convert types where required'
Converting the first field to a string by adding .toString()
```

**Causa raíz:** el nodo Google Sheets `Lookup lead existente` devuelve `subscriber_id` como **número** cuando el valor de la celda es todo dígitos (autodetección de tipo de columna de Google Sheets/n8n) — no como string, aunque la columna se escriba siempre como texto. El nodo `IF lead existe?` (heredado sin cambios desde v1) tenía el operator seteado a `type: "string"` con `typeValidation: "strict"` a nivel del grupo de condiciones → al comparar un valor `number` contra un chequeo tipado `string`, n8n aborta en vez de coercionar.

**No es un bug nuevo de v2** — este nodo nunca se tocó en el fix del 2026-07-08 (el fix de esa fecha fue en `Validate Input`, el trigger, y los nodos `Return`). Simplemente no se había disparado antes en ninguno de los tests previos porque ninguno había ejercitado la rama UPDATE con un `subscriber_id` puramente numérico contra el Lookup real de Sheets.

**Fix aplicado en vivo por la agencia** (2026-07-10): el operator de la condición `exists-check` pasó de

```json
{ "type": "string", "operation": "notEmpty" }
```
a
```json
{ "type": "number", "operation": "notEmpty", "singleValue": true }
```

Con esto el chequeo evalúa "¿hay un valor?" sin importar si Sheets lo tipó como number o string, y deja de chocar con `typeValidation: strict`.

**Repo actualizado:** `03_workflows/sys-tool-registrar-datos-lead-v3.json` (preserva `workflowId` `v9HD7P2uroG4Ni3A`) incorpora este fix sobre la base de v2. Es el archivo vigente para cualquier reimport futuro — v2.json queda solo como referencia histórica de cómo estaba antes del hotfix.

**Verificado post-fix** (`sys_tool_calls`, sesiones reales 2026-07-10 ~16:28-16:30 UTC): `wa_1253975717` y `wa_1531778764` — ambas `RESOLVED`, ambas con `tel_webhook = "{{phone}}"` (ManyChat falló, como es esperado que pase a veces) pero `tel_chat` con un número real (el lead lo escribió, el agente lo pidió y lo pasó bien) → el fallback agéntico funcionó end-to-end. Las dos filas quedaron en la planilla "SYS - Leads (Captura Emails)" con `origen: derivacion` — coincide con que llegaron vía la red estructural de `notificar_lead` (ver `06_docs/guia-notificar-lead-registra-en-planilla-2026-07-10.md`, ya aplicada y LIVE).

**Otras condiciones del mismo tipo — riesgo latente a revisar:** no se auditaron todavía el resto de los nodos `IF`/`Filter` de los demás sub-workflows tools de SYS en busca del mismo patrón (`typeValidation: strict` + operator `type: string` sobre un valor que puede llegar numérico desde Sheets/Airtable). Si vuelve a aparecer un error "Wrong type... is a number but was expecting a string", es probablemente el mismo patrón en otro nodo — aplicar el mismo fix (operator a `type: number` + `notEmpty` + `singleValue: true`, o activar "Convert types where required" a nivel del grupo de condiciones si se prefiere una solución más permisiva y única).
