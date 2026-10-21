#!/usr/bin/env python3
"""Aplica un paquete de ediciones al systemMessage del nodo `Agente IA WPP` del main `1eS1Z5k898c3ATnf`.

  python3 vtr_prompt_deploy.py --paso 2 [--execute]     prompt_paso2.py (reagendar + no inventar datos de la cita)
  python3 vtr_prompt_deploy.py --paso 4 [--execute]     prompt_paso4.py (voseo → tuteo)

Sin --execute: arma el texto nuevo, valida anclas, lo deja en OUT/candidato-pasoN.txt y no toca nada.
Con --execute: guarda pre/post del workflow (sha256), hace PUT y verifica que SÓLO cambió el systemMessage.
Rollback: PUT del JSON en ghl-live-2026-09-24-agente-link/pre/main-pasoN.json
"""
import copy, importlib, json, sys
from pathlib import Path
import importlib.util

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("p", HERE.parent / "batches-2026-09-23" / "vtr_pre_bsp_fixes.py")
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
sys.path.insert(0, str(HERE))

MAIN = "1eS1Z5k898c3ATnf"
AGENTE = "Agente IA WPP"
OUT = p.ROOT / "clients/VTR_Venttur/03_workflows/ghl-live-2026-09-24-agente-link"


def main():
    paso = sys.argv[sys.argv.index("--paso") + 1]
    mod = importlib.import_module(f"prompt_paso{paso}")
    c, wf = p.api("GET", f"/workflows/{MAIN}")
    if c != 200:
        sys.exit(f"❌ GET {c} {wf}")
    sm = p.node(wf, AGENTE)["parameters"]["options"]["systemMessage"]
    if mod.MARK in sm:
        print(f"↷ paso {paso} ya aplicado"); return
    nuevo = mod.apply(sm)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"candidato-paso{paso}.txt").write_text(nuevo)
    if "--execute" not in sys.argv:
        print(f"[dry-run] paso {paso} ok · {len(sm)} → {len(nuevo)} chars · {OUT / f'candidato-paso{paso}.txt'}"); return
    pre = copy.deepcopy(wf)
    p.node(wf, AGENTE)["parameters"]["options"]["systemMessage"] = nuevo
    h0 = p.save(pre, OUT / "pre" / f"main-paso{paso}.json")
    body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
            "settings": {k: v for k, v in (wf.get("settings") or {}).items() if k in p.SETTINGS_OK}}
    c, r = p.api("PUT", f"/workflows/{MAIN}", body)
    if c != 200:
        sys.exit(f"❌ PUT {c} {r}")
    c, post = p.api("GET", f"/workflows/{MAIN}")
    h1 = p.save(post, OUT / "post" / f"main-paso{paso}.json")
    A = {n["name"]: json.dumps(n, sort_keys=True) for n in pre["nodes"]}
    B = {n["name"]: json.dumps(n, sort_keys=True) for n in post["nodes"]}
    cambiados = [k for k in A if A[k] != B.get(k)] + [k for k in B if k not in A]
    chk = {"systemMessage": p.node(post, AGENTE)["parameters"]["options"]["systemMessage"] == nuevo,
           "solo_agente": cambiados == [AGENTE],
           "conexiones": json.dumps(pre["connections"], sort_keys=True) == json.dumps(post["connections"], sort_keys=True),
           "activo": post["active"]}
    print(("✅" if all(chk.values()) else "❌"), chk, f"· pre {h0[:12]} · post {h1[:12]}")


if __name__ == "__main__":
    main()
