# Testing Guide v7 — TOFO Pizza

**Fecha:** 2026-06-19
**Prompt objetivo:** B2B v1.8 → v1.9 (en construcción)
**Workflows objetivo:** main v4 (en construcción) + sub-workflow `chequear-disponibilidad-tofo` (mismo workflowId `vpLmZ299yXJrOSBv`, evaluar v3 → v4 si Zoom va a producción)
**Cliente:** Mauricio García de la Vega (TOFO Pizza, Robotic Vending de México)
**Objetivo:** Validar los fixes derivados de la reunión Mauricio del 18/6/26 (28 min):
1. **Punto 6 — Precio con consentimiento** (CONTRADICE el plan v1 del 17/6 — Mauricio aclaró que el agente NO debe soltar precio proactivamente; debe **pedir consentimiento** primero).
2. **Punto Zoom — Cita fantasma persistente** (el agente le dice al lead "te agendé en Zoom" pero el meeting nunca se crea en el dashboard).
3. **Punto Airtable captura** (renglón 488 hacia arriba todos dicen "contacto a redes sociales" — el agente no está capturando nombre + ubicación + interés).
4. **Punto Ficha técnica + Video** (cuando lead pregunta costo → manda ficha técnica; cuando pregunta funcionamiento → manda video).
5. **Fase A** del bump consolidado del 17/6 (timezones MX + ghost-bookings residuales + financiamiento proactivo).

---

## Estructura de herencia

Esta guía v7 **hereda íntegros** los siguientes bloques de `testing-guide-v6.md` (NO se reescriben, se ejecutan tal cual están escritos en v6):

| Sección heredada | Origen | Qué cubre |
|---|---|---|
| **§A** | v6 | 10 tests pin-data sub-workflow `chequear-disponibilidad` (validación entrada, IF válido, get availability, evaluar solapamiento JS, switch libre/ocupado, crear evento, respond shape con `zoom_link` + `zoom_status`, fallback Zoom) |
| **§B** | v6 | 17 tests conversación E2E B2B (saludo + cualificación + agendamiento + confirmación con `join_url`, fallback Zoom) |
| **§C** | v6 | 12 tests regression incidente Oscar Amaya (confusión moneda MXN/USD, validación de moneda, financiamiento externo) |
| **§G** | v6 | 18 tests regression incidente Mauricio 2026-06-08 (prohibición absoluta cita sin tool, filtro horario fuera ventana, funcionamiento canónico de la máquina, prioridad precio, coherencia RRSS) |
| **§H** | v6 | 5 tests Ghost-booking (urgencia, pasivo-agresivo, falsa memoria, todo-en-un-turno, stress multi-turno — checkpoint mental v1.8) |
| **§I** | v6 | 4 tests Timezones MX (Tijuana DST, Hermosillo Sonora sin DST, ciudad ambigua, lead "yo me arreglo") |
| **§K** | v6 | 3 tests Financiamiento proactivo (presupuesto insuficiente sin pedir, pregunta directa crédito, pregunta institución específica) |
| **§L** | v6 | Notas operativas (triage por tipo de fallo, queries SQL útiles) |
| **§Z (heredado)** | v6 | 5 verificaciones manuales Zoom dashboard (renombrado a **§Z-legacy** abajo — se mantiene como referencia pero queda superado por **§Zoom** nueva con cuenta real de Mauricio) |

Las secciones **reescritas o nuevas** en v7 son: **§J reescrita**, **§M nueva**, **§N nueva**, **§Zoom nueva** (reemplaza §Z-legacy operativamente), **§D actualizado**.

---

## §J — Precio + Consent (REESCRITA en v7)

**Contexto del cambio vs v6:** la testing-guide-v6 incorporaba 5 casos de "precio proactivo" basados en el plan v1 del 17/6 (puntos 6 y 7 del análisis WhatsApp). En la reunión del 18/6 Mauricio **contradijo explícitamente** esa lectura:

> "Cuando le diga el nombre y dónde está, le pregunta si quiere saber el precio de la máquina, la TOFO pizza, y si dice que sí, le da el precio. Y después ahí vemos si la persona está interesada o no."

Lectura: el agente **NO debe soltar precio en turno 1** ni siquiera ante intención implícita de compra. Debe primero capturar **nombre + ubicación**, luego **preguntar consentimiento** ("¿querés el precio?"), y solo dar precio si el lead acepta. Excepción única: pregunta **explícita** del lead por precio ("¿cuánto cuesta?") → respuesta directa sin consentimiento previo (sería absurdo pedir permiso para algo que pidieron).

