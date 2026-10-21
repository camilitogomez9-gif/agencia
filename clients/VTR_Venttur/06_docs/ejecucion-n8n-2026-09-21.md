# Ejecución n8n — Decisiones A + B (VTR → GHL) · 2026-09-21

> Batch aprobado por la agencia: **limpieza + despachador + CAPI (ledger a Supabase)**.
> Regla: **no tocar los 14 originales de producción** (siguen ON hasta el cutover del 26/9).
> Todo lo nuevo/modificado queda **OFF** hasta el cutover. Snapshots live con sha256 en
> `03_workflows/ghl-live-2026-09-21-ejecucion/`. Backups de lo borrado en `03_workflows/dead-track-backup-2026-09-21/`.

---

## 1. Limpieza ✅ HECHO

- 🗑️ **Borrados de n8n** los 2 artefactos muertos del track descartado (backup en repo antes de borrar; verificado que ningún otro flujo los referenciaba):
  - `jhwqWHIHEQ4Lhljs` **venttur-main-GHL** (airtable32/clientify3/manychat27) — era la fuente de la confusión del prompt.
  - `Os2By0ktLL7etnhH` **Meta CAPI - Venttur (GHL)** (airtable37, copia sin migrar).
- Verificado: ambos devuelven 404 tras el DELETE. Inventario VTR limpio (sin artefactos muertos, sin temporales de esta sesión).

## 2. Despachador (Decisión B + 3 bugs) ✅ HECHO Y VERIFICADO — `vrShEXQGGAo4FqAt` (OFF)

Editado en vivo (GET→edit→PUT→re-GET verificado). 9 → **10 nodos**. Sigue **OFF**.

- **Decisión B — carril outreach consolidado:** nuevo nodo `Query outreach (Form Meta)` (contacts/search `origen='Form Meta'`) insertado en la cadena `… Query nurturing → Query outreach → Seleccionar`. El motor `Seleccionar` suma la **3ª prioridad `outreach`** (sólo si `touch1_programado_at` ya venció), bajo el **mismo TOPE-2 global** (el `gate()` ya lo aplica). Con esto el carril de toques de W10 vive en el despachador único (doc 09).
- **Bug 1 (P0) — `Update toques (+1)`:** escribía `ultima_actividad` (`jrdfZCF6VWAA3L7WDVdB`) en cada toque saliente → rompía el barrido de interrumpidos. **Corregido → `ultimo_toque_at` (`P3a7nGkO57LwCvHhYQyc`)**.
- **Bug 2 (P0) — TERMINAL:** `['Cita confirmada']` → **`['Cita confirmada','Cerrada']`** (no re-tocar leads cerrados). El valor `'Cerrada'` ya existe en el CF `estado_conversacion` en GHL (verificado).
- **Bug 3 (P1) — sessionKey de la memoria sintética:** `Siembra memoria` usaba `$json.phone` crudo → **ahora `session_key = nsk(phone)`** (misma derivación dígitos/MX 52→521 que el Rescate GHL). ⚠️ Queda por reconciliar `+`/sin-`+` contra el main vivo en el cutover (afecta igual a Rescate + despachador; no se adivina ahora).

**Verificado:** JS syntax-check OK · IDs de custom field confirmados 1:1 contra GHL vivo · las 3 queries de selección devuelven datos reales (rescate **1.014**, nurturing **41**, outreach **457** contactos). ⚠️ Ver §5 (los 1.014 de rescate exigen la política §8 antes de activar). Envío (`Enviar template GHL`) sigue **placeholder/disabled** — gated por WABA + templateId por programa.

## 3. CAPI → Supabase (Decisión A) ✅ FUNDACIÓN + REBUILDS HECHOS Y VERIFICADOS

El ledger sale de Airtable a **Supabase** (misma DB de la memoria, cred n8n `ihpvM7nYMdLCwWDP`; la MCP de Supabase apunta a otro proyecto, así que todo se hizo vía n8n). Verificado que esa cred conecta a la Supabase real de VTR (`n8n_chat_histories` = 42.566 filas).

