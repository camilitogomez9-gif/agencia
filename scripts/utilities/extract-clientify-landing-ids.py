#!/usr/bin/env python3
"""Extrae IDs de meeting/superform/webform de landings de Clientify (VTR).

Recorre un `landings.md` con la estructura:
    # Título de sub-carpeta

    https://promo.venttur.com/algo
    https://promo.venttur.com/otra

Para cada URL, fetchea el HTML y anota debajo:
    https://promo.venttur.com/algo
      - meeting_id: 6689
      - webform_id: 161720
      - og_title: Agendamiento Estudiar y Trabajar

Idempotente: si ya hay anotaciones (líneas indentadas con "  - "), las reemplaza.

Uso:
    python3 scripts/utilities/extract-clientify-landing-ids.py "/ruta/a/landings.md"
"""

from __future__ import annotations

import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

MEETING_RE = re.compile(r"app\.clientify\.com/meetings/script/(\d+)\.js")
SUPERFORM_RE = re.compile(r"api\.clientify\.net/web-marketing/superforms/script/(\d+)\.js")
WEBFORM_RE = re.compile(r"api\.clientify\.net/web-marketing/webforms/process/(\d+)/?")
OGTITLE_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]+)"')

URL_LINE_RE = re.compile(r"^\s*(https?://\S+)\s*$")
ANNOTATION_RE = re.compile(r"^  - (meeting_id|superform_id|webform_id|og_title|error): ")

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"


def fetch(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept-Language": "es-MX,es;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    # Clientify sirve UTF-8; forzamos decodificación tolerante
    return raw.decode("utf-8", errors="replace")


def extract_ids(html: str) -> dict[str, str]:
    out: dict[str, str] = {}
    if m := MEETING_RE.search(html):
        out["meeting_id"] = m.group(1)
    if m := SUPERFORM_RE.search(html):
        out["superform_id"] = m.group(1)
    if m := WEBFORM_RE.search(html):
        out["webform_id"] = m.group(1)
    if m := OGTITLE_RE.search(html):
        out["og_title"] = m.group(1).strip()
    return out


def annotate(url: str) -> list[str]:
    """Devuelve las líneas de anotación (indentadas con 2 espacios) para una URL."""
    try:
        html = fetch(url)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        return [f"  - error: {e}"]
    except Exception as e:  # noqa: BLE001
        return [f"  - error: {type(e).__name__}: {e}"]

    ids = extract_ids(html)
    if not ids:
        return ["  - error: no IDs found in HTML"]
    order = ["meeting_id", "superform_id", "webform_id", "og_title"]
    return [f"  - {k}: {ids[k]}" for k in order if k in ids]


def process(md_path: Path) -> None:
    lines = md_path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    i = 0
    total_urls = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        m = URL_LINE_RE.match(line)
        if m:
            url = m.group(1)
            # descartar http(s) que no sean landings de Clientify/Venttur — pero por defecto anotamos todas
            total_urls += 1
            print(f"[{total_urls}] {url}", file=sys.stderr)
            # saltar anotaciones existentes debajo de esta URL
            j = i + 1
            while j < len(lines) and ANNOTATION_RE.match(lines[j]):
                j += 1
            new_ann = annotate(url)
            out.extend(new_ann)
            i = j
            continue
        i += 1

    md_path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"\n{total_urls} URLs procesadas → {md_path}", file=sys.stderr)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Uso: {sys.argv[0]} <ruta a landings.md>", file=sys.stderr)
        return 1
    md_path = Path(sys.argv[1]).expanduser()
    if not md_path.is_file():
        print(f"No es un archivo: {md_path}", file=sys.stderr)
        return 1
    process(md_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
