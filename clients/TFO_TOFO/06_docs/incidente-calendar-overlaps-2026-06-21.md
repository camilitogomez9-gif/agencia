# Postmortem — Calendar overlaps + tool rogue (2026-06-21)

**Estado:** Cerrado pendiente verificación 3 días post-deploy.
**Severidad:** P1 (impacto directo en cliente, pérdida de confianza).
**Cliente:** TOFO Pizza — Mauricio García de la Vega.
**Detectado por:** Mauricio (mandó screenshot del calendar al grupo TOFO).

---

## TL;DR

Durante varios días, el calendar de Mauricio acumuló **múltiples citas overlapeadas en los slots 10/11/12 hora CDMX**. Causa raíz: el Agente de B2B tenía cableada como `ai_tool` una herramienta `Create an event in Google Calendar` (sin `toolDescription`) **paralela** a `check_disponibilidad`. El LLM podía crear eventos directos en el calendar sin pasar por el chequeo de overlap ni por la integración Zoom. Fix: desconectar la tool rogue + agregar **REGLA ABSOLUTA #4** en el prompt prohibiendo cualquier tool de Calendar/Zoom directa. Belt-and-suspenders.

Como bonus, el postmortem resuelve también el ticket "Zoom meetings no aparecen en dashboard de Mauricio" del 19/6 — era el mismo bug: la tool rogue solo creaba Calendar event, no Zoom meeting. La credencial Zoom probablemente estaba bien todo el tiempo.

---

## Cronología

| Fecha | Evento |
|-------|--------|
| **~2026-05** (build inicial) | Durante la construcción del agente conversacional B2B, alguien (¿la agencia? ¿Edgardo?) experimentó con un nodo `Create an event in Google Calendar` directo cableado al AI Agent. Funcionalmente equivalente al sub-workflow pero más simple. Quedó en el canvas. |
| **2026-06-04** | Bump del sub-workflow `Chequear disponibilidad` v1 → v2 (JS determinista + TZ + validaciones). Se establece como la **vía oficial** de creación de citas. **No se removió la tool rogue paralela** — quedó cableada con la creencia tácita de que "el LLM va a elegir la buena". |
| **2026-06-08** | Incidente Mauricio (Oscar/Ricardo/Isauro): ghost-booking + info inventada. Diagnóstico apuntó al prompt débil (no decía explícitamente "prohibido confirmar sin tool"). Bump B2B v1.5 → v1.6 con prohibición absoluta en §Cómo agendar. **Auditoría del inventario de tools del agente no se hizo** — todos asumimos que el problema era de prompting, no de infra. |
| **2026-06-15** | Bump sub-workflow v2 → v3 con Zoom auto-agendamiento. Las citas creadas vía `check_disponibilidad` ahora crean Calendar + Zoom atómicamente. La tool rogue sigue sin tocarse. |
| **2026-06-19** | Mauricio reporta "los meetings de Zoom no aparecen en mi dashboard, tengo que recrearlos a mano". Se asume causa = credencial Zoom equivocada. Se redacta plan de migración OAuth (`zoom-credencial-fix-2026-06-19.md`). Plan queda bloqueado esperando credenciales de Mauricio. **La hipótesis correcta — tool rogue creando solo Calendar, no Zoom — no se planteó porque nadie revisó el inventario de tools del agente.** |
| **2026-06-21** | Bump §0 v1.14 parte 2 (3 reglas absolutas) — incluye "nunca confirmar sin tool" como regla #1 dura. Aún así no atrapa el bug porque la regla #1 se cumple técnicamente: el LLM SÍ invoca una tool (la rogue), y SÍ ve un status OK, y SÍ confirma. La regla nunca menciona que solo `check_disponibilidad` es válida. |
| **2026-06-21 PM** | Mauricio manda screenshot del calendar con overlaps masivos. |
| **2026-06-21 PM** | Auditoría exhaustiva de wiring del workflow vivo (3 agentes Explore en paralelo). Smoking gun encontrado: `Create an event in Google Calendar` cableado al Agente de B2B sin `toolDescription`. Plan de fix aprobado en plan mode. |
| **2026-06-21 PM** | Bump prompt B2B v1.14 → v1.15 con **REGLA ABSOLUTA #4** (la única tool autorizada para agenda es `check_disponibilidad`). Guía manual escrita para la cirugía n8n. Testing-guide v8 con §P anti-tool-rogue (6 casos). Postmortem (este doc). |
| **PENDIENTE** | la agencia (o Mauricio) ejecuta la guía manual: desconectar 3 nodos rogue del Agente de B2B + cleanup retroactivo del calendar. |

