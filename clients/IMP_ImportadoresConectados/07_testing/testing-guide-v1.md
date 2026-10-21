# Guía de Testing — Agente Importadores Conectados v1

**Canal:** Instagram DM / WhatsApp / Facebook
**Prompt versión testeada:** v1.3
**Estado:** Pendiente

---

## Instrucciones de uso

1. Ejecutar cada caso en el canal real o en el entorno de prueba (Telegram).
2. Pegar la respuesta exacta del agente en "Resultado obtenido".
3. Marcar OK como `true`, `false` o `parcial`.
4. Para los marcadores `[AUDIO:NOMBRE]`: validar que el agente los emite correctamente. Si el flow de ManyChat aún no está creado, el texto del audio debe llegar como mensaje normal (fallback funcional).
5. Agregar notas al pie si hay patrones sistémicos.

---

## Casos simples

Casos de un solo turno para validar comportamientos puntuales.

| # | Mensaje a enviar | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|-------------------|-------------------|----|
| 1 | `Hola` | Apertura con `[AUDIO:RESPUESTA_INICIAL]` + texto del audio. UNA sola pregunta ("¿hoy ya estás vendiendo algo o estás arrancando desde cero?"). No saluda como Diego ("yo te explico"), habla como Setter del equipo. | | |
| 2 | `Hola, quiero info del programa Importadores Conectados` | Apertura con `[AUDIO:RESPUESTA_INICIAL]`. NO empieza explicando el programa — primero indaga situación. | | |
| 3 | `¿Cuánto cuesta el programa?` (lead solo_precio) | Setter no da precio seco. Califica primero: una pregunta para entender situación. Luego presenta IC con precio USD 497 + módulos completos (importación, finanzas, marketing, ecommerce, ventas). | | |
| 4 | `¿Cuánto cuesta la mentoría 1:1?` | NO da precio fijo. Explica que la Mentoría 1:1 se cotiza según el caso y propone agendar una llamada con el equipo de Diego. Mensaje directivo: "Te paso el link de agenda". Etiqueta `[NOTIFICAR_AGENDA]`. | | |
| 5 | `¿Cuánto tiempo tengo acceso a las clases?` | Aclara: clases grabadas con acceso ILIMITADO. Acompañamiento, chat directo, clases en vivo y coaching: 3 meses. | | |
| 6 | `¿El programa es solo de importación?` | NO. Aclara módulos completos: importación + finanzas + marketing + ecommerce + ventas. Menciona clases en vivo con Diego y otros expertos. | | |
| 7 | `¿Qué incluye el programa?` (después de calificar) | Lista IC con: clases grabadas (acceso ilimitado), módulos completos, clases en vivo con Diego y expertos, 3 meses de acompañamiento, plantillas, planilla de compra, asesor IA. NO se queda solo en "clases grabadas". | | |
| 8 | `Garantizan que voy a ganar plata?` | Cierra con honestidad: no hay garantía mágica, lo que ofrecen es proceso y método. NO usa "garantizado", "fácil", "rápido". | | |
| 9 | `Quiero algo que me dé ingresos pasivos sin trabajar` | Descalifica limpiamente sin re-encauzar. Etiqueta `[NOTIFICAR_DESCALIFICADO]`. | | |
| 10 | `Es muy caro` | Usa `[AUDIO:OBJECION_PRECIO]`. NO baja el precio. Reencuadra al valor. | | |
| 11 | `Importar de China me da miedo, parece complicado` | Usa `[AUDIO:ROMPER_MIEDO]`. NO descarta el miedo, lo legitima y reencuadra. | | |
| 12 | `Tengo un negocio que ya funciona perfecto, quiero importar mis productos` | Deriva a Tecnoimport. Etiqueta `[NOTIFICAR_DERIVAR_TECNOIMPORT]`. NO ofrece IC ni Mentoría — el lead no necesita formación. | | |

---

## Flujos conversacionales

### Flujo 1: Lead desde cero — apertura a propuesta

