#!/usr/bin/env python3
"""Paso 3 (24/9) · Remanente de N1: memoria con clave de 10 dígitos (teléfono mexicano sin el 52).

N1 (corrido el 24/9 16:04 UTC) migró 42.521 filas `52…`/`521…` → `+521…`. Quedaron 143 filas con clave de sólo
dígitos fuera de su regex ({11,15}). Clasificadas el 24/9:
  · 12 sesiones de leads de Form Meta con el teléfono cargado sin lada país (`tel +6677474751`, ladas 667, 662,
    624, 492, 477, 951: México) → acá se pasan a `+521` + 10 dígitos, que es la clave con la que entraría ese
    mismo teléfono por WhatsApp (nsk: 52+10 → 521+10). Ninguno existe hoy en GHL (la importación los salteó).
  · 2 sesiones de pruebas por Telegram (6390727286, 8976567756) y 4 de jul-2025 con id de ManyChat sin teléfono
    (554606174, 2081204536, 1457136969, 1271557903) → se dejan como están (no hay a qué mapearlas).

Respaldo en `vtr_sessionkey_backup_0924` antes del UPDATE (idempotente). Rollback:
  UPDATE n8n_chat_histories h SET session_id = b.session_id FROM vtr_sessionkey_backup_0924 b WHERE h.id = b.id;

Uso: python3 vtr_3_memoria_sin_lada.py            (sólo muestra lo que haría)
     python3 vtr_3_memoria_sin_lada.py --execute
"""
import json, sys, time, uuid, urllib.request, importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "p", Path(__file__).parents[1] / "batches-2026-09-23" / "vtr_pre_bsp_fixes.py")
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
sys.path.insert(0, str(Path(__file__).parent))
import vtr_sql_lectura as L

SESIONES = ["6677474751", "6623270861", "6621480903", "6243176600", "6621138616", "6621396435",
            "4922289607", "4775611806", "6673031215", "9512345190", "6674879798", "6621100934"]
LISTA = ",".join(f"'{s}'" for s in SESIONES)
SQL = f"""
CREATE TABLE IF NOT EXISTS vtr_sessionkey_backup_0924 (id bigint PRIMARY KEY, session_id text NOT NULL, backed_up_at timestamptz DEFAULT now());
WITH bk AS (INSERT INTO vtr_sessionkey_backup_0924 (id, session_id)
            SELECT id, session_id FROM n8n_chat_histories WHERE session_id IN ({LISTA})
            ON CONFLICT (id) DO NOTHING RETURNING id),
up AS (UPDATE n8n_chat_histories SET session_id = '+521' || session_id WHERE session_id IN ({LISTA}) RETURNING id)
SELECT (SELECT count(*) FROM bk) AS respaldadas, (SELECT count(*) FROM up) AS actualizadas;
"""
ANTES = f"SELECT count(*) AS filas, count(DISTINCT session_id) AS sesiones FROM n8n_chat_histories WHERE session_id IN ({LISTA})"
DESPUES = (f"SELECT (SELECT count(*) FROM n8n_chat_histories WHERE session_id IN ({LISTA})) AS quedan, "
           f"(SELECT count(*) FROM n8n_chat_histories WHERE session_id IN ({','.join(repr('+521' + s) for s in SESIONES)})) AS con_clave_nueva, "
           "(SELECT count(*) FROM n8n_chat_histories WHERE session_id ~ '^[0-9]+$') AS solo_digitos_total")


def escribir(sql):
    """Workflow temporal webhook → Postgres con ESTE sql fijo (no parametrizable desde afuera). Se borra al final."""
    path = "vtr-paso3-" + uuid.uuid4().hex[:10]
    wf = {"name": "TEMP · VTR paso 3 memoria sin lada (24/9)", "settings": {"executionOrder": "v1"},
          "nodes": [{"parameters": {"httpMethod": "POST", "path": path, "responseMode": "lastNode", "options": {}},
                     "name": "Webhook", "type": "n8n-nodes-base.webhook", "typeVersion": 2, "position": [0, 0],
                     "id": str(uuid.uuid4()), "webhookId": str(uuid.uuid4())},
                    {"parameters": {"operation": "executeQuery", "query": sql, "options": {}}, "name": "SQL",
                     "type": "n8n-nodes-base.postgres", "typeVersion": 2.6, "position": [220, 0],
                     "id": str(uuid.uuid4()), "credentials": L.PG}],
          "connections": {"Webhook": {"main": [[{"node": "SQL", "type": "main", "index": 0}]]}}}
    c, r = p.api("POST", "/workflows", wf)
    if c not in (200, 201):
        sys.exit(f"❌ crear {c} {r}")
    wid = r["id"]
    try:
        if p.api("POST", f"/workflows/{wid}/activate")[0] != 200:
            sys.exit("❌ activar")
        time.sleep(2)
        req = urllib.request.Request(f"{p.BASE}/webhook/{path}", data=b"{}", headers={"content-type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.load(resp)
    finally:
        p.api("POST", f"/workflows/{wid}/deactivate"); p.api("DELETE", f"/workflows/{wid}")


if __name__ == "__main__":
    print("antes  :", L.correr([ANTES])[0])
    if "--execute" not in sys.argv:
        print("[dry-run] haría:", SQL.strip()[:300], "…"); sys.exit()
    print("migrar :", escribir(SQL))
    print("después:", L.correr([DESPUES])[0])
