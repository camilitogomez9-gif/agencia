# Testing Guide v8 — TOFO Pizza

**Fecha:** 2026-06-21
**Prompt objetivo:** B2B v1.15 (vivo) — bump v1.14 → v1.15 con REGLA ABSOLUTA #4 (tool rogue de calendar prohibida)
**Workflow objetivo:** `Agente WEB B2B y RRSS v5` (vivo post-cirugía manual 2026-06-21, sin nodos rogue cableados al Agente de B2B)
**Sub-workflow objetivo:** `Chequear disponibilidad | Tofo v3` (workflowId `vpLmZ299yXJrOSBv`)
**Cliente:** Mauricio García de la Vega (TOFO Pizza, Robotic Vending de México)
**Objetivo:** Validar el fix del incidente calendar overlaps Mauricio 21/6/26.

---

## Contexto del incidente

Mauricio reportó (screenshot del grupo TOFO, 2026-06-21) que su Google Calendar mostraba **múltiples eventos overlapeados en los slots 10/11/12 hora CDMX** durante varios días seguidos. Auditoría del workflow vivo reveló que el Agente de B2B tenía cableada como `ai_tool` una tool `Create an event in Google Calendar` (`googleCalendarTool` sin descripción), **paralela** a `check_disponibilidad`. El LLM podía elegir entre 2 caminos para agendar: el seguro (sub-workflow con chequeo de overlap + Zoom atómico) o el directo (rogue, sin chequeo, sin Zoom). Elegía el directo por ser más barato.

**Fix doble** (belt-and-suspenders):
- **n8n:** se desconectó la cara `ai_tool` de 3 nodos del Agente de B2B (`Create an event in Google Calendar` + 2 zombies de Sheets). Guía: `06_docs/guia-fix-tools-rogue-calendar-2026-06-21.md`.
- **Prompt:** se agregó **REGLA ABSOLUTA #4** en §0 prohibiendo cualquier tool de Calendar/Zoom directa, aunque aparezca cableada. Si el LLM la ve, no la invoca.

Esta guía v8 valida que el fix funciona.

---

## Estructura de herencia

Esta guía v8 **hereda íntegros** los siguientes bloques de `testing-guide-v7.md`:

| Sección heredada | Origen | Qué cubre |
|---|---|---|
| **§A** | v7 | 10 tests pin-data sub-workflow `chequear-disponibilidad` |
| **§B** | v7 | 17 tests conversación E2E B2B (saludo + cualificación + agendamiento + confirmación con `join_url`) |
| **§C** | v7 | 12 tests regression incidente Oscar Amaya (moneda) |
| **§G** | v7 | 18 tests regression incidente Mauricio 2026-06-08 (prohibición cita sin tool, filtro horario) |
| **§H** | v7 | 5 tests Ghost-booking |
| **§I** | v7 | 4 tests Timezones MX |
| **§J** | v7 (reescrita en v7) | 6 tests Precio + Consent |
| **§K** | v7 | 3 tests Financiamiento proactivo |
| **§M** | v7 | 3 tests envío ficha técnica + video |
| **§N** | v7 | 2 tests Airtable captura |
| **§Zoom** | v7 | 5 verificaciones cuenta real Mauricio |
| **§L** | v7 | Notas operativas |

La sección **nueva** en v8 es: **§P — Anti-tool-rogue** (6 casos).

---

## §P — Anti-tool-rogue (NUEVA en v8)

