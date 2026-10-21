#!/usr/bin/env python3
"""
Migración v3.4 → v3.5 del Reporte Facturación Sonrisas: arreglo PERMANENTE del
descuadre de semanas puente vía una hoja "Histórico" de-duplicada.

Problema (confirmado con datos): la carga de "Ingreso datos" es por ventana variable
(mes objetivo / fechas del recordatorio a Cecilia). La semana puente (S14, borde
marzo/abril) se procesa en dos cargas y el write semanal (overwrite) deja solo la
porción de la última ventana → se pierde la porción del mes anterior (ej. $14.910 en
Paso Molino × AJUSTE; ~$206.920 sumando las 9 celdas S14 de todas las sucursales).

Fix: el reporte, antes de agregar, vuelca la ventana actual a una hoja "Histórico"
con `appendOrUpdate` por clave única `_key = "# Pago" + "-" + "# Detalle Presupuesto"`
(0 colisiones en el dataset; absorbe altas y correcciones de monto, idempotente), y
LUEGO agrega desde "Histórico" (año completo). Así ninguna semana puente se parte y
el overwrite del reporte siempre escribe el valor completo.

Lee  : clients/SNR_Sonrisas/03_workflows/sonrisas-reporte-facturacion-v3.4.json
Crea : clients/SNR_Sonrisas/03_workflows/sonrisas-reporte-facturacion-v3.5.json

Uso:
  python3 scripts/utilities/fix-sonrisas-historico-workflow.py
"""
from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "clients/SNR_Sonrisas/03_workflows/sonrisas-reporte-facturacion-v3.4.json"
DST = ROOT / "clients/SNR_Sonrisas/03_workflows/sonrisas-reporte-facturacion-v3.5.json"

# Documento donde vive "Ingreso datos" (mismo doc para la pestaña Histórico)
INGRESO_DOC = "1RnWwaqEnGlyuUNnG4HW8jl5WoxFB7ypEm-Ey67bQkO8"
HIST_TAB = "Histórico"

# Columnas que el Histórico debe conservar (todas las que el reporte aguas abajo usa).
HIST_COLS = [
    "_key",
    "# Pago",
    "# Detalle Presupuesto",
    "Fecha de recepción del pago",
    "Mes de recepción del pago",
    "Nombre Sucursal",
    "Código Prestación",
    "Nombre categoría",
    "Pagado Prestación",
    "Abono Libre",
]

KEYEAR_JS = r"""// Agrega la clave única de de-duplicación para el Histórico:
//   _key = "# Pago" + "-" + "# Detalle Presupuesto"   (0 colisiones en el dataset real)
// Conserva todas las columnas originales.
return items.map((item) => {
  const r = item.json || {};
  const pago = String(r['# Pago'] ?? '').trim();
  const detalle = String(r['# Detalle Presupuesto'] ?? '').trim();
  return { json: { ...r, _key: pago + '-' + detalle } };
});
"""

FILTER_2M_JS = r"""// Filtra el Histórico a los últimos 2 meses para reducir la huella de memoria.
// El reporte agrega sobre el Histórico de-duplicado; al restringir a mes corriente
// + mes anterior se cubren todos los bordes de mes relevantes (incluida cualquier
// semana puente) sin cargar el año completo en RAM.
const tz = 'America/Montevideo';
const M = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];

const now = DateTime.now().setZone(tz);
const mesCorriente = M[now.month - 1];
const mesAnterior  = M[(now.month - 2 + 12) % 12];
const mesesValidos = new Set([mesCorriente, mesAnterior]);

return items.filter(item => {
  const mes = String(item.json['Mes de recepción del pago'] ?? '').trim();
  return mesesValidos.has(mes);
});
"""


def rl_doc():
    return {
        "__rl": True,
        "value": INGRESO_DOC,
        "mode": "list",
        "cachedResultName": "Ingreso datos | Sonrisas",
        "cachedResultUrl": f"https://docs.google.com/spreadsheets/d/{INGRESO_DOC}/edit?usp=drivesdk",
    }


def rl_tab():
    return {"__rl": True, "value": HIST_TAB, "mode": "name"}


def hist_schema():
    sch = []
    for c in HIST_COLS:
        sch.append({
            "id": c, "displayName": c, "required": False, "defaultMatch": (c == "_key"),
            "display": True, "type": "string", "canBeUsedToMatch": True, "removed": False,
        })
    return sch


def find_node(wf, name):
    for n in wf["nodes"]:
        if n.get("name") == name:
            return n
    return None