---

## Análisis 5-why

**P:** ¿Por qué hubo overlaps en el calendar de Mauricio?
**R:** Porque el agente creó múltiples citas en el mismo slot sin chequear disponibilidad.

**P:** ¿Por qué el agente no chequeaba disponibilidad?
**R:** Porque invocó una tool alternativa (`Create an event in Google Calendar`) en lugar de `check_disponibilidad`.

**P:** ¿Por qué tenía esa tool alternativa disponible?
**R:** Porque quedó cableada al AI Agent desde la fase de build inicial cuando se exploraron alternativas de implementación. Nadie la removió cuando se decidió consolidar en `check_disponibilidad`.

**P:** ¿Por qué nadie la removió?
**R:** Porque no había un proceso de auditoría del inventario de tools después de cada bump del sub-workflow. Los bumps se enfocaron en el sub-workflow y el prompt, asumiendo que el wiring del agente principal estaba estable.

**P:** ¿Por qué no había proceso de auditoría?
**R:** Porque el patrón "auditar inventario `ai_tool` post-bump" no estaba en el runbook ni en el SOP. Era conocimiento implícito que dependía de que alguien se acordara de mirarlo.

→ **Causa raíz organizacional:** el patrón "1 cambio en el sub-workflow → auditar el inventario `ai_tool` del agente principal" no estaba codificado. **Acción correctiva:** crear estándar reusable `_core/standards/n8n-ai-agent-tool-inventory-audit.md` que se aplique a cualquier agente conversacional de la agencia.

---

## ¿Por qué los fixes previos no atraparon esto?

**Fix v1.6 (8/6):** agregó prohibición "NUNCA confirmar cita sin `check_disponibilidad` libre=true". **Falló porque:** el LLM cumplía técnicamente — invocaba la tool rogue, veía status OK (devolvía el evento creado), y confirmaba. La regla mencionaba `check_disponibilidad` como la canónica, pero no prohibía explícitamente alternativas.

**Fix v1.8 (17/6):** agregó "checkpoint mental" anti-ghost-booking. **Falló por la misma razón:** el checkpoint preguntaba "¿invoqué `check_disponibilidad`?" pero si el LLM invocaba la rogue (que también es una tool de calendar), podía responderse a sí mismo "sí, invoqué una tool de calendar" y proceder. El checkpoint no especifica "exactamente `check_disponibilidad`".

**Fix v1.14 §0 (21/6 AM):** elevó las 3 reglas a "ley dura" con framing absoluto. **Falló por la misma razón:** la regla #1 dice "nunca confirmes cita sin `check_disponibilidad` con `libre: true`" — pero el LLM con tool rogue activa puede argumentar que invocó alguna forma de "chequeo" (la rogue devuelve el evento creado como confirmación de éxito). La regla nunca dijo "exclusivamente `check_disponibilidad` y ninguna otra".

**Patrón común de los 3 fallos:** los fixes apuntaron al **prompt**, asumiendo que el inventario de tools del agente era confiable. El bug vivía en la **infra** (wiring), no en el prompt. Mientras la tool rogue estuviera disponible para el LLM, ningún prompt iba a ser 100% seguro.

