"""
FASE 4 · Increment 4a — tool crear_contacto → upsert Contact GHL (staging, NO toca vivos).
Agrega al staging 3sLd7KY3o8I7NvXi un tool `crear_contacto` (toolHttpRequest) conectado al
Agente IA WPP por ai_tool. Reemplaza el sub Clientify+Airtable del vivo por UNA sola alta en GHL
(POST /contacts/upsert). nombre/apellido por $fromAI; phone/email deterministas del Normalizar payload.
Idempotente (upsert por name). Uso: python3 gen-staging-inc4a.py
"""
import json, os, sys, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(__file__))
from _ghl_client import load_n8n, UA, GHL
BASE, KEY = load_n8n(); BASE = BASE.rstrip("/"); WID = "3sLd7KY3o8I7NvXi"
LOCATION = GHL().location_id
CRED_ID = "YkVmaA4jlRbO1TQD"; CRED_NAME = "GHL VTR (PIT)"

def n8n(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method,
        headers={"X-N8N-API-KEY": KEY, "User-Agent": UA, "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode(); return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")

# jsonBody del upsert: identidad determinista (phone si hay, sino email sintético) + nombre/apellido por IA
json_body = (
"={{ (() => { const n = $('Normalizar payload').first().json; "
"const b = { locationId: '" + LOCATION + "', "
"firstName: $fromAI('nombre','nombre de pila del lead'), "
"lastName: $fromAI('apellido','apellido del lead') }; "
"if (n.phone) b.phone = n.phone; "
"if (n.email) b.email = n.email; "
"return JSON.stringify(b); })() }}"
)
crear = {
    "parameters": {
        "method": "POST",
        "url": "https://services.leadconnectorhq.com/contacts/upsert",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendHeaders": True,
        "parametersHeaders": {"values": [
            {"name": "Version", "valueProvider": "fieldValue", "value": "2021-07-28"},
            {"name": "Content-Type", "valueProvider": "fieldValue", "value": "application/json"},
            {"name": "Accept", "valueProvider": "fieldValue", "value": "application/json"},
            {"name": "User-Agent", "valueProvider": "fieldValue", "value": UA},
        ]},
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": json_body,
        "toolDescription": ("Da de alta / actualiza al lead en el CRM. Actívala SOLO cuando el lead te "
                            "haya dado su nombre completo (nombre y apellido). Guarda 'nombre' y 'apellido'."),
    },
    "id": "vtr-crear-contacto-ghl", "name": "crear_contacto",
    "type": "@n8n/n8n-nodes-langchain.toolHttpRequest", "typeVersion": 1.1,
    "position": [360, 260],
    "credentials": {"httpHeaderAuth": {"id": CRED_ID, "name": CRED_NAME}},
}

st, wf = n8n("GET", f"/api/v1/workflows/{WID}")
assert st == 200, f"no pude leer staging: {st}"
def upsert(node):
    for i, n in enumerate(wf["nodes"]):
        if n["name"] == node["name"]:
            wf["nodes"][i] = node; return
    wf["nodes"].append(node)
upsert(crear)
# conectar como ai_tool al Agente IA WPP
conns = wf["connections"]
conns.setdefault("crear_contacto", {})["ai_tool"] = [[{"node": "Agente IA WPP", "type": "ai_tool", "index": 0}]]
put = {"name": wf["name"], "nodes": wf["nodes"], "connections": conns,
       "settings": wf.get("settings", {"executionOrder": "v1"})}
st, d = n8n("PUT", f"/api/v1/workflows/{WID}", put)
print("PUT →", st)
if st == 200:
    _, rb = n8n("GET", f"/api/v1/workflows/{WID}")
    print("nodos:", [n["name"] for n in rb["nodes"]])
    print("crear_contacto ai_tool →", rb["connections"].get("crear_contacto"))
else:
    print(json.dumps(d)[:500])
