# Venttur → GHL — Qué falta y qué depende del número (WABA)

**Fecha:** 2026-09-11 · Base: migración real (registro de ejecución + guía de pendientes).

> **Resumen:** la migración está casi entera (datos y estructura ya en GHL, agente nuevo probado por Telegram). Lo que falta se divide en **lo que necesita el número de WhatsApp conectado** y **lo que se puede hacer antes o en paralelo**.
> Leyenda de responsable: **[Cliente]** Venttur · **[la agencia]** agencia/n8n · **[Camilo]** vos.

---

## 🔴 DEPENDE de la transición del WABA (no se puede hasta conectar el número)

Todo esto cuelga de una verificación de 2 min del cliente en Meta (¿el número se porta desde Venttur o hay que sacar chip nuevo?).

1. **Enviar y recibir mensajes reales por WhatsApp** — el canal en sí. `[la agencia]`
2. **Plantillas de Meta** — subirlas y esperar aprobación (**24-72h**). Solo se pueden subir con el WABA. `[la agencia + Meta]`
3. **Audios entrantes** — detección + transcripción (Whisper). Necesita ver un audio real de GHL. `[la agencia]`
4. **Validaciones del canal (sandbox)** — que el mensaje entre a n8n, que el envío libre (<24h) ande, que el template por API funcione. `[la agencia]`
5. **Armado final del envío** (increments 5 y 6: envío por GHL + switch por canal WA/IG/FB). `[la agencia]`
6. **Probar el CAPI de punta a punta** con leads reales entrando. `[la agencia]`
7. **Testing E2E completo** (todos los subsistemas juntos, en verde). `[la agencia]`
8. **Traspaso del número + cutover** (salida en vivo). `[la agencia + Cliente]`

---

## 🟢 NO depende del WABA (se puede hacer ahora o en paralelo)

### Del cliente (Venttur)
- **Tokens nuevos de Meta** (para el CAPI) → se actualizan en Airtable. El CAPI es independiente del WhatsApp. `[Cliente]`
- **Textos**: confirmación y recordatorios de cita + los 3 programas nuevos (Viajes educativos, etc.) + sus precios. `[Cliente]`
- **Definir** las etapas comerciales de esos 3 programas nuevos. `[Cliente]`
- **Decisiones**: a qué asesor va cada handoff por programa · cada cuánto salen los seguimientos · mails/chat ids de Mauricio y Max. `[Cliente]`

### De la agencia (en su n8n / GHL)
- **Aviso al equipo** cuando se eleva a humano (workflow en GHL) — necesita los mails/chat ids del cliente. `[la agencia]`
- **Terminar el despachador** de re-enganche (el motor de selección; solo el envío final espera las plantillas). `[la agencia]`
- **Cablear "Cualificado"** (el bot marca al lead que califica) y el estado **"Cerrada"** (detectar "por ahora no puedo"). `[la agencia]`
- **Crear los 8 calendarios** (esperan usuarios + conectar los calendarios personales de los asesores — no el número). `[la agencia + Cliente]`
- **Redactar los textos de las plantillas** de Meta, para tenerlos listos y subirlos apenas esté el número. `[la agencia / agencia]`

### Tuyo (Camilo)
- **Rotar la OpenAI key** (seguridad, sin apuro — no bloquea nada). Ver `plan-rotacion-secretos-2026-09-11.md`. `[Camilo]`
- **Verificar en ManyChat** un cruce de dos flujos (Agenda / Seguimiento) antes de tocar esas plantillas. `[Camilo]`
- **Coordinar** con la agencia (lo de su n8n) y con el cliente (número, tokens, textos, decisiones). `[Camilo]`
- **Cerrar la expectativa de Clientify** con el cliente: el historial de chat, adjuntos y automatizaciones **NO** migran a GHL — hay que avisarlo antes de apagar Clientify. `[Camilo + Cliente]`

---

## En una línea

El **camino crítico** (canal, plantillas, audio, tests, cutover) **espera el número**. Lo demás (tokens Meta, textos, calendarios, despachador, decisiones, rotar la key) se puede ir haciendo antes para que, cuando el número esté, falte lo menos posible.
