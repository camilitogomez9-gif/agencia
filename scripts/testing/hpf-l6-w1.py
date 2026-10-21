#!/usr/bin/env python3
"""
HPF · L6 — Gate de W1 · Inbound Handler.

El gate es COBERTURA TOPOLÓGICA: toda arista de todo if/switch recorrida por al menos
un fixture. Un sumidero que nunca se ejercita es un sumidero que en producción se
traga mensajes en silencio — pasó en el intento anterior.

W1 responde temprano (un ack), así que la evidencia NO sale del cuerpo HTTP: sale del
runData de la ejecución, igual que hicimos para los errores de W0.
"""
import json
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EVID = REPO / "clients/HPF_HappyFlops/07_testing/evidencia-migracion/L6"
W1 = "https://[TU-INSTANCIA-N8N]/webhook/hpf-w1-inbound"
N8N = "https://dev[TU-INSTANCIA-N8N]"
W1_ID = "nA14dNwJ7VS3YMYr"
# En L6 el cerebro era un stub ("Router (stub L7)"). Desde que W6 existe, la señal de
# "el mensaje llegó al agente" es que corrió el executeWorkflow que lo invoca.
CEREBRO = "W6 · conversación"
GHL = "https://services.leadconnectorhq.com"
CONTACTO = "3tzzBVjsKlOF2RJjKNOL"
OPORTUNIDAD = "vzYAb3P86uJ08CI9jKyV"
TEL = "+5213300000199"
ETAPAS = {
    "Lead Nuevo": "cf8fc770-81b1-422c-8394-d00bfb97a3f0",
    "En Espera": "48de80e9-31a9-472a-b030-5b9fe9174810",
    "Ganado": "909a816d-997e-4d90-8dc1-dc4b0dcd16d7",
}
RES = []
ARISTAS = set()


def env():
    e = {}
    for line in (REPO / ".env").read_text().splitlines():
        if line.strip() and not line.strip().startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            e[k.strip()] = v.strip().strip('"').strip("'")
    return e


E = env()
H_W1 = {"Content-Type": "application/json",
        E["HPF_WEBHOOK_AUTH_HEADER_NAME"]: E["HPF_WEBHOOK_AUTH_HEADER_VALUE"]}
H_N8N = {"X-N8N-API-KEY": E["HPF_N8N_API_KEY"]}
H_GHL = {"Authorization": f"Bearer {E['GHL_API_KEY']}", "Version": "2021-07-28",
         "Content-Type": "application/json", "User-Agent": "curl/8.7.1"}


def post(url, body, headers):
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return r.status, json.loads(r.read().decode() or "null")
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, {"_raw": raw[:300]}


def etapa(nombre):
    req = urllib.request.Request(f"{GHL}/opportunities/{OPORTUNIDAD}",
                                 data=json.dumps({"pipelineId": "RMnhLPqtXoWUBGZ0gvbh",
                                                  "pipelineStageId": ETAPAS[nombre]}).encode(),
                                 headers=H_GHL, method="PUT")
    urllib.request.urlopen(req, timeout=60).read()


def ejecucion(msg_id, intentos=20):
    """Busca la ejecución de W1 que procesó este messageId."""
    for _ in range(intentos):
        u = f"{N8N}/api/v1/executions?workflowId={W1_ID}&limit=12&includeData=true"
        d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H_N8N), timeout=90))
        for ex in d.get("data", []):
            rd = (ex.get("data") or {}).get("resultData") or {}
            run = rd.get("runData") or {}
            norm = run.get("Normalizar entrada")
            if not norm:
                continue
            try:
                got = norm[0]["data"]["main"][0][0]["json"]["messageId"]
            except Exception:
                continue
            if got == msg_id:
                return ex, run, rd.get("error")
        time.sleep(3)
    return None, {}, None


def nodos_corridos(run):
    return set(run.keys())


def reg(cid, titulo, ok, detalle, aristas=(), pasos=None):
    EVID.mkdir(parents=True, exist_ok=True)
    ARISTAS.update(aristas)
    EVID.joinpath(f"{cid}.json").write_text(json.dumps(
        {"caso": cid, "titulo": titulo, "resultado": "CORROBORADO" if ok else "FALLA",
         "detalle": detalle, "aristas": sorted(aristas), "pasos": pasos or []},
        indent=2, ensure_ascii=False), encoding="utf-8")
    RES.append((cid, titulo, ok))
    print(f"  {'✅' if ok else '❌'} {cid} {titulo}\n       {detalle}")


def enviar(**kw):
    body = {"contactId": CONTACTO, "messageId": kw.pop("messageId", str(uuid.uuid4())),
            "conversationId": "44tBzIqK9ODLJ7Jr9Lco", "phone": TEL,
            "canal": "WhatsApp", "debounce_seg": 0, **kw}
    s, r = post(W1, body, H_W1)
    return body["messageId"], s, r


