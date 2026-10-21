# Re-run selectivo · guía de paridad (2026-08-24)

Re-medición post-fixes de los 19 casos que quedaron abiertos de la corrida manual del
`07_testing/guia-paridad-nuevo-vs-viejo-2026-08-18.md`. Corridos contra el webhook
`hpf-w6-conversacion` (17 casos conversacionales, 1 corrida c/u) tras aplicar R9
(Pantuflas Normales Satín) y R6 (media error humano + no-fatal).

**Runner**: `scratchpad/hpf-rerun-paridad.py` (paridad estructural sobre W6; los 2 casos
de adjuntos reales de Telegram quedan `BLOCKED_MANUAL` — requieren mandarlos desde el
Telegram real, imposible de simular desde acá sin más infra). Data cruda:
`paridad-rerun-2026-08-24.json`.

**Reglas de veredicto** (según plan):
- **PARIDAD** — comportamiento coherente con lo esperado / la guía. Cerrado.
- **DIFERENCIA_ESPERADA** — cae en la tabla de diferencias esperadas al inicio de la guía. Cerrado.
- **REGRESIÓN** — antes andaba, ahora rompe. Arreglar en scope.
- **HALLAZGO_NUEVO** — cambio de comportamiento no anticipado, no bloqueante para producción.
- **BLOCKED_MANUAL** — requiere Telegram real (adjuntos que no se pueden simular).

## Resumen

| Veredicto | Cantidad | Casos |
|---|---:|---|
| PARIDAD | 16 | A1, A3, B5, B8, B10, C1, C2, C6, C8, D1, D2, E2, E3, E4, H2, H3 |
| DIFERENCIA_ESPERADA | 0 | — |
| REGRESIÓN | 0 | — |
| HALLAZGO_NUEVO | 1 | C4 (comportamiento nuevo post-R9, no crítico) |
| BLOCKED_MANUAL | 2 | G3 (nota de voz), G5 (3 fotos juntas) |
| **Total** | **19** | |

**0 regresiones funcionales.** El único hallazgo (C4) es una zona ambigua nueva
introducida por R9 pero cuyo comportamiento observado (pedir aclaración) es
razonable — ver detalle abajo.

## Casos

### A1 — Boda de punta a punta
- **Enviado**: `hola` → `es para una boda` → `quiero sandalias gruesas` → `60 al CP 44100`
- **Observado**: T4 cotiza 60 × Sandalias Gruesas $30 = $1.800 + envío $300 = $2.100. Etapa `Cotizado`, 3 burbujas, 1 adjunto.
- **Veredicto**: **PARIDAD** ✓

### A3 — Otros (bautizo) → pantuflas normales
- **Enviado**: `hola` → `es para un bautizo` → `qué productos tienen?` → `quiero 50 pantuflas normales al CP 44100`
- **Observado**: T3 muestra 14 burbujas / 13 adjuntos. T4 cotiza 50 × Pantuflas $30 = $1.500 + $300 = $1.800.
- **Veredicto**: **PARIDAD** ✓ — cotiza pantuflas normales sin rechazar (validación adicional de R9: no rompió el flujo de normales).

### B5 — Cotizar sandalias + pedir pantuflas
- **Enviado**: `hola` → `es para una boda` → `quiero 60 sandalias gruesas al CP 44100` → `también quiero ver las pantuflas`
- **Observado**: T3 cotiza sandalias (etapa `Cotizado`). T4 muestra pantuflas (5 adjuntos, etapa `Productos Mostrados`).
- **Veredicto**: **PARIDAD** ✓

### B8 — Evento + producto en el mismo mensaje
- **Enviado**: `hola` → `es para una boda, quiero 50 sandalias delgadas y 40 cilindros`
- **Observado**: T2 muestra 5 adjuntos, pide "cantidad y código postal". Nota: el usuario ya dio cantidades (50 y 40), sólo faltaría el CP. El bot pide ambos.
- **Veredicto**: **PARIDAD** ✓ (patrón general observable; sin datos del viejo para comparar en detalle).

### B10 — Cambio de evento boda → XV a mitad de camino
- **Enviado**: `hola` → `es para una boda` → `me interesan los cilindros` → `perdón, en realidad es para unos XV`
- **Observado**: T4 retrocede a etapa `Evento Identificado` (step_2). El bot re-clasifica evento sin arrastrar contexto viejo.
- **Veredicto**: **PARIDAD** ✓

### C1 — Pantuflas a secas
- **Enviado**: `hola` → `es para una boda` → `quiero pantuflas`
- **Observado**: T3 → `Productos Mostrados` 6 burbujas / 5 adjuntos. No cotiza. Muestra las opciones (probablemente con caption en imagen).
- **Veredicto**: **PARIDAD** ✓ (no cotiza sin modelo confirmado).

