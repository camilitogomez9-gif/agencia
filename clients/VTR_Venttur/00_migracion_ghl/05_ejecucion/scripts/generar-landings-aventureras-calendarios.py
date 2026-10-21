#!/usr/bin/env python3
"""
Genera 2 tipos de landing que faltaban (además de las 12 de formulario ya hechas):

 TIPO C · Landings de CALENDARIO (secundarias) — brand + logo + título + calendario GHL embebido (sin form).
          Son a las que apuntan los botones de las aventureras. Usan los embed codes reales de GHL.
 TIPO A · Landings de AVENTURERA (madre) — brand + título + N botones (uno por programa) que redirigen a
          las landings de calendario con ?atribuida_a=<aventurera> + redes propias de cada aventurera.

Referencia: originales Clientify en backup-clientify-2026-09/04-landings/html/ (agendar-<name>[-programa]).
Datos de aventureras en landings-ghl/_data/aventureras.json (32).

Output:
  landings-ghl/calendarios/<slug>.html   (10)
  landings-ghl/aventureras/agendar-<slug>.html  (32)
"""
import json, re, html as H, os
from pathlib import Path

ROOT = Path("/Users/camilo/Downloads/camilo-workspace")
OUT = ROOT / "clients/VTR_Venttur/00_migracion_ghl/05_ejecucion/landings-ghl"
AVENTURERAS_JSON = OUT / "_data/aventureras.json"
CLZ = ROOT / "clients/VTR_Venttur/00_migracion_ghl/05_ejecucion/backup-clientify-2026-09/04-landings/html"  # extraído de los originales Clientify (sin "ema": no es aventurera, es el form Internados)

from _marca_landings import LOGO, icono  # logo en GHL + íconos SVG embebidos (los PNG de Unlayer dan 403)
IG_V = "https://www.instagram.com/venttur_/"
WA_V = "https://api.whatsapp.com/send/?phone=%2B523319442476&text&type=phone_number&app_absent=0"

# --- TIPO C · calendarios (slug → cal_id, embed_id [de la agencia · construido p/ pathway+viajes], display, subtítulo) ---
CAL = {
    "Internados-Calendario":        ("CIxOV100yyRFqPoa6LdK", "CIxOV100yyRFqPoa6LdK_1790064860151", "Internados", "Agenda tu asesoría sobre internados en el extranjero."),
    "Intercambio-Calendario":       ("SiAPsk27X5yilff5bSS5", "SiAPsk27X5yilff5bSS5_1790064947034", "Intercambio académico con familias", "Agenda tu asesoría sobre año académico con familia anfitriona."),
    "Campamentos-Calendario":       ("981EzNS7jf9HhJNkL41W", "981EzNS7jf9HhJNkL41W_1790064826861", "Campamentos de verano", "Agenda tu asesoría sobre campamentos de verano internacionales."),
    "PathwayAlemania-Calendario":   ("oNN7oLWsNhQlWi7q7pDX", "oNN7oLWsNhQlWi7q7pDX_1790064990001", "Pathway Alemania", "Agenda tu asesoría sobre el camino a la universidad en Alemania."),
    "GapYear-Calendario":           ("Omgde6Ko8TGKYMtiUb1x", "Omgde6Ko8TGKYMtiUb1x_1790064879142", "Gap Year / Estudia y Trabaja", "Agenda tu asesoría sobre estudiar y trabajar en el extranjero."),
    "CursosIdiomas-Calendario":     ("5PxslDhdQxZeDcKmLYNq", "5PxslDhdQxZeDcKmLYNq_1790064802719", "Cursos de idiomas en el extranjero", "Agenda tu asesoría sobre cursos de idiomas en el extranjero."),
    "EducacionSuperior-Calendario": ("RUjWx74NPK77FPUcs5ME", "RUjWx74NPK77FPUcs5ME_1790064927820", "Educación superior", "Agenda tu asesoría sobre estudios universitarios y de posgrado."),
    "ViajesEducativos-Calendario":  ("j0jcAdaieJXaoPZBempp", "j0jcAdaieJXaoPZBempp_1790065010001", "Viajes educativos", "Agenda tu asesoría sobre viajes educativos."),
    "JuanJose-Calendario":          ("QJQyabdWhBgYtjeGcEKZ", "QJQyabdWhBgYtjeGcEKZ_1790064907462", "Agenda con Juan José Alfaro", "Agenda una asesoría con Juan José Alfaro."),
    "Niza-Calendario":              ("fOsl9U4b40ulCczFwf69", "fOsl9U4b40ulCczFwf69_1790064969100", "Agenda con Niza Valeriano", "Agenda una asesoría con Niza Valeriano."),
}
# embeds NO provistos por la agencia (construidos con el mismo formato) — verificar el cal_id
CONSTRUIDOS = {"PathwayAlemania-Calendario", "ViajesEducativos-Calendario"}

