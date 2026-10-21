#!/usr/bin/env python3
"""
HPF · L6 — Genera W1 · Inbound Handler (esqueleto).

Cubre: webhook, normalización, idempotencia, identidad, gates de etapa y debounce.
El router y los agentes quedan stubbeados — eso es L7.

Reemplaza del origen: `New_Message`, `If25`, `Get_Contact`, `Clear_Contact_Data`,
`All_Data`, `No es IA`, `No es EEUU`, `Get_Entity*`, los gates `If5/7/8/9/12/20/21/23`,
`Si está en perdidos`, `En prod?*`, `Memory_ID*` y los 15 nodos de los dos debounces.

Tres cosas que NO existían en el origen y son obligatorias acá:

1. **Idempotencia.** El debounce de 50 s hace que el webhook de GHL timeoutee; si GHL
   reintenta, el mismo mensaje entra dos veces. En Kommo esto no pasaba porque el
   webhook respondía al instante. Se resuelve con un INSERT ON CONFLICT atómico.

2. **Respuesta temprana.** Por lo mismo: W1 contesta un ack apenas pasa el gate de
   idempotencia y sigue procesando async — que es, además, lo que hace el origen
   (su webhook no espera).

3. **Identidad.** Kommo mandaba el lead ya creado. GHL manda un contacto; la
   oportunidad hay que resolverla o crearla, y el sessionKey de la memoria hay que
   preservarlo o los leads en curso pierden el historial en el cutover.

Salida: clients/HPF_HappyFlops/03_workflows/ghl/W1-inbound.json
"""
import json
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "clients/HPF_HappyFlops/03_workflows/ghl"
W0_ID = "VK4M7VQm8CMefbty"
W2_ID = "MdbOREN56lfQTYlM"   # Salida
W6_ID = "cNmJCP2qVhdtfCH0"   # Conversación
CRED_PG = {"postgres": {"id": "uK59P60DJmOJc4Lm", "name": "H.F"}}
CRED_REDIS = {"redis": {"id": "o8I3YHY4b5xY8Ipo", "name": "H.F"}}
CRED_WEBHOOK = {"httpHeaderAuth": {"id": "jUb7ZjztncX5ACpc", "name": "HPF GHL Webhook Auth"}}
WEBHOOK_PATH = "hpf-w1-inbound"

SQL_IDEMPOTENCIA = """CREATE TABLE IF NOT EXISTS hpf_mensajes_vistos (
  message_id text PRIMARY KEY,
  visto_at   timestamptz NOT NULL DEFAULT now()
);
DELETE FROM hpf_mensajes_vistos WHERE visto_at < now() - interval '24 hours';
INSERT INTO hpf_mensajes_vistos (message_id) VALUES ($1)
ON CONFLICT (message_id) DO NOTHING
RETURNING message_id;"""

# Preserva el session_id histórico de Kommo (`<telefono>2131`). Si el contacto no
# está mapeado todavía, lo deriva del teléfono con la misma regla del origen.
SQL_IDENTIDAD = """CREATE TABLE IF NOT EXISTS hpf_identity (
  ghl_contact_id   text PRIMARY KEY,
  phone_raw        text,
  phone_e164       text,
  session_id       text NOT NULL,
  kommo_entity_id  text,
  kommo_contact_id text,
  created_at       timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS hpf_identity_session_idx ON hpf_identity (session_id);
INSERT INTO hpf_identity (ghl_contact_id, phone_e164, session_id)
VALUES ($1, $2, regexp_replace($2, '\\D', '', 'g') || '2131')
ON CONFLICT (ghl_contact_id) DO UPDATE SET phone_e164 = COALESCE(EXCLUDED.phone_e164,
                                                                 hpf_identity.phone_e164)
RETURNING session_id, ghl_contact_id;"""

