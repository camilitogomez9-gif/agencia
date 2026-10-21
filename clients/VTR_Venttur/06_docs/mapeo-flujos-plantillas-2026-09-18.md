# Mapeo Flujos Clientify ↔ Plantillas Meta — 2026-09-18

Generado por `scripts/utilities/audit-clientify-flows-vs-templates.py`.

**Snapshot Clientify:** `/Users/camilo/Downloads/Clientify/flujos de trabajo/`
**Plantillas Meta:** 92 canónicas (50 WABA bot `1931874540684022` + 42 WABA Rodrigo `141523652373940`)

## Categorías

| Categoría | Significado |
|---|---|
| **Plantilla** | Screenshot con nombre exacto = plantilla Meta (dispara esa plantilla) |
| **Freetext** | Mensaje libre de sesión (`_freetext_*.png` + sidecar `.txt` con el body) |
| **Notemplate** | Flujo NO dispara WhatsApp (RRHH, tarea interna, CRM puro) |
| **Lanzador/Acción** | Detalle de trigger o step del flujo (con parámetros no visibles en canvas) |
| **Unknown** | Nombre de plantilla desconocido — resolver manualmente |
| **Mismatch** | Nombre sin prefijo que NO matchea con las 92 canónicas — alerta |

---

## Owner: Mauricio

### Afiliados Venttur
**Freetext (mensaje libre):**
- `WA`
  > ¡Bienvenida a Venttur! ¡Hola {{1}}! 🌟 Soy {{2}} de Venttur. ¡Qué alegría nos da …
- `leads_perfilamiento`
  > ¡Hola {{1}}, Espero que te encuentres muy bien! 👍  Tras tu interés en un interna…

**Notemplate (1):** `Oportunidad`

**Acción (2):** `accion_Oportunidad`, `accion_leads_perfilamiento`


### Flujos Seguimiento Campaña EMA Erika
**Plantillas Meta:**
- `mensaje_1_seguimiento_ema` (WABA Rodrigo, APPROVED)
- `seguimiento_ema_dia_10_3` (WABA Rodrigo, APPROVED)
- `seguimiento_ema_dia_15` (WABA Rodrigo, APPROVED)

**Freetext (mensaje libre):**
- `Campaña_Internados_Erika_Retargueting`
  > 👋 ¡Hola {{1}}!  Soy {{2}} de Venttur Education & Travel. 🌍✈️ Espero que estés bi…

**Notemplate (3):** `Campaña_Internados_Erika_Dia_20`, `Campaña_Internados_Erika_Dia_5`, `Campaña_Whatsapp_Erika`

**Acción (7):** `accion2_mensaje_1_seguimiento_ema`, `accion3_mensaje_1_seguimiento_ema`, `accion_Campaña_Internados_Erika_Retargueting`, `accion_Campaña_Whatsapp_Erika`, `accion_mensaje_1_seguimiento_ema`, `accion_seguimiento_ema_dia_10_3`, `accion_seguimiento_ema_dia_15`


### RRHH
**Freetext (mensaje libre):**
- `Mensaje_Candidatas_AUX_ADMN`
  > Hola {{1}}!  Mi nombre es {{2}} de Venttur Education & Travel. Nos dejaste tu CV…
- `Mensaje_Candidatas_MKT`
  > Hola {{1}}!  Mi nombre es {{2}} de Venttur Education & Travel. Nos dejaste tu CV…
- `Sugerencias_mkt_OCC`
  > ¡Hola {{1}}! Mi nombre es {{2}} de Venttur Education & Travel ¡Mucho gusto!  Te …


## Owner: Max

### Confirmaciones de citas
**Plantillas Meta:**
- `confirmacion_0_cita_internados_2026` (WABA Rodrigo, APPROVED)
- `confirmacion_p1_boarding` → *consolidada en `confirmacion_0_cita_internados_2026` (2026-09-18)* (WABA Rodrigo, APPROVED)

**Acción (1):** `accion_confirmacion_p1_boarding`


### Rescate No show
#### AA Familia - Rescate No show
**Plantillas Meta:**
- `rescate2_noshow_aafamilia` (WABA Rodrigo, APPROVED)

