"""
FASE 4 · Increment 4b — tool elevar → GHL (handoff): Assign to User + pausar bot (DND).
Agrega al staging 3sLd7KY3o8I7NvXi un tool `elevar` (toolHttpRequest) conectado por ai_tool.
Hace PUT /contacts/{id} {assignedTo: <default Mauricio>, dnd:true} — assign + pausa (primitivos validados).
El contactId sale de 'Buscar Contact GHL'. La NOTIFICACIÓN a Mauricio&Max (email+app, fix "Notify:0")
NO va acá: se resuelve con un Workflow nativo de GHL (registrado como gap). Idempotente.
Uso: python3 gen-staging-inc4b.py
"""
import json, os, sys, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(__file__))
from _ghl_client import load_n8n, UA
BASE, KEY = load_n8n(); BASE = BASE.rstrip("/"); WID = "3sLd7KY3o8I7NvXi"
CRED_ID = "YkVmaA4jlRbO1TQD"; CRED_NAME = "GHL VTR (PIT)"
MAURICIO = "cXRMSnBx81rYivxQruKX"  # default de asignación v1 (ver gap: asignar al asesor del programa)

def n8n(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method,
        headers={"X-N8N-API-KEY": KEY, "User-Agent": UA, "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode(); return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")

# url con el contactId resuelto del Buscar Contact GHL
url = ("=https://services.leadconnectorhq.com/contacts/"
       "{{ $('Buscar Contact GHL').first().json.contacts && $('Buscar Contact GHL').first().json.contacts[0] "
       "? $('Buscar Contact GHL').first().json.contacts[0].id : '' }}")
elevar = {
    "parameters": {
        "method": "PUT",
        "url": url,
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
        "jsonBody": '={"assignedTo": "' + MAURICIO + '", "dnd": true}',
        "toolDescription": ("Deriva la conversacion a un humano. Actívala SOLO cuando el lead pida "
                            "hablar con una persona/emergencia, o repita el MISMO mensaje 2+ veces "
                            "consecutivas. Asigna a un asesor y pausa el bot para ese contacto."),
    },
    "id": "vtr-elevar-ghl", "name": "elevar",
    "type": "@n8n/n8n-nodes-langchain.toolHttpRequest", "typeVersion": 1.1,
    "position": [560, 260],
    "credentials": {"httpHeaderAuth": {"id": CRED_ID, "name": CRED_NAME}},
}

st, wf = n8n("GET", f"/api/v1/workflows/{WID}")
assert st == 200
def upsert(node):
    for i, n in enumerate(wf["nodes"]):
        if n["name"] == node["name"]: wf["nodes"][i] = node; return
    wf["nodes"].append(node)
upsert(elevar)
conns = wf["connections"]
conns.setdefault("elevar", {})["ai_tool"] = [[{"node": "Agente IA WPP", "type": "ai_tool", "index": 0}]]
put = {"name": wf["name"], "nodes": wf["nodes"], "connections": conns,
       "settings": wf.get("settings", {"executionOrder": "v1"})}
st, d = n8n("PUT", f"/api/v1/workflows/{WID}", put)
print("PUT →", st)
if st == 200:
    _, rb = n8n("GET", f"/api/v1/workflows/{WID}")
    print("nodos:", [n["name"] for n in rb["nodes"]])
    tools = [k for k,v in rb["connections"].items() if "ai_tool" in v]
    print("tools (ai_tool):", tools)
else:
    print(json.dumps(d)[:500])