JS_NORMALIZAR = """
// Contrato de entrada — lo define NUESTRO workflow WF-01 de GHL, no GHL: el paso
// "Webhook" de un GHL Workflow deja mapear campos a mano. Está documentado en la guía
// de provisión; si cambia allá, cambia acá.
//   { contactId, conversationId, messageId, body, attachments[], phone, canal }
const j0 = $input.first().json || {};
const src = (j0.body && j0.body.contactId !== undefined) ? j0.body : j0;

const faltan = ['contactId', 'messageId'].filter(k => !src[k]);
if (faltan.length) {
  throw new Error(`W1: el relay no mandó ${faltan.join(', ')}. ` +
    `Revisar el mapeo del paso Webhook en WF-01.`);
}

let adj = src.attachments ?? [];
if (typeof adj === 'string') {
  const t = adj.trim();
  adj = t.startsWith('[') ? JSON.parse(t) : (t ? [t] : []);
}
if (!Array.isArray(adj)) adj = adj ? [adj] : [];

const texto = String(src.body ?? '').trim();

// Ruteo por tipo, réplica de `checkType` del origen (text / voice / Image).
let tipo = 'texto';
const url0 = String(adj[0] || '').toLowerCase();
if (adj.length) {
  if (/\\.(ogg|oga|mp3|m4a|wav|amr)(\\?|$)/.test(url0)) tipo = 'audio';
  else if (/\\.pdf(\\?|$)/.test(url0)) tipo = 'pdf';
  else tipo = 'imagen';
}

return [{ json: {
  contactId: String(src.contactId),
  conversationId: src.conversationId ? String(src.conversationId) : null,
  messageId: String(src.messageId),
  phone: src.phone ? String(src.phone) : null,
  canal: src.canal || 'WhatsApp',
  texto,
  adjuntos: adj,
  tipo,
  // el test manda debounce_seg: 0; producción usa los del origen (50 texto / 15 imagen)
  debounce_seg: src.debounce_seg !== undefined
    ? Number(src.debounce_seg)
    : (tipo === 'imagen' ? 15 : 50),
  recibido_at: $now.toISO(),
} }];
"""

JS_EVALUAR = """
// Traducción de los gates de etapa del origen. En Kommo se hacía con `contains` sobre
// el JSON del lead serializado — de ahí el bug del "143" que matcheaba cualquier
// timestamp. Acá es igualdad de UUID.
const ETAPAS = __ETAPAS__;
const nombreDe = Object.fromEntries(Object.entries(ETAPAS).map(([k, v]) => [v, k]));

// El agente se calla en estas etapas (equivale a If7/If9/If12/If20 + "Si está en perdidos")
const BLOQUEO = {
  'En Espera':        'atencion_humana',   // Kommo 91266100 atención personalizada
  'Pago Confirmado':  'pago_confirmado',   // Kommo 91450360
  'En Producción':    'en_produccion',     // Kommo 100395519
  'Ventas Perdidas':  'perdido',           // Kommo 143
  'Ganado':           'ganado',            // Kommo 142
};

const ctx  = $('Normalizar entrada').first().json;
const ses  = $('Resolver identidad').first().json;
const opp  = ($input.first().json.data || {}).opportunity || {};
const via  = $('W0 · find or create').first().json.via || null;

const etapaId     = opp.pipelineStageId || null;
const etapaNombre = nombreDe[etapaId] || null;
const motivo      = BLOQUEO[etapaNombre] || null;

// Cliente que vuelve: la oportunidad ya existía y está cerrada. En Kommo esto era un
// lead nuevo; acá hay que reciclar la misma (ver PM-IDN-03-decision.md).
const vuelve = via === 'existente' && ['Ganado', 'Ventas Perdidas'].includes(etapaNombre);

let ruta = 'seguir';
if (vuelve) ruta = 'cliente_vuelve';
else if (motivo) ruta = 'bloqueado';

return [{ json: {
  ...ctx,
  sessionId: ses.session_id,
  opportunityId: opp.id || null,
  etapa_id: etapaId,
  etapa: etapaNombre,
  via_oportunidad: via,
  ruta,
  motivo_bloqueo: motivo,
  gates: { etapa: etapaNombre, bloqueo: motivo, via, cliente_vuelve: vuelve },
} }];
"""

JS_ULTIMO = """
// Debounce "gana el último", igual que el origen: cada mensaje empuja a una lista de
// Redis y duerme; al despertar sólo sigue la ejecución cuyo texto sigue siendo el
// último de la lista. Las demás mueren acá.
//
// Ojo: el origen tenía este mismo mecanismo ROTO en la rama de imagen — `Guardar1`
// empujaba `$workflow.id`, que es constante, así que la comparación daba siempre true
// y no deduplicaba nada. Acá se empuja el messageId, que sí es único.
const ctx  = $('Evaluar estado').first().json;
const raw  = $input.first().json;
const lista = raw.Mensajes ?? raw.propertyName ?? raw ?? [];
const arr = Array.isArray(lista) ? lista : [lista];
const ultimo = arr.length ? String(arr[arr.length - 1]) : null;
const soyElUltimo = ultimo === ctx.messageId;

return [{ json: {
  ...ctx,
  debounce: { acumulados: arr.length, ultimo, soy_el_ultimo: soyElUltimo,
              mensajes: arr },
  soy_el_ultimo: soyElUltimo,
} }];
"""

