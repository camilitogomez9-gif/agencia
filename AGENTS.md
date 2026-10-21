# AGENTS.md

Este archivo provee instrucciones a Codex (Codex.ai/code) cuando trabaja con código en este repositorio.

---

## Qué Es Esto

Este es el **workspace operativo de la agencia** — un entorno estructurado diseñado para trabajar con Codex como asistente agente entre sesiones. El usuario abrirá nuevas sesiones de Codex repetidamente, usando `/iniciar` al comienzo de cada una para cargar contexto esencial sin sobrecargar el contexto.

**Este archivo (AGENTS.md) es la base.** Se carga automáticamente al inicio de cada sesión. Mantenelo actualizado — es la única fuente de verdad sobre cómo Codex debe entender y operar dentro de este workspace.

---

## La Relación Codex-Usuario

Codex opera como un **asistente agente** con acceso a las carpetas del workspace, archivos de contexto, comandos y salidas. La relación es:

- **Usuario**: Define objetivos, provee contexto sobre su rol/función y dirige el trabajo mediante comandos
- **Codex**: Lee el contexto, entiende los objetivos del usuario, ejecuta comandos, produce salidas y mantiene la consistencia del workspace

Codex siempre debe orientarse a través de `/iniciar` al inicio de la sesión, y luego actuar con plena conciencia de quién es el usuario, qué está tratando de lograr y cómo este workspace lo apoya.

---

## Control de Versiones

El workspace usa **git** para tracking de cambios. Esto permite que `/cliente-sync` detecte
con precisión qué archivos se crearon o modificaron en cada sesión de trabajo.

- Todo cambio significativo termina en un `git commit` automático vía `cliente-sync`
- El historial git es el log de trabajo por cliente
- Convención de commits: `sync(IMP): descripción del trabajo realizado`
- Para ver el historial de un cliente: `git log --oneline -- clients/IMP_ImportadoresConectados/`

---

## Estructura del Workspace

```
.
├── AGENTS.md              # Este archivo — contexto principal, siempre cargado
├── README.md              # Visión general del workspace
├── shell-aliases.md       # Alias bash para operaciones comunes
├── .gitignore             # Archivos excluidos del tracking
│
├── .Codex/
│   ├── commands/          # Comandos que Codex puede ejecutar
│   └── skills/            # Skills personalizados
│
├── _core/                 # Recursos compartidos reutilizables (no son de un cliente específico)
│   ├── modules/           # Módulos de integración (airtable, n8n, whatsapp, etc.)
│   ├── prompts/           # Prompts base para agentes
│   │   └── agents/        # System prompts reutilizables
│   ├── standards/         # Convenciones de nomenclatura, metodologías, guías
│   └── templates/         # Plantillas base
│       ├── agents/        # Plantilla de agente IA
│       ├── workflows/     # Workflows n8n reutilizables por tema
│       └── docs_client/   # Plantilla CLIENT_INFO.md
│
├── clients/               # Proyectos por cliente
│   ├── _template/         # Plantilla estándar para duplicar al crear un cliente nuevo
│   ├── IMP_ImportadoresConectados/  # Agente de ventas conversacional
│   └── SNR_Sonrisas/      # Automatización reporte de facturación
│
├── agents/                # Agentes IA corporativos (la agencia propio)
├── workflows/             # Workflows n8n organizados por integración y nicho
├── docs/                  # Documentación interna, ADRs, runbooks
├── planes/                # Planes del modo plan integrado de Codex/Claude Code
├── ops/                   # Operaciones del ciclo de vida de clientes
├── testing/               # QA, sandbox, bug reports
│
├── scripts/
│   ├── generators/        # Scripts que generan nuevas estructuras
│   └── utilities/         # Scripts de soporte operacional
│
├── contexto/              # Contexto de fondo sobre el negocio y objetivos
│
└── salidas/               # Herramientas internas de la agencia
    ├── call-audit/        # Endpoint Modal para auditoría de llamadas de venta
    ├── telegram-bot/      # Bot Telegram (proof of concept)
    ├── modal_saarev/      # Proyecto experimental Modal
    └── diagramas/         # Diagramas draw.io generados por /diagramar
```

