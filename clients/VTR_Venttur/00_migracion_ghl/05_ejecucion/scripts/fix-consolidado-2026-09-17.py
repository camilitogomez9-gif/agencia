#!/usr/bin/env python3
"""
Fix consolidado: matchea por TELÉFONO canonicalizado (columna `id` del CSV Leads)
y pobla los CFs faltantes:
- fbclid
- folio (retry para los 31 not-found que quedaron en el fix por email)
- (agendan cita ya fue resuelto en fix-agendan-cita-phone.py)

Uso:
  python3 fix-consolidado.py --dry-run
  python3 fix-consolidado.py --apply
"""
import argparse, csv, json, os, re, time, urllib.request, urllib.error

PIT = "pit-0d2b7776-2ccd-4671-ac5e-76ec4c0b4471"
LOC = "7aXb4JCKsWV5nUyBXeSF"
BASE = "https://services.leadconnectorhq.com"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

CSV_LEADS = "/Users/camilo/Downloads/camilo-workspace/clients/VTR_Venttur/00_migracion_ghl/00_inputs/airtable-csvs/leads.csv"

CF_FBCLID = "8REOsOHYC3boWRY74Rx5"
CF_FOLIO = "S80aYglwiVLkMsf95Ddz"

def canon_phone(raw):
    if raw is None: return None
    digits = re.sub(r"\D", "", str(raw))
    if not digits: return None
    if digits.startswith("52"):
        rest = digits[2:]
        if rest.startswith("1") and len(rest) == 11: return "+521" + rest[1:]
        if len(rest) == 10: return "+521" + rest
        return "+" + digits
    if 10 <= len(digits) <= 15: return "+" + digits
    return "+" + digits

def http(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method, headers={
        "Authorization": f"Bearer {PIT}", "Version": "2021-07-28",
        "Content-Type": "application/json", "Accept": "application/json", "User-Agent": UA
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode() or '{}')
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or '{}')

def search_by_phone(phone):
    body = {"locationId": LOC, "pageLimit": 1,
            "filters": [{"field":"phone","operator":"eq","value":phone}]}
    code, d = http("POST", "/contacts/search", body)
    if code == 200:
        contacts = d.get('contacts', [])
        if contacts: return contacts[0].get('id')
    return None

def patch_cfs(cid, cfs):
    body = {"customFields": cfs}
    return http("PUT", f"/contacts/{cid}", body)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    # Cargar leads con teléfono
    to_process = []
    with open(CSV_LEADS, encoding='utf-8-sig') as f:
        r = csv.DictReader(f)
        for row in r:
            tel_raw = (row.get('id') or '').strip()
            if not tel_raw: continue
            canon = canon_phone(tel_raw)
            if not canon: continue

            fbclid = (row.get('fbclid') or '').strip()
            folio = (row.get('Folio') or '').strip()

            cfs = []
            if fbclid and fbclid not in ('-', '0', 'N/A'):
                cfs.append({'id': CF_FBCLID, 'value': fbclid})
            if folio and folio not in ('N/A (WA)', 'N/A (Form)', 'N/A', '', '0', '-'):
                cfs.append({'id': CF_FOLIO, 'value': folio})

            if cfs:
                to_process.append({'phone': canon, 'cfs': cfs, 'nom': row.get('Nombre Completo','')})

    # dedup por phone
    seen = set()
    dedup = []
    for x in to_process:
        if x['phone'] not in seen:
            seen.add(x['phone'])
            dedup.append(x)

    print(f"Total con CFs a poblar por phone: {len(to_process)} → dedup: {len(dedup)}", flush=True)
    print(f"\nModo: {'APPLY' if args.apply else 'DRY-RUN'}\n", flush=True)

    fixed, notfound, err = 0, 0, 0
    for i, x in enumerate(dedup):
        cid = search_by_phone(x['phone'])
        if not cid:
            notfound += 1
            if notfound <= 5:
                print(f"  NOT FOUND: {x['phone']} · {x['nom']}", flush=True)
            time.sleep(0.1)
            continue
        if args.apply:
            st, r = patch_cfs(cid, x['cfs'])
            if st in (200, 201):
                fixed += 1
            else:
                err += 1
                if err <= 3:
                    print(f"  ERROR {st}: {x['phone']} · {str(r)[:100]}", flush=True)
        else:
            fixed += 1
        time.sleep(0.15)
        if (i+1) % 100 == 0:
            print(f"  progreso: {i+1}/{len(dedup)}  fixed={fixed}, notfound={notfound}, err={err}", flush=True)

    print(f"\n=== RESUMEN ({'APPLY' if args.apply else 'DRY-RUN'}) ===")
    print(f"Procesados:   {len(dedup)}")
    print(f"Fixed:        {fixed}")
    print(f"Not found:    {notfound}")
    print(f"Errores:      {err}")

if __name__ == "__main__":
    main()
