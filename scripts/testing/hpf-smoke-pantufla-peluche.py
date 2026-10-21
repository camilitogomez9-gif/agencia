#!/usr/bin/env python3
"""
HPF · smoke de la pantufla de peluche (item 4 de la reunión del 2026-08-11).

Oscar: "En esta de peluche, este no tiene catálogo. Le están mandando el catálogo igual que
acá el de satín, para que en esa de moño de peluche se lo quiten, porque son diferentes
diseños. El video está bien, nada más el catálogo hay que quitarlo."

Qué se verifica, contra el catálogo real y no contra el texto del agente:
  A. lead que pregunta por la pantufla DE PELUCHE  → NO recibe el catálogo de satín
  B. lead que pregunta por pantuflas EN GENERAL    → SÍ lo sigue recibiendo (no romper el caso bueno)
  C. lead que pregunta por la de SATÍN             → SÍ lo recibe
  D. ninguno de los tres se queda sin ninguna imagen (el riesgo de acotar el match)
"""
import json
import pathlib
import sys
import time
import urllib.error
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[2]
W6 = "https://[TU-INSTANCIA-N8N]/webhook/hpf-w6-conversacion"
CAT = REPO / "clients/HPF_HappyFlops/00_migracion_ghl/06_registro/catalogo-airtable.json"

# los catálogos de DISEÑOS de pantuflas (los que no deben acompañar a la de peluche)
CATALOGOS_SATIN = {"Pantuflas de satín boda personalizadas", "Catalogo pantuflas"}

NOMBRE = {}
for f in json.loads(CAT.read_text(encoding="utf-8")):
    u = (f.get("ghl_media") or {}).get("url")
    if u:
        NOMBRE.setdefault(u, set()).add(f.get("producto"))


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


def post(body, timeout=240):
    req = urllib.request.Request(W6, data=json.dumps(body).encode(), headers=H, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.loads(r.read().decode() or "null")
            return r.status, (d[0] if isinstance(d, list) and d else d)
    except urllib.error.HTTPError as e:
        return e.code, {"_raw": e.read().decode()[:400]}


def conversacion(sid, evento_txt, pregunta):
    post({"sessionId": sid, "texto": "hola", "contactId": None,
          "opportunityId": None, "primer_contacto": True})
    post({"sessionId": sid, "texto": evento_txt, "contactId": None,
          "opportunityId": None, "primer_contacto": False})
    s, d = post({"sessionId": sid, "texto": pregunta, "contactId": None,
                 "opportunityId": None, "primer_contacto": False})
    adj = [a for p in (d.get("partes") or []) for a in (p.get("adjuntos") or [])]
    nombres = sorted({n for a in adj for n in NOMBRE.get(a, {"(desconocido)"})})
    return s, nombres


CASOS = [
    ("A", "quiero las pantuflas de moño de peluche, que diseños tienen?",
     False, "la de peluche NO debe traer el catálogo de diseños de satín"),
    ("B", "me interesan las pantuflas, que opciones hay?",
     True, "pantuflas en general SÍ debe traer el catálogo"),
    ("C", "quiero las pantuflas de moño de satin",
     False, "la de satín trae su propia ficha; el catálogo genérico es opcional"),
]


def main():
    base = int(time.time())
    fallas = []
    for cid, pregunta, espera_catalogo, nota in CASOS:
        sid = f"smoke-peluche-{base}-{cid}"
        print(f"\n=== caso {cid} · «{pregunta}» ===")
        print(f"    ({nota})")
        s, nombres = conversacion(sid, "es para una boda", pregunta)
        print(f"    http={s}  fichas: {', '.join(nombres) or '(ninguna)'}")
        tiene_cat = bool(CATALOGOS_SATIN & set(nombres))
        if not nombres:
            fallas.append(f"{cid}: el lead no recibió ninguna imagen")
            print("    ❌ sin imágenes")
            continue
        if cid == "A":
            if tiene_cat:
                fallas.append(f"{cid}: sigue llegando el catálogo de satín con la de peluche")
                print("    ❌ llegó el catálogo de satín")
            elif "Pantuflas mono peluche" not in nombres:
                fallas.append(f"{cid}: no llegó la ficha de la pantufla de peluche")
                print("    ❌ no llegó la ficha de peluche")
            else:
                print("    ✅ llegó la de peluche y NO el catálogo de satín")
        elif cid == "B":
            if not tiene_cat:
                fallas.append(f"{cid}: se rompió el caso general, ya no llega el catálogo")
                print("    ❌ el caso general perdió el catálogo")
            else:
                print("    ✅ el caso general sigue trayendo el catálogo")
        else:
            if "Pantuflas mono satin" in nombres:
                print("    ✅ llegó la ficha de satín")
            else:
                fallas.append(f"{cid}: no llegó la ficha de satín")
                print("    ❌ no llegó la ficha de satín")

    print("\n" + "=" * 62)
    if fallas:
        print("❌ FALLA")
        for f in fallas:
            print(f"   · {f}")
        sys.exit(1)
    print("✅ la pantufla de peluche ya no arrastra el catálogo de satín")


if __name__ == "__main__":
    main()
