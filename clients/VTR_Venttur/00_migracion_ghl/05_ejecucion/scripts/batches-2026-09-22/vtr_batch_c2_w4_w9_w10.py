#!/usr/bin/env python3
"""
Batch C.2 · Construir W4 · W9 · W10 (GHL) — todos OFF hasta CUTOVER-2.

W4  · Formulario landing → Contact GHL      (reemplaza ZB6erhWicZmDfC4I)
W9  · Actualizar link_enviado → GHL          (reemplaza gRSMjzxggA4UePjz)
W10 · Outreach Sheet → Contact GHL (ingest)  (reemplaza CUuFxbst3iHpgeXS, solo ingesta)

Patrón GHL replicado del batch-C/main + elevar:
  - cred header-auth "GHL VTR (PIT)" id YkVmaA4jlRbO1TQD (aporta Authorization: Bearer <PIT>)
  - authentication=genericCredentialType, genericAuthType=httpHeaderAuth
  - customFields: [{id, value}]  (formato confirmado en W11/despachador)
  - Version 2021-07-28 (contacts)

Idempotente por NOMBRE: si ya existe un workflow con el mismo name, no lo re-crea.
POST /workflows crea el workflow INACTIVO por defecto (no se llama a /activate).
"""
import json
import subprocess
import uuid
import hashlib
from pathlib import Path

ROOT = Path("/Users/camilo/Downloads/camilo-workspace")
OLDWF = Path("/private/tmp/claude-501/-Users-la agencia-Downloads-camilo-workspace/f0b8fdaa-d98d-40f3-b33a-dba949ad0b8d/scratchpad/oldwf")
BATCH_DIR = ROOT / "clients/VTR_Venttur/03_workflows/ghl-live-2026-09-22-batch-C2"
BATCH_DIR.mkdir(parents=True, exist_ok=True)

# --- Credenciales por nombre/id ---
GHL_CRED = {"id": "YkVmaA4jlRbO1TQD", "name": "GHL VTR (PIT)"}
SHEETS_TRIG_CRED = {"id": "xjVkf0DxxXJ7sMSa", "name": "la agencia (@gmail)"}
LOC = "7aXb4JCKsWV5nUyBXeSF"
N8N_BASE = None  # set below
RESCATE_WEBHOOK = "https://[TU-INSTANCIA-N8N]/webhook/vtr-rescate-link"

# --- Custom field IDs (contact) ---
CF = {
    "programa_interes": "xK2NFqtz1DYUw3gYdn8I",
    "atribuida_a": "yEgBeLQNnCPkTTv8OvfX",
    "link_enviado": "rHzGNiesWuESPmSZyviJ",
    "folio": "S80aYglwiVLkMsf95Ddz",
    "fbclid": "8REOsOHYC3boWRY74Rx5",
    "ad_name": "McKjVHiSyU1IU3G1PpN1",
    "platform": "ffxBAFkCuCgBI1vo8PmS",
    "grado_escolar": "HjNeRtIv6XHHMgFbtsaR",
    "inicio_deseado": "dUvMI4NaamfRPOF1p95q",
    "nivel_ingles": "uOecQsOv9i3uwMeSgEkX",
    "fuente_lead": "2hv0GovhSzZO3hj9cFqm",
    "tipo_contacto": "4sj9sWAen1PvGCkn9eCN",
    "origen": "BEhJWnXS9SQovJTLSA2W",
    "toques_enviados": "ez934lu03v7nC4ZRS7LJ",
    "outreach_enviado": "wFD12kJI9fCufQmvHAGc",
    "touch1_programado_at": "95bG6wvWFk2ma17T4NuE",
}


def env_get(k):
    r = subprocess.run(["grep", f"^{k}=", str(ROOT / ".env")], capture_output=True, text=True, check=True)
    return r.stdout.strip().split("\n")[0].split("=", 1)[1].strip().strip('"').strip("'")


