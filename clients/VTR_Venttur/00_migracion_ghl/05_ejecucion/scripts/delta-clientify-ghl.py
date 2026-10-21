#!/usr/bin/env python3
"""
D1 · Delta de datos Clientify → GHL (lo que pasó en Clientify después del export del 24/7).

El import del 3-6/9 salió del snapshot `00_inputs/vtr-data-snapshot-2026-07-24.json`. Este script trae el estado de
hoy por la API de Clientify (sólo lectura) y lo compara contra lo que ya se importó (idmaps de `salida-import/`):
  · contactos nuevos       → no están en `contact-idmap.json` por ningún teléfono canónico ni email
  · deals nuevos           → su id no está en `deal-idmap.json`
  · deals modificados      → ya importados, pero en Clientify cambió etapa/pipeline/estado/monto/dueño/nombre
                             respecto del snapshot del 24/7 (lo que se importó)
Reutiliza la normalización del import (`etl-preproceso.py`: teléfono canónico MX, CF de Clientify) y los payloads
de `import-datos.py` (pipelines, etapas, custom fields, dueños), así que lo nuevo queda igual que lo importado.

Uso (sin --apply nada escribe en GHL; --export sólo lee Clientify):
  python3 delta-clientify-ghl.py --export              # baja contactos, deals y companies de Clientify
  python3 delta-clientify-ghl.py --plan                # compara, arma el plan y el reporte (lee GHL sólo en --check-ghl)
  python3 delta-clientify-ghl.py --plan --check-ghl    # además lee de GHL la etapa actual de los deals modificados
  python3 delta-clientify-ghl.py --stage contacts|opps-new|opps-update [--apply] [--limit N]

Escrituras: en serie, 0.5 s entre llamadas (límite 25/10 s y 10.000/día por location). Idempotente: los contactos y
deals creados se suman a los mismos idmaps del import; las actualizaciones se registran en `salida-delta/`.
Una actualización de deal sólo se aplica si en GHL la oportunidad sigue como se importó (si alguien la movió en GHL,
se reporta como conflicto y no se pisa).
"""
import argparse, glob, importlib.util, json, os, re, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
EJ = os.path.dirname(HERE)                                   # 05_ejecucion/
ROOT = os.path.dirname(EJ)                                   # 00_migracion_ghl/
REPO = "/Users/camilo/Downloads/camilo-workspace"
SNAP = os.path.join(ROOT, "00_inputs", "vtr-data-snapshot-2026-07-24.json")
EXPORT_DIR = os.path.join(EJ, "backup-clientify-2026-09", "08-delta-api")   # gitignored
OUTI = os.path.join(EJ, "salida-import")
OUTD = os.path.join(EJ, "salida-delta")
API = "https://api.clientify.net/v1"
HOY = time.strftime("%Y-%m-%d")

sys.path.insert(0, HERE)
_spec = importlib.util.spec_from_file_location("import_datos", os.path.join(HERE, "import-datos.py"))
imp = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(imp)


def env(key):
    for line in open(os.path.join(REPO, ".env")):
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip()


def usar_pipelines_vivos(g=None):
    """Las etapas operativas de GHL (runbook de Rodrigo) son un superset del spec del import: resolver contra GHL."""
    if g is None:
        from _ghl_client import GHL
        g = GHL()
    st, d = g.get("/opportunities/pipelines", params={"locationId": g.location_id})
    if st != 200: raise SystemExit(f"❌ no pude leer los pipelines de GHL: {st}")
    for p in d["pipelines"]:
        imp.pl_idmap[p["name"]] = {"id": p["id"], "stages": {s["name"]: s["id"] for s in p["stages"]}}


