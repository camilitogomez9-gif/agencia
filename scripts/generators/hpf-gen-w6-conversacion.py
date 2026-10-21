#!/usr/bin/env python3
"""
HPF · L7 — Genera W6 · Conversación: el cerebro del agente.

Router → Switch de 4 → { Starter | Main Image | Products | Recolector } → partes.

Los systemMessage se leen del grafo CONGELADO (04_agents/base-prod-2026-08-06/) y se
insertan sin tocar una coma. La única excepción es Recolector1, que usa el prompt
parchado — decisión firmada en esta sesión, ver el encabezado de ese archivo.

W6 no manda mensajes: devuelve `partes[]`. Quien envía es W2. Así el cerebro se puede
testear sin escribir en GHL, y la cadencia sigue viviendo en un solo lugar.

Salida: clients/HPF_HappyFlops/03_workflows/ghl/W6-conversacion.json
"""
import hashlib
import json
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PROMPTS = REPO / "clients/HPF_HappyFlops/04_agents/base-prod-2026-08-06"
PARCHADO = REPO / "clients/HPF_HappyFlops/04_agents/agente-recolector1-imagen-parchado.md"
OUT = REPO / "clients/HPF_HappyFlops/03_workflows/ghl"
W3_ID, W4_ID, W5_ID = "vSLHOawn2bFVXyOK", "psGRDByGNjHQ2DVT", "mmo29FTvIquxksWV"
CRED_OAI = {"openAiApi": {"id": "a1k3E4C9uRRHxngs", "name": "H.F"}}
CRED_PG = {"postgres": {"id": "uK59P60DJmOJc4Lm", "name": "H.F"}}
CRED_WH = {"httpHeaderAuth": {"id": "jUb7ZjztncX5ACpc", "name": "HPF GHL Webhook Auth"}}
WEBHOOK_PATH = "hpf-w6-conversacion"

MANIF = json.loads((PROMPTS / "MANIFIESTO.json").read_text())


def prompt(archivo):
    return (PROMPTS / archivo).read_text()


def nodo(nombre, tipo, tv, pos, params, **extra):
    n = {"parameters": params, "id": str(uuid.uuid4()), "name": nombre,
         "type": tipo, "typeVersion": tv, "position": pos}
    n.update(extra)
    return n


def modelo(nombre, pos, model, temp=None):
    opts = {} if temp is None else {"temperature": temp}
    return nodo(nombre, "@n8n/n8n-nodes-langchain.lmChatOpenAi", 1.2, pos,
                {"model": {"__rl": True, "value": model, "mode": "list"},
                 "options": opts}, credentials=CRED_OAI)


def memoria(nombre, pos, ventana=20):
    return nodo(nombre, "@n8n/n8n-nodes-langchain.memoryPostgresChat", 1.3, pos,
                {"sessionIdType": "customKey",
                 "sessionKey": "={{ $('Normalizar entrada').first().json.sessionId }}",
                 "contextWindowLength": ventana}, credentials=CRED_PG)


def parser(nombre, pos, ejemplo):
    return nodo(nombre, "@n8n/n8n-nodes-langchain.outputParserStructured", 1.2, pos,
                {"jsonSchemaExample": json.dumps(ejemplo, ensure_ascii=False, indent=2)})


def agente(nombre, pos, sysmsg, texto, con_parser=False, tools=False):
    opts = {"systemMessage": sysmsg}
    if tools:
        opts["returnIntermediateSteps"] = True
    p = {"promptType": "define", "text": texto, "hasOutputParser": con_parser,
         "options": opts}
    return nodo(nombre, "@n8n/n8n-nodes-langchain.agent", 1.7, pos, p)


def tool_wf(nombre, pos, wf_id, wf_name, descripcion, campos):
    return nodo(nombre, "@n8n/n8n-nodes-langchain.toolWorkflow", 2.2, pos, {
        "description": descripcion,
        "workflowId": {"__rl": True, "value": wf_id, "mode": "id",
                       "cachedResultName": wf_name},
        "workflowInputs": {"mappingMode": "defineBelow", "value": campos,
                           "matchingColumns": [], "schema": [],
                           "attemptToConvertTypes": False, "convertFieldsToString": True},
    })


