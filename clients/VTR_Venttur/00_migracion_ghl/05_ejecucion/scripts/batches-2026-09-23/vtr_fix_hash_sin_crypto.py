#!/usr/bin/env python3
"""Fix 23/9 noche: `Compute idempotency hash` del main usaba require('crypto'), que este n8n no permite en los Code
nodes (VMError: Cannot find module 'crypto') → el main fallaba en el 2.º nodo con cada mensaje. Se reemplaza por un
hash en JS puro (cyrb53 ×2 → 32 hex). Idempotente (marca HASH-JS-0923). Guarda pre/post en
03_workflows/ghl-live-2026-09-23-pre-bsp-fixes/. Sirve con el main prendido: sólo cambia el código de ese nodo."""
import json, sys, importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("p", Path(__file__).with_name("vtr_pre_bsp_fixes.py"))
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)

CODE = r"""// Idempotencia: por id de mensaje si GHL lo manda; si no, contact_id + date_created + body.  HASH-JS-0923
// Hash en JS puro: este n8n no permite require('crypto') en los Code nodes.
function cyrb53(str, seed) {
  let h1 = 0xdeadbeef ^ seed, h2 = 0x41c6ce57 ^ seed;
  for (let i = 0; i < str.length; i++) { const ch = str.charCodeAt(i);
    h1 = Math.imul(h1 ^ ch, 2654435761); h2 = Math.imul(h2 ^ ch, 1597334677); }
  h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507) ^ Math.imul(h2 ^ (h2 >>> 13), 3266489909);
  h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507) ^ Math.imul(h1 ^ (h1 >>> 13), 3266489909);
  return (h2 >>> 0).toString(16).padStart(8, '0') + (h1 >>> 0).toString(16).padStart(8, '0');
}
const item = $input.first().json;
const raw = item.message_id
  ? `mid::${item.message_id}`
  : `${item.contact_id || ''}::${item.date_created || ''}::${item.message_body || ''}`;
return [{ json: { ...item, dedup_hash: cyrb53(raw, 1) + cyrb53(raw, 2) } }];
"""

code, wf = p.api("GET", f"/workflows/{p.IDS['main']}")
n = p.node(wf, "Compute idempotency hash")
if "HASH-JS-0923" in n["parameters"]["jsCode"]:
    sys.exit("↷ ya aplicado")
if "--execute" not in sys.argv:
    sys.exit(f"[dry-run] reemplazaría el código de 'Compute idempotency hash' (main activo={wf['active']})")
p.save(wf, p.OUT / "pre" / "main-antes-hash-js.json")
n["parameters"]["jsCode"] = CODE
body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
        "settings": {k: v for k, v in (wf.get("settings") or {}).items() if k in p.SETTINGS_OK}}
c, r = p.api("PUT", f"/workflows/{p.IDS['main']}", body)
if c != 200:
    sys.exit(f"❌ PUT {c} {r}")
c, post = p.api("GET", f"/workflows/{p.IDS['main']}")
p.save(post, p.OUT / "post" / "main.json")
print(f"✅ hash en JS puro · main activo={post['active']}")
