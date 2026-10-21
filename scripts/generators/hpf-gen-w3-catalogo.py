#!/usr/bin/env python3
"""
HPF · L5 — Genera W3 · Catálogo: resuelve qué fichas mandar.

Reemplaza del origen: `Formula` + `Search_Main_Image` + `Return_Formula` +
`Search_Products` + `Loop Over Items` + los parsers de la columna CURL de Airtable.

Por qué caché en Postgres y no consulta directa a GHL:
  · `records/search` de GHL tiene lag de indexación — comprobado dos veces (oportunidades
    y fichas). En el camino caliente de una conversación eso es inaceptable.
  · El filtro de Airtable era `AND({subcategoria}=X, OR(SEARCH(p1,...), SEARCH(p2,...)))`.
    En SQL eso es directo; en `records/search` no hay equivalente.
  · La memoria del agente ya vive en esa misma Postgres: una pieza menos que mantener.

El catálogo cambia cuando Oscar lo edita, o sea casi nunca: TTL de 15 min y refresco
perezoso (sólo cuando está vencido o vacío).

Salida: clients/HPF_HappyFlops/03_workflows/ghl/W3-catalogo.json
"""
import json
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "clients/HPF_HappyFlops/03_workflows/ghl"
W0_ID = "VK4M7VQm8CMefbty"
CRED_PG = {"postgres": {"id": "uK59P60DJmOJc4Lm", "name": "H.F"}}
CRED_WEBHOOK = {"httpHeaderAuth": {"id": "jUb7ZjztncX5ACpc", "name": "HPF GHL Webhook Auth"}}
WEBHOOK_PATH = "hpf-w3-catalogo"
TTL_SEG = 900

# DDL + estado en una sola ida: el workflow se autoinstala y no hay migración manual
# que alguien se olvide de correr.
SQL_ESTADO = """CREATE TABLE IF NOT EXISTS hpf_fichas (
  ficha_id      text PRIMARY KEY,
  nombre        text NOT NULL,
  evento        text,
  subcategoria  text,
  descripcion   text,
  media_url     text,
  media_tipo    text,
  bot_id_kommo  text,
  activo        boolean NOT NULL DEFAULT true,
  refrescado_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS hpf_fichas_evento_idx ON hpf_fichas (evento);
CREATE INDEX IF NOT EXISTS hpf_fichas_nombre_lower_idx ON hpf_fichas (lower(nombre));
SELECT count(*)::int AS n,
       COALESCE(EXTRACT(EPOCH FROM (now() - max(refrescado_at))), 1e9)::int AS edad_seg
FROM hpf_fichas;"""

# Upsert completo desde un jsonb. Va por parámetro para no pelear con comillas y
# saltos de línea de las descripciones. Borra en el mismo statement lo que ya no está
# en GHL, así el refresco es un reemplazo real y no una acumulación.
SQL_UPSERT = """WITH entrada AS (
  SELECT x->>'ficha_id' AS ficha_id, x->>'nombre' AS nombre, x->>'evento' AS evento,
         x->>'subcategoria' AS subcategoria, x->>'descripcion' AS descripcion,
         x->>'media_url' AS media_url, x->>'media_tipo' AS media_tipo,
         x->>'bot_id_kommo' AS bot_id_kommo, (x->>'activo')::boolean AS activo
  FROM jsonb_array_elements($1::jsonb) AS x
), borrados AS (
  DELETE FROM hpf_fichas WHERE ficha_id NOT IN (SELECT ficha_id FROM entrada)
)
INSERT INTO hpf_fichas (ficha_id, nombre, evento, subcategoria, descripcion,
                        media_url, media_tipo, bot_id_kommo, activo, refrescado_at)
SELECT ficha_id, nombre, evento, subcategoria, descripcion,
       media_url, media_tipo, bot_id_kommo, activo, now()
FROM entrada
ON CONFLICT (ficha_id) DO UPDATE SET
  nombre = EXCLUDED.nombre, evento = EXCLUDED.evento,
  subcategoria = EXCLUDED.subcategoria, descripcion = EXCLUDED.descripcion,
  media_url = EXCLUDED.media_url, media_tipo = EXCLUDED.media_tipo,
  bot_id_kommo = EXCLUDED.bot_id_kommo, activo = EXCLUDED.activo,
  refrescado_at = now();"""

# Réplica del filterByFormula de Airtable:
#   AND({subcategoria} = X, OR(SEARCH(p1, LOWER({productos})), SEARCH(p2, ...)))
SQL_CONSULTA = """SELECT ficha_id, nombre, evento, subcategoria, descripcion,
       media_url, media_tipo, bot_id_kommo
FROM hpf_fichas
WHERE ($1 = '' OR lower(evento) = lower($1))
  AND ($2 = '' OR lower(subcategoria) = lower($2))
  AND ($3::jsonb = '[]'::jsonb OR EXISTS (
        SELECT 1 FROM jsonb_array_elements_text($3::jsonb) AS t
        WHERE lower(nombre) LIKE '%' || lower(t) || '%'))
  AND activo
ORDER BY subcategoria NULLS FIRST, nombre;"""

