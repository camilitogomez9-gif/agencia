#!/usr/bin/env python3
"""
Batch C.2 · Sub-workflow vtr-tool-elevar-ghl (OFF).

3 pasos secuenciales:
1. PUT /contacts/{id} {"dnd": true} → pausar bot para ese contacto
2. PUT /contacts/{id} {"assignedTo": userId} → asignar a userId GHL
3. Telegram notification a grupo -4925599962 con resumen

Recibe (Execute Workflow Trigger):
  - contact_id: string
  - user_id: string
  - resumen: string
"""
import json, subprocess, uuid, hashlib
from pathlib import Path

ROOT = Path("/Users/camilo/Downloads/camilo-workspace")
BATCH_DIR = ROOT / "clients/VTR_Venttur/03_workflows/ghl-live-2026-09-22-batch-C"
MAIN_WF_ID = "1eS1Z5k898c3ATnf"
GHL_PIT_CRED_ID = "YkVmaA4jlRbO1TQD"
GHL_PIT_CRED_NAME = "GHL VTR (PIT)"
TELEGRAM_CRED_ID = "V5k84z3AjQc9Y5yg"
TELEGRAM_CRED_NAME = "botla agencia"
TELEGRAM_CHAT = "-4925599962"


def env_get(k):
    r = subprocess.run(["grep", f"^{k}=", str(ROOT / ".env")], capture_output=True, text=True, check=True)
    return r.stdout.strip().split("\n")[0].split("=", 1)[1].strip().strip('"').strip("'")

def curl_json(method, path, data=None, allow_fail=False):
    base = env_get("N8N_BASE_URL").rstrip("/"); key = env_get("N8N_API_KEY")
    cmd = ["curl", "-sS", "-w", "\n%{http_code}", "-X", method,
           "-H", f"X-N8N-API-KEY: {key}", "-H", "Content-Type: application/json"]
    if data is not None: cmd.extend(["--data-binary", "@-"])
    cmd.append(f"{base}/api/v1{path}")
    r = subprocess.run(cmd, input=json.dumps(data) if data else None, capture_output=True, text=True)
    parts = r.stdout.rsplit("\n", 1)
    body = parts[0] if len(parts) == 2 else r.stdout
    code = parts[1].strip() if len(parts) == 2 else "?"
    if not (200 <= int(code) < 300) and not allow_fail:
        raise RuntimeError(f"{method} {path} → {code}: {body[:500]}")
    try: return json.loads(body), code
    except: return body, code


def new_id(): return str(uuid.uuid4())


