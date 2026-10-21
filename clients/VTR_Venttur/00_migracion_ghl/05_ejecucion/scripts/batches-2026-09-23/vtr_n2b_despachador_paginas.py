#!/usr/bin/env python3
"""N2b (23/9 noche): las 3 consultas del despachador traían sólo 100 contactos sin orden (rescate tiene 1.015 y Form
Meta 457): un lead nuevo podía quedar fuera. pageLimit 500 + orden descendente (Form Meta por dateAdded; rescate y
nurturing por dateUpdated), así los recientes — los únicos que pasan el filtro de 30 días — siempre entran."""
import json, sys, importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("p", Path(__file__).with_name("vtr_pre_bsp_fixes.py"))
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
OUT = p.OUT / "n2-despachador"; WID = "vrShEXQGGAo4FqAt"
c, wf = p.api("GET", f"/workflows/{WID}")
for nm, campo in (("Query rescate", "dateUpdated"), ("Query nurturing", "dateUpdated"), ("Query outreach (Form Meta)", "dateAdded")):
    n = p.node(wf, nm); b = json.loads(n["parameters"]["jsonBody"])
    b["pageLimit"] = 500; b["sort"] = [{"field": campo, "direction": "desc"}]
    n["parameters"]["jsonBody"] = json.dumps(b, ensure_ascii=False)
if "--execute" not in sys.argv: sys.exit("[dry-run] ok")
c0, pre = p.api("GET", f"/workflows/{WID}"); p.save(pre, OUT / "pre" / "despachador-paginas.json")
body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
        "settings": {k: v for k, v in (wf.get("settings") or {}).items() if k in p.SETTINGS_OK}}
c, r = p.api("PUT", f"/workflows/{WID}", body)
if c != 200: sys.exit(f"❌ PUT {c} {r}")
c, post = p.api("GET", f"/workflows/{WID}"); p.save(post, OUT / "post" / "despachador-paginas.json"); print("✅ 3 consultas con 500 + orden desc")
