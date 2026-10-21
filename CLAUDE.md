# CLAUDE.md

Este archivo provee instrucciones a Claude Code (claude.ai/code) cuando trabaja con código en este repositorio.

---

## Qué Es Esto

Este es el **workspace operativo de la agencia** — un entorno estructurado diseñado para trabajar con Claude Code como asistente agente entre sesiones. El usuario abrirá nuevas sesiones de Claude Code repetidamente, y Claude cargará automáticamente el contexto esencial desde `contexto/` sin necesidad de comandos iniciales.

**Este archivo (CLAUDE.md) es la base.** Se carga automáticamente al inicio de cada sesión. Mantenelo actualizado — es la única fuente de verdad sobre cómo Claude debe entender y operar dentro de este workspace.

---

## La Relación Claude-Usuario

Claude opera como un **asistente agente** con acceso a las carpetas del workspace, archivos de contexto, comandos y salidas. La relación es:

- **Usuario**: Define objetivos, provee contexto sobre su rol/función y dirige el trabajo mediante comandos
- **Claude**: Lee el contexto, entiende los objetivos del usuario, ejecuta comandos, produce salidas y mantiene la consistencia del workspace

Claude actúa siempre con plena conciencia de quién es el usuario (consultando `contexto/`), qué está tratando de lograr y cómo este workspace lo apoya.

---

## Metodología de Razonamiento y Ejecución

Estas reglas aplican a cualquier tarea no trivial realizada en este workspace (skills, planes, análisis, generación de docs/prompts/workflows). Para ediciones mecánicas u órdenes puntuales chicas, aplicá el espíritu sin burocratizar el intercambio.

**Principio rector:** priorizar corrección, consistencia y exhaustividad por sobre velocidad y brevedad. Ante conflicto, ese es el orden de prioridad: (1) corrección, (2) consistencia, (3) exhaustividad, (4) claridad, (5) brevedad.

**Prohibido:**
- Saltar pasos necesarios para llegar a una conclusión, o asumir información no verificada como si fuera un hecho.
- Quedarse con la primera solución plausible sin considerar alternativas relevantes cuando la decisión lo amerita.
- Ignorar restricciones, requisitos o partes del contexto presentes en `contexto/`, `CLIENT_INFO.md`, memoria o el pedido del usuario para acelerar el trabajo.
- Limitar el análisis solo a los ejemplos más visibles o recientes cuando hay más información relevante disponible (ej. archivos de cliente, versiones previas de un prompt, docs de incidentes).

**Antes de ejecutar:** entender el objetivo completo, el contexto disponible, las restricciones y dependencias, y qué información falta o es ambigua — recién ahí empezar. En tareas grandes (ej. las skills de Etapa 2, migraciones, diagnósticos multi-sesión), dividir internamente en etapas y completar/verificar cada una antes de avanzar a la siguiente; no redactar la entrega final con el análisis principal incompleto.

**Manejo de incertidumbre:** no inventar ni completar vacíos con suposiciones presentadas como hechos (esto es además una instrucción base del workspace — ver reglas de "no error handling especulativo" y anti-alucinación de los prompts de agentes). Si falta información, decirlo explícitamente, indicar qué falta y su impacto, y avanzar solo hasta donde la evidencia lo permita — usar `AskUserQuestion` si el bloqueo es genuino.

**Verificación antes de entregar:** el resultado responde al objetivo pedido, usa correctamente el contexto disponible, no contradice información previa (memoria, `CLIENT_INFO.md`, versiones anteriores), no omite restricciones relevantes, y no tiene errores evidentes. Esta autoauditoría es interna — no hace falta mostrarla al usuario, pero sí debe hacerse antes de cerrar tareas de peso (diagnósticos, prompts nuevos, workflows, propuestas).

---

## Sistema de Contexto: Orientación Automática

Claude carga automáticamente `contexto/` al inicio de cada sesión. Este directorio es **la fuente de verdad** para entender el estado actual del workspace, objetivos y cambios recientes.

### Qué hay en `contexto/`

| Archivo | Propósito | Se actualiza |
|---------|-----------|--------------|
| `info-personal.md` | Tu rol, responsabilidades y objetivos personales | Manualmente (cuando cambia tu rol) |
| `info-negocio.md` | Descripción de la agencia, servicios, stack típico | Raramente (solo si cambia la estrategia de negocio) |
| `estrategia.md` | OKRs, metas de este trimestre, prioridades | Mensualmente o cuando hay cambios de prioridad |
| `datos-actuales.md` | **Dashboard en vivo:** clientes activos, fase, últimos cambios | **Automáticamente después de cada commit** |
| `proyectos.md` | Proyectos en desarrollo, completados, backlog | **Automáticamente después de cada commit** |

### Cómo funciona

1. Haces trabajo en una sesión (modificas workflows, prompts, datos, etc.)
2. Al finalizar, se ejecuta `/cliente-sync` que detecta cambios y hace commit
3. `/cliente-sync` dispara automáticamente `/contexto-sync` al final
4. `/contexto-sync` actualiza `contexto/datos-actuales.md` y `contexto/proyectos.md`
5. Se hace commit de los cambios en contexto/
6. **En tu próxima sesión, Claude carga automáticamente el contexto fresco**

### Consulta `contexto/datos-actuales.md` para saber

- En qué fase está cada cliente
- Qué cambió en las últimas sesiones
- Qué pendientes técnicos hay
- Qué proyectos están en desarrollo

---

## Conversión automática de archivos pesados (MarkItDown)

Cuando el usuario adjunta o referencia un archivo en un formato **convertible a Markdown** —especialmente si es **pesado** (>500 KB o >5 páginas / >20 slides)— **convertirlo primero a `.md` con MarkItDown y leer el `.md` resultante** en vez de leer el binario directo. Reduce drásticamente el contexto consumido y evita los límites de paginación de PDFs.

**Formatos cubiertos por MarkItDown:** PDF · DOCX · PPTX · HTML · EPUB · JSON · XML · ZIP · imágenes (OCR) · audio (Whisper).

**Cuándo NO convertir (leer directo):**
- Archivos ya en texto plano (.md, .txt, .py, .ts, .json chico, etc.).
- Binarios muy chicos donde la paginación nativa alcanza (PDF de 1-3 páginas, DOCX corto).
- Cuando el usuario explícitamente pide leer el binario tal cual.

**Cómo:** binario disponible globalmente como `markitdown` (instalado vía pipx con Python 3.12, extras `[all]`).

```bash
# Patrón estándar
markitdown "/ruta/al/archivo.pdf" -o "/tmp/markitdown-cache/archivo.md"
```

**Convención de cache:** guardar la salida en `/tmp/markitdown-cache/<nombre>.md` (no contaminar `~/Downloads` ni el repo). Crear el dir con `mkdir -p` si no existe. Si el mismo archivo ya se convirtió en la sesión, reutilizar el `.md` sin reconvertir.

**Repo y referencia:** clon completo en `_core/tools/markitdown/` (Microsoft, MIT). Consultar el README de ese directorio para nuevos plugins o opciones avanzadas.

### Excepciones explícitas: spreadsheets y CSV

**NO usar MarkItDown para `.xlsx` / `.xls`.** Dos razones:
1. La "compresión" es pobre (~2× típico vs ~50-70× en PDF) porque un XLSX ya es texto comprimido.
2. **Se pierden las fórmulas** — solo quedan los valores calculados. Para los Excels operativos de los clientes (cálculo de pago a choferes, reportes de facturación, calculadoras de tarifas, etc.) la **lógica vive en las fórmulas**, no en los números. Además, los headers se rompen cuando hay celdas mergeadas en la fila 1 (patrón común en Excels armados por pymes).

**Qué usar en su lugar:**
- **Por defecto:** la skill `anthropic-skills:xlsx`. Lee fórmulas y valores, respeta merges, trabaja por hoja.
- **Si la skill no alcanza:** mini-script con `openpyxl` que extraiga fórmulas (`data_only=False`) y valores (`data_only=True`) lado a lado, hoja por hoja.

**NO usar MarkItDown para `.csv`.** Ya es texto plano y tabular. Markitdown no agrega valor.
- Si es chico (<2.000 líneas): leer con `Read`.
- Si es grande: herramientas tabulares (`head`, `awk`, mini-script con pandas) según la pregunta concreta.

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
├── CLAUDE.md              # Este archivo — contexto principal, siempre cargado
├── README.md              # Visión general del workspace
├── shell-aliases.md       # Alias bash para operaciones comunes
├── .gitignore             # Archivos excluidos del tracking
│
├── .claude/
│   ├── commands/          # Comandos que Claude puede ejecutar
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
| `contexto/`      | Quién es el usuario, su rol, prioridades actuales, estado del workspace. **Cargado automáticamente en cada sesión.** |
| `salidas/`       | Herramientas internas activas de la agencia (endpoints, bots, experimentos).                 |

---

## Skills de Cliente

Skills para gestionar el ciclo de vida completo de clientes. Se invocan con `/nombre-skill` o describiéndole la acción a Claude.

| Skill | Trigger | Qué hace |
|-------|---------|----------|
| `/cliente-nuevo` | "crear cliente", "nuevo cliente", "onboarding X" | Crea `clients/XXX_Nombre/` desde `_template`, completa `CLIENT_INFO.md`, registra en CLAUDE.md |
| `/cliente-avance` | "avancé en X", "actualizar cliente X", "registrar progreso" | Crea/edita archivos en la carpeta del cliente según la fase; actualiza `CLIENT_INFO.md` y CLAUDE.md |
| `/cliente-upsell` | "upsell para X", "nueva oportunidad con X" | Documenta el upsell en `ops/04_upsells/` y actualiza el cliente |
| `/cliente-estado` | "estado de X", "status de X", "qué tenemos con X" | Lee todos los archivos del cliente y genera un briefing completo |
| `/cliente-sync` | automático al final de cada skill, o "sincronizar X" | Escanea outputs nuevos, actualiza `CLIENT_INFO.md` y CLAUDE.md, reporta solo qué cambió |
| `/generar-system-prompt` | "crear system prompt", "generar prompt para el agente de X", "escribir instrucciones para el bot" | Genera un system prompt completo optimizado para n8n, listo para copiar y pegar |
| `/iterar-prompt` | "integrar esto al prompt", "actualizar prompt con...", "resultados del testing", "corregir el prompt", "ajustes post-testing", "el cliente mandó correcciones" | Integra nueva información a un prompt existente (Modo A) o aplica correcciones post-testing (Modo B). Siempre versiona antes de modificar y actualiza la guía de testing. |

## Skills de Workflows y Automatización

| Skill | Trigger | Qué hace |
|-------|---------|----------|
| `/reporte-semanal-email` | "crear reporte semanal", "workflow que mande métricas por email", "resumen automático de conversaciones", "análisis semanal", "dashboard por correo", "reporte periódico para el cliente" | Construye un workflow n8n completo para reportes periódicos con envío por email. Incorpora arquitectura híbrida JS+LLM, determinismo (temperature=0), listas cerradas, HTML email-safe. Guarda en `clients/[XXX]/03_workflows/`. |

## Skills de Documentación Técnica

| Skill | Trigger | Qué hace |
|-------|---------|----------|
| `/generar-uml` | "generar UML", "documentar arquitectura", "crear diagramas del proyecto", "documentar para handoff", "UML de X cliente" | Escanea archivos del proyecto (workflows n8n, prompts, schemas, docs) y genera documentación UML en Mermaid: Componentes + Secuencia obligatorios, Actividad/Estado/Despliegue opcionales. Output: `clients/[XXX]/06_docs/uml-handoff-YYYY-MM-DD.md`. |
| `/auditoria-airtable-cliente` | "auditar el Airtable de X", "el cliente reportó que el linkeo está roto", "preparar reunión sobre la base de datos", "revisar inconsistencias del Airtable", "detectar drift entre schema documentado y base real" | **Requiere ultracode.** Workflow multi-agente (7 dimensiones adversariales en paralelo: primary fields, linked records, data quality, schema-vs-docs, tool-contract, reverse-links, vistas) sobre un snapshot local de la base Airtable del cliente. Produce 3 entregables: reporte de inconsistencias rankeadas P0/P1/P2 con fixes `curl --dry-run` listos (`06_docs/airtable-auditoria-YYYY-MM-DD.md`), guía operativa para quien edita la base (`06_docs/airtable-guia-*-YYYY-MM-DD.md`), y diagrama Mermaid (`erDiagram`) del schema real listo para pegar en Figma/FigJam (`salidas/diagramas/*.mmd`, sin fences — paste-to-diagram directo). Nunca aplica cambios en la base viva. Validado en SYS 2026-07-01 (65 findings únicos, 7 P0 silenciosos en producción). |

## Skills de Prospección

| Skill | Trigger | Qué hace |
|-------|---------|----------|
| `/lead-generator` | "generá leads", "necesito clientes potenciales", "buscá negocios en [zona]", "armá una lista de [nicho]", "prospectame [categoría]" | Scraping de Google Maps via Apify MCP → filtrado por calidad → priorización → CSV listo para CRM. Requiere MCP de Apify conectado. |

## Skills de Agente Etapa 2 (Airtable + Supabase + ManyChat + n8n)

Suite de 15 skills + 1 SOP que cubre el ciclo completo de un agente conversacional productivo. Validados en SYS. Stack target: Airtable (RAG/catálogo) + Supabase (memoria + observabilidad) + ManyChat (canales IG/WA/FB) + n8n (orquestación) + OpenAI (gpt-4o).

**Cimiento metodológico:** `_core/standards/loop-plan-implement-smoke-iterate.md` (SOP-1) — Plan → Implement → Smoke → Iterate, con plantillas y trampas recurrentes.

### Lote 1 — ALTA (flujo core Etapa 2)

| Skill | Trigger | Qué hace |
|-------|---------|----------|
| `/bootstrap-agente-etapa-2` | "arrancar Etapa 2 para X", "pasar X a producción", "iniciar Etapa 2 cliente", "bootstrap del cliente X" | Andamiaje completo: Plan Maestro + 8 planes tácticos + runbook stub + credentials templates gitignored + architecture doc stub |
| `/generar-workflow-agente-n8n` | "generar workflow main para X", "crear el agente principal de X", "armar workflow v0.1 del agente" | Main workflow v0.1 (webhook → normalize → AI Agent + Postgres Chat Memory → respond), SIN tools |
| `/generar-subworkflows-tools-n8n` | "generar las tools del agente X", "crear sub-workflows tools", "armar los JSONs de las tools", "F4 del cliente X" | N sub-workflows tools siguiendo el patrón Trigger → Validate → Airtable → Format → Log → Return + doc tools-spec |
| `/integrar-tools-al-main-fromai` | "integrar tools al main", "armar v0.2 del agente X", "conectar las herramientas al agente principal", "F5 cliente X" | v0.2 con toolWorkflow + `$fromAI()` cableado. Evita TODOS los bugs descubiertos en SYS (schema strict, sintaxis $fromAI, types) |
| `/smoke-test-agente-webhook` | "smoke test del agente X", "probar el agente en producción", "diagnóstico rápido del webhook" | Script Python E2E contra webhook + evaluación con LLM-as-judge gpt-4o-mini + reporte |
| `/inspector-bugs-toolworkflow-n8n` | "el agente no responde", "tool no se invoca", "schema error en n8n", "diagnosticar bugs del agente X" | Inspecciona via MCP n8n + detecta los 8 bugs típicos descubiertos en SYS + reporta fix exacto |

### Lote 2 — MEDIA (infra, RAG, ops)

| Skill | Trigger | Qué hace |
|-------|---------|----------|
| `/setup-supabase-memoria-agente` | "setup Supabase para X", "configurar memoria del agente X", "armar la base de Postgres para X", "F2 cliente X" | SQL schema (4 tablas + 3 vistas + función upsert), guía proyecto sa-east-1 free tier, credentials gitignored con Session Pooler + Ignore SSL pre-cocinados |
| `/migrar-excel-a-airtable-rag` | "el cliente mandó el Excel", "migrar el catálogo a Airtable", "re-alinear el proyecto con el catálogo real", "F1 cliente X con su xlsx" | Parsea Excel cliente → CSVs Airtable por tabla + README import + detección de divergencias vs asunciones del Plan Maestro |
| `/generar-doc-fromai-tools-manual` | "doc de config $fromAI", "guía manual de tools", "doc para Edgardo de la config", "armar guía para reconfigurar tools manualmente" | Doc `f5-tools-fromai-config.md` como source-of-truth para reconfig manual post re-import (limitación n8n) |
| `/generar-runbook-agente` | "armar runbook del agente X", "runbook para X", "guía de troubleshooting del agente", "doc de soporte producción cliente X" | Runbook operativo: SLAs P1-P3, diagnóstico rápido, incidentes comunes, queries SQL, decisiones arquitectónicas, lecciones aprendidas |
| `/comparador-real-vs-config-toolworkflow` | "comparar config real vs esperada", "detectar drift", "qué cambió en el agente", "validar que la config esté como dice el doc" | Detecta drift entre lo REAL en n8n y lo ESPERADO según docs locales por tool/field con ✓/✗ |

### Lote 3 — BAJA (soportes y stubs)

| Skill | Trigger | Qué hace |
|-------|---------|----------|
| `/generar-architecture-doc` | "armar architecture doc de X", "documentar arquitectura X", "doc de arquitectura para handoff", "F0/F1 architecture cliente X" | Doc `architecture-v2.md`: diagrama ASCII + componentes + integraciones + 14 decisiones críticas + capacidad + riesgos |
| `/generar-testing-guide-stub` | "armar testing guide de X", "stub de testing para X", "casos de prueba para el agente X", "F7 testing cliente X" | Stub testing-guide: ~18 casos simples + ~16 flujos multi-turno cubriendo tool calling, memoria, NOT_FOUND, multi-canal, reglas operativas |
| `/sync-status-cliente-3-docs` | "actualizar status de X", "sincronizar 3 docs de X", "marcar avance en F5 de X en todos lados", "marcar X como GO-LIVE" | Sync atómico de status en CLIENT_INFO + CLAUDE.md raíz + contexto/datos-actuales (sin esperar commit) |
| `/generar-csvs-airtable-batch` | "generar CSVs para Airtable", "armar los CSV de import", "necesito los CSVs para importar a la base de X", "F1 sin Excel real, solo schema" | CSVs stub schema-first con seeds estándar interno (cuando no hay Excel todavía). Reemplazado por `/migrar-excel-a-airtable-rag` cuando llega el Excel |

### Mapa flujo Plan Maestro → Skills

```
F0 (bootstrap)  ──► bootstrap-agente-etapa-2 + generar-architecture-doc
F1 (Airtable)   ──► migrar-excel-a-airtable-rag (con Excel) | generar-csvs-airtable-batch (sin Excel)
F2 (Supabase)   ──► setup-supabase-memoria-agente
F3 (memoria)    ──► generar-workflow-agente-n8n
F4 (tools)      ──► generar-subworkflows-tools-n8n
F5 (integrar)   ──► integrar-tools-al-main-fromai → generar-doc-fromai-tools-manual → inspector-bugs (si rompe)
F7 (testing)    ──► generar-testing-guide-stub → smoke-test-agente-webhook → inspector-bugs / comparador-real
F8 (producción) ──► generar-runbook-agente + sync-status-cliente-3-docs
```

---

## Comandos

### /crear-plan [pedido]

**Propósito:** Crear un plan de implementación detallado antes de hacer cambios.

Usalo cuando se agrega nueva funcionalidad, comandos, scripts, o se hacen cambios estructurales. Produce un documento de plan en `planes/` que captura contexto, justificación y tareas paso a paso.

Ejemplo: `/crear-plan agregar agente de seguimiento para clientes dental`

### /implementar [ruta-al-plan]

**Propósito:** Ejecutar un plan creado por /crear-plan.

Lee el plan, ejecuta cada paso en orden, valida el trabajo y actualiza el estado del plan.

Ejemplo: `/implementar planes/agente-dental-follow-up-2026-04-10.md`

### /email-html-generator [cliente]

**Propósito:** Generar un HTML elegante, responsivo y email-safe con branding la agencia a partir del JSON de un reporte y el HTML actual del nodo "Send a message" de n8n.

Recibe el JSON con datos (cualquier estructura) y el HTML viejo del nodo Gmail/SMTP. Devuelve un nuevo HTML mejorado, listo para copiar y pegar en n8n. Preserva las variables de interpolación n8n (`{{ $json.X }}`).

**Tema auto-detectado** según el contexto: `duolingo` (agentes/engagement), `corporate` (finanzas B2B), `minimal` (dental/médico/legal), `warm` (CRM/retail). Override opcional con `tema:X`. En todos los casos aplica branding propio: header `#0d0a1f`, accent bar `#7c3aed`, footer oscuro con tagline en `#a78bfa`.

Ejemplo: `/email-html-generator cliente:Narvaja`
Override de tema: `/email-html-generator tema:minimal cliente:Sonrisas`

---

## Instrucción Crítica: Mantener Este Archivo

**Siempre que Claude haga cambios en el workspace, DEBE considerar si CLAUDE.md necesita actualizarse.**

Después de cualquier cambio — agregar comandos, clientes, scripts, flujos de trabajo, o modificar la estructura — preguntarse:

1. ¿Este cambio agrega nueva funcionalidad que los usuarios necesitan conocer?
2. ¿Modifica la estructura del workspace documentada arriba?
3. ¿Debe listarse un nuevo comando?
4. ¿Se agregó un nuevo cliente en `clients/`?

Si la respuesta es sí a cualquiera, actualizar las secciones relevantes. Este archivo debe siempre reflejar el estado actual del workspace.

---

## Flujo de Trabajo de Sesión

1. **Inicio**: Claude carga automáticamente `contexto/`. Consulta `contexto/datos-actuales.md` si necesitas contexto fresco
2. **Trabajo**: Usar comandos o dirigir a Claude con tareas
3. **Planificar cambios**: Usar `/crear-plan` antes de adiciones significativas
4. **Ejecutar**: Usar `/implementar` para ejecutar los planes
5. **Mantener**: Al finalizar, `/cliente-sync` actualiza automáticamente CLAUDE.md, `contexto/` y hace commits

---

## Convenciones de Nomenclatura

Ver `_core/standards/naming_conventions.md` para el diccionario completo. Resumen:

| Tipo | Formato | Ejemplo |
|------|---------|---------|
| Cliente | `[XXX]_Nombre` | IMP_ImportadoresConectados |
| Workflow n8n | `WF_[NICHE]_[FUNCION]_v[N]` | WF_DENTAL_LeadCapture_v1 |
| Agente IA | `AGT_[FUNCION]_v[N]` | AGT_Booking_v2 |
| Prompt | `PRM_[ROL]_[NICHE]_v[N]` | PRM_QualificationBot_Dental_v2 |
| Módulo | `MOD_[INTEGRACION]_[FUNCION]` | MOD_WA_SendMessage |

Nichos válidos: `DENTAL` | `REALESTATE` | `AGENCY` | `AUTO` | `GENERIC`

---

## Clientes Activos

### IMP — Importadores Conectados / Diego Labores (`clients/IMP_ImportadoresConectados/`)

Agente de ventas conversacional para @diegolabores (negocio: Importadores Conectados — cursos y mentoría de importaciones). Responde DMs en Instagram, WhatsApp y Facebook usando n8n AI Agent con gpt-4.1-mini. CRM en Airtable, notificaciones al equipo por Telegram.

**Contactos:** Diego Labores (dueño) · Georgina Paradiso / Geor (secretaria)

**Stack:** ManyChat + WhatsApp Business API + n8n + Airtable + OpenAI gpt-4.1-mini + Telegram

