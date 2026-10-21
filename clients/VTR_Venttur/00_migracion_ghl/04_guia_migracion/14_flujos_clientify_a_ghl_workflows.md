# 14 · Flujos Clientify → GHL Workflows

> **Status: draft del inventario · pendiente ejecución.** Alimentado por `06_docs/inventario-flujos-clientify-2026-09-18.md` (auditor Pieza 3, corrido 2026-09-18).

---

## 14.1 Fuente de verdad

- **Inventario canónico:** `06_docs/inventario-flujos-clientify-2026-09-18.md` — cada sub-carpeta con las plantillas Meta que dispara + freetexts + notas de destino.
- **Mapeo detallado:** `06_docs/mapeo-flujos-plantillas-2026-09-18.md` — matriz por categorías (Match/Freetext/Notemplate/Acción/Lanzador/Unknown) + huérfanas.
- **Subset crítico Meta:** `06_docs/plantillas-waba-rodrigo-a-reaprobar-2026-09-18.md` — 12 plantillas del WABA de Rodrigo a reaprobar en el WABA del bot antes del cutover.

## 14.2 Universo total

Del auditor (2026-09-18):
- **9 sub-carpetas** (flujos) distribuidos en 3 owners: Mauricio (6), Rodrigo (3), Max (0 raíz + 3 con sub-sub-carpetas por programa).
- **4 sub-sub-carpetas** en `Max/Rescate No show/` (una por programa: AA Familia, Boarding, Pathway, Summer).
- **71 screenshots clasificados** en 6 categorías + 0 mismatches.
- **Diego descartado oficialmente** — sus 7 flujos legacy no requieren migración.

## 14.3 Destino por flujo (propuesta)

Basado en el inventario. Se refina al construir cada uno.

### Mauricio (6 flujos)
| Flujo | Plantillas Meta | Freetext | Destino GHL |
|---|---|---|---|
| Afiliados Venttur | — | `_freetext_WA`, `_freetext_leads_perfilamiento` | GHL Workflow con Send Free-Form (solo dentro de ventana 24h) o submitear 2 plantillas nuevas si Meta acepta la temática. Ojo: contenido de referral con comisiones — Meta puede rechazar. |
| Evento La Garenne | — | — | (vacía en el snapshot — sub-carpeta creada sin bajar) |
| Flujos Seguimiento Campaña EMA Erika | `mensaje_1_seguimiento_ema` (Rodrigo), `seguimiento_ema_dia_10_3` (Rodrigo), `seguimiento_ema_dia_15` (Rodrigo) + 1 freetext | 1 freetext | GHL Workflow — Send template (3 plantillas del WABA Rodrigo, ver §14.4 abajo) + 1 free-form. |
| Padres de Familia Luminos. | — (2 screenshots Screenshot_YYYY-MM-DD) | — | Sin bajar. Screenshots autogenerados no interpretados. |
| Platica Sebastian 2025 | — | — | (vacía) |
| RRHH | — | 3 freetexts (Mensaje_Candidatas_MKT, Mensaje_Candidatas_AUX_ADMN, Sugerencias_mkt_OCC) | GHL Workflow interno para RRHH. Free-form dentro de ventana 24h — no requiere plantilla porque es reactivo a inbound del candidato. |

### Rodrigo (3 flujos)
| Flujo | Plantillas Meta | Notemplate/Lanzador/Acción | Destino GHL |
|---|---|---|---|
| EMA METODOLOGÍA | — | 1 notemplate + 1 lanzador + 1 acción | GHL Workflow puro CRM (crea oportunidad $25K MXN cuando cambia etapa a "Cita de Ventas concretada"). Ver `_accion_AGENDÓ_CITA.png` para parámetros. |
| OPERATIVO IDIOMAS | — | ~16 acciones y notemplates | GHL Workflow multi-step operativo (aplicación, cobro, documentos, etc.). Puro CRM. |
| OPERATIVO INTERNADOS | — | ~21 acciones y notemplates | GHL Workflow multi-step operativo. Puro CRM. |

