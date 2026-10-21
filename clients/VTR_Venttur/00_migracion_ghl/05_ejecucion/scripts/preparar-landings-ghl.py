#!/usr/bin/env python3
"""
Arma lo necesario para publicar las 50 landings DENTRO de GHL (Sites → Funnels) bajo promo.venttur.com.

Método (22/9): un solo funnel `LP · Calendarios`. Cada landing es un step "plantilla" (una sección con un Custom
Code que la oculta); el contenido lo dibuja el CARGADOR del funnel (Configuración → Código de seguimiento del
cuerpo) leyendo la ruta y buscando la landing en un JSON publicado en la biblioteca de medios de GHL. Este script
genera los fragmentos (fuente de ese JSON), el manifiesto de steps y los redirects de los paths viejos de
Clientify (esos van por API: `crear-redirects-ghl.py`). El JSON y el cargador los arma `generar-renderer-ghl.py`.

Salida (landings-ghl/_ghl/, se regenera entera salvo cargador.html / cargador-url.txt):
  formulario/<slug>.html · calendarios/<slug>.html · aventureras/<slug>.html · especiales/Programas.html
        fragmento de cada landing (CSS acotado a .vtr-lp)
  MANIFEST.md       · una fila por step: nombre, ruta GHL, título SEO, descripción
  redirects.json    · redirects {path, target} para crear-redirects-ghl.py
  REDIRECTS.md      · la misma tabla, para revisar

Uso:  python3 preparar-landings-ghl.py && python3 generar-renderer-ghl.py [--publicar]
"""
import json, re, shutil, html as H
from _marca_landings import LOGO, icono
from _referenciadoras import paginas as paginas_referenciadoras
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
LAND = BASE / "landings-ghl"
OUT = LAND / "_ghl"
CLZ = BASE / "backup-clientify-2026-09/04-landings/html"
DOMAIN = "promo.venttur.com"
VENTTUR_HOME = "https://venttur.com"

FUNNELS = {  # subdir → nombre del funnel en GHL
    "formulario": "LP · Formularios",
    "calendarios": "LP · Calendarios",
    "aventureras": "LP · Aventureras",
}

# Sufijo de programa en las sub-landings viejas → landing de calendario (tipo C)
PROG_CAL = {
    "afamilia": "Intercambio-Calendario",
    "internado": "Internados-Calendario", "internados": "Internados-Calendario",
    "presencial": "Internados-Calendario",
    "summercamp": "Campamentos-Calendario", "summerc": "Campamentos-Calendario", "summer": "Campamentos-Calendario",
    "pathway": "PathwayAlemania-Calendario",
    "gapyear": "GapYear-Calendario", "gapid": "GapYear-Calendario", "gapyear-australia": "GapYear-Calendario",
}
# Campañas/eventos de Clientify (webforms que mueren con Clientify) → form del programa (tipo B)
CAMPANA = [
    (r"^(AAFAMILIA|AAFRNACIA)-|^IntercambioFrancia", "AAFamilia-Agendar"),  # Francia es destino, no programa
    (r"^(PW_|alemaniapathway)", "PW_Alemania_Agendar"),
    (r"^(australia|Australia|GapyearAustralia|RegistroGapyearAustralia|Registro_Australia_Feria)",
     "Estudiar-y-Trabajar-en-Australia"),
    (r"^(boarding|ema$|ema-|luminos$|IBsinFronteras|lagarenne-)", "agendar-ema"),  # La Garenne = evento internados
]
# "SPE Agendamiento - <aventurera>": agendamiento de Internados (embudo SPE) atribuido, no son madres con botones
SPE_AVENTURERA = {"aramirez", "carol", "chuerta", "mgomez", "pgomez"}
CON_AVENTURERA = [
    (r"^video-ema-(.+)$", "entrenamientospe"),       # mismo "Encuentra tu Internado" con video
    (r"^lagarenne-[A-Z]+-(.+)$", "agendar-ema"),     # evento La Garenne por aventurera
]
# Procesos internos sin equivalente → sitio de Venttur. Vacío desde el 23/9: las 5 del programa de referenciadoras
# (PMR, graciasafil, agendarPMR, CapacitacionRef, seguimientoref) se rehicieron como landings (_referenciadoras.py).
INTERNAS = set()
# Páginas de Clientify que sólo embebían algo externo: se redirige directo a eso (23/9, backup 04-landings)
DIRECTAS = {
    "formularioref": "https://docs.google.com/forms/d/e/1FAIpQLSf3MEYt45eryHVuEa-GVuWaW5dEOgfFFNCw-Z5OtHVAtsF9_A/viewform",
    "ChatHistoria": "https://web-production-574701.up.railway.app",
}
# Páginas que se rehacen como landing especial del funnel (no llevan redirect)
ESPECIALES = {"preparate", "PMR", "graciasafil", "agendarPMR", "CapacitacionRef", "seguimientoref"}
MAPS_OFICINA = "https://maps.app.goo.gl/fKp5DfzCg6bwPfdU8"
VIDEO_PREPARATE = "https://iframe.mediadelivery.net/embed/157135/868c6f06-e09d-4e2c-b3f9-bda91ca54e11?autoplay=false&loop=false&muted=false&preload=false"


