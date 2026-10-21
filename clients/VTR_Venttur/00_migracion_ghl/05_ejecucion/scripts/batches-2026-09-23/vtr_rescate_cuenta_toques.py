#!/usr/bin/env python3
"""24/9: el rescate (Fase 1 / Fase 2) no sumaba `toques_enviados` ni `ultimo_toque_at`, así que el tope global de 2
(D2) y el mínimo de 24 h entre toques del despachador no lo veían (Viri: rescate Fase 1 03:51 y el despachador le iba
a mandar otro). Después de cada envío exitoso (messageId), +1 toque y ultimo_toque_at = ahora.
Idempotente (TOQUES-RESCATE-0924)."""
import sys, importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("p", Path(__file__).with_name("vtr_pre_bsp_fixes.py"))
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
WID = "YB0UxwEVwzISdd54"; OUT = p.OUT / "rescate-toques"
CODE = """// TOQUES-RESCATE-0924: sólo si el envío devolvió messageId
const env = $input.first().json || {};
if (!env.messageId) return [];
const c = (($('__GET__').first().json || {}).contact) || {};
const cf = {}; for (const x of (c.customFields || [])) cf[x.id] = x.value;
const toques = Number(cf['ez934lu03v7nC4ZRS7LJ']) || 0;
return [{ json: { contactId: c.id || $('__CODE__').first().json.contactId,
  body: { customFields: [ { id: 'ez934lu03v7nC4ZRS7LJ', value: toques + 1 }, { id: 'P3a7nGkO57LwCvHhYQyc', value: new Date().toISOString() } ] } } }];"""
c, wf = p.api("GET", f"/workflows/{WID}")
if any(n["name"].startswith("Toque +1") for n in wf["nodes"]): sys.exit("↷ ya aplicado")
for fase, send, get, code in (("1", "GHL: Send WhatsApp Fase 1", "GHL: Get Contact (1)", "Code: Fase 1 (GHL)"),
                              ("2", "GHL: Send WhatsApp Fase 2", "GHL: Get Contact (2)", "Code: Fase 2 (GHL)")):
    x, y = p.node(wf, send)["position"]
    cn = p.code_node(f"Toque +1 (Fase {fase})", [x + 220, y + 260], CODE.replace("__GET__", get).replace("__CODE__", code))
    hn = p.http_node(f"GHL: Update toques (Fase {fase})", [x + 440, y + 260], "PUT",
                     "=https://services.leadconnectorhq.com/contacts/{{ $json.contactId }}",
                     body="={{ JSON.stringify($json.body) }}", flags={"onError": "continueRegularOutput"})
    hn["parameters"]["specifyBody"] = "json"
    wf["nodes"] += [cn, hn]
    p.link(wf, send, cn["name"])
    p.set_targets(wf, cn["name"], 0, [hn["name"]])
if "--execute" not in sys.argv: print("[dry-run] ok"); sys.exit()
c0, pre = p.api("GET", f"/workflows/{WID}"); p.save(pre, OUT / "pre" / "rescate.json")
body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
        "settings": {k: v for k, v in (wf.get("settings") or {}).items() if k in p.SETTINGS_OK}}
c, r = p.api("PUT", f"/workflows/{WID}", body)
if c != 200: sys.exit(f"❌ PUT {c} {r}")
c, post = p.api("GET", f"/workflows/{WID}"); p.save(post, OUT / "post" / "rescate.json")
print("✅ rescate suma toques ·", len(post["nodes"]), "nodos · activo", post["active"])
