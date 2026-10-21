"""
FASE 0 · Snapshot del estado actual de la sub-cuenta GHL (read-only).
- Confirma de paso los paths 🔍 (custom fields, custom values, tags, pipelines, calendars, users, businesses).
- Detecta los artefactos de juguete ZZSBX/zzz del sandbox.
- Guarda cada respuesta en snapshots/ghl-estado-inicial-<fecha>/<obj>.json
No escribe nada en GHL.
"""
import json, os, sys
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(__file__))
from _ghl_client import GHL

STAMP = "2026-09-03"  # fecha lógica del snapshot (no usar Date.now para reproducibilidad)
OUTDIR = os.path.join(os.path.dirname(__file__), "..", "snapshots", f"ghl-estado-inicial-{STAMP}")
os.makedirs(OUTDIR, exist_ok=True)

g = GHL()
LOC = g.location_id

# (etiqueta, método, path, params, clave de lista en la respuesta)
PROBES = [
    ("location",            "GET", f"/locations/{LOC}", None, None),
    ("customFields_contact","GET", f"/locations/{LOC}/customFields", {"model": "contact"}, "customFields"),
    ("customFields_opp",    "GET", f"/locations/{LOC}/customFields", {"model": "opportunity"}, "customFields"),
    ("customValues",        "GET", f"/locations/{LOC}/customValues", None, "customValues"),
    ("tags",                "GET", f"/locations/{LOC}/tags", None, "tags"),
    ("pipelines",           "GET", "/opportunities/pipelines", {"locationId": LOC}, "pipelines"),
    ("calendars",           "GET", "/calendars/", {"locationId": LOC}, "calendars"),
    ("calendarGroups",      "GET", "/calendars/groups", {"locationId": LOC}, "groups"),
    ("users",               "GET", "/users/", {"locationId": LOC}, "users"),
    ("businesses",          "GET", "/businesses/", {"locationId": LOC}, "businesses"),
]

results = {}
print(f"{'OBJETO':24} {'HTTP':>5}  {'COUNT':>6}")
for label, method, path, params, listkey in PROBES:
    st, data = g.get(path, params=params)
    count = ""
    if isinstance(data, dict) and listkey and isinstance(data.get(listkey), list):
        count = len(data[listkey])
    with open(os.path.join(OUTDIR, f"{label}.json"), "w", encoding="utf-8") as f:
        json.dump({"status": st, "params": params, "data": data}, f, ensure_ascii=False, indent=2)
    results[label] = {"status": st, "count": count, "listkey": listkey}
    print(f"{label:24} {st:>5}  {str(count):>6}")

# --- ZZSBX / zzz artefactos de juguete ---
print("\n=== Artefactos de juguete (ZZSBX / zzz) ===")
def scan(label, listkey, needle_fields):
    p = os.path.join(OUTDIR, f"{label}.json")
    if not os.path.exists(p):
        return
    d = json.load(open(p))["data"]
    items = d.get(listkey, []) if isinstance(d, dict) else []
    for it in items:
        blob = json.dumps(it, ensure_ascii=False).lower()
        if "zzsbx" in blob or "zzz sbx" in blob or "zzz" in (it.get("name","").lower() if isinstance(it,dict) else ""):
            print(f"  [{label}] id={it.get('id')} name={it.get('name')}")

scan("customFields_contact", "customFields", ["name"])
scan("customFields_opp", "customFields", ["name"])
scan("businesses", "businesses", ["name"])
scan("tags", "tags", ["name"])

# Contactos de juguete conocidos (del sandbox 01 §Artefactos)
TOY_CONTACTS = ["cjO6zKlRaeHdpPPwlIop", "J4eBGuKUUOVrdLmbQv85"]
for cid in TOY_CONTACTS:
    st, d = g.get(f"/contacts/{cid}")
    c = d.get("contact", {}) if isinstance(d, dict) else {}
    print(f"  [contact] {cid}: HTTP {st} name={c.get('firstName')} {c.get('lastName')} phone={c.get('phone')}")

with open(os.path.join(OUTDIR, "_resumen.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\nGuardado en {OUTDIR}")
