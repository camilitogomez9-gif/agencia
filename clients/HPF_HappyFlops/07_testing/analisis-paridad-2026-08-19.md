# Informe de paridad — Happy Flops · agente nuevo (n8n + GHL) vs. original (Kommo)

**Corrida:** 50 casos × 2 agentes, 18-19/8/2026 (Camilo) · **Fuente:** `clients/HPF_HappyFlops/07_testing/paridad-resultados-2026-08-19.md`
**Verificación:** 3 pasadas adversariales sobre los hallazgos + corroboración contra el catálogo migrado (`00_migracion_ghl/06_registro/catalogo-airtable.json`), los prompts congelados pre-migración (`04_agents/base-prod-2026-08-06/`) y los workflows vivos.

---

## 1. El veredicto

**Todavía no.** El agente nuevo replica el camino comercial central sin fisuras (la aritmética de las 27 cotizaciones del test coincide peso por peso con el viejo, incluidos los cortes de caja y los envíos por CP), pero hay **6 regresiones S1** que pueden costar plata o trabar un lead, y las tres más caras son de **datos migrados o de nodo, no del LLM** — o sea, baratas de arreglar y verificables sin re-entrenar nada.

Lo importante: la causa raíz de la mitad de las regresiones no es la que se venía asumiendo. **La migración copió el campo equivocado de Airtable.** El bot viejo nunca envía el texto de las fichas (sus nodos `Envio Mensaje7/8` sólo hacen POST a `/salesbot/run` con `{bot_id, entity_id}`, el texto vive dentro del salesbot de Kommo); Airtable guarda dos copias por ficha, `descripcion` (obsoleta) y `CURL` (captura del envío real), y a GHL se migró `descripcion`. Eso explica los precios, la ficha de mandiles y varias diferencias sueltas de una sola vez.

**Gate con fecha de vencimiento:** varios fixes dependen de textos y assets que **sólo existen dentro de los salesbots de Kommo** y no están respaldados en ningún otro lado. Hay que bajarlos **antes** de dar de baja esa cuenta, y el `CURL` sólo cubre 40 de las 65 fichas.

---

## 2. Conteo por familia

No hay un "42/50" honesto. Así queda:

| Familia | Casos | Detalle |
|---|---|---|
| **IGUAL** | 12 | B1, B3, B7, B9, B10, D5, D6, F2, F3, F6, G2, H5 |
| **EQUIVALENTE** | 9 | A2, B4, B6, C5, C6, D1, F5, F8, G1* |
| **MEJORA-FIRMADA** | 3 | C3, C8, F1 |
| **DISTINTO (regresión real)** | **15** | A1, A3, B5, B8, C1, C2, C4, D2, E2, E3, E4, G3, G5, H2, H3 |
| **MUDO** | 0 | — |
| **HEREDADO (fallan los dos)** | 7 | B2, C7, E1, F4, F7, H1, H4 |
| **SIN EVIDENCIA** | 4 | D3, D4, E5, G4 |

\* G1 pasa a MEJORA tras la verificación (ver §5).

**Los 15 DISTINTO colapsan en 8 causas raíz.** No son 15 problemas: cinco casos son el mismo precio mal migrado, tres son la misma línea de texto faltante, cuatro son la misma frase enlatada.

---

## 3. Las regresiones reales

### 🔴 S1

#### R1 · Precios $1 por debajo en 5 fichas: el lead lee un número y paga otro
**Viejo:** `💡 Disponibles en suela delgada ($25) o suela gruesa ($30)` · `💰 Precio promo: $30 el par`
**Nuevo:** `($24)` / `($29)` · `💰 Precio promo: $29 el par` — y después cotiza `50 Pantuflas x $30 = $1,500` en el mismo turno (C4).
**Casos:** A3, B5, C1, C2, C4, E2 (5 con las dos columnas presentes).

**Causa verificada.** No es alucinación ni carga manual. Son exactamente **5 records** del catálogo migrado, y los listé del JSON:

