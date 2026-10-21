#!/usr/bin/env python3
"""Fetch de plantillas de WhatsApp desde Meta Graph API para VTR (Venttur).

Requiere que exista en `.env` la variable `VTR_META_WABA_TOKEN` con un token de
System User que tenga permiso `whatsapp_business_management` y rol sobre ambos
WABAs. Ver el plan en `/Users/camilo/.claude/plans/harmonic-prancing-raven.md`
§Pieza 2 para cómo generarlo.

Venttur tiene DOS WABAs distintos (descubierto 2026-09-17):
  - `1931874540684022` — "Venttur | Agente de IA" — WABA OPERATIVO del bot
    (número +5213326274502), conectado a ManyChat. ~50 plantillas.
  - `141523652373940`  — "Venttur Education & travel" — WABA secundario
    (probablemente conectado a Clientify para recordatorios/formularios).
    42 plantillas.

Uso:
    source .env && python3 scripts/utilities/fetch-vtr-whatsapp-templates.py [WABA_ID]

Sin argumento: usa el WABA operativo del bot (1931874540684022).

Genera 2 outputs en `clients/VTR_Venttur/06_docs/`:
  - `plantillas-meta-live-{WABA_ID}-YYYY-MM-DD.json` — dump crudo del API.
  - `plantillas-meta-live-{WABA_ID}-YYYY-MM-DD.md` — tabla legible.

Al final, reporta total por estado, presencia de `formulario_boarding`,
y drift vs borradores locales.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

# WABAs conocidos de Venttur (descubierto 2026-09-17)
WABA_OPERATIVO_BOT = "1931874540684022"  # "Venttur | Agente de IA" · número +5213326274502 · ManyChat
WABA_SECUNDARIO = "141523652373940"      # "Venttur Education & travel" · probable Clientify
GRAPH_VERSION = "v20.0"
REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = REPO_ROOT / "clients" / "VTR_Venttur" / "06_docs"
# Resuelto en runtime desde argv o el default
WABA_ID = WABA_OPERATIVO_BOT
BORRADORES_MD = DOCS_DIR / "plantillas-meta-borradores-2026-09-11.md"
NURTURING_MD = DOCS_DIR / "plantillas-meta-nurturing-2026-09-11.md"

# Regex para nombres tipo `nombre_plantilla` en headings/backticks de los borradores locales
LOCAL_NAME_RE = re.compile(r"`([a-z][a-z0-9_]{2,50})`")


def http_get_json(url: str, token: str) -> dict:
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {e.code} {url}\n{body}") from e


def fetch_all_templates(token: str, waba_id: str) -> list[dict]:
    url = (
        f"https://graph.facebook.com/{GRAPH_VERSION}/{waba_id}/message_templates"
        f"?limit=100&fields=name,language,status,category,components"
    )
    all_data: list[dict] = []
    while url:
        payload = http_get_json(url, token)
        all_data.extend(payload.get("data", []))
        url = payload.get("paging", {}).get("next")
    return all_data


def body_text(components: list[dict]) -> str:
    for comp in components or []:
        if comp.get("type") == "BODY":
            return (comp.get("text") or "").replace("\n", " ⏎ ").strip()
    return ""


def var_count(text: str) -> int:
    return len(re.findall(r"\{\{\d+\}\}", text))


def render_md(templates: list[dict]) -> str:
    lines = [
        f"# Plantillas de WhatsApp — dump live desde Meta (VTR)",
        "",
        f"**Fecha:** {date.today().isoformat()} · **WABA:** `{WABA_ID}`",
        f"**Fuente:** `GET /{GRAPH_VERSION}/{WABA_ID}/message_templates` — {len(templates)} plantillas.",
        "",
        "| Nombre | Idioma | Estado | Categoría | Vars | Cuerpo (primeros 120) |",
        "|---|---|---|---|---:|---|",
    ]
    for t in sorted(templates, key=lambda x: (x.get("status", ""), x.get("name", ""))):
        body = body_text(t.get("components", []))
        preview = body[:120] + ("…" if len(body) > 120 else "")
        # escapar pipes en el preview
        preview = preview.replace("|", "\\|")
        lines.append(
            f"| `{t.get('name','')}` | {t.get('language','')} | {t.get('status','')} "
            f"| {t.get('category','')} | {var_count(body)} | {preview} |"
        )
    lines.append("")
    return "\n".join(lines)


def local_template_names() -> set[str]:
    names: set[str] = set()
    for md in (BORRADORES_MD, NURTURING_MD):
        if not md.is_file():
            continue
        for m in LOCAL_NAME_RE.finditer(md.read_text(encoding="utf-8")):
            candidate = m.group(1)
            # filtrar patrones que casi seguro NO son nombres de plantilla
            if candidate in {"utility", "marketing", "authentication", "es_mx", "es_MX"}:
                continue
            names.add(candidate)
    return names


def print_report(templates: list[dict]) -> None:
    print("\n" + "=" * 60)
    print(f"REPORTE — {len(templates)} plantillas devueltas por Meta")
    print("=" * 60)

    # Por estado
    by_status: dict[str, int] = {}
    for t in templates:
        by_status[t.get("status", "?")] = by_status.get(t.get("status", "?"), 0) + 1
    print("\nPor estado:")
    for st, n in sorted(by_status.items()):
        print(f"  {st}: {n}")

    remote_names = {t.get("name", "") for t in templates}

    print("\n¿Aparece `formulario_boarding`?", "SÍ ✅" if "formulario_boarding" in remote_names else "NO ❌")

    # Drift
    local_names = local_template_names()
    only_remote = sorted(remote_names - local_names)
    only_local = sorted(local_names - remote_names)
    print(f"\nDrift vs borradores locales ({BORRADORES_MD.name} + {NURTURING_MD.name}):")
    print(f"  En Meta y NO en local ({len(only_remote)}):")
    for n in only_remote:
        print(f"    + {n}")
    print(f"  En local y NO en Meta ({len(only_local)}):")
    for n in only_local:
        print(f"    - {n}")


def main() -> int:
    token = os.environ.get("VTR_META_WABA_TOKEN")
    if not token:
        print(
            "ERROR: falta VTR_META_WABA_TOKEN en el entorno.\n"
            "Corré: source .env && python3 scripts/utilities/fetch-vtr-whatsapp-templates.py [WABA_ID]\n"
            "Ver plan §Pieza 2 para cómo generar el token.",
            file=sys.stderr,
        )
        return 1

    global WABA_ID
    if len(sys.argv) > 1:
        WABA_ID = sys.argv[1]
    # else: usa WABA_OPERATIVO_BOT por default

    print(f"Fetching plantillas del WABA {WABA_ID} …", file=sys.stderr)
    templates = fetch_all_templates(token, WABA_ID)

    stamp = date.today().isoformat()
    json_out = DOCS_DIR / f"plantillas-meta-live-{WABA_ID}-{stamp}.json"
    md_out = DOCS_DIR / f"plantillas-meta-live-{WABA_ID}-{stamp}.md"
    json_out.write_text(json.dumps(templates, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_out.write_text(render_md(templates), encoding="utf-8")
    print(f"\nEscrito: {json_out.relative_to(REPO_ROOT)}", file=sys.stderr)
    print(f"Escrito: {md_out.relative_to(REPO_ROOT)}", file=sys.stderr)

    print_report(templates)
    return 0


if __name__ == "__main__":
    sys.exit(main())
