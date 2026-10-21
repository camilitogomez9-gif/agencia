#!/usr/bin/env python3
"""
HPF · W2 — un contacto que no está en `hpf_identity` hacía que NO se enviara nada, en silencio.

EL BUG (encontrado 2026-08-20 probando el blindaje de onError)
`¿Es Telegram?` es un `SELECT ... WHERE ghl_contact_id = $1 LIMIT 1` SIN `alwaysOutputData`.
Si el contacto no está en la tabla devuelve 0 filas, y en n8n un nodo sin items de entrada NO
se ejecuta: `Decidir transporte`, `Ruteo transporte` y los 5 nodos de envío quedan sin correr.
W2 termina **en verde**, con 5 nodos ejecutados y CERO mensajes enviados.

Evidencia: ejecución 1130111, `status=success`, `finished=True`, nodos que corrieron =
[Webhook, Normalizar partes, Recorrer partes, Preparar op, ¿Es Telegram?]. Tres burbujas
pedidas, ninguna enviada, ningún error.

Y el fallback que debía cubrirlo es INALCANZABLE. `Decidir transporte` dice literalmente:
    // Sin fila en hpf_identity o sin prefijo +999 → es un lead de verdad y sale por GHL.
...pero para eso tiene que ejecutarse, y con 0 filas no se ejecuta nunca. Es el mismo patrón
que el fallback muerto de `Cards a partes` en W6.

EL FIX
`alwaysOutputData: true` en `¿Es Telegram?`. Con 0 filas emite un item vacío, `Decidir
transporte` corre, `chat_id` queda null, `_por_telegram` false, y la burbuja sale por GHL —
exactamente lo que el comentario dice que tiene que pasar.

Uso:  hpf-fix-w2-identidad-vacia.py [--dry-run]
"""
import argparse
import json
import pathlib
import sys
import urllib.error
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[2]
W2_ID = "MdbOREN56lfQTYlM"
NODO = "¿Es Telegram?"
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
    if NODO not in idx:
        sys.exit(f"❌ no existe {NODO!r}. Nodos: {', '.join(sorted(idx))[:300]}")
    antes = idx[NODO].get("alwaysOutputData")
    n_antes = len(w["nodes"])
    print(f"   {NODO}: alwaysOutputData {antes!r} → True")
    if antes is True:
        print("   • ya estaba puesto, nada que hacer")
        return
    if a.dry_run:
        print("\n(dry-run: no escribo)")
        return

    idx[NODO]["alwaysOutputData"] = True
    s, r = api(f"/api/v1/workflows/{W2_ID}", "PUT",
               {k: w[k] for k in PUT_KEYS if k in w})
    if s != 200:
        sys.exit(f"❌ PUT falló: {s} {r}")

    s, w2 = api(f"/api/v1/workflows/{W2_ID}")
    idx2 = {n["name"]: n for n in w2["nodes"]}
    ok = idx2[NODO].get("alwaysOutputData") is True and len(w2["nodes"]) == n_antes
    print(f"   {'✅' if ok else '❌'} read-back: alwaysOutputData="
          f"{idx2[NODO].get('alwaysOutputData')!r} · {len(w2['nodes'])} nodos")
    if not ok:
        sys.exit(1)
    print("   ✅ aplicado y verificado")


if __name__ == "__main__":
    main()
