#!/usr/bin/env python3
"""N2 (23/9 noche): después del BSP los templateId de GHL cambiaron (los 6 del despachador dan "Template not found")
y la API pública no lista plantillas de WhatsApp. Lo que sí funciona (capturado de la UI de GHL y probado por API con
el PIT, 201 + delivered): POST /conversations/messages con
  {type:'WhatsApp', contactId, message:<texto>, whatsapp:{type:'template', template:{name, lang, category},
   placeholders:{header:[], body:[vars], buttons:[]}}}
Este script:
  1. `Seleccionar`: elige la plantilla por carril y toque (y programa), con su texto renderizado.
       rescate   → toque 1 agenda_seg · toque 2 seguimiento_dia_3_<prog>
       nurturing → toque 1 seguimiento_dia_1_<prog> · toque 2 seguimiento_dia_3_<prog>
       outreach  → toque 1 boarding_form_followup · toque 2 boarding_form_followup_touch2
     prog: bs (Internados) · aa (Intercambio) · sc (Campamentos) · ptw (Pathway) · gy (Gap Year) · gen (resto / sin programa)
  2. `Enviar template GHL`: el body nuevo (nombre + idioma + variables).
  3. `Update toques` y `Siembra memoria` corren sólo si el envío devolvió messageId (antes corrían aunque fallara);
     la memoria guarda el texto real enviado.
Deja los nodos de envío con el estado disabled que tengan (habilitar con vtr_post2_despachador.py --habilitar-envio).
Catálogo de plantillas (texto, idioma, variables): 06_docs/plantillas-ghl-waba-nueva-2026-09-23.json"""
import json, sys, uuid, importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("p", Path(__file__).with_name("vtr_pre_bsp_fixes.py"))
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
OUT = p.OUT / "n2-despachador"; WID = "vrShEXQGGAo4FqAt"
CAT = p.ROOT / "clients/VTR_Venttur/06_docs/plantillas-ghl-waba-nueva-2026-09-23.json"
SEL = "Seleccionar (tope-2 + prioridad)"


def plantillas_js():
    cat = json.loads(CAT.read_text())
    return json.dumps({k: {"lang": v["lang"], "category": v["category"], "body": v["body"]} for k, v in cat.items()},
                      ensure_ascii=False)


NUEVO = """// Plantillas por carril y toque (N2-0923). GHL manda la plantilla por NOMBRE + idioma + variables
// (los templateId cambiaron con el BSP y no hay API para listarlos). Catálogo: 06_docs/plantillas-ghl-waba-nueva-2026-09-23.json
const PLANTILLAS = __CAT__;
function progCode(programa) {
  const p = String(programa || '').toLowerCase();
  if (/internado|boarding/.test(p)) return 'bs';
  if (/intercambio|familia|\\baa\\b|a[nñ]o acad/.test(p)) return 'aa';
  if (/campament|summer/.test(p)) return 'sc';
  if (/pathway|alemania/.test(p)) return 'ptw';
  if (/gap|hapy|happy|estudi.*trabaj/.test(p)) return 'gy';
  return 'gen';
}
function elegirPlantilla(lane, toques, programa) {
  const pc = progCode(programa);
  const d1 = pc === 'sc' ? 'seguimiento_dia_1_plantilla_sc' : 'seguimiento_dia_1_' + pc;
  const d3 = 'seguimiento_dia_3_' + pc;
  if (lane === 'outreach') return toques >= 1 ? 'boarding_form_followup_touch2' : 'boarding_form_followup';
  if (lane === 'rescate') return toques >= 1 ? d3 : 'agenda_seg';
  return toques >= 1 ? d3 : d1;
}
function armarPlantilla(name, firstName) {
  const t = PLANTILLAS[name]; if (!t) return null;
  const nombre = String(firstName || '').trim().split(/\\s+/)[0] || 'qué tal';
  const nVars = (t.body.match(/\\{\\{\\d+\\}\\}/g) || []).length;
  const vars = nVars ? [nombre] : [];
  return { name, lang: t.lang, category: t.category, vars, texto: t.body.replace(/\\{\\{1\\}\\}/g, nombre) };
}
"""

