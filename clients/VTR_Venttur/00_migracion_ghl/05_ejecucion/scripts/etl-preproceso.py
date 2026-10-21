"""
FASE 2 · Pre-proceso / ETL (VTR → GHL). NO escribe en GHL.
Construye la unión deduplicada Airtable Leads + Clientify → ~8.575 GHL Contacts.
- Canonicaliza teléfono MX (52↔521 → +521<nac10>); no-MX E.164.
- Remapea `Programa interés` → 8 canónicos.
- Merge por teléfono canónico (+ FK corroboración + email fallback phone-less).
- Precedencia de campos por dominio (identidad→Clientify, estado bot→Airtable...).
- Mide población de los 6 CF genéricos de Clientify.
- Dedup de deals por contacto+pipeline (OPPORTUNITY_NO_DUPLICATE).
Salidas: salida-etl/{contacts,opportunities,companies}.jsonl + reporte de conteos.
"""
import csv, json, os, re, sys, collections

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")   # 00_migracion_ghl/
LEADS = os.path.join(ROOT, "00_inputs", "airtable-csvs", "leads.csv")
SNAP = os.path.join(ROOT, "00_inputs", "vtr-data-snapshot-2026-07-24.json")
OUT = os.path.join(os.path.dirname(__file__), "..", "salida-etl")
os.makedirs(OUT, exist_ok=True)

# ---------- helpers ----------
def canon_phone(raw):
    """→ (canonical +E.164, flag). MX colapsa 52/521 a +521<nac10>."""
    if raw is None:
        return None, None
    digits = re.sub(r"\D", "", str(raw))
    if not digits:
        return None, None
    if digits.startswith("52"):
        rest = digits[2:]
        if rest.startswith("1") and len(rest) == 11:
            return "+521" + rest[1:], None
        if len(rest) == 10:
            return "+521" + rest, None
        return "+" + digits, "malformado_mx"
    if 10 <= len(digits) <= 15:
        return "+" + digits, ("sin_cc" if len(digits) == 10 else None)
    return "+" + digits, "malformado"

PROG_MAP = {
    "Boarding School": "Internados",
    "Boarding IA": "Internados",
    "AA Familiar IA": "Intercambio académico con familias",
    "Pathway IA": "Pathway Alemania",
    "Summer Camp IA": "Campamentos de verano",
    "Gap Year IA": "Gap Year / Estudia y Trabaja",
    "Automatización - Comentarios": None,   # no es programa
    "No definido": None, "": None,
}
def remap_programa(v):
    v = (v or "").strip()
    return PROG_MAP.get(v, "__UNKNOWN__" if v else None)

STATUS_MAP = {  # Clientify status_desc → GHL opportunity status
    "Open": "open", "Won": "won", "Lost": "lost", "Expired": "abandoned",
}

# ---------- load ----------
clientify = json.load(open(SNAP, encoding="utf-8"))[0]["json"]["clientify"]
c_contacts, c_deals, c_companies = clientify["contacts"], clientify["deals"], clientify["companies"]

with open(LEADS, encoding="utf-8-sig") as f:
    leads = list(csv.DictReader(f))

report = []
def R(s): report.append(s); print(s)

R(f"Airtable Leads: {len(leads)} · Clientify contacts: {len(c_contacts)} deals: {len(c_deals)} companies: {len(c_companies)}")

# ---------- 1) canonicalizar + índices ----------
# Clientify: cada contacto puede tener varios phones → todas las variantes canónicas apuntan al mismo
cl_by_phone = {}          # canon_phone -> clientify contact (primero gana)
cl_by_email = {}          # email lower -> clientify contact
cl_phoneless = []
mal_mx = 0
for ct in c_contacts:
    canons = set()
    for p in ct.get("phones", []) or []:
        cp, flag = canon_phone(p.get("phone"))
        if flag == "malformado_mx":
            mal_mx += 1
        if cp and not flag:
            canons.add(cp)
    ct["_canons"] = sorted(canons)
    for cp in canons:
        cl_by_phone.setdefault(cp, ct)
    for e in ct.get("emails", []) or []:
        em = (e.get("email") or "").strip().lower()
        if em:
            cl_by_email.setdefault(em, ct)
    if not canons:
        cl_phoneless.append(ct)

# Airtable: 1 phone por lead (columna id)
at_by_phone = {}
at_prog_counts = collections.Counter()
at_unknown_prog = collections.Counter()
for ld in leads:
    cp, flag = canon_phone(ld.get("id"))
    ld["_canon"] = cp if not flag else None
    ld["_prog"] = remap_programa(ld.get("Programa interés"))
    if ld["_prog"] == "__UNKNOWN__":
        at_unknown_prog[ld.get("Programa interés")] += 1
    elif ld["_prog"]:
        at_prog_counts[ld["_prog"]] += 1
    if ld["_canon"]:
        at_by_phone.setdefault(ld["_canon"], ld)

R(f"\nClientify: teléfonos canónicos únicos={len(cl_by_phone)} · phone-less={len(cl_phoneless)} · emails únicos={len(cl_by_email)} · variantes MX malformadas={mal_mx}")
R(f"Airtable: teléfonos canónicos únicos={len(at_by_phone)} (de {len(leads)} leads)")

