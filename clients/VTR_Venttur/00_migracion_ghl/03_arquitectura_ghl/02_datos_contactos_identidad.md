# 02 · Datos — Contactos e identidad → GHL Contacts

> **🔴 Riesgo #1.** Este mapping define el schema del Contact que **todo** workflow lee y escribe, y fusiona 3 sistemas con identidades distintas en un solo registro. Si la resolución de identidad falla, GHL nace con duplicados y cada flujo downstream hereda el error. Es el primero que se ataca.
>
> Números corroborados contra `00_inputs/` (2026-08-26), no contra los docs.

---

## 1. El problema de identidad (con números reales)

Hoy el mismo lead vive replicado en 3 sistemas, con **3 identidades desalineadas** unidas solo por el teléfono — y el teléfono está sucio.

| Sistema | Registros | Clave natural | Estado de la clave |
|---|---|---|---|
| **Airtable Leads** | 3.819 | teléfono (`id`=`id_2`, sin `+`) | 2.510 con prefijo `521` / 1.229 con `52` → **el quirk MX en los datos** |
| **Clientify Contacts** | 6.968 | teléfono (`+521…` en E.164) o email | 4.558 con teléfono, **2.410 SIN teléfono**; 2.576 con email; **170 con las dos variantes 52/521 en el mismo registro** |
| **ManyChat subscribers** | ~ (subset) | subscriber_id + teléfono | transitorio; solo aporta estado de canal |

**FKs de cruce en Airtable Leads** (parciales y asimétricas):

- `ID Clientify` presente en **1.730 (45,3%)** · `ID Manychat` en **2.907 (76,1%)**.
- 1.260 tienen ambas · 470 solo Clientify · 1.647 solo ManyChat · **442 sin ninguna FK** (solo se pueden cruzar por teléfono).

**Solape real por teléfono canónico** (colapsando `521`→`52`):

- Airtable 3.462 teléfonos únicos · Clientify ≈4.558 únicos · **intersección solo 1.855**.
- Solo-Airtable 1.607 · solo-Clientify ≈2.703.
- **Universo GHL Contacts ≈ 6.165 (por teléfono) + hasta 2.410 (Clientify sin teléfono) ≈ 8.575** (cotas ±2 según el tratamiento de ~260 teléfonos malformados en Clientify).

> **La consecuencia dura:** Clientify es el **superset** de contactos (6.968, el CRM comercial completo), Airtable Leads es el **subset** que tocó el bot/los forms (3.819). El Contact de GHL = **unión deduplicada**. Sin canonicalizar el quirk MX antes de importar, los 1.855 solapados y los 170 de doble-variante **se duplican**.

---

## 2. Estrategia de merge y dedup

