# Testing Guide v6 — TOFO Pizza (bump prompt B2B v1.8)

**Fecha:** 2026-06-17
**Versiones cubiertas:** Derivación v1.4 · B2B **v1.8** · Servicio v1.5 · Reposición v1.4 · RRSS v1.5 · Sub-workflow `Chequear disponibilidad | Tofo v3` (`vpLmZ299yXJrOSBv`)
**Objetivo:** validar los 4 fixes del bump prompt B2B v1.7 → v1.8 derivados del análisis WhatsApp Mauricio 17/6/26 (punto 3 citas fantasma + timezone, punto 6 precio proactivo, punto 7 financiamiento proactivo). Hereda **completo** §A/§B/§C/§D/§G/§Z de v5 sin cambios estructurales — agrega 4 secciones nuevas (§H, §I, §J, §K) con casos regresivos para los fixes nuevos.

---

## Estructura

- **§A** — Tests pin data del sub-workflow v3 (10 casos heredados de v5 sin cambios)
- **§B** — Tests E2E con AI Agent (16 casos heredados de v5)
- **§C** — Regression Oscar Amaya v1.5 (12 casos heredados de v5)
- **§D** — Checklist promoción LIVE (actualizado para v1.8 — abajo)
- **§G** — Regression incidente Mauricio 2026-06-08 (18 casos heredados de v5)
- **§H — NUEVO: Ghost-booking** (5 casos — punto 3a del análisis WhatsApp)
- **§I — NUEVO: Timezones MX** (4 casos — punto 3b)
- **§J — NUEVO: Precio proactivo + productos viejos** (3 casos + 1 anti-regression — punto 6)
- **§K — NUEVO: Financiamiento proactivo** (3 casos — punto 7)
- **§L — Notas operativas** (renombrado desde §H de v5, sin cambios)
- **§Z** — Verificación end-to-end Zoom (heredado de v5)

Marcado de resultado: ⬜ pendiente · ✅ pasa · ❌ falla · 🟡 parcial

---

## §H — Ghost-booking (5 casos, punto 3a)

**Objetivo:** verificar que el agente B2B v1.8 NUNCA confirma una cita sin haber invocado `check_disponibilidad` y recibido `libre: true`. El "checkpoint mental" agregado en v1.8 debe disparar incluso bajo presión, urgencia, o cuando todos los datos parecen completos.

**Cómo ejecutar:** correr cada caso como conversación E2E desde sandbox ManyChat (canal IG o WPP) contra el agente vivo. Después de cada confirmación o no-confirmación del agente, verificar logs Postgres (tabla `sys_tool_calls` o equivalente TFO) que `check_disponibilidad` haya sido invocada **antes** de cualquier mensaje del agente que contenga la palabra "agendé", "queda", "confirmado", o equivalente.

| # | Escenario | Mensaje del lead | Comportamiento esperado | Criterio binario |
|---|---|---|---|---|
| H1 | Lead presiona "es urgente" | "Necesito agendar YA, solo a las 9 puedo mañana. Es urgente. Confírmame por favor." | Agente NO confirma. Aplica filtrado pre-tool: pide horario válido (10/11/12 hora México). Aclara que urgencia ≠ excepción. | ✅ si NO contiene frase de confirmación + ✅ si NO se invocó tool con 09:00 |
| H2 | Lead pasivo-agresivo | "Si no me agendas a las 9 me voy con la competencia." | Agente NO confirma. Mantiene la ventana 10/11/12 firme. Tono empático pero sin ceder. | ✅ si NO confirma + ✅ si ofrece horario válido |
| H3 | Lead asume cita previa fantasma | (Turno previo: el agente NO invocó tool pero dijo "te agendé para mañana 10:00"). Lead siguiente turno: "¿Ya quedó agendada la cita?" | Agente corrige: "Una corrección rápida: déjame verificar disponibilidad real con el calendario del director — ¿me confirmas día y hora otra vez?" + invoca tool con horario válido. | ✅ si reconoce el error + ✅ si invoca `check_disponibilidad` en este turno |
| H4 | Lead da todo en un turno | "Hola, soy Pedro, estoy en Guadalajara, quiero agendar llamada mañana a las 11 hora México." | Agente NO confirma sin tool. Invoca `check_disponibilidad` con `2026-MM-DDT11:00:00-06:00` PRIMERO, luego confirma al lead con el `zoom_link` literal del response. | ✅ si invoca tool ANTES de confirmar + ✅ si la confirmación incluye `zoom_link` real |
| H5 | Stress test multi-turno | Lead manda 5 mensajes rápidos con horarios variados (mezcla válidos e inválidos). Probar que el agente sostiene el checkpoint en cada turno. | Agente NO confirma sin tool en ningún turno. Filtra inválidos sin invocar. Invoca tool solo con horarios 10/11/12 hora México. | ✅ ratio invocaciones-tool / mensajes de confirmación debe ser 1:1 |

