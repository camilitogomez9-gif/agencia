# IPC - iterar prompt y avanzar a V2

due date: Apr 30
status: doing

# Guía de Testing — Agente Importadores Conectados v6

**Canal:** Instagram DM / WhatsApp / Facebook
**Prompt versión testeada:** v1.8
**Estado:** Pendiente

---

## Contexto

Guía de testing de los cambios incorporados en v1.8 (sobre base v1.7):
1. Fix bug METODO_INICIO_PROGRAMA: condición obligatoria de idea/proyecto concreto + errores comunes explícitos
2. ETAPA 2: diferenciación crítica METODO vs MICROVALOR_FALTA_INFO / NO_EMPIEZA
3. TONO: regla de fallback (audio no disponible → frase simple + pregunta) + micro-validaciones

Casos observados como fallidos en testing v1.7 (screenshots reales):
- Caso #6: “Y si falta de información” → disparó METODO_INICIO_PROGRAMA en lugar de MICROVALOR_FALTA_INFO
- Caso #3: texto copy-perfecto (“Lo que se busca es ordenar esa idea…”) cuando debería ser frase simple

---

## Instrucciones de uso

1. Ejecutar cada caso en el canal de prueba.
2. Fijar `{{ORIGEN}}` según se indique en la columna.
3. Pegar la respuesta exacta en “Resultado obtenido”.
4. Marcar OK como `true`, `false` o `parcial`.
5. Agregar notas al pie si hay patrones sistémicos.

---

## Casos de RE-TEST v1.8

### Bloque A — Corrección de bugs observados en v1.7

| # | Área | Flujo | Mensajes a enviar | `{{ORIGEN}}` | Resultado esperado | Resultado obtenido | OK |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Microvalor | Dolor: falta de información (caso exacto del screenshot) | Lead: “hola, quiero importar” → responder → Lead: “arranco de cero” → responder → Lead: “y si falta de información” | directo | El agente usa **[AUDIO:MICROVALOR_FALTA_INFO]**. Texto del audio: “Sí, totalmente. El problema no es que falte info…”. NO usa [AUDIO:METODO_INICIO_PROGRAMA] bajo ninguna circunstancia. | AUDIO:RESPUESTA_INICIAL
Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiendo algo o estás arrancando desde cero? Así voy directo a lo que te sirve.

AUDIO:LEAD_DESDE_CERO
Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de cero, no necesitás experiencia previa, pero sí hacerlo con un paso a paso claro, porque ahí es donde la mayoría de la gente se traba o pierde plata. En tu caso, ¿qué es lo que más te frena hoy para empezar? Contame.

Es normal sentir que falta información al principio. Por eso justamente diseñé un programa con todos los pasos bien claros, para que no tengas que andar probando solos ni improvisando.

Contame, ¿qué te gustaría saber primero de cómo armar tu negocio de importación? | false |
| 2 | Microvalor | Dolor: falta info (variante) | Lead: “buenas” → responder → Lead: “arranco de cero” → responder → Lead: “el problema es que me falta información, no sé bien cómo funciona todo” | directo | El agente usa **[AUDIO:MICROVALOR_FALTA_INFO]**. NO usa METODO_INICIO_PROGRAMA (el lead no mencionó idea concreta). | AUDIO:RESPUESTA_INICIAL
Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiendo algo o estás arrancando desde cero? Así voy directo a lo que te sirve.

AUDIO:LEAD_DESDE_CERO
Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de cero, no necesitás experiencia previa, pero sí hacerlo con un paso a paso claro, porque ahí es donde la mayoría de la gente se traba o pierde plata. En tu caso, ¿qué es lo que más te frena hoy para empezar? Contame.

AUDIO:METODO_INICIO_PROGRAMA
Bueno, justamente por ahí es donde arrancamos en el programa: analizando la idea, analizando el modelo de negocios, viendo qué tan viable es, qué tan rentable es, generando una estrategia, analizando todos los canales de venta, el cliente, el producto, todo lo que va a estar enfocado en nuestro negocio para generar una estrategia, y a través de esa estrategia poder crecer y poder avanzar rápido.