def ruta_ghl(slug):
    """Ruta del step en GHL. GHL sólo admite minúsculas, números, guiones y barras en la ruta de un paso
    (probado 22/9): las mayúsculas las baja solo y sirve igual sin distinguir, pero el guion bajo lo rechaza.
    Las 2 landings con "_" (EstudiaryTrabajar_Agendar, PW_Alemania_Agendar) viven con "-" y la URL original
    sigue funcionando por un redirect (los redirects de GHL sí aceptan "_"; los usan el agente, el rescate y
    plantillas de WhatsApp aprobadas por Meta, así que la URL original NO puede morir)."""
    return "/" + slug.replace("_", "-")


def handle_map():
    """handle viejo ('abuendia') → slug de aventurera ('AlinaBuendia'), leído de los botones de cada madre."""
    m = {}
    for f in CLZ.glob("agendar-*.html"):
        slug = f.stem[len("agendar-"):]
        if "-" in slug:
            continue
        for h in re.findall(r'promo\.venttur\.com/agendar-([A-Za-z]+)-', f.read_text(errors="ignore")):
            m.setdefault(h.lower(), slug)
    return m


PROGRAMAS = [  # (label, landing de calendario)
    ("Internados", "Internados-Calendario"), ("Intercambio con familia", "Intercambio-Calendario"),
    ("Campamentos de verano", "Campamentos-Calendario"), ("Pathway Alemania", "PathwayAlemania-Calendario"),
    ("Gap Year / Estudia y trabaja", "GapYear-Calendario"), ("Viajes educativos", "ViajesEducativos-Calendario"),
    ("Educación superior", "EducacionSuperior-Calendario"), ("Cursos de idiomas", "CursosIdiomas-Calendario"),
]


def pagina_programas():
    """Página comodín: se configura como 404 y como página por defecto de promo.venttur.com. Cualquier link
    viejo que no conozcamos cae acá y el visitante igual puede agendar (no ve un error)."""
    btns = "".join(f'<a href="/{slug}">{H.escape(lbl)} →</a>' for lbl, slug in PROGRAMAS)
    ref = (LAND / "calendarios" / "Internados-Calendario.html").read_text(encoding="utf-8")
    styles = re.search(r"<style>.*?</style>", ref, re.S).group(0)
    wa = "https://api.whatsapp.com/send/?phone=%2B523319442476&text&type=phone_number&app_absent=0"
    body = (f'<header class="hero"><img src="{LOGO}" '
            f'alt="Venttur Education &amp; Travel"><h1>¡Agenda tu asesoría gratuita!</h1>'
            f'<p>Elige el programa que te interesa.</p></header>'
            f'<main class="wrap"><section class="card"><div class="btns">{btns}</div></section>'
            f'<div class="social">{icono("whatsapp", wa, "WhatsApp")}</div>'
            f'<p class="foot">© Venttur Education &amp; Travel</p></main>'
            # conserva el query entrante (atribuida_a, fbclid) al pasar al calendario
            '<script>(function(){var q=location.search.replace(/\\?/g,function(m,i){return i?"&":m;});'
            'if(!q)return;document.querySelectorAll(".vtr-lp .btns a").forEach(function(a){a.href+=q;});})();</script>')
    doc = (f"<!DOCTYPE html><html><head><title>Programas · Venttur</title>"
           f'<meta name="description" content="Agenda tu asesoría gratuita con Venttur.">'
           f"{styles}</head><body>{body}</body></html>")
    return fragmento(doc)


