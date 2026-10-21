#!/usr/bin/env python3
"""
Parches pre-BSP (23/9) al stack nuevo de VTR. Todos los workflows tocados están OFF (o son sub-workflows).

Por qué existe: el main nuevo nunca se ejecutó con un payload real de GHL (el staging se probó por Telegram
con otra entrada). La revisión nodo por nodo del 23/9 encontró que, tal como estaba, no respondía ningún
mensaje:
  1. `Check dedup` (SELECT sin filas) no emitía ítems → el flujo moría en el 1.er nodo Postgres.
  2. La entrada del bot pasaba por la cadena de Airtable y leía `body.custom_fields.respuesta_definitiva`
     (campo de ManyChat): con el payload de GHL tira TypeError.
  3. `Enviar WPP` mandaba `$json.parte1 || $json.text`, pero `Normalizar burbujas` devuelve `mcBody`/`texto`
     → mensaje vacío.
Y en el resto del stack, cosas que se rompían en el primer uso real (detalle por función abajo).

Uso:
  python3 vtr_pre_bsp_fixes.py            # dry-run: dice qué cambiaría en cada workflow
  python3 vtr_pre_bsp_fixes.py --execute  # aplica, con snapshot antes/después + sha256
Idempotente: cada parche busca su marca `PRE-BSP-0923` y no se re-aplica.
"""
import copy, hashlib, json, sys, time, urllib.error, urllib.request, uuid
from pathlib import Path

ROOT = Path("/Users/camilo/Downloads/camilo-workspace")
OUT = ROOT / "clients/VTR_Venttur/03_workflows/ghl-live-2026-09-23-pre-bsp-fixes"
MARK = "PRE-BSP-0923"
LOC = "7aXb4JCKsWV5nUyBXeSF"
GHL_CRED = {"httpHeaderAuth": {"id": "YkVmaA4jlRbO1TQD", "name": "GHL VTR (PIT)"}}
OPENAI_VTR = {"openAiApi": {"id": "ibkhdCMyhr3yqDQk", "name": "OpenAI | Venttur"}}
SETTINGS_OK = ("executionOrder", "callerPolicy", "errorWorkflow", "saveDataErrorExecution",
               "saveDataSuccessExecution", "saveManualExecutions", "saveExecutionProgress", "timezone")

IDS = {
    "main": "1eS1Z5k898c3ATnf",
    "elevar": "v9XkOfL9dQtY2wyv",
    "w6": "AS9ZNhY3GJDfhY3P",
    "rescate": "YB0UxwEVwzISdd54",
    "despachador": "vrShEXQGGAo4FqAt",
    "clasificador": "Xmyoewwa1W5gm1fy",
    "w14": "OaOyHA2tfjMtuWTk",
}


def env(key):
    for line in open(ROOT / ".env"):
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip()


BASE, KEY = env("N8N_BASE_URL").rstrip("/"), env("N8N_API_KEY")


def api(method, path, body=None):
    req = urllib.request.Request(BASE + "/api/v1" + path, method=method,
                                 headers={"X-N8N-API-KEY": KEY, "accept": "application/json",
                                          "content-type": "application/json"},
                                 data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:600]


# ───────────────────────── helpers ─────────────────────────
def node(wf, name):
    for n in wf["nodes"]:
        if n["name"] == name:
            return n
    raise KeyError(f"no existe el nodo '{name}' en {wf['name']}")


def has(wf, name):
    return any(n["name"] == name for n in wf["nodes"])


def replace_in(n, old, new, key="jsCode"):
    s = n["parameters"][key]
    if old not in s:
        raise ValueError(f"[{n['name']}] no encuentro el ancla: {old[:80]!r}")
    n["parameters"][key] = s.replace(old, new)


def json_replace(n, old, new):
    s = json.dumps(n["parameters"], ensure_ascii=False)
    if old not in s:
        raise ValueError(f"[{n['name']}] no encuentro el ancla: {old[:80]!r}")
    n["parameters"] = json.loads(s.replace(old, new))


def http_node(name, pos, method, url, body=None, version="2021-07-28", flags=None):
    p = {"method": method, "url": url, "authentication": "genericCredentialType",
         "genericAuthType": "httpHeaderAuth", "sendHeaders": True,
         "headerParameters": {"parameters": [{"name": "Version", "value": version}]}, "options": {}}
    if body is not None:
        p.update({"sendBody": True, "contentType": "json", "jsonBody": body})
    n = {"parameters": p, "name": name, "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
         "position": pos, "id": str(uuid.uuid4()), "credentials": copy.deepcopy(GHL_CRED)}
    n.update(flags or {})
    return n


