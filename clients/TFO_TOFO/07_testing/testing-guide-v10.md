# Testing Guide v10 — Agente B2B TOFO Pizza

**Versión del prompt:** v1.20
**Fecha:** 2026-06-30
**Herencia:** §A-§P + §Q + §R de testing-guide-v9 permanecen vigentes (no re-correr salvo regression).

---

## Contexto del bump v10

Testing focalizado en el cambio v1.19 → v1.20: **el agente ahora pregunta el día PRIMERO y solo después ofrece los slots para ese día específico** (instrucción Mauricio 30/6/26).

Antes (v1.19): agente listaba los 6 slots junto con la pregunta de día → lead procesaba 2 decisiones simultáneas.

Ahora (v1.20): 2a pregunta solo el día → lead responde día → **agente invoca `listar_disponibilidad_dia`** (tool nueva read-only) → 2b ofrece SOLO los `slots_libres` que devolvió la tool → lead elige → `check_disponibilidad` bookea.

**Tool nueva `listar_disponibilidad_dia`** (`03_workflows/listar-disponibilidad-dia-tofo-v1.json`): input `fecha` (YYYY-MM-DD), devuelve `{status, fecha, dia_humano, slots_libres, mensaje}`. Es de solo lectura (no crea eventos).

**Bloqueante:** solo se promueve v1.20 a producción cuando §S pasa 100% Y `listar_disponibilidad_dia` está deployada + cableada al main. **✅ Coherencia de slots resuelta:** `check_disponibilidad` **v6** ya acepta los 6 slots (`:00` y `:30`) — no hay mismatch con `listar_disponibilidad_dia`. §A-§R siguen aplicando si querés revalidar regresión general — no bloqueante.

**Nota de testing:** los casos §S involucran 2 tools reales (`listar_disponibilidad_dia` + `check_disponibilidad`). Si el test runner no mockea tool responses, §S es **manual-only en n8n** (conversaciones de prueba dedicadas). Los "resultado esperado" abajo asumen que la tool devolvió los 6 slots libres; si el calendar tiene ocupaciones reales, el agente debe ofrecer solo los libres que la tool reporte.

---

## §S — Nuevo flow de agendamiento (día primero → listar_disponibilidad_dia → slots libres)

Todos los casos asumen que el gate de §9 (nombre + ubicación) ya está cumplido y el lead avanza a agendar.

### S1 — Happy path lead Centro (CDMX)

**Setup:** lead ya cualificado, "Juan de CDMX", pide agendar.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "Dale, agendemos la llamada con el director" | Agente pregunta SOLO el día. Ejemplos válidos: "¿Qué día te queda mejor? El director toma reuniones de lunes a viernes." o variantes equivalentes. **NO lista los slots todavía.** No aparecen los strings "10:00", "10:30", "11:00", "11:30", "12:00", "12:30" en este turno. |
| 2 | user | "El viernes me viene bien" | Agente **invoca `listar_disponibilidad_dia`** con `fecha` = próximo viernes (YYYY-MM-DD) → recibe `slots_libres` → ofrece SOLO esos, en hora CDMX. Si la tool devolvió los 6: "Genial, para el viernes tengo libre (hora México, CDMX): 10:00, 10:30, 11:00, 11:30, 12:00 o 12:30. ¿Cuál te queda mejor?". **NO lista slots sin consultar la tool.** |
| 3 | user | "10:30" | Agente invoca `check_disponibilidad` con ISO `YYYY-MM-DDT10:30:00-06:00` para el próximo viernes. **NO confirma cita antes de la respuesta de la tool.** |

### S2 — Lead Culiacán (huso deducido)

**Setup:** lead "René de Culiacán, Sinaloa" pide agendar.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "Quiero agendar la llamada" | Agente pregunta solo el día. NO menciona huso al lead. NO pregunta zona horaria. NO lista slots. |
| 2 | user | "El jueves" | Agente invoca `listar_disponibilidad_dia` (fecha=jueves) → recibe `slots_libres` en CDMX → convierte a hora Culiacán (Δ=-1h) y ofrece SOLO esos. Si vinieron los 6: "Genial, para el jueves tengo libre (hora Culiacán): 9:00, 9:30, 10:00, 10:30, 11:00 o 11:30..." **NO menciona hora CDMX al lead.** |
| 3 | user | "10:00" | Agente convierte: 10 hora Culiacán = 11:00 CDMX. Invoca `check_disponibilidad` con ISO `YYYY-MM-DDT11:00:00-06:00`. |

### S3 — Lead Cancún (huso +1h)

