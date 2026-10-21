# 05 · CAPI / Atribución — se queda en n8n + Airtable

> **🟡 Riesgo medio.** La atribución Meta CAPI **no migra a GHL** — se queda tal cual en n8n + Airtable (decisión confirmada Etapa 0). Este doc fija el borde: qué tablas y qué lógica permanecen fuera del perímetro GHL, el único fix (atribución data-driven en vez del hardcode Boarding), y cómo el CAPI se engancha al nuevo Contact de GHL.
>
> Corroborado contra `wf-meta-capi.json`, `wf-capi-registro-folio.json`, los CSVs de Folios/Programas/Mensajes anuncios.

---

## 1. Qué se queda (y por qué)

**Se queda en n8n + Airtable, sin cambios de topología:**

| Pieza | Qué es | Por qué se queda |
|---|---|---|
| `wf-meta-capi` (`z98w2yWVEMOfifMl`) | envía evento `Lead` server-side a Meta (2 ramas: FOLIO / CTWA) | lógica CAPI madura (SHA-256, Graph API v21); GHL no la reemplaza |
| `wf-capi-registro-folio` (`9yCbynoKDt9hgiBq`) | persiste la huella `fbc/fbp/fbclid/ip/ua` en el clic-a-WA | webhook desde la landing; independiente del CRM |
| Airtable **Folios CAPI** (4.003) | ledger de huellas de atribución | tracking, no CRM; no tiene sentido en GHL Contacts |
| Airtable **Programas CAPI** (4) | pixel_id + access_token + default_url por programa | config de pixels; vive con el CAPI |
| Airtable **Mensajes anuncios** (25) | anuncio Meta → mensaje de apertura → programa de interés | insumo de atribución (§3) |

**Razón raíz (`ESTADO` §Etapa 0):** *"n8n sigue siendo el cerebro; conserva la lógica CAPI (SHA-256, lookups, Graph API POST)."* El CAPI es medición, no gestión de leads — su casa natural es n8n, no el CRM.

---

## 2. El único fix — atribución data-driven (no hardcode Boarding)

**Hoy:** la rama CTWA de `wf-meta-capi` **hardcodea `{Programa}='BS'`** (nodo `Buscar Config Programa2`) → todo clic-a-WhatsApp se atribuye al pixel Boarding `228398216567258`, sin usar `programa_wpp` (que ni existe en el workflow). El cliente lo llamó *"correcto hoy (única campaña activa), insostenible mañana."*

**Fix (decisión cliente, atribución separada de conversación):**
- La **atribución** se determina por el **dato de referral de Meta** (el anuncio/pixel del que vino), **automática, interna, no se le pregunta al lead**.
- Se prepara el ruteo por **pixel/programa real** (aunque hoy solo Internados tenga campaña) → cuando se activen campañas de otros programas, cada una atribuye a su pixel, sin cambiar código.
- **No se toca la conversación:** el programa que rutea el calendario/asesor sale de lo que el lead **dice** (descubrimiento), no del anuncio (`06`, `01`). Atribución (medición) y conversación (ruteo) quedan **desacopladas**.

**Consecuencia:** los **keyword triggers CTWA se descartan** (`00` §6) — el mapeo keyword→programa deja de existir porque la conversación ya no deduce el programa del anuncio.

---

## 3. Mensajes anuncios (25) — atribución sí, ruteo no

La tabla `Mensajes anuncios` (anuncio → mensaje de apertura → `Interes`) hoy la usa el main para deducir `Fuente lead` **y** `Programa interés` matcheando el primer mensaje del lead. Con el desacople:
- **Se queda** para determinar **`Fuente lead`** (de qué anuncio/campaña vino) → medición.
- **Deja de usarse para el ruteo de programa** (eso lo pregunta el agente). El `Programa interés` que gobierna calendario/nurturing sale del descubrimiento.
- Enums de `Interes` (AA Familiar IA / Pathway IA / Boarding IA / Automatización - Comentarios) → alimentan atribución, no el enum canónico de ruteo (`01`).

---

## 4. Pixels por programa (estado real)

Solo **2 pixels / 4 códigos** existen:

| Código | Pixel | Programa |
|---|---|---|
| BS / BSG / BSC | `228398216567258` | Boarding (Internados) |
| HF | `24520910174237152` | AA Familiar (Intercambio académico) |

**Summer Camp, Pathway, Gap Year y los 3 huérfanos NO tienen fila en Programas CAPI** → su tracking CAPI es inexistente/forzado a Boarding vía el hardcode. El fix §2 prepara el terreno; **crear las filas de pixel cuando cada programa tenga campaña** (no antes) es parte de `10`.

---

## 5. Cómo el CAPI se engancha al nuevo Contact de GHL

Hoy `wf-meta-capi` hace lookup en Airtable Leads por teléfono (`filterByFormula {id}=<tel>`) para actualizar `Folio`/`id_2`/`fbclid`. **Decisión abierta N.4:** con Airtable Leads congelado post-migración, el lookup queda desactualizado. Opciones:
- **(a)** el CAPI consulta la **GHL API por teléfono** (el Contact de GHL es la nueva fuente) para resolver el lead → **preferida** (n8n-first, fuente única).
- **(b)** mantener un sync liviano GHL→Airtable Leads solo para el CAPI.

Los campos de atribución del lado del lead (`Folio`, `fbclid`) **no viven en el Contact de GHL como CRM** — se resuelven en la capa CAPI (Airtable Folios + el teléfono como llave). El Contact GHL solo necesita el teléfono canónico para el cruce. → validar en sandbox el lookup de Contact por teléfono vía API.

---

## 6. Bugs de datos de la capa CAPI (arrastrar/corregir)

| Bug | Detalle | Acción |
|---|---|---|
| **Regex de folio inconsistente** | main acepta `[A-Za-z0-9_]`, CAPI acepta `.+?` → folios con `-` (ej. `7T-UBW`) matchean en CAPI pero no en el main | unificar el regex |
| **Folios CAPI sin dedup** | CREATE puro, 4.003 filas con folios repetidos (`WRLWWQ` ≥2) | dedup por `event_id` ya existe en el envío; la tabla queda con ruido (tolerable) |
| **`utm_*` no se parsean** | llegan embebidos en `Landing URL`, no en columnas | oportunidad: parsear a custom fields si se quiere segmentar |
| **`Timestamp` ms vs s** | `fb.1.{ts}.{fbclid}` — CSV muestra 13 díg (ms), probablemente OK | verificar en el import |
| **Secretos en el CSV** | `access_token` de Meta por-programa expuesto en Programas CAPI | **rotar antes del handoff** |

---

## 7. Banderas de este mapping

1. **Lookup CAPI→Contact** (§5): validar el camino (a) GHL API por teléfono en sandbox; si no es viable, fallback (b).
2. **Filas de pixel de los programas sin campaña** (§4): se crean cuando haya campaña, no antes; el fix §2 no las inventa.
3. **`access_token` de Meta rotar** (secreto en el CSV).
4. **La landing `go.venttur.com/bs`** sigue disparando `wf-capi-registro-folio` en el clic — ese webhook **se queda**; lo que se repunta a GHL es el **formulario** (submit), no el registro de folio (`08` bandera 3, `10`).

---

*Corroborado contra `wf-meta-capi.json`, `wf-capi-registro-folio.json` y los CSVs de Folios (4.003) / Programas (4) / Mensajes anuncios (25). 2026-08-26.*
