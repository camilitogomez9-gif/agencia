#!/usr/bin/env python3
"""
HPF · L7 — Gate de W4 (CALCULADORA) y W5 (ATENCION_PERSONALIZADA).

W4 calcula plata del cliente: los casos golden salen del incidente real de julio
(35 cilindros cuando el mínimo son 40) y de los tramos de costo del `Code2`.
"""
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EVID = REPO / "clients/HPF_HappyFlops/07_testing/evidencia-migracion/L7"
W4 = "https://[TU-INSTANCIA-N8N]/webhook/hpf-w4-calculadora"
W5 = "https://[TU-INSTANCIA-N8N]/webhook/hpf-w5-atencion"
GHL = "https://services.leadconnectorhq.com"
CONTACTO = "3tzzBVjsKlOF2RJjKNOL"
OPORTUNIDAD = "vzYAb3P86uJ08CI9jKyV"
EN_ESPERA = "48de80e9-31a9-472a-b030-5b9fe9174810"
LEAD_NUEVO = "cf8fc770-81b1-422c-8394-d00bfb97a3f0"
RES = []


def env():
    e = {}
    for line in (REPO / ".env").read_text().splitlines():
        if line.strip() and not line.strip().startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            e[k.strip()] = v.strip().strip('"').strip("'")
    return e


E = env()
H_WH = {"Content-Type": "application/json",
        E["HPF_WEBHOOK_AUTH_HEADER_NAME"]: E["HPF_WEBHOOK_AUTH_HEADER_VALUE"]}
H_GHL = {"Authorization": f"Bearer {E['GHL_API_KEY']}", "Version": "2021-07-28",
         "Content-Type": "application/json", "User-Agent": "curl/8.7.1"}


def call(url, body, headers, method="POST"):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
                                 headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read().decode() or "null")
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, {"_raw": raw[:300]}


def ghl_get(path):
    req = urllib.request.Request(GHL + path, headers=H_GHL)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def prim(r):
    return r[0] if isinstance(r, list) and r else (r if isinstance(r, dict) else {})


def reg(cid, titulo, ok, detalle, pasos):
    EVID.mkdir(parents=True, exist_ok=True)
    EVID.joinpath(f"{cid}.json").write_text(json.dumps(
        {"caso": cid, "titulo": titulo, "resultado": "CORROBORADO" if ok else "FALLA",
         "detalle": detalle, "pasos": pasos}, indent=2, ensure_ascii=False), encoding="utf-8")
    RES.append((cid, titulo, ok))
    print(f"  {'✅' if ok else '❌'} {cid} {titulo}\n       {detalle}")


def calc(items=None, cuentas=None):
    body = {}
    if items is not None:
        body["items"] = json.dumps(items) if isinstance(items, list) else items
    if cuentas is not None:
        body["cuentas"] = cuentas
    return call(W4, body, H_WH)


# ── W4 ────────────────────────────────────────────────────────────────

def k01():
    """50 sandalias delgadas: 7.5 kg → tramo 5–7 no, 7.1–12 sí → $300."""
    s, r = calc(items=[{"producto": "Sandalias Delgadas", "cantidad": 50}])
    d = prim(r)
    ok = s == 200 and d.get("ok") and d.get("costo_total_envio") == 300
    reg("K-01", "50 sandalias delgadas → 1 caja", ok,
        f"http={s} costo={d.get('costo_total_envio')} cajas={d.get('cantidad_cajas')} "
        f"resumen={d.get('resumen_cajas')}", [{"resp": d}])


def k02():
    """EL CASO DEL INCIDENTE: 35 cilindros con mínimo 40.

    En producción el rechazo existe pero muere en el Set, que sólo expone
    `resumen_cajas`. El agente recibía vacío y no sabía qué decirle al cliente.
    """
    s, r = calc(items=[{"producto": "Cilindros", "cantidad": 35}])
    d = prim(r)
    rechaza = d.get("ok") is False and d.get("error") == "MINIMO_NO_ALCANZADO"
    explica = bool(d.get("message_to_agent")) and "40" in str(d.get("message_to_agent"))
    detalle_ok = any(v.get("minimo_requerido") == 40 for v in (d.get("detalle_violaciones") or []))
    ok = s == 200 and rechaza and explica and detalle_ok
    reg("K-02", "35 cilindros (mínimo 40) → rechazo QUE LLEGA al agente", ok,
        f"rechaza={rechaza} explica_el_minimo={explica} detalle={d.get('detalle_violaciones')} "
        f"→ msg: {str(d.get('message_to_agent'))[:110]}", [{"resp": d}])


