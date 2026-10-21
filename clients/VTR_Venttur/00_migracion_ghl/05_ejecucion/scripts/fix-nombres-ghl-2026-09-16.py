#!/usr/bin/env python3
"""
Fix nombres GHL: split de firstName combinado (nombre+apellido en un campo) por primer espacio,
excluyendo instituciones (School/Academy/College/Institute).

Uso:
  python3 fix-nombres-ghl.py --dry-run           # dry-run sobre TODA la base
  python3 fix-nombres-ghl.py --apply             # PATCH real
  python3 fix-nombres-ghl.py --dry-run --limit 50  # muestreo pequeño
"""
import argparse, json, os, sys, time, urllib.request, urllib.error

PIT = "pit-0d2b7776-2ccd-4671-ac5e-76ec4c0b4471"
LOC = "7aXb4JCKsWV5nUyBXeSF"
BASE = "https://services.leadconnectorhq.com"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

INSTITUCION_KW = [
    'school', 'academy', 'college', 'institute', 'colegio', 'universidad',
    'university', 'campus', 'centre', 'ranch', 'foundation', 'consultants',
    'servicios', 'agency', 'sociedad', 's.a.', 's.l.', 'inc.', 'ltd',
    'sistema', 'departamento', 'sport', 'sports', 'summer camp', 'iutg',
]

def is_institucion(name: str) -> bool:
    lo = name.lower().strip()
    # todo mayúsculas y >=3 tokens
    if name.isupper() and len(name.split()) >= 2 and len(name) > 12:
        return True
    for kw in INSTITUCION_KW:
        if kw in lo:
            return True
    return False

def http(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method, headers={
        "Authorization": f"Bearer {PIT}",
        "Version": "2021-07-28",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": UA,
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode() or '{}')
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or '{}')

def search_page(page, page_limit=100):
    body = {
        "locationId": LOC,
        "pageLimit": page_limit,
        "page": page,
        "filters": [
            {"field": "dateAdded", "operator": "range", "value": {
                "gte": "2026-09-03T00:00:00.000Z",
                "lte": "2026-09-05T00:00:00.000Z"
            }}
        ]
    }
    code, d = http("POST", "/contacts/search", body)
    return code, d

def patch_contact(cid, first, last):
    body = {"firstName": first, "lastName": last}
    return http("PUT", f"/contacts/{cid}", body)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", default=True)
    ap.add_argument("--apply", action="store_true", default=False)
    ap.add_argument("--limit", type=int, default=0, help="Limitar # contactos a procesar (0 = todos)")
    args = ap.parse_args()
    APPLY = args.apply
    LIMIT = args.limit

    print(f"Modo: {'APPLY' if APPLY else 'DRY-RUN'}  Limit: {LIMIT or 'all'}")

    total_found = 0
    total_fixed = 0
    total_skipped_inst = 0
    total_errors = 0
    ejemplos_fix = []
    ejemplos_inst = []

    page = 1
    procesados = 0
    while True:
        code, d = search_page(page)
        if code != 200:
            print(f"HTTP {code} en página {page}: {d}")
            break
        contacts = d.get('contacts', [])
        if not contacts:
            break
        for c in contacts:
            first = (c.get('firstName') or '').strip()
            last = (c.get('lastName') or '').strip()
            # solo procesamos: firstName con espacio Y lastName vacío
            if not first or ' ' not in first or last:
                continue
            total_found += 1
            procesados += 1

            if is_institucion(first):
                total_skipped_inst += 1
                if len(ejemplos_inst) < 10:
                    ejemplos_inst.append(first)
                continue

            # Split por primer espacio
            parts = first.split(' ', 1)
            new_first = parts[0]
            new_last = parts[1].strip()
            if len(ejemplos_fix) < 15:
                ejemplos_fix.append((first, new_first, new_last))

            if APPLY:
                st, r = patch_contact(c['id'], new_first, new_last)
                if st in (200, 201):
                    total_fixed += 1
                else:
                    total_errors += 1
                    print(f"  ERROR {st} en {c['id']}: {str(r)[:100]}")
                time.sleep(0.1)  # rate limit courtesy
            else:
                total_fixed += 1

            if LIMIT and procesados >= LIMIT:
                break
        if LIMIT and procesados >= LIMIT:
            break
        if len(contacts) < 100:
            break  # última página
        page += 1

    print(f"\n=== RESUMEN ({'APPLIED' if APPLY else 'DRY-RUN'}) ===")
    print(f"Contactos con firstName combinado detectados: {total_found}")
    print(f"  {'Fixed' if APPLY else 'A fixear'}:                                {total_fixed}")
    print(f"  Skipped (instituciones):                    {total_skipped_inst}")
    print(f"  Errores:                                    {total_errors}")

    print(f"\n--- Muestra a fixear ---")
    for orig, f, l in ejemplos_fix:
        print(f"  {orig!r:50s}  →  first={f!r}  last={l!r}")

    print(f"\n--- Muestra saltada (instituciones) ---")
    for x in ejemplos_inst:
        print(f"  {x!r}")

if __name__ == "__main__":
    main()
