# FAMILIAS — mapa de fallas del baseline

**Baseline corrido:** 2026-08-05 · **Build:** `hpf-inbound-handler-testbuild-nodebounce-2026-08-05.json`
`sha256 f92ceb1c…` · `versionId 4fc5b0c7-0ef0-4a7b-b5fd-1dc5e8033b45`

**Resultado:** 32 `PASA` · 2 `PARCIAL` · 1 `FALLA` · 0 `SIN-EVIDENCIA` sobre 35 casos.
**S1: 19 `PASA` / 1 `PARCIAL`.** El tripwire del 60 % no se disparó.
**93 artefactos** en `evidencia/`, uno por turno.

> Cero fallas huérfanas: las 3 tienen familia, causa raíz y ruta.

---

## F-1 · Variantes de producto que no se pidieron

**Caso:** `HPF-FIC-032` (S2, `PARCIAL`) · **Evidencia:** `evidencia/HPF-FIC-032/turno_2.*.json`

**Síntoma.** Al pedir *"quiero las pantuflas de moño de satín"* el bot entrega **8 partes**: la ficha de
la pantufla **cerrada** con su foto, su video y su catálogo, y recién después la de moño de satín. El
lead pidió una variante y recibió dos.

**Causa raíz.** `Sanitize + Split Output` `jsCode:365` y `jsCode:373`, dos reglas que no cubren este caso:

```js
// 365: si dice "pantufla" y NO dice variante -> empuja las 3
if (!tieneCantidad && /pantufla/i.test(textoPedido) && !/peluche|mo[ñn]o|mono|sat[íi]n/i.test(textoPedido)) {…}
// 373: si dice "pantufla" + "moño" y NO dice cuál -> empuja las 2 de moño y filtra la lisa
if (/pantufla/i.test(mensajeLead) && /mo[ñn]o|mono/i.test(mensajeLead) && !/peluche|sat[íi]n/i.test(mensajeLead)) {…}
```

*"pantuflas de moño de satín"* contiene `satín`, así que **ninguna de las dos reglas aplica**. La ficha
lisa entra igual porque su keyword es `"pantufla"`, que matchea el mensaje. No hay una tercera regla
para "pidió una variante concreta → mandá solo esa".

**Relación con el cliente.** Oscar lo reportó el 3/8 17:19 como *"a la de moño de satín le mandó el
video de la de peluche"*. El video que sobra no es el de peluche: es el de la **pantufla lisa**. Misma
familia —variantes de más— pero distinto síntoma. Arreglar el mapeo de videos, que es lo que su
descripción sugiere, **no** habría resuelto nada.

**Hermanos a revisar antes de tocar:** la misma ausencia de regla aplica a cualquier producto con
variantes que compartan keyword. Buscar en el `CATALOGO` las entradas cuyo `k:[…]` sea prefijo de otro:
`pantuflas` ⊂ `pantufla_satin`/`pantufla_peluche` es el caso conocido; hay que verificar `cilindros`
vs `cat_cilindros` y `vaso_popote` vs `cat_vasos`.

---

## F-2 · Correcciones del cliente que se pierden

**Caso:** `HPF-FIC-035` (S1, `PARCIAL`) · **Evidencia:** `evidencia/HPF-FIC-035/turno_2.*.json`

**Síntoma.** La ficha de la pantufla de peluche dice `blanca, negra, morada y rosa`. Oscar la corrigió
el **3/8 a las 17:30 (XV) y 17:38 (Boda)** a `blanca, negra, morada, rosa`. La corrección nunca se aplicó.

**Causa raíz.** No es de código: es de proceso. El texto vivo es el que Oscar mandó el **1/8**; su
corrección del 3/8 llegó por WhatsApp, entre otros 40 mensajes, y no quedó registrada en ningún lado.
No hay un lugar donde los textos canónicos del cliente vivan versionados.

**Fix:** aplicar la corrección en `jsCode` (2 minutos) — **primer ítem de la Fase 3, por decisión de la agencia.**

