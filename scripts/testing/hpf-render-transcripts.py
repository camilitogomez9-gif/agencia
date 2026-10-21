#!/usr/bin/env python3
"""
Renderiza los artefactos de evidencia como transcripts legibles — lo que el lead
efectivamente vio, no lo que el LLM produjo.

El protocolo pone esto primero en la entrega: Juanpi no puede auditar un número
cuyo numerador y denominador produjo la misma persona que hizo el trabajo, pero
sí puede leer una conversación y decir "esto está bien" o "esto no".

Cada mensaje sale del `message_part` del Sanitize (el contenido byte-exacto) más
el acuse del emisor (la prueba de que se entregó). Nada está pegado a mano.

    python3 scripts/testing/hpf-render-transcripts.py HPF-FIC-008 HPF-FIC-009 ...
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EVID = REPO / "clients/HPF_HappyFlops/07_testing/evidencia"

ICONO = {"photo_url": "🖼️ foto", "doc_url": "📄 catálogo PDF", "video_url": "🎥 video"}


def artefactos(caso: str) -> list[dict]:
    """El último intento de cada turno, en orden."""
    porturno: dict[int, tuple[int, str]] = {}
    for f in glob.glob(str(EVID / caso / "turno_*.json")):
        base = Path(f).stem                      # turno_2.attempt3
        t = int(base.split("_")[1].split(".")[0])
        a = int(base.split("attempt")[1]) if "attempt" in base else 0
        if t not in porturno or a > porturno[t][0]:
            porturno[t] = (a, f)
    return [json.load(open(porturno[t][1], encoding="utf-8")) for t in sorted(porturno)]


def render(caso: str, titulo: str = "") -> str:
    arts = artefactos(caso)
    if not arts:
        return f"### {caso}\n\n_sin evidencia en disco_\n"

    out = [f"### {titulo or caso}", ""]
    entregadas = sum(a.get("n_entregadas", 0) for a in arts)
    esperadas = sum(a.get("n_esperadas", 0) for a in arts)
    out.append(f"`{caso}` · {len(arts)} turnos · **{entregadas}/{esperadas} partes entregadas** · "
               f"evidencia en `07_testing/evidencia/{caso}/`")
    out.append("")

    for a in arts:
        out.append(f"**Lead:** {a['texto_enviado'] or '_(media)_'}")
        out.append("")
        acuses = {(p["emisor"], p["run"]): p for p in a.get("partes_emitidas", [])}
        entregados = [p for p in a.get("partes_emitidas", []) if p.get("entregado")]
        for i, p in enumerate(a.get("partes_esperadas", [])):
            media = [ICONO[k] for k in ("photo_url", "doc_url", "video_url") if p.get(k)]
            sello = ""
            if i < len(entregados):
                mid = entregados[i].get("message_id")
                sello = f"  `msg_id {mid}`" if mid else ""
            adj = f"  ·  _{' + '.join(media)}_" if media else ""
            texto = (p.get("message_part") or "").replace("\n", "\n> ")
            out.append(f"> **Rebeca:** {texto}{adj}{sello}")
            out.append(">")
        for p in a.get("textos_post", []) or []:
            out.append(f"> **Rebeca** _(imagen del evento / promo)_: {p.splitlines()[0]}…")
            out.append(">")
        out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    casos = sys.argv[1:]
    if not casos:
        sys.exit("pasá los ids de caso a renderizar")
    for c in casos:
        print(render(c))
        print("---\n")