**Setup:** lead "Ana de Cancún" pide agendar.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "Agendame por favor" | Agente pregunta solo el día. NO lista slots. |
| 2 | user | "El martes" | Agente invoca `listar_disponibilidad_dia` (fecha=martes) → convierte `slots_libres` a hora Cancún (Δ=+1h) y ofrece SOLO esos. Si vinieron los 6: "Genial, para el martes tengo libre (hora Cancún): 11:00, 11:30, 12:00, 12:30, 13:00 o 13:30..." |
| 3 | user | "12:00" | Agente convierte: 12 hora Cancún = 11:00 CDMX. Invoca `check_disponibilidad` con ISO `YYYY-MM-DDT11:00:00-06:00`. |

### S4 — Lead da día + hora en UN turno (skip de PASO 2a + 2b)

**Setup:** lead "Pedro de Guadalajara" cualificado.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "Agendame el jueves a las 11" | Agente NO re-pregunta ni día ni hora. Reconoce que tiene ambos datos. Aceptable cualquiera de las 2 vías: (a) invocar `listar_disponibilidad_dia` (fecha=jueves) para confirmar que 11:00 está en `slots_libres` y luego `check_disponibilidad`; o (b) ir directo a `check_disponibilidad` con ISO jueves 11:00 (que atrapa `ocupado` si no está libre). **NO responde con "¿Qué día te queda mejor?"** ni re-pregunta la hora — sería regression del skip. |

### S5 — Lead da SOLO el día (voluntario)

**Setup:** lead "Marta de León" cualificada.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "Quiero la llamada el miércoles" | Agente reconoce que el día ya está dado → saltea la pregunta del PASO 2a → **invoca `listar_disponibilidad_dia` (fecha=miércoles)** → PASO 2b: ofrece los `slots_libres` del miércoles en hora CDMX (Centro). **NO re-pregunta el día.** |
| 2 | user | "11:00" | Agente invoca tool con ISO del miércoles 11:00 CDMX. |

### S6 — Sábado → rebote

**Setup:** lead cualificado en CDMX.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "Cuando puedo agendar?" | Agente pregunta el día (PASO 2a). |
| 2 | user | "El sábado" | Agente rebota: "Solo tomamos lunes a viernes. ¿Qué día te queda?" **NO ofrece slots del sábado.** NO invoca tool. Vuelve a PASO 2a. |
| 3 | user | "Ok, el lunes" | Agente invoca `listar_disponibilidad_dia` (fecha=lunes) → PASO 2b: ofrece los `slots_libres` del lunes en hora CDMX. |

### S7 — Fecha pasada → rebote

**Setup:** lead cualificado en Monterrey.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "Agendame el 10 de junio" (fecha en el pasado según Contexto temporal del User Message) | Agente rebota: "Esa fecha ya pasó. ¿Te queda otro día esta semana o la próxima?" NO invoca tool. Vuelve a PASO 2a. |

### S8 — Hora fuera de ventana (después de dar día)

**Setup:** lead "Luis de Puebla" cualificado.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "Agendame" | Agente pregunta el día. |
| 2 | user | "Viernes" | Agente invoca `listar_disponibilidad_dia` (fecha=viernes) → PASO 2b: ofrece los `slots_libres` para el viernes en hora CDMX. |
| 3 | user | "9 de la mañana" | Agente rebota con formato de PASO 2b que referencia el día: "Para el viernes el horario es 10:00, 10:30, 11:00, 11:30, 12:00 o 12:30 (hora México). ¿Cuál te queda?" **NO invoca tool con 09:00.** El día "viernes" ya elegido se conserva. |
| 4 | user | "12:30" | Agente invoca tool con ISO del viernes 12:30 CDMX. |

### S9 — Minutos no redondos

**Setup:** lead "Sofía de CDMX" cualificada.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "Agendame el jueves a las 11:15" | Agente reconoce el día (jueves) y rebota la hora: "Las reuniones empiezan en punto o y media — para el jueves tenés 10:00, 10:30, 11:00, 11:30, 12:00 o 12:30 (hora México). ¿Cuál te queda?" El día "jueves" se conserva; solo pide re-elegir hora. **NO invoca tool con minutos ≠ :00/:30.** |
| 2 | user | "11:30" | Agente invoca tool con ISO jueves 11:30. |

### S10 — Tool devuelve ocupado con alternativas (lead Centro)

**Setup:** lead "Diego de GDL", ya eligió miércoles 11:00.

Setup mock: la tool devuelve `{libre: false, motivo: "ocupado", alternativas: ["10:00","10:30","12:30"]}`.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "El miércoles a las 11" | Agente invoca tool → recibe ocupado + alternativas. Ofrece las 3 alternativas al lead en hora CDMX (Centro, Δ=0h): "El miércoles a las 11 está ocupado. Tengo disponible 10:00, 10:30 o 12:30 (hora México). ¿Cuál te queda?" **NO confirma cita.** |
| 2 | user | "12:30" | Agente invoca tool con ISO miércoles 12:30. |

