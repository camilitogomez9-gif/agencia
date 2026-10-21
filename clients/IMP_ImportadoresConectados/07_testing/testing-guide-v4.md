# Guía de Testing — Agente Importadores Conectados v4

**Canal:** Instagram DM / WhatsApp / Facebook
**Prompt versión testeada:** v1.6
**Estado:** Pendiente

---

## Contexto

Guía de **re-test** de los casos que fallaron o salieron parciales en la testing v3 (prompt v1.5). El prompt v1.6 incorpora 4 correcciones. Esta guía valida que esos fallos quedaron resueltos sin romper los casos que ya andaban bien.

**Correcciones aplicadas en v1.6:** caso #3, caso #6, caso #27, Flujo 13 turno 4 (fallo grave: audio repetido).

---

## Instrucciones de uso

1. Ejecutar cada caso en el canal de prueba.
2. Fijar `{{ORIGEN}}` según se indique en la columna.
3. Pegar la respuesta exacta en "Resultado obtenido".
4. Marcar OK como `true`, `false` o `parcial`.
5. Agregar notas al pie si hay patrones sistémicos.

---

## Casos RE-TEST v1.6

| # | Caso previo | Mensaje a enviar | Variable `{{ORIGEN}}` | Resultado esperado (v1.6) | Resultado obtenido | OK |
|---|---|-----------------|---|-------------------|-------------------|----|
| 3 | false | `¿Cuánto cuesta el programa?` (primer mensaje) | `directo` | PRIMERO `[AUDIO:RESPUESTA_INICIAL]` (apertura obligatoria aunque el lead pregunte precio). Dentro del texto del audio, UNA pregunta para calificar. NO da precio en el primer mensaje. Recién con contexto del lead presenta IC con USD 497 + 4 pilares. | | |
| 6 | false | `¿El programa es solo de importación?` (después de calificar) | `directo` | Menciona EXPLÍCITAMENTE los 4 pilares: módulos (importación, finanzas, marketing, ecommerce, ventas), clases grabadas con acceso ilimitado, clases EN VIVO conmigo y con expertos, 3 meses de acompañamiento. La frase "clases en vivo" DEBE aparecer en la respuesta. | | |
| 27 | parcial | `Hola, quiero comprar el programa de importadores conectados, ¿cómo hago?` (primer mensaje) | `directo` | Lead caliente con intención explícita de compra en el primer mensaje → agente NO hace preguntas de calificación. Va directo a `[AUDIO:CIERRE_DIRECTO]` + texto del catálogo + separador `---` + bloque del link + separador `---` + `[NOTIFICAR_CIERRE]`. | | |

---

## Flujo RE-TEST v1.6 — Flujo 13 (fallo grave: audio repetido)

**Objetivo:** validar que el agente NO repite el mismo audio en la misma conversación. En v3 el agente envió `[AUDIO:RESPUESTA_INICIAL]` dos veces: una en el turno 2 (apertura) y otra en el turno 4 (para confirmar identidad). En v1.6, si el audio ya fue usado, debe responder en texto.

**Variable:** `{{ORIGEN}} = directo`

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Hola, info del programa` | — | | |
| 2 | Agente | — | `[AUDIO:RESPUESTA_INICIAL]` + texto exacto. UNA pregunta. (Primera y única vez que se usa este audio.) | | |
| 3 | Usuario | `Pará, ¿estoy hablando con Diego o con un asistente?` | — | | |
| 4 | Agente | — | Confirma identidad como Diego en TEXTO (no con audio — `[AUDIO:RESPUESTA_INICIAL]` ya fue enviado en turno 2 y NO puede repetirse). Respuesta natural: algo como "Sí, soy yo, Diego. Perdón si la duda — el canal lo manejo yo mismo." o similar. Reencauza la conversación. | | |

---

## Notas adicionales

_Completar al finalizar el re-test._

**Validaciones específicas a v1.6:**

- ¿El agente abre con audio INCLUSO cuando el lead pregunta precio o info en el primer mensaje?
- ¿Al presentar IC, la respuesta contiene la frase "clases en vivo" (o "clases EN VIVO") de forma explícita?
- ¿Ante primer mensaje con intención explícita de compra, el agente va directo a CIERRE_DIRECTO sin preguntas?
- ¿El agente NUNCA repite el mismo marcador `[AUDIO:X]` dos veces en la misma conversación?

---

> Guía de testing v4 — re-test del prompt v1.6 sobre los fallos detectados en la testing v3.
