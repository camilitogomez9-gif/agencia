#!/usr/bin/env python3
"""
HPF — Cambia `allowDuplicateOpportunity` de la sub-cuenta GHL.

El toggle NO está en Settings → Opportunities & Pipelines (ahí sólo aparece el de
owners). La API sí lo expone en `location.settings.allowDuplicateOpportunity`.

Qué implica el flag:
  false (actual) → un contacto = UNA oportunidad, para siempre. Incluso si está en
                   `lost`, crear otra devuelve 400 OPPORTUNITY_NO_DUPLICATE. Un cliente
                   que vuelve a comprar reescribe la oportunidad del pedido anterior.
  true           → replica Kommo, donde cada pedido era un lead nuevo.

Es read-modify-write: lee los settings actuales, cambia SÓLO ese flag y reescribe el
resto idéntico. Guarda un snapshot antes de tocar nada.

Uso:
    python3 scripts/utilities/hpf-toggle-duplicate-opportunity.py            # muestra estado
    python3 scripts/utilities/hpf-toggle-duplicate-opportunity.py --activar
    python3 scripts/utilities/hpf-toggle-duplicate-opportunity.py --desactivar
    python3 scripts/utilities/hpf-toggle-duplicate-opportunity.py --revertir  # desde el snapshot
"""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SNAP = REPO / "clients/HPF_HappyFlops/06_docs/ghl-location-settings-snapshot.json"
API = "https://services.leadconnectorhq.com"
FLAG = "allowDuplicateOpportunity"


def load_env():
    e = {}
    for line in (REPO / ".env").read_text().splitlines():
        if line.strip() and not line.strip().startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            e[k.strip()] = v.strip().strip('"').strip("'")
    return e


E = load_env()
LOC = E["GHL_LOCATION_ID"]
HDR = {"Authorization": f"Bearer {E['GHL_API_KEY']}", "Version": "2021-07-28",
       "Content-Type": "application/json", "User-Agent": "curl/8.7.1"}


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, headers=HDR, method=method)
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw.strip() else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, {"_raw": raw[:400]}


def leer():
    s, r = call("GET", f"/locations/{LOC}")
    if s >= 300:
        print(f"❌ GET /locations/{LOC} → {s}: {json.dumps(r)[:300]}")
        sys.exit(1)
    return r.get("location", r)


def escribir(settings, loc):
    body = {"companyId": loc.get("companyId"), "name": loc.get("name"),
            "settings": settings}
    s, r = call("PUT", f"/locations/{LOC}", body)
    return s, r


def main():
    loc = leer()
    st = dict(loc.get("settings") or {})
    actual = st.get(FLAG)
    print(f"sub-cuenta : {loc.get('name')} ({LOC})")
    print(f"{FLAG}: {actual}")

    if "--revertir" in sys.argv:
        if not SNAP.exists():
            print("❌ no hay snapshot para revertir")
            sys.exit(1)
        prev = json.loads(SNAP.read_text())
        s, r = escribir(prev["settings"], loc)
        print(f"revertido a los settings del snapshot → http={s}")
        return

    destino = None
    if "--activar" in sys.argv:
        destino = True
    elif "--desactivar" in sys.argv:
        destino = False
    if destino is None:
        print("\n(sólo lectura — pasá --activar o --desactivar para cambiarlo)")
        return
    if actual == destino:
        print(f"ya está en {destino}, nada que hacer")
        return

    SNAP.parent.mkdir(parents=True, exist_ok=True)
    SNAP.write_text(json.dumps({"tomado_de": LOC, "settings": st},
                               indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"snapshot → {SNAP.relative_to(REPO)}")

    nuevo = dict(st)
    nuevo[FLAG] = destino
    s, r = escribir(nuevo, loc)
    if s >= 300:
        print(f"❌ PUT → {s}: {json.dumps(r, ensure_ascii=False)[:400]}")
        if s in (401, 403):
            print("   → el PIT no tiene scope de escritura de location "
                  "(locations.write). Habría que hacerlo desde la cuenta de agencia.")
        sys.exit(1)

    # la evidencia es el read-back, no el 2xx
    confirmado = leer().get("settings", {}).get(FLAG)
    print(f"PUT http={s} · read-back {FLAG}={confirmado} "
          f"{'✅' if confirmado == destino else '❌ NO se aplicó'}")
    print("\nVerificá el efecto real con:")
    print("  python3 scripts/testing/hpf-ghl-primitivas.py T-16")


if __name__ == "__main__":
    main()
