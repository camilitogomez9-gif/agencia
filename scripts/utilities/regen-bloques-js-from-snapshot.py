#!/usr/bin/env python3
"""
regen-bloques-js-from-snapshot.py
Re-emite los 3 bloques JS (Filtro / Categoria / Clase) directamente desde el
snapshot v2 mes-aware, sin requerir un xlsx ni modificar el snapshot.

Útil después de:
- correr `override-snapshot-codigos.py` (overrides manuales)
- editar el snapshot a mano

Uso:
    python3 scripts/utilities/regen-bloques-js-from-snapshot.py [--out <directorio>]

Default: imprime a stdout. Con --out, escribe filtro.js / categoria.js / clase.js
en el directorio dado.

NO toca update-sonrisas-nodes.py ni el snapshot. Importa los generadores del
script principal para no duplicar lógica.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


SNAPSHOT_REL = Path("clients") / "SNR_Sonrisas" / "_snapshots" / "codigos-historico.json"


def workspace_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def importar_update_script():
    """Importa update-sonrisas-nodes.py como módulo (tiene guion en el nombre,
    no se puede `import` directo). Usamos importlib."""
    path = workspace_root() / "scripts" / "utilities" / "update-sonrisas-nodes.py"
    spec = importlib.util.spec_from_file_location("update_sonrisas", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["update_sonrisas"] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=None,
                        help="Directorio donde escribir filtro.js / categoria.js / clase.js")
    parser.add_argument("--snapshot", type=Path, default=None,
                        help="Path al snapshot (default: workspace SNR)")
    args = parser.parse_args()

    snapshot_path = args.snapshot or (workspace_root() / SNAPSHOT_REL)
    with snapshot_path.open("r", encoding="utf-8") as f:
        snapshot = json.load(f)

    version = snapshot.get("version", 1)
    if version < 2:
        print(f"❌ Snapshot está en v{version}. Migrar primero.", file=sys.stderr)
        return 1

    upd = importar_update_script()

    # Construir tabla_por_mes directamente desde el snapshot (sin xlsx)
    tabla_por_mes: dict[str, dict[str, dict]] = {}
    for cod, info in snapshot.get("codigos", {}).items():
        for m, entrada in info.get("meses", {}).items():
            tabla_por_mes.setdefault(m, {})[cod] = {
                "categoria": entrada.get("categoria"),
                "clase": entrada.get("clase"),
                "computaImporte": entrada.get("computaImporte", True),
                "computaCantidad": entrada.get("computaCantidad", True),
            }
    meses_ordenados = sorted(tabla_por_mes.keys())

    js_filtro = upd.generar_filtro_mesaware(tabla_por_mes, meses_ordenados)
    js_categoria = upd.generar_categoria_mesaware(tabla_por_mes, meses_ordenados)
    js_clase = upd.generar_clase_mesaware(tabla_por_mes, meses_ordenados)

    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "filtro.js").write_text(js_filtro + "\n", encoding="utf-8")
        (args.out / "categoria.js").write_text(js_categoria + "\n", encoding="utf-8")
        (args.out / "clase.js").write_text(js_clase + "\n", encoding="utf-8")
        print(f"✓ Escritos en {args.out}:")
        for f in ("filtro.js", "categoria.js", "clase.js"):
            p = args.out / f
            print(f"    {f}  ({p.stat().st_size:,} bytes)")
    else:
        sep = "─" * 70
        print(f"\n{sep}")
        print("NODO: Filtro  (pegar en Filtro1 del Reporte + Filtro y Filtro3 del Correo)")
        print(sep)
        print(js_filtro)
        print(f"\n{sep}")
        print("NODO: Categoria  (pegar en Categoria del Reporte + Categoria y Categoria1 del Correo)")
        print(sep)
        print(js_categoria)
        print(f"\n{sep}")
        print("NODO: Clase  (pegar en Clase1 del Reporte + Clase y Clase1 del Correo)")
        print(sep)
        print(js_clase)

    # Resumen
    n_codigos_union = len({c for m in tabla_por_mes.values() for c in m})
    print()
    print(f"  Meses en snapshot: {meses_ordenados}")
    print(f"  Códigos totales (unión de meses): {n_codigos_union}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
