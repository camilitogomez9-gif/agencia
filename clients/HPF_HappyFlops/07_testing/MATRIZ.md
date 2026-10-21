# MATRIZ — protocolo de paridad HPF · Fase 1 congelada

**Congelada:** 2026-08-05 · **Build bajo test:** `hpf-inbound-handler-testbuild-nodebounce-2026-08-05.json`
`sha256 f92ceb1c422e6f7614a5ef75a7dfa3410cbbc03f60e9b16c5cc1b7ef945159d1` · `versionId 4fc5b0c7-0ef0-4a7b-b5fd-1dc5e8033b45` · 71 nodos

> **Regla del protocolo:** a partir de acá **solo se puede agregar**, nunca borrar ni reformular.
> Achicar el denominador después de ver los resultados es cómo "pasaron" los tres intentos anteriores.
>
> Derivación reproducible: `python3 scripts/testing/hpf-derivar-matriz.py`
> Todo lo que sigue sale de ahí o del build congelado. Nada se eligió a ojo.

---

## 1. Matriz A — conversacional

**Cálculo:** `3 eventos × 4 pasos × 11 clases de entrada = 132 celdas`

- **eventos:** Boda · XV · Otros — confirmados como los tres reales en el `ALIAS` del build
  (`jsCode:108-112`: `BAUTIZO`/`CUMPLEAÑOS`/`GRADUACION`/`EMPRESARIAL` → `OTROS`)
- **pasos:** saludo · imagen de evento · fichas de producto · cotización/cierre
- **clases:** producto puntual · pedido colectivo · producto ambiguo · producto fuera del evento ·
  cantidad + CP · debajo del mínimo · pregunta de negocio · imagen · audio · comprobante · ráfaga

### 1.1 Lo que sostiene el oráculo observado

| | |
|---|---|
| Transcripts | 10 · **269 turnos** · 125 `LEAD` · 72 `RECIBE` |
| `RECIBE` vacíos (`{}`) | **13** → mensajes reales al lead: **59**, no 72 |
| Eventos | **9 XV · 1 Boda · 0 Otros** |
| **Celdas con oráculo `OBSERVADO`** | **17 / 132 (13 %)** |

Las 17 celdas cubiertas:

| Celda | Turnos | Ejemplos |
|---|---|---|
| Boda · saludo · pregunta de negocio | 1 | `sample_3:T1` |
| Boda · fichas · pregunta de negocio | 2 | `sample_3:T7,T9` |
| Boda · fichas · ráfaga | 3 | `sample_3:T5,T9,T13` |
| XV · saludo · producto puntual | 3 | `sample_6:T1`, `sample_8:T1`, `sample_9:T1` |
| XV · saludo · pregunta de negocio | 5 | `sample_1:T1`, `sample_9:T1` |
| XV · imagen de evento · ráfaga | 7 | `sample_1:T5`, `sample_5:T5` |
| XV · fichas · producto puntual | 21 | `sample_4:T7,T9` |
| XV · fichas · pedido colectivo | 2 | `sample_9:T7,T9` ← **el caso "todos"** |
| XV · fichas · producto ambiguo | 11 | `sample_2:T16,T18` |
| XV · fichas · pregunta de negocio | 27 | `sample_1:T7`, `sample_2:T20` |
| XV · fichas · imagen | 4 | `sample_2:T20`, `sample_8:T14` |
| XV · fichas · comprobante | 4 | `sample_4:T60,T62,T64,T66` |
| XV · fichas · ráfaga | 46 | `sample_1:T9`, `sample_2:T8` |
| XV · cotización · producto ambiguo | 4 | `sample_4:T44`, `sample_8:T39` |
| XV · cotización · cantidad + CP | 6 | `sample_4:T14,T16` |
| XV · cotización · pregunta de negocio | 4 | `sample_2:T12`, `sample_7:T15` |
| XV · cotización · ráfaga | 7 | `sample_2:T14`, `sample_4:T16` |