- `Boda | Pantuflas boda` → $29
- `XV | Pantuflas XV` → $29
- `Otros | Pantuflas XV` → $29
- `XV | Comparativa sandalias suelas delgadas y gruesas` → $24/$29
- `Otros | Comparativa sandalias suelas delgadas y gruesas` → $24/$29

El canon está confirmado dos veces en el prompt congelado (`agente-recolector.md:163-168`: Delgadas $25 / Gruesas $30 / Pantuflas $30). Los cinco vienen del campo `descripcion` de Airtable, cuyo `CURL` gemelo dice el precio bueno.

**Corrección de alcance a lo que veníamos diciendo:** *sí* afecta a boda (`Boda|Pantuflas boda` dice $29). Lo que no existe en boda es la ficha comparativa de sandalias, por eso en A1 el nuevo nunca llegó a enunciar el unitario.

**Fix:** re-migrar los 5 desde `CURL`. **Pendiente antes de tocar:** en la variante de Boda el $29 podría estar **quemado en la imagen** (`INFOGRAFÍA final 2-11 (1).png`), distinta de la de XV (`Pantuflas XV-2.jpeg`); las transcripciones de Camilo se contradicen entre casos y son archivos distintos, así que las dos lecturas son compatibles. Hay que abrir los dos assets antes de decidir si además hay que reemplazar imágenes.

---

#### R2 · No cotiza aunque tenga todos los datos, y vuelve a pedir lo que el lead acaba de dar
**Viejo (B5, mismo input):** `· 60 Sandalias Gruesas x $30 = $1,800 · Envío: $300 · Total: $2,100`
**Nuevo:** `Para poder cotizarle las sandalias gruesas, necesitaría que me diga la cantidad y el código postal. 😊` — el mensaje era *"quiero 60 sandalias gruesas al CP 44100"*.
**Casos:** B5, B8, C6, D1, **D2**, H3. Dos cotizaciones perdidas de verdad (B5 y H3); las otras cuatro son ruido que no cambia el desenlace.

**Causa verificada.** La frase sale de una regla **incondicional** del prompt (línea 7: *"Pedir los datos de cotización cada vez que respondas información sobre productos que no se hayan cotizado anteriormente"*), idéntica en los dos agentes — así que la regla explica la frase pero no la diferencia. Lo que sí está descartado es que sea "no parsea": en B6 el nuevo **valida las 60 piezas contra el mínimo de 50 en la misma oración** en la que dice necesitar la cantidad. El dato está. Y también está descartada la hipótesis de "el turno emitió fichas y por eso no cotizó": en C4 el turno emitió 3 fichas + PDF + 2 videos y cotizó igual. **Es intermitente.**

