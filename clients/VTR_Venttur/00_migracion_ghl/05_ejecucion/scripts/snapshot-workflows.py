#!/usr/bin/env python3
"""
Snapshot de los workflows productivos VTR → JSON + sha256. Para CIERRE-3 y backups pre/post.

Uso:
  python3 snapshot-workflows.py <dir_destino>
Ej:
  python3 snapshot-workflows.py clients/VTR_Venttur/03_workflows/ghl-live-cutover-final
"""
import re, json, sys, hashlib, os, urllib.request

ROOT = "/Users/camilo/Downloads/camilo-workspace"


def env(key):
    for line in open(f"{ROOT}/.env"):
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip()


BASE = env("N8N_BASE_URL").rstrip("/"); KEY = env("N8N_API_KEY")

# Stack GHL (14) + los 6 viejos que se apagan en el cutover
WORKFLOWS = {
    "1eS1Z5k898c3ATnf": "main-venttur-ghl",
    "v9XkOfL9dQtY2wyv": "vtr-tool-elevar-ghl",
    "Xmyoewwa1W5gm1fy": "clasificador-postconv",
    "mf7VQJelfieCDJ5r": "meta-capi-supabase",
    "4HgMkK34xqITULM3": "capi-registro-folio-supabase",
    "qYgeTc9PCq3TiGDn": "W11-estado-contesto",
    "OaOyHA2tfjMtuWTk": "W14-correo-semanal",
    "vrShEXQGGAo4FqAt": "despachador-proactivo",
    "YB0UxwEVwzISdd54": "rescate-post-link-ghl",
    "LrJuzU7qDeELWiAl": "barrido-interrumpida",
    "LhPSfMYtQbNcEK32": "W4-formulario-landing-ghl",
    "AS9ZNhY3GJDfhY3P": "W6-confirmacion-agenda-ghl",
    "TROsQ5h78baAuVOY": "W9-actualizar-link-enviado-ghl",
    "MbPTKvy0bq8b4YAw": "W10-outreach-ingest-ghl",
    # Los 6 productivos viejos: sin ellos el snapshot pre-cutover no sirve para volver atrás
    "k3aivKSP67S97IHn": "OLD-main-venttur-manychat",
    "2PSekVBxarsrnVBu": "OLD-confirmacion-agenda",
    "ZB6erhWicZmDfC4I": "OLD-formulario-clientify",
    "CUuFxbst3iHpgeXS": "OLD-outreach-form-meta",
    "9yCbynoKDt9hgiBq": "OLD-capi-registro-folio-airtable",
    "H6qYB3Oj97bxaTCX": "OLD-estado-interrumpida-airtable",
}


def get(wid):
    req = urllib.request.Request(f"{BASE}/api/v1/workflows/{wid}", headers={"X-N8N-API-KEY": KEY})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def main():
    if len(sys.argv) < 2:
        print("uso: snapshot-workflows.py <dir_destino>"); sys.exit(1)
    out = sys.argv[1] if os.path.isabs(sys.argv[1]) else f"{ROOT}/{sys.argv[1]}"
    os.makedirs(out, exist_ok=True)
    lines = ["# Snapshot workflows VTR\n", "| archivo | id | active | nodos | sha256 |", "|---|---|---|---:|---|"]
    for wid, name in WORKFLOWS.items():
        try:
            wf = get(wid)
        except Exception as e:
            print(f"  ✗ {name} ({wid}): {e}"); lines.append(f"| {name} | {wid} | ERR | - | {e} |"); continue
        path = f"{out}/{name}.json"
        txt = json.dumps(wf, indent=2, ensure_ascii=False)
        # Tokens hardcodeados en nodos viejos (ManyChat) no se copian al repo: el snapshot es para leer/diffear,
        # el rollback es re-activar el workflow vivo, no re-importarlo.
        txt = re.sub(r"(Bearer )[0-9]+:[A-Za-z0-9]+", r"\1<REDACTED>", txt)
        txt = re.sub(r"sk-(proj-)?[A-Za-z0-9_-]{20,}", "sk-<REDACTED>", txt)
        open(path, "w").write(txt)
        sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
        active = wf.get("active"); nodes = len(wf.get("nodes", []))
        print(f"  ✓ {name}  active={active} nodos={nodes}")
        lines.append(f"| {name} | `{wid}` | {'ON' if active else 'OFF'} | {nodes} | `{sha[:16]}…` |")
    open(f"{out}/README.md", "w").write("\n".join(lines) + "\n")
    print(f"\n💾 {len(WORKFLOWS)} workflows → {out} (+ README.md con sha256)")


if __name__ == "__main__":
    main()
