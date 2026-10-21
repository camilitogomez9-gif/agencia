"""
FASE 4 · Increment 2 — context builder gap#1 sobre el staging (NO toca vivos).
Agrega al staging '[Venttur] GHL staging (Telegram test)' (3sLd7KY3o8I7NvXi):
  Normalizar payload → [Buscar Contact GHL] → [Construir estado lead] → Agente IA WPP
- Buscar Contact GHL: POST /contacts/search por teléfono (fallback email), cred GHL VTR (PIT).
- Construir estado lead: Code que arma [ESTADO DEL LEAD] desde los customFields del contacto
  (lógica validada contra GHL real, réplica del text del main vivo).
- Reescribe el text del Agente IA WPP para inyectar el [ESTADO DEL LEAD] real.
Idempotente: si los nodos ya existen, los actualiza en lugar de duplicar.
Uso: python3 gen-staging-inc2.py
"""
import json, os, sys, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(__file__))
from _ghl_client import load_n8n, UA, GHL

BASE, KEY = load_n8n(); BASE = BASE.rstrip("/")
LOCATION = GHL().location_id
WID = "3sLd7KY3o8I7NvXi"
CRED_ID = "YkVmaA4jlRbO1TQD"; CRED_NAME = "GHL VTR (PIT)"
HERE = os.path.dirname(__file__)
cf = json.load(open(os.path.join(HERE, "..", "spec", "custom-fields-idmap.json")))["contact"]
FID = {k: cf[k]["id"] for k in ["programa_interes","origen","fuente_lead","link_enviado",
       "estado_conversacion","toques_enviados","grado_escolar","inicio_deseado","nivel_ingles"]}