JS_ENTRADA = """
// Entrada: { evento, subcategoria?, productos? }
//   evento       — Boda | XV | Otros  (o el nombre de la tabla origen)
//   subcategoria — "Producto Principal" | "Accesorios"  (vacío = ambas)
//   productos    — nombres sueltos a buscar (vacío = todas las del evento)
const j0 = $input.first().json || {};
const porWebhook = !!(j0.body && j0.body.evento !== undefined);
const src = porWebhook ? j0.body : j0;

let productos = src.productos ?? [];
if (typeof productos === 'string') {
  const t = productos.trim();
  productos = t.startsWith('[') ? JSON.parse(t) : (t ? [t] : []);
}
if (!Array.isArray(productos)) productos = [productos];
productos = productos.map(p => String(p).trim()).filter(Boolean);

return [{ json: {
  _via: porWebhook ? 'webhook' : 'subworkflow',
  evento: String(src.evento ?? '').trim(),
  subcategoria: String(src.subcategoria ?? '').trim(),
  productos,
  ttl_seg: src.ttl_seg !== undefined ? Number(src.ttl_seg) : __TTL__,
} }];
"""

JS_PREPARAR_UPSERT = """
// Aplana los records del custom object al shape de la tabla.
const recs = ($input.first().json.data || {}).records || [];
const filas = recs.map(r => {
  const p = r.properties || {};
  return {
    ficha_id: p.ficha_id || r.id,
    nombre: p.nombre || '',
    evento: p.evento || '',
    subcategoria: p.subcategoria || '',
    descripcion: p.descripcion || '',
    media_url: p.media_url || '',
    media_tipo: p.media_tipo || '',
    bot_id_kommo: p.bot_id_kommo || '',
    activo: String(p.activo).toLowerCase() !== 'false',
  };
}).filter(f => f.ficha_id && f.nombre);
if (filas.length === 0) {
  // Nunca vaciar la caché por una respuesta vacía de GHL: sería quedarse sin catálogo
  // en medio de una conversación.
  throw new Error('W3: GHL devolvió 0 fichas; no se refresca la caché');
}
return [{ json: { filas_json: JSON.stringify(filas), cantidad: filas.length } }];
"""

JS_CARDS = """
// Salida: una tarjeta por ficha, en el orden en que hay que mandarlas.
const filas = $input.all().map(i => i.json).filter(f => f && f.ficha_id);
const ctx = $('Normalizar entrada').first().json;
const cards = filas.map(f => ({
  ficha_id: f.ficha_id,
  nombre: f.nombre,
  texto: f.descripcion || '',
  media_url: f.media_url || null,
  media_tipo: f.media_tipo || null,
  subcategoria: f.subcategoria || null,
}));
const sin_media = cards.filter(c => !c.media_url).map(c => c.nombre);
return [{ json: {
  ok: true,
  evento: ctx.evento,
  subcategoria: ctx.subcategoria || null,
  productos_pedidos: ctx.productos,
  cantidad: cards.length,
  cards,
  // el llamador tiene que saber que estas fichas no tienen asset: su contenido
  // vivía sólo dentro del salesbot de Kommo
  sin_media,
} }];
"""


def nodo(nombre, tipo, tv, pos, params, **extra):
    n = {"parameters": params, "id": str(uuid.uuid4()), "name": nombre,
         "type": tipo, "typeVersion": tv, "position": pos}
    n.update(extra)
    return n


