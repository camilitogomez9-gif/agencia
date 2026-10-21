#!/usr/bin/env python3
"""
D2 · Plantillas de presupuesto (estimate templates) en GHL, replicando los presupuestos de Clientify.

De dónde sale cada dato (API de Clientify, lectura, 23/9, 242 presupuestos):
  · Emisor: Viajes y Experiencias GARDE S de RL de CV · nombre comercial Venttur Education & Travel ·
    RFC VEG221012DA6 · Juan Palomar y Arias 616, Guadalajara, Jalisco 44670 · contacto@venttur.com.
  · IVA: va por producto (16% fees/inscripciones, 0% cuotas administrativas y programas de terceros). En GHL
    ya quedó en cada producto (impuesto "IVA 16%", exclusivo), así que cada plantilla lleva el IVA de su ítem.
  · Términos: cambian por programa (Perfilamiento EMA suma pago total + garantía) y la cuenta bancaria cambia
    por asesor. Se copian los del presupuesto más reciente de cada asesor (al 18/9):
      Rodrigo    → Banorte   (00259 Perfilamiento, 00251 Fee)
      Juan José  → BBVA      (00255 Pathway)
      Andrés     → Banamex + Banorte (00260 Pre-evaluación Pathway)
    Qué cuenta va en cada caso lo confirma Venttur (A9 de la guía); si cambia, se edita la plantilla.

Uso:
  python3 crear-plantillas-presupuesto-ghl.py            # dry-run: muestra lo que crearía
  python3 crear-plantillas-presupuesto-ghl.py --execute  # crea las que falten (idempotente por nombre), de a una
"""
import json, re, sys, time, urllib.request, urllib.error
from pathlib import Path

CREDS = Path("/Users/camilo/Downloads/camilo-workspace/clients/VTR_Venttur/06_docs/ghl-credentials.md")
API = "https://services.leadconnectorhq.com"
TAX_IVA = "6ab4155291704e023e6d8625"  # "IVA 16%" creado en Pagos › Configuración › Tasas (23/9)


def cred(k):
    return re.search(rf"{k}\s*=\s*(\S+)", CREDS.read_text()).group(1)


PIT, LOC = cred("PIT_TOKEN"), cred("LOCATION_ID")


def call(method, path, body=None):
    req = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {PIT}", "Version": "2021-07-28",
                                          "Accept": "application/json", "Content-Type": "application/json",
                                          "User-Agent": "curl/8.4.0"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.getcode(), json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:600]


BENEF = "<p>Beneficiario: Viajes y Experiencias GARDE, S. DE R.L. DE C.V.</p>"
BANORTE = "<p>Banco: BANORTE<br>Cuenta CLABE MXN: 072 320 013237430986<br>Número de cuenta: 132 374 3098</p>"
BBVA = "<p>Banco: BBVA<br>Cuenta CLABE MXN: 012 320 001196818093<br>Número de cuenta: 011 968 1809</p>"
BANAMEX = "<p>Banco: BANAMEX<br>Cuenta CLABE MXN: 002 320 701347461635</p>"
CIERRE = ("<p>Correo: contacto@venttur.com</p>"
          "<p><em>*Favor de enviar comprobante de pago a cualquier representante de Venttur Education &amp; Travel*</em></p>")
EMA = ("<p>Se requiere liquidar el pago del perfilamiento EMA en su totalidad para proceder a agendar la Evaluación "
       "individual y familiar.</p><p><strong>GARANTÍA</strong> de reembolso del 100% del programa de perfilamiento EMA "
       "si las instituciones presentadas por Venttur Education &amp; Travel no cumplen con las expectativas de tu "
       "familia.</p>")

# nombre de plantilla → (producto por defecto, términos)
PLANTILLAS = {
    # GHL limita el nombre a 40 caracteres
    "Perfilamiento EMA · Rodrigo (Banorte)": ("Perfilamiento 1", EMA + BENEF + BANORTE + CIERRE),
    "Presupuesto · Rodrigo (Banorte)": ("Perfilamiento 2", BENEF + BANORTE + CIERRE),
    "Presupuesto · Juan José (BBVA)": ("Primera Inscripción Programa Pathway", BENEF + BBVA + CIERRE),
    "Presupuesto · Andrés (Banamex/Banorte)": ("Primera Inscripción Programa Pathway", BENEF + BANAMEX + BANORTE + CIERRE),
}

NEGOCIO = {
    "name": "Venttur Education & Travel",
    "phoneNo": "+523320016463",
    "address": {"addressLine1": "Juan Palomar y Arias 616", "city": "Guadalajara", "state": "Jalisco",
                "countryCode": "MX", "postalCode": "44670"},
    "website": "https://www.venttur.com",
}
# La razón social y el RFC no tienen campo propio en businessDetails (customValues pide objetos sin esquema
# documentado): van al inicio de los términos.
EMISOR = ("<p><strong>Viajes y Experiencias GARDE S de RL de CV</strong> · RFC VEG221012DA6<br>"
          "Venttur Education &amp; Travel</p>")


def item(prod):
    code, pr = call("GET", f"/products/{prod['_id']}/price?locationId={LOC}")
    price = pr["prices"][0]
    it = {"name": prod["name"], "description": "", "productId": prod["_id"], "priceId": price["_id"],
          "amount": price["amount"], "qty": 1, "currency": "MXN", "type": "one_time", "taxes": []}
    if prod.get("isTaxesEnabled") and TAX_IVA in (prod.get("taxes") or []):
        it["taxes"] = [{"_id": TAX_IVA, "name": "IVA 16%", "rate": 16, "calculation": "exclusive"}]
        it["taxInclusive"] = False
    return it


def main():
    execute = "--execute" in sys.argv
    code, loc = call("GET", f"/locations/{LOC}")
    negocio = dict(NEGOCIO, logoUrl=loc["location"].get("logoUrl", ""))
    code, pl = call("GET", f"/products/?locationId={LOC}&limit=100")
    productos = {p["name"]: p for p in pl["products"]}
    code, ex = call("GET", f"/invoices/estimate/template?altId={LOC}&altType=location&limit=100&offset=0")
    existentes = {t["name"]: t for t in ex.get("data", [])}
    for nombre, (prod, terms) in PLANTILLAS.items():
        if nombre in existentes:
            print(f"= ya existe  {nombre}  ({existentes[nombre].get('_id')})")
            continue
        body = {"altId": LOC, "altType": "location", "name": nombre, "title": "PRESUPUESTO", "currency": "MXN",
                "liveMode": True, "businessDetails": negocio, "items": [item(productos[prod])],
                "discount": {"value": 0, "type": "percentage"}, "termsNotes": EMISOR + terms,
                "estimateNumberPrefix": "VTR-", "automaticTaxesEnabled": False}
        if not execute:
            it = body["items"][0]
            print(f"→ crearía    {nombre}  · {it['name']} ${it['amount']} {'+IVA' if it['taxes'] else 'sin IVA'}")
            continue
        code, r = call("POST", "/invoices/estimate/template", body)
        ok = code in (200, 201)
        print(f"{'✓' if ok else '✗ ' + str(code)}  {nombre}  {r.get('_id') if isinstance(r, dict) else r}")
        if not ok:
            raise SystemExit("Corto acá: no sigo creando con un body que GHL rechaza.")
        time.sleep(0.5)
    if not execute:
        print("\n[DRY-RUN] Agregá --execute para crearlas.")


if __name__ == "__main__":
    main()
