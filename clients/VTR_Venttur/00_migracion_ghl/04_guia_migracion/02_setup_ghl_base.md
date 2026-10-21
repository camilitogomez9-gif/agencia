# 02 · Setup GHL base — sub-cuenta, usuarios/owners, custom fields, tags

> ### 🔄 Estado a 2026-09-07 — ✅ HECHO (por API, read-back verificado)
> **56 custom fields** (52 contact + 4 opportunity) creados con dataType correcto · **enum `programa_interes`** (8 canónicos) · **5 tags** (`RESCATE_PROGRAMA_NO_MAPEADO`, `LINK_ABANDONADO_FRIO`, `seguimiento_agenda`, `seguimiento` + **`cualificado`** `SAf2PNSjPNNYJisUSAFq`). **Usuarios creados**: Rodrigo `IaSkyQuhbjGdwNyXg1VD`, Andrés `4VtbDVSjnoHm5125qa8I`, Max `rlxMWsDRGCwJdhY6HkrU`, + Diego García / Juan José Alfaro / Niza. **Diego Matus NO se creó** (sus deals → Juan José Alfaro). Credencial n8n `GHL VTR (PIT)` `YkVmaA4jlRbO1TQD`.
> **🔴 [CLIENTE] pendiente:** emails reales de los usuarios (Mauricio/Max) si se usan para las notificaciones del handoff.

> **🟡 Riesgo medio.** El esqueleto del CRM: la configuración de la sub-cuenta, el mapeo de owners a usuarios GHL, y **toda la lista canónica de custom fields y tags** que después leen/escriben el import (`06`) y los workflows (`07`-`09`). Se puede empezar **en paralelo al sandbox** — crear campos y usuarios no depende de los comportamientos que valida `01` (solo A2 y A6 deciden si un par de campos van a nativo vs custom).
>
> **Para quién:** la agencia. **Prerequisito:** sub-cuenta creada (✅) + Private Integration token (`01 §0`). **Referencia:** `03_arquitectura_ghl/02_datos_contactos_identidad.md §3-5/§9`, `04_datos_campos_tags.md`, `01_taxonomia_programas.md §1`, `03 §3/§5`.
>
> **Estimado:** 3-4 hs. **Corroborado contra el sistema real** (snapshot 2026-07-24 + `leads.csv`) — no contra la prosa.

---

## 2.1 Configuración base de la sub-cuenta

| Setting | Valor | Por qué | Depende de sandbox |
|---|---|---|---|
| **Currency (location)** | `MXN` | Es la moneda dominante; los USD se preservan por Opportunity con el custom `moneda` (§2.5) | A6 |
| **Timezone** | `America/Mexico_City` | Todo el negocio es MX; el agente y los recordatorios calculan sobre esta TZ | — |
| **Allow Duplicate Contacts** | ⚠️ **OFF** | Es la premisa del merge de `06` (dedup por teléfono/email). Con ON, el import crea duplicados | A1 |
| **Business Profile** (nombre, dominio) | Venttur | Aparece en el inbox y en OBA de WhatsApp | — |

✅ **Checkpoint:** confirmar que *Allow Duplicate Contacts* = OFF **antes** de cargar un solo contacto en `06`.

---

## 2.2 Usuarios y owners (mapeo Clientify → GHL) ⚠️ requiere confirmación del cliente

**Owners reales extraídos del snapshot** (`clientify.contacts[].owner_name` + `deals[].owner_name`, no de la prosa):

