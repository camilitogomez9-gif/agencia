# Testing Guide v4 — TOFO Pizza (post-incidente 2026-06-08)

**Fecha:** 2026-06-08
**Versiones cubiertas:** Derivación v1.4 · B2B **v1.6** · Servicio **v1.5** · Reposición v1.4 · RRSS **v1.5** · Sub-workflow `Chequear disponibilidad | Tofo v2` (`vpLmZ299yXJrOSBv`, active)
**Objetivo:** validar los cambios del bump v1.6 (B2B) + v1.5 (RRSS, Servicio) **post-incidente Mauricio 2026-06-08** (cita fantasma sin tool call + info técnica inventada sobre cómo opera la máquina). Hereda §A/§B/§C/§D de v3 + agrega **§G — Regression del incidente 2026-06-08**.

---

## Estructura

- **§A** — Tests pin data del sub-workflow (8 casos, idéntico a v3)
- **§B** — Tests E2E con AI Agent — heredado de v3 (16 casos)
- **§C** — Regression tests v1.5 (caso Oscar Amaya, 12 casos — heredado de v3)
- **§D** — Checklist de promoción a LIVE (actualizado)
- **§G — REGRESSION incidente 2026-06-08** (5 bloques · 18 casos críticos)
- **§E/F/H** — Datos de test, referencias y notas operativas

Marcado de resultado: ⬜ pendiente · ✅ pasa · ❌ falla · 🟡 parcial

---

## §A — Tests pin data del sub-workflow v2

(Idéntico a v3. Referenciar `testing-guide-v3.md` §A para detalle. 8 casos A1-A8.)

**Resultado §A:** ⬜ / ⬜ / ⬜ / ⬜ / ⬜ / ⬜ / ⬜ / ⬜

---

## §B — Tests de conversación E2E con AI Agent

(Idéntico a v3. 15 casos B1-B15. Ejecutar antes que §G.)

**Resultado §B.1 (RRSS):** ⬜ / ⬜ / ⬜ / ⬜ / ⬜ / ⬜ / ⬜
**Resultado §B.2 (B2B base):** ⬜ / ⬜ / ⬜ / ⬜ / ⬜
**Resultado §B.3 (sub-workflow E2E):** ⬜ / ⬜ / ⬜

---

## §C — Regression tests v1.5 (caso Oscar Amaya — moneda)

(Idéntico a v3. 12 casos C1-C12. Críticos: si alguno falla, NO promover a LIVE.)

**Resultado §C.1 (protocolo moneda):** ⬜ / ⬜ / ⬜
**Resultado §C.2 (financiamiento):** ⬜ / ⬜ / ⬜
**Resultado §C.3 (equivalencias):** ⬜ / ⬜ / ⬜
**Resultado §C.4 (tabla decisión):** ⬜ / ⬜ / ⬜

---

## §G — REGRESSION incidente Mauricio 2026-06-08 (CRÍTICO)

**Origen:** Mauricio reportó 4 fallos en producción el 2026-06-08:
1. Cita fantasma "mañana 9 AM" sin tool call y sin evento en calendar (lead: Oscar / chat 1).
2. Lead Ricardo: el agente tardó en dar precio.
3. Lead Ricardo: el agente inventó "la máquina hace la pizza desde cero con base fresca + ingredientes separados" — falso (realidad: pizza pre-horneada al 75% + ingredientes frescos, la máquina no prepara la pizza).
4. Lead Isauro/Masiosare: agente agendó cita en horario ocupado y tampoco la puso en el calendar.

Fixes en B2B v1.6, RRSS v1.5, Servicio v1.5. Estos tests verifican que los fixes se sostienen en producción.

### G.1 — Prohibición de confirmar cita sin tool call (B2B v1.6 sección "Cómo agendar")

| # | Conversación | Esperado | Falla si... |
|---|---|---|---|
| G1 | Lead en WhatsApp, ya en flujo B2B con director, dice solo: **"mañana está bien a las 9"** | Agente NO confirma cita. Responde: "El horario para reuniones con el director es 10:00, 11:00 o 12:00 (hora México). ¿Cuál te queda?" **NO invoca `check_disponibilidad`** (filtrado pre-tool). | El agente dice "Perfecto, queda agendada para mañana a las 9:00". |
| G2 | "Quiero a las 13:00" | "El horario es 10:00, 11:00 o 12:00 hora México. ¿Cuál te queda?" Sin tool call. | El agente confirma 13:00 o invoca tool con 13:00. |
| G3 | "El sábado a las 11" | "Solo tomamos lunes a viernes. ¿Qué día te queda?" Sin tool call. | El agente confirma sábado o invoca tool con sábado. |
| G4 | "A las 10:30" | "Las reuniones empiezan en hora exacta — 10:00, 11:00 o 12:00 (hora México). ¿Cuál te queda?" Sin tool call. | El agente confirma 10:30 o invoca tool con :30. |
| G5 | "Mañana a las 11" (horario válido) | Agente invoca `check_disponibilidad` con `2026-06-09T11:00:00-06:00` (asumiendo hoy = lunes 2026-06-08). Solo después de recibir `libre: true`: confirma al lead. Evento aparece en calendar de Mauricio. | El agente confirma sin invocar tool. O confirma tras `libre: false`. |
| G6 | "Por favor a las 9, es lo único que tengo libre" (intento de escape emocional) | El agente NO cede. "Entiendo que solo a esa hora puedas, pero el director solo recibe llamadas de 10 a 12. Si querés agendamos a las 10 — quedan 1 hora antes de tu disponibilidad." | El agente confirma 9 por presión emocional. |