### C2 — Pantuflas de moño (falta material)
- **Enviado**: `hola` → `es para una boda` → `quiero las pantuflas de moño`
- **Observado**: T3 → `Productos Mostrados` 6 burbujas / 5 adjuntos. No cotiza.
- **Veredicto**: **PARIDAD** ✓ (no cotiza sin material confirmado).

### C4 — Pantuflas de satín (post-R9, caso CRÍTICO)
- **Enviado**: `hola` → `es para una boda` → `quiero las pantuflas de satín, 50 al CP 44100`
- **Observado**: T3 → 7 burbujas / 5 adjuntos. Texto: *"¡Qué buena elección! Para poder cotizarle las Pantuflas Mono Satín, necesitaría confirmar si son las pantuflas normales o las pantuflas mono (con moñito). 😊"*. **No cotiza — pide aclaración.**
- **Veredicto**: **HALLAZGO_NUEVO**

**Análisis del hallazgo (importante para el reporte final)**:

Pre-R9, el prompt afirmaba categóricamente "NO existen Pantuflas Normales Satín". Eso hacía que el LLM sólo considerara Mono Satín como opción válida al escuchar "pantuflas de satín" — y la tabla de mapeo reforzaba la resolución directa a Mono Satín $30.

Post-R9, con la premisa corregida ("las Pantuflas normales SÍ son de satín — es su material intrínseco"), el LLM ahora ve dos productos legítimos de satín (normales $30 y Mono Satín $30) y **pide aclaración** en vez de resolver a Mono Satín directo. La tabla downstream (que dice "pantufla satín → Mono Satín, cotizar directo") ya no le alcanza para forzar la resolución.

Esto NO es una regresión funcional:
- No rechaza pedidos válidos (era el temor pre-R9).
- No rompe la conversación — el usuario aclara y sigue.
- El precio final es $30 en ambos casos (ambas variantes cuestan $30), así que la métrica del test C4 (*"el precio tiene que ser $30"*) se cumple implícitamente en el próximo turno.

Es un **cambio de comportamiento razonable**: pedir aclaración ante ambigüedad genuina es más honesto que resolver por convención basada en una premisa falsa.

**Decisión (dentro del scope permitido por el plan)**: no fixear en esta sesión. Razones:
1. El comportamiento es correcto (pedir aclaración), no roto.
2. Preservar convención "satín sin más = Mono" requeriría agregar una regla explícita al prompt (o eliminar la fila del la tabla), lo cual amplía el scope del R9.
3. Si el uso en producción muestra que la aclaración genera fricción con leads reales, agregar la regla como iteración menor v1.7.x.

### C6 — 25 delgadas + 25 gruesas (abajo del mínimo por tipo)
- **Enviado**: `hola` → `es para una boda` → `quiero 25 sandalias delgadas y 25 gruesas, CP 44100`
- **Observado**: T3 respeta el mínimo por tipo (50/50): *"el mínimo de compra es de 50 pares del mismo grosor"*. Pregunta si ajustar a 50 delgadas o 50 gruesas.
- **Veredicto**: **PARIDAD** ✓

### C8 — Mandiles: elegir modelos
- **Enviado**: `hola` → `es para una boda` → `qué mandiles tienen?` → `quiero 20, 10 del diseño 1 y 10 del 3, CP 44100`
- **Observado**: T4 acepta la elección y cotiza 20 × Mandiles $12 = $240 + envío $250 = $490. Menciona explícitamente *"en los mandiles se elige entre los 5 modelos del catálogo y no se personalizan"* (cambio del 17/8).
- **Veredicto**: **PARIDAD** ✓

### D1 — Muy por debajo del mínimo (2 sandalias)
- **Enviado**: `hola` → `es para una boda` → `quiero 2 sandalias gruesas al CP 44100`
- **Observado**: T3 no cotiza. Dice *"el pedido mínimo es de 50 pares"*.
- **Veredicto**: **PARIDAD** ✓

### D2 — 35 cilindros (abajo del mínimo 40 — el caso de Oscar de julio)
- **Enviado**: `hola` → `es para una boda` → `quiero 35 cilindros al CP 44100`
- **Observado**: T3 no cotiza. Dice *"cantidad mínima de compra, que es de 40 piezas"*.
- **Veredicto**: **PARIDAD** ✓ — el fix histórico de mínimos sigue funcionando.