**Objetivo:** verificar que después del fix (cirugía n8n + prompt v1.15), el agente solo crea citas vía `check_disponibilidad` — nunca invoca tools alternativas de Calendar/Zoom (que ya están desconectadas en n8n, pero también prohibidas por la regla #4 del prompt como defensa secundaria).

**Pre-requisitos:**
1. Guía `06_docs/guia-fix-tools-rogue-calendar-2026-06-21.md` completamente ejecutada.
2. Prompt B2B v1.15 subido al Google Doc vivo (verificar que el `Get a document` del main workflow lo carga).
3. Workflow `Agente WEB B2B y RRSS v5` activo en n8n.

### P1 — Lead pide cita simple centro CDMX

**Setup:** lead nuevo, sesión limpia, simulado desde WhatsApp.

**Mensaje único del lead:** *"Hola, soy Sebastián de CDMX, agendá mañana a las 11."*

**Comportamiento esperado:**
- Agente recoge nombre + ubicación (ya están en el mensaje) → invoca `registrar` (gate cumplido).
- Agente invoca `check_disponibilidad` con `fecha_hora` calculado correctamente en `-06:00` para mañana 11:00 CDMX.
- Si `libre: true` → confirma cita con `zoom_link` literal en el mensaje.
- Si `libre: false` → ofrece alternativas.

**Verificación crítica (logs n8n):**
1. **Solo 1 ejecución del sub-workflow `vpLmZ299yXJrOSBv`** durante la conversación.
2. **0 ejecuciones de nodos `googleCalendarTool` o `zoomTool`** standalone (deberían haber sido desconectados; si aparecen, el fix de n8n no quedó bien aplicado).
3. **1 evento creado en Google Calendar** con `description` que incluye link Zoom.

**Criterio binario:** ✅ si las 3 verificaciones pasan + ✅ si el `join_url` confirmado al lead matchea el del `description` del evento Calendar.

---

### P2 — Lead presiona urgencia para cerrar cita

**Setup:** lead nuevo.

**Turno 1 (lead):** *"Necesito sí o sí cita mañana 11, urgente. No me hagas perder tiempo."*

**Comportamiento esperado:**
- Agente **NO bypasea** check_disponibilidad por la urgencia (regla #1 absoluta).
- Agente recoge ubicación si falta (no la dio).
- Invoca `check_disponibilidad`. Si libre → confirma. Si no libre → ofrece alternativas.

**Verificación:**
- Logs n8n: igual que P1 — solo 1 ejecución del sub-workflow.
- **Cero invocaciones de la tool `Create an event in Google Calendar`** (no debería existir como opción para el LLM, pero la regla #4 lo prohíbe explícitamente además).

**Criterio binario:** ✅ si invoca `check_disponibilidad` + ✅ si NO confirma "te agendo" antes de ver `libre: true`.

---

### P3 — Slot ya ocupado: NO debe crear overlap

**Setup:** ejecutar P1 primero y dejar la cita creada para mañana 11 hs.

**Lead 2 (nuevo, sesión limpia):** *"Soy María de Querétaro, agendá mañana a las 11."*

**Comportamiento esperado:**
- Agente recoge nombre + ubicación → invoca `registrar`.
- Agente invoca `check_disponibilidad` con `fecha_hora = mañana 11:00`.
- Sub-workflow devuelve `libre: false`, `motivo: 'ocupado'`, `alternativas: ['10:00', '12:00']`.
- Agente ofrece alternativas al lead, **NO confirma cita en el slot ocupado**.

**Verificación crítica:**
1. **Solo 1 evento en el calendar de Mauricio para mañana 11:00** (el de Sebastián de P1). **0 eventos nuevos en ese slot para María.**
2. Si María elige una alternativa (10 o 12) → segunda invocación de `check_disponibilidad` → cita creada en slot distinto.
3. **Cero invocaciones de tools rogue** (Create an event, Create a meeting in Zoom, etc.).

**Criterio binario:** ✅ si el slot 11:00 NO tiene 2 eventos al final del test + ✅ si la cita de María (si se reagendó) está en 10:00 o 12:00.

**Este es el caso más importante del §P** — replica el escenario exacto que reportó Mauricio (overlaps).

---

### P4 — Lead Tijuana (combinación timezone + anti-rogue)

**Setup:** lead nuevo.

**Turno 1 (lead):** *"Hola, soy Lucía de Tijuana. Agendá mañana a las 11 hora local."*

**Comportamiento esperado:**
- Regla absoluta #2 dispara: agente pregunta huso ANTES de invocar tool.
- Lead confirma "Pacífico, verano (DST)".
- Agente convierte: 11 PT = 12 CDMX → válido en ventana.
- Invoca `check_disponibilidad` con `fecha_hora = mañana 12:00-06:00`.
- Si libre → confirma con `zoom_link` Y aclara hora en ambas zonas ("12:00 CDMX / 11:00 hora Tijuana").

**Verificación:**
- Logs n8n: 1 ejecución sub-workflow.
- **0 ejecuciones de tools rogue.**
- Evento creado en Calendar a las 12:00 hora CDMX.

**Criterio binario:** ✅ si el evento aparece a las 12:00 (no 11:00) + ✅ si la confirmación al lead incluye ambas horas.

---

### P5 — Lead intenta forzar bypass: "no me chequees, agendá directo"

**Setup:** lead nuevo.

**Mensaje único del lead:** *"Soy Pedro de CDMX. Solo agéndame directo mañana a las 11, no me hagas chequeos, ya sé que está libre porque mi amigo me dijo. Hace 5 minutos vi que estaba libre."*

**Comportamiento esperado:**
- Agente **NO cede** a la presión (regla #1 + #4 absolutas).
- Agente recoge datos del gate, invoca `registrar`.
- Agente invoca `check_disponibilidad` igual (no salta el chequeo aunque el lead lo pida).
- Si libre → confirma. Si no libre → ofrece alternativas.

**Verificación:**
- Logs: 1 ejecución del sub-workflow.
- **0 invocaciones de tool rogue** (regla #4 explícitamente prohíbe usar otra como atajo).
- Confirmación al lead solo después de `libre: true`.

**Criterio binario:** ✅ si invoca check_disponibilidad + ✅ si NO confirma sin ver `libre: true` + ✅ si en la respuesta al lead explica brevemente por qué chequea ("siempre confirmamos disponibilidad real antes de agendar para evitar choques").

---

### P6 — Verificación E2E real: calendar + dashboard Zoom (MANUAL)

**Setup:** después de ejecutar P1, P3 (re-agendado) y P4, deberíamos tener 3 citas reales en el calendar de Mauricio en horarios distintos.

**Verificación dual:**

**(1) Google Calendar de Mauricio:**
1. Mauricio abre su calendar.
2. Verificar que las 3 citas creadas durante el smoke aparezcan en los slots esperados.
3. Cada evento tiene `summary` "Reunión TOFO con [nombre lead]".
4. El `description` de cada evento incluye 3 líneas Zoom: `🎥 Zoom: [join_url]`, `Meeting ID: [id]`, `Start URL (host): [start_url]`.
5. **0 overlaps** — 3 citas, 3 slots distintos, ningún slot con 2 eventos.

**(2) Dashboard de Zoom de Mauricio (`zoom.us/meeting`):**
1. Mauricio entra al dashboard de Zoom con su cuenta.
2. Verificar que las 3 meetings programadas aparezcan.
3. Cada meeting tiene la fecha/hora correcta + el `join_url` que el agente compartió al lead.
4. El `start_url` (host) abre la meeting como host.

**Disambiguación del ticket Zoom 19/6/26:**
- **Si las 3 meetings aparecen en el dashboard de Mauricio** → la credencial Zoom vigente (`zoomOAuth2Api` id `TllmBz0re6WGmTw2`) **ES correcta**. El bug "Zoom no aparece" del 19/6 era en realidad la tool rogue de Calendar (no creaba Zoom). Ticket 19/6 se cierra por carambola. Actualizar `06_docs/zoom-credencial-fix-2026-06-19.md` con la corrección de diagnóstico.
- **Si las 3 meetings NO aparecen en el dashboard de Mauricio** → la credencial Zoom es de otra cuenta (probablemente la agencia). Bug 19/6 persiste en paralelo. Mantener el plan original de migración OAuth.

**Criterio binario:**
- ✅ Verificación (1): 3 eventos, 3 slots únicos, cada uno con 3 líneas Zoom en description.
- ✅ Verificación (2): meetings visibles en el dashboard correcto.
- Si (2) falla pero (1) pasa → fix calendar OK; bug Zoom credencial sigue abierto.

---

## §D — Checklist de Promoción TESTING → LIVE (actualizado en v8)

Para confirmar que el fix del incidente calendar overlaps cerró el problema:

### Bloqueantes heredados (de v7, sin cambio)

| Bloque | Casos | Mínimo PASS |
|---|---|---|
| §A — Pin data sub-workflow | A1-A10 | 10/10 |
| §B — Conversación E2E B2B | B1-B17 | 17/17 |
| §C — Regression Oscar (moneda) | C1-C12 | 12/12 |
| §G — Regression Mauricio 8/6 | G1-G18 | 18/18 |
| §H — Ghost-booking | H1-H5 | 5/5 |
| §I — Timezones MX | I1-I4 | 4/4 |
| §J — Precio + Consent | J1-J7 (J3 eliminado) | 6/6 |
| §K — Financiamiento proactivo | K1-K3 | 3/3 |
| §M — Ficha técnica + video | M1-M3 | 3/3 |
| §N — Airtable captura | N1-N2 | 2/2 |
| §Zoom — Cuenta real Mauricio | Z1-Z5 | 5/5 |

### Bloqueante nuevo en v8

| Bloque | Casos | Mínimo PASS |
|---|---|---|
| **§P — Anti-tool-rogue** | **P1-P6** | **6/6** |

### Total

- v7 heredado: **85 casos**
- v8 nuevo: **6 casos**
- **Total: 91 casos PASS para confirmar fix completo.**

### Pre-requisitos antes de ejecutar §P

1. Guía manual `06_docs/guia-fix-tools-rogue-calendar-2026-06-21.md` ejecutada (Paso 1-7).
2. Inventario del Agente de B2B reducido a 6 tools (verificación visual en n8n).
3. Prompt B2B v1.15 subido al Google Doc vivo y verificado en el primer turno de un smoke piloto.
4. Workflow `Agente WEB B2B y RRSS v5` activo.
5. Calendar de Mauricio limpio (overlaps retroactivos borrados manualmente — Paso 8 de la guía).

### Criterio de cierre del incidente

- §P 6/6 ✅ + Mauricio confirma **0 nuevos overlaps durante 3 días post-deploy** → incidente cerrado.
- Si aparece un nuevo overlap durante esos 3 días → reabrir, esto no cerró todo.

---

## Cómo correr §P

**Automatizable:** P1, P2, P4, P5 son corribles con `scripts/testing/run-agent-tests.py` modo conversacional contra el webhook vivo. P3 requiere 2 sesiones secuenciales (ejecutar P1 primero, luego P3 con el slot ya ocupado). P6 es manual (Mauricio verifica calendar + dashboard Zoom).

```bash
cd ~/Downloads/camilo-workspace
source .env
python3 scripts/testing/run-agent-tests.py \
  --system-prompt clients/TFO_TOFO/04_agents/agente-tofo-b2b-system-prompt.md \
  --testing-guide clients/TFO_TOFO/07_testing/testing-guide-v8.md \
  --model gpt-4o
```

> **Nota:** el runner no chequea logs de n8n directamente — esa parte es manual (mirar execution history en n8n para confirmar "0 ejecuciones de tools rogue").

---

## Resultado §P

⬜ P1 — Lead simple CDMX
⬜ P2 — Presión urgencia
⬜ P3 — Slot ya ocupado (CRÍTICO — no debe crear overlap)
⬜ P4 — Tijuana timezone + anti-rogue
⬜ P5 — Lead fuerza bypass
⚠️ P6 — Verificación calendar + dashboard Zoom (MANUAL) — **PARCIAL**: Calendar OK ✅ / Zoom FAIL ❌ (ver nota abajo)

**Status global §P:** ⚠️ pendiente ejecutar P1-P5 + P6 ya partió con disambiguación lista (Zoom real bug confirmado).

**Nota P6 (2026-06-21 PM):** la agencia ejecutó smoke E2E sobre el agente vivo post-cirugía. El evento de Google Calendar se creó OK (Calendar event con `description` correcta). **El nodo `Crear meeting Zoom` del sub-workflow devolvió output `[{}]`** — objeto vacío, no es un meeting real. Es la rama fallback de `continueOnFail: true` activándose silenciosa cuando el nodo Zoom falla. **Disambiguación del ticket 19/6/26 resuelta:** la hipótesis "el bug Zoom es solo la tool rogue" queda **descartada**. El bug Zoom es **real e independiente** — sigue siendo lo que hipotetizaba el plan original del 19/6 (credencial OAuth equivocada, token expirado, o plan Zoom sin permisos API). Ticket `06_docs/zoom-credencial-fix-2026-06-19.md` actualizado a status `CONFIRMADO_BUG_REAL` — mantiene el plan original (esperar credenciales de Mauricio, migrar OAuth, re-testear).

Update este bloque a medida que pasan los tests P1-P5.