**Objetivo:** validar el camino completo de un lead que arranca sin negocio hasta el envío del link de IC.
**Perfil del lead:** nunca_emprendo

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Hola, quiero más información del programa para aprender a importar` | — | | |
| 2 | Agente | — | `[AUDIO:RESPUESTA_INICIAL]` + texto. UNA sola pregunta: "¿hoy ya estás vendiendo algo o estás arrancando desde cero?" | | |
| 3 | Usuario | `Estoy por empezar de cero, no tengo negocio` | — | | |
| 4 | Agente | — | `[AUDIO:LEAD_DESDE_CERO]` + texto. Termina con UNA pregunta abierta ("¿ya tenías algo en mente o estás viendo opciones todavía?"). NO suelta info del programa todavía. | | |
| 5 | Usuario | `No, estoy viendo opciones. ¿Qué incluye el programa?` | — | | |
| 6 | Agente | — | Presenta IC con: precio USD 497, clases grabadas con acceso ILIMITADO, módulos completos (importación, finanzas, marketing, ecommerce, ventas), clases en vivo con Diego y otros expertos, 3 meses de acompañamiento, asesor IA. UNA pregunta de cierre ("¿te interesa que avancemos?"). | | |

**Rama A — Lead acepta y quiere arrancar:**

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 7 | Usuario | `Sí, quiero empezar` | — | | |
| 8 | Agente | — | Secuencia de envío de link: `[AUDIO:CIERRE_DIRECTO]` + texto del audio + `---` + texto corto contextual + LINK + `---` + `[NOTIFICAR_CIERRE]`. NO envía solo el link. | | |

**Rama B — Lead duda por precio:**

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 7 | Usuario | `Mmm USD 497 es bastante para mí ahora` | — | | |
| 8 | Agente | — | `[AUDIO:OBJECION_PRECIO]` + texto del audio. UNA pregunta de cierre. | | |
| 9 | Usuario | `Quiero arrancar igual` | — | | |
| 10 | Agente | — | Secuencia: `[AUDIO:CIERRE_REENCUADRE]` + `---` + texto + LINK + `---` + `[NOTIFICAR_CIERRE]`. | | |

---

### Flujo 2: Lead con negocio — busca margen

**Objetivo:** validar que el agente diferencia bien entre "negocio funcionando + quiere importar" (Tecnoimport) vs. "negocio con dificultad" (Asesoría/Mentoría).
**Perfil del lead:** ya_vende

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Hola, tengo un emprendimiento y quiero saber si los puedo ayudar` | — | | |
| 2 | Agente | — | `[AUDIO:RESPUESTA_INICIAL]`. UNA pregunta. | | |
| 3 | Usuario | `Ya vendo, tengo una marca de bijou` | — | | |
| 4 | Agente | — | `[AUDIO:LEAD_CON_NEGOCIO]` + texto del audio. UNA pregunta sobre productos / situación. | | |
| 5 | Usuario | `Vendo bien, lo que quiero es importar mis productos directo de China para mejorar margen` | — | | |
| 6 | Agente | — | DERIVA a Tecnoimport. Mensaje claro: "Para tu caso lo que te conviene es trabajar directo con Tecnoimport...". Etiqueta `[NOTIFICAR_DERIVAR_TECNOIMPORT]`. NO ofrece IC ni Mentoría. | | |

**Rama A — Lead con dificultad concreta:**

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 5 | Usuario | `La verdad estoy estancada, no entiendo bien mis números y no sé cómo escalar` | — | | |
| 6 | Agente | — | Ofrece Asesoría 1:1 con Diego (USD 100, 1 hora) como sesión de claridad O agendar llamada para evaluar Mentoría/Consultoría. NO deriva a Tecnoimport. | | |
| 7 | Usuario | `Me interesa la asesoría, pero quiero algo más profundo` | — | | |
| 8 | Agente | — | Propone llamada para evaluar Mentoría 1:1. NO da precio de Mentoría. Etiqueta `[NOTIFICAR_AGENDA]`. | | |

---

### Flujo 3: Lead muy verde — explorar antes de empujar

**Objetivo:** validar que el agente no empuja venta a un lead curioso sin claridad.
**Perfil del lead:** sin_clasificar

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Hola, estoy viendo nomás` | — | | |
| 2 | Agente | — | `[AUDIO:RESPUESTA_INICIAL]` o respuesta cálida. UNA pregunta. | | |
| 3 | Usuario | `No sé bien, capaz me interesa importar pero no estoy seguro` | — | | |
| 4 | Agente | — | NO empuja venta. Pregunta qué lo tiene dudando. UNA sola pregunta. | | |
| 5 | Usuario | `No sé si voy a poder, no tengo experiencia ni plata` | — | | |
| 6 | Agente | — | `[AUDIO:ROMPER_MIEDO]` o respuesta similar. Si después sigue sin claridad, ofrece Entrenamiento Gratuito. | | |

---

### Flujo 4: Cierre sin decisión — follow up

**Objetivo:** validar el cierre limpio cuando el lead pide tiempo después de explorar.
**Perfil del lead:** nunca_emprendo

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `(Después de toda la propuesta) Lo tengo que pensar` | — | | |
| 2 | Agente | — | Pregunta qué necesita pensar exactamente. UNA pregunta. | | |
| 3 | Usuario | `Necesito tiempo` | — | | |
| 4 | Agente | — | NO usa urgencia. NO insiste. Cierre con calidez: "Dale, tomá el tiempo que necesités. Cuando quieras retomarlo, acá estamos." Etiqueta `[NOTIFICAR_FOLLOWUP]`. NO termina con "estamos para acompañarte cuando quieras" como respuesta suave que suelta al lead. | | |

---

### Flujo 5: Lead pide agendamiento

**Objetivo:** validar que el agente lidera el agendamiento, no pregunta "¿querés que te pase el link?".
**Perfil del lead:** intento_fracaso

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Quiero hablar con alguien para que me asesore mi caso` | — | | |
| 2 | Agente | — | Mensaje DIRECTIVO: "Te paso el link de agenda: [LINK]". NO pregunta "¿querés que te pase el link?". Etiqueta `[NOTIFICAR_AGENDA]`. | | |

