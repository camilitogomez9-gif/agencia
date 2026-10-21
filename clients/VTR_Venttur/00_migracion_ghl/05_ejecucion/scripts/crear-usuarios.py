"""
FASE 1.7 · Crear usuarios GHL (cliente: todos menos Diego Matus). Idempotente.
- GET existentes → crea los que faltan (por email). POST /users/ envía invitación real.
- Escribe usuarios-idmap.json: by_email + by_name → userId, con el REMAP Diego Matus → Juan José.
Uso: python3 crear-usuarios.py [--dry-run]
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from _ghl_client import GHL

DRY = "--dry-run" in sys.argv
HERE = os.path.dirname(__file__)
SPEC = json.load(open(os.path.join(HERE, "..", "spec", "usuarios.json"), encoding="utf-8"))
IDMAP = os.path.join(HERE, "..", "spec", "usuarios-idmap.json")
g = GHL(); LOC = g.location_id
COMPANY = SPEC["companyId"]

# existentes
st, d = g.get("/users/", params={"locationId": LOC})
have = {(u.get("email") or "").lower(): u for u in d.get("users", [])}
print(f"Usuarios existentes: {[u.get('email') for u in d.get('users',[])]}")

by_email = {e: u.get("id") for e, u in have.items()}
by_name = {}
for u in SPEC.get("ya_existe", []):
    by_name[u["owner_name"]] = by_email.get(u["email"].lower())

for u in SPEC["crear"]:
    em = u["email"].lower()
    if em in have:
        by_email[em] = have[em].get("id"); by_name[u["owner_name"]] = have[em].get("id")
        print(f"  = ya existe: {u['email']}"); continue
    body = {"companyId": COMPANY, "firstName": u["firstName"], "lastName": u["lastName"],
            "email": u["email"], "type": "account", "role": u.get("role", "user"),
            "locationIds": [LOC]}
    if DRY:
        print(f"  [dry] CREATE user {u['email']}"); continue
    st, d = g.post("/users/", body)
    usr = (d.get("user") or d or {}) if isinstance(d, dict) else {}
    uid = usr.get("id")
    if uid:
        by_email[em] = uid; by_name[u["owner_name"]] = uid
        print(f"  ✅ creado: {u['email']} → {uid} (invitación enviada)")
    else:
        print(f"  ❌ {u['email']}: HTTP {st} {json.dumps(d)[:200]}")
    time.sleep(0.3)

# REMAP Diego Matus → Juan José
for nm in SPEC.get("no_crear", []):
    target = nm["reasignar_a"].lower()
    tid = by_email.get(target)
    if tid:
        by_email[nm["email"].lower()] = tid
        by_name[nm["owner_name"]] = tid
        print(f"  ↪ remap {nm['owner_name']} / {nm['email']} → {nm['reasignar_a']} ({tid})")

if not DRY:
    json.dump({"by_email": by_email, "by_name": by_name}, open(IDMAP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\nidmap → usuarios-idmap.json · by_email={len(by_email)} by_name={len(by_name)}")
