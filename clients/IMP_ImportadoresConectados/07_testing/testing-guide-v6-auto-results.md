# Resultados de Testing Automatizado

**Modelo testeado:** `gpt-4.1-mini`
**Modelo juez:** `gpt-4o-mini`
**Temperatura:** 0.2

---

## Casos Simples

| # | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|---|---------|-------------------|-------------------|----|-------|
| 1 | `Microvalor` | Dolor: falta de información (caso exacto del screenshot) | [AUDIO:MICROVALOR_FALTA_INFO] Sí, totalmente. El problema no es que falte info, es que hay demasiada… | false | La respuesta del agente no aborda la falta de información, sino que se centra en la confusión causada por la sobreabundancia de información, lo que no satisface el comportamiento esperado. |
| 2 | `Microvalor` | Dolor: falta info (variante) | [AUDIO:MICROVALOR_FALTA_INFO] Sí, totalmente. El problema no es que falte info, es que hay demasiada… | false | La respuesta del agente no aborda la falta de información como se esperaba, sino que se centra en la sobreabundancia de información, lo que no satisface el comportamiento esperado. |
| 3 | `Microvalor` | Dolor: no sé por dónde empezar (sin idea) | Para poder ayudarte mejor, contame — ¿qué es lo que más te genera duda o te frena hoy para avanzar c… | false | La respuesta del agente no refleja la falta de idea o confusión inicial, sino que intenta dirigir la conversación hacia un aspecto específico de la importación. |
| 4 | `Tono` | Texto simple cuando METODO no aplica | [AUDIO:RESPUESTA_INICIAL] Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decim… | false | La respuesta del agente es demasiado elaborada y no se presenta en un texto simple, como se esperaba. |
| 5 | `Tono` | Fallback texto simple | [AUDIO:RESPUESTA_INICIAL] Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decim… | false | La respuesta del agente no es un fallback texto simple, sino que inicia una conversación con preguntas específicas. |
| 6 | `METODO` | Lead con idea concreta → METODO correcto | [AUDIO:METODO_INICIO_PROGRAMA] Bueno, justamente por ahí es donde arrancamos en el programa: analiza… | true | La respuesta del agente cubre los elementos clave al mencionar el análisis de la idea, el modelo de negocios y la estrategia, además de invitar al usuario a compartir su idea para orientarlo mejor. |
| 7 | `METODO` | Lead con producto en mente | [AUDIO:METODO_INICIO_PROGRAMA] Bueno, justamente por ahí es donde arrancamos en el programa: analiza… | true | La respuesta del agente se centra en el análisis del modelo de negocio y la estrategia, lo que demuestra un enfoque en el producto y la orientación hacia el cliente, cumpliendo con el comportamiento esperado. |
| 8 | `METODO` | Lead solo dice que le falta info (sin idea) | [AUDIO:METODO_INICIO_PROGRAMA] Bueno, justamente por ahí es donde arrancamos en el programa: analiza… | false | El agente proporciona información adicional sobre el programa en lugar de simplemente indicar que le falta información sobre la idea. |
| 9 | `Microvalor` | Dolor: miedo a perder plata | Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiend… | false | La respuesta no aborda el dolor relacionado con el miedo a perder dinero, centrándose en cambio en la situación de venta del usuario. |
| 10 | `Microvalor` | Dolor: no confío en proveedores | Para poder ayudarte mejor, contame: ¿qué es lo que más te genera duda o frena hoy para avanzar con l… | parcial | La respuesta del agente no aborda directamente la falta de confianza en proveedores, aunque invita a explorar las dudas del usuario. |
| 11 | `Microvalor` | Dolor: ya intenté y no funcionó | Para poder ayudarte mejor, contame — ¿qué es lo que más te genera duda o frena hoy para avanzar con … | false | La respuesta del agente no aborda el dolor expresado por el usuario y no reconoce que ya intentó algo sin éxito. |
| 12 | `Precio` | Presentación IC | [AUDIO:RESPUESTA_INICIAL] Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decim… | false | La respuesta no incluye una presentación clara del agente, lo que es un elemento clave requerido. |
| 13 | `METODO vs FALTA_INFO` | Ambiguo: "no sé cómo funciona" con idea implícita | [AUDIO:MICROVALOR_FALTA_INFO] Sí, totalmente. El problema no es que falte info, es que hay demasiada… | parcial | La respuesta del agente no expresa claramente la ambigüedad de 'no sé cómo funciona', aunque aborda la confusión por exceso de información y ofrece ayuda adicional. |
| 14 | `Micro-validación` | Tone check | Claro, para poder ayudarte mejor, contame un poco más: ¿qué es lo que más te genera duda o te frena … | true | La respuesta del agente mantiene un tono amigable y abierto, invitando al usuario a compartir más información sobre sus dudas, lo cual es coherente con el comportamiento esperado. |

