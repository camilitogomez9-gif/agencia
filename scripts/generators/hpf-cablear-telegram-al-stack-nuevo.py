#!/usr/bin/env python3
"""
HPF · cablear Telegram al stack nuevo (W1 entrada · W2 salida).

POR QUÉ
Hasta el 14/08 Telegram entraba al build VIEJO (`HPF Inbound Handler`) y el stack nuevo
sólo se podía tocar por el webhook de W1 o el polling de GHL de W8. O sea que Oscar, Camilo
y la agencia testeaban un agente y se arreglaba otro.

El primer intento fue un puente aparte (W11) que iba directo a W6. Servía para ver qué
contesta el bot, pero salteaba W1 (identidad, debounce, etapas, seguimientos) y W2 (envío),
que es justo el pipeline que va a correr en producción. Este cableado lo reemplaza:
**Telegram entra por W1 y sale por W2**, y todo lo demás sigue yendo a GHL sin cambios.

DISEÑO — la decisión que lo hace simple
El contrato de W1 exige un `contactId` de GHL. Un usuario de Telegram no tiene teléfono, así
que se le fabrica uno con el prefijo **+999**, que es un código de país sin asignar: no puede
colisionar con un número real de un lead. Con eso `upsert_contact` de W0 crea (o encuentra) un
contacto de verdad en GHL, y a partir de ahí el pipeline entero funciona igual que para
WhatsApp — misma oportunidad, mismas etapas, mismos custom fields.

Y como `hpf_identity` ya guarda `phone_e164` por contacto, **el chat id se recupera del
teléfono**: no hace falta ninguna tabla nueva. W2 mira el teléfono del contacto; si empieza
con +999, manda por Telegram en vez de por GHL.

QUÉ NO CAMBIA
Catálogo, estado del lead, etapas, custom fields, seguimientos: todo sigue yendo a GHL.
Lo único que cambia es por dónde entra y sale el mensaje.

Uso:
    hpf-cablear-telegram-al-stack-nuevo.py --dry-run
    hpf-cablear-telegram-al-stack-nuevo.py
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

CRED_TG = {"telegramApi": {"id": "yXtgg8Djbxglxq9H", "name": "HPF"}}
CRED_PG = {"postgres": {"id": "uK59P60DJmOJc4Lm", "name": "H.F"}}
W0_ID = "VK4M7VQm8CMefbty"
PREFIJO = "+999"          # código de país sin asignar: no colisiona con un lead real

# ── W1 · entrada ──────────────────────────────────────────────────────────────
JS_TG_A_GHL = """// Telegram → el payload que espera W1, que es el de GHL.
//
// W1 exige `contactId` de GHL y un usuario de Telegram no tiene teléfono, así que se le
// fabrica uno con el prefijo +999 (código de país SIN ASIGNAR: no puede pisar el número
// de un lead real). El nodo siguiente hace upsert_contact con ese teléfono y devuelve un
// contactId de verdad, así el resto del pipeline no se entera de que vino de Telegram.
//
// El mismo prefijo es lo que W2 mira después para decidir si responde por Telegram o por
// GHL — por eso no se puede cambiar acá sin cambiarlo allá.
const j = $input.first().json || {};
const msg = j.message || j;
const chat = msg.chat || {};
const from = msg.from || {};
const chatId = String(chat.id ?? from.id ?? '');
if (!chatId) throw new Error('W1/TG: mensaje de Telegram sin chat id');

const nombre = [from.first_name, from.last_name].filter(Boolean).join(' ')
             || from.username || ('Telegram ' + chatId);

// Telegram entrega los adjuntos como file_id, que hay que canjear por URL con la API del
// bot. Eso todavía no está cableado, así que por ahora se procesa el texto y se avisa.
const texto = String(msg.text || msg.caption || '').trim();