JS_EVIDENCIA = """
// Objeto de evidencia del turno completo. Es lo que el runner de paridad lee del
// runData: qué entró, por dónde ruteó, qué tools usó y qué salió a GHL.
const ctx = $('Evaluar estado').first().json;
const cerebro = $('W6 · conversación').first().json;
const envio = $input.first().json;
return [{ json: {
  ok: true,
  sessionId: ctx.sessionId, contactId: ctx.contactId, opportunityId: ctx.opportunityId,
  entrada: { texto: ctx.texto, tipo: ctx.tipo, adjuntos: ctx.adjuntos },
  etapa: ctx.etapa, gates: ctx.gates,
  step: cerebro.step,
  tools_usadas: cerebro.tools_usadas || [],
  partes_enviadas: envio.partes_enviadas ?? null,
  enviados: envio.enviados || [],
} }];
"""

ETAPAS = {
    "Lead Nuevo": "cf8fc770-81b1-422c-8394-d00bfb97a3f0",
    "Saludo Enviado": "f9709293-d03c-47f1-949f-0c03ab077a45",
    "Evento Identificado": "fec50c94-fba0-444b-8c75-7a97da9e0daa",
    "Productos Mostrados": "49c7401f-8af1-4d8f-a1b4-e989b6d0a5e2",
    "Cotizado": "96fa0ade-c853-4db3-97f4-56d58d69af8c",
    "Esperando Pago": "843a06f1-1214-4baa-a3a0-f197cb240b5d",
    "Pago Confirmado": "96d760e5-f290-456c-a117-57e61ce6c27d",
    "Diseño en Proceso": "d35bb30d-97d5-48c4-81f8-5ecabf32e57d",
    "En Producción": "008689c6-80d8-4712-981b-1d800e1e6137",
    "Enviado": "218b9b41-4007-4b1c-bbe4-4e775ddf00b5",
    "En Espera": "48de80e9-31a9-472a-b030-5b9fe9174810",
    "Ganado": "909a816d-997e-4d90-8dc1-dc4b0dcd16d7",
    "Ventas Perdidas": "6abfe419-adf2-4df5-87c5-ef4f62e01464",
}


def nodo(nombre, tipo, tv, pos, params, **extra):
    n = {"parameters": params, "id": str(uuid.uuid4()), "name": nombre,
         "type": tipo, "typeVersion": tv, "position": pos}
    n.update(extra)
    return n


def pg(nombre, pos, query, repl=None, siempre=False):
    p = {"operation": "executeQuery", "query": query, "options": {}}
    if repl:
        p["options"] = {"queryReplacement": repl}
    extra = {"credentials": CRED_PG}
    if siempre:
        extra["alwaysOutputData"] = True
    return nodo(nombre, "n8n-nodes-base.postgres", 2.4, pos, p, **extra)


def w0(nombre, pos, op, args_expr):
    return nodo(nombre, "n8n-nodes-base.executeWorkflow", 1.2, pos, {
        "workflowId": {"__rl": True, "value": W0_ID, "mode": "id",
                       "cachedResultName": "HPF·GHL · W0 Client"},
        "workflowInputs": {"mappingMode": "defineBelow",
                           "value": {"op": op, "args": args_expr},
                           "matchingColumns": [], "schema": [],
                           "attemptToConvertTypes": False, "convertFieldsToString": True},
        "options": {"waitForSubWorkflow": True}})


def cond_ig(izq, der, tipo="string"):
    return {"id": str(uuid.uuid4()), "leftValue": izq, "rightValue": der,
            "operator": {"type": tipo, "operation": "equals"}}


