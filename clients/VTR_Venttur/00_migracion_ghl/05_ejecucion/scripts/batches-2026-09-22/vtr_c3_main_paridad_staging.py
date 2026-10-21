#!/usr/bin/env python3
"""
Batch C.3 · Paridad del main de producción (1eS1Z5k898c3ATnf) con el agente staging testeado (3sLd7KY3o8I7NvXi).

Hallazgos de la auditoría 2026-09-22 (tarde) que esto corrige:
  1. Prompt: el main corría el prompt VIEJO (7 menciones a Diego, que ya no está · D9). → prompt del staging
     (= v2.2 del repo + regla cerrar_conversacion · el que pasó la regresión Nahe N1-N7).
  2. crear_contacto: escribía a Clientify+Airtable (muere el sábado; el nombre nunca llegaba a GHL).
     → toolHttpRequest PUT /contacts/{contact_id} en GHL (no pisa lastName si el lead no lo dijo).
  3. elevar: contact_id y user_id los inventaba el LLM ($fromAI) → handoff roto.
     → contact_id determinístico (Normalize GHL Payload) + user_id fijo Mauricio (paridad staging).
  4. cerrar_conversacion: no existía en el main → se porta del staging (estado_conversacion=Cerrada).
  5. [ESTADO DEL LEAD] se armaba desde Airtable (queda viejo post-cutover: link enviado/estado viven en GHL).
     → GET /contacts/{contact_id} + 'Construir estado lead' (código del staging, adaptado a GET).

Todo sigue OFF. Snapshot previo en ghl-live-2026-09-22-batch-C2/pre/. DRY=1 para no escribir.
"""
import json, os, subprocess, uuid, hashlib, tempfile, urllib.request

ROOT = "/Users/camilo/Downloads/camilo-workspace"
MAIN_ID = "1eS1Z5k898c3ATnf"
STG_ID = "3sLd7KY3o8I7NvXi"
BATCH = f"{ROOT}/clients/VTR_Venttur/03_workflows/ghl-live-2026-09-22-batch-C2"
GHL_CRED = {"httpHeaderAuth": {"id": "YkVmaA4jlRbO1TQD", "name": "GHL VTR (PIT)"}}
MAURICIO = "cXRMSnBx81rYivxQruKX"
AGENT = "Agente IA WPP"
NORM = "$('Normalize GHL Payload').first().json.contact_id"
GET_NODE = "GHL · Get contact (estado)"
EST_NODE = "Construir estado lead"


def env(k):
    for l in open(f"{ROOT}/.env"):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip()


BASE = env("N8N_BASE_URL").rstrip("/"); KEY = env("N8N_API_KEY")


