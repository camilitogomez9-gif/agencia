# SYS — Sistemas y Soluciones

## Datos generales
- ID: SYS
- Nombre: Sistemas y Soluciones
- Niche: generic (industria gráfica)
- Fecha inicio: 2026-04-11
- Status: **LIVE · desarrollo transferido a Camilo (2026-08-04).** La migración de infraestructura a cuentas del cliente quedó **hecha**; el deploy de main v0.9, el de `guardar_email` v2 / `registrar_datos_lead`, la auditoría de workflowId/credenciales reales en n8n y la limpieza de los 5 dropdowns de Airtable **pasan a la línea de Camilo** — no son cola de la agencia. Sigue abierto del lado de la agencia solo el **upsell comercial** (CRM completo + Meta Ads quick replies). Estado técnico previo: **(Etapa 2 deployada · 2026-06-23)** — main v0.9 vivo en n8n, 10 tools cableadas, **prompt v2.7 vivo** (deploy 2026-07-10), memoria Postgres en Supabase, ManyChat integrado, agente atendiendo leads reales en WhatsApp/IG/FB.
- **2026-07-01/10 — Auditoría Airtable (65 findings, mayoría P0 resueltos) + registro de leads gated por teléfono + fix "papel fotográfico":** ver detalle completo en la entrada de SYS en `CLAUDE.md` raíz (demasiado extenso para duplicar acá). Resumen: (1) auditoría multi-agente de la base Airtable disparada por bug reportado por Edgardo, 7 P0 encontrados y en su mayoría resueltos (Sustratos limpio, Equipos↔Aplicaciones regenerado, 3 tools con field names rotos corregidas); pendiente limpieza de 5 dropdowns bloqueada por permiso de API. (2) Reunión Jimena+Edgardo 2026-07-08 disparó fix de registro de leads: teléfono ahora es gate obligatorio (prompt v2.6→v2.7 + sub-workflow `registrar_datos_lead` v2→v3), con un fix adicional post-test en producción (v2.7) porque ManyChat manda `{{phone}}` de forma intermitente e irresoluble para algunos contactos. **Red estructural en `notificar_lead` ✅ aplicada y verificada en producción** (2026-07-09/10, ya no pendiente). **Bug adicional encontrado y resuelto en producción**: type mismatch en el nodo `IF lead existe?` (Google Sheets devuelve `subscriber_id` como number, el operator esperaba string con validación estricta) — fix en `registrar_datos_lead` v3. (3) Fix "papel fotográfico" (Airtable + dato fijo en prompt) foldeado en v2.7. (4) Guía operativa para Edgardo reescrita en formato ultra-simple (`06_docs/airtable-guia-edgardo-2026-07-02.md`). (5) **`notificar_lead` re-exportado como v5 post-fix — reveló que los workflowId/credenciales documentados para las tools de SYS NO coinciden con los reales en n8n** (probable migración de infra a cuentas del cliente no registrada). Ver nota completa en `CLAUDE.md` raíz — recomendado auditar IDs reales antes de cualquier futuro "import in-place".
- **2026-06-25 — Diagnóstico adaptativo por formato (feedback Jipi, ✅ deployado y validado):** Jipi reportó que el agente preguntaba "cuántas unidades estimás producir diariamente" a leads consultando por plotters rollo a rollo — pregunta sin sentido para esa línea (se cotiza por metro, no por unidad). Fix: prompt v2.3 → v2.4 con ETAPA 3 reescrita en 3 ramas (A — plotters: pregunta **ancho + cabezales**, NO unidades; B — láser papel cortado Konica/RISO: mantiene copias mensuales + color; C — DTF/sublimación textil: mantiene volumen de prendas). Nuevo bloque "Rangos técnicos canónicos para diagnóstico (plotters)" con anchos 1.60-6.60 m + cabezales 2-32 + dimensiones típicas camas planas. Regla operativa 20 reescrita para reflejar la ramificación. **NO** se tocó Airtable (fields `Ancho`, `Cabezales hasta/incluidos/tipo`, `Formato` ya existen) ni los workflows JSON (`consultar_catalogo` filtra correctamente con query libre). Smoke tests E2E contra el webhook productivo 4/4 PASS: S1 plotter UV → pregunta ancho directo; S2 (mismo lead da 1.80) → pasa a cabezales sin re-preguntar unidades (replica anti-regression del bug del screenshot Jipi); S3 alquiler láser 5000 copias A4 → Rama B sin regression; S4 DTF 200 remeras/día → Rama C sin regression. `sys_session_state` consolidó S1+S2 en 1 row (memoria persistente). `sys_tool_calls` vacío (correcto — los turnos de diagnóstico inicial no requieren tools). Plan: `/Users/camilo/.claude/plans/tenemos-que-corregir-una-magical-moore.md`. Backup v2.3 preservado en repo.
- **2026-06-24 P1 — Fix `consultar_catalogo` HF6090 (en repo, pendiente deploy):** Jipi reportó que el agente no reconoce la Cama Plana Huenú HF6090 promocionada en una campaña Meta activa. Causa raíz: el `Classify Intent` JS del sub-workflow `consultar_catalogo` (workflowId `oQtLMujJBHlxZTTJ`) no normalizaba acentos (`"Huenú".toLowerCase()` → `"huenú"` no matcheaba el array `['huenu', …]`), no extraía `formato` ni `modelo_hint`, y caía en un fallback que buscaba el string completo en `{Modelo}`/`{Marca}` cortos. Aun extrayendo modelo `"HF6090"`, el campo Airtable es `"HF 6090"` con espacio → SEARCH directo nunca matcheaba. Fix nuevo: **`03_workflows/sys-tool-consultar-catalogo-v4.json`** (preserva workflowId `oQtLMujJBHlxZTTJ` → import in-place sobrescribe el workflow vivo). 5 cambios: (a) `Classify Intent` reescrito — normaliza acentos con `String.prototype.normalize('NFD')`, agrega `FORMAT_MAP` (Cama Plana / Rollo a Rollo / Híbrido / Plotter / Mesa / Cilíndrica / etc.), agrega regex `modelo_hint` (HF6090 / HR 1602 / DLI-1688 / X4E-7703 / C450i), tokeniza con stopwords AR (hola, quiero, información, sobre, …), y arma 3 fórmulas `filterByFormula_equipos/aplicaciones/inventario` listas para downstream. (b) Builder de fórmulas en cascada de prioridad: modelo_hint > marca+tec > marca+formato > formato+tec > solo marca/formato/tec > fallback tokens. La fórmula clave para HF 6090 es `AND(FIND("HF6090", UPPER(SUBSTITUTE(SUBSTITUTE(SUBSTITUTE({Modelo}," ",""),"-",""),"/","")))>0, {Marca}="HUENU")` — quita espacios/guiones del campo Modelo antes de comparar. (c) 3 expressions `filterByFormula` de los nodos Airtable reemplazadas por `={{ '=' + $('Classify Intent').first().json.filterByFormula_X }}`. (d) Nodo `Airtable: Inventario Konica` ya NO devuelve `TRUE()` por default (evita traer 21 records refurbished irrelevantes al LLM). (e) `Format Output` enriquecido: agrega `formato`, `linea_producto`, `velocidad`, `cabezales_incluidos`, `cabezales_tipo`, `datos_extra`, `tipo_uso` al output items[]. Precio EXCLUIDO (política cliente: el agente NUNCA da precios). Mensaje NOT_FOUND ahora lista los hints extraídos para debug operativo. **Tests pin-data simulados con Node localmente (16 casos)**: todos pasan. Test 1 (el bug crítico) extrae correctamente `intent=equipo, marca=HUENU, formato="Cama Plana", modelo_hint=HF6090` y genera la fórmula esperada. Riesgos documentados (no bloqueantes, follow-up): falso positivo `modelo_hint=I3200` para queries sobre cabezales (mitigación: blacklist tokens cabezales); modelos `X4E-7703` con patrón letra-dígito-letra no captura el regex actual (1 solo modelo así en base). Pendiente operativo en system prompt v2.3: documentar `consultar_catalogo` (gap conocido — la tool no aparece en la sección HERRAMIENTAS). Guía completa de deploy + tests + smoke + rollback: `06_docs/guia-fix-consultar-catalogo-hf6090-2026-06-24.md`. Plan aprobado: `/Users/camilo/.claude/plans/users-la agencia-downloads-equipos-grid-view-transient-llama.md`. **Deploy pendiente**: importar v4 en n8n (overwrite del vivo, mantiene workflowId) → ejecutar tests 1, 4, 5, 8, 9, 12 con pin-data → smoke E2E con mensaje literal del lead Meta → activar + monitorear ratio NOT_FOUND/RESOLVED 24-48hs en `sys_tool_calls`.
- **2026-06-23 — Mejoras Edgardo (mail):** (1) **#1 Recontacto a 4 días** ✅ deployado — `sys-seguimientos-leads-v2.json` + vista Supabase v3 (`supabase-schema-v3-seguimientos.sql`); cron Lun-Vie 11h ART, sin LLM, texto fijo con `[Nombre]` reemplazado o fallback genérico; 39 leads procesados en primera corrida + 1 smoke la agencia OK. (2) **#2 Mails a `emarti@`+`marketing@`** ✅ deployado — `sys-tool-notificar-lead-v4` + `sys-tool-guardar-email-v5`; 2 bugs en cadena diagnosticados y resueltos: (a) credencial Gmail OAuth 403 reconectada; (b) en notificar-lead las refs `$json.X` en el nodo Gmail resolvían a `undefined` porque está downstream de un HTTP ManyChat → fix con `$('Validate Input').first().json.X` (13 refs). Este bug explica el verbatim "antes llegaba vacío". CC `info@` removido. (3) **#3 Consulta precios interna desde Google Sheets** ❌ RECHAZADA por Edgardo — diseño completo guardado: sub-workflow standalone `03_workflows/sys-tool-consulta-precios-interna-archivado-v1.json` + README + propuesta económica `01_discovery/propuesta-consulta-precios-interna-2026-06-23.md` (USD 240/2hs) + guía deploy `06_docs/guia-deploy-consulta-precios-interna-2026-06-23.md`. Posible re-incorporación dentro de un proyecto más grande. Plan original: `/Users/camilo/.claude/plans/bien-lo-que-vamos-snazzy-nygaard.md`.
- **Refactor nuclear 2026-06-03 — Bug Zod LangChain:** los 3 tools `consultar_aplicacion`, `buscar_equipo`, `consultar_inventario_usados` fallaban con `Received tool input did not match expected schema` en n8n LangChain v1.122.4 → bypass por arquitectura: reemplazados por **1 tool consolidada `consultar_catalogo`** (`03_workflows/sys-tool-consultar-catalogo-v1.json`) con superficie mínima de schema (`query: string` + `session_id`). Sub-workflow internamente: Code "Classify Intent" (regex) → Switch 3-way → 3 nodos Airtable con `filterByFormula` OR multi-keyword → Format → Log → Return. Postmortem completo: `06_docs/incidente-bug-zod-langchain-2026-06-03.md`. **Pendiente:** re-exportar `sys-agente-principal` post-nuclear de n8n como v0.5 (el v0.4 del repo NO refleja estado vivo).
- **Captura de emails (2026-06-02):** nueva Tool 10 `guardar_email` + sub-workflow `sys-tool-guardar-email-v1.json` + Google Sheet "SYS - Leads (Captura Emails)" tab `Emails` (Sheet ID `15OrQ-uI_x5rAorjkMpz_V_TvFxVf31nsDfTjm9oUqsc`, 6 columnas: `timestamp`, `email`, `nombre`, `telefono`, `subscriber_id`, `session_id` — contrato minimalista alineado al alcance original). Credencial Google Sheets en n8n: `la agencia` (cred ID `2a5f0S7mTtvH5XH2`, reutilizada). System prompt v2.1 → v2.2 con regla operativa 7 + ETAPAS 5 y 6 actualizadas. Workflow importado y activo en n8n (`v9HD7P2uroG4Ni3A`). Segmentación rica (origen del lead / canal / aplicación de interés) queda fuera de alcance — irá en el upsell CRM.
- **Cierre Etapa 2 (2026-06-05):** (a) **Gap B descuento** → DESCARTADO por Edgardo (2026-06-09): el cliente decidió no incorporar el tema del descuento; el prompt queda en v2.1 sin mención de descuento. (b) **Gap C canal web** → OBSOLETO, se considera cubierto vía WhatsApp. (c) **Gap A migración de infra a cuentas del cliente** → guía creada: `06_docs/guia-migracion-infra-cliente-2026-06-05.md`. Deploy del main v0.6 + seguimientos ya hecho.