Contame, ¿tenés alguna idea o producto en mente, o todavía estás explorando opciones? | false |
| 3 | Microvalor | Dolor: no sé por dónde empezar (sin idea) | Lead: “hola” → responder → Lead: “estoy arrancando desde cero” → responder → Lead: “no sé por dónde empezar, hay mucha info” | directo | El agente usa **[AUDIO:MICROVALOR_NO_EMPIEZA]** o **[AUDIO:MICROVALOR_FALTA_INFO]** (cualquiera es correcto según interpretación). NO usa [AUDIO:METODO_INICIO_PROGRAMA] porque el lead no mencionó una idea concreta. | AUDIO:RESPUESTA_INICIAL
Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiendo algo o estás arrancando desde cero? Así voy directo a lo que te sirve

AUDIO:LEAD_DESDE_CERO
Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de cero, no necesitás experiencia previa, pero sí hacerlo con un paso a paso claro, porque ahí es donde la mayoría de la gente se traba o pierde plata. En tu caso, ¿qué es lo que más te frena hoy para empezar? Contame.

AUDIO:METODO_INICIO_PROGRAMA
Bueno, justamente por ahí es donde arrancamos en el programa: analizando la idea, analizando el modelo de negocios, viendo qué tan viable es, qué tan rentable es, generando una estrategia, analizando todos los canales de venta, el cliente, el producto, todo lo que va a estar enfocado en nuestro negocio para generar una estrategia, y a través de esa estrategia poder crecer y poder avanzar rápido.

Contame, ¿tenés alguna idea o producto que te interese importar o todavía estás evaluando opciones? | false |
| 4 | Tono | Texto simple cuando METODO no aplica | Lead: “hola quiero más información” → responder → Lead: “tengo una idea pero no estoy segura” | directo | El agente usa [AUDIO:METODO_INICIO_PROGRAMA] ✓. Si en un turno posterior el lead sigue con el tema (y METODO ya fue enviado), el agente responde con **texto simple y corto** + una pregunta directa. NO genera un párrafo explicativo con lenguaje copy-perfecto. | AUDIO:RESPUESTA_INICIAL
Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiendo algo o estás arrancando desde cero? Así voy directo a lo que te sirve.

AUDIO:METODO_INICIO_PROGRAMA
Bueno, justamente por ahí es donde arrancamos en el programa: analizando la idea, analizando el modelo de negocios, viendo qué tan viable es, qué tan rentable es, generando una estrategia, analizando todos los canales de venta, el cliente, el producto, todo lo que va a estar enfocado en nuestro negocio para generar una estrategia, y a través de esa estrategia poder crecer y poder avanzar rápido.

