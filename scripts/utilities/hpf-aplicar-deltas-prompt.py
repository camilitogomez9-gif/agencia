#!/usr/bin/env python3
"""
HPF · capa de deltas sobre los prompts congelados.

POR QUÉ EXISTE
`clients/HPF_HappyFlops/04_agents/base-prod-2026-08-06/*.md` es la copia CONGELADA de los
prompts de producción de Kommo, verificada por sha256 contra `MANIFIESTO.json`. Es la base
del protocolo de paridad de la migración: sirve justamente para poder demostrar que el bot
nuevo dice lo mismo que el viejo. Editarla a mano destruye esa garantía y deja el repo sin
forma de distinguir "divergencia deliberada" de "se nos escapó algo".

Los cambios que pidió Oscar en la reunión del 2026-08-11 SON divergencias deliberadas. Así
que la base no se toca: cada cambio vive en su propio archivo de delta, con el anchor
literal, el reemplazo y la cita de la reunión que lo justifica. El prompt que se deploya es
`base + deltas`, recomputable en cualquier momento, y cada delta se puede revertir solo.

USO
    hpf-aplicar-deltas-prompt.py --list                 # qué deltas hay y a qué prompt van
    hpf-aplicar-deltas-prompt.py --check                # ¿los anchors siguen matcheando?
    hpf-aplicar-deltas-prompt.py --diff products        # ver el resultado
    hpf-aplicar-deltas-prompt.py --deploy               # componer y subir a W6 vivo
    hpf-aplicar-deltas-prompt.py --deploy --only products

FORMATO DE UN DELTA  (04_agents/deltas-oscar-2026-08-11/NN-slug.json)
{
  "prompt": "products",                       // clave de PROMPTS, abajo
  "item_reunion": "1",                        // qué punto de la reunión resuelve
  "descripcion": "negritas y emojis...",
  "cita_oscar": "es muy importante aquí en México señalar...",
  "ediciones": [ {"anchor": "...", "reemplazo": "...", "motivo": "..."} ]
}
El anchor tiene que aparecer EXACTAMENTE UNA VEZ en el prompt base ya compuesto con los
deltas anteriores (se aplican en orden alfabético de archivo). Si no, aborta sin deployar.
"""
import argparse
import difflib
import hashlib
import importlib.util
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
BASE = REPO / "clients/HPF_HappyFlops/04_agents/base-prod-2026-08-06"
DELTAS = REPO / "clients/HPF_HappyFlops/04_agents/deltas-oscar-2026-08-11"

_spec = importlib.util.spec_from_file_location(
    "hpfdeploy", pathlib.Path(__file__).parent / "hpf-deploy-workflow.py")
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)

# clave -> (archivo base, nodo de W6 donde vive el systemMessage)
PROMPTS = {
    "router":     ("agente-router.md",     "Router"),
    "starter":    ("agente-starter.md",    "Starter"),
    "main-image": ("agente-main-image.md", "Main Image"),
    "products":   ("agente-products.md",   "Products"),
    "recolector": ("agente-recolector.md", "Recolector"),
}


def cargar_deltas(solo=None):
    """solo: lista de prefijos de archivo ('02','04') para aplicar un subconjunto.

    Hace falta porque el alcance aprobado de un ciclo puede ser menor que lo que hay en
    disco: el 14/8 se aprobaron los puntos 2,3,6,7,8 y quedaron fuera los deltas del saludo
    (01, 03) y de la pantufla (07), que ya están resueltos por nodo. Sin este filtro, un
    --deploy aplicaría de más y metería cambios que nadie pidió — justo lo que hay que evitar.
    """
    if not DELTAS.exists():
        return {}
    por_prompt = {}
    for p in sorted(DELTAS.glob("*.json")):
        if solo and not any(p.name.startswith(s) for s in solo):
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        d["_archivo"] = p.name
        por_prompt.setdefault(d["prompt"], []).append(d)
    return por_prompt


def componer(clave, deltas, estricto=True):
    """Devuelve (texto_final, informe). informe = lista de (delta, edicion, ok, detalle)."""
    arch, _ = PROMPTS[clave]
    txt = (BASE / arch).read_text(encoding="utf-8")
    informe = []
    for d in deltas:
        for i, ed in enumerate(d["ediciones"]):
            n = txt.count(ed["anchor"])
            if n == 1:
                txt = txt.replace(ed["anchor"], ed["reemplazo"])
                informe.append((d["_archivo"], i, True, "aplicado"))
            elif n == 0 and ed["reemplazo"] in txt:
                informe.append((d["_archivo"], i, True, "ya estaba aplicado (idempotente)"))
            else:
                informe.append((d["_archivo"], i, False,
                                f"el anchor aparece {n} veces, tiene que ser 1"))
                if estricto:
                    return txt, informe
    return txt, informe


def imprimir_informe(clave, informe):
    ok = all(r[2] for r in informe)
    for arch, i, bien, det in informe:
        print(f"     {'✓' if bien else '✗'} {arch} · edición {i}: {det}")
    return ok


