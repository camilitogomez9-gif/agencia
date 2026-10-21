#!/usr/bin/env python3
"""
override-snapshot-codigos.py
Aplica overrides manuales al snapshot mes-aware de Sonrisas.
Para casos donde la "verdad operativa" (cómo se cobró en realidad) difiere de
lo que dice el xlsx vigente (que refleja una decisión posterior del catálogo).

Caso real (2026-06-14): los códigos `P*` (P0000, P1000-P1004, P2000-P2002) en
mayo y junio fueron facturados como PERIODONCIA en la realidad (Histórico_2M
tiene 20 filas mayo + 3 filas junio = $63.070 con códigos P*), pero el xlsx de
mayo y junio los mapea a PROTESIS porque Cecilia eliminó las entradas
PERIODONCIA del catálogo (migró a códigos nuevos `PE*`). Sin override, el
sistema mes-aware seguiría clasificándolas como PROTESIS.

Uso:
    python3 scripts/utilities/override-snapshot-codigos.py

Hard-coded el override para el incidente PERIODONCIA Mayo. Si necesitás
overrides distintos, editar OVERRIDES.

El script:
1. Carga snapshot v2.
2. Aplica overrides sobre `codigos[X].meses[YYYY-MM]`.
3. Loggea cada override en `snapshot.changelog` con motivo.
4. Guarda.

NO toca `update-sonrisas-nodes.py` ni regenera los bloques JS. Después de
correr este script, para regenerar los bloques: corré
`regen-bloques-js-from-snapshot.py` (NO `update-sonrisas-nodes.py`, que
pisaría los overrides si lo corrés con un xlsx encima).
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path


SNAPSHOT_REL = Path("clients") / "SNR_Sonrisas" / "_snapshots" / "codigos-historico.json"

# ── DEFINICIÓN DEL OVERRIDE ─────────────────────────────────────────────────
# Cada entrada: (mes_arg YYYY-MM, codigo, categoria_nueva, clase_nueva, computaImporte, computaCantidad, motivo)
CODIGOS_PERIODONCIA_VIEJOS = ["P0000", "P1000", "P1001", "P1002", "P1003", "P1004", "P2000", "P2001", "P2002"]
MESES_AFECTADOS = ["2026-05", "2026-06"]
MOTIVO_INCIDENTE = (
    "incidente PERIODONCIA Mayo 2026: las facturas reales del Histórico con códigos "
    "P* fueron cobradas como PERIODONCIA (Histórico_2M tiene $63.070 en mayo+junio "
    "con códigos P*). El xlsx de mayo/junio los mapea a PROTESIS porque Cecilia "
    "migró las prestaciones a códigos nuevos PE*, pero las facturas legacy siguen "
    "usando códigos P*. Ver: 06_docs/incidente-periodoncia-mayo-2026-06-14.md"
)

OVERRIDES: list[dict] = []
for mes in MESES_AFECTADOS:
    for cod in CODIGOS_PERIODONCIA_VIEJOS:
        OVERRIDES.append({
            "mes_arg": mes,
            "cod": cod,
            "categoria": "PERIODONCIA",
            "clase": None,
            "computaImporte": True,
            "computaCantidad": True,
            "motivo": MOTIVO_INCIDENTE,
        })


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
        print(f"❌ Snapshot está en v{snap.get('version', 1)}. Migrar primero con migrate-snapshot-mesaware.py", file=sys.stderr)
        return 1

    snap.setdefault("changelog", [])
    fecha_corrida = date.today().isoformat()

    aplicados = 0
    saltados = 0
    no_existen = 0
    for o in OVERRIDES:
        cod = o["cod"]
        mes = o["mes_arg"]
        if cod not in snap["codigos"]:
            print(f"⚠  {cod} no existe en snapshot — agregando nueva entrada con override")
            snap["codigos"][cod] = {
                "meses": {},
                "first_seen": fecha_corrida,
                "last_seen_xlsx": fecha_corrida,
            }
            no_existen += 1

        entrada_actual = snap["codigos"][cod].get("meses", {}).get(mes)
        entrada_nueva = {
            "categoria": o["categoria"],
            "clase": o["clase"],
            "computaImporte": o["computaImporte"],
            "computaCantidad": o["computaCantidad"],
        }

        if entrada_actual == entrada_nueva:
            saltados += 1
            continue

        # Logueo cada campo que cambia
        for campo, valor_nuevo in entrada_nueva.items():
            valor_anterior = (entrada_actual or {}).get(campo) if entrada_actual else None
            if valor_anterior != valor_nuevo:
                snap["changelog"].append({
                    "fecha_corrida": fecha_corrida,
                    "mes_arg": mes,
                    "cod": cod,
                    "campo": campo,
                    "antes": valor_anterior,
                    "ahora": valor_nuevo,
                    "tipo": "OVERRIDE_MANUAL",
                    "motivo": o["motivo"],
                })

        snap["codigos"][cod].setdefault("meses", {})[mes] = entrada_nueva
        aplicados += 1

    # Re-ordenar para diffs estables
    snap["codigos"] = {c: snap["codigos"][c] for c in sorted(snap["codigos"].keys())}
    for cod, info in snap["codigos"].items():
        if "meses" in info:
            info["meses"] = {m: info["meses"][m] for m in sorted(info["meses"].keys())}

    snap["last_updated"] = fecha_corrida

    with snapshot_path.open("w", encoding="utf-8") as f:
        json.dump(snap, f, indent=2, ensure_ascii=False)
        f.write("\n")

    sep = "═" * 70
    print(sep)
    print("OVERRIDES APLICADOS")
    print(sep)
    print(f"  Snapshot:           {snapshot_path}")
    print(f"  Overrides aplicados: {aplicados}")
    print(f"  Sin cambios (idempotencia): {saltados}")
    print(f"  Códigos creados (no existían): {no_existen}")
    print(f"  Total entradas changelog: {len(snap['changelog'])}")
    print()
    print(f"  Detalle aplicado:")
    print(f"    Códigos: {', '.join(CODIGOS_PERIODONCIA_VIEJOS)}")
    print(f"    Meses:   {', '.join(MESES_AFECTADOS)}")
    print(f"    Nueva categoría: PERIODONCIA (clase=null, computaImporte=true, computaCantidad=true)")
    print(sep)
    print("\nSiguiente: regenerar los 3 bloques JS con el snapshot ya corregido:")
    print("  python3 scripts/utilities/regen-bloques-js-from-snapshot.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
