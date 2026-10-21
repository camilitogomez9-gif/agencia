#!/usr/bin/env python3
"""
Migración del workflow de Reporte Facturación Sonrisas para cerrar el descuadre
Mensual vs Semanal (gap de $14.910 en Paso Molino × AJUSTE).

Lee  : clients/SNR_Sonrisas/03_workflows/sonrisas-reporte-facturacion-v3.3.json
Crea : clients/SNR_Sonrisas/03_workflows/sonrisas-reporte-facturacion-v3.4.json
(NO modifica el v3.3 original.)

Cambios aplicados (todos verificados al final):
  A) Nodo nuevo "Parsear y validar fecha" (Code) antes de "Filtro de campos":
     parsea 'Fecha de recepción del pago' de forma robusta (yyyy-MM-dd, ISO con hora,
     dd/MM/yyyy, d/M/yyyy, dd-MM-yyyy, serial de Sheets) y deriva _semana / _semanaMes
     / _mesDerivado desde una ÚNICA fecha validada. Marca _fechaValida=false sin
     descartar (no produce 'SNaN' silencioso).
  B) "Filtro de campos": Semana y Semana_mes ahora leen _semana / _semanaMes
     (mismo origen validado). 'Mes' se mantiene en el campo manual (no se toca el
     formato de las etiquetas de mes existentes en el Sheet).
  C) "Filtro1": además de códigos desconocidos, ABORTA si alguna fila con contenido
     tiene fecha no parseable → la rama de error existente (Respond Error) la reporta.
     Esto convierte el descarte silencioso en un fallo visible.
  D) Las 4 escrituras (semana, Reporte general, Por sucursal semana, Por sucursal mes)
     pasan de operación 'update' → 'appendOrUpdate' para que una etiqueta de semana
     nueva se AGREGUE en vez de perderse en silencio.

Uso:
  python3 scripts/utilities/fix-sonrisas-reconciliacion-workflow.py
"""
from __future__ import annotations

import copy
import json
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "clients/SNR_Sonrisas/03_workflows/sonrisas-reporte-facturacion-v3.3.json"
DST = ROOT / "clients/SNR_Sonrisas/03_workflows/sonrisas-reporte-facturacion-v3.4.json"

PARSE_NODE_NAME = "Parsear y validar fecha"
WRITERS = ["semana", "Reporte general", "Por sucursal semana", "Por sucursal mes"]

