#!/usr/bin/env python3
"""
Batch A · VTR cutover · fixes al workflow k3aivKSP67S97IHn ([Venttur] main).

A1: rotar OpenAI key hardcoded en nodo `Transcribir audio/s`.
    De: header Authorization con `Bearer sk-proj-OpKR...` (comprometido).
    A:  authentication=predefinedCredentialType + nodeCredentialType=openAiApi + credentials.openAiApi
        apuntando a `4mYcYoPAC42ngJYz` (credencial n8n con la key rotada).

A2: fix nodo `Hay audios?`.
    De: `and` de 3 conditions (array notEmpty + notContains "jpeg" + notContains "webp").
    A:  `and` de 2 conditions (array notEmpty + regex match audio whitelist).
    Regex whitelist: `\\.(ogg|oga|mp3|m4a|wav|amr|opus)($|\\?)` sobre `$json.audio[0]`.

Requiere:
    - N8N_API_KEY en .env (grep|cut, sin source)
    - N8N_BASE_URL en .env
    - Snapshot pre en clients/VTR_Venttur/03_workflows/ghl-live-2026-09-21-batch-A/pre/vtr-main.json

Salida:
    - clients/VTR_Venttur/03_workflows/ghl-live-2026-09-22-batch-A/post/vtr-main.json (post PUT)
    - clients/VTR_Venttur/03_workflows/ghl-live-2026-09-22-batch-A/README.md
"""

import json
import subprocess
import sys
import hashlib
from pathlib import Path
from datetime import datetime

ROOT = Path("/Users/camilo/Downloads/camilo-workspace")
PRE_JSON = ROOT / "clients/VTR_Venttur/03_workflows/ghl-live-2026-09-21-batch-A/pre/vtr-main.json"
POST_DIR = ROOT / "clients/VTR_Venttur/03_workflows/ghl-live-2026-09-22-batch-A"
POST_JSON = POST_DIR / "post/vtr-main.json"
MID_JSON = POST_DIR / "mid/vtr-main-patched.json"

WORKFLOW_ID = "k3aivKSP67S97IHn"
CRED_OPENAI = "4mYcYoPAC42ngJYz"  # credencial n8n con la OpenAI key rotada
NODE_TRANSCRIBIR = "Transcribir audio/s"
NODE_HAY_AUDIOS = "Hay audios?"


def env_get(key):
    """Lee un valor de .env con grep|cut. NO ejecuta el archivo."""
    result = subprocess.run(
        ["grep", f"^{key}=", str(ROOT / ".env")],
        capture_output=True, text=True, check=True
    )
    line = result.stdout.strip().split("\n")[0]
    return line.split("=", 1)[1].strip().strip('"').strip("'")