def curl_json(method, path, data=None, allow_fail=False):
    base = env_get("N8N_BASE_URL").rstrip("/")
    key = env_get("N8N_API_KEY")
    cmd = ["curl", "-sS", "-w", "\n%{http_code}", "-X", method,
           "-H", f"X-N8N-API-KEY: {key}", "-H", "Content-Type: application/json"]
    if data is not None:
        cmd.extend(["--data-binary", "@-"])
    cmd.append(f"{base}/api/v1{path}")
    r = subprocess.run(cmd, input=json.dumps(data) if data else None, capture_output=True, text=True)
    parts = r.stdout.rsplit("\n", 1)
    body = parts[0] if len(parts) == 2 else r.stdout
    code = parts[1].strip() if len(parts) == 2 else "?"
    if not (200 <= int(code) < 300) and not allow_fail:
        raise RuntimeError(f"{method} {path} → {code}: {body[:600]}")
    try:
        return json.loads(body), code
    except Exception:
        return body, code


def nid():
    return str(uuid.uuid4())


def find_existing(name):
    data, _ = curl_json("GET", "/workflows?limit=250")
    for wf in data.get("data", []):
        if wf.get("name") == name:
            return wf.get("id")
    return None


def create_and_snapshot(wf, snap_name):
    existing = find_existing(wf["name"])
    if existing:
        print(f"   ⚠️  ya existe '{wf['name']}' → id={existing} (no re-creo)")
        wid = existing
    else:
        created, _ = curl_json("POST", "/workflows", data=wf)
        wid = created["id"]
        print(f"   ✓ creado id={wid} active={created.get('active')}")
    final, _ = curl_json("GET", f"/workflows/{wid}")
    path = BATCH_DIR / snap_name
    with open(path, "w") as f:
        json.dump(final, f, indent=2, ensure_ascii=False)
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
    print(f"   💾 {snap_name} · sha256={sha}")
    return wid, sha


def ghl_http(name, method, url, json_body_expr, pos, extra_headers=None):
    headers = [{"name": "Version", "value": "2021-07-28"}, {"name": "LocationId", "value": LOC}]
    if extra_headers:
        headers.extend(extra_headers)
    return {
        "parameters": {
            "method": method,
            "url": url,
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "sendHeaders": True,
            "headerParameters": {"parameters": headers},
            "sendBody": True,
            "contentType": "json",
            "jsonBody": json_body_expr,
            "options": {},
        },
        "id": nid(),
        "name": name,
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": pos,
        "credentials": {"httpHeaderAuth": GHL_CRED},
    }


# ============================================================
# W4 · Formulario landing → Contact GHL
# ============================================================
W4_NORMALIZE = r"""
// W4 · Normalize landing payload → GHL upsert body
const body = $json.body || $json;

function canonMX(raw){
  let d=(raw||'').toString().replace(/[^0-9]/g,'');
  if(!d) return null;
  if(d.length===10) d='521'+d;                                   // local 10 → 521+10
  else if(d.length===12 && d.startsWith('52')) d='521'+d.slice(2); // 52+10 → 521+10
  else if(d.length===11 && d.startsWith('52')) d='521'+d.slice(2); // 52+9 (best effort)
  // 13 dígitos empezando 521 → se deja
  return '+'+d;
}
function canonPrograma(raw){
  const r=(raw||'').toString().toLowerCase();
  if(/internado|boarding/.test(r)) return 'Internados';
  if(/intercambio|familia|acad[eé]mico|\baa\b|a[nñ]o acad/.test(r)) return 'Intercambio académico con familias';
  if(/campamento|summer/.test(r)) return 'Campamentos de verano';
  if(/pathway/.test(r)) return 'Pathway Alemania';
  if(/gap|estudia|estudio y trabajo|trabajar/.test(r)) return 'Gap Year / Estudia y Trabaja';
  if(/viaje/.test(r)) return 'Viajes educativos';
  if(/superior/.test(r)) return 'Educación superior';
  if(/idioma/.test(r)) return 'Cursos de idiomas en el extranjero';
  return null; // desconocido → no se escribe programa_interes (SINGLE_OPTIONS)
}

const phone = canonMX(body.telefono);
const programa = canonPrograma(body.programa);
const programa_raw = (body.programa||'').toString();
const fbclid = body.fbclid_completo || body.fbclid || null;
const atribuida = (body.atribuida_a||'').toString();
const folio = (body.folio||'').toString();

const CF = %CF%;
const customFields = [];
if(folio)     customFields.push({id: CF.folio, value: folio});
if(programa)  customFields.push({id: CF.programa_interes, value: programa});
if(atribuida) customFields.push({id: CF.atribuida_a, value: atribuida});
if(fbclid)    customFields.push({id: CF.fbclid, value: fbclid});

const tags = ['Form Landing'];
if(programa) tags.push(programa); else if(programa_raw) tags.push(programa_raw);

const ghl_body = {
  locationId: '%LOC%',
  phone: phone || undefined,
  firstName: (body.nombre||'').toString(),
  lastName: (body.apellidos||body.apellido||'').toString(),
  email: (body.email||'').toString() || undefined,
  customFields,
  tags
};

return [{ json: { ghl_body, _debug: { phone, programa, programa_raw } } }];
""".replace("%CF%", json.dumps(CF)).replace("%LOC%", LOC)

