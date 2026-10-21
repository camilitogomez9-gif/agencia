#!/usr/bin/env python3
"""
HPF · R4b — cuando W3 no devuelve NINGUNA ficha, que conteste el Recolector.

EL BUG
En step_3 `Cards a partes` hace `partes.push(CTA_STEP_3)` de forma incondicional, así que:
  · el CTA "¿Le interesa sumarlos a la cotización?" sale aunque NO haya fichas que sumar —
    el lead ve una pregunta sobre unas fichas que nunca recibió;
  · y el fallback `if (partes.length === 0)` de la línea siguiente es INALCANZABLE por
    construcción, porque ese push garantiza length >= 1.
Pasa cuando el producto no existe para ese evento (vasos en Otros, mandiles en XV).

POR QUÉ EL FALLBACK NO ALCANZA
"Déjame revisar eso y te confirmo" no es paridad. El viejo responde con el dato del prompt
(E3: "Claro que sí! Tenemos Vasos Popote 24 oz… Cada vaso tiene un costo de $35"). Ese dato
está en el systemMessage del Recolector vivo (verificado: $35, mínimo 50, reglas de diseño y
un ejemplo de cotización completo). Así que la respuesta correcta es HACER QUE CONTESTE, no
inventar un texto de relleno.

ORDEN DE LAS DOS ESCRITURAS — importa
Se aplica en UN solo PUT, pero el orden lógico es: primero el OR de `¿Requiere cotizar?` y
después el `sin_fichas` de `Cards a partes`. Si se hiciera al revés y algo fallara en el
medio, quedaría una ventana donde el caso sin fichas no emite CTA **ni** invoca al
Recolector: silencio total para el lead.

Uso:  hpf-fix-r4b-sin-fichas.py [--dry-run]
"""
import argparse
import json
import pathlib
import sys
import urllib.error
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[2]
W6_ID = "cNmJCP2qVhdtfCH0"
PUT_KEYS = ("name", "nodes", "connections", "settings", "staticData")

A_CTA = """if (step === 'step_2' && dinamico) {
  partes.unshift({ texto: dinamico, adjuntos: [] });
} else if (step === 'step_3') {
  partes.push({ texto: CTA_STEP_3, adjuntos: [] });
}

if (partes.length === 0) {
  partes.push({ texto: 'Déjame revisar eso y te confirmo.', adjuntos: [] });
}"""
R_CTA = """// ¿W3 no trajo NINGUNA ficha para este evento x producto? Entonces no hay nada que "sumar
// a la cotización" y el CTA queda colgando: el lead recibe una pregunta sobre unas fichas
// que nunca vio. Pasa cuando el producto no existe para ese evento (vasos en Otros,
// mandiles en XV).
//
// En ese caso no se emite NADA acá: contesta el Recolector, que sí tiene el dato en el
// prompt (Vasos popote $35, mínimo 50, con ejemplo de cotización). Es lo que hace el viejo
// en E3. Para que eso ocurra, `¿Requiere cotizar?` tiene una condición OR sobre este mismo
// flag — los dos cambios van juntos y no tiene sentido uno sin el otro.
const sin_fichas = cards.length === 0;

if (step === 'step_2' && dinamico) {
  partes.unshift({ texto: dinamico, adjuntos: [] });
} else if (step === 'step_3' && !sin_fichas) {
  partes.push({ texto: CTA_STEP_3, adjuntos: [] });
}

// Este fallback era INALCANZABLE en step_3: el push del CTA garantizaba length >= 1 y la
// condición no se evaluaba nunca como verdadera. Ahora sí es alcanzable, pero se excluye el
// caso `sin_fichas` a propósito — ahí contesta el Recolector con el dato real, y un
// "déjame revisar eso" encima sería peor que no decir nada.
if (partes.length === 0 && !sin_fichas) {
  partes.push({ texto: 'Déjame revisar eso y te confirmo.', adjuntos: [] });
}"""

