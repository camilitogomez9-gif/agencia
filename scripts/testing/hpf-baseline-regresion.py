#!/usr/bin/env python3
"""
HPF · baseline de regresión conversacional para W6.

PARA QUÉ
la agencia puso una condición dura sobre los cambios de este ciclo: que corrijan los puntos de Oscar
y que **no modifiquen ningún otro aspecto del agente**. Los smokes dirigidos prueban lo que se
tocó; no prueban lo que NO se tocó. Esto sí: se captura el comportamiento del bot ANTES de
cambiar nada, se re-captura DESPUÉS, y se diffea. Toda diferencia fuera de la lista aprobada es
una regresión.

QUÉ COMPARA — y qué NO
El bot es un LLM: comparar texto literal sería ruido puro y el diff estaría siempre en rojo. Se
comparan los hechos ESTABLES de cada turno:

  · adjuntos enviados, resueltos a nombre de ficha contra el catálogo real (determinístico:
    vienen de la base, no del modelo)
  · `step` ruteado y `etapa_destino` (la máquina de estados)
  · cantidad de burbujas
  · qué NODOS ejecutaron (de la API de ejecuciones) — caza cambios de topología y ramas que
    dejan de correr, que es la regresión más silenciosa de todas
  · flags binarios: marcador `url1234.com123` crudo, emojis fuera del inventario del original,
    presencia de negritas

Lo probabilístico no se compara por corrida sino por TASA: cada escenario se corre N veces y se
compara la proporción. Es la lección del 12/8, donde el "¿cuánto cuestan?" daba 4/7 y una sola
corrida podía decir cualquier cosa.

USO
    hpf-baseline-regresion.py --capturar antes.json            # 1 corrida por escenario
    hpf-baseline-regresion.py --capturar antes.json --repite 3  # 3, para medir tasas
    hpf-baseline-regresion.py --diff antes.json despues.json
    hpf-baseline-regresion.py --capturar x.json --solo pago,ubicacion
"""
import argparse
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[2]
BASE = REPO / "clients/HPF_HappyFlops/04_agents/base-prod-2026-08-06"
CAT = REPO / "clients/HPF_HappyFlops/00_migracion_ghl/06_registro/catalogo-airtable.json"
W6 = "https://[TU-INSTANCIA-N8N]/webhook/hpf-w6-conversacion"

SEQ = re.compile("(?:[\U0001F000-\U0001FAFF☀-➿️⃣‍\U0001F1E6-\U0001F1FF〰〽㊗㊙©®]"
                 "[️‍\U0001F3FB-\U0001F3FF⃣]*)+")


def emojis(t):
    return {m.group(0) for m in SEQ.finditer(t or "") if m.group(0).strip(" ‍️")}


def inventario():
    """Set de emojis permitido = el que usa el prompt original. No hardcodeado."""
    per = set()
    for p in BASE.glob("*.md"):
        per |= emojis(p.read_text(encoding="utf-8"))
    piezas = set()
    for s in per:
        for m in re.finditer("[\U0001F000-\U0001FAFF☀-➿][️‍]*", s):
            piezas.add(m.group(0))
    return per | piezas


PERMITIDOS = inventario()

FICHA = {}
for f in json.loads(CAT.read_text(encoding="utf-8")):
    u = (f.get("ghl_media") or {}).get("url")
    if u:
        FICHA.setdefault(u, set()).add(
            f"{f.get('evento') or f.get('tabla')}/{f.get('producto')}")


def env():
    e = {}
    for line in (REPO / ".env").read_text().splitlines():
        if line.strip() and not line.strip().startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            e[k.strip()] = v.strip().strip('"').strip("'")
    return e


E = env()
H = {"Content-Type": "application/json",
     E["HPF_WEBHOOK_AUTH_HEADER_NAME"]: E["HPF_WEBHOOK_AUTH_HEADER_VALUE"]}
N8N = E["HPF_N8N_API"].rstrip("/")
KEY = E.get("HPF_N8N_API_KEY") or E["N8N_API_KEY"]


