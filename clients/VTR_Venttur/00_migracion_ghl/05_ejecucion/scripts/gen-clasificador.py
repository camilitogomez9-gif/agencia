"""
FASE 4 · Reconstrucción 1:1 del clasificador post-conversación (Cualificado).
Crea 'vtr-clasificador-postconv-v1' — INACTIVO. Porta VERBATIM el nodo OpenAI del vivo
`resumen-etiquetas-seguimientos` (misma rúbrica de 5 tareas, gpt-4o-mini temp 0, jsonOutput) y
cablea la salida `cualificado`: IF cualificado=='1' → agrega el tag `cualificado` al Contact.
Fiel al checkbox Airtable (representación tag, no depende del ciclo de vida de la Opportunity).
Las otras salidas (tags/tipo/resumen/asesoria) quedan computadas por el LLM; su cableado a CFs es
incremento aparte (ver REGISTRO). NO toca vivos. Idempotente por nombre.
Uso: python3 gen-clasificador.py
"""
import json, os, sys, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(__file__))
from _ghl_client import load_n8n, UA
BASE, KEY = load_n8n(); BASE = BASE.rstrip("/")
NAME = "vtr-clasificador-postconv-v1"
CRED_GHL = {"id": "YkVmaA4jlRbO1TQD", "name": "GHL VTR (PIT)"}
OPENAI_CRED = {"id": "Fa3aaCsYTBS79y3Y", "name": "OpenAI la agencia®"}
TAG = "cualificado"
LIVE = os.path.join(os.path.dirname(__file__), "..", "..", "..", "03_workflows", "vivo-2026-08-17", "resumen-etiquetas-seguimientos.json")

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

# --- portar el nodo OpenAI vivo verbatim, swap de la conversación ---
live = json.load(open(LIVE, encoding="utf-8"))
o_live = [n for n in live["nodes"] if n["name"] == "OpenAI"][0]
params = json.loads(json.dumps(o_live["parameters"]))
c = params["messages"]["values"][0]["content"]
c = c.replace("{{ $('Obtener historial conversación').item.json.conversation }}",
              "{{ $json.conversation }}")
params["messages"]["values"][0]["content"] = c

trigger = {"parameters": {"workflowInputs": {"values": [
        {"name": "conversation", "type": "string"}, {"name": "contactId", "type": "string"}]}},
    "id": "clf-trigger", "name": "When Executed by Another Workflow",
    "type": "n8n-nodes-base.executeWorkflowTrigger", "typeVersion": 1.1, "position": [-420, 0]}

classifier = {"parameters": params, "id": "clf-openai", "name": "Clasificar (rúbrica 5 tareas)",
    "type": "@n8n/n8n-nodes-langchain.openAi", "typeVersion": 1.8, "position": [-180, 0],
    "credentials": {"openAiApi": OPENAI_CRED}}

iff = {"parameters": {"conditions": {"combinator": "and", "conditions": [{
        "id": "c1", "leftValue": "={{ $json.message.content.cualificado }}",
        "operator": {"name": "filter.operator.equals", "operation": "equals", "type": "string"},
        "rightValue": "1"}], "options": {"caseSensitive": True, "typeValidation": "strict", "version": 2}},
    "options": {}}, "id": "clf-if", "name": "¿Cualificado?", "type": "n8n-nodes-base.if",
    "typeVersion": 2.2, "position": [80, 0]}

addtag = {"parameters": {"method": "POST",
        "url": "=https://services.leadconnectorhq.com/contacts/{{ $('When Executed by Another Workflow').first().json.contactId }}/tags",
        "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
        "sendHeaders": True, "parametersHeaders": {"values": [
            {"name": "Version", "value": "2021-07-28"}, {"name": "Content-Type", "value": "application/json"},
            {"name": "User-Agent", "value": UA}]},
        "sendBody": True, "specifyBody": "json", "jsonBody": '={"tags":["' + TAG + '"]}',
        "options": {}},
    "id": "clf-tag", "name": "Tag cualificado (GHL)", "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2, "position": [300, -80], "onError": "continueRegularOutput",
    "credentials": {"httpHeaderAuth": CRED_GHL}}

note = {"parameters": {"content": ("## Clasificador post-conversación (1:1 del vivo)\n\nINACTIVO. Porta la rúbrica de 5 tareas "
        "(tags/tipo/resumen/asesoria/**cualificado**). Hoy cablea SOLO `cualificado→tag`.\n\n"
        "**Criterio cualificado='1' (las 3):** 2º/3º idioma · escuela privada+bilingüe · edad del programa "
        "(10-17 SummerCamp / 13-17 AñoAcad+Boarding / 18-30 Pathway+GapYear).\n\n"
        "Pendiente: disparo real (post-conversación, hoy 8h) + cableado de tags/tipo/resumen/asesoria."),
        "height": 240, "width": 340}, "id": "clf-note", "name": "Sticky Note",
        "type": "n8n-nodes-base.stickyNote", "typeVersion": 1, "position": [-180, 160]}

nodes = [trigger, classifier, iff, addtag, note]
connections = {
    "When Executed by Another Workflow": {"main": [[{"node": "Clasificar (rúbrica 5 tareas)", "type": "main", "index": 0}]]},
    "Clasificar (rúbrica 5 tareas)": {"main": [[{"node": "¿Cualificado?", "type": "main", "index": 0}]]},
    "¿Cualificado?": {"main": [[{"node": "Tag cualificado (GHL)", "type": "main", "index": 0}], []]},
}
payload = {"name": NAME, "nodes": nodes, "connections": connections, "settings": {"executionOrder": "v1"}}
st, d = n8n("POST", "/api/v1/workflows", payload)
if st in (200, 201) and d.get("id"):
    print(f"✅ creado: {d['id']} · {NAME} (INACTIVO)")
    _, rb = n8n("GET", f"/api/v1/workflows/{d['id']}")
    print("   nodos:", [n["name"] for n in rb["nodes"]], "· active:", rb.get("active"))
    # sanity: la conversación quedó swappeada
    oc = [n for n in rb["nodes"] if n["name"].startswith("Clasificar")][0]
    print("   conv ref OK:", "$json.conversation" in oc["parameters"]["messages"]["values"][0]["content"])
else:
    print(f"❌ HTTP {st}: {json.dumps(d)[:500]}")
