#!/usr/bin/env python3
"""
Fix `agendan cita` en GHL: para cada lead de Airtable con Agendan cita=true,
setea el CF `agendan cita` en el contacto GHL (match por email).

También ataca `folio` cuando Airtable tiene un valor no vacío ni "N/A".

Uso:
  python3 fix-agendan-cita.py --dry-run
  python3 fix-agendan-cita.py --apply
"""
import argparse, csv, json, os, time, urllib.request, urllib.error, urllib.parse

PIT = "pit-0d2b7776-2ccd-4671-ac5e-76ec4c0b4471"
LOC = "7aXb4JCKsWV5nUyBXeSF"
BASE = "https://services.leadconnectorhq.com"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

CSV_LEADS = "/Users/camilo/Downloads/camilo-workspace/clients/VTR_Venttur/00_migracion_ghl/00_inputs/airtable-csvs/leads.csv"

CF_AGENDAN = "LwXu8AxMLhVGCbNmgzm2"  # agendan cita (checkbox)
CF_FOLIO = "S80aYglwiVLkMsf95Ddz"    # folio (probablemente text)

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

def search_by_email(email):
    body = {"locationId": LOC, "pageLimit": 5,
            "filters": [{"field":"email","operator":"eq","value":email}]}
    code, d = http("POST", "/contacts/search", body)
    if code == 200:
        contacts = d.get('contacts', [])
        if contacts:
            return contacts[0].get('id')
    return None

def patch_cf(cid, cf_id, value):
    body = {"customFields": [{"id": cf_id, "value": value}]}
    return http("PUT", f"/contacts/{cid}", body)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    APPLY = args.apply
    LIMIT = args.limit

    print(f"Modo: {'APPLY' if APPLY else 'DRY-RUN'}  Limit: {LIMIT or 'all'}")

    to_fix_agendan = []
    to_fix_folio = []
    with open(CSV_LEADS, encoding='utf-8-sig') as f:
        r = csv.DictReader(f)
        for row in r:
            email = (row.get('Email') or '').strip()
            if not email:
                continue
            agendan = (row.get('Agendan cita') or '').strip().lower()
            folio = (row.get('Folio') or '').strip()
            if agendan in ('checked', 'true', 'yes', 'sí', 'x', '1'):
                to_fix_agendan.append((email, row.get('Nombre Completo', '')))
            if folio and folio not in ('N/A (WA)', 'N/A (Form)', 'N/A', '', '0', '-'):
                to_fix_folio.append((email, folio, row.get('Nombre Completo', '')))

    print(f"\nAirtable → GHL:")
    print(f"  Contactos con Agendan cita=true en Airtable + email: {len(to_fix_agendan)}")
    print(f"  Contactos con Folio válido en Airtable + email:      {len(to_fix_folio)}")

    if LIMIT:
        to_fix_agendan = to_fix_agendan[:LIMIT]
        to_fix_folio = to_fix_folio[:LIMIT]

    # --- Aplicar Agendan cita ---
    print(f"\n=== Fase 1: Agendan cita ({len(to_fix_agendan)}) ===")
    fixed_a, notfound_a, err_a = 0, 0, 0
    for i, (email, name) in enumerate(to_fix_agendan):
        cid = search_by_email(email)
        if not cid:
            notfound_a += 1
            if notfound_a <= 5:
                print(f"  NOT FOUND: {email} · {name}")
            time.sleep(0.15)
            continue
        if APPLY:
            st, r = patch_cf(cid, CF_AGENDAN, ["true"])
            if st in (200, 201):
                fixed_a += 1
            else:
                err_a += 1
                if err_a <= 3:
                    print(f"  ERROR {st}: {email} · {str(r)[:100]}")
        else:
            fixed_a += 1
        time.sleep(0.15)
        if i % 50 == 0 and i > 0:
            print(f"  progreso: {i}/{len(to_fix_agendan)}   fixed={fixed_a}, notfound={notfound_a}, err={err_a}")

    print(f"\n  Agendan cita — resultado: fixed={fixed_a}, not_found={notfound_a}, err={err_a}")

    # --- Aplicar Folio ---
    print(f"\n=== Fase 2: Folio ({len(to_fix_folio)}) ===")
    fixed_f, notfound_f, err_f = 0, 0, 0
    for i, (email, folio, name) in enumerate(to_fix_folio):
        cid = search_by_email(email)
        if not cid:
            notfound_f += 1
            if notfound_f <= 5:
                print(f"  NOT FOUND: {email} · {name}")
            time.sleep(0.15)
            continue
        if APPLY:
            st, r = patch_cf(cid, CF_FOLIO, folio)
            if st in (200, 201):
                fixed_f += 1
            else:
                err_f += 1
                if err_f <= 3:
                    print(f"  ERROR {st}: {email} · {folio} · {str(r)[:100]}")
        else:
            fixed_f += 1
        time.sleep(0.15)
        if i % 50 == 0 and i > 0:
            print(f"  progreso: {i}/{len(to_fix_folio)}   fixed={fixed_f}, notfound={notfound_f}, err={err_f}")

    print(f"\n  Folio — resultado: fixed={fixed_f}, not_found={notfound_f}, err={err_f}")

    print(f"\n=== TOTAL ===")
    print(f"Agendan cita fixed: {fixed_a}/{len(to_fix_agendan)}")
    print(f"Folio fixed:        {fixed_f}/{len(to_fix_folio)}")

if __name__ == "__main__":
    main()
