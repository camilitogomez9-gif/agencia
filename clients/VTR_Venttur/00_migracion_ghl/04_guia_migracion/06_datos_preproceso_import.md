# 06 · Datos — pre-proceso, merge e import a GHL

> ### 🔄 Estado a 2026-09-07 — ✅ IMPORT EJECUTADO Y RECONCILIADO
> **companies 266 · contacts 6.316 · opps 2.295** (0 fallos) · **assignedTo reasignado en 4.736 contacts**. **61 opps duplicadas** (ventanas de kill del resume) **BORRADAS** → **2.299 opps** finales en GHL. `fecha_alta_original` poblado (25/25 en muestra). Verificado por reconciliación vs idmaps + spot-checks.
> **Regla operativa aprendida (incidente 3/9):** NUNCA correr escrituras a GHL en paralelo → 429 en cascada; siempre secuencial + backoff (`_ghl_client.py`).
> **✅ Auditoría de migrabilidad Clientify:** entregable existe (`05_ejecucion/auditoria-migrabilidad-clientify.md`) — falta OK/decisión del cliente antes de apagar Clientify.
> **🟡 Decisión pendiente:** `Lead Score` / `Tipo lead` (cálculo fuera de los 14 workflows) → relocalizar a n8n vs migrar congelados.

> **🔴 Riesgo #1.** Fusiona 3 sistemas con identidades desalineadas en **~8.575 GHL Contacts** deduplicados, remapea el enum de programas, y carga Companies → Contacts → Opportunities. Si la resolución de identidad falla, GHL nace con duplicados y todo downstream hereda el error.
>
> **Para quién:** la agencia. **Prerequisito:** módulo `02` (custom fields + owners confirmados) + `03` (pipelines) + **sandbox A1-A6 en verde** (este es el módulo que ESPERA al sandbox) + **auditoría de migrabilidad Clientify** (§6.3, gate del cliente). **Referencia:** `02_datos_contactos_identidad.md`, `01_taxonomia_programas.md §3`, `03 §3`.
>
> **Estimado:** 8-12 hs. Números corroborados contra `leads.csv` (3.819) + snapshot Clientify (6.968).

---

## 6.1 El problema de identidad (números reales)

| Sistema | Registros | Clave | Estado |
|---|---|---|---|
| **Airtable Leads** | 3.819 | teléfono (`id`=`id_2`, sin `+`) | 2.510 con `521` / 1.229 con `52` → **el quirk MX en los datos** |
| **Clientify** | 6.968 | teléfono E.164 o email | 4.558 con teléfono, **2.410 SIN**; 2.576 con email; **170 con doble variante 52/521** |
| **ManyChat** | subset | subscriber_id + teléfono | transitorio; no aporta identidad nueva |

**FKs de cruce (Airtable):** `ID Clientify` en 1.730 (45%) · `ID Manychat` en 2.907 (76%) · **442 sin ninguna FK** (solo por teléfono).

**Solape por teléfono canónico** (colapsando 521→52): Airtable 3.462 únicos · Clientify ≈4.558 · **intersección 1.855** · solo-Airtable 1.607 · solo-Clientify ≈2.703. → **Universo GHL ≈ 6.165 (por teléfono) + hasta 2.410 (Clientify sin teléfono) ≈ 8.575**.

> Clientify es el **superset** (6.968, CRM comercial completo); Airtable es el **subset** que tocó el bot (3.819). El Contact GHL = **unión deduplicada**. Sin canonicalizar el quirk MX antes de importar, los 1.855 solapados y los 170 de doble-variante **se duplican**.

---

## 6.2 Pre-proceso / ETL (n8n o script) — construir la unión deduplicada

### Paso 1 — Canonicalizar el teléfono (todas las fuentes)
- **MX móvil:** colapsar `+52 1 NNNNNNNNNN` (13díg) y `+52 NNNNNNNNNN` (12díg) a **una forma canónica**. **Recomendado: `+521…`** (WhatsApp-dialable, la que usa la WABA). La colisión 52↔521 se resuelve por el **número nacional de 10 dígitos**.
- **No-MX** (32 US/CA + ~40 de otros países): E.164 tal cual.
- 🔧 **Fix de origen:** el `sessionKey` del agente en el main **no normaliza** 52→521 → hoy hay doble sesión. La canonicalización lo cierra del lado de los datos; el fix en caliente del main va en `07`. **Aplicar ambos juntos** para no partir sesiones entre histórico y nuevo.

### Paso 2 — Remapear `Programa interés` (doc `01 §3`)
Reescribir según el crosswalk (corroborado contra `leads.csv`):

