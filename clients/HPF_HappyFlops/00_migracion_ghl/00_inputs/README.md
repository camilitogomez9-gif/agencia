# 00_inputs — Material de Etapa 0 (Migración HPF → GHL)

Esta carpeta concentra todo el material que necesita Etapa 1 (Deducción de la lógica del sistema actual) para producir el Mapa Funcional sin lagunas.

Plan maestro: `planes/rol-act-a-como-scalable-hippo.md`

## Checklist de inputs

### ✅ Ya en el workspace
- [x] **Workflows n8n** — en `clients/HPF_HappyFlops/03_workflows/` (7 archivos JSON)

### ⬜ Pendientes — pasarlos a esta carpeta

#### 1. Airtable — `airtable/`
- [ ] `productos_imagen_principal.csv` — export completo de la tabla "Imagen Principal" (`tblsDWUQbfANNWMeK`) de la base `Productos | Happy Flops` (`appMHtUN9zKYODufC`)
- [ ] `productos_<otra_tabla>.csv` — cada tabla referenciada por `evento_id` en runtime (catálogo de productos por tipo de evento)
- [ ] `airtable_schema.md` — listado de campos de cada tabla, incluso campos no usados en n8n (para entender el modelo de datos completo)

#### 2. Kommo — `kommo/`
- [ ] `pipeline_etapas.csv` — todas las etapas del pipeline `11622596`: `id`, `name`, `color`, `sort_order`, automatizaciones asociadas
- [ ] `custom_fields_lead.csv` — todos los custom fields del lead: `id`, `name`, `type`, `enums` (si aplica)
- [ ] `salesbot_scripts/` — JSON o screenshots de los scripts de salesbot referenciados por `/api/v2/salesbot/run` (~30 nodos legacy en main-v2)
- [ ] `tags_activos.csv` — listado de tags en uso

#### 3. System prompt del agente — `agente/`
- [ ] `system_prompt_actual.md` — si está fuera de los JSON. Si solo vive embebido en los nodos LangChain del JSON, lo extraigo en Etapa 1 y dejo el resultado acá.

#### 4. GHL access — `ghl_access.md`
- [ ] Subdomain de la sub-account (o aviso de que hay que crearla)
- [ ] API key / Private Integration token
- [ ] Plan tier (para saber qué features están disponibles: Conversation AI, Workflows, Custom Objects, etc.)
- [ ] ¿Sub-account vacía existente o hay que crearla?

#### 5. Canales activos — `canales.md`
- [ ] Listado de canales por los que entran leads HOY: WhatsApp Business API directa, ManyChat, IG, FB, webchat, etc.
- [ ] Por cada canal: ¿quién es el dueño técnico (token/credentials)?

#### 6. Golden test set — `golden_transcripts/`
- [ ] 5-10 transcripts reales anonimizados (puede ser TXT o JSON con timestamps)
- [ ] Cada uno debe representar un caso del agente: lead nuevo, cotización, comprobante, abandono, etc.
- [ ] Para cada transcript, idealmente: outputs del sistema actual (mensajes enviados, etapas alcanzadas, notificaciones disparadas)

---

## Decisiones que tenés que confirmar antes de Etapa 3

(Ver plan maestro, sección "Decisiones que requieren tu confirmación antes de Etapa 3")

1. Modo de cutover: paralelo vs. secuencial con downtime
2. GHL Conversation AI nativo vs. n8n + OpenAI puente
3. Catálogo de productos: GHL Custom Objects vs. Airtable como source of truth
4. Memoria de conversación: GHL Conversations nativo vs. persistencia adicional
5. AmoCRM legacy: desactivar pre-migración vs. mantener hasta cutover

Podés responder esto antes o durante Etapa 0 — lo necesitamos firme antes de Etapa 3.
