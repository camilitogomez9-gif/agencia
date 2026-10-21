#!/usr/bin/env python3
"""
HPF · el carril de prueba de Telegram recibe adjuntos (Fase 0 de la guía de paridad).

EL PROBLEMA
`TG · armar payload` fija `attachments: []`, así que por Telegram no entra media. Seis
familias de la matriz de paridad (comprobante de pago, imagen de producto, imagen no
categorizable, PDF, audio, guardia de horario) sólo existen del lado viejo y no se pueden
cruzar contra el agente nuevo.

EL CANJE
Telegram entrega `file_id`, no URLs. La URL que produzcamos tiene que ser pública sin auth,
terminar en la extensión correcta —es lo ÚNICO que mira `Normalizar entrada` para clasificar
el mensaje— y ser fetcheable por la API de visión de OpenAI. Se baja el binario con el nodo
Telegram y se sube a la Media Library de GHL, que devuelve una URL de
`assets.cdn.filesafe.space`: el mismo dominio de las 65 fichas, ya probado con OpenAI y con
el `Descargar audio` de W1, y que conserva la extensión.

Construir `api.telegram.org/file/bot<TOKEN>/<file_path>` NO es viable: los Code node de n8n
no leen credenciales, y la credencial `telegramApi` mete el token en el PATH, cosa que el
mecanismo genérico de auth del HTTP Request no sabe hacer (sólo header/query/body/basic).
Hardcodearlo dejaría un secreto en el JSON del workflow, en el repo y en cada log de
ejecución — y se lo pasaría a OpenAI en `imageUrls`.

TOPOLOGÍA
El ruteo de media va DESPUÉS de `TG · ruteo reset`, así que una foto con caption `/reset`
resetea y no sube nada. Todo en cadena principal: sin ramas paralelas no aplica la trampa de
`executionOrder: v1` / `isExecuted`.

`Normalizar entrada` conserva `Webhook inbound` entre sus ancestros. No es cosmético:
`Responder ack` es un respondToWebhook tv1.1 que valida estáticamente que haya un Webhook
entre sus padres. Romper eso tira el carril de PRODUCCIÓN, no el de test.

Idempotente: si ya está aplicado, no duplica nada.

Uso:  hpf-fix-telegram-adjuntos.py [--dry-run] [--sin-unit]
Rollback:
  hpf-deploy-workflow.py --restore \
    clients/HPF_HappyFlops/03_workflows/ghl-live-2026-08-17-post-paridad/W1.json
"""
import importlib.util
import pathlib
import sys

# se carga a mano porque el nombre del archivo tiene guiones
_spec = importlib.util.spec_from_file_location(
    "hpfdeploy", pathlib.Path(__file__).parent / "hpf-deploy-workflow.py")
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)

CRED_TG = {"telegramApi": {"id": "yXtgg8Djbxglxq9H", "name": "HPF"}}
CRED_GHL = {"httpHeaderAuth": {"id": "Zz21t1RdLIMvud4j", "name": "GHL PIT HPF"}}
LOC = "onRwi0ZF4uYi0Lp6GAbE"
CDN = "https://assets.cdn.filesafe.space/" + LOC + "/media/"

