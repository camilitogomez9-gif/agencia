---
name: bootstrap-agente-etapa-2
description: >
  Usar este skill cuando un cliente pasa de Etapa 1 (testing conversacional)
  a Etapa 2 (producción con tools reales). Se activa con frases como
  "arrancar Etapa 2 para X", "pasar X a producción", "iniciar Etapa 2 cliente",
  "bootstrap del cliente X", o cuando ya hay un system prompt validado en
  testing Telegram y se quiere armar todo el andamiaje productivo. Crea el
  Plan Maestro, planes tácticos por fase, runbook stub, credentials templates
  gitignored, architecture doc stub. Stack target: Airtable + Supabase + ManyChat + n8n.
---

# Skill: Bootstrap Agente Etapa 2

## Descripción

Genera todo el andamiaje inicial para mover un cliente de Etapa 1 (testing conversacional sobre Telegram, con placeholders de tools y memoria volátil) a Etapa 2 (producción con ManyChat multi-canal + tools reales sobre Airtable + memoria persistente en Supabase + observabilidad).

Stack pre-cocinado:
- **Canales**: ManyChat (IG/WA/FB)
- **Orquestación**: n8n self-hosted
- **LLM**: OpenAI gpt-4o (con gpt-4.1-mini para sub-tasks)
- **Memoria**: Supabase Postgres (Session Pooler)
- **RAG / catálogo**: Airtable (single source)
- **Notificaciones**: Gmail + Telegram

Si el cliente requiere stack diferente, este skill NO aplica — usar bootstrap específico.

---

## Cuándo invocarlo

- Cliente con prompt v1.x validado en Telegram
- Cliente aprobó la propuesta económica de Etapa 2
- Decisión "vamos a producción" tomada

## Cuándo NO invocarlo

- Cliente aún en Etapa 1 (testing prompt)
- Cliente con stack no estándar (ej. Chatwoot, Kommo, Manychat ya no)
- Cliente cuya solución no es "agente conversacional con tools" (ej. workflow puramente automatización)

---

## Proceso

### Paso 1 — Recopilar inputs

Si no fueron provistos, preguntar:

1. **ID cliente** (3 letras existentes — verificar en `clients/`)
2. **Canales target**: alguna combinación de IG, WA, FB (otros: ver bootstrap específico)
3. **Niche del agente** (dental, real estate, gráfica, agency, etc.)
4. **Path al system prompt v1.x actual** (de la Etapa 1)
5. **Decisiones cliente pre-flight resueltas o pendientes**:
   - Nombre del agente (o sin nombre)
   - URL tienda online si aplica
   - Mail destino de notificaciones leads
   - Especialización de representantes (Opción A: sin / Opción B: con)
   - CRM ahora o upsell futuro (Opción A: sin Airtable Leads / Opción B: con)
   - Precios visibles al agente (sí / no / oculto en vista filtrada)

Si alguna de las 6 decisiones está pendiente, registrarla como bloqueo en CLIENT_INFO.

### Paso 2 — Validar precondiciones

Verificar que existan:
- `clients/{XXX}_{Nombre}/CLIENT_INFO.md` (cliente registrado vía `cliente-nuevo`)
- `clients/{XXX}_{Nombre}/04_agents/{nombre}-system-prompt.md` con versión v1.x
- Confirmar testing Etapa 1 completado (preguntar al usuario si no está claro en log)

Si falta alguna, **detener** y derivar a `/cliente-nuevo` o `/iterar-prompt` según corresponda.

### Paso 3 — Generar el Plan Maestro

Crear `planes/{XXX}-etapa-2-plan-maestro-{YYYY-MM-DD}.md` siguiendo el patrón de SYS (`/Users/camilo/.claude/plans/contexto-general-del-dapper-sun.md`):