def code_node(name, pos, code):
    return {"parameters": {"jsCode": code}, "name": name, "type": "n8n-nodes-base.code", "typeVersion": 2,
            "position": pos, "id": str(uuid.uuid4())}


def if_bool(name, pos, expr):
    return {"parameters": {"conditions": {
        "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 2},
        "conditions": [{"id": str(uuid.uuid4()), "leftValue": expr, "rightValue": True,
                        "operator": {"type": "boolean", "operation": "true", "singleValue": True}}],
        "combinator": "and"}, "options": {}},
        "name": name, "type": "n8n-nodes-base.if", "typeVersion": 2.2, "position": pos, "id": str(uuid.uuid4())}


def link(wf, src, dst, out=0):
    c = wf["connections"].setdefault(src, {}).setdefault("main", [])
    while len(c) <= out:
        c.append([])
    if not any(x["node"] == dst for x in c[out]):
        c[out].append({"node": dst, "type": "main", "index": 0})


def unlink(wf, src, dst, out=None):
    for i, lst in enumerate(wf["connections"].get(src, {}).get("main", [])):
        if out is None or i == out:
            lst[:] = [x for x in lst if x["node"] != dst]


def set_targets(wf, src, out, dsts):
    c = wf["connections"].setdefault(src, {}).setdefault("main", [])
    while len(c) <= out:
        c.append([])
    c[out] = [{"node": d, "type": "main", "index": 0} for d in dsts]


def marked(wf):
    return MARK in json.dumps(wf, ensure_ascii=False)


# ───────────────────────── MAIN ─────────────────────────
NORMALIZE = r"""// Adapter GHL Contact Reply → shape consumido por el resto del workflow.  PRE-BSP-0923
// Acepta el body custom de Camilo ({contact_id, phone, message:{body}, contact:{...}}) y el payload estándar
// de la acción Webhook de GHL (contact_id, first_name, phone, message:{body}, customData…).
const item = $input.first().json;
const body = item.body || item;
const contact = body.contact || {};
const msg = (body.message && typeof body.message === 'object') ? body.message : {};

const contact_id = body.contact_id || body.contactId || contact.id || null;
const phoneRaw = body.phone || contact.phone || null;
const message_body = (msg.body || (typeof body.message === 'string' ? body.message : '') || body.body || body.text || '').toString();
const message_id = msg.id || msg.messageId || body.messageId || body.message_id || null;
const attachments = [].concat(msg.attachments || [], body.attachments || []).filter(u => typeof u === 'string' && u);
const attribution_url = (contact.lastAttributionSource && contact.lastAttributionSource.url)
  || (contact.attributionSource && contact.attributionSource.url)
  || (body.lastAttributionSource && body.lastAttributionSource.url)
  || (body.attributionSource && body.attributionSource.url) || null;
const date_created = body.dateAdded || body.date_created || body.timestamp || new Date().toISOString();

// nsk() idéntico al del rescate/despachador (Batch F.2 · D5) → sessionKey consistente cross-workflow
function nsk(x){ x=(x||'').toString().replace(/[^0-9]/g,''); if(x.length===12 && x.startsWith('52')) x='521'+x.slice(2); return x; }
const wa = nsk(phoneRaw);
const plus = wa ? ('+' + wa) : null;
const firstName = (contact.firstName || contact.first_name || body.first_name || contact.name || '').toString();
const lastName = (contact.lastName || contact.last_name || body.last_name || '').toString();

return [{ json: {
  contact_id,
  phone: plus,
  message_body,
  message_id,
  attachments,
  attribution_url,
  date_created,
  wa_id: wa || null,
  session_key: plus,          // +521<10> — memoria/rescate/despachador (D5)
  whatsapp_phone: plus,       // compat legacy
  id: contact_id,             // compat legacy (nodos que usaban body.id → ahora contactId GHL)
  whatsapp_name: firstName,
  last_name: lastName,
  text: message_body,
  payload: { whatsapp_url: attribution_url, referral: contact.attributionSource || body.attributionSource || null },
  _raw: body,
}}];"""

