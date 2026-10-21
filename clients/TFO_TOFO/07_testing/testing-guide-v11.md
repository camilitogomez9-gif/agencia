# Testing Guide v11 — Agente B2B TOFO Pizza

**Versión del prompt:** v1.21
**Fecha:** 2026-07-01
**Herencia:** §A-§R (v9) + §S-§T (v10) permanecen vigentes, **con 2 excepciones reescritas por este bump: S8 y S12** (ver abajo — el comportamiento que testeaban quedó superseded por el escalamiento). No re-correr §A-§R/resto de §S/§T salvo regression.

---

## Contexto del bump v11

Testing focalizado en el cambio v1.20 → v1.21: **cuando el lead pide un horario fuera de la ventana estándar (10:00-12:30 CDMX) en día Lunes a Viernes, el agente ya NO rebota pidiendo otro horario — escala la conversación al director** vía `elevar_conversacion(tipo='b2b')` + un mensaje avisando que lo pone en contacto con Mauricio (instrucción Mauricio, dictada 1/7/26).

Fin de semana y fecha pasada **no cambian** — siguen con rechazo canónico simple, sin escalar (Mauricio no revisó ese comportamiento).

**⚠️ S8 y S12 de testing-guide-v10.md quedan SUPERSEDED** — testeaban exactamente el escenario "hora fuera de ventana en día ya validado L-V" con el comportamiento VIEJO (rebotar pidiendo otro horario). Ese comportamiento ahora es INCORRECTO. Se reescriben acá con el resultado esperado correcto. No usar la versión de v10 para esos 2 casos.

---

## §S — Nuevo flow de agendamiento (heredado de v10, sin cambios salvo S8/S12)

Los casos S1-S7, S9-S11, S13-S18 de `testing-guide-v10.md` **siguen vigentes tal cual** — no involucran horarios fuera de ventana, no se ven afectados por este bump. No se repiten acá; consultar v10.

### S8 — Hora fuera de ventana (después de dar día) → REESCRITO: ahora ESCALA

**Setup:** lead "Luis de Puebla" cualificado (Centro, Δ=0h).

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "Agendame" | Agente pregunta el día. |
| 2 | user | "Viernes" | Agente invoca `listar_disponibilidad_dia` (fecha=viernes) → PASO 2b: ofrece los `slots_libres` para el viernes en hora CDMX. |
| 3 | user | "9 de la mañana" | 9:00 CDMX cae fuera de [10:00, 12:30] en día L-V → agente **escala**: manda un mensaje al estilo "ese horario me queda fuera de la agenda estándar del director, te pongo en contacto con Mauricio..." (no calcar literal) + invoca `elevar_conversacion(tipo='b2b')`. **CRÍTICO — NO debe pasar:** NO invoca `check_disponibilidad` con 09:00. NO repite los slots del viernes ("10:00, 10:30, 11:00...") como alternativa. NO dice "queda agendada" ni ninguna variante de confirmación. NO revela que está usando una tool. |

(Sin turno 4 — tras la escalación, el hilo queda pausado para que Mauricio lo retome; no hay continuación esperada del agente en el mismo test.)

### S12 — Tool devuelve `fuera_ventana` (red de seguridad) → REESCRITO: ahora ESCALA

**Setup:** el filtrado pre-tool debería haber atrapado esto antes de invocar la tool, pero por si el modelo se salteó el filtro y de todos modos invocó `check_disponibilidad` con una hora inválida.

Setup mock: la tool devuelve `{libre: false, motivo: "fuera_ventana"}`.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | Setup previo del test: lead en zona Centro que llegó a PASO 3-4 con horario fuera de ventana y la tool respondió `fuera_ventana` | (test manual) | Agente aplica el mismo procedimiento de escalamiento: mensaje canónico + `elevar_conversacion(tipo='b2b')`. **CRÍTICO — NO debe pasar:** NO repite "10:00, 10:30, 11:00, 11:30, 12:00 o 12:30" como si fuera una alternativa a elegir (ese era el comportamiento viejo, v1.20). NO vuelve a invocar `check_disponibilidad` para ese horario. |

---

## §U — Escalamiento fuera-de-ventana (nuevo v1.21)

Todos los casos asumen que el gate de §9 (nombre + ubicación) ya está cumplido.

### U1 — Horario después del cierre, lead Centro

**Setup:** lead "Fernanda de CDMX" cualificada, ya en PASO 2b habiendo recibido slots del martes.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "El martes a las 14:00" | 14:00 CDMX cae después de 12:30 en día L-V → agente **escala**: mensaje avisando que la pone en contacto con Mauricio + invoca `elevar_conversacion(tipo='b2b')`. NO invoca `check_disponibilidad`. NO ofrece los slots del martes como alternativa antes de escalar. |

### U2 — Horario antes de la apertura, lead Centro (día + hora en un solo turno)

**Setup:** lead "Gonzalo de Guadalajara" cualificado, primer mensaje de agendamiento.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "Agendame el miércoles a las 8" | 8:00 CDMX cae antes de 10:00 en día L-V (miércoles) → agente **escala** directo, sin pasar primero por PASO 2a/2b ni ofrecer slots del miércoles. Invoca `elevar_conversacion(tipo='b2b')`. NO invoca `check_disponibilidad` con 08:00. |

