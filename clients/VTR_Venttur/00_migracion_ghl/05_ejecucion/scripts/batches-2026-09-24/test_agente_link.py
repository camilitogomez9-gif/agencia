#!/usr/bin/env python3
"""Prueba offline del agente VTR (gpt-4o, temperatura 0, igual que el nodo `OpenAI Chat Model`) para los casos de
link/cita. Arma el mensaje de usuario igual que el main: `[ESTADO DEL LEAD]\\n<estado>\\n\\nMensaje del usuario: …\\n\\n
Fecha de hoy: …`, con la historia previa como turnos (la memoria de n8n guarda el input completo).

No toca n8n, GHL ni WhatsApp: sólo llama a OpenAI.

Uso: python3 test_agente_link.py --prompt <archivo systemMessage> [--estado viejo|nuevo] [--elevar vivo|v2.4] [--reps N]\n     (--prompt acepta el .txt descargado del Google Doc: Archivo → Descargar → Texto sin formato)
"""
import argparse, json, re, sys, time, urllib.error, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from prompt_paso4 import restos as restos_voseo

ROOT = Path("/Users/camilo/Downloads/camilo-workspace")
KEY = next(l.split("=", 1)[1].strip() for l in open(ROOT / ".env") if l.startswith("OPENAI_API_KEY="))
FECHA = "Thursday 24 of September of 2026 11:30AM"

BASE = ("Nombre: {nom} (ya lo sabes, no se lo vuelvas a preguntar)\nPrograma de interes: {prog}\nOrigen: DESCONOCIDO\n")
EST = {
    # Mauricio: flag agendan_cita=true importado, cero citas en GHL
    "mauricio": {
        "viejo": BASE.format(nom="Mauricio Garcia", prog="Internados") +
                 "Link de agenda: YA ENVIADO\nCita: AGENDADA (no le vuelvas a mandar el link)\nConversacion: Cita confirmada",
        "nuevo": BASE.format(nom="Mauricio Garcia", prog="Internados") +
                 "Link de agenda: YA ENVIADO\nCita: el CRM la marca como agendada, pero no tenemos la fecha registrada "
                 "(puede ser una cita anterior). No le ofrezcas el link por tu cuenta, pero si pide agendar, reagendar o "
                 "dice que su cita ya paso, mándale el link de su programa en ese mismo mensaje.\n"
                 "Conversacion: Cita confirmada (sin fecha registrada)"},
    # Daiana: cita real futura en GHL
    "daiana": {
        "viejo": BASE.format(nom="Daiana Oyuela", prog="Campamentos de verano") +
                 "Link de agenda: YA ENVIADO\nCita: AGENDADA (no le vuelvas a mandar el link)\nConversacion: Cita confirmada",
        "nuevo": BASE.format(nom="Daiana Oyuela", prog="Campamentos de verano") +
                 "Link de agenda: YA ENVIADO\nCita: AGENDADA para el viernes 25 de septiembre, 9:45 a. m. (hora de CDMX) · "
                 "Campamentos. No vuelvas a venderle la asesoria. Si pide cambiarla o reagendarla, mándale el link de su "
                 "programa para que elija otro horario.\nConversacion: Cita confirmada"},
    # Daiana con la cita ya pasada
    "pasada": {
        "viejo": BASE.format(nom="Daiana Oyuela", prog="Campamentos de verano") +
                 "Link de agenda: YA ENVIADO\nCita: AGENDADA (no le vuelvas a mandar el link)\nConversacion: Cita confirmada",
        "nuevo": BASE.format(nom="Daiana Oyuela", prog="Campamentos de verano") +
                 "Link de agenda: YA ENVIADO y NO tiene una cita vigente\nCita: NO tiene una cita vigente. Tuvo una el "
                 "martes 22 de septiembre, 9:45 a. m. (hora de CDMX) y ya paso. Si quiere otra o pregunta por agendar, "
                 "mándale el link de su programa.\nConversacion: Cita confirmada (de una cita anterior, hoy no tiene una vigente)"},
    # Viri: link enviado, sin cita
    "viri": {
        "viejo": BASE.format(nom="Viri Salgado", prog="Internados") + "Link de agenda: YA ENVIADO\nConversacion: Contestó",
        "nuevo": BASE.format(nom="Viri Salgado", prog="Internados") +
                 "Link de agenda: YA ENVIADO y NO agendó todavía\nCita: sin agendar\nConversacion: Contestó"},
    "nuevo": {"viejo": "Lead nuevo: no tenemos nada de esta persona todavia.",
              "nuevo": "Lead nuevo: no tenemos nada de esta persona todavia."},
}

