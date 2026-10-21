#!/usr/bin/env python3
"""
Deriva la cobertura de la Matriz A (conversacional) y la Matriz B (topológica)
del protocolo de paridad de Happy Flops.

La cobertura NO se elige, se deriva. Ese fue el modo de fallar de los tres
intentos previos: los casos se eligieron a ojo y el denominador quedó a merced
de quien lo escribía.

  Matriz A = evento(3) × paso(4) × clase de entrada(11) = 132 celdas.
             La cobertura observada sale de parsear los 10 transcripts reales.
  Matriz B = toda salida de if/switch/splitInBatches del workflow congelado.

Salida: JSON a stdout, para que MATRIZ.md se construya de acá y no a mano.

    python3 scripts/testing/hpf-derivar-matriz.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HPF = REPO / "clients/HPF_HappyFlops"
ORACULO = HPF / "07_testing/oraculo"
BUILD = HPF / "03_workflows/hpf-inbound-handler-testbuild-nodebounce-2026-08-05.json"

EVENTOS = ["Boda", "XV", "Otros"]
PASOS = ["saludo", "imagen de evento", "fichas de producto", "cotización/cierre"]
CLASES = [
    "producto puntual", "pedido colectivo", "producto ambiguo",
    "producto fuera del evento", "cantidad + CP", "debajo del mínimo",
    "pregunta de negocio", "imagen", "audio", "comprobante", "ráfaga",
]

# Mínimos de compra. Fuente: 00_migracion_ghl/01_logica_actual/05_reglas_negocio.md:32-40
MINIMOS = {"sandalias": 50, "pantuflas": 50, "cilindros": 40,
           "mandiles": 12, "anticrudas": 35, "vasos": 50}
# Gate de evento. Fuente: 05_reglas_negocio.md:38,56,67 + 04_agentes_llm.md:140
SOLO_BODA = {"mandiles"}

PRODUCTOS = {
    "sandalias": r"sandalia", "pantuflas": r"pantufla", "cilindros": r"cilindro|termo",
    "mandiles": r"mandil", "anticrudas": r"anti\s*cruda|anticruda|kit", "vasos": r"vaso|popote",
}


def parsear_sample(texto: str) -> list[dict]:
    """Devuelve [{turno, rol, contenido}] a partir del markdown del oráculo."""
    turnos = []
    for m in re.finditer(r"\*\*T(\d+) · (LEAD|RECIBE|DECIDE)\*\*\s*\n```(?:json)?\n(.*?)\n```",
                         texto, re.S):
        turnos.append({"turno": int(m.group(1)), "rol": m.group(2),
                       "contenido": m.group(3)})
    return turnos


def evento_de_sample(turnos: list[dict]) -> str:
    """El evento sale de los DECIDE, que es la decisión interna observada."""
    for t in turnos:
        if t["rol"] != "DECIDE":
            continue
        m = re.search(r'"evento"\s*:\s*"([^"]+)"', t["contenido"])
        if m:
            v = m.group(1).upper()
            if "BODA" in v:
                return "Boda"
            if "XV" in v or "QUINCE" in v:
                return "XV"
            return "Otros"
    # sin evento explícito en los DECIDE: se infiere del texto del lead
    blob = " ".join(t["contenido"].lower() for t in turnos if t["rol"] == "LEAD")
    if re.search(r"\bxv\b|quince|15\s*a[ñn]os", blob):
        return "XV"
    if re.search(r"\bbodas?\b", blob):
        return "Boda"
    return "Otros"


def clasificar(texto: str, prev: list[str]) -> list[str]:
    """Clases de entrada que ejerce este turno del lead. Reglas explícitas y auditables."""
    t = texto.lower()
    out = []
    prods = [p for p, rx in PRODUCTOS.items() if re.search(rx, t)]

    if re.search(r"\btodos?\b|todo el catalogo|todos los productos", t):
        out.append("pedido colectivo")
    if len(prods) == 1 and "pedido colectivo" not in out:
        out.append("producto puntual")
    if re.search(r"mo[ñn]o|sat[ií]n|peluche|delgada|gruesa", t):
        out.append("producto ambiguo")

    cant = [int(x) for x in re.findall(r"\b(\d{1,4})\b", t)]
    cp = re.search(r"\b\d{5}\b", t) or re.search(r"\bc\.?p\.?\b", t)
    if cant and cp:
        out.append("cantidad + CP")
    for p in prods:
        chicos = [c for c in cant if 0 < c < MINIMOS[p] and c not in (15, 9)]
        if chicos:
            out.append("debajo del mínimo")
            break
    if re.search(r"\?|cu[aá]nto|cu[aá]l|c[oó]mo|d[oó]nde|precio|env[ií]o|tiempo|tarda|garant", t):
        out.append("pregunta de negocio")
    if re.search(r"te env[ií]o una imagen|foto del producto|adjunto|imagen del producto", t):
        out.append("imagen")
    if re.search(r"nota de voz|audio", t):
        out.append("audio")
    if re.search(r"comprobante|transferenc|dep[oó]sit|pagu[eé]|pago realizado", t):
        out.append("comprobante")
    if prev and texto.strip() and texto.strip() == prev[-1].strip():
        out.append("ráfaga")
    return sorted(set(out))


def paso_de_turno(i: int, turnos: list[dict], texto: str) -> str:
    """El paso del embudo que ejerce el turno."""
    if i <= 1:
        return "saludo"
    t = texto.lower()
    if re.search(r"\bxv\b|quince|\bboda\b|bautizo|graduaci|cumplea", t) and i <= 4:
        return "imagen de evento"
    if re.search(r"\b\d{5}\b", t) or re.search(r"\bc\.?p\.?\b", t) or re.search(r"cotiz|total|precio final", t):
        return "cotización/cierre"
    return "fichas de producto"


def matriz_a() -> dict:
    celdas = {(e, p, c): [] for e in EVENTOS for p in PASOS for c in CLASES}
    resumen = []
    for f in sorted(ORACULO.glob("sample_*.md"),
                    key=lambda x: int(re.search(r"\d+", x.stem).group())):
        turnos = parsear_sample(f.read_text(encoding="utf-8"))
        ev = evento_de_sample(turnos)
        leads = [t for t in turnos if t["rol"] == "LEAD"]
        recibes = [t for t in turnos if t["rol"] == "RECIBE"]
        vacios = sum(1 for t in recibes if t["contenido"].strip() in ("{}", ""))
        prev: list[str] = []
        for i, t in enumerate(leads):
            clases = clasificar(t["contenido"], prev)
            paso = paso_de_turno(i, turnos, t["contenido"])
            for c in clases:
                celdas[(ev, paso, c)].append(f"{f.stem}:T{t['turno']}")
            prev.append(t["contenido"])
        resumen.append({"sample": f.stem, "evento": ev, "turnos": len(turnos),
                        "lead": len(leads), "recibe": len(recibes), "recibe_vacios": vacios})
    cubiertas = {k: v for k, v in celdas.items() if v}
    return {"resumen_samples": resumen,
            "total_celdas": len(celdas), "celdas_con_observado": len(cubiertas),
            "celdas": {f"{e}|{p}|{c}": v for (e, p, c), v in celdas.items()}}


def matriz_b() -> dict:
    d = json.loads(BUILD.read_text(encoding="utf-8"))
    conns = d["connections"]
    aristas = []
    for n in d["nodes"]:
        t = n["type"].split(".")[-1]
        if t not in ("if", "switch", "splitInBatches", "filter"):
            continue
        outs = conns.get(n["name"], {}).get("main", [])
        if t == "switch":
            reglas = (n["parameters"].get("rules") or {}).get("values") or []
            etiquetas = [(r.get("outputKey") or f"rule{i}") for i, r in enumerate(reglas)]
            if (n["parameters"].get("options") or {}).get("fallbackOutput") is not None:
                etiquetas.append("fallback")
        elif t == "splitInBatches":
            etiquetas = ["done", "loop"]
        else:
            etiquetas = ["true", "false"]
        for i, lab in enumerate(etiquetas):
            dest = [x["node"] for x in (outs[i] if i < len(outs) and outs[i] else [])]
            aristas.append({"nodo": n["name"], "tipo": t, "idx": i, "salida": lab,
                            "destino": dest, "sumidero": not dest})
    externos = [n["name"] for n in d["nodes"]
                if n["type"].split(".")[-1] in
                ("httpRequest", "telegram", "postgres", "openAi", "agent", "toolHttpRequest")]
    return {"nodos_decision": len({a["nodo"] for a in aristas}),
            "total_aristas": len(aristas),
            "sumideros": [a for a in aristas if a["sumidero"]],
            "aristas": aristas, "nodos_externos": externos}


if __name__ == "__main__":
    if not BUILD.exists():
        sys.exit(f"falta el build congelado: {BUILD}")
    a, b = matriz_a(), matriz_b()
    print(json.dumps({
        "matriz_a": a, "matriz_b": b,
        "calculo_A": f"{len(EVENTOS)} eventos × {len(PASOS)} pasos × {len(CLASES)} clases = "
                     f"{len(EVENTOS)*len(PASOS)*len(CLASES)} celdas",
    }, ensure_ascii=False, indent=1))