HASH = r"""// Idempotencia: por id de mensaje si GHL lo manda; si no, sha256(contact_id + date_created + body).  PRE-BSP-0923
const crypto = require('crypto');
const item = $input.first().json;
const raw = item.message_id
  ? `mid::${item.message_id}`
  : `${item.contact_id || ''}::${item.date_created || ''}::${item.message_body || ''}`;
const hash = crypto.createHash('sha256').update(raw).digest('hex');
return [{ json: { ...item, dedup_hash: hash } }];
"""

SEPARAMOS = r"""// Texto + audios del mensaje entrante (GHL).  PRE-BSP-0923
// Texto: el del webhook. Adjuntos: los del webhook + los del último mensaje entrante de la conversación
// (API de GHL), porque la acción Webhook no siempre trae los adjuntos. Sólo se toman si ese mensaje es de
// los últimos 10 min, para no arrastrar un audio viejo.
const n = $('Normalize GHL Payload').first().json;
let texto = (n.text || '').toString().trim();
let urls = [].concat(n.attachments || []);
try {
  const r = $('GHL · Mensajes recientes').first().json || {};
  const raw = (r.messages && (r.messages.messages || r.messages)) || [];
  const inb = (Array.isArray(raw) ? raw : [])
    .filter(m => m && m.direction === 'inbound')
    .sort((a, b) => (Date.parse(b.dateAdded || 0) || 0) - (Date.parse(a.dateAdded || 0) || 0));
  if (inb.length) {
    const ult = inb[0];
    const edad = Date.now() - (Date.parse(ult.dateAdded || 0) || 0);
    if (edad >= 0 && edad < 10 * 60 * 1000) {
      urls = urls.concat(ult.attachments || []);
      if (!texto && ult.body) texto = String(ult.body).trim();
    }
  }
} catch (e) { /* sin API → sólo lo del webhook */ }

const esImagen = u => /\.(jpe?g|png|webp|gif|heic)(\?|$)/i.test(u) || /\/image\//i.test(u);
const enTexto = (texto.match(/https?:\/\/\S+/g) || [])
  .filter(u => /\.(ogg|oga|opus|mp3|m4a|wav|amr|aac|webm|mpeg|mpga)(\?|$)/i.test(u) || /storage\.googleapis\.com\/msgsndr/i.test(u));
const todas = [...new Set(urls.concat(enTexto).filter(u => typeof u === 'string' && /^https?:\/\//.test(u)))];
for (const u of todas) texto = texto.split(u).join(' ').replace(/\s+/g, ' ').trim();
const imagenes = todas.filter(esImagen);
const audio = todas.filter(u => !esImagen(u));   // lo que no es imagen se intenta transcribir (si falla, se ignora)
if (imagenes.length) texto = (texto ? texto + ' ' : '') + '[El usuario envió una imagen que no puedes ver]';
return [{ json: { texto, audio } }];"""

ESTADO_ADD = r"""const tags = (hit.tags || []).map(t => String(t).toLowerCase());
const pausado = tags.includes('bot_pausado');  // PRE-BSP-0923 · lo pone la tool elevar; se saca a mano para reactivar el bot
"""

BURBUJAS = r"""// Una burbuja = un mensaje de WhatsApp (antes eran los campos parte1-3 de ManyChat).  PRE-BSP-0923
const j = $input.first().json || {};
let partes = ((j.mcBody && j.mcBody.fields) || []).map(f => String(f.field_value || '').trim()).filter(Boolean);
if (!partes.length && j.texto) partes = String(j.texto).split(/\n{2,}/).map(s => s.trim()).filter(Boolean);
return partes.map((message, i) => ({ json: { message, burbuja: i + 1, total: partes.length } }));"""