JS_ENTRADA = """
// Entrada desde W1 (o desde el webhook de prueba, mismo shape).
const j0 = $input.first().json || {};
const porWebhook = !!(j0.body && j0.body.sessionId !== undefined);
const src = porWebhook ? j0.body : j0;
for (const k of ['sessionId', 'texto']) {
  if (src[k] === undefined) throw new Error(`W6: falta "${k}"`);
}
return [{ json: {
  _via: porWebhook ? 'webhook' : 'subworkflow',
  sessionId: String(src.sessionId),
  contactId: src.contactId ?? null,
  opportunityId: src.opportunityId ?? null,
  texto: String(src.texto),
  evento: src.evento ?? null,
  primer_contacto: !!src.primer_contacto,
  fecha: $now.setZone('America/Mexico_City').toFormat("cccc dd/LL/yyyy HH:mm"),
} }];
"""

JS_RUTA = """
// El Router devuelve {step: "step_N"}. El origen defaulteaba a step_4 ante cualquier
// cosa rara — se conserva, es la vía de escape documentada.
const ctx = $('Normalizar entrada').first().json;
const out = $input.first().json;
const crudo = out.output ?? out;
let step = (typeof crudo === 'object' ? crudo.step : crudo) || 'step_4';
step = String(step).trim();
if (!/^step_[1-4]$/.test(step)) step = 'step_4';
// Primer contacto siempre va al saludo, sin importar lo que diga el Router.
if (ctx.primer_contacto) step = 'step_1';
return [{ json: { ...ctx, step } }];
"""

JS_PARTIR = """
// Corta la respuesta del agente en burbujas. El origen usaba un LLM para esto
// (Message a model1, 13 KB de prompt). Acá es determinístico: mismo criterio de corte
// —párrafos— pero sin una llamada más ni la variabilidad de un modelo.
// REGLA HEREDADA: una cotización y el bloque de los 7 pasos NUNCA se parten.
const ctx = $('Normalizar entrada').first().json;
const salida = $input.first().json;
let txt = String(salida.output ?? salida.text ?? '').trim();
if (!txt) throw new Error('W6: el agente no devolvió texto');

// El modelo a veces envuelve toda la respuesta entre comillas (rectas o tipográficas)
// y eso llegaba al cliente tal cual: la primera burbuja abría con « y la última
// cerraba con ». En el origen lo absorbía el splitter LLM; acá hay que sacarlo.
const PAR = [['"', '"'], ['\u201c', '\u201d'], ["'", "'"], ['\u00ab', '\u00bb']];
for (const [a, b] of PAR) {
  if (txt.length > 1 && txt.startsWith(a) && txt.endsWith(b)) {
    txt = txt.slice(a.length, -b.length).trim();
    break;
  }
}

const INDIVISIBLE = /(Cotizaci[óo]n|Anticipo|7 SENCILLOS PASOS|7 DIAS DE PROMO)/i;

let partes;
if (INDIVISIBLE.test(txt)) {
  partes = [txt];                                  // entero, sin cortar
} else {
  partes = txt.split(/\\n\\s*\\n/).map(s => s.trim()).filter(Boolean);
  // el origen mandaba como máximo 3 burbujas
  if (partes.length > 3) {
    partes = [partes[0], partes[1], partes.slice(2).join('\\n\\n')];
  }
  if (partes.length === 0) partes = [txt];
}

const pasos = (salida.intermediateSteps || []).map(s => s?.action?.tool).filter(Boolean);
return [{ json: {
  ok: true,
  sessionId: ctx.sessionId, contactId: ctx.contactId,
  step: $('Elegir ruta').first().json.step,
  partes,
  tools_usadas: pasos,
  texto_completo: txt,
} }];
"""