| Owner Clientify (verbatim) | Contactos | Deals | Rol probable | → Usuario GHL |
|---|---|---|---|---|
| `Mauricio Garcia de la Vega Delfin` | 4.776 | 1.292 | **Dueño** | Usuario **activo** (admin) — recibe elevaciones (`06 §5`) |
| `Rodrigo Garcia de la Vega` | 820 | 480 | **Asesor** — Internados, Intercambio, Campamentos (3 calendarios, `07`) | Usuario **activo** + calendario personal conectado (dependencia C1) |
| `Andrés García de la Vega` | 709 | 124 | **Asesor** — los otros 5 programas (5 calendarios, `07`) | Usuario **activo** + calendario personal conectado |
| `Diego García de la Vega Delfín` | 268 | 289 | **Sale del ruteo automático** (trabaja leads orgánicos propios, `01`/`07`) | Usuario **activo pero fuera del ruteo del agente** — preserva sus 289 deals |
| `Max Almonte` | 227 | 1 | **Técnico** — recibe notificaciones de elevación (`06 §5`) | Usuario **activo** |
| `Diego Matus` | 47 | **131** | ✅ **ya no está** (Mauricio 2026-09-03) — su trabajo lo tomó Juan José | ❌ **NO se crea usuario**; sus 47 contactos + 131 deals se **reasignan a Juan José** |
| `Niza Valeriano` | 109 | 1 | ✅ **colaboradora activa** (Mauricio) | Usuario **activo** |
| `Juan José Alfaro` | 12 | 20 | ✅ **colaborador activo** (Mauricio) — **hereda lo de Diego Matus** | Usuario **activo** + reasignación de los 47/131 de Matus |

> ### ✅ Resuelto (Mauricio 2026-09-03): mapeo de owners cerrado
> Había **dos Diegos** distintos en el snapshot. Resolución del cliente: **Diego Matus, Niza y Juan José son colaboradores.** **Diego Matus ya no está** — su trabajo (47 contactos + **131 deals**) lo tomó **Juan José Alfaro**, que sigue activo. **Niza Valeriano** sigue activa. **Diego García de la Vega Delfín** (289 deals) es de la familia, sale del ruteo automático pero se conserva como usuario con sus deals.

**Mapeo final de owners → usuarios GHL:**
- **Activos** (crear como usuario, con email): Mauricio · Rodrigo · Andrés · Max · **Juan José Alfaro** · **Niza Valeriano** · Diego García (fuera del ruteo).
- **Inactivo** (NO crear usuario): **Diego Matus** → su `owner_name` en los 47 contactos + 131 deals se **reescribe a Juan José Alfaro** en el pre-proceso (`06`), antes de cargar.

> **Único pendiente de Mauricio:** los **emails** de los 7 usuarios activos (para crearlos; el `POST /users/` los exige, + `companyId = WbuYAfjKqOU9k7R5t9RL`).

**Nota de género/pronombres:** los nombres no determinan pronombres; en cualquier texto de handoff o notificación usar el neutro hasta que el cliente los aclare.

✅ **Checkpoint:** los 7 usuarios activos **existen en GHL con su email** + Diego Matus reasignado a Juan José en el pre-proceso, **antes** de cargar Contacts/Opportunities (`06 §8.4`).

---

## 2.3 Contact custom fields — estado del bot (source of truth: **Airtable Leads**)

Las 30 columnas de `leads.csv` (verbatim: `id, id_2, Link asesoría enviado, Asistió, Agendan cita, Programa interés, Inicio Deseado, Tipo, Grado Escolar, Nivel Inglés, Creada, ID Clientify, ID Manychat, Nombre Completo, Email, Fuente lead, Folio, fbclid, Estado conversación, Última actividad, Outreach Form Meta enviado, Outreach Form Meta enviado at, Origen, Toques enviados, Ultimo toque at, Ad Name, Platform, Touch 1 programado at, Lead Score, Tipo lead`) se rutean a: campo **nativo**, **custom field**, **Opportunity** (`03`), **se queda en n8n/CAPI** (`05`) o **se descarta**.

**Nativos (NO crear como custom):** `Nombre Completo`→first/last name · `Email`→email · `id/id_2`→phone (canonicalizado, `06`) · `Fuente lead`→**source** (+ custom, ver abajo) · `Creada`→dateAdded (si A2 pasa).

**Custom fields a crear** (folder sugerido: **"Estado del bot"**):

