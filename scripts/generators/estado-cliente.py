#!/usr/bin/env python3
"""Genera el tablero de estado de un cliente (HTML autocontenido).

Fuente de verdad: clients/<CLIENTE>/06_docs/estado/estado.json
Salida:           clients/<CLIENTE>/06_docs/estado/estado-proyecto.html

Además del JSON, lee solo:
  - el documento de puntos de cierre (qué secciones siguen sin respuesta),
  - Airtable (cuántos pacientes hay cargados; caché de 6 h, falla en silencio),
  - la fecha de hoy (semanas que lleva el pendiente de un lado).

Uso:
  python3 scripts/generators/estado-cliente.py --cliente XXX_Cliente
  python3 scripts/generators/estado-cliente.py --all
  python3 scripts/generators/estado-cliente.py --carpeta ~/ruta/a/XXX_Cliente   # fuera del workspace
  python3 scripts/generators/estado-cliente.py --hook   # lee el JSON del hook de Claude Code por stdin

El archivo solo se reescribe si el contenido cambió, para no generar commits de ruido.
"""
import argparse
import datetime as dt
import html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLIENTS = ROOT / "clients"
REL_ESTADO = Path("06_docs/estado")
CACHE_TTL = 6 * 3600

ESTADOS = {
    "cerrada": ("Cerrada", "success", "", 'var(--success)'),
    "en_curso": ("En curso", "warning", "ti-progress", 'var(--warning)'),
    "bloqueada": ("Bloqueada", "danger", "ti-circle-dashed", 'var(--danger)'),
    "lista": ("Lista para arrancar", "neutral", "ti-circle-dashed", 'var(--muted)'),
    "no_iniciada": ("No iniciada", "neutral", "ti-circle-dashed", 'var(--muted)'),
}
PRIORIDAD = {"🔴": "danger", "🟡": "warning", "🟢": "success"}


def e(s):
    return html.escape(str(s), quote=True)


def secciones_abiertas(doc: Path, prefijo: str):
    """Devuelve [(id, prioridad, titulo, abierta)] de las secciones '## R1 🔴 ...'."""
    if not doc.exists():
        return []
    texto = doc.read_text(encoding="utf-8")
    patron = re.compile(rf"^## ({re.escape(prefijo)}\d+) (🔴|🟡|🟢) (.+)$", re.M)
    marcas = list(patron.finditer(texto))
    out = []
    for i, m in enumerate(marcas):
        fin = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
        siguiente = re.search(r"^#{1,2} ", texto[m.end():fin], re.M)
        bloque = texto[m.end(): m.end() + siguiente.start()] if siguiente else texto[m.end():fin]
        abierta = bool(re.search(r"^> \*[^*\n]*:\*\s*$", bloque, re.M))
        out.append((m.group(1), m.group(2), m.group(3).strip(), abierta))
    return out


def pacientes_airtable(cdir: Path, cfg: dict):
    """Cuenta registros de la tabla de pacientes. Usa caché; devuelve None si no puede."""
    cache_f = cdir / REL_ESTADO / ".cache.json"
    cache = {}
    if cache_f.exists():
        try:
            cache = json.loads(cache_f.read_text())
        except Exception:
            cache = {}
    if cache.get("ts", 0) > time.time() - CACHE_TTL and "pacientes" in cache:
        return cache["pacientes"]
    cred = cdir / cfg.get("credenciales", "")
    try:
        pat = re.search(r"^PAT=(\S+)", cred.read_text(), re.M).group(1)
        n, offset = 0, None
        while True:
            url = f"https://api.airtable.com/v0/{cfg['base']}/{cfg['tabla_pacientes']}?pageSize=100"
            if offset:
                url += f"&offset={offset}"
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {pat}"})
            d = json.load(urllib.request.urlopen(req, timeout=8))
            n += len(d.get("records", []))
            offset = d.get("offset")
            if not offset:
                break
    except Exception:
        return cache.get("pacientes")
    cache_f.write_text(json.dumps({"ts": time.time(), "pacientes": n}))
    return n


def pill(texto, tono):
    return f'<span class="pill {tono}">{e(texto)}</span>'