def si(nombre, pos, conds, comb="and"):
    return nodo(nombre, "n8n-nodes-base.if", 2, pos, {
        "conditions": {"options": {"caseSensitive": True, "version": 2,
                                   "typeValidation": "loose"},
                       "combinator": comb, "conditions": conds},
        "options": {}})


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    js_eval = JS_EVALUAR.replace("__ETAPAS__",
                                 json.dumps(ETAPAS, ensure_ascii=False, indent=2))
    nodes = [
        nodo("Webhook inbound", "n8n-nodes-base.webhook", 2, [-1180, 0],
             {"httpMethod": "POST", "path": WEBHOOK_PATH, "authentication": "headerAuth",
              "responseMode": "responseNode", "options": {}},
             webhookId=str(uuid.uuid4()), credentials=CRED_WEBHOOK),
        nodo("Normalizar entrada", "n8n-nodes-base.code", 2, [-960, 0],
             {"jsCode": JS_NORMALIZAR.strip()}),
        pg("Idempotencia", [-740, 0], SQL_IDEMPOTENCIA,
           "={{ [ $json.messageId ] }}", siempre=True),
        si("¿Mensaje nuevo?", [-520, 0],
           [{"id": str(uuid.uuid4()), "leftValue": "={{ $json.message_id }}",
             "rightValue": "", "operator": {"type": "string", "operation": "exists"}}]),
        nodo("Responder ack", "n8n-nodes-base.respondToWebhook", 1.1, [-300, -140], {
            "respondWith": "json",
            "responseBody": '={{ JSON.stringify({ok: true, aceptado: true, '
                            'messageId: $(\'Normalizar entrada\').first().json.messageId}) }}',
            "options": {}}),
        nodo("Responder duplicado", "n8n-nodes-base.respondToWebhook", 1.1, [-300, 160], {
            "respondWith": "json",
            "responseBody": '={{ JSON.stringify({ok: true, aceptado: false, '
                            'motivo: "duplicado", messageId: '
                            '$(\'Normalizar entrada\').first().json.messageId}) }}',
            "options": {}}),
        nodo("Fin · duplicado", "n8n-nodes-base.noOp", 1, [-80, 160], {}),
        pg("Resolver identidad", [-80, -140], SQL_IDENTIDAD,
           "={{ [ $('Normalizar entrada').first().json.contactId, "
           "$('Normalizar entrada').first().json.phone || '' ] }}"),
        w0("W0 · find or create", [140, -140], "find_or_create_opportunity",
           "={{ JSON.stringify({contactId: $('Normalizar entrada').first().json.contactId, "
           "name: 'WhatsApp ' + ($('Normalizar entrada').first().json.phone || "
           "$('Normalizar entrada').first().json.contactId)}) }}"),
        w0("W0 · leer oportunidad", [360, -140], "get_opportunity",
           "={{ JSON.stringify({opportunityId: $json.data.opportunity.id}) }}"),
        nodo("Evaluar estado", "n8n-nodes-base.code", 2, [580, -140],
             {"jsCode": js_eval.strip()}),
        nodo("Ruteo por estado", "n8n-nodes-base.switch", 3, [800, -140], {
            "rules": {"values": [
                {"conditions": {"options": {"caseSensitive": True, "version": 2,
                                            "typeValidation": "loose"},
                                "combinator": "and",
                                "conditions": [cond_ig("={{ $json.ruta }}", "bloqueado")]},
                 "renameOutput": True, "outputKey": "bloqueado"},
                {"conditions": {"options": {"caseSensitive": True, "version": 2,
                                            "typeValidation": "loose"},
                                "combinator": "and",
                                "conditions": [cond_ig("={{ $json.ruta }}", "cliente_vuelve")]},
                 "renameOutput": True, "outputKey": "cliente_vuelve"},
                {"conditions": {"options": {"caseSensitive": True, "version": 2,
                                            "typeValidation": "loose"},
                                "combinator": "and",
                                "conditions": [cond_ig("={{ $json.ruta }}", "seguir")]},
                 "renameOutput": True, "outputKey": "seguir"},
            ]}, "options": {}}),
        nodo("Fin · agente en silencio", "n8n-nodes-base.noOp", 1, [1020, -320], {}),
        # STUB L7: acá van el volcado a notas_postventa y el reset a Lead Nuevo
        nodo("Reciclar oportunidad (stub)", "n8n-nodes-base.noOp", 1, [1020, -140], {}),
        nodo("Debounce · push", "n8n-nodes-base.redis", 1, [1020, 40], {
            "operation": "push", "list": "={{ 'hpf:' + $json.contactId }}",
            "messageData": "={{ $json.messageId }}", "tail": True},
            credentials=CRED_REDIS),
        nodo("Debounce · esperar", "n8n-nodes-base.wait", 1.1, [1240, 40],
             {"amount": "={{ $('Evaluar estado').first().json.debounce_seg }}",
              "unit": "seconds"}, webhookId=str(uuid.uuid4())),
        nodo("Debounce · leer", "n8n-nodes-base.redis", 1, [1460, 40], {
            "operation": "get", "propertyName": "Mensajes",
            "key": "={{ $('Evaluar estado').first().json.contactId ? "
                   "'hpf:' + $('Evaluar estado').first().json.contactId : '' }}",
            "options": {}}, credentials=CRED_REDIS),
        nodo("¿Soy el último?", "n8n-nodes-base.code", 2, [1680, 40],
             {"jsCode": JS_ULTIMO.strip()}),
        si("Gana el último", [1900, 40],
           [{"id": str(uuid.uuid4()), "leftValue": "={{ $json.soy_el_ultimo }}",
             "rightValue": True, "operator": {"type": "boolean", "operation": "true",
                                              "singleValue": True}}]),
        nodo("Debounce · limpiar", "n8n-nodes-base.redis", 1, [2120, -60], {
            "operation": "delete",
            "key": "={{ 'hpf:' + $json.contactId }}"}, credentials=CRED_REDIS),
        nodo("Fin · superado por otro mensaje", "n8n-nodes-base.noOp", 1, [2120, 160], {}),
        nodo("W6 · conversación", "n8n-nodes-base.executeWorkflow", 1.2, [2340, -60], {
            "workflowId": {"__rl": True, "value": W6_ID, "mode": "id",
                           "cachedResultName": "HPF·GHL · W6 Conversación"},
            "workflowInputs": {"mappingMode": "defineBelow", "value": {
                "sessionId": "={{ $json.sessionId }}",
                "contactId": "={{ $json.contactId }}",
                "opportunityId": "={{ $json.opportunityId }}",
                "texto": "={{ $json.texto }}",
                "primer_contacto": "={{ $json.etapa === 'Lead Nuevo' }}"},
                "matchingColumns": [], "schema": [], "attemptToConvertTypes": False,
                "convertFieldsToString": True},
            "options": {"waitForSubWorkflow": True}}),
        nodo("W2 · enviar", "n8n-nodes-base.executeWorkflow", 1.2, [2560, -60], {
            "workflowId": {"__rl": True, "value": W2_ID, "mode": "id",
                           "cachedResultName": "HPF·GHL · W2 Salida"},
            "workflowInputs": {"mappingMode": "defineBelow", "value": {
                "contactId": "={{ $('Evaluar estado').first().json.contactId }}",
                "partes": "={{ JSON.stringify($json.partes) }}",
                "pausa_seg": "={{ $('Normalizar entrada').first().json.debounce_seg > 0 ? 2 : 0 }}"},
                "matchingColumns": [], "schema": [], "attemptToConvertTypes": False,
                "convertFieldsToString": True},
            "options": {"waitForSubWorkflow": True}}),
        nodo("Evidencia del turno", "n8n-nodes-base.code", 2, [2780, -60],
             {"jsCode": JS_EVIDENCIA.strip()}),
        nodo("Fin · procesado", "n8n-nodes-base.noOp", 1, [3000, -60], {}),
    ]

    C = {
        "Webhook inbound": [["Normalizar entrada"]],
        "Normalizar entrada": [["Idempotencia"]],
        "Idempotencia": [["¿Mensaje nuevo?"]],
        "¿Mensaje nuevo?": [["Responder ack"], ["Responder duplicado"]],
        "Responder duplicado": [["Fin · duplicado"]],
        "Responder ack": [["Resolver identidad"]],
        "Resolver identidad": [["W0 · find or create"]],
        "W0 · find or create": [["W0 · leer oportunidad"]],
        "W0 · leer oportunidad": [["Evaluar estado"]],
        "Evaluar estado": [["Ruteo por estado"]],
        "Ruteo por estado": [["Fin · agente en silencio"],
                             ["Reciclar oportunidad (stub)"],
                             ["Debounce · push"]],
        "Reciclar oportunidad (stub)": [["Debounce · push"]],
        "Debounce · push": [["Debounce · esperar"]],
        "Debounce · esperar": [["Debounce · leer"]],
        "Debounce · leer": [["¿Soy el último?"]],
        "¿Soy el último?": [["Gana el último"]],
        "Gana el último": [["Debounce · limpiar"], ["Fin · superado por otro mensaje"]],
        "Debounce · limpiar": [["W6 · conversación"]],
        "W6 · conversación": [["W2 · enviar"]],
        "W2 · enviar": [["Evidencia del turno"]],
        "Evidencia del turno": [["Fin · procesado"]],
    }
    conexiones = {src: {"main": [[{"node": d, "type": "main", "index": 0} for d in br]
                                 for br in brs]} for src, brs in C.items()}

    wf = {"name": "HPF·GHL · W1 Inbound", "nodes": nodes, "connections": conexiones,
          "settings": {"executionOrder": "v1"}}
    p = OUT / "W1-inbound.json"
    p.write_text(json.dumps(wf, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ {p.relative_to(REPO)}  ({len(nodes)} nodos)")
    print(f"   webhook: POST /webhook/{WEBHOOK_PATH}")


if __name__ == "__main__":
    main()
