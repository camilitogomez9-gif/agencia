# Guía detallada · Creación y deploy de las landings GHL (2026-09-22)

Reemplazan las landings de Clientify. **54 HTML ya generadas** (self-contained, on-brand Venttur) en
`00_migracion_ghl/05_ejecucion/landings-ghl/`, en 3 subdirectorios = **3 tipos**. Esta guía es para
**publicarlas** en `promo.venttur.com/<slug>` (deploy plano por slug, los subdirs son sólo organización del repo).

| Tipo | Subdir | # | Qué es | Generador |
|---|---|---:|---|---|
| **A · Aventurera (madre)** | `aventureras/` | 32 | brand + N botones (uno por programa) → landing de calendario con `?atribuida_a=<aventurera>` + redes propias de la aventurera | `generar-landings-aventureras-calendarios.py` |
| **B · Formulario** | `formulario/` | 12 | brand + form (pide datos → W4 + CAPI folio) + calendario. Para outreach/rescate (slugs hardcodeados) | `generar-landings-ghl.py` |
| **C · Calendario (secundaria)** | `calendarios/` | 10 | brand + logo + título + **calendario GHL embebido** (sin form). A donde apuntan los botones de las aventureras | `generar-landings-aventureras-calendarios.py` |

---

## 0. Cómo funcionan (2 flujos)

**Flujo aventurera (A → C):** replica el de Clientify.
```
Lead entra a  promo.venttur.com/agendar-<aventurera>      (TIPO A · madre)
   → ve N botones (1 por programa) + las redes de esa aventurera
   → toca un botón  →  promo.venttur.com/<Programa>-Calendario?atribuida_a=<aventurera>   (TIPO C)
        → landing con el calendario GHL embebido (brand, sin form)
        → agenda  → GHL crea/dedup el Contact, captura la URL (con ?atribuida_a=) en attributionSource.url
                  → dispara "Customer Booked Appointment" → W6 confirma + marca agendan_cita
                  (si no agenda en 45 min → Rescate GHL escribe)
```

**Flujo formulario (B):** para outreach/rescate donde queremos los datos primero.
```
Lead entra a  promo.venttur.com/<slug>?atribuida_a=<x>&fbclid=...   (TIPO B)
   → llena el form (nombre, apellidos, WhatsApp, email)
        → POST a W4 (vtr-form-landing-ghl-08d86c06) → Contact GHL con programa_interes+atribuida_a+folio+fbclid
        → POST a CAPI folio (capi-registro-folio-vtr-supabase) → registra el folio para Meta CAPI
   → se revela el calendario del programa → agenda → W6 confirma
```

- Teléfono → E.164 con `intl-tel-input` (default MX). `atribuida_a`/`fbclid` del query string; `folio` client-side.
- **Branding:** logo Venttur (CDN), navy `#0d1b40`, WhatsApp/IG de Venttur (las madres usan las redes propias de la aventurera).
- `entrenamientospe` (tipo B) lleva el **video de SPE**.

---

## 1a. TIPO A · Aventureras madre (32)

Una por aventurera, en `aventureras/agendar-<slug>.html`. Los slugs y las redes propias salen de las
originales de Clientify (`agendar-<name>.html`). Cada una tiene 3-5 botones (según los programas que
promovía esa aventurera) que llevan a las landings de calendario (tipo C) con `?atribuida_a=<slug>`.
Programa → botón: internado→Internados, afamilia→Intercambio con familia, summercamp→Summer Camp,
pathway→Pathway Alemania, gapyear→Gap Year. Slugs: `agendar-AlinaBuendia`, `agendar-AnaGo`, … (32 · ver dir · `agendar-ema` NO es aventurera: es el form de Internados).

## 1b. TIPO B · Formulario (12)

En `formulario/`. Slug → programa → calendario:

| slug | Programa | Calendar GHL | Slug |
|---|---|---|---|
| `agendar-ema` · `entrenamientospe` (+video) · `SPEagendar` | Internados | `CIxOV100yyRFqPoa6LdK` | 🔒 fijo |
| `AAFamilia-Agendar` | Intercambio académico con familias | `SiAPsk27X5yilff5bSS5` | 🔒 fijo |
| `SummerCamp-Agendar` | Campamentos de verano | `981EzNS7jf9HhJNkL41W` | 🔒 fijo |
| `PW_Alemania_Agendar` | Pathway Alemania | `oNN7oLWsNhQlWi7q7pDX` | 🔒 fijo |
| `EstudiaryTrabajar_Agendar` · `Estudiar-y-Trabajar-en-Australia` · `gap-year-agendar` | Gap Year / Estudia y Trabaja | `Omgde6Ko8TGKYMtiUb1x` | 🔒 (2) · 🟢 (1) |
| `viajes-educativos-agendar` | Viajes educativos | `j0jcAdaieJXaoPZBempp` | 🟢 |
| `educacion-superior-agendar` | Educación superior | `RUjWx74NPK77FPUcs5ME` | 🟢 |
| `cursos-idiomas-agendar` | Cursos de idiomas en el extranjero | `5PxslDhdQxZeDcKmLYNq` | 🟢 |

## 1c. TIPO C · Calendario secundarias (10)

En `calendarios/`. Brand + título + **el embed code real de GHL** (los que pasó la agencia). A donde apuntan los botones de las aventureras:

| slug | Calendar GHL | Embed |
|---|---|---|
| `Internados-Calendario` | `CIxOV100yyRFqPoa6LdK` | ✅ code de la agencia |
| `Intercambio-Calendario` | `SiAPsk27X5yilff5bSS5` | ✅ code de la agencia |
| `Campamentos-Calendario` | `981EzNS7jf9HhJNkL41W` | ✅ code de la agencia |
| `GapYear-Calendario` | `Omgde6Ko8TGKYMtiUb1x` | ✅ code de la agencia |
| `CursosIdiomas-Calendario` | `5PxslDhdQxZeDcKmLYNq` | ✅ code de la agencia |
| `EducacionSuperior-Calendario` | `RUjWx74NPK77FPUcs5ME` | ✅ code de la agencia |
| `JuanJose-Calendario` | `QJQyabdWhBgYtjeGcEKZ` | ✅ code de la agencia (calendario personal Juan José Alfaro) |
| `Niza-Calendario` | `fOsl9U4b40ulCczFwf69` | ✅ code de la agencia (calendario personal Niza Valeriano) |
| `PathwayAlemania-Calendario` | `oNN7oLWsNhQlWi7q7pDX` | ⚠️ **embed CONSTRUIDO** (la agencia no pasó el code; verificar el cal_id) |
| `ViajesEducativos-Calendario` | `j0jcAdaieJXaoPZBempp` | ⚠️ **embed CONSTRUIDO** (verificar) |

> 🔒/🟢 igual que antes (los tipo B tienen slugs hardcodeados en Meta/rescate). Los slugs de tipo A y C son
> nuevos/renombrables. Para regenerar: editá los generadores + re-corré (limpian y regeneran su subdir).

---

## 2. Publicación: GHL Funnels (decisión 22/9 · centralización)

**Las landings se publican dentro de GHL**, no en un host externo. Pasos operativos: **A2, A3 y B5 de la guía
raíz `guia-recta-final-ejecutable-2026-09-20.md`**. Resumen:

**Estado 22/9: hecho.** 50 landings en el funnel único `LP · Calendarios`, publicadas en `vtr.[TU-DOMINIO]`,
verificadas 50/50, en español de México (tuteo).

1. Fuente: `generar-landings-aventureras-calendarios.py` + `generar-landings-ghl.py` → `preparar-landings-ghl.py`
   → `landings-ghl/_ghl/`: 50 fragmentos (CSS acotado a `.vtr-lp`), `MANIFEST.md` (nombre, ruta GHL y SEO por
   step) y `redirects.json` + `REDIRECTS.md` (205 redirects: paths viejos de Clientify + las 2 URLs con `_`).
2. `generar-renderer-ghl.py --publicar` arma un JSON con las 50 landings (verificado byte a byte contra los
   fragmentos), lo sube a la biblioteca de medios de GHL y escribe `cargador.html`, que va en Configuración del
   funnel → *Código de seguimiento del cuerpo*. El cargador lee la ruta y dibuja la landing; ruta desconocida →
   Programas.
3. En GHL cada landing es un step **plantilla** (sección oculta) creado con Clonar paso + nombre y URL del paso
   (pestaña Publicación). GHL no admite `_` en rutas de step: `EstudiaryTrabajar_Agendar` y
   `PW_Alemania_Agendar` viven con `-` y la URL original entra por redirect.