**Hermano estructural, sin caso todavía:** cualquier otra corrección que Oscar haya mandado por chat
después del 1/8 corre el mismo riesgo. Comparé las 8 fichas contra sus mensajes y esta es la única
diferencia de contenido, pero eso cubre solo lo que mandó en jul/ago.

---

## F-3 · Entradas que dejan al lead sin ninguna respuesta

**Caso:** `HPF-TOP-018b` (S2, `FALLA`) · **Evidencia:** `evidencia/HPF-TOP-018b/turno_1.*.json`

**Síntoma.** Con `message_type` desconocido (un sticker), el `Sanitize` emite **0 partes**, no corre
ningún emisor, y la ejecución queda en `success`. El lead no recibe nada y del lado nuestro no hay
señal de que pasó algo.

**Causa raíz.** `Switch by Message Type` tiene `options.fallbackOutput: "extra"` pero **solo 3 salidas
conectadas**. `Auth + Normalize` normaliza a `text`/`image`/`audio` solo cuando el tipo está en su
lista conocida; un tipo desconocido pasa tal cual y cae al fallback, que no va a ningún lado.

**Fix:** cablear la salida `fallback` a un mensaje genérico. Decisión D-04, ya aprobada por la agencia.

**Hermanos — los otros 3 sumideros del build, mismo patrón:**

| Sumidero | Efecto | Estado |
|---|---|---|
| `Es El Ultimo Mensaje?[false]` | la ejecución muere sin error ni respuesta | conocido, es el diseño del debounce |
| `Evento Recien Identificado?[false]` | no manda imagen ni promo | correcto: es el camino normal |
| `Es Origen Telegram? (Post)[true]` | en Telegram no corre la cadena de imagen/promo | verificado en `HPF-TOP-021` |

Solo el del `Switch` deja al lead sin nada. Los otros tres son intencionales o inocuos.

---

## Hallazgos sin caso asignado

Cosas que aparecieron mirando la evidencia y que no eran lo que el caso medía.

### H-1 · La imagen del evento y la promo salen por SMS, no por WhatsApp

En la rama GHL, `Send Message via GHL` manda `"type": "WhatsApp"`, pero **`Send Imagen Principal` y
`Send Promo Evento` mandan `"type": "SMS"`**. Verificado en el `jsonBody` de los tres nodos del build
congelado, y las dos llamadas devolvieron `messageId`, así que GHL las aceptó.

En una conversación de WhatsApp, eso puede significar que el lead recibe el menú y la promo por un
canal distinto —o que se cobra un SMS— justo en el turno donde se identifica el evento, que es el más
importante del embudo.

**No lo toco en Fase 2.** Va a la entrega y necesita decisión: es la rama a la que se migra el número.

### H-2 · En GHL el acuse no prueba entrega

GHL devuelve `{conversationId, messageId, traceId}` y **no el texto**. El acuse prueba que GHL
*aceptó* el mensaje, no que el lead lo recibió ni qué decía. El contenido se verifica leyendo la
entrada del emisor (`Check Evento Just Set.descripcion` / `.promoText`), que es lo que efectivamente
se envía.

**Consecuencia para la entrega:** en Telegram se puede afirmar *"entregado"*; en GHL, solo
*"aceptado por GHL"*. Son dos niveles distintos y no hay que mezclarlos en el reporte.

---

## Anexo · Los 4 falsos rojos del primer baseline

La primera pasada dio 7 no-verdes. **4 eran defectos de mis asserts, no del bot.** Se corrigieron y se
re-corrieron; los 4 pasan. Queda registrado porque un falso rojo manda a arreglar lo que no está roto,
y porque el patrón se repite.

| Caso | Qué asumí mal | Cómo se corrigió |
|---|---|---|
| `HPF-COT-013` | La entrada decía *"50 piezas, cp 61800"* sin el grosor de suela → el agente preguntaba, que es **la conducta correcta según Oscar (31/7)**. Mi assert la leía como falla | Se corrigió **la entrada**, no el esperado |
| `HPF-NRP-022`, `HPF-FIC-031` | Asumí que el catálogo de cilindros viaja como PDF. Viaja como **imagen** | Assert cambiado a buscar el texto del catálogo |
| `HPF-CAN-025` | Contaba los emisores post-loop (imagen + promo) contra las partes del `Sanitize` → *"entregadas 4/2"*; y el menú viaja como caption de esa cadena, que no inspeccionaba | Se separaron `EMISORES_LOOP` de `EMISORES_POST` y se agregó la lectura de `Check Evento Just Set` |

