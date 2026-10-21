"""
Las 5 páginas del programa de referenciadoras (antes en Clientify), rehechas para GHL el 23/9.

Fuente: backup-clientify-2026-09/04-landings/html/{PMR,graciasafil,agendarPMR,CapacitacionRef,seguimientoref}.html
y la configuración pública de los 3 calendarios de Clientify (backup-clientify-2026-09/05-calendarios/referenciadoras/).
Mismo contenido y orden que el original, con la marca de las demás landings. Sólo se corrigieron erratas evidentes
("guias", "de llevamos", "Experiancias") y el link de TikTok, que en el original no era una URL válida.

- PMR: el formulario de Clientify (superform 169777: nombre, apellidos, email, teléfono, país, ciudad) se reemplazó
  por el formulario nativo de GHL `form-referenciadoras-pmr`. El botón de PayPal se conserva tal cual.
- agendarPMR / CapacitacionRef / seguimientoref: calendario nuevo de GHL (uno por página), embebido igual que las
  landings de calendario (el query string pasa al calendario, así se conserva `atribuida_a`).
"""
import html as H
from urllib.parse import quote

from _marca_landings import LOGO, icono

HERO_FOTO = "https://assets.cdn.filesafe.space/7aXb4JCKsWV5nUyBXeSF/media/b7902a36-7708-484b-85f1-38cdeef7f3fa.jpg"
FORM_PMR = "OOti4mdEUsW79AOIob6r"   # form-referenciadoras-pmr (GHL)
PAYPAL = "https://www.paypal.com/ncp/payment/M3VWZ9E8BC2BG"
WA = "https://api.whatsapp.com/send/?phone=%2B523319442476&text&type=phone_number&app_absent=0"
WA_CTA = "https://wa.me/523319442476/?text=" + quote("¡Hola, quiero conocer más acerca de sus programas! ✈️📚")
IG = "https://www.instagram.com/venttur_/"
FB = "https://facebook.com/Venttur.Ed"
TT = "https://www.tiktok.com/@venttur_"

CALENDARIOS = {  # slug → (id del calendario GHL, nombre legible)
    "agendarPMR": ("POT8dw9E68OnaCRSgplA", "Plática sobre el programa de referencias"),
    "CapacitacionRef": ("W1o9YsO8QdwzG4IBucOF", "Capacitación inicial para nuevas aventureras"),
    "seguimientoref": ("muGHmcmYz1pPqX5DGkJU", "Sesión 1 a 1 con Mauricio"),
}

EXTRA_CSS = (
    "<style>"
    ".hero.foto{background:linear-gradient(rgba(13,27,64,.35),rgba(13,27,64,.55)),url('" + HERO_FOTO + "') center/cover}"
    ".hero .lead{font-size:1.05rem;opacity:.95;max-width:600px;margin:10px auto 0;font-style:italic}"
    ".cta{display:inline-block;background:#8fb3b0;color:var(--navy);text-decoration:none;border-radius:40px;"
    "padding:14px 30px;font-size:1.1rem;font-weight:700;margin-top:22px}"
    ".cta.navy{background:var(--navy);color:#fff}"
    ".pp{margin-top:18px}"
    ".txt h2{font-size:1.25rem;color:var(--navy);margin:0 0 12px;line-height:1.3}"
    ".txt p,.txt li{font-size:.98rem;color:#333;margin-bottom:10px}.txt ul{padding-left:20px}"
    ".grid{display:grid;grid-template-columns:1fr;gap:12px}"
    "@media(min-width:600px){.grid{grid-template-columns:1fr 1fr}.grid.t3{grid-template-columns:1fr 1fr 1fr}}"
    ".item{background:var(--bg);border-radius:12px;padding:14px}.item b{display:block;color:var(--navy);margin-bottom:4px}"
    ".item p{margin:0;font-size:.93rem}"
    ".faq b{display:block;color:var(--navy);margin-top:12px}.faq p{margin:4px 0 0}"
    ".centro{text-align:center}"
    "iframe.form{width:100%;min-height:640px;border:none}"
    ".foot small{display:block;margin-top:2px}"
    "</style>"
)

