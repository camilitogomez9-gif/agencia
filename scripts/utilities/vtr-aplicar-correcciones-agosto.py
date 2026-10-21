#!/usr/bin/env python3
"""
vtr-aplicar-correcciones-agosto.py — Aplica en el n8n vivo las correcciones del
"Reporte la agencia 1 — Agente WhatsApp Venttur — Agosto 2026".

Cada patch es independiente, tiene un ancla verificada y aborta si el ancla no aparece
(nunca escribe a ciegas). Por defecto corre en DRY-RUN: muestra qué cambiaría sin tocar nada.

    python3 scripts/utilities/vtr-aplicar-correcciones-agosto.py --list
    python3 scripts/utilities/vtr-aplicar-correcciones-agosto.py            # dry-run de todos
    python3 scripts/utilities/vtr-aplicar-correcciones-agosto.py --apply P1 P4
    python3 scripts/utilities/vtr-aplicar-correcciones-agosto.py --apply all

Rollback: clients/VTR_Venttur/03_workflows/vivo-2026-08-17/ (los 14 workflows con sha256,
exportados por API antes de tocar nada).

Requiere N8N_BASE_URL y N8N_API_KEY en el .env de la raíz del workspace.

YA APLICADO A MANO (no está acá): las 4 referencias rotas de `Confirmación de agenda`
(`2PSekVBxarsrnVBu`), que dejaban sin confirmación a los leads de Andrés y Diego.
"""
import argparse
import copy
import json
import os
import re
import sys
import urllib.error
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MAIN = "k3aivKSP67S97IHn"          # [Venttur] — agente principal
OUTREACH = "CUuFxbst3iHpgeXS"      # VTR - Outreach Form Meta
DISPATCHER = "DyrDumQgb6S4zHsS"    # Resumen, etiquetas, seguimientos


# ─── API ──────────────────────────────────────────────────────────────────────

