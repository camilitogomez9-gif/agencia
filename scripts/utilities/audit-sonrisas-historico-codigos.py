#!/usr/bin/env python3
"""
audit-sonrisas-historico-codigos.py
Audita un export del Histórico de Sonrisas (CSV o JSON) y reporta cuántas
filas usaron cada código en cada mes, con foco especial en los códigos del
incidente PERIODONCIA Mayo 2026 (`P*` vs `PE*`).

Uso:
    python3 scripts/utilities/audit-sonrisas-historico-codigos.py <export> [--mes YYYY-MM] [--full]

Inputs aceptados:
    - CSV exportado del Data Table `SNR | Histórico Pagos` (columnas snake_case)
    - JSON exportado de la Data Table (lista de objetos con los mismos campos)
    - CSV/Excel del tab Histórico_2M del Google Sheet (columnas con nombres viejos)

Output:
    - Conteo por mes × código de los 9 códigos sospechosos
    - Conteo por mes × prefijo (P*, PE*)
    - Monto total agregado por mes × código
    - Sugerencia: cuántas filas mayo usan P* (deberían reclasificarse) vs PE*

Sin dependencias externas adicionales si es CSV simple; pandas para Excel.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


# Columnas esperadas en orden de prioridad
COLS_FECHA = ["Fecha_de_recepcion_del_pago", "Fecha de recepción del pago", "fecha", "Fecha"]
COLS_MES = ["Mes_de_recepcion_del_pago", "Mes de recepción del pago", "mes", "Mes"]
COLS_CODIGO = ["Codigo_Prestacion", "Código Prestación", "codigo", "Código"]
COLS_PAGADO = ["Pagado_Prestacion", "Pagado Prestación", "pagado", "Pagado"]

# Codigos sospechosos del incidente
CODIGOS_P_VIEJOS = {"P0000", "P1000", "P1001", "P1002", "P1003", "P1004", "P2000", "P2001", "P2002"}
CODIGOS_PE_NUEVOS = {"PE0000", "PE1000", "PE1001", "PE1002", "PE1003", "PE1004", "PE1005", "PE1006", "PE1007", "PE2000", "PE2001", "PE2002"}

MESES_ES = {
    "Enero": "01", "Febrero": "02", "Marzo": "03", "Abril": "04",
    "Mayo": "05", "Junio": "06", "Julio": "07", "Agosto": "08",
    "Septiembre": "09", "Octubre": "10", "Noviembre": "11", "Diciembre": "12",
}


def _first_present(row: dict, candidates: list[str]) -> str | None:
    for k in candidates:
        if k in row and row[k] not in (None, "", "nan"):
            return k
    return None


def _normalizar_mes(row: dict) -> str | None:
    """Devuelve YYYY-MM derivado del row. Prioriza Fecha; fallback a Mes (nombre español)."""
    k_fecha = _first_present(row, COLS_FECHA)
    if k_fecha:
        v = str(row[k_fecha])
        if len(v) >= 7 and v[4] == "-":
            return v[:7]
    k_mes = _first_present(row, COLS_MES)
    if k_mes:
        nombre = str(row[k_mes]).strip().capitalize()
        if nombre in MESES_ES:
            # asumimos año actual; útil solo si fecha no disponible
            from datetime import date
            return f"{date.today().year:04d}-{MESES_ES[nombre]}"
    return None


def _to_number(v) -> float:
    if v in (None, "", "nan"):
        return 0.0
    try:
        if isinstance(v, str):
            v = v.replace(",", ".").strip()
        return float(v)
    except (ValueError, TypeError):
        return 0.0


def cargar(path: Path) -> list[dict]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("r", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    if suffix == ".json":
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        if isinstance(data, list):
            return data
        raise ValueError(f"JSON con shape inesperado: {type(data).__name__}")
    if suffix in (".xlsx", ".xls"):
        try:
            import pandas as pd
        except ImportError:
            print("❌ Para leer xlsx necesito pandas: pip install pandas openpyxl", file=sys.stderr)
            sys.exit(2)
        df = pd.read_excel(path)
        return df.to_dict(orient="records")
    raise ValueError(f"Formato no soportado: {suffix}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("export", type=Path, help="CSV/JSON/XLSX del Histórico")
    parser.add_argument("--mes", default=None, help="Filtrar a YYYY-MM (ej. 2026-05)")
    parser.add_argument("--full", action="store_true", help="Mostrar TODOS los códigos, no solo los sospechosos")
    args = parser.parse_args()

    if not args.export.exists():
        print(f"❌ Archivo no encontrado: {args.export}", file=sys.stderr)
        return 1

    filas = cargar(args.export)
    print(f"✓ {len(filas)} fila(s) cargada(s) de {args.export}")

    # Normalizar y filtrar
    procesadas = []
    sin_mes = 0
    for f in filas:
        mes = _normalizar_mes(f)
        if not mes:
            sin_mes += 1
            continue
        if args.mes and mes != args.mes:
            continue
        k_cod = _first_present(f, COLS_CODIGO)
        k_pag = _first_present(f, COLS_PAGADO)
        cod = str(f[k_cod]).strip().upper() if k_cod else ""
        pagado = _to_number(f[k_pag]) if k_pag else 0.0
        if not cod:
            continue
        procesadas.append({"mes": mes, "codigo": cod, "pagado": pagado})

    if sin_mes:
        print(f"⚠  {sin_mes} fila(s) sin mes derivable (sin fecha + sin Mes_de_recepcion)")
    if args.mes:
        print(f"✓ Filtrado a mes {args.mes}: {len(procesadas)} fila(s)")
    print()

    # Conteo por mes × código
    por_mes_codigo: dict[tuple[str, str], dict] = defaultdict(lambda: {"filas": 0, "pagado_total": 0.0})
    for p in procesadas:
        k = (p["mes"], p["codigo"])
        por_mes_codigo[k]["filas"] += 1
        por_mes_codigo[k]["pagado_total"] += p["pagado"]

    # Reporte focalizado en códigos del incidente
    sep = "═" * 80
    print(sep)
    print("CÓDIGOS DEL INCIDENTE PERIODONCIA ↔ PROTESIS")
    print(sep)
    print(f"  {'MES':10s} {'CÓDIGO':10s} {'FILAS':>8s} {'PAGADO TOTAL':>16s}  GRUPO")
    print(sep)

    codigos_incidente = CODIGOS_P_VIEJOS | CODIGOS_PE_NUEVOS
    meses = sorted({p["mes"] for p in procesadas})
    for mes in meses:
        for cod in sorted(codigos_incidente):
            v = por_mes_codigo.get((mes, cod))
            if not v:
                continue
            grupo = "P* viejo (PROTESIS hoy)" if cod in CODIGOS_P_VIEJOS else "PE* nuevo (PERIODONCIA)"
            print(f"  {mes:10s} {cod:10s} {v['filas']:>8d} {v['pagado_total']:>16,.2f}  {grupo}")

    # Resumen agregado por mes × grupo
    print()
    print(sep)
    print("RESUMEN POR MES × GRUPO (P* vs PE*)")
    print(sep)
    print(f"  {'MES':10s} {'GRUPO':30s} {'FILAS':>8s} {'PAGADO TOTAL':>16s}")
    print(sep)
    for mes in meses:
        for grupo_name, grupo_set in [("P* viejos", CODIGOS_P_VIEJOS), ("PE* nuevos", CODIGOS_PE_NUEVOS)]:
            filas_g = sum(v["filas"] for (m, c), v in por_mes_codigo.items() if m == mes and c in grupo_set)
            pagado_g = sum(v["pagado_total"] for (m, c), v in por_mes_codigo.items() if m == mes and c in grupo_set)
            if filas_g > 0:
                print(f"  {mes:10s} {grupo_name:30s} {filas_g:>8d} {pagado_g:>16,.2f}")

    # Diagnóstico
    print()
    print(sep)
    print("DIAGNÓSTICO DEL INCIDENTE")
    print(sep)
    for mes in meses:
        p_filas = sum(v["filas"] for (m, c), v in por_mes_codigo.items() if m == mes and c in CODIGOS_P_VIEJOS)
        pe_filas = sum(v["filas"] for (m, c), v in por_mes_codigo.items() if m == mes and c in CODIGOS_PE_NUEVOS)
        p_pagado = sum(v["pagado_total"] for (m, c), v in por_mes_codigo.items() if m == mes and c in CODIGOS_P_VIEJOS)
        pe_pagado = sum(v["pagado_total"] for (m, c), v in por_mes_codigo.items() if m == mes and c in CODIGOS_PE_NUEVOS)
        total_filas = p_filas + pe_filas
        if total_filas == 0:
            continue
        print(f"  {mes}:")
        print(f"    Filas con códigos P* (clasificadas como PROTESIS):   {p_filas:>6} ({p_filas/total_filas*100:.1f}%)  ${p_pagado:,.2f}")
        print(f"    Filas con códigos PE* (clasificadas como PERIODONCIA): {pe_filas:>6} ({pe_filas/total_filas*100:.1f}%)  ${pe_pagado:,.2f}")
        if p_filas > 0:
            print(f"    ⚠  Si las prestaciones P* en {mes} eran realmente PERIODONCIA (no PROTESIS),")
            print(f"       hay ${p_pagado:,.2f} mal clasificados como PROTESIS.")
        else:
            print(f"    ✓ Todas las prestaciones del mes están en PE* (sistema migrado).")

    if args.full:
        print()
        print(sep)
        print("TODOS LOS CÓDIGOS POR MES (--full)")
        print(sep)
        print(f"  {'MES':10s} {'CÓDIGO':10s} {'FILAS':>8s} {'PAGADO TOTAL':>16s}")
        for (mes, cod) in sorted(por_mes_codigo.keys()):
            v = por_mes_codigo[(mes, cod)]
            print(f"  {mes:10s} {cod:10s} {v['filas']:>8d} {v['pagado_total']:>16,.2f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
