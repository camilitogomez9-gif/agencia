#!/usr/bin/env python3
"""
HPF · L5 — Genera W2 · Salida: la ÚNICA implementación de la cadencia de mensajes.

Reemplaza del origen (arquitectura de salesbots de Kommo):
  · 14 × `actualizar*`   — PATCH del texto al campo custom 1099420 del lead
  · 32 × `Envio Mensaje*`— POST /api/v2/salesbot/run con el bot_id que lee ese campo
  ·  3 × `Saludo PTE`    — la secuencia de saludo
  ·  Character_Cleaner / Message a model1 / Formatear mensaje1 + los Wait de 2 s

En GHL el envío es UNA llamada, así que los dos pasos colapsan. Lo que NO colapsa es
la cadencia: mandar la respuesta partida en 2-3 burbujas con pausa es lo que hace que
Rebeca no suene a bot, y eso se preserva tal cual.

La llaman W1 y los 4 workflows de reenganche. Si mañana cambia la pausa, cambia acá y
en ningún otro lado.

Salida: clients/HPF_HappyFlops/03_workflows/ghl/W2-salida.json
"""
import json
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "clients/HPF_HappyFlops/03_workflows/ghl"
W0_ID = "VK4M7VQm8CMefbty"
CRED_WEBHOOK = {"httpHeaderAuth": {"id": "jUb7ZjztncX5ACpc", "name": "HPF GHL Webhook Auth"}}
WEBHOOK_PATH = "hpf-w2-salida"

JS_ENTRADA = """
// Entrada: { contactId, partes: [ {texto, adjuntos?} | "texto suelto" ], pausa_seg? }
// Sale un item por parte, ya numerado. El orden es el contrato: parte1, parte2, parte3.
const j0 = $input.first().json || {};
const porWebhook = !!(j0.body && j0.body.contactId !== undefined);
const src = porWebhook ? j0.body : j0;

if (!src.contactId) throw new Error('W2: falta "contactId"');

let partes = src.partes ?? [];
if (typeof partes === 'string') {
  // Puede ser un array serializado o, simplemente, el texto de una única burbuja.
  const t = partes.trim();
  if (t.startsWith('[') || t.startsWith('{')) {
    try { partes = JSON.parse(t); }
    catch (e) { throw new Error('W2: "partes" parece JSON pero no parsea'); }
  } else {
    partes = [partes];
  }
}
if (!Array.isArray(partes)) partes = [partes];

// normaliza: string suelto → {texto}; descarta vacías (el origen también las salteaba
// con los If parte2/parte3 notEmpty)
const norm = [];
for (const p of partes) {
  const o = (typeof p === 'string') ? { texto: p } : (p || {});
  const texto = (o.texto ?? o.text ?? '').toString();
  const adj = o.adjuntos ?? o.attachments ?? [];
  const adjuntos = Array.isArray(adj) ? adj : (adj ? [adj] : []);
  if (!texto.trim() && adjuntos.length === 0) continue;
  norm.push({ texto, adjuntos });
}
if (norm.length === 0) throw new Error('W2: no quedó ninguna parte con contenido');

const pausa = src.pausa_seg !== undefined ? Number(src.pausa_seg) : 2;

return norm.map((p, i) => ({ json: {
  _via: porWebhook ? 'webhook' : 'subworkflow',
  contactId: src.contactId,
  seq: i + 1,
  total: norm.length,
  texto: p.texto,
  adjuntos: p.adjuntos,
  // la última parte no espera: la pausa va ENTRE burbujas, no después de la última
  pausa_seg: (i + 1 < norm.length) ? pausa : 0,
} }));
"""

JS_PREPARAR = """
// Traduce la parte al contrato de W0. Una parte con adjuntos va por send_media.
const p = $input.first().json;
const conMedia = Array.isArray(p.adjuntos) && p.adjuntos.length > 0;
return [{ json: {
  ...p,
  op: conMedia ? 'send_media' : 'send_text',
  args: conMedia
    ? { contactId: p.contactId, mensaje: p.texto, adjuntos: p.adjuntos }
    : { contactId: p.contactId, mensaje: p.texto },
} }];
"""

JS_RESUMEN = """
// Junta lo que devolvió cada llamada a W0. Este objeto ES la evidencia del envío:
// lleva el texto exacto que salió y el id que devolvió GHL, para poder releerlo.
const enviados = [];
for (const it of $input.all()) {
  const j = it.json || {};
  const d = (j.data || {});
  enviados.push({
    seq: j.seq ?? null,
    body: j.texto ?? null,
    attachments: j.adjuntos ?? [],
    ghl_message_id: d.messageId ?? null,
    ghl_conversation_id: d.conversationId ?? null,
    http_status: j.http_status ?? null,
  });
}
enviados.sort((a, b) => (a.seq ?? 0) - (b.seq ?? 0));
return [{ json: {
  ok: enviados.every(e => e.ghl_message_id),
  partes_enviadas: enviados.length,
  enviados,
} }];
"""