PAYPAL_HTML = (
    '<div class="pp"><style>.pp-M3VWZ9E8BC2BG{text-align:center;border:none;border-radius:1.5rem;min-width:11.625rem;'
    'padding:0 2rem;height:2.625rem;font-weight:bold;background-color:#FFD140;color:#000000;font-family:"Helvetica Neue",'
    'Arial,sans-serif;font-size:1rem;line-height:1.25rem;cursor:pointer;}</style>'
    f'<form action="{PAYPAL}" method="post" target="_top" '
    'style="display:inline-grid;justify-items:center;align-content:start;gap:0.5rem;">'
    '<input class="pp-M3VWZ9E8BC2BG" type="submit" value="Comprar ahora" />'
    '<img src="https://www.paypalobjects.com/images/Debit_Credit_APM.svg" alt="cards" />'
    '<section style="color:#fff;font-size:.85rem">Con la tecnología de <img src="https://www.paypalobjects.com/paypal-ui/logos/svg/paypal-wordmark-color.svg" '
    'alt="paypal" style="height:0.875rem;vertical-align:middle;" /></section></form></div>'
)


def _doc(title, desc, styles, body):
    return (f"<!DOCTYPE html><html><head><title>{H.escape(title)}</title>"
            f'<meta name="description" content="{H.escape(desc)}">'
            f"{styles}{EXTRA_CSS}</head><body>{body}</body></html>")


def _social(*redes):
    m = {"facebook": (FB, "Facebook"), "whatsapp": (WA, "WhatsApp"), "instagram": (IG, "Instagram"), "tiktok": (TT, "TikTok")}
    return '<div class="social">' + "".join(icono(r, m[r][0], m[r][1]) for r in redes) + "</div>"


FOOT = ('<p class="foot">© Venttur Education &amp; Travel · Todos los derechos reservados'
        '<small>Viajes y Experiencias GARDE S de RL de CV</small></p>')


def _qs_script(el_id):
    # conserva el query entrante (atribuida_a, fbclid, utm) en el iframe, igual que las landings de calendario
    return ('<script>(function(){var f=document.getElementById("' + el_id + '");'
            'var q=location.search.replace(/\\?/g,function(m,i){return i?"&":m;});'
            'if(q)f.src=f.getAttribute("src")+q;})();</script>')


