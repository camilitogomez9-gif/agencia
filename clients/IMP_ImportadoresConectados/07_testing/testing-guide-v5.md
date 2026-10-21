# Guía de Testing — Agente Importadores Conectados v5

**Canal:** Instagram DM / WhatsApp / Facebook
**Prompt versión testeada:** v1.7
**Estado:** Pendiente

---

## Contexto

Guía de testing de los cambios incorporados en v1.7:
1. Precio IC actualizado: USD 697 (antes USD 497)
2. Regla de tono: frases simples y naturales, no copy-perfectas
3. Regla audio-texto: el audio complementa el texto, no lo duplica
4. 5 nuevos audios de microvalor por dolor + mapeo en ETAPA 2

---

## Instrucciones de uso

1. Ejecutar cada caso en el canal de prueba.
2. Fijar `{{ORIGEN}}` según se indique en la columna.
3. Pegar la respuesta exacta en "Resultado obtenido".
4. Marcar OK como `true`, `false` o `parcial`.
5. Agregar notas al pie si hay patrones sistémicos.

---

## Casos RE-TEST v1.7

| # | Área | Flujo | Mensajes a enviar | `{{ORIGEN}}` | Resultado esperado | Resultado obtenido | OK |
|---|------|-------|-------------------|--------------|-------------------|-------------------|----|
| 1 | Precio | Presentación IC directa | Lead: "quiero empezar, ¿de cuánto es el programa?" → esperar respuesta → Lead: "bien, cuéntame" | directo | El agente presenta IC con **USD 697** (NO 497). El texto dice "697". NO aparece "497" en ningún punto de la conversación. | | |
| 2 | Precio | Cierre con precio | Lead: "hola, quiero importar" → responder → Lead: "arranco de cero" → responder → Lead: "sí, quiero empezar" | directo | Cuando el agente presente IC con precio, la cifra es **USD 697**. | | |
| 3 | Tono | Naturalidad post-idea | Lead: "hola quiero más información" → responder → Lead: "tengo una idea pero no sé cómo encararla" | directo | El agente usa `[AUDIO:METODO_INICIO_PROGRAMA]`. El texto de cualquier mensaje posterior es corto, directo, sin frases tipo "Lo que se busca es ordenar esa idea para ver si tiene sentido y cómo encarar la importación con criterio." Las frases son cortadas y naturales. | | |
| 4 | Microvalor | Dolor: miedo a perder plata | Lead: "buenas" → responder → Lead: "arranco de cero" → responder → Lead: "me da miedo perder plata, si invierto y no me va" | directo | El agente usa **[AUDIO:MICROVALOR_MIEDO_PLATA]**. NO usa [AUDIO:OBJECION_PRECIO] ni [AUDIO:ROMPER_MIEDO]. El texto del audio es: "Te entiendo, es súper común eso...". Después del audio, avanza (reencuadre o pregunta de cierre suave), NO salta directo a propuesta de IC. | | |
| 5 | Microvalor | Dolor: no sé por dónde empezar | Lead: "hola" → responder → Lead: "estoy arrancando de cero" → responder → Lead: "no sé por dónde empezar, me perdí con tanta info" | directo | El agente usa **[AUDIO:MICROVALOR_NO_EMPIEZA]** (NO [AUDIO:MICROVALOR_FALTA_INFO] — el trigger es "no saber por dónde empezar", no la falta de info en sí). Texto del audio: "Bien, ahí está el punto...". | | |
| 6 | Microvalor | Dolor: falta de información | Lead: "hola, quiero importar" → responder → Lead: "arranco de cero" → responder → Lead: "y si falta de información" | directo | El agente usa **[AUDIO:MICROVALOR_FALTA_INFO]**. NO usa [AUDIO:METODO_INICIO_PROGRAMA] (que es para cuando el lead tiene una idea concreta). Texto del audio: "Sí, totalmente. El problema no es que falte info...". | | |
| 7 | Microvalor | Dolor: no confío en proveedores | Lead: "buenas" → responder → Lead: "ya vendo algo, quiero importar" → responder → Lead: "el tema es que no sé a quién comprarle, me da miedo que me estafen" | directo | El agente usa **[AUDIO:MICROVALOR_PROVEEDORES]**. Texto del audio: "Sí, eso también es bastante común...". | | |
| 8 | Microvalor | Dolor: ya lo intenté y no funcionó | Lead: "hola" → responder → Lead: "arranco de cero" → responder → Lead: "en realidad ya lo intenté antes pero no me fue bien" | directo | El agente usa **[AUDIO:MICROVALOR_INTENTO_FRACASO]** (NO [AUDIO:OBJECION_PRECIO] ni [AUDIO:ROMPER_MIEDO]). Texto del audio: "Ok, eso pasa bastante...". Clasifica o re-clasifica el perfil como `intento_fracaso` internamente. | | |
| 9 | Microvalor | No repetir microvalor ya enviado | (Continuación del caso #4 si pasó) Lead recibe MICROVALOR_MIEDO_PLATA → responde → Lead dice algo que vuelve a mencionar el miedo a perder plata | directo | El agente NO repite [AUDIO:MICROVALOR_MIEDO_PLATA]. Responde en texto normal con la misma idea pero sin audio. | | |
| 10 | Audio-texto | Complemento audio + texto | Cualquier caso donde el agente genere una respuesta con audio en un bloque Y texto en otro bloque (separados por ---) | cualquiera | El texto del segundo bloque agrega información nueva que el audio no dijo (ej: una pregunta de seguimiento, el link, un dato concreto). NO repite la idea del audio en otras palabras. | | |

---

## Notas de testing

- Los casos #4–#8 son el corazón de esta guía. Si los microvalores no se disparan correctamente, el agente sigue respondiendo con el mismo audio genérico a todos los leads.
- El caso #3 verifica tono: buscar específicamente si el agente usa frases largas y "copy-perfectas" vs. frases cortas y naturales.
- El caso #10 puede evaluarse revisando cualquier respuesta con audio + texto en la misma salida.

---

**Correcciones aplicadas en v1.7:** precio IC (697), regla de tono (frases simples), regla audio-texto (complemento), 5 microvalores por dolor.