**Directorios principales:**

| Directorio       | Propósito                                                                                  |
| ---------------- | ------------------------------------------------------------------------------------------ |
| `_core/`         | Recursos reutilizables entre clientes: prompts, templates, estándares de nomenclatura.     |
| `clients/`       | Un directorio por cliente. Cada uno sigue el ciclo 01_discovery → 08_delivery.            |
| `agents/`        | Agentes IA propios de la agencia (no de clientes específicos).                               |
| `workflows/`     | Workflows n8n organizados por integración (`by-integration/`) y nicho (`by-niche/`).      |
| `docs/`          | Documentación interna, decisiones de arquitectura, runbooks.                               |
| `planes/`        | Planes del modo plan integrado de Codex/Claude Code para este workspace.                   |
| `ops/`           | Procesos de onboarding, desarrollo, mantenimiento y upsell de clientes.                    |
| `testing/`       | Sandbox, casos de prueba, reportes de bugs.                                                |
| `scripts/`       | Scripts de automatización. Utilidades en `utilities/`, generadores en `generators/`.       |
| `contexto/`      | Quién es el usuario, su rol, prioridades actuales. Leído por `/iniciar`.                   |
| `salidas/`       | Herramientas internas activas de la agencia (endpoints, bots, experimentos).                 |

---

## Skills de Cliente

Skills para gestionar el ciclo de vida completo de clientes. Se invocan con `/nombre-skill` o describiéndole la acción a Codex.

| Skill | Trigger | Qué hace |
|-------|---------|----------|
| `/cliente-nuevo` | "crear cliente", "nuevo cliente", "onboarding X" | Crea `clients/CLTXXX_Nombre/` desde `_template`, completa `CLIENT_INFO.md`, registra en AGENTS.md |
| `/cliente-avance` | "avancé en X", "actualizar cliente X", "registrar progreso" | Crea/edita archivos en la carpeta del cliente según la fase; actualiza `CLIENT_INFO.md` y AGENTS.md |
| `/cliente-upsell` | "upsell para X", "nueva oportunidad con X" | Documenta el upsell en `ops/04_upsells/` y actualiza el cliente |
| `/cliente-estado` | "estado de X", "status de X", "qué tenemos con X" | Lee todos los archivos del cliente y genera un briefing completo |
| `/cliente-sync` | automático al final de cada skill, o "sincronizar X" | Escanea outputs nuevos, actualiza `CLIENT_INFO.md` y AGENTS.md, reporta solo qué cambió |
| `/generar-system-prompt` | "crear system prompt", "generar prompt para el agente de X", "escribir instrucciones para el bot" | Genera un system prompt completo optimizado para n8n, listo para copiar y pegar |
| `/iterar-prompt` | "integrar esto al prompt", "actualizar prompt con...", "resultados del testing", "corregir el prompt", "ajustes post-testing", "el cliente mandó correcciones" | Integra nueva información a un prompt existente (Modo A) o aplica correcciones post-testing (Modo B). Siempre versiona antes de modificar y actualiza la guía de testing. |

---

## Comandos

### /iniciar

**Propósito:** Inicializar una nueva sesión con plena conciencia del contexto.

Ejecutalo al inicio de cada sesión. Codex:

1. Leerá AGENTS.md y los archivos de contexto
2. Resumirá su comprensión del usuario, el workspace y los objetivos
3. Confirmará que está listo para asistir

### /crear-plan [pedido]

**Propósito:** Crear un plan de implementación detallado antes de hacer cambios.

Usalo cuando se agrega nueva funcionalidad, comandos, scripts, o se hacen cambios estructurales. Produce un documento de plan en `planes/` que captura contexto, justificación y tareas paso a paso.

