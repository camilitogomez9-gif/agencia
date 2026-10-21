#!/usr/bin/env python3
"""
HPF · 3.2 — restituir la "sugerencia anterior" que Products perdió en la migración.

EL BUG
El systemMessage de `Products` tiene, textual:

    # Sugerencia anterior de Rebeca
    - Si la sugerencia anterior: {{ $json.message.content }} contiene productos que se le
      ofrecen al usuario y este te consulta el precio, info o cuanto cuestan...

Pero a `Products` lo alimenta UN solo nodo, `Switch de step [2]`, cuyo item viene de
`Elegir ruta` → `{...ctx, step}`. Ese objeto NO tiene la clave `message`, así que la
expresión resuelve vacío y **el bloque entero está muerto**: el agente nunca sabe qué le
ofreció al lead en el turno anterior.

NO ES HEREDADO — ES REGRESIÓN DE LA MIGRACIÓN
El origen tenía un nodo Postgres dedicado justo antes:

    Switch1 [2] → GET_LAST_INTERACTION → AI Agent Products

    SELECT message FROM n8n_chat_histories
    WHERE session_id = '...' AND message->>'type' = 'ai'
      AND message->>'content' NOT LIKE '%step_%'
    ORDER BY id DESC LIMIT 1;

O sea que allá `$json.message.content` SÍ resolvía: era el último mensaje del agente. La
migración se llevó el nodo y dejó la referencia colgando.

Es el candidato a explicar R8 (el cross-sell que cayó de 7 apariciones a 2) y el
«¿cuánto cuestan?» referido a lo último ofrecido, que el CLAUDE.md registra como
intermitente ~3/5 y "quedó así por diseño".

DOS CAMBIOS, UN SOLO PUT — y el segundo NO es opcional
Al meter un nodo entre `Switch de step` y `Products`, `$json` dentro de Products deja de ser
el ctx y pasa a ser la fila de Postgres. `Products.parameters.text` usa `{{ $json.texto }}` y
`{{ $json.fecha }}`, así que se romperían — es exactamente el bug de R2. Por eso se convierten
a referencia absoluta en la misma escritura.

DEGRADACIÓN SEGURA
El nodo va con `alwaysOutputData: true` (sin eso, 0 filas mata la rama: es el bug que apareció
en `¿Es Telegram?` de W2) y `onError: continueRegularOutput` (un problema de base no puede
tumbar el turno). En los dos casos `message.content` queda vacío y el comportamiento es el de
hoy, ni mejor ni peor.

Uso:  hpf-fix-sugerencia-anterior.py [--dry-run]
"""
import argparse
import json
import pathlib
import sys
import urllib.error
import urllib.request
import uuid

REPO = pathlib.Path(__file__).resolve().parents[2]
W6_ID = "cNmJCP2qVhdtfCH0"
NUEVO = "Leer sugerencia anterior"
PUT_KEYS = ("name", "nodes", "connections", "settings", "staticData")

QUERY = """-- El ultimo mensaje del AGENTE en esta sesion. Lo lee el systemMessage de `Products`
-- para resolver "la sugerencia anterior": si Rebeca ofrecio anticrudas y el lead contesta
-- "cuanto cuestan?", Products tiene que saber a que se referia.
--
-- Replica GET_LAST_INTERACTION del origen (main-happy-flops.json), que la migracion
-- perdio. El filtro NOT LIKE '%step_%' tambien es del origen: descarta los mensajes de
-- ruteo, que no son sugerencias de producto.
SELECT message
FROM n8n_chat_histories
WHERE session_id = $1
  AND message->>'type' = 'ai'
  AND message->>'content' NOT LIKE '%step_%'
ORDER BY id DESC
LIMIT 1;"""

