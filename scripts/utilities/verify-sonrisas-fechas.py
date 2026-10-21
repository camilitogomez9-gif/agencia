#!/usr/bin/env python3
"""
Verificación de la regla de fechas 'Mes objetivo' para los flujos de Facturación Sonrisas.

Simula, sábado por sábado, la regla de carga (reemplazar todo) + el cierre mensual
'al cerrar la semana borde', y prueba que:

  1) Cada mes se cierra (finaliza/emite) EXACTAMENTE una vez.
  2) Al cierre, la planilla contiene TODOS los días hábiles (Lun-Sáb) del mes.
  3) Ningún día hábil del año queda sin procesarse (cobertura total, sin huecos).
  4) La rama Semana_mes, filtrada a 'mes objetivo', nunca mezcla dos meses (sin colisión "Semana N").
  5) La semana absoluta (incl. la que cruza el borde) está completa al emitirse.

Además cuantifica los días que la lógica VIEJA (mensual el último día del mes) perdía.

Modelo: clínica cerrada los domingos (sin datos). Días hábiles = Lun..Sáb.
"""
from datetime import date, timedelta

# ---------- utilidades de calendario (weekday(): Lun=0..Dom=6; Sáb=5) ----------
def first_sat_ge(d: date) -> date:
    """Primer sábado en o después de d."""
    return d + timedelta(days=(5 - d.weekday()) % 7)

def last_sat_le(d: date) -> date:
    """Último sábado en o antes de d."""
    return d - timedelta(days=(d.weekday() - 5) % 7)

def month_start(d: date) -> date:
    return d.replace(day=1)

def month_end(d: date) -> date:
    nxt = (d.replace(day=28) + timedelta(days=4)).replace(day=1)
    return nxt - timedelta(days=1)

def add_month(d: date) -> date:
    return (month_end(d) + timedelta(days=1))

def is_workday(d: date) -> bool:
    return d.weekday() != 6  # no domingo

# ---------- REGLA CORREGIDA: mes objetivo + finalize ----------
def mes_objetivo(sat: date):
    """Dado el sábado de referencia, devuelve (primer_dia_mes_objetivo, es_finalize)."""
    curr = month_start(sat)
    prev_end = curr - timedelta(days=1)
    prev = month_start(prev_end)
    f_prev = first_sat_ge(prev_end)          # sábado que completa el mes anterior
    meso = prev if sat == f_prev else curr
    f_final = first_sat_ge(month_end(meso))  # sábado que completa el mes objetivo
    es_finalize = (sat == f_final)
    return meso, es_finalize

def rango_carga(sat: date):
    """Rango que Cecilia descarga y pega (reemplazando todo)."""
    meso, _ = mes_objetivo(sat)
    return (month_start(meso), sat)          # [1° mes objetivo .. este sábado]