def k03():
    """Pedido grande: se parte en cajas por peso y por límite de piezas."""
    s, r = calc(items=[{"producto": "Sandalias Delgadas", "cantidad": 300},
                       {"producto": "Cilindros", "cantidad": 300}])
    d = prim(r)
    ok = (s == 200 and d.get("ok") and (d.get("cantidad_cajas") or 0) >= 2
          and (d.get("costo_total_envio") or 0) > 300)
    reg("K-03", "pedido grande → varias cajas", ok,
        f"cajas={d.get('cantidad_cajas')} costo={d.get('costo_total_envio')} "
        f"resumen={d.get('resumen_cajas')}", [{"resp": d}])


def k04():
    """Formato legacy `cuentas`: sin nombres no se pueden validar mínimos,
    pero el origen igual calculaba y avisaba."""
    s, r = calc(cuentas="50 x 0.15, 40 x 0.14")
    d = prim(r)
    ok = s == 200 and d.get("ok") and d.get("costo_total_envio") is not None
    reg("K-04", "formato legacy `cuentas` sigue funcionando", ok,
        f"costo={d.get('costo_total_envio')} advertencia={str(d.get('advertencia_minimos'))[:70]}",
        [{"resp": d}])


def k05():
    """Producto desconocido: rompe en vez de inventar un peso."""
    s, r = calc(items=[{"producto": "helicoptero", "cantidad": 100}])
    ok = s >= 400 or (prim(r).get("ok") is False)
    reg("K-05", "producto desconocido → no inventa peso", ok,
        f"http={s} · {json.dumps(prim(r), ensure_ascii=False)[:150]}", [{"resp": r}])


def k06():
    """Mandiles: mínimo 12 y peso 0 (no suman a la caja)."""
    s, r = calc(items=[{"producto": "Mandiles", "cantidad": 12}])
    d = prim(r)
    ok = s == 200 and d.get("ok")
    reg("K-06", "mandiles (mínimo 12, peso 0)", ok,
        f"ok={d.get('ok')} costo={d.get('costo_total_envio')} cajas={d.get('cantidad_cajas')}",
        [{"resp": d}])


# ── W5 ────────────────────────────────────────────────────────────────

def a01():
    """Derivación: Telegram + etapa En Espera + tag, todo verificado por read-back."""
    s, r = call(W5, {"contactId": CONTACTO, "opportunityId": OPORTUNIDAD,
                     "motivo": "diseño personalizado"}, H_WH)
    d = prim(r)
    time.sleep(2)
    etapa = ghl_get(f"/opportunities/{OPORTUNIDAD}")["opportunity"]["pipelineStageId"]
    tags = ghl_get(f"/contacts/{CONTACTO}")["contact"].get("tags", [])
    ok = (s == 200 and d.get("ok") and etapa == EN_ESPERA
          and "atencion_humana" in tags and d.get("message_to_agent"))
    reg("A-01", "derivación: etapa + tag + aviso, con read-back", ok,
        f"http={s} etapa={'En Espera' if etapa == EN_ESPERA else etapa} "
        f"tag={'atencion_humana' in tags} msg={str(d.get('message_to_agent'))[:60]}",
        [{"resp": d, "etapa": etapa, "tags": tags}])


def a02():
    """Sin contactId rompe."""
    s, r = call(W5, {"opportunityId": OPORTUNIDAD}, H_WH)
    ok = s >= 400
    reg("A-02", "derivación sin contactId → rompe", ok, f"http={s}", [{"resp": r}])


def limpiar():
    call(f"{GHL}/opportunities/{OPORTUNIDAD}",
         {"pipelineId": "RMnhLPqtXoWUBGZ0gvbh", "pipelineStageId": LEAD_NUEVO},
         H_GHL, "PUT")
    call(f"{GHL}/contacts/{CONTACTO}/tags", {"tags": ["atencion_humana"]}, H_GHL, "DELETE")


CASOS = [k01, k02, k03, k04, k05, k06, a01, a02]


def main():
    print("HPF · L7 — gate de tools (W4 CALCULADORA · W5 ATENCION)\n")
    for f in CASOS:
        try:
            f()
        except Exception as e:
            reg(f.__name__.upper(), (f.__doc__ or "").strip().split("\n")[0], False,
                f"EXCEPCIÓN {type(e).__name__}: {e}", [])
    limpiar()
    ok = sum(1 for *_, o in RES if o)
    print(f"\n{'=' * 68}\nL7·tools: {ok}/{len(RES)} corroborados")
    for cid, t, o in RES:
        if not o:
            print(f"  ❌ {cid} {t}")


if __name__ == "__main__":
    main()
