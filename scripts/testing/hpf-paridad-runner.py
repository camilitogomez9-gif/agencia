#!/usr/bin/env python3
"""
Runner de evidencia del protocolo de paridad — Happy Flops.

Corre un caso contra el workflow VIVO y baja a disco la prueba de qué recibió
el lead. No usa channel:"test" (ese camino saltea el Sanitize y los 7 emisores,
o sea todo lo que el lead realmente ve).

La evidencia sale del runData de la API de n8n, que por cada nodo emisor trae el
input (message_part, photo_url), el orden, y el acuse real de la API de Telegram
o de GHL. Es un superconjunto de la tabla hpf_outbound_log que propone el
protocolo, y se obtiene sin tocar la topología del workflow.

Hechos del vivo medidos el 2026-08-05, sobre los que descansa este código:
  - El POST bloquea hasta que la ejecución termina y devuelve 200 con body
    vacío (Respond to Webhook no se alcanza en la rama Telegram).
  - `_probe_id` inyectado en el body sobrevive intacto hasta runData.
  - El acuse de Telegram es {ok:true, result:{message_id, chat, text}},
    NO {message_id} plano.
  - Telegram RECORTA el espacio final del texto. Por eso el contenido
    byte-exacto se afirma sobre message_part (lo que produjo el Sanitize),
    nunca sobre el texto entregado.
  - contact_id es a la vez la clave del debounce y la DIRECCIÓN DE ENTREGA.
    Namespearlo da aislamiento perfecto y cero entrega — es lo que produjo las
    140 partes sin entregar del 05/08 02:29. Se namespea `phone`, que es la
    sessionKey de la memoria y no se usa en ningún otro lado.

Uso:
    python3 scripts/testing/hpf-paridad-runner.py --caso HPF-SAL-001 --spec casos.yaml
    python3 scripts/testing/hpf-paridad-runner.py --smoke "quiero sandalias para mi boda"
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EVIDENCIA = REPO / "clients/HPF_HappyFlops/07_testing/evidencia"

# Los del loop emiten UNA parte del Sanitize cada uno: contra estos se cuenta la entrega.
EMISORES_LOOP = [
    "Send Photo (Telegram)",
    "Send Document (Telegram)",
    "Send Video (Telegram)",
    "Send a text message1",
    "Send Message via GHL",
]
# Estos cuelgan de la cadena post-loop y mandan contenido propio que NO sale del
# Sanitize (la imagen del evento y la promo). Solo existen en la rama GHL.
# Contarlos contra n_esperadas da "entregadas 4/2" y es un falso rojo.
EMISORES_POST = ["Send Imagen Principal", "Send Promo Evento"]
EMISORES = EMISORES_LOOP + EMISORES_POST
NODO_SANITIZE = "Sanitize + Split Output"
NODO_AGENTE = "Vendedor (LLM Agent)"
NODO_WEBHOOK = "Webhook - Inbound"

# Estados cerrados. No existe PENDIENTE.
PASA, FALLA, PARCIAL, SIN_EVIDENCIA, BLOQUEADO = (
    "PASA", "FALLA", "PARCIAL", "SIN-EVIDENCIA", "BLOQUEADO-POR-CANAL")


# --------------------------------------------------------------------------- entorno

def cargar_env() -> dict:
    env = {}
    for linea in (REPO / ".env").read_text().splitlines():
        linea = linea.strip()
        if linea and not linea.startswith("#") and "=" in linea:
            k, v = linea.split("=", 1)
            env[k] = v
    faltan = [k for k in ("HPF_N8N_API", "HPF_N8N_WORKFLOW_ID", "HPF_N8N_WEBHOOK_URL",
                          "HPF_WEBHOOK_AUTH_HEADER_NAME", "HPF_WEBHOOK_AUTH_HEADER_VALUE",
                          "HPF_TG_CHAT_ID") if not env.get(k)]
    if faltan:
        sys.exit(f"faltan en .env: {', '.join(faltan)}")
    return env


class N8N:
    def __init__(self, env: dict, api_key: str):
        self.base = env["HPF_N8N_API"]
        self.wf = env["HPF_N8N_WORKFLOW_ID"]
        self.key = api_key

    def _get(self, path: str, timeout: int = 60):
        req = urllib.request.Request(f"{self.base}/api/v1/{path}",
                                     headers={"X-N8N-API-KEY": self.key})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)

    def ultimo_execution_id(self) -> int:
        data = self._get(f"executions?workflowId={self.wf}&limit=1")["data"]
        return int(data[0]["id"]) if data else 0

    def ejecuciones_desde(self, last_id: int, limite: int = 20) -> list:
        return [e for e in self._get(f"executions?workflowId={self.wf}&limit={limite}")["data"]
                if int(e["id"]) > last_id]

    def ejecucion(self, eid) -> dict:
        return self._get(f"executions/{eid}?includeData=true")

    def version_actual(self) -> str:
        """versionId por el listado: barato. Bajar el workflow entero son 351 KB."""
        for w in self._get("workflows?limit=250")["data"]:
            if w["id"] == self.wf:
                return w.get("versionId", "")
        return ""


# --------------------------------------------------------------------------- acuses

def leer_acuse(salida: dict) -> dict:
    """Normaliza el acuse de un emisor. La forma real la medimos, no la supusimos."""
    result = salida.get("result")
    if isinstance(result, dict) and result.get("message_id"):
        chat = result.get("chat") or {}
        return {"canal": "telegram", "entregado": True,
                "message_id": result["message_id"],
                "chat_id": chat.get("id"),
                "texto_entregado": result.get("text") or result.get("caption") or "",
                "error": None}
    if salida.get("messageId") or salida.get("conversationId"):
        return {"canal": "ghl", "entregado": True,
                "message_id": salida.get("messageId"),
                "chat_id": salida.get("conversationId"),
                "texto_entregado": None,  # GHL no devuelve el texto en el acuse
                "error": None}
    if "error" in salida:
        return {"canal": None, "entregado": False, "message_id": None,
                "chat_id": None, "texto_entregado": None,
                "error": str(salida["error"])}
    return {"canal": None, "entregado": False, "message_id": None, "chat_id": None,
            "texto_entregado": None, "error": f"acuse no reconocido: {list(salida)[:8]}"}


def _primer_json(run_item: dict):
    try:
        return run_item["data"]["main"][0][0]["json"]
    except (KeyError, IndexError, TypeError):
        return None


# --------------------------------------------------------------------------- turno

def correr_turno(n8n: N8N, env: dict, *, lane_contact_id: str, session_id: str,
                 texto: str, canal: str = "telegram", stage: str = "Lead Nuevo",
                 media_url: str = "", message_type: str = "",
                 post_timeout: int = 300) -> dict:
    """
    Manda un turno y devuelve el artefacto de evidencia.

    lane_contact_id  la DIRECCIÓN de entrega (chat de Telegram o contacto de GHL).
                     Nunca se namespea: hacerlo rompe la entrega.
    session_id       la sessionKey de la memoria (campo `phone`). Sí se namespea:
                     es lo que aísla un caso de otro sin tocar la base.
    """
    if canal == "telegram":
        opportunity_id = f"tg_opp_{lane_contact_id}"
    else:
        opportunity_id = env.get("HPF_GHL_TEST_OPPORTUNITY_ID", "")
        if not opportunity_id:
            raise RuntimeError("canal ghl sin HPF_GHL_TEST_OPPORTUNITY_ID en .env")

    probe = f"{session_id}#{uuid.uuid4().hex[:12]}"
    version_antes = n8n.version_actual()
    last_id = n8n.ultimo_execution_id()

    cuerpo = {"contact_id": lane_contact_id, "opportunity_id": opportunity_id,
              "phone": session_id,
              # message_type explícito cuando el caso lo declara: es la única forma
              # de ejercer la rama fallback del Switch. Si no, se deriva del media.
              "message_type": message_type or ("image" if media_url else "text"),
              "message_text": texto, "stage": stage, "custom_fields": {},
              "_probe_id": probe}
    if media_url:
        cuerpo["media_url"] = media_url

    req = urllib.request.Request(
        env["HPF_N8N_WEBHOOK_URL"], data=json.dumps(cuerpo).encode(),
        headers={"Content-Type": "application/json",
                 env["HPF_WEBHOOK_AUTH_HEADER_NAME"]: env["HPF_WEBHOOK_AUTH_HEADER_VALUE"]})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=post_timeout) as r:
            http = r.status
    except urllib.error.HTTPError as e:
        http = e.code
    except Exception as e:                                    # noqa: BLE001
        http = f"EXCEPCION {type(e).__name__}: {e}"
    segundos_post = round(time.time() - t0, 1)

    # Correlación por token, nunca por ventana de tiempo: el reloj de la notebook
    # y el de n8n no son el mismo (medido: +0.9 s de skew).
    hallada = None
    for _ in range(25):
        for e in n8n.ejecuciones_desde(last_id):
            det = n8n.ejecucion(e["id"])
            run = det.get("data", {}).get("resultData", {}).get("runData", {})
            wh = run.get(NODO_WEBHOOK)
            if not wh:
                continue
            j = _primer_json(wh[0]) or {}
            if (j.get("body") or {}).get("_probe_id") == probe:
                hallada = (e["id"], det, run)
                break
        if hallada:
            break
        time.sleep(4)

    art = {
        "probe_id": probe, "session_id": session_id, "contact_id": lane_contact_id,
        "canal": canal, "texto_enviado": texto, "media_url": media_url or None,
        "http": http, "segundos_post": segundos_post,
        "version_antes": version_antes, "version_despues": n8n.version_actual(),
        "capturado_utc": datetime.now(timezone.utc).isoformat(),
    }
    if not hallada:
        art.update({"execution_id": None, "estado_turno": SIN_EVIDENCIA,
                    "motivo": "execution_not_found"})
        return art

    eid, det, run = hallada
    art["execution_id"] = eid
    art["status_n8n"] = det["status"]
    art["startedAt"] = det["startedAt"]
    art["stoppedAt"] = det.get("stoppedAt")

    # Regla 1: la cantidad esperada sale del Sanitize, NO de los emisores que
    # corrieron. Contar sobre los emisores presentes es circular: un emisor que
    # no corrió no genera parte y por lo tanto no puede fallar.
    san = run.get(NODO_SANITIZE)
    if san:
        partes_esperadas = [p.get("json", {}) for p in (san[0]["data"]["main"][0] or [])]
    else:
        partes_esperadas = []
    art["n_esperadas"] = len(partes_esperadas)
    art["partes_esperadas"] = [
        {"idx": i,
         "message_part": p.get("message_part"),
         "photo_url": p.get("photo_url") or None,
         "doc_url": p.get("doc_url") or None,
         "video_url": p.get("video_url") or None}
        for i, p in enumerate(partes_esperadas)]

    emitidas, post = [], []
    for nombre in EMISORES:
        for idx, item in enumerate(run.get(nombre, [])):
            salida = _primer_json(item)
            reg = {"emisor": nombre, "run": idx,
                   "ms": item.get("executionTime"),
                   "reintentos_posibles": (item.get("executionTime") or 0) > 5000}
            reg.update(leer_acuse(salida) if salida is not None
                       else {"entregado": False, "error": "sin json de salida"})
            (post if nombre in EMISORES_POST else emitidas).append(reg)
    art["partes_emitidas"] = emitidas
    art["n_entregadas"] = sum(1 for p in emitidas if p.get("entregado"))
    # La cadena post-loop manda contenido que no sale del Sanitize (imagen del
    # evento, promo). Se guarda aparte para que no falsee el conteo de entrega,
    # pero sí entra en las búsquedas de texto: el menú viaja como caption de ahí.
    art["partes_post"] = post
    # GHL devuelve {conversationId, messageId, traceId} y NO el texto: el acuse
    # prueba que GHL aceptó, no qué se mandó. El contenido de la cadena post-loop
    # se lee de la entrada del emisor — `Check Evento Just Set` produce
    # `descripcion` (el menú) y `promoText`, que es literalmente lo que se envía.
    textos = [p.get("texto_entregado") for p in post if p.get("texto_entregado")]
    ctx = run.get("Check Evento Just Set")
    if ctx:
        j = _primer_json(ctx[0]) or {}
        for campo in ("descripcion", "promoText"):
            if j.get(campo):
                textos.append(j[campo])
        art["contexto_post"] = {k: j.get(k) for k in ("currentEvento", "justSet", "imagenUrl")}
    art["textos_post"] = textos

    # Regla 2: cero partes es FALLA, no "no medido". El Sanitize puede devolver []
    # y dejar al lead sin nada, con la ejecución en verde.
    art["cero_partes"] = art["n_esperadas"] == 0

    # Regla 5: el output crudo del agente es el único lugar donde se distingue
    # "el modelo obedeció" de "el regex del Sanitize nos tapó". Se guarda entero.
    ag = run.get(NODO_AGENTE)
    if ag:
        j = _primer_json(ag[0]) or {}
        pasos = j.get("intermediateSteps") or []
        art["agente"] = {
            "output": j.get("output"),
            "tools": [p.get("action", {}).get("tool") for p in pasos],  # igualdad, no substring
        }
    else:
        art["agente"] = {"output": None, "tools": []}

    return art


# --------------------------------------------------------------------------- asserts

def entrega_ok(art: dict, chat_esperado: str | None = None) -> tuple[str, str]:
    """Regla 1 + regla 4: todas las partes del Sanitize entregadas, y al destinatario correcto."""
    if art.get("estado_turno") == SIN_EVIDENCIA:
        return SIN_EVIDENCIA, art.get("motivo", "")
    if art["n_esperadas"] == 0:
        return FALLA, "el Sanitize no emitió ninguna parte: el lead no recibió nada"
    if art["n_entregadas"] != art["n_esperadas"]:
        errores = {p.get("error") for p in art["partes_emitidas"] if p.get("error")}
        return FALLA, (f"entregadas {art['n_entregadas']}/{art['n_esperadas']}"
                       + (f" · {'; '.join(str(e)[:60] for e in errores if e)}" if errores else ""))
    if chat_esperado:
        malas = [p for p in art["partes_emitidas"]
                 if p.get("canal") == "telegram" and str(p.get("chat_id")) != str(chat_esperado)]
        if malas:
            return FALLA, f"entregado al chat equivocado: {malas[0].get('chat_id')} != {chat_esperado}"
    return PASA, f"{art['n_entregadas']}/{art['n_esperadas']} entregadas"


def contiene_verbatim(art: dict, needle: str, *, scope: str = "parte") -> tuple[str, str]:
    """
    Byte-exacto, sin normalizar. Nada de strip/trim/colapsar espacios: los defectos
    preservados a propósito (NBSP, doble espacio antes del emoji) SON la paridad.

    Se afirma sobre message_part, no sobre el texto entregado: Telegram recorta el
    espacio final (medido el 2026-08-05).
    """
    partes = [p.get("message_part") or "" for p in art.get("partes_esperadas", [])]
    # El caption de la imagen del evento y la promo no salen del Sanitize; en la
    # rama GHL el menú de productos viaja ahí. Si no se incluyen, un needle real
    # se reporta como ausente.
    partes = partes + [t for t in (art.get("textos_post") or []) if t]
    if not partes:
        return SIN_EVIDENCIA, "sin partes que inspeccionar"
    n = needle.encode()
    if scope == "turno_concatenado":
        # El vivo parte captions largos: un needle puede cruzar el corte.
        heno = "\n".join(partes).encode()
        return (PASA, "hallado en el turno") if n in heno else (FALLA, _diff(partes, needle))
    for i, p in enumerate(partes):
        if n in p.encode():
            return PASA, f"hallado en parte {i}"
    return FALLA, _diff(partes, needle)


def no_contiene(art: dict, needle: str, *, scope: str = "parte") -> tuple[str, str]:
    """Regla 3: un negativo NO puede pasar por ausencia de partes."""
    if not art.get("partes_esperadas"):
        return SIN_EVIDENCIA, "sin partes: el negativo no se puede evaluar"
    estado, det = contiene_verbatim(art, needle, scope=scope)
    if estado == SIN_EVIDENCIA:
        return SIN_EVIDENCIA, det
    return (FALLA, f"apareció {needle!r}: {det}") if estado == PASA else (PASA, "ausente")


def tool_invocada(art: dict, nombre: str) -> tuple[str, str]:
    """Igualdad sobre action.tool. Nunca `nombre in json.dumps(steps)`: eso matchea
    contra el texto de un error o contra el argumento de otra tool."""
    tools = art.get("agente", {}).get("tools") or []
    return (PASA, f"tools={tools}") if nombre in tools else (FALLA, f"tools={tools}")


def tool_no_invocada(art: dict, nombre: str) -> tuple[str, str]:
    tools = art.get("agente", {}).get("tools")
    if tools is None:
        return SIN_EVIDENCIA, "sin intermediateSteps (¿returnIntermediateSteps apagado?)"
    return (FALLA, f"se invocó {nombre}") if nombre in tools else (PASA, f"tools={tools}")


def _diff(partes: list[str], needle: str) -> str:
    """La parte con mayor prefijo común, no la más larga: el diff tiene que ser útil."""
    mejor, mejor_n = "", -1
    for p in partes:
        comun = 0
        for a, b in zip(p, needle):
            if a != b:
                break
            comun += 1
        if comun > mejor_n:
            mejor, mejor_n = p, comun
    return (f"no hallado; mejor coincidencia diverge en el byte {mejor_n}: "
            f"esperado {needle[mejor_n:mejor_n+18]!r} vs recibido {mejor[mejor_n:mejor_n+18]!r}")


# --------------------------------------------------------------------------- persistencia

def guardar(art: dict, caso: str, turno: int) -> Path:
    d = EVIDENCIA / caso
    d.mkdir(parents=True, exist_ok=True)
    n = 1
    while (p := d / f"turno_{turno}.attempt{n}.json").exists():   # regla 8: nunca sobrescribir
        n += 1
    p.write_text(json.dumps(art, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


BUILD = REPO / "clients/HPF_HappyFlops/03_workflows/hpf-inbound-handler-testbuild-nodebounce-2026-08-05.json"
SPEC = REPO / "clients/HPF_HappyFlops/07_testing/casos.json"


def sha_baseline() -> str:
    return hashlib.sha256(BUILD.read_bytes()).hexdigest() if BUILD.exists() else ""


# --------------------------------------------------------------------- needles

def resolver_needles() -> dict:
    """
    Regla 7: los esperados NO se transcriben a mano — se re-extraen del build
    congelado. Una transcripción a `casos.json` mataría el NBSP, el doble espacio
    antes del emoji y el espacio final, que es justo lo que se está midiendo.
    """
    d = json.loads(BUILD.read_text(encoding="utf-8"))
    js = {n["name"]: n for n in d["nodes"]}[NODO_SANITIZE]["parameters"]["jsCode"]
    n: dict[str, str] = {}

    m = re.search(r"const SALUDO_PARTES = \[\s*(.*?)\s*\];", js, re.S)
    if m:
        for i, parte in enumerate(re.findall(r"'((?:[^'\\]|\\.)*)'", m.group(1))):
            n[f"SALUDO_{i}"] = parte.replace("\\n", "\n").replace("\\'", "'")

    # Ojo: hay tres mapas distintos con claves BODA/XV/OTROS (imagen principal,
    # menú de productos, alias). El menú se ancla por contenido, no por posición.
    for ev in ("BODA", "XV", "OTROS"):
        m = re.search(rf"^\s*{ev}\s*:\s*'(TENEMOS ESTOS PRODUCTOS(?:[^'\\]|\\.)*)'", js, re.M)
        if m:
            n[f"MENU_{ev}"] = m.group(1).replace("\\n", "\n").replace("\\'", "'")

    m = re.search(r"const SIETE_PASOS = '((?:[^'\\]|\\.)*)'", js)
    if m:
        n["SIETE_PASOS"] = m.group(1).replace("\\n", "\n").replace("\\'", "'")

    cur = None
    for linea in js.split("\n"):
        mi = re.search(r'id:"([^"]+)"', linea)
        if mi:
            cur = mi.group(1)
        mf = re.search(r'\bf:"((?:[^"\\]|\\.)*)"', linea)
        if mf and cur:
            n[f"FICHA_{cur}"] = mf.group(1).replace("\\n", "\n").replace('\\"', '"')
            cur = None
    return n


# --------------------------------------------------------------------- casos

def evaluar(caso: dict, arts: list[dict], needles: dict, lane: str) -> tuple[str, list]:
    """Evalúa los asserts sobre el ÚLTIMO turno salvo que el assert diga otra cosa."""
    res = []
    ult = arts[-1]

    for a in caso.get("asserts", []):
        t = a["t"]
        art = arts[a["turno"] - 1] if a.get("turno") else ult

        if t == "entrega":
            e, det = entrega_ok(art, chat_esperado=lane if caso["canal"] == "telegram" else None)
        elif t == "minpartes":
            n = art.get("n_esperadas", 0)
            e, det = (PASA, f"{n} partes") if n >= a["v"] else (FALLA, f"solo {n} partes, se esperaban >= {a['v']}")
        elif t in ("tiene", "no"):
            if a.get("n"):
                needle = needles.get(a["n"])
                if needle is None:
                    e, det = SIN_EVIDENCIA, f"needle {a['n']} no existe en el build"
                    res.append((f"{t}:{a.get('n') or a.get('lit')}", e, det)); continue
            else:
                needle = a["lit"]
            if a.get("ci"):                                  # solo para negativos sobre texto libre
                partes = [(p.get("message_part") or "").lower() for p in art.get("partes_esperadas", [])]
                hay = any(needle.lower() in p for p in partes)
                if not art.get("partes_esperadas"):
                    e, det = SIN_EVIDENCIA, "sin partes"
                else:
                    ok = hay if t == "tiene" else not hay
                    e, det = (PASA, "ok") if ok else (FALLA, f"{'no aparece' if t=='tiene' else 'aparece'} {needle!r}")
            else:
                e, det = (contiene_verbatim if t == "tiene" else no_contiene)(art, needle)
        elif t == "tool":
            e, det = tool_invocada(art, a["v"])
        elif t == "notool":
            e, det = tool_no_invocada(art, a["v"])
        elif t in ("media", "nomedia"):
            hay = any(p.get(a["v"]) for p in art.get("partes_esperadas", []))
            if not art.get("partes_esperadas"):
                e, det = SIN_EVIDENCIA, "sin partes"
            else:
                ok = hay if t == "media" else not hay
                e, det = (PASA, "ok") if ok else (FALLA, f"{'falta' if t=='media' else 'sobra'} {a['v']}")
        else:
            e, det = SIN_EVIDENCIA, f"assert desconocido: {t}"
        res.append((f"{t}:{a.get('n') or a.get('lit') or a.get('v') or ''}"[:46], e, det))

    estados = [r[1] for r in res]
    if any(s == SIN_EVIDENCIA for s in estados):
        final = SIN_EVIDENCIA
    elif all(s == PASA for s in estados):
        final = PASA
    elif any(s == PASA for s in estados):
        final = PARCIAL
    else:
        final = FALLA
    return final, res


def correr_caso(n8n: N8N, env: dict, caso: dict, needles: dict) -> dict:
    lane = (env["HPF_TG_CHAT_ID"] if caso["canal"] == "telegram"
            else env["HPF_GHL_TEST_CONTACT_ID"])
    session = f"sess_{caso['id'].lower().replace('-', '_')}_{int(time.time())}"
    arts = []
    for i, turno in enumerate(caso["turnos"], 1):
        if isinstance(turno, str):
            turno = {"texto": turno}
        art = correr_turno(n8n, env, lane_contact_id=lane, session_id=session,
                           texto=turno.get("texto", ""), canal=caso["canal"],
                           media_url=turno.get("media_url", ""),
                           message_type=turno.get("message_type", ""))
        art["baseline_sha256"] = sha_baseline()
        art["caso"] = caso["id"]
        guardar(art, caso["id"], i)
        arts.append(art)
        if art.get("estado_turno") == SIN_EVIDENCIA:
            break
    estado, detalle = evaluar(caso, arts, needles, lane)
    return {"id": caso["id"], "sev": caso["sev"], "canal": caso["canal"],
            "estado": estado, "asserts": detalle, "turnos": len(arts),
            "fuera": caso.get("fuera_denominador", False),
            "version": arts[-1].get("version_antes") if arts else None}


# --------------------------------------------------------------------------- cli

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", help="manda un solo mensaje y muestra la evidencia")
    ap.add_argument("--canal", default="telegram", choices=["telegram", "ghl"])
    ap.add_argument("--caso", default="SMOKE")
    ap.add_argument("--session", help="sessionKey; por defecto una nueva")
    ap.add_argument("--todos", action="store_true", help="corre todos los casos del spec")
    ap.add_argument("--solo", help="corre solo estos ids, separados por coma")
    ap.add_argument("--jsonl", default="/tmp/hpf-fase2.jsonl")
    args = ap.parse_args()

    env = cargar_env()
    api_key = os.environ.get("HPF_N8N_API_KEY")
    if not api_key:
        sys.exit("exportá HPF_N8N_API_KEY antes de correr")
    n8n = N8N(env, api_key)

    if args.todos or args.solo:
        needles = resolver_needles()
        spec = json.loads(SPEC.read_text(encoding="utf-8"))
        casos = spec["casos"]
        if args.solo:
            pedidos = {x.strip() for x in args.solo.split(",")}
            casos = [c for c in casos if c["id"] in pedidos]
        if spec["_meta"]["sha256"] != sha_baseline():
            sys.exit("el build cambió respecto al spec congelado: parar y re-decidir")
        print(f"needles resueltos del build: {len(needles)}")
        print(f"casos a correr: {len(casos)}\n")
        salida = Path(args.jsonl)
        for i, caso in enumerate(casos, 1):
            if caso["canal"] == "ghl" and not env.get("HPF_GHL_TEST_CONTACT_ID"):
                r = {"id": caso["id"], "sev": caso["sev"], "canal": "ghl",
                     "estado": BLOQUEADO, "asserts": [], "fuera": False}
            else:
                r = correr_caso(n8n, env, caso, needles)
            with salida.open("a") as fh:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
            marca = {"PASA": "OK  ", "FALLA": "FALLA", "PARCIAL": "PARC",
                     "SIN-EVIDENCIA": "S/EV", "BLOQUEADO-POR-CANAL": "BLOQ"}[r["estado"]]
            print(f"[{i:>2}/{len(casos)}] {marca} {r['id']:<14} {r['sev']}")
            for nombre, est, det in r["asserts"]:
                if est != PASA:
                    print(f"          · {nombre:<44} {est}: {det[:96]}")
        return

    if not args.smoke:
        sys.exit("usá --todos, --solo <ids> o --smoke")

    lane = (env["HPF_TG_CHAT_ID"] if args.canal == "telegram"
            else env["HPF_GHL_TEST_CONTACT_ID"])
    session = args.session or f"sess_{args.caso.lower()}_{int(time.time())}"

    art = correr_turno(n8n, env, lane_contact_id=lane, session_id=session,
                       texto=args.smoke, canal=args.canal)
    art["baseline_sha256"] = sha_baseline()
    ruta = guardar(art, args.caso, 1)

    print(f"HTTP {art['http']} en {art['segundos_post']}s · exec {art.get('execution_id')} "
          f"· version {art.get('version_antes')}")
    print(f"partes: Sanitize emitió {art.get('n_esperadas')} · entregadas {art.get('n_entregadas')}")
    for p in art.get("partes_emitidas", []):
        marca = "OK " if p.get("entregado") else "ERR"
        print(f"  [{marca}] {p['emisor']} #{p['run']} "
              f"msg_id={p.get('message_id')} {str(p.get('error') or '')[:60]}")
    print(f"tools: {art['agente']['tools']}")
    est, det = entrega_ok(art, chat_esperado=lane if args.canal == "telegram" else None)
    print(f"entrega_ok -> {est} ({det})")
    print(f"evidencia: {ruta.relative_to(REPO)}")


if __name__ == "__main__":
    main()
