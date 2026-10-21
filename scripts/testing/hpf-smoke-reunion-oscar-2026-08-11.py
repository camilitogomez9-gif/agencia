#!/usr/bin/env python3
"""
HPF · smoke integral de los cambios pedidos por Oscar en la reunión del 2026-08-11.

Un caso por item, contra el W6 vivo. Los veredictos se sacan de lo que efectivamente le
llega al cliente (texto + adjuntos), no de lo que el agente dice que hizo.

Uso:  python3 scripts/testing/hpf-smoke-reunion-oscar-2026-08-11.py [--solo 3,4,11]
"""
import argparse
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[2]
W6 = "https://[TU-INSTANCIA-N8N]/webhook/hpf-w6-conversacion"
CAT = REPO / "clients/HPF_HappyFlops/00_migracion_ghl/06_registro/catalogo-airtable.json"

FICHA = {}
for f in json.loads(CAT.read_text(encoding="utf-8")):
    u = (f.get("ghl_media") or {}).get("url")
    if u:
        FICHA.setdefault(u, set()).add(
            f"{f.get('evento') or f.get('tabla')}/{f.get('producto')}")

CATALOGOS_PANTUFLA = {"Pantuflas de satín boda personalizadas", "Catalogo pantuflas"}


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


def post(sid, texto, primer=False, timeout=300):
    body = {"sessionId": sid, "texto": texto, "contactId": None,
            "opportunityId": None, "primer_contacto": primer}
    req = urllib.request.Request(W6, data=json.dumps(body).encode(), headers=H, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.loads(r.read().decode() or "null")
            d = d[0] if isinstance(d, list) and d else d
    except urllib.error.HTTPError as e:
        return {"_http": e.code, "_raw": e.read().decode()[:400], "partes": []}
    except Exception as e:
        return {"_err": str(e)[:200], "partes": []}
    return d


def turno(sid, texto, primer=False, mostrar=True):
    d = post(sid, texto, primer)
    partes = d.get("partes") or []
    txt = "\n".join(p.get("texto") or "" for p in partes)
    adj = [a for p in partes for a in (p.get("adjuntos") or [])]
    if mostrar:
        print(f"    → «{texto[:64]}»")
        for p in partes:
            print("        · " + (p.get("texto") or "").replace("\n", " ⏎ ")[:112])
        for a in adj:
            print(f"        📎 {a.rsplit('/', 1)[-1][:30]:32} {', '.join(sorted(FICHA.get(a, {'(?)'})))[:60]}")
        if d.get("_http") or d.get("_err"):
            print(f"        ⚠️  {d.get('_http') or ''} {str(d.get('_raw') or d.get('_err'))[:200]}")
    return d, txt, adj


def nombres(adj):
    return {n.split("/", 1)[-1] for a in adj for n in FICHA.get(a, set())}


R = []


def reg(item, titulo, ok, detalle):
    R.append((item, titulo, ok, detalle))
    print(f"    {'✅' if ok else '❌'} item {item} · {titulo}\n        {detalle}")


# ─────────────────────────────────────────────────────────────────────────────
def caso_3(base):
    sid = f"sm-{base}-3"
    print("\n=== item 3 · negritas en el saludo fijo ===")
    _, txt, _ = turno(sid, "hola", primer=True)
    falta = [m for m in ("*Happy Flops*", "*Rebeca*", "*Boda*", "*XV Años*", "*Otros*")
             if m not in txt]
    reg("3", "saludo con negritas", not falta,
        "todas las negritas presentes" if not falta else f"faltan: {falta}")


def caso_4(base):
    print("\n=== item 4 · la pantufla de peluche no arrastra el catálogo de satín ===")
    sid = f"sm-{base}-4a"
    turno(sid, "hola", primer=True, mostrar=False)
    turno(sid, "es para una boda", mostrar=False)
    _, _, adj = turno(sid, "quiero las pantuflas de moño de peluche, que diseños tienen?")
    n = nombres(adj)
    cat = CATALOGOS_PANTUFLA & n
    ok = bool(n) and not cat and "Pantuflas mono peluche" in n
    reg("4", "peluche sin catálogo de satín", ok,
        f"fichas={sorted(n)}" + (f" · SE COLÓ {sorted(cat)}" if cat else ""))

    sid = f"sm-{base}-4b"
    turno(sid, "hola", primer=True, mostrar=False)
    turno(sid, "es para una boda", mostrar=False)
    _, _, adj2 = turno(sid, "me interesan las pantuflas, que opciones hay?")
    n2 = nombres(adj2)
    ok2 = bool(CATALOGOS_PANTUFLA & n2)
    reg("4b", "el caso general sigue trayendo el catálogo", ok2, f"fichas={sorted(n2)}")


def caso_678(base):
    sid = f"sm-{base}-678"
    print("\n=== items 6-8 · una conversación de XV recibe fichas de XV ===")
    turno(sid, "hola", primer=True, mostrar=False)
    turno(sid, "es para los 15 años de mi hija", mostrar=False)
    _, _, adj = turno(sid, "me interesan los cilindros y los termos")
    ajenos = [a for a in adj
              if FICHA.get(a) and not any(o.startswith("XV/") for o in FICHA[a])]
    reg("6-8", "fichas del evento correcto", bool(adj) and not ajenos,
        f"{len(adj)} adjunto(s), 0 ajenos a XV" if not ajenos
        else f"ajenos: {[sorted(FICHA[a]) for a in ajenos]}")


def caso_10(base):
    sid = f"sm-{base}-10"
    print("\n=== item 10 · '¿de dónde son?' da dirección + Maps, distinto de '¿es seguro?' ===")
    turno(sid, "hola", primer=True, mostrar=False)
    turno(sid, "es para una boda", mostrar=False)
    _, txt_ub, _ = turno(sid, "y ustedes de donde son? tienen tienda fisica?")
    tiene_dir = "ZAVALA" in txt_ub.upper() or "SAN JUAN BOSCO" in txt_ub.upper()
    tiene_map = "goo.su" in txt_ub
    md = bool(re.search(r"\[[^\]]+\]\(https?://", txt_ub))
    reg("10", "ubicación con dirección y mapa", tiene_dir and tiene_map and not md,
        f"dirección={tiene_dir} maps={tiene_map} markdown_roto={md}")

    sid2 = f"sm-{base}-10b"
    turno(sid2, "hola", primer=True, mostrar=False)
    turno(sid2, "es para una boda", mostrar=False)
    _, txt_seg, _ = turno(sid2, "como se que es seguro comprarles? no sera estafa?")
    ok2 = ("ZAVALA" not in txt_seg.upper()) and len(txt_seg.strip()) > 20
    reg("10b", "'¿es seguro?' sigue con su propia respuesta", ok2,
        "no devuelve la dirección" if ok2 else "devolvió la dirección (no se separaron)")


def caso_11_12(base):
    sid = f"sm-{base}-11"
    print("\n=== items 11 y 12 · cotización, oferta, precio de lo ofrecido y cierre de pago ===")
    turno(sid, "hola", primer=True, mostrar=False)
    turno(sid, "es para una boda", mostrar=False)
    _, txt_cot, _ = turno(sid, "quiero 60 sandalias gruesas al codigo postal 44100, cuanto sale?")

    # item 1/2 — negritas y emojis en la cotización que genera el Recolector
    negritas = len(re.findall(r"\*[^*\n]{2,60}\*", txt_cot))
    emojis = len([c for c in txt_cot if ord(c) > 0x2500])
    reg("1-2", "la cotización sale con negritas y emojis", negritas >= 2 and emojis >= 1,
        f"{negritas} tramo(s) en negrita, {emojis} emoji(s)")

    # item 12 — "¿cuánto cuestan?" referido a lo último ofrecido.
    # El producto ofrecido NO se asume: se extrae del "ya que pides X, ¿le gustaría agregar
    # Y?" del turno anterior. La primera versión de este test daba por hecho que la oferta
    # era mandiles y marcaba falla cuando el agente contestaba bien por lo que realmente
    # había ofrecido (cilindros).
    PRODUCTOS = ("sandalias", "cilindros", "mandiles", "anticruda", "pantuflas", "vasos",
                 "termos", "costales")
    m = re.search(r"(?:le |te )?gustar[íi]a agregar ([^?¿\n.!]{0,80})", txt_cot, re.I)
    ofrecidos = {p for p in PRODUCTOS if p in (m.group(1).lower() if m else "")}
    ya_cotizados = {p for p in PRODUCTOS
                    if re.search(rf"\d[\d,.]*\s*\*?{p}", txt_cot, re.I)}
    _, txt_of, _ = turno(sid, "cuanto cuestan?")
    resp = txt_of.lower()
    menciona_ofrecido = bool(ofrecidos & {p for p in PRODUCTOS if p in resp})
    solo_repite = (not menciona_ofrecido) and bool(
        (ya_cotizados - ofrecidos) & {p for p in PRODUCTOS if p in resp})
    if not ofrecidos:
        reg("12", "'¿cuánto cuestan?' contesta por lo ofrecido", False,
            "no pude detectar qué ofreció el turno anterior: caso no concluyente")
    else:
        reg("12", "'¿cuánto cuestan?' contesta por lo ofrecido", menciona_ofrecido,
            f"ofrecido={sorted(ofrecidos)} · responde por={sorted({p for p in PRODUCTOS if p in resp})}"
            + (" · REPITIÓ lo ya cotizado" if solo_repite else ""))

    # item 11 — datos de pago primero, comprobante después
    _, txt_pago, adj_pago = turno(sid, "si, quiero avanzar, pasame los datos para pagar")
    marcador = "url1234" in txt_pago
    pdf = [a for a in adj_pago if a.lower().endswith(".pdf")]
    pide_comp = bool(re.search(r"comprobante|captura|foto del pago", txt_pago, re.I))
    ok = (not marcador) and bool(pdf)
    reg("11", "manda el PDF de números de cuenta (y no el marcador crudo)", ok,
        f"marcador_crudo={marcador} pdf_adjunto={len(pdf)} pide_comprobante={pide_comp}")
    reg("11b", "no pide comprobante sin haber mandado los datos",
        bool(pdf) or not pide_comp,
        "pide comprobante junto con los datos" if pdf and pide_comp
        else ("no pide comprobante" if not pide_comp else "pide comprobante SIN datos ❗"))


CASOS = {"3": caso_3, "4": caso_4, "6-8": caso_678, "10": caso_10, "11-12": caso_11_12}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", default="")
    a = ap.parse_args()
    base = int(time.time())
    pedidos = [c.strip() for c in a.solo.split(",") if c.strip()] or list(CASOS)
    for c in pedidos:
        if c not in CASOS:
            print(f"⚠️  caso desconocido: {c} (hay: {', '.join(CASOS)})")
            continue
        CASOS[c](base)

    print("\n" + "=" * 70)
    print(f"{'item':8} {'':2} resultado")
    for item, titulo, ok, _ in R:
        print(f"{item:8} {'✅' if ok else '❌'} {titulo}")
    malos = [r for r in R if not r[2]]
    print(f"\n{len(R) - len(malos)}/{len(R)} en verde")
    sys.exit(1 if malos else 0)


if __name__ == "__main__":
    main()
