#!/usr/bin/env python3
"""
Genera las landings de agendamiento GHL (estáticas, self-contained) que reemplazan a las
Clientify. Modelo (decisión la agencia): form → W4 (crea contacto + atribuida_a + folio) + CAPI folio,
luego embed de calendario GHL del programa. Fidelidad a la marca Venttur (logo, navy #0d1b40, social).

Slugs EXACTOS (hardcodeados en rescate + plantillas Meta APPROVED — no cambiar los 5 primeros).
Deploy: donde se sirva promo.venttur.com/<slug> (GHL Funnels o CNAME a host estático).

Output: 05_ejecucion/landings-ghl/<slug>.html
"""
import html
from pathlib import Path

OUT = Path("/Users/camilo/Downloads/camilo-workspace/clients/VTR_Venttur/00_migracion_ghl/05_ejecucion/landings-ghl/formulario")
OUT.mkdir(parents=True, exist_ok=True)

W4_WEBHOOK = "https://[TU-INSTANCIA-N8N]/webhook/vtr-form-landing-ghl-08d86c06"
CAPI_WEBHOOK = "https://[TU-INSTANCIA-N8N]/webhook/capi-registro-folio-vtr-supabase"
from _marca_landings import LOGO, icono  # logo en GHL + íconos SVG embebidos (los PNG de Unlayer dan 403)
WA = "https://api.whatsapp.com/send/?phone=%2B523319442476&text&type=phone_number&app_absent=0"
IG = "https://www.instagram.com/venttur_/"
CAL_BASE = "https://api.leadconnectorhq.com/widget/booking/"

# slug → (programa canónico, calendarId, subtítulo, video_url|None)
# Slugs ALINEADOS a §F de la guía de raíz + doc 13 §13.6 (fuente autoritativa).
# Los 6 bloqueantes (hardcodeados en plantillas Meta APPROVED): AAFamilia-Agendar, PW_Alemania_Agendar,
# SummerCamp-Agendar, agendar-ema, entrenamientospe, SPEagendar. Cambiarlos rompe outreach/Meta.
VIDEO_SPE = "https://iframe.mediadelivery.net/embed/157135/66dc6f37-54e4-4152-b532-6520b3f1d8c8?autoplay=false"
LANDINGS = [
    # Bloqueantes (Meta APPROVED) — slugs FIJOS
    ("agendar-ema", "Internados", "CIxOV100yyRFqPoa6LdK",
     "Educación con internado en el extranjero para tu hijo o hija.", None),
    ("AAFamilia-Agendar", "Intercambio académico con familias", "SiAPsk27X5yilff5bSS5",
     "Un año académico viviendo con una familia anfitriona en el extranjero.", None),
    ("SummerCamp-Agendar", "Campamentos de verano", "981EzNS7jf9HhJNkL41W",
     "Campamentos de verano internacionales para vivir una experiencia única.", None),
    ("PW_Alemania_Agendar", "Pathway Alemania", "oNN7oLWsNhQlWi7q7pDX",
     "Tu camino a la universidad en Alemania con el programa Pathway.", None),
    ("entrenamientospe", "Internados", "CIxOV100yyRFqPoa6LdK",
     "Descubre cómo encontrar el internado ideal para tu hijo o hija.", VIDEO_SPE),
    ("SPEagendar", "Internados", "CIxOV100yyRFqPoa6LdK",
     "Agenda tu asesoría del Sistema Personal de Entrenamiento (SPE).", None),
    # Rescate F1 (hardcodeados en el mensaje de rescate) — slugs FIJOS
    ("EstudiaryTrabajar_Agendar", "Gap Year / Estudia y Trabaja", "Omgde6Ko8TGKYMtiUb1x",
     "Estudia y trabaja en el extranjero durante tu año sabático.", None),
    ("Estudiar-y-Trabajar-en-Australia", "Gap Year / Estudia y Trabaja", "Omgde6Ko8TGKYMtiUb1x",
     "Estudia y trabaja en Australia durante tu Gap Year.", None),
    # Huérfanos §F (D7 · slugs lowercase-hyphen de §F, no bloqueantes)
    ("gap-year-agendar", "Gap Year / Estudia y Trabaja", "Omgde6Ko8TGKYMtiUb1x",
     "Vive tu Gap Year con propósito en el extranjero.", None),
    ("viajes-educativos-agendar", "Viajes educativos", "j0jcAdaieJXaoPZBempp",
     "Viajes educativos con propósito para ampliar horizontes.", None),
    ("educacion-superior-agendar", "Educación superior", "RUjWx74NPK77FPUcs5ME",
     "Estudios universitarios y de posgrado en el extranjero.", None),
    ("cursos-idiomas-agendar", "Cursos de idiomas en el extranjero", "5PxslDhdQxZeDcKmLYNq",
     "Aprende un idioma con inmersión total en el extranjero.", None),
]