### 1.2 Justificación de las 115 celdas sin oráculo observado

El protocolo exige **una línea por celda excluida**. Se agrupan por causa, porque la causa es la misma
y repetirla 115 veces sería ruido, no rigor. Ninguna se excluye del universo: todas quedan con un
grado de oráculo asignado, que es lo que el gate G1 pide.

| Grupo | Celdas | Por qué no hay `OBSERVADO` | Grado asignado | ¿Entra al denominador P0? |
|---|---|---|---|---|
| **Todo el evento `Otros`** | 44 | Cero samples. El router legacy colapsaba lo no-XV a `Boda` — se ve literal en `sample_3`, donde el lead dice *"Son 50 años"* y el `DECIDE` responde `"evento":"Boda"`. No es muestreo: la rama no se alcanzaba | `REGLA` (`05_reglas_negocio.md:62-69`) + `CSV` (`Otros-Grid view.csv`) | Sí, 2 casos |
| **`Boda` salvo 3 celdas** | 41 | Un solo sample, y mal clasificado | `CSV` (`Boda-Grid view.csv`) + build (`jsCode:102`) | Sí, 4 casos |
| **Clase `audio`** | 12 | Cero ocurrencias en 10/10 samples | `REGLA` (el `Switch by Message Type` tiene rama `audio` → Whisper) | Sí, 1 caso |
| **Clase `debajo del mínimo`** | 12 | Cantidades observadas: 50,50,50,50,50,60. El mínimo es 50: nunca se pidió menos | `REGLA` (`05_reglas_negocio.md:32-40,155`) | Sí, 2 casos |
| **Clase `producto fuera del evento`** | 12 | Solo aparece como `DECIDE` en `sample_9:T7` (mandiles dentro de un XV), nunca como `RECIBE` | `REGLA` + build (`jsCode:35 ev:["BODA"]`) | Sí, 2 casos |
| **`imagen de evento` salvo 1 celda** | ~10 | El paso existía pero salía por salesbots de Kommo, fuera del stream del LLM → no quedó en los transcripts | build (`jsCode:102-104`) | Sí, 2 casos |
| **Resto** | ~4 | Combinaciones que el embudo no produce (ej. `comprobante` en `saludo`) | `JUICIO` | No — a `PARKING.md` |

> **Consecuencia que hay que decir y no suavizar:** las **18 fichas de producto verbatim** —la superficie
> que el protocolo más protege— **no tienen ni un `RECIBE` observado**, porque el original las mandaba
> como bloques pre-horneados de Kommo, fuera del stream. Su oráculo es grado `CSV`, nunca `OBSERVADO`.
> Comparar la ficha contra el propio `jsCode` sería tautología: se comparan contra
> `00_migracion_ghl/00_inputs/*-Grid view.csv`, que es fuente independiente.

---

## 2. Matriz B — topológica

Derivada del build congelado: **16 nodos de decisión · 34 aristas · 4 sumideros · 30 nodos con llamada externa.**

### 2.1 Los 4 sumideros

Salidas sin destino. **No son cobertura faltante: son defectos del build**, y van a la entrega como tales.

| Sumidero | Qué pasa cuando se toma | ¿Alcanzable? | Caso |
|---|---|---|---|
| `Switch by Message Type[fallback]` | El lead **no recibe nada** | **Sí** — `Auth + Normalize` deja pasar un `message_type` desconocido (ej. `sticker`) sin media | `HPF-TOP-018` |
| `Es El Ultimo Mensaje?[false]` | La ejecución muere sin error ni respuesta | Sí, con ráfaga | `HPF-TOP-019` *(requiere waits)* |
| `Evento Recien Identificado?[false]` | No se manda imagen principal ni promo | Sí, camino normal | `HPF-TOP-020` |
| `Es Origen Telegram? (Post)[true]` | En Telegram no corre `Update last_outbound_at` ni la cadena de imagen/promo | Sí, **siempre** en Telegram | `HPF-TOP-021` |