Esta sección reemplaza íntegra la §J de v6.

### J1 — Intención implícita "quiero una máquina" → captura primero, consent después

**Setup:** lead nuevo, sesión limpia.

**Turno 1 (lead):** "Hola, quiero una máquina TOFO."

**Comportamiento esperado del agente:**
- NO suelta precio.
- NO arranca cualificación elaborada (presupuesto, plazos, ubicación de instalación).
- Saluda + pide **nombre + ubicación** (los 2 datos canónicos según Mauricio para considerarlo lead con interés).

**Turno 2 (lead):** "Soy Juan, estoy en Guadalajara."

**Comportamiento esperado del agente:**
- Confirma recepción de los datos.
- Pregunta explícitamente: **"¿Querés que te pase el precio de la máquina TOFO Pizza?"** (o redacción equivalente).
- NO da precios todavía.

**Turno 3 (lead):** "Sí, dale."

**Comportamiento esperado del agente:**
- Da **los 2 precios**: Opción A China USD 9.300 + IVA / Opción B México USD 26.300 + IVA.
- Invoca **`enviar_ficha_tecnica`** (ver §M1 para validación de la tool).
- Pregunta abierta cualificadora ("¿qué tenés pensado, instalación llave en mano o importás vos?").

**Veredicto:** PASS si los 3 turnos cumplen, FAIL si en turno 1 o 2 suelta precio sin pedir consent.

---

### J2 — Frase indirecta "¿cómo le hago para arrancar?"

**Setup:** lead nuevo, sesión limpia.

**Turno 1 (lead):** "Hola, me interesa la TOFO. ¿Cómo le hago para arrancar?"

**Comportamiento esperado del agente:**
- Mismo flujo que J1: pide **nombre + ubicación** sin soltar precio.

**Turno 2 (lead):** "Carlos, Monterrey."

**Comportamiento esperado:**
- Pregunta consent: "¿Querés el precio?"

**Turno 3 (lead):** "Sí."

**Comportamiento esperado:**
- Da los 2 precios + invoca `enviar_ficha_tecnica`.

**Veredicto:** PASS si replica el flujo J1.

---

### J3 — (Eliminado en v7)

El J3 de v6 (escenario "2 turnos sin precio" proactivo) queda **descartado** porque contradice el criterio del 18/6 de Mauricio. El agente NUNCA debe soltar precio sin consent explícito o pregunta directa del lead.

---

### J4 — Anti-regression NO-B2B

**Setup:** lead consulta tema de sucursal o servicio al cliente.

**Turno 1 (lead):** "Hola, ¿a qué hora abre la sucursal Plaza Patria?"

**Comportamiento esperado del agente:**
- Responde la pregunta de sucursal (deriva a subagente Servicio al Cliente o responde con la info canónica si está en el contexto).
- **NO** menciona precios B2B (USD 9.300 / USD 26.300).
- **NO** pregunta "¿querés el precio de la máquina?" (esto es venta B2B, el lead pregunta otra cosa).

**Veredicto:** FAIL si menciona precios B2B en cualquier turno de esta conversación.

---

### J5 — Lead pregunta por concesión / alquiler / renta → no inventa productos viejos

**Setup:** lead nuevo, sesión limpia.

**Turno 1 (lead):** "Hola, ¿manejan concesión con alquiler de la máquina?"

**Comportamiento esperado del agente:**
- Respuesta canónica: TOFO **no maneja concesiones, alquiler ni renta de máquina**. Solo venta directa (Opción A China / Opción B México llave en mano) + financiamiento externo si el lead necesita (banco/arrendadora/factura).
- **NO** inventa esquemas como "$200,000 MXN + renta", "compra a 4 años", "concesión con alquiler" (artefactos de versiones eliminadas que el agente alucinaba en el caso Marco del 10/6/26).
- Si el lead acepta el modelo de venta directa → flujo J1 (captura nombre + ubicación → consent → precio).

**Veredicto:** FAIL si menciona cualquier producto viejo o esquema inventado.

---

### J6 — Lead da nombre + ubicación pero NO pidió precio

**Setup:** lead arrancó con saludo, agente ya pidió nombre + ubicación, lead respondió sin tocar tema precio.

**Turno 1 (agente, ya hecho):** "Hola, ¿cómo te llamás y desde dónde nos escribís?"