def load(p, d=None): return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else d
def save(p, o): json.dump(o, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


# ---------- normalización (misma que etl-preproceso.py) ----------
def canon_phone(raw):
    if raw is None: return None, None
    digits = re.sub(r"\D", "", str(raw))
    if not digits: return None, None
    if digits.startswith("52"):
        rest = digits[2:]
        if rest.startswith("1") and len(rest) == 11: return "+521" + rest[1:], None
        if len(rest) == 10: return "+521" + rest, None
        return "+" + digits, "malformado_mx"
    if 10 <= len(digits) <= 15:
        return "+" + digits, ("sin_cc" if len(digits) == 10 else None)
    return "+" + digits, "malformado"


def canons_of(ct):
    out = set()
    for p in ct.get("phones", []) or []:
        cp, flag = canon_phone(p.get("phone"))
        if cp and not flag: out.add(cp)
    return sorted(out)


def emails_of(ct):
    return [e["email"].strip() for e in ct.get("emails", []) or [] if (e.get("email") or "").strip()]


CLIENTIFY_CF_MAP = {"Timezone": "clientify_timezone", "Guests": "Guests", "Date": "Date",
                    "Textinput": "Textinput", "File": "File", "Task-Id": "Task-Id",
                    "Contact-Type": "contact_type", "Nombre del estudiante": "nombre_estudiante",
                    "Procesos Internos": "procesos_internos"}


def build_contact(canon, ct):
    """Igual que build_contact de etl-preproceso.py para un contacto sólo-Clientify."""
    emails = emails_of(ct)
    r = {"canon_phone": canon, "firstName": ct.get("first_name"), "lastName": ct.get("last_name") or "",
         "email": emails[0] if emails else None, "owner_email": ct.get("owner"),
         "source_airtable": False, "source_clientify": True, "cf": {}, "clientify_id": ct.get("id")}
    cf = r["cf"]
    def put(k, v):
        if v not in (None, "", [], {}): cf[k] = v
    cf["link_enviado"] = False
    cf["outreach_enviado"] = False
    put("fecha_alta_original", ct.get("created"))
    put("owner_clientify", ct.get("owner"))
    put("status_clientify", ct.get("status"))
    put("canal_origen", ct.get("channel"))
    put("medium", ct.get("medium"))
    put("rfc", ct.get("taxpayer_identification_number"))
    put("title", ct.get("title"))
    if ct.get("gdpr_accept"): cf["gdpr_accept"] = True
    put("gdpr_acceptance_date", ct.get("gdpr_acceptance_date"))
    put("gdpr_revoke_date", ct.get("gdpr_revoke_date"))
    if ct.get("disclaimer"): cf["disclaimer"] = True
    for c in ct.get("custom_fields", []) or []:
        nm = c.get("field") or c.get("name")
        if nm in CLIENTIFY_CF_MAP: put(CLIENTIFY_CF_MAP[nm], c.get("value"))
    return r


CAMPOS_DEAL = ("pipeline_desc", "pipeline_stage_desc", "status_desc", "amount", "owner_name", "name")


def opp_row(dl):
    cp, _ = canon_phone(dl.get("contact_phone"))
    return {"deal_id": dl.get("id"), "name": dl.get("name"), "pipeline_desc": dl.get("pipeline_desc"),
            "pipeline_stage_desc": dl.get("pipeline_stage_desc"),
            "status": imp_status(dl.get("status_desc")), "monetaryValue": dl.get("amount"),
            "moneda": dl.get("currency"), "owner_name": dl.get("owner_name"),
            "contact_canon_phone": cp, "contact_email": dl.get("contact_email"),
            "probabilidad": dl.get("probability"), "cierre_esperado": dl.get("expected_closed_date"),
            "cierre_real": dl.get("actual_closed_date"), "modified": dl.get("modified"),
            "status_desc": dl.get("status_desc"),
            "clientify": {k: dl.get(k) for k in CAMPOS_DEAL}}


def imp_status(s):
    return {"Open": "open", "Won": "won", "Lost": "lost", "Expired": "abandoned"}.get(s, "open")


# ---------- export ----------
def export():
    key = env("VTR_CLIENTIFY_API_KEY")
    if not key: raise SystemExit("❌ falta VTR_CLIENTIFY_API_KEY en .env")
    H = {"Authorization": f"Token {key}", "Accept": "application/json", "User-Agent": "curl/8.7.1"}
    os.makedirs(EXPORT_DIR, exist_ok=True)
    for kind in ("contacts", "deals", "companies"):
        rows, url = [], f"{API}/{kind}/?page_size=100"
        while url:
            for i in range(4):
                try:
                    d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=90)); break
                except Exception as e:
                    if i == 3: raise
                    time.sleep(3 * (i + 1))
            rows += d["results"]; url = d.get("next"); time.sleep(0.3)
        p = os.path.join(EXPORT_DIR, f"{kind}-{HOY}.json"); save(p, rows)
        print(f"{kind}: {len(rows)} (API count {d.get('count')}) → {os.path.relpath(p, EJ)}")