def render(cdir: Path, st: dict) -> str:
    hoy = dt.date.today()
    fu = st.get("fuentes", {})

    cerradas = sum(1 for f in st["fases"] if f["estado"] == "cerrada")
    cobrado = sum(c["usd"] for c in st.get("cobros", []) if c.get("estado") == "cobrado")
    total = st.get("contrato", {}).get("pago_inicial_usd", 0)

    pend = st.get("pendiente_en") or {}
    semanas, quien = None, pend.get("quien")
    if pend.get("desde"):
        semanas = (hoy - dt.date.fromisoformat(pend["desde"])).days // 7
    lbl_sem = "Semanas con el pendiente de nuestro lado" if quien == "nosotros" else "Semanas esperando al cliente"
    tono_sem = "danger" if (quien == "nosotros" and semanas and semanas >= 2) else ""

    secciones = secciones_abiertas(cdir / fu.get("puntos_de_cierre", ""), fu.get("secciones_cliente", "R"))
    abiertas = [s for s in secciones if s[3]]

    pac = None
    if fu.get("airtable"):
        pac = pacientes_airtable(cdir, fu["airtable"])

    m = []
    m.append(("Fases del contrato cerradas", f"{cerradas} de {len(st['fases'])}", ""))
    m.append(("Cobrado del pago inicial", f"USD {cobrado} / {total}", ""))
    if semanas is not None:
        m.append((lbl_sem, str(semanas), tono_sem))
    if st.get("objetivo"):
        m.append((st["objetivo"]["label"], st["objetivo"]["valor"], ""))
    metricas = "".join(
        f'<div class="metric"><p class="lbl">{e(l)}</p><p class="num {t}">{e(v)}</p></div>' for l, v, t in m
    )

    filas = []
    for f in st["fases"]:
        nombre_estado, tono, icono, color = ESTADOS.get(f["estado"], ESTADOS["no_iniciada"])
        etiqueta = f.get("etiqueta", nombre_estado)
        extra = ""
        if f.get("progreso_auto") == "pacientes_airtable" and pac is not None:
            meta = fu["airtable"].get("meta_pacientes")
            extra = f'<p class="sub auto">Pacientes en Airtable: {pac}' + (f" de ~{meta}" if meta else "") + "</p>"
        filas.append(
            f'<div class="row"><span class="ico" style="border-color:{color};background:{color if f["estado"] == "cerrada" else "transparent"}" aria-hidden="true"></span>'
            f'<div class="grow"><div class="head"><p class="ph">{e(f["nombre"])}</p>{pill(etiqueta, tono)}</div>'
            f'<p class="sub">{e(f["detalle"])}</p>{extra}'
            f'<div class="bar"><div style="width:{int(f.get("progreso", 0))}%;background:{color}"></div></div></div></div>'
        )

    def items(lista):
        out = []
        for it in lista:
            cls = ' class="it done"' if it.get("hecho") else ' class="it"'
            out.append(f"<p{cls}>{e(it['texto'])}</p>")
        return "".join(out) or '<p class="it">Nada pendiente</p>'

    cli = "".join(
        f'<p class="it"><span class="dot {PRIORIDAD.get(p, "")}"></span>{e(i)} · {e(t)}</p>' for i, p, t, _ in abiertas
    ) or '<p class="it">Nada pendiente</p>'
    resp = len(secciones) - len(abiertas)
    cli_titulo = f"Cliente · {resp} de {len(secciones)} respondidos" if secciones else "Cliente"

    bl = st.get("bloqueos", {})
    bloqueos = (
        f'<div class="card dangerb"><p class="who danger">Nosotros</p>{items(bl.get("nosotros", []))}</div>'
        f'<div class="card"><p class="who warning">{e(cli_titulo)}</p>{cli}</div>'
        f'<div class="card"><p class="who accent">Decisiones tuyas</p>{items(bl.get("decisiones", []))}</div>'
    )

    pasos = []
    for p in st.get("camino", []):
        tono = "success" if p.get("hito_cobro") else "neutral"
        hecho = " done" if p.get("hecho") else ""
        check = '✓ ' if p.get("hecho") else ""
        pasos.append(
            f'<div class="row{hecho}"><span class="pill {tono} when">{check}{e(p["cuando"])}</span>'
            f'<div><p class="ph">{e(p["titulo"])}</p><p class="sub">{e(p["detalle"])}</p></div></div>'
        )
    alerta = (
        f'<p class="sub warn">⚠ {e(st["alerta_camino"])}</p>'
        if st.get("alerta_camino") else ""
    )
    fuera = "".join(f'<p class="it">{e(x)}</p>' for x in st.get("fuera_de_contrato", []))

    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Estado del proyecto · {e(st["id"])}</title>
