#!/usr/bin/env python3
"""N9 (preparado 24/9, NO aplicado) · El system prompt del agente se lee de un Google Doc editable (pedido de Max).
Marca: PROMPT-DOC-0924.

Mismo objetivo que SYS, con un arreglo: en SYS, si el Doc falla, el camino de respaldo pasa por el Telegram
antes del agente y el agente lee `$json.backup` de la salida del Telegram, que no lo trae → prompt vacío. Acá el
prompt lo elige un Code node y el agente lo lee de ese nodo por nombre, pase por donde pase.

Topología nueva en el main `1eS1Z5k898c3ATnf` (entre `¿Bot pausado?` [salida "no"] y `Agente IA WPP`):

  ¿Bot pausado? ──no──► Prompt · Google Doc ──► Elegir prompt ──► ¿Prompt de respaldo? ──no──► Agente IA WPP
                        (googleDocs get,         (valida el Doc;        │
                         sigue aunque falle)      si falla → respaldo)  └──sí──► Aviso prompt respaldo ──► Agente IA WPP
                                                                                  (Telegram botla agencia 6390727286)

  · `Agente IA WPP` → systemMessage = `{{ $('Elegir prompt').first().json.system_prompt }}`.
  · Respaldo = el texto de `--respaldo` (por defecto el prompt v2.3 del repo) embebido en `Elegir prompt`.
  · El Doc se considera roto si: no respondió, tiene menos de 15.000 caracteres, o le falta alguna de las
    partes que el sistema necesita ("[ESTADO DEL LEAD]", el título "## 📲 Enlaces de asesoría", el link
    "agendar-ema" y la regla "No agendo yo"). En ese caso
    se usa el respaldo y llega un Telegram con el motivo (uno por mensaje mientras siga roto).

Uso:
  python3 vtr_9_prompt_google_docs.py --doc-url <URL del Doc>                         dry-run (valida y muestra)
  python3 vtr_9_prompt_google_docs.py --doc-url <URL> --execute                       aplica (pre/post con sha256)
  python3 vtr_9_prompt_google_docs.py --doc-url <URL> --respaldo <archivo> --execute  otro respaldo (ej. v2.4)
  python3 vtr_9_prompt_google_docs.py --actualizar-respaldo <archivo> --execute       sólo cambia el respaldo
  python3 vtr_9_prompt_google_docs.py --rollback --execute                              vuelve al main de antes
Rollback: `--rollback --execute` hace PUT de ghl-live-2026-09-24-agente-link/pre/main-n9.json (el prompt vuelve a quedar
fijo en el nodo, como hoy).
"""
import copy, json, sys, uuid, importlib.util
from pathlib import Path

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("p", HERE.parent / "batches-2026-09-23" / "vtr_pre_bsp_fixes.py")
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)

MARK = "PROMPT-DOC-0924"
MAIN = "1eS1Z5k898c3ATnf"
OUT = p.ROOT / "clients/VTR_Venttur/03_workflows/ghl-live-2026-09-24-agente-link"
RESPALDO_DEF = p.ROOT / "clients/VTR_Venttur/04_agents/agente-venttur-system-prompt-v2.3.md"
GDOCS_CRED = {"googleDocsOAuth2Api": {"id": "LuHm4iiDhCNWvSqM", "name": "la agencia v2"}}   # la misma de Cereza / Reporte Semanal
TG_CRED = {"telegramApi": {"id": "V5k84z3AjQc9Y5yg", "name": "botla agencia"}}             # la de "Alerta promesa fantasma"
AGENTE, PAUSA = "Agente IA WPP", "¿Bot pausado?"
N_DOC, N_ELEGIR, N_IF, N_AVISO = "Prompt · Google Doc", "Elegir prompt", "¿Prompt de respaldo?", "Aviso prompt respaldo"
MARCAS = ["[ESTADO DEL LEAD]", "## 📲 Enlaces de asesoría", "agendar-ema", "No agendo yo"]
MIN_LEN = 15000


def arg(name):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else None


def code_elegir(respaldo):
    return (
        f"// Elegir prompt — {MARK}. El system prompt sale del Google Doc; si el Doc no respondió o parece roto,\n"
        "// se usa el RESPALDO (versión congelada) y el IF de abajo manda un Telegram con el motivo.\n"
        f"const RESPALDO = {json.dumps(respaldo, ensure_ascii=False)};\n"
        f"const MARCAS = {json.dumps(MARCAS, ensure_ascii=False)};\n"
        f"const MIN_LEN = {MIN_LEN};\n"
        "let doc = '';\n"
        f"try {{ doc = String(($('{N_DOC}').first().json || {{}}).content || ''); }} catch (e) {{ doc = ''; }}\n"
        "doc = doc.replace(/\\r\\n/g, '\\n').trim();\n"
        "let motivo = '';\n"
        "if (!doc) motivo = 'el Google Doc no respondió (¿credencial vencida o sin acceso?)';\n"
        "else if (doc.length < MIN_LEN) motivo = `el Google Doc tiene ${doc.length} caracteres (mínimo ${MIN_LEN})`;\n"
        "else { const f = MARCAS.filter(m => !doc.includes(m)); if (f.length) motivo = 'al Google Doc le faltan: ' + f.join(', '); }\n"
        "return [{ json: { system_prompt: motivo ? RESPALDO : doc, fuente: motivo ? 'respaldo' : 'doc', motivo,\n"
        "                  largo: (motivo ? RESPALDO : doc).length } }];\n")


