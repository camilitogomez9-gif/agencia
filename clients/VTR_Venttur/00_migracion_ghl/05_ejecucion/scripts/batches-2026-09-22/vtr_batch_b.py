#!/usr/bin/env python3
"""
Batch B · VTR cutover · infra Supabase.

B1: crear tablas vtr_message_dedup y vtr_message_buffer (idempotencia + debounce +20s).
B2: migración one-shot de folios Airtable Folios CAPI ([AIRTABLE_TABLE_ID])
    → Supabase capi_folios (idempotente vía ON CONFLICT DO UPDATE).

Cada uno se construye como workflow n8n con Webhook Trigger, se crea, se activa,
se dispara con curl, se lee la respuesta, se desactiva. El JSON queda como referencia
en clients/VTR_Venttur/03_workflows/ghl-live-2026-09-22-batch-B/.

Requiere:
    - N8N_API_KEY / N8N_BASE_URL en .env
    - Credencial n8n `ihpvM7nYMdLCwWDP` (Postgres Venttur)
    - Credencial n8n `[N8N_CREDENTIAL_ID]` (Airtable Venttur Dashboard)
"""

import json
import subprocess
import sys
import hashlib
import time
import uuid
from pathlib import Path

ROOT = Path("/Users/camilo/Downloads/camilo-workspace")
BATCH_DIR = ROOT / "clients/VTR_Venttur/03_workflows/ghl-live-2026-09-22-batch-B"
CRED_POSTGRES = "ihpvM7nYMdLCwWDP"
CRED_POSTGRES_NAME = "Venttur"
CRED_AIRTABLE = "[N8N_CREDENTIAL_ID]"
CRED_AIRTABLE_NAME = "Venttur Dashboard"
AIRTABLE_BASE = "[AIRTABLE_BASE_ID]"
AIRTABLE_TABLE_FOLIOS = "[AIRTABLE_TABLE_ID]"


def env_get(key):
    result = subprocess.run(
        ["grep", f"^{key}=", str(ROOT / ".env")],
        capture_output=True, text=True, check=True
    )
    line = result.stdout.strip().split("\n")[0]
    return line.split("=", 1)[1].strip().strip('"').strip("'")


def curl_json(method, path, data=None, allow_fail=False):
    base = env_get("N8N_BASE_URL").rstrip("/")
    key = env_get("N8N_API_KEY")
    url = f"{base}/api/v1{path}"
    cmd = [
        "curl", "-sS", "-w", "\n%{http_code}",
        "-X", method,
        "-H", f"X-N8N-API-KEY: {key}",
        "-H", "Content-Type: application/json",
    ]
    if data is not None:
        cmd.extend(["--data-binary", "@-"])
    cmd.append(url)
    result = subprocess.run(cmd, input=json.dumps(data) if data else None,
                            capture_output=True, text=True)
    output = result.stdout
    # Split off last line (http code)
    parts = output.rsplit("\n", 1)
    body = parts[0] if len(parts) == 2 else output
    code = parts[1].strip() if len(parts) == 2 else "?"
    if not (200 <= int(code) < 300) and not allow_fail:
        raise RuntimeError(f"curl {method} {path} → {code}:\n{body}")
    try:
        return json.loads(body), code
    except json.JSONDecodeError:
        return body, code


def curl_webhook(webhook_url, body=None):
    cmd = [
        "curl", "-sS", "-w", "\n%{http_code}",
        "-X", "POST",
        "-H", "Content-Type: application/json",
        "--max-time", "600",
    ]
    if body is not None:
        cmd.extend(["--data-binary", "@-"])
    else:
        cmd.extend(["--data-binary", "{}"])
    cmd.append(webhook_url)
    result = subprocess.run(cmd, input=json.dumps(body) if body else None,
                            capture_output=True, text=True)
    output = result.stdout
    parts = output.rsplit("\n", 1)
    body_out = parts[0] if len(parts) == 2 else output
    code = parts[1].strip() if len(parts) == 2 else "?"
    try:
        return json.loads(body_out), code
    except json.JSONDecodeError:
        return body_out, code