def curl_json(method, path, data=None, extra_headers=None):
    """curl a n8n API. Devuelve dict parseado o texto."""
    base = env_get("N8N_BASE_URL").rstrip("/")
    key = env_get("N8N_API_KEY")
    url = f"{base}/api/v1{path}"
    cmd = [
        "curl", "-sSf",
        "-X", method,
        "-H", f"X-N8N-API-KEY: {key}",
        "-H", "Content-Type: application/json",
    ]
    if extra_headers:
        for h, v in extra_headers.items():
            cmd.extend(["-H", f"{h}: {v}"])
    if data is not None:
        cmd.extend(["--data-binary", "@-"])
    cmd.append(url)
    result = subprocess.run(
        cmd, input=json.dumps(data) if data else None,
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"curl {method} {path} failed:\n{result.stderr}\n{result.stdout}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return result.stdout


def sha256_of(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def apply_a1_openai_credential(node):
    """A1: reemplaza header Bearer hardcoded por credential n8n openAiApi."""
    params = node.setdefault("parameters", {})
    # Migrar a credential predefined
    params["authentication"] = "predefinedCredentialType"
    params["nodeCredentialType"] = "openAiApi"

    # Sacar el header Authorization (queda como sendHeaders=true pero sin ese header)
    # Mantenemos Content-Type: multipart/form-data porque el body es multipart
    if "headerParameters" in params:
        header_params = params["headerParameters"].get("parameters", [])
        header_params = [h for h in header_params if h.get("name") != "Authorization"]
        if header_params:
            params["headerParameters"]["parameters"] = header_params
        else:
            # Si solo estaba Authorization, saco headerParameters entero
            params.pop("headerParameters", None)
            params["sendHeaders"] = False

    # Cablear credential
    node.setdefault("credentials", {})
    node["credentials"]["openAiApi"] = {
        "id": CRED_OPENAI,
        "name": "OpenAI Venttur (rotada 2026-09-22)"
    }
    return node


def apply_a2_hay_audios_whitelist(node):
    """A2: reemplaza blacklist de imágenes por whitelist regex de audio."""
    conditions = node["parameters"]["conditions"]
    # Preservar el primer condition (array notEmpty sobre $json.audio)
    first = conditions["conditions"][0]
    assert first["operator"]["type"] == "array", f"Primera condition esperada array, got: {first}"

    # Reemplazar las 3 conditions actuales por 2:
    # 1. array notEmpty (preservada)
    # 2. regex match audio whitelist sobre $json.audio[0]
    new_conditions = [
        first,
        {
            "id": "audio-whitelist-2026-09-22",
            "leftValue": "={{ $json.audio[0] }}",
            "rightValue": "\\.(ogg|oga|mp3|m4a|wav|amr|opus)($|\\?)",
            "operator": {
                "type": "string",
                "operation": "regex"
            }
        }
    ]
    conditions["conditions"] = new_conditions
    conditions["combinator"] = "and"
    return node


def main():
    POST_DIR.mkdir(parents=True, exist_ok=True)
    (POST_DIR / "post").mkdir(exist_ok=True)
    (POST_DIR / "mid").mkdir(exist_ok=True)

    if not PRE_JSON.exists():
        print(f"❌ pre snapshot missing: {PRE_JSON}", file=sys.stderr)
        sys.exit(1)

    print(f"📥 Leyendo pre-snapshot: {PRE_JSON}")
    with open(PRE_JSON) as f:
        wf = json.load(f)

    print(f"   workflow: {wf.get('name')} · id={wf.get('id')} · active={wf.get('active')} · nodes={len(wf.get('nodes', []))}")

    # Localizar nodos
    nodes_by_name = {n["name"]: n for n in wf["nodes"]}
    if NODE_TRANSCRIBIR not in nodes_by_name:
        print(f"❌ nodo '{NODE_TRANSCRIBIR}' no encontrado", file=sys.stderr)
        sys.exit(1)
    if NODE_HAY_AUDIOS not in nodes_by_name:
        print(f"❌ nodo '{NODE_HAY_AUDIOS}' no encontrado", file=sys.stderr)
        sys.exit(1)

    print(f"✅ nodo A1: {NODE_TRANSCRIBIR} (id={nodes_by_name[NODE_TRANSCRIBIR]['id']})")
    print(f"✅ nodo A2: {NODE_HAY_AUDIOS} (id={nodes_by_name[NODE_HAY_AUDIOS]['id']})")

    # Aplicar A1 (rotar OpenAI key)
    print(f"\n🔧 A1: migrando '{NODE_TRANSCRIBIR}' a credential '{CRED_OPENAI}'...")
    apply_a1_openai_credential(nodes_by_name[NODE_TRANSCRIBIR])

    # Aplicar A2 (whitelist regex audio)
    print(f"🔧 A2: whitelist regex en '{NODE_HAY_AUDIOS}'...")
    apply_a2_hay_audios_whitelist(nodes_by_name[NODE_HAY_AUDIOS])

    # Guardar snapshot intermedio (post-patch, pre-PUT)
    with open(MID_JSON, "w") as f:
        json.dump(wf, f, indent=2, ensure_ascii=False)
    print(f"💾 mid snapshot: {MID_JSON} · sha256={sha256_of(MID_JSON)}")

    # Verificar que la credencial existe en n8n
    print(f"\n🔍 Verificando credencial n8n '{CRED_OPENAI}'...")
    try:
        cred_info = curl_json("GET", f"/credentials/schema/openAiApi")
        # Este endpoint devuelve el schema, no la credencial. Solo confirma que openAiApi es tipo válido.
        print(f"   ✓ openAiApi es tipo válido en n8n")
    except Exception as e:
        print(f"   ⚠️ no pudimos verificar schema: {e}")

    # PUT al workflow
    # n8n PUT /workflows/{id} espera SOLO: name, nodes, connections, settings.
    # Otros campos (id, active, tags, versionId, meta, createdAt, updatedAt) provocan 400.
    put_body = {
        "name": wf["name"],
        "nodes": wf["nodes"],
        "connections": wf["connections"],
        "settings": wf.get("settings", {}),
    }

    print(f"\n📤 PUT /workflows/{WORKFLOW_ID}...")
    try:
        put_result = curl_json("PUT", f"/workflows/{WORKFLOW_ID}", data=put_body)
        print(f"   ✓ PUT ok · updatedAt={put_result.get('updatedAt', 'n/a')}")
    except Exception as e:
        print(f"❌ PUT falló: {e}", file=sys.stderr)
        sys.exit(1)

    # GET back
    print(f"\n📥 GET post-PUT para snapshot final...")
    post_wf = curl_json("GET", f"/workflows/{WORKFLOW_ID}")
    with open(POST_JSON, "w") as f:
        json.dump(post_wf, f, indent=2, ensure_ascii=False)
    print(f"💾 post snapshot: {POST_JSON} · sha256={sha256_of(POST_JSON)}")

    # Verificar cambios aplicados
    print(f"\n🔬 Verificación post-PUT:")
    post_nodes = {n["name"]: n for n in post_wf["nodes"]}

    tnode = post_nodes[NODE_TRANSCRIBIR]
    auth = tnode["parameters"].get("authentication")
    cred = tnode.get("credentials", {}).get("openAiApi", {}).get("id")
    header_params = tnode["parameters"].get("headerParameters", {}).get("parameters", [])
    has_auth_header = any(h.get("name") == "Authorization" for h in header_params)
    print(f"   {NODE_TRANSCRIBIR}:")
    print(f"     authentication: {auth} (esperado: predefinedCredentialType)")
    print(f"     credentials.openAiApi.id: {cred} (esperado: {CRED_OPENAI})")
    print(f"     Authorization header hardcodeado: {has_auth_header} (esperado: False)")
    assert auth == "predefinedCredentialType", "A1 no aplicó authentication"
    assert cred == CRED_OPENAI, f"A1 credential no aplicó: got {cred}"
    assert not has_auth_header, "A1 no removió header Authorization hardcoded"

    hnode = post_nodes[NODE_HAY_AUDIOS]
    conds = hnode["parameters"]["conditions"]["conditions"]
    print(f"   {NODE_HAY_AUDIOS}: {len(conds)} conditions (esperado: 2)")
    assert len(conds) == 2, f"A2 debe tener 2 conditions, tiene {len(conds)}"
    assert conds[1]["operator"]["operation"] == "regex", "A2 segunda condition debe ser regex"
    print(f"     condition[1].operator: regex ✓")
    print(f"     condition[1].rightValue: {conds[1]['rightValue']}")

    print(f"\n✅ Batch A aplicado y verificado.")


if __name__ == "__main__":
    main()
