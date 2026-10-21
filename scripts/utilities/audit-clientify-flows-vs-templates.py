#!/usr/bin/env python3
"""Pieza 3: Auditor del snapshot Clientify vs plantillas Meta canónicas.

Recorre `/Users/camilo/Downloads/Clientify/flujos de trabajo/` y cruza cada screenshot
contra las 92 plantillas Meta canónicas (dumps del 2026-09-17). Genera 3 outputs:

  1. `mapeo-flujos-plantillas-YYYY-MM-DD.md`
     Matriz por sub-carpeta con categorías: Match / Freetext / Notemplate / Lanzador /
     Accion / Unknown / Mismatch. Reporta plantillas Meta no referenciadas por ningún flujo.

  2. `inventario-flujos-clientify-YYYY-MM-DD.md`
     Lista por sub-carpeta con las plantillas + freetexts + notas — input directo para
     Etapa 4 de la migración GHL.

  3. `plantillas-waba-rodrigo-a-reaprobar-YYYY-MM-DD.md`
     Subset crítico: cada plantilla del WABA de Rodrigo (`141523652373940`) que aparezca
     en un screenshot es candidato a reaprobación en el WABA del bot. Incluye body real.

Uso:
    python3 audit-clientify-flows-vs-templates.py
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).resolve().parents[2]
CLIENTIFY = Path("/Users/camilo/Downloads/Clientify")
FLUJOS = CLIENTIFY / "flujos de trabajo"
DOCS_DIR = REPO_ROOT / "clients" / "VTR_Venttur" / "06_docs"

WABA_BOT = "1931874540684022"
WABA_RODRIGO = "141523652373940"

# Prefijos válidos de la convención
PREFIXES = ["_notemplate_", "_freetext_", "_lanzador_", "_accion_", "_accion2_", "_accion3_", "_unknown_"]


def split_prefix(stem: str) -> tuple[str, str]:
    for p in PREFIXES:
        if stem.startswith(p):
            return (p, stem[len(p):])
    return ("", stem)


def load_templates() -> dict[str, dict]:
    """Carga los 2 dumps → mapa nombre → {waba, language, category, status, body, components}."""
    out: dict[str, dict] = {}
    for waba in (WABA_BOT, WABA_RODRIGO):
        p = DOCS_DIR / f"plantillas-meta-live-{waba}-2026-09-17.json"
        if not p.is_file():
            print(f"ERROR: falta dump {p}", file=sys.stderr)
            sys.exit(1)
        data = json.loads(p.read_text(encoding="utf-8"))
        for t in data:
            body = ""
            for c in t.get("components", []):
                if c.get("type") == "BODY":
                    body = c.get("text", "")
                    break
            out[t["name"]] = {
                "waba": waba,
                "language": t.get("language", ""),
                "category": t.get("category", ""),
                "status": t.get("status", ""),
                "body": body,
                "components": t.get("components", []),
            }
    return out


def scan_flows(templates: dict[str, dict]) -> dict:
    """Recorre `flujos de trabajo/{Owner}/{Flujo}/**` y categoriza cada .png.

    Devuelve:
        {
          "Owner": {
            "Sub-carpeta": {
              "plantillas": [nombres matched],
              "notemplate": [slugs],
              "freetext": [{slug, body: contenido del .txt}],
              "lanzador": [slugs],
              "accion": [slugs],  # + accion2, accion3
              "unknown": [slugs],
              "mismatch": [nombres sin prefijo que no matchean],
              "sub_sub_carpetas": {"Sub-sub-carpeta": {...misma estructura}},
            }
          }
        }
    """
    tree: dict = defaultdict(lambda: defaultdict(lambda: {
        "plantillas": [],
        "notemplate": [],
        "freetext": [],
        "lanzador": [],
        "accion": [],
        "unknown": [],
        "mismatch": [],
        "sub_sub": defaultdict(lambda: {
            "plantillas": [],
            "notemplate": [],
            "freetext": [],
            "lanzador": [],
            "accion": [],
            "unknown": [],
            "mismatch": [],
        }),
    }))

    for owner_dir in sorted(FLUJOS.iterdir()):
        if not owner_dir.is_dir() or owner_dir.name == ".DS_Store":
            continue
        owner = owner_dir.name
        for flujo_dir in sorted(owner_dir.iterdir()):
            if not flujo_dir.is_dir() or flujo_dir.name == ".DS_Store":
                continue
            flujo = flujo_dir.name
            # Recolectar archivos directos + sub-sub-carpetas
            for f in sorted(flujo_dir.iterdir()):
                if f.name == ".DS_Store":
                    continue
                if f.is_dir():
                    # sub-sub-carpeta (ej. Max/Rescate No show/AA Familia - Rescate No show/)
                    for ff in sorted(f.iterdir()):
                        if ff.name == ".DS_Store" or ff.is_dir():
                            continue
                        _classify(ff, tree[owner][flujo]["sub_sub"][f.name], templates)
                elif f.suffix.lower() == ".png":
                    _classify(f, tree[owner][flujo], templates)
                # Los .txt se procesan como sidecar dentro de _classify

    return tree


def _classify(png: Path, bucket: dict, templates: dict[str, dict]) -> None:
    if png.suffix.lower() != ".png":
        return
    stem = png.stem
    prefix, slug = split_prefix(stem)
    if prefix == "":
        # Sin prefijo → debe ser nombre de plantilla
        if stem in templates:
            bucket["plantillas"].append(stem)
            return
        # Patrón parametrizado: `{plantilla}_-_{descripcion}` (1 flujo dispara la misma plantilla con variante)
        # Ej: `formulario_boarding_-_Rescate_de_seguimiento_boarding` → plantilla `formulario_boarding` + desc
        m = re.match(r"^(.+?)_-_(.+)$", stem)
        if m and m.group(1) in templates:
            bucket["plantillas"].append(m.group(1))
            return
        bucket["mismatch"].append(stem)
    elif prefix == "_notemplate_":
        bucket["notemplate"].append(slug)
    elif prefix == "_freetext_":
        sidecar = png.parent / f"_freetext_{slug}.txt"
        body = sidecar.read_text(encoding="utf-8").strip() if sidecar.is_file() else ""
        bucket["freetext"].append({"slug": slug, "body": body, "has_sidecar": sidecar.is_file()})
    elif prefix == "_lanzador_":
        bucket["lanzador"].append(slug)
    elif prefix.startswith("_accion"):
        bucket["accion"].append(f"{prefix.strip('_')}_{slug}")
    elif prefix == "_unknown_":
        bucket["unknown"].append(slug)


def render_mapeo(tree: dict, templates: dict[str, dict]) -> str:
    stamp = date.today().isoformat()
    used_templates: set[str] = set()
    lines = [
        f"# Mapeo Flujos Clientify ↔ Plantillas Meta — {stamp}",
        "",
        "Generado por `scripts/utilities/audit-clientify-flows-vs-templates.py`.",
        "",
        f"**Snapshot Clientify:** `/Users/camilo/Downloads/Clientify/flujos de trabajo/`",
        f"**Plantillas Meta:** 92 canónicas (50 WABA bot `{WABA_BOT}` + 42 WABA Rodrigo `{WABA_RODRIGO}`)",
        "",
        "## Categorías",
        "",
        "| Categoría | Significado |",
        "|---|---|",
        "| **Plantilla** | Screenshot con nombre exacto = plantilla Meta (dispara esa plantilla) |",
        "| **Freetext** | Mensaje libre de sesión (`_freetext_*.png` + sidecar `.txt` con el body) |",
        "| **Notemplate** | Flujo NO dispara WhatsApp (RRHH, tarea interna, CRM puro) |",
        "| **Lanzador/Acción** | Detalle de trigger o step del flujo (con parámetros no visibles en canvas) |",
        "| **Unknown** | Nombre de plantilla desconocido — resolver manualmente |",
        "| **Mismatch** | Nombre sin prefijo que NO matchea con las 92 canónicas — alerta |",
        "",
        "---",
        "",
    ]

    for owner in sorted(tree.keys()):
        lines.append(f"## Owner: {owner}")
        lines.append("")
        for flujo, b in sorted(tree[owner].items()):
            lines.append(f"### {flujo}")
            _render_bucket(lines, b, templates, used_templates, indent="")
            # Sub-sub-carpetas
            if b.get("sub_sub"):
                for sub, bb in sorted(b["sub_sub"].items()):
                    lines.append(f"#### {sub}")
                    _render_bucket(lines, bb, templates, used_templates, indent="")
            lines.append("")

    # Plantillas no referenciadas (huérfanas)
    all_names = set(templates.keys())
    orphans = sorted(all_names - used_templates)
    lines.append("---")
    lines.append("")
    lines.append(f"## Plantillas Meta NO referenciadas ({len(orphans)}/{len(all_names)})")
    lines.append("")
    lines.append("Plantillas del dump que no aparecen en ningún screenshot. Candidatas a descartar o revisar si el flujo se bajó incompleto.")
    lines.append("")
    for name in orphans:
        t = templates[name]
        waba_label = "bot" if t["waba"] == WABA_BOT else "Rodrigo"
        lines.append(f"- `{name}` — WABA {waba_label} · {t['status']} · {t['category']} · {t['language']}")
    lines.append("")
    return "\n".join(lines)


def _render_bucket(lines: list[str], b: dict, templates: dict[str, dict], used: set, indent: str) -> None:
    def add(txt: str):
        lines.append(indent + txt)
    plt = b.get("plantillas", [])
    ntpl = b.get("notemplate", [])
    ftxt = b.get("freetext", [])
    lz = b.get("lanzador", [])
    ac = b.get("accion", [])
    unk = b.get("unknown", [])
    mm = b.get("mismatch", [])
    if plt:
        add("**Plantillas Meta:**")
        for name in plt:
            t = templates.get(name)
            waba_label = "bot" if t and t["waba"] == WABA_BOT else "Rodrigo"
            add(f"- `{name}` (WABA {waba_label}, {t['status'] if t else '?'})")
            used.add(name)
        add("")
    if ftxt:
        add("**Freetext (mensaje libre):**")
        for ft in ftxt:
            body_prev = ft["body"][:80].replace("\n", " ") + ("…" if len(ft["body"]) > 80 else "")
            sidecar_note = "" if ft["has_sidecar"] else " ⚠ sin sidecar"
            add(f"- `{ft['slug']}`{sidecar_note}")
            if body_prev:
                add(f"  > {body_prev}")
        add("")
    if ntpl:
        add(f"**Notemplate ({len(ntpl)}):** " + ", ".join(f"`{s}`" for s in ntpl))
        add("")
    if lz:
        add(f"**Lanzador ({len(lz)}):** " + ", ".join(f"`{s}`" for s in lz))
        add("")
    if ac:
        add(f"**Acción ({len(ac)}):** " + ", ".join(f"`{s}`" for s in ac))
        add("")
    if unk:
        add(f"**⚠ Unknown ({len(unk)}):** " + ", ".join(f"`{s}`" for s in unk))
        add("")
    if mm:
        add(f"**⚠ MISMATCH ({len(mm)}):** " + ", ".join(f"`{s}`" for s in mm) + " — revisar")
        add("")


def render_inventario(tree: dict, templates: dict[str, dict]) -> str:
    stamp = date.today().isoformat()
    lines = [
        f"# Inventario de Flujos Clientify — {stamp}",
        "",
        "Input directo para la Etapa 4 de la migración a GHL. Cada flujo → cómo se reconstruye.",
        "",
        "## Legenda",
        "",
        "- **Destino GHL:** propuesta de destino (Workflow / Funnel / se-descarta).",
        "- Los flujos que solo tienen `_notemplate_` (sin plantillas ni freetext) son puro CRM — se recrean como GHL Workflow.",
        "- Los flujos con freetext requieren decidir: submitear plantilla nueva a Meta O usar send free-form de GHL.",
        "",
        "---",
        "",
    ]
    for owner in sorted(tree.keys()):
        lines.append(f"## {owner}")
        lines.append("")
        for flujo, b in sorted(tree[owner].items()):
            plt = b.get("plantillas", [])
            ftxt = b.get("freetext", [])
            ntpl = b.get("notemplate", [])
            sub = b.get("sub_sub", {})
            lines.append(f"### {flujo}")
            lines.append("")
            if plt:
                for name in plt:
                    t = templates.get(name)
                    waba_lbl = "bot" if t and t["waba"] == WABA_BOT else "Rodrigo"
                    lines.append(f"- Plantilla: **`{name}`** (WABA {waba_lbl})")
            for ft in ftxt:
                lines.append(f"- Freetext: **`{ft['slug']}`** — body en `flujos de trabajo/{owner}/{flujo}/_freetext_{ft['slug']}.txt`")
            if ntpl:
                lines.append(f"- Sin WhatsApp — solo CRM/tarea/email: {len(ntpl)} nodos")
            if sub:
                lines.append("")
                lines.append("**Sub-flujos por programa:**")
                for sub_name, sub_b in sorted(sub.items()):
                    plt_sub = sub_b.get("plantillas", [])
                    ftxt_sub = sub_b.get("freetext", [])
                    subs_desc = []
                    for name in plt_sub:
                        t = templates.get(name)
                        waba_lbl = "bot" if t and t["waba"] == WABA_BOT else "Rodrigo"
                        subs_desc.append(f"`{name}` (WABA {waba_lbl})")
                    for ft in ftxt_sub:
                        subs_desc.append(f"freetext `{ft['slug']}`")
                    lines.append(f"- **{sub_name}:** {', '.join(subs_desc) if subs_desc else '(sin plantilla)'}")
            lines.append("")
    return "\n".join(lines)


def render_reaprobar(tree: dict, templates: dict[str, dict]) -> str:
    stamp = date.today().isoformat()
    # Colectar todas las plantillas del WABA de Rodrigo usadas en flujos
    used_rodrigo: dict[str, list[str]] = defaultdict(list)  # nombre → lista de flujos donde aparece
    def collect(bucket, path_str):
        for name in bucket.get("plantillas", []):
            t = templates.get(name)
            if t and t["waba"] == WABA_RODRIGO:
                used_rodrigo[name].append(path_str)
    for owner, flujos in tree.items():
        for flujo, b in flujos.items():
            collect(b, f"{owner}/{flujo}")
            for sub_name, sub_b in b.get("sub_sub", {}).items():
                collect(sub_b, f"{owner}/{flujo}/{sub_name}")

    lines = [
        f"# Plantillas del WABA de Rodrigo a reaprobar en el WABA del bot — {stamp}",
        "",
        f"**Contexto:** el WABA `{WABA_RODRIGO}` (número personal de Rodrigo) muere con Clientify. Los flujos operativos que hoy disparan estas plantillas hay que reconstruirlos en GHL apuntando al WABA del bot (`{WABA_BOT}`), lo que requiere **reaprobar cada plantilla** en el nuevo WABA (24-72h por plantilla). Este documento es el input directo del proceso.",
        "",
        f"**Total a reaprobar:** {len(used_rodrigo)} plantillas.",
        "",
        "## Lista",
        "",
    ]
    for name in sorted(used_rodrigo.keys()):
        t = templates[name]
        lines.append(f"### `{name}`")
        lines.append("")
        lines.append(f"- **Idioma:** `{t['language']}` · **Categoría:** `{t['category']}` · **Estado hoy en WABA Rodrigo:** `{t['status']}`")
        lines.append(f"- **Usada en:** {', '.join(f'`{p}`' for p in used_rodrigo[name])}")
        lines.append("")
        lines.append("**Body actual (submitear tal cual al WABA del bot):**")
        lines.append("")
        lines.append("```")
        lines.append(t["body"])
        lines.append("```")
        lines.append("")
        # Componentes adicionales (header, footer, buttons) si los hay
        extras = [c for c in t.get("components", []) if c.get("type") != "BODY"]
        if extras:
            lines.append("**Componentes adicionales:**")
            for c in extras:
                lines.append(f"- `{c.get('type')}`: {json.dumps(c, ensure_ascii=False)[:200]}")
            lines.append("")
    return "\n".join(lines)


def main() -> int:
    if not FLUJOS.is_dir():
        print(f"ERROR: {FLUJOS} no existe", file=sys.stderr)
        return 1

    print("Cargando 92 plantillas canónicas…", file=sys.stderr)
    templates = load_templates()
    print(f"  {len(templates)} plantillas cargadas.", file=sys.stderr)

    print("Escaneando flujos…", file=sys.stderr)
    tree = scan_flows(templates)

    stamp = date.today().isoformat()
    out_mapeo = DOCS_DIR / f"mapeo-flujos-plantillas-{stamp}.md"
    out_inv = DOCS_DIR / f"inventario-flujos-clientify-{stamp}.md"
    out_reap = DOCS_DIR / f"plantillas-waba-rodrigo-a-reaprobar-{stamp}.md"

    out_mapeo.write_text(render_mapeo(tree, templates), encoding="utf-8")
    out_inv.write_text(render_inventario(tree, templates), encoding="utf-8")
    out_reap.write_text(render_reaprobar(tree, templates), encoding="utf-8")

    print(f"\n✅ Escritos:", file=sys.stderr)
    print(f"  {out_mapeo.relative_to(REPO_ROOT)}", file=sys.stderr)
    print(f"  {out_inv.relative_to(REPO_ROOT)}", file=sys.stderr)
    print(f"  {out_reap.relative_to(REPO_ROOT)}", file=sys.stderr)

    # Resumen
    total_flujos = sum(len(v) for v in tree.values())
    total_sub = sum(len(b.get("sub_sub", {})) for owner in tree.values() for b in owner.values())
    total_pngs = sum(
        len(b.get("plantillas", [])) + len(b.get("notemplate", [])) + len(b.get("freetext", []))
        + len(b.get("lanzador", [])) + len(b.get("accion", [])) + len(b.get("unknown", [])) + len(b.get("mismatch", []))
        for owner in tree.values() for b in owner.values()
    )
    print(f"\nResumen: {len(tree)} owners · {total_flujos} sub-carpetas · {total_sub} sub-sub-carpetas · {total_pngs} clasificados", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