JS_PAYLOAD = r'''// Telegram → el payload que espera W1, que es el de GHL.
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

const texto = String(msg.text || msg.caption || '').trim();

// ── adjuntos ──────────────────────────────────────────────────────────────────────────
// Telegram entrega los adjuntos como `file_id`. Acá SÓLO se decide cuál se canjea y con
// qué extensión va a quedar; el canje lo hacen `TG · bajar archivo` → `TG · subir a GHL`.
//
// La extensión NO se lee de Telegram. `file_path` de la Bot API suele traerla bien, pero
// es un dato que no controlamos y de él depende TODA la clasificación que hace
// `Normalizar entrada`, que mira exclusivamente la extensión de adjuntos[0]:
//     .ogg .oga .mp3 .m4a .wav .amr → audio   (→ Whisper)
//     .pdf                          → pdf     (→ W7, sin visión)
//     cualquier otro adjunto        → imagen  (→ W7, visión de OpenAI)
// Un video queda como 'imagen' y la visión lo rechaza: es EXACTAMENTE lo que le pasa hoy
// a un lead real que manda un video por WhatsApp. Se replica a propósito — esta Fase 0
// existe para que la guía de paridad DESCUBRA estas cosas, no para taparlas.
const MAX = 20 * 1024 * 1024;   // techo duro de getFile en la Bot API

// Extensiones que un `document` puede tener para que valga la pena subirlo. Es más
// estricto que producción, y sólo acá: sin esto un .zip se sube, la visión lo rechaza y
// el caso de prueba "documento no soportado" no tiene resultado observable.
const DOC_OK = ['pdf', 'jpg', 'jpeg', 'png', 'webp', 'gif',
                'ogg', 'oga', 'mp3', 'm4a', 'wav', 'amr', 'mp4', 'mov', 'm4v'];

const extDe = (n, def) => {
  const m = String(n || '').toLowerCase().match(/\.([a-z0-9]{1,5})$/);
  return m ? m[1] : def;
};

let media = null;     // { file_id, ext, clase, bytes }
let rechazo = '';

if (Array.isArray(msg.photo) && msg.photo.length) {
  // `photo` es el array de tamaños, ordenado de menor a mayor. El último es el que le
  // sirve a la visión.
  const p = msg.photo[msg.photo.length - 1];
  media = { file_id: p.file_id, ext: 'jpg', clase: 'foto',
            bytes: Number(p.file_size || 0) };
} else if (msg.voice) {
  // Las notas de voz de Telegram son OGG/Opus. '.oga' matchea el regex de audio de W1.
  media = { file_id: msg.voice.file_id, ext: 'oga', clase: 'nota de voz',
            bytes: Number(msg.voice.file_size || 0) };
} else if (msg.audio) {
  media = { file_id: msg.audio.file_id, ext: extDe(msg.audio.file_name, 'mp3'),
            clase: 'audio', bytes: Number(msg.audio.file_size || 0) };
} else if (msg.video_note) {
  media = { file_id: msg.video_note.file_id, ext: 'mp4', clase: 'video',
            bytes: Number(msg.video_note.file_size || 0) };
} else if (msg.animation) {
  // Un GIF de Telegram es un mp4, y viene con `animation` Y `document` poblados a la vez.
  // Por eso va ANTES de document: si no, entra por la rama equivocada.
  media = { file_id: msg.animation.file_id, ext: 'mp4', clase: 'video',
            bytes: Number(msg.animation.file_size || 0) };
} else if (msg.video) {
  media = { file_id: msg.video.file_id, ext: extDe(msg.video.file_name, 'mp4'),
            clase: 'video', bytes: Number(msg.video.file_size || 0) };
} else if (msg.document) {
  const ext = extDe(msg.document.file_name, '');
  if (DOC_OK.includes(ext)) {
    media = { file_id: msg.document.file_id, ext, clase: 'documento',
              bytes: Number(msg.document.file_size || 0) };
  } else {
    // El nombre del archivo NO se echa en el aviso: un 'mi_archivo.zip' metería un '_'
    // suelto y, si el nodo de Telegram sale con parse_mode, eso es un 400.
    rechazo = 'No puedo procesar ese tipo de archivo. Mandame una foto, un PDF o una nota de voz.';
  }
} else if (msg.sticker) {
  rechazo = 'No puedo procesar stickers. Mandame una foto, un PDF o una nota de voz.';
} else if (msg.location || msg.venue) {
  rechazo = 'No puedo procesar ubicaciones. Escribime la direccion como texto.';
} else if (msg.contact || msg.poll || msg.dice || msg.game) {
  rechazo = 'No puedo procesar ese tipo de mensaje. Mandame texto, una foto, un PDF o una nota de voz.';
}

// getFile devuelve 400 arriba de 20 MB y no hay manera de bajar el archivo. Se corta acá,
// con el file_size que ya viene en el update, para dar un mensaje entendible en vez del
// error crudo de la API.
if (media && media.bytes > MAX) {
  rechazo = 'Ese archivo pesa mas de 20 MB y Telegram no me deja bajarlo. Mandame uno mas chico.';
  media = null;
}

// Sin texto y sin adjunto reconocible no hay nada que procesar. Ojo: una FOTO SIN CAPTION
// no cae acá — tiene media, y el mensaje de imagen con texto vacío es válido de punta a
// punta (W7 hace String(src.texto ?? '') y la visión sólo usa la URL).
if (!media && !rechazo && !texto) {
  rechazo = 'No pude leer ese mensaje. Mandame texto, una foto, un PDF o una nota de voz.';
}

return [{ json: {
  _tg_chat_id: chatId,
  _tg_nombre: nombre,
  // Se sigue emitiendo porque es diagnóstico útil en el log, pero YA NO ES UN GUARD: si
  // alguien lo cablea "para completar", rompe las fotos sin caption. El guard real es
  // `_tg_ruta`.
  _tg_sin_texto: !texto,
  telefono_sintetico: '+999' + chatId,
  texto,
  // messageId real de Telegram: es la clave de idempotencia del debounce de W1 y viene
  // garantizada, así que no hace falta que W1 la derive por hash.
  messageId: 'tg:' + chatId + ':' + String(msg.message_id ?? ''),
  // ── contrato con los nodos de media ────────────────────────────────────────────────
  // Ternario TOTAL: siempre vale una de las tres. Por eso `TG · ruteo media` puede ir sin
  // fallback y no pierde items.
  _tg_ruta: rechazo ? 'no_soportado' : (media ? 'con_media' : 'sin_media'),
  _tg_media: media,
  _media_error: rechazo,
} }];
'''

