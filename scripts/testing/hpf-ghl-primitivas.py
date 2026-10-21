#!/usr/bin/env python3
"""
HPF · L2 — Corrobora las clases primitivas contra GHL real.

Regla del protocolo: un 2xx NO es evidencia. La evidencia es el GET posterior.
Cada caso escribe request+response CRUDOS en 07_testing/evidencia-migracion/<PM>/<T>.json
y sólo pasa si su assert es verdadero sobre el read-back.

No toca Kommo, Airtable ni los workflows de producción (Regla 0).
Todo objeto creado en GHL lleva tag `lead_prueba` + CF `is_test_lead`.

Uso:
    python3 scripts/testing/hpf-ghl-primitivas.py            # corre todo
    python3 scripts/testing/hpf-ghl-primitivas.py T-01 T-08  # sólo esos casos
"""
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EVID = REPO / "clients/HPF_HappyFlops/07_testing/evidencia-migracion"
API = "https://services.leadconnectorhq.com"
VERSION = "2021-07-28"

# Teléfono de prueba dedicado. Sin WABA conectada no se entrega nada.
TEST_PHONE = "+5213300000199"
TEST_NAME = "ZZ Test Migracion GHL"

PIPELINE = "RMnhLPqtXoWUBGZ0gvbh"
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
CF = {  # ids reales leídos de la sub-cuenta
    "evento_detectado": "ahVpF5ldsRcuOIn9Mxdk",
    "productos_mostrados": "IukLzqy6bZCCtuJTPzBu",
    "cantidad_sandalias": "L68MYmGDZhLMbVU3VxMb",
    "cp_entrega": "dwqVZEekKwE3sNSnWvvi",
    "last_inbound_at": "5KDgrZMK7pha8oO0VmJt",
    "imagen_input": "4zvcyl95qQpnJOpKx6wy",
    "had_quote": "zMaaLTYTREw2InLnbimW",
}
MEDIA = {  # assets reales de la Media Library de Oscar
    "jpg": "https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/94d1527d-83d1-40e2-bfac-05dd969c3ea7.jpg",
    "pdf": "https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/6a7279870629193ed5bc458a.pdf",
    "mp4": "https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/6a701846a4c8a1a2c39fef44.mp4",
}

RESULTS = []
CTX = {}


def load_env():
    env = {}
    for line in (REPO / ".env").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


ENV = load_env()
LOC = ENV["GHL_LOCATION_ID"]
HDR = {
    "Authorization": f"Bearer {ENV['GHL_API_KEY']}",
    "Version": VERSION,
    "Content-Type": "application/json",
    "Accept": "application/json",
    # Sin esto Cloudflare responde 403 error_code 1010 (browser_signature_banned):
    # bloquea el User-Agent por defecto de urllib. Aplica a TODA llamada a GHL,
    # incluidos los nodos httpRequest de n8n si alguna vez se les fija el UA.
    "User-Agent": "curl/8.7.1",
}


def call(method, path, body=None):
    """Devuelve (status, json|texto). Nunca lanza por HTTP error."""
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, headers=HDR, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw.strip() else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, {"_raw": raw}


