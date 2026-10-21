#!/usr/bin/env python3
"""
HPF · L3 — Genera W0 · GHL Client: el ÚNICO workflow que habla con GHL.

Por qué existe: en el intento anterior, un `toolHttpRequest` que fallaba contra GHL
le devolvía el texto del error al LLM como si fuera un resultado válido, dejando el
nodo en verde (ver 06_docs/fix-tools-ghl-404-demo-telegram-2026-07-24.md). Con W0 eso
es imposible: nadie pega a GHL directo, y un no-2xx corta la ejecución con throw.

Contratos codificados acá salen de L2, todos corroborados con read-back real:
  · User-Agent obligatorio      → sin él Cloudflare devuelve 403 error_code 1010
  · find_or_create              → POST optimista; 400 OPPORTUNITY_NO_DUPLICATE trae meta.existingId
  · /opportunities/search       → snake_case (camelCase da 422) y tiene lag de indexación
  · update_cf                   → GHL ignora en silencio un id desconocido y devuelve 200:
                                  por eso se valida la clave ANTES de mandar

Salida: clients/HPF_HappyFlops/03_workflows/ghl/W0-ghl-client.json
"""
import json
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "clients/HPF_HappyFlops/03_workflows/ghl"

CRED_GHL = {"httpHeaderAuth": {"id": "Zz21t1RdLIMvud4j", "name": "GHL PIT HPF"}}
# El webhook de prueba escribe en GHL con nuestro PIT: va con header auth, no abierto.
CRED_WEBHOOK = {"httpHeaderAuth": {"id": "jUb7ZjztncX5ACpc", "name": "HPF GHL Webhook Auth"}}
WEBHOOK_PATH = "hpf-w0-ghl-client"

# ── Contrato: campos custom de oportunidad (los 36 reales de la sub-cuenta).
# Se declara el tipo porque CHECKBOX y MULTIPLE_OPTIONS exigen array.
CF = {
    "cantidad_cilindros": ("1Xo6QgstbpNRu0TiKM7d", "NUMERICAL"),
    "diseno_aprobado_at": ("3Qo691OqUvdHgy19Mu9t", "DATE"),
    "imagen_input": ("4zvcyl95qQpnJOpKx6wy", "CHECKBOX"),
    "last_inbound_at": ("5KDgrZMK7pha8oO0VmJt", "TEXT"),
    "comprobante_anticipo_at": ("7P3cnSOeLJSovzI6m6XM", "TEXT"),
    "payment_proof_detectado": ("7U96fnkNbLy1Bj2BQ4Gr", "CHECKBOX"),
    "time_to_close_hours": ("7XcZT790aiApLPE7bACF", "NUMERICAL"),
    "re_engagement_completed_at": ("B3nrry4BcwtJGWyQxCPi", "DATE"),
    "cotizacion_anticipo_mxn": ("BKXYT8Bv4lxJy2durCC0", "NUMERICAL"),
    "talla_sandalias": ("HN7EV1XOh5XjsSlC8Bq9", "TEXT"),
    "productos_mostrados": ("IukLzqy6bZCCtuJTPzBu", "LARGE_TEXT"),
    "cantidad_mandiles": ("KZp0egPZZpdPk16bUMLW", "NUMERICAL"),
    "cantidad_sandalias": ("L68MYmGDZhLMbVU3VxMb", "NUMERICAL"),
    "had_information": ("NaqWKjsZrYLN0mGsV6U2", "CHECKBOX"),
    "paqueteria": ("RXAZLR1JFyFchlSI6a5V", "TEXT"),
    "notas_postventa": ("SQNM1WOMu42dtFoB74jj", "LARGE_TEXT"),
    "attention_motive": ("TTjvs6uXHwppBxbyab2y", "TEXT"),
    "tracking_number": ("VvfK034u8gXfHu5U8O2f", "TEXT"),
    "fecha_prometida_envio": ("WKVYhWFzJNmNgYJRBV5F", "DATE"),
    "cotizacion_emitida": ("WvS1z4CvV6UTVU7ZpL6p", "CHECKBOX"),
    "cantidad_otros": ("XxGTN1MLWhBFBEGHLDo6", "NUMERICAL"),
    "last_outbound_at": ("YUoSJZklOjsnh6l3KgmV", "TEXT"),
    "evento_detectado": ("ahVpF5ldsRcuOIn9Mxdk", "MULTIPLE_OPTIONS"),
    "created_at_first_contact": ("bAu2xA3TBx2vCLTFVpv7", "DATE"),
    "ultima_imagen_clasificada": ("dseuLadHs3dRLup2sRIV", "TEXT"),
    "cp_entrega": ("dwqVZEekKwE3sNSnWvvi", "TEXT"),
    "cotizacion_generada_at": ("ewuFioQF7h26yD5fN7U2", "DATE"),
    "tipo_suela": ("i8zWb498oK7SSOulvM9g", "SINGLE_OPTIONS"),
    "comprobante_liquidacion_url": ("iqZFq6sIoabZq5Vrjx1i", "TEXT"),
    "last_re_engagement_wave": ("j8xbPFvAnlowIcC9ZzmC", "TEXT"),
    "had_image": ("k4jHbS2HHH3d74Z7121a", "CHECKBOX"),
    "time_to_quote_hours": ("oUDC43WUGiKhTkN3Sg42", "NUMERICAL"),
    "comprobante_anticipo_url": ("te6n4eJtmKLg0Nktk3za", "TEXT"),
    "monto_cotizado_mxn": ("xznzWZlvPHQI3HdsQfzM", "NUMERICAL"),
    "comprobante_liquidacion_at": ("yLakDK5rk5lX2fxc0PZi", "TEXT"),
    "had_quote": ("zMaaLTYTREw2InLnbimW", "CHECKBOX"),
}

