# Inputs para Migración VTR → GHL

> Checklist de todo el material necesario para completar Etapa 1 (deducción de lógica actual).
> Los items marcados con [x] ya están disponibles en el workspace.

---

## 1. Workflows n8n — ✅ 14/14 completo

| Workflow | ID n8n | Estado | Ubicación |
|----------|--------|--------|-----------|
| [Venttur] (principal) | — | [x] Disponible | `wf-venttur-main.json` |
| Meta CAPI - Venttur | `z98w2yWVEMOfifMl` | [x] Disponible | `wf-meta-capi.json` (también `../03_workflows/meta-capi-venttur-v2.json`) |
| CAPI Registro Folio - Venttur | `9yCbynoKDt9hgiBq` | [x] Disponible | `wf-capi-registro-folio.json` |
| Formulario Clientify - Venttur | — | [x] Disponible | `wf-formulario-clientify.json` |
| Actualizar 'Link enviado' - Venttur | — | [x] Disponible | `wf-actualizar-link-enviado.json` |
| Confirmación de agenda - Venttur | — | [x] Disponible | `wf-confirmacion-agenda.json` |
| Crear contacto Clientify y Airtable | — | [x] Disponible | `wf-crear-contacto-clientify-airtable.json` |
| Resumen, etiquetas, seguimientos | — | [x] Disponible | `wf-resumen-etiquetas-seguimientos.json` |
| Seguimiento agenda - Venttur | — | [x] Disponible | `wf-seguimiento-agenda.json` |
| Correo Semanal - Venttur | — | [x] Disponible | `wf-correo-semanal.json` |
| Rescate Post-Link | `mkEP1qFN7MVb9qP0` | [x] Disponible | `wf-rescate-post-link.json` (también `../03_workflows/wf-rescate-post-link-v3.json`) |
| Outreach Form Meta | `CUuFxbst3iHpgeXS` | [x] Disponible | `wf-outreach-form-meta.json` (también `../03_workflows/outreach-form-meta-venttur-v5.json`) |
| Estado lead (Contestó) | `b52CUYEkI2Ah3Xj6` | [x] Disponible | `wf-estado-lead.json` (también `../03_workflows/wf-estado-lead-venttur-v2.json`) |
| Estado interrumpida (barrido) | `H6qYB3Oj97bxaTCX` | [x] Disponible | `wf-estado-interrumpida.json` (también `../03_workflows/wf-estado-interrumpida-venttur-v2.json`) |

**Nota:** versiones normalizadas en `../03_workflows/` para referencia de producción. Los 4 últimos superan a las versiones que ya estaban guardadas en el repo (ver `ESTADO_MIGRACION.md` sección "Reconciliación workflows n8n" para el detalle de qué cambió).

---

## 2. ManyChat

- [x] **✅ EXPORT ACTUAL (2026-07-24)** en `vtr-data-snapshot-2026-07-24.json`: **16 flows + 4 folders** (lista vigente, supera los 14 de mayo), **5 tags**, **13 custom fields**, **page_info**, 0 widgets/growth tools. Los 5 endpoints (`getFlows/getTags/getInfo/getWidgets/getCustomFields`) confirmados funcionando.
- [x] **Contenido interno de flows** — 15 screenshots del editor en `manychat-flows-content-2026-07-20.md`. Cubre 12/14 flows conocidos + descubrió los 3 Outreach Touch 1/2/3. No cubiertos: "Asignar número" (bajo impacto) y el "Rescate Post-Link" viejo de ManyChat (reemplazado por el workflow n8n, ya está en detalle completo).
- [ ] **Keyword triggers CTWA** — la API pública de ManyChat NO los expone (por eso no están en el snapshot). Mapeo keyword→programa para leads click-to-WhatsApp. Parcialmente deducible de `programa_wpp` + rama CTWA de Meta CAPI + tabla `Mensajes anuncios`. Confirmar strings con el cliente si Etapa 1 lo requiere.
- [ ] **Configuración canal WA** — Número conectado, Business Account ID, proveedor API. Se necesita en Etapa 3 (diseño GHL), no para Etapa 1.

**Snapshots:** `manychat-snapshot-2026-05-13.md` (histórico, 14 flows) queda superado por `vtr-data-snapshot-2026-07-24.json` (16 flows, vigente). ⚠️ En el JSON, `manychat.flows` es un array de 1 wrapper `{flows:[16], folders:[4]}` — los 16 flows están anidados adentro.

---

## 3. Airtable

Base: `[AIRTABLE_BASE_ID]` (Venttur Dashboard)

| Tabla | ID | Estado | Ubicación |
|-------|----|--------|-----------|
| Folios CAPI | `[AIRTABLE_TABLE_ID]` | [x] Disponible (4.003 filas) | `airtable-csvs/folios-capi.csv` |
| Programas CAPI | `[AIRTABLE_TABLE_ID]` | [x] Disponible (4 programas) | `airtable-csvs/programas-capi.csv` |
| Leads | `[AIRTABLE_TABLE_ID]` | [x] Disponible (3.820 filas) | `airtable-csvs/leads.csv` |
| Mensajes anuncios | — | [x] Disponible (25 anuncios) | `airtable-csvs/mensajes-anuncios.csv` |
| Reporte semanal | — | [x] Disponible (37 semanas históricas) | `airtable-csvs/reporte-semanal.csv` |
| Tabla apoyo (ignorar) | — | [x] Disponible (2.114 filas) — el cliente indica que es descartable | `airtable-csvs/tabla-apoyo-ignorar.csv` |

**Schema real confirmado (extraído de los headers, no del doc viejo):**