def _env():
    env = {}
    with open(os.path.join(RAIZ, ".env")) as f:
        for line in f:
            m = re.match(r"^([A-Z0-9_]+)=(.*)$", line.strip())
            if m:
                env[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    if "N8N_BASE_URL" not in env or "N8N_API_KEY" not in env:
        sys.exit("ERROR: faltan N8N_BASE_URL o N8N_API_KEY en el .env")
    return env


ENV = _env()
BASE = ENV["N8N_BASE_URL"].rstrip("/")


def _req(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(
        f"{BASE}/api/v1{path}", data=data, method=method,
        headers={"X-N8N-API-KEY": ENV["N8N_API_KEY"],
                 "Content-Type": "application/json", "Accept": "application/json"})
    try:
        return json.load(urllib.request.urlopen(r, timeout=60))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode()[:600]}")


def get_wf(wid):
    return _req("GET", f"/workflows/{wid}")


def put_wf(wf):
    payload = {k: wf[k] for k in ("name", "nodes", "connections", "settings") if k in wf}
    return _req("PUT", f"/workflows/{wf['id']}", payload)


def nodo(wf, name):
    for n in wf["nodes"]:
        if n["name"] == name:
            return n
    raise KeyError(f"nodo inexistente: {name!r}")


# ─── Patches ──────────────────────────────────────────────────────────────────
# Cada función recibe el workflow y devuelve la lista de cambios (vacía = no hizo nada).

def p1_tope_toques(wf):
    """Ola 1.1 — el tri-toque del outreach baja a 2. Cierra parte de H3."""
    cambios = []
    n = nodo(wf, "Get Leads Pendientes")
    f = n["parameters"]["filterByFormula"]
    if "{Toques enviados} < 3" not in f:
        print("   ancla no encontrada en filterByFormula"); return []
    nuevo = f.replace("{Toques enviados} < 3", "{Toques enviados} < 2", 1)
    clausula = (", AND({Toques enviados} = 2, IS_AFTER(NOW(), "
                "DATEADD({Touch 1 programado at}, 72, 'hours')))")
    if clausula in nuevo:
        nuevo = nuevo.replace(clausula, "", 1)
        cambios.append("Get Leads Pendientes: eliminada la cadencia de 72 h (Touch 3)")
    n["parameters"]["filterByFormula"] = nuevo
    cambios.append("Get Leads Pendientes: {Toques enviados} < 3  ->  < 2")

    # desconectar la rama Touch 3 del Switch (los nodos quedan huérfanos, no se borran:
    # reconectar la salida[2] es el rollback)
    br = wf["connections"].get("Switch", {}).get("main", [])
    if len(br) > 2 and br[2]:
        destino = [x["node"] for x in br[2]]
        br[2] = []
        cambios.append(f"Switch salida[2] desconectada (iba a {destino})")
    return cambios


def p2_whitelist(wf):
    """Ola 2.1 — el gate del drip omitía agendar-ema. Es el 64% de H2."""
    n = nodo(wf, "OpenAI")
    s = json.dumps(n["parameters"], ensure_ascii=False)
    m = re.search(r"(Ten cuidado, los [^:]*links para agendar [^:]*: )([^.]*\.)", s)
    if not m:
        print("   ancla no encontrada en el prompt de la Tarea 4"); return []
    lista = ("'promo.venttur.com/agendar-ema', 'promo.venttur.com/AAFamilia-Agendar', "
             "'promo.venttur.com/SummerCamp-Agendar', 'promo.venttur.com/PW_Alemania_Agendar', "
             "'promo.venttur.com/EstudiaryTrabajar_Agendar' o "
             "'promo.venttur.com/Estudiar-y-Trabajar-en-Australia'.")
    s = s[:m.start(2)] + lista + s[m.end(2):]
    n["parameters"] = json.loads(s)
    return ["OpenAI/Tarea 4: whitelist corregida (+agendar-ema, -SPEagendar inexistente, -2 duplicados)"]


def p3_gate_por_campo(wf):
    """Ola 2.2 — el drip deja de preguntarle al LLM y lee el campo real de Airtable."""
    cambios = []
    for name in ("No envio link?", "No envio link? x2"):
        n = nodo(wf, name)
        c = n["parameters"]["conditions"]["conditions"][0]
        if "message.content.asesoria" not in str(c.get("leftValue", "")):
            print(f"   {name}: ancla no encontrada"); continue
        c["leftValue"] = "={{ $('Obtener ID Clientify').item.json['Link asesoría enviado'] ?? false }}"
        c["rightValue"] = ""
        c["operator"] = {"type": "boolean", "operation": "false", "singleValue": True}
        n["parameters"]["conditions"]["options"]["typeValidation"] = "loose"
        cambios.append(f"{name}: gate por 'Link asesoría enviado' de Airtable en vez de la inferencia del LLM")
    return cambios


def p4_audios(wf):
    """Ola 2.6 — `Hay audios?` exigía que una URL de S3 fuera igual al string 'webp'.

    Condición imposible con combinador AND: la rama de transcripción nunca corrió y una
    nota de voz pura llegaba al agente como string vacío.
    """
    n = nodo(wf, "Hay audios?")
    for c in n["parameters"]["conditions"]["conditions"]:
        if c.get("rightValue") == "webp" and c["operator"].get("operation") == "equals":
            c["operator"] = {"type": "string", "operation": "notContains"}
            return ["Hay audios?: condición 3  equals 'webp'  ->  notContains 'webp'"]
    print("   ancla no encontrada (¿ya estaba corregido?)")
    return []


def p5_dedupe(wf):
    """Ola 2.5 — el dedupe descartaba mensajes en silencio (H4, caso Omar Montes).

    Escribía `headers.mensaje` (latin1 mojibake) y comparaba contra `respuesta_definitiva`
    (UTF-8), así que sólo disparaba con texto ASCII puro. Y su salida TRUE era rama muerta.
    """
    cambios = []
    n = nodo(wf, "Actualizar ultimo mensaje")
    col = n["parameters"]["columns"]["value"]
    if "headers.mensaje" in str(col.get("Ultimo mensaje", "")):
        col["Ultimo mensaje"] = "={{ $('Webhook').item.json.body.custom_fields.respuesta_definitiva }}"
        cambios.append("Actualizar ultimo mensaje: escribe respuesta_definitiva (UTF-8), no headers.mensaje (mojibake)")

    br = wf["connections"].get("Repetido?", {}).get("main", [])
    while len(br) < 2:
        br.append([])
    if not br[0]:
        br[0] = [{"node": "Actualizar ultimo mensaje", "type": "main", "index": 0}]
        cambios.append("Repetido? salida TRUE cableada (antes moría ahí: el mensaje se perdía sin respuesta)")
    wf.setdefault("connections", {}).setdefault("Repetido?", {})["main"] = br
    return cambios


PATCHES = [
    ("P1", OUTREACH,    "Ola 1.1 · tri-toque a 2 toques + desconectar Touch 3", p1_tope_toques),
    ("P2", DISPATCHER,  "Ola 2.1 · whitelist de links (+agendar-ema)",          p2_whitelist),
    ("P3", DISPATCHER,  "Ola 2.2 · gate del drip por campo real de Airtable",   p3_gate_por_campo),
    ("P4", MAIN,        "Ola 2.6 · Hay audios? condición imposible",            p4_audios),
    ("P5", MAIN,        "Ola 2.5 · dedupe que descartaba mensajes (H4)",        p5_dedupe),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", nargs="*", metavar="ID", help="IDs a aplicar, o 'all'. Sin esto: dry-run.")
    ap.add_argument("--list", action="store_true", help="lista los patches y sale")
    args = ap.parse_args()

    if args.list:
        for pid, wid, desc, _ in PATCHES:
            print(f"  {pid}  {wid}  {desc}")
        return

    sel = None
    if args.apply is not None:
        sel = None if (not args.apply or "all" in args.apply) else set(args.apply)
    aplicar = args.apply is not None

    print("MODO:", "APLICAR (escribe en producción)" if aplicar else "DRY-RUN (no escribe nada)")
    print()

    for pid, wid, desc, fn in PATCHES:
        if sel is not None and pid not in sel:
            continue
        print(f"[{pid}] {desc}")
        antes = get_wf(wid)
        wf = copy.deepcopy(antes)
        try:
            cambios = fn(wf)
        except KeyError as e:
            print(f"   ABORTADO: {e}\n")
            continue
        if not cambios:
            print("   sin cambios\n")
            continue
        for c in cambios:
            print(f"   · {c}")
        if not aplicar:
            print("   (dry-run: no se escribió)\n")
            continue
        put_wf(wf)
        despues = get_wf(wid)
        na = {n["name"] for n in antes["nodes"]}
        nd = {n["name"] for n in despues["nodes"]}
        if na != nd:
            print(f"   !! cambió el set de nodos: +{nd - na} -{na - nd}")
        print(f"   APLICADO · nodos {len(antes['nodes'])} -> {len(despues['nodes'])}\n")


if __name__ == "__main__":
    main()
