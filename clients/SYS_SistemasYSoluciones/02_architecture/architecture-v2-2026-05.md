# Arquitectura — SYS Etapa 2 (v2)

> **Cliente:** SYS — Sistemas y Soluciones
> **Versión arquitectura:** v2 (Etapa 2 — Producción)
> **Fecha:** 2026-05-28
> **Estado:** diseño aprobado, pendiente implementación
> **Reemplaza:** Etapa 1 (Telegram + Google Sheets placeholder)

---

## Diagrama de componentes

```
                    ┌───────────────────────────────────────────────────┐
                    │              CANALES (clientes finales)            │
                    │  WhatsApp Business  │  Instagram DM  │  Facebook  │
                    └───────────┬─────────────────┬──────────────┬──────┘
                                │                 │              │
                                ▼                 ▼              ▼
                       ┌───────────────────────────────────────────────┐
                       │                 MANYCHAT                       │
                       │  - Default Reply Flow → External Request      │
                       │  - Custom fields (parte1/2/3, agent_state)    │
                       │  - Flow "Responder Multi-Parte"                │
                       │  - Flow "Fallback Humano"                      │
                       └───────────────────┬───────────────────────────┘
                                            │ POST webhook + Bearer auth
                                            ▼
        ┌───────────────────────────────────────────────────────────────────┐
        │                    n8n — Workflow Principal                        │
        │                    (sys-agente-principal-v1.json)                  │
        │                                                                    │
        │     [Webhook] → [Normalize] → [Buscar/Crear Lead Airtable]         │
        │       → [Cargar Session State Postgres] → [Build User Msg Ctx]     │
        │       → [AI AGENT gpt-4o]  ←──┐                                    │
        │            ├─ Postgres Chat Memory (20 turnos)                     │
        │            ├─ 8 tools sub-workflows (toolWorkflow nodes)           │
        │            └─ User msg con [CONTEXTO TURNO]                        │
        │       → [Log Tool Calls Postgres]                                  │
        │       → [FORMATEAR MENSAJE gpt-4o-mini JSON output]   ← v0.5 nuevo │
        │       → [Split Respuesta: parsea JSON + compacta partes]           │
        │       → [setCustomFields ManyChat] → [sendFlow ManyChat]           │
        │       → [Update Lead Airtable] → [Update Session State Postgres]   │
        │       → [Respond to Webhook]                                       │
        └────────────────────┬──────────────┬────────────────┬───────────────┘
                              │              │                │
                              ▼              ▼                ▼
                  ┌──────────────────┐ ┌──────────────┐ ┌──────────────┐
                  │     SUPABASE      │ │  AIRTABLE    │ │   GMAIL +    │
                  │  Postgres         │ │ SyS Catalogo │ │   TELEGRAM   │
                  │  - n8n_chat_*     │ │  11 tablas   │ │ (notif lead) │
                  │  - sys_tool_calls │ │              │ │              │
                  │  - sys_session_*  │ │              │ │              │
                  └──────────────────┘ └──────────────┘ └──────────────┘
```

---

## Componentes

| Componente | Herramienta | Función | Estado |
|-----------|-------------|---------|--------|
| Canales conversacionales | WhatsApp Business + Instagram DM + Facebook Messenger | Recepción + envío de mensajes con cliente final | Producción cliente |
| Gestión de sesiones canal | ManyChat (Pro) | Webhook routing, custom fields, flows, multi-canal | Producción cliente |
| Orquestación | n8n (DigitalOcean self-hosted la agencia) | Workflow principal + 8 sub-workflows tools | A construir |
| LLM principal | OpenAI gpt-4o | Razonamiento conversacional + tool calling | API existente |
| LLM auxiliar (tools internas) | OpenAI gpt-4.1-mini | Clasificación de aplicaciones, ranking ambiguo | API existente |
| LLM formatter de respuesta | OpenAI gpt-4o-mini (`@n8n/n8n-nodes-langchain.openAi`, jsonOutput, temperature=0) | Particiona el output del AI Agent en 1-3 bloques estructurados `{parte1, parte2, parte3}` para envío secuencial vía ManyChat. Preserva exactamente marcas/modelos del catálogo. Patrón validado en NPR/NVJ/HBV/STK. **F7 — 2026-06-03.** Detalle: `06_docs/formatter-mensajes-config.md` | LIVE |
| Memoria persistente | Supabase Postgres (Free tier, sa-east-1) | Historial conversacional + tool calls + session state | A crear |
| Base de conocimiento / RAG | Airtable (base SyS Catalogo, **12 tablas**) | Single source: equipos (92 reales), tecnologías (10), FAQs (12), representantes (1), cabezales (10), insumos (33), inventario Konica refurbished (21). **Tabla Leads creada pero sin uso productivo (CRM pausado 2026-05-28).** Schema re-alineado al Excel real del cliente 2026-05-29 — ver `06_docs/realineacion-post-excel-2026-05-29.md` | F1 ejecutada parcialmente, requiere re-import post-realineación |
| Notificaciones a representante | Gmail SMTP + Telegram bot interno | Mail al rep + Gerente; alerts al el equipo | Existente (compartido) |
| Observabilidad | Postgres `sys_tool_calls` + Telegram alerts | Logs, métricas, monitoreo. **Vistas Airtable Leads omitidas en F1 (CRM pausado)** | A crear |