**Verificación post-ejecución:**
```sql
-- En tabla sys_tool_calls (o equivalente TFO), para cada sessionKey de testing:
SELECT
  session_key,
  tool_name,
  status,
  created_at
FROM sys_tool_calls
WHERE session_key = '<sessionKey del test>'
  AND tool_name IN ('check_disponibilidad', 'elevar_conversacion')
ORDER BY created_at;
```
Cualquier turno del agente con confirmación de cita debe tener **una invocación previa de `check_disponibilidad` con `status = RESOLVED` y `libre = true` en la respuesta**. Si no hay, es ghost booking.

**Resultado §H:** ⬜ / ⬜ / ⬜ / ⬜ / ⬜

---

## §I — Timezones MX (4 casos, punto 3b)

**Objetivo:** verificar que el agente B2B v1.8 pregunta zona horaria a leads fuera del centro de México, y que construye el ISO con offset correcto para que la cita real en el calendar del director caiga en hora CDMX 10/11/12.

**Cómo ejecutar:** correr cada caso como conversación E2E. Verificar el `start.dateTime` del evento creado en Google Calendar (debería ser siempre hora CDMX 10:00/11:00/12:00).

| # | Escenario | Mensajes del lead | Comportamiento esperado | Criterio binario |
|---|---|---|---|---|
| I1 | Lead en Tijuana | "Hola, soy Lucía, estoy en Tijuana. Quiero agendar llamada el jueves a las 11 hora local." | Agente activa PASO 1.5: pregunta zona ("¿Pacífico, Sonora o Centro?"). Lead confirma "Pacífico". Si es verano (DST): 11 PT = 12 CDMX → invoca tool con `12:00-06:00` → válido. Si invierno (sin DST): 11 PT = 13 CDMX → fuera de ventana, pide otro horario. | ✅ si pregunta TZ + ✅ si invoca tool con `12:00-06:00` (verano) o pide horario válido (invierno) + ✅ confirmación al lead incluye "(hora CDMX)" o "(11:00 tu hora local, 12:00 CDMX)" |
| I2 | Lead en Hermosillo (Sonora — sin DST) | "Soy Roberto de Hermosillo. Agéndame jueves a las 10 hora Sonora." | Agente reconoce Sonora (UTC-7 fijo). 10 hora Sonora = 11 CDMX → válido. Construye ISO `<fecha>T11:00:00-06:00`. Confirma "agendado para el jueves a las 11:00 hora CDMX (= 10:00 hora Sonora)". | ✅ si invoca tool con `11:00-06:00` + ✅ si confirmación incluye ambas horas |
| I3 | Lead ambiguo solo ciudad | "Estoy en Ciudad Juárez. Agéndame jueves 11." | Agente activa PASO 1.5 (Ciudad Juárez está en UTC-7 sin DST como Sonora, pero el agente puede no saberlo — debe preguntar). Lead aclara. Agente convierte y construye ISO. | ✅ si pregunta TZ antes de invocar tool |
| I4 | Lead "yo me arreglo" (edge case) | "Soy Carlos de La Paz BCS. Solo necesito hora local, yo me arreglo. Mañana 11 hora La Paz." | Agente NO insiste en preguntar TZ explícitamente, pero confirma usando **hora CDMX explícita** ("listo, tu cita queda 11:00 hora local = 12:00 hora CDMX en verano"). | ✅ si confirmación incluye "(hora CDMX)" además de "(hora local)" |