### 2.2 Cobertura de las 34 aristas

| Nodo | Aristas | Cubiertas por | N/A con razón |
|---|---|---|---|
| `If` (comando /b) | 2 | — | 2 · solo alcanzable por `Telegram Trigger`; el webhook no pasa por ese `If` |
| `¿Media de Telegram?` | 2 | `HPF-CAN-022` (false) | 1 · true requiere `telegram_file_id`, que solo produce el trigger nativo |
| `Switch by Message Type` | 4 | `HPF-CAN-022` (text), `HPF-CAN-023` (image), `HPF-CAN-024` (audio), `HPF-TOP-018` (fallback) | 0 |
| `¿Audio de Telegram?` | 2 | `HPF-CAN-024` (false→Download) | 1 · true idem `¿Media de Telegram?` |
| `Es Pago Detectado?` | 2 | `HPF-COT-016` (true), casi todos (false) | 0 |
| `Es Stage Pausado?` | 2 | todos (false) | 1 · true requiere stage pausado en GHL → `PARKING-01` |
| `Es El Ultimo Mensaje?` | 2 | todos (true), `HPF-TOP-019` (false) | 0 |
| `¿Es test?` | 2 | todos (false) | 1 · true es el nivel C del protocolo: **prohibido** como gate |
| `Loop Message Parts` | 2 | todos | 0 |
| `Es Origen Telegram?` | 2 | todos los Telegram (true), `HPF-CAN-025` (false) | 0 |
| `¿Parte con foto?` | 2 | `HPF-FIC-008` | 0 |
| `¿Parte con documento?` | 2 | `HPF-FIC-008` | 0 |
| `¿Parte con video?` | 2 | `HPF-FIC-008` | 0 |
| `Es Origen Telegram? (Post)` | 2 | `HPF-TOP-021` (true), `HPF-CAN-025` (false) | 0 |
| `Evento Recien Identificado?` | 2 | `HPF-EVT-005` (true), `HPF-TOP-020` (false) | 0 |
| `Es Origen Telegram? (Pago)` | 2 | `HPF-COT-016` (true) | 1 · false es la rama GHL de pago → `PARKING-02` |

**`aristas_cubiertas / aristas_totales` = 26 / 34.** Las 8 restantes tienen razón escrita arriba.

---

## 3. Los 25 casos P0

**Leyenda.** `intención`: `PARIDAD` = tiene que hacer lo mismo que el original · `DELTA` = distinto a
propósito, firmado · `NO-REPLICAR` = copiar al original **es una falla**.
`severidad`: `S1` = cambia si el lead compra o si Rebeca tiene que intervenir (**único gate go/no-go**) ·
`S2` = se nota pero no cambia el resultado comercial · `S3` = cosmético.
`req`: `waits` = necesita los `Wait` reactivados, corre al final y **fuera del denominador** de esta corrida.

### 3.1 Saludo y evento

| id | intención | sev | oráculo | canal | turnos | input | esperado / assert |
|---|---|---|---|---|---|---|---|
| `HPF-SAL-001` | PARIDAD | S2 | `OBSERVADO` `sample_9:T2` + build `jsCode:116-119` | telegram | 1 | `hola` | 3 partes byte-exactas de `SALUDO_PARTES`. La parte 2 termina en **espacio** (`'…su evento? '`) — se afirma sobre `message_part`, no sobre el texto entregado: Telegram recorta el final |
| `HPF-SAL-002` | PARIDAD | S1 | `OBSERVADO` `sample_9:T1` | telegram | 1 | `Hola buenos días me puedes dar información acerca del precio de sandalias` | Saluda **y** no ignora el pedido. Positivo obligatorio: menciona sandalias |
| `HPF-EVT-003` | PARIDAD | S1 | build `jsCode:103` | telegram | 2 | `hola` → `xv años` | Menú de XV byte-exacto. **`'*Mandiles para Boda*' not in partes`** |
| `HPF-EVT-004` | PARIDAD | S1 | build `jsCode:102` + `Boda-Grid view.csv` | telegram | 2 | `hola` → `boda` | Menú de Boda byte-exacto, **con** `*Mandiles para Boda*` |
| `HPF-EVT-005` | PARIDAD | S2 | build `jsCode:104` + `ALIAS jsCode:110` | telegram | 2 | `hola` → `es para un bautizo` | Resuelve a `OTROS`. Menú de Otros byte-exacto. Cierra `Evento Recien Identificado?[true]` |
| `HPF-EVT-006` | PARIDAD | S3 | build `jsCode:103-104` | telegram | 2 | `hola` → `graduación` | El menú de XV termina en `información  😊` (**dos** espacios) y el de Otros en `información 😊` (**uno**). Diferencial byte-exacto |

