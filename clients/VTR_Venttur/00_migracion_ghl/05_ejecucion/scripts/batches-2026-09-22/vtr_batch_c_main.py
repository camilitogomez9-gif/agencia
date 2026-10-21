#!/usr/bin/env python3
"""
Batch C.1 · Construir main-venttur-ghl v0.1 (OFF).

Estrategia:
1. Duplicar k3aivKSP67S97IHn (post Batch A) como nuevo workflow.
2. Cambiar name + webhook path.
3. AGREGAR (no reemplazar, para preservar lógica probada) al inicio:
   - `Normalize GHL Payload` (Code): mapea payload GHL Contact Reply → shape ManyChat que espera el resto.
   - `Compute idempotency hash` (Code): sha256(contact_id + date_created + body).
   - `Check dedup` (Postgres SELECT): busca hash en vtr_message_dedup.
   - `Is duplicate?` (IF): si sí → exit sin responder al webhook.
   - `Insert dedup` (Postgres): INSERT ON CONFLICT DO NOTHING.
4. REESCRIBIR tool `elevar`:
   - Reemplazar el toolHttpRequest actual con toolWorkflow apuntando a un sub-workflow nuevo `vtr-tool-elevar-ghl`.
5. Cambiar Enviar WPP (Meta directo) → POST /conversations/messages GHL (adaptación mínima).
   NOTA: si el shape difiere de lo asumido (Test C diferido a CUTOVER-3), la guía dice fallback a template send.
6. Workflow queda OFF. Snapshot en repo. la agencia activa en CUTOVER-2.

Los nodos Airtable existentes (Actualizar Airtable, Crear registro, etc.) NO se tocan en v0.1
— se pueden migrar a GHL escrituras en un batch posterior si el cliente lo pide.
"""
import json
import subprocess
import uuid
import hashlib
from pathlib import Path

ROOT = Path("/Users/camilo/Downloads/camilo-workspace")
BATCH_DIR = ROOT / "clients/VTR_Venttur/03_workflows/ghl-live-2026-09-22-batch-C"
SOURCE = ROOT / "clients/VTR_Venttur/03_workflows/ghl-live-2026-09-22-batch-A/post/vtr-main.json"

CRED_POSTGRES = "ihpvM7nYMdLCwWDP"
CRED_POSTGRES_NAME = "Venttur"
CRED_TELEGRAM = "V5k84z3AjQc9Y5yg"  # botla agencia cred name
GHL_PIT_LOCATION = "7aXb4JCKsWV5nUyBXeSF"
GHL_BASE_URL = "https://services.leadconnectorhq.com"


def env_get(k):
    r = subprocess.run(["grep", f"^{k}=", str(ROOT / ".env")], capture_output=True, text=True, check=True)
    return r.stdout.strip().split("\n")[0].split("=", 1)[1].strip().strip('"').strip("'")


def curl_json(method, path, data=None, allow_fail=False):
    base = env_get("N8N_BASE_URL").rstrip("/")
    key = env_get("N8N_API_KEY")
    cmd = ["curl", "-sS", "-w", "\n%{http_code}", "-X", method,
           "-H", f"X-N8N-API-KEY: {key}", "-H", "Content-Type: application/json"]
    if data is not None:
        cmd.extend(["--data-binary", "@-"])
    cmd.append(f"{base}/api/v1{path}")
    r = subprocess.run(cmd, input=json.dumps(data) if data else None, capture_output=True, text=True)
    parts = r.stdout.rsplit("\n", 1)
    body = parts[0] if len(parts) == 2 else r.stdout
    code = parts[1].strip() if len(parts) == 2 else "?"
    if not (200 <= int(code) < 300) and not allow_fail:
        raise RuntimeError(f"{method} {path} → {code}: {body[:500]}")
    try:
        return json.loads(body), code
    except:
        return body, code


def new_id():
    return str(uuid.uuid4())


