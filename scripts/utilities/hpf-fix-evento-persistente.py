#!/usr/bin/env python3
"""
HPF · fix del evento persistente en W6.

PROBLEMA (verificado en vivo el 2026-08-12)
Oscar reportó que en una conversación de XV el agente le mandaba la infografía y el
catálogo de cilindros de BODA, mientras que el catálogo de pantuflas sí venía de XV.

No es un archivo mal cargado (las 65 fichas tienen su media correcta y las de XV son de
XV) ni un filtro roto (W3 filtra bien: XV+cilindros devuelve las 3 fichas de XV). El
evento se le pregunta al LLM en CADA turno:

  Leer Products:  evento: String(o.evento || '').trim()   ← o = salida del agente Products

y el prompt de Products usa "Boda" en 12 de sus 13 ejemplos, así que el modelo derrapa a
Boda a mitad de conversación. Por eso unas fichas salen bien y otras mal en el mismo chat.

No hay ninguna capa de memoria del evento:
  - W1 no le pasa `evento` a W6 → `Normalizar entrada` recibe siempre null.
  - `Partir en burbujas` no devuelve `evento` → `Decidir seguimiento` persiste
    `cerebro.evento` que es undefined → `hpf_seguimientos.evento` queda NULL para siempre.

FIX
Autocontenido en W6, sin tocar W1 ni GHL:
  1. `Leer evento`   — Postgres EN LA CADENA PRINCIPAL:
     `Normalizar entrada → Leer evento → Router`. Crea `hpf_estado_sesion` si no existe
     y lee el evento de la sesión.
  2. `Guardar evento` — Postgres, rama paralela de `Leer Main Image` (el único lugar donde
     el evento se clasifica de verdad). Es una escritura y nadie lee su salida en el mismo
     turno, así que acá el orden no importa.
  3. `Leer Products`  — prefiere el evento del estado; el LLM queda como respaldo para el
     turno en que el estado todavía no existe.
  4. `Router.text`    — pasa de `$json.texto` a `$('Normalizar entrada').first().json.texto`,
     porque ahora tiene un nodo Postgres por delante y `$json` ya no es el contexto.

POR QUÉ EN LA CADENA PRINCIPAL Y NO EN UNA RAMA PARALELA
El primer intento lo puso como rama paralela de `Normalizar entrada` para no cambiarle el
input a nadie. Se aplicó bien y NO FUNCIONÓ: n8n con executionOrder v1 recorre la rama del
Router hasta el final antes de volver a la otra, así que cuando corre `Leer Products` el
nodo todavía no ejecutó y `isExecuted` da false. Medido sobre 6 ejecuciones reales:
`Leer evento` devolvía el valor correcto (Boda / XV) y `evento_desde_estado` era False en
todas. En la cadena principal el orden queda garantizado por la topología.

`Elegir ruta` reconstruye el contexto con `$('Normalizar entrada')`, así que Products y todo
lo que va después del Router no se ve afectado por el nodo nuevo.

Idempotente: si los nodos ya existen no los duplica, y migra la topología de rama paralela
a cadena principal si detecta la versión anterior.
"""
import importlib.util
import pathlib
import sys

# se carga a mano porque el nombre del archivo tiene guiones
_spec = importlib.util.spec_from_file_location(
    "hpfdeploy", pathlib.Path(__file__).parent / "hpf-deploy-workflow.py")
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)

CRED_PG = {"postgres": {"id": "uK59P60DJmOJc4Lm", "name": "H.F"}}

SQL_LEER = """CREATE TABLE IF NOT EXISTS hpf_estado_sesion (
  session_id     text PRIMARY KEY,
  evento         text,
  actualizado_at timestamptz NOT NULL DEFAULT now()
);
-- Sub-select en vez de WHERE: así devuelve SIEMPRE una fila (evento NULL si no hay
-- estado todavía) y `$('Leer evento').first()` nunca explota en el primer turno.
SELECT (SELECT evento FROM hpf_estado_sesion WHERE session_id = $1) AS evento;"""