### 3.2 Fichas de producto y media

| id | intención | sev | oráculo | canal | turnos | input | esperado / assert |
|---|---|---|---|---|---|---|---|
| `HPF-FIC-007` | PARIDAD | S1 | `CSV` `XV-Grid view.csv` | telegram | 2 | `xv años` → `quiero sandalias` | Ficha de sandalias byte-exacta contra el CSV. `tool_invocada(MOSTRAR_PRODUCTOS)` |
| `HPF-FIC-008` | PARIDAD | S1 | build `jsCode:29-95` | telegram | 2 | `boda` → `quiero sandalias y cilindros` | **Ejerce las 3 aristas de media**: `¿Parte con foto?[true]`, `¿Parte con documento?[true]`, `¿Parte con video?[true]`. `entrega_ok` con `n_entregadas == n_esperadas` |
| `HPF-FIC-009` | PARIDAD | S1 | `OBSERVADO` `sample_9:T7-T9` | telegram | 2 | `xv años` → `Precio de todos` | Devuelve los productos del menú de XV. **`'Mandiles' not in partes`** — ver decisión provisional D-01 |
| `HPF-FIC-010` | PARIDAD | S1 | `REGLA` `05_reglas_negocio.md:38` + build `jsCode:35` | telegram | 2 | `xv años` → `quiero mandiles` | Gate de evento: **no** manda la ficha de mandiles en XV |
| `HPF-FIC-011` | PARIDAD | S2 | `CSV` `Boda-Grid view.csv` | telegram | 2 | `boda` → `quiero mandiles` | Sí manda la ficha de mandiles, byte-exacta contra el CSV |
| `HPF-FIC-012` | PARIDAD | S3 | build `jsCode` (regresión v18) | telegram | 2 | `boda` → `qué colores de tapas hay` | **Regresión conocida:** el v18 preservaba dos NBSP (`*colores*\xa0que\xa0gustes`) y el vivo tiene cero. Documenta el defecto, no lo tapa |

### 3.3 Cotización, mínimos y pago

| id | intención | sev | oráculo | canal | turnos | input | esperado / assert |
|---|---|---|---|---|---|---|---|
| `HPF-COT-013` | PARIDAD | S1 | `OBSERVADO` `sample_4:T14-T16` | telegram | 3 | `xv años` → `quiero sandalias` → `50 piezas, cp 61800` | Cotiza. `tool_invocada(COTIZADOR)` **y** `tool_invocada(CALCULAR_ENVIO)`. No vuelve a pedir cantidad ni CP |
| `HPF-COT-014` | PARIDAD | S1 | `REGLA` `05_reglas_negocio.md:37,155` | telegram | 3 | `boda` → `quiero cilindros` → `35 cilindros, cp 44680` | Mínimo de cilindros = 40. **Rechaza y lo dice.** `tool_no_invocada(COTIZADOR)`. Es el incidente real del 2026-07-15 |
| `HPF-COT-015` | PARIDAD | S2 | `REGLA` `05_reglas_negocio.md:32` | telegram | 3 | `boda` → `quiero sandalias` → `50 pares, cp 44680` | Justo en el mínimo: **sí** cotiza |
| `HPF-COT-016` | PARIDAD | S1 | build `Es Pago Detectado?` | telegram | 2 | `boda` → `ya hice la transferencia, les paso el comprobante` | Detecta pago. Cierra `Es Pago Detectado?[true]` y `Es Origen Telegram? (Pago)[true]` |
| `HPF-COT-017` | PARIDAD | S2 | build `jsCode:121` | telegram | 2 | `boda` → `cómo hago el pedido` | Bloque `SIETE_PASOS` byte-exacto. La línea 2 **es un espacio, no está vacía** |