def i01():
    """Camino feliz: llega hasta el router stub. Aristas: nuevo, seguir, gana-último."""
    etapa("Lead Nuevo")
    mid, s, r = enviar(body="Hola, quiero sandalias para una boda")
    ex, run, err = ejecucion(mid)
    corridos = nodos_corridos(run)
    router = CEREBRO in corridos
    # El stub devolvía el item de entrada; el executeWorkflow de W6 devuelve la respuesta
    # del sub-workflow, así que el contexto del turno se lee de `Evaluar estado`.
    salida = run.get("Evaluar estado", [{}])[0].get("data", {}).get("main", [[{}]])[0][0].get("json", {})
    ok = (s == 200 and r.get("aceptado") is True and router
          and salida.get("etapa") == "Lead Nuevo" and salida.get("tipo") == "texto")
    reg("I-01", "camino feliz hasta el router", ok,
        f"ack={r.get('aceptado')} llegó_al_router={router} etapa={salida.get('etapa')} "
        f"sessionId={salida.get('sessionId')} opp={salida.get('opportunityId')}",
        ["nuevo", "seguir", "gana_ultimo"], [{"resp": r, "router": salida}])
    return salida


def i02():
    """El mismo messageId dos veces: la segunda es duplicado. Arista: duplicado."""
    mid = str(uuid.uuid4())
    _, s1, r1 = enviar(messageId=mid, body="primera vez")
    time.sleep(2)
    _, s2, r2 = enviar(messageId=mid, body="segunda vez")
    ok = r1.get("aceptado") is True and r2.get("aceptado") is False and r2.get("motivo") == "duplicado"
    reg("I-02", "idempotencia por messageId", ok,
        f"1ª aceptado={r1.get('aceptado')} · 2ª aceptado={r2.get('aceptado')} "
        f"motivo={r2.get('motivo')} → GHL puede reintentar sin duplicar turnos",
        ["duplicado"], [{"1": r1, "2": r2}])


def i03():
    """Etapa bloqueante: el agente se calla. Arista: bloqueado."""
    etapa("En Espera")
    mid, s, r = enviar(body="sigo ahi?")
    ex, run, err = ejecucion(mid)
    corridos = nodos_corridos(run)
    ev = run.get("Evaluar estado", [{}])[0].get("data", {}).get("main", [[{}]])[0][0].get("json", {})
    ok = ("Fin · agente en silencio" in corridos and CEREBRO not in corridos
          and ev.get("motivo_bloqueo") == "atencion_humana")
    reg("I-03", "etapa bloqueante → agente en silencio", ok,
        f"ruta={ev.get('ruta')} motivo={ev.get('motivo_bloqueo')} "
        f"llegó_al_router={CEREBRO in corridos} (debe ser False)",
        ["bloqueado"], [{"evaluar": ev}])


def i04():
    """Cliente que vuelve tras Ganado: el bot se calla y avisa. Arista: cliente_vuelve.

    En Kommo un lead en 143 que escribía NO recibía respuesta: `Si está en perdidos` tenía
    una sola salida y era un Telegram al equipo, y la reactivación era manual. Para 142 no
    había ni gate ni alerta (la rama `If5` out1 quedó sin conectar) — acá ambas alertan.
    Este caso validaba lo contrario hasta el 2026-08-17, cuando el relevamiento del origen
    mostró que `cliente_vuelve` ganándole a `bloqueado` era un delta, no una función.
    """
    etapa("Ganado")
    mid, s, r = enviar(body="hola, quiero repetir el pedido")
    ex, run, err = ejecucion(mid)
    corridos = nodos_corridos(run)
    ev = run.get("Evaluar estado", [{}])[0].get("data", {}).get("main", [[{}]])[0][0].get("json", {})
    callado = CEREBRO not in corridos
    aviso = "Aviso · cliente vuelve" in corridos
    ok = (ev.get("ruta") == "cliente_vuelve"
          and "Cliente vuelve · sin respuesta" in corridos
          and callado and aviso
          # deja de reabrir la fila cerrada de hpf_seguimientos con cerrado_at = NULL
          and "Marcar actividad" not in corridos)
    reg("I-04", "cliente que vuelve (Ganado) → el bot no responde y avisa al equipo", ok,
        f"ruta={ev.get('ruta')} via={ev.get('via_oportunidad')} etapa={ev.get('etapa')} "
        f"llegó_al_cerebro={not callado} (debe ser False) · avisó_por_telegram={aviso}",
        ["cliente_vuelve"], [{"evaluar": ev, "corridos": sorted(corridos)}])
    etapa("Lead Nuevo")