W4 = {
    "name": "W4 · Formulario landing → Contact GHL - Venttur (OFF)",
    "nodes": [
        {
            "parameters": {"httpMethod": "POST", "path": f"vtr-form-landing-ghl-{nid()[:8]}",
                           "responseMode": "responseNode", "options": {}},
            "id": nid(), "name": "Webhook", "type": "n8n-nodes-base.webhook",
            "typeVersion": 2, "position": [0, 0], "webhookId": nid(),
        },
        {
            "parameters": {"jsCode": W4_NORMALIZE},
            "id": nid(), "name": "Normalize (build GHL body)", "type": "n8n-nodes-base.code",
            "typeVersion": 2, "position": [220, 0],
        },
        ghl_http("POST /contacts/upsert", "POST",
                 "https://services.leadconnectorhq.com/contacts/upsert",
                 "={{ JSON.stringify($json.ghl_body) }}", [440, 0]),
        {
            "parameters": {"respondWith": "json", "responseBody": '={"ok": true, "contactId": "{{ $json.contact ? $json.contact.id : ($json.id || "") }}"}', "options": {}},
            "id": nid(), "name": "Responder OK", "type": "n8n-nodes-base.respondToWebhook",
            "typeVersion": 1.1, "position": [660, 0],
        },
    ],
    "connections": {
        "Webhook": {"main": [[{"node": "Normalize (build GHL body)", "type": "main", "index": 0}]]},
        "Normalize (build GHL body)": {"main": [[{"node": "POST /contacts/upsert", "type": "main", "index": 0}]]},
        "POST /contacts/upsert": {"main": [[{"node": "Responder OK", "type": "main", "index": 0}]]},
    },
    "settings": {"executionOrder": "v1"},
}

# ============================================================
# W9 · Actualizar link_enviado → GHL + dispara Rescate
# ============================================================
W9_BUILD_BODY = r"""
// W9 · normaliza input + arma body PUT link_enviado + tags
const i = $json;
const contact_id = i.contact_id || i.contactId || '';
const programa = (i.programa || i.programa_interes || '').toString();
const first_name = (i.first_name || i.firstName || '').toString();
const phone = (i.phone || '').toString();
const opportunityId = (i.opportunityId || '').toString();

const CF = %CF%;
const put_body = {
  customFields: [{ id: CF.link_enviado, value: 'true' }],
  tags: ['LINK_ENVIADO'].concat(programa ? [programa] : [])
};
const rescate_body = { first_name, programa_interes: programa, phone, contactId: contact_id, opportunityId };

return [{ json: { contact_id, programa, first_name, phone, opportunityId, put_body, rescate_body } }];
""".replace("%CF%", json.dumps(CF))