def pg(nombre, pos, query, replacement=None, siempre=False):
    p = {"operation": "executeQuery", "query": query, "options": {}}
    if replacement:
        p["options"] = {"queryReplacement": replacement}
    extra = {"credentials": CRED_PG}
    if siempre:
        # Con 0 filas el nodo no emite y la cadena se corta en silencio. "No hay ese
        # producto para ese evento" es un caso conversacional real, no un error.
        extra["alwaysOutputData"] = True
    return nodo(nombre, "n8n-nodes-base.postgres", 2.4, pos, p, **extra)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    nodes = [
        nodo("Ejecutado por otro workflow", "n8n-nodes-base.executeWorkflowTrigger", 1.1,
             [-700, 0], {"inputSource": "jsonExample", "jsonExample": json.dumps({
                 "evento": "Boda", "subcategoria": "Producto Principal",
                 "productos": ["sandalias", "cilindros"]}, indent=2, ensure_ascii=False)}),
        nodo("Webhook (carril de prueba)", "n8n-nodes-base.webhook", 2, [-700, 200],
             {"httpMethod": "POST", "path": WEBHOOK_PATH, "authentication": "headerAuth",
              "responseMode": "responseNode", "options": {}},
             webhookId=str(uuid.uuid4()), credentials=CRED_WEBHOOK),
        nodo("Normalizar entrada", "n8n-nodes-base.code", 2, [-460, 100],
             {"jsCode": JS_ENTRADA.replace("__TTL__", str(TTL_SEG)).strip()}),
        pg("Estado de caché", [-240, 100], SQL_ESTADO),
        nodo("¿Refrescar caché?", "n8n-nodes-base.if", 2, [-20, 100], {
            "conditions": {"options": {"caseSensitive": True, "version": 2,
                                       "typeValidation": "loose"},
                           "combinator": "or",
                           "conditions": [
                               {"id": str(uuid.uuid4()), "leftValue": "={{ $json.n }}",
                                "rightValue": 0,
                                "operator": {"type": "number", "operation": "equals"}},
                               {"id": str(uuid.uuid4()), "leftValue": "={{ $json.edad_seg }}",
                                "rightValue": "={{ $('Normalizar entrada').first().json.ttl_seg }}",
                                "operator": {"type": "number", "operation": "gt"}}]},
            "options": {}}),
        nodo("W0 · traer fichas", "n8n-nodes-base.executeWorkflow", 1.2, [220, -40], {
            "workflowId": {"__rl": True, "value": W0_ID, "mode": "id",
                           "cachedResultName": "HPF·GHL · W0 Client"},
            "workflowInputs": {"mappingMode": "defineBelow", "value": {
                "op": "search_fichas", "args": "={{ JSON.stringify({pageLimit: 100}) }}"},
                "matchingColumns": [], "schema": [], "attemptToConvertTypes": False,
                "convertFieldsToString": True},
            "options": {"waitForSubWorkflow": True}}),
        nodo("Aplanar fichas", "n8n-nodes-base.code", 2, [440, -40],
             {"jsCode": JS_PREPARAR_UPSERT.strip()}),
        pg("Refrescar caché", [660, -40], SQL_UPSERT,
           "={{ [ $json.filas_json ] }}"),
        pg("Consultar caché", [880, 100], SQL_CONSULTA,
           "={{ [ $('Normalizar entrada').first().json.evento, "
           "$('Normalizar entrada').first().json.subcategoria, "
           "JSON.stringify($('Normalizar entrada').first().json.productos) ] }}",
           siempre=True),
        nodo("Armar cards", "n8n-nodes-base.code", 2, [1100, 100],
             {"jsCode": JS_CARDS.strip()}),
        nodo("¿Vino por webhook?", "n8n-nodes-base.if", 2, [1320, 100], {
            "conditions": {"options": {"caseSensitive": True, "version": 2,
                                       "typeValidation": "loose"},
                           "combinator": "and",
                           "conditions": [{
                               "id": str(uuid.uuid4()),
                               "leftValue": "={{ $('Normalizar entrada').first().json._via }}",
                               "rightValue": "webhook",
                               "operator": {"type": "string", "operation": "equals"}}]},
            "options": {}}),
        nodo("Respond to Webhook", "n8n-nodes-base.respondToWebhook", 1.1, [1540, 0],
             {"respondWith": "allIncomingItems", "options": {}}),
        nodo("Devolver al llamador", "n8n-nodes-base.noOp", 1, [1540, 200], {}),
    ]

    conexiones = {
        "Ejecutado por otro workflow": {"main": [[{"node": "Normalizar entrada", "type": "main", "index": 0}]]},
        "Webhook (carril de prueba)": {"main": [[{"node": "Normalizar entrada", "type": "main", "index": 0}]]},
        "Normalizar entrada": {"main": [[{"node": "Estado de caché", "type": "main", "index": 0}]]},
        "Estado de caché": {"main": [[{"node": "¿Refrescar caché?", "type": "main", "index": 0}]]},
        "¿Refrescar caché?": {"main": [
            [{"node": "W0 · traer fichas", "type": "main", "index": 0}],
            [{"node": "Consultar caché", "type": "main", "index": 0}],
        ]},
        "W0 · traer fichas": {"main": [[{"node": "Aplanar fichas", "type": "main", "index": 0}]]},
        "Aplanar fichas": {"main": [[{"node": "Refrescar caché", "type": "main", "index": 0}]]},
        "Refrescar caché": {"main": [[{"node": "Consultar caché", "type": "main", "index": 0}]]},
        "Consultar caché": {"main": [[{"node": "Armar cards", "type": "main", "index": 0}]]},
        "Armar cards": {"main": [[{"node": "¿Vino por webhook?", "type": "main", "index": 0}]]},
        "¿Vino por webhook?": {"main": [
            [{"node": "Respond to Webhook", "type": "main", "index": 0}],
            [{"node": "Devolver al llamador", "type": "main", "index": 0}],
        ]},
    }

    wf = {"name": "HPF·GHL · W3 Catálogo", "nodes": nodes, "connections": conexiones,
          "settings": {"executionOrder": "v1"}}
    p = OUT / "W3-catalogo.json"
    p.write_text(json.dumps(wf, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ {p.relative_to(REPO)}  ({len(nodes)} nodos · TTL {TTL_SEG}s)")
    print(f"   webhook de prueba: POST /webhook/{WEBHOOK_PATH}")


if __name__ == "__main__":
    main()
