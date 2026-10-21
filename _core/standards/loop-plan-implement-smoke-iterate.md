# SOP-1 — Loop "Plan → Implement → Smoke → Iterate"

> **Tipo:** Standard Operating Procedure (método de trabajo)
> **Aplica a:** todos los proyectos de la agencia, especialmente agentes conversacionales Etapa 2 (Airtable + Supabase + ManyChat + n8n)
> **Origen:** lecciones acumuladas de cliente SYS (transición Etapa 1 → Etapa 2)
> **Fecha:** 2026-05-31

---

## Por qué este SOP existe

Los proyectos de agentes IA en producción tienen una característica estructural: **cada fase tiene componentes que dependen de servicios externos (Airtable, Supabase, ManyChat, OpenAI) cuya configuración real no siempre coincide con lo planificado en el papel**. Esto genera:

- Bugs descubiertos solo al ejecutar
- Decisiones técnicas que solo emergen al chocar con la realidad (ej. IPv6 de Supabase Direct Connection, sintaxis exacta de `$fromAI()`, `queryReplacement` con comas internas)
- Re-trabajo en cascada cuando un assumption inicial falla

El antídoto es **NO trabajar en un solo "big bang"**. Cada bloque de trabajo se desglosa en un loop corto:

1. **Plan** (artefactos esperados, no más de 1-2 horas de trabajo planificado)
2. **Implement** (ejecutar el plan)
3. **Smoke** (probar el resultado contra realidad, no contra papel)
4. **Iterate** (capturar divergencias en docs, ajustar plan, volver a 2)

Cada loop completo dura ~2-4 horas, no días. Si después de 2 loops un bloque sigue roto, **stop, escalar, redefinir**.

---

## Las 4 fases del loop

### Fase 1 — Plan

**Goal:** declarar entregables concretos verificables, no objetivos vagos.

**Artefactos del Plan:**
- Lista de archivos a crear/modificar (con paths exactos)
- Decisiones técnicas pre-cocinadas (qué se eligió y por qué)
- Smoke test verificable (cómo probaremos que funcionó)
- Criterio de "done" claro (no "implementar X" sino "X responde con Y al input Z")

**NO incluir en el Plan:**
- Specs internos del implementador ("voy a usar tal algoritmo")
- Optimizaciones prematuras
- Cosas que dependen de info que no tenemos

**Tiempo:** 15-30 min máximo. Si excede, dividir en bloques más chicos.

### Fase 2 — Implement

**Goal:** ejecutar exactamente lo planificado, NO improvisar nuevas decisiones.

**Reglas:**
- Si aparece una decisión no contemplada en el Plan: **detener implementación, agregarla al Plan, justificarla**, después continuar.
- Cada archivo creado/modificado se documenta en el log (qué cambió, por qué).
- Si una dependencia externa falla (Airtable rate limit, Supabase IPv6, etc.): **detener, capturar el error textual exacto, decidir workaround en Plan, continuar**.

**Tiempo:** 60-120 min. Si excede, el Plan estaba mal dimensionado.

### Fase 3 — Smoke

**Goal:** probar contra realidad, no contra papel.

**Tipos de smoke test (por orden de utilidad):**
1. **Test end-to-end con curl** (al webhook real, no a OpenAI directo)
2. **Test del componente aislado** (sub-workflow, query SQL, etc.)
3. **Inspect via MCP** (n8n, Supabase, Airtable) — comparar config real vs esperada
4. **Test manual UI** (último recurso, no escala)

**Cada smoke debe verificar:**
- Comportamiento positivo (input X → output Y correcto)
- Comportamiento negativo (input inválido → error controlado, no silencioso)
- Persistencia (si aplica: query a DB para confirmar write)
- Logs (si aplica: query a tabla de tool_calls / events)

**Tiempo:** 15-45 min.

### Fase 4 — Iterate

**Goal:** capturar divergencias antes de pasar al siguiente bloque.

**Capturas obligatorias:**

