#!/usr/bin/env python3
"""
HPF · L7 — Genera W4 (CALCULADORA) y W5 (ATENCION_PERSONALIZADA).

W4 · CALCULADORA — port de `OPiuPFwRmq6QgACL`. El `Code2` se copia BYTE-EXACTO del
grafo congelado: son los pesos, los límites de empaque, los tramos de costo y los
mínimos de compra. Tocar ahí es tocar plata del cliente.

  DELTA deliberado: el `Edit Fields1` del origen expone un solo campo,
  `resumen_cajas`. Cuando `Code2` rechaza por mínimo devuelve
  `{error, detalle_violaciones, message_to_agent}` — sin `resumen_cajas` — así que el
  agente recibía vacío y NUNCA veía por qué se rechazó. La validación cortaba el
  cálculo pero no comunicaba nada. W4 devuelve el objeto completo.

W5 · ATENCION_PERSONALIZADA — port de `SUgT7UPYyQ3NDgRp` (3 nodos):
  Telegram al grupo + PATCH del lead a la etapa de atención personalizada.
  En GHL eso es `update_stage` a "En Espera" + el tag `atencion_humana`.

Salida: clients/HPF_HappyFlops/03_workflows/ghl/W4-calculadora.json  y  W5-atencion.json
"""
import hashlib
import json
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BASE = REPO / "clients/HPF_HappyFlops/03_workflows/base-prod-2026-08-06"
OUT = REPO / "clients/HPF_HappyFlops/03_workflows/ghl"
W0_ID = "VK4M7VQm8CMefbty"
CRED_TG = {"telegramApi": {"id": "vgyWhM8OBUJtYOGC", "name": "H.F"}}
CRED_WEBHOOK = {"httpHeaderAuth": {"id": "jUb7ZjztncX5ACpc", "name": "HPF GHL Webhook Auth"}}
TG_CHAT = "-4925599962"

# sha256 del Code2 del grafo congelado. Si cambia, el port dejó de ser byte-exacto.
SHA_CODE2 = "9b3c9f5f0f7c9a0b"  # se recalcula al generar; ver salida


def nodo(nombre, tipo, tv, pos, params, **extra):
    n = {"parameters": params, "id": str(uuid.uuid4()), "name": nombre,
         "type": tipo, "typeVersion": tv, "position": pos}
    n.update(extra)
    return n


def conexiones(mapa):
    return {s: {"main": [[{"node": d, "type": "main", "index": 0} for d in br]
                         for br in brs]} for s, brs in mapa.items()}


def w0(nombre, pos, op, args_expr):
    return nodo(nombre, "n8n-nodes-base.executeWorkflow", 1.2, pos, {
        "workflowId": {"__rl": True, "value": W0_ID, "mode": "id",
                       "cachedResultName": "HPF·GHL · W0 Client"},
        "workflowInputs": {"mappingMode": "defineBelow",
                           "value": {"op": op, "args": args_expr},
                           "matchingColumns": [], "schema": [],
                           "attemptToConvertTypes": False, "convertFieldsToString": True},
        "options": {"waitForSubWorkflow": True}})


def if_webhook(pos, nodo_ref):
    return nodo("¿Vino por webhook?", "n8n-nodes-base.if", 2, pos, {
        "conditions": {"options": {"caseSensitive": True, "version": 2,
                                   "typeValidation": "loose"},
                       "combinator": "and",
                       "conditions": [{"id": str(uuid.uuid4()),
                                       "leftValue": f"={{{{ $('{nodo_ref}').first().json._via }}}}",
                                       "rightValue": "webhook",
                                       "operator": {"type": "string",
                                                    "operation": "equals"}}]},
        "options": {}})


JS_ENTRADA_CALC = """
// Contrato heredado del origen: `items` (preferido) o `cuentas` (legacy).
//
// DELTA vs el origen: allá el trigger declaraba SIEMPRE los dos campos, y el ruteo
// interno es `if (input.items !== undefined)`. Con `items: ''` esa condición da true,
// entra a orderFromItems(''), parseItemsInput devuelve null y TIRA. O sea: la rama
// `cuentas` era inalcanzable y cualquier llamada legacy reventaba — aunque el prompt
// del Recolector la documenta como formato válido y el código tiene su `else if` con
// mensaje de advertencia, que nunca corrió.
// Acá `items` sólo viaja si trae contenido, así que la rama legacy funciona de verdad.
const j0 = $input.first().json || {};
const porWebhook = !!(j0.body && (j0.body.items !== undefined || j0.body.cuentas !== undefined));
const src = porWebhook ? j0.body : j0;

const vacio = v => v === undefined || v === null ||
                   (typeof v === 'string' && v.trim() === '') ||
                   (Array.isArray(v) && v.length === 0);

const out = { _via: porWebhook ? 'webhook' : 'subworkflow' };
if (!vacio(src.items)) out.items = src.items;
if (!vacio(src.cuentas)) out.cuentas = src.cuentas;
if (out.items === undefined && out.cuentas === undefined) {
  throw new Error('W4: hay que mandar `items` (preferido) o `cuentas` (legacy)');
}
return [{ json: out }];
"""

