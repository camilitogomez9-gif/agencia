# Protocolo de paridad HPF — v1

**Para:** Camilo · **Ejecutar en:** tu sesión de Claude Code, sobre este repo
**Objetivo:** que el bot nuevo se comporte como el original en todo lo que importa, y que eso quede **demostrado**, no afirmado.

> Este protocolo existe porque ya hubo tres intentos que se declararon listos y no lo estaban. No fallaron por falta de esfuerzo: fallaron porque se verificó a un nivel que no era el que le falla al cliente, y porque la lista de casos se eligió a ojo. Todo lo que sigue está diseñado contra eso.

---

# PARTE 0 — El contrato (leé esto entero; el resto es consulta)

## Las 6 reglas

1. **El oráculo son los 10 transcripts reales, no el código.** Están en `07_testing/oraculo/`. Si un esperado no sale de ahí, de los CSVs de Airtable o del catálogo de mensajes, se marca `INFERIDO` y **no cuenta para ningún gate**.
2. **El denominador se congela antes de mirar los resultados.** La matriz de casos se escribe en Fase 1 y a partir de ahí **solo se puede agregar**, nunca borrar ni reformular. Achicar el denominador después de ver el resultado es cómo "pasaron" los intentos anteriores.
3. **Nada existe sin artefacto en disco.** Un caso solo puede estar en `PASA` si hay un archivo con el texto literal que recibió el lead. Sin archivo el estado es `SIN-EVIDENCIA`, y cuenta como falla.
4. **Observar y arreglar son fases separadas.** En Fase 2 se corre todo y solo se anota. El mapa completo de fallas va antes del primer fix. (Excepción acotada en §Fase 2.)
5. **Paridad no es el objetivo en todo.** El original tiene 9 fallas que el propio cliente reportó. Cada caso lleva `intención: PARIDAD | DELTA | NO-REPLICAR`. En un caso `NO-REPLICAR`, copiar al original **es una falla, no un acierto**.
6. **A Oscar no le escribe nadie.** El canal es Juanpi por Telegram. Si Juanpi no está, se espera o se sigue con el default escrito — pero no se escribe a Oscar.

## Los 4 antipatrones que producen verdes falsos

Estos cuatro son los que reproducen el fracaso anterior de una forma **indistinguible del éxito**. Si rompés uno, el número que reportes no vale nada:

1. **Verificar con `channel:"test"` y llamarlo verificación.** Ese modo devuelve el output crudo del LLM y **se saltea el nodo `Sanitize + Split Output`**, que es donde viven las 15 fichas verbatim, las fotos, el filtro de voz y el corte en burbujas. O sea: se saltea todo lo que el lead realmente recibe. Sirve como pre-chequeo, nunca como evidencia de gate.
2. **Normalizar strings en los asserts.** Nada de `.trim()`, `.strip()`, colapsar espacios ni normalizar unicode. Buena parte de la paridad son **defectos preservados a propósito**: el NBSP en la ficha de tapas de termos, los dos espacios antes del 😊 en el caption de XV, `catalogo` sin tilde en cilindros y `catálogo` con tilde en mandiles. Normalizar da verde y borra justo lo que se está midiendo.
3. **Confundir "la tool se invocó" con "la tool escribió".** En Telegram las tools de GHL devuelven **404 siempre** (el `opportunity_id` es `tg_opp_<chatid>`, sintético). Una `toolHttpRequest` que falla le pasa el texto del error al LLM y **el nodo queda en verde**. Además: nunca verifiques tool calls con `nombre in json.dumps(steps).lower()` — eso matchea contra el texto de un error o el argumento de otra tool. Parseá `intermediateSteps` y compará `action.tool` por igualdad.
4. **Correr dos casos seguidos sin resetear.** La memoria vive en `n8n_chat_histories` con ventana de 30 mensajes y el `debounce_buffer` está keyed por contacto. Sin limpiar entre casos, los casos de anti-loop dan verde **por contaminación**, no por lógica.