TEXT_VIEJO = "=Respuesta del usuario: {{ $json.texto }}\n\nFecha de hoy: {{ $json.fecha }}"
TEXT_NUEVO = ("=Respuesta del usuario: {{ $('Normalizar entrada').first().json.texto }}\n\n"
              "Fecha de hoy: {{ $('Normalizar entrada').first().json.fecha }}")


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

    if NUEVO in idx:
        print(f"   • {NUEVO!r} ya existe — nada que hacer")
        return
    for req in ("Products", "Switch de step", "Leer evento"):
        if req not in idx:
            sys.exit(f"❌ falta {req!r}")

    # validar la conexión que se va a reescribir
    sal = w["connections"]["Switch de step"]["main"]
    if len(sal) < 3 or [x["node"] for x in (sal[2] or [])] != ["Products"]:
        sys.exit(f"❌ esperaba 'Switch de step'[2] -> ['Products'], hay "
                 f"{[x['node'] for x in (sal[2] or [])] if len(sal) > 2 else 'nada'}")
    print("   ✓ Switch de step [2] -> Products (confirmado)")

    txt = idx["Products"]["parameters"].get("text")
    if txt != TEXT_VIEJO:
        sys.exit(f"❌ Products.parameters.text no es el esperado:\n   {txt!r}")
    print(f"   ✓ Products.parameters.text → referencia absoluta ({len(TEXT_VIEJO)} → {len(TEXT_NUEVO)})")

    cred = idx["Leer evento"].get("credentials")
    print(f"   ✓ credencial Postgres clonada de 'Leer evento': {list((cred or {}).values())[0]['name']!r}")
    print(f"   ✓ nodo nuevo {NUEVO!r} entre Switch de step [2] y Products")

    if a.dry_run:
        print("\n(dry-run: no escribo)")
        return

    nodo = {
        "parameters": {"operation": "executeQuery", "query": QUERY,
                       "options": {"queryReplacement":
                                   "={{ [ $('Normalizar entrada').first().json.sessionId ] }}"}},
        "type": "n8n-nodes-base.postgres", "typeVersion": 2.4,
        "position": [296, 560], "id": str(uuid.uuid4()), "name": NUEVO,
        "alwaysOutputData": True, "onError": "continueRegularOutput",
        "credentials": cred,
    }
    w["nodes"].append(nodo)
    idx["Products"]["parameters"]["text"] = TEXT_NUEVO
    w["connections"]["Switch de step"]["main"][2] = [
        {"node": NUEVO, "type": "main", "index": 0}]
    w["connections"][NUEVO] = {"main": [[{"node": "Products", "type": "main", "index": 0}]]}

    s, r = api(f"/api/v1/workflows/{W6_ID}", "PUT", {k: w[k] for k in PUT_KEYS if k in w})
    if s != 200:
        sys.exit(f"❌ PUT falló: {s} {r}")

    s, w2 = api(f"/api/v1/workflows/{W6_ID}")
    idx2 = {n["name"]: n for n in w2["nodes"]}
    c2 = w2["connections"]
    ok = True
    for cond, msg in [
        (NUEVO in idx2, f"nodo {NUEVO!r} presente"),
        (idx2.get(NUEVO, {}).get("alwaysOutputData") is True, "alwaysOutputData=True"),
        (idx2["Products"]["parameters"]["text"] == TEXT_NUEVO, "Products.text absoluto"),
        ([x["node"] for x in (c2["Switch de step"]["main"][2] or [])] == [NUEVO],
         f"Switch de step [2] -> {NUEVO}"),
        ([x["node"] for x in (c2.get(NUEVO, {}).get("main", [[]])[0] or [])] == ["Products"],
         f"{NUEVO} -> Products"),
        (len(w2["nodes"]) == n_antes + 1, f"nodos {n_antes} → {n_antes + 1}"),
    ]:
        print(f"   {'✅' if cond else '❌'} {msg}")
        ok = ok and cond
    print("   " + ("✅ aplicado y verificado" if ok else "❌ NO verificado"))
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
