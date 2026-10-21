#!/usr/bin/env python3
"""
Fix `agendan cita` en GHL: para cada lead en Airtable con Agendan cita=true,
matchear por TELÉFONO (columna `id` del CSV, canonicalizado MX 52↔521) y setear
el CF `agendan cita` en GHL.

Usa la misma canonicalización que etl-preproceso.py:
  52<10> → +521<10> (con 1 al inicio o sin)

Uso:
  python3 fix-agendan-cita-phone.py --dry-run
  python3 fix-agendan-cita-phone.py --apply [--limit N]
"""
import argparse, csv, json, os, re, time, urllib.request, urllib.error

PIT = "pit-0d2b7776-2ccd-4671-ac5e-76ec4c0b4471"
LOC = "7aXb4JCKsWV5nUyBXeSF"
BASE = "https://services.leadconnectorhq.com"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

CSV_LEADS = "/Users/camilo/Downloads/camilo-workspace/clients/VTR_Venttur/00_migracion_ghl/00_inputs/airtable-csvs/leads.csv"

CF_AGENDAN = "LwXu8AxMLhVGCbNmgzm2"  # agendan cita (checkbox)

def canon_phone(raw):
    """Copia del canonPhone del ETL: MX colapsa 52/521 → +521<nac10>."""
    if raw is None: return None
    digits = re.sub(r"\D", "", str(raw))
    if not digits: return None
    if digits.startswith("52"):
        rest = digits[2:]
        if rest.startswith("1") and len(rest) == 11:
            return "+521" + rest[1:]
        if len(rest) == 10:
            return "+521" + rest
        return "+" + digits
    if 10 <= len(digits) <= 15:
        return "+" + digits
    return "+" + digits

def http(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method, headers={
        "Authorization": f"Bearer {PIT}", "Version": "2021-07-28",
        "Content-Type": "application/json", "Accept": "application/json",
        "User-Agent": UA,
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode() or '{}')
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or '{}')

def search_by_phone(phone):
    body = {"locationId": LOC, "pageLimit": 5,
            "filters": [{"field":"phone","operator":"eq","value":phone}]}
    code, d = http("POST", "/contacts/search", body)
    if code == 200:
        contacts = d.get('contacts', [])
        if contacts:
            return contacts[0].get('id')
    return None

def get_contact(cid):
    code, d = http("GET", f"/contacts/{cid}")
    if code == 200:
        return d.get('contact', d)
    return None

def patch_cf(cid, cf_id, value):
    body = {"customFields": [{"id": cf_id, "value": value}]}
    return http("PUT", f"/contacts/{cid}", body)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--skip-check", action="store_true", help="skip check si ya tiene agendan=true")
    args = ap.parse_args()

    to_fix = []
    with open(CSV_LEADS, encoding='utf-8-sig') as f:
        r = csv.DictReader(f)
        for row in r:
            agendan = (row.get('Agendan cita') or '').strip().lower()
            if agendan not in ('checked', 'true'):
                continue
            tel_raw = (row.get('id') or '').strip()
            if not tel_raw:
                continue
            canon = canon_phone(tel_raw)
            if not canon:
                continue
            to_fix.append({
                'phone': canon,
                'raw': tel_raw,
                'nombre': row.get('Nombre Completo', ''),
            })

    # dedup por phone (ya vi que Grisel Trejo aparece 2 veces con mismo tel)
    seen = set()
    dedup = []
    for x in to_fix:
        if x['phone'] not in seen:
            seen.add(x['phone'])
            dedup.append(x)
    print(f"Total leads con Agendan cita + phone: {len(to_fix)}")
    print(f"Dedup por phone canónico:              {len(dedup)}")

    if args.limit:
        dedup = dedup[:args.limit]

    print(f"\nModo: {'APPLY' if args.apply else 'DRY-RUN'}   procesando: {len(dedup)}\n", flush=True)

    fixed, already, notfound, err = 0, 0, 0, 0
    for i, lead in enumerate(dedup):
        cid = search_by_phone(lead['phone'])
        if not cid:
            notfound += 1
            if notfound <= 5:
                print(f"  NOT FOUND: {lead['phone']} · {lead['nombre']}", flush=True)
            time.sleep(0.12)
            continue

        if args.apply:
            # opcionalmente saltear si ya está
            if not args.skip_check:
                c = get_contact(cid)
                if c:
                    cfs = c.get('customFields', [])
                    for cf in cfs:
                        if cf.get('id') == CF_AGENDAN:
                            v = cf.get('value')
                            if v == ['true'] or v is True or v == 'true':
                                already += 1
                                break
                    else:
                        st, r = patch_cf(cid, CF_AGENDAN, ["true"])
                        if st in (200, 201):
                            fixed += 1
                        else:
                            err += 1
                            if err <= 3:
                                print(f"  ERROR {st}: {lead['phone']} · {str(r)[:100]}", flush=True)
                    time.sleep(0.2)
                else:
                    err += 1
            else:
                st, r = patch_cf(cid, CF_AGENDAN, ["true"])
                if st in (200, 201):
                    fixed += 1
                else:
                    err += 1
                time.sleep(0.15)
        else:
            fixed += 1
            time.sleep(0.05)

        if (i+1) % 50 == 0:
            print(f"  progreso: {i+1}/{len(dedup)}  fixed={fixed} already={already} notfound={notfound} err={err}", flush=True)

    print(f"\n=== RESUMEN ({'APPLY' if args.apply else 'DRY-RUN'}) ===")
    print(f"Leads procesados:   {len(dedup)}")
    print(f"Ya tenían Agendan:  {already}")
    print(f"Fixed:              {fixed}")
    print(f"Not found en GHL:   {notfound}")
    print(f"Errores:            {err}")

if __name__ == "__main__":
    main()