SQL_GUARDAR = """CREATE TABLE IF NOT EXISTS hpf_estado_sesion (
  session_id     text PRIMARY KEY,
  evento         text,
  actualizado_at timestamptz NOT NULL DEFAULT now()
);
INSERT INTO hpf_estado_sesion (session_id, evento, actualizado_at)
VALUES ($1, $2, now())
ON CONFLICT (session_id) DO UPDATE
  SET evento = EXCLUDED.evento, actualizado_at = now()
RETURNING session_id, evento;"""

NODOS = [
    {
        "id": "b1e7a4d0-1111-4aaa-9001-0e1a2b3c4d01",
        "name": "Leer evento",
        "type": "n8n-nodes-base.postgres",
        "typeVersion": 2.4,
        "position": [-760, 100],
        "credentials": CRED_PG,
        "parameters": {
            "operation": "executeQuery",
            "query": SQL_LEER,
            "options": {"queryReplacement": "={{ [ $json.sessionId ] }}"},
        },
    },
    {
        "id": "b1e7a4d0-2222-4aaa-9002-0e1a2b3c4d02",
        "name": "Guardar evento",
        "type": "n8n-nodes-base.postgres",
        "typeVersion": 2.4,
        "position": [280, -200],
        "credentials": CRED_PG,
        "parameters": {
            "operation": "executeQuery",
            "query": SQL_GUARDAR,
            "options": {"queryReplacement": "={{ [ $json.sessionId, $json.evento ] }}"},
        },
    },
]

ANCHOR = """return [{ json: { ...ctx, step: $('Elegir ruta').first().json.step,
                  evento: String(o.evento || '').trim(),"""

REEMPLAZO = """// El evento ya NO se le pregunta al LLM si el estado lo tiene resuelto. Products lo
// re-derivaba de la memoria en cada turno y derrapaba a "Boda" (12 de sus 13 ejemplos
// usan Boda), así que una conversación de XV recibía fichas de Boda a mitad de camino
// mientras otras fichas del mismo turno venían bien. El LLM queda como respaldo sólo
// para el turno en que todavía no hay estado. isExecuted porque `Leer evento` corre en
// una rama paralela — mismo patrón que `Partir en burbujas` usa con `Cards a partes`.
const _le = $('Leer evento');
const _eventoEstado = _le.isExecuted
  ? String((_le.first().json || {}).evento || '').trim() : '';
const _eventoLLM = String(o.evento || '').trim();

return [{ json: { ...ctx, step: $('Elegir ruta').first().json.step,
                  evento: _eventoEstado || _eventoLLM,
                  evento_llm: _eventoLLM,
                  evento_desde_estado: !!_eventoEstado,"""


