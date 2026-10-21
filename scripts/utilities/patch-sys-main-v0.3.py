#!/usr/bin/env python3
"""
Patch sys-agente-principal-v0.2.json → v0.3.json

Cambios:
1. Activa attemptToConvertTypes=true y convertFieldsToString=true en TODOS los toolWorkflow nodes restantes
2. Elimina los nodos de testing: debug_echo, Respond Test (con body), IF channel test?
3. Re-cablea Webhook → Normalize Payload directamente (sin pasar por IF channel test?)
4. Limpia la cabecera "⚠️ DEBUG MODE TEMPORAL" del systemMessage del AI Agent
5. Elimina referencias a los nodos removidos en connections

Uso:
    python3 scripts/utilities/patch-sys-main-v0.3.py [INPUT] [OUTPUT]

Defaults:
    INPUT  = ~/Downloads/sys-agente-principal-v0.2.json
    OUTPUT = ~/Downloads/sys-agente-principal-v0.3.json (+ copia al repo)
"""

import json
import sys
import shutil
from pathlib import Path

HOME = Path.home()
DEFAULT_INPUT = HOME / "Downloads" / "sys-agente-principal-v0.2.json"
DEFAULT_OUTPUT = HOME / "Downloads" / "sys-agente-principal-v0.3.json"
REPO_COPY = HOME / "Downloads" / "camilo-workspace" / "clients" / "SYS_SistemasYSoluciones" / "03_workflows" / "sys-agente-principal-v0.3.json"

NODES_TO_REMOVE = {"debug_echo", "Respond Test (con body)", "IF channel test?"}

DEBUG_HEADER = (
    "\n---\n⚠️ DEBUG MODE TEMPORAL — Antes de invocar `consultar_aplicacion`, "
    "`buscar_equipo`, o `consultar_inventario_usados`, llamá PRIMERO a `debug_echo` "
    "con `raw_args` = JSON string conteniendo TODOS los args que pensás pasar a la "
    "tool real. Después invocá la tool real normalmente. Esto es solo para "
    "diagnóstico — no afecta tu comportamiento con el usuario, ni se lo "
    "menciones.\n---\n"
)


def patch_workflow(workflow: dict) -> dict:
    # ── 1. Filtrar nodos eliminados ─────────────────────────────────────────
    original_count = len(workflow["nodes"])
    workflow["nodes"] = [n for n in workflow["nodes"] if n["name"] not in NODES_TO_REMOVE]
    removed_count = original_count - len(workflow["nodes"])
    print(f"  · Nodos eliminados: {removed_count} (esperado: {len(NODES_TO_REMOVE)})")

    # ── 2. Activar attemptToConvertTypes + convertFieldsToString en toolWorkflow ─
    converted = 0
    for node in workflow["nodes"]:
        if node.get("type") == "@n8n/n8n-nodes-langchain.toolWorkflow":
            wi = node.get("parameters", {}).get("workflowInputs", {})
            if "attemptToConvertTypes" in wi or "convertFieldsToString" in wi:
                wi["attemptToConvertTypes"] = True
                wi["convertFieldsToString"] = True
                converted += 1
    print(f"  · toolWorkflow nodes con convertTypes activados: {converted}")

    # ── 3. Limpiar systemMessage del AI Agent ───────────────────────────────
    cleaned_prompt = False
    for node in workflow["nodes"]:
        if node.get("name") == "AI Agent":
            params = node.get("parameters", {})
            sm = params.get("options", {}).get("systemMessage") or params.get("systemMessage")
            if sm and DEBUG_HEADER in sm:
                new_sm = sm.replace(DEBUG_HEADER, "\n")
                if "options" in params and "systemMessage" in params.get("options", {}):
                    params["options"]["systemMessage"] = new_sm
                else:
                    params["systemMessage"] = new_sm
                cleaned_prompt = True
    print(f"  · systemMessage limpiado: {cleaned_prompt}")

    # ── 4. Re-cablear conexiones eliminando referencias a nodos removidos ───
    new_connections = {}
    for source_name, outputs in workflow.get("connections", {}).items():
        if source_name in NODES_TO_REMOVE:
            continue
        new_outputs = {}
        for slot, branches in outputs.items():
            new_branches = []
            for branch in branches:
                filtered = [conn for conn in branch if conn.get("node") not in NODES_TO_REMOVE]
                new_branches.append(filtered)
            new_outputs[slot] = new_branches
        new_connections[source_name] = new_outputs

    # ── 4b. Split Respuesta → setCustomFields ManyChat directo ─────────────
    # El flujo original era: AI Agent → Split Respuesta → IF channel test?
    #   ├─ true  → Respond Test (con body)        [testing branch — eliminada]
    #   └─ false → setCustomFields ManyChat       [producción]
    # Tras eliminar IF channel test?, hay que apuntar Split Respuesta
    # directo al path productivo (setCustomFields ManyChat).
    new_connections["Split Respuesta"] = {
        "main": [[{"node": "setCustomFields ManyChat", "type": "main", "index": 0}]]
    }
    print("  · Split Respuesta re-cableado → setCustomFields ManyChat (path productivo)")

    workflow["connections"] = new_connections

    # ── 5. Bump del nombre + versionId ──────────────────────────────────────
    workflow["name"] = "sys-agente-principal-v0.3"
    if "versionId" in workflow:
        workflow["versionId"] = "v0.3-attemptToConvertTypes-on-no-debug"
    if "id" in workflow:
        # nuevo id para forzar import como workflow nuevo si se desea
        # (si la agencia prefiere overwrite del existente, n8n lo maneja por nombre)
        del workflow["id"]

    return workflow


def main():
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT

    print(f"📥 Input:  {input_path}")
    print(f"📤 Output: {output_path}")
    print()

    with input_path.open() as f:
        wf = json.load(f)

    print(f"Aplicando patch a sys-agente-principal-v0.3:")
    wf = patch_workflow(wf)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as f:
        json.dump(wf, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Escrito: {output_path}")

    # Copia al repo
    REPO_COPY.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(output_path, REPO_COPY)
    print(f"✅ Copia al repo: {REPO_COPY}")

    # Verificación post-write
    with output_path.open() as f:
        check = json.load(f)
    tools = [n["name"] for n in check["nodes"] if n.get("type") == "@n8n/n8n-nodes-langchain.toolWorkflow"]
    print(f"\n🔍 Verificación post-patch:")
    print(f"  · Total nodos: {len(check['nodes'])}")
    print(f"  · toolWorkflow nodes ({len(tools)}): {sorted(tools)}")
    print(f"  · Nodos removidos detectados: {sum(1 for n in check['nodes'] if n['name'] in NODES_TO_REMOVE)} (esperado: 0)")

    all_converted = all(
        n["parameters"]["workflowInputs"].get("attemptToConvertTypes") is True
        and n["parameters"]["workflowInputs"].get("convertFieldsToString") is True
        for n in check["nodes"]
        if n.get("type") == "@n8n/n8n-nodes-langchain.toolWorkflow"
    )
    print(f"  · 100% toolWorkflow con convertTypes=true: {all_converted}")


if __name__ == "__main__":
    main()
