#!/usr/bin/env python3
"""Consulta SÓLO LECTURA a la base Supabase de VTR (tabla de memoria del agente) vía la credencial n8n `Venttur`
(ihpvM7nYMdLCwWDP) — no hay acceso directo a esa base desde acá. Crea un workflow temporal (webhook → Postgres),
corre la consulta y lo borra. Rechaza cualquier SQL que no empiece con SELECT/WITH o que tenga verbos de escritura.

Uso: python3 vtr_sql_lectura.py "SELECT ..."   (varias consultas: pasar varios argumentos)
"""
import json, re, sys, time, uuid, urllib.request, importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "p", Path(__file__).parents[1] / "batches-2026-09-23" / "vtr_pre_bsp_fixes.py")
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
PG = {"postgres": {"id": "ihpvM7nYMdLCwWDP", "name": "Venttur"}}
PROHIBIDO = re.compile(r"\b(insert|update|delete|drop|alter|create|truncate|grant|revoke|copy|call|do)\b", re.I)


def correr(queries):
    for q in queries:
        if not re.match(r"\s*(select|with)\b", q, re.I) or PROHIBIDO.search(q):
            sys.exit(f"❌ sólo lecturas: {q[:80]}")
    path = "vtr-sql-lectura-" + uuid.uuid4().hex[:10]
    hook = {"parameters": {"httpMethod": "POST", "path": path, "responseMode": "lastNode",
                           "responseData": "allEntries", "options": {}},
            "name": "Webhook", "type": "n8n-nodes-base.webhook", "typeVersion": 2, "position": [0, 0],
            "id": str(uuid.uuid4()), "webhookId": str(uuid.uuid4())}
    pg = {"parameters": {"operation": "executeQuery", "query": "={{ $json.body.q }}", "options": {}},
          "name": "SQL", "type": "n8n-nodes-base.postgres", "typeVersion": 2.6, "position": [220, 0],
          "id": str(uuid.uuid4()), "credentials": PG}
    wf = {"name": "TEMP · VTR SQL lectura (24/9)", "nodes": [hook, pg], "settings": {"executionOrder": "v1"},
          "connections": {"Webhook": {"main": [[{"node": "SQL", "type": "main", "index": 0}]]}}}
    c, r = p.api("POST", "/workflows", wf)
    if c not in (200, 201):
        sys.exit(f"❌ crear {c} {r}")
    wid = r["id"]
    try:
        c, r2 = p.api("POST", f"/workflows/{wid}/activate")
        if c != 200:
            sys.exit(f"❌ activar {c} {r2}")
        time.sleep(2)
        out = []
        for q in queries:
            req = urllib.request.Request(f"{p.BASE}/webhook/{path}", data=json.dumps({"q": q}).encode(),
                                         headers={"content-type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=120) as resp:
                out.append(json.load(resp))
        return out
    finally:
        p.api("POST", f"/workflows/{wid}/deactivate"); p.api("DELETE", f"/workflows/{wid}")


if __name__ == "__main__":
    for q, res in zip(sys.argv[1:], correr(sys.argv[1:])):
        print("»", q.strip()[:140]); print(json.dumps(res, ensure_ascii=False, indent=1)[:3000])