TEMPLATE = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Agenda tu asesoría gratuita · {programa_h} · Venttur</title>
<meta name="description" content="Agenda una asesoría gratuita con Venttur para el programa de {programa_h}.">
<meta name="robots" content="index,follow">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/intl-tel-input@18.1.1/build/css/intlTelInput.css">
<style>
  :root{{ --navy:#0d1b40; --navy2:#16265a; --accent:#c9a24b; --bg:#f5f7fb; --ok:#1f8a4c; --err:#a94442; }}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
       background:var(--bg);color:#1a1a1a;line-height:1.5;-webkit-font-smoothing:antialiased}}
  .hero{{background:linear-gradient(160deg,var(--navy) 0%,var(--navy2) 100%);color:#fff;padding:28px 16px 40px;text-align:center}}
  .hero img{{width:180px;max-width:60%;margin:0 auto 18px;display:block}}
  .hero h1{{font-size:1.55rem;font-weight:700;max-width:640px;margin:0 auto 10px;line-height:1.3}}
  .hero p{{font-size:1rem;opacity:.9;max-width:560px;margin:0 auto}}
  .wrap{{max-width:640px;margin:-24px auto 0;padding:0 16px 48px}}
  .card{{background:#fff;border-radius:16px;box-shadow:0 8px 30px rgba(13,27,64,.12);padding:24px 20px;margin-bottom:20px}}
  .card h2{{color:var(--navy);font-size:1.15rem;margin-bottom:4px}}
  .card .step{{display:inline-block;background:var(--accent);color:#fff;font-size:.75rem;font-weight:700;
              border-radius:999px;padding:3px 10px;margin-bottom:12px;letter-spacing:.3px}}
  label{{display:block;font-size:.85rem;font-weight:600;color:var(--navy);margin:14px 0 5px}}
  input[type=text],input[type=email],input[type=tel]{{width:100%;padding:12px 14px;border:1.5px solid #d7deea;
    border-radius:10px;font-size:1rem;transition:border .15s}}
  input:focus{{outline:none;border-color:var(--navy)}}
  .iti{{width:100%}}
  .btn{{width:100%;background:var(--navy);color:#fff;border:none;border-radius:10px;padding:14px;
        font-size:1.05rem;font-weight:700;margin-top:20px;cursor:pointer;transition:background .15s}}
  .btn:hover{{background:var(--navy2)}}
  .btn:disabled{{opacity:.6;cursor:not-allowed}}
  .msg{{margin-top:12px;font-size:.9rem;text-align:center;display:none}}
  .msg.err{{color:var(--err);display:block}}
  .cal-section{{display:none}}
  .cal-section.show{{display:block;animation:fade .4s ease}}
  @keyframes fade{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
  iframe.cal{{width:100%;min-height:680px;border:none;overflow:hidden}}
  .social{{text-align:center;padding:20px 0 8px}}
  .social a{{display:inline-block;margin:0 8px}}
  .social img{{width:34px;height:34px;opacity:.85}}
  .foot{{text-align:center;font-size:.75rem;color:#8a93a6;padding:8px 16px 24px}}
  .hidden-anchor{{position:relative;top:-70px}}
</style>
</head>
<body>
  <header class="hero">
    <img src="{logo}" alt="Venttur Education &amp; Travel">
    <h1>¡Elige el horario que más te convenga para tu asesoría gratuita!</h1>
    <p>{subtitulo}</p>
  </header>

  <main class="wrap">
    {video_block}
    <section class="card" id="formCard">
      <span class="step">Paso 1 de 2</span>
      <h2>Déjanos tus datos</h2>
      <form id="leadForm" novalidate>
        <label for="nombre">Nombre</label>
        <input type="text" id="nombre" name="nombre" autocomplete="given-name" required>
        <label for="apellidos">Apellidos</label>
        <input type="text" id="apellidos" name="apellidos" autocomplete="family-name" required>
        <label for="telefono">WhatsApp</label>
        <input type="tel" id="telefono" name="telefono" autocomplete="tel" required>
        <label for="email">Correo electrónico</label>
        <input type="email" id="email" name="email" autocomplete="email" required>
        <button class="btn" type="submit" id="submitBtn">Continuar al calendario →</button>
        <div class="msg" id="msg"></div>
      </form>
    </section>

    <div class="hidden-anchor" id="calAnchor"></div>
    <section class="card cal-section" id="calCard">
      <span class="step">Paso 2 de 2</span>
      <h2>Reserva tu horario</h2>
      <p style="font-size:.9rem;color:#5a6478;margin-bottom:14px">Elige el día y la hora que mejor te queden para tu asesoría gratuita.</p>
      <iframe class="cal" src="{cal_base}{calendar_id}" scrolling="no" id="{calendar_id}_booking"></iframe>
    </section>

    <div class="social">
      {social}
    </div>
    <p class="foot">© Venttur Education &amp; Travel · Programa: {programa_h}</p>
  </main>

  <script src="https://cdn.jsdelivr.net/npm/intl-tel-input@18.1.1/build/js/intlTelInput.min.js"></script>
  <script src="https://link.msgsndr.com/js/form_embed.js" type="text/javascript"></script>
  <script>
    var PROGRAMA = {programa_js};
    var W4 = "{w4}";
    var CAPI = "{capi}";

    // Teléfono internacional (default MX)
    var telInput = document.querySelector("#telefono");
    var iti = window.intlTelInput(telInput, {{
      initialCountry: "mx",
      preferredCountries: ["mx","us"],
      utilsScript: "https://cdn.jsdelivr.net/npm/intl-tel-input@18.1.1/build/js/utils.js"
    }});

    // Helpers de atribución / tracking
    // Los redirects de GHL pegan el query entrante con un segundo "?" (…?atribuida_a=x?fbclid=y, verificado 22/9):
    // se normaliza a "&" antes de leerlo o reenviarlo, si no la atribución queda "x?fbclid=y".
    var QS = location.search.replace(/\?/g, function(m, i){{ return i ? "&" : m; }});
    function qp(name){{ return new URLSearchParams(QS).get(name) || ""; }}
    function cookie(name){{ var m=document.cookie.match('(^|;)\\s*'+name+'\\s*=\\s*([^;]+)'); return m?m.pop():""; }}
    function genFolio(){{ return "F-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2,8); }}

    var ATRIBUIDA = qp("atribuida_a");
    var FBCLID = qp("fbclid");
    var FOLIO = genFolio();

    // Calendario: reenviar el query de la landing al widget (atribución robusta fuera de GHL) y,
    // al enviar el form, prellenar nombre/apellido/email/teléfono para que el lead no retipee.
    var calF = document.getElementById("{calendar_id}_booking");
    var CALBASE = calF.getAttribute("src");
    if (QS) calF.src = CALBASE + QS;

    var form = document.getElementById("leadForm");
    var btn = document.getElementById("submitBtn");
    var msg = document.getElementById("msg");

    function showErr(t){{ msg.className="msg err"; msg.textContent=t; }}

    form.addEventListener("submit", async function(e){{
      e.preventDefault();
      msg.style.display="none";
      var nombre=document.getElementById("nombre").value.trim();
      var apellidos=document.getElementById("apellidos").value.trim();
      var email=document.getElementById("email").value.trim();
      var telefono = iti.getNumber(); // E.164 con +
      if(!nombre || !apellidos || !telefono || !email){{ showErr("Completa todos los campos, por favor."); return; }}
      if(!iti.isValidNumber()){{ showErr("Revisa el número de WhatsApp."); return; }}

      btn.disabled=true; btn.textContent="Guardando…";

      var w4Body = {{
        nombre: nombre, apellidos: apellidos, telefono: telefono, email: email,
        programa: PROGRAMA, folio: FOLIO, atribuida_a: ATRIBUIDA,
        fbclid_completo: FBCLID, fbp: cookie("_fbp"), url: location.href
      }};
      var capiBody = {{
        folio: FOLIO, programa: PROGRAMA, fbclid_completo: FBCLID,
        fbp: cookie("_fbp"), url: location.href, timestamp: Date.now()
      }};

      // Fire-and-forget ambos; no bloquear al lead si uno falla
      try {{
        await Promise.allSettled([
          fetch(W4, {{method:"POST", headers:{{"Content-Type":"application/json"}}, body:JSON.stringify(w4Body)}}),
          fetch(CAPI, {{method:"POST", headers:{{"Content-Type":"application/json"}}, body:JSON.stringify(capiBody)}})
        ]);
      }} catch(err) {{ /* seguir igual: el calendario es la conversión real */ }}

      // Prefill del widget GHL con los datos del form (+ query original: atribuida_a, fbclid, utm)
      var pre = new URLSearchParams(QS);
      pre.set("first_name", nombre); pre.set("last_name", apellidos);
      pre.set("email", email); pre.set("phone", telefono);
      calF.src = CALBASE + "?" + pre.toString();

      // Revelar calendario + scroll
      document.getElementById("calCard").classList.add("show");
      document.getElementById("calAnchor").scrollIntoView({{behavior:"smooth"}});
      btn.textContent="✓ Datos guardados";
    }});
  </script>
</body>
</html>
"""


def build(slug, programa, calendar_id, subtitulo, video=None):
    video_block = ""
    if video:
        video_block = (
            '<section class="card"><span class="step">Mira esto primero</span>'
            '<div style="position:relative;padding-top:56.25%">'
            f'<iframe src="{video}" loading="lazy" '
            'style="position:absolute;top:0;left:0;width:100%;height:100%;border:none;border-radius:10px" '
            'allow="accelerometer;gyroscope;autoplay;encrypted-media;picture-in-picture" '
            'allowfullscreen></iframe></div></section>'
        )
    return TEMPLATE.format(
        programa_h=html.escape(programa),
        programa_js='"' + programa.replace('"', '\\"') + '"',
        subtitulo=html.escape(subtitulo),
        logo=LOGO, social=icono("whatsapp", WA, "WhatsApp") + icono("instagram", IG, "Instagram"),
        cal_base=CAL_BASE, calendar_id=calendar_id,
        w4=W4_WEBHOOK, capi=CAPI_WEBHOOK,
        video_block=video_block,
    )


if __name__ == "__main__":
    # limpiar output previo (evita dejar slugs viejos renombrados)
    for old in OUT.glob("*.html"):
        old.unlink()
    for slug, programa, cal, sub, video in LANDINGS:
        out = OUT / f"{slug}.html"
        out.write_text(build(slug, programa, cal, sub, video), encoding="utf-8")
        print(f"  ✓ {slug}.html  ({programa}){'  + video' if video else ''}")
    print(f"\n{len(LANDINGS)} landings en {OUT}")