def nodo(nombre, tipo, tv, pos, params, **extra):
    n = {"parameters": params, "id": str(uuid.uuid4()), "name": nombre,
         "type": tipo, "typeVersion": tv, "position": pos}
    n.update(extra)
    return n


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    nodes = [
        nodo("Ejecutado por otro workflow", "n8n-nodes-base.executeWorkflowTrigger", 1.1,
             [-520, 0], {"inputSource": "jsonExample", "jsonExample": json.dumps({
                 "contactId": "...",
                 "partes": [{"texto": "primera burbuja"},
                            {"texto": "con foto", "adjuntos": ["https://..."]}],
                 "pausa_seg": 2}, indent=2, ensure_ascii=False)}),
        nodo("Webhook (carril de prueba)", "n8n-nodes-base.webhook", 2, [-520, 200],
             {"httpMethod": "POST", "path": WEBHOOK_PATH, "authentication": "headerAuth",
              "responseMode": "responseNode", "options": {}},
             webhookId=str(uuid.uuid4()), credentials=CRED_WEBHOOK),
        nodo("Normalizar partes", "n8n-nodes-base.code", 2, [-280, 100],
             {"jsCode": JS_ENTRADA.strip()}),
        nodo("Recorrer partes", "n8n-nodes-base.splitInBatches", 3, [-40, 100],
             {"batchSize": 1, "options": {"reset": False}}),
        nodo("Preparar op", "n8n-nodes-base.code", 2, [200, 220],
             {"jsCode": JS_PREPARAR.strip()}),
        nodo("W0 · enviar", "n8n-nodes-base.executeWorkflow", 1.2, [420, 220], {
            "workflowId": {"__rl": True, "value": W0_ID, "mode": "id",
                           "cachedResultName": "HPF·GHL · W0 Client"},
            "workflowInputs": {"mappingMode": "defineBelow", "value": {
                "op": "={{ $json.op }}",
                "args": "={{ JSON.stringify($json.args) }}"},
                "matchingColumns": [], "schema": [], "attemptToConvertTypes": False,
                "convertFieldsToString": True},
            "options": {"waitForSubWorkflow": True}}),
        nodo("Arrastrar contexto", "n8n-nodes-base.code", 2, [640, 220], {"jsCode": (
            "// W0 devuelve sólo su resultado; le re-pegamos la parte para el resumen.\n"
            "const p = $('Preparar op').first().json;\n"
            "const r = $input.first().json || {};\n"
            "return [{ json: { ...r, seq: p.seq, texto: p.texto, adjuntos: p.adjuntos,\n"
            "                  pausa_seg: p.pausa_seg } }];")}),
        nodo("Pausa entre burbujas", "n8n-nodes-base.wait", 1.1, [860, 220],
             {"amount": "={{ $json.pausa_seg }}", "unit": "seconds"},
             webhookId=str(uuid.uuid4())),
        nodo("Armar resumen", "n8n-nodes-base.code", 2, [200, -20],
             {"jsCode": JS_RESUMEN.strip()}),
        nodo("¿Vino por webhook?", "n8n-nodes-base.if", 2, [440, -20], {
            "conditions": {"options": {"caseSensitive": True, "version": 2,
                                       "typeValidation": "loose"},
                           "combinator": "and",
                           "conditions": [{
                               "id": str(uuid.uuid4()),
                               "leftValue": "={{ $('Normalizar partes').first().json._via }}",
                               "rightValue": "webhook",
                               "operator": {"type": "string", "operation": "equals"}}]},
            "options": {}}),
        nodo("Respond to Webhook", "n8n-nodes-base.respondToWebhook", 1.1, [680, -100],
             {"respondWith": "allIncomingItems", "options": {}}),
        nodo("Devolver al llamador", "n8n-nodes-base.noOp", 1, [680, 60], {}),
    ]

    conexiones = {
        "Ejecutado por otro workflow": {"main": [[{"node": "Normalizar partes", "type": "main", "index": 0}]]},
        "Webhook (carril de prueba)": {"main": [[{"node": "Normalizar partes", "type": "main", "index": 0}]]},
        "Normalizar partes": {"main": [[{"node": "Recorrer partes", "type": "main", "index": 0}]]},
        # splitInBatches v3: salida 0 = "done", salida 1 = "loop"
        "Recorrer partes": {"main": [
            [{"node": "Armar resumen", "type": "main", "index": 0}],
            [{"node": "Preparar op", "type": "main", "index": 0}],
        ]},
        "Preparar op": {"main": [[{"node": "W0 · enviar", "type": "main", "index": 0}]]},
        "W0 · enviar": {"main": [[{"node": "Arrastrar contexto", "type": "main", "index": 0}]]},
        "Arrastrar contexto": {"main": [[{"node": "Pausa entre burbujas", "type": "main", "index": 0}]]},
        "Pausa entre burbujas": {"main": [[{"node": "Recorrer partes", "type": "main", "index": 0}]]},
        "Armar resumen": {"main": [[{"node": "¿Vino por webhook?", "type": "main", "index": 0}]]},
        "¿Vino por webhook?": {"main": [
            [{"node": "Respond to Webhook", "type": "main", "index": 0}],
            [{"node": "Devolver al llamador", "type": "main", "index": 0}],
        ]},
    }

    wf = {"name": "HPF·GHL · W2 Salida", "nodes": nodes, "connections": conexiones,
          "settings": {"executionOrder": "v1"}}
    p = OUT / "W2-salida.json"
    p.write_text(json.dumps(wf, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ {p.relative_to(REPO)}  ({len(nodes)} nodos)")
    print(f"   webhook de prueba: POST /webhook/{WEBHOOK_PATH}")


if __name__ == "__main__":
    main()