def pagina_preparate():
    """"Prepárate para tu asesoría": instrucciones para las familias antes de la cita. Rehecha del backup de
    Clientify (/preparate, 23/9) con el mismo contenido y video, en tuteo mexicano."""
    ref = (LAND / "calendarios" / "Internados-Calendario.html").read_text(encoding="utf-8")
    styles = re.search(r"<style>.*?</style>", ref, re.S).group(0)
    extra = ("<style>.prep h2{font-size:1.05rem;color:var(--navy);margin:18px 0 6px}.prep h2:first-child{margin-top:0}"
             ".prep p,.prep li{font-size:.97rem;color:#333;margin-bottom:6px}.prep ul{padding-left:20px}"
             ".prep a{color:var(--navy);font-weight:600}"
             ".video{position:relative;padding-top:56.25%;border-radius:12px;overflow:hidden;background:#000}"
             ".video iframe{position:absolute;inset:0;width:100%;height:100%;border:0}</style>")
    wa = "https://api.whatsapp.com/send/?phone=%2B523319442476&text&type=phone_number&app_absent=0"
    wa_attr = H.escape(wa)
    body = (f'<header class="hero"><img src="{LOGO}" alt="Venttur Education &amp; Travel">'
            f'<h1>¡Prepárate para tu asesoría!</h1>'
            f'<p>Sigue estas indicaciones para aprovechar al máximo la reunión.</p></header>'
            f'<main class="wrap"><section class="card"><div class="video"><iframe src="{H.escape(VIDEO_PREPARATE)}" '
            f'allow="accelerometer;gyroscope;autoplay;encrypted-media;picture-in-picture" allowfullscreen '
            f'loading="lazy" title="Prepárate para tu asesoría"></iframe></div></section>'
            f'<section class="card prep">'
            f'<h2>¿Dónde es la reunión?</h2>'
            f'<p>Si eres de Guadalajara, la reunión es presencial: será un placer recibirte en nuestras oficinas. '
            f'<a href="{MAPS_OFICINA}" target="_blank" rel="noopener">Ver la ubicación</a>.</p>'
            f'<p>Si no eres de Guadalajara, la reunión es virtual: el enlace está en el mensaje de confirmación de tu '
            f'cita. Si no lo encuentras, <a href="{wa_attr}" target="_blank" rel="noopener">escríbenos por WhatsApp</a>.</p>'
            f'<h2>Puntualidad</h2><p>Llega o conéctate entre 5 y 10 minutos antes.</p>'
            f'<h2>Entorno</h2><ul><li>Un lugar tranquilo y sin distracciones.</li>'
            f'<li>No tomes la reunión en movimiento.</li></ul>'
            f'<h2>¿Quiénes pueden asistir?</h2><p>Te recomendamos que, si pueden, asistan ambos padres o cualquier '
            f'adulto responsable de tomar esta decisión. En esta reunión no recomendamos que esté presente el '
            f'estudiante: ¡ya habrá tiempo para platicarlo con él o ella!</p></section>'
            f'<div class="social">{icono("whatsapp", wa, "WhatsApp")}'
            f'{icono("instagram", "https://www.instagram.com/venttur_/", "Instagram")}</div>'
            f'<p class="foot">© Venttur Education &amp; Travel</p></main>')
    doc = (f"<!DOCTYPE html><html><head><title>Prepárate para tu asesoría · Venttur</title>"
           f'<meta name="description" content="Indicaciones para tu asesoría con Venttur: dónde es, cuánto dura y quiénes pueden asistir.">'
           f"{styles}{extra}</head><body>{body}</body></html>")
    return fragmento(doc)


