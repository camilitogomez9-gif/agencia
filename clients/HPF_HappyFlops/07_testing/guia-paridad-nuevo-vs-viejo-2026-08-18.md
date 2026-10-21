# Test de paridad — agente nuevo vs. agente original

El **nuevo** (n8n + GoHighLevel) se prueba por **Telegram**. El **viejo** (Kommo) por
**WhatsApp**. La misma secuencia en los dos, y se pegan las dos respuestas.

Enviá el texto —está en `código` para copiarlo de un toque— y pegá **todo** lo que conteste
el bot, incluidas las imágenes que manda (con poner "[llega la foto del catálogo]" alcanza).
Si manda varios mensajes, pegalos todos.

**No hace falta que juzgues si está bien o mal.** Pegá lo que llega y listo; la comparación
la hago yo después. Donde sí te pido que mires algo puntual, está escrito abajo del caso.

---

## Antes de empezar

**1 · Mirá en qué etapa está tu lead en los dos sistemas.** Si quedó en `En Espera`,
`Pago Confirmado`, `Ganado` o `Ventas Perdidas`, **el bot no te va a contestar** y no vas a
ver ningún error. En GHL movelo a `Lead Nuevo`; en Kommo, a `ETAPA 1`.

**2 · Reset entre caso y caso.** Cada bloque numerado arranca conversación nueva. Si no
reseteás, el bot ya sabe el evento y la mitad de los casos no prueba nada.

- **Nuevo (Telegram):** mandá `/reset`. Tiene que ir solo — `/reset por favor` no matchea.
  Te contesta `🧹 Memoria y buffer limpios.`
- **Viejo (WhatsApp):** no tiene comando. Corré esto contra la Postgres:

```sql
DELETE FROM n8n_chat_histories WHERE session_id = '+<tu-teléfono>2131';
```

El `session_id` es tu teléfono **con el `+`** y pegado a `2131`, sin guion bajo. Ejemplo:
`+5491122334455` → `'+54911223344552131'`.

**3 · Al terminar la jornada**, mandá un `/reset` final en Telegram. Borra la campaña de
seguimiento pendiente y evita que te lleguen mensajes de reenganche una hora después.

---

## ⚠️ Dos cosas que te van a pasar y no son fallas

**El viejo te va a escribir solo.** Cada saludo deja una ejecución dormida que despierta a
los ~60 minutos, te manda un WhatsApp de reenganche **y lo escribe en la memoria**. Si en
medio de un caso aparece un mensaje que no pediste, es eso. No se puede evitar; anotalo y
seguí.

**Si el bot nuevo deja de contestar de golpe**, casi seguro tu oportunidad quedó en
`En Espera` — pasa con cualquier caso del bloque H. Se destraba moviéndola a `Lead Nuevo`
en GHL. `/reset` **no** lo arregla.

---

## Diferencias esperadas — leé esto antes de empezar

Casi todos los turnos van a diferir en el formato. **Nada de esto es una falla**, no hace
falta que lo anotes:

| Vas a ver | Por qué |
|---|---|
| El **viejo llega sin `¿` ni `¡`** y casi sin emojis | Tiene un filtro de caracteres que los borra. Sobreviven sólo `✨ ⏳ ✏ ☺` |
| En **Telegram ves los asteriscos** `*así*` en vez de negrita | Los nodos de Telegram no activan Markdown a propósito: un asterisco suelto del modelo tira la ejecución |
| La **cotización llega en 1 mensaje en el nuevo y en ~3 en el viejo** | El nuevo nunca parte una cotización; el viejo la parte con un modelo |
| El nuevo contesta **al instante**, el viejo **50 s después** | El carril de prueba de Telegram no espera; producción sí |
| El nuevo usa **más emojis y negritas** | Se lo pidió Oscar (cambio de agosto) |
| Contestan **distinto a "¿de dónde son?"** | En el nuevo la dirección está separada de la respuesta de "¿es confiable?" |
| **Mandiles**: el nuevo deja elegir modelo, el viejo no | Cambio del 17/8, confirmado por Oscar |
| **Pantufla de peluche**: el nuevo manda una sola imagen | Cambio pedido por Oscar |
| El **texto de los datos de pago es distinto** | El viejo manda un texto fijo; el nuevo lo escribe el agente |
| El viejo manda **más avisos al grupo** del equipo | Puede recibir más tipos de archivo |

**Lo que sí quiero que me marques** (poné `⚠️` al lado y seguí): que falte un producto, que
un precio no coincida, que no pregunte algo que debería preguntar, que cotice por debajo del
mínimo, que mande fotos del evento equivocado, o que directamente no conteste.

---

