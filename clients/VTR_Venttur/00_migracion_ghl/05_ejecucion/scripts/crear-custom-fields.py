"""
FASE 1.1/1.2 · Crear los custom fields de Contact + Opportunity (idempotente).
- Lee spec/custom-fields.json.
- GET existentes → crea solo los que faltan (match por nombre, case-insensitive).
- Read-back de cada creación. Escribe idmap (name→id/fieldKey) a spec/custom-fields-idmap.json.
- NO borra nada. Re-correr no duplica.
Uso: python3 crear-custom-fields.py [--dry-run]
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from _ghl_client import GHL

DRY = "--dry-run" in sys.argv
SPEC = os.path.join(os.path.dirname(__file__), "..", "spec", "custom-fields.json")
IDMAP = os.path.join(os.path.dirname(__file__), "..", "spec", "custom-fields-idmap.json")
spec = json.load(open(SPEC, encoding="utf-8"))
g = GHL(); LOC = g.location_id

idmap = json.load(open(IDMAP)) if os.path.exists(IDMAP) else {"contact": {}, "opportunity": {}}

def existing(model):
    st, d = g.get(f"/locations/{LOC}/customFields", params={"model": model})
    lst = d.get("customFields", []) if isinstance(d, dict) else []
    return {(c.get("name") or "").strip().lower(): c for c in lst}

for model in ("contact", "opportunity"):
    have = existing(model)
    print(f"\n=== {model.upper()} — existentes: {len(have)} ===")
    created = skipped = failed = 0
    for fld in spec[model]:
        nm = fld["name"]; key = nm.strip().lower()
        if key in have:
            c = have[key]
            idmap[model][nm] = {"id": c.get("id"), "fieldKey": c.get("fieldKey"), "dataType": c.get("dataType")}
            skipped += 1
            continue
        body = {"name": nm, "dataType": fld["dataType"], "model": model}
        if fld.get("options"):
            body["options"] = fld["options"]
        if DRY:
            print(f"  [dry] CREATE {nm} ({fld['dataType']})"); created += 1; continue
        st, d = g.post(f"/locations/{LOC}/customFields", body)
        cf = d.get("customField", {}) if isinstance(d, dict) else {}
        if st in (200, 201) and cf.get("id"):
            # read-back
            st2, d2 = g.get(f"/locations/{LOC}/customFields/{cf['id']}")
            rb = (d2.get("customField") or {}).get("dataType") if isinstance(d2, dict) else None
            ok = rb == fld["dataType"]
            idmap[model][nm] = {"id": cf["id"], "fieldKey": cf.get("fieldKey"), "dataType": cf.get("dataType")}
            print(f"  {'✅' if ok else '⚠️'} {nm:48} {fld['dataType']:14} id={cf['id']} rb={rb}")
            created += 1
        else:
            print(f"  ❌ {nm:48} HTTP {st} {json.dumps(d)[:120]}")
            failed += 1
        time.sleep(0.15)
    print(f"  → creados={created} · ya existían={skipped} · fallidos={failed}")

if not DRY:
    json.dump(idmap, open(IDMAP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\nidmap → {IDMAP} (contact={len(idmap['contact'])}, opportunity={len(idmap['opportunity'])})")
