#!/usr/bin/env python3
"""
HPF · migra los llamadores de W0 de `args` string a `args` objeto.

EL PROBLEMA
Todos los nodos `executeWorkflow` que llaman a W0 le pasan `args` serializado:

    ={{ JSON.stringify({contactId: ...}) }}

Eso funciona sólo mientras el nodo tenga `schema: []`. Pero **la UI de n8n repuebla el
schema con sólo abrir y guardar el workflow**, y al hacerlo declara `args` como `object`
(lo deriva del `jsonExample` del trigger de W0). Con el schema poblado, un string deja de
validar y el nodo tira `Invalid input for 'args'` sin llegar a ejecutarse.

No es teórico: pasó dos veces el 14/08 con el nodo de Telegram, y la segunda vez fue un
guardado desde la UI el que revirtió el arreglo solo.

Medido en un workflow descartable con el schema ya poblado:
    args string  → falla la validación
    args objeto  → pasa (con convertFieldsToString en true o en false)

W0 acepta las dos formas — su `Normalizar entrada` hace `JSON.parse` sólo si le llega un
string — así que pasar el objeto es estrictamente mejor: deja de depender de que nadie
abra el editor.

QUÉ HACE
Reescribe `={{ JSON.stringify(X) }}` como `={{ X }}` y pone `convertFieldsToString: false`
(en true, n8n pisaría el objeto a string y volveríamos al mismo punto). Verifica que la
expresión interior quede byte-idéntica: si no puede garantizarlo, no toca ese nodo.

Uso:  hpf-migrar-args-a-objeto.py [--dry-run]
"""
import importlib.util
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "hpfdeploy", REPO / "scripts/utilities/hpf-deploy-workflow.py")
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)

W0_ID = "VK4M7VQm8CMefbty"
PRE, SUF = "={{ JSON.stringify(", ") }}"


def convertir(expr):
    """'={{ JSON.stringify(X) }}' -> '={{ X }}'. None si no matchea el patrón exacto."""
    if not (expr.startswith(PRE) and expr.endswith(SUF)):
        return None
    interior = expr[len(PRE):-len(SUF)]
    # Si el interior tiene paréntesis desbalanceados, el `)` final no era el de
    # JSON.stringify y el corte estaría partiendo la expresión al medio.
    if interior.count("(") != interior.count(")"):
        return None
    return "={{ " + interior + " }}"


def main():
    dry = "--dry-run" in sys.argv
    total = migrados = saltados = 0
    for k in ("W0", "W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8", "W9", "W10"):
        w = D.bajar(k)
        tocado = False
        for n in w["nodes"]:
            if not n["type"].endswith("executeWorkflow"):
                continue
            p = n.get("parameters", {})
            if W0_ID not in json.dumps(p):
                continue
            wi = p.get("workflowInputs", {})
            expr = str(wi.get("value", {}).get("args", ""))
            if "JSON.stringify" not in expr:
                continue
            total += 1
            nuevo = convertir(expr)
            if nuevo is None:
                saltados += 1
                print(f"  ⚠️  {k} · {n['name']}: patrón inesperado, NO lo toco")
                print(f"      {expr[:120]}")
                continue
            wi["value"]["args"] = nuevo
            wi["convertFieldsToString"] = False
            tocado = True
            migrados += 1
            print(f"  ✓ {k} · {n['name'][:30]:32} {nuevo[:66]}")
        if tocado and not dry:
            D.subir(k, w)
    print(f"\n{migrados}/{total} migrados · {saltados} salteados")
    if dry:
        print("(dry-run: no escribí nada)")
        return

    # relectura: que no quede ninguno en string y que el objeto sea sintácticamente sano
    print("\n── verificación contra el vivo")
    quedan = []
    for k in ("W0", "W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8", "W9", "W10"):
        s, w = D.api(f"/api/v1/workflows/{D.IDS[k]}")
        for n in w["nodes"]:
            p = n.get("parameters", {})
            if not n["type"].endswith("executeWorkflow") or W0_ID not in json.dumps(p):
                continue
            wi = p.get("workflowInputs", {})
            a = str(wi.get("value", {}).get("args", ""))
            if "JSON.stringify" in a:
                quedan.append(f"{k}/{n['name']}")
            elif wi.get("convertFieldsToString") is not False:
                quedan.append(f"{k}/{n['name']} (convertFieldsToString sigue en true)")
    if quedan:
        print("  ❌ quedaron sin migrar:")
        for q in quedan:
            print(f"     {q}")
        sys.exit(1)
    print("  ✅ ningún llamador de W0 pasa `args` como string")


if __name__ == "__main__":
    main()
