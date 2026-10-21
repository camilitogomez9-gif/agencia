# Pendientes n8n — "¿falta algo?" (post-BSP/WABA) · VTR → GHL

> **Propósito:** este es el **registro canónico** de lo que falta terminar/ajustar en **n8n** para cerrar la
> migración. Después de la migración BSP del WABA, si la pregunta es *"¿falta algo en n8n?"*, la respuesta
> exacta está acá.
> **Regla de oro que sigue vigente:** los flujos ORIGINALES de producción **no se tocan hasta el cutover**;
> todo lo reconstruido en GHL vive **OFF** hasta que se activa en el cutover.
> Actualizado: 2026-09-21 (tras batches de ejecución del 21/9). Fuentes: `ejecucion-n8n-2026-09-21.md` +
> `revision-n8n-al-100-2026-09-20.md`. Snapshots vivos con sha256 en `03_workflows/ghl-live-2026-09-21-ejecucion/`.

## Leyenda de estado
✅ hecho · 🟢 construido y OFF (listo, sólo falta activar) · 🟡 construido pero con ajuste puntual pendiente ·
🔴 falta construir · 🔗 falta *wiring* (que el agente principal lo invoque) · ⛔ gated por WABA/calendarios/decisión de cliente.

---

## 1. Inventario n8n vivo — estado de cada pieza

| Workflow | n8n id | Estado hoy | Migrado a GHL | Qué falta |
|---|---|---|---|---|
| **Agente principal (producción)** `[Venttur]` | `k3aivKSP67S97IHn` | ON (ManyChat/Airtable) | — (es el original) | Se apaga en cutover. Aplicar prompt v2.2 al vivo el D-day. |
| **Agente staging (GHL, test Telegram)** | `3sLd7KY3o8I7NvXi` | ON | 🟡 parcial | Prompt v2.2 ✅ aplicado. Faltan increments 5/6 (⛔ WABA) + wiring (ver §C) + fixes builder (ver §E). |
| Despachador nurturing | `vrShEXQGGAo4FqAt` | OFF | 🟢/🟡 | templateId por programa (⛔ WABA), política recontacto §8, activar. |
| Rescate Post-Link GHL | `YB0UxwEVwzISdd54` | OFF | 🟢/🟡 | envío por template (⛔ WABA), fix ruteo `'idioma'`, verificar señal `agendan_cita`, activar. |
| Barrido interrumpida | `LrJuzU7qDeELWiAl` | OFF | 🟢/🟡 | errorWorkflow + paginación, verificar exclusión de citados, decidir 24h vs 5d, activar. |
| Clasificador post-conv | `Xmyoewwa1W5gm1fy` | OFF | ✅ | 🔗 que el main lo invoque (+8h / al cerrar). |
| Digest diario guardrail | `BzBCMGxEdJy6zmA9` | ON | ✅ | nada. |
| Meta CAPI (Supabase) | `mf7VQJelfieCDJ5r` | OFF | ✅ | migrar folios históricos (cutover), rotar token, referral CTWA del main, swap+activar. |
| CAPI Registro Folio (Supabase) | `4HgMkK34xqITULM3` | OFF | ✅ | repuntar webhook al path original en cutover, activar. |
| Estado lead 'Contestó' (GHL) | `qYgeTc9PCq3TiGDn` | OFF | ✅ | 🔗 que el main lo invoque por inbound. |
| Correo Semanal (GHL) | `OaOyHA2tfjMtuWTk` | OFF | ✅ | definir métrica exacta + destinatario real + paginación; activar (depende de que OP·Bot tenga opps). |
| **Formulario landing** | `ZB6erhWicZmDfC4I` (orig, ON) | ON | 🔴 **falta construir** | Rebuild W4 → Contact GHL. NO gated. |
| **Confirmación de agenda** | `2PSekVBxarsrnVBu` (orig, ON) | ON | 🔴 **falta construir** | Rebuild W6 → GHL Calendar. ⛔ calendarios GHL + OAuth asesores + trigger booking. |
| **Actualizar link enviado** | `gRSMjzxggA4UePjz` (orig, OFF) | OFF | 🔴 **falta construir** | Rebuild W9 → custom `link_enviado` + dispara rescate. NO gated. |
| **Outreach Form Meta (ingest)** | `CUuFxbst3iHpgeXS` (orig, ON) | ON | 🔴 **falta construir** | Rebuild del ingest Sheet→Contact GHL (el carril de toques ya está en el despachador). |
| Meta CAPI (original) | `z98w2yWVEMOfifMl` | OFF | reemplazado | borrar/desactivar en cutover (lo cubre `mf7VQJelfieCDJ5r`). |
| CAPI Folio (original) | `9yCbynoKDt9hgiBq` | ON | reemplazado | swap al `4HgMkK34xqITULM3` en cutover. |
| Rescate (original) | `mkEP1qFN7MVb9qP0` | OFF | reemplazado | borrar en cutover. |
| Estado interrumpida (original) | `H6qYB3Oj97bxaTCX` | ON | reemplazado | apagar cuando entre `LrJuzU7qDeELWiAl`. |
| Estado lead (original) | `b52CUYEkI2Ah3Xj6` | OFF | reemplazado | borrar en cutover. |
| Resumen/etiquetas (original W13) | `DyrDumQgb6S4zHsS` | OFF | reemplazado | borrar en cutover (lo cubren clasificador + despachador). |
| Seguimiento agenda (W7) | `DZlSEQS5qzX1Y01K` | OFF | descartado | borrar en cutover (consolidado en rescate). |
| Crear contacto (W5) | `cZUNKQyZNOHy5twQ` | OFF | disuelto | borrar en cutover (lo cubre la tool `crear_contacto` + W11). |
| Correo semanal (original) | `BrFfQyDfamdUzq64` | OFF | reemplazado | borrar/archivar tras validar el GHL. |
| Data Export Runner | `rQj7p6qfcwYMMnQN` | OFF | one-shot | borrar post-cutover. |
| Cortar para resumen [OUTDATED] | `2m8knqC0IIgGixiP` | OFF | obsoleto | borrar. |
| TEMP GHL IDs | `ay9tr5TzVRp4LU80` | OFF | temporal | borrar post-cutover. |
| TEMP Setup Postgres M6 | `Dys4uaXlveGta3q2` | OFF | temporal | borrar post-cutover. |

