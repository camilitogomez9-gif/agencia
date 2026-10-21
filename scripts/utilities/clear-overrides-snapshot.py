#!/usr/bin/env python3
"""
clear-overrides-snapshot.py
Limpia los overrides manuales aplicados por `override-snapshot-codigos.py`.
Restaura las entradas P* (P0000, P1000-P1004, P2000-P2002) en mayo y junio a
los valores que vinieron del xlsx vigente (PROTESIS), porque resolver la
ambigüedad PERIODONCIA↔PROTESIS por `Nombre categoría` del row es el patrón
correcto (replica del v3.5 viejo: CODIGOS_AMBIGUOS + resolverAmbiguo).

Después de correr este script:
- El snapshot tiene los 9 códigos P* en mayo+junio como PROTESIS.
- Las entradas OVERRIDE_MANUAL del changelog se eliminan.
- Re-generar los bloques JS con regen-bloques-js-from-snapshot.py.

El JS embebido en los workflows NO usa el snapshot para los códigos ambiguos:
hace resolverAmbiguo(row.Categoria) que lee el `Nombre categoría` original
de la fila del Histórico.

Uso:
    python3 scripts/utilities/clear-overrides-snapshot.py

Idempotente: si no hay overrides aplicados, no toca nada.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path


SNAPSHOT_REL = Path("clients") / "SNR_Sonrisas" / "_snapshots" / "codigos-historico.json"

# Entradas "naturales" (vienen del xlsx, sin override) para los 9 ambiguos
CODIGOS_P_AMBIGUOS = ["P0000", "P1000", "P1001", "P1002", "P1003", "P1004", "P2000", "P2001", "P2002"]
ENTRADA_NATURAL = {
    "categoria": "PROTESIS",  # lo que dice el xlsx de mayo y de junio para esos códigos
    "clase": None,
    "computaImporte": True,
    "computaCantidad": True,
}
MESES_RESTAURADOS = ["2026-05", "2026-06"]


def workspace_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def main() -> int:
    snapshot_path = workspace_root() / SNAPSHOT_REL
    if not snapshot_path.exists():
        print(f"❌ Snapshot no encontrado: {snapshot_path}", file=sys.stderr)
        return 1

    with snapshot_path.open("r", encoding="utf-8") as f:
        snap = json.load(f)

    if snap.get("version", 1) < 2:
        print("❌ Snapshot está en v1. No tiene sentido limpiar overrides.", file=sys.stderr)
        return 1

    snap.setdefault("changelog", [])

    restaurados = 0
    skip = 0
    for cod in CODIGOS_P_AMBIGUOS:
        if cod not in snap.get("codigos", {}):
            print(f"⚠  {cod} no está en snapshot — skip")
            skip += 1
            continue
        for mes in MESES_RESTAURADOS:
            actual = snap["codigos"][cod].get("meses", {}).get(mes)
            if actual == ENTRADA_NATURAL:
                continue
            snap["codigos"][cod].setdefault("meses", {})[mes] = dict(ENTRADA_NATURAL)
            restaurados += 1

    # Limpiar entradas OVERRIDE_MANUAL del changelog
    cl_antes = len(snap["changelog"])
    snap["changelog"] = [c for c in snap["changelog"] if c.get("tipo") != "OVERRIDE_MANUAL"]
    cl_borrados = cl_antes - len(snap["changelog"])

    # Re-ordenar
    snap["codigos"] = {c: snap["codigos"][c] for c in sorted(snap["codigos"].keys())}
    for cod, info in snap["codigos"].items():
        if "meses" in info:
            info["meses"] = {m: info["meses"][m] for m in sorted(info["meses"].keys())}

    snap["last_updated"] = date.today().isoformat()

    with snapshot_path.open("w", encoding="utf-8") as f:
        json.dump(snap, f, indent=2, ensure_ascii=False)
        f.write("\n")

    sep = "═" * 70
    print(sep)
    print("OVERRIDES LIMPIADOS")
    print(sep)
    print(f"  Snapshot:                  {snapshot_path}")
    print(f"  Entradas P* restauradas:   {restaurados} (PROTESIS, mayo + junio)")
    print(f"  Códigos skip (no existían): {skip}")
    print(f"  Entradas changelog borradas: {cl_borrados}")
    print(sep)
    print("Siguiente: re-modificar update-sonrisas-nodes.py + regenerar JS con resolución de ambiguos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