GHL deduplica Contacts por email y/o teléfono, pero **no normaliza el formato del teléfono** (match string-exacto) y el comportamiento depende del setting *Allow Duplicate Contacts*. Con solo 12,6% de Airtable y ~37% de Clientify con email, la mayoría de los ~6.165 merges recae en el teléfono → **la canonicalización previa es obligatoria** y el orden de match del upsert (email vs teléfono) **se valida en una sub-cuenta GHL sandbox antes del import masivo** (riesgo de ejecución #1, ver §9). Orden de resolución:

**Paso 1 — Canonicalizar el teléfono (todas las fuentes).**
- MX móvil: colapsar `+52 1 NNNNNNNNNN` (13díg, forma WhatsApp) y `+52 NNNNNNNNNN` (12díg) a **una sola forma canónica**. Recomendado: conservar la forma **`+521…` (WhatsApp-dialable)** como valor almacenado, porque el canal es WhatsApp y es la que usa la WABA. La colisión 52↔521 se resuelve por el número nacional de 10 dígitos.
- No-MX (32 US/CA + cola de ~40 de otros países): E.164 tal cual.
- 🔧 **Fix de origen:** el `sessionKey` del agente en el main **no normaliza** 52→521 (sí lo hacen outreach/rescate) → hoy hay riesgo de doble sesión. La canonicalización de la migración lo cierra de un lado; el fix en caliente del main es aparte (`06`).

**Paso 2 — Merge por teléfono canónico entre sistemas.** Los 1.855 que solapan Airtable∩Clientify colapsan a un Contact. Los 170 Clientify con doble-variante colapsan a uno.

**Paso 3 — Corroborar con las FKs.** Donde exista `ID Clientify`/`ID Manychat` en Airtable, usarlas como **confirmación secundaria** del merge (atrapan casos donde el teléfono difiere en formato pero es la misma persona). No son la clave primaria porque tienen cobertura parcial (45%/76%).

**Paso 4 — Fallback para los 2.410 Clientify sin teléfono.** Match por **email** (2.576 Clientify tienen email) → luego por **nombre + owner**; si no matchea, migrar como Contact phone-less (GHL lo permite; quedan sin canal WA hasta que aporten teléfono).

**Paso 5 — Resultado:** ≈8.575 GHL Contacts (cota superior), deduplicados. La cifra baja según cuántos phone-less matcheen por email.

> **Caveat (no bloquea el diseño):** no existe migración automática Clientify→GHL. La **auditoría de migrabilidad** (`ronda-2` §B2) dimensiona qué entra por CSV bulk vs manual antes de apagar Clientify. No cambia *qué* se migra ni la topología; es gate de cutover.

---

## 3. Source of truth por dominio de campo

Regla de precedencia cuando el mismo dato existe en más de un sistema:

| Dominio | Fuente autoritativa | Por qué | Relleno de huecos |
|---|---|---|---|
| Identidad (nombre, teléfono, email) | **Clientify** (base CRM) | Es el superset comercial | Airtable `Nombre Completo`/`Email` llenan lo que falte; preferir el más completo |
| Owner / asesor | **Clientify** (`owner_name`) | Airtable no tiene owner | — |
| Estado comercial, deals, notas, survey CF | **Clientify** | Es el sistema de ventas | → `03` (deals), `04` (CF) |
| Estado del bot (Programa interés, Estado conversación, Lead Score, Toques, timestamps) | **Airtable Leads** | El bot escribe ahí | ManyChat no compite |
| Atribución (Folio, fbclid, pixel) | **Airtable/CAPI** | Se queda en n8n | → `05` |
| Fuente / `source` | **Airtable `Fuente lead`** (precede) | más poblado y específico que Clientify | si vacío, Clientify `contact_source` |
| Canal transitorio (`parte1/2/3`, `respuesta_definitiva`, `programa_wpp`) | **ManyChat** → **se descarta** | Efímero; GHL Conversations guarda los mensajes | → `06` |

---

## 4. Traducción — Airtable Leads (30 columnas; `id_2` es dup exacto de `id`) → GHL

Cada columna se rutea a: **Contact** (campo estándar o custom), **Opportunity** (`03`), **se queda en n8n/CAPI** (`05`), o **se descarta**.

| Columna Airtable | Qué es hoy | Destino GHL/n8n | Qué cambia | Nota |
|---|---|---|---|---|
| `id` / `id_2` | teléfono sin `+` (idénticos) | **Contact.phone** (canonicalizado) | pasa a E.164 `+521…`; deja de ser PK textual | clave de merge (§2) |
| `Nombre Completo` | nombre del que escribe | **Contact.first_name + last_name** | split nombre/apellido | 99,7% presente |
| `Email` | email del lead | **Contact.email** | 1:1 | solo 12,6% (cohorte Form Meta) |
| `Programa interés` | programa (LLM/outreach) | **Contact.custom `programa_interes`** (enum de `01`) | remapeo por `01`; unifica Boarding | dropdown en GHL (mejor tipado) |
| `Tipo` | Padre/Madre \| Estudiante | **Contact.custom `tipo_contacto`** | dropdown | 2.821 Padre/Madre |
| `Grado Escolar` | grado del hijo/a | **Contact.custom `grado_escolar`** | 1:1 | de cualificación |
| `Nivel Inglés` | nivel de inglés | **Contact.custom `nivel_ingles`** | 1:1 | |
| `Inicio Deseado` | cuándo quiere iniciar | **Contact.custom `inicio_deseado`** | 1:1 | |
| `Fuente lead` | fuente/campaña | **Contact.source** (precedencia sobre Clientify `contact_source`) + custom `fuente_lead` | GHL tiene `source` nativo | 1.904 vacío; incluye destinos (Francia) → nota |
| `Origen` | Form Meta / vacío | **Contact.custom `origen`** | 1:1 | 483 Form Meta |
| `Ad Name` | anuncio de Meta | **Contact.custom `ad_name`** | 1:1 | atribución conversación |
| `Platform` | ig / fb | **Contact.custom `platform`** | 1:1 | 309 ig / 174 fb |
| `Lead Score` | score numérico | **Contact.custom `lead_score`** | valor histórico | ⚠️ el **cálculo vive fuera del wf** (no localizado); si no se replica en n8n, queda **congelado** al snapshot. Localizar (`09`) |
| `Tipo lead` | hot/warm/cold | **Contact.custom `tipo_lead`** | dropdown (3 valores) | 3510 cold / 181 warm / 128 hot; probablemente deriva de `Lead Score` → mismo congelamiento si no se replica el cálculo |
| `Creada` | fecha de alta | **Contact.dateAdded** *(o custom `fecha_alta_original` si GHL no acepta fecha histórica — validar en sandbox)* | nativo si es seteable | ver §9 |
| `Última actividad` | último inbound (UTC) | **Contact.custom `ultima_actividad`** | también lo refleja Conversations | solo 5% poblado; guard del barrido (`09`) |
| `ID Clientify` | FK 1:1 a Clientify | **se descarta post-merge** | queda `Contact.id` GHL | corroboración de merge (§2) |
| `ID Manychat` | FK 1:1 a ManyChat | **se descarta post-merge** | ManyChat desaparece | corroboración de merge |
| `Folio` | folio CAPI | **se queda en n8n/CAPI** | no es dato de contacto | → `05` (16,7% poblado) |
| `fbclid` | click id de Meta | **se queda en n8n/CAPI** | → `05` | 3,8% |
| `Agendan cita` | ✅ agendó (bool) | **Opportunity (etapa)** | pasa a stage de pipeline | → `03` |
| `Asistió` | asistió a la cita (bool) | **Opportunity (etapa)** | → reporte | → `03` |
| `Estado conversación` | Activa/Contestó/Cita conf./Interrumpida | **Contact custom `estado_conversacion` / tag** (NO etapa lineal) | es ortogonal a la etapa comercial — no colapsar a un stage | → `03` lo resuelve; `Activa` se descarta |
| `Link asesoría enviado` | link enviado (bool) | **Contact custom `link_enviado`** (NO etapa) | es el **GATE que lee el rescate**: si fuera etapa, avanzar a "agendó" lo pisaría y rompería el gate | → `09` |
| `Outreach Form Meta enviado` | bool | **Contact.custom `outreach_enviado`** | driver de nurturing | → `09` |
| `Outreach Form Meta enviado at` | timestamp | **Contact.custom `outreach_enviado_at`** | → `09` | |
| `Toques enviados` | 0..3 | **Contact.custom `toques_enviados`** | tope global 2 (`09`) | driver del tope |
| `Ultimo toque at` | timestamp | **Contact.custom `ultimo_toque_at`** | → `09` | |
| `Touch 1 programado at` | timestamp ancla | **Contact.custom `touch1_programado_at`** | ancla de cadencia | → `09`; 12,6% |

> Los campos de `Programa interés`/`Tipo`/`Nivel Inglés`/etc. se catalogan como custom fields en `04`; acá se fija a qué entidad GHL pertenecen (Contact) y su source-of-truth (Airtable).

---

## 5. Traducción — Clientify Contact (estructural) → GHL Contact

| Campo Clientify | Qué es | Destino GHL | Nota |
|---|---|---|---|
| `id` | PK Clientify | **se descarta post-merge** | queda `Contact.id` GHL; usado como corroboración (`ID Clientify` de Airtable) |
| `first_name` / `last_name` | nombre | **Contact.first_name / last_name** | fuente autoritativa de identidad |
| `phones[]` | 1+ teléfonos (`+521…` y/o `+52…`) | **Contact.phone** (canonicalizado) | 170 registros con doble variante → colapsan; type/unsubscribed → nota |
| `emails[]` | 1+ emails | **Contact.email** (+ additional emails) | fallback de merge para phone-less |
| `owner` / `owner_name` | asesor dueño | **Contact.owner (assigned user)** | mapear owners Clientify → usuarios GHL |
| `status` | in-deal/cold-lead/… | **Contact.custom `status_clientify`** | estado de ciclo comercial; convive con pipeline |
| `channel` | webform/inbox_messenger/manual/… (fragmentado) | **Contact.custom `canal_origen`** | ~15 valores distintos; normalizar a lista corta |
| `medium` | inbox/reuniones/… | **Contact.custom `medium`** | idem |
| `contact_source` | Otros/Referencias/Facebook (casi todo null) | **Contact.source** solo si Airtable `Fuente lead` está vacío (precedencia §3) | mayormente vacío |
| `tags[]` | tags freeform (ej. "boarding school 25", URLs) | **Contact.tags** | → catálogo y limpieza en `04` |
| `company` | empresa vinculada | **Contact.company** + Companies | 266 companies → `03` |
| `custom_fields` | los 22 CF de encuesta Venttur | **Contact custom fields** | → `04` |
| `created` / `modified` / `last_contact` | fechas | **Contact.dateAdded / dateUpdated / lastActivity** *(validar en sandbox si aceptan valores históricos; si no, `created`→custom `fecha_alta_original`, `last_contact`→custom `ultima_actividad`)* | ver §9 |
| `addresses` | direcciones | **Contact.address** | 1:1 si presente |
| `birthday` | cumpleaños | **Contact.dateOfBirth** | 1:1 |
| `title` | título | **Contact.custom `title`** | |
| `taxpayer_identification_number` | RFC/ID fiscal | **Contact.custom `rfc`** | poco poblado |
| `picture_url` | foto | **Contact.custom** o descarta | bajo valor |
| `gdpr_accept` / `gdpr_acceptance_date` / `gdpr_revoke_date` | consentimiento | **Contact.custom `gdpr_*`** | preservar por cumplimiento |
| `disclaimer` | flag legal | **Contact.custom** | |
| `url` | URL del contacto en Clientify | **se descarta** | link a sistema que muere |

---

## 6. ManyChat subscriber → GHL (mayormente se descarta)

ManyChat no es una fuente de identidad autónoma: su subscriber replica al lead que ya vive en Airtable/Clientify. Sus 13 custom fields son en su mayoría **transitorios de canal** y se descartan; los pocos con dato de negocio ya viven en Airtable.

| Custom field ManyChat | Destino | Nota |
|---|---|---|
| `parte1` / `parte2` / `parte3` / `respuesta_definitiva` | **se descartan** | mecanismo de multi-burbuja; se rehace en `06` |
| `agendan_cita` | **ya vive en Airtable** → Opportunity | duplica; no migra desde ManyChat |
| `programa_wpp` / `programa_rescate` / `programa_interes` | **ya vive en Airtable** `Programa interés` | no migra desde ManyChat |
| `ctwa_clid` / `ad_source_id` | **se queda en n8n/CAPI** | atribución → `05` |
| `mensaje_inicial_asesoria` / `mensaje_link_asesoria` | **se rehace en `07`** (confirmación) | efímero |
| `wpp` | **se descarta** | huérfano |

El detalle completo (tipos, ids) está en `04`. Aquí basta con: **ninguna identidad nueva entra desde ManyChat**; sus subs se resuelven contra el Contact ya mergeado por teléfono.

---

## 7. Colapso del triple-write y de la doble alta (descartes)

- **Triple-write** (Airtable + Clientify + Supabase con 3 identidades) → **un solo Contact GHL**. La memoria conversacional sigue en Supabase (no es identidad); las FKs desaparecen.
- **Doble alta de contacto** (nodo determinístico `Crear primer contacto` con el nombre del perfil ManyChat **+** tool agéntica `crear_contacto` con el nombre que el lead escribe) → **una sola alta en GHL**. En destino: GHL crea/upsertea el Contact al primer inbound (Contact Reply); el agente solo **enriquece** (nombre real, programa) vía update, nunca crea un segundo registro. Elimina el pisado de nombres.

---

## 8. Mecánica de migración (nivel diseño)

1. **Pre-proceso (n8n o script):** exportar Clientify (contacts) + Airtable Leads; canonicalizar teléfonos; remapear `Programa interés` por `01`; construir la unión deduplicada (§2).
2. **Orden de carga:** Companies (`03`) → Contacts (este doc) → Opportunities (`03`). Respeta dependencias de vínculo.
3. **Idempotencia:** upsert por teléfono canónico (+ email fallback). Re-correr no duplica.
4. **Owners:** crear/mapear los usuarios GHL (Rodrigo, Andrés, Mauricio, Niza…) antes de la carga para preservar `owner`.
5. **No viaja automático:** historial de conversaciones, adjuntos y automatizaciones de Clientify (la auditoría de migrabilidad los dimensiona; el cliente los respalda por su cuenta).

---

## 9. Banderas de este mapping

1. **Forma canónica del teléfono MX** (`+521…` vs `+52…`): decisión de ejecución. Lo crítico es **colapsar a una** antes de importar. Recomendado `+521…` (WhatsApp).
2. **2.410 Clientify sin teléfono:** cuántos matchean por email define el tamaño real del universo (6.165 → 8.575). Se resuelve al correr el pre-proceso.
3. **Owners Clientify → usuarios GHL:** hay que enumerar los owners reales (aparecen "Mauricio Garcia de la Vega Delfin", "Niza Valeriano", etc.) y decidir el mapeo, incluida la gente que ya no está.
4. **`channel`/`medium` de Clientify muy fragmentados** (20+ valores): normalizar a una lista corta en `04` en vez de migrar el ruido 1:1.
5. **Migrabilidad Clientify** (caveat): gate de cutover, no de diseño. La topología de este mapping no cambia según su resultado.
6. **Asunciones de plataforma GHL a validar en sandbox** (riesgo de ejecución): (a) el **orden de match del upsert** de Contacts (email vs teléfono) + comportamiento con *Allow Duplicate Contacts* — GHL no normaliza formato de teléfono; (b) si `dateAdded`/`dateUpdated`/`lastActivity` **aceptan valores históricos** o los estampa la plataforma al importar (si no, van a custom fields `fecha_alta_original`/`ultima_actividad`). Probar **antes** del import masivo.
7. **Cálculo de `Lead Score` / `Tipo lead`:** vive fuera de los 14 workflows y no está localizado. Decisión pendiente: **relocalizarlo y replicarlo en n8n** (n8n-first) o migrar score/tipo como **valores históricos congelados** que dejan de actualizarse. → `09`.

---

*Corroborado contra `leads.csv` (3.819) y el snapshot Clientify (6.968 contactos) en `00_inputs/`. 2026-08-26.*
