# HPF v18 — Paridad de voz con el Rebeca original (Kommo)

**Fecha:** 2026-07-31
**Workflow:** `HPF Inbound Handler` (id `IPO1c36NLzkXrBh9`) — entregado como `03_workflows/hpf-inbound-handler-v18-paridad-rebeca.json`
**Objetivo:** que al conversar sea imposible distinguir el agente nuevo del original. Todo lo que corre por detrás (cálculo de envío, CRM, tools, debounce, resolución de oportunidad, ruteo) queda intacto.

---

## 1. Cómo entregaba mensajes el original

Rastreando `03_workflows/happyflops-main-v3.json` (236 nodos), había **dos caminos de salida**, y el corte entre ellos es lo que produce toda la estética que se había perdido.

### Camino A — texto libre del LLM (filtrado)

`AI Agent Recolector` → `Message a model1` (splitter) → `Character_Cleaner` → `actualizar19/20/21` → salesbot genérico `60854`.

```js
// Character_Cleaner (nodo Code)
.replace(/[¿¡]/g, '')        // los signos de apertura NUNCA llegaban al lead
.replace(/\n{2,}/g, '\n')    // sin líneas en blanco

// actualizar19/20/21 (expresión dentro del HTTP Request)
.replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, '')  // emojis del plano astral
.replace(/[︎️]/g, '')                  // variation selectors
.replace(/‍/g, '')                          // ZWJ
```

Sobrevivían solo los símbolos del BMP: **✨ ⏳ ✏ ☺**. Por eso el original "no usaba signos de apertura" — los escribía y se los comían. Y por eso su texto libre casi no tenía emojis.

Lo que el LLM escribía vs. lo que el lead veía:

| El LLM escribía | Al lead le llegaba |
|---|---|
| `¡Qué buena elección!` | `Qué buena elección!` |
| `¡Son un hit en bodas! ✨` | `Son un hit en bodas! ✨` |
| `...para el envío. 😊` | `...para el envío. ` |
| `¿Le gustaría avanzar...?` | `Le gustaría avanzar...?` |

### Camino B — bloques pre-horneados (sin filtro)

n8n **detectaba una cadena en la salida del LLM y la reemplazaba** por un salesbot de Kommo con el contenido cargado a mano:

| Detector | Condición | Reemplazo |
|---|---|---|
| `If24` | output contiene `👼🏢` | saludo en 3 salesbots (`60952/54/56`), 2 s entre cada uno |
| `If26` / `If27` | la parte contiene `HAZ TU PEDIDO EN 7 SENCILLOS PASOS!` | salesbot `60958` |
| `File_Not_Required` | output contiene `.com123` | PDF de cuentas (`60820`) |
| `Formula` → `Search_Main_Image` | tool de evento | imagen del catálogo + caption, desde Airtable |
| `Search_Products` → `Loop Over Items` | tool de productos | una foto+ficha por fila, 2 s entre cada una |
| `actualizar23` | fin del loop de productos | el pedido de cantidad + CP, texto fijo |

**Esa es la arquitectura que replica el v18: detectar y sustituir.** Los bloques canónicos salen del LLM y los inyecta el código, verbatim, *después* del filtro — así es imposible que un filtro los toque por accidente.

---

## 2. Inventario verbatim

Fuentes: `00_migracion_ghl/00_inputs/{Boda,XV,Otros}-Grid view.csv` (columna `CURL` → campo `text`; `descripcion` cuando no hay CURL) e `Imagen Principal-Grid view.csv`, más los `systemMessage` de `happyflops-main-v3.json`.

### 2.1 Fichas de producto (15) — se inyectan como caption de la foto

8 principales, 5 accesorios y 2 catálogos de diseño. Detalles de bytes que se preservan tal cual:

