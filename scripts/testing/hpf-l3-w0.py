#!/usr/bin/env python3
"""
HPF · L3 — Gate de W0 · GHL Client.

Dos condiciones para cerrar L3:
  1. Los asserts de L2 siguen pasando, pero AHORA a través de W0 (mismo read-back real).
  2. Un pedido inválido FALLA LA EJECUCIÓN. No devuelve texto de error como si fuera
     un resultado — que es exactamente lo que rompió el intento anterior.

Artefactos crudos en 07_testing/evidencia-migracion/L3/<caso>.json
"""
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EVID = REPO / "clients/HPF_HappyFlops/07_testing/evidencia-migracion/L3"
W0 = "https://[TU-INSTANCIA-N8N]/webhook/hpf-w0-ghl-client"
GHL = "https://services.leadconnectorhq.com"

CONTACTO = "3tzzBVjsKlOF2RJjKNOL"
OPORTUNIDAD = "vzYAb3P86uJ08CI9jKyV"
JPG = ("https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/"
       "94d1527d-83d1-40e2-bfac-05dd969c3ea7.jpg")

RES = []


def env():
    e = {}
    for line in (REPO / ".env").read_text().splitlines():
        if line.strip() and not line.strip().startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            e[k.strip()] = v.strip().strip('"').strip("'")
    return e


E = env()
H_W0 = {"Content-Type": "application/json",
        E["HPF_WEBHOOK_AUTH_HEADER_NAME"]: E["HPF_WEBHOOK_AUTH_HEADER_VALUE"]}
H_GHL = {"Authorization": f"Bearer {E['GHL_API_KEY']}", "Version": "2021-07-28",
         "User-Agent": "curl/8.7.1"}


def w0(op, args):
    body = {"op": op, "args": args}
    req = urllib.request.Request(W0, data=json.dumps(body).encode(),
                                 headers=H_W0, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read().decode() or "null"), body
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw), body
        except json.JSONDecodeError:
            return e.code, {"_raw": raw[:500]}, body


def ghl_get(path):
    req = urllib.request.Request(GHL + path, headers=H_GHL)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"_error": e.code, "_raw": e.read().decode()[:300]}


def prim(resp):
    """W0 devuelve una lista de un item cuando responde por webhook."""
    if isinstance(resp, list) and resp:
        return resp[0]
    return resp if isinstance(resp, dict) else {}


def reg(cid, titulo, ok, detalle, pasos):
    EVID.mkdir(parents=True, exist_ok=True)
    EVID.joinpath(f"{cid}.json").write_text(json.dumps(
        {"caso": cid, "titulo": titulo,
         "resultado": "CORROBORADO" if ok else "FALLA",
         "detalle": detalle, "pasos": pasos}, indent=2, ensure_ascii=False), encoding="utf-8")
    RES.append((cid, titulo, ok))
    print(f"  {'✅' if ok else '❌'} {cid} {titulo}\n       {detalle}")


# ── positivos: los contratos de L2, ahora vía W0 ──────────────────────────

def g01():
    s, r, b = w0("get_opportunity", {"opportunityId": OPORTUNIDAD})
    d = prim(r)
    ok = s == 200 and d.get("ok") and d["data"]["opportunity"]["id"] == OPORTUNIDAD
    reg("G-01", "get_opportunity", ok, f"http={s} ok={d.get('ok')}", [{"req": b, "resp": r}])


def g02():
    s, r, b = w0("upsert_contact", {"phone": "+5213300000199", "name": "ZZ Test Migracion GHL",
                                    "tags": ["lead_prueba"]})
    d = prim(r)
    ok = s == 200 and d.get("ok") and d["data"]["contact"]["id"] == CONTACTO
    reg("G-02", "upsert_contact (dedup por teléfono)", ok,
        f"http={s} id={d.get('data', {}).get('contact', {}).get('id')}", [{"req": b, "resp": r}])


def g03():
    s, r, b = w0("find_or_create_opportunity", {"contactId": CONTACTO})
    d = prim(r)
    ok = s == 200 and d.get("ok") and d["data"]["opportunity"]["id"] == OPORTUNIDAD
    reg("G-03", "find_or_create_opportunity", ok,
        f"http={s} via={d.get('via')} id={d.get('data', {}).get('opportunity', {}).get('id')} "
        f"→ el 400 OPPORTUNITY_NO_DUPLICATE se traduce a éxito", [{"req": b, "resp": r}])