---

## 2. Lo que falta, por categoría

### A · Flujos ya construidos en GHL — sólo falta ACTIVARLOS (post-WABA)
- 🟢 Despachador `vrShEXQGGAo4FqAt` → activar tras: (1) cablear `templateId` por programa/carril (⛔ templates Meta), (2) política recontacto §8 (primeros 7 días: sólo `link_enviado=true AND cita=false AND estado NOT IN (Cerrada,Perdida)` — hoy la query de rescate trae ~1.014).
- 🟢 Rescate GHL `YB0UxwEVwzISdd54` → activar tras: envío por template (⛔ WABA), fix `'idioma'`, verificar que el booking escribe `agendan_cita`.
- 🟢 Barrido `LrJuzU7qDeELWiAl` → activar tras: errorWorkflow + paginación + verificar exclusión de citados; apagar el original `H6qYB3Oj97bxaTCX`.
- 🟢 CAPI `mf7VQJelfieCDJ5r` + `4HgMkK34xqITULM3` → ver §D (swap + migración de folios).
- 🟢 Correo `OaOyHA2tfjMtuWTk` → activar tras definir métrica + destinatario (⛔ decisión cliente).

### B · Flujos que FALTAN construir (no existen en GHL todavía)
- 🔴 **W4 Formulario landing → Contact GHL** (`ZB6erhWicZmDfC4I` es el original). Colapsar Clientify+Airtable a un `POST /contacts/upsert`, remap `BS→Internados`, repuntar la landing. **NO gated — construible ya.**
- 🔴 **W9 Actualizar link enviado → GHL** (`gRSMjzxggA4UePjz` original). Marca custom `link_enviado` (`rHzGNiesWuESPmSZyviJ`) + tag por programa + dispara el rescate. **NO gated — construible ya.**
- 🔴 **W6 Confirmación de agenda → GHL Calendar** (`2PSekVBxarsrnVBu` original). ⛔ Depende de los 8 calendarios GHL + OAuth de asesores + el trigger de booking (GHL Workflow → webhook n8n). Fix del bug: enviar → **después** marcar; borrar el path de Diego.
- 🔴 **W10 ingest Outreach Form Meta → Contact GHL** (`CUuFxbst3iHpgeXS` original). El **carril de toques ya vive en el despachador** (Decisión B); falta sólo el ingest Sheet→Contact GHL (dedup por teléfono/Folio). Tope-2 y de-hardcode `Programa interés`.