**Turno 2 (lead):** "Soy Patricia, desde León."

**Comportamiento esperado del agente:**
- Confirma datos.
- Pregunta explícitamente: **"¿Querés que te pase el precio de la máquina TOFO Pizza?"**
- NO asume que quiere precio sin preguntar.
- NO arranca cualificación elaborada antes del consent.
- **NO invoca `enviar_ficha_tecnica` en este turno** (el lead no ha aceptado precio aún — ficha acompaña al precio, no al consent question; mandarla acá rompe el gate del §9).

**Turno 3a (lead acepta):** "Sí, pasámelo."

**Comportamiento esperado:**
- Da los 2 precios + invoca `enviar_ficha_tecnica` (ver §M1).

**Turno 3b (lead rechaza):** "No, todavía no, primero quiero entender."

**Comportamiento esperado:**
- **Respeta el "no"**: no insiste, no fuerza precio.
- Pregunta abierta para entender qué quiere saber ("Dale, contame qué te gustaría saber primero").
- Mantiene puerta abierta para volver al precio cuando el lead lo pida.

**Veredicto:** PASS si los 2 sub-caminos (acepta/rechaza) se manejan según contrato. FAIL si: (a) no pregunta consent en turno 2, (b) suelta precio sin consent, (c) insiste con precio cuando lead dijo no.

---

### J7 — Lead pregunta precio EXPLÍCITAMENTE en turno 1 SIN datos → pedir datos primero, después dar precio

**Setup:** lead nuevo, sesión limpia (sin nombre ni ubicación), pregunta directa por precio en el primer mensaje.

**Turno 1 (lead):** "Hola, ¿cuánto cuesta la máquina?"

**Comportamiento esperado del agente (§9 fila 2 — consent implícito, pero faltan datos):**
- **NO** suelta el precio ni la ficha técnica todavía — faltan nombre + ubicación (gate del §9).
- Reconoce la pregunta brevemente + pide nombre + ubicación en una sola línea: *"¡Hola! Con gusto te paso el precio. ¿Me confirmas tu nombre y desde qué país me escribes?"*
- **NO** pide consent adicional ("¿querés el precio?") — el lead ya lo pidió, no hay que volver a preguntarlo.
- **NO invoca `enviar_ficha_tecnica` en este turno** (rompe el gate).

**Turno 2 (lead):** "Soy Patricia, desde México."

**Comportamiento esperado del agente (consent implícito ya dado, datos completos → §9 fila 8 efectivamente):**
- **Dispara precio automáticamente** (NO pide consent de nuevo — la pregunta directa del turno 1 ya lo suple).
- Da **los 2 precios** (Opción A USD 9.300 + IVA / Opción B USD 26.300 + IVA).
- Invoca **`enviar_ficha_tecnica`** (igual que J1/J6 — la ficha acompaña al precio).
- Cierra con pregunta de continuidad ("¿Cuál de las dos opciones se ajusta mejor a lo que buscás?").

**Veredicto:** FAIL si: (a) el agente suelta precio o ficha en turno 1 (rompe gate); (b) el agente pide consent extra en turno 2 (redundante porque ya pidió en turno 1); (c) el agente arranca cualificación adicional en turno 2 antes de soltar precio.

---

## §M — Envío de Ficha Técnica + Video (NUEVA en v7)

**Contexto:** Mauricio aclaró el 18/6/26 que el agente debe enviar **ficha técnica (PDF) cuando lead pregunta costo** y **video cuando lead pregunta funcionamiento**. Hoy la gente está confundida — algunos clientes preguntan "¿tienen prohibido mandar videos?" porque el agente no envía nada. Mauricio explicitó:

> "Cuando te pregunta el costo, inmediatamente manda la ficha técnica. Pregunta costo, ficha técnica. ¿Cómo funciona la máquina? Le pasas el video."

Esta sección valida que las tools `enviar_ficha_tecnica` y `enviar_video_funcionamiento` se invoquen en los contextos correctos.

### M1 — Lead pregunta precio → ficha técnica acompaña

**Setup:** cualquier flujo que termine con el agente dando precio (J1 turno 3, J6 turno 3a, J7 turno 1).

**Comportamiento esperado del agente:**
- Después de dar los 2 precios, invoca **`enviar_ficha_tecnica`** con `subscriber_id` + `canal`.
- El sub-workflow entrega el PDF al lead vía ManyChat (sendFlow con flow_ns de ficha técnica).
- El mensaje del agente menciona la ficha ("Te paso también la ficha técnica con todos los detalles") para que el lead sepa qué le llega.

