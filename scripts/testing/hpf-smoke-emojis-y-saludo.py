#!/usr/bin/env python3
"""
HPF · guardia de emojis y del saludo fijo.

Oscar (2026-08-12): las opciones de evento llegaban SIN emojis y con un bullet "•" que no
existe en el original, y el emoji del saludo llegaba partido como "☺♀". Su instrucción:
usar SOLO los emojis que usaba el agente original, porque son los únicos que se muestran
bien en el canal.

Este test hace dos cosas:
  1. SALUDO — compara byte a byte lo que llega contra el saludo canónico compuesto
     (base congelada + deltas). Cualquier emoji partido o carácter agregado lo caza.
  2. GUARDIA DE EMOJIS — recorre una conversación completa y falla si en CUALQUIER mensaje
     aparece un emoji que no esté en el inventario de los prompts congelados.

El inventario NO está hardcodeado: se extrae de 04_agents/base-prod-2026-08-06/*.md en cada
corrida, así que si mañana se agrega un emoji al original, este test lo acepta solo.
"""
import argparse
import importlib.util
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[2]
BASE = REPO / "clients/HPF_HappyFlops/04_agents/base-prod-2026-08-06"
W6 = "https://[TU-INSTANCIA-N8N]/webhook/hpf-w6-conversacion"

SEQ = re.compile(
    "(?:[\U0001F000-\U0001FAFF☀-➿️⃣‍"
    "\U0001F1E6-\U0001F1FF〰〽㊗㊙©®]"
    "[️‍\U0001F3FB-\U0001F3FF⃣]*)+")


def emojis(t):
    return {m.group(0) for m in SEQ.finditer(t or "") if m.group(0).strip(" ‍️")}


def inventario_original():
    """El set permitido, extraído de los prompts congelados."""
    permitidos = set()
    for p in BASE.glob("*.md"):
        permitidos |= emojis(p.read_text(encoding="utf-8"))
    # además de las secuencias completas, se aceptan sus piezas sueltas: el original usa
    # "🤵👰" pegados y un mensaje podría traer solo uno de los dos legítimamente.
    piezas = set()
    for s in permitidos:
        for m in re.finditer("[\U0001F000-\U0001FAFF☀-➿][️‍]*", s):
            piezas.add(m.group(0))
    return permitidos | piezas


def saludo_canonico():
    s = importlib.util.spec_from_file_location(
        "a", REPO / "scripts/utilities/hpf-aplicar-deltas-prompt.py")
    A = importlib.util.module_from_spec(s)
    s.loader.exec_module(A)
    txt = A.componer("starter", A.cargar_deltas()["starter"], estricto=True)[0]
    i = txt.index("“Hola")
    j = txt.index("”", i)
    return txt[i + 1:j]


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


def turno(sid, texto, primer=False):
    body = {"sessionId": sid, "texto": texto, "contactId": None,
            "opportunityId": None, "primer_contacto": primer}
    req = urllib.request.Request(W6, data=json.dumps(body).encode(), headers=H, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            d = json.loads(r.read().decode() or "null")
            d = d[0] if isinstance(d, list) and d else d
    except urllib.error.HTTPError as e:
        return {"partes": [], "_http": e.code}
    return d


GUION = [
    ("hola", True),
    ("es para una boda", False),
    ("me interesan las sandalias gruesas", False),
    ("quiero 60 al codigo postal 44100", False),
    ("si, quiero avanzar, pasame los datos para pagar", False),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sid", default=str(int(time.time())))
    a = ap.parse_args()
    sid = f"smoke-emoji-{a.sid}"
    permitidos = inventario_original()
    print(f"inventario del original: {len(permitidos)} secuencias/piezas permitidas")

    fallas = []

    # ── 1. saludo byte a byte
    print("\n=== saludo fijo, byte a byte ===")
    # `Partir en burbujas` corta por párrafo y hace trim() de cada burbuja — con razón: el
    # prompt original tiene espacios al final de línea que no deben viajar. Así que la
    # comparación normaliza igual en los dos lados, si no da un falso positivo por un espacio.
    def norm(t):
        return "\n\n".join(p.strip() for p in re.split(r"\n\s*\n", t) if p.strip())

    esperado = norm(saludo_canonico())
    d = turno(sid, *GUION[0])
    recibido = norm("\n\n".join((p.get("texto") or "") for p in (d.get("partes") or [])))
    if recibido == esperado:
        print("  ✅ idéntico al canónico")
    else:
        fallas.append("el saludo no llega byte-idéntico al canónico")
        print("  ❌ DIFIERE")
        print(f"     esperado ({len(esperado)}): {esperado!r}")
        print(f"     recibido ({len(recibido)}): {recibido!r}")
        for k, (x, y) in enumerate(zip(esperado, recibido)):
            if x != y:
                print(f"     primer byte distinto en {k}: "
                      f"esperado U+{ord(x):04X} · recibido U+{ord(y):04X}")
                break
    # los emojis del saludo, uno por uno
    for e in ("\U0001F935\U0001F470", "\U0001F382\U0001F973", "\U0001F47C\U0001F3E2"):
        if e in recibido:
            print(f"  ✅ {e} presente en las opciones")
        else:
            fallas.append(f"falta el emoji {e} en las opciones de evento")
            print(f"  ❌ falta {e}")
    for basura in ("•", "**"):
        if basura in recibido:
            fallas.append(f"el saludo trae {basura!r}, que no está en el original")
            print(f"  ❌ aparece {basura!r}")

    # ── 2. guardia de emojis sobre la conversación entera
    print("\n=== guardia de emojis sobre la conversación ===")
    vistos = {}
    for texto, primer in GUION[1:]:
        d = turno(sid, texto, primer)
        for p in (d.get("partes") or []):
            t = p.get("texto") or ""
            for e in emojis(t):
                vistos.setdefault(e, []).append(texto[:34])
    fuera = {e: v for e, v in vistos.items() if e not in permitidos}
    print(f"  emojis usados: {sorted(vistos)}")
    if fuera:
        fallas.append(f"emojis fuera del set original: {sorted(fuera)}")
        for e, v in sorted(fuera.items()):
            cps = " ".join(f"U+{ord(c):04X}" for c in e)
            print(f"  ❌ {e!r} ({cps}) — en respuesta a: {v[0]!r}")
    else:
        print("  ✅ todos dentro del set del original")

    print("\n" + "=" * 66)
    if fallas:
        print("❌ FALLA")
        for f in fallas:
            print(f"   · {f}")
        sys.exit(1)
    print("✅ saludo byte-exacto y ningún emoji fuera del set original")


if __name__ == "__main__":
    main()