4. En el cutover (B5): CNAME `promo` → `sites.ludicrous.cloud`, dominio `promo.venttur.com` en GHL, página por
   defecto y 404 = Programas (probado en `vtr.[TU-DOMINIO]`: ruta inventada → `/programas` con el query),
   todo en el asistente "Conectar un dominio" (enlazar a `LP · Calendarios` es aditivo: ensayado con `vtr2`, las
   50 páginas sirven en ~1 min sin sacar el dominio anterior; confirmar que el dominio principal del funnel quede
   en `promo`, porque de él sale el destino del 404), `crear-redirects-ghl.py --execute`
   y `verificar-landings-ghl.py --dominio promo.venttur.com` (+ `--redirects`).

> Los redirects sí van por API (`/funnels/lookup/redirect`, verificado con el PIT). Las páginas no: la API de
> GHL no crea steps de funnel.

---

## 3. Dependencias para que funcionen end-to-end

- **W4** (`LhPSfMYtQbNcEK32`) y **CAPI folio** (`4HgMkK34xqITULM3`) deben estar **ON** — se prenden en
  CUTOVER-2 (`cutover-toggles.py`). Antes del cutover el form POSTea a webhooks OFF (404) → el lead igual
  ve el calendario y puede agendar (degradación elegante, no rompe la conversión real).
- **Calendarios GHL** de los 8 programas: activos (ya creados, §0 de la guía de raíz).
- **W6** (`AS9ZNhY3GJDfhY3P`) ON + el GHL Workflow "Customer Booked Appointment" (Camilo) → confirma la cita.
- **Rescate** (`YB0UxwEVwzISdd54`) ON → escribe si no agendan.

---

## 4. Verificación (por landing)

Para cada slug:

1. `curl -I https://promo.venttur.com/<slug>` → **200**.
2. Abrí `https://promo.venttur.com/<slug>?atribuida_a=test-deploy` en incógnito → carga logo + headline + form.
3. Llená el form con datos de prueba + un teléfono real tuyo → enviá.
4. En GHL → **Contacts** → buscá el contacto → confirmá: creado, con `atribuida_a=test-deploy`, `programa_interes`
   correcto, `folio` poblado.
5. Confirmá que aparece el **calendario del programa correcto** (tabla §1) y que podés agendar.
6. (Post-agenda) confirmá que W6 mandó la confirmación por WhatsApp + `agendan_cita=true`.
7. Borrá el contacto de prueba.

**Verificación del flujo aventurera (A → C):**
1. Abrí `promo.venttur.com/agendar-<aventurera>` → carga logo + botones (1 por programa) + redes de esa aventurera.
2. Tocá un botón → va a `promo.venttur.com/<Programa>-Calendario?atribuida_a=<aventurera>` → carga el calendario.
3. Agendá de prueba → confirmá en GHL Contacts que el contacto tiene `attributionSource.url` con `?atribuida_a=<aventurera>`.

**Smoke rápido de atribución** (una vez varias publicadas): `scripts/reporte-aventureras.py --full`.

> ⚠️ **Embeds construidos:** `PathwayAlemania-Calendario` y `ViajesEducativos-Calendario` usan un embed
> armado con el cal_id (la agencia no pasó su code). Verificá que carguen bien antes de publicar; si el cal_id
> cambió, actualizalo en el generador.

---

## 5. Troubleshooting

| Síntoma | Causa probable | Fix |
|---|---|---|
| `curl` da 404 | slug no publicado / clean-URL mal | revisá el nombre del archivo = slug y la config de clean URLs |
| El form no crea contacto | W4 OFF (pre-cutover) o webhook mal | normal antes de CUTOVER-2; después, revisá que W4 esté ON |
| El calendario no carga | cal_id equivocado o calendario inactivo | verificá el `src` del iframe = `.../widget/booking/<cal_id>` de la tabla §1 |
| Bandera de país equivocada en el teléfono | `intl-tel-input` detecta por IP | cosmético; el número se guarda en E.164 igual |
| Atribución no aparece en GHL | el lead entró sin `?atribuida_a=` | el link de la aventurera debe llevar el query param (ver `generar-links-aventureras.py`) |

---

## 6. Datos que faltan para completar el módulo (no bloquean el deploy de landings)

- **Datos bancarios** (para el template de invoice/presupuesto, no para la landing) — pendiente ubicar.
- **Slugs reales de aventureras** — para `generar-links-aventureras.py --csv`.
