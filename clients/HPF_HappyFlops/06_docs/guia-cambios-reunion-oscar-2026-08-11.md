# Cambios de la reunión con Oscar — 2026-08-11 (aplicados el 2026-08-12)

> ## ⏪ 2026-08-14 — los 7 deltas de PROMPT están REVERTIDOS en el vivo
>
> Pedido de la agencia. Se deshicieron **solo los cambios de system prompt** (items 1, 2, 3, 4, 10, 11, 12):
> los nodos `Starter`, `Products` y `Recolector` de W6 volvieron a la base congelada
> `04_agents/base-prod-2026-08-06/*.md`. Verificado byte a byte contra los systemMessage del
> snapshot `ghl-live-2026-08-12/W6.json` — los 5 son idénticos al estado previo a la reunión.
>
> **Los cambios de NODO siguen vivos y no se tocaron:** `Leer evento` / `Guardar evento`
> (persistencia del evento, el bug de XV recibiendo fichas de Boda), el marcador de pago
> `url1234.com123` en `Partir en burbujas`, y la canonicalización de pantufla peluche. W6 sigue
> en 41 nodos y activo.
>
> Los 7 deltas quedan intactos en `04_agents/deltas-oscar-2026-08-11/` — son re-aplicables con
> `hpf-aplicar-deltas-prompt.py --deploy`, y se revierten de nuevo con `--revert` (flag agregado
> ese mismo día; antes el script prometía el revert en el docstring pero no lo implementaba).
>
> **Lo que sigue abajo describe el estado del 12/8, no el actual.** Para los items de prompt,
> leelo como "esto se aplicó y después se dio marcha atrás".

Todo lo de acá está **aplicado y verificado en el devn8n vivo**, no es un plan. El punto de
rollback es `03_workflows/ghl-live-2026-08-12/` (export de los 11 workflows previo a tocar
nada, con sha256). El estado posterior está en `03_workflows/ghl-live-2026-08-12-post-cambios/`.

---

## Lo primero que hay que saber: los generadores quedaron atrás del vivo

Antes de tocar nada se midió el drift entre `scripts/generators/hpf-gen-w*.py` y devn8n:

| workflow | vivo | repo | drift |
|---|---:|---:|---|
| W1 Inbound | 39 | 25 | **14 nodos solo en vivo** (debounce, audio, etapas, seguimientos) |
| W6 Conversación | 39 | 33 | **9 solo en vivo** (`Leer Products`, `Leer canónicos`, `Canonicalizar productos`, `Recuperar cards`…) y perdió los 3 Parser |
| W7 Media · W8 Relay · W9 SQL · W10 Seguimientos | 31/15/4/22 | — | **no existen en el repo** |

**Consecuencia operativa:** correr un generador y deployar **borraría** esos nodos. Por eso
todos los cambios de esta sesión se aplicaron como **parches dirigidos de nodo sobre el JSON
vivo**, con el anchor verificado antes de escribir y relectura del vivo después. Herramienta:
`scripts/utilities/hpf-deploy-workflow.py`.

Los 5 systemMessage de W6 sí estaban **byte-exactos** con `04_agents/base-prod-2026-08-06/*.md`,
así que la base congelada sigue siendo fiel y los prompts se cambian por capa de deltas.

---

## Capa de deltas sobre los prompts congelados

`04_agents/base-prod-2026-08-06/*.md` es la copia congelada de los prompts de producción de
Kommo, verificada por sha256 contra `MANIFIESTO.json`. Es la base del protocolo de paridad de
la migración: sirve para poder demostrar que el bot nuevo dice lo mismo que el viejo. **No se
edita.**

Los cambios de Oscar son divergencias deliberadas, así que viven en
`04_agents/deltas-oscar-2026-08-11/`: un archivo por cambio, con el anchor literal, el
reemplazo, el item de la reunión que resuelve y la cita textual de Oscar que lo justifica.
El prompt que se deploya es `base + deltas`, recomputable, y cada delta se revierte solo.

```bash
python3 scripts/utilities/hpf-aplicar-deltas-prompt.py --list     # qué deltas hay
python3 scripts/utilities/hpf-aplicar-deltas-prompt.py --check     # ¿los anchors matchean?
python3 scripts/utilities/hpf-aplicar-deltas-prompt.py --diff recolector
python3 scripts/utilities/hpf-aplicar-deltas-prompt.py --deploy     # componer y subir a W6
```

Si un anchor deja de matchear (porque alguien editó el prompt vivo a mano), `--check` falla
ruidosamente y no deploya nada.

---

