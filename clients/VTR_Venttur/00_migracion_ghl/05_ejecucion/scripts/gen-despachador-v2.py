"""
FASE 4 · Despachador v2 — motor de selección COMPLETO (tope-2 + 2 carriles + exclusión booked).
Actualiza in-place el workflow vrShEXQGGAo4FqAt (INACTIVO). NO toca vivos.
Topología: Cron → Query booked (OP·Bot) → Query rescate (link=true) → Query nurturing (estado OR)
  → Seleccionar (Code: merge + dedup + prioridad rescate>nurturing + tope-2 null-safe + excluir
  booked/terminal + recencia) → [Enviar template / Siembra memoria / Update toques] (disabled, gated).
Lógica del Code = validada en Python vs GHL real 2026-09-07.
Uso: python3 gen-despachador-v2.py
"""
import json, os, sys, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(__file__))
from _ghl_client import load_n8n, UA, GHL
BASE, KEY = load_n8n(); BASE = BASE.rstrip("/")
LOCATION = GHL().location_id
WID = "vrShEXQGGAo4FqAt"
CRED = {"id": "YkVmaA4jlRbO1TQD", "name": "GHL VTR (PIT)"}
cf = json.load(open(os.path.join(os.path.dirname(__file__), "..", "spec", "custom-fields-idmap.json")))["contact"]
pl = json.load(open(os.path.join(os.path.dirname(__file__), "..", "spec", "pipelines-idmap.json")))
L, T, E, UAF = cf["link_enviado"]["id"], cf["toques_enviados"]["id"], cf["estado_conversacion"]["id"], cf["ultima_actividad"]["id"]
OPID = pl["OP · Bot Venttur"]["id"]
STAGES = pl["OP · Bot Venttur"]["stages"]
BOOKED_IDS = [STAGES[s] for s in ["Cita agendada", "Cita confirmada", "Asistió"] if s in STAGES]