**Verificación:**
1. Tool call logueada en `sys_tool_calls` (o equivalente TOFO) con `tool_name = 'enviar_ficha_tecnica'` y `status = 'RESOLVED'`.
2. ManyChat dashboard: el flow de ficha técnica disparó al subscriber correcto.
3. Lead recibe el PDF en su canal (verificar manualmente con cuenta de prueba).

**Veredicto:** FAIL si: (a) el agente da precio sin invocar la tool, (b) la tool falla con error de schema (síntoma del bug Zod LangChain — escalar a postmortem), (c) el PDF no llega al lead.

---

### M2 — Lead pregunta "¿cómo funciona la máquina?" → video

**Setup:** lead nuevo, sesión limpia.

**Turno 1 (lead):** "Oye, ¿cómo funciona la máquina TOFO?"

**Comportamiento esperado del agente:**
- Da una **descripción breve canónica** (replica la sección "🍕 Cómo funciona la máquina" del prompt v1.6+: pizza pre-horneada al 75% + ingredientes frescos + horno termina el horneado al momento).
- Invoca **`enviar_video_funcionamiento`** con `subscriber_id` + `canal`.
- El mensaje del agente menciona el video ("Te paso un video corto para que lo veas en acción").
- NO inventa detalles técnicos no autorizados (capacidad interna, tiempo de conservación, tipo de horno específico — esto está cubierto por anti-alucinación v1.6+ y §G del v6).

**Verificación:**
1. Tool call logueada con `tool_name = 'enviar_video_funcionamiento'` y `status = 'RESOLVED'`.
2. Flow de video se dispara en ManyChat.
3. Lead recibe el video.

**Veredicto:** FAIL si: (a) el agente describe el funcionamiento sin enviar el video, (b) inventa info técnica no autorizada, (c) la tool falla.

---

### M3 — Lead pide contrato / dossier / propuesta formal → NO manda nada

**Setup:** lead avanzado en flujo B2B, ya tiene precio + ficha técnica, pide siguiente nivel de documentación.

**Turno 1 (lead):** "¿Me pasás el contrato y el dossier completo de la operación?"

**Comportamiento esperado del agente:**
- Responde que **eso lo conversa el director** (Mauricio) en la cita.
- Ofrece agendar la cita (flujo `check_disponibilidad` + `Crear evento`).
- **NO** invoca `enviar_ficha_tecnica` (la ficha ya se mandó en M1).
- **NO** inventa que va a mandar el contrato o el dossier.
- **NO** menciona email/teléfono de Mauricio (bloque anti-alucinación común v1.4+).

**Veredicto:** FAIL si: (a) el agente promete mandar contrato/dossier, (b) inventa email/tel de Mauricio, (c) invoca una tool de envío sin existir.

---

## §N — Airtable Captura de Datos (NUEVA en v7)

**Contexto:** Mauricio reportó el 18/6/26 que del renglón 488 hacia arriba de Airtable, **todos los registros dicen "contacto a redes sociales"** — el agente no está capturando nombre + ubicación + interés del lead. El criterio operativo de Mauricio para considerar "lead con interés" es: el lead dio **nombre + ubicación**. Si solo saludó y se fue, no es lead.

> "Del renglón 488 para arriba, todos dicen 'contacto a redes sociales' porque no cogieron nada más de información, solo cogieron la información inicial."

Esta sección valida que el workflow main escriba a Airtable con los campos correctos cuando el lead da nombre + ubicación, y que NO escriba registros vacíos.

### N1 — Conversación E2E con nombre + ubicación capturados → registro completo en Airtable

**Setup:** lead nuevo, sesión limpia. Ejecutar flujo J1 completo (3 turnos: lead pide máquina → agente pide datos → lead da nombre + ubicación → consent → precio).

**Comportamiento esperado del workflow:**
- Después del turno 2 del lead ("Soy Juan, Guadalajara"), el workflow main (o sub-flujo de captura) debe escribir a **Airtable Leads** un registro con:
  - `Nombre` = "Juan"
  - `Ubicación` = "Guadalajara"
  - `Canal` = (WhatsApp / Instagram / Facebook según el `canal` del payload)
  - `subscriber_id` = el ID de ManyChat
  - `Estado` = "Interés inicial" (o equivalente del schema TOFO)
  - `Fecha primer contacto` = NOW()