### C · Wiring del agente principal (W1) — lo que el main GHL debe invocar
El agente staging **hoy no invoca nada de esto**. En el cutover (o en el build de W1) hay que cablear, en paralelo por inbound / según corresponda:
- 🔗 rama `Envió link?` (output contiene `promo.venttur.com/`) → **W9** (marca `link_enviado` + dispara rescate).
- 🔗 executeWorkflow → **W2 Meta CAPI** (`mf7VQJelfieCDJ5r`) por inbound.
- 🔗 estampado **'Contestó'** → **W11** (`qYgeTc9PCq3TiGDn`) por inbound (input `contactId`).
- 🔗 **clasificador** (`Xmyoewwa1W5gm1fy`) +8h / al cerrar conversación (input `conversation` + `contactId`).
- 🔗 disparo del **despachador** de nurturing (o dejarlo al cron del despachador).
- ⛔ increments 5/6: entrada por **GHL Contact Reply**, salida **free-form Conversations** multi-burbuja, **audio** (whisper). Gated WABA.

### D · Migración de datos + swaps del cutover
- Migrar **Folios históricos** Airtable (`[AIRTABLE_TABLE_ID]`) → `capi_folios` (one-shot; mismo patrón ya probado con Programas). **Correr en el cutover** (si se corre antes queda stale porque el W3 original sigue escribiendo a Airtable).
- **Rotar** el `access_token` de Meta y actualizar `capi_programas` (Supabase).
- **Swap CAPI:** desactivar `9yCbynoKDt9hgiBq` (folio) y `z98w2yWVEMOfifMl` (CAPI); repuntar el webhook de `4HgMkK34xqITULM3` al path `capi-registro-folio-venttur`; activar `4HgMkK34xqITULM3` + `mf7VQJelfieCDJ5r`.
- **Referral CTWA:** confirmar que el main GHL pasa el `programa` del referral de Meta al trigger de CAPI (hoy `mf7VQJelfieCDJ5r` usa fallback `'BS'`).
- **Apagar** los 14 originales al swap; **borrar** los descartados (W5 `cZUNKQyZNOHy5twQ`, W7 `DZlSEQS5qzX1Y01K`, W13 `DyrDumQgb6S4zHsS`, Data Export, OUTDATED, TEMPs).
- Dar de baja las credenciales **Airtable** (`airtableTokenApi`) y **Clientify** (`httpHeaderAuth`) cuando ningún flujo las use; dar de baja las tablas Airtable Folios/Programas tras verificar CAPI E2E.