**Archivos clave:**
- `03_workflows/flujo-n8n-agente-diegolabores.json` — Workflow de producción (IG + WhatsApp + Facebook)
- `03_workflows/flujo-n8n-telegram-test.json` — Workflow de prueba con Telegram
- `04_agents/agente-diegolabores-system-prompt.md` — System prompt v1.12 (testing v7 completo 46/46 — MICROVALOR_NO_EMPIEZA solo sin producto declarado, LEAD_CON_INTERÉS_DECLARADO sin re-diagnóstico post-IC, METODO NO-disparadores, MICROVALOR_MIEDO_PLATA/ROMPER_MIEDO, excepción anti-cadena)
- `04_agents/agente-diegolabores-system-prompt-v1.9.md` — Backup v1.9
- `04_agents/agente-diegolabores-system-prompt-v1.8.md` — Backup v1.8
- `04_agents/agente-diegolabores-system-prompt-v1.6.md` — Backup v1.6
- `04_agents/agente-diegolabores-system-prompt-v1.7.md` — Backup v1.7
- `04_agents/agente-diegolabores-system-prompt-v1.5.md` — Backup v1.5
- `04_agents/agente-diegolabores-system-prompt-v1.4.md` — Backup v1.4 (rol Diego primera persona, antes de re-testing)
- `04_agents/agente-diegolabores-system-prompt-v1.3.md` — Backup v1.3 (versión Setter previa al cambio de rol)
- `04_agents/agente-diegolabores-system-prompt-v1.2.md` — Backup v1.2
- `05_crm/airtable-leads-db-schema.md` — Esquema tabla Leads en Airtable
- `06_docs/brand-bible.md` — **Fuente de verdad**: productos, precios, avatar, tono. ⚠️ **Desactualizado y así queda** (actualización descartada el 2026-08-04): el precio real de IC es USD 697, la Mentoría 1:1 es variable (no USD 2.000 fijo) y falta el producto Asesoría 1:1 con Diego (USD 100/1h). Leerlo con esa salvedad.
- `06_docs/audios-catalogo.md` — Catálogo de audios (4 grabados + 15 que nunca se grabaron). ❌ **Línea descartada el 2026-08-04** — queda como referencia, no como plan de grabación.
- `07_testing/testing-guide-v1.md` — Guía de testing v1 sobre prompt v1.3 (10 flujos + 12 casos simples)
- `07_testing/testing-guide-v2.md` — Guía de testing v2 sobre prompt v1.4 (identidad Diego primera persona + apertura por origen + audio METODO_INICIO_PROGRAMA)
- `07_testing/testing-guide-v3.md` — Guía de re-test v3 sobre prompt v1.5 (solo casos que fallaron o salieron parciales en v2)
- `07_testing/testing-guide-v4.md` — Guía de re-test v4 sobre prompt v1.6 (caso #3, #6, #27 + Flujo 13 turno 4)
- `07_testing/testing-guide-v5.md` — Guía de testing v5 sobre prompt v1.7 (precio 697, tono simple, 5 microvalores por dolor)
- `07_testing/testing-guide-v6.md` — Guía de testing v6 sobre prompt v1.8 (resultados: fix #2 MIEDO_PLATA/ROMPER_MIEDO OK, anti-cadena bloqueaba microvalores, METODO sin idea aún disparaba)
- `07_testing/testing-guide-v7.md` — Guía de re-test v7 sobre prompt v1.12 (16 casos: METODO NO-disparadores, distinción miedo, excepción anti-cadena, lead interés declarado) — ✅ 46/46 true

**Variables n8n:** `AIRTABLE_BASE_ID_DIEGOLABORES`, `AIRTABLE_TABLE_LEADS`, `MANYCHAT_API_KEY`, `TELEGRAM_CHAT_ID_EQUIPO`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_ACCESS_TOKEN`, **`ORIGEN`** (`form` o `directo`, nuevo en v1.4)

**Pendientes: ❌ ninguno — todos descartados el 2026-08-04.** Se abandona la línea de audios completa y
el ajuste del brand bible. El agente queda como está, funcionando con texto.

<details>
<summary>Cola histórica descartada (referencia)</summary>

- ~~Diego: grabar los 15 audios faltantes (10 originales + 5 microvalores)~~
- ~~Implementar el parser de marcadores `[AUDIO:NOMBRE]` en n8n~~
- ~~Crear los flows en ManyChat (uno por audio del catálogo)~~
- ~~Mapping `audio_id → manychat_flow_id` en n8n~~
- ~~Cargar la variable `{{ORIGEN}}` en el webhook~~
- ~~Actualizar el brand bible (precio IC USD 697, mentoría 1:1 variable, Asesoría 1:1 USD 100/h)~~

</details>

> Nota: carpeta física renombrada de `IMP_DiegoLabores` a `IMP_ImportadoresConectados` el 2026-04-17.

---

### SNR — Sonrisas (`clients/SNR_Sonrisas/`)

Automatización del reporte de facturación mensual para clínica dental Sonrisas.

> **Estado al 2026-08-04 — SNR sin pendientes abiertos.** Se descartó toda la cola: la verificación
> del informe de gestión de turnos, el bootstrap/deploy de la clasificación mes-aware, la corrección
> del informe de no confirmados/atendidos, el informe de eficiencia de doctores (estaba en pausa por
> datos defectuosos de Dentalink) y la hoja de ruta + presupuesto de la plataforma centralizada.
> Lo que está en producción sigue corriendo; no hay trabajo planificado encima.
> ⚠️ La página de Notion *Estado de Proyectos* del cliente todavía refleja la cola vieja.

> **🆕 Mantenimiento — decisión 13-ago-2026.** la agencia deja de hacer el mantenimiento como hasta ahora; se le plantea a Cecilia una propuesta **A/B** (A: vía la agencia B2B US$500/mes con persona dedicada; B: traspaso a la comunidad US$250–350/mes con contrato que desliga a la agencia — Camilo no es opción). Actual ~US$292/mes. Reunión `06_docs/reunion-cecilia-2026-08-13.md`, propuesta `06_docs/propuesta-mantenimiento-2026-08.md`, marco `ops/03_mantenimientos/esquema-opciones-mantenimiento-2026-08-13.md`. Pieza web https://propuesta-sonrisas.vercel.app (pública por URL, `noindex`; fuente `06_docs/propuesta-web/`). Pendiente: enviar la propuesta. Nota: la transición a Camilo (`planes/plan-transicion-camilo-2026-07-07.md`) daba SNR como "sin arrancar" — este esquema A/B la reemplaza para Sonrisas.

**✅ v3.6 Reporte + v6 Correos en PRODUCCIÓN (2026-06-15) — smoke tests OK:** Mayo $4.219.997 (coincide histórico exacto). Junio $943.280 (recupera $35.060 que v3.5 perdía en códigos no mapeados PE1000/PE1005/OR127/OA049/RD008). Cierre formal del incidente PERIODONCIA Mayo. La causa raíz REAL del incidente (descubierta el 2026-06-15) NO fue drift mes-aware como diagnostiqué inicialmente — fueron 3 bugs en cadena: (1) Upsert Histórico tabla sin matching column → duplicaba filas 13x desde la migración a Data Tables del 2026-06-06 (50.422 vs 3920 reales); (2) fan-out implícito en Get Histórico tabla — `selectMany.ts` de n8n ejecuta el Get UNA VEZ POR INPUT ITEM, multiplicando RAM N×3920 → SIGKILL del worker (mensaje engañoso "may have run out of memory"); (3) CODIGO_A_CATEGORIA del v3.5 desactualizado, no mapeaba 5 códigos nuevos que Cecilia agregó. Aún así el sistema mes-aware se mantiene como mejora estructural para drift futuro. Fixes aplicados en v3.6/v6: matching column `key` en Upsert, `executeOnce: true` en Get, Data Table purgada, CODIGOS_AMBIGUOS + resolverAmbiguo (réplica fiel del v3.5 viejo), snapshot v2 con TABLA_MES_AWARE embebida, `Filtro de campos` del Correos propaga `Fecha_de_recepcion_del_pago`. Postmortem: `clients/SNR_Sonrisas/06_docs/incidente-periodoncia-mayo-2026-06-14.md`. Runbook operativo para Cecilia: `clients/SNR_Sonrisas/06_docs/runbook-actualizacion-codigos-mes.md`.

**🆕 Clasificación mes-aware — ❌ bootstrap + deploy descartados el 2026-08-04 (queda el registro del rediseño, 2026-06-14):** se rediseñó el sistema de clasificación de códigos para resolver el incidente **PERIODONCIA Mayo = $0** del reporte de primera semana de junio. Los nodos Filtro/Categoria/Clase (3 en Reporte + 6 en Correos) clasificaban TODAS las filas con UN solo juego de códigos hardcodeado del último xlsx de Cecilia, incluso las filas de mes anterior con códigos viejos. Solución: snapshot **v1 (flat) → v2 (mes-aware)** con `codigos[X].meses[YYYY-MM]`; workflows nuevos v3.6 (Reporte) + v6 (Correos) con `TABLA_MES_AWARE` embebida + función `lookupMesAware(codigo, mes_key)` (mes_key derivado de `_fechaISO.substring(0,7)`); fallback hacia atrás → adelante → `_error`. Script `scripts/utilities/update-sonrisas-nodes.py` refactorizado a mes-aware con flag `--mes YYYY-MM`, ventana pruning 6 meses, NO aborta ante cambio cat/clase entre meses (en lugar de eso reporta en bloque "REVISIÓN REQUERIDA" para inspección humana). 2 scripts nuevos: `scripts/utilities/migrate-snapshot-mesaware.py` (one-shot v1→v2 con backup automático) + `scripts/utilities/verify-sonrisas-codigos-mesaware.py` (10 casos golden). Docs: `06_docs/incidente-periodoncia-mayo-2026-06-14.md` (postmortem, NO comunicado al cliente — decisión la agencia), `06_docs/cambios-flujo-facturacion-mesaware-2026-06-14.md` (cambios técnicos completos), `06_docs/runbook-actualizacion-codigos-mes.md` (8 pasos operativos para el operador). Plan completo: `/Users/camilo/.claude/plans/en-base-al-ltimo-velvety-starlight.md`. **Bloqueante deploy:** conseguir xlsx de **mayo + junio** archivados de Cecilia (decisión cerrada con operador) para que el primer reporte post-deploy ya corrija PERIODONCIA Mayo retroactivamente. Pasos: (1) `migrate-snapshot-mesaware.py` (idempotente, backup en `_snapshots/codigos-historico.v1-backup.json`); (2) `update-sonrisas-nodes.py --mes 2026-05 <xlsx_mayo>` → debería emitir bloque "REVISIÓN REQUERIDA" listando los códigos PERIODONCIA que cambiaron entre mayo y junio (confirmación causa raíz); (3) `update-sonrisas-nodes.py --mes 2026-06 <xlsx_junio>` re-corrida limpia; (4) crear `sonrisas-reporte-facturacion-v3.6.json` y `sonrisas-correos-reportes-facturacion-v6.json` pegando los 3 bloques JS en los 9 nodos (3 en v3.6 + 6 en v6); (5) smoke test manual + verifier; (6) cutover sábado.

**Archivos clave:**
- `03_workflows/sonrisas-registro-inasistencias-v2.json` — Workflow n8n de facturación
- `03_workflows/sonrisas-reporte-facturacion-v3.5.json` — **Workflow producción reporte facturación** (v3.5: fix permanente reconciliación Mensual vs Semanal + filtro RAM). Causa real: semana puente S14 (borde marzo/abril) se procesa en dos cargas y el write semanal overwrite deja solo la porción de la última ventana → pierde marzo ($14.910 Paso Molino AJUSTE; ~$206.920 en las 9 celdas S14). Fix: cadena `Keyear Histórico → Upsert Histórico (appendOrUpdate por _key) → Get Histórico → Filtrar Histórico 2M` → acumula en `Histórico` de-duplicado pero procesa solo mes corriente + mes anterior para no saturar RAM en instancias de 2 GB. **Setup:** crear pestaña `Histórico` (ver `06_docs/cambios-flujo-facturacion-v3.4-reconciliacion-2026-05-25.md`). Hereda v3.4. **Filtro de memoria — resuelto (2026-05-26):** `Filtrar Histórico 2M` (por mes calendario) re-rompía S14; se **deshabilitó** y el reporte procesa el año completo sin OOM (Histórico de 8 columnas entra en 2 GB) → reconciliación garantizada + S14 sano. Nodo conservado deshabilitado por si crece el dataset (doc §9). **Quota API — resuelto (2026-06-01):** con >16.000 filas en `Histórico`, el nodo `Get Histórico` excedía quota de lecturas paginadas. Solución: tab `Histórico_2M` en el Google Sheet con QUERY server-side; el nodo `Get Histórico` ahora lee de `Histórico_2M`. Fórmula en A1 de `Histórico_2M`: `=QUERY(Histórico!A:J,"SELECT * WHERE Col3 = '"&INDEX({"Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"},MONTH(TODAY()))&"' OR Col3 = '"&INDEX({"Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"},IF(MONTH(TODAY())=1,12,MONTH(TODAY())-1))&"'",1)` — usar `INDEX` con array español (no `TEXT(...,"MMMM")` que devuelve inglés). `Col3` = `Mes de recepción del pago` en el tab real (no Col5 como indica el schema spec). **Drift de códigos + migración a Data Tables — resuelto (2026-06-06):** dos problemas resueltos en cadena. (1) **Drift de códigos**: `Histórico_2M` traía filas del mes anterior con códigos retirados del xlsx vigente → `Filtro1` los marca `_error: true` → reporte aborta todo el mes. Fix: el script `update-sonrisas-nodes.py` acumula códigos en `_snapshots/codigos-historico.json` (unión `xlsx_actual ∪ snapshot`, pruning automático a >2 meses); `--no-snapshot` para debug; aborta ante conflictos categoría/clase snapshot vs xlsx. (2) **Saturación Get Histórico + latencia QUERY**: resuelto vía **migración de `Upsert Histórico` + `Get Histórico` (Google Sheets) a Data Tables nativas n8n** (`Upsert Histórico tabla` + `Get Histórico tabla`, tabla `SNR | Histórico Pagos` id `tpb3Go26RuhK5cuN`). Cero quota API, cero latencia recompute, el filtrado a "mes corriente + mes anterior" vive en el `filters.conditions` del Get sobre `Mes_de_recepcion_del_pago`. **Cambios colaterales en 3 nodos**: `Parsear y validar fecha`, `Filtro de campos`, `Filtro1` actualizados para los nombres snake_case de la Data Table (`Fecha_de_recepcion_del_pago`, `Codigo_Prestacion`, `Pagado_Prestacion`, etc.). `Filtro de campos` actúa como capa de normalización: lee los nombres nuevos del input y reescribe a los nombres viejos (`Código Prestación`, `Pagado Prestación`) para que el resto del flujo downstream no cambie. **Estado:** Aplicado en n8n vivo y sincronizado al repo (2026-06-06 PM, 45 nodos). Doc: `06_docs/cambios-flujo-facturacion-drift-codigos-2026-06-06.md`. **Correos migrado en cadena (2026-06-07):** `sonrisas-correos-reportes-facturacion-v5.json` ya lee de la Data Table `SNR | Histórico Pagos` (misma fuente que el Reporte) + códigos actualizados al snapshot + cálculo de `Semana` con fallback robusto Luxon↔string (la Data Table entrega campos `dateTime` como Luxon, no string)
- `03_workflows/sonrisas-reporte-facturacion-v3.4.json` — Backup v3.4 (endurecimiento: parseo robusto de fecha, abort ante fecha inválida, writes `appendOrUpdate`)
- `03_workflows/sonrisas-reporte-facturacion-v3.3.json` — Backup v3.3 (previo al fix de reconciliación)
- `03_workflows/sonrisas-reporte-facturacion-v3.2.json` — Versión anterior (v3.2: Filtro 326 códigos desde xlsx, Categoria por lookup código→Rubro, Clase ortodoncia actualizada, abort en código desconocido)
- `03_workflows/sonrisas-reporte-facturacion-v3.1.json` — Versión anterior (v3.1: ALINEADORES como categoría)
- `03_workflows/sonrisas-reporte-facturacion-v5.json` — Versión anterior (v5: CLASES por Rubro, OTRO=0, escritura aditiva)
- `03_workflows/sonrisas-reporte-facturacion-v4.json` — Versión anterior (v4: rediseño radical)
- `06_docs/sonrisas-metricas-inasistencias.md` — Documentación del proceso
- `06_docs/cambios-flujo-facturacion-2026-04-18.md` — Cambios v3
- `06_docs/cambios-flujo-facturacion-v4-2026-04-18.md` — Cambios v3 → v4 (mapeo de nodos, nuevo rango, verificación)
- `03_workflows/sonrisas-correos-reportes-facturacion-v5.json` — **Workflow producción correos** diario + semanal + mensual (v5, 2026-06-07). Cambios vs v4: (a) las 2 lecturas Sheets `Get row(s) in sheet` × 2 reemplazadas por `Get Histórico tabla` (Data Table `SNR | Histórico Pagos` id `tpb3Go26RuhK5cuN`), filtrando server-side por `Mes_de_recepcion_del_pago` = mes corriente OR mes anterior (misma fuente que Reporte v3.5); (b) `Filtro de campos` × 2 actualizados a leer nombres snake_case del input + assignment `Pagado Prestación` ← `Pagado_Prestacion` + cálculo `Semana` robusto que detecta Luxon DateTime vs string (la Data Table entrega `dateTime` como Luxon); (c) `Filtro`, `Filtro3`, `Categoria`, `Categoria1`, `Clase`, `Clase1` regenerados con los 343 códigos del snapshot vigente (`_snapshots/codigos-historico.json`); (d) `Filtro` y `Filtro3` mantienen `throw new Error` (Correos no tiene IF downstream — el throw dispara `errorWorkflow OBkUyb8fuo30DzA9`); (e) Subject de nodos Gmail `Semanal` y `la agencia (pruebas)` ahora usa `${{ $json.totalGeneral.format('es') }}` para mostrar miles con separador. Trigger Diario intacto (HTTP Pagos2, no usa Sheets ni Data Table). Credencial Sheets remanente: `wPnIRnRcU44L0ZWl`. Generador: `/tmp/migrate_correos.py` (one-shot, no committeado)
- `03_workflows/sonrisas-correos-reportes-facturacion-v4.json` — Backup v4 (las 2 lecturas leen el tab `Histórico` en vez de `Facturación` → emails Semanal/Mensual acotan al período actual sobre datos completos; único cambio vs v3). Requiere `Histórico` poblado por el Reporte v3.5 y columna `Fecha` en `yyyy-mm-dd`. Migración: `scripts/utilities/fix-sonrisas-correos-historico.py`
- `03_workflows/sonrisas-correos-reportes-facturacion-v3.json` — Backup v3 (lee `Facturación`/Ingreso datos directo)
- `03_workflows/sonrisas-correos-reportes-facturacion-v2.json` — Versión anterior (v2: ALINEADORES en display HTML)
- `03_workflows/sonrisas-correos-reportes-facturacion-v1.json` — Versión anterior (v1: sin ALINEADORES)
- `03_workflows/sonrisas-datos-agregados-v2.json` — Workflow datos agregados: integración API Dentalink para crear/buscar pacientes, extracción de datos vía OpenAI
- `03_workflows/sonrisas-gestion-turnos-semanal-v1.json` — Informe semanal de gestión de turnos por sucursal (Agendadas {7,28,8,19,14,2} / Atendidos 2 / No asistió 8 + % Atendidos + % Inasistencia). API Dentalink con paginación `links.next`, sábado 18h Montevideo → Google Sheets "Métricas de Pacientes 2026" (pestañas `% Asistencia N`, upsert por semana, vía Loop Over Items). ❌ **Verificación descartada el 2026-08-04** (quedó sin comprobar el mapeo sucursal→pestaña `substring(4,5)` y la TZ del trigger — asumir que puede estar mal si alguien retoma). La API solo expone estado actual → NO incluye % sobre confirmadas/notificados WA (requeriría CSV de historial de estados)
- `06_docs/sonrisas-gestion-turnos-metricas.md` — Doc del informe de gestión de turnos (métricas, mapeo de estados, arquitectura, setup, verificación, límite de la API)
- `06_docs/guia-fechas-facturacion-2026-05-24.md` — Guía de implementación del rediseño de fechas (concepto "Mes objetivo", regla de carga de Cecilia, cambios por nodo en Recordatorio/Correos/Reporte, verificación). **Update 2026-06-07:** post-migración a Data Table, el nodo `lapso` del workflow `SNR | Recordatorio Ingreso Datos` ahora calcula `primerDia = sat.minus({ days: 6 })` (domingo de la última semana) en lugar de `mesObjetivo.toISODate()` (1° del mes objetivo). Cecilia carga solo la última semana cada sábado — el histórico de la Data Table cubre el resto vía `appendOrUpdate` idempotente por `_key`. `mesObjetivoNombre` / `mesObjetivoAnio` / `esFinalize` se conservan para los Correos.

**Verificar lógica de fechas:** `python3 scripts/utilities/verify-sonrisas-fechas.py` (simula cobertura "Mes objetivo" sobre un año; prueba 0 días perdidos).

**Auditar reconciliación Mensual vs Semanal:** `python3 scripts/utilities/verify-sonrisas-reconciliacion.py --csv <ingreso-datos.csv> --sucursal "Paso Molino" --clase AJUSTE` (replica la lógica sobre un CSV, lista filas que descuadran y simula el `update`).

**Actualizar códigos:** cuando se actualiza el Listado de Precios, ejecutar:
```bash
python3 scripts/utilities/update-sonrisas-nodes.py ~/Downloads/"Listado de Precios Completo.xlsx"
```

---

### SYS — Sistemas y Soluciones (`clients/SYS_SistemasYSoluciones/`)

Agente de calificación y asesoramiento para la industria gráfica. Atiende leads entrantes en WhatsApp, Instagram y Facebook; califica la necesidad del cliente, asesora sobre tecnologías de impresión, y deriva al representante comercial con notificación por mail.

**Estado:** Etapa 1 (testing Telegram, v1.7) COMPLETADO ✅. Etapa 2 (Producción ManyChat + tools reales + memoria) — Plan Maestro aprobado 2026-05-28. **LIVE en producción**: main v0.9 + 10 tools + **prompt v2.7** (deployado 2026-07-10) + `registrar_datos_lead` v2 (gate por teléfono) + `sys-tool-consultar-catalogo-v5.json` (fixes T-01/T-02/T-03/T-04/T-05/T-06 de la auditoría Airtable).

**🆕 Registro de leads gated por teléfono + notificar_lead registra en planilla + fix "papel fotográfico" — 2026-07-08/10 (LIVE):** disparado por accionable de la reunión Jimena+Edgardo del 2026-07-08 ("Registro de leads"). Diagnóstico: el prompt v2.5 ya describía el comportamiento deseado pero la implementación no lo hacía cumplir — el teléfono se pasaba por `$fromAI` (lo copiaba el LLM) en vez de salir determinístico de ManyChat, y `registrar_datos_lead-v1` registraba con solo el nombre sin exigir teléfono. **Fix (prompt v2.6, 2026-07-08):** (1) sub-workflow `sys-tool-registrar-datos-lead-v2.json` (preserva workflowId `v9HD7P2uroG4Ni3A`) — `Validate Input` resuelve el teléfono por coalesce `telefono_webhook` (determinístico, ManyChat) → `telefono` (agéntico, lo que el lead escribió); sin teléfono numérico válido devuelve `status: REJECTED, reason: telefono_invalido` y no escribe nada; (2) nodo tool `registrar_datos_lead` del main recableado: `telefono_webhook` determinístico desde `Normalize Payload.phone`, `telefono` solo por `$fromAI` cuando el lead lo escribe en el chat; (3) `Build User Message Context` agrega línea `Teléfono del lead: <número>` / `NO disponible` al `[CONTEXTO TURNO]`; (4) Regla operativa 26 reescrita con la matriz de decisión número×correo. Guía: `06_docs/guia-deploy-registro-leads-telefono-2026-07-08.md`. **Test en producción (10/7) reveló 2 gaps nuevos:** para el contacto de test, ManyChat manda `{{phone}}` de forma **intermitente e irresoluble** (confirmado por el cliente: el body de la solicitud externa a veces trae el número real, a veces el literal `{{phone}}` — no es arreglable del lado ManyChat); y el lead dijo "mi número es este" sin escribir dígitos → el agente aceptó eso, derivó con `notificar_lead` usando un teléfono fantasma, y **nunca llamó `registrar_datos_lead`** (las tools se trataron como sustitutas, no como acciones independientes). **Fix (prompt v2.7, 2026-07-10):** Regla 18 endurecida (frases tipo "el de WhatsApp"/"este" NO son un número, exigir dígitos escritos antes de derivar o registrar), Regla 26 con bloqueo duro (`Teléfono del lead: NO disponible` → no derivar NI registrar hasta conseguir el número) + pairing obligatorio (`notificar_lead` con teléfono válido dispara también `registrar_datos_lead` en el mismo turno), y REGLA CRÍTICA nueva en `notificar_lead` prohibiendo derivar con `{{phone}}`/no-numérico. Backups: `agente-sistemasysoluciones-system-prompt-v2.5.md` (nunca antes en repo — vivía solo en Google Docs) y `-v2.6.md`. **Red estructural (no solo prompt) — guía `06_docs/guia-notificar-lead-registra-en-planilla-2026-07-10.md`, ✅ APLICADA y LIVE (2026-07-09/10):** como confiar 100% en que el LLM llame ambas tools es frágil (ya falló una vez en producción), se implementó que el sub-workflow `notificar_lead` invoque también a `registrar_datos_lead` (Execute Sub-workflow, nodo nuevo `Registrar en planilla`) tras derivar — mismo gate/coalesce, así todo lead derivado con teléfono válido queda en la planilla sin depender del LLM. **Verificado en producción** con 2 conversaciones reales del 2026-07-10 (`wa_1253975717`, `wa_1531778764`): `notificar_lead` derivó y `registrar_datos_lead` se disparó en el mismo flujo (pairing OK), ambas filas en la planilla con `origen: derivacion` (huella del delta). **Hallazgo colateral:** `sys-tool-notificar-lead-v4.json` en repo tiene una conexión rota (nodo Gmail renombrado a `Gmail Send (emarti + marketing)` pero la conexión apunta al nombre viejo `Gmail Send (CM + cc info@)`) — el repo está desincronizado de lo vivo (que sí manda el mail bien); por eso el fix de notificar_lead se aplicó como delta/guía y NO como JSON completo para import. **✅ Housekeeping cerrado (2026-07-10):** `notificar_lead` vivo re-exportado y guardado como `03_workflows/sys-tool-notificar-lead-v5.json`. **🚨 Hallazgo importante al re-exportar — los workflowId documentados para SYS no coinciden con los reales:** el export post-fix tiene `id: M25w0GBLPgiHYJzw`, NO `QI1gO4dZ5vXXo7V3` como está documentado en repo (v4.json) y en todo el historial de este CLAUDE.md desde 2026-06-05. Mismo patrón puertas adentro: el nodo `Registrar en planilla` de este export apunta a `registrar_datos_lead` en `ETyWBXpUQelRTBA2` (cachedResultName `sys-tool-registrar-datos-lead-v2`), NO `v9HD7P2uroG4Ni3A` que es el ID que usé en toda esta sesión (v1/v2/v3.json) y que el usuario confirmó como funcionando (los fixes SÍ se aplicaron correctamente ahí, vía edición manual en la UI, no por import-by-ID). Las credenciales también difieren (Postgres `GSbtwALckB7A2BPZ` vs `cQLxF5deDtmo4HTV` documentado; Gmail `qS9Zx4CRuxN6P7Rz` vs `5R0ScEVqcfjKYanp`; ManyChat `M0esMwMcEknjNmSs` vs `UnA18VVz7bSrSUNX`), y el destino del mail de derivación es SOLO `marketing@sistemasysoluciones.com` (no `emarti@+marketing@` como se documentó en la mejora del 2026-06-23). **Hipótesis más probable:** la migración de infraestructura a cuentas del cliente (pendiente desde 2026-06-05, ver `06_docs/guia-migracion-infra-cliente-2026-06-05.md`) ocurrió en algún momento sin quedar registrada — un n8n nuevo bajo cuenta del cliente genera IDs de workflow y credenciales nuevos al importar. **Impacto:** cualquier guía histórica de SYS que diga "preserva workflowId X → import in-place" puede estar apuntando a un ID que ya no existe en el n8n vivo. No se corrigieron retroactivamente todas las menciones históricas (alcance grande, se prioriza no bloquear el cierre de esta sesión) — **recomendado: auditar los IDs reales de las ~10 tools de SYS antes de la próxima vez que se necesite hacer un import-in-place**, no asumir que el ID documentado es correcto sin confirmar primero en n8n. **☢️ Bug adicional encontrado en producción y resuelto (2026-07-10) — type mismatch en `IF lead existe?`:** al re-invocar `registrar_datos_lead` para un lead ya existente, n8n tiraba `Wrong type: '1531778764' is a number but was expecting a string`. Causa: Google Sheets devuelve `subscriber_id` como number cuando el valor es todo dígitos, pero el nodo `IF lead existe?` (heredado sin cambios desde v1) tenía el operator tipado `string` con `typeValidation: strict` → choca al comparar. No es un bug nuevo del fix del 08 — nunca se había ejercitado la rama UPDATE con un subscriber_id puramente numérico. Fix aplicado en vivo: operator `{type: "string", operation: "notEmpty"}` → `{type: "number", operation: "notEmpty", singleValue: true}`. Repo actualizado: `03_workflows/sys-tool-registrar-datos-lead-v3.json` (preserva workflowId `v9HD7P2uroG4Ni3A`; v2.json queda como referencia histórica). Documentado en `06_docs/guia-deploy-registro-leads-telefono-2026-07-08.md` §9 (errata post-deploy), incluye nota de riesgo latente: mismo patrón (`typeValidation: strict` + operator `string` sobre valor potencialmente numérico de Sheets/Airtable) no auditado todavía en el resto de los sub-workflows tools de SYS. **Fix "papel fotográfico" (2026-07-10, foldeado en v2.7):** un lead pidió imprimir sobre papel fotográfico y el agente recomendó una impresora láser — causa raíz confirmada por API: el token "papel" matcheaba el sustrato "Papel común" de la aplicación "Producción editorial" (que recomienda RISO/IDL Láser), y no existía ninguna aplicación de "papel fotográfico". Fix doble: (a) nueva fila en Airtable `Aplicaciones` (`recTKuMg6cekhMnhc`, creada por API) — "Papel fotográfico", sin Tecnologías recomendadas (deliberado — SyS no tiene equipo para eso), Sustratos típicos + Keywords cliente cargados; (b) como esa fila sola NO alcanza (la app "Producción editorial" sigue matcheando "papel" y devolviéndose en el mismo resultado), se agregó el dato fijo "Papel fotográfico / casas de fotos" en BASE DE CONOCIMIENTO del prompt v2.7 — prohíbe explícitamente recomendar láser/RISO para ese uso aunque la tool las devuelva. **Guía operativa para Edgardo reescrita** (`06_docs/airtable-guia-edgardo-2026-07-02.md`, revisión 2026-07-10) — contrastada contra el objetivo real de la reunión (que sea autoservicio, "úsenla y avisen si falta algo"): agrega sección "Cómo agregar o editar" (mecánica básica que no sabían), sección Aplicaciones enriquecida con "cómo corregir una recomendación equivocada" (usa el caso papel fotográfico como ejemplo), tabla nueva "Si el agente responde algo mal, ¿dónde lo arreglo?" (síntoma → tabla), y se sacó el callout interno de los dropdowns pendientes (ruido de la agencia, no les correspondía).

**🆕 Auditoría exhaustiva Airtable + fixes P0 — 2026-07-01/02 (mayoría LIVE):** disparado por audio de Edgardo reportando que el campo `Sustratos compatibles` de Equipos mostraba anchos numéricos (166, 186, 320) en vez de nombres de sustrato. Se corrió el skill `/auditoria-airtable-cliente` (workflow multi-agente, 7 dimensiones adversariales sobre snapshot de 11 tablas/266 records) → **65 findings únicos: 7 P0, 19 P1, 39 P2** (`06_docs/airtable-auditoria-2026-07-01.md`). El bug de Edgardo (S-01: 37/53 records de Sustratos contaminados, 77 links de Equipos apuntando a fantasmas) fue solo 1 de 7 P0 — había 6 más rotos en silencio, incluyendo 2 tools en producción leyendo field names que ya no existían. **Aplicado (Airtable, escritura real por PAT, verificado):** S-01 resuelto (16 sustratos reales, 0 links colgados); T-06 Formato — 10 records migrados (MESA/PLOTTER/PLIEGO → Mesa/Plotter/Pliego); S-04 aprobado y ejecutado — 62/92 equipos con `Aplicaciones compatibles` regenerado por superposición de Tecnología (370 links). **Bloqueado (no aplicado):** limpieza de choices garbage en 5 dropdowns de Equipos (Marca/Formato/Disponibilidad zona/Status/Notas internas) — 3 intentos reales de PATCH a la meta API fallaron con 422 `INVALID_REQUEST_UNKNOWN` en 2 sesiones distintas; el PAT (`06_docs/airtable-credentials.md`) tiene `data.records:write` pero no `schema.bases:write`. Requiere limpieza manual en la UI o un token nuevo con ese scope. **Aplicado (n8n, código listo, mayoría deployada):** `sys-tool-consultar-catalogo-v5.json` (preserva workflowId `oQtLMujJBHlxZTTJ`) — fixes T-01 (`{Nombre}`→`{Aplicación}`), T-02 (tilde `Sustratos típicos`), T-03 (mapping Konica Minolta separado por intent), T-04 (saca ref muerta a `Velocidad`), T-05/T-06 (mitad n8n: `BRAND_MAP`/`FORMAT_MAP` corregidos) + **1 bug adicional no listado en el reporte original**: el filtro final `.filter(it => it.modelo)` descartaba silenciosamente TODOS los resultados de `intent=aplicacion` (esos items tienen `aplicacion`, no `modelo`) — ahora el filtro es intent-aware. También `sys-tool-consultar-url-tienda-v3.json` (preserva `EDoSNfvaEQTevJmj`) y `sys-tool-consultar-inventario-usados-v2.json` (cableado de vistas "Para agente" ya existentes, finding V-01). Doc de schema corregido: `05_crm/airtable-syscatalogo-schema.md` con sección "Correcciones 2026-07-01" (drift confirmado doc-vs-base-viva en 6+ tablas). **Estado de ejecución consolidado:** `06_docs/guia-fixes-post-auditoria-2026-07-01.md` (3 rondas documentadas). **De paso**, se generó el skill reutilizable `.claude/skills/auditoria-airtable-cliente/` para repetir este proceso con otros clientes (diagrama en Mermaid/Figma, no draw.io). **Pendiente:** limpieza manual de los 5 dropdowns (bloqueado, ver arriba); ~15 findings P1/P2 con decisión de negocio pendiente (duplicados BIZHUB/UV 6004/insumos SOFT, hipótesis marca Sinajet vs TENETH de 19 equipos DF/DG/DH, 91 `Descripción corta` vacías — requieren contenido real, no limpieza).

**🆕 `guardar_email` → `registrar_datos_lead` v1 — 2026-06-24 (en repo, pendiente deploy):** disparado por audio Edgardo del 2026-06-24 (P2 del análisis del digest matutino propuesto). Hoy `guardar_email` solo se activa cuando el lead deja email → cobertura parcial (sheet `Captura Emails` no ve leads que conversan + dan nombre/teléfono pero no email). Nuevo criterio: **el registro arranca apenas el lead da su nombre** (mínimo), y se enriquece (re-invocaciones) cuando llegan email/teléfono. Cambios: (1) **Sub-workflow nuevo `sys-tool-registrar-datos-lead-v1.json`** preserva el workflowId `v9HD7P2uroG4Ni3A` (import = overwrite in-place del v5). Validate Input acepta input parcial (≥1 de nombre/email/teléfono); Lookup por `subscriber_id` (vs email); nuevo bloque Merge with existing + Update Sheets en la rama "ya existe" — mergea sin pisar campos previos con vacíos; rama Append sin cambios; **notif Gmail dispara SOLO en INSERT, updates silenciosos** (decisión la agencia: digest matutino cubrirá la visibilidad de los enriquecidos); `Update datos_capturados` ahora persiste los 3 campos (vs v5 que solo escribía `mail`) → el main lee del state y no re-pregunta; log a `sys_tool_calls` con `tool_name='registrar-datos-lead'`. (2) **Prompt v2.2 → v2.3** — dos cambios mergeados: (A) Tool 9 reescrita en HERRAMIENTAS (criterio activación + upsert), Regla operativa 26 reescrita completa (activar con nombre + re-invocar con más datos, NO invocar con "hola" ni inventar campos, NO repetir en el mismo turno con los mismos datos), preámbulo de HERRAMIENTAS actualizado. (B) Merge de deltas del Google Doc vivo que el cliente editó directamente sin reflejar en repo: "Comercializan **y alquilan**" en ROL E IDENTIDAD; bullet "Alquiler de equipos" en Datos fijos (Konica Minolta monocromáticas y color para papel cortado; NO plotters/camas planas/cortadoras); nueva sub-sección "Flujo de consultas de alquiler" (4 preguntas + zona AMBA/interior); nueva sub-sección "Flujo de coordinación de demostración" (formulario mailing "Hola, quisiera coordinar una visita"). El backup `agente-sistemasysoluciones-system-prompt-v2.2.md` es snapshot del REPO en v2.2, NO de producción (que tenía los deltas de alquiler sin mergear). Para rollback verdadero re-extraer del Google Doc vivo antes de tocarlo. (3) **Edits en main vivo** (no pre-editado en repo, guía paso a paso): rename del toolWorkflow node `guardar_email` → `registrar_datos_lead`, description y 5 `$fromAI` descriptions actualizadas, set node `backup` con prompt v2.3 inline. Guía completa de deploy + 6 smoke tests E2E + queries de auditoría + rollback: `06_docs/guia-deploy-registrar-datos-lead-2026-06-24.md`. Backup prompt v2.2: `04_agents/agente-sistemasysoluciones-system-prompt-v2.2.md`. **Hoja "Ayer" del sheet Captura Emails** (resuelta en paralelo el 2026-06-24, en producción) usa fórmula `FILTER + ARRAYFORMULA + DATEVALUE/TIMEVALUE - 3/24` para mostrar leads de ayer en zona ART; queda como vista on-demand mientras el digest matutino (P1) no se construye.

**🆕 Mejoras Edgardo (mail 2026-06-23) — implementadas hoy:**

1. **#1 Recontacto a 4 días** ✅ deployado. Workflow `sys-seguimientos-leads-v2.json` reemplaza v1 — cron diario Lun-Vie 11h ART, sin LLM, mensaje fijo de Edgardo con `[Nombre]` reemplazado o fallback genérico. Vista Supabase nueva en `06_docs/supabase-schema-v3-seguimientos.sql` (1 toque a 4 días, no más 2 toques 24h+7d del v2 anterior). 39 leads procesados en primera corrida manual + 1 smoke con la agencia (subscriber `2004316097`). Cleanup: 1 leftover `smoke_email_001` borrado pre-corrida. Observación no bloqueante: 38/40 leads sin `nombre` en `sys_session_state.datos_capturados` → salen con fallback "Hola, buen día." en vez de personalizado. El nombre se persiste correctamente en Airtable Leads vía `notificar_lead` pero no en el state.

2. **#2 Mails a `emarti@`+`marketing@sistemasysoluciones.com`** ✅ deployado. 2 bugs en cadena diagnosticados y resueltos: (a) credencial `Gmail | la agencia®` (id `5R0ScEVqcfjKYanp`) perdió OAuth (403 Forbidden) — Edgardo reportó "antes dejó de llegar", causa raíz era esta — reconectada por usuario; (b) en `notificar-lead-v3` el nodo Gmail estaba downstream de `Asignar a Jimena (ManyChat)` y todas las refs eran `$json.X` → resolvían a `undefined` porque `$json` era la respuesta de ManyChat `{success:true}` — esto explica el "antes llegaba vacío" verbatim de Edgardo. Fix en v4: 13 refs cambiadas a `$('Validate Input').first().json.X`. Workflows vivos: `sys-tool-notificar-lead-v4.json` (id `QI1gO4dZ5vXXo7V3`) + `sys-tool-guardar-email-v5.json` (id `v9HD7P2uroG4Ni3A`, agrega nodo `Gmail Send notif (emarti + marketing)` entre Append y Format Output, solo dispara en email nuevo). Smoke 3 y 4 OK. CC `info@` removido (no estaba en lista oficial de Edgardo).

3. **#3 Consulta de precios interna desde Google Sheets** ❌ **RECHAZADA por Edgardo (2026-06-23)** — posible re-incorporación dentro de un proyecto más grande. Diseño completo desarrollado en plan `/Users/camilo/.claude/plans/bien-lo-que-vamos-snazzy-nygaard.md` (path desviado pre-AI Agent, sin LLM, lectura en vivo del sheet de Rodri, whitelist Rodrigo+la agencia para testing, bypasea dedup, no contamina memoria del agente). Llegamos a generar main v0.10 con los 8 nodos del path interno cableados; tras el rechazo se eliminó v0.10 (v0.9 sigue siendo main canónico) y se preservó la lógica como sub-workflow standalone `03_workflows/sys-tool-consulta-precios-interna-archivado-v1.json` (8 nodos, Execute Workflow Trigger en lugar de IF whitelist, pinData con subId la agencia + query "cuanto sale el HUENU UV") + README `03_workflows/README-consulta-precios-interna-archivado.md` + propuesta económica `01_discovery/propuesta-consulta-precios-interna-2026-06-23.md` (USD 240 / 2hs / 48hs / pago al aprobar) + guía deploy `06_docs/guia-deploy-consulta-precios-interna-2026-06-23.md`. Cleanup adicional: prompt revertido a v2.2 (eliminada sección MODO INTERNO + Tool 10 + Regla 27 que se habían agregado para soportar #3), `sys-tool-consultar-precio-interno-v1.json` → `.superseded.json` (era una versión anterior del diseño como tool del agente).

**Stack Etapa 2:** n8n + ManyChat (IG/WA/FB) + OpenAI gpt-4o + Supabase Postgres (memoria) + Airtable (RAG/catálogo) + Gmail + Telegram

**Archivos clave:**

*Plan y arquitectura:*
- `/Users/camilo/.claude/plans/contexto-general-del-dapper-sun.md` — **Plan Maestro Etapa 2** (17 secciones, 8 fases, ~15-25 días estimados)
- `02_architecture/architecture-v2-2026-05.md` — Arquitectura v2 (componentes, integraciones, 16 decisiones arquitectónicas, capacidad, riesgos)

*System prompt:*
- `04_agents/agente-sistemasysoluciones-system-prompt.md` — **System prompt v2.7 — LIVE (deployado 2026-07-10)**. Hereda v2.4 (ramificación A/B/C diagnóstico) + v2.5 (mesas de corte, accesorio cilíndrico, política insumos). v2.6 (2026-07-08): registro de leads gated por teléfono — línea `Teléfono del lead` en el contexto, ficha `registrar_datos_lead` con fuente determinística (ManyChat) vs agéntica (chat), Regla 26 reescrita. v2.7 (2026-07-10): fix post-test en producción — Regla 18 endurecida (no aceptar "mi número es este" sin dígitos), Regla 26 con bloqueo duro sin teléfono + pairing obligatorio `notificar_lead`↔`registrar_datos_lead`, REGLA CRÍTICA anti-`{{phone}}` en derivación, + dato fijo "Papel fotográfico / casas de fotos" (nunca recomendar láser/RISO para ese uso). Guías de deploy: `06_docs/guia-deploy-registro-leads-telefono-2026-07-08.md` (incluye §9 errata hotfix `IF lead existe?` type mismatch, resuelto — ver `sys-tool-registrar-datos-lead-v3.json`) + `06_docs/guia-notificar-lead-registra-en-planilla-2026-07-10.md` (✅ aplicada y verificada en producción).
- `04_agents/agente-sistemasysoluciones-system-prompt-v2.6.md` — Backup v2.6 (snapshot pre-fix Regla 18/26 post-test producción)
- `04_agents/agente-sistemasysoluciones-system-prompt-v2.5.md` — Backup v2.5 (snapshot del texto vivo en Google Docs al 2026-07-08 — nunca había estado en repo, el repo estaba parado en v2.4)
- `04_agents/agente-sistemasysoluciones-system-prompt-v2.3.md` — Backup v2.3 (snapshot pre-bump diagnóstico adaptativo — último plan de deploy registrar_datos_lead al 2026-06-25)
- `04_agents/agente-sistemasysoluciones-system-prompt-v2.2.md` — Backup v2.2 (snapshot pre-bump registrar_datos_lead — último vivo en n8n al 2026-06-24)
- `04_agents/agente-sistemasysoluciones-system-prompt-v2.1.md` — Backup v2.1 (snapshot post-fix Zod Episodio 2)
- `04_agents/agente-sistemasysoluciones-system-prompt-v2.0.md` — Backup v2.0 (último de Etapa 2 pre-Episodio 2; coincide con el live hasta 2026-06-05)
- `04_agents/agente-sistemasysoluciones-system-prompt-v1.7.md` — Backup v1.7 (último de Etapa 1)
- `04_agents/agente-sistemasysoluciones-system-prompt-v1.6.md` — Backup v1.6
- `04_agents/agente-sistemasysoluciones-system-prompt-v1.5.md` — Backup v1.5
- `04_agents/agente-sistemasysoluciones-system-prompt-v1.4.md` — Backup v1.4

*Schemas:*
- `05_crm/airtable-syscatalogo-schema.md` — Schema Airtable `SyS Catalogo` (11 tablas). **Sección "Correcciones 2026-07-01"** documenta el drift confirmado doc-vs-base-viva post-auditoría (Cabezales/Insumos/Konica Minolta/Config Mensual/Leads + estado Sustratos/Equipos↔Aplicaciones ya resueltos).
- `06_docs/supabase-schema.sql` — SQL ejecutable Supabase (4 tablas + 3 vistas + función `upsert_session_state`)

*Auditoría Airtable (2026-07-01):*
- `06_docs/airtable-auditoria-2026-07-01.md` — Reporte completo: 65 findings (7 P0/19 P1/39 P2), fixes propuestos con `curl --dry-run`, preguntas para Edgardo, plan de fixes, matriz tool↔Airtable.
- `06_docs/guia-fixes-post-auditoria-2026-07-01.md` — Estado de ejecución (3 rondas: S-01+T-06 parcial / retry schema-write fallido / S-04 aprobado y ejecutado).
- `06_docs/snippets/clipboard-consultar-catalogo-classify-format-2026-07-01.json`, `clipboard-inventario-usados-view-2026-07-01.json`, `clipboard-lineas-priorizadas-format-2026-07-01.json` — nodos sueltos para pegar (formato clipboard la agencia).

*Registro de leads / teléfono (2026-07-08/10):*
- `06_docs/guia-deploy-registro-leads-telefono-2026-07-08.md` — Deploy del gate por teléfono (sub-workflow v2 + edits main + prompt v2.6). LIVE.
- `06_docs/guia-notificar-lead-registra-en-planilla-2026-07-10.md` — Red estructural: `notificar_lead` invoca también `registrar_datos_lead`. **✅ Aplicada y verificada en producción (2026-07-09/10).**
- `03_workflows/sys-tool-registrar-datos-lead-v3.json` — Hotfix del `IF lead existe?` (type mismatch number/string de Google Sheets). Preserva workflowId `v9HD7P2uroG4Ni3A` (⚠️ ver nota de discrepancia de IDs más arriba), reemplaza a v2 como archivo vigente.
- `03_workflows/sys-tool-notificar-lead-v5.json` — Re-export del workflow vivo post-fix (2026-07-10), incluye el nodo `Registrar en planilla` de la red estructural. **`id: M25w0GBLPgiHYJzw`** — no coincide con `QI1gO4dZ5vXXo7V3` documentado hasta ahora, ver hallazgo arriba. Es la fuente de verdad más reciente y confiable para este tool.
- `06_docs/snippets/clipboard-registrar-datos-lead-node-2026-07-08.json`, `build-user-message-context-v2.6.js`, `clipboard-notificar-registrar-en-planilla-node-2026-07-10.json` — nodos/código sueltos para pegar.

*Specs y operación:*
- `06_docs/tools-spec-v1.md` — Spec detallada de las 8 tools (inputs/outputs, implementación n8n nodo por nodo, validaciones, errores, contrato común RESOLVED/AMBIGUOUS/NOT_FOUND/ERROR)
- `06_docs/airtable-guia-edgardo-2026-07-02.md` — **Guía operativa vigente para Edgardo** (revisión 2026-07-10, formato ultra-simple por tabla: uso/modificás/no tocás + tabla "dónde lo arreglo"). Reemplaza en uso a `guia-airtable-edgardo-v1.md` (no borrado, queda como histórico).
- `06_docs/guia-airtable-edgardo-v1.md` — Guía editor Airtable v1 (histórica, ver la vigente arriba)
- `06_docs/runbook.md` — Runbook operativo (P1-P3 SLAs, diagnóstico rápido, incidentes comunes, queries SQL útiles, escalamiento)

*Testing:*
- `07_testing/testing-guide-v6.md` — **v6 actual: Testing Etapa 2** (18 casos simples + 16 flujos cubriendo tool calling, memoria persistente, NOT_FOUND anti-alucinación, multi-canal, reglas 22-25)
- `07_testing/testing-guide-v5b-retest-v1.7.md` — Re-test v1.7 (renombrado desde v6 viejo)
- `07_testing/testing-guide-v5.md` — Testing v1.6 — Completado
- `07_testing/testing-guide-v4.md` — Testing v1.5 — Completado
- `07_testing/testing-guide-v3.md` — Re-test v1.4 (8 casos corregidos)
- `07_testing/testing-guide-v2.md` — Testing v1.3 completo
- `07_testing/testing-guide-v1.md` — Testing inicial

**Workflows pendientes de implementar (Fase 3-4):** `03_workflows/sys-agente-principal-v1.json` + 8 sub-workflows tools (`sys-tool-buscar-equipo-v1.json`, `sys-tool-consultar-tecnologia-v1.json`, `sys-tool-consultar-aplicacion-v1.json`, `sys-tool-consultar-compatibilidad-v1.json`, `sys-tool-consultar-faq-v1.json`, `sys-tool-consultar-lineas-priorizadas-v1.json`, `sys-tool-consultar-url-tienda-v1.json`, `sys-tool-notificar-lead-v1.json`).

**Bloqueos cliente (pre-flight Fase 0):** ✅ todos resueltos 2026-05-28. Sin nombre propio del agente, URL tienda `https://www.sistemasysoluciones.com`, mail `info@sistemasysoluciones.com`, Opción A sin especialización de reps, catálogo arranca con stub (Edgardo completa).

**⚠ Alcance reducido — CRM pausado 2026-05-28:** cliente decidió no avanzar con CRM en Etapa 2. Tabla Airtable Leads creada pero sin uso productivo. Tool `notificar_lead` solo manda mail + Telegram (sin write a Airtable). Vistas Leads + seguimiento automático + reporte semanal quedan para upsell. **Re-proponer al mes 1 post-GO-LIVE.** Upsell formal: `ops/04_upsells/SYS-upsell-crm-leads-2026-05-28.md` (USD 500 único + USD 30/mes bundle CRM + Seguimiento + Reporte).

**✅ Re-alineación post-Excel — 2026-05-29:** cliente entregó `BASE DE PRODUCTOS.xlsx` con catálogo completo. Schema Airtable + prompt + tools re-alineados a la realidad: marcas reales (HUENU/DLICAN/TENETH/HANRUN/XENONS + RISO/Sinajet/Konica Minolta, NO Mimaki/Roland), 10 tecnologías (+Solvente +Corte), 12 tablas Airtable (+Inventario Konica Minolta refurbished), 11 CSVs importables, prompt v2.0 → v2.1, +1 tool nueva (`consultar_inventario_usados` = Tool 9). Doc maestro: `clients/SYS_SistemasYSoluciones/06_docs/realineacion-post-excel-2026-05-29.md`.

**✅ F1 COMPLETADA — 2026-05-29:** base Airtable creada y poblada (~230 records: 92 equipos + 10 cabezales + 33 insumos + 21 inventario Konica + seeds varios), credencial n8n `Airtable SYS` configurada (`3zohdTBWzW8UUN6P`), vistas "Para agente" configuradas, smoke test OK. Variables n8n: decisión **Opción C — hardcoded** (plan n8n actual no soporta Variables UI). Catálogo único de valores en `06_docs/airtable-credentials.md` sección "Valores hardcoded". Único pendiente operativo: onboarding 30 min con Edgardo (no bloqueante).

**✅ F2 COMPLETADA — 2026-05-29:** proyecto Supabase `la agencia-sys` creado (region sa-east-1, free tier), schema ejecutado (4 tablas + 3 vistas + función `upsert_session_state`), credencial n8n `Supabase SYS` configurada, smoke test OK. **Decisiones técnicas registradas:** (a) usar **Session Pooler** `aws-0-sa-east-1.pooler.supabase.com:5432` en vez de Direct Connection — la direct usa IPv6 y el droplet n8n no tiene IPv6 outbound; (b) **Ignore SSL Issues = true** en credencial — Node.js (n8n) sin cert root de Supabase. Detalles en `06_docs/supabase-credentials.md` (gitignored).

**✅ F3 COMPLETADA — 2026-05-29:** workflow `sys-agente-principal-v0.1` activo en n8n (10 nodos: webhook → normalize → IF skip → context → AI Agent gpt-4o + Postgres Chat Memory + system prompt v2.1 inline → split → respond). 5 smoke tests pasados incluyendo memoria persistente cross-turn y aislamiento por sessionKey. 2 nits menores observados (saludo no usa "asistente virtual" + frase Regla 4 del mail variante) — anotados para revisar en F7.

**✅ F4 COMPLETADA — 2026-05-29:** 9 sub-workflows tools importados en n8n con credentials cableadas (Airtable SYS + Supabase SYS). Patrón común: Trigger → Validate → Airtable → Format → Log Postgres → Return. 8 tools lectura + 1 escritura (`notificar-lead`: Gmail + Telegram + Postgres state, sin Airtable Leads por CRM pausado).

**✅ F5 COMPLETADA — 2026-05-29:** `sys-agente-principal-v0.2.json` (19 nodos = 10 base + 9 toolWorkflow nodes conectados al AI Agent via `ai_tool`). Cada tool con `$fromAI()` cableado en sus inputs + descripciones ricas para el LLM. Smoke tests E2E OK. Logs a `sys_tool_calls` escribiendo correctamente. **Bug resuelto durante F5:** `queryReplacement` en 10 nodos Postgres (9 `Log to sys_tool_calls` + 1 `Update session_state`) usaba sintaxis CSV concatenada (`={{ A }}, ={{ B }}`) que rompía con valores JSON conteniendo comas. Fix: sintaxis array `={{ [A, B, C, D, E] }}`. Documentado en runbook sección "Incidentes resueltos".

**🔄 F6 en ejecución — 2026-05-29:** integración ManyChat. v0.3 del main reemplaza el Respond JSON directo por `setCustomFields` + `sendFlow` API calls. Setup ManyChat: 4 custom fields + 2 flows (Default Reply con External Request + Responder Multi-Parte trigger-eado por sendFlow).

**🆕 Captura de emails — 2026-06-02 (cableada en prod, alcance vigente):** existe la tool `guardar_email` (`03_workflows/sys-tool-guardar-email-v1.json` vivo en prod, **`sys-tool-guardar-email-v2.json` en repo pendiente deployar como Capa 2 del fix re-saludo/re-pregunta** — agrega 1 nodo Postgres `Update datos_capturados` entre `IF skip?` rama false y `Lookup email existente` que escribe el `mail` capturado a `sys_session_state.datos_capturados` con merge JSONB nativo; antes solo iba a Google Sheets y el main no lo veía → la Regla 4 volvía a ofrecer el descuento turno tras turno; v2 reemplaza al v1 in-place al importar con el mismo workflowId `v9HD7P2uroG4Ni3A`). Persiste el email del lead en Google Sheets apenas se captura, con dedup vía lookup previo. Sheet "SYS - Leads (Captura Emails)" (`15OrQ-uI_x5rAorjkMpz_V_TvFxVf31nsDfTjm9oUqsc`). El sub-workflow valida email + acepta args opcionales de segmentación (`origen` enum, `aplicacion_interes`, `canal`) que se persisten cuando llegan. **Documentación del prompt:** v2.0 NO documentaba `guardar_email` (gap). **Resuelto 2026-06-05 (Episodio 2 Zod):** v2.1 agrega Tool 9 en HERRAMIENTAS + Regla operativa 26 (PROHIBIDO invocar sin email explícito). Pendientes operativos no críticos: completar el header del Google Sheet con las 3 columnas extra (`canal`, `aplicacion_interes`, `origen`) si se quiere persistir segmentación real cuando el AI la pase.

**✅ Elevación al CM por mail con link + asignación automática a Jimena — 2026-06-05:** decisión cliente (Edgardo) — cuando el agente invoca `notificar_lead`, el sub-workflow `sys-tool-notificar-lead-v2` (workflowId `QI1gO4dZ5vXXo7V3`) hace dos cosas: (a) HTTP a `https://api.manychat.com/fb/sending/sendFlow` con `flow_ns="content20260605164825_697855"` que asigna la conversación a **Jimena** en Live Chat + pausa el bot; (b) Gmail HTML a `marketing@sistemasysoluciones.com` (TO) con cc a `info@sistemasysoluciones.com`, link directo al chat (`https://app.manychat.com/fb5013937/chat/<subscriber_id>`) y datos del lead. Sin Telegram (removido del sub-workflow). El main `sys-agente-principal-v0.5.json` (26 nodos, workflowId del nodo notificar_lead apunta al v2) tiene tres nodos adicionales que cargan el prompt v2.0 desde Google Docs (`Get a document` → AI Agent · `backup` set-node con prompt hardcoded como fallback · `notificar` Telegram a chatId `6390727286` si Docs falla). **PAGE_ID ManyChat:** `5013937`. **Credenciales en n8n:** Gmail `Gmail | la agencia®` (id `5R0ScEVqcfjKYanp`), ManyChat HTTP `Webhook SYS Inbound` (id `UnA18VVz7bSrSUNX`), Postgres `Supabase SYS` (id `cQLxF5deDtmo4HTV`). Guía: `06_docs/guia-elevacion-cm-mail-link-2026-06-03.md` + `06_docs/asignacion-jimena-manychat-2026-06-05.md`. Fix Zod aplicado en notificar_lead y guardar_email (descripciones `$fromAI` minimalistas).

**☢️ Refactor nuclear — Bug Zod LangChain — 2026-06-03:** los 3 tools `consultar_aplicacion`, `buscar_equipo`, `consultar_inventario_usados` fallaban consistentemente con `Received tool input did not match expected schema` en n8n LangChain v1.122.4 (`DynamicStructuredTool.call` con `errorDetails: {}` opaco). Se descartaron 8 hipótesis intermedias (attemptToConvertTypes, jsonExample types, $fromAI descriptions, mappingMode passthrough, Trigger passthrough, workflowId placeholder, prompt strict, prompt revert). **Solución que sí destrabó: refactor nuclear** — los 3 tools rotos reemplazados por **1 tool consolidada `consultar_catalogo`** (`03_workflows/sys-tool-consultar-catalogo-v1.json`) con superficie mínima de schema (`query: string` + `session_id`). Sub-workflow internamente: Code `Classify Intent` (regex + stopword filter + formula-builder) → Switch 3-way (aplicacion / inventario / equipo) → 3 nodos Airtable con `filterByFormula` OR multi-keyword → Format Output → Log → Return. Smoke test post-nuclear: **5/10 OK + 5 Parcial + 0 Error** (vs 4 Errors pre-nuclear). Tools retornan items reales: HUENU UV → `HR 6004 DU / HR 1602 SU / HR 3208 UV / HR 3212 UV / CCD CAMERA UV3040`; Konica usados → `BIZHUB C450i / BIZHUB 558E / Acurio Press C3080 / BIZHUB C224`. Postmortem completo: `06_docs/incidente-bug-zod-langchain-2026-06-03.md`. **Pendiente:** (a) re-exportar `sys-agente-principal` post-nuclear de n8n como v0.5 (el v0.4 del repo NO refleja estado vivo); (b) refinar prompt para que cuando `consultar_catalogo` devuelve items con `modelo`, el agente los mencione específicamente; (c) verificar/poblar tabla Aplicaciones en Airtable.

**☢️ Bug Zod LangChain — Episodio 2 — 2026-06-05:** el AI Agent crashó con `Received tool input did not match expected schema` ante el mensaje `"Federico Vizcarra 1131345321 san Miguel"` en la session `wa_1686796493` (lead inbound dando nombre + teléfono + zona, sin email). Query a `sys_tool_calls` confirmó la firma del bug Zod: la sesión solo tiene una row, `consultar-catalogo` RESOLVED a 12:03:33; ningún `notificar_lead` ni `guardar_email` logueado — el sub-workflow del tool culpable nunca ejecutó. **Diagnóstico refinado:** el LLM ya tenía contexto de equipo del `consultar_catalogo` previo, y con nombre+tel+zona del nuevo mensaje completó mentalmente los 4 obligatorios → probable culpable `notificar_lead` (11 campos LLM-exposed = la superficie más amplia del workflow). `guardar_email` queda como hipótesis secundaria (5 campos, sin email — improbable pero posible). **Causa secundaria — gap del prompt:** v2.0 vigente NO documentaba `guardar_email`. **Fix doble preventivo (cubre ambos candidatos):** (A) Schema: descripciones `$fromAI` minimalistas en los 16 campos LLM-exposed (`notificar_lead` 11 + `guardar_email` 5; Required OFF, Type string — sub-workflows validan internamente). (B) Prompt: bump v2.0 → v2.1 con Tool 9 + Regla operativa 26 (PROHIBIDO invocar `guardar_email` sin email explícito). Guía paso a paso reescrita con dos vías de fix: `06_docs/guia-fix-guardar-email-zod-2026-06-05.md` (Paso 0 opcional verificar tool + Paso 1A EDITs `notificar_lead` + Paso 1B EDITs `guardar_email` + Paso 2 copy-paste prompt v2.1 + Paso 3 smoke E2E 3 casos + Paso 4 re-export v0.6 + Anexo A auditoría preventiva de las 4 tools restantes). Postmortem actualizado: `06_docs/incidente-bug-zod-langchain-2026-06-03.md` sección "Episodio 2" con evidencia `sys_tool_calls`. **Pendiente:** aplicar Pasos 1A+1B+2+3+4 en n8n vivo + commit `sys-agente-principal-v0.6.json` + (opcional) Anexo A para hardenear resto de tools.

**🎙️ Formatter de mensajes — 2026-06-03:** agregado nodo gpt-4o-mini intermedio entre AI Agent y Split Respuesta — el AI Agent omitía los separadores `---` en respuestas con tool calls → Split Respuesta lumpeaba todo a `ai_msg_1` → ManyChat mandaba un mensaje único largo perdiendo cadencia. Solución: nodo `Formatear mensaje` (`@n8n/n8n-nodes-langchain.openAi`, `jsonOutput=true`, `temperature=0`) que recibe el output del AI Agent y devuelve `{parte1, parte2, parte3}` JSON estructurado. Split Respuesta jsCode actualizado a v3 que parsea el JSON + **compacta partes no-vacías** en orden (defensa contra modelo que salte parte2). Patrón validado en NPR/NVJ/HBV/STK previo a SYS. Costo: +300ms latencia + ~$0.0005/turno. Config completa: `06_docs/formatter-mensajes-config.md` (system prompt + jsCode paste-ready + verificación curl). Smoke post-formatter: **6/10 OK + 4 Parcial + 0 Error**.

**Roadmap (8 fases del Plan Maestro):** F0 Pre-flight (1-2d) → F1 Migración Airtable (3-5d) → F2 Setup Supabase (1d) → F3 Memoria persistente (1-2d) → F4 Tools build (3-5d) → F5 System Prompt v2.0 (2d) → F6 Integración ManyChat (2-3d) → F7 Testing E2E (3-5d) → F8 Producción (2-3d).

**Cierre 2026-06-05 (gaps de la recomendación de cierre):** **Gap B (descuento)** → DESCARTADO por Edgardo (2026-06-09): el cliente decidió NO incorporar el tema del descuento. El prompt queda en v2.1 sin mención de descuento. **Gap C (canal web)** → OBSOLETO, se considera cubierto vía WhatsApp. **Gap A (migración infra)** → guía creada (ver pendiente 1). Deploy main v0.6 + seguimientos ya hecho.

**🔧 Cola de cierre del proyecto — ✅ CERRADA el 2026-08-04.** La migración de infraestructura se
completó y **el desarrollo pasa a Camilo**: todo lo que quedaba en repo sin deployar deja de ser
pendiente de la agencia-la agencia y se maneja en su línea de trabajo.

- ✅ **Migración de infraestructura a cuentas del cliente — HECHA.** Airtable, Supabase y n8n corren
  ahora en cuentas propias del cliente, con todas las credenciales reconectadas.
- ➡️ **Deploy de main v0.9** (fix re-saludo + re-pregunta de datos ya capturados) — **pasa a Camilo.**
- ➡️ **Deploy de `sys-tool-guardar-email-v2` y `registrar_datos_lead`** — **pasa a Camilo.**
- ➡️ **Auditoría de workflowId/credenciales reales en n8n** (los documentados no coinciden con los
  vivos, probable secuela de la migración) — **pasa a Camilo.**
- ➡️ **Limpieza de los 5 dropdowns de Airtable** (estaba bloqueada por permiso de API) — **pasa a Camilo.**

> ⚠️ Todo lo que sigue abajo con etiqueta "en repo, pendiente deploy" hay que leerlo con esa lente:
> es backlog de Camilo, no cola de la agencia.

<details>
<summary>Detalle histórico de la cola (al 2026-06-05)</summary>

1. **Migración de infraestructura a cuentas del cliente** — pasar todo lo que hoy corre en cuentas la agencia a infraestructura propia del cliente: (a) crear cuenta **Airtable** del cliente + replicar base + actualizar credenciales en n8n; (b) crear cuenta **Supabase** del cliente + ejecutar schema + actualizar credenciales en n8n; (c) instalar **n8n** en el servidor que ya tienen + importar todos los flujos (main + sub-workflows tools); (d) re-conectar todas las credenciales nuevas en n8n. ManyChat YA está en cuenta del cliente, no se toca. Es el ítem más pesado de los 3. **Guía de migración paso a paso: `06_docs/guia-migracion-infra-cliente-2026-06-05.md`** (qué se migra, pasos por plataforma, reconexión de credenciales, chequeos E2E, rollback).
2. ~~**Seguimientos automáticos**~~ → **✅ Listo para deployar (2026-06-05):** workflow `03_workflows/sys-seguimientos-leads-v1.json` (cron Lun-Vie 9/13/17 ART, 2 toques a 24h + 7d, mensaje generado con gpt-4o-mini personalizado). Schema v2: `06_docs/supabase-schema-v2-seguimientos.sql` (columna `seguimientos_enviados` + vista `sys_leads_para_seguimiento`). Requiere desplegar también el main v0.6 (que agrega nodo `Update ultima_actividad` para que la vista funcione). Guía: `06_docs/guia-implementacion-seguimientos-y-mejoras-2026-06-05.md`.
3. ~~**Implementaciones del Google Docs del cliente**~~ → **✅ Listo para deployar (2026-06-05):** 4 puntos del cliente cubiertos en main v0.6 (`03_workflows/sys-agente-principal-v0.6.json`) + 5 edits al prompt en Google Doc (documentados en `06_docs/edits-prompt-mejoras-2026-06-05.md`). Cobertura: (1) provincia/localidad → Reglas 3 + 26 nuevas; (2) reconocer "ese número" → Build User Message Context inyecta `subId` cuando canal=wa + Regla 27 nueva; (3) preguntar equipo/experiencia → ETAPA 5.5 nueva; (4) mensajes duplicados → `Respond to Webhook` movido en paralelo al `Build User Message Context` (responde 200 OK al instante, downstream sigue async — elimina reintentos de ManyChat por timeout). Prompt bump v2.0 → v2.1.

</details>

**Estado main:**
- **v0.5** (vivo en n8n actualmente) — snapshot de prod del 2026-06-05.
- **v0.6** (en repo, pre-fix re-saludo) — v0.5 + 3 cambios localizados: `Build User Message Context` con `subId`, `Respond to Webhook` movido temprano (fix duplicados), nuevo nodo `Update ultima_actividad` después del `IF skip?` (necesario para que el cron de seguimientos funcione). Diff verificado: 27 nodos vs 26, conexiones de `IF skip?` rama no-skip ahora son 3 paralelas, `sendFlow ManyChat` queda como nodo terminal. **No toca el systemMessage** (los edits del prompt van directo al Google Doc).
- **v0.7** (en repo, intermedio — superado por v0.9) — Capa 1 del fix: `Get session_state` SELECT + `Build User Message Context` leyendo state real + `Update ultima_actividad` no pisa etapa. Queda como reference si se necesita rollback parcial.
- **v0.8** (en repo, **NO deployar — perdió `Update ultima_actividad`**) — iteración intermedia que eliminó por error el nodo `Update ultima_actividad` asumiendo que el nuevo `Upsert state patch` lo cubría funcionalmente. Funcionalmente sí lo cubre (ambos UPSERTs escriben `ultima_actividad = NOW()`), pero defense in depth + ownership claro del cron de seguimientos justificó conservarlo separado. Reemplazado por v0.9.
- **v0.9** (en repo, **deploy a cargo de Camilo desde 2026-08-04** — ya no es cola de la agencia) — **Capa 1 + Capa 2 del fix re-saludo + re-pregunta de datos ya capturados** (plan: `/Users/camilo/.claude/plans/act-a-como-un-senior-imperative-quasar.md`), regenerado desde v0.6 (base canónica) preservando los 3 fixes de v0.6 (Update ultima_actividad para alimentar `sys_leads_para_seguimiento`, Respond to Webhook paralelo anti-timeout ManyChat, subId inyectado en Build cuando canal=wa). 31 nodos vs 28 de v0.6 (+3: `Get session_state`, `Parse datos del mensaje`, `Upsert state patch`). Cambios: (a) nodo Code `Parse datos del mensaje` (parser determinístico SIN LLM: regex de email + teléfono AR + nombre por heurística disparadores "soy/me llamo/mi nombre es" + ubicación por lista cerrada de zonas AR; filtra explícitamente el teléfono de oficina 4342-5742; no pisa datos ya capturados); (b) nodo Postgres `Upsert state patch` con `INSERT ... ON CONFLICT DO UPDATE SET datos_capturados = sys_session_state.datos_capturados || EXCLUDED.datos_capturados, ultima_actividad = NOW()` — merge JSONB nativo, NO toca etapa; (c) `Build User Message Context` reescrito para mergear `_stateRow.datos_capturados + patch` en JS y mostrar al LLM la versión MÁS FRESCA en el MISMO turno donde el patch se detectó, manteniendo el subId del canal de v0.6; (d) `Update ultima_actividad` modificado para NO pisar `etapa = 'diagnostico'` y CONSERVADO en paralelo — defense in depth ante fallas del Upsert state patch (ambos escriben `ultima_actividad` redundantemente). Topología nueva: `IF skip? false → [Get session_state → Parse → Upsert → Build → Get a document → ... → AI Agent | Respond to Webhook | Update ultima_actividad]` (3 paralelas a la salida del IF skip false; el flujo principal es la cadena serial). El nodo `backup` (set node con snapshot inline del prompt para fallback si Google Docs falla) fue sincronizado con el prompt v2.2 completo. Capa 3 ya APLICADA en el archivo local: prompt v2.1 → v2.2 con sección "USO DEL CONTEXTO DEL TURNO" — falta subirlo al Google Doc vivo (guía: `06_docs/edits-prompt-v2.2-uso-contexto-turno-2026-06-09.md`). **Plan de deploy**: importar v0.9 a n8n staging + importar `sys-tool-consultar-catalogo-v2.json` + `sys-tool-guardar-email-v3.json` + `sys-tool-notificar-lead-v3.json` (ver bugfix Return Output abajo) + actualizar el Google Doc del prompt según la guía, correr smoke tests A/B/C/D/E/F/G/H/I del plan, promover si pasa.

**🐛 Bugfix Return Output de tools — 2026-06-09:** detectado que 3 sub-workflows devolvían `{success:true}` (output del Log Postgres) en lugar del shape estándar `{status, data, message_to_agent, trace_id}` que el AI Agent espera. Causa: el nodo `Return Output` usaba `={{ $json }}` (output del nodo previo = Log Postgres execute query). **Fix A** — `Return Output` final ahora referencia explícitamente el `Format Output` correcto: `consultar_catalogo` usa `={{ $('Format Output').first().json }}`; `guardar_email` (con 2 ramas saved/already_exists) usa patrón `isExecuted` para elegir el Format que efectivamente corrió. **Fix B** — `Return NOT_FOUND (skip)` de `consultar_catalogo` quitó el `JSON.stringify({...})` que devolvía un string en vez del objeto esperado por `jsonOutput`. **Fix C** — los `Return ERROR` de `guardar_email` y `notificar_lead` (rama de validación fallida) devolvían los datos crudos del `Validate Input` — ahora construyen el shape estándar con `message_to_agent` extraído de Validate y `trace_id = $execution.id`. **JSONs generados en repo** (todos preservan el workflowId vivo, importar = overwrite directo): `sys-tool-consultar-catalogo-v2.json` (id `oQtLMujJBHlxZTTJ`); `sys-tool-guardar-email-v3.json` (id `v9HD7P2uroG4Ni3A`, sucede al v2 mío que heredaba el bug); `sys-tool-notificar-lead-v3.json` (id `QI1gO4dZ5vXXo7V3`, solo Fix C — Return Output ya estaba OK). **Las otras 7 tools del grupo OK** (`buscar_equipo`, `consultar_aplicacion`, `consultar_compatibilidad`, `consultar_faq`, `consultar_inventario_usados`, `consultar_lineas_priorizadas`, `consultar_tecnologia`, `consultar_url_tienda`) ya usan `={{ $('Format Output').item.json }}` y NO necesitan fix.

**Upsells pendientes — sigue abierto (owner: la agencia, comercial):** CRM completo (`ops/04_upsells/SYS-upsell-crm-leads-2026-05-28.md`) + integración Meta Ads quick replies. Ambos se proponen al cliente después de cerrar Etapa 2.

---

### VTR — Venttur (`clients/VTR_Venttur/`)

Tracking de conversiones Lead en Meta CAPI para plataforma educativa. Recibe folios desde landings via webhook, los cruza con datos CAPI en Airtable, y envía eventos Lead a Meta al momento de la conversación en WhatsApp. Rama CTWA activa (Opción A). **Outreach proactivo WA post-form Meta en producción ✅ (2026-06-13).**

**Contactos:** Mauricio García de la Vega (dueño) · Max (técnico)

> ⚠️ **Dos clientes distintos con dueños del mismo nombre.** El dueño de **Venttur** y el de
> **TOFO Pizza** se llaman **ambos Mauricio García de la Vega**: el de Venttur es **hijo** del de
> TOFO. No son la misma persona y no son el mismo cliente. Antes de escribirle a "Mauricio",
> confirmá de qué proyecto estás hablando — mezclarlos ya generó una atribución errónea de un
> pendiente el 2026-08-05.

**Stack:** ManyChat + WhatsApp Business API + n8n + Airtable + Meta CAPI + Clientify

**Infraestructura:**
- Airtable base: `[AIRTABLE_BASE_ID]` | Credentials n8n: `[N8N_CREDENTIAL_ID]`
- Tablas: Folios CAPI (`[AIRTABLE_TABLE_ID]`), Programas CAPI (`[AIRTABLE_TABLE_ID]`), Leads (`[AIRTABLE_TABLE_ID]`)

**Archivos clave:**
- `03_workflows/meta-capi-venttur-v2.json` — Workflow principal CAPI (rama folio + rama CTWA via `programa_wpp`)
- `03_workflows/wf-rescate-post-link.json` — **Workflow Rescate Post-Link** (`mkEP1qFN7MVb9qP0`). 2 fases (45 min + 24 hrs), check `Agendan cita` en Airtable, routing por programa, `setCustomFields` batch con `mcBody`/`JSON.stringify`. Disparado desde `wf-actualizar-link-enviado` via Execute Workflow. **En producción** ✅.
- `06_docs/rescue-flow-implementation-guide.md` — Guía de implementación flujo Rescate Post-Link (actualizada 2026-05-26 con patrón mcBody, field_id, quirks ManyChat API)
- `06_docs/rescue-flow-message-templates.md` — 12 templates de mensajes de rescate (6 programas × 2 fases)
- `03_workflows/wf-estado-lead-venttur-v1.json` — Sub-workflow **estado de lead** (nuevo): estampa `Estado conversación = Contestó` + `Última actividad` por cada mensaje entrante; match por `Telefono`; guarda anti-downgrade (no pisa `Cita confirmada`). Llamado desde `venttur-main` (no bloqueante).
- `03_workflows/wf-estado-interrumpida-venttur-v1.json` — Workflow **barrido de silencio** (nuevo, programado cada 1 h): marca `Conversación interrumpida` los leads con `Última actividad` > 24 h, sin cita y no ya interrumpidos. Idempotente.
- `06_docs/estado-leads-implementation-guide.md` — ❌ **DESCARTADO 2026-08-04 (no se aplica; queda como diseño de referencia).** Guía paso a paso del reporte automático de estado de leads (n8n-centric, cero cambios ManyChat). Incluye los 2 campos Airtable nuevos (`Estado conversación` single-select, `Última actividad` date+time), import de los 2 workflows, y los 3 EDITs en vivo (A: `venttur-main` nodo `Estampar estado (Contestó)`; B: `crear-contacto-clientify-airtable` nodo `Crear o actualizar contacto`; C: `confirmacion-agenda` nodos `Agendan cita = true` y `Crear contacto`). **No se aplicaron — descartado el 2026-08-04.**
- `03_workflows/formulario-clientify-venttur-v1.json` — Workflow Formulario Clientify (webhook landings → Airtable + Clientify + tag por programa). **2026-06-06 fix en prod:** nodo `Etiquetar Contacto` — URL pasa a expresión con `isExecuted` que toma el id de la rama del IF `es vacío` que efectivamente corrió (`Crear Contacto Clientify` lead nuevo / `Crear Contacto Clientify1` lead repetido). Resuelve "Node hasn't been executed" cuando el lead ya existía en Clientify. JSON local sincronizado. Detalle: `06_docs/fix-etiquetar-contacto-isexecuted-2026-06-06.md`.
- `03_workflows/outreach-form-meta-venttur-v1-pre-sheets-migration.json` — **Snapshot del workflow VIVO al 2026-06-17** (19 nodos, active=true, **solo Touch 1** con webhook receptor `vtr-form-meta-outreach` — NO tiene tri-toque, descubrimiento al comparar repo vs n8n vivo). Sirve como base de rollback antes de la migración a Sheets Trigger.
- `03_workflows/outreach-form-meta-venttur-v1.json` — Backup del workflow Outreach (LIVE 2026-06-13 con solo Touch 1; tri-toque committed al repo 2026-06-16 pero nunca deployado). workflowId `CUuFxbst3iHpgeXS`.
- `03_workflows/outreach-form-meta-venttur-v2.json` — **Workflow Outreach v2 — Sheets Trigger + tri-toque + 8 campos cualificación** (smoke tests OK 2026-06-22, pendiente activación + monitoreo 48h). 25 nodos, 21 conexiones. Cambios principales: (a) Webhook + Respond rápido eliminados; nuevo `Sheets Trigger - Form Meta Sync` con event=rowAdded estricto, polling 1min, valueRender=UNFORMATTED_VALUE, sobre docID `1HzJVMBwnGikiI_U805N7oqcXPYE7TjEFTL1rqdcCEIU` sheet `Boarding_Schools_Venttur_2026-test-2` gid 160362675. (b) Normalize Payload reescrito con loop `$input.all()`, helpers `stripMetaPrefix`/`parsePhone`/`splitName`/`deriveTipo`/`deriveFuente`, manejo de 3 formatos de phone_number incluido edge case `p:MX` + whatsapp vacío → rama `_error` con shape `{_error, _error_reason, _meta_lead_id, _row_number, _raw_row}`. Sin default country code (los del sheet ya vienen con CC). `deriveTipo` devuelve `Padre/Madre` (genérico, granularidad papá/mamá vive en Ad Name). `deriveFuente` mapea platform ig→Instagram, fb→Facebook. (c) IF `(_error?)` post-Normalize: rama TRUE → Execute Workflow `webapp_errors` (id `OBkUyb8fuo30DzA9`) shape plano (workflow_id/name + execution_id/url + error_message/stack), FIN sin loop; rama FALSE → Split In Batches Flujo A (batchSize 1) → Buscar Lead Existente. (d) Buscar Lead Existente filtra por `OR({Folio}=meta_lead_id, {Telefono}=telefono)` con fields incluyendo Folio + Outreach Form Meta enviado + Toques enviados + ID Manychat + Agendan cita + Estado conversación. (e) Crear Lead Nuevo cambiado de `create` a `upsert` con `matchingColumns=["Folio"]` (idempotencia hard). Mapping con 18 campos incluyendo los 8 nuevos: Nombre/Apellido/Telefono/Email/Programa interés=Boarding School/Origen=Form Meta/Outreach Form Meta enviado=false/Contestan 1er mensaje=false/Folio=meta_lead_id/Fuente lead/Tipo=Padre/Madre/Ad Name/Platform/Grado Escolar/Inicio Deseado/Nivel Inglés/Toques enviados=0/Touch 1 programado at. (f) IF gate `¿Lead seguro actualizar?` antes de Actualizar Lead Existente con conditions `Outreach Form Meta enviado ?? false === false` AND `Toques enviados ?? 0 === 0` (coalescing porque Airtable no devuelve campos checkbox unchecked en el response). Solo si gate=TRUE → Actualizar Lead Existente con mapping solo de campos inmutables (id_2/Folio/Origen/Ad Name/Platform/Grado Escolar/Inicio Deseado/Nivel Inglés). NUNCA toca Toques enviados/Outreach Form Meta enviado/Última actividad/Estado conversación. (g) Tri-toque del Flujo B heredado del repo v1 tri-toque: Cron 5min → Get Leads Pendientes con `filterByFormula` reescrito usando `Touch 1 programado at` (`AND({Origen}='Form Meta', NOT({Agendan cita}), {Última actividad}=BLANK(), {Toques enviados}<3, {Touch 1 programado at}, OR(AND({Toques}=0, IS_AFTER(NOW(), {Touch 1 prog at})), AND({Toques}=1, IS_AFTER(NOW(), DATEADD({Touch 1 prog at}, 24, 'hours'))), AND({Toques}=2, IS_AFTER(NOW(), DATEADD({Touch 1 prog at}, 72, 'hours')))))`) → Split (1) → Switch por Toques enviados → 3 ramas (rama 0 createSubscriber + sendFlow Outreach Boarding Form `content20260612151152_969589`, rama 1 sendFlow Touch 2 `content20260616231914_193459`, rama 2 sendFlow Touch 3 `content20260616231947_185709`) → ¿Subscriber OK? (solo rama 0) → Marcar Enviado / Log Error → Registrar Error Supabase. (h) Credencial nueva `Google Sheets - Venttur Meta Sync` (Google Sheets Trigger OAuth2 API, cuenta OWNER del sheet, scopes spreadsheets.readonly + drive.readonly). Smoke tests ejecutados (Pin Data en nodo Sheets Trigger, execute step por nodo): Caso A (happy path lead hot preparatoria+agosto_2026+avanzado) ✅ Lead Score=100, Tipo lead=hot, Touch 1 programado at=NOW()+1h, todos los campos correctos. Caso B (edge case p:MX + whatsapp vacío) ✅ rama _error→sub-flujo webapp_errors, no se creó row Airtable. Caso C (dedup por Folio, mismo lead_id) ✅ match por Folio, IF gate=TRUE (post-fix coalescing), Actualizar Lead Existente solo toca inmutables. Caso D (lead ya procesado con Outreach=true y Toques=1) ✅ gate=FALSE, no se ejecutó Actualizar, estado protegido. Bugs corregidos durante smoke: (1) `deriveTipo` devolvía 'Padre'/'Madre' separados pero campo Airtable solo acepta 'Padre/Madre' → fix devuelve genérico, granularidad en Ad Name; (2) IF gate fallaba en Caso C porque Airtable no devuelve checkbox unchecked → fix `?? false` y `?? 0` para nullish coalescing. 2 flujos en un workflow: (A) webhook receptor `vtr-form-meta-outreach` que recibe leads del Form Meta y hace upsert en Airtable Leads (dedup por teléfono, normalización E.164 con default AR, marca `Origen=Form Meta` + `Contestan 1er mensaje=false` + `Outreach Form Meta enviado=false` + `Toques enviados=0` + defaults `Fuente lead=Facebook - Instagram`, `Folio=N/A (Form)`, `fbclid=-`); (B) cron cada 5 min que levanta leads pendientes (filterByFormula: Origen=Form Meta + no agendó + Última actividad BLANK + `Toques enviados < 3` + cadencia tri-toque desde `CREATED_TIME()` del form: 5min/24h/72h). Switch por `Toques enviados` enruta a 3 ramas: rama 0 (Touch 1) → `createSubscriber` ManyChat (con `consent_phrase`) → `sendFlow Outreach Boarding Form` (flow_ns `content20260612151152_969589`, template MARKETING `boarding_form_followup` es_MX); rama 1 (Touch 2) → `sendFlow` directo (flow_ns `content20260616231914_193459`) usando `ID Manychat` ya guardado; rama 2 (Touch 3) → `sendFlow` directo (flow_ns `content20260616231947_185709`). `Marcar Enviado` incrementa `Toques enviados`, setea `Ultimo toque at`, preserva `Outreach Form Meta enviado at` original. Rama de error: nodo `Log Error` + `Execute Workflow` al sub-flujo de registro de errores (shape plano `workflow_id`/`workflow_name`/`execution_id`/`execution_url`/`error_message`/`error_stack` → Set reconstruye nested → Supabase `workflow_errors`). Bearer ManyChat migrado a Credential `Venttur Header Auth account` (id `9OZtsIsmuVEG9l6R`). Permiso `wa_id` import confirmado activo sin requerir ticket.
- `06_docs/outreach-form-meta-implementation-guide.md` — **Guía de implementación Outreach Form Meta**. 11 secciones + mapeo de campos Airtable por nodo. Decisiones cerradas: delay 1h (D1), 1 toque (D2), MARKETING (D3 — Meta rechazó utility, requiere opt-in explícito), AR default (D4). Caveat técnico documentado: `Última actividad` NO se setea desde este flujo (es del lead). Trade-off: leads que reciben outreach y nunca responden quedan en `Estado conversación = BLANK`. Sugerencia opcional para modificar `wf-estado-interrumpida-venttur` para considerar `Outreach Form Meta enviado at` como proxy.
- `03_workflows/outreach-form-meta-backfill-v1.json` — **Workflow one-shot manual** (17 nodos) que corrimos 2026-06-23 para enviar Touch 1 a los leads `lead_status=CREATED` del Google Sheet de Form Meta. El Sheets Trigger del v2 no los procesó porque la conexión se hizo después de su inserción. Topología: Manual Trigger → Get All Sheet Rows → Filter CREATED → Normalize Payload (mismo JS que v2) → Split In Batches (1) → IF (_error?) → Airtable Upsert (Folio matching) → createSubscriber ManyChat → ¿Subscriber OK? → sendFlow Touch 1 (flow_ns `content20260612151152_969589`) → Marcar Enviado → Sheets Marcar contacted → Wait 1.5s → loop. Idempotente por Folio + id_2 + id del sheet. **Después de correr este backfill, bulk-edit en Airtable Leads filtrando `Origen=Form Meta` + `Outreach Form Meta enviado=false` + `Touch 1 programado at!=BLANK`** para setear: `Toques enviados=1` (único bloqueante del cron del v2), `Outreach Form Meta enviado=true`, `Outreach Form Meta enviado at=NOW`, `Ultimo toque at=NOW`. **NO setear** `Última actividad` ni `Agendan cita` (el cron las usa como guard de exclusión). **Recuperar `ID Manychat` de ManyChat dashboard** para los leads sin ese campo (Touch 2/3 lo leen via `$json['ID Manychat']`, sin él fallan).
- `03_workflows/outreach-form-meta-backfill-v2.json` — **Backfill v2 con memoria sintética** (21 nodos = v1 + 3 nodos post-`Marcar Enviado`). Agrega: (a) `Build Memory Texts` (Code) que arma 2 mensajes desde lead data — uno `system` con prosa natural ("El lead María García (...) completó un formulario de Meta interesada en Boarding School para preparatoria con inicio deseado en agosto_2026 y nivel de inglés intermedio. Vino por la campaña BS_MAMAS_TEST1 en ig.") y uno `ai` con texto del Touch 1 renderizado con `{{first_name}}` reemplazado por `Nombre`; (b) `Insert system FORM (idempotent)` Postgres node con `INSERT ... WHERE NOT EXISTS` para idempotencia; (c) `Insert ai Touch 1` Postgres node simple insert. SessionKey = `Telefono` sin `+` (debe matchear `venttur-main:33-34` exacto). Credencial Postgres `Venttur` (id `ihpvM7nYMdLCwWDP`). El nodo `memoryPostgresChat` v1.3 del main carga estos 2 mensajes como turnos anteriores cuando el lead responde → agente no re-saluda ni repregunta nombre. **TODO antes de import:** reemplazar el placeholder `TOUCH_1_TEXT` del Code node con el texto literal de Meta del template `boarding_form_followup` (copy/paste desde ManyChat Flow editor).
- `06_docs/template-texts-canonical.md` — **Doc fuente de verdad** de los 15 templates que el sistema envía al lead (3 outreach Touch 1/2/3 + 12 rescate post-link). Los textos de los 12 rescate están literales (copiados de `rescue-flow-message-templates.md`); ✅ **los 3 outreach también quedaron cargados literales el 2026-08-04** (antes vivían solo en Meta Business Manager / ManyChat Flow editor, sin versionar). Plantilla del mensaje `system` con prosa natural + pseudocódigo del builder (función `buildSystemMessage`) con reglas de omisión elegante para campos vacíos. Mapping `Programa interés` → texto Rescate Fase 1/2 por programa.
- `06_docs/guia-implementacion-memoria-sintetica-2026-06-23.md` — **Guía paso a paso** para los EDITs en n8n vivo: outreach v2 (`CUuFxbst3iHpgeXS`) agrega 3 nodos post-`Marcar Enviado` Touch 1 + 1 nodo post-`Marcar Enviado` Touch 2 + 1 nodo post-`Marcar Enviado` Touch 3. Rescate post-link (`mkEP1qFN7MVb9qP0`) agrega `Build Rescate Memory (Fase 1)` Code centralizado con mapping por programa → `Insert system FORM` idempotente → `Insert ai Rescate Fase 1` + idem para Fase 2 (sin system insert, ya existe). Incluye 4 smoke tests S1-S4 + rollback SQL + checklist de implementación.
- `03_workflows/backfill-vtr-chat-memory-v1.json` — **Workflow n8n one-shot manual** que carga memoria histórica para leads ya contactados pero sin chat history. Topología: Manual Trigger → Airtable Search Leads (filterByFormula `AND({Outreach Form Meta enviado}=TRUE(), {Telefono}!=BLANK())`, retorna 19 fields del lead) → Split In Batches (1) → Build Context (Code: normaliza Telefono → sessionKey strip non-digits, extrae Toques enviados + outreach_at_iso) → IF (phone válido?) → Postgres Check Session Exists (`SELECT COUNT(*) AS row_count FROM n8n_chat_histories WHERE session_id=$1`) → IF (sesión vacía?) → Build Messages (Code: arma 2-4 items por lead — system con prosa natural + ai_touch_1 + ai_touch_2 si Toques>=2 + ai_touch_3 si Toques>=3, timestamps inferidos +0/+24h/+72h desde `Outreach Form Meta enviado at`) → Postgres Insert Message (corre N veces, 1 por mensaje, `INSERT INTO n8n_chat_histories (session_id, message, created_at) VALUES ($1, $2::jsonb, $3::timestamptz)`) → Wait 0.5s → loop. Idempotente vía Check Session Exists. **Cero acceso directo a Supabase** — usa credenciales n8n ya cableadas: Airtable `Venttur Dashboard` (`[N8N_CREDENTIAL_ID]`) + Postgres `Venttur` (`ihpvM7nYMdLCwWDP`). 3 textos canónicos hardcoded en Code `Build Messages` (matchean texto literal de Meta del template `boarding_form_followup` + Touch 2/3). 12 nodos. Estimado 1500 leads × 0.5s = ~13 min ejecución completa.
- `scripts/utilities/backfill-vtr-chat-memory.py` — **REFERENCIA** del builder de prosa natural + textos canónicos. NO se usa para deploy (no hay acceso DB local al Postgres VTR). El deploy real corre por el workflow n8n `backfill-vtr-chat-memory-v1.json`. Útil para debug local de `build_system_message()` con un lead específico.

- `03_workflows/outreach-form-meta-venttur-v4.json` — **Outreach v4 — fix Touch 1 sin delay (2026-06-27).** Único cambio vs v3: el `Normalize Payload` (Code JS, Flujo A) ahora setea `const touch1At = new Date().toISOString();` (antes `Date.now() + 60*60*1000`). Diagnóstico disparado por caso Haseira (lead creado 3:18 ART, cron a 3:20 no la pickeaba): el +1h del Normalize bloqueaba al lead 1h post-creación combinado con el filtro `IS_AFTER(NOW(), {Touch 1 programado at})` del `Get Leads Pendientes`. Ahora el Cron pickea en el próximo ciclo de 5 min post-creación. Touch 2/3 caen ahora a +24h/+72h desde la creación (antes +1h+24h / +1h+72h). Validado E2E con lead Enrique: Trigger → Normalize `touch_1_programado_at: 2026-06-27T20:57:56.003Z` (sin offset) → Crear Lead Nuevo escribe `Touch 1 programado at: 20:57:56.003Z` (passthrough limpio). Guía actualizada: `06_docs/guia-implementacion-trigger-sheets-2026-06-17.md` líneas 27/333-334/504/711 reflejan el nuevo comportamiento (riesgo race condition trigger vs cron rebajado de 🔴 critical a 🟢 mitigada).
- `03_workflows/outreach-form-meta-venttur-v3.json` — **Snapshot del outreach v3 vivo al 2026-06-23 PM** (52 nodos = v2 + memoria sintética). Mantiene v2 íntegro (Sheets Trigger + tri-toque + 8 campos cualificación + IF gate + rama `_error`) y agrega después de cada `Marcar Enviado` del Flujo B la cadena de memoria: rama 0 (Touch 1) tiene `Build Memory Texts (Touch 1)` → `Insert system FORM (idempotent)` (Postgres con `INSERT ... WHERE NOT EXISTS` por `message->>'type'='system'`) → `Insert ai Touch 1`; ramas 1 y 2 (Touch 2/3) tienen `Build Memory Texts` → `Insert ai Touch N` (sin system FORM, ya existe del Touch 1 previo). Postgres credential `Venttur` (id `ihpvM7nYMdLCwWDP`) cableada. SessionKey = `lead.Telefono` directo (Code lee `$('Split In Batches (1)').item.json.Telefono`). El `memoryPostgresChat` del main carga los mensajes sintéticos como turnos previos cuando el lead responde → agente no re-saluda ni repregunta nombre. **Issue cosmético detectado:** un nodo del v3 está nombrado `Insert ai Touch ` con espacio al final (falta el "1") — no bloquea ejecución pero conviene renombrar.
- `03_workflows/wf-rescate-post-link-v2.json` — **Snapshot del rescate v2 vivo al 2026-06-23 PM** (23 nodos = v1 + memoria sintética). Mantiene v1 íntegro (Wait 45min + 1er check + IF agendó + Code Fase 1 + setCustomFields + sendFlow Fase 1 + Wait 24hrs + 2do check + IF agendó + Code Fase 2 + setCustomFields + sendFlow Fase 2 + addTag LINK_ABANDONADO_FRIO + 2 telegram notifs). Memoria cableada en paralelo a los `sendFlow`: Fase 1 → `Build Rescate Memory (Fase 1)` (Code centralizado con mapping por programa, emite system_message + ai_message) → `Insert system FORM (idempotent)1` → `Insert ai Rescate Fase 1`; Fase 2 → `Build Rescate Memory (Fase 2)` (Code solo con ai_message, NO emite system) → `Insert ai Rescate Fase 2` (sin Insert system FORM intermedio porque ya existe). Postgres credential `Venttur`. **Issues detectados a fixear** (no bloqueantes pero romperán ejecuciones cuando el flujo dispare en prod): (1) `Build Rescate Memory (Fase 1)` JS referencia `$('Get Lead').first().json` — ese nodo no existe en este workflow, el nodo Airtable real se llama `Airtable: 1er check`; (2) `Build Rescate Memory (Fase 2)` mismo issue — debe referenciar `$('Airtable: 2do check')`; (3) `Build Rescate Memory (Fase 1)` usa `{{first_name}}` en lugar de `[first_name]` (la convención del proyecto es `[first_name]` para no chocar con parser n8n; la Fase 2 ya está bien).

**Memoria sintética del agente (diseño cerrado 2026-06-23 · ✅ COMPLETA — cableada en outreach v3 + rescate v2, los 3 fixes menores se aplicaron el 2026-08-04):** resuelve re-saludo + re-pregunta de datos del form cuando el lead responde post-outreach. Cada workflow que dispara `sendFlow` ManyChat inserta 1-2 rows en `n8n_chat_histories` (sessionKey = `Telefono` sin `+`, mismo que el `memoryPostgresChat` del main) — un `system` con datos del form en prosa natural (idempotente vía `WHERE NOT EXISTS`) + un `ai` con texto del template enviado. **Cero cambios en `venttur-main` ni en el system prompt** — el nodo de memoria carga los mensajes sintéticos como turnos previos y el LLM no re-saluda ni repregunta naturalmente. Scope MVP: outreach v2 (Touch 1/2/3) + rescate post-link (Fase 1/2). Out: formulario-clientify (Form Landing), confirmación cita, seguimiento 48h, link asesoría, etiquetas. Plan completo: `/Users/camilo/.claude/plans/lexical-zooming-pond.md`. Riesgos conocidos: IG/FB-only sin teléfono comparten sessionKey vacío (bug pre-existente del main, fuera de scope); templates con texto que cambie post-aprobación Meta queda con texto viejo en memoria de leads ya logueados.

> ## 🆕 Reporte la agencia 1 (agosto 2026) — correcciones en curso · leer antes de tocar VTR
>
> Max entregó una auditoría sobre **245 conversaciones / 1.320 mensajes** de julio-agosto. Es la
> **fuente de verdad**: ante cualquier contradicción con el código o con este archivo, gana el reporte.
> Guía de aplicación: **`06_docs/guia-correcciones-reporte-agosto-2026.md`**.
> Rollback: **`03_workflows/vivo-2026-08-17/`** (14 workflows con sha256, tomados por API).
>
> **Causa raíz que el propio reporte nombra:** el agente **no recibe ningún estado del lead**. El User
> Message del nodo `Agente IA WPP` es sólo `Mensaje del usuario: {...}` + la fecha. No sabe si ya mandó
> el link, si el lead agendó, su programa, su origen ni sus datos del formulario.
>
> **Tres cosas que ningún análisis previo había visto:**
> 1. **La whitelist de links del dispatcher no incluye `promo.venttur.com/agendar-ema`** (el link de
>    Boarding y el fallback ante duda), y la instrucción fuerza `'cero'` para cualquier otro → **todo
>    lead que lo recibió entra al drip genérico por construcción**. Es el 64% del Hallazgo 2 y explica
>    por qué las plantillas que fallan son las `_bs` (Boarding School).
> 2. **`Hay audios?` es una condición imposible** (`and` + `audio[0] equals "webp"` sobre una URL de S3)
>    → la rama de transcripción **nunca corrió**; una nota de voz llega al agente como string vacío.
> 3. **`Repetido?` descarta mensajes en silencio** con un comparador desalineado (escribe mojibake
>    latin1, compara contra UTF-8) y su salida TRUE es rama muerta. Es el caso Omar Montes (H4).
>
> **H1 y H3 comparten causa:** `Agendan cita = true` se escribe **antes** del envío en
> `confirmacion-agenda`, y la cadena muere después con `Referenced node doesn't exist` (ejecución
> `1362988`, verificada). El lead queda marcado como agendado, sin confirmación y **excluido de todo
> seguimiento**. 2 de los 3 paths de asesor (Andrés y Diego) referencian nodos inexistentes.
>
> **Decisiones tomadas:** precio **con rango por programa** y cierre con fecha concreta (el prompt lo
> prohibía en 5 lugares) · **tope global de 2** toques por contacto · **cadencia de nurturing se muda
> de ManyChat a n8n** (`03_workflows/vtr-despachador-proactivo-v1.json`).
>
> ⚠️ **Corrección a este archivo:** los EDITs de estado de leads **NO fueron descartados** el
> 2026-08-04. `Estampar estado (Contestó)` está vivo y habilitado en el main, y `b52CUYEkI2Ah3Xj6`
> tiene 18 ejecuciones exitosas. El `Estado conversación` al 5% del CSV se explica porque ese export
> es del 2026-07-24, anterior al cableado.

**Migración GHL en curso:** `00_migracion_ghl/` contiene el análisis completo del sistema actual para migrar a GHL. Incluye `ESTADO_MIGRACION.md` (estado global), `00_inputs/` (checklist + snapshot de datos + 14 workflows), y `01_logica_actual/` (6 documentos: mapa funcional, triggers y eventos, ciclo de vida lead, catálogo mensajes, reglas negocio, redundancias). **Etapa 1 completa — los 6 docs REESCRITOS y enriquecidos ~4-8× el 2026-08-07** con los inputs completos de Etapa 0 (14 workflows analizados nodo-por-nodo vía orquestación multi-agente + system prompt del agente "Mauricio" + snapshot de datos de las 5 plataformas + 6 CSVs). Corrigen el error grave de mayo ("no hay agente IA" → sí hay un agente conversacional "Mauricio" gpt-4o como núcleo) y suman los subsistemas que faltaban (rescate/outreach/estado/nurturing ya LIVE). Hallazgos confirmados desde los JSON (ver ESTADO_MIGRACION §"Hallazgos de Etapa 1"): rama CTWA hardcodea `{Programa}='BS'` (no usa `programa_wpp`), tool `contestan_2do` fantasma, sessionKey del main no normaliza el quirk MX 52→521, "Estudio y Trabajo" código muerto en rescate, doble grafía Boarding School/Boarding IA, secretos hardcodeados, flow "Elevar" con "Notify Assignees: 0". **Etapa 2 CASI CERRADA (2026-08-18) — respuestas del cliente integradas.** Mauricio García confirmó el cuestionario el 2026-08-17; `02_validacion_cliente/cuestionario-venttur-2026-07-24.md` es ahora el **registro firmado** (ya no un cuestionario en blanco), el máster interno `preguntas-cierre-2026-07-24.md` tiene A1..A11 volcadas, y los 6 docs de `01_logica_actual/` llevan un bloque "🆕 Validación con el cliente" con lo que les cambia. **Etapa 0 casi completa (18/8 PM):** 3 de 4 datos del canal WA recibidos (número `+52 1 33 2627 4502` de Venttur, WABA ID `1931874540684022`). Falta desambiguar si ese WABA está bajo el Business Manager de Venttur (portable) o de ManyChat (no portable, escenario Collazo). Verificación de 2 min en `business.facebook.com` y **Etapa 3 se desbloqueó**. **Cutover confirmado: 15/9/2026.** ⚠️ **Trampa de versiones:** el cliente respondió la versión de **12 preguntas** enviada el 7/8; el archivo del repo se había adelantado a **14** el 17/8 (commit `d7ac607c`) agregando *rangos de precio* y *qué significa "Cerrada"* — **esas 2 nunca salieron y siguen sin responder**. Decisiones del cliente que cambian el diseño: 8 programas canónicos (Pathway es solo Alemania · Gap Year = Estudia y Trabaja · **Francia es destino, no programa**; los destinos van como nota, nunca como campo) · **Diego sale del ruteo automático** (su path roto en `wf-confirmacion-agenda` se borra, no se repara) · **8 calendarios GHL, uno por programa**, con disponibilidad compartida por asesor · **el agente NUNCA asume el programa** ni con origen evidente (atribución automática y conversación se separan) · **Clientify se apaga y migra completo** (6.968 contactos + 2.338 deals + 266 companies, 1:1, etapas manuales) · **un solo número** para conversación, confirmación y recordatorios · reporte semanal solo con **citas agendadas**. **2 hallazgos nuevos:** (a) 🚨 **hay DOS números de WhatsApp en operación** — ManyChat (agente) y **Clientify (recordatorios de cita)**, lo que explica por qué los recordatorios "existen" para el cliente pero no aparecen en ninguno de los 14 workflows: viven fuera de nuestro perímetro; (b) 🚨 **3 de los 8 programas no existen en el sistema** — `Viajes educativos` y `Educación superior` tienen 0 hits en todo el cliente y `Cursos de idiomas` solo un link suelto: hoy un lead que pregunta por Educación superior cae al fallback `agendar-ema`, o sea el link de **Internados con Rodrigo** (programa y asesor equivocados). Ronda 2 CERRADA (18/8 PM). Definido: (a) "Cerrada" al reabrir = el bot atiende normal sin sobreescribir programa ni disparar nurturing; (b) recordatorios pre-cita 24 h + 1 h; (c) confirmación con fecha/hora/asesor/link; (d) multi-programa = el bot pregunta/sugiere; (e) 3 huérfanos con tratamiento completo (scope grande); (f) Clientify migra en su totalidad; (g) cutover completo el 15/9 (presiona la fecha). Único sin definir: rangos de precio de los 3 huérfanos ("-" → no cotiza, pasa a asesoría). Ver `02_validacion_cliente/puntos-abiertos-ronda-2-2026-08-18.md`. **Prioridad #1 — revisión de portabilidad del número: DIAGNÓSTICO HECHO (2026-08-18)**, `06_docs/portabilidad-numero-whatsapp-2026-08-18.md`. GHL soporta migración BSP nativa sin recrear la WABA, preservando número, display name, calidad, límites de mensajería, OBA y plantillas; downtime de minutos. Todo depende de una pregunta sin responder: **si el número lo proveyó ManyChat NO es portable** (son de un solo uso). **El cliente decidió quedarse con el mismo número y descartó comprar chip** — decisión de preferencia, no de factibilidad: no elimina el riesgo, elimina el plan B. Corte propuesto: si al 1/9 no está confirmada, chip nuevo. **El número de Clientify muere con Clientify y no se avisa** (decisión 18/8). Mapeo: ManyChat → GHL Conversations, Clientify → GHL CRM, Airtable Leads → GHL Contacts, n8n CAPI se mantiene. **✅ Etapa 3 (diseño de arquitectura GHL) COMPLETA (2026-09-01):** los 12 docs de `03_arquitectura_ghl/` (00-11) materializan ese mapeo campo por campo con el método quirúrgico de HPF, verificados adversarialmente en 3 rondas — ver `ESTADO_MIGRACION.md` §"Etapa 3" y el pendiente #2 abajo. Etapa 4 (guía paso a paso) desbloqueada.

> ## 🚀 Cutover WABA → GHL · WhatsApp a la hora H que fija la agencia · DNS de promo a la hora T de la agencia · LEER ANTES DE TOCAR VTR
>
> **Revisión 24/9: el agente no mandaba el link (reporte de Mauricio).** Causa: el `[ESTADO DEL LEAD]` del main GHL decía `Cita: AGENDADA (no le vuelvas a mandar el link)` por un flag `agendan_cita` importado de Clientify, sin cita real en GHL, y además la memoria de ManyChat no se veía (N1). Aplicado y verificado en `1eS1Z5k898c3ATnf`: (1) el estado usa las citas reales de GHL (nodo `GHL · Citas (estado)`: con fecha, pasada o sin fecha); (2) prompt v2.3 con las reglas "Reagendar = mandar el link" y "No inventes nada sobre la cita"; (3) N1 cerrado, más el remanente de 12 sesiones sin lada; (4) prompt en tuteo. Suite gpt-4o: 12/12 contra el vivo (baseline 5/9). Detalle y rollback: `03_workflows/ghl-live-2026-09-24-agente-link/README.md` · prompt `04_agents/agente-venttur-system-prompt-v2.3.md`.
>
> **Revisión 23/9 noche (manda sobre todo lo de abajo):** ✅ **WhatsApp ya está en GHL** (BSP hecho ~16:00 CDMX: cuenta de WhatsApp NUEVA "Venttur Education and Travel", número verificado, calidad Verde; la WABA vieja `1931874540684022` quedó con el número "Transferido"). Stack nuevo ON, stack viejo del agente OFF (B6). La guía raíz se simplificó a **próximos pasos N1-N5** + B5/D/E. Abiertos críticos: N1 memoria de conversaciones viejas (claves `521…` vs `+521…`, UPDATE pendiente de OK), N2 los 6 templateId del despachador cambiaron con el traspaso (Form Meta sin primer toque hasta cargarlos), N5 W14 cuenta 0 citas. Alertas VTR → Telegram `6390727286` (el `-4925599962` es de HPF).
>
> **Revisión 23/9 tarde (manda sobre todo lo de abajo):** el main nuevo no respondía ningún mensaje (dedup sin salida + entrada leyendo campos de ManyChat + envío vacío). Parcheados 7 workflows del stack nuevo (`batches-2026-09-23/vtr_pre_bsp_fixes.py`, guía A11). La pausa del bot ahora es el tag `bot_pausado` (no DND). Falta la prueba E2E del main (A12) antes del BSP.
>
> **Revisión 23/9 (manda sobre lo de abajo):** el traspaso de WhatsApp **ya no espera al DNS**. Mientras `promo` siga en Clientify, el agente manda los mismos links en `vtr.[TU-DOMINIO]` (`dominio-links-agente.py --a vtr`, en B2; `--a promo` en B5). 23 flujos de Rodrigo ya **publicados**; WF-01/WF-02/WEBHOOK en **borrador**; TTL de `promo` todavía 4 h (sólo frena B5 y el apagado de Clientify). **H = 23/9**: Max tiene el chip y el traspaso se hace ese día. Aventureras sigue activo (Max, 23/9).
>
> **Revisión 22/9 noche (antes de leer lo de abajo):** hallazgos que cambian el plan — (1) los **23 flujos de Rodrigo están en BORRADOR** en GHL; (2) **WF-01 / WF-02 / WEBHOOK** publicados pueden duplicar el inbound post-BSP; (3) el **import a GHL salió de exports del 10/7 y 24/7**: faltan ~350 contactos, ~100 deals nuevos y ~150 deals movidos (gate D1 antes de apagar Clientify); (4) el **TTL del CNAME `promo` es 4 h** (bajarlo antes del flip); (5) el despachador mandaba los 2 toques con 1 h de diferencia (política corregida por `vtr_post2_despachador.py`); (6) 195 paths de Clientify quedaban en 404 → redirects por API GHL (`crear-redirects-ghl.py`). **Landings: se publican en GHL Funnels** (no Vercel), código listo en `landings-ghl/_ghl/` + `MANIFEST.md`. (7) El TTL que se bajó el 22/9 fue el de `vtr.[TU-DOMINIO]`; el de `promo.venttur.com` (zona venttur.com, otra cuenta Hostinger) sigue en 4 h.
>
> **Estado al 2026-09-22 (fin del día):** Batches A/B/C.1/D/F.1/F.2 ✅ aplicados por Claude (todo OFF esperando CUTOVER-2 salvo el patch A al productivo `k3aivKSP67S97IHn`). PREP-1 a PREP-4 ✅ cerrados por la agencia. Decisiones cliente 8/9 cerradas (única abierta: D7 precios/textos programas huérfanos, con default aplicado).
>
> Fuentes de verdad (leer en este orden):
> 1. **Prompt de continuación técnica**: `PROMPT-CONTINUACION-CODEX.md` (raíz repo) — estado real actualizado + bloqueantes + credenciales por nombre. Pegarlo en una sesión nueva de Claude Code para retomar.
> 2. **Guía de ejecución paso a paso (ÚNICA)**: `guia-recta-final-ejecutable-2026-09-20.md` en la **raíz del repo** — revisada el 22/9 noche contra el estado vivo. La copia de `06_docs/` es sólo un puntero. **Cutover = día y hora que confirme la agencia para cambiar el CNAME de `promo`** (desde jue 24/9 09:00 CDMX; ya no jueves 09:30 ART fijo). Orden Fase B: B0 → B1 `--solo-on` (**sin rescate**) → B2 → agencia cambia CNAME → B5 `--landings-on` (W4 + CAPI + **rescate**) → B3 BSP → B4 → B6 `--solo-off` → B7 → +4 h `--landings-off`. Motivo: con B3 antes de B5 el lead agenda en Clientify y el rescate/despachador le escriben "no agendaste". Si la agencia no puede: **Plan B** (WhatsApp solo; rescate OFF y despachador sin envío hasta B5; Clientify no se apaga sin B5 = gate D4). Fases C (POST) → D (gates: delta, presupuestos, cero Clientify, B5) → E (cierre).
> 3. **Decisiones cliente**: `clients/VTR_Venttur/06_docs/decisiones-cliente-cutover-2026-09-24.md` — 8/9 cerradas, solo D7 abierta.
> 4. **Batches 2026-09-22**: `03_workflows/ghl-live-2026-09-22-batch-{A,B,C,F}/README.md` — detalle técnico + sha256 de cada batch aplicado.
>
> **Workflows nuevos creados 22/9 (OFF hasta CUTOVER-2):** `main-venttur-ghl` `1eS1Z5k898c3ATnf` + sub-workflow `vtr-tool-elevar-ghl` `v9XkOfL9dQtY2wyv`. Templates cableados en despachador `vrShEXQGGAo4FqAt` (6 IDs de Camilo confirmados). sessionKey `+521<10>` unificado en rescate `YB0UxwEVwzISdd54` + despachador.
>
> **Bloqueantes abiertos:** W4/W9/W10 (construir en n8n UI · specs en batch-C README) · W6 (construir post-OAuth §PAR-E · ahora desbloqueado) · ~~landings~~ ✅ **50 landings creadas en GHL el 22/9** (funnel único `LP · Calendarios` en `vtr.[TU-DOMINIO]`, cargador + JSON, tuteo mexicano, 205 redirects ensayados; A3b ensayado con `vtr2.[TU-DOMINIO]`: enlazar el dominio deja las landings sirviendo en ~1 min, pero **sólo en el dominio principal** (corregido 23/9; los otros redirigen a `<principal>/programas`) → B5 suma el puente `crear-redirects-ghl.py --puente`; queda sólo B5 el día T) · revocar OpenAI key vieja `sk-proj-OpKR…` en dashboard · rotación 10 keys `.env` agendada semana 2026-09-29.
>
> Plan estratégico original: `planes/la-gu-a-recta-final-snug-aurora.md`. Snapshots de rollback: `03_workflows/ghl-live-2026-09-21-ejecucion/` + `vivo-2026-09-21-preventivo/`. Registro canónico n8n: `06_docs/pendientes-n8n-post-waba.md`.

**Pendientes VTR — revisados al 2026-08-04:**

*Abiertos:*
1. ~~**Confirmar códigos de programas CTWA + crear los keyword triggers en ManyChat.**~~ ❌ **OBSOLETO
   (2026-08-18).** El cliente decidió que el agente **nunca** deduzca el programa del anuncio: la
   atribución va automática por el referral de Meta y el programa sale del descubrimiento
   conversacional. Sumado a que ManyChat se reemplaza por GHL, el mapeo keyword→programa deja de
   existir como pieza.
2. **Migración a GHL — ✅ Etapa 3 (diseño de arquitectura GHL) COMPLETA (2026-09-01).** Los **12 docs
   de `00_migracion_ghl/03_arquitectura_ghl/`** (00-11) traducen 1:1 el sistema actual al stack
   n8n+GHL con el método quirúrgico de HPF, **verificados adversarialmente en 3 rondas** (fidelidad de
   datos con jq/python contra el snapshot y los CSVs + método + consistencia con las decisiones del
   cliente). Corrección material atrapada: los deals de Clientify están en **~19 pipelines, no ~10**
   (80% Expired). Índice + outcomes en `ESTADO_MIGRACION.md` §"Etapa 3". **Etapa 4 (guía paso a paso)
   desbloqueada.** Lo que queda antes/durante la Etapa 4:
   (a) 🔴 **resolver las 10 asunciones de plataforma GHL a validar en sandbox** (`03_arquitectura_ghl/00_overview.md`
   §7.10) — dedup por teléfono, fechas históricas, disponibilidad compartida entre calendarios, Contact
   Reply trigger, free-form send, template por API, media de audio, pausar bot por-contacto, query de
   Contacts por custom field, trigger de booking — **antes del import**;
   (b) 🔴 **revisión de portabilidad del número** — pedido #1 del cliente, único punto que depende de un
   tercero (ManyChat + Meta); deadline propio 1/9 o chip nuevo;
   (c) 🔴 **auditoría de migrabilidad de Clientify** antes del apagado (gate que pidió el cliente);
   (d) 🟡 **2 decisiones de la agencia pendientes de OK del cliente:** tope global de 2 toques + prioridad
   entre secuencias (`09` §8), y "lo escribe el agente al cerrar el descubrimiento" para `Cualificado`
   (`03` §5).
3. **Revisar el pago doble** — consultar con **Mauricio (el de Venttur, hijo)**. Confirmado el
   2026-08-05: el pendiente es de Venttur y el interlocutor es Mauricio, no Max. Ver el aviso de
   nombres duplicados al inicio de esta sección.
4. **3 campos Airtable a confirmar con Max** (`Fuente lead`, `Tabla métricas`, `Reporte semanal` —
   default seguro = no setear).
5. **Inputs faltantes — ✅ línea obsoleta, corregida el 2026-08-18.** Verificado: los exports de
   ManyChat (20 archivos), los 6 CSVs de Airtable y los 3 workflows (Formulario Clientify + CAPI
   Registro Folio + Outreach Form Meta) **están todos en `00_migracion_ghl/00_inputs/`** desde el
   2026-07-24. El acceso a GHL está **diferido a propósito** (la sub-account se crea cuando el mapa
   esté definido). **Lo único realmente faltante son los 4 datos del canal de WhatsApp** (número del
   bot, quién lo proveyó, WABA/Business Manager, verificación de negocio) — ver
   `06_docs/portabilidad-numero-whatsapp-2026-08-18.md` §7.

*Cerrados el 2026-08-04:*
- ✅ **3 fixes menores de la memoria sintética** aplicados — el cableado de outreach v3 + rescate v2
  queda completo.
- ✅ **Textos literales de los 3 templates de outreach cargados** en `06_docs/template-texts-canonical.md`
  (ya no viven solo en Meta Business Manager / ManyChat).

*Descartados el 2026-08-04:*
- ❌ **Los 3 EDITs en n8n vivo del reporte de estado de leads** (`06_docs/estado-leads-implementation-guide.md`)
  y los 2 campos Airtable asociados. El diseño queda documentado, no se aplica.
- ❌ **Monitoreo del delivery rate de Rescate Fase 2 (~25 hs).** No se persigue.

*Contexto vigente:* **outreach proactivo WA** ✅ LIVE desde 2026-06-13, hoy en v4 con tri-toque +
Sheets Trigger + 8 campos de cualificación. **Rescate Post-Link** ✅ en producción.

---

### CLZ — Collazo Servicio Técnico (`clients/CLZ_Collazo/`)

Agente conversacional que responde consultas, detecta el servicio necesario (aires, calefones, electricidad) y guía al usuario a reservar via cal.com. Incluye seguimiento automático 8 hs post-conversación. **Nuevo (2026-06-10):** round-robin manual en n8n que reemplaza al de cal.com (que no funcionaba) y reparte los bookings entre Matías y Fabián moviendo el evento de calendar cuando le toca a Fabián.

**🆕 Migración de canal Chatrace → ManyChat (2026-06-30) — ❌ la recuperación del número viejo quedó descartada el 2026-08-04.** Se deja de perseguir la liberación de `+598 91339312`: el número operativo es el nuevo (092 665 505) y el broadcast de aviso cubre a los contactos históricos. Lo de abajo queda como registro del incidente.

**Detalle del incidente:** el número histórico de WhatsApp (+598 91339312) quedó bloqueado tras dar de baja la cuenta de Chatrace — Chatrace lo había registrado en una WABA propia (no en la del cliente), por lo que no había ningún "partner" que remover desde el Business Manager de Collazo. Gestiones en paralelo con Chatrace support (respuestas contradictorias, sin liberar el número), Meta Business Support (caso abierto, sin resolución) y ManyChat support (ticket escalando a Meta Partner Operations, pendiente respuesta) no destrabaron el número viejo. **Plan B ejecutado:** Matías activó un número nuevo y se conectó directo a la WABA existente de Collazo (ID `10111928183308888`) vía Embedded Signup de ManyChat — **regla crítica: nunca instalar WhatsApp/WhatsApp Business app en ese número**, Cloud API y app son excluyentes y repetiría el mismo bloqueo. n8n ya recableado a ManyChat. Bugs resueltos durante la integración: 401 "Wrong format token" en `setCustomFields` (faltaba prefijo `Bearer ` en la credencial), 400 "Value for number custom field" (`ai_msg_count` mandado como string en vez de number), `has_audio` con `.contains()` (no existe en JS, fix a `.includes('.ogg')`), links de reserva devueltos en markdown sucio `[texto](url)` (fix en dos capas: prompt con regla + ejemplo negativo, y guardrail determinístico por regex en el Code node), y reglas de corte de mensaje poco naturales en el nodo `Formatear mensaje` (reescrito para cortar como lo haría un humano en WhatsApp — nunca a mitad de una idea). Detalle completo: `06_docs/migracion-whatsapp-manychat-2026-06-30.md`. **Pendiente:** re-exportar `agente-collazo-main.json` completo desde n8n (el repo quedó desactualizado, la topología ManyChat tiene nodos nuevos — `Normalize Payload`, `setCustomFields`, `Build ManyChat Payload` — no reflejados en el JSON local); seguimiento de los casos abiertos para liberar el número viejo; actualizar canales públicos con el número nuevo si aplica.

**🆕 Zona de cobertura + fixes de prompt (2026-07-15):** Collazo pidió por audio agregar Villa García (Ruta 8, km 19) a las zonas cubiertas — el bot le había dicho a un cliente que no llegaban ahí. Prompt v1.5 → v1.7: (a) agregada la zona; (b) testing automatizado post-cambio detectó y corrigió 2 fallos preexistentes — el agente confirmaba qué zonas sí cubre antes de preguntar ante ciudades no cubiertas pero reconocibles (ej. Salto), revelando indirectamente que no llegan (fix: regla explícita de no mencionar zonas cubiertas al preguntar ubicación); y mencionaba proactivamente el costo de visita ($750) en consultas de "otros servicios" sin que se pidiera (fix: regla explícita). Ver `07_testing/testing-guide-v3.md`.

**Stack:** n8n + OpenAI GPT-4o + PostgreSQL (memoria + round-robin state) + ManyChat (canal WhatsApp, reemplaza a Chatrace) + cal.com + Google Calendar (Matías + Fabián)

**🆕 Notificación masiva de cambio de número (2026-07-31) — 🔸 PENDIENTE: correr el broadcast.** La plantilla ya está aprobada (2026-08-04); lo único que falta es ejecutarlo. workflow manual `clz-notificacion-cambio-numero-v1.json` que dispara la secuencia ManyChat `content20260731170830_999980` (plantilla ya aprobada por Meta) a los 426 contactos históricos de cal.com, avisando el nuevo número 092 665 505. Loop `createSubscriber` → `¿Subscriber OK?` → `sendFlow` con 1.5s de espera entre contactos, y un nodo `Resumen Final` que devuelve conteo de enviados/fallidos + detalle al terminar el loop (vía workflow static data, sin necesidad de Airtable/Sheets). **Split en 2 días (2026-07-31 PM):** ManyChat avisó que sin verificar la cuenta de WhatsApp Business el límite es 250 conversaciones iniciadas por la empresa cada 24hs — con 426 de un saque se pasaba. Se agregó el nodo `Config Envío (día 1 o 2)` (Set node con campo `dia_envio`) que hace que el nodo de contactos reparta la lista en 2 mitades exactas de 213 (`dia_envio=1` → primeros 213, `dia_envio=2` → restantes 213), cada una bajo 250 con margen. Se corre el workflow 2 veces (una por día, con 24hs de diferencia), cambiando el valor antes de cada corrida. ~5.3 min de ejecución por corrida (213 × 1.5s). **Fix de datos aplicado al generar el flujo:** 189 de los 426 teléfonos venían con un "0" de más pegado al código de país (formato de marcado local uruguayo guardado detrás de `+598`, ej. `+598091046641`) — se normalizaron a E.164 real (`+59891046641`); sin este fix ~44% de los envíos habrían fallado. 2 contactos quedan marcados `revisar` (teléfono con dígitos faltantes, probable error de carga en cal.com). Límite de contactos ManyChat: 66/2500 hoy, subiría a ~492/2500 con este envío — margen amplio. **Pendiente antes de correr:** bindear la credencial `CLZ API Header Auth` (ya existe en n8n) en los 2 nodos HTTP Request, hacer un smoke test con 1 contacto real, y confirmar el número de teléfono correcto (con código de país) para ese smoke test.

**🆕 v2 con plantilla Utility — ahorro de ~USD 31 (2026-08-01) · ✅ PLANTILLA APROBADA (2026-08-04):** al ir a mandar el broadcast se detectó que la plantilla se aprobaba siempre como **Marketing** aunque se propusiera Utility. No es un bug de ManyChat: desde el **2026-04-09** Meta recategoriza automáticamente y su veredicto manda. **Costo real (rate card ManyChat, bucket "Rest of Latin America" donde cae Uruguay): $0.0851/msg Marketing vs $0.0130 Utility** → sobre 426 envíos, **$36.25 vs $5.54**. Verificado empíricamente por la agencia cargando $10 y mandando 1 plantilla (monedero → $9.91). **Causa de la recategorización:** Utility exige que el mensaje actualice sobre una **acción previa y específica de ese cliente** (Meta lista "post-purchase notifications"); un anuncio institucional al padrón entero no califica, y el texto original sumaba señales de Marketing (signos de admiración, el CTA "Agenden 092 665 505", "muchas gracias"). El nombre de la plantilla no influye — el clasificador lee el contenido. **Solución:** plantilla nueva `actualizacion_contacto_servicio` redactada como notificación post-venta atada al servicio real de cada contacto (tono neutro, sin imperativos ni exclamaciones), con 3 variables — `{{1}}` nombre (system field First Name), `{{2}}` servicio y `{{3}}` fecha (custom fields `clz_servicio` + `clz_fecha_servicio`, **ambos tipo Text**; un tipo Date rompe con 400, mismo patrón del bug `ai_msg_count` del 30/06). Workflow `clz-notificacion-cambio-numero-v2-utility.json` (16 nodos): el loop pasa a 3 llamadas API por contacto (`createSubscriber` → `setCustomFields` → `sendFlow`) con guarda en cada paso — si `setCustomFields` falla NO se dispara el `sendFlow`, porque una variable vacía hace que WhatsApp rechace el envío (o que llegue un mensaje roto). Los 426 contactos se regeneraron desde el markdown incluyendo servicio + fecha, con las 3 variables verificadas no-vacías. Mantiene el split 213/213. **✅ Plantilla aprobada como Utility y costo confirmado (2026-08-01):** el smoke descontó $9.91 → $9.90 = **$0.01/mensaje**, consistente con la tarifa Utility. El ahorro sobre los 426 se materializa (~$5.5 en vez de ~$36). **Aprendizaje transferible:** el patrón de redacción Utility (atar el mensaje a una acción previa y específica del cliente, tono neutro, sin imperativos ni exclamaciones) sirve para los recordatorios de visita y confirmaciones de reserva atados a bookings de cal.com, que son recurrentes y donde el ahorro se multiplica mes a mes.

**✅ Fallback de subscriber existente — resuelto y validado E2E (2026-08-01):** `createSubscriber` devuelve error cuando el teléfono ya es subscriber, y sin fallback esos contactos nunca recibían el mensaje (se perdían silenciosamente en el conteo de fallidos). La solución tardó varias iteraciones porque **`findBySystemField` no sirve para contactos de WhatsApp**: el system field *Phone* y el número de WhatsApp son campos distintos en ManyChat, y ese endpoint devuelve `status: success` con `data: []` aunque el contacto exista — con `+`, sin `+`, y con `whatsapp_phone` (que además ni siquiera es un param válido: solo acepta `phone` o `email`). No es un problema de formato ni de configuración; está [reportado en el foro oficial](https://community.manychat.com/general-q-a-43/issue-with-manychat-api-get-fb-subscriber-findbysystemfield-not-returning-data-for-phone-parameter-4945) y la respuesta del moderador es exactamente el workaround que se implementó. **Solución final:** `findByCustomField` sobre un custom field propio `clz_wa_id` (id `14840611`, tipo Text) que el mismo workflow setea en `setCustomFields` junto a `clz_servicio` y `clz_fecha_servicio`. Cadena: `createSubscriber` → `¿Subscriber creado?` → (false) `findByCustomField` → `¿Encontrado?` → `Resolver subscriber_id` → `¿Subscriber resuelto?` → `setCustomFields` → `¿Custom Fields OK?` → `sendFlow`. El `Resolver` normaliza el `data.id` venga del create (objeto) o del find (array) **y arrastra el contacto completo hacia adelante**, para que los nodos de abajo lean `$json` en vez de reachear hacia atrás atravesando IFs y Code nodes (lo que rompe la cadena de paired item de n8n). **Alcance del fix:** cubre cualquier contacto creado por este workflow → re-correr es seguro. NO cubre los ~66 subscribers preexistentes (no tienen `clz_wa_id`); esos quedan logueados en `detalle_fallidos` y son, por construcción, gente que ya le escribió al número nuevo después del 30/06 — o sea que ya lo tienen agendado. **Validado E2E el 2026-08-01:** corrida 1 (contacto nuevo) y corrida 2 (mismo contacto, ya existente) ambas entregaron el mensaje con las 3 variables renderizadas. **Bugs de n8n corregidos en el camino:** las 2 salidas del `Split In Batches` v3 son `['done','loop']` — índice 0 es *done*, invertirlas hace que el resumen dispare primero y el batch no se procese nunca; `batchSize` y el `unit` del nodo `Wait` deben declararse explícitos (los defaults son 10 y **horas**); y los 5 Code nodes usaban `this.getWorkflowStaticData` en vez de `$getWorkflowStaticData` (ver `_core/standards/n8n-data-references.md`).

**🆕 Formularios del team cal.com + prefill de teléfono (2026-08-05):** el bot ya entregaba los 9 links del **team** `Collazo Servicio Técnico` (`cal.com/team/collazo-servicio/...`, team id `256131`), pero esos event types **no tenían ni un solo campo custom** — solo los del sistema, y con el teléfono **oculto**. O sea que quien reservaba por el team no dejaba teléfono, ni documento, ni la confirmación del costo de $750. Los 7 event types personales (`hidden: true`, pero accesibles por link directo — en cal.com `hidden` significa "no listado en el perfil", no inaccesible) sí tenían el formulario completo. **Aplicado por API a los 9 del team:** réplica campo por campo de los formularios personales (marca/btu/Tipo/cant_aires/problema_*/material + documento + confirmación $750), teléfono **visible y obligatorio** (en los personales es opcional — decisión de la agencia, el flujo de WhatsApp depende del número), y `notes`/`guests` ocultos para igualar el form personal. Verificado campo por campo contra la fuente + render real de la página pública. **Dos asunciones a confirmar:** `desmontaje-de-calefon` y `desmontaje-instalacion-de-calefon` no tienen contraparte personal → se les asumió el set de calefón, y están en uso real; y `mantenimiento-aire-acondicionado` pregunta *"cantidad de aires a **instalar**"*, typo heredado del personal que se replicó tal cual en vez de corregirse unilateralmente. **Bandera de Brasil en el campo teléfono — no es configurable:** cal.com resuelve el país en runtime por **IP del visitante** (endpoint `public.countryCode`); las 3 propiedades plausibles de la API v2 (`defaultCountry`/`defaultCountryCode`/`countryCode`) se aceptan con 200 y **se descartan en silencio** — parece que funcionó y no hace nada. Lo que sí funciona es prellenar el número por query string (`?attendeePhoneNumber=%2B598...`), que además ahorra tipear el campo ahora obligatorio. Ver el bloque siguiente.

**🆕 Prefill de teléfono en los links — ✅ deployado, inerte hasta el paso ManyChat (2026-08-05):** aplicado por API en el workflow vivo `[Collazo] Agente Principal v3` (`TcxaNLAZRfduShW7`, 22 nodos, activo) — 2 Code nodes editados: `Normalize Payload` agrega `phone_e164` (normalizado a E.164 UY, contempla el "0" de marcado local del broadcast del 31/07 y el literal `{{phone}}` sin renderizar) y `Build ManyChat Payload` agrega `prefillCalcom()` que pega `?attendeePhoneNumber=` a cada link de cal.com de las 3 partes. **Se injerta DESPUÉS del splitter y no antes:** entre `Code in JavaScript1` y `Build ManyChat Payload` está `Formatear mensaje`, que es un **LLM** partiendo el texto en 3 — si el prefill fuera antes, ese modelo manipularía una URL larga con query string y puede cortarla al medio. Validado con 14 casos en Node + ejecución real post-deploy (`1323321`, canal whatsapp, ambos nodos success). **🔸 Falta el único paso que lo activa:** en ManyChat → flow **Default Reply** → **External Request** → agregar `"phone": "{{phone}}"` al body. Hasta entonces `phone_e164` llega `null` y los links salen igual que siempre (degradación deliberada: el peor caso es el comportamiento actual). Sin efecto en Instagram/Facebook, que no tienen teléfono. Guía: `06_docs/guia-prefill-telefono-calcom-2026-08-05.md`.

**Archivos clave:**
- **Workflow vivo del agente: `[Collazo] Agente Principal v3` — n8n id `TcxaNLAZRfduShW7`** (22 nodos, activo, instancia `[TU-INSTANCIA-N8N]`). Es la fuente de verdad; el JSON del repo NO lo refleja.
- `06_docs/guia-prefill-telefono-calcom-2026-08-05.md` — Prefill del teléfono en links cal.com: diagnóstico del país por IP, por qué va después del splitter, `jsCode` completo de los 2 nodos, 5 smoke tests y rollback. Pasos 1-2 aplicados; paso 3 (ManyChat) pendiente
- `03_workflows/agente-collazo-main.json` — Workflow principal del agente (⚠️ desactualizado post-migración ManyChat — son 16 nodos y un Code de 2 líneas, ni siquiera tiene el guardrail de links; el vivo tiene 22. Pendiente re-exportar)
- `03_workflows/clz-notificacion-cambio-numero-v2-utility.json` — v2 con plantilla Utility + 3 variables (ver detalle arriba). **Plantilla aprobada como Utility y costo confirmado el 2026-08-01** ($9.91 → $9.90 = $0.01/msg). 19 nodos tras agregar el fallback de subscriber existente. Setup completo en el sticky "🔧 Setup ManyChat" dentro del workflow
- `06_docs/snippets/clipboard-clz-fallback-subscriber-existente-2026-08-01.json` — los 3 nodos del fallback (`findBySystemField` + `¿Encontrado?` + `Resolver subscriber_id`) en formato clipboard, para pegar sin re-importar el workflow entero (preserva `flow_ns` y credenciales ya bindeadas)
- `03_workflows/clz-notificacion-cambio-numero-v1.json` — Notificación masiva vía plantilla Marketing `cambio_numero` (ya aprobada). **Es el fallback si Meta recategoriza la Utility del v2**
- `06_docs/migracion-whatsapp-manychat-2026-06-30.md` — Incidente número bloqueado + migración a ManyChat + bugs resueltos
- `03_workflows/seguimiento-collazo.json` — Sub-workflow de seguimiento automático (8 hs delay)
- `03_workflows/collazo-round-robin-v1.json` — **Round-Robin manual cal.com → Google Calendar** (35 nodos: Webhook + Parse + Switch event → 3 lanes CREATED/RESCHEDULED/CANCELLED, con routing por servicio en `clz_event_type_routing` + alternancia atómica en `clz_round_robin_state` + mapping en `clz_event_assignment`). Cuando le toca a Fabián: `getAll` por iCalUID en calendar Matías → delete + create en calendar Fabián con `sendUpdates=none` (movimiento silencioso). En repo, pendiente deploy
- `04_agents/agente-collazo-system-prompt.md` — System prompt **v1.7** (precio instalación calefón, comportamiento proactivo mantenimiento, reconocimiento de variaciones de servicio, zona Villa García/Ruta 8 km 19, cierre de escape en regla de zona no cubierta y regla de no mencionar proactivamente el costo de visita en "otros servicios")
- `05_crm/clz-round-robin-schema.sql` — DDL 3 tablas (`clz_round_robin_state` singleton + `clz_event_type_routing` por slug + `clz_event_assignment` mapping) + seeds + queries operativas comentadas
- `06_docs/round-robin-design.md` — Diseño + arquitectura + setup paso a paso del round-robin
- `06_docs/calcom-webhook-setup.md` — Guía 1 página para registrar webhook en cal.com (URL, eventos, secret HMAC)
- `07_testing/testing-guide-v2.md` — Guía de testing del agente conversacional v1.4
- `07_testing/testing-guide-v3.md` — Guía de testing v3 (prompt v1.7): agrega casos de zona Villa García + correcciones post-testing automatizado (zona no cubierta reconocible, costo de visita no solicitado). Testing automatizado con `run-agent-tests.py` detectó variancia residual (temperature 0.2) en casos de precios/links no relacionados a esta sesión — ❌ **re-test dedicado descartado el 2026-08-04**
- `07_testing/testing-guide-round-robin-v1.md` — Testing del round-robin (11 casos C1-C11: primer/segundo/tercer booking, cancel fabián/matías, reagendado, concurrencia, retry, pausa, override por servicio, lag)
- `07_testing/fixtures/` — Payloads cal.com de ejemplo (`created.json`, `rescheduled.json`, `cancelled.json`)

**Routing por servicio confirmado con Matías (2026-06-10):** 5 servicios en round-robin (instalación/reparación/mantenimiento/desmontaje de aire + instalación de calefón); 2 exclusivos de Matías (`reparacion-de-calefon` + `servicio-electrico`). Aplicado en el SQL seed y queda activo desde el próximo deploy del schema.

**🔬 Diagnóstico del round-robin nativo — 2026-08-05 (`06_docs/diagnostico-round-robin-calcom-2026-08-05.md`):** antes de deployar 35 nodos + 3 tablas se verificó con datos la premisa de junio (*"el RR nativo de cal.com no funciona, causa desconocida — no la vamos a debuggear"*), que nunca se había comprobado. **Confirmada: no reparte.** Sobre 249 bookings de 180 días, 241 (96,8%) fueron a Matías; las únicas 8 de Fabián se crearon el 29-30/4 en una ventana de 2 días y **están todas canceladas** — son las pruebas de setup, y coinciden con su última actividad en cal.com. **Desde el 1° de mayo: 126 reservas reales, 0 a Fabián.** Y no es por config: los 9 event types del team (`collazo-servicio`, id `256131`) están en `schedulingType: roundRobin`, la asignación de hosts replica exactamente la regla de negocio (2 exclusivos de Matías, 7 con ambos), ambos hosts tienen `priority: medium`, y Fabián **sí** tiene disponibilidad configurada (comparando dos event types del mismo rubro, aporta 2 slots sobre 36 en 7 días — solo suma cuando Matías está ocupado, porque su agenda ya satura el día). **Causa raíz abierta:** la hipótesis principal es que Fabián no tenga *destination calendar* en cal.com — cal.com le leería la agenda pero no podría crearle eventos, así que lo saltea al asignar. Se verifica en Settings → Calendars de su cuenta, y si es eso, conectarlo podría hacer funcionar el RR nativo y **volver innecesario todo el workflow de n8n**. Es la misma conversación que ya había que tener con él por el 2FA del OAuth. **2 bugs corregidos de paso:** (1) el seed de `clz_event_type_routing` usaba los slugs de los event types *personales* — los del team llevan "de" en el medio, así que `reparacion-de-calefon` no matcheaba y caía al default `round-robin` **siendo exclusivo de Matías**; corregido en el SQL, ahora con los 9 slugs del team + los 2 personales legacy; (2) el diseño no contemplaba sacar a Fabián como host antes de activar el workflow — sin eso cal.com y n8n repartirían en paralelo (costo medido de sacarlo: ~6% de disponibilidad). **La premisa central del diseño se sostiene** (241/249 cayeron en el calendar de Matías), así que la arquitectura sirve tal cual. El error 400 que reportó Matías el 04/08 queda sin explicar — no se reprodujo.

**🔸 Pendiente abierto — terminar de setear el Round Robin (pre-deploy):** (a) **primero: verificar el destination calendar de Fabián** — puede volver innecesario todo lo demás; (b) sacar a Fabián como host de los 7 event types del team; (c) obtener Calendar IDs de Matías y Fabián + crear las 2 credenciales OAuth en n8n; (d) ejecutar el SQL schema en Postgres Collazo (ya con los slugs corregidos); (e) reemplazar placeholders `MATIAS_CALENDAR_ID_REPLACE` / `FABIAN_CALENDAR_ID_REPLACE` en el workflow + bindear las 2 credenciales nuevas; (f) registrar webhook en cal.com con los 3 eventos (plan pago confirmado → 1 webhook global, no 7 por event-type).

---

### NPR — Napier Salon (`clients/NPR_Napier/`)

Agente conversacional para gestión de citas de la peluquería para hombres Napier Salon. Dueño: Wilfrido. El sistema tiene dos agentes: Agente Principal (conversacional, atiende al cliente) y Agente Admin (operativo, sin confirmaciones innecesarias). Ambos usan un nodo Code `Fechas` que pre-calcula `fecha_contexto` en el User Message para resolver fechas relativas sin depender del LLM.

**Stack:** n8n + OpenAI GPT-4.1-mini + Google Calendar + Airtable + Chatwoot + PostgreSQL (memoria)

**Archivos clave:**
- `03_workflows/sub-admin-napier-v1.json` — Workflow n8n Agente Admin (build activo)
- `04_agents/agente-napier-principal-system-prompt.md` — System prompt v1.0 (conversacional, para el cliente)
- `04_agents/agente-napier-admin-system-prompt.md` — System prompt v1.0 (operativo, operaciones inmediatas sin confirmación excepto cancelar)
- `04_agents/subagente-napier-calendario-system-prompt.md` — System prompt v1.0 Subagente Calendario
- `04_agents/subagente-napier-crm-system-prompt.md` — System prompt v1.0 Subagente CRM

**Pendientes: ❌ ninguno — descartados el 2026-08-04.** Los 5 fixes manuales del workflow no se aplican; el proyecto queda congelado en testing tal como está. Se conservan listados abajo solo como referencia de lo que quedó sin corregir: (1) fix "Date & Time 2" → "Date & Time1" en nodo Subagente Calendario; (2) reordenar Operación B + REGLA DE IDs + step 4.5 Consultar disponibilidad en nodo Subagente Calendario; (3) cambiar $fromAI tipo `string` → `json` en campos `cliente` y `staff` del nodo `Registro citas`; (4) reemplazar regla matemática de slots por listas hardcodeadas en todos los nodos de agentes; (5) referenciar `fecha_contexto` del User Message en nodos Agente Principal y Agente Admin

---

### HPF — Happy Flops (`clients/HPF_HappyFlops/`)

Flujos de automatización para Happy Flops (sandalias e insumos para fiestas y eventos). Proyecto en mantenimiento con flujo principal importado.

**Stack:** n8n · GoHighLevel (migración en curso) · OpenAI gpt-4.1 · Postgres (memoria + debounce) · Telegram (canal de demo)

> ## ✅ Sesión 2026-09-03 — Promo vasos verificada + Sandalias Lisas $24 alta completa (BOT DE KOMMO, no GHL). Leer antes que lo de abajo.
>
> Todo sobre el **bot productivo de Kommo** = `[Happy Flops]` **`pYtiBlhOTr7HVPmr` en `devn8n`, activo, 239 nodos** (el que atiende clientes hoy, NO el GHL W-series). Sub-workflow CALCULADORA = `OPiuPFwRmq6QgACL` (`Code2`). Editado por API con anclas + verificación funcional. Backup de rollback (estado pre-todo): **`03_workflows/kommo-live-2026-09-03-pre-sandalia-lisa/`**.
>
> ⚠️ **El bot vivo de Kommo DERIVÓ del snapshot congelado `base-prod-2026-08-06`** (systemMessage del Recolector 55.600 → ~59.900 chars). La base-prod ya NO refleja producción; para el bot Kommo, la fuente de verdad es el vivo en devn8n. Import por API: filtrar `settings` (la API rechaza `binaryMode`/`availableInMCP`; n8n los preserva igual).
>
> **1. Promo popote ($25 + 1 solo color por pedido):** ya estaba aplicada en el bot Kommo (alguien la puso antes) — **verificada en vivo** corriendo el prompt real (cotiza $25, fuerza 1 color, aguanta insistencia). El bot **GHL W6** (`cNmJCP2qVhdtfCH0`) sigue con **$35 + "cada 20 vasos"** — diferido a propósito hasta el cutover (si no, pisa la promo).
>
> **2. Precios de Oscar (confirmados por WhatsApp):** 9 de 11 ya coincidían con el bot → **sin cambio**. Los $24/$29/$29 del Excel eran VIEJOS: Oscar mantiene Sandalia Delgada $25, Gruesa $30, Pantufla $30. "Costal $7" ya cubierto por "Bolsitas $7"; "Anticruda $10" aparte.
>
> **3. Sandalias Lisas $24 — producto NUEVO, alta completa end-to-end.** Atributos reales de Oscar: **SIN impresión, NO se personaliza** (como mandiles), **mínimo 40 pares** (no 50), **6 colores**, bolsa celofán, **se surte y envía en 2-3 días hábiles** (sin los 15 de producción), disponible en **todos los eventos** pero **NO se ofrece proactivamente** (solo si el cliente pregunta por sandalias sin impresión). Aplicado: prompt Recolector (bloque dedicado + carve-outs mínimos/diseño/tiempos/tabla + canónico/peso/precio) + CALCULADORA (`WEIGHT` 0.15 / `CATEGORY` SANDALIAS / `MIN` 40 / alias). Routing de imagen: keyword **`lisas`** (distinto, sin "sandalias" para no colarse en pedidos genéricos) en `Message a model` + `AI Agent Products`. **la agencia hizo su parte**: salesbots en Kommo + fila Airtable (base `appNl0TCf82Nc9sA9`, tablas evento Boda `tblV3ULnD5O6650xK`/XV `tblxd3j0b5cdLHTIl`/Otros `tbl2kg4m8LeHjNk7m`, `productos`=`lisas`, `subcategoria`=`Producto Principal`, `bot_id`). Verificado: cotiza $24, mín 40 (39 rechaza), no ofrece impresión, entrega 2-3 días, routing genérico→`sandalias` / sin impresión→`lisas` sin fuga. **Residual conocido (dejado por decisión de la agencia):** en pedido SOLO de lisas el cierre fijo de "7 pasos" todavía dice "elegí tu diseño"/"15 días de producción" — no se forzó porque ese cierre es compartido; se retoma con un branch si Oscar lo nota.
>
> Arquitectura de image-dispatch del bot Kommo (para futuras altas de producto): `AI Agent Products` (decide productos) → `Message a model` (normaliza a vocab cerrado) → `Data` (evento→tabla) → `Return_Formula` (`AND({subcategoria}, OR(SEARCH(kw, LOWER({productos}))))`) → `Search_Products` (base `appNl0TCf82Nc9sA9`, tabla = evento) → `Loop Over Items` → salesbot por `bot_id`. Un producto nuevo = fila en la(s) tabla(s) de evento con su keyword en `productos` + `bot_id` + reconocerlo en los 2 clasificadores.

> ## ✅ Sesión 2026-08-28 — 10 puntos reunión Oscar + reactivadores R1 (todo en producción). Leer esto antes que lo de abajo.
>
> Aplicado y verificado en el vivo (`devn8n`). Rollback: `03_workflows/ghl-live-2026-08-28-post-oscar-reactivadores/` (13 workflows con sha256). Parches: `03_workflows/parches-2026-08-27/`.
>
> **10 puntos de la reunión con Oscar** (todos aplicados, verificados con baseline de regresión 12 escenarios × 3 + smokes E2E, diff limpio):
> **P1** fuera de horario → manda el mensaje de horario de atención, ya no la imagen de vacaciones (nodo `Respuesta fuera de horario`, W7) · **P2** vocabulario mexicano (ya estaba: lila→morado, fucsia→fiusha, rosado→rosa) · **P3** colores NO son productos — no los cotiza; fix real en `Cards a partes` (W6): el CTA "¿le interesa sumarlos a la cotización?" ya no se agrega para `subcategoria = Accesorios` · **P4** imagen **"COLORES DE CORREAS"** — ficha nueva `Colores de correas` creada en Boda/XV/Otros con `colores-correas-sandalias.jpeg`; requirió mapping en **3 capas** (Products + `Canonicalizar productos` LLM + `Cards a partes`) porque el término se perdía en el canonicalizador · **P5** upsell post-cotización (fraseo "Mira, ya que pides… ¡Son un hit en bodas!") · **P6** precios sin tocar (Oscar confirmó que están bien) · **P7** fichas de **"Otros"** — 4 reemplazadas (cilindros ×3 + pantuflas, ya no muestran arte de XV) + **`Sandalias personalizadas` nueva** (Otros no tenía imagen-foto de sandalias) · **P8** datos de pago — texto **byte-exacto** de Oscar fijado determinísticamente en `Partir en burbujas` (W6) + PDF · **P10** Mono→Moño en el display (W6/W7; W4 ya reconocía "moño").
>
> **⚠️ Corrección al CLAUDE.md:** el "bug POST" de `custom_objects.fichas` (400/422) que este archivo daba por roto **ya NO reproduce** — se crearon fichas nuevas por API sin problema (POST con `locationId` en el body → 201). Script de reemplazo de asset: `scripts/utilities/hpf-reemplazar-asset-ficha.py`; el registro local `00_migracion_ghl/06_registro/catalogo-airtable.json` se sincroniza en cada alta para que `--poblar` no revierta.
>
> **Reactivadores R1 (P9)** — tras confirmar con Oscar que **R2-R5 son etapas muertas** (creadas en Kommo pero sin ninguna automatización; verificado: ni los 8 flujos Kommo ni los 51 workflows de `devn8n` las alimentan — el sistema real de reactivación es de **un solo ciclo R1**): (1) **W10 tag→etapa** — `Decidir acción` + `Armar cierre` ahora mueven a `R1 SIN INFORMACION` / `R1 CON INFORMACION` en vez de aplicar tag; el dict `STAGES` de **W0** suma las 3 etapas R1 (stage IDs en el doc) — el flujo de move ya era genérico; (2) **W5 → R1 AP** — nodo `W0 · leer oportunidad` nuevo (W5 pasó a 11 nodos): si el lead está en reactivación R1 y se eleva a atención personalizada va a `R1 AP`, sino a `En Espera` como siempre (verificado E2E: R1→R1 AP, Cotizado→En Espera); (3) **etapas R2 borradas** del pipeline GHL por Oscar en la UI (estaban vacías; GHL no permite borrar stages por API → 404). Diseño + los 6 stage IDs: `06_docs/diseno-reactivadores-r1-r2-2026-08-27.md`. La cadencia (olas `[60,240,300]` min + eval 24h) y los textos de los toques ya vivían en W10.
>
> **Auditoría de renombrado de etapas GHL (pedido de Oscar):** es **seguro** renombrar — todo el acoplamiento es por **stage ID inmutable** (n8n usa dicts nombre→ID y nunca compara el label que devuelve GHL; el HPF Inbound Handler que deriva `stageName` está desactivado y usa dict interno por ID; los workflows de GHL usan IDs). Consecuencia: si se renombra, conviene actualizar los dicts internos de n8n para coherencia (no es funcionalmente obligatorio). ⚠️ La estructura de GHL **NO es 1:1 con Kommo** (la migración la rediseñó — ver `00_migracion_ghl/03_arquitectura_ghl/01_pipeline_ghl.md` §2): 3 etapas sin correspondencia limpia (Lead Nuevo↔Incoming leads, Enviado, En Espera). **"En Espera" NO se puede borrar** — tiene 13 leads vivos y la usa W5. Mapeo GHL→Kommo entregado en chat, pendiente de confirmar Lead Nuevo→Incoming leads vs →ETAPA 1.
>
> **Pendiente principal:** plantillas Meta Kommo→GHL (~66 plantillas, es el bloqueante M7 del WABA). Prompt de arranque autocontenido preparado para atacarlo en sesión aparte (extracción / implementación / envío n8n-vs-GHL / timing pre-vs-post WABA). Y el renombrado de etapas si Oscar confirma el mapeo.

> ## 🔄 MIGRACIÓN GHL REHECHA DESDE CERO — 2026-08-06/07. Leer esto antes que nada de lo de abajo.
>
> Se descartó todo lo construido en la migración anterior (los `hpf-inbound-handler-*.json`,
> `00_migracion_ghl/03_arquitectura_ghl/` y `04_guia_migracion/`) y se reconstruyó partiendo
> sólo de la solución pre-migración, con corroboración punto por punto contra los sistemas reales.
>
> **Hallazgo que invalida buena parte de lo escrito abajo:** el bot productivo **no** es
> `happyflops-main-v3.json` ni vive en la instancia de agencia. Es **`pYtiBlhOTr7HVPmr`
> (239 nodos) en `dev[TU-INSTANCIA-N8N]`**. Lo que hay en `[TU-INSTANCIA-N8N]` con el mismo
> nombre es una copia vieja abandonada que sigue suscrita al webhook de Kommo y descarta todo.
> Fuente de verdad congelada con sha256: `03_workflows/base-prod-2026-08-06/` (8 workflows, 403 nodos).
>
> **Construido y corroborado** — 7 workflows nuevos en `devn8n`, cada uno con generador
> reproducible (`scripts/generators/hpf-gen-*.py`) y gate re-ejecutable (`scripts/testing/hpf-*.py`):
> W0 Client `VK4M7VQm8CMefbty` · W1 Inbound `nA14dNwJ7VS3YMYr` · W2 Salida `MdbOREN56lfQTYlM` ·
> W3 Catálogo `vSLHOawn2bFVXyOK` · W4 CALCULADORA `psGRDByGNjHQ2DVT` · W5 ATENCION `mmo29FTvIquxksWV` ·
> W6 Conversación `cNmJCP2qVhdtfCH0`. **Funciona end-to-end**: un POST al webhook de W1 termina
> en burbujas dentro de GHL. Airtable y Kommo ya no se tocan: el catálogo (65/65 fichas con asset)
> vive en el custom object `custom_objects.fichas` con caché en Postgres.
>
> **Correcciones a afirmaciones previas de este archivo:** la CALCULADORA con validación de
> mínimos **sí** está deployada (el trigger va a `Code2`, no a `Code1`); y el prompt del
> Recolector de producción son 55.600 chars, no 48.459.
>
> **⏭ Para continuar** (falta el runner de paridad, la rama de imagen y 2 helpers):
> `00_migracion_ghl/06_registro/PROMPT-CONTINUAR-L7.md` — prompt de arranque autocontenido.
> ⚠️ La API key de `devn8n` venció el **2026-08-13** (401 en todos los scripts). **Renovada el
> 2026-08-14** — el valor nuevo está en `.env` línea 45 (`HPF_N8N_API_KEY`). Si vuelve a dar 401,
> generar otra desde la UI de devn8n y pisar esa línea.

> ## 📍 Estado del vivo al 2026-08-17 — leer esto antes de tocar HPF
>
> **Export completo y verificado: `03_workflows/ghl-live-2026-08-18-adjuntos-telegram/`** (13
> workflows con sha256 en su README). Es la fuente de verdad. `ghl-live-2026-08-17-post-paridad/`
> es el snapshot previo al cableado de adjuntos (W1 en 52 nodos) y `ghl-live-2026-08-17/` el
> previo a la paridad del cliente que vuelve; los dos sirven de rollback. Los generadores
> `hpf-gen-w*.py` siguen atrás del vivo —
> **regenerar y deployar borra nodos de producción.** Todo cambio va como parche dirigido de nodo:
> `scripts/utilities/hpf-deploy-workflow.py --apply` (valida que el anchor exista y sea único, relee
> del vivo para confirmar). Los cambios de prompt van por la capa de deltas, nunca editando la base
> congelada `04_agents/base-prod-2026-08-06/`.
>
> **🔴 Lo más importante: Telegram entra por W1, no por el handler viejo.** Hasta el 14/8 había **dos
> sistemas en paralelo** sin que nadie lo supiera — todo el desarrollo iba a los W-series y todo el
> testing de Oscar, Camilo y la agencia seguía pegándole a `HPF Inbound Handler` (`IPO1c36NLzkXrBh9`).
> Ese handler quedó **desactivado**; el Telegram Trigger vive ahora en W1, que además tiene el
> comando de reset (`/b /borrar /reset /clear /nuevo /nueva`). W1: **59** nodos · W6: 41 · ambos activos.
>
> **Trampas medidas — no re-descubrirlas:**
> · el Telegram Trigger **sin `webhookId` activa sin error y nunca recibe nada**;
> · `args` hacia W0 debe ir como **objeto**, no `JSON.stringify` — abrir y guardar el workflow en la
>   UI repuebla el schema y un string deja de validar (`Invalid input for 'args'`). ✅ **los 14
>   llamadores están migrados desde el 17/8**; hasta entonces los 3 de W1 seguían en string pese a
>   que este archivo los daba por migrados, y sobrevivieron de casualidad a una repoblación real de
>   schema (`W6 · conversación` pasó de `schema: []` a 6 entradas entre el 14 y el 17);
> · GHL rechaza teléfonos `+999` → la identidad de Telegram va por **email** sintético;
> · en un Switch, `fallbackOutput: 3` no se acepta: una regla explícita por salida;
> · una rama **paralela** corre DESPUÉS de la principal (`executionOrder: v1`), así que `isExecuted`
>   da false — los nodos que otro nodo referencia van **en la cadena principal**;
> · `records/search` de GHL tiene **lag de indexación**: después de un PUT devuelve el valor viejo
>   un rato. El read-back va por **GET directo** del record, nunca por search.
>
> **Principio que quedó medido:** los arreglos por **nodo** dieron 4/4 y 5/5; los arreglos por
> **prompt**, 4/7 y 3/5. Si se puede resolver en un nodo, se resuelve en un nodo.
>
> **Abierto:** el evento **"Otros"** comparte assets de XV y le faltan fichas · **"¿cuánto cuestan?"**
> referido a lo último ofrecido es intermitente (~3/5) y quedó así por diseño · **crear registros
> nuevos en `custom_objects.fichas` por API está roto** (400 sin `locationId`, 422 con él) — bloquea
> agregar fichas sin pasar por la UI · **preguntarle a Oscar si el lead ahora elige el diseño de
> mandil por número** (ver abajo).
>
> Guía de test vigente: `07_testing/guia-test-la agencia-2026-08-14.md`. Baseline de regresión:
> `scripts/testing/hpf-baseline-regresion.py` (compara hechos estables, no texto — el bot es un LLM).
> ⚠️ Ese baseline **solo pega al webhook de W6** y nunca ejecuta W1: para cambios en W1 el gate es
> `scripts/testing/hpf-l6-w1.py`, que entra por su webhook y lee el `runData` por API (8 casos,
> 7 aristas topológicas).

> ## ✅ Adjuntos de Telegram + guía de paridad nuevo-vs-viejo — 2026-08-18
>
> **El carril de prueba de Telegram ya recibe media.** Hasta el 18/8 `TG · armar payload`
> hardcodeaba `attachments: []` con el comentario *"Telegram entrega los adjuntos como file_id,
> que hay que canjear por URL con la API del bot. Eso todavía no está cableado"*. Consecuencia: seis
> familias enteras (comprobante de pago, imagen de producto, imagen no categorizable, PDF, audio,
> guardia de horario) **sólo existían del lado del bot viejo** y no había con qué compararlas.
>
> **Cómo se canjea:** se baja el binario con el nodo Telegram y se sube a la Media Library de GHL,
> que devuelve una URL de `assets.cdn.filesafe.space` — el mismo dominio de las 65 fichas, ya
> probado con la visión de OpenAI y con el `Descargar audio` de W1, y que conserva la extensión.
> **Construir `api.telegram.org/file/bot<TOKEN>/<file_path>` no es viable**: los Code node no leen
> credenciales, y la credencial `telegramApi` mete el token en el **path**, algo que el auth
> genérico del HTTP Request no sabe hacer (sólo header/query/body/basic). Hardcodearlo dejaría un
> secreto en el JSON, en el repo, en cada log — y se lo pasaría a OpenAI en `imageUrls`.
>
> 7 nodos nuevos en W1 (**52 → 59**), script `scripts/utilities/hpf-fix-telegram-adjuntos.py`,
> 38 asserts post-PUT en verde. La extensión **la fija el código, no Telegram**: foto→`jpg`,
> nota de voz→`oga`, video→`mp4`, documento→la del `file_name` con whitelist. Es lo único que mira
> `Normalizar entrada` para clasificar, así que se probó el clasificador contra 11 payloads
> simulados antes de deployar (incluye `.PDF` en mayúscula, el GIF que llega con `animation` y
> `document` a la vez, y el rechazo por >20 MB).
>
> **Tres decisiones que conviene no re-discutir:**
> · el ruteo de media va **después** del ruteo de reset, así que una foto con caption `/reset`
>   resetea y no sube nada;
> · **`debounce_seg: 15` para media** (0 sigue para texto): con 0 el "gana el último" no deduplica
>   nada — un álbum de Telegram son N mensajes independientes y cada ejecución se ve a sí misma
>   como última;
> · un **video queda clasificado como `imagen`** y la visión lo rechaza, degradando a derivación a
>   humano. Es un **bug preexistente de producción** (le pasa a cualquier lead que mande un video
>   por WhatsApp) y se replicó a propósito. Ticket aparte.
>
> **Verificado de paso:** el `unit` de `Debounce · esperar` **es segundos**. El nodo no lo declara
> y era el riesgo feo (si el default fuera `hours`, producción llevaría meses con un debounce de
> 50 horas). Se resolvió midiendo ejecuciones reales: las que corrieron con `debounce_seg=8`
> duraron 25 s y 10 s totales. El script igual lo explicita.
>
> **La guía de paridad:** `07_testing/guia-paridad-nuevo-vs-viejo-2026-08-18.md` — **50 casos en
> 8 bloques**, cada uno con la secuencia a enviar y dos slots para pegar (nuevo por Telegram, viejo
> por WhatsApp). Dos decisiones de estructura: los casos que dejan el lead trabado
> (`ATENCION_PERSONALIZADA`, comprobante de pago) van **agrupados al final**, porque cortan la
> corrida sin mensaje de error; y abre con una **tabla de diferencias esperadas**, sin la cual casi
> todos los turnos "difieren" por formato — el viejo filtra `¿ ¡` y los emojis fuera del BMP,
> Telegram muestra los asteriscos literales, y la cotización sale en 1 burbuja contra ~3.
>
> ⚠️ **Antes de correrla, saber esto:** el viejo **no tiene reset** (hay que borrar
> `n8n_chat_histories` a mano por `session_id = '+<tel>2131'`) y **se auto-contamina**: cada saludo
> deja una ejecución dormida que despierta a los 60 min, manda un WhatsApp y **escribe ese texto en
> la memoria compartida**. Y el lead de test entra al pipeline productivo de Kommo, con alertas que
> publican nombre y teléfono en el grupo del equipo. Asumido, sin aviso previo a Oscar.


> ## ✅ Paridad del cliente que vuelve + catálogo de mandiles — aplicado el 2026-08-17
>
> **El hallazgo dio vuelta el pedido: no había un reciclado que implementar, había un delta que
> revertir.** En Kommo, un lead en `143` (Ventas Perdidas) que volvía a escribir **no recibía
> respuesta**: la ruta terminaba en un Telegram al equipo (*"El Lead: {entity_id} esta en \*Ventas
> Perdidos\* y envió un mensaje"*) y se revivía a mano — es lo que Oscar describió el 9/5 como
> *"Rebeca contesta ~50 mensajes diarios de leads en 'ventas perdidas' que escriben de vuelta"*.
> Para `142` (Ganado) no había ni gate ni alerta: la rama `If5` out1 quedó sin conectar.
>
> W1 tenía eso bien traducido (`BLOQUEO` con los comentarios `// Kommo 142` y `// Kommo 143`) pero
> el orden de precedencia lo anulaba: `if (vuelve) … else if (motivo)` hacía que `cliente_vuelve`
> le ganara a `bloqueado`, y esa salida iba a un NoOp pass-through hacia el debounce. **El bot
> contestaba.** Los tres actos de `PM-IDN-03` (volcar a `notas_postventa`, resetear a `Lead Nuevo`,
> limpiar la cotización) fueron diseñados para ese comportamiento, así que **quedan superados** —
> y `notas_postventa` no era paridad de todos modos: en Kommo el bot no dejaba nada al cerrar (cero
> `/leads/notes`, y de sus 15 custom fields de lead ninguno era del pedido).
>
> **Qué se aplicó** (los 3 en W1, cada uno con verificación entre medio):
> 1. **`args` a objeto** en `W0 · find or create`, `W0 · leer oportunidad` y `W0 · avanzar etapa`
>    (`hpf-migrar-args-a-objeto.py`). Iban primero por estar aguas arriba de todo.
> 2. **`primer_contacto` desde la memoria** — `W6 · conversación` recibía
>    `{{ $json.etapa === 'Lead Nuevo' }}` y descartaba el `primer_contacto` que `Evaluar estado` ya
>    calcula contando turnos en `n8n_chat_histories`. Parche:
>    `03_workflows/parches-2026-08-14/w1-primer-contacto-desde-memoria.json`.
> 3. **El mute con aviso** — `scripts/utilities/hpf-fix-mute-cliente-vuelve.py`: renombra el NoOp a
>    `Cliente vuelve · sin respuesta`, le cuelga `Aviso · cliente vuelve` (Telegram, chat
>    `-4925599962`, **el mismo grupo que usaba Kommo**, `onError: continueRegularOutput`) y corta la
>    conexión al debounce. **No se tocó el `jsCode` de `Evaluar estado`**: lo referencian 8 nodos por
>    nombre, y la ruta `cliente_vuelve` ya aislaba el caso, así que alcanzó con recablear.
>
> Verificado en vivo: Ventas Perdidas y Ganado → sin respuesta + alerta enviada; `En Espera` → sin
> respuesta y **sin** alerta (paridad: en Kommo solo `143` alertaba); ráfaga de 3 → 3 alertas
> (paridad: el Switch va antes del debounce, igual que en Kommo). Gate `hpf-l6-w1.py`: **8/8, 7/7
> aristas**. Efecto colateral a favor: estos leads dejan de llegar a `Marcar actividad`, que reabría
> su fila de `hpf_seguimientos` con `cerrado_at = NULL` para que W10 la volviera a cerrar cada ciclo.
>
> **Dos errores de test corregidos de paso.** `hpf-l6-w1.py` referenciaba `Router (stub L7)`, un nodo
> que no existe desde que W6 es real. Y su caso `i08` **validaba lo contrario de la paridad**:
> esperaba el `session_id` sin el `+` del teléfono, cuando en Kommo la clave era
> `{{ numero_telefono }}2131` sobre un valor que empieza con `+` (lo prueba el nodo `No es EEUU`, que
> compara `.substring(0,2)` contra `"+1"`). "Arreglar" el sistema para que ese assert pasara habría
> roto la continuidad de memoria en el cutover.
>
> **Corrección a este archivo:** cuatro documentos del repo afirman que el `session_id` de Kommo era
> el `entity_id` del lead (`01_logica_actual/05_reglas_negocio.md:358`, `01_mapa_funcional.md:375`,
> `ESTADO_MIGRACION.md:166`, `uml-handoff-2026-05-14.md`) y **están mal** — era el teléfono, igual que
> hoy. De ahí salió una receta de cutover en `04_guia_migracion/09_cutover.md:47-58` cuya query no
> habría devuelto una sola fila. El punto `PM-MEM-02` de `puntos.jsonl` sigue `PENDIENTE` con
> `contrato_origen: null`: nunca se corroboró, por eso sobrevivió el error.
>
> **Catálogo de mandiles: reemplazado.** `hpf-actualizar-catalogo-mandiles.py` toca las tres
> superficies (Media Library → record → caché `hpf_fichas` vía W3 con `ttl_seg: 0`) y **sincroniza
> `06_registro/catalogo-airtable.json`**, que no es documentación sino la fuente que lee
> `hpf-crear-objeto-fichas.py --poblar`: tenía todavía la URL vieja de la sandalia XV del 14/8, así
> que un `--poblar` habría revertido ese cambio en silencio. Rollback en
> `parches-2026-08-14/ficha-mandiles-catalogo-rollback.json`. **El prompt NO se tocó**: el catálogo
> nuevo está numerado 1 a 5, lo que invita a "quiero el 3", pero la `REGLA CRÍTICA` de
> `agente-recolector.md:751-789` decía que los mandiles no se eligen. ✅ **Resuelto el 17/8 — ver abajo.**

> ## ✅ Mandiles: se ELIGEN de 5 modelos — aplicado el 2026-08-17
>
> Oscar respondió por WhatsApp: *"Los mandiles si los eligen de los 5 modelos que hay disponibles.
> NO se personalizan, tiene que escoger de las 5 frases que hay. […] Puede escoger como guste,
> todos de 1 diseño o surtido de los que quiera. […] Mínimo en total 12."*
>
> **La distinción que el prompt no hacía: ELEGIR ≠ PERSONALIZAR.** Colapsaba las dos cosas en la
> misma prohibición, así que decía que iban surtidos, que no se elegían, y **derivaba a
> `ATENCION_PERSONALIZADA` a quien sólo quería ver los modelos** — lo contrario del autoservicio que
> Oscar busca. 9 ediciones en el `Recolector` de W6 + 2 en el `Recolector1` de W7 (rama de imagen,
> que repetía "Mandiles: Surtidos según modelos disponibles"). Parches:
> `parches-2026-08-14/w6-mandiles-se-eligen.json` y `w7-mandiles-se-eligen.json`; el gemelo con la
> cita y los motivos vive en `04_agents/deltas-oscar-2026-08-11/08-recolector-mandiles-eleccion.json`.
>
> **Anti-alucinación:** el bot NO tiene las 5 frases en texto en ninguna parte — viven sólo en la
> imagen del catálogo. Las ediciones dicen explícitamente *"mandá el catálogo, NO enumeres las frases"*.
> Sin eso el modelo las inventaría, que es peor que la derivación que había antes.
>
> Verificado E2E: pedir 20 con dos modelos → cotiza · 12 todos del mismo → cotiza · pedir el nombre
> de los novios → se niega e invoca `ATENCION_PERSONALIZADA` · 6 piezas → rechaza por el mínimo de 12.
>
> ### 🚨 Dos cosas que este archivo registraba mal, descubiertas al aplicarlo
>
> **1. Los deltas de prompt NO están todos revertidos.** Arriba dice que los 7 volvieron a la base
> congelada el 14/8. Eso fue cierto ese día (los snapshots `ghl-live-2026-08-12` y `-08-14` tienen
> los 55.600 chars de la base), pero **después se re-aplicaron el 02 (negritas) y el 06 (ubicación)**
> — que son justo los que prueba la guía de test del 14/8. Medido el 17/8: vivo 61.995 chars, base
> 55.600, base+los-7 64.578. Los deltas 03 y 04 no están.
> ⚠️ **Consecuencia práctica: `hpf-aplicar-deltas-prompt.py --deploy` es peligroso hoy.** Compone
> siempre desde la base congelada, así que pisaría lo que el vivo tiene de más. Mientras el vivo esté
> divergido, los cambios de prompt van por **parche de nodo** con anchor verificado contra el vivo.
>
> **2. `hpf-deploy-workflow.py` perdía ediciones en silencio — corregido.** `aplicar()` leía el campo
> del nodo original en cada iteración, así que N ediciones sobre un mismo campo se calculaban todas
> contra el texto de partida y al escribir se pisaban entre sí: **sobrevivía sólo la última**. Cada
> anchor validaba bien contra el original, así que el fallo era invisible. Nunca se disparó porque
> todos los parches previos del repo tenían una sola edición; este de mandiles tiene 9. Ahora las
> ediciones se encadenan y el dry-run lo muestra (`61995 → 62041 → 62126 → …`).

> ## ✅ Cambios de la reunión con Oscar — aplicados el 2026-08-12 · ⏪ la parte de PROMPT revertida el 2026-08-14
>
> **Estado actual del vivo:** los **cambios de nodo siguen puestos** (persistencia del evento con
> `Leer evento`/`Guardar evento`, marcador de pago `url1234.com123` en `Partir en burbujas`,
> canonicalización de pantufla peluche) — W6 en 41 nodos, activo. Los **7 deltas de system prompt
> están revertidos**: `Starter`, `Products` y `Recolector` volvieron a la base congelada
> `04_agents/base-prod-2026-08-06/*.md`, verificado byte a byte contra los systemMessage del
> snapshot pre-reunión `ghl-live-2026-08-12/W6.json`. Los deltas quedan en disco y son
> re-aplicables: `hpf-aplicar-deltas-prompt.py --deploy` los vuelve a poner, `--revert` los saca
> (flag nuevo del 14/8 — el script lo prometía en el docstring y no lo tenía implementado).
>
> Guía completa: **`06_docs/guia-cambios-reunion-oscar-2026-08-11.md`**.
> Rollback: `03_workflows/ghl-live-2026-08-12/` (los 11 workflows con sha256, previo a tocar nada).
> Estado posterior: `03_workflows/ghl-live-2026-08-12-post-cambios/`.
>
> **🚨 Los generadores quedaron atrás del vivo — no regenerar y deployar.** Medido: W1 vivo tiene
> **14 nodos** y W6 **9** que el repo no conoce, y **W7 Media / W8 Relay / W9 SQL / W10 Seguimientos
> no existen en el repo** (`m8KhaZV3nSjJ55ci`, `Ki7IRFYQn1mqOh5p`, `2Govwp16YAcpgJ2C`,
> `fpKvo0ECWIhFcckE`). Correr `hpf-gen-w*.py` y subir **borraría** esos nodos. Todo cambio va como
> parche dirigido de nodo con anchor verificado: `scripts/utilities/hpf-deploy-workflow.py`.
> Los 5 systemMessage de W6 sí estaban byte-exactos con `04_agents/base-prod-2026-08-06/*.md`.
>
> **Capa de deltas de prompt** (`04_agents/deltas-oscar-2026-08-11/`, 7 archivos, 17 ediciones):
> la base congelada NO se edita — sigue siendo la garantía de paridad de la migración. Cada cambio
> es un delta con anchor literal + cita de Oscar. `hpf-aplicar-deltas-prompt.py --check|--diff|--deploy`.
>
> **El bug del evento (XV recibía fichas de Boda) era ausencia de memoria, no un archivo mal
> cargado ni un filtro roto.** Se descartaron las dos hipótesis con evidencia (las 65 fichas tienen
> media viva y las de XV son de XV; W3 con `{evento:XV, productos:[cilindros]}` devuelve las 3 de XV).
> La causa: `Leer Products` le preguntaba el evento al LLM en cada turno, y el prompt de Products usa
> "Boda" en 12 de sus 13 ejemplos. No existía persistencia en ninguna capa: W1 no le pasa `evento` a
> W6, y `hpf_seguimientos.evento` quedaba NULL para siempre. Se construyó: tabla `hpf_estado_sesion`
> + nodos `Leer evento` / `Guardar evento` en W6.
> ⚠️ **Trampa de n8n que costó un intento entero:** con `executionOrder: v1` una rama paralela corre
> DESPUÉS de la rama principal completa, así que `isExecuted` daba false y el estado se ignoraba —
> el smoke daba verde por casualidad porque el LLM acertaba. Se destapó instrumentando el nodo
> (`evento_desde_estado`) y leyéndolo de las ejecuciones por API. Los nodos que otro nodo referencia
> tienen que ir **en la cadena principal**.
>
> **El marcador de pago `url1234.com123` no lo procesaba nadie.** Aparece 4 veces en el prompt del
> Recolector y 0 veces en código de los 11 workflows: en Kommo lo interceptaba un salesbot, en GHL le
> llegaba literal al cliente y el PDF de números de cuenta nunca salía. Ahora `Partir en burbujas` lo
> detecta, lo saca del texto y adjunta el PDF (leído de `hpf_fichas`, no hardcodeado).
>
> **Corrección a este archivo:** la dirección y el link de Google Maps **sí** estaban en el repo
> (`agente-recolector.md` línea 38, link `https://goo.su/OVoA`). Lo que faltaba era separar
> "¿de dónde son?" de "¿cómo sé que es seguro?", que colapsaban a la misma respuesta corta.
>
> **Sigue bloqueado por assets que no tenemos:** el catálogo nuevo de mandiles (Oscar dijo que lo
> mandaba) y el **video de reseñas de confianza** — el salesbot de Kommo `62110` **no está entre las
> 65 fichas migradas** y hay que bajarlo antes de dar de baja esa cuenta.

> ⚠️ **SUPERADO — leer primero `## Pendientes HPF — revisados al 2026-08-04`.** El 2026-08-04 se
> deployó el **v16** y se aplicó el fix de `Send Photo`, así que los tres síntomas descritos abajo
> (CRM desconectado por ids falsos, cero imágenes, y el debounce) **ya no describen el flujo vivo**.
> El bloque se conserva porque documenta el diagnóstico que llevó al v16.

**⚡ ESTADO AL 2026-07-24 (histórico) — lo que estaba VIVO en n8n antes del deploy del v16:** workflow `HPF Inbound Handler` (id `IPO1c36NLzkXrBh9`, **active: true**, 64 nodos). Snapshot en `03_workflows/hpf-inbound-handler-live-2026-07-24.json`. Es el **v14 - demo telegram con las 3 tools de CRM restauradas a la versión de producción del v12** (`IDENTIFICAR_EVENTO`, `MOSTRAR_PRODUCTOS`, `COTIZADOR` byte-idénticas al v12; `ATENCION_PERSONALIZADA` nunca se había tocado). El system prompt sigue siendo el del v14 (13.434 chars, con el marcador `[IMAGEN:XX]`). **NO es el v16** — ese quedó en repo sin deployar. Consecuencias de esta combinación, verificadas sobre el export:
- **Las 4 tools pegan a GHL con ids falsos.** El adaptador `Code in JavaScript` sigue fabricando `opportunity_id = tg_opp_<chatid>` y usando el chat id como `contact_id`, así que cada tool call es un 404. Y como una `toolHttpRequest` que falla le devuelve el texto del error al LLM **dejando el nodo en verde** (verificado en el source de n8n), volvió el bug original que reportó Oscar. En la práctica **el CRM sigue desconectado**: no escribe nada.
- **Cero imágenes.** El único camino de imagen vivo por Telegram es el marcador `[IMAGEN:XX]` → `Sanitize + Split Output` → `¿Parte con foto?` → `Send Photo (Telegram)`, y ese nodo **no tiene el parámetro de la foto**: el v14 lo guardaba como `fileId`, que en `sendPhoto` no existe (verificado en `Telegram.node.ts:873` — el parámetro correcto es **`file`**; `fileId` es solo de `resource: file / operation: get`). n8n descartó la clave desconocida al re-guardar el nodo y hoy queda vacío. **El envío de fotos nunca funcionó, ni en el v14 ni en el v16 (que heredó el mismo error en 3 nodos, ya corregido en repo).** La cadena determinística (`Get Current Opportunity` → `Check Evento Just Set` → `Send Imagen Principal`) solo corre en la rama GHL: `Es Origen Telegram? (Post)` tiene la salida de Telegram vacía.
- **Debounce en 0s.** El nodo se llama `Wait 15s (Debounce)` pero su `amount` es `0` → el agente contesta burbuja por burbuja en vez de agrupar la ráfaga.
- Sin saludo fijo, sin transiciones de etapa y con el contexto `[7]` vacío: `Auth + Normalize` hardcodea `stage: 'Evento Identificado'` y `custom_fields` vacíos.

**v16 — ✅ DEPLOYADO el 2026-08-04:** `03_workflows/hpf-inbound-handler-v16-telegram-crm-real.json` (101 nodos). Se arma sobre el **v12** (última versión con la arquitectura de producción intacta) + el prompt del v14, y resuelve la raíz de lo de arriba: identidad real del lead (`POST /contacts/upsert` con email determinístico `tg-<chatid>@telegram.[TU-DOMINIO]` → `GET /opportunities/search` → create), saludo fijo de 3 partes con candado anti-duplicado, máquina de estados (lo que en prod hace WF-06), imagen del evento + promo, y fichas de producto. Stage ids y custom field ids se resuelven en runtime (`GET /opportunities/pipelines` + `GET /locations/{loc}/customFields?model=opportunity`), sin ids hardcodeados que mantener. Location GHL `onRwi0ZF4uYi0Lp6GAbE`. Prompt = v14 con 5 cambios (3 bloques de degradación revertidos + regla 15 anti-filtrado de errores de tool + fecha de hoy en `[7]`); `CALCULAR_ENVIO` byte-idéntico y las 12 reglas inviolables intactas. **4 bugs latentes que encontró y corrige** (todos siguen vivos en el flujo actual): (1) el `jsonBody` de `Move Stage Pago` arranca con `==` desde el v12 → n8n consume solo el primer `=` → body inválido → **la transición de etapa de pago nunca funcionó**; (2) las escrituras de custom fields tipo checkbox son schema-inválidas — `customFieldsInputArraySchema` exige `id` (no `key`) e items string, y v12 manda `{"key": "had_quote", "field_value": [true, "Tuvo cot."]}`; como GHL valida el array completo, **una entrada inválida rechaza el PUT entero** y se lleva puesta la escritura que sí importa que viaja en el mismo request; (3) la salida `done` de `Loop Message Parts` emite `processedItems` acumulado, así que la cadena de cierre corría una vez por burbuja (resuelto con `executeOnce`); (4) el `sendPhoto` con `fileId` descrito arriba. Verificado con 53 chequeos ejecutando los nodos Code contra payloads reales de GHL en Node.js + validador estático + auditoría adversarial de 5 agentes. **Falso positivo descartado de esa auditoría:** 4 de 5 auditores reportaron como P0 que `PUT /opportunities/{id}` no acepta `pipelineStageId` y `customFields` en el mismo body — el `UpdateOpportunityDto` real tiene 7 props todas opcionales y sin `oneOf`, así que es válido; el "hallazgo" salió de una frase ambigua en el contexto que les pasé (lección: una premisa mal redactada en el prompt de auditoría se propaga como hecho verificado a todos los agentes). Guía: `06_docs/guia-v16-telegram-crm-real-2026-07-24.md`.

**Archivos clave:**
- `03_workflows/hpf-inbound-handler-live-2026-07-24.json` — snapshot del export del 2026-07-24 21:30 (id `IPO1c36NLzkXrBh9`, 64 nodos). **Ya no es el vivo** — reemplazado por el v16 el 2026-08-04; queda como punto de rollback
- `03_workflows/hpf-inbound-handler-v16-telegram-crm-real.json` — **el que está corriendo desde el 2026-08-04** (101 nodos, CRM realmente conectado — ver arriba)
- `03_workflows/hpf-inbound-handler-v12-pre-demo.json` — última versión con el path GHL de producción intacto (62 nodos). Es la base del v16 y la referencia de la rama de producción
- `03_workflows/hpf-inbound-handler-v14-demo-telegram.json` — demo Telegram con CRM desconectado (64 nodos). Es la base del build vivo
- `06_docs/guia-v16-telegram-crm-real-2026-07-24.md` — pre-flight (3 curls para validar el PIT y el locationId), import, recorrido E2E de 8 pasos con lo que hay que mirar en GHL, gaps abiertos y rollback
- `06_docs/fix-tools-ghl-404-demo-telegram-2026-07-24.md` — diagnóstico del 404 que reportó Oscar (`MOSTRAR_PRODUCTOS` pegando a GHL con el `opportunity_id` falso). Superado por el v16, que resuelve la causa raíz en vez de neutralizar la tool
- `03_workflows/happyflops-main-v3.json` — **Flujo principal vivo al 2026-05-30** (236 nodos, agentes AI Agent + Starter + Main Image + Products + Recolector + Recolector1 + Recolector2 huérfano; tools CALCULADORA workflow + CALCULADORA1 toolCalculator). El `Recolector` activo (pos [4160,1344]) usa la CALCULADORA nueva con schema cuentas+items
- `03_workflows/happyflops-calculadora-v2.json` — **Sub-workflow `HPF - Calculadora` v2 (2026-07-15, en repo, pendiente deploy)** — preserva workflowId `OPiuPFwRmq6QgACL`. Agrega a `Code1` una validación determinística de **mínimos de compra** por producto (`Sandalias Delgadas/Gruesas`: 50, `Pantuflas`+variantes: 50, `Cilindros`: 40, `Vaso Popote`: 50, `Kits Anticrudas`/`Costales`: 35, `Mandiles`: 12): si un producto del formato `items` no alcanza su mínimo, la tool RECHAZA el cálculo devolviendo `{error: "MINIMO_NO_ALCANZADO", detalle_violaciones, message_to_agent}` en vez de un `costo_total_envio` válido. El formato legacy `cuentas` (sin nombre de producto) no puede validarse — sigue funcionando igual que antes pero ahora con un campo `advertencia_minimos` explícito. Disparado por incidente real: Oscar reportó cotización de 35 Cilindros (mínimo real 40). Validado con 6 casos en Node.js fuera de n8n. Ver `06_docs/guia-fix-minimo-cilindros-2026-07-15.md`.
- `03_workflows/happyflops-calculadora-v1.json` — Versión anterior (pre-fix mínimos). Trigger expone schema `{cuentas, items}` ambos requeridos. `Code1`: prefiere `items` con `{producto, cantidad}` y aplica límites por categoría (CILINDROS max 250/caja, SANDALIAS max 200/caja, peso max 35kg/caja) — pero SIN validar mínimos de compra, esa era la causa raíz del incidente. Catálogo de pesos: Cilindros/Vaso Popote 0.14 kg; Sandalias/Pantuflas/Pantuflas Mono Satin/Peluche 0.15 kg; Mandiles/Kits Anticrudas/Costales 0 kg. PRODUCT_ALIASES robusto (variaciones "satin"/"satín", "moño"/"mono"). Code `(viejo)` desconectado con rangos de costo distintos (a revisar con Oscar)
- `03_workflows/happyflops-main-v2.json` — Backup v2 (fix sandalias solo mujeres + integridad de precios + SAVE_FIRST_MESSAGE)
- `03_workflows/happyflops-main-v1.json` — Backup v1
- `03_workflows/happyflops-seg-rebeca-v1.json` — Sub-workflow seguimiento Rebeca
- `03_workflows/happyflops-seg-imagen-v1.json` — Sub-workflow seguimiento por imagen
- `03_workflows/happyflops-seg-cotizacion-v1.json` — Sub-workflow seguimiento cotización
- `03_workflows/happyflops-seg-7pasos-v1.json` — Sub-workflow seguimiento 7 pasos
- `03_workflows/happyflops-atencion-personalizada-v1.json` — Sub-workflow atención personalizada (Kommo + Telegram)
- `04_agents/agente-happyflops-recolector-system-prompt.md` — System prompt **v1.6 (2026-07-15, en repo, pendiente deploy)** del `AI Agent Recolector` (Rebeca). v1.6 agrega la sección **"REGLA CRÍTICA — Mínimos de compra"** (mismo tratamiento que Mandiles/Pantuflas/Precios/Género: tabla de mínimos + checklist obligatorio antes de invocar CALCULADORA + aclaración de que "ahorrar preguntas" nunca justifica saltear el chequeo) + paso 4 nuevo en la descripción de la tool CALCULADORA (qué hacer si la tool rechaza el cálculo) + aclaración en las 2 menciones de "solo recordás el mínimo cuando piden por debajo" (es sobre tono, no sobre si hay que verificar). Disparado por el mismo incidente Cilindros 35/40. Hereda v1.5 (undocumented hasta ahora — agregaba PRE-CHECK + REGLA OBLIGATORIA de Mandiles, respaldado retroactivamente como backup en esta sesión) y v1.4.
- `04_agents/agente-happyflops-recolector-system-prompt-v1.5.md` — Backup v1.5 (snapshot del prompt vivo antes del fix de mínimos; nunca había sido versionado como archivo propio — era el contenido de `agente-happyflops-recolector-system-prompt.md` previo a esta sesión)
- `04_agents/agente-happyflops-recolector-system-prompt-v1.4.md` — Backup v1.4
- `04_agents/agente-happyflops-recolector-system-prompt-v1.3.md` — Backup v1.3 (reescribe `# Tools → CALCULADORA`: contrato `items` con nombres canónicos como formato preferido + `cuentas` legacy. Resuelve el error "Received tool input did not match expected schema" del Caso C)
- `04_agents/agente-happyflops-recolector-system-prompt-v1.2.md` — Backup v1.2 (post-mapeo cliente→producto, pre-fix calculadora). Coincide con el prompt vivo de producción al momento del testing del Caso C
- `04_agents/agente-happyflops-recolector-system-prompt-v1.1.md` — Backup v1.1 (post-refuerzo, pre-mapeo)
- `04_agents/agente-happyflops-recolector-system-prompt-v1.0.md` — Baseline real al 2026-05-30 previa al refuerzo
- `06_docs/guia-fix-minimo-cilindros-2026-07-15.md` — **Guía del fix de mínimos de compra** (diagnóstico completo + pasos de deploy Paso 0-3 + rollback + 6 casos de prueba Node.js). Incluye hallazgo colateral: el prompt embebido en `happyflops-main-v3.json` (repo) está desactualizado vs. el `.md` vigente — todavía usa el formato legacy `cuentas` en la sección CALCULADORA en vez de `items`, por lo que el delta v1.3 documentado abajo nunca se confirmó como aplicado en n8n vivo.
- `06_docs/estrategia-plantillas-whatsapp-meta-2026-08-28.md` — **Estrategia de plantillas Meta HSM (Kommo → GHL).** Encuadre + plan por fases (no runbook). Reencuadra el problema: el "66 plantillas" no existe en el repo (146 salesbots ≠ plantillas Meta); el sistema nuevo solo necesita ~4 nuevas; y verificado en el vivo (W10 `fpKvo0ECWIhFcckE` + W0 `VK4M7VQm8CMefbty`) que el reactivador manda 1h/4h/5h — todo IN-window, y el W0 hoy solo tiene `send_text` (no hay `send_template`). §0 resumen ejecutivo · §2.4 verificación en Meta BM de dueño del WABA (gate único) · §5 mapeo plantilla ↔ flujo · §7 colisiones (LLM-personalizado ≠ HSM, Utility vs Marketing) · §8 plan de fases · §9 verificaciones pendientes headless. Sirve para la conversación con Oscar; requiere después un `guia-implementacion-plantillas-meta-...` con textos redactados + Workflow GHL "Send WhatsApp Template" + trigger n8n + plan de test.
- `06_docs/guia-fix-pantuflas-mono-2026-05-30.md` — Guía 3 EDITs v1.0 → v1.1 (precios + ⚠️ + REGLA CRÍTICA Material y modelo)
- `06_docs/delta-fix-pantuflas-v1.2-2026-05-30.md` — Delta v1.1 → v1.2 (1 EDIT: tabla mapeo cliente→producto)
- `06_docs/delta-fix-calculadora-v1.3-2026-05-30.md` — Delta v1.2 → v1.3 (1 EDIT: reescribir sección CALCULADORA con contrato `items` + `cuentas` y nombres canónicos). Incluye contexto técnico del schema langchain y pendientes derivados (revisar rangos costo entre Code1 vs viejo, Recolector2 huérfano, Recolector1 con CALCULADORA1)
- `07_testing/testing-results-v1.1-2026-05-30.md` — Resultados de los 5 casos sobre v1.1: A/B/E ✅, D parcial (gatilló v1.2), C falló con error schema (causa identificada — gatilló v1.3)

**Migración GHL en curso:** `00_migracion_ghl/` contiene el análisis completo del flujo Kommo para migrar a GHL. Incluye `ESTADO_MIGRACION.md` (estado global), inputs (CSVs + `kommo_export.json`), y carpetas de fases: `01_logica_actual/` (mapa funcional, intents, máquina de estados, catálogo de mensajes, reglas de negocio), `02_logica_validada/`, `03_arquitectura_ghl/`, `04_guia_migracion/`, `05_ejecucion/`.

**🆕 Fix mínimo de compra no respetado — incidente Cilindros 35/40 (2026-07-15, Capa 2 verificada en producción, Capa 1 pendiente de pegar completa):** Oscar reportó que el agente cotizó 35 Cilindros a un lead cuando el mínimo real es 40 piezas. Diagnóstico: el mínimo estaba correctamente documentado en el prompt (2 veces), pero era la ÚNICA capa de control — la tool CALCULADORA nunca validó mínimos de compra (solo límites de empaque), así que un cálculo por debajo del mínimo se veía igual de "válido" que uno correcto, sin ninguna señal de alerta. La regla de mínimos tampoco había recibido el tratamiento "REGLA CRÍTICA" que sí tienen Mandiles/Pantuflas/Precios/Género, quedando más fácil de saltear en un prompt de ~840 líneas. Fix de doble capa: prompt v1.6 (REGLA CRÍTICA + checklist) + `happyflops-calculadora-v2.json` (rechazo determinístico en la tool, defensa en profundidad). **Verificación directa contra producción (2026-07-15):** el usuario pegó el `Code1` y el prompt realmente vivos en n8n — el `Code1` resultó ser byte-por-byte idéntico al v1 del repo (confirma la causa raíz sin ambigüedad, y descarta el drift `cuentas`-only que se sospechaba, la producción real ya usaba `items`). Tras pegar el nuevo `Code1`, el usuario corrió los 4 tests directo en el sub-workflow (sin depender del bot, por un lead trabado en una etapa donde el bot no interactúa) — 4/4 resultados exactos a los esperados. Al pedir el prompt vivo completo para el mismo chequeo, se detectó un **paste parcial**: solo se había pegado el paso 4 de `# Tools → CALCULADORA`; faltaba la sección entera "REGLA CRÍTICA — Mínimos de compra" (25 líneas — ya referenciada 2 veces en el prompt sin existir realmente) y 1 de las 2 aclaraciones sobre "solo recordás el mínimo cuando piden por debajo". Se le dio al usuario el prompt v1.6 completo para reemplazo total del System Message (no parches sueltos, para no repetir el hueco). Hallazgo colateral (repo, no bloqueante): `happyflops-main-v3.json` (repo) sigue con la sección CALCULADORA vieja (`cuentas`-only) — es un export desactualizado, no refleja lo vivo.

**📋 Reporte de estado del CRM (2026-07-27):** `06_docs/estado-crm-ghl-2026-07-27.md` — doc para Notion con la estructura completa del CRM en GHL (sub-cuenta, pipeline y 13 etapas, custom fields de Opportunity y Contact, tags, custom values), el mapa de qué dato vive en qué sistema, el ciclo de vida de un lead paso a paso, qué escribe cada pieza, lo que falta, y **una checklist de revisión manual por plataforma** (GHL, n8n, Postgres, Meta/WABA, Telegram, Airtable/Kommo) con qué mirar y qué síntoma tiene cada cosa si está mal configurada. Tres hallazgos que salieron de armarlo: (1) los **Custom Values de GHL no los lee nadie** — precios, teléfono oficial y textos de promo viven hardcodeados en el prompt y en la tool de envío, así que si Oscar edita un precio en la UI el agente sigue cotizando el viejo; (2) **conectar la WABA no alcanza**: sin WF-01 construido en GHL nadie llama al webhook de n8n, el número queda conectado y el bot no responde; (3) lo más urgente y con fecha de vencimiento real es **bajar los assets de los salesbots de Kommo** (fotos de producto, catálogos PDF, videos y el PDF de números de cuenta) antes de dar de baja esa cuenta — no existen en ningún otro lado.

## Pendientes HPF — revisados al 2026-08-04

**Se cerró casi toda la cola del 24-jul.** Queda un solo bloqueante real (la WABA) más un pedido
nuevo de estética conversacional. El detalle histórico de los ítems cerrados vive en el git log y en
`06_docs/`.

### 🔴 Abierto — bloquea producción

1. **Conexión de la WABA (M7).** Es lo que convierte al bot en producción real. Bloqueos: (a) el
   número `+52 331 594 8670` está **activo en Kommo** y no puede migrarse hasta el cutover — hay que
   elegir entre un número secundario de testing (Opción A, recomendada) o migrar el día del cutover
   con ~10 min de downtime (Opción B); (b) las plantillas Meta tardan **24-72 hs** en aprobarse, así
   que conviene arrancarlas ya.

### 🟡 Abierto — calidad conversacional

2. **Replicar la estética conversacional del agente original.** Owner: **Camilo.** El bot nuevo
   funciona pero no suena como el original de Kommo; hay que igualar tono, ritmo y formato de las
   respuestas. Referencia de método: `06_docs/benchmark-bot-referencia/delta-y-backlog.md` (el mismo
   protocolo de ingeniería inversa que se armó para el Agentic Setter).

### 🟢 Deuda técnica de la línea Kommo (el bot que se reemplaza)

3. Sin cambios y sin urgencia: confirmar que se pegó completo el prompt v1.6 del Recolector (la Capa
   2 / `Code1` ya está verificada y viva); re-exportar `happyflops-main-v3.json` a una v4 con el
   prompt y el `Code1` realmente vigentes; decidir qué hacer con `Recolector2` (huérfano) y
   `Recolector1`; verificar los rangos de costo de `Code1` vs `(viejo)` en el sub-workflow
   Calculadora. Al migrar, trasladar al bot de GHL la regla de disambiguación, el contrato `items` y
   la validación de mínimos.

### ✅ Cerrado el 2026-08-04

- **Fix `Send Photo (Telegram)`** — parámetro `file` aplicado; el camino del marcador `[IMAGEN:XX]`
  vuelve a andar.
- **Decisión de CRM** — se deployó el **v16**: resuelve contacto y oportunidad reales contra GHL, así
  que las 4 tools ya no devuelven 404 ni le pasan el error al LLM como si fuera un resultado válido.
- **Assets del catálogo + datos bancarios** — Oscar los pasó. El mapa `FICHAS` del v16 quedó lleno y
  el agente ya puede dar los datos de cuenta que ofrecía sin tener.
- **Workflows de GHL (M4) construidos** — WF-01 (enrutador + saludo fijo), WF-02 (reenganche), WF-04
  (pago), WF-05 (guardia de horario), WF-06 (transiciones de etapa).

### ❌ Descartado el 2026-08-04

- **Debounce en 0s → 15/45.** No se toca.
- **Confirmar el "v15 fantasma" y los 4 bugs latentes.** El v16 ya los corrige en el camino vivo; no
  se sale a buscar ese build.
- **Confirmar con Oscar si "Costales" y "Kits Anticrudas" son el mismo producto.** No se persigue.

**🚧 Fix temporal — Filtro "solo contactos nuevos" tras caída de ManyChat (2026-06-12):** ManyChat estuvo caído un período; Oscar atendió manualmente las conversaciones que entraron en la caída y se pausó el agente. Para reactivar el agente sin pisar las conversaciones que tomó Oscar, se diseñó un IF temporal en `HPF - Main` entre `Clear_Contact_Data` y `All_Data` que filtra por `data.created_at` del contacto Kommo > cutoff Unix (semántica elegida: contacto nuevo = nunca existió en Kommo; cero riesgo de pisar humanos, a costa de no re-engager contactos pre-existentes). Cutoff: timestamp Unix del momento exacto en que se reactive (`date +%s`). Guía paso a paso: `06_docs/guia-filtro-contactos-nuevos-2026-06-12.md` (incluye smoke tests + cómo revertir). NO relacionado a migración GHL — es fix temporal reversible.

---

### NVJ — Narvaja Hogar (`clients/NVJ_Narvaja/`)

Agente de ventas conversacional para Narvaja Hogar (tienda uruguaya de artículos para el hogar: colchones, sommiers, roperos, sofás, electrodomésticos). Responde consultas via WhatsApp, Instagram y Facebook; transcribe audios, analiza imágenes y eleva conversaciones al equipo humano con resumen.

**Stack:** ManyChat + WhatsApp + n8n + OpenAI GPT-4.1-mini + Airtable + PostgreSQL (memoria)

**Archivos clave:**
- `03_workflows/narvaja-agente-principal-v1.json` — Workflow principal (agente conversacional + anti-loop + canal WPP/IG/FB)
- `03_workflows/narvaja-elevar-conversacion-v1.json` — Sub-workflow de escalamiento al equipo humano
- `03_workflows/narvaja-resumen-semanal-v1.json` — Workflow de resumen semanal automático (métricas → Telegram)
- `03_workflows/narvaja-resumen-semanal-v2.json` — Resumen semanal v2 (análisis gpt-4o-mini, JSON estructurado, HTML por Gmail con diseño elegante tipo Duolingo)
- `03_workflows/narvaja-resumen-semanal-v3.json` — Resumen semanal v3 (fix no-determinismo: conteos en JS deterministas, escalamientos detectados por regex sobre tool calls, prompt con pasos secuenciales, listas cerradas de categorías/motivos, temperature=0, seed=42)

---

### TFO — TOFO Pizza (`clients/TFO_TOFO/`)

Agente conversacional multi-canal (WhatsApp, Instagram, Facebook) para TOFO Pizza, marca de pizzas robóticas de Guadalajara (Robotic Vending de México). Arquitectura de derivación: un agente principal detecta la intención y activa subagentes especializados (RRSS, B2B, Servicio al Cliente, Reposición). El agente B2B califica prospectos y agenda llamada con director via Google Calendar + crea meeting de Zoom automáticamente (v3, 2026-06-15 — pendiente deploy).

**Dueño:** Mauricio García de la Vega · mauriciogarciadelav@gmail.com
**Técnico:** José Miguel Chumacera (ya en ManyChat, rol Agent — solo ve chats asignados)

> ⚠️ **Ojo con el nombre:** el dueño de **VTR — Venttur** se llama **igual**, Mauricio García de la
> Vega, y es **hijo** de este Mauricio. Son dos clientes distintos y dos personas distintas. El mail
> de arriba es el de TOFO. Antes de mandar una propuesta o un mensaje a "Mauricio", confirmá el
> proyecto.

**Stack:** n8n + OpenAI GPT-4.1 + Google Docs + Google Sheets + Google Calendar + Zoom + Airtable + WhatsApp/IG/FB

**Ubicaciones activas:** Flex Norte · Flex Sur · UAG · Plaza Patria · Estación Juárez

> ## ✅ Estado al 2026-08-04 — TOFO sin pendientes abiertos
> Se cerró la cola completa que venía arrastrándose desde junio. **Todo lo de abajo que diga
> "pendiente deploy" o "fix local listo" ya está aplicado en el n8n vivo** — se conserva el detalle
> histórico porque documenta el diagnóstico, no porque quede trabajo.
>
> | Ítem | Cierre |
> |---|---|
> | 🚨 P0 — Citas Zoom no se crean | ✅ **Resuelto.** El agente crea la meeting y pasa el `join_url` real |
> | 🚨 Calendar overlaps + tool rogue | ✅ **Cirugía aplicada** en n8n vivo + cleanup retroactivo del calendar de Mauricio hecho |
> | Prompts B2B v1.17 · RRSS v1.9 · Servicio v1.6 | ✅ **Deployados** (copy-paste manual al `systemMessage`) |
> | 🎥 Zoom auto-agendamiento (`chequear-disponibilidad` v3/v4) | ✅ **Deployado** |
> | 🟡 P2 — Envío automático de ficha técnica + video | ✅ **Implementado** |
> | 🟡 P2 — Plan / límite Airtable | ✅ **Decidido por el cliente** |
> | 13 preguntas a Mauricio (auditoría de datos fijos) | ❌ **Descartado** — no se persigue |
>
> ⚠️ Recordatorio operativo: los prompts siguen **hardcodeados** en el `systemMessage` del nodo AI
> Agent, así que cualquier bump futuro sigue exigiendo copy-paste manual.

**Modelos de negocio B2B:**
- Opción A — Puesta en China: $9,300 USD + IVA (cliente gestiona importación)
- Opción B — Puesta en México: $26,300 USD + IVA (llave en mano, white label)
- No se venden insumos; no hay concesiones ni franquicias

**Archivos clave:**
- `03_workflows/agente-tofo-web-b2b-rrss-v1.json` — Workflow principal antiguo (referencia histórica; 2026-06-04 reemplazado por v2 + snapshot prod)
- `03_workflows/agente-tofo-web-b2b-rrss-prod-snapshot-2026-06-04.json` — **Snapshot del workflow vivo `Agente WEB B2B y RRSS` en producción** (50 nodos, capturado 2026-06-04 vía export desde n8n). Topología real verificada: Webhook → Responder rápido ManyChat → Code in JavaScript (detecta canal) → Existe? (Airtable) → ¿Existe? → Crear contacto inicial → Separamos en partes → Split Out → Get_Audio/s → Transcribir audio/s → Aggregate → Analizar imágen → Juntar mensajes → Agente de derivacion de Lead (AI Agent principal con 8 tools). User Message vigente: `Fecha de hoy: {{ $now }}` (UTC — drift respecto a CDMX, motivo del fix v2)
- `03_workflows/agente-tofo-web-b2b-rrss-v2.json` — **Workflow main con los 5 edits del Patrón Napier aplicados** (51 nodos = 50 originales + nodo `Fechas`). Edits: (1) nodo `Fechas` Code JS entre `Juntar mensajes` y `Agente de derivacion de Lead` con `fecha_contexto` en TZ CDMX; (2) User Message del `Agente de derivacion de Lead` reemplaza `$now` por bloque `# Contexto temporal`; (3) campo `text` del subagente `Agente de B2B` agrega bloque `# Contexto temporal`; (4) `check_disponibilidad` agrega inputs `subscriber_id` / `canal` / `telefono` reusando `Code in JavaScript` para canal. **Edit 5 NO requerido**: el sub-workflow v2 se importó in-place reemplazando al v1 con el mismo ID `vpLmZ299yXJrOSBv`, así que el `workflowId.value` del toolWorkflow ya apunta correctamente al v2. Aplicado en prod por la agencia 2026-06-05.
- `03_workflows/agente-tofo-web-b2b-rrss-v3.json` — **Main v3** (50 nodos = v2 − 1 nodo Zoom huérfano). Elimina el `Create a meeting in Zoom` (id `99ac4397-36ce-4da8-acf1-fb40ee412275`, `n8n-nodes-base.zoomTool`) que estaba cableado al Agente de B2B vía `ai_tool` pero **nunca documentado en el prompt** — el LLM jamás lo invocaba. La integración Zoom vive ahora consolidada en el sub-workflow `chequear-disponibilidad-tofo-v3.json` (atomicidad: 1 tool call agenda Calendar + Zoom en un solo paso). Sin cambios en ningún otro nodo del main. **Estado:** en repo, pendiente importar a n8n.
- `03_workflows/elevar-conversacion-tofo-prod-snapshot-2026-06-03.json` — **Snapshot del workflow vivo en producción** (capturado 2026-06-03 vía export desde n8n). Topología confirmada: Switch 3-way → `Elevar Miguel` (repo) + `Elevar a Mauricio` (b2b + fallback). `active: true`
- `03_workflows/elevar-conversacion-tofo-v2.json` — Blueprint de diseño 2026-05-26 (ya aplicado en prod). Backup v1: `elevar-conversacion-tofo-v1.json`
- `03_workflows/chequear-disponibilidad-tofo-prod-snapshot-2026-06-04.json` — **Snapshot pre-fix del sub-workflow `Chequear disponibilidad | Tofo` (id `vpLmZ299yXJrOSBv`)** capturado 2026-06-04. Topología v1: Trigger → Get availability → IF Vacío → Code "Obtener intervalos" → OpenAI gpt-4.1-mini "Crear mensaje" → Switch → Crear evento / No disponible
- `03_workflows/chequear-disponibilidad-tofo-v2.json` — **Sub-workflow rediseñado** (10 nodos, cero LLM, JS determinista con Luxon TZ CDMX): Trigger (5 inputs) → Validar entrada → IF válido → Get availability con TZ explícito → Evaluar solapamiento JS → Switch libre/ocupado → Crear evento / Respond OCUPADO con alternativas / Respond NO VÁLIDO con motivo. **Estado al 2026-06-05:** importado y `active: true` en n8n con el **mismo workflowId `vpLmZ299yXJrOSBv`** (reemplaza al v1 in-place, no requiere cambiar `workflowId.value` en el main). Crear evento usa credencial `Google Calendar account 2` (id `CVeDywE8Gb5JgEjC`) — verificar con Mauricio que sea el calendar correcto. Pendiente: 8 tests pin data + smoke E2E (ver `07_testing/testing-guide-v3.md`)
- `03_workflows/chequear-disponibilidad-tofo-v3.json` — **Sub-workflow v3 con Zoom auto-agendamiento** (11 nodos = 10 v2 + nodo `Crear meeting Zoom` insertado entre el switch LIBRE y el Crear evento). Cambios: (1) nuevo nodo `n8n-nodes-base.zoom` operación `meeting.create` con `continueOnFail: true`, credencial `zoomOAuth2Api` id `TllmBz0re6WGmTw2` ("Zoom account"), duración 30 min, waitingRoom=true, muteUponEntry=true, joinBeforeHost=false, type=2 (scheduled), timezone CDMX; (2) nodo `Crear evento` actualizado: `description` ahora incluye 3 líneas Zoom (`🎥 Zoom: {join_url || 'PENDIENTE'}`, `Meeting ID`, `Start URL (host)`) — el `start_url` con ZAK token va SOLO al description (no al output del sub-workflow); (3) `Respond LIBRE` agrega `zoom_link` (string|null), `zoom_status` ('ok'|'fallback'), y reescribe `mensaje` con lógica condicional (link literal si ok / "te paso el link aparte" si fallback); (4) referencias actualizadas con `$('Evaluar solapamiento').first().json.X` para que el contexto de negocio sobreviva al pasar por el nodo Zoom. **Failure mode:** si Zoom falla (cuota, OAuth, red) el sub-workflow NO aborta — el evento de Calendar se crea igual con `PENDIENTE` y el agente le dice al lead "te paso el link aparte". **Preserva workflowId `vpLmZ299yXJrOSBv`** (reemplazo in-place al importar, el main NO necesita cambios). **Estado:** en repo, pendiente importar a n8n.
- `03_workflows/chequear-disponibilidad-tofo-v4.json` — **Sub-workflow v4 = v3 con citas de 30 minutos** (instrucción Mauricio 22/6/26). Único cambio vs v3: el evento de Google Calendar pasa de durar 1 hora a **30 minutos**. Concretamente: nodo `Validar entrada` cambia `fecha_fin: dt.plus({ hours: 1 })` → `dt.plus({ minutes: 30 })` (el `Crear evento` usa ese `fecha_fin` como `end`), y `Evaluar solapamiento` cambia `finCupo = iniCupo.plus({ hours: 1 })` → `plus({ minutes: 30 })` para coherencia del chequeo de overlap. El nodo `Crear meeting Zoom` ya tenía `duration: 30`. **Preserva workflowId `vpLmZ299yXJrOSBv`** (import = overwrite in-place). **Estado:** en repo, pendiente importar a n8n.
- `04_agents/agente-tofo-b2b-system-prompt.md` — System prompt B2B **v1.17** (en repo al 2026-06-22, **✅ DEPLOYADO al n8n vivo el 2026-08-04** — prompt hardcodeado en el `systemMessage` del nodo AI Agent, requiere copy-paste manual al actualizar) — **precio detrás del gate nombre+ubicación + citas de 30 minutos (instrucción Mauricio 22/6/26)**. Mauricio observó en prod *"el agente da precios antes de preguntar nombre y ubicación"* + pidió *"mover el dar la info de precios hacia adentro del gate"* y *"que programe las citas de 30 minutos"*. **2 cambios:** (1) **§9 reescrita REVIRTIENDO v1.9** — el precio de la máquina (USD 9.300/26.300) ya NO se da antes de capturar nombre + ubicación del lead (mismos dos datos del gate de `registrar`, ambos gates se cumplen juntos). Escenario 1 (lead pregunta precio sin gate) → pedir nombre+ubicación primero con framing de cortesía, SIN soltar la cifra; al completar ambos → `registrar` + precio. Escenario 2 (proactivo) → capturar datos, luego consent question. El gate retiene SOLO la cifra; el resto (funcionamiento, specs, diferencias estructurales sin números, urgencia) fluye libre. Ajustes en cadena: §8, §🔟 ("Si pregunta precios"/"diferencia A vs B" con guard de gate), respuesta canónica concesión sin cifras si gate no cumplido. (2) **citas de 30 min** — §Cómo agendar ("1 hora"→"30 min", última 12:00 termina 12:30) + §🔟 dossier ("15 min"→"30 min") + sub-workflow `chequear-disponibilidad-tofo-v4.json`. **Testing v9 §Q** (gate, gpt-4.1): 8/8 respuestas del agente verificadas correctas por inspección manual (gate enforced al 100%); juez gpt-4o-mini rota 1 false/corrida por artefacto (marca "precios oficiales"/"40% arancel" como precio, no es fallo del prompt). **Sin tocar RRSS** (precio de menú al consumidor = retail, no aplica el gate de lead) ni los otros 3 subagentes. Backup v1.16 preservado. Hereda v1.16 — datos canónicos de funcionamiento. Aprovecha la ficha técnica oficial PNG (`00003318-brochure Maquina TOFO Pizza.png`) que Mauricio envió al chat el 10/6/26 — ya pre-aprobada como asset por él, ya se envía al lead vía `enviar_ficha_tecnica`, así que todo lo que está literalmente en ella es contenido autorizado citable sin riesgo de alucinación. **3 cambios concretos**: (1) §🍕 FUNCIONAMIENTO — agrega **DATO CANÓNICO #4 (HORNO Y COCCIÓN)**: horno de convección de aire eléctrico giratorio + 350°C + 3-5 min + 60 pizzas/día producción + sin refrigeración activa (insumos pre-fríos). Actualiza "Tiempo total al cliente" de "menos de 3 minutos" → "3 a 5 minutos" (ficha autoritativa). El bloque "🚫 PROHIBIDO inventar" mantiene 6 items aún sin canonical (quién carga / frecuencia de recarga / **capacidad de almacenamiento interna ≠ capacidad de producción** / tiempo de conservación / receta / **sabores custom B2B / white label**). (2) §⚙️ INSTALACIÓN — peso 500 → **550 kg** + voltaje ampliado a "**220V / 60Hz, 35A, potencia máxima 6.5 kW**" (sin tirar la amperaje recomendada existente). (3) NUEVA sección **§📋 ESPECIFICACIONES TÉCNICAS (ficha oficial)** insertada entre §📱 CONTROL y §🔧 REFACCIONES: dimensiones 1800×1100×2350 mm · 550 kg · pantalla 51" táctil vertical · 4G + Wi-Fi · sistema de pago (Tarjeta + Contactless operativos / QR / App próximamente) · operación 24/7 · cocción 350°C / 3-5 min · capacidad producción 60 pizzas/día · refrigeración N/A. (4) Anti-alucinación reescrita: 8 preguntas que antes derivaban al director ahora se responden con info canónica de §🍕 + §📋 (tipo de horno, temperatura, tiempo cocción, capacidad producción, dimensiones, peso, consumo eléctrico, pago, conectividad); 6 preguntas siguen pendientes de Mauricio (recarga, almacenamiento exacto, conservación, sabores custom B2B, proceso interno). Línea "Especificaciones técnicas" del bloque "SÍ se entregan" actualizada con specs nuevas. **Items no cubiertos por la ficha** (siguen como "lo aterriza el director" si el lead pregunta, sin invención): quién carga las pizzas / frecuencia de recarga / capacidad de almacenamiento exacta / tiempo de conservación de pizzas pre-elaboradas / sabores custom B2B white label. NO son pedido del cliente — son zonas que la ficha no cubre y se respetan vía anti-alucinación, NO se persiguen como pending. Backup v1.15 preservado. Hereda v1.15 (REGLA ABSOLUTA #4 anti-tools-rogue Calendar/Zoom), v1.14 (§0 reglas absolutas + criterio en archivos), v1.13 (tools ficha técnica + video), v1.12 (gate Airtable nombre+ubicación), v1.9 (precio como filtro temprano + consent question), v1.6 (sección 🍕 inicial + PROHIBICIÓN ABSOLUTA cita sin tool + funcionamiento canónico).
- `04_agents/agente-tofo-b2b-system-prompt-v1.15.md` — Backup B2B v1.15 (último deployado al n8n vivo · pre-bump datos canónicos funcionamiento)
- `04_agents/agente-tofo-b2b-system-prompt-v1.16.md` — Backup B2B v1.16 (pre-gate precio · datos canónicos funcionamiento)
- `04_agents/agente-tofo-b2b-system-prompt-v1.8.md` — Backup B2B v1.8 (último de pre-reunión 18/6/26 · versión "soltar precio proactivo en 2 turnos" superseded por consent question de v1.9, nunca llegó a prod)
- `04_agents/agente-tofo-b2b-system-prompt-v1.7.md` — Backup B2B v1.7 (último de pre-bump 17/6/26)
- `04_agents/agente-tofo-b2b-system-prompt-v1.6.md` — Backup B2B v1.6 (último de pre-Zoom auto-agendamiento)
- `04_agents/agente-tofo-b2b-system-prompt-v1.5.md` — Backup B2B v1.5 (post-incidente confusión moneda Oscar Amaya, pre-incidente Mauricio 2026-06-08)
- `04_agents/agente-tofo-b2b-system-prompt-v1.4.md` — Backup B2B v1.4 (post-respuestas Mauricio, pre-incidente Oscar)
- `04_agents/agente-tofo-b2b-system-prompt-v1.3.md` — Backup B2B v1.3 (último de pre-respuestas Mauricio)
- `04_agents/agente-tofo-b2b-system-prompt-v1.2.md` — Backup B2B v1.2
- `04_agents/agente-tofo-b2b-system-prompt-v1.1.md` — Backup B2B v1.1
- `04_agents/agente-tofo-servicio-system-prompt.md` — System prompt Servicio al Cliente **v1.6** (en repo al 2026-06-22, ✅ DEPLOYADO al n8n vivo el 2026-08-04 — prompt hardcodeado). **Mismo fix de tiempo de cocción que RRSS v1.9 y B2B v1.16**: 3 referencias "menos de 3 minutos" → "3 a 5 minutos" (en §4 lista temas atendidos + §🍕 DATO CANÓNICO #2 + respuesta modelo §5 Funcionamiento). Sin cambios en otras secciones. Hereda v1.5 (sección 🍕 + anti-aluc post incidente Mauricio 2026-06-08). Backup v1.5 preservado.
- `04_agents/agente-tofo-servicio-system-prompt-v1.5.md` — Backup Servicio v1.5 (último vivo en n8n al 22/6 · post incidente Mauricio 2026-06-08 — agrega sección "🍕 Cómo funciona la máquina" + refuerza anti-aluc)
- `04_agents/agente-tofo-servicio-system-prompt-v1.4.md` — Backup Servicio v1.4 (pre-incidente Mauricio 2026-06-08)
- `04_agents/agente-tofo-servicio-system-prompt-v1.3.md` — Backup Servicio v1.3 (último de pre-respuestas Mauricio)
- `04_agents/agente-tofo-servicio-system-prompt-v1.2.md` — Backup Servicio v1.2
- `04_agents/agente-tofo-reposicion-system-prompt.md` — System prompt Reposición **v1.4** (naming oficial sucursales en pregunta de ubicación + bloque anti-alucinación común: NO compartir tel/email/contratos + refuerzo no reembolsos en cualquier forma). Sin cambios en bump 2026-06-08 (no maneja descripción técnica de la máquina).
- `04_agents/agente-tofo-reposicion-system-prompt-v1.3.md` — Backup Reposición v1.3 (último de pre-respuestas Mauricio)
- `04_agents/agente-tofo-reposicion-system-prompt-v1.1.md` — Backup Reposición v1.1
- `04_agents/agente-tofo-derivacion-system-prompt.md` — System prompt Derivación **v1.4** (bloque anti-alucinación común: NO dar email/teléfono/contratos; usar `fecha_contexto` del User Message como fuente de verdad; `elevar_conversacion` solo para B2B compra o Repo falla; NO elevar para consultas administrativas genéricas). Sin cambios en bump 2026-06-08 (no agenda ni describe la máquina).
- `04_agents/agente-tofo-derivacion-system-prompt-v1.3.md` — Backup Derivación v1.3 (último de pre-respuestas Mauricio)
- `04_agents/agente-tofo-derivacion-system-prompt-v1.2.md` — Backup Derivación v1.2
- `04_agents/agente-tofo-rrss-system-prompt.md` — System prompt RRSS **v1.9** (en repo al 2026-06-22, ✅ DEPLOYADO al n8n vivo el 2026-08-04 — prompt hardcodeado). **Alinea tiempo de cocción a la ficha oficial**: 11 referencias "menos de 3 minutos" / "en 3 minutos" → "3 a 5 minutos" / "en pocos minutos" (8 en respuestas modelo de marketing, 1 en sección 🍕 DATO CANÓNICO #2, 1 en tabla resumen, 1 en allowed phrases list línea 242). Origen: smoke S3 contra el live detectó la inconsistencia — la ficha técnica oficial de Mauricio dice "Tiempo de cocción: 3 a 5 minutos". Sin cambios en otras secciones. Hereda v1.8 (gate escape hatch fix) + v1.7 (field list `registrar` v2) + v1.6 (GATE Airtable nombre+ubicación). Backup v1.8 preservado.
- `04_agents/agente-tofo-rrss-system-prompt-v1.9.md` — Backup RRSS v1.9 (= snapshot del current en repo · ✅ deployado 2026-08-04)
- `04_agents/agente-tofo-rrss-system-prompt-v1.5.md` — Backup RRSS v1.5 (post incidente Mauricio 2026-06-08 — descripción funcionamiento autorizada + sección 🍕)
- `04_agents/agente-tofo-rrss-system-prompt-v1.4.md` — Backup RRSS v1.4 (pre-incidente Mauricio 2026-06-08)
- `04_agents/agente-tofo-rrss-system-prompt-v1.3.md` — Backup RRSS v1.3 (último de pre-respuestas Mauricio)
- `04_agents/agente-tofo-rrss-system-prompt-v1.1.md` — Backup RRSS v1.1
- `07_testing/testing-guide-v7.md` — **Testing guide v7 (bump v1.9 reunión Mauricio 18/6/26)** — hereda §A/§B/§C/§G/§H/§I/§K/§Z íntegros de v6 + cambios: (a) **§J reescrito completo** — "Precio proactivo + productos viejos" de v1.8 ya NO aplica; nuevos casos verifican el flow consent: agente recoge nombre + ubicación → pregunta literal "¿quieres saber el precio de la máquina TOFO Pizza?" → solo si lead confirma suelta precio + ficha técnica; anti-regression "soltar proactivo" (casos donde v1.8 hubiera soltado pero v1.9 debe preguntar consent primero); anti-regression productos viejos (concesión/alquiler/renta sin inventar). (b) **§M nuevo "Ficha técnica + video funcionamiento"** — verifica los 2 triggers exactos: pregunta de costo (post-consent positivo) → invoca `enviar_ficha_tecnica`; pregunta "cómo funciona" → invoca `enviar_video_funcionamiento`; anti-regression "tenemos prohibido mandar videos" (verbatim que el agente NUNCA debe decir según Mauricio). (c) **§N nuevo "Airtable captura"** — verifica que el agente sigue completando los campos de captura del lead aún cuando hay derivación posterior; cubre regression del incidente del renglón 488+ donde leads quedaban con "contacto a redes sociales" sin info adicional. (d) **§Zoom esqueleto nuevo** — casos para verificar end-to-end que el Zoom meeting efectivamente se crea en el dashboard de Zoom + el join_url está activo (no solo que el agente lo escribe en el mensaje). Detalle de implementación queda para cuando se resuelva la hipótesis de credencial mal configurada. **§D actualizado** con bloqueante v1.9 completo antes de promover.
- `07_testing/testing-guide-v5.md` — **Testing guide v5 (Zoom auto-agendamiento)** — hereda §A/§B/§C/§G íntegros de v4 + cambios: (a) **§A actualizado** con A6/A8 que verifican el shape ampliado del `Respond LIBRE` (incluye `zoom_link` + `zoom_status`); (b) **A9 nuevo**: happy path Zoom — el `join_url` matchea `^https://.+\.zoom\.us/j/\d+\?pwd=.+$` y aparece literal en `mensaje`; (c) **A10 nuevo**: fallback Zoom failure — forzar falla del nodo Zoom (cambiar `type=999` o deactivate), verificar `zoom_status: 'fallback'` + `zoom_link: null` + Calendar event creado igual con `PENDIENTE`; (d) **B16 nuevo**: E2E conversación B2B verificando que el agente incluye `join_url` literal en confirmación al lead; (e) **B17 nuevo**: E2E fallback — agente usa "te paso el link aparte" sin inventar; (f) **§Z nuevo**: 5 verificaciones manuales en Zoom dashboard + Calendar (meeting aparece programada, `join_url` lleva al lobby, `start_url` arranca como host, description tiene 3 líneas Zoom, limpieza opcional post-test); (g) **§D actualizado**: checklist con A9/A10/B16/B17/Z1-Z5 + prompt B2B v1.7 + sub-workflow v3 + main v3.
- `07_testing/testing-guide-v4.md` — **Testing guide v4 (post-incidente 2026-06-08)** — hereda §A/§B/§C de v3 + agrega **§G Regression del incidente Mauricio** (18 casos críticos): §G.1 prohibición cita sin tool (6 casos incluyendo intento de escape emocional) · §G.2 filtro horario fuera ventana NO invoca tool · §G.3 funcionamiento canónico de la máquina (6 casos: verbatim Ricardo, "¿es congelada?", "¿masa fresca?", "¿cuántas guarda?") · §G.4 prioridad PRECIO (3 casos) · §G.5 coherencia RRSS sin "masa fresca" · §H notas operativas con triage por tipo de fallo + queries SQL
- `07_testing/testing-guide-v3.md` — Testing guide v3 (pre GO-LIVE) — cubre cambios v1.4 + B2B v1.5. §A 8 tests pin data del sub-workflow v2 · §B 15 tests conversación E2E · §C 12 regression incidente Oscar Amaya · §D checklist promoción
- `07_testing/testing-guide-v2.md` — Guía de testing v2 (38 casos: derivación, B2B, servicio, reposición, RRSS + estimaciones con variables completas) [histórico]
- `06_docs/incidente-info-inventada-y-cita-2026-06-08.md` — **Postmortem incidente Mauricio 2026-06-08** (cita fantasma + info técnica inventada). §1 verbatim Mauricio · §2 3 screenshots descritos (Oscar/Ricardo/Isauro) · §3 diagnóstico 4 fallas (cita sin tool, info inventada, precio tardío, cita doble) · §4 7 reglas nuevas (prohibición absoluta cita, filtro pre-tool, funcionamiento canónico, prioridad precio, frase RRSS, sección replicada, anti-aluc reforzado) · §5 aplicación · §6 datos NO autorizados pendientes para Mauricio (quién carga, capacidad, conservación, tipo horno, sabores custom B2B)
- `06_docs/guia-asignacion-fallas-miguel-2026-05-26.md` — Guía de contexto inicial: asignación automática de chats de fallas a Miguel (Técnico) via ManyChat Live Chat
- `06_docs/guia-edits-n8n-asignacion-miguel-2026-06-03.md` — **Guía de verificación + pendientes** (no de edits): el workflow vivo ya tiene los 3 nodos cableados (`Elevar Miguel` / `Elevar a Mauricio` / Switch 3-way) y está activo. Documenta el estado, los pendientes Google Docs + ManyChat + 7 tests E2E, riesgos conocidos (doble escalamiento, token hardcoded)
- `06_docs/datos-fijos-auditoria-2026-06-04.md` — **Auditoría de datos fijos en los 5 prompts v1.3** (2026-06-04). ⚠️ **Las 13 preguntas a Mauricio de §3 quedaron descartadas el 2026-08-04** — no se persiguen; el doc vale como registro de las inconsistencias detectadas, no como lista de tareas. Contenido: §1 single source of truth · §2 inconsistencias internas (Plantas Flex fantasma, Al Pastor/Pastor, Modelo Base $129 vs realidad $119-139, arancel 40% sin fecha, ventana B2B inconsistente prompt vs sub-workflow) · §3 13 preguntas a Mauricio (bloqueantes: email/teléfono/política cancelación/garantía/devolución/Plantas Flex/arancel) · §4 bloque anti-alucinación común para v1.4 + adaptaciones por prompt. **Update 2026-06-05:** Mauricio respondió — ver doc `respuestas-mauricio-datos-fijos-2026-06-05.md`
- `06_docs/preguntas-mauricio-datos-fijos-2026-06-04.md` — Versión WhatsApp-friendly de §3 de la auditoría, lista para copy-paste al cliente
- `06_docs/respuestas-mauricio-datos-fijos-2026-06-05.md` — **Respuestas de Mauricio integradas** (2026-06-05): respuestas verbatim + mapeo a 13 preguntas (10 resueltas, 3 abiertas) + datos canónicos actualizados (sucursales con naming oficial, 5 Google Maps links, pricing por grupo Estaciones+UAG vs Flex, arancel 15%→40% transitorio con stock bajo, identidad EMMA Vivanti, política comunicación) + delta por prompt para v1.4 + vacíos restantes manejados con anti-alucinación + canalizar por chat
- `06_docs/incidente-confusion-moneda-2026-06-05.md` — **Incidente Oscar Amaya** (2026-06-05): el agente B2B v1.4 prometió Opción B a un lead con presupuesto de $250.000 MXN sin validar moneda (Opción B son $26.300 USD ≈ $460.000 MXN — no alcanza). Diagnóstico: faltaba (a) protocolo de validación de moneda y (b) opción de financiamiento como red de seguridad. Solución: bump B2B v1.4 → v1.5. Documenta los 4 reglas del Protocolo de moneda, la nueva sección de Financiamiento externo (banco/arrendadora/financiera con factura), las 5 respuestas modelo nuevas y la tabla de decisión presupuesto vs opción.
- `06_docs/guia-fix-chequear-disponibilidad-2026-06-04.md` — **Guía operativa para aplicar el fix del sub-workflow `Chequear disponibilidad`** (v1 → v2). Lista 10 bugs detectados (TZ sin offset, LLM no determinista, prompt LLM contradictorio, sin validación día/fecha/minutos, evento sin timeZone, sin retorno estructurado, sin patrón Napier), 6 pasos para aplicar, 8 tests con pin data + smoke E2E, plan de rollback
- `06_docs/guia-fix-fecha-contexto-main-2026-06-04.md` — **Guía para agregar nodo `Fechas` al main workflow (Patrón Napier adaptado a CDMX)**: snippet Code JS listo para pegar (TZ America/Mexico_City), dónde insertarlo (Webhook/Normalize → Fechas → AI Agent), cómo inyectar `fecha_contexto` al User Message, y cómo cablear los 3 inputs nuevos (`subscriber_id`, `canal`, `telefono`) al toolWorkflow `check_disponibilidad`

**Asignación de fallas:** Cuando el Agente de Reposición o Servicio invoca `elevar_conversacion` con `tipo='repo'`, el sub-workflow `Elevar conversación | Tofo` enruta vía Switch a Telegram Miguel (`8067142805`) + HTTP a ManyChat con flow_ns `content20251129220130_658273` (asigna chat a Miguel + notifica + pausa bot). Ramas `b2b` y fallback van a Mauricio (`5839874323` + flow_ns `content20260526142445_613819`). Miguel (rol Agent) solo ve chats asignados. Mauricio conserva visibilidad total. **Estado al 2026-06-03:** ya cableado y activo en prod. Auto-cleanup del tag `FALLA_TECNICA` queda manual por Miguel (descartado).

**Fix sub-workflow Chequear disponibilidad — 2026-06-05 (en prod, active):** el flujo v1 (`vpLmZ299yXJrOSBv`) tenía 10 bugs (TZ México sin offset, LLM gpt-4.1-mini evaluando solapamiento con prompt contradictorio, sin validaciones Lun-Vie/fecha pasada/minutos, evento sin `timeZone`, sin retorno estructurado). **Resuelto:** sub-workflow v2 reemplaza al v1 in-place (mismo ID `vpLmZ299yXJrOSBv`) con 10 nodos JS determinista + Luxon TZ CDMX + ventana Lun-Vie inicios 10/11/12 + retorno estable `{libre, motivo, mensaje, alternativas}`. Main con Patrón Napier completo (nodo `Fechas` + `# Contexto temporal` en User Message + B2B subagente + 3 inputs nuevos al toolWorkflow). El `Crear evento` del sub-workflow usa credencial `Google Calendar account 2` (diferente al de Get availability) — verificar con Mauricio el calendar destino. **Pendiente solo:** (a) ejecutar `07_testing/testing-guide-v3.md` (§A 8 pin data + §B 15 conversación E2E + §C 12 regression Oscar); (b) post-tests OK → promover TESTING → LIVE.

**Bump B2B v1.4 → v1.5 — incidente confusión moneda Oscar Amaya (2026-06-05 PM):** el agente B2B v1.4 prometió Opción B ($26.300 USD ≈ $460k MXN) a un lead con presupuesto $250.000 sin validar moneda (probablemente MXN). Caso Oscar Amaya — Mauricio redirige manualmente. Solución en B2B v1.5: (a) **Protocolo de moneda** 4 reglas con tabla decisión (cubre B / cubre solo A sticker / no cubre A); (b) TC referencial ~17.5 MXN/USD + equivalencias canónicas en Opción A (~$165k MXN) y Opción B (~$460k MXN); (c) **Sección Financiamiento externo**: TOFO no da financiamiento directo, entrega factura para banco/arrendadora/financiera (no recomendar específico); (d) 6 respuestas modelo nuevas; (e) Regla anti-aluc 1.5 expresa: NUNCA afirmar "alcanza" sin moneda confirmada. Detalle: `06_docs/incidente-confusion-moneda-2026-06-05.md`. Regression test en `07_testing/testing-guide-v3.md` §C.

**☢️ Incidente Mauricio 2026-06-08 — cita fantasma + info técnica inventada (CRÍTICO):** Mauricio reportó 4 fallos del agente en producción: (1) Oscar — agente confirmó "mañana 9 AM" sin invocar `check_disponibilidad`, hora fuera ventana 10/11/12 y el evento nunca llegó al calendar; (2) Ricardo — agente tardó en dar precio (priorizó cualificación sobre respuesta directa); (3) Ricardo — agente inventó "la máquina hace la pizza desde cero con base fresca + ingredientes separados" (falso: pizza viene **pre-horneada al 75% + ingredientes frescos**, la máquina solo termina el horneado al momento); (4) Isauro — segundo caso de cita fantasma + doble booking. **Bumps aplicados (2026-06-08):** B2B **v1.5 → v1.6** (5 fixes: sección NUEVA "🍕 FUNCIONAMIENTO DE LA MÁQUINA" con info canónica autorizada por Mauricio + PROHIBICIÓN ABSOLUTA de confirmar cita sin tool call previa exitosa + filtro pre-tool para horarios fuera de ventana + prioridad PRECIO sobre cualificación + anti-aluc reforzado con "funcionamiento interno" como dato prohibido). RRSS **v1.4 → v1.5** (reemplaza frase "Masa fresca, ingredientes premium...Cero congelados" por descripción autorizada + sección "Cómo funciona la máquina" replicada). Servicio **v1.4 → v1.5** (idem). Derivación + Reposición sin cambios. Testing guide **v4** con §G regression (18 casos críticos). Postmortem: `06_docs/incidente-info-inventada-y-cita-2026-06-08.md`. Casos Oscar e Isauro redirigidos manualmente por Mauricio. **Prompts v1.6/v1.5/v1.5 ya vivos en n8n ✅** (copy-paste a Google Docs / nodos ya aplicado por la agencia). **Bloqueante único para LIVE:** ejecutar §G de testing-guide-v4 (18 casos críticos) sobre el agente vivo + §A/§B/§C heredados de v3. **Datos pendientes para Mauricio** (manejados con anti-alucinación + "lo aterriza el director"): quién carga la máquina, capacidad de almacenamiento, tiempo de conservación de pizzas pre-horneadas, tipo de horno, sabores custom B2B white label.

**🎥 Zoom auto-agendamiento — 2026-06-15 · ✅ DEPLOYADO 2026-08-04:** Mauricio pidió (mensaje WPP 2026-06-08 19:31) que el agente "agende automáticamente la conferencia en Zoom y le mande el enlace al contacto". Lectura: cuando el sub-workflow confirma una cita en Google Calendar, debe crear también una meeting de Zoom única (no PMI estático) y el agente debe pasar el `join_url` al lead en el mismo mensaje de confirmación. Hoy Mauricio coordina manualmente post-agendamiento — fricción que el incidente del 08 ya golpeó la confianza. **Hallazgo clave durante exploración:** existía un nodo `n8n-nodes-base.zoomTool` ("Create a meeting in Zoom", id `99ac4397-36ce-4da8-acf1-fb40ee412275`) en el main v2 cableado al Agente de B2B vía `ai_tool` PERO **nunca documentado en el prompt v1.6** → el LLM jamás lo invocaba. Por eso el feedback de Mauricio nunca se cumplió aunque la infraestructura estuviera ahí. **Credencial Zoom ya existe**: `zoomOAuth2Api` id `TllmBz0re6WGmTw2` ("Zoom account"). **Solución consolidada:** (a) `chequear-disponibilidad-tofo-v3.json` — sub-workflow v3 con nodo `Crear meeting Zoom` insertado entre el switch LIBRE y `Crear evento`, con `continueOnFail: true`. Failure mode: si Zoom falla, el evento Calendar se crea igual con `description` que dice `🎥 Zoom: PENDIENTE` y el `Respond LIBRE` devuelve `zoom_status: 'fallback'` + mensaje fallback ("te paso el link aparte"). Decisiones: duración 30 min, waitingRoom=true, type=2 scheduled, timezone CDMX. `start_url` y `password` van SOLO al `description` del Calendar (NUNCA al output del sub-workflow → riesgo de leak por LLM). `zoom_link` que cruza al agente = `join_url` con passcode embebido. Preserva workflowId `vpLmZ299yXJrOSBv`. (b) `agente-tofo-web-b2b-rrss-v3.json` — main sin el nodo zoomTool huérfano (50 nodos = v2 − 1). (c) B2B **v1.6 → v1.7** — shape ampliado documentado + 2 RESPUESTAS SUGERIDAS según `zoom_status` + nueva regla anti-link-inventado v1.7 (NUNCA inventar/acortar/usar PMI/usar link de cita anterior). (d) `testing-guide-v5.md` — hereda íntegro v4 + A6/A8 con shape nuevo + A9 happy Zoom + A10 fallback + B16/B17 E2E + §Z 5 verificaciones manuales Zoom dashboard. **Plan**: `/Users/camilo/.claude/plans/mauricio-de-tofo-quiere-reflective-hare.md`. **Pendiente deploy**: importar sub-workflow v3 a n8n (overwrite v2 in-place vía workflowId), importar main v3, subir prompt v1.7 al Google Doc vivo, ejecutar testing-guide-v5 (§A + §B + §C + §G + §Z), promover TESTING → LIVE post-pass. Estimado 3h 30min. **Nota plan Zoom**: free tier limita a 40 min/meeting — verificar con Mauricio si tiene Pro (la duración 30 min fija no debería tocar el techo, pero confirmar). **Bump consolidado**: por el bump del 17/6 (puntos 3/6/7 del análisis WhatsApp) — ver bloque siguiente — los 2 deploys se consolidan en 1 (subir prompt v1.8 al Google Doc + importar workflows v3 + correr testing v6 completo en una sola pasada).

**🔧 Bump prompt B2B v1.7 → v1.9 + testing v7 — análisis WhatsApp Mauricio 17/6/26 + reunión Mauricio 18/6/26 · ✅ DEPLOYADO 2026-08-04:** análisis del export completo de WhatsApp (`/Users/camilo/Downloads/WhatsApp Chat - Tofo | la agencia/_chat.txt`, 1/4/26 → 15/6/26) + reunión 28 min con Mauricio 18/6/26 consolidan 6 fixes en un único bump v1.7 → v1.9. La versión intermedia v1.8 (build 17/6 con regla "soltar precio proactivo en 2 turnos") quedó SUPERSEDED por la reunión del 18/6 antes de salir a prod — se preserva como backup `agente-tofo-b2b-system-prompt-v1.8.md` para referencia. **6 fixes consolidados en v1.9**: (3a) **Checkpoint mental anti-ghost-booking** dentro de PROHIBICIÓN ABSOLUTA que obliga al modelo a preguntarse antes de cada confirmación "¿invoqué la tool y vi `libre: true`?"; resuelve incidentes Oscar/Ricardo/Isauro 8/6 + contactos "gp"/"bally hoo" 4/6 (leads jamás materializados en Airtable). (3b) **Timezones MX** — Mauricio 4/6/26: "que tome en cuenta las diferencias horarias". PASO 1.5 nuevo: agente pregunta zona (Centro/Pacífico/Sonora) si lead no está en Jalisco/CDMX/centro; PASO 4 tabla conversión a CDMX (-06:00/-07:00/-08:00 según DST); ISO siempre en `-06:00` para que director vea hora CDMX en calendar; confirmación al lead incluye "(hora CDMX)" además de "(hora local)". (6) **Precio con consent question — REFINADO POR REUNIÓN 18/6**: la regla v1.8 era "soltar precio proactivo apenas detecte intención de compra"; Mauricio el 18/6 la CONTRADIJO y pidió el flow opuesto. Cita textual 18/6: *"Cuando le diga el nombre y dónde está, le pregunta si quiere saber el precio de la máquina, la TOFO pizza, y si dice que sí, le da el precio. Y después ahí vemos si la persona está interesada o no."* Fix v1.9: el agente recoge nombre + ubicación, luego pregunta literal "¿quieres saber el precio de la máquina TOFO Pizza?" y SOLO con sí explícito suelta precio. Se mantiene la prohibición de inventar productos viejos (concesión/alquiler/renta/$200k inversión inicial). (7) **Financiamiento proactivo (5/6/26)** — lenguaje pasivo "puedes buscar" → activo "te apoyamos a buscar"; agente ofrece de oficio cuando hay gap presupuesto. (8) **Archivos autorizados — ficha técnica + video** (Mauricio 18/6). Cita: *"Cuando te pregunta el costo, inmediatamente manda la ficha técnica. Pregunta costo, ficha técnica. ¿Cómo funciona la máquina? Le pasas el video. Porque ahora la gente está contestando 'tenemos prohibido mandar videos'. No es cierto."* 2 triggers exactos documentados: precio (post-consent) → ficha técnica PDF; "cómo funciona" → video MP4. (9) **2 tools nuevas documentadas en el prompt**: `enviar_ficha_tecnica` + `enviar_video_funcionamiento` — sub-workflows + asset hosting pendientes de build separado. **Testing**: `07_testing/testing-guide-v7.md` hereda §A/§B/§C/§G/§H/§I/§K/§Z íntegros de v6 + §J reescrito (consent question reemplaza "soltar proactivo"), §M nuevo (ficha técnica + video), §N nuevo (Airtable captura), §Zoom esqueleto. **Plan v2 fuente de verdad**: `/Users/camilo/.claude/plans/1-qued-resuelto-2-enchanted-trinket.md`. **Pendiente deploy**: subir prompt v1.9 al Google Doc vivo, importar sub-workflow v3 + main v3 a n8n, build de los sub-workflows `enviar_ficha_tecnica` + `enviar_video_funcionamiento` (incluido asset hosting de PDF + MP4), correr testing-guide-v7 completo, promover TESTING → LIVE post-pass. **NO se modifica sub-workflow chequear-disponibilidad v3 ni main v3 para TZ** — TZ se maneja vía prompt; el JS permanece igual.

**🟡 P2 — Envío automático ficha técnica + video funcionamiento (reunión Mauricio 18/6/26) · ✅ IMPLEMENTADO 2026-08-04:** Mauricio pidió que el agente mande automáticamente 2 assets ya pre-aprobados ante triggers exactos. Cita textual: *"Cuando te pregunta el costo, inmediatamente manda la ficha técnica. Pregunta costo, ficha técnica. ¿Cómo funciona la máquina? Le pasas el video. Porque ahora la gente está contestando 'tenemos prohibido mandar videos'. No es cierto."* **Triggers canónicos**: (a) post-consent positivo de precio → invoca `enviar_ficha_tecnica` (PDF con specs + precios + términos) Y suelta el precio en texto en el mismo turno; (b) lead pregunta "¿cómo funciona la máquina?" / "¿cómo opera?" / similar → invoca `enviar_video_funcionamiento` (MP4 corto, ~30-60s) Y responde con la descripción canónica de v1.6 ("pizza pre-horneada al 75% + ingredientes frescos, la máquina termina el horneado al momento"). **Pendiente build**: (1) recibir de Mauricio el PDF ficha técnica + el MP4 video (assets); (2) hostearlos en URL pública estable (recomendación: Cloudflare R2 o S3 público; descartar Google Drive porque WhatsApp Business no maneja bien los links); (3) build de 2 sub-workflows n8n `sys-enviar-ficha-tecnica` + `sys-enviar-video-funcionamiento` que envían el media vía ManyChat sendFlow + responden el shape estándar al agente; (4) cablear las 2 tools al main + actualizar `workflowId` en el toolWorkflow del agente B2B. Documentado en prompt v1.9 (tools 8 y 9 nuevas). Casos §M de `testing-guide-v7.md` cubren esto end-to-end.

**🟡 P2 — Plan / límite Airtable (reunión Mauricio 18/6/26) · ✅ CERRADO 2026-08-04 — el cliente decidió:** la base Airtable de TOFO está acercándose al límite de records del plan Free (1.000 records por base / 1.200 records por workspace según plan vigente). Con ~1.113 leads vivos + crecimiento orgánico, el cliente necesita decidir entre upgrade a Team plan (~USD 24/mes) o purga periódica de leads viejos sin actividad. Decisión queda en manos de Mauricio — la agencia solo recomienda y propone alternativas. Doc nuevo con análisis costo/beneficio + 3 opciones (upgrade / purga / migración a Supabase): `06_docs/airtable-plan-decision-2026-06-19.md`. **Pendiente:** mandar el doc a Mauricio + esperar respuesta. Esta decisión NO bloquea el deploy de v1.9 — si Mauricio elige purga, el script de cleanup se cotiza aparte (~2h trabajo, USD 130 one-shot o incluido en mantenimiento mensual si tiene activo).

**⚠️ P1 — Diferencia ManyChat (1494) vs Airtable (1113) ≈ 400 leads (reunión Mauricio 18/6/26):** Mauricio compartió que ManyChat reporta ~1494 conversaciones únicas mientras que Airtable tiene ~1113 leads registrados — un gap de ~400 leads (~27%) que tuvieron conversación pero nunca llegaron a Airtable. Criterio operativo cerrado con Mauricio en la reunión: **lead con interés = lead que dio nombre + ubicación**. Lo que no llegó a ese piso queda como "conversación curiosa" y NO debe materializar como lead en Airtable. **Hipótesis del gap**: (a) "conversaciones curiosas" legítimas (intent vago, sin nombre/ubicación) → expected, NO bug; (b) parte del gap es el incidente Airtable captura (renglón 488+) — leads que sí dieron nombre + ubicación pero el agente no escribió a Airtable; (c) leads que escribieron una sola vez (ej. "hola") y nunca volvieron → expected pero podrían contarse como interés bajo. **Plan de validación**: (1) muestrear 50 conversaciones ManyChat sin lead correspondiente en Airtable → clasificar por categoría (curiosa / capturó pero no escribió / one-shot); (2) si >30% son del bucket "capturó pero no escribió" → confirmar que es el mismo bug del bloque anterior y se resuelve junto; (3) reportar números limpios a Mauricio post-fix para que tenga un dashboard real de conversión.

**✅ 2026-06-21 RESUELTO — Fix Airtable Gate nombre+ubicación (sesión completa con smoke validation 4/4 PASS).** Combina la solución del punto P1 "Airtable captura" (creación de contactos vacíos) Y el punto #4 de la lista Mauricio 18/6/26 (criterio nombre+ubicación). **Cambios estructurales**: (1) **`Crear contacto inicial` eliminado del main workflow** — era el causante de los ~580 records vacíos "contacto a redes sociales" del renglón 488+. Topología nueva: `Webhook → Responder rápido ManyChat → Code in JavaScript → Separamos en partes` (sin Airtable en el path inicial). (2) **Tool `registrar` rediseñada (schema v2)**: 14 campos = 6 determinísticos + 8 `$fromAI` con descripciones non-empty (anti bug Zod). Nuevo campo `Nombre completo` (LLM, dicho por el lead en chat) — distinto de `Nombre / Usuario` (determinístico, display name del webhook). Campo `Whatsapp` poblado por webhook cuando canal=WPP. Campo `Ultimo contacto` nuevo. (3) **`Dias de proceso` migrado a fórmula Airtable** `DATETIME_DIFF(NOW(), {Fecha captado}, 'days')` — antes hardcoded `0`. (4) **Derivación restaurado al rol real** — durante la sesión descubrimos que el `Agente de derivacion de Lead` (main) tenía systemMessage de 52KB que arrancaba con "Eres el Agente B2B Oficial" (era un B2B clone), no un derivador. Restaurado del snapshot 4/6/26 al derivador real de 7KB que delega a subagentes. Sin este fix los subagentes B2B/RRSS nunca recibían el flow y `registrar` nunca se invocaba. **Prompts bumpeados**: B2B v1.9 → **v1.10** (GATE) → **v1.11** (timing "EN EL MISMO TURNO" + field list real) → **v1.12** (cierra escape hatch `"México - sin ciudad confirmada"` que el LLM usaba para bypassear el gate). RRSS v1.5 → **v1.6** → **v1.7** → **v1.8** (mismos fixes adaptados). **Bugs encontrados durante el deploy**: (a) tool no estaba cableada al main → user la cableó; rechazada como parche en favor de restaurar Derivación; (b) prompt v1.10 tenía leftover "preferentemente cerca del final" → el LLM defería siempre → fix v1.11; (c) v1.11 dejaba escape hatch en field instruction `"México - sin ciudad confirmada"` → SMOKE 2 creó row con Federico sin ubicación → fix v1.12 cierra todo escape. **Smoke validation final**: SMOKE 1 (sin nombre/ubic) → 0 rows ✓ · SMOKE 2 (Federico solo nombre) → 0 rows ✓ · SMOKE 3 (Ana+Monterrey) → 1 row con todos los campos ✓ · SMOKE 4 (segundo turno mismo ID) → upsert sin duplicar ✓. **Outputs en repo**: `03_workflows/agente-tofo-web-b2b-rrss-v4.json` (47 nodos = 50 prod − 3 eliminados, snapshot reference) · `04_agents/agente-tofo-b2b-system-prompt.md` (v1.12 vivo + backups v1.9/v1.10/v1.11) · `04_agents/agente-tofo-rrss-system-prompt.md` (v1.8 vivo + backups v1.5/v1.6/v1.7) · `04_agents/agente-tofo-derivacion-system-prompt-restore.md` (Derivación 7KB extraído de snapshot 4/6) · `06_docs/guia-fix-airtable-gate-nombre-ubicacion-2026-06-21.md` (guía de deploy + 4 smokes + rollback) · `06_docs/gap-manychat-airtable-causas-2026-06-21.md` (registro de causas posibles del gap 1494 vs 1113, no bloqueante). **Variable `.env` agregada**: `TFO_N8N_WEBHOOK_URL=https://tofo.app.n8n.cloud/webhook/09689e14-54ae-4252-a131-422a7d4e0bb4`. **Pendientes derivados (NO bloqueantes)**: cleanup retroactivo de los ~580 records vacíos del renglón 488+ (punto #2 lista Mauricio — bulk delete con filtro `Estado IN ("1. Contacto RRSS", "2. Contacto WhatsApp") AND Ubicación Mencionada IS BLANK`); decisión upgrade Airtable plan / purga / migración (punto #3 — Mauricio decide).

**🚨 2026-06-21 PM — Calendar overlaps + tool rogue · ✅ RESUELTO 2026-08-04 (cirugía aplicada en n8n vivo + cleanup retroactivo del calendar de Mauricio hecho).** Mauricio mandó screenshot del grupo TOFO con el calendar mostrando **múltiples eventos overlapeados en los slots 10/11/12 hora CDMX** durante varios días seguidos — varias citas pisándose en mismo horario. Auditoría exhaustiva del workflow vivo `Agente WEB B2B y RRSS` reveló el **smoking gun**: el Agente de B2B tenía cableada como `ai_tool` una herramienta `Create an event in Google Calendar` (`n8n-nodes-base.googleCalendarTool` sin `toolDescription`), **paralela** a `check_disponibilidad`. El LLM podía elegir entre 2 vías de agendamiento: (a) la segura (`check_disponibilidad` → sub-workflow v3 → ventana 10/11/12 + chequeo de overlap + Zoom atómico) o (b) la directa (`Create an event` rogue → escribe directo al calendar sin chequeo, sin Zoom). Elegía la directa por ser más barata cognitivamente. **Los fixes previos (v1.6 prohibición cita sin tool + v1.8 checkpoint mental + v1.14 §0 reglas absolutas)** NO atraparon esto porque las reglas hablaban de "siempre invocá `check_disponibilidad`" pero NUNCA prohibían explícitamente otras tools de calendar/zoom alternativas — el LLM cumplía técnicamente al invocar la rogue. **Hipótesis adicional resuelta de paso:** el ticket Zoom del 19/6/26 ("meetings no aparecen en dashboard Mauricio") probablemente fue causado por el mismo bug — la tool rogue solo crea Calendar event, NO Zoom meeting. Coincide 100% con el síntoma. La credencial Zoom probablemente estaba OK todo el tiempo (verificación en §P6 de testing-guide v8 lo confirma/refuta). **Fix doble (belt-and-suspenders)**: (a) **prompt B2B v1.14 → v1.15** — agregada **REGLA ABSOLUTA #4** en §0: "La ÚNICA tool autorizada para crear citas es `check_disponibilidad`. PROHIBIDO invocar cualquier otra tool que toque Google Calendar o Zoom directamente, aunque aparezca en tu lista de tools disponibles." (b) **cirugía n8n vivo** (guía `06_docs/guia-fix-tools-rogue-calendar-2026-06-21.md`) — desconectar `ai_tool` de 3 nodos del Agente de B2B: `Create an event in Google Calendar` (CRÍTICO) + 2 zombies disabled (`registrarrrrrrr`, `Crear la base de datos`). Inventario post-fix queda en 6 tools (de 9). `Doc informacion al cliente` queda para validación follow-up separada. **Auditoría preventiva de otros subagentes (RRSS / Servicio / Reposición / Derivación)**: limpio, no hay rogues críticas — solo 6 tools sin `toolDescription` distribuidas (zombies de bajo riesgo, follow-up). **Outputs en repo**: `04_agents/agente-tofo-b2b-system-prompt.md` v1.15 (vivo en local + `-v1.15.md` backup) · `06_docs/guia-fix-tools-rogue-calendar-2026-06-21.md` (guía manual para la agencia/Mauricio paso a paso 9 pasos) · `06_docs/incidente-calendar-overlaps-2026-06-21.md` (postmortem 5-why + cronología + acciones correctivas + snapshot inventario pre/post-fix) · `07_testing/testing-guide-v8.md` (§P anti-tool-rogue, 6 casos nuevos + heredado completo v7) · `_core/standards/n8n-ai-agent-tool-inventory-audit.md` (estándar reusable la agencia — checklist + plantilla + anti-patterns para aplicar a cualquier agente conversacional). **Pendientes operativos**: (1) ejecutar la guía manual en n8n vivo (export del JSON pre-fix → desconectar 3 nodos → re-export como v5 al repo); (2) subir prompt v1.15 al Google Doc vivo; (3) Mauricio limpia overlaps retroactivos en su calendar a mano (Paso 8 de la guía); (4) correr §P de testing-guide v8 (6 casos, P3 es el crítico — slot ya ocupado NO debe crear overlap); (5) verificar §P6 calendar + dashboard Zoom para resolver ticket 19/6/26 por carambola o mantenerlo abierto; (6) follow-up segunda pasada cleanup elimina los 3 nodos huérfanos (opcional, post-72hs sin incidentes); (7) auditar 8 clientes activos restantes con el nuevo estándar (backlog).

**🆕 2026-06-30 — Snapshot del workflow vivo + drift detectado (investigación consumo OpenAI).** El repo había quedado desactualizado respecto al workflow vivo en n8n — `03_workflows/agente-tofo-web-b2b-rrss-v5.json` no reflejaba la estructura real. la agencia exportó el workflow vivo y lo guardó como `03_workflows/agente-tofo-web-b2b-rrss-prod-snapshot-2026-06-30.json` (mismo workflowId `rO0sAQvJU7LmUoYQ`, 47 nodos vs 45 de v5) — **este snapshot es la fuente de verdad del estado en vivo, confirmado, no v5**. **Drift detectado:** (a) **2 nodos nuevos en vivo no presentes en v5** — tool `listar_disponibilidad_dia` (coincide con el flujo PASO 2a/2b introducido en el prompt B2B v1.20, nunca se documentó el cableado real) + nodo `Execute a SQL query` (Postgres, sin doc); (b) **`systemMessage` del Agente de B2B embebido en vivo = 114.117 chars**, más grande que el de v5 (69.948) pero **más chico** que el `.md` vigente en repo (124.869 bytes, v1.21 con la regla de escalamiento fuera-de-ventana) — es decir, el workflow en n8n ya tiene la estructura nueva (tool + nodo SQL) pero todavía no se subió el texto de prompt v1.21 más reciente. **Relevante para la investigación de consumo abierta:** confirma que el B2B prompt siguió creciendo después del 22/6 (105K→114K+ en vivo, y subirá más aún cuando se deploye v1.21) y suma un candidato nuevo no contemplado en el análisis original — la tool `listar_disponibilidad_dia` agrega una invocación más por conversación de agendamiento. **Estado del plan de reducción de tokens:** usar `prod-snapshot-2026-06-30.json` (no v5) + prompt B2B v1.21 + `testing-guide-v11.md` (no v9) como base para la Fase 1 del diagnóstico.

**⚠️ P1 — Airtable captura datos del lead — incidente reunión Mauricio 18/6/26 [SUPERSEDED por el bloque ✅ de arriba]:** Mauricio reportó textualmente: *"Del renglón 488 para arriba, todos dicen 'contacto a redes sociales' porque no cogieron nada más de información, solo cogieron la información inicial."* Síntoma: leads recientes en Airtable quedan con campo "Estado" = "contacto a redes sociales" + sin nombre/ubicación/contacto capturado, pese a que la conversación tuvo intercambio real. **🆕 Criterio explícito de creación (Mauricio 18/6/26):** *"Yo creo que se tienen que registrar todos los que dejen nombre y lugar de donde están ubicados — esa ya es una señal de interés para mí."* → **El registro Airtable NO debe existir hasta que el agente capture nombre + ubicación.** Hoy se crea al inicio con info parcial (basura según criterio Mauricio). Hipótesis: (a) regression del flujo de captura en el main workflow después del bump v1.6/v1.7 — el agente conversó pero no escribió los campos secundarios a Airtable; (b) el write a Airtable se dispara al INICIO del webhook con subscriber_id + canal + "contacto a redes sociales" sin esperar la captura de nombre/ubicación; (c) no hay tool del agente que invoque el write **solo cuando** tenga los 2 campos canónicos. **Plan de fix (alineado con criterio Mauricio)**: (1) auditar los 50 nodos de `agente-tofo-web-b2b-rrss-prod-snapshot-2026-06-04.json` para localizar el nodo Airtable de write inicial; (2) **eliminar el write inicial automático** que genera registros "contacto a redes sociales" basura; (3) **agregar tool nueva `crear_lead_airtable`** invocable por el agente con upsert por `subscriber_id` (idempotente), que el agente DEBE invocar apenas tenga **nombre + ubicación** capturados (no antes, no parcial); (4) regla operativa nueva en prompt v1.9 (o v1.10): "DEBES invocar `crear_lead_airtable` apenas tengas nombre + ubicación. Si solo tenés uno de los dos, NO la invoques."; (5) **opcional radical**: bulk-delete de los ~580 registros "contacto a redes sociales" sin nombre/ubicación — confirmar con Mauricio antes de ejecutar. Casos §N de `testing-guide-v7.md` cubren esto en regression (N1 con nombre+ubicación → registro completo; N2 solo saludo → NO se crea registro).

**🚨 P0 — Citas Zoom no se crean (incidente reunión Mauricio 18/6/26) · ✅ RESUELTO 2026-08-04 — el agente crea la meeting y pasa el `join_url` real. Historial del diagnóstico:** Mauricio reportó textualmente: *"No está haciendo las citas en Zoom aún. Les dice al cliente que le hizo la cita en Zoom, pero no la hace."* **Estado actual (2026-06-21 PM, post-cirugía tools rogue):** smoke test ejecutado por la agencia sobre el agente vivo con `check_disponibilidad` confirmó: el evento Calendar se crea OK ✅ **pero el nodo `Crear meeting Zoom` del sub-workflow `Chequear disponibilidad | Tofo v3` devuelve output `[{}]`** (objeto vacío) — eso NO es un meeting Zoom creado, es el fallback silencioso de `continueOnFail: true` cuando el nodo falla. **Diagnóstico**: la hipótesis "tool rogue era la causa única del bug Zoom" queda **descartada** — la rogue era un factor (creaba eventos sin Zoom), pero **además existe un bug real en el nodo Zoom del sub-workflow**. Hipótesis principal sigue siendo credencial `zoomOAuth2Api` id `TllmBz0re6WGmTw2` ("Zoom account") mal configurada, token expirado, o cuenta sin permisos API. Hipótesis secundaria: plan Zoom de la cuenta no permite `meeting.create` vía API (free tier requiere upgrade). **Plan original del 19/6 sigue vigente y bloqueante para cerrar Zoom**: (1) Mauricio manda credenciales OAuth de su cuenta real Zoom por WhatsApp privado; (2) la agencia verifica account + crea credential nueva en n8n; (3) re-bindea nodo `Crear meeting Zoom` al credential nuevo; (4) test manual del nodo → debería devolver `{join_url, start_url, id, ...}` no `{}`; (5) si sigue fallando con credential nueva → confirmar plan Zoom de Mauricio soporta API; (6) si plan no soporta → pivot a sharable PMI link estático (calidad menor) o upgrade. **Mientras tanto en producción:** los leads están recibiendo confirmación de cita en Calendar pero sin link Zoom funcional — el prompt v1.15 REGLA ABSOLUTA #3 prohíbe inventar Zoom link, así que el agente debería usar el fallback "te paso el link aparte" (verificar comportamiento real). Doc fix: `06_docs/zoom-credencial-fix-2026-06-19.md`.

**📺 Pendiente decisión Mauricio — TikTok ManyChat (punto 5 del análisis WhatsApp 2026-06-17):** ManyChat sacó TikTok del plan Pro vigente. Para reconectar Mauricio necesita upgrade al plan Business (~$60 USD/mes adicionales). Mauricio dijo "funcionaba muy bien" (8/6/26 línea 638) pero no tenemos métricas de volumen previo. Doc: `06_docs/tiktok-manychat-decision-2026-06-17.md` con análisis costo/beneficio + 2 preguntas para Mauricio (volumen TikTok pre-corte en ManyChat + TikTok Analytics nativo) + recomendación por defecto (upgrade por 3 meses con tracking estricto si no llega data; revisar a los 3 meses: ≥3 leads cualificados → mantener, sino downgrade) + mensaje WhatsApp listo para enviar. **Pendiente**: la agencia manda el mensaje a Mauricio próximo lunes (22/6/26); decisión queda registrada en el doc cuando Mauricio responda.

**📦 Paquete agente de fallas — modelo reventa para clientes de Mauricio:** Mauricio en la llamada del 12/6 pidió paquetizar el agente de fallas técnicas para revenderlo a sus propios clientes (dueños de pizzerías con máquinas TOFO). **v2 generada 2026-06-22 — USD 360 al contado, 2 sem calendario, ~3h trabajo la agencia, posicionado como kit inicial honesto (no producto pulido)**. Stack reducido post-reunión Mauricio 18/6/26: WhatsApp Cloud API directa + Simple Memory nativa n8n + AI Agent gpt-4.1 — sin ManyChat, sin Supabase/Postgres, sin Telegram escalation (el agente instruye al cliente final por texto a contactar al técnico, no dispara notificación proactiva). Costo operativo cliente final baja de USD 60-100/mes (v1) a USD 15-30/mes. Palanca de venta de Mauricio: una sola venta a cliente final (típico USD 800-1.200 por implementación) recupera el paquete. 4 entregables: prompt fallas-only con placeholders + workflow n8n único importable + README corto (3-5 pp, sin screenshots) + Loom walkthrough async (10-15 min). Sin sesión Zoom sync, sin testing guide formal, sin diagrama draw.io, sin garantía formal de 30 días (solo 14 días de fix informal post-entrega). Pago único al contado previo a implementación (no 50/50 — el alcance es chico y el plazo es corto, el cobro adelantado elimina riesgo de cancelación intermedia). Docs v2: `01_discovery/paquete-agente-fallas-mauricio-v2-2026-06-21.md` (interno) + `01_discovery/propuesta-paquete-agente-fallas-mauricio-v2-2026-06-21.md` (versión cliente lista para mandar a Mauricio por WhatsApp). Add-ons archivados (no en propuesta para no diluir el SÍ a USD 360): `ops/04_upsells/TFO-addons-paquete-fallas-archivados-2026-06-21.md` — tool de escalamiento real Telegram USD 80 / WhatsApp template USD 120 (probable primer add-on que aparezca apenas el cliente final note que "instruir por texto al cliente que llame al técnico" no escala), implementación llave en mano USD 400 primer cliente final / USD 500 siguientes, mantenimiento mensual USD 120 (compromiso mínimo 3 meses), multi-idioma USD 400/idioma, capacitación profunda USD 250/sesión 90 min. Docs v1 superseded (preservados como referencia histórica del scope original): `01_discovery/paquete-agente-fallas-mauricio-2026-06-14.md` + `01_discovery/propuesta-paquete-agente-fallas-mauricio-2026-06-14.md` + `06_docs/guia-infra-cliente-final-paquete-fallas-2026-06-14.md`. **Pendiente**: mandar propuesta v2 a Mauricio por WhatsApp + cobrar USD 360 al contado al aceptar + mandar formulario de 3 decisiones de arranque (tono prompt MX/LatAm, cliente final puntual para Loom real vs dummy, canal/contacto para placeholder de escalamiento por texto) + bloquear ~1.5h S1 + ~1.5h S2 en calendario.

**🆕 B2B v1.20 → v1.21 — Escalamiento fuera-de-ventana en vez de rechazo (instrucción Mauricio, dictada 1/7/26):** cuando el lead pide un horario fuera de la ventana estándar (10:00-12:30 CDMX, 6 slots — sin cambios, no se extendió) en día Lunes a Viernes, el agente ya no rebota pidiéndole otro horario — **escala la conversación al director** vía `elevar_conversacion(tipo='b2b')` + un mensaje avisando que lo pone en contacto directo con Mauricio para que él decida si puede hacer una excepción. Motivación: un lead con un único horario disponible fuera de agenda puede ser premium (proyecto grande/urgente), y un rechazo automático puede perderlo — la pausa deliberada le da a Mauricio la chance de filtrar y responder personalmente. Fin de semana y fecha pasada NO cambian (Mauricio no las revisó esta vez): siguen con rechazo canónico simple, sin escalar. **Cambios**: nueva REGLA ABSOLUTA #5 (ahora 5 reglas duras, antes 4) + nueva sección "📞 ESCALAMIENTO FUERA-DE-VENTANA" en "Cómo agendar reunión" + tabla "Filtrado pre-tool" y motivo `fuera_ventana` de PASO 5 actualizados + REGLA ABSOLUTA #4 documenta los 3 usos válidos de `elevar_conversacion` (post-cita, error técnico, escalamiento — este último es el único caso donde se activa sin haber invocado `check_disponibilidad` antes). Sin cambios en la ventana en sí, en el flujo `listar_disponibilidad_dia` (PASO 2a/2b, v1.20), en REGLAS #1-#3, en el gate de precio §9, ni en los otros 3 subagentes. Backup v1.20 preservado en `agente-tofo-b2b-system-prompt-v1.20.md`. Testing guide nueva `07_testing/testing-guide-v11.md` (hereda v10, reescribe S8/S12 que testeaban el comportamiento viejo, agrega §U con 8 casos del escalamiento). **Estado:** en repo, ✅ DEPLOYADO al n8n vivo el 2026-08-04, junto con v1.17/v1.19/v1.20 (copy-paste manual al Google Doc del prompt). **Pendiente:** correr §U de testing-guide-v11 (automatizado por texto + verificación manual en n8n de que `elevar_conversacion` se invoca/no se invoca según corresponda), confirmar que el sub-workflow de `elevar_conversacion` acepta ser llamada sin contexto de cita agendada.

---

### DLK — Dialectika (`clients/DLK_Dialectika/`)

Plataforma web B2C y B2B para Dialectika (psicología), con automatizaciones en n8n y Supabase como base de datos. Cliente en Chile.

**Contactos:** Pablo (dueño) · Carlos (mano derecha) · Esteban (desarrollador web)

**Stack:** n8n + Supabase

**Archivos clave:**
- (completar a medida que se crean)

---

### INT — Interno (`clients/INT_Interno/`)

Registro interno de la agencia. No es un cliente real — existe para asociar gastos y proyectos propios de la agencia en la webapp.

**Stack:** —

**Archivos clave:**
- (sin archivos de trabajo — uso exclusivo en webapp)

---

### HBV — Heber Vera (`clients/HBV_HeberVera/`)

Agente conversacional para Heber Vera Intercoiffure (peluquería de referencia en Montevideo, 50 años de trayectoria). Atiende consultas en WhatsApp, guía reservas via Fresha, cubre flujo especial de prótesis oncológicas. Reportes semanales de métricas vía Telegram. Dueña: Eloísa Vera.

**Stack:** n8n + OpenAI GPT-4o + Google Sheets + Telegram + Fresha

**Archivos clave:**
- `03_workflows/heber-vera-agente-principal-v1.json` — Agente principal (consultas, precios, reservas, prótesis oncológicas, división de respuestas en 3 partes)
- `03_workflows/heber-vera-metricas-semanales-v1.json` — Reporte semanal automático (Google Sheets → GPT-4o → Telegram)
- `01_discovery/paquete-marca-personal-elo-2026-06-13.md` — **Paquete interno** (la agencia) para nueva línea de servicio "Marca Personal Eloísa": 8 semanas, USD 1.000, 10 entregables (5 docs estratégicos del curso + plan contenido 60d + KPIs + manual operativo Micaela), cronograma kickoff + 3 quincenales + cierre, riesgos y mitigaciones, cálculo de costo interno. Consultoría estratégica ortogonal al agente WPP.
- `01_discovery/propuesta-marca-personal-elo-2026-06-13.md` — **Propuesta externa** para Eloísa. Formato Markdown listo para Notion. Tono rioplatense, una sola opción USD 1.000 50/50. ❌ **No se envía — descartado el 2026-08-04.** Queda archivada.
- `06_docs/incidente-reconnect-messenger-2026-06-22.md` — ❌ **Incidente cerrado sin resolución el 2026-08-04** (no se sigue escalando a Chatrace; n8n y WhatsApp nunca se vieron afectados). Registro histórico: dashboard Chatrace muestra "You don't manage any chatbot" + mail "Reconnect Messenger" del bot 1444981. n8n sigue ejecutando (WA probablemente no afectado). Soporte primera línea **escaló a agente humano** y advirtió que "Create New Account" crea bot nuevo (pérdida permanente de subscribers/flows `1742402002782`+`1762181904878`/custom fields/persistent menu/API token). Bloqueante: respuesta del agente humano de Chatrace. Plan B = OAuth coordinado con Eloísa solo si soporte no puede restaurar el binding del usuario al bot existente.

---

### STK — Stark Supplements (`clients/STK_StarkSupplements/`)

Agente conversacional de ventas ("Kathe") para Stark Supplements (suplementos deportivos, Bolivia). Responde consultas en WhatsApp/IG/FB vía Kommo, recomienda productos con imágenes (unitarios y packs), maneja cotización, detecta comprobantes de pago, y eleva a humanos. Seguimiento automático en 4 toques (30m, 2h, 8h, 24h). Dueño: Cristian.

**Contactos:** Cristian (dueño)

**Stack:** n8n + Kommo + Airtable + OpenAI (GPT-4o + GPT-4.1-mini + Whisper) + PostgreSQL + Redis + Telegram

**Archivos clave:**
- `03_workflows/stark-agente-principal-v1.json` — Workflow principal (webhook Kommo, anti-spam Redis, agente Kathe GPT-4o, envío vía salesbot)
- `03_workflows/stark-seguimientos-v1.json` — Seguimientos automáticos (4 toques: 30m/2h/8h/24h, generados con GPT-4.1-mini, detención si responde)
- `03_workflows/stark-elevar-conversacion-v1.json` — Sub-workflow de elevación a humano (4 buckets: pago, humano/tienda, salud, reclamo)
- `03_workflows/stark-tool-verificar-producto-v1.json` — Tool de verificación de producto (clasificador pack/unitario, match en Airtable, intro técnica + foto vía salesbot)
- `06_docs/contexto-handoff-juampi-2026-05-10.md` — Contexto completo del traspaso (arquitectura, integraciones, credenciales, notas)
- `06_docs/pendientes-produccion.md` — Lista de pendientes para poner en producción

**Pendientes: ❌ ninguno — todos descartados el 2026-08-04.** El proyecto queda **congelado en pre-producción**: no se reconstruyen los bots en Kommo (el cliente los borró 6 veces), no se cablea el routing del workflow Elevar Conversación, no se busca el sub-workflow "Enviar Información" faltante y no se persigue el cobro de los USD 1.500 + mantenimiento. Lo que hay en `03_workflows/` queda como está.

> Contexto para retomar: `06_docs/pendientes-produccion.md` y `06_docs/contexto-handoff-juampi-2026-05-10.md` conservan el detalle de lo que faltaba. **Son referencia histórica, no una lista de tareas viva.**

---

### CRZ — Cereza Invest (`clients/CRZ_CerezaInvest/`)

Agente de ventas conversacional ("Alexis") para Cereza Invest (Argentina, rubro inversiones / educación financiera). Responde leads por WhatsApp e Instagram vía ManyChat; transcribe audios con Whisper; activa flows de ManyChat para precios/fricción y escalamiento. Memoria por sesión en PostgreSQL.

**Dueño:** Maxi Robles

**Stack:** ManyChat + n8n + OpenAI gpt-4.1 + Whisper + PostgreSQL (memoria)

**Archivos clave:**
- `03_workflows/cereza-invest-agente-principal-v1.json` — Workflow principal (agente Alexis + transcripción audios + routing IG/WPP + tools notificar/escalar)
- `04_agents/agente-cereza-invest-system-prompt.md` — System prompt v1 (referencia; el prompt en vivo se obtiene desde Google Docs en n8n)

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

### Meeting Summary (`salidas/meeting-summary/`)

CLI en Python que fetchea el transcript de la última reunión grabada en Fathom (vía webhook n8n), lo manda a Claude y genera un resumen adaptado al tipo de reunión detectado (técnica interna, kick-off, alineación con cliente, u otra).

**Para usar:**
```bash
cd salidas/meeting-summary
pip install -r requirements.txt
ANTHROPIC_API_KEY=sk-... python meeting_summary.py [--save]
```

**Flags:**
- `--webhook-url URL` — override de la URL del webhook (default: `https://[TU-INSTANCIA-N8N]/webhook/my-meeting-transcripts`)
- `--save` — guarda el resumen como `resumen_YYYY-MM-DD_HH-MM.md` en el directorio actual

**Env vars:** `ANTHROPIC_API_KEY` (requerida), `N8N_WEBHOOK_URL` (opcional, override de URL)

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

### Test Runner de Agentes (`scripts/testing/run-agent-tests.py`)

Ejecuta automáticamente los casos de una guía de testing contra la OpenAI API y evalúa resultados con LLM-as-judge. Genera dos outputs:
- `*-auto-results.md` — casos automatizables con resultados y veredictos
- `*-manual.md` — casos que requieren tool calls de n8n (verificación humana)

Invocado por `/iterar-prompt` en los pasos A.8b y B.7b (loop iterativo hasta que todo pase).

```bash
source .env && python3 scripts/testing/run-agent-tests.py \
  --system-prompt clients/[XXX]/04_agents/agente-[nombre]-system-prompt.md \
  --testing-guide clients/[XXX]/07_testing/testing-guide-v[N].md \
  --model gpt-4.1-mini
```

**Requiere:** `OPENAI_API_KEY` en `.env` (ya gitignored). Solo compatible con modelos OpenAI.
**Detección manual-only:** casos cuyo "Resultado esperado" contiene `[NOMBRE_HERRAMIENTA]` (mayúsculas + guiones bajos).

---

### Tablero de estado por cliente (`scripts/generators/estado-cliente.py`)

Genera `clients/[XXX]/06_docs/estado/estado-proyecto.html`, un tablero autocontenido con modo claro y oscuro. Muestra las fases del contrato, los bloqueos agrupados por responsable (nosotros · cliente · decisiones de la agencia), el camino al 100% y lo que queda fuera del contrato. Se activa en cualquier cliente que tenga `06_docs/estado/estado.json`. Hoy no lo usa ningún cliente.

- **Fuente de verdad:** `estado.json`. Las fases, los bloqueos, el camino y los cobros los actualiza Claude (Paso 4.C de `/cliente-sync`).
- **Lo que lee solo:**
  - los pendientes del cliente, desde los placeholders `> *…:*` sin responder del documento de puntos de cierre;
  - los pacientes cargados en Airtable (caché de 6 h en `.cache.json`, gitignored);
  - las semanas que lleva el pendiente de un lado.
- **Automático:**
  - hook `PostToolUse` (Write|Edit) en `.claude/settings.json`, que regenera el tablero del cliente cuyo archivo se tocó;
  - hook `Stop`, que corre `--all`.
  - Solo reescribe el HTML si el contenido cambió.

```bash
python3 scripts/generators/estado-cliente.py --cliente XXX_Cliente   # o --all
```

### Actualizador de Nodos Sonrisas (`scripts/utilities/update-sonrisas-nodes.py`)

Genera código JS para los nodos **Filtro**, **Categoria** y **Clase** de los flujos Sonrisas (Reporte Facturación + Correos) a partir del Listado de Precios completo (xlsx). **Clasificación 100% por código.**

```bash
python3 scripts/utilities/update-sonrisas-nodes.py ~/Downloads/"Listado de Precios Completo.xlsx"
```

**Validación previa obligatoria (aborta sin generar nada):** (1) **códigos únicos** — si un código aparece en >1 fila (Rubros en conflicto o fila redundante) corta y pide a Cecilia corregir el archivo (la clasificación por código sólo es robusta si cada código mapea a un único Rubro); (2) **Rubro conocido** — si algún Rubro no está en `RUBRO_A_CATEGORIA` aborta (evita categoría `OTRO` silenciosa). Exit code 1 en cualquier caso.

Genera 3 bloques JS:
- **Filtro**: 326 códigos válidos (todos con `Computa para Planilla Importe == SI`), `throw Error` en código desconocido, flags `computaImporte`/`computaCantidad`
- **Categoria**: lookup table código→categoría derivado de Rubro del xlsx (10 categorías), **puro por código** (sin fallback al `Nombre categoría` — habilitado por la validación de unicidad)
- **Clase**: AJUSTE (99 cód. Rubro `ORTODONCIA AJUSTES`), COMBO (36, `ORTODONCIA INSTALACION`), RETIRO (15, `ORTODONCIA RETIRO`). **Solo ortodoncia**: descarta las filas no-ortodoncia (NO produce OTRO; lo no-ortho se ve en el bloque Categoria). Cambio 2026-05-25 — antes asignaba `OTRO`, que acumulaba $9.18M de odontología general (42% de la facturación)

**Nota (2026-05-26):** el listado actual tiene 11 códigos duplicados (9 conflicto PERIODONCIA↔PROTESIS: `P0000,P1000-P1004,P2000-P2002`; 2 redundantes: `C0014,RD003`) y le faltan 2 códigos facturados (`C0015`, `302`). El skill aborta hasta que Cecilia entregue un listado con códigos únicos y completo.

**Requiere:** `pandas` y `openpyxl` (`pip install pandas openpyxl`)

---

### Verificador de Fechas Sonrisas (`scripts/utilities/verify-sonrisas-fechas.py`)

Simula la regla "Mes objetivo" + rango de carga (reemplazo semanal los sábados) sobre más de un año y prueba que ningún día hábil (Lun-Sáb) quede sin procesar en los bordes de mes, que no haya colisión `Semana_mes`, y que cada mes se cierre exactamente una vez. Cuantifica además los días que perdía la lógica vieja (22 día-mes/año en 2026).

```bash
python3 scripts/utilities/verify-sonrisas-fechas.py
```

Sin dependencias externas (solo stdlib). Ver guía: `clients/SNR_Sonrisas/06_docs/guia-fechas-facturacion-2026-05-24.md`.

---

### Reconciliación Mensual vs Semanal Sonrisas (`scripts/utilities/verify-sonrisas-reconciliacion.py`)

Replica la lógica del Reporte Facturación (clasificación de Clase + fórmula de Semana del año) sobre un CSV exportado de `Ingreso datos`, y reconcilia Σ por Mes vs Σ por Semana para una celda Sucursal × Clase. Lista las filas con fecha no parseable (que hoy se descartan del semanal) y, con `--semanas-en-sheet`, simula el `update` para cuantificar exactamente el monto que se pierde por falta de fila.

```bash
python3 scripts/utilities/verify-sonrisas-reconciliacion.py --csv <ingreso-datos.csv> --sucursal "Paso Molino" --clase AJUSTE
```

Sin dependencias externas (solo stdlib).

---

### Migración Reconciliación Reporte Sonrisas (`scripts/utilities/fix-sonrisas-reconciliacion-workflow.py`)

Aplica de forma reproducible el endurecimiento al workflow: lee `sonrisas-reporte-facturacion-v3.3.json` y genera `v3.4.json` (agrega nodo `Parsear y validar fecha`, repunta Semana/Semana_mes a la fecha validada, hace que `Filtro1` aborte ante fecha inválida, y cambia los 4 writers a `appendOrUpdate`). No modifica el v3.3 original; valida el JSON resultante.

```bash
python3 scripts/utilities/fix-sonrisas-reconciliacion-workflow.py
```

---

### Migración Histórico Reporte Sonrisas (`scripts/utilities/fix-sonrisas-historico-workflow.py`)

Aplica el **fix permanente**: lee `v3.4.json` y genera `v3.5.json` agregando la cadena `Keyear Histórico → Upsert Histórico (appendOrUpdate por _key) → Get Histórico → Filtrar Histórico 2M`, de modo que el reporte acumule en `Histórico` de-duplicado y procese solo el mes corriente + mes anterior para no saturar RAM en instancias de 2 GB. Clave `_key = # Pago + - + # Detalle Presupuesto`. Requiere crear la pestaña `Histórico` en n8n (ver doc de cambios).

```bash
python3 scripts/utilities/fix-sonrisas-historico-workflow.py
```

---

### Wireado Correos al Histórico (`scripts/utilities/fix-sonrisas-correos-historico.py`)

Cambio mínimo en el workflow de correos: lee `sonrisas-correos-reportes-facturacion-v3.json` y genera `v4.json` repuntando las dos lecturas (`Get row(s) in sheet`, `Get row(s) in sheet1`) del tab `Facturación` al tab `Histórico`. No toca nada más (verificado: 43 nodos, conexiones idénticas).

```bash
python3 scripts/utilities/fix-sonrisas-correos-historico.py
```

---

# Dry-run primero (imprime payloads sin enviar):
python3 scripts/utilities/migrate-pap-icp-to-airtable.py --dry-run

# Migración completa (~155 → ~750 registros):
python3 scripts/utilities/migrate-pap-icp-to-airtable.py

# Solo una entidad:
python3 scripts/utilities/migrate-pap-icp-to-airtable.py --only pacientes
```

Lee credenciales de `clients/XXX_Cliente/06_docs/airtable-credentials.md` (gitignored). Orden interno: Garantes → Pacientes → Asignaciones (respeta dependencias de linked records). Requiere `openpyxl` (`pip install openpyxl`).

---

## Templates y Recursos Compartidos (`_core/`)

| Ubicación | Contenido |
|-----------|-----------|
| `_core/standards/naming_conventions.md` | Convenciones de ID para workflows, agentes, prompts, módulos |
| `_core/standards/manychat-integration-pattern.md` | **Estándar interno 2026** ManyChat ↔ n8n: naming custom fields (`ai_*`/`lead_*`/`session_*`), auth via Credential, payload dinámico, 3 flows canónicos. **Aplicar a todo build nuevo.** |
| `_core/standards/n8n-data-references.md` | **Estándar interno n8n** — cuándo usar `$json` vs `$('NodeName').item.json` para referencias entre nodos. Evita bug recurrente en nodos Postgres/HTTP donde `$json` trae el output del nodo previo (no el contexto de negocio). Incluye además los **built-ins del Code node**: `$getWorkflowStaticData` (correcto) vs `this.getWorkflowStaticData` (TypeError en runtime, no lo detecta ni el JSON válido ni `node --check`) + comando `jq` para detectarlo antes de entregar. **Lectura obligatoria al construir o revisar workflows n8n.** |
| `_core/standards/n8n-entrega-nodos.md` | **Estándar interno n8n — formato de entrega.** Nodo suelto para pegar → SIEMPRE envuelto en `{ "nodes": [...], "connections": {} }` (formato clipboard, nunca el nodo pelado). **Incluye el `jsCode` de un Code node: va el nodo completo, no el JS suelto** — y aclarar siempre que pegar crea un nodo nuevo, no reemplaza al existente. Workflow nuevo → JSON importable. EDIT en producción → guía paso a paso. **Lectura obligatoria antes de devolver nodos/workflows.** |
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
| `_core/tools/markitdown/` | Clon de [microsoft/markitdown](https://github.com/microsoft/markitdown) (MIT). Binario instalado vía pipx como `markitdown`. Convierte PDF/DOCX/PPTX/HTML/EPUB/imágenes/audio a Markdown. **NO usar para XLSX ni CSV** (ver regla operativa en "Conversión automática de archivos pesados"). |

---

## Instrucción Crítica: Mantener Este Archivo

Actualizar CLAUDE.md cada vez que:
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