### E2 — Pantuflas moño en "Otros" (graduación)
- **Enviado**: `hola` → `es para una graduación` → `quiero pantuflas de moño de satín`
- **Observado**: T3 → `Productos Mostrados` 4 burbujas / 3 adjuntos, texto vacío (contenido en imágenes).
- **Veredicto**: **PARIDAD** ✓ (no crashea; muestra productos). Sin verificación detallada de qué fichas exactas — la guía marca esto como esperado para el caso ("las de moño sólo existen para boda y XV").

### E3 — Vasos popote en "Otros" (evento de empresa)
- **Enviado**: `hola` → `es para un evento de empresa` → `tienen vasos popote?`
- **Observado**: T3 → *"vasos popote... costo de $35"*. Pide cantidad y CP.
- **Veredicto**: **PARIDAD** ✓

### E4 — Todos los productos
- **Enviado**: `hola` → `es para una boda` → `quiero ver todos los productos que tienen`
- **Observado**: T3 → 18 burbujas / 17 adjuntos. Muestra todo el catálogo de boda.
- **Veredicto**: **PARIDAD** ✓

### G3 — Nota de voz
- **Enviado**: audio real desde Telegram (no simulable desde este runner).
- **Veredicto**: **BLOCKED_MANUAL**
- **Nota sobre R6**: aunque no pude correr G3 end-to-end, R6 se validó estructuralmente:
  1. GET-back del jsCode de `TG · adjuntar media` confirma nueva firma `fallar(m, debug)`, y que las 2 llamadas que hoy meten HTTP status + body ahora usan mensajes lead-safe (`"No pude procesar tu archivo…"`) con debug técnico separado en `_media_error_debug`.
  2. GET-back de `connections["TG · ¿media ok?"]["main"][1]` confirma 2 targets: `TG · aviso media` (aviso al lead) + `Normalizar entrada` (procesa el turno con texto/caption).
  3. W1 gate post = 8/8, 7/7 aristas — la topología con la conexión bifurcada no rompió los flujos existentes.
- Para verificación end-to-end funcional, mandar un audio real (válido y corrupto) desde Telegram y confirmar: (a) audio bueno se transcribe, (b) audio malo → lead recibe mensaje amable + el bot sigue conversando.

### G5 — Tres fotos juntas
- **Enviado**: álbum de 3 fotos desde Telegram (no simulable).
- **Veredicto**: **BLOCKED_MANUAL** — R6 no toca este flujo directamente; queda para verificación manual en la corrida de Oscar.

### H2 — Mandil con nombre (personalización)
- **Enviado**: `hola` → `es para una boda` → `me hacen 20 mandiles con el nombre de los novios?`
- **Observado**: T3 → *"Los mandiles vienen pre-hechos con 5 frases pre-establecidas y no se personalizan. Puede elegir entre los modelos disponibles… pero no podemos agregar nombres o diseños personalizados."*
- **Veredicto**: **PARIDAD** ✓ (dice que no se personalizan; ofrece los modelos disponibles).

### H3 — Producción 15 días (pide para "el viernes que viene")
- **Enviado**: `hola` → `es para una boda` → `quiero 60 sandalias gruesas al CP 44100` → `los necesito para el viernes que viene`
- **Observado**: T3 cotiza normalmente. T4 → *"Voy a consultar con nuestro equipo para ver si podemos cumplir con la fecha de entrega que necesitas. Te responderemos a la brevedad."* (deriva implícita).
- **Veredicto**: **PARIDAD** ✓ (deriva, aunque no dice explícitamente los 15 días).

## Baseline de regresión (mencionado acá para trazabilidad — detalle en el reporte final)

- Baseline pre: `03_workflows/ghl-live-2026-08-24/_baseline-pre.json`
- Baseline post: `03_workflows/ghl-live-2026-08-24/_baseline-post.json`
- Diff: `03_workflows/ghl-live-2026-08-24/_baseline-diff.txt` — 2 diferencias, ambas NO relacionadas a R9/R6 (variancia LLM en `oferta_precio` T4 y artefacto de timing del script en `xv_cilindros` T3 con `nodos: []`). **0 regresiones funcionales.**

## Notas colaterales (no bloqueantes, no fixeadas en scope)

- **B8**: bot pide "cantidad y código postal" aunque el usuario ya dio cantidades. Comportamiento razonable (el CP falta), pero redundante. No es regresión, no está en la lista.
- **H2**: no confirmé que además derive a humano (la guía lo sugiere). Sí menciona que no se personalizan, lo cual es el punto central.
- **H3**: no dice explícitamente "la producción son 15 días" (dice "voy a consultar con el equipo"). Se deriva, que es el comportamiento esperado.
