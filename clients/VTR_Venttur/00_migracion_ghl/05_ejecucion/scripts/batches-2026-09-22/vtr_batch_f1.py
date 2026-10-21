#!/usr/bin/env python3
"""
Batch F.1 · Cablear templateId por programa en el despachador vrShEXQGGAo4FqAt.

Cambios:
1. Nodo `Seleccionar (tope-2 + prioridad)`:
   - Agregar constante PROGRAMA_FIELD = 'xK2NFqtz1DYUw3gYdn8I' (custom field id de programa_interes en GHL)
   - Agregar mapping TEMPLATE_BY_PROGRAMA con los 6 IDs que pasó la agencia
   - En mk(), leer programa del contact y resolver templateId
   - Skip lead si no matchea (templateId = null → downstream IF salta)

2. Nodo `Enviar template GHL (PLACEHOLDER)`:
   - Rename a `Enviar template GHL`
   - Body: templateId hardcoded → {{ $json.templateId }}
   - jsonBody usa expresión

3. Nodo IF nuevo `Tiene templateId?` entre Seleccionar y Enviar template:
   - Rama true → Enviar template
   - Rama false → skip (loguear que se skippeó)

templateIds (por la agencia):
  - Pathway              = 6aa1b033a3ed42683a182e66
  - Boarding School      = 6aa1b033c99a8adae9721464
  - AA Familia           = 6aa1b0323e3fe07bce43d4ab
  - Estudio y Trabajo    = 6aa1b032a3ed42683a182e5c
  - Summer Camp          = 6aa1b03145d5045847ef9762
  - Hapy Year (Gap Year) = 6aa1b0309686d7ff49f76c20
"""
import json, subprocess, uuid, hashlib
from pathlib import Path

ROOT = Path("/Users/camilo/Downloads/camilo-workspace")
BATCH_DIR = ROOT / "clients/VTR_Venttur/03_workflows/ghl-live-2026-09-22-batch-F"
POST_DIR = BATCH_DIR / "post"
POST_DIR.mkdir(parents=True, exist_ok=True)
WF_ID = "vrShEXQGGAo4FqAt"


def env_get(k):
    r = subprocess.run(["grep", f"^{k}=", str(ROOT / ".env")], capture_output=True, text=True, check=True)
    return r.stdout.strip().split("\n")[0].split("=", 1)[1].strip().strip('"').strip("'")