| Valor actual | Conteo | → Canónico |
|---|---|---|
| `Boarding School` + `Boarding IA` | 482+437=919 | **Internados** (unificar) |
| `AA Familiar IA` | 632 | **Intercambio académico con familias** |
| `Pathway IA` | 881 | **Pathway Alemania** |
| `Summer Camp IA` | 42 | **Campamentos de verano** |
| `Gap Year IA` | 25 | **Gap Year / Estudia y Trabaja** |
| `Automatización - Comentarios` | 5 | **(no es programa)** → `fuente_lead`/tag |
| `No definido` / vacío | 1.315 | **(sin programa)** — el agente lo descubre |

Los destinos (Francia, etc.) → `destino_interes` (nota), **nunca** al enum (`01 §5`).

### Paso 3 — Merge por teléfono canónico
Los **1.855** que solapan Airtable∩Clientify colapsan a un Contact. Los **170** Clientify de doble-variante colapsan a uno.

### Paso 4 — Corroborar con las FKs
Donde exista `ID Clientify`/`ID Manychat` en Airtable → **confirmación secundaria** del merge (atrapa mismos leads con formato de teléfono distinto). NO son clave primaria (cobertura 45%/76%).

### Paso 5 — Fallback para los 2.410 Clientify sin teléfono
Match por **email** (2.576 tienen) → luego **nombre + owner** → si no matchea, migrar como Contact **phone-less** (sin canal WA hasta que aporten teléfono).

### Source of truth por dominio (precedencia de campos, `02 §3`)
- **Identidad** (nombre/teléfono/email): **Clientify** (superset); Airtable rellena huecos.
- **Owner/asesor:** **Clientify** (`owner_name`, `02 §2.2`). 🔧 **Normalización en el pre-proceso:** reescribir `owner_name = "Diego Matus"` → **"Juan José Alfaro"** en los 47 contactos + 131 deals (Diego Matus ya no está; su trabajo lo tomó JJ — Mauricio 2026-09-03). No se crea usuario GHL para Diego Matus.
- **Estado del bot** (programa, estado_conversacion, link_enviado, toques, timestamps): **Airtable**.
- **Fuente:** Airtable `Fuente lead` precede; si vacío, Clientify `contact_source`.
- **Comercial** (deals, CF encuesta): Clientify (`03`, `04`).

---

## 6.3 🔴 Gate del cliente — auditoría de migrabilidad de Clientify

**Antes de apagar Clientify**, el cliente exige saber **qué NO se puede pasar** para respaldarlo por su cuenta (`ronda-2 §B2`). Es **entregable de la agencia, no opcional**, y dimensiona automático vs manual.

**No existe migración automática Clientify→GHL.** Auditar y reportar:

| Qué | ¿Migra? | Cómo |
|---|---|---|
| Contactos (6.968) | ✅ | CSV bulk / API (este módulo) |
| Deals (2.338) + pipelines | ✅ | CSV / API a Opportunities (`03`) — buena parte **reconstrucción manual/por lote** |
| Companies (266) | ✅ | CSV / API (`03 §4`) |
| Custom fields (22) | ✅ | como CF (`02 §2.4`) |
| **Historial de conversaciones** | ❌ probable | **el cliente lo respalda por su cuenta** |
| **Adjuntos** (archivos en contactos/deals) | ❌ probable | **respaldo del cliente** |
| **Automatizaciones de Clientify** | ❌ | se reconstruyen (o mueren) en GHL/n8n |

> **Entregable:** un doc corto que liste, por categoría, qué entra por bulk vs manual vs no-migra, para que el cliente respalde lo que no viaja **antes** del cutover. Es **gate de cutover**, no de diseño — la topología de `02`/`03` no cambia según su resultado.

---

## 6.4 Import execution

### Orden de carga (respeta dependencias de vínculo)
**Companies → Contacts → Opportunities** (`02 §8`).

### Idempotencia
- **Upsert por teléfono canónico** (+ email fallback) — re-correr **no duplica** (depende de sandbox **A1**).
- Owners (Rodrigo, Andrés, Mauricio, Max + confirmados) **creados en `02` antes** de la carga → `owner`/`assignedTo` matchean.
- `dateAdded`/`lastActivity`: histórico si **A2** pasa; si no, a `fecha_alta_original`/`ultima_actividad`.
- Deals `Expired`→`abandoned` si **A3** pasa; si no, `lost` + `status_origen_clientify`.
- Moneda: `monetaryValue` + custom `moneda` si **A6** pasa.

