#!/usr/bin/env python3
"""Fix 23/9 noche · avisos de `elevar` (v9XkOfL9dQtY2wyv).
- El Telegram iba al grupo -4925599962 (es el de Happy Flops; el bot no está) → "chat not found" (ejecución 1495639).
  Pasa al chat 6390727286, el que usan las demás alertas de VTR.
- D3 (decisiones del cliente): las notificaciones van a administracion@venttur.com → Gmail nuevo (misma credencial
  que W14).
- El último nodo devolvía el error de Telegram como resultado de la tool y el agente le decía al lead "hubo un
  problema". Nodo final `Respuesta al agente` con un resultado limpio.
Idempotente (marca AVISOS-0923). Pre/post en 03_workflows/ghl-live-2026-09-23-pre-bsp-fixes/elevar-avisos/."""
import sys, uuid, json, importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("p", Path(__file__).with_name("vtr_pre_bsp_fixes.py"))
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
OUT = p.OUT / "elevar-avisos"
WID = p.IDS["elevar"]
T = "$('When Executed by Another Workflow').first().json"
LINK = f"https://app.gohighlevel.com/v2/location/{p.LOC}/contacts/detail/{{{{ {T}.contact_id }}}}"

c, wf = p.api("GET", f"/workflows/{WID}")
if "AVISOS-0923" in json.dumps(wf, ensure_ascii=False):
    sys.exit("↷ ya aplicado")
tg = p.node(wf, "3. Telegram notify")
tg["parameters"]["chatId"] = "6390727286"
tg["notes"] = "AVISOS-0923: antes -4925599962 (grupo de Happy Flops, el bot no está)."
x, y = tg["position"]
gm = {"parameters": {"sendTo": "administracion@venttur.com",
                     "subject": f"=Lead derivado a un asesor · {{{{ {T}.contact_id }}}}",
                     "emailType": "text",
                     "message": (f"=Un lead pidió hablar con una persona y el bot dejó de responderle.\n\n"
                                 f"Contacto en GHL: {LINK}\n\nResumen del bot:\n{{{{ {T}.resumen }}}}\n\n"
                                 "Para devolverle la conversación al bot, sacar la etiqueta bot_pausado del contacto."),
                     "options": {"appendAttribution": False, "bccList": "camilitogomez9@gmail.com"}},
      "name": "4. Mail administración", "type": "n8n-nodes-base.gmail", "typeVersion": 2.1,
      "position": [x + 220, y], "id": str(uuid.uuid4()),
      "credentials": {"gmailOAuth2": {"id": "5R0ScEVqcfjKYanp", "name": "Gmail | la agencia®"}},
      "onError": "continueRegularOutput"}
res = {"parameters": {"mode": "raw", "jsonOutput": '={"ok": true, "resultado": "Conversación derivada a un asesor humano. Avísale al lead que un asesor le va a escribir por este mismo chat en breve. No le digas que hubo un error."}', "options": {}},
       "name": "Respuesta al agente", "type": "n8n-nodes-base.set", "typeVersion": 3.4,
       "position": [x + 440, y], "id": str(uuid.uuid4()), "notes": "AVISOS-0923"}
wf["nodes"] += [gm, res]
p.set_targets(wf, "3. Telegram notify", 0, ["4. Mail administración"])
p.set_targets(wf, "4. Mail administración", 0, ["Respuesta al agente"])
if "--execute" not in sys.argv:
    sys.exit(f"[dry-run] ok · activo={wf['active']}")
c0, pre = p.api("GET", f"/workflows/{WID}"); p.save(pre, OUT / "pre" / "elevar.json")
body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
        "settings": {k: v for k, v in (wf.get("settings") or {}).items() if k in p.SETTINGS_OK}}
c, r = p.api("PUT", f"/workflows/{WID}", body)
if c != 200:
    sys.exit(f"❌ PUT {c} {r}")
c, post = p.api("GET", f"/workflows/{WID}"); p.save(post, OUT / "post" / "elevar.json")
print(f"✅ elevar: Telegram → 6390727286, mail a administracion@, respuesta limpia · {len(post['nodes'])} nodos")