| Campo GHL (key) | Tipo GHL | Valores / enum | Origen Airtable | Nota |
|---|---|---|---|---|
| `programa_interes` | **SINGLE_OPTIONS** | los **8 canónicos** (§2.3.1) | `Programa interés` | remapeo en `06` (doc `01`) |
| `tipo_contacto` | SINGLE_OPTIONS | Padre/Madre · Estudiante | `Tipo` | 2.821 Padre/Madre |
| `grado_escolar` | TEXT | — | `Grado Escolar` | cualificación |
| `nivel_ingles` | SINGLE_OPTIONS | (valores reales del CSV) | `Nivel Inglés` | |
| `inicio_deseado` | TEXT | — | `Inicio Deseado` | |
| `fuente_lead` | TEXT | — | `Fuente lead` | además va a **source** nativo (precedencia `02 §3`) |
| `origen` | SINGLE_OPTIONS | Form Meta · (vacío) | `Origen` | 483 Form Meta |
| `ad_name` | TEXT | — | `Ad Name` | atribución conversación |
| `platform` | SINGLE_OPTIONS | ig · fb | `Platform` | 309 ig / 174 fb |
| `lead_score` | **NUMERICAL** | — | `Lead Score` | ⚠️ **congelado**: el cálculo vive fuera de los 14 wf (`09` decide si se relocaliza a n8n o se migra fijo) |
| `tipo_lead` | SINGLE_OPTIONS | hot · warm · cold | `Tipo lead` | 3.510 cold / 181 warm / 128 hot |
| `estado_conversacion` | SINGLE_OPTIONS | Contestó · Interrumpida · Cita confirmada | `Estado conversación` | ⚠️ **NO etapa** (ortogonal, `03 §5`); `Activa` **no migra** (0 leads) |
| `link_enviado` | **CHECKBOX** | true/false | `Link asesoría enviado` | ⚠️ **NO etapa — es el GATE del rescate** (`09 §3`) |
| `outreach_enviado` | CHECKBOX | true/false | `Outreach Form Meta enviado` | driver de nurturing |
| `outreach_enviado_at` | DATE | — | `Outreach Form Meta enviado at` | |
| `toques_enviados` | NUMERICAL | 0..N | `Toques enviados` | ⚠️ **driver del tope global de 2** (`09 §2`) |
| `ultimo_toque_at` | DATE | — | `Ultimo toque at` | |
| `touch1_programado_at` | DATE | — | `Touch 1 programado at` | ancla de cadencia; 12,6% poblado |
| `ultima_actividad` | DATE | — | `Última actividad` | guard del barrido (`09`); solo 5% poblado |
| `destino_interes` | TEXT | — | (de `Fuente lead`/nota) | **Francia y demás destinos van acá, NO al enum de programa** (`01 §5`) |
| `fecha_alta_original` | DATE | — | `Creada` | **solo si el sandbox A2 falla** (si `dateAdded` acepta histórico, no se crea) |

**Se quedan fuera de Contact:** `Agendan cita`/`Asistió`→**etapa del pipeline operativo** (`03 §5`) · `Folio`/`fbclid`→**n8n/CAPI** (`05`) · `ID Clientify`/`ID Manychat`→**corroboración de merge, se descartan post-import** (`02 §2`).

### 2.3.1 Enum de `programa_interes` — los 8 canónicos (verbatim doc `01`)

Valores del dropdown (el remapeo de las cohortes actuales ocurre en `06`, no acá):

1. **Internados**
2. **Intercambio académico con familias**
3. **Viajes educativos** ⭐ (huérfano, `10`)
4. **Educación superior** ⭐ (huérfano, `10`)
5. **Campamentos de verano**
6. **Cursos de idiomas en el extranjero** ⭐ (huérfano, `10`)
7. **Pathway Alemania**
8. **Gap Year / Estudia y Trabaja**
- *(vacío)* = sin programa aún (el agente lo descubre; **regla dura: nunca se asume por el origen**)

> **Corroborado contra `leads.csv`:** los 8 valores actuales de `Programa interés` (No definido 1.315 · Pathway IA 881 · AA Familiar IA 632 · Boarding School 482 · Boarding IA 437 · Summer Camp IA 42 · Gap Year IA 25 · Automatización - Comentarios 5) remapean a estos 8 canónicos según la tabla de `01 §3`. `Boarding School` + `Boarding IA` → **Internados** (unificar, `01 §2.1`). `Automatización - Comentarios` → **NO es programa** (va a `fuente_lead`/tag).

---

## 2.4 Contact custom fields — identidad/comercial + encuesta (source of truth: **Clientify**)

Los **22 custom fields de Clientify** (verbatim del snapshot) + campos estructurales. La mayoría son una **encuesta de satisfacción post-programa** (histórico, no campos vivos que el bot escriba).