def patch_main(wf):
    if marked(wf):
        return "ya parcheado"
    # 1 · dedup que no mata el flujo
    node(wf, "Check dedup")["alwaysOutputData"] = True
    # 2 · adapter + hash robustos
    node(wf, "Normalize GHL Payload")["parameters"]["jsCode"] = NORMALIZE
    node(wf, "Compute idempotency hash")["parameters"]["jsCode"] = HASH

    # 3 · entrada del bot: GHL → Separamos (sin pasar por Airtable)
    x, y = node(wf, "Responder rápido ManyChat")["position"]
    wf["nodes"].append(http_node(
        "GHL · Conversación", [x + 224, y - 400], "GET",
        f"=https://services.leadconnectorhq.com/conversations/search?locationId={LOC}"
        "&contactId={{ $('Normalize GHL Payload').first().json.contact_id }}",
        version="2021-04-15", flags={"alwaysOutputData": True, "onError": "continueRegularOutput"}))
    wf["nodes"].append(http_node(
        "GHL · Mensajes recientes", [x + 448, y - 400], "GET",
        "=https://services.leadconnectorhq.com/conversations/"
        "{{ (($json.conversations || [])[0] || {}).id || 'sin-conversacion' }}/messages?limit=10",
        version="2021-04-15", flags={"alwaysOutputData": True, "onError": "continueRegularOutput"}))
    link(wf, "Responder rápido ManyChat", "GHL · Conversación")
    link(wf, "GHL · Conversación", "GHL · Mensajes recientes")
    link(wf, "GHL · Mensajes recientes", "Separamos en partes")
    unlink(wf, "Crear primer contacto", "Separamos en partes")
    unlink(wf, "No existe", "Separamos en partes")
    node(wf, "Separamos en partes")["parameters"]["jsCode"] = SEPARAMOS

    # audios: la clasificación la hace el Code; el IF sólo mira si hay algo, y la cadena de audio no rompe
    node(wf, "Hay audios?")["parameters"]["conditions"]["conditions"] = [
        c for c in node(wf, "Hay audios?")["parameters"]["conditions"]["conditions"]
        if c["operator"].get("operation") != "regex"]
    for nm in ("Get_Audio/s", "Transcribir audio/s"):
        node(wf, nm)["onError"] = "continueRegularOutput"

    # 4 · rama Airtable (trazabilidad): sin campos de ManyChat y sin poder cortar el bot
    M = "$('Normalize GHL Payload').first().json"
    for nm in ("Repetido?", "Actualizar ultimo mensaje", "Crear registro"):
        json_replace(node(wf, nm), "$('Webhook').item.json.body.custom_fields.respuesta_definitiva", f"{M}.text")
    cp = node(wf, "Crear primer contacto")
    json_replace(cp, "$('Webhook').first().json.body.custom_fields.respuesta_definitiva", f"({M}.text || '')")
    json_replace(cp, "$('Webhook').first().json.body.first_name", f"{M}.whatsapp_name")
    json_replace(cp, "$('Webhook').first().json.body.last_name", f"{M}.last_name")
    replace_in(node(wf, "Code in JavaScript"),
               "const webhookNode = $('Webhook').first();\nconst body = webhookNode && webhookNode.json && webhookNode.json.body;\n"
               "const custom = body && body.custom_fields;\nconst rawRespuesta = custom && custom.respuesta_definitiva;",
               "// PRE-BSP-0923: el texto viene del adapter de GHL (antes custom_fields.respuesta_definitiva de ManyChat)\n"
               "const rawRespuesta = $('Normalize GHL Payload').first().json.text;")
    for nm in ("Buscar registro", "Existe", "Repetido?", "Actualizar ultimo mensaje", "Crear registro",
               "Tomar todos los mensajes", "Code in JavaScript", "Tomar fuente correcta", "Buscar si ya existe",
               "No existe", "Crear primer contacto"):
        node(wf, nm)["onError"] = "continueRegularOutput"

    # 5 · pausa del bot (tag bot_pausado) antes del agente
    replace_in(node(wf, "Construir estado lead"), "const L = [];", ESTADO_ADD + "const L = [];")
    replace_in(node(wf, "Construir estado lead"),
               "return [{ json: { estado: L.join('\\n'), encontrado: true } }];",
               "return [{ json: { estado: L.join('\\n'), encontrado: true, pausado } }];")
    cx, cy = node(wf, "Construir estado lead")["position"]
    wf["nodes"].append(if_bool("¿Bot pausado?", [cx + 110, cy - 180], "={{ $json.pausado === true }}"))
    set_targets(wf, "Construir estado lead", 0, ["¿Bot pausado?"])
    set_targets(wf, "¿Bot pausado?", 0, [])
    set_targets(wf, "¿Bot pausado?", 1, ["Agente IA WPP"])

    # 6 · guardrail de promesa fantasma: leer la salida real del formateador, estado desde GHL, tuteo
    dp = node(wf, "Detectar promesa fantasma")
    replace_in(dp, "const item = $input.first();\nconst p1 = String(item.json.parte1 || '');\n"
                   "const p2 = String(item.json.parte2 || '');\nconst p3 = String(item.json.parte3 || '');",
               "const item = $input.first();\n// PRE-BSP-0923: el formateador (jsonOutput) devuelve las partes en message.content\n"
               "const P = (item.json && item.json.message && item.json.message.content) || item.json || {};\n"
               "const p1 = String(P.parte1 || '');\nconst p2 = String(P.parte2 || '');\nconst p3 = String(P.parte3 || '');")
    replace_in(dp, "  lead = $('Buscar si ya existe').first().json || {};",
               "  const gc = (($('GHL · Get contact (estado)').first().json || {}).contact) || {};\n"
               "  const cf = {}; for (const x of (gc.customFields || [])) cf[x.id] = x.value;\n"
               "  lead = { 'Programa interés': cf['xK2NFqtz1DYUw3gYdn8I'] || '', 'Nombre': gc.firstName || '' };")
    replace_in(dp, "`Perdón, ${salut}me anticipé — para reservar la asesoría necesito que elijas tu horario directo "
                   "en el link, así se sincroniza con la agenda de ${link.experto}`",
               "`Perdón, ${salut}me adelanté: para reservar la asesoría necesito que elijas tu horario directo "
               "en el link, así se sincroniza con la agenda de ${link.experto}`")
    replace_in(dp, "`Vos elegís día y hora, y me llega la confirmación automáticamente. Si tenés alguna duda antes "
                   "de la llamada, escribime por aquí`",
               "`Tú eliges día y hora, y me llega la confirmación automáticamente. Si tienes alguna duda antes "
               "de la llamada, escríbeme por aquí`")

    # 7 · nombre del lead para el guardrail de burbujas: desde GHL (Airtable ya no corre antes)
    replace_in(node(wf, "Normalizar burbujas"),
               "    const lead = $('Buscar si ya existe').first().json;\n"
               "    nombre = String((lead && lead.Nombre) || '').trim().split(' ')[0];",
               "    const lead = (($('GHL · Get contact (estado)').first().json || {}).contact) || {};  // PRE-BSP-0923\n"
               "    nombre = String(lead.firstName || '').trim().split(' ')[0];")

    # \b no entiende la ñ: con una lead "Ana", "mañana" perdía "ana" ("mañ a las 10"). Límite Unicode.
    replace_in(node(wf, "Normalizar burbujas"),
               "const re = new RegExp('\\\\b' + nombre.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&') + '\\\\b', 'gi');",
               "const re = new RegExp('(?<![\\\\p{L}\\\\p{N}])' + nombre.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&') "
               "+ '(?![\\\\p{L}\\\\p{N}])', 'giu');  // PRE-BSP-0923")
    # el guardrail deja pasar una respuesta que ya trae link: reconocer los dos dominios (B2 pasa a vtr)
    replace_in(dp, "if (/promo\\.venttur\\.com\\//i.test(fullText)) {",
               "if (/(promo\\.venttur\\.com|vtr\\.[TU-DOMINIO])\\//i.test(fullText)) {")

    # 8 · envío: una burbuja por mensaje, en orden y con pausa
    bx, by = node(wf, "Normalizar burbujas")["position"]
    wf["nodes"].append(code_node("Burbujas → mensajes", [bx + 180, by - 228], BURBUJAS))
    set_targets(wf, "Normalizar burbujas", 0, ["Burbujas → mensajes"])
    set_targets(wf, "Burbujas → mensajes", 0, ["Enviar WPP"])
    ew = node(wf, "Enviar WPP")
    ew["parameters"]["jsonBody"] = ("={{ JSON.stringify({ type: 'WhatsApp', contactId: "
                                    "$('Normalize GHL Payload').first().json.contact_id, message: $json.message }) }}")
    ew["parameters"]["options"] = {"batching": {"batch": {"batchSize": 1, "batchInterval": 1500}}}
    node(wf, "Envió link?")["executeOnce"] = True
    return "parcheado"


