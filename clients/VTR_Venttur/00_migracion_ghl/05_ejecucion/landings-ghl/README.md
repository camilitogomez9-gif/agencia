# Landings GHL (reemplazo de Clientify) · 2026-09-22

**50 landings en 3 subdirs** (fuente, español de México con tuteo). Para GHL: `scripts/preparar-landings-ghl.py` genera `_ghl/` (fragmentos + manifiesto + 205 redirects que crea `scripts/crear-redirects-ghl.py`) y `scripts/generar-renderer-ghl.py --publicar` arma el JSON y el cargador que las dibuja dentro del funnel `LP · Calendarios`. **No se pega código página por página.** Guía: `06_docs/guia-deploy-landings-2026-09-22.md` y A2/B5 de la guía raíz.

| Subdir | # | Tipo | Generador |
|---|---:|---|---|
| `aventureras/` | 32 | **A** · madre (brand + botones → calendario `?atribuida_a=` + redes propias) | `generar-landings-aventureras-calendarios.py` |
| `formulario/` | 12 | **B** · form (pide datos → W4 + CAPI folio) + calendario | `generar-landings-ghl.py` |
| `calendarios/` | 10 | **C** · brand + calendario GHL embebido (sin form) | `generar-landings-aventureras-calendarios.py` |

Todos on-brand Venttur, self-contained. La tabla de abajo es del **tipo B** (formulario). Los tipo A/C
+ el flujo aventurera están en la guía de deploy. Slugs de tipo B **alineados a §F + doc 13 §13.6**.

## Tipo B · Formulario — mapping slug → programa → calendario

**Modelo (decisión la agencia):** form → W4 (crea contacto GHL + `atribuida_a` + `folio`) + POST paralelo a
CAPI folio, luego se revela el **embed de calendario GHL** del programa. La cita se agenda en el
calendario → contacto GHL (dedup por teléfono) → W6 confirma.

| Archivo / slug | Programa (`programa_interes`) | Calendar GHL | Origen del slug |
|---|---|---|---|
| `agendar-ema` | Internados | `CIxOV100yyRFqPoa6LdK` | 🔒 Meta APPROVED (bloqueante) |
| `AAFamilia-Agendar` | Intercambio académico con familias | `SiAPsk27X5yilff5bSS5` | 🔒 Meta APPROVED (ya publicada §B) |
| `SummerCamp-Agendar` | Campamentos de verano | `981EzNS7jf9HhJNkL41W` | 🔒 Meta APPROVED (bloqueante) |
| `PW_Alemania_Agendar` | Pathway Alemania | `oNN7oLWsNhQlWi7q7pDX` | 🔒 Meta APPROVED (bloqueante) |
| `entrenamientospe` | Internados (funnel SPE) | `CIxOV100yyRFqPoa6LdK` | 🔒 Meta APPROVED (bloqueante) · **+ video SPE** |
| `SPEagendar` | Internados (funnel SPE) | `CIxOV100yyRFqPoa6LdK` | 🔒 Meta APPROVED (bloqueante) |
| `EstudiaryTrabajar_Agendar` | Gap Year / Estudia y Trabaja | `Omgde6Ko8TGKYMtiUb1x` | 🔒 Rescate F1 (hardcodeado) |
| `Estudiar-y-Trabajar-en-Australia` | Gap Year / Estudia y Trabaja | `Omgde6Ko8TGKYMtiUb1x` | 🔒 Rescate F1 (hardcodeado) |
| `gap-year-agendar` | Gap Year / Estudia y Trabaja | `Omgde6Ko8TGKYMtiUb1x` | 🟢 huérfano §F (renombrable) |
| `viajes-educativos-agendar` | Viajes educativos | `j0jcAdaieJXaoPZBempp` | 🟢 huérfano §F (renombrable) |
| `educacion-superior-agendar` | Educación superior | `RUjWx74NPK77FPUcs5ME` | 🟢 huérfano §F (renombrable) |
| `cursos-idiomas-agendar` | Cursos de idiomas en el extranjero | `5PxslDhdQxZeDcKmLYNq` | 🟢 huérfano §F (renombrable) |

> ⚠️ **Los 🔒 NO se pueden cambiar** — hardcodeados en mensajes del Rescate GHL (`promo.venttur.com/<slug>`)
> y/o en plantillas Meta APPROVED. Cambiarlos rompe outreach / dispara reaprobación Meta (24-72h).
> Los 🟢 huérfanos (§F, sin plantilla) son renombrables.
>
> **SPE** (`entrenamientospe` / `SPEagendar`) = Sistema Personal de Entrenamiento, funnel que lleva a
> Internados → usa `programa=Internados` + `cal-internados`. `entrenamientospe` lleva el video de SPE arriba.
> **AAFamilia-Agendar** ya estaba publicada (§B) — se incluye por completitud, verificar antes de re-deployar.

## Piezas swappeadas vs la Clientify original

| Clientify (viejo) | GHL (nuevo) |
|---|---|
| Widget meetings `app.clientify.com/meetings/script/7776.js` | iframe `api.leadconnectorhq.com/widget/booking/<calId>` + `link.msgsndr.com/js/form_embed.js` |
| Form POST `api.clientify.net/web-marketing/webforms/process/146952/` | `fetch` POST a W4 (`vtr-form-landing-ghl-08d86c06`) |
| Tracking/pixel Clientify | POST a CAPI folio (`capi-registro-folio-vtr-supabase`) + captura `fbclid`/`_fbp` |
| (marca preservada) | logo Unlayer CDN, navy `#0d1b40`, headline original, WhatsApp `+523319442476`, IG `venttur_` |

## Deploy

Pasos A2 (crear en GHL Funnels), A3 (verificación) y B5 (dominio `promo.venttur.com` + redirects en el cutover) de la guía raíz
`guia-recta-final-ejecutable-2026-09-20.md`. Datos de las aventureras: `_data/aventureras.json` (32).

**Nota webhooks:** W4 + CAPI folio nuevo están OFF hasta el cutover — antes de eso el form POSTea a webhooks
inactivos (degrada sin romper al lead: el calendario igual se revela y es la conversión real).
