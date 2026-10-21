"""Paso 4 (24/9) · System prompt del agente: voseo → tuteo mexicano (los leads de Venttur son de México).
Marca: TUTEO-0924. Las secciones que escribió la agencia (estado del lead, reglas duras, precio, situaciones) estaban
en voseo, y varios ejemplos entre comillas los copia el bot casi textual ("Vos elegís día y hora…").

Primero frases (donde el cambio depende del contexto), después palabras sueltas con borde de palabra.
Toda sustitución tiene que encontrar al menos una ocurrencia; al final se re-escanea y no puede quedar voseo."""
import re

MARK = "Tú eliges día y hora"   # frase única que sólo existe después del paso 4 (TUTEO-0924)

FRASES = [
    ("sos vos\nquien lo re-envía", "eres tú\nquien lo reenvía"),
    ("coordinar la cita vos por chat", "coordinar la cita tú por chat"),
    ("Vos NO tenés herramienta", "Tú NO tienes herramienta"),
    ("> Vos: *", "> Tú: *"),
    ("Vos elegís día y hora", "Tú eliges día y hora"),
    ("Elegís el día y hora", "Eliges el día y hora"),
    ("re-enviá", "reenvía"),
    ("(elegí UNA)", "(elige UNA)"),
    ("saltealo y andá directo", "sáltalo y ve directo"),
    ("contá\n   los signos", "cuenta\n   los signos"),
    ("Variálas", "Varíalas"),
]

PALABRAS = {
    "leelo": "léelo", "actuá": "actúa", "sabés": "sabes", "tenés": "tienes", "Usalos": "Úsalos", "usalos": "úsalos",
    "reconocé": "reconoce", "Reconocé": "Reconoce", "preguntá": "pregunta", "Respondé": "Responde",
    "respondé": "responde", "recibís": "recibes", "validás": "validas", "aportás": "aportas", "repetís": "repites",
    "prometés": "prometes", "inventás": "inventas", "podés": "puedes", "seguís": "sigues", "hacés": "haces",
    "releé": "relee", "reescribí": "reescribe", "Reescribilo": "Reescríbelo", "conectá": "conecta",
    "decime": "dime", "Redirigilo": "Redirígelo", "redirigilo": "redirígelo", "mirá": "mira", "saludá": "saluda",
    "seguí": "sigue", "Seguí": "Sigue", "pedilo": "pídelo", "esperá": "espera", "Ajustá": "Ajusta",
    "dejalo": "déjalo", "reconocelo": "reconócelo", "activá": "activa", "dejá": "deja", "desglosalo": "desglósalo",
    "Confirmá": "Confirma", "confirmá": "confirma", "decilo": "dilo", "devolvé": "devuelve", "conversá": "conversa",
    "Validá": "Valida", "ofrecé": "ofrece",
}

# re-escaneo: formas de voseo que no pueden quedar
VOSEO = re.compile(r"\b(vos|Vos|sos|tenés|podés|sabés|querés|hacés|elegís|decime|contame)\b"
                   r"|\b\w+(?:á|é)(?=[\s,.:;!?)\"'*])"
                   r"|\b\w+(?:ás|és|ís)\b")
PERMITIDAS = {"está", "Está", "más", "sé", "qué", "Qué", "será", "además", "después", "Después", "inglés", "Andrés",
              "través", "país", "estás", "podrás", "jamás", "quizás", "demás", "atrás", "detrás", "interés", "francés",
              "papás", "mamá", "papá", "Canadá", "allá", "acá", "estés", "esté", "podrá", "verá", "dará", "tendrá",
              "irá", "hará", "ayudará", "llegará", "estará", "sabrá", "confiará", "asesorará", "terminé", "Dale",
              "detrás", "cortés", "Perú", "mamás", "alemán", "Malta", "según", "así", "Así", "aquí", "allí", "ahí",
              "Estás", "aprenderás", "permitirá", "atenderá", "escribirá", "contactará", "comunicará", "enviará",
              "estaré", "podré", "pondré", "tendrás", "quedará", "llegarán", "atenderán"}   # tuteo presente / futuro, no voseo


def restos(text):
    return sorted({m.group(0) for m in VOSEO.finditer(text)} - PERMITIDAS)


def apply(text):
    if MARK in text:
        raise RuntimeError("ya aplicado")
    llaves = text.count("{{")
    for old, new in FRASES:
        if old not in text:
            raise ValueError(f"frase no encontrada: {old!r}")
        text = text.replace(old, new)
    for old, new in PALABRAS.items():
        rx = re.compile(r"(?<![\w-])" + re.escape(old) + r"(?![\w])")
        text, n = rx.subn(new, text)
        if n == 0:
            raise ValueError(f"palabra no encontrada: {old!r}")
    if text.count("{{") != llaves:
        raise ValueError("cambió la cantidad de {{ }}")
    r = restos(text)
    if r:
        raise ValueError(f"queda voseo: {r}")
    return text