## El bug del evento (items 6, 7 y 8) — era más profundo de lo que parecía

Oscar reportó que en una conversación de XV recibía la infografía y el catálogo de cilindros
**de Boda**, mientras que el catálogo de pantuflas sí venía de XV.

Lo que se descartó con evidencia, en este orden:

1. **No es un archivo mal cargado.** Las 65 fichas tienen media viva (verificado con HEAD:
   HTTP 206 en las 8 críticas) y las de XV son distintas de las de Boda, incluso en formato
   (`abfc91fc….jpeg` vs `6a62bf3d….png`). Oscar confirmó visualmente que las de XV son de XV.
2. **No es el filtro de W3.** Llamada real a W3 con `{evento:"XV", productos:["cilindros"]}`
   devuelve exactamente las 3 fichas de XV. W3 filtra bien.
3. **Tampoco es que el evento se clasificara mal**, porque en el mismo turno unas fichas
   venían bien y otras mal.

**La causa:** el evento se le preguntaba al LLM en **cada turno**. `Leer Products` hacía
`evento: String(o.evento || '').trim()`, donde `o` es la salida del agente Products — y el
prompt de Products usa `"Boda"` en 12 de sus 13 ejemplos, así que el modelo derrapa a Boda a
mitad de conversación.

**Y no existía ninguna capa de memoria del evento.** Se midió:

- W1 no le pasa `evento` a W6 → `Normalizar entrada` recibe siempre `null`.
- `Partir en burbujas` no devolvía `evento` → `Decidir seguimiento` persistía
  `cerebro.evento`, que es `undefined` → la columna `hpf_seguimientos.evento` quedaba NULL
  para siempre, y el `COALESCE` la mantenía NULL.

O sea que el fix no era "leer el estado": era **construir el estado**.

### Lo que se hizo (`scripts/utilities/hpf-fix-evento-persistente.py`, idempotente)

1. Nodo `Leer evento` (Postgres) **en la cadena principal**:
   `Normalizar entrada → Leer evento → Router`. Crea `hpf_estado_sesion` si no existe y lee
   el evento de la sesión.
2. Nodo `Guardar evento` (Postgres) en rama paralela de `Leer Main Image` — el único lugar
   donde el evento se clasifica de verdad. Upsert.
3. `Leer Products` prefiere el evento del estado; el LLM queda como respaldo solo para el
   turno en que todavía no hay estado.
4. `Router.text` pasa de `$json.texto` a `$('Normalizar entrada').first().json.texto`, porque
   ahora tiene un Postgres por delante.

### ⚠️ La trampa que costó el primer intento

El primer intento puso `Leer evento` como **rama paralela** de `Normalizar entrada`, para no
cambiarle el input a nadie. Se aplicó bien, verificó bien estructuralmente… y **no funcionaba**.

Con `executionOrder: v1`, n8n recorre la rama del Router **hasta el final** antes de volver a
la otra rama. Así que cuando corría `Leer Products`, el nodo todavía no había ejecutado y
`isExecuted` daba `false`. Medido sobre 6 ejecuciones reales: `Leer evento` devolvía el valor
correcto (Boda / XV) y `evento_desde_estado` era `False` **en todas**.

**La lección:** un smoke que solo mira el resultado final habría dado verde por casualidad
(el LLM acertaba el evento en el caso feliz). Lo que lo destapó fue instrumentar el nodo
(`evento_desde_estado`, `evento_llm`) y leerlo de las ejecuciones vía API. Cualquier fix que
dependa de referencias entre ramas de n8n necesita esa traza, no alcanza el output.

Post-fix, con el nodo en la cadena principal: `desde_estado=True`.

---

## Item 4 — la pantufla de peluche ya no arrastra el catálogo de satín

Oscar: *"En esta de peluche, este no tiene catálogo. Le están mandando el catálogo igual que
acá el de satín […] son diferentes diseños. El video está bien, nada más el catálogo hay que
quitarlo."*

Medido contra W3:

| lo que se le pide a W3 | qué devuelve |
|---|---|
| `["pantuflas"]` | 5 cards, **incluido el catálogo de satín** |
| `["pantuflas mono peluche"]` | 1 card: solo la imagen de peluche ✅ |
| `["pantuflas mono satin"]` | 1 card: solo la de satín |
| `["pantuflas mono satín"]` (con tilde) | **0 cards** ⚠️ |
| `["pantuflas mono …"]` en evento `Otros` | **0 cards** ⚠️ (no existen cargadas) |

