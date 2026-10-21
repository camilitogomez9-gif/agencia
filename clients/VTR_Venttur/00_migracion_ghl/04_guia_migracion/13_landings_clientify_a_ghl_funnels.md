# 13 · Landings Clientify → GHL Funnels

> **Status: draft del inventario · pendiente ejecución.** Alimenta la Pieza 4 del plan `harmonic-prancing-raven.md`. Depende de: DNS del dominio (`sites.ludicrous.cloud`), 8 calendarios de GHL creados (`04`), Etapa 4 GHL desbloqueada.

---

## 13.1 Fuente de verdad

El snapshot manual del 18/9 vive en `/Users/camilo/Downloads/Clientify/landings y calendarios/`, organizado por owner. La estructura y estado se enumeran en:

- `landings y calendarios/Mauricio/landings.md` — 206 URLs distribuidas en 7 sub-carpetas (`Estudia y trabaja Australia`, `Registros La Garenne`, `otros`, `PMR`, `GAP Year`, `EMA`, `Landing referenciadoras`). La sección "Landing referenciadoras" tiene 31 sub-carpetas (aventureras) × 3 h3 (`{Aventurera}` + `PROGRAMAS RODRIGO` + `PROGRAMAS ANDRES`), con ~4-6 URLs cada una. La Pieza 1 (extract-clientify-landing-ids.py) procesó 13/206 URLs con IDs auto-extraídos; el resto quedan solo como URL + og_title parcial (se pueden anotar corriendo Pieza 1 con más tiempo o en batches).
- `landings y calendarios/Andrés/landings.md` — 10 URLs en 2 sub-carpetas (`Ferias estudiantiles`, `Pathway Alemania`). Todas anotadas.
- `landings y calendarios/Max/landings.md` — 21 URLs en 6 sub-carpetas (`Platica Sebastian`, `TU HIJO EL MUNDO Y SU FUTURO`, `Campaña Alemania oferta de valor pathway`, `Boarding School` con sub-carpetas por variante — Girls/Prestigio/Deportes, `General - Venttur`, `Intercambio Académico con familia`). Todas anotadas.

## 13.2 Regla de rebuild

**Cada URL de `promo.venttur.com/*`** = **1 GHL Funnel** con path preservado exacto. Ejemplo:

| URL Clientify actual | GHL Funnel destino |
|---|---|
| `https://promo.venttur.com/EstudiaryTrabajar_Agendar` | Funnel con path `/EstudiaryTrabajar_Agendar` bajo dominio `promo.venttur.com` (CNAME → `sites.ludicrous.cloud`) |
| `https://promo.venttur.com/lagarenne-GDL-marissa` | idem con `/lagarenne-GDL-marissa` |
| `https://promo.venttur.com/agendar-DiegoG` | idem con `/agendar-DiegoG` (referenciadoras — la aventurera "Diego Garcia" apunta a los links de los asesores) |

**No cambiar paths** — están hardcodeados en las 92 plantillas Meta aprobadas y en workflows de n8n. Cualquier cambio dispara reaprobación Meta (24-72h) y rompe outreach.

## 13.3 Contenido de cada Funnel

Para cada landing, el Funnel de GHL tiene 3 componentes según su tipo:

- **Landing de agendamiento** (tiene `meeting_id` en `landings.md`): el Funnel embebe el calendario GHL correspondiente (uno de los 8 calendarios Round Robin de `04`). El `meeting_id` de Clientify es solo referencia visual — el calendario GHL se crea desde cero.
- **Landing de registro a evento** (tiene `superform_id` + `webform_id`, típico "La Garenne", "Boarding" para submitir datos): el Funnel embebe un GHL Form con los campos del formulario original.
- **Landing referenciadora** (aventurera): puede tener solo texto/CTA para redirigir a un funnel de agendamiento del programa. Cada aventurera tiene 1 madre + 5 hijos (uno por programa).

## 13.4 Setup de dominio

Ver `harmonic-prancing-raven.md §Pieza 4` para la estrategia zero-downtime:
1. Semanas -3 a -1: buildear todo en `staging-promo.venttur.com` con CNAME → GHL.
2. -48h: bajar TTL del CNAME `promo.venttur.com` a 60s.
3. Día D: agregar `promo.venttur.com` en GHL, relinkear cada funnel, flip CNAME.
4. Post-D: 301 redirects granulares como red de seguridad.

## 13.5 Estimación por lote

| Lote | Landings | Esfuerzo estimado |
|---|---:|---:|
| **Priorizado (6 paths bloqueantes de plantillas Meta APPROVED)** | **6** | **5-8h** ← ver §13.6 |
| Agendamiento estándar (con calendario) | ~9 restantes | ~4h con 3 templates maestros clonados |
| Registro a evento (formularios) | ~20 | ~8h |
| Referenciadoras (aventureras × programas) | ~120 | ~20h con Mecanismo #1 (hidden field), +8-12h si el test §07 falla y se cae al Mecanismo #3 |
| **Total** | ~155 | **~37-52h** — pero ver §13.7 para el análisis de por qué el sub-lote aventureras puede colapsar radicalmente |

Alineado con estimación original en `harmonic-prancing-raven.md §Pieza 4` (40-55h con QA + setup).

---

## 13.6 Lote priorizado — 6 paths hardcodeados en plantillas Meta APPROVED (bloqueantes)