def i05():
    """Ráfaga: el primero muere en el debounce, gana el último.
    Arista: pierde_debounce."""
    etapa("Lead Nuevo")
    m1, _, _ = enviar(body="quiero", debounce_seg=8)
    time.sleep(2)
    m2, _, _ = enviar(body="quiero 50 sandalias", debounce_seg=8)
    time.sleep(12)
    ex1, run1, _ = ejecucion(m1)
    ex2, run2, _ = ejecucion(m2)
    c1, c2 = nodos_corridos(run1), nodos_corridos(run2)
    primero_muere = "Fin · superado por otro mensaje" in c1 and CEREBRO not in c1
    segundo_pasa = CEREBRO in c2
    ok = primero_muere and segundo_pasa
    reg("I-05", "debounce: gana el último de la ráfaga", ok,
        f"1º murió_en_debounce={primero_muere} · 2º llegó_al_router={segundo_pasa}",
        ["pierde_debounce"], [{"m1": sorted(c1), "m2": sorted(c2)}])


def i06():
    """Relay incompleto: rompe con un mensaje que dice qué revisar."""
    s, r = post(W1, {"messageId": str(uuid.uuid4()), "body": "sin contacto"}, H_W1)
    ok = s >= 400
    reg("I-06", "relay sin contactId → rompe", ok, f"http={s} · {json.dumps(r)[:120]}",
        [], [{"resp": r}])


def i07():
    """Ruteo por tipo de adjunto, réplica de checkType del origen."""
    casos = {
        "imagen": ["https://assets.cdn.filesafe.space/x/media/a.jpg"],
        "audio": ["https://assets.cdn.filesafe.space/x/media/a.ogg"],
        "pdf": ["https://assets.cdn.filesafe.space/x/media/a.pdf"],
    }
    got = {}
    for esperado, adj in casos.items():
        mid, _, _ = enviar(body="", attachments=adj)
        _, run, _ = ejecucion(mid)
        n = run.get("Normalizar entrada", [{}])[0].get("data", {}).get("main", [[{}]])[0][0].get("json", {})
        got[esperado] = n.get("tipo")
    ok = all(got[k] == k for k in casos)
    reg("I-07", "ruteo por tipo (imagen / audio / pdf)", ok, f"detectado={got}", [],
        [{"detectado": got}])


def i08():
    """El sessionKey histórico se preserva: <teléfono sin no-dígitos> + 2131."""
    # El teléfono va TAL CUAL, con el '+'. En Kommo la clave era
    # `{{ All_Data.numero_telefono }}2131` sobre el custom field del contacto, y ese valor
    # empieza con '+' — lo prueba el nodo `No es EEUU`, que compara `.substring(0,2)`
    # contra "+1". Este caso esperaba el formato sin no-dígitos, que es la derivación VIEJA
    # que el `CASE` de `Resolver identidad` justamente repara. Corregir el sistema para que
    # pasara este assert habría roto la continuidad de memoria en el cutover.
    esperado = TEL + "2131"
    mid, _, _ = enviar(body="chequeo de sesión")
    _, run, _ = ejecucion(mid)
    r = run.get("Evaluar estado", [{}])[0].get("data", {}).get("main", [[{}]])[0][0].get("json", {})
    ok = r.get("sessionId") == esperado
    reg("I-08", "sessionKey compatible con la memoria de Kommo", ok,
        f"obtenido={r.get('sessionId')!r} esperado={esperado!r} "
        f"→ los leads en curso no pierden el historial en el cutover", [], [{"router": r}])


CASOS = [i01, i02, i03, i04, i05, i06, i07, i08]
TODAS = {"nuevo", "duplicado", "bloqueado", "cliente_vuelve", "seguir",
         "gana_ultimo", "pierde_debounce"}


def main():
    print("HPF · L6 — gate de W1 (cobertura topológica)\n")
    for f in CASOS:
        try:
            f()
        except Exception as e:
            reg(f.__name__.upper(), (f.__doc__ or "").strip(), False,
                f"EXCEPCIÓN {type(e).__name__}: {e}")
    ok = sum(1 for *_, o in RES if o)
    faltan = TODAS - ARISTAS
    print(f"\n{'=' * 68}\nL6·W1: {ok}/{len(RES)} corroborados")
    print(f"aristas cubiertas: {len(ARISTAS)}/{len(TODAS)} → {sorted(ARISTAS)}")
    if faltan:
        print(f"🔴 SIN CUBRIR: {sorted(faltan)}")
    for cid, t, o in RES:
        if not o:
            print(f"  ❌ {cid} {t}")


if __name__ == "__main__":
    main()