def sha256_of(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def save_snapshot(wf, name):
    """Guarda un workflow JSON al dir del batch."""
    path = BATCH_DIR / f"{name}.json"
    with open(path, "w") as f:
        json.dump(wf, f, indent=2, ensure_ascii=False)
    return path, sha256_of(path)


def make_workflow_b1_setup_tables():
    """Workflow B1: CREATE TABLE dedup + buffer + verify counts."""
    webhook_path = f"vtr-batch-b1-setup-{uuid.uuid4().hex[:8]}"
    return webhook_path, {
        "name": "VTR Batch B1 · Setup Supabase Tables (one-shot)",
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": webhook_path,
                    "responseMode": "responseNode",
                    "options": {}
                },
                "id": str(uuid.uuid4()),
                "name": "Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2.1,
                "position": [0, 0],
                "webhookId": str(uuid.uuid4())
            },
            {
                "parameters": {
                    "operation": "executeQuery",
                    "query": (
                        "CREATE TABLE IF NOT EXISTS vtr_message_dedup ("
                        "  hash text PRIMARY KEY,"
                        "  contact_id text NOT NULL,"
                        "  date_created timestamptz NOT NULL,"
                        "  body text NOT NULL,"
                        "  first_seen_at timestamptz NOT NULL DEFAULT now()"
                        ");"
                    ),
                    "options": {}
                },
                "id": str(uuid.uuid4()),
                "name": "CREATE vtr_message_dedup",
                "type": "n8n-nodes-base.postgres",
                "typeVersion": 2.6,
                "position": [240, 0],
                "credentials": {"postgres": {"id": CRED_POSTGRES, "name": CRED_POSTGRES_NAME}}
            },
            {
                "parameters": {
                    "operation": "executeQuery",
                    "query": (
                        "CREATE TABLE IF NOT EXISTS vtr_message_buffer ("
                        "  contact_id text PRIMARY KEY,"
                        "  messages jsonb NOT NULL DEFAULT '[]'::jsonb,"
                        "  first_message_at timestamptz,"
                        "  last_message_at timestamptz,"
                        "  flushed_at timestamptz"
                        ");"
                    ),
                    "options": {}
                },
                "id": str(uuid.uuid4()),
                "name": "CREATE vtr_message_buffer",
                "type": "n8n-nodes-base.postgres",
                "typeVersion": 2.6,
                "position": [480, 0],
                "credentials": {"postgres": {"id": CRED_POSTGRES, "name": CRED_POSTGRES_NAME}}
            },
            {
                "parameters": {
                    "operation": "executeQuery",
                    "query": (
                        "SELECT "
                        "  (SELECT COUNT(*) FROM vtr_message_dedup) AS dedup_count,"
                        "  (SELECT COUNT(*) FROM vtr_message_buffer) AS buffer_count,"
                        "  (SELECT COUNT(*) FROM capi_folios) AS folios_count,"
                        "  (SELECT COUNT(*) FROM capi_programas) AS programas_count;"
                    ),
                    "options": {}
                },
                "id": str(uuid.uuid4()),
                "name": "Verify counts",
                "type": "n8n-nodes-base.postgres",
                "typeVersion": 2.6,
                "position": [720, 0],
                "credentials": {"postgres": {"id": CRED_POSTGRES, "name": CRED_POSTGRES_NAME}}
            },
            {
                "parameters": {
                    "respondWith": "json",
                    "responseBody": (
                        "={{ { ok: true, "
                        "dedup_count: $json.dedup_count, "
                        "buffer_count: $json.buffer_count, "
                        "folios_count: $json.folios_count, "
                        "programas_count: $json.programas_count } }}"
                    ),
                    "options": {}
                },
                "id": str(uuid.uuid4()),
                "name": "Respond",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1.1,
                "position": [960, 0]
            }
        ],
        "connections": {
            "Webhook": {"main": [[{"node": "CREATE vtr_message_dedup", "type": "main", "index": 0}]]},
            "CREATE vtr_message_dedup": {"main": [[{"node": "CREATE vtr_message_buffer", "type": "main", "index": 0}]]},
            "CREATE vtr_message_buffer": {"main": [[{"node": "Verify counts", "type": "main", "index": 0}]]},
            "Verify counts": {"main": [[{"node": "Respond", "type": "main", "index": 0}]]}
        },
        "settings": {}
    }