**Ojo con esto:** el "no avisa el mínimo de cilindros" (hallazgo #3 de Camilo, el caso que reportó Oscar en julio) **es esta misma frase**, no un defecto aparte. Un solo fix cierra los seis casos.

---

#### R3 · La ficha de mandiles no se envía nunca: desaparecen precio, mínimo y "no se personalizan"
**Viejo (6 de 6 corridas):** `✨ Mandiles para boda / 🍾 Ideales para el novio y sus amigos / ℹ️ No se personalizan. / 💰 Precio promo: $12 c/u / 📦 Pedido mínimo de 12 piezas.` + catálogo + video.
**Nuevo (6 de 6):** sólo la grilla numerada + `Te comparto el *catálogo de diseños* que tenemos para *Mandiles*`.
**Casos:** C8, D3, D4, E4, E5, **H2**.

**Causa verificada.** El record existe, completo y activo: lo leí en el catálogo migrado (`Boda | Mandiles`, con el texto entero incluido el `ℹ️ No se personalizan.`). Y una llamada al webhook de W3 en producción devuelve **3 cards** para `{Boda, mandiles}` (catálogo + ficha + video); el bot despachó 1. El filtro está en el **término** que `Products`/`Canonicalizar productos` le pide a W3, aguas arriba: la query hace `nombre LIKE '%término%'` y un término con "catalogo" matchea sólo la card del catálogo.

**Esto reencuadra el hallazgo #6 de Camilo.** No es que el LLM incumpla intermitentemente: es que el aviso determinístico nunca sale. En C8 apareció porque el LLM lo improvisó **dentro** del bloque de cotización; en H2 no hubo cotización y no quedó nada. Reforzar el prompt otra vez no arregla nada.

**Fix:** de nodo/selección de fichas. Se cierra leyendo el `runData` de `Leer canónicos` en una ejecución. Probablemente el mismo eslabón explica el reenvío de sandalias de R10 (ahí sobra un término en vez de faltar).

---

#### R4 · Vasos Popote: fuera de la lista de boda, y sin red cuando no hay ficha
**Viejo:** `Sandalias / Cilindros / Mandiles para Boda / Kit anti cruda / Pantuflas / **Vasos**` (6). Y en E3, sobre "Otros": `Claro que sí! Tenemos *Vasos Popote 24 oz*` + `Cada vaso tiene un costo de *$35*`.
**Nuevo:** lista de 5 sin Vasos, en las ~30 corridas de boda. En E3: `¿Le interesa sumarlos a la cotización? Dígame: Cantidad, Código postal` y nada más.

**Causa verificada — son DOS fixes, no uno.**
1. El record `Imagen Principal | Todos los productos` (bot 60810, Boda) enumera 5 productos. Un campo. **Pero el texto con "Vasos" no existe en Airtable** ni en `descripcion` ni en `CURL` (el `CURL` también lista 5 y encima con otro cierre). La versión vigente vive sólo en el salesbot de Kommo → hay que ir a buscarla ahí.
2. Cuando W3 no devuelve ficha para el par evento×producto, **el agente no cae de vuelta al prompt**, que sí tiene el dato (`Vasos popote: $35`, `MÍNIMO 50 piezas`, líneas 168 y 225 del prompt congelado). El mecanismo exacto: `Cards a partes` tiene un fallback (`Déjame revisar eso y te confirmo`) que sólo dispara si `partes.length === 0`, pero en step_3 siempre se hace `partes.push(CTA_STEP_3)` antes — **el fallback es inalcanzable por construcción**. Fix de nodo, dos líneas, y cubre también E1.

**Ticket que hoy nunca se ofrece:** 50 × $35 = $1.750 mínimo.

---

#### R5 · Toda imagen que no sea una foto simple de producto deriva a una persona y deja el lead mudo
**Viejo (G5, las mismas 3 imágenes):** `Qué bonito diseño de sandalias! Quiere que continuemos con el proceso para cotizar su pedido?` + pide cantidad, grosor y CP.
**Nuevo:** `Ya avisé al equipo para que una persona te ayude con esa imagen.`
El efecto cascada está documentado en el propio test: la primera corrida de G5 se anuló porque *"la derivación de G4 había dejado la oportunidad en `En Espera` y el bot estaba en silencio"*.

**Dos precisiones que cambian el fix.** (a) *"Derivar traba el lead"* es **heredado**: el viejo hace PATCH a `status_id: 91266100` y su main tiene la guardia `If7` sobre ese status. Lo que difiere es la **clasificación**. (b) El formato queda descartado como causa: en G5 el viejo recibió las tres como **archivos PNG** y las procesó igual.

**Hay TRES variables confundidas, no dos.** `Analizar producto` (W7) recibe **una sola URL** y su prompt ordena `falso` ante *"más de un tipo"* o ante duda; con `debounce_seg: 15` para media, un álbum de Telegram colapsa a **la última imagen**. Así que además de formato y contenido, no sabemos **cuál** de las N imágenes se analizó. El re-test tiene que incluir un álbum donde la última sea una foto limpia de producto.

---

#### R6 · La nota de voz devuelve el JSON de error de GHL al cliente
**Nuevo:** `GHL rechazo la subida (HTTP 400). {"status":400,"message":"Invalid File Type","name":"HttpException","code":"INVALID FILE TYPE","traceId":"af74ecb1-…` — el turno entero se pierde.
**Viejo:** ignora el audio pero mantiene la conversación viva.

**Salvedad de atribución:** el canje `file_id` → Media Library es específico del carril de Telegram (cableado el 18/8, un día de vida, cero corridas previas). En producción por WhatsApp el adjunto llega con URL propia y el 400 puede no reproducirse. **Lo que hay que arreglar sí o sí es la fuga**: cualquier fallo del pipeline de media hoy le muestra al lead un JSON con traceId.

---

### 🟠 S2

**R7 · "Otros" con material de XV en cilindros.** Verificado agrupando por URL de media: **5 records de Otros comparten archivo con su gemelo de XV** — `Cilindros Info`, `Cilindros Catálogo 1`, `Cilindros Catálogo 2` (las dos apuntan al mismo archivo, duplicado latente) y las dos de anticrudas. De esos 5, **sólo los 3 de cilindros son regresión** (el viejo sí manda la ficha de bautizo *"Mi Bautizo / Lesly / 13 de mayo 2017"* y las grillas de graduación y comunión); los 2 de anticrudas fallan igual en los dos agentes → heredado. Los archivos correctos están en los salesbots de Kommo. **Caduca con la baja.**

**R8 · El cross-sell dirigido cae de 7 a 2.** Conté las 9 apariciones de `"ya que pides"` en las 6.701 líneas: **2 del nuevo** (A1 cilindros, D5 mandiles) contra **7 del viejo**, sobre un número comparable de cotizaciones (~13-14 por lado). Está mandado explícitamente en el prompt congelado (líneas 8, 30 y sección `#Criterio de prioridad en Aumento de Ticket`), idéntico en los dos. La capacidad existe y dispara; la frecuencia se desplomó. Baja el ticket medio en todas las cotizaciones.

**R9 · El nuevo asume la variante de pantufla donde el viejo pregunta (C4).** Ante *"las pantuflas de satín"* el viejo frena (`necesitaría confirmar si se refiere a las *Pantuflas Mono Satín* o a otro modelo`) y el nuevo cotiza `50 Pantuflas Mono Satín`, que no es la que el lead nombró (la lisa se personaliza con nombre y fecha; la de moño va 1 diseño cada 50 pares). Causa probable: el bloque que agregó el delta 07 a `Canonicalizar productos` (*"pantuflas mono satin → SOLO si el usuario nombró el satín"*), que empuja a resolver la variante en vez de preguntar. El paso 4 (muestra digital) debería atraparlo, pero después de cobrado el anticipo.

**R10 · Reenvía el catálogo de sandalias dentro del turno de pantuflas (B5).** El nuevo despacha el PDF de sandalias (`6a62bf3a0e0316cbe00f3312.pdf`, identificado en B1/B2) + un video de sandalias en un turno de pantuflas; el viejo manda sólo material de pantuflas. Distinto del reenvío heredado de B2, donde fallan los dos.

---

### 🟡 S3

- **PDFs con nombre de hash.** El nombre legible no se perdió (está en `ghl_media.name`), pero la Media Library sirve el hash. Costo externo bajo; costo interno alto: el diagnóstico de A3 sólo se pudo cerrar cruzando **tamaños** de archivo.
- **La prueba social va antes de la cotización.** Estructural, no azar: `Partir en burbujas` hace `fichasFinales.concat(partes)`. El orden del viejo (cotizar y después tranquilizar) atiende la objeción cuando aparece. Una línea.
- **El dump de "todos los productos" sale desordenado.** La query de W3 hace `ORDER BY subcategoria NULLS FIRST, nombre` (alfabético). El viejo agrupa ficha→catálogo→video por producto. Una línea de SQL.
- **"Aquí tienes el enlace para realizar el pago"** cuando lo que adjunta es un PDF. Fijar la frase en `Partir en burbujas`, donde ya vive el bloque del marcador `url1234.com123`.

---

## 4. Fallos heredados — no bloquean, pero son deuda del producto

| Fallo | Casos | Nota |
|---|---|---|
| **Sandalias para hombre**: ninguno aclara que sólo hay modelo de mujer | F7 | Para el negocio es grave (pedido de 50+ pares → reclamo o devolución). La regla ya existía como fix del prompt de Kommo. |
| **Talla**: ninguno la responde, aunque está en la ficha (unitalla 25.5 cm) | F4 | Mismo mecanismo que F7: la ficha reemplaza a la respuesta. |
| **Mandiles en XV**: ninguno bloquea el producto fuera de su evento | E1 | El viejo encima **afirma que sí los tiene** contra su propio catálogo. No existe ninguna ficha de mandiles fuera de Boda. |
| **Logo o diseño propio**: ninguno deriva | H1 | La regla está escrita (`agente-recolector.md:188`). Es incumplimiento en ambos, no funcionalidad ausente. |
| **Desambiguación de variantes** (normales/moño, peluche/satín, "costalitos") | C1, C2, C7 | En C7 la regla está textual en los dos prompts y ninguno la cumple. |
| **Pantufla de moño en "Otros"** | E2 | El record de Otros se llama literalmente `Pantuflas XV` y su asset es `Pantuflas XV.jpeg`. Airtable ya era la copia. |
| **Anticrudas en "Otros"** cae en material de XV | A3, E4 | Verificado: mismo archivo en los dos. |
| **Nota de voz**: ninguno transcribe ni usa el contenido | G3 | El audio daba evento, producto y cantidad. El viejo tiene la cadena `Get_Audio → Transcribir → Aggregate` cableada, así que merece diagnóstico propio antes de asumir que no existe. |
| **Reenvío de material ya mostrado** | B2 | Ninguno de los dos lleva registro de qué despachó. |
| **La ráfaga no se junta**: el ganador procesa sólo su texto | H4 | Ver §6, punto 7. |

---

## 5. Lo que el nuevo aporta

- **Mandiles elegibles** (delta 08, Oscar 17/8): grilla numerada ①–⑤ → el lead pide "el 1 y el 3" y **cotiza** ($240 + $250 = $490, correcto). El viejo, con una foto sin numerar, no puede y nunca cotiza.
- **Pantufla de moño de peluche** (delta 07): una sola ficha, la pedida. El viejo manda las tres + PDF + video. Beneficio colateral: ese camino no expone el $29.
- **Ubicación separada de "¿es estafa?"** (delta 06) y **URLs peladas** en vez de markdown roto. Los dos casos que F1/F2 venían a verificar los falla el viejo.
- **Persistencia del evento (G1).** Se resuelve con el propio transcript: en G1 **ninguno** de los dos emitió el saludo inicial, o sea que ninguno venía de sesión limpia — y aun así el viejo re-preguntó el evento y el nuevo lo conservó. Es `hpf_estado_sesion` funcionando. G2 repite el patrón.
- **Deriva por fecha imposible (H3)** donde el viejo queda mudo. Es cumplimiento de una regla común, no una mejora de diseño.
- **No inserta el saludo espurio** a mitad de conversación (4 apariciones del viejo: B10, C1, C3, E4).
- **Mejor infraestructura de mínimos que el viejo.** `Formatear salida` de W4 documenta el delta: en el original el Set exponía sólo `resumen_cajas`, así que un rechazo por mínimo llegaba al agente vacío; el nuevo expone `message_to_agent` y `detalle_violaciones`.
- **La línea "(Pedidos solo para eventos 2026)"**: no es un agregado del nuevo. Está mandada verbatim en el prompt congelado pre-migración (`agente-main-image.md:9 y :20`, dentro de un bloque *"Incluye DE FORMA FIJA EL SIGUIENTE MENSAJE"*). **El que incumple su propia spec es el viejo, en 50/50 corridas.**

---

## 6. Correcciones al resumen de Camilo

La corrida es excelente: 50 casos × 2 agentes con evidencia literal pegada de los dos lados es lo que permitió todo este análisis, y varias de las trampas (capturas incompletas, corridas sobre el evento equivocado) las declaró él mismo. Lo que hay que ajustar es **la atribución de causas**, que en cinco de siete apunta al lugar equivocado y sobredimensiona el trabajo.

1. **Precios ($1 menos):** el síntoma es correcto y es S1. La causa **no** es que el LLM se equivoque ni que alguien haya cargado mal a mano: es el campo `descripcion` de Airtable migrado tal cual. Son **5 records, no 3**, y **sí aplica a Boda**.
2. **"Falta el producto Vasos Popote":** el producto **no falta**. Está en el prompt ($35, mínimo 50) y tiene ficha con imagen en Boda y en XV. Faltan una línea de texto y una rama de fallback. Además, **E3 se corrió en "Otros", el único evento donde legítimamente no hay ficha de vasos** (verificado: el catálogo tiene el record en Boda y XV, no en Otros), así que la conclusión "el nuevo no conoce el producto" no está probada.
3. **"No avisa el mínimo de cilindros":** correcto, pero **no es un defecto independiente** — es la misma frase enlatada del punto 8 de su propia lista. Y la tool no es la culpable: W4 tiene `Cilindros: 40` y su relay de rechazos es mejor que el del viejo. Perseguirlo por separado es trabajo desperdiciado.
4. **"Falta el set de material de Otros":** sobredimensionado ~4×. Otros tiene **18 fichas migradas y activas**; lo que está mal es a qué apuntan **5** de ellas, y sólo **3 son regresión** (cilindros). El PDF de pantuflas de Otros **sí** está migrado: el nuevo manda `6a62bf3af9c6f6a920d2e17f.pdf — 212.7 KB` y el viejo `PANTUFLAS_EVENTOS_OTROS — 213 kB`. Mismo archivo.
5. **"Las imágenes que no son foto simple derivan":** correcto y S1, pero *"traba el lead"* es **heredado** (el viejo también saca al lead de circulación al derivar). Y hay **tres** variables confundidas, no una.
6. **"No aclara que los mandiles no se personalizan":** el síntoma es correcto y S1. La causa **no es el LLM**: es que la ficha con el disclaimer, el precio y el mínimo **nunca se envía**, en las 6 corridas. Fix de selección de fichas, no de prompt. (Y dado el principio ya medido en este proyecto — arreglos por nodo 4/4 y 5/5 contra prompt 4/7 y 3/5 — ir por el prompt otra vez era el camino con peor historial.)
7. **"Ráfaga: responde el saludo duplicado":** es **artefacto del carril de prueba**. `TG · armar payload` fija `debounce_seg: 0` sólo para texto de Telegram, con el comentario del propio nodo explicando por qué; en producción `Normalizar entrada` aplica 50 s y el mecanismo "gana el último" deja pasar una sola ejecución. **No debería reproducirse por WhatsApp.** Lo real y compartido es que ninguno de los dos junta la ráfaga. (Verificado por lectura de código, no por ejecución.)

**Bonus:** el reset por `/b` que quedó marcado como anomalía en H5 es un alias deliberado del whitelist (`/b /borrar /reset /clear /nuevo /nueva`) y además el viejo no tiene reset, así que está fuera del alcance de la paridad.

**Un error del documento que conviene corregir antes de que se propague:** el resumen de H3 abre con *"Cotización previa idéntica en los dos: $2,100"* y la transcripción del nuevo no contiene ninguna cotización (el propio paréntesis lo aclara). Tal como está redactado, borra la regresión más cara del bloque y deja H3 como una victoria limpia. Lo mismo, menor: B4 y F5 tienen encabezados de "captura incompleta" con el turno pegado completo abajo.

---

## 7. Lo que quedó sin resolver

**Re-tests obligatorios antes del cutover (baratos):**

1. **B10 — el más caro.** Es el camino exacto que arregló la persistencia del evento el 12/8, y la corrida termina antes del turno decisivo: nadie pidió un producto después del cambio de evento. Y la trampa documentada de esa implementación (una rama paralela corre **después** con `executionOrder: v1`, así que `isExecuted` da false) hace que un smoke pueda dar verde por casualidad si el LLM acierta el evento solo. **Re-correr con un cuarto turno pidiendo producto.**
2. **G4/G5 con las tres variables separadas:** foto jpg limpia en álbum de 3 · un .png de una sandalia sola · una captura de pantalla como foto jpg · y un álbum donde la **última** sea foto limpia.
3. **G4 con lo que pedía el guion:** se mandó un `.png` en vez de `.zip`/`.docx`. (Para PDF el hueco es menor: W7 ya tiene rama `¿Es PDF?` → `Analizar comprobante`.)
4. **La imagen de la pantufla de Boda:** ¿el $29 está quemado en el asset o sólo en el texto? Define si el fix son 5 campos o 5 campos + 1 archivo.
5. **El PDF de datos bancarios.** El nuevo entrega 2.4 MB y el viejo `NUMEROS DE CUENTA NUEVA` de 2.0 MB. En todos los demás pares de assets los tamaños coinciden al kilobyte. Nadie abrió ninguno de los dos. Es el documento con el que el lead transfiere el anticipo: chequeo de dos minutos que no se hizo.

**Sin evidencia y sin cerrar:** D3/D4 (mandiles en y bajo el mínimo — parcialmente cubierto por C8/H2, que sí tienen captura completa), E4/E5 (cobertura del dump y exclusión de producto).

**Verificaciones que el test pedía y no se registraron:** si llega aviso al grupo del equipo en las derivaciones (H1, H2, H5, **G4, G5** — justo los dos que trabaron el lead); si el silencio del viejo en H3 fue derivación silenciosa o falta de respuesta (mirar la etapa en Kommo); si la derivación por fecha imposible de H3 **también** deja el lead mudo en `En Espera` — si aplica, convierte una mejora en trampa operativa para leads calientes.

**Cobertura que el test no tiene:** la **validación de formato de código postal** (el viejo detectó "CP 4410" y pidió el dígito faltante; no está como regla en ningún prompt, así que es emergente y no hay razón para asumir que se hereda) y la **regla de 1 diseño cada 50 pares**, que está dos veces en el prompt congelado y ninguno de los dos menciona jamás, ni siquiera con 400 sandalias.

**Y el gate temporal, que es lo más urgente aunque no sea un bug:** los textos vigentes de las fichas y al menos 3 assets de cilindros de "Otros" viven **sólo dentro de los salesbots de Kommo**. El `CURL` cubre 40 de 65 fichas y en varios casos (Vasos) ni siquiera trae la versión vigente. Existe el workflow `kommo-salesbot-text-capture-runner` (`bYMfYToYsZMFpVDw`) justo para eso: **hay que correrlo completo antes de dar de baja esa cuenta**, junto con la bajada de assets que ya estaba pendiente. Después del apagado, varios de estos fixes dejan de ser posibles.

---

### Camino corto sugerido

Los 6 S1 son: 5 campos de texto (R1) · 1 campo + 2 líneas de nodo (R4) · 1 fix de selección de término (R3) · 1 fix de nodo en el pipeline de media (R6) · 1 diagnóstico de clasificación (R5) · 1 intermitencia a medir con repeticiones (R2). **Ninguno pide reescribir un prompt.** Con eso resuelto y B10 re-corrido, el nuevo queda en condiciones de reemplazar al viejo.