def fragmento(src):
    """HTML completo → fragmento para Custom Code de GHL + metadatos SEO.
    - saca doctype/html/head/body; conserva <link> de CSS, <style> y <script>
    - envuelve todo en <div class="vtr-lp"> y acota el CSS: `body{…}` → `.vtr-lp{…}` y el reset `*{…}` →
      `.vtr-lp *{…}`, para no desarmar el resto de la página de GHL."""
    s = src
    meta = {
        "title": H.unescape((re.search(r"<title>(.*?)</title>", s, re.S) or [None, ""])[1].strip()),
        "description": H.unescape((re.search(r'<meta name="description" content="([^"]*)"', s) or [None, ""])[1]),
    }
    head = (re.search(r"<head>(.*?)</head>", s, re.S) or [None, ""])[1]
    body = (re.search(r"<body[^>]*>(.*)</body>", s, re.S) or [None, s])[1]
    links = "\n".join(re.findall(r'<link rel="stylesheet"[^>]*>', head))
    styles = "\n".join(re.findall(r"<style>.*?</style>", head, re.S))
    styles = re.sub(r"(^|\n|\})\s*\*\s*\{", r"\1\n  .vtr-lp *{", styles)
    styles = re.sub(r"(^|\n|\})\s*body\s*\{", r"\1\n  .vtr-lp{", styles)
    # GHL envuelve el elemento en section/row/column con padding y un .inner de max 1170px (medido en la
    # piloto del 22/9). Se anulan sólo en el contenedor que tiene la landing: ancho completo sin tocar la UI.
    ghl = ("<style>.c-section:has(.vtr-lp),.c-row:has(.vtr-lp),.c-column:has(.vtr-lp){padding:0!important}"
           ".c-section:has(.vtr-lp) .inner{max-width:none!important;margin:0!important}</style>")
    frag = f"{ghl}\n{links}\n{styles}\n<div class=\"vtr-lp\">\n{body.strip()}\n</div>\n"
    return frag, meta


