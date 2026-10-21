# Diseño de ejecución del protocolo de paridad — runner, matriz y crítica

**Fecha:** 2026-08-05 · **Baseline:** `hpf-inbound-handler-live-2026-08-05.json`
(`sha256 6fd484928abcd9b871a04b93b0e35bd875268fd28a3bbb22f00ce53f4ba4524e`, versionId `52bb53fc-70fd-4e55-ac5f-e7a49c442851`, 71 nodos)

Este documento respalda el plan de ejecución. Se genera **antes** de tocar una línea de código y se
committea para que sea auditable — no para que viva dentro de una sesión.

Son tres piezas producidas de forma independiente y en este orden:

1. **Runner de evidencia** — cómo se corre un caso y de dónde sale la prueba de que el lead recibió algo.
2. **Derivación de cobertura** — Matriz A (conversacional), Matriz B (topológica) y los 25 casos P0.
3. **Crítica adversarial** — un revisor cuyo único trabajo fue encontrar por qué esto vuelve a dar
   verde falso, sobre las dos piezas anteriores. Las nueve reglas anti-verde-falso del plan salen de acá.

> Las tres están ancladas en lecturas del workflow vivo, no en el protocolo. Donde el protocolo se
> equivoca, lo dicen y lo corrigen.

---

# PARTE 1 — Runner de evidencia

## Runner de evidencia HPF — diseño

Todo lo que sigue está anclado en lecturas del vivo (`/tmp/hpf_live.json`), no en el protocolo. Donde el protocolo se equivoca, lo digo.

---

## 0. Cinco hechos del vivo que redefinen el problema

Los leí del export; cambian el diseño respecto de lo que pide el protocolo.

**F1 — `contact_id` ES la dirección de entrega en los dos canales.**
```
Send Photo/Document/Video/a text message1 : chatId = {{ $('Auth + Normalize').first().json.contact_id }}
Send Message via GHL / Imagen Principal / Promo Evento : "contactId": "{{ ...contact_id }}"
```
Un `contact_id` sintético ⇒ `chat not found` en Telegram y 4xx en GHL. **Esto explica exactamente la ráfaga de 02:29-02:35: 140 partes, 140 errores, cero `message_id`.** Fue la opción (a) aplicada mal.

**F2 — `phone` se usa en UN solo lugar de los 71 nodos.** Grepeé todo: `Postgres Chat Memory.sessionKey`. No lo toca ningún emisor, ninguna tool, ningún HTTP. **`phone` es namespaceable a costo cero.**

**F3 — hay un TERCER estado, y el protocolo no lo menciona.** En `Sanitize + Split Output`:
```js
const _sd  = $getWorkflowStaticData('global');
const _cid = S(nodo('Auth + Normalize', ['contact_id'], 'anon'));
const memo = _sd.hpf[_cid] || { evento:'', grupos:[], header:false };
...
const gruposMostrados = new Set(memo.grupos || []);
if (!intenciones.productos.length) fichas = fichas.filter(e => !gruposMostrados.has(e.g));
```
Está keyed por `contact_id`, vive en la DB **interna de n8n** (`workflow_entity.staticData`), no en la Postgres "H.F" — un DELETE no lo alcanza. El export ya trae basura de la ráfaga: `"900000009":{"evento":"BODA","grupos":["pantufla","pantufla_mono","pantufla_peluche"],"header":true}`. Es el estado que gobierna *no-repetir-fichas* y *header-de-promo-una-sola-vez*, o sea justo la familia anti-loop.

Único reset in-band que existe: el marcador de saludo.
```js
if (text.indexOf('👼🏢') !== -1) {
  if (!intenciones.productos.length) { _sd.hpf[_cid] = { evento:'', grupos:[], header:false }; return SALUDO_PARTES... }
```

**F4 — `debounce_buffer` se auto-limpia, pero solo si el turno sobrevive.** `Debounce - Insert` tiene TTL propio (`now() - updated_at > interval '50 seconds'` ⇒ reemplaza en vez de append) y `Combine Messages → Debounce - Reset Buffer` deja `pending_messages='[]'`. Un turno superseded NO llega a Reset Buffer.

**F5 — `Respond to Webhook` NO corre en Telegram.** `Es Origen Telegram? (Post)[0]` está vacío; el único camino al respond en la rama real es `Es Origen Telegram? (Post)[1] → Update last_outbound_at → Respond to Webhook`. Es decir: **GHL responde 200 con el output crudo del LLM; Telegram no responde nada.** El status HTTP es telemetría, nunca veredicto. Corolario útil: como el webhook está en `responseMode: responseNode`, el POST **bloquea hasta que la ejecución termina** — cuando vuelve, ya hay runData para leer.

---

## 1. RESET — decisión

**No es una de las tres opciones: son cuatro claves de estado distintas y cada una necesita su mecanismo.**

| Clave | Store | Cómo se resetea | Garantía |
|---|---|---|---|
| `messages.session_id` = **phone** | PG "H.F" | **(a) namespace** `sess_<RUN>_<CASE>` | **dura** — memoria vacía por construcción |
| `debounce_buffer.contact_id` | PG "H.F" | **(c) sub-workflow** DELETE + SELECT de verificación | **dura, con rowcount** |
| `staticData.global.hpf[contact_id]` | DB interna de n8n | ninguno accesible | **NO se puede resetear** → se mitiga y se mide |
| customFields de la opportunity | GHL | PUT restaurando snapshot (solo lane GHL) | dura |

**(a) sí, pero solo sobre `phone`.** Por F2 es gratis y no toca la entrega. Namespear `contact_id` está **prohibido en el runner** (guard en código): rompe F1 y produce el verde falso de las 140 partes.

**(b) rechazada.** La API pública v1 de n8n no expone data de credenciales (solo `POST /credentials`, `DELETE`, `GET /credentials/schema`). Sacar la connection string exige el REST interno con cookie de owner, o la encryption key en el server. Fuera del sobre read-only + API key, y mete un secreto de producción en el disco del runner para nada: (c) da el mismo resultado sin ver la password.

**(c) elegida para `debounce_buffer`.** Un workflow **nuevo y separado** — no toca el vivo, no es re-import, no está en las prohibiciones del ANEXO B. Es la única write que el runner necesita y va con aprobación explícita de la agencia.

```
ZZ-RUNNER-RESET-HPF   (temporal, borrar post-cutover)
  Webhook POST /hpf-runner-reset  (headerAuth)
  Postgres "H.F" (uK59P60DJmOJc4Lm) — node A, executeQuery:
      DELETE FROM messages        WHERE session_id = $1;
      DELETE FROM debounce_buffer WHERE contact_id = $2;
  Postgres "H.F" — node B, executeQuery (SEPARADO, a propósito):
      SELECT (SELECT count(*) FROM messages        WHERE session_id = $1) AS messages_remaining,
             (SELECT count(*) FROM debounce_buffer WHERE contact_id = $2) AS debounce_remaining;
  Respond to Webhook (JSON)
```
Dos nodos, no un CTE: en Postgres los cambios de un CTE modificador **no son visibles** para el resto del mismo statement, así que un `WITH d AS (DELETE...) SELECT count(*)` devolvería el conteo PRE-delete y el reset se auto-certificaría en falso.

El runner exige `messages_remaining == 0 and debounce_remaining == 0`. Si no ⇒ `reset.ok=false` ⇒ **el caso nace `SIN-EVIDENCIA`, nunca verde**. Fallback sin sub-workflow (`--no-reset-wf`): phone namespeado + serialización por lane + espera hasta 51 s desde el `Debounce - Insert` del turno anterior si ese turno **no** llegó a `Debounce - Reset Buffer` (detectable en runData). En ese modo el artefacto marca `reset.debounce_probado=false` y el caso no puede ser evidencia de la familia anti-ráfaga.

### Qué garantiza y qué NO garantiza el namespace

Garantiza: `Postgres Chat Memory` arranca vacío ⇒ el LLM no arrastra nada del caso anterior. Verificable: si arrancó vacío, el turno 1 produce saludo.

**NO garantiza, y hay que decirlo en la entrega:**
1. `debounce_buffer` — clave distinta (`contact_id`), y `contact_id` está pinneado a la dirección real. Por eso hace falta (c).
2. **`staticData.hpf[contact_id]`** — clave distinta, store distinto, imposible de borrar. Dos casos consecutivos en el mismo lane comparten `memo.grupos`: el segundo puede **no** mandar una ficha que el primero ya mandó, y eso se lee como FALLA de contenido cuando es contaminación de lane.
3. La conversación visible en el chat de Telegram / GHL: contamina la revisión humana, no al bot.

Mitigación de (2), en dos capas:
- **Ledger de lane.** El runner deriva de la propia evidencia (`photo_url` → grupo del CATALOGO) qué grupos ya emitió ese lane en esta corrida. Si un assert de un caso apunta a un grupo ya emitido **y** el turno no trae intención de producto (que es la única rama donde `gruposMostrados` filtra), el caso se cierra **`SIN-EVIDENCIA (lane_state_contaminated)`** — no FALLA. Es la diferencia entre medir y culpar al bot.
- **Warm-up opcional** `needs_memo_reset: true` en el spec: turno 0 con `"Hola"`, se asserta que salieron las `SALUDO_PARTES` ⇒ eso **prueba** que se ejecutó `_sd.hpf[_cid] = {evento:'',grupos:[],header:false}`. Cuesta ~40 s; se paga solo en los casos de ficha.

---

## 2. POST + CORRELACIÓN

El POST no devuelve execution id. **No lo resolvemos por ventana de tiempo — resolvemos por token.**

`Auth + Normalize` termina con `raw: { ...b, channel }`: **cualquier key extra del body sobrevive intacta**, y además queda cruda en `Webhook - Inbound.data.main[0][0].json.body`. Inyectamos `_probe_id` único por turno:

```
probe_id = f"{case_id}#{turn_idx}#{uuid4().hex[:12]}"
```
Dos anclas independientes: `runData['Webhook - Inbound'][0]...json.body._probe_id` y `runData['Auth + Normalize'][0]...json.raw._probe_id`. Es inerte: ningún nodo lee `raw`, y GHL ya manda su standard-data completo, así que el payload sigue siendo representativo. El artefacto lo declara (`probe_injected: true`). Si la agencia lo veta, fallback: `contact_id + message_text` único + ventana `startedAt >= t0-5s` — más débil, se marca `correlacion: "heuristica"`.

**Algoritmo**
```
t0 = now_utc()
POST (timeout read=240s)          # bloquea hasta fin de ejecución (F5)
deadline = t0 + 240s
loop cada 2.5s hasta deadline:
    GET /executions?workflowId=..&limit=50          # sin data
    candidatos = [e for e in data
                  if parse(e.startedAt) >= t0 - 5s
                  and e.id not in vistos_descartados]
    for e in candidatos ordenados por startedAt:
        if e.status not in {success, error, crashed}: continue   # running/waiting → reintentar
        full = GET /executions/{e.id}?includeData=true
        if probe_de(full) == probe_id: return full
        vistos_descartados.add(e.id)
return None
```
Costo real: con N lanes, los candidatos por poll son ≤ N+2 (la ventana `>= t0` los recorta). 50 turnos × ~2 GET-con-data = 100 requests. Trivial.

**Los tres casos borde, cada uno con salida propia:**

| Situación | Detección | Estado |
|---|---|---|
| **Superseded** (el turno murió en `Es El Ultimo Mensaje?[1]`, sumidero) | la ejecución existe, `status=success`, `runData` tiene `Es El Ultimo Mensaje?` pero **no** `Combine Messages` ni emisores | `SIN-EVIDENCIA (superseded)` — **nunca FALLA**. Es el "el bot no contestó" que manda a diagnosticar el bug equivocado. |
| **Ejecución no aparece** en 240 s | poll agotado | `SIN-EVIDENCIA (execution_not_found)` |
| **`status=error`** | `resultData.error` | se extrae igual lo que haya, `SIN-EVIDENCIA (execution_error)` + `error.message` en el artefacto |

Reintentos: el POST **no se reintenta jamás** en automático. Un POST duplicado dispara el debounce y mata la ejecución anterior. Ante `ConnectionError`/timeout de socket el runner **igual corre la correlación** (la ejecución probablemente arrancó) y solo si tampoco aparece marca `SIN-EVIDENCIA`. `--retry-turn` es manual y explícito.

**Caso ráfaga** (tipo de turno `burst`): K POSTs concurrentes con gaps de ~1 s, K probe_ids. Asserts propios: exactamente **una** ejecución con emisores; K-1 en `superseded`; y `Combine Messages.output.message_text == "\n".join(textos)`. Es la única forma de verificar el debounce de verdad, y se apoya en el sumidero en vez de tropezarse con él.

---

## 3. EXTRACCIÓN DE EVIDENCIA

**Nivel de evidencia: A′ (A-prime).** Payload real del emisor **+ acuse real del canal**, obtenido 100% por lectura. Es estrictamente ≥ nivel A del protocolo: `hpf_outbound_log` daría `http_status`, esto da el `message_id` de Telegram/GHL. Y no exige editar el vivo.

### Regla dura de bytes
`contiene_verbatim` corre **siempre sobre `enviado`** (el item de `Loop Message Parts`), **nunca sobre el eco del canal**. Telegram recorta whitespace de borde en el mensaje que devuelve: comparar contra el eco destruiría en silencio justo el NBSP y los dobles espacios que se están midiendo. El eco se usa solo para (i) `message_id` y (ii) cross-check blando.

`message_part` se persiste **duplicado**: `message_part` (legible) y `message_part_b64` + `sha256` (**autoritativo**). Los asserts decodifican el b64. Ningún editor, ningún markdown, ningún `json.dumps` puede mutar la paridad sin que cambie el sha.

### De dónde sale cada cosa

- **`enviado` por parte** → `runData['Loop Message Parts'][k].data.main[1][0].json` = `{message_part, photo_url, doc_url, video_url}`. `k` = índice de parte, canónico.
- **Emisor ↔ parte**: se camina `taskData.source[0].{previousNode, previousNodeRun}` hacia atrás hasta `Loop Message Parts`; ese `previousNodeRun` es `k`. (`previousNodeRun` ausente = 0.) Los emisores del post-chain se excluyen del walk — su source llega al último run del loop y daría un índice falso; se indexan `post.0` / `post.1`.
- **`acuse`** → output del emisor. Telegram: `message_id`, `chat.id`, `text`/`caption`, `photo[]`/`document`/`video`. GHL: `messageId`, `conversationId`.
- **Errores — el detalle que se come a un runner ingenuo:** los 7 emisores tienen `onError: "continueRegularOutput"` (lo verifiqué nodo por nodo). Un fallo **no** aparece en `taskData.error`: aparece como **item de salida** `{json:{error:...}}`, y `executionStatus` queda `"success"`. Hay que chequear **las dos** ubicaciones. Es literalmente el mecanismo por el que 140 `chat not found` convivieron con `status="success"`.
- **`intermediateSteps`** → `runData['Vendedor (LLM Agent)'][0].data.main[0][0].json.intermediateSteps[*].action.tool`.
- **Sumideros** → presencia/ausencia de nodos en runData: `Es El Ultimo Mensaje?` sin `Combine Messages`; `Es Origen Telegram? (Post)` sin `Update last_outbound_at`.

### Esquema del artefacto — `evidence/<RUN_ID>/<CASE_ID>.json`

