#!/usr/bin/env python3
"""Fix 23/9 noche · formato de n8n_chat_histories. El nodo Postgres Chat Memory de n8n guarda cada mensaje PLANO:
{"type":"human|ai|system","content":"…",…} (LangChain PostgresChatMessageHistory guarda el `data` aplanado con el
type). Evidencia: ejecución 1495474 del main, `Armar conversación` (que leía message->'data'->>'content') devolvió
todos los turnos vacíos. Por eso:
  · rescate: se revierte el cambio de vtr_pre_bsp_fixes.py a {type, data:{content}} → vuelve a {type, content}.
  · main `Armar conversación (memoria)`: lee message->>'content' (con fallback a data.content).
  · despachador `Siembra memoria`: {type, content} (está deshabilitado hasta C2).
Idempotente (marca MEM-FLAT-0923)."""
import sys, importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("p", Path(__file__).with_name("vtr_pre_bsp_fixes.py"))
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
MK = "MEM-FLAT-0923"
OUT = p.OUT / "formato-memoria"


def rescate(wf):
    p.replace_in(p.node(wf, "Build Rescate Memory (Fase 1)"),
                 "const system = { type: 'system', data: { content: `",
                 "const system = { type: 'system', content: `")
    p.replace_in(p.node(wf, "Build Rescate Memory (Fase 1)"),
                 "pero no agendó.` } }; const ai = { type: 'ai', data: { content: c.message || '' } }; /* PRE-BSP-0923 */",
                 f"pero no agendó.` }}; const ai = {{ type: 'ai', content: c.message || '' }}; /* {MK}: formato plano de n8n */")
    p.replace_in(p.node(wf, "Build Rescate Memory (Fase 2)"),
                 "ai_message: { type: 'ai', data: { content: c.message || '' } } /* PRE-BSP-0923 */",
                 f"ai_message: {{ type: 'ai', content: c.message || '' }} /* {MK}: formato plano de n8n */")


def main_(wf):
    n = p.node(wf, "Armar conversación (memoria)")
    p.replace_in(n, "COALESCE(message->'data'->>'content','')",
                 "COALESCE(message->>'content', message->'data'->>'content', '')", key="query")
    n["notes"] = f"{MK}: la memoria de n8n guarda el content plano (message->>'content')."


def despachador(wf):
    n = p.node(wf, "Siembra memoria (Supabase)")
    s = n["parameters"]["options"]["queryReplacement"]
    old = "JSON.stringify({type:'ai', data:{content:'[toque proactivo: '+$json.lane+']'}})"
    if old not in s:
        raise ValueError("ancla siembra")
    n["parameters"]["options"]["queryReplacement"] = s.replace(old, "JSON.stringify({type:'ai', content:'[toque proactivo: '+$json.lane+']'})")
    n["notes"] = f"{MK}: formato plano de n8n ({{type, content}})."


for alias, wid, fn in (("rescate", "YB0UxwEVwzISdd54", rescate), ("main", "1eS1Z5k898c3ATnf", main_),
                       ("despachador", "vrShEXQGGAo4FqAt", despachador)):
    c, wf = p.api("GET", f"/workflows/{wid}")
    import json
    if MK in json.dumps(wf, ensure_ascii=False):
        print(f"↷ {alias} ya aplicado"); continue
    fn(wf)
    if "--execute" not in sys.argv:
        print(f"[dry-run] {alias} activo={wf['active']} ok"); continue
    c0, pre = p.api("GET", f"/workflows/{wid}"); p.save(pre, OUT / "pre" / f"{alias}.json")
    body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
            "settings": {k: v for k, v in (wf.get("settings") or {}).items() if k in p.SETTINGS_OK}}
    c, r = p.api("PUT", f"/workflows/{wid}", body)
    if c != 200:
        sys.exit(f"❌ PUT {alias} {c} {r}")
    c, post = p.api("GET", f"/workflows/{wid}"); p.save(post, OUT / "post" / f"{alias}.json")
    print(f"✅ {alias} · activo={post['active']}")