## El tripwire (esto es lo que te salva el día)

> **Corridos los primeros 20 casos, si el pase está por debajo del 60%: PARÁS y le mandás el número crudo a Juanpi antes de escribir un solo fix.**

Renegociar el alcance es decisión de Juanpi, no tuya. El protocolo te obliga a que el dato le llegue temprano y con números, no tarde y con excusas. Lo mismo con cualquier bloqueo: se comunica **en el momento en que se detecta**, nunca recién en la entrega.

## El plan del día

| Franja | Qué | Gate |
|---|---|---|
| 0:00–0:30 | **Pre-flight.** Accesos y export del workflow vivo | G0 |
| 0:30–2:00 | **Fase 1.** Congelar oráculo, matriz y decisiones | G1 |
| 2:00–5:00 | **Fase 2.** Correr todo sin arreglar nada. Baseline | G2 |
| 5:00–8:00 | **Fase 3.** Arreglar por familias y re-verificar | G3 |
| 8:00–8:30 | **Entrega** a Juanpi | — |

**Techo de alcance para hoy, ya decidido — no lo amplíes:** ≤25 casos P0, promedio ≤2 turnos, **una** corrida completa + una de regresión sobre un núcleo de 8. Todo lo demás gatea el cutover, no la demo de mañana.

**Por qué ese techo:** un turno del sistema real cuesta **30-45 segundos de reloj** (15 s de debounce fijo + el agente con un prompt de 19 KB + 2 s entre partes). Presupuestá en turnos, no en casos: `turnos × 40 s`. 25 casos × 2 turnos ≈ 33 min de puro reloj, y eso **sin** contar diagnóstico. Si planificás 90 casos no entrás, y lo primero que vas a saltear a la hora 9 es el reset entre casos — que es justo lo que invalida la medición.

**Podés paralelizar por `contact_id`:** el debounce está keyed por contacto, así que N casos concurrentes no se pisan.

---

# PARTE 1 — Pre-flight (30 min, bloqueante)

Nada de esto es trámite. Cada ítem que falle cambia el plan, y hay que descubrirlo **ahora**, no a la hora 3.

## P1. Accesos

- [ ] Entrás al n8n de Happy Flops.
- [ ] Exportás el workflow `IPO1c36NLzkXrBh9` y lo committeás como `03_workflows/hpf-inbound-handler-live-<fecha>.json`.
- [ ] Credencial Postgres de memoria (`n8n_chat_histories` + `debounce_buffer`) responde.
- [ ] Sub-cuenta GHL: hay un contacto de prueba **con opportunity** en el pipeline. Verificalo por curl, no por la UI.
- [ ] Bot de Telegram responde.

**Si el export no sale, no hay protocolo.** Escalá a la agencia en el momento.

## P2. Qué versión está viva realmente

El repo y n8n **ya divergieron antes**. No asumas que corre lo que dice el repo. Sobre el export que acabás de hacer, comparás 4 valores contra v17 y v18:

| Qué mirar | Dónde |
|---|---|
| chars del `systemMessage` | nodo `Vendedor (LLM Agent)` |
| `options.returnIntermediateSteps` | nodo `Vendedor (LLM Agent)` — **tiene que estar en `true`** |
| chars del `jsCode` | nodo `Sanitize + Split Output` |
| `amount` | nodo `Wait 1.5s Between Parts` y `Wait 15s (Debounce)` |

- Si matchea v17 → aplicás el v18 pegando los 4 nodos de `06_docs/snippets/clipboard-v18-nodos-tocados-2026-07-31.json`.
- Si no matchea ninguna versión conocida → es un Frankenstein. Decidilo con la agencia antes de seguir.
- **Nunca re-importes el JSON completo.** En este cliente un re-import ya rompió configs de tools, y además borra el binding de la credencial Header Auth del webhook (síntoma: HTTP 500 instantáneo en ~0.8 s, antes de que corra el agente).