return [{ json: {
  _tg_chat_id: chatId,
  _tg_nombre: nombre,
  _tg_sin_texto: !texto,
  telefono_sintetico: '""" + PREFIJO + """' + chatId,
  texto,
  // messageId real de Telegram: es la clave de idempotencia del debounce de W1 y viene
  // garantizada, así que no hace falta que W1 la derive por hash.
  messageId: 'tg:' + chatId + ':' + String(msg.message_id ?? ''),
} }];"""

JS_ARMAR_PAYLOAD = """// Toma el contactId que devolvió W0 y arma el payload GHL definitivo para W1.
const ctx = $('TG → payload GHL').first().json;
const r = $input.first().json || {};
// W0 devuelve el contacto en distintas formas según sea alta o match; se aceptan todas
// en vez de asumir una y romper el día que GHL cambie el shape.
const c = r.contact || r.data?.contact || r.data || r;
const contactId = c.id || c.contactId || c._id;
if (!contactId) {
  throw new Error('W1/TG: upsert_contact no devolvió contactId — ' +
    JSON.stringify(r).slice(0, 200));
}
return [{ json: {
  contactId: String(contactId),
  conversationId: null,
  messageId: ctx.messageId,
  body: ctx.texto,
  attachments: [],
  phone: ctx.telefono_sintetico,
  canal: 'Telegram',
  // debounce en 0: en una prueba manual no tiene sentido esperar 50 segundos por si el
  // tester manda otro mensaje. Producción (WhatsApp) sigue con los del origen.
  debounce_seg: 0,
} }];"""


def nodo(nombre, tipo, tv, pos, params, **extra):
    n = {"parameters": params, "type": tipo, "typeVersion": tv,
         "id": f"tg-{abs(hash(nombre)) % 10**12:012d}", "name": nombre, "position": pos}
    n.update(extra)
    return n


def cablear_w1(dry):
    w = D.bajar("W1")
    idx = {n["name"]: n for n in w["nodes"]}
    print(f"── W1 ({len(w['nodes'])} nodos)")
    nuevos = [
        nodo("Telegram Trigger", "n8n-nodes-base.telegramTrigger", 1.2, [-1180, 320],
             {"updates": ["message"], "additionalFields": {}}, credentials=CRED_TG,
             # webhookId OBLIGATORIO: sin él n8n activa el workflow, no da error y no
             # llega nunca un mensaje. Costó un ciclo de test el 14/08.
             webhookId="3b8e5c17-6a24-4d91-8f0b-51c7a9e2d604"),
        nodo("TG → payload GHL", "n8n-nodes-base.code", 2, [-980, 320],
             {"jsCode": JS_TG_A_GHL}),
        nodo("TG · upsert contacto", "n8n-nodes-base.executeWorkflow", 1.2, [-780, 320], {
            "workflowId": {"__rl": True, "value": W0_ID, "mode": "id",
                           "cachedResultName": "HPF·GHL · W0 Client"},
            "workflowInputs": {"mappingMode": "defineBelow", "value": {
                "op": "upsert_contact",
                # `args` va como OBJETO, no como JSON.stringify.
                #
                # El resto de los llamadores de W0 usan JSON.stringify y funcionan porque
                # tienen `schema: []`. Pero la UI de n8n REPUEBLA el schema con sólo abrir
                # y guardar el workflow, y ahí declara `args` como object — el string deja
                # de validar y el nodo tira "Invalid input for 'args'". Pasó dos veces el
                # 14/08: la segunda, un guardado desde la UI revirtió el fix solo.
                #
                # Medido en un workflow descartable con el schema poblado:
                #   args string → falla la validación
                #   args objeto → pasa (con convertFieldsToString true o false)
                # W0 acepta las dos formas (hace JSON.parse sólo si le llega string), así
                # que el objeto es estrictamente mejor: no depende de que nadie abra la UI.
                "args": "={{ {email: 'tg-' + $json._tg_chat_id + "
                        "'@telegram.happyflops.mx', name: $json._tg_nombre, "
                        "source: 'telegram-test', tags: ['canal-telegram','test']} }}"},
                "matchingColumns": [], "schema": [],
                # false porque `args` es un objeto: en true n8n lo pisaría a string.
                "attemptToConvertTypes": False, "convertFieldsToString": False},
            "options": {"waitForSubWorkflow": True}}),
        nodo("TG · armar payload", "n8n-nodes-base.code", 2, [-580, 320],
             {"jsCode": JS_ARMAR_PAYLOAD}),
    ]
    for nd in nuevos:
        if nd["name"] in idx:
            print(f"   • {nd['name']}: ya existe")
        else:
            w["nodes"].append(nd)
            print(f"   + {nd['name']}")
    c = w["connections"]
    cadena = [("Telegram Trigger", "TG → payload GHL"),
              ("TG → payload GHL", "TG · upsert contacto"),
              ("TG · upsert contacto", "TG · armar payload"),
              ("TG · armar payload", "Normalizar entrada")]
    for a, b in cadena:
        r = c.setdefault(a, {}).setdefault("main", [[]])
        if not r:
            r.append([])
        if b in [t["node"] for t in r[0]]:
            print(f"   • {a} → {b}: ya conectado")
        else:
            r[0].append({"node": b, "type": "main", "index": 0})
            print(f"   + {a} → {b}")
    if not dry:
        D.subir("W1", w)
    return w


# ── W2 · salida ───────────────────────────────────────────────────────────────
SQL_CHAT = """-- ¿este contacto es un tester de Telegram? El chat id vive en el teléfono
-- sintético que le puso W1 (+999<chatid>), así que no hace falta ninguna tabla nueva.
SELECT CASE WHEN phone_e164 LIKE '""" + PREFIJO + """%'
            THEN substring(phone_e164 from %s) ELSE NULL END AS chat_id
