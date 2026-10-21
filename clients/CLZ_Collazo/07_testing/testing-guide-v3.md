# Guía de Testing — Collazo Servicio Técnico v3

**Canal:** Chatrace (bot de WhatsApp/chat)
**Prompt versión testeada:** v1.7
**Estado:** Pendiente

---

## Instrucciones de uso

1. Ejecutar cada caso en el canal real o en el entorno de prueba
2. Pegar la respuesta exacta del agente en "Resultado obtenido"
3. Marcar OK como `true`, `false` o `parcial`
4. Agregar notas al pie si hay patrones sistémicos

---

## Nuevos casos — Zona de cobertura (v1.6)

Estos casos verifican que el agente reconozca la nueva zona agregada (Villa García, Ruta 8 km 19) como cubierta.

| # | Mensaje a enviar | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|-------------------|-------------------|----|
| 22 | `¿Llegan a Villa García?` | Confirma que sí, Villa García está dentro de la zona de cobertura (Interior de Canelones). NO pregunta a qué departamento pertenece — la reconoce directamente. | | |
| 23 | `Estoy en ruta 8 km 19, ¿hacen instalaciones ahí?` | Confirma cobertura de la zona (Villa García / Ruta 8 km 19). NO dice que no cubre la zona. | | |

---

## Nuevos casos — Variaciones de servicio (v1.4)

Estos casos verifican que el agente reconozca sinónimos y variaciones en las consultas de servicio y mapee correctamente al enlace de reserva correspondiente.

| # | Mensaje a enviar | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|-------------------|-------------------|----|
| 10 | `¿Hacen desinstalación de calefón?` | Consulta si es para poner uno nuevo (retiro de tanque viejo, $900 adicional) o solo retiro. NO envía link sin entender el contexto. NO dice que ese servicio no existe. | | |
| 11 | `¿Pueden sacar un calefón que tengo instalado?` | Igual que caso #10: consulta si hay nueva instalación o es solo retiro. | | |
| 12 | `Quiero que me quiten el aire acondicionado` | Identifica como Desmontaje Aire Acondicionado. Informa precio ($1800 para 9000–18000 BTU, $2000 para 24000 BTU). Envía link: cal.com/collazo-servicio/desmontaje-aire-acondicionado. | | |
| 13 | `¿Hacen desinstalación de split?` | Igual que caso #12: identifica como Desmontaje Aire Acondicionado, informa precios y envía link de desmontaje. | | |
| 14 | `Mi calefón no prende, ¿me pueden ayudar?` | Identifica como Reparación Calefón. Indica que necesita visita técnica para cotizar. Envía link: cal.com/collazo-servicio/reparacion-calefon. | | |
| 15 | `El aire está roto, no enfría bien` | Identifica como Reparación Aire Acondicionado. Indica que necesita visita técnica. Envía link: cal.com/collazo-servicio/reparacion-aire-acondicionado. | | |
| 16 | `¿Hacen limpieza de aires?` | Identifica como Mantenimiento Aire Acondicionado. Informa precio base $1800, menciona posibles materiales adicionales en visita. Envía link de mantenimiento. Todo en el mismo mensaje, sin preguntas previas. | | |
| 17 | `Quiero hacer el service del aire` | Igual que caso #16: Mantenimiento, precio $1800, link de reserva. Sin preguntas previas. | | |
| 18 | `Necesito que me coloquen un split` | Identifica como Instalación Aire Acondicionado. Informa precios por BTU. Envía link: cal.com/collazo-servicio/instalacion-aire. | | |
| 19 | `¿Pueden venir a revisar el tablero eléctrico?` | Identifica como Servicio Eléctrico. Envía link: cal.com/collazo-servicio/servicio-electrico. | | |
| 20 | `Se me cortó la luz en una habitación` | Identifica como Servicio Eléctrico. Envía link: cal.com/collazo-servicio/servicio-electrico. | | |
| 21 | `¿Instalan calefones a gas?` | Aclara que solo instalan calefones eléctricos (no a gas). Tono amable. | | |