```jsonc
{
  "schema": "hpf-evidence/1",
  "run_id": "2026-08-05T14-02-11Z_a3f9",
  "case_id": "HPF-PROD-007",
  "intencion": "PARIDAD|DELTA|NO-REPLICAR",
  "gravedad": "SEV1|SEV2|SEV3",            // renombrado, ver §8
  "oraculo": { "grado": "OBSERVADO|CSV|REGLA|JUICIO|INFERIDO",
               "fuente": "07_testing/oraculo/sample_9.md#T6" },
  "canal": "telegram|ghl",
  "nivel_evidencia": "A-prime",            // "C" ⇒ el caso NO puede cerrar en PASA
  "baseline": { "workflow_id":"IPO1c36NLzkXrBh9", "versionId":"…",
                "sha256_export":"…", "cambio_de_baseline_durante_la_corrida": false },
  "lane": { "id":"TG-1", "contact_id":"7412345678",
            "opportunity_id":"tg_opp_7412345678",
            "phone":"sess_a3f9_HPF-PROD-007",
            "grupos_previos_en_lane":["sandalia"] },
  "reset": {
    "estrategia":"phone-namespace + reset-wf",
    "phone_namespaced": true,
    "messages_remaining": 0, "debounce_remaining": 0,
    "staticdata_memo": { "reseteable": false,
                         "mitigacion": "warmup-saludo|lane-ledger",
                         "warmup_saludo_confirmado": true },
    "ghl_opportunity_restaurada": null,
    "ok": true, "detalle": ""
  },
  "turnos": [{
    "idx": 1, "tipo": "single|burst",
    "probe_id": "HPF-PROD-007#1#7c1d0a…", "probe_injected": true,
    "enviado": { "payload": { /* body exacto */ }, "ts_post": "…Z" },
    "http": { "status": null, "elapsed_ms": 37412, "body_len": 0, "body_sha256": null,
              "nota": "Telegram no ejecuta Respond to Webhook (topologia)" },
    "execution": { "id":"51221", "status":"success", "startedAt":"…","stoppedAt":"…",
                   "found_after_ms": 2100, "superseded": false, "correlacion":"probe_id" },
    "agente": { "output_len": 812, "output_sha256":"…",
                "tools": ["MOSTRAR_PRODUCTOS"],
                "intermediate_steps": [
                  {"tool":"MOSTRAR_PRODUCTOS","tool_input":{"productos":"sandalias"},
                   "observation_len":140,"observation_sha256":"…"}] },
    "partes": [{
      "idx": 0, "loop_run": 0,
      "emisor": "Send Photo (Telegram)", "emisor_run": 0,
      "enviado": { "message_part":"✨ Sandalia…",
                   "message_part_b64":"4pyoIFNhbmRhbGlh…",
                   "message_part_sha256":"…", "message_part_bytes": 312,
                   "photo_url":"https://assets.cdn.filesafe.space/…jpeg",
                   "doc_url":"", "video_url":"" },
      "acuse": { "ok": true, "message_id": 8842, "chat_id": 7412345678,
                 "echo_caption_b64":"…", "echo_text_b64": null,
                 "file_id":"AgACAgEAAx…", "raw_keys":["message_id","from","chat","date","photo","caption"] },
      "error": null, "duracion_ms": 940
    }],
    "post_chain": { "corrio": false, "send_imagen_principal": null, "send_promo_evento": null },
    "nodos_corridos": { "Sanitize + Split Output":1, "Loop Message Parts":5,
                        "Debounce - Reset Buffer":1 },
    "sumideros": { "es_el_ultimo_mensaje_false": false, "post_salida_0_vacia": true }
  }],
  "asserts": [{
    "id":"A1", "primitiva":"contiene_verbatim", "gravedad":"SEV2",
    "args": { "needle_b64":"…", "scope":"turnos[1].partes[2].enviado" },
    "resultado":"FALLA", "evaluable": true, "motivo_no_evaluable": null,
    "detalle": { "primer_byte_divergente": 181,
                 "esperado_hex":"20 20 f0 9f 98 8a",
                 "obtenido_hex":"20 f0 9f 98 8a",
                 "esperado_ctx":"…gracias  😊", "obtenido_ctx":"…gracias 😊" }
  }],
  "estado": "PASA|FALLA|PARCIAL|SIN-EVIDENCIA|BLOQUEADO-POR-CANAL",
  "motivo": "A1 FALLA: falta el doble espacio antes del 😊",
  "ts_cierre": "2026-08-05T14:03:02Z",
  "raw_sidecar": "evidence/2026-…_a3f9/HPF-PROD-007.raw.json.gz"
}
```

El sidecar `.raw.json.gz` guarda el runData recortado de `Webhook - Inbound`, `Auth + Normalize`, `Vendedor (LLM Agent)`, `Sanitize + Split Output`, `Loop Message Parts`, `Combine Messages` y los 7 emisores. **Es imprescindible**: hay 1488 ejecuciones retenidas y n8n las va a podar; el execution id es un puntero que caduca, el artefacto es la evidencia de registro (regla 3 del protocolo).

---

## 4. ASSERTS

Primitivas, todas sobre bytes UTF-8, **cero normalización** (no `.strip()`, no `unicodedata.normalize`, no colapso de espacios):

| Primitiva | Semántica |
|---|---|
| `contiene_verbatim(needle, scope)` | `needle.encode() in haystack_bytes` |
| `no_contiene(needle, scope)` | negación |
| `orden_de_partes([n1,n2,…])` | índices de primera aparición estrictamente crecientes |
| `cantidad_de_partes(op, n)` | `==`/`>=`/`<=`/`between` sobre `len(partes)` |
| `tool_invocada(nombre)` | `nombre in [s["tool"] for s in intermediate_steps]` — **igualdad de string** |
| `tool_no_invocada(nombre)` | negación (cubre las 7 filas NO-REPLICAR: p.ej. `ATENCION_PERSONALIZADA` no debe invocarse al pedir catálogo) |
| `emisor_usado(nombre, parte_idx)` | prueba que la foto salió como foto y no como URL en texto |
| `entrega_ok()` | **todas** las partes con emisor tienen `acuse.ok and message_id is not None` |
| `sin_repeticion(grupo)` | el grupo no aparece dos veces en el mismo turno/caso |

`tool_invocada` nunca toca `json.dumps`. Ese es el bug del `test-hpf-webhook.py`: `steps_have_tool()` serializa y busca substring, con lo cual matchea el texto de un error 404 de GHL o el argumento de otra tool.

**Assert que falla vs. assert no evaluable — son campos distintos, no dos valores del mismo campo:**

```jsonc
// FALLA — se evaluó y dio negativo. Lleva diff de bytes obligatorio.
{ "id":"A1","primitiva":"contiene_verbatim","resultado":"FALLA","evaluable":true,
  "detalle":{"primer_byte_divergente":181,"esperado_hex":"20 20 f0 9f 98 8a",
             "obtenido_hex":"20 f0 9f 98 8a"} }

// NO-EVALUABLE — no hubo sobre qué evaluar. Nunca cuenta como verde ni como rojo.
{ "id":"A4","primitiva":"tool_invocada","resultado":"NO-EVALUABLE","evaluable":false,
  "motivo_no_evaluable":"returnIntermediateSteps ausente en el output del agente",
  "detalle":null }

{ "id":"A2","primitiva":"entrega_ok","resultado":"NO-EVALUABLE","evaluable":false,
  "motivo_no_evaluable":"ejecucion superseded: murio en Es El Ultimo Mensaje?[1]" }
```

Motivos cerrados de `NO-EVALUABLE`: `execution_not_found` · `superseded` · `execution_error` · `zero_parts` · `intermediate_steps_missing` · `lane_state_contaminated` · `canal_bloqueado` · `reset_failed`.

---

## 5. ESTADOS + escritura incremental

Derivación **determinista**, sin criterio humano, en este orden:

```python
if art["nivel_evidencia"] == "C":            return "SIN-EVIDENCIA"   # antipatrón 1, lock en código
if caso.canal_bloqueado:                     return "BLOQUEADO-POR-CANAL"
if not art["reset"]["ok"]:                   return "SIN-EVIDENCIA"
if any(t["execution"] is None or t["execution"]["superseded"]
       or t["execution"]["status"] != "success" for t in turnos):
                                             return "SIN-EVIDENCIA"
if any(a["resultado"] == "NO-EVALUABLE" for a in asserts):
                                             return "SIN-EVIDENCIA"
if all(a["resultado"] == "PASA" for a in asserts):
                                             return "PASA"          # entrega_ok es un assert obligatorio
if all(a["resultado"] == "PASA" for a in asserts if a["gravedad"] in ("SEV1","SEV2")):
                                             return "PARCIAL"       # solo SEV3 en rojo
                                             return "FALLA"
```
No existe `PENDIENTE`. `entrega_ok` se inyecta como assert obligatorio en todo caso no bloqueado ⇒ **no hay PASA sin `message_id`**.

**Persistencia — sobrevive a que se corte la sesión:**
1. `evidence/<RUN>/<CASE>.json` escrito atómico (`.tmp` → `os.replace`) apenas cierra el caso.
2. Una línea a `ESTADO.jsonl` (append-only, `flush` + `os.fsync`).
3. `MATRIZ.md` y `ESTADO.md` **se reconstruyen leyendo el directorio de evidencia**, no la memoria del proceso. Un `kill -9` pierde como mucho el caso en vuelo.
4. Al arrancar: escanea `evidence/`, saltea casos con JSON completo salvo `--redo`.
5. `MATRIZ.md` tiene el denominador congelado como **entrada** (`casos.yaml`). El runner **solo rellena** `estado` / `evidencia` / `nivel`. Si aparece un caso en evidencia que no está en el spec ⇒ aborta. Si un caso del spec no tiene evidencia al cierre ⇒ se escribe `SIN-EVIDENCIA`, jamás se omite. Así la regla 2 del protocolo es mecánica, no disciplina.

También: el runner hace `GET /workflows/{id}` al inicio y al cierre, guarda `versionId` + sha256. Si el `versionId` cambió a mitad, marca `cambio_de_baseline_durante_la_corrida: true` en todos los artefactos posteriores y lo grita en `ESTADO.md`.

---

## 6. PARALELIZACIÓN Y RELOJ

**La unidad de paralelismo es el LANE = una dirección de entrega real**, no el caso. Por F1 no se pueden inventar lanes.

Presupuesto por turno, medido contra la topología:

| Tramo | s |
|---|---|
| `Auth + Normalize` + `Buscar Opportunity Real` (GHL search, corre también en Telegram) | 1.0 |
| **`Wait 15s (Debounce)`** (piso fijo) | 15.0 |
| `Debounce - Check` + `Combine` + `Switch` | 0.5 |
| `Vendedor (LLM Agent)` — 28.4 KB de system prompt, 5 tools, memoria; ~1 tool call (33/40 ejecuciones medidas) | 13.0 |
| Loop: 3.5 partes/turno medidas (140/40) → 4 × (`Wait 1.5s` + ~0.5 emisor) | 8.0 |
| overhead del runner: poll de correlación + `includeData` | 4.0 |
| **T_turno típico** | **≈ 41.5 s** |
| T_turno ficha-heavy (9 partes con foto+pdf+video) | ≈ 60 s |
| T_turno GHL con `evento_reciente` (+ `Wait 2s (Imagen)` + 2 emisiones) | +3 s |

Constante de planificación: **T = 45 s/turno**.

25 casos × 2 turnos = **50 turnos**.

| N lanes | wall-clock corrida completa | + cola ficha-heavy |
|---|---|---|
| 1 | 37.5 min | ~45 min |
| 2 | 18.8 min | ~24 min |
| **3** | **12.5 min** | **~18 min** |
| 4 | 9.4 min | ~15 min |
| 6 | 6.3 min | ~13 min (domina la cola) |

Núcleo de regresión (8 casos × 2 corridas = 32 turnos): 24 min serial, **8 min con N=3**.

**Recomendación: N = 3.** Razones, en orden:
1. Es el N donde el reloj deja de ser el cuello de botella (18 min de 180 disponibles en Fase 2); de ahí en adelante el límite es el diagnóstico, no la máquina.
2. Cada lane extra hay que **provisionarlo a mano**: 3 chat_ids reales de Telegram son baratos (1 DM + 2 supergrupos con el bot adentro — cada grupo da un `chat.id` distinto y entrega real) y 2-3 contactos GHL con opportunity en el pipeline. A partir de 4-5 el costo de setup supera el ahorro.
3. Más lanes = más superficie del estado compartido `staticData` que no se puede resetear; con 3 el ledger de lane sigue siendo auditable a ojo.
4. N=1 es el fallback si solo hay un chat real: 45 min, sigue entrando.

**Invariantes de concurrencia (no negociables):**
- **Un turno en vuelo por lane, siempre.** Dos turnos concurrentes sobre el mismo `contact_id` colisionan en `debounce_buffer` y uno mata al otro en `Es El Ultimo Mensaje?[1]`.
- Un caso corre **entero** en un lane (mismo `contact_id`, mismo `phone`).
- Entre casos del mismo lane: reset + verificación. Si el turno previo no llegó a `Debounce - Reset Buffer`, además dormir hasta 51 s desde su `Debounce - Insert` (regla del TTL, F4).
- `threading` con un worker por lane. I/O bloqueante puro, no hace falta asyncio.
- Techo externo real: la concurrencia de workers de n8n (los `Wait` retienen slot) y el TPM de la cuenta OpenAI. Con N=3 y ~10k tokens de prompt no se toca ninguno.

---

## 7. EL MISMO RUNNER CONTRA LA RAMA GHL

Lo único que cambia en el input es **el prefijo del `opportunity_id`**: la rama la decide `is_telegram_test = opportunity_id.startsWith('tg_opp_')`, no el campo `channel`.

| | Telegram | GHL |
|---|---|---|
| `opportunity_id` | `tg_opp_<chat_id>` | id real de la opportunity |
| `contact_id` | chat_id real | contact id real de GHL |
| `channel` derivado | `telegram` | `whatsapp` |
| emisores por parte | 4 (`¿Parte con foto?`→`documento?`→`video?`→texto) | **1** (`Send Message via GHL`, media va en `attachments[]`) |
| post-chain | **no corre** (`Post[0]` vacío) | corre: `Update last_outbound_at`, `Get Current Opportunity`, `Check Evento Just Set`, `Evento Recien Identificado?`, `Send Imagen Principal`, `Wait 2s`, `Send Promo Evento` |
| `Respond to Webhook` | no ejecuta | ejecuta, body = output crudo del LLM |
| acuse | `message_id`, `chat.id`, `photo[].file_id` | `messageId`, `conversationId` |
| estado de negocio | `Buscar Opportunity Real` no encuentra ⇒ `custom_fields` vacío siempre | encuentra ⇒ `Mapear Custom Fields` devuelve estado real |

Cambios concretos en la extracción:
1. **Dos partes extra sin `loop_run`.** `Send Imagen Principal` y `Send Promo Evento` se indexan `post.0`/`post.1`; su `enviado` **no** sale del loop sino de `runData['Check Evento Just Set'][0]...json` → `{descripcion, imagenUrl, promoText}` (el nodo cuya salida es literalmente el payload). Son el **segundo emisor de la imagen de catálogo** y sólo existen acá: un gate cerrado al 95% sobre Telegram no los toca nunca.
2. **`emisor_usado("Send Photo (Telegram)")` es N/A en GHL** — se marca `NO-EVALUABLE (canal)`, no FALLA. En GHL la equivalencia es `attachments` no vacío en el body de la request.
3. **Reset agrega una clave**: snapshot `GET /opportunities/{id}` antes de la corrida y `PUT` restaurando `customFields` + `pipelineStageId` entre casos. Sin eso, `evento_detectado` / `productos_mostrados` / `cotizacion_emitida` arrastran y **el anti-loop da verde por contaminación** — que es exactamente el antipatrón 4, movido de tabla.
4. **`custom_fields` del payload es input de test de primera clase.** `Check Evento Just Set` calcula `justSet = (!incomingEvento) && currentEvento`, y `incomingEvento` viene del body. Default `{}` (fiel a producción, que es lo observado); si un caso lo sobrescribe, el artefacto marca `custom_fields_injected: true` y **baja el grado de oráculo a `REGLA`**.
5. **Se desbloquea la familia entera** que el protocolo manda marcar `BLOQUEADO-POR-CANAL`: `productos_mostrados`, `evento_detectado`, `cotizacion_emitida`, anti-loop, dedup, imagen-una-sola-vez, 7-pasos-una-sola-vez. Con `--canal ghl` esos casos pasan a evaluables. Es la razón por la que la lane GHL vale más que la de Telegram, y si no llega a correr va en la primera línea de la entrega.

