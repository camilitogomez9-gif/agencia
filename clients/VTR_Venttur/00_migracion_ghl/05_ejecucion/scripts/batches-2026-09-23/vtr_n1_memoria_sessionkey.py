#!/usr/bin/env python3
"""N1 (23/9): las conversaciones de la época ManyChat guardaron la memoria con session_id sólo dígitos
(`521XXXXXXXXXX`, a veces `52XXXXXXXXXX`); el stack nuevo usa `+521XXXXXXXXXX` (nsk + '+', D5). Este script crea
un workflow one-shot en n8n (webhook) que:
  1. respalda (id, session_id) de las filas afectadas en `vtr_sessionkey_backup_0923` (idempotente),
  2. las pasa al formato nuevo (`52`+10 → `+521`+10; resto de 11-15 dígitos → `+` + dígitos),
  3. devuelve conteos antes/después.
Rollback: UPDATE n8n_chat_histories h SET session_id = b.session_id FROM vtr_sessionkey_backup_0923 b WHERE h.id = b.id;
Uso: --crear (crea y activa), --correr (llama al webhook), --borrar (desactiva y borra el workflow)."""
import json, sys, time, urllib.request, importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("p", Path(__file__).with_name("vtr_pre_bsp_fixes.py"))
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
STATE = p.OUT / "n1-memoria" / "estado.json"
PATH = "vtr-n1-sessionkey-0923-8f3a"
PG = {"postgres": {"id": "ihpvM7nYMdLCwWDP", "name": "Venttur"}}
SQL = r"""
CREATE TABLE IF NOT EXISTS vtr_sessionkey_backup_0923 (id bigint PRIMARY KEY, session_id text NOT NULL, backed_up_at timestamptz DEFAULT now());
WITH antes AS (SELECT count(*) AS filas, count(DISTINCT session_id) AS sesiones FROM n8n_chat_histories WHERE session_id ~ '^[0-9]{11,15}$'),
bk AS (INSERT INTO vtr_sessionkey_backup_0923 (id, session_id)
       SELECT id, session_id FROM n8n_chat_histories WHERE session_id ~ '^[0-9]{11,15}$'
       ON CONFLICT (id) DO NOTHING RETURNING id),
up AS (UPDATE n8n_chat_histories SET session_id = CASE WHEN session_id ~ '^52[0-9]{10}$' THEN '+521' || substr(session_id, 3) ELSE '+' || session_id END
       WHERE session_id ~ '^[0-9]{11,15}$' RETURNING id)
SELECT (SELECT filas FROM antes) AS filas_afectadas, (SELECT sesiones FROM antes) AS sesiones_afectadas,
       (SELECT count(*) FROM bk) AS respaldadas, (SELECT count(*) FROM up) AS actualizadas;
"""
CHECK = r"""CREATE TABLE IF NOT EXISTS vtr_sessionkey_backup_0923 (id bigint PRIMARY KEY, session_id text NOT NULL, backed_up_at timestamptz DEFAULT now());
SELECT count(*) FILTER (WHERE session_id ~ '^[0-9]{11,15}$') AS quedan_sin_mas,
 count(*) FILTER (WHERE session_id LIKE '+%') AS con_mas, count(DISTINCT session_id) AS sesiones_total,
 (SELECT count(*) FROM vtr_sessionkey_backup_0923) AS en_backup FROM n8n_chat_histories;"""


def wf():
    return {"name": "TEMP · VTR N1 sessionKey + (one-shot 23/9)", "settings": {"executionOrder": "v1"},
            "nodes": [
                {"parameters": {"httpMethod": "POST", "path": PATH, "responseMode": "lastNode", "options": {}},
                 "name": "Webhook", "type": "n8n-nodes-base.webhook", "typeVersion": 2, "position": [0, 0],
                 "id": "a1", "webhookId": "b7f1d0e2-8f3a-4c1e-9a7b-0923aa11bb22"},
                {"parameters": {"rules": {"values": [
                    {"conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 2},
                                    "conditions": [{"id": "c1", "leftValue": "={{ $json.body.accion }}", "rightValue": "migrar",
                                                    "operator": {"type": "string", "operation": "equals"}}], "combinator": "and"}},
                    {"conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 2},
                                    "conditions": [{"id": "c2", "leftValue": "={{ $json.body.accion }}", "rightValue": "chequear",
                                                    "operator": {"type": "string", "operation": "equals"}}], "combinator": "and"}}]},
                    "options": {}},
                 "name": "Acción", "type": "n8n-nodes-base.switch", "typeVersion": 3.2, "position": [220, 0], "id": "a2"},
                {"parameters": {"operation": "executeQuery", "query": SQL, "options": {}}, "name": "Migrar",
                 "type": "n8n-nodes-base.postgres", "typeVersion": 2.6, "position": [440, -100], "id": "a3", "credentials": PG},
                {"parameters": {"operation": "executeQuery", "query": CHECK, "options": {}}, "name": "Chequear",
                 "type": "n8n-nodes-base.postgres", "typeVersion": 2.6, "position": [440, 100], "id": "a4", "credentials": PG},
            ],
            "connections": {"Webhook": {"main": [[{"node": "Acción", "type": "main", "index": 0}]]},
                            "Acción": {"main": [[{"node": "Migrar", "type": "main", "index": 0}],
                                                [{"node": "Chequear", "type": "main", "index": 0}]]}}}


def call(accion):
    base = p.BASE
    req = urllib.request.Request(f"{base}/webhook/{PATH}", data=json.dumps({"accion": accion}).encode(),
                                 headers={"content-type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


if "--crear" in sys.argv:
    c, r = p.api("POST", "/workflows", wf())
    if c not in (200, 201): sys.exit(f"❌ crear {c} {r}")
    STATE.parent.mkdir(parents=True, exist_ok=True); STATE.write_text(json.dumps({"id": r["id"]}))
    c2, r2 = p.api("POST", f"/workflows/{r['id']}/activate")
    print("creado", r["id"], "activar:", c2, (r2 if c2 != 200 else "ok"))
elif "--actualizar" in sys.argv:
    wid = json.loads(STATE.read_text())["id"]; w = wf()
    c, r = p.api("PUT", f"/workflows/{wid}", {k: w[k] for k in ("name", "nodes", "connections", "settings")})
    print("put", c, "" if c == 200 else r)
elif "--chequear" in sys.argv:
    print(call("chequear"))
elif "--correr" in sys.argv:
    print("antes :", call("chequear")); print("migrar:", call("migrar")); print("después:", call("chequear"))
elif "--borrar" in sys.argv:
    wid = json.loads(STATE.read_text())["id"]
    print("deactivate", p.api("POST", f"/workflows/{wid}/deactivate")[0], "delete", p.api("DELETE", f"/workflows/{wid}")[0])
