# Deploy · S3-b, S3-a, S3-c, R4b y la sugerencia anterior · 2026-08-21

Rollback de W6: `03_workflows/parches-2026-08-20/W6-snapshot-pre-sugerencia.json` (41 nodos).

---

## S3-b · el dump agrupado por producto · ✅

`W3` → `Consultar caché` → `ORDER BY`. Antes era alfabético y **partía las familias**: el
catálogo de anticrudas salía **primero** y su ficha **sexta**.

Ahora: `subcategoria` → **familia** → **rol** (ficha → catálogo → video) → `nombre`.
`media_tipo` (`imagen`|`video`|`pdf`) es la señal del rol; los PDF de este catálogo **son**
catálogos de diseños.

Simulado sobre las 65 fichas reales y después **verificado contra la caché viva**: orden
idéntico a la simulación en los 3 eventos.

> **Declarado:** el orden **entre** familias no se pudo verificar contra el viejo — la corrida
> de E4 del viejo se hizo sobre "Otros" y no sobre Boda, y la captura está cortada. Se usa la
> lista de prioridad del prompt. Es decisión de negocio, no un hecho medido.

**Efecto colateral útil:** el agrupamiento **hace visible el hueco**. En Boda la familia
sandalias queda con catálogo y video y **sin ficha** — es la que nunca se migró (bot `60766`).

## S3-a · la prueba social ya no sale antes de la cotización · ✅

**El concat `fichasFinales.concat(partes)` NO era la causa**; invertirlo —lo que proponía el
análisis— no arreglaba nada. La causa es el `splice(fichasFinales.length, …)`: en el turno de la
cotización **no hay fichas**, así que esa posición es **0** y el video quedaba primero.

Y había un segundo defecto: cotización y 7 pasos salían en **una sola burbuja gigante**, porque
`INDIVISIBLE` matchea el texto entero si aparece cualquiera de sus marcas.

Se corta sólo en ese borde, **al principio de la línea** (si no, `¡HAZ TU PEDIDO EN ` queda
colgando de la cotización), y el video se inserta ahí.

Probado en Node sobre 5 formas de turno **antes** de tocar producción. Verificado en vivo **2/2**:
`fichas → cotización → prueba social → 7 pasos`.

> El caso D del test unitario es el que importa: con marcador de pago **el PDF se cuelga de los
> 7 pasos y no del video**. Por eso el video se inserta *en* el borde y no con un push al final.

**No contradice a Oscar** (11/08, *"antes de enviar los pasos"*): los dos criterios apuntan al
mismo lugar.

## S3-c · decía "el enlace" y adjuntaba un PDF · ✅ (a la segunda)

Objetivo, del transcript: el viejo dice *"Aquí tiene toda la **info para el pago**"*; el nuevo
decía *"Aquí tienes **el enlace** para realizar el pago"* (línea 5653).

> ⚠️ **La v1 pasó el dry-run, entró a producción y falló 1 de 3 corridas.** El modelo escribió
> *"el enlace **con toda la información** para realizar el pago"* y la regex exigía que
> `el enlace` estuviera pegado a `para el pago`. **No se puede enumerar cómo lo va a redactar.**

La v2 ataca el **sustantivo**: dentro del bloque `teniaMarcador` lo adjuntado es siempre el PDF,
así que cualquier "enlace"/"link" ahí es falso por construcción. El test unitario sobre 8
redacciones encontró **dos roturas más** antes de deployar: `los enlaces` daba **"los los datos"**
y quedaba `datos … datos` redundante. **8/8 limpio.**

## R4b · sin fichas, que conteste el Recolector · ✅

En step_3 el CTA se emitía **incondicionalmente**, así que salía aunque no hubiera fichas que
sumar — el lead veía una pregunta sobre unas fichas que nunca recibió — y el fallback
`partes.length === 0` era **inalcanzable por construcción**.

Ahora `sin_fichas` corta el CTA y `¿Requiere cotizar?` tiene un `OR` que fuerza el paso por el
Recolector, que sí tiene el dato en el prompt.

**Orden deliberado de las dos escrituras** (un solo PUT): primero el `OR`, después el
`sin_fichas`. Al revés, una falla en el medio dejaría una ventana sin CTA **ni** Recolector:
silencio total.

Verificado **4/4**: sin fichas → 1 burbuja con respuesta, sin CTA · con fichas → CTA intacto.

> **Matiz honesto:** responde *"necesitaría la cantidad y el código postal"*, no el precio. El
> viejo decía *"cada vaso cuesta $35"*. R4b arregló lo **estructural**; el contenido lo decide el
> prompt.
>
> Y de paso: la lista de productos por evento del prompt **no incluye vasos en "Otros"**
> (Boda 7, XV 6, Otros 4). El viejo, al ofrecerlos en E3, se sale de su propia lista.

