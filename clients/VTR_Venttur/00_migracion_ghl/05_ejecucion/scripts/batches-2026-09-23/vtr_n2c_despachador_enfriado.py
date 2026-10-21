#!/usr/bin/env python3
"""N2c (24/9): el carril `rescate` del despachador se superponía con el workflow de rescate (Fase 1 a los 45 min y
Fase 2 a las 22 h del link): Viri recibió la Fase 1 a las 03:51 y el despachador le iba a mandar `agenda_seg` a las
16:00. Los carriles rescate y nurturing ahora exigen ≥24 h sin actividad del lead (`ultima_actividad`): no se
interrumpe a quien está conversando y las primeras 24 h después del link son del workflow de rescate.
Idempotente (ENFRIADO-0924)."""
import sys, importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("p", Path(__file__).with_name("vtr_pre_bsp_fixes.py"))
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
WID = "vrShEXQGGAo4FqAt"; OUT = p.OUT / "n2-despachador"
c, wf = p.api("GET", f"/workflows/{WID}")
n = p.node(wf, "Seleccionar (tope-2 + prioridad)")
if "ENFRIADO-0924" in n["parameters"]["jsCode"]: sys.exit("↷ ya aplicado")
p.replace_in(n, "const reciente = (iso) =>",
             "// ENFRIADO-0924: ≥24 h sin actividad del lead (rescate y nurturing)\n"
             "const enfriado = (iso) => { const t = iso ? Date.parse(iso) : NaN; return !isNaN(t) && (now - t) >= 24*36e5; };\n"
             "const reciente = (iso) =>")
p.replace_in(n, "if (gate(c) && reciente(cfv(c,UAF))) sel.set(c.id, mk(c,'rescate'));",
             "if (gate(c) && reciente(cfv(c,UAF)) && enfriado(cfv(c,UAF))) sel.set(c.id, mk(c,'rescate'));")
p.replace_in(n, "if (gate(c) && reciente(cfv(c,UAF))) sel.set(c.id, mk(c,'nurturing'));",
             "if (gate(c) && reciente(cfv(c,UAF)) && enfriado(cfv(c,UAF))) sel.set(c.id, mk(c,'nurturing'));")
if "--execute" not in sys.argv: print("[dry-run] ok"); sys.exit()
c0, pre = p.api("GET", f"/workflows/{WID}"); p.save(pre, OUT / "pre" / "despachador-enfriado.json")
body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
        "settings": {k: v for k, v in (wf.get("settings") or {}).items() if k in p.SETTINGS_OK}}
c, r = p.api("PUT", f"/workflows/{WID}", body)
if c != 200: sys.exit(f"❌ PUT {c} {r}")
c, post = p.api("GET", f"/workflows/{WID}"); p.save(post, OUT / "post" / "despachador-enfriado.json")
print("✅ rescate/nurturing con ≥24 h sin actividad · envío habilitado:", not p.node(post, "Enviar template GHL").get("disabled"))
