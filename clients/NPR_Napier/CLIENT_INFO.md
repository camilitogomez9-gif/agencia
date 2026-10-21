# NPR — Napier Salon

## Datos generales
- ID: NPR
- Nombre: Napier Salon
- Niche: Peluquería / Barbería
- Fecha inicio: 2026-04-21
- Status: **congelado en testing (2026-08-04)** — los 5 fixes manuales del workflow n8n quedaron descartados y no se aplican

## Stack activo
- [x] n8n
- [x] Airtable
- [ ] Clientify
- [ ] Google Sheets
- [ ] WhatsApp
- [x] Notion

## Contactos clave
| Rol | Nombre | Contacto |
|-----|--------|---------|
| Decisor / Dueño | Wilfrido | — |

## Descripción del proyecto

Agente conversacional para gestión de citas de la peluquería para hombres **Napier Salon**.  
El sistema tiene dos agentes: un Agente Principal (conversacional, atiende al cliente) y un Agente Admin (operativo, gestiona citas en Google Calendar + Airtable vía Subagente Calendario).

**Stack:** n8n + OpenAI GPT-4.1-mini + Google Calendar + Airtable + Chatwoot

**Staff:** NAPIER (Estilista Senior) · ALAN (Barbero) · WILSON (Barbero) · JULIA (Manicurista)

**Horario:** Mar–Vie 8am–5pm · Sáb 8am–6pm · Dom/Lun cerrado

**Zona horaria:** America/Santo_Domingo

## OKRs del proyecto
1. Reducir carga operativa de gestión de citas manual
2. Confirmar y cancelar citas sin intervención humana
3. Eliminar errores de doble-reserva via validación en Google Calendar + Airtable

## Archivos clave
- `03_workflows/sub-admin-napier-v1.json` — Workflow n8n Agente Admin (versión en build: nodo Fechas + Agente Principal + Subagente Calendario + Subagente CRM)
- `04_agents/agente-napier-principal-system-prompt.md` — System prompt v1.0 Agente Principal (conversacional, para el cliente)
- `04_agents/agente-napier-admin-system-prompt.md` — System prompt v1.0 Agente Admin (operativo, sin confirmaciones innecesarias)
- `04_agents/subagente-napier-calendario-system-prompt.md` — System prompt v1.0 Subagente Calendario (Google Calendar + Airtable)
- `04_agents/subagente-napier-crm-system-prompt.md` — System prompt v1.0 Subagente CRM (gestión de clientes en Airtable)

## Notas críticas
- El nodo `Fechas` (Code en n8n) pre-calcula `fecha_contexto` y lo inyecta en el User Message antes de ambos agentes. Las fechas relativas ("mañana", "el viernes") se resuelven ahí y NO deben calcularse dentro del LLM.
- ❌ **Bug conocido, corrección descartada el 2026-08-04:** el system prompt del nodo Subagente Calendario dice "Date & Time 2" pero la herramienta conectada se llama "Date & Time1". Corregir directo en el nodo del workflow (ya corregido en el .md de referencia).
- ❌ **Corregido en el system prompt, pero NO se aplica al workflow (descartado el 2026-08-04):** Operación B del Subagente Calendario reordenada — los lookups `buscar record cliente` (→ CLIENTE_ID) y `buscar record staff` (→ STAFF_ID) van PRIMERO antes de crear el evento en Calendar, para evitar confusión de IDs en el campo `cliente` de `Registro citas`. También se actualizaron las descripciones `$fromAI` de los campos `cliente` y `staff` del nodo `Registro citas`.
- La session key de Postgres Chat Memory es `[phone]_admin`. Para limpiar la memoria de un cliente específico, borrar la entrada con esa key en la tabla de Postgres.
