# Registro de ejecución — Etapa 5 (VTR → GHL)

> Log vivo de la ejecución del plan `planes/vtr-ghl-ejecucion-etapa5-2026-09-03.md`, fase por fase.
> Cada fase: qué se hizo (real) + verificación + bloqueantes **registrados** (no detienen el avance).
> Arranque: 2026-09-03. Location GHL: `7aXb4JCKsWV5nUyBXeSF` ("Venttur"). n8n: `[TU-INSTANCIA-N8N]`.

## 🔴 RETOMAR MAÑANA (2026-09-04) — leer esto primero

**Dónde quedamos (todo guardado e idempotente, cero pérdida):**
- Companies **266 ✅** · Contacts **6.316 ✅** (idmap 9.040 keys) · **Opps 1.250/2.338** · Reasignación de owners **1.800** hecha.
- **Bloqueante: cap diario de API GHL agotado (B-12)** — `X-RateLimit-Daily-Remaining: 0/10.000` al 2026-09-03 22:52 UTC. Resetea en ~24h.
- Fase 4 **increment 1 ✅** (staging `[Venttur] GHL staging (Telegram test)` `3sLd7KY3o8I7NvXi`, activo, agente responde por Telegram con memoria; ambos nodos en el bot "Venttur").

**Cuándo probar mañana:** desde **~10-11 AM (hora UY/AR)**. El resume **chequea el cap solo**: si todavía no reseteó, aborta sin hacer nada → reintentar a la tarde (después de ~17h ya está seguro, sea reset a medianoche UTC o ventana rodante de 24h).

**Pasos para retomar (en orden, SECUENCIAL — nunca en paralelo):**
1. `cd clients/VTR_Venttur/00_migracion_ghl/05_ejecucion/scripts`
2. `python3 resume-import.py --check-only` → ver `X-RateLimit-Daily-Remaining`. Si > 5 → seguir; si 0 → esperar.
3. `python3 resume-import.py` → corre **opps (resume desde 1.250)** + **reasignación (resume desde 1.800)**, lento (0.5s), guarda cada 25/50. Idempotente.
4. **Reconciliación:** verificar en GHL — Opps ≈ 2.338 − (deals sin contacto ~43), 0 duplicados por `deal_id`, Companies 266, Contacts ~6.316, owners preservados. ⚠️ Chequear que las opps no pasen de ~2.295 (si hay más, hubo ventana de duplicados del run viejo → dedupear por atributos).
5. **Fase 4 increments 2-6** (`fase4-build-design.md`): context builder gap#1 (lee Contact GHL) → sessionKey MX 52→521 → tools `crear_contacto`/`elevar`→GHL → send GHL free-form → despachador/audio/CAPI/confirmación.

**Deps del usuario abiertas (no bloquean el resume del import):**
- **B-13:** el bot Telegram VTR ya está bindeado y probado ✅ (pero el usuario notó "pila de cosas que ajustar" en el agente por Telegram → afinar en los increments 2-6).
- **Owners Rodrigo/Andrés/Max:** ya en la sub-cuenta (B-11 ✅) → la reasignación de mañana los cubre.
- Pendiente lejano: WABA/número (Fase 5, al final), C1 disponibilidad compartida, textos de los 3 huérfanos.

---

## ✅ Resoluciones del usuario (2026-09-03)

- **B-01 RESUELTO:** la sub-cuenta `7aXb4JCKsWV5nUyBXeSF` **es la de producción**. Se construye in-place.
- **B-02 RESUELTO:** `allowDuplicateOpportunity = ON` (verificado por read-back: `True`).
- **⚠️ CORRECCIÓN de supuesto (2026-09-03):** el doc `02 §2.2` asumía "GHL cobra por asiento de usuario" — **es FALSO.** GHL incluye **usuarios ilimitados en todos los planes** (tarifa plana a nivel agencia: Starter US$97 / Unlimited US$297 / Agency Pro US$497). Crear usuarios **no cuesta extra**. La decisión de owners deja de ser de costo y pasa a ser sólo **"¿esta persona necesita login propio en GHL, o alcanza con preservar sus deals como dato?"**. Fuentes: getautomized.com/gohighlevel-pricing, ghlcentral.com/gohighlevel-pricing.
- **B-03 RESUELTO con workaround (usuarios NO imprescindibles para el import):** el `assignedTo` **no** se setea en el import; el owner real se preserva en el CF **`owner_clientify`** (contact + opportunity) → sin crear logins ni disparar emails de invitación autónomamente (el motivo ya **no es costo** —ver corrección arriba— sino no dar acceso a la cuenta a gente inactiva/desconocida sin OK). Los usuarios se crean **solo en Fase 5** (Rodrigo/Andrés los exige el calendario; Max puede recibir elevaciones por Telegram/email sin asiento). Cuando existan, un script de reasignación mapea `owner_clientify` → `assignedTo` por email.
  - **Qué era "lo dudoso" de los owners** (8 reales, verificados contra el snapshot): 4 claros (**Mauricio** admin ya existe · **Rodrigo** asesor · **Andrés** asesor · **Max** técnico). Los 4 a decidir: **Diego García** (`dgarcia@`, 289 deals) es familia y asesor, **ya fuera del ruteo** por decisión del cliente — lo único abierto es si le pagan asiento o se reasignan sus deals; **Diego Matus** (`dmatus@`, **131 deals**) es un **segundo Diego, apellido y mail distintos, que ningún doc de Etapa 1-3 identificó** — hay que preguntar quién es; **Juan José Alfaro** (`jalfaro@`, 20 deals) y **Niza Valeriano** (`nvaleriano@`, 1 deal, 109 contactos) parecen históricos/inactivos. La duda para los 4 es la misma: **¿asiento activo (persona que sigue operando) o se preservan sus deals sin asiento?** Con el workaround **esto ya NO bloquea el import** — se resuelve cuando el cliente conteste y se reasigna.
- **B-04 RESUELTO:** import autorizado → ejecutándose (companies → contacts → opportunities, idempotente).
- **B-05 (canal):** WABA al final, después de los tests. **Los tests se harán por Telegram** (patrón HPF: Telegram Trigger en n8n + normalizar el payload para replicar el Contact Reply de GHL) → **desbloquea el build+test de la Fase 4 sin depender de la WABA.**
- **B-06 RESUELTO:** tope-2 + prioridad, `Cualificado` (queda en el pipeline operativo), y fallback 1-cal-por-asesor (si C1 falla) — **todos aceptados.**

---

## 🚧 Bloqueantes registrados (vivos — revisar antes de las fases que indican)

