# Incidente — Reconnect Messenger Chatrace bot 1444981

**Fecha de detección:** 2026-06-22
**Estado:** ABIERTO — escalado a soporte humano de Chatrace
**Severidad:** P2 (UI inaccesible, producción no afectada en canal principal)
**Bot afectado:** Heber Vera (`account_id: 1444981`)

---

## Síntomas

1. Al loguearse en Chatrace con las credenciales históricas (mail correcto, confirmado en incógnito sobre Safari) el dashboard muestra **"You don't manage any chatbot"** con un botón "Create New Account" y otro "Sign Out".
2. En la casilla del mismo mail llegó un correo automático de Chatrace con título **"Reconnect Messenger"** y body con `Account name: Heber Vera` + `Account ID: 1444981`.
3. El workflow productivo en n8n (`heber-vera-agente-principal-v1`) **sigue ejecutando** y procesando mensajes — el bot responde a los clientes.

## Diagnóstico

La desconexión es entre **Chatrace y la Página de Facebook/Instagram** del cliente, no entre la cuenta de usuario y el bot. Causas posibles: token de FB expirado, auditoría de seguridad de Meta, o remoción de la app Chatrace desde Meta Business Settings.

Mientras el OAuth no se restablezca, Chatrace oculta el bot del dashboard del usuario (de ahí el mensaje "You don't manage any chatbot"), aunque el bot sigue vivo en el servidor.

La hipótesis "te quitaron del equipo del bot" queda **descartada** por la prueba del correo de Reconnect, que es el patrón canónico de Chatrace cuando se cae el binding con Meta.

## Por qué n8n sigue respondiendo

Hipótesis confirmada vía API (2026-06-22): el canal principal del cliente es **WhatsApp**, que en Chatrace se vincula vía Cloud API + WABA token (no vía el OAuth de Facebook Page). La desconexión del mail solo afecta IG + FB Messenger, dejando WhatsApp operativo.

Evidencia: `GET https://api.chatrace.com/users/59893466058` con `X-ACCESS-TOKEN: 1444981.XqI...` devolvió subscriber real (Maria, UY, `+59893466058`) con:
- `account_id: 1444981` (bot correcto, sano)
- `archived: false`, `blocked: false`, `subscribed: "1"`
- `channel: "5"` + `wa_user_id: "UY.1637213574022184"` (canal WhatsApp)
- `subscribed_date: 2026-06-21 23:59:38` + `last_interaction` mismo día → bot recibiendo contactos nuevos en tiempo real

**Conclusión operativa:** producción no está degradada en el canal principal. La urgencia es recuperar acceso UI antes de que el agente humano de Chatrace responda — pero no hay riesgo de que se pierdan conversaciones de clientes mientras tanto.

## Acciones tomadas

| # | Acción | Status |
|---|--------|--------|
| 1 | Verificar credenciales correctas | ✅ Confirmado — mail correcto |
| 2 | Probar en incógnito | ✅ Mismo resultado |
| 3 | Abrir ticket con soporte Chatrace | ✅ Abierto 2026-06-22 |
| 4 | Soporte de primera línea responde y **escala a agente humano** | ✅ Escalado |

### Respuesta de soporte (primera línea, 2026-06-22)

> "I can't directly confirm from my side whether your specific user is still linked to bot 1444981, and I also can't restore/attach access to you without an agent checking your account permissions. I've escalated this to a human Chatrace support agent now.
>
> In the meantime, clicking 'Create New Account' will **typically create a new bot/account**, unless you reconnect using the exact same existing bot/account session (i.e., without creating a new one). So to avoid creating duplicates, it's safer to try reconnecting **inside the existing bot first** (if it's visible under your bots).
>
> When support replies, they can verify: (a) whether your user is still associated with bot 1444981 (c) whether they can restore your access from their side."

→ Confirma la sospecha: **NO usar "Create New Account"** sin antes esperar al agente humano. El path seguro es que soporte restaure el binding del usuario al bot existente.

## Pendientes

- [ ] **Bloqueante**: respuesta del agente humano de Chatrace
- [ ] Contactar a Eloísa para identificar qué Facebook personal es admin de la Página (necesario si soporte pide hacer OAuth)
- [x] Backup defensivo vía API: **conclusión 2026-06-22** — el token `1444981.XqI...` es de scope **Tools** (`/swagger/tools`), no admin. **No expone listados bot-level** (flows, custom_fields globales, tags, account info). Probes en vivo confirmados:
   - 🟢 `POST /users {phone:"+5989..."}` → find-or-create por teléfono (`{success, contact_created, data:{id}}`)
   - 🟢 `GET /users/{id}` → subscriber completo
   - 🟢 `GET /users/{id}/custom_fields` → custom field values del subscriber
   - 🟢 `GET /users/{id}/tags` → tags del subscriber
   - 🟢 `POST /users/{id}/send/{flow_id}` → dispara flow (lo que ya usa n8n)
   - 🟡 `/flows`, `/tags`, `/custom_fields`, `/account`, `/page`, `/me`, `/v1/*`, `/users/{id}/conversations` → 404 (no existen en scope tools)
   - 🔴 `/api/swagger/tools` sin token → 401 (token verificado server-side, sigue válido)

   **Implicancia:** no se puede exportar el bot completo desde la API. Los `flow_id` críticos (`1742402002782`+`1762181904878`) ya viven en `03_workflows/heber-vera-agente-principal-v1.json`. La memoria operativa del bot (flows definidos en Chatrace, mappings keywords→flow, sequences, config canal) sigue siendo inaccesible sin UI. Rescate por subscriber individual sí es posible si tenemos `user_id` o teléfono.
- [x] Verificar si WhatsApp está siendo el canal que mantiene n8n activo — **confirmado vía API** (`channel: "5"` + `wa_user_id` populado en subscriber reciente)

## Riesgo de mitigación incorrecta

Si se aprieta "Create New Account" sin coordinación, los riesgos son (en orden):
1. **Meta swap del page subscription** al bot nuevo → el bot 1444981 queda huérfano de Página y no se puede recuperar ni con soporte
2. Pérdida de subscribers, custom fields, flows (incluidos `1742402002782` y `1762181904878` hardcodeados en n8n), tags, persistent menu, API key
3. Reset del estado de ventana 24h por subscriber en IG/FB
4. Re-vinculación de WABA token + phone number ID

→ El costo de esperar al agente humano es bajo (WA sigue andando); el costo de un OAuth pifiado es permanente.

**Refuerzo 2026-06-22:** el sondeo API confirmó que el token de n8n NO permite hacer un export defensivo del bot completo. Eso ELEVA la importancia de no perder acceso UI — sin UI no hay forma de auditar/rebuildear flows o custom fields. La opción "rompí el bot pero después lo reconstruyo desde la API" no existe; solo se pueden rescatar subscribers individuales.

Confirmación adicional: soporte L1 explícitamente advirtió que "Create New Account" crea bot nuevo y recomendó "reconnect inside the existing bot first" — path que **solo está disponible si el agente humano restaura visibilidad del bot en el UI**.

## Próxima revisión

Reabrir incidente con la respuesta de soporte cuando llegue. Si llega path "reconnect inside existing bot", documentar el procedimiento exacto antes de ejecutar.

---

**Plan B documentado** (solo si soporte humano falla y se confirma que no hay forma de recuperar acceso UI al 1444981 sin OAuth nuevo): coordinar con Eloísa el OAuth con el FB admin de la Página, screenshotear todos los flow IDs y custom fields antes de empezar, y verificar después que el bot reconectado mantenga el ID `1444981`. Si aparece ID nuevo → frenar y volver a soporte.