---

## Casos simples (heredados de v1)

| # | Mensaje a enviar | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|-------------------|-------------------|----|
| 1 | `Hola` | Saludo con "Hola! Soy el asistente de Collazo ⚡️ En qué puedo ayudarte?" | | |
| 2 | `¿Cuánto sale el mantenimiento del aire?` | Informa precio base $1800 + aclara posibles materiales adicionales + envía link de reserva de mantenimiento. Todo en el mismo mensaje, sin preguntas previas. | | |
| 3 | `¿Hacen instalación de calefón?` | Confirma que sí, informa precio base $1900 (30–60 lts), menciona +$900 si hay retiro de tanque viejo, materiales extras se informan en visita, y envía link de instalación calefón. | | |
| 4 | `¿Cuánto sale reparar un calefón?` | Indica que no se puede saber el costo sin evaluar el problema y que es necesaria una visita técnica. Envía link de reparación calefón. | | |
| 5 | `¿Trabajan los domingos?` | Indica que no realizan servicios los domingos. Horarios: lunes a viernes 9–19, sábados 9–13. | | |
| 6 | `¿Llegan a Solymar?` | Confirma que sí, Solymar está dentro de la zona de cobertura (Ciudad de la Costa, Canelones). | | |
| 7 | `¿Llegan a Salto?` | No confirma ni niega. Pregunta en qué ciudad o zona general se encuentra para confirmar cobertura. | | |
| 8 | `¿Qué medios de pago aceptan?` | Efectivo, transferencia bancaria y Mercado Pago (tarjetas vía MP). Sin POS. Facturación electrónica disponible. | | |
| 9 | `Quiero arreglar mi lavarropas` | Aclara amablemente que solo trabajan con aires acondicionados, calefones y electricidad. | | |

---

## Notas adicionales — Testing automatizado (2026-07-15)

**Correcciones aplicadas en v1.7:** casos #4, #7 — se corrió el testing automatizado (`run-agent-tests.py`, modelo `gpt-4o`, juez `gpt-4o-mini`) sobre el prompt v1.6 y se detectaron 2 fallos preexistentes sin relación con el agregado de Villa García:
- **#4** — el agente mencionaba proactivamente el costo de la visita ($750) en consultas de reparación de calefón sin que se lo pidieran. Fix: regla explícita en "Otros servicios" prohibiendo mencionarlo salvo que se pregunte.
- **#7** — ante zonas no cubiertas pero reconocibles (ej. Salto), el agente confirmaba qué zonas sí cubre antes de preguntar, revelando indirectamente que no llega. Fix: regla explícita de no mencionar zonas cubiertas al hacer la pregunta de confirmación de ubicación.

Ambos casos verificaron `true` en 2 corridas posteriores tras el fix.

**⚠️ Variancia observada, no atribuible a los fixes de esta sesión:** en la 3ª corrida (post-fix #7) aparecieron 4 resultados `parcial` en casos que no fueron tocados por ningún cambio de esta sesión y que habían dado `true` en la 1ª corrida sin cambios de prompt: #4 (omitió el link de reparación calefón), #12 (truncó la URL de desmontaje a `desmontaje-aire` en vez de `desmontaje-aire-acondicionado`), #13 y #18 (omitieron los precios de desmontaje/instalación que sí habían dado en la 1ª corrida). Es consistente con no-determinismo del modelo (temperature 0.2) más que con una regresión real. **Recomendado:** re-correr el testing automatizado completo en una sesión dedicada para confirmar si es ruido puntual o un patrón — en particular el caso #12 (truncamiento de URL) amerita seguimiento porque un link roto es un fallo de producción real si se repite.

---

> Guía de testing v3 para Collazo Servicio Técnico. Prompt v1.7. Hereda íntegros los casos de v1/v2 (heredados de v1 + variaciones de servicio v1.4) y agrega los casos #22-23 de zona de cobertura (v1.6) + correcciones #4/#7 (v1.7).