O sea que W3 ya distinguía bien: lo que faltaba era que le pidieran el nombre específico.
Se agregó vocabulario al nodo `Canonicalizar productos` (`pantuflas mono peluche` /
`pantuflas mono satin`) con las dos trampas medidas documentadas ahí mismo, y un delta en
`agente-products.md` para que Products conserve el material en vez de aplanar a `"pantuflas"`.

---

## Item 11 — el marcador de pago no lo procesaba nadie

Oscar: *"todavía ni me manda los números de cuenta y ya me está pidiendo el pago."*

El prompt del Recolector le dice al agente que emita el marcador `url1234.com123` para mandar
los datos bancarios. **Se midió: ese marcador aparece 4 veces en el prompt y 0 veces en código
de cualquiera de los 11 workflows vivos.** En Kommo lo interceptaba un salesbot; en GHL no hay
salesbots, así que el marcador le llegaba al cliente como texto literal y el PDF nunca salía.

Arreglar solo el orden en el prompt habría sido peor: le prohibiría pedir el comprobante sin
darle forma de mandar los datos, dejando el cierre de pago sin salida.

`scripts/utilities/hpf-fix-marcador-pago.py`:

1. `Leer evento` devuelve además `pdf_pago`, leído de `hpf_fichas` (no hardcodeado) — una
   query, dos datos.
2. `Partir en burbujas` detecta el marcador, **lo saca del texto** y adjunta el PDF a la
   burbuja. Si el PDF no está en la caché, saca el marcador igual: un mensaje sin adjunto es
   malo, `url1234.com123` en el chat es peor.
3. Deja trazas (`pago_marcador`, `pago_pdf`) para auditar en las ejecuciones.

Más el delta de prompt que fija el orden: **primero los datos, después el comprobante**, con
prohibición explícita de pedir la captura en un turno donde no salgan los números de cuenta.

---

## Item 10 — la dirección sí estaba en el prompt

Se había concluido que el texto de ubicación no existía en el repo. **Era un error de
búsqueda:** el link es `https://goo.su/OVoA` y los greps buscaban `maps`. La dirección está en
`agente-recolector.md` línea 38:

> JUAN R. ZAVALA #538 (CALLE 38), COL SAN JUAN BOSCO, GUADALAJARA, JALISCO, C.P. 44730
> (Fachada Fucsia, Portones Negros)

Lo que faltaba era **separar las dos preguntas**, que colapsaban a la misma respuesta corta:

- *"¿de dónde son?" / "¿tienen tienda física?"* → dirección completa + Google Maps como URL
  pelada (nunca `[texto](link)`, que WhatsApp no renderiza).
- *"¿cómo sé que es seguro?" / "¿es estafa?"* → la respuesta de confianza con el link de
  reviews, sin cambios.

⚠️ **Confirmar con Oscar** que la dirección y el link siguen vigentes: vienen del prompt de
Kommo y nadie los revalidó.

---

## Items 1 y 2 — negritas y emojis: tres superficies distintas, no una

Oscar pidió negritas y emojis en los mensajes generados, señalando que los únicos con emoji
eran los predeterminados. Al rastrearlo aparecieron **tres orígenes distintos** para lo que
el cliente ve, y solo uno es LLM:

| lo que ve el cliente | de dónde sale | qué se hizo |
|---|---|---|
| saludo inicial | `agente-starter.md` (fijo) | delta 01: `*Happy Flops*`, `*Rebeca*`, opciones en negrita |
| descripción de cada ficha de producto | **dato**: `ficha.descripcion` del custom object de GHL, cacheada en `hpf_fichas` | **no se tocó** — son 65 records en el CRM del cliente |
| "¿Le interesa sumarlos a la cotización?" | **hardcodeado** en el nodo `Cards a partes` | negritas + 😊 |
| cotización con precios | agente **Recolector** (LLM) | delta 02 |

**El `texto_dinamico` del agente Products se descarta**: `Cards a partes` solo lo usa en
`step_2` y lo toma de `Leer Main Image`. Por eso **no** se aplicaron las 5 ediciones que se
habían especificado para `agente-products.md` en ese punto — habrían agregado ~2 KB de prompt
para cero efecto visible.

---

## Emojis: lista cerrada, y el saludo ya no lo escribe el LLM (2026-08-12, tarde)

Oscar reportó, probando la primera versión de estos cambios, que **las opciones de evento
llegaban sin sus emojis**, con un bullet `•` que no existe en el original, y que el emoji del
saludo llegaba partido como `☺♀`. Su instrucción fue explícita: usar **solo** los emojis que
usaba el agente original, porque son los únicos que se muestran bien en el canal.

**Dos causas distintas, las dos mías.**