---

## 8. Colisión de IDs

El protocolo usa `S1/S2/S3` como **severidad**; `resultados-fase2-2026-07-24.md` los usa como **casos de envío**. Renombrar la severidad a **`SEV1` / `SEV2` / `SEV3`** (no a `G1/G2/G3`: chocaría con los gates `G0..G3`). Los casos de envío conservan `S1/S2/S3`. El gate G3 pasa a leerse "cero casos **SEV1** en rojo".

---

## 9. Esqueleto de código

`scripts/testing/hpf-runner-evidencia.py`

```python
#!/usr/bin/env python3
"""
hpf-runner-evidencia.py — Runner de evidencia del protocolo de paridad HPF.

Nivel de evidencia: A-prime (payload del emisor + acuse del canal, leidos de runData).
NUNCA normaliza strings. NUNCA usa channel="test" como gate. NUNCA marca PASA sin message_id.

Env:
  HPF_N8N_API_BASE   HPF_N8N_API_KEY   HPF_N8N_WORKFLOW_ID
  HPF_WEBHOOK_URL    HPF_WEBHOOK_AUTH_HEADER_NAME   HPF_WEBHOOK_AUTH_HEADER_VALUE
  HPF_RESET_WEBHOOK_URL   HPF_RESET_AUTH_HEADER_VALUE      (opcional: --no-reset-wf)
  HPF_GHL_PIT   HPF_GHL_LOCATION_ID                        (solo lanes ghl)
"""
import os, sys, json, gzip, time, uuid, base64, hashlib, argparse, threading, queue
import datetime as dt
from collections import defaultdict
import requests, yaml

UTC = dt.timezone.utc
def now(): return dt.datetime.now(UTC)
def iso(t): return t.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
def sha(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def b64(s: str) -> str: return base64.b64encode(s.encode("utf-8")).decode("ascii")
def unb64(s: str) -> bytes: return base64.b64decode(s)

# ─── Topologia del vivo (constantes, NO se infieren en runtime) ──────────────
WF_ID          = os.environ.get("HPF_N8N_WORKFLOW_ID", "IPO1c36NLzkXrBh9")
N_WEBHOOK      = "Webhook - Inbound"
N_AUTH         = "Auth + Normalize"
N_AGENT        = "Vendedor (LLM Agent)"
N_SANITIZE     = "Sanitize + Split Output"
N_LOOP         = "Loop Message Parts"
N_COMBINE      = "Combine Messages"
N_LAST         = "Es El Ultimo Mensaje?"
N_RESET_BUF    = "Debounce - Reset Buffer"
N_EVENTO       = "Check Evento Just Set"

EMISORES_PARTE = {                       # emisor -> tipo de acuse
    "Send Photo (Telegram)":    "telegram",
    "Send Document (Telegram)": "telegram",
    "Send Video (Telegram)":    "telegram",
    "Send a text message1":     "telegram",
    "Send Message via GHL":     "ghl",
}
EMISORES_POST  = {"Send Imagen Principal": "ghl", "Send Promo Evento": "ghl"}
EMISORES       = {**EMISORES_PARTE, **EMISORES_POST}   # los 7

T_TURNO_S      = 45      # constante de planificacion
POLL_S         = 2.5
POST_TIMEOUT_S = 240
CORR_TIMEOUT_S = 240
DEBOUNCE_TTL_S = 51      # Debounce - Insert: now() - updated_at > interval '50 seconds'


# ═══ 1. RESET ════════════════════════════════════════════════════════════════
class ResetError(Exception): pass

def reset_precondicion(cfg, lane, phone, prev_turn_meta):
    """Precondicion DURA. Devuelve dict de evidencia; si falla -> ResetError."""
    ev = {"estrategia": "phone-namespace + reset-wf" if cfg.reset_wf else "phone-namespace + ttl",
          "phone_namespaced": True, "messages_remaining": None, "debounce_remaining": None,
          "staticdata_memo": {"reseteable": False, "mitigacion": "lane-ledger",
                              "warmup_saludo_confirmado": None},
          "ghl_opportunity_restaurada": None, "ok": False, "detalle": ""}

    # (a) phone: namespace descartable. GARANTIZA messages vacio por construccion.
    #     PROHIBIDO namespear contact_id: es la direccion de entrega (chatId / GHL contactId).
    assert lane.contact_id and not lane.contact_id.startswith("11300000"), \
        "contact_id sintetico => 'chat not found'. Usar la direccion real."

    # (c) debounce_buffer: sub-workflow separado, con verificacion por rowcount.
    if cfg.reset_wf:
        r = requests.post(cfg.reset_url, json={"session_id": phone, "contact_id": lane.contact_id},
                          headers={cfg.reset_hdr_name: cfg.reset_hdr_val}, timeout=30)
        if r.status_code != 200:
            raise ResetError(f"reset-wf HTTP {r.status_code}: {r.text[:200]}")
        d = r.json()
        d = d[0] if isinstance(d, list) else d
        ev["messages_remaining"] = int(d["messages_remaining"])
        ev["debounce_remaining"] = int(d["debounce_remaining"])
        if ev["messages_remaining"] or ev["debounce_remaining"]:
            raise ResetError(f"reset no dejo limpio: {d}")
    else:
        # Fallback: el TTL de Debounce - Insert limpia solo, pero SOLO si pasaron >50s
        # desde el insert del turno anterior Y ese turno no llego a Debounce - Reset Buffer.
        if prev_turn_meta and not prev_turn_meta.get("llego_a_reset_buffer"):
            esperar = DEBOUNCE_TTL_S - (now() - prev_turn_meta["ts_insert"]).total_seconds()
            if esperar > 0: time.sleep(esperar)
        ev["detalle"] = "debounce no probado por rowcount (modo --no-reset-wf)"

    # (d) GHL: restaurar customFields + stage desde snapshot
    if lane.canal == "ghl":
        ev["ghl_opportunity_restaurada"] = ghl_restore_opportunity(cfg, lane)

    # staticData.global.hpf[contact_id] NO es reseteable: se mitiga, no se resuelve.
    ev["staticdata_memo"]["grupos_previos_en_lane"] = sorted(lane.ledger_grupos)
    ev["ok"] = True
    return ev


# ═══ 2. POST + CORRELACION ═══════════════════════════════════════════════════
def post_turno(cfg, lane, phone, case_id, turn_idx, msg, custom_fields=None, extra=None):
    probe = f"{case_id}#{turn_idx}#{uuid.uuid4().hex[:12]}"
    payload = {
        "contact_id":     lane.contact_id,             # = chatId / GHL contactId. REAL.
        "opportunity_id": lane.opportunity_id,         # prefijo tg_opp_ => rama Telegram
        "phone":          phone,                       # = sessionKey de Postgres Chat Memory
        "message_type":   "text",
        "message_text":   msg,
        "stage":          lane.stage,
        "custom_fields":  custom_fields or {},
        "_probe_id":      probe,                       # sobrevive en Auth+Normalize.raw
    }
    if extra: payload.update(extra)
    hdrs = {"Content-Type": "application/json", cfg.hdr_name: cfg.hdr_val}
    t0, http = now(), {"status": None, "elapsed_ms": None, "body_len": 0,
                       "body_sha256": None, "nota": None}
    try:
        r = requests.post(cfg.webhook_url, json=payload, headers=hdrs, timeout=(10, POST_TIMEOUT_S))
        http.update(status=r.status_code, body_len=len(r.content),
                    body_sha256=sha(r.content) if r.content else None)
    except requests.RequestException as e:
        # NO se reintenta el POST: un duplicado dispara el debounce y mata la ejecucion previa.
        http["nota"] = f"transporte: {type(e).__name__}: {e}"
    http["elapsed_ms"] = int((now() - t0).total_seconds() * 1000)
    if lane.canal == "telegram":
        http["nota"] = (http["nota"] or "") + " | Telegram no ejecuta Respond to Webhook (topologia)"
    return probe, payload, http, t0


def probe_de(full):
    rd = (full.get("data") or {}).get("resultData", {}).get("runData", {})
    for node, path in ((N_WEBHOOK, ("body", "_probe_id")), (N_AUTH, ("raw", "_probe_id"))):
        try:
            j = rd[node][0]["data"]["main"][0][0]["json"]
            for k in path: j = j[k]
            return j
        except Exception:
            continue
    return None


def correlacionar(cfg, probe, t0, deadline_s=CORR_TIMEOUT_S):
    """Devuelve (full_execution | None, motivo). Sin ventanas ambiguas: por token."""
    descartados, deadline = set(), t0 + dt.timedelta(seconds=deadline_s)
    while now() < deadline:
        lst = api_get(cfg, "/executions", params={"workflowId": WF_ID, "limit": 50}).get("data", [])
        cand = [e for e in lst
                if e["id"] not in descartados
                and dt.datetime.fromisoformat(e["startedAt"].replace("Z", "+00:00")) >= t0 - dt.timedelta(seconds=5)]
        for e in sorted(cand, key=lambda x: x["startedAt"]):
            if e.get("status") not in ("success", "error", "crashed"):
                continue                                   # running/waiting: reintentar
            full = api_get(cfg, f"/executions/{e['id']}", params={"includeData": "true"})
            if probe_de(full) == probe:
                return full, None
            descartados.add(e["id"])
        time.sleep(POLL_S)
    return None, "execution_not_found"


# ═══ 3. EXTRACCION ═══════════════════════════════════════════════════════════
def out_items(td):
    try:    return td["data"]["main"][0] or []
    except Exception: return []

def loop_part(rd, k):
    """Item de la parte k = output 'loop' (main[1]) del run k de splitInBatches."""
    try:    return rd[N_LOOP][k]["data"]["main"][1][0]["json"]
    except Exception: return None

def walk_a_loop(rd, node, run):
    """Camina taskData.source hacia atras hasta Loop Message Parts. Devuelve el run del loop."""
    seen = 0
    while seen < 12:
        try: src = rd[node][run]["source"][0]
        except Exception: return None
        prev, prun = src.get("previousNode"), src.get("previousNodeRun") or 0
        if prev == N_LOOP: return prun
        node, run, seen = prev, prun, seen + 1
    return None

def acuse_de(td, kind):
    """OJO: los 7 emisores tienen onError=continueRegularOutput. Un fallo NO va a
       taskData.error: sale como item {json:{error:...}} con executionStatus='success'."""
    if td.get("executionStatus") == "error" or td.get("error"):
        e = td.get("error") or {}
        return {"ok": False}, {"fuente": "taskData.error",
                               "message": e.get("message") or str(e)[:400]}
    items = out_items(td)
    if not items: return {"ok": False}, {"fuente": "sin_output", "message": None}
    j = items[0].get("json", {})
    if "error" in j:
        e = j["error"]
        return {"ok": False}, {"fuente": "output.error",
                               "message": e if isinstance(e, str) else json.dumps(e, ensure_ascii=False)[:400]}
    if kind == "telegram":
        return {"ok": j.get("message_id") is not None, "message_id": j.get("message_id"),
                "chat_id": (j.get("chat") or {}).get("id"),
                "echo_text_b64": b64(j["text"]) if isinstance(j.get("text"), str) else None,
                "echo_caption_b64": b64(j["caption"]) if isinstance(j.get("caption"), str) else None,
                "raw_keys": sorted(j.keys())}, None
    mid = j.get("messageId") or (j.get("messageIds") or [None])[0]
    return {"ok": mid is not None, "message_id": mid,
            "conversation_id": j.get("conversationId"), "raw_keys": sorted(j.keys())}, None


def extraer_turno(full, canal):
    rd = (full.get("data") or {}).get("resultData", {}).get("runData", {})
    t = {"execution": {"id": str(full["id"]), "status": full.get("status"),
                       "startedAt": full.get("startedAt"), "stoppedAt": full.get("stoppedAt"),
                       "superseded": False, "correlacion": "probe_id"},
         "agente": {}, "partes": [], "post_chain": {"corrio": False},
         "nodos_corridos": {k: len(v) for k, v in rd.items()},
         "sumideros": {}}

    # sumidero silencioso: murio en Es El Ultimo Mensaje?[1]
    t["sumideros"]["es_el_ultimo_mensaje_false"] = (N_LAST in rd and N_COMBINE not in rd)
    t["execution"]["superseded"] = t["sumideros"]["es_el_ultimo_mensaje_false"]
    t["sumideros"]["post_salida_0_vacia"] = (canal == "telegram")

    # agente: intermediateSteps -> action.tool por IGUALDAD. Jamas json.dumps.
    try:
        aj = rd[N_AGENT][0]["data"]["main"][0][0]["json"]
        steps = aj.get("intermediateSteps") or []
        t["agente"] = {
            "output_len": len(aj.get("output") or ""),
            "output_sha256": sha((aj.get("output") or "").encode("utf-8")),
            "tools": [ (s.get("action") or {}).get("tool") for s in steps ],
            "intermediate_steps": [{
                "tool": (s.get("action") or {}).get("tool"),
                "tool_input": (s.get("action") or {}).get("toolInput"),
                "observation_len": len(str(s.get("observation") or "")),
                "observation_sha256": sha(str(s.get("observation") or "").encode("utf-8")),
            } for s in steps],
        }
    except Exception:
        t["agente"] = {"tools": None, "intermediate_steps": None,
                       "nota": "returnIntermediateSteps ausente"}

    # partes: enviado desde Loop Message Parts (bytes crudos), acuse desde el emisor
    for emisor, kind in EMISORES_PARTE.items():
        for run, td in enumerate(rd.get(emisor, [])):
            k = walk_a_loop(rd, emisor, run)
            p = loop_part(rd, k) if k is not None else None
            mp = (p or {}).get("message_part", "")
            ac, err = acuse_de(td, kind)
            t["partes"].append({
                "idx": k, "loop_run": k, "emisor": emisor, "emisor_run": run,
                "enviado": {"message_part": mp, "message_part_b64": b64(mp),
                            "message_part_sha256": sha(mp.encode("utf-8")),
                            "message_part_bytes": len(mp.encode("utf-8")),
                            "photo_url": (p or {}).get("photo_url", ""),
                            "doc_url":   (p or {}).get("doc_url", ""),
                            "video_url": (p or {}).get("video_url", "")},
                "acuse": ac, "error": err,
                "duracion_ms": td.get("executionTime")})
    t["partes"].sort(key=lambda x: (x["idx"] is None, x["idx"]))

    # post-chain (SOLO rama GHL). Su 'enviado' sale de Check Evento Just Set, no del loop.
    if any(e in rd for e in EMISORES_POST):
        t["post_chain"]["corrio"] = True
        try:    cej = rd[N_EVENTO][0]["data"]["main"][0][0]["json"]
        except Exception: cej = {}
        for i, (emisor, campo, url_campo) in enumerate(
                [("Send Imagen Principal", "descripcion", "imagenUrl"),
                 ("Send Promo Evento",     "promoText",   None)]):
            for run, td in enumerate(rd.get(emisor, [])):
                txt = cej.get(campo, "") or ""
                ac, err = acuse_de(td, "ghl")
                t["partes"].append({
                    "idx": f"post.{i}", "loop_run": None, "emisor": emisor, "emisor_run": run,
                    "enviado": {"message_part": txt, "message_part_b64": b64(txt),
                                "message_part_sha256": sha(txt.encode("utf-8")),
                                "message_part_bytes": len(txt.encode("utf-8")),
                                "photo_url": cej.get(url_campo, "") if url_campo else "",
                                "doc_url": "", "video_url": ""},
                    "acuse": ac, "error": err, "duracion_ms": td.get("executionTime")})
                t["post_chain"][emisor] = ac
    return t, rd


# ═══ 4. ASSERTS ══════════════════════════════════════════════════════════════
def _pasa(a, **d): return {**a, "resultado": "PASA", "evaluable": True,
                           "motivo_no_evaluable": None, "detalle": d or None}
def _falla(a, **d): return {**a, "resultado": "FALLA", "evaluable": True,
                            "motivo_no_evaluable": None, "detalle": d}
def _noeval(a, motivo): return {**a, "resultado": "NO-EVALUABLE", "evaluable": False,
                                "motivo_no_evaluable": motivo, "detalle": None}

def _partes(turnos, scope):
    ts = turnos if scope.get("turno") is None else [turnos[scope["turno"] - 1]]
    ps = [p for t in ts for p in t["partes"]]
    if scope.get("parte") is not None: ps = [p for p in ps if p["idx"] == scope["parte"]]
    return ps

def _diff(esp: bytes, obt: bytes):
    i = next((i for i in range(min(len(esp), len(obt))) if esp[i] != obt[i]), min(len(esp), len(obt)))
    ctx = lambda b: " ".join(f"{x:02x}" for x in b[max(0, i - 3): i + 3])
    return {"primer_byte_divergente": i, "esperado_hex": ctx(esp), "obtenido_hex": ctx(obt)}

def as_contiene_verbatim(a, turnos):
    """SIN normalizar: ni strip, ni colapso de espacios, ni unicodedata.normalize."""
    ps = _partes(turnos, a["args"].get("scope", {}))
    if not ps: return _noeval(a, "zero_parts")
    needle = unb64(a["args"]["needle_b64"])
    for p in ps:
        if needle in unb64(p["enviado"]["message_part_b64"]): return _pasa(a, parte=p["idx"])
    peor = max(ps, key=lambda p: p["enviado"]["message_part_bytes"])
    return _falla(a, **_diff(needle, unb64(peor["enviado"]["message_part_b64"])),
                  esperado_ctx=needle.decode("utf-8", "replace")[:120],
                  obtenido_ctx=peor["enviado"]["message_part"][:120])

def as_tool_invocada(a, turnos):
    t = turnos[a["args"].get("turno", len(turnos)) - 1]
    tools = t["agente"].get("tools")
    if tools is None: return _noeval(a, "intermediate_steps_missing")
    return _pasa(a, tools=tools) if a["args"]["nombre"] in tools else _falla(a, tools=tools)

def as_entrega_ok(a, turnos):
    ps = [p for t in turnos for p in t["partes"]]
    if not ps: return _noeval(a, "zero_parts")
    malas = [{"idx": p["idx"], "emisor": p["emisor"], "error": p["error"]}
             for p in ps if not (p["acuse"].get("ok") and p["acuse"].get("message_id") is not None)]
    return _falla(a, sin_message_id=malas, total=len(ps)) if malas else _pasa(a, total=len(ps))

def as_orden_de_partes(a, turnos):
    ps = _partes(turnos, a["args"].get("scope", {}))
    if not ps: return _noeval(a, "zero_parts")
    pos = []
    for n64 in a["args"]["needles_b64"]:
        n = unb64(n64)
        i = next((i for i, p in enumerate(ps) if n in unb64(p["enviado"]["message_part_b64"])), None)
        if i is None: return _falla(a, faltante_b64=n64, encontrados=pos)
        pos.append(i)
    return _pasa(a, pos=pos) if pos == sorted(pos) and len(set(pos)) == len(pos) else _falla(a, pos=pos)

PRIMITIVAS = {"contiene_verbatim": as_contiene_verbatim,
              "no_contiene":       lambda a, t: _invertir(as_contiene_verbatim(a, t)),
              "orden_de_partes":   as_orden_de_partes,
              "cantidad_de_partes":as_cantidad_de_partes,     # analogo
              "tool_invocada":     as_tool_invocada,
              "tool_no_invocada":  lambda a, t: _invertir(as_tool_invocada(a, t)),
              "emisor_usado":      as_emisor_usado,           # analogo
              "entrega_ok":        as_entrega_ok}


# ═══ 5. ESTADO ═══════════════════════════════════════════════════════════════
def derivar_estado(art):
    if art["nivel_evidencia"] == "C":                       return "SIN-EVIDENCIA"   # antipatron 1
    if art.get("canal_bloqueado"):                          return "BLOQUEADO-POR-CANAL"
    if not art["reset"]["ok"]:                              return "SIN-EVIDENCIA"
    for t in art["turnos"]:
        e = t.get("execution")
        if not e or e["superseded"] or e["status"] != "success":
            return "SIN-EVIDENCIA"
    A = art["asserts"]
    if any(a["resultado"] == "NO-EVALUABLE" for a in A):     return "SIN-EVIDENCIA"
    if all(a["resultado"] == "PASA" for a in A):             return "PASA"
    if all(a["resultado"] == "PASA" for a in A if a["gravedad"] in ("SEV1", "SEV2")):
                                                            return "PARCIAL"
    return "FALLA"


# ═══ 6. PERSISTENCIA (sobrevive kill -9) ═════════════════════════════════════
IO = threading.Lock()

def cerrar_caso(cfg, art, rd_por_turno):
    art["estado"] = derivar_estado(art)
    art["ts_cierre"] = iso(now())
    d = cfg.out / "evidence" / cfg.run_id
    d.mkdir(parents=True, exist_ok=True)
    raw = d / f"{art['case_id']}.raw.json.gz"
    with gzip.open(raw, "wt", encoding="utf-8") as f:
        json.dump({str(i): {k: v for k, v in rd.items()
                            if k in {N_WEBHOOK, N_AUTH, N_AGENT, N_SANITIZE, N_LOOP,
                                     N_COMBINE, N_LAST, N_EVENTO, *EMISORES}}
                   for i, rd in enumerate(rd_por_turno)}, f, ensure_ascii=False)
    art["raw_sidecar"] = str(raw.relative_to(cfg.out))
    p, tmp = d / f"{art['case_id']}.json", d / f"{art['case_id']}.json.tmp"
    tmp.write_text(json.dumps(art, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, p)                                   # atomico
    with IO:
        with open(cfg.out / "ESTADO.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": art["ts_cierre"], "case_id": art["case_id"],
                                "estado": art["estado"], "motivo": art.get("motivo", ""),
                                "evidencia": str(p.relative_to(cfg.out))}, ensure_ascii=False) + "\n")
            f.flush(); os.fsync(f.fileno())
        render_matriz(cfg)                               # se RECONSTRUYE leyendo el disco
        render_estado(cfg)


# ═══ 7. LANES + POOL ═════════════════════════════════════════════════════════
class Lane:
    """Un lane = UNA direccion de entrega real. No se inventan: contact_id sintetico
       => 'chat not found'. Invariante: un turno en vuelo por lane, siempre."""
    def __init__(self, d):
        self.id, self.canal = d["id"], d["canal"]
        self.contact_id, self.opportunity_id = str(d["contact_id"]), str(d["opportunity_id"])
        self.stage = d.get("stage", "Evento Identificado")
        self.ledger_grupos, self.lock = set(), threading.Lock()
        self.ultimo_turno = None
        assert (self.opportunity_id.startswith("tg_opp_")) == (self.canal == "telegram")

def correr(cfg, casos, lanes):
    colas = {l.id: queue.Queue() for l in lanes}
    for i, c in enumerate(casos):                        # sticky: el caso entero en un lane
        colas[lanes[i % len(lanes)].id].put(c)
    hilos = [threading.Thread(target=worker, args=(cfg, l, colas[l.id]), daemon=False)
             for l in lanes]
    for h in hilos: h.start()
    for h in hilos: h.join()

def worker(cfg, lane, q):
    while True:
        try: caso = q.get_nowait()
        except queue.Empty: return
        with lane.lock:                                  # serializacion dura por lane
            try:    correr_caso(cfg, lane, caso)
            except Exception as e:
                cerrar_caso(cfg, esqueleto_sin_evidencia(cfg, lane, caso, repr(e)), [])
```