def g04():
    pasos = []
    for etapa in ("Cotizado", "Ventas Perdidas", "Lead Nuevo"):
        s, r, b = w0("update_stage", {"opportunityId": OPORTUNIDAD, "etapa": etapa})
        got = ghl_get(f"/opportunities/{OPORTUNIDAD}")["opportunity"]["pipelineStageId"]
        esperado = prim(r).get("data", {}).get("opportunity", {}).get("pipelineStageId")
        pasos.append({"etapa": etapa, "req": b, "http": s, "stage_leido": got})
        if got != esperado:
            reg("G-04", "update_stage por nombre de etapa", False,
                f"{etapa}: leí {got} esperaba {esperado}", pasos)
            return
    reg("G-04", "update_stage por nombre de etapa", True,
        "3 etapas movidas y releídas OK (acepta nombre, no sólo UUID)", pasos)


def g05():
    cent = f"L3-{int(time.time())}"
    s, r, b = w0("update_cf", {"opportunityId": OPORTUNIDAD,
                               "campos": {"productos_mostrados": cent, "cp_entrega": "44100"}})
    got = {c["id"]: c.get("fieldValue")
           for c in ghl_get(f"/opportunities/{OPORTUNIDAD}")["opportunity"]["customFields"]}
    ok = s == 200 and got.get("IukLzqy6bZCCtuJTPzBu") == cent
    reg("G-05", "update_cf texto por clave (no por id)", ok,
        f"http={s} leído={got.get('IukLzqy6bZCCtuJTPzBu')!r}", [{"req": b, "resp": r}])


def g06():
    s, r, b = w0("update_cf", {"opportunityId": OPORTUNIDAD,
                               "campos": {"imagen_input": "Tuvo imagen"}})
    got = {c["id"]: c.get("fieldValue")
           for c in ghl_get(f"/opportunities/{OPORTUNIDAD}")["opportunity"]["customFields"]}
    v = got.get("4zvcyl95qQpnJOpKx6wy")
    ok = s == 200 and isinstance(v, list) and v
    reg("G-06", "update_cf checkbox (W0 lo envuelve en array solo)", ok,
        f"http={s} leído={v!r} — el llamador mandó un string suelto", [{"req": b, "resp": r}])


def g07():
    s1, r1, b1 = w0("add_tag", {"contactId": CONTACTO, "tags": "atencion_humana"})
    t1 = ghl_get(f"/contacts/{CONTACTO}")["contact"]["tags"]
    s2, r2, b2 = w0("remove_tag", {"contactId": CONTACTO, "tags": "atencion_humana"})
    t2 = ghl_get(f"/contacts/{CONTACTO}")["contact"]["tags"]
    ok = "atencion_humana" in t1 and "atencion_humana" not in t2
    reg("G-07", "add_tag / remove_tag", ok, f"tras_add={t1} tras_remove={t2}",
        [{"req": b1, "resp": r1}, {"req": b2, "resp": r2}])


def _leer_msgs(conv):
    d = ghl_get(f"/conversations/{conv}/messages?limit=20")
    m = d.get("messages")
    if isinstance(m, dict):
        m = m.get("messages", [])
    return m or []


def g08():
    txt = f"W0 smoke texto {int(time.time())}\n*negrita* y salto"
    s, r, b = w0("send_text", {"contactId": CONTACTO, "mensaje": txt})
    d = prim(r)
    conv = d.get("data", {}).get("conversationId")
    time.sleep(2)
    msgs = _leer_msgs(conv) if conv else []
    hit = next((m for m in msgs if m.get("body") == txt), None)
    ok = s == 200 and hit is not None
    reg("G-08", "send_text con read-back byte-exacto", ok,
        f"http={s} conv={conv} body_exacto={'sí' if hit else 'NO'} status={(hit or {}).get('status')}",
        [{"req": b, "resp": r}])


def g09():
    txt = f"W0 smoke media {int(time.time())}"
    s, r, b = w0("send_media", {"contactId": CONTACTO, "mensaje": txt, "adjuntos": JPG})
    d = prim(r)
    conv = d.get("data", {}).get("conversationId")
    time.sleep(2)
    hit = next((m for m in _leer_msgs(conv) if m.get("body") == txt), None) if conv else None
    ok = s == 200 and hit is not None and hit.get("attachments") == [JPG]
    reg("G-09", "send_media (adjunto suelto → array)", ok,
        f"http={s} attachments={(hit or {}).get('attachments')}", [{"req": b, "resp": r}])