- **Tablas creadas** (verificado): `capi_folios` (13 cols, PK folio) + `capi_programas` (5 cols, PK programa).
- **Programas config migrado** (verificado): 4 filas (BS/BSC/BSG/HF) con `pixel_id` + `default_url` + `access_token` (el token se migró sin exponerlo; rotarlo sigue siendo tarea aparte, §16.2 de la guía).
- **W3 rebuild — `CAPI Registro Folio (Supabase)` (`4HgMkK34xqITULM3`, OFF):** idéntico al original salvo el nodo de guardado → **Postgres upsert en `capi_folios`**. **Verificado E2E**: se envió un folio de prueba por su webhook, aterrizó correcto en `capi_folios` (fbc computado bien, ts/landing_url), y se limpió la fila de prueba. Webhook nuevo `capi-registro-folio-vtr-supabase` (en cutover se repunta al path del original).
- **W2 rebuild — `Meta CAPI (Supabase)` (`mf7VQJelfieCDJ5r`, OFF):** 20 → **16 nodos**.
  - Los 4 nodos de ledger Airtable → **Postgres** (`Buscar Folio`, `Buscar Config Programa1/2`, `Update record2` fbtrace). Se **conservaron los nombres** de nodo para no romper ninguna referencia `$('...')` downstream.
  - **Borrados** los 4 nodos de la tabla Airtable **Leads** (`Buscar Lead por Teléfono`, `existe1`, `Update record3`, `Folio (N/A)`) — verificado que el evento CAPI no los usa. Rewire limpio, sin conexiones colgadas.
  - **CTWA data-driven:** `Buscar Config Programa2` ya no hardcodea `BS` → toma `programa` del referral del Trigger con **fallback `'BS'`**.
  - `Preparar CAPI Data1/2` + los 2 `HTTP Request Meta CAPI` (Graph v21) **intactos**.
  - **Verificado:** el SELECT de folio devuelve exactamente las claves aliaseadas `Timestamp` y `Landing URL` que `Preparar CAPI Data1` consume; el config read devuelve pixel/token/url. No se disparó ningún evento real a Meta (el flujo quedó OFF; su lógica de firing es byte-idéntica al original).

## 4. Pendiente CAPI para el cutover (NO se hace ahora, se haría stale)

- **Migración one-shot de Folios históricos** Airtable (`[AIRTABLE_TABLE_ID]`, ~4.000 filas) → `capi_folios`. Mismo patrón ya probado con Programas (Airtable read → Postgres upsert). Se corre **en el cutover** (si se corre ahora, el W3 original sigue escribiendo folios a Airtable hasta el swap y la copia queda desactualizada).
- **Swap en cutover:** desactivar W3 original + repuntar el webhook del W3-Supabase al path `capi-registro-folio-venttur`; activar W2-Supabase; desactivar W2/W3 originales.
- **Rotar el `access_token` de Meta** y actualizar `capi_programas` (higiene; opcional pero recomendado).
- Tras verificar el envío CAPI E2E, dar de baja las tablas Airtable Folios/Programas.

## 5. Nota importante para el go-live del despachador

La query de rescate devuelve **1.014 contactos** (`link_enviado=true`) — el pico de leads históricos que la revisión ya anticipó. `RECENCIA_DIAS=30` **no filtra** a los que tienen `ultima_actividad` null (históricos). **Antes de activar el despachador** hay que implementar la **política de recontacto §8** (primeros 7 días: sólo `link_enviado=true AND cita=false AND estado NOT IN (Cerrada,Perdida)`) o el envío saldría a ~1.000 contactos. El flujo está OFF, así que no dispara nada todavía.

## 6. Gotchas de n8n API confirmados en esta sesión (para futuras ediciones)

- **Heredoc de shell:** usar SIEMPRE `<< 'PYEOF'` (comillas) o escribir a archivo — con heredoc sin comillas el shell mastica `$('...')`, `$json`, `$1` dentro de los strings de Python. (Un W2 salió corrupto por esto → borrado y rehecho vía archivo.)
- **Expresiones n8n:** `String(...)` dentro de un `={{ ... }}` de `queryReplacement` tira `invalid syntax` → coercionar en un Code node previo, no en la expresión.
- **Webhook tras PUT estructural:** cambiar la topología de un workflow con webhook por API **no re-registra** el webhook → hay que `deactivate` + `activate`.
- **PUT de workflow:** mandar sólo `{name, nodes, connections, settings}` y limpiar `settings` (la API rechaza `availableInMCP`). `active` no se togglea por PUT (endpoints `/activate` `/deactivate`).

## 7. Estado del inventario VTR (post-batch)

8 ON = los 8 originales de producción intactos (main, staging agent, CAPI Folio, Confirmación, Estado interrumpida, Formulario, Outreach, digest). Todo lo demás OFF. 2 muertos borrados. Sin temporales de esta sesión.

