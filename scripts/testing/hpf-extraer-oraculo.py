#!/usr/bin/env python3
"""
hpf-extraer-oraculo.py — Extrae el corpus de comportamiento OBSERVADO del bot Rebeca original.

Fuente: clients/HPF_HappyFlops/00_migracion_ghl/00_inputs/conversation_samples.json
Salida: clients/HPF_HappyFlops/07_testing/oraculo/

Son 10 transcripts reales de produccion del bot legacy (Kommo), etiquetados
'golden_test_transcript_for_migration_parity'. Estuvieron sin usar desde el 2026-05-03.

OJO con la estructura: el JSON es una LISTA de UN elemento, y ese elemento tiene la
clave 'conversation_samples' con los 10 samples adentro. Hacer len(json.load(f))
devuelve 1 y hace creer que hay una sola conversacion. Es el error que llevo a
subdimensionar el ground truth en los intentos previos.

Los turnos 'assistant' vienen en dos formatos:
  - texto plano  -> es lo que el lead REALMENTE recibio
  - JSON {"output": {...}} -> es una decision interna (Router: step_N, o el agente
    de productos: {evento, productos[], texto_dinamico}). No lo ve el lead, pero es
    oro: es un corpus ETIQUETADO de entrada -> decision.

Uso:
  python3 scripts/testing/hpf-extraer-oraculo.py
  python3 scripts/testing/hpf-extraer-oraculo.py --sample sample_9
"""
import json
import os
import re
import sys
import argparse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
BASE = os.path.join(REPO, "camilo-workspace") if not os.path.isdir(
    os.path.join(REPO, "clients")) else REPO
SRC = os.path.join(BASE, "clients/HPF_HappyFlops/00_migracion_ghl/00_inputs/conversation_samples.json")
OUT = os.path.join(BASE, "clients/HPF_HappyFlops/07_testing/oraculo")

# ─── Saneo del oraculo ────────────────────────────────────────────────────────
# UNICA funcion de normalizacion permitida en todo el protocolo, y solo borra dos
# cosas que metio el anonimizador / el sistema, NO contenido del bot:
#   1. el sufijo "Fecha de hoy: ..." que inyectaba el flujo legacy en el user message
#   2. el token [PHONE] con que el anonimizador piso telefonos Y fechas
# Todo lo demas (NBSP, dobles espacios, tildes inconsistentes, emojis) queda BINARIO:
# esos defectos son la paridad.
RE_FECHA = re.compile(r"\s*Fecha de hoy:.*$", re.S)
RE_PREFIJO = re.compile(r"^(Respuesta del usuario|Mensaje del usuario):\s*")


def sanear_input_lead(texto):
    """Limpia el turno del LEAD para poder reproducirlo como input de test."""
    t = RE_FECHA.sub("", texto)
    t = RE_PREFIJO.sub("", t)
    return t.strip()


def clasificar_turno_agente(texto):
    """Devuelve ('decision', obj) si es JSON interno, o ('mensaje', texto) si lo vio el lead."""
    t = texto.strip()
    if t.startswith("{") and '"output"' in t:
        try:
            return "decision", json.loads(t)["output"]
        except Exception:
            pass
    # el legacy a veces envolvia el mensaje en comillas tipograficas
    return "mensaje", t.strip("“”")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", help="extraer solo este sample_id")
    args = ap.parse_args()

    if not os.path.exists(SRC):
        print("ERROR: no encuentro %s" % SRC, file=sys.stderr)
        sys.exit(2)

    wrapper = json.load(open(SRC, encoding="utf-8"))
    samples = wrapper[0]["conversation_samples"]  # <-- el array real
    if args.sample:
        samples = [s for s in samples if s["sample_id"] == args.sample]

    os.makedirs(OUT, exist_ok=True)
    indice = []
    total_turnos = total_mensajes = total_decisiones = 0

    for s in samples:
        sid = s["sample_id"]
        lineas = ["# Oraculo observado — %s" % sid,
                  "",
                  "Fuente: `00_migracion_ghl/00_inputs/conversation_samples.json` "
                  "(transcript real de produccion del bot legacy en Kommo).",
                  "session_hash: `%s` · turnos: %d" % (s.get("session_hash", "?"), len(s["turns"])),
                  "",
                  "- `LEAD` = lo que escribio el cliente (ya saneado, listo para usar como input de test).",
                  "- `RECIBE` = lo que el bot original le mando al lead. **Esto es el esperado.**",
                  "- `DECIDE` = decision interna del Router/agente de productos. No la ve el lead.",
                  "",
                  "---",
                  ""]
        productos_vistos = set()
        for t in s["turns"]:
            n = t["turn"]
            if t["role"] == "human":
                lineas.append("**T%d · LEAD**" % n)
                lineas.append("```\n%s\n```" % sanear_input_lead(t["text"]))
            else:
                tipo, val = clasificar_turno_agente(t["text"])
                if tipo == "decision":
                    total_decisiones += 1
                    if isinstance(val, dict) and val.get("productos"):
                        productos_vistos.update(val["productos"])
                    lineas.append("**T%d · DECIDE**" % n)
                    lineas.append("```json\n%s\n```" % json.dumps(val, ensure_ascii=False, indent=2))
                else:
                    total_mensajes += 1
                    lineas.append("**T%d · RECIBE**" % n)
                    lineas.append("```\n%s\n```" % val)
            lineas.append("")
            total_turnos += 1

        path = os.path.join(OUT, "%s.md" % sid)
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lineas))

        indice.append({
            "sample_id": sid,
            "turnos": len(s["turns"]),
            "productos_mencionados": sorted(productos_vistos),
            "archivo": "oraculo/%s.md" % sid,
        })
        print("  %-11s %3d turnos -> %s" % (sid, len(s["turns"]), os.path.basename(path)))

    with open(os.path.join(OUT, "INDICE.json"), "w", encoding="utf-8") as f:
        json.dump(indice, f, ensure_ascii=False, indent=2)

    print("\n%d transcripts · %d turnos · %d mensajes al lead · %d decisiones internas"
          % (len(samples), total_turnos, total_mensajes, total_decisiones))
    print("Salida: %s" % OUT)


if __name__ == "__main__":
    main()