def g10():
    s, r, b = w0("search_products", {})
    d = prim(r)
    n = len(d.get("data", {}).get("records", []))
    ok = s == 200 and n > 0
    reg("G-10", "search_products", ok, f"http={s} registros={n}", [{"req": b, "resp": r}])


# ── negativos: W0 tiene que ROMPER, no devolver texto ────────────────────

W0_ID = "VK4M7VQm8CMefbty"


def ultimo_error_w0():
    """El webhook devuelve un genérico 'Workflow execution failed'; el mensaje real
    vive en la ejecución. Ahí es donde hay que buscar la evidencia."""
    u = (f"https://dev[TU-INSTANCIA-N8N]/api/v1/executions"
         f"?workflowId={W0_ID}&limit=1&includeData=true")
    req = urllib.request.Request(u, headers={"X-N8N-API-KEY": E["HPF_N8N_API_KEY"]})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.load(r)
    ex = (d.get("data") or [None])[0]
    if not ex:
        return None, None
    rd = ((ex.get("data") or {}).get("resultData") or {})
    msg = (rd.get("error") or {}).get("message")
    if not msg:  # a veces el error queda en el runData del nodo
        for nodo, corridas in (rd.get("runData") or {}).items():
            for c in corridas:
                if c.get("error"):
                    msg = c["error"].get("message")
    return ex.get("status"), msg


def _debe_fallar(cid, titulo, op, args, fragmento):
    s, r, b = w0(op, args)
    time.sleep(1.5)
    estado, msg = ultimo_error_w0()
    fallo_duro = s >= 400 and estado == "error"
    menciona = bool(msg) and fragmento.lower() in msg.lower()
    ok = fallo_duro and menciona
    reg(cid, titulo, ok,
        f"http={s} · ejecución={estado} · error={msg[:130] if msg else None!r}",
        [{"req": b, "resp_webhook": r, "estado_ejecucion": estado, "error_ejecucion": msg}])
    return ok


def g11():
    _debe_fallar("G-11", "op desconocida", "borrar_todo", {}, "op desconocida")


def g12():
    _debe_fallar("G-12", "falta argumento obligatorio", "update_stage",
                 {"opportunityId": OPORTUNIDAD}, "etapa")


def g13():
    """El caso que justifica W0: sin validación, GHL acepta el id con typo,
    devuelve 200 y pierde el dato en silencio (T-17)."""
    cent = f"NO-DEBE-ESCRIBIRSE-{int(time.time())}"
    antes = {c["id"]: c.get("fieldValue")
             for c in ghl_get(f"/opportunities/{OPORTUNIDAD}")["opportunity"]["customFields"]}
    s, r, b = w0("update_cf", {"opportunityId": OPORTUNIDAD,
                               "campos": {"producto_mostrado": cent,  # typo: falta la "s"
                                          "cp_entrega": "99999"}})
    despues = {c["id"]: c.get("fieldValue")
               for c in ghl_get(f"/opportunities/{OPORTUNIDAD}")["opportunity"]["customFields"]}
    intacto = antes.get("dwqVZEekKwE3sNSnWvvi") == despues.get("dwqVZEekKwE3sNSnWvvi")
    ok = s >= 400 and intacto
    reg("G-13", "campo custom con typo: corta ANTES del PUT", ok,
        f"http={s} (esperado ≥400) · cp_entrega intacto={intacto} "
        f"({antes.get('dwqVZEekKwE3sNSnWvvi')!r}) → sin W0 esto se perdía en silencio",
        [{"req": b, "resp": r}])


def g14():
    _debe_fallar("G-14", "etapa inexistente", "update_stage",
                 {"opportunityId": OPORTUNIDAD, "etapa": "Etapa Inventada"}, "etapa desconocida")


CASOS = [g01, g02, g03, g04, g05, g06, g07, g08, g09, g10, g11, g12, g13, g14]


def main():
    print("HPF · L3 — gate de W0 (todo pasa por el choke point)\n")
    for f in CASOS:
        try:
            f()
        except Exception as e:
            reg(f.__name__.upper(), f.__doc__ or "", False, f"EXCEPCIÓN {type(e).__name__}: {e}", [])
    okc = sum(1 for *_, ok in RES if ok)
    print(f"\n{'=' * 68}\nL3: {okc}/{len(RES)} corroborados")
    for cid, t, ok in RES:
        if not ok:
            print(f"  ❌ {cid} {t}")


if __name__ == "__main__":
    main()