### 3.4 Las 7 filas `NO-REPLICAR`

Van **sí o sí**, con su firma y su "qué hace el nuevo en su lugar" — que **sí existe**, contra lo que
afirma `protocolo:168` (ver §3.6). Todo negativo lleva un positivo obligatorio al lado (regla 6):
un regex negativo sobre texto libre del LLM da verde con el bug reproduciéndose.

| id | conducta del original que **NO** se replica | firma | qué hace el nuevo | sev | canal |
|---|---|---|---|---|---|
| `HPF-NRP-018` | Loop de repetición: re-manda info y re-pide datos que ya tenía (~30 % de los leads) | `reunion-2026-05-21-rebeca-casos.md:15,36` → `02_mejoras:28` → `04_agentes_llm.md:107-116` → `E-01` | Usa lo ya capturado. **Positivo:** en T3 cotiza reusando el CP exacto de T2 | **S1** | ghl |
| `HPF-NRP-019` | Re-pide cantidad y CP después de haber cotizado | `reunion:13` → `02_mejoras:28` → `04_agentes_llm.md:109-111` | No re-pregunta. **Positivo:** responde al comentario del lead | **S1** | ghl |
| `HPF-NRP-020` | Cotiza pantuflas de moño como si fueran satín clásicas | `reunion:21` → `02_mejoras:31` → `04_agentes_llm.md:152-156` → `E-04` | **Confirma la variante antes** de llamar `COTIZADOR` | **S1** | telegram |
| `HPF-NRP-021` | Pide mail para mandar cotización en PDF en vez de escalar | `reunion:23,59` → `02_mejoras:32` → `04_agentes_llm.md:290-292` → `E-05` | No promete PDF ni pide email. Deriva al equipo | S2 | telegram |
| `HPF-NRP-022` | Escala el chat cuando le piden un catálogo, en vez de mandarlo | `reunion:27,54-56` → `02_mejoras:34` §5 D2 → `04_agentes_llm.md:118-127` → `E-07/E-08` | **Manda el catálogo.** `tool_no_invocada(ATENCION_PERSONALIZADA)` | **S1** | telegram |
| `HPF-NRP-023` | Escala cuando le piden "fotos" en la desambiguación de pantuflas | `reunion:29` → `02_mejoras:35` → `04_agentes_llm.md:129-131` → `E-09` | Manda las fotos de las variantes | S2 | telegram |
| `HPF-NRP-024` | No reconoce vasos con popote en imágenes; no cotiza y escala | `reunion:25` → `02_mejoras:33` → `04_agentes_llm.md:377-379` → `E-06` | Categoría `VASO_POPOTE` del Vision Classifier | S2 | telegram |

**Fila #8, nueva — no estaba en el protocolo.** El oráculo tiene **13 turnos donde el original
respondió `{}`**: el lead reenvía el mismo texto 5-6 veces contra el silencio (`sample_4:T29-T37`,
`sample_6:T17-T25`, `sample_8:T19-T23`). Quedarse mudo es la peor conducta del original y no estaba
en las 7 filas precargadas.

| id | conducta | qué hace el nuevo | sev | canal |
|---|---|---|---|---|
| `HPF-NRP-025` | Responder `{}` — el lead no recibe nada | **Siempre responde algo.** `n_esperadas >= 1` (regla 2 del runner) | **S1** | telegram |

