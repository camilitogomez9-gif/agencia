# 09 · n8n — CAPI (se queda) + formulario/landing

> ### 🔄 Estado a 2026-09-07 — 🟡 PENDIENTE (sin cambios de diseño)
> El CAPI **se queda en n8n** (no migra). Pendiente [LA AGENCIA-n8n]: fix de atribución data-driven (sacar el hardcode `{Programa}='BS'`), enganche CAPI→Contact GHL por teléfono (asunción A5 ✅ ya resuelta), repunte del formulario/landing `go.venttur.com` a upsert de Contact GHL. **[LA AGENCIA] rotar el `access_token` de Meta** expuesto en el CSV `Programas CAPI` (higiene, ver `00 §Secretos`).

> **🟡 Riesgo medio.** La atribución Meta CAPI **no migra a GHL** — se queda tal cual en n8n + Airtable. Este módulo fija el borde (qué permanece fuera del perímetro GHL), el **único fix** (atribución data-driven en vez del hardcode Boarding), el enganche del CAPI al nuevo Contact de GHL, y el **repunte del formulario/landing** a GHL.
>
> **Para quién:** la agencia. **Prerequisito:** `06` (Contacts cargados, para el lookup por teléfono) + **sandbox A5** (lookup Contact por teléfono/CF). **Referencia:** `05_datos_capi_atribucion.md`, `08 §wf4`.
>
> **Estimado:** 3-5 hs. Corroborado contra `wf-meta-capi.json` (16), `wf-capi-registro-folio.json` (5), `wf-formulario-clientify.json` (9).

---

## 9.1 Qué se queda (sin cambios de topología)

| Pieza | Nodos | Por qué se queda |
|---|---|---|
| `wf-meta-capi` (`z98w2yWVEMOfifMl`) | 16 (airtable×7, code×3, httpRequest×2 Graph v21) | lógica CAPI madura (SHA-256, Graph API); GHL no la reemplaza |
| `wf-capi-registro-folio` (`9yCbynoKDt9hgiBq`) | 5 (webhook + airtable) | persiste la huella `fbc/fbp/fbclid/ip/ua` en el clic-a-WA; independiente del CRM |
| Airtable **Folios CAPI** (4.003) | — | ledger de huellas; no tiene sentido en GHL Contacts |
| Airtable **Programas CAPI** (4) | — | pixel_id + access_token + default_url por programa |
| Airtable **Mensajes anuncios** (25) | — | anuncio → mensaje de apertura → programa (§9.4) |

**Razón raíz (`ESTADO` Etapa 0):** el CAPI es **medición, no gestión de leads** — su casa natural es n8n, no el CRM.

---

## 9.2 El único fix — atribución data-driven (no hardcode Boarding)

**Hoy:** la rama CTWA de `wf-meta-capi` **hardcodea `{Programa}='BS'`** (nodo `Buscar Config Programa2`) → todo clic-a-WhatsApp se atribuye al pixel Boarding `228398216567258`, sin usar `programa_wpp`. Correcto **hoy** (Internados es la única campaña), **insostenible mañana** (rompe con la 2ª campaña).

🔧 **Fix (atribución separada de conversación):**
- La **atribución** se determina por el **dato de referral de Meta** (anuncio/pixel del que vino) — **automática, interna, no se le pregunta al lead**.
- Se prepara el ruteo por **pixel/programa real** (aunque hoy solo Internados tenga campaña) → cuando se activen otras campañas, cada una atribuye a su pixel **sin cambiar código**.
- **No se toca la conversación:** el programa que rutea calendario/asesor sale de lo que el lead **dice** (descubrimiento), no del anuncio (`01`/`06`).

**Consecuencia:** los **keyword triggers CTWA se descartan** (`00 §6`) — el mapeo keyword→programa deja de existir.

**Pixels reales (solo 2 / 4 códigos):** BS/BSG/BSC → `228398216567258` (Internados) · HF → `24520910174237152` (Intercambio). Summer/Pathway/Gap Year/los 3 huérfanos **NO tienen fila en Programas CAPI** → crear la fila de pixel **cuando cada programa tenga campaña** (no antes, `10`).

---

## 9.3 Enganche CAPI → Contact GHL (N.4)