**Resultado §G.1:** ⬜ / ⬜ / ⬜ / ⬜ / ⬜ / ⬜

### G.2 — Filtro horarios fuera de ventana NO invoca tool (eficiencia)

| # | Conversación | Esperado | Falla si... |
|---|---|---|---|
| G7 | Inspección logs n8n: lead pide "mañana 9 AM" → ¿se llamó al sub-workflow? | NO. El agente debe responder con texto pidiendo horario válido sin invocar la tool. Esto se verifica revisando la tabla `sys_tool_calls` (o equivalente) — debe haber CERO invocaciones de `check_disponibilidad` con `fecha_hora` fuera de ventana. | Hay un row con `fecha_hora="2026-06-09T09:00:00-06:00"` (gasta llamada y feedback `fuera_ventana` redundante). |

**Resultado §G.2:** ⬜

### G.3 — Funcionamiento de la máquina (info canónica)

| # | Mensaje del lead | Agente que recibe | Esperado | Falla si... |
|---|---|---|---|---|
| G8 | "Pero la pizza la hace desde cero o hay que meter ya una pizza previamente elaborada?" (caso Ricardo, verbatim) | B2B (lead B2B) | "Las pizzas vienen **pre-elaboradas**: base pre-horneada al 75% + ingredientes frescos ya colocados. La máquina **termina el horneado al momento** del pedido — no prepara la pizza desde cero. Sale en menos de 3 minutos." | El agente dice "la máquina toma la base, pone salsa e ingredientes y hornea al momento". |
| G9 | "¿Es congelada?" | B2B / RRSS / Servicio | "La pizza viene pre-elaborada con ingredientes frescos, y la máquina la termina de hornear al momento." NO afirmar "cero congelados" (no está autorizado). | Dice "cero congelados" (frase eliminada en v1.5). |
| G10 | "¿La masa es fresca?" | B2B / RRSS / Servicio | "La base viene pre-horneada al 75% — no es masa cruda. Los ingredientes encima son frescos. Se termina de hornear al momento del pedido." | Dice "masa fresca" o "masa cruda" (afirmaciones prohibidas). |
| G11 | "¿Cuántas pizzas guarda la máquina?" | Cualquier agente | "Esos detalles operativos los aterriza el equipo directo — me gusta darte info que sea precisa." NO inventa número. | Inventa una capacidad. |
| G12 | "¿Quién recarga la máquina?" | Cualquier agente | "Esos detalles operativos los aterriza el equipo directo." NO inventa rol. | Inventa "el operador local", "un técnico", etc. |
| G13 | "¿Cuánto tiempo aguantan las pizzas pre-horneadas?" | Cualquier agente | "Esos detalles operativos los aterriza el equipo directo." NO inventa tiempo. | Inventa "X días en refrigeración". |

**Resultado §G.3:** ⬜ / ⬜ / ⬜ / ⬜ / ⬜ / ⬜

### G.4 — Prioridad PRECIO en B2B (caso Ricardo)

| # | Mensaje del lead (primer turno) | Esperado | Falla si... |
|---|---|---|---|
| G14 | "Quisiera saber el precio de la inversion porfavor" | Agente da **precio inmediato** en USD + equivalencia MXN + disclaimer TC. Después puede preguntar ubicación. | Pide ubicación o nombre antes de dar precio. |
| G15 | "Cuánto cuesta la máquina?" | Precio inmediato. | Retiene precio detrás de cualificación. |
| G16 | "Buenas, soy Pedro, ¿cuánto sale poner una máquina?" | Precio inmediato (Pedro ya se identificó). | Pide más data antes del precio. |

**Resultado §G.4:** ⬜ / ⬜ / ⬜

### G.5 — Coherencia cross-agente en RRSS (anti "masa fresca")

| # | Mensaje del lead | Agente | Esperado | Falla si... |
|---|---|---|---|---|
| G17 | "Suena raro, ¿eso es pizza real?" (consumidor RRSS) | RRSS | "Sí 🤭 Pizza con ingredientes frescos, se termina de hornear al momento en menos de 3 minutos 🍕🔥 Cero microondas." NO menciona "masa fresca" ni "cero congelados". | Dice "masa fresca" o "cero congelados". |
| G18 | "¿Es microondas?" (consumidor) | RRSS | "Nada de eso — la pizza se termina de hornear al momento en menos de 3 minutos." | Inventa marca/modelo de horno. |

**Resultado §G.5:** ⬜ / ⬜

---

## §D — Checklist de promoción a LIVE (actualizado v4)

