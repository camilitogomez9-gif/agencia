# Guía de Testing — Collazo Servicio Técnico v1

**Canal:** Chatrace (bot de WhatsApp/chat)
**Prompt versión testeada:** v1.1
**Estado:** Pendiente

---

## Instrucciones de uso

1. Ejecutar cada caso en el canal real o en el entorno de prueba
2. Pegar la respuesta exacta del agente en "Resultado obtenido"
3. Marcar OK como `true`, `false` o `parcial`
4. Agregar notas al pie si hay patrones sistémicos

---

## Casos simples

| # | Mensaje a enviar | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|-------------------|-------------------|----|
| 1 | `Hola` | Saludo con "Hola! Soy el asistente de Collazo ⚡️ En qué puedo ayudarte?" | | |
| 2 | `¿Cuánto sale el mantenimiento del aire?` | Informa precio base $1800 + aclara posibles materiales adicionales + envía link de reserva de mantenimiento. Todo en el mismo mensaje, sin preguntas previas. | | |
| 3 | `¿Hacen instalación de calefón?` | Confirma que sí, informa precio base $1900 (30–60 lts), menciona +$900 si hay retiro de tanque viejo, materiales extras se informan en visita, y envía link de instalación calefón. | | |
| 4 | `¿Cuánto sale reparar un calefón?` | Indica que no se puede saber el costo sin evaluar el problema y que es necesaria una visita técnica. Envía link de reparación calefón. | | |
| 5 | `¿Trabajan los domingos?` | Indica que no realizan servicios los domingos. Horarios: Lunes a Viernes 9–19, Sábados 9–13. | | |
| 6 | `¿Llegan a Solymar?` | Confirma que sí, Solymar está dentro de la zona de cobertura (Ciudad de la Costa, Canelones). | | |
| 7 | `¿Llegan a Salto?` | No confirma ni niega. Pregunta en qué ciudad o zona general se encuentra para confirmar cobertura. | | |
| 8 | `¿Qué medios de pago aceptan?` | Efectivo, transferencia bancaria y Mercado Pago (tarjetas vía MP). Sin POS. Facturación electrónica disponible. | | |
| 9 | `Quiero arreglar mi lavarropas` | Aclara amablemente que solo trabajan con aires acondicionados, calefones y electricidad. | | |
| 10 | `¿Tienen garantía?` | Instalaciones: 1 año. Reparaciones: 6 meses. | | |

---

## Flujos conversacionales

---

### Flujo 1: Consulta de mantenimiento → reserva directa

**Objetivo:** Validar comportamiento proactivo — precio + link en el mismo turno, sin fricción.

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Hola, quiero hacer el mantenimiento del aire` | Saluda, informa precio base $1800, aclara posibles adicionales en visita, y envía link cal.com/collazo-servicio-tozuqm/mantenimiento-aire-acondicionado — todo en el mismo mensaje | | |
| 2 | Usuario | `¿Y cuánto tarda el mantenimiento?` | Responde la consulta de manera concisa (tiempo estimado si lo sabe, o indica que se informa en la visita) | | |
| 3 | Usuario | `Perfecto, voy a reservar` | Confirma que puede elegir día y horario disponible en el link ya enviado | | |

---

### Flujo 2: Instalación de calefón con retiro de tanque viejo

**Objetivo:** Validar que el agente informa correctamente el precio base + costo adicional de retiro.

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Quiero instalar un calefón nuevo, tengo uno viejo que sacar` | Informa precio base $1900 + retiro de tanque viejo $900 adicional + materiales extras se informan en visita + envía link de instalación calefón | | |
| 2 | Usuario | `¿El precio varía según la marca?` | Indica que el precio base aplica para la instalación estándar; cualquier material adicional se informa en el momento de la visita | | |
| 3 | Usuario | `Bien, ¿cómo reservo?` | Envía o recuerda el link de instalación calefón | | |

---

### Flujo 3: Instalación de aire acondicionado con consulta de ménsulas

**Objetivo:** Validar que informa precio base + ménsulas como adicional + link.

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `¿Cuánto sale instalar un aire de 12000 BTU?` | Precio base $3500. Menciona que el técnico puede requerir ménsulas (soportes) como costo adicional ($900 el par para esa potencia), y otros materiales se informan en la visita. | | |
| 2 | Usuario | `¿Las ménsulas son obligatorias?` | Explica que depende del caso, el técnico lo evalúa en la visita | | |
| 3 | Usuario | `Dale, quiero reservar` | Envía link de instalación de aire acondicionado | | |

---

### Flujo 4: Reparación de calefón — derivación simple

**Objetivo:** Validar que para reparación calefón solo envía el link sin dar precio (correcto: no hay precio base).

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Mi calefón no calienta bien, ¿pueden arreglarlo?` | Confirma que sí. Indica que el costo se determina en la visita. Envía link de reparación calefón. | | |
| 2 | Usuario | `¿Tienen idea de cuánto puede costar?` | Indica que sin evaluar no pueden dar un precio exacto, que la visita tiene costo $750 (solo si preguntan) | | |

---

### Flujo 5: Usuario fuera de horario o zona

**Objetivo:** Validar manejo de horarios y zonas no cubiertas.

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `¿Pueden venir el domingo a las 10?` | Indica que los domingos no realizan servicios. Sugiere coordinar de lunes a viernes 9–19 o sábados 9–13 mediante el link de reserva. | | |
| 2 | Usuario | `¿Y el sábado a las 14?` | Indica que los sábados solo trabajan hasta las 13 hs. | | |

---

### Flujo 6: Usuario que no puede acceder al link

**Objetivo:** Validar que activa la herramienta 'elevar' correctamente.

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `No puedo abrir el enlace que me mandaste` | Activa herramienta 'elevar' y avisa que un técnico se pondrá en contacto | | |

---

## Notas adicionales

_Completar al finalizar el testing con observaciones sistémicas: patrones de error,
comportamientos inesperados, sugerencias de mejora._

---

> Guía de testing v1 para Collazo Servicio Técnico. Prompt v1.1.