# ───────────────────────── ELEVAR ─────────────────────────
def patch_elevar(wf):
    if marked(wf):
        return "ya parcheado"
    n1 = node(wf, "1. PUT dnd:true (pausar bot)")
    n1["name"] = "1. Tag bot_pausado (pausar bot)"
    n1["notes"] = (f"{MARK}: antes era dnd:true. El DND de GHL bloquea también los mensajes del asesor y el main "
                   "no lo miraba. Ahora el main corta si el contacto tiene el tag bot_pausado. Para reactivar el "
                   "bot: sacar el tag en GHL.")
    n1["parameters"].update({"method": "POST",
                             "url": "=https://services.leadconnectorhq.com/contacts/{{ $json.contact_id }}/tags",
                             "jsonBody": "={{ JSON.stringify({ tags: ['bot_pausado'] }) }}"})
    wf["connections"]["1. Tag bot_pausado (pausar bot)"] = wf["connections"].pop("1. PUT dnd:true (pausar bot)")
    for src in wf["connections"].values():
        for lst in src.get("main", []):
            for c in lst:
                if c["node"] == "1. PUT dnd:true (pausar bot)":
                    c["node"] = "1. Tag bot_pausado (pausar bot)"
    tg = node(wf, "3. Telegram notify")
    T = "$('When Executed by Another Workflow').first().json"
    tg["parameters"]["text"] = (
        "=🚨 Lead elevado — VTR (bot pausado)\n\n"
        f"Contacto: https://app.gohighlevel.com/v2/location/{LOC}/contacts/detail/{{{{ {T}.contact_id }}}}\n"
        f"Asignado a: {{{{ {T}.user_id }}}}\n\nResumen:\n{{{{ {T}.resumen }}}}\n\n"
        "Para devolverle la conversación al bot: sacar el tag bot_pausado.")
    tg["parameters"]["additionalFields"] = {}   # sin Markdown: un _ o * del resumen rompía el envío
    tg["onError"] = "continueRegularOutput"
    return "parcheado"


