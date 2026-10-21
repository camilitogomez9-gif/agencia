---
name: generar-architecture-doc
description: >
  Usar este skill cuando hay que generar el doc de arquitectura `architecture-v2.md`
  de un agente conversacional Etapa 2 (componentes, integraciones, decisiones
  arquitectónicas, capacidad, riesgos). Se activa con frases como "armar
  architecture doc de X", "documentar arquitectura X", "doc de arquitectura
  para handoff", "F0/F1 architecture cliente X". Stack target: Airtable +
  Supabase + ManyChat + n8n.
---

# Skill: Generar Architecture Doc Agente Etapa 2

## Descripción

Genera el doc `architecture-v2-{YYYY-MM}.md` que describe la arquitectura del agente productivo. Es el doc al que recurre la agencia cuando hay que entender "cómo está armado el sistema" sin abrir n8n. Validado en SYS.

**Estructura validada en SYS:**

1. Resumen ejecutivo (1 párrafo)
2. Diagrama ASCII de componentes
3. Tabla de componentes (componente | rol | stack | dueño)
4. Flujo end-to-end de un mensaje (numerado)
5. Tablas de integraciones (sistema externo | tipo | qué intercambia)
6. Decisiones arquitectónicas críticas (las 14-16 principales)
7. Capacidad y límites (free tier limits, picos esperados)
8. Riesgos conocidos (lo que sabemos que puede romperse + mitigación)
9. Roadmap evolutivo (qué cambia en v3, qué upsells están pre-cocinados)

---

## Cuándo invocarlo

- F0/F1 del Plan Maestro Etapa 2 (durante o post bootstrap)
- Antes de presentar arquitectura al cliente
- Cuando hay handoff a otro técnico (junto a runbook + UML)
- Cuando se hace un cambio arquitectónico mayor (v2 → v3)

## Cuándo NO invocarlo

- Cliente Etapa 1 sin tools (overkill)
- Solo se cambió una tool — actualizar el v2 existente, no regenerar

---

## Inputs requeridos

1. **Cliente ID + nombre**
2. **Stack confirmado** (canales, AI provider, memoria, RAG, CRM si aplica)
3. **Lista de tools** (8-10 típico)
4. **Decisiones arquitectónicas tomadas** (las críticas: Session Pooler, Ignore SSL, hardcoded constants, $fromAI pattern, etc.)
5. **Picos esperados** (mensajes/día estimados)

---

## Proceso

### Paso 1 — Generar el doc con secciones estándar

Path: `clients/{XXX}_{Nombre}/02_architecture/architecture-v2-{YYYY-MM}.md`

Base: `clients/SYS_SistemasYSoluciones/02_architecture/architecture-v2-2026-05.md` (validado).

### Paso 2 — Diagrama ASCII

Plantilla:

```
┌─────────────┐    ┌──────────────┐    ┌──────────┐
│  Canal IG   │───▶│   ManyChat   │───▶│   n8n    │
│  Canal WA   │    │ (router/cap) │    │ webhook  │
│  Canal FB   │    └──────────────┘    └────┬─────┘
└─────────────┘                              │
                                             ▼
                                    ┌────────────────┐
                                    │  AI Agent      │
                                    │  gpt-4o        │◀── Postgres Chat
                                    │  (LangChain)   │     Memory
                                    └────────┬───────┘    (Supabase)
                                             │
                       ┌────────────┬────────┼────────┬─────────────┐
                       ▼            ▼        ▼        ▼             ▼
                  tool 1      tool 2    tool 3   ...        tool N
                  (Airtable)  (Airtable) (Gmail) ...        (Postgres)
                       │            │        │
                       └────────────┴────────┴───▶  Log a sys_tool_calls
```

Adaptar a stack del cliente.

### Paso 3 — Tabla de componentes

```markdown
| Componente | Rol | Stack | Dueño |
|---|---|---|---|
| Canales | Entrada/salida usuario final | ManyChat IG/WA/FB | Cliente |
| Orquestación | Recibir webhook + routing + responder | n8n self-hosted DigitalOcean | la agencia |
| AI Agent | Razonamiento + tool calling | OpenAI gpt-4o (LangChain) | la agencia |
| Memoria | Histórico cross-turn por sesión | Supabase Postgres (n8n_chat_histories) | la agencia |
| RAG/Catálogo | Productos, FAQs, KB del negocio | Airtable | Cliente edita / la agencia schema |
| Notificación | Alertar al equipo del cliente | Gmail + Telegram | Cliente recibe |
| Observabilidad | Logging tool calls + métricas | Supabase Postgres (sys_tool_calls) | la agencia |
```