# --------------------------------------------------------------------------------------
# JS del nodo nuevo "Parsear y validar fecha" (corre en modo "Run Once for All Items").
# DateTime (luxon) está disponible como global en los Code node de n8n.
# --------------------------------------------------------------------------------------
PARSE_JS = r"""// Parsea 'Fecha de recepción del pago' de forma robusta y deriva semana/mes desde
// una ÚNICA fecha validada. No descarta nada en silencio: marca _fechaValida=false
// y 'Filtro1' aborta el flujo si una fila CON contenido tiene fecha inválida.
const tz = 'America/Montevideo';
const M = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
const FORMATOS = ['yyyy-MM-dd', "yyyy-MM-dd'T'HH:mm:ss", 'yyyy-MM-dd HH:mm:ss', 'dd/MM/yyyy', 'd/M/yyyy', 'dd-MM-yyyy'];

function serialAFecha(n) {
  // Serial de Google Sheets / Excel: días desde 1899-12-30
  return DateTime.fromObject({ year: 1899, month: 12, day: 30 }, { zone: tz }).plus({ days: Math.floor(n) });
}

function parseFecha(raw) {
  if (raw === null || raw === undefined) return null;
  if (typeof raw === 'number' && isFinite(raw)) {
    return (raw >= 1 && raw <= 80000) ? serialAFecha(raw) : null;
  }
  const s = String(raw).trim();
  if (!s) return null;
  for (const f of FORMATOS) {
    const d = DateTime.fromFormat(s, f, { zone: tz });
    if (d.isValid) return d.startOf('day');
  }
  const iso = DateTime.fromISO(s, { zone: tz });
  if (iso.isValid) return iso.startOf('day');
  if (/^\d+(\.\d+)?$/.test(s)) {
    const n = parseFloat(s);
    if (n >= 1 && n <= 80000) return serialAFecha(n);
  }
  return null;
}

function semanaAnio(dt) {
  const jan1 = dt.startOf('year');
  const daysToFirstSunday = (7 - jan1.weekday) % 7;
  const firstSunday = jan1.plus({ days: daysToFirstSunday });
  if (dt <= firstSunday) return 'S1';
  const firstMonday = firstSunday.plus({ days: 1 });
  const diffDays = Math.floor(dt.diff(firstMonday, 'days').days);
  return 'S' + (2 + Math.floor(diffDays / 7));
}

function semanaMes(dt) {
  const monthStart = dt.startOf('month');
  const daysToFirstSunday = (7 - monthStart.weekday) % 7;
  const firstSunday = monthStart.plus({ days: daysToFirstSunday });
  if (dt <= firstSunday) return 'Semana 1';
  const firstMonday = firstSunday.plus({ days: 1 });
  const diffDays = Math.floor(dt.diff(firstMonday, 'days').days);
  return 'Semana ' + (2 + Math.floor(diffDays / 7));
}

return items.map((item) => {
  const row = item.json || {};
  const dt = parseFecha(row['Fecha de recepción del pago']);
  if (!dt || !dt.isValid) {
    return { json: { ...row, _fechaValida: false, _fechaISO: null, _semana: null, _semanaMes: null, _mesDerivado: null } };
  }
  return {
    json: {
      ...row,
      _fechaValida: true,
      _fechaISO: dt.toISODate(),
      _semana: semanaAnio(dt),
      _semanaMes: semanaMes(dt),
      _mesDerivado: M[dt.month - 1],
    },
  };
});
"""

# Bloque de abort original de Filtro1 (se reemplaza por uno que también valida fechas).
FILTRO1_OLD_ABORT = """if (desconocidos.size > 0) {
  const lista = [...desconocidos].sort().join(", ");
  return [{ json: { _error: true, codigos: lista } }];
}"""

FILTRO1_NEW_ABORT = """// Detectar filas con fecha no parseable (vienen marcadas por 'Parsear y validar fecha')
const fechasInvalidas = [];
for (const item of items) {
  const r = item.json || {};
  const cod = String(r["Código Prestación"] || "").trim();
  const pg = Number(r["Pagado Prestación"]);
  const tieneContenido = cod !== "" || (Number.isFinite(pg) && pg !== 0);
  if (tieneContenido && r._fechaValida === false) {
    fechasInvalidas.push((r.row_number != null ? ("fila " + r.row_number + " ") : "") + "cod=" + cod + " fecha='" + String(r["Fecha de recepción del pago"] ?? "") + "'");
  }
}

if (desconocidos.size > 0 || fechasInvalidas.length > 0) {
  const lista = [...desconocidos].sort().join(", ");
  return [{ json: { _error: true, codigos: lista, fechas_invalidas: fechasInvalidas } }];
}"""

RESPOND_ERROR_OLD = "={{ JSON.stringify({ status: 'error', codigos: $json.codigos }) }}"
RESPOND_ERROR_NEW = "={{ JSON.stringify({ status: 'error', codigos: $json.codigos, fechas_invalidas: $json.fechas_invalidas }) }}"


def find_node(wf, name):
    for n in wf["nodes"]:
        if n.get("name") == name:
            return n
    return None