---

## Integraciones

| De | A | Método | Auth |
|----|---|--------|------|
| ManyChat | n8n webhook `/sys-agent` | HTTP POST JSON | Header `Authorization: Bearer {{MANYCHAT_AUTH_TOKEN}}` |
| n8n | OpenAI Chat Completions | HTTP via n8n LangChain node | API Key (n8n credential) |
| n8n | Postgres Chat Memory | n8n LangChain node | Connection string Supabase (n8n credential) |
| n8n | Airtable | n8n Airtable node | Personal Access Token con scope a base |
| n8n | ManyChat API (`setCustomFields`, `sendFlow`) | HTTP POST | Header `Bearer {{MANYCHAT_API_KEY_SYS}}` |
| n8n | Gmail (notificación al rep) | n8n Gmail node | OAuth credential |
| n8n | Telegram bot | n8n Telegram node | Bot token (compartido) |
| Sub-workflows tools | Workflow principal | Execute Workflow Trigger | Internal n8n |

---

## Decisiones de arquitectura

| # | Decisión | Alternativa descartada | Razón |
|---|---|---|---|
| 1 | ManyChat como gateway de los 3 canales | WhatsApp Business API directa + IG Graph API + Messenger Platform | ManyChat unifica los 3 canales con UX consistente, gestiona estados, custom fields, y reduce N webhooks a 1. Cliente ya está contratado con ManyChat. |
| 2 | gpt-4o como modelo principal | gpt-4.1-mini / Claude 3.5 Sonnet / Gemini | Tool calling robusto + multi-idioma rioplatense excelente. Validado en CRZ + STK. mini reservado para tareas chicas dentro de tools. |
| 3 | Tools como sub-workflows n8n separados | Tools inline en workflow / HTTP Request Tool puro | Permite versionar, testear y reutilizar cada tool. Patrón validado en STK. Mantenimiento granular. |
| 4 | Postgres (Supabase) para memoria | LangChain MemoryBufferWindow / Redis / Airtable | Postgres es persistente, soporta SQL custom, y Supabase free tier alcanza. Patrón validado en CRZ/STK/NPR. |
| 5 | Airtable como single-source catálogo | Mantener 6 Google Sheets / Notion DB / Supabase tables | Airtable da relaciones, vistas, validaciones, mobile editing. Sheets es plano y no escala. Notion DB es lento para queries. Postgres-only requiere portal admin custom. |
| 6 | Search nativo Airtable (filterByFormula + tool LLM si N>5) | Embeddings + pgvector | Catálogo SYS <500 records, queries estructuradas (tecnología, línea, aplicación). Embeddings = overkill. Reservado para v2.1 si aparecen queries vagas frecuentes. |
| 7 | División respuesta en 3 partes con `---` + custom fields `ai_msg_*` namespaced | Múltiples webhook calls / streaming / patrón legacy `parte1/2/3` sin prefijo | ManyChat solo acepta 1 respuesta sincrónica al webhook. setCustomFields + sendFlow es el patrón validado. **SYS F6 adopta el [ManyChat Standard interno 2026](../../../_core/standards/manychat-integration-pattern.md)**: naming `ai_msg_1/2/3 + ai_msg_count`, auth via n8n Credential (no Bearer hardcoded), payload dinámico vía Code node. Mejora vs CRZ/NVJ/IMP legacy. **F7 2026-06-03: agregado nodo Formatter intermedio** — ver decisión #17. |
| 17 | **Formatter dedicado gpt-4o-mini** intercalado entre AI Agent y Split Respuesta | Solo reforzar el prompt principal para que use `---` separadores | gpt-4o omitía los `---` en respuestas con tool calls → Split Respuesta lumpeaba todo a `ai_msg_1` → ManyChat mandaba mensaje único largo. Reforzar el prompt es frágil (LLM ignora la regla bajo carga). Patrón formatter validado en NPR/NVJ/HBV/STK. Trade-off aceptado: +300ms latencia y +$0.0005/turno por reliability garantizada. JSON output con `parte1/2/3` + Split Respuesta compacta partes no-vacías (defensa contra modelo que llene parte1+parte3 saltando parte2). Detalle: `06_docs/formatter-mensajes-config.md`. |
| 8 | Tool `notificar_lead` como única write | Workflow paralelo que detecta cierre con regex sobre output | Tool calling es declarativo y auditable. LLM decide explícitamente. Idempotencia controlada en sub-workflow. |
| 9 | Sin Redis anti-spam en v2.0 | Implementar siempre (patrón STK/NPR) | Volumen esperado SYS (B2B) es bajo. Suma complejidad sin beneficio inmediato. Mover a v2.1 si pico real. |
| 10 | Sin Whisper / Vision en v2.0 | Implementar desde start | Audios e imágenes estaban explícitamente bloqueados en v1.6 ("próxima etapa"). Mover a v2.1 cuando cliente lo solicite. |
| 11 | Truncar memoria a 3000 chars en query (no en write) | Resumen LLM al exceder N turnos | Conversaciones SYS cortas (5-20 turnos). Truncar es simple y efectivo. Resumen va a v2.2 si conversaciones se alargan. |
| 12 | Sessions por canal+sub_id | Sessions globales por persona (cross-canal) | Mismo cliente en IG y WA = conversaciones distintas. Refleja cómo lo percibe el usuario. Cross-canal sería v3.0. |
| 13 | Migración total Sheets → Airtable | Sync periódico Sheets → Airtable | Single source. Cliente edita un solo lugar. Sync adds otra pieza al sistema. Onboarding Edgardo de 30 min cubre el cambio. |
| 14 | Notificación rep por mail + Telegram | Solo mail / solo Telegram / WhatsApp directo al rep | Mail = formal y respaldo. Telegram = inmediato a la agencia para monitoreo. WhatsApp al rep sería intrusivo y requeriría más infra. |
| 15 | Idempotencia notificar_lead con ventana 30 min | Sin idempotencia / siempre upsert | Si LLM invoca 2 veces → no spam al rep. 30 min cubre la latencia esperada. |
| 16 | Logging tool calls a Postgres (no a archivos) | n8n logs nativos / archivo CSV | SQL queryable para debugging + métricas. Mismo pattern que STK. |

