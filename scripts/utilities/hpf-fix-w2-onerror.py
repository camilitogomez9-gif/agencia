#!/usr/bin/env python3
"""
HPF · W2 — que un adjunto malo no se lleve puesto el turno entero.

EL BUG
Los 5 nodos de envío de W2 tienen `onError: null` (= stopWorkflow). Cuando uno falla, muere
W2 completo y el loop `Recorrer partes` no sigue: se pierden TODAS las burbujas posteriores.
Es lo que pasaba con la ficha de mandiles (PNG de 6,12 MB, sobre el techo de 5 MB de Telegram):
llegaba la burbuja #1 y el turno se cortaba en la #2, en 6 de 6 corridas del test de paridad.

SON 5 NODOS, NO 4
El plan listaba sólo los 4 de Telegram. Medido sobre el vivo: `W0 · enviar` —el carril de
PRODUCCIÓN, el que manda a GHL— tiene exactamente la misma fragilidad. Los 5 convergen en
`Arrastrar contexto`, que reconstruye desde `$('Preparar op')` y no depende del output del nodo
caído, así que el loop puede continuar.

LO QUE NO SE TOCA
`W2 · enviar` (dentro de W1) queda como está. Ahí `onError` NO es una decisión técnica: haría
que el turno avance de etapa y marque actividad aunque el mensaje no haya salido, dejando al
lead marcado como atendido sin serlo y sacándolo del barrido de seguimientos. Puede ser peor
que el bug. Va aparte, con decisión de negocio.

CONTRAPARTIDA ACEPTADA
Esto convierte un fallo ruidoso en uno silencioso. Por eso `Armar resumen` pasa a contar las
burbujas que fallaron, para que quede en la ejecución y no haya que adivinarlo.

Uso:  hpf-fix-w2-onerror.py [--dry-run]
"""
import argparse
import json
import pathlib
import sys
import urllib.error
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[2]
W2_ID = "MdbOREN56lfQTYlM"
NODOS = ["TG · texto", "TG · foto", "TG · video", "TG · documento", "W0 · enviar"]
PUT_KEYS = ("name", "nodes", "connections", "settings", "staticData")

ANCHOR_RESUMEN = """  enviados.push({
    seq: j.seq ?? null,"""
NUEVO_RESUMEN = """  // Un envío que falló llega acá por `onError: continueRegularOutput` con `j.error`
  // poblado. Sin contarlo, el fallo pasa a ser SILENCIOSO: el lead recibe el turno
  // incompleto y la ejecución queda en verde. Es la contrapartida de haber blindado los
  // nodos de envío, y queda visible en el resumen en vez de haber que adivinarla.
  if (j.error) {
    enviados.push({ seq: j.seq ?? null, body: j.texto ?? null,
                    attachments: j.adjuntos ?? [], fallo: String(
                      (j.error && (j.error.message || j.error.description)) || j.error
                    ).slice(0, 200) });
    continue;
  }
  enviados.push({
    seq: j.seq ?? null,"""

ANCHOR_RETURN = """return [{ json: {
  ok: enviados.every(e => e.ghl_message_id),
  partes_enviadas: enviados.length,
  enviados,
} }];"""
NUEVO_RETURN = """const fallidas = enviados.filter(e => e.fallo);
return [{ json: {
  // `ok` sigue significando lo mismo para el carril GHL. Se le suma que NINGUNA burbuja
  // haya fallado: con los nodos blindados, "no hubo excepción" ya no implica "salió todo".
  ok: enviados.every(e => e.ghl_message_id) && fallidas.length === 0,
  partes_enviadas: enviados.length,
  partes_fallidas: fallidas.length,
  fallos: fallidas.map(e => ({ seq: e.seq, fallo: e.fallo })),
  enviados,
} }];"""


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

    s, w = api(f"/api/v1/workflows/{W2_ID}")
    if s != 200:
        sys.exit(f"❌ no pude bajar W2: {s} {w}")
    idx = {n["name"]: n for n in w["nodes"]}
    n_antes = len(w["nodes"])

    # 1) validar TODO antes de escribir
    faltan = [n for n in NODOS if n not in idx]
    if faltan:
        sys.exit(f"❌ no existen en el vivo: {faltan}")
    ya = [n for n in NODOS if idx[n].get("onError") == "continueRegularOutput"]
    if ya:
        print(f"   • ya blindados (no se tocan): {ya}")

    resumen = idx.get("Armar resumen")
    if not resumen:
        sys.exit("❌ no existe 'Armar resumen'")
    code = resumen["parameters"]["jsCode"]
    for anc in (ANCHOR_RESUMEN, ANCHOR_RETURN):
        n = code.count(anc)
        if n != 1:
            sys.exit(f"❌ anchor de 'Armar resumen' aparece {n} veces, tiene que ser 1:\n"
                     f"   {anc[:90]!r}")
    nuevo_code = code.replace(ANCHOR_RESUMEN, NUEVO_RESUMEN).replace(
        ANCHOR_RETURN, NUEVO_RETURN)
    print(f"   ✓ 'Armar resumen': {len(code)} → {len(nuevo_code)} chars")

    for n in NODOS:
        print(f"   ✓ {n}: onError {idx[n].get('onError')!r} → 'continueRegularOutput'")

    if a.dry_run:
        print("\n(dry-run: no escribo)")
        return

    # 2) escribir
    for n in NODOS:
        idx[n]["onError"] = "continueRegularOutput"
        idx[n]["alwaysOutputData"] = True
    resumen["parameters"]["jsCode"] = nuevo_code

    body = {k: w[k] for k in PUT_KEYS if k in w}
    s, r = api(f"/api/v1/workflows/{W2_ID}", "PUT", body)
    if s != 200:
        sys.exit(f"❌ PUT falló: {s} {r}")

    # 3) releer del vivo
    s, w2 = api(f"/api/v1/workflows/{W2_ID}")
    idx2 = {n["name"]: n for n in w2["nodes"]}
    ok = True
    for n in NODOS:
        real = idx2[n].get("onError")
        if real == "continueRegularOutput":
            print(f"   ✅ {n} confirmado en el vivo")
        else:
            ok = False
            print(f"   ❌ {n} quedó en {real!r}")
    if idx2["Armar resumen"]["parameters"]["jsCode"] != nuevo_code:
        ok = False
        print("   ❌ 'Armar resumen' no coincide con lo enviado")
    else:
        print("   ✅ 'Armar resumen' confirmado en el vivo")
    if len(w2["nodes"]) != n_antes:
        ok = False
        print(f"   ❌ cambió la cantidad de nodos: {n_antes} → {len(w2['nodes'])}")
    else:
        print(f"   ✅ {n_antes} nodos, sin cambios")
    print("   " + ("✅ aplicado y verificado" if ok else "❌ NO verificado"))
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