Uso:
```
source .env && python3 scripts/testing/hpf-runner-evidencia.py \
  --casos clients/HPF_HappyFlops/07_testing/fase2/casos.yaml \
  --lanes clients/HPF_HappyFlops/07_testing/fase2/lanes.yaml \
  --out   clients/HPF_HappyFlops/07_testing/fase2 \
  --workers 3
```
Guards en código, no en la disciplina: `--pre-chequeo` es la **única** forma de mandar `channel:"test"`, y en ese modo estampa `nivel_evidencia:"C"` ⇒ ningún caso puede cerrar en `PASA`. Un `contact_id` que no sea una dirección real aborta con assert.

---

### Critical Files for Implementation
- /Users/camilo/Downloads/camilo-workspace/scripts/testing/hpf-runner-evidencia.py (a crear)
- /Users/camilo/Downloads/camilo-workspace/clients/HPF_HappyFlops/07_testing/protocolo-paridad-hpf-v1.md
- /tmp/hpf_live.json (nodos `Auth + Normalize`, `Sanitize + Split Output`, `Debounce - Insert`, los 7 emisores, `Es Origen Telegram? (Post)`)
- /Users/camilo/Downloads/camilo-workspace/scripts/testing/test-sys-webhook-quick.py (única base con auth header)
- /Users/camilo/Downloads/camilo-workspace/clients/HPF_HappyFlops/07_testing/oraculo/INDICE.json + sample_*.md (fuente de los needles verbatim)

---

# PARTE 2 — Derivación de cobertura y los 25 casos P0

# DERIVACIÓN DE COBERTURA — HPF Inbound Handler (vivo, 71 nodos)

Todo lo que sigue está derivado de `/tmp/hpf_live.json` (el vivo congelado) y del oráculo. Cita `ruta:línea`. Donde digo "jsCode:N" es el número de línea **dentro del `jsCode` del nodo `Sanitize + Split Output`**, reproducible con:
`python3 -c "import json;d=json.load(open('/tmp/hpf_live.json'));print([n for n in d['nodes'] if n['name']=='Sanitize + Split Output'][0]['parameters']['jsCode'])" | cat -n`
Idem "systemMessage:N" sobre `Vendedor (LLM Agent).parameters.options.systemMessage`.

---

## A) MATRIZ A — conversacional

### Cálculo de N

```
dimensiones = evento(3) × paso(4) × clase de entrada(11)
N = 3 × 4 × 11 = 132 celdas
```
evento = {Boda, XV, Otros} · paso = {saludo, imagen de evento, fichas de producto, cotización/cierre} · clase = las 11 de protocolo:128.

**Excluidas 77 · Testables 55 · P0 contable 25.**

### Justificación por celda excluida (una línea cada regla, con el conteo)

| # | Celdas | Regla de exclusión | Fundamento verificable |
|---|---|---|---|
| X1 | 22 | `paso=saludo` × evento: en el saludo el evento es por definición desconocido, así que Boda/XV/Otros son **la misma celda** — colapso 3→1. | systemMessage:136 "Si no hay evento en [10], manda el saludo de [3] tal cual" |
| X2 | 6 | `paso=saludo` × {producto puntual, colectivo, ambiguo, fuera de evento, cantidad+CP, bajo mínimo}: nombrar producto **suprime el saludo**; la celda se reclasifica a `paso=fichas`, no se borra. | systemMessage:139-141 + :317 (regla 25); Sanitize jsCode:278-284 (`if (text.indexOf('👼🏢')…) { if(!intenciones.productos.length) return SALUDO; text=''; }`) |
| X3 | 18 | `paso=imagen de evento` × las mismas 6 clases: `nombraProducto=true` o `intenciones.productos.length>0` ⇒ `eventoReciente=false` ⇒ la portada no se emite. | jsCode:262-265 y jsCode:484 (`if (eventoReciente && !fichasFinal.length)`) |
| X4 | 3 | `paso=imagen de evento` × comprobante: un comprobante entra por `Es Pago Detectado?[true]` y nunca llega al Sanitize. | `connections`: Parse Vision → Es Pago Detectado? → Update payment_proof_detectado |
| X5 | 3 | `paso=imagen de evento` × imagen: Parse Vision reescribe `message_text` a `[Imagen recibida: …]`, que no contiene evento ⇒ `eventoSenalado=false`. | nodo `Parse Vision` jsCode (última línea) + jsCode:233-242 |
| X6 | 3 | `paso=imagen de evento` × audio: el audio es **transporte**; tras Whisper la celda es idéntica a su gemela de texto. Se cubre una sola vez, fuera de esta fila. | Switch[audio] → ¿Audio de Telegram? → Whisper → `Audio a Text` → Vendedor |
| X7 | 3 | `paso=fichas` × comprobante: rama de pago, no de fichas. | idem X4 |
| X8 | 1 | `Boda × producto fuera del evento`: en Boda no existe producto excluido (mandiles `ev:["BODA"]`, vaso `ev:["BODA","XV"]`). | jsCode:35, jsCode:50; `Boda-Grid view.csv:163` (mandiles existe) |
| X9 | 3 | `paso=cotización` × pedido colectivo: "todos" es clase del paso *fichas*; al cotizar degenera en cantidad+CP. | oraculo/sample_9.md:64-83 (el colectivo termina pidiendo cantidad+CP) |
| X10 | 3 | `paso=cotización` × producto ambiguo: desambiguar es **precondición** de cotizar; la celda vive en el paso fichas. | systemMessage:220-237 ([5] DESAMBIGUACIÓN OBLIGATORIA) |
| X11 | 3 | `paso=cotización` × producto puntual: al cotizar es indistinguible de cantidad+CP. | oraculo/sample_7.md:99-117 |
| X12 | 6 | `paso=cotización` × {imagen, audio}: transportes ortogonales al paso. | idem X6 |
| X13 | 3 | `paso=cotización` × ráfaga: transporte ortogonal, se cubre una vez en su propia celda. | protocolo:251 |

**22+6+18+3+3+3+3+1+3+3+3+6+3 = 77 ✓**

### Celdas testables por paso y grado de oráculo

| paso | testables | OBSERVADO | CSV | REGLA | INFERIDO (excluidas del set contable) |
|---|---|---|---|---|---|
| saludo | 5 | 1 (pregunta de negocio) | 0 | 3 (imagen, comprobante, ráfaga) | 1 (audio — cero audios en el oráculo) |
| imagen de evento | 6 | 2 (XV, Boda-vía-sample_3) | 1 (Otros: `Imagen Principal-Grid view.csv:4`) | 1 (ráfaga) | 2 (ráfaga×Boda, ráfaga×Otros) |
| fichas de producto | 29 | 7 | 11 | 6 | 5 |
| cotización/cierre | 15 | 5 | 3 | 5 | 2 |
| **total** | **55** | **15** | **15** | **15** | **10** |

**Las 10 INFERIDO quedan explícitamente fuera del set contable (gate G1, protocolo:204).** Son, nominalmente: audio×saludo, ráfaga×{Boda,Otros} en portada, y 7 celdas de `evento=Otros` que no tienen ni un RECIBE ni fila propia en `Otros-Grid view.csv` (verificado: `grep -i "mandil\|popote" Otros-Grid\ view.csv` → 0 resultados).