### 3.5 Topológicos y de canal *(fuera del denominador P0, listados aparte)*

| id | qué ejerce | sev | req | nota |
|---|---|---|---|---|
| `HPF-TOP-018b` | `Switch by Message Type[fallback]` con `message_type: "sticker"` | S2 | — | Sumidero alcanzable: el lead no recibe nada |
| `HPF-TOP-019` | `Es El Ultimo Mensaje?[false]` | S2 | **waits** | Requiere ráfaga real |
| `HPF-TOP-020` | `Evento Recien Identificado?[false]` | S3 | — | Camino normal de segundo turno |
| `HPF-TOP-021` | `Es Origen Telegram? (Post)[true]` | S2 | — | Documenta que en Telegram no corre la cadena de imagen/promo |
| `HPF-CAN-022` | rama `text` completa | S1 | — | Camino feliz |
| `HPF-CAN-023` | rama `image` → Vision Classifier | S2 | — | Requiere `media_url` |
| `HPF-CAN-024` | rama `audio` → Whisper | S2 | — | Requiere `media_url` de audio |
| `HPF-CAN-025` | rama GHL completa (`Es Origen Telegram?[false]`) | **S1** | ghl | Sin esto, toda la familia de estado queda sin verificar |

### 3.6 Corrección al protocolo, aplicada acá

`protocolo:168` afirma que la especificación de qué debe hacer el nuevo en lugar de cada
`NO-REPLICAR` *"hoy no existe en ningún lado"*. **Es falso para las 7.** Existe, redactada línea por
línea, en tres archivos que el ANEXO C no lista y que quedan citados en la tabla de §3.4:

- `00_migracion_ghl/02_logica_validada/02_mejoras_post_reunion_2026-05-21.md`
- `00_migracion_ghl/03_arquitectura_ghl/04_agentes_llm.md`
- `00_migracion_ghl/04_guia_migracion/08_testing_precutover.md` (Test Plan E, `E-01…E-10`)

`protocolo:156` también atribuye mal la firma: dice que las 7 salen de *"Rebeca 21/5 y las decisiones
del 12/5"*, pero `01_decisiones.md` (12/5) **no contiene ninguna de las 7**. El firmante real es el
doc del 26/5.

---

## 4. Núcleo de regresión (8)

Verde en **2 corridas consecutivas** desde memoria limpia, con los `Wait` reactivados.

`HPF-SAL-001` · `HPF-EVT-003` · `HPF-FIC-008` · `HPF-FIC-009` · `HPF-FIC-010` · `HPF-COT-013` ·
`HPF-COT-014` · `HPF-NRP-025`

Criterio: uno por familia, priorizando los S1 y los que ejercen más aristas. `HPF-NRP-025` entra
porque "el bot no contestó" es el defecto que más sangra y el único que un corpus mal diseñado no
puede ni declarar.

---

## 5. G2-bis — gate de mutación

Cada defecto tiene que romper **al menos un caso nominal, con `FALLA` y diff de bytes**. Un
`SIN-EVIDENCIA` **no aprueba el gate**: mediría la fragilidad del runner, no la sensibilidad del corpus.

| # | Defecto sobre el build vivo | Punto de inyección | Casos que deben romperse |
|---|---|---|---|
| 1 | Borrar la entrada `id:"sandalias"` del `CATALOGO` | `Sanitize` `jsCode:29-34` | `HPF-FIC-007`, `HPF-FIC-008`, `HPF-FIC-009` |
| 2 | `$25` → `$24` en el prompt | `systemMessage` | `HPF-COT-013`, `HPF-COT-015` |
| 3 | Apagar `returnIntermediateSteps` | `Vendedor (LLM Agent)` | **Solo cuenta el efecto funcional**: `leerSteps` vacío → `fichas=[]` → `HPF-FIC-007/008`. Los asserts de `tool_invocada` que se caen son instrumentación y quedan **fuera** del gate |
| 4 | Borrar `ev:["BODA"]` de la ficha de mandiles | `Sanitize` `jsCode:35` | `HPF-FIC-010`, `HPF-FIC-009` |
| 5 | Sacar el header `⏳(7 DIAS DE PROMO)⏳` | `systemMessage` + `jsCode:310` | `HPF-COT-013`, `HPF-COT-015` |

