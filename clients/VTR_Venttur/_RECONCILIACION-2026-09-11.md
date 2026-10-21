# Reconciliación de la migración VTR — 2026-09-11

## Qué pasó

Existían **dos caminos paralelos** de la migración Venttur → GHL:

1. **Migración real (autoritativa)** — hecha con scripts entre el 3 y el 7 de septiembre (contactos importados, estructura GHL creada, agente nuevo en staging probado por Telegram). Llegó como carpeta limpia (`VTR_Venttur-limpio`) y **se adoptó como base** el 2026-09-11. Es la fuente de verdad.
2. **Track divergente (mío, superseded)** — armado en esta sesión duplicando el bot viejo de ManyChat. Quedó obsoleto al descubrir la migración real.

## Archivos del track divergente (superseded — conservados solo como referencia)

- `03_workflows/venttur-main-GHL-v1.json` → **gitignored** (tiene la OpenAI key hardcodeada; excluido hasta rotar)
- `03_workflows/wf-meta-capi-GHL-v1.json` + `wf-meta-capi-GHL-checklist.md`
- `03_workflows/wf-rescate-post-link-GHL-v1.json` + `wf-rescate-post-link-GHL-checklist.md`
- `00_migracion_ghl/04_guia_implementacion/` (guía M1-M9)
- `00_migracion_ghl/especificaciones-waba-traspaso.md`

**No usar estos como base.** La base real es el resto de `00_migracion_ghl/` (registro de ejecución, guía de migración de 12 módulos, arquitectura, ejecución).

## Qué se excluyó de git (PII + secretos) — ver `.gitignore`

- `00_inputs/airtable-csvs/` (leads con PII + token de Meta en texto plano)
- `05_ejecucion/salida-etl/` y `salida-import/` (8.525 contactos reales)
- `05_ejecucion/snapshots/n8n-vivo-*/` (workflows con secretos)
- `05_crm/*.csv` (teléfonos)

Estos archivos **siguen en la carpeta original** de Descargas (`VTR_Venttur-limpio`) si se necesitan.

## Estado real (resumen)

- **Datos migrados a GHL** (6.316 contactos + 2.299 opps + 266 companies, 2026-09-06).
- **Estructura GHL**: 56 custom fields + 20 pipelines + tags.
- **Agente nuevo** en staging (`3sLd7KY3o8I7NvXi`), probado por Telegram, con tools `crear_contacto` y `elevar` ya en GHL.
- **Bloqueante principal**: la WABA / número de WhatsApp (todo el canal cuelga de eso).

Detalle completo: `00_migracion_ghl/05_ejecucion/REGISTRO-EJECUCION.md` y `06_docs/guia-pendientes-pre-traspaso-waba-2026-09-07.md`.