W9 = {
    "name": "W9 · Actualizar link_enviado (GHL) - Venttur (OFF)",
    "nodes": [
        {
            "parameters": {"inputSource": "jsonExample",
                           "jsonExample": json.dumps({"contact_id": "abc123", "phone": "+5213312345678",
                                                      "programa": "Internados", "first_name": "Juan",
                                                      "opportunityId": ""})},
            "id": nid(), "name": "When Executed by Another Workflow",
            "type": "n8n-nodes-base.executeWorkflowTrigger", "typeVersion": 1.1, "position": [0, 0],
        },
        {
            "parameters": {"jsCode": W9_BUILD_BODY},
            "id": nid(), "name": "Preparar payloads", "type": "n8n-nodes-base.code",
            "typeVersion": 2, "position": [220, 0],
        },
        ghl_http("PUT link_enviado=true + tags", "PUT",
                 "=https://services.leadconnectorhq.com/contacts/{{ $json.contact_id }}",
                 "={{ JSON.stringify($json.put_body) }}", [440, 0]),
        {
            "parameters": {
                "method": "POST", "url": RESCATE_WEBHOOK,
                "sendBody": True, "contentType": "json",
                "jsonBody": "={{ JSON.stringify($('Preparar payloads').first().json.rescate_body) }}",
                "options": {},
            },
            "id": nid(), "name": "Disparar Rescate (webhook)", "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2, "position": [660, 0],
        },
    ],
    "connections": {
        "When Executed by Another Workflow": {"main": [[{"node": "Preparar payloads", "type": "main", "index": 0}]]},
        "Preparar payloads": {"main": [[{"node": "PUT link_enviado=true + tags", "type": "main", "index": 0}]]},
        "PUT link_enviado=true + tags": {"main": [[{"node": "Disparar Rescate (webhook)", "type": "main", "index": 0}]]},
    },
    "settings": {"executionOrder": "v1"},
}

# ============================================================
# W10 · Outreach Sheet → Contact GHL (solo ingesta)
# ============================================================
# Reusar el Normalize Payload verbatim del W10 viejo (parsing battle-tested)
old_w10 = json.load(open(OLDWF / "W10-outreach-form-meta.json"))
W10_NORMALIZE = None
for n in old_w10["nodes"]:
    if n["name"] == "Normalize Payload":
        W10_NORMALIZE = n["parameters"]["jsCode"]
assert W10_NORMALIZE, "no encontré Normalize Payload en W10 viejo"

W10_BUILD_BODY = r"""
// W10 · normalized item → GHL upsert body (solo items válidos)
const i = $json;
const CF = %CF%;

const platform = (i.platform||'').toLowerCase();
const platform_opt = (platform==='ig'||platform==='fb') ? platform : null;
const nivel = (i.nivel_ingles||'').toString().toLowerCase();
const nivel_opt = ['básico','basico','intermedio','avanzado'].includes(nivel)
  ? (nivel==='basico'?'básico':nivel) : null;
const tipo = (i.tipo==='Padre/Madre') ? 'Padre/Madre' : 'No especificado';

const customFields = [
  { id: CF.folio, value: (i.meta_lead_id||'').toString() },
  { id: CF.programa_interes, value: 'Internados' },   // Outreach Form Meta = Boarding School
  { id: CF.origen, value: 'Form Meta' },
  { id: CF.fuente_lead, value: (i.fuente_lead||'').toString() },
  { id: CF.tipo_contacto, value: tipo },
  { id: CF.ad_name, value: (i.ad_name||'').toString() },
  { id: CF.grado_escolar, value: (i.grado_escolar||'').toString() },
  { id: CF.inicio_deseado, value: (i.inicio_deseado||'').toString() },
  { id: CF.touch1_programado_at, value: (i.touch_1_programado_at||'').toString() },
  { id: CF.toques_enviados, value: 0 },
  { id: CF.outreach_enviado, value: 'false' },
];
if(platform_opt) customFields.push({ id: CF.platform, value: platform_opt });
if(nivel_opt) customFields.push({ id: CF.nivel_ingles, value: nivel_opt });

const ghl_body = {
  locationId: '%LOC%',
  phone: i.telefono_con_plus || undefined,
  firstName: (i.nombre||'').toString(),
  lastName: (i.apellido||'').toString(),
  email: (i.email||'').toString() || undefined,
  customFields,
  tags: ['Origen: Form Meta', 'Internados']
};
return [{ json: { ghl_body } }];
""".replace("%CF%", json.dumps(CF)).replace("%LOC%", LOC)