JS_SALIDA_CALC = """
// DELTA vs el origen: allá el Set exponía sólo `resumen_cajas`, así que un rechazo por
// mínimo (que no trae ese campo) llegaba al agente como vacío y el LLM nunca sabía por
// qué no podía cotizar. Acá viaja el objeto entero.
const r = $input.first().json || {};
if (r.error) {
  return [{ json: {
    ok: false,
    error: r.error,
    detalle_violaciones: r.detalle_violaciones || [],
    // el prompt del Recolector espera leer esto para explicarle el mínimo al cliente
    message_to_agent: r.message_to_agent || 'No se puede cotizar.',
  } }];
}
return [{ json: {
  ok: true,
  costo_total_envio: r.costo_total_envio ?? null,
  costo_total_envio_str: r.costo_total_envio_str ?? null,
  cantidad_cajas: r.cantidad_cajas ?? null,
  resumen_cajas: r.resumen_cajas ?? [],
  cajas: r.cajas ?? [],
  advertencia_minimos: r.advertencia_minimos ?? null,
  // nombre heredado: es el campo que el prompt del Recolector nombra hoy
  'Cantidad de cajas necesarias y costo de envio': r.resumen_cajas ?? [],
} }];
"""

JS_ENTRADA_AP = """
// El origen recibía `{lead: <entity_id de Kommo>}`. Acá la identidad es
// contactId + opportunityId, que es lo que W1 ya tiene resuelto.
const j0 = $input.first().json || {};
const porWebhook = !!(j0.body && j0.body.contactId !== undefined);
const src = porWebhook ? j0.body : j0;
if (!src.contactId) throw new Error('W5: falta "contactId"');
return [{ json: {
  _via: porWebhook ? 'webhook' : 'subworkflow',
  contactId: String(src.contactId),
  opportunityId: src.opportunityId ? String(src.opportunityId) : null,
  motivo: src.motivo || null,
} }];
"""

JS_SALIDA_AP = """
const c = $('Normalizar entrada').first().json;
return [{ json: {
  ok: true,
  contactId: c.contactId,
  opportunityId: c.opportunityId,
  motivo: c.motivo,
  // lo que el LLM lee: confirma que la derivación ocurrió
  message_to_agent: 'Listo, ya avisé al equipo para que te atienda una persona.',
} }];
"""


def gen_w4():
    calc = json.loads((BASE / "tool-calculadora.json").read_text())
    code2 = next(n for n in calc["nodes"] if n["name"] == "Code2")["jsCode_"] \
        if False else next(n for n in calc["nodes"]
                           if n["name"] == "Code2")["parameters"]["jsCode"]
    sha = hashlib.sha256(code2.encode()).hexdigest()

    nodes = [
        nodo("Ejecutado por otro workflow", "n8n-nodes-base.executeWorkflowTrigger", 1.1,
             [-460, 0], {"inputSource": "jsonExample",
                         "jsonExample": '{\n  "cuentas": "",\n  "items": ""\n}'}),
        nodo("Webhook (carril de prueba)", "n8n-nodes-base.webhook", 2, [-460, 200],
             {"httpMethod": "POST", "path": "hpf-w4-calculadora",
              "authentication": "headerAuth", "responseMode": "responseNode",
              "options": {}}, webhookId=str(uuid.uuid4()), credentials=CRED_WEBHOOK),
        nodo("Normalizar entrada", "n8n-nodes-base.code", 2, [-220, 100],
             {"jsCode": JS_ENTRADA_CALC.strip()}),
        # ⚠️ BYTE-EXACTO del grafo congelado. No editar acá: editar en producción,
        # re-congelar y regenerar. El sha está en el manifiesto.
        nodo("Calcular (byte-exacto del origen)", "n8n-nodes-base.code", 2, [20, 100],
             {"jsCode": code2}),
        nodo("Formatear salida", "n8n-nodes-base.code", 2, [260, 100],
             {"jsCode": JS_SALIDA_CALC.strip()}),
        if_webhook([500, 100], "Normalizar entrada"),
        nodo("Respond to Webhook", "n8n-nodes-base.respondToWebhook", 1.1, [740, 0],
             {"respondWith": "allIncomingItems", "options": {}}),
        nodo("Devolver al llamador", "n8n-nodes-base.noOp", 1, [740, 200], {}),
    ]
    conn = conexiones({
        "Ejecutado por otro workflow": [["Normalizar entrada"]],
        "Webhook (carril de prueba)": [["Normalizar entrada"]],
        "Normalizar entrada": [["Calcular (byte-exacto del origen)"]],
        "Calcular (byte-exacto del origen)": [["Formatear salida"]],
        "Formatear salida": [["¿Vino por webhook?"]],
        "¿Vino por webhook?": [["Respond to Webhook"], ["Devolver al llamador"]],
    })
    wf = {"name": "HPF·GHL · W4 CALCULADORA", "nodes": nodes, "connections": conn,
          "settings": {"executionOrder": "v1"}}
    (OUT / "W4-calculadora.json").write_text(json.dumps(wf, indent=2, ensure_ascii=False),
                                             encoding="utf-8")
    print(f"✅ W4-calculadora.json ({len(nodes)} nodos)")
    print(f"   Code2 byte-exacto: {len(code2)} chars · sha256 {sha[:16]}…")
    return sha