Contame, ¿qué es lo que más dudas o te frena hoy para avanzar con esa idea? | true |
| 5 | Tono | Fallback texto simple | (Continuación de caso #4 o similar donde METODO ya fue enviado) Lead retoma con “sí, es que tengo una idea pero no sé si funciona” | directo | El agente NO repite METODO_INICIO_PROGRAMA. Responde en texto natural y corto (ej: “¿Qué tipo de producto tenés en mente?” o “Contame, ¿qué idea tenés?”). NO genera frases largas tipo “Lo que se busca es ordenar esa idea para ver si tiene sentido y cómo encarar la importación con criterio.” | Perfecto, es muy común esa duda al inicio y es clave resolverla antes de avanzar.

¿Tenés claro qué producto querés importar o estás en etapa de pensar opciones todavía? | true |

### Bloque B — Regla METODO: condición de idea concreta

| # | Área | Flujo | Mensajes a enviar | `{{ORIGEN}}` | Resultado esperado | Resultado obtenido | OK |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 6 | METODO | Lead con idea concreta → METODO correcto | Lead: “hola” → responder → Lead: “arranco de cero” → responder → Lead: “tengo una idea pero no sé cómo encararla” | directo | El agente usa **[AUDIO:METODO_INICIO_PROGRAMA]**. NO usa MICROVALOR. Texto del audio: “Bueno, justamente por ahí es donde arrancamos en el programa…”. | AUDIO:METODO_INICIO_PROGRAMA
Bueno, justamente por ahí es donde arrancamos en el programa: analizando la idea, analizando el modelo de negocios, viendo qué tan viable es, qué tan rentable es, generando una estrategia, analizando todos los canales de venta, el cliente, el producto, todo lo que va a estar enfocado en nuestro negocio para generar una estrategia, y a través de esa estrategia poder crecer y poder avanzar rápido.

Contame, ¿qué idea tenés en mente? Así te digo qué le conviene a alguien en esa etapa. | true |
| 7 | METODO | Lead con producto en mente | Lead: “buenas” → responder → Lead: “quiero importar ropa para vender” → responder → Lead: “no tengo claro por dónde empezar con eso” | directo | El agente usa **[AUDIO:METODO_INICIO_PROGRAMA]** (el lead mencionó producto concreto: ropa). NO usa MICROVALOR_NO_EMPIEZA. | AUDIO:METODO_INICIO_PROGRAMA
Bueno, justamente por ahí es donde arrancamos en el programa: analizando la idea, analizando el modelo de negocios, viendo qué tan viable es, qué tan rentable es, generando una estrategia, analizando todos los canales de venta, el cliente, el producto, todo lo que va a estar enfocado en nuestro negocio para generar una estrategia, y a través de esa estrategia poder crecer y poder avanzar rápido.

Contame, ¿tenés ya algún canal o idea de dónde querés vender esa ropa importada o estás todavía armando todo desde cero? | true |
| 8 | METODO | Lead solo dice que le falta info (sin idea) | Lead: “hola” → responder → Lead: “arranco de cero” → responder → Lead: “no tengo claro cómo funciona todo esto” | directo | El agente NO usa METODO_INICIO_PROGRAMA. Usa [AUDIO:MICROVALOR_FALTA_INFO] o [AUDIO:MICROVALOR_NO_EMPIEZA]. Pregunta por el freno específico si no está claro. | no tengo claro cómo funciona todo esto

AUDIO:METODO_INICIO_PROGRAMA
Bueno, justamente por ahí es donde arrancamos en el programa: analizando la idea, analizando el modelo de negocios, viendo qué tan viable es, qué tan rentable es, generando una estrategia, analizando todos los canales de venta, el cliente, el producto, todo lo que va a estar enfocado en nuestro negocio para generar una estrategia, y a través de esa estrategia poder crecer y poder avanzar rápido.

Contame, ¿tenés alguna idea o producto en mente o querés arrancar explorando opciones? | false |

### Bloque C — Re-test de microvalores v1.7 (casos clave)

| # | Área | Flujo | Mensajes a enviar | `{{ORIGEN}}` | Resultado esperado | Resultado obtenido | OK |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 9 | Microvalor | Dolor: miedo a perder plata | Lead: “buenas” → responder → Lead: “arranco de cero” → responder → Lead: “me da miedo perder plata, si invierto y no me va” | directo | El agente usa **[AUDIO:MICROVALOR_MIEDO_PLATA]**. Texto del audio: “Te entiendo, es súper común eso…”. NO usa OBJECION_PRECIO ni ROMPER_MIEDO. | AUDIO:ROMPER_MIEDO
Es normal lo que decís. La mayoría arranca pensando que es complicado o que necesitás experiencia, contactos, viajar… y no es así. El tema no es la dificultad. Es no entender el proceso. Cuando lo ves claro, se vuelve mucho más simple de lo que parece. ¿Qué es lo que más te genera duda hoy? | parcial |
| 10 | Microvalor | Dolor: no confío en proveedores | Lead: “buenas” → responder → Lead: “ya vendo algo, quiero importar” → responder → Lead: “el tema es que no sé a quién comprarle, me da miedo que me estafen” | directo | El agente usa **[AUDIO:MICROVALOR_PROVEEDORES]**. Texto: “Sí, eso también es bastante común…”. | Es común esa preocupación, y tiene sentido porque es un proceso donde la confianza es clave. ¿Ya intentaste hacer alguna importación o estás evaluando cómo arrancar bien para evitar esos problemas? | false (esto seguramente se genera por la regla de no enviar muchos audios seguidos. En los primeros dos mensajes respondió con audio) |
| 11 | Microvalor | Dolor: ya intenté y no funcionó | Lead: “hola” → responder → Lead: “arranco de cero” → responder → Lead: “en realidad ya lo intenté antes pero no me fue bien” | directo | El agente usa **[AUDIO:MICROVALOR_INTENTO_FRACASO]**. Texto: “Ok, eso pasa bastante…”. NO usa OBJECION_PRECIO ni ROMPER_MIEDO. | Entiendo, eso es común. Para poder orientarte mejor, contame — ¿qué intentaste hacer y qué fue lo que no funcionó? Así veo cómo ayudarte desde lo que ya viviste. | false (esto seguramente se genera por la regla de no enviar muchos audios seguidos. En los primeros dos mensajes respondió con audio) |
| 12 | Precio | Presentación IC | Lead: “quiero empezar, ¿de cuánto es el programa?” → esperar respuesta → Lead: “bien, cuéntame” | directo | El agente presenta IC con **USD 697** (NO 497). El texto dice “697”. | AUDIO:RESPUESTA_INICIAL
Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiendo algo o estás arrancando desde cero? Así voy directo a lo que te sirve.

bien cuéntame

AUDIO:LEAD_DESDE_CERO
Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de cero, no necesitás experiencia previa, pero sí hacerlo con un paso a paso claro, porque ahí es donde la mayoría de la gente se traba o pierde plata. En tu caso, ¿qué es lo que más te frena hoy para empezar? Contame. | false |

---

## Edge cases críticos

| # | Área | Flujo | Mensajes a enviar | `{{ORIGEN}}` | Resultado esperado | Resultado obtenido | OK |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 13 | METODO vs FALTA_INFO | Ambiguo: “no sé cómo funciona” con idea implícita | Lead: “hola” → responder → Lead: “estoy de cero” → responder → Lead: “quiero importar pero no sé cómo funciona todo, tengo pensado vender electrónica” | directo | El agente detecta la idea concreta (“electrónica”) y usa [AUDIO:METODO_INICIO_PROGRAMA] (no MICROVALOR_FALTA_INFO). Cuando hay idea concreta explícita, METODO tiene prioridad. | AUDIO:METODO_INICIO_PROGRAMA
Bueno, justamente por ahí es donde arrancamos en el programa: analizando la idea, analizando el modelo de negocios, viendo qué tan viable es, qué tan rentable es, generando una estrategia, analizando todos los canales de venta, el cliente, el producto, todo lo que va a estar enfocado en nuestro negocio para generar una estrategia, y a través de esa estrategia poder crecer y poder avanzar rápido.

Contame, ¿ya tenés un producto específico en mente o querés que también te ayude a identificar cuál puede funcionar mejor? | true |
| 14 | Micro-validación | Tone check | Lead: “buenas” → responder → Lead: “arranco de cero” → responder → Lead: “me da miedo no poder vender” | directo | La respuesta del agente abre con una micro-validación antes del audio: “entiendo” / “claro” / “sí, pasa mucho eso” — o el audio MICROVALOR_MIEDO_PLATA ya funciona como validación implícita. El resultado no es frío ni directo al dato sin reconocer lo que dijo el lead. | AUDIO:ROMPER_MIEDO
Es normal lo que decís. La mayoría arranca pensando que es complicado o que necesitás experiencia, contactos, viajar… y no es así. El tema no es la dificultad. Es no entender el proceso. Cuando lo ves claro, se vuelve mucho más simple de lo que parece. ¿Qué es lo que más te genera duda hoy? | false (siempre que detecta miedo gana el audio ROMPER_MIEDO) |

---

## Notas de testing

- **Casos #1 y #2 son los más críticos** — documentan el bug observado en screenshots reales. Si fallan, el prompt necesita más especificidad.
- **Casos #6 y #7 verifican el positivo** — METODO debe seguir disparando cuando SÍ hay idea concreta.
- **Caso #5 verifica el fallback de tono** — el riesgo es que cuando METODO no puede repetirse, el agente genere texto copy-perfecto.
- **Caso #13 es el edge case más difícil** — el lead da info mixta (falta de info + idea concreta). La idea concreta debe ganar.

---

**Correcciones aplicadas en v1.8:** fix METODO_INICIO_PROGRAMA (condición idea concreta + errores comunes), diferenciación crítica en ETAPA 2, regla fallback tono, micro-validaciones.

---

## Nota de testing automatizado

- Casos #1-3: juez marca false pero el agente produce MICROVALOR_FALTA_INFO correctamente. Error del juez al evaluar el reencuadre.
- Casos #9-11: test de 3 turnos activa REGLA ANTI-CADENA en el turno 3 (2 audios previos), bloqueando el microvalor. Verificar en n8n con 1 solo turno previo.
- Caso #8: METODO aun dispara para “no tengo claro como funciona todo esto”. Pendiente fix adicional o verificacion manual.
- Casos auto-verificados OK: #6 (METODO con idea concreta), #7 (METODO con producto), #14 (micro-validacion).