JS_CARDS_A_PARTES = """
// Las cards del catálogo se convierten en burbujas: texto + su asset.
const ctx = $('Normalizar entrada').first().json;
const r = $input.first().json;
const cards = r.cards || [];
const partes = cards.map(c => ({
  texto: c.texto || c.nombre,
  adjuntos: c.media_url ? [c.media_url] : [],
}));
if (partes.length === 0) {
  partes.push({ texto: 'Déjame revisar eso y te confirmo.', adjuntos: [] });
}
return [{ json: {
  ok: true, sessionId: ctx.sessionId, contactId: ctx.contactId,
  step: $('Elegir ruta').first().json.step,
  partes, sin_media: r.sin_media || [], tools_usadas: ['CATALOGO'],
} }];
"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    p_router = prompt("agente-router.md")
    p_starter = prompt("agente-starter.md")
    p_mainimg = prompt("agente-main-image.md")
    p_products = prompt("agente-products.md")
    p_recolector = prompt("agente-recolector.md")

    U = "={{ $json.texto }}"
    nodes = [
        nodo("Ejecutado por otro workflow", "n8n-nodes-base.executeWorkflowTrigger", 1.1,
             [-1100, 0], {"inputSource": "jsonExample", "jsonExample": json.dumps(
                 {"sessionId": "", "contactId": "", "opportunityId": "",
                  "texto": "", "evento": "", "primer_contacto": False},
                 indent=2)}),
        nodo("Webhook (carril de prueba)", "n8n-nodes-base.webhook", 2, [-1100, 200],
             {"httpMethod": "POST", "path": WEBHOOK_PATH, "authentication": "headerAuth",
              "responseMode": "responseNode", "options": {}},
             webhookId=str(uuid.uuid4()), credentials=CRED_WH),
        nodo("Normalizar entrada", "n8n-nodes-base.code", 2, [-880, 100],
             {"jsCode": JS_ENTRADA.strip()}),

        # ── Router
        agente("Router", [-640, 100], p_router,
               "=Mensaje del usuario: {{ $json.texto }}", con_parser=True),
        modelo("LM Router", [-720, 320], "gpt-5-mini"),
        memoria("Memoria Router", [-600, 320], 25),
        parser("Parser Router", [-480, 320], {"step": "step_1"}),
        nodo("Elegir ruta", "n8n-nodes-base.code", 2, [-400, 100],
             {"jsCode": JS_RUTA.strip()}),

        nodo("Switch de step", "n8n-nodes-base.switch", 3, [-180, 100], {
            "rules": {"values": [
                {"conditions": {"options": {"caseSensitive": True, "version": 2,
                                            "typeValidation": "loose"},
                                "combinator": "and", "conditions": [
                                    {"id": str(uuid.uuid4()),
                                     "leftValue": "={{ $json.step }}", "rightValue": s,
                                     "operator": {"type": "string", "operation": "equals"}}]},
                 "renameOutput": True, "outputKey": k}
                for s, k in (("step_1", "1-saludo"), ("step_2", "2-evento"),
                             ("step_3", "3-productos"), ("step_4", "4-cierre"))]},
            "options": {}}),

        # ── step_1 · Starter
        agente("Starter", [120, -260], p_starter, "=Respuesta del usuario: {{ $json.texto }}"),
        modelo("LM Starter", [60, -60], "gpt-4o-mini", 0),
        memoria("Memoria Starter", [200, -60]),

        # ── step_2 · Main Image → catálogo (imagen principal del evento)
        agente("Main Image", [120, -40], p_mainimg,
               "=Respuesta del usuario: {{ $json.texto }}\nFecha de hoy: {{ $json.fecha }}",
               con_parser=True),
        modelo("LM Main Image", [40, 160], "gpt-4o", 0),
        memoria("Memoria Main Image", [160, 160]),
        parser("Parser Main Image", [280, 160], {"evento": "Boda", "texto_dinamico": ""}),
        nodo("W3 · imagen principal", "n8n-nodes-base.executeWorkflow", 1.2, [400, -40], {
            "workflowId": {"__rl": True, "value": W3_ID, "mode": "id",
                           "cachedResultName": "HPF·GHL · W3 Catálogo"},
            "workflowInputs": {"mappingMode": "defineBelow", "value": {
                "evento": "={{ $json.output.evento }}",
                "productos": '=["todos los productos"]'},
                "matchingColumns": [], "schema": [], "attemptToConvertTypes": False,
                "convertFieldsToString": True},
            "options": {"waitForSubWorkflow": True}}),

        # ── step_3 · Products → catálogo (fichas)
        agente("Products", [120, 220], p_products, U, con_parser=True),
        modelo("LM Products", [40, 420], "gpt-4.1-mini", 0.3),
        memoria("Memoria Products", [160, 420]),
        parser("Parser Products", [280, 420],
               {"evento": "", "subcategoria": "", "productos": ["producto1"],
                "texto_dinamico": ""}),
        nodo("W3 · fichas", "n8n-nodes-base.executeWorkflow", 1.2, [400, 220], {
            "workflowId": {"__rl": True, "value": W3_ID, "mode": "id",
                           "cachedResultName": "HPF·GHL · W3 Catálogo"},
            "workflowInputs": {"mappingMode": "defineBelow", "value": {
                "evento": "={{ $json.output.evento }}",
                "subcategoria": "={{ $json.output.subcategoria }}",
                "productos": "={{ JSON.stringify($json.output.productos) }}"},
                "matchingColumns": [], "schema": [], "attemptToConvertTypes": False,
                "convertFieldsToString": True},
            "options": {"waitForSubWorkflow": True}}),
        nodo("Cards a partes", "n8n-nodes-base.code", 2, [640, 100],
             {"jsCode": JS_CARDS_A_PARTES.strip()}),

        # ── step_4 · Recolector (la vendedora) con sus tools
        agente("Recolector", [120, 520], p_recolector,
               "=Mensaje del usuario: {{ $json.texto }}\nFecha de hoy: {{ $json.fecha }}",
               tools=True),
        modelo("LM Recolector", [0, 740], "gpt-4o", 0.2),
        memoria("Memoria Recolector", [120, 740]),
        tool_wf("CALCULADORA", [240, 740], W4_ID, "HPF·GHL · W4 CALCULADORA",
                "Calcula el costo de envío y el empaque de una cotización. Recibe `items`: "
                "un JSON string con un arreglo de objetos {producto, cantidad} usando los "
                "nombres canónicos del catálogo. Devuelve costo_total_envio, cantidad_cajas "
                "y resumen_cajas. Si algún producto está por debajo de su mínimo de compra, "
                "RECHAZA el cálculo y devuelve message_to_agent con el mínimo real: en ese "
                "caso comunicáselo al cliente y no inventes un valor alternativo.",
                {"items": "={{ $fromAI('items', 'JSON string con [{producto, cantidad}]', "
                          "'string') }}", "cuentas": ""}),
        tool_wf("ATENCION_PERSONALIZADA", [360, 740], W5_ID,
                "HPF·GHL · W5 ATENCION_PERSONALIZADA",
                "Deriva la conversación a una persona del equipo. Llamala cuando pidan "
                "diseños personalizados, un diseño específico, cuando no tengas información "
                "suficiente, cuando la consulta sea demasiado específica, ante quejas o "
                "postventa, o cuando no estés seguro de tu respuesta.",
                {"contactId": "={{ $('Normalizar entrada').first().json.contactId }}",
                 "opportunityId": "={{ $('Normalizar entrada').first().json.opportunityId }}",
                 "motivo": "={{ $fromAI('motivo', 'por qué derivás', 'string') }}"}),
        nodo("Think", "@n8n/n8n-nodes-langchain.toolThink", 1, [480, 740],
             {"description": "Para razonar sobre el costo del envio si te lo solicitan."}),

        nodo("Partir en burbujas", "n8n-nodes-base.code", 2, [640, 380],
             {"jsCode": JS_PARTIR.strip()}),

        nodo("¿Vino por webhook?", "n8n-nodes-base.if", 2, [880, 240], {
            "conditions": {"options": {"caseSensitive": True, "version": 2,
                                       "typeValidation": "loose"},
                           "combinator": "and", "conditions": [{
                               "id": str(uuid.uuid4()),
                               "leftValue": "={{ $('Normalizar entrada').first().json._via }}",
                               "rightValue": "webhook",
                               "operator": {"type": "string", "operation": "equals"}}]},
            "options": {}}),
        nodo("Respond to Webhook", "n8n-nodes-base.respondToWebhook", 1.1, [1100, 140],
             {"respondWith": "allIncomingItems", "options": {}}),
        nodo("Devolver al llamador", "n8n-nodes-base.noOp", 1, [1100, 340], {}),
    ]

    main_c = {
        "Ejecutado por otro workflow": [["Normalizar entrada"]],
        "Webhook (carril de prueba)": [["Normalizar entrada"]],
        "Normalizar entrada": [["Router"]],
        "Router": [["Elegir ruta"]],
        "Elegir ruta": [["Switch de step"]],
        "Switch de step": [["Starter"], ["Main Image"], ["Products"], ["Recolector"]],
        "Starter": [["Partir en burbujas"]],
        "Main Image": [["W3 · imagen principal"]],
        "W3 · imagen principal": [["Cards a partes"]],
        "Products": [["W3 · fichas"]],
        "W3 · fichas": [["Cards a partes"]],
        "Recolector": [["Partir en burbujas"]],
        "Cards a partes": [["¿Vino por webhook?"]],
        "Partir en burbujas": [["¿Vino por webhook?"]],
        "¿Vino por webhook?": [["Respond to Webhook"], ["Devolver al llamador"]],
    }
    conn = {s: {"main": [[{"node": d, "type": "main", "index": 0} for d in br]
                         for br in brs]} for s, brs in main_c.items()}

    # sub-conexiones (modelo / memoria / parser / tools)
    sub = [
        ("LM Router", "ai_languageModel", "Router"),
        ("Memoria Router", "ai_memory", "Router"),
        ("Parser Router", "ai_outputParser", "Router"),
        ("LM Starter", "ai_languageModel", "Starter"),
        ("Memoria Starter", "ai_memory", "Starter"),
        ("LM Main Image", "ai_languageModel", "Main Image"),
        ("Memoria Main Image", "ai_memory", "Main Image"),
        ("Parser Main Image", "ai_outputParser", "Main Image"),
        ("LM Products", "ai_languageModel", "Products"),
        ("Memoria Products", "ai_memory", "Products"),
        ("Parser Products", "ai_outputParser", "Products"),
        ("LM Recolector", "ai_languageModel", "Recolector"),
        ("Memoria Recolector", "ai_memory", "Recolector"),
        ("CALCULADORA", "ai_tool", "Recolector"),
        ("ATENCION_PERSONALIZADA", "ai_tool", "Recolector"),
        ("Think", "ai_tool", "Recolector"),
    ]
    for src, tipo, dst in sub:
        conn.setdefault(src, {})[tipo] = [[{"node": dst, "type": tipo, "index": 0}]]

    wf = {"name": "HPF·GHL · W6 Conversación", "nodes": nodes, "connections": conn,
          "settings": {"executionOrder": "v1"}}
    p = OUT / "W6-conversacion.json"
    p.write_text(json.dumps(wf, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"✅ {p.relative_to(REPO)}  ({len(nodes)} nodos)")
    print("\nprompts insertados (sha del grafo congelado):")
    for nom, arch in (("AI Agent", "router"), ("AI Agent Starter", "starter"),
                      ("AI Agent Main Image", "main-image"),
                      ("AI Agent Products", "products"),
                      ("AI Agent Recolector", "recolector")):
        e = MANIF[nom]
        txt = prompt(e["archivo"])
        ok = hashlib.sha256(txt.encode()).hexdigest() == e["sha256"]
        print(f"  {arch:12s} {e['chars']:6d} chars  {'byte-exacto ✅' if ok else 'DIFIERE ❌'}")
    print(f"\n   webhook de prueba: POST /webhook/{WEBHOOK_PATH}")


if __name__ == "__main__":
    main()