def pmr(styles):
    sabemos = [
        "Muchas veces, como mamá, buscas aprovechar tu tiempo y habilidades sin descuidar a tu familia, pero encontrar algo que encaje no siempre es fácil.",
        "Eres esa persona a la que confían para pedir recomendaciones: el restaurante perfecto, el regalo ideal. Tu opinión influye más de lo que imaginas.",
        "Has trabajado duro para construir un círculo de confianza y un estilo de vida que valoras, pero sabes que siempre es posible buscar nuevas formas de crecer.",
        "Te gustaría tener una actividad que complemente tu día a día, que sea flexible y no comprometa lo que ya haces por tu familia.",
    ]
    madres = [
        ("Tengan liderazgo natural:", "Eres esa mamá que otros buscan para organizar eventos, dar recomendaciones o simplemente pedir consejo."),
        ("Sean activas socialmente:", "Participas en la escuela de tus hijos, en clubes deportivos o eventos sociales, y conoces a otras familias que confían en ti."),
        ("Valoren la educación y las experiencias premium:", "Sabes que una buena educación abre puertas y entiendes la importancia de invertir en el futuro."),
        ("Cuenten con un estilo de vida socialmente activo:", "Participas en círculos donde se habla de viajes, clubes, educación y experiencias internacionales."),
    ]
    harias = [
        ("Escucha y comparte", "Conecta con otras familias y cuéntales cómo Venttur puede ayudarles a transformar la vida de sus hijos."),
        ("Agenda una reunión", "Cuando alguien muestre interés, coordina una cita con nuestro equipo de consultores expertos. Nosotros nos encargamos del resto."),
        ("Gana recompensas", "Por cada familia que se convierta en cliente, recibirás una comisión significativa que complementará tu ingreso actual."),
    ]
    accede = [
        ("Ingresos adicionales", "Esquema de comisiones atractivo, que puede llegar a generarte hasta $40,000 MXN por cada estudiante inscrito."),
        ("Material y soporte", "Desde guías hasta estrategias de comunicación, te llevamos de la mano para que puedas iniciar a referenciar."),
        ("Capacitaciones", "Aprende a usar tus habilidades naturales y todo lo que necesitas acerca de los internados en el extranjero."),
        ("Flexibilidad total", "Trabaja desde casa a tu ritmo y sin sacrificar tu estilo de vida."),
    ]
    faq = [
        ("¿Cómo puedo saber si este programa de referenciación es adecuado para mí?",
         "Si estás buscando una oportunidad que te permita crecer tanto personal como profesionalmente, manteniendo un equilibrio con tu vida familiar, nuestro programa podría ser ideal para ti. Es especialmente apropiado para quienes tienen una red interesada en la educación internacional y desean hacer un impacto significativo en sus comunidades."),
        ("¿Qué tipo de apoyo y formación ofrece Venttur para los nuevos afiliados?",
         "En Venttur, estamos comprometidos con tu éxito. Ofrecemos formación integral sobre nuestro sistema de perfilamiento estudiantil, además de estrategias efectivas de comunicación y marketing. Nuestro equipo de soporte está siempre disponible para guiarte en cada paso del camino."),
        ("¿Cuál es el potencial de ingresos en el programa de referenciación de Venttur?",
         "El potencial de ingresos varía dependiendo de tu dedicación y esfuerzo. Nuestro sistema de comisiones está diseñado para recompensar tus éxitos en la referenciación de manera justa y transparente, reflejando tu contribución al crecimiento de Venttur."),
        ("¿Necesito tener experiencia previa en ventas o marketing para tener éxito en este programa?",
         "No es necesario tener experiencia previa. Valoramos más tu pasión por la educación y tu habilidad para establecer conexiones genuinas. Con nuestra formación y recursos, te equiparemos con todo lo que necesitas para tener éxito."),
        ("¿Hay algún costo inicial para unirme al programa de referenciación de Venttur?",
         "Sí, hay una inversión inicial para unirte al programa, la cual cubre tu formación, acceso a herramientas y soporte continuo. Consideramos esta inversión como un compromiso con tu crecimiento y éxito dentro del programa."),
        ("¿Cuánto tiempo suele tomar ver resultados una vez que me uno al programa de referenciación de Venttur?",
         "En nuestro programa de Venttur, diseñamos el proceso para que puedas empezar rápidamente. Muchos de nuestros afiliados comienzan a agendar citas dentro de los primeros quince días y, con dedicación, es posible empezar a recibir comisiones al cabo de un mes. Además, la inversión inicial que realizas en el programa se puede recuperar, e incluso obtener utilidades, con el cierre de tu primera referencia exitosa. Esto hace que Venttur no solo sea una oportunidad para crecer profesionalmente, sino también una opción financiera viable y gratificante."),
    ]
    items = lambda xs, cls="grid": f'<div class="{cls}">' + "".join(
        f'<div class="item"><b>{H.escape(t)}</b><p>{H.escape(d)}</p></div>' for t, d in xs) + "</div>"
    form_id = f"inline-{FORM_PMR}"
    body = (
        f'<header class="hero foto"><img src="{LOGO}" alt="Venttur Education &amp; Travel">'
        '<h1>¿Eres esa mamá a la que otras acuden para recibir recomendaciones confiables y valiosas?</h1>'
        '<p class="lead">Recomienda experiencias educativas premium en el extranjero, ayuda a familias y genera ingresos de forma sencilla y flexible.</p>'
        f'<a class="cta" href="{H.escape(WA_CTA)}" target="_blank" rel="noopener">Platicar con un asesor</a>'
        f'{PAYPAL_HTML}</header>'
        '<main class="wrap">'
        '<section class="card txt"><h2>Sabemos que…</h2><ul>' + "".join(f"<li>{H.escape(x)}</li>" for x in sabemos) + '</ul>'
        '<p>Si esto te suena familiar, <b>Venttur podría ser exactamente lo que estás buscando.</b></p>'
        '<p>En Venttur ayudamos a familias a encontrar internados internacionales premium: escuelas privadas en el extranjero donde estudiantes de secundaria y preparatoria viven, estudian y crecen. Estas experiencias únicas no solo transforman su educación, sino que los preparan para un futuro brillante.</p>'
        '<p>Estamos buscando madres como tú, que puedan ayudarnos a conectar a más familias con estas oportunidades excepcionales.</p></section>'
        '<section class="card txt"><h2>Estamos buscando madres que…</h2><ul>' +
        "".join(f"<li><b>{H.escape(a)}</b> {H.escape(b)}</li>" for a, b in madres) + '</ul>'
        '<p class="centro"><b>Si estas características te describen, ¡queremos conocerte!</b></p></section>'
        '<section class="card txt"><h2>¿Qué harías como referenciadora?</h2>' + items(harias, "grid t3") + '</section>'
        '<section class="card txt"><h2>Únete sin costo y accede a:</h2>' + items(accede) +
        '<p class="centro" style="margin-top:14px"><b>Y lo mejor: no necesitas experiencia previa ni inversión inicial</b></p>'
        '<p class="centro"><a class="cta navy" href="#salto">Platicar con un asesor</a></p></section>'
        '<section class="card txt"><p><i>“En Venttur, buscamos personas comprometidas y motivadas, listas para explorar nuevas oportunidades y crecer. Pero entendemos que nuestro programa no es para todos. A continuación, te ayudaremos a determinar si este camino se alinea con tus metas y estilo de vida.”</i></p>'
        '<h2>Preguntas frecuentes</h2><div class="faq">' +
        "".join(f"<b>{H.escape(q)}</b><p>{H.escape(a)}</p>" for q, a in faq) + '</div></section>'
        '<section class="card" id="salto">'
        f'<iframe class="form" src="https://api.leadconnectorhq.com/widget/form/{FORM_PMR}" id="{form_id}" '
        "data-layout=\"{'id':'INLINE'}\" data-trigger-type=\"alwaysShow\" data-trigger-value=\"\" "
        'data-activation-type="alwaysActivated" data-activation-value="" data-deactivation-type="neverDeactivate" '
        f'data-deactivation-value="" data-form-name="form-referenciadoras-pmr" data-height="640" '
        f'data-layout-iframe-id="{form_id}" data-form-id="{FORM_PMR}" title="Platicar con un asesor"></iframe>'
        f'{_qs_script(form_id)}<script src="https://link.msgsndr.com/js/form_embed.js" type="text/javascript"></script></section>'
        + _social("facebook", "whatsapp", "instagram", "tiktok") + FOOT + '</main>')
    return _doc("Programa de referenciadoras · Venttur",
                "Recomienda experiencias educativas premium en el extranjero, ayuda a familias y genera ingresos de forma sencilla y flexible.",
                styles, body)


