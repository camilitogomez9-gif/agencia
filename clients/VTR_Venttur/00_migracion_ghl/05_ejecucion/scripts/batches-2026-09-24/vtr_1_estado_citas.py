#!/usr/bin/env python3
"""Paso 1 (24/9) · El [ESTADO DEL LEAD] usa las citas REALES del contacto en GHL.   Marca: CITAS-0924

Diagnóstico (caso Mauricio, 23/9 18:28 CDMX): el contacto `uFx22fuKbExjkkUssx37` venía de la importación con
`agendan_cita = true` y `estado = Cita confirmada` (pruebas viejas en Clientify) y CERO citas en GHL. El builder
del estado ponía `Cita: AGENDADA (no le vuelvas a mandar el link)` → el bot se negó 4 turnos a mandar el link,
inventó un "correo de confirmación" y dijo no tener acceso a la fecha.

Qué hace en el main `1eS1Z5k898c3ATnf`:
  · Nodo nuevo `GHL · Citas (estado)` (GET /contacts/{id}/appointments) entre `GHL · Get contact (estado)` y
    `Construir estado lead`. executeOnce + alwaysOutputData + continueRegularOutput: si GHL falla, el builder
    cae al comportamiento por flag (sin romper la respuesta).
  · `Construir estado lead` reescrito (fuente: estado_lead_citas.js): cita futura con fecha · cita pasada ·
    flag sin cita registrada · sin cita. Saca el "(no le vuelvas a mandar el link)" y devuelve la frase
    "YA ENVIADO y NO agendó todavía" que el prompt usa como disparador.

Uso:
  python3 vtr_1_estado_citas.py                 dry-run (arma el parche y valida anclas)
  python3 vtr_1_estado_citas.py --verificar     corre el builder NUEVO dentro de n8n en un workflow temporal
                                                (sólo lecturas a GHL) para Mauricio, Daiana, Viri y la agencia; lo borra
  python3 vtr_1_estado_citas.py --execute       aplica al main (guarda pre/post con sha256)
Rollback: PUT del JSON en ghl-live-2026-09-24-agente-link/pre/main-paso1.json
"""
import copy, json, sys, time, uuid, urllib.request, importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "p", Path(__file__).parents[1] / "batches-2026-09-23" / "vtr_pre_bsp_fixes.py")
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)

MARK = "CITAS-0924"
MAIN = "1eS1Z5k898c3ATnf"
OUT = p.ROOT / "clients/VTR_Venttur/03_workflows/ghl-live-2026-09-24-agente-link"
BUILDER = (Path(__file__).with_name("estado_lead_citas.js")).read_text()
N_CITAS = "GHL · Citas (estado)"
N_GET = "GHL · Get contact (estado)"
N_EST = "Construir estado lead"
URL = "=https://services.leadconnectorhq.com/contacts/{{ $('Normalize GHL Payload').first().json.contact_id }}/appointments"
FLAGS = {"executeOnce": True, "alwaysOutputData": True, "onError": "continueRegularOutput"}


def patch_main(wf):
    if p.has(wf, N_CITAS):
        raise RuntimeError("el nodo de citas ya existe")
    get, est = p.node(wf, N_GET), p.node(wf, N_EST)
    # sanity: la cadena actual es Get contact → Construir estado lead
    cur = [t["node"] for outs in wf["connections"].get(N_GET, {}).get("main", []) for t in outs]
    if cur != [N_EST]:
        raise RuntimeError(f"cadena inesperada desde {N_GET}: {cur}")
    citas = p.http_node(N_CITAS, [get["position"][0] + 112, get["position"][1] + 160], "GET", URL, flags=FLAGS)
    citas["notes"] = MARK + ": citas reales del contacto para el [ESTADO DEL LEAD]"
    wf["nodes"].append(citas)
    p.set_targets(wf, N_GET, 0, [N_CITAS])
    p.set_targets(wf, N_CITAS, 0, [N_EST])
    est["parameters"]["jsCode"] = BUILDER


