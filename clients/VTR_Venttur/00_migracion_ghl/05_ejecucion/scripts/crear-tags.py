"""
FASE 1.3 · Crear los 4 tags canónicos de ManyChat (02 §2.6). `wpp` NO se crea (huérfano).
Idempotente: GET existentes → crea los que faltan. Escribe idmap a spec/tags-idmap.json.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _ghl_client import GHL

TAGS = ["RESCATE_PROGRAMA_NO_MAPEADO", "LINK_ABANDONADO_FRIO", "seguimiento_agenda", "seguimiento"]
g = GHL(); LOC = g.location_id
IDMAP = os.path.join(os.path.dirname(__file__), "..", "spec", "tags-idmap.json")

st, d = g.get(f"/locations/{LOC}/tags")
have = {(t.get("name") or "").strip().lower(): t for t in d.get("tags", [])}
print(f"Tags existentes: {[t.get('name') for t in d.get('tags',[])]}")
idmap = {}
for nm in TAGS:
    if nm.lower() in have:
        t = have[nm.lower()]; idmap[nm] = t.get("id"); print(f"  = ya existe: {nm} ({t.get('id')})"); continue
    st, d = g.post(f"/locations/{LOC}/tags", {"name": nm})
    t = d.get("tag", {}) if isinstance(d, dict) else {}
    if st in (200, 201) and t.get("id"):
        idmap[nm] = t["id"]; print(f"  ✅ creado: {nm} ({t['id']})")
    else:
        print(f"  ❌ {nm}: HTTP {st} {json.dumps(d)[:120]}")
json.dump(idmap, open(IDMAP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
# read-back
st, d = g.get(f"/locations/{LOC}/tags")
print("Read-back total tags:", [t.get("name") for t in d.get("tags", [])])
