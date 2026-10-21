# HPF — Diagnóstico: `MOSTRAR_PRODUCTOS` no dispara / no llegan las imágenes en un chat sí y en otro no

**Fecha:** 2026-07-31
**Workflow analizado:** `HPF Inbound Handler` (id `IPO1c36NLzkXrBh9`, `active: true`, **67 nodos**) — export del 2026-07-31.
**Síntoma reportado:** en el chat de Telegram de la agencia el agente no activa `MOSTRAR_PRODUCTOS` ni manda fotos; en el chat de Camilo sí.

> Este export **no** es el `v14` documentado hasta ahora (64 nodos). Tiene 3 nodos nuevos (`Buscar Opportunity Real`, `Elegir Opportunity Activa`, `Mapear Custom Fields`), el `Sanitize + Split Output` reescrito con marcadores `[FOTO:producto]`, el `Send Photo (Telegram)` corregido (`file` en lugar de `fileId`) y el debounce en 15 s (antes 0). Actualizar el repo con este snapshot.

---

## 1. Lo primero: el flujo NO tiene ninguna bifurcación por chat

Se auditaron los 67 nodos y las 71 conexiones. **No existe ni un solo nodo que se comporte distinto según quién escribe.** Todo chat de Telegram recorre exactamente el mismo camino:

```
Telegram Trigger → Code in JavaScript → If (¿no es /b?) → Auth + Normalize
  → Buscar Opportunity Real → Elegir Opportunity Activa → Mapear Custom Fields
  → Generate Message ID → Debounce - Insert → Wait 15s → Debounce - Check Latest
  → Es El Ultimo Mensaje? → Combine Messages → ¿Media de Telegram? → Switch by Message Type
  → Text Passthrough → Vendedor (LLM Agent) → ¿Es test? → Sanitize + Split Output
  → Loop Message Parts → Es Origen Telegram? → ¿Parte con foto? → Send Photo / Send text
```

Lo único que varía entre un chat y otro es: **(a)** el `chat_id` (que es a la vez `contact_id`, `phone`, `sessionKey` de memoria y clave del `debounce_buffer`), **(b)** el historial en Postgres, y **(c)** qué escribió cada persona.

Conclusión: la diferencia no puede venir del ruteo. Viene del estado o del timing.

---

## 2. Descartado: el prompt / la decisión del LLM

Se replicó el nodo `Vendedor (LLM Agent)` fuera de n8n (mismo `systemMessage` con las expresiones resueltas como quedan en el path Telegram, mismo `gpt-4.1`, `temperature 0.3`, `max_tokens 1500`, mismas 5 tools con sus schemas):

| Escenario probado | `MOSTRAR_PRODUCTOS` |
|---|---|
| Chat nuevo → "que productos tienen?" | 6/6 |
| "quiero ver sandalias y cilindros" | 6/6 |
| Historial donde ya se mostró el catálogo | 6/6 |
| `Stage actual: Esperando Pago` | 3/3 |
| `Stage actual: En Producción` + cotización emitida | 3/3 |
| `Productos ya mostrados` ya cargado | 3/3 |
| `Stage: Cotizado` + cotización + productos mostrados | 3/3 |
| **Total** | **33/33** |

Y en el segundo tramo (cuando vuelve el resultado de la tool), el modelo emitió los marcadores `[FOTO:sandalias]` / `[FOTO:cilindros]` en **10/10** corridas — **tanto cuando la tool devolvió OK como cuando devolvió el `404 Opportunity not found` que es lo que realmente pasa hoy en Telegram**. El error de GHL no le cambia la conducta.

**El prompt no es el problema para llamar la tool** — y las ejecuciones reales lo confirman: en los dos chats `MOSTRAR_PRODUCTOS` se ejecutó y devolvió el 404 esperado. Lo que el prompt sí dejaba librado al azar era el marcador `[FOTO:...]` (ver §3).

---

## 3. CAUSA RAÍZ CONFIRMADA

Con las salidas reales del nodo `Sanitize + Split Output` de las dos ejecuciones quedó cerrado:

**Ejecución de la agencia** — la tool `MOSTRAR_PRODUCTOS` **sí se ejecutó** (devolvió el 404 esperado), el agente contestó *"Claro! Aquí tiene fotos de sandalias para boda"* … y las 3 partes salieron con `photo_url: ""`.