Estructura obligatoria de 17 secciones:
1. Context
2. Resumen Ejecutivo (componentes principales + costos esperados)
3. Arquitectura General (diagrama ASCII)
4. Flujo Conversacional End-to-End
5. Integración ManyChat
6. Arquitectura de Memoria
7. Diseño Supabase/Postgres
8. Arquitectura RAG (search Airtable + tool LLM)
9. Diseño Airtable
10. Diseño de Herramientas (8-10 tools)
11. Estrategia de Tool Calling
12. Ajustes del System Prompt (v1.x → v2.0)
13. Estrategia de Retrieval
14. Flujo Técnico Completo
15. Riesgos y Mitigaciones
16. Buenas Prácticas
17. Roadmap de Implementación (8 fases F0-F8)

**Decisiones técnicas pre-cocinadas** que deben aparecer en el Plan Maestro:
- Supabase Session Pooler (NO Direct, NO Transaction Pooler)
- SSL=require + Ignore SSL Issues=true en credencial Postgres
- `n8n_chat_histories` + `sys_tool_calls` + `sys_session_state` como tablas mínimas
- Memoria con `contextWindowLength: 20` + truncación 3000 chars
- Patrón main workflow: Webhook → Normalize → IF skip → Context → AI Agent + Memory + Tools → Split → Respond
- Patrón sub-workflow tool: Trigger → Validate → External Search → Format → Log → Return
- Contrato output tools: `{status: RESOLVED|AMBIGUOUS|NOT_FOUND|ERROR, data, message_to_agent, trace_id}`
- `$fromAI()` con backticks + type=string + comentario `/*n8n-auto-generated-fromAI-override*/`
- `queryReplacement` Postgres como array literal `={{ [A, B, C] }}`
- Hardcoded constants (Opción C) si plan n8n no tiene Variables UI
- Patrón ManyChat Respond-First (respond 200 inmediato, push respuesta via setCustomFields + sendFlow)
- **ManyChat Standard interno 2026** — naming custom fields (`ai_*`/`lead_*`/`session_*`/`meta_*`), auth via n8n Credential (no Bearer hardcoded), 3 flows canónicos (`[LA AGENCIA] Default Reply`, `[LA AGENCIA] Responder Multi-Parte`, `[LA AGENCIA] Fallback Humano`), payload dinámico vía Code node. Ver `_core/standards/manychat-integration-pattern.md`

### Paso 4 — Generar planes tácticos por fase

Crear los 8 plantillas de plan táctico (uno por fase) en `planes/{XXX}-f{N}-{fase}-{YYYY-MM-DD}.md`:

| Fase | Nombre | Estado inicial |
|---|---|---|
| F0 | Pre-flight | Pendiente bloqueos cliente |
| F1 | Migración Airtable | Bloqueado por F0 |
| F2 | Setup Supabase | Bloqueado por F0 |
| F3 | Workflow principal | Bloqueado por F2 |
| F4 | Tools sub-workflows | Bloqueado por F1 + F3 |
| F5 | Integración tools | Bloqueado por F4 |
| F6 | Integración ManyChat | Bloqueado por F5 |
| F7 | Testing E2E | Bloqueado por F6 |
| F8 | Producción + observability | Bloqueado por F7 |

Cada plan táctico usa la plantilla de Plan del SOP-1 (`_core/standards/loop-plan-implement-smoke-iterate.md`).

### Paso 5 — Generar estructura de docs

En `clients/{XXX}_{Nombre}/06_docs/` crear (vacíos o con stub):

| Archivo | Contenido inicial |
|---|---|
| `runbook.md` | Stub con secciones obligatorias (SLAs P1-P3, diagnóstico rápido, incidentes comunes, queries SQL útiles, escalamiento, lecciones aprendidas, decisiones arquitectónicas críticas) |
| `airtable-credentials.md` | Template gitignored con placeholders `<<<COMPLETAR_*>>>` |
| `supabase-credentials.md` | Template gitignored con decisiones técnicas pre-cocinadas |
| `manychat-credentials.md` | Template gitignored |
| `tools-spec-v1.md` | Stub con sección por las 9 tools genéricas, listas para completar |
| `f1-migracion-airtable-log.md` | Estructura plantilla del SOP-1 |

En `clients/{XXX}_{Nombre}/02_architecture/` crear:

| Archivo | Contenido inicial |
|---|---|
| `architecture-v2-{YYYY-MM}.md` | Stub con secciones: diagrama de componentes, componentes, integraciones, decisiones arquitectónicas (16+), capacidad y costos, riesgos identificados, migración desde Etapa 1 |

En `clients/{XXX}_{Nombre}/05_crm/` crear:

| Archivo | Contenido inicial |
|---|---|
| `airtable-{niche}-schema.md` | Schema doc con las 11 tablas estándar (Tecnologías/Categorías, Sustratos/Materiales, Líneas, Aplicaciones, Cabezales/Componentes, Insumos/Consumibles, Productos/Equipos, FAQs, Representantes, Leads, Config Mensual). Niche-aware en nomenclatura. |

### Paso 6 — Actualizar `.gitignore` raíz

Asegurar que existan los patterns:
```
**/airtable-credentials.md
**/supabase-credentials.md
**/manychat-credentials.md
**/*-credentials.md
**/credentials-*.md
```

Si no existen, agregar.

### Paso 7 — Actualizar status en 3 lugares

1. `CLIENT_INFO.md` → cambiar status a `BUILD Etapa 2 — F0 pre-flight en ejecución`
2. `CLAUDE.md` raíz → en sección del cliente, agregar `**Estado:** Etapa 1 (testing) COMPLETADO ✅. Etapa 2 (Producción ManyChat + tools reales + memoria) — Plan Maestro generado {YYYY-MM-DD}, en build.`
3. `contexto/datos-actuales.md` → fila del cliente: status `BUILD Etapa 2 (F0)`, próximo paso `F0 desbloquear: nombre agente, URL tienda, mail destino, mapeo reps`

### Paso 8 — Reportar al usuario

Devolver al usuario:
- Lista de archivos creados
- Lista de bloqueos pre-flight pendientes con preguntas concretas al cliente
- Próximos pasos sugeridos:
  - Si hay bloqueos: "Conseguir respuesta a las 6 preguntas pre-flight"
  - Si no: "Arrancar F1 con `setup-supabase-memoria-agente` + `migrar-excel-a-airtable-rag` en paralelo"

---

## Composición con otros skills

Este skill **invoca** (cuando aplica):
- `setup-supabase-memoria-agente` (S7) — opcionalmente arrancar F2 en paralelo si las creds del cliente ya están listas
- `cliente-sync` — al cierre del bootstrap para commitear cambios

Este skill **NO invoca** directamente (queda como próximos pasos del usuario):
- `migrar-excel-a-airtable-rag` (S8) — espera input del cliente
- `generar-workflow-agente-n8n` (S2) — espera F1 + F2
- `generar-subworkflows-tools-n8n` (S3) — espera F4

---

## Validación / smoke test

Al finalizar, verificar:

- [ ] Plan maestro existe y tiene las 17 secciones
- [ ] 8 planes tácticos generados (F0-F8)
- [ ] Runbook stub creado
- [ ] 3 credentials templates creados (Airtable, Supabase, ManyChat) — gitignored
- [ ] Architecture doc stub creado
- [ ] `.gitignore` cubre los patterns de credentials
- [ ] Status actualizado en CLIENT_INFO + CLAUDE.md + datos-actuales
- [ ] Bloqueos pre-flight listados explícitamente

Si algún punto falla, marcar como incompleto y reportar.

---

## Notas operativas

- **Tiempo estimado del skill:** 30-45 min de trabajo del asistente (vs 8-10h sin skill).
- **Composición permitida** con S7 si las credenciales Supabase ya están disponibles desde otro cliente o desde la agencia default.
- **Modelos LLM hardcoded por default:** gpt-4o agente principal + gpt-4.1-mini sub-tasks. Si el cliente pide otro modelo, ajustar en Paso 3 (plan maestro).
- **Si el cliente NO tiene ManyChat contratado**, generar igual los planes pero marcar F6 como "bloqueado contratación" y proponer arrancar F7 (testing con curl) antes de F6.
