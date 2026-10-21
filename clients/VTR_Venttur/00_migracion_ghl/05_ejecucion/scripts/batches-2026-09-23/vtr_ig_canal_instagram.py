#!/usr/bin/env python3
"""Fix 24/9 · el agente también responde por Instagram (y Facebook) desde GHL.

Diagnóstico (24/9): ningún mensaje de Instagram llegaba al main (`Inbound bot` en GHL filtraba sólo WhatsApp —
eso lo cambia la agencia en GHL) y, aunque llegara, el stack nuevo estaba cableado a WhatsApp:
  · main: `Enviar WPP` mandaba siempre `type: 'WhatsApp'`; la memoria usaba el teléfono como sessionKey (los
    contactos de IG no tienen teléfono → clave vacía, memoria compartida); la cadena Airtable creaba una fila
    `Leads` sin teléfono por cada mensaje; alerta/log del guardrail sin identificador.
  · W9 → rescate: el rescate mandaba WhatsApp y armaba la sessionKey desde el teléfono ('+' a secas para IG).
  · despachador: mandaría plantillas de WhatsApp a contactos sin teléfono.

Qué hace (marca IG-0924, idempotente):
  main        Normalize detecta el canal (message.type 19/18/11 o texto) y usa `ig_<contactId>` como
              sessionKey si no hay teléfono (con teléfono sigue '+521…', WhatsApp queda idéntico).
              `Separamos en partes` confirma el canal con el último mensaje entrante de la API de GHL
              (messageType TYPE_INSTAGRAM/…), que es lo que usa `Enviar WPP`. `No existe` exige teléfono.
              Guardrail usa sessionKey si no hay teléfono. `Actualizar link` pasa canal + sessionKey a W9.
  W9          recibe canal + sessionKey y los reenvía al rescate.
  rescate     Fase 1 sale por el canal del lead. Fase 2 (24 h después) sólo por WhatsApp: en IG/FB queda fuera
              de la ventana de 24 h de Meta → no se manda, pero igual se etiqueta y se mueve a Abandonado frío.
  despachador no toca contactos sin teléfono (las plantillas son de WhatsApp).

Uso: python3 vtr_ig_canal_instagram.py [--execute]
"""
import copy, json, sys, importlib.util, uuid
from pathlib import Path
spec = importlib.util.spec_from_file_location("p", Path(__file__).with_name("vtr_pre_bsp_fixes.py"))
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)

MARK = "IG-0924"
OUT = p.ROOT / "clients/VTR_Venttur/03_workflows/ghl-live-2026-09-24-instagram"
IDS = {"main": "1eS1Z5k898c3ATnf", "w9": "TROsQ5h78baAuVOY",
       "rescate": "YB0UxwEVwzISdd54", "despachador": "vrShEXQGGAo4FqAt"}
N = "$('Normalize GHL Payload').first().json"