| # | Bloqueante | Tipo | Bloquea | Estado |
|---|---|---|---|---|
| B-01 | **¿La sub-cuenta `7aXb4JCKsWV5nUyBXeSF` es la de producción?** La location se llama "Venttur" (no "sandbox"), tiene a Mauricio como **admin real** y currency/TZ MX ya configurados → **parece la de producción**. Se ejecuta in-place per default del plan. | 🔶 decisión usuario/cliente | confirmación conceptual (no frena escritura reversible de estructura) | abierto |
| B-02 | `allowDuplicateOpportunity = OFF` → hay que ponerlo **ON** (toggle UI, no API) antes de importar los 2.338 deals (`OPPORTUNITY_NO_DUPLICATE`). | 🛑 toggle de cuenta | FASE 3 (deals) | abierto |
| B-03 | **Usuarios GHL** (crear Rodrigo/Andrés/Max + decidir los 4 dudosos) → `POST /users/` envía invitación por email a personal real + cobra asiento. | 🛑 outward-facing + 🔶 mapeo owners | FASE 1.7 + FASE 3 (`assignedTo`) | abierto |
| B-04 | **Import masivo de contactos/deals reales** (~8.575 + 2.338). | 🛑 irreversible/masivo | FASE 3 | abierto (espera OK explícito) |
| B-05 | **Canal vivo / WABA** (portabilidad, envío WhatsApp real, tests B1-B4). | 🛑 canal vivo + terceros | FASE 5 | abierto |
| B-06 | Decisiones de cliente 🔶: tope-2 + prioridad · "Cualificado lo escribe el agente" · fallback 1-cal-por-asesor (si C1 falla). | 🔶 cliente | FASE 1 (pipeline) / FASE 4 / FASE 5 | abierto |
| B-07 | Gates de terceros: portabilidad WABA (deadline 1/9 vencido) · aprobación templates Meta (24-72h) · auditoría migrabilidad Clientify · assets de los 3 huérfanos. | 🔶 terceros | FASE 5 / cutover | abierto |
| B-08 | **Orden de stages de los pipelines comerciales** no está en el snapshot → se creó con el orden narrativo de `03`; confirmar/reordenar en la UI de Clientify (drag, reversible). | 🔶 dato externo | FASE 1.4 (position) | mitigado (orden razonable puesto) |
| B-09 | **Viajes educativos** (huérfano 100% nuevo) necesita un **pipeline comercial nuevo** cuyas etapas NO existen en el snapshot → no se inventan (clonar un `Operativo *` o definir con comercial). | 🔶 cliente/comercial | FASE 1/3 (pipeline) | abierto |
| B-10 | **Calendarios** — un calendario GHL funcional exige team member (usuario) + el modelo de disponibilidad compartida depende de **C1** (manual). Spec listo (`spec/calendarios.json`); creación en FASE 5. Ahora **desbloqueado parcialmente** (Andrés-owned calendars esperan B-11; los de Rodrigo también). | 🛑 depende de B-11 + C1 | FASE 5 | abierto (spec listo) |
| B-11 | ~~Rodrigo/Andrés/Max no estaban en la sub-cuenta~~ | ✅ **RESUELTO 2026-09-03** | — | el usuario los agregó desde el UI de agencia; ids en `usuarios-idmap.json` (rgarcia=`IaSkyQuhbjGdwNyXg1VD`, agarcia=`4VtbDVSjnoHm5125qa8I`, malmonte=`rlxMWsDRGCwJdhY6HkrU`). Reasignación ahora cubre los 8 owners. Calendarios de Rodrigo/Andrés desbloqueados (falta solo C1) |
| B-13 | **Bot de Telegram VTR dedicado** para testear el staging main (increment 1). Un bot = un webhook → no reusar el compartido. Usuario: BotFather → token → credencial n8n → bindear en los 2 nodos Telegram del workflow `3sLd7KY3o8I7NvXi` → activar. | 🟡 dep usuario | testear Fase 4 increment 1 | abierto |
| B-12 | 🔴 **Cap diario de API GHL AGOTADO** — `X-RateLimit-Daily-Remaining: 0` (límite **10.000 req/día**, burst 25/10s). Consumido por los retry storms del run en paralelo. **No se libera hasta el reset diario (horas).** Todo guardado e idempotente → resume trivial: `python3 scripts/resume-import.py` (chequea el cap, corre opps + reasignación **secuencial**). Falta: opps ~1.088 + reasignación ~3.400 ≈ 4.500 req (entra en un día de budget). | 🔴 cap externo GHL | reanudar import (opps + reasignación) | **abierto — esperar reset** |

---

## FASE 0 — Verificación idempotente + snapshot ✅ COMPLETA (2026-09-03)

**Ejecutado (read-only, nada escrito en GHL/n8n):**

- ✅ **PIT + scopes** — `GET /locations/7aXb4JCKsWV5nUyBXeSF` → **HTTP 200**. Location **"Venttur"**, `companyId WbuYAfjKqOU9k7R5t9RL`, country **MX**, timezone **America/Mexico_City**, currency **MXN**, `allowDuplicateContact = OFF` ✅ (precondición del merge ya satisfecha).
- ✅ **n8n API** — `GET /api/v1/workflows` → **HTTP 200**, 496 workflows en la instancia. **14 workflows VTR exportados** (JSON completo) a `snapshots/n8n-vivo-2026-09-03/` + 2 extras (data export runner, "Cortar para resumen" OUTDATED).
  - ⚠️ **El main vivo `k3aivKSP67S97IHn` "[Venttur]" tiene 39 nodos** (el export del repo `wf-venttur-main.json` tenía 37) → confirma "el repo va detrás del vivo". La Fase 4 se basa en este export fresco.
  - Mapa id→alias de los 14 en `snapshots/n8n-vivo-2026-09-03/_index-vtr.json`.
- ✅ **Snapshot del estado GHL inicial** (`snapshots/ghl-estado-inicial-2026-09-03/`), confirmando de paso los paths 🔍 (todos HTTP 200):

| Objeto | Endpoint confirmado | Estado inicial |
|---|---|---|
| customFields (contact/opp) | `GET /locations/{loc}/customFields?model=contact\|opportunity` | **0 / 0** (limpio) |
| customValues | `GET /locations/{loc}/customValues` | 0 |
| tags | `GET /locations/{loc}/tags` | 3 (samples GHL: `follow-up`, `high priority`, `warm lead`) |
| pipelines | `GET /opportunities/pipelines?locationId=` | 1 (sample GHL `Marketing Pipeline`) |
| calendars / groups | `GET /calendars/` · `GET /calendars/groups` | 0 / 0 |
| users | `GET /users/?locationId=` | 1 (**Mauricio** `administracion@venttur.com`, role **admin** — ya existe, no re-crear) |
| businesses | `GET /businesses/?locationId=` | 3 (samples GHL `(Example) …`) |

- ✅ **Artefactos de juguete ZZSBX/zzz: ya no están** (0 custom fields; contactos toy → HTTP 400; sin "ZZSBX Escuela"). Lo único pre-existente son **datos de ejemplo de GHL** (3 tags sample, 1 pipeline sample, 3 businesses `(Example)`), **inocuos y sin colisión** con los nombres target → limpieza opcional, no bloqueante.

**Verificación:** todos los `GET` en 200; snapshots escritos a disco; idempotencia de Fase 1 asegurada (check-before-create contra estos snapshots).

**Salidas:** `scripts/_ghl_client.py`, `scripts/snapshot-ghl-estado.py`, `scripts/snapshot-n8n-vtr.py`, `snapshots/ghl-estado-inicial-2026-09-03/`, `snapshots/n8n-vivo-2026-09-03/`.

**Blocker nuevo:** B-01 (sandbox→prod, conceptual — no frena la estructura reversible).

---

## FASE 2 — Pre-proceso / ETL ✅ COMPLETA (2026-09-03)

**Ejecutado local (0 escrituras a GHL):** `scripts/etl-preproceso.py` sobre `leads.csv` (3.819) + snapshot Clientify (6.968/2.338/266). Corrobora el diseño **con precisión**:

