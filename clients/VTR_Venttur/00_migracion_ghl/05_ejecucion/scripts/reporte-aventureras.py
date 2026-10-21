#!/usr/bin/env python3
"""
Reporte de atribución de leads a aventureras (VTR migración GHL).

Lee contactos GHL, parsea `attributionSource.url` (y `lastAttributionSource.url` como fallback)
buscando el query param `?atribuida_a=<slug>`, agrupa por slug y emite:

- Salida por stdout: tabla con conteo de leads por aventurera.
- CSV opcional (`--csv <ruta>`): 3 columnas → `slug_aventurera`, `total_leads`, `contact_ids`.

Es reemplazo del workflow GHL "Fallback · atribuida_a desde attributionSource" (§5.6).
Corre on-demand — no hay dependencia con custom fields, workflows ni triggers.

Uso:
    python3 reporte-aventureras.py                                    # stdout
    python3 reporte-aventureras.py --csv reporte-<fecha>.csv          # + CSV
    python3 reporte-aventureras.py --detalle                          # incluye cada contact_id + email

Requiere: PIT VTR en clients/VTR_Venttur/06_docs/ghl-credentials.md línea `PIT_TOKEN = pit-...`.
"""
import os, sys, json, re, time, argparse, urllib.request, urllib.error
from pathlib import Path
from collections import defaultdict
from urllib.parse import unquote

LOC = "7aXb4JCKsWV5nUyBXeSF"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
RE_ATRIBUIDA = re.compile(r'[?&]atribuida_a=([^&#?]+)')  # corta en "?": los redirects de GHL dejan ?x?fbclid=y


def load_pit():
    p = Path(__file__).resolve().parents[5] / "clients/VTR_Venttur/06_docs/ghl-credentials.md"
    for line in p.read_text().splitlines():
        if line.strip().startswith("PIT_TOKEN"):
            return line.split("=", 1)[1].strip()
    raise SystemExit("PIT_TOKEN no encontrado en ghl-credentials.md")


def http_get(url, tok):
    req = urllib.request.Request(
        url, method="GET",
        headers={"Authorization": f"Bearer {tok}", "Version": "2021-07-28", "User-Agent": UA},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def get_contact(cid, tok):
    return http_get(f"https://services.leadconnectorhq.com/contacts/{cid}", tok).get("contact", {})


def iter_contacts_page(tok, start_after_id=None, start_after=None):
    url = f"https://services.leadconnectorhq.com/contacts/?locationId={LOC}&limit=100"
    if start_after_id and start_after:
        url += f"&startAfterId={start_after_id}&startAfter={start_after}"
    return http_get(url, tok)


def parse_slug(url):
    if not url:
        return None
    m = RE_ATRIBUIDA.search(url)
    return unquote(m.group(1)) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", help="Ruta CSV de salida (opcional).")
    ap.add_argument("--detalle", action="store_true", help="Incluir contact_id + email por aventurera.")
    ap.add_argument("--full", action="store_true",
                    help="Hacer GET singular por cada contact (más lento, pero attributionSource completo).")
    args = ap.parse_args()

    tok = load_pit()
    conteo = defaultdict(list)  # slug → [{'id':..., 'email':..., 'url':...}]
    total_contacts = 0
    start_after_id, start_after = None, None
    page = 0

    print(f"═══ Escaneando contactos VTR (loc {LOC}) ═══", file=sys.stderr)
    while True:
        page += 1
        try:
            data = iter_contacts_page(tok, start_after_id, start_after)
        except urllib.error.HTTPError as e:
            print(f"❌ HTTP {e.code} en página {page}: {e.read().decode()[:200]}", file=sys.stderr)
            break
        contacts = data.get("contacts", [])
        if not contacts:
            break
        for c in contacts:
            total_contacts += 1
            cid = c.get("id")
            email = c.get("email") or ""
            url = None
            if args.full:
                try:
                    full = get_contact(cid, tok)
                    attr_url = (full.get("attributionSource") or {}).get("url") or ""
                    last_url = (full.get("lastAttributionSource") or {}).get("url") or ""
                    # preferir el que contenga ?atribuida_a= (validado 21/9 con Test B PREP-2:
                    # en VTR el slug suele venir en lastAttributionSource, no en attributionSource)
                    if "atribuida_a=" in last_url:
                        url = last_url
                    elif "atribuida_a=" in attr_url:
                        url = attr_url
                    else:
                        url = attr_url or last_url
                except Exception as e:
                    print(f"  ⚠ error GET {cid}: {e}", file=sys.stderr)
                time.sleep(0.05)
            else:
                # el listado no trae attributionSource poblado → sirve solo si --full
                pass
            slug = parse_slug(url)
            if slug:
                conteo[slug].append({"id": cid, "email": email, "url": url})
        # paginación
        meta = data.get("meta") or {}
        start_after_id = meta.get("startAfterId")
        start_after = meta.get("startAfter")
        print(f"  página {page}: +{len(contacts)} contactos · total {total_contacts}", file=sys.stderr)
        if not start_after_id or not start_after:
            break
        time.sleep(0.1)

    if not args.full:
        print("⚠  Corrido sin --full: el listado GHL no trae attributionSource. Los conteos serán 0.", file=sys.stderr)
        print("   Volvé a correr con --full para obtener datos reales (más lento, ~1 seg cada 20 contactos).", file=sys.stderr)

    # emitir tabla stdout
    print(f"\n═══ Reporte aventureras · {total_contacts} contactos escaneados ═══")
    if not conteo:
        print("Sin resultados (0 contactos con ?atribuida_a=<slug>).")
    else:
        print(f"{'aventurera':30s} {'leads':>8s}")
        print("─" * 40)
        for slug, leads in sorted(conteo.items(), key=lambda kv: -len(kv[1])):
            print(f"{slug[:30]:30s} {len(leads):>8d}")
            if args.detalle:
                for l in leads:
                    print(f"    · {l['email']:40s} · {l['id']}")

    # CSV opcional
    if args.csv:
        import csv
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["slug_aventurera", "total_leads", "contact_ids"])
            for slug, leads in sorted(conteo.items(), key=lambda kv: -len(kv[1])):
                w.writerow([slug, len(leads), "|".join(l["id"] for l in leads)])
        print(f"\nCSV escrito: {args.csv}", file=sys.stderr)


if __name__ == "__main__":
    main()