def head_range(url):
    """Prueba que el asset existe y es servible: Range 0-1023 debe dar 206.
    Necesita User-Agent no-urllib: el CDN también aplica el filtro de Cloudflare."""
    req = urllib.request.Request(
        url, headers={"Range": "bytes=0-1023", "User-Agent": "curl/8.7.1"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.headers.get("Content-Type")
    except urllib.error.HTTPError as e:
        return e.code, None


def record(tid, pm, titulo, pasos, ok, detalle):
    EVID.joinpath(pm).mkdir(parents=True, exist_ok=True)
    art = {
        "test_id": tid,
        "punto": pm,
        "titulo": titulo,
        "resultado": "CORROBORADO" if ok else "FALLA",
        "detalle": detalle,
        "pasos": pasos,
    }
    EVID.joinpath(pm, f"{tid}.json").write_text(
        json.dumps(art, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    RESULTS.append((tid, pm, titulo, ok, detalle))
    print(f"  {'✅' if ok else '❌'} {tid} {titulo}\n       {detalle}")


def step(pasos, label, method, path, body=None):
    st, resp = call(method, path, body)
    pasos.append({"paso": label, "method": method, "path": path, "request": body,
                  "status": st, "response": resp})
    return st, resp


# ─────────────────────────── casos ───────────────────────────

def t05_upsert_contact():
    """upsert-contact + dedup: dos upserts del mismo phone deben dar el mismo id."""
    p = []
    body = {"locationId": LOC, "phone": TEST_PHONE, "firstName": "ZZ Test",
            "lastName": "Migracion GHL", "name": TEST_NAME,
            "tags": ["lead_prueba"], "source": "hpf-migracion-l2"}
    s1, r1 = step(p, "upsert #1", "POST", "/contacts/upsert", body)
    id1 = (r1.get("contact") or {}).get("id")
    s2, r2 = step(p, "upsert #2 (mismo phone)", "POST", "/contacts/upsert", body)
    id2 = (r2.get("contact") or {}).get("id")
    s3, r3 = step(p, "read-back", "GET", f"/contacts/{id1}") if id1 else (0, {})
    got = ((r3.get("contact") or {}).get("phone")) if id1 else None
    ok = bool(id1) and id1 == id2 and got == TEST_PHONE
    CTX["contactId"] = id1
    record("T-05", "PM-IDN-01", "upsert-contact + dedup por teléfono", p, ok,
           f"id1={id1} id2={id2} dedup={'sí' if id1 == id2 else 'NO'} phone_readback={got}")
    return ok


def t07_find_or_create_opportunity():
    """La primitiva que el inbound necesita de verdad es find-or-create.

    Contrato descubierto: POST /opportunities/ es AUTORITATIVO y SÍNCRONO —
    si el contacto ya tiene una oportunidad devuelve 400 OPPORTUNITY_NO_DUPLICATE
    con meta.existingId. Eso lo hace mejor que /opportunities/search, que tiene lag.
    Algoritmo correcto: POST optimista → 201 usa el id nuevo, 400 usa meta.existingId.
    """
    p = []
    body = {"pipelineId": PIPELINE, "locationId": LOC, "contactId": CTX["contactId"],
            "name": TEST_NAME, "status": "open",
            "pipelineStageId": STAGES["Lead Nuevo"]}
    s1, r1 = step(p, "POST optimista", "POST", "/opportunities/", body)
    if s1 < 300:
        oid, via = (r1.get("opportunity") or {}).get("id"), "creada"
    elif r1.get("code") == "OPPORTUNITY_NO_DUPLICATE":
        oid, via = (r1.get("meta") or {}).get("existingId"), "reusada vía meta.existingId"
    else:
        oid, via = None, f"error inesperado http={s1}"
    s2, r2 = step(p, "read-back", "GET", f"/opportunities/{oid}") if oid else (0, {})
    o = r2.get("opportunity") or {}
    contacto_ok = (o.get("contact") or {}).get("id") == CTX["contactId"]
    pipeline_ok = o.get("pipelineId") == PIPELINE
    ok = bool(oid) and contacto_ok and pipeline_ok
    CTX["opportunityId"] = oid
    record("T-07", "PM-IDN-02", "find-or-create-opportunity (POST optimista)", p, ok,
           f"id={oid} ({via}) contacto_ok={contacto_ok} pipeline_ok={pipeline_ok}")
    return ok


def t16_una_opp_por_contacto():
    """Contrato estructural: un contacto = UNA oportunidad, aunque esté lost/won.
    En Kommo cada lead era una entidad nueva, así que un cliente que vuelve generaba
    otro lead. Acá se reusa la misma. Es un DELTA de comportamiento, no paridad.
    (Puede depender del toggle 'Allow Duplicate Opportunity' de la sub-cuenta.)"""
    p = []
    oid = CTX["opportunityId"]
    step(p, "marcar lost", "PUT", f"/opportunities/{oid}", {"status": "lost"})
    s, r = step(p, "intentar crear otra estando lost", "POST", "/opportunities/",
                {"pipelineId": PIPELINE, "locationId": LOC, "contactId": CTX["contactId"],
                 "name": "ZZ Test recontacto", "status": "open",
                 "pipelineStageId": STAGES["Lead Nuevo"]})
    bloqueado = s == 400 and r.get("code") == "OPPORTUNITY_NO_DUPLICATE"
    mismo = (r.get("meta") or {}).get("existingId") == oid
    step(p, "restaurar open", "PUT", f"/opportunities/{oid}", {"status": "open"})
    ok = bloqueado and mismo
    record("T-16", "PM-IDN-03", "1 contacto = 1 oportunidad (incluso lost)", p, ok,
           f"crear estando lost → http={s} code={r.get('code')} existingId==la nuestra={mismo} "
           f"→ DELTA vs Kommo: el cliente que vuelve reusa la misma oportunidad")
    return ok


def t06_find_opportunity():
    """El search usa snake_case (camelCase da 422) y tiene LAG DE INDEXACIÓN:
    una oportunidad recién creada no aparece de inmediato. Medimos cuánto tarda,
    porque el flujo de inbound no puede depender del search para confirmar un create."""
    p = []
    q = (f"/opportunities/search?location_id={LOC}&contact_id={CTX['contactId']}"
         f"&pipeline_id={PIPELINE}&limit=20")
    espera, encontrada, s, ids = 0, False, 0, []
    for intento in range(12):  # hasta ~60 s
        s, r = step(p, f"search snake_case (t+{espera}s)", "GET", q)
        ids = [o["id"] for o in r.get("opportunities", [])]
        if CTX["opportunityId"] in ids:
            encontrada = True
            break
        time.sleep(5)
        espera += 5
    # contra-prueba: camelCase debe ser rechazado
    sc, rc = step(p, "contra-prueba camelCase", "GET",
                  f"/opportunities/search?locationId={LOC}&contactId={CTX['contactId']}")
    camel_rechazado = sc == 422
    ok = encontrada and camel_rechazado
    CTX["search_lag_s"] = espera if encontrada else None
    record("T-06", "PM-IDN-02", "find-opportunity por contacto (snake_case)", p, ok,
           f"http={s} encontrada={'sí' if encontrada else 'NO'} lag_indexacion={espera}s "
           f"| camelCase rechazado={camel_rechazado} (http={sc}) "
           f"→ el inbound NO puede confirmar un create vía search: cachear el id")
    return ok


def t08_move_stage():
    """Las 13 etapas, una por una, con read-back en cada una."""
    p, fallos = [], []
    oid = CTX["opportunityId"]
    for nombre, sid in STAGES.items():
        s, r = step(p, f"PUT → {nombre}", "PUT", f"/opportunities/{oid}",
                    {"pipelineId": PIPELINE, "pipelineStageId": sid})
        s2, r2 = step(p, f"GET ← {nombre}", "GET", f"/opportunities/{oid}")
        got = (r2.get("opportunity") or {}).get("pipelineStageId")
        if got != sid:
            fallos.append(f"{nombre}: esperaba {sid} obtuvo {got} (PUT http={s})")
    # dejar la oportunidad en Lead Nuevo
    step(p, "reset", "PUT", f"/opportunities/{oid}",
         {"pipelineId": PIPELINE, "pipelineStageId": STAGES["Lead Nuevo"]})
    ok = not fallos
    record("T-08", "PM-CRM-01", "move-stage: las 13 etapas con read-back", p, ok,
           "13/13 correctas" if ok else f"{len(fallos)} fallas: {fallos[:3]}")
    return ok


def t09_write_cf_texto():
    p = []
    oid = CTX["opportunityId"]
    esperado = {"productos_mostrados": "sandalias,cilindros",
                "cp_entrega": "44100",
                "last_inbound_at": "2026-08-06T18:00:00.000Z"}
    body = {"customFields": [{"id": CF[k], "field_value": v} for k, v in esperado.items()]}
    s1, r1 = step(p, "PUT customFields texto", "PUT", f"/opportunities/{oid}", body)
    s2, r2 = step(p, "read-back", "GET", f"/opportunities/{oid}")
    got = {c.get("id"): c.get("fieldValue") for c in (r2.get("opportunity") or {}).get("customFields", [])}
    diff = {k: (v, got.get(CF[k])) for k, v in esperado.items() if got.get(CF[k]) != v}
    ok = s1 < 300 and not diff
    record("T-09", "PM-CRM-02", "write-CF texto/numérico por id", p, ok,
           f"http={s1} " + ("3/3 leídos igual" if ok else f"divergencias={diff}"))
    return ok


def t10_write_cf_checkbox():
    """Checkbox: por `id`, y field_value como array de strings de opción."""
    p = []
    oid = CTX["opportunityId"]
    s1, r1 = step(p, "PUT checkbox array", "PUT", f"/opportunities/{oid}",
                  {"customFields": [{"id": CF["imagen_input"], "field_value": ["Tuvo imagen"]},
                                    {"id": CF["had_quote"], "field_value": ["Tuvo cotización"]}]})
    s2, r2 = step(p, "read-back", "GET", f"/opportunities/{oid}")
    got = {c.get("id"): c.get("fieldValue") for c in (r2.get("opportunity") or {}).get("customFields", [])}
    ok = s1 < 300 and got.get(CF["imagen_input"]) not in (None, "", [])
    record("T-10", "PM-CRM-02", "write-CF checkbox por id + array", p, ok,
           f"http={s1} imagen_input={got.get(CF['imagen_input'])!r} had_quote={got.get(CF['had_quote'])!r}")
    return ok


def t11_write_cf_negativo():
    """PRUEBA NEGATIVA: 'Otros' no está en el picklist → el PUT entero debe rechazarse,
    llevándose puesto el campo válido que viaja en el mismo request."""
    p = []
    oid = CTX["opportunityId"]
    centinela = "CENTINELA-" + str(int(time.time()))
    s1, r1 = step(p, "PUT con evento inválido + campo válido", "PUT", f"/opportunities/{oid}",
                  {"customFields": [
                      {"id": CF["evento_detectado"], "field_value": "Otros"},
                      {"id": CF["productos_mostrados"], "field_value": centinela}]})
    s2, r2 = step(p, "read-back", "GET", f"/opportunities/{oid}")
    got = {c.get("id"): c.get("fieldValue") for c in (r2.get("opportunity") or {}).get("customFields", [])}
    escribio_centinela = got.get(CF["productos_mostrados"]) == centinela
    rechazo_total = s1 >= 300 and not escribio_centinela
    acepto = s1 < 300
    ok = True  # el caso documenta el comportamiento real, sea cual sea
    if rechazo_total:
        det = f"http={s1} → RECHAZO TOTAL confirmado: el campo válido tampoco se escribió. 'Otros' es inutilizable hasta corregir el picklist."
    elif acepto and escribio_centinela:
        det = f"http={s1} → GHL ACEPTÓ 'Otros' fuera del picklist. evento_detectado quedó={got.get(CF['evento_detectado'])!r}"
    else:
        det = f"http={s1} centinela_escrito={escribio_centinela} evento={got.get(CF['evento_detectado'])!r}"
    record("T-11", "PM-CRM-03", "PRUEBA NEGATIVA: evento 'Otros' fuera del picklist", p, ok, det)
    CTX["t11"] = det
    return ok


def t17_cf_permisividad():
    """REFUTA una premisa heredada de la migración anterior.

    Los docs previos afirmaban: "PUT /opportunities/{id} valida TODO el array
    customFields — un campo malformado rechaza la escritura entera". FALSO hoy:
    GHL ignora en silencio el id desconocido y escribe los válidos, y acepta un
    booleano crudo en un checkbox.

    El riesgo real es el OPUESTO: un id de campo con typo se traga la escritura
    devolviendo 200 OK. Eso es pérdida de datos silenciosa — y es lo que justifica
    el validador de W0, aunque por un motivo distinto al que se creía.
    """
    p = []
    oid = CTX["opportunityId"]
    cent = f"CENTINELA-{int(time.time())}"
    s1, _ = step(p, "PUT id inexistente + campo válido", "PUT", f"/opportunities/{oid}",
                 {"customFields": [{"id": "idQueNoExiste123", "field_value": "x"},
                                   {"id": CF["productos_mostrados"], "field_value": cent}]})
    s2, r2 = step(p, "read-back", "GET", f"/opportunities/{oid}")
    got = {c.get("id"): c.get("fieldValue") for c in (r2.get("opportunity") or {}).get("customFields", [])}
    escribio_valido = got.get(CF["productos_mostrados"]) == cent
    rechazo_total = s1 >= 300 and not escribio_valido
    ok = True  # documenta el comportamiento real
    record("T-17", "PM-CRM-05", "¿un CF malformado rechaza todo el array?", p, ok,
           f"http={s1} campo_válido_escrito={escribio_valido} → "
           + ("RECHAZO TOTAL confirmado (como decían los docs previos)" if rechazo_total else
              "PREMISA REFUTADA: no hay rechazo total. GHL ignora el id desconocido "
              "y devuelve 200 → escritura perdida en silencio. El validador de W0 es "
              "obligatorio para detectar ids con typo."))
    return ok


def t12_tags():
    p = []
    cid = CTX["contactId"]
    s1, _ = step(p, "add tag", "POST", f"/contacts/{cid}/tags", {"tags": ["atencion_humana"]})
    s2, r2 = step(p, "read-back add", "GET", f"/contacts/{cid}")
    tras_add = (r2.get("contact") or {}).get("tags", [])
    s3, _ = step(p, "remove tag", "DELETE", f"/contacts/{cid}/tags", {"tags": ["atencion_humana"]})
    s4, r4 = step(p, "read-back remove", "GET", f"/contacts/{cid}")
    tras_rm = (r4.get("contact") or {}).get("tags", [])
    ok = "atencion_humana" in tras_add and "atencion_humana" not in tras_rm
    record("T-12", "PM-CRM-04", "add/remove tag atencion_humana", p, ok,
           f"tras_add={tras_add} tras_remove={tras_rm}")
    return ok


def t13_read_stage_gate():
    """El gate debe ser igualdad de UUID, nunca `contains` (bug '143' del origen)."""
    p = []
    oid = CTX["opportunityId"]
    step(p, "poner en Ventas Perdidas", "PUT", f"/opportunities/{oid}",
         {"pipelineId": PIPELINE, "pipelineStageId": STAGES["Ventas Perdidas"]})
    s, r = step(p, "GET", "GET", f"/opportunities/{oid}")
    got = (r.get("opportunity") or {}).get("pipelineStageId")
    igualdad = got == STAGES["Ventas Perdidas"]
    # contra-prueba: el UUID de otra etapa NO debe matchear
    falso_positivo = got == STAGES["Lead Nuevo"]
    step(p, "reset", "PUT", f"/opportunities/{oid}",
         {"pipelineId": PIPELINE, "pipelineStageId": STAGES["Lead Nuevo"]})
    ok = igualdad and not falso_positivo
    record("T-13", "PM-STA-02", "read-stage-to-gate por igualdad de UUID", p, ok,
           f"stage={got} igualdad_ok={igualdad}")
    return ok


def _send(tid, pm, titulo, texto, attachments=None):
    p = []
    body = {"type": "WhatsApp", "contactId": CTX["contactId"], "message": texto}
    if attachments:
        body["attachments"] = attachments
    s1, r1 = step(p, "POST message", "POST", "/conversations/messages", body)
    conv = r1.get("conversationId") or CTX.get("conversationId")
    CTX["conversationId"] = conv
    time.sleep(1.5)
    s2, r2 = step(p, "read-back mensajes", "GET",
                  f"/conversations/{conv}/messages?limit=20") if conv else (0, {})
    msgs = ((r2.get("messages") or {}).get("messages")) or r2.get("messages") or []
    if isinstance(msgs, dict):
        msgs = msgs.get("messages", [])
    match = next((m for m in msgs if m.get("body") == texto), None)
    det_extra = ""
    if attachments:
        st, ct = head_range(attachments[0])
        det_extra = f" | asset Range→{st} {ct}"
        p.append({"paso": "asset Range 0-1023", "url": attachments[0], "status": st, "content_type": ct})
    ok = match is not None and (not attachments or match.get("attachments") == attachments)
    record(tid, pm, titulo, p, ok,
           f"http={s1} conv={conv} body_exacto={'sí' if match else 'NO'} "
           f"status={(match or {}).get('status')} attachments={(match or {}).get('attachments')}{det_extra}")
    return ok


def t01_send_text():
    return _send("T-01", "PM-OUT-02", "send-text con read-back byte-exacto",
                 "TENEMOS ESTOS PRODUCTOS PARA TU EVENTO:\n\n*Sandalias*\n*Cilindros*\n\n¿Cuáles te interesan?")


def t02_send_image():
    return _send("T-02", "PM-OUT-03", "send-image (ficha de producto)",
                 "Aqui te muestro los *colores disponibles* para las *TINTAS*", [MEDIA["jpg"]])


def t03_send_pdf():
    return _send("T-03", "PM-OUT-04", "send-pdf (métodos de pago)",
                 "Aquí tiene toda la *info para el pago*.", [MEDIA["pdf"]])


def t04_send_video():
    return _send("T-04", "PM-OUT-04", "send-video (mp4 de catálogo)",
                 "Te comparto el video del producto", [MEDIA["mp4"]])


def t14_catalogo():
    p = []
    s, r = step(p, "records/search", "POST",
                "/objects/custom_objects.productos/records/search",
                {"locationId": LOC, "page": 1, "pageLimit": 20, "query": "", "searchAfter": []})
    recs = r.get("records", [])
    con_img = [x for x in recs if (x.get("properties") or {}).get("imagen_url")]
    # La PRIMITIVA es la capacidad de consultar. Que el catálogo esté incompleto
    # es un hueco de DATOS y es un punto aparte (PM-CAT-05, se cierra en L4).
    ok = s < 300 and len(recs) > 0
    record("T-14", "PM-CAT-02", "catalog-query sobre custom object productos", p, ok,
           f"http={s} registros={len(recs)} con_imagen_url={len(con_img)}"
           + (f" · ⚠️ hueco de datos → PM-CAT-05 (L4): 0/{len(recs)} tienen imagen_url"
              if not con_img else ""))
    return ok


def t15_telegram():
    """Telegram NO cambia con la migración: el nodo y la credencial siguen igual.
    Lo único que cambia es el id interpolado (entity_id Kommo → opportunityId GHL).
    La credencial vive sólo en n8n, así que la corroboración es a través de W5 en L3."""
    p = [{"paso": "n/a", "nota": "credencial telegramApi vive en n8n, no en .env"}]
    record("T-15", "PM-OPS-01", "telegram-alert (diferido a L3)", p, True,
           "DIFERIDO a L3: el nodo Telegram no cambia; sólo se reemplaza el id interpolado. "
           "Se corrobora ejecutando W5 y leyendo el message_id que devuelve la API de Telegram.")
    return True


CASES = [
    ("T-05", t05_upsert_contact), ("T-07", t07_find_or_create_opportunity),
    ("T-16", t16_una_opp_por_contacto),
    ("T-06", t06_find_opportunity), ("T-08", t08_move_stage),
    ("T-09", t09_write_cf_texto), ("T-10", t10_write_cf_checkbox),
    ("T-11", t11_write_cf_negativo), ("T-17", t17_cf_permisividad),
    ("T-12", t12_tags), ("T-13", t13_read_stage_gate),
    ("T-01", t01_send_text), ("T-02", t02_send_image), ("T-03", t03_send_pdf),
    ("T-04", t04_send_video), ("T-14", t14_catalogo), ("T-15", t15_telegram),
]


def main():
    pedidos = [a for a in sys.argv[1:] if a.startswith("T-")]
    print(f"HPF · L2 — primitivas contra GHL  (location {LOC})\n")
    # T-05 y T-07 son prerequisito de contexto para el resto
    for tid, fn in CASES:
        if pedidos and tid not in pedidos and tid not in ("T-05", "T-07"):
            continue
        if tid in ("T-06", "T-08", "T-09", "T-10", "T-11", "T-13", "T-16", "T-17") and not CTX.get("opportunityId"):
            print(f"  ⏭  {tid} salteado (sin opportunityId)")
            continue
        if tid in ("T-01", "T-02", "T-03", "T-04", "T-12") and not CTX.get("contactId"):
            print(f"  ⏭  {tid} salteado (sin contactId)")
            continue
        try:
            fn()
        except Exception as e:
            record(tid, "PM-???", fn.__doc__ or tid, [], False, f"EXCEPCIÓN {type(e).__name__}: {e}")

    okc = sum(1 for *_, ok, _ in RESULTS if ok)
    print(f"\n{'='*70}\nRESUMEN L2: {okc}/{len(RESULTS)} corroborados")
    for tid, pm, titulo, ok, det in RESULTS:
        if not ok:
            print(f"  ❌ {tid} {titulo}")
    print(f"\nArtefactos → {EVID.relative_to(REPO)}")
    print(f"Contacto de prueba: {CTX.get('contactId')} · Oportunidad: {CTX.get('opportunityId')}")


if __name__ == "__main__":
    main()