## Stack activo

### Etapa 1 (testing — completado)
- [x] n8n
- [x] Google Sheets / Planillas Drive (6 sheets de catálogo, placeholders)
- [x] Telegram (canal de testing)

### Etapa 2 (producción — en build)
- [x] n8n (workflows nuevos a construir)
- [x] OpenAI (gpt-4o agente principal + gpt-4.1-mini tools internas)
- [ ] ManyChat (Pro plan, IG/WA/FB unificados) — F6
- [x] Supabase Postgres (free tier, sa-east-1) — memoria persistente — **F2 ✅ 2026-05-29** (4 tablas + 3 vistas creadas; credencial n8n `Supabase SYS` via Session Pooler; SSL `require` + Ignore SSL Issues `true`. Detalles: `06_docs/supabase-credentials.md` gitignored)
- [x] Airtable (base `SyS Catalogo`, **12 tablas**, ~230 records reales) — RAG + catálogo + inventario refurbished — **F1 ✅** (base creada, importada, credencial n8n configurada `3zohdTBWzW8UUN6P`)
- [ ] Gmail SMTP (notificación al representante) — config en F4
- [x] Telegram bot (alertas al el equipo, compartido)

## Canales de atención (productivos en Etapa 2)
- WhatsApp Business (vía ManyChat)
- Instagram DM @sistemasysoluciones (vía ManyChat)
- Facebook Messenger (vía ManyChat)

