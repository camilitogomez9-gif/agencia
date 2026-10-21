#!/usr/bin/env python3
"""
HPF · edición dirigida de workflows n8n en devn8n.

Existe porque los generadores (`scripts/generators/hpf-gen-w*.py`) quedaron atrás del vivo:
W1 tiene 14 nodos y W6 tiene 9 que el repo no conoce, y W7/W8/W9/W10 no están en el repo.
Regenerar y deployar los borraría. Así que los cambios se aplican como parches de nodo
sobre el JSON vivo, con el anchor verificado antes de escribir.

Uso:
    # ver un nodo
    hpf-deploy-workflow.py --show W6 'Leer Products'

    # aplicar un parche declarado en un .json de parches
    hpf-deploy-workflow.py --apply parches/mi-parche.json

    # volver a un snapshot
    hpf-deploy-workflow.py --restore clients/HPF_HappyFlops/03_workflows/ghl-live-2026-08-12/W6.json

Formato de un parche:
{
  "wf": "W6",
  "descripcion": "por qué",
  "ediciones": [
    {"nodo": "Leer Products", "campo": "parameters.jsCode",
     "anchor": "texto literal y único", "reemplazo": "texto nuevo"}
  ]
}
`anchor` tiene que aparecer exactamente una vez en el campo o el parche aborta sin escribir.
"""
import argparse
import json
import pathlib
import sys
import urllib.error
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[2]
SNAP = REPO / "clients/HPF_HappyFlops/03_workflows/ghl-live-2026-08-12"

IDS = {
    "W0": "VK4M7VQm8CMefbty", "W1": "nA14dNwJ7VS3YMYr", "W2": "MdbOREN56lfQTYlM",
    "W3": "vSLHOawn2bFVXyOK", "W4": "psGRDByGNjHQ2DVT", "W5": "mmo29FTvIquxksWV",
    "W6": "cNmJCP2qVhdtfCH0", "W7": "m8KhaZV3nSjJ55ci", "W8": "Ki7IRFYQn1mqOh5p",
    "W9": "2Govwp16YAcpgJ2C", "W10": "fpKvo0ECWIhFcckE",
}
# n8n rechaza el PUT si el body trae campos de sólo lectura.
PUT_KEYS = ("name", "nodes", "connections", "settings", "staticData")


def env():
    e = {}
    for line in (REPO / ".env").read_text().splitlines():
        if line.strip() and not line.strip().startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            e[k.strip()] = v.strip().strip('"').strip("'")
    return e


E = env()
BASE = E["HPF_N8N_API"].rstrip("/")
KEY = E.get("HPF_N8N_API_KEY") or E["N8N_API_KEY"]