### S11 — Tool devuelve ocupado con alternativas (lead Cancún — conversión de alternativas)

**Setup:** lead "Ana de Cancún" (Δ=+1h), ya eligió martes 12:00 hora Cancún (= 11:00 CDMX).

Setup mock: la tool devuelve `{libre: false, motivo: "ocupado", alternativas: ["10:00","10:30","12:30"]}` en hora CDMX.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "El martes a las 12" | Agente convierte a CDMX (11:00), invoca tool → ocupado + alternativas. Convierte las 3 alternativas a hora Cancún (+1h): 11:00, 11:30, 13:30. Ofrece: "El martes a las 12 está ocupado. Tengo disponible 11:00, 11:30 o 13:30 (hora Cancún). ¿Cuál te queda?" **NO menciona hora CDMX al lead.** |

### S12 — Tool devuelve fuera_ventana (el filtrado pre-tool falló)

**Setup:** el filtrado pre-tool debería haber atrapado esto, pero por si acaso.

Setup mock: la tool devuelve `{libre: false, motivo: "fuera_ventana"}`.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | Setup previo del test: lead en zona Centro que llegó a PASO 3-4 con horario fuera de ventana | (test manual) | Agente responde: "Para el [día] el horario es 10:00, 10:30, 11:00, 11:30, 12:00 o 12:30 hora México. ¿Cuál te queda?" — repitiendo los slots del día que ya eligió. NO vuelve a PASO 2a. |

### S13 — Lead se arrepiente y cambia de día después de ver slots

**Setup:** lead "Marcos de CDMX" cualificado.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "Agendame" | Agente pregunta día (2a). |
| 2 | user | "El viernes" | Agente aplica 2b: ofrece slots del viernes. |
| 3 | user | "Uy no, mejor el jueves" | Agente reconoce el cambio de día → invoca `listar_disponibilidad_dia` (fecha=jueves) → ofrece los `slots_libres` del jueves. **NO bookea el viernes con `check_disponibilidad`.** No pide re-cualificación. |

### S14 — Anti-regression: NO listar los 6 slots en el turno inicial

**Setup:** lead "Kevin de CDMX" cualificado, pide agendar por primera vez.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "Ok, agendemos la videollamada" | Agente pregunta solo el día. **CRÍTICO: los strings "10:00", "10:30", "11:00", "11:30", "12:00", "12:30" NO deben aparecer en la respuesta de este turno.** Si aparecen → regression del v1.19. La única mención horaria aceptable en el turno inicial es "lunes a viernes" (referencia al día, no a los slots). |

### S15 — Lead responde con día ambiguo → agente pide precisar

**Setup:** lead cualificado.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "Cuando pueda esta semana" | Agente reconoce que "esta semana" no es un día concreto y pide precisar: "¿Qué día concreto te queda mejor esta semana? Lunes, martes, miércoles, jueves o viernes." **NO ofrece slots todavía.** NO elige día por su cuenta. NO invoca la tool sin un día concreto. |
| 2 | user | "Miércoles" | Agente invoca `listar_disponibilidad_dia` (fecha=miércoles) → aplica 2b con `slots_libres`. |

### S16 — Día LLENO (`slots_libres` vacío) — corazón del fix

**Setup:** lead "Bruno de CDMX" cualificado. Mock: `listar_disponibilidad_dia` devuelve `{status:"OK", fecha, dia_humano:"viernes...", slots_libres:[], mensaje:"No hay cupos..."}`.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "Agendame el viernes" | Agente invoca `listar_disponibilidad_dia` (fecha=viernes) → recibe `slots_libres: []` → **NO ofrece ningún horario** → rebote al PASO 2a: "Para el viernes ya no me quedan cupos libres. ¿Te sirve otro día de esta semana o la próxima?" **CRÍTICO: NO inventa slots. NO ofrece 10:00-12:30.** |
| 2 | user | "El lunes" | Agente invoca `listar_disponibilidad_dia` (fecha=lunes) → ofrece los `slots_libres` de ese día. |

### S17 — Día PARCIALMENTE ocupado — solo ofrece los libres

**Setup:** lead "Vera de GDL" cualificada. Mock: `listar_disponibilidad_dia` para el jueves devuelve `{status:"OK", slots_libres:["11:30","12:00","12:30"], ...}` (10:00/10:30/11:00 ocupados).

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "El jueves" | Agente ofrece SOLO los 3 libres: "Genial, para el jueves tengo libre (hora México, CDMX): 11:30, 12:00 o 12:30. ¿Cuál te queda?" **CRÍTICO: NO menciona 10:00, 10:30 ni 11:00 — están ocupados y la tool los excluyó.** |
| 2 | user | "10:00" (pide un ocupado) | Agente NO invoca `check_disponibilidad` con 10:00. Repite los libres: "Para el jueves tengo libre 11:30, 12:00 o 12:30. ¿Cuál te queda?" |
| 3 | user | "12:00" | Agente invoca `check_disponibilidad` con ISO jueves 12:00 CDMX. |

