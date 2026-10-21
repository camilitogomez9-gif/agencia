#!/usr/bin/env python3
"""
HPF · L0 — Congela la fuente de verdad pre-migración.

REGLA 0: este script SOLO hace GET contra n8n. No modifica nada.

El bot productivo vive en la instancia `dev[TU-INSTANCIA-N8N]` (NO en la de agencia).
Exporta los 8 workflows que componen la solución, con sha256, y escribe BASELINE.json
para poder detectar después si alguien tocó producción.

Uso:
    python3 scripts/utilities/hpf-congelar-base.py             # exporta y crea baseline
    python3 scripts/utilities/hpf-congelar-base.py --verificar # re-chequea contra el baseline
"""
import hashlib
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "clients/HPF_HappyFlops/03_workflows/base-prod-2026-08-06"
BASELINE = OUT / "BASELINE.json"

BASE_URL = "https://dev[TU-INSTANCIA-N8N]"
ENV_KEY = "HPF_N8N_API_KEY"

# Los 8 workflows que componen la solución pre-migración, resueltos desde los
# nodos executeWorkflow/toolWorkflow del main.
WORKFLOWS = {
    "pYtiBlhOTr7HVPmr": "main-happy-flops",
    "YR8yBPNdgVl0TxT1": "seg-rebeca",
    "D04kO8VPKoAKL004": "seg-imagen",
    "dNzLtCZFJnIqjlZx": "seg-cotizacion",
    "xo1sLt9cAhFAC6k3": "seg-7pasos",
    "SUgT7UPYyQ3NDgRp": "atencion-personalizada",
    "OPiuPFwRmq6QgACL": "tool-calculadora",
    "bYMfYToYsZMFpVDw": "kommo-salesbot-text-capture-runner",
}

# Referencia rota conocida: `Execute Workflow4` (rama imagen del seguimiento de
# 7 pasos) apunta a este id, que NO existe en la instancia. Se registra como punto.
REFERENCIAS_ROTAS = {"nkRBXbc4G0Cn67gY": "Execute Workflow4 → '7 Pasos, seg - Happpy Flops'"}


def load_env():
    env = {}
    for line in (REPO / ".env").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def get(key, path):
    req = urllib.request.Request(BASE_URL + path, headers={"X-N8N-API-KEY": key})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)


def canonical(wf):
    """JSON estable para hashear: sin metadatos volátiles."""
    return json.dumps(
        {k: wf[k] for k in ("name", "nodes", "connections", "settings") if k in wf},
        sort_keys=True,
        ensure_ascii=False,
    )


def main():
    verificar = "--verificar" in sys.argv
    key = load_env()[ENV_KEY]
    OUT.mkdir(parents=True, exist_ok=True)

    baseline, drift = {}, []
    prev = json.loads(BASELINE.read_text()) if (verificar and BASELINE.exists()) else {}

    for wid, slug in WORKFLOWS.items():
        try:
            wf = get(key, f"/api/v1/workflows/{wid}")
        except urllib.error.HTTPError as e:
            print(f"  !! {slug} ({wid}): HTTP {e.code}")
            drift.append(f"{slug}: inaccesible (HTTP {e.code})")
            continue

        sha = hashlib.sha256(canonical(wf).encode()).hexdigest()
        entry = {
            "id": wid, "name": wf.get("name"), "nodes": len(wf.get("nodes", [])),
            "active": wf.get("active"), "versionId": wf.get("versionId"),
            "updatedAt": wf.get("updatedAt"), "sha256": sha, "archivo": f"{slug}.json",
        }
        baseline[wid] = entry

        if verificar and wid in prev:
            for f in ("versionId", "updatedAt", "sha256", "active", "nodes"):
                if prev[wid].get(f) != entry[f]:
                    drift.append(f"{slug}.{f}: {prev[wid].get(f)!r} → {entry[f]!r}")
        else:
            (OUT / f"{slug}.json").write_text(
                json.dumps(wf, indent=2, ensure_ascii=False), encoding="utf-8")

        print(f"  {slug:36s} {wid}  nodos={entry['nodes']:4d}  "
              f"active={str(entry['active']):5s}  {sha[:12]}")

    if verificar:
        if drift:
            print("\n🔴 DRIFT — producción cambió desde el congelamiento:")
            for d in drift:
                print("   ", d)
            sys.exit(1)
        print(f"\n✅ Sin drift: los {len(baseline)} workflows están idénticos al baseline.")
        return

    BASELINE.write_text(json.dumps(baseline, indent=2, ensure_ascii=False), encoding="utf-8")
    total = sum(e["nodes"] for e in baseline.values())
    print(f"\n✅ Congelados {len(baseline)}/{len(WORKFLOWS)} workflows · {total} nodos totales")
    for wid, desc in REFERENCIAS_ROTAS.items():
        print(f"⚠️  Referencia rota en producción: {desc} → id {wid} no existe")
    print(f"   → {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
