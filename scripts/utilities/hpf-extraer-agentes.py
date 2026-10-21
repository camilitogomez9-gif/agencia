#!/usr/bin/env python3
"""
HPF · L7 — Extrae los agentes del grafo congelado, con hash.

La regla del plan es "prompts byte-exactos del grafo congelado". Sin un hash eso es
una aspiración; con hash es verificable. Cada prompt sale a un .md propio y el
manifiesto guarda su sha256 + el modelo, temperatura, memoria, tools y parser.

El historial de este cliente tiene un "paste parcial" de prompt que costó semanas
(ver guia-fix-minimo-cilindros-2026-07-15.md): se pegó sólo un fragmento y nadie lo
notó porque el prompt ya referenciaba la sección faltante. `--verificar` existe para
que eso no pueda repetirse en silencio.

    python3 scripts/utilities/hpf-extraer-agentes.py            # extrae
    python3 scripts/utilities/hpf-extraer-agentes.py --verificar # re-chequea hashes
"""
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BASE = REPO / "clients/HPF_HappyFlops/03_workflows/base-prod-2026-08-06/main-happy-flops.json"
OUT = REPO / "clients/HPF_HappyFlops/04_agents/base-prod-2026-08-06"
MANIF = OUT / "MANIFIESTO.json"

SLUG = {
    "AI Agent": "router",
    "AI Agent Starter": "starter",
    "AI Agent Main Image": "main-image",
    "AI Agent Products": "products",
    "AI Agent Recolector": "recolector",
    "AI Agent Recolector1": "recolector1-imagen",
    "AI Agent Recolector2": "recolector2-huerfano",
    "AI Agent Recolector3": "recolector3-huerfano",
    "AI Agent Starter1": "starter1-huerfano",
}


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def alcanzables(d):
    """Nodos alcanzables desde el webhook por conexiones main."""
    conns = d["connections"]
    seen, stack = set(), ["New_Message"]
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        for br in conns.get(cur, {}).get("main", []) or []:
            for t in (br or []):
                stack.append(t["node"])
    return seen


def sub_conectados(d, agente):
    """Qué modelo / memoria / tools / parser cuelgan de este agente."""
    out = {"modelo": None, "memoria": None, "tools": [], "parser": None}
    for src, c in d["connections"].items():
        for tipo, brs in c.items():
            if tipo == "main":
                continue
            for br in (brs or []):
                for t in (br or []):
                    if t["node"] != agente:
                        continue
                    if tipo == "ai_languageModel":
                        out["modelo"] = src
                    elif tipo == "ai_memory":
                        out["memoria"] = src
                    elif tipo == "ai_tool":
                        out["tools"].append(src)
                    elif tipo == "ai_outputParser":
                        out["parser"] = src
    out["tools"].sort()
    return out