## P3. Cómo vas a llegar al sistema

- [ ] Confirmás el host del webhook **del workflow exportado**, no del doc (hay dos hosts contradictorios dando vueltas).
- [ ] Guardás en `.env`: `HPF_N8N_WEBHOOK_URL`, `HPF_WEBHOOK_AUTH_HEADER_NAME`, `HPF_WEBHOOK_AUTH_HEADER_VALUE`.
- [ ] Mecanismo de reset: hoy `/b` solo existe en la rama de Telegram. Conectá `Webhook - Inbound` al mismo IF, o usá un `contact_id` único por caso derivado del id del caso. **Sin una de las dos, ningún caso de anti-loop se puede contar.**

> ⚠️ `scripts/testing/test-hpf-webhook.py` apunta al **bot viejo**. No lo uses como harness de esto sin repuntarlo.

## P4. Lo que sale por Juanpi a primera hora

Esto no depende del testing y **tiene fecha de vencimiento real** (la cuenta de Kommo se va a dar de baja y estos archivos solo viven ahí):

> Oscar: para cerrar el bot nuevo necesitamos 3 cosas que solo están dentro de Kommo —
> (1) el PDF de **números de cuenta**; (2) los **videos** de producto; (3) los **catálogos PDF** de mandiles, pantuflas y sandalias.
> Sin el PDF de cuentas el bot no puede cerrar el Paso 5 solo.

---

# PARTE 2 — Fase 1: congelar el oráculo y la matriz (1:30)

**En esta fase no se toca una línea de código.** Al cerrarla, `git diff` sobre `03_workflows/` y `04_agents/` no muestra cambios de lógica.

## Paso 0 — El oráculo ya está extraído

`07_testing/oraculo/` tiene **10 transcripts reales de producción del bot original**: 269 turnos, 72 mensajes que el lead efectivamente recibió y 72 decisiones internas del Router y del agente de productos.

Estuvieron sin usar en el repo desde el 2026-05-03. Los intentos anteriores creyeron que había una sola conversación — el JSON es una lista de un elemento que adentro tiene el array de 10, y `len()` sobre el wrapper da 1.

Para regenerarlos: `python3 scripts/testing/hpf-extraer-oraculo.py`

Cada archivo marca tres cosas:
- `LEAD` — lo que escribió el cliente, saneado y listo para usar como input de test
- `RECIBE` — **lo que el bot original le mandó. Esto es el esperado.**
- `DECIDE` — la decisión interna (`step_N`, `productos[]`, `evento`). No la ve el lead, pero es un corpus **etiquetado** de entrada → decisión

**Regla dura:** un bloque canónico tomado del propio v18 no es oráculo, es tautología — testea que el código es igual a sí mismo. El oráculo sale de los transcripts, de los CSVs de Airtable (`00_migracion_ghl/00_inputs/*-Grid view.csv`) o del catálogo de mensajes.

## Paso 1 — La matriz de cobertura

La cobertura **no se elige, se deriva**. Así se escapó "todos" durante tres meses.

**Matriz A — conversacional.** Producto cartesiano de:

- **evento**: Boda · XV · Otros
- **paso**: saludo · imagen de evento · fichas de producto · cotización/cierre
- **clase de entrada**: producto puntual · pedido colectivo ("todos") · producto ambiguo (pantuflas moño vs satín) · producto fuera del evento (mandiles en XV) · cantidad + CP · debajo del mínimo · pregunta de negocio · imagen · audio · comprobante · ráfaga

Escribís el cálculo (`dimensiones × valores = N celdas`) y **una línea de justificación por cada celda que excluís**. Sin el cálculo escrito la matriz es ad hoc y el gate no pasa.

