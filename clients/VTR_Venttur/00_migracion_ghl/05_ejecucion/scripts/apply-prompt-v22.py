#!/usr/bin/env python3
"""
Aplicar el prompt v2.2 (agente-venttur-system-prompt-v2.2.md, 49.375 chars, 0 menciones a "Diego")
al nodo `Agente IA WPP` de un workflow n8n VTR.

Uso:
    export N8N_BASE_URL=$(grep '^N8N_BASE_URL=' .env | cut -d= -f2)
    export N8N_API_KEY=$(grep '^N8N_API_KEY=' .env | cut -d= -f2-)

    # Dry-run (muestra qué haría, no toca nada):
    python3 apply-prompt-v22.py staging
    python3 apply-prompt-v22.py vivo

    # Apply real (irreversible sin snapshot previo):
    python3 apply-prompt-v22.py staging --apply
    python3 apply-prompt-v22.py vivo --apply

Cronograma según guía ejecutable:
    D-1 (25/9 12:00): apply staging + smoke.
    D-day (26/9 09:00): apply vivo tras GO/NO-GO check.

Antes de --apply vivo: sacar snapshot preventivo con snapshot-n8n-vtr.py.
"""
import os, sys, json, urllib.request, hashlib
from pathlib import Path

TARGETS = {
    "staging": {"id": "3sLd7KY3o8I7NvXi", "name": "[Venttur] GHL staging (Telegram test)"},
    "vivo":    {"id": "k3aivKSP67S97IHn", "name": "[Venttur]"},
}
NODE_NAME = "Agente IA WPP"

def load_v22():
    repo = Path(__file__).resolve().parents[5]
    p = repo / "clients/VTR_Venttur/04_agents/agente-venttur-system-prompt-v2.2.md"
    content = p.read_text(encoding="utf-8")
    if "diego" in content.lower():
        raise SystemExit(f"❌ ABORTO: v2.2 file has 'Diego' — refuse to deploy: {p}")
    return content

def fetch_workflow(url_base, key, wf_id):
    req = urllib.request.Request(f"{url_base}/api/v1/workflows/{wf_id}",
                                  headers={"X-N8N-API-KEY": key})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def put_workflow(url_base, key, wf_id, wf_data):
    # n8n API PUT full workflow — payload debe incluir name/nodes/connections/settings mínimo
    keep = {k: wf_data[k] for k in ("name","nodes","connections","settings") if k in wf_data}
    body = json.dumps(keep).encode()
    req = urllib.request.Request(
        f"{url_base}/api/v1/workflows/{wf_id}",
        data=body, method="PUT",
        headers={"X-N8N-API-KEY": key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in TARGETS:
        print(f"Uso: python3 apply-prompt-v22.py <staging|vivo> [--apply]"); sys.exit(2)
    target = sys.argv[1]
    apply_real = "--apply" in sys.argv[2:]
    url_base = os.environ["N8N_BASE_URL"].rstrip("/")
    key = os.environ["N8N_API_KEY"]

    v22 = load_v22()
    v22_hash = hashlib.sha256(v22.encode()).hexdigest()
    print(f"═══ Prompt v2.2 (fuente) ═══")
    print(f"  chars: {len(v22)}")
    print(f"  sha256: {v22_hash}")
    print(f"  menciones 'Diego': {v22.lower().count('diego')} (esperado 0)")

    wf_id = TARGETS[target]["id"]
    wf = fetch_workflow(url_base, key, wf_id)
    print(f"\n═══ Target: {target} ({TARGETS[target]['name']}) ═══")
    print(f"  wf_id: {wf_id}")

    node = None
    for n in wf.get("nodes", []):
        if n.get("name") == NODE_NAME:
            node = n; break
    if not node:
        raise SystemExit(f"❌ nodo '{NODE_NAME}' no encontrado en {wf.get('name')}")

    opts = node.get("parameters", {}).get("options", {})
    current_sm = opts.get("systemMessage", "")
    print(f"  chars vivos: {len(current_sm)}")
    print(f"  menciones 'Diego' vivos: {current_sm.lower().count('diego')}")

    # Mostrar diff-metrics
    delta = len(v22) - len(current_sm)
    print(f"\n  ▼ Δ chars: {delta:+d}")

    if not apply_real:
        print("\n⏹  DRY-RUN — no se aplicó. Correr con --apply para pisar.")
        return

    # Aplicar: sustituir systemMessage manteniendo el `=` prefix si estaba (n8n usa `=` para markear expresion)
    new_sm = ("=" + v22) if current_sm.startswith("=") else v22
    node["parameters"]["options"]["systemMessage"] = new_sm

    print("\n⏳ PUT workflow...")
    result = put_workflow(url_base, key, wf_id, wf)
    # verificar
    wf2 = fetch_workflow(url_base, key, wf_id)
    for n in wf2.get("nodes", []):
        if n.get("name") == NODE_NAME:
            sm2 = n.get("parameters",{}).get("options",{}).get("systemMessage","")
            hits = sm2.lower().count("diego")
            print(f"✅ Verificación: chars post={len(sm2)} · menciones 'Diego' post={hits}")
            if hits > 0:
                raise SystemExit(f"❌ ADVERTENCIA: el vivo aún tiene 'Diego' post-apply — revisar")
            print(f"🎉 Deploy {target} OK.")
            return

if __name__ == "__main__":
    main()