JS_ARMAR = r'''// Toma el contactId que devolvió W0 y arma el payload GHL definitivo para W1.
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
  // Vacío a propósito. La rama con adjunto la pisa `TG · adjuntar media`, que es el único
  // nodo que llega a conocer la URL pública.
  attachments: [],
  phone: ctx.telefono_sintetico,
  canal: 'Telegram',
  // 0 para texto: en una prueba manual esperar 50s por respuesta es insufrible, y un
  // mensaje escrito no viene en ráfaga. Para media 0 NO sirve — un álbum de Telegram
  // llega como N mensajes independientes y el "gana el último" no alcanza a deduplicar
  // nada. `TG · adjuntar media` lo sube a 15 en esa rama.
  debounce_seg: 0,
  // Se arrastran para el Switch de ruteo y para el aviso de rechazo.
  _tg_ruta: ctx._tg_ruta,
  _media_error: ctx._media_error,
} }];
'''

JS_NOMBRAR = r'''// El nombre del archivo lo fijamos NOSOTROS, no Telegram.
//
// `TG · bajar archivo` nombra el binario con lo que venga en `file_path` de la Bot API
// ('photos/file_12.jpg', 'voice/file_13.oga'...). En la práctica la extensión viene bien,
// pero es un dato que no controlamos y de él depende TODA la clasificación de
// `Normalizar entrada`. Así que se reescribe con la que ya decidió `TG → payload GHL`, y
// se manda además en el campo `name` del multipart — que es de donde GHL saca el nombre
// con el que publica el archivo. Dos mecanismos, uno tiene que pegar.
const ctx = $('TG → payload GHL').first().json;
const med = ctx._tg_media || {};
const it  = $input.first();
const j   = it.json || {};
const res = j.result || {};

// Prefijo 'tg-test-' para poder listarlos y borrarlos después de la corrida:
//     hpf-subir-media-ghl.py --listar tg-test
// El chat y el message_id hacen el nombre trazable y único.
const nombre = 'tg-test-' + ctx._tg_chat_id + '-' +
               String(ctx.messageId).split(':').pop() + '.' + med.ext;

// getFile falla con 400 si el archivo pasa los 20 MB o si el file_id venció. El nodo
// anterior va con onError:continueRegularOutput justamente para poder avisarlo por
// Telegram en vez de morir en silencio, así que acá NO se tira: se marca y se sigue.
// `TG · subir a GHL` va a fallar también (no hay binario), pero `TG · adjuntar media`
// reporta ESTE error, que es el de verdad, y no el derivado.
if (!res.file_path || !it.binary || !it.binary.data) {
  return [{ json: { ...j, _nombre_ghl: nombre,
    _media_error: 'No pude bajar el archivo de Telegram. Proba con uno mas chico o mandalo de nuevo.' } }];
}

// El binario viaja tal cual; sólo se le cambian los metadatos de nombre. El mimeType NO se
// toca: lo puso el nodo de Telegram desde la respuesta real y GHL lo usa como Content-Type.
it.binary.data.fileName = nombre;
it.binary.data.fileExtension = med.ext;
return [{ json: { ...j, _nombre_ghl: nombre, _media_error: '' }, binary: it.binary }];
'''