Los 5 se revierten y la reversión **se verifica por re-export y sha256**, nunca por memoria.

---

## 6. Denominador declarado

| Grupo | Casos | Entra al gate |
|---|---|---|
| P0 contables (Telegram) | **21** | Sí |
| P0 canal GHL (`HPF-NRP-018`, `-019`, `HPF-CAN-025`) | 3 | Sí, si hay GHL. Si no: `BLOQUEADO-POR-CANAL` y va en la primera línea de la entrega |
| Requieren `Wait` reactivados (`HPF-TOP-019`, ráfaga) | 1 | No — corren al final, listados aparte |

**Total: 25.** Ver `PARKING.md` para lo que quedó fuera con su razón.

> **Sin porcentaje agregado.** El resultado se reporta **por familia**. Un "21/25 = 84 %" se lee como
> paridad y no lo es: si la rama GHL no corrió, el titular es *"0 de 6 familias de estado verificadas"*.

---

## 7. AMPLIACIÓN — casos derivados del chat con Oscar (jul/ago)

**Agregados el 2026-08-05**, después de congelar. El protocolo permite **agregar, nunca borrar**: por
eso van en una sección aparte y con la fecha, para que se vea qué entró después.

Fuente: export de WhatsApp del grupo HPF, mensajes de julio y agosto. Cada caso cita el mensaje que
lo origina. Esto es oráculo grado **`OBSERVADO` (cliente)** — es la queja literal de quien paga, que
es más autoritativo que el CSV.

### 7.1 Quejas que todavía no tenían caso

| id | intención | sev | origen | turnos | input | assert |
|---|---|---|---|---|---|---|
| `HPF-COT-026` | PARIDAD | **S1** | Oscar 31/7 17:36: *"lo de que pregunte el grosor de la suela está bien · lo de la tapa no tiene porque preguntarlo, tiene que cotizar así"* | 3 | `boda` → `quiero sandalias` → `50 pares delgadas, cp 44680` | Cotiza. **`'tapa' not in partes`**. Positivo obligatorio: aparece el total |
| `HPF-FIC-027` | PARIDAD | **S1** | Oscar 31/7 17:36: *"los mandiles ni le pedí y me está diciendo que cuántos mandiles quiero agregar"* | 2 | `boda` → `quiero sandalias` | **`'mandil' not in partes`** — no ofrece lo que no se pidió. Positivo: manda la ficha de sandalias |
| `HPF-NRP-028` | NO-REPLICAR | **S1** | Oscar 31/7 17:34 y 3/8 16:44: *"le dije lo que quería y volvió a mandarme toda la información"* | 3 | `xv años` → `quiero pantuflas de satín` → `50 pares, cp 44680` | **La versión Telegram del anti-loop.** No re-manda la ficha en T3. Positivo: cotiza con el CP de T3 |
| `HPF-EVT-029` | PARIDAD | **S1** | Juanpi, audio 5/8: *"si dice que quiere todos y todavía no sabe el evento, se le pregunta el evento"* | 2 | `hola` → `quiero precio de todos` | Pregunta el evento **antes** de listar productos |

### 7.2 Regresión — quejas del 3/8 que el build vivo parece haber corregido

Verificadas por lectura del `jsCode`, **no por ejecución**. Entran como casos para confirmar que están
arregladas de verdad y que no vuelven.