## 8. Batch 2 (2026-09-21 PM) — clasificador + prompt v2.2 + W11 + W14 ✅ HECHO Y VERIFICADO

- **Clasificador `Xmyoewwa1W5gm1fy` (OFF, 5→11 nodos):** agregado `Preparar writes` (mapea rúbrica→enum GHL) + **`Set tipo_contacto`** (4sj9sWAen1PvGCkn9eCN) + **`Add nota resumen`** (POST /notes) + **`Set programa_interes` con guarda** (GET contacto → sólo escribe si está vacío; mapeo `Boarding IA→Internados`, etc.). Se conserva el tag `cualificado`. La tarea 4 `asesoria` (whitelist vieja sin `agendar-ema`) queda **sin cablear** (inerte). **Verificado:** las 3 escrituras GHL contra un contacto de prueba → PUT tipo 200, POST nota 201, PUT programa 200 (valores confirmados por GET); contacto borrado. Falta: que el main lo invoque post-conversación (wiring de W1/cutover).
- **Prompt v2.2 (Diego) en el staging `3sLd7KY3o8I7NvXi` (ON):** aplicado el delta **quirúrgico** de v2.1→v2.2 (8 ediciones: sacar a Diego, reasignar sus 2 links de Australia a **Andrés**) sobre el prompt vivo, **preservando** el `cerrar_conversacion` y la ref Nahe que el staging tiene y que v2.2 del repo NO trae (por eso NO se pisó con el archivo, se aplicó el delta). **Verificado:** Diego 7→0, `cerrar_conversacion` ✓, Nahe ✓, sigue activo, 13 nodos. Backup del prompt previo: `04_agents/agente-venttur-staging-live-backup-2026-09-21.md`. El **main de producción `[Venttur]` NO se tocó** (mantiene Diego hasta el D-day, por plan). Falta (cierre item-2 MVP): correr los 5 casos Nahe en el staging.
- **W11 `Estado lead Contestó (GHL)` (`qYgeTc9PCq3TiGDn`, NUEVO, OFF, 4 nodos):** sub-workflow paridad-1:1 del original — input `contactId` → GET contacto → guarda **forward-only** (no degrada `Cita confirmada`/`agendan_cita`) → PUT `estado_conversacion` + `ultima_actividad`. **Verificado:** guard JS syntax OK; PUT estado+fecha (DATE) contra contacto de prueba → 200, valores confirmados, contacto borrado. Falta: que el main lo invoque por inbound (wiring W1/cutover).
- **W14 `Venttur | Correo Semanal (GHL)` (`OaOyHA2tfjMtuWTk`, NUEVO, OFF, 5 nodos):** Schedule (lun 10h) → `opportunities/search` del pipeline OP·Bot → Code cuenta **citas agendadas** (etapas booked, ventana 7d) → Gmail (HTML branded). Sin Airtable. **Verificado:** lógica de conteo unit-testeada en Node (4/4: cuenta booked-en-ventana, excluye viejas/otras etapas, fallback createdAt); `pipeline_stage_id` filtra server-side (escalable); el `date` param de GHL da 400. **Open decisions (sticky en el flujo):** definición exacta de la métrica (etapas + createdAt vs cambio-de-etapa), destinatario real (hoy placeholder `[EMAIL-AGENCIA]`), paginación cuando OP·Bot supere 100 opps. OP·Bot está **vacío** hasta que el bot corra en producción → conteo real = 0 por ahora.

Snapshots de los 4 en `03_workflows/ghl-live-2026-09-21-ejecucion/` (con sha256).

## 9. Lo que sigue — registro canónico

> **`06_docs/pendientes-n8n-post-waba.md`** es la fuente única de "qué falta en n8n" (tabla flujo-por-flujo + checklist de 12 pasos). También resumido en `guia-recta-final-cutover-2026-09-16.md §21` y `guia-recta-final-ejecutable-2026-09-20.md §15`.

Resumen: W4 Formulario→GHL · W6 Confirmación agenda→GHL (⛔ calendarios) · W9 Actualizar link→GHL · W10 ingest→GHL · migración one-shot de Folios en el cutover · **wiring**: el main (W1) debe invocar clasificador + W11 + CAPI + actualizar-link, y completar el agente (splitter, audio, rama link, debounce, dedup). Varios gated por WABA.
