#!/usr/bin/env python3
"""
Carga el catálogo de servicios de Clientify → GHL Products (para presupuestos/Estimates).
Fuente: ~/Downloads/ListProducts.csv + ListProducts-2.csv (47 productos).

Curación:
 - Descarta TEST (ELTIS, Prueba) + ONE-OFF (cotizaciones de clientes puntuales).
 - Dedup por nombre.
 - Carga SOLO los MXN (la location GHL es MXN). Los 15 en moneda extranjera (EUR/USD/CAD/GBP)
   quedan flaggeados aparte — decisión de moneda pendiente (ver reporte).
 - IVA: se carga el precio base; el 16% IVA se aplica a nivel de invoice/template (Camilo).

Idempotente: si ya existe un product con ese nombre en GHL, no lo re-crea.
"""
import csv, json, re, sys, urllib.request, urllib.error

CREDS = "/Users/camilo/Downloads/camilo-workspace/clients/VTR_Venttur/06_docs/ghl-credentials.md"
CSVS = ["/Users/camilo/Downloads/ListProducts.csv", "/Users/camilo/Downloads/ListProducts-2.csv"]


def cred(k):
    m = re.search(rf"{k}\s*=\s*(\S+)", open(CREDS).read()); return m.group(1) if m else None


PIT = cred("PIT_TOKEN"); LOC = cred("LOCATION_ID")
BASE = "https://services.leadconnectorhq.com"
H = {"Authorization": f"Bearer {PIT}", "Version": "2021-07-28", "Accept": "application/json",
     "Content-Type": "application/json", "User-Agent": "curl/8.4.0"}


def call(method, path, body=None):
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(BASE + path, data=data, headers=H, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.getcode(), json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]


def load_rows():
    rows = []
    for f in CSVS:
        with open(f, newline='', encoding='utf-8') as fh:
            rows += list(csv.DictReader(fh, delimiter=';'))
    return rows


def is_junk(r):
    n = r['name'].lower()
    if any(t in n for t in ['test', 'prueba', 'eltis']):
        return True
    if any(t in r['name'] for t in ['Marcelo Guadiana', 'Javier y Anna', 'Lia Mariana']):
        return True
    return False


EXCHANGE_NOTE = ['La Garenne', 'Lyceum', 'ALPADIA', 'Learn&Study']


def existing_names():
    names = set()
    offset = 0
    while True:
        code, resp = call("GET", f"/products/?locationId={LOC}&limit=100&offset={offset}")
        if not isinstance(resp, dict):
            break
        prods = resp.get("products", [])
        for p in prods:
            names.add(p.get("name"))
        if len(prods) < 100:
            break
        offset += 100
    return names


def main():
    dry = "--dry" in sys.argv
    rows = load_rows()
    mxn, foreign, junk = [], [], []
    seen = set()
    for r in rows:
        if is_junk(r):
            junk.append(r); continue
        if r['currency'] != 'MXN':
            foreign.append(r); continue
        key = r['name'].strip()
        if key in seen:
            continue  # dedup por nombre
        seen.add(key)
        mxn.append(r)

    print(f"Filas: {len(rows)} · MXN únicos: {len(mxn)} · foreign: {len(foreign)} · junk descartados: {len(junk)}")

    if dry:
        print("\n[DRY] MXN a cargar:")
        for r in mxn:
            note = " ⚠️TC" if any(t in r['name'] for t in EXCHANGE_NOTE) else ""
            print(f"  {float(r['price']):>10,.2f} MXN  {r['name']}{note}")
        print("\n[DRY] foreign (flag):")
        for r in foreign:
            print(f"  {float(r['price']):>10,.2f} {r['currency']}  {r['name']}")
        return

    have = existing_names()
    print(f"Productos ya en GHL: {len(have)}\n")
    created, skipped, failed = 0, 0, []
    for r in mxn:
        name = r['name'].strip()
        if name in have:
            print(f"  ⏭  ya existe: {name}")
            skipped += 1; continue
        desc = (r.get('description') or '').strip()
        if any(t in name for t in EXCHANGE_NOTE):
            desc = ("⚠️ Precio según tipo de cambio del día — verificar antes de cotizar.\n\n" + desc).strip()
        prod = {"name": name, "locationId": LOC, "description": desc[:1500],
                "productType": "SERVICE", "availableInStore": False}
        code, resp = call("POST", "/products/", prod)
        if code != 201 or not isinstance(resp, dict):
            failed.append((name, f"create {code}: {resp}")); print(f"  ✗ {name}: create {code}"); continue
        pid = resp.get("_id") or resp.get("product", {}).get("_id")
        price = {"name": name, "type": "one_time", "currency": "MXN",
                 "amount": float(r['price']), "locationId": LOC}
        c2, r2 = call("POST", f"/products/{pid}/price", price)
        if c2 != 201:
            failed.append((name, f"price {c2}: {r2}")); print(f"  ⚠ {name}: product OK pero price {c2}"); continue
        print(f"  ✓ {name}  ${float(r['price']):,.2f} MXN")
        created += 1

    print(f"\n=== RESUMEN ===\n  creados: {created} · ya existían: {skipped} · fallidos: {len(failed)}")
    for n, e in failed:
        print(f"  ✗ {n}: {e}")
    print(f"\n  FOREIGN sin cargar (decisión de moneda pendiente): {len(foreign)}")
    for r in foreign:
        print(f"    {float(r['price']):>10,.2f} {r['currency']}  {r['name']}")


if __name__ == "__main__":
    main()
