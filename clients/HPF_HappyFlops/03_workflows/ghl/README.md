# Workflows GHL — migración HPF

Workflows **nuevos**, creados al lado de producción (Regla 0: nada de lo vivo se toca).
Instancia `dev[TU-INSTANCIA-N8N]`, prefijo `HPF·GHL ·`, webhook paths propios.

| Archivo | n8n id | estado | rol |
|---|---|---|---|
| `W0-ghl-client.json` | `VK4M7VQm8CMefbty` | activo | el único workflow que habla con GHL |
| `W2-salida.json` | `MdbOREN56lfQTYlM` | activo | la única implementación de la cadencia de burbujas |
| `W3-catalogo.json` | `vSLHOawn2bFVXyOK` | activo | resuelve qué fichas mandar, con caché en Postgres |
| `W1-inbound.json` | `nA14dNwJ7VS3YMYr` | activo | entrada: idempotencia, identidad, gates, debounce |

| | regenerar | gate |
|---|---|---|
| W0 | `scripts/generators/hpf-gen-w0-ghl-client.py` | `scripts/testing/hpf-l3-w0.py` → **14/14** |
| W2 | `scripts/generators/hpf-gen-w2-salida.py` | `scripts/testing/hpf-l5-w2.py` → **6/6** |
| W3 | `scripts/generators/hpf-gen-w3-catalogo.py` | `scripts/testing/hpf-l5-w3.py` → **8/8** |
| W1 | `scripts/generators/hpf-gen-w1-inbound.py` | `scripts/testing/hpf-l6-w1.py` → **8/8 · 7/7 aristas** |

## W0 · GHL Client

8 nodos. Entrada `{op, args}` por dos vías —`executeWorkflowTrigger` (producción) y
webhook `hpf-w0-ghl-client` con header auth (pruebas)— que convergen en el mismo camino:
**el carril de test no es una rama aparte**, sólo cambia por dónde entró el pedido.

11 ops: `upsert_contact` · `get_contact` · `find_or_create_opportunity` · `get_opportunity` ·
`update_stage` · `update_cf` · `add_tag` · `remove_tag` · `send_text` · `send_media` ·
`search_products`.

Salida uniforme `{ok, op, http_status, via, data, error}`. **Un no-2xx hace `throw`**, no
devuelve el error como resultado — que es exactamente lo que rompió el intento anterior
(`06_docs/fix-tools-ghl-404-demo-telegram-2026-07-24.md`).

### Lo que W0 resuelve de entrada

- **User-Agent explícito.** Sin él Cloudflare devuelve `403 error_code 1010`.
- **`find_or_create` sin carrera.** `POST /opportunities/` optimista; el `400
  OPPORTUNITY_NO_DUPLICATE` trae `meta.existingId` y se traduce a éxito con `via: "existente"`.
  No se usa `/opportunities/search`, que tiene lag de indexación.
- **Campos custom por clave, no por id.** El llamador escribe `{"campos": {"cp_entrega": "44100"}}`
  y W0 resuelve el id contra el schema de 36 campos. Una clave desconocida **corta antes del PUT**:
  GHL la aceptaría, devolvería 200 y perdería el dato en silencio (T-17).
- **Checkbox y multi-opción se envuelven solos** en array; el llamador manda el valor suelto.
- **Etapas por nombre** (`"Cotizado"`) además de por UUID.

### Trampa encontrada

n8n **trunca los mensajes de error quedándose con el final** (~130 chars). Una excepción que
lista los 36 campos válidos pierde justo la parte que dice qué estuvo mal. Por eso los mensajes
son cortos y lo accionable va primero. Y el detalle del error **no llega al cuerpo del webhook**
(n8n responde un genérico `Workflow execution failed`): la evidencia real está en la ejecución,
vía `GET /api/v1/executions?workflowId=…&includeData=true`.

## W2 · Salida

12 nodos. Entrada `{contactId, partes, pausa_seg}` donde cada parte es `{texto, adjuntos?}`
o un string suelto. Recorre las partes llamando a W0 (`send_text` / `send_media` según haya
adjuntos), con una pausa **entre** burbujas — no después de la última.

Colapsa del origen: los 14 `actualizar*` (PATCH al campo 1099420), los 32 `Envio Mensaje*`
(`salesbot/run`), los 3 `Saludo PTE` y los `Wait` de 2 s. En GHL el envío es una sola llamada,
así que los dos pasos del salesbot desaparecen; la cadencia se conserva porque es lo que hace
que Rebeca no suene a bot.

Devuelve `{ok, partes_enviadas, enviados:[{seq, body, attachments, ghl_message_id,
ghl_conversation_id}]}`. Ese objeto **es** la evidencia del envío: permite releer cada mensaje
en GHL y comparar el texto byte a byte.

## Trampa de n8n que costó una iteración

**Un workflow devuelve al llamador la salida del último nodo ejecutado.** Si la rama termina
en una salida de `IF` sin nada conectado, devuelve `[]` — y el workflow de arriba se corta
en silencio, con la ejecución en verde.

W0 tenía exactamente eso: la rama de sub-workflow moría en el `false` del IF. Por webhook
andaba perfecto (el `Respond` disparaba), así que el gate de L3 lo daba por bueno; recién
apareció cuando W2 lo llamó de verdad. Por eso ahora **ambos** tienen un nodo terminal
explícito `Devolver al llamador`.

