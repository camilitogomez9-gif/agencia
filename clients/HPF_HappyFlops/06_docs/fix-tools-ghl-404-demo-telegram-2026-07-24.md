# Fix — tools del agente pegando a GHL en la demo Telegram (HTTP 404)

> ⚠️ **Actualización 2026-07-24 21:30 — este fix NO se aplicó, y de hecho se fue en la dirección contraria.**
> Las 3 tools de CRM fueron **restauradas** a la versión de producción del v12 en el workflow vivo, así que
> el 404 que este doc diagnostica volvió: siguen pegando a `/opportunities/tg_opp_<chatid>`. El diagnóstico
> de causa raíz de abajo sigue siendo correcto y vigente; lo que cambió es la decisión. Las dos salidas
> reales están en `guia-v16-telegram-crm-real-2026-07-24.md`: deployar el v16 (resuelve ids reales de GHL)
> o volver las tools a stub hasta que entre la WABA.

**Fecha:** 2026-07-24 · **Workflow:** `HPF Inbound Handler` (v14 – demo telegram) · **Tipo:** EDIT sobre flujo vivo (no se pre-edita el JSON en producción)

---

## 1. Síntoma

En una prueba por Telegram, al pedirle imágenes de un producto, la tool `MOSTRAR_PRODUCTOS` devolvió:

```json
[
  { "response": "HTTP 404 There was an error: \"The resource you are requesting could not be found\"" }
]
```

---

## 2. Causa

El agente sigue invocando **tools que pegan a la API de GHL**, pero la demo por Telegram **no tiene contacto ni oportunidad en GHL** — los IDs son inventados.

Cadena de evidencia:

1. El adaptador del Telegram Trigger (nodo **`Code in JavaScript`**) fabrica la identidad del lead:
   ```js
   contact_id: chatId,                    // 6390727286  → es el chat de Telegram, no un contacto GHL
   opportunity_id: `tg_opp_${chatId}`,    // tg_opp_6390727286 → no existe en GHL
   ```
2. En las versiones previas del flujo (v10 / v11 / v12 en `~/Downloads`), `MOSTRAR_PRODUCTOS` era un **HTTP Request Tool**:
   ```
   PUT https://services.leadconnectorhq.com/opportunities/{{ $('Auth + Normalize').first().json.opportunity_id }}
   body: { customFields: [ { key: "productos_mostrados", field_value: "{productos}" }, ... ] }
   ```
   → con `opportunity_id = tg_opp_6390727286`, GHL responde **404 `The resource you are requesting could not be found`**.
3. El shape observado (`{ "response": "HTTP 404 There was an error: ..." }`) es exactamente cómo el **HTTP Request Tool** de n8n le devuelve un error al LLM. Un **Code Tool** no puede producirlo: devuelve el string de su `return`.
4. `onError: continueRegularOutput` **no evita esto**: el toolHttpRequest atrapa el error HTTP y lo entrega como *respuesta* de la tool. El agente recibe el texto del 404 como si fuera el resultado.

### Estado real en el JSON v14

| Tool | Tipo en v14 | ¿Pega a GHL? |
|------|-------------|--------------|
| `IDENTIFICAR_EVENTO` | `toolCode` (stub) | no |
| `MOSTRAR_PRODUCTOS` | `toolCode` (stub) | no |
| `COTIZADOR` | `toolCode` (stub) | no |
| `CALCULAR_ENVIO` | `toolCode` (JS puro) | no |
| **`ATENCION_PERSONALIZADA`** | **`toolHttpRequest`** → `POST /contacts/{{contact_id}}/tags` + credencial `httpHeaderAuth` | **SÍ — quedó sin migrar** |

O sea: en el export v14 tres tools ya fueron convertidas a stub, pero **`ATENCION_PERSONALIZADA` sigue pegando a GHL** y va a tirar el mismo 404 apenas el agente derive a humano (que es justo lo que el prompt manda hacer cuando el lead insiste con fotos/catálogo — reglas [5].4 y [5].10).

