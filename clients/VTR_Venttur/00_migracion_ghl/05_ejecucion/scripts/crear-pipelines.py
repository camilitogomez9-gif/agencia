"""
FASE 1.4 · Crear los pipelines (operativo del bot + comerciales verbatim). Idempotente.
- Valida cada pipeline comercial contra el set de stages REAL del snapshot (atrapa typos).
- GET existentes → crea solo los que faltan (por nombre). Read-back. idmap → spec/pipelines-idmap.json
  (name → {id, stages:{stageName: stageId}}) para la Fase 3.
Uso: python3 crear-pipelines.py [--dry-run]
"""
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
from _ghl_client import GHL

DRY = "--dry-run" in sys.argv
HERE = os.path.dirname(__file__)
SPEC = json.load(open(os.path.join(HERE, "..", "spec", "pipelines.json"), encoding="utf-8"))
SNAP = json.load(open(os.path.join(HERE, "..", "..", "00_inputs", "vtr-data-snapshot-2026-07-24.json"), encoding="utf-8"))
IDMAP = os.path.join(HERE, "..", "spec", "pipelines-idmap.json")

# stages reales por pipeline (snapshot)
snap_stages = collections.defaultdict(set)
for d in SNAP[0]["json"]["clientify"]["deals"]:
    if d.get("pipeline_stage_desc"):
        snap_stages[d.get("pipeline_desc")].add(d["pipeline_stage_desc"])

# validación de fidelidad de nombres
print("=== Validación stages spec vs snapshot ===")
problems = 0
for p in SPEC["pipelines"]:
    cl = p.get("clientify")
    if not cl or p.get("operativo") or "+" in (cl or ""):
        continue
    real = snap_stages.get(cl, set())
    spec_set = set(p["stages"])
    missing = real - spec_set          # en snapshot, faltan en spec
    extra = spec_set - real            # en spec, no en snapshot
    if missing or extra:
        problems += 1
        print(f"  ⚠️ {p['name']}: faltan_en_spec={sorted(missing)} extra_en_spec={sorted(extra)}")
if not problems:
    print("  ✅ todos los stages de los comerciales coinciden verbatim con el snapshot")

g = GHL(); LOC = g.location_id
st, d = g.get("/opportunities/pipelines", params={"locationId": LOC})
have = {(p.get("name") or "").strip().lower(): p for p in d.get("pipelines", [])}
print(f"\n=== Pipelines existentes: {[p.get('name') for p in d.get('pipelines',[])]} ===")

idmap = json.load(open(IDMAP)) if os.path.exists(IDMAP) else {}
created = skipped = failed = 0
for p in SPEC["pipelines"]:
    nm = p["name"]; key = nm.strip().lower()
    if key in have:
        ex = have[key]
        idmap[nm] = {"id": ex.get("id"), "legacy": p.get("legacy", False),
                     "stages": {s.get("name"): s.get("id") for s in ex.get("stages", [])}}
        skipped += 1; print(f"  = ya existe: {nm}"); continue
    body = {"name": nm, "locationId": LOC,
            "stages": [{"name": s, "position": i} for i, s in enumerate(p["stages"])]}
    if DRY:
        print(f"  [dry] CREATE {nm} ({len(p['stages'])} stages)"); created += 1; continue
    st, d = g.post("/opportunities/pipelines", body)
    pi = d.get("pipeline", {}) if isinstance(d, dict) else {}
    if st in (200, 201) and pi.get("id"):
        st2, d2 = g.get(f"/opportunities/pipelines?locationId={LOC}")
        rb = next((x for x in d2.get("pipelines", []) if x.get("id") == pi["id"]), pi)
        idmap[nm] = {"id": pi["id"], "legacy": p.get("legacy", False),
                     "stages": {s.get("name"): s.get("id") for s in rb.get("stages", [])}}
        ok = len(rb.get("stages", [])) == len(p["stages"])
        print(f"  {'✅' if ok else '⚠️'} {nm:36} id={pi['id']} stages={len(rb.get('stages',[]))}/{len(p['stages'])}{' [legacy]' if p.get('legacy') else ''}")
        created += 1
    else:
        print(f"  ❌ {nm}: HTTP {st} {json.dumps(d)[:140]}"); failed += 1

if not DRY:
    json.dump(idmap, open(IDMAP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\n→ creados={created} · ya existían={skipped} · fallidos={failed} · idmap total={len(idmap)}")