def deployar(compuestos):
    """Un solo PUT a W6 con los systemMessage indicados, y relectura para confirmar."""
    w = D.bajar("W6")
    idx = {n["name"]: n for n in w["nodes"]}
    for clave, txt in compuestos.items():
        nodo = PROMPTS[clave][1]
        if nodo not in idx:
            sys.exit(f"❌ el nodo «{nodo}» no existe en W6 vivo")
        idx[nodo]["parameters"].setdefault("options", {})["systemMessage"] = txt
        print(f"   → {nodo}: {len(txt)} chars")
    D.subir("W6", w)

    v = D.bajar("W6")
    vidx = {n["name"]: n for n in v["nodes"]}
    bien = True
    for clave, txt in compuestos.items():
        nodo = PROMPTS[clave][1]
        real = vidx[nodo]["parameters"].get("options", {}).get("systemMessage", "")
        if real == txt:
            print(f"   ✅ {nodo} confirmado en el vivo ({len(real)} chars)")
        else:
            bien = False
            print(f"   ❌ {nodo} no coincide (vivo {len(real)} vs esperado {len(txt)})")
    if len(v["nodes"]) != len(w["nodes"]):
        bien = False
        print(f"   ❌ cambió la cantidad de nodos: {len(w['nodes'])} → {len(v['nodes'])}")
    return bien


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--diff", metavar="PROMPT")
    ap.add_argument("--deploy", action="store_true")
    ap.add_argument("--revert", action="store_true",
                    help="deploya la base CONGELADA sin deltas: deshace en el vivo los "
                         "cambios de prompt de la reunión. Los deltas quedan en disco, "
                         "así que --deploy los vuelve a aplicar.")
    ap.add_argument("--only", metavar="PROMPT")
    ap.add_argument("--deltas", metavar="02,04,06",
                    help="aplica SOLO los deltas cuyo archivo empieza con estos prefijos. "
                         "Sirve cuando el alcance aprobado es menor que lo que hay en disco.")
    a = ap.parse_args()

    solo = [s.strip() for s in (a.deltas or "").split(",") if s.strip()] or None
    porp = cargar_deltas(solo)
    if not porp:
        sys.exit(f"no hay deltas en {DELTAS.relative_to(REPO)}"
                 + (f" que empiecen con {solo}" if solo else ""))
    if solo:
        aplicados = sorted(d["_archivo"] for ds in porp.values() for d in ds)
        print(f"alcance: {len(aplicados)} delta(s) — {', '.join(aplicados)}")

    if a.list:
        for clave, ds in sorted(porp.items()):
            print(f"\n{clave}  ({PROMPTS[clave][0]} → nodo «{PROMPTS[clave][1]}» de W6)")
            for d in ds:
                print(f"   {d['_archivo']}  item {d.get('item_reunion','?')}  "
                      f"{len(d['ediciones'])} edición(es)")
                print(f"      {d.get('descripcion','')}")
        return

    if a.revert:
        compuestos = {}
        for clave in sorted(porp):
            if a.only and clave != a.only:
                continue
            txt = (BASE / PROMPTS[clave][0]).read_text(encoding="utf-8")
            compuestos[clave] = txt
            print(f"── {clave}: vuelve a la base congelada · {len(txt)} chars · "
                  f"sha {hashlib.sha256(txt.encode()).hexdigest()[:16]}")
        bien = deployar(compuestos)
        print("✅ deltas revertidos en el vivo" if bien else "❌ NO verificado")
        sys.exit(0 if bien else 1)

    if a.check or a.deploy:
        todo_ok = True
        compuestos = {}
        for clave, ds in sorted(porp.items()):
            if a.only and clave != a.only:
                continue
            print(f"\n── {clave}")
            txt, informe = componer(clave, ds, estricto=False)
            ok = imprimir_informe(clave, informe)
            base_len = len((BASE / PROMPTS[clave][0]).read_text(encoding="utf-8"))
            print(f"     {base_len} → {len(txt)} chars · sha {hashlib.sha256(txt.encode()).hexdigest()[:16]}")
            todo_ok &= ok
            compuestos[clave] = txt
        if not todo_ok:
            sys.exit("\n❌ hay anchors que no matchean: no deployo nada")
        print("\n✅ todos los anchors matchean")
        if not a.deploy:
            return

        bien = deployar(compuestos)
        print("✅ deltas deployados y verificados" if bien else "❌ NO verificado")
        sys.exit(0 if bien else 1)

    if a.diff:
        clave = a.diff
        txt, informe = componer(clave, porp.get(clave, []), estricto=False)
        if not imprimir_informe(clave, informe):
            sys.exit("❌ anchors sin matchear")
        base = (BASE / PROMPTS[clave][0]).read_text(encoding="utf-8")
        for l in difflib.unified_diff(base.splitlines(), txt.splitlines(),
                                      "base", "base+deltas", lineterm="", n=2):
            print(l)
        return

    ap.print_help()


if __name__ == "__main__":
    main()