### Verificación / reconciliación (post-import)
✅ Chequear conteos contra las cotas del diseño:
- **Contacts:** ≈ 6.165 (por teléfono) + los phone-less que no matchearon por email → **≈8.575 cota superior**. Reportar el número real (baja según cuántos phone-less matcheen).
- **0 duplicados** por teléfono canónico (query de verificación).
- **Opportunities:** 2.338 (± los deals sin Contact resuelto → a revisar).
- **Companies:** 266.
- **programa_interes** remapeado: Internados 919 · Pathway 881 · Intercambio 632 · Campamentos 42 · Gap Year 25 · sin programa 1.320.
- Owners preservados (spot-check de los conteos de `02 §2.2`).

---

## 6.5 Alcance del import — ✅ B3 Opción A (completo, cliente 2026-09-03)

**Todo migra para el 15/9 en una sola pasada.** No hay olas.

| Qué entra al 15/9 | Volumen |
|---|---|
| **Companies** | 266 |
| **Contacts** (unión deduplicada) | ~8.575 |
| **Opportunities** — pipeline operativo del bot (`03 §2`) | — |
| **Opportunities** — los 20 pipelines comerciales (deals 1:1) | 2.338 |

> ⚠️ Con Opción A **no queda nada para una 2ª ola**: la reconstrucción de los 2.338 deals + 266 companies (buena parte **manual**, `§6.3`) tiene que estar **completa y reconciliada antes del cutover**. Es el ítem que más presiona el 15/9 → **arrancar el import en paralelo al sandbox**, no después. Si no llega, abrir con el cliente la conversación de fecha antes del D-3 (`12 §12.1`).

---

## 6.6 Banderas y checkpoints

| Bandera | Estado |
|---|---|
| Forma canónica MX (`+521…`) | decisión de ejecución — lo crítico es **colapsar a una** |
| 2.410 Clientify sin teléfono | cuántos matchean por email define el universo real (6.165→8.575) |
| Owners incl. inactivos con deals | **cerrado en `02 §2.2`** con el cliente |
| `channel`/`medium` fragmentados (~20 valores) | migrar 1:1 + campo derivado normalizado (`04 §7`), no colapsar a ciegas |
| Migrabilidad Clientify | **gate §6.3** — entregable antes de apagar Clientify |
| `Lead Score`/`Tipo lead` | cálculo fuera de los wf → **relocalizar a n8n o migrar congelado** (`09`) |
| 🆕 **Opp duplicada por contacto** | **`OPPORTUNITY_NO_DUPLICATE`** (sandbox) — un contacto con varios deals en un pipeline colisiona → **activar "Allow Duplicate Opportunity" o dedupear antes de cargar los 2.338 deals** |
| Companies = `/businesses/` | endpoint corregido (sandbox A4); no soporta CF de business |
| `dateAdded` no seteable por API | **A2 falló** → fecha de alta a `fecha_alta_original` (probar si el CSV import de la UI lo admite) |

> ✅ **Sandbox 2026-09-03 (`01`):** A1 ✅ (GHL NO normaliza teléfono → canonicalización obligatoria, ya en §6.2) · A3 ✅ · A6 ✅ · B5 ✅ · A2 ❌ (fecha a custom) · A4 corrección (`/businesses/`) · **A5 PARCIAL: query por teléfono ✅ (`POST /contacts/search` con filtro anidado), por custom field ✗ (400)** → el lookup CAPI por teléfono (`09`) va; el filtro por CF del despachador puede necesitar el índice Postgres. · ⚠️ **UA obligatorio** (Cloudflare 1010) en todo HTTP a GHL, incl. los scripts de import de este módulo.

✅ **Checkpoints de cierre:**
- [ ] Pre-proceso corrido: teléfonos canonicalizados + programas remapeados + unión deduplicada construida.
- [ ] Auditoría de migrabilidad Clientify entregada al cliente (qué respaldar).
- [ ] Companies → Contacts → Opportunities cargados en orden, upsert idempotente.
- [ ] Reconciliación de conteos en verde (≈8.575 Contacts, 0 duplicados, remapeo correcto).
- [ ] (B3 = Opción A) Companies + Contacts + los 2.338 deals migrados y reconciliados **antes** del cutover.
- [ ] Airtable Leads congelado (read-only) post-migración.

---

*Corroborado contra `leads.csv` (3.819, quirk 2.510/1.229, remapeo de programas exacto) y el snapshot Clientify (6.968 contactos, 2.410 sin teléfono, 170 doble-variante). 2026-09-03.*