STAGES = {
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

JS_ENTRADA = """
// Unifica las dos vías de entrada: sub-workflow y webhook de prueba.
// El carril de test y el de producción comparten TODO lo de abajo: la única
// diferencia es por dónde entró el pedido.
const out = [];
for (const it of $input.all()) {
  const j = it.json || {};
  const porWebhook = !!(j.body && (j.body.op !== undefined));
  const src = porWebhook ? j.body : j;
  if (!src.op) {
    throw new Error('W0: falta el argumento "op" en el pedido');
  }
  let args = src.args ?? {};
  if (typeof args === 'string') {
    try { args = JSON.parse(args); }
    catch (e) { throw new Error('W0: "args" no es JSON válido: ' + args); }
  }
  out.push({ json: { op: String(src.op), args, _via: porWebhook ? 'webhook' : 'subworkflow' } });
}
return out;
"""

JS_REQUEST = """
// Tabla de contratos GHL. Todo lo de acá fue corroborado en L2 con read-back real
// (ver 07_testing/evidencia-migracion/L2-informe-primitivas.md).
const API      = 'https://services.leadconnectorhq.com';
const LOC      = 'onRwi0ZF4uYi0Lp6GAbE';
const PIPELINE = 'RMnhLPqtXoWUBGZ0gvbh';
const STAGES   = __STAGES__;
const CF       = __CF__;

const { op, args, _via } = $input.first().json;

function exigir(campos) {
  for (const c of campos) {
    const v = args[c];
    if (v === undefined || v === null || v === '') {
      throw new Error(`W0 op "${op}": falta el argumento obligatorio "${c}"`);
    }
  }
}

function idEtapa(nombre) {
  if (STAGES[nombre]) return STAGES[nombre];
  // permitir pasar el UUID directo
  if (Object.values(STAGES).includes(nombre)) return nombre;
  throw new Error(`W0: etapa desconocida "${nombre}" (${Object.keys(STAGES).length} válidas)`);
}

// Traduce {clave: valor} a customFields[], validando la clave contra el schema.
// Sin esto, un id con typo se escribe "bien" (GHL devuelve 200) y el dato se pierde
// en silencio — comprobado en T-17.
function camposCustom(campos) {
  const salida = [];
  for (const [clave, valor] of Object.entries(campos)) {
    const def = CF[clave];
    if (!def) {
      // Mensaje corto a propósito: n8n trunca los errores largos por el final.
      throw new Error(`W0: campo custom desconocido "${clave}" ` +
        `(${Object.keys(CF).length} válidos) — GHL lo aceptaría y perdería el dato`);
    }
    const [id, tipo] = def;
    let v = valor;
    if (tipo === 'CHECKBOX' || tipo === 'MULTIPLE_OPTIONS') {
      v = Array.isArray(v) ? v : [v];
    }
    salida.push({ id, field_value: v });
  }
  return salida;
}

// pageLimit 100 trae el catálogo entero en una sola llamada. (El 403 que se le
// atribuía a pageLimit>20 en los docs previos era en realidad el User-Agent.)
function buscarObjeto(objectKey) {
  return { method: 'POST', path: `/objects/${objectKey}/records/search`, body: {
    locationId: LOC, page: args.page || 1, pageLimit: args.pageLimit || 100,
    query: args.query || '', searchAfter: args.searchAfter || [] } };
}

const OPS = {
  upsert_contact: () => {
    exigir(['phone']);
    return { method: 'POST', path: '/contacts/upsert', body: {
      locationId: LOC, phone: args.phone,
      firstName: args.firstName, lastName: args.lastName, name: args.name,
      tags: args.tags, source: args.source || 'hpf-n8n' } };
  },
  get_contact: () => {
    exigir(['contactId']);
    return { method: 'GET', path: `/contacts/${args.contactId}` };
  },
  find_or_create_opportunity: () => {
    exigir(['contactId']);
    // POST optimista: es autoritativo y SIN lag, a diferencia de /opportunities/search.
    return { method: 'POST', path: '/opportunities/', body: {
      pipelineId: PIPELINE, locationId: LOC, contactId: args.contactId,
      name: args.name || 'Lead WhatsApp', status: 'open',
      pipelineStageId: idEtapa(args.etapa || 'Lead Nuevo') } };
  },
  get_opportunity: () => {
    exigir(['opportunityId']);
    return { method: 'GET', path: `/opportunities/${args.opportunityId}` };
  },
  update_stage: () => {
    exigir(['opportunityId', 'etapa']);
    return { method: 'PUT', path: `/opportunities/${args.opportunityId}`,
      body: { pipelineId: PIPELINE, pipelineStageId: idEtapa(args.etapa) } };
  },
  update_cf: () => {
    exigir(['opportunityId', 'campos']);
    return { method: 'PUT', path: `/opportunities/${args.opportunityId}`,
      body: { customFields: camposCustom(args.campos) } };
  },
  add_tag: () => {
    exigir(['contactId', 'tags']);
    return { method: 'POST', path: `/contacts/${args.contactId}/tags`,
      body: { tags: Array.isArray(args.tags) ? args.tags : [args.tags] } };
  },
  remove_tag: () => {
    exigir(['contactId', 'tags']);
    return { method: 'DELETE', path: `/contacts/${args.contactId}/tags`,
      body: { tags: Array.isArray(args.tags) ? args.tags : [args.tags] } };
  },
  send_text: () => {
    exigir(['contactId', 'mensaje']);
    return { method: 'POST', path: '/conversations/messages', body: {
      type: 'WhatsApp', contactId: args.contactId, message: args.mensaje } };
  },
  send_media: () => {
    exigir(['contactId', 'adjuntos']);
    const adj = Array.isArray(args.adjuntos) ? args.adjuntos : [args.adjuntos];
    return { method: 'POST', path: '/conversations/messages', body: {
      type: 'WhatsApp', contactId: args.contactId,
      message: args.mensaje || '', attachments: adj } };
  },
  search_products: () => buscarObjeto('custom_objects.productos'),
  // Fichas de catálogo: las ~65 tarjetas que el bot manda (texto + asset).
  // Objeto aparte de `productos`, que son los 15 SKU con precio/mínimo/peso.
  search_fichas: () => buscarObjeto('custom_objects.fichas'),
};

if (!OPS[op]) {
  throw new Error(`W0: op desconocida "${op}" (${Object.keys(OPS).length} válidas)`);
}
const spec = OPS[op]();
// limpia claves undefined para no mandar nulls que GHL interpreta como borrado
if (spec.body) {
  for (const k of Object.keys(spec.body)) if (spec.body[k] === undefined) delete spec.body[k];
}
return [{ json: { op, _via, _req: { ...spec, url: API + spec.path } } }];
"""

JS_SALIDA = """
// La evidencia es el status real, no que el nodo haya quedado verde.
const r    = $input.first().json;
const ctx  = $('Construir request').first().json;
const spec = ctx._req;
const op   = ctx.op;

const status = r.statusCode ?? 0;
let data = r.body;
if (typeof data === 'string') { try { data = JSON.parse(data); } catch (e) { /* queda como texto */ } }

const ok = status >= 200 && status < 300;

// Único no-2xx que NO es un error: el contacto ya tenía oportunidad.
// GHL devuelve el id existente en meta.existingId — autoritativo y sin lag.
if (!ok && op === 'find_or_create_opportunity' && data && data.code === 'OPPORTUNITY_NO_DUPLICATE') {
  return [{ json: { ok: true, op, http_status: status, via: 'existente',
    data: { opportunity: { id: data.meta.existingId } }, error: null } }];
}

if (!ok) {
  // throw a propósito: que reviente acá y no que el LLM reciba el error como resultado.
  throw new Error(`W0 ${op}: GHL ${spec.method} ${spec.path} → HTTP ${status} :: ` +
    JSON.stringify(data).slice(0, 500));
}

return [{ json: { ok: true, op, http_status: status,
  via: op === 'find_or_create_opportunity' ? 'creada' : null, data, error: null } }];
"""


def nodo(nombre, tipo, tv, pos, params, **extra):
    n = {"parameters": params, "id": str(uuid.uuid4()), "name": nombre,
         "type": tipo, "typeVersion": tv, "position": pos}
    n.update(extra)
    return n


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    js_req = (JS_REQUEST
              .replace("__STAGES__", json.dumps(STAGES, ensure_ascii=False, indent=2))
              .replace("__CF__", json.dumps(CF, ensure_ascii=False, indent=2)))

    nodes = [
        nodo("Ejecutado por otro workflow", "n8n-nodes-base.executeWorkflowTrigger", 1.1,
             [-460, 0], {"inputSource": "jsonExample",
                         "jsonExample": json.dumps({"op": "get_opportunity",
                                                    "args": {"opportunityId": "..."}}, indent=2)}),
        nodo("Webhook (carril de prueba)", "n8n-nodes-base.webhook", 2,
             [-460, 200], {"httpMethod": "POST", "path": WEBHOOK_PATH,
                           "authentication": "headerAuth",
                           "responseMode": "responseNode", "options": {}},
             webhookId=str(uuid.uuid4()), credentials=CRED_WEBHOOK),
        nodo("Normalizar entrada", "n8n-nodes-base.code", 2, [-220, 100],
             {"jsCode": JS_ENTRADA.strip()}),
        nodo("Construir request", "n8n-nodes-base.code", 2, [0, 100],
             {"jsCode": js_req.strip()}),
        nodo("GHL", "n8n-nodes-base.httpRequest", 4.2, [240, 100], {
            "method": "={{ $json._req.method }}",
            "url": "={{ $json._req.url }}",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "sendHeaders": True,
            "headerParameters": {"parameters": [
                {"name": "Version", "value": "2021-07-28"},
                {"name": "Accept", "value": "application/json"},
                # Sin User-Agent explícito, Cloudflare responde 403 error_code 1010
                # (browser_signature_banned). Corroborado en L2.
                {"name": "User-Agent", "value": "hpf-n8n/1.0"},
            ]},
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify($json._req.body || {}) }}",
            "options": {"response": {"response": {"fullResponse": True, "neverError": True}}},
        }, credentials=CRED_GHL),
        nodo("Normalizar salida", "n8n-nodes-base.code", 2, [480, 100],
             {"jsCode": JS_SALIDA.strip()}),
        nodo("¿Vino por webhook?", "n8n-nodes-base.if", 2, [700, 100], {
            "conditions": {"options": {"caseSensitive": True, "version": 2,
                                       "typeValidation": "loose"},
                           "combinator": "and",
                           "conditions": [{
                               "id": str(uuid.uuid4()),
                               "leftValue": "={{ $('Normalizar entrada').first().json._via }}",
                               "rightValue": "webhook",
                               "operator": {"type": "string", "operation": "equals"}}]},
            "options": {}}),
        nodo("Respond to Webhook", "n8n-nodes-base.respondToWebhook", 1.1, [940, 0],
             {"respondWith": "allIncomingItems", "options": {}}),
        # n8n devuelve al llamador la salida del ÚLTIMO NODO EJECUTADO. Si la rama
        # termina en una salida de IF sin nada conectado, devuelve [] y el workflow
        # de arriba se corta en silencio. Este noOp es el nodo terminal explícito.
        nodo("Devolver al llamador", "n8n-nodes-base.noOp", 1, [940, 200], {}),
    ]

    conexiones = {
        "Ejecutado por otro workflow": {"main": [[{"node": "Normalizar entrada", "type": "main", "index": 0}]]},
        "Webhook (carril de prueba)": {"main": [[{"node": "Normalizar entrada", "type": "main", "index": 0}]]},
        "Normalizar entrada": {"main": [[{"node": "Construir request", "type": "main", "index": 0}]]},
        "Construir request": {"main": [[{"node": "GHL", "type": "main", "index": 0}]]},
        "GHL": {"main": [[{"node": "Normalizar salida", "type": "main", "index": 0}]]},
        "Normalizar salida": {"main": [[{"node": "¿Vino por webhook?", "type": "main", "index": 0}]]},
        "¿Vino por webhook?": {"main": [
            [{"node": "Respond to Webhook", "type": "main", "index": 0}],
            [{"node": "Devolver al llamador", "type": "main", "index": 0}],
        ]},
    }

    wf = {"name": "HPF·GHL · W0 Client", "nodes": nodes, "connections": conexiones,
          "settings": {"executionOrder": "v1"}}
    p = OUT / "W0-ghl-client.json"
    p.write_text(json.dumps(wf, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ {p.relative_to(REPO)}  ({len(nodes)} nodos, {len(CF)} campos custom, "
          f"{len(STAGES)} etapas)")
    print(f"   webhook de prueba: POST /webhook/{WEBHOOK_PATH}")


if __name__ == "__main__":
    main()
