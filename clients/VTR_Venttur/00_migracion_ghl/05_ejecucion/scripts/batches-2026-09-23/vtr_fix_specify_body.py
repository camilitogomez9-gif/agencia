#!/usr/bin/env python3
"""Fix 23/9 noche: en los HTTP Request v4.2 con contentType=json, n8n usa `jsonBody` sólo si specifyBody='json';
sin eso manda el body por pares (vacío → {"": ""}). Lo tenían 9 nodos del stack nuevo (envío de WhatsApp del main,
upsert de W4 y W10, confirmación y marca de W6, pausa y asignación de elevar, PUT y disparo del rescate en W9):
ninguno mandaba su cuerpo. Verificado en la ejecución 1495468 del main (request body {"": ""}).
Idempotente. Guarda pre/post en 03_workflows/ghl-live-2026-09-23-pre-bsp-fixes/specify-body/."""
import sys, importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("p", Path(__file__).with_name("vtr_pre_bsp_fixes.py"))
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
IDS = {"main": "1eS1Z5k898c3ATnf", "w4": "LhPSfMYtQbNcEK32", "w6": "AS9ZNhY3GJDfhY3P", "w10": "MbPTKvy0bq8b4YAw",
       "elevar": "v9XkOfL9dQtY2wyv", "w9": "TROsQ5h78baAuVOY"}
OUT = p.OUT / "specify-body"
ex = "--execute" in sys.argv
for alias, wid in IDS.items():
    c, wf = p.api("GET", f"/workflows/{wid}")
    fix = [n for n in wf["nodes"] if n["type"].endswith("httpRequest") and n["parameters"].get("sendBody")
           and "jsonBody" in n["parameters"] and n["parameters"].get("specifyBody") != "json"]
    if not fix:
        print(f"↷ {alias:7s} nada que corregir"); continue
    if not ex:
        print(f"[dry-run] {alias:7s} activo={wf['active']} · {[n['name'] for n in fix]}"); continue
    p.save(wf, OUT / "pre" / f"{alias}.json")
    for n in fix:
        n["parameters"]["specifyBody"] = "json"
    body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
            "settings": {k: v for k, v in (wf.get("settings") or {}).items() if k in p.SETTINGS_OK}}
    c, r = p.api("PUT", f"/workflows/{wid}", body)
    if c != 200:
        sys.exit(f"❌ PUT {alias} {c} {r}")
    c, post = p.api("GET", f"/workflows/{wid}")
    p.save(post, OUT / "post" / f"{alias}.json")
    print(f"✅ {alias:7s} {len(fix)} nodos · activo={post['active']}")
