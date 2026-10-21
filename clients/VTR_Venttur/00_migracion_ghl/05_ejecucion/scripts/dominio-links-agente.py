#!/usr/bin/env python3
"""
Cambia el dominio de los links de agendamiento que manda el agente nuevo (main-venttur-ghl).

Para qué: el traspaso de WhatsApp (BSP) no depende del DNS de promo.venttur.com, pero el agente manda links a
promo, que sirve Clientify hasta que la agencia cambie el CNAME. Si el BSP va antes, el lead agendaría en
Clientify y GHL no lo vería (sin confirmación W6, rescate que escribe "no agendaste", agente que no ve la cita).
Mientras tanto el agente manda las mismas rutas en vtr.[TU-DOMINIO], que ya sirve las 50 landings de GHL
(y los redirects de las rutas con guion bajo). Cuando promo sirva GHL (B5), se vuelve a promo.

Toca sólo el host (las rutas no cambian) en 3 nodos del main y 2 del rescate:
  · Agente IA WPP             → prompt, sección "📲 Enlaces de asesoría"
  · Detectar promesa fantasma → links del redirect determinístico
  · Envió link?               → el IF que dispara W9 (link_enviado + rescate) cuando el output trae un link
  · Rescate: Code: Fase 1 / Fase 2 (GHL) → el link de cada mensaje de rescate (23/9: ya quedó en vtr con
    vtr_pre_bsp_fixes.py; en B5 `--a promo` lo vuelve junto con el main)

Uso:
  python3 dominio-links-agente.py --a vtr              # dry-run: cuenta qué cambiaría
  python3 dominio-links-agente.py --a vtr --execute    # antes del BSP, mientras promo siga en Clientify
  python3 dominio-links-agente.py --a promo --execute  # en B5, cuando promo.venttur.com ya sirve GHL
Antes de escribir guarda el workflow entero en snapshots/main-links-<fecha>-antes-de-<destino>.json.
"""
import json, sys, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path("/Users/camilo/Downloads/camilo-workspace")
SNAP = Path(__file__).resolve().parent.parent / "snapshots"
MAIN = "1eS1Z5k898c3ATnf"
NODOS = ("Agente IA WPP", "Detectar promesa fantasma", "Envió link?")
RESCATE = "YB0UxwEVwzISdd54"
NODOS_RESCATE = ("Code: Fase 1 (GHL)", "Code: Fase 2 (GHL)")
OBJETIVOS = ((MAIN, "main", NODOS), (RESCATE, "rescate", NODOS_RESCATE))
HOSTS = {"vtr": "vtr.[TU-DOMINIO]", "promo": "promo.venttur.com"}
SETTINGS_OK = ("executionOrder", "callerPolicy", "errorWorkflow", "saveDataErrorExecution",
               "saveDataSuccessExecution", "saveManualExecutions", "saveExecutionProgress", "timezone")


def env(key):
    for line in open(ROOT / ".env"):
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip()


BASE, KEY = env("N8N_BASE_URL").rstrip("/"), env("N8N_API_KEY")


def api(method, path, body=None):
    req = urllib.request.Request(BASE + path, method=method,
                                 headers={"X-N8N-API-KEY": KEY, "accept": "application/json",
                                          "content-type": "application/json"},
                                 data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:400]


def conteo(wf, nodos=NODOS):
    out = {}
    for n in wf["nodes"]:
        if n["name"] in nodos:
            s = json.dumps(n["parameters"], ensure_ascii=False)
            out[n["name"]] = {h: s.count(v) for h, v in HOSTS.items()}
    return out


def main():
    if "--a" not in sys.argv or sys.argv[sys.argv.index("--a") + 1] not in HOSTS:
        raise SystemExit("uso: dominio-links-agente.py --a vtr|promo [--execute]")
    dest = sys.argv[sys.argv.index("--a") + 1]
    orig = "promo" if dest == "vtr" else "vtr"
    execute = "--execute" in sys.argv
    for wid, alias, nodos in OBJETIVOS:
        cambiar(wid, alias, nodos, orig, dest, execute)


def cambiar(wid, alias, nodos, orig, dest, execute):
    code, wf = api("GET", f"/api/v1/workflows/{wid}")
    if code != 200:
        raise SystemExit(f"❌ GET {alias}: {code} {wf}")
    antes = conteo(wf, nodos)
    faltan = [n for n in nodos if n not in antes]
    if faltan:
        raise SystemExit(f"❌ no encuentro los nodos {faltan} en {alias}: no toco nada")
    total = sum(c[orig] for c in antes.values())
    print(f"\n{alias} {wid} · activo={wf.get('active')} · {HOSTS[orig]} → {HOSTS[dest]}")
    for n, c in antes.items():
        print(f"  {n:28s} {HOSTS[orig]}: {c[orig]:2d}   {HOSTS[dest]}: {c[dest]:2d}")
    if total == 0:
        print(f"  Ya está en {HOSTS[dest]}. Nada que hacer.")
        return
    if not execute:
        print(f"  [DRY-RUN] Cambiaría {total} links. Agregá --execute para aplicarlo.")
        return

    SNAP.mkdir(exist_ok=True)
    snap = SNAP / f"{alias}-links-{time.strftime('%Y-%m-%d-%H%M')}-antes-de-{dest}.json"
    snap.write_text(json.dumps(wf, ensure_ascii=False, indent=1))

    for n in wf["nodes"]:
        if n["name"] in nodos:
            n["parameters"] = json.loads(json.dumps(n["parameters"], ensure_ascii=False)
                                         .replace(HOSTS[orig], HOSTS[dest]))
    body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
            "settings": {k: v for k, v in (wf.get("settings") or {}).items() if k in SETTINGS_OK}}
    code, resp = api("PUT", f"/api/v1/workflows/{wid}", body)
    if code != 200:
        raise SystemExit(f"❌ PUT {alias}: {code} {resp}\n   Snapshot intacto en {snap}")

    code, wf2 = api("GET", f"/api/v1/workflows/{wid}")
    despues = conteo(wf2, nodos)
    quedan = sum(c[orig] for c in despues.values())
    print(f"  {'✅' if quedan == 0 else '❌'} {total} links pasados a {HOSTS[dest]} · quedan {quedan} en {HOSTS[orig]}"
          f" · activo={wf2.get('active')} (sin cambios)\n   Rollback: {snap.name}")


if __name__ == "__main__":
    main()
