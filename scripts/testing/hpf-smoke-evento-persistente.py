#!/usr/bin/env python3
"""
HPF · smoke del evento persistente (W6).

Prueba lo que Oscar reportó: en una conversación de XV, las fichas de cilindros salían de
Boda. El test recorre una conversación de XV y verifica que las fichas que vuelven sean las
de XV, comparando el media_url contra el catálogo real — no contra lo que diga el agente.

Uso:  python3 scripts/testing/hpf-smoke-evento-persistente.py [--sid SUFIJO]
"""
import argparse
import json
import pathlib
import sys
import time
import urllib.error
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[2]
W6 = "https://[TU-INSTANCIA-N8N]/webhook/hpf-w6-conversacion"
W9 = "https://[TU-INSTANCIA-N8N]/webhook/hpf-w9-sql"
CAT = REPO / "clients/HPF_HappyFlops/00_migracion_ghl/06_registro/catalogo-airtable.json"

# media_url -> "evento/producto", construido del catálogo real. Es el oráculo: si vuelve
# un archivo de Boda en una conversación de XV, se ve acá sin depender del texto del agente.
ORACULO = {}
for f in json.loads(CAT.read_text(encoding="utf-8")):
    u = (f.get("ghl_media") or {}).get("url")
    if u:
        ORACULO.setdefault(u, []).append(
            f"{f.get('evento') or f.get('tabla')}/{f.get('producto')}")


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


def post(url, body, timeout=240):
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers=H, method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode() or "null"), time.time() - t0
    except urllib.error.HTTPError as e:
        return e.code, {"_raw": e.read().decode()[:600]}, time.time() - t0
    except Exception as e:
        return "ERR", {"_raw": str(e)[:300]}, time.time() - t0


def prim(r):
    return r[0] if isinstance(r, list) and r else (r if isinstance(r, dict) else {})


def turno(sid, texto, primer=False):
    body = {"sessionId": sid, "texto": texto, "contactId": None,
            "opportunityId": None, "primer_contacto": primer}
    s, r, dur = post(W6, body)
    d = prim(r)
    partes = d.get("partes") or []
    adj = [a for p in partes for a in (p.get("adjuntos") or [])]
    print(f"\n  → «{texto}»   http={s} {dur:.1f}s  step={d.get('step')} "
          f"burbujas={len(partes)}")
    for p in partes:
        t = (p.get("texto") or "").replace("\n", " ⏎ ")
        print(f"       · {t[:118]}")
    for a in adj:
        dueños = ORACULO.get(a, ["(no está en el catálogo)"])
        print(f"       📎 {a.rsplit('/', 1)[-1][:34]:36} → {', '.join(dueños)}")
    if s != 200:
        print(f"       ⚠️  {str(d)[:300]}")
    return d, adj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sid", default=str(int(time.time())))
    a = ap.parse_args()
    sid = f"smoke-evento-{a.sid}"
    print(f"sessionId = {sid}")

    fallas = []

    print("\n=== T1 · saludo ===")
    turno(sid, "hola, buenas tardes", primer=True)

    print("\n=== T2 · el lead dice que es de XV ===")
    d2, _ = turno(sid, "es para los 15 años de mi hija")

    print("\n=== T3 · pide cilindros (el turno que fallaba) ===")
    d3, adj3 = turno(sid, "me interesan los cilindros, cuantos diseños tienen?")

    # ── veredicto sobre los adjuntos
    # Un archivo sólo viola el evento si NINGUNO de sus dueños es XV. Los 9 archivos
    # compartidos por los tres eventos (los 5 videos + correas/tintas/bolsa/tapas) son
    # legítimos: son el mismo asset a propósito, y Oscar confirmó que los videos van bien.
    def ajeno(a):
        dueños = ORACULO.get(a, [])
        return bool(dueños) and not any(o.startswith("XV/") for o in dueños)

    ajenos = [a for a in adj3 if ajeno(a)]
    propios = [a for a in adj3 if not ajeno(a)]
    print("\n=== veredicto ===")
    if not adj3:
        fallas.append("T3 no devolvió ningún adjunto: no se puede juzgar el evento")
        print("  ⚠️  T3 sin adjuntos")
    elif ajenos:
        fallas.append(f"T3 devolvió {len(ajenos)} archivo(s) que no son de XV")
        for a in ajenos:
            print(f"  ❌ archivo ajeno al evento: {ORACULO[a]}")
    else:
        print(f"  ✅ T3: {len(propios)} adjunto(s), todos válidos para XV")
        for a in propios:
            excl = [o for o in ORACULO[a] if o.startswith("XV/")]
            comp = len(ORACULO[a]) > 1
            print(f"       {excl[0]}{'  (asset compartido entre eventos)' if comp else ''}")

    # ── caso adversarial: pedir un producto que SÓLO existe en Boda.
    # Si el evento se respeta, el agente no puede contestar con fichas de mandiles de Boda:
    # los mandiles no existen para XV. Es el test que separa "el estado manda" de
    # "el LLM eligió bien por casualidad".
    print("\n=== T4 · adversarial: mandiles (producto exclusivo de Boda) en un chat de XV ===")
    _, adj4 = turno(sid, "y los mandiles cuanto salen?")
    mandiles_boda = [a for a in adj4
                     if any("Mandil" in o and o.startswith("Boda/") for o in ORACULO.get(a, []))]
    if mandiles_boda:
        fallas.append("T4 devolvió fichas de mandiles de Boda en una conversación de XV")
        for a in mandiles_boda:
            print(f"  ❌ {ORACULO[a]}")
    else:
        print("  ✅ T4: no se colaron fichas de mandiles de Boda")

    # ── estado persistido
    print("\n=== estado en la base ===")
    s, r, _ = post(W9, {"consulta": "estado_sesion", "param": sid})
    rows = r if isinstance(r, list) else [r]
    fila = next((x for x in rows if isinstance(x, dict) and x.get("session_id")), None)
    if fila:
        print(f"  hpf_estado_sesion: session_id={fila['session_id']} evento={fila.get('evento')!r}")
        if (fila.get("evento") or "").strip().upper() not in ("XV", "XV AÑOS"):
            fallas.append(f"el evento persistido es {fila.get('evento')!r}, esperaba XV")
    else:
        print(f"  ⚠️  no pude leer hpf_estado_sesion ({str(r)[:200]})")
        print("      (si dice 'no está en la lista blanca', hay que agregar la consulta a W9)")

    print("\n" + "=" * 62)
    if fallas:
        print("❌ FALLA")
        for f in fallas:
            print(f"   · {f}")
        sys.exit(1)
    print("✅ el evento se respeta: conversación de XV → fichas de XV")


if __name__ == "__main__":
    main()
