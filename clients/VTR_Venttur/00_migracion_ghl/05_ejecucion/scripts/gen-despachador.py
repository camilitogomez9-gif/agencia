"""
FASE 4 · Increment 6 (pieza nurturing) — Despachador proactivo único con TOPE-2.
Crea el workflow n8n 'vtr-despachador-proactivo-v1' — INACTIVO (es un cron; no debe correr
hasta que existan templates + se cierren los gaps). NO toca vivos. Idempotente por nombre.

Corazón = motor de selección con tope-2 (validado contra GHL real 2026-09-07):
  Schedule → Query candidatos rescate (link_enviado=true) → Seleccionar (Code: tope-2 null-safe,
  excluye terminal, prioridad rescate>nurturing, 1 toque/contacto, cota de recencia)
  → [Enviar template GHL (PLACEHOLDER, disabled)] → [Siembra memoria Supabase] → [Update toques]

GAPS marcados (ver REGISTRO §BLOQUEANTES):
  - "sin cita agendada" NO se excluye por CF (la cita vive en el pipeline operativo) → cruzar con
    opportunities en etapas booked; se completa con el increment de booking (asunción j, gated).
  - cota de recencia: parámetro RECENCIA_DIAS (default 30) — confirmar ventana con el cliente.
  - templates Meta inexistentes → el nodo de envío es placeholder hasta B-07.
  - paginación completa del query (v1 procesa 1 página/run).
Uso: python3 gen-despachador.py
"""
import json, os, sys, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(__file__))
from _ghl_client import load_n8n, UA, GHL
BASE, KEY = load_n8n(); BASE = BASE.rstrip("/")
LOCATION = GHL().location_id
CRED_ID = "YkVmaA4jlRbO1TQD"; CRED_NAME = "GHL VTR (PIT)"
PG_CRED = "ihpvM7nYMdLCwWDP"  # Postgres Venttur (memoria, reusa el del staging)
NAME = "vtr-despachador-proactivo-v1"
cf = json.load(open(os.path.join(os.path.dirname(__file__), "..", "spec", "custom-fields-idmap.json")))["contact"]
L, T, E, UAF = cf["link_enviado"]["id"], cf["toques_enviados"]["id"], cf["estado_conversacion"]["id"], cf["ultima_actividad"]["id"]

