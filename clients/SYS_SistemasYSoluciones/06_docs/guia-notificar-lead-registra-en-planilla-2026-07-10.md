# Guía — Red estructural: `notificar_lead` registra en la planilla (2026-07-10)

> ✅ **APLICADA — LIVE (2026-07-09/10).** la agencia implementó Parte A + Parte B en el n8n vivo. **Verificado en producción** con 2 conversaciones reales del 2026-07-10 (`sys_tool_calls`, sesiones `wa_1253975717` y `wa_1531778764`): en ambas, `notificar_lead` derivó y `registrar_datos_lead` se disparó en el mismo flujo (`registro=true` en el pairing), y las 2 filas resultantes en la planilla "SYS - Leads (Captura Emails)" tienen `origen: derivacion` — la huella del valor fijo que este delta setea en el nodo `Registrar en planilla`. Pendiente solo el housekeeping de la nota 2 más abajo (re-exportar `notificar_lead` vivo como v5 para resincronizar el repo).

**Objetivo:** que **todo lead derivado** quede sí o sí en la planilla de captura, sin depender de que el LLM llame dos tools. Cierra el bug confirmado: en la conversación del 10/7, `notificar_lead` se disparó pero `registrar_datos_lead` no (el agente las trató como sustitutas).

**Idea:** cuando `notificar_lead` termina de derivar, llama a `registrar_datos_lead` (Execute Sub-workflow) con el mismo `telefono_webhook` determinístico. Reusa el gate + coalesce de registrar (única fuente de verdad). Si hay teléfono válido (de ManyChat o escrito por el lead), el lead queda en la planilla; si no, `registrar` devuelve `REJECTED` y no escribe nada — sin romper la derivación.

Complementa el prompt v2.7 (que ya le pide al agente registrar junto con derivar). El prompt es la primera línea; esto es la red por si el LLM falla.

---

## ⚠️ Por qué esto va como guía y NO como JSON para importar

El `sys-tool-notificar-lead-v4.json` del repo **está desincronizado con lo vivo**: tiene una conexión rota (el nodo Gmail se renombró a `Gmail Send (emarti + marketing)` pero la conexión quedó apuntando al nombre viejo `Gmail Send (CM + cc info@)`). Lo vivo SÍ manda el mail (está bien), o sea el repo v4 es un guardado a mitad de edición. **Importar un v5 armado desde ese repo pisaría producción y regresaría el mail.** Por eso: se aplica el delta a mano sobre el workflow vivo. NO importar un JSON completo de notificar_lead.

(Si en algún momento querés re-sincronizar el repo: exportá el notificar_lead vivo DESPUÉS de este cambio y guardalo como `sys-tool-notificar-lead-v5.json`.)

---

## Pre-requisito

`registrar_datos_lead` v2 tiene que estar deployado (ya lo está — el smoke del 10/7 con `telefono_webhook` dio RESOLVED). El nuevo nodo lo invoca por su `workflowId` `v9HD7P2uroG4Ni3A`.

---

## Parte A — Main: pasar `telefono_webhook` al nodo `notificar_lead`

Mismo patrón que ya aplicaste en el nodo `registrar_datos_lead`.

1. En el main, abrir el nodo toolWorkflow **`notificar_lead`** (apunta a `QI1gO4dZ5vXXo7V3`).
2. En **Workflow Inputs**, agregar un campo nuevo `telefono_webhook` con la expresión (determinística, NO `$fromAI`):
   ```
   ={{ $('Normalize Payload').item.json.phone }}
   ```
3. Dejar todo el resto igual (incluido `telefono` por `$fromAI`).

Con esto, cuando el agente deriva, `notificar_lead` recibe el número determinístico de ManyChat además del que haya pasado el LLM.

---

## Parte B — Sub-workflow `notificar_lead`: agregar el registro

1. En n8n abrir `notificar_lead` (`QI1gO4dZ5vXXo7V3`).

2. **Trigger** (`Execute Workflow Trigger`): en el `jsonExample`, agregar la línea `"telefono_webhook": ""` (para que el input se reconozca). Queda:
   ```json
   {
     "nombre": "",
     "telefono": "",
     "telefono_webhook": "",
     "ubicacion": "",
     "equipo_o_aplicacion": "",
     "mail": "",
     "empresa": "",
     "perfil": "Sin clasificar",
     "urgencia": false,
     "notas": "",
     "tecnologia_interes": "",
     "subscriber_id": "",
     "canal": "",
     "session_id": ""
   }
   ```

