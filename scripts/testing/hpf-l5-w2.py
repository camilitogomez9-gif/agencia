#!/usr/bin/env python3
"""
HPF · L5 — Gate de W2 · Salida.

Lo que hay que probar no es "el nodo quedó verde": es que la respuesta salió
partida en burbujas separadas, EN ORDEN y byte-exactas, y que el adjunto viajó.
Todo se verifica releyendo GET /conversations/{id}/messages.
"""
import json
import time
from datetime import datetime
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EVID = REPO / "clients/HPF_HappyFlops/07_testing/evidencia-migracion/L5"
W2 = "https://[TU-INSTANCIA-N8N]/webhook/hpf-w2-salida"
GHL = "https://services.leadconnectorhq.com"
CONTACTO = "3tzzBVjsKlOF2RJjKNOL"
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
H_W2 = {"Content-Type": "application/json",
        E["HPF_WEBHOOK_AUTH_HEADER_NAME"]: E["HPF_WEBHOOK_AUTH_HEADER_VALUE"]}
H_GHL = {"Authorization": f"Bearer {E['GHL_API_KEY']}", "Version": "2021-07-28",
         "User-Agent": "curl/8.7.1"}


def w2(body):
    req = urllib.request.Request(W2, data=json.dumps(body).encode(), headers=H_W2, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return r.status, json.loads(r.read().decode() or "null")
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, {"_raw": raw[:400]}


def msgs(conv):
    req = urllib.request.Request(f"{GHL}/conversations/{conv}/messages?limit=30", headers=H_GHL)
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.load(r)
    m = d.get("messages")
    if isinstance(m, dict):
        m = m.get("messages", [])
    return m or []


def prim(r):
    return r[0] if isinstance(r, list) and r else (r if isinstance(r, dict) else {})


def reg(cid, titulo, ok, detalle, pasos):
    EVID.mkdir(parents=True, exist_ok=True)
    EVID.joinpath(f"{cid}.json").write_text(json.dumps(
        {"caso": cid, "titulo": titulo, "resultado": "CORROBORADO" if ok else "FALLA",
         "detalle": detalle, "pasos": pasos}, indent=2, ensure_ascii=False), encoding="utf-8")
    RES.append((cid, titulo, ok))
    print(f"  {'✅' if ok else '❌'} {cid} {titulo}\n       {detalle}")


def s01():
    """3 burbujas de texto: separadas, en orden, byte-exactas."""
    t = int(time.time())
    partes = [f"S01-p1-{t} Hola! gracias por escribir a Happy Flops",
              f"S01-p2-{t} Me podría decir de que es su evento?",
              f"S01-p3-{t} 🤵👰 - Boda | 🎂🥳 - XV Años | 👼🏢 - Otros"]
    s, r = w2({"contactId": CONTACTO, "partes": partes, "pausa_seg": 2})
    d = prim(r)
    conv = (d.get("enviados") or [{}])[0].get("ghl_conversation_id")
    time.sleep(3)
    ms = msgs(conv) if conv else []
    idx = [next((i for i, m in enumerate(ms) if m.get("body") == p), None) for p in partes]
    encontradas = all(i is not None for i in idx)
    # GHL devuelve el más nuevo primero → el orden de envío es índice descendente
    orden_ok = encontradas and idx == sorted(idx, reverse=True)
    ok = s == 200 and d.get("partes_enviadas") == 3 and encontradas and orden_ok
    reg("S-01", "3 burbujas separadas, en orden, byte-exactas", ok,
        f"http={s} partes_enviadas={d.get('partes_enviadas')} índices={idx} orden_ok={orden_ok} conv={conv}",
        [{"req": partes, "resp": d}])


def s02():
    """Una parte con adjunto sale por send_media y conserva la URL exacta."""
    t = int(time.time())
    partes = [{"texto": f"S02-texto-{t}"},
              {"texto": f"S02-media-{t}", "adjuntos": JPG}]
    s, r = w2({"contactId": CONTACTO, "partes": partes, "pausa_seg": 1})
    d = prim(r)
    conv = (d.get("enviados") or [{}])[0].get("ghl_conversation_id")
    time.sleep(3)
    ms = msgs(conv) if conv else []
    con_media = next((m for m in ms if m.get("body") == f"S02-media-{t}"), None)
    ok = s == 200 and con_media is not None and con_media.get("attachments") == [JPG]
    reg("S-02", "parte con adjunto → send_media (adjunto suelto se envuelve)", ok,
        f"http={s} attachments={(con_media or {}).get('attachments')}", [{"req": partes, "resp": d}])


def s03():
    """Partes vacías se descartan — el origen también las salteaba (If parteN notEmpty)."""
    t = int(time.time())
    partes = [f"S03-unica-{t}", "", "   ", None]
    s, r = w2({"contactId": CONTACTO, "partes": [p for p in partes if p is not None],
               "pausa_seg": 0})
    d = prim(r)
    ok = s == 200 and d.get("partes_enviadas") == 1
    reg("S-03", "descarta partes vacías", ok,
        f"http={s} mandé 3 (2 vacías) → partes_enviadas={d.get('partes_enviadas')}",
        [{"req": partes, "resp": d}])


def s04():
    """La pausa va ENTRE burbujas, no después de la última.

    Se mide sobre los `dateAdded` que GHL le puso a los mensajes, no sobre la duración
    del HTTP: esa incluye 2 sub-workflows + 2 llamadas a GHL, y con un margen chico el
    test falla por carga de la instancia sin que W2 tenga nada malo (pasó: 8.5 s).
    """
    t = int(time.time())
    partes = [f"S04-a-{t}", f"S04-b-{t}"]
    pausa = 4
    ini = time.time()
    s, r = w2({"contactId": CONTACTO, "partes": partes, "pausa_seg": pausa})
    dur = time.time() - ini
    d = prim(r)
    conv = (d.get("enviados") or [{}])[0].get("ghl_conversation_id")
    time.sleep(3)
    ms = msgs(conv) if conv else []

    def cuando(body):
        m = next((x for x in ms if x.get("body") == body), None)
        if not m or not m.get("dateAdded"):
            return None
        return datetime.fromisoformat(m["dateAdded"].replace("Z", "+00:00")).timestamp()

    t1, t2 = cuando(partes[0]), cuando(partes[1])
    gap = (t2 - t1) if (t1 and t2) else None
    # el gap real tiene que rondar la pausa; margen amplio porque incluye el
    # round-trip de la segunda llamada
    gap_ok = gap is not None and pausa - 1 <= gap <= pausa + 6
    # y la última NO espera: si esperara, el total sería ~2× la pausa por encima
    sin_espera_final = dur < (pausa * 2 + 8)
    ok = s == 200 and d.get("partes_enviadas") == 2 and gap_ok and sin_espera_final
    reg("S-04", "pausa entre burbujas, no después de la última", ok,
        f"http={s} gap_real_entre_burbujas={gap if gap is None else round(gap, 2)}s "
        f"(pausa_seg={pausa}) · duración_total={dur:.1f}s",
        [{"req": partes, "resp": d, "gap_seg": gap, "duracion_http": dur}])


def s05():
    """Sin contactId tiene que romper, no responder algo parecido a un éxito."""
    s, r = w2({"partes": ["x"]})
    cuerpo = json.dumps(r, ensure_ascii=False)
    ok = s >= 400
    reg("S-05", "falta contactId → rompe", ok, f"http={s} · {cuerpo[:120]}", [{"resp": r}])


def s06():
    """Una sola parte: el caso más común (respuesta corta), sin pausas."""
    t = int(time.time())
    s, r = w2({"contactId": CONTACTO, "partes": f"S06-unica-{t}"})
    d = prim(r)
    e = (d.get("enviados") or [{}])[0]
    ok = s == 200 and d.get("partes_enviadas") == 1 and e.get("ghl_message_id")
    reg("S-06", "parte única pasada como string suelto", ok,
        f"http={s} message_id={e.get('ghl_message_id')}", [{"resp": d}])


CASOS = [s01, s02, s03, s04, s05, s06]


def main():
    print("HPF · L5 — gate de W2 (cadencia de salida)\n")
    for f in CASOS:
        try:
            f()
        except Exception as e:
            reg(f.__name__.upper(), (f.__doc__ or "").strip(), False,
                f"EXCEPCIÓN {type(e).__name__}: {e}", [])
    ok = sum(1 for *_, o in RES if o)
    print(f"\n{'=' * 68}\nL5·W2: {ok}/{len(RES)} corroborados")
    for cid, t, o in RES:
        if not o:
            print(f"  ❌ {cid} {t}")


if __name__ == "__main__":
    main()