---

## Flujo técnico de un turno (orden de operaciones)

```
1. ManyChat dispara External Request a webhook n8n
   - Body: { canal, subscriber_id, mensaje, custom_fields, ... }
   - Header: Authorization: Bearer ${MANYCHAT_AUTH_TOKEN}

2. n8n Webhook recibe (responseMode: lastNode, timeout 25s)

3. Normalize Payload (Code):
   - Detecta canal (wa/ig/fb)
   - Extrae subscriber_id, mensaje
   - Construye leadIdentifier = canal + "_" + subscriber_id
   - Skip si mensaje vacío

4. Buscar/Crear Lead en Airtable
   - filterByFormula: {Subscriber ID} = "..." AND {Canal} = "..."
   - Si NO existe: crear con Status=Nuevo, Canal, Subscriber ID, timestamp

5. Cargar Session State (Postgres SELECT)
   - SELECT * FROM sys_session_state WHERE session_id = ...
   - Si NO existe: INSERT default (etapa=bienvenida, datos_capturados={}, productos_mostrados=[])

6. Build User Message Context (Code):
   - Inyecta [CONTEXTO TURNO] al user message con: canal, fecha, perfil, etapa,
     datos capturados, productos mostrados

7. AI Agent (gpt-4o, timeout 18s)
   - System message: prompt v2.0 con {{NOMBRE_AGENTE}} y {{URL_TIENDA}} resueltos
   - User message: del paso 6
   - Memory: Postgres Chat Memory (sessionKey = leadIdentifier, window 20)
   - Tools: 8 sub-workflows conectados
   - returnIntermediateSteps: true (para logging)

8. Log Tool Calls (Postgres INSERT loop)
   - Para cada intermediateStep:
     INSERT INTO sys_tool_calls VALUES (...)

9. Formatear mensaje (gpt-4o-mini, jsonOutput=true, temperature=0) — **F7 2026-06-03**
   - Input: $('AI Agent').first().json.output (con o sin separadores `---`)
   - System message: ver `06_docs/formatter-mensajes-config.md` (3 secciones: dividir / formatear / preservar nombres técnicos)
   - Strip de `¿`, `¡`, `'`, `"` en el input (patrón heredado de RCA)
   - Output: JSON `{parte1: string, parte2: string, parte3: string}` (alguna(s) pueden ser "")