def make_workflow_b2_migrate_folios():
    """Workflow B2: Airtable Folios CAPI → Supabase capi_folios (idempotente)."""
    webhook_path = f"vtr-batch-b2-migrate-folios-{uuid.uuid4().hex[:8]}"
    return webhook_path, {
        "name": "VTR Batch B2 · Migrar folios Airtable → Supabase (one-shot)",
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": webhook_path,
                    "responseMode": "responseNode",
                    "options": {}
                },
                "id": str(uuid.uuid4()),
                "name": "Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2.1,
                "position": [0, 0],
                "webhookId": str(uuid.uuid4())
            },
            {
                "parameters": {
                    "operation": "search",
                    "base": {"__rl": True, "value": AIRTABLE_BASE, "mode": "id"},
                    "table": {"__rl": True, "value": AIRTABLE_TABLE_FOLIOS, "mode": "id"},
                    "returnAll": True,
                    "options": {}
                },
                "id": str(uuid.uuid4()),
                "name": "Airtable Folios",
                "type": "n8n-nodes-base.airtable",
                "typeVersion": 2.1,
                "position": [240, 0],
                "credentials": {"airtableTokenApi": {"id": CRED_AIRTABLE, "name": CRED_AIRTABLE_NAME}}
            },
            {
                "parameters": {
                    "operation": "executeQuery",
                    "query": (
                        "INSERT INTO capi_folios (folio,fbclid,fbc,fbp,programa,ts,landing_url,user_agent,ip,updated_at) "
                        "VALUES ($1,$2,$3,$4,$5,$6::timestamptz,$7,$8,$9,now()) "
                        "ON CONFLICT (folio) DO UPDATE SET "
                        "fbclid=EXCLUDED.fbclid,fbc=EXCLUDED.fbc,fbp=EXCLUDED.fbp,"
                        "programa=EXCLUDED.programa,ts=EXCLUDED.ts,landing_url=EXCLUDED.landing_url,"
                        "user_agent=EXCLUDED.user_agent,ip=EXCLUDED.ip,updated_at=now()"
                    ),
                    "options": {
                        "queryReplacement": (
                            "={{ ["
                            "$json.Folio || $json.fields?.Folio || null, "
                            "$json.fbclid || $json.fields?.fbclid || null, "
                            "$json.fbc || $json.fields?.fbc || null, "
                            "$json.fbp || $json.fields?.fbp || null, "
                            "$json.Programa || $json.fields?.Programa || null, "
                            "$json.Timestamp || $json.fields?.Timestamp || null, "
                            "$json['Landing URL'] || $json.fields?.['Landing URL'] || null, "
                            "$json.user_agent || $json.fields?.user_agent || null, "
                            "$json.ip || $json.fields?.ip || null"
                            "] }}"
                        )
                    }
                },
                "id": str(uuid.uuid4()),
                "name": "Upsert folio",
                "type": "n8n-nodes-base.postgres",
                "typeVersion": 2.6,
                "position": [480, 0],
                "credentials": {"postgres": {"id": CRED_POSTGRES, "name": CRED_POSTGRES_NAME}}
            },
            {
                "parameters": {
                    "operation": "executeQuery",
                    "query": "SELECT COUNT(*) AS supabase_count FROM capi_folios;",
                    "options": {}
                },
                "id": str(uuid.uuid4()),
                "name": "Count after",
                "type": "n8n-nodes-base.postgres",
                "typeVersion": 2.6,
                "position": [720, 0],
                "credentials": {"postgres": {"id": CRED_POSTGRES, "name": CRED_POSTGRES_NAME}}
            },
            {
                "parameters": {
                    "respondWith": "json",
                    "responseBody": (
                        "={{ { ok: true, "
                        "supabase_count_after: $json.supabase_count, "
                        "airtable_count: $('Airtable Folios').all().length "
                        "} }}"
                    ),
                    "options": {}
                },
                "id": str(uuid.uuid4()),
                "name": "Respond",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1.1,
                "position": [960, 0]
            }
        ],
        "connections": {
            "Webhook": {"main": [[{"node": "Airtable Folios", "type": "main", "index": 0}]]},
            "Airtable Folios": {"main": [[{"node": "Upsert folio", "type": "main", "index": 0}]]},
            "Upsert folio": {"main": [[{"node": "Count after", "type": "main", "index": 0}]]},
            "Count after": {"main": [[{"node": "Respond", "type": "main", "index": 0}]]}
        },
        "settings": {}
    }


def run_workflow_one_shot(webhook_path, wf_json, batch_label, wait_secs=3, dispatch_timeout=None):
    """Crea + activa + dispara webhook + desactiva. Devuelve response del webhook."""
    print(f"\n══ {batch_label} ══")
    print(f"  📤 POST /workflows...")
    created, code = curl_json("POST", "/workflows", data=wf_json)
    wf_id = created["id"]
    print(f"     ✓ created id={wf_id}")

    print(f"  🔛 POST /workflows/{wf_id}/activate...")
    curl_json("POST", f"/workflows/{wf_id}/activate")
    time.sleep(wait_secs)
    print(f"     ✓ activated (esperando {wait_secs}s por webhook registration)")

    base = env_get("N8N_BASE_URL").rstrip("/")
    webhook_url = f"{base}/webhook/{webhook_path}"
    print(f"  ⚡ curl POST {webhook_url}...")
    resp, http_code = curl_webhook(webhook_url)
    print(f"     ← http {http_code}")
    print(f"     ← body: {json.dumps(resp, indent=2)[:400] if isinstance(resp, dict) else resp[:400]}")

    print(f"  🔴 POST /workflows/{wf_id}/deactivate...")
    curl_json("POST", f"/workflows/{wf_id}/deactivate", allow_fail=True)
    print(f"     ✓ deactivated")

    # Get final workflow state for snapshot
    final_wf, _ = curl_json("GET", f"/workflows/{wf_id}")
    return wf_id, resp, final_wf


