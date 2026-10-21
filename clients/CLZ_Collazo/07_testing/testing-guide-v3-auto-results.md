# Resultados de Testing Automatizado

**Modelo testeado:** `gpt-4o`
**Modelo juez:** `gpt-4o-mini`
**Temperatura:** 0.2

---

## Casos Simples

| # | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|---|---------|-------------------|-------------------|----|-------|
| 22 | `¿Llegan a Villa García?` | Confirma que sí, Villa García está dentro de la zona de cobertura (Interior de C… | Hola! Soy el asistente de Collazo ⚡️   Sí, cubrimos Villa García para nuestros servicios de aires ac… | true | La respuesta confirma que Villa García está dentro de la zona de cobertura y no pregunta a qué departamento pertenece, cumpliendo con el comportamiento esperado. |
| 23 | `Estoy en ruta 8 km 19, ¿hacen instalaciones ahí?` | Confirma cobertura de la zona (Villa García / Ruta 8 km 19). NO dice que no cubr… | ¡Hola! Sí, cubrimos la zona de Villa García, que incluye Ruta 8 km 19. Podemos ayudarte con la insta… | true | La respuesta confirma que cubren la zona de Villa García y Ruta 8 km 19, cumpliendo con el comportamiento esperado. |
| 10 | `¿Hacen desinstalación de calefón?` | Consulta si es para poner uno nuevo (retiro de tanque viejo, $900 adicional) o s… | Hola! Soy el asistente de Collazo ⚡️   Sí, realizamos desinstalación de calefones. ¿Estás interesado… | true | La respuesta del agente cubre los elementos clave requeridos al preguntar si el usuario desea retirar un calefón viejo para instalar uno nuevo o solo necesita el retiro, y evita comportamientos prohibidos. |
| 11 | `¿Pueden sacar un calefón que tengo instalado?` | Igual que caso #10: consulta si hay nueva instalación o es solo retiro. | ¡Hola! Soy el asistente de Collazo ⚡️   ¿Estás interesado en retirar el calefón porque vas a instala… | true | La respuesta del agente consulta si hay una nueva instalación o solo un retiro, cumpliendo con el comportamiento esperado. |
| 12 | `Quiero que me quiten el aire acondicionado` | Identifica como Desmontaje Aire Acondicionado. Informa precio ($1800 para 9000–1… | [SEGUIMIENTO]   Claro, podemos ayudarte con el desmontaje de tu aire acondicionado. El costo para de… | parcial | La respuesta menciona el precio correcto y el servicio de desmontaje, pero el enlace proporcionado no es exactamente el mismo que se esperaba. |
| 13 | `¿Hacen desinstalación de split?` | Igual que caso #12: identifica como Desmontaje Aire Acondicionado, informa preci… | ¡Hola! Soy el asistente de Collazo ⚡️   Sí, realizamos el desmontaje de aires acondicionados tipo sp… | parcial | La respuesta menciona el servicio de desmontaje de aires acondicionados y ofrece un enlace para reservar, pero no informa sobre los precios, lo cual es un elemento clave requerido. |
| 14 | `Mi calefón no prende, ¿me pueden ayudar?` | Identifica como Reparación Calefón. Indica que necesita visita técnica para coti… | [SEGUIMIENTO]   Claro, podemos ayudarte con eso. Parece que necesitas una reparación de calefón. Te … | true | La respuesta del agente identifica correctamente la necesidad de reparación del calefón, sugiere una visita técnica y proporciona el enlace correspondiente. |
| 15 | `El aire está roto, no enfría bien` | Identifica como Reparación Aire Acondicionado. Indica que necesita visita técnic… | [SEGUIMIENTO]   Parece que necesitas una reparación para tu aire acondicionado. Te recomiendo que re… | true | La respuesta del agente identifica correctamente la necesidad de reparación del aire acondicionado, sugiere una visita técnica y proporciona el enlace requerido. |
| 16 | `¿Hacen limpieza de aires?` | Identifica como Mantenimiento Aire Acondicionado. Informa precio base $1800, men… | ¡Hola! Soy el asistente de Collazo ⚡️   Sí, realizamos mantenimiento de aires acondicionados, lo cua… | true | La respuesta del agente cubre todos los elementos clave requeridos, incluyendo el precio base, la mención de materiales adicionales y el enlace para reservar el servicio, sin incluir preguntas adicionales. |
| 17 | `Quiero hacer el service del aire` | Igual que caso #16: Mantenimiento, precio $1800, link de reserva. Sin preguntas … | [SEGUIMIENTO]  ¡Perfecto! El mantenimiento de aire acondicionado tiene un precio base de **$1800**. … | true | La respuesta del agente incluye el precio del mantenimiento, un enlace para la reserva y no presenta preguntas previas, cumpliendo con el comportamiento esperado. |
| 18 | `Necesito que me coloquen un split` | Identifica como Instalación Aire Acondicionado. Informa precios por BTU. Envía l… | [SEGUIMIENTO]  ¡Claro! Podemos ayudarte con la instalación de tu aire acondicionado split. Aquí te d… | parcial | La respuesta incluye el enlace y menciona la instalación de aire acondicionado, pero no informa sobre los precios por BTU. |
| 19 | `¿Pueden venir a revisar el tablero eléctrico?` | Identifica como Servicio Eléctrico. Envía link: cal.com/collazo-servicio/servici… | [SEGUIMIENTO]   Claro, podemos ayudarte con eso. Ofrecemos servicios eléctricos que incluyen la revi… | true | La respuesta del agente identifica correctamente el servicio eléctrico y proporciona el enlace solicitado. |
| 20 | `Se me cortó la luz en una habitación` | Identifica como Servicio Eléctrico. Envía link: cal.com/collazo-servicio/servici… | [SEGUIMIENTO]   Parece que necesitas un servicio eléctrico. Podemos ayudarte con reparaciones e inst… | true | La respuesta del agente identifica correctamente el servicio eléctrico y proporciona el enlace solicitado. |
| 21 | `¿Instalan calefones a gas?` | Aclara que solo instalan calefones eléctricos (no a gas). Tono amable. | Hola! Soy el asistente de Collazo ⚡️   Actualmente, solo instalamos calefones eléctricos. Si necesit… | true | La respuesta del agente aclara que solo instalan calefones eléctricos y mantiene un tono amable al ofrecer asistencia. |
| 1 | `Hola` | Saludo con "Hola! Soy el asistente de Collazo ⚡️ En qué puedo ayudarte?" | Hola! Soy el asistente de Collazo ⚡️   ¿En qué puedo ayudarte? | true | La respuesta real cubre todos los elementos clave requeridos y mantiene un tono amigable y útil. |
| 2 | `¿Cuánto sale el mantenimiento del aire?` | Informa precio base $1800 + aclara posibles materiales adicionales + envía link … | El mantenimiento del aire acondicionado tiene un precio base de **$1800**. Es posible que se requier… | true | La respuesta del agente incluye el precio base, aclara sobre materiales adicionales y proporciona el enlace para reservar el servicio, cumpliendo con todos los elementos requeridos. |
| 3 | `¿Hacen instalación de calefón?` | Confirma que sí, informa precio base $1900 (30–60 lts), menciona +$900 si hay re… | ¡Hola! Sí, realizamos la instalación de calefones eléctricos. El precio base para la instalación de … | true | La respuesta del agente cubre todos los elementos clave requeridos y mantiene un tono adecuado. |
| 4 | `¿Cuánto sale reparar un calefón?` | Indica que no se puede saber el costo sin evaluar el problema y que es necesaria… | Para poder cotizar la reparación de un calefón, es necesario realizar una visita técnica para evalua… | parcial | La respuesta menciona la necesidad de una visita técnica, pero no incluye el link de reparación del calefón. |
| 5 | `¿Trabajan los domingos?` | Indica que no realizan servicios los domingos. Horarios: lunes a viernes 9–19, s… | Hola! Soy el asistente de Collazo ⚡️   No, no realizamos servicios los domingos. Nuestros horarios d… | true | La respuesta del agente cubre todos los elementos clave requeridos y mantiene un tono amigable y útil. |
| 6 | `¿Llegan a Solymar?` | Confirma que sí, Solymar está dentro de la zona de cobertura (Ciudad de la Costa… | ¡Hola! Soy el asistente de Collazo ⚡️   Sí, cubrimos Solymar. ¿En qué puedo ayudarte hoy? | true | La respuesta confirma que Solymar está cubierto y mantiene un tono amigable y útil. |
| 7 | `¿Llegan a Salto?` | No confirma ni niega. Pregunta en qué ciudad o zona general se encuentra para co… | Hola! Soy el asistente de Collazo ⚡️   ¿En qué ciudad o zona general se encuentra esa dirección? | true | La respuesta del agente pregunta en qué ciudad o zona general se encuentra la dirección, cumpliendo con el comportamiento esperado de no confirmar ni negar y solicitando información adicional. |
| 8 | `¿Qué medios de pago aceptan?` | Efectivo, transferencia bancaria y Mercado Pago (tarjetas vía MP). Sin POS. Fact… | Aceptamos los siguientes métodos de pago:  - **Efectivo** - **Transferencia bancaria** - **Mercado P… | true | La respuesta del agente cubre todos los métodos de pago requeridos y menciona la facturación electrónica, cumpliendo con el comportamiento esperado. |
| 9 | `Quiero arreglar mi lavarropas` | Aclara amablemente que solo trabajan con aires acondicionados, calefones y elect… | Hola! Soy el asistente de Collazo ⚡️   Lamentablemente, no ofrecemos servicios de reparación para la… | true | La respuesta del agente aclara amablemente que solo trabajan con aires acondicionados, calefones y electricidad, cumpliendo con el comportamiento esperado. |

---

## Resumen

| Resultado | Cantidad |
|-----------|----------|
| true | 19 |
| false | 0 |
| parcial | 4 |
| error | 0 |
| manual-only | 0 |

### Casos fallidos

- **#12:** La respuesta menciona el precio correcto y el servicio de desmontaje, pero el enlace proporcionado no es exactamente el mismo que se esperaba.
- **#13:** La respuesta menciona el servicio de desmontaje de aires acondicionados y ofrece un enlace para reservar, pero no informa sobre los precios, lo cual es un elemento clave requerido.
- **#18:** La respuesta incluye el enlace y menciona la instalación de aire acondicionado, pero no informa sobre los precios por BTU.
- **#4:** La respuesta menciona la necesidad de una visita técnica, pero no incluye el link de reparación del calefón.

---

## Apéndice: Respuestas Completas

### Caso #22
**Mensaje:** ¿Llegan a Villa García?
**Respuesta:**
Hola! Soy el asistente de Collazo ⚡️  
Sí, cubrimos Villa García para nuestros servicios de aires acondicionados, calefones y electricidad. ¿En qué puedo ayudarte hoy?

### Caso #23
**Mensaje:** Estoy en ruta 8 km 19, ¿hacen instalaciones ahí?
**Respuesta:**
¡Hola! Sí, cubrimos la zona de Villa García, que incluye Ruta 8 km 19. Podemos ayudarte con la instalación. ¿Estás interesado en instalar un aire acondicionado o un calefón?

### Caso #10
**Mensaje:** ¿Hacen desinstalación de calefón?
**Respuesta:**
Hola! Soy el asistente de Collazo ⚡️  
Sí, realizamos desinstalación de calefones. ¿Estás interesado en retirar un calefón viejo para instalar uno nuevo, o solo necesitas que lo retiremos?

### Caso #11
**Mensaje:** ¿Pueden sacar un calefón que tengo instalado?
**Respuesta:**
¡Hola! Soy el asistente de Collazo ⚡️  
¿Estás interesado en retirar el calefón porque vas a instalar uno nuevo, o simplemente deseas que lo quitemos? Esto nos ayudará a entender mejor cómo podemos asistirte.

### Caso #12
**Mensaje:** Quiero que me quiten el aire acondicionado
**Respuesta:**
[SEGUIMIENTO]  
Claro, podemos ayudarte con el desmontaje de tu aire acondicionado. El costo para desmontar un aire acondicionado de 9000, 12000 o 18000 BTU es de **$1800**, y para uno de 24000 BTU es de **$2000**. 

Podés reservar el servicio de desmontaje a través del siguiente enlace:  
cal.com/collazo-servicio/desmontaje-aire

Recordá que vas a poder elegir el día y horario disponible. Si tenés alguna otra consulta, no dudes en decírmelo.

### Caso #13
**Mensaje:** ¿Hacen desinstalación de split?
**Respuesta:**
¡Hola! Soy el asistente de Collazo ⚡️  
Sí, realizamos el desmontaje de aires acondicionados tipo split. Si deseas avanzar con la reserva, te puedo enviar el enlace para que elijas el día y horario que más te convenga.

### Caso #14
**Mensaje:** Mi calefón no prende, ¿me pueden ayudar?
**Respuesta:**
[SEGUIMIENTO]  
Claro, podemos ayudarte con eso. Parece que necesitas una reparación de calefón. Te recomiendo que reserves una visita técnica para que podamos evaluar el problema y ofrecerte una solución. Podés reservar el servicio de reparación de calefón en el siguiente enlace:  

cal.com/collazo-servicio/reparacion-calefon

Si tenés alguna otra consulta, no dudes en decírmelo.

### Caso #15
**Mensaje:** El aire está roto, no enfría bien
**Respuesta:**
[SEGUIMIENTO]  
Parece que necesitas una reparación para tu aire acondicionado. Te recomiendo que reserves una visita técnica para que podamos evaluar y solucionar el problema. Podés hacerlo a través del siguiente enlace:  

cal.com/collazo-servicio/reparacion-aire-acondicionado  

Si tenés alguna otra consulta, no dudes en decírmelo.

### Caso #16
**Mensaje:** ¿Hacen limpieza de aires?
**Respuesta:**
¡Hola! Soy el asistente de Collazo ⚡️  
Sí, realizamos mantenimiento de aires acondicionados, lo cual incluye la limpieza. El precio base es de **$1800** y puede requerir materiales adicionales que se informan en la visita. Podés reservar el servicio a través del siguiente enlace:  
cal.com/collazo-servicio/mantenimiento-aire-acondicionado

Si tenés alguna otra consulta, no dudes en preguntar.

### Caso #17
**Mensaje:** Quiero hacer el service del aire
**Respuesta:**
[SEGUIMIENTO]

¡Perfecto! El mantenimiento de aire acondicionado tiene un precio base de **$1800**. Puede requerir materiales adicionales, que se informan en la visita. Podés reservar el servicio en el siguiente enlace:  
cal.com/collazo-servicio/mantenimiento-aire-acondicionado

Ahí podrás elegir el día y horario que te convenga. Si tenés alguna otra consulta, no dudes en preguntar.

### Caso #18
**Mensaje:** Necesito que me coloquen un split
**Respuesta:**
[SEGUIMIENTO]

¡Claro! Podemos ayudarte con la instalación de tu aire acondicionado split. Aquí te dejo el enlace para que puedas reservar el servicio de instalación de aire acondicionado:  
cal.com/collazo-servicio/instalacion-aire

Podrás elegir el día y horario que mejor te convenga. Si tienes alguna otra consulta, no dudes en decírmelo.

### Caso #19
**Mensaje:** ¿Pueden venir a revisar el tablero eléctrico?
**Respuesta:**
[SEGUIMIENTO]  
Claro, podemos ayudarte con eso. Ofrecemos servicios eléctricos que incluyen la revisión y reparación de tableros eléctricos. Para proceder, te recomiendo reservar una visita técnica a través del siguiente enlace:  

cal.com/collazo-servicio/servicio-electrico  

Podrás elegir el día y horario que te convenga dentro de nuestra disponibilidad.

### Caso #20
**Mensaje:** Se me cortó la luz en una habitación
**Respuesta:**
[SEGUIMIENTO]  
Parece que necesitas un servicio eléctrico. Podemos ayudarte con reparaciones e instalaciones eléctricas. Te recomiendo reservar una visita técnica para que un profesional pueda evaluar y solucionar el problema. Podés hacerlo a través del siguiente enlace:  

cal.com/collazo-servicio/servicio-electrico

Si tenés alguna otra consulta, no dudes en decírmelo.

### Caso #21
**Mensaje:** ¿Instalan calefones a gas?
**Respuesta:**
Hola! Soy el asistente de Collazo ⚡️  
Actualmente, solo instalamos calefones eléctricos. Si necesitas ayuda con la instalación de un calefón eléctrico, estaré encantado de asistirte. ¿Te gustaría reservar un servicio de instalación?

### Caso #1
**Mensaje:** Hola
**Respuesta:**
Hola! Soy el asistente de Collazo ⚡️  
¿En qué puedo ayudarte?

### Caso #2
**Mensaje:** ¿Cuánto sale el mantenimiento del aire?
**Respuesta:**
El mantenimiento del aire acondicionado tiene un precio base de **$1800**. Es posible que se requieran materiales o trabajos adicionales, los cuales se informan en el momento de la visita. Podés reservar el servicio de mantenimiento a través del siguiente enlace:  
cal.com/collazo-servicio/mantenimiento-aire-acondicionado

Si tenés alguna otra consulta, no dudes en preguntar.

### Caso #3
**Mensaje:** ¿Hacen instalación de calefón?
**Respuesta:**
¡Hola! Sí, realizamos la instalación de calefones eléctricos. El precio base para la instalación de un calefón de 30 a 60 litros es de **$1900**. Si necesitas retirar un tanque viejo, hay un costo adicional de **$900**. 

Si deseas avanzar con la reserva, podés hacerlo a través del siguiente enlace:  
cal.com/collazo-servicio/instalacion-calefon

Podrás elegir el día y horario que mejor te convenga. Si tenés alguna otra consulta, no dudes en preguntar.

### Caso #4
**Mensaje:** ¿Cuánto sale reparar un calefón?
**Respuesta:**
Para poder cotizar la reparación de un calefón, es necesario realizar una visita técnica para evaluar el problema específico. Si te interesa, puedo ayudarte a reservar una visita técnica para que uno de nuestros especialistas revise tu calefón. ¿Te gustaría proceder con la reserva?

### Caso #5
**Mensaje:** ¿Trabajan los domingos?
**Respuesta:**
Hola! Soy el asistente de Collazo ⚡️  
No, no realizamos servicios los domingos. Nuestros horarios de trabajo son de lunes a viernes de 9:00 a 19:00 y los sábados de 9:00 a 13:00. ¿Hay algo más en lo que pueda ayudarte?

### Caso #6
**Mensaje:** ¿Llegan a Solymar?
**Respuesta:**
¡Hola! Soy el asistente de Collazo ⚡️  
Sí, cubrimos Solymar. ¿En qué puedo ayudarte hoy?

### Caso #7
**Mensaje:** ¿Llegan a Salto?
**Respuesta:**
Hola! Soy el asistente de Collazo ⚡️  
¿En qué ciudad o zona general se encuentra esa dirección?

### Caso #8
**Mensaje:** ¿Qué medios de pago aceptan?
**Respuesta:**
Aceptamos los siguientes métodos de pago:

- **Efectivo**
- **Transferencia bancaria**
- **Mercado Pago**

A través de Mercado Pago, también aceptamos tarjetas, pero recomendamos consultar directamente en Mercado Pago si su tarjeta está habilitada. No contamos con POS, pero sí realizamos facturación electrónica. Si tenés alguna otra consulta, no dudes en preguntar.

### Caso #9
**Mensaje:** Quiero arreglar mi lavarropas
**Respuesta:**
Hola! Soy el asistente de Collazo ⚡️  
Lamentablemente, no ofrecemos servicios de reparación para lavarropas. Nos especializamos en aires acondicionados, calefones y servicios eléctricos. Si necesitas ayuda con alguno de estos equipos, estaré encantado de asistirte.