Hoy `wf-meta-capi` hace lookup en Airtable Leads por teléfono (`filterByFormula {id}=<tel>`) para actualizar `Folio`/`id_2`/`fbclid`. Con Airtable Leads **congelado** post-migración, ese lookup queda desactualizado.

🔧 **Fix (N.4, preferida a — n8n-first):** el CAPI consulta la **GHL API por teléfono** (el Contact GHL es la nueva fuente) para resolver el lead. **Depende de sandbox A5** (lookup por teléfono exacto). Fallback (b): sync liviano GHL→Airtable solo para el CAPI.

Los campos de atribución (`Folio`, `fbclid`) **no viven en el Contact GHL como CRM** — se resuelven en la capa CAPI (Airtable Folios + teléfono como llave). El Contact GHL solo aporta el teléfono canónico para el cruce.

---

## 9.4 Formulario + landing → GHL

**`wf-formulario-clientify`** (9 nodos: webhook + airtable×2 + httpRequest×4 Clientify) — hoy crea lead en **Airtable + Clientify** desde el submit de la landing.

🔧 **RECONSTRUYE:** crea **Contact GHL** (no Clientify+Airtable); fix `isExecuted` (el bug del `Etiquetar Contacto` de VTR); persiste `programa_interes`.

**Landing `go.venttur.com/bs`:**
- **Sigue viva para orgánicos** (el formulario nativo de Meta la sustituyó solo para pago).
- 🔧 **Repuntar el submit a GHL** para que no quede como puerta muerta (`ronda-2`, `08 §wf3`). Las dos rutas (form Meta + landing) quedan funcionando e intercambiables.
- ⚠️ **El registro de folio NO se repunta:** el webhook `wf-capi-registro-folio` que dispara la landing **en el clic** se **queda** (es atribución, `05 §7.4`). Lo que se repunta a GHL es el **formulario** (submit), no el registro de folio.
- Un orgánico que entra por la landing → Contact GHL → alimenta el mismo despachador (`08`).

**Mensajes anuncios (25):** se queda para determinar **`Fuente lead`** (medición); **deja de usarse para el ruteo de programa** (eso lo pregunta el agente). Los enums de `Interes` alimentan atribución, no el enum canónico de ruteo (`01`).

---

## 9.5 Bugs de datos CAPI (arrastrar/corregir)

| Bug | Acción |
|---|---|
| Regex de folio inconsistente (main `[A-Za-z0-9_]` vs CAPI `.+?`) → folios con `-` matchean distinto | **unificar el regex** |
| Folios CAPI sin dedup (4.003 con repetidos) | dedup por `event_id` ya existe en el envío; la tabla queda con ruido (tolerable) |
| `utm_*` embebidos en `Landing URL` (no en columnas) | oportunidad: parsear a custom fields si se quiere segmentar |
| `access_token` de Meta por-programa **expuesto en el CSV** Programas CAPI | ⚠️ **rotar antes del handoff** |

---

## 9.6 Banderas y checkpoints

| Bandera | Estado |
|---|---|
| Lookup CAPI→Contact por teléfono | ✅ **sandbox A5: query por teléfono FUNCIONA** (`POST /contacts/search` con filtro anidado `{group,filters}`+`contains`; el `GET ?query=` no es fiable) → camino (a) viable. ⚠️ **UA obligatorio** (Cloudflare 1010) en el nodo HTTP. Fallback (b) sync GHL→Airtable solo si hace falta |
| Filas de pixel de programas sin campaña | se crean cuando haya campaña (`10`) |
| `access_token` Meta | **rotar** |
| Landing repuntada a GHL | dependencia de `10` (form de los huérfanos) |

✅ **Checkpoints de cierre:**
- [ ] `wf-meta-capi` + `wf-capi-registro-folio` intactos y corriendo (SE QUEDAN).
- [ ] CTWA data-driven (sin hardcode `{Programa}='BS'`).
- [ ] Lookup CAPI resuelve el Contact por GHL API (o fallback sync).
- [ ] Formulario reconstruido → Contact GHL; landing `go.venttur.com/bs` repuntada.
- [ ] Regex de folio unificado; `access_token` rotado.

---

*Corroborado contra `wf-meta-capi.json` (16, hardcode `{Programa}='BS'`), `wf-capi-registro-folio.json` (5), `wf-formulario-clientify.json` (9), CSVs Folios/Programas/Mensajes. 2026-09-03.*
