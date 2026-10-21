#!/usr/bin/env python3
"""
HPF · comando de reset de memoria en la rama de Telegram de W1.

QUÉ REPLICA
El handler viejo tenía un If sobre `/b`, `/borrar`, `/reset`, `/clear` que hacía:
    DELETE FROM messages WHERE session_id = $1;
    DELETE FROM debounce_buffer WHERE contact_id = $2;
y contestaba "Memoria y buffer limpiados".

QUÉ CAMBIA EN EL STACK NUEVO
Esas dos tablas no existen más. El estado de una sesión ahora vive en cuatro lugares, y
limpiar sólo la memoria del chat deja al bot en un estado raro — por ejemplo recordando el
evento y sin recordar la conversación:

  · `n8n_chat_histories`  — la memoria de los 5 agentes de W6 (session_id)
  · `hpf_estado_sesion`   — el evento elegido (session_id)
  · `hpf_seguimientos`    — la cola de re-enganche (session_id)
  · Redis `hpf:<contactId>` — el buffer del debounce de W1

Se limpian los cuatro. NO se toca `hpf_identity` (si se borrara, el próximo mensaje
generaría otro session_id y la sesión anterior quedaría huérfana en vez de reiniciada) ni
`hpf_mensajes_vistos` (la idempotencia usa el message_id de Telegram, que ya es único por
mensaje). Tampoco se toca nada en GHL: el contacto, la oportunidad y la etapa siguen.

DÓNDE SE INTERCALA
Después de `TG · armar payload`, que es el primer punto donde ya existen contactId y
teléfono — hacen falta los dos: el contactId para la clave de Redis y el teléfono para
derivar el session_id (`phone || '2131'`, la fórmula de `Resolver identidad`).

Uso:  hpf-telegram-reset-memoria.py [--dry-run]
"""
import importlib.util
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "hpfdeploy", REPO / "scripts/utilities/hpf-deploy-workflow.py")
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)

CRED_TG = {"telegramApi": {"id": "yXtgg8Djbxglxq9H", "name": "HPF"}}
CRED_PG = {"postgres": {"id": "uK59P60DJmOJc4Lm", "name": "H.F"}}
CRED_REDIS = {"redis": {"id": "o8I3YHY4b5xY8Ipo", "name": "H.F"}}

COMANDOS = ["/b", "/borrar", "/reset", "/clear", "/nuevo", "/nueva"]

JS_DETECTAR = """// ¿Es un comando de reset? Se compara igual que en el handler viejo: texto entero,
// sin espacios, en minúsculas. Así "/reset" resetea y "reset el pedido" no.
const p = $input.first().json;
const COMANDOS = """ + str(COMANDOS).replace("'", '"') + """;
const t = String(p.body || '').trim().toLowerCase();
// El session_id se deriva igual que en `Resolver identidad` de W1 (phone || '2131').
// Si esa fórmula cambia allá, hay que cambiarla acá — es la misma clave de memoria.
const sessionId = String(p.phone || '') + '2131';
return [{ json: { ...p, _es_reset: COMANDOS.includes(t), _session_id: sessionId } }];"""

SQL_BORRAR = """-- Reset de sesión. Las tres tablas se limpian juntas: dejar una a medias deja al
-- bot recordando el evento sin recordar la conversación, que es peor que no resetear.
DELETE FROM n8n_chat_histories WHERE session_id = $1;
DELETE FROM hpf_estado_sesion  WHERE session_id = $1;
DELETE FROM hpf_seguimientos   WHERE session_id = $1;
SELECT $1::text AS session_id;"""

JS_AVISO = """const p = $('TG · ¿es reset?').first().json;
return [{ json: { chatId: p._tg_chat_id_reset,
  texto: 'Listo, borré la memoria de esta conversación.\\n\\n'
       + 'Se limpió el historial del chat, el evento elegido y la cola de seguimientos. '
       + 'El contacto y la oportunidad en el CRM NO se tocaron.\\n\\n'
       + 'Escribí "hola" para arrancar un caso nuevo.' } }];"""


def nodo(nombre, tipo, tv, pos, params, **extra):
    n = {"parameters": params, "type": tipo, "typeVersion": tv,
         "id": f"rst-{abs(hash(nombre)) % 10**12:012d}", "name": nombre, "position": pos}
    n.update(extra)
    return n


