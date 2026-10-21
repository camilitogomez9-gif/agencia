# v16 — Telegram con el CRM real de GHL (build para que pruebe Oscar)

**Fecha:** 2026-07-24 · **Archivo:** `HPF Inbound Handler (v16 - telegram + CRM real).json` (101 nodos)
**Base:** `v12` (arquitectura de producción) + system prompt del `v14`

---

## 0. Estado real — qué está vivo hoy (actualizado 2026-07-24, 21:30)

**Este v16 NO está deployado.** Lo que corre en n8n es `HPF Inbound Handler` (id `IPO1c36NLzkXrBh9`,
active, 64 nodos, snapshot en `03_workflows/hpf-inbound-handler-live-2026-07-24.json`): el **v14 - demo
telegram con las 3 tools de CRM restauradas a la versión del v12**. El prompt sigue siendo el del v14,
con el marcador `[IMAGEN:XX]`.

Esa combinación deja tres cosas rotas, verificadas sobre el export:

| Qué | Por qué |
|---|---|
| **El CRM no escribe nada** | El adaptador sigue fabricando `opportunity_id = tg_opp_<chatid>` y usa el chat id como `contact_id` → cada tool call es un 404. Y una `toolHttpRequest` que falla le devuelve el texto del error al LLM dejando el nodo en verde: volvió el bug que reportó Oscar. |
| **No llega ninguna imagen** | `Send Photo (Telegram)` se quedó sin parámetro de foto. El v14 lo guardaba como `fileId`, que en `sendPhoto` no existe (el correcto es `file`; `fileId` es de `resource: file / operation: get`), así que n8n descartó la clave al re-guardar el nodo. **El envío de fotos nunca funcionó.** Fix de 1 parámetro: `06_docs/snippets/clipboard-send-photo-telegram-fix-2026-07-24.json`. |
| **El debounce está en 0s** | El nodo se llama `Wait 15s (Debounce)` pero su `amount` es `0` → contesta burbuja por burbuja. |

Además, por venir del v14: no hay saludo fijo, no se mueven etapas y el contexto `[7]` del prompt llega
vacío (`Auth + Normalize` hardcodea `stage: 'Evento Identificado'`).

**La decisión de fondo es una sola:** o se deploya este v16 (y el CRM anda por Telegram ya mismo), o se
vuelven las 3 tools a stub hasta que entre la WABA. Hoy estamos en el peor de los dos mundos: pegan a
GHL, fallan, y el error viaja al LLM.

---

## 1. Qué cambia respecto del build vivo

El build vivo tiene las tools apuntando a GHL pero con ids inventados, el contexto `[7]` del prompt vacío
y el envío de fotos roto (ver §0).

El v16 **es el agente de producción corriendo por Telegram**. Todo lo que hace en la WABA lo hace acá:

| Función | Build vivo | v16 |
|---|---|---|
| Contacto y oportunidad en GHL | inventados (`tg_opp_<chatid>`) → 404 | reales (`/contacts/upsert` + `/opportunities/search` + create) |
| `IDENTIFICAR_EVENTO` / `MOSTRAR_PRODUCTOS` / `COTIZADOR` | 404, y el error viaja al LLM | escriben los custom fields reales |
| `ATENCION_PERSONALIZADA` | 404 contra GHL | aplica el tag `atencion_humana` + notifica |
| Contexto `[7]` del prompt (evento, cantidades, CP, cotización) | vacío | leído del Opportunity |
| Etapas del pipeline | ninguna | se mueven solas (Lead Nuevo → … → Cotizado → Esperando Pago → Pago Confirmado) |
| Saludo fijo de 3 partes | no existe por Telegram | lo manda n8n, igual que WF-01 |
| Imagen del evento + promo | vía marcador `[IMAGEN:XX]`, pero el nodo de foto está roto | se envía al identificar el evento (nodo corregido) |
| Fichas de producto | no existen | se envían las que tienen asset estable |
| Comprobante de pago | movía un id falso | mueve la etapa real y responde |

**Lo único distinto de producción es el canal.** Cuando se conecte la WABA, la rama de GHL ya está
cableada en paralelo (`Es Origen Telegram?` × 4) y no hay que reconstruir nada.

### Sobre el prompt

El system prompt del v14 y el del v12 son **idénticos salvo 3 bloques**, y esos 3 bloques eran justamente
las degradaciones de la demo (el marcador `[IMAGEN:XV]` y el "hoy no podés enviar fotos"). Toda la estética
conversacional (`[1b]`: minúsculas, sin signos de apertura, una idea por burbuja) ya estaba en el v12.