**Hallazgo estructural del grado:** los **10 samples son 9 XV + 1 "Boda"**, y ese "Boda" es la misclasificación de `Son 50 años` (oraculo/sample_3.md:24 → :42). **CERO Otros.** Consecuencia dura: la columna `evento=Otros` **no puede tener ninguna celda OBSERVADO**, y su mejor grado posible es CSV (`Otros-Grid view.csv`). Cualquier caso P0 de Otros que se afirme como "paridad observada" es INFERIDO disfrazado.

---

## B) MATRIZ B — topológica

Universo derivado por enumeración sobre `/tmp/hpf_live.json`: **14 nodos `if` × 2 = 28 aristas**, **1 `switch` con `options.fallbackOutput:"extra"` = 4 salidas**, **1 `splitInBatches` = 2 salidas** ⇒ **34 aristas de decisión**. Más **36 nodos con llamada externa** (13 httpRequest, 7 telegram, 4 postgres, 4 toolHttpRequest, 1 toolCode, 1 agent, 1 lmChat, 1 memoryPostgres, 1 openAi, 1 webhook, 1 telegramTrigger, 1 respondToWebhook). **Universo = 70.**

### Los 4 sumideros silenciosos (confirmados por enumeración, no por memoria)

| Sumidero | Evidencia en el JSON | Efecto | Cubierto por |
|---|---|---|---|
| `Es El Ultimo Mensaje?` [false] | `connections['Es El Ultimo Mensaje?'].main` tiene **len 1** — la salida false no existe | ejecución muere sin error, sin respuesta, con `status="success"` | **HPF-TOP-021** |
| `Es Origen Telegram? (Post)` [true] | `main[0] == []` (array vacío explícito) | en Telegram nunca corren `Update last_outbound_at` ni la cadena `Get Current Opportunity → Send Imagen Principal → Send Promo Evento` | **HPF-CAN-023** (se observa como sumidero) + N/A escrito |
| `Switch by Message Type` [extra/fallback] | `options.fallbackOutput:"extra"` pero `main` tiene **len 3** | `message_type` fuera de {audio,image,text} muere en verde | **HPF-TOP-022** |
| `Evento Recien Identificado?` [false] | `main` tiene **len 1** | benigno: no hay nada más que emitir | N/A escrito |

### Aristas no cubiertas (4 de 34), con razón escrita

| Arista | Razón / N/A |
|---|---|
| `Es Stage Pausado?` [true] → `Send Ack Stage Pausado` | Exige una opportunity real estacionada en `Esperando Pago/Pago Confirmado/Diseño en Proceso/En Producción/Enviado` **y** una imagen. No entra en el techo de 25. → **PARKING-01**. |
| `Es Origen Telegram? (Pago)` [true] → `Send a text message` | **Arista defectuosa, no testeable**: `Send a text message.chatId = {{ $('Telegram Trigger').item.json.message.from.id }}` — nodo que **no existe en el camino del webhook**. Un comprobante con `opportunity_id: tg_opp_*` revienta en runtime. Se reporta como defecto, no se testea. |
| `¿Media de Telegram?` [true] → `Telegram Get File` | Requiere `telegram_file_id`, que solo produce el `Telegram Trigger`. No es reproducible por el runner curl. → smoke manual del pre-flight, **fuera del set contable**. |
| `¿Audio de Telegram?` [true] → `Whisper Transcribe` | Idem anterior. |

### Nodos externos no cubiertos (3 de 36)

`Send a text message` (arista defectuosa), `Send Ack Stage Pausado` (PARKING-01), `Telegram Get File` (no reproducible por curl).

### Reporte

```
aristas_cubiertas / aristas_totales   = 30 / 34   (88%)
nodos_externos_cubiertos / totales    = 33 / 36   (92%)
MATRIZ B TOTAL                        = 63 / 70   (90%)
```
Descomposición de la cobertura de aristas por caso: ver columna `assert` en (C); cada caso declara qué arista ejerce.

**Además hay que cubrir el sumidero de nivel C:** `¿Es test?`[true] → `Respond to Webhook`. Se ejerce **una sola vez en el pre-flight** como smoke de conectividad, con nivel de evidencia declarado **C**, y **no cuenta para ningún gate** (protocolo:226). Ese camino saltea el Sanitize y los 7 emisores.

---

## C) LOS 25 CASOS P0

### Regla de selección (escrita antes de mirar resultados, protocolo:15)

- **R1** — toda celda OBSERVADO con severidad S1 entra.
- **R2** — las 7 filas NO-REPLICAR de protocolo:156-168 entran, sea cual sea su grado.
- **R3** — toda arista S1 de Matriz B no cubierta por R1∪R2 entra.
- **R4** — grado INFERIDO ⇒ fuera del set contable.
- **R5** — el resto a PARKING con una línea.

### Convención de IDs y corrección de colisión

El protocolo usa **S1/S2/S3 como severidad**; `resultados-fase2-2026-07-24.md:24-26` usa S1/S2/S3 como **casos de envío**. **Renombrados** los de envío a **ENV-01 (100 sand. gruesas), ENV-02 (300 cilindros), ENV-03 (50 mandiles)**; en este documento S1/S2/S3 es **solo severidad** (protocolo:146-148: *S1 = cambia si el lead compra o si Rebeca tiene que intervenir*).

### Precondición dura del runner (aplica a los 25)

```sql
DELETE FROM messages        WHERE session_id = '<phone del caso>';
DELETE FROM debounce_buffer WHERE contact_id = '<contact_id del caso>';
```
NO `n8n_chat_histories` (es del bot viejo). `Postgres Chat Memory.sessionKey = {{ $('Auth + Normalize').first().json.phone }}` ⇒ **un `phone` único por caso aísla la memoria gratis**. `debounce_buffer` está keyed por `contact_id`, y en Telegram `contact_id` **es el chat_id** (`Send Photo (Telegram).chatId = {{ $('Auth + Normalize').first().json.contact_id }}`) ⇒ **los casos Telegram comparten contact_id, no se pueden paralelizar y el DELETE de debounce es obligatorio entre casos.** Los casos GHL sí paralelizan por contact_id distinto.
Si el DELETE falla ⇒ `SIN-EVIDENCIA` automático (protocolo:249).

### Tabla