## 3.2 · la "sugerencia anterior" de Products · ✅ (a la segunda)

**No era heredado: era regresión de la migración.** El origen tenía un nodo Postgres dedicado —
`Switch1 [2] → GET_LAST_INTERACTION → AI Agent Products` — que leía el último mensaje del agente.
Ahí `{{ $json.message.content }}` **sí** resolvía. La migración se llevó el nodo y dejó la
referencia colgando, con el bloque entero muerto.

Restituido como `Leer sugerencia anterior` (W6: 41 → 42 nodos), con:
- **`alwaysOutputData: true`** — sin eso, 0 filas mata la rama. Es el bug que apareció hoy mismo
  en `¿Es Telegram?` de W2.
- **`onError: continueRegularOutput`** — un problema de base no puede tumbar el turno.
- **`Products.parameters.text` convertido a referencia absoluta en la MISMA escritura**: al
  insertar un nodo, `$json` deja de ser el ctx y `texto`/`fecha` se romperían. Es el bug de R2,
  que iría de arriba.

**Baseline de regresión antes y después:** la única diferencia estructural es el nodo nuevo
apareciendo en la lista de ejecutados. Ningún otro escenario cambió.

> ⚠️ **Y aun así hacía lo incorrecto.** El nodo pasó todas las verificaciones estructurales y,
> mirando el `runData` real, devolvía **el JSON del agente**:
> `{"evento":"Boda","texto_dinamico":"Qué padre!…"}`.
>
> En Kommo el filtro `NOT LIKE '%step_%'` alcanzaba; en W6 **los agentes escriben su salida
> estructurada en la memoria**, no el texto al cliente. Copiar la query del origen tal cual no
> bastaba. Se agregó `left(ltrim(content),1) <> '{'`, que deja sólo prosa — la del Recolector,
> que es la que de verdad le habla al lead. Verificado: devuelve prosa.

---

## Sobre `oferta_precio` T4 — no atribuir

Ese turno osciló **step_4 → step_3 → step_4 → step_3 → step_4** a lo largo del día, con cambios
que demostrablemente no tocan el ruteo. **Es variable.** No se le atribuye a ningún fix, en
ninguna dirección.

---

## R10 · el arrastre de productos de turnos anteriores · ✅

**Causa: SOBRA un término, no falta.** En B5 el orden observado era exactamente el `ORDER BY`
de W3 para `['pantuflas','sandalias']` — `Products` arrastra el producto del turno previo y W3
devuelve las fichas de los dos.

Fix en `Leer canónicos`, replicando el patrón que ese mismo nodo ya usa para el material de
pantufla: mirar el texto del lead.

> ⚠️ **La guarda es lo importante, no el filtro.** Sólo filtra si el mensaje **actual** nombra
> un producto. Con *"cuánto cuestan?"* o *"dale"* NO filtra, porque ahí el arrastre es
> **correcto**: el lead se refiere a lo último ofrecido. Es lo que sostienen B4 **y el bloque
> "Sugerencia anterior" de `Products` que se restituyó hoy mismo** — un guard mal calibrado
> anularía ese fix a media hora de haberlo hecho.

Y si el filtro dejaría la lista vacía se conserva la original: cubre *"todos menos cilindros"*,
donde el canonicalizador ya excluyó el producto y el texto igual lo nombra.

**13 casos en Node antes de tocar producción**, incluidos los 3 de exclusión. Verificado en vivo:

| caso | resultado |
|---|---|
| **B5** · pantuflas tras cotizar sandalias | 5 fichas, **todas pantuflas, 0 ajenas** — el PDF `Boda/Sandalias para boda personalizadas` ya no se cuela |
| **B4** · «cuánto cuestan?» | no filtra, el agente responde |
| **"todos los productos"** | 18 burbujas, dump completo sin recortar |

---

## R8 · re-medición tras restituir la sugerencia anterior

**El mecanismo quedó probado.** Corrida 2 de 5: en T3 el agente ofreció cilindros y en T4, ante
un *"cuánto cuestan?"* que no nombra producto, respondió **"Los cilindros tienen un costo de $10
cada uno"** — resolvió a lo **sugerido**, no a lo cotizado. Con la referencia muerta eso era
imposible.

**Lo que NO se afirma:** que R8 esté resuelto. Cross-sell **2/5** contra el 2/13 del test es
alentador pero **N=5 no alcanza**, y la comparación ni siquiera es pareja — la sonda fuerza
cotización en cada corrida y las ~13 del test estaban repartidas en escenarios variados.

**Para cerrarlo hace falta una muestra del tamaño del test original.** Queda abierto.