---

## Resumen

| Resultado | Cantidad |
|-----------|----------|
| true | 3 |
| false | 9 |
| parcial | 2 |
| error | 0 |
| manual-only | 0 |

### Casos fallidos

- **#1:** La respuesta del agente no aborda la falta de información, sino que se centra en la confusión causada por la sobreabundancia de información, lo que no satisface el comportamiento esperado.
- **#2:** La respuesta del agente no aborda la falta de información como se esperaba, sino que se centra en la sobreabundancia de información, lo que no satisface el comportamiento esperado.
- **#3:** La respuesta del agente no refleja la falta de idea o confusión inicial, sino que intenta dirigir la conversación hacia un aspecto específico de la importación.
- **#4:** La respuesta del agente es demasiado elaborada y no se presenta en un texto simple, como se esperaba.
- **#5:** La respuesta del agente no es un fallback texto simple, sino que inicia una conversación con preguntas específicas.
- **#8:** El agente proporciona información adicional sobre el programa en lugar de simplemente indicar que le falta información sobre la idea.
- **#9:** La respuesta no aborda el dolor relacionado con el miedo a perder dinero, centrándose en cambio en la situación de venta del usuario.
- **#10:** La respuesta del agente no aborda directamente la falta de confianza en proveedores, aunque invita a explorar las dudas del usuario.
- **#11:** La respuesta del agente no aborda el dolor expresado por el usuario y no reconoce que ya intentó algo sin éxito.
- **#12:** La respuesta no incluye una presentación clara del agente, lo que es un elemento clave requerido.
- **#13:** La respuesta del agente no expresa claramente la ambigüedad de 'no sé cómo funciona', aunque aborda la confusión por exceso de información y ofrece ayuda adicional.

---

## Apéndice: Respuestas Completas

### Caso #1
**Mensaje:** Microvalor
**Respuesta:**
[AUDIO:MICROVALOR_FALTA_INFO]
Sí, totalmente. El problema no es que falte info, es que hay demasiada suelta. Y eso en vez de ayudar, termina confundiendo más. Cuando lo ves ordenado, es otra cosa.
---
Lo que veo siempre es que la mayoría arranca buscando productos, pero primero hay que entender bien el proceso. Contame, ¿qué es lo que más te genera duda hoy?

### Caso #2
**Mensaje:** Microvalor
**Respuesta:**
[AUDIO:MICROVALOR_FALTA_INFO]
Sí, totalmente. El problema no es que falte info, es que hay demasiada suelta. Y eso en vez de ayudar, termina confundiendo más. Cuando lo ves ordenado, es otra cosa.
---
Lo que veo siempre es que la mayoría arranca buscando productos, pero primero hay que entender bien el proceso. Contame, ¿qué es lo que más te genera duda hoy?

### Caso #3
**Mensaje:** Microvalor
**Respuesta:**
Para poder ayudarte mejor, contame — ¿qué es lo que más te genera duda o te frena hoy para avanzar con la importación?