- NO debe escribir "contacto a redes sociales" como `Ubicación` o como cualquier otro campo (esto era el síntoma del problema reportado).

**Verificación:**
1. Abrir Airtable → tabla Leads → buscar el registro recién creado por `subscriber_id`.
2. Validar los 6 campos esperados llenos correctamente.
3. Validar que NO existan registros adicionales duplicados para el mismo `subscriber_id`.

**Veredicto:** FAIL si: (a) el registro no se crea, (b) `Nombre` o `Ubicación` vienen vacíos o con "contacto a redes sociales", (c) se duplican registros.

---

### N2 — Lead solo saluda y se va → NO se crea registro

**Setup:** lead nuevo, sesión limpia.

**Turno 1 (lead):** "Hola."

**Turno 2 (agente):** [Saludo + pide nombre + ubicación]

**Turno 3 (lead):** [no responde / cierra conversación / dice "después te aviso"]

**Comportamiento esperado del workflow:**
- **NO se crea registro en Airtable Leads** — el lead no dio nombre ni ubicación, según criterio Mauricio no es lead con interés.
- Puede haber log de la sesión en Postgres (`session_state` o equivalente) para memoria, pero **no** llegó a Airtable como lead cualificado.

**Verificación:**
1. Abrir Airtable → tabla Leads → confirmar que NO existe registro nuevo con ese `subscriber_id`.
2. Si el schema tiene tabla separada "Contactos iniciales" o equivalente, validar la regla operativa con Mauricio (puede que ahí sí caiga, pero NO en Leads).

**Veredicto:** FAIL si se crea registro con campos vacíos o placeholder "contacto a redes sociales".

---

## §Zoom — Verificación E2E Cuenta Real Mauricio (NUEVA en v7)

**Contexto:** Mauricio confirmó el 18/6/26 que el problema Zoom persiste:

> "No está haciendo las citas en Zoom aún. Les dice al cliente que le hizo la cita en Zoom, pero no la hace."

La testing-guide-v6 §Z incluye verificaciones manuales pero asume credenciales de testing. **Esta §Zoom nueva debe ejecutarse contra la cuenta Zoom REAL de Mauricio**, no contra credenciales fantasma de la agencia o de desarrollo. Bloqueante: obtener credenciales Zoom OAuth de Mauricio + verificar que `zoomOAuth2Api` id `TllmBz0re6WGmTw2` en n8n esté apuntando a la cuenta correcta del cliente (no a la cuenta de testing).

Esta sección **supera operativamente** la §Z heredada de v6 (ahora renombrada §Z-legacy). Solo Z-Zoom-1 a Z-Zoom-5 son bloqueantes para promover a LIVE.

### Z-Zoom-1 — Smoke E2E con cuenta REAL de Mauricio

**Setup:**
- Credencial `zoomOAuth2Api` en n8n apunta a la cuenta Zoom de Mauricio (NO la agencia NO testing).
- Sub-workflow `chequear-disponibilidad-tofo` con nodo `Crear meeting Zoom` activo y `continueOnFail: true`.
- Lead de prueba simulado con número de WhatsApp real controlado por la agencia o el tester.

**Test:**
1. Disparar webhook con conversación E2E B2B que termine en agendamiento (flujo B16 de v6 §B).
2. El sub-workflow debe ejecutarse y crear evento en Calendar + meeting en Zoom.
3. Verificar en el **dashboard Zoom de Mauricio** (no en otro dashboard) que la meeting **aparece programada** con:
   - Fecha y hora correctas (en TZ CDMX `-06:00`)
   - Duración 30 min
   - Topic / nombre legible (ej. "TOFO B2B — [nombre lead]")
   - Host = Mauricio

**Veredicto:** FAIL si: (a) la meeting NO aparece en el dashboard de Mauricio (esto reproduce el problema reportado), (b) aparece en otra cuenta Zoom (credencial mal cableada), (c) los campos no coinciden con lo agendado.

---

### Z-Zoom-2 — `join_url` apunta al meeting correcto

**Setup:** continuación de Z-Zoom-1, meeting creada con éxito.