# ── escenarios ────────────────────────────────────────────────────────────────
# Cubren los puntos de Oscar Y las validaciones que él dijo que están bien — esas son
# justamente el control: si cambian, rompimos algo que funcionaba.
ESCENARIOS = {
    "saludo":        ["hola"],
    "boda_sandalias": ["hola", "es para una boda",
                       "me interesan las sandalias gruesas",
                       "quiero 60 al codigo postal 44100"],
    "xv_cilindros":  ["hola", "es para los 15 años de mi hija",
                      "me interesan los cilindros y los termos"],
    "peluche":       ["hola", "es para una boda",
                      "quiero las pantuflas de moño de peluche, que diseños tienen?"],
    "pantuflas_gen": ["hola", "es para una boda",
                      "me interesan las pantuflas, que opciones hay?"],
    "mandiles":      ["hola", "es para una boda", "que tienen de mandiles?"],
    "anticruda":     ["hola", "es para una boda", "me muestras los kits anticruda?"],
    "ubicacion":     ["hola", "es para una boda",
                      "y ustedes de donde son? tienen tienda fisica?"],
    "seguridad":     ["hola", "es para una boda",
                      "como se que es seguro comprarles? no sera estafa?"],
    "pago":          ["hola", "es para una boda",
                      "quiero 60 sandalias gruesas al codigo postal 44100, cuanto sale?",
                      "si, quiero avanzar, pasame los datos para pagar"],
    "oferta_precio": ["hola", "es para una boda",
                      "quiero 60 sandalias gruesas al codigo postal 44100, cuanto sale?",
                      "cuanto cuestan?"],
    "otros_evento":  ["hola", "es para un bautizo", "que productos tienen?"],
}


