#!/usr/bin/env python3
"""
HPF · W11 — Puente Telegram → stack nuevo.

POR QUÉ EXISTE (14/08)
Se descubrió que veníamos corriendo dos sistemas en paralelo sin saberlo:

  · Oscar, Camilo y la agencia testeaban por Telegram → eso entra por el `telegramTrigger` de
    `HPF Inbound Handler` (id IPO1c36NLzkXrBh9, 71 nodos), que es el build VIEJO.
  · Todos los arreglos de los últimos días se aplicaron al stack NUEVO (W0…W10), cuyo
    único ingreso es el webhook de W1 o el polling de conversaciones de GHL de W8.

O sea que la reunión con Oscar, las correcciones de Camilo y los tests de la agencia se hicieron
sobre un agente distinto del que se venía arreglando. Este puente cierra esa brecha: hace que
Telegram entre al stack nuevo.

QUÉ HACE
Telegram → normaliza → W6 (el cerebro) → devuelve cada burbuja a Telegram, respetando el
orden y los adjuntos (foto / documento / video según el tipo de media de la ficha).

ALCANCE — leer esto antes de sacar conclusiones de un test
Este puente ejerce **W6**, que es donde viven TODOS los arreglos que se hicieron: saludo,
negritas, evento persistente, pantufla de peluche, marcador de pago, link de Maps. NO ejerce
W1 (debounce, audio, etapas, seguimientos) ni W2 (envío por GHL), porque esos dependen de que
el contacto exista en GHL y crearían registros de prueba en el CRM del cliente.

Dicho de otra forma: sirve para validar lo que Oscar evalúa (qué contesta y qué imágenes
manda). No sustituye una prueba del pipeline completo antes del go-live.

Uso:
    hpf-gen-w11-puente-telegram.py            # crea o actualiza el workflow (inactivo)
    hpf-gen-w11-puente-telegram.py --activar  # además lo activa y apaga el trigger del viejo
"""
import importlib.util
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "hpfdeploy", REPO / "scripts/utilities/hpf-deploy-workflow.py")
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)

NOMBRE = "HPF·GHL · W11 Puente Telegram"
CRED_TG = {"telegramApi": {"id": "yXtgg8Djbxglxq9H", "name": "HPF"}}
W6_ID = "cNmJCP2qVhdtfCH0"
VIEJO = "IPO1c36NLzkXrBh9"

JS_NORMALIZAR = """// Telegram → el shape que espera W6.
// sessionId: se usa el chat id crudo. NO se le pone prefijo a propósito — así la
// conversación de Telegram y la del webhook de prueba comparten memoria y se puede
// comparar lo que ve el tester con lo que miden los scripts.
const j = $input.first().json || {};
const msg = j.message || j;
const chat = msg.chat || {};
const from = msg.from || {};
const chatId = String(chat.id ?? from.id ?? '');
if (!chatId) throw new Error('W11: mensaje de Telegram sin chat id');

const texto = String(msg.text || msg.caption || '').trim();
if (!texto) {
  // audio/foto/sticker: W6 sólo entiende texto. Se avisa y se corta, en vez de mandarle
  // una cadena vacía y que conteste cualquier cosa.
  return [{ json: { chatId, _sin_texto: true,
    aviso: 'Por ahora este canal de prueba sólo procesa texto.' } }];
}
return [{ json: {
  chatId,
  sessionId: chatId,
  texto,
  contactId: null,
  opportunityId: null,
  // primer_contacto lo resuelve W6 contando turnos humanos en la memoria; acá se manda
  // false y se deja que él decida, que es como entra desde W1.
  primer_contacto: false,
} }];"""

JS_PARTES = """// Aplana la respuesta de W6 a una lista de envíos para Telegram.
const chatId = $('Normalizar Telegram').first().json.chatId;
const r = $input.first().json || {};
const partes = r.partes || [];
if (!partes.length) {
  return [{ json: { chatId, tipo: 'texto', texto: 'Déjame revisar eso y te confirmo.' } }];
}
// El tipo de envío se decide por la extensión del asset, igual que en el handler viejo:
// una foto mandada como documento le llega al lead como archivo adjunto, no como imagen.
const tipoDe = (url) => {
  const u = String(url).toLowerCase().split('?')[0];
  if (/\\.(jpe?g|png|webp|gif)$/.test(u)) return 'foto';
  if (/\\.(mp4|mov|m4v)$/.test(u)) return 'video';
  return 'documento';
};
const out = [];
for (const p of partes) {
  const texto = String(p.texto || '').trim();
  const adj = p.adjuntos || [];
  if (!adj.length) {
    if (texto) out.push({ chatId, tipo: 'texto', texto });
    continue;
  }
  // el texto viaja como caption del primer adjunto, así llegan juntos
  adj.forEach((url, i) => out.push({
    chatId, tipo: tipoDe(url), url,
    texto: i === 0 ? texto : '',
  }));
}
return out.map(json => ({ json }));"""


def nodo(nombre, tipo, tv, pos, params, **extra):
    n = {"parameters": params, "type": tipo, "typeVersion": tv,
         "id": f"w11-{abs(hash(nombre)) % 10**12:012d}", "name": nombre, "position": pos}
    n.update(extra)
    return n


