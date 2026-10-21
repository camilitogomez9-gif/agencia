# Reporte de incidencia de link de agendamiento

## Caso Nahe

**Descripción del caso**

* Lead: Nahelli Macías Álvarez (WhatsApp `+5214731005555`, ManyChat `1947408257`), interesada en Año Académico Familiar para su hijo de 13.
* 23/11/2025: primera consulta, el bot le envió correctamente el link `promo.venttur.com/agendar-ema`. Ella no agendó ("lo platico con mi esposo").
* 10/9/2026: volvió a escribir con más contexto sobre su hijo. Le preguntó al bot "¿el lunes a las 11 podrás?".
* El bot respondió aceptando: "Claro, Nahe. Voy a coordinar para que tengas la asesoría el lunes a las 11".
* 14/9 y 15/9: Nahe se preparó para llamadas que nunca existieron. Nadie la contactó.
* 15/9 09:10 CDMX: cerró con "me parece falta de seriedad… mandar a un menor de edad con alguien en quien quieras confiar, pero van 2 veces con confusiones mejor no gracias".

**Hallazgos**

* El link a Nahe **sí se envió** correctamente en noviembre. Airtable la marca `Link asesoría enviado = true` desde entonces.
* La cita del lunes 14 y del martes 15 **nunca existieron**: `Agendan cita = false` en todo momento.
* El bot le "coordinó" citas en 8 turnos distintos entre el 10 y el 15 de septiembre. Todas fantasma.
* En los 4 mensajes de hoy (15/9 09:07–09:10), el bot le contestó pero **en ninguno le mandó el link**: solo pidió disculpas y ofreció "coordinar de nuevo".
* Los mensajes salieron OK del sistema (ManyChat devolvió `status: success` en las 4 ejecuciones). No hubo falla técnica de envío.

**Cómo recuperarla**

* **Llamada telefónica directa**, no WhatsApp. Idealmente Mauricio o Rodrigo, no el bot ni el CM.
* Disculparse honestamente, admitir que fue un error del sistema, ofrecer una asesoría personalizada con Rodrigo fuera del calendar (en un horario que ella elija).
* No entrar en detalles técnicos. La versión pública: "un error nuestro, no un fallo de Rodrigo".
* Después de la llamada, actualizar en Airtable `Estado conversación` a "Recuperación en curso" o "Perdida (error sistema)".
* Si hay post público, coordinar la respuesta: nunca dar detalles técnicos, solo "ya te contactamos por privado, disculpá el mal rato".

## Causa del problema

* El agente **no tiene herramienta para agendar en el calendar** de los asesores. La única vía real es que el lead use el link para reservar él mismo.
* El prompt del agente (versión que estaba corriendo hasta ayer) tenía **dos instrucciones explícitas** que le decían al bot que "coordinara el horario a mano" cuando el lead ya había recibido el link:
    * En el bloque de estado del lead: "reconocé que ya se lo mandaste, preguntá qué lo detuvo y **ofrecé coordinar el horario a mano**".
    * En la sección "Ya le mandaste el link y no agendó": "dime qué día te viene bien y **lo coordino contigo directo**".
* El bot ejecutaba esas instrucciones correctamente. El problema era el prompt, no el modelo ni la infraestructura.
* Cuando Nahe preguntó "¿el lunes a las 11 podrás?", el bot siguió las instrucciones y prometió coordinar. No tenía cómo cumplir.
* No es un caso aislado: cualquier lead que haya vuelto pidiendo agendar por chat (en vez de usar el link) pudo haber caído en el mismo error.

## Soluciones implementadas (2026-09-16 14:49 UTC)

**Cambio 1: prompt del agente (v2.0 → v2.1)**

* Se eliminaron las dos instrucciones que le decían al bot "coordinar a mano".
* Se agregó una **regla absoluta nueva** ("No agendo yo") en la sección de reglas rectoras, que prohíbe explícitamente coordinar, agendar, programar, confirmar o reservar cita por chat.
* Se agregó la lista de frases prohibidas ("voy a coordinar", "quedamos", "programamos la llamada", "te confirmo el horario", etc.) para que el modelo sepa exactamente qué evitar.
* Se reescribió la sección "Ya le mandaste el link y no agendó": ahora, cuando un lead vuelve pidiendo agendar, el bot **re-envía el link inmediatamente** con framing "acá te lo dejo otra vez para que elijas horario".

**Cambio 2: guardrail estructural (red de seguridad)**

* Se agregó un nodo determinístico entre el modelo y el envío que detecta si el bot, a pesar del prompt nuevo, sigue prometiendo coordinar cita por chat.
* Si detecta una promesa fantasma, **reemplaza el mensaje automáticamente** con el link canónico del programa del lead + una disculpa breve.
* La lógica es determinística (regex, sin LLM), así que no puede fallar por temperature o por presión conversacional.
* Validado con 12 casos de prueba antes de deployarlo (incluyendo mensajes verbatim de Nahe).

**Prueba post-fix**

* Se corrieron los mensajes reales de Nahe contra el prompt nuevo (5 escenarios distintos, incluyendo el "¿el lunes a las 11 podrás?" que disparó el bug).
* En todos, el bot ahora responde enviando el link correcto (`promo.venttur.com/AAFamilia-Agendar`) en vez de prometer una cita.
* Ejemplo de la respuesta nueva al mismo mensaje que rompió con Nahe:
    > "Para reservar tu horario, necesito que uses este enlace: promo.venttur.com/AAFamilia-Agendar. Ahí puedes elegir el día y la hora que te acomode mejor, y me llega la confirmación automáticamente."

## Estado actual del agente

* Prompt v2.1 activo desde el 16/9 14:49 UTC.
* Guardrail activo en la misma ventana.
* El agente responde a leads en producción normalmente. La única diferencia visible es que **ya no acepta coordinar citas por chat**: siempre redirige al link.
* Nada más cambió: la personalidad, el tono, la lógica de calificación, la memoria y los precios son los mismos.

## Cómo se comporta de ahora en más

* Cuando el lead **pide agendar** (por primera vez o volviendo después): el bot envía el link del programa correcto y le dice que él elija día y hora ahí.
* Cuando el lead **propone un horario específico** ("el lunes a las 11", "mañana a las 9"): el bot no acepta; le manda el link para que reserve él mismo.
* Cuando el lead **insiste** ("no, mejor tú me dices"): el bot sigue redirigiendo al link, con framing distinto cada vez.
* Cuando el lead **solo saluda o pregunta info** (sin pedir agendar): el bot conversa normal, sin re-mandar el link espontáneamente.

## Lo que sigue

* **Recuperación de Nahe** (bloqueante, hoy): llamada telefónica humana. Coordinar con Mauricio o Rodrigo.
* **Barrido de la cohorte reciente** (esta semana): script que detecte otros leads que quedaron en el mismo estado ("pidieron agendar, el bot les prometió una cita, nadie los llamó"). Estimación gruesa: unos 30-40 casos posibles en las últimas 4 semanas, hasta correr el análisis no lo sabemos con certeza.
* **Alerta inmediata a Max por Telegram** cuando el guardrail intercepte una promesa fantasma en producción: así vemos en tiempo real si el prompt v2.1 falla y en qué contexto.
* **Reconciliador diario** entre Airtable, ManyChat y n8n para detectar divergencias silenciosas antes de que exploten como este caso.

## Anexos técnicos

Detalle completo con evidencia por ejecución, cronología minuto a minuto, snapshots antes/después del fix y tests golden del guardrail: `06_docs/incidente-nahe-2026-09-15.md`, `03_workflows/vivo-2026-09-16-post-fix-prompt-guardrail/`.
