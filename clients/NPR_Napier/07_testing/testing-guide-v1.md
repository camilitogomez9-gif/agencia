# Guía de Testing — Agente Admin Napier v1

**Canal:** WhatsApp (admin)
**Prompt versión testeada:** v1.1
**Estado:** Pendiente

---

## Instrucciones de uso

1. Enviar cada mensaje como si fueras el administrador del salón
2. Pegar la respuesta exacta del agente en "Resultado obtenido"
3. Marcar OK como `true`, `false` o `parcial`
4. Agregar notas al pie si hay patrones sistémicos

---

## Casos simples

| # | Mensaje a enviar | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|-------------------|-------------------|----|
| 1 | `Agendar cita para mañana a las 10:40.\n\nStaff: Alan\nCliente: Wilfrido Estrella\nNúmero: +18494470823` | Crea la cita directamente sin preguntar nada. Confirma con fecha, hora y staff. NO pregunta quién es el cliente ni pide confirmación. | | |
| 2 | `Agendar cita para el sábado a las 8:00.\n\nStaff: Napier\nCliente: Juan Pérez\nNúmero: +18091234567` | Crea la cita directamente. Confirma. NO pregunta "¿eres tú el cliente?". | | |
| 3 | `Agendar cita para el viernes a las 10:40.\n\nStaff: Wilson\nCliente: Carlos Méndez\nNúmero: +18494470823` | Wilfrido Estrella ya tiene cita futura. El agente NO debe bloquearlo ni preguntar. Debe responder "Procede con la creación" internamente y confirmar la nueva cita creada. | | |
| 4 | `Agendar cita para mañana a las 1:20.\n\nStaff: Alan\nCliente: Pedro Soto\nNúmero: +18497654321` | La hora 1:20 pm cae en horario de almuerzo. El agente delega a Subagente Calendario (Operación A) para obtener disponibilidad real. NO sugiere slots de su lista sin verificar. | | |
| 5 | `Agendar cita para mañana a las 11:05.\n\nStaff: Alan\nCliente: Luis Rivera\nNúmero: +18491112222` | 11:05 no es slot válido para Alan (40 min). El agente delega a Subagente Calendario para obtener opciones reales. NO responde con slots de la lista sin verificar. | | |
| 6 | `Agendar cita para el lunes a las 9:00.\n\nStaff: Napier\nCliente: Mario González\nNúmero: +18493334444` | Lunes es día cerrado. El agente NO agenda y ofrece días disponibles. | | |
| 7 | `Cancelar cita de +18494470823` | El agente consulta la cita futura del cliente, muestra los datos y pide confirmación: "Responde: sí, cancela." | | |
| 8 | `Ver cita de +18491234567` | El agente consulta y devuelve fecha, hora y staff de la cita futura. Si no hay cita, informa. | | |

---

## Flujos conversacionales

---

### Flujo 1: Agendar cita completa — cliente nuevo

**Objetivo:** Verificar que el agente usa el nombre del mensaje del admin (no pregunta) y crea sin confirmación

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Admin | `Agendar cita para el jueves a las 9:20.\n\nStaff: Wilson\nCliente: Roberto Almonte\nNúmero: +18095557777` | — | | |
| 2 | Agente | — | Consulta CRM por +18095557777. Al no encontrarlo, usa "Roberto Almonte" del mensaje para crearlo. NO pregunta el nombre. Luego crea la cita. Confirma con fecha y hora. | | |

---

### Flujo 2: Múltiples citas para el mismo cliente

**Objetivo:** El admin puede crear varias citas para el mismo cliente sin bloqueo

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Admin | `Agendar cita para el martes a las 8:00.\n\nStaff: Alan\nCliente: Wilfrido Estrella\nNúmero: +18494470823` | Crea la primera cita. Confirma. | | |
| 2 | Admin | `Agendar cita para el miércoles a las 10:40.\n\nStaff: Alan\nCliente: Wilfrido Estrella\nNúmero: +18494470823` | El Subagente informa que ya existe cita futura. El Admin responde "Procede con la creación de todas formas." Se crea la segunda cita. El admin NO ve mensajes sobre la cita existente. | | |

---

### Flujo 3: Cancelar cita — con confirmación

**Objetivo:** La cancelación requiere confirmación explícita del admin

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Admin | `Cancelar cita de +18094440001` | — | | |
| 2 | Agente | — | Muestra la cita encontrada (fecha, hora, staff). Pide: "Responde: sí, cancela." NO cancela aún. | | |
| 3 | Admin | `sí, cancela` | — | | |
| 4 | Agente | — | Cancela la cita. Confirma cancelación con fecha y hora. | | |

---

### Flujo 4: Slot inválido → opciones reales

**Objetivo:** Cuando la hora no es slot válido, el agente NO sugiere de su lista — delega a Subagente

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Admin | `Agendar cita para el viernes a las 11:00.\n\nStaff: Alan\nCliente: Felipe Castro\nNúmero: +18093210987` | — | | |
| 2 | Agente | — | 11:00 no es slot válido para Alan. El agente delega a Subagente Calendario para obtener slots disponibles reales. Presenta máximo 3 opciones concretas con horario y verificadas en Calendar. | | |
| 3 | Admin | Elige una de las opciones | — | | |
| 4 | Agente | — | Crea la cita inmediatamente. Confirma. NO pide "¿confirmas?". | | |

---

## Notas adicionales

_Completar al finalizar el testing._

- Verificar que el teléfono +18494470823 se use en formato E.164 sin espacios ni paréntesis cuando se pasa al CRM y Subagente.
- Si hay un slot exacto en el mensaje del admin → Caso 1 (crear directo). Si la hora no existe en la lista → Caso 2 (disponibilidad real).
- Los casos 3 y 4 de simples son los más críticos: miden el bug de bloqueo de múltiples citas y el bug de sugerencia sin verificar.

---

> Guía de testing v1 para Agente Admin Napier. Cubre cambios de prompt v1.1: admin vs cliente, múltiples citas, slots inválidos → Subagente, eliminación de reagendar.