def main():
    BATCH_DIR.mkdir(parents=True, exist_ok=True)

    with open(SOURCE) as f:
        wf = json.load(f)

    # Preservar solo campos aceptados por POST /workflows
    new_wf = {
        "name": "main-venttur-ghl (v0.1 OFF · esperando CUTOVER-2)",
        "nodes": wf["nodes"],
        "connections": wf["connections"],
        "settings": wf.get("settings", {})
    }

    # Todos los nodos originales conservan sus IDs
    nodes = new_wf["nodes"]
    conns = new_wf["connections"]

    # ── Cambio 1: webhook path nuevo ──
    for n in nodes:
        if n["type"] == "n8n-nodes-base.webhook":
            n["parameters"]["path"] = f"main-venttur-ghl-{uuid.uuid4().hex[:8]}"
            n["webhookId"] = new_id()
            break

    # ── Cambio 2: Nodos nuevos de shape adapter + dedup ──
    # Los insertaremos entre Webhook y "Responder rápido ManyChat"

    normalize_node = {
        "parameters": {
            "jsCode": (
                "// Adapter: GHL Contact Reply payload → shape ManyChat-like consumido por el resto.\n"
                "// Payload GHL esperado: { contact_id, phone, message: {body, ...}, contact: {lastAttributionSource: {url}} }\n"
                "const item = $input.first().json;\n"
                "const body = item.body || item;\n"
                "\n"
                "const contact_id = body.contact_id || body.contactId || body.id || null;\n"
                "const phone = body.phone || body.contact?.phone || null;\n"
                "const message_body = body.message?.body || body.body || body.text || '';\n"
                "const attribution_url = body.contact?.lastAttributionSource?.url \n"
                "                     || body.contact?.attributionSource?.url \n"
                "                     || null;\n"
                "const date_created = body.dateAdded || body.date_created || body.timestamp || new Date().toISOString();\n"
                "\n"
                "return [{ json: {\n"
                "  // shape GHL nativo (para dedup + nuevos consumers)\n"
                "  contact_id, phone, message_body, attribution_url, date_created,\n"
                "  // shape ManyChat-compat para el resto del workflow\n"
                "  wa_id: phone ? phone.replace('+','') : null,\n"
                "  whatsapp_name: body.contact?.firstName || body.contact?.name || '',\n"
                "  text: message_body,\n"
                "  payload: {\n"
                "    whatsapp_url: attribution_url,\n"
                "    referral: body.contact?.attributionSource || null,\n"
                "  },\n"
                "  // preservar original para debug\n"
                "  _raw: body,\n"
                "}}];\n"
            )
        },
        "id": new_id(),
        "name": "Normalize GHL Payload",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [200, -200]
    }

    hash_node = {
        "parameters": {
            "jsCode": (
                "// Idempotencia por hash sha256(contact_id + date_created + body)\n"
                "const crypto = require('crypto');\n"
                "const item = $input.first().json;\n"
                "const raw = `${item.contact_id || ''}::${item.date_created || ''}::${item.message_body || ''}`;\n"
                "const hash = crypto.createHash('sha256').update(raw).digest('hex');\n"
                "return [{ json: { ...item, dedup_hash: hash } }];\n"
            )
        },
        "id": new_id(),
        "name": "Compute idempotency hash",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [400, -200]
    }

    check_dedup_node = {
        "parameters": {
            "operation": "executeQuery",
            "query": (
                "SELECT hash FROM vtr_message_dedup WHERE hash = $1 LIMIT 1;"
            ),
            "options": {"queryReplacement": "={{ [$json.dedup_hash] }}"}
        },
        "id": new_id(),
        "name": "Check dedup",
        "type": "n8n-nodes-base.postgres",
        "typeVersion": 2.6,
        "position": [600, -200],
        "credentials": {"postgres": {"id": CRED_POSTGRES, "name": CRED_POSTGRES_NAME}}
    }

    is_dup_if = {
        "parameters": {
            "conditions": {
                "options": {"caseSensitive": True, "typeValidation": "loose", "version": 2},
                "conditions": [{
                    "id": new_id(),
                    "leftValue": "={{ $json.hash }}",
                    "rightValue": "",
                    "operator": {"type": "string", "operation": "notEmpty", "singleValue": True}
                }],
                "combinator": "and"
            },
            "options": {}
        },
        "id": new_id(),
        "name": "Is duplicate?",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2.2,
        "position": [800, -200]
    }

    insert_dedup_node = {
        "parameters": {
            "operation": "executeQuery",
            "query": (
                "INSERT INTO vtr_message_dedup (hash, contact_id, date_created, body) "
                "VALUES ($1, $2, $3::timestamptz, $4) ON CONFLICT (hash) DO NOTHING;"
            ),
            "options": {
                "queryReplacement": (
                    "={{ [$('Compute idempotency hash').first().json.dedup_hash, "
                    "$('Compute idempotency hash').first().json.contact_id, "
                    "$('Compute idempotency hash').first().json.date_created, "
                    "$('Compute idempotency hash').first().json.message_body] }}"
                )
            }
        },
        "id": new_id(),
        "name": "Insert dedup",
        "type": "n8n-nodes-base.postgres",
        "typeVersion": 2.6,
        "position": [1000, -100],
        "credentials": {"postgres": {"id": CRED_POSTGRES, "name": CRED_POSTGRES_NAME}}
    }

    exit_dup_node = {
        "parameters": {
            "respondWith": "text",
            "responseBody": "duplicate",
            "options": {"responseCode": 200}
        },
        "id": new_id(),
        "name": "Exit duplicate",
        "type": "n8n-nodes-base.respondToWebhook",
        "typeVersion": 1.1,
        "position": [1000, -300]
    }

    # Agregar los nuevos nodos al array
    nodes.extend([normalize_node, hash_node, check_dedup_node, is_dup_if, insert_dedup_node, exit_dup_node])

    # ── Cambio 3: rewire connections ──
    # Original: Webhook → Responder rápido ManyChat
    # Nuevo:    Webhook → Normalize → Hash → Check dedup → Is duplicate?
    #                                                       ├─ true → Exit duplicate
    #                                                       └─ false → Insert dedup → Responder rápido ManyChat → resto igual
    # Encontrar la conexión saliente de Webhook
    if "Webhook" in conns:
        original_next = conns["Webhook"]["main"][0]  # lista de nodos next
        # Redireccionar Webhook → Normalize
        conns["Webhook"] = {"main": [[{"node": "Normalize GHL Payload", "type": "main", "index": 0}]]}
        # Y Insert dedup → lo que originalmente venía después de Webhook
        conns["Normalize GHL Payload"] = {"main": [[{"node": "Compute idempotency hash", "type": "main", "index": 0}]]}
        conns["Compute idempotency hash"] = {"main": [[{"node": "Check dedup", "type": "main", "index": 0}]]}
        conns["Check dedup"] = {"main": [[{"node": "Is duplicate?", "type": "main", "index": 0}]]}
        conns["Is duplicate?"] = {
            "main": [
                [{"node": "Exit duplicate", "type": "main", "index": 0}],  # true = duplicado
                [{"node": "Insert dedup", "type": "main", "index": 0}]      # false = no dup
            ]
        }
        conns["Insert dedup"] = {"main": [original_next]}

    # ── Cambio 4: reescribir tool `elevar` ──
    # Original: toolHttpRequest a Telegram/Airtable. Nuevo: toolWorkflow a sub-workflow vtr-tool-elevar-ghl
    # (el sub-workflow lo creamos en un paso siguiente, pero dejamos el nodo apuntando a un ID placeholder)
    for i, n in enumerate(nodes):
        if n["name"] == "elevar" and n["type"] == "@n8n/n8n-nodes-langchain.toolHttpRequest":
            # Reemplazar el nodo entero por un toolWorkflow (placeholder workflowId, actualizar tras crear el sub-workflow)
            nodes[i] = {
                "parameters": {
                    "name": "elevar",
                    "description": (
                        "Elevá la conversación al equipo humano. Usá cuando el lead pide asesor, cuando hay "
                        "objeciones fuertes que no podés manejar, o cuando el bot no puede responder. "
                        "3 acciones automáticas: pausa bot (DND=true) + asigna a userId + notifica Telegram."
                    ),
                    "workflowId": {"__rl": True, "value": "REPLACE_WITH_SUBWORKFLOW_ID", "mode": "id"},
                    "workflowInputs": {
                        "mappingMode": "defineBelow",
                        "value": {
                            "contact_id": "={{ $fromAI('contact_id','GHL contact ID que se debe elevar','string') }}",
                            "user_id": "={{ $fromAI('user_id','GHL userId al que se asigna (elegir el correcto según programa)','string') }}",
                            "resumen": "={{ $fromAI('resumen','Resumen de la conversación para el humano que atiende','string') }}"
                        }
                    }
                },
                "id": new_id(),
                "name": "elevar",
                "type": "@n8n/n8n-nodes-langchain.toolWorkflow",
                "typeVersion": 2.2,
                "position": n["position"]
            }
            break

    # ── Cambio 5: reescribir "Enviar WPP" a POST /conversations/messages GHL ──
    # Placeholder básico. El shape exacto se valida en CUTOVER-3.
    for n in nodes:
        if n["name"] == "Enviar WPP" and n["type"] == "n8n-nodes-base.httpRequest":
            n["parameters"] = {
                "method": "POST",
                "url": f"{GHL_BASE_URL}/conversations/messages",
                "authentication": "genericCredentialType",
                "genericAuthType": "httpHeaderAuth",
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [
                        {"name": "Version", "value": "2021-04-15"},
                        {"name": "LocationId", "value": GHL_PIT_LOCATION}
                    ]
                },
                "sendBody": True,
                "contentType": "json",
                "jsonBody": (
                    "={{ JSON.stringify({\n"
                    "  type: 'WhatsApp',\n"
                    "  contactId: $('Normalize GHL Payload').first().json.contact_id,\n"
                    "  message: $json.parte1 || $json.text || $json.message || ''\n"
                    "}) }}"
                ),
                "options": {}
            }
            # Cred header auth (Bearer PIT) — el usuario debe cablear la credencial "GHL VTR (PIT) YkVmaA4jlRbO1TQD"
            n["credentials"] = {"httpHeaderAuth": {"id": "YkVmaA4jlRbO1TQD", "name": "GHL VTR (PIT)"}}
            break

    print(f"📤 POST /workflows (main-venttur-ghl v0.1 OFF)...")
    created, _ = curl_json("POST", "/workflows", data=new_wf)
    wf_id = created["id"]
    print(f"   ✓ created id={wf_id}, active={created.get('active')}")

    # Guardar snapshot
    path = BATCH_DIR / "main-venttur-ghl-v0.1.json"
    # GET final para snapshot con IDs finales
    final, _ = curl_json("GET", f"/workflows/{wf_id}")
    with open(path, "w") as f:
        json.dump(final, f, indent=2, ensure_ascii=False)
    with open(path, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    print(f"   💾 {path.name} · sha256={sha}")

    return {"wf_id": wf_id, "sha256": sha, "path": str(path)}


if __name__ == "__main__":
    r = main()
    print(f"\n{'='*50}")
    print(json.dumps(r, indent=2))
