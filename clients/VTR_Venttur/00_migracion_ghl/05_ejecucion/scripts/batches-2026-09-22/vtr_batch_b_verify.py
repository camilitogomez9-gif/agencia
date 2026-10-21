#!/usr/bin/env python3
"""Verifica delta B2: reejecuta workflow con conteo de folios únicos en Airtable."""
import json, subprocess, uuid, time, hashlib
from pathlib import Path

ROOT = Path("/Users/camilo/Downloads/camilo-workspace")
CRED_POSTGRES = "ihpvM7nYMdLCwWDP"

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
    if not (200 <= int(code) < 300) and not allow_fail: raise RuntimeError(f"{method} {path} → {code}: {body}")
    try: return json.loads(body), code
    except: return body, code

def curl_webhook(url):
    cmd = ["curl", "-sS", "-w", "\n%{http_code}", "-X", "POST", "-H", "Content-Type: application/json",
           "--max-time", "300", "--data-binary", "{}", url]
    r = subprocess.run(cmd, capture_output=True, text=True)
    parts = r.stdout.rsplit("\n", 1)
    body = parts[0] if len(parts) == 2 else r.stdout
    try: return json.loads(body), (parts[1].strip() if len(parts) == 2 else "?")
    except: return body, (parts[1].strip() if len(parts) == 2 else "?")

# Workflow one-shot: mini query directa a Supabase para chequear COUNT DISTINCT
webhook_path = f"vtr-verify-{uuid.uuid4().hex[:8]}"
wf = {
    "name": "VTR Verify B2 (one-shot)",
    "nodes": [
        {"parameters": {"httpMethod": "POST", "path": webhook_path,
                        "responseMode": "responseNode", "options": {}},
         "id": str(uuid.uuid4()), "name": "Webhook", "type": "n8n-nodes-base.webhook",
         "typeVersion": 2.1, "position": [0, 0], "webhookId": str(uuid.uuid4())},
        {"parameters": {"operation": "executeQuery",
                        "query": ("SELECT (SELECT COUNT(*) FROM capi_folios) AS total, "
                                  "(SELECT COUNT(DISTINCT folio) FROM capi_folios) AS uniq, "
                                  "(SELECT COUNT(*) FROM capi_folios WHERE folio IS NULL OR folio = '') AS null_folio;"),
                        "options": {}},
         "id": str(uuid.uuid4()), "name": "Query", "type": "n8n-nodes-base.postgres",
         "typeVersion": 2.6, "position": [240, 0],
         "credentials": {"postgres": {"id": CRED_POSTGRES, "name": "Venttur"}}},
        {"parameters": {"respondWith": "json",
                        "responseBody": "={{ { total: $json.total, uniq: $json.uniq, null_folio: $json.null_folio } }}",
                        "options": {}},
         "id": str(uuid.uuid4()), "name": "Respond", "type": "n8n-nodes-base.respondToWebhook",
         "typeVersion": 1.1, "position": [480, 0]}
    ],
    "connections": {
        "Webhook": {"main": [[{"node": "Query", "type": "main", "index": 0}]]},
        "Query": {"main": [[{"node": "Respond", "type": "main", "index": 0}]]}
    },
    "settings": {}
}

created, _ = curl_json("POST", "/workflows", data=wf)
wid = created["id"]
print(f"✓ created verify workflow {wid}")
curl_json("POST", f"/workflows/{wid}/activate")
time.sleep(2)
url = f"{env_get('N8N_BASE_URL').rstrip('/')}/webhook/{webhook_path}"
resp, code = curl_webhook(url)
print(f"← http {code}: {resp}")
curl_json("POST", f"/workflows/{wid}/deactivate", allow_fail=True)
# Delete workflow (limpieza)
curl_json("DELETE", f"/workflows/{wid}", allow_fail=True)
print("✓ verify workflow deleted (cleanup)")