### S18 — `status: NO_VALIDO` desde la tool (sábado via tool)

**Setup:** el filtrado pre-tool del día debería atrapar el sábado en 2a, pero si no lo hace y la tool recibe un sábado, devuelve `{status:"NO_VALIDO", motivo:"no_laboral", slots_libres:[], mensaje:"Solo... lunes a viernes..."}`.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | (test manual) lead da un día que llega como sábado a la tool | — | Agente usa el `mensaje` de la tool y rebota al PASO 2a: "Solo tomamos lunes a viernes. ¿Qué día te queda?" NO ofrece slots. |

---

## §T — Anti-regression heredado (spot-check rápido)

Ejecutar estos casos SOLO si sospechás que el bump v1.20 rompió algo del flow previo. Si §S pasa 100%, §T es opcional.

### T1 — Gate de precio (§9 v1.17)

**Setup:** lead nuevo, sin nombre ni ubicación declarados.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "Hola, cuánto cuesta la máquina?" | Agente NO da precio. Pide nombre + ciudad con framing de cortesía. Los strings "9,300", "26,300", "165,000", "460,000" NO aparecen. |

### T2 — Prohibición cita sin tool

**Setup:** lead cualificado da día + hora válidos.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "El jueves 11:00" | Agente invoca `check_disponibilidad` ANTES de confirmar. NO dice "listo, te agendo" ni variantes sin haber visto `libre: true` en la respuesta de la tool. |

### T3 — NO preguntar huso al lead (§REGLA #2)

**Setup:** lead "Carlos de Tijuana" cualificado.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "Agendame" | Agente pregunta día. **NO pregunta huso.** Frases prohibidas: "¿en qué huso estás?", "¿tu zona es Pacífico o Centro?", "confirmame en qué huso estás en Tijuana". |
| 2 | user | "El martes" | Agente ofrece slots del martes en hora Tijuana (Δ=-2h verano default): 8:00, 8:30, 9:00, 9:30, 10:00, 10:30. |

---

## Notas operativas

- **Cómo correr el testing automatizado:**
  ```bash
  source .env && python3 scripts/testing/run-agent-tests.py \
    --system-prompt clients/TFO_TOFO/04_agents/agente-tofo-b2b-system-prompt.md \
    --testing-guide clients/TFO_TOFO/07_testing/testing-guide-v10.md \
    --model gpt-4.1 \
    --dry-run
  ```
  (Confirmar modelo con la agencia antes de correr sin `--dry-run` — el B2B vive en producción sobre gpt-4.1 según CLIENT_INFO. Si el sub-workflow no está mockeable, S10-S12 quedan como manual-only en n8n.)

- **Casos manual-only en n8n:** S3 turno 3, S8 turno 4, S10-S12 involucran invocación real de `check_disponibilidad`. Si el test runner no mockea tool responses, esos turnos van a testing-guide-v10-manual.md o se ejecutan en n8n con conversaciones de prueba dedicadas.

- **Bloqueante para promover v1.20 a producción:**
  - [ ] §S1-S15 pasan 100% en testing automatizado o manual
  - [ ] §S14 verificado explícitamente (anti-regression del turno inicial)
  - [ ] Prompt v1.20 pegado al Google Doc vivo del cliente
  - [ ] Verificar en el n8n vivo que el AI Agent B2B tenga el `systemMessage` actualizado

- **Deploy de la tool (bloqueante):** importar `03_workflows/listar-disponibilidad-dia-tofo-v1.json` a n8n → anotar el workflowId que asigne → cablear al main como toolWorkflow `listar_disponibilidad_dia` con `$fromAI` en `fecha` (descripción: "Día a consultar en formato YYYY-MM-DD, hora CDMX") → verificar credencial `Google Calendar account` (`z0IngCgigP1wgAux`) conectada. Correr los 3 smokes (jsonExample en el Trigger) antes de cablear.
- **✅ Coherencia `check_disponibilidad` resuelta:** el **v6** (`chequear-disponibilidad-tofo-v6.json`) ya valida hora ∈ {10,11,12} + minutos ∈ {0,30} = los 6 slots, y calcula alternativas sobre los 6. Alineado con `listar_disponibilidad_dia`. Ambos leen con credencial `Google Calendar account 2` (`CVeDywE8Gb5JgEjC`). Verificar que el v6 esté efectivamente deployado en el n8n vivo (id `vpLmZ299yXJrOSBv`).
