#!/usr/bin/env python3
"""
Snapshot de los 13 workflows VTR desde n8n vivo → repo local.

Uso:
    export N8N_BASE_URL=$(grep '^N8N_BASE_URL=' .env | cut -d= -f2)
    export N8N_API_KEY=$(grep '^N8N_API_KEY=' .env | cut -d= -f2-)
    python3 snapshot-n8n-vtr.py <YYYY-MM-DD-suffix>

Ej:
    python3 snapshot-n8n-vtr.py 2026-09-25-pre-cutover
    python3 snapshot-n8n-vtr.py 2026-09-21-preventivo

Genera:
    clients/VTR_Venttur/03_workflows/vivo-<YYYY-MM-DD-suffix>/
        <slug>.json                 (1 por workflow)
        README.md                   (sha256 de cada + timestamp)
"""
import os, sys, json, hashlib, urllib.request
from pathlib import Path
from datetime import datetime, timezone

VTR_IDS = {
    "k3aivKSP67S97IHn": "main-venttur",
    "3sLd7KY3o8I7NvXi": "staging-agent-telegram",
    "2PSekVBxarsrnVBu": "confirmacion-agenda",
    "H6qYB3Oj97bxaTCX": "wf-estado-interrumpida",
    "b52CUYEkI2Ah3Xj6": "wf-estado-lead",
    "gRSMjzxggA4UePjz": "actualizar-link-enviado",
    "vrShEXQGGAo4FqAt": "despachador-proactivo-v2",
    "Xmyoewwa1W5gm1fy": "clasificador-cualificado",
    "DyrDumQgb6S4zHsS": "resumen-etiquetas-seguimientos",
    "CUuFxbst3iHpgeXS": "outreach-form-meta",
    "mkEP1qFN7MVb9qP0": "wf-rescate-post-link",
    "BzBCMGxEdJy6zmA9": "vtr-digest-diario-guardrail",
    "LrJuzU7qDeELWiAl": "barrido-interrumpida-ghl",
}

def fetch(url_base, key, wf_id):
    req = urllib.request.Request(f"{url_base}/api/v1/workflows/{wf_id}",
        headers={"X-N8N-API-KEY": key})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 snapshot-n8n-vtr.py <YYYY-MM-DD-suffix>"); sys.exit(1)
    suffix = sys.argv[1]
    url_base = os.environ["N8N_BASE_URL"].rstrip("/")
    key = os.environ["N8N_API_KEY"]

    repo_root = Path(__file__).resolve().parents[5]  # scripts/05_ejecucion/00_migracion_ghl/VTR_Venttur/clients/<REPO>/
    outdir = repo_root / "clients/VTR_Venttur/03_workflows" / f"vivo-{suffix}"
    outdir.mkdir(parents=True, exist_ok=True)

    hashes = {}
    for wf_id, slug in VTR_IDS.items():
        try:
            data = fetch(url_base, key, wf_id)
            body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
            path = outdir / f"{slug}.json"
            path.write_bytes(body)
            h = hashlib.sha256(body).hexdigest()
            hashes[slug] = (wf_id, h, data.get("active"), data.get("name",""))
            print(f"  ✅ {slug:<38} → {h[:12]}  [active={data.get('active')}]")
        except Exception as e:
            print(f"  ❌ {slug} ({wf_id}): {e}")

    # README
    now = datetime.now(timezone.utc).isoformat()
    readme = outdir / "README.md"
    with readme.open("w") as f:
        f.write(f"# Snapshot n8n VTR · vivo-{suffix}\n\n")
        f.write(f"**Generado:** {now}\n")
        f.write(f"**Origen:** {url_base}\n")
        f.write(f"**Workflows:** {len(hashes)}\n\n")
        f.write("| Slug | Workflow ID | Active | sha256 | Nombre |\n")
        f.write("|---|---|---|---|---|\n")
        for slug,(wid,h,active,name) in sorted(hashes.items()):
            f.write(f"| `{slug}` | `{wid}` | {active} | `{h}` | {name} |\n")
    print(f"\n📁 Snapshot en: {outdir}")
    print(f"📄 README: {readme}")

if __name__ == "__main__":
    main()