# Bloque A · El camino completo, un evento cada uno

## A1 · Boda de punta a punta

**Escribí:** `hola` → `es para una boda` → `quiero sandalias gruesas` → `60 al CP 44100`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

---

## A2 · XV de punta a punta

**Escribí:** `hola` → `es para los 15 de mi hija` → `me interesan los cilindros` → `100 al CP 44100`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

---

## A3 · Otros de punta a punta

**Escribí:** `hola` → `es para un bautizo` → `qué productos tienen?` → `quiero 50 pantuflas normales al CP 44100`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** que las fotos sean de "Otros" y no de boda o XV.

---

# Bloque B · Transiciones — cambiar de tema a mitad de conversación

Es el bloque más importante: acá es donde el agente tiene que soltar un contexto sin perder
el anterior.

## B1 · Pido un producto y después otro

**Escribí:** `hola` → `es para una boda` → `quiero sandalias` → `ahora mostrame los cilindros`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

---

## B2 · Menciono uno que ya vi junto con uno nuevo

**Escribí:** `hola` → `es para una boda` → `quiero sandalias` → `me muestras las sandalias y los cilindros?`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** debería mandar **sólo cilindros**, porque las sandalias ya se las mostró.

---

## B3 · Ver producto y después cotizarlo

**Escribí:** `hola` → `es para una boda` → `me interesan los cilindros` → `quiero 100, CP 44100`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

---

## B4 · Cotizo y después pregunto el precio de lo que me ofreció

**Escribí:** `hola` → `es para una boda` → `quiero 60 sandalias gruesas al CP 44100` → `cuánto cuestan?`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

⚠️ **Este ya sabemos que falla ~2 de cada 5 veces en el nuevo** (contesta por las sandalias
en vez de por lo que acaba de ofrecer). Está medido y subir el modelo lo empeora. **No lo
reportes como bug nuevo** — si te falla, anotá "falló" y seguí.

---

## B5 · Cotizo y después pido otro producto

**Escribí:** `hola` → `es para una boda` → `quiero 60 sandalias gruesas al CP 44100` → `también quiero ver las pantuflas`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

---

## B6 · Agrego un producto a una cotización ya hecha

**Escribí:** `hola` → `es para una boda` → `quiero 60 sandalias gruesas al CP 44100` → `agregame 50 cilindros`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** que la cotización nueva incluya **las dos cosas**, y que el envío se recalcule.

---

## B7 · Pregunto por un producto antes de decir el evento

**Escribí (primer mensaje de la conversación, sin saludar):** `cuánto cuestan las sandalias?`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** tiene que preguntar el evento primero, no tirar el precio.

---

## B8 · Evento y producto en el mismo mensaje

**Escribí:** `hola` → `es para una boda, quiero 50 sandalias delgadas y 40 cilindros`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

---

## B9 · Pido productos y después pregunto algo del negocio

**Escribí:** `hola` → `es para una boda` → `quiero sandalias` → `hacen envíos a todo México?`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

---

## B10 · Cambio de evento a mitad de camino

**Escribí:** `hola` → `es para una boda` → `me interesan los cilindros` → `perdón, en realidad es para unos XV`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** si después de esto le pedís otro producto, ¿te manda fotos de XV o sigue en boda?

---

# Bloque C · Variantes — cuando hay que preguntar antes de cotizar

## C1 · "Pantuflas" a secas

**Escribí:** `hola` → `es para una boda` → `quiero pantuflas`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** tiene que preguntar si las quiere normales o con moño. No debería cotizar todavía.

---

## C2 · "Pantuflas de moño" — falta el material

**Escribí:** `hola` → `es para una boda` → `quiero las pantuflas de moño`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** ahora tiene que preguntar si de peluche o de satín.

---

## C3 · "Pantuflas de moño de peluche" — completo

**Escribí:** `hola` → `es para una boda` → `quiero las pantuflas de moño de peluche`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** en el nuevo llega **una sola imagen**, la de peluche, sin catálogo. Es un
cambio pedido por Oscar; el viejo probablemente mande más cosas.

---

## C4 · "Pantuflas de satín"

**Escribí:** `hola` → `es para una boda` → `quiero las pantuflas de satín, 50 al CP 44100`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** el precio tiene que ser $30 (el de peluche es $35).

---

## C5 · "Sandalias" sin decir el grosor

**Escribí:** `hola` → `es para una boda` → `quiero 60 sandalias al CP 44100`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** tiene que preguntar delgadas o gruesas **antes** de cotizar, aunque ya le
diste cantidad y código postal.

---

## C6 · Los dos grosores en el mismo pedido

