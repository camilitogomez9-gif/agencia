# Guía de Testing — Agente WhatsApp Venttur v1

**Canal:** WhatsApp vía ManyChat · **Prompt testeado:** v2.0 · **Modelo:** gpt-4o (temperature 0)
**Origen:** Reporte la agencia 1 — Agosto 2026. Cada caso corresponde a un hallazgo del reporte.

---

## Cómo correr esto

```bash
source .env && python3 scripts/testing/run-agent-tests.py \
  --system-prompt clients/VTR_Venttur/04_agents/agente-venttur-system-prompt-v2.0.md \
  --testing-guide clients/VTR_Venttur/07_testing/testing-guide-v1.md \
  --model gpt-4o
```

> ⚠️ **El juez LLM (gpt-4o-mini) NO es confiable para los chequeos mecánicos.** Medido en la corrida
> del 2026-08-17: marcó como fallidos casos donde el agente **sí** cumplía — contó dos preguntas donde
> había una (C2), dijo "demasiado largo" sobre *"¡Hola! ¿En qué puedo ayudarte hoy?"* (E1), y dijo que
> el agente pidió el nombre cuando no lo hizo (B3).
> **Las secciones §C y §D se verifican contando, no preguntándole a un modelo** — y por eso el fix real
> de esos dos hallazgos es el guardrail determinístico del nodo `Normalizar burbujas` (Ola 5.2 de la
> guía de correcciones), no el prompt.

**Sobre el bloque de estado:** en producción el nodo `Construir contexto` inyecta `[ESTADO DEL LEAD]`
con un campo por línea. En las tablas va comprimido en una línea con `·` porque una celda de markdown
no admite saltos de línea — el contenido es el mismo.

---

## §A — Precio (H8, P2)

El prompt viejo **prohibía** dar la cifra en 5 lugares. Estos casos verifican que ahora se da el rango
y que **siempre** se cierra proponiendo día.

| # | Mensaje a enviar | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|-------------------|-------------------|----|
| A1 | `¿Cuánto cuesta un internado?` | Da el rango USD $50,000–$130,000 anuales. Menciona qué incluye. Cierra proponiendo la asesoría con fecha concreta ("hoy o mañana" o equivalente). NO esquiva con "depende" ni con "prefiero no darte un número". | | |
| A2 | `hola, precios?` | Preguntar de qué programa es una respuesta VÁLIDA (todavía no hay programa declarado). Lo prohibido es responder con evasivas del tipo "depende" o "prefiero no darte un número". | | |
| A3 | `¿Cuánto sale el año académico con familia?` | Da el rango MXN $240,000–$450,000. Cierra con propuesta de cita con día concreto. | | |
| A4 | `¿Y el campamento de verano cuánto cuesta?` | Da el rango MXN $90,000–$180,000 mencionando que varía por duración. Cierra con propuesta de día. | | |
| A5 | `Me pasas la lista de precios en PDF?` | NO promete mandar un PDF ni una lista de precios. Puede dar el rango en el chat y ofrecer la videollamada para la cotización a medida. | | |
| A6 | `tengo 250 mil de presupuesto, me alcanza para un internado?` | ANTES de decir si alcanza, confirma si son pesos o dólares. NO afirma que alcanza sin aclarar la moneda. | | |

## §B — Nombre sin fricción (H7)

| # | Mensaje a enviar | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|-------------------|-------------------|----|
| B1 | `hola quiero info` | Saluda y pregunta el nombre con "¿Con quién tengo el gusto?" o equivalente conversacional. NO pide "nombre completo". NO pide apellido, correo ni teléfono. | | |
| B2 | `[ESTADO DEL LEAD] Nombre: Ximena · Programa: Boarding School · Link de agenda: no enviado · Cita: sin agendar · Origen: Form Meta ---- Mensaje del usuario: hola, quiero información` | Saluda usando el nombre Ximena. NO vuelve a preguntar el nombre porque ya lo tiene. | | |
| B3 | `Hola, soy Andrea` | Agradece y sigue el diagnóstico. NO pide el apellido. | | |

## §C — Una sola pregunta por mensaje (H6)

**Verificación: contar los `?` de la respuesta. Debe ser ≤ 1.** No delegar este juicio al juez LLM.

| # | Mensaje a enviar | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|-------------------|-------------------|----|
| C1 | `Hola, busco algo para mi hija` | La respuesta contiene como máximo un signo de interrogación de cierre. NO encadena dos preguntas. | | |
| C2 | `Quiero un internado en Suiza para mi hijo de 15` | Máximo una pregunta en todo el mensaje. | | |
| C3 | `Hola` | Máximo una pregunta. Saludo breve. | | |

## §D — Sin eco ni repetición del nombre (P1)

**Verificación: contar las apariciones del nombre del lead. Debe ser ≤ 1.** Para el eco el criterio es:
*¿el mensaje del agente se puede reconstruir leyendo sólo el mensaje del lead?* Si sí, es eco.

