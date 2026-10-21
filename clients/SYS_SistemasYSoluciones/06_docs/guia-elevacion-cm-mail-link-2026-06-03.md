# Guía — Elevación al CM por mail + link directo a ManyChat (SYS)

**Fecha:** 2026-06-03
**Cliente:** SYS — Sistemas y Soluciones
**Decisión cliente:** Edgardo eligió **Opción 2** del menú de handover ("Mail con link directo al chat, el CM entra y responde desde ahí").

---

## Qué hace el cambio

Cuando el agente invoca `notificar_lead`, el sistema envía:

1. **Mail HTML al CM** (Community Manager) en el `TO` — con un **link directo al chat del lead en el dashboard de ManyChat**. El CM hace clic, ve toda la conversación previa con el bot, y toma control del chat para seguir respondiendo desde Live Chat.
2. **Copia (CC) a `info@sistemasysoluciones.com`** — para mantener visibilidad del equipo y backup histórico.
3. **Telegram a la agencia** — sin cambios (igual que hoy, visibilidad interna nuestra).

No se cambia el flujo del agente, **no se toca el system prompt vigente (v2.0)**, no se agregan tools nuevas. Solo cambia el sub-workflow `notificar_lead` y la forma en que el `toolWorkflow` del main lo invoca (le pasa `subscriber_id` + `canal` que antes no recibía).

**Adicionalmente — fix preventivo del bug Zod LangChain Episodio 2 (2026-06-05):** el v0.5 también aplica las descripciones `$fromAI` minimalistas a los 11 campos de `notificar_lead` y los 5 de `guardar_email`. Esto destraba el error `Received tool input did not match expected schema` que aparecía cuando el agente intentaba invocar la tool tras recolectar los datos del lead. Detalle del fix en sección "El bug Zod y cómo lo resuelve v0.5" más abajo.

---

## Estado del repo

Tras el refactor nuclear del 2026-06-03, el repo refleja la realidad de producción:

| Archivo | Qué es |
|---------|--------|
| [sys-agente-principal-v0.4.json](../03_workflows/sys-agente-principal-v0.4.json) | **Snapshot fiel del main vivo en n8n** post-nuclear (23 nodos, `consultar_catalogo` consolidada, nodo `Formatear mensaje`, Split Respuesta v3, prompt v2.0 inline). Pre-cambios de elevación CM y pre-fix Zod. |
| [sys-agente-principal-v0.5.json](../03_workflows/sys-agente-principal-v0.5.json) | **v0.4 + cambios de elevación CM aplicados + fix Zod en `notificar_lead` y `guardar_email`.** Nodos modificados: `notificar_lead` (apunta a sub-workflow v2, agrega `subscriber_id` + `canal` desde `Normalize Payload`, descripciones `$fromAI` minimalistas en 11 campos), `guardar_email` (descripciones `$fromAI` minimalistas en 5 campos como fix preventivo). El resto idéntico a v0.4. |
| [sys-tool-notificar-lead-v2.json](../03_workflows/sys-tool-notificar-lead-v2.json) | **Nuevo sub-workflow** que reemplaza al v1. Cambios vs v1: trigger acepta `subscriber_id` + `canal`; JS arma `live_chat_url`; Gmail HTML al CM con cc a info@; Telegram igual. |
| [sys-tool-notificar-lead-v1.json](../03_workflows/sys-tool-notificar-lead-v1.json) | Backup del sub-workflow vivo actual. No tocar. |

---

## Inputs que necesitamos de Edgardo

Bloquean la activación. Pedirlos antes de tocar n8n:

| Input | Para qué | Pendiente |
|-------|----------|-----------|
| **Mail del CM** | Destinatario `TO` del mail de notificación | ☐ |
| **Page ID de ManyChat** | Construir el link al chat. Es el número que va antes del `:` en el header `Bearer {PAGE_ID}:{API_KEY}` del credential `ManyChat - SYS` en n8n. Si no lo encuentra, lo sacás vos del backend (paso 2). | ☐ |

Mensaje sugerido a Edgardo:

> Para activar el handover por mail con link al chat necesito 2 datos: (1) el mail del CM al que tienen que llegar los leads, y (2) el Page ID de la cuenta ManyChat de SyS (lo tengo si me decís a quién consultar; si no, lo saco yo del backend). Con esos dos lo dejo activado.