def verificar():
    """Workflow temporal: Webhook → Get contact → Citas → builder nuevo → responde. Sólo GETs a GHL."""
    path = "vtr-citas-verif-" + uuid.uuid4().hex[:8]
    cid = "={{ $('Webhook').first().json.query.cid }}"
    get = p.http_node(N_GET, [220, 0], "GET", "=https://services.leadconnectorhq.com/contacts/{{ $('Webhook').first().json.query.cid }}",
                      flags={"alwaysOutputData": True, "onError": "continueRegularOutput"})
    cit = p.http_node(N_CITAS, [440, 0], "GET", "=https://services.leadconnectorhq.com/contacts/{{ $('Webhook').first().json.query.cid }}/appointments",
                      flags=FLAGS)
    est = p.code_node(N_EST, [660, 0], BUILDER)
    hook = {"parameters": {"path": path, "responseMode": "lastNode", "options": {}}, "name": "Webhook",
            "type": "n8n-nodes-base.webhook", "typeVersion": 2, "position": [0, 0], "id": str(uuid.uuid4()),
            "webhookId": str(uuid.uuid4())}
    wf = {"name": "TEMP · VTR verificación estado citas (24/9)", "nodes": [hook, get, cit, est],
          "connections": {"Webhook": {"main": [[{"node": N_GET, "type": "main", "index": 0}]]},
                          N_GET: {"main": [[{"node": N_CITAS, "type": "main", "index": 0}]]},
                          N_CITAS: {"main": [[{"node": N_EST, "type": "main", "index": 0}]]}},
          "settings": {"executionOrder": "v1"}}
    c, r = p.api("POST", "/workflows", wf)
    if c not in (200, 201):
        sys.exit(f"❌ crear {c} {r}")
    wid = r["id"]
    try:
        c2, r2 = p.api("POST", f"/workflows/{wid}/activate")
        if c2 != 200:
            sys.exit(f"❌ activar {c2} {r2}")
        time.sleep(2)
        casos = {"Mauricio (flag sin cita)": "uFx22fuKbExjkkUssx37", "Daiana (cita futura)": "PaByN20bCopWMAQFiLb8",
                 "Viri (link sin cita)": "GRgb6GQ4V8y4eAR3CrN9", "la agencia (citas canceladas)": "YIv9OmbKw2vtXHdX9OOO"}
        for k, v in casos.items():
            with urllib.request.urlopen(f"{p.BASE}/webhook/{path}?cid={v}", timeout=60) as resp:
                out = json.load(resp)
            print(f"=== {k}\n{out.get('estado')}\n  citas_ok={out.get('citas_ok')} vigente={out.get('cita_vigente')}")
    finally:
        print("temp: deactivate", p.api("POST", f"/workflows/{wid}/deactivate")[0],
              "delete", p.api("DELETE", f"/workflows/{wid}")[0])


def main():
    if "--verificar" in sys.argv:
        return verificar()
    c, wf = p.api("GET", f"/workflows/{MAIN}")
    if c != 200:
        sys.exit(f"❌ GET main {c} {wf}")
    if MARK in json.dumps(wf, ensure_ascii=False):
        print("↷ ya aplicado"); return
    pre = copy.deepcopy(wf)
    patch_main(wf)
    if "--execute" not in sys.argv:
        print(f"[dry-run] ok · nodos {len(pre['nodes'])} → {len(wf['nodes'])} · activo={wf['active']}"); return
    h0 = p.save(pre, OUT / "pre" / "main-paso1.json")
    body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
            "settings": {k: v for k, v in (wf.get("settings") or {}).items() if k in p.SETTINGS_OK}}
    c, r = p.api("PUT", f"/workflows/{MAIN}", body)
    if c != 200:
        sys.exit(f"❌ PUT {c} {r}")
    c, post = p.api("GET", f"/workflows/{MAIN}")
    h1 = p.save(post, OUT / "post" / "main-paso1.json")
    chk = {
        "marca": MARK in json.dumps(post, ensure_ascii=False),
        "activo": post["active"],
        "nodos": len(post["nodes"]) == len(pre["nodes"]) + 1,
        "get→citas": [t["node"] for o in post["connections"][N_GET]["main"] for t in o] == [N_CITAS],
        "citas→estado": [t["node"] for o in post["connections"][N_CITAS]["main"] for t in o] == [N_EST],
        "builder": p.node(post, N_EST)["parameters"]["jsCode"] == BUILDER,
        "cred": p.node(post, N_CITAS).get("credentials") == p.GHL_CRED,
    }
    print(("✅" if all(chk.values()) else "❌"), chk, f"· pre {h0[:12]} · post {h1[:12]}")


if __name__ == "__main__":
    main()