3. **Agregar el nodo `Registrar en planilla`.** Dos vías:

   **Vía clipboard:** copiar el contenido de `06_docs/snippets/clipboard-notificar-registrar-en-planilla-node-2026-07-10.json` y pegar (Cmd/Ctrl+V) en el canvas. Después **verificar en la UI** que:
   - El campo *Workflow* apunta a `sys-tool-registrar-datos-lead-v3` (`v9HD7P2uroG4Ni3A`).
   - El mapeo de inputs quedó como abajo (los nombres de parámetro del nodo "Execute Sub-workflow" varían un poco según la versión de n8n — confirmá que los 9 campos se mapean).

   **Vía UI (más robusto):** agregar un nodo **Execute Sub-workflow**, seleccionar `sys-tool-registrar-datos-lead-v3`, y mapear los inputs así:
   | Input (registrar) | Expresión |
   |---|---|
   | `nombre` | `={{ $('Validate Input').first().json.nombre }}` |
   | `telefono` | `={{ $('Validate Input').first().json.telefono }}` |
   | `telefono_webhook` | `={{ $('Validate Input').first().json.telefono_webhook }}` |
   | `email` | `={{ $('Validate Input').first().json.mail }}` |
   | `aplicacion_interes` | `={{ $('Validate Input').first().json.equipo_o_aplicacion }}` |
   | `origen` | `derivacion` (texto fijo) |
   | `canal` | `={{ $('Validate Input').first().json.canal }}` |
   | `subscriber_id` | `={{ $('Validate Input').first().json.subscriber_id }}` |
   | `session_id` | `={{ $('Validate Input').first().json.session_id }}` |

   Marcar el nodo con **Continue On Fail = true** (Settings del nodo) → si el registro falla, la derivación no se rompe.

4. **Cablear el nodo en el camino de éxito.** Hoy (en lo vivo) la cadena es:
   `Asignar a Jimena (ManyChat) → Gmail Send (emarti + marketing) → Update session_state → Format Output`.
   Insertar `Registrar en planilla` entre `Update session_state` y `Format Output`:
   - Borrar la conexión `Update session_state → Format Output`.
   - Agregar `Update session_state → Registrar en planilla`.
   - Agregar `Registrar en planilla → Format Output`.

   Resultado: `... → Update session_state → Registrar en planilla → Format Output → Log → Return`.

5. Guardar. Confirmar que `notificar_lead` sigue `active`.

---

## Cómo queda el comportamiento

| Caso | Qué pasa |
|---|---|
| Lead deriva con teléfono real (de ManyChat o escrito) | `notificar_lead` deriva + `registrar_datos_lead` (vía el nodo nuevo) hace upsert en la planilla → lead en la planilla ✅ |
| Agente ya había registrado antes en la conversación | El nodo nuevo llama a registrar → es un UPDATE (upsert por `subscriber_id`) → no duplica, no re-manda mail |
| Lead deriva pero ManyChat mandó `{{phone}}` y el lead no escribió número | `registrar` coalesce falla → `REJECTED` → NO escribe fila basura. La derivación sigue. (El prompt v2.7 debería evitar que se llegue acá; si igual pasa, no ensucia la planilla.) |

**Sobre el mail:** `registrar_datos_lead` manda su mail "nuevo lead" a emarti+marketing solo en ALTA nueva. Como `notificar_lead` también manda su mail de derivación a emarti+marketing, un lead derivado-sin-registro-previo genera 2 mails a esa casilla. Es el mismo patrón que ya existía cuando el agente registraba y derivaba por separado — no es nuevo. Si molesta, se puede silenciar el mail de registrar cuando lo llama notificar (agregando un flag `suppress_mail` a registrar) — avisá y lo hago.

---

## Smoke tests

| # | Escenario | Esperado |
|---|---|---|
| N1 | Derivación con teléfono real (WhatsApp con número, o lead que escribió los dígitos) | En `sys_tool_calls` aparecen DOS filas para la sesión: `notificar-lead` RESOLVED **y** `registrar-datos-lead` RESOLVED. Fila nueva/actualizada en la planilla con `telefono`. |
| N2 | Lead ya registrado por el agente, luego deriva | `registrar-datos-lead` (disparado por notificar) da RESOLVED con `already_exists=true`, sin duplicar la fila. |
| N3 | Deriva con `{{phone}}` y sin número escrito | `registrar-datos-lead` (disparado por notificar) da `REJECTED / telefono_invalido`. No hay fila nueva. La derivación (mail + asignación) igual ocurrió. |

**Query:**
```sql
SELECT created_at, tool_name,
       output_payload->>'status' AS status,
       output_payload->>'reason' AS reason
FROM sys_tool_calls
WHERE session_id = '<sessionKey del test>'
ORDER BY created_at;
```
Esperado en N1: ver `notificar-lead` y `registrar-datos-lead`, ambos RESOLVED, en la misma sesión.

---

## Rollback

Borrar el nodo `Registrar en planilla` y re-cablear `Update session_state → Format Output`. Quitar `telefono_webhook` del nodo `notificar_lead` del main. `notificar_lead` vuelve a derivar sin registrar (comportamiento previo).