def post(sid, texto, primer, probe):
    body = {"sessionId": sid, "texto": texto, "contactId": None,
            "opportunityId": None, "primer_contacto": primer, "_probe": probe}
    req = urllib.request.Request(W6, data=json.dumps(body).encode(), headers=H, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            d = json.loads(r.read().decode() or "null")
            return d[0] if isinstance(d, list) and d else (d or {})
    except urllib.error.HTTPError as e:
        return {"_http": e.code, "_raw": e.read().decode()[:300], "partes": []}
    except Exception as e:
        return {"_err": str(e)[:200], "partes": []}


def nodos_ultima_ejecucion():
    """Qué nodos corrieron en la última ejecución de W6. Caza cambios de topología."""
    try:
        r = urllib.request.Request(
            f"{N8N}/api/v1/executions?workflowId=cNmJCP2qVhdtfCH0&limit=1&includeData=false",
            headers={"X-N8N-API-KEY": KEY, "Accept": "application/json"})
        with urllib.request.urlopen(r, timeout=60) as x:
            ex = json.loads(x.read().decode()).get("data") or []
        if not ex:
            return None
        r2 = urllib.request.Request(
            f"{N8N}/api/v1/executions/{ex[0]['id']}?includeData=true",
            headers={"X-N8N-API-KEY": KEY, "Accept": "application/json"})
        with urllib.request.urlopen(r2, timeout=90) as x:
            d = json.loads(x.read().decode())
        return sorted((((d.get("data") or {}).get("resultData") or {}).get("runData") or {}).keys())
    except Exception:
        return None


def huella(d):
    """Los hechos estables de un turno. NO incluye el texto: eso es ruido de LLM."""
    partes = d.get("partes") or []
    txt = "\n".join(p.get("texto") or "" for p in partes)
    adj = [a for p in partes for a in (p.get("adjuntos") or [])]
    fichas = sorted({n for a in adj for n in FICHA.get(a, {f"(fuera del catálogo) {a[-24:]}"})})
    usados = emojis(txt)
    return {
        "http_ok": not (d.get("_http") or d.get("_err")),
        "step": d.get("step"),
        "etapa_destino": d.get("etapa_destino"),
        "n_burbujas": len(partes),
        "n_adjuntos": len(adj),
        "fichas": fichas,
        "marcador_crudo": "url1234" in txt,
        "emojis_fuera_del_set": sorted(usados - PERMITIDOS),
        "tiene_negritas": bool(re.search(r"\*[^*\n]{2,60}\*", txt)),
        "n_negritas": len(re.findall(r"\*[^*\n]{2,60}\*", txt)),
        "pide_comprobante": bool(re.search(r"comprobante|captura", txt, re.I)),
        "manda_pdf": any(a.lower().endswith(".pdf") for a in adj),
        "menciona_direccion": bool(re.search(r"ZAVALA|SAN JUAN BOSCO", txt, re.I)),
        "menciona_maps": "goo.su" in txt,
        "markdown_link": bool(re.search(r"\[[^\]]+\]\(https?://", txt)),
        # se guarda recortado solo para poder mirar a ojo cuando algo llama la atención;
        # el diff NO lo usa
        "_muestra": txt[:200],
    }


def capturar(nombres, repite):
    base = int(time.time())
    out = {"_capturado_at": base, "_repeticiones": repite, "escenarios": {}}
    for nom in nombres:
        turnos_esc = ESCENARIOS[nom]
        out["escenarios"][nom] = []
        for it in range(repite):
            sid = f"base-{base}-{nom}-{it}"
            corrida = []
            print(f"  {nom} · corrida {it+1}/{repite}", flush=True)
            for k, texto in enumerate(turnos_esc):
                d = post(sid, texto, k == 0, f"{nom}-{it}-{k}")
                h = huella(d)
                if k == len(turnos_esc) - 1:
                    h["nodos"] = nodos_ultima_ejecucion()
                corrida.append({"turno": texto, **h})
            out["escenarios"][nom].append(corrida)
    return out


def resumen(cap, nom):
    """Consolida las N corridas de un escenario: lo estable como valor, lo variable como tasa."""
    corridas = cap["escenarios"][nom]
    n = len(corridas)
    turnos = len(corridas[0])
    res = []
    for t in range(turnos):
        campos = {}
        for campo in ("step", "etapa_destino", "n_adjuntos", "fichas", "marcador_crudo",
                      "emojis_fuera_del_set", "tiene_negritas", "manda_pdf",
                      "pide_comprobante", "menciona_direccion", "menciona_maps",
                      "markdown_link", "http_ok", "nodos"):
            vals = [json.dumps(c[t].get(campo), ensure_ascii=False, sort_keys=True)
                    for c in corridas if campo in c[t]]
            if not vals:
                continue
            unicos = sorted(set(vals))
            if len(unicos) == 1:
                campos[campo] = json.loads(unicos[0])
            else:
                # el campo varía entre corridas: se guarda la TASA de cada valor, no el valor.
                # La clave queda como el JSON serializado a propósito — los valores pueden ser
                # listas (fichas, nodos) y una lista no puede ser clave de un dict.
                campos[campo] = {"_tasa": {v: round(vals.count(v) / n, 2) for v in unicos}}
        res.append({"turno": corridas[0][t]["turno"], **campos})
    return res


def diff(a, b):
    ca, cb = json.loads(pathlib.Path(a).read_text()), json.loads(pathlib.Path(b).read_text())
    escenarios = sorted(set(ca["escenarios"]) | set(cb["escenarios"]))
    hallazgos = []
    for nom in escenarios:
        if nom not in ca["escenarios"] or nom not in cb["escenarios"]:
            hallazgos.append((nom, "-", "escenario presente en una sola captura", "", ""))
            continue
        ra, rb = resumen(ca, nom), resumen(cb, nom)
        if len(ra) != len(rb):
            hallazgos.append((nom, "-", "distinta cantidad de turnos", len(ra), len(rb)))
            continue
        for t, (x, y) in enumerate(zip(ra, rb)):
            for campo in sorted(set(x) | set(y)):
                if campo == "turno":
                    continue
                va, vb = x.get(campo, "(ausente)"), y.get(campo, "(ausente)")
                if json.dumps(va, sort_keys=True, ensure_ascii=False) != \
                   json.dumps(vb, sort_keys=True, ensure_ascii=False):
                    hallazgos.append((nom, f"T{t+1} «{x['turno'][:34]}»", campo, va, vb))
    print(f"\n{'='*76}\nDIFF  {pathlib.Path(a).name} → {pathlib.Path(b).name}\n{'='*76}")
    if not hallazgos:
        print("\n✅ sin diferencias: el comportamiento es idéntico en todo lo medido")
        return 0
    actual = None
    for nom, turno, campo, va, vb in hallazgos:
        if nom != actual:
            print(f"\n── {nom}")
            actual = nom
        print(f"   {turno}  ·  {campo}")
        print(f"      antes:   {json.dumps(va, ensure_ascii=False)[:150]}")
        print(f"      después: {json.dumps(vb, ensure_ascii=False)[:150]}")
    print(f"\n{len(hallazgos)} diferencia(s). Cada una tiene que estar justificada por un punto "
          f"de la lista aprobada; si no, es una regresión.")
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capturar", metavar="SALIDA.json")
    ap.add_argument("--repite", type=int, default=1)
    ap.add_argument("--solo", default="")
    ap.add_argument("--diff", nargs=2, metavar=("ANTES.json", "DESPUES.json"))
    a = ap.parse_args()

    if a.diff:
        sys.exit(diff(*a.diff))
    if not a.capturar:
        ap.print_help()
        return
    nombres = [s.strip() for s in a.solo.split(",") if s.strip()] or list(ESCENARIOS)
    desconocidos = [n for n in nombres if n not in ESCENARIOS]
    if desconocidos:
        sys.exit(f"❌ escenarios desconocidos: {desconocidos}. Hay: {list(ESCENARIOS)}")
    print(f"capturando {len(nombres)} escenario(s) × {a.repite} corrida(s)")
    cap = capturar(nombres, a.repite)
    pathlib.Path(a.capturar).write_text(json.dumps(cap, ensure_ascii=False, indent=1),
                                        encoding="utf-8")
    print(f"\n✅ {a.capturar}")
    for nom in nombres:
        r = resumen(cap, nom)
        ult = r[-1]
        print(f"  {nom:16} step={ult.get('step')} fichas={str(ult.get('fichas'))[:56]}")


if __name__ == "__main__":
    main()
