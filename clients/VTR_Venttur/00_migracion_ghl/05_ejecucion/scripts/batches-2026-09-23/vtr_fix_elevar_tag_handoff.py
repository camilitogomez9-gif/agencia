#!/usr/bin/env python3
"""Fix 23/9 noche: `elevar` ponía sólo `bot_pausado`. El workflow GHL `Handoff · Notificación al equipo` (mails
internos a Max y Mauricio) se dispara con la etiqueta `atencion_humana`, así que nunca corría. Se agregan las dos.
Idempotente. Pre/post en 03_workflows/ghl-live-2026-09-23-pre-bsp-fixes/elevar-tag-handoff/."""
import sys, importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("p", Path(__file__).with_name("vtr_pre_bsp_fixes.py"))
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
OUT = p.OUT / "elevar-tag-handoff"; WID = p.IDS["elevar"]
c, wf = p.api("GET", f"/workflows/{WID}")
n = p.node(wf, "1. Tag bot_pausado (pausar bot)")
old = "={{ JSON.stringify({ tags: ['bot_pausado'] }) }}"
if n["parameters"]["jsonBody"] != old:
    sys.exit(f"↷ ya aplicado o distinto: {n['parameters']['jsonBody']}")
if "--execute" not in sys.argv:
    sys.exit("[dry-run] agregaría atencion_humana")
p.save(wf, OUT / "pre" / "elevar.json")
n["parameters"]["jsonBody"] = "={{ JSON.stringify({ tags: ['bot_pausado', 'atencion_humana'] }) }}"
body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
        "settings": {k: v for k, v in (wf.get("settings") or {}).items() if k in p.SETTINGS_OK}}
c, r = p.api("PUT", f"/workflows/{WID}", body)
if c != 200: sys.exit(f"❌ PUT {c} {r}")
c, post = p.api("GET", f"/workflows/{WID}"); p.save(post, OUT / "post" / "elevar.json")
print("✅ elevar pone bot_pausado + atencion_humana")
