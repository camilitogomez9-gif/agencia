#!/usr/bin/env python3
"""
Reasignar el formId de los 8 calendarios GHL VTR a un formId nuevo.

Uso:
    python3 swap-form-id-calendarios.py <new_form_id>
    python3 swap-form-id-calendarios.py <new_form_id> --dry-run

Ej:
    python3 swap-form-id-calendarios.py aBcDeFgHiJkLmNoP

Cuando la agencia cree `form-aventurera` en UI (Sitios → Formularios) con el campo `atribuida_a` marcado como Oculto,
copiar su id y correr este script para hacer swap en los 8 calendarios de producción.

Requiere:
    PIT VTR en /clients/VTR_Venttur/06_docs/ghl-credentials.md línea `PIT_TOKEN = pit-...`
"""
import os, sys, json, urllib.request, urllib.error, time
from pathlib import Path

# Los 8 calendarios de producción
CALENDARS = [
    ("cal-internados",         "CIxOV100yyRFqPoa6LdK"),
    ("cal-intercambio",        "SiAPsk27X5yilff5bSS5"),
    ("cal-campamentos",        "981EzNS7jf9HhJNkL41W"),
    ("cal-viajes-educativos",  "j0jcAdaieJXaoPZBempp"),
    ("cal-educacion-superior", "RUjWx74NPK77FPUcs5ME"),
    ("cal-cursos-idiomas",     "5PxslDhdQxZeDcKmLYNq"),
    ("cal-pathway-alemania",   "oNN7oLWsNhQlWi7q7pDX"),
    ("cal-gap-year",           "Omgde6Ko8TGKYMtiUb1x"),
]
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

def load_pit():
    p = Path(__file__).resolve().parents[5] / "clients/VTR_Venttur/06_docs/ghl-credentials.md"
    for line in p.read_text().splitlines():
        if line.strip().startswith("PIT_TOKEN"):
            return line.split("=",1)[1].strip()
    raise SystemExit("PIT_TOKEN no encontrado")

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 swap-form-id-calendarios.py <new_form_id> [--dry-run]"); sys.exit(2)
    new_form = sys.argv[1]
    dry = "--dry-run" in sys.argv
    tok = load_pit()

    print(f"═══ Swap formId → {new_form} en 8 calendarios de VTR ═══")
    for name, cal_id in CALENDARS:
        if dry:
            print(f"  ⏹  DRY: {name} ({cal_id}) — formId={new_form}, stickyContact=true")
            continue
        body = json.dumps({"formId": new_form, "stickyContact": True}).encode()
        req = urllib.request.Request(
            f"https://services.leadconnectorhq.com/calendars/{cal_id}",
            data=body, method="PUT",
            headers={"Authorization": f"Bearer {tok}", "Version": "2021-07-28", "User-Agent": UA, "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                r.read()
                print(f"  ✅ {name}")
        except urllib.error.HTTPError as e:
            print(f"  ❌ {name} → {e.code}: {e.read().decode()[:150]}")
        time.sleep(0.3)
    if dry:
        print("\n⏹  DRY-RUN — no se aplicó nada.")

if __name__ == "__main__":
    main()
