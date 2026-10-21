#!/usr/bin/env python3
"""Merge del zip de Camilo (Andrés + Max) sobre la copia local de Clientify.

Reglas del merge:
  1. NUNCA sobrescribe un archivo existente. Reporta conflictos y skipea.
  2. Excluye `Mauricio/` y `Rodrigo/` (owners de la agencia). Skipea con reporte.
  3. Excluye `Diego/` (descartado 18/9 tarde). Skipea con reporte.
  4. Excluye `README.md` y `PROMPT-PARA-CLAUDE-DE-CAMILO.md` en raíz (ya más nuevos en destino).
  5. Excluye `landings y calendarios/Mauricio/landings.md` (la agencia tiene la versión con aventureras).
  6. Trae de Camilo: `landings y calendarios/{Andrés,Max}/landings.md` y `flujos de trabajo/Max/**`.

Uso:
    python3 merge-camilo-snapshot.py "/ruta/al/zip"          # dry-run (default)
    python3 merge-camilo-snapshot.py "/ruta/al/zip" --apply  # aplica
"""

from __future__ import annotations

import filecmp
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path


def to_nfc(s: str) -> str:
    """Normaliza un string a NFC (macOS filesystem convention)."""
    return unicodedata.normalize("NFC", s)

DEST = Path("/Users/camilo/Downloads/Clientify")

# Prefijos de path (dentro del zip, sin `Clientify/`) que se skipean por decisión de la sesión
SKIP_PREFIXES = [
    "flujos de trabajo/Mauricio",   # owner la agencia
    "flujos de trabajo/Rodrigo",    # owner la agencia
    "flujos de trabajo/Diego",      # descartado 18/9
    "landings y calendarios/Mauricio",  # la agencia tiene el md con aventureras cargadas
]

SKIP_ROOT_FILES = {"README.md", "PROMPT-PARA-CLAUDE-DE-CAMILO.md"}

# Remapear paths corruptos del zip (doble encoding UTF-8 → Latin-1 → UTF-8)
# Solo aplica a partes de path que Camilo trabaja (Andrés). El resto de nombres corruptos
# vive en carpetas que se skipean (Rodrigo, Diego, Mauricio).
PATH_REMAP = {
    "Andr├®s": "Andrés",
}


def should_skip(rel: Path) -> str | None:
    """Devuelve motivo si hay que skipear; None si se procesa."""
    parts = rel.parts
    if not parts:
        return "root"
    if parts[0] in SKIP_ROOT_FILES:
        return f"root file (existe versión nueva en destino)"
    # Skipeo por prefijo
    joined = "/".join(parts)
    for pref in SKIP_PREFIXES:
        if joined == pref or joined.startswith(pref + "/"):
            return f"prefijo excluido ({pref})"
    return None


def files_equal(a: Path, b: Path) -> bool:
    try:
        return filecmp.cmp(a, b, shallow=False)
    except Exception:
        return False


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: merge-camilo-snapshot.py <zip> [--apply]", file=sys.stderr)
        return 1
    zip_path = Path(sys.argv[1]).expanduser()
    apply = "--apply" in sys.argv

    if not zip_path.is_file():
        print(f"ERROR: zip no existe: {zip_path}", file=sys.stderr)
        return 1
    if not DEST.is_dir():
        print(f"ERROR: destino no existe: {DEST}", file=sys.stderr)
        return 1

    print(f"{'APLICANDO' if apply else 'DRY-RUN'} · zip: {zip_path}")
    print(f"Destino: {DEST}\n")

    # Descomprimir a tmp
    tmpdir = Path(tempfile.mkdtemp(prefix="camilo-merge-"))
    r = subprocess.run(
        ["unzip", "-q", "-o", str(zip_path), "-d", str(tmpdir)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(f"ERROR unzip: {r.stderr}", file=sys.stderr)
        return 1

    src_root = tmpdir / "Clientify"
    if not src_root.is_dir():
        print(f"ERROR: zip no contiene 'Clientify/' en raíz", file=sys.stderr)
        return 1

    # Contadores
    new_files: list[Path] = []
    identical: list[Path] = []
    conflicts: list[tuple[Path, Path]] = []
    zip_wins: list[tuple[Path, str]] = []   # sobrescrito porque zip tenía más contenido (solo landings.md)
    skipped: list[tuple[Path, str]] = []

    # Recorrer todos los archivos reales del zip
    for src in sorted(src_root.rglob("*")):
        if src.is_dir():
            continue
        if src.name == ".DS_Store":
            continue
        rel = src.relative_to(src_root)
        # (1) Remapear partes corruptas → nombre correcto
        # (2) Normalizar path a NFC
        rel_nfc = Path(*[to_nfc(PATH_REMAP.get(p, p)) for p in rel.parts])
        reason = should_skip(rel_nfc)
        if reason:
            skipped.append((rel_nfc, reason))
            continue
        dst = DEST / rel_nfc
        if dst.exists():
            if files_equal(src, dst):
                identical.append(rel_nfc)
            else:
                # Excepción: si es un landings.md y el zip tiene más contenido, gana el zip
                if dst.name == "landings.md":
                    src_lines = len(src.read_text(encoding="utf-8").splitlines())
                    dst_lines = len(dst.read_text(encoding="utf-8").splitlines())
                    if src_lines > dst_lines * 1.5:
                        zip_wins.append((rel_nfc, f"zip: {src_lines} líneas vs destino: {dst_lines}"))
                        if apply:
                            shutil.copy2(src, dst)
                        continue
                conflicts.append((rel_nfc, dst))
        else:
            new_files.append(rel_nfc)
            if apply:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

    # Reporte
    print("=" * 70)
    print(f"NUEVOS (traer del zip): {len(new_files)}")
    for r in new_files:
        print(f"  + {r}")
    print()
    print(f"IDÉNTICOS (skipear silencioso): {len(identical)}")
    if len(identical) <= 20:
        for r in identical:
            print(f"  = {r}")
    print()
    print(f"ZIP GANA (landings.md con más contenido — sobrescribe): {len(zip_wins)}")
    for r, note in zip_wins:
        print(f"  → {r}  ({note})")
    print()
    print(f"CONFLICTOS (destino tiene distinto, NO sobrescribo): {len(conflicts)}")
    for r, d in conflicts:
        print(f"  ! {r}  ← revisar manualmente si querés integrar")
    print()
    print(f"SKIPPED por regla: {len(skipped)}")
    reasons: dict[str, int] = {}
    for _, reason in skipped:
        reasons[reason] = reasons.get(reason, 0) + 1
    for reason, n in sorted(reasons.items(), key=lambda x: -x[1]):
        print(f"  · {reason}: {n} archivos")
    print()
    print("=" * 70)
    if apply:
        print(f"✅ APLICADO. {len(new_files)} archivos copiados.")
    else:
        print("Dry-run OK. Re-corré con `--apply` para copiar los NUEVOS.")

    # Limpieza
    shutil.rmtree(tmpdir, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