**Ejecución de Camilo** — mismo nodo, 3 partes, las 3 con su `photo_url`.

Ninguna de las líneas de la agencia es "canónica", así que **no es el bug del `isCanon`** (ese existe igual, ver §3b, pero no es el que le pegó). Lo que pasó es más simple y más grave:

> **El LLM no escribió el marcador `[FOTO:...]`.**
> Y como el envío de la imagen depende 100% de que el modelo escriba voluntariamente ese marcador de texto, si no lo escribe, no hay foto — aunque haya llamado la tool y aunque le esté diciendo al lead "aquí tiene las fotos".

Esa es la causa: **una entrega determinística (mandar una imagen) colgada de una decisión probabilística del modelo (escribir un token en el texto)**. Por eso sale en un chat y no en otro sin que nada del flujo cambie: es un dado que se tira en cada turno.

### 3b. Bug secundario (real, también corregido)

Aun cuando el modelo SÍ escribe el marcador, `Sanitize + Split Output` lo descarta si la línea cae en `isCanon()`.

El código captura el marcador y después decide la rama:

```js
let lineFoto = null;
line = line.replace(/\[FOTO:\s*([^\]]+)\]/gi, (_, prod) => { lineFoto = buscarFoto(prod); return ''; }).trim();

if (isCanon(line)) {
  buf.push(line); bufCanon = true;     // ← acá lineFoto se PIERDE, nunca se usa
} else {
  const part = { message_part: line };
  if (lineFoto) part.photo_url = lineFoto;   // ← solo acá sobrevive
  parts.push(part);
}
```

Y `isCanon()` devuelve `true` para, entre otras cosas:
- cualquier línea que arranque con numeración: `/^\s*\d+[.)]\s/` → `1. Sandalias…`, `2) Cilindros…`
- cualquier línea que contenga un precio unitario: `/x\s*\$/` → `Sandalias 50 pares x $25`

Ejecutado el código real del nodo contra salidas reales del modelo:

| Salida del modelo | Fotos enviadas |
|---|---|
| `- Sandalias… [FOTO:sandalias]` (lista con guiones) | **2 de 2** ✅ |
| `1. *Sandalias delgadas* $25/par [FOTO:sandalias]` (lista numerada) | **0 de 2** ❌ |
| `Sandalias delgadas 50 pares x $25 [FOTO:sandalias]` | **0 de 2** ❌ |

Misma tool call, mismos marcadores, mismo lead — **la foto llega o no llega según cómo el modelo haya formateado esa línea**. Y el formato cambia con la conversación (en cuanto entran precios o el modelo decide numerar, se cae). Esto explica exactamente "a Camilo sí, a mí no", sin que haya nada distinto en el ruteo.

---

## 4. La solución: la foto se deriva de la tool call, no del texto

`returnIntermediateSteps: true` en el nodo `Vendedor (LLM Agent)` hace que su output incluya `intermediateSteps`, con **las tool calls reales y sus argumentos**. Entonces `Sanitize + Split Output` ya no pregunta "¿el modelo escribió el marcador?" sino "**¿qué productos pidió mostrar la tool?**" — y adjunta esas URLs sí o sí.

Tres capas, en orden:

1. **Determinística** — `intermediateSteps` → tool `MOSTRAR_PRODUCTOS` → argumento `productos` → URLs (match por keyword, el más específico gana: `pantufla moño peluche` no dispara además la foto genérica de pantufla).
2. **Marcadores** `[FOTO:producto]` — siguen funcionando, sirven para emparejar cada foto con su línea de texto. Ahora una línea con marcador nunca entra al bloque canónico (fix de §3b).
3. **Colocación** — cada URL de la capa 1 que no quedó adjunta se pega a la parte cuyo texto menciona ese producto; si el texto no lo nombra, sale como mensaje propio con su título (`*Cilindros 500ml*`). Tope duro de 3 fotos por turno.

Degradación: si `returnIntermediateSteps` no estuviera disponible, `intermediateSteps` queda `undefined` y el código cae a la capa 2 (comportamiento actual + fix del `isCanon`). No rompe nada.

Y en el prompt, la regla se invierte: **llamar `MOSTRAR_PRODUCTOS` ES enviar las fotos**, con prohibición explícita de anunciar fotos sin llamarla.

### Verificación