Ejemplo: `/crear-plan agregar agente de seguimiento para clientes dental`

### /implementar [ruta-al-plan]

**Propósito:** Ejecutar un plan creado por /crear-plan.

Lee el plan, ejecuta cada paso en orden, valida el trabajo y actualiza el estado del plan.

Ejemplo: `/implementar planes/agente-dental-follow-up-2026-04-10.md`

---

## Instrucción Crítica: Mantener Este Archivo

**Siempre que Codex haga cambios en el workspace, DEBE considerar si AGENTS.md necesita actualizarse.**

Después de cualquier cambio — agregar comandos, clientes, scripts, flujos de trabajo, o modificar la estructura — preguntarse:

1. ¿Este cambio agrega nueva funcionalidad que los usuarios necesitan conocer?
2. ¿Modifica la estructura del workspace documentada arriba?
3. ¿Debe listarse un nuevo comando?
4. ¿Se agregó un nuevo cliente en `clients/`?

Si la respuesta es sí a cualquiera, actualizar las secciones relevantes. Este archivo debe siempre reflejar el estado actual del workspace.

---

## Flujo de Trabajo de Sesión

1. **Inicio**: Ejecutar `/iniciar` para cargar el contexto
2. **Trabajo**: Usar comandos o dirigir a Codex con tareas
3. **Planificar cambios**: Usar `/crear-plan` antes de adiciones significativas
4. **Ejecutar**: Usar `/implementar` para ejecutar los planes
5. **Mantener**: Codex actualiza AGENTS.md y `contexto/` a medida que el workspace evoluciona

---

## Convenciones de Nomenclatura

Ver `_core/standards/naming_conventions.md` para el diccionario completo. Resumen:

| Tipo | Formato | Ejemplo |
|------|---------|---------|
| Cliente | `[XXX]_Nombre` | IMP_DiegoLabores |
| Workflow n8n | `WF_[NICHE]_[FUNCION]_v[N]` | WF_DENTAL_LeadCapture_v1 |
| Agente IA | `AGT_[FUNCION]_v[N]` | AGT_Booking_v2 |
| Prompt | `PRM_[ROL]_[NICHE]_v[N]` | PRM_QualificationBot_Dental_v2 |
| Módulo | `MOD_[INTEGRACION]_[FUNCION]` | MOD_WA_SendMessage |

Nichos válidos: `DENTAL` | `REALESTATE` | `AGENCY` | `AUTO` | `GENERIC`

---

## Clientes Activos

### IMP — Importadores Conectados / Diego Labores (`clients/IMP_ImportadoresConectados/`)

Agente de ventas conversacional para @diegolabores (negocio: Importadores Conectados — cursos y mentoría de importaciones). Responde DMs en Instagram, WhatsApp y Facebook usando n8n AI Agent con Gemini 2.5 Flash. CRM en Airtable, notificaciones al equipo por Telegram.

**Contactos:** Diego Labores (dueño) · Georgina Paradiso / Geor (secretaria)

**Stack:** ManyChat + WhatsApp Business API + n8n + Airtable + Gemini 2.5 Flash + Telegram

**Archivos clave:**
- `03_workflows/flujo-n8n-agente-diegolabores.json` — Workflow de producción (IG + WhatsApp + Facebook)
- `03_workflows/flujo-n8n-telegram-test.json` — Workflow de prueba con Telegram
- `04_agents/agente-diegolabores-system-prompt.md` — System prompt (legacy; ver brand-bible)
- `05_crm/airtable-leads-db-schema.md` — Esquema tabla Leads en Airtable
- `06_docs/brand-bible.md` — **Fuente de verdad**: productos, precios, avatar, tono. Actualizar aquí cuando cambien productos o posicionamiento.