**Escribí:** `hola` → `es para una boda` → `quiero 25 sandalias delgadas y 25 gruesas, CP 44100`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** el mínimo es 50 **de cada tipo**, así que 25 y 25 no debería alcanzar.

---

## C7 · "Costalitos" — palabra ambigua

**Escribí:** `hola` → `es para una boda` → `tienen costalitos?`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** "costalitos" puede ser el kit anticruda o las bolsitas. ¿Pregunta cuál, o
asume uno?

---

## C8 · Mandiles: elegir modelos

**Escribí:** `hola` → `es para una boda` → `qué mandiles tienen?` → `quiero 20, 10 del diseño 1 y 10 del 3, CP 44100`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** el nuevo tiene que aceptar la elección y cotizar. El viejo probablemente diga
que van surtidos — **eso es esperado**, es el cambio del 17/8.

---

# Bloque D · Mínimos y cotizaciones

## D1 · Muy por debajo del mínimo

**Escribí:** `hola` → `es para una boda` → `quiero 2 sandalias gruesas al CP 44100`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** tiene que decir que el mínimo es 50 y **no cotizar**.

---

## D2 · Justo abajo del mínimo de cilindros

**Escribí:** `hola` → `es para una boda` → `quiero 35 cilindros al CP 44100`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** el mínimo de cilindros es 40. Este es el caso que reportó Oscar en julio.

---

## D3 · Mandiles justo en el mínimo

**Escribí:** `hola` → `es para una boda` → `quiero 12 mandiles al CP 44100`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** 12 es el mínimo exacto, tiene que cotizar.

---

## D4 · Mandiles abajo del mínimo

**Escribí:** `hola` → `es para una boda` → `quiero 6 mandiles al CP 44100`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

---

## D5 · Cotización de tres productos juntos

**Escribí:** `hola` → `es para una boda` → `quiero 50 sandalias gruesas, 100 cilindros y 40 kits anticruda, CP 44100`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** que el total sume bien y que el envío contemple las cajas.

---

## D6 · Pedido grande — varias cajas

**Escribí:** `hola` → `es para una boda` → `quiero 400 sandalias gruesas al CP 44100`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** 400 no entran en una caja (el tope es 200). ¿Cobra dos envíos?

---

# Bloque E · Qué existe en cada evento

## E1 · Mandiles en XV

**Escribí:** `hola` → `es para unos XV` → `tienen mandiles?`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

⚠️ **Sabemos que el nuevo tiene un problema acá**: los mandiles son sólo para boda, y en XV
no hay ninguna ficha cargada, así que manda un mensaje pidiendo cantidad y código postal
**sin ninguna foto arriba**. Pegá lo que llegue igual — quiero ver qué hace el viejo.

---

## E2 · Pantuflas de moño en "Otros"

**Escribí:** `hola` → `es para una graduación` → `quiero pantuflas de moño de satín`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** las de moño sólo existen para boda y XV. ¿Qué ofrece para "Otros"?

---

## E3 · Vasos popote en "Otros"

**Escribí:** `hola` → `es para un evento de empresa` → `tienen vasos popote?`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

---

## E4 · "Todos los productos"

**Escribí:** `hola` → `es para una boda` → `quiero ver todos los productos que tienen`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** llegan muchas imágenes. Contá cuántas en cada uno y si aparecen los mismos
productos.

---

## E5 · "Todos menos uno"

**Escribí:** `hola` → `es para una boda` → `mostrame todos menos las pantuflas`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

---

# Bloque F · Preguntas del negocio

## F1 · Dónde están

**Escribí:** `hola` → `es para una boda` → `de dónde son? tienen tienda física?`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** el link de Google Maps tiene que llegar **pelado** (`https://goo.su/...`), no
entre corchetes ni paréntesis.

---

## F2 · Si es confiable

**Escribí (conversación nueva):** `hola` → `es para una boda` → `cómo sé que no es estafa?`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** esta respuesta tiene que ser **distinta** a la de F1 — acá va el Facebook, no
la dirección.

---

## F3 · Paquetería

**Escribí:** `hola` → `es para una boda` → `con qué paquetería mandan?`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

---

## F4 · Tallas

**Escribí:** `hola` → `es para una boda` → `qué tallas tienen las sandalias?`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

---

## F5 · Datos para pagar

**Escribí:** `hola` → `es para una boda` → `quiero 60 sandalias gruesas al CP 44100` → `sí, quiero avanzar, pasame los datos para pagar`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** tiene que llegar el **PDF con los números de cuenta**. Si ves el texto
`url1234.com123` escrito en el mensaje, avisame — eso es un bug.

---

## F6 · Cuánto pesa el pedido