**Acción (2):** `accion_rescate2_noshow_aafamilia`, `accion_rescate2_noshow_aafamilia_-_etiqueta`

#### Boarding - Rescate No show
**Plantillas Meta:**
- `rescate2_noshow_internado` (WABA Rodrigo, APPROVED)

**Acción (2):** `accion_rescate2_noshow_internado`, `accion_rescate2_noshow_internado_-_etiqueta`

#### Pathway - Rescate No show
**Plantillas Meta:**
- `rescate2_noshow_pathway` (WABA Rodrigo, APPROVED)

**Acción (2):** `accion_rescate2_noshow_pathway`, `accion_rescate2_noshow_pathway_-_etiqueta`

#### Summer - Rescate No show
**Plantillas Meta:**
- `rescate2_noshow_summercamp` (WABA Rodrigo, APPROVED)

**Acción (2):** `accion_rescate2_noshow_summercamp`, `accion_rescate2_noshow_summercamp_-_etiqueta`


### Seguimientos - formulario - landings
**Plantillas Meta:**
- `formulario_aa_v2` (WABA bot · antes formulario_aa en Rodrigo, APPROVED)
- `formulario_aafamilia_v2` (WABA bot · antes formulario_aafamilia en Rodrigo, APPROVED)
- `formulario_boarding_v2` (WABA bot · antes formulario_boarding en Rodrigo, APPROVED)
- `formulario_boarding_v2` (WABA bot · antes formulario_boarding en Rodrigo, APPROVED)

**Acción (2):** `accion_formulario_aa`, `accion_formulario_aafamilia`


## Owner: Rodrigo

### EMA METODOLOGÍA
**Notemplate (1):** `AGENDÓ_CITA`

**Lanzador (1):** `AGENDÓ_CITA`

**Acción (1):** `accion_AGENDÓ_CITA`


### OPERATIVO IDIOMAS
**Notemplate (10):** `Aplicación_realizada_en_espera_de_documentos`, `Cambiar_a_seguimiento`, `Cambiar_oportunidad_a_Realizar_Aplicación`, `Cambio_de_oportunidad_recabar_datos_y_documentos_idiomas`, `Cobrar_Programa`, `Coordinar_llegada_IDIOMAS`, `Documentos_recibidos,_enviar_presupuesto_final`, `Enviar_comprobante_de_Pago`, `Enviar_correo_con_formulario_idiomas_prueba`, `Trámite_Visa`

**Acción (6):** `accion_Cambiar_a_seguimiento`, `accion_Cambiar_oportunidad_a_Realizar_Aplicación`, `accion_Cobrar_Programa`, `accion_Documentos_recibidos,_enviar_presupuesto_final`, `accion_Enviar_comprobante_de_Pago`, `accion_Enviar_correo_con_formulario_idiomas_prueba`


### OPERATIVO INTERNADOS
**Notemplate (12):** `Agendar_cita_escuela_+_familia`, `Agendar_cita_para_presentación_de_escuelas`, `Agendar_cita_perfilamientos_con_Cristy`, `Aplicación_internados_pt_2`, `Cambiar_a_seguimiento`, `Enviar_aplicación_a_escuela`, `Espera_de_aceptación_del_alumno`, `Esperar_resultados_de_perfilamientos_y_meter_datos_del_alumno_al_sistema`, `Estudiante_aceptado_inicio_orientación`, `Hacer_Aplicación_a_escuela`, `Presupuesto_Abierto_NO_pagado`, `Presupuesto_Pagado`

**Acción (9):** `accion_Agendar_cita_escuela_+_familia`, `accion_Agendar_cita_para_presentación_de_escuelas`, `accion_Aplicación_internados_pt_2`, `accion_Cambiar_a_seguimiento`, `accion_Enviar_aplicación_a_escuela`, `accion_Esperar_resultados_de_perfilamientos_y_meter_datos_del_alumno_al_sistema`, `accion_Hacer_Aplicación_a_escuela`, `accion_Presupuesto_Abierto_NO_pagado`, `accion_Presupuesto_Pagado`


---