### Max (3 flujos, todos con plantillas Meta)
| Flujo | Plantillas Meta | Destino GHL |
|---|---|---|
| Confirmaciones de citas | `confirmacion_0_cita_internados_2026`, `confirmacion_p1_boarding` (ambas WABA Rodrigo) + 1 acción | GHL Workflow con Send template + escalar a asesor. **Requiere reaprobación de ambas plantillas en el WABA del bot** (ver §14.4). |
| Rescate No show | 4 sub-flujos (uno por programa): `rescate2_noshow_aafamilia`, `_internado`, `_pathway`, `_summercamp` (los 4 del WABA Rodrigo) + `_accion_` con etiqueta | GHL Workflow con timing 24h post-no-show. **Reaprobar las 4 plantillas.** |
| Seguimientos - formulario - landings | `formulario_aa_v2`, `formulario_aafamilia_v2`, `formulario_boarding_v2` (renombradas al subir al WABA del bot — 18/9 cooldown en originales) + acciones | GHL Workflow trigger `Form Submitted` → send template. **Reaprobar las 3 plantillas.** |

## 14.4 Cruce con reaprobación de plantillas Meta

Las **11 plantillas del WABA de Rodrigo** (consolidada `confirmacion_0_cita_internados_2026` con `confirmacion_p1_boarding` — idénticas) listadas en `06_docs/plantillas-waba-rodrigo-a-reaprobar-2026-09-18.md` con **body real** para submit inmediato:

1. `confirmacion_0_cita_internados_2026` — Confirmaciones de citas (Max)
2. `confirmacion_p1_boarding` — Confirmaciones de citas (Max)
3. `formulario_aa` — Seguimientos formulario (Max)
4. `formulario_aafamilia` — Seguimientos formulario (Max)
5. `formulario_boarding` — Seguimientos formulario (Max)
6. `mensaje_1_seguimiento_ema` — Flujos EMA Erika (Mauricio)
7. `rescate2_noshow_aafamilia` — Rescate No show (Max)
8. `rescate2_noshow_internado` — Rescate No show (Max)
9. `rescate2_noshow_pathway` — Rescate No show (Max)
10. `rescate2_noshow_summercamp` — Rescate No show (Max)
11. `seguimiento_ema_dia_10_3` — Flujos EMA Erika (Mauricio)
12. `seguimiento_ema_dia_15` — Flujos EMA Erika (Mauricio)

**Acción inmediata:** submitear las 12 al WABA del bot (`1931874540684022`) vía Meta BM UI o `POST /{waba}/message_templates` con el body del dump. 24-72h de review por plantilla. Empezar YA — cutover Clientify 26-27/9 (8-9 días).

## 14.5 Freetexts a decidir

De los 6 freetexts detectados:
- **RRHH (3):** contenido interno de reclutamiento. Recomendación: **NO submitear a Meta** — usar Send Free-Form de GHL dentro de ventana 24h (el candidato mandó CV, hay ventana abierta).
- **Afiliados Venttur (2):** contenido de reclutamiento de afiliadas para referrals. Meta probablemente rechaza (política MLM). Recomendación: **evaluar rediseño del texto** para pasar review Meta como MARKETING, o descartar la línea si no es prioridad estratégica.
- **Campaña EMA Erika Retargueting (1):** contenido de seguimiento a leads. Recomendación: **submitear como plantilla nueva** al WABA del bot (probablemente pasa review sin ajuste).

## 14.6 Sin migración

- **Todos los flujos de Diego** — descartados (owner salió del ruteo).
- **Sub-carpetas vacías** (`Evento La Garenne`, `Platica Sebastian 2025`) — la agencia no bajó screenshots. Si esas landings/flujos siguen activos en Clientify, revisar antes del cutover si vale la pena bajarlos. Si no aparecen en el `promo.venttur.com/*` linkeado desde plantillas Meta, se pueden dar por muertos.
- **Screenshots autogenerados** en Padres de Familia Luminos. (`Screenshot 2026-09-16 at 16.11.43.png`) — sin naming convention, sin interpretación. Revisar manualmente o descartar.