**Estructurales → custom fields** (folder **"Clientify / comercial"**):

| Campo GHL (key) | Tipo | Origen Clientify | Nota |
|---|---|---|---|
| `nombre_estudiante` | TEXT | CF `Nombre del estudiante` | ⚠️ **≠ first_name** (el que escribe es el padre/madre) |
| `contact_type` | TEXT | CF `Contact-Type` | convive con `tipo_contacto` de Airtable |
| `procesos_internos` | TEXT | CF `Procesos Internos` (type 4) | operativo |
| `status_clientify` | TEXT | `status` (in-deal/cold-lead/…) | ciclo comercial; convive con pipeline |
| `canal_origen` | TEXT | `channel` (~15 valores) | migrar 1:1 + campo derivado normalizado (`04 §7`) |
| `medium` | TEXT | `medium` (~5 valores) | idem |
| `rfc` | TEXT | `taxpayer_identification_number` | poco poblado |
| `title` | TEXT | `title` | |
| `gdpr_accept` | CHECKBOX | `gdpr_accept` | **preservar por cumplimiento** |
| `gdpr_acceptance_date` | DATE | `gdpr_acceptance_date` | |
| `gdpr_revoke_date` | DATE | `gdpr_revoke_date` | |
| `disclaimer` | CHECKBOX | `disclaimer` | |

**Nativos (NO custom):** `first_name`/`last_name` · `phones[]`→phone · `emails[]`→email · `owner_name`→owner (§2.2) · `company`→Company (`03 §4`) · `addresses`→address · `birthday`→dateOfBirth · `created/modified/last_contact`→dateAdded/dateUpdated/lastActivity (si A2 pasa; si no, `fecha_alta_original`/`ultima_actividad`).

**Encuesta post-programa → 13 custom fields** (folder **"Encuesta Venttur"**, todos **LARGE_TEXT**, histórico):
`Recomendación del programa` · `Experiencia Global Venttur` · `Mejora Venttur según cliente` · `Información Venttur` · `Atención en extranjero Venttur` · `Acompañamiento Venttur` · `Asesoría Venttur` · `Experiencia Cultural` · `Adaptación` · `Instalaciones` · `Calidad de clases/actividades` · `Experencia General Programa` (sic — respetar la grafía de origen) · `Recomendaciones y comentarios clientes Venttur`.

**6 genéricos — decidir por población** (`04 §8.1`): `Task-Id` · `File` · `Guests` · `Date` · `Timezone` · `Textinput`. Huelen a widget de form/booking. ⚠️ **En `06` medir cuántos están poblados y migrar solo esos**; descartar los vacíos (no crear campos muertos).

**Se descartan (`02 §5`):** `url` (link a Clientify que muere) · `picture_url` (bajo valor).

---

## 2.5 Opportunity custom fields (source of truth: **Clientify deals**)

Lo que no es campo nativo de Opportunity (`03 §3`, `04 §5`). Folder **"Deal / comercial"**:

| Campo GHL (key) | Tipo | Origen deal Clientify | Nota |
|---|---|---|---|
| `cierre_esperado` | DATE | `expected_closed_date` | GHL no tiene nativo fiable |
| `cierre_real` | DATE | `actual_closed_date` | idem |
| `probabilidad` | NUMERICAL | `probability` | GHL deriva de la etapa; se preserva el histórico |
| `moneda` | **SINGLE_OPTIONS** | `currency` (MXN/USD mezclados) | ⚠️ **preserva la moneda por deal** (opción a de A6); el rollup mezcla monedas |
| `status_origen_clientify` | TEXT | `status_desc` (Expired/…) | ⚠️ **solo si el sandbox A3 falla** (si `abandoned` no es seteable, preserva "Expired" acá) |

+ los `custom_fields` propios de cada deal que estén **poblados** (`04 §5`).