wf = {
    "name": "vtr-tool-elevar-ghl (invocable, OFF hasta cutover)",
    "nodes": [
        {
            "parameters": {
                "inputSource": "jsonExample",
                "jsonExample": json.dumps({"contact_id": "abc", "user_id": "usr123", "resumen": "..."})
            },
            "id": new_id(),
            "name": "When Executed by Another Workflow",
            "type": "n8n-nodes-base.executeWorkflowTrigger",
            "typeVersion": 1.1,
            "position": [0, 0]
        },
        {
            "parameters": {
                "method": "PUT",
                "url": "=https://services.leadconnectorhq.com/contacts/{{ $json.contact_id }}",
                "authentication": "genericCredentialType",
                "genericAuthType": "httpHeaderAuth",
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [
                        {"name": "Version", "value": "2021-07-28"}
                    ]
                },
                "sendBody": True,
                "contentType": "json",
                "jsonBody": '={{ JSON.stringify({ "dnd": true }) }}',
                "options": {}
            },
            "id": new_id(),
            "name": "1. PUT dnd:true (pausar bot)",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [220, 0],
            "credentials": {"httpHeaderAuth": {"id": GHL_PIT_CRED_ID, "name": GHL_PIT_CRED_NAME}}
        },
        {
            "parameters": {
                "method": "PUT",
                "url": "=https://services.leadconnectorhq.com/contacts/{{ $('When Executed by Another Workflow').first().json.contact_id }}",
                "authentication": "genericCredentialType",
                "genericAuthType": "httpHeaderAuth",
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [
                        {"name": "Version", "value": "2021-07-28"}
                    ]
                },
                "sendBody": True,
                "contentType": "json",
                "jsonBody": '={{ JSON.stringify({ "assignedTo": $(\'When Executed by Another Workflow\').first().json.user_id }) }}',
                "options": {}
            },
            "id": new_id(),
            "name": "2. PUT assignedTo (asignar userId)",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [440, 0],
            "credentials": {"httpHeaderAuth": {"id": GHL_PIT_CRED_ID, "name": GHL_PIT_CRED_NAME}}
        },
        {
            "parameters": {
                "chatId": TELEGRAM_CHAT,
                "text": (
                    "=🚨 Lead elevado — VTR\n"
                    "\n"
                    "Contact ID: `{{ $('When Executed by Another Workflow').first().json.contact_id }}`\n"
                    "Asignado a userId: `{{ $('When Executed by Another Workflow').first().json.user_id }}`\n"
                    "\n"
                    "Resumen:\n"
                    "{{ $('When Executed by Another Workflow').first().json.resumen }}"
                ),
                "additionalFields": {"parse_mode": "Markdown"}
            },
            "id": new_id(),
            "name": "3. Telegram notify",
            "type": "n8n-nodes-base.telegram",
            "typeVersion": 1.2,
            "position": [660, 0],
            "credentials": {"telegramApi": {"id": TELEGRAM_CRED_ID, "name": TELEGRAM_CRED_NAME}}
        }
    ],
    "connections": {
        "When Executed by Another Workflow": {"main": [[{"node": "1. PUT dnd:true (pausar bot)", "type": "main", "index": 0}]]},
        "1. PUT dnd:true (pausar bot)": {"main": [[{"node": "2. PUT assignedTo (asignar userId)", "type": "main", "index": 0}]]},
        "2. PUT assignedTo (asignar userId)": {"main": [[{"node": "3. Telegram notify", "type": "main", "index": 0}]]}
    },
    "settings": {}
}

print("📤 POST /workflows (vtr-tool-elevar-ghl)...")
created, _ = curl_json("POST", "/workflows", data=wf)
elevar_id = created["id"]
print(f"   ✓ id={elevar_id}, active={created.get('active')}")

# Save snapshot
final, _ = curl_json("GET", f"/workflows/{elevar_id}")
path = BATCH_DIR / "vtr-tool-elevar-ghl.json"
with open(path, "w") as f:
    json.dump(final, f, indent=2, ensure_ascii=False)
with open(path, "rb") as f:
    sha = hashlib.sha256(f.read()).hexdigest()
print(f"   💾 {path.name} · sha256={sha}")

# Actualizar el main-venttur-ghl con el workflowId real del sub-elevar
print(f"\n📥 GET main-venttur-ghl {MAIN_WF_ID}...")
main_wf, _ = curl_json("GET", f"/workflows/{MAIN_WF_ID}")
for n in main_wf["nodes"]:
    if n["name"] == "elevar" and n["type"] == "@n8n/n8n-nodes-langchain.toolWorkflow":
        n["parameters"]["workflowId"]["value"] = elevar_id
        n["parameters"]["workflowId"]["cachedResultName"] = wf["name"]
        break
put_body = {"name": main_wf["name"], "nodes": main_wf["nodes"],
            "connections": main_wf["connections"], "settings": main_wf.get("settings", {})}
print(f"📤 PUT main-venttur-ghl (actualizar workflowId de elevar)...")
curl_json("PUT", f"/workflows/{MAIN_WF_ID}", data=put_body)
print(f"   ✓ patched")

# Re-save main snapshot
final_main, _ = curl_json("GET", f"/workflows/{MAIN_WF_ID}")
main_path = BATCH_DIR / "main-venttur-ghl-v0.1.json"
with open(main_path, "w") as f:
    json.dump(final_main, f, indent=2, ensure_ascii=False)
with open(main_path, "rb") as f:
    main_sha = hashlib.sha256(f.read()).hexdigest()
print(f"   💾 {main_path.name} · sha256={main_sha} (updated)")

print(f"\n{'='*50}")
print(f"elevar_id: {elevar_id}")
print(f"main_id:   {MAIN_WF_ID}")
