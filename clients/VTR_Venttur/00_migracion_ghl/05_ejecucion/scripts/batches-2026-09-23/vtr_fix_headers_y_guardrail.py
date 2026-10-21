#!/usr/bin/env python3
"""Fix 23/9 noche.
1. Headers: 16 HTTP Request (despachador, barrido, clasificador, W11) tenían los headers en `parametersHeaders.values`
   (formato de las tools del agente); el HTTP Request v4.2 lee `headerParameters.parameters` → no mandaban `Version`
   y GHL respondía 401 "version header was not found" (visto en la ejecución 1495493 del clasificador). Con
   onError=continue el fallo era silencioso: el barrido nunca marcaba, W11 nunca estampaba Contestó, el despachador
   no encontraba candidatos.
2. Guardrail de promesa fantasma (main): una pregunta no es una promesa. "¿Te queda mejor hoy o mañana para agendar
   una videollamada?" se interceptaba y reemplazaba una buena respuesta (ejecución 1495490). Ahora sólo analiza las
   oraciones afirmativas.
Idempotente. Pre/post en 03_workflows/ghl-live-2026-09-23-pre-bsp-fixes/headers-guardrail/."""
import json, sys, importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("p", Path(__file__).with_name("vtr_pre_bsp_fixes.py"))
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
OUT = p.OUT / "headers-guardrail"
WFS = {"despachador": "vrShEXQGGAo4FqAt", "barrido": "LrJuzU7qDeELWiAl", "clasificador": "Xmyoewwa1W5gm1fy",
       "w11": "qYgeTc9PCq3TiGDn", "main": "1eS1Z5k898c3ATnf"}
ANCLA = "const fullText = (p1 + ' ' + p2 + ' ' + p3).toLowerCase();"
NUEVO = ("// GUARD-Q-0923: sólo oraciones afirmativas. Una pregunta (\"¿te queda hoy o mañana?\") no es una promesa.\n"
         "const fullText = (p1 + '. ' + p2 + '. ' + p3).split(/(?<=[.!?\\n])\\s+/)"
         ".filter(o => o.indexOf('?') === -1).join(' ').toLowerCase();")


def fix(wf):
    cambios = []
    for n in wf["nodes"]:
        pr = n["parameters"]
        if n["type"].endswith("httpRequest") and "parametersHeaders" in pr:
            vals = pr.pop("parametersHeaders").get("values", [])
            pr["sendHeaders"] = True
            pr["headerParameters"] = {"parameters": [{"name": v["name"], "value": v.get("value", "")} for v in vals]}
            cambios.append(n["name"])
        if n["name"] == "Detectar promesa fantasma" and "GUARD-Q-0923" not in pr["jsCode"]:
            p.replace_in(n, ANCLA, NUEVO)
            cambios.append(n["name"])
    return cambios


for alias, wid in WFS.items():
    c, wf = p.api("GET", f"/workflows/{wid}")
    ch = fix(wf)
    if not ch:
        print(f"↷ {alias:12s} nada que corregir"); continue
    if "--execute" not in sys.argv:
        print(f"[dry-run] {alias:12s} activo={wf['active']} · {ch}"); continue
    c0, pre = p.api("GET", f"/workflows/{wid}"); p.save(pre, OUT / "pre" / f"{alias}.json")
    body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
            "settings": {k: v for k, v in (wf.get("settings") or {}).items() if k in p.SETTINGS_OK}}
    c, r = p.api("PUT", f"/workflows/{wid}", body)
    if c != 200:
        sys.exit(f"❌ PUT {alias} {c} {r}")
    c, post = p.api("GET", f"/workflows/{wid}"); p.save(post, OUT / "post" / f"{alias}.json")
    print(f"✅ {alias:12s} {len(ch)} nodos · activo={post['active']}")