# ───────────────────────── W6 ─────────────────────────
W6_CITA = r"""
// PRE-BSP-0923 · Si la fecha del webhook no se pudo leer (GHL manda {{appointment.start_time}} formateado, no
// ISO), se toma de la API: la cita más reciente del contacto.
let startIso = start;
if (!fecha || !meeting) {
  try {
    const r = $('GHL · Citas del contacto').first().json || {};
    const evs = (r.events || []).filter(e => e && e.startTime && !/cancel/i.test(e.appointmentStatus || ''));
    evs.sort((a, b) => (Date.parse(b.dateAdded || b.startTime) || 0) - (Date.parse(a.dateAdded || a.startTime) || 0));
    const ev = evs[0];
    if (ev) {
      if (!fecha) {
        let dt = DateTime.fromISO(String(ev.startTime).replace(' ', 'T'), { setZone: true });
        if (!/[zZ]|[+-]\d\d:?\d\d$/.test(String(ev.startTime))) dt = DateTime.fromISO(String(ev.startTime).replace(' ', 'T'), { zone: 'America/Mexico_City' });
        dt = dt.setZone('America/Mexico_City');
        if (dt.isValid) { fecha = dt.toFormat("dd/MM 'a las' HH:mm"); startIso = dt.toISO(); }
      }
      if (!meeting && ev.address && /^https?:\/\//.test(ev.address)) meeting = ev.address;
    }
  } catch (e) {}
}
"""


def patch_w6(wf):
    if marked(wf):
        return "ya parcheado"
    nb = node(wf, "Normalize + build msg")
    replace_in(nb, "const meeting    = (p.meeting_link || p.meeting_location || p.address || '').toString();",
               "let meeting    = (p.meeting_link || p.meeting_location || p.address || '').toString();\n"
               "if (meeting && !/^https?:\\/\\//.test(meeting)) meeting = '';")
    # el bloque de la API va después del parseo del webhook y antes de armar el mensaje
    replace_in(nb, "let message =", W6_CITA + "\nlet message =")
    x, y = node(wf, "Webhook: appointment GHL")["position"]
    wf["nodes"].append(http_node(
        "GHL · Citas del contacto", [x + 110, y + 200], "GET",
        "=https://services.leadconnectorhq.com/contacts/{{ ($json.body || $json).contact_id || ($json.body || $json).contactId }}/appointments",
        flags={"alwaysOutputData": True, "onError": "continueRegularOutput"}))
    set_targets(wf, "Webhook: appointment GHL", 0, ["GHL · Citas del contacto"])
    set_targets(wf, "GHL · Citas del contacto", 0, ["Normalize + build msg"])
    replace_in(nb, "const p = $json.body || $json;",
               "const p = $('Webhook: appointment GHL').first().json.body || $('Webhook: appointment GHL').first().json;")
    # el marcado de la cita NO puede depender de que el WhatsApp salga (fuera de ventana 24 h, sin chat, etc.)
    node(wf, "1. Enviar confirmación (WhatsApp)")["onError"] = "continueRegularOutput"
    node(wf, "2. Marcar agendan_cita=true")["onError"] = "continueRegularOutput"
    return "parcheado"