| Métrica | ETL real | Cota diseño | ✓ |
|---|---|---|---|
| Remapeo programas | Internados **919** · Pathway **881** · Intercambio **632** · Campamentos **42** · Gap Year **25** · sin-prog **1.320** | idénticos | ✅ exacto |
| Deals por estado | Expired **1.875** · Lost **381** · Open **50** · Won **32** | idénticos | ✅ exacto |
| Moneda | MXN 2.127 · USD 211 (mixta) | mixta | ✅ (A6) |
| Universo GHL Contacts | 6.086 por tel + 2.467 phone-less = **8.553** | ≈8.575 | ✅ en rango |
| Merge Airtable∩Clientify | 1.844 (solo-AT 1.590 · solo-CL 2.652) | 1.855/1.607/2.703 | ✅ ±tol |
| Dedup en salida | **0 canónicos duplicados** | 0 | ✅ |
| **`OPPORTUNITY_NO_DUPLICATE`** | **38 contactos / 85 deals** colisionan por contacto+pipeline | — | → B-02 |
| Valores de programa NO mapeados | **0** (crosswalk cubre todo) | — | ✅ |

- **6 CF genéricos — población medida** (input para Fase 1.1): `Timezone` **1.024** (crear) · Textinput 72 · Guests 54 · Date 45 · File 24 · Task-Id 10.
- **Salidas:** `salida-etl/contacts.jsonl` (8.525) · `opportunities.jsonl` (2.338) · `companies.jsonl` (266) · `reporte-conteos-2026-09-03.md`.
- **Entregable del gate:** `auditoria-migrabilidad-clientify.md` (qué migra bulk/API vs manual vs no-migra) — listo para el cliente.

**Verificación:** conteos re-derivados del sistema real coinciden con las cotas; 0 duplicados; remapeo sin valores huérfanos.

**Sin bloqueantes nuevos.** Confirma B-02 (38/85 opps colisionan → `Allow Duplicate Opportunity` ON antes de Fase 3).

---

## FASE 1 — Estructura GHL por API 🟢 PARCIAL (estructura reversible creada; users/calendarios gated)

**Config base:** ✅ ya estaba correcta en la sub-cuenta (currency **MXN**, TZ **America/Mexico_City**, `allowDuplicateContact = OFF`). No hubo que togglear nada.

### ✅ 1.1/1.2 Custom fields — 56 creados, read-back verificado
- **52 contact + 4 opportunity**, todos con dataType correcto (spot-check de picklists: `programa_interes` 8 canónicos, `platform` [ig,fb], `moneda` [MXN,USD]).
- Idempotencia probada (re-run: 51 skip + 1 create).
- 1 ajuste: **`Timezone` colisiona con campo estándar GHL** → preservado como `clientify_timezone` (TEXT).
- **NO creados** (correcto): `status_origen_clientify` (A3 pasó), CF sobre business (A4).
- idmap: `spec/custom-fields-idmap.json` (name→id/fieldKey) — para Fase 3.

### ✅ 1.3 Tags — 4 canónicos creados
`RESCATE_PROGRAMA_NO_MAPEADO`, `LINK_ABANDONADO_FRIO`, `seguimiento_agenda`, `seguimiento` (GHL los guarda en minúscula). `wpp` **NO** creado. idmap: `spec/tags-idmap.json`.

### ✅ 1.4 Pipelines — 20 creados (operativo del bot + 19 comerciales), read-back N/N
- **`OP · Bot Venttur`** (10 stages; `Cualificado` provisional, B-06).
- **19 comerciales verbatim** (`«sin pipeline»`+`Por defecto` → `Sin asignar / Default`). **Validación automática: todos los stages coinciden verbatim con el snapshot** ✅. 5 legacy marcados.
- ⚠️ Orden de stages = narrativo de `03` (B-08: confirmar en Clientify UI).
- idmap: `spec/pipelines-idmap.json` (pipelineId + stageId por nombre) — para Fase 3.

### ⏸️ 1.5 Calendarios — DIFERIDO (spec listo `spec/calendarios.json`)
Un calendario funcional exige team member (usuario, B-03) y el modelo de disponibilidad compartida depende de C1 (manual). Crear shells name-only ahora sería premat­uro (C1 podría cambiar 8→1-por-asesor). → **B-10**, se crea en FASE 5.

### ⏸️ 1.6 Custom values — DIFERIDO
Los concretos (links de booking por programa) dependen de los calendarios (B-10). Se crean con los calendarios / el prompt del agente (Fase 4/5).

### ✅/🛑 1.7 Usuarios — parcial (cliente autorizó "crear todos menos Diego Matus", 2026-09-03)
- **Creados** (invitación enviada): **Diego García** (`Y1cWtQ0KoVhP9U1iD7MV`), **Juan José Alfaro** (`6CjRtzsyf22fVa5MPDMa`), **Niza Valeriano** (`IXGCCUCvrY7DNm4wFclF`). **Mauricio** ya existía (admin).
- **Diego Matus: NO creado** (ya no está); sus 131 deals + contactos → **Juan José Alfaro** (remap en `usuarios-idmap.json`: `dmatus@`/"Diego Matus" → `6CjRtzsyf22fVa5MPDMa`).
- **Rodrigo/Andrés/Max: 🛑 B-11** — ya existen a nivel agencia pero no en esta sub-cuenta; el PIT no puede agregarlos (requiere UI de agencia). Sus records quedan con `owner_clientify`.
- **`assignedTo`:** cableado a las opps (por `owner_name` → userId) y reasignable en contacts (`reasignar-owners.py`) para los 4 owners resolubles (Mauricio, Diego García, Juan José+Matus, Niza). Cobertura estimada ~5.200 contactos; ~1.740 (Rodrigo/Andrés/Max) esperan B-11.

**Verificación FASE 1:** custom fields + tags + pipelines existen con read-back correcto e idempotencia probada. Estructura de datos lista para Fase 3 (idmaps escritos). Lo gated (users, calendarios, custom values) queda registrado, no frena.

**Blockers nuevos:** B-09 (pipeline comercial de Viajes educativos), B-10 (calendarios).

---

## ⚠️ Incidente rate-limit (2026-09-03) — corregido

**Qué pasó:** corrí **opportunities + reasignación de contacts EN PARALELO** → duplicó el rate de requests a GHL → **429 Too Many Requests** en cascada. El retry del cliente reintentaba cada 429 (backoff) → todo se arrastró ~1.5h, 245 opps fallaron, y el PIT quedó **throttled account-wide** (hasta un `GET /locations` daba 429).

**Causa raíz:** dos jobs concurrentes + `sleep 0.06s` (~5 req/s combinado) + retry storms superaron el límite de GHL (burst 100/10s + cap sostenido).

**Fix aplicado:**
- **Nunca correr jobs de escritura en paralelo** — siempre **secuencial, solo**.
- Base rate **0.06s → 0.35s** (contacts/opps) / 0.25s (reasignación).
- `_ghl_client`: 429 respeta `Retry-After` + backoff exponencial (hasta 45s, 6 reintentos).
- idmaps se guardan **cada 25/50** (no cada 250) → un kill pierde ≤25 (ventana mínima).
- Espera de cooldown del throttle antes de reanudar.

**Estado al momento del kill:** companies 266 ✅ · contacts 6.316 ✅ · **opps 1.250 creados** (en `deal-idmap`, se reanuda desde ahí) · reasignación 1.800 (idempotente, se reanuda). Sin pérdida de datos — todo idempotente.

---

