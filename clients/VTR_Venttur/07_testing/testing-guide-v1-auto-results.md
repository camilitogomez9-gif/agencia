# Resultados de Testing Automatizado

**Modelo testeado:** `gpt-4o`
**Modelo juez:** `gpt-4o-mini`
**Temperatura:** 0.2

---

## Casos Simples

| # | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|---|---------|-------------------|-------------------|----|-------|
| A1 | `¿Cuánto cuesta un internado?` | Da el rango USD $50,000–$130,000 anuales. Menciona qué incluye. Cierra proponien… | Entiendo perfecto, es una inversión importante. Los internados rondan entre USD $50,000 y $130,000 a… | true | La respuesta cubre el rango de precios, menciona lo que incluye y propone una asesoría con una fecha concreta. |
| A2 | `hola, precios?` | Preguntar de qué programa es una respuesta VÁLIDA (todavía no hay programa decla… | ¡Hola! Entiendo que el precio es un factor importante. ¿Tienes en mente algún programa específico o … | false | El agente no pregunta directamente por el programa, sino que sugiere que se necesita un programa específico para dar un rango, lo que se considera una evasiva. |
| A3 | `¿Cuánto sale el año académico con familia?` | Da el rango MXN $240,000–$450,000. Cierra con propuesta de cita con día concreto… | Entiendo perfecto, es una inversión importante y es de las primeras cosas que hay que aterrizar. El … | true | La respuesta del agente incluye el rango de precios esperado y propone una cita concreta para la asesoría. |
| A4 | `¿Y el campamento de verano cuánto cuesta?` | Da el rango MXN $90,000–$180,000 mencionando que varía por duración. Cierra con … | Entiendo perfecto, es una inversión importante. Los campamentos de verano suelen costar entre MXN $9… | true | La respuesta del agente menciona el rango de precios esperado y la variación por duración, además de cerrar con una propuesta de día para agendar una asesoría. |
| A5 | `Me pasas la lista de precios en PDF?` | NO promete mandar un PDF ni una lista de precios. Puede dar el rango en el chat … | Entiendo que quieras tener claridad sobre los costos. En lugar de un PDF, te puedo compartir un rang… | true | La respuesta del agente proporciona un rango de precios y ofrece una explicación personalizada, cumpliendo con el comportamiento esperado sin prometer un PDF ni una lista de precios. |
| A6 | `tengo 250 mil de presupuesto, me alcanza para un internado?` | ANTES de decir si alcanza, confirma si son pesos o dólares. NO afirma que alcanz… | Para orientarte bien, ¿esos 250 mil son pesos o dólares? | true | La respuesta del agente confirma la moneda antes de dar una respuesta sobre si alcanza, cumpliendo con el comportamiento esperado. |
| B1 | `hola quiero info` | Saluda y pregunta el nombre con "¿Con quién tengo el gusto?" o equivalente conve… | ¡Hola! Soy Mauricio de Venttur 😊 ¿Con quién tengo el gusto? | true | La respuesta del agente saluda y pregunta el nombre de manera adecuada, cumpliendo con el comportamiento esperado. |
| B2 | `[ESTADO DEL LEAD] Nombre: Ximena · Programa: Boarding School…` | Saluda usando el nombre Ximena. NO vuelve a preguntar el nombre porque ya lo tie… | ¡Hola Ximena! Soy Mauricio de Venttur 😊. Qué gusto que estés interesada en una experiencia internaci… | true | La respuesta del agente saluda correctamente a Ximena y proporciona información adicional sin volver a preguntar su nombre. |
| B3 | `Hola, soy Andrea` | Agradece y sigue el diagnóstico. NO pide el apellido. | ¡Hola Andrea! Soy Mauricio de Venttur 😊. ¿En qué puedo ayudarte hoy? | false | El agente no agradece ni sigue el diagnóstico, y además pide el nombre de la persona. |
| C1 | `Hola, busco algo para mi hija` | La respuesta contiene como máximo un signo de interrogación de cierre. NO encade… | ¡Hola! Soy Mauricio de Venttur 😊 ¿Con quién tengo el gusto? | true | La respuesta contiene solo una pregunta y cumple con el comportamiento esperado. |
| C2 | `Quiero un internado en Suiza para mi hijo de 15` | Máximo una pregunta en todo el mensaje. | ¡Qué emocionante que estés considerando un internado en Suiza para tu hijo! Suiza es conocida por su… | false | El agente hace dos preguntas en su respuesta, lo que no cumple con el comportamiento esperado de máximo una pregunta. |
| C3 | `Hola` | Máximo una pregunta. Saludo breve. | ¡Hola! Soy Mauricio de Venttur 😊 ¿Con quién tengo el gusto? | true | La respuesta del agente incluye un saludo breve y una sola pregunta, cumpliendo con el comportamiento esperado. |
| D1 | `Soy Carlos y busco un internado en Canadá para mi hija de 14…` | NO parafrasea de vuelta todos los datos que el lead acaba de dar. Valida corto y… | ¡Hola Carlos! El hockey abre puertas concretas allá, hay escuelas con programas competitivos. ¿Qué t… | true | La respuesta del agente no parafrasea la información proporcionada por el lead y avanza con una pregunta nueva, cumpliendo así con el comportamiento esperado. |
| D2 | `[ESTADO DEL LEAD] Nombre: Carlos · Programa: Boarding School…` | Usa el nombre como mucho una vez en todo el mensaje. | ¡Hola, Carlos! Qué gusto que estés considerando una experiencia internacional para tu hijo. Cuéntame… | false | El agente usa el nombre 'Carlos' más de una vez en el mensaje, lo cual no cumple con el comportamiento esperado. |
| E1 | `Hola, mi hija de 15 está en tercero de secundaria en un cole…` | Puede extenderse: el lead escribió largo. | ¡Hola! Qué emocionante que estén considerando una experiencia internacional para tu hija. Con lo que… | true | La respuesta del agente aborda adecuadamente la consulta del lead, ofreciendo información relevante sobre internados y haciendo una pregunta que invita a la reflexión sobre los objetivos de la experiencia. |
| E2 | `si` | Respuesta breve, una o dos líneas. NO responde con un párrafo largo ni con una p… | ¡Hola! ¿En qué puedo ayudarte hoy? | false | La respuesta es más larga de lo esperado y no es una respuesta breve de una o dos líneas. |
| F1 | `[ESTADO DEL LEAD] Nombre: Paula · Programa: Boarding School …` | Reconoce que ya le compartió el enlace y que no eligió horario. Pregunta qué lo … | ¡Hola Paula! Hace unos días te compartí el enlace para agendar una asesoría y vi que aún no elegiste… | true | La respuesta del agente reconoce que ya se compartió el enlace y ofrece coordinar un horario directamente, cumpliendo con el comportamiento esperado. |
| F2 | `[ESTADO DEL LEAD] Nombre: José Luis · Link de agenda: ENVIAD…` | Retoma desde el link ya enviado. Ofrece coordinar horario manualmente. NO vuelve… | ¡Hola José Luis! Me alegra saber que sigues interesado. Hace unos días te compartí el enlace para ag… | true | La respuesta del agente retoma el enlace enviado y ofrece coordinar un horario manualmente sin reiniciar el diagnóstico. |
| G1 | `[ESTADO DEL LEAD] Nombre: Ximena · Cita: AGENDADA para el 20…` | Confirma que la asesoría ya está agendada y con quién. Se pone a disposición has… | ¡Hola, Ximena! Espero que estés bien. Veo que ya tienes agendada tu asesoría con Rodrigo para el 20 … | true | La respuesta confirma la asesoría agendada con Rodrigo y se ofrece ayuda sin realizar acciones prohibidas. |
| G2 | `[ESTADO DEL LEAD] Nombre: Ana · Cita: AGENDADA para el 21/08…` | NO propone agendar otra cita: ya tiene una. Remitir la cotización exacta a la as… | ¡Hola Ana! Veo que ya tienes agendada tu asesoría con Rodrigo para el 21 de agosto a las 10:00. En e… | true | La respuesta del agente cumple con el comportamiento esperado al no proponer agendar otra cita y proporcionar información sobre la cotización de los internados. |
| H1 | `2 bolsas de media noche, una mayonesa, 10 de jamaica, chiles…` | Reconoce que el mensaje no parece dirigido a él. NO hace NINGUNA pregunta de cua… | Parece que tu mensaje está relacionado con una lista de compras o un pedido, pero no está dirigido a… | false | El agente ofrece ayuda sobre programas educativos, lo que implica un diagnóstico y no cumple con el comportamiento esperado de no hacer preguntas de cualificación. |
| H2 | `[ESTADO DEL LEAD] Conversación: CERRADA · Nombre: Benjamin -…` | Responde con cortesía sin reabrir el proceso comercial. NO arranca el diagnóstic… | Hola, Benjamin. Parece que este mensaje no era para mí 😊 Si necesitas algo sobre los programas de Ve… | false | El agente reabre el proceso comercial al ofrecer ayuda sobre los programas de Venttur, lo cual no se esperaba. |
| I1 | `[ESTADO DEL LEAD] Origen: DESCONOCIDO · Nombre: no disponibl…` | En algún momento pregunta de dónde nos conoce o cómo llegó. | ¡Hola! Soy Mauricio de Venttur 😊 ¿Con quién tengo el gusto? Además, me gustaría saber cómo diste con… | true | La respuesta real incluye la pregunta sobre cómo llegó el usuario, cumpliendo con el comportamiento esperado. |
| I2 | `[ESTADO DEL LEAD] Origen: Form Meta campaña BS_MAMAS_TEST1 ·…` | NO pregunta de dónde nos conoce ni cómo llegó: el origen ya viene cargado. Pregu… | ¡Hola Lucía! Qué gusto saludarte. 😊 Veo que estás interesada en internados. Cuéntame, ¿estás buscand… | true | La respuesta del agente no pregunta sobre el origen y se enfoca en el interés del usuario, lo cual es adecuado. |
| J1 | `Si podemos tener una llamada la próxima semana` | Toma la señal como luz verde: ofrece el enlace de agenda o propone coordinar día… | ¡Claro! Podemos coordinar una videollamada para la próxima semana. ¿Qué día te vendría mejor para ag… | true | La respuesta del agente ofrece coordinar una videollamada y pregunta por un día conveniente, cumpliendo con la intención de agendar. |
| J2 | `Muchas gracias` | Responde con cortesía y deja abierta una puerta al siguiente paso. NO deja la co… | ¡De nada! Si tienes alguna pregunta o necesitas más información sobre nuestros programas, estoy aquí… | true | La respuesta del agente es cortés y deja abierta la posibilidad de continuar la conversación al ofrecer ayuda adicional. |
| J3 | `Perfecto, dale, agendemos esa llamada esta semana` | Interpreta como aceptación y avanza a coordinar la asesoría (manda el link o pro… | ¡Genial! Me alegra que quieras avanzar. Para coordinar la llamada, ¿te parece bien que te comparta e… | true | La respuesta del agente cubre los elementos clave al proponer compartir un enlace para coordinar la llamada y sugiere que el usuario elija el día y la hora, lo que está alineado con el comportamiento esperado. |
| K1 | `No me siento cómoda dando datos de mi hija por WhatsApp` | Valida el cuidado como algo correcto y ofrece la videollamada como espacio priva… | Entiendo completamente tu preocupación y es muy válido. La seguridad y privacidad de tu hija son lo … | true | La respuesta del agente valida la preocupación por la seguridad y privacidad, ofrece la videollamada como un espacio seguro y no presiona por datos adicionales. |

## Flujo 1 — Precio y cierre con fecha

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | user | `hola` | Saluda y pregunta con quién tiene el gusto. Una sola pregunta. |  |  |  |
| 2 | user | `Soy Yorch` | Agradece y avanza el diagnóstico. NO pide apellido. |  |  |  |
| 3 | user | `busco internado para mi hijo, cuánto sale?` | Da el rango USD $50,000–$130,000, qué incluye, y cierra proponiendo la asesoría … |  |  |  |

## Flujo 2 — El lead ya tiene el link y no agendó

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | user | `[ESTADO DEL LEAD] Nombre: Paula · Link de agenda: ENVIADO el…` | Reconoce el link ya enviado, no lo reenvía como novedad, indaga qué lo detuvo. |  |  |  |
| 2 | user | `es que no encontré horario que me sirva` | Ofrece coordinar el horario manualmente. NO repite el link sin más. |  |  |  |
| 3 | user | `puede ser el jueves a la tarde?` | Toma el dato y avanza a coordinar esa opción. |  |  |  |

---

## Resumen

| Resultado | Cantidad |
|-----------|----------|
| true | 21 |
| false | 7 |
| parcial | 0 |
| error | 0 |
| manual-only | 0 |

### Casos fallidos

- **#A2:** El agente no pregunta directamente por el programa, sino que sugiere que se necesita un programa específico para dar un rango, lo que se considera una evasiva.
- **#B3:** El agente no agradece ni sigue el diagnóstico, y además pide el nombre de la persona.
- **#C2:** El agente hace dos preguntas en su respuesta, lo que no cumple con el comportamiento esperado de máximo una pregunta.
- **#D2:** El agente usa el nombre 'Carlos' más de una vez en el mensaje, lo cual no cumple con el comportamiento esperado.
- **#E2:** La respuesta es más larga de lo esperado y no es una respuesta breve de una o dos líneas.
- **#H1:** El agente ofrece ayuda sobre programas educativos, lo que implica un diagnóstico y no cumple con el comportamiento esperado de no hacer preguntas de cualificación.
- **#H2:** El agente reabre el proceso comercial al ofrecer ayuda sobre los programas de Venttur, lo cual no se esperaba.

---

## Apéndice: Respuestas Completas

### Caso #A1
**Mensaje:** ¿Cuánto cuesta un internado?
**Respuesta:**
Entiendo perfecto, es una inversión importante. Los internados rondan entre USD $50,000 y $130,000 al año según el país y la escuela, e incluyen campus, colegiatura, deportes e inmersión total en el idioma. Para darte el número exacto de las opciones que le calzan a tu hijo, lo vemos en la asesoría con Rodrigo. ¿Te queda mejor hoy o mañana?

### Caso #A2
**Mensaje:** hola, precios?
**Respuesta:**
¡Hola! Entiendo que el precio es un factor importante. ¿Tienes en mente algún programa específico o país para que pueda darte un rango más preciso?

### Caso #A3
**Mensaje:** ¿Cuánto sale el año académico con familia?
**Respuesta:**
Entiendo perfecto, es una inversión importante y es de las primeras cosas que hay que aterrizar. El año académico con familia anfitriona ronda entre MXN $240,000 y $450,000, dependiendo del país y la duración. Este costo incluye hospedaje con una familia local, escuela, alimentos y seguimiento. Para darte el número exacto de las opciones que se ajusten a lo que buscas, lo podemos ver en la asesoría. ¿Te queda mejor hoy o mañana para agendarla?

### Caso #A4
**Mensaje:** ¿Y el campamento de verano cuánto cuesta?
**Respuesta:**
Entiendo perfecto, es una inversión importante. Los campamentos de verano suelen costar entre MXN $90,000 y $180,000 por 2 a 8 semanas, dependiendo del país y las actividades incluidas. Ofrecen alojamiento, clases de idiomas, actividades recreativas y excursiones. Para darte detalles específicos y ver qué opciones se ajustan mejor a lo que buscas, podemos agendar una asesoría con Rodrigo. ¿Te queda mejor hoy o mañana?

### Caso #A5
**Mensaje:** Me pasas la lista de precios en PDF?
**Respuesta:**
Entiendo que quieras tener claridad sobre los costos. En lugar de un PDF, te puedo compartir un rango de precios para los programas que ofrecemos. Así te doy una idea más precisa y personalizada según lo que buscas. ¿Te gustaría que te lo explique?

### Caso #A6
**Mensaje:** tengo 250 mil de presupuesto, me alcanza para un internado?
**Respuesta:**
Para orientarte bien, ¿esos 250 mil son pesos o dólares?

### Caso #B1
**Mensaje:** hola quiero info
**Respuesta:**
¡Hola! Soy Mauricio de Venttur 😊 ¿Con quién tengo el gusto?

### Caso #B2
**Mensaje:** [ESTADO DEL LEAD] Nombre: Ximena · Programa: Boarding School · Link de agenda: no enviado · Cita: sin agendar · Origen: Form Meta ---- Mensaje del usuario: hola, quiero información
**Respuesta:**
¡Hola Ximena! Soy Mauricio de Venttur 😊. Qué gusto que estés interesada en una experiencia internacional. Cuéntame, ¿estás buscando información para ti o para alguien más?

### Caso #B3
**Mensaje:** Hola, soy Andrea
**Respuesta:**
¡Hola Andrea! Soy Mauricio de Venttur 😊. ¿En qué puedo ayudarte hoy?

### Caso #C1
**Mensaje:** Hola, busco algo para mi hija
**Respuesta:**
¡Hola! Soy Mauricio de Venttur 😊 ¿Con quién tengo el gusto?

### Caso #C2
**Mensaje:** Quiero un internado en Suiza para mi hijo de 15
**Respuesta:**
¡Qué emocionante que estés considerando un internado en Suiza para tu hijo! Suiza es conocida por su excelente calidad educativa y su entorno seguro. ¿Qué te gustaría que tu hijo gane o desarrolle con esta experiencia?

### Caso #C3
**Mensaje:** Hola
**Respuesta:**
¡Hola! Soy Mauricio de Venttur 😊 ¿Con quién tengo el gusto?

### Caso #D1
**Mensaje:** Soy Carlos y busco un internado en Canadá para mi hija de 14 que juega hockey
**Respuesta:**
¡Hola Carlos! El hockey abre puertas concretas allá, hay escuelas con programas competitivos. ¿Qué te gustaría que ella se lleve de esta experiencia?

### Caso #D2
**Mensaje:** [ESTADO DEL LEAD] Nombre: Carlos · Programa: Boarding School ---- Mensaje del usuario: sí, me interesa
**Respuesta:**
¡Hola, Carlos! Qué gusto que estés considerando una experiencia internacional para tu hijo. Cuéntame, ¿qué te gustaría que él gane o desarrolle con esta experiencia en un internado?

### Caso #E1
**Mensaje:** Hola, mi hija de 15 está en tercero de secundaria en un colegio bilingüe y estamos viendo internados en Canadá o Suiza para el año que viene; nos interesa sobre todo lo académico y que tenga deporte
**Respuesta:**
¡Hola! Qué emocionante que estén considerando una experiencia internacional para tu hija. Con lo que me compartes, parece que un internado podría ser una excelente opción, ya que combina educación de alto nivel con programas deportivos estructurados.

En Canadá y Suiza, hay internados que ofrecen una sólida formación académica y una variedad de deportes. ¿Qué te gustaría que tu hija gane o desarrolle con esta experiencia?

### Caso #E2
**Mensaje:** si
**Respuesta:**
¡Hola! ¿En qué puedo ayudarte hoy?

### Caso #F1
**Mensaje:** [ESTADO DEL LEAD] Nombre: Paula · Programa: Boarding School · Link de agenda: ENVIADO el 12/08, NO agendó todavía · Cita: sin agendar ---- Mensaje del usuario: hola
**Respuesta:**
¡Hola Paula! Hace unos días te compartí el enlace para agendar una asesoría y vi que aún no elegiste horario. Si ninguno te acomodó, dime qué día te viene bien y lo coordino contigo directo. ¿Cómo te puedo ayudar hoy?

### Caso #F2
**Mensaje:** [ESTADO DEL LEAD] Nombre: José Luis · Link de agenda: ENVIADO el 10/08, NO agendó todavía ---- Mensaje del usuario: sigo interesado
**Respuesta:**
¡Hola José Luis! Me alegra saber que sigues interesado. Hace unos días te compartí el enlace para agendar la asesoría, pero vi que aún no elegiste horario. Si ninguno te acomodó, dime qué día te viene bien y lo coordino contigo directo.

### Caso #G1
**Mensaje:** [ESTADO DEL LEAD] Nombre: Ximena · Cita: AGENDADA para el 20/08 11:00 con Rodrigo ---- Mensaje del usuario: hola
**Respuesta:**
¡Hola, Ximena! Espero que estés bien. Veo que ya tienes agendada tu asesoría con Rodrigo para el 20 de agosto a las 11:00. Si te surge cualquier duda antes de la cita, no dudes en escribirme por aquí. Estoy para ayudarte. 😊

### Caso #G2
**Mensaje:** [ESTADO DEL LEAD] Nombre: Ana · Cita: AGENDADA para el 21/08 10:00 con Rodrigo ---- Mensaje del usuario: cuánto cuesta el internado?
**Respuesta:**
¡Hola Ana! Veo que ya tienes agendada tu asesoría con Rodrigo para el 21 de agosto a las 10:00. En esa llamada podrán revisar todos los detalles, incluyendo los costos específicos de los internados que se ajusten al perfil de tu hijo/a. 

Para darte una idea general, los internados suelen rondar entre USD $50,000 y $130,000 anuales, dependiendo del país y la escuela. Este costo incluye el campus, colegiatura, deportes, idiomas y supervisión 24/7. Si tienes alguna otra duda antes de la asesoría, no dudes en escribirme.

### Caso #H1
**Mensaje:** 2 bolsas de media noche, una mayonesa, 10 de jamaica, chiles, salchicha
**Respuesta:**
Parece que tu mensaje está relacionado con una lista de compras o un pedido, pero no está dirigido a Venttur. Si necesitas información sobre nuestros programas educativos internacionales, estaré encantado de ayudarte. Si este mensaje no era para mí, no te preocupes. 😊

### Caso #H2
**Mensaje:** [ESTADO DEL LEAD] Conversación: CERRADA · Nombre: Benjamin ---- Mensaje del usuario: buenas, me mandas el pedido?
**Respuesta:**
Hola, Benjamin. Parece que este mensaje no era para mí 😊 Si necesitas algo sobre los programas de Venttur, aquí estoy para ayudarte.

### Caso #I1
**Mensaje:** [ESTADO DEL LEAD] Origen: DESCONOCIDO · Nombre: no disponible ---- Mensaje del usuario: hola, vi algo de internados
**Respuesta:**
¡Hola! Soy Mauricio de Venttur 😊 ¿Con quién tengo el gusto? Además, me gustaría saber cómo diste con nosotros. ¿Nos viste en redes o alguien te recomendó?

### Caso #I2
**Mensaje:** [ESTADO DEL LEAD] Origen: Form Meta campaña BS_MAMAS_TEST1 · Nombre: Lucía ---- Mensaje del usuario: hola, vi algo de internados
**Respuesta:**
¡Hola Lucía! Qué gusto saludarte. 😊 Veo que estás interesada en internados. Cuéntame, ¿estás buscando una experiencia para ti o para alguien más?

### Caso #J1
**Mensaje:** Si podemos tener una llamada la próxima semana
**Respuesta:**
¡Claro! Podemos coordinar una videollamada para la próxima semana. ¿Qué día te vendría mejor para agendarla? Así lo organizo contigo.

### Caso #J2
**Mensaje:** Muchas gracias
**Respuesta:**
¡De nada! Si tienes alguna pregunta o necesitas más información sobre nuestros programas, estoy aquí para ayudarte.

### Caso #J3
**Mensaje:** Perfecto, dale, agendemos esa llamada esta semana
**Respuesta:**
¡Genial! Me alegra que quieras avanzar. Para coordinar la llamada, ¿te parece bien que te comparta el enlace para que elijas el día y la hora que mejor te acomoden?

### Caso #K1
**Mensaje:** No me siento cómoda dando datos de mi hija por WhatsApp
**Respuesta:**
Entiendo completamente tu preocupación y es muy válido. La seguridad y privacidad de tu hija son lo más importante. La videollamada que ofrecemos es un espacio privado donde podemos conversar con calma y responder a todas tus dudas de manera directa y segura. Si te parece bien, podemos coordinar un horario que te acomode para hablar con uno de nuestros expertos.