def latest(kind):
    fs = sorted(glob.glob(os.path.join(EXPORT_DIR, f"{kind}-*.json")))
    if not fs: raise SystemExit(f"❌ no hay export de {kind}: correr --export")
    return load(fs[-1]), os.path.basename(fs[-1])


# ---------- plan ----------
def plan(check_ghl=False):
    contacts, fc = latest("contacts"); deals, fd = latest("deals"); companies, fco = latest("companies")
    snap = load(SNAP)[0]["json"]["clientify"]
    snap_deals = {d["id"]: d for d in snap["deals"]}
    snap_contacts = {c["id"] for c in snap["contacts"]}
    upd = load(os.path.join(OUTD, "deals-actualizados.json"), {})
    creados = load(os.path.join(OUTD, "deals-creados.json"), {})
    cmap = load(os.path.join(OUTI, "contact-idmap.json"), {})
    dmap = load(os.path.join(OUTI, "deal-idmap.json"), {})
    bmap = load(os.path.join(OUTI, "business-idmap.json"), {})
    os.makedirs(OUTD, exist_ok=True)
    usar_pipelines_vivos()

    # contactos
    nuevos, seen, sin_id, ya = [], set(), 0, 0
    for ct in sorted(contacts, key=lambda c: c.get("created") or ""):
        canons, emails = canons_of(ct), emails_of(ct)
        keys = canons + emails
        if not keys: sin_id += 1; continue
        if any(k in cmap for k in keys): ya += 1; continue
        if any(k in seen for k in keys): continue          # otro contacto nuevo con el mismo teléfono/email
        seen.update(keys)
        nuevos.append(build_contact(canons[0] if canons else None, ct))
    nuevos_desde_snap = sum(1 for r in nuevos if r["clientify_id"] not in snap_contacts)

    # deals
    deals_nuevos, deals_mod, sin_pipeline = [], [], []
    for dl in deals:
        did = str(dl["id"])
        if did not in dmap:
            r = opp_row(dl); deals_nuevos.append(r)
            pid, sid = imp.resolve_pipeline(r["pipeline_desc"], r["pipeline_stage_desc"])
            if not pid or not sid: sin_pipeline.append((did, r["pipeline_desc"], r["pipeline_stage_desc"]))
            continue
        # base = lo que hoy tiene GHL según nuestros registros: último update del delta › creación del delta › 24/7
        old = (upd.get(did) or {}).get("clientify") or creados.get(did) or snap_deals.get(dl["id"])
        if not old: continue
        cambios = {k: [old.get(k), dl.get(k)] for k in CAMPOS_DEAL if str(old.get(k)) != str(dl.get(k))}
        if cambios:
            r = opp_row(dl); r["opp_id"] = dmap[did]; r["cambios"] = cambios
            r["importado"] = opp_row(old)
            pid, sid = imp.resolve_pipeline(r["pipeline_desc"], r["pipeline_stage_desc"])
            if not pid or not sid: sin_pipeline.append((did, r["pipeline_desc"], r["pipeline_stage_desc"]))
            deals_mod.append(r)

    # contactos de los deals nuevos: ¿resuelven a un contacto (importado o nuevo)?
    claves_nuevas = {k for r in nuevos for k in [r["canon_phone"], r["email"]] if k}
    sin_contacto = [r["deal_id"] for r in deals_nuevos
                    if not any(k in cmap or k in claves_nuevas for k in [r["contact_canon_phone"], r["contact_email"]] if k)]

    companies_nuevas = [c["name"].strip() for c in companies if (c.get("name") or "").strip() and c["name"].strip() not in bmap]

    conflictos = []
    if check_ghl:
        from _ghl_client import GHL
        g = GHL()
        for r in deals_mod:
            st, d = g.get(f"/opportunities/{r['opp_id']}")
            o = (d or {}).get("opportunity", {}) if isinstance(d, dict) else {}
            pid, sid = imp.resolve_pipeline(r["importado"]["pipeline_desc"], r["importado"]["pipeline_stage_desc"])
            r["ghl_actual"] = {"pipelineId": o.get("pipelineId"), "pipelineStageId": o.get("pipelineStageId"),
                               "status": o.get("status"), "http": st}
            r["ghl_como_se_importo"] = (o.get("pipelineId") == pid and o.get("pipelineStageId") == sid
                                        and o.get("status") == r["importado"]["status"])
            if not r["ghl_como_se_importo"]: conflictos.append(r["deal_id"])
            time.sleep(0.25)

    plan_ = {"fecha": HOY, "exports": [fc, fd, fco], "contactos_nuevos": nuevos, "deals_nuevos": deals_nuevos,
             "deals_modificados": deals_mod, "sin_pipeline": sin_pipeline, "deals_sin_contacto": sin_contacto,
             "companies_nuevas": companies_nuevas, "conflictos_ghl": conflictos, "check_ghl": check_ghl}
    save(os.path.join(OUTD, "plan.json"), plan_)

    from collections import Counter
    mod_tipo = Counter(k for r in deals_mod for k in r["cambios"])
    L = [f"# D1 · Plan del delta Clientify → GHL · {HOY}", "",
         f"Exports: {fc}, {fd}, {fco} · base: snapshot 24/7 + idmaps del import (3-6/9).", "",
         "| | Cantidad |", "|---|---:|",
         f"| Contactos en Clientify hoy | {len(contacts)} |",
         f"| · ya importados (teléfono o email en el idmap) | {ya} |",
         f"| · sin teléfono ni email (no importables) | {sin_id} |",
         f"| · **nuevos a crear** | **{len(nuevos)}** ({nuevos_desde_snap} creados después del 24/7) |",
         f"| Deals en Clientify hoy | {len(deals)} |",
         f"| · **nuevos a crear** | **{len(deals_nuevos)}** |",
         f"| · **ya importados con cambios desde el 24/7** | **{len(deals_mod)}** |",
         f"| · deals nuevos sin contacto resoluble | {len(sin_contacto)} |",
         f"| · etapa/pipeline sin equivalente en GHL | {len(sin_pipeline)} |",
         f"| Companies nuevas | {len(companies_nuevas)} |", "",
         "Cambios en los deals ya importados, por campo: " + ", ".join(f"{k} {v}" for k, v in mod_tipo.most_common()), ""]
    if check_ghl:
        L += [f"Chequeo contra GHL: {len(deals_mod) - len(conflictos)} siguen como se importaron · "
              f"**{len(conflictos)} ya cambiaron en GHL** (no se pisan).", ""]
    if sin_pipeline:
        L += ["Etapas sin equivalente:", ""] + [f"- deal {a}: {b} / {c}" for a, b, c in sin_pipeline[:40]] + [""]
    est = len(nuevos) + len(deals_nuevos) + 2 * len(deals_mod)
    L += [f"Escrituras estimadas a GHL: ~{est} (+ lecturas). A 0.5 s ≈ {est // 120 + 1} min."]
    open(os.path.join(OUTD, f"plan-{HOY}.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


# ---------- apply ----------
def apply_stage(stage, apply, limit):
    from _ghl_client import GHL
    p = load(os.path.join(OUTD, "plan.json"))
    if not p: raise SystemExit("❌ correr --plan primero")
    g = GHL(); LOC = g.location_id
    usar_pipelines_vivos(g)
    byemail = imp.umap["by_email"]
    cmap_p = os.path.join(OUTI, "contact-idmap.json"); cmap = load(cmap_p, {})
    dmap_p = os.path.join(OUTI, "deal-idmap.json"); dmap = load(dmap_p, {})
    upd_p = os.path.join(OUTD, "deals-actualizados.json"); upd = load(upd_p, {})
    creados_p = os.path.join(OUTD, "deals-creados.json"); creados = load(creados_p, {})
    ok = skip = fail = 0

    if stage == "contacts":
        rows = p["contactos_nuevos"][:limit or None]
        for r in rows:
            keys = [k for k in (r["canon_phone"], r["email"]) if k]
            if any(k in cmap for k in keys): skip += 1; continue
            body = imp.contact_payload(r, LOC)
            uid = byemail.get((r.get("owner_email") or "").lower())
            if uid: body["assignedTo"] = uid
            if not apply: ok += 1; continue
            st, d = g.post("/contacts/upsert", body)
            c = (d.get("contact") or {}) if isinstance(d, dict) else {}
            if c.get("id"):
                for k in keys: cmap[k] = c["id"]
                ok += 1
            else:
                fail += 1; print(f"FAIL {keys}: {st} {json.dumps(d)[:160]}")
            if ok % 25 == 0: save(cmap_p, cmap)
            time.sleep(0.5)
        if apply: save(cmap_p, cmap)

    elif stage == "opps-new":
        rows = p["deals_nuevos"][:limit or None]
        for r in rows:
            did = str(r["deal_id"])
            if did in dmap: skip += 1; continue
            cid = cmap.get(r["contact_canon_phone"]) or cmap.get(r["contact_email"])
            if not cid: skip += 1; print(f"sin contacto: deal {did}"); continue
            body = imp.opp_payload(r, cid, LOC)
            if not body.get("pipelineId") or not body.get("pipelineStageId"):
                skip += 1; print(f"sin pipeline: deal {did} {r['pipeline_desc']} / {r['pipeline_stage_desc']}"); continue
            if not apply: ok += 1; continue
            st, d = g.post("/opportunities/", body)
            o = (d.get("opportunity") or {}) if isinstance(d, dict) else {}
            if o.get("id"):
                dmap[did] = o["id"]; ok += 1
                creados[did] = {k: r.get(k) for k in ("name", "pipeline_desc", "pipeline_stage_desc", "owner_name")}
                creados[did].update({"status_desc": r.get("status_desc"), "amount": r.get("monetaryValue")})
            else: fail += 1; print(f"FAIL deal {did}: {st} {json.dumps(d)[:160]}")
            if ok % 25 == 0: save(dmap_p, dmap); save(creados_p, creados)
            time.sleep(0.5)
        if apply: save(dmap_p, dmap); save(creados_p, creados)

    elif stage == "opps-update":
        rows = p["deals_modificados"][:limit or None]
        for r in rows:
            did = str(r["deal_id"])
            if (upd.get(did) or {}).get("modified") == r["modified"]: skip += 1; continue
            pid, sid = imp.resolve_pipeline(r["pipeline_desc"], r["pipeline_stage_desc"])
            if not pid or not sid: skip += 1; print(f"sin pipeline: deal {did}"); continue
            ipid, isid = imp.resolve_pipeline(r["importado"]["pipeline_desc"], r["importado"]["pipeline_stage_desc"])
            st, d = g.get(f"/opportunities/{r['opp_id']}")
            o = (d.get("opportunity") or {}) if isinstance(d, dict) else {}
            if not (o.get("pipelineId") == ipid and o.get("pipelineStageId") == isid
                    and o.get("status") == r["importado"]["status"]):
                skip += 1; print(f"conflicto (cambió en GHL, no se pisa): deal {did} opp {r['opp_id']}"); continue
            body = {"pipelineId": pid, "pipelineStageId": sid, "status": r["status"],
                    "name": r.get("name") or "Deal", "monetaryValue": imp._num(r.get("monetaryValue"))}
            aid = imp.umap["by_name"].get(r.get("owner_name"))
            if aid: body["assignedTo"] = aid
            if not apply: ok += 1; continue
            st, d = g.put(f"/opportunities/{r['opp_id']}", body)
            if st in (200, 201):
                upd[did] = {"opp_id": r["opp_id"], "cambios": r["cambios"], "modified": r["modified"],
                            "at": time.strftime("%Y-%m-%dT%H:%M:%S"), "clientify": r["clientify"]}
                ok += 1
            else: fail += 1; print(f"FAIL update deal {did}: {st} {json.dumps(d)[:160]}")
            if ok % 25 == 0: save(upd_p, upd)
            time.sleep(0.5)
        if apply: save(upd_p, upd)

    print(f"{'APPLY' if apply else 'DRY'} {stage}: ok={ok} saltados={skip} fallidos={fail}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", action="store_true")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--check-ghl", action="store_true")
    ap.add_argument("--stage", choices=["contacts", "opps-new", "opps-update"])
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    if a.export: export()
    if a.plan: plan(a.check_ghl)
    if a.stage: apply_stage(a.stage, a.apply, a.limit)