def nodos(doc_url, respaldo, base):
    x, y = base
    doc = {"parameters": {"operation": "get", "documentURL": doc_url}, "name": N_DOC,
           "type": "n8n-nodes-base.googleDocs", "typeVersion": 2, "position": [x, y + 200], "id": str(uuid.uuid4()),
           "credentials": copy.deepcopy(GDOCS_CRED), "onError": "continueRegularOutput", "alwaysOutputData": True,
           "executeOnce": True, "notes": MARK + ": instrucciones del agente (editables por Venttur)"}
    elegir = p.code_node(N_ELEGIR, [x + 220, y + 200], code_elegir(respaldo))
    elegir["executeOnce"] = True
    gate = p.if_bool(N_IF, [x + 440, y + 200], f"={{{{ $('{N_ELEGIR}').first().json.fuente === 'respaldo' }}}}")
    aviso = {"parameters": {"chatId": "6390727286",
                            "text": f"=⚠️ VTR · el agente está usando el prompt de RESPALDO: {{{{ $('{N_ELEGIR}').first().json.motivo }}}}",
                            "additionalFields": {"appendAttribution": False}},
             "name": N_AVISO, "type": "n8n-nodes-base.telegram", "typeVersion": 1.2, "position": [x + 660, y + 320],
             "id": str(uuid.uuid4()), "credentials": copy.deepcopy(TG_CRED), "continueOnFail": True}
    return doc, elegir, gate, aviso


def patch(wf, doc_url, respaldo):
    if p.has(wf, N_DOC):
        raise RuntimeError("ya aplicado")
    if [t["node"] for t in wf["connections"][PAUSA]["main"][1]] != [AGENTE]:
        raise RuntimeError("cadena inesperada en ¿Bot pausado?")
    ag = p.node(wf, AGENTE)
    doc, elegir, gate, aviso = nodos(doc_url, respaldo, p.node(wf, PAUSA)["position"])
    wf["nodes"] += [doc, elegir, gate, aviso]
    p.set_targets(wf, PAUSA, 1, [N_DOC])
    p.set_targets(wf, N_DOC, 0, [N_ELEGIR])
    p.set_targets(wf, N_ELEGIR, 0, [N_IF])
    p.set_targets(wf, N_IF, 0, [N_AVISO])     # sí, respaldo → aviso → agente
    p.set_targets(wf, N_IF, 1, [AGENTE])      # no → agente
    p.set_targets(wf, N_AVISO, 0, [AGENTE])
    ag["parameters"]["options"]["systemMessage"] = f"={{{{ $('{N_ELEGIR}').first().json.system_prompt }}}}"


def put(wf, pre, tag):
    h0 = p.save(pre, OUT / "pre" / f"main-{tag}.json")
    body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
            "settings": {k: v for k, v in (wf.get("settings") or {}).items() if k in p.SETTINGS_OK}}
    c, r = p.api("PUT", f"/workflows/{MAIN}", body)
    if c != 200:
        sys.exit(f"❌ PUT {c} {r}")
    c, post = p.api("GET", f"/workflows/{MAIN}")
    h1 = p.save(post, OUT / "post" / f"main-{tag}.json")
    print(f"✅ activo={post['active']} · nodos {len(pre['nodes'])} → {len(post['nodes'])} · pre {h0[:12]} · post {h1[:12]}")


def main():
    execute = "--execute" in sys.argv
    c, wf = p.api("GET", f"/workflows/{MAIN}")
    if c != 200:
        sys.exit(f"❌ GET {c} {wf}")
    pre = copy.deepcopy(wf)
    if "--rollback" in sys.argv:
        f = OUT / "pre" / "main-n9.json"
        old = json.loads(f.read_text())
        print(f"rollback ← {f} ({len(old['nodes'])} nodos)")
        if not execute:
            return print("[dry-run] ok")
        return put(old, pre, "n9-rollback")
    nuevo_resp = arg("--actualizar-respaldo")
    if nuevo_resp:
        n = p.node(wf, N_ELEGIR)
        n["parameters"]["jsCode"] = code_elegir(Path(nuevo_resp).read_text())
        print(f"respaldo → {nuevo_resp} ({len(Path(nuevo_resp).read_text())} chars)")
        return put(wf, pre, "n9-respaldo") if execute else print("[dry-run] ok")
    doc_url = arg("--doc-url") or "https://docs.google.com/document/d/REEMPLAZAR/edit"
    respaldo = Path(arg("--respaldo") or RESPALDO_DEF).read_text()
    faltan = [m for m in MARCAS if m not in respaldo]
    if faltan or len(respaldo) < MIN_LEN:
        sys.exit(f"❌ el respaldo no pasa su propia validación: faltan {faltan}, {len(respaldo)} chars")
    patch(wf, doc_url, respaldo)
    print(f"[{'execute' if execute else 'dry-run'}] nodos {len(pre['nodes'])} → {len(wf['nodes'])} · respaldo "
          f"{len(respaldo)} chars · doc {doc_url}")
    if execute:
        if "REEMPLAZAR" in doc_url:
            sys.exit("❌ falta --doc-url")
        put(wf, pre, "n9")


if __name__ == "__main__":
    main()