---

## Implementación — paso a paso

### Paso 1: confirmar credencial Gmail SYS en n8n

1. En n8n → **Credentials** → buscar "Gmail SYS".
2. Si no existe, crear una credencial `Gmail OAuth2` autenticada con la cuenta de envío que usen (puede ser `info@sistemasysoluciones.com` o una cuenta noreply nuestra). Test con `getProfile` (botón "Test step" en la pantalla del credential).
3. **Anotá el credential ID** — n8n te va a pedir resolverlo al importar el sub-workflow.

### Paso 2: obtener el Page ID de ManyChat

Opción A — preguntar a Edgardo (más rápido).

Opción B — sacarlo del backend de n8n:
1. n8n → **Credentials** → abrir `ManyChat - SYS`.
2. Mostrar el header value (icono de ojo): formato `Bearer {PAGE_ID}:{API_KEY}`. Lo que está antes del `:` es el `PAGE_ID`.
3. Anotalo.

Validación rápida (opcional):
```bash
curl -s -H "Authorization: Bearer <PAGE_ID>:<API_KEY>" \
  https://api.manychat.com/fb/page/getInfo | jq .
```
Tiene que devolver info del page (`name`, `id`, etc.).

### Paso 3: importar el sub-workflow `sys-tool-notificar-lead-v2`

1. En n8n → **Workflows** → **Import from File**.
2. Cargar `clients/SYS_SistemasYSoluciones/03_workflows/sys-tool-notificar-lead-v2.json`.
3. n8n te va a pedir **resolver placeholders**:
   - **Gmail credential**: seleccionar `Gmail SYS` del paso 1.
   - **Telegram credential**: seleccionar la credencial existente "Telegram Bot Interno" (la misma que usás en otros workflows). Si no existe o no querés Telegram en producción, dejá el nodo deshabilitado (no es bloqueante — el flujo principal sigue).
   - **Postgres credential**: ya viene cableada a `Supabase SYS` (id `cQLxF5deDtmo4HTV`). Verificar que esa credential exista.
4. **Editar el nodo `Validate Input`**:
   - Reemplazar la línea `const PAGE_ID = '<<<MANYCHAT_PAGE_ID>>>';` por el valor real (paso 2). Por ejemplo:
     ```js
     const PAGE_ID = '123456789';
     ```
5. **Editar el nodo `Gmail Send (CM + cc info@)`**:
   - Campo `To`: reemplazar `<<<MAIL_CM>>>` por el mail real del CM.
   - Campo `CC` (en `options.ccList`): dejar `info@sistemasysoluciones.com` como está.
   - Verificar que el `Email Type` esté en `HTML`.
6. **Editar el nodo `Telegram Send (la agencia)`** (opcional):
   - `Chat ID`: reemplazar `<<<COMPLETAR_TELEGRAM_CHAT_ID_SYS>>>` por el chat ID del grupo Telegram interno donde la agencia recibe leads. Si no tenés grupo, dejá el nodo deshabilitado (el flujo igual funciona porque tiene `continueOnFail: true`).
7. **Activar el workflow** (toggle "Active" arriba a la derecha).
8. **Anotar el `workflowId` que asigna n8n** al sub-workflow (lo ves en la URL del workflow: `/workflow/<workflowId>`). Lo vas a usar en el paso 4 — aunque si n8n mantiene el mismo `workflowId` que el v1 (caso típico cuando re-importás encima), no necesitás cambiar nada en el main.

### Paso 4: importar el main `sys-agente-principal-v0.5`

1. En n8n → **Workflows** → abrir el `sys-agente-principal` actual (el vivo).
2. **Antes de importar, hacer backup:** en el menú `⋯` → `Download` → guardar el JSON actual como respaldo local (por si querés rollback rápido).
3. **Borrar el workflow actual** o **importar v0.5 reemplazando**:
   - Opción A — reemplazar: menú `⋯` → `Import from File` → cargar `sys-agente-principal-v0.5.json` → n8n reemplaza el contenido del workflow actual manteniendo el `workflowId`.
   - Opción B — crear nuevo: import como workflow nuevo, activarlo, desactivar el viejo. Recordá actualizar la URL del webhook si los IDs cambian.