**Nativos de Opportunity:** `name` · `monetaryValue` (`amount`) · `pipelineId`/`pipelineStageId` (`03`) · `status` (open/won/lost/**abandoned**) · `contactId` (link al Contact mergeado) · `assignedTo` (owner) · `source`.

---

## 2.6 Tags

### ManyChat (5 tags → Contact tags, verbatim del snapshot)

| Tag (id) | Destino | Nota |
|---|---|---|
| `RESCATE_PROGRAMA_NO_MAPEADO` (`87501935`) | **Contact tag** | con la fusión de "Estudio y Trabajo" (`00 §6`) debería dejar de aplicarse; los 3 huérfanos ya no caen acá (`10`) |
| `LINK_ABANDONADO_FRIO` (`87501917`) | **Contact tag** | terminal del rescate; convive con el estado |
| `seguimiento_agenda` (`77385811`) | **Contact tag** | del seguimiento-agenda (que se consolida, `09`) |
| `seguimiento` (`68459367`) | **Contact tag** | genérico de nurturing |
| `wpp` (`72033971`) | ❌ **se descarta** | huérfano — no lo aplica ningún flow (`00 §6`, `04 §6`) |

### Clientify (freeform → limpieza, `04 §6`)

No hay catálogo cerrado (códigos de programa, "boarding school 25", `<programa>_link_enviado`, URLs). Reglas de migración:
- **Códigos de programa** (`BSG`/`BS`/`HF`…) → redundantes con `programa_interes` → **no migrar como tag** (o normalizar).
- **Tags de link** (`<programa>_link_enviado`) → redundantes con el custom `link_enviado` → **no migrar**.
- **Segmentos/campañas reales** → **Contact tags** limpios.
- **Ruido / URLs** → **descartar**.

> La limpieza fina de los tags freeform de Clientify se ejecuta en el pre-proceso (`06`), no a mano acá — acá se fija la **regla**.

---

## 2.7 Dependencia del sandbox y checkpoints

> ✅ **Sandbox corrido 2026-09-03 (`01`):** resultados que fijan qué campos crear:
> - **A2 FALLÓ por API** (`dateAdded` → 422) → **crear `fecha_alta_original` y `ultima_actividad`** como custom fields (NO son opcionales por la vía API). *(Queda por ver si el CSV import de la UI admite `dateAdded`.)*
> - **A3 PASÓ** (`abandoned` seteable) → **NO crear `status_origen_clientify`**.
> - **A6 PASÓ** (`monetaryValue` crudo) → `moneda` custom viable (opción a).
> - **A4:** el objeto Company es **`/businesses/`** y **no soporta custom fields** (`model=company`→422) → los CF de escuela (`sector`/`rfc`/social) van a **nota** o se descartan, no como custom fields de business.

| Este módulo asume… | Check | Resultado 2026-09-03 |
|---|---|---|
| `dateAdded` histórico seteable | **A2** | ❌ por API → **crear `fecha_alta_original`/`ultima_actividad`** |
| `moneda` por-Opportunity preserva el dato | **A6** | ✅ crudo preservado |
| `abandoned` seteable → no crear `status_origen_clientify` | **A3** | ✅ seteable → **no crear** el custom |
| Business (Company) acepta custom fields | **A4** | ❌ no soporta → CF de escuela a nota/descarte |

✅ **Checkpoints de cierre del módulo:**
- [ ] Sub-cuenta con MXN + TZ México + Allow Duplicate OFF.
- [ ] Usuarios activos creados con email (mapeo de owners **confirmado con el cliente**, incl. los dos Diegos + los históricos).
- [ ] Todos los custom fields de Contact creados (folders "Estado del bot", "Clientify / comercial", "Encuesta Venttur").
- [ ] Enum `programa_interes` con los 8 valores canónicos.
- [ ] Custom fields de Opportunity creados (folder "Deal / comercial").
- [ ] Tags canónicos creados; `wpp` NO creado.
- [ ] Los campos condicionales (`fecha_alta_original`, `status_origen_clientify`) creados **solo** si su check de sandbox falló.

> **Regla del gate:** este módulo **crea la estructura vacía** — no carga datos. La carga (que sí espera los checks A1-A6 en verde) es `06`.

---

*Corroborado contra el snapshot 2026-07-24 (8 owners reales con conteos; 22 CF Clientify + 13 CF ManyChat + 5 tags verbatim) y `leads.csv` (30 columnas; 8 valores de `Programa interés`). 2026-09-03.*