### Paso 4 — Decisiones arquitectónicas (pre-pobladas)

Embebir las 14-16 decisiones validadas SYS:

1. Memoria persistente cross-turn en Postgres (no en n8n Static Data)
2. Supabase managed vs self-hosted (managed por velocidad + costo)
3. Session Pooler vs Direct Connection (IPv6)
4. Ignore SSL Issues en credential Postgres (Node.js sin cert root)
5. Airtable como single source para RAG (no Pinecone — overkill para catálogo <1000 records)
6. Hardcoded constants (Opción C) por limitación n8n plan
7. AI Agent con tool calling real (vs router determinístico)
8. `$fromAI` pattern con backticks + type=string + comment auto-gen
9. Tool output contract `{status, data, message_to_agent, trace_id}`
10. queryReplacement como array literal (no CSV concatenado)
11. Logging a `sys_tool_calls` con `continueOnFail=true` (nunca matar la tool por log fail)
12. ManyChat Respond-First pattern (cuando aplica): respuesta directa al usuario en <10s, agente trabaja en async
13. Patrón retry para Airtable rate-limit (5 req/sec base — backoff exponencial)
14. CRM tabla "ghosting" para upsell pendiente (estructura existe pero no se usa)
15. Multi-canal vía ManyChat (no Twilio directo — costo + velocidad)
16. n8n self-hosted en DigitalOcean (no n8n cloud — costo a escala)

Adaptar al stack del cliente. No copiar literal si no aplican.

### Paso 5 — Capacidad y límites

Tabla con free tier limits:

```markdown
| Recurso | Free tier | Estimado uso típico | Cuándo upgrade |
|---|---|---|---|
| Supabase DB | 500 MB | ~50 MB/mes en 1000 conversaciones | Cliente >5k conversaciones/mes |
| Supabase egress | 2 GB/mes | <500 MB/mes | Improbable trigger |
| Airtable records | 1000/base (free) | 100-500 records típicos | Catálogo >800 records |
| OpenAI tokens | $ por uso | ~$15-30/mes en gpt-4o | N/A (consumo directo) |
| n8n executions | self-hosted ilimitado | N/A | N/A |
| ManyChat MAU | 1000 (free) | Variable según cliente | Trigger del propio cliente |
```

### Paso 6 — Riesgos conocidos

Tabla con riesgo + mitigación:

```markdown
| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Re-import n8n destruye config $fromAI | Alta | Alto | `f5-tools-fromai-config.md` + skill S11 |
| OpenAI rate limit / outage | Media | Alto | Fallback a "tu consulta fue recibida, te respondemos" + alert |
| Airtable rate limit en pico | Baja | Medio | Retry backoff exponencial en tools |
| Supabase free tier exceeded | Baja | Bajo | Alert al 80% (skill cliente-sync notifica) |
| Excel del cliente rompe asunciones | Alta | Medio | Skill S8 detecta y re-alinea |
```

### Paso 7 — Roadmap evolutivo

```markdown
## v2.1 (próximo — semanas)
- Activar tool X que quedó stub
- Onboarding completo del editor Airtable

## v3 (mes 2-3, si upsell se activa)
- CRM Leads activado (Airtable Leads + vistas + seguimiento)
- Reporte semanal automatizado al cliente

## v4 (mes 4+, si volumen lo justifica)
- Migración a OpenAI gpt-4o-mini (cuando feature parity + costo OK)
- Eventual: embeddings + retrieval semántico para FAQs largos
```

### Paso 8 — Reportar al usuario

Output:
- Path del doc
- Lista de secciones generadas
- Sugerir: combinar con runbook (S10) + UML (`/generar-uml`) para handoff completo

---

## Composición

**Invoca:** ninguno.
**Es invocado por:** F0/F1 del Plan Maestro, o standalone pre-handoff.
**Complementa:** `generar-runbook-agente` (S10), `/generar-uml`.

---

## Notas operativas

- **Tiempo:** 20-40 min del skill.
- **El doc es para la agencia + cliente técnico.** No es para el end-user.
- **Mantenerlo versionado en file name** (`architecture-v2-2026-05.md`, `architecture-v3-2026-08.md`).
- **Decisiones arquitectónicas son inmutables** — si se cambian, generar v.next, no editar.