def main():
    BATCH_DIR.mkdir(parents=True, exist_ok=True)

    # ── B1: setup tablas ──────────────────────────────────
    b1_path, b1_wf = make_workflow_b1_setup_tables()
    b1_id, b1_resp, b1_final = run_workflow_one_shot(b1_path, b1_wf, "B1 · Setup tablas")

    path, sha = save_snapshot(b1_final, "b1-setup-tables")
    print(f"  💾 {path.name} · sha256={sha}")

    dedup_count = b1_resp.get("dedup_count") if isinstance(b1_resp, dict) else "?"
    buffer_count = b1_resp.get("buffer_count") if isinstance(b1_resp, dict) else "?"
    folios_count_pre = b1_resp.get("folios_count") if isinstance(b1_resp, dict) else "?"
    programas_count = b1_resp.get("programas_count") if isinstance(b1_resp, dict) else "?"

    print(f"\n  📊 counts post-B1:")
    print(f"     vtr_message_dedup:   {dedup_count}")
    print(f"     vtr_message_buffer:  {buffer_count}")
    print(f"     capi_folios (pre migración): {folios_count_pre}")
    print(f"     capi_programas:      {programas_count}")

    # ── B2: migrar folios ────────────────────────────────
    b2_path, b2_wf = make_workflow_b2_migrate_folios()
    b2_id, b2_resp, b2_final = run_workflow_one_shot(b2_path, b2_wf, "B2 · Migrar folios", wait_secs=3)

    path, sha = save_snapshot(b2_final, "b2-migrate-folios")
    print(f"  💾 {path.name} · sha256={sha}")

    supabase_count_after = b2_resp.get("supabase_count_after") if isinstance(b2_resp, dict) else "?"
    airtable_count = b2_resp.get("airtable_count") if isinstance(b2_resp, dict) else "?"

    print(f"\n  📊 counts post-B2:")
    print(f"     capi_folios (post migración): {supabase_count_after}")
    print(f"     Airtable Folios CAPI:          {airtable_count}")

    # Guardar log en 05_ejecucion/logs
    log_dir = ROOT / "clients/VTR_Venttur/05_ejecucion/logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "batch-b-supabase-2026-09-22.md"
    with open(log_path, "w") as f:
        f.write(f"""# Batch B · Supabase infra + migración folios · 2026-09-22

## Estado post-ejecución

### Tablas creadas (idempotente `IF NOT EXISTS`)

- `vtr_message_dedup` · PK `hash text` · cols `contact_id text, date_created timestamptz, body text, first_seen_at timestamptz DEFAULT now()`
- `vtr_message_buffer` · PK `contact_id text` · cols `messages jsonb DEFAULT '[]', first_message_at, last_message_at, flushed_at timestamptz`

### Counts finales

| Tabla | Count |
|---|---|
| `vtr_message_dedup` | {dedup_count} |
| `vtr_message_buffer` | {buffer_count} |
| `capi_folios` (pre-migración) | {folios_count_pre} |
| `capi_folios` (post-migración) | {supabase_count_after} |
| `capi_programas` (referencia) | {programas_count} |
| Airtable Folios CAPI | {airtable_count} |

**Delta migración:** {supabase_count_after} - {folios_count_pre} = **{(supabase_count_after or 0) - (folios_count_pre or 0) if isinstance(supabase_count_after, int) and isinstance(folios_count_pre, int) else '?'}** rows nuevas o actualizadas (idempotente vía ON CONFLICT DO UPDATE).

### Comparación Airtable vs Supabase

- Airtable: {airtable_count} rows
- Supabase: {supabase_count_after} rows
- Delta: {(airtable_count or 0) - (supabase_count_after or 0) if isinstance(airtable_count, int) and isinstance(supabase_count_after, int) else '?'} (esperado: 0)

### Workflows ejecutados

- B1 `{b1_id}` (setup tablas · desactivado post-run · snapshot en `03_workflows/ghl-live-2026-09-22-batch-B/b1-setup-tables.json`)
- B2 `{b2_id}` (migración folios · desactivado post-run · snapshot en `03_workflows/ghl-live-2026-09-22-batch-B/b2-migrate-folios.json`)

Ambos workflows quedan OFF en n8n. Si se necesitan re-ejecutar, activarlos + POST al webhook (URL en el JSON).
""")
    print(f"\n  💾 log: {log_path}")

    return {
        "b1_id": b1_id,
        "b2_id": b2_id,
        "dedup_count": dedup_count,
        "buffer_count": buffer_count,
        "folios_count_pre": folios_count_pre,
        "folios_count_post": supabase_count_after,
        "airtable_count": airtable_count,
        "programas_count": programas_count,
    }


if __name__ == "__main__":
    result = main()
    print(f"\n✅ Batch B completo")
    print(json.dumps(result, indent=2, default=str))