4. n8n te va a pedir resolver las credenciales (las que aparecen referenciadas):
   - `Supabase SYS` → seleccionar.
   - `OpenAI` (para gpt-4o y gpt-4o-mini del formatter) → seleccionar.
   - `ManyChat - SYS` → seleccionar.
5. **Verificar el nodo `notificar_lead`** post-importación:
   - El campo **Workflow** del toolWorkflow node tiene que apuntar a `sys-tool-notificar-lead-v2`. Si quedó apuntando a v1, abrir el dropdown y cambiarlo a v2.
   - En **Workflow Inputs** verificar que aparezcan los 13 inputs (11 originales + `subscriber_id` + `canal`). Si por algún motivo no aparecen, agregar:
     ```
     subscriber_id  →  ={{ $('Normalize Payload').item.json.subId }}
     canal          →  ={{ $('Normalize Payload').item.json.canalLabel }}
     ```
6. **Activar el workflow** (toggle "Active").

> **Nota:** los demás nodos del main (`AI Agent` con prompt v2.0 inline, `Formatear mensaje`, `Split Respuesta`, `consultar_catalogo`, etc.) ya vienen exactamente iguales al estado actual de prod — no necesitás revisarlos uno por uno. Lo verifiqué con `diff` antes de generar el v0.5: el único cambio es el nodo `notificar_lead`.

### Paso 5: smoke test manual del sub-workflow

1. Abrir `sys-tool-notificar-lead-v2` en n8n.
2. Click en el nodo `Execute Workflow Trigger` → **Execute Step** con este payload (pegarlo en "Sample Data"):
   ```json
   {
     "nombre": "Smoke Test",
     "telefono": "1122334455",
     "ubicacion": "CABA",
     "equipo_o_aplicacion": "DTF textil para remeras",
     "mail": "test@example.com",
     "empresa": "Test SRL",
     "perfil": "Pyme",
     "urgencia": false,
     "notas": "Test E2E elevación CM",
     "tecnologia_interes": "DTF Textil",
     "subscriber_id": "1234567890",
     "canal": "WhatsApp",
     "session_id": "smoke-test-001"
   }
   ```
3. Verificar paso a paso:
   - `Validate Input` → output tiene `live_chat_url` poblada con formato `https://app.manychat.com/<PAGE_ID>/chat/1234567890`.
   - `Gmail Send` → ejecutó OK.
   - **Revisar inbox del CM y de `info@`**: tiene que llegar el mail con el botón "→ Abrir conversación en ManyChat". Click → abre el dashboard de ManyChat en el chat del subscriber `1234567890` (puede mostrar "subscriber not found" porque es un ID falso; lo importante es que la URL esté bien construida).
   - `Telegram Send` → si está cableado, notificación llega al grupo de la agencia.
   - `Update session_state` y `Log to sys_tool_calls` → filas nuevas en Supabase (verificar con cualquier consulta SQL al schema `sys_session_state` y `sys_tool_calls`).

### Paso 6: smoke test E2E desde el agente

1. Mandar mensaje real al webhook desde WhatsApp/IG/FB conectado a ManyChat. Llegar hasta el punto donde el agente invoca `notificar_lead`. Ejemplo:
   ```
   Cliente: Hola, necesito una impresora DTF para textil
   Cliente: Soy de CABA, mi nombre es Juan, teléfono 11 5555 5555
   Cliente: Quiero que un comercial me llame
   ```
2. Verificar:
   - El CM recibe el mail con link.
   - El link del mail abre el chat REAL del subscriber en ManyChat (no "not found").
   - El CM puede tomar el chat desde Live Chat (botón "Take over" o equivalente en la UI de ManyChat).
3. **El CM responde desde ManyChat** — verificar que el cliente lo recibe en el canal original (WA/IG/FB) y que el agente no le sobreescribe la respuesta.

### Paso 7: avisar a Edgardo + al CM

Una vez validado:

> Listo, dejé activado el handover por mail. Cada vez que el agente califica un lead, le va a llegar un mail al CM con un botón "Abrir conversación en ManyChat". Click → entra al chat → toma control desde Live Chat → responde. El mail también queda copiado a info@ para que ustedes tengan visibilidad. Avisame si querés que mande un ejemplo del mail para que el CM sepa qué esperar, o si prefieren que les explique el flujo en 5 minutos por llamada.

---

## Verificación final (checklist)