def api(method, path, body=None):
    req = urllib.request.Request(BASE + "/api/v1" + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"X-N8N-API-KEY": KEY, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def nid(): return str(uuid.uuid4())


HDRS = {"values": [
    {"name": "Version", "valueProvider": "fieldValue", "value": "2021-07-28"},
    {"name": "Content-Type", "valueProvider": "fieldValue", "value": "application/json"},
    {"name": "Accept", "valueProvider": "fieldValue", "value": "application/json"},
]}

ESTADO_JS = r"""// Construir estado lead — portado del staging testeado (3sLd7KY3o8I7NvXi), adaptado a GET /contacts/{id}
const FID = {"programa_interes": "xK2NFqtz1DYUw3gYdn8I", "origen": "BEhJWnXS9SQovJTLSA2W", "fuente_lead": "2hv0GovhSzZO3hj9cFqm", "link_enviado": "rHzGNiesWuESPmSZyviJ", "estado_conversacion": "Omg1BvHmpXR0MMGsrpFh", "toques_enviados": "ez934lu03v7nC4ZRS7LJ", "grado_escolar": "HjNeRtIv6XHHMgFbtsaR", "inicio_deseado": "dUvMI4NaamfRPOF1p95q", "nivel_ingles": "uOecQsOv9i3uwMeSgEkX", "agendan_cita": "LwXu8AxMLhVGCbNmgzm2"};
let hit = null;
try {
  const r = $('GHL · Get contact (estado)').first().json || {};
  hit = r.contact || (r.body && r.body.contact) || null;
} catch (e) { hit = null; }
if (!hit || !hit.id) { return [{ json: { estado: 'Lead nuevo: no tenemos nada de esta persona todavia.', encontrado: false } }]; }
const cfs = {};
for (const x of (hit.customFields || [])) cfs[x.id] = x.value;
const V = (k) => cfs[FID[k]];
const truthy = (v) => v === true || v === 'true' || (Array.isArray(v) && v.includes('true'));
const L = [];
const nom = ((hit.firstName||'') + ' ' + (hit.lastName||'')).trim();
L.push('Nombre: ' + (nom ? nom + ' (ya lo sabes, no se lo vuelvas a preguntar)' : 'no disponible'));
const prog = (V('programa_interes')||'').toString().trim();
L.push('Programa de interes: ' + (prog && prog !== 'No definido' ? prog : 'sin definir'));
const org = (V('origen')||'').toString().trim(); const fue = (V('fuente_lead')||'').toString().trim();
L.push('Origen: ' + (org || fue || 'DESCONOCIDO'));
L.push('Link de agenda: ' + (truthy(V('link_enviado')) ? 'YA ENVIADO' : 'no enviado'));
if (truthy(V('agendan_cita'))) L.push('Cita: AGENDADA (no le vuelvas a mandar el link)');
const est = (V('estado_conversacion')||'').toString().trim(); if (est) L.push('Conversacion: ' + est);
const toq = V('toques_enviados'); if (toq) L.push('Toques enviados: ' + toq);
const form = [
  V('grado_escolar') ? 'grado ' + V('grado_escolar') : null,
  V('inicio_deseado') ? 'inicio ' + V('inicio_deseado') : null,
  V('nivel_ingles') ? 'ingles ' + V('nivel_ingles') : null,
].filter(Boolean);
if (form.length) L.push('Del formulario (ya los tenemos): ' + form.join(' - '));
return [{ json: { estado: L.join('\n'), encontrado: true } }];
"""

AGENT_TEXT = ("=[ESTADO DEL LEAD]\n{{ $('Construir estado lead').first().json.estado }}\n\n"
              "Mensaje del usuario: {{ $('Obtener solo texto').isExecuted ? "
              "$('Obtener solo texto').first().json['Mensaje completo'] : "
              "$('Juntar mensajes').first().json['Mensaje completo'] }}\n\n"
              "Fecha de hoy: {{ $now.setZone('America/Mexico_City').format('EEEE dd \\'of\\' MMMM \\'of\\' yyyy hh:mma') }}")


def main():
    dry = os.environ.get("DRY") == "1"
    m = api("GET", f"/workflows/{MAIN_ID}")
    s = api("GET", f"/workflows/{STG_ID}")
    nodes, conns = m["nodes"], m["connections"]
    by = {n["name"]: n for n in nodes}
    sby = {n["name"]: n for n in s["nodes"]}

    # --- inspección previa ---
    for nm in ("Obtener solo texto", "Juntar mensajes"):
        n = by[nm]
        print(f"[pre] {nm}: {n['type'].split('.')[-1]} · salida→ {[c['node'] for o in conns.get(nm,{}).get('main',[]) for c in o]}")
    print(f"[pre] agent.text usa $json['Mensaje completo']: {'$json' in by[AGENT]['parameters'].get('text','')}")

    # 1. prompt = staging
    stg_prompt = next(n for n in s["nodes"] if n["type"] == "@n8n/n8n-nodes-langchain.agent")["parameters"]["options"]["systemMessage"]
    by[AGENT]["parameters"].setdefault("options", {})["systemMessage"] = stg_prompt

    # 2. crear_contacto → GHL (PUT por contact_id, sin pisar lastName)
    cc = by["crear_contacto"]
    pos = cc["position"]
    nodes.remove(cc)
    nodes.append({
        "parameters": {
            "toolDescription": "Guarda el nombre del lead en el CRM (GHL). Activala apenas el lead te diga su nombre; el apellido solo si lo dijo espontaneamente. Nunca le menciones al lead que hiciste esto.",
            "method": "PUT",
            "url": "=https://services.leadconnectorhq.com/contacts/{{ " + NORM + " }}",
            "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
            "sendHeaders": True, "parametersHeaders": HDRS,
            "sendBody": True, "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify(Object.assign({ firstName: $fromAI('nombre', 'nombre de pila del lead') }, ($fromAI('apellido', 'apellido del lead, vacio si no lo dijo') || '').trim() ? { lastName: $fromAI('apellido', 'apellido del lead, vacio si no lo dijo') } : {})) }}",
        },
        "id": nid(), "name": "crear_contacto", "type": "@n8n/n8n-nodes-langchain.toolHttpRequest",
        "typeVersion": 1.1, "position": pos, "credentials": GHL_CRED,
    })

    # 3. elevar → contact_id determinístico + Mauricio fijo
    ev = by["elevar"]["parameters"]
    ev["workflowInputs"]["value"]["contact_id"] = "={{ " + NORM + " }}"
    ev["workflowInputs"]["value"]["user_id"] = MAURICIO
    ev["description"] = ("Deriva la conversacion a un humano. Activala SOLO cuando el lead pida hablar con una persona, "
                         "tenga una emergencia, o repita el MISMO mensaje 2+ veces consecutivas. Pausa el bot para ese "
                         "contacto, lo asigna a Mauricio (direccion) y avisa al equipo por Telegram.")

    # 4. cerrar_conversacion (portado del staging)
    sc = json.loads(json.dumps(sby["cerrar_conversacion"]))
    sc["id"] = nid()
    sc["parameters"]["url"] = "=https://services.leadconnectorhq.com/contacts/{{ " + NORM + " }}"
    sc["parameters"]["parametersHeaders"] = HDRS
    sc["position"] = [pos[0] + 220, pos[1]]
    if "cerrar_conversacion" not in by:
        nodes.append(sc)
    conns.setdefault("cerrar_conversacion", {})["ai_tool"] = [[{"node": AGENT, "type": "ai_tool", "index": 0}]]
    conns.setdefault("crear_contacto", {})["ai_tool"] = [[{"node": AGENT, "type": "ai_tool", "index": 0}]]

    # 5. estado del lead desde GHL (GET + Construir) entre {Juntar mensajes, Obtener solo texto} y el agente
    ap = by[AGENT]["position"]
    if GET_NODE not in by:
        nodes.append({
            "parameters": {
                "method": "GET", "url": "=https://services.leadconnectorhq.com/contacts/{{ " + NORM + " }}",
                "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
                "sendHeaders": True,
                "headerParameters": {"parameters": [{"name": "Version", "value": "2021-07-28"}]},
                "options": {},
            },
            "id": nid(), "name": GET_NODE, "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
            "position": [ap[0] - 440, ap[1] - 200], "credentials": GHL_CRED,
            "executeOnce": True, "alwaysOutputData": True, "onError": "continueRegularOutput",
        })
        nodes.append({
            "parameters": {"jsCode": ESTADO_JS},
            "id": nid(), "name": EST_NODE, "type": "n8n-nodes-base.code", "typeVersion": 2,
            "position": [ap[0] - 220, ap[1] - 200], "executeOnce": True,
        })
    for src in ("Juntar mensajes", "Obtener solo texto"):
        conns[src]["main"] = [[{"node": GET_NODE, "type": "main", "index": 0}]]
    conns[GET_NODE] = {"main": [[{"node": EST_NODE, "type": "main", "index": 0}]]}
    conns[EST_NODE] = {"main": [[{"node": AGENT, "type": "main", "index": 0}]]}
    by[AGENT]["parameters"]["text"] = AGENT_TEXT

    # --- validación ---
    names = {n["name"] for n in nodes}
    bad = [f"{s_}→{c['node']}" for s_, sp in conns.items() for t in sp.values() for o in t for c in o if c["node"] not in names]
    f = tempfile.NamedTemporaryFile("w", suffix=".js", delete=False); f.write(ESTADO_JS); f.close()
    js_ok = subprocess.run(["node", "--check", f.name], capture_output=True).returncode == 0; os.unlink(f.name)
    tools = sorted(s_ for s_, sp in conns.items() for o in sp.get("ai_tool", []) for c in o if c["node"] == AGENT)
    new_sm = by[AGENT]["parameters"]["options"]["systemMessage"]
    print(f"\n[val] conexiones colgadas: {bad or 'ninguna'} · JS estado node --check: {'OK' if js_ok else 'FALLA'}")
    print(f"[val] tools del agente: {tools}")
    print(f"[val] prompt: {len(new_sm)} chars · Diego={new_sm.lower().count('diego')} · cerrar_conversacion={'cerrar_conversacion' in new_sm}")
    print(f"[val] elevar inputs: {json.dumps(ev['workflowInputs']['value'], ensure_ascii=False)}")
    print(f"[val] agente ← {[s_ for s_, sp in conns.items() for o in sp.get('main', []) for c in o if c['node'] == AGENT]}")
    if bad or not js_ok:
        raise SystemExit("❌ validación falló, no se aplica")
    if dry:
        print("\n[DRY] nada escrito."); return

    os.makedirs(f"{BATCH}/pre", exist_ok=True)
    pre = f"{BATCH}/pre/main-venttur-ghl-pre-paridad.json"
    json.dump(api("GET", f"/workflows/{MAIN_ID}"), open(pre, "w"), indent=2, ensure_ascii=False)
    api("PUT", f"/workflows/{MAIN_ID}", {"name": m["name"], "nodes": nodes, "connections": conns, "settings": m.get("settings", {})})
    post = api("GET", f"/workflows/{MAIN_ID}")
    out = f"{BATCH}/main-venttur-ghl-v0.3-paridad-staging.json"
    json.dump(post, open(out, "w"), indent=2, ensure_ascii=False)
    sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
    print(f"\n✓ aplicado · active={post.get('active')} · nodos={len(post['nodes'])}")
    print(f"  pre : {os.path.basename(pre)} sha={sha(pre)}")
    print(f"  post: {os.path.basename(out)} sha={sha(out)}")


if __name__ == "__main__":
    main()