| Tipo de divergencia | Dónde se documenta |
|---|---|
| Decisión técnica nueva | `06_docs/runbook.md` sección "Decisiones arquitectónicas críticas" |
| Bug resuelto | `06_docs/runbook.md` sección "Incidentes resueltos" |
| Cambio de scope del Plan | `06_docs/f{N}-{fase}-log.md` sección "Desviaciones del Plan" |
| Nueva regla de tono / behavior del agente | `04_agents/{nombre}-system-prompt.md` → versionar (v.next) |
| Decisión del cliente | `CLIENT_INFO.md` sección "Decisiones cliente" |
| Cambio que afecta el plan maestro | Updatear plan maestro + razón del cambio |

**Updates de status obligatorios (3 lugares al cerrar bloque):**
1. `CLIENT_INFO.md` — status de la fase
2. `CLAUDE.md` (raíz workspace) — sección del cliente
3. `contexto/datos-actuales.md` — fila del cliente

**Decisión final del loop:**
- ✅ Smoke pasó → siguiente bloque
- ⚠️ Smoke parcial → ajustar Plan, re-implementar componentes específicos, volver a smoke
- 🔴 Smoke falló y no sabemos por qué → **escalar** (más diagnóstico, MCP, ejecuciones n8n, logs Postgres)

**Tiempo:** 15-30 min.

---

## Patrones recurrentes de divergencia (lecciones SYS)

Estas son las "trampas" más frecuentes. Si las anticipás en el Plan, ahorrás 1-3 loops por proyecto.

### Trampa 1 — Servicios externos con assumptions ocultas

| Servicio | Assumption errónea típica | Realidad |
|---|---|---|
| Supabase | "Direct connection funciona" | Direct usa IPv6, droplets sin IPv6 fallan → **usar Session Pooler 5432, NO Transaction Pooler 6543** |
| Supabase + n8n | "SSL=require valida cert OK" | Node.js no tiene cert root → **Ignore SSL Issues = true** |
| n8n LangChain `$fromAI` | "type=array funciona" | Zod rechaza arrays mal formados → **TODO type=string, parsear adentro** |
| n8n Postgres node | "queryReplacement con comas funciona" | Si los valores tienen comas internas (JSON.stringify), parsing CSV se rompe → **usar array literal `={{ [A,B,C] }}`** |
| n8n re-import | "El JSON se importa íntegro" | Workflow IDs cached se rompen al re-importar, hay que re-seleccionar → **NO regenerar JSON tras config manual; mantener UI como source of truth** |
| ManyChat External Request | "El webhook puede tardar lo que quiera" | Timeout ~10s → **patrón Respond-First (responder 200 inmediato, pushear respuesta real con setCustomFields + sendFlow)** |

### Trampa 2 — Asunciones de catálogo cliente

El catálogo real (Excel/Sheets/CSV) que entrega el cliente **casi siempre rompe asunciones**. Patrón observado SYS:

- Asunción: marcas globales (Mimaki, Roland) → Realidad: marcas chinas (HUENU, DLICAN)
- Asunción: 8 tecnologías → Realidad: 10 (+Solvente, +Corte)
- Asunción: 30-50 productos → Realidad: 92
- Asunción: sin precios en catálogo → Realidad: todos con precio USD

**Anticipar en el Plan:** marcar como "input cliente pendiente" todo lo que dependa del catálogo real, y planificar re-alineación obligatoria post-entrega.

### Trampa 3 — Decisiones cliente bloqueantes que se descubren tarde

Antes de F1, conseguir respuesta a:
- ¿Nombre del agente? ¿O sin nombre?
- ¿URL tienda online?
- ¿Mail destino notificaciones leads?
- ¿Especialización por rep/zona/línea o un solo destino?
- ¿CRM ahora o upsell futuro?
- ¿Precios visibles al agente o no?

Cualquiera de estos sin respuesta = bloqueo en cadena.

### Trampa 4 — Fragmentación de status

El status del cliente vive en 3 lugares (`CLIENT_INFO.md`, `CLAUDE.md`, `contexto/datos-actuales.md`). Olvidarse uno = pérdida de contexto futura.

**Mitigación:** al cerrar cada loop, actualizar los 3. No esperar a "final de fase".

---

## Plantilla de Plan (copiar al inicio de cada bloque)

