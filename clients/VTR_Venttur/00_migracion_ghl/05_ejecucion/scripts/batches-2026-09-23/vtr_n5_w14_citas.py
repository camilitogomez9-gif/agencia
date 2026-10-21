#!/usr/bin/env python3
"""N5 (23/9): W14 (correo semanal) contaba oportunidades del pipeline OP·Bot en etapas de cita, pero nada crea
oportunidades ahí → el lunes iba a decir 0. Ahora cuenta las citas reales de los 10 calendarios de leads (8 de
programa + Juan José + Niza), creadas en los últimos 7 días y no canceladas, sin los contactos de prueba, con el
desglose por programa.
  --execute                aplica el cambio (snapshot pre/post)
  --prueba-a CORREO HH:MM  (con el workflow activo) manda la próxima corrida a CORREO a esa hora (hora del
                           servidor n8n) en vez de administracion@; --restaurar lo deja como estaba."""
import copy, json, sys, uuid, importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("p", Path(__file__).with_name("vtr_pre_bsp_fixes.py"))
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
OUT = p.OUT / "n5-w14"; WID = "OaOyHA2tfjMtuWTk"
CALS = {"CIxOV100yyRFqPoa6LdK": "Internados", "SiAPsk27X5yilff5bSS5": "Intercambio académico con familias",
        "981EzNS7jf9HhJNkL41W": "Campamentos de verano", "oNN7oLWsNhQlWi7q7pDX": "Pathway Alemania",
        "Omgde6Ko8TGKYMtiUb1x": "Gap Year / Estudia y Trabaja", "5PxslDhdQxZeDcKmLYNq": "Cursos de idiomas",
        "RUjWx74NPK77FPUcs5ME": "Educación superior", "j0jcAdaieJXaoPZBempp": "Viajes educativos",
        "QJQyabdWhBgYtjeGcEKZ": "Asesoría con Juan José Alfaro", "fOsl9U4b40ulCczFwf69": "Asesoría con Niza Valeriano"}
PRUEBA = ["YIv9OmbKw2vtXHdX9OOO", "8m2b1HHEgoEf2hy5X6CA"]  # la agencia Test ×2

GEN = f"""// W14 · un item por calendario de leads (N5-0923)
const CALS = {json.dumps(CALS, ensure_ascii=False)};
const now = Date.now();
return Object.entries(CALS).map(([calendarId, programa]) => ({{ json: {{ calendarId, programa,
  startTime: String(now - 7*864e5), endTime: String(now + 120*864e5) }} }}));"""

CONTAR = f"""// W14 · cuenta CITAS AGENDADAS en la semana (creadas en los últimos 7 días, no canceladas).  N5-0923
// Fuente: API de calendarios de GHL (antes contaba oportunidades de OP·Bot, que nadie crea).
const PRUEBA = {json.dumps(PRUEBA)};
const now = Date.now(); const WEEK = 7*864e5;
const cals = $('Calendarios').all().map(i => i.json);
const res = $input.all();
const vistos = new Set(); const porPrograma = {{}};
res.forEach((it, idx) => {{
  const programa = (cals[idx] || {{}}).programa || 'Otro';
  for (const e of ((it.json && it.json.events) || [])) {{
    if (!e || vistos.has(e.id)) continue;
    if (e.deleted || /cancel|invalid/i.test(e.appointmentStatus || '')) continue;
    if (PRUEBA.includes(e.contactId)) continue;
    const creada = Date.parse(e.dateAdded || '');
    if (!creada || now - creada > WEEK) continue;
    vistos.add(e.id); porPrograma[programa] = (porPrograma[programa] || 0) + 1;
  }}
}});
const n = vistos.size;
const d0 = new Date(now - WEEK).toISOString().slice(0,10);
const d1 = new Date(now).toISOString().slice(0,10);
const semana = d0 + ' → ' + d1;
const filas = Object.entries(porPrograma).sort((a,b) => b[1]-a[1])
  .map(([k,v]) => `<tr><td style="padding:6px 0;color:#333;font-size:14px">${{k}}</td><td style="padding:6px 0;text-align:right;font-weight:700;color:#0d0a1f">${{v}}</td></tr>`).join('');
const html = `<!DOCTYPE html><html><body style="margin:0;font-family:Arial,Helvetica,sans-serif;background:#0d0a1f;padding:24px"><div style="max-width:520px;margin:0 auto;background:#ffffff;border-radius:12px;overflow:hidden"><div style="height:6px;background:#7c3aed"></div><div style="padding:28px"><h2 style="color:#0d0a1f;margin:0 0 4px">Resumen semanal Venttur</h2><p style="color:#888;margin:0 0 20px;font-size:13px">Semana ${{semana}}</p><div style="background:#f5f3ff;border-radius:10px;padding:24px;text-align:center"><div style="font-size:46px;font-weight:800;color:#7c3aed;line-height:1">${{n}}</div><div style="color:#333;font-size:15px;margin-top:4px">citas agendadas</div></div>${{filas ? `<table style="width:100%;margin-top:18px;border-collapse:collapse">${{filas}}</table>` : ''}}</div><div style="background:#0d0a1f;color:#a78bfa;padding:14px;text-align:center;font-size:12px">la agencia</div></div></body></html>`;
return [{{ json: {{ citas_agendadas: n, por_programa: porPrograma, semana, html, subject: `📊 Resumen semanal Venttur — ${{n}} citas agendadas` }} }}];"""