**Lección aprendida:** cuando un bug "supuestamente arreglado" reaparece, el siguiente diagnóstico debe incluir auditoría del wiring del agente, no solo del prompting. **El prompt es la última capa de defensa, no la primera.**

---

## Lo que arreglamos hoy

### En n8n (vía guía manual)

Desconectamos la cara `ai_tool` de 3 nodos del Agente de B2B:
- `Create an event in Google Calendar` (CRÍTICO — el smoking gun)
- `Crear la base de datos` (googleSheetsTool disabled — zombie)
- `registrarrrrrrr` (googleSheetsTool disabled — zombie)

Inventario del Agente de B2B post-cirugía: **6 tools** (de 9 que tenía antes), todas con `toolDescription` o claramente operativas:
- `check_disponibilidad`, `elevar_conversacion`, `registrar`, `enviar_ficha_tecnica`, `enviar_video_funcionamiento`, `Doc informacion al cliente` (este último queda para validación follow-up).

### En el prompt (B2B v1.14 → v1.15)

Agregamos **REGLA ABSOLUTA #4** en §0:

> La ÚNICA tool autorizada para crear citas es `check_disponibilidad`. PROHIBIDO invocar cualquier otra tool que toque Google Calendar o Zoom directamente, aunque aparezca en tu lista de tools disponibles.

Belt-and-suspenders: si en el futuro alguien re-cablea por error otra tool de Calendar/Zoom (cleanup incompleto, build de nueva feature, etc.), el prompt es la segunda defensa.

### Bonus: resolución del ticket Zoom 19/6/26

Hipótesis nueva: el síntoma "Zoom no aparece en dashboard de Mauricio" del 19/6 fue causado por el mismo bug que los overlaps. La tool rogue (`Create an event in Google Calendar`) solo creaba Calendar event, **no Zoom meeting** (el sub-workflow v3 sí los crea ambos atómicamente). Coincide 100% con lo visto en dashboard. El plan de migración de credencial Zoom probablemente no era necesario.

Verificación en §P6 de testing-guide v8: si post-fix los meetings aparecen en el dashboard de Mauricio → credencial OK, ticket 19/6 se cierra por carambola. Si no aparecen → bug Zoom credencial existe en paralelo, plan original sigue vigente.

---

## Acciones correctivas

| # | Acción | Owner | Estado |
|---|--------|-------|--------|
| 1 | Desconectar 3 nodos rogue del Agente de B2B en n8n vivo | la agencia (o Mauricio) | ⏳ Pendiente (guía: `guia-fix-tools-rogue-calendar-2026-06-21.md`) |
| 2 | Bump prompt B2B v1.15 + subir al Google Doc vivo | la agencia (la agencia) | ✅ Local listo + ⏳ pendiente subir a Google Doc |
| 3 | Cleanup retroactivo del calendar de Mauricio | Mauricio | ⏳ Pendiente — Paso 8 de la guía |
| 4 | Smoke §P de testing-guide v8 (6 casos) | la agencia (la agencia) | ⏳ Pendiente post-deploy |
| 5 | Disambiguación del ticket Zoom 19/6/26 (§P6) | Mauricio + la agencia | ⏳ Pendiente post-smoke |
| 6 | Crear estándar reusable `n8n-ai-agent-tool-inventory-audit.md` | la agencia (la agencia) | ⏳ Pendiente |
| 7 | Aplicar el estándar a los 8 clientes activos de la agencia como auditoría preventiva | la agencia | ⏳ Backlog (próxima semana) |
| 8 | Eliminación completa de los 3 nodos desconectados (segunda pasada de cleanup) | la agencia | ⏳ Opcional, post-3 días sin incidentes |

---

## Auditoría preventiva — otros subagentes y otros clientes