def n8n(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method,
        headers={"X-N8N-API-KEY": KEY, "User-Agent": UA, "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode(); return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")

def http_headers():
    return {"values": [{"name": "Version", "value": "2021-07-28"},
        {"name": "Content-Type", "value": "application/json"}, {"name": "Accept", "value": "application/json"},
        {"name": "User-Agent", "value": UA}]}

def query_node(name, jsonbody, pos):
    return {"parameters": {"method": "POST", "url": "https://services.leadconnectorhq.com/contacts/search",
        "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
        "sendHeaders": True, "parametersHeaders": http_headers(),
        "sendBody": True, "specifyBody": "json", "jsonBody": json.dumps(jsonbody), "options": {}},
        "id": "q-" + name, "name": name, "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
        "position": pos, "onError": "continueRegularOutput", "credentials": {"httpHeaderAuth": CRED}}

cron = {"parameters": {"rule": {"interval": [{"field": "hours", "hoursInterval": 1}]}},
        "id": "desp-cron", "name": "Cron despachador", "type": "n8n-nodes-base.scheduleTrigger",
        "typeVersion": 1.2, "position": [-720, 0]}

q_booked = {"parameters": {"method": "GET",
        "url": "https://services.leadconnectorhq.com/opportunities/search",
        "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
        "sendHeaders": True, "parametersHeaders": http_headers(),
        "sendQuery": True, "queryParameters": {"parameters": [
            {"name": "location_id", "value": LOCATION}, {"name": "pipeline_id", "value": OPID}, {"name": "limit", "value": "100"}]},
        "options": {}},
        "id": "q-booked", "name": "Query booked (OP·Bot)", "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2, "position": [-520, 0], "onError": "continueRegularOutput", "credentials": {"httpHeaderAuth": CRED}}

q_rescate = query_node("Query rescate", {"locationId": LOCATION, "pageLimit": 100,
    "filters": [{"group": "AND", "filters": [{"field": f"customFields.{L}", "operator": "eq", "value": "true"}]}]}, [-320, 0])
q_nurt = query_node("Query nurturing", {"locationId": LOCATION, "pageLimit": 100,
    "filters": [{"group": "OR", "filters": [
        {"field": f"customFields.{E}", "operator": "eq", "value": "Contestó"},
        {"field": f"customFields.{E}", "operator": "eq", "value": "Interrumpida"}]}]}, [-120, 0])

select_js = (
"// Motor de selección COMPLETO — TOPE-2 (validado vs GHL real 2026-09-07)\n"
"const T='" + T + "', E='" + E + "', L='" + L + "', UAF='" + UAF + "';\n"
"const BOOKED_STAGE_IDS = " + json.dumps(BOOKED_IDS) + ";\n"
"const RECENCIA_DIAS = 30;              // ⚠ null en históricos → no filtra (ver gap en la guía)\n"
"const TERMINAL = ['Cita confirmada'];\n"
"const flat = (n, key) => { try { return $(n).all().flatMap(i => (i.json && i.json[key]) || []); } catch(e){ return []; } };\n"
"const cfv = (c, id) => { for (const x of (c.customFields||[])) if (x.id===id) return x.value; return null; };\n"
"const truthy = v => v===true||v==='true'||(Array.isArray(v)&&v.includes('true'));\n"
"const now = Date.now();\n"
"// 1) contactIds con cita (opps OP·Bot en etapas booked)\n"
"const bookedOpps = flat('Query booked (OP·Bot)', 'opportunities');\n"
"const booked = new Set(bookedOpps.filter(o => BOOKED_STAGE_IDS.includes(o.pipelineStageId)).map(o => o.contactId));\n"
"const gate = (c) => {\n"
"  if (booked.has(c.id)) return false;\n"
"  let toq = cfv(c, T); toq = (toq===null||toq===''||(Array.isArray(toq)&&!toq.length))?0:Number(toq);\n"
"  if (toq >= 2) return false;                       // TOPE GLOBAL 2\n"
"  const est = (cfv(c, E)||'').toString().trim();\n"
"  if (TERMINAL.includes(est)) return false;\n"
"  const ua = cfv(c, UAF); const t = ua ? Date.parse(ua) : null;\n"
"  if (t && (now - t) > RECENCIA_DIAS*864e5) return false;\n"
"  return true;\n"
"};\n"
"const sel = new Map();\n"
"// prioridad: rescate primero (link_enviado=true, sin cita)\n"
"for (const c of flat('Query rescate','contacts')) { if (gate(c)) sel.set(c.id, {contactId:c.id, phone:c.phone, firstName:c.firstName, lane:'rescate', toques_actual: Number(cfv(c,T))||0}); }\n"
"// nurturing: estado activo SIN link (los con link ya están en rescate)\n"
"for (const c of flat('Query nurturing','contacts')) { if (sel.has(c.id)) continue; if (truthy(cfv(c,L))) continue; if (gate(c)) sel.set(c.id, {contactId:c.id, phone:c.phone, firstName:c.firstName, lane:'nurturing', toques_actual: Number(cfv(c,T))||0}); }\n"
"return [...sel.values()].map(json => ({ json }));  // 1 item/contacto; 1 msg/contacto/run\n"
)
select = {"parameters": {"jsCode": select_js}, "id": "desp-select", "name": "Seleccionar (tope-2 + prioridad)",
          "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [100, 0]}

send = {"parameters": {"method": "POST", "url": "https://services.leadconnectorhq.com/conversations/messages",
        "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
        "sendHeaders": True, "parametersHeaders": http_headers(), "sendBody": True, "specifyBody": "json",
        "jsonBody": '={\n  "type": "WhatsApp",\n  "contactId": "{{ $json.contactId }}",\n  "templateId": "PENDIENTE_B-07"\n}', "options": {}},
        "id": "desp-send", "name": "Enviar template GHL (PLACEHOLDER)", "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2, "position": [320, -120], "disabled": True, "onError": "continueRegularOutput", "credentials": {"httpHeaderAuth": CRED}}
mem = {"parameters": {"operation": "executeQuery",
        "query": "INSERT INTO n8n_chat_histories (session_id, message) VALUES ($1, $2::jsonb)",
        "options": {"queryReplacement": "={{ [ $json.phone, JSON.stringify({type:'ai', data:{content:'[toque proactivo: '+$json.lane+']'}}) ] }}"}},
        "id": "desp-mem", "name": "Siembra memoria (Supabase)", "type": "n8n-nodes-base.postgres", "typeVersion": 2.6,
        "position": [320, 0], "disabled": True, "credentials": {"postgres": {"id": "ihpvM7nYMdLCwWDP", "name": "Postgres Venttur"}}}
upd = {"parameters": {"method": "PUT", "url": "=https://services.leadconnectorhq.com/contacts/{{ $json.contactId }}",
        "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
        "sendHeaders": True, "parametersHeaders": http_headers(), "sendBody": True, "specifyBody": "json",
        "jsonBody": ('={"customFields":[{"id":"' + T + '","value":{{ ($json.toques_actual||0)+1 }}},{"id":"' + UAF + '","value":"{{ $now.toISO() }}"}]}'), "options": {}},
        "id": "desp-upd", "name": "Update toques (+1)", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
        "position": [320, 120], "disabled": True, "onError": "continueRegularOutput", "credentials": {"httpHeaderAuth": CRED}}
note = {"parameters": {"content": ("## Despachador · TOPE-2 (motor completo)\n\nINACTIVO. Selección validada vs GHL real.\n"
        "**GAPS pre-ACTIVO** (ver guía pre-traspaso §4):\n- recencia null en históricos → ~1000 candidatos rescate en go-live (falta política históricos)\n"
        "- exclusión 'con cita' = 0 hasta poblar OP·Bot con booking\n- envío = placeholder (templates B-07)\n- paginación de los 3 queries: verificar en run vivo"),
        "height": 260, "width": 340}, "id": "desp-note", "name": "Sticky Note", "type": "n8n-nodes-base.stickyNote",
        "typeVersion": 1, "position": [-320, 200]}

nodes = [cron, q_booked, q_rescate, q_nurt, select, send, mem, upd, note]
connections = {
    "Cron despachador": {"main": [[{"node": "Query booked (OP·Bot)", "type": "main", "index": 0}]]},
    "Query booked (OP·Bot)": {"main": [[{"node": "Query rescate", "type": "main", "index": 0}]]},
    "Query rescate": {"main": [[{"node": "Query nurturing", "type": "main", "index": 0}]]},
    "Query nurturing": {"main": [[{"node": "Seleccionar (tope-2 + prioridad)", "type": "main", "index": 0}]]},
    "Seleccionar (tope-2 + prioridad)": {"main": [[
        {"node": "Enviar template GHL (PLACEHOLDER)", "type": "main", "index": 0},
        {"node": "Siembra memoria (Supabase)", "type": "main", "index": 0},
        {"node": "Update toques (+1)", "type": "main", "index": 0}]]},
}
payload = {"name": "vtr-despachador-proactivo-v1", "nodes": nodes, "connections": connections, "settings": {"executionOrder": "v1"}}
st, d = n8n("PUT", f"/api/v1/workflows/{WID}", payload)
print("PUT →", st)
if st == 200:
    _, rb = n8n("GET", f"/api/v1/workflows/{WID}")
    print("nodos:", [n["name"] for n in rb["nodes"]], "· active:", rb.get("active"))
else:
    print(json.dumps(d)[:500])