10. Split Respuesta (Code) — **v3 jsCode actualizado**
    - Parsea el JSON del paso 9 con try/catch (fallback: todo a `parte1` si parsea mal)
    - **Compacta partes no-vacías** y asigna en orden a `ai_msg_1/2/3`
      (defensa contra gpt-4o-mini que llene parte1+parte3 saltando parte2)
    - Calcula `ai_msg_count` = cantidad de partes no-vacías
    - Conserva `raw` con el output original del AI Agent para auditoría

11. setCustomFields ManyChat (HTTP POST)
    - URL depende de canal: /fb/ vs /ig/ vs /wa/
    - Body: subscriber_id + fields [ai_msg_1, ai_msg_2, ai_msg_3, ai_msg_count]

11. sendFlow ManyChat (HTTP POST)
    - Trigger flow "Responder Multi-Parte" en ManyChat
    - Ese flow envía las 3 partes con delays naturales

12. Update Lead Airtable
    - Última actividad, Status (si cambió), Etapa, Datos capturados nuevos

13. Update Session State (Postgres upsert function)
    - SELECT upsert_session_state(...) — function definida en supabase-schema.sql

14. Respond to Webhook
    - { ok: true, trigger_flow: "responder_multi_parte" }
```

---

## Capacidad y costos

| Item | Capacidad / costo | Notas |
|---|---|---|
| Supabase Free tier | 500 MB DB, 2 GB egress/mes, 60 conexiones concurrent | Cubre SYS por 6+ meses |
| Airtable | 1000 records/base (Free) o 50000 (Team $20/mes) | Si Leads supera 800, upgrade a Team |
| OpenAI gpt-4o | ~$0.005/conversación (turno típico) | 1000 conv/mes ≈ $5–10 |
| OpenAI gpt-4.1-mini (tools internos) | ~10% del costo gpt-4o | Despreciable |
| n8n self-hosted | $0 incremental (DigitalOcean droplet compartido) | |
| ManyChat Pro | $15/mes | Cliente paga |
| Total la agencia mensual | $25–40 + $20 (si Airtable Team) | |

---

## Riesgos identificados

Ver [Plan Maestro §14](/Users/camilo/.claude/plans/contexto-general-del-dapper-sun.md) — 17 riesgos identificados con mitigación específica.

Top 5 más críticos:

| Riesgo | Mitigación |
|---|---|
| LLM tarda >20s y ManyChat hace timeout | Timeout AI Agent a 18s; fallback humano si excede |
| LLM inventa specs (alucinación) | Reglas anti-alucinación + retrieve real Airtable + revisión primeros 50 leads |
| `notificar_lead` con datos incompletos | Validación bloqueante en sub-workflow + prompt explícito |
| Edgardo edita Airtable y rompe schema | Guía editor + monitoreo errores tool_calls |
| Costo OpenAI explota por loop | Rate limit por sub_id en future v2.1; monitoreo dashboard |

---

## Migración desde Etapa 1

| Etapa 1 (v1.7 Telegram) | Etapa 2 (v2.0 ManyChat) |
|---|---|
| Trigger Telegram | Trigger Webhook ManyChat |
| Memoria LangChain BufferWindow (volátil) | Postgres Chat Memory (persistente, 20 turnos) |
| 6 "tools" como referencia a Sheets | 8 tools reales sub-workflows |
| KB hardcodeada en prompt (~70 líneas) | KB en Airtable, consultada con `consultar_tecnologia` |
| `[NOTIFICAR_LEAD]` placeholder texto | Tool real con asignación rep + mail + Telegram |
| `[REGISTRAR_LEAD]` placeholder | Se ejecuta dentro de `notificar_lead` |
| `[COMPLETAR mes a mes]` hardcoded | Tool `consultar_lineas_priorizadas` |
| Variables: `[NOMBRE_AGENTE]`, `[URL_TIENDA]` | + `{{CANAL}}`, `{{FECHA_HOY}}`, `{{PERFIL_LEAD}}`, `{{ETAPA_ACTUAL}}`, `{{DATOS_CAPTURADOS}}`, `{{PRODUCTOS_MOSTRADOS}}` |

---

## Referencias

- [Plan Maestro Etapa 2](/Users/camilo/.claude/plans/contexto-general-del-dapper-sun.md) — diseño completo
- [System Prompt v2.0](../04_agents/agente-sistemasysoluciones-system-prompt.md)
- [Schema Airtable](../05_crm/airtable-syscatalogo-schema.md)
- [Schema Supabase](../06_docs/supabase-schema.sql)
- [Tools Spec v1](../06_docs/tools-spec-v1.md)
- [Guía Edgardo](../06_docs/guia-airtable-edgardo-v1.md)
- [Runbook](../06_docs/runbook.md)

---

**Documento vivo. Actualizar cuando cambien decisiones arquitectónicas o componentes.**