**Contexto crítico (revisado 19/9 post-audit):** de las 155-237 landings totales, sólo **6 paths rompen si no se rebuild antes del cutover**. Son los que están hardcodeados en el body de plantillas Meta ya **APPROVED** por Meta (`submit-templates-log.json`). Cambiar el path = trigger re-aprobación de la plantilla (24-72h). El resto de landings o no están en plantillas Meta (solo en workflows n8n o texto ManyChat), o sus plantillas todavía están en cola de aprobación (se pueden ajustar antes del 26/9).

### Los 6 paths bloqueantes

| # | Path (bajo `promo.venttur.com/`) | Programa | Plantillas Meta APPROVED que lo hardcodean |
|---|---|---|---|
| 1 | `/AAFamilia-Agendar` | Año Académico Familia | `formulario_aa_v2` (APPROVED), + pending relacionadas del outreach |
| 2 | `/PW_Alemania_Agendar` | Pathway Alemania | pendientes del outreach `pw_alemania_*` |
| 3 | `/SummerCamp-Agendar` | Summer Camp | pendientes del outreach `summercamp_*` |
| 4 | `/agendar-ema` | Boarding School (fallback bot) | 3+ plantillas del flow EMA Erika (`mensaje_1_seguimiento_ema`, `seguimiento_ema_dia_15`, `seguimiento_ema_dia_10_3`) |
| 5 | `/entrenamientospe` | SPE (Sistema Personal de Entrenamiento) | `seguimiento_ema_dia_10_3` (video link) |
| 6 | `/SPEagendar` | SPE | 3 plantillas APPROVED lo hardcodean (agregado post-audit 19/9) |

**+1 URL Clientify huérfana** (no path canónico pero también bloqueante): la URL embebida en el flow `saludo_despues_de_feria_educativa_alemania` — es un link único que muere con Clientify y no está capturado en el inventario general. Requiere identificación específica (extract del snapshot Clientify de Andrés).

### Sacados del lote priorizado (falsos positivos del análisis original)

- `/EstudiaryTrabajar_Agendar` — aparece SOLO como texto en flows ManyChat, no en body de plantillas Meta. No rompe Meta si cambia. Se puede rebuild post-cutover.
- `/Estudiar-y-Trabajar-en-Australia` — idem, solo texto en el prompt del agente (v2.2 lo mapea a Andrés).

### Ventana de ejecución

- **21-22/9 (T-5 a T-4):** Camilo rebuilda los 6 paths priorizados en GHL Funnels UI (5-8h estimadas: ~3 templates maestros clonados + personalización de CTA + embed de calendarios GHL correspondientes).
- **Verificación:** para cada uno, abrir en incógnito y confirmar que carga bien + el CTA lleva al calendario correcto.
- **Setup CNAME zero-downtime:** ver `harmonic-prancing-raven.md §Pieza 4` — se pega al vivo el D-day 26/9 en el paso del cutover.

---

## 13.7 Sub-lote aventureras — por qué existen y cómo colapsan

**Por qué existen:** Venttur generó ~30 landings madres + ~120 hijas (una por combinación aventurera × programa) porque en Clientify **el único mecanismo de atribución era el path de la URL**. Cada aventurera necesitaba su propio slug (`/agendar-{Nombre}-{programa}`) para que el sistema supiera de qué agente comercial venía el lead al agendar.

**Cómo colapsan en GHL:** GHL soporta **Query Key + Hidden Field** en calendarios: 1 landing template + 1 calendario + N valores del hidden field (via query string) = misma atribución sin necesidad de ~120 landings distintas. La verificación técnica está en el runbook cutover `§07 test hidden fields` (15 min de ejecución de la agencia).

**Escenarios:**
- **Mecanismo #1 (hidden field pasa OK):** ~120 landings de aventureras se colapsan a **1-5 templates** + hidden field. Effort baja de ~20h a **~2-4h** (armar los templates + generar los 30-120 links parametrizados para las aventureras).
- **Mecanismo #3 (fallback, si hidden field falla):** workflow post-booking en GHL que parsea el URL de referrer y escribe el custom field. Effort: +8-12h de setup del workflow, pero también evita las 120 landings.

**En ambos escenarios el sub-lote aventureras deja de ser ~20h para volverse ~2-12h.** Este es el mayor ahorro potencial de la migración de landings — mucho más grande que el ahorro por API (evaluado y descartado el 19/9: solo 15-25% via CRUD de Redirects, ver `06_docs/notas-ghl-api-funnels-2026-09-19.md` — TODO crear).

### Prerrequisito bloqueante

**Test §07 hidden fields (15 min, la agencia)** — sin este test corrido y confirmado, el sub-lote aventureras no arranca. Es el gate crítico. Runbook exacto en `06_docs/guia-recta-final-cutover-2026-09-16.md §07`.

### Ownership y ventana

- **Test §07:** la agencia ejecuta 22/9 (T-4).
- **Aventureras rebuild:** Camilo, 22-24/9 (T-4 a T-2), dependiendo del resultado del test.
- **Slugs canónicos:** el cliente (Mauricio) debe confirmar la nomenclatura final de aventureras antes de arrancar (hoy hay 30 madres con inconsistencias: algunas con guión final, otras con `-Australia`, etc.). Bloqueante T-3.