JS_ADJUNTAR = r'''// Última parada del canje: convierte lo que devolvió GHL en el `attachments[]` que espera
// `Normalizar entrada`.
//
// El contrato no es negociable: `Normalizar entrada` clasifica el mensaje MIRANDO LA
// EXTENSIÓN de adjuntos[0]. Si la URL no termina como corresponde, un audio se procesa
// como imagen y el turno sale mal SIN NINGÚN ERROR. Por eso acá se verifica la extensión
// de la URL final antes de dejarla pasar: un bug silencioso se convierte en un mensaje.
const base = $('TG · ¿es reset?').first().json;   // el payload completo de esta rama
const ctx  = $('TG → payload GHL').first().json;
const nom  = $('TG · nombrar archivo').first().json;
const med  = ctx._tg_media || {};

// n8n trunca los errores POR EL FINAL: lo accionable va primero, el ruido al final.
// Y se limpian los caracteres de Markdown: el repo se contradice sobre si los nodos de
// Telegram salen con parse_mode, y un '_' suelto del body de GHL sería un 400.
const fallar = (m) => [{ json: { ...base,
  _media_error: String(m).replace(/[*_`\[\]]/g, ' ').slice(0, 300) } }];

// Error arrastrado desde la bajada.
if (nom._media_error) return fallar(nom._media_error);

const up  = $input.first().json || {};
const st  = Number(up.statusCode ?? 200);
const b   = up.body ?? up;
const txt = (typeof b === 'string') ? b : JSON.stringify(b || {});

if (st < 200 || st >= 300) {
  // 401/403 = el PIT de la credencial no tiene scope medias.write, o Cloudflare.
  return fallar('GHL rechazo la subida (HTTP ' + st + '). ' + txt.slice(0, 140));
}

// GHL devuelve el id del archivo; según la versión, a veces también la URL. Se aceptan las
// dos formas y, si sólo vino el id, se arma la URL del CDN — el mismo patrón con el que se
// sirven las 65 fichas del catálogo.
const CDN = 'https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/';
const id  = b.fileId || b.id || b._id || (b.file && b.file.id) || '';
let url = String(b.url || b.fileUrl || (b.file && b.file.url) || '');
if (!url && id) url = CDN + id + '.' + med.ext;
if (!url) return fallar('GHL acepto el archivo pero no devolvio URL. ' + txt.slice(0, 140));

// El assert que evita el bug silencioso.
const limpia = url.split('?')[0].toLowerCase();
if (!limpia.endsWith('.' + String(med.ext).toLowerCase())) {
  return fallar('La URL de GHL no termino en .' + med.ext +
                ' y W1 la clasificaria mal. URL: ' + url.slice(-70));
}

return [{ json: {
  ...base,
  attachments: [url],
  // 15 s, no 0. Con 0 el "gana el último" no deduplica nada: cada ejecución empuja a Redis
  // y lee al instante, y siempre se ve última. Un álbum de 3 fotos son 3 mensajes
  // independientes de Telegram → 3 respuestas. Con 15 las tres empujan y sólo la última
  // sigue. 15 es además lo que `Normalizar entrada` aplicaría solo para una imagen, así
  // que la comparación con producción es honesta.
  // (Producción usa 50 para audio; acá también van 15 — diferencia declarada en la guía.)
  debounce_seg: 15,
  _media_error: '',
  _tg_media_url: url,
  _tg_media_clase: med.clase,
} }];
'''


def _cond(id_, left, right, op):
    return {"options": {"caseSensitive": True, "leftValue": "",
                        "typeValidation": "strict", "version": 2},
            "conditions": [{"id": id_, "leftValue": left,
                            "rightValue": right, "operator": op}],
            "combinator": "and"}


def _regla(id_, valor):
    return {"conditions": {"options": {"caseSensitive": True, "version": 2,
                                       "typeValidation": "loose"},
                           "combinator": "and",
                           "conditions": [{"id": id_,
                                           "leftValue": "={{ $json._tg_ruta }}",
                                           "rightValue": valor,
                                           "operator": {"type": "string",
                                                        "operation": "equals"}}]},
            "renameOutput": True, "outputKey": valor}


