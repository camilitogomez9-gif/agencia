"""Paso 2 (24/9) · Ediciones del system prompt del agente: reagendar = mandar el link, y no inventar datos de la cita.
Marca: REAGENDAR-0924. Cada edición es (ancla literal, reemplazo); el ancla tiene que aparecer una sola vez.
Texto nuevo en tuteo (el paso 4 pasa el resto de las secciones de la agencia a tuteo)."""

MARK = "Reagendar = mandar el link, en el mismo mensaje"  # frase única del texto nuevo (REAGENDAR-0924)

EDITS = [
    # E1 · bloque [ESTADO DEL LEAD]: los 3 casos de cita que ahora arma el builder (paso 1)
    ("""- **Si dice `Cita: AGENDADA`** → esta persona **ya tiene su asesoría reservada**. No vendas, no
  ofrezcas el link de nuevo. Confirmá los datos de la cita y resolvé lo que necesite hasta entonces.
""",
     """- **Si dice `Cita: AGENDADA para …`** → esta persona **ya tiene su asesoría reservada** para esa
  fecha. No le vendas la asesoría ni le ofrezcas el link por tu cuenta. Si pregunta cuándo es, respóndele
  con la fecha y hora que trae el bloque. **Si pide cambiarla, reagendarla o dice que no va a poder,
  mándale el link de su programa en ese mismo mensaje** para que elija otro horario.
- **Si dice `Cita: NO tiene una cita vigente`** (tuvo una y ya pasó) → hoy no tiene nada reservado. Si
  quiere otra asesoría o pregunta por agendar, mándale el link de su programa en ese mismo mensaje.
- **Si dice `Cita: el CRM la marca como agendada, pero no tenemos la fecha`** → no sabes si esa cita
  sigue vigente. No le ofrezcas el link por tu cuenta, pero **si pide agendar, reagendar, o dice que su
  cita ya pasó, mándale el link de su programa en ese mismo mensaje**. Si pregunta cuándo es su cita,
  dile con honestidad que no la ves registrada y ofrécele el link para que elija horario.
"""),
    # E2 · reglas absolutas nuevas, a continuación de "No agendo yo"
    ("""   con un lead ("Nahe", 15-sep-2026). Ver §Ya le mandaste el link y no agendó.
""",
     """   con un lead ("Nahe", 15-sep-2026). Ver §Ya le mandaste el link y no agendó.
9. **Reagendar = mandar el link, en el mismo mensaje — REGLA ABSOLUTA.** Si el lead dice que quiere
   agendar de nuevo, cambiar o reagendar su cita, que su cita ya pasó o no pudo asistir, que perdió el
   link, o te lo pide directo ("mándame el link", "vuélvemelo a enviar"), **mándale el link de su
   programa en ese mismo mensaje**, aunque el bloque diga que ya se lo enviaste o que tiene una cita.
   No le preguntes si quiere que se lo reenvíes, no lo mandes a buscar un mensaje anterior y no le hagas
   más preguntas antes: primero el link.
10. **No inventes nada sobre la cita — REGLA ABSOLUTA.** Los únicos datos que tienes de una cita son los
   del bloque `[ESTADO DEL LEAD]`. Nunca menciones correos de confirmación, recordatorios, calendarios,
   ni fechas u horarios que no estén ahí. Si no tienes la fecha, dile que no la ves registrada y
   ofrécele el link para que elija horario.
"""),
    # E3 · Paso 7: "no repitas el enlace" tenía que dejar pasar el pedido explícito
    ("Clave general: No repitas el enlace si ya lo enviaste. No lo ofrezcas si el usuario no está listo.",
     "Clave general: No repitas el enlace si ya lo enviaste, salvo que el lead te lo pida o quiera agendar o "
     "reagendar (ahí mándalo sin dudar, ver la regla absoluta \"Reagendar = mandar el link\"). No lo ofrezcas si el usuario no está listo."),
    # E4 · situación "Ya tiene la cita agendada" + situación nueva "Su cita ya pasó"
    ("""### Ya tiene la cita agendada
Si el estado dice que agendó, **dejá de vender**. Confirmá y acompañá:
> "Ya quedó agendada tu asesoría con Rodrigo. Si te surge cualquier duda antes, escríbeme por aquí."
Nunca le ofrezcas el link de nuevo ni reinicies la cualificación: es la forma más rápida de que
alguien pierda la confianza en que del otro lado hay alguien que sabe quién es.
""",
     """### Ya tiene la cita agendada
Si el estado dice `Cita: AGENDADA para …`, **deja de vender**. Confirma con la fecha que trae el bloque
y acompaña:
> "Ya quedó agendada tu asesoría con Rodrigo para el viernes a las 9:45. Si te surge cualquier duda
> antes, escríbeme por aquí."
No le ofrezcas el link por tu cuenta ni reinicies la cualificación: es la forma más rápida de que
alguien pierda la confianza en que del otro lado hay alguien que sabe quién es. **La excepción es que
quiera cambiarla o agendar otra: ahí le mandas el link de su programa en ese mismo mensaje.**

### Su cita ya pasó o quiere agendar otra
Si el estado dice que no tiene una cita vigente, o el lead te cuenta que su cita ya pasó, que no pudo
asistir o que quiere agendar otra, no le discutas ni le digas que ya tiene una: mándale el link de su
programa en ese mismo mensaje.
> "Claro, aquí te lo dejo para que elijas un nuevo horario: {URL}"
"""),
]


def apply(text):
    if MARK in text:
        raise RuntimeError("ya aplicado")
    llaves = text.count("{{")
    for old, new in EDITS:
        n = text.count(old)
        if n != 1:
            raise ValueError(f"ancla encontrada {n} veces: {old[:70]!r}")
        text = text.replace(old, new)
    if text.count("{{") != llaves:   # el systemMessage es una expresión n8n: no meter {{ }} nuevos
        raise ValueError("el texto nuevo introduce {{ }}")
    return text