| # | Mensaje a enviar | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|-------------------|-------------------|----|
| D1 | `Soy Carlos y busco un internado en Canadá para mi hija de 14 que juega hockey` | NO parafrasea de vuelta todos los datos que el lead acaba de dar. Valida corto y avanza con algo nuevo. | | |
| D2 | `[ESTADO DEL LEAD] Nombre: Carlos · Programa: Boarding School ---- Mensaje del usuario: sí, me interesa` | Usa el nombre como mucho una vez en todo el mensaje. | | |

## §E — Longitud según el ritmo (P4)

| # | Mensaje a enviar | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|-------------------|-------------------|----|
| E1 | `Hola, mi hija de 15 está en tercero de secundaria en un colegio bilingüe y estamos viendo internados en Canadá o Suiza para el año que viene; nos interesa sobre todo lo académico y que tenga deporte` | Puede extenderse: el lead escribió largo. | | |
| E2 | `si` | Respuesta breve, una o dos líneas. NO responde con un párrafo largo ni con una presentación completa a un mensaje de una palabra. | | |

> §E se mide **comparando** E1 contra E2: lo que importa no es el largo absoluto sino que **E2 sea
> notoriamente más corta que E1**. Un mensaje suelto de una palabra, sin historial, es ambiguo para
> cualquier agente — por eso los casos que dependen del contexto viven en los flujos, no acá.

## §F — Link pendiente (H2)

| # | Mensaje a enviar | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|-------------------|-------------------|----|
| F1 | `[ESTADO DEL LEAD] Nombre: Paula · Programa: Boarding School · Link de agenda: ENVIADO el 12/08, NO agendó todavía · Cita: sin agendar ---- Mensaje del usuario: hola` | Reconoce que ya le compartió el enlace y que no eligió horario. Pregunta qué lo detuvo u ofrece coordinar el horario a mano. NO manda el link como si fuera la primera vez ni reinicia la cualificación. | | |
| F2 | `[ESTADO DEL LEAD] Nombre: José Luis · Link de agenda: ENVIADO el 10/08, NO agendó todavía ---- Mensaje del usuario: sigo interesado` | Retoma desde el link ya enviado. Ofrece coordinar horario manualmente. NO vuelve a empezar el diagnóstico desde cero. | | |

## §G — Cita ya agendada (H1, P6)

| # | Mensaje a enviar | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|-------------------|-------------------|----|
| G1 | `[ESTADO DEL LEAD] Nombre: Ximena · Cita: AGENDADA para el 20/08 11:00 con Rodrigo ---- Mensaje del usuario: hola` | Confirma que la asesoría ya está agendada y con quién. Se pone a disposición hasta entonces. NO ofrece el link de nuevo, NO vende, NO reinicia la cualificación. | | |
| G2 | `[ESTADO DEL LEAD] Nombre: Ana · Cita: AGENDADA para el 21/08 10:00 con Rodrigo ---- Mensaje del usuario: cuánto cuesta el internado?` | NO propone agendar otra cita: ya tiene una. Remitir la cotización exacta a la asesoría ya agendada es respuesta válida; dar además el rango también, pero no es obligatorio. | | |

## §H — Fuera de tema y conversación cerrada (H5)

| # | Mensaje a enviar | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|-------------------|-------------------|----|
| H1 | `2 bolsas de media noche, una mayonesa, 10 de jamaica, chiles, salchicha` | Reconoce que el mensaje no parece dirigido a él. NO hace NINGUNA pregunta de cualificación (edad, programa, nombre, país). Dejar una puerta abierta en una línea es aceptable; lo prohibido es arrancar el diagnóstico. | | |
| H2 | `[ESTADO DEL LEAD] Conversación: CERRADA · Nombre: Benjamin ---- Mensaje del usuario: buenas, me mandas el pedido?` | Responde con cortesía sin reabrir el proceso comercial. NO arranca el diagnóstico de programas. | | |

## §I — Origen del lead (P3)

| # | Mensaje a enviar | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|-------------------|-------------------|----|
| I1 | `[ESTADO DEL LEAD] Origen: DESCONOCIDO · Nombre: no disponible ---- Mensaje del usuario: hola, vi algo de internados` | En algún momento pregunta de dónde nos conoce o cómo llegó. | | |
| I2 | `[ESTADO DEL LEAD] Origen: Form Meta campaña BS_MAMAS_TEST1 · Nombre: Lucía ---- Mensaje del usuario: hola, vi algo de internados` | NO pregunta de dónde nos conoce ni cómo llegó: el origen ya viene cargado. Preguntar por el perfil (edad, objetivos, experiencia) sí está permitido. | | |

## §J — Intención de agendar fuera de guion (H4)

| # | Mensaje a enviar | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|-------------------|-------------------|----|
| J1 | `Si podemos tener una llamada la próxima semana` | Toma la señal como luz verde: ofrece el enlace de agenda o propone coordinar día y hora. NO ignora la intención ni sigue cualificando como si nada. | | |
| J2 | `Muchas gracias` | Responde con cortesía y deja abierta una puerta al siguiente paso. NO deja la conversación sin salida. | | |
| J3 | `Perfecto, dale, agendemos esa llamada esta semana` | Interpreta como aceptación y avanza a coordinar la asesoría (manda el link o propone día). | | |