## FASE 3 — Import de datos 🟡 PREPARADO + VALIDADO (masivo 🛑 gated)

**Scripts listos** (`scripts/import-datos.py`, idempotente, `--dry-run` por defecto, `--apply` para escribir). **Dry-run valida los payloads contra los idmaps reales — 0 escrituras:**

| Stage | Dry-run | Resultado |
|---|---|---|
| **companies** | 266 | endpoint `/businesses/`, sin CF (A4). assignedTo pendiente de user-idmap (B-03). |
| **contacts** | 8.525 | 6.058 con teléfono · **8.525/8.525 con ≥1 customField** (IDs resueltos vía idmap) · payloads bien formados (phone canónico, valores mapeados, CHECKBOX→['true'], estado_conversacion normalizado). assignedTo pendiente (B-03). |
| **opportunities** | 2.338 | **✅ 2.338/2.338 resuelven pipeline+stage limpio (0 problemas)** · status GHL: open 50 · abandoned 1.875 · lost 381 · won 32 · moneda como custom. assignedTo pendiente (B-03). |

**Verificación:** el plan de import está validado end-to-end contra la estructura real creada en Fase 1 — lo único sin resolver es `assignedTo` (espera los usuarios, B-03).

**🛑 NO ejecutado el masivo.** Gates duros antes de `--apply`: **(1)** usuarios creados → user-idmap (B-03) · **(2)** `Allow Duplicate Opportunity` ON (B-02) · **(3)** OK explícito del usuario para el masivo (B-04). Protocolo: `--apply --limit 5` (lote de prueba + read-back) → recién el masivo.

---

## FASE 4 — Workflows n8n nuevos (staging) 🟢 EN CURSO (build por Telegram, arrancado 2026-09-03)