def construir():
    N = [
        # webhookId es OBLIGATORIO en un nodo trigger de Telegram: n8n lo usa para armar la
        # URL que registra en Telegram con setWebhook. Sin él el workflow se activa, no da
        # ningún error, y no llega NUNCA un mensaje. Pasó el 14/08 y costó un ciclo de test.
        # Es fijo, no aleatorio, para que regenerar no cambie la URL registrada.
        nodo("Telegram Trigger", "n8n-nodes-base.telegramTrigger", 1.2, [-720, 0],
             {"updates": ["message"], "additionalFields": {}}, credentials=CRED_TG,
             webhookId="7c1f0a94-9d3e-4f52-b6a8-2e5c1d0b3a77"),
        nodo("Normalizar Telegram", "n8n-nodes-base.code", 2, [-500, 0],
             {"jsCode": JS_NORMALIZAR}),
        nodo("¿Trae texto?", "n8n-nodes-base.if", 2.2, [-300, 0], {
            "conditions": {"options": {"caseSensitive": True, "version": 2,
                                       "typeValidation": "loose"},
                           "combinator": "and",
                           "conditions": [{"id": "c1",
                                           "leftValue": "={{ $json._sin_texto }}",
                                           "rightValue": True,
                                           "operator": {"type": "boolean",
                                                        "operation": "notEquals"}}]},
            "options": {}}),
        nodo("W6 · conversación", "n8n-nodes-base.executeWorkflow", 1.2, [-80, -100], {
            "workflowId": {"__rl": True, "value": W6_ID, "mode": "id",
                           "cachedResultName": "HPF·GHL · W6 Conversación"},
            "workflowInputs": {"mappingMode": "defineBelow", "value": {
                "sessionId": "={{ $json.sessionId }}",
                "contactId": "={{ $json.contactId }}",
                "opportunityId": "={{ $json.opportunityId }}",
                "texto": "={{ $json.texto }}",
                "primer_contacto": "={{ $json.primer_contacto }}"},
                "matchingColumns": [], "schema": [],
                "attemptToConvertTypes": False, "convertFieldsToString": True},
            "options": {"waitForSubWorkflow": True}}),
        nodo("Aplanar burbujas", "n8n-nodes-base.code", 2, [140, -100],
             {"jsCode": JS_PARTES}),
        nodo("Recorrer envíos", "n8n-nodes-base.splitInBatches", 3, [360, -100],
             {"batchSize": 1, "options": {}}),
        nodo("Ruteo por tipo", "n8n-nodes-base.switch", 3.2, [580, 60], {
            "rules": {"values": [
                {"conditions": {"options": {"caseSensitive": True, "version": 2,
                                            "typeValidation": "loose"},
                                "combinator": "and",
                                "conditions": [{"leftValue": "={{ $json.tipo }}",
                                                "rightValue": "texto",
                                                "operator": {"type": "string",
                                                             "operation": "equals"}}]},
                 "outputKey": "texto"},
                {"conditions": {"options": {"caseSensitive": True, "version": 2,
                                            "typeValidation": "loose"},
                                "combinator": "and",
                                "conditions": [{"leftValue": "={{ $json.tipo }}",
                                                "rightValue": "foto",
                                                "operator": {"type": "string",
                                                             "operation": "equals"}}]},
                 "outputKey": "foto"},
                {"conditions": {"options": {"caseSensitive": True, "version": 2,
                                            "typeValidation": "loose"},
                                "combinator": "and",
                                "conditions": [{"leftValue": "={{ $json.tipo }}",
                                                "rightValue": "video",
                                                "operator": {"type": "string",
                                                             "operation": "equals"}}]},
                 "outputKey": "video"}]},
            "options": {"fallbackOutput": 3, "renameFallbackOutput": "documento"}}),
        nodo("Enviar texto", "n8n-nodes-base.telegram", 1.2, [820, -120], {
            "chatId": "={{ $json.chatId }}", "text": "={{ $json.texto }}",
            "additionalFields": {"appendAttribution": False}}, credentials=CRED_TG),
        nodo("Enviar foto", "n8n-nodes-base.telegram", 1.2, [820, 20], {
            "operation": "sendPhoto", "chatId": "={{ $json.chatId }}",
            "file": "={{ $json.url }}",
            # `file` y no `fileId`: fileId es de resource:file/operation:get y n8n descarta
            # la clave desconocida al guardar — es el bug que dejó el handler viejo sin
            # mandar ninguna foto durante semanas.
            "additionalFields": {"caption": "={{ $json.texto }}",
                                 "appendAttribution": False}}, credentials=CRED_TG),
        nodo("Enviar video", "n8n-nodes-base.telegram", 1.2, [820, 160], {
            "operation": "sendVideo", "chatId": "={{ $json.chatId }}",
            "file": "={{ $json.url }}",
            "additionalFields": {"caption": "={{ $json.texto }}",
                                 "appendAttribution": False}}, credentials=CRED_TG),
        nodo("Enviar documento", "n8n-nodes-base.telegram", 1.2, [820, 300], {
            "operation": "sendDocument", "chatId": "={{ $json.chatId }}",
            "binaryData": False, "file": "={{ $json.url }}",
            "additionalFields": {"caption": "={{ $json.texto }}",
                                 "appendAttribution": False}}, credentials=CRED_TG),
        nodo("Pausa entre burbujas", "n8n-nodes-base.wait", 1.1, [1060, 60],
             {"amount": 1, "unit": "seconds"}, webhookId="w11-wait-0001"),
        nodo("Avisar sin texto", "n8n-nodes-base.telegram", 1.2, [-80, 140], {
            "chatId": "={{ $json.chatId }}", "text": "={{ $json.aviso }}",
            "additionalFields": {"appendAttribution": False}}, credentials=CRED_TG),
    ]
    C = {
        "Telegram Trigger": {"main": [[{"node": "Normalizar Telegram", "type": "main", "index": 0}]]},
        "Normalizar Telegram": {"main": [[{"node": "¿Trae texto?", "type": "main", "index": 0}]]},
        "¿Trae texto?": {"main": [
            [{"node": "W6 · conversación", "type": "main", "index": 0}],
            [{"node": "Avisar sin texto", "type": "main", "index": 0}]]},
        "W6 · conversación": {"main": [[{"node": "Aplanar burbujas", "type": "main", "index": 0}]]},
        "Aplanar burbujas": {"main": [[{"node": "Recorrer envíos", "type": "main", "index": 0}]]},
        # salida 0 = done (no hace nada), salida 1 = loop. El orden importa: invertirlas
        # hace que el loop no procese nunca. Ya mordió en CLZ.
        "Recorrer envíos": {"main": [[], [{"node": "Ruteo por tipo", "type": "main", "index": 0}]]},
        "Ruteo por tipo": {"main": [
            [{"node": "Enviar texto", "type": "main", "index": 0}],
            [{"node": "Enviar foto", "type": "main", "index": 0}],
            [{"node": "Enviar video", "type": "main", "index": 0}],
            [{"node": "Enviar documento", "type": "main", "index": 0}]]},
        "Enviar texto": {"main": [[{"node": "Pausa entre burbujas", "type": "main", "index": 0}]]},
        "Enviar foto": {"main": [[{"node": "Pausa entre burbujas", "type": "main", "index": 0}]]},
        "Enviar video": {"main": [[{"node": "Pausa entre burbujas", "type": "main", "index": 0}]]},
        "Enviar documento": {"main": [[{"node": "Pausa entre burbujas", "type": "main", "index": 0}]]},
        "Pausa entre burbujas": {"main": [[{"node": "Recorrer envíos", "type": "main", "index": 0}]]},
    }
    return {"name": NOMBRE, "nodes": N, "connections": C,
            "settings": {"executionOrder": "v1"}}


