#!/usr/bin/env python3
"""
migrate-snapshot-mesaware.py
One-shot que migra el snapshot `codigos-historico.json` de v1 (flat) a v2
(mes-aware: `codigos[X].meses[YYYY-MM]`).

Uso:
    python3 scripts/utilities/migrate-snapshot-mesaware.py

Comportamiento:
- Lee el snapshot actual en `clients/SNR_Sonrisas/_snapshots/codigos-historico.json`.
- Si version >= 2: imprime "ya está migrado" y sale sin tocar nada (idempotente).
- Si version == 1:
    1. Crea backup en `codigos-historico.v1-backup.json` (si no existe ya).
    2. Para cada código, crea una entrada `meses[YYYY-MM]` donde YYYY-MM se deriva
       del `last_seen_xlsx` del v1 (o, si está ausente, de `last_updated` global).
       Esa entrada copia `categoria` y `clase`; `computaImporte` y `computaCantidad`
       se asumen `true` (política conservadora — el snapshot v1 no las persistía y la
       lógica del nodo Filtro/Clase tampoco las miraba para códigos legacy).
    3. Conserva `first_seen` y `last_seen_xlsx` top-level del código (auditoría).
    4. Sube `version` a 2, agrega `ventana_meses: 6` y `changelog: []`.
    5. Escribe el v2 en el mismo path (sustituye al v1).

El backup permite rollback inmediato: borrar el v2 y renombrar el backup.

NO toca ningún workflow ni nodo de n8n. Esto es solo el primer paso del bootstrap;
después corres `update-sonrisas-nodes.py --mes YYYY-MM` con cada xlsx histórico.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


SNAPSHOT_REL_PATH = Path("clients") / "SNR_Sonrisas" / "_snapshots" / "codigos-historico.json"
BACKUP_NAME = "codigos-historico.v1-backup.json"


def workspace_root() -> Path:
    """`<workspace>/scripts/utilities/<este script>` → workspace = parent.parent.parent."""
    return Path(__file__).resolve().parent.parent.parent


def derivar_yyyymm(iso_date: str | None, fallback: str | None) -> str:
    """Devuelve los primeros 7 chars (YYYY-MM) de la mejor fuente disponible.
    Si ninguna está disponible y parseable, lanza ValueError."""
    for candidate in (iso_date, fallback):
        if candidate and len(candidate) >= 7 and candidate[4] == "-":
            return candidate[:7]
    raise ValueError(f"no se pudo derivar YYYY-MM de iso_date={iso_date!r} fallback={fallback!r}")


def migrar_v1_a_v2(snapshot_v1: dict) -> dict:
    """Construye el snapshot v2 a partir de un v1 flat. Idempotente: si ya es v2, lo devuelve igual."""
    version_actual = snapshot_v1.get("version", 1)
    if version_actual >= 2:
        return snapshot_v1

    last_updated_global = snapshot_v1.get("last_updated")
    codigos_v2: dict[str, dict] = {}

    for cod, info in snapshot_v1.get("codigos", {}).items():
        first_seen = info.get("first_seen")
        last_seen_xlsx = info.get("last_seen_xlsx")
        yyyymm = derivar_yyyymm(last_seen_xlsx, last_updated_global)

        entrada_mes = {
            "categoria": info.get("categoria"),
            "clase": info.get("clase"),  # puede ser None (no-ortodoncia)
            "computaImporte": True,       # default conservador (v1 no persistía estos flags)
            "computaCantidad": True,
        }

        codigos_v2[cod] = {
            "meses": {yyyymm: entrada_mes},
            "first_seen": first_seen,
            "last_seen_xlsx": last_seen_xlsx,
        }

    return {
        "version": 2,
        "last_updated": last_updated_global,
        "ventana_meses": 6,
        "comment": (
            "Snapshot mes-aware de códigos. Cada código guarda sus clasificaciones "
            "por mes (YYYY-MM) para que el lookup de Filtro/Categoria/Clase use los "
            "códigos vigentes en el mes de recepción del pago. Pruning automático a "
            "6 meses. NO editar a mano salvo conflictos."
        ),
        "codigos": dict(sorted(codigos_v2.items())),
        "changelog": [],
    }


def main() -> int:
    root = workspace_root()
    snapshot_path = root / SNAPSHOT_REL_PATH
    backup_path = snapshot_path.parent / BACKUP_NAME

    if not snapshot_path.exists():
        print(f"❌ Snapshot no encontrado en {snapshot_path}", file=sys.stderr)
        return 1

    with snapshot_path.open("r", encoding="utf-8") as f:
        snapshot = json.load(f)

    version = snapshot.get("version", 1)
    if version >= 2:
        print(f"✓ Snapshot ya está en v{version}. Nada que migrar.")
        return 0

    # Backup (no sobrescribir si ya existe — preserva el primer backup confirmado)
    if backup_path.exists():
        print(f"ℹ  Backup ya existe en {backup_path} (no se sobreescribe).")
    else:
        shutil.copy2(snapshot_path, backup_path)
        print(f"✓ Backup v1 creado: {backup_path}")

    # Migrar
    try:
        snapshot_v2 = migrar_v1_a_v2(snapshot)
    except ValueError as e:
        print(f"❌ Error migrando: {e}", file=sys.stderr)
        return 1

    # Escribir v2 (mismo path)
    with snapshot_path.open("w", encoding="utf-8") as f:
        json.dump(snapshot_v2, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # Resumen
    n_codigos = len(snapshot_v2["codigos"])
    meses_vistos: set[str] = set()
    for info in snapshot_v2["codigos"].values():
        meses_vistos.update(info.get("meses", {}).keys())

    sep = "─" * 70
    print(sep)
    print("MIGRACIÓN v1 → v2 COMPLETA")
    print(sep)
    print(f"  Path:              {snapshot_path}")
    print(f"  Backup v1:         {backup_path}")
    print(f"  Códigos migrados:  {n_codigos}")
    print(f"  Meses generados:   {sorted(meses_vistos)}")
    print(f"  Ventana pruning:   {snapshot_v2['ventana_meses']} meses")
    print(sep)
    print("Siguientes pasos del bootstrap:")
    print(f"  1) update-sonrisas-nodes.py --mes 2026-05 '<xlsx_mayo>'")
    print(f"  2) update-sonrisas-nodes.py --mes 2026-06 '<xlsx_junio>'")
    print(f"  3) inspeccionar bloque 'REVISIÓN REQUERIDA' al final de cada corrida")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