Y el 404 que se vio en la prueba salió de un `MOSTRAR_PRODUCTOS` que todavía era el HTTP Tool → hay que **verificar el nodo en el n8n vivo**, porque el archivo v14 y la instancia pueden estar desalineados (el tipo de un nodo no se puede cambiar desde la UI: hay que borrar y volver a crear).

---

## 3. Cambios a aplicar

> ⚠️ El **nombre del nodo es el nombre de la tool** que ve el LLM y está referenciado en el system prompt. Tiene que quedar idéntico: `ATENCION_PERSONALIZADA`, `MOSTRAR_PRODUCTOS`. Si pegás el nodo sin borrar el viejo, n8n lo renombra a `...1` y el prompt deja de matchear.

### Cambio 1 — `ATENCION_PERSONALIZADA` → Code Tool (obligatorio)

1. Abrir el workflow → clic en el nodo **`ATENCION_PERSONALIZADA`** → **Delete**.
2. Copiar el contenido de `06_docs/snippets/clipboard-atencion-personalizada-toolcode-2026-07-24.json` y pegarlo en el canvas (Cmd/Ctrl+V).
3. Conectar el conector inferior del nodo nuevo al input **Tool** del nodo **`Vendedor (LLM Agent)`**.
4. Guardar.

Código del nodo nuevo:
```js
// DEMO Telegram: no hay CRM que taggear. Se registra la derivacion y se sigue.
return 'ok, derivado a atencion humana';
```

### Cambio 2 — `MOSTRAR_PRODUCTOS` → verificar en el n8n vivo

1. Abrir el nodo **`MOSTRAR_PRODUCTOS`**.
2. Si muestra **URL / Method / `services.leadconnectorhq.com`** → es el HTTP Tool viejo: repetir el procedimiento del Cambio 1 con `06_docs/snippets/clipboard-mostrar-productos-toolcode-2026-07-24.json`.
3. Si ya muestra un editor de **JavaScript** con `return 'ok, registrado';` → está OK, no tocar.
4. Aprovechar y chequear igual `COTIZADOR` e `IDENTIFICAR_EVENTO` con el mismo criterio.

---

## 4. Verificación

Mandar por Telegram: *"me pasás fotos de las sandalias?"*

- La tool que se invoque debe devolver `[{ "response": "ok, registrado" }]` (o `"ok, derivado a atencion humana"`), **nunca** un `HTTP 404`.
- El agente responde describiendo el producto en texto (precio, mínimo, variantes) sin prometer fotos — comportamiento esperado del prompt para esta etapa.
- En la ejecución no debe aparecer ninguna llamada a `services.leadconnectorhq.com` desde el bloque de tools.

---

## 5. Cuando entre WABA → GHL (revertir)

Las 4 tools de CRM vuelven a ser HTTP Request Tools. Referencia: `~/Downloads/HPF Inbound Handler (v12).json`. Dos cosas a corregir al restaurarlas:

- **Bug de copy/paste en el body de `MOSTRAR_PRODUCTOS` (v12):** además de `productos_mostrados` setea `{ "key": "had_image", "field_value": [true, "Tuvo imagen"] }`. Eso pertenece a `Set imagen_input`, no a "mostré productos" — marca `had_image` en leads que nunca mandaron una imagen. Sacarlo.
- **El 404 crudo no debería llegarle al LLM.** Aun en producción, un ID vencido o un token mal seteado le devuelve al agente el texto del error como si fuera un resultado válido. Conviene envolver las escrituras a GHL en un sub-workflow tool que devuelva shape estándar (`{status, message_to_agent}`) en vez de pegar directo desde el toolHttpRequest.

---

## 6. Fuera de este fix (para decidir con Oscar)

Hoy la única foto que sale es la imagen de catálogo por evento, vía el marcador `[IMAGEN:BODA|XV|OTROS]` que expande `Sanitize + Split Output`, una sola vez por conversación. Si Oscar quiere **fotos por producto** cuando el lead las pide, la plomería ya está: `Sanitize + Split Output` emite `photo_url` por parte, `¿Parte con foto?` la detecta y `Send Photo (Telegram)` la manda. Sería agregar un marcador `[FOTO:PRODUCTO]` + un mapa de URLs por producto, y levantar la prohibición del prompt ("NO prometas mandar fotos"). No está incluido acá.