LINK = re.compile(r"vtr\.[TU-DOMINIO]/\S+|promo\.venttur\.com/\S+", re.I)
CORREO = re.compile(r"correo|e-?mail|recordatorio", re.I)
FECHA_CITA = re.compile(r"viernes|25 de septiembre|9:45", re.I)

# (id, estado, [mensajes del lead], esperado por turno: 'link' | 'nolink' | None) + chequeos extra
CASOS = [
    ("M1 Mauricio: hola → quiero agendar nuevamente", "mauricio", ["Hola", "Quiero agendar nuevamente"], [None, "link"]),
    ("M2 Mauricio: ¿cuándo es mi cita?", "mauricio", ["Según tú cuando está agendada mi cita?"], ["nocorreo"]),
    ("M3 Mauricio: ya pasó, quiero otra", "mauricio", ["Ya pasó la fecha quiero volver a agendar una nueva"], ["link"]),
    ("D1 Daiana (cita futura): ¿cuándo es?", "daiana", ["Hola, me recuerdas cuándo es mi cita?"], ["fecha+nolink"]),
    ("D2 Daiana (cita futura): cambiarla", "daiana", ["Necesito cambiar mi cita, ese día no puedo"], ["link"]),
    ("D3 Daiana (cita futura): gracias", "daiana", ["Muchas gracias!"], ["nolink"]),
    ("P1 cita pasada: quiero otra", "pasada", ["No pude conectarme a la llamada, quiero otra"], ["link"]),
    ("V1 link sin cita: propone horario", "viri", ["¿El lunes a las 11 podemos hablar?"], ["link"]),
    ("R1 precio: rango + propuesta de día", "viri", ["¿Cuánto cuesta un internado más o menos?"], ["precio"]),
    ("R2 moneda: confirma pesos o dólares", "viri", ["Tengo 250 mil de presupuesto, ¿me alcanza?"], ["moneda"]),
    ("R3 una sola pregunta por mensaje", "nuevo", ["Hola, me interesa un intercambio para mi hija"], ["unapregunta"]),
    ("S1 cita futura: comprobante de pago → asesor", "daiana",
     ["Ya hice el pago de la inscripción, ¿a quién le mando el comprobante?"], ["elevar"]),
    ("S2 link no abre → lo reenvía", "viri", ["No me abre el link que me mandaste"], ["link"]),
    ("S3 contacto viejo saluda → ofrece ayuda", "mauricio", ["Hola"], ["resuelve"]),
    ("S4 cita futura: cambio de programa", "daiana",
     ["Necesito cambiar el campamento que elegí por otro de otra fecha, ¿cómo le hago?"], ["resuelve"]),
    ("N1 lead nuevo: no manda link de entrada", "nuevo",
     ["Hola! Quiero agendar una asesoría para encontrar el internado ideal de mi hijo"], ["nolink"]),
]

ELEVAR = {
    "vivo": "Deriva la conversacion a un humano. Activala SOLO cuando el lead pida hablar con una persona, tenga una "
            "emergencia, o repita el MISMO mensaje 2+ veces consecutivas. Pausa el bot para ese contacto, lo asigna a "
            "Mauricio (direccion) y avisa al equipo por Telegram.",
    "v2.4": "Deriva la conversacion a un asesor humano. Activala cuando el lead pida hablar con una persona, tenga una "
            "emergencia, necesite algo que solo un asesor puede hacer (pagos o comprobantes, documentos, cambios en su "
            "tramite), o repita el MISMO mensaje 2+ veces consecutivas. Si le dices al lead que un asesor lo va a "
            "atender, tienes que activarla en ese mismo turno. Pausa el bot para ese contacto, lo asigna a Mauricio "
            "(direccion) y avisa al equipo por Telegram.",
}

TOOLS = [{"type": "function", "function": {"name": n, "description": d,
          "parameters": {"type": "object", "properties": props, "required": []}}}
         for n, d, props in [
             ("crear_contacto", "Guarda el nombre del lead en el CRM.", {"nombre": {"type": "string"}, "apellido": {"type": "string"}}),
             ("elevar", "(se completa en main según --elevar)", {"resumen": {"type": "string"}}),
             ("cerrar_conversacion", "Marca la conversacion como Cerrada.", {}),
         ]]