def main():
    # cargador.html / cargador-url.txt describen lo que está PUBLICADO en GHL (los escribe generar-renderer-ghl.py
    # --publicar): se conservan. Después de correr este script hay que correr generar-renderer-ghl.py.
    vivos = {n: (OUT / n).read_bytes() for n in ("cargador.html", "cargador-url.txt") if (OUT / n).exists()}
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    for n, b in vivos.items():
        (OUT / n).write_bytes(b)
    nuevos, filas_m = {}, []
    for sub, funnel in FUNNELS.items():
        (OUT / sub).mkdir(parents=True)
        for f in sorted((LAND / sub).glob("*.html")):
            if f.stem.lower() in {k.lower() for k in nuevos}:
                raise SystemExit(f"❌ colisión de slug (GHL no distingue mayúsculas): {f.stem}")
            nuevos[f.stem] = sub
            frag, meta = fragmento(f.read_text(encoding="utf-8"))
            (OUT / sub / f.name).write_text(frag, encoding="utf-8")
            filas_m.append((funnel, f.stem, ruta_ghl(f.stem), meta["title"], meta["description"], f"{sub}/{f.name}"))

    (OUT / "especiales").mkdir(parents=True)
    frag, meta = pagina_programas()
    (OUT / "especiales" / "Programas.html").write_text(frag, encoding="utf-8")
    filas_m.append(("LP · Calendarios", "Programas", "/programas", meta["title"], meta["description"],
                    "especiales/Programas.html"))
    frag, meta = pagina_preparate()
    (OUT / "especiales" / "preparate.html").write_text(frag, encoding="utf-8")
    filas_m.append(("LP · Calendarios", "preparate", "/preparate", meta["title"], meta["description"],
                    "especiales/preparate.html"))
    ref_styles = re.search(r"<style>.*?</style>", (LAND / "calendarios" / "Internados-Calendario.html").read_text(encoding="utf-8"), re.S).group(0)
    for slug, doc in paginas_referenciadoras(ref_styles).items():
        frag, meta = fragmento(doc)
        (OUT / "especiales" / f"{slug}.html").write_text(frag, encoding="utf-8")
        filas_m.append(("LP · Calendarios", slug, ruta_ghl(slug), meta["title"], meta["description"], f"especiales/{slug}.html"))

    hm = handle_map()
    redirects, revisar = [], []

    def add(path, target, motivo):
        if target.startswith("/"):
            ruta, _, q = target.partition("?")   # sólo la ruta: el query lleva "atribuida_a"
            target = f"https://{DOMAIN}{ruta_ghl(ruta[1:])}" + (f"?{q}" if q else "")
        redirects.append({"path": f"/{path}", "target": target, "motivo": motivo})

    for slug in sorted(nuevos):
        if ruta_ghl(slug) != f"/{slug}":
            add(slug, f"/{slug}", "URL original con guion bajo → step GHL con guion medio")

    listados = {p.stem for p in CLZ.glob("*.html")}
    linkeados = set()
    for f in CLZ.glob("*.html"):
        linkeados |= set(re.findall(r'promo\.venttur\.com/(agendar-[A-Za-z]+-[A-Za-z\-]+)', f.read_text(errors="ignore")))
    for v in sorted(listados | linkeados):
        if v in nuevos or v in ESPECIALES:
            continue
        if v in DIRECTAS:
            add(v, DIRECTAS[v], "embebía algo externo → directo a eso"); continue
        if v.startswith("agendar-") and v[len("agendar-"):] in SPE_AVENTURERA:
            h = v[len("agendar-"):]
            add(v, f"/SPEagendar?atribuida_a={hm.get(h.lower(), h)}", "SPE agendamiento por aventurera")
            continue
        m = re.match(r"^agendar-([A-Za-z]+)-(.+?)-?$", v)
        if m:
            h, prog = m.group(1), m.group(2).lower()
            cal = PROG_CAL.get(prog)
            if not cal:
                revisar.append(v); add(v, "/agendar-ema", "programa no reconocido → Internados"); continue
            add(v, f"/{cal}?atribuida_a={hm.get(h.lower(), h)}",
                "sub-landing aventurera" + ("" if h.lower() in hm else " (handle sin madre)"))
            continue
        hit = False
        for rx, dst in CON_AVENTURERA:
            m = re.match(rx, v)
            if m:
                add(v, f"/{dst}?atribuida_a={hm.get(m.group(1).lower(), m.group(1))}", "campaña con aventurera")
                hit = True; break
        if hit:
            continue
        for rx, dst in CAMPANA:
            if re.match(rx, v):
                add(v, f"/{dst}", "campaña/evento → form del programa"); hit = True; break
        if hit:
            continue
        add(v, VENTTUR_HOME, "interna referenciadoras/afiliados (sin equivalente)" if v in INTERNAS else "sin clasificar")
        revisar.append(v)

    (OUT / "redirects.json").write_text(json.dumps(redirects, indent=1, ensure_ascii=False), encoding="utf-8")

    with open(OUT / "MANIFEST.md", "w", encoding="utf-8") as f:
        f.write(f"# Landings en GHL · {len(filas_m)} steps del funnel `LP · Calendarios`\n\n"
                "Una fila = un step. Cada step es una copia de la plantilla (Clonar paso o \"Utilizar los "
                "actuales\" → Internados-Calendario) con el **nombre** y la **ruta** de la tabla; el contenido lo "
                "dibuja el cargador del funnel según la ruta. El título SEO de la tabla es el que pone el cargador "
                "en el navegador; en el step se puede cargar igual para las vistas previas de links. La columna "
                "Archivo es la fuente del JSON (no se pega a mano).\n\n")
        cur = None
        for funnel, name, path, title, desc, arch in filas_m:
            if funnel != cur:
                cur = funnel
                f.write(f"\n## Grupo `{funnel}`\n\n| ✓ | Step | Path | Título SEO | Descripción | Archivo |\n|---|---|---|---|---|---|\n")
            f.write(f"| [ ] | {name} | `{path}` | {title} | {desc or '—'} | `_ghl/{arch}` |\n")

    with open(OUT / "REDIRECTS.md", "w", encoding="utf-8") as f:
        f.write(f"# Redirects {DOMAIN} (paths viejos de Clientify → GHL)\n\n{len(redirects)} redirects. "
                "Se crean por API con `scripts/crear-redirects-ghl.py` (requiere el dominio ya conectado en GHL).\n\n")
        if revisar:
            f.write("## ⚠️ Revisar con Mauricio (sin equivalente GHL → venttur.com)\n\n" +
                    "".join(f"- `/{r}`\n" for r in revisar) + "\n")
        f.write("| Path viejo | Destino | Motivo |\n|---|---|---|\n")
        for r in redirects:
            f.write(f"| `{r['path']}` | `{r['target']}` | {r['motivo']} |\n")

    print(f"✓ {len(filas_m)} fragmentos en {OUT} ({', '.join(f'{k}: {sum(1 for x in nuevos.values() if x == k)}' for k in FUNNELS)})")
    print(f"✓ {len(redirects)} redirects → redirects.json · MANIFEST.md · REDIRECTS.md")
    if revisar:
        print(f"⚠️ {len(revisar)} a revisar: {', '.join(revisar)}")


if __name__ == "__main__":
    main()