**Test:**
1. Tomar el `join_url` que el agente envió al lead en el mensaje de confirmación (extraído del log del workflow o del mensaje real en WhatsApp).
2. Abrir el `join_url` en un navegador (incognito recomendado).
3. Verificar que:
   - Abre el lobby/waiting room de Zoom
   - Muestra el nombre/topic correcto de la meeting
   - El passcode embebido en el `join_url` funciona (no pide volver a ingresarlo)
   - Si waiting room está activo, queda esperando admisión (no entra solo)

**Veredicto:** FAIL si: (a) el link da error 404 / "meeting not found", (b) abre una meeting distinta a la creada, (c) el passcode no funciona y pide ingresarlo manualmente.

---

### Z-Zoom-3 — `start_url` da control de host a Mauricio

**Setup:** continuación, evento Calendar abierto.

**Test:**
1. En el evento de Google Calendar de Mauricio, abrir la `description` y localizar la línea `Start URL (host)`.
2. Mauricio (o tester con acceso a cuenta de Mauricio) abre el `start_url` en navegador.
3. Verificar que:
   - Abre la meeting como **host** (no como participante)
   - Tiene controles de host (mute all, end meeting, manage participants)
   - El topic coincide con el de la meeting agendada

**Veredicto:** FAIL si: (a) abre como participante y no como host, (b) abre meeting distinta, (c) el `start_url` no está en la description del evento.

---

### Z-Zoom-4 — Limpieza post-test

**Test:**
1. Eliminar todas las meetings de prueba del dashboard Zoom de Mauricio.
2. Eliminar todos los eventos de prueba del Google Calendar de Mauricio.
3. Eliminar (o marcar como "test") los registros de Airtable Leads generados.
4. Verificar que el lead de prueba NO recibió notificaciones adicionales no deseadas.

**Veredicto:** PASS si el ambiente queda limpio sin residuos.

---

### Z-Zoom-5 — Email de invitación correcto

**Setup:** continuación de Z-Zoom-1.

**Test:**
1. Verificar si Zoom envió email de invitación al lead (configuración de la cuenta + del meeting).
2. Si sí: validar que el email tiene:
   - `join_url` correcto
   - Hora correcta en TZ del lead (o TZ CDMX si no se setea TZ del lead)
   - Topic / agenda visibles
   - From = Mauricio (no la agencia)
3. Si no se manda email automático (configuración común): confirmar con Mauricio que esto es lo esperado (el agente ya pasó el `join_url` por WhatsApp, no hace falta email).

**Veredicto:** FAIL si: (a) email viene de cuenta equivocada (la agencia en vez de Mauricio), (b) hora incorrecta, (c) link roto.

---

## §Z-legacy — Verificaciones manuales heredadas de v6

Las 5 verificaciones manuales §Z de v6 (meeting aparece en dashboard, `join_url` lobby, `start_url` host, description con 3 líneas, limpieza opcional) quedan como **referencia histórica**. Operativamente reemplazadas por §Zoom de v7 (que usa cuenta real de Mauricio en lugar de cuenta de testing). Si el tester ya corrió §Zoom 1-5, no necesita correr §Z-legacy.

---

## §D — Checklist de Promoción TESTING → LIVE (actualizado en v7)

Para promover el bump v1.8 → v1.9 a producción, **todos** los bloqueantes deben estar PASS. Resaltado en **negrita** los bloques nuevos o reescritos en v7.

### Bloqueantes heredados (de v6, sin cambio)

| Bloque | Casos | Mínimo PASS |
|---|---|---|
| §A — Pin data sub-workflow | A1-A10 | 10/10 |
| §B — Conversación E2E B2B | B1-B17 | 17/17 |
| §C — Regression Oscar Amaya (moneda) | C1-C12 | 12/12 |
| §G — Regression incidente Mauricio 8/6 | G1-G18 | 18/18 |
| §H — Ghost-booking | H1-H5 | 5/5 |
| §I — Timezones MX | I1-I4 | 4/4 |
| §K — Financiamiento proactivo | K1-K3 | 3/3 |

### Bloqueantes nuevos / reescritos en v7

| Bloque | Casos | Mínimo PASS |
|---|---|---|
| **§J — Precio + Consent (reescrita)** | **J1-J2, J4-J7** (J3 eliminado) | **6/6** |
| **§M — Envío ficha técnica + video** | **M1-M3** | **3/3** |
| **§N — Airtable captura datos** | **N1-N2** | **2/2** |
| **§Zoom — Cuenta real Mauricio** | **Z-Zoom-1 a Z-Zoom-5** | **5/5** |

### Total bloqueante

