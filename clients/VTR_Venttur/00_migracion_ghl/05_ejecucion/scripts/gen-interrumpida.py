"""
FASE 4 · Barrido "Conversación interrumpida" → GHL/n8n (reconstrucción de wf-estado-interrumpida).
Crea 'vtr-barrido-interrumpida-v1' — INACTIVO. NO toca vivos. Idempotente por nombre.
Cron horario → Query Contacts estado_conversacion='Contestó' → Code (silencio >24h, null-safe,
anti-downgrade: solo 'Contestó'→'Interrumpida') → PUT estado_conversacion='Interrumpida'.
Query por custom field validada (asunción i ✓). SEND del PUT habilitado (es escritura de estado
interna, no canal). Idempotente en efecto (un 'Contestó' pasa a 'Interrumpida' una vez).
Uso: python3 gen-interrumpida.py
"""
import json, os, sys, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(__file__))
from _ghl_client import load_n8n, UA, GHL
BASE, KEY = load_n8n(); BASE = BASE.rstrip("/"); LOCATION = GHL().location_id
NAME = "vtr-barrido-interrumpida-v1"; CRED = {"id": "YkVmaA4jlRbO1TQD", "name": "GHL VTR (PIT)"}
cf = json.load(open(os.path.join(os.path.dirname(__file__), "..", "spec", "custom-fields-idmap.json")))["contact"]
E, UAF = cf["estado_conversacion"]["id"], cf["ultima_actividad"]["id"]

def n8n(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method,
        headers={"X-N8N-API-KEY": KEY, "User-Agent": UA, "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode(); return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")

_, idx = n8n("GET", "/api/v1/workflows?limit=250")
for w in idx.get("data", []):
    if w.get("name") == NAME:
        print(f"= ya existe: {w['id']} — no duplico"); sys.exit(0)

hdr = {"values": [{"name": "Version", "value": "2021-07-28"}, {"name": "Content-Type", "value": "application/json"},
       {"name": "Accept", "value": "application/json"}, {"name": "User-Agent", "value": UA}]}
cron = {"parameters": {"rule": {"interval": [{"field": "hours", "hoursInterval": 1}]}}, "id": "int-cron",
        "name": "Cron 1h", "type": "n8n-nodes-base.scheduleTrigger", "typeVersion": 1.2, "position": [-420, 0]}
query = {"parameters": {"method": "POST", "url": "https://services.leadconnectorhq.com/contacts/search",
        "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendHeaders": True,
        "parametersHeaders": hdr, "sendBody": True, "specifyBody": "json",
        "jsonBody": json.dumps({"locationId": LOCATION, "pageLimit": 100,
            "filters": [{"group": "AND", "filters": [{"field": f"customFields.{E}", "operator": "eq", "value": "Contestó"}]}]}),
        "options": {}}, "id": "int-q", "name": "Query estado=Contestó", "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2, "position": [-220, 0], "onError": "continueRegularOutput", "credentials": {"httpHeaderAuth": CRED}}
select = {"parameters": {"jsCode": (
    "const UAF='" + UAF + "'; const HORAS=24;\n"
    "const cs = (($json.contacts)||[]);\n"
    "const cfv=(c,id)=>{for(const x of (c.customFields||[])) if(x.id===id) return x.value; return null;};\n"
    "const now=Date.now(); const out=[];\n"
    "for(const c of cs){ const ua=cfv(c,UAF); const t=ua?Date.parse(ua):null;\n"
    "  if(t && (now-t) > HORAS*3600e3) out.push({json:{contactId:c.id}});\n"  # null → NO marca (no sabemos silencio)
    "}\n"
    "return out;  // solo los 'Contestó' con silencio > 24h (anti-downgrade: la query ya excluye terminales)\n")},
    "id": "int-sel", "name": "Silencio > 24h", "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [0, 0]}
put = {"parameters": {"method": "PUT", "url": "=https://services.leadconnectorhq.com/contacts/{{ $json.contactId }}",
        "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendHeaders": True,
        "parametersHeaders": hdr, "sendBody": True, "specifyBody": "json",
        "jsonBody": '={"customFields":[{"id":"' + E + '","value":"Interrumpida"}]}', "options": {}},
        "id": "int-put", "name": "Marcar Interrumpida", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
        "position": [200, 0], "onError": "continueRegularOutput", "credentials": {"httpHeaderAuth": CRED}}
note = {"parameters": {"content": ("## Barrido interrumpida\n\nINACTIVO. Query por CF validada. ⚠ ultima_actividad null "
        "en históricos → no se marcan (correcto: no sabemos silencio). Umbral 24h operativo (≠ ~5d del reporte, `09`§6)."),
        "height": 180, "width": 320}, "id": "int-note", "name": "Sticky Note", "type": "n8n-nodes-base.stickyNote",
        "typeVersion": 1, "position": [-220, 160]}
nodes = [cron, query, select, put, note]
connections = {"Cron 1h": {"main": [[{"node": "Query estado=Contestó", "type": "main", "index": 0}]]},
    "Query estado=Contestó": {"main": [[{"node": "Silencio > 24h", "type": "main", "index": 0}]]},
    "Silencio > 24h": {"main": [[{"node": "Marcar Interrumpida", "type": "main", "index": 0}]]}}
st, d = n8n("POST", "/api/v1/workflows", {"name": NAME, "nodes": nodes, "connections": connections, "settings": {"executionOrder": "v1"}})
if st in (200, 201) and d.get("id"):
    print(f"✅ creado: {d['id']} · {NAME} (INACTIVO)")
    _, rb = n8n("GET", f"/api/v1/workflows/{d['id']}"); print("  nodos:", [n["name"] for n in rb["nodes"]], "active:", rb.get("active"))
else:
    print(f"❌ HTTP {st}: {json.dumps(d)[:400]}")