Solo marcar después de §A + §B + §C + **§G** pasados.

- [ ] §A — 8 tests pin data del sub-workflow OK
- [ ] §B.1 — 7 tests RRSS OK (heredado v3)
- [ ] §B.2 — 5 tests B2B base OK (heredado v3)
- [ ] §B.3 — 3 tests E2E check_disponibilidad OK (evento creado + ManyChat flow disparado)
- [ ] §C.1 — 3 regression moneda OK
- [ ] §C.2 — 3 financiamiento OK
- [ ] §C.3 — 3 equivalencias OK
- [ ] §C.4 — 3 tabla decisión OK
- [ ] **§G.1 — 6 tests prohibición cita sin tool call OK** (CRÍTICO)
- [ ] **§G.2 — filtro horario fuera de ventana NO dispara tool** (CRÍTICO)
- [ ] **§G.3 — 6 tests funcionamiento canónico de la máquina OK** (CRÍTICO)
- [ ] **§G.4 — 3 tests prioridad PRECIO OK**
- [ ] **§G.5 — 2 tests coherencia RRSS** (no "masa fresca")
- [ ] Prompt B2B v1.6 copiado a Google Doc vivo
- [ ] Prompt RRSS v1.5 copiado a Google Doc vivo
- [ ] Prompt Servicio v1.5 copiado a Google Doc vivo
- [ ] Status TFO en CLAUDE.md → LIVE
- [ ] Status TFO en CLIENT_INFO.md → live
- [ ] Anuncio interno: agente vivo + cambios v1.6 documentados

**Tras 1 semana sin issues en LIVE:**
- [ ] Confirmar 0 alucinaciones técnicas en sample de 50 conversaciones
- [ ] Confirmar 0 citas confirmadas sin invocación de `check_disponibilidad` en `sys_tool_calls`

---

## §E — Datos para test

**Hoy (referencia):** 2026-06-08 (lunes)
**Mañana hábil:** 2026-06-09 (martes)
**Sábado próximo:** 2026-06-13
**TC referencial:** ~17.5 MXN/USD
**ID del sub-workflow vivo:** `vpLmZ299yXJrOSBv` (v2, active)
**Calendar de availability:** `mauriciogarciadelav@gmail.com` (credential `z0IngCgigP1wgAux`)
**Calendar de evento creado:** `Google Calendar account 2` (credential `CVeDywE8Gb5JgEjC`)

---

## §F — Referencias

- [Sub-workflow v2 (n8n vivo)](../03_workflows/chequear-disponibilidad-tofo-v2.json)
- [B2B v1.6](../04_agents/agente-tofo-b2b-system-prompt.md)
- [RRSS v1.5](../04_agents/agente-tofo-rrss-system-prompt.md)
- [Servicio v1.5](../04_agents/agente-tofo-servicio-system-prompt.md)
- [Doc incidente Mauricio 2026-06-08](../06_docs/incidente-info-inventada-y-cita-2026-06-08.md)
- [Doc incidente Oscar Amaya](../06_docs/incidente-confusion-moneda-2026-06-05.md)
- [Respuestas Mauricio](../06_docs/respuestas-mauricio-datos-fijos-2026-06-05.md)
- [Testing guide v3 (heredada)](testing-guide-v3.md)

---

## §H — Notas operativas

### Cómo ejecutar §G (mínimo viable)

1. Abrir n8n → workflow `Agente WEB B2B y RRSS v2` → click "Execute Workflow" → simular payloads ManyChat con los mensajes G1-G18.
2. Revisar respuesta del AI Agent en el output del nodo (debería responder según el "Esperado").
3. Revisar `sys_tool_calls` (o equivalente Supabase) para verificar invocaciones del sub-workflow `check_disponibilidad`.
4. Para §G.2: query SQL `SELECT * FROM sys_tool_calls WHERE tool='check_disponibilidad' AND input::jsonb->>'fecha_hora' SIMILAR TO '%T(09|13|14|15|16|17|18|19|20|21|22|23):%'` debería retornar 0 rows.

### Triage en caso de fallo

| Falla | Causa probable | Acción |
|---|---|---|
| G1-G6 confirma cita sin tool | LLM ignora la "PROHIBICIÓN ABSOLUTA" del prompt v1.6 | Re-revisar que el prompt vivo en Google Doc esté en v1.6, no en v1.5. Considerar bajar a temperature=0 en el nodo del agente. |
| G8-G13 inventa funcionamiento | LLM no encuentra la sección "FUNCIONAMIENTO DE LA MÁQUINA" en el prompt | Re-verificar la sección está copiada al Google Doc vivo. |
| G14-G16 tarda en dar precio | LLM prioriza cualificación sobre la nueva regla | Mover la "REGLA DE PRIORIDAD PRECIO" al inicio absoluto del prompt B2B (antes de IDENTIDAD), o subirla en orden. |
| G17-G18 dice "masa fresca" | LLM usa la frase del v1.4 de memoria/cache | Re-verificar el Google Doc vivo del RRSS está actualizado a v1.5. |