**Variables n8n:** `AIRTABLE_BASE_ID_DIEGOLABORES`, `AIRTABLE_TABLE_LEADS`, `MANYCHAT_API_KEY`, `TELEGRAM_CHAT_ID_EQUIPO`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_ACCESS_TOKEN`

> Nota: carpeta física renombrada de `IMP_DiegoLabores` a `IMP_ImportadoresConectados` el 2026-04-17.

---

### SNR — Sonrisas (`clients/SNR_Sonrisas/`)

Automatización del reporte de facturación mensual para clínica dental Sonrisas.

**Archivos clave:**
- `03_workflows/sonrisas-registro-inasistencias-v2.json` — Workflow n8n de facturación
- `03_workflows/sonrisas-reporte-facturacion-v3.json` — Workflow final reporte facturación (semana año + semana mes por sucursal, limpieza mensual MES CORRIENTE)
- `06_docs/sonrisas-metricas-inasistencias.md` — Documentación del proceso

**Actualizar códigos:** cuando se actualiza el Listado de Precios, ejecutar:
```bash
python3 scripts/utilities/update-sonrisas-nodes.py ~/Downloads/"Listado de Precios Completo.xlsx"
```

---

### SYS — Sistemas y Soluciones (`clients/SYS_SistemasYSoluciones/`)

Agente de calificación y asesoramiento para la industria gráfica. Atiende leads entrantes en WhatsApp, Instagram y Facebook; califica la necesidad del cliente, asesora sobre tecnologías de impresión, y deriva al representante comercial con notificación por mail.

**Stack:** n8n + AI Agent + Planillas Drive + mail

**Archivos clave:**
- `04_agents/agente-sistemasysoluciones-system-prompt.md` — System prompt v1.1
- `07_testing/testing-guide-v1.md` — Guía de testing inicial

**Pendientes:** nombre del agente, URL tienda online de insumos, listado de equipos (responsable: Edgardo), showroom/financiación FAQs

---

### VTR — Venttur (`clients/VTR_Venttur/`)

Tracking de conversiones Lead en Meta CAPI para plataforma educativa. Recibe folios desde landings via webhook, los cruza con datos CAPI en Airtable, y envía eventos Lead a Meta al momento de la conversación en WhatsApp. Pendiente: rama CTWA (Opción A — reporting interno por programa).

**Stack:** ManyChat + WhatsApp Business API + n8n + Airtable + Meta CAPI

**Infraestructura:**
- Airtable base: `[AIRTABLE_BASE_ID]` | Credentials n8n: `[N8N_CREDENTIAL_ID]`
- Tablas: Folios CAPI (`[AIRTABLE_TABLE_ID]`), Programas CAPI (`[AIRTABLE_TABLE_ID]`), Leads (`[AIRTABLE_TABLE_ID]`)

**Archivos clave:**
- `03_workflows/meta-capi-venttur-v2.json` — Workflow corregido (fix Update record1 + Buscar Folio)

**Pendientes:** implementar rama CTWA Opción A en Flow 2 (requiere lista de programas + textos pre-cargados del cliente)

---

### CLZ — Collazo Servicio Técnico (`clients/CLZ_Collazo/`)

Agente conversacional que responde consultas, detecta el servicio necesario (aires, calefones, electricidad) y guía al usuario a reservar via cal.com. Incluye seguimiento automático 8 hs post-conversación via Chatrace.

**Stack:** n8n + OpenAI GPT-4o + PostgreSQL (memoria) + Chatrace + cal.com

**Archivos clave:**
- `03_workflows/agente-collazo-main.json` — Workflow principal del agente
- `03_workflows/seguimiento-collazo.json` — Sub-workflow de seguimiento automático (8 hs delay)
- `04_agents/agente-collazo-system-prompt.md` — System prompt v1.1 (precio instalación calefón + comportamiento proactivo mantenimiento)
- `07_testing/testing-guide-v1.md` — Guía de testing v1

---

### NVJ — Narvaja Hogar (`clients/NVJ_Narvaja/`)

Agente de ventas conversacional para Narvaja Hogar (tienda uruguaya de artículos para el hogar: colchones, sommiers, roperos, sofás, electrodomésticos). Responde consultas via WhatsApp, Instagram y Facebook; transcribe audios, analiza imágenes y eleva conversaciones al equipo humano con resumen.

**Stack:** ManyChat + WhatsApp + n8n + OpenAI GPT-4.1-mini/GPT-4o-mini + Airtable + PostgreSQL (memoria)

**Archivos clave:**
- `03_workflows/narvaja-agente-principal-v1.json` — Workflow principal (agente conversacional + anti-loop + canal WPP/IG/FB)
- `03_workflows/narvaja-elevar-conversacion-v1.json` — Sub-workflow de escalamiento al equipo humano
- `03_workflows/narvaja-resumen-semanal-v1.json` — Workflow de resumen semanal automático (métricas → Telegram)
- `03_workflows/narvaja-resumen-semanal-v2.json` — Resumen semanal v2 (análisis gpt-4o-mini, JSON estructurado, HTML por Gmail)
- `03_workflows/narvaja-resumen-semanal-v3.json` — Resumen semanal v3 (conteos deterministas en JS, prompt secuencial, listas cerradas, temperature=0, seed=42)

---

## Herramientas Internas

### Auditoría de Llamadas (`salidas/call-audit/`)

Endpoint serverless (Modal) que recibe transcripciones de llamadas de ventas y devuelve un scorecard objetivo en JSON (15 métricas, feedback accionable, objeciones detectadas). Se integra con n8n y Airtable: Fathom → n8n → Modal → Airtable.

**Para deployar:**
```bash
cd salidas/call-audit
modal deploy main.py
```

**Para testear localmente:**
```bash
cd salidas/call-audit
modal run main.py
```

**Requiere:** secrets en Modal: `openai-api-key` (OPENAI_API_KEY) y `api-auth-token` (API_AUTH_TOKEN).

**Templates de referencia:** `_core/templates/workflows/auditoria-llamadas/`

---

### Agente Outreach IG

Workflow n8n que automatiza respuestas de Instagram cuando un prospecto contesta un DM de outreach enviado manualmente. ManyChat como canal; n8n consulta Notion para discriminar outreach vs. inbound; Gemini genera respuestas con delays naturales de tipeo.

**Stack:** ManyChat + n8n + Notion + Gemini 2.5 Flash

**Para activar:**
1. Importar `_core/templates/workflows/outreach-ig/flujo-n8n-outreach-ig.json` en n8n
2. Configurar variables: `MANYCHAT_API_KEY`, `NOTION_API_TOKEN`, `NOTION_OUTREACH_DB_ID`, `GEMINI_API_KEY`
3. Crear Flow en ManyChat → External Request POST al webhook de n8n con body `{ subscriber_id, ig_username, last_message, conversation_id }`

**System prompt:** `_core/templates/workflows/outreach-ig/agente-outreach-ig-system-prompt.md`
**Schema Notion:** `_core/templates/workflows/outreach-ig/notion-outreach-db-schema.md`

---

### Bot de Telegram

Bot centralizado para notificaciones y comandos operativos de la agencia. Corre en n8n (DigitalOcean). Referencia completa en `_core/templates/workflows/telegram/telegram-bot.md`.

**Funcionalidades activas:**
- **Captura de ideas de video** (`_core/templates/workflows/telegram/flujo-n8n-bot-ideas.json`): texto o audio → Groq Whisper → Groq LLaMA → Notion DB "Reels IG". Confirma "Idea guardada ✅".
- **Reporte semanal** (`_core/templates/workflows/telegram/flujo-n8n-bot-reporte-semanal.json`): schedule semanal → Notion Finanzas → Groq genera mensaje sarcástico → grupo Telegram.

---

### Diagramador de Contexto (`salidas/diagramas/`)

Comando `/diagramar` que convierte texto no estructurado en diagramas visuales draw.io. Detecta automáticamente el tipo de input (flujo de ventas, mapa mental, diagrama de proceso, mapa de relaciones).

```
/diagramar [pegar texto o transcripción aquí]
```

Los diagramas se guardan en `salidas/diagramas/`. Guía de tipos: `_core/standards/drawio-tipos-diagrama.md`.

---

## Scripts Utilitarios

### Actualizador de Nodos Sonrisas (`scripts/utilities/update-sonrisas-nodes.py`)

Genera código JS para los nodos **Filtro** y **Clase** del flujo `Sonrisas | Reporte Facturación` a partir del Listado de Precios completo.

```bash
python3 scripts/utilities/update-sonrisas-nodes.py ~/Downloads/"Listado de Precios Completo.xlsx"
```

Criterios automáticos:
- **Filtro**: incluye códigos con `Computa para Planilla Importe == SI`
- **Clase**: clasifica códigos `Computa para Planilla Cantidad == SI` en AJUSTE (OA*), COMBO (OR100+), RETIRO (OR001–OR007)

**Requiere:** `pandas` y `openpyxl` (`pip install pandas openpyxl`)

---

## Templates y Recursos Compartidos (`_core/`)

| Ubicación | Contenido |
|-----------|-----------|
| `_core/standards/naming_conventions.md` | Convenciones de ID para workflows, agentes, prompts, módulos |
| `_core/standards/drawio-tipos-diagrama.md` | Guía de tipos de diagrama draw.io y plantillas XML |
| `_core/standards/ventas/` | Metodología de llamada de ventas + rúbrica de evaluación |
| `_core/templates/workflows/auditoria-llamadas/` | Esquemas JSON/Airtable + flujos n8n para auditoría de llamadas |
| `_core/templates/workflows/llamadas/` | Pipeline Fathom → n8n → Notion + Pinecone |
| `_core/templates/workflows/outreach-ig/` | Workflow + system prompt + schema Notion para outreach IG |
| `_core/templates/workflows/telegram/` | Workflows del bot Telegram (ideas + reporte semanal) |
| `_core/templates/workflows/linkedin-pipeline/` | Prompts YT → infografía → LinkedIn |
| `_core/prompts/agents/` | System prompts reutilizables (outreach, linkedin) |
| `_core/templates/agents/AGT_BASE_v1.md` | Plantilla base para definir un agente IA |
| `_core/templates/agents/SYSTEM_PROMPT_TEMPLATE.md` | Template modular para system prompts de agentes conversacionales en n8n |
| `_core/templates/agents/testing-guide-template.md` | Template base para guías de testing de agentes. Usado por `/iterar-prompt` y `/generar-system-prompt`. |
| `_core/standards/system-prompt-engineering.md` | Principios, patrones y checklist para diseño de system prompts |
| `_core/templates/workflows/agente-telegram/` | Template workflow n8n para agente conversacional v1 canal Telegram (Airtable + AI Agent + notificaciones) |
| `_core/templates/workflows/WF_BASE_v1.md` | Plantilla base para documentar un workflow n8n |

---

## Instrucción Crítica: Mantener Este Archivo

Actualizar AGENTS.md cada vez que:
- Se agrega un nuevo cliente en `clients/` → agregar entrada en "Clientes Activos"
- Se agrega un script → documentar en "Scripts Utilitarios"
- Se modifica la estructura del workspace
- Se agrega un nuevo recurso importante a `_core/`

---

## Notas

- Mantener el contexto mínimo pero suficiente — evitar sobrecarga
- Los planes creados con el modo plan integrado de Codex/Claude Code para este workspace van en `planes/`, no en `/Users/camilo/.claude/plans/`.
- Los planes creados con `/crear-plan` también deben guardarse en `planes/` con nombres de archivo con fecha (ej. `proyecto-2026-04-10.md`).
- Para crear un cliente nuevo: duplicar `clients/_template/` y completar `CLIENT_INFO.md`
