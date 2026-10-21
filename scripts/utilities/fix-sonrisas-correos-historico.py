#!/usr/bin/env python3
"""
Wirea el workflow de Correos al Histórico (cambio mínimo).

Los emails Semanal y Mensual filtran al período actual (Filtro7 = semana actual,
Filtro4 = mes actual). Si leen la ventana de "Ingreso datos" pueden quedar con datos
incompletos en el borde de mes. Apuntándolos a la hoja "Histórico" (año completo,
de-duplicada, que mantiene el Reporte v3.5) los filtros de período siguen acotando el
email, pero ahora sobre datos completos.

ÚNICO cambio: las dos lecturas (`Get row(s) in sheet`, `Get row(s) in sheet1`) pasan a
leer el tab "Histórico" (mismo documento). No se toca nada más.

Lee  : clients/SNR_Sonrisas/03_workflows/sonrisas-correos-reportes-facturacion-v3.json
Crea : clients/SNR_Sonrisas/03_workflows/sonrisas-correos-reportes-facturacion-v4.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "clients/SNR_Sonrisas/03_workflows/sonrisas-correos-reportes-facturacion-v3.json"
DST = ROOT / "clients/SNR_Sonrisas/03_workflows/sonrisas-correos-reportes-facturacion-v4.json"

READ_NODES = ["Get row(s) in sheet", "Get row(s) in sheet1"]
HIST_TAB = "Histórico"


def main() -> int:
    wf = json.loads(SRC.read_text(encoding="utf-8"))
    nodes = {n.get("name"): n for n in wf["nodes"]}

    changed = []
    for name in READ_NODES:
        n = nodes.get(name)
        if n is None:
            print(f"ERROR: falta el nodo '{name}' en {SRC.name}", file=sys.stderr)
            return 2
        sn = n["parameters"].get("sheetName", {})
        prev = sn.get("cachedResultName") or sn.get("value")
        # Repuntar a la pestaña Histórico por nombre (mismo documentId)
        n["parameters"]["sheetName"] = {"__rl": True, "value": HIST_TAB, "mode": "name"}
        changed.append(f"{name}: tab '{prev}' -> '{HIST_TAB}'")

    if "name" in wf:
        wf["name"] = wf["name"].rstrip() + ""  # nombre se mantiene; sólo cambia el archivo

    out = json.dumps(wf, ensure_ascii=False, indent=2)
    json.loads(out)
    DST.write_text(out + "\n", encoding="utf-8")

    print(f"OK → {DST.relative_to(ROOT)}")
    for c in changed:
        print(f"   • {c}")
    print("   • (no se modificó ningún otro nodo)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
