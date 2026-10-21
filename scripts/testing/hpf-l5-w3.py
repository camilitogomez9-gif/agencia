#!/usr/bin/env python3
"""
HPF · L5 — Gate de W3 · Catálogo.

El oráculo es el catálogo de Airtable (catalogo-airtable.json): lo que W3 devuelva
tiene que coincidir con lo que la fórmula de Airtable habría devuelto.
"""
import json
import time
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EVID = REPO / "clients/HPF_HappyFlops/07_testing/evidencia-migracion/L5"
CAT = REPO / "clients/HPF_HappyFlops/00_migracion_ghl/06_registro/catalogo-airtable.json"
W3 = "https://[TU-INSTANCIA-N8N]/webhook/hpf-w3-catalogo"
RES = []


def env():
    e = {}
    for line in (REPO / ".env").read_text().splitlines():
        if line.strip() and not line.strip().startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            e[k.strip()] = v.strip().strip('"').strip("'")
    return e


E = env()
H = {"Content-Type": "application/json",
     E["HPF_WEBHOOK_AUTH_HEADER_NAME"]: E["HPF_WEBHOOK_AUTH_HEADER_VALUE"]}


def w3(body):
    req = urllib.request.Request(W3, data=json.dumps(body).encode(), headers=H, method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return r.status, json.loads(r.read().decode() or "null"), time.time() - t0
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw), time.time() - t0
        except json.JSONDecodeError:
            return e.code, {"_raw": raw[:300]}, time.time() - t0


def prim(r):
    return r[0] if isinstance(r, list) and r else (r if isinstance(r, dict) else {})


def norm(s):
    s = unicodedata.normalize("NFD", str(s or "")).encode("ascii", "ignore").decode()
    return s.lower().strip()


CATALOGO = json.loads(CAT.read_text())


def oraculo(evento="", subcat="", productos=()):
    """Lo que la fórmula de Airtable habría devuelto para estos filtros."""
    out = []
    for c in CATALOGO:
        ev = c.get("evento") or c["tabla"]
        if evento and norm(ev) != norm(evento):
            continue
        if subcat and norm(c.get("subcategoria")) != norm(subcat):
            continue
        if productos and not any(norm(p) in norm(c["producto"]) for p in productos):
            continue
        if not (c.get("ghl_media") or {}).get("url"):
            # W3 filtra por activo, que es "hay asset"
            continue
        out.append(c["producto"])
    return sorted(out)


def reg(cid, titulo, ok, detalle, pasos):
    EVID.mkdir(parents=True, exist_ok=True)
    EVID.joinpath(f"{cid}.json").write_text(json.dumps(
        {"caso": cid, "titulo": titulo, "resultado": "CORROBORADO" if ok else "FALLA",
         "detalle": detalle, "pasos": pasos}, indent=2, ensure_ascii=False), encoding="utf-8")
    RES.append((cid, titulo, ok))
    print(f"  {'✅' if ok else '❌'} {cid} {titulo}\n       {detalle}")


def c01():
    """Arranque en frío: la caché está vacía y se refresca sola desde GHL."""
    s, r, dur = w3({"evento": "Boda"})
    d = prim(r)
    esp = oraculo("Boda")
    got = sorted(c["nombre"] for c in d.get("cards", []))
    ok = s == 200 and got == esp
    reg("C-01", "arranque en frío: refresca la caché solo", ok,
        f"http={s} {dur:.1f}s cards={len(got)} esperadas={len(esp)} "
        f"{'iguales' if got == esp else 'DIFIEREN: ' + str(set(esp) ^ set(got))[:150]}",
        [{"req": {"evento": "Boda"}, "cards": got}])


def c02():
    """Segunda llamada: pega en caché y es notablemente más rápida."""
    t0 = time.time()
    s, r, dur = w3({"evento": "Boda"})
    d = prim(r)
    ok = s == 200 and d.get("cantidad") == len(oraculo("Boda")) and dur < 3
    reg("C-02", "segunda llamada pega en caché", ok,
        f"http={s} {dur:.2f}s (esperado <3s) cards={d.get('cantidad')}", [{"dur": dur}])