```markdown
## Plan — {Bloque X.Y: nombre}

### Goal
{1 oración del entregable concreto}

### Artefactos a producir
- [ ] {path/archivo1.json} — {qué hace}
- [ ] {path/archivo2.md} — {qué hace}
- [ ] Modificación de {archivo3} — {qué cambia}

### Decisiones técnicas pre-cocinadas
1. {Decisión} — porque {razón}
2. {Decisión} — porque {razón}

### Dependencias externas
- {Servicio X} debe estar {estado}
- {Decisión Y del cliente} debe estar {estado}

### Smoke test
**Cómo verificamos que funcionó:**
1. {Comando / acción}
2. **Esperado:** {output / comportamiento concreto}

### Definition of Done
- [ ] {Criterio 1 medible}
- [ ] {Criterio 2 medible}
- [ ] Updates de status (3 lugares)
- [ ] Log de divergencias actualizado
```

---

## Plantilla de log por fase (copiar a `06_docs/f{N}-{fase}-log.md`)

```markdown
# F{N} — {Nombre fase} — Log

**Estado:** {en ejecución | completada | bloqueada}
**Fecha inicio:** {YYYY-MM-DD}
**Fecha fin:** {YYYY-MM-DD}
**Ejecutor:** {la agencia | la agencia+Claude}

## Resumen
{1-2 párrafos de qué se hizo}

## Decisiones tomadas durante ejecución
1. {Decisión} — fecha — razón
2. {Decisión} — fecha — razón

## Divergencias del Plan
1. {Divergencia} — impacto — acción tomada
2. {Divergencia} — impacto — acción tomada

## Smoke tests ejecutados
| # | Test | Resultado | Notas |
|---|---|---|---|
| 1 | {qué probamos} | ✅/⚠️/🔴 | {observación} |

## Lecciones aprendidas (para próximos proyectos)
- {Lección 1}
- {Lección 2}

## Status updates aplicados
- [x] CLIENT_INFO.md
- [x] CLAUDE.md (raíz)
- [x] contexto/datos-actuales.md
```

---

## Cómo usar este SOP en la práctica

### Antes de arrancar cualquier bloque
1. Abrir este doc
2. Copiar la plantilla de Plan
3. Llenarla en máximo 30 min
4. Empezar Implement

### Durante Implement
- Si surge decisión no planificada → pausar, actualizar Plan, continuar
- Si surge error técnico inesperado → buscar en sección "Trampas recurrentes"

### Después de Smoke
- Si pasó: actualizar log + 3 docs de status + cerrar bloque
- Si no pasó: identificar componente puntual, ajustar Plan parcialmente, re-implementar componente, re-smoke

### Cierre de fase completa
- Asegurar log F{N} completo
- Lecciones aprendidas → si son patrones nuevos, agregar a este SOP

---

## Anti-patrones (qué NO hacer)

| Anti-patrón | Por qué falla |
|---|---|
| Planificar 8 horas de trabajo en un solo bloque | Demasiada superficie de error, smoke tardío, debugging complejo |
| Saltarse el smoke porque "lo planifiqué bien" | El papel siempre coincide con sí mismo; la realidad no |
| Implementar sin actualizar log | Pérdida de contexto futura, especialmente al volver semanas después |
| Cambiar el Plan en silencio durante Implement | El log queda inconsistente, no podés explicar por qué tal componente quedó como quedó |
| Re-importar JSON tras config manual en UI | Pérdida garantizada de config (especialmente `$fromAI`, workflow IDs de toolWorkflow nodes) |
| Asumir que servicios externos "funcionan como en la doc" | Nunca. Siempre smoke. |

---

## Skills relacionados que implementan este SOP

Cada skill de la biblioteca interna sigue esta estructura (Plan → Implement → Smoke → Iterate). Lista no exhaustiva:

- `bootstrap-agente-etapa-2` — crea el primer Plan maestro de un proyecto
- `generar-workflow-agente-n8n` — Plan + Implement del main workflow
- `generar-subworkflows-tools-n8n` — Plan + Implement de las 9 tools
- `smoke-test-agente-webhook` — Smoke automatizado del agente productivo
- `inspector-bugs-toolworkflow-n8n` — diagnóstico para Iterate cuando Smoke falla

---

**Este SOP es el cimiento de todo lo demás. Si un skill no respeta el loop Plan→Implement→Smoke→Iterate, hay algo mal.**
