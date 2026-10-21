"""
FASE 4 · Genera el staging main '[Venttur] GHL staging (Telegram test)' — NO toca los vivos.
Increment 1 (testeable SIN GHL): Telegram Trigger → Normalizar payload → Agente IA WPP
(reusa gpt-4o + system prompt 46.8K + Postgres memory del main vivo) → Enviar Telegram.
- Deja fuera (se agrega post-reset GHL): context builder gap#1 (lee Contact GHL), tools
  crear_contacto/elevar→GHL, send free-form GHL, despachador, audio, dedup.
- INACTIVO. Credencial Telegram SIN bindear (el usuario crea un bot VTR dedicado y lo bindea;
  un bot solo tiene UN webhook → no reusar el compartido).
Crea via n8n API. Idempotente por nombre (si ya existe, no duplica: reporta el id).
"""
import json, os, sys, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(__file__))
from _ghl_client import load_n8n, UA

HERE = os.path.dirname(__file__)
LIVE = os.path.join(HERE, "..", "snapshots", "n8n-vivo-2026-09-03", "k3aivKSP67S97IHn___Venttur_.json")
BASE, KEY = load_n8n(); BASE = BASE.rstrip("/")
NAME = "[Venttur] GHL staging (Telegram test)"

def n8n(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method,
        headers={"X-N8N-API-KEY": KEY, "User-Agent": UA, "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode(); return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")

# idempotencia: buscar por nombre
_, idx = n8n("GET", "/api/v1/workflows?limit=250")
for w in idx.get("data", []):
    if w.get("name") == NAME:
        print(f"= ya existe: {w['id']} ({NAME}) — no duplico"); sys.exit(0)

live = json.load(open(LIVE, encoding="utf-8"))
lv = {n["name"]: n for n in live["nodes"]}

def clone(nm):
    return json.loads(json.dumps(lv[nm]))

# --- nodos reusados del vivo ---
model = clone("OpenAI Chat Model"); model["position"] = [-40, 220]
memory = clone("Postgres Chat Memory"); memory["position"] = [140, 220]
memory["parameters"]["sessionKey"] = "={{ $('Normalizar payload').first().json.sessionKey }}"
agent = clone("Agente IA WPP"); agent["position"] = [180, 0]
# user message simple (el [ESTADO DEL LEAD] gap#1 se agrega con el context builder GHL post-reset)
agent["parameters"]["text"] = "=Mensaje del usuario: {{ $('Normalizar payload').first().json.message }}\nCanal: telegram (test)\nFecha: {{ $now }}"

# --- entry Telegram + normalize ---
tg_trigger = {
    "parameters": {"updates": ["message"], "additionalFields": {}},
    "id": "tg-trigger-vtr", "name": "Telegram Trigger",
    "type": "n8n-nodes-base.telegramTrigger", "typeVersion": 1.2,
    "position": [-460, 0], "webhookId": "vtr-staging-tg-webhook-1",
    "credentials": {},  # ⚠️ el usuario bindea un bot VTR dedicado
}
normalize = {
    "parameters": {"jsCode": (
        "const u = $input.first().json;\n"
        "const msg = u.message || u.edited_message || {};\n"
        "const text = msg.text || msg.caption || '';\n"
        "const chatId = String((msg.chat||{}).id || '');\n"
        "const from = msg.from || {};\n"
        "const name = ((from.first_name||'') + ' ' + (from.last_name||'')).trim();\n"
        "// identidad de test (patrón HPF): email sintético que GHL aceptará luego; sessionKey por chat\n"
        "return [{ json: {\n"
        "  message: text,\n"
        "  chatId,\n"
        "  sessionKey: chatId,\n"
        "  canal: 'telegram',\n"
        "  name,\n"
        "  email: `tg-${chatId}@venttur.test`,\n"
        "  _raw: u,\n"
        "}}];")},
    "id": "tg-normalize-vtr", "name": "Normalizar payload",
    "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [-260, 0],
}
tg_send = {
    "parameters": {"chatId": "={{ $('Normalizar payload').first().json.chatId }}",
                   "text": "={{ $json.output }}", "additionalFields": {"appendAttribution": False}},
    "id": "tg-send-vtr", "name": "Enviar Telegram",
    "type": "n8n-nodes-base.telegram", "typeVersion": 1.2, "position": [560, 0],
    "credentials": {},  # mismo bot VTR
}

nodes = [tg_trigger, normalize, model, memory, agent, tg_send]
connections = {
    "Telegram Trigger": {"main": [[{"node": "Normalizar payload", "type": "main", "index": 0}]]},
    "Normalizar payload": {"main": [[{"node": "Agente IA WPP", "type": "main", "index": 0}]]},
    "OpenAI Chat Model": {"ai_languageModel": [[{"node": "Agente IA WPP", "type": "ai_languageModel", "index": 0}]]},
    "Postgres Chat Memory": {"ai_memory": [[{"node": "Agente IA WPP", "type": "ai_memory", "index": 0}]]},
    "Agente IA WPP": {"main": [[{"node": "Enviar Telegram", "type": "main", "index": 0}]]},
}

payload = {"name": NAME, "nodes": nodes, "connections": connections,
           "settings": live.get("settings", {"executionOrder": "v1"})}
st, d = n8n("POST", "/api/v1/workflows", payload)
if st in (200, 201) and d.get("id"):
    print(f"✅ creado: {d['id']} · {NAME} (INACTIVO)")
    # verificación read-back
    _, rb = n8n("GET", f"/api/v1/workflows/{d['id']}")
    print(f"   read-back nodos: {len(rb.get('nodes',[]))} · active: {rb.get('active')}")
    print("   nodos:", [n["name"] for n in rb.get("nodes", [])])
else:
    print(f"❌ HTTP {st}: {json.dumps(d)[:400]}")