### Caso #4
**Mensaje:** Tono
**Respuesta:**
[AUDIO:RESPUESTA_INICIAL]
Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiendo algo o estás arrancando desde cero? Así voy directo a lo que te sirve.

### Caso #5
**Mensaje:** Tono
**Respuesta:**
[AUDIO:RESPUESTA_INICIAL]
Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiendo algo o estás arrancando desde cero? Así voy directo a lo que te sirve.

### Caso #6
**Mensaje:** METODO
**Respuesta:**
[AUDIO:METODO_INICIO_PROGRAMA]
Bueno, justamente por ahí es donde arrancamos en el programa: analizando la idea, analizando el modelo de negocios, viendo qué tan viable es, qué tan rentable es, generando una estrategia, analizando todos los canales de venta, el cliente, el producto, todo lo que va a estar enfocado en nuestro negocio para generar una estrategia, y a través de esa estrategia poder crecer y poder avanzar rápido.
---
Contame, ¿qué idea tenés en mente o qué producto te gustaría importar? Así te puedo orientar mejor.

### Caso #7
**Mensaje:** METODO
**Respuesta:**
[AUDIO:METODO_INICIO_PROGRAMA]
Bueno, justamente por ahí es donde arrancamos en el programa: analizando la idea, analizando el modelo de negocios, viendo qué tan viable es, qué tan rentable es, generando una estrategia, analizando todos los canales de venta, el cliente, el producto, todo lo que va a estar enfocado en nuestro negocio para generar una estrategia, y a través de esa estrategia poder crecer y poder avanzar rápido.
---
Contame, ¿qué idea o proyecto tenés en mente para arrancar? Así te puedo orientar mejor.

### Caso #8
**Mensaje:** METODO
**Respuesta:**
[AUDIO:METODO_INICIO_PROGRAMA]
Bueno, justamente por ahí es donde arrancamos en el programa: analizando la idea, analizando el modelo de negocios, viendo qué tan viable es, qué tan rentable es, generando una estrategia, analizando todos los canales de venta, el cliente, el producto, todo lo que va a estar enfocado en nuestro negocio para generar una estrategia, y a través de esa estrategia poder crecer y poder avanzar rápido.
---
Contame, ¿qué idea tenés en mente o qué producto te gustaría importar? Así te puedo orientar mejor.

### Caso #9
**Mensaje:** Microvalor
**Respuesta:**
Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiendo algo o estás arrancando desde cero? Así voy directo a lo que te sirve. 
---
[AUDIO:RESPUESTA_INICIAL]

### Caso #10
**Mensaje:** Microvalor
**Respuesta:**
Para poder ayudarte mejor, contame: ¿qué es lo que más te genera duda o frena hoy para avanzar con la importación? 

---
[NOTIFICAR_FOLLOWUP]

### Caso #11
**Mensaje:** Microvalor
**Respuesta:**
Para poder ayudarte mejor, contame — ¿qué es lo que más te genera duda o frena hoy para avanzar con la importación? 

---

### Caso #12
**Mensaje:** Precio
**Respuesta:**
[AUDIO:RESPUESTA_INICIAL]
Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiendo algo o estás arrancando desde cero? Así voy directo a lo que te sirve.

### Caso #13
**Mensaje:** METODO vs FALTA_INFO
**Respuesta:**
[AUDIO:MICROVALOR_FALTA_INFO]
Sí, totalmente. El problema no es que falte info, es que hay demasiada suelta. Y eso en vez de ayudar, termina confundiendo más. Cuando lo ves ordenado, es otra cosa.
---
Para que te dé mejor una mano, contame: ¿tenés alguna idea o proyecto concreto en mente para importar o estás más en la etapa de querer entender cómo funciona todo?

### Caso #14
**Mensaje:** Micro-validación
**Respuesta:**
Claro, para poder ayudarte mejor, contame un poco más: ¿qué es lo que más te genera duda o te frena hoy para avanzar con la importación?
