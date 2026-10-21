#!/usr/bin/env python3
"""
Reconciliación Mensual vs Semanal — Reporte Facturación Sonrisas.

Reproduce, sobre el CSV exportado de la pestaña "Ingreso datos" (Facturación), la
lógica EXACTA del workflow `sonrisas-reporte-facturacion-v3.3.json` para confirmar y
cuantificar el descuadre entre el total mensual y el total semanal de una celda
Sucursal × Clase (p. ej. Paso Molino × AJUSTE).

Causa que detecta:
  - El total MENSUAL se arma con el campo MANUAL "Mes de recepción del pago".
  - El total SEMANAL se calcula desde "Fecha de recepción del pago".
  - Las escrituras a Sheets usan operación `update`, que descarta en silencio toda
    fila cuya etiqueta (Sxx) no exista en la pestaña destino. Por eso una semana sin
    fila pre-creada —o una fecha mal formateada que produce Semana inválida— queda
    fuera del semanal pero sigue contando en el mensual.

A nivel de cómputo, Σ(por Mes) == Σ(por Semana) SIEMPRE (son dos particiones del
mismo conjunto). El gap aparece al ESCRIBIR. Por eso el script:
  1. Calcula el total verdadero (ambas particiones, deben coincidir).
  2. Lista filas con fecha no parseable (candidatas a Semana inválida → descarte).
  3. Desglosa por semana (S1..Sn) para ver qué semana falta en tu Sheet.
  4. Si pasás --semanas-en-sheet (o --tab-csv), simula el `update` y te dice el monto
     exacto que se pierde (los $14.910) y a qué semana pertenece.

Uso:
  python3 scripts/utilities/verify-sonrisas-reconciliacion.py \
      --csv ~/Downloads/ingreso-datos.csv \
      --sucursal "Paso Molino" --clase AJUSTE

  # Pinpoint exacto del gap, indicando qué etiquetas de semana existen en la pestaña:
  python3 scripts/utilities/verify-sonrisas-reconciliacion.py \
      --csv ~/Downloads/ingreso-datos.csv --sucursal "Paso Molino" --clase AJUSTE \
      --semanas-en-sheet "S2,S3,S4,S5,S6,S7,S8,S9,S10,S11,S12,S13,S14,S15,S16,S17,S18,S19,S20,S21"

Sin dependencias externas (solo stdlib).
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
import unicodedata
from collections import defaultdict
from datetime import date, datetime, timedelta

# --------------------------------------------------------------------------------------
# Clasificación de Clase (idéntica a Clase1 del workflow v3.3)
# --------------------------------------------------------------------------------------
CLASES_ORTODONCIA = {
    "AJUSTE": [
        "OA001", "OA002", "OA003", "OA004", "OA005", "OA006", "OA007", "OA008", "OA009",
        "OA010", "OA011", "OA012", "OA013", "OA014", "OA015", "OA016", "OA017", "OA018",
        "OA019", "OA020", "OA021", "OA022", "OA023", "OA024", "OA025", "OA026", "OA027",
        "OA028", "OA029", "OA030", "OA031", "OA032", "OA033", "OA034", "OA035", "OA036",
        "OA037", "OA038", "OA039", "OA040", "OA041", "OA042", "OA043", "OA044", "OA045",
        "OA046", "OA047", "OA048", "OA100", "OA101", "OA102", "OA103", "OA104", "OA105",
        "OA106", "OA107", "OA108", "OA109", "OA110", "OA111", "OA200", "OA201", "OA202",
        "OA203", "OA204", "OA205", "OA206", "OA207", "OA208", "OA300", "OA301", "OA302",
        "OA600", "OA601", "OA602", "OA603", "OA604", "OA605", "OA606", "OA607", "OA608",
        "OA609", "OA700", "OA701", "OA702", "OA703", "OA704", "OA800", "OA801", "OO001",
        "OO002", "OO003", "OO004", "OO005", "OO006", "OO100", "OO101", "OO102", "OO200",
    ],
    "RETIRO": [
        "OR001", "OR002", "OR003", "OR004", "OR005", "OR006", "OR007", "OR008", "OR009",
        "OR010", "OR011", "OR012", "OR020", "OR021", "OR022",
    ],
    "COMBO": [
        "OR013", "OR014", "OR016", "OR017", "OR018", "OR019", "OR100", "OR101", "OR102",
        "OR103", "OR104", "OR105", "OR106", "OR107", "OR108", "OR109", "OR110", "OR111",
        "OR112", "OR113", "OR114", "OR115", "OR116", "OR117", "OR118", "OR119", "OR120",
        "OR121", "OR122", "OR123", "OR124", "OR125", "OR126", "OR200", "OR201", "OR202",
    ],
}
_CODIGO_A_CLASE: dict[str, str] = {}
for _clase, _codigos in CLASES_ORTODONCIA.items():
    for _c in _codigos:
        _CODIGO_A_CLASE[_c] = _clase

MESES_ES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]


def clase_de(codigo: str) -> str:
    return _CODIGO_A_CLASE.get(codigo.strip().upper(), "OTRO")


# --------------------------------------------------------------------------------------
# Semana del año — port EXACTO de la fórmula Luxon del workflow (Lun=1..Dom=7)
# --------------------------------------------------------------------------------------
def luxon_weekday(d: date) -> int:
    """Luxon: Lunes=1 ... Domingo=7. Python date.weekday(): Lunes=0 ... Domingo=6."""
    return d.weekday() + 1


def semana_anio(d: date) -> str:
    jan1 = date(d.year, 1, 1)
    days_to_first_sunday = (7 - luxon_weekday(jan1)) % 7
    first_sunday = jan1 + timedelta(days=days_to_first_sunday)
    if d <= first_sunday:
        return "S1"
    first_monday = first_sunday + timedelta(days=1)
    diff_days = (d - first_monday).days
    week = 2 + (diff_days // 7)
    return f"S{week}"


def semana_mes(d: date) -> str:
    month_start = date(d.year, d.month, 1)
    days_to_first_sunday = (7 - luxon_weekday(month_start)) % 7
    first_sunday = month_start + timedelta(days=days_to_first_sunday)
    if d <= first_sunday:
        return "Semana 1"
    first_monday = first_sunday + timedelta(days=1)
    diff_days = (d - first_monday).days
    week = 2 + (diff_days // 7)
    return f"Semana {week}"


# --------------------------------------------------------------------------------------
# Parseo de fecha
# --------------------------------------------------------------------------------------
def parse_fecha_estricta(raw: str):
    """Replica DateTime.fromFormat(raw, 'yyyy-MM-dd'). None si no matchea EXACTO."""
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def parse_fecha_robusta(raw: str):
    """
    Parser tolerante (lo que debería usar el workflow corregido). Devuelve date o None.
    Acepta: yyyy-MM-dd, ISO con hora, dd/MM/yyyy, d/M/yyyy, dd-MM-yyyy y serial de Sheets.
    """
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None

    # Serial de Google Sheets / Excel (días desde 1899-12-30)
    try:
        if s.replace(".", "", 1).isdigit():
            serial = float(s)
            if 1 <= serial <= 80000:  # rango razonable de fechas
                return (date(1899, 12, 30) + timedelta(days=int(serial)))
    except ValueError:
        pass

    fmts = (
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y",
        "%d/%m/%y",
        "%m/%d/%Y",  # último: ambiguo, se intenta al final
        "%d-%m-%Y",
    )
    for f in fmts:
        try:
            return datetime.strptime(s, f).date()
        except ValueError:
            continue
    # ISO genérico
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def parse_monto(raw: str) -> float:
    """Convierte un importe de Sheets a float. Tolera $, espacios y separadores."""
    if raw is None:
        return 0.0
    s = str(raw).strip()
    if not s:
        return 0.0
    s = s.replace("$", "").replace(" ", "").replace(" ", "")
    if not s:
        return 0.0
    # Si hay coma y punto, asumir formato es-UY: punto miles, coma decimal.
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        # Solo coma: decidir si es decimal (1 sola coma, <=2 dígitos a la derecha)
        ent, _, dec = s.partition(",")
        s = f"{ent}.{dec}" if len(dec) in (1, 2) else s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return 0.0


# --------------------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------------------
def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", str(s or ""))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.strip().lower()


def find_col(fieldnames, *candidates):
    """Encuentra una columna por nombre normalizado (tolera acentos/espacios)."""
    nmap = {norm(f): f for f in fieldnames}
    for cand in candidates:
        if norm(cand) in nmap:
            return nmap[norm(cand)]
    # match parcial
    for cand in candidates:
        for nf, orig in nmap.items():
            if norm(cand) in nf:
                return orig
    return None


def fmt(n: float) -> str:
    return f"$ {n:,.0f}".replace(",", ".")


def semana_key(label: str):
    """Orden natural de etiquetas Sxx."""
    try:
        return int(label[1:]) if label.startswith("S") and label[1:].isdigit() else 9999
    except ValueError:
        return 9999


# --------------------------------------------------------------------------------------
# Núcleo
# --------------------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="Reconciliación Mensual vs Semanal Sonrisas")
    ap.add_argument("--csv", required=True, help="CSV exportado de 'Ingreso datos' (Facturación)")
    ap.add_argument("--sucursal", default="Paso Molino", help="Filtro de sucursal (substring)")
    ap.add_argument("--clase", default="AJUSTE", help="Clase: AJUSTE/RETIRO/COMBO/OTRO/TODAS")
    ap.add_argument("--semanas-en-sheet", default="",
                    help="Etiquetas Sxx presentes en la pestaña, separadas por coma (simula el update).")
    ap.add_argument("--delimiter", default="", help="Forzar delimitador del CSV (auto si vacío)")
    args = ap.parse_args()

    try:
        with open(args.csv, newline="", encoding="utf-8-sig") as fh:
            sample = fh.read(4096)
            fh.seek(0)
            if args.delimiter:
                dialect = csv.excel
                dialect.delimiter = args.delimiter
            else:
                try:
                    dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
                except csv.Error:
                    dialect = csv.excel
            reader = csv.DictReader(fh, dialect=dialect)
            rows = list(reader)
            fields = reader.fieldnames or []
    except FileNotFoundError:
        print(f"ERROR: no encontré el archivo {args.csv}", file=sys.stderr)
        return 2

    col_fecha = find_col(fields, "Fecha de recepción del pago", "Fecha de recepcion del pago", "Fecha")
    col_mes = find_col(fields, "Mes de recepción del pago", "Mes de recepcion del pago", "Mes")
    col_codigo = find_col(fields, "Código Prestación", "Codigo Prestacion", "Código", "Codigo")
    col_pagado = find_col(fields, "Pagado Prestación", "Pagado Prestacion", "Pagado")
    col_suc = find_col(fields, "Nombre Sucursal", "Sucursal")

    faltan = [n for n, c in [
        ("Fecha", col_fecha), ("Mes", col_mes), ("Código", col_codigo),
        ("Pagado", col_pagado), ("Sucursal", col_suc),
    ] if c is None]
    if faltan:
        print(f"ERROR: no pude mapear columnas: {', '.join(faltan)}", file=sys.stderr)
        print(f"Columnas detectadas: {fields}", file=sys.stderr)
        return 2

    suc_filtro = norm(args.sucursal)
    clase_filtro = args.clase.strip().upper()

    por_mes: dict[str, float] = defaultdict(float)
    por_semana: dict[str, float] = defaultdict(float)
    semana_to_meses: dict[str, set] = defaultdict(set)
    filas_fecha_invalida = []  # (idx, raw_fecha, mes_manual, monto)
    filas_mes_vacio = []
    total_filas = 0
    total_verdadero = 0.0

    for idx, r in enumerate(rows, start=2):  # +2: fila 1 = header en el Sheet
        suc = r.get(col_suc, "")
        if suc_filtro and suc_filtro not in norm(suc):
            continue
        codigo = str(r.get(col_codigo, "") or "").strip().upper()
        clase = clase_de(codigo)
        if clase_filtro != "TODAS" and clase != clase_filtro:
            continue

        monto = parse_monto(r.get(col_pagado, ""))
        if monto == 0.0 and not codigo:
            continue  # fila vacía real

        total_filas += 1
        total_verdadero += monto

        # --- Lado MENSUAL (campo manual, como hoy) ---
        mes_manual = str(r.get(col_mes, "") or "").strip()
        if mes_manual:
            por_mes[mes_manual] += monto
        else:
            filas_mes_vacio.append((idx, codigo, monto))

        # --- Lado SEMANAL (calculado estricto yyyy-MM-dd, como hoy) ---
        raw_fecha = r.get(col_fecha, "")
        d = parse_fecha_estricta(raw_fecha)
        if d is None:
            filas_fecha_invalida.append((idx, raw_fecha, mes_manual, monto))
            por_semana["S_INVALIDA"] += monto
        else:
            sk = semana_anio(d)
            por_semana[sk] += monto
            semana_to_meses[sk].add(MESES_ES[d.month - 1])

    # ----------------------------------------------------------------------------------
    print("=" * 78)
    print(f"  RECONCILIACIÓN — Sucursal '{args.sucursal}' × Clase '{args.clase}'")
    print(f"  CSV: {args.csv}")
    print("=" * 78)
    print(f"Filas consideradas: {total_filas}")
    print(f"Total verdadero (suma de Pagado Prestación): {fmt(total_verdadero)}")
    print()

    suma_mes = sum(por_mes.values())
    suma_sem_compute = sum(por_semana.values())
    print(f"Σ por Mes  (todas las etiquetas): {fmt(suma_mes)}")
    print(f"Σ por Semana (incl. inválidas):   {fmt(suma_sem_compute)}")
    if abs(suma_mes - suma_sem_compute) < 0.5 and abs(suma_mes - total_verdadero) < 0.5:
        print("  → A nivel CÓMPUTO ambas particiones coinciden (correcto). El gap nace al ESCRIBIR.")
    print()

    # --- Desglose mensual ---
    print("-" * 78)
    print("BLOQUE MENSUAL (campo manual 'Mes de recepción del pago')")
    for mes, v in sorted(por_mes.items(), key=lambda kv: MESES_ES.index(kv[0]) if kv[0] in MESES_ES else 99):
        print(f"  {mes:<14} {fmt(v):>16}")
    print()

    # --- Desglose semanal ---
    print("-" * 78)
    print("BLOQUE SEMANAL (calculado de 'Fecha de recepción del pago')")
    for sk in sorted(por_semana.keys(), key=semana_key):
        meses = ",".join(sorted(semana_to_meses.get(sk, []), key=lambda m: MESES_ES.index(m) if m in MESES_ES else 99))
        marca = "  <-- SEMANA INVÁLIDA (fecha no parseable)" if sk == "S_INVALIDA" else ""
        print(f"  {sk:<14} {fmt(por_semana[sk]):>16}   [{meses}]{marca}")
    print()

    # --- Filas problemáticas ---
    if filas_fecha_invalida:
        total_inv = sum(m for *_, m in filas_fecha_invalida)
        print("-" * 78)
        print(f"⚠ FILAS CON FECHA NO PARSEABLE (hoy se descartan del semanal): {len(filas_fecha_invalida)}  =  {fmt(total_inv)}")
        for idx, raw, mes, monto in filas_fecha_invalida[:40]:
            print(f"    fila {idx}: fecha='{raw}'  mes_manual='{mes}'  pagado={fmt(monto)}")
        if len(filas_fecha_invalida) > 40:
            print(f"    ... (+{len(filas_fecha_invalida) - 40} más)")
        print()
    if filas_mes_vacio:
        total_mv = sum(m for *_, m in filas_mes_vacio)
        print(f"⚠ FILAS CON 'Mes' MANUAL VACÍO (se descartarían del mensual): {len(filas_mes_vacio)} = {fmt(total_mv)}")
        print()

    # --- Simulación del write `update` (pinpoint del gap) ---
    if args.semanas_en_sheet.strip():
        presentes = {x.strip() for x in args.semanas_en_sheet.split(",") if x.strip()}
        print("=" * 78)
        print("SIMULACIÓN DEL `update` — qué se pierde porque la fila de semana no existe")
        print("=" * 78)
        total_visible = 0.0
        perdido = 0.0
        for sk, v in sorted(por_semana.items(), key=lambda kv: semana_key(kv[0])):
            if sk in presentes:
                total_visible += v
            else:
                perdido += v
                meses = ",".join(sorted(semana_to_meses.get(sk, [])))
                print(f"  DESCARTADA  {sk:<12} {fmt(v):>16}   [{meses or 'inválida'}]")
        print()
        print(f"  Total semanal VISIBLE en el Sheet : {fmt(total_visible)}")
        print(f"  Total mensual (verdadero)         : {fmt(suma_mes)}")
        print(f"  GAP (lo que el `update` descartó)  : {fmt(suma_mes - total_visible)}")
        print()

    # --- Verificación con parser robusto (lo que daría el fix) ---
    invalidas_robusto = 0
    for idx, raw, mes, monto in filas_fecha_invalida:
        if parse_fecha_robusta(raw) is not None:
            invalidas_robusto += 1
    if filas_fecha_invalida:
        print("-" * 78)
        recuperables = invalidas_robusto
        print(f"Con el parser ROBUSTO del fix: {recuperables}/{len(filas_fecha_invalida)} "
              f"de esas fechas se parsean correctamente (dejarían de descartarse).")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