## Contactos clave
| Rol | Nombre | Contacto |
|-----|--------|---------|
| Decisor / Responsable catálogo | Edgardo | (pendiente confirmar) |
| Gerente / Receptor copia notificaciones | (pendiente) | (pendiente) |
| Técnico | — | — |

## OKRs del proyecto
1. Agente atiende y califica leads entrantes en WhatsApp/IG/FB sin intervención humana
2. ~~Leads derivados quedan registrados automáticamente en Airtable con todos los datos~~ → **EXCLUIDO del alcance Etapa 2.** Cliente no quiere CRM por ahora. Tabla Leads queda creada pero sin uso productivo. Ver upsell pendiente: `ops/04_upsells/SYS-upsell-crm-leads-2026-05-28.md`
3. Representante comercial recibe notificación por mail en menos de 1 minuto del trigger (mail a `info@sistemasysoluciones.com`)
4. (Etapa 2) Catálogo y FAQs mantenibles por el cliente sin tocar código (todo en Airtable)
5. (Etapa 2) Memoria persistente: agente recuerda al cliente entre sesiones del mismo canal

## ⚠️ Alcance reducido confirmado 2026-05-28 — CRM PAUSADO

El cliente decidió NO avanzar con la implementación CRM durante F1. Cambios:

- **Tabla Airtable `Leads`**: creada pero **vacía y sin uso productivo**. Tool `notificar_lead` NO escribe ahí.
- **Vistas Leads en Airtable**: NO creadas (`Nuevos hoy`, `Pendientes derivación >24h`, `Derivados`, etc.).
- **Tool `notificar_lead`**: queda en versión simplificada — solo envía mail a `info@sistemasysoluciones.com` + Telegram al el equipo. NO hace Airtable Create/Update.
- **Seguimiento automático (día +1 / +7)**: NO se implementa.
- **Reporte semanal por mail al Gerente**: NO se implementa.
- **Dashboard operativo Airtable**: NO se crea.