- v6 heredado: **69 casos** (10 + 17 + 12 + 18 + 5 + 4 + 3)
- v7 nuevo / reescrito: **16 casos** (6 + 3 + 2 + 5)
- **Total: 85 casos PASS para promover a LIVE.**

### Pre-requisitos antes de ejecutar testing

1. **Prompt B2B v1.9** subido al Google Doc vivo (el AI Agent lo carga vía `Get a document`).
2. **Main workflow v4** importado en n8n con los siguientes nodos confirmados:
   - Nodo `Fechas` (Patrón Napier CDMX) intacto desde v3.
   - Nodo de captura de datos a Airtable (verificar §N1/N2).
   - Tools `enviar_ficha_tecnica` y `enviar_video_funcionamiento` cableadas como `ai_tool` al Agente B2B con `$fromAI()` correctamente configurado.
   - Nodo `Update ultima_actividad` intacto (cron seguimientos depende de él).
3. **Sub-workflow `chequear-disponibilidad-tofo` v4** (o v3 si Zoom queda en v3) importado preservando workflowId `vpLmZ299yXJrOSBv`.
4. **Credencial Zoom de Mauricio** cableada en `zoomOAuth2Api` id `TllmBz0re6WGmTw2` — verificar antes de Z-Zoom-1.
5. **ManyChat flows** de ficha técnica y video creados y con flow_ns documentados en `06_docs/`.
6. **Airtable Leads schema** validado con Mauricio: campos `Nombre`, `Ubicación`, `Canal`, `subscriber_id`, `Estado`, `Fecha primer contacto` existen y son escribibles desde n8n.

### Post-deploy (primeras 48h)

1. Monitorear `sys_tool_calls` (o equivalente TOFO) cada 12h durante las primeras 48h post-LIVE buscando errores Zod en `enviar_ficha_tecnica` / `enviar_video_funcionamiento`.
2. Auditar Airtable Leads en H+24 y H+48 — confirmar que NO aparece "contacto a redes sociales" en `Ubicación` (problema reportado por Mauricio el 18/6 debe quedar resuelto).
3. Verificar en Zoom dashboard de Mauricio que las meetings se crean efectivamente — si reaparece el problema "cita fantasma", escalar a postmortem y rollback inmediato del sub-workflow al v2.
4. Spot-check 5 conversaciones B2B reales que terminen en agendamiento: confirmar que el lead recibió el `join_url` literal en WhatsApp y que la meeting existe en el dashboard.

### Rollback

Si cualquier bloqueante post-deploy FAILa:
- **§J/§M/§N falla** → rollback del prompt al v1.8 vía Google Doc + revertir main a v3.
- **§Zoom falla en producción real** → desactivar nodo `Crear meeting Zoom` en sub-workflow (vuelve a v2 funcionalmente, eventos Calendar siguen creándose, Zoom queda manual como hoy) + bump prompt B2B con frase "Mauricio te pasa el Zoom aparte" hasta resolver.
- **Airtable §N falla** → desactivar nodo de captura de datos en main, volver a v3 (acepta que el problema "contacto a redes sociales" persiste mientras se diagnostica, pero el agente sigue funcionando).

---

## Apéndice — Decisiones cerradas en este bump

1. **Precio con consent (J1/J6) > precio proactivo (J3 v6 eliminado)** — fuente: Mauricio 18/6/26 verbatim. El plan v1 del 17/6 quedó superado.
2. **Pregunta explícita de precio = respuesta directa sin consent (J7)** — interpretación operativa de "si pregunta cuánto cuesta, le dices cuánto cuesta" (no pedir permiso para algo que pidieron).
3. **Captura Airtable solo con nombre + ubicación (§N)** — criterio Mauricio "lead con interés" = los 2 datos canónicos. Saludo solo NO genera registro.
4. **Ficha técnica acompaña al precio siempre (§M1)** — Mauricio verbatim "pregunta costo, ficha técnica".
5. **Video acompaña a "cómo funciona" siempre (§M2)** — Mauricio verbatim + corrige confusión "¿tienen prohibido mandar videos?".
6. **§Zoom debe correrse contra cuenta real (no testing)** — sin esto, "cita fantasma" persiste como bug invisible que el lead descubre cuando llega a la hora del meeting.
7. **Backup v1.8 ya creado** en `clients/TFO_TOFO/04_agents/agente-tofo-b2b-system-prompt-v1.8.md` antes de iniciar el bump v1.8 → v1.9.