- [ ] Credencial Gmail SYS existe en n8n y pasa test.
- [ ] Page ID de ManyChat obtenido y reemplazado en el JS del nodo `Validate Input` del sub-workflow v2.
- [ ] Mail del CM obtenido y reemplazado en el `To` del Gmail Send del sub-workflow v2.
- [ ] Sub-workflow `sys-tool-notificar-lead-v2` importado, configurado y activo en n8n.
- [ ] Main `sys-agente-principal-v0.5` importado y activo. Nodo `notificar_lead` apunta al v2 y tiene `subscriber_id`/`canal` cableados.
- [ ] Smoke test manual del sub-workflow OK (mail llega al CM con link funcional, CC a info@).
- [ ] Smoke test E2E desde el agente OK (mail del CM lleva al chat real, CM puede tomar control).
- [ ] Edgardo + CM avisados del nuevo flujo.

---

## Notas y decisiones

- **Por qué no se toca el prompt:** tras el refactor nuclear (2026-06-03), el cliente está en producción con prompt v2.0 inline. Es la versión validada y vigente — no se reemplaza por v2.1/v2.2/v2.3 (esas eran iteraciones experimentales descartadas). La tool `notificar_lead` se documenta automáticamente al AI Agent vía el campo `description` del nodo `toolWorkflow` en el main; no hace falta editarlo en el prompt.

- **Por qué `cc` a info@ y no `bcc`:** que el CM vea explícitamente quién más tiene copia, así sabe que hay backup del equipo si necesita escalar. Si más adelante prefieren `bcc` para no llenar el mail del CM, cambiar en el nodo Gmail (campo `bccList` en `options`).

- **Por qué link a ManyChat y no a WhatsApp Business directo:** desde Live Chat de ManyChat el CM ve TODA la conversación previa con el bot (lo que es crítico para no repetir preguntas que ya hizo el agente). Si responde directo desde WA Business, no ve el historial.

- **Qué pasa si `subscriber_id` está vacío (test sin canal real):** el JS evita construir el link y el mail muestra el mensaje "⚠ Link directo no disponible". En producción, el `subscriber_id` viene siempre desde el `Normalize Payload` del main y nunca va a estar vacío.

- **¿Cuándo conviene asignar el chat al CM via API (en vez de solo mandarle link)?** Cuando el CM tenga su propio usuario en ManyChat con rol "Agent" (no admin). Ahí podemos cablear `setLiveChatAssignee` en el sub-workflow para asignar directamente y que el chat aparezca en su queue. Es Opción 1 del menú original (la que Edgardo descartó). Si en algún momento cambia de idea, el patrón está documentado en `clients/TFO_TOFO/06_docs/guia-asignacion-fallas-miguel-2026-05-26.md`.

- **Telegram queda como visibilidad interna:** la agencia sigue viendo los leads en el grupo Telegram (cuando lo cableemos). No se manda al CM porque Edgardo eligió mail; agregar Telegram también sería redundante y ruidoso para él.

- **Rollback rápido:** si algo falla en producción y querés volver al comportamiento previo, en el main vivo: abrir el nodo `notificar_lead` → cambiar el dropdown del campo `Workflow` de `sys-tool-notificar-lead-v2` a `sys-tool-notificar-lead-v1` (que sigue en n8n). 1 click + Save → comportamiento idéntico al pre-cambio. No hace falta re-importar nada.

---

## Próximos pasos (post-implementación, opcionales)