# ---------- 2/3) merge por teléfono canónico ----------
inter = set(cl_by_phone) & set(at_by_phone)
only_at = set(at_by_phone) - set(cl_by_phone)
only_cl = set(cl_by_phone) - set(at_by_phone)
R(f"\nMerge por teléfono: intersección Airtable∩Clientify={len(inter)} · solo-Airtable={len(only_at)} · solo-Clientify={len(only_cl)}")

# ---------- 4) corroboración por FK ----------
fk_cl = sum(1 for ld in leads if (ld.get("ID Clientify") or "").strip())
fk_mc = sum(1 for ld in leads if (ld.get("ID Manychat") or "").strip())
R(f"FK Airtable: ID Clientify={fk_cl} ({100*fk_cl//len(leads)}%) · ID Manychat={fk_mc} ({100*fk_mc//len(leads)}%)")

# ---------- 5) phone-less: match por email ----------
pl_by_email = pl_orphan = 0
at_emails = {(ld.get("Email") or "").strip().lower(): ld for ld in leads if (ld.get("Email") or "").strip()}
for ct in cl_phoneless:
    matched = any((e.get("email") or "").strip().lower() in at_emails for e in ct.get("emails", []) or [])
    if [e for e in ct.get("emails", []) or [] if e.get("email")]:
        pl_by_email += 1 if matched else 0
    if not matched and not ([e for e in ct.get("emails", []) or [] if e.get("email")]):
        pl_orphan += 1

# ---------- 6) población de los 6 CF genéricos ----------
GEN6 = ["Task-Id", "File", "Guests", "Date", "Timezone", "Textinput"]
gen_pop = collections.Counter()
for ct in c_contacts:
    for cf in ct.get("custom_fields", []) or []:
        nm = cf.get("name") or cf.get("field") or ""
        val = cf.get("value")
        if nm in GEN6 and val not in (None, "", [], {}):
            gen_pop[nm] += 1
R("\nPoblación de los 6 CF genéricos de Clientify (crear solo los poblados):")
for g in GEN6:
    R(f"  {g}: {gen_pop.get(g,0)}")

# ---------- 7) deals: status map + moneda + dedup por contacto+pipeline ----------
status_counts = collections.Counter()
curr_counts = collections.Counter()
by_contact_pipeline = collections.Counter()
deal_prog_pipeline = collections.Counter()
for dl in c_deals:
    status_counts[dl.get("status_desc")] += 1
    curr_counts[dl.get("currency")] += 1
    ckey = (dl.get("contact") or dl.get("contact_phone") or dl.get("contact_email"), dl.get("pipeline_desc"))
    by_contact_pipeline[ckey] += 1
    deal_prog_pipeline[dl.get("pipeline_desc")] += 1
collisions = {k: v for k, v in by_contact_pipeline.items() if v > 1}
n_coll_deals = sum(v for v in collisions.values())
R(f"\nDeals status: {dict(status_counts)}")
R(f"Deals moneda: {dict(curr_counts)}")
R(f"OPPORTUNITY_NO_DUPLICATE: {len(collisions)} contactos con >1 deal en el mismo pipeline "
  f"({n_coll_deals} deals afectados) → requiere 'Allow Duplicate Opportunity' ON o dedupe")

# ---------- 8) universo GHL Contacts ----------
universo_phone = len(set(cl_by_phone) | set(at_by_phone))
universo_total = universo_phone + len(cl_phoneless)
R(f"\nUNIVERSO GHL Contacts: por teléfono={universo_phone} + phone-less={len(cl_phoneless)} = {universo_total} (cota superior)")

# ---------- remapeo de programas (Airtable) ----------
R("\nRemapeo `Programa interés` (Airtable):")
for k, v in sorted(at_prog_counts.items(), key=lambda x: -x[1]):
    R(f"  {k}: {v}")
sin_prog = sum(1 for ld in leads if ld["_prog"] is None)
R(f"  (sin programa): {sin_prog}")
if at_unknown_prog:
    R(f"  ⚠️ valores NO mapeados: {dict(at_unknown_prog)}")

# ---------- salidas jsonl (import-ready, para Fase 3) ----------
# Contacts: unión deduplicada. Clientify identidad + Airtable estado bot.
def merged_contacts():
    seen = set()
    out = []
    # 1) por teléfono (Clientify base)
    for cp, ct in cl_by_phone.items():
        if cp in seen: continue
        seen.add(cp)
        for other in ct["_canons"]: seen.add(other)
        ld = at_by_phone.get(cp)
        out.append(build_contact(cp, ct, ld))
    # 2) solo-Airtable (sin Clientify)
    for cp in only_at:
        if cp in seen: continue
        seen.add(cp)
        out.append(build_contact(cp, None, at_by_phone[cp]))
    # 3) phone-less Clientify
    for ct in cl_phoneless:
        out.append(build_contact(None, ct, None))
    return out

