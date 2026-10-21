"""
Reconciliación post-import VTR → GHL. Cuenta lo REAL en la location vs los idmaps.
Solo lecturas. Uso: python3 reconciliar-import.py
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _ghl_client import GHL

HERE = os.path.dirname(__file__)
OUTI = os.path.join(HERE, "..", "salida-import")
def load(p, d=None): return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else d

g = GHL(); LOC = g.location_id

# --- totales reales en GHL ---
st_o, d_o = g.get("/opportunities/search", params={"location_id": LOC, "limit": 1})
opp_total = (d_o.get("meta") or {}).get("total") if isinstance(d_o, dict) else None

st_c, d_c = g.post("/contacts/search", {"locationId": LOC, "pageLimit": 1})
con_total = d_c.get("total") if isinstance(d_c, dict) else None

# --- esperados (idmaps) ---
deal = json.load(open(os.path.join(OUTI, "deal-idmap.json")))
con_map = json.load(open(os.path.join(OUTI, "contact-idmap.json")))
reassigned = json.load(open(os.path.join(OUTI, "reassigned-contacts.json")))
con_ids = set(con_map.values())

print(f"location: {LOC}")
print(f"OPPS   — GHL real: {opp_total}  | idmap (creados): {len(deal)}")
print(f"CONTACTS — GHL real: {con_total}  | idmap distinct: {len(con_ids)}  | reasignados: {len(reassigned)}")

# --- spot-check: 5 opps del idmap, ver pipeline+stage+assignedTo ---
print("\nSpot-check 5 opps (pipeline / stage / assignedTo):")
sample = list(deal.values())[:5]
ok_pl = ok_as = 0
for oid in sample:
    st, d = g.get(f"/opportunities/{oid}")
    o = (d.get("opportunity") or {}) if isinstance(d, dict) else {}
    pl = o.get("pipelineId"); sg = o.get("pipelineStageId"); asg = o.get("assignedTo")
    if pl and sg: ok_pl += 1
    if asg: ok_as += 1
    print(f"  {oid}: pl={'OK' if pl else 'FALTA'} stage={'OK' if sg else 'FALTA'} assignedTo={asg or 'FALTA'} status={o.get('status')}")
print(f"  → {ok_pl}/5 con pipeline+stage · {ok_as}/5 con assignedTo")

# --- spot-check: 5 contacts reasignados, ver assignedTo ---
print("\nSpot-check 5 contacts reasignados (assignedTo):")
ok_c = 0
for cid in reassigned[:5]:
    st, d = g.get(f"/contacts/{cid}")
    c = (d.get("contact") or {}) if isinstance(d, dict) else {}
    asg = c.get("assignedTo")
    if asg: ok_c += 1
    print(f"  {cid}: assignedTo={asg or 'FALTA'}")
print(f"  → {ok_c}/5 con assignedTo")