# ───────────────────────── RESCATE ─────────────────────────
def patch_rescate(wf):
    if marked(wf):
        return "ya parcheado"
    for n in wf["nodes"]:
        cr = n.get("credentials") or {}
        if "httpHeaderAuth" in cr and cr["httpHeaderAuth"]["id"] != GHL_CRED["httpHeaderAuth"]["id"]:
            n["credentials"] = copy.deepcopy(GHL_CRED)
    # links: mismas rutas en vtr hasta B5 (dominio-links-agente.py --a promo los vuelve)
    for nm in ("Code: Fase 1 (GHL)", "Code: Fase 2 (GHL)"):
        json_replace(node(wf, nm), "promo.venttur.com", "vtr.[TU-DOMINIO]")
        # no rescatar a quien el asesor ya tomó o cerró
        replace_in(node(wf, nm), "const agendo = ",
                   "const _tags = (contact.tags || []).map(t => String(t).toLowerCase()); "
                   "const _est = ((cfs.find ? cfs.find(f => f.id === 'Omg1BvHmpXR0MMGsrpFh') : null) || {}).value || ''; "
                   "const _fuera = _tags.includes('bot_pausado') || /cerrada|cita confirmada/i.test(String(_est)); /* PRE-BSP-0923 */ "
                   "const agendo = _fuera || ")
    # Fase 2 dentro de la ventana de 24 h de WhatsApp (45 min + 22 h desde el link): a las 24 h + 45 min un
    # mensaje libre ya no sale
    node(wf, "Wait: 24 hrs")["parameters"]["amount"] = 22
    node(wf, "Wait: 24 hrs")["notes"] = f"{MARK}: 22 h (antes 24) para caer dentro de la ventana de 24 h de WhatsApp."
    for nm in ("GHL: Send WhatsApp Fase 1", "GHL: Send WhatsApp Fase 2", "GHL: addTag no_mapeado",
               "GHL: addTag link_abandonado_frio", "GHL: Move stage Abandonado frío"):
        node(wf, nm)["onError"] = "continueRegularOutput"
    # memoria en el formato real de LangChain ({type, data:{content}}): con {type, content} el agente la leía vacía
    replace_in(node(wf, "Build Rescate Memory (Fase 1)"),
               "const system = { type: 'system', content: `",
               "const system = { type: 'system', data: { content: `")
    replace_in(node(wf, "Build Rescate Memory (Fase 1)"),
               "pero no agendó.` }; const ai = { type: 'ai', content: c.message || '' };",
               "pero no agendó.` } }; const ai = { type: 'ai', data: { content: c.message || '' } }; /* PRE-BSP-0923 */")
    replace_in(node(wf, "Build Rescate Memory (Fase 2)"),
               "ai_message: { type: 'ai', content: c.message || '' }",
               "ai_message: { type: 'ai', data: { content: c.message || '' } } /* PRE-BSP-0923 */")
    return "parcheado"


# ───────────────────────── DESPACHADOR ─────────────────────────
def patch_despachador(wf):
    if marked(wf):
        return "ya parcheado"
    replace_in(node(wf, "Seleccionar (tope-2 + prioridad)"),
               "  if (booked.has(c.id)) return false;",
               "  if (booked.has(c.id)) return false;\n"
               "  if ((c.tags || []).map(t => String(t).toLowerCase()).includes('bot_pausado')) return false;  // PRE-BSP-0923 · lo tiene un asesor")
    return "parcheado"


# ───────────────────────── CLASIFICADOR ─────────────────────────
NOTA_PICK = r"""// Un solo resumen por contacto, que se actualiza (antes: una nota nueva por cada mensaje).  PRE-BSP-0923
const PREF = '🤖 Resumen del bot';
const notas = ($json.notes || []);
const previa = notas.find(n => String(n.body || '').startsWith(PREF));
const w = $('Preparar writes').first().json;
return [{ json: { contactId: w.contactId, noteId: previa ? previa.id : '', body: PREF + ' (se actualiza solo)\n\n' + (w.resumen || '') } }];"""