---

### Flujo 6: Lead caliente — quiere arrancar de una

**Objetivo:** validar que el agente no insiste con preguntas cuando el lead ya tiene decisión.
**Perfil del lead:** nunca_emprendo

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Hola, quiero comprar el programa de importadores conectados, ¿cómo hago?` | — | | |
| 2 | Agente | — | NO insiste con preguntas de calificación. Va directo al cierre: `[AUDIO:CIERRE_DIRECTO]` + texto + `---` + LINK + `---` + `[NOTIFICAR_CIERRE]`. | | |

---

### Flujo 7: Lead con perfil ya_importa

**Objetivo:** validar que el agente NO ofrece Club del Importador como primera opción sin calificar.
**Perfil del lead:** ya_importa

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Hola, ya importo desde hace un par de años, busco mejorar` | — | | |
| 2 | Agente | — | Pregunta primero qué quiere mejorar específicamente. NO recomienda Club de entrada. UNA pregunta. | | |
| 3 | Usuario | `Quiero mejorar contactos con proveedores y ver cómo manejan otros importadores` | — | | |
| 4 | Agente | — | Recién ahí presenta el Club del Importador (USD 17/mes) como opción. | | |

---

### Flujo 8: Identidad del Setter (NO Diego)

**Objetivo:** validar que el agente nunca habla en primera persona como Diego.
**Perfil del lead:** sin_clasificar

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `¿Vos sos Diego?` | — | | |
| 2 | Agente | — | Aclara que es del equipo de Diego, no Diego. Tono cercano. NO inventa nombre. | | |
| 3 | Usuario | `¿Y Diego me va a acompañar?` | — | | |
| 4 | Agente | — | Refiere a Diego en tercera persona ("Diego participa en las clases en vivo y revisa los planes"). NO dice "yo te acompaño". | | |

---

### Flujo 9: Verificación regla "una pregunta por turno"

**Objetivo:** detectar si el agente formula varias preguntas seguidas en el mismo mensaje.
**Perfil del lead:** sin_clasificar

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Hola, info por favor` | — | | |
| 2 | Agente | — | `[AUDIO:RESPUESTA_INICIAL]` con UNA sola pregunta. Contar signos `?` en el mensaje: debe ser 1 (el del audio). | | |
| 3 | Usuario | `Estoy emprendiendo` | — | | |
| 4 | Agente | — | UNA pregunta. NO "¿qué te gustaría lograr y en qué etapa estás?". | | |

---

### Flujo 10: Verificación uso de "negocio real"

**Objetivo:** confirmar que el agente NO usa la frase "negocio real".
**Perfil del lead:** nunca_emprendo

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Hola, quiero empezar a importar` | — | | |
| 2 | Agente | — | NO contiene la frase "negocio real". Puede decir "negocio" sin el "real". | | |

---

## Notas adicionales

_Completar al finalizar el testing con observaciones sistémicas: patrones de error,
comportamientos inesperados, sugerencias de mejora._

**Validaciones específicas a la nueva funcionalidad de audios:**

- ¿Los marcadores `[AUDIO:NOMBRE]` aparecen en su propia línea al inicio del bloque?
- ¿El texto del audio acompaña siempre al marcador (para fallback funcional)?
- ¿`[AUDIO:RESPUESTA_INICIAL]` se usa SIEMPRE en el primer mensaje del agente?
- ¿La secuencia de envío de link es siempre `[AUDIO:CIERRE_*]` + texto contextual + LINK?
- ¿Hay casos donde el agente sobre-usa los audios (los mete cuando no aplica)?
- ¿Hay casos donde el agente NO usa el audio que correspondía?

---

> Guía de testing v1 para Agente Importadores Conectados. Casos diseñados sobre el prompt v1.3 (correcciones de Georgina + funcionalidad de audios).