NODOS = [
    {"id": "d3f1a2b0-1111-4ccc-9101-0a1b2c3d4e01",
     "name": "TG · ruteo media",
     "type": "n8n-nodes-base.switch", "typeVersion": 3,
     "position": [-48, 440],
     "parameters": {"rules": {"values": [_regla("rm-con", "con_media"),
                                         _regla("rm-sin", "sin_media"),
                                         _regla("rm-no", "no_soportado")]},
                    "options": {}}},

    {"id": "d3f1a2b0-2222-4ccc-9102-0a1b2c3d4e02",
     "name": "TG · bajar archivo",
     "type": "n8n-nodes-base.telegram", "typeVersion": 1.2,
     "position": [160, 440],
     "webhookId": "5a1c7e30-8b44-4d21-9e6f-71a2b3c4d5e6",
     "credentials": CRED_TG,
     # Sin esto, un getFile fallido mata la ejecución antes de que exista el aviso.
     "onError": "continueRegularOutput",
     "parameters": {
         "resource": "file", "operation": "get",
         "fileId": "={{ $('TG → payload GHL').first().json._tg_media.file_id }}",
         "download": True}},

    {"id": "d3f1a2b0-3333-4ccc-9103-0a1b2c3d4e03",
     "name": "TG · nombrar archivo",
     "type": "n8n-nodes-base.code", "typeVersion": 2,
     "position": [368, 440],
     "parameters": {"jsCode": JS_NOMBRAR}},

    {"id": "d3f1a2b0-4444-4ccc-9104-0a1b2c3d4e04",
     "name": "TG · subir a GHL",
     "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
     "position": [576, 440],
     "credentials": CRED_GHL,
     "onError": "continueRegularOutput",
     "parameters": {
         "method": "POST",
         "url": "https://services.leadconnectorhq.com/medias/upload-file",
         "authentication": "genericCredentialType",
         "genericAuthType": "httpHeaderAuth",
         "sendHeaders": True,
         "headerParameters": {"parameters": [
             {"name": "Version", "value": "2021-07-28"},
             {"name": "Accept", "value": "application/json"},
             # Cloudflare (regla 1010) devuelve 403 con el UA por defecto de una librería.
             # Este string exacto es el que ya usa el nodo `GHL` de W0 y funciona.
             {"name": "User-Agent", "value": "hpf-n8n/1.0"}]},
         "sendBody": True,
         "contentType": "multipart-form-data",
         # Shape verificado contra un multipart real del repo (NVJ_Narvaja, nodo
         # `Transcribir audio/s`, mismo typeVersion 4.2): el binario lleva
         # `parameterType: formBinaryData` + `inputDataFieldName`, y los campos de texto
         # van SIN `parameterType`.
         "bodyParameters": {"parameters": [
             {"name": "name", "value": "={{ $json._nombre_ghl }}"},
             {"name": "hosted", "value": "false"},
             {"name": "altId", "value": LOC},
             {"name": "altType", "value": "location"},
             {"parameterType": "formBinaryData", "name": "file",
              "inputDataFieldName": "data"}]},
         "options": {"timeout": 120000,
                     "response": {"response": {"fullResponse": True,
                                               "neverError": True}}}}},

    {"id": "d3f1a2b0-5555-4ccc-9105-0a1b2c3d4e05",
     "name": "TG · adjuntar media",
     "type": "n8n-nodes-base.code", "typeVersion": 2,
     "position": [784, 440],
     "parameters": {"jsCode": JS_ADJUNTAR}},

    {"id": "d3f1a2b0-6666-4ccc-9106-0a1b2c3d4e06",
     "name": "TG · ¿media ok?",
     "type": "n8n-nodes-base.if", "typeVersion": 2.2,
     "position": [992, 440],
     "parameters": {"conditions": _cond("mo-1", "={{ $json._media_error }}", "",
                                        {"type": "string", "operation": "empty",
                                         "singleValue": True}),
                    "options": {}}},

    {"id": "d3f1a2b0-7777-4ccc-9107-0a1b2c3d4e07",
     "name": "TG · aviso media",
     "type": "n8n-nodes-base.telegram", "typeVersion": 1.2,
     "position": [1200, 560],
     "webhookId": "6b2d8f41-9c55-4e32-8f70-82b3c4d5e6f7",
     "credentials": CRED_TG,   # el MISMO bot que recibe, si no contesta otro
     # SIN onError a propósito: acá el aviso ES el objetivo. Si falla, quiero rojo.
     "parameters": {
         "chatId": "={{ $('TG → payload GHL').first().json._tg_chat_id }}",
         "text": "={{ $json._media_error || 'No pude procesar ese mensaje. "
                 "Mandame texto, una foto, un PDF o una nota de voz.' }}",
         "additionalFields": {"appendAttribution": False}}},
]

