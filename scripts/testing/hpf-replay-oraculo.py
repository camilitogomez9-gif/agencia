#!/usr/bin/env python3
"""
C1 de la Fase 4 — réplica del oráculo.

Toma los turnos que escribieron leads reales en producción contra el bot VIEJO y
los vuelve a mandar, en su secuencia original, al bot NUEVO. Después compara lo
que respondió cada uno.

Es la respuesta directa a "¿el agente nuevo responde como el original?", y es el
corpus más barato de defender: no lo eligió nadie, son las conversaciones que
efectivamente ocurrieron.

Veredictos:
  IGUAL         byte-exacto
  EQUIVALENTE   difiere en forma, no en efecto comercial (lo dictamina un juez
                LLM con la respuesta del original al lado — es una tarea de
                comparación, no de opinión)
  DISTINTO      cambia lo que el lead entiende o hace
  NO-REPLICAR   el original respondió {} (vacío). Ahí el nuevo DEBE responder
                algo: quedarse mudo es FALLA.

El juez nunca convierte un rojo en verde: solo puede marcar para revisión.

    python3 scripts/testing/hpf-replay-oraculo.py --samples 9,3 [--sin-juez]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ORACULO = REPO / "clients/HPF_HappyFlops/07_testing/oraculo"
SALIDA = REPO / "clients/HPF_HappyFlops/07_testing/campana-exhaustiva-2026-08-05"

sys.path.insert(0, str(REPO / "scripts/testing"))
import importlib.util
_spec = importlib.util.spec_from_file_location("runner", REPO / "scripts/testing/hpf-paridad-runner.py")
runner = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(runner)


def parsear(texto: str) -> list[dict]:
    return [{"turno": int(m.group(1)), "rol": m.group(2), "contenido": m.group(3)}
            for m in re.finditer(
                r"\*\*T(\d+) · (LEAD|RECIBE|DECIDE)\*\*\s*\n```(?:json)?\n(.*?)\n```",
                texto, re.S)]


def pares(turnos: list[dict]) -> list[tuple[dict, dict | None]]:
    """(LEAD, el RECIBE que le siguió) — los DECIDE no los ve el lead."""
    out = []
    for i, t in enumerate(turnos):
        if t["rol"] != "LEAD":
            continue
        sig = next((x for x in turnos[i + 1:] if x["rol"] in ("LEAD", "RECIBE")), None)
        out.append((t, sig if sig and sig["rol"] == "RECIBE" else None))
    return out


# Diferencias firmadas: el bot nuevo hace esto a propósito y NO es una regresión.
# Sin este contexto el juez marca DISTINTO cada mejora que el cliente pidió.
DELTAS = """Estas diferencias son DELIBERADAS y fueron pedidas por el cliente. Si la única
diferencia es una de estas, el veredicto es MEJORA-FIRMADA:
- el nuevo no re-manda info ni re-pide datos que ya tenía
- el nuevo no re-pide cantidad ni código postal después de haber cotizado
- el nuevo confirma la variante de pantufla antes de cotizar, en vez de asumir
- el nuevo no pide mail ni promete PDF: deriva al equipo
- el nuevo manda el catálogo en vez de escalar el chat
- el nuevo manda las fotos de pantuflas en vez de escalar
- el nuevo reconoce vasos con popote en imágenes
- el nuevo SIEMPRE responde algo; el viejo a veces se quedaba mudo"""


def juzgar(lead: str, original: str, nuevo: str, key: str) -> tuple[str, str]:
    """Comparación, no opinión: el juez ve las dos respuestas y la lista de deltas."""
    prompt = (
        "Compará dos respuestas de un bot de venta de recuerditos para eventos, a un mismo "
        "mensaje de un lead. La primera es la del bot viejo (la referencia). La segunda es la "
        "del bot nuevo.\n\n"
        f"{DELTAS}\n\n"
        f"MENSAJE DEL LEAD:\n{lead}\n\nRESPUESTA DEL BOT VIEJO:\n{original}\n\n"
        f"RESPUESTA DEL BOT NUEVO:\n{nuevo}\n\n"
        "¿El bot nuevo logra el mismo efecto comercial? Da lo mismo que cambie la redacción, "
        "el orden o el formato. Lo que importa es si el lead entiende lo mismo y puede hacer "
        "lo mismo: mismos productos, mismos precios, misma pregunta o pedido de datos, misma "
        "capacidad de avanzar la compra.\n\n"
        "Si el nuevo omite algo que el viejo hacía y NO está en la lista de arriba, es DISTINTO "
        "aunque te parezca una mejora: eso lo decide el cliente, no vos.\n\n"
        'Respondé SOLO un JSON: '
        '{"veredicto":"EQUIVALENTE"|"MEJORA-FIRMADA"|"DISTINTO","motivo":"<una oración>"}')
    body = json.dumps({"model": "gpt-4o", "temperature": 0,
                       "messages": [{"role": "user", "content": prompt}],
                       "response_format": {"type": "json_object"}}).encode()
    req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=body,
                                 headers={"Authorization": f"Bearer {key}",
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            j = json.loads(json.load(r)["choices"][0]["message"]["content"])
        return j.get("veredicto", "DISTINTO"), j.get("motivo", "")
    except Exception as e:                                        # noqa: BLE001
        return "DISTINTO", f"el juez falló: {type(e).__name__}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", help="números, ej. 9,3. Por defecto los 10")
    ap.add_argument("--sin-juez", action="store_true")
    ap.add_argument("--max-turnos", type=int, default=0, help="corta cada sample (0 = todos)")
    args = ap.parse_args()

    env = runner.cargar_env()
    api_key = os.environ.get("HPF_N8N_API_KEY") or sys.exit("falta HPF_N8N_API_KEY")
    n8n = runner.N8N(env, api_key)
    okey = ""
    if not args.sin_juez:
        for l in (REPO / ".env").read_text().splitlines():
            if l.startswith("OPENAI_API_KEY="):
                okey = l.split("=", 1)[1]
    lane = env["HPF_TG_CHAT_ID"]
    SALIDA.mkdir(parents=True, exist_ok=True)

    nums = ([int(x) for x in args.samples.split(",")] if args.samples
            else sorted(int(re.search(r"\d+", f.stem).group()) for f in ORACULO.glob("sample_*.md")))

    filas = []
    for n in nums:
        f = ORACULO / f"sample_{n}.md"
        turnos = parsear(f.read_text(encoding="utf-8"))
        pp = pares(turnos)
        if args.max_turnos:
            pp = pp[:args.max_turnos]
        sesion = f"sess_replay_s{n}_{int(time.time())}"
        print(f"\n=== sample_{n} · {len(pp)} turnos del lead ===")
        for idx, (lead, recibe) in enumerate(pp, 1):
            art = runner.correr_turno(n8n, env, lane_contact_id=lane, session_id=sesion,
                                      texto=lead["contenido"], canal="telegram")
            nuevo = "\n".join((p.get("message_part") or "")
                              for p in art.get("partes_esperadas", []))
            esperado = (recibe or {}).get("contenido", "").strip()
            vacio = esperado in ("{}", "")

            if vacio:
                ver = "NO-REPLICAR-OK" if art.get("n_esperadas", 0) >= 1 else "MUDO"
                motivo = "el original no respondió; el nuevo sí" if ver == "NO-REPLICAR-OK" \
                    else "el nuevo también se quedó mudo"
            elif esperado.strip() == nuevo.strip():
                ver, motivo = "IGUAL", "byte-exacto"
            elif args.sin_juez or not okey:
                ver, motivo = "REVISAR", "sin juez"
            else:
                ver, motivo = juzgar(lead["contenido"], esperado, nuevo, okey)

            print(f"  T{lead['turno']:<3} {ver:<15} {lead['contenido'][:52]!r}")
            filas.append({"sample": f"sample_{n}", "turno": lead["turno"],
                          "lead": lead["contenido"], "original": esperado, "nuevo": nuevo,
                          "veredicto": ver, "motivo": motivo,
                          "partes": art.get("n_esperadas"), "entregadas": art.get("n_entregadas"),
                          "execution": art.get("execution_id")})
            (SALIDA / "replay-oraculo.jsonl").open("a").write(
                json.dumps(filas[-1], ensure_ascii=False) + "\n")

    import collections
    c = collections.Counter(x["veredicto"] for x in filas)
    print(f"\n{'='*66}\nRÉPLICA DEL ORÁCULO — {len(filas)} turnos")
    for k, v in c.most_common():
        print(f"  {k:<16} {v}")
    malos = [x for x in filas if x["veredicto"] in ("DISTINTO", "MUDO")]  # MEJORA-FIRMADA no cuenta
    if malos:
        print(f"\n{len(malos)} turnos donde el nuevo NO logra lo mismo:")
        for x in malos[:15]:
            print(f"  {x['sample']} T{x['turno']}: {x['motivo'][:88]}")


if __name__ == "__main__":
    main()
