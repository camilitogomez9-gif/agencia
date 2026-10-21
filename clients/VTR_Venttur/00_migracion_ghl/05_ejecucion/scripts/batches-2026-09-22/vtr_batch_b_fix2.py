#!/usr/bin/env python3
"""
Fix B2 iteración 2: agregar IF filter para descartar rows con Folio null/vacío.
"""
import json
import subprocess
import uuid
import time
import hashlib
from pathlib import Path

ROOT = Path("/Users/camilo/Downloads/camilo-workspace")
BATCH_DIR = ROOT / "clients/VTR_Venttur/03_workflows/ghl-live-2026-09-22-batch-B"
WF_B2_ID = "FoDzrFAEynflWjeG"
CRED_POSTGRES = "ihpvM7nYMdLCwWDP"
CRED_POSTGRES_NAME = "Venttur"


def env_get(key):
    result = subprocess.run(["grep", f"^{key}=", str(ROOT / ".env")],
                            capture_output=True, text=True, check=True)
    return result.stdout.strip().split("\n")[0].split("=", 1)[1].strip().strip('"').strip("'")


def curl_json(method, path, data=None, allow_fail=False):
    base = env_get("N8N_BASE_URL").rstrip("/")
    key = env_get("N8N_API_KEY")
    cmd = ["curl", "-sS", "-w", "\n%{http_code}", "-X", method,
           "-H", f"X-N8N-API-KEY: {key}", "-H", "Content-Type: application/json"]
    if data is not None:
        cmd.extend(["--data-binary", "@-"])
    cmd.append(f"{base}/api/v1{path}")
    r = subprocess.run(cmd, input=json.dumps(data) if data else None,
                       capture_output=True, text=True)
    parts = r.stdout.rsplit("\n", 1)
    body = parts[0] if len(parts) == 2 else r.stdout
    code = parts[1].strip() if len(parts) == 2 else "?"
    if not (200 <= int(code) < 300) and not allow_fail:
        raise RuntimeError(f"curl {method} {path} → {code}:\n{body}")
    try: return json.loads(body), code
    except json.JSONDecodeError: return body, code


def curl_webhook(url):
    cmd = ["curl", "-sS", "-w", "\n%{http_code}", "-X", "POST",
           "-H", "Content-Type: application/json", "--max-time", "600",
           "--data-binary", "{}", url]
    r = subprocess.run(cmd, capture_output=True, text=True)
    parts = r.stdout.rsplit("\n", 1)
    body = parts[0] if len(parts) == 2 else r.stdout
    code = parts[1].strip() if len(parts) == 2 else "?"
    try: return json.loads(body), code
    except json.JSONDecodeError: return body, code


def main():
    print(f"📥 GET workflow B2...")
    wf, _ = curl_json("GET", f"/workflows/{WF_B2_ID}")

    nodes = wf["nodes"]
    # Añadir IF node "Has folio?" entre Airtable Folios y Upsert folio
    if_node = {
        "parameters": {
            "conditions": {
                "options": {
                    "caseSensitive": True,
                    "leftValue": "",
                    "typeValidation": "loose",
                    "version": 2
                },
                "conditions": [
                    {
                        "id": "has-folio-2026-09-22",
                        "leftValue": "={{ ($json.Folio || '').toString().trim() }}",
                        "rightValue": "",
                        "operator": {"type": "string", "operation": "notEmpty", "singleValue": True}
                    }
                ],
                "combinator": "and"
            },
            "options": {}
        },
        "id": str(uuid.uuid4()),
        "name": "Has folio?",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2.2,
        "position": [360, 0]
    }

    # Insertar el IF y sacar la conexión directa Airtable→Upsert
    # Ver si ya existe (idempotente si re-corre)
    if not any(n["name"] == "Has folio?" for n in nodes):
        nodes.append(if_node)

    # Reajustar conexiones
    conns = wf["connections"]
    conns["Airtable Folios"] = {"main": [[{"node": "Has folio?", "type": "main", "index": 0}]]}
    conns["Has folio?"] = {
        "main": [
            [{"node": "Upsert folio", "type": "main", "index": 0}],  # rama true
            []  # rama false (descartar)
        ]
    }
    # Upsert folio → Count after ya existe

    # Actualizar el Respond node para reportar counts precisos
    for n in nodes:
        if n["name"] == "Respond":
            n["parameters"]["responseBody"] = (
                "={{ { ok: true, "
                "supabase_count_after: $json.supabase_count, "
                "airtable_count: $('Airtable Folios').all().length, "
                "with_folio: $('Has folio?').all().length, "
                "skipped_null_folio: $('Airtable Folios').all().length - $('Has folio?').all().length "
                "} }}"
            )

    put_body = {"name": wf["name"], "nodes": nodes,
                "connections": conns, "settings": wf.get("settings", {})}
    print(f"📤 PUT (agregar IF filter)...")
    curl_json("PUT", f"/workflows/{WF_B2_ID}", data=put_body)

    print(f"🔛 activate...")
    curl_json("POST", f"/workflows/{WF_B2_ID}/activate")
    time.sleep(3)

    webhook_path = None
    for n in nodes:
        if n["type"] == "n8n-nodes-base.webhook":
            webhook_path = n["parameters"]["path"]

    base = env_get("N8N_BASE_URL").rstrip("/")
    url = f"{base}/webhook/{webhook_path}"
    print(f"⚡ curl POST {url}...")
    print(f"   (esto puede tomar 30-60s por 4006 rows)")
    resp, http_code = curl_webhook(url)
    print(f"   ← http {http_code}")
    if isinstance(resp, dict):
        print(f"   ← body: {json.dumps(resp, indent=2)}")
    else:
        print(f"   ← body raw: {str(resp)[:400]}")

    print(f"🔴 deactivate...")
    curl_json("POST", f"/workflows/{WF_B2_ID}/deactivate", allow_fail=True)

    # Save snapshot
    final_wf, _ = curl_json("GET", f"/workflows/{WF_B2_ID}")
    path = BATCH_DIR / "b2-migrate-folios.json"
    with open(path, "w") as f:
        json.dump(final_wf, f, indent=2, ensure_ascii=False)
    with open(path, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    print(f"💾 {path.name} · sha256={sha}")

    return resp


if __name__ == "__main__":
    result = main()
    print(f"\n{'='*50}")
    print(f"result: {result}")