**Razón:** decisión del cliente, esperando aprobación + cotización del módulo CRM.

**Activación futura:** ver upsell formal en `ops/04_upsells/SYS-upsell-crm-leads-2026-05-28.md` (USD 500 único + USD 30/mes adicional al retainer, bundle CRM + Seguimiento + Reporte).

## Notas críticas
- El agente NUNCA da precios de equipos — siempre deriva a representante comercial
- Insumos y repuestos tienen tienda online propia — el agente puede direccionar ahí (tool `consultar_url_tienda`)
- Notificación va por mail al representante asignado por línea de producto y zona, con copia al Gerente
- Seguimiento: día siguiente + semana siguiente (máximo 2 mensajes) — implementación en Etapa 2.1
- Audios e imágenes: bloqueados para Etapa 2.1 (no en v2.0)

## Bloqueos cliente (pre-flight Fase 0 del plan) — actualizado 2026-05-28

- [x] **Nombre del agente** → RESUELTO: el agente NO tiene nombre propio. Se presenta como "el asistente virtual de Sistemas y Soluciones". Variable `{{NOMBRE_AGENTE}}` eliminada del prompt.
- [x] **URL tienda online** → RESUELTO: `https://www.sistemasysoluciones.com`
- [x] **Mail del Gerente / contacto central** → RESUELTO: `info@sistemasysoluciones.com`
- [x] **Mapeo Representante → Línea + Zona** → RESUELTO: **Opción A — sin especialización**. Todos los leads van a `info@sistemasysoluciones.com`. La tabla Airtable `Representantes` se simplifica a 1 fila fallback. Tool `notificar_lead` NO hace lookup; manda mail directo a `info@`. Migrar a Opción B (con especialización) queda como cambio futuro si el cliente lo pide.
- [x] **Catálogo completo de equipos** → RESUELTO 2026-05-29: cliente entregó `BASE DE PRODUCTOS.xlsx` con 92 equipos (HUENU, DLICAN, TENETH, HANRUN, XENONS, RISO, Sinajet) + 10 cabezales (EPSON, RICOH, KM) + 33 insumos + 21 equipos Konica refurbished. Schema Airtable re-alineado, CSVs regenerados, prompt v2.0 → v2.1. Ver `06_docs/realineacion-post-excel-2026-05-29.md`.

