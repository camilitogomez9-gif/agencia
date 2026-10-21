#!/usr/bin/env python3
"""
HPF · punto 9 — ¿qué agente se equivoca cuando el lead dice "¿cuánto cuestan?"?

EL PUNTO
Oscar (11/8): el bot ofrece "ya que pides sandalias, ¿le gustaría agregar mandiles o kit
anticruda?", el lead responde "¿cuánto cuestan?" y el bot le repite los precios de lo YA
cotizado en vez de responder por lo ofrecido. *"La gente cuando pone esto, se refiere a esto
que le estás ofreciendo."*

POR QUÉ ESTE SCRIPT EXISTE
En la llamada se asumió que el arreglo era subir el modelo, y lo primero que uno haría es subir
el del Recolector, que es quien cotiza. Pero en la corrida que falló el 12/8 quien eligió mal el
producto fue **Products** (`gpt-4.1-mini`, temp 0.3 — el único agente con temperatura alta del
workflow). Subir el modelo equivocado costaría plata y no arreglaría nada.

Así que primero se mide: se corre el caso N veces y, por cada una, se lee la EJECUCIÓN para ver
qué produjo cada nodo. La respuesta final no alcanza para saber quién falló.

Qué mira, por corrida:
  · qué producto ofreció el turno anterior (se extrae del "¿le gustaría agregar X?")
  · qué emitió `Leer Products` (evento + productos) — el candidato principal
  · qué emitió `Leer canónicos`
  · por qué rama salió la respuesta (step_3 fichas vs step_4 Recolector)
  · si la respuesta final habla de lo ofrecido o de lo ya cotizado

USO
    hpf-diagnostico-punto9.py --n 6
    hpf-diagnostico-punto9.py --n 6 --etiqueta despues-de-subir-modelo
"""
import argparse
import json
import pathlib
import re
import time
import urllib.error
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[2]
W6 = "https://[TU-INSTANCIA-N8N]/webhook/hpf-w6-conversacion"
WF = "cNmJCP2qVhdtfCH0"
PRODUCTOS = ("sandalias", "cilindros", "mandiles", "anticruda", "pantuflas",
             "vasos", "termos", "costales")


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
N8N = E["HPF_N8N_API"].rstrip("/")
KEY = E.get("HPF_N8N_API_KEY") or E["N8N_API_KEY"]


def post(sid, texto, primer=False):
    body = {"sessionId": sid, "texto": texto, "contactId": None,
            "opportunityId": None, "primer_contacto": primer}
    req = urllib.request.Request(W6, data=json.dumps(body).encode(), headers=H, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            d = json.loads(r.read().decode() or "null")
            return d[0] if isinstance(d, list) and d else (d or {})
    except urllib.error.HTTPError as e:
        return {"_http": e.code, "partes": []}


def api(path):
    r = urllib.request.Request(N8N + path,
                               headers={"X-N8N-API-KEY": KEY, "Accept": "application/json"})
    with urllib.request.urlopen(r, timeout=120) as x:
        return json.loads(x.read().decode())


def ultima_runData():
    ex = api(f"/api/v1/executions?workflowId={WF}&limit=1&includeData=false").get("data") or []
    if not ex:
        return {}
    d = api(f"/api/v1/executions/{ex[0]['id']}?includeData=true")
    return ex[0]["id"], (((d.get("data") or {}).get("resultData") or {}).get("runData") or {})


def salida(rd, nodo):
    try:
        return rd[nodo][0]["data"]["main"][0][0]["json"]
    except Exception:
        return None


def texto_de(d):
    return "\n".join(p.get("texto") or "" for p in (d.get("partes") or []))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--etiqueta", default="")
    a = ap.parse_args()
    base = int(time.time())
    filas = []

    for i in range(a.n):
        sid = f"p9-{base}-{i}"
        post(sid, "hola", primer=True)
        post(sid, "es para una boda")
        cot = post(sid, "quiero 60 sandalias gruesas al codigo postal 44100, cuanto sale?")
        t_cot = texto_de(cot)
        m = re.search(r"(?:le |te )?gustar[íi]a agregar ([^?¿\n.!]{0,80})", t_cot, re.I)
        ofrecidos = {p for p in PRODUCTOS if p in (m.group(1).lower() if m else "")}
        ya_cot = {p for p in PRODUCTOS if re.search(rf"\d[\d,.]*\s*\*?{p}", t_cot, re.I)}

        resp = post(sid, "cuanto cuestan?")
        t_resp = texto_de(resp)
        habla_de = {p for p in PRODUCTOS if p in t_resp.lower()}

        _id, rd = ultima_runData()
        lp = salida(rd, "Leer Products") or {}
        lc = salida(rd, "Leer canónicos") or {}
        rama = ("Products" if "Leer Products" in rd else
                "Recolector" if "Recolector" in rd else "?")

        acierta = bool(ofrecidos & habla_de)
        repite = (not acierta) and bool((ya_cot - ofrecidos) & habla_de)
        filas.append({
            "i": i, "exec": _id, "ofrecido": sorted(ofrecidos), "responde": sorted(habla_de),
            "acierta": acierta, "repite_lo_cotizado": repite,
            "step": resp.get("step"), "rama": rama,
            "products_productos": lp.get("productos"),
            "canonicos_productos": lc.get("productos"),
            "nodos": sorted(rd.keys()),
        })
        f = filas[-1]
        print(f"  [{i+1}/{a.n}] {'✅' if acierta else '❌'} ofrecido={f['ofrecido']} "
              f"responde={f['responde']} step={f['step']} "
              f"Products.productos={f['products_productos']}")

    ok = sum(1 for f in filas if f["acierta"])
    print(f"\n{'='*70}\nTASA: {ok}/{a.n}" + (f"  ({a.etiqueta})" if a.etiqueta else ""))
    print("referencia del 12/8 con el delta de prompt: 4/7\n")

    malos = [f for f in filas if not f["acierta"]]
    if malos:
        print("En las corridas que fallaron, quién eligió mal:")
        for f in malos:
            elige_mal = (f["products_productos"] is not None
                         and not (set(map(str.lower, f["products_productos"] or []))
                                  & set(f["ofrecido"])))
            print(f"  exec {f['exec']}  step={f['step']}  "
                  f"Products emitió {f['products_productos']} → "
                  f"{'PRODUCTS eligió mal' if elige_mal else 'Products OK, falla aguas abajo'}")
        culpa_products = sum(
            1 for f in malos
            if f["products_productos"] is not None
            and not (set(map(str.lower, f["products_productos"] or [])) & set(f["ofrecido"])))
        print(f"\n  → Products responsable en {culpa_products}/{len(malos)} de las fallas")
        print("  → el modelo a subir es el de "
              + ("Products (LM Products, hoy gpt-4.1-mini temp 0.3)"
                 if culpa_products > len(malos) / 2
                 else "el Recolector (LM Recolector, hoy gpt-4o temp 0.2)"))

    sal = REPO / f"clients/HPF_HappyFlops/07_testing/baseline-2026-08-14/punto9-{a.etiqueta or 'antes'}.json"
    sal.parent.mkdir(parents=True, exist_ok=True)
    sal.write_text(json.dumps({"tasa": f"{ok}/{a.n}", "corridas": filas},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n→ {sal.relative_to(REPO)}")


if __name__ == "__main__":
    main()