def main() -> int:
    wf = json.loads(SRC.read_text(encoding="utf-8"))
    changes = []

    # --- pre-flight: nodos esperados ---
    required = ["Filtro de campos", "Filtro1", "Respond Error", "Get row(s) in sheet"] + WRITERS
    missing = [r for r in required if find_node(wf, r) is None]
    if missing:
        print(f"ERROR: faltan nodos esperados en {SRC.name}: {missing}", file=sys.stderr)
        return 2
    if find_node(wf, PARSE_NODE_NAME) is not None:
        print("ERROR: el workflow ya tiene el nodo de parseo (¿migración ya aplicada?).", file=sys.stderr)
        return 2

    filtro_campos = find_node(wf, "Filtro de campos")

    # ===== A) Nodo nuevo "Parsear y validar fecha" =====
    fx, fy = filtro_campos["position"]
    parse_node = {
        "parameters": {"jsCode": PARSE_JS},
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [fx - 224, fy],
        "id": str(uuid.uuid4()),
        "name": PARSE_NODE_NAME,
    }
    # correr posición de Filtro de campos un poco a la derecha para que no se solapen
    filtro_campos["position"] = [fx + 40, fy]
    wf["nodes"].append(parse_node)
    changes.append(f"A) nodo '{PARSE_NODE_NAME}' agregado")

    # --- rewire conexiones: (todo lo que apuntaba a 'Filtro de campos') -> parse -> 'Filtro de campos'
    conns = wf["connections"]
    redirected = 0
    for src, obj in conns.items():
        for branch in obj.get("main", []):
            for c in branch:
                if c.get("node") == "Filtro de campos":
                    c["node"] = PARSE_NODE_NAME
                    redirected += 1
    conns[PARSE_NODE_NAME] = {"main": [[{"node": "Filtro de campos", "type": "main", "index": 0}]]}
    changes.append(f"A) reconexión: {redirected} entrada(s) -> '{PARSE_NODE_NAME}' -> 'Filtro de campos'")
    if redirected == 0:
        print("ADVERTENCIA: no se encontró ninguna conexión entrante a 'Filtro de campos'.", file=sys.stderr)

    # ===== B) Filtro de campos: Semana / Semana_mes desde el origen validado =====
    asg = filtro_campos["parameters"]["assignments"]["assignments"]
    by_name = {a["name"]: a for a in asg}
    if "Semana" not in by_name or "Semana_mes" not in by_name:
        print("ERROR: 'Filtro de campos' no tiene asignaciones Semana/Semana_mes.", file=sys.stderr)
        return 2
    by_name["Semana"]["value"] = "={{ $json._semana }}"
    by_name["Semana_mes"]["value"] = "={{ $json._semanaMes }}"
    changes.append("B) 'Filtro de campos': Semana y Semana_mes ahora leen _semana/_semanaMes")
    # 'Mes' se deja como está (campo manual) a propósito.

    # ===== C) Filtro1: abortar también ante fecha inválida =====
    f1 = find_node(wf, "Filtro1")
    js = f1["parameters"]["jsCode"]
    if FILTRO1_OLD_ABORT not in js:
        print("ERROR: no encontré el bloque de abort original en 'Filtro1'.", file=sys.stderr)
        return 2
    f1["parameters"]["jsCode"] = js.replace(FILTRO1_OLD_ABORT, FILTRO1_NEW_ABORT, 1)
    changes.append("C) 'Filtro1': aborta ante fecha no parseable (rama de error)")

    re_node = find_node(wf, "Respond Error")
    if re_node["parameters"].get("responseBody") == RESPOND_ERROR_OLD:
        re_node["parameters"]["responseBody"] = RESPOND_ERROR_NEW
        changes.append("C) 'Respond Error': incluye fechas_invalidas")
    else:
        print("ADVERTENCIA: 'Respond Error' tenía un body inesperado, no se modificó.", file=sys.stderr)

    # ===== D) writers: update -> appendOrUpdate =====
    for w in WRITERS:
        node = find_node(wf, w)
        op = node["parameters"].get("operation")
        if op == "update":
            node["parameters"]["operation"] = "appendOrUpdate"
            changes.append(f"D) '{w}': update -> appendOrUpdate")
        else:
            print(f"ADVERTENCIA: '{w}' tenía operation='{op}', no se cambió.", file=sys.stderr)

    # --- nombre del workflow ---
    if "name" in wf:
        wf["name"] = wf["name"].replace("v3.3", "v3.4")

    # --- escribir y validar round-trip ---
    out = json.dumps(wf, ensure_ascii=False, indent=2)
    json.loads(out)  # valida que parsea
    DST.write_text(out + "\n", encoding="utf-8")

    print(f"OK → {DST.relative_to(ROOT)}")
    for c in changes:
        print(f"   • {c}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
