#!/usr/bin/env python3
"""
Refactor GHL del main-venttur-ghl (1eS1Z5k898c3ATnf) — OFF, in-place (PUT).

A. Normalize GHL Payload: enriquece con session_key (+521<10>, idéntico a nsk() del rescate),
   whatsapp_phone, id (=contact_id) para compat legacy.
B. 10 refs ManyChat (body.whatsapp_phone/body.id) → $('Normalize GHL Payload').json.{session_key|wa_id|id}.
C. 3 Execute re-points a sub-workflows GHL nuevos con contratos correctos:
   - Estampar estado → W11 qYgeTc9PCq3TiGDn {contactId}
   - Actualizar link → W9 TROsQ5h78baAuVOY {contact_id, phone}
   - Execute Workflow → clasificador Xmyoewwa1W5gm1fy {conversation, contactId} (per-turn + memoria)
D. Bypass Settear variables (ManyChat, dead): reconecta Normalizar burbujas → Enviar WPP + disabled.
E. Clasificador per-turn: nuevo Postgres 'Armar conversación (memoria)' desde Responder rápido ManyChat.
F. Meta CAPI: NO se toca (deferido — su sub-workflow nuevo mf7VQJelfieCDJ5r tiene Trigger desconectado).

Verifica que cada reemplazo string matchee exactamente antes de aplicar.
"""
import json, subprocess, uuid, hashlib
from pathlib import Path

ROOT = Path("/Users/camilo/Downloads/camilo-workspace")
BATCH_DIR = ROOT / "clients/VTR_Venttur/03_workflows/ghl-live-2026-09-22-batch-C2"
MAIN_ID = "1eS1Z5k898c3ATnf"
PG_CRED = {"id": "ihpvM7nYMdLCwWDP", "name": "Venttur"}
NORM = "Normalize GHL Payload"
W11_ID = "qYgeTc9PCq3TiGDn"
W9_ID = "TROsQ5h78baAuVOY"
CLF_ID = "Xmyoewwa1W5gm1fy"


def env_get(k):
    r = subprocess.run(["grep", f"^{k}=", str(ROOT / ".env")], capture_output=True, text=True, check=True)
    return r.stdout.strip().split("\n")[0].split("=", 1)[1].strip().strip('"').strip("'")


def curl_json(method, path, data=None):
    base = env_get("N8N_BASE_URL").rstrip("/"); key = env_get("N8N_API_KEY")
    cmd = ["curl", "-sS", "-w", "\n%{http_code}", "-X", method,
           "-H", f"X-N8N-API-KEY: {key}", "-H", "Content-Type: application/json"]
    if data is not None: cmd.extend(["--data-binary", "@-"])
    cmd.append(f"{base}/api/v1{path}")
    r = subprocess.run(cmd, input=json.dumps(data) if data else None, capture_output=True, text=True)
    parts = r.stdout.rsplit("\n", 1); body = parts[0]; code = parts[1].strip()
    if not (200 <= int(code) < 300):
        raise RuntimeError(f"{method} {path} → {code}: {body[:600]}")
    try: return json.loads(body)
    except: return body


def nid(): return str(uuid.uuid4())


def wfid(wid, name):
    return {"__rl": True, "value": wid, "mode": "list",
            "cachedResultUrl": f"/workflow/{wid}", "cachedResultName": name}


def wf_inputs(fields):  # fields: dict name->expr
    return {
        "mappingMode": "defineBelow",
        "value": dict(fields),
        "matchingColumns": list(fields.keys()),
        "schema": [{"id": k, "displayName": k, "required": False, "defaultMatch": False,
                    "display": True, "canBeUsedToMatch": True, "type": "string", "removed": False}
                   for k in fields],
        "attemptToConvertTypes": False,
        "convertFieldsToString": True,
    }


