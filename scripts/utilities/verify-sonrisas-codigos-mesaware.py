#!/usr/bin/env python3
"""
verify-sonrisas-codigos-mesaware.py
Replica en Python la lógica de lookup mes-aware embebida en los nodos JS
(Filtro/Categoria/Clase generados por update-sonrisas-nodes.py) y la corre
contra un set de casos golden para asegurar que la clasificación produce los
resultados esperados.

Uso:
    # Casos golden built-in (snapshot real del workspace)
    python3 scripts/utilities/verify-sonrisas-codigos-mesaware.py

    # Casos custom desde JSON
    python3 scripts/utilities/verify-sonrisas-codigos-mesaware.py --casos casos.json

    # Otro snapshot
    python3 scripts/utilities/verify-sonrisas-codigos-mesaware.py --snapshot otro.json

Formato JSON de casos custom:
[
  {
    "id": "G1",
    "descripcion": "Sin cambios entre meses, fila de mayo",
    "codigo": "00001",
    "fecha_iso": "2026-05-10",
    "esperado": {
      "categoria": "GENERAL",
      "clase": null,
      "fallback": null,
      "error": false
    }
  }
]

Salida: tabla PASS/FAIL + resumen agregado. Exit code 0 si todo PASS, 1 si hay FAIL.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SNAPSHOT_REL = Path("clients") / "SNR_Sonrisas" / "_snapshots" / "codigos-historico.json"


def workspace_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


# ═══ LÓGICA MES-AWARE (mirror del JS embebido) ═══════════════════════════════

def materializar_tabla_desde_snapshot(snapshot: dict) -> tuple[dict[str, dict[str, dict]], list[str]]:
    """Reproduce TABLA_MES_AWARE + MESES_ORDENADOS tal como los emitiría el script
    para los nodos n8n. Aplica solo lo que está EN el snapshot (sin xlsx encima)."""
    tabla: dict[str, dict[str, dict]] = {}
    for cod, info in snapshot.get("codigos", {}).items():
        for m, entrada in info.get("meses", {}).items():
            tabla.setdefault(m, {})[cod] = {
                "categoria": entrada.get("categoria"),
                "clase": entrada.get("clase"),
                "computaImporte": entrada.get("computaImporte", True),
                "computaCantidad": entrada.get("computaCantidad", True),
            }
    meses_ordenados = sorted(tabla.keys())
    return tabla, meses_ordenados


def lookup_mes_aware(
    tabla: dict[str, dict[str, dict]],
    meses_ordenados: list[str],
    codigo: str,
    mes_key: str | None,
) -> tuple[dict | None, str | None]:
    """Devuelve (entrada, fallback). fallback ∈ {None, "atras:YYYY-MM", "adelante:YYYY-MM"}.
    None si el código no existe en ningún mes."""
    if not codigo or not mes_key:
        return None, None
    # Match directo
    if mes_key in tabla and codigo in tabla[mes_key]:
        return tabla[mes_key][codigo], None
    # Hacia atrás: mes más reciente <= mes_key
    for m in reversed(meses_ordenados):
        if m > mes_key:
            continue
        if codigo in tabla.get(m, {}):
            return tabla[m][codigo], f"atras:{m}"
    # Hacia adelante: mes más antiguo > mes_key
    for m in meses_ordenados:
        if m <= mes_key:
            continue
        if codigo in tabla.get(m, {}):
            return tabla[m][codigo], f"adelante:{m}"
    return None, None


def derivar_mes_key(fecha_iso: str | None) -> str | None:
    if not fecha_iso:
        return None
    if len(fecha_iso) >= 7 and fecha_iso[4] == "-":
        return fecha_iso[:7]
    return None


def clasificar_fila(
    tabla: dict[str, dict[str, dict]],
    meses_ordenados: list[str],
    codigo: str,
    fecha_iso: str | None,
) -> dict:
    """Output equivalente a lo que producirían los nodos Filtro+Categoria+Clase
    combinados para una sola fila:
        {
          error: bool,             # True si código desconocido o fecha inválida
          categoria: str | None,
          clase: str | None,        # None si no-ortodoncia (se descartaría en Clase)
          computaImporte: bool,
          computaCantidad: bool,
          fallback: str | None,
        }
    """
    mes_key = derivar_mes_key(fecha_iso)
    if mes_key is None:
        return {
            "error": True,
            "error_motivo": "fecha_invalida",
            "categoria": None,
            "clase": None,
            "computaImporte": None,
            "computaCantidad": None,
            "fallback": None,
        }
    entrada, fallback = lookup_mes_aware(tabla, meses_ordenados, codigo, mes_key)
    if entrada is None:
        return {
            "error": True,
            "error_motivo": "codigo_desconocido",
            "categoria": None,
            "clase": None,
            "computaImporte": None,
            "computaCantidad": None,
            "fallback": None,
        }
    return {
        "error": False,
        "error_motivo": None,
        "categoria": entrada.get("categoria"),
        "clase": entrada.get("clase"),
        "computaImporte": bool(entrada.get("computaImporte", True)),
        "computaCantidad": bool(entrada.get("computaCantidad", True)),
        "fallback": fallback,
    }


# ═══ CASOS GOLDEN (built-in) ═════════════════════════════════════════════════

CASOS_GOLDEN_BUILTIN = [
    {
        "id": "G1",
        "descripcion": "Sin cambios entre meses, fila de mayo — código presente en mayo",
        "codigo": "EJEMPLO_MAYO_GENERAL",
        "fecha_iso": "2026-05-10",
        "esperado": {"categoria": "GENERAL", "clase": None, "fallback": None, "error": False},
        "skip_si_no_existe": True,
    },
    {
        "id": "G2",
        "descripcion": "Categoria distinta entre mayo y junio, fila de mayo → usa MAYO",
        "codigo": "EJEMPLO_CAMBIO_CAT",
        "fecha_iso": "2026-05-15",
        "esperado": {"categoria": "CAT_MAYO", "fallback": None, "error": False},
        "skip_si_no_existe": True,
    },
    {
        "id": "G3",
        "descripcion": "Categoria distinta entre mayo y junio, fila de junio → usa JUNIO",
        "codigo": "EJEMPLO_CAMBIO_CAT",
        "fecha_iso": "2026-06-15",
        "esperado": {"categoria": "CAT_JUNIO", "fallback": None, "error": False},
        "skip_si_no_existe": True,
    },
    {
        "id": "G4",
        "descripcion": "Código existe solo en mayo (retirado en junio), fila de mayo → directo",
        "codigo": "EJEMPLO_RETIRADO",
        "fecha_iso": "2026-05-15",
        "esperado": {"fallback": None, "error": False},
        "skip_si_no_existe": True,
    },
    {
        "id": "G5",
        "descripcion": "Código retirado (solo en mayo), fila de junio → fallback atras:2026-05",
        "codigo": "EJEMPLO_RETIRADO",
        "fecha_iso": "2026-06-15",
        "esperado": {"fallback": "atras:2026-05", "error": False},
        "skip_si_no_existe": True,
    },
    {
        "id": "G6",
        "descripcion": "Código nuevo en junio, fila de junio → directo",
        "codigo": "EJEMPLO_NUEVO_JUNIO",
        "fecha_iso": "2026-06-10",
        "esperado": {"fallback": None, "error": False},
        "skip_si_no_existe": True,
    },
    {
        "id": "G7",
        "descripcion": "Código nuevo en junio, fila de mayo (retroactiva) → fallback adelante:2026-06",
        "codigo": "EJEMPLO_NUEVO_JUNIO",
        "fecha_iso": "2026-05-10",
        "esperado": {"fallback": "adelante:2026-06", "error": False},
        "skip_si_no_existe": True,
    },
    {
        "id": "G8",
        "descripcion": "Código que nunca existió → error codigo_desconocido",
        "codigo": "ZZZZZ_NO_EXISTE",
        "fecha_iso": "2026-05-10",
        "esperado": {"error": True, "error_motivo": "codigo_desconocido"},
    },
    {
        "id": "G9",
        "descripcion": "Fila sin _fechaISO → error fecha_invalida",
        "codigo": "00001",
        "fecha_iso": None,
        "esperado": {"error": True, "error_motivo": "fecha_invalida"},
    },
    {
        "id": "G10",
        "descripcion": "Caso PERIODONCIA Mayo (real) — código de PERIODONCIA en fila de mayo no debe dar OTRO",
        "codigo": "EJEMPLO_PERIODONCIA_MAYO",
        "fecha_iso": "2026-05-15",
        "esperado": {"categoria": "PERIODONCIA", "error": False},
        "skip_si_no_existe": True,
    },
]


def _matchea_esperado(resultado: dict, esperado: dict) -> tuple[bool, list[str]]:
    """Compara solo los campos del 'esperado'. Devuelve (pass, motivos_fail)."""
    motivos: list[str] = []
    for campo, valor_esperado in esperado.items():
        if campo not in resultado:
            motivos.append(f"campo '{campo}' no en resultado")
            continue
        if resultado[campo] != valor_esperado:
            motivos.append(f"{campo}: esperado={valor_esperado!r} obtenido={resultado[campo]!r}")
    return (len(motivos) == 0, motivos)


# ═══ MAIN ════════════════════════════════════════════════════════════════════

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, default=None,
                        help="path al snapshot.json (default: workspace SNR)")
    parser.add_argument("--casos", type=Path, default=None,
                        help="path a casos.json (default: built-in)")
    args = parser.parse_args()

    snapshot_path = args.snapshot or (workspace_root() / SNAPSHOT_REL)
    if not snapshot_path.exists():
        print(f"❌ Snapshot no encontrado: {snapshot_path}", file=sys.stderr)
        return 1
    with snapshot_path.open("r", encoding="utf-8") as f:
        snapshot = json.load(f)

    version = snapshot.get("version", 1)
    if version < 2:
        print(
            f"❌ Snapshot está en v{version}. Este verifier requiere v2 (mes-aware).\n"
            f"   Corré primero: python3 scripts/utilities/migrate-snapshot-mesaware.py",
            file=sys.stderr,
        )
        return 1

    tabla, meses_ordenados = materializar_tabla_desde_snapshot(snapshot)

    if args.casos:
        with args.casos.open("r", encoding="utf-8") as f:
            casos = json.load(f)
    else:
        casos = CASOS_GOLDEN_BUILTIN
        # Filtrar built-in: los casos con código de placeholder se SKIP si no
        # existe en el snapshot real (suelen referir a datos del bootstrap)
        casos = [c for c in casos if not c.get("skip_si_no_existe")
                 or c["codigo"] in {cod for m in tabla.values() for cod in m}
                 or c["codigo"].startswith("ZZZZZ")
                 or c["codigo"].startswith("00")]

    if not casos:
        print("⚠  No hay casos para correr. El snapshot built-in usa códigos placeholder")
        print("   (EJEMPLO_*) que no existen en el snapshot real. Pasale casos custom con --casos.")
        return 0

    print(f"\n═══ verify-sonrisas-codigos-mesaware ═══")
    print(f"  snapshot:        {snapshot_path}")
    print(f"  version:         {version}")
    print(f"  meses:           {meses_ordenados}")
    print(f"  códigos totales: {len({c for m in tabla.values() for c in m})}")
    print(f"  casos:           {len(casos)}")
    print()

    fails = 0
    for caso in casos:
        resultado = clasificar_fila(tabla, meses_ordenados, caso["codigo"], caso.get("fecha_iso"))
        ok, motivos = _matchea_esperado(resultado, caso["esperado"])
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"  {status}  {caso['id']:4s} {caso['descripcion']}")
        if not ok:
            fails += 1
            for m in motivos:
                print(f"           → {m}")
            print(f"           resultado: {resultado}")

    print()
    print(f"  {len(casos) - fails}/{len(casos)} PASS, {fails} FAIL")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
