"""
Limpia SOLO las opps duplicadas (mismo contactId+name que una opp del deal-idmap,
y cuyo id NO está en el idmap). NUNCA toca las 2.295 reales ni las 4 de ejemplo de GHL.
POR DEFECTO dry-run. Requiere --apply para borrar. Guarda los borrados en opps-borradas.json.
Uso: python3 limpiar-opps-duplicadas.py [--apply] [--limit N]
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from _ghl_client import GHL

HERE = os.path.dirname(__file__); OUTI = os.path.join(HERE, "..", "salida-import")
apply = "--apply" in sys.argv
limit = 0
for i, a in enumerate(sys.argv):
    if a == "--limit": limit = int(sys.argv[i+1])

g = GHL(); LOC = g.location_id
deal = json.load(open(os.path.join(OUTI, "deal-idmap.json")))
idset = set(deal.values())

allo = []; params = {"location_id": LOC, "limit": 100}
while True:
    st, d = g.get("/opportunities/search", params=params)
    b = d.get("opportunities", []); allo += b
    nxt = (d.get("meta") or {}).get("startAfterId"); nxa = (d.get("meta") or {}).get("startAfter")
    if not b or len(b) < 100 or not nxt: break
    params = {"location_id": LOC, "limit": 100, "startAfterId": nxt, "startAfter": nxa}

idmap_keys = {(o.get("contactId"), (o.get("name") or "").strip()) for o in allo if o.get("id") in idset}
# dup = NO en idmap Y su (contacto,nombre) matchea una del idmap
dups = [o for o in allo if o.get("id") not in idset
        and (o.get("contactId"), (o.get("name") or "").strip()) in idmap_keys]
if limit: dups = dups[:limit]

print(f"duplicados a borrar: {len(dups)}  (idmap intacto: {len(idset)})")
if not apply:
    print("DRY-RUN — nada borrado. Correr con --apply para ejecutar.")
    for o in dups[:10]: print("  ", o.get("id"), o.get("name"))
    sys.exit(0)

borradas = []
for o in dups:
    oid = o.get("id")
    st, d = g.delete(f"/opportunities/{oid}")
    if st in (200, 201): borradas.append(oid)
    else: print(f"FAIL delete {oid}: {st} {json.dumps(d)[:120]}")
    time.sleep(0.4)
json.dump(borradas, open(os.path.join(OUTI, "opps-borradas.json"), "w"))
print(f"APPLY — borradas {len(borradas)}/{len(dups)}. Registradas en opps-borradas.json")