def main():
    wf = construir()
    s, existentes = D.api("/api/v1/workflows?limit=250")
    prev = next((w for w in (existentes.get("data") or []) if w["name"] == NOMBRE), None)
    if prev:
        s, r = D.api(f"/api/v1/workflows/{prev['id']}", "PUT", wf)
        wid = prev["id"]
        print(f"actualizado {wid} ({s})")
    else:
        s, r = D.api("/api/v1/workflows", "POST", wf)
        if s not in (200, 201):
            sys.exit(f"❌ no pude crear: {s} {r}")
        wid = r["id"]
        print(f"creado {wid}")
    print(f"   {len(wf['nodes'])} nodos")

    if "--activar" not in sys.argv:
        print("\n(no activo nada; correr con --activar para conectar Telegram)")
        return

    # 1) apagar el trigger del viejo ANTES de activar el nuevo: Telegram admite un solo
    #    consumidor por token, y tener los dos prendidos deja el resultado al azar.
    s, viejo = D.api(f"/api/v1/workflows/{VIEJO}")
    tg = [n for n in viejo["nodes"] if n["type"].endswith("telegramTrigger")]
    for n in tg:
        n["disabled"] = True
    body = {k: viejo[k] for k in ("name", "nodes", "connections", "settings") if k in viejo}
    s, _ = D.api(f"/api/v1/workflows/{VIEJO}", "PUT", body)
    print(f"\n· trigger de Telegram del handler viejo: deshabilitado ({s})")
    s, _ = D.api(f"/api/v1/workflows/{VIEJO}/deactivate", "POST", {})
    print(f"· handler viejo desactivado ({s})")

    # 2) activar el puente
    s, _ = D.api(f"/api/v1/workflows/{wid}/activate", "POST", {})
    print(f"· puente activado ({s})")

    # 3) confirmar leyendo del vivo
    _, v = D.api(f"/api/v1/workflows/{wid}")
    _, o = D.api(f"/api/v1/workflows/{VIEJO}")
    otg = [n for n in o["nodes"] if n["type"].endswith("telegramTrigger")]
    print(f"\n  puente  activo={v.get('active')}  nodos={len(v['nodes'])}")
    print(f"  viejo   activo={o.get('active')}  trigger disabled={otg[0].get('disabled') if otg else '?'}")


if __name__ == "__main__":
    main()