| id | intención (doc que la firma) | sev | oráculo (ruta:línea) | canal | t | input literal por turno | esperado | assert concreto (arista/nodo que ejerce) |
|---|---|---|---|---|---|---|---|---|
| **HPF-SAL-001** | PARIDAD contenido / DELTA formato (3 burbujas) — `criterios-fase1-v1.md:32` | S2 | OBSERVADO `oraculo/sample_2.md:19` (idem 5:19, 7:19, 9:19, 10:19 — 8/10 sin la comilla parásita de 1:19 y 3:19) | ambos | 1 | `¡Hola! Quiero más información.` | **Exactamente 3 partes, byte-exactas** (jsCode:116-120): P1=`Hola! gracias por escribir a Happy Flops, me llamo Rebeca soy un asistente virtual, yo le estaré atendiendo con gusto ☺️🙋‍♀` · P2=`Me podría decir de que es su evento? ` (**espacio final**) · P3=`🤵👰 - Boda\n🎂🥳 - XV Años\n👼🏢 - Otros` | `len(runData['Send a text message1'])==3`; `text[i]===P_i` **sin trim/normalize**; cada run con `message_id` numérico; `'Send Photo (Telegram)' not in runData`. Ejerce `¿Parte con foto?[false]`, `¿Parte con documento?[false]`, `¿Parte con video?[false]` |
| **HPF-EVT-002** | PARIDAD promo / DELTA byte (ver nota) — `protocolo:172-189` | **S1** | OBSERVADO-DECIDE `oraculo/sample_9.md:43` (idem 1:43, 4:43, 5:43, 6:43, 7:43, 8:43, 10:43 — 9/10) | ambos | 1 | `Es para unos XV` | **2 partes**: P1=`Qué padre! 😊··\n🎉 *¡SEMANA LOCA DE PROMOS! SOLO 7 DÍAS PARA LLEVARTE TUS RECUERDITOS PERSONALIZADOS CON DESCUENTAZO* 🎉` (**DOS espacios** tras 😊, jsCode:106) · P2 = caption `TENEMOS ESTOS PRODUCTOS PARA TU EVENTO:\n\n*Sandalias*\n*Cilindros*\n*Kit anti cruda*\n*Pantuflas*\n\nDime cuales te interesan, así te mostramos toda su información··😊` (**DOS espacios** antes de 😊, jsCode:103) con `photo_url` = `…/136d7ce1-0487-4767-a408-16742a068939.jpg` (jsCode:98) | P1 y caption byte-exactos; `'*Mandiles para Boda*' not in caption`; foto emitida como foto (`Send Photo` con `message_id`), no como URL. `intermediateSteps` contiene `action.tool === 'IDENTIFICAR_EVENTO'` (igualdad). Ejerce `¿Parte con foto?[true]` |
| **HPF-FIC-003** | PARIDAD ficha (CSV) / DELTA video+PDF+reformato — `mejoras…2026-05-21.md:64` | **S1** | CSV `XV-Grid view.csv:172` (`descripcion` S1) + DELTA firmado en jsCode:34 | ambos | 1 | `Es para unos XV, quiero precio de sandalias` | Orden exacto: [ficha sandalias jsCode:34 + `photo_url=…6a62bf41b86ae4203405cbf9.jpeg`] → [`Mira este video para que veas cómo se ve 🎥` + `video_url=…6a701852cf81b06f05808192.mp4`] → [`Aquí tienes el catálogo completo 📋` + `doc_url=…6a701851a4c8a1a2c39ff069.pdf` (pdf.XV)] → [CTA femenino `¿Le interesa sumarlas a la cotización?\nDígame:\n- Cantidad\n- Código postal\n\n¡Gracias!` jsCode:122-123] | 1 run de `Send Photo`, 1 de `Send Video`, 1 de `Send Document`, último `Send a text message1` === CTA byte-exacto **con "sumarlas"**; `action.tool === 'MOSTRAR_PRODUCTOS'`; ficha byte-exacta contra jsCode:34 **y** contiene los tokens del CSV (`$25`,`$30`,`50 pares`). Ejerce `¿Parte con documento?[true]`, `¿Parte con video?[true]` |
| **HPF-FIC-004** | NO-REPLICAR parcial (gate de evento en colectivo) + PARIDAD 6 productos — `protocolo:172-189` | **S1** | OBSERVADO `oraculo/sample_9.md:64-79` (DECIDE 6 productos) + `:83` (RECIBE) | ambos | 2 | T1 `Xv años` · T2 `Precio de todos` | Fichas de **todos los válidos en XV** (sandalias, las 3 pantuflas por jsCode:365-370, cilindros+cat, kit+cat, vaso+cat) y **CERO mandiles**; **una sola** CTA_DATOS al final | ninguna parte contiene `Mandiles`; existe parte `✨ Cilindros personalizados`; `count(partes que empiezan con '¿Le interesa sumarl') == 1`; `action.tool === 'MOSTRAR_PRODUCTOS'`. **PROVISIONAL-EJECUTOR** (default protocolo:188: se respeta el gate) |
| **HPF-COT-005** | PARIDAD | **S1** | OBSERVADO ×3 independientes: `sample_4.md:132`, `sample_8.md:251`, `sample_2.md:117` | ambos | 2 | T1 `XV años` · T2 `50 sandalias delgadas, CP 61800` | `⏳(7 DIAS DE PROMO)⏳` exacto; `50 Sandalias Delgadas x $25 = $1,250`; `Envío: $300`; `Total: $1,550`; `Anticipo (50%): $775`; bloque SIETE_PASOS canónico (jsCode:121) | regex sobre partes concatenadas: `⏳\(7 DIAS DE PROMO\)⏳`, `\$1,250`, `\$300`, `\$1,550`, `\$775`; **`$24` ausente**; `count('HAZ TU PEDIDO EN 7 SENCILLOS PASOS')==1`; `action.tool==='CALCULAR_ENVIO'`; ninguna parte matchea `\d\s*kg`. Math re-derivada del `CALCULAR_ENVIO` vivo: 50×0.15=7.5 kg → bracket `>7 && <=12` → $300 ✓ |
| **HPF-COT-006** | PARIDAD | **S1** | OBSERVADO `oraculo/sample_7.md:117` | ambos | 2 | T1 `Hola XV, quiero pantuflas de satín personalizadas` · T2 `60 piezas, el código postal es 59230` | `60 Pantuflas x $30 = $1,800`; `Envío: $300`; `Total: $2,100`; `Anticipo (50%): $1,050` | regex `\$1,800`, `\$300`, `\$2,100`, `\$1,050`. Math: 60×0.15=9 kg → $300 ✓ |
| **HPF-COT-007** | PARIDAD | **S1** | OBSERVADO `oraculo/sample_4.md:284` | ambos | 2 | T1 `XV años, sandalias` · T2 `50 piezas de la gruesa, código postal 61800` | `50 Sandalias Gruesas x $30 = $1,500`; `Envío: $300`; `Total: $1,800`; `Anticipo (50%): $900` | regex `Gruesas`, `\$1,500`, `\$1,800`, `\$900`; **PROHIBIDO** `\$25` en la línea de sandalias. Discrimina la variante de suela contra HPF-COT-005 |
| **HPF-FIC-008** | PARIDAD | S2 | OBSERVADO `oraculo/sample_2.md:95` + `sample_4.md:110` | ambos | 1 | `XV años, quiero cotizar 50 sandalias CP 44100` | NO cotiza; pide delgada vs gruesa **en el mismo mensaje** (systemMessage:220-237) | ninguna parte contiene `⏳(7 DIAS DE PROMO)⏳`; alguna matchea `/delgad\|gruesa/i`; `'COTIZADOR' not in [s.action.tool for s in intermediateSteps]` |
| **HPF-NRP-009** | **NO-REPLICAR #1** (loop de repetición, ~30% de leads) — `mejoras…2026-05-21.md:28` y `:50`; `08_testing_precutover.md:205` (E-01); `reunion-2026-05-21-rebeca-casos.md:15` | **S1** | OBSERVADO del defecto: `sample_6.md:92-152`, `sample_4.md:157-217` | **ghl** — **BLOQUEADO-POR-CANAL en Telegram** | 2 | T1 `Es para una boda, quiero 50 sandalias delgadas, CP 44730` · T2 `y los termos cuánto?` | **Qué hace el nuevo en su lugar:** lee `[10] CONTEXTO DEL LEAD` (systemMessage:331-340) + memoria; **no re-pregunta cantidad ni CP** y cotiza cilindros reutilizando el CP ya dado (systemMessage:44) | en T2 ninguna parte matchea `/(código postal\|cuántas piezas\|qué cantidad)/i`; ninguna re-emite el bloque 7 pasos; `'IDENTIFICAR_EVENTO' not in tools(T2)`. **Bloqueo:** en Telegram `[10]` viene siempre vacío (systemMessage:140) ⇒ el caso da verde vacío. Es el bug estrella de Oscar (protocolo:245) |
| **HPF-NRP-010** | **NO-REPLICAR #2** (re-pide cantidad+CP si el lead sigue comentando) — `reunion…rebeca-casos.md:13`; `08_testing_precutover.md:205` | **S1** | OBSERVADO del defecto `sample_4.md:157-217` (5 `{}` tras corregir la suela) | **ghl** — BLOQUEADO-POR-CANAL | 2 | T1 `Boda, 50 sandalias delgadas CP 44730` · T2 `oye y los diseños los puedo elegir yo? quiero uno con nuestros nombres` | **Nuevo:** responde sobre diseño **sin reabrir la recolección** ni re-cotizar | T2: ninguna parte pide cantidad ni CP; ninguna contiene `⏳(7 DIAS DE PROMO)⏳`; hay al menos 1 parte no vacía (contra el patrón `{}` del original) |
| **HPF-NRP-011** | **NO-REPLICAR #3** (cotiza moño como satín clásica) — `reunion…rebeca-casos.md:21`; `mejoras…:31` y `:61`; `08_testing_precutover.md:208` (E-04); `criterios-fase1-v1.md:79-82` | **S1** | CSV `XV-Grid view.csv` (variantes) + REGLA systemMessage:245-246 | ambos | 1 | `Para unos XV quiero pantuflas de moño` | **Nuevo:** manda **las DOS fichas de moño** y **saca la lisa** (jsCode:373-379), y confirma variante antes de cotizar: `✨ Pantufla de moño de satín para XV años…$30` (jsCode:22) + `✨ Pantufla de moño de peluche para XV años…$35` (jsCode:17) | exactamente 2 partes que empiezan con `✨ Pantufla de moño de`; **ninguna** parte empieza con `✨ Pantuflas de satín personalizadas` (jsCode:28); ninguna parte contiene `⏳(7 DIAS DE PROMO)⏳` |
| **HPF-NRP-012** | **NO-REPLICAR #4** (pide mail para PDF) — `reunion…rebeca-casos.md:23`; `mejoras…:32` y `:62`; `08_testing_precutover.md:209` (E-05); `criterios-fase1-v1.md:104-107` | **S1** | REGLA systemMessage:304 (regla 12) | ambos | 2 | T1 `¿Me mandas la cotización formal en PDF a mi correo?` · T2 `necesito el PDF sí o sí, es para mi contadora` | **Nuevo:** no promete PDF, no pide email, ofrece la cotización en el chat; ante insistencia **llama `ATENCION_PERSONALIZADA`** | ninguna parte contiene `PDF`, `correo`, `e-mail` ni `@`; en T2 `'ATENCION_PERSONALIZADA' in [s.action.tool …]` **por igualdad**, y el run del nodo `ATENCION_PERSONALIZADA` existe en runData |
| **HPF-NRP-013** | **NO-REPLICAR #5** (escala cuando piden catálogo) — `reunion…rebeca-casos.md:27`; `mejoras…:34` y `:64`; `08_testing_precutover.md:211-212`; `criterios-fase1-v1.md:99-102` | **S1** | CSV `Boda-Grid view.csv:8` (`Te comparto el *catalogo de diseños* que tenemos para *Cilindros*`) | ambos | 1 | `Es para una boda. Me mandas el catálogo de diseños de cilindros?` | **Nuevo:** manda el catálogo vía `MOSTRAR_PRODUCTOS`: ficha cilindros + video + **parte byte-exacta** `Te comparto el *catalogo de diseños* que tenemos para *Cilindros*` (jsCode:81, `catalogo` **sin tilde**) con `photo_url=…6a701855188345b27e310907.jpeg` (auto-adjunta por `cat:"cat_cilindros"`, jsCode:45 + :464-465) | existe parte con ese texto **byte-exacto** y `photo_url` no vacío; `'ATENCION_PERSONALIZADA' NOT in tools`; `action.tool==='MOSTRAR_PRODUCTOS'` |
| **HPF-NRP-014** | **NO-REPLICAR #6** (escala al pedir "fotos" en la desambiguación) — `reunion…rebeca-casos.md:29`; `mejoras…:35` y `:65`; `08_testing_precutover.md:213` (E-09) | S2 | REGLA jsCode:268 (`pidioDeNuevo`) + jsCode:359 | ambos | 2 | T1 `XV, quiero pantuflas` · T2 `mándame fotos de cada una` | **Nuevo:** re-envía la infografía de cada variante aunque ya se hayan mostrado (jsCode:355-359 permite re-mandar cuando `pidioDeNuevo`) | T2: `len(runData['Send Photo (Telegram)']) >= 2`; `'ATENCION_PERSONALIZADA' NOT in tools`; ninguna parte matchea `/consultar con.*equipo\|un asesor/i` |
| **HPF-NRP-015** | **NO-REPLICAR #7** (no reconoce vasos con popote en imagen) — `reunion…rebeca-casos.md:25`; `mejoras…:33` y `:63`; `08_testing_precutover.md:210` (E-06) | **S1** | REGLA: categorías del `Vision Classifier` (`jsonBody`, incluye `vaso_popote`) + CSV `XV-Grid view.csv:210` | ambos | 1 | `message_type:"image"`, `media_url:"https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/6a62bf42ca81015f1c93cf8d.jpeg"`, `message_text:""`, `stage:"Evento Identificado"`, `custom_fields:{"evento_detectado":"XV"}` | **Nuevo:** Vision devuelve `vaso_popote` y el Vendedor lo cotiza ($35/u, mín 50 — systemMessage:250), no escala | `json.loads(runData['Vision Classifier'].choices[0].message.content)['producto'] == 'vaso_popote'`; alguna parte contiene `Vaso con popote 24 oz` o `$35`; `'ATENCION_PERSONALIZADA' NOT in tools`. Ejerce `Switch[image]`, `Es Pago Detectado?[false]`, `Es Stage Pausado?[false]`, nodo `Set imagen_input` |
| **HPF-FIC-016** | PARIDAD (gate de evento en pedido puntual) | **S1** | CSV: `XV-Grid view.csv` **no tiene fila Mandiles** (`grep -i mandil` → 0) vs `Boda-Grid view.csv:163`; `reglas_negocio.md:56` | ambos | 1 | `Me interesan mandiles para unos XV` | No manda la ficha de mandiles ni cotiza; dice que son solo de Boda | ninguna parte contiene `✨ Mandiles para boda`; ninguna contiene `⏳(7 DIAS DE PROMO)⏳`; alguna matchea `/solo.*boda\|exclusiv.*boda/i`. Verifica el gate `ev:["BODA"]` (jsCode:35) vía `matchCatalogo` jsCode:155 |
| **HPF-COT-017** | PARIDAD | **S1** | CSV/REGLA `reglas_negocio.md:39`; `criterios-fase1-v1.md:74-77`; systemMessage:247 y :275 | ambos | 1 | `Para una boda, dame 35 cilindros CP 44730` | NO cotiza; dice el mínimo real (40) y espera ajuste | ninguna parte contiene `⏳(7 DIAS DE PROMO)⏳`; alguna contiene `40`; `'COTIZADOR' NOT in tools` |
| **HPF-AUD-018** | PARIDAD (regla inviolable de género) **+ cobertura de transporte audio** | **S1** | REGLA `reglas_negocio.md:16`; `criterios-fase1-v1.md:64-67`; systemMessage [8] | ambos | 1 | `message_type:"audio"`, `media_url:"<URL pública .ogg con la locución 'quiero sandalias para el padrino'>"` | Transcribe y aclara que las sandalias son **solo para mujeres**; no insinúa versión masculina | `runData['Download Audio']` y `runData['Whisper Transcribe']` existen y 200; el texto transcripto llega al agente; ninguna parte matchea `/versión masculina\|de hombre\|para caballeros/i`. Ejerce `Switch[audio]`, `¿Audio de Telegram?[false]`, nodos `Download Audio` + `Whisper Transcribe` |
| **HPF-COT-019** | PARIDAD | S2 | REGLA `reglas_negocio.md:17` y `:256`; `criterios-fase1-v1.md:89-92`; filtro jsCode:292 | ambos | 1 | `¿cuánto pesa el paquete de 100 sandalias?` | No revela kg ni menciona cajas | ninguna parte matchea `/\d\s*(kg\|kilos?\|kilogramos?)\b/i` ni `/caja/i` |
| **HPF-COT-020** | PARIDAD | S2 | REGLA `reglas_negocio.md:18` y `:187`; systemMessage:286 y :297; filtro jsCode:293-294 | ambos | 1 | `¿tenés otro whatsapp o número para llamar?` | Solo `3315948670` | `all(m == '3315948670' for m in re.findall(r'\b\d{7,10}\b', ''.join(partes)))` |
| **HPF-TOP-021** | DELTA documentado (sumidero) — `protocolo:251` | **S1** | REGLA (topología: `connections['Es El Ultimo Mensaje?'].main` len 1) + OBSERVADO del síntoma `sample_6.md:111-152` y `sample_4.md:176-217` (5 RECIBE `{}` seguidos) | ambos | 2 (misma ventana de 15 s) | T1 `Hola` · T2 (a los 3 s) `es para unos XV` | La 1ª ejecución muere en `Es El Ultimo Mensaje?` sin emitir nada y con `status="success"`; la 2ª emite la respuesta al **combinado** `Hola\nes para unos XV` | hay 2 ejecuciones; exec1: `'Combine Messages' not in runData` y cero runs de emisores; exec2: `runData['Combine Messages'].message_text == 'Hola\nes para unos XV'` y ≥1 emisor con `message_id`. Ejerce `Es El Ultimo Mensaje?[false]` |
| **HPF-TOP-022** | DELTA/defecto (4º sumidero) | **S1** | REGLA (`Switch.options.fallbackOutput=="extra"` y `connections['Switch by Message Type'].main` len 3) | ghl (curl) | 1 | `{"message_type":"video","message_text":"les mando un video de referencia","media_url":""}` | La ejecución llega al Switch y **muere en el fallback** sin llamar al agente ni a ningún emisor, en verde | `'Switch by Message Type' in runData`; `'Vendedor (LLM Agent)' not in runData`; cero runs de los 7 emisores; `status=='success'`. **Es el mismo patrón de la ráfaga del 05/08** (140 partes, 140 errores, 0 message_id, todo verde) |
| **HPF-CAN-023** | DELTA (los 3 emisores nuevos del vivo vs v18) | **S1** | REGLA (topología `¿Parte con foto?/documento?/video?`) + jsCode:458-473 | **telegram** | 1 | `Es para una boda, quiero ver sandalias` | 4 emisores distintos disparan en orden ficha → video → pdf → CTA | **Evidencia de entrega, nivel A por runData:** ≥1 run de `Send Photo (Telegram)`, `Send Video (Telegram)`, `Send Document (Telegram)` y `Send a text message1`; **cada uno con `result.message_id` numérico y `result.chat.id == <chat_id real>`**; **CERO objetos `{error}`**; índices de run en el orden esperado; `len(caption) <= 1024`; el gap entre runs consecutivos ≈ 1.5 s (nodo `Wait 1.5s Between Parts`, amount=1.5). Ejerce también `Es Origen Telegram? (Post)[true] → sumidero` |
| **HPF-CAN-024** | PARIDAD (2º emisor de la portada, solo existe fuera de Telegram) — `protocolo:229` | **S1** | OBSERVADO-DECIDE `sample_9.md:43` + REGLA topología | **ghl** — **BLOQUEADO-POR-CANAL** | 1 | `Es para unos XV` sobre contacto GHL real con opportunity, `custom_fields.evento_detectado` vacío | `Get Current Opportunity` 200 → `justSet==true` → `Send Imagen Principal` (attachments[0] = IMAGENES.XV) → `Wait 2s` → `Send Promo Evento` con `promoText` byte-exacto | `runData['Check Evento Just Set'].justSet === true`; run de `Send Imagen Principal` 201 con `attachments[0]=='…136d7ce1-0487-4767-a408-16742a068939.jpg'`; run de `Send Promo Evento` 201 con `message` === `promoText` de `Check Evento Just Set` — que **incluye** `*(Pedidos solo para eventos 2026 por tema de tiempos)*` y por lo tanto **difiere de la `PROMO` del Sanitize (jsCode:106)**. Ejerce `Es Origen Telegram? (Post)[false]`, `Evento Recien Identificado?[true]`, nodos `Update last_outbound_at`, `Get Current Opportunity`, `Send Imagen Principal`, `Send Promo Evento` |
| **HPF-CAN-025** | PARIDAD | **S1** | REGLA `reglas_negocio.md:322-334` + nodo `Decidir Stage Pago` | **ghl** — **BLOQUEADO-POR-CANAL** | 1 | `message_type:"image"`, `media_url:"<URL pública de un comprobante>"`, `stage:"Cotizado"` | Vision `payment_proof=true` → `Update payment_proof_detectado` → `Decidir Stage Pago` → `Move Stage Pago` a `843a06f1-1214-4baa-a3a0-f197cb240b5d` → mensaje `¡Recibí tu comprobante! 🎉 Lo verificamos en breve y te confirmamos.` | `Vision.payment_proof === true`; `Update payment_proof_detectado` 200; `Decidir Stage Pago.nextStageId == '843a06f1-…'`; `Move Stage Pago` 200; `HTTP Request` (GHL) 201. Ejerce `Es Pago Detectado?[true]`, `Es Origen Telegram? (Pago)[false]`. **Defecto derivado:** el mismo caso por Telegram revienta — `Send a text message.chatId` lee `$('Telegram Trigger')`, nodo inexistente en el camino del webhook |

**Techo:** 25 casos · **34 turnos** · promedio **1.36** ≤ 2 · presupuesto de reloj ≈ **34 × 40 s ≈ 23 min** (protocolo:48), sin diagnóstico.

**BLOQUEADO-POR-CANAL si GHL no está:** HPF-NRP-009, HPF-NRP-010, HPF-CAN-024, HPF-CAN-025 (4 casos, **fuera del denominador** del gate de Telegram, protocolo:243). Además, en Telegram toda la familia de estado (`productos_mostrados`, `evento_detectado`, `cotizacion_emitida`, anti-loop, dedup) da verde vacío porque `Mapear Custom Fields` no tiene opportunity real (`Elegir Opportunity Activa` corta si `is_telegram_test`). **Si al final del día no hubo GHL, la entrega dice "anti-loop NO VERIFICADO" en la primera línea** (protocolo:245).

### PARKING (no entran, una línea cada uno)

- **PARKING-01** — `Es Stage Pausado?[true] → Send Ack Stage Pausado`: exige una opportunity estacionada en stage post-venta + imagen; además **la pausa solo aplica a imágenes** (`Check Stage Pausado` cuelga de `Es Pago Detectado?[false]`, no del texto) — un mensaje de texto en `En Producción` **sí** despierta al agente. Defecto reportable.
- **PARKING-02** — `¿Media de Telegram?[true]` y `¿Audio de Telegram?[true]`: exigen `telegram_file_id`, no reproducible por curl; smoke manual.
- **PARKING-03** — verbatim S3 de `cat_mandiles`: el vivo dice `Te comparto el *catalogo de frases* que tenemos para los *MANDILES*` (jsCode:93) vs `Boda-Grid view.csv:186` `Te comparto el *catálogo de diseños* que tenemos para *Mandiles*` (tilde + "diseños/frases" + casing). No se toca mientras haya un S1 o S2 abierto (protocolo:152).
- **PARKING-04** — CTA_DATOS: el vivo mete `\n\n¡Gracias!` (jsCode:122) donde el original tiene `\n¡Gracias!` (`sample_4.md:72`). 1 byte, S3.
- **PARKING-05** — divergencia entre los dos emisores de la promo: `Sanitize.PROMO` (jsCode:106) **sin** el renglón `*(Pedidos solo para eventos 2026 por tema de tiempos)*`, `Check Evento Just Set.promoText` **con** él. El lead recibe textos distintos según el canal. S2.
- **PARKING-06** — orden invertido de la portada: en Telegram sale `[PROMO, IMAGEN]` (jsCode:486), en GHL sale `[IMAGEN, PROMO]` (`Send Imagen Principal → Wait 2s → Send Promo Evento`). S2.
- **PARKING-07** — celdas `evento=Otros` (7): sin ningún RECIBE observado; su mejor grado es CSV y no llegan a S1 en este recorte.

---

## D) NÚCLEO DE REGRESIÓN DE 8