def c03():
    """Filtro por subcategoría: la mitad del AND de la fórmula de Airtable."""
    s, r, _ = w3({"evento": "XV", "subcategoria": "Accesorios"})
    d = prim(r)
    esp = oraculo("XV", "Accesorios")
    got = sorted(c["nombre"] for c in d.get("cards", []))
    ok = s == 200 and got == esp
    reg("C-03", "filtro evento + subcategoría", ok,
        f"cards={len(got)} esperadas={len(esp)} "
        f"{'iguales' if got == esp else 'DIFIEREN: ' + str(set(esp) ^ set(got))[:150]}",
        [{"cards": got}])


def c04():
    """El OR(SEARCH(p1), SEARCH(p2)) de Airtable, replicado en SQL."""
    prods = ["sandalias", "cilindros"]
    s, r, _ = w3({"evento": "Boda", "productos": prods})
    d = prim(r)
    esp = oraculo("Boda", "", prods)
    got = sorted(c["nombre"] for c in d.get("cards", []))
    ok = s == 200 and got == esp
    reg("C-04", "OR sobre varios productos (LIKE case-insensitive)", ok,
        f"pedí {prods} → cards={len(got)} esperadas={len(esp)} "
        f"{'iguales' if got == esp else 'DIFIEREN: ' + str(set(esp) ^ set(got))[:150]}",
        [{"cards": got}])


def c05():
    """Producto inexistente: 0 cards, no error ni catálogo entero."""
    s, r, _ = w3({"evento": "Boda", "productos": ["helicoptero"]})
    d = prim(r)
    ok = s == 200 and d.get("cantidad") == 0
    reg("C-05", "producto inexistente → 0 cards, sin romper", ok,
        f"http={s} cantidad={d.get('cantidad')}", [{"resp": d}])


def c06():
    """Las cards traen el texto y el asset que corresponden."""
    s, r, _ = w3({"evento": "Boda", "productos": ["colores de tintas"]})
    d = prim(r)
    card = (d.get("cards") or [{}])[0]
    origen = next((c for c in CATALOGO
                   if c["tabla"] == "Boda" and "Colores de tintas" in c["producto"]), {})
    mismo_texto = (card.get("texto") or "").strip() == (origen.get("descripcion") or "").strip()
    mismo_media = card.get("media_url") == (origen.get("ghl_media") or {}).get("url")
    ok = s == 200 and mismo_texto and mismo_media
    reg("C-06", "la card lleva el texto y el asset correctos", ok,
        f"texto_igual={mismo_texto} media_igual={mismo_media} tipo={card.get('media_tipo')}",
        [{"card": card}])


def c07():
    """Las 3 filas homónimas de Imagen Principal se distinguen por evento."""
    res = {}
    for ev in ("Boda", "XV", "Otros"):
        s, r, _ = w3({"evento": ev, "productos": ["todos los productos"]})
        d = prim(r)
        cards = d.get("cards") or []
        res[ev] = cards[0].get("media_url") if cards else None
    distintas = len({v for v in res.values() if v}) == 3
    ok = all(res.values()) and distintas
    reg("C-07", "imagen principal distinta por evento (3 fichas homónimas)", ok,
        f"{ {k: (v or '')[-24:] for k, v in res.items()} } distintas={distintas}",
        [{"por_evento": res}])


def c08():
    """Sin filtro de producto devuelve todo el evento — el caso 'todos'."""
    s, r, _ = w3({"evento": "Otros"})
    d = prim(r)
    esp = oraculo("Otros")
    got = sorted(c["nombre"] for c in d.get("cards", []))
    ok = s == 200 and got == esp
    reg("C-08", "sin filtro de producto → todas las del evento", ok,
        f"cards={len(got)} esperadas={len(esp)} "
        f"{'iguales' if got == esp else 'DIFIEREN: ' + str(set(esp) ^ set(got))[:150]}",
        [{"cards": got}])


CASOS = [c01, c02, c03, c04, c05, c06, c07, c08]


def main():
    print("HPF · L5 — gate de W3 (catálogo con caché en Postgres)\n")
    for f in CASOS:
        try:
            f()
        except Exception as e:
            reg(f.__name__.upper(), (f.__doc__ or "").strip(), False,
                f"EXCEPCIÓN {type(e).__name__}: {e}", [])
    ok = sum(1 for *_, o in RES if o)
    print(f"\n{'=' * 68}\nL5·W3: {ok}/{len(RES)} corroborados")
    for cid, t, o in RES:
        if not o:
            print(f"  ❌ {cid} {t}")


if __name__ == "__main__":
    main()