def put(wf, tag):
    c0, pre = p.api("GET", f"/workflows/{WID}"); p.save(pre, OUT / "pre" / f"w14-{tag}.json")
    body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
            "settings": {k: v for k, v in (wf.get("settings") or {}).items() if k in p.SETTINGS_OK}}
    c, r = p.api("PUT", f"/workflows/{WID}", body)
    if c != 200: sys.exit(f"❌ PUT {c} {r}")
    c, post = p.api("GET", f"/workflows/{WID}"); p.save(post, OUT / "post" / f"w14-{tag}.json"); return post


c, wf = p.api("GET", f"/workflows/{WID}")
if "--prueba-a" in sys.argv:
    i = sys.argv.index("--prueba-a"); correo, hhmm = sys.argv[i + 1], sys.argv[i + 2]; hh, mm = hhmm.split(":")
    gm = next(n for n in wf["nodes"] if n["type"].endswith("gmail"))
    gm["parameters"]["sendTo"] = correo; gm["parameters"]["options"].pop("bccList", None)
    st = p.node(wf, "Schedule Trigger")
    st["parameters"]["rule"] = {"interval": [{"field": "cronExpression", "expression": f"{int(mm)} {int(hh)} * * *"}]}
    post = put(wf, "prueba"); print("prueba programada", hhmm, "→", correo, "activo", post["active"]); sys.exit()
if "--restaurar" in sys.argv:
    gm = next(n for n in wf["nodes"] if n["type"].endswith("gmail"))
    gm["parameters"]["sendTo"] = "administracion@venttur.com"; gm["parameters"]["options"]["bccList"] = "camilitogomez9@gmail.com"
    p.node(wf, "Schedule Trigger")["parameters"]["rule"] = {"interval": [{"field": "weeks", "triggerAtDay": [1], "triggerAtHour": 10}]}
    post = put(wf, "restaurado"); print("restaurado · activo", post["active"]); sys.exit()
if p.has(wf, "Calendarios"):
    sys.exit("↷ ya aplicado")
q = p.node(wf, "GHL Query OP·Bot"); x, y = q["position"]
wf["nodes"] = [n for n in wf["nodes"] if n["name"] != "GHL Query OP·Bot"]
wf["connections"].pop("GHL Query OP·Bot", None)
wf["nodes"].append(p.code_node("Calendarios", [x, y], GEN))
http = p.http_node("GHL citas por calendario", [x + 200, y], "GET", "https://services.leadconnectorhq.com/calendars/events",
                   version="2021-04-15", flags={"onError": "continueRegularOutput"})
http["parameters"]["sendQuery"] = True
http["parameters"]["queryParameters"] = {"parameters": [
    {"name": "locationId", "value": p.LOC}, {"name": "calendarId", "value": "={{ $json.calendarId }}"},
    {"name": "startTime", "value": "={{ $json.startTime }}"}, {"name": "endTime", "value": "={{ $json.endTime }}"}]}
http["parameters"]["options"] = {"batching": {"batch": {"batchSize": 1, "batchInterval": 500}}}
wf["nodes"].append(http)
p.node(wf, "Contar citas")["parameters"]["jsCode"] = CONTAR
p.set_targets(wf, "Schedule Trigger", 0, ["Calendarios"])
p.set_targets(wf, "Calendarios", 0, ["GHL citas por calendario"])
p.set_targets(wf, "GHL citas por calendario", 0, ["Contar citas"])
for n in wf["nodes"]:
    if n["type"] == "n8n-nodes-base.stickyNote":
        n["parameters"]["content"] = ("## W14 Correo semanal (GHL)\n- Métrica (D6): citas creadas en los últimos 7 días en los 10 calendarios de leads, "
                                      "no canceladas, sin contactos de prueba. Fuente: API de calendarios (N5, 23/9).\n- Destinatario: administracion@venttur.com (CCO Camilo).")
if "--execute" not in sys.argv:
    sys.exit("[dry-run] ok")
post = put(wf, "n5"); print("✅ W14 cuenta citas reales ·", len(post["nodes"]), "nodos · activo", post["active"])