<style>
:root{{--bg:#faf9f5;--s1:#f0eee6;--s2:#fff;--tx:#141413;--tx2:#5e5d59;--muted:#87867f;--bd:rgba(31,30,29,.15);
--success:#3b6d11;--bgs:#eaf3de;--warning:#854f0b;--bgw:#faeeda;--danger:#a32d2d;--bgd:#fcebeb;--accent:#534ab7;--bga:#eeedfe}}
@media (prefers-color-scheme:dark){{:root{{--bg:#1f1e1d;--s1:#2a2928;--s2:#262624;--tx:#faf9f5;--tx2:#c2c0b6;--muted:#9c9a92;--bd:rgba(222,220,209,.15);
--success:#97c459;--bgs:#173404;--warning:#ef9f27;--bgw:#412402;--danger:#f09595;--bgd:#501313;--accent:#afa9ec;--bga:#26215c}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--tx);font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}}
main{{max-width:760px;margin:0 auto;padding:24px 16px 40px}}h1{{font-size:22px;font-weight:500;margin:0 0 4px}}
.lbl{{font-size:12px;color:var(--muted);margin:0 0 8px}}.sec{{margin:22px 0 8px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}}.grid3{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}}
.metric{{background:var(--s1);border-radius:8px;padding:14px}}.num{{font-size:24px;font-weight:500;margin:0}}.num.danger{{color:var(--danger)}}
.card{{background:var(--s2);border:.5px solid var(--bd);border-radius:12px;padding:14px 18px}}.dangerb{{border-color:var(--danger)}}
.row{{display:flex;align-items:flex-start;gap:12px;padding:10px 0;border-top:.5px solid var(--bd)}}.row:first-child{{border-top:none}}
.row.done{{opacity:.55}}.ico{{flex:none;width:14px;height:14px;border-radius:50%;border:2px solid;margin-top:4px}}.grow{{flex:1;min-width:0}}.head{{display:flex;justify-content:space-between;gap:8px}}
.ph{{font-size:14px;font-weight:500;margin:0}}.sub{{font-size:13px;color:var(--tx2);margin:2px 0 0;line-height:1.5}}.sub.auto{{color:var(--accent)}}.sub.warn{{color:var(--warning);margin-top:10px}}
.bar{{height:6px;background:var(--s1);border-radius:3px;overflow:hidden;margin-top:6px}}.bar div{{height:100%}}
.pill{{font-size:12px;padding:2px 10px;border-radius:8px;white-space:nowrap}}.pill.success{{background:var(--bgs);color:var(--success)}}.pill.warning{{background:var(--bgw);color:var(--warning)}}
.pill.danger{{background:var(--bgd);color:var(--danger)}}.pill.neutral{{background:var(--s1);color:var(--tx2)}}.when{{min-width:92px;text-align:center}}
.who{{font-size:13px;font-weight:500;margin:0 0 6px;display:flex;align-items:center;gap:6px}}.who.danger{{color:var(--danger)}}.who.warning{{color:var(--warning)}}.who.accent{{color:var(--accent)}}
.it{{font-size:13px;color:var(--tx2);margin:5px 0;line-height:1.5}}.it.done{{text-decoration:line-through;opacity:.6}}
.dot{{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:7px;background:var(--muted)}}.dot.danger{{background:var(--danger)}}.dot.warning{{background:var(--warning)}}.dot.success{{background:var(--success)}}
footer{{font-size:12px;color:var(--muted);margin-top:24px}}
</style></head><body><main>
<h1>{e(st["cliente"])} · estado del proyecto</h1>
<p class="lbl">Contrato: {e(st.get("contrato", {}).get("fuente", ""))}</p>
<div class="grid" style="margin-top:14px">{metricas}</div>
<p class="lbl sec">Las fases del contrato</p><div class="card">{''.join(filas)}</div>
<p class="lbl sec">Qué nos bloquea, según quién lo tiene que resolver</p><div class="grid3">{bloqueos}</div>
<p class="lbl sec">Camino al 100% del contrato</p><div class="card">{''.join(pasos)}{alerta}</div>
<p class="lbl sec">Fuera del contrato original (cotizar aparte o posponer)</p><div class="card">{fuera}</div>
<footer>Datos al {hoy.isoformat()} · generado por scripts/generators/estado-cliente.py a partir de estado.json, {e(fu.get("puntos_de_cierre", ""))} y Airtable. No editar a mano.</footer>
</main></body></html>
"""


def generar(cdir: Path, verbose=True):
    sj = cdir / REL_ESTADO / "estado.json"
    if not sj.exists():
        return False
    st = json.loads(sj.read_text(encoding="utf-8"))
    out = cdir / REL_ESTADO / "estado-proyecto.html"
    nuevo = render(cdir, st)
    if out.exists() and out.read_text(encoding="utf-8") == nuevo:
        if verbose:
            print(f"{cdir.name}: sin cambios")
        return False
    out.write_text(nuevo, encoding="utf-8")
    if verbose:
        print(f"{cdir.name}: actualizado → {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}")
    return True


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--cliente")
    g.add_argument("--carpeta", help="ruta a una carpeta de cliente fuera del workspace")
    g.add_argument("--all", action="store_true")
    g.add_argument("--hook", action="store_true")
    a = ap.parse_args()

    if a.cliente:
        generar(CLIENTS / a.cliente)
    elif a.carpeta:
        generar(Path(a.carpeta).expanduser().resolve())
    elif a.all:
        for c in sorted(CLIENTS.iterdir()):
            if (c / REL_ESTADO / "estado.json").exists():
                generar(c)
    else:
        try:
            data = json.load(sys.stdin)
            fp = Path(data.get("tool_input", {}).get("file_path", "")).resolve()
            rel = fp.relative_to(CLIENTS)
        except Exception:
            return
        if fp.name == "estado-proyecto.html":
            return
        generar(CLIENTS / rel.parts[0], verbose=False)


if __name__ == "__main__":
    main()