- **Folios CAPI:** `Folio, fbclid, Programa, Timestamp, Landing URL, fbc, fbp, user_agent, ip, fbtrace_id`
- **Programas CAPI:** `Nombre del programa, Programa, pixel_id, access_token, default_url` — 4 programas: BS/BSG/BSC (Boarding IA) + HF (AA Familiar IA)
- **Mensajes anuncios:** `Anuncio, Mensaje, Interes` — mapea nombre de anuncio Meta → mensaje de apertura → programa de interés (24 anuncios activos)
- **Leads (29 columnas) — ¡incluye las FK que resuelven el linkeo entre plataformas!:**
  `id, id_2, Link asesoría enviado, Asistió, Agendan cita, Programa interés, Inicio Deseado, Tipo, Grado Escolar, Nivel Inglés, Creada, **ID Clientify**, **ID Manychat**, Nombre Completo, Email, Fuente lead, Folio, fbclid, Estado conversación, Última actividad, Outreach Form Meta enviado, Outreach Form Meta enviado at, Origen, Toques enviados, Ultimo toque at, Ad Name, Platform, Touch 1 programado at, Lead Score, Tipo lead`
  → `ID Clientify` e `ID Manychat` son la clave para cruzar 1:1 cada lead de Airtable con su contacto real en Clientify y su subscriber en ManyChat — crítico para la migración de datos a GHL Contacts.
- **Reporte semanal:** agregado semanal ya calculado (leads, cualificados, citas agendadas, tasa de conversión, tasa de asistencia) — replicar esta lógica en el nuevo stack o mantenerla en Airtable es una decisión de Etapa 3.
- **Tabla apoyo (ignorar):** `ID, Ultimo mensaje` — 2 columnas, guardada por completitud pero el cliente ya indicó que se descarta.

**Cómo exportar (si hace falta re-exportar por cambios):** Airtable → abrir tabla → menú ⋯ → Download CSV.

---

## 4. Clientify

- [x] **✅ EXPORTADO (2026-07-24):** `vtr-data-snapshot-2026-07-24.json`. Datos reales: **6.968 contactos + 2.338 deals + 266 companies + 22 custom fields**. Los 4 endpoints CONFIRMADOS con datos: `GET /contacts/`, `/deals/`, `/companies/`, `/custom-fields/` (los 3 últimos estaban "a verificar" — ya no).
- [x] **Endpoints reales confirmados** (extraídos de los HTTP Request nodes en producción): base `https://api.clientify.net/v1/`, auth `Authorization: Token <token>`. En uso por los workflows: `POST /contacts/` (crear), `GET /contacts/?phone=X` (buscar), `POST /contacts/{id}/tags/`, `POST /contacts/{id}/note/`.
- [x] **Workflow de export:** `wf-vtr-data-export-runner.json` (también en `../03_workflows/vtr-data-export-runner-v1.json`) — Clientify + ManyChat + Supabase en un solo flujo. Corrido OK. Nota: los deals/companies/custom-fields de Clientify NO se usan en ningún workflow de producción de VTR (Clientify se usa solo para contacts/tags/notes), pero se exportaron igual para tener el panorama completo del CRM que se migra a GHL.
- [x] **Tags de Clientify:** vienen embebidos por-contacto en cada registro (campo `tags`), no hay endpoint de lista separado necesario — se ven en el snapshot.
- [ ] **Estado de integración** — Confirmar si hay otros workflows o automatismos conectados a Clientify fuera de n8n

---

## 5. Supabase (Postgres)

- [x] **Schema confirmado por inspección de código** (no supuesto) — ver `supabase-queries-venttur.md` para el detalle completo y los queries de export.
- [x] Credencial n8n `Venttur` (id `ihpvM7nYMdLCwWDP`), tabla `n8n_chat_histories` (`id, session_id, message jsonb, created_at`), `session_id` = teléfono sin `+`.
- [ ] **Pendiente:** correr el query de `information_schema.tables` (incluido en `supabase-queries-venttur.md` §5) para confirmar si existe una segunda tabla `workflow_errors` — documentada en CLAUDE.md como usada por `outreach-form-meta-venttur` y `wf-rescate-post-link`, que son 2 de los workflows que todavía no tengo (ver reconciliación de la lista de 14 en `ESTADO_MIGRACION.md`).

---

## 6. Meta / Pixel

**No bloqueante para continuar la migración** (decisión del usuario, 2026-05-13) — la solución post-migración va a tener partes en Meta y en n8n, se cierra en una etapa posterior.

- [ ] Listado de pixels por programa, campaigns/adsets activas (queda para cuando se diseñe la Etapa 3)

---

## 7. GHL

**No bloqueante para continuar la migración** (decisión del usuario, 2026-05-13).

- [ ] Sub-account, subdomain, API key, plan tier, canal WA — se resuelve al iniciar Etapa 3 (diseño de arquitectura GHL)

---

## 8. Landings

- [ ] **URLs de landings activas** — El usuario puede pasar algunas pero no puede asegurar que sean todas todavía; pendiente de confirmar con Mauricio y Max
- [ ] **Estructura del webhook** — Qué campos manda, a qué URL
- [ ] **Estado del opt-in WA** — ¿Mauricio agregó el campo `whatsapp_optin`?

---

## Documentación existente (ya analizada)

- [x] `../06_docs/rescue-flow-implementation-guide.md` — Arquitectura rescate
- [x] `../06_docs/rescue-flow-message-templates.md` — 12 templates
- [x] `../06_docs/clientify-timeout-audit-2026-04-21.md` — Auditoría Clientify