W10 = {
    "name": "W10 · Outreach Sheet → Contact GHL (ingesta) - Venttur (OFF)",
    "nodes": [
        {
            "parameters": {
                "pollTimes": {"item": [{"mode": "everyMinute"}]},
                "documentId": {"__rl": True, "value": "1HzJVMBwnGikiI_U805N7oqcXPYE7TjEFTL1rqdcCEIU", "mode": "list",
                               "cachedResultName": "LEADS - FORMULARIO (VTR)",
                               "cachedResultUrl": "https://docs.google.com/spreadsheets/d/1HzJVMBwnGikiI_U805N7oqcXPYE7TjEFTL1rqdcCEIU/edit?usp=drivesdk"},
                "sheetName": {"__rl": True, "value": 160362675, "mode": "list",
                              "cachedResultName": "Boarding_Schools_Venttur_2026-test-2",
                              "cachedResultUrl": "https://docs.google.com/spreadsheets/d/1HzJVMBwnGikiI_U805N7oqcXPYE7TjEFTL1rqdcCEIU/edit#gid=160362675"},
                "event": "rowAdded", "options": {"valueRender": "UNFORMATTED_VALUE"},
            },
            "id": nid(), "name": "Sheets Trigger - Form Meta Sync",
            "type": "n8n-nodes-base.googleSheetsTrigger", "typeVersion": 1, "position": [0, 0],
            "credentials": {"googleSheetsTriggerOAuth2Api": SHEETS_TRIG_CRED},
        },
        {
            "parameters": {"jsCode": W10_NORMALIZE},
            "id": nid(), "name": "Normalize Payload", "type": "n8n-nodes-base.code",
            "typeVersion": 2, "position": [220, 0],
        },
        {
            "parameters": {"conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 2},
                           "conditions": [{"id": nid(), "leftValue": "={{ $json._error }}", "rightValue": True,
                                           "operator": {"type": "boolean", "operation": "true", "singleValue": True}}],
                           "combinator": "and"}, "options": {}},
            "id": nid(), "name": "IF (_error?)", "type": "n8n-nodes-base.if",
            "typeVersion": 2.2, "position": [440, 0],
        },
        {
            "parameters": {"jsCode": W10_BUILD_BODY},
            "id": nid(), "name": "Build GHL body", "type": "n8n-nodes-base.code",
            "typeVersion": 2, "position": [660, 120],
        },
        ghl_http("POST /contacts/upsert", "POST",
                 "https://services.leadconnectorhq.com/contacts/upsert",
                 "={{ JSON.stringify($json.ghl_body) }}", [880, 120]),
        {
            "parameters": {},
            "id": nid(), "name": "Descartar (phone inválido)", "type": "n8n-nodes-base.noOp",
            "typeVersion": 1, "position": [660, -120],
        },
    ],
    "connections": {
        "Sheets Trigger - Form Meta Sync": {"main": [[{"node": "Normalize Payload", "type": "main", "index": 0}]]},
        "Normalize Payload": {"main": [[{"node": "IF (_error?)", "type": "main", "index": 0}]]},
        "IF (_error?)": {"main": [
            [{"node": "Descartar (phone inválido)", "type": "main", "index": 0}],   # true = error
            [{"node": "Build GHL body", "type": "main", "index": 0}],               # false = válido
        ]},
        "Build GHL body": {"main": [[{"node": "POST /contacts/upsert", "type": "main", "index": 0}]]},
    },
    "settings": {"executionOrder": "v1"},
}


if __name__ == "__main__":
    results = {}
    print("=" * 60)
    print("W4 · Formulario landing → Contact GHL")
    print("=" * 60)
    results["W4"] = create_and_snapshot(W4, "W4-formulario-landing-ghl.json")

    print("\n" + "=" * 60)
    print("W9 · Actualizar link_enviado → GHL")
    print("=" * 60)
    results["W9"] = create_and_snapshot(W9, "W9-actualizar-link-enviado-ghl.json")

    print("\n" + "=" * 60)
    print("W10 · Outreach Sheet → Contact GHL (ingesta)")
    print("=" * 60)
    results["W10"] = create_and_snapshot(W10, "W10-outreach-ingest-ghl.json")

    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    for k, (wid, sha) in results.items():
        print(f"  {k}: id={wid}")