CABLEADO = {
    "TG · ruteo reset":     [["TG · borrar memoria"], ["TG · ruteo media"]],
    "TG · ruteo media":     [["TG · bajar archivo"], ["Normalizar entrada"],
                             ["TG · aviso media"]],
    "TG · bajar archivo":   [["TG · nombrar archivo"]],
    "TG · nombrar archivo": [["TG · subir a GHL"]],
    "TG · subir a GHL":     [["TG · adjuntar media"]],
    "TG · adjuntar media":  [["TG · ¿media ok?"]],
    "TG · ¿media ok?":      [["Normalizar entrada"], ["TG · aviso media"]],
}

SENT_PAYLOAD = "_tg_ruta"
SENT_ARMAR = "_tg_ruta: ctx._tg_ruta"


def cablear(conn, origen, salidas):
    m = conn.setdefault(origen, {}).setdefault("main", [])
    while len(m) < len(salidas):
        m.append([])
    for i, destinos in enumerate(salidas):
        actual = [t["node"] for t in m[i]]
        if actual == destinos:
            print(f"   • {origen}[{i}] → {destinos}: ya cableado")
        else:
            m[i] = [{"node": d, "type": "main", "index": 0} for d in destinos]
            print(f"   ~ {origen}[{i}]: {actual} → {destinos}")


def verificar():
    print("\n── verificación contra el vivo")
    v = D.bajar("W1")
    vidx = {n["name"]: n for n in v["nodes"]}
    c = v["connections"]
    ok = True

    def chk(cond, bien, mal):
        nonlocal ok
        print(f"   {'✅' if cond else '❌'} {bien if cond else mal}")
        if not cond:
            ok = False

    chk(len(v["nodes"]) == 59, "59 nodos", f"quedaron {len(v['nodes'])}, esperaba 59")

    for nd in NODOS:
        n = vidx.get(nd["name"])
        chk(bool(n), f"{nd['name']} existe", f"FALTA {nd['name']}")
        if not n:
            continue
        chk(n["type"] == nd["type"] and n["typeVersion"] == nd["typeVersion"],
            f"{nd['name']}: {n['type'].split('.')[-1]} tv{n['typeVersion']}",
            f"{nd['name']}: type/typeVersion mal")
        for k, esp in (nd.get("credentials") or {}).items():
            real = n.get("credentials", {}).get(k, {}).get("id")
            chk(real == esp["id"], f"{nd['name']}: cred {k}={real}",
                f"{nd['name']}: cred {k}={real}, esperaba {esp['id']}")
        if "onError" in nd:
            chk(n.get("onError") == nd["onError"], f"{nd['name']}: onError ok",
                f"{nd['name']}: onError {n.get('onError')!r}")

    chk(SENT_PAYLOAD in vidx["TG → payload GHL"]["parameters"]["jsCode"],
        "TG → payload GHL parcheado", "TG → payload GHL NO quedó parcheado")
    chk(SENT_ARMAR in vidx["TG · armar payload"]["parameters"]["jsCode"],
        "TG · armar payload parcheado", "TG · armar payload NO quedó parcheado")

    for origen, esp in CABLEADO.items():
        real = [[t["node"] for t in r] for r in c[origen]["main"]]
        chk(real == esp, f"{origen} → {real}", f"{origen} → {real}, esperaba {esp}")

    # `Responder ack` es un respondToWebhook tv1.1: valida estáticamente que haya un
    # Webhook entre sus ancestros. Si `Normalizar entrada` pierde a `Webhook inbound`,
    # se cae el carril de PRODUCCIÓN.
    ent = sorted({o for o, s in c.items() for r in s.get("main", [])
                  for t in r if t["node"] == "Normalizar entrada"})
    esp = sorted(["Webhook inbound", "TG · ruteo media", "TG · ¿media ok?"])
    chk(ent == esp, f"Normalizar entrada la alimentan {ent}",
        f"entradas de Normalizar entrada: {ent}, esperaba {esp}")

    chk(not c.get("TG · aviso media", {}).get("main", [[]])[0],
        "TG · aviso media es terminal", "TG · aviso media tiene salida")

    for o, e in [("TG · borrar memoria", ["TG · limpiar debounce"]),
                 ("TG · limpiar debounce", ["TG · aviso reset"]),
                 ("TG · aviso reset", ["TG · confirmar reset"])]:
        real = [t["node"] for t in c[o]["main"][0]]
        chk(real == e, f"reset intacto: {o} → {real}", f"RESET ROTO: {o} → {real}")

    chk(vidx["Debounce · esperar"]["parameters"].get("unit") == "seconds",
        "Debounce · esperar en segundos", "Debounce · esperar sin unit explícito")

    # Sin webhookId el Telegram Trigger activa sin error y nunca recibe nada.
    trig = [n for n in v["nodes"] if n["type"].endswith("telegramTrigger")]
    chk(bool(trig) and all(n.get("webhookId") for n in trig),
        "el Telegram Trigger conserva su webhookId",
        "¡el Telegram Trigger perdió el webhookId!")

    s, meta = D.api(f"/api/v1/workflows/{D.IDS['W1']}")
    chk(meta.get("active") is True, "W1 sigue activo", "W1 quedó INACTIVO")

    print("\n✅ aplicado" if ok else "\n❌ revisar")
    return ok