El v16 usa el prompt del v14 con 5 cambios, ninguno toca las 12 reglas inviolables ni el formato `[8]`:

1. Stage "Saludo Enviado" → el sistema manda la imagen; el agente no la anuncia (se elimina el marcador).
2. Stage "Evento Identificado" → habilita el envío de fichas sin permitir que las prometa.
3. Pedido de catálogo/foto → invoca `MOSTRAR_PRODUCTOS` (antes solo describía).
4. **Regla 15 nueva:** prohíbe filtrarle al lead el texto de error de una herramienta.
   Motivo: verificado en el código de n8n — cuando una `toolHttpRequest` falla, el agente recibe
   `HTTP 404 There was an error: "..."` **como si fuera un resultado válido** y el nodo queda en verde.
   Es exactamente lo que produjo el 404 que reportaste.
5. `[7]` ahora incluye la fecha de hoy en zona México (gap #3 del paneo).

---

## 2. Antes de importar — 3 curls de pre-flight

El workflow no tiene ningún stage id ni custom field id hardcodeado: los resuelve en runtime.
Pero necesita que el PIT `GHL PIT HPF` tenga los scopes de lectura. Corré esto con el token real:

```bash
PIT="pit-....."   # el valor de la credencial "GHL PIT HPF" en n8n
LOC="onRwi0ZF4uYi0Lp6GAbE"
H=(-H "Authorization: Bearer $PIT" -H "Version: 2021-07-28")
curl -s "${H[@]}" "https://services.leadconnectorhq.com/locations/$LOC" | head -c 300
curl -s "${H[@]}" "https://services.leadconnectorhq.com/opportunities/pipelines?locationId=$LOC" | head -c 600
curl -s "${H[@]}" "https://services.leadconnectorhq.com/locations/$LOC/customFields?model=opportunity" | head -c 600
```

- El **1°** confirma que `onRwi0ZF4uYi0Lp6GAbE` es la sub-cuenta de Happy Flops. Ese id está inferido de
  las URLs de la Media Library (`assets.cdn.filesafe.space/<locationId>/media/...`); no está escrito en
  ningún doc del repo — `01_setup_ghl.md:21` quedó con el campo en blanco.
- El **2°** debe devolver el pipeline `Happy Flops IA` con sus 13 etapas.
- El **3°** debe devolver los custom fields con `fieldKey` tipo `opportunity.evento_detectado`.

Si alguno da 401/403, falta un scope en el PIT (`opportunities.readonly`, `locations/customFields.readonly`,
`contacts.write`, `opportunities.write`). Si el 2° o el 3° fallan, el bot igual responde: cae a los ids
hardcodeados históricos y sigue conversando, pero no mueve etapas.

### ⚠️ Un chequeo más, en la UI de GHL (30 segundos, pero es el que puede arruinar la demo)

**Settings → Business Profile → Contact Deduplication Preferences → campo primario = Email.**

Telegram no da teléfono, así que la identidad del lead se ancla al email sintético
`tg-<chatid>@telegram.[TU-DOMINIO]`. `POST /contacts/upsert` **no dedupea por el payload**: respeta ese
setting de la sub-cuenta. Si el campo primario está en *Phone* y no hay secundario, un upsert sin teléfono
se queda sin clave de match y **crea un contacto nuevo en cada mensaje**.

Síntoma inconfundible si pasa: el bot manda el saludo de 3 partes **en cada mensaje** y en GHL aparece un
contacto y una oportunidad nuevos por cada cosa que escribís. Si lo ves, es esto y no otra cosa.

---

## 3. Import

1. Importar `HPF Inbound Handler (v16 - telegram + CRM real).json` como workflow **nuevo** (viene sin `id`).
2. Verificar credenciales (viajan referenciadas por id, pero conviene mirar):
   `GHL PIT HPF` · `HPF` (Telegram) · `H.F` (OpenAI) · `H.F` (Postgres).
3. El nodo `Webhook - Inbound` **pierde el binding de la credencial Header Auth en cada import** — es un
   problema conocido. No afecta a Telegram; re-seleccionarla solo cuando se use la rama de producción.
4. Desactivar el v14 antes de activar el v16 (los dos escuchan el mismo bot de Telegram).
5. `Notificar equipo (Telegram)` avisa cuando el agente deriva a un humano. Está apuntando al chat de la agencia
   (`6390727286`); cambiarlo por el de Oscar o el del grupo del equipo cuando se defina.

---

## 4. Recorrido de verificación (correr antes de dárselo a Oscar)

Es el recorrido de 8 pasos del paneo, con lo que hay que mirar **en GHL** en cada uno:

| # | Mandás por Telegram | Esperado en el chat | Esperado en GHL |
|---|---|---|---|
| 1 | `hola` | los 3 mensajes del saludo fijo, con 2s entre cada uno | contacto nuevo + oportunidad en **Saludo Enviado** |
| 2 | `es para unos XV` | respuesta del agente + **imagen del catálogo XV** + promo | `evento_detectado = XV`, etapa **Evento Identificado** |
| 3 | `quiero sandalias y cilindros` | descripción en texto + **ficha de cilindros y de kit anticruda** | `productos_mostrados`, etapa **Productos Mostrados** |
| 4 | `100 sandalias delgadas y 50 cilindros, CP 44100` | cotización con `Envío: $400 · Total: $3,400 · Anticipo: $1,700` + los 7 pasos | `monto_cotizado_mxn = 3400`, etapa **Cotizado** |
| 5 | foto de un comprobante | "¡Recibí tu comprobante! 🎉…" | etapa **Esperando Pago** + `payment_proof_detectado` |
| 6 | un audio | responde al contenido del audio | — |
| 7 | un sticker | responde con naturalidad, no se cae | — |
| 8 | `/b` | "arranqué de cero…" | oportunidad de vuelta en **Lead Nuevo**, campos limpios y el tag `atencion_humana` removido |

Un caso más que conviene probar: pedile **"quiero hablar con una persona"**. El agente debe llamar a
`ATENCION_PERSONALIZADA` → el contacto queda taggeado `atencion_humana` en GHL, te llega el aviso por
Telegram, y a partir de ahí **el bot deja de responder** (es el comportamiento de producción: el humano
tomó la conversación). Para reactivarlo: `/b`, o sacar el tag a mano en GHL.

Los 4 números de envío ya están verificados y no deben cambiar:
`100 sand. delgadas + 50 cilindros = $400` · `100 gruesas = $350` · `300 cilindros = $750` · `50 mandiles = $250`.

Si en el paso 3 **las fichas se repiten en cada turno**, es que `GET /opportunities/search` no está
devolviendo los `customFields` (el spec dice que sí, pero conviene mirarlo): la comparación antes/después
se quedaría sin el "antes". El fix es agregar un `GET /opportunities/{id}` en `Resolver Contexto CRM` para
que las dos fotos salgan del mismo endpoint. La imagen del evento ya está blindada contra esto con una
segunda llave: solo se manda si el lead venía de `Lead Nuevo` o `Saludo Enviado`.

### Los custom fields de tipo checkbox

`had_information`, `had_image` y `had_quote` **ya no se escriben**, y es a propósito. Verifiqué el
OpenAPI de GHL: cuando `field_value` es un array (el caso de los checkbox), el schema
`customFieldsInputArraySchema` exige `id` — no acepta `key` — y sus items tienen que ser strings.
El v12 los mandaba como `{"key": "had_quote", "field_value": [true, "Tuvo cot."]}`: dos violaciones.
Como GHL valida el array completo, **una entrada inválida tira el PUT entero** — se habría perdido con
ella la escritura que sí importa (`evento_detectado`, `productos_mostrados`, la cotización), que viajaba
en el mismo request. Nunca se detectó porque en la demo el `opportunity_id` era falso y todo daba 404.

Las tools quedaron entonces escribiendo **solo campos de texto**, que es la variante donde el spec dice
textual *"Pass either `id` or `key` of custom field"*. Los dos checkbox que van en un PUT propio
(`imagen_input`, `payment_proof_detectado`) sí se escriben, por `id` resuelto en runtime y con items string;
si fallan, no arrastran nada.

Los tres `had_*` los usa la segmentación del reenganche (WF-02), que todavía no existe. Cuando haga falta,
se agregan en un nodo aparte por `id` — pero antes hay que mirar en la UI de GHL cómo quedaron definidos
esos campos (si son checkbox con opciones, el valor correcto es `["Tuvo cot."]`, no `[true, ...]`).

---

## 5. Lo que sigue abierto (necesita a Oscar)

1. **Fichas de sandalias, pantuflas, mandiles y vaso popote.** El bot de Kommo las mandaba, pero no por
   URL: disparaba un `bot_id` y el salesbot adjuntaba el binario. Las únicas copias públicas vivas son
   11 URLs de `i.ibb.co` (verificadas hoy: 200 OK) y cubren cilindros, kit anticruda, bolsa, tintas,
   correas 9/15mm y tapas termos — que es lo que quedó cargado. Las de Airtable (`v5.airtableusercontent.com`)
   ya están **muertas** (404, son links firmados que expiraron) y los IDs de Drive piden login.
   **Sandalias — el producto más pedido — no tiene ninguna copia recuperable fuera de Kommo.**
   Para cerrarlo: bajar los assets de Kommo (o que Oscar los pase), subirlos a la Media Library de GHL y
   pegar las URLs en el mapa `FICHAS` del nodo `Check Evento Just Set`. Está comentado y listo para llenar.
2. **Datos bancarios.** Siguen sin estar en ningún nodo, y el agente los ofrece proactivamente al cerrar.
   El original mandaba un PDF (`NUMEROS DE CUENTA.pdf`, salesbot `60820`) que hoy solo existe dentro de Kommo.
   Hace falta el PDF o los datos en texto.
3. **Debounce en 15s.** Es el valor de la demo. En producción con WhatsApp debería volver a 45s.
4. **Guardia de horario laboral** (WF-05: fuera de 9-18 responder el mensaje de horario). No está en el v16
   a propósito: si Oscar prueba a la noche el bot quedaría mudo. Es un IF de un nodo cuando se active.
5. **Seguimientos / reenganche** (las olas a 1h/3h/5h y 24h/48h/120h/168h). Fuera de alcance de este
   workflow **por diseño**: en la arquitectura objetivo viven en `WF-02 Reenganche Dual` dentro de GHL,
   que todavía no está construido (M4 pendiente). El v16 sí escribe los dos campos de los que depende
   (`last_outbound_at` y `last_inbound_at`, en ISO 8601), así que cuando WF-02 exista funciona sin tocar nada.
   Para la demo es mejor así: con las olas activas, Oscar recibiría un seguimiento a la hora de probar.
6. **Conexión de la WABA (M7).** Es lo que vuelve real toda la rama de producción — con la WABA conectada,
   `contact_id` y `opportunity_id` llegan de GHL y toda la cadena de resolución de identidad del v16 deja
   de hacer falta (queda cableada en paralelo, sin molestar). Dos bloqueos: el número `+52 331 594 8670`
   está **activo en Kommo** y no se puede migrar hasta el cutover — hay que decidir entre un número
   secundario para testing (Opción A de M7, la recomendada) o migrarlo el día del cutover con ~10 min de
   downtime; y las plantillas de Meta tardan **24-72 hs** en aprobarse, así que conviene mandarlas a
   aprobación antes que nada.
7. **Los 6 workflows de GHL (M4) sin construir:** WF-01 (enrutador + saludo fijo), WF-02 (reenganche),
   WF-03 (barrido), WF-04 (pago), WF-05 (horario), WF-06 (transiciones de etapa). Mientras no existan,
   todo eso lo tiene que hacer n8n — que es justamente lo que implementa este v16 para el canal Telegram.

---

## 6. Nota sobre la numeración

Le puse **v16** y no v15 porque el paneo de hoy menciona un "v15" con FAQ `[3b]`, fecha actual y cotización
100% determinística — pero **ese build no existe en el disco**: ninguno de los archivos `HPF Inbound Handler
(v7…v14)` tiene la sección `[3b]` ni un nodo de fecha. Si ese v15 existe en tu n8n, pasámelo y hago el merge;
si no, esos ítems siguen abiertos (la fecha ya la incorporé acá).

---

## 7. Rollback

Re-importar `03_workflows/hpf-inbound-handler-live-2026-07-24.json` (el snapshot del build que corre hoy)
y desactivar el v16. La memoria no se pisa: el v16 usa `session_key = tg_<chatid>` y el build vivo usa el
chat id pelado, así que son sesiones distintas — al volver atrás, el historial de hoy sigue donde estaba.

---

## 8. Si NO se deploya el v16

La alternativa es dejar el build vivo y taparle los tres agujeros de §0 a mano:

1. **Foto:** reemplazar el nodo `Send Photo (Telegram)` con
   `06_docs/snippets/clipboard-send-photo-telegram-fix-2026-07-24.json` (borrar el viejo antes de pegar,
   si no n8n lo renombra a `...1`). Con eso vuelve a andar la imagen de catálogo por evento.
2. **Debounce:** poner `amount: 15` en `Wait 15s (Debounce)`.
3. **Tools:** volverlas a stub `return 'ok, registrado';` hasta que entre la WABA — si no, cada tool call
   es un 404 cuyo texto termina en el contexto del LLM. Los nodos están en
   `06_docs/snippets/clipboard-mostrar-productos-toolcode-2026-07-24.json` y
   `clipboard-atencion-personalizada-toolcode-2026-07-24.json`.

Con esos tres cambios el build vivo queda coherente como demo (sin CRM, pero sin errores dando vueltas).
Lo que no se resuelve por esa vía es el CRM: para eso hace falta el v16 o la WABA.