### 1. El LLM estaba retipeando el saludo

El prompt del Starter dice *"el mensaje no puede ser modificado bajo ninguna circumstancia"* y
el modelo lo modificaba igual: le cambiaba los guiones por `•`, se comía los emojis de las
opciones y rompía el `☺️🙋‍♀`. Es esperable — ese emoji es una secuencia compuesta
(`U+263A U+FE0F` + `U+1F64B U+200D U+2640`) y un modelo que la reescribe carácter por carácter
la parte.

**Fix:** el saludo ya no pasa por el LLM. `Partir en burbujas` tiene la constante
`SALUDO_CANONICO` y, si `step === 'step_1'`, **descarta** lo que escribió el agente y manda el
literal. El literal no se escribe a mano: sale de componer `base-prod + deltas`, así que hay una
sola fuente de verdad.

⚠️ Efecto colateral conocido: la memoria (`n8n_chat_histories`) guarda la versión del LLM, no la
canónica. No afecta al cliente ni a la detección de primer contacto (que cuenta turnos humanos),
pero está anotado por si alguien audita la memoria y ve una diferencia.

⚠️ Divergencia deliberada: se sacó la **comilla recta suelta** del final de la primera línea. El
mensaje abre con `“` y cierra con `”`; esa `"` no cierra nada, es un typo del original. Antes no
se veía porque el LLM reescribía el mensaje; ahora que se manda literal, llegaría al cliente. Si
se prefiere paridad byte-exacta con Kommo, se revierte solo esa parte del delta 01.

### 2. Yo había inventado 9 emojis

La primera versión del delta 02 traía una tabla de emojis por línea de cotización con
**💰 💳 🥤 🥿 👡 🧋 🎁 🍳 👛** — ninguno existe en los prompts originales. Se sacaron todos.

La paleta permitida no es una lista que yo decida: sale del inventario de los 16 prompts
congelados (20 secuencias) y, para el Recolector, de la **línea 125 de su propio prompt
original**, que ya decía:

> *"Usa párrafos cortos, emojis moderados (😊, ✨, 👟) y negritas para destacar Producto, Evento,
> Cotización, Anticipo, Total."*

O sea que **la negrita ya estaba pedida en el original** y no se cumplía — eso era el pedido real
de Oscar. Los emojis por línea eran agregado mío. La cotización volvió al formato original: solo
el `⏳` de la línea de promo, y lo que distingue cada línea es la negrita.

### Guardia automática

`scripts/testing/hpf-smoke-emojis-y-saludo.py` recorre una conversación completa y falla si
aparece cualquier emoji que no esté en el inventario. **El inventario no está hardcodeado**: se
extrae de `base-prod-2026-08-06/*.md` en cada corrida, así que si mañana se agrega un emoji al
original, el test lo acepta solo. También compara el saludo byte a byte contra el canónico.

```bash
python3 scripts/testing/hpf-smoke-emojis-y-saludo.py
```

Resultado: saludo byte-exacto ✅ · emojis usados en la conversación
`✏️ ✨ 🎉 🎨 📸 😊 🚀 🚚 🛠️` — todos del original ✅

---

## Resultado de la verificación (2026-08-12)

`hpf-smoke-reunion-oscar-2026-08-11.py` → **10/10 en verde**, contra el W6 vivo:

| item | qué se verificó | evidencia |
|---|---|---|
| 3 | saludo con negritas | `*Happy Flops*`, `*Rebeca*`, `*Boda*`, `*XV Años*`, `*Otros*` |
| 4 | peluche sin catálogo de satín | 1 ficha: `Pantuflas mono peluche` |
| 4b | el caso genérico no se rompió | 5 fichas, catálogo incluido |
| 6-8 | conversación de XV → fichas de XV | 3 adjuntos, 0 ajenos + `evento_desde_estado=True` |
| 10 | ubicación con dirección y mapa | dirección + `goo.su`, sin markdown roto |
| 10b | "¿es seguro?" mantiene su respuesta | no devuelve la dirección |
| 1-2 | cotización con negritas y emojis | 16 tramos en negrita, 14 emojis |
| 12 | "¿cuánto cuestan?" por lo ofrecido | ofrecido=cilindros → responde cilindros |
| 11 | manda el PDF, no el marcador | `marcador_crudo=False`, PDF adjunto |
| 11b | no pide comprobante sin datos | comprobante junto con los datos |

Regresión: `hpf-smoke-evento-persistente.py` ✅ · `hpf-smoke-pantufla-peluche.py` ✅ ·
gate preexistente `hpf-l5-w3.py` **8/8 corroborados** (el catálogo no se movió).