**Escribí:** `hola` → `es para una boda` → `quiero 60 sandalias gruesas al CP 44100` → `cuántos kilos pesa el paquete?`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** tiene **prohibido** decir el peso. Si te lo dice, marcalo.

---

## F7 · Sandalias para hombre

**Escribí:** `hola` → `es para una boda` → `tienen sandalias para hombre?`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** sólo hay para mujer. No tiene que insinuar que existen de hombre.

---

## F8 · Despedida

**Escribí:** `hola` → `es para una boda` → `quiero sandalias` → `gracias, después te aviso`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** no debería seguir vendiendo. Un `👍` alcanza.

---

# Bloque G · Fotos, audios y archivos

Estos casos **antes no se podían probar en Telegram** — el canal no recibía adjuntos. Se
cableó el 18/8 para esta guía, así que además de comparar contra el viejo, sirven para
estrenar eso. Si algo falla raro acá, avisame con el detalle: puede ser del cableado nuevo
y no del agente.

## G1 · Foto de un producto, con texto

**Mandá** una foto de unas sandalias (cualquier foto de sandalias sirve) **con el texto**
`te mando una foto de lo que quiero`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

---

## G2 · La misma foto, sin texto

**Mandá** la misma foto, **sin escribir nada**.

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** tiene que reconocer la foto igual. Si contesta algo genérico como si no
hubiera recibido nada, marcalo.

---

## G3 · Nota de voz

**Mandá un audio** diciendo: *"hola, quiero sandalias para una boda, son sesenta"*

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

⚠️ **Es la primera vez que el audio corre de punta a punta en el nuevo.** Si falla, pegá lo
que salga (o "no contestó nada") — probablemente saque un bug propio, no de paridad.

---

## G4 · Un archivo que no corresponde

**Mandá** un `.zip` cualquiera (o un `.docx`).

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** el nuevo tiene que avisar que no puede procesarlo, sin colgarse.

---

## G5 · Tres fotos juntas

**Mandá 3 fotos seleccionadas juntas** (álbum), con el texto `me gustan estos modelos` en una.

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** el nuevo tiene que contestar **una sola vez**, no tres. Puede tardar ~15 s.

---

# Bloque H · Últimos — estos dejan el lead trabado

⚠️ **Estos casos van al final a propósito.** Cada uno deja tu lead en un estado donde el bot
deja de contestar. Después de cada uno, si querés seguir probando, hay que destrabarlo:

- **Nuevo:** mover la oportunidad a `Lead Nuevo` en GHL.
- **Viejo:** mover el lead a `ETAPA 1` en Kommo.

## H1 · Pido un diseño propio

**Escribí:** `hola` → `es para una boda` → `quiero sandalias con el logo de los novios que les mando yo`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** los dos deberían derivar a una persona. Fijate si además te llega un aviso al
grupo del equipo.

---

## H2 · Quiero un mandil con una frase mía

**Escribí:** `hola` → `es para una boda` → `me hacen 20 mandiles con el nombre de los novios?`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** los mandiles no se personalizan (eso no cambió). Tiene que decirlo y derivar.

---

## H3 · Lo necesito para la semana que viene

**Escribí:** `hola` → `es para una boda` → `quiero 60 sandalias gruesas al CP 44100` → `los necesito para el viernes que viene`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** la producción son 15 días. Menos que eso tiene que derivar a una persona.

---

## H4 · Mensajes en ráfaga

**Escribí tres mensajes seguidos, rápido, sin esperar respuesta:**
`quiero` → `sandalias gruesas` → `60 al CP 44100`

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** este es un caso donde **esperamos que difieran**. El viejo junta los tres
mensajes; el nuevo se queda sólo con el último. Quiero medir cuánto se nota.

---

## H5 · Comprobante de pago — el último de todos

**Mandá una imagen o PDF que parezca un comprobante de transferencia.** Usá uno falso o un
screenshot armado, **no uno real de un cliente**: el archivo queda público en internet.

**NUEVO (Telegram)**

_(pegar acá)_

**VIEJO (WhatsApp)**

_(pegar acá)_

**Qué mirar:** los dos tienen que agradecer el pago. Después de esto **el bot se calla en los
dos sistemas** — es correcto, el lead pasa a manos del equipo. Acá termina la corrida.

---

# Cuando termines

1. Mandá `/reset` en Telegram.
2. Borrá la memoria del viejo con el `DELETE` de arriba.
3. Movés los dos leads a la etapa inicial (`Lead Nuevo` / `ETAPA 1`).
4. Pasame el archivo completo.

No hace falta que completes los 49 casos de una. Si cortás a la mitad, avisame por dónde
quedaste — los bloques son independientes salvo el H, que va último.