def chat(messages):
    body = {"model": "gpt-4o", "temperature": 0, "messages": messages, "tools": TOOLS}
    req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    for intento in range(12):   # la cuenta tiene un TPM bajo: 429 → esperar y reintentar
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)["choices"][0]["message"]
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            espera = float(e.headers.get("retry-after") or 0) or 15
            time.sleep(min(max(espera, 5), 60))
    raise RuntimeError("OpenAI 429 persistente")


TOOLS_LLAMADAS = []


def turno(system, hist, estado, msg):
    user = f"[ESTADO DEL LEAD]\n{estado}\n\nMensaje del usuario: {msg}\n\nFecha de hoy: {FECHA}"
    msgs = [{"role": "system", "content": system}] + hist + [{"role": "user", "content": user}]
    TOOLS_LLAMADAS.clear()
    for _ in range(3):
        m = chat(msgs)
        if m.get("tool_calls"):
            TOOLS_LLAMADAS.extend(tc["function"]["name"] for tc in m["tool_calls"])
            msgs.append(m)
            for tc in m["tool_calls"]:
                msgs.append({"role": "tool", "tool_call_id": tc["id"], "content": '{"ok": true}'})
            continue
        return user, m.get("content") or ""
    return user, ""


def check(exp, out):
    link = bool(LINK.search(out))
    if exp == "link":
        return link
    if exp == "nolink":
        return not link
    if exp == "nocorreo":
        return not CORREO.search(out)
    if exp == "precio":
        return bool(re.search(r"50[,.]?000|130[,.]?000", out)) and bool(re.search(r"hoy o mañana|mañana", out, re.I))
    if exp == "moneda":
        return bool(re.search(r"pesos o d[oó]lares|d[oó]lares o pesos", out, re.I)) and not LINK.search(out)
    if exp == "unapregunta":
        return out.count("?") <= 1
    if exp == "elevar":          # deriva de verdad (tool) y no inventa un canal
        return "elevar" in TOOLS_LLAMADAS and not re.search(r"correo|e-?mail", out, re.I)
    if exp == "resuelve":        # no manda a un correo inventado ni cierra con "no tengo acceso"
        return not re.search(r"correo|e-?mail|no tengo acceso|enlace que te (envié|mandé)", out, re.I)
    if exp == "fecha+nolink":
        return bool(FECHA_CITA.search(out)) and not link
    return True


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--prompt", required=True)
    a.add_argument("--estado", default="nuevo", choices=["viejo", "nuevo"])
    a.add_argument("--reps", type=int, default=1)
    a.add_argument("--solo", default="")
    a.add_argument("--elevar", default="vivo", choices=["vivo", "v2.4"],
                   help="descripción de la tool elevar: la de hoy en n8n o la de la Edición 3 del borrador v2.4")
    args = a.parse_args()
    for t in TOOLS:
        if t["function"]["name"] == "elevar":
            t["function"]["description"] = ELEVAR[args.elevar]
    system = Path(args.prompt).read_text()
    if system.startswith("="):
        system = system[1:]
    tot = ok = 0
    for rep in range(args.reps):
        for cid, est, msgs, exps in CASOS:
            if args.solo and not cid.startswith(args.solo):
                continue
            hist, res = [], []
            for msg, exp in zip(msgs, exps):
                u, out = turno(system, hist, EST[est][args.estado], msg)
                hist += [{"role": "user", "content": u}, {"role": "assistant", "content": out}]
                good = check(exp, out)
                res.append((msg, exp, good, out))
            vos = sorted({w for _, _, _, out in res for w in restos_voseo(out)})
            passed = all(g for _, e, g, _ in res if e) and not vos
            if vos:
                print(f"    ⚠️ voseo en la respuesta: {vos}")
            tot += 1; ok += passed
            print(f"{'✅' if passed else '❌'} [{rep+1}] {cid}")
            for msg, exp, good, out in res:
                print(f"    lead: {msg}\n    bot{'' if exp is None else ' (' + exp + (' ok' if good else ' FALLA') + ')'}: "
                      + out.replace(chr(10), ' / ')[:420])
    print(f"\n{ok}/{tot} casos OK · prompt={Path(args.prompt).name} · estado={args.estado}")
    sys.exit(0 if ok == tot else 1)


if __name__ == "__main__":
    main()