def patch_main(wf):
    # 1 · Normalize: canal + sessionKey sin teléfono
    n = p.node(wf, "Normalize GHL Payload")
    p.replace_in(n, "const plus = wa ? ('+' + wa) : null;\n",
                 "const plus = wa ? ('+' + wa) : null;\n"
                 "// IG-0924: canal del mensaje entrante. GHL manda message.type numérico (19 WhatsApp, 18 Instagram,\n"
                 "// 11 Facebook); se acepta también texto. Sin dato: con teléfono es WhatsApp, sin teléfono Instagram.\n"
                 "function canalDe(t) {\n"
                 "  if (t === null || t === undefined || t === '') return null;\n"
                 "  const M = { 19: 'WhatsApp', 18: 'IG', 11: 'FB' };\n"
                 "  if (M[Number(t)]) return M[Number(t)];\n"
                 "  const s = String(t).toLowerCase();\n"
                 "  if (s.includes('instagram') || s === 'ig') return 'IG';\n"
                 "  if (s.includes('facebook') || s.includes('messenger') || s === 'fb') return 'FB';\n"
                 "  if (s.includes('whatsapp')) return 'WhatsApp';\n"
                 "  return null;\n"
                 "}\n"
                 "const canal = canalDe(msg.type) || canalDe(msg.messageType) || canalDe(body.messageType)\n"
                 "  || canalDe(body.channel) || canalDe(body.canal) || (wa ? 'WhatsApp' : 'IG');\n"
                 "// Con teléfono la memoria sigue siendo '+521…' (la comparten rescate/despachador); sin teléfono, por contacto.\n"
                 "const session_key = plus || (contact_id ? (canal === 'FB' ? 'fb_' : 'ig_') + contact_id : null);\n")
    p.replace_in(n, "  session_key: plus,          // +521<10> — memoria/rescate/despachador (D5)\n",
                 "  session_key,                // +521<10> (D5) · ig_<contactId> sin teléfono (IG-0924)\n"
                 "  canal,                      // WhatsApp | IG | FB (IG-0924)\n")

    # 2 · Separamos en partes: el canal real sale del último entrante de la API de GHL
    s = p.node(wf, "Separamos en partes")
    p.replace_in(s, "return [{ json: { texto, audio } }];",
                 "// IG-0924: canal de respuesta = el del último mensaje entrante (la conversación de GHL es una sola por\n"
                 "// contacto y mezcla canales). Si la API no respondió, el que detectó Normalize.\n"
                 "let canal = n.canal || 'WhatsApp';\n"
                 "try {\n"
                 "  const r = $('GHL · Mensajes recientes').first().json || {};\n"
                 "  const raw = (r.messages && (r.messages.messages || r.messages)) || [];\n"
                 "  const ult = (Array.isArray(raw) ? raw : []).filter(m => m && m.direction === 'inbound')\n"
                 "    .sort((a, b) => (Date.parse(b.dateAdded || 0) || 0) - (Date.parse(a.dateAdded || 0) || 0))[0];\n"
                 "  const M = { TYPE_WHATSAPP: 'WhatsApp', TYPE_INSTAGRAM: 'IG', TYPE_FACEBOOK: 'FB' };\n"
                 "  if (ult && M[ult.messageType]) canal = M[ult.messageType];\n"
                 "} catch (e) { /* queda el de Normalize */ }\n"
                 "return [{ json: { texto, audio, canal } }];")

    # 3 · Enviar por el canal del lead
    e = p.node(wf, "Enviar WPP")
    p.replace_in(e, "type: 'WhatsApp', contactId:",
                 "type: ($('Separamos en partes').first().json.canal || " + N + ".canal || 'WhatsApp'), contactId:",
                 key="jsonBody")

    # 4 · Airtable Leads (legado): sin teléfono no se crea fila (antes: una por mensaje)
    ne = p.node(wf, "No existe")
    ne["parameters"]["conditions"]["conditions"].append({
        "id": str(uuid.uuid4()), "leftValue": "={{ " + N + ".wa_id }}", "rightValue": "",
        "operator": {"type": "string", "operation": "notEmpty", "singleValue": True}})
    ne["parameters"]["conditions"]["options"]["typeValidation"] = "loose"
    ne["notes"] = "IG-0924: exige teléfono (Leads de Airtable se buscan por teléfono)"

    # 5 · Guardrail: identificador aunque no haya teléfono
    for name in ("Alerta promesa fantasma", "Log guardrail hit"):
        p.json_replace(p.node(wf, name), N + ".wa_id", "(" + N + ".wa_id || " + N + ".session_key)")

    # 6 · W9 recibe canal + sessionKey
    a = p.node(wf, "Actualizar link")
    wi = a["parameters"]["workflowInputs"]
    wi["value"]["canal"] = "={{ $('Separamos en partes').first().json.canal || " + N + ".canal }}"
    wi["value"]["session_key"] = "={{ " + N + ".session_key }}"
    for k in ("canal", "session_key"):
        if not any(x["id"] == k for x in wi["schema"]):
            wi["schema"].append({"id": k, "displayName": k, "required": False, "defaultMatch": False,
                                 "display": True, "canBeUsedToMatch": True, "type": "string", "removed": False})
        if k not in wi["matchingColumns"]:
            wi["matchingColumns"].append(k)


