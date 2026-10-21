"""
FASE 4 · Increment 3 — sessionKey MX (52/521) sobre el staging (NO toca vivos).
Reescribe 'Normalizar payload' del staging 3sLd7KY3o8I7NvXi para:
  - emitir `phone` (canónico +E.164, MX 52/521 → +521<10>) — réplica de canon_phone del ETL (Fase 2).
  - sessionKey = canonPhone(phone) si hay teléfono; sino chatId (Telegram test → sigue por chatId,
    NO parte la sesión activa de la agencia).
Esto arregla el bug del vivo (sessionKey = replace(/[^0-9]/g,'') sin normalizar → doble sesión 52 vs 521).
Idempotente. Uso: python3 gen-staging-inc3.py
"""
import json, os, sys, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(__file__))
from _ghl_client import load_n8n, UA
BASE, KEY = load_n8n(); BASE = BASE.rstrip("/"); WID = "3sLd7KY3o8I7NvXi"

def n8n(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method,
        headers={"X-N8N-API-KEY": KEY, "User-Agent": UA, "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode(); return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")

JS = r"""// canon de teléfono MX (réplica de canon_phone del ETL Fase 2): 52/521 → +521<nac10>
function canonPhone(raw) {
  if (raw == null) return '';
  const digits = String(raw).replace(/\D/g, '');
  if (!digits) return '';
  if (digits.startsWith('52')) {
    const rest = digits.slice(2);
    if (rest.startsWith('1') && rest.length === 11) return '+521' + rest.slice(1);
    if (rest.length === 10) return '+521' + rest;
    return '+' + digits;
  }
  if (digits.length >= 10 && digits.length <= 15) return '+' + digits;
  return '+' + digits;
}
const u = $input.first().json;
const msg = u.message || u.edited_message || {};
const text = msg.text || msg.caption || '';
const chatId = String((msg.chat || {}).id || '');
const from = msg.from || {};
const name = ((from.first_name || '') + ' ' + (from.last_name || '')).trim();
// En producción (canal wa) el teléfono llega en el webhook; en el test por Telegram NO hay teléfono.
const phoneRaw = u.whatsapp_phone || u.phone || (msg.contact && msg.contact.phone_number) || '';
const phone = canonPhone(phoneRaw);
// sessionKey: por teléfono canónico si existe (evita doble sesión 52 vs 521); sino por chatId (Telegram)
const sessionKey = phone || chatId;
return [{ json: {
  message: text,
  chatId,
  phone,
  sessionKey,
  canal: 'telegram',
  name,
  email: `tg-${chatId}@venttur.test`,
  _raw: u,
}}];
"""

st, wf = n8n("GET", f"/api/v1/workflows/{WID}")
assert st == 200, f"no pude leer staging: {st}"
touched = False
for n in wf["nodes"]:
    if n["name"] == "Normalizar payload":
        n["parameters"]["jsCode"] = JS; touched = True
assert touched, "no encontré 'Normalizar payload'"
put = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
       "settings": wf.get("settings", {"executionOrder": "v1"})}
st, d = n8n("PUT", f"/api/v1/workflows/{WID}", put)
print("PUT →", st)
if st == 200:
    _, rb = n8n("GET", f"/api/v1/workflows/{WID}")
    nn = {x["name"]: x for x in rb["nodes"]}["Normalizar payload"]
    print("sessionKey line:", [l.strip() for l in nn["parameters"]["jsCode"].splitlines() if "sessionKey =" in l])
else:
    print(json.dumps(d)[:400])