**Matriz B — topológica.** Derivada del JSON con `jq`: enumerá las salidas de todo nodo `if` / `switch` / `splitInBatches` y todo nodo con llamada externa, y exigí por cada arista **o bien un caso, o bien un N/A con razón escrita**. Son 20 líneas de `jq` y habría cazado los 4 sumideros silenciosos sin depender de la memoria de nadie.

## Paso 2 — Cada caso lleva estos campos

| Campo | Valores |
|---|---|
| `id` | `HPF-<CLASE>-<NNN>` |
| `intención` | `PARIDAD` · `DELTA` · `NO-REPLICAR` — **obligatorio**, con puntero al doc que lo firma |
| `severidad` | `S1` · `S2` · `S3` |
| `oráculo` | `OBSERVADO` (transcript) · `CSV` · `REGLA` · `JUICIO` · `INFERIDO` |
| `canal` | `telegram` · `ghl` · `ambos` |
| `evidencia` | ruta al artefacto — vacío = `SIN-EVIDENCIA` |

**Severidad, definida sin ambigüedad:**
- **S1** — cambia si el lead compra, o si Rebeca tiene que intervenir. *Es el único gate go/no-go.*
- **S2** — se nota pero no cambia el resultado comercial.
- **S3** — cosmético.

> **Verbatim NO es gate duro.** En el original la exactitud de bytes sí era funcional, porque los 4 sub-workflows de seguimiento se encadenaban por match de substring del último mensaje. En el sistema nuevo ese acoplamiento **no existe**. Verbatim entra como S2/S3 salvo donde demuestres que algo aguas abajo depende del texto literal. Si lo dejás como bloqueante vas a perder dos horas persiguiendo un NBSP mientras "todos" sigue roto.
>
> **Regla de secuencia:** no se toca ninguna fila S3 mientras quede una S1 o S2 abierta.

## Paso 3 — El delta ya viene precargado

Antes de escribir un solo caso propio, cargá estas filas. Salen de la reunión con Rebeca del 21/5 y de las decisiones del 12/5, y **son comportamientos del original que NO hay que replicar**:

| # | Conducta del original | Intención |
|---|---|---|
| 1 | Loop de repetición: re-manda info y re-pide datos que ya tenía (~30% de los leads) | `NO-REPLICAR` |
| 2 | Re-pide cantidad y CP después de haber cotizado, si el lead sigue comentando | `NO-REPLICAR` |
| 3 | Cotiza pantuflas de moño como si fueran satín clásicas | `NO-REPLICAR` |
| 4 | Pide mail para mandar cotización formal en PDF en vez de escalar a humano | `NO-REPLICAR` |
| 5 | Escala el chat cuando le piden un catálogo, en vez de mandarlo | `NO-REPLICAR` |
| 6 | Escala cuando le piden "fotos" en la desambiguación de pantuflas | `NO-REPLICAR` |
| 7 | No reconoce vasos con popote en imágenes; a veces no cotiza y escala | `NO-REPLICAR` |

Para cada `NO-REPLICAR`, escribí **en una línea** qué tiene que hacer el sistema nuevo en su lugar. Hoy esa especificación no existe en ningún lado, y sin ella el caso no es testeable.

**Si no hacés este paso, el resultado predecible es que codifiques los bugs del original como aserciones y "arregles" el sistema nuevo para que vuelva a fallar.** El repo tiene 2.749 líneas describiendo el bot roto contra 196 de decisiones de mejora: la asimetría te empuja sola hacia ahí.

## Paso 4 — "todos": ya tiene comportamiento observado

**Sacalo de decisiones abiertas.** `07_testing/oraculo/sample_9.md` tiene el caso literal. Ante `"Precio de todos"` en un evento **XV**, el original respondió:

```json
{"evento":"XV","subcategoria":"Producto Principal",
 "productos":["pantuflas","sandalias","cilindros","mandiles","anticrudas","vasos"],
 "texto_dinamico":"¿Le interesa sumarlos a la cotización?\nDígame:\n- Cantidad\n- Código postal\n¡Gracias!"}
```

