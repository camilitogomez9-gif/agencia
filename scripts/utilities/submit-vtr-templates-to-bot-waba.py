#!/usr/bin/env python3
"""Submit de las 12 plantillas del WABA de Rodrigo al WABA del bot via Meta Graph API.

Lee `06_docs/plantillas-waba-rodrigo-a-reaprobar-2026-09-18.md` (los nombres), toma
los `components` originales del JSON dump del WABA de Rodrigo, y hace
`POST /{waba_bot}/message_templates` por cada plantilla.

Reglas de seguridad:
  1. Chequea colisiones: si el WABA del bot ya tiene una plantilla con ese nombre + idioma,
     no la submitea (Meta la rechazaría con 400).
  2. Idempotente: guarda un log JSON con lo submiteado; re-ejecutar solo reintenta las que
     no lograron entrar en el pipeline de review.
  3. Preserva `name`, `language`, `category`, `components` del original.
  4. Dry-run por default. --apply para efectivamente submitear.

Uso:
    source .env && python3 scripts/utilities/submit-vtr-templates-to-bot-waba.py         # dry-run
    source .env && python3 scripts/utilities/submit-vtr-templates-to-bot-waba.py --apply  # submit
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = REPO_ROOT / "clients" / "VTR_Venttur" / "06_docs"
LOG_PATH = DOCS_DIR / "submit-templates-log.json"

WABA_BOT = "1931874540684022"       # destino
WABA_RODRIGO = "141523652373940"    # origen
GRAPH_VERSION = "v20.0"


def http_json(method: str, url: str, token: str, body: dict | None = None) -> tuple[int, dict]:
    data = None
    headers = {"Authorization": f"Bearer {token}"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return (resp.status, json.loads(resp.read().decode("utf-8")))
    except urllib.error.HTTPError as e:
        body_txt = e.read().decode("utf-8", errors="replace")
        try:
            body_json = json.loads(body_txt)
        except Exception:
            body_json = {"raw": body_txt}
        return (e.code, body_json)


def fetch_existing_names(token: str, waba: str) -> set[tuple[str, str]]:
    """Retorna set de (name, language) que ya existen en el WABA."""
    existing: set[tuple[str, str]] = set()
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{waba}/message_templates?limit=100&fields=name,language,status"
    while url:
        code, payload = http_json("GET", url, token)
        if code != 200:
            print(f"ERROR fetch existing: HTTP {code} · {payload}", file=sys.stderr)
            sys.exit(1)
        for t in payload.get("data", []):
            existing.add((t["name"], t["language"]))
        url = payload.get("paging", {}).get("next")
    return existing


def load_names_to_submit() -> list[str]:
    """Lee `plantillas-waba-rodrigo-a-reaprobar-*.md` y extrae los nombres de plantilla."""
    md_files = sorted(DOCS_DIR.glob("plantillas-waba-rodrigo-a-reaprobar-*.md"))
    if not md_files:
        print("ERROR: no encuentro doc `plantillas-waba-rodrigo-a-reaprobar-*.md`", file=sys.stderr)
        sys.exit(1)
    md = md_files[-1]
    print(f"Leyendo nombres de: {md.name}", file=sys.stderr)
    # Formato: ### `nombre`
    names = re.findall(r"^### `([a-z0-9_]+)`", md.read_text(encoding="utf-8"), re.MULTILINE)
    return names


def load_rodrigo_templates() -> dict[str, dict]:
    """Retorna mapa nombre → dict con components, language, category del WABA de Rodrigo."""
    dumps = sorted(DOCS_DIR.glob(f"plantillas-meta-live-{WABA_RODRIGO}-*.json"))
    if not dumps:
        print(f"ERROR: no encuentro dump del WABA {WABA_RODRIGO}", file=sys.stderr)
        sys.exit(1)
    data = json.loads(dumps[-1].read_text(encoding="utf-8"))
    return {t["name"]: t for t in data}


def load_log() -> dict:
    if LOG_PATH.is_file():
        return json.loads(LOG_PATH.read_text(encoding="utf-8"))
    return {"submitted": {}, "last_run": None}


def save_log(log: dict) -> None:
    LOG_PATH.write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_submit_body(template: dict) -> dict | None:
    """Construye el body para POST /{waba}/message_templates.

    Retorna None si la plantilla tiene HEADER media (VIDEO/IMAGE/DOCUMENT) —
    no submitable sin upload previo del asset via Resumable Upload API.
    """
    components = []
    for c in template.get("components", []):
        typ = c.get("type")
        fmt = c.get("format", "")
        if typ == "HEADER" and fmt in ("VIDEO", "IMAGE", "DOCUMENT"):
            return None
        # Copiar tal cual (`example` es obligatorio cuando hay variables)
        components.append(dict(c))
    return {
        "name": template["name"],
        "language": template["language"],
        "category": template["category"],
        "components": components,
    }


def main() -> int:
    token = os.environ.get("VTR_META_WABA_TOKEN")
    if not token:
        print("ERROR: falta VTR_META_WABA_TOKEN. Corré: source .env && python3 ...", file=sys.stderr)
        return 1

    apply = "--apply" in sys.argv

    print(f"{'APLICANDO' if apply else 'DRY-RUN'}", file=sys.stderr)
    print(f"WABA destino: {WABA_BOT} (bot)", file=sys.stderr)
    print(f"WABA origen: {WABA_RODRIGO} (Rodrigo)\n", file=sys.stderr)

    # 1. Cargar nombres a submitear
    names = load_names_to_submit()
    print(f"Plantillas a submitear: {len(names)}", file=sys.stderr)

    # 2. Cargar templates del WABA de Rodrigo
    rodrigo_templates = load_rodrigo_templates()

    # 3. Chequear colisiones en el WABA del bot
    print(f"Chequeando colisiones en WABA {WABA_BOT}…", file=sys.stderr)
    existing = fetch_existing_names(token, WABA_BOT)
    print(f"  {len(existing)} plantillas actuales en el bot.\n", file=sys.stderr)

    # 4. Cargar log de submits previos
    log = load_log()

    # 5. Iterar
    results: list[dict] = []
    for name in names:
        tmpl = rodrigo_templates.get(name)
        if not tmpl:
            results.append({"name": name, "action": "SKIP", "reason": "no está en dump WABA Rodrigo"})
            continue
        key = f"{name}|{tmpl['language']}"
        if key in log["submitted"]:
            prev = log["submitted"][key]
            results.append({"name": name, "action": "SKIP", "reason": f"ya submiteado {prev['ts']} · id {prev.get('id')}"})
            continue
        if (name, tmpl["language"]) in existing:
            results.append({"name": name, "action": "SKIP", "reason": f"ya existe en WABA bot con idioma {tmpl['language']}"})
            continue

        body = build_submit_body(tmpl)
        if body is None:
            results.append({"name": name, "action": "SKIP-MEDIA", "reason": "HEADER con VIDEO/IMAGE/DOCUMENT — requiere upload de asset (submitear manual en Meta BM UI)"})
            continue
        # Detectar violación de política: variable al inicio/fin del BODY
        body_text = ""
        for c in body["components"]:
            if c.get("type") == "BODY":
                body_text = c.get("text", "").strip()
                break
        var_re = re.compile(r"^\{\{\d+\}\}|\{\{\d+\}\}$")
        if var_re.search(body_text[:10]) or var_re.search(body_text[-10:]):
            # Verificar precisamente inicio y fin
            starts_with_var = bool(re.match(r"^\{\{\d+\}\}", body_text))
            ends_with_var = bool(re.search(r"\{\{\d+\}\}$", body_text))
            if starts_with_var or ends_with_var:
                results.append({"name": name, "action": "SKIP-POLICY", "reason": f"BODY {'empieza' if starts_with_var else 'termina'} con variable — Meta rechaza (subcode 2388299)"})
                continue
        preview = body_text[:80] if body_text else "(no body)"
        if not apply:
            results.append({"name": name, "action": "WOULD SUBMIT", "language": tmpl["language"], "category": tmpl["category"], "body_preview": preview})
            continue

        # SUBMIT REAL
        url = f"https://graph.facebook.com/{GRAPH_VERSION}/{WABA_BOT}/message_templates"
        code, resp = http_json("POST", url, token, body)
        ts = datetime.now(timezone.utc).isoformat()
        if code in (200, 201):
            template_id = resp.get("id")
            status = resp.get("status", "?")
            log["submitted"][key] = {"ts": ts, "id": template_id, "status": status, "http": code}
            results.append({"name": name, "action": "SUBMITTED", "id": template_id, "status": status})
            print(f"  ✅ {name} → id {template_id} · status {status}", file=sys.stderr)
        else:
            err = resp.get("error", {})
            # Meta expone el detalle en error_user_msg / error_user_title
            err_msg = err.get("error_user_msg") or err.get("message", str(resp))
            err_msg = err_msg[:180]
            results.append({"name": name, "action": "ERROR", "http": code, "message": err_msg})
            print(f"  ❌ {name} → HTTP {code}: {err_msg}", file=sys.stderr)
        # Rate limit: pausa entre submits
        time.sleep(1)

    log["last_run"] = datetime.now(timezone.utc).isoformat()
    if apply:
        save_log(log)

    # Reporte
    print("\n" + "=" * 70, file=sys.stderr)
    for r in results:
        print(f"  {r['action']:14} · {r['name']}" + (f" · {r.get('reason','')}" if r.get('reason') else "") + (f" · {r.get('message','')}" if r.get('message') else ""), file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    summary: dict[str, int] = {}
    for r in results:
        summary[r["action"]] = summary.get(r["action"], 0) + 1
    for action, n in sorted(summary.items()):
        print(f"  {action}: {n}", file=sys.stderr)
    if apply:
        print(f"\nLog: {LOG_PATH.relative_to(REPO_ROOT)}", file=sys.stderr)
    else:
        print("\nDry-run OK. Corré con `--apply` para submitear.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