- **Captura de feedback:** después de 1 semana, preguntarle al CM si el flujo es cómodo o si quiere algún ajuste (formato del mail, qué campos destacar, frecuencia).
- **Migrar a Opción 1 si el volumen crece:** si los leads pasan los 5-10/día, vale la pena agregar al CM como user en ManyChat y asignar chats automáticamente (Opción 1). Hoy con baja volumetría, mail + link alcanza.
- **Reporte semanal al CM:** sumar al upsell CRM un reporte semanal con KPIs (# leads recibidos, # tomados, % conversión). Descripto en `ops/04_upsells/SYS-upsell-crm-leads-2026-05-28.md`.

---

## El bug Zod y cómo lo resuelve v0.5

### Síntoma observado durante el smoke test E2E

Al ejecutar el paso 6 (los 3 mensajes de prueba con el agente), después de que el cliente pasa nombre + teléfono + ubicación, el agente pide el mail y luego al intentar invocar la tool falla con `Received tool input did not match expected schema`. La fila en `sys_tool_calls` queda con `status='ERROR'` y `output_payload` típicamente vacío `{}`.

### Causa raíz (documentada en postmortem 2026-06-05)

Las descripciones `$fromAI` de los nodos `notificar_lead` y `guardar_email` traían frases como `"Opcional:"`, `"Si no, dejar vacío"`, `"Si no estás seguro"`, `"(ej: CABA, Mar del Plata, Salta)"`. Estas frases hacen que el LLM **omita** el campo del JSON cuando no lo tiene claro. LangChain sintetiza el schema con todos los campos esperados; Zod en strict mode encuentra los campos ausentes y rechaza el call.

### Fix aplicado en v0.5

3 reglas combinadas:

1. **Descripciones `$fromAI` minimalistas** (5-12 palabras), sin "Opcional", "Si no...", ejemplos entre paréntesis, ni instrucciones lógicas. Ejemplos en v0.5:
   - `nombre` → `'Nombre del lead'` (antes: `'OBLIGATORIO: nombre del lead'`)
   - `empresa` → `'Empresa del lead'` (antes: `'Opcional: empresa si corresponde'`)
   - `urgencia` → `'Urgencia del lead: true o false'` (antes: `'Opcional: pasá la string true si... sino false o dejá vacío'`)
2. **`Required = false`** en todos los campos `$fromAI` (la obligatoriedad la enforce el sub-workflow vía Validate Input, no LangChain/Zod).
3. **`Type = 'string'`** en todos (sin `'json'` ni `'number'` que rompen el schema).

Adicionalmente, la `description` del nodo (la descripción de la tool que ve el AI Agent) ahora incluye explícitamente: *"Pasá TODOS los args con la información que hayas recolectado de la conversación — si no tenés un dato, pasalo como string vacío, no omitas argumentos."* Esto refuerza el comportamiento esperado.

### Si preferís fixear los nodos en vivo (sin re-importar todo el main)

Si ya importaste el main vivo y solo querés aplicar el fix Zod sin re-cargar el JSON entero, podés reemplazar los 2 nodos uno por uno con los snippets de abajo:

#### JSON del nodo `notificar_lead` (clipboard, listo para `Ctrl+V`)

```json
{
  "meta": { "instanceId": "sys-notificar-lead-zod-fix-2026-06-05" },
  "nodes": [
    {
      "parameters": {
        "description": "ÚNICA tool de escritura. Notifica al equipo comercial sobre un lead calificado (mail al CM con link directo al chat de ManyChat + cc a info@sistemasysoluciones.com + Telegram interno la agencia). Invocá SOLO cuando tengas los 4 datos obligatorios: nombre + telefono + ubicacion + equipo_o_aplicacion. Pasá TODOS los args con la información que hayas recolectado de la conversación (empresa, perfil, tecnologia_interes, notas, urgencia, mail) — si no tenés un dato, pasalo como string vacío, no omitas argumentos. La tool valida internamente y rechaza el call si faltan los 4 obligatorios.",
        "workflowId": {
          "__rl": true,
          "value": "QI1gO4dZ5vXXo7V3",
          "mode": "list",
          "cachedResultUrl": "/workflow/QI1gO4dZ5vXXo7V3",
          "cachedResultName": "sys-tool-notificar-lead-v2"
        },
        "workflowInputs": {
          "mappingMode": "defineBelow",
          "value": {
            "nombre": "={{ $fromAI('nombre', `Nombre del lead`, 'string') }}",
            "telefono": "={{ $fromAI('telefono', `Teléfono del lead`, 'string') }}",
            "ubicacion": "={{ $fromAI('ubicacion', `Ubicación o localidad del lead`, 'string') }}",
            "equipo_o_aplicacion": "={{ $fromAI('equipo_o_aplicacion', `Equipo o aplicación que consulta el cliente`, 'string') }}",
            "mail": "={{ $fromAI('mail', `Mail del lead`, 'string') }}",
            "empresa": "={{ $fromAI('empresa', `Empresa del lead`, 'string') }}",
            "perfil": "={{ $fromAI('perfil', `Perfil del lead: Distribuidor, Pyme, Emprendedor o Sin clasificar`, 'string') }}",
            "urgencia": "={{ $fromAI('urgencia', `Urgencia del lead: true o false`, 'string') }}",
            "notas": "={{ $fromAI('notas', `Notas adicionales sobre el lead`, 'string') }}",
            "tecnologia_interes": "={{ $fromAI('tecnologia_interes', `Tecnología de interés del lead`, 'string') }}",
            "subscriber_id": "={{ $('Normalize Payload').item.json.subId }}",
            "canal": "={{ $('Normalize Payload').item.json.canalLabel }}",
            "session_id": "={{ $('Normalize Payload').item.json.leadIdentifier }}"
          },
          "matchingColumns": [],
          "schema": [
            { "id": "nombre", "displayName": "nombre", "required": false, "defaultMatch": false, "display": true, "canBeUsedToMatch": true, "type": "string" },
            { "id": "telefono", "displayName": "telefono", "required": false, "defaultMatch": false, "display": true, "canBeUsedToMatch": true, "type": "string" },
            { "id": "ubicacion", "displayName": "ubicacion", "required": false, "defaultMatch": false, "display": true, "canBeUsedToMatch": true, "type": "string" },
            { "id": "equipo_o_aplicacion", "displayName": "equipo_o_aplicacion", "required": false, "defaultMatch": false, "display": true, "canBeUsedToMatch": true, "type": "string" },
            { "id": "mail", "displayName": "mail", "required": false, "defaultMatch": false, "display": true, "canBeUsedToMatch": true, "type": "string" },
            { "id": "empresa", "displayName": "empresa", "required": false, "defaultMatch": false, "display": true, "canBeUsedToMatch": true, "type": "string" },
            { "id": "perfil", "displayName": "perfil", "required": false, "defaultMatch": false, "display": true, "canBeUsedToMatch": true, "type": "string" },
            { "id": "urgencia", "displayName": "urgencia", "required": false, "defaultMatch": false, "display": true, "canBeUsedToMatch": true, "type": "string" },
            { "id": "notas", "displayName": "notas", "required": false, "defaultMatch": false, "display": true, "canBeUsedToMatch": true, "type": "string" },
            { "id": "tecnologia_interes", "displayName": "tecnologia_interes", "required": false, "defaultMatch": false, "display": true, "canBeUsedToMatch": true, "type": "string" },
            { "id": "subscriber_id", "displayName": "subscriber_id", "required": false, "defaultMatch": false, "display": true, "canBeUsedToMatch": false, "type": "string" },
            { "id": "canal", "displayName": "canal", "required": false, "defaultMatch": false, "display": true, "canBeUsedToMatch": false, "type": "string" },
            { "id": "session_id", "displayName": "session_id", "required": false, "defaultMatch": false, "display": true, "canBeUsedToMatch": true, "type": "string" }
          ],
          "attemptToConvertTypes": true,
          "convertFieldsToString": true
        }
      },
      "id": "30211bea-0ebf-4b94-a85b-50134062e31a",
      "name": "notificar_lead",
      "type": "@n8n/n8n-nodes-langchain.toolWorkflow",
      "typeVersion": 2.2,
      "position": [-112, 288]
    }
  ],
  "connections": {}
}
```

**Cómo pegarlo en n8n:** abrir el main vivo → borrar el nodo `notificar_lead` actual → `Ctrl+V` con el JSON copiado → el nodo aparece en `[-112, 288]` → abrir el nodo, en **Workflow** seleccionar `sys-tool-notificar-lead-v2` desde el dropdown → reconectar la salida del nodo a la pata `Tool` del AI Agent → guardar.

#### JSON del nodo `guardar_email` (clipboard, listo para `Ctrl+V`)

```json
{
  "meta": { "instanceId": "sys-guardar-email-zod-fix-2026-06-05" },
  "nodes": [
    {
      "parameters": {
        "description": "Persiste el email del cliente en Google Sheets apenas se captura. Invocá esta tool en el MISMO turno en que el cliente comparte su email (por novedades, por derivación, o espontáneo). No esperes al cierre. Es independiente de notificar_lead — pueden coexistir en el mismo turno. Pasá TODOS los args con la información que hayas recolectado de la conversación (nombre, telefono, origen, aplicacion_interes) — si no tenés un dato, pasalo como string vacío, no omitas argumentos. Si already_exists=true en el output, no lo menciones al cliente: seguí natural.",
        "workflowId": {
          "__rl": true,
          "value": "v9HD7P2uroG4Ni3A",
          "mode": "list",
          "cachedResultUrl": "/workflow/v9HD7P2uroG4Ni3A",
          "cachedResultName": "sys-tool-guardar-email-v1"
        },
        "workflowInputs": {
          "mappingMode": "defineBelow",
          "value": {
            "email": "={{ $fromAI('email', `Email del cliente en formato xxx@xxx.xxx`, 'string') }}",
            "nombre": "={{ $fromAI('nombre', `Nombre del cliente`, 'string') }}",
            "telefono": "={{ $fromAI('telefono', `Teléfono del cliente`, 'string') }}",
            "origen": "={{ $fromAI('origen', `Motivo del email. Valores: newsletter, derivacion, descuento_insumos, otro`, 'string') }}",
            "aplicacion_interes": "={{ $fromAI('aplicacion_interes', `Aplicación o equipo que el cliente consulta`, 'string') }}",
            "canal": "={{ $('Normalize Payload').item.json.canalLabel }}",
            "subscriber_id": "={{ $('Normalize Payload').item.json.subId }}",
            "session_id": "={{ $('Normalize Payload').item.json.sessionKey }}"
          },
          "matchingColumns": [],
          "schema": [
            { "id": "email", "displayName": "email", "required": false, "defaultMatch": false, "display": true, "canBeUsedToMatch": true, "type": "string", "removed": false },
            { "id": "nombre", "displayName": "nombre", "required": false, "defaultMatch": false, "display": true, "canBeUsedToMatch": true, "type": "string", "removed": false },
            { "id": "telefono", "displayName": "telefono", "required": false, "defaultMatch": false, "display": true, "canBeUsedToMatch": true, "type": "string", "removed": false },
            { "id": "aplicacion_interes", "displayName": "aplicacion_interes", "required": false, "defaultMatch": false, "display": true, "canBeUsedToMatch": true, "type": "string", "removed": false },
            { "id": "origen", "displayName": "origen", "required": false, "defaultMatch": false, "display": true, "canBeUsedToMatch": true, "type": "string", "removed": false },
            { "id": "canal", "displayName": "canal", "required": false, "defaultMatch": false, "display": true, "canBeUsedToMatch": true, "type": "string", "removed": false },
            { "id": "subscriber_id", "displayName": "subscriber_id", "required": false, "defaultMatch": false, "display": true, "canBeUsedToMatch": true, "type": "string", "removed": false },
            { "id": "session_id", "displayName": "session_id", "required": false, "defaultMatch": false, "display": true, "canBeUsedToMatch": true, "type": "string", "removed": false }
          ],
          "attemptToConvertTypes": true,
          "convertFieldsToString": true
        }
      },
      "type": "@n8n/n8n-nodes-langchain.toolWorkflow",
      "typeVersion": 2.2,
      "position": [656, 288],
      "id": "9ea6c015-80a9-4454-8d93-7478fd2b989d",
      "name": "guardar_email"
    }
  ],
  "connections": {}
}
```

**Cómo pegarlo en n8n:** mismo procedimiento que el de `notificar_lead`, pero con este JSON. Posición `[656, 288]`. Reconectar a la pata `Tool` del AI Agent.

### Verificación post-fix

Después de aplicar los 2 nodos actualizados (o de importar el v0.5 entero), repetir el smoke test del paso 6 con los mismos 3 mensajes. Esperado:

1. Agente pide el mail (paso natural).
2. Cliente da el mail.
3. Agente invoca `guardar_email` y `notificar_lead` en el mismo turno (es válido, las dos son independientes).
4. **Sin error Zod.** Filas nuevas en `sys_tool_calls` con `status='RESOLVED'` para ambas.
5. Mail al CM llega con link funcional.
6. Fila nueva en Google Sheet "SYS - Leads (Captura Emails)" con el mail capturado.

### Postmortems relacionados

- [incidente-bug-zod-langchain-2026-06-03.md](incidente-bug-zod-langchain-2026-06-03.md) — Episodio 1 (refactor nuclear de catálogo).
- [guia-fix-guardar-email-zod-2026-06-05.md](guia-fix-guardar-email-zod-2026-06-05.md) — Episodio 2 (este fix); guía original detallada por nodo. La presente guía aplica una versión consolidada del mismo fix dentro del v0.5.