Verde en **2 corridas consecutivas** desde memoria y buffer limpios (protocolo:302). Criterio de selección: **S1 + cada uno cubre una familia de emisión/arista distinta + tiene oráculo OBSERVADO o CSV citable + es de los que fallan en silencio**.

| # | caso | por qué está |
|---|---|---|
| 1 | **HPF-CAN-023** | Es **el único que prueba entrega real**: 4 emisores × `message_id` + `chat.id`. Es exactamente lo que el 05/08 dio 140 errores con status verde. Sin este, todo el resto es teatro. |
| 2 | **HPF-EVT-002** | Paso 2 del embudo, byte-exacto, y el único que ejerce `¿Parte con foto?[true]` en la rama de portada. Es donde vive el defecto de mutación #5 por vecindad. |
| 3 | **HPF-FIC-003** | Único que ejerce **las 3 aristas de media nuevas del vivo** (`documento[true]`, `video[true]`, `foto[true]`) más el CTA byte-exacto. Es el caso que muere si se toca `CATALOGO`. |
| 4 | **HPF-FIC-004** | El "todos" de sample_9 — la falla que se escapó tres meses (protocolo:122). Cubre el gate de evento en modo colectivo, que es la única decisión provisional abierta. |
| 5 | **HPF-COT-005** | La cotización byte-exacta con **3 confirmaciones independientes del oráculo** y la math del `CALCULAR_ENVIO` re-derivada. Es el ancla de precios. |
| 6 | **HPF-NRP-009** | El problema #1 de Rebeca (~30% de leads) y el bug estrella de Oscar. Si queda rojo o bloqueado, va en la primera línea de la entrega. |
| 7 | **HPF-NRP-011** | Único caso cuya lógica vive en un bloque frágil del Sanitize (jsCode:373-379) que **reescribe la selección del LLM**; es el candidato natural a flakear. |
| 8 | **HPF-TOP-021** | La no-flakiness sobre debounce **solo se puede demostrar acá**: es el único caso cuyo resultado depende del reloj de 15 s y del estado de `debounce_buffer`. Dos corridas verdes acá valen más que dos corridas verdes de los otros siete juntos. |

**Alterno si GHL cae:** HPF-NRP-009 se reemplaza por **HPF-NRP-013** (catálogo, S1, byte-exacto contra CSV, y ejerce la misma familia "no escalar"), y se declara explícitamente que anti-loop quedó no verificado.

---

## E) G2-bis — los 5 defectos de mutación, adaptados al VIVO

Cada uno con la ruta exacta de inyección **sobre el vivo** (nodo por nodo, nunca re-import — protocolo:81) y el caso nominal que tiene que romperse.

| # | Defecto (adaptado al vivo) | Punto de inyección | Casos que DEBEN romperse |
|---|---|---|---|
| **1** | Borrar una ficha del mapa `CATALOGO` del Sanitize → **borrar la entrada `id:"sandalias"`** (jsCode:29-34) | `Sanitize + Split Output.jsCode` líneas 29-34 | **HPF-FIC-003** (desaparecen ficha+video+PDF+CTA), **HPF-CAN-023** (0 runs de `Send Photo/Video/Document`), **HPF-FIC-004** (falta sandalias en el colectivo). ✅ rompe 3 |
| **2** | `$25 → $24` en el prompt | `systemMessage:242` (`- Sandalias delgadas (suela 9mm): $25/par — mínimo 50 pares.`) | **HPF-COT-005** (assert `\$1,250` / `\$1,550` / `\$775` contra `sample_4.md:132`) y el assert explícito `'$24' not in partes`. ✅ rompe 1 |
| **3** | Apagar `returnIntermediateSteps` en `Vendedor (LLM Agent)` | `parameters.options.returnIntermediateSteps: false` | **Rompe dos veces**: (a) todo assert de `action.tool` → HPF-FIC-003, 004, 005, 008, 012, 013, 014, 015, 017; (b) **funcionalmente**, `leerSteps(agent.intermediateSteps)` (jsCode:196-215) devuelve vacío ⇒ `fichas=[]` ⇒ **no se manda ninguna ficha ni el CTA** → HPF-FIC-003, 004, HPF-NRP-011, 013, 014, HPF-CAN-023. ✅ rompe 12 |
| **4** | Romper el gate `evento === 'BODA'` de la ficha de mandiles → **borrar `ev:["BODA"]`** | `Sanitize + Split Output.jsCode:35` | **HPF-FIC-016** (aparecería `✨ Mandiles para boda` en XV y el assert `'✨ Mandiles para boda' not in partes` cae), **HPF-FIC-004** (el assert `'Mandiles' not in partes` del caso "todos" cae). ✅ rompe 2 |
| **5** | Sacar el header `⏳(7 DIAS DE PROMO)⏳` | `systemMessage:195` y `systemMessage:300` (regla 8) | **HPF-COT-005**, **HPF-COT-006**, **HPF-COT-007** (assert de header exacto). ✅ rompe 3 |

**Los 5 rompen ≥1 caso nominal. No hay eje ciego entre los 5 del protocolo.**

### Huecos de cobertura que el gate de mutación SÍ revela (declararlos, no taparlos)

1. **Hueco real — precio en la ficha vs precio en el prompt.** Si en vez de systemMessage:242 se muta **la ficha** (`jsCode:34`, `💰 suela delgada $25` → `$24`), **ningún caso rompe**, porque ningún assert compara la ficha byte a byte contra el CSV. **Mitigación ya incorporada:** el assert de HPF-FIC-003 exige la ficha byte-exacta contra jsCode:34 **y** los tokens `$25`/`$30`/`50 pares` de `XV-Grid view.csv:172`. Con esa mitigación el hueco se cierra; sin ella, el corpus no mide el eje "ficha".
2. **Hueco real — el gate de stage pausado.** Mutar `PAUSED_STAGES` en `Check Stage Pausado` no rompe ningún caso: `Es Stage Pausado?[true]` está en PARKING-01. Eje descubierto.
3. **Hueco real — la rama Telegram de pago.** Mutar `Send a text message` no rompe nada porque esa arista ya está muerta por construcción (`chatId` lee `$('Telegram Trigger')` desde el camino del webhook). No es un hueco de tests: es un defecto del vivo que ningún test puede alcanzar. Va a la entrega como "NO VERIFICADO — arista defectuosa".
4. **Hueco parcial — verbatim de accesorios/catálogos.** Mutar `cat_anticrudas` (jsCode:85), `tapas` (jsCode:73) o `bolsa_shein` (jsCode:69) no rompe ningún caso P0. Están todos en PARKING (S3) por la regla de secuencia (protocolo:152): no se tocan mientras quede un S1/S2 abierto. Eje declarado como **descubierto a propósito**.

**Reversión:** los 5 se revierten y se verifica **por re-export + sha256**, no por memoria (protocolo:283 y :311).

---

## Archivos críticos para la implementación

- `/tmp/hpf_live.json` — el baseline congelado; fuente de la Matriz B, de los literales byte-exactos (`Sanitize + Split Output.jsCode`), de los precios (`systemMessage`) y de la math de envío (`CALCULAR_ENVIO.jsCode`).
- `/Users/camilo/Downloads/camilo-workspace/clients/HPF_HappyFlops/07_testing/protocolo-paridad-hpf-v1.md` — el contrato: severidades (:146-148), las 7 filas NO-REPLICAR (:156-168), el techo (:46), los sumideros (:251), la escalera de evidencia (:219-229).
- `/Users/camilo/Downloads/camilo-workspace/clients/HPF_HappyFlops/07_testing/oraculo/` — `sample_9.md` (todos + promo), `sample_4.md`, `sample_7.md`, `sample_8.md`, `sample_2.md` (cotizaciones byte-exactas), `sample_6.md` (los `{}` del loop).
- `/Users/camilo/Downloads/camilo-workspace/clients/HPF_HappyFlops/00_migracion_ghl/00_inputs/XV-Grid view.csv` y `Boda-Grid view.csv` — fuente CSV independiente de las fichas y del gate de mandiles (ausencia en XV).
- `/Users/camilo/Downloads/camilo-workspace/clients/HPF_HappyFlops/00_migracion_ghl/04_guia_migracion/08_testing_precutover.md:199-216` — Test Plan E (E-01…E-10 → P1-P9), el puntero que firma las 7 filas NO-REPLICAR.

---

# PARTE 3 — Crítica adversarial

## Veredicto

El diseño es mucho mejor que los tres intentos previos en un punto (correlación por token, evidencia por `runData`), y sigue teniendo **al menos 7 caminos por los que un caso cierra en PASA sin que el lead haya recibido lo que se afirma**, más 2 por los que el gate se declara cumplido sin serlo. Todo lo de abajo está verificado contra `/tmp/hpf_live.json`, no es hipotético.

---

## A. Falsos verdes (Q1) — ordenados por probabilidad × daño

### H1 — Entrega parcial se lee como entrega completa **(el más grave)**
`entrega_ok` itera `t["partes"]`, y `t["partes"]` se construye **iterando los emisores presentes en runData**. Es circular: si un emisor no corrió, la parte no existe, y por lo tanto no puede fallar.
**Escenario:** `Sanitize` emite 6 partes (ficha + video + catálogo + PDF + CTA). La ejecución muere / se evicta / el worker se cae después de la parte 3. runData trae 3 runs de emisor, los 3 con `message_id`. → `entrega_ok` PASA, `contiene_verbatim` de la ficha PASA, el caso cierra **PASA con el lead sin CTA y sin PDF**.
**Cambio mínimo:** extraer `n_esperadas = len(runData['Sanitize + Split Output'][0]['data']['main'][0])` (equivalente: `len(runData['Loop Message Parts']) - 1`), guardarlo en el artefacto, y `entrega_ok` exige `len(partes_con_message_id) == n_esperadas`. `cantidad_de_partes` debe medirse contra `n_esperadas`, nunca contra `len(partes)`.

### H2 — El defecto estrella de producción está mapeado a "no medido", no a FALLA
Verificado en `Sanitize + Split Output` jsCode:489: `if (!out.length) { const t = filtrarLibre(text); if (t) out = [...] }` — si `out` queda vacío y `filtrarLibre` devuelve vacío, **el nodo retorna `[]`**: cero iteraciones del loop, cero emisores, `status="success"`, el lead recibe **nada**. Eso es literalmente el patrón `{}` de `sample_4.md:176-217` y `sample_6.md:111-152`.
El diseño lo manda a `_noeval(a,"zero_parts")` → NO-EVALUABLE → SIN-EVIDENCIA. **El runner no puede reportar "el bot no contestó" como falla.** Es el bug que más sangra y el único que el corpus está estructuralmente ciego a declarar.
**Cambio mínimo:** `expected_min_parts` en `casos.yaml` (default 1). `zero_parts` es **FALLA** salvo que el caso declare `expected_parts: 0` (HPF-TOP-022).

### H3 — Los asserts negativos pasan al vacío
Dos caminos concretos:
1. `no_contiene = _invertir(as_contiene_verbatim(...))` — `_invertir` sobre un resultado `NO-EVALUABLE` está **indefinido en el diseño**; con la implementación obvia (flip PASA↔FALLA) un NO-EVALUABLE se vuelve PASA o pasa filtrado.
2. `walk_a_loop` devuelve `None` → `p = None` → `mp = (p or {}).get("message_part","")` → **string vacío con sha256 válido**. Todo `no_contiene` / `tool_no_invocada` pasa sobre `b""`.

10 de los 25 casos (008, 009, 010, 011, 012, 013, 016, 017, 019, 020) descansan principalmente en negativos.
**Cambio mínimo:** (i) `_invertir` propaga NO-EVALUABLE; (ii) `walk_a_loop → None` setea `enviado: null` + `indice_no_resuelto: true`, y cualquier assert que toque esa parte es NO-EVALUABLE; (iii) prohibido el default `""` en `.get("message_part", ...)`.

### H4 — Dos casos son tautologías impuestas por el sanitizador, no por el agente
- jsCode:292 — `text.split('\n').filter(l => !/\d\s*(kg|kilos?|kilogramos?)\b/i.test(l))` borra **toda línea con kg** antes de emitir.
- jsCode:294 — `text.replace(/\b\d{7,10}\b/g, m => m === '3315948670' ? m : '')` blanquea **todo número de 7-10 dígitos** que no sea el oficial.

**HPF-COT-019** (`ninguna parte matchea /\d\s*kg/`) y **HPF-COT-020** (`todos los números == 3315948670`) son verdes **por construcción, con cualquier prompt, incluso con la regla borrada del systemMessage**. Miden el regex, no al agente. Lo mismo aplica a los strips de `CTA_AGRESIVOS` (jsCode:296+).
**Cambio mínimo:** ambos asserts se evalúan **dos veces**: contra `Vendedor (LLM Agent).output` (pre-sanitize, la regla) y contra las partes (el efecto neto), reportados por separado. Requiere H5.

### H5 — El artefacto tira la única evidencia pre-sanitize
Se guarda `agente.output_len` y `output_sha256`, **no el output**. El output crudo del agente es el único lugar donde se distingue "el modelo obedeció" de "el regex nos tapó". Sin él, H4 no se puede cerrar y ningún hallazgo sobre reglas del prompt es auditable.
**Cambio mínimo:** `agente.output_b64` en el artefacto + el nodo completo en el sidecar.

### H9 — `entrega_ok` no verifica el destinatario
Chequea `message_id is not None`, nunca `chat.id == lane.contact_id`. Un `lanes.yaml` con un chat_id viejo entrega todo, perfecto, **al chat equivocado** → PASA. Solo HPF-CAN-023 lo chequea, y en prosa.
**Cambio mínimo:** `entrega_ok` exige `int(acuse.chat_id) == int(lane.contact_id)` en cada parte Telegram, y `conversationId` estable en GHL.

### H10 — El acuse de GHL no es entrega
`Send Message via GHL` devuelve `messageId` cuando **GHL acepta**; el envío por WhatsApp/LC-Phone ocurre después y falla por su cuenta (número inválido, ventana 24h, proveedor). El diseño llama A-prime simétrico a Telegram; no lo es.
**Cambio mínimo:** etiquetar `A-prime(entregado)` para Telegram y `A-prime(aceptado)` para GHL, y o bien un `GET` del status del mensaje por caso, o una línea explícita en la entrega: "entrega real en GHL: NO VERIFICADA".

### H18 — `retryOnFail=True` en los 7 emisores (verificado nodo por nodo)
No solo `onError: continueRegularOutput`: **los 7 tienen `retryOnFail: true`**. Consecuencias: una parte que falló dos veces y salió a la tercera es indistinguible de un envío limpio; el reintento puede haber **entregado dos veces** (Telegram entrega y la respuesta se pierde); y `executionTime` queda inflado, lo que rompe el assert "gap ≈ 1.5 s" de HPF-CAN-023.
**Cambio mínimo:** guardar `executionTime` por parte y marcar las que exceden el umbral de reintento; el assert de gap pasa a `>= 1.5s`, nunca `≈`.

---

## B. Correlación (Q2)

### H7 — La ventana está anclada al reloj de la notebook, no al de n8n
`startedAt >= t0 - 5s` compara un timestamp del servidor n8n/Postgres con `datetime.now()` local. Cualquier skew > 5 s (y `settings.timezone = "America/Mexico_City"` invita además a un error de parseo de tz) tira **todos** los candidatos fuera de la ventana → `execution_not_found` en todos los turnos, o peor, en algunos.
**Cambio mínimo:** eliminar el tiempo del filtro. Antes del POST, `GET /executions?limit=1` → `last_id`; después filtrar por `id > last_id`. Los ids son monótonos. El probe sigue siendo la identidad. Medir el skew una vez en el pre-flight y estamparlo.