| id | sev | queja original | por qué parece arreglado | input |
|---|---|---|---|---|
| `HPF-FIC-030` | **S1** | Oscar 3/8 16:42: *"en las pantuflas solo me mandó las cerradas, no mandó las otras 2 de moño"* | `jsCode:365-370` empuja las 3 variantes si no hay variante ni cantidad en el mensaje | `xv años` → `quiero pantuflas` |
| `HPF-FIC-031` | S2 | Oscar 3/8 17:19: *"aquí no mandó el catálogo de los cilindros"* | `cilindros` tiene `cat:"cat_cilindros"` | `boda` → `quiero cilindros` |
| `HPF-FIC-032` | S2 | Oscar 3/8 17:19: *"a la de moño de satín le mandó el video de la de peluche (la de satín no tiene video, solo catálogo)"* | `pantufla_satin` **no** tiene campo `v:`; `pantufla_peluche` sí | `boda` → `quiero las pantuflas de moño de satín` |
| `HPF-FIC-033` | S2 | Oscar 3/8 17:20: *"la de peluche dice que es de satín y que cuesta $30 · debe decir de peluche y cuestan $35"* | La ficha viva dice `Pantufla de moño de peluche` y `$35 el par` | `boda` → `quiero pantuflas de peluche` |

### 7.3 Fichas verbatim contra el texto del cliente

`HPF-FIC-034` · PARIDAD · **S2** · canal telegram

Oscar mandó los textos canónicos de las 8 fichas el **1/8 (14:58-15:25)** y corrigió la de peluche el
**3/8 (17:30 y 17:38)**, y pidió explícitamente: *"pongan las descripciones que les pasé el sábado"*
(3/8 16:42). Eso convierte su mensaje en el oráculo de mayor autoridad para las fichas — por encima
del CSV y por encima del v18.

**Comparación ya hecha (lectura, no ejecución) — las 8 difieren:**

| Ficha | Diferencia |
|---|---|
| `pantufla_peluche` | Oscar 3/8: `blanca, negra, morada, rosa` · vivo: `blanca, negra, morada y rosa` → **la corrección del 3/8 no se aplicó** |
| `sandalias` | Oscar: `📦 Pedido mínimo de 50 pares."` (comilla suelta) · vivo: sin la comilla |
| `mandiles` | Oscar: `✨ Mandiles🍾 Ideales para el novio…` en una línea · vivo: partido en dos |
| las 8 | Oscar usa una línea con **un espacio** como separador · el vivo usa línea vacía |

Las tres primeras son de contenido. La cuarta es el mismo tipo de defecto preservado que la línea 2
del bloque de 7 pasos, que **es un espacio y no está vacía**.

**D-02 resuelta (la agencia, 5/8): la referencia es el texto que manda el bot hoy.** Las dos erratas de
Oscar quedan corregidas y el separador de línea vacía se mantiene. `HPF-FIC-034` se corre comparando
contra el `f:` del build congelado.

`HPF-FIC-035` · PARIDAD · **S1** · telegram — **corrección del cliente sin aplicar.**
No es verbatim, es contenido: Oscar corrigió los colores de la pantufla de peluche el **3/8 a las
17:30 y 17:38** (las dos veces, XV y Boda) de `blanca, negra, morada y rosa` a
`blanca, negra, morada, rosa`, y el bot sigue con la versión del 1/8. Input: `boda` → `quiero
pantuflas de peluche`. Assert: la ficha contiene `blanca, negra, morada, rosa`. **Hoy este caso falla
por diseño** — es un fix pendiente, y por eso entra como S1: es una instrucción explícita del cliente
que se perdió.

### 7.4 Denominador actualizado

| | antes | ahora |
|---|---|---|
| P0 contables | 21 | **30** |
| Canal GHL | 3 | 3 |
| Requieren `Wait` | 1 | 1 |
| **Total** | **25** | **34** |

Presupuesto de reloj: 34 casos × ~2,5 turnos × ~12 s ≈ **17 minutos** de reloj puro. El techo de 25
del protocolo se excede por decisión de la agencia y por pedido explícito del cliente, no por deriva.