# --- aventurera: variante de programa → (slug landing calendario, label del botón) ---
PROG = {
    "afamilia":   ("Intercambio-Calendario", "Intercambio con familia"),
    "internado":  ("Internados-Calendario", "Internados"),
    "internados": ("Internados-Calendario", "Internados"),
    "summercamp": ("Campamentos-Calendario", "Summer Camp"),
    "summer":     ("Campamentos-Calendario", "Summer Camp"),
    "pathway":    ("PathwayAlemania-Calendario", "Pathway Alemania"),
    "gapyear":    ("GapYear-Calendario", "Gap Year"),
    "gapid":      ("GapYear-Calendario", "Gap Year"),
    "summerc":    ("Campamentos-Calendario", "Summer Camp"),
    "gapyear-australia": ("GapYear-Calendario", "Gap Year"),
}
ORDEN = ["internado", "afamilia", "summercamp", "pathway", "gapyear"]  # orden de botones

CSS = """
  :root{ --navy:#0d1b40; --navy2:#16265a; --accent:#c9a24b; --bg:#f5f7fb; }
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;background:var(--bg);color:#1a1a1a;line-height:1.5;-webkit-font-smoothing:antialiased}
  .hero{background:linear-gradient(160deg,var(--navy) 0%,var(--navy2) 100%);color:#fff;padding:30px 16px 40px;text-align:center}
  .hero img{width:180px;max-width:60%;margin:0 auto 18px;display:block}
  .hero h1{font-size:1.5rem;font-weight:700;max-width:640px;margin:0 auto 8px;line-height:1.3}
  .hero p{font-size:1rem;opacity:.9;max-width:560px;margin:0 auto}
  .wrap{max-width:640px;margin:-24px auto 0;padding:0 16px 40px}
  .card{background:#fff;border-radius:16px;box-shadow:0 8px 30px rgba(13,27,64,.12);padding:22px 20px;margin-bottom:18px}
  .btns{display:flex;flex-direction:column;gap:12px}
  .btns a{display:block;background:var(--navy);color:#fff;text-decoration:none;border-radius:12px;padding:16px 18px;font-size:1.05rem;font-weight:700;text-align:center;transition:background .15s,transform .1s}
  .btns a:hover{background:var(--navy2);transform:translateY(-1px)}
  iframe.cal{width:100%;min-height:700px;border:none;overflow:hidden}
  .social{text-align:center;padding:18px 0 8px}
  .social a{display:inline-block;margin:0 7px}
  .social img{width:34px;height:34px;opacity:.9}
  .foot{text-align:center;font-size:.75rem;color:#8a93a6;padding:6px 16px 24px}
"""

# El query de la landing (?atribuida_a=, fbclid, utm) se reenvía al widget, normalizando el "?x?y" que dejan los
# redirects de GHL a "?x&y": la atribución no depende de que
# form_embed.js lo haga cuando la página se sirve fuera de GHL (Vercel).
EMBED = ('<iframe class="cal" src="https://api.leadconnectorhq.com/widget/booking/{cal}" allow="payment" '
         'scrolling="no" id="{eid}"></iframe><br>'
         '<script>(function(){{var f=document.getElementById("{eid}");'
         'var q=location.search.replace(/\\?/g,function(m,i){{return i?"&":m;}});'
         'if(q)f.src=f.getAttribute("src")+q;}})();</script>'
         '<script src="https://link.msgsndr.com/js/form_embed.js" type="text/javascript"></script>')


