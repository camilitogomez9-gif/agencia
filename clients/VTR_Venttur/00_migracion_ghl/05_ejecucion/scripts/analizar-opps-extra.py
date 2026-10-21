"""
Aísla las opps que están en GHL pero NO en deal-idmap, y las caracteriza:
¿son duplicados (mismo contactId+name que una opp del idmap) o legítimas ajenas?
Solo lecturas. Uso: python3 analizar-opps-extra.py
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _ghl_client import GHL

HERE = os.path.dirname(__file__); OUTI = os.path.join(HERE, "..", "salida-import")
g = GHL(); LOC = g.location_id

deal = json.load(open(os.path.join(OUTI, "deal-idmap.json")))
idmap_oppids = set(deal.values())

# traer TODAS las opps (paginado 100)
allo = []
url = "/opportunities/search"; params = {"location_id": LOC, "limit": 100}
page = 0
while True:
    st, d = g.get(url, params=params)
    if not isinstance(d, dict): break
    batch = d.get("opportunities", [])
    allo.extend(batch)
    page += 1
    nxt = (d.get("meta") or {}).get("startAfterId"); nxa = (d.get("meta") or {}).get("startAfter")
    if not batch or len(batch) < 100 or not nxt: break
    params = {"location_id": LOC, "limit": 100, "startAfterId": nxt, "startAfter": nxa}
    if page > 30: break

print(f"opps traídas de GHL: {len(allo)}")

# index de las del idmap por (contactId, name)
idmap_key = {}
extra = []
for o in allo:
    oid = o.get("id")
    key = (o.get("contactId"), (o.get("name") or "").strip())
    if oid in idmap_oppids:
        idmap_key[key] = oid
    else:
        extra.append(o)

print(f"opps NO en idmap (extra): {len(extra)}")

dup = 0; huerf = 0
muestra = []
for o in extra:
    key = (o.get("contactId"), (o.get("name") or "").strip())
    if key in idmap_key:
        dup += 1
        if len(muestra) < 8: muestra.append(("DUP", o.get("id"), o.get("name"), o.get("dateAdded")))
    else:
        huerf += 1
        if len(muestra) < 8: muestra.append(("HUERF", o.get("id"), o.get("name"), o.get("dateAdded")))

print(f"  → duplicados (mismo contacto+nombre que una del idmap): {dup}")
print(f"  → huérfanas (no matchean ninguna del idmap): {huerf}")
print("\nMuestra:")
for t in muestra: print("  ", t)

# guardar los IDs extra para eventual limpieza (NO borra nada)
json.dump([o.get("id") for o in extra], open(os.path.join(OUTI, "opps-extra-ids.json"), "w"))
print(f"\nIDs extra guardados en salida-import/opps-extra-ids.json ({len(extra)}) — NO se borró nada.")