## Archivos clave

### Plan y arquitectura
- `/Users/camilo/.claude/plans/contexto-general-del-dapper-sun.md` — **Plan Maestro Etapa 2** (17 secciones)
- `02_architecture/architecture-v2-2026-05.md` — Arquitectura v2 (componentes, integraciones, decisiones, capacidad, riesgos)

### System prompts
- `04_agents/agente-sistemasysoluciones-system-prompt.md` — **v2.4 actual** (2026-06-25 — Diagnóstico adaptativo por formato, feedback Jipi. ETAPA 3 ramificada A/B/C: plotters preguntan ancho+cabezales, láser papel cortado mantiene copias mensuales+color, DTF/sublimación mantiene volumen de prendas. Bloque nuevo "Rangos técnicos canónicos". Smoke 4/4 PASS contra webhook prod. Hereda v2.3 — `registrar_datos_lead`; v2.2 — USO DEL CONTEXTO DEL TURNO; v2.1 — `guardar_email` + Regla 26; v2.0 — Etapa 2)
- `04_agents/agente-sistemasysoluciones-system-prompt-v2.3.md` — Backup v2.3 (pre-diagnóstico adaptativo, último estado con `registrar_datos_lead` + flujos alquiler/demo merged del Google Doc)
- `04_agents/agente-sistemasysoluciones-system-prompt-v2.2.md` — Backup v2.2 (pre-`registrar_datos_lead`, último estado con `guardar_email` + sección "USO DEL CONTEXTO DEL TURNO")
- `04_agents/agente-sistemasysoluciones-system-prompt-v2.1.md` — Backup v2.1 (post-realineación Excel)
- `04_agents/agente-sistemasysoluciones-system-prompt-v2.0.md` — Backup v2.0
- `04_agents/agente-sistemasysoluciones-system-prompt-v1.7.md` — Backup v1.7 (Etapa 1)
- `04_agents/agente-sistemasysoluciones-system-prompt-v1.6.md` — Backup v1.6
- `04_agents/agente-sistemasysoluciones-system-prompt-v1.5.md` — Backup v1.5
- `04_agents/agente-sistemasysoluciones-system-prompt-v1.4.md` — Backup v1.4

### Schemas
- `05_crm/airtable-syscatalogo-schema.md` — Schema completo Airtable (11 tablas, seeds, vistas)
- `06_docs/supabase-schema.sql` — SQL ejecutable Supabase (4 tablas + 3 vistas + 1 función upsert)

### Specs
- `06_docs/tools-spec-v1.md` — Spec detallada de las 8 tools (inputs, outputs, implementación, validaciones)
- `06_docs/guia-airtable-edgardo-v1.md` — Guía de onboarding para Edgardo (operación Airtable)
- `06_docs/runbook.md` — Runbook operativo (incidentes comunes, queries SQL, escalamiento)

### Testing
- `07_testing/testing-guide-v6.md` — **v6 actual: testing Etapa 2** (18 casos simples + 16 flujos)
- `07_testing/testing-guide-v5b-retest-v1.7.md` — Re-test v1.7 (renombrado desde testing-guide-v6 viejo)
- `07_testing/testing-guide-v5.md` — Testing v1.6/v1.5
- `07_testing/testing-guide-v4.md` — Testing v1.4
- `07_testing/testing-guide-v3.md` — Testing v1.3
- `07_testing/testing-guide-v2.md` — Testing v1.2 (re-test)
- `07_testing/testing-guide-v1.md` — Testing v1.2 inicial