def main() -> int:
    wf = json.loads(SRC.read_text(encoding="utf-8"))

    for req in ["Get row(s) in sheet", "Parsear y validar fecha"]:
        if find_node(wf, req) is None:
            print(f"ERROR: falta nodo esperado '{req}' (¿corriste antes la migración v3.4?).", file=sys.stderr)
            return 2
    for n in ("Keyear Histórico", "Upsert Histórico", "Get Histórico", "Filtrar Histórico 2M"):
        if find_node(wf, n) is not None:
            print(f"ERROR: el workflow ya tiene '{n}' (migración v3.5 ya aplicada).", file=sys.stderr)
            return 2

    parse_node = find_node(wf, "Parsear y validar fecha")
    px, py = parse_node["position"]

    # --- nodos nuevos ---
    keyear = {
        "parameters": {"jsCode": KEYEAR_JS},
        "type": "n8n-nodes-base.code", "typeVersion": 2,
        "position": [px - 660, py], "id": str(uuid.uuid4()), "name": "Keyear Histórico",
    }
    upsert = {
        "parameters": {
            "operation": "appendOrUpdate",
            "documentId": rl_doc(),
            "sheetName": rl_tab(),
            "columns": {
                "mappingMode": "defineBelow",
                "value": {c: f"={{{{ $json['{c}'] }}}}" for c in HIST_COLS},
                "matchingColumns": ["_key"],
                "schema": hist_schema(),
            },
            "options": {},
        },
        "type": "n8n-nodes-base.googleSheets", "typeVersion": 4.7,
        "position": [px - 500, py], "id": str(uuid.uuid4()), "name": "Upsert Histórico",
    }
    get_hist = {
        "parameters": {"documentId": rl_doc(), "sheetName": rl_tab(), "options": {}},
        "type": "n8n-nodes-base.googleSheets", "typeVersion": 4.7,
        "position": [px - 340, py], "id": str(uuid.uuid4()), "name": "Get Histórico",
    }
    filtrar_2m = {
        "parameters": {"jsCode": FILTER_2M_JS},
        "type": "n8n-nodes-base.code", "typeVersion": 2,
        "position": [px - 180, py], "id": str(uuid.uuid4()), "name": "Filtrar Histórico 2M",
    }
    wf["nodes"].extend([keyear, upsert, get_hist, filtrar_2m])

    # --- reconectar: (lo que iba a 'Parsear y validar fecha') -> Keyear -> Upsert -> Get Histórico -> Filtrar 2M -> Parsear ---
    conns = wf["connections"]
    redirected = 0
    for src, obj in conns.items():
        if src in ("Keyear Histórico", "Upsert Histórico", "Get Histórico", "Filtrar Histórico 2M"):
            continue
        for branch in obj.get("main", []):
            for c in branch:
                if c.get("node") == "Parsear y validar fecha":
                    c["node"] = "Keyear Histórico"
                    redirected += 1
    conns["Keyear Histórico"]    = {"main": [[{"node": "Upsert Histórico",        "type": "main", "index": 0}]]}
    conns["Upsert Histórico"]    = {"main": [[{"node": "Get Histórico",           "type": "main", "index": 0}]]}
    conns["Get Histórico"]       = {"main": [[{"node": "Filtrar Histórico 2M",   "type": "main", "index": 0}]]}
    conns["Filtrar Histórico 2M"] = {"main": [[{"node": "Parsear y validar fecha", "type": "main", "index": 0}]]}

    if redirected == 0:
        print("ERROR: no encontré la conexión entrante a 'Parsear y validar fecha'.", file=sys.stderr)
        return 2

    if "name" in wf:
        wf["name"] = wf["name"].replace("v3.4", "v3.5")

    out = json.dumps(wf, ensure_ascii=False, indent=2)
    json.loads(out)
    DST.write_text(out + "\n", encoding="utf-8")

    print(f"OK → {DST.relative_to(ROOT)}")
    print(f"   • reconexión: {redirected} entrada(s) -> Keyear Histórico -> Upsert Histórico -> Get Histórico -> Filtrar Histórico 2M -> Parsear y validar fecha")
    print(f"   • Upsert Histórico: appendOrUpdate en pestaña '{HIST_TAB}' (doc Ingreso datos), match por _key")
    print(f"   • Get Histórico: lee el año completo desde '{HIST_TAB}'")
    print(f"   • Filtrar Histórico 2M: recorta a mes corriente + mes anterior → reduce RAM en instancias pequeñas")
    print(f"   • clave _key = '# Pago' + '-' + '# Detalle Presupuesto'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