def graciasafil(styles):
    body = (
        f'<header class="hero foto"><img src="{LOGO}" alt="Venttur Education &amp; Travel">'
        '<h1>¡Gracias por dar el primer paso!</h1></header>'
        '<main class="wrap"><section class="card txt">'
        '<p>¡Estamos emocionados de verte aquí! Tu interés en el programa de referenciación de Venttur es el comienzo de algo grande. Queremos agradecerte por dar este importante paso hacia un futuro lleno de oportunidades y crecimiento.</p>'
        '<p>Un miembro de nuestro equipo de asesores se comunicará contigo en breve a través de WhatsApp. Estará listo para responder todas tus preguntas y guiarte en los próximos pasos de tu viaje con Venttur. ¡Prepárate para una conversación enriquecedora y llena de ideas!</p>'
        '<p>Estamos aquí para apoyarte en cada paso. ¡Hablemos pronto!</p>'
        '<p><b>Con cariño,<br>el equipo de Venttur</b></p></section>'
        + _social("facebook", "whatsapp", "instagram", "tiktok") + FOOT + '</main>')
    return _doc("¡Gracias por dar el primer paso! · Venttur",
                "Gracias por tu interés en el programa de referenciación de Venttur.", styles, body)


def calendario(slug, styles):
    cal_id, nombre = CALENDARIOS[slug]
    el = f"{cal_id}_ref"
    body = (
        f'<header class="hero"><img src="{LOGO}" alt="Venttur Education &amp; Travel">'
        '<h1>¡Elige el horario que más te convenga para nuestra reunión!</h1>'
        f'<p>{H.escape(nombre)} · ¡Nos vemos pronto!</p></header>'
        '<main class="wrap"><section class="card">'
        f'<iframe class="cal" src="https://api.leadconnectorhq.com/widget/booking/{cal_id}" allow="payment" scrolling="no" id="{el}"></iframe><br>'
        f'{_qs_script(el)}<script src="https://link.msgsndr.com/js/form_embed.js" type="text/javascript"></script></section>'
        + _social("whatsapp", "instagram") + FOOT + '</main>')
    return _doc(f"Agenda · {nombre} · Venttur", f"Agenda tu reunión con Venttur: {nombre}.", styles, body)


def paginas(styles):
    """slug → HTML completo de las 5 páginas."""
    out = {"PMR": pmr(styles), "graciasafil": graciasafil(styles)}
    for slug in CALENDARIOS:
        out[slug] = calendario(slug, styles)
    return out