### E · Ajustes finos / decisiones abiertas (n8n)
- **sessionKey `+`/sin-`+`:** reconciliar la forma canónica del sessionKey de memoria contra el main vivo post-cutover. Afecta igual a **rescate + despachador + memoria sintética** (hoy usan `nsk()` = dígitos sin `+`; el `memoryPostgresChat` del staging usa `canonPhone()` = con `+`). Es un solo fix coordinado.
- **Agente — fixes de builder (no gated):** reponer en `Construir estado lead` las líneas **`Cita: AGENDADA`** (deriva de `estado_conversacion='Cita confirmada'` o stage) y **`Link… NO agendó todavía`** — sin ellas el agente le vende a quien ya reservó y pierde el disparador de "ya le mandaste el link".
- **Agente — piezas no gated a agregar:** splitter multi-burbuja (`Formatear mensaje WPP` + `Normalizar burbujas`), debounce en n8n, dedup n8n-native (UTF-8), `phone` en la tool `crear_contacto`, rama de guardrail completa (alerta P1 Telegram + INSERT `vtr_phantom_interceptions`), notificación en la tool `elevar` (bug Notify Assignees:0 → mails/chat ids del equipo).
- **Correo W14:** métrica exacta (etapas que cuentan + `createdAt` vs cambio-de-etapa), destinatario real (hoy placeholder `[EMAIL-AGENCIA]`), paginación cuando OP·Bot supere 100 opps.
- **Tope-2** de toques + prioridad rescate>nurturing: tomado técnicamente, falta OK explícito del cliente.
- **Barrido 24h vs ~5d:** 24h operativo (barrido) vs ~5d (métrica de reporte) — confirmar el umbral con el cliente.

### F · Limpieza post-cutover
Borrar TEMPs (`ay9tr5TzVRp4LU80`, `Dys4uaXlveGta3q2`), Data Export (`rQj7p6qfcwYMMnQN`), OUTDATED (`2m8knqC0IIgGixiP`) y los originales reemplazados una vez estable +48h.

---

## 3. Checklist "post-WABA — ¿falta algo?" (orden sugerido)

**Ya está el número/WABA en GHL. Para cerrar n8n, en orden:**

1. [ ] **Agente W1 — completar (no gated):** splitter multi-burbuja · debounce · dedup · fixes builder (`Cita`/`Link`) · `phone` en `crear_contacto` · guardrail completo (alerta+log) · notify en `elevar`.
2. [ ] **Agente W1 — canal (gated WABA, ahora desbloqueado):** entrada GHL Contact Reply · salida free-form Conversations multi-burbuja · audio→whisper.
3. [ ] **Agente W1 — wiring:** cablear W9 (rama link) · W2 CAPI · W11 (Contestó) · clasificador +8h · dispatcher.
4. [ ] **Construir W9** (Actualizar link) y **W4** (Formulario→GHL).
5. [ ] **Construir W6** (Confirmación agenda) — necesita calendarios GHL + OAuth asesores + trigger booking.
6. [ ] **Construir W10 ingest** (Sheet→Contact GHL); el carril de toques ya está en el despachador.
7. [ ] **CAPI cutover:** migrar folios históricos · rotar token · swap webhooks · activar `mf7VQJelfieCDJ5r` + `4HgMkK34xqITULM3` · confirmar referral CTWA.
8. [ ] **Activar los nurturing/rescate:** cablear `templateId` por programa (rescate + despachador + outreach) · política recontacto §8 · activar despachador + rescate + barrido.
9. [ ] **Correo W14:** definir métrica + destinatario · activar.
10. [ ] **sessionKey** reconciliado (`+` vs sin `+`) en rescate/despachador/memoria.
11. [ ] **Swap + limpieza:** apagar los 14 originales · borrar descartados (W5/W7/W13/Data Export/OUTDATED/TEMPs) · dar de baja credenciales Airtable + Clientify.
12. [ ] **Testing E2E** de todos los subsistemas en verde antes de dar por cerrada la parte n8n.

> Cuando estos 12 estén ✅, **no falta nada en n8n**. Detalle node-level de cada rebuild: `revision-n8n-al-100-2026-09-20.md` §4.
