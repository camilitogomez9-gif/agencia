#!/usr/bin/env python3
"""
Generador de links únicos por aventurera × programa para atribución (§2.2 de la guía ejecutable).

Dos modos:
    --modo widget (default): link directo al widget booking GHL.
        URL: https://api.leadconnectorhq.com/widget/booking/<cal_id>?atribuida_a=<slug>
    --modo landing: link a la landing GHL Funnels que embeba el calendario.
        URL: https://promo.venttur.com/<slug-landing>?atribuida_a=<slug>
        Requiere que existan las 10 landings publicadas en `promo.venttur.com`
        (§PAR-A · Batch E). El tracking `?atribuida_a=` cae a `attributionSource.url`
        en el Contact GHL y se lee on-demand con `scripts/reporte-aventureras.py --full`.

Uso:
    python3 generar-links-aventureras.py                                    # widget, hardcoded
    python3 generar-links-aventureras.py --csv aventureras.csv              # widget, desde CSV
    python3 generar-links-aventureras.py --modo landing --output-csv .csv   # landing, salida CSV
    python3 generar-links-aventureras.py --modo landing --csv aventureras.csv --output-md .md

Formato del CSV de input (headers): slug,programas
    slug es el que va en ?atribuida_a=<slug>
    programas es lista separada por | (ej: "internados|intercambio|campamentos")
    O usar "TODOS" para asignar los 8 programas.

Los cal_ids de los 8 calendarios de producción están hardcodeados abajo, generados por API el 21/9.
"""
import csv, sys, os, argparse
from pathlib import Path

# Los 8 calendarios de producción (ver 06_docs/ids-recursos-ghl-vtr.md).
# Cada tupla: (nombre_display, cal_id, landing_slug para modo landing)
# landing_slug = las landings de CALENDARIO (tipo C, en landings-ghl/calendarios/) — mismo destino que los
# botones de las madres aventureras, así la atribución es coherente por las 2 vías (madre o link directo).
CALENDARS = {
    "internados":        ("Internados (Rodrigo)",           "CIxOV100yyRFqPoa6LdK", "Internados-Calendario"),
    "intercambio":       ("Intercambio (Rodrigo)",          "SiAPsk27X5yilff5bSS5", "Intercambio-Calendario"),
    "campamentos":       ("Campamentos (Rodrigo)",          "981EzNS7jf9HhJNkL41W", "Campamentos-Calendario"),
    "viajes-educativos": ("Viajes educativos (Andrés)",     "j0jcAdaieJXaoPZBempp", "ViajesEducativos-Calendario"),
    "educacion-superior":("Educación superior (Andrés)",    "RUjWx74NPK77FPUcs5ME", "EducacionSuperior-Calendario"),
    "cursos-idiomas":    ("Cursos de idiomas (Andrés)",     "5PxslDhdQxZeDcKmLYNq", "CursosIdiomas-Calendario"),
    "pathway-alemania":  ("Pathway Alemania (Andrés)",      "oNN7oLWsNhQlWi7q7pDX", "PathwayAlemania-Calendario"),
    "gap-year":          ("Gap Year (Andrés)",              "Omgde6Ko8TGKYMtiUb1x", "GapYear-Calendario"),
}

# Placeholder — reemplazar con los slugs reales que confirme el cliente (§6 accionable #3)
AVENTURERAS_DEFAULT = [
    ("maria-perez",       "TODOS"),
    ("juana-gonzalez",    "internados|intercambio"),
    ("luisa-fernandez",   "TODOS"),
    ("ana-martinez",      "gap-year"),
    # ... etc (30-ish)
]

WIDGET_BASE = "https://api.leadconnectorhq.com/widget/booking"
LANDING_BASE = "https://promo.venttur.com"  # dominio público (hardcodeado en rescate/Meta); vtr.[TU-DOMINIO] era staging


def build_links(aventureras, modo="widget"):
    out = []
    for slug, programas in aventureras:
        if programas.strip().upper() == "TODOS":
            keys = list(CALENDARS.keys())
        else:
            keys = [k.strip() for k in programas.split("|") if k.strip() in CALENDARS]
        for k in keys:
            name, cal_id, landing_slug = CALENDARS[k]
            if modo == "widget":
                url = f"{WIDGET_BASE}/{cal_id}?atribuida_a={slug}"
            elif modo == "landing":
                url = f"{LANDING_BASE}/{landing_slug}?atribuida_a={slug}"
            else:
                raise ValueError(f"modo desconocido: {modo}")
            out.append({
                "aventurera": slug,
                "programa": k,
                "nombre_calendario": name,
                "cal_id": cal_id,
                "landing_slug": landing_slug,
                "modo": modo,
                "url": url
            })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", help="CSV input con headers 'slug,programas'")
    ap.add_argument("--output-md", help="MD output")
    ap.add_argument("--output-csv", help="CSV output")
    ap.add_argument("--modo", choices=["widget", "landing"], default="widget",
                    help="widget = link al booking GHL (default); "
                         "landing = URL a landing bajo promo.venttur.com")
    args = ap.parse_args()

    if args.csv:
        with open(args.csv) as f:
            reader = csv.DictReader(f)
            aventureras = [(r["slug"], r.get("programas","TODOS")) for r in reader]
    else:
        aventureras = AVENTURERAS_DEFAULT
        print("⚠️ usando AVENTURERAS_DEFAULT — pasar --csv con los slugs reales del cliente")

    if args.modo == "landing":
        print(f"📍 modo landing: URLs bajo {LANDING_BASE}/<Programa>-Agendar?atribuida_a=<slug>")
        print(f"   Requiere que las 10 landings estén publicadas en promo.venttur.com (Batch E · landings-ghl/)")

    links = build_links(aventureras, modo=args.modo)
    print(f"Generados {len(links)} links "
          f"({len(set(l['aventurera'] for l in links))} aventureras × ~4-8 programas c/u · modo={args.modo})")

    if args.output_md:
        with open(args.output_md, "w") as f:
            f.write(f"# Links aventureras × programas (modo: {args.modo})\n\n")
            if args.modo == "landing":
                f.write(f"Cada URL apunta a una landing GHL Funnels bajo `{LANDING_BASE}`. ")
                f.write("El query param `?atribuida_a=<slug>` cae a `attributionSource.url` en el Contact GHL. ")
                f.write("Lee on-demand con `scripts/reporte-aventureras.py --full`.\n\n")
            current = None
            for l in links:
                if l['aventurera'] != current:
                    current = l['aventurera']
                    f.write(f"\n## {current}\n\n")
                f.write(f"- **{l['programa']}** ({l['nombre_calendario']}): `{l['url']}`\n")
        print(f"📄 MD: {args.output_md}")

    if args.output_csv:
        with open(args.output_csv, "w", newline="") as f:
            fieldnames = ["aventurera", "programa", "nombre_calendario", "cal_id", "landing_slug", "modo", "url"]
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader(); w.writerows(links)
        print(f"📄 CSV: {args.output_csv}")

    if not (args.output_md or args.output_csv):
        for l in links[:15]:
            print(f"  · {l['aventurera']:<20} × {l['programa']:<20} → {l['url']}")
        if len(links) > 15: print(f"  ... {len(links)-15} más (--output-md/--output-csv para lista completa)")

if __name__ == "__main__":
    main()