- **Precios**: se usa la versión del CURL ($25/$30 sandalias, $30 pantuflas), que es la vigente. El campo `descripcion` de Airtable tiene precios viejos ($24/$29) — descartado.
- **NBSP (U+00A0)** en la ficha de tapas de termos: `*colores* que gustes`.
- `catalogo` **sin** tilde en el de cilindros y anticrudas, `catálogo` **con** tilde en el de mandiles. Está así en el original.
- `Aqui te muestro` sin tilde, en la ficha de tintas.
- **Variante por evento** con el token `{EV}`: `pantufla moño satín`, `pantufla moño peluche` y `vaso popote` cambian su primera línea (` para boda` / ` para XV años` / nada en Otros).
- **`mandiles` está gateado a Boda**: si el lead de XV lo pide, no sale.
- Los catálogos de cilindros y anticrudas conservan su foto (`i.ibb.co`). Los de mandiles, pantuflas y sandalias no tienen URL recuperable.
- Para **Otros**, las fichas de cilindros y kit anticruda vienen del catálogo de Boda: en el CSV de Otros esas filas existen pero con texto vacío (vivían dentro de Kommo). El contenido es agnóstico del evento ("Ideales para todo tipo de evento"), así que no hay pérdida.

Ficha más larga: 368 caracteres. Ninguna se acerca al límite de 1024 de un caption de Telegram.

### 2.2 Imagen del catálogo por evento

Caption verbatim. **XV lleva DOS espacios antes del 😊** — está así en producción, no es un error de transcripción.

```
TENEMOS ESTOS PRODUCTOS PARA TU EVENTO:

*Sandalias*
*Cilindros*
*Mandiles para Boda*      ← solo Boda
*Kit anti cruda*
*Pantuflas*

Dime cuales te interesan, así te mostramos toda su información 😊
```

Y la promo que la acompaña, con espacio final después del emoji y saltos simples:

```
Qué padre! 😊  
🎉 *¡SEMANA LOCA DE PROMOS! SOLO 7 DÍAS PARA LLEVARTE TUS RECUERDITOS PERSONALIZADOS CON DESCUENTAZO* 🎉
*(Pedidos solo para eventos 2026 por tema de tiempos)*
```

### 2.3 Saludo — 3 mensajes, 2 s entre cada uno

```
1: Hola! gracias por escribir a Happy Flops, me llamo Rebeca soy un asistente virtual, yo le estaré atendiendo con gusto ☺️🙋‍♀
2: Me podría decir de que es su evento?      ← con espacio final
3: 🤵👰 - Boda
   🎂🥳 - XV Años
   👼🏢 - Otros
```

`Me **podría** decir` — no "puede" (que es lo que decía el v2) ni "puedes". 10/10 transcripts dicen "podría". El emoji es `🙋` + ZWJ + `♀`, **sin** variation selector final.

### 2.4 Los 7 pasos — verbatim del salesbot 60958

Se preservan los errores del original: `COTIZACION` y `PRODUCCION` sin tilde, `15 DIAS` sin tilde, `Hace el *PAGO FINAL*` (debería ser "Haces"), el punto extra después de 🛠️, y **la línea 2 es un espacio solo, no está vacía**.

### 2.5 Pedido de datos — verbatim del nodo `actualizar23`

```
¿Le interesa sumarlos a la cotización?
Dígame:
- Cantidad
- Código postal

¡Gracias!
```

Conserva `¿` y `¡` y la línea en blanco: no pasaba por el filtro. El género (`sumarlos` / `sumarlas`) lo resuelve el código según los productos mostrados. **No se manda si todo lo mostrado fue accesorio** — ahí el original preguntaba la preferencia.

### 2.6 Los demás bloques fijos

Paquetería (con `pero,` con coma y `sea las más económica`, ambos errores del original que el v2 había "corregido"), referencias/anti-estafa, unitalla, kit anticruda, tarjetas, precios bajo presión, mandiles pre-hechos, cierre post-pago, bucle de despedida con 👍, upsell con `Mira, ya que pides [x]... ¡Son un hit en [evento]! ✨`.

> Excepción deliberada: el original decía `trjetas` (typo) en el mensaje de tarjetas. No se replica — un typo visible en un mensaje de pago es riesgo comercial, no color de voz.

---

## 3. Qué cambia en el flujo, y qué no

**El orden del turno de cotización** es `cotización → 7 pasos → upsell → cierre`. El prompt original se contradecía (ponía el upsell antes de los 7 pasos), pero los transcripts reales de producción confirman este orden. Gana la evidencia.

