#!/usr/bin/env python3
"""
Patch sys-agente-principal-v0.3.json → v0.4.json

Restaura el branch de testing (IF channel test? + Respond Test con body)
para que el smoke test del webhook pueda recibir el body con la respuesta
del agente. La rama solo se activa cuando channel == 'test'; producción
(ManyChat real) sigue intacta.

Cambios vs v0.3:
1. Re-agrega node "IF channel test?" (condición: $('Normalize Payload').channel == 'test')
2. Re-agrega node "Respond Test (con body)" (devuelve JSON con ai_msg_1/2/3)
3. Re-cablea Split Respuesta: → setCustomFields ManyChat  →  IF channel test?
4. IF channel test? rama true  → Respond Test (con body)  [terminal, body=JSON]
5. IF channel test? rama false → setCustomFields ManyChat → sendFlow → Respond to Webhook [producción]

Uso:
    python3 scripts/utilities/patch-sys-main-v0.4.py [INPUT] [OUTPUT]
"""

import json
import sys
import shutil
from pathlib import Path

HOME = Path.home()
DEFAULT_INPUT = HOME / "Downloads" / "sys-agente-principal-v0.3.json"
DEFAULT_OUTPUT = HOME / "Downloads" / "sys-agente-principal-v0.4.json"
REPO_COPY = HOME / "Downloads" / "camilo-workspace" / "clients" / "SYS_SistemasYSoluciones" / "03_workflows" / "sys-agente-principal-v0.4.json"

# Nodos a restaurar (copy-paste exacto de v0.2)
NODES_TO_RESTORE = [
    {
        "parameters": {
            "conditions": {
                "options": {
                    "caseSensitive": False,
                    "leftValue": "",
                    "typeValidation": "loose"
                },
                "conditions": [
                    {
                        "id": "test-channel-check",
                        "leftValue": "={{ $('Normalize Payload').first().json.channel }}",
                        "rightValue": "test",
                        "operator": {
                            "type": "string",
                            "operation": "equals"
                        }
                    }
                ],
                "combinator": "and"
            },
            "options": {}
        },
        "type": "n8n-nodes-base.if",
        "typeVersion": 2.2,
        "position": [816, 192],
        "id": "e51e0fba-058c-4a57-a0ac-ec9f1f63572d",
        "name": "IF channel test?"
    },
    {
        "parameters": {
            "respondWith": "json",
            "responseBody": "={{ JSON.stringify({ ok: true, raw: $('Split Respuesta').first().json.raw, ai_msg_1: $('Split Respuesta').first().json.ai_msg_1, ai_msg_2: $('Split Respuesta').first().json.ai_msg_2, ai_msg_3: $('Split Respuesta').first().json.ai_msg_3, ai_msg_count: $('Split Respuesta').first().json.ai_msg_count }) }}",
            "options": {
                "responseCode": 200
            }
        },
        "type": "n8n-nodes-base.respondToWebhook",
        "typeVersion": 1.1,
        "position": [992, 96],
        "id": "4e09820f-7c57-4306-854e-af2965c7817a",
        "name": "Respond Test (con body)"
    }
]


def patch_workflow(workflow: dict) -> dict:
    # ── 1. Agregar los 2 nodos restaurados ─────────────────────────────────
    existing_names = {n["name"] for n in workflow["nodes"]}
    added = []
    for node in NODES_TO_RESTORE:
        if node["name"] not in existing_names:
            workflow["nodes"].append(node)
            added.append(node["name"])
    print(f"  · Nodos restaurados: {added}")

    # ── 2. Re-cablear conexiones ───────────────────────────────────────────
    conn = workflow["connections"]

    # Split Respuesta: setCustomFields → IF channel test?
    conn["Split Respuesta"] = {
        "main": [[{"node": "IF channel test?", "type": "main", "index": 0}]]
    }

    # IF channel test? rama 0 (true → test) → Respond Test (con body)
    # IF channel test? rama 1 (false → prod) → setCustomFields ManyChat
    conn["IF channel test?"] = {
        "main": [
            [{"node": "Respond Test (con body)", "type": "main", "index": 0}],
            [{"node": "setCustomFields ManyChat", "type": "main", "index": 0}],
        ]
    }

    # Respond Test es terminal — no agregamos output

    print("  · Split Respuesta → IF channel test?")
    print("  · IF channel test? rama true → Respond Test (con body)")
    print("  · IF channel test? rama false → setCustomFields ManyChat")

    # ── 3. Bump versionId/name ─────────────────────────────────────────────
    workflow["name"] = "sys-agente-principal-v0.4"
    if "versionId" in workflow:
        workflow["versionId"] = "v0.4-restaura-testing-branch"
    if "id" in workflow:
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

    print("Aplicando patch v0.3 → v0.4:")
    wf = patch_workflow(wf)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as f:
        json.dump(wf, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Escrito: {output_path}")

    REPO_COPY.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(output_path, REPO_COPY)
    print(f"✅ Copia al repo: {REPO_COPY}")

    # Verificación: trazar cadena productiva (false branch) y testing (true branch)
    with output_path.open() as f:
        check = json.load(f)

    def trace(start, branch_idx_for_if):
        chain, seen, cur = [start], set(), start
        while cur and cur not in seen and len(chain) < 25:
            seen.add(cur)
            outs = check["connections"].get(cur, {}).get("main", [])
            if not outs:
                break
            node = next((n for n in check["nodes"] if n["name"] == cur), None)
            is_if = node and "if" in node.get("type", "").lower()
            idx = branch_idx_for_if if (is_if and len(outs) > 1) else 0
            if not outs[idx]:
                break
            cur = outs[idx][0].get("node")
            chain.append(cur)
        return chain

    print("\n🔍 Verificación:")
    print(f"  Cadena PRODUCCIÓN (IF→false): " + " → ".join(trace("Webhook (ManyChat)", 1)))
    print(f"  Cadena TESTING    (IF→true):  " + " → ".join(trace("Webhook (ManyChat)", 0)))


if __name__ == "__main__":
    main()