NORM_CODE = r"""// Adapter GHL Contact Reply → shape GHL-nativo consumido por el resto del workflow.
// Inbound GHL POSTea: { contact_id, phone, message:{body}, contact:{...} } (confirmado por la agencia).
const item = $input.first().json;
const body = item.body || item;

const contact_id = body.contact_id || body.contactId || null;
const phoneRaw = body.phone || (body.contact && body.contact.phone) || null;
const message_body = (body.message && body.message.body) || body.body || body.text || '';
const attribution_url = (body.contact && ((body.contact.lastAttributionSource && body.contact.lastAttributionSource.url) || (body.contact.attributionSource && body.contact.attributionSource.url))) || null;
const date_created = body.dateAdded || body.date_created || body.timestamp || new Date().toISOString();

// nsk() idéntico al del rescate/despachador (Batch F.2 · D5) → sessionKey consistente cross-workflow
function nsk(x){ x=(x||'').toString().replace(/[^0-9]/g,''); if(x.length===12 && x.startsWith('52')) x='521'+x.slice(2); return x; }
const wa = nsk(phoneRaw);
const plus = wa ? ('+' + wa) : null;

return [{ json: {
  contact_id,
  phone: plus,
  message_body,
  attribution_url,
  date_created,
  wa_id: wa || null,
  session_key: plus,          // +521<10> — memoria/rescate/despachador (D5)
  whatsapp_phone: plus,       // compat legacy
  id: contact_id,             // compat legacy (nodos que usaban body.id → ahora contactId GHL)
  whatsapp_name: (body.contact && (body.contact.firstName || body.contact.name)) || '',
  text: message_body,
  payload: { whatsapp_url: attribution_url, referral: (body.contact && body.contact.attributionSource) || null },
  _raw: body,
}}];"""

# --- Reemplazos string exactos (old → new). Se valida que cada old exista una vez. ---
REPL = {
    # sessionKey memoria
    "={{ String($('Responder rápido ManyChat').first().json.body.whatsapp_phone || '').replace(/[^0-9]/g, '') }}":
        "={{ $('Normalize GHL Payload').first().json.session_key }}",
    # crear_contacto
    "={{ $('Responder rápido ManyChat').first().json.body.id }}":
        "={{ $('Normalize GHL Payload').first().json.id }}",
    "={{ $('Responder rápido ManyChat').first().json.body.whatsapp_phone.replace('+','') }}":
        "={{ $('Normalize GHL Payload').first().json.wa_id }}",
    # Crear registro
    "={{ $('Webhook').item.json.body.id }}":
        "={{ $('Normalize GHL Payload').first().json.id }}",
    # Buscar registro
    '={ID} = "{{ $json.body.id }}"':
        '={ID} = "{{ $(\'Normalize GHL Payload\').first().json.id }}"',
    # primer_registro (item variant)
    "={{ $('Responder rápido ManyChat').item.json.body.whatsapp_phone.replace('+','') }}":
        "={{ $('Normalize GHL Payload').first().json.wa_id }}",
    "={{ $('Responder rápido ManyChat').item.json.body.id }}":
        "={{ $('Normalize GHL Payload').first().json.id }}",
    # Crear primer contacto (Webhook variant)
    "={{ $('Webhook').first().json.body.whatsapp_phone.replace('+','') }}":
        "={{ $('Normalize GHL Payload').first().json.wa_id }}",
    "={{ $('Webhook').first().json.body.id }}":
        "={{ $('Normalize GHL Payload').first().json.id }}",
    # Buscar si ya existe
    "={id} = '{{ $('Webhook').first().json.body.whatsapp_phone.replace('+','') }}'":
        "={id} = '{{ $('Normalize GHL Payload').first().json.wa_id }}'",
    # Normalizar burbujas code
    "const subscriberId = $('Webhook').first().json.body.id;":
        "const subscriberId = $('Normalize GHL Payload').first().json.id;",
    # Alerta promesa fantasma text (telefono/id)
    "{{ $('Webhook').first().json.body.whatsapp_phone || $('Webhook').first().json.body.id }}":
        "{{ $('Normalize GHL Payload').first().json.wa_id }}",
    # Alerta: corregir id de main viejo → nuevo
    "workflow/k3aivKSP67S97IHn/executions": "workflow/1eS1Z5k898c3ATnf/executions",
    # Log guardrail queryReplacement
    "$('Webhook').first().json.body.whatsapp_phone || $('Webhook').first().json.body.id,":
        "$('Normalize GHL Payload').first().json.wa_id,",
}


def deep_replace(obj, counts):
    if isinstance(obj, str):
        s = obj
        for old, new in REPL.items():
            if old in s:
                s = s.replace(old, new)
                counts[old] = counts.get(old, 0) + 1
        return s
    if isinstance(obj, dict):
        return {k: deep_replace(v, counts) for k, v in obj.items()}
    if isinstance(obj, list):
        return [deep_replace(v, counts) for v in obj]
    return obj