CLIENTIFY_CF_MAP = {"Timezone": "clientify_timezone", "Guests": "Guests", "Date": "Date",
                    "Textinput": "Textinput", "File": "File", "Task-Id": "Task-Id",
                    "Contact-Type": "contact_type", "Nombre del estudiante": "nombre_estudiante",
                    "Procesos Internos": "procesos_internos"}

def build_contact(canon, ct, ld):
    ct = ct or {}; ld = ld or {}
    email = None
    for e in ct.get("emails", []) or []:
        if e.get("email"): email = e["email"]; break
    if not email and ld.get("Email"): email = ld["Email"]
    r = {"canon_phone": canon,
         "firstName": ct.get("first_name") or ld.get("Nombre Completo"),
         "lastName": ct.get("last_name") or "",
         "email": email, "owner_email": ct.get("owner"),
         "source_airtable": bool(ld), "source_clientify": bool(ct), "cf": {}}
    cf = r["cf"]
    def put(k, v):
        if v not in (None, "", [], {}): cf[k] = v
    # --- Airtable (estado del bot) ---
    put("programa_interes", ld.get("_prog"))
    put("tipo_contacto", ld.get("Tipo"))
    put("grado_escolar", ld.get("Grado Escolar"))
    put("nivel_ingles", ld.get("Nivel Inglés"))
    put("inicio_deseado", ld.get("Inicio Deseado"))
    put("fuente_lead", ld.get("Fuente lead"))
    put("origen", ld.get("Origen"))
    put("ad_name", ld.get("Ad Name"))
    put("platform", ld.get("Platform"))
    put("lead_score", ld.get("Lead Score"))
    put("tipo_lead", ld.get("Tipo lead"))
    put("estado_conversacion", ld.get("Estado conversación"))
    cf["link_enviado"] = (ld.get("Link asesoría enviado") or "").strip() != ""
    cf["outreach_enviado"] = (ld.get("Outreach Form Meta enviado") or "").strip() != ""
    put("outreach_enviado_at", ld.get("Outreach Form Meta enviado at"))
    put("toques_enviados", ld.get("Toques enviados"))
    put("ultimo_toque_at", ld.get("Ultimo toque at"))
    put("touch1_programado_at", ld.get("Touch 1 programado at"))
    put("ultima_actividad", ld.get("Última actividad"))
    # --- Clientify (identidad/comercial) ---
    put("fecha_alta_original", ct.get("created") or ld.get("Creada"))
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
    # --- Clientify per-record custom_fields (field/value) ---
    for c in ct.get("custom_fields", []) or []:
        nm = c.get("field") or c.get("name")
        if nm in CLIENTIFY_CF_MAP:
            put(CLIENTIFY_CF_MAP[nm], c.get("value"))
    return r

contacts_out = merged_contacts()
with open(os.path.join(OUT, "contacts.jsonl"), "w", encoding="utf-8") as f:
    for r in contacts_out: f.write(json.dumps(r, ensure_ascii=False) + "\n")

with open(os.path.join(OUT, "opportunities.jsonl"), "w", encoding="utf-8") as f:
    for dl in c_deals:
        cp, _ = canon_phone(dl.get("contact_phone"))
        f.write(json.dumps({
            "deal_id": dl.get("id"),
            "name": dl.get("name"), "pipeline_desc": dl.get("pipeline_desc"),
            "pipeline_stage_desc": dl.get("pipeline_stage_desc"),
            "status": STATUS_MAP.get(dl.get("status_desc"), "open"),
            "monetaryValue": dl.get("amount"), "moneda": dl.get("currency"),
            "assignedTo_email": None, "owner_name": dl.get("owner_name"),
            "contact_canon_phone": cp, "contact_email": dl.get("contact_email"),
            "probabilidad": dl.get("probability"),
            "cierre_esperado": dl.get("expected_closed_date"),
            "cierre_real": dl.get("actual_closed_date"),
        }, ensure_ascii=False) + "\n")

with open(os.path.join(OUT, "companies.jsonl"), "w", encoding="utf-8") as f:
    for co in c_companies:
        f.write(json.dumps({"name": co.get("name"), "assignedTo_email": co.get("owner"),
                            "sector": co.get("company_sector"),
                            "rfc": co.get("taxpayer_identification_number")}, ensure_ascii=False) + "\n")

R(f"\nSalidas: contacts.jsonl={len(contacts_out)} · opportunities.jsonl={len(c_deals)} · companies.jsonl={len(c_companies)}")
# verificación: 0 duplicados de canon en la salida
canons = [r["canon_phone"] for r in contacts_out if r["canon_phone"]]
dups = [k for k, v in collections.Counter(canons).items() if v > 1]
R(f"Verificación dedup: canónicos duplicados en salida = {len(dups)} (esperado 0)")

open(os.path.join(OUT, "reporte-conteos-2026-09-03.md"), "w", encoding="utf-8").write(
    "# FASE 2 · Reporte de conteos (dry-run ETL) — 2026-09-03\n\n```\n" + "\n".join(report) + "\n```\n")
print("\nReporte → salida-etl/reporte-conteos-2026-09-03.md")
