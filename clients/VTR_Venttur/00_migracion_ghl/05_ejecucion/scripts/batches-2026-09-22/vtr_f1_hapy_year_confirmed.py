#!/usr/bin/env python3
"""Actualizar el jsCode del despachador: quitar el comment "la agencia typo, asumo Gap Year"
y reemplazar por confirmación explícita."""
import json, subprocess, hashlib
from pathlib import Path

ROOT = Path("/Users/camilo/Downloads/camilo-workspace")
POST = ROOT / "clients/VTR_Venttur/03_workflows/ghl-live-2026-09-22-batch-F/post/despachador.json"
WF_ID = "vrShEXQGGAo4FqAt"

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

wf = curl_json("GET", f"/workflows/{WF_ID}")
sel = next(n for n in wf["nodes"] if n["name"] == "Seleccionar (tope-2 + prioridad)")
old = "'hapy year':     '6aa1b0309686d7ff49f76c20',  // la agencia typo, asumo Gap Year"
new = "'hapy year':     '6aa1b0309686d7ff49f76c20',  // typo por Gap Year — confirmado por la agencia 2026-09-22"
if old in sel["parameters"]["jsCode"]:
    sel["parameters"]["jsCode"] = sel["parameters"]["jsCode"].replace(old, new)
    body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"], "settings": wf.get("settings", {})}
    curl_json("PUT", f"/workflows/{WF_ID}", data=body)
    print("✓ patched comment 'hapy year' → confirmado Gap Year")
else:
    print("↷ ya está confirmado (idempotente)")

final = curl_json("GET", f"/workflows/{WF_ID}")
with open(POST, "w") as f:
    json.dump(final, f, indent=2, ensure_ascii=False)
with open(POST, "rb") as f:
    sha = hashlib.sha256(f.read()).hexdigest()
print(f"💾 despachador.json · sha256={sha}")
