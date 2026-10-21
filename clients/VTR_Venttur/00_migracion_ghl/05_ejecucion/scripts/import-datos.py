"""
FASE 3 · Import a GHL (companies → contacts → opportunities). Idempotente.
- assignedTo NO se setea (workaround B-03): el owner real se preserva en el CF `owner_clientify`;
  se reasigna a assignedTo cuando existan los usuarios.
- Idempotencia: business-idmap (name→id), contact-idmap (phone/email→id), deal-idmap (deal_id→oppId)
  en salida-import/. Re-correr saltea lo ya hecho.
POR DEFECTO --dry-run. --apply escribe.
Uso: python3 import-datos.py --stage companies|contacts|opportunities [--apply] [--limit N]
"""
import argparse, json, os, re, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from _ghl_client import GHL

HERE = os.path.dirname(__file__)
SPEC = os.path.join(HERE, "..", "spec")
ETL = os.path.join(HERE, "..", "salida-etl")
OUTI = os.path.join(HERE, "..", "salida-import")
os.makedirs(OUTI, exist_ok=True)

def load(p, d=None): return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else d
def save(p, o): json.dump(o, open(p, "w", encoding="utf-8"), ensure_ascii=False)
def jsonl(name):
    p = os.path.join(ETL, name)
    return [json.loads(l) for l in open(p, encoding="utf-8")] if os.path.exists(p) else []

cf_idmap = load(os.path.join(SPEC, "custom-fields-idmap.json"), {"contact": {}, "opportunity": {}})
pl_idmap = load(os.path.join(SPEC, "pipelines-idmap.json"), {})
umap = load(os.path.join(SPEC, "usuarios-idmap.json"), {"by_email": {}, "by_name": {}})

ESTADO_MAP = {"Conversación interrumpida": "Interrumpida"}

def norm_date(v):
    if not v: return None
    s = str(v)
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)          # ISO
    if m: return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)      # D/M/YYYY (Airtable)
    if m: return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    return None

def cf_val(model, name, value):
    meta = cf_idmap.get(model, {}).get(name)
    if not meta: return None
    dt = meta["dataType"]
    if dt == "CHECKBOX":
        return {"id": meta["id"], "value": ["true"]} if value else None
    if value in (None, "", []): return None
    if dt == "NUMERICAL":
        try: value = float(value); value = int(value) if value == int(value) else value
        except (ValueError, TypeError): return None
    elif dt == "DATE":
        value = norm_date(value)
        if not value: return None
    elif dt == "SINGLE_OPTIONS" and name == "estado_conversacion":
        value = ESTADO_MAP.get(value, value)
    return {"id": meta["id"], "value": value}

def resolve_pipeline(pdesc, sdesc):
    if not pdesc or pdesc == "«sin pipeline»": pname, sname = "Sin asignar / Default", "Sin etapa"
    elif pdesc == "Por defecto": pname, sname = "Sin asignar / Default", sdesc or "Propuesta presentada"
    else: pname, sname = pdesc, sdesc
    pl = pl_idmap.get(pname)
    if not pl: return None, None
    return pl["id"], pl["stages"].get(sname)

def contact_payload(r, LOC):
    b = {"locationId": LOC, "firstName": r.get("firstName") or "", "lastName": r.get("lastName") or ""}
    if r.get("canon_phone"): b["phone"] = r["canon_phone"]
    if r.get("email"): b["email"] = r["email"]
    cfs = [e for k, v in (r.get("cf") or {}).items() for e in [cf_val("contact", k, v)] if e]
    if cfs: b["customFields"] = cfs
    return b

def opp_payload(r, contact_id, LOC):
    pid, sid = resolve_pipeline(r.get("pipeline_desc"), r.get("pipeline_stage_desc"))
    b = {"locationId": LOC, "pipelineId": pid, "pipelineStageId": sid, "contactId": contact_id,
         "name": r.get("name") or "Deal", "status": r.get("status") or "open",
         "monetaryValue": _num(r.get("monetaryValue"))}
    aid = umap["by_name"].get(r.get("owner_name"))   # Diego Matus → Juan José (remap en el idmap)
    if aid: b["assignedTo"] = aid
    cfs = []
    for k, v in [("moneda", r.get("moneda")), ("probabilidad", r.get("probabilidad")),
                 ("cierre_esperado", r.get("cierre_esperado")), ("cierre_real", r.get("cierre_real")),
                 ("owner_clientify", r.get("owner_name"))]:
        e = cf_val("opportunity", k, v)
        if e: cfs.append(e)
    if cfs: b["customFields"] = cfs
    return b

def _num(v):
    try: return float(v)
    except (ValueError, TypeError): return 0

