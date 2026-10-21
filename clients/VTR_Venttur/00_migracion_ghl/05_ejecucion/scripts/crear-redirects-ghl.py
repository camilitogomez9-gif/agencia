#!/usr/bin/env python3
"""
Crea en GHL (Sites → URL Redirects) los redirects de los paths viejos de Clientify bajo promo.venttur.com.
Lee landings-ghl/_ghl/redirects.json (lo genera preparar-landings-ghl.py).

Requisito: el dominio promo.venttur.com ya agregado en GHL (Settings → Domains). GHL no acepta redirects para
un dominio que no conoce; si el primero falla, el script corta.

Uso:
  python3 crear-redirects-ghl.py              # dry-run: cuántos crea y cuántos ya existen
  python3 crear-redirects-ghl.py --execute    # crea los que faltan, en serie (idempotente)
  python3 crear-redirects-ghl.py --borrar --execute   # rollback: borra los de esta lista
  python3 crear-redirects-ghl.py --dominio vtr.[TU-DOMINIO] --execute   # ensayo en el dominio de pruebas:
        # los destinos promo.venttur.com se reescriben a ese dominio, así la cadena se prueba de punta a punta
  python3 crear-redirects-ghl.py --puente --execute   # B5, DESPUÉS de que promo sea el dominio principal del funnel:
        # en vtr.[TU-DOMINIO], cada landing (MANIFEST.md) → la misma ruta en promo.venttur.com. El funnel sólo sirve
        # en su dominio principal (verificado 23/9: vtr2 respondía 301 a vtr/programas); sin este puente los links
        # de vtr que el agente mandó antes de B5 caerían en Programas. Un redirect en un dominio no principal sí
        # funciona y conserva el query (probado 23/9 en vtr2).

API: POST /funnels/lookup/redirect · GET /funnels/lookup/redirect/list · DELETE /funnels/lookup/redirect/{id}
"""
import json, re, sys, time, urllib.request, urllib.error
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
REDIRECTS = BASE / "landings-ghl/_ghl/redirects.json"
CREDS = Path("/Users/camilo/Downloads/camilo-workspace/clients/VTR_Venttur/06_docs/ghl-credentials.md")
PROMO = "promo.venttur.com"
DOMAIN = (sys.argv[sys.argv.index("--dominio") + 1] if "--dominio" in sys.argv
          else "vtr.[TU-DOMINIO]" if "--puente" in sys.argv else PROMO).lower()
API = "https://services.leadconnectorhq.com"


def cred(k):
    m = re.search(rf"{k}\s*=\s*(\S+)", CREDS.read_text())
    return m.group(1) if m else None


PIT, LOC = cred("PIT_TOKEN"), cred("LOCATION_ID")
HDR = {"Authorization": f"Bearer {PIT}", "Version": "2021-07-28", "Accept": "application/json",
       "Content-Type": "application/json", "User-Agent": "curl/8.4.0"}


def call(method, path, body=None):
    req = urllib.request.Request(API + path, method=method, headers=HDR,
                                 data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.getcode(), json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]


def existentes():
    out, off = {}, 0
    while True:
        code, d = call("GET", f"/funnels/lookup/redirect/list?locationId={LOC}&limit=20&offset={off}")
        if code != 200:
            raise SystemExit(f"❌ no pude listar redirects: {code} {d}")
        rows = d.get("data") or []
        for r in rows:
            if (r.get("domain") or "").lower() == DOMAIN:
                out[(r.get("path") or "").lower()] = r
        if len(rows) < 20:
            return out
        off += 20


def main():
    execute, borrar = "--execute" in sys.argv, "--borrar" in sys.argv
    if "--puente" in sys.argv:
        lista = [{"path": m.group(1), "target": f"https://{PROMO}{m.group(1)}"}
                 for m in re.finditer(r"^\| \[.\] \| .+? \| `(/[^`]+)` \|", (REDIRECTS.parent / "MANIFEST.md").read_text(), re.M)]
    else:
        lista = json.loads(REDIRECTS.read_text())
    if DOMAIN != PROMO and "--puente" not in sys.argv:
        for r in lista:
            r["target"] = r["target"].replace(f"https://{PROMO}", f"https://{DOMAIN}")
    ya = existentes()

    if borrar:
        objetivo = [ya[r["path"].lower()] for r in lista if r["path"].lower() in ya]
        print(f"{'BORRANDO' if execute else '[dry-run] borraría'} {len(objetivo)} redirects de {DOMAIN}")
        for r in objetivo if execute else []:
            code, d = call("DELETE", f"/funnels/lookup/redirect/{r.get('id') or r.get('_id')}?locationId={LOC}")
            print(f"  {'✓' if code < 300 else '✗ ' + str(code)}  {r.get('path')}")
            time.sleep(0.6)
        return

    faltan = [r for r in lista if r["path"].lower() not in ya]
    print(f"{len(lista)} en la lista · {len(lista) - len(faltan)} ya existen · {len(faltan)} por crear")
    if not execute:
        for r in faltan[:5]:
            print(f"  → {r['path']}  ⇒  {r['target']}")
        print("\n[DRY-RUN] Nada cambió. Agregá --execute para crearlos.")
        return

    ok = 0
    for i, r in enumerate(faltan):
        code, d = call("POST", "/funnels/lookup/redirect",
                       {"locationId": LOC, "domain": DOMAIN, "path": r["path"], "target": r["target"], "action": "url"})
        if code >= 300:
            print(f"  ✗ {code} {r['path']}: {d}")
            if i == 0:
                raise SystemExit(f"❌ falló el primero: ¿está {DOMAIN} conectado en GHL → Settings → Domains?")
            continue
        ok += 1
        time.sleep(0.6)  # nunca en paralelo: límite de ráfaga de GHL
    print(f"\n✅ {ok}/{len(faltan)} creados. Verificá: curl -sI https://{DOMAIN}{faltan[0]['path']} | grep -i location")


if __name__ == "__main__":
    main()