**Resultado §I:** ⬜ / ⬜ / ⬜ / ⬜

---

## §J — Precio proactivo + productos viejos (3 + 1 casos, punto 6)

**Objetivo:** verificar que el agente B2B v1.8 suelta precios proactivamente cuando detecta intención de compra (no solo pregunta directa), y que NO inventa productos viejos ("concesión con alquiler", "renta + compra", "$200.000 + mensualidad").

| # | Escenario | Mensaje del lead | Comportamiento esperado | Criterio binario |
|---|---|---|---|---|
| J1 | Intención implícita | "Hola, soy Marco. Quiero una máquina TOFO." | Agente dentro del primer turno: saludo breve + suelta los 2 precios (Opción A $9,300 USD ≈ $165k MXN / Opción B $26,300 USD ≈ $460k MXN) + disclaimer TC + pregunta cuál se adapta. | ✅ si menciona ambos precios en USD + ambos en MXN en el primer turno + ✅ si NO empieza con cualificación extendida |
| J2 | Frase indirecta | "¿Cómo le hago para arrancar con el negocio de TOFO?" | Agente trata como intención de compra (Escenario 2 de la REGLA). Suelta precios en el primer o segundo turno. | ✅ si precios aparecen en turno 1 o 2 |
| J3 | Dos turnos sin precio | Turno 1 lead: "Me interesa la máquina." Turno 2 lead: "Sí, quiero saber más." | Agente, en turno 3 máximo, suelta proactivamente los 2 precios (Escenario 3 de la REGLA). | ✅ si precios aparecen máximo en turno 3 |
| J4 (anti-regression) | NO es B2B | (Caso de RRSS o Servicio): "Hola, ¿dónde está la sucursal Flex Norte?" | Agente de Derivación NO clasifica B2B, NO invoca al agente B2B, NO suelta precios B2B. | ✅ si NO menciona "$9,300" o "$26,300" |
| J5 (productos viejos) | Pregunta por concesión | "¿Tienen concesión con alquiler de máquina?" | Agente responde "Hoy no manejamos esquema de concesión ni renta — solo venta directa (Opción A o B). Si lo que te preocupa es el monto inicial, te apoyamos a buscar financiamiento externo." NO inventa montos viejos ($200k inicial + renta mensual, etc.). | ✅ si NO menciona "$200,000" / "$600,000" / "renta mensual" / "concesión 4 años" + ✅ si redirige a venta + financiamiento |

**Resultado §J:** ⬜ / ⬜ / ⬜ / ⬜ / ⬜

---

## §K — Financiamiento proactivo (3 casos, punto 7)

**Objetivo:** verificar que el agente B2B v1.8 ofrece financiamiento externo proactivamente (no espera la pregunta del lead) y usa lenguaje "te apoyamos" en lugar de "puedes buscar".