def n8n(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method,
        headers={"X-N8N-API-KEY": KEY, "User-Agent": UA, "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode(); return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")

# idempotencia
_, idx = n8n("GET", "/api/v1/workflows?limit=250")
for w in idx.get("data", []):
    if w.get("name") == NAME:
        print(f"= ya existe: {w['id']} — no duplico"); sys.exit(0)

sched = {"parameters": {"rule": {"interval": [{"field": "hours", "hoursInterval": 1}]}},
         "id": "desp-cron", "name": "Cron despachador", "type": "n8n-nodes-base.scheduleTrigger",
         "typeVersion": 1.2, "position": [-420, 0]}

query = {
    "parameters": {
        "method": "POST", "url": "https://services.leadconnectorhq.com/contacts/search",
        "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
        "sendHeaders": True, "parametersHeaders": {"values": [
            {"name": "Version", "value": "2021-07-28"}, {"name": "Content-Type", "value": "application/json"},
            {"name": "Accept", "value": "application/json"}, {"name": "User-Agent", "value": UA}]},
        "sendBody": True, "specifyBody": "json",
        "jsonBody": json.dumps({"locationId": LOCATION, "pageLimit": 100,
            "filters": [{"group": "AND", "filters": [{"field": f"customFields.{L}", "operator": "eq", "value": "true"}]}]}),
        "options": {},
    },
    "id": "desp-query", "name": "Query candidatos rescate", "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2, "position": [-200, 0], "onError": "continueRegularOutput",
    "credentials": {"httpHeaderAuth": {"id": CRED_ID, "name": CRED_NAME}},
}

select_js = (
"// Motor de selección — TOPE-2 (validado vs GHL real 2026-09-07)\n"
"const T='" + T + "', E='" + E + "', L='" + L + "', UAF='" + UAF + "';\n"
"const RECENCIA_DIAS = 30;              // cota de recencia (confirmar con cliente)\n"
"const TERMINAL = ['Cita confirmada'];  // estados que NO se re-tocan (+ Cerrada/perdido cuando exista)\n"
"const r = $json || {}; const cands = r.contacts || (r.body && r.body.contacts) || [];\n"
"const cfv = (c, id) => { for (const x of (c.customFields||[])) if (x.id===id) return x.value; return null; };\n"
"const now = Date.now(); const out = [];\n"
"for (const c of cands) {\n"
"  let toq = cfv(c, T); toq = (toq===null||toq===''||Array.isArray(toq)&&!toq.length)?0:Number(toq);\n"
"  const est = (cfv(c, E)||'').toString().trim();\n"
"  if (TERMINAL.includes(est)) continue;         // ya agendó/cerró\n"
"  if (toq >= 2) continue;                        // TOPE GLOBAL 2\n"
"  const ua = cfv(c, UAF); const uaMs = ua ? Date.parse(ua) : null;\n"
"  if (uaMs && (now - uaMs) > RECENCIA_DIAS*864e5) continue;  // cota de recencia (null = no filtra, TODO)\n"
"  // prioridad: link_enviado=true → rescate. (el query ya trae solo link=true; el carril nurturing\n"
"  //   se agrega como 2do query link_enviado!=true cuando se defina; ver REGISTRO §gaps)\n"
"  out.push({ json: { contactId: c.id, phone: c.phone, firstName: c.firstName,\n"
"    lane: 'rescate', toques_actual: toq, estado: est,\n"
"    // GAP: 'sin cita' no verificable por CF — cruzar con pipeline operativo (booking, asunción j)\n"
"    _needs_cita_check: true } });\n"
"}\n"
"return out;   // 1 item por contacto elegible; el envío es 1 mensaje/contacto/run\n"
)
select = {"parameters": {"jsCode": select_js}, "id": "desp-select", "name": "Seleccionar (tope-2 + prioridad)",
          "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [20, 0]}

send = {  # PLACEHOLDER — templates Meta inexistentes (B-07). DISABLED hasta el cutover.
    "parameters": {"method": "POST",
        "url": "https://services.leadconnectorhq.com/conversations/messages",
        "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
        "sendHeaders": True, "parametersHeaders": {"values": [
            {"name": "Version", "value": "2021-07-28"}, {"name": "Content-Type", "value": "application/json"},
            {"name": "User-Agent", "value": UA}]},
        "sendBody": True, "specifyBody": "json",
        "jsonBody": '={\n  "type": "WhatsApp",\n  "contactId": "{{ $json.contactId }}",\n  "templateId": "PENDIENTE_B-07",\n  "_comment": "PLACEHOLDER: reemplazar por el template Meta aprobado del carril/programa"\n}',
        "options": {}},
    "id": "desp-send", "name": "Enviar template GHL (PLACEHOLDER)", "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2, "position": [240, -120], "disabled": True, "onError": "continueRegularOutput",
    "credentials": {"httpHeaderAuth": {"id": CRED_ID, "name": CRED_NAME}},
}

mem = {  # siembra memoria sintética (patrón existente) — inserta un turno 'ai' por el toque
    "parameters": {"operation": "executeQuery",
        "query": ("INSERT INTO n8n_chat_histories (session_id, message) VALUES "
                  "($1, $2::jsonb)"),
        "options": {"queryReplacement": "={{ [ $json.phone, JSON.stringify({type:'ai', data:{content:'[toque proactivo: '+$json.lane+']'}}) ] }}"}},
    "id": "desp-mem", "name": "Siembra memoria (Supabase)", "type": "n8n-nodes-base.postgres",
    "typeVersion": 2.6, "position": [240, 0], "disabled": True,
    "credentials": {"postgres": {"id": PG_CRED, "name": "Postgres Venttur"}},
}

upd = {  # incrementa toques_enviados + ultimo_toque_at
    "parameters": {"method": "PUT",
        "url": "=https://services.leadconnectorhq.com/contacts/{{ $json.contactId }}",
        "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
        "sendHeaders": True, "parametersHeaders": {"values": [
            {"name": "Version", "value": "2021-07-28"}, {"name": "Content-Type", "value": "application/json"},
            {"name": "User-Agent", "value": UA}]},
        "sendBody": True, "specifyBody": "json",
        "jsonBody": ('={"customFields":[{"id":"' + T + '","value":{{ ($json.toques_actual||0)+1 }}},'
                     '{"id":"' + UAF + '","value":"{{ $now.toISO() }}"}]}'),
        "options": {}},
    "id": "desp-upd", "name": "Update toques (+1)", "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2, "position": [240, 120], "disabled": True, "onError": "continueRegularOutput",
    "credentials": {"httpHeaderAuth": {"id": CRED_ID, "name": CRED_NAME}},
}

note = {"parameters": {"content": ("## Despachador proactivo · TOPE-2\n\nINACTIVO. El motor de selección (Code) está "
        "validado vs GHL real. Los nodos de ENVÍO/MEMORIA/UPDATE están **disabled** hasta:\n"
        "- templates Meta (B-07)\n- excluir 'con cita' vía pipeline operativo (asunción j)\n"
        "- cota de recencia confirmada\n- carril nurturing (2do query link!=true)\n- paginación completa"),
        "height": 260, "width": 320}, "id": "desp-note", "name": "Sticky Note",
        "type": "n8n-nodes-base.stickyNote", "typeVersion": 1, "position": [-200, 180]}

nodes = [sched, query, select, send, mem, upd, note]
connections = {
    "Cron despachador": {"main": [[{"node": "Query candidatos rescate", "type": "main", "index": 0}]]},
    "Query candidatos rescate": {"main": [[{"node": "Seleccionar (tope-2 + prioridad)", "type": "main", "index": 0}]]},
    "Seleccionar (tope-2 + prioridad)": {"main": [[
        {"node": "Enviar template GHL (PLACEHOLDER)", "type": "main", "index": 0},
        {"node": "Siembra memoria (Supabase)", "type": "main", "index": 0},
        {"node": "Update toques (+1)", "type": "main", "index": 0}]]},
}
payload = {"name": NAME, "nodes": nodes, "connections": connections, "settings": {"executionOrder": "v1"}}
st, d = n8n("POST", "/api/v1/workflows", payload)
if st in (200, 201) and d.get("id"):
    print(f"✅ creado: {d['id']} · {NAME} (INACTIVO)")
    _, rb = n8n("GET", f"/api/v1/workflows/{d['id']}")
    print("   nodos:", [n["name"] for n in rb["nodes"]], "· active:", rb.get("active"))
else:
    print(f"❌ HTTP {st}: {json.dumps(d)[:500]}")