def main():
    verificar = "--verificar" in sys.argv
    d = json.loads(BASE.read_text())
    N = {n["name"]: n for n in d["nodes"]}
    vivos = alcanzables(d)
    OUT.mkdir(parents=True, exist_ok=True)

    manif, drift = {}, []
    prev = json.loads(MANIF.read_text()) if (verificar and MANIF.exists()) else {}

    # ── agentes langchain
    for nombre, nodo in N.items():
        if not nodo["type"].endswith("langchain.agent"):
            continue
        p = nodo["parameters"]
        sysmsg = (p.get("options") or {}).get("systemMessage") or ""
        conex = sub_conectados(d, nombre)
        mod = N.get(conex["modelo"] or "", {})
        mp = mod.get("parameters", {})
        slug = SLUG.get(nombre, nombre.lower().replace(" ", "-"))
        e = {
            "nodo": nombre, "alcanzable": nombre in vivos,
            "chars": len(sysmsg), "sha256": sha(sysmsg),
            "prompt_usuario": p.get("text"),
            "modelo_nodo": conex["modelo"],
            "modelo": (mp.get("model") or {}).get("value") if isinstance(mp.get("model"), dict) else mp.get("model"),
            "temperature": (mp.get("options") or {}).get("temperature"),
            "memoria": conex["memoria"], "tools": conex["tools"], "parser": conex["parser"],
            "returnIntermediateSteps": (p.get("options") or {}).get("returnIntermediateSteps"),
            "archivo": f"agente-{slug}.md",
        }
        manif[nombre] = e
        if verificar and nombre in prev:
            if prev[nombre]["sha256"] != e["sha256"]:
                drift.append(f"{nombre}: sha256 cambió "
                             f"({prev[nombre]['chars']} → {e['chars']} chars)")
        elif not verificar:
            (OUT / e["archivo"]).write_text(sysmsg, encoding="utf-8")

    # ── nodos LLM sueltos (canonicalizador, gate, splitter, visión, whisper)
    for nombre, nodo in N.items():
        if not nodo["type"].endswith("langchain.openAi"):
            continue
        p = nodo["parameters"]
        # El prompt no vive en el mismo lado según el resource: los de chat lo tienen en
        # messages.values[].content; los de `image/analyze` en `text`. Extraer del lugar
        # equivocado devuelve vacío sin fallar — y "byte-exacto" de nada no es nada.
        msgs = ((p.get("messages") or {}).get("values")) or []
        texto = "\n\n---\n\n".join(str(m.get("content", "")) for m in msgs)
        if not texto and p.get("text"):
            texto = str(p["text"])
        slug = nombre.lower().replace(" ", "-").replace("/", "-")
        e = {
            "nodo": nombre, "alcanzable": nombre in vivos,
            "tipo": f"{p.get('resource', 'chat')}/{p.get('operation', 'complete')}",
            "modelo": (p.get("modelId") or {}).get("value") if isinstance(p.get("modelId"), dict) else p.get("modelId"),
            "jsonOutput": (p.get("options") or {}).get("jsonOutput"),
            "chars": len(texto), "sha256": sha(texto),
            "archivo": f"llm-{slug}.md",
        }
        if not texto.strip():
            # whisper no lleva prompt; cualquier otro con 0 chars es un bug de extracción
            e["sin_prompt"] = True
            e["archivo"] = None
            if p.get("resource") != "audio":
                raise SystemExit(f"❌ {nombre}: 0 chars extraídos y no es audio — "
                                 f"revisar de qué parámetro sale el prompt")
        manif[nombre] = e
        if verificar and nombre in prev:
            if prev[nombre]["sha256"] != e["sha256"]:
                drift.append(f"{nombre}: sha256 cambió")
        elif not verificar and texto.strip():
            (OUT / e["archivo"]).write_text(texto, encoding="utf-8")

    if verificar:
        if drift:
            print("🔴 DRIFT en los prompts extraídos:")
            for x in drift:
                print("   ", x)
            sys.exit(1)
        print(f"✅ Sin drift: {len(manif)} prompts idénticos al manifiesto.")
        return

    MANIF.write_text(json.dumps(manif, indent=2, ensure_ascii=False), encoding="utf-8")

    ags = {k: v for k, v in manif.items() if "modelo_nodo" in v}
    print(f"{'agente':26s} {'alc':4s} {'chars':>7s} {'modelo':14s} {'temp':>5s} tools")
    for k, v in sorted(ags.items(), key=lambda x: -x[1]["chars"]):
        print(f"{k:26s} {'sí' if v['alcanzable'] else 'NO':4s} {v['chars']:7d} "
              f"{str(v['modelo']):14s} {str(v['temperature']):>5s} "
              f"{','.join(t.replace('ATENCION_PERSONALIZADA', 'AP') for t in v['tools']) or '—'}")
    llms = {k: v for k, v in manif.items() if "modelo_nodo" not in v}
    print(f"\n{'nodo LLM':26s} {'alc':4s} {'chars':>7s} {'modelo':14s} tipo")
    for k, v in sorted(llms.items(), key=lambda x: -x[1]["chars"]):
        print(f"{k:26s} {'sí' if v['alcanzable'] else 'NO':4s} {v['chars']:7d} "
              f"{str(v['modelo']):14s} {v['tipo']}")
    print(f"\n→ {OUT.relative_to(REPO)}  ({len(manif)} prompts)")


if __name__ == "__main__":
    main()