Dos cosas importantes:
- Devuelve **los 6 productos** y después pide cantidad + CP una sola vez.
- **Ignora el gate de evento**: mete `mandiles` en una conversación de XV, cuando la regla de negocio dice que mandiles es solo de Boda.

Eso último es la única decisión real que queda, y va **con default y sin bloquear**:

> **Default (implementalo así):** en pedido colectivo se respeta el gate de evento — en XV no se manda mandiles.
> **Pregunta para Juanpi, con la evidencia:** *"el original en pedido colectivo ignora el gate por evento y mete Mandiles en XV. ¿Lo replicamos o lo corregimos? Corregirlo es lo que implementé; volver atrás son 10 minutos."*

## Paso 5 — Decisiones: nunca te bloqueás

Estado `PROVISIONAL-EJECUTOR`: aplicás el default escrito, seguís trabajando, y la decisión **se promueve sola a la primera sección del paquete a Juanpi**, redactada como pregunta ("decidí X porque Y; si preferís Z son N minutos").

El gate exige que las provisionales estén **listadas**, no firmadas. A las 3 de la mañana no hay a quién preguntarle, y un gate que exige una firma inalcanzable se convierte en un gate decorativo que vas a firmar vos.

**`decisiones-abiertas.md` sale para Juanpi apenas cerrás la Fase 1**, no al final del día: es el único artefacto que bloquea a un tercero.

## Gate G1

- [ ] `MATRIZ.md` existe, con el cálculo de N escrito y una justificación por celda excluida
- [ ] 100% de los casos tienen `intención` (ninguno vacío) y las 7 filas precargadas están
- [ ] 100% de los casos tienen `oráculo` con fuente citada
- [ ] 0 casos con `oráculo: INFERIDO` dentro del set contable
- [ ] Matriz B: `aristas_cubiertas / aristas_totales` reportado
- [ ] `decisiones-abiertas.md` enviado a Juanpi
- [ ] `git diff` sobre `03_workflows/` y `04_agents/` sin cambios de lógica

> **Control humano más barato de todo el protocolo:** mandale la matriz congelada a Juanpi o a la agencia **antes** de empezar a ejecutar. Diez minutos aprobando el denominador valen más que todos los gates autoverificados juntos, porque es lo único que un revisor externo puede evaluar de verdad.

---

# PARTE 3 — Fase 2: observar sin arreglar (3:00)

## Paso 1 — La superficie de verificación

Esto es la corrección más importante del protocolo. **Se verifica sobre lo que se entrega, no sobre lo que se calcula.**

Escalera, de mejor a peor. Usá el escalón más alto que puedas y **declará cuál usaste**:

| Nivel | Qué es | Vale como gate |
|---|---|---|
| **A. Evento de entrega** | tabla `hpf_outbound_log(run_id, canal, idx, message_part, photo_url, http_status, ts)`, con un nodo de log **en rama paralela** antes de cada uno de los 5 emisores | ✅ sí |
| **B. Array de Sanitize** | el `{message_part, photo_url}[]` que sale del nodo, con `¿Es test?` movido río abajo | ⚠️ sí para contenido, no para entrega |
| **C. `channel:"test"` tal cual está hoy** | output crudo del LLM | ❌ nunca |

Los 5 emisores: `Send Photo (Telegram)`, `Send a text message1`, `Send Message via GHL`, `Send Imagen Principal`, `Send Promo Evento`.

**Por qué importa:** aun moviendo el `¿Es test?` detrás del Sanitize, el camino de test sigue omitiendo `Loop Message Parts`, `Es Origen Telegram?`, los 3 emisores, `Wait 1.5s Between Parts` y toda la cadena `Es Origen Telegram? (Post) → Get Current Opportunity → Check Evento Just Set → Send Imagen Principal → Send Promo Evento` — que es el **segundo emisor de la imagen de catálogo** y solo existe en la rama no-Telegram. Podés cerrar el gate al 95% sobre un camino que ningún lead recorre. Sería la misma falla histórica con otro nombre: antes "verifiqué el prompt", ahora "verifiqué el Sanitize".

