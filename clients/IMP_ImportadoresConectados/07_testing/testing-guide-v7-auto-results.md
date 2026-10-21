# Resultados de Testing Automatizado

**Modelo testeado:** `gpt-4.1-mini`
**Modelo juez:** `gpt-4o-mini`
**Temperatura:** 0.2

---

## Caso 1 — "no tengo claro cómo funciona todo esto"

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `hola` | — |  |  |  |
| 2 | Agente | `—` | — | [AUDIO:RESPUESTA_INICIAL] Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decim… | true | Sin criterio de evaluación especificado. |
| 3 | Usuario | `arranco de cero` | — |  |  |  |
| 4 | Agente | `—` | — | [AUDIO:LEAD_DESDE_CERO] Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de… | true | Sin criterio de evaluación especificado. |
| 5 | Usuario | `no tengo claro cómo funciona todo esto` | — |  |  |  |
| 6 | Agente | `—` | Usa [AUDIO:MICROVALOR_FALTA_INFO] o [AUDIO:MICROVALOR_NO_EMPIEZA]. NO usa [AUDIO… | [AUDIO:MICROVALOR_FALTA_INFO] Sí, totalmente. El problema no es que falte info, es que hay demasiada… | true | La respuesta del agente utiliza el audio correcto y hace una pregunta de diagnóstico adecuada, cumpliendo con el comportamiento esperado. |

## Caso 2 — "me falta información, no sé bien cómo funciona todo"

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `buenas` | — |  |  |  |
| 2 | Agente | `—` | — | [AUDIO:RESPUESTA_INICIAL] Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decim… | true | Sin criterio de evaluación especificado. |
| 3 | Usuario | `arranco de cero` | — |  |  |  |
| 4 | Agente | `—` | — | [AUDIO:LEAD_DESDE_CERO] Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de… | true | Sin criterio de evaluación especificado. |
| 5 | Usuario | `el problema es que me falta información, no sé bien cómo fun…` | — |  |  |  |
| 6 | Agente | `—` | Usa [AUDIO:MICROVALOR_FALTA_INFO]. NO usa [AUDIO:METODO_INICIO_PROGRAMA]. El lea… | [AUDIO:MICROVALOR_FALTA_INFO] Sí, totalmente. El problema no es que falte info, es que hay demasiada… | true | La respuesta del agente utiliza el audio correcto y hace una pregunta de diagnóstico adecuada, cumpliendo con el comportamiento esperado. |

## Caso 3 — "no sé por dónde empezar, hay mucha info"

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `hola` | — |  |  |  |
| 2 | Agente | `—` | — | [AUDIO:RESPUESTA_INICIAL] Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decim… | true | Sin criterio de evaluación especificado. |
| 3 | Usuario | `estoy arrancando desde cero` | — |  |  |  |
| 4 | Agente | `—` | — | [AUDIO:LEAD_DESDE_CERO] Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de… | true | Sin criterio de evaluación especificado. |
| 5 | Usuario | `no sé por dónde empezar, hay mucha info` | — |  |  |  |
| 6 | Agente | `—` | Usa [AUDIO:MICROVALOR_NO_EMPIEZA] o [AUDIO:MICROVALOR_FALTA_INFO]. NO usa [AUDIO… | [AUDIO:MICROVALOR_NO_EMPIEZA] Bien, ahí está el punto. No es que no puedas, es que no está claro el … | true | La respuesta real del agente utiliza el audio esperado y mantiene un tono alineado con la intención de ayudar al usuario. |

## Caso 4 — "no sé cómo funciona todo" (variante edge, sin idea)

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `hola` | — |  |  |  |
| 2 | Agente | `—` | — | [AUDIO:RESPUESTA_INICIAL] Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decim… | true | Sin criterio de evaluación especificado. |
| 3 | Usuario | `de cero` | — |  |  |  |
| 4 | Agente | `—` | — | [AUDIO:LEAD_DESDE_CERO] Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de… | true | Sin criterio de evaluación especificado. |
| 5 | Usuario | `no sé cómo funciona todo esto del tema de importaciones` | — |  |  |  |
| 6 | Agente | `—` | Usa [AUDIO:MICROVALOR_FALTA_INFO] o [AUDIO:MICROVALOR_NO_EMPIEZA]. NO usa [AUDIO… | [AUDIO:MICROVALOR_FALTA_INFO] Sí, totalmente. El problema no es que falte info, es que hay demasiada… | true | La respuesta del agente utiliza el audio correcto y hace preguntas de diagnóstico, cumpliendo con el comportamiento esperado. |

## Caso 5 — "me da miedo perder plata"

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `buenas` | — |  |  |  |
| 2 | Agente | `—` | — | [AUDIO:RESPUESTA_INICIAL] Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decim… | true | Sin criterio de evaluación especificado. |
| 3 | Usuario | `arranco de cero` | — |  |  |  |
| 4 | Agente | `—` | — | [AUDIO:LEAD_DESDE_CERO] Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de… | true | Sin criterio de evaluación especificado. |
| 5 | Usuario | `me da miedo perder plata, si invierto y no me va` | — |  |  |  |
| 6 | Agente | `—` | Usa [AUDIO:MICROVALOR_MIEDO_PLATA]. El texto incluye algo como "Te entiendo, es … | [AUDIO:MICROVALOR_MIEDO_PLATA] Te entiendo, es súper común eso. Sobre todo cuando no tenés claro cóm… | true | La respuesta del agente incluye el audio esperado, expresa empatía y aborda el miedo al proceso de importar sin romper el miedo, cumpliendo con el comportamiento esperado. |

## Caso 6 — "me da miedo no poder vender"

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `buenas` | — |  |  |  |
| 2 | Agente | `—` | — | [AUDIO:RESPUESTA_INICIAL] Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decim… | true | Sin criterio de evaluación especificado. |
| 3 | Usuario | `arranco de cero` | — |  |  |  |
| 4 | Agente | `—` | — | [AUDIO:LEAD_DESDE_CERO] Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de… | true | Sin criterio de evaluación especificado. |
| 5 | Usuario | `me da miedo no poder vender` | — |  |  |  |
| 6 | Agente | `—` | Usa [AUDIO:MICROVALOR_MIEDO_PLATA]. NO usa ROMPER_MIEDO. "No poder vender" es mi… | [AUDIO:MICROVALOR_MIEDO_PLATA] Te entiendo, es súper común eso. Sobre todo cuando no tenés claro cóm… | true | La respuesta del agente utiliza el audio correcto y aborda el miedo al resultado económico, explicando que la mayoría de los errores provienen de no entender el proceso, lo cual es coherente con el comportamiento esperado. |

## Caso 7 — miedo al PROCESO de importar (debe usar ROMPER_MIEDO)

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `hola` | — |  |  |  |
| 2 | Agente | `—` | — | [AUDIO:RESPUESTA_INICIAL] Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decim… | true | Sin criterio de evaluación especificado. |
| 3 | Usuario | `arranco de cero` | — |  |  |  |
| 4 | Agente | `—` | — | [AUDIO:LEAD_DESDE_CERO] Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de… | true | Sin criterio de evaluación especificado. |
| 5 | Usuario | `me parece muy complicado eso de importar, no tengo experienc…` | — |  |  |  |
| 6 | Agente | `—` | Usa [AUDIO:ROMPER_MIEDO]. NO usa MICROVALOR_MIEDO_PLATA. "Muy complicado" + "no … | [AUDIO:ROMPER_MIEDO] Es normal lo que decís. La mayoría arranca pensando que es complicado o que nec… | true | La respuesta del agente utiliza el audio adecuado, aborda la creencia sobre el proceso de importar y mantiene un tono alentador, cumpliendo con el comportamiento esperado. |

## Caso 8 — "¿y si no vendo?"

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `buenas` | — |  |  |  |
| 2 | Agente | `—` | — | [AUDIO:RESPUESTA_INICIAL] Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decim… | true | Sin criterio de evaluación especificado. |
| 3 | Usuario | `quiero empezar algo propio` | — |  |  |  |
| 4 | Agente | `—` | — | Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de cero, no necesitás expe… | true | Sin criterio de evaluación especificado. |
| 5 | Usuario | `¿y si no vendo nada?` | — |  |  |  |
| 6 | Agente | `—` | Usa [AUDIO:MICROVALOR_MIEDO_PLATA]. Es miedo al resultado de negocio. NO usa ROM… | [AUDIO:MICROVALOR_MIEDO_PLATA] Te entiendo, es súper común eso. Sobre todo cuando no tenés claro cóm… | true | La respuesta real del agente utiliza el audio correcto y aborda el miedo al resultado de negocio, además de ofrecer una perspectiva positiva sobre el proceso. |

## Caso 9 — microvalor en turno 3 (miedo a perder plata, excepción anti-cadena)

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `buenas` | — |  |  |  |
| 2 | Agente | `—` | — | [AUDIO:RESPUESTA_INICIAL] Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decim… | true | Sin criterio de evaluación especificado. |
| 3 | Usuario | `arranco de cero` | — |  |  |  |
| 4 | Agente | `—` | — | [AUDIO:LEAD_DESDE_CERO] Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de… | true | Sin criterio de evaluación especificado. |
| 5 | Usuario | `me da miedo perder plata, si invierto y no me va` | — |  |  |  |
| 6 | Agente | `—` | Usa [AUDIO:MICROVALOR_MIEDO_PLATA] aunque sea el 3er audio en la secuencia. La e… | [AUDIO:MICROVALOR_MIEDO_PLATA] Te entiendo, es súper común eso. Sobre todo cuando no tenés claro cóm… | true | La respuesta del agente utiliza el audio esperado y aborda el dolor específico del lead, además de mantener un tono empático y alineado con la intención de ayudar. |

## Caso 10 — microvalor proveedores en turno 3 (excepción anti-cadena)

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `buenas` | — |  |  |  |
| 2 | Agente | `—` | — | [AUDIO:RESPUESTA_INICIAL] Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decim… | true | Sin criterio de evaluación especificado. |
| 3 | Usuario | `ya vendo algo, quiero importar` | — |  |  |  |
| 4 | Agente | `—` | — | [AUDIO:LEAD_CON_NEGOCIO] Bien, ahí en ese caso tiene mucho sentido lo que estás viendo. Lo que pasa … | true | Sin criterio de evaluación especificado. |
| 5 | Usuario | `el tema es que no sé a quién comprarle, me da miedo que me e…` | — |  |  |  |
| 6 | Agente | `—` | Usa [AUDIO:MICROVALOR_PROVEEDORES] aunque haya 2 audios previos (RESPUESTA_INICI… | [AUDIO:MICROVALOR_PROVEEDORES] Sí, eso también es bastante común. Porque desde afuera no sabés en qu… | true | La respuesta del agente utiliza el audio esperado y aborda la desconfianza en proveedores, además de ofrecer un enfoque constructivo sobre el proceso de selección. |

## Caso 11 — microvalor intento fracaso en turno 3 (excepción anti-cadena)

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `hola` | — |  |  |  |
| 2 | Agente | `—` | — | [AUDIO:RESPUESTA_INICIAL] Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decim… | true | Sin criterio de evaluación especificado. |
| 3 | Usuario | `arranco de cero` | — |  |  |  |
| 4 | Agente | `—` | — | [AUDIO:LEAD_DESDE_CERO] Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de… | true | Sin criterio de evaluación especificado. |
| 5 | Usuario | `en realidad ya lo intenté antes pero no me fue bien` | — |  |  |  |
| 6 | Agente | `—` | Usa [AUDIO:MICROVALOR_INTENTO_FRACASO] aunque haya 2 audios previos. La excepció… | [AUDIO:MICROVALOR_INTENTO_FRACASO] Ok, eso pasa bastante. Muchas veces no es el producto, sino cómo … | true | La respuesta del agente utiliza el audio esperado y aborda el tema del intento fallido, además de mantener un tono empático y ofrecer una continuación de la conversación. |

## Caso 12 — "quiero empezar + ¿cuánto cuesta?" → "cuéntame"

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `quiero empezar, ¿de cuánto es el programa?` | — |  |  |  |
| 2 | Agente | `—` | Abre con [AUDIO:RESPUESTA_INICIAL]. | [AUDIO:RESPUESTA_INICIAL] Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decim… | true | La respuesta real del agente abre con el audio esperado y continúa con un saludo y una pregunta relevante, manteniendo un tono amigable y útil. |
| 3 | Usuario | `bien, cuéntame` | — |  |  |  |
| 4 | Agente | `—` | Presenta IC con precio USD 697 + los 4 pilares (clases grabadas, módulos, EN VIV… | Importadores Conectados cuesta USD 697. Tiene clases grabadas con acceso ilimitado, módulos de impor… | true | La respuesta del agente presenta correctamente el precio y los 4 pilares del programa, además de mantener el interés del lead sin reiniciar el diagnóstico. |

## Caso 13 — "¿cuánto vale?" → "dale, contame"

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `hola, ¿cuánto vale el programa de importaciones?` | — |  |  |  |
| 2 | Agente | `—` | Abre con [AUDIO:RESPUESTA_INICIAL]. | [AUDIO:RESPUESTA_INICIAL] Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decim… | true | La respuesta real del agente abre con el audio esperado y continúa con un saludo amigable y una pregunta relevante, cumpliendo con el comportamiento esperado. |
| 3 | Usuario | `dale, contame` | — |  |  |  |
| 4 | Agente | `—` | Presenta IC con precio USD 697 + los 4 pilares del programa (clases grabadas, mó… | Importadores Conectados cuesta USD 697.  Tiene clases grabadas con acceso ilimitado, módulos de impo… | true | La respuesta del agente incluye el precio y todos los pilares del programa, cumpliendo con el comportamiento esperado. |

## Caso 14 — lead con idea concreta sigue usando METODO

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `hola` | — |  |  |  |
| 2 | Agente | `—` | — | [AUDIO:RESPUESTA_INICIAL] Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decim… | true | Sin criterio de evaluación especificado. |
| 3 | Usuario | `arranco de cero` | — |  |  |  |
| 4 | Agente | `—` | — | [AUDIO:LEAD_DESDE_CERO] Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de… | true | Sin criterio de evaluación especificado. |
| 5 | Usuario | `tengo una idea pero no sé cómo encararla` | — |  |  |  |
| 6 | Agente | `—` | Usa [AUDIO:METODO_INICIO_PROGRAMA]. "Una idea" mencionada explícitamente → condi… | [AUDIO:METODO_INICIO_PROGRAMA] Bueno, justamente por ahí es donde arrancamos en el programa: analiza… | true | La respuesta del agente menciona explícitamente la idea y se alinea con el comportamiento esperado al iniciar el programa y preguntar sobre la idea del usuario. |

## Caso 15 — lead con producto concreto sigue usando METODO

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `buenas` | — |  |  |  |
| 2 | Agente | `—` | — | [AUDIO:RESPUESTA_INICIAL] Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decim… | true | Sin criterio de evaluación especificado. |
| 3 | Usuario | `quiero importar ropa para vender` | — |  |  |  |
| 4 | Agente | `—` | — | [AUDIO:METODO_INICIO_PROGRAMA] Bueno, justamente por ahí es donde arrancamos en el programa: analiza… | true | Sin criterio de evaluación especificado. |
| 5 | Usuario | `no tengo claro por dónde empezar con eso` | — |  |  |  |
| 6 | Agente | `—` | NO usa [AUDIO:MICROVALOR_NO_EMPIEZA] ni MICROVALOR_FALTA_INFO. El lead ya declar… | Bien, ahí está el punto. No es que no puedas, es que no está claro el camino. Y cuando no tenés un p… | true | La respuesta del agente avanza en el diagnóstico al preguntar sobre el capital, cumpliendo con el comportamiento esperado y evitando los comportamientos prohibidos. |

## Caso 16 — info + idea concreta → METODO gana

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `hola` | — |  |  |  |
| 2 | Agente | `—` | — | [AUDIO:RESPUESTA_INICIAL] Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decim… | true | Sin criterio de evaluación especificado. |
| 3 | Usuario | `de cero` | — |  |  |  |
| 4 | Agente | `—` | — | [AUDIO:LEAD_DESDE_CERO] Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de… | true | Sin criterio de evaluación especificado. |
| 5 | Usuario | `quiero importar pero no sé cómo funciona todo, tengo pensado…` | — |  |  |  |
| 6 | Agente | `—` | Usa [AUDIO:METODO_INICIO_PROGRAMA]. Lead dijo "no sé cómo funciona" pero TAMBIÉN… | [AUDIO:METODO_INICIO_PROGRAMA] Bueno, justamente por ahí es donde arrancamos en el programa: analiza… | true | La respuesta del agente aborda la idea concreta mencionada por el lead y se enfoca en el análisis del modelo de negocios, lo que cumple con el comportamiento esperado. |

---

## Resumen

| Resultado | Cantidad |
|-----------|----------|
| true | 46 |
| false | 0 |
| parcial | 0 |
| error | 0 |
| manual-only | 0 |

---

## Apéndice: Respuestas Completas

### Caso 1 — "no tengo claro cómo funciona todo esto" — Turno 2
**Respuesta:**
[AUDIO:RESPUESTA_INICIAL]
Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiendo algo o estás arrancando desde cero? Así voy directo a lo que te sirve.

### Caso 1 — "no tengo claro cómo funciona todo esto" — Turno 4
**Respuesta:**
[AUDIO:LEAD_DESDE_CERO]
Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de cero, no necesitás experiencia previa, pero sí hacerlo con un paso a paso claro, porque ahí es donde la mayoría de la gente se traba o pierde plata. En tu caso, ¿qué es lo que más te frena hoy para empezar? Contame.

### Caso 1 — "no tengo claro cómo funciona todo esto" — Turno 6
**Respuesta:**
[AUDIO:MICROVALOR_FALTA_INFO]
Sí, totalmente. El problema no es que falte info, es que hay demasiada suelta. Y eso en vez de ayudar, termina confundiendo más. Cuando lo ves ordenado, es otra cosa.
---
Lo que veo siempre es que la mayoría arranca buscando productos, pero primero hay que entender bien el proceso. Contame, ¿tenés alguna idea o producto en mente para importar?

### Caso 2 — "me falta información, no sé bien cómo funciona todo" — Turno 2
**Respuesta:**
[AUDIO:RESPUESTA_INICIAL]
Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiendo algo o estás arrancando desde cero? Así voy directo a lo que te sirve.

### Caso 2 — "me falta información, no sé bien cómo funciona todo" — Turno 4
**Respuesta:**
[AUDIO:LEAD_DESDE_CERO]
Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de cero, no necesitás experiencia previa, pero sí hacerlo con un paso a paso claro, porque ahí es donde la mayoría de la gente se traba o pierde plata. En tu caso, ¿qué es lo que más te frena hoy para empezar? Contame.

### Caso 2 — "me falta información, no sé bien cómo funciona todo" — Turno 6
**Respuesta:**
[AUDIO:MICROVALOR_FALTA_INFO]
Sí, totalmente. El problema no es que falte info, es que hay demasiada suelta. Y eso en vez de ayudar, termina confundiendo más. Cuando lo ves ordenado, es otra cosa.
---
Lo que veo siempre es que la mayoría arranca buscando productos, pero primero hay que entender bien el proceso. Contame, ¿tenés alguna idea o producto en mente para importar?

### Caso 3 — "no sé por dónde empezar, hay mucha info" — Turno 2
**Respuesta:**
[AUDIO:RESPUESTA_INICIAL]
Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiendo algo o estás arrancando desde cero? Así voy directo a lo que te sirve.

### Caso 3 — "no sé por dónde empezar, hay mucha info" — Turno 4
**Respuesta:**
[AUDIO:LEAD_DESDE_CERO]
Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de cero, no necesitás experiencia previa, pero sí hacerlo con un paso a paso claro, porque ahí es donde la mayoría de la gente se traba o pierde plata. En tu caso, ¿qué es lo que más te frena hoy para empezar? Contame.

### Caso 3 — "no sé por dónde empezar, hay mucha info" — Turno 6
**Respuesta:**
[AUDIO:MICROVALOR_NO_EMPIEZA]
Bien, ahí está el punto. No es que no puedas, es que no está claro el camino. Y cuando no tenés un paso a paso, todo parece más complicado. Pero cuando lo ordenás, se vuelve mucho más simple.

---
Lo que veo siempre es que la mayoría arranca buscando productos, pero primero hay que entender bien el proceso. Contame, ¿tenés alguna idea o producto en mente para importar?

### Caso 4 — "no sé cómo funciona todo" (variante edge, sin idea) — Turno 2
**Respuesta:**
[AUDIO:RESPUESTA_INICIAL]
Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiendo algo o estás arrancando desde cero? Así voy directo a lo que te sirve.

### Caso 4 — "no sé cómo funciona todo" (variante edge, sin idea) — Turno 4
**Respuesta:**
[AUDIO:LEAD_DESDE_CERO]
Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de cero, no necesitás experiencia previa, pero sí hacerlo con un paso a paso claro, porque ahí es donde la mayoría de la gente se traba o pierde plata. En tu caso, ¿qué es lo que más te frena hoy para empezar? Contame.

### Caso 4 — "no sé cómo funciona todo" (variante edge, sin idea) — Turno 6
**Respuesta:**
[AUDIO:MICROVALOR_FALTA_INFO]
Sí, totalmente. El problema no es que falte info, es que hay demasiada suelta. Y eso en vez de ayudar, termina confundiendo más. Cuando lo ves ordenado, es otra cosa.
---
Lo que veo siempre es que la mayoría arranca buscando productos, pero primero hay que entender bien el proceso. Contame, ¿tenés alguna idea o producto en mente para importar o querés arrancar explorando?

### Caso 5 — "me da miedo perder plata" — Turno 2
**Respuesta:**
[AUDIO:RESPUESTA_INICIAL]
Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiendo algo o estás arrancando desde cero? Así voy directo a lo que te sirve.

### Caso 5 — "me da miedo perder plata" — Turno 4
**Respuesta:**
[AUDIO:LEAD_DESDE_CERO]
Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de cero, no necesitás experiencia previa, pero sí hacerlo con un paso a paso claro, porque ahí es donde la mayoría de la gente se traba o pierde plata. En tu caso, ¿qué es lo que más te frena hoy para empezar? Contame.

### Caso 5 — "me da miedo perder plata" — Turno 6
**Respuesta:**
[AUDIO:MICROVALOR_MIEDO_PLATA]
Te entiendo, es súper común eso. Sobre todo cuando no tenés claro cómo es el proceso. Porque desde afuera parece que podés perder plata fácil. Pero en realidad, la mayoría de los errores vienen por no saber bien qué mirar antes de comprar. Cuando eso lo entendés, el riesgo baja muchísimo.
---
Lo que veo siempre es que la mayoría arranca buscando productos, pero primero hay que entender bien el proceso. Contame, ¿tenés alguna idea o producto en mente para importar?

### Caso 6 — "me da miedo no poder vender" — Turno 2
**Respuesta:**
[AUDIO:RESPUESTA_INICIAL]
Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiendo algo o estás arrancando desde cero? Así voy directo a lo que te sirve.

### Caso 6 — "me da miedo no poder vender" — Turno 4
**Respuesta:**
[AUDIO:LEAD_DESDE_CERO]
Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de cero, no necesitás experiencia previa, pero sí hacerlo con un paso a paso claro, porque ahí es donde la mayoría de la gente se traba o pierde plata. En tu caso, ¿qué es lo que más te frena hoy para empezar? Contame.

### Caso 6 — "me da miedo no poder vender" — Turno 6
**Respuesta:**
[AUDIO:MICROVALOR_MIEDO_PLATA]
Te entiendo, es súper común eso. Sobre todo cuando no tenés claro cómo es el proceso. Porque desde afuera parece que podés perder plata fácil. Pero en realidad, la mayoría de los errores vienen por no saber bien qué mirar antes de comprar. Cuando eso lo entendés, el riesgo baja muchísimo.
---
Lo que veo siempre es que la mayoría arranca buscando productos, pero primero hay que entender bien el proceso. Contame, ¿tenés alguna idea o producto en mente para importar?

### Caso 7 — miedo al PROCESO de importar (debe usar ROMPER_MIEDO) — Turno 2
**Respuesta:**
[AUDIO:RESPUESTA_INICIAL]
Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiendo algo o estás arrancando desde cero? Así voy directo a lo que te sirve.

### Caso 7 — miedo al PROCESO de importar (debe usar ROMPER_MIEDO) — Turno 4
**Respuesta:**
[AUDIO:LEAD_DESDE_CERO]
Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de cero, no necesitás experiencia previa, pero sí hacerlo con un paso a paso claro, porque ahí es donde la mayoría de la gente se traba o pierde plata. En tu caso, ¿qué es lo que más te frena hoy para empezar? Contame.

### Caso 7 — miedo al PROCESO de importar (debe usar ROMPER_MIEDO) — Turno 6
**Respuesta:**
[AUDIO:ROMPER_MIEDO]
Es normal lo que decís. La mayoría arranca pensando que es complicado o que necesitás experiencia, contactos, viajar… y no es así. El tema no es la dificultad. Es no entender el proceso. Cuando lo ves claro, se vuelve mucho más simple de lo que parece. ¿Qué es lo que más te genera duda hoy?

### Caso 8 — "¿y si no vendo?" — Turno 2
**Respuesta:**
[AUDIO:RESPUESTA_INICIAL]
Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiendo algo o estás arrancando desde cero? Así voy directo a lo que te sirve.

### Caso 8 — "¿y si no vendo?" — Turno 4
**Respuesta:**
Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de cero, no necesitás experiencia previa, pero sí hacerlo con un paso a paso claro, porque ahí es donde la mayoría de la gente se traba o pierde plata. En tu caso, ¿qué es lo que más te frena hoy para empezar? Contame.

### Caso 8 — "¿y si no vendo?" — Turno 6
**Respuesta:**
[AUDIO:MICROVALOR_MIEDO_PLATA]
Te entiendo, es súper común eso. Sobre todo cuando no tenés claro cómo es el proceso. Porque desde afuera parece que podés perder plata fácil. Pero en realidad, la mayoría de los errores vienen por no saber bien qué mirar antes de comprar. Cuando eso lo entendés, el riesgo baja muchísimo.
---
Lo que veo siempre es que la mayoría arranca buscando productos, pero primero hay que entender bien el proceso. Contame, ¿tenés alguna idea o producto en mente para importar?

### Caso 9 — microvalor en turno 3 (miedo a perder plata, excepción anti-cadena) — Turno 2
**Respuesta:**
[AUDIO:RESPUESTA_INICIAL]
Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiendo algo o estás arrancando desde cero? Así voy directo a lo que te sirve.

### Caso 9 — microvalor en turno 3 (miedo a perder plata, excepción anti-cadena) — Turno 4
**Respuesta:**
[AUDIO:LEAD_DESDE_CERO]
Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de cero, no necesitás experiencia previa, pero sí hacerlo con un paso a paso claro, porque ahí es donde la mayoría de la gente se traba o pierde plata. En tu caso, ¿qué es lo que más te frena hoy para empezar? Contame.

### Caso 9 — microvalor en turno 3 (miedo a perder plata, excepción anti-cadena) — Turno 6
**Respuesta:**
[AUDIO:MICROVALOR_MIEDO_PLATA]
Te entiendo, es súper común eso. Sobre todo cuando no tenés claro cómo es el proceso. Porque desde afuera parece que podés perder plata fácil. Pero en realidad, la mayoría de los errores vienen por no saber bien qué mirar antes de comprar. Cuando eso lo entendés, el riesgo baja muchísimo.
---
Lo que veo siempre es que la mayoría arranca buscando productos, pero primero hay que entender bien el proceso. ¿Tenés alguna idea o producto en mente para importar?

### Caso 10 — microvalor proveedores en turno 3 (excepción anti-cadena) — Turno 2
**Respuesta:**
[AUDIO:RESPUESTA_INICIAL]
Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiendo algo o estás arrancando desde cero? Así voy directo a lo que te sirve.

### Caso 10 — microvalor proveedores en turno 3 (excepción anti-cadena) — Turno 4
**Respuesta:**
[AUDIO:LEAD_CON_NEGOCIO]
Bien, ahí en ese caso tiene mucho sentido lo que estás viendo. Lo que pasa muchas veces es que ya están vendiendo, pero compran caro… y no se dan cuenta cuánto margen están perdiendo ahí. La importación bien hecha te cambia eso. Decime, ¿qué tipo de productos estás trabajando ahora?

### Caso 10 — microvalor proveedores en turno 3 (excepción anti-cadena) — Turno 6
**Respuesta:**
[AUDIO:MICROVALOR_PROVEEDORES]
Sí, eso también es bastante común. Porque desde afuera no sabés en quién confiar. Pero hay formas bastante claras de filtrar proveedores y evitar los típicos errores. Cuando eso lo entendés, cambia mucho la seguridad.
---
Lo que veo siempre es que la mayoría arranca buscando proveedores, pero primero hay que entender bien el proceso para no perder plata ni tiempo. Contame, ¿ya tenés capital para hacer tu primera importación o estás en etapa de planificación?

### Caso 11 — microvalor intento fracaso en turno 3 (excepción anti-cadena) — Turno 2
**Respuesta:**
[AUDIO:RESPUESTA_INICIAL]
Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiendo algo o estás arrancando desde cero? Así voy directo a lo que te sirve.

### Caso 11 — microvalor intento fracaso en turno 3 (excepción anti-cadena) — Turno 4
**Respuesta:**
[AUDIO:LEAD_DESDE_CERO]
Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de cero, no necesitás experiencia previa, pero sí hacerlo con un paso a paso claro, porque ahí es donde la mayoría de la gente se traba o pierde plata. En tu caso, ¿qué es lo que más te frena hoy para empezar? Contame.

### Caso 11 — microvalor intento fracaso en turno 3 (excepción anti-cadena) — Turno 6
**Respuesta:**
[AUDIO:MICROVALOR_INTENTO_FRACASO]
Ok, eso pasa bastante. Muchas veces no es el producto, sino cómo se encaró todo. Porque si no entendés bien el proceso, terminás probando sin mucho criterio. Y eso desgasta.
---
Lo que veo siempre es que la mayoría arranca buscando productos, pero primero hay que entender bien el proceso. Contame, ¿qué fue lo que intentaste hacer antes?

### Caso 12 — "quiero empezar + ¿cuánto cuesta?" → "cuéntame" — Turno 2
**Respuesta:**
[AUDIO:RESPUESTA_INICIAL]
Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiendo algo o estás arrancando desde cero? Así voy directo a lo que te sirve.

### Caso 12 — "quiero empezar + ¿cuánto cuesta?" → "cuéntame" — Turno 4
**Respuesta:**
Importadores Conectados cuesta USD 697. Tiene clases grabadas con acceso ilimitado, módulos de importación, finanzas, marketing, ecommerce y ventas, clases en vivo conmigo y con otros expertos, y 3 meses de acompañamiento.

¿Lo ves para vos?  
---

### Caso 13 — "¿cuánto vale?" → "dale, contame" — Turno 2
**Respuesta:**
[AUDIO:RESPUESTA_INICIAL]
Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiendo algo o estás arrancando desde cero? Así voy directo a lo que te sirve.

### Caso 13 — "¿cuánto vale?" → "dale, contame" — Turno 4
**Respuesta:**
Importadores Conectados cuesta USD 697.

Tiene clases grabadas con acceso ilimitado, módulos de importación, finanzas, marketing, ecommerce y ventas, clases en vivo conmigo y con otros expertos, y 3 meses de acompañamiento.

¿Lo ves para vos?

### Caso 14 — lead con idea concreta sigue usando METODO — Turno 2
**Respuesta:**
[AUDIO:RESPUESTA_INICIAL]
Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiendo algo o estás arrancando desde cero? Así voy directo a lo que te sirve.

### Caso 14 — lead con idea concreta sigue usando METODO — Turno 4
**Respuesta:**
[AUDIO:LEAD_DESDE_CERO]
Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de cero, no necesitás experiencia previa, pero sí hacerlo con un paso a paso claro, porque ahí es donde la mayoría de la gente se traba o pierde plata. En tu caso, ¿qué es lo que más te frena hoy para empezar? Contame.

### Caso 14 — lead con idea concreta sigue usando METODO — Turno 6
**Respuesta:**
[AUDIO:METODO_INICIO_PROGRAMA]
Bueno, justamente por ahí es donde arrancamos en el programa: analizando la idea, analizando el modelo de negocios, viendo qué tan viable es, qué tan rentable es, generando una estrategia, analizando todos los canales de venta, el cliente, el producto, todo lo que va a estar enfocado en nuestro negocio para generar una estrategia, y a través de esa estrategia poder crecer y poder avanzar rápido.
---
Contame, ¿qué idea tenés en mente?

### Caso 15 — lead con producto concreto sigue usando METODO — Turno 2
**Respuesta:**
[AUDIO:RESPUESTA_INICIAL]
Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiendo algo o estás arrancando desde cero? Así voy directo a lo que te sirve.

### Caso 15 — lead con producto concreto sigue usando METODO — Turno 4
**Respuesta:**
[AUDIO:METODO_INICIO_PROGRAMA]
Bueno, justamente por ahí es donde arrancamos en el programa: analizando la idea, analizando el modelo de negocios, viendo qué tan viable es, qué tan rentable es, generando una estrategia, analizando todos los canales de venta, el cliente, el producto, todo lo que va a estar enfocado en nuestro negocio para generar una estrategia, y a través de esa estrategia poder crecer y poder avanzar rápido.
---
Perfecto, contame — ¿hoy ya vendés ropa o arrancás desde cero con esto?

### Caso 15 — lead con producto concreto sigue usando METODO — Turno 6
**Respuesta:**
Bien, ahí está el punto. No es que no puedas, es que no está claro el camino. Y cuando no tenés un paso a paso, todo parece más complicado. Pero cuando lo ordenás, se vuelve mucho más simple.
---
Para que te dé mejor una mano, ¿tenés ya algo de capital para arrancar o estás viendo todavía?

### Caso 16 — info + idea concreta → METODO gana — Turno 2
**Respuesta:**
[AUDIO:RESPUESTA_INICIAL]
Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiendo algo o estás arrancando desde cero? Así voy directo a lo que te sirve.

### Caso 16 — info + idea concreta → METODO gana — Turno 4
**Respuesta:**
[AUDIO:LEAD_DESDE_CERO]
Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de cero, no necesitás experiencia previa, pero sí hacerlo con un paso a paso claro, porque ahí es donde la mayoría de la gente se traba o pierde plata. En tu caso, ¿qué es lo que más te frena hoy para empezar? Contame.

### Caso 16 — info + idea concreta → METODO gana — Turno 6
**Respuesta:**
[AUDIO:METODO_INICIO_PROGRAMA]
Bueno, justamente por ahí es donde arrancamos en el programa: analizando la idea, analizando el modelo de negocios, viendo qué tan viable es, qué tan rentable es, generando una estrategia, analizando todos los canales de venta, el cliente, el producto, todo lo que va a estar enfocado en nuestro negocio para generar una estrategia, y a través de esa estrategia poder crecer y poder avanzar rápido.
---
Para entender mejor, ¿ya tenés capital para hacer la primera importación o estás en etapa de juntar ese dinero?