**14/14** casos unitarios sobre el código real extraído del JSON final (caso la agencia, caso Camilo, lista numerada, línea con `x $`, tool sin texto, moño peluche, producto sin foto, 2 tool calls → tope 3, regresión cotización, regresión `[IMAGEN:XV]`, sin `intermediateSteps`, charla sin productos, `toolInput` string, otras tools).

**5/5** end-to-end con LLM real (gpt-4.1, temp 0.3, prompt nuevo, resultado 404 de la tool) → texto real → código real del nodo. Incluye un caso donde el modelo **no escribió el marcador** y las fotos salieron igual.

**12/12** llamadas a `MOSTRAR_PRODUCTOS` con el prompt nuevo cuando corresponde foto, con argumentos limpios (`"sandalias, pantuflas, cilindros"`), y **4/4 correctamente sin llamarla** para "bolsa personalizada" (producto sin foto).

---

## 4b. Sumideros silenciosos (no fueron la causa, pero conviene taparlos)

Hay **tres puntos** aguas arriba donde una ejecución muere sin error y sin respuesta:

| Nodo | Rama muerta | Cuándo te come el mensaje |
|---|---|---|
| `Es El Ultimo Mensaje?` | salida **false sin conectar** | Llegó otro mensaje tuyo durante los 15 s de `Wait 15s (Debounce)`. Por diseño gana el último — pero si escribís en ráfaga (típico testeando), varias ejecuciones mueren acá |
| `Switch by Message Type` | `fallbackOutput: extra` **sin conectar** | `message_type` no es `audio`/`image`/`text` |
| `Buscar Opportunity Real` | **sin `onError`** | Si GHL responde 4xx a la búsqueda, la ejecución muere ahí y nunca llega al agente (ejecución en rojo) |

Si alguna vez el bot directamente no contesta, mirá en qué nodo se corta la ejecución. Query para inspeccionar el buffer de un chat:

```sql
SELECT contact_id, jsonb_array_length(pending_messages) AS pendientes,
       last_message_id, updated_at, now() - updated_at AS antiguedad
FROM debounce_buffer WHERE contact_id = '6390727286';
```

---

## 5. Bug de fondo: el CRM sigue desconectado en Telegram

Independiente del síntoma, pero hay que decirlo porque toca a `MOSTRAR_PRODUCTOS`:

Las 4 tools de GHL (`MOSTRAR_PRODUCTOS`, `IDENTIFICAR_EVENTO`, `COTIZADOR`, `ATENCION_PERSONALIZADA`) apuntan a:

```
https://services.leadconnectorhq.com/opportunities/{{ $('Auth + Normalize').first().json.opportunity_id }}
```

y en el path Telegram ese valor es el sintético `tg_opp_<chatid>` que fabrica `Code in JavaScript`. **Todas devuelven 404 siempre.** Como una `toolHttpRequest` que falla le pasa el texto del error al LLM y deja el nodo en verde, esto no se ve: la tool "dispara" pero **no escribe nada en el CRM**.

Y la cadena nueva que se agregó para resolverlo (`Buscar Opportunity Real → Elegir Opportunity Activa → Mapear Custom Fields`) hoy es **código muerto**, por tres motivos acumulados:

1. `Elegir Opportunity Activa` hace `if (prev.is_telegram_test) return prev;` → en Telegram nunca resuelve nada.
2. `Combine Messages` hace `return { ...$('Auth + Normalize').first().json, message_text }` → **descarta** el `opportunity_id` y los `custom_fields` enriquecidos, también para leads reales de GHL.
3. Las tools y el bloque `[6]` del prompt leen `$('Auth + Normalize')` directo, así que ni siquiera consumirían el enriquecimiento.

Resolver esto de verdad es el trabajo del **v16** (`hpf-inbound-handler-v16-telegram-crm-real.json`), que crea contacto y oportunidad reales para Telegram vía `POST /contacts/upsert` con email determinístico. No lo resuelve un parche acá.

---

## 6. Fixes

### 6.1 — APLICADO en `hpf-inbound-handler-v17-fotos-deterministicas.json`

JSON listo para importar (preserva `id: IPO1c36NLzkXrBh9`, 67 nodos, conexiones y credenciales idénticas al vivo). **Solo 2 nodos modificados:**

