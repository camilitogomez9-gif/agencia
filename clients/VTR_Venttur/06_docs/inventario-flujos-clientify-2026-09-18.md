# Inventario de Flujos Clientify — 2026-09-18

Input directo para la Etapa 4 de la migración a GHL. Cada flujo → cómo se reconstruye.

## Legenda

- **Destino GHL:** propuesta de destino (Workflow / Funnel / se-descarta).
- Los flujos que solo tienen `_notemplate_` (sin plantillas ni freetext) son puro CRM — se recrean como GHL Workflow.
- Los flujos con freetext requieren decidir: submitear plantilla nueva a Meta O usar send free-form de GHL.

---

## Mauricio

### Afiliados Venttur

- Freetext: **`WA`** — body en `flujos de trabajo/Mauricio/Afiliados Venttur/_freetext_WA.txt`
- Freetext: **`leads_perfilamiento`** — body en `flujos de trabajo/Mauricio/Afiliados Venttur/_freetext_leads_perfilamiento.txt`
- Sin WhatsApp — solo CRM/tarea/email: 1 nodos

### Flujos Seguimiento Campaña EMA Erika

- Plantilla: **`mensaje_1_seguimiento_ema`** (WABA Rodrigo)
- Plantilla: **`seguimiento_ema_dia_10_3`** (WABA Rodrigo)
- Plantilla: **`seguimiento_ema_dia_15`** (WABA Rodrigo)
- Freetext: **`Campaña_Internados_Erika_Retargueting`** — body en `flujos de trabajo/Mauricio/Flujos Seguimiento Campaña EMA Erika/_freetext_Campaña_Internados_Erika_Retargueting.txt`
- Sin WhatsApp — solo CRM/tarea/email: 3 nodos

### RRHH

- Freetext: **`Mensaje_Candidatas_AUX_ADMN`** — body en `flujos de trabajo/Mauricio/RRHH/_freetext_Mensaje_Candidatas_AUX_ADMN.txt`
- Freetext: **`Mensaje_Candidatas_MKT`** — body en `flujos de trabajo/Mauricio/RRHH/_freetext_Mensaje_Candidatas_MKT.txt`
- Freetext: **`Sugerencias_mkt_OCC`** — body en `flujos de trabajo/Mauricio/RRHH/_freetext_Sugerencias_mkt_OCC.txt`

## Max

### Confirmaciones de citas

- Plantilla: **`confirmacion_0_cita_internados_2026`** (WABA Rodrigo)
- Plantilla: **`confirmacion_p1_boarding` → *consolidada en `confirmacion_0_cita_internados_2026` (2026-09-18)*** (WABA Rodrigo)

### Rescate No show


**Sub-flujos por programa:**
- **AA Familia - Rescate No show:** `rescate2_noshow_aafamilia` (WABA Rodrigo)
- **Boarding - Rescate No show:** `rescate2_noshow_internado` (WABA Rodrigo)
- **Pathway - Rescate No show:** `rescate2_noshow_pathway` (WABA Rodrigo)
- **Summer - Rescate No show:** `rescate2_noshow_summercamp` (WABA Rodrigo)

### Seguimientos - formulario - landings

- Plantilla: **`formulario_aa`** (WABA Rodrigo)
- Plantilla: **`formulario_aafamilia`** (WABA Rodrigo)
- Plantilla: **`formulario_boarding`** (WABA Rodrigo)
- Plantilla: **`formulario_boarding`** (WABA Rodrigo)

## Rodrigo

### EMA METODOLOGÍA

- Sin WhatsApp — solo CRM/tarea/email: 1 nodos

### OPERATIVO IDIOMAS

- Sin WhatsApp — solo CRM/tarea/email: 10 nodos

### OPERATIVO INTERNADOS

- Sin WhatsApp — solo CRM/tarea/email: 12 nodos