Lección para los workflows que faltan: **probar las dos vías de entrada**, no sólo el webhook.
Un carril que no se ejercita es un carril que diverge.

## W3 · Catálogo

13 nodos. Entrada `{evento, subcategoria?, productos?}` → salida `{cards[], sin_media[]}`.
Reemplaza `Formula` + `Search_Main_Image` + `Return_Formula` + `Search_Products` +
`Loop Over Items` + los parsers de la columna CURL de Airtable.

**Los datos viven en el custom object `custom_objects.fichas`** (65 registros, 58 con asset),
creado y poblado por `scripts/utilities/hpf-crear-objeto-fichas.py`. Es un objeto aparte de
`productos` a propósito: `productos` son los 15 SKU con precio/mínimo/peso para cotizar;
`fichas` son las tarjetas que el bot manda. Distinta granularidad, distinta tabla.

**Caché en la misma Postgres que la memoria del agente** (tabla `hpf_fichas`, TTL 15 min,
refresco perezoso). Tres razones:
- `records/search` de GHL tiene lag de indexación — comprobado en oportunidades y en fichas.
  En el camino caliente de una conversación eso no sirve.
- El filtro de Airtable era `AND({subcategoria}=X, OR(SEARCH(p1), SEARCH(p2)…))`. En SQL es
  directo; en `records/search` no hay equivalente.
- Es la Postgres que ya está cableada para `n8n_chat_histories`: una pieza menos.

El `CREATE TABLE IF NOT EXISTS` va en la misma consulta que el chequeo de frescura, así que
el workflow se autoinstala: no hay migración manual que alguien pueda olvidarse de correr.

El gate compara contra el catálogo de Airtable como oráculo: mismos filtros, mismas fichas.

## Trampas de n8n encontradas (van al registro)

1. **Un workflow devuelve la salida del último nodo ejecutado.** Si la rama termina en una
   salida de `IF` sin nada conectado, devuelve `[]` y el llamador se corta en silencio, con
   la ejecución en verde. Por eso los tres tienen `Devolver al llamador`.
   Apareció recién cuando W2 llamó a W0 de verdad: el gate de L3 sólo probaba el webhook.
2. **Un nodo con 0 filas no emite**, y la cadena se corta. "No hay ese producto para ese
   evento" es un caso conversacional legítimo → `alwaysOutputData` en el `SELECT`, no en el
   Code de después.
3. **n8n trunca los mensajes de error quedándose con el final** (~130 chars). Lo accionable
   va primero y corto.
4. **`pageLimit` de `records/search` acepta 100 sin problema.** El 403 que los docs previos
   le atribuían era el User-Agent (Cloudflare 1010). Con 100 entra el catálogo entero en una
   sola llamada.

## W1 · Inbound Handler (esqueleto)

23 nodos. Router y agentes stubbeados — eso es L7.

Reemplaza del origen: `New_Message`, `If25`, `Get_Contact`, `Clear_Contact_Data`,
`All_Data`, `No es IA`, `No es EEUU`, los 4 `Get_Entity*`, los gates
`If5/7/8/9/12/20/21/23`, `Si está en perdidos`, `En prod?*`, los `Memory_ID*` y los
15 nodos de los dos debounces.

### Tres piezas que no existían en el origen

**Idempotencia por `messageId`** — `INSERT ... ON CONFLICT DO NOTHING RETURNING`, atómico
(un get/set en Redis tiene carrera). En Kommo no hacía falta: su webhook respondía al
instante. Acá el debounce de 50 s garantiza timeout del webhook de GHL, y si GHL
reintenta el mismo mensaje entra dos veces.

**Respuesta temprana** — el ack sale apenas pasa idempotencia; el resto sigue async.
Es además lo que hace el origen, cuyo webhook no espera. Por eso la evidencia de los
tests no sale del cuerpo HTTP sino del `runData` de la ejecución.

**Resolución de identidad** — Kommo mandaba el lead ya creado; GHL manda un contacto.
`hpf_identity` deriva el `session_id` histórico (`<teléfono sin no-dígitos>2131`), así
los leads en curso no pierden la memoria en el cutover.

### Dos traducciones que corrigen bugs del origen

**Gates por igualdad de UUID.** En Kommo se hacían con `contains` sobre el JSON del lead
serializado: `"143"` (Ventas Perdidos) matcheaba cualquier timestamp que contuviera esos
dígitos. El mapeo Kommo→GHL de las 5 etapas de bloqueo está explícito en `Evaluar estado`,
con el id de Kommo como comentario.

**El debounce empuja el `messageId`, no `$workflow.id`.** El origen tenía este mecanismo
roto en la rama de imagen: empujaba una constante, así que "¿soy el último?" daba siempre
true y no deduplicaba. Es un DELTA deliberado.

### Contrato de entrada

Lo define **nuestro** WF-01 de GHL, no GHL: el paso "Webhook" de un GHL Workflow deja
mapear campos a mano. Si cambia allá, cambia en `Normalizar entrada`.

```json
{ "contactId": "...", "conversationId": "...", "messageId": "...",
  "body": "...", "attachments": [], "phone": "+52...", "canal": "WhatsApp" }
```

### Cobertura topológica — 7/7 aristas

`nuevo` · `duplicado` · `bloqueado` · `cliente_vuelve` · `seguir` · `gana_ultimo` ·
`pierde_debounce`. Ningún sumidero sin ejercitar.