def log(stage, msg):
    with open(os.path.join(OUTI, f"progress-{stage}.log"), "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["companies", "contacts", "opportunities"])
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    g = GHL(); LOC = g.location_id
    apply = a.apply

    # ---------------- COMPANIES ----------------
    if a.stage == "companies":
        rows = jsonl("companies.jsonl"); rows = rows[:a.limit] if a.limit else rows
        idmap = load(os.path.join(OUTI, "business-idmap.json"), {})
        # cargar existentes
        st, d = g.get("/businesses/", params={"locationId": LOC})
        for b in d.get("businesses", []): idmap.setdefault((b.get("name") or "").strip(), b.get("id"))
        created = skipped = failed = 0
        for r in rows:
            nm = (r.get("name") or "").strip()
            if not nm or nm in idmap: skipped += 1; continue
            if not apply: created += 1; continue
            st, d = g.post("/businesses/", {"name": nm, "locationId": LOC})
            bid = (d.get("business") or d or {}).get("id") if isinstance(d, dict) else None
            if bid: idmap[nm] = bid; created += 1
            else: failed += 1; log("companies", f"FAIL {nm}: {st} {json.dumps(d)[:120]}")
            time.sleep(0.08)
        if apply: save(os.path.join(OUTI, "business-idmap.json"), idmap)
        log("companies", f"{'APPLY' if apply else 'DRY'} companies: creados={created} saltados={skipped} fallidos={failed} idmap={len(idmap)}")
        return

    # ---------------- CONTACTS ----------------
    if a.stage == "contacts":
        rows = jsonl("contacts.jsonl"); rows = rows[:a.limit] if a.limit else rows
        idmap = load(os.path.join(OUTI, "contact-idmap.json"), {})
        created = skipped = noid = failed = 0
        for i, r in enumerate(rows):
            key = r.get("canon_phone") or r.get("email")
            if not key: noid += 1; continue
            if key in idmap: skipped += 1; continue
            if not apply: created += 1; continue
            st, d = g.post("/contacts/upsert", contact_payload(r, LOC))
            c = (d.get("contact") or {}) if isinstance(d, dict) else {}
            if c.get("id"):
                if r.get("canon_phone"): idmap[r["canon_phone"]] = c["id"]
                if r.get("email"): idmap[r["email"]] = c["id"]
                created += 1
            else:
                failed += 1; log("contacts", f"FAIL {key}: {st} {json.dumps(d)[:140]}")
            if apply and created % 25 == 0:
                save(os.path.join(OUTI, "contact-idmap.json"), idmap)
                log("contacts", f"... {i+1}/{len(rows)} · creados={created} saltados={skipped} sin-id={noid} fallidos={failed}")
            time.sleep(0.5)
        if apply: save(os.path.join(OUTI, "contact-idmap.json"), idmap)
        log("contacts", f"{'APPLY' if apply else 'DRY'} contacts: creados={created} saltados={skipped} sin-identificador={noid} fallidos={failed} idmap={len(idmap)}")
        return

    # ---------------- OPPORTUNITIES ----------------
    if a.stage == "opportunities":
        rows = jsonl("opportunities.jsonl"); rows = rows[:a.limit] if a.limit else rows
        cmap = load(os.path.join(OUTI, "contact-idmap.json"), {})
        dmap = load(os.path.join(OUTI, "deal-idmap.json"), {})
        created = skipped = nocontact = failed = 0
        for i, r in enumerate(rows):
            did = str(r.get("deal_id"))
            if did in dmap: skipped += 1; continue
            cid = cmap.get(r.get("contact_canon_phone")) or cmap.get(r.get("contact_email"))
            if not cid and apply and r.get("contact_canon_phone"):  # fallback: search por teléfono
                st, d = g.post("/contacts/search", {"locationId": LOC, "pageLimit": 1,
                    "filters": [{"group": "OR", "filters": [{"field": "phone", "operator": "eq", "value": r["contact_canon_phone"]}]}]})
                hits = d.get("contacts", []) if isinstance(d, dict) else []
                if hits: cid = hits[0].get("id")
            if not cid: nocontact += 1; continue
            if not apply: created += 1; continue
            st, d = g.post("/opportunities/", opp_payload(r, cid, LOC))
            o = (d.get("opportunity") or {}) if isinstance(d, dict) else {}
            if o.get("id"): dmap[did] = o["id"]; created += 1
            else: failed += 1; log("opportunities", f"FAIL deal {did}: {st} {json.dumps(d)[:140]}")
            if apply and created % 25 == 0:
                save(os.path.join(OUTI, "deal-idmap.json"), dmap)
                log("opportunities", f"... {i+1}/{len(rows)} · creados={created} saltados={skipped} sin-contacto={nocontact} fallidos={failed}")
            time.sleep(0.5)
        if apply: save(os.path.join(OUTI, "deal-idmap.json"), dmap)
        log("opportunities", f"{'APPLY' if apply else 'DRY'} opportunities: creados={created} saltados={skipped} sin-contacto={nocontact} fallidos={failed} idmap={len(dmap)}")
        return

if __name__ == "__main__":
    main()