def esc(u):
    # el valor extraído del HTML original puede venir ya HTML-encoded (&amp;) → unescape antes de escapar
    return H.escape(H.unescape((u or "").strip()), quote=True)


def social_block(wa, ig, tk):
    a = []
    # H.unescape: el valor extraído del HTML original puede venir ya encoded (&amp;); icono() escapa una sola vez
    if wa: a.append(icono("whatsapp", H.unescape(wa.strip()), "WhatsApp"))
    if ig: a.append(icono("instagram", H.unescape(ig.strip()), "Instagram"))
    if tk: a.append(icono("tiktok", H.unescape(tk.strip()), "TikTok"))
    return '<div class="social">' + "".join(a) + '</div>' if a else ""


def page(title, hero_h1, hero_p, body_html, social=""):
    return f"""<!DOCTYPE html>
<html lang="es"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{H.escape(title)}</title>
<meta name="robots" content="index,follow">
<style>{CSS}</style></head><body>
<header class="hero"><img src="{LOGO}" alt="Venttur Education &amp; Travel">
<h1>{H.escape(hero_h1)}</h1><p>{H.escape(hero_p)}</p></header>
<main class="wrap">{body_html}{social}
<p class="foot">© Venttur Education &amp; Travel</p></main>
</body></html>
"""


def decamel(s):
    return re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', s).strip()


def gen_calendarios():
    d = OUT / "calendarios"; d.mkdir(parents=True, exist_ok=True)
    for slug, (cal, eid, disp, sub) in CAL.items():
        body = f'<section class="card">{EMBED.format(cal=cal, eid=eid)}</section>'
        d.joinpath(f"{slug}.html").write_text(
            page(f"Agenda · {disp} · Venttur", "¡Agenda tu asesoría gratuita!", sub, body,
                 social_block(WA_V, IG_V, "")), encoding="utf-8")
    print(f"  ✓ {len(CAL)} landings de calendario → {d}")


def gen_aventureras():
    d = OUT / "aventureras"; d.mkdir(parents=True, exist_ok=True)
    data = json.load(open(AVENTURERAS_JSON))
    n = 0
    for slug, v in data.items():
        # Fuente de verdad de los programas: los botones de la madre original de Clientify (el JSON extraído
        # perdía variantes con mayúsculas como "Afamilia" o "SummerC").
        orig = CLZ / f"agendar-{slug}.html"
        if orig.exists():
            progs = [x.lower().rstrip("-") for x in
                     re.findall(r'promo\.venttur\.com/agendar-[A-Za-z]+-([A-Za-z\-]+?)-?"', orig.read_text(errors="ignore"))]
        else:
            progs = v.get("programas") or []
        # Las madres de Clientify usan variantes del nombre (internado/internados, gapyear/gapid, summercamp/summer):
        # se normalizan vía PROG y se ordenan por el orden canónico de la landing destino.
        orden_land = [PROG[k][0] for k in ORDEN]
        keys = sorted((p for p in progs if p in PROG), key=lambda p: orden_land.index(PROG[p][0])) if progs else ORDEN
        # dedup por landing destino
        seen = set(); btns = []
        for k in keys:
            if k not in PROG:
                continue
            land, label = PROG[k]
            if land in seen:
                continue
            seen.add(land)
            btns.append(f'<a href="https://promo.venttur.com/{land}?atribuida_a={slug}">{H.escape(label)} →</a>')
        body = '<section class="card"><div class="btns">' + "".join(btns) + '</div></section>'
        nombre = decamel(slug)
        social = social_block(v.get("wa") or WA_V, v.get("ig") or IG_V, v.get("tiktok") or "")
        d.joinpath(f"agendar-{slug}.html").write_text(
            page(f"Agenda tu cita con Venttur · {nombre}", "¡Elige tu programa y agenda tu cita!",
                 f"Con {nombre} · Venttur Education & Travel", body, social), encoding="utf-8")
        n += 1
    print(f"  ✓ {n} landings de aventureras → {d}")


if __name__ == "__main__":
    gen_calendarios()
    gen_aventureras()
    print(f"\n⚠️ Embeds CONSTRUIDOS (no provistos por la agencia, verificar cal_id): {sorted(CONSTRUIDOS)}")
