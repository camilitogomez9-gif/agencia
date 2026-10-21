#!/usr/bin/env python3
"""Repara bugs de naming en el snapshot Clientify según convención.

3 tipos de fix:
  1. `_notemplate_X.png` con sidecar `_freetext_X.txt` → renombrar el `.png` a `_freetext_X.png`.
     Alinea con la convención: `.txt` sidecar solo aplica a `_freetext_`.

  2. `_continuacion_*` → renombrar a `_accion2_*` (subíndice según convención de acciones múltiples).
     Alternativa considerada: `_notemplate_`. Se prefiere `_accion2_` porque suele indicar segunda
     acción/detalle de un flujo, coherente con `_accion_`.

  3. Espacios parasitarios después del prefijo (`_accion_ Foo.png` → `_accion_foo.png`).
     Normaliza a snake_case: espacios → `_`, mayúsculas → minúsculas. Solo aplica al slug (después
     del prefijo). NO toca el prefijo mismo ni la extensión.

Uso:
    python3 fix-naming-clientify-snapshot.py                  # dry-run
    python3 fix-naming-clientify-snapshot.py --apply           # aplica
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path("/Users/camilo/Downloads/Clientify")
FLUJOS_ROOT = ROOT / "flujos de trabajo"

# Prefijos válidos de la convención (7 prefijos + sin-prefijo)
VALID_PREFIXES = ["_notemplate_", "_freetext_", "_lanzador_", "_accion_", "_accion2_", "_accion3_", "_unknown_"]

# Prefijo no canónico a renombrar: `_continuacion_` → `_accion3_`
# (verificado en caso `mensaje_1_seguimiento_ema`: _accion_ y _accion2_ ya existen; _continuacion_ es la 3a acción)
LEGACY_PREFIX = "_continuacion_"
LEGACY_NEW_PREFIX = "_accion3_"


def split_name(filename: str) -> tuple[str, str, str]:
    """Devuelve (prefix, slug, ext). Prefix vacío si no matchea. Ext incluye el punto."""
    p = Path(filename)
    ext = p.suffix
    stem = p.stem
    for pref in VALID_PREFIXES + [LEGACY_PREFIX]:
        if stem.startswith(pref):
            return (pref, stem[len(pref):], ext)
    return ("", stem, ext)


def slugify(s: str) -> str:
    """Normaliza el slug: espacios → `_`, colapsa `__+` → `_`, quita espacios laterales.
    NO fuerza lowercase (algunos slugs mantienen convención del cliente).
    """
    s = s.strip()
    s = re.sub(r"\s+", "_", s)  # espacios a underscore
    s = re.sub(r"_+", "_", s)   # colapsar múltiples underscores
    return s


def main() -> int:
    apply = "--apply" in sys.argv

    if not FLUJOS_ROOT.is_dir():
        print(f"ERROR: {FLUJOS_ROOT} no existe", file=sys.stderr)
        return 1

    print(f"{'APLICANDO' if apply else 'DRY-RUN'}\n")

    fixes: list[tuple[Path, Path, str]] = []  # (src, dst, motivo)
    warnings: list[tuple[Path, str]] = []

    # Recorrer todos los .png y .txt bajo flujos de trabajo/
    for f in sorted(FLUJOS_ROOT.rglob("*")):
        if f.is_dir() or f.name == ".DS_Store":
            continue
        prefix, slug, ext = split_name(f.name)
        new_prefix = prefix
        new_slug = slug

        # Fix 1: _continuacion_ → _accion2_
        if prefix == LEGACY_PREFIX:
            new_prefix = LEGACY_NEW_PREFIX

        # Fix 3: espacios parasitarios en el slug
        new_slug = slugify(new_slug)

        # Fix 2 (solo para .png): si es _notemplate_X pero existe sidecar _freetext_X.txt, renombrar a _freetext_
        if prefix == "_notemplate_" and ext.lower() == ".png":
            sidecar = f.parent / f"_freetext_{slug}.txt"
            if sidecar.exists():
                new_prefix = "_freetext_"

        new_name = f"{new_prefix}{new_slug}{ext}"
        if new_name != f.name:
            new_path = f.parent / new_name
            if new_path.exists() and new_path != f:
                warnings.append((f, f"colisión: {new_path.name} ya existe"))
                continue
            motivos = []
            if new_prefix != prefix:
                motivos.append(f"prefix `{prefix}` → `{new_prefix}`")
            if new_slug != slug:
                motivos.append(f"slug `{slug}` → `{new_slug}`")
            fixes.append((f, new_path, " · ".join(motivos)))

    # Reportar
    print(f"CAMBIOS PROPUESTOS: {len(fixes)}\n")
    for src, dst, motivo in fixes:
        rel_src = src.relative_to(ROOT)
        rel_dst = dst.relative_to(ROOT)
        print(f"  {rel_src.parent}/")
        print(f"    {src.name}")
        print(f"    → {dst.name}")
        print(f"      ({motivo})")
        print()

    if warnings:
        print(f"\nAVISOS: {len(warnings)}")
        for f, w in warnings:
            print(f"  ⚠ {f.relative_to(ROOT)}: {w}")

    if apply:
        applied = 0
        for src, dst, _ in fixes:
            src.rename(dst)
            applied += 1
        print(f"\n✅ APLICADO. {applied} renames.")
    else:
        print("\nDry-run. Corré con `--apply` para renombrar.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