El de GHL era el más caro: habría reportado la única rama que importa para el cutover como rota,
estando bien.


---

## Gate de mutación G2-bis — resultado

Cinco defectos inyectados a propósito en el workflow vivo. Las cinco reversiones se hicieron pegando
el build congelado conocido-bueno (nunca un inverso calculado) y se verificaron por re-export.

| # | Defecto | Veredicto | Detalle |
|---|---|---|---|
| 1 | Borrar la ficha de sandalias del `CATALOGO` | ✅ **detectada** | `HPF-FIC-007` · `tiene:FICHA_sandalias` FALLA con diff en el byte 0 |
| 2 | `$25` → `$24` en el prompt | ✅ **detectada, tras cerrar el hueco** | Al principio no rompía nada. `HPF-COT-013` ahora afirma que la cotización dice `$25` y **no** dice `$24` |
| 3 | Apagar `returnIntermediateSteps` | ✅ **detectada** | `HPF-FIC-008` · 4 asserts en rojo: 2 partes en vez de 4, sin foto, sin PDF, sin video |
| 4 | Borrar `ev:["BODA"]` del gate de mandiles | 🔵 **redundancia, no hueco** | El agente igual se negó: *"los mandiles están disponibles solo para bodas"*, y ni invocó la tool. El prompt bloquea antes que el gate del `Sanitize` |
| 5 | Sacar el header `⏳(7 DIAS DE PROMO)⏳` | ✅ **detectada, tras cerrar el hueco** | Al principio no rompía nada. `HPF-COT-013` ahora lo afirma byte-exacto |

**4 de 5 detectadas · 1 redundancia documentada · 0 ejes ciegos.**

### Lo que el gate encontró sobre el propio corpus

**Dos huecos reales.** Ningún caso afirmaba el precio que cotiza el agente ni el header de la promo.
Los cerré agregando a `HPF-COT-013` y `HPF-COT-015`: que aparezca `⏳(7 DIAS DE PROMO)⏳`, que aparezca
`$25`, y que **no** aparezca `$24`. El positivo solo no alcanzaba: si el prompt dijera `$24` y el
agente cotizara `$24`, el `$25` de la ficha seguiría apareciendo y el assert pasaría igual.

**Un error de criterio mío.** La primera corrida reportó **0/5**. El script exigía estado `FALLA` para
aprobar, pero un caso con varios asserts donde solo algunos caen queda en `PARCIAL` — que es
exactamente cómo se ve una detección limpia. M1 y M3 sí habían detectado. Escribí "aprueba solo con
FALLA" pensando en excluir `SIN-EVIDENCIA` y de paso excluí `PARCIAL`. Criterio corregido: aprueba con
`FALLA` o `PARCIAL` mientras haya un assert en rojo con diff de bytes; `SIN-EVIDENCIA` nunca aprueba,
porque ahí se rompió la instrumentación y no se detectó nada.

**Una trampa de artefactos.** Los 5 casos que tocó el gate quedaron con su último artefacto generado
sobre un build roto a propósito. Los transcripts de entrega se habían renderizado antes, así que están
limpios — pero re-renderizar sin re-correr habría mandado la conversación de un bot mutilado como si
fuera la buena. Re-corridos sobre el build limpio: 6/6 `PASA`.

**Y un aviso para el ensayo en seco.** Antes de escribir nada, las 5 mutaciones se aplicaron en local
validando el JS con `node --check`. La mutación 1 **rompía la sintaxis**: el corte del bloque tomaba
como final la línea del `pdf:{…},`, que también termina en `},`. Escrito al vivo, el `Sanitize` quedaba
inválido y se caían **todas** las conversaciones, no solo las de sandalias. El peligro de este gate no
es la mutación que rompe de menos: es la que rompe de más.