def curl_json(method, path, data=None):
    key = env_get("N8N_API_KEY"); base = env_get("N8N_BASE_URL").rstrip("/")
    cmd = ["curl", "-sSf", "-X", method, "-H", f"X-N8N-API-KEY: {key}",
           "-H", "Content-Type: application/json"]
    if data is not None: cmd.extend(["--data-binary", "@-"])
    cmd.append(f"{base}/api/v1{path}")
    r = subprocess.run(cmd, input=json.dumps(data) if data else None,
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


# ── PATCH 1: nuevo jsCode para Seleccionar con mapping template ──
NEW_JSCODE = r"""// Motor de selección COMPLETO — TOPE-2 (validado vs GHL real 2026-09-07) · outreach lane + fixes 2026-09-21 · templateId cableado 2026-09-22
const T='ez934lu03v7nC4ZRS7LJ', E='Omg1BvHmpXR0MMGsrpFh', L='rHzGNiesWuESPmSZyviJ', UAF='jrdfZCF6VWAA3L7WDVdB', TOUCH1='95bG6wvWFk2ma17T4NuE';
const PROGRAMA_FIELD = 'xK2NFqtz1DYUw3gYdn8I';  // custom field programa_interes en GHL
const BOOKED_STAGE_IDS = ["36fa419c-e836-48a8-8a77-72b38d357173", "7c0c40b6-4a25-4d1c-a2a2-40e5f38095bc", "08f742d9-2aaa-4a76-abc2-48d34a9f3ba9"];
const RECENCIA_DIAS = 30;              // ⚠ null en históricos → no filtra (política §8 recontacto pendiente)
const TERMINAL = ['Cita confirmada', 'Cerrada'];   // + Cerrada (2026-09-21): no re-tocar leads cerrados

// Template IDs por programa (Camilo · 2026-09-22 · §PAR-B cerrado)
// ⚠ Programas huérfanos (Viajes educativos, Educación superior, Cursos idiomas) NO tienen template → skip
const TEMPLATE_BY_PROGRAMA = {
  'boarding':      '6aa1b033c99a8adae9721464',
  'boarding_ia':   '6aa1b033c99a8adae9721464',
  'boarding school':'6aa1b033c99a8adae9721464',
  'internados':    '6aa1b033c99a8adae9721464',
  'internado':     '6aa1b033c99a8adae9721464',
  'aa':            '6aa1b0323e3fe07bce43d4ab',
  'aa familia':    '6aa1b0323e3fe07bce43d4ab',
  'aa familiar':   '6aa1b0323e3fe07bce43d4ab',
  'aa familiar ia':'6aa1b0323e3fe07bce43d4ab',
  'intercambio':   '6aa1b0323e3fe07bce43d4ab',
  'intercambio académico':'6aa1b0323e3fe07bce43d4ab',
  'intercambio academico':'6aa1b0323e3fe07bce43d4ab',
  'summer':        '6aa1b03145d5045847ef9762',
  'summer camp':   '6aa1b03145d5045847ef9762',
  'summer camp ia':'6aa1b03145d5045847ef9762',
  'campamento':    '6aa1b03145d5045847ef9762',
  'campamentos':   '6aa1b03145d5045847ef9762',
  'campamentos de verano':'6aa1b03145d5045847ef9762',
  'pathway':       '6aa1b033a3ed42683a182e66',
  'pathway ia':    '6aa1b033a3ed42683a182e66',
  'pathway alemania':'6aa1b033a3ed42683a182e66',
  'estudio y trabajo':'6aa1b032a3ed42683a182e5c',
  'estudia y trabaja':'6aa1b032a3ed42683a182e5c',
  'gap year':      '6aa1b0309686d7ff49f76c20',
  'gap year ia':   '6aa1b0309686d7ff49f76c20',
  'gap year / estudia y trabaja':'6aa1b0309686d7ff49f76c20',
  'hapy year':     '6aa1b0309686d7ff49f76c20',  // la agencia typo, asumo Gap Year
  'happy year':    '6aa1b0309686d7ff49f76c20',
};

function resolveTemplate(programa) {
  if (!programa) return null;
  const key = String(programa).toLowerCase().trim();
  return TEMPLATE_BY_PROGRAMA[key] || null;
}

// sessionKey canónico = misma derivación que el rescate GHL (nsk) · con '+' desde Batch F.2 (2026-09-22)
function nsk(x){ x=(x||'').toString().replace(/[^0-9]/g,''); if(x.length===12 && x.startsWith('52')) x='521'+x.slice(2); return x; }
const flat = (n, key) => { try { return $(n).all().flatMap(i => (i.json && i.json[key]) || []); } catch(e){ return []; } };
const cfv = (c, id) => { for (const x of (c.customFields||[])) if (x.id===id) return x.value; return null; };
const truthy = v => v===true||v==='true'||(Array.isArray(v)&&v.includes('true'));
const now = Date.now();
const bookedOpps = flat('Query booked (OP·Bot)', 'opportunities');
const booked = new Set(bookedOpps.filter(o => BOOKED_STAGE_IDS.includes(o.pipelineStageId)).map(o => o.contactId));
const gate = (c) => {
  if (booked.has(c.id)) return false;
  let toq = cfv(c, T); toq = (toq===null||toq===''||(Array.isArray(toq)&&!toq.length))?0:Number(toq);
  if (toq >= 2) return false;                       // TOPE GLOBAL 2 (outreach+rescate+nurturing)
  const est = (cfv(c, E)||'').toString().trim();
  if (TERMINAL.includes(est)) return false;
  const ua = cfv(c, UAF); const t = ua ? Date.parse(ua) : null;
  if (t && (now - t) > RECENCIA_DIAS*864e5) return false;
  return true;
};
const mk = (c, lane) => {
  const programa = cfv(c, PROGRAMA_FIELD);
  const templateId = resolveTemplate(programa);
  return {
    contactId: c.id,
    phone: c.phone,
    session_key: '+' + nsk(c.phone),
    firstName: c.firstName,
    programa: programa || '',
    templateId,
    lane,
    toques_actual: Number(cfv(c,T))||0
  };
};
const sel = new Map();
// prioridad 1: rescate (link_enviado=true, sin cita)
for (const c of flat('Query rescate','contacts')) { if (gate(c)) sel.set(c.id, mk(c,'rescate')); }
// prioridad 2: nurturing (estado activo, SIN link — los con link ya están en rescate)
for (const c of flat('Query nurturing','contacts')) { if (sel.has(c.id)) continue; if (truthy(cfv(c,L))) continue; if (gate(c)) sel.set(c.id, mk(c,'nurturing')); }
// prioridad 3: outreach Form Meta (Decisión B — consolida el carril de toques de W10; sólo si touch1 ya venció)
for (const c of flat('Query outreach (Form Meta)','contacts')) {
  if (sel.has(c.id)) continue;
  if (truthy(cfv(c,L))) continue;
  const t1 = cfv(c, TOUCH1); const due = t1 ? (Date.parse(t1) <= now) : true;
  if (due && gate(c)) sel.set(c.id, mk(c,'outreach'));
}
return [...sel.values()].map(json => ({ json }));  // 1 item/contacto; 1 msg/contacto/run"""


def new_id():
    return str(uuid.uuid4())


def main():
    print(f"📥 GET despachador {WF_ID}...")
    wf = curl_json("GET", f"/workflows/{WF_ID}")
    nodes = wf["nodes"]
    conns = wf["connections"]

    # Patch 1: Seleccionar (tope-2 + prioridad) — nuevo jsCode con mapping template
    sel_node = next((n for n in nodes if n["name"] == "Seleccionar (tope-2 + prioridad)"), None)
    assert sel_node, "Seleccionar node no encontrado"
    sel_node["parameters"]["jsCode"] = NEW_JSCODE
    print(f"  ✓ patched Seleccionar (tope-2 + prioridad) con mapping TEMPLATE_BY_PROGRAMA")

    # Patch 2: Enviar template GHL — usar $json.templateId
    enviar_node = next((n for n in nodes if n["name"].startswith("Enviar template GHL")), None)
    assert enviar_node, "Enviar template GHL node no encontrado"
    old_name = enviar_node["name"]
    enviar_node["name"] = "Enviar template GHL"
    enviar_node["parameters"]["jsonBody"] = (
        "={{ JSON.stringify({"
        " type: 'WhatsApp',"
        " contactId: $json.contactId,"
        " templateId: $json.templateId"
        "}) }}"
    )
    # Asegurar specifyBody = json
    enviar_node["parameters"]["specifyBody"] = "json"
    print(f"  ✓ patched '{old_name}' → 'Enviar template GHL' (body con $json.templateId)")

    # Patch 3: agregar IF gate `Tiene templateId?` entre Seleccionar y Enviar template
    # Si ya existe (idempotente), skip
    if not any(n["name"] == "Tiene templateId?" for n in nodes):
        if_node = {
            "parameters": {
                "conditions": {
                    "options": {"caseSensitive": True, "typeValidation": "loose", "version": 2},
                    "conditions": [{
                        "id": "has-template-2026-09-22",
                        "leftValue": "={{ $json.templateId }}",
                        "rightValue": "",
                        "operator": {"type": "string", "operation": "notEmpty", "singleValue": True}
                    }],
                    "combinator": "and"
                },
                "options": {}
            },
            "id": new_id(),
            "name": "Tiene templateId?",
            "type": "n8n-nodes-base.if",
            "typeVersion": 2.2,
            "position": [sel_node["position"][0] + 200, sel_node["position"][1]]
        }
        nodes.append(if_node)
        print(f"  ✓ agregado IF 'Tiene templateId?' entre Seleccionar y Enviar template")

    # Rewire: Seleccionar → Tiene templateId? → (true) Enviar template GHL → resto igual
    #                                        → (false) skip (nada)
    # Guardar la conexión saliente actual de Seleccionar
    old_next = None
    if "Seleccionar (tope-2 + prioridad)" in conns:
        old_next = conns["Seleccionar (tope-2 + prioridad)"]["main"][0]

    conns["Seleccionar (tope-2 + prioridad)"] = {
        "main": [[{"node": "Tiene templateId?", "type": "main", "index": 0}]]
    }
    # IF: rama true (index 0) = Enviar template GHL / rama false (index 1) = vacío
    # Restauro la conexión original (que iba a "Enviar template GHL (PLACEHOLDER)") como rama true
    # Fix: la conn original apuntaba al nodo con nombre viejo. Ahora se llama "Enviar template GHL", igual funciona por nombre
    if old_next:
        # Actualizar el node target al nuevo nombre
        for item in old_next:
            if item.get("node") == "Enviar template GHL (PLACEHOLDER)":
                item["node"] = "Enviar template GHL"
        conns["Tiene templateId?"] = {"main": [old_next, []]}
    else:
        conns["Tiene templateId?"] = {"main": [[{"node": "Enviar template GHL", "type": "main", "index": 0}], []]}

    # Actualizar cualquier otra referencia al nombre viejo
    for src, spec in list(conns.items()):
        for branch in spec.get("main", []):
            for item in branch:
                if item.get("node") == "Enviar template GHL (PLACEHOLDER)":
                    item["node"] = "Enviar template GHL"

    put_body = {"name": wf["name"], "nodes": nodes,
                "connections": conns, "settings": wf.get("settings", {})}
    print(f"📤 PUT /workflows/{WF_ID}...")
    curl_json("PUT", f"/workflows/{WF_ID}", data=put_body)
    print(f"   ✓ patched")

    # Snapshot post
    final = curl_json("GET", f"/workflows/{WF_ID}")
    path = POST_DIR / "despachador.json"
    with open(path, "w") as f:
        json.dump(final, f, indent=2, ensure_ascii=False)
    with open(path, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    print(f"   💾 {path.name} · sha256={sha}")


if __name__ == "__main__":
    main()
