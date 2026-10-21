#!/usr/bin/env python3
"""Descargar 3 workflows para investigar sessionKey."""
import json, subprocess
from pathlib import Path

ROOT = Path("/Users/camilo/Downloads/camilo-workspace")
OUT = ROOT / "clients/VTR_Venttur/03_workflows/ghl-live-2026-09-22-batch-F/pre"
OUT.mkdir(parents=True, exist_ok=True)

def env_get(k):
    r = subprocess.run(["grep", f"^{k}=", str(ROOT / ".env")], capture_output=True, text=True, check=True)
    return r.stdout.strip().split("\n")[0].split("=", 1)[1].strip().strip('"').strip("'")

def curl_workflow(wid, name):
    key = env_get("N8N_API_KEY")
    base = env_get("N8N_BASE_URL").rstrip("/")
    r = subprocess.run(
        ["curl", "-sSf", "-H", f"X-N8N-API-KEY: {key}", f"{base}/api/v1/workflows/{wid}"],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        print(f"❌ {name} ({wid}): {r.stderr}")
        return None
    with open(OUT / f"{name}.json", "w") as f:
        f.write(r.stdout)
    wf = json.loads(r.stdout)
    print(f"✓ {name}: nodes={len(wf['nodes'])} active={wf.get('active')}")
    return wf

wfs = {}
for wid, name in [("YB0UxwEVwzISdd54", "rescate-ghl"),
                   ("vrShEXQGGAo4FqAt", "despachador"),
                   ("3sLd7KY3o8I7NvXi", "staging-agent")]:
    wfs[name] = curl_workflow(wid, name)

# Buscar nodos con sessionKey / canonPhone / nsk
print("\n=== Buscar nodos con sessionKey / canonPhone / nsk ===")
for name, wf in wfs.items():
    if not wf: continue
    print(f"\n--- {name} ---")
    for n in wf["nodes"]:
        params = json.dumps(n.get("parameters", {}))
        if any(kw in params for kw in ["sessionKey", "canonPhone", "nsk(", "session_id", "session_key"]):
            # Encontrar el snippet relevante
            j = params.find("canonPhone")
            if j < 0: j = params.find("nsk(")
            if j < 0: j = params.find("sessionKey")
            if j < 0: j = params.find("session_id")
            snippet = params[max(0, j-100):j+300]
            print(f"  · {n['name']} ({n['type']})")
            print(f"    {snippet}")