**`Vendedor (LLM Agent)`**
- `options.returnIntermediateSteps: true` ← habilita la capa determinística
- `systemMessage` v1 → v2: Paso 3 reescrito (la tool es lo que manda las fotos; una línea por producto, sin numeración ni precios), regla "Fotos a pedido" reescrita, **REGLA CRÍTICA 15** nueva (prohibido decir "aquí tiene las fotos" sin llamar la tool en el mismo turno). Backup: `04_agents/agente-hpf-inbound-rebeca-system-prompt-v2.md`

**`Sanitize + Split Output`** — jsCode v3 (también suelto en `06_docs/snippets/sanitize-split-output-fix-foto-2026-07-31.js`):
- capa 1 determinística desde `intermediateSteps`
- una línea con `[FOTO:]` nunca entra al bloque canónico (fix §3b)
- match más específico primero (peluche / moño satín antes que pantufla genérica), 1 foto por grupo
- tope duro de 3 fotos por turno
- nunca fusiona una parte que tiene foto (antes el merge se comía fotos del final)
- guarda de caption: `sendPhoto` rechaza captions > 1024 chars con un `400` que **mata la ejecución**; si la parte con foto pasa de 1000 se corta y el resto sale como texto aparte

**Después de importar:** abrí el nodo `Vendedor (LLM Agent)` → Options → confirmá que **"Return Intermediate Steps" quedó en ON**. Sin eso el flujo sigue andando pero pierde la capa determinística.

### 6.2 — Tapar los sumideros silenciosos · PENDIENTE (no incluido en el JSON)

Que un mensaje se pierda sin dejar rastro es lo que hace que este bug sea invisible. Conectar:

- `Es El Ultimo Mensaje?` salida **false** → un nodo **NoOp** llamado `Descartado por debounce` (no manda nada al lead, pero la ejecución queda verde y se ve por qué murió).
- `Switch by Message Type` salida **extra** (fallback) → al mismo NoOp, o a `Text Passthrough` si preferís que igual conteste.
- `Buscar Opportunity Real` → **Settings › On Error › Continue (using regular output)**. Hoy un 4xx de GHL mata la conversación entera; con esto sigue de largo (en Telegram el resultado ni se usa).

### 6.3 — Pendientes que quedan abiertos (no son de esta sesión)

- **Debounce en ráfaga**: si escribís 3 mensajes en menos de 15 s, 2 ejecuciones mueren en `Es El Ultimo Mensaje?`. Es el diseño, pero mientras se testea conviene esperar >15 s entre mensajes para no confundir el síntoma.
- **`Debounce - Reset Buffer` corre después de toda la cadena del agente** (por posición: `¿Media de Telegram?` está más arriba-izquierda). Si el agente o el envío fallan, el reset nunca corre y el próximo mensaje dentro de los 50 s arrastra el texto viejo.
- **`pinData` en `Telegram Trigger`** con el `/b` de la agencia: si ejecutás "Test workflow" desde el editor, n8n corre con ese payload pinneado y lo único que hace es borrar la memoria. No afecta producción, pero explica tests que "no hacen nada". Conviene despinnearlo.
- **CRM real en Telegram** → v16 (§5).
- **Imagen de evento en Telegram**: `Es Origen Telegram? (Post)` tiene la **salida 0 (Telegram) vacía**, así que la cadena `Get Current Opportunity → Send Imagen Principal → Send Promo Evento` sólo corre para GHL. En Telegram la imagen del evento depende de que el modelo emita `[IMAGEN:evento]` — pero el prompt vigente ya no se lo pide (dice "el sistema la manda automáticamente", cosa que en Telegram no ocurre).

---

## 7. Orden sugerido

1. Importar `hpf-inbound-handler-v17-fotos-deterministicas.json` (sobrescribe in-place por `id`).
2. Confirmar que **Return Intermediate Steps** quedó ON en `Vendedor (LLM Agent)`.
3. Probar desde tu chat y desde el de Camilo: "mandame fotos de las sandalias" / "que productos manejan" / "quiero ver sandalias, pantuflas y cilindros". Las fotos tienen que salir en los dos.
4. Verificar en el output de `Sanitize + Split Output` que las partes traen `photo_url` **aunque el texto del modelo no tenga ningún `[FOTO:...]`** — esa es la prueba de que la capa determinística está funcionando.
5. Cuando puedas, aplicar §6.2 (sumideros silenciosos) para que un mensaje perdido deje rastro.
