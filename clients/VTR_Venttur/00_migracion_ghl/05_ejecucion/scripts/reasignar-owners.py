"""
FASE 3.b · Reasignar assignedTo de los Contacts ya importados (owner_clientify → userId).
- Los contacts se importaron con owner_clientify pero sin assignedTo (workaround B-03).
  Ahora que existen usuarios, se setea assignedTo por email del owner.
- Diego Matus → Juan José (remap ya en usuarios-idmap).
- Owners sin usuario en la location (Rodrigo/Andrés/Max, B-11) → se saltan (quedan con owner_clientify).
- Idempotente: registra los hechos en salida-import/reassigned-contacts.json.
Uso: python3 reasignar-owners.py [--apply] [--limit N]
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from _ghl_client import GHL

HERE = os.path.dirname(__file__)
SPEC = os.path.join(HERE, "..", "spec"); OUTI = os.path.join(HERE, "..", "salida-import"); ETL = os.path.join(HERE, "..", "salida-etl")
def load(p, d=None): return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else d

apply = "--apply" in sys.argv
limit = 0
for i, a in enumerate(sys.argv):
    if a == "--limit": limit = int(sys.argv[i+1])

umap = load(os.path.join(SPEC, "usuarios-idmap.json"), {"by_email": {}})
cmap = load(os.path.join(OUTI, "contact-idmap.json"), {})
done = set(load(os.path.join(OUTI, "reassigned-contacts.json"), []))
rows = [json.loads(l) for l in open(os.path.join(ETL, "contacts.jsonl"), encoding="utf-8")]
if limit: rows = rows[:limit]

g = GHL(); LOC = g.location_id
byemail = umap["by_email"]
ok = skip_noowner = skip_nouser = skip_nocid = already = failed = 0
for r in rows:
    owner = (r.get("owner_email") or "").lower()
    if not owner: skip_noowner += 1; continue
    uid = byemail.get(owner)
    if not uid: skip_nouser += 1; continue           # Rodrigo/Andrés/Max (B-11)
    cid = cmap.get(r.get("canon_phone")) or cmap.get(r.get("email"))
    if not cid: skip_nocid += 1; continue
    if cid in done: already += 1; continue
    if not apply: ok += 1; continue
    st, d = g.put(f"/contacts/{cid}", {"assignedTo": uid})
    if st in (200, 201): done.add(cid); ok += 1
    else: failed += 1
    if apply and ok % 50 == 0:
        json.dump(sorted(done), open(os.path.join(OUTI, "reassigned-contacts.json"), "w"))
        print(f"... reasignados={ok} · sin-usuario(B-11)={skip_nouser} · fallidos={failed}")
    time.sleep(0.5)
if apply: json.dump(sorted(done), open(os.path.join(OUTI, "reassigned-contacts.json"), "w"))
print(f"{'APPLY' if apply else 'DRY'} reasignación contacts: hechos={ok} · ya-estaban={already} · "
      f"sin-owner={skip_noowner} · sin-usuario-en-location(B-11: Rodrigo/Andrés/Max)={skip_nouser} · sin-contactId={skip_nocid} · fallidos={failed}")
