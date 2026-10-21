#!/usr/bin/env python3
"""
Verifica por re-export —nunca de memoria— que el workflow vivo quedó como se
esperaba después de una escritura, y que la deuda de test está en cero.

    python3 scripts/testing/hpf-verificar-deuda.py                 # solo deuda
    python3 scripts/testing/hpf-verificar-deuda.py --esperado X.json  # + diff contra lo esperado

Requiere HPF_N8N_API_KEY en el entorno.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# Valores que tienen que quedar así al cerrar. El debounce va en 50 s por
# decisión de la agencia del 2026-08-05, NO en los 15 que dice el protocolo.
DEUDA = {
    "debounce_segundos": 50,
    "entre_partes_segundos": 1.5,
    "returnIntermediateSteps": True,
    "nodos_deshabilitados": [],
}


def bajar(wf: str = "IPO1c36NLzkXrBh9") -> dict:
    key = os.environ.get("HPF_N8N_API_KEY")
    if not key:
        sys.exit("falta HPF_N8N_API_KEY en el entorno")
    req = urllib.request.Request(
        f"https://dev[TU-INSTANCIA-N8N]/api/v1/workflows/{wf}",
        headers={"X-N8N-API-KEY": key})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def revisar_deuda(d: dict) -> list[tuple[str, bool, str]]:
    ns = {n["name"]: n for n in d["nodes"]}
    out = []

    deshab = [n["name"] for n in d["nodes"] if n.get("disabled")]
    out.append(("ningún nodo deshabilitado", deshab == DEUDA["nodos_deshabilitados"],
                str(deshab or "ninguno")))

    deb = next((n for n in d["nodes"] if "Debounce" in n["name"] and n["type"].endswith("wait")), None)
    if deb:
        amt = deb["parameters"].get("amount")
        out.append((f"debounce en {DEUDA['debounce_segundos']} s",
                    amt == DEUDA["debounce_segundos"] and not deb.get("disabled"),
                    f"{deb['name']} = {amt}" + (" (DESHABILITADO)" if deb.get("disabled") else "")))

    ent = ns.get("Wait 1.5s Between Parts")
    if ent:
        out.append(("espera entre partes activa",
                    ent["parameters"].get("amount") == DEUDA["entre_partes_segundos"] and not ent.get("disabled"),
                    f"{ent['parameters'].get('amount')}" + (" (DESHABILITADO)" if ent.get("disabled") else "")))

    ag = next((n for n in d["nodes"] if "agent" in n["type"].lower()), None)
    if ag:
        ris = ag["parameters"].get("options", {}).get("returnIntermediateSteps")
        out.append(("returnIntermediateSteps en true", ris is True, str(ris)))

    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--esperado", help="JSON con el estado esperado, para diffear")
    args = ap.parse_args()

    real = bajar()
    print(f"vivo: {len(real['nodes'])} nodos · active={real['active']} · versionId={real['versionId']}")

    if args.esperado:
        esp = json.loads(Path(args.esperado).read_text())
        E = {n["name"]: n for n in esp["nodes"]}
        R = {n["name"]: n for n in real["nodes"]}
        dif = [k for k in E
               if json.dumps(E[k].get("parameters"), sort_keys=True)
               != json.dumps(R.get(k, {}).get("parameters"), sort_keys=True)]
        print(f"  nodos que no quedaron como se esperaba: {dif or 'ninguno'}")
        ce = sorted((c.get("id"), c.get("name"))
                    for n in esp["nodes"] for c in (n.get("credentials") or {}).values())
        cr = sorted((c.get("id"), c.get("name"))
                    for n in real["nodes"] for c in (n.get("credentials") or {}).values())
        print(f"  credenciales: {len(cr)} · preservadas: {ce == cr}")
        sw = real["connections"].get("Switch by Message Type", {}).get("main", [])
        destino = [x["node"] for x in (sw[3] or [])] if len(sw) > 3 else []
        print(f"  Switch salidas: {[len(x or []) for x in sw]} · fallback -> {destino or 'SIN CABLEAR'}")

    print("\ndeuda de test:")
    todo_ok = True
    for nombre, ok, detalle in revisar_deuda(real):
        print(f"  [{'OK ' if ok else 'NO '}] {nombre:<34} {detalle}")
        todo_ok &= ok
    print("\n" + ("deuda en cero" if todo_ok else "queda deuda pendiente"))
    sys.exit(0 if todo_ok else 1)


if __name__ == "__main__":
    main()
