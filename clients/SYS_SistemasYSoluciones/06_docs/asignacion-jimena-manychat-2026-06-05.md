# Asignación automática a Jimena via ManyChat (SYS)

**Fecha:** 2026-06-05
**Contexto:** Add-on al sub-workflow `sys-tool-notificar-lead-v2`. Cuando el agente eleva un lead, además de mandar mail al CM con link, el sistema asigna la conversación a Jimena en ManyChat y pausa el bot para esa session.

---

## Por qué un nodo HTTP a `sendFlow` y no asignación directa

La API pública de ManyChat v2 **no expone endpoint** para asignar Live Chat a un usuario ni para pausar automation a nivel de subscriber. Lo único que se puede hacer programáticamente es ejecutar un flow del workspace via `POST /fb/sending/sendFlow`. Por eso la única opción viable es:

1. Crear un **flow custom en ManyChat** con dos acciones:
   - `Conversation → Assign to → Jimena`
   - `Automation → OFF` (pausa el bot para esa session)
2. Disparar ese flow desde n8n con un nodo HTTP que llama a `sendFlow` pasando el `subscriber_id` del lead.

Patrón ya validado en TFO (`Elevar Miguel` / `Elevar a Mauricio`).

---

## Setup en ManyChat (Edgardo/la agencia)

1. Crear un nuevo **Flow** en ManyChat → nombre sugerido: `SYS – Asignar a Jimena`.
2. Como primer paso del flow, agregar la **Action**: `Conversation → Assign to` → seleccionar usuario `Jimena`.
3. Segundo paso opcional pero recomendado: **Action**: `Automation → Set to OFF` (así el bot no responde mientras Jimena maneja el chat).
4. Guardar y publicar.
5. Copiar el **Flow Namespace** (`flow_ns`): Settings del flow → API → copiar el string tipo `content20251129220130_658273`.

---

## Setup en n8n

1. Sub-workflow `sys-tool-notificar-lead-v2` ya tiene incorporado el nodo HTTP `Asignar a Jimena (ManyChat)` entre `Telegram Send (la agencia)` y `Update session_state`.
2. Abrir ese nodo y configurar:
   - **Credential**: seleccionar `ManyChat - SYS` (la misma que usan `setCustomFields` y `sendFlow` del main).
   - **Body JSON** → reemplazar `<<<COMPLETAR_FLOW_NS_ASIGNAR_JIMENA>>>` por el `flow_ns` copiado del paso anterior.

---

## JSON del nodo (clipboard, listo para `Ctrl+V` si preferís pegarlo en lugar de re-importar el sub-workflow)

```json
{
  "meta": { "instanceId": "sys-asignar-jimena-2026-06-05" },
  "nodes": [
    {
      "id": "a7e2c3f1-9d4b-4c8e-b2a5-1e8f6d3c7b91",
      "name": "Asignar a Jimena (ManyChat)",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [840, 300],
      "parameters": {
        "method": "POST",
        "url": "https://api.manychat.com/fb/sending/sendFlow",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            { "name": "Accept", "value": "application/json" }
          ]
        },
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={\n  \"subscriber_id\": \"{{ $('Validate Input').first().json.subscriber_id }}\",\n  \"flow_ns\": \"<<<COMPLETAR_FLOW_NS_ASIGNAR_JIMENA>>>\"\n}",
        "options": {}
      },
      "credentials": {
        "httpHeaderAuth": {
          "id": "<<<COMPLETAR_MANYCHAT_SYS_CRED_ID>>>",
          "name": "ManyChat - SYS"
        }
      },
      "continueOnFail": true,
      "notes": "Dispara el flow de ManyChat que asigna la conversación a Jimena + pausa el bot. flow_ns y Credential a completar."
    }
  ],
  "connections": {}
}
```

Después de pegarlo: conectar la salida de `Telegram Send (la agencia)` al input del nodo nuevo, y la salida del nodo nuevo a `Update session_state`. Guardar.

---

## Verificación

Smoke test del sub-workflow con el payload de prueba del paso 5 de la guía principal. Esperado:

1. Mail llega al CM con link.
2. Telegram a la agencia (si está cableado).
3. **En ManyChat**: la conversación del subscriber de prueba aparece asignada a Jimena en Live Chat, y el bot deja de responder a esa session hasta que Jimena resuelva o re-active automation manualmente.
4. Fila en `sys_tool_calls` con `status='RESOLVED'`.

Si el HTTP a ManyChat falla (`401`, `flow_ns invalid`, etc.), `continueOnFail: true` evita que se rompa el resto del sub-workflow — el mail al CM y el Telegram ya se enviaron, sólo se pierde la asignación automática (Jimena la puede tomar manualmente desde el link del mail).