def api(path, method="GET", body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        BASE + path, data=data, method=method,
        headers={"X-N8N-API-KEY": KEY, "Accept": "application/json",
                 "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read().decode() or "null")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:600]


def bajar(wf):
    s, w = api(f"/api/v1/workflows/{IDS[wf]}")
    if s != 200:
        sys.exit(f"❌ no pude bajar {wf}: {s} {w}")
    return w


def subir(wf, w):
    body = {k: w[k] for k in PUT_KEYS if k in w}
    s, r = api(f"/api/v1/workflows/{IDS[wf]}", "PUT", body)
    if s != 200:
        sys.exit(f"❌ PUT {wf} falló: {s} {r}")
    return r


def _pasos(campo):
    """'parameters.messages.values[1].content' -> ['parameters','messages','values',1,'content']"""
    out = []
    for parte in campo.split("."):
        while "[" in parte:
            nombre, resto = parte.split("[", 1)
            if nombre:
                out.append(nombre)
            i, parte = resto.split("]", 1)
            out.append(int(i))
        if parte:
            out.append(parte)
    return out


def get_campo(nodo, campo):
    cur = nodo
    for p in _pasos(campo):
        try:
            cur = cur[p]
        except (KeyError, IndexError, TypeError):
            return None
    return cur


def set_campo(nodo, campo, valor):
    pasos = _pasos(campo)
    cur = nodo
    for p in pasos[:-1]:
        cur = cur[p]
    cur[pasos[-1]] = valor


def aplicar(ruta, dry=False):
    p = json.loads(pathlib.Path(ruta).read_text(encoding="utf-8"))
    wf = p["wf"]
    print(f"── parche sobre {wf}: {p.get('descripcion', '')}")
    w = bajar(wf)
    idx = {n["name"]: n for n in w["nodes"]}

    # 1) validar TODO antes de escribir nada.
    #    Las ediciones se ENCADENAN: varias sobre el mismo campo se aplican una sobre el
    #    resultado de la anterior. Antes cada una se calculaba contra el texto original y
    #    después se escribían en secuencia, así que de N ediciones sobre un mismo campo
    #    sobrevivía sólo la última — en silencio, porque cada anchor validaba bien contra
    #    el original. No se notó hasta el 17/08 porque todos los parches previos tenían una
    #    sola edición.
    estado = {}
    for ed in p["ediciones"]:
        nom, campo = ed["nodo"], ed["campo"]
        if nom not in idx:
            sys.exit(f"❌ el nodo {nom!r} no existe en {wf} vivo. "
                     f"Nodos: {', '.join(sorted(idx))[:400]}")
        clave = (nom, campo)
        if clave in estado:
            actual = estado[clave]
        else:
            actual = get_campo(idx[nom], campo)
            if actual is None:
                sys.exit(f"❌ {nom}: el campo {campo!r} no existe")
            if not isinstance(actual, str):
                sys.exit(f"❌ {nom}.{campo} no es texto (es {type(actual).__name__})")
        n = actual.count(ed["anchor"])
        if n != 1:
            sys.exit(f"❌ {nom}.{campo}: el anchor aparece {n} veces, tiene que ser 1.\n"
                     f"   anchor: {ed['anchor'][:200]!r}")
        if ed["reemplazo"] == ed["anchor"]:
            sys.exit(f"❌ {nom}.{campo}: el reemplazo es idéntico al anchor")
        nuevo = actual.replace(ed["anchor"], ed["reemplazo"])
        estado[clave] = nuevo
        print(f"   ✓ anchor único en {nom}.{campo} ({len(actual)} → {len(nuevo)} chars)")

    if dry:
        print("   (dry-run: no escribo)")
        return

    # 2) escribir: una vez por campo, con el texto ya encadenado
    for (nom, campo), nuevo in estado.items():
        set_campo(idx[nom], campo, nuevo)
    subir(wf, w)

    # 3) releer del vivo y confirmar que quedó
    w2 = bajar(wf)
    idx2 = {n["name"]: n for n in w2["nodes"]}
    ok = True
    for (nom, campo), esperado in estado.items():
        real = get_campo(idx2[nom], campo)
        if real == esperado:
            print(f"   ✅ {nom}.{campo} confirmado en el vivo ({len(real)} chars)")
        else:
            ok = False
            print(f"   ❌ {nom}.{campo} NO coincide con lo enviado")
    if len(w2["nodes"]) != len(w["nodes"]):
        ok = False
        print(f"   ❌ cambió la cantidad de nodos: {len(w['nodes'])} → {len(w2['nodes'])}")
    print("   " + ("✅ parche aplicado y verificado" if ok else "❌ parche NO verificado"))
    if not ok:
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", nargs=2, metavar=("WF", "NODO"))
    ap.add_argument("--nodes", metavar="WF")
    ap.add_argument("--apply", metavar="PARCHE.json")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--restore", metavar="SNAPSHOT.json")
    a = ap.parse_args()

    if a.nodes:
        for n in bajar(a.nodes)["nodes"]:
            print(f"  {n['type'].split('.')[-1]:24} {n['name']}")
    elif a.show:
        wf, nom = a.show
        for n in bajar(wf)["nodes"]:
            if n["name"] == nom:
                print(json.dumps(n, ensure_ascii=False, indent=2))
                return
        sys.exit(f"❌ no encontré el nodo {nom!r} en {wf}")
    elif a.apply:
        aplicar(a.apply, a.dry_run)
    elif a.restore:
        p = pathlib.Path(a.restore)
        w = json.loads(p.read_text(encoding="utf-8"))
        wf = next((k for k, v in IDS.items() if v == w.get("id")), p.stem)
        subir(wf, w)
        print(f"✅ {wf} restaurado desde {p.name} ({len(w['nodes'])} nodos)")
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