**Si tocás la topología:** export con sha256 antes, nodo por nodo (nunca re-import), y un smoke inmediato después — un mensaje real por Telegram, no solo el curl.

**Dos tipos de evidencia, no los mezcles:**
- **Contenido byte-exacto** → sobre el payload del emisor (fila de `hpf_outbound_log` o JSON crudo de `getUpdates`). **Nunca sobre texto pegado a mano.**
- **Entrega** (llegó como foto y no como URL, orden, caption ≤1024, espaciado ~2 s) → captura visual, con asserts estructurales.

## Paso 2 — Lo que en Telegram no se puede verificar

En Telegram el estado se pierde en cada mensaje por diseño (`Mapear Custom Fields` lo pisa) y las tools de GHL devuelven 404. Entonces **toda la familia que depende de estado no puede dar más que un verde vacío**:

`productos_mostrados` · `evento_detectado` · `cotizacion_emitida` · anti-loop · dedup · imagen-una-sola-vez · 7 pasos una sola vez

Marcá esos casos como **`BLOQUEADO-POR-CANAL`** desde la matriz. **No entran al denominador del gate de Telegram.** Si al final del día no hubo GHL, la entrega dice *"anti-loop no verificado"* — nunca "verde".

Es literalmente el bug estrella de Oscar, así que si no llegás a correrlo en GHL, decilo en la primera línea de la entrega.

## Paso 3 — Correr

- Un caso por vez, con reset de `n8n_chat_histories` y `debounce_buffer` **dentro del runner como precondición dura**. Si el DELETE falla, el caso se marca `SIN-EVIDENCIA` automáticamente, nunca verde. Todo paso manual que se repite 50 veces se saltea alrededor de la vez 30.
- Debounce en **15 s**, el de producción. Un test que pasa con 0.3 s no dice nada: con 0.3 el agente contesta globito por globito, que es una de las cosas que reclamó Oscar.
- **No escribas en ráfaga mientras testeás a mano.** Cada mensaje nuevo mata la ejecución anterior en `Es El Ultimo Mensaje?`, cuya salida `false` no está conectada: muere sin error y sin respuesta. Se lee como "el bot no contestó" y te manda a diagnosticar el bug equivocado.
- Estados cerrados: `PASA` · `FALLA` · `PARCIAL` · `SIN-EVIDENCIA` · `BLOQUEADO-POR-CANAL`. Nada de `PENDIENTE` al cerrar.

**Escribí a `MATRIZ.md` y `ESTADO.md` después de CADA caso.** Lo que no está en el archivo no existe: no sobrevive a una compactación de contexto.

## Paso 4 — Prohibido arreglar, con una excepción

En esta fase se anota y se sigue. Si el caso 3 falla, vas al 4.

**Excepción acotada:** podés aplicar un fix si desbloquea **3 o más casos pendientes**. Dos obligaciones: lo anotás en el log con la hora, y **re-corrés todo lo ya corrido** antes de cerrar la fase.

*(La excepción está para que la regla se pueda cumplir. Una prohibición absoluta se rompe a la hora 6, y cuando se rompe una regla las demás pierden fuerza — incluidas el reset entre casos y la captura del artefacto, que son las que sostienen la validez de la medición.)*

## Gate G2

- [ ] Baseline committeado **antes del primer fix**, con el sha256 del export vivo — `git log` lo demuestra
- [ ] 0 casos en `PENDIENTE`
- [ ] 0 casos en `SIN-EVIDENCIA`
- [ ] 0 casos marcados `PASA` con evidencia de nivel C
- [ ] Nivel de evidencia declarado por caso (A o B)
- [ ] Casos `BLOQUEADO-POR-CANAL` listados y fuera del denominador

