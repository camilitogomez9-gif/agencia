#!/usr/bin/env python3
"""
Batch F.2 · Reconciliar sessionKey `+`/sin-`+` en rescate + despachador.
Default D5: alinear a `canonPhone()` (con `+`) — el que usa staging + memoria.
"""
import json, subprocess, hashlib
from pathlib import Path

ROOT = Path("/Users/camilo/Downloads/camilo-workspace")
BATCH_DIR = ROOT / "clients/VTR_Venttur/03_workflows/ghl-live-2026-09-22-batch-F"
POST_DIR = BATCH_DIR / "post"
POST_DIR.mkdir(parents=True, exist_ok=True)


def env_get(k):
    r = subprocess.run(["grep", f"^{k}=", str(ROOT / ".env")], capture_output=True, text=True, check=True)
    return r.stdout.strip().split("\n")[0].split("=", 1)[1].strip().strip('"').strip("'")


def curl_json(method, path, data=None):
    key = env_get("N8N_API_KEY"); base = env_get("N8N_BASE_URL").rstrip("/")
    cmd = ["curl", "-sSf", "-X", method, "-H", f"X-N8N-API-KEY: {key}",
           "-H", "Content-Type: application/json"]
    if data is not None: cmd.extend(["--data-binary", "@-"])
    cmd.append(f"{base}/api/v1{path}")
    r = subprocess.run(cmd, input=json.dumps(data) if data else None,
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def patch_workflow(wf_id, patches):
    """Aplica patches (list of (node_name, old_str, new_str)) al workflow."""
    wf = curl_json("GET", f"/workflows/{wf_id}")
    changes = 0
    for node_name, old, new in patches:
        for n in wf["nodes"]:
            if n["name"] == node_name:
                js = n["parameters"].get("jsCode", "")
                if old in js:
                    n["parameters"]["jsCode"] = js.replace(old, new)
                    changes += 1
                    print(f"  ✓ patched {node_name}")
                elif new in js:
                    print(f"  ↷ {node_name} ya tiene el fix (idempotente)")
                else:
                    print(f"  ⚠️ {node_name}: no encontré patrón")
                break
    if changes:
        body = {"name": wf["name"], "nodes": wf["nodes"],
                "connections": wf["connections"], "settings": wf.get("settings", {})}
        curl_json("PUT", f"/workflows/{wf_id}", data=body)
    return changes


def snapshot(wf_id, name):
    wf = curl_json("GET", f"/workflows/{wf_id}")
    p = POST_DIR / f"{name}.json"
    with open(p, "w") as f:
        json.dump(wf, f, indent=2, ensure_ascii=False)
    with open(p, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    print(f"    💾 {p.name} · sha256={sha}")


print("═══ Rescate GHL YB0UxwEVwzISdd54 ═══")
patch_workflow("YB0UxwEVwzISdd54", [
    ("Code: Fase 1 (GHL)", "const session_key = nsk(phone);", "const session_key = '+' + nsk(phone);"),
    ("Code: Fase 2 (GHL)", "const session_key = nsk(phone);", "const session_key = '+' + nsk(phone);"),
])
snapshot("YB0UxwEVwzISdd54", "rescate-ghl")

print("\n═══ Despachador vrShEXQGGAo4FqAt ═══")
patch_workflow("vrShEXQGGAo4FqAt", [
    ("Seleccionar (tope-2 + prioridad)", "session_key: nsk(c.phone)", "session_key: '+' + nsk(c.phone)"),
])
snapshot("vrShEXQGGAo4FqAt", "despachador")

print("\n✅ Batch F.2 aplicado.")
