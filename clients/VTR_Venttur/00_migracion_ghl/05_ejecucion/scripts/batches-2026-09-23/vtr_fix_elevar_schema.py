#!/usr/bin/env python3
"""Fix 23/9 noche: el toolWorkflow `elevar` del main tenía workflowInputs.value sin `schema` → n8n le pasaba
contact_id/user_id/resumen en null al sub-workflow (ejecución 1495630: POST /contacts//tags → 404). Se agrega el
schema de los 3 campos. Idempotente. Pre/post en 03_workflows/ghl-live-2026-09-23-pre-bsp-fixes/elevar-schema/."""
import sys, importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("p", Path(__file__).with_name("vtr_pre_bsp_fixes.py"))
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
OUT = p.OUT / "elevar-schema"
c, wf = p.api("GET", f"/workflows/{p.IDS['main']}")
n = p.node(wf, "elevar")
wi = n["parameters"]["workflowInputs"]
if wi.get("schema"):
    sys.exit("↷ ya tiene schema")
wi["schema"] = [{"id": f, "displayName": f, "required": False, "defaultMatch": False, "display": True,
                 "canBeUsedToMatch": True, "type": "string", "removed": False}
                for f in ("contact_id", "user_id", "resumen")]
wi["matchingColumns"] = []
wi["attemptToConvertTypes"] = False
wi["convertFieldsToString"] = False
if "--execute" not in sys.argv:
    sys.exit(f"[dry-run] agregaría schema a elevar (main activo={wf['active']})")
p.save(wf, OUT / "pre" / "main.json")
p.save(wf, OUT / "pre" / "main.json")
c0, pre = p.api("GET", f"/workflows/{p.IDS['main']}"); p.save(pre, OUT / "pre" / "main.json")
body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
        "settings": {k: v for k, v in (wf.get("settings") or {}).items() if k in p.SETTINGS_OK}}
c, r = p.api("PUT", f"/workflows/{p.IDS['main']}", body)
if c != 200:
    sys.exit(f"❌ PUT {c} {r}")
c, post = p.api("GET", f"/workflows/{p.IDS['main']}"); p.save(post, OUT / "post" / "main.json")
print(f"✅ schema de elevar agregado · main activo={post['active']}")