### ✅ Increment 1 construido + verificado — loop testeable SIN GHL
**Workflow staging `3sLd7KY3o8I7NvXi` · `[Venttur] GHL staging (Telegram test)`** (INACTIVO, 6 nodos), creado por n8n API **sin tocar ningún workflow vivo**. `Telegram Trigger → Normalizar payload → Agente IA WPP → Enviar Telegram`, reusando **gpt-4o + system prompt 46.868 chars + Postgres memory** del vivo (creds `ibkhdCMyhr3yqDQk` / `ihpvM7nYMdLCwWDP`). Verificado: prompt intacto, conexiones ai_languageModel/ai_memory/main OK, Telegram Trigger **con webhookId** (gotcha HPF). Generador: `scripts/gen-staging-main.py` (idempotente). Diseño completo + roadmap de incrementos: `fase4-build-design.md`.
- **Para testear (B-13):** falta un **bot de Telegram VTR dedicado** (BotFather → credencial n8n → bindear en los 2 nodos → activar). No se reusa el bot compartido (un bot = un webhook).
- **Increments 2-6 (context builder gap#1, sessionKey MX, tools→GHL, send GHL, despachador/audio/CAPI/confirmación):** varios tocan GHL → esperan el reset del cap (B-12). Ver `fase4-build-design.md`.

---

### Registro previo (prerequisitos, siguen válidos)

**Lo que ya está listo (desbloqueado):**
- ✅ **Re-export fresco de los 14 workflows VTR vivos** (Fase 0) — el prerequisito "re-exportar el main vivo antes de tocar". Main real = `k3aivKSP67S97IHn` "[Venttur]" **39 nodos** (repo tenía 37).
- ✅ **IDs de la estructura GHL** (custom fields, pipelines, tags) disponibles en los idmaps → el cableado ID-dependiente ya tiene contra qué apuntar.
- ✅ **A5 por teléfono confirmado** (`POST /contacts/search`) para el context-builder y el lookup CAPI; **B5** (`dnd:true`) para el handoff.

**Bloqueante real (registrado, no resoluble por mí ahora):** el **núcleo del canal** (entrada Contact Reply → n8n, envío free-form/template) depende de **B1/B2/B3** — checks de sandbox que exigen **inbound de WhatsApp real + un número de test** (B-05). No se puede validar sin el canal vivo. Además **A5 por custom field falló (400)** → el cron del despachador usa el índice Postgres (fallback ya diseñado). Construir los ~40 nodos del main reconstruido / despachador / CAPI-clone **a ciegas** (sin poder ejecutarlos contra GHL) produciría artefactos no testeados: es un **build enfocado que se hace cuando B1/B2 estén verdes**, iterando con ejecuciones reales. → **queda registrado**, con la estructura y los exports listos para arrancarlo.

---

## FASE 5 — Gateado (flag y frenar) 🔴 REGISTRADO (terceros / canal vivo / cliente)

Todo aquí depende de terceros, del canal vivo o de decisiones del cliente — **ninguno resoluble autónomamente**, todos registrados:
- **WABA / portabilidad** (B-05, B-07): desambiguar el WABA `1931874540684022` (Venttur BM = portable / ManyChat = chip nuevo). Deadline 1/9 vencido.
- **Templates Meta** (B-07): crear ~10 + las 3 `seg_dia_*_bs`; aprobación 24-72h. `Agenda`/`Seguimiento agenda` posiblemente cruzados — no tocar hasta verificar en ManyChat.
- **Calendarios + C1** (B-10): crear los 8 (spec listo) cuando existan usuarios + conectar calendarios personales (manual) para disponibilidad compartida.
- **3 huérfanos** (B-07): assets/textos del cliente + pipeline comercial de Viajes educativos (B-09).
- **Tests B1-B4 / C1** (B-05): con número de test + OK.
- **Decisiones de cliente** (B-06): tope-2 + prioridad · Cualificado · fallback 1-cal-por-asesor.

---

## Resumen de avance (2026-09-03)

| Fase | Estado | Nota |
|---|---|---|
| 0 Verificación + snapshot | ✅ COMPLETA | PIT/n8n OK; estado GHL/n8n fotografiado; ZZSBX ya limpio |
| 1 Estructura GHL | 🟢 PARCIAL | **56 custom fields + 4 tags + 20 pipelines** creados y verificados; calendarios/custom-values diferidos; usuarios gated (B-03) |
| 2 ETL | ✅ COMPLETA | unión deduplicada + reconciliación (corrobora el diseño) + auditoría Clientify |
| 3 Import | 🟡 PREPARADO | scripts + dry-run validados (2.338 opps resuelven 100%); masivo 🛑 |
| 4 n8n staging | 🔴 REGISTRADO | exports frescos + IDs listos; build enfocado gated en B1/B2 |
| 5 Gateado | 🔴 REGISTRADO | terceros / canal vivo / cliente |

**Lo escrito en GHL hoy es 100% estructura reversible** (custom fields, tags, pipelines) — cero datos de contacto, cero canal, cero acción outward-facing.

---

## ✅ Import masivo EJECUTADO + reconciliado (2026-09-06)

Gates confirmados por el usuario (usuarios asignados + `Allow Duplicate Opportunity` ON) + cap diario full (9998). Corrido `resume-import.py` **secuencial** (opps → reasignación), exit 0.

**Resultado:**
- **Opps:** `creados(total)=2.295 · fallidos=0 · sin-contacto=43` (2.295 + 43 = 2.338 deals de origen ✓). pipeline+stage+assignedTo verificados (spot-check 5/5).
- **Contacts:** 6.316 creados (completado en la sesión previa); GHL real 6.329 ≈ idmap 6.324 (+5 despreciable).
- **Reasignación `assignedTo`:** 4.736 contacts (incluye Rodrigo/Andrés/Max, ya no gated por B-11). Spot-check 5/5.
- **Sin 429, sin pérdida** — el fix de rate-limit (0.5s + backoff + secuencial) aguantó.

**⚠️ Hallazgo — 61 opps duplicadas:** GHL tiene 2.360 opps = 2.295 (idmap) + 61 duplicados + 4 ejemplos default de GHL. Los 61 son duplicados de las ventanas de kill (opp creada en GHL pero idmap sin guardar antes del corte → recreada en el resume; `Allow Duplicate` las dejó pasar). Verificados: mismo contactId+name que una opp real del idmap. IDs en `salida-import/opps-extra-ids.json`. Script de limpieza guardado y acotado: `scripts/limpiar-opps-duplicadas.py` (dry-run por defecto, apunta SOLO a los 61, nunca a las 2.295 ni a los ejemplos). **✅ RESUELTO 2026-09-06: los 61 fueron BORRADOS** con OK explícito del usuario (`--apply`, 61/61) → quedan **2.299 opps** finales (2.295 reales + 4 ejemplos default de GHL).

**Scripts nuevos:** `reconciliar-import.py`, `analizar-opps-extra.py`, `limpiar-opps-duplicadas.py` (todos read-only salvo el último con `--apply`).

---

## FASE 4 · Increment 2 (context builder) — ✅ construido + validado (2026-09-06)

- Credencial n8n nueva **`GHL VTR (PIT)` (`YkVmaA4jlRbO1TQD`, httpHeaderAuth)** creada por API con el PIT (Authorization: Bearer). Es la que usarán todos los nodos GHL del staging.
- Staging `3sLd7KY3o8I7NvXi`: `Normalizar payload → Buscar Contact GHL → Construir estado lead → Agente IA WPP`. Generador: `scripts/gen-staging-inc2.py` (idempotente). Read-back OK (9 nodos).
- Lógica READ del `[ESTADO DEL LEAD]` validada contra GHL real (Python): `search by phone` trae customFields; SINGLE_OPTIONS como etiqueta, CHECKBOX como `['true']`.
- **Descubierto al aplicar:** el staging ya está **ACTIVO** y el usuario **ya bindeó un bot de Telegram** (`Venttur`, telegramApi) en Trigger + Enviar (B-13 parcial). Mi PUT preservó eso.
- **Pendiente E2E (Camilo):** mandar un mensaje al bot para confirmar el flujo en vivo (sin ejecuciones registradas aún). Un lead de test por Telegram cae en rama "Lead nuevo" (email sintético / sin teléfono) — la rama "lead conocido" quedó validada en Python.

**Siguiente:** Increment 3 (sessionKey MX 52→521, sin GHL) y/o Increment 4 (tools → GHL: `crear_contacto` upsert Contact + `elevar` Assign+DND+notificar Mauricio Y Max).

---

## FASE 4 · Increments 3 + 4a + 4b — ✅ construidos + validados (2026-09-07)

Todo en el staging `3sLd7KY3o8I7NvXi` (ACTIVO, bot Telegram `Venttur` bindeado). Nada de esto toca los 14 workflows vivos. Cada uno con generador idempotente en `scripts/`.

- **Increment 3 — sessionKey MX** (`gen-staging-inc3.py`): `Normalizar payload` reescrito con `canonPhone()` (réplica de `canon_phone` del ETL: `52`/`521`+10 → `+521<10>`). `sessionKey = canonPhone(phone) || chatId`. Arregla el bug del vivo (sessionKey sin normalizar → doble sesión 52 vs 521). En Telegram no hay teléfono → sigue por chatId (no cambia la sesión de Camilo). Verificado: 52+10 y 521+10 colapsan igual.
- **Increment 4a — `crear_contacto` → upsert Contact GHL** (`gen-staging-inc4a.py`): toolHttpRequest `POST /contacts/upsert`, `nombre`/`apellido` por `$fromAI`, phone/email deterministas del Normalizar payload, cred `GHL VTR (PIT)`. Reemplaza el sub Clientify+Airtable del vivo por una sola alta. **Validado por API**: upsert 201 → re-upsert `new:False` mismo id (dedup por teléfono/email OK). Conectado como `ai_tool`.
- **Increment 4b — `elevar` → GHL (handoff)** (`gen-staging-inc4b.py`): toolHttpRequest `PUT /contacts/{id}` `{assignedTo: Mauricio, dnd:true}` (contactId de `Buscar Contact GHL`). **Primitivos validados por API**: assign+dnd en un PUT → 200, read-back `assignedTo`+`dnd:true`. Conectado como `ai_tool`. **La notificación (email+app, fix "Notify:0") NO va acá — ver bloqueante B-N1.**

Tools del agente en staging ahora: `crear_contacto`, `elevar`.

### Sandbox de plataforma GHL (asunciones `00`§7.10) — resueltas headless (2026-09-07)
- **(a) match del upsert**: matchea por **teléfono** (same phone → mismo id). Confirma que la canonicalización previa era obligatoria (GHL no normaliza formato). ✅
- **(b) fechas históricas**: GHL **ignora `dateAdded` histórico** (mandé 2023 → read-back null). Cubierto: el ETL manda la fecha original al CF `fecha_alta_original` (mapea `created`/`Creada`), **poblado 25/25 en la muestra**. ✅
- **(h) silenciar por-contacto (DND)**: `dnd:true` funciona. ✅
- **(i) query de Contacts por custom field**: `filters:[{field:"customFields.<id>",operator:"eq",value:"Internados"}]` → 200, total 836. **Desbloquea el despachador cron + barrido de interrumpida.** ✅

---

## 🔴 BLOQUEANTES Y HALLAZGOS ABIERTOS (al 2026-09-07)

### Requieren terceros / canal vivo (no resolubles headless)
- **B-05/B-07 · WABA + portabilidad** (camino crítico al cutover 15/9): desambiguar si el WABA `1931874540684022` (número bot `+52 1 33 2627 4502`) vive bajo el BM de **Venttur** (portable, escenario A) o de **ManyChat** (chip nuevo, escenario B). **Deadline propio 1/9 ya vencido.** Verificación de 2 min en `business.facebook.com` de Venttur. Detalle: `06_docs/portabilidad-numero-whatsapp-2026-08-18.md`.
- **B-07 · Templates Meta**: crear ~10 + las 3 `seg_dia_3/5/7_bs` faltantes; aprobación 24-72h. Agendar YA.
- **Asunción (d) free-form send de sesión <24h**: load-bearing para el reply del agente; validar en LeadConnector con canal vivo + nº de test.
- **Asunción (e) Contact Reply trigger** (path de TODO el inbound WA/IG/FB → n8n): validar con canal vivo.
- **Asunción (f) send de template por API** con merge params por programa: necesita templates aprobados.
- **Asunción (g) URL de media del audio entrante**: necesita inbound de audio real.

### Requieren decisión del cliente
- ~~**tope-2 global + prioridad**~~ — ✅ **OK dado** (despachador construido con tope-2, 2026-09-07).
- ~~**`Cualificado`**~~ — ✅ **RESUELTO 2026-09-07**: determinado desde los flujos vivos (clasificador batch ~8h; criterio: 2º/3º idioma + escuela privada&bilingüe + edad por programa). NO era real-time del agente. Reconstruido en `Xmyoewwa1W5gm1fy` (tag). Ver §HALLAZGO Cualificado.
- **elevar · a qué usuario asigna**: hoy default **Mauricio** (v1). Objetivo: **al asesor del programa** → requiere el mapa programa→asesor (los 8 calendarios/asesores). Decisión + dato.

### Requieren build GHL-side (no vía API n8n)
- **B-N1 · Notificación del handoff (fix "Notify:0")**: notificar a **Mauricio y Max** por **email + notificación de app + inbox** al elevar. El inbox ya lo cubre el `assignedTo`; email+app se resuelven mejor con un **Workflow nativo de GHL** (trigger: tag `elevado-a-humano` o cambio de assignee → Internal Notification). No hay credencial de email en el n8n de VTR (confirmado). **Pendiente: construir ese Workflow en GHL** (la tool `elevar` ya deja al contacto asignado+DND; falta que dispare la notificación). Alternativa interim: notificar por Telegram desde n8n a los chat ids de Mauricio/Max.
- **Asunción (c) disponibilidad compartida entre calendarios de un asesor** (Andrés tiene 5): requiere los 8 calendarios creados + calendario personal conectado. Gated (calendarios no creados).
- **Asunción (j) trigger de booking + query de appointments**: para confirmación/recordatorios; requiere calendarios + citas.

### Increments de Fase 4 aún NO construidos (gated en lo de arriba)
- **Increment 5 — send GHL free-form + switch por canal**: el envío real por GHL Conversations depende de (d)+WABA. En staging el send sigue por Telegram. **No se construye a ciegas.**
- **Increment 6 — audio (camino nuevo B4), dedup n8n, despachador nurturing, `Cerrada`, CAPI-clone, formulario, confirmación/recordatorios**: el despachador ya está desbloqueado por (i) pero depende de las decisiones de cliente (tope-2/prioridad); audio depende de (g); confirmación/recordatorios de (c)/(j)+calendarios.

### Hallazgo de seguridad (heredado del vivo)
- **Secretos hardcodeados** en workflows vivos: token ManyChat (Bearer en el nodo `elevar` del main), API key OpenAI de whisper, token Clientify. **Rotar y mover a credenciales antes del cutover** (`06`§8 bandera 7).

---

## FASE 4 · Despachador proactivo (tope-2) + confirmaciones (2026-09-07)

- **`elevar` → Mauricio confirmado por el usuario** (default de asignación v1 queda firme). Sin cambio de código; se cierra ese gap de decisión.
- **Despachador único creado: `vrShEXQGGAo4FqAt` · `vtr-despachador-proactivo-v1` (INACTIVO, 7 nodos).** `gen-despachador.py`, idempotente. Consolida los 4 mecanismos de re-enganche (`09`) en un cron.
  - **Motor de selección con TOPE-2 — validado vs GHL real:** query `link_enviado=true` (1014 candidatos) → Code `Seleccionar`: tope-2 **null-safe** (toques null→0), excluye estado terminal (`Cita confirmada`), cota de recencia `RECENCIA_DIAS=30`, 1 toque/contacto. Resultado del dry-run: 1008 elegibles / 6 excluidos por terminal / 0 por tope (los históricos tienen toques null).
  - **Nodos de ENVÍO / MEMORIA / UPDATE cableados pero `disabled`** hasta cerrar los gaps.

### Hallazgos del sondeo de datos (informan el despachador)
- **`toques_enviados` poblado en solo ~34 contactos** (resto null) → el gate tope-2 es **code-side null=0**, no filtro server-side.
- **Operador `gt`/`<` sobre custom field → 422** (GHL no filtra rangos numéricos por CF en search). Confirmado: selección por filtro positivo + gate en código.
- **`link_enviado=true` = 1014** (coherente con el universo ~1.090 del embudo). `estado_conversacion`: Contestó 1 / Interrumpida 40 / Cita confirmada 6.

### Gaps del despachador para pasarlo a ACTIVO (registrados)
1. **"Sin cita agendada" NO es un CF** — la cita vive en el **pipeline operativo del bot** (`03`§5). Excluir a los que ya agendaron requiere cruzar con las Opportunities en etapas booked → se completa con el **increment de booking (asunción j, gated)**. Hoy el motor solo excluye `estado_conversacion='Cita confirmada'` (6), NO los ~375 que agendaron.
2. **Carril nurturing** (`link_enviado!=true`): falta el 2do query + el split de carril. Ojo: `link!=true` son ~5.300 en su mayoría históricos → **imprescindible la cota de recencia** para no spamear. `RECENCIA_DIAS` a confirmar con cliente.
3. **Templates Meta inexistentes (B-07)** → el nodo de envío es placeholder (`templateId: PENDIENTE_B-07`).
4. **Paginación completa** del query (v1 procesa 1 página de 100/run).
5. **Cadencia temporal fina** (a qué horas caen los 2 toques) — decisión de cliente (`09`§8).

### `Cualificado` — definición actual y qué falta para destrabarlo
- **Qué es:** una **etapa del pipeline operativo del bot** (`Nuevo → Contactado → En diagnóstico → Cualificado → Cita agendada → Cita confirmada → Asistió → Ganado/Perdido`), **+ tag**. Es un pipeline **reconstruido** (hoy en Airtable es un flag `Cualificado` bool; en GHL pasa a etapa, `03`§5).
- **Definición del cliente:** **cualitativa** — "el lead avanza en el descubrimiento y encaja con el perfil".
- **Lo único PENDIENTE (propuesta de la agencia, a confirmar):** el **disparador mecánico** — *"lo escribe el agente al cerrar el descubrimiento"*. Falta la señal concreta y observable con la que el agente marca `Cualificado` (p.ej.: cuando capturó programa + el lead manifestó intención real / encaja perfil). Sin esa regla, el agente no sabe *cuándo* mover a `Cualificado`.
- **Dónde se aplica:** lo escribiría el agente (una tool que mueve la Opportunity operativa a la etapa `Cualificado`) — esa tool NO está construida aún; depende de esta definición.

---

## HALLAZGO · Criterio de `Cualificado` — DETERMINADO desde los flujos vivos (2026-09-07)

Investigación pedida por el usuario. El campo `Cualificado` (checkbox Airtable) lo escribe el nodo `Actualizar 'cualificado'` de **`resumen-etiquetas-seguimientos.json`**. Cadena: `Execute Workflow Trigger → Esperar 8h → Postgres (historial) → Code → Airtable (ID Clientify) → OpenAI (gpt-4o-mini, temp 0, jsonOutput) → IF cualificado=="1" → Airtable Cualificado=true`.

**Criterio exacto (Tarea 5 del prompt del clasificador) — `cualificado='1'` si y SOLO si las 3:**
1. El usuario ya tiene conocimiento de un **segundo o tercer idioma**.
2. **Estudia o estudió en escuela privada y bilingüe.**
3. Cumple la **edad** del programa: **10-17** Summer Camp · **13-17** Año Académico y Boarding · **18-30** Pathway y Gap Year.
Si falla ≥1 → `'0'`.

**Corrección al diseño:** NO lo escribe el agente en tiempo real (eso era propuesta de la agencia). Es un **clasificador batch ~8h post-conversación** que además emite `tags` (programa), `tipo` (Padre/Madre|Estudiante), `resumen`, `asesoria` (uno/cero según recibió link). Doc `03`§5 corregido.

**Pipeline destino ya existe:** `OP · Bot Venttur` (`sezekQ4oFybMb4S5Bop1`), etapa `Cualificado`.

**Decisión abierta (chica) para reconstruirlo:** (a) mantener batch 8h (1:1) vs rediseñar a tiempo real; (b) representar `Cualificado` como **tag de contacto** (fiel al checkbox Airtable, sin depender del ciclo de vida de la Opportunity) vs **etapa del pipeline** `OP · Bot Venttur` (requiere que el lead tenga una Opportunity operativa — ciclo de vida aún no construido). La reconstrucción del clasificador (portar el prompt + rubrica) NO está bloqueada por terceros; sí depende de esta elección de representación.

## FASE 4 · Clasificador post-conversación (Cualificado) reconstruido 1:1 (2026-09-07)

- **Tag `cualificado` creado en GHL** (`SAf2PNSjPNNYJisUSAFq`) — representación fiel al checkbox Airtable (no depende del ciclo de vida de la Opportunity). idmap actualizado.
- **Workflow `vtr-clasificador-postconv-v1` (`Xmyoewwa1W5gm1fy`, INACTIVO)** — `gen-clasificador.py`. Porta VERBATIM el nodo OpenAI del vivo (rúbrica de 5 tareas, gpt-4o-mini temp 0, jsonOutput), swap de la conversación al input del trigger. Cadena: `Execute Workflow Trigger (conversation, contactId) → Clasificar → IF cualificado=='1' → Tag cualificado (GHL)`.
- **Validado end-to-end:** (1) LLM port — caso que califica (15a, privada+bilingüe, 2 idiomas, Boarding) → `cualificado='1'`, tags `['Boarding IA']`, tipo `Padre/Madre`; (2) tag-add — `POST /contacts/{id}/tags` 201, read-back `['cualificado']`.
- **Alcance v1:** cablea SOLO la salida `cualificado`→tag. Las otras salidas del mismo clasificador (`tags`→programa, `tipo`→tipo_contacto, `resumen`, `asesoria`→link_enviado) las computa el LLM pero su cableado a CFs es incremento aparte (con la guarda no-overwrite de `09`§4). Disparo real (post-conversación, hoy 8h) se cablea cuando se reconstruya el main.

## FASE 4 · Pasada autónoma de build no-bloqueante (2026-09-07)

- **Despachador v2** (`vrShEXQGGAo4FqAt`, `gen-despachador-v2.py`): motor de selección COMPLETO — 3 queries (booked OP·Bot + rescate link=true + nurturing estado OR) → Code tope-2 null-safe + dedup + prioridad + exclusión booked + recencia. Validado en Python (rescate 1014→1001). Envío/mem/update disabled (templates gated).
- **Barrido interrumpida** (`LrJuzU7qDeELWiAl`, `gen-interrumpida.py`): cron 1h → query estado='Contestó' → silencio >24h null-safe → PUT 'Interrumpida'. Reconstruye `wf-estado-interrumpida`. INACTIVO.
- **Query caps GHL:** `ne`/`gt` sobre custom field → 422 (nurturing usa OR-group por estado, funciona); `opportunities/search` por stage funciona (0 hoy, OP·Bot sin opps).
- **Findings go-live despachador (registrados en la guía pre-traspaso):** (1) `ultima_actividad` null en históricos → recencia inefectiva → ~1000 candidatos rescate en 1ª corrida (falta política históricos); (2) exclusión "con cita"=0 hasta poblar OP·Bot con booking.
- **Bloqueante handoff-notify:** no hay chat ids de Mauricio/Max (solo Camilo `6390727286`) + Workflows GHL no creables por API → fix va por GHL-UI (email+app) o chat ids del equipo. Registrado.
- Detalle completo + inventario staging: `06_docs/guia-pendientes-pre-traspaso-waba-2026-09-07.md` §"Actualización de build 2026-09-07".

## FASE 4 · Testeo del agente por Telegram dejado redondo (2026-09-07)

- **Guía para Mauricio + pre-flight de Camilo:** `07_testing/testing-guide-telegram-agente-2026-09-07.md` (8 casos + criterios + qué reportar + cleanup de contactos `@venttur.test`).
- **Validación headless del agente:** corrido el system prompt vivo (46.8K) por gpt-4o con el formato real de User Message (`[ESTADO DEL LEAD]` + mensaje). Resultados on-brand: saluda como Mauricio/Venttur, pide nombre, da rango de precio Internados (USD 50-130k) + ofrece asesoría con Rodrigo, y **respeta `[ESTADO DEL LEAD]`** (con Nombre en el estado NO re-pregunta). Confirma la calidad de conversación que verá Mauricio.
- **De-risk `crear_contacto`:** el jsonBody pasó de un IIFE con `$fromAI` embebido al **patrón plano `$fromAI`** (evita el trap Zod "tool input did not match schema" histórico del repo). elevar quedó igual (body estático). Headers verificados OK en los 3 nodos HTTP.
- **Pendiente único (runtime):** el POST directo al webhook del Telegram Trigger da 404 (n8n no lo expone así) → el runtime completo se confirma con el **pre-flight "hola"** de Camilo antes de compartirlo. Todo lo demás (agente, context-builder logic, headers, tool) validado.

---

## FASE Nahe · fix de producción sobre el vivo (2026-09-15 → 16, la agencia+Claude)

Autor de este bloque: **la agencia+Claude** (paralelo al track de Camilo, sobre el vivo `k3aivKSP67S97IHn`).

### 2026-09-15 — Incidente Nahe detectado

- Max reportó vía WhatsApp que una lead (Nahelli Macías Álvarez, id_2 `5214731005555`, programa AA Familiar IA) se quejó públicamente porque el agente le prometió una llamada que nunca existió.
- Reconstrucción con evidencia por ejecución + Postgres history: `06_docs/incidente-nahe-2026-09-15.md`.
- **Causa raíz identificada:** el prompt v2.0 vivo tenía dos instrucciones que le enseñaban al agente a *"coordinar el horario a mano"* cuando el link ya se había enviado. El agente ejecutaba esas instrucciones correctamente pero NO tiene tool de calendar — resultado: promete horarios que nadie del lado del asesor cubre.
- **Snapshot pre-fix:** `03_workflows/vivo-2026-09-15-pre-fix-nahe/` (con sha256).

### 2026-09-16 (14:49 UTC) — FASE 3 fix estructural sobre el vivo

- **Capa 1 · prompt v2.0 → v2.1** (+2.692 chars): REGLA ABSOLUTA #8 "No agendo yo" en Principios rectores + fix del bloque `[ESTADO DEL LEAD]` + advertencia en `§📲 Enlaces de asesoría` + reescritura del § "Ya le mandaste el link y no agendó". Archivo: `04_agents/agente-venttur-system-prompt-v2.1.md`.
- **Capa 2 · guardrail estructural** (13 nodos totales, 43 al final con Fase 6): nodo Code `Detectar promesa fantasma` entre `Formatear mensaje WPP` y `Normalizar burbujas`. Detecta patrón "verbo de coordinar/quedar + referencia temporal, sin URL canónica" (2 caminos, 12/12 tests golden). Si intercepta, reemplaza `{parte1, parte2, parte3}` por link canónico + framing de disculpa. Emite flag `_phantom_promise_intercepted: true`.
- **Tests:** golden 12/12 + smoke test 5/5 escenarios de Nahe contra OpenAI con prompt v2.1 vivo.
- **Snapshot post-fix:** `03_workflows/vivo-2026-09-16-post-fix-prompt-guardrail/` con detector JS versionado + tests.

### 2026-09-16 (~16:00 UTC) — FASE 6 alertas + persistencia

- **Tabla Postgres** `vtr_phantom_interceptions` (session_key, execution_id, lead_nombre, lead_programa, url_enviada, mensaje_original_parte1..3, occurred_at). Índices por occurred_at y session_key.
- **Alerta P1** (Telegram inmediato) al chat `6390727286` cuando el guardrail intercepta. Credencial `botla agencia` (`V5k84z3AjQc9Y5yg`). En paralelo al INSERT Postgres.
- **Workflow separado `VTR · digest diario guardrail`** (`BzBCMGxEdJy6zmA9`, ACTIVE): cron 08:00 CDMX (14:00 UTC) que lee `vtr_phantom_interceptions` de las últimas 24h. Si N=0 no envía nada; si N>0 manda digest consolidado con top 5 por severidad.
- **Snapshot post-fix Fase 6:** `03_workflows/vivo-2026-09-16-post-fix-fase6-alertas/` (main-venttur 43 nodos + vtr-digest-diario-guardrail).

### 2026-09-16 — FASE 5 barrido de cohorte

- Query Postgres `n8n_chat_histories` últimos 30 días con misma lógica del detector → 60 turnos AI confirmados con promesa fantasma en 34 sesiones distintas.
- 11 leads con 2+ promesas · 7 leads con patrón exacto de Nahe.
- CSV + resumen: `06_docs/barrido-leads-promesa-fantasma-2026-09-16.md/csv`.

### 2026-09-16 — FASE 7 contratos de diseño a la migración GHL

Agregado a los docs de arquitectura y guía de migración:
- `03_arquitectura_ghl/06 §9` — Contratos de diseño heredados del incidente Nahe (capa prompt + capa estructural + anti-patrón generalizable).
- `03_arquitectura_ghl/07 §7` — Regla dura "el agente NO agenda por chat" (separada del reorden de write en §3).
- `04_guia_migracion/07_n8n_agente_canal.md §7.7` — banderas y checkpoints actualizados (prompt cutover obligatorio con Regla #8, guardrail heredado, digest heredado).
- `04_guia_migracion/11_testing_precutover.md §11.3.bis` — bloque de regresión N1-N7 con mensajes verbatim de Nahe + falla dura de aprobación si el prompt del cutover no tiene la Regla #8.

---

## FASE Sincronización · integración del zip de Camilo + Bloque 0 staging (2026-09-16, la agencia+Claude)

Autor: **la agencia+Claude**. Cierra la sincronización tri-fuente antes del cutover 18-19/9.

### Bloque 0 · Guardrail Nahe replicado al staging n8n

- **Snapshot pre-fix:** `03_workflows/staging-2026-09-16-pre-replica-guardrail/` (workflow `3sLd7KY3o8I7NvXi`, 12 nodos, sha256 `4103e04a…`).
- **Aplicado por API** los 4 edits del prompt v2.0 → v2.1 (47.462 → 50.188 chars) + inserción del nodo Code `Detectar promesa fantasma` entre `Agente IA WPP` y `Enviar Telegram`. Detector adaptado al pipeline sin splitter (trabaja sobre `$json.output` crudo). Lee `programa_interes` del custom field `xK2NFqtz1DYUw3gYdn8I` del contact.
- **Snapshot post-fix:** `03_workflows/staging-2026-09-16-post-replica-guardrail/` (13 nodos, sha256 `44c99ff9…`, versionId `ac7eea71…`, active=true).
- **Tests:** 8/8 golden del detector staging + 3/3 smoke contra OpenAI (mensajes verbatim de Nahe responden con `promo.venttur.com/AAFamilia-Agendar`).
- **Pendiente iterativo (no bloquea cutover):** replicar en el staging la alerta P1 Telegram + INSERT en `vtr_phantom_interceptions` (por ahora solo emite el flag en runData). Iteración post-cutover si se quiere trazar activaciones durante el testing.

### Bloque 1 · Integración del zip de Camilo

- Fuente: `/Users/camilo/Downloads/_RECONCILIACION-2026-09-11.zip` (Camilo, 220 archivos post-consolidación 11/9).
- **13 archivos NUEVOS copiados al WS:** `_RECONCILIACION-2026-09-11.md`, `PENDIENTES-MIGRACION-2026-09-11.md`, 8 docs bajo `06_docs/*-2026-09-11.md`, workflow `venttur-staging-agent-cerrada-v1.json`, `CLIENT_INFO-migracion-real.md`.
- **7 archivos SUPERSEDED NO copiados** (según `_RECONCILIACION-2026-09-11.md §Archivos del track divergente`): `04_guia_implementacion/`, `especificaciones-waba-traspaso.md`, `venttur-main-GHL-v1.json` (tiene OpenAI key hardcodeada), `wf-meta-capi-GHL-v1.json`+checklist, `wf-rescate-post-link-GHL-v1.json`+checklist.
- **111 archivos B (conflicto manejable)**: tamaños casi idénticos (differ solo en scrub `la agencia` ↔ `la agencia`, `la agencia` ↔ `Camilo`). Mantengo la versión WS.
- **5 archivos F (conflicto grande)**: los 4 docs de Fase 7 (`03_arquitectura_ghl/06`, `07`, `04_guia_migracion/07`, `11`) + `ESTADO_MIGRACION.md` — mi versión gana (más nueva + contenido Fase 7 que Camilo no vio).

### Bloque 3 · Actualización con desbloqueos de la reunión 15/9

- **WABA:** Escenario A confirmado → marcado en `ESTADO_MIGRACION.md §Actualización 2026-09-16` + `12_cutover.md`. Deudas de higiene en 5 docs más (banderas en `SINCRONIZACION`).
- **Fecha cutover 18-19/9:** actualizado en `12_cutover.md` header + `ESTADO_MIGRACION.md`.
- **Cualificado = TAG:** decisión abierta cerrada en `03_arquitectura_ghl/03_datos_pipeline_deals_estado.md`.
- **Aventureras (~100-125 landings):** §6 nuevo en `03_arquitectura_ghl/07_agendamiento_calendarios.md`, contradicción con §1/§5 documentada. Requiere rediseño previo o aceptación de trazabilidad transitoria. Owner del rediseño: la agencia (via Bloque 2 del plan).
- **Recontact policy:** §8 nuevo en `03_arquitectura_ghl/09_nurturing_rescate_reengagement.md` (primer contacto solo a leads con link + sin cita agendada).
- **Handoff MCP/PIT para Camilo:** doc nuevo `06_docs/handoff-camilo-mcp-ghl.md`.

### Bloque 4 · Doc pivote temporal

- `SINCRONIZACION-2026-09-16.md` (sunset 26/9): fuente de verdad temporal que consolida los pendientes vivos, estado del Bloque 0, cambios del 15/9 y hitos hacia el cutover 18-19.

### Bloque 5 · CLIENT_INFO y REGISTRO (este archivo)

- `CLIENT_INFO.md`: nota de 2026-09-16 al principio con todo el contexto post-16/9. Base del archivo intacta.
- `REGISTRO-EJECUCION.md`: adoptado el body del zip 11/9 de Camilo (contenido 08-11 que no estaba en el WS) + APPEND de las fases Nahe + Sincronización (estas 2 secciones nuevas).