### U3 — Sábado a una hora "fuera de ventana" → sigue siendo rechazo canónico, NO escala

**Setup:** lead "Ximena de Monterrey" cualificada.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "El sábado a las 15" | Sábado ≠ L-V → agente responde: "Solo tomamos lunes a viernes. ¿Qué día te queda?" **CRÍTICO: NO invoca `elevar_conversacion`.** La regla del día (sábado) gana sobre la regla de la ventana — el escalamiento es SOLO para L-V. |

### U4 — Fecha pasada → sigue siendo rechazo canónico, NO escala

**Setup:** lead "Iván de Puebla" cualificado.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "Agendame el 10 de junio a las 9" (fecha en el pasado según Contexto temporal del User Message) | Agente responde: "Esa fecha ya pasó. ¿Te queda otro día esta semana o la próxima?" **CRÍTICO: NO invoca `elevar_conversacion`** — no hay nada que escalar en una fecha que ya pasó. |

### U5 — Minutos no redondos DENTRO de la ventana → pide minuto válido, NO escala

**Setup:** lead "Renata de León" cualificada, ya con día jueves elegido.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "El jueves a las 11:15" | 11:00 está dentro de la ventana, el problema es el minuto → agente pide minuto válido repitiendo los `slots_libres` del jueves: "Las reuniones empiezan en punto o y media..." **NO invoca `elevar_conversacion`** — el minuto se corrige, no se escala. |

### U6 — Minutos no redondos Y fuera de ventana → gana la ventana, escala

**Setup:** lead "Tomás de CDMX" cualificado, día lunes ya elegido.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "El lunes a las 14:15" | 14:00 ya está fuera de ventana (después de 12:30); el minuto `:15` es secundario → agente **escala** (mensaje canónico + `elevar_conversacion(tipo='b2b')`). **NO** responde solo pidiendo un minuto válido ("¿:00 o :30?") — sería tratar el síntoma equivocado. |

### U7 — Lead con huso fuera de Centro pide horario que, convertido, cae fuera de ventana

**Setup:** lead "Paola de Culiacán" (Δ=-1h) cualificada, día jueves ya elegido.

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "El jueves a las 8 de la mañana" (hora Culiacán, sin aclarar huso) | Agente asume hora local Culiacán (no pregunta huso — REGLA #2), convierte: 8 hora Culiacán = 9:00 CDMX, fuera de [10:00,12:30] → **escala** (mensaje canónico + `elevar_conversacion(tipo='b2b')`). **NO pregunta el huso al lead en ningún momento de este intercambio.** NO invoca `check_disponibilidad`. |

### U8 — Anti-regression: `elevar_conversacion` NO se usa para casos no relacionados

**Setup:** lead "Bruno de Tijuana" responde con monosílabos varios turnos sin interés en agendar (lead frío, no relacionado a horarios).

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | "ok" | Agente NO invoca `elevar_conversacion` — este no es ninguno de los 3 casos válidos (post-cita, error técnico, fuera-de-ventana L-V). Sigue el protocolo normal de leads fríos (§9 Edge case F), sin escalar. |

---

## §T — Anti-regression heredado (spot-check rápido)

Ejecutar solo si sospechás que el bump v1.21 rompió algo del flow previo (gate de precio, prohibición de cita sin tool, deducción de huso). Ver `testing-guide-v10.md` §T — sin cambios, no se repite acá.

---

## Notas operativas

- **Cómo correr el testing automatizado:**
  ```bash
  source .env && python3 scripts/testing/run-agent-tests.py \
    --system-prompt clients/TFO_TOFO/04_agents/agente-tofo-b2b-system-prompt.md \
    --testing-guide clients/TFO_TOFO/07_testing/testing-guide-v11.md \
    --model gpt-4.1 \
    --dry-run
  ```
  (Confirmar modelo con la agencia antes de correr sin `--dry-run`.)

- **Casos manual-only en n8n:** S12 (mock de motivo `fuera_ventana`), y cualquier caso donde haga falta confirmar que `elevar_conversacion` efectivamente se invocó (el test runner de texto no puede verificar tool calls reales — puede verificar que el TEXTO de la respuesta no contiene confirmaciones prohibidas ni listas de slots, pero la invocación de la tool en sí requiere n8n). U1, U2, U6, U7 son verificables por texto (el mensaje no debe mencionar slots ni confirmar cita) pero la tool call en sí es manual-only.

- **Bloqueante para promover v1.21 a producción:**
  - [ ] §U1-U8 pasan 100% en testing automatizado (texto) + verificación manual en n8n de que `elevar_conversacion` se invoca en U1/U2/U6/U7 y NO se invoca en U3/U4/U5/U8
  - [ ] S8 y S12 re-verificados con el comportamiento nuevo (no el de v10)
  - [ ] Prompt v1.21 pegado al Google Doc vivo del cliente (reemplaza v1.20/v1.17 — verificar cuál está efectivamente en el `systemMessage` del nodo AI Agent B2B antes de pegar, dado que v1.20 seguía pendiente de deploy)
  - [ ] Verificar en el n8n vivo que `elevar_conversacion` acepta ser invocada sin `check_disponibilidad` previa (revisar el sub-workflow — no debería requerir contexto de una cita agendada, solo `tipo='b2b'` y el `subscriber_id`/`canal` que ya usa hoy)