### H8 — "El POST bloquea hasta que termina la ejecución" no vale en Telegram
Verificado: `responseMode: "responseNode"` y `connections['Es Origen Telegram? (Post)'].main[0] == []` → **`Respond to Webhook` nunca se alcanza en Telegram**. El comportamiento de n8n cuando un workflow con responseNode termina sin tocarlo depende de versión (500 "no data returned", o cuelga hasta el timeout del ingress). Sobre ese supuesto descansan el corolario de §2 *y* el presupuesto de 45 s/turno. Si cuelga, cada turno Telegram cuesta hasta 240 s y los 18 min con N=3 se vuelven ~2 h; si devuelve 500 al instante, el poll arranca antes de que la ejecución llegue al Wait.
**Cambio mínimo:** medirlo en el pre-flight con un POST real; derivar `POST_TIMEOUT_S` de esa medición; y hacer la correlación totalmente independiente del retorno del POST (queda así si se toma el `last_id` **antes** del POST, H7).

**Lo que sí está bien (una línea cada uno, no lo desarrollo):** la inyección de `_probe_id` es sólida — `Auth + Normalize` termina en `raw: { ...b, channel }` y sus guardas solo tiran si falta `contact_id` o si no hay texto ni media, no valida keys desconocidas. `Loop Message Parts` tiene `options: {}` → batchSize 1, así que `main[1][0]` es correcto. `tool_invocada` por igualdad sobre `action.tool` es correcto: los tools son `toolHttpRequest` con esos nombres exactos.

---

## C. Aislamiento (Q3)

### H6 — `staticData` en **queue mode**: el propio autor del vivo dice que no es reproducible
`Sanitize + Split Output` jsCode:245-247, textual: *"la instancia corre en queue mode y `$getWorkflowStaticData` solo sobrevive si el turno siguiente cae en el mismo worker. A veces persiste y a veces no, que es peor que nunca"*.
Entonces `memo.grupos` es **por worker** y no determinista. El "ledger de lane" asume un memo único y determinista: es un placebo. El warm-up de saludo escribe el reset (jsCode:280) en el worker que lo ejecutó, que puede no ser el del turno siguiente: tampoco garantiza nada. Resultado: HPF-FIC-004 / NRP-011 / NRP-014 / FIC-016 pueden salir verdes una corrida y rojas la siguiente por razones ajenas al bot, y **el gate de "2 corridas verdes" se puede aprobar cayendo dos veces en un worker limpio**.
Dos cosas que el diseño no aprovecha y una que sobreestima:
- **Sí es legible:** `GET /workflows/{id}` devuelve `staticData.global.hpf` (el export ya trae `"900000009": {...}`). Se puede registrar antes y después de cada caso como evidencia, aunque en queue mode esa copia sea la persistida en DB y no la del worker.
- **La exposición es más chica de lo que dice el diseño:** el filtro jsCode:361 solo corre en el `else` de jsCode:355 y solo `if (!intenciones.productos.length)`. Cuando el LLM sí invoca `MOSTRAR_PRODUCTOS` con productos, el memo **no filtra**. Eso debería ser un **assert de precondición** del caso (`intenciones.productos.length > 0`), no una suposición.
- **`memo.header` se escribe (jsCode:492) y no se lee en ningún lado.** La portada depende de `eventoReciente` (jsCode:265/484), no del memo.
**Cambio mínimo:** `depende_de_memo: true` por caso → k≥3 verdes consecutivos; snapshot de `staticData` pre/post caso en el artefacto; assert de precondición sobre `intenciones.productos`; y una línea en la entrega: *"`gruposMostrados` no es reproducible en esta instancia (queue mode); la familia anti-repetición se mide con una dependencia no determinista conocida"*.

### H17 — El sub-workflow de reset es un DELETE sin guarda sobre la tabla de memoria productiva
`DELETE FROM messages WHERE session_id = $1` con `$1` controlado íntegramente por `casos.yaml` / `lanes.yaml`. Un caso que se olvide el namespace, o un fallback que use el phone real, **borra la memoria de una conversación viva**. La guarda está en la disciplina del runner, no en el SQL.
**Cambio mínimo:** la guarda va en el WHERE: `AND session_id LIKE 'sess\_%'`. Devolver rowcount borrado: si en un namespace fresco es > 0, abortar la corrida.

**Lo que sí está bien:** namespear `phone` aísla de verdad y es gratis — verificado: `phone` aparece solo en el Code de Telegram, en `Auth + Normalize` y en `Postgres Chat Memory.sessionKey`; `Buscar Opportunity Real` busca por `contact_id`, no por phone. El veto a namespear `contact_id` es correcto y es la causa exacta de la ráfaga del 05/08.

---

## D. Normalización silenciosa (Q4)

Además de H3 (`.get(..., "")`):

### H20 — La procedencia de los needles está indefinida
El diseño exige `needle_b64` pero nunca dice **quién lo produce ni desde qué bytes**. Si un humano transcribe el esperado desde `sample_9.md` a `casos.yaml`, el NBSP, el doble espacio tras `😊` y el espacio final de `Me podría decir de que es su evento` — exactamente lo que miden HPF-SAL-001 y HPF-EVT-002 — mueren en el editor y la corrida mide la transcripción. Es el punto más probable donde se evapora la exactitud de bytes.
**Cambio mínimo:** `casos.yaml` guarda `fuente: <path>#Lnn:col_a-col_b` + `needle_sha256`; el runner **re-extrae los bytes del archivo fuente** al arrancar y aborta si el sha no coincide.

### H19 — El vivo parte captions largos; `contiene_verbatim` no lo sabe
jsCode:499+ parte una burbuja cuando tiene `photo_url` y `len(text) > 1000`. `contiene_verbatim` busca por parte y nunca sobre la concatenación, así que un needle que cruza el corte es **FALLA falsa** (diagnóstico equivocado, que es cómo se quemaron los intentos anteriores).
**Cambio mínimo:** `scope: parte | turno_concatenado` explícito por assert; la concatenación en orden de loop y sobre bytes.

Menor pero real: `_diff` en la rama FALLA elige `peor = max(ps, key=bytes)` — una parte arbitraria sin relación con el needle. El "primer byte divergente" que va al reporte es ruido. Corregir: si ninguna parte contiene el needle, elegir la de mayor prefijo común, no la más larga.

---

## E. Estados, gates y entrega (Q5–Q9)

### H11 — Tres de los 25 casos no pueden cerrar PASA por construcción, y uno está en el núcleo de 8
`derivar_estado` devuelve SIN-EVIDENCIA si algún turno es `superseded`, si `status != "success"`, o si algún assert es NO-EVALUABLE. Pero:
- **HPF-TOP-021** *requiere* una ejecución superseded (es su hallazgo) → nunca PASA. Y es el #8 del núcleo de regresión, el único que demuestra no-flakiness del debounce.
- **HPF-TOP-022** *requiere* cero partes y que el agente no corra → `entrega_ok` NO-EVALUABLE → nunca PASA.
- **HPF-CAN-025** depende de ramas con `status` variable.

El gate "8 verdes en 2 corridas" es **inalcanzable por diseño**. A las 2 AM alguien afloja el gate: ese es el mecanismo exacto de los tres falsos verdes anteriores.
**Cambio mínimo:** `esperado: {superseded: true, partes: 0, agente_corrio: false}` por caso; el estado compara expectativa contra observación en vez de aplicar una regla global. `entrega_ok` declarable `no_aplica` con motivo escrito en el artefacto.

### H12 — El gate de mutación puntúa "se rompió el harness" como "se detectó el defecto"
Mutación #3 (apagar `returnIntermediateSteps`) vuelve NO-EVALUABLE todo `tool_invocada` → SIN-EVIDENCIA. Si SIN-EVIDENCIA cuenta como "el caso se rompió", **cualquier mutación que dañe la instrumentación aprueba el gate**: mide la fragilidad del runner, no la sensibilidad del corpus. Mutación #1 puede caer en lo mismo vía H2. Además, la cuenta "rompe 12 casos" está inflada: 9 de esos 12 son asserts de instrumentación, no de comportamiento.
**Cambio mínimo:** el criterio del gate es `estado == FALLA` **con diff de bytes**, no `estado != PASA`. Un SIN-EVIDENCIA en el gate de mutación = **gate no aprobado**, y se lista. Partir #3 en (a) instrumentación (fuera del gate) y (b) el efecto funcional real (`leerSteps` vacío → `fichas=[]`), que sí es de comportamiento.

### H15 — El caso más importante del suite puede dar verde con el bug presente
HPF-NRP-009 assert: `ninguna parte matchea /(código postal|cuántas piezas|qué cantidad)/i`. El defecto observado es "vuelve a pedir los datos", y el bot lo hace con *"¿a qué CP te lo mandamos?"*, *"¿me confirmás el número de piezas?"*, *"¿cuántos vas a querer?"* — ninguna matchea. **Verde con el bug de Oscar reproduciéndose.** Lo mismo vale para NRP-010, 012, 013, 014.
**Cambio mínimo:** todo negativo sobre texto libre del LLM va acompañado de un **positivo obligatorio** (en T2 debe aparecer la cotización de cilindros reusando el CP exacto de T1 + `⏳(7 DIAS DE PROMO)⏳`); y los negativos-regex sobre texto libre se declaran grado **JUICIO**, insuficientes por sí solos para cerrar PASA.

### H16 — En Telegram el estado es inerte **y no se puede inyectar** (verificado, más fuerte de lo que dice el diseño)
`Elegir Opportunity Activa` retorna `prev` si `is_telegram_test`; `Mapear Custom Fields` corre igual y produce `custom_fields.evento_detectado = strVal(undefined) = ''` — **string vacío, no `undefined`** — y `nodo()` (jsCode:127-133) solo cae al default cuando el valor es `null`/`undefined`. Por lo tanto el fallback a `Auth + Normalize.custom_fields` (jsCode:229-230) es **código muerto en el camino del webhook**: no se puede falsear `evento_detectado` / `productos_mostrados` / `cotizacion_emitida` metiéndolos en el body de un lane Telegram.
Consecuencia: anti-loop, dedup, "imagen una sola vez", "7 pasos una sola vez", NRP-009 y NRP-010 son medibles **solo con GHL real**. El diseño lo dice, pero igual habilita publicar "21/25 PASA" con los 4 casos GHL "fuera del denominador" — un 84 % que se va a leer como paridad.
**Cambio mínimo:** prohibir el porcentaje agregado. Reporte por familia. Si el lane GHL no corrió, el titular es *"0 de 6 familias de estado verificadas"* y nada más.

### H13 — La matriz **sí** se puede achicar después de ver los resultados (Q6)
`casos.yaml` se llama "denominador congelado" pero nada lo congela: no hay `spec_sha256`, ni commit id, ni hash de la lista de asserts, ni en el artefacto ni en `ESTADO.jsonl`. Y `--redo` **sobrescribe el artefacto anterior**. Se puede borrar dos casos rojos de `casos.yaml`, borrar sus JSON, re-renderizar `MATRIZ.md` desde el disco, y el resultado es autoconsistente. También se puede **debilitar un assert sin cambiar la cantidad de casos** — el conteo no lo detecta.
**Cambio mínimo:** `spec_sha256` + `spec_git_commit` + `asserts_sha256` por caso, estampados en **cada** artefacto y en cada línea del jsonl; el renderer se niega a construir una matriz con hashes mezclados; `--redo` escribe `<CASE>.attempt<N>.json`, nunca borra, y la matriz toma el **peor** intento.

### H14 — Camilo edita a mitad: se registra pero no se actúa (Q7)
`versionId` se lee al inicio y al cierre. Un edit-and-revert entre ambos es invisible. Y `cambio_de_baseline_durante_la_corrida` se escribe en el artefacto pero **`derivar_estado` nunca lo lee**: un fix aplicado a las 15:10 produce un reporte donde casos pre-fix (rojos) y post-fix (verdes) se promedian bajo un solo sha. Además, la fase G2-bis cambia `versionId` a propósito, con lo cual la bandera se vuelve ruido esperado.
**Cambio mínimo:** capturar `versionId` **por turno** desde `GET /workflows?limit=250` (barato, no el export completo), estamparlo en el turno, y `derivar_estado` devuelve SIN-EVIDENCIA si el `versionId` del turno != el baseline declarado del caso. En fase de mutación, el `versionId` mutado **es** el baseline declarado.

### Sin k>1: la no-flakiness no se mide
Todos los casos corren una vez (los 8 del núcleo, dos). El agente es un LLM con tools. Tres veredictos de "listo" que no lo estaban huelen exactamente a verde de una sola tirada.
**Cambio mínimo:** `k` por caso; todo caso cuyo esperado sea texto libre del LLM (NRP-*, COT-008, COT-017) corre k=3 y debe ser 3/3, con los k outputs guardados. **Esto revienta el presupuesto de reloj**: 34 turnos × 45 s ≈ 23 min está calculado con k=1, sin warm-ups, sin resets y sin reintentos. El número real es 2-3×. Un presupuesto falso lleva a recortar casos al final del día — que es H13 disparándose sola.

### Q9 — Afirmaciones de la entrega que hoy no tendrían artefacto detrás
1. "El lead recibe el mensaje completo" → H1 (no se cuenta contra `Sanitize`).
2. "Entrega verificada en GHL" → H10 (solo aceptación).
3. "El bot nunca revela kg ni otro teléfono" → H4 (lo garantiza el regex, no el agente).
4. "No hay flakiness" → k=1.
5. "Anti-loop verificado" → H16 si no hay GHL.
6. "Baseline congelado durante toda la corrida" → H14.
7. "Los 5 defectos inyectados rompen casos" → H12.
8. "El reset dejó el estado limpio" → H6 (el memo no se resetea ni se verifica; en queue mode ni siquiera es determinista).

---

## Orden de aplicación (si hay que priorizar)
1. H1, H2, H3 (los tres falsos verdes de extracción — sin esto no arranques).
2. H7, H8 (sin correlación confiable no hay nada).
3. H11, H12 (sin esto el gate es inaprobable o mentiroso).
4. H4/H5, H9, H15 (asserts que miden lo que no es).
5. H13, H14, H17 (integridad del registro y seguridad del reset).
6. H6, H16, H10, H18, H19, H20 (declaraciones y bordes).

---

### Critical Files for Implementation
- /tmp/hpf_live.json — `Sanitize + Split Output.jsCode` (:127-133 `nodo()`, :245-247 queue mode, :278-284 reset del memo, :292-294 los strips que hacen tautológicos COT-019/020, :346-362 `gruposMostrados`, :484-494, :489 cero partes, :499+ corte de caption), `Auth + Normalize.jsCode` (`raw`, guardas), `Debounce - Insert` / `Es El Ultimo Mensaje?` / `Debounce - Reset Buffer`, los 7 emisores (`onError` + `retryOnFail`), `Mapear Custom Fields`, `Elegir Opportunity Activa`.
- /Users/camilo/Downloads/camilo-workspace/scripts/testing/hpf-runner-evidencia.py (a crear) — `entrega_ok`, `_partes`, `walk_a_loop`, `_invertir`, `derivar_estado`, `correlacionar`.
- /Users/camilo/Downloads/camilo-workspace/clients/HPF_HappyFlops/07_testing/protocolo-paridad-hpf-v1.md — severidades, gates G0-G3, escalera de evidencia.
- /Users/camilo/Downloads/camilo-workspace/clients/HPF_HappyFlops/07_testing/oraculo/ — fuente de los needles; hay que extraerlos por offset de bytes, no transcribirlos.
- /Users/camilo/Downloads/camilo-workspace/clients/HPF_HappyFlops/00_migracion_ghl/00_inputs/XV-Grid view.csv y Boda-Grid view.csv — segunda fuente para cerrar el hueco "ficha vs prompt" del gate de mutación.
