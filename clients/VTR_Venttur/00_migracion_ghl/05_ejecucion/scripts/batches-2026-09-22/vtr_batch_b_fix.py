#!/usr/bin/env python3
"""
Fix Batch B2: corregir Timestamp (Unix epoch ms) → ISO string antes del INSERT.

Re-usa el workflow B2 existente (FoDzrFAEynflWjeG). Modifica solo el nodo Upsert folio.
Re-ejecuta y verifica.
"""
import json
import subprocess
import sys
import uuid
import time
from pathlib import Path

ROOT = Path("/Users/camilo/Downloads/camilo-workspace")
BATCH_DIR = ROOT / "clients/VTR_Venttur/03_workflows/ghl-live-2026-09-22-batch-B"
WF_B2_ID = "FoDzrFAEynflWjeG"


def env_get(key):
    result = subprocess.run(["grep", f"^{key}=", str(ROOT / ".env")],
                            capture_output=True, text=True, check=True)
    return result.stdout.strip().split("\n")[0].split("=", 1)[1].strip().strip('"').strip("'")


def curl_json(method, path, data=None, allow_fail=False):
    base = env_get("N8N_BASE_URL").rstrip("/")
    key = env_get("N8N_API_KEY")
    url = f"{base}/api/v1{path}"
    cmd = ["curl", "-sS", "-w", "\n%{http_code}", "-X", method,
           "-H", f"X-N8N-API-KEY: {key}", "-H", "Content-Type: application/json"]
    if data is not None:
        cmd.extend(["--data-binary", "@-"])
    cmd.append(url)
    result = subprocess.run(cmd, input=json.dumps(data) if data else None,
                            capture_output=True, text=True)
    parts = result.stdout.rsplit("\n", 1)
    body = parts[0] if len(parts) == 2 else result.stdout
    code = parts[1].strip() if len(parts) == 2 else "?"
    if not (200 <= int(code) < 300) and not allow_fail:
        raise RuntimeError(f"curl {method} {path} → {code}:\n{body}")
    try:
        return json.loads(body), code
    except json.JSONDecodeError:
        return body, code


def curl_webhook(url):
    cmd = ["curl", "-sS", "-w", "\n%{http_code}", "-X", "POST",
           "-H", "Content-Type: application/json", "--max-time", "600",
           "--data-binary", "{}", url]
    result = subprocess.run(cmd, capture_output=True, text=True)
    parts = result.stdout.rsplit("\n", 1)
    body = parts[0] if len(parts) == 2 else result.stdout
    code = parts[1].strip() if len(parts) == 2 else "?"
    try:
        return json.loads(body), code
    except json.JSONDecodeError:
        return body, code


def main():
    print(f"📥 GET workflow B2 {WF_B2_ID}...")
    wf, _ = curl_json("GET", f"/workflows/{WF_B2_ID}")
    print(f"   {wf['name']} · nodes={len(wf['nodes'])}")

    # Encontrar y modificar Upsert folio
    upsert_node = None
    for n in wf["nodes"]:
        if n["name"] == "Upsert folio":
            upsert_node = n
            break
    assert upsert_node, "nodo 'Upsert folio' no encontrado"

    # Cambio 1: query sin ::timestamptz explícito (ya que le pasamos ISO)
    # Cambio 2: queryReplacement convierte Timestamp (bigint ms) → ISO string
    upsert_node["parameters"]["query"] = (
        "INSERT INTO capi_folios (folio,fbclid,fbc,fbp,programa,ts,landing_url,user_agent,ip,updated_at) "
        "VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,now()) "
        "ON CONFLICT (folio) DO UPDATE SET "
        "fbclid=EXCLUDED.fbclid,fbc=EXCLUDED.fbc,fbp=EXCLUDED.fbp,"
        "programa=EXCLUDED.programa,ts=EXCLUDED.ts,landing_url=EXCLUDED.landing_url,"
        "user_agent=EXCLUDED.user_agent,ip=EXCLUDED.ip,updated_at=now()"
    )
    upsert_node["parameters"]["options"]["queryReplacement"] = (
        "={{ ["
        "$json.Folio || null, "
        "$json.fbclid || null, "
        "$json.fbc || null, "
        "$json.fbp || null, "
        "$json.Programa || null, "
        "($json.Timestamp != null ? new Date($json.Timestamp).toISOString() : null), "
        "$json['Landing URL'] || null, "
        "$json.user_agent || null, "
        "$json.ip || null"
        "] }}"
    )

    # PUT
    put_body = {"name": wf["name"], "nodes": wf["nodes"],
                "connections": wf["connections"], "settings": wf.get("settings", {})}
    print(f"📤 PUT /workflows/{WF_B2_ID} (fix Timestamp bigint→ISO)...")
    curl_json("PUT", f"/workflows/{WF_B2_ID}", data=put_body)
    print(f"   ✓ patched")

    # Activate
    print(f"🔛 activate...")
    curl_json("POST", f"/workflows/{WF_B2_ID}/activate")
    time.sleep(3)

    # Encontrar webhook path
    webhook_path = None
    for n in wf["nodes"]:
        if n["type"] == "n8n-nodes-base.webhook":
            webhook_path = n["parameters"]["path"]
            break

    base = env_get("N8N_BASE_URL").rstrip("/")
    url = f"{base}/webhook/{webhook_path}"
    print(f"⚡ curl POST {url}...")
    resp, http_code = curl_webhook(url)
    print(f"   ← http {http_code}")
    print(f"   ← body: {json.dumps(resp, indent=2) if isinstance(resp, dict) else resp}")

    # Deactivate
    print(f"🔴 deactivate...")
    curl_json("POST", f"/workflows/{WF_B2_ID}/deactivate", allow_fail=True)

    # Save updated workflow snapshot
    final_wf, _ = curl_json("GET", f"/workflows/{WF_B2_ID}")
    path = BATCH_DIR / "b2-migrate-folios.json"
    with open(path, "w") as f:
        json.dump(final_wf, f, indent=2, ensure_ascii=False)

    import hashlib
    with open(path, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    print(f"💾 {path.name} · sha256={sha}")

    # Update log
    log_path = ROOT / "clients/VTR_Venttur/05_ejecucion/logs/batch-b-supabase-2026-09-22.md"
    if isinstance(resp, dict) and resp.get("ok"):
        supabase_count = resp.get("supabase_count_after")
        airtable_count = resp.get("airtable_count")
        delta = int(supabase_count) - int(airtable_count) if str(supabase_count).isdigit() and str(airtable_count).isdigit() else "?"
        print(f"\n📊 Post-fix counts:")
        print(f"   Airtable Folios CAPI: {airtable_count}")
        print(f"   Supabase capi_folios: {supabase_count}")
        print(f"   Delta (esperado 0):    {delta}")

        # Append to log
        with open(log_path, "a") as f:
            f.write(f"\n\n## Fix B2 · 2026-09-22 04:XX UTC\n\n"
                   f"Error inicial: `cannot cast type bigint to timestamp with time zone`. "
                   f"Airtable envía `Timestamp` como bigint (Unix epoch ms). "
                   f"Fix: `queryReplacement` convierte con `new Date($json.Timestamp).toISOString()`.\n\n"
                   f"| Métrica | Valor |\n|---|---|\n"
                   f"| Airtable Folios CAPI | {airtable_count} |\n"
                   f"| Supabase capi_folios | {supabase_count} |\n"
                   f"| Delta | {delta} |\n")


if __name__ == "__main__":
    main()