def main():
    dry = "--dry-run" in sys.argv
    w = D.bajar("W6")
    idx = {n["name"]: n for n in w["nodes"]}
    print(f"W6 vivo: {len(w['nodes'])} nodos")

    # ── 1. nodos nuevos (idempotente)
    for nd in NODOS:
        if nd["name"] in idx:
            print(f"   • {nd['name']}: ya existe, no lo duplico")
        else:
            w["nodes"].append(nd)
            print(f"   + nodo {nd['name']}")

    conn = w["connections"]

    # ── 2a. `Leer evento` INTERCALADO en la cadena principal, no en paralelo.
    #        Normalizar entrada → Leer evento → Router
    ne = conn.setdefault("Normalizar entrada", {}).setdefault("main", [[]])
    if not ne:
        ne.append([])
    if [t["node"] for t in ne[0]] == ["Leer evento"]:
        print("   • Normalizar entrada → Leer evento: ya intercalado")
    else:
        previos = [t["node"] for t in ne[0]]
        ne[0] = [{"node": "Leer evento", "type": "main", "index": 0}]
        print(f"   ~ Normalizar entrada: {previos} → ['Leer evento']")
    le = conn.setdefault("Leer evento", {}).setdefault("main", [[]])
    if not le:
        le.append([])
    if [t["node"] for t in le[0]] == ["Router"]:
        print("   • Leer evento → Router: ya conectado")
    else:
        le[0] = [{"node": "Router", "type": "main", "index": 0}]
        print("   + conexión Leer evento → Router")

    # ── 2b. `Guardar evento` sí va en paralelo: es una escritura y nadie lee su salida
    #        en el mismo turno, así que el orden es indistinto.
    lmi = conn.setdefault("Leer Main Image", {}).setdefault("main", [[]])
    if not lmi:
        lmi.append([])
    if "Guardar evento" in [t["node"] for t in lmi[0]]:
        print("   • Leer Main Image → Guardar evento: ya conectado")
    else:
        lmi[0].append({"node": "Guardar evento", "type": "main", "index": 0})
        print("   + conexión Leer Main Image → Guardar evento (rama paralela)")

    # ── 2c. Router deja de leer $json (ahora tiene un Postgres por delante)
    rt = {n["name"]: n for n in w["nodes"]}["Router"]["parameters"]
    VIEJO = "=Mensaje del usuario: {{ $json.texto }}"
    NUEVO = "=Mensaje del usuario: {{ $('Normalizar entrada').first().json.texto }}"
    if rt.get("text") == NUEVO:
        print("   • Router.text: ya repuntado")
    elif rt.get("text") == VIEJO:
        rt["text"] = NUEVO
        print("   ~ Router.text repuntado a $('Normalizar entrada')")
    else:
        sys.exit(f"❌ Router.text inesperado: {rt.get('text')!r}")

    # ── 3. parche de Leer Products
    lp = {n["name"]: n for n in w["nodes"]}["Leer Products"]
    js = lp["parameters"]["jsCode"]
    if "_eventoEstado" in js:
        print("   • Leer Products: ya parcheado")
    else:
        n = js.count(ANCHOR)
        if n != 1:
            sys.exit(f"❌ anchor de Leer Products aparece {n} veces (tiene que ser 1)")
        lp["parameters"]["jsCode"] = js.replace(ANCHOR, REEMPLAZO)
        print(f"   ~ Leer Products parcheado ({len(js)} → {len(lp['parameters']['jsCode'])} chars)")

    if dry:
        print("(dry-run: no escribo)")
        return

    D.subir("W6", w)

    # ── 4. releer del vivo y verificar
    v = D.bajar("W6")
    vidx = {n["name"]: n for n in v["nodes"]}
    ok = True
    for nd in NODOS:
        if nd["name"] not in vidx:
            ok = False
            print(f"   ❌ falta {nd['name']} en el vivo")
        else:
            q = vidx[nd["name"]]["parameters"]["query"]
            cred = vidx[nd["name"]].get("credentials", {}).get("postgres", {}).get("id")
            print(f"   ✅ {nd['name']}: {len(q)} chars de SQL, cred={cred}")
            if cred != CRED_PG["postgres"]["id"]:
                ok = False
                print("      ❌ credencial equivocada")
    esperado = {"Normalizar entrada": ["Leer evento"],
                "Leer evento": ["Router"]}
    for origen, dest_esp in esperado.items():
        dest = [t["node"] for t in v["connections"][origen]["main"][0]]
        if dest == dest_esp:
            print(f"   ✅ {origen} → {dest}")
        else:
            ok = False
            print(f"   ❌ {origen} → {dest}, esperaba {dest_esp}")
    dest = [t["node"] for t in v["connections"]["Leer Main Image"]["main"][0]]
    if "Guardar evento" in dest:
        print(f"   ✅ Leer Main Image → {dest}")
    else:
        ok = False
        print(f"   ❌ Leer Main Image no conecta a Guardar evento: {dest}")
    rt = vidx["Router"]["parameters"].get("text", "")
    if "$('Normalizar entrada')" in rt:
        print("   ✅ Router.text lee de Normalizar entrada")
    else:
        ok = False
        print(f"   ❌ Router.text sigue en {rt!r}")
    if "_eventoEstado" in vidx["Leer Products"]["parameters"]["jsCode"]:
        print("   ✅ Leer Products parcheado en el vivo")
    else:
        ok = False
        print("   ❌ Leer Products NO quedó parcheado")
    print(f"\nW6 vivo ahora: {len(v['nodes'])} nodos")
    print("✅ fix aplicado y verificado" if ok else "❌ fix NO verificado")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