MK_OLD = """const mk = (c, lane) => {
  const programa = cfv(c, PROGRAMA_FIELD);
  const templateId = resolveTemplate(programa);
  return {"""
MK_NEW = """const mk = (c, lane) => {
  const programa = cfv(c, PROGRAMA_FIELD);
  const plantilla = armarPlantilla(elegirPlantilla(lane, Number(cfv(c,T))||0, programa), c.firstName);
  const templateId = plantilla ? plantilla.name : null;   // el IF `Tiene templateId?` sigue mirando este campo
  return {
    plantilla,"""

BODY = ("={{ JSON.stringify({ type: 'WhatsApp', contactId: $json.contactId, message: $json.plantilla.texto, "
        "whatsapp: { type: 'template', template: { name: $json.plantilla.name, lang: $json.plantilla.lang, "
        "category: $json.plantilla.category }, placeholders: { header: [], body: $json.plantilla.vars, buttons: [] } } }) }}")

c, wf = p.api("GET", f"/workflows/{WID}")
sel = p.node(wf, SEL)
code = sel["parameters"]["jsCode"]
if "N2-0923" in code:
    sys.exit("↷ ya aplicado")
i = code.find("// Template IDs por programa"); j = code.find("// sessionKey canónico")
assert i > 0 and j > i, "anclas de Seleccionar"
code = code[:i] + NUEVO.replace("__CAT__", plantillas_js()) + "\n" + code[j:]
assert MK_OLD in code
sel["parameters"]["jsCode"] = code.replace(MK_OLD, MK_NEW)

env = p.node(wf, "Enviar template GHL")
env["parameters"]["jsonBody"] = BODY
for h in env["parameters"]["headerParameters"]["parameters"]:
    if h["name"] == "Version": h["value"] = "2021-04-15"

S = f"$('{SEL}').item.json"
upd = p.node(wf, "Update toques (+1)")
upd["parameters"]["url"] = f"=https://services.leadconnectorhq.com/contacts/{{{{ {S}.contactId }}}}"
upd["parameters"]["jsonBody"] = ('={"customFields":[{"id":"ez934lu03v7nC4ZRS7LJ","value":{{ (' + S + '.toques_actual||0)+1 }}},'
                                 '{"id":"P3a7nGkO57LwCvHhYQyc","value":"{{ $now.toISO() }}"}]}')
mem = p.node(wf, "Siembra memoria (Supabase)")
mem["parameters"]["options"]["queryReplacement"] = (
    "={{ [ " + S + ".session_key, JSON.stringify({type:'ai', content: " + S + ".plantilla.texto}) ] }}")
x, y = env["position"]
ok = p.if_bool("¿Enviado?", [x + 220, y], "={{ !!$json.messageId }}")
ok["parameters"]["conditions"]["conditions"][0]["operator"] = {"type": "boolean", "operation": "true", "singleValue": True}
wf["nodes"].append(ok)
p.set_targets(wf, "Tiene templateId?", 0, ["Enviar template GHL"])
p.set_targets(wf, "Enviar template GHL", 0, ["¿Enviado?"])
p.set_targets(wf, "¿Enviado?", 0, ["Update toques (+1)", "Siembra memoria (Supabase)"])
if "--execute" not in sys.argv:
    sys.exit("[dry-run] ok")
c0, pre = p.api("GET", f"/workflows/{WID}"); p.save(pre, OUT / "pre" / "despachador.json")
body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
        "settings": {k: v for k, v in (wf.get("settings") or {}).items() if k in p.SETTINGS_OK}}
c, r = p.api("PUT", f"/workflows/{WID}", body)
if c != 200: sys.exit(f"❌ PUT {c} {r}")
c, post = p.api("GET", f"/workflows/{WID}"); p.save(post, OUT / "post" / "despachador.json")
print("✅ despachador con plantillas por nombre · activo", post["active"],
      "· envío deshabilitado:", p.node(post, "Enviar template GHL").get("disabled"))