def main():
    wf = curl_json("GET", f"/workflows/{MAIN_ID}")
    nodes = wf["nodes"]
    conns = wf["connections"]

    def node(nm): return next((n for n in nodes if n["name"] == nm), None)

    # --- A. Reemplazar código de Normalize GHL Payload ---
    node(NORM)["parameters"]["jsCode"] = NORM_CODE

    # --- B. Reemplazos string en el resto ---
    counts = {}
    for n in nodes:
        if n["name"] == NORM:
            continue
        n["parameters"] = deep_replace(n["parameters"], counts)
    missing = [o for o in REPL if o not in counts]
    print("### B · reemplazos aplicados ###")
    for o, c in counts.items():
        print(f"  ✓ x{c}: {o[:55]}...")
    if missing:
        print("  ⚠️ NO encontrados (revisar):")
        for o in missing:
            print(f"     {o[:70]}")

    # --- C. Re-point Execute nodes ---
    est = node("Estampar estado (Contestó)")
    est["parameters"]["workflowId"] = wfid(W11_ID, "Estado lead Contestó (GHL) - Venttur")
    est["parameters"]["workflowInputs"] = wf_inputs({"contactId": "={{ $('Normalize GHL Payload').first().json.contact_id }}"})
    est["parameters"].setdefault("options", {})["waitForSubWorkflow"] = False

    lnk = node("Actualizar link")
    lnk["parameters"]["workflowId"] = wfid(W9_ID, "W9 · Actualizar link_enviado (GHL) - Venttur")
    lnk["parameters"]["workflowInputs"] = wf_inputs({
        "contact_id": "={{ $('Normalize GHL Payload').first().json.contact_id }}",
        "phone": "={{ $('Normalize GHL Payload').first().json.phone }}",
    })

    # --- E. Nodo Armar conversación (memoria) + re-point Execute Workflow → clasificador ---
    armar = {
        "parameters": {
            "operation": "executeQuery",
            "query": ("SELECT COALESCE(string_agg("
                      "CASE WHEN message->>'type'='human' THEN 'Usuario: ' "
                      "WHEN message->>'type'='ai' THEN 'Asistente: ' ELSE '' END "
                      "|| COALESCE(message->'data'->>'content',''), E'\\n' ORDER BY id), '') AS conversation "
                      "FROM n8n_chat_histories WHERE session_id = $1"),
            "options": {"queryReplacement": "={{ $('Normalize GHL Payload').first().json.session_key }}"},
        },
        "id": nid(), "name": "Armar conversación (memoria)", "type": "n8n-nodes-base.postgres",
        "typeVersion": 2.5, "position": [1180, 560],
        "credentials": {"postgres": PG_CRED},
        "onError": "continueRegularOutput",
    }
    nodes.append(armar)

    clf = node("Execute Workflow")
    clf["name"] = "Clasificar postconv (GHL)"
    clf["parameters"]["workflowId"] = wfid(CLF_ID, "vtr-clasificador-postconv-v1")
    clf["parameters"]["workflowInputs"] = wf_inputs({
        "conversation": "={{ ($('Armar conversación (memoria)').first().json.conversation || '') + '\\nUsuario: ' + $('Normalize GHL Payload').first().json.text }}",
        "contactId": "={{ $('Normalize GHL Payload').first().json.contact_id }}",
    })
    clf["parameters"].setdefault("options", {})["waitForSubWorkflow"] = False

    # --- D. Bypass Settear variables (reconectar Normalizar burbujas → Enviar WPP + disabled) ---
    node("Settear variables")["disabled"] = True

    # ============ CONNECTIONS ============
    def set_main(src, targets, idx=0):
        conns.setdefault(src, {}).setdefault("main", [])
        while len(conns[src]["main"]) <= idx:
            conns[src]["main"].append([])
        conns[src]["main"][idx] = [{"node": t, "type": "main", "index": 0} for t in targets]

    def append_main(src, target, idx=0):
        conns.setdefault(src, {}).setdefault("main", [])
        while len(conns[src]["main"]) <= idx:
            conns[src]["main"].append([])
        conns[src]["main"][idx].append({"node": target, "type": "main", "index": 0})

    # D: Normalizar burbujas → Enviar WPP (bypass Settear variables); dejar Settear variables sin salida
    set_main("Normalizar burbujas", ["Enviar WPP"])
    conns.pop("Settear variables", None)

    # E: sacar Execute Workflow (ahora clasificador) de la cadena de conversación
    #    Crear primer contacto → Separamos en partes (antes iba a Execute Workflow)
    set_main("Crear primer contacto", ["Separamos en partes"])
    #    Execute Workflow ya no va a Separamos en partes
    conns.pop("Clasificar postconv (GHL)", None)
    conns.pop("Execute Workflow", None)
    #    Responder rápido ManyChat → + Armar conversación (rama nueva)
    append_main("Responder rápido ManyChat", "Armar conversación (memoria)")
    #    Armar conversación → Clasificar postconv
    set_main("Armar conversación (memoria)", ["Clasificar postconv (GHL)"])

    # --- VALIDACIÓN pre-PUT ---
    import os, tempfile
    print("\n### VALIDACIÓN ###")
    # 1. JS de Normalize + Armar (sql no, es SQL) — node --check del Normalize
    f = tempfile.NamedTemporaryFile("w", suffix=".js", delete=False); f.write(NORM_CODE); f.close()
    r = subprocess.run(["node", "--check", f.name], capture_output=True, text=True); os.unlink(f.name)
    print(f"  Normalize node --check: {'OK' if r.returncode==0 else 'FALLA '+r.stderr[:150]}")
    # 2. Conexiones: todos los targets existen
    names = {n["name"] for n in nodes}
    bad = []
    for src, sp in conns.items():
        if src not in names: bad.append(f"src '{src}' no existe")
        for outs in sp.get("main", []):
            for c in outs:
                if c["node"] not in names: bad.append(f"target '{c['node']}' no existe (de {src})")
    print(f"  conexiones coherentes: {'OK' if not bad else 'FALLA: '+'; '.join(bad[:5])}")
    # 3. Settear variables sin salida + disabled
    sv = node("Settear variables")
    print(f"  Settear variables: disabled={sv.get('disabled')} · sin conexiones salientes={'Settear variables' not in conns}")
    # 4. Normalizar burbujas → Enviar WPP directo
    nb_tgt = [c["node"] for o in conns.get("Normalizar burbujas", {}).get("main", []) for c in o]
    print(f"  Normalizar burbujas → {nb_tgt} (esperado: Enviar WPP)")
    # 5. Clasificador wiring
    rr_tgt = [c["node"] for o in conns.get("Responder rápido ManyChat", {}).get("main", []) for c in o]
    ac_tgt = [c["node"] for o in conns.get("Armar conversación (memoria)", {}).get("main", []) for c in o]
    cpc_tgt = [c["node"] for o in conns.get("Crear primer contacto", {}).get("main", []) for c in o]
    print(f"  Responder rápido → {rr_tgt}")
    print(f"  Armar conversación → {ac_tgt}")
    print(f"  Crear primer contacto → {cpc_tgt} (esperado: Separamos en partes)")
    # 6. No quedan refs ManyChat sin intención
    leftover = []
    for n in nodes:
        if n["name"] in (NORM,): continue
        txt = json.dumps(n.get("parameters", {}), ensure_ascii=False)
        for tok in ["body.whatsapp_phone", "body.id", "id_manychat", ".body.whatsapp"]:
            if tok in txt:
                leftover.append(f"{n['name']}:{tok}")
    print(f"  refs ManyChat remanentes: {leftover if leftover else 'ninguna ✓'}")

    if os.environ.get("DRY") == "1":
        print("\n[DRY] no se hace PUT. Snapshot en memoria validado.")
        return

    # PUT
    put_body = {"name": wf["name"], "nodes": nodes, "connections": conns, "settings": wf.get("settings", {})}
    curl_json("PUT", f"/workflows/{MAIN_ID}", data=put_body)

    final = curl_json("GET", f"/workflows/{MAIN_ID}")
    path = BATCH_DIR / "main-venttur-ghl-v0.2-refactor.json"
    json.dump(final, open(path, "w"), indent=2, ensure_ascii=False)
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
    print(f"\n✓ main refactorizado · nodos={len(final['nodes'])} active={final.get('active')}")
    print(f"  snapshot: {path.name} · sha256={sha}")


if __name__ == "__main__":
    main()