# ---------- semana absoluta Lun→Dom (igual a 'Filtro de campos') ----------
def semana_abs(d: date):
    """Etiqueta S_n y el lunes/domingo del bucket que contiene d (Lun→Dom)."""
    jan1 = date(d.year, 1, 1)
    days_to_first_sun = (6 - jan1.weekday()) % 7  # weekday: Dom=6
    first_sun = jan1 + timedelta(days=days_to_first_sun)
    if d <= first_sun:
        # semana 1 (parcial): 1-ene .. primer domingo
        return ("S1", jan1, first_sun)
    first_mon = first_sun + timedelta(days=1)
    diff = (d - first_mon).days
    wk = 2 + diff // 7
    mon = first_mon + timedelta(days=7 * (diff // 7))
    return (f"S{wk}", mon, mon + timedelta(days=6))

def semana_mes(d: date):
    """Etiqueta 'Semana N' relativa al mes (Lun→Dom, primera semana parcial)."""
    ms = month_start(d)
    days_to_first_sun = (6 - ms.weekday()) % 7
    first_sun = ms + timedelta(days=days_to_first_sun)
    if d <= first_sun:
        return "Semana 1"
    first_mon = first_sun + timedelta(days=1)
    diff = (d - first_mon).days
    return f"Semana {2 + diff // 7}"

def daterange(a: date, b: date):
    d = a
    while d <= b:
        yield d
        d += timedelta(days=1)

# ============================ SIMULACIÓN ============================
def run(year_from=2025, year_to=2027):
    # sábados de referencia entre nov-2025 y feb-2027 (cubre 2026 completo + bordes)
    start = first_sat_ge(date(2025, 11, 1))
    end = date(2027, 2, 28)
    sats = []
    s = start
    while s <= end:
        sats.append(s)
        s += timedelta(days=7)

    errores = []
    finalizes = {}  # mes(ISO yyyy-mm) -> [sábados que lo finalizan]

    # --- 1) cada mes finaliza exactamente una vez ---
    for sat in sats:
        meso, fin = mes_objetivo(sat)
        if fin:
            key = meso.strftime("%Y-%m")
            finalizes.setdefault(key, []).append(sat)

    for mes in [date(2026, m, 1) for m in range(1, 13)]:
        key = mes.strftime("%Y-%m")
        n = len(finalizes.get(key, []))
        if n != 1:
            errores.append(f"[FINALIZE] {key}: se finaliza {n} veces (esperado 1) -> {finalizes.get(key)}")

    # --- 2) al cierre, la planilla tiene todos los días hábiles del mes ---
    for mes in [date(2026, m, 1) for m in range(1, 13)]:
        f_final = first_sat_ge(month_end(mes))
        ini, fin_sat = rango_carga(f_final)
        sheet = set(daterange(ini, fin_sat))
        habiles = {d for d in daterange(mes, month_end(mes)) if is_workday(d)}
        faltan = habiles - sheet
        if faltan:
            errores.append(f"[MENSUAL] {mes:%Y-%m}: faltan {len(faltan)} días al cierre: "
                           f"{sorted(str(d) for d in faltan)[:5]}...")
        # mes objetivo en el cierre debe ser el propio mes
        meso, _ = mes_objetivo(f_final)
        if meso != mes:
            errores.append(f"[MENSUAL] {mes:%Y-%m}: en su cierre el mes objetivo es {meso:%Y-%m}")

    # --- 3) cobertura total: cada día hábil de 2026 procesado bajo su propio mes ---
    # Un día d se procesa bajo mes M si: existe un sábado con mesObjetivo==month(d),
    # d está en la planilla ese sábado, y Mes(d)==M (filtro). Verificamos en el cierre de cada mes.
    procesados = {}  # día -> set de meses bajo los que se contó
    for sat in sats:
        meso, _ = mes_objetivo(sat)
        ini, finsat = rango_carga(sat)
        for d in daterange(ini, finsat):
            if not is_workday(d):
                continue
            # filtro de la rama mensual/semana_mes: solo filas cuyo mes == mes objetivo
            if month_start(d) == meso:
                procesados.setdefault(d, set()).add(meso.strftime("%Y-%m"))

    for d in daterange(date(2026, 1, 1), date(2026, 12, 31)):
        if not is_workday(d):
            continue
        meses = procesados.get(d, set())
        if len(meses) == 0:
            errores.append(f"[COBERTURA] {d} (hábil) NUNCA se procesa")
        elif len(meses) > 1:
            errores.append(f"[COBERTURA] {d} se procesa en >1 mes: {meses}")
        elif meses != {month_start(d).strftime('%Y-%m')}:
            errores.append(f"[COBERTURA] {d} se procesa bajo mes equivocado: {meses}")

    # --- 4) sin colisión Semana_mes: al cierre, filtrado a mes objetivo, una sola etiqueta por (semana) ---
    for mes in [date(2026, m, 1) for m in range(1, 13)]:
        f_final = first_sat_ge(month_end(mes))
        ini, finsat = rango_carga(f_final)
        sheet = [d for d in daterange(ini, finsat) if is_workday(d) and month_start(d) == mes]
        # cada 'Semana N' debe mapear a un único mes (trivial tras filtro) y cubrir días contiguos
        etiquetas = {}
        for d in sheet:
            etiquetas.setdefault(semana_mes(d), set()).add(month_start(d))
        for et, ms in etiquetas.items():
            if len(ms) != 1:
                errores.append(f"[SEMANA_MES] {mes:%Y-%m}: etiqueta {et} mezcla meses {ms}")

    # --- 5) semana absoluta completa al emitirse (cada domingo reporta el bucket de ayer) ---
    for sat in sats:
        domingo = sat + timedelta(days=1)
        etq, lun, dom = semana_abs(sat)             # bucket que contiene al sábado
        meso, _ = mes_objetivo(sat)
        ini, finsat = rango_carga(sat)
        sheet = set(daterange(ini, finsat))
        habiles_bucket = {d for d in daterange(lun, dom) if is_workday(d)}
        faltan = habiles_bucket - sheet
        if faltan and date(2026,1,1) <= sat <= date(2026,12,31):
            errores.append(f"[SEMANAL] domingo {domingo}: bucket {etq} incompleto, faltan {sorted(str(d) for d in faltan)}")

    # --- comparación con lógica VIEJA (mensual el último día del mes) ---
    print("=" * 70)
    print("LÓGICA VIEJA — días perdidos por mes (cola posterior al último sábado del mes,")
    print("que cargaba recién el mes siguiente, cuando el mensual ya había salido):")
    print("=" * 70)
    total_perdidos = 0
    for mes in [date(2026, m, 1) for m in range(1, 13)]:
        me = month_end(mes)
        ult_sab_en_mes = last_sat_le(me)
        cola = [d for d in daterange(ult_sab_en_mes + timedelta(days=1), me) if is_workday(d)]
        if cola:
            total_perdidos += len(cola)
            print(f"  {mes:%Y-%m}: {len(cola)} día(s) en riesgo -> {', '.join(d.strftime('%d-%a') for d in cola)}")
    print(f"  TOTAL días-mes en riesgo (vieja): {total_perdidos}")
    print()

    # --- resultado ---
    print("=" * 70)
    if errores:
        print(f"❌ {len(errores)} PROBLEMA(S) CON LA REGLA NUEVA:")
        for e in errores:
            print("  - " + e)
    else:
        print("✅ REGLA NUEVA: 0 días perdidos. Cobertura total, sin colisión, 1 cierre por mes.")
    print("=" * 70)

    # --- tabla ilustrativa de algunos bordes 2026 ---
    print("\nEjemplos de bordes 2026 (sábado de referencia -> mes objetivo / ¿cierra? / rango):")
    ejemplos = [date(2026,1,3), date(2026,2,7), date(2026,2,28), date(2026,3,7),
                date(2026,4,25), date(2026,5,2), date(2026,5,9), date(2026,5,30),
                date(2026,6,6), date(2026,12,5), date(2027,1,2), date(2027,1,9)]
    for sat in ejemplos:
        meso, fin = mes_objetivo(sat)
        ini, f = rango_carga(sat)
        print(f"  {sat:%Y-%m-%d %a} -> obj={meso:%Y-%m}  cierra={'SÍ' if fin else 'no':3}  "
              f"carga=[{ini:%Y-%m-%d} .. {f:%Y-%m-%d}]")

    return len(errores) == 0

if __name__ == "__main__":
    ok = run()
    raise SystemExit(0 if ok else 1)