## Plantillas Meta NO referenciadas (80/92)

Plantillas del dump que no aparecen en ningún screenshot. Candidatas a descartar o revisar si el flujo se bajó incompleto.

- `agenda_seg` — WABA bot · APPROVED · MARKETING · es_MX
- `boarding_form_follow` — WABA bot · APPROVED · MARKETING · es_MX
- `boarding_form_followup` — WABA bot · APPROVED · MARKETING · es_MX
- `boarding_form_followup_touch2` — WABA bot · APPROVED · MARKETING · es_MX
- `boarding_form_followup_touch3` — WABA bot · APPROVED · MARKETING · es_MX
- `candidatas_no_community_manager` — WABA Rodrigo · APPROVED · MARKETING · es_MX
- `confirmacin_cita_internados_nuevo` — WABA Rodrigo · APPROVED · MARKETING · es_MX
- `confirmacion_01_cita_boarding` — WABA Rodrigo · APPROVED · UTILITY · es_MX
- `confirmacion_02_cita_boarding` — WABA Rodrigo · APPROVED · UTILITY · es_MX
- `confirmacion_basica_hoy` — WABA Rodrigo · APPROVED · MARKETING · es_MX
- `confirmacion_cita_1_aafrancia` — WABA Rodrigo · APPROVED · MARKETING · es_MX
- `confirmacion_cita_1_boarding` — WABA Rodrigo · APPROVED · MARKETING · es_MX
- `confirmacion_cita_1_summer` — WABA Rodrigo · APPROVED · MARKETING · es_MX
- `confirmacion_cita_2_aafrancia` — WABA Rodrigo · APPROVED · MARKETING · es_MX
- `confirmacion_cita_2_boarding` — WABA Rodrigo · APPROVED · MARKETING · es_MX
- `confirmacion_cita_2_summer` — WABA Rodrigo · APPROVED · MARKETING · es_MX
- `confirmacion_cita_3_aafrancia` — WABA Rodrigo · APPROVED · MARKETING · es_MX
- `confirmacion_cita_3_boarding` — WABA Rodrigo · APPROVED · MARKETING · es_MX
- `confirmacion_cita_3_summer` — WABA Rodrigo · APPROVED · MARKETING · es_MX
- `confirmacion_cita_afiliados` — WABA Rodrigo · APPROVED · MARKETING · es_MX
- `confirmacion_cita_internados` — WABA Rodrigo · APPROVED · MARKETING · es_MX
- `entrevista_laboral_2` — WABA Rodrigo · APPROVED · MARKETING · es_MX
- `instrucciones_para_la_candidata` — WABA Rodrigo · APPROVED · MARKETING · es_MX
- `notificacion_candidatas_no_elegidas` — WABA Rodrigo · APPROVED · MARKETING · es_MX
- `notificacion_vacante_ocupada` — WABA Rodrigo · APPROVED · MARKETING · es
- `plantilla_formulario_aa` — WABA Rodrigo · APPROVED · MARKETING · en
- `postulantes_gerente_operativo` — WABA Rodrigo · APPROVED · MARKETING · es_MX
- `rescate1_noshow_aafamilia` — WABA Rodrigo · APPROVED · MARKETING · es_MX
- `rescate1_noshow_internado` — WABA Rodrigo · APPROVED · MARKETING · es
- `rescate1_noshow_pathway` — WABA Rodrigo · APPROVED · MARKETING · es_MX
- `rescate1_noshow_summercamp` — WABA Rodrigo · APPROVED · MARKETING · es_MX
- `saludo_despues_de_feria_educativa_alemania` — WABA Rodrigo · APPROVED · MARKETING · es_MX
- `saludo_entrevista_1` — WABA Rodrigo · APPROVED · MARKETING · es_MX
- `saludo_retomar_conversacion` — WABA Rodrigo · APPROVED · MARKETING · es_MX
- `seg_dia_1_bs` — WABA bot · APPROVED · MARKETING · es_MX
- `seg_dia_1_pw` — WABA bot · APPROVED · MARKETING · es_MX
- `seg_dia_3_aa` — WABA bot · APPROVED · MARKETING · es_MX
- `seg_dia_3_bs` — WABA bot · APPROVED · MARKETING · es_MX
- `seg_dia_3_gen` — WABA bot · APPROVED · MARKETING · es_MX
- `seg_dia_3_gy` — WABA bot · APPROVED · MARKETING · es_MX
- `seg_dia_3_ptw` — WABA bot · APPROVED · MARKETING · es_MX
- `seg_dia_3_sc` — WABA bot · APPROVED · MARKETING · es_MX
- `seg_dia_5_aa` — WABA bot · APPROVED · MARKETING · es_MX
- `seg_dia_5_bs` — WABA bot · APPROVED · MARKETING · es_MX
- `seg_dia_5_gen` — WABA bot · APPROVED · MARKETING · es_MX
- `seg_dia_5_gy` — WABA bot · APPROVED · MARKETING · es_MX
- `seg_dia_5_ptw` — WABA bot · APPROVED · MARKETING · es_MX
- `seg_dia_5_sc` — WABA bot · APPROVED · MARKETING · es_MX
- `seg_dia_7_aa` — WABA bot · APPROVED · MARKETING · es_MX
- `seg_dia_7_bs` — WABA bot · APPROVED · MARKETING · es_MX
- `seg_dia_7_gen` — WABA bot · APPROVED · MARKETING · es_MX
- `seg_dia_7_gy` — WABA bot · APPROVED · MARKETING · es_MX
- `seg_dia_7_ptw` — WABA bot · APPROVED · MARKETING · es_MX
- `seg_dia_7_sc` — WABA bot · APPROVED · MARKETING · es_MX
- `seguimiento_dia_1_aa` — WABA bot · APPROVED · MARKETING · es
- `seguimiento_dia_1_bs` — WABA bot · APPROVED · MARKETING · es
- `seguimiento_dia_1_gen` — WABA bot · APPROVED · MARKETING · es_MX
- `seguimiento_dia_1_gy` — WABA bot · APPROVED · MARKETING · es
- `seguimiento_dia_1_plantilla_sc` — WABA bot · APPROVED · MARKETING · es
- `seguimiento_dia_1_ptw` — WABA bot · APPROVED · MARKETING · es
- `seguimiento_dia_3_aa` — WABA bot · APPROVED · MARKETING · es
- `seguimiento_dia_3_bs` — WABA bot · APPROVED · MARKETING · es
- `seguimiento_dia_3_gen` — WABA bot · APPROVED · MARKETING · es_MX
- `seguimiento_dia_3_gy` — WABA bot · APPROVED · MARKETING · es
- `seguimiento_dia_3_ptw` — WABA bot · APPROVED · MARKETING · es
- `seguimiento_dia_3_sc` — WABA bot · APPROVED · MARKETING · es_MX
- `seguimiento_dia_5_aa` — WABA bot · APPROVED · MARKETING · es
- `seguimiento_dia_5_bs` — WABA bot · APPROVED · MARKETING · es
- `seguimiento_dia_5_gen` — WABA bot · APPROVED · MARKETING · es_MX
- `seguimiento_dia_5_gy` — WABA bot · APPROVED · MARKETING · es
- `seguimiento_dia_5_ptw` — WABA bot · APPROVED · MARKETING · es
- `seguimiento_dia_5_sc` — WABA bot · APPROVED · MARKETING · es_MX
- `seguimiento_dia_7_aa` — WABA bot · APPROVED · MARKETING · es
- `seguimiento_dia_7_bs` — WABA bot · APPROVED · MARKETING · es
- `seguimiento_dia_7_gen` — WABA bot · APPROVED · MARKETING · es_MX
- `seguimiento_dia_7_gy` — WABA bot · APPROVED · MARKETING · es
- `seguimiento_dia_7_ptw` — WABA bot · APPROVED · MARKETING · es
- `seguimiento_dia_7_sc` — WABA bot · APPROVED · MARKETING · es_MX
- `seguimiento_gen_no_agendo` — WABA bot · APPROVED · MARKETING · es_MX
- `seguimiento_reclutamiento_venttur` — WABA Rodrigo · APPROVED · MARKETING · es_MX