def main():
    dry = "--dry-run" in sys.argv
    w = D.bajar("W1")
    idx = {n["name"]: n for n in w["nodes"]}
    print(f"W1 vivo: {len(w['nodes'])} nodos")
    if "TG · armar payload" not in idx:
        sys.exit("❌ falta la rama de Telegram; correr primero hpf-cablear-telegram-al-stack-nuevo.py")

    # el chat id se arrastra desde el nodo de entrada para poder contestar
    js_detectar = JS_DETECTAR.replace(
        "return [{ json: { ...p,",
        "const tg = $('TG → payload GHL').first().json;\nreturn [{ json: { ...p, "
        "_tg_chat_id_reset: tg._tg_chat_id,")

    nuevos = [
        nodo("TG · ¿es reset?", "n8n-nodes-base.code", 2, [-400, 320],
             {"jsCode": js_detectar}),
        nodo("TG · ruteo reset", "n8n-nodes-base.if", 2.2, [-220, 320], {
            "conditions": {"options": {"caseSensitive": True, "version": 2,
                                       "typeValidation": "loose"},
                           "combinator": "and",
                           "conditions": [{"id": "r1",
                                           "leftValue": "={{ $json._es_reset }}",
                                           "rightValue": True,
                                           "operator": {"type": "boolean",
                                                        "operation": "equals"}}]},
            "options": {}}),
        nodo("TG · borrar memoria", "n8n-nodes-base.postgres", 2.4, [-40, 200], {
            "operation": "executeQuery", "query": SQL_BORRAR,
            "options": {"queryReplacement": "={{ [ $json._session_id ] }}"}},
             credentials=CRED_PG),
        nodo("TG · limpiar debounce", "n8n-nodes-base.redis", 1, [160, 200], {
            "operation": "delete",
            "key": "={{ 'hpf:' + $('TG · ¿es reset?').first().json.contactId }}"},
             credentials=CRED_REDIS),
        nodo("TG · aviso reset", "n8n-nodes-base.code", 2, [360, 200],
             {"jsCode": JS_AVISO}),
        nodo("TG · confirmar reset", "n8n-nodes-base.telegram", 1.2, [560, 200], {
            "chatId": "={{ $json.chatId }}", "text": "={{ $json.texto }}",
            "additionalFields": {"appendAttribution": False}}, credentials=CRED_TG),
    ]
    for nd in nuevos:
        if nd["name"] in idx:
            print(f"   • {nd['name']}: ya existe")
        else:
            w["nodes"].append(nd)
            print(f"   + {nd['name']}")

    c = w["connections"]
    # intercalar: TG · armar payload → ¿es reset? → ruteo → (true) borrar / (false) seguir
    ap = c.setdefault("TG · armar payload", {}).setdefault("main", [[]])
    if [t["node"] for t in ap[0]] == ["TG · ¿es reset?"]:
        print("   • TG · armar payload → TG · ¿es reset?: ya intercalado")
    else:
        print(f"   ~ TG · armar payload: {[t['node'] for t in ap[0]]} → ['TG · ¿es reset?']")
        ap[0] = [{"node": "TG · ¿es reset?", "type": "main", "index": 0}]
    c["TG · ¿es reset?"] = {"main": [[{"node": "TG · ruteo reset", "type": "main", "index": 0}]]}
    c["TG · ruteo reset"] = {"main": [
        [{"node": "TG · borrar memoria", "type": "main", "index": 0}],
        [{"node": "Normalizar entrada", "type": "main", "index": 0}]]}
    c["TG · borrar memoria"] = {"main": [[{"node": "TG · limpiar debounce", "type": "main", "index": 0}]]}
    c["TG · limpiar debounce"] = {"main": [[{"node": "TG · aviso reset", "type": "main", "index": 0}]]}
    c["TG · aviso reset"] = {"main": [[{"node": "TG · confirmar reset", "type": "main", "index": 0}]]}
    print("   + rama de reset cableada (true→borra · false→sigue al flujo normal)")

    if dry:
        print("(dry-run: no escribo)")
        return

    D.subir("W1", w)
    v = D.bajar("W1")
    vi = {n["name"] for n in v["nodes"]}
    ok = True
    for x in ("TG · ¿es reset?", "TG · ruteo reset", "TG · borrar memoria",
              "TG · limpiar debounce", "TG · confirmar reset"):
        ok &= x in vi
        print(f"   {'✅' if x in vi else '❌'} {x}")
    r = v["connections"]["TG · ruteo reset"]["main"]
    bien = (r[0][0]["node"] == "TG · borrar memoria"
            and r[1][0]["node"] == "Normalizar entrada")
    ok &= bien
    print(f"   {'✅' if bien else '❌'} ruteo: true→borrar · false→Normalizar entrada")
    ap = [t["node"] for t in v["connections"]["TG · armar payload"]["main"][0]]
    ok &= ap == ["TG · ¿es reset?"]
    print(f"   {'✅' if ap == ['TG · ¿es reset?'] else '❌'} TG · armar payload → {ap}")
    print(f"\n   W1: {len(v['nodes'])} nodos")
    print("✅ aplicado y verificado" if ok else "❌ NO verificado")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