### Dos falsos positivos que dio el test antes de estar bien calibrado

Vale registrarlos porque los dos habrían llevado a "arreglar" algo que funcionaba:

1. **El oráculo marcaba como error de evento un archivo compartido.** 9 de los 65 assets son
   deliberadamente el mismo para los tres eventos (los 5 videos + correas, tintas, bolsa,
   tapas). El test marcaba "vino un archivo de Boda" sin chequear que además fuera de XV.
   Corregido: un archivo solo viola el evento si **ninguno** de sus dueños es el evento en curso.
2. **El test del item 12 asumía que la oferta era mandiles.** El agente había ofrecido
   *cilindros* y respondió por cilindros — o sea, bien. Corregido: el producto ofrecido se
   extrae del "¿le gustaría agregar X?" del turno anterior en vez de darse por sabido.

---

## Cómo verificar

```bash
# el bug del evento, con el caso adversarial de mandiles (producto exclusivo de Boda)
python3 scripts/testing/hpf-smoke-evento-persistente.py

# la pantufla de peluche, incluyendo que no se rompa el caso general
python3 scripts/testing/hpf-smoke-pantufla-peluche.py

# todos los items de la reunión, de punta a punta
python3 scripts/testing/hpf-smoke-reunion-oscar-2026-08-11.py
python3 scripts/testing/hpf-smoke-reunion-oscar-2026-08-11.py --solo 4,11-12
```

Los veredictos se sacan de lo que efectivamente le llega al cliente (texto + adjuntos),
cruzando cada `media_url` contra `catalogo-airtable.json`, no de lo que el agente dice que hizo.

⚠️ Un detalle del oráculo: 9 de los 65 archivos están **compartidos a propósito** entre los
tres eventos (los 5 videos + correas 9/15 mm, colores de tintas, bolsa shein, tapas termos).
Un test que marque "vino un archivo de Boda" sin chequear si además es de XV da falso positivo
— pasó en la primera corrida.

---

## Rollback

```bash
python3 scripts/utilities/hpf-deploy-workflow.py --restore clients/HPF_HappyFlops/03_workflows/ghl-live-2026-08-12/W6.json
```

---

## Lo que quedó abierto

| # | Qué falta | Por qué |
|---|---|---|
| 5 | **Catálogo nuevo de mandiles** | Oscar dijo en la llamada "ahorita te mando" el reemplazo de la imagen con mandiles rojos. Hasta que llegue, la ficha sigue mostrando producto discontinuado. Afecta `Mandiles` → `INFOGRAFIA final-04 (1).png` y `Catalogo de Mandiles` → `WhatsApp Image 2026-01-05 at 12.12.19.jpeg` |
| 9 | **Video de reseñas de confianza** | El salesbot `VIDEO RESEÑAS DE CONFIANZA` (Kommo id `62110`) **no está entre las 65 fichas migradas**. Hay que bajarlo de Kommo antes de dar de baja esa cuenta: no existe en ningún otro lado. Sin el asset no se puede cablear el paso previo a los 7 pasos |
| — | **`Otros` usa el catálogo de cilindros de XV** | El archivo `2f8fb77f….jpeg` está compartido por `XV/Cilindros catálogo`, `Otros/Cilindros Catálogo 1` y `Otros/Cilindros Catálogo 2`. Como Oscar confirmó que ese archivo es el de XV, Otros está mostrando material de XV — y tiene dos fichas apuntando al mismo archivo, así que una está mal cargada o es redundante. No se tocó porque no sabemos cuál es el archivo correcto. Oscar no lo detectó porque solo probó Boda y XV |
| — | **`Otros` sin pantuflas mono** | En evento `Otros`, pedir peluche o satín devuelve 0 cards. Mismo hueco de datos |
| — | **Dirección y link de Maps sin revalidar** | Vienen del prompt de Kommo; confirmar con Oscar |
| 12 | **El "¿cuánto cuestan?" es intermitente: 4 de 7 corridas** | Medido el 2026-08-12 repitiendo el mismo caso 7 veces contra el vivo. Cuando falla, hace exactamente lo que reportó Oscar: ofrece cilindros y contesta por sandalias. La regla del prompt está y se endureció; el modelo la cumple ~57% de las veces. **Esto confirma lo que Oscar y la agencia ya sospechaban en la llamada: es techo de modelo, no de prompt.** La palanca siguiente es subir el modelo del Recolector (hoy el `LM Recolector` de W6) y volver a medir con el mismo test. Para comparar: el item 11, que se resolvió con código determinístico en vez de con prompt, dio 4/4 |