def main():
    dry = "--dry-run" in sys.argv
    w = D.bajar("W1")
    idx = {n["name"]: n for n in w["nodes"]}
    print(f"W1 vivo: {len(w['nodes'])} nodos")

    # ── 0. precondiciones: el vivo tiene que ser el que creemos
    for n in ("TG → payload GHL", "TG · armar payload", "TG · ¿es reset?",
              "TG · ruteo reset", "Normalizar entrada", "Debounce · esperar"):
        if n not in idx:
            sys.exit(f"❌ falta {n!r} en el vivo")
    if len(w["nodes"]) not in (52, 59):
        sys.exit(f"❌ W1 tiene {len(w['nodes'])} nodos, esperaba 52 (limpio) o 59 (ya aplicado)")

    # ── 1. nodos nuevos (idempotente por nombre)
    for nd in NODOS:
        if nd["name"] in idx:
            print(f"   • {nd['name']}: ya existe, no lo duplico")
        else:
            w["nodes"].append(nd)
            print(f"   + nodo {nd['name']}")

    # ── 2. los dos Code (idempotente por centinela)
    for nombre, js, cent in (("TG → payload GHL", JS_PAYLOAD, SENT_PAYLOAD),
                             ("TG · armar payload", JS_ARMAR, SENT_ARMAR)):
        actual = idx[nombre]["parameters"]["jsCode"]
        if cent in actual:
            print(f"   • {nombre}: ya parcheado")
        else:
            idx[nombre]["parameters"]["jsCode"] = js
            print(f"   ~ {nombre} reescrito ({len(actual)} → {len(js)} chars)")

    # ── 3. `Debounce · esperar` no declara `unit`. Hoy da igual porque el carril de
    #      Telegram fuerza 0; con 15 deja de dar igual. Medido sobre ejecuciones reales:
    #      las que corrieron con debounce_seg=8 duraron 25 s y 10 s totales, así que el
    #      default ES segundos. Igual se explicita: un default implícito que deja de ser
    #      inofensivo hay que volverlo explícito.
    if "--sin-unit" not in sys.argv:
        p = idx["Debounce · esperar"]["parameters"]
        if p.get("unit") == "seconds":
            print("   • Debounce · esperar: unit ya explícito")
        elif "unit" in p:
            sys.exit(f"❌ Debounce · esperar ya tiene unit={p['unit']!r} — PARAR y revisar")
        else:
            p["unit"] = "seconds"
            print("   ~ Debounce · esperar: unit ← 'seconds' (era implícito)")

    # ── 4. cableado
    for origen, salidas in CABLEADO.items():
        cablear(w["connections"], origen, salidas)
    if w["connections"].get("TG · aviso media", {}).get("main", [[]])[0]:
        sys.exit("❌ TG · aviso media tiene salida y debería ser terminal")

    if dry:
        print("(dry-run: no escribo)")
        return

    D.subir("W1", w)
    sys.exit(0 if verificar() else 1)


if __name__ == "__main__":
    main()