def patch_w9(wf):
    t = next(n for n in wf["nodes"] if n["type"].endswith("executeWorkflowTrigger"))
    ex = json.loads(t["parameters"]["jsonExample"])
    ex.update({"canal": "WhatsApp", "session_key": "+5213312345678"})
    t["parameters"]["jsonExample"] = json.dumps(ex, ensure_ascii=False)
    n = p.node(wf, "Preparar payloads")
    p.replace_in(n, "const rescate_body = { first_name, programa_interes: programa, phone, contactId: contact_id, opportunityId };",
                 "const canal = (trig.canal || 'WhatsApp').toString();          // IG-0924\n"
                 "const session_key = (trig.session_key || '').toString();\n"
                 "const rescate_body = { first_name, programa_interes: programa, phone, contactId: contact_id, opportunityId, canal, session_key };")


def patch_rescate(wf):
    for name in ("Code: Fase 1 (GHL)", "Code: Fase 2 (GHL)"):
        n = p.node(wf, name)
        p.replace_in(n, "const session_key = '+' + nsk(phone);",
                     "const canal = (hook.canal || 'WhatsApp').toString(); /* IG-0924 */ "
                     "const session_key = hook.session_key || ('+' + nsk(phone));")
        p.replace_in(n, "programa, session_key } }];", "programa, session_key, canal } }];")
    p.replace_in(p.node(wf, "GHL: Send WhatsApp Fase 1"), "type: 'WhatsApp'",
                 "type: ($('Code: Fase 1 (GHL)').item.json.canal || 'WhatsApp')", key="jsonBody")
    # Fase 2 cae fuera de la ventana de 24 h de Instagram/Facebook: sólo por WhatsApp
    ag = p.node(wf, "IF: ¿ya agendó? (Fase 2)")
    send = p.node(wf, "GHL: Send WhatsApp Fase 2")
    gate = p.if_bool("¿Fase 2 por WhatsApp?", [send["position"][0] - 220, send["position"][1] + 160],
                     "={{ $('Code: Fase 2 (GHL)').item.json.canal === 'WhatsApp' }}")
    gate["notes"] = "IG-0924: IG/FB a +24 h está fuera de la ventana de Meta → sin envío, pero sí tag + etapa"
    wf["nodes"].append(gate)
    p.set_targets(wf, ag["name"], 1, [gate["name"]])
    p.set_targets(wf, gate["name"], 0, [send["name"]])
    p.set_targets(wf, gate["name"], 1, ["GHL: addTag link_abandonado_frio"])


def patch_despachador(wf):
    n = p.node(wf, "Seleccionar (tope-2 + prioridad)")
    p.replace_in(n, "const gate = (c) => {\n  if (booked.has(c.id)) return false;",
                 "const gate = (c) => {\n  if (booked.has(c.id)) return false;\n"
                 "  if (!c.phone) return false;   // IG-0924: las plantillas son de WhatsApp (contactos de Instagram sin teléfono)")


PATCHES = {"main": patch_main, "w9": patch_w9, "rescate": patch_rescate, "despachador": patch_despachador}


def main():
    execute = "--execute" in sys.argv
    for key, fn in PATCHES.items():
        wid = IDS[key]
        c, wf = p.api("GET", f"/workflows/{wid}")
        if c != 200:
            sys.exit(f"❌ GET {key} {c} {wf}")
        if MARK in json.dumps(wf, ensure_ascii=False):
            print(f"↷ {key}: ya aplicado"); continue
        pre = copy.deepcopy(wf)
        fn(wf)
        if not execute:
            print(f"[dry-run] {key} ({wf['name']}): ok"); continue
        h0 = p.save(pre, OUT / "pre" / f"{key}.json")
        body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
                "settings": {k: v for k, v in (wf.get("settings") or {}).items() if k in p.SETTINGS_OK}}
        c, r = p.api("PUT", f"/workflows/{wid}", body)
        if c != 200:
            sys.exit(f"❌ PUT {key} {c} {r}")
        c, post = p.api("GET", f"/workflows/{wid}")
        h1 = p.save(post, OUT / "post" / f"{key}.json")
        ok = MARK in json.dumps(post, ensure_ascii=False)
        print(f"{'✅' if ok else '❌'} {key}: activo={post['active']} · pre {h0[:12]} · post {h1[:12]}")


if __name__ == "__main__":
    main()
