#!/usr/bin/env python3
"""
Gate de mutación G2-bis — protocolo de paridad HPF.

Un corpus que no puede fallar no mide nada. Este script inyecta defectos a
propósito en el workflow VIVO y verifica que cada uno rompa al menos un caso
nombrado, con FALLA y diff de bytes.

Criterio del gate (más duro que "el caso dejó de pasar):
  - APRUEBA con FALLA o PARCIAL, siempre que haya al menos un assert en rojo
    con diff de bytes. Un SIN-EVIDENCIA NO aprueba: ahí se rompió la
    instrumentación, no se detectó el defecto.
  - Si un defecto no rompe nada, es un HUECO DE COBERTURA y se reporta como tal.
    Eso no es un fallo del gate: es exactamente para lo que existe.

Seguridad, porque esto rompe producción a propósito:
  - La reversión pega el BUILD FINAL CONGELADO, no un inverso calculado.
  - Va en try/finally: se revierte aunque el test explote.
  - Se verifica por re-export después de cada mutación.
  - Si una reversión falla, ABORTA todo y avisa.

    python3 scripts/testing/hpf-gate-mutacion.py [--solo 1,3]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BUENO = REPO / "clients/HPF_HappyFlops/03_workflows/hpf-inbound-handler-final-2026-08-05.json"
API = "https://dev[TU-INSTANCIA-N8N]/api/v1/workflows/IPO1c36NLzkXrBh9"
RUNNER = REPO / "scripts/testing/hpf-paridad-runner.py"


def _req(method: str, data: bytes | None = None):
    key = os.environ.get("HPF_N8N_API_KEY") or sys.exit("falta HPF_N8N_API_KEY")
    return urllib.request.Request(
        API, data=data, method=method,
        headers={"X-N8N-API-KEY": key, "Content-Type": "application/json"})


def bajar() -> dict:
    with urllib.request.urlopen(_req("GET"), timeout=60) as r:
        return json.load(r)


def escribir(d: dict) -> int:
    body = json.dumps({"name": d["name"], "nodes": d["nodes"],
                       "connections": d["connections"],
                       "settings": d.get("settings", {})}).encode()
    with urllib.request.urlopen(_req("PUT", body), timeout=90) as r:
        return r.status


def restaurar() -> bool:
    """Siempre desde el build congelado conocido-bueno."""
    escribir(json.loads(BUENO.read_text(encoding="utf-8")))
    vivo = bajar()
    bueno = json.loads(BUENO.read_text(encoding="utf-8"))
    V = {n["name"]: json.dumps(n.get("parameters"), sort_keys=True) for n in vivo["nodes"]}
    B = {n["name"]: json.dumps(n.get("parameters"), sort_keys=True) for n in bueno["nodes"]}
    return V == B


# --------------------------------------------------------------- las 5 mutaciones

def m1_borrar_ficha_sandalias(d: dict) -> str:
    n = next(x for x in d["nodes"] if x["name"] == "Sanitize + Split Output")
    L = n["parameters"]["jsCode"].split("\n")
    ini = next(i for i, l in enumerate(L) if 'id:"sandalias"' in l)
    # Contar llaves, no buscar "},": la línea del pdf:{...} también termina así
    # y cortar ahí deja el JS roto. Lo detectó el ensayo en seco con node --check.
    prof, fin = 0, ini
    while True:
        prof += L[fin].count("{") - L[fin].count("}")
        if prof == 0:
            break
        fin += 1
    del L[ini:fin + 1]
    n["parameters"]["jsCode"] = "\n".join(L)
    return f"borradas las líneas {ini+1}-{fin+1} del CATALOGO (entrada sandalias)"


def m2_precio_prompt(d: dict) -> str:
    ag = next(x for x in d["nodes"] if "agent" in x["type"].lower())
    sm = ag["parameters"]["options"]["systemMessage"]
    if "$25" not in sm:
        return "SIN EFECTO: '$25' no aparece en el systemMessage"
    ag["parameters"]["options"]["systemMessage"] = sm.replace("$25", "$24")
    return f"{sm.count('$25')} ocurrencias de '$25' -> '$24' en el prompt"


def m3_apagar_ris(d: dict) -> str:
    ag = next(x for x in d["nodes"] if "agent" in x["type"].lower())
    ag["parameters"].setdefault("options", {})["returnIntermediateSteps"] = False
    return "returnIntermediateSteps -> false"


def m4_gate_mandiles(d: dict) -> str:
    n = next(x for x in d["nodes"] if x["name"] == "Sanitize + Split Output")
    js = n["parameters"]["jsCode"]
    viejo = 'id:"mandiles", g:"mandil", tipo:"principal", ev:["BODA"]'
    if viejo not in js:
        return "SIN EFECTO: no se encontró el gate ev:[\"BODA\"] de mandiles"
    n["parameters"]["jsCode"] = js.replace(viejo, 'id:"mandiles", g:"mandil", tipo:"principal"')
    return 'borrado ev:["BODA"] de la ficha de mandiles'


def m5_header_promo(d: dict) -> str:
    tocados = []
    for x in d["nodes"]:
        for campo, cont in (("jsCode", x.get("parameters", {})),
                            ("systemMessage", x.get("parameters", {}).get("options", {}))):
            v = cont.get(campo)
            if isinstance(v, str) and "7 DIAS DE PROMO" in v:
                cont[campo] = v.replace("7 DIAS DE PROMO", "XXXXXXXXXXXXXXX")
                tocados.append(f"{x['name']}.{campo}")
    return f"header '7 DIAS DE PROMO' neutralizado en {tocados or 'NINGÚN nodo'}"


MUTACIONES = [
    (1, "borrar la ficha de sandalias del CATALOGO", m1_borrar_ficha_sandalias, ["HPF-FIC-007"]),
    (2, "$25 -> $24 en el prompt", m2_precio_prompt, ["HPF-COT-013", "HPF-FIC-007"]),
    (3, "apagar returnIntermediateSteps", m3_apagar_ris, ["HPF-FIC-008"]),
    (4, 'borrar ev:["BODA"] del gate de mandiles', m4_gate_mandiles, ["HPF-FIC-010"]),
    (5, "sacar el header de promo", m5_header_promo, ["HPF-COT-013", "HPF-FIC-009"]),
]


def correr(casos: list[str]) -> dict:
    out = subprocess.run(
        [sys.executable, "-u", str(RUNNER), "--solo", ",".join(casos),
         "--jsonl", "/tmp/hpf-mutacion.jsonl"],
        capture_output=True, text=True, cwd=str(REPO))
    estados = {}
    for linea in out.stdout.splitlines():
        for c in casos:
            if c in linea:
                estados[c] = linea.split("]")[1].split()[0] if "]" in linea else "?"
    return estados


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", help="números de mutación, ej. 1,3")
    args = ap.parse_args()
    pedidas = {int(x) for x in args.solo.split(",")} if args.solo else None

    if not BUENO.exists():
        sys.exit(f"falta el build conocido-bueno: {BUENO}")
    print(f"build de restauración: {BUENO.name}\n")

    resultados = []
    for num, desc, mutar, casos in MUTACIONES:
        if pedidas and num not in pedidas:
            continue
        print(f"{'='*72}\nMUTACIÓN {num} — {desc}")
        try:
            d = bajar()
            detalle = mutar(d)
            print(f"  inyectada: {detalle}")
            escribir(d)
            print(f"  escrita. corriendo {', '.join(casos)} …")
            estados = correr(casos)
            for c, e in estados.items():
                print(f"    {c}: {e}")
            # PARCIAL cuenta como detección: el caso pasó de verde a tener
            # asserts en rojo con diff de bytes. Exigir FALLA agregada (TODOS los
            # asserts rojos) es demasiado estricto y reporta 0/5 sobre un corpus
            # que sí detecta. Lo que NO cuenta es SIN-EVIDENCIA: ahí se rompió la
            # instrumentación, no se detectó el defecto.
            rompio = [c for c, e in estados.items() if e in ("FALLA", "PARC")]
            sinev = [c for c, e in estados.items() if e == "S/EV"]
            if rompio:
                veredicto, nota = "APRUEBA", f"rompió {', '.join(rompio)}"
            elif sinev:
                veredicto, nota = "NO APRUEBA", f"solo SIN-EVIDENCIA en {', '.join(sinev)}"
            else:
                veredicto, nota = "HUECO", "ningún caso se rompió: eje sin cobertura"
            print(f"  -> {veredicto}: {nota}")
            resultados.append((num, desc, detalle, estados, veredicto, nota))
        finally:
            print("  revirtiendo…", end=" ")
            if restaurar():
                print("OK, verificado por re-export")
            else:
                print("\n\n*** LA REVERSIÓN FALLÓ. ABORTO. REVISAR EL WORKFLOW A MANO. ***")
                sys.exit(2)

    print(f"\n{'='*72}\nRESUMEN DEL GATE")
    for num, desc, _, _, veredicto, nota in resultados:
        print(f"  [{veredicto:<10}] {num}. {desc:<46} {nota}")
    huecos = [r for r in resultados if r[4] != "APRUEBA"]
    print(f"\n{len(resultados)-len(huecos)}/{len(resultados)} mutaciones detectadas por el corpus")
    if huecos:
        print("Ejes sin cobertura, a declarar en la entrega:")
        for num, desc, *_ in huecos:
            print(f"  - {desc}")
    json.dump([{"n": n, "desc": d, "detalle": det, "estados": e, "veredicto": v, "nota": no}
               for n, d, det, e, v, no in resultados],
              open("/tmp/hpf-gate-mutacion.json", "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