### G2-bis — el gate de mutación (20 min, no lo saltees)

Un corpus que no puede fallar no mide nada. Inyectá estos 5 defectos y verificá que **cada uno rompe al menos un caso, nombrado**:

1. Borrar una ficha del mapa `CATALOGO` del Sanitize
2. Cambiar `$25` → `$24` en el prompt
3. Apagar `returnIntermediateSteps` en `Vendedor (LLM Agent)`
4. Romper el gate `evento === 'BODA'` de la ficha de mandiles
5. Sacar el header `⏳(7 DIAS DE PROMO)⏳`

Si un defecto no rompe nada, tenés un hueco en ese eje. **Revertí los 5 antes de seguir** y verificá la reversión por re-export, no por memoria.

---

# PARTE 4 — Fase 3: arreglar por familias (3:00)

## Paso 1 — Agrupar antes de tocar

Cada `FALLA` se asigna a una **familia** en `FAMILIAS.md`, con causa raíz escrita y ruta+línea. **Cero fallas huérfanas.**

Arreglar por familia y no por síntoma es lo que evita el patrón de parchear lo que se ve y dejar los hermanos vivos.

## Paso 2 — Buscar los hermanos

Por cada familia: corré la búsqueda de sitios equivalentes, **pegá los resultados**, y testeá al menos un hermano con artefacto propio. Si arreglaste un gate por evento en un lugar, hay que ver los otros lugares donde ese gate se aplica.

## Paso 3 — Re-verificar

- Todo caso re-verificado necesita **captura nueva con timestamp posterior al fix**. Prohibido marcar `PASA` reusando un artefacto viejo.
- Núcleo de regresión (8 casos): verde en **2 corridas consecutivas** desde memoria y buffer limpios. La no-flakiness se exige sobre el núcleo, nunca sobre el corpus completo — no entra en el día.

## Paso 4 — Deuda de test en cero

- [ ] Debounce de vuelta en **15**
- [ ] `returnIntermediateSteps` en `true`
- [ ] Los 5 defectos de mutación revertidos
- [ ] Instrumentación revertida (o declarada como permanente a propósito)
- [ ] Ningún nodo quedó deshabilitado
- [ ] Verificado **por re-export**, no por memoria

> **Los transcripts que le mandás a Juanpi se generan sobre el flujo final**, después de revertir todo y con el debounce en 15. Nunca antes. Si no, lo que aprueba no es lo que queda deployado.

## Gate G3

- [ ] **Cero casos S1 en rojo** — este es el único go/no-go
- [ ] 100% de las fallas asignadas a familia con causa raíz
- [ ] Cada familia con sus hermanos buscados y ≥1 testeado
- [ ] Núcleo de 8 verde en 2 corridas
- [ ] Deuda de test en cero, verificada por re-export
- [ ] `git diff --stat` toca solo archivos de la lista blanca — cualquier otro se revierte

---

# PARTE 5 — La entrega

**Invertida a propósito.** Juanpi no puede auditar un número cuyo numerador y denominador produjo la misma persona que hizo el trabajo, y no va a leer 124 filas en Telegram.

Orden obligatorio:

1. **5-6 transcripts completos, tal como los ve el lead.** El flujo feliz punta a punta, el caso "todos", y uno por rama. Esto es lo que Juanpi realmente puede evaluar.
2. **"Esto ahora es distinto A PROPÓSITO"** — la lista corta de deltas, cada uno con quién lo pidió (Rebeca 21/5, decisiones 12/5) y qué hace el nuevo en su lugar.
3. **Lo que NO se verificó**, nominal y sin suavizar. Si anti-loop quedó bloqueado por canal, va acá y en la primera línea.
4. **Las decisiones provisionales**, redactadas como preguntas con su default aplicado.
5. **El número**, como respaldo: `N/M casos · S1 N/M · celdas cubiertas N/M`, con la lista nominal de rojas y su causa raíz.

