#!/usr/bin/env python3
"""
Actualiza W9 (TROsQ5h78baAuVOY) in-place: agrega GET /contacts/{id} para auto-enriquecer
programa + first_name, así el main solo pasa {contact_id, phone}. Preserva el id (PUT).
"""
import json, subprocess, uuid, hashlib
from pathlib import Path

ROOT = Path("/Users/camilo/Downloads/camilo-workspace")
BATCH_DIR = ROOT / "clients/VTR_Venttur/03_workflows/ghl-live-2026-09-22-batch-C2"
W9_ID = "TROsQ5h78baAuVOY"
GHL_CRED = {"id": "YkVmaA4jlRbO1TQD", "name": "GHL VTR (PIT)"}
RESCATE_WEBHOOK = "https://[TU-INSTANCIA-N8N]/webhook/vtr-rescate-link"
CF = {"link_enviado": "rHzGNiesWuESPmSZyviJ", "programa_interes": "xK2NFqtz1DYUw3gYdn8I"}


def env_get(k):
    r = subprocess.run(["grep", f"^{k}=", str(ROOT / ".env")], capture_output=True, text=True, check=True)
    return r.stdout.strip().split("\n")[0].split("=", 1)[1].strip().strip('"').strip("'")


def curl_json(method, path, data=None):
    base = env_get("N8N_BASE_URL").rstrip("/"); key = env_get("N8N_API_KEY")
    cmd = ["curl", "-sS", "-w", "\n%{http_code}", "-X", method,
           "-H", f"X-N8N-API-KEY: {key}", "-H", "Content-Type: application/json"]
    if data is not None: cmd.extend(["--data-binary", "@-"])
    cmd.append(f"{base}/api/v1{path}")
    r = subprocess.run(cmd, input=json.dumps(data) if data else None, capture_output=True, text=True)
    parts = r.stdout.rsplit("\n", 1); body = parts[0]; code = parts[1].strip()
    if not (200 <= int(code) < 300):
        raise RuntimeError(f"{method} {path} → {code}: {body[:500]}")
    try: return json.loads(body)
    except: return body


def nid(): return str(uuid.uuid4())

PREPARAR = r"""
// W9 · auto-enriquece programa + first_name desde el GET contact
const trig = $('When Executed by Another Workflow').first().json;
const contact_id = (trig.contact_id || trig.contactId || '').toString();
const phone = (trig.phone || '').toString();
const opportunityId = (trig.opportunityId || '').toString();

const resp = $json || {};
const c = resp.contact || resp || {};
const first_name = (trig.first_name || c.firstName || c.first_name || '').toString();

const PROGRAMA_FIELD = '%PROG%';
let programa = (trig.programa || trig.programa_interes || '').toString();
if (!programa) {
  const cfs = c.customFields || c.customField || [];
  if (Array.isArray(cfs)) {
    const f = cfs.find(x => x.id === PROGRAMA_FIELD);
    if (f) programa = (f.value || f.field_value || '').toString();
  }
}

const CF = %CF%;
const put_body = {
  customFields: [{ id: CF.link_enviado, value: 'true' }],
  tags: ['LINK_ENVIADO'].concat(programa ? [programa] : [])
};
const rescate_body = { first_name, programa_interes: programa, phone, contactId: contact_id, opportunityId };
return [{ json: { contact_id, programa, first_name, phone, opportunityId, put_body, rescate_body } }];
""".replace("%PROG%", CF["programa_interes"]).replace("%CF%", json.dumps(CF))

wf = curl_json("GET", f"/workflows/{W9_ID}")

# Reconstruir nodos: Trigger → GET contact → Preparar payloads → PUT → POST rescate
trig_node = next(n for n in wf["nodes"] if n["type"] == "n8n-nodes-base.executeWorkflowTrigger")
put_node = next(n for n in wf["nodes"] if n["name"] == "PUT link_enviado=true + tags")
rescate_node = next(n for n in wf["nodes"] if n["name"] == "Disparar Rescate (webhook)")

get_node = {
    "parameters": {
        "method": "GET",
        "url": "=https://services.leadconnectorhq.com/contacts/{{ $json.contact_id || $json.contactId }}",
        "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
        "sendHeaders": True,
        "headerParameters": {"parameters": [{"name": "Version", "value": "2021-07-28"}]},
        "options": {},
    },
    "id": nid(), "name": "GET contact (enrich)", "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2, "position": [200, 0], "credentials": {"httpHeaderAuth": GHL_CRED},
}
prep_node = {
    "parameters": {"jsCode": PREPARAR},
    "id": nid(), "name": "Preparar payloads", "type": "n8n-nodes-base.code",
    "typeVersion": 2, "position": [400, 0],
}
# reposicionar
put_node["position"] = [600, 0]
rescate_node["position"] = [800, 0]

wf["nodes"] = [trig_node, get_node, prep_node, put_node, rescate_node]
wf["connections"] = {
    trig_node["name"]: {"main": [[{"node": "GET contact (enrich)", "type": "main", "index": 0}]]},
    "GET contact (enrich)": {"main": [[{"node": "Preparar payloads", "type": "main", "index": 0}]]},
    "Preparar payloads": {"main": [[{"node": "PUT link_enviado=true + tags", "type": "main", "index": 0}]]},
    "PUT link_enviado=true + tags": {"main": [[{"node": "Disparar Rescate (webhook)", "type": "main", "index": 0}]]},
}

put_body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"], "settings": wf.get("settings", {})}
curl_json("PUT", f"/workflows/{W9_ID}", data=put_body)
final = curl_json("GET", f"/workflows/{W9_ID}")
path = BATCH_DIR / "W9-actualizar-link-enviado-ghl.json"
json.dump(final, open(path, "w"), indent=2, ensure_ascii=False)
sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
print(f"✓ W9 actualizado (self-enrich) · nodos={len(final['nodes'])} active={final.get('active')}")
print(f"  sha256={sha}")