FROM hpf_identity WHERE ghl_contact_id = $1 LIMIT 1;"""

JS_DECIDIR = """// Decide el transporte de esta burbuja: Telegram o GHL.
const p = $('Preparar op').first().json;
const filas = $input.all().map(i => i.json || {});
const chatId = (filas[0] || {}).chat_id || null;
// Sin fila en hpf_identity o sin prefijo +999 → es un lead de verdad y sale por GHL.
// El default es GHL a propósito: si algo falla en la detección, el peor caso es que un
// tester no reciba el mensaje, no que un lead real lo reciba por el canal equivocado.
return [{ json: { ...p, _chat_id: chatId, _por_telegram: !!chatId } }];"""

JS_TG_PARTES = """// Una burbuja de W2 → los envíos de Telegram que le corresponden.
const p = $input.first().json;
const chatId = p._chat_id;
const adj = Array.isArray(p.adjuntos) ? p.adjuntos : [];
const tipoDe = (url) => {
  const u = String(url).toLowerCase().split('?')[0];
  if (/\\.(jpe?g|png|webp|gif)$/.test(u)) return 'foto';
  if (/\\.(mp4|mov|m4v)$/.test(u)) return 'video';
  return 'documento';
};
if (!adj.length) return [{ json: { chatId, tipo: 'texto', texto: p.texto || '' } }];
// el texto va como caption del primer adjunto, así llegan juntos
return adj.map((url, i) => ({ json: {
  chatId, tipo: tipoDe(url), url, texto: i === 0 ? (p.texto || '') : '' } }));"""


def cablear_w2(dry):
    w = D.bajar("W2")
    idx = {n["name"]: n for n in w["nodes"]}
    print(f"\n── W2 ({len(w['nodes'])} nodos)")
    nuevos = [
        nodo("¿Es Telegram?", "n8n-nodes-base.postgres", 2.4, [640, 260], {
            "operation": "executeQuery", "query": SQL_CHAT.replace("%s", "5"),
            "options": {"queryReplacement": "={{ [ $json.contactId ] }}"}},
             credentials=CRED_PG),
        nodo("Decidir transporte", "n8n-nodes-base.code", 2, [840, 260],
             {"jsCode": JS_DECIDIR}),
        nodo("Ruteo transporte", "n8n-nodes-base.if", 2.2, [1040, 260], {
            "conditions": {"options": {"caseSensitive": True, "version": 2,
                                       "typeValidation": "loose"},
                           "combinator": "and",
                           "conditions": [{"id": "t1",
                                           "leftValue": "={{ $json._por_telegram }}",
                                           "rightValue": True,
                                           "operator": {"type": "boolean",
                                                        "operation": "equals"}}]},
            "options": {}}),
        nodo("TG · aplanar", "n8n-nodes-base.code", 2, [1240, 160],
             {"jsCode": JS_TG_PARTES}),
        nodo("TG · switch tipo", "n8n-nodes-base.switch", 3.2, [1440, 160], {
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
        # `file` y NO `fileId`: fileId es de resource:file/operation:get. n8n descarta la
        # clave desconocida al guardar y el nodo queda sin foto — es el bug que tuvo el
        # handler viejo durante semanas sin que nadie lo viera.
        nodo("TG · texto", "n8n-nodes-base.telegram", 1.2, [1660, 40], {
            "chatId": "={{ $json.chatId }}", "text": "={{ $json.texto }}",
            "additionalFields": {"appendAttribution": False}}, credentials=CRED_TG),
        nodo("TG · foto", "n8n-nodes-base.telegram", 1.2, [1660, 160], {
            "operation": "sendPhoto", "chatId": "={{ $json.chatId }}",
            "file": "={{ $json.url }}",
            "additionalFields": {"caption": "={{ $json.texto }}",
                                 "appendAttribution": False}}, credentials=CRED_TG),
        nodo("TG · video", "n8n-nodes-base.telegram", 1.2, [1660, 280], {
            "operation": "sendVideo", "chatId": "={{ $json.chatId }}",
            "file": "={{ $json.url }}",
            "additionalFields": {"caption": "={{ $json.texto }}",
                                 "appendAttribution": False}}, credentials=CRED_TG),
        nodo("TG · documento", "n8n-nodes-base.telegram", 1.2, [1660, 400], {
            "operation": "sendDocument", "chatId": "={{ $json.chatId }}",
            "binaryData": False, "file": "={{ $json.url }}",
            "additionalFields": {"caption": "={{ $json.texto }}",
                                 "appendAttribution": False}}, credentials=CRED_TG),
    ]
    for nd in nuevos:
        if nd["name"] in idx:
            print(f"   • {nd['name']}: ya existe")
        else:
            w["nodes"].append(nd)
            print(f"   + {nd['name']}")

    c = w["connections"]
    # se intercala entre `Preparar op` y `W0 · enviar`: la rama GHL queda intacta
    pr = c.setdefault("Preparar op", {}).setdefault("main", [[]])
    if [t["node"] for t in pr[0]] == ["¿Es Telegram?"]:
        print("   • Preparar op → ¿Es Telegram?: ya intercalado")
    else:
        print(f"   ~ Preparar op: {[t['node'] for t in pr[0]]} → ['¿Es Telegram?']")
        pr[0] = [{"node": "¿Es Telegram?", "type": "main", "index": 0}]
    lineal = [("¿Es Telegram?", "Decidir transporte"),
              ("Decidir transporte", "Ruteo transporte")]
    for a, b in lineal:
        r = c.setdefault(a, {}).setdefault("main", [[]])
        if not r:
            r.append([])
        r[0] = [{"node": b, "type": "main", "index": 0}]
    # true → Telegram · false → la rama GHL de siempre
    c["Ruteo transporte"] = {"main": [
        [{"node": "TG · aplanar", "type": "main", "index": 0}],
        [{"node": "W0 · enviar", "type": "main", "index": 0}]]}
    c["TG · aplanar"] = {"main": [[{"node": "TG · switch tipo", "type": "main", "index": 0}]]}
    c["TG · switch tipo"] = {"main": [
        [{"node": "TG · texto", "type": "main", "index": 0}],
        [{"node": "TG · foto", "type": "main", "index": 0}],
        [{"node": "TG · video", "type": "main", "index": 0}],
        [{"node": "TG · documento", "type": "main", "index": 0}]]}
    # las 4 salidas de Telegram vuelven al mismo punto donde seguía la rama GHL
    for n in ("TG · texto", "TG · foto", "TG · video", "TG · documento"):
        c[n] = {"main": [[{"node": "Arrastrar contexto", "type": "main", "index": 0}]]}
    print("   + rama Telegram cableada; la rama GHL sigue por 'W0 · enviar'")
    if not dry:
        D.subir("W2", w)
    return w


def main():
    dry = "--dry-run" in sys.argv
    cablear_w1(dry)
    cablear_w2(dry)
    if dry:
        print("\n(dry-run: no escribí nada)")
        return
    print("\n── verificación contra el vivo")
    ok = True
    v1 = D.bajar("W1")
    n1 = {n["name"] for n in v1["nodes"]}
    for x in ("Telegram Trigger", "TG → payload GHL", "TG · upsert contacto", "TG · armar payload"):
        ok &= x in n1
        print(f"   {'✅' if x in n1 else '❌'} W1 · {x}")
    dest = [t["node"] for t in v1["connections"]["TG · armar payload"]["main"][0]]
    ok &= "Normalizar entrada" in dest
    print(f"   {'✅' if 'Normalizar entrada' in dest else '❌'} W1 · TG · armar payload → {dest}")
    v2 = D.bajar("W2")
    n2 = {n["name"] for n in v2["nodes"]}
    for x in ("¿Es Telegram?", "Decidir transporte", "Ruteo transporte", "TG · foto"):
        ok &= x in n2
        print(f"   {'✅' if x in n2 else '❌'} W2 · {x}")
    r = v2["connections"]["Ruteo transporte"]["main"]
    bien = r[0][0]["node"] == "TG · aplanar" and r[1][0]["node"] == "W0 · enviar"
    ok &= bien
    print(f"   {'✅' if bien else '❌'} W2 · true→Telegram / false→W0 · enviar")
    print(f"\n   W1 {len(v1['nodes'])} nodos · W2 {len(v2['nodes'])} nodos")
    print("✅ cableado y verificado" if ok else "❌ NO verificado")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