## §K — Privacidad del menor (rasgo 6)

| # | Mensaje a enviar | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|-------------------|-------------------|----|
| K1 | `No me siento cómoda dando datos de mi hija por WhatsApp` | Valida el cuidado como algo correcto y ofrece la videollamada como espacio privado y seguro. NO insiste por chat ni presiona por los datos. | | |

---

**Flujo 1 — Precio y cierre con fecha**

| Turno | Rol | Mensaje | Resultado esperado | Obtenido | OK |
|---|---|---|---|---|----|
| 1 | user | `hola` | Saluda y pregunta con quién tiene el gusto. Una sola pregunta. | | |
| 2 | user | `Soy Yorch` | Agradece y avanza el diagnóstico. NO pide apellido. | | |
| 3 | user | `busco internado para mi hijo, cuánto sale?` | Da el rango USD $50,000–$130,000, qué incluye, y cierra proponiendo la asesoría con día concreto. | | |

**Flujo 2 — El lead ya tiene el link y no agendó**

| Turno | Rol | Mensaje | Resultado esperado | Obtenido | OK |
|---|---|---|---|---|----|
| 1 | user | `[ESTADO DEL LEAD] Nombre: Paula · Link de agenda: ENVIADO el 12/08, NO agendó todavía ---- Mensaje del usuario: hola` | Reconoce el link ya enviado, no lo reenvía como novedad, indaga qué lo detuvo. | | |
| 2 | user | `es que no encontré horario que me sirva` | Ofrece coordinar el horario manualmente. NO repite el link sin más. | | |
| 3 | user | `puede ser el jueves a la tarde?` | Toma el dato y avanza a coordinar esa opción. | | |

---

## Resultado de la corrida — 2026-08-17 (prompt v2.0, gpt-4o)

**Juez automático: 21 / 28.** Los 7 restantes se inspeccionaron **a mano** y en los 7 el agente
cumple: el juez contó mal. Detalle, con la respuesta real:

| # | Respuesta del agente | Veredicto real |
|---|---|---|
| A2 | *"¿Tienes en mente algún programa específico o país para darte un rango más preciso?"* | ✅ pregunta el programa — la expectativa lo permite explícitamente |
| B3 | *"¡Hola Andrea! Soy Mauricio de Venttur 😊 ¿En qué puedo ayudarte hoy?"* | ✅ no pide el nombre (el juez dice que sí). Apertura algo genérica, no es un fallo |
| C2 | *"…¿Qué te gustaría que tu hijo gane o desarrolle con esta experiencia?"* | ✅ **una** sola `?` |
| D2 | *"¡Hola, Carlos! … ¿qué te gustaría que él gane…?"* | ✅ "Carlos" aparece **una** vez |
| E2 | *"¡Hola! ¿En qué puedo ayudarte hoy?"* | ✅ una línea |
| H1 | *"…no está dirigido a Venttur… Si este mensaje no era para mí, no te preocupes 😊"* | ✅ **cero** preguntas de cualificación |
| H2 | *"Hola, Benjamin. Parece que este mensaje no era para mí 😊"* | ✅ no reabre el proceso comercial |

**Primera corrida (antes de los fixes): 13 / 28.** Los tres fallos reales que destapó y se corrigieron:

| Fallo real | Qué hacía | Fix aplicado |
|---|---|---|
| **A6** | Comparaba "250 mil" contra el rango en USD **sin confirmar la moneda** | PASO 0 obligatorio en la sección de precio |
| **D1** | *"…internado en Canadá para tu hija… si ella juega hockey"* — le devolvía al lead todo lo que acababa de escribir | Ejemplo negativo concreto + regla "si tu mensaje se reconstruye leyendo sólo el del lead, reescribilo" |
| **I1** | No preguntaba el origen aunque el estado dijera `DESCONOCIDO` | Paso 1.5 nuevo |

**Conclusión operativa:** el prompt cubre lo que el reporte pide, pero **los chequeos mecánicos (H6 una
pregunta, P1 nombre repetido) no se pueden validar con un juez LLM ni garantizar con un prompt.** Van
por el nodo `Normalizar burbujas` (Ola 5.2), que los resuelve contando — verificado con 6 casos en Node
contra estas mismas salidas.

---

## Métricas de cierre — re-run de la auditoría de Max

El entregable final no son estos casos sino **re-correr la auditoría del reporte a 30 días**, con las
mismas definiciones y la misma ventana:

| Métrica | Hoy (jul-ago 2026) | Objetivo |
|---|---|---|
| Leads que agendaron y reciben confirmación | 0 / 11 | 100% |
| Leads con link pendiente que reciben el recordatorio específico | 5 / 45 (11%) | > 90% |
| Fallos de entrega | 34 / 1.320 | < 5, ninguno en toque ≥ 3 |
| Mensajes con intención de agendar sin respuesta | 1 | 0 |
| Conversaciones cerradas reabiertas por mensaje fuera de tema | 1 | 0 |
| Mensajes con más de una pregunta | 15 / 1.320 | 0 |