def patch_clasificador(wf):
    if marked(wf):
        return "ya parcheado"
    node(wf, "Clasificar (rúbrica 5 tareas)")["credentials"] = copy.deepcopy(OPENAI_VTR)
    add = node(wf, "Add nota resumen (GHL)")
    x, y = add["position"]
    add["name"] = "POST nota resumen (GHL)"
    add["parameters"]["url"] = "=https://services.leadconnectorhq.com/contacts/{{ $json.contactId }}/notes"
    add["parameters"]["jsonBody"] = "={{ JSON.stringify({ body: $json.body }) }}"
    put = copy.deepcopy(add)
    put.update({"name": "PUT nota resumen (GHL)", "id": str(uuid.uuid4()), "position": [x, y + 180]})
    put["parameters"]["method"] = "PUT"
    put["parameters"]["url"] = "=https://services.leadconnectorhq.com/contacts/{{ $json.contactId }}/notes/{{ $json.noteId }}"
    wf["nodes"].append(put)
    getn = http_node("GET notas (GHL)", [x - 220, y - 180], "GET",
                     "=https://services.leadconnectorhq.com/contacts/{{ $('Preparar writes').first().json.contactId }}/notes",
                     flags={"alwaysOutputData": True, "onError": "continueRegularOutput"})
    wf["nodes"].append(getn)
    wf["nodes"].append(code_node("Elegir nota", [x - 40, y - 180], NOTA_PICK))
    iff = if_bool("¿Nota existente?", [x + 120, y - 180], "={{ !!$json.noteId }}")
    wf["nodes"].append(iff)
    old_next = wf["connections"].pop("Add nota resumen (GHL)")["main"][0]
    set_targets(wf, "Set tipo_contacto (GHL)", 0, ["GET notas (GHL)"])
    set_targets(wf, "GET notas (GHL)", 0, ["Elegir nota"])
    set_targets(wf, "Elegir nota", 0, ["¿Nota existente?"])
    set_targets(wf, "¿Nota existente?", 0, ["PUT nota resumen (GHL)"])
    set_targets(wf, "¿Nota existente?", 1, ["POST nota resumen (GHL)"])
    wf["connections"]["POST nota resumen (GHL)"] = {"main": [old_next]}
    wf["connections"]["PUT nota resumen (GHL)"] = {"main": [copy.deepcopy(old_next)]}
    return "parcheado"


# ───────────────────────── W14 ─────────────────────────
def patch_w14(wf):
    if marked(wf):
        return "ya parcheado"
    q = node(wf, "GHL Query OP·Bot")
    q["parameters"]["headerParameters"] = {"parameters": [{"name": "Version", "value": "2021-07-28"}]}
    q["notes"] = f"{MARK}: faltaba el header Version (GHL responde 4xx sin él)."
    return "parcheado"


PATCHES = [("main", patch_main), ("elevar", patch_elevar), ("w6", patch_w6), ("rescate", patch_rescate),
           ("despachador", patch_despachador), ("clasificador", patch_clasificador), ("w14", patch_w14)]


def save(wf, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(wf, ensure_ascii=False, indent=1))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    execute = "--execute" in sys.argv
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
    shas = []
    for key, fn in PATCHES:
        if only and key not in only:
            continue
        wid = IDS[key]
        code, wf = api("GET", f"/workflows/{wid}")
        if code != 200:
            raise SystemExit(f"❌ GET {key} {wid}: {code} {wf}")
        if wf.get("active"):
            print(f"⚠️  {key} ({wid}) está ACTIVO: no se toca")
            continue
        antes = copy.deepcopy(wf)
        res = fn(wf)
        if res != "parcheado":
            print(f"↷ {key:12s} {wid} · {res}")
            continue
        if not execute:
            print(f"[dry-run] {key:12s} {wid} · aplicaría el parche ({len(antes['nodes'])} → {len(wf['nodes'])} nodos)")
            continue
        s1 = save(antes, OUT / "pre" / f"{key}.json")
        body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
                "settings": {k: v for k, v in (wf.get("settings") or {}).items() if k in SETTINGS_OK}}
        code, resp = api("PUT", f"/workflows/{wid}", body)
        if code != 200:
            raise SystemExit(f"❌ PUT {key}: {code} {resp}\n   snapshot pre en {OUT / 'pre' / (key + '.json')}")
        code, post = api("GET", f"/workflows/{wid}")
        s2 = save(post, OUT / "post" / f"{key}.json")
        ok = marked(post) and not post.get("active")
        print(f"{'✅' if ok else '❌'} {key:12s} {wid} · {len(antes['nodes'])} → {len(post['nodes'])} nodos · activo={post.get('active')}")
        shas.append((key, wid, s1, s2))
    if shas:
        (OUT / "sha256.txt").write_text("".join(f"{k} {w} pre={a} post={b}\n" for k, w, a, b in shas))


if __name__ == "__main__":
    main()