def gen_w5():
    nodes = [
        nodo("Ejecutado por otro workflow", "n8n-nodes-base.executeWorkflowTrigger", 1.1,
             [-460, 0], {"inputSource": "jsonExample",
                         "jsonExample": '{\n  "contactId": "",\n  "opportunityId": "",\n'
                                        '  "motivo": ""\n}'}),
        nodo("Webhook (carril de prueba)", "n8n-nodes-base.webhook", 2, [-460, 200],
             {"httpMethod": "POST", "path": "hpf-w5-atencion",
              "authentication": "headerAuth", "responseMode": "responseNode",
              "options": {}}, webhookId=str(uuid.uuid4()), credentials=CRED_WEBHOOK),
        nodo("Normalizar entrada", "n8n-nodes-base.code", 2, [-220, 100],
             {"jsCode": JS_ENTRADA_AP.strip()}),
        # Texto calcado del origen; sólo cambia el id que se interpola
        # (Kommo entity_id → GHL contactId) y se suma el motivo cuando lo hay.
        nodo("Avisar al equipo (Telegram)", "n8n-nodes-base.telegram", 1.2, [20, 100], {
            "chatId": TG_CHAT,
            "text": "=👋 El Lead: {{ $json.contactId }} necesita atención personalizada"
                    "{{ $json.motivo ? ' — ' + $json.motivo : '' }}",
            "additionalFields": {"appendAttribution": False}}, credentials=CRED_TG),
        w0("W0 · mover a En Espera", [260, 100], "update_stage",
           "={{ JSON.stringify({opportunityId: "
           "$('Normalizar entrada').first().json.opportunityId, etapa: 'En Espera'}) }}"),
        w0("W0 · tag atencion_humana", [500, 100], "add_tag",
           "={{ JSON.stringify({contactId: "
           "$('Normalizar entrada').first().json.contactId, tags: ['atencion_humana']}) }}"),
        nodo("Formatear salida", "n8n-nodes-base.code", 2, [740, 100],
             {"jsCode": JS_SALIDA_AP.strip()}),
        if_webhook([980, 100], "Normalizar entrada"),
        nodo("Respond to Webhook", "n8n-nodes-base.respondToWebhook", 1.1, [1220, 0],
             {"respondWith": "allIncomingItems", "options": {}}),
        nodo("Devolver al llamador", "n8n-nodes-base.noOp", 1, [1220, 200], {}),
    ]
    conn = conexiones({
        "Ejecutado por otro workflow": [["Normalizar entrada"]],
        "Webhook (carril de prueba)": [["Normalizar entrada"]],
        "Normalizar entrada": [["Avisar al equipo (Telegram)"]],
        "Avisar al equipo (Telegram)": [["W0 · mover a En Espera"]],
        "W0 · mover a En Espera": [["W0 · tag atencion_humana"]],
        "W0 · tag atencion_humana": [["Formatear salida"]],
        "Formatear salida": [["¿Vino por webhook?"]],
        "¿Vino por webhook?": [["Respond to Webhook"], ["Devolver al llamador"]],
    })
    wf = {"name": "HPF·GHL · W5 ATENCION_PERSONALIZADA", "nodes": nodes,
          "connections": conn, "settings": {"executionOrder": "v1"}}
    (OUT / "W5-atencion.json").write_text(json.dumps(wf, indent=2, ensure_ascii=False),
                                          encoding="utf-8")
    print(f"✅ W5-atencion.json ({len(nodes)} nodos)")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    gen_w4()
    gen_w5()