| # | Escenario | Mensaje del lead | Comportamiento esperado | Criterio binario |
|---|---|---|---|---|
| K1 | Presupuesto MXN insuficiente sin preguntar financiamiento | "Soy Ana, tengo $200,000 MXN para invertir, quiero una máquina." | Agente activa Protocolo de moneda (confirma MXN si no está claro) → reconoce que NO cubre Opción B ($460k MXN) ni end-to-end Opción A. **Proactivamente** ofrece financiamiento externo: "Te apoyamos a buscar financiamiento con un banco, una arrendadora o una financiera…" | ✅ si menciona financiamiento sin que el lead lo pida + ✅ si usa "te apoyamos" o equivalente (NO "puedes buscar") |
| K2 | Pregunta directa por crédito | "¿Dan crédito? ¿O algún plan de pago?" | Agente: "Nosotros no damos financiamiento directo, pero te apoyamos a buscar financiamiento externo: las máquinas se entregan con factura y esa factura sirve para banco, arrendadora o financiera." | ✅ si usa frase "te apoyamos" + ✅ si menciona las 3 categorías sin recomendar institución específica |
| K3 | Pregunta institución específica | "¿Qué banco recomiendan?" o "¿BBVA da crédito para esto?" | Agente: NO recomienda banco/arrendadora/financiera específica. Responde "El director te orienta en la llamada con cuál de las tres vías te conviene arrancar según tu perfil." | ✅ si NO menciona nombre de banco/financiera concreto + ✅ si redirige al director |

**Resultado §K:** ⬜ / ⬜ / ⬜

---

## §D — Checklist promoción LIVE (actualizado para v1.8)

Antes de promover el prompt v1.8 + activar workflows main v3 + sub-workflow v3 en producción:

- [ ] Backup `agente-tofo-b2b-system-prompt-v1.7.md` existe en `04_agents/` (verificado en commit)
- [ ] Prompt v1.8 sincronizado al Google Doc vivo que levanta el AI Agent
- [ ] Sub-workflow v3 importado a n8n (mismo workflowId `vpLmZ299yXJrOSBv`)
- [ ] Main v3 importado y activo
- [ ] §A 8 tests pin data del sub-workflow: 8/8 ✅
- [ ] §B 16 tests E2E: 16/16 ✅
- [ ] §C 12 regression Oscar Amaya: 12/12 ✅
- [ ] §G 18 regression incidente 2026-06-08: 18/18 ✅
- [ ] **§H 5 ghost-booking: 5/5 ✅** (bloqueante — el incidente que dispara este bump)
- [ ] **§I 4 timezones MX: 4/4 ✅** (bloqueante — drift silencioso de hora)
- [ ] **§J 5 precio + productos viejos: 5/5 ✅** (bloqueante — fricción + invención de productos)
- [ ] **§K 3 financiamiento proactivo: 3/3 ✅** (bloqueante — tono pasivo actual)
- [ ] §Z 5 verificaciones manuales Zoom dashboard: 5/5 ✅
- [ ] 1 semana de monitoreo post-deploy: 0 incidentes de ghost-booking en logs `sys_tool_calls`

**Total bloqueante: 76/76 casos ✅** antes de marcar puntos 3/6/7 del análisis WhatsApp como resueltos en CLAUDE.md.

---

## §L — Notas operativas (renombrado desde §H de v5)

(Sin cambios — heredado íntegro de `testing-guide-v5.md` §H "Notas operativas". Cómo ejecutar A9, cómo ejecutar A10, triage en caso de fallo.)

---

## Referencias

- [Prompt B2B v1.8](../04_agents/agente-tofo-b2b-system-prompt.md)
- [Prompt B2B v1.7 backup](../04_agents/agente-tofo-b2b-system-prompt-v1.7.md)
- [Testing guide v5 (heredada)](testing-guide-v5.md)
- [Sub-workflow v3 — Zoom integrado](../03_workflows/chequear-disponibilidad-tofo-v3.json)
- [Main v3](../03_workflows/agente-tofo-web-b2b-rrss-v3.json)
- [Plan de bump](/Users/camilo/.claude/plans/1-qued-resuelto-2-enchanted-trinket.md)
- [Análisis WhatsApp Mauricio 17/6/26](../../../WhatsApp%20Chat%20-%20Tofo%20%7C%20la agencia/_chat.txt) (fuente original)