Toda afirmación de la sección 1 va etiquetada `[VERIFICADO: <ruta>]`. Prohibido escribir "debería", "probablemente", "asumo", "parece que". Solo **VERIFICADO** (con ruta), **INFERIDO** o **NO VERIFICADO**.

## Y algo que tiene que salir antes de la demo

Por Juanpi a Oscar, 10 líneas, **antes** de que vea el bot:

> *"Estas N conductas del bot viejo no las replicamos a propósito"* — cada una con quién la pidió y qué hace el nuevo en su lugar.

Sin eso, Oscar prueba, a los cuatro mensajes dice *"antes esto lo derivaba a Rebeca"* — que es una de las mejoras firmadas hace dos meses — y la demo se convierte en "sigue sin andar igual que antes", que es exactamente la frase que originó todo esto. Las aserciones no van a entrar en esa conversación.

---

# ANEXO A — Fuera de alcance, y hay que decirlo

**El sistema nuevo no tiene reactivadores.** El original tiene **41 de sus 146 salesbots** dedicados a re-engagement (R1/R2/R3 con info y sin info, r1-r6 promo, genéricos, API) más 4 sub-workflows de seguimiento en n8n (131 nodos: Rebeca, imagen, cotización, 7 pasos), con cadencia 1 h → 3 h → 8 h → 24 h. El sistema nuevo tiene **cero** — WF-02 de GHL nunca se construyó.

Es el **28% de la superficie de conducta del original**, y es una parte grande de lo que hace que un lead termine comprando. No es un problema de prompt y no se arregla en este protocolo.

**Decilo explícitamente en la entrega.** Si Oscar dice "el bot nuevo vende menos", esta puede ser la razón principal, y no va a aparecer en ninguna aserción conversacional.

# ANEXO B — Prohibiciones

- **No toques el bot original de Kommo** (`happyflops-main-v3.json` ni los 4 sub-workflows de seguimiento), y no generes leads de prueba ahí. Está en producción vendiendo USD 1.000-2.000 por día. Todo el ground truth ya está capturado en el repo.
- **No re-importes el JSON completo** del workflow nuevo. Nodos sueltos.
- **No refactorices de paso.** Cualquier mejora que no sea el fix mínimo de una familia enumerada va a `PARKING.md`.
- **No le mandes nada a Oscar.**
- **No cierres una fase con una frase.** Ni "anduvo bien", ni "quedó fino", ni "lo probé y responde". Solo conteos verificables por comando.

# ANEXO C — Rutas

| Qué | Dónde |
|---|---|
| Oráculo observado (10 transcripts) | `07_testing/oraculo/` |
| Extractor del oráculo | `scripts/testing/hpf-extraer-oraculo.py` |
| Textos canónicos (fuente independiente) | `00_migracion_ghl/00_inputs/*-Grid view.csv` |
| Catálogo de mensajes | `00_migracion_ghl/01_logica_actual/04_catalogo_mensajes.md` |
| Reglas de negocio | `00_migracion_ghl/01_logica_actual/05_reglas_negocio.md` |
| Máquina de estados | `00_migracion_ghl/01_logica_actual/03_maquina_estados.md` |
| Decisiones firmadas (el delta) | `00_migracion_ghl/02_logica_validada/01_decisiones.md` |
| Las 9 fallas de Rebeca | `00_migracion_ghl/00_inputs/reunion-2026-05-21-rebeca-casos.md` |
| Arquitectura del v18 | `06_docs/paridad-voz-rebeca-2026-07-31.md` |
| Nodos del v18 para pegar | `06_docs/snippets/clipboard-v18-nodos-tocados-2026-07-31.json` |
| Inventario de los 146 salesbots | `00_migracion_ghl/00_inputs/kommo_export.json` → `[0].salesbots` |