### Workflows (a construir Fase 3-4 del roadmap)
- `03_workflows/sys-agente-principal-v1.json` — pendiente (Fase 3)
- `03_workflows/sys-tool-buscar-equipo-v1.json` — pendiente (Fase 4)
- `03_workflows/sys-tool-consultar-tecnologia-v1.json` — pendiente
- `03_workflows/sys-tool-consultar-aplicacion-v1.json` — pendiente
- `03_workflows/sys-tool-consultar-compatibilidad-v1.json` — pendiente
- `03_workflows/sys-tool-consultar-faq-v1.json` — pendiente
- `03_workflows/sys-tool-consultar-lineas-priorizadas-v1.json` — pendiente
- `03_workflows/sys-tool-consultar-url-tienda-v1.json` — pendiente
- `03_workflows/sys-tool-notificar-lead-v1.json` — pendiente
- `03_workflows/sys-tool-guardar-email-v1.json` — **construido + importado 2026-06-02** (Tool 10, contrato minimalista alineado a alcance: `email` + opcionales `nombre`/`telefono` + `subscriber_id`/`session_id` desde contexto. Sheet `15OrQ-uI_x5rAorjkMpz_V_TvFxVf31nsDfTjm9oUqsc` tab `Emails` 6 cols. Credencial `la agencia` reutilizada. Pendiente: cablear toolWorkflow node en main v0.2.)

## Variables n8n requeridas (Etapa 2)

| Variable | Tipo | Estado |
|---|---|---|
| `MANYCHAT_API_KEY_SYS` | env secret | pendiente (cliente) |
| `MANYCHAT_AUTH_TOKEN` | env secret | pendiente (la agencia genera) |
| `MANYCHAT_FLOW_RESPONDER_MULTI_PARTE` | env | pendiente (la agencia crea en ManyChat) |
| `AIRTABLE_BASE_ID_SYS` | env | pendiente (después de crear base) |
| `AIRTABLE_TOKEN_SYS` | env secret | pendiente (después de crear base) |
| `OPENAI_API_KEY` | env secret | existente (compartido) |
| `TELEGRAM_BOT_TOKEN_INTERNO` | env secret | existente (compartido) |
| `TELEGRAM_CHAT_ID_EQUIPO_SYS` | env | pendiente (crear chat) |
| ~~`NOMBRE_AGENTE_SYS`~~ | — | ELIMINADA: sin nombre propio (2026-05-28) |
| `URL_TIENDA_SYS` | env | RESUELTO: `https://www.sistemasysoluciones.com` |
| `GMAIL_TO_LEAD_SYS` | env | RESUELTO: `info@sistemasysoluciones.com` (destino único de notificaciones de leads) |
| `GMAIL_FROM_SYS` | env | RESUELTO: `info@sistemasysoluciones.com` (mismo destino — el cliente puede ajustar a alias específico después si lo desea) |

## Próximos pasos

1. **Fase 0 — Pre-flight** (1-2 días): conseguir datos del cliente bloqueantes (nombre agente, URL tienda, mail Gerente, mapeo reps). Crear Supabase + Airtable workspaces.
2. **Fase 1 — Migración a Airtable** (3-5 días): crear base + tablas + seeds.
3. **Fase 2 — Supabase setup** (1 día): ejecutar `supabase-schema.sql`.
4. **Fase 3 — Memoria persistente** (1-2 días): main workflow con Postgres Chat Memory.
5. **Fase 4 — Tools build** (3-5 días): 8 sub-workflows.
6. **Fase 5 — System Prompt v2.0** (2 días): conectar tools al AI Agent + variables dinámicas.
7. **Fase 6 — Integración ManyChat** (2-3 días): flows, custom fields, multi-canal. **Adopta [ManyChat Standard interno 2026](../../_core/standards/manychat-integration-pattern.md)** — naming `ai_msg_1/2/3 + ai_msg_count` (no `parte1/2/3` legacy), auth via Credential `ManyChat - SYS`, payload dinámico vía Code node. Ver guía F6: `06_docs/f6-manychat-setup-guide.md`.
8. **Fase 7 — Testing E2E** (3-5 días): testing-guide-v6 al 100%.
9. **Fase 8 — Producción** (2-3 días): GO LIVE, monitoring, onboarding Edgardo.

Total estimado: 15-25 días.
