# Etapa 4 — Guía de Implementación Paso a Paso

> **Para quién:** la agencia (implementador técnico). Oscar supervisa y provee accesos.  
> **Prerequisito:** Etapa 3 completa (arquitectura en `03_arquitectura_ghl/`).  
> **Modelo de referencia:** esta guía asume lectura previa de los 8 documentos de arquitectura.

---

## Estructura de módulos

| Módulo | Archivo | Estimado |
|--------|---------|----------|
| **M1** — Setup inicial GHL | `01_setup_ghl.md` | 2-3 hs |
| **M2** — Pipeline, Custom Fields y Custom Values | `02_pipeline_y_campos.md` | 3-4 hs |
| **M3** — Custom Object: Producto | `03_custom_object_producto.md` | 2-3 hs |
| **M4** — Workflows GHL (WF-01 a WF-06) | `04_workflows_ghl.md` | 6-8 hs |
| **M5** — n8n: endpoints y lógica IA | `05_n8n_endpoints.md` | 8-10 hs |
| **M6** — Supabase: tablas y conexión | `06_supabase.md` | 1-2 hs |
| **M7** — WhatsApp WABA y plantillas Meta | `07_whatsapp_meta.md` | 2-4 hs |
| **M8** — Testing y validación pre-cutover | `08_testing_precutover.md` | 4-6 hs |
| **M9** — Cutover y go-live | `09_cutover.md` | 2-3 hs |

**Total estimado:** 30-43 horas de trabajo técnico.

---

## Orden de ejecución recomendado

```
M1 → M2 → M3 → M7 → M6 → M4 → M5 → M8 → M9
```

M7 (WhatsApp) se hace temprano porque la aprobación de templates Meta tarda 24-72 hs.  
M4 y M5 son paralelos si hay dos personas trabajando; si no, M4 antes (GHL primero, n8n después).

---

## Convenciones usadas en esta guía

- `[VALOR]` → placeholder que vos completás con el valor real
- `⚠️` → paso crítico, no saltear
- `✅` → checkpoint de verificación (confirmar antes de continuar)
- `📋` → copiar/pegar literal
- Nombres de stages GHL en **negrita**
- IDs de Kommo en `monoespaciado`

---

## Accesos necesarios antes de empezar

| Recurso | Quién lo provee | Dónde va |
|---------|----------------|----------|
| Cuenta GHL (crear sub-account) | la agencia | M1 |
| WhatsApp Business number de HPF | Oscar | M7 |
| Supabase Project URL + anon key + service key | Oscar (ya tiene cuenta Pro) | M6 |
| OpenAI API key HPF (o la de la agencia con límite) | la agencia/Oscar | M5 |
| Redis URL (Upstash o propio) | la agencia | M5 |
| Telegram Bot token + chat_id Oscar | Oscar | M5 |
| Número WA actual de Rebeca: `3315948670` | Oscar | M7 |

---

## Referencias cruzadas

Cada módulo referencia los documentos de arquitectura correspondientes:

- Pipeline → `03_arquitectura_ghl/01_pipeline_ghl.md`
- Custom Fields/Values → `03_arquitectura_ghl/02_data_model.md`
- Workflows GHL → `03_arquitectura_ghl/03_workflows_ghl.md`
- Agentes LLM → `03_arquitectura_ghl/04_agentes_llm.md`
- Re-engagement → `03_arquitectura_ghl/05_reengagement.md`
- Integraciones → `03_arquitectura_ghl/06_integraciones.md`
- Post-venta → `03_arquitectura_ghl/07_post_venta_y_handoff.md`