**Otros subagentes del workflow TOFO** (RRSS, Servicio, Reposición, Derivación): auditados el mismo día. **Limpio**, no hay rogues críticas. Detalles en el apéndice de `guia-fix-tools-rogue-calendar-2026-06-21.md`. 6 tools sin `toolDescription` quedan como follow-up de baja prioridad (zombies que no causan el bug).

**Otros clientes de la agencia** con agentes conversacionales que crean recursos externos (citas, registros, mensajes): NPR (Napier), CLZ (Collazo), HBV (Heber Vera), STK (Stark), HPF (HappyFlops), NVJ (Narvaja), CRZ (Cereza Invest), SYS (Sistemas y Soluciones), IMP (Importadores). **Pendiente:** correr el grep contra cada uno como auditoría preventiva. Estimado: 1h total (script + reporte). Va al backlog.

---

## Regla derivada para el runbook

> **Después de cada bump significativo del sub-workflow de tools o consolidación de funcionalidad en una única tool, auditar el inventario `ai_tool` del agente principal y los subagentes. Cualquier tool que no esté explícitamente documentada como necesaria, queda desconectada (no solo disabled).**

Esta regla queda capturada en el estándar reusable `_core/standards/n8n-ai-agent-tool-inventory-audit.md`.

---

## Indicadores de éxito (3 días post-deploy)

- **0 nuevos overlaps** en el calendar de Mauricio durante 72 hs.
- **Meetings de Zoom aparecen en el dashboard** de Mauricio para cada nueva cita.
- **Logs de n8n:** ejecuciones del sub-workflow `vpLmZ299yXJrOSBv` = #citas confirmadas al lead. Ejecuciones de nodos rogue (Create an event, Zoom standalone) = 0.
- **Mauricio confirma** explícitamente en el grupo de TOFO que el problema está resuelto.

Si alguna de las 4 falla → reopen incident.

---

## Anexo — Snapshot del inventario `ai_tool` del Agente de B2B

### Antes del fix (2026-06-21 AM, smoking gun)

| # | Nodo | Type | Descripción | Estado |
|---|------|------|-------------|--------|
| 1 | `check_disponibilidad` | toolWorkflow → vpLmZ299yXJrOSBv | ✅ | wired |
| 2 | **`Create an event in Google Calendar`** | **googleCalendarTool** | ❌ VACÍA | wired (smoking gun) |
| 3 | `elevar_conversacion` | toolWorkflow | ✅ | wired |
| 4 | `registrar` | airtableTool | ✅ | wired |
| 5 | `enviar_ficha_tecnica` | toolHttpRequest | ✅ | wired |
| 6 | `enviar_video_funcionamiento` | toolHttpRequest | ✅ | wired |
| 7 | `Doc informacion al cliente` | googleDocsTool | ❌ sin desc | wired |
| 8 | `Crear la base de datos` | googleSheetsTool | ❌ sin desc | wired (disabled, zombie) |
| 9 | `registrarrrrrrr` | googleSheetsTool | ❌ sin desc | wired (disabled, zombie) |

### Después del fix (2026-06-21 PM, esperado)

| # | Nodo | Type | Descripción | Estado |
|---|------|------|-------------|--------|
| 1 | `check_disponibilidad` | toolWorkflow → vpLmZ299yXJrOSBv | ✅ | wired |
| 2 | `elevar_conversacion` | toolWorkflow | ✅ | wired |
| 3 | `registrar` | airtableTool | ✅ | wired |
| 4 | `enviar_ficha_tecnica` | toolHttpRequest | ✅ | wired |
| 5 | `enviar_video_funcionamiento` | toolHttpRequest | ✅ | wired |
| 6 | `Doc informacion al cliente` | googleDocsTool | ⚠️ sin desc | wired (follow-up: validar uso + agregar descripción) |

Diff: -3 nodos cableados (Create an event + 2 sheets). +0 nodos. Los 3 nodos siguen presentes en el canvas pero sin conexión `ai_tool` (rollback fácil si algo sale mal).