**"Foto antes que precio", sin el loop.** El original tenía prohibido cotizar un producto sin haber mandado antes su ficha ("penado de muerte" en el prompt del router). Se conserva para la primera aparición de cada producto. Lo que **no** se replica es el re-disparo: si el lead vuelve a mencionar un producto ya visto, el agente no re-manda la ficha ni re-pide cantidad y CP. Ese loop era el defecto #1 y #2 del buzón de Rebeca y afectaba a ~30% de los leads.

**Tampoco se replican** otros defectos documentados: pedir el correo y prometer un PDF ante una "cotización formal" (#6), escalar cuando el lead pide un catálogo (#8), y el `¡Qué diseño tan bonito!` ante una imagen del lead (#3, #5) — ahí se mantiene la regla del v2 de confirmar el producto por nombre.

---

## 4. Cambios por nodo

Cuatro nodos. Cero cambios de topología, conexiones o credenciales.

| Nodo | Campo | Cambio |
|---|---|---|
| `Sanitize + Split Output` | `jsCode` | reescritura completa (v5) — el 90% del trabajo |
| `Vendedor (LLM Agent)` | `options.systemMessage` | v2 → v3 |
| `Wait 1.5s Between Parts` | `amount` | `1.5` → `2` (cadencia del original) |
| `Check Evento Just Set` | `jsCode` | 2 strings a verbatim, para que el path GHL diga lo mismo que el de Telegram |

### El nuevo `Sanitize + Split Output`

```
E0  entradas          agent.output · intermediateSteps · evento · productos_mostrados
E1  intenciones       tool calls reales → fichas pedidas + evento
E2  marcadores        [FOTO:] / [IMAGEN:] legacy: se capturan y se sacan del texto
E3  evento            cascada: tool → Mapear Custom Fields → Auth+Normalize → marcador
                      → heurística sobre el mensaje del lead → OTROS
E4  normalizar        comillas, ** → *, ###, líneas con kg/peso, teléfonos ≠ 3315948670
E5  guillotina CTA    borra las preguntas que el original consideraba agresivas
E6  segmentar         bloques atómicos (cotización, 7 pasos, CTA, fijos) vs libres
E7  ══ FILTRO ══      SOLO al texto del LLM: astral + ¿¡ + colapso de \n\n
E8  detect-and-swap   los bloques canónicos se reemplazan por su versión verbatim
E9  splitter          ≤3 burbujas, corte en frontera de oración, sin terminar en punto
E10 ensamblado        texto + fichas + CTA + promo/imagen de evento
E11 guards            caption > 1024, partes vacías, topes
```

Todo lo inyectado entra **después** de E7, así que es imposible que un filtro lo toque.

**El splitter** replica las reglas de `Message a model1`: no corta a mitad de oración, ninguna parte libre termina en punto, la cotización y los 7 pasos van enteros en una sola burbuja, y no corta dentro de un monto (`$2,500.`), de una abreviatura (`C.P.`) ni de una URL.

**Dos de-duplicaciones nuevas**, porque el LLM tiende a escribir lo que el sistema ya inyecta: si se van a mandar fichas de productos, se le borran del texto las preguntas por cantidad/CP (el CTA canónico ya pregunta) y los anuncios de foto ("un momento y le paso las imágenes").

---

## 5. Verificación ejecutada

**35/35 unitarios** sobre el `jsCode` real extraído del JSON final:
fichas verbatim byte a byte (las 15, incluidos los NBSP) · variante por evento · mandiles gateado · dedup por grupo · accesorios que no compiten con principales · topes de fotos y burbujas · CTA canónico con género · saludo en 3 partes · 7 pasos en una sola burbuja con sus emojis · cotización atómica de punta a punta · el filtro borra astrales y `¿¡` pero no toca fichas ni promo · caption XV con sus dos espacios · anti-loop con y sin pedido explícito · degradación sin `intermediateSteps` · `toolInput` como string · otras tools no disparan fichas · `[IMAGEN:]` legacy · output vacío · ningún caption > 1024.

**13 conversaciones end-to-end** con gpt-4.1 real (prompt v3) → nodo v5 real, comparadas contra `conversation_samples.json`:
saludo en frío · evento → promo + catálogo · pedir 2 productos · turno de cotización completo · segunda cotización sin repetir 7 pasos ni upsell · desambiguación de pantuflas sin cotizar · accesorio sin pedir cantidad · producto ya mostrado (responde sin re-mandar) · post-pago · paquetería byte a byte · cotización formal sin pedir mail · presión sobre el precio · mínimo no alcanzado.

**Integridad del JSON:** `id == IPO1c36NLzkXrBh9`, 67 nodos, conexiones idénticas, credenciales idénticas, exactamente 4 nodos modificados.

---

## 6. Deploy

1. Importar `03_workflows/hpf-inbound-handler-v18-paridad-rebeca.json` (sobrescribe in-place por `id`).
   Alternativa más segura, dado que en este cliente un re-import ya rompió configs de tools: pegar los 4 nodos uno por uno desde `06_docs/snippets/clipboard-v18-nodos-tocados-2026-07-31.json`.
2. Confirmar que **Return Intermediate Steps** sigue en ON en `Vendedor (LLM Agent)` → Options. Sin eso el nodo pierde la capa determinística y cae a los marcadores.
3. Probar en Telegram: `hola` → `boda` → `quiero ver sandalias y cilindros` → `50 delgadas CP 44100`.
   Lo que tiene que pasar: saludo en 3 mensajes → promo + imagen del catálogo → una frase corta + 2 fotos con su ficha verbatim + el pedido de cantidad y CP → cotización en un solo mensaje + 7 pasos en un solo mensaje + upsell y cierre.
4. Chequear que el texto libre del agente llegue **sin** `¿ ¡` y sin emojis astrales, y que las fichas y los 7 pasos sí conserven los suyos. Ese contraste es la firma del original.

**Rollback:** re-importar `hpf-inbound-handler-v17-fotos-deterministicas.json`.

---

## 7. Lo que falta y los riesgos

**No recuperable del repo — hay que pedírselo a Oscar:**

- **Datos bancarios.** El original nunca los tuvo en texto: emitía el centinela `url1234.com123` y n8n lo cambiaba por el PDF `NUMEROS DE CUENTA.pdf`, que vive dentro de Kommo. El agente llega hasta "le paso los números de cuenta" y de ahí escala a `ATENCION_PERSONALIZADA`. **Es lo único que impide cerrar el Paso 5 solo.**
- **Videos de producto** (sandalias, pantuflas, cilindros, mandiles, kit anticruda) y **catálogos PDF** de mandiles, pantuflas y sandalias. Las filas existen en Airtable pero sin URL: los archivos vivían en los salesbots de Kommo. El original mandaba ficha + catálogo + video por producto; el v18 manda solo la ficha.
- **Las 5 frases de los mandiles** — el propio prompt original admite que no las tenía.

**Riesgos:**

- **`i.ibb.co` es hosting gratuito de terceros** y de él dependen 7 fichas (los 5 accesorios y los 2 catálogos). Verificadas 200 OK hoy. Conviene re-subirlas a la media library de GHL y cambiar las URLs en el catálogo del nodo: 15 minutos de ops y elimina la dependencia.
- **El turno se hace más largo.** Un turno de 3 productos son 5 mensajes a 2 s, sobre los 15 s de debounce. Es lo que hacía el original, pero conviene medirlo en producción.
- **`parse_mode` no está seteado** en los nodos de Telegram, así que los `*asteriscos*` se ven literales en el demo. En WhatsApp/GHL renderiza bien. No conviene activar Markdown: un asterisco desbalanceado del LLM devuelve 400 y mata la ejecución.
- **En Telegram el CRM sigue devolviendo 404**, así que el dedup por `productos_mostrados` y el guard de "imagen del catálogo una sola vez" son no-ops ahí. Se resuelve con el v16, no con este cambio.
- El catálogo de anticrudas tiene **dos URLs distintas** entre las fuentes (Boda vs XV/Otros). Se usó la de Boda; conviene mirarlas y confirmar que son la misma imagen.