def n8n(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method,
        headers={"X-N8N-API-KEY": KEY, "User-Agent": UA, "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode(); return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")

st, wf = n8n("GET", f"/api/v1/workflows/{WID}")
assert st == 200, f"no pude leer staging: {st} {wf}"
nodes = {n["name"]: n for n in wf["nodes"]}

# ---------- nodo HTTP: Buscar Contact GHL ----------
buscar = {
    "parameters": {
        "method": "POST",
        "url": "https://services.leadconnectorhq.com/contacts/search",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendHeaders": True,
        "headerParameters": {"parameters": [
            {"name": "Version", "value": "2021-07-28"},
            {"name": "Content-Type", "value": "application/json"},
            {"name": "Accept", "value": "application/json"},
            {"name": "User-Agent", "value": UA},
        ]},
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={{ (() => { const n = $('Normalizar payload').first().json; "
                    "const phone = n.phone || ''; const email = n.email || ''; "
                    "const f = phone ? {field:'phone',operator:'eq',value:phone} "
                    ": {field:'email',operator:'eq',value:email}; "
                    "return JSON.stringify({ locationId: '" + LOCATION + "', pageLimit: 1, "
                    "filters: [{ group:'OR', filters:[f] }] }); })() }}",
        "options": {},
    },
    "id": "vtr-buscar-contact-ghl", "name": "Buscar Contact GHL",
    "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
    "position": [-60, 0], "onError": "continueRegularOutput",
    "credentials": {"httpHeaderAuth": {"id": CRED_ID, "name": CRED_NAME}},
}
# nota: locationId real se resuelve; para no depender de $vars, lo inyectamos literal abajo

# ---------- Code: Construir estado lead ----------
estado_js = (
"const FID = " + json.dumps(FID) + ";\n"
"let hit = null;\n"
"try {\n"
"  const r = $('Buscar Contact GHL').first().json || {};\n"
"  const arr = r.contacts || (r.body && r.body.contacts) || [];\n"
"  hit = arr[0] || null;\n"
"} catch (e) { hit = null; }\n"
"if (!hit || !hit.id) { return [{ json: { estado: 'Lead nuevo: no tenemos nada de esta persona todavia.', encontrado: false } }]; }\n"
"const cfs = {};\n"
"for (const x of (hit.customFields || [])) cfs[x.id] = x.value;\n"
"const V = (k) => cfs[FID[k]];\n"
"const truthy = (v) => v === true || v === 'true' || (Array.isArray(v) && v.includes('true'));\n"
"const L = [];\n"
"const nom = ((hit.firstName||'') + ' ' + (hit.lastName||'')).trim();\n"
"L.push('Nombre: ' + (nom ? nom + ' (ya lo sabes, no se lo vuelvas a preguntar)' : 'no disponible'));\n"
"const prog = (V('programa_interes')||'').toString().trim();\n"
"L.push('Programa de interes: ' + (prog && prog !== 'No definido' ? prog : 'sin definir'));\n"
"const org = (V('origen')||'').toString().trim(); const fue = (V('fuente_lead')||'').toString().trim();\n"
"L.push('Origen: ' + (org || fue || 'DESCONOCIDO'));\n"
"L.push('Link de agenda: ' + (truthy(V('link_enviado')) ? 'YA ENVIADO' : 'no enviado'));\n"
"const est = (V('estado_conversacion')||'').toString().trim(); if (est) L.push('Conversacion: ' + est);\n"
"const toq = V('toques_enviados'); if (toq) L.push('Toques enviados: ' + toq);\n"
"const form = [\n"
"  V('grado_escolar') ? 'grado ' + V('grado_escolar') : null,\n"
"  V('inicio_deseado') ? 'inicio ' + V('inicio_deseado') : null,\n"
"  V('nivel_ingles') ? 'ingles ' + V('nivel_ingles') : null,\n"
"].filter(Boolean);\n"
"if (form.length) L.push('Del formulario (ya los tenemos): ' + form.join(' - '));\n"
"return [{ json: { estado: L.join('\\n'), encontrado: true } }];\n"
)
estado = {
    "parameters": {"jsCode": estado_js},
    "id": "vtr-construir-estado", "name": "Construir estado lead",
    "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [140, 0],
}

# ---------- reescribir text del agente ----------
agent = nodes["Agente IA WPP"]
agent["parameters"]["text"] = (
"=[ESTADO DEL LEAD]\n"
"{{ $('Construir estado lead').first().json.estado }}\n\n"
"Mensaje del usuario: {{ $('Normalizar payload').first().json.message }}\n\n"
"Fecha de hoy: {{ $now.setZone('America/Mexico_City').format(\"EEEE dd 'of' MMMM 'of' yyyy hh:mma\") }}"
)

# upsert de los 2 nodos nuevos (idempotente por name)
def upsert(node):
    for i, n in enumerate(wf["nodes"]):
        if n["name"] == node["name"]:
            wf["nodes"][i] = node; return
    wf["nodes"].append(node)
upsert(buscar); upsert(estado)

# reposicionar el resto para que no se pisen
for n in wf["nodes"]:
    if n["name"] == "Agente IA WPP": n["position"] = [360, 0]
    if n["name"] == "Enviar Telegram": n["position"] = [740, 0]
    if n["name"] == "OpenAI Chat Model": n["position"] = [180, 240]
    if n["name"] == "Postgres Chat Memory": n["position"] = [360, 240]

# reconexiones: Normalizar → Buscar → Construir → Agente
conns = wf["connections"]
conns["Normalizar payload"] = {"main": [[{"node": "Buscar Contact GHL", "type": "main", "index": 0}]]}
conns["Buscar Contact GHL"] = {"main": [[{"node": "Construir estado lead", "type": "main", "index": 0}]]}
conns["Construir estado lead"] = {"main": [[{"node": "Agente IA WPP", "type": "main", "index": 0}]]}

put = {"name": wf["name"], "nodes": wf["nodes"], "connections": conns,
       "settings": wf.get("settings", {"executionOrder": "v1"})}
st, d = n8n("PUT", f"/api/v1/workflows/{WID}", put)
print("PUT →", st)
if st == 200:
    _, rb = n8n("GET", f"/api/v1/workflows/{WID}")
    print("nodos:", [n["name"] for n in rb["nodes"]])
    print("active:", rb.get("active"))
else:
    print(json.dumps(d)[:500])