A_RET = """  step, partes, sin_media: r.sin_media || [], tools_usadas: ['CATALOGO'],"""
R_RET = """  step, partes, sin_media: r.sin_media || [], tools_usadas: ['CATALOGO'],
  // Lo lee `¿Requiere cotizar?` para forzar el paso por el Recolector.
  sin_fichas,"""


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
    req = urllib.request.Request(
        BASE + path, data=json.dumps(body).encode() if body is not None else None,
        method=method, headers={"X-N8N-API-KEY": KEY, "Accept": "application/json",
                                "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read().decode() or "null")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:500]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    s, w = api(f"/api/v1/workflows/{W6_ID}")
    if s != 200:
        sys.exit(f"❌ no pude bajar W6: {s} {w}")
    idx = {n["name"]: n for n in w["nodes"]}
    n_antes = len(w["nodes"])

    for nom in ("Cards a partes", "¿Requiere cotizar?"):
        if nom not in idx:
            sys.exit(f"❌ no existe {nom!r}")

    # ── 1) el OR de ¿Requiere cotizar?
    cond = idx["¿Requiere cotizar?"]["parameters"]["conditions"]
    if len(cond["conditions"]) != 1:
        sys.exit(f"❌ esperaba 1 condición, hay {len(cond['conditions'])} — revisar a mano")
    ya = any("sin_fichas" in json.dumps(c) for c in cond["conditions"])
    if ya:
        print("   • el OR ya estaba puesto")
    else:
        print(f"   ✓ ¿Requiere cotizar?: combinator {cond['combinator']!r} → 'or' + 2ª condición sin_fichas")

    # ── 2) el jsCode de Cards a partes
    code = idx["Cards a partes"]["parameters"]["jsCode"]
    for anc in (A_CTA, A_RET):
        n = code.count(anc)
        if n != 1:
            sys.exit(f"❌ anchor aparece {n} veces (tiene que ser 1):\n   {anc[:110]!r}")
    nuevo = code.replace(A_CTA, R_CTA).replace(A_RET, R_RET)
    print(f"   ✓ Cards a partes: {len(code)} → {len(nuevo)} chars")

    if a.dry_run:
        print("\n(dry-run: no escribo)")
        return

    if not ya:
        cond["combinator"] = "or"
        cond["conditions"].append({
            "id": "sin-fichas",
            "leftValue": "={{ $('Cards a partes').first().json.sin_fichas }}",
            "rightValue": "",
            "operator": {"type": "boolean", "operation": "true", "singleValue": True},
        })
    idx["Cards a partes"]["parameters"]["jsCode"] = nuevo

    s, r = api(f"/api/v1/workflows/{W6_ID}", "PUT", {k: w[k] for k in PUT_KEYS if k in w})
    if s != 200:
        sys.exit(f"❌ PUT falló: {s} {r}")

    s, w2 = api(f"/api/v1/workflows/{W6_ID}")
    idx2 = {n["name"]: n for n in w2["nodes"]}
    ok = True
    c2 = idx2["¿Requiere cotizar?"]["parameters"]["conditions"]
    if c2["combinator"] == "or" and any("sin_fichas" in json.dumps(x) for x in c2["conditions"]):
        print("   ✅ ¿Requiere cotizar? confirmado en el vivo (OR + sin_fichas)")
    else:
        ok = False; print("   ❌ ¿Requiere cotizar? no quedó")
    if idx2["Cards a partes"]["parameters"]["jsCode"] == nuevo:
        print("   ✅ Cards a partes confirmado en el vivo")
    else:
        ok = False; print("   ❌ Cards a partes no coincide")
    if len(w2["nodes"]) != n_antes:
        ok = False; print(f"   ❌ nodos {n_antes} → {len(w2['nodes'])}")
    else:
        print(f"   ✅ {n_antes} nodos, sin cambios")
    print("   " + ("✅ aplicado y verificado" if ok else "❌ NO verificado"))
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
