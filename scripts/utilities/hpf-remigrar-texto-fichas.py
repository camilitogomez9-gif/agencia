#!/usr/bin/env python3
"""
HPF · re-migra el TEXTO de las fichas desde el CURL de Airtable.

POR QUÉ
La migración copió el campo `descripcion` de Airtable, que está desactualizado. Cada fila tiene
además el `CURL`: la captura del envío REAL que hacía Kommo, o sea el texto vigente. De ahí salen
los precios que hoy están $1 por debajo ($24/$29 en vez de $25/$30).

EL REGEX DEL BRIEF ESTÁ ROTO — no usarlo
    "text":"(.*?)","crm_dialog_id"      ← pierde filas
Hay DOS formas de payload en la columna CURL: unas cierran con `crm_dialog_id` y otras con
`crm_entity`. Con el regex de arriba se pierden 3 filas de Boda, y una de ellas es
`Pantuflas boda`, o sea uno de los targets. Acá se parsea el JSON de `--data-raw` de verdad.

TRES SUPERFICIES, NO UNA (igual que hpf-actualizar-catalogo-mandiles.py)
  1. El record del custom object en GHL — PUT con `?locationId=` en la QUERY (en el body da 422,
     sin él 404). Devuelve 2xx aunque no escriba, así que se relee por GET DIRECTO, nunca por
     `records/search`, que tiene lag de indexación.
  2. La caché Postgres `hpf_fichas` — el bot lee de ahí, no de GHL. Se fuerza el refresco
     llamando al webhook de W3 con `ttl_seg: 0`.
  3. `00_migracion_ghl/06_registro/catalogo-airtable.json` — NO es documentación: lo lee
     `hpf-crear-objeto-fichas.py --poblar` para hacer PUT a GHL. Sin sincronizarlo, un `--poblar`
     posterior revierte el fix en silencio.

QUÉ NO HACE
No toca `media_url`. `Boda | Pantuflas boda` NO está en la lista: su imagen tiene el $29
rasterizado (verificado el 2026-08-20), así que arreglarle el texto solo dejaría el mensaje
contradiciéndose. Entra cuando llegue el arte nuevo de Oscar.

Uso:  hpf-remigrar-texto-fichas.py [--dry-run] [--solo FICHA_ID]
"""
import argparse
import csv
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[2]
CLIENTE = REPO / "clients/HPF_HappyFlops"
REGISTRO = CLIENTE / "00_migracion_ghl/06_registro/catalogo-airtable.json"
INPUTS = CLIENTE / "00_migracion_ghl/00_inputs"
ROLLBACK = CLIENTE / "03_workflows/parches-2026-08-20/fichas-texto-rollback.json"

API = "https://services.leadconnectorhq.com"
OBJ = "custom_objects.fichas"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# Las 4 que sólo necesitan texto. Boda|Pantuflas boda queda AFUERA a propósito (ver docstring).
OBJETIVO = [
    ("XV",    "Pantuflas XV"),
    ("XV",    "Comparativa sandalias suelas delgadas y gruesas"),
    ("Otros", "Pantuflas XV"),
    ("Otros", "Comparativa sandalias suelas delgadas y gruesas"),
]
CSVS = {"Boda": "Boda-Grid view.csv", "XV": "XV-Grid view.csv", "Otros": "Otros-Grid view.csv"}


def env():
    e = {}
    for line in (REPO / ".env").read_text().splitlines():
        if line.strip() and not line.strip().startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            e[k.strip()] = v.strip().strip('"').strip("'")
    return e


E = env()
LOC = E["GHL_LOCATION_ID"]
H = {"Authorization": f"Bearer {E['GHL_API_KEY']}", "Version": "2021-07-28",
     "Content-Type": "application/json", "User-Agent": UA}


def ghl(metodo, path, body=None):
    req = urllib.request.Request(
        API + path, data=json.dumps(body).encode() if body is not None else None,
        headers=H, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw.strip().startswith(("{", "[")) else raw)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:400]


def texto_del_curl(curl):
    """El texto vigente que Kommo mandaba. Acepta las DOS formas de payload."""
    if not curl or "--data-raw" not in curl:
        return None
    m = re.search(r"--data-raw\s+'(.*)'\s*$", curl, re.S)
    if m:                                   # camino bueno: parsear el JSON entero
        try:
            return json.loads(m.group(1)).get("text")
        except Exception:
            pass
    m = re.search(r'"text"\s*:\s*"((?:[^"\\]|\\.)*)"', curl, re.S)   # fallback
    if not m:
        return None
    try:
        return json.loads('"' + m.group(1) + '"')
    except Exception:
        return m.group(1)


def leer_csvs():
    """{(evento, producto): texto_vigente}"""
    out = {}
    for evento, arch in CSVS.items():
        with open(INPUTS / arch, encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                t = texto_del_curl(row.get("CURL"))
                if t:
                    out[(evento, (row.get("productos") or "").strip())] = t
    return out


def buscar_ficha(ficha_id):
    page = 1
    while page <= 20:
        s, r = ghl("POST", f"/objects/{OBJ}/records/search",
                   {"locationId": LOC, "page": page, "pageLimit": 20,
                    "query": "", "searchAfter": []})
        if s >= 300:
            sys.exit(f"❌ search http={s} {r}")
        recs = r.get("records", [])
        if not recs:
            return None, None
        for rec in recs:
            p = rec.get("properties") or {}
            if p.get("ficha_id") == ficha_id:
                return rec.get("id"), p
        page += 1
    return None, None


def leer_record(rid):
    """GET directo. NUNCA records/search para el read-back: lag de indexación."""
    s, r = ghl("GET", f"/objects/{OBJ}/records/{rid}?locationId={LOC}")
    if s >= 300 or not isinstance(r, dict):
        return None
    return ((r.get("record") or r).get("properties")) or {}


def refrescar_cache(evento, productos):
    url = "https://[TU-INSTANCIA-N8N]/webhook/hpf-w3-catalogo"
    h = {"Content-Type": "application/json",
         E["HPF_WEBHOOK_AUTH_HEADER_NAME"]: E["HPF_WEBHOOK_AUTH_HEADER_VALUE"]}
    body = {"evento": evento, "productos": productos, "ttl_seg": 0}
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=h, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.loads(r.read().decode() or "null")
    except urllib.error.HTTPError as e:
        return {"_http": e.code, "_raw": e.read().decode()[:300]}


def sincronizar_registro(cambios, dry):
    """cambios: {ficha_id: texto_nuevo}. Reescribe `descripcion` en el registro local."""
    datos = json.loads(REGISTRO.read_text(encoding="utf-8"))
    tocados = []
    for f in datos:
        fid = f"{f.get('tabla')}::{f.get('evento') or f.get('tabla')}::{f.get('producto')}"
        if fid in cambios and f.get("descripcion") != cambios[fid]:
            f["descripcion"] = cambios[fid]
            tocados.append(fid)
    if tocados and not dry:
        REGISTRO.write_text(json.dumps(datos, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")
    print(f"   ~ registro: {len(tocados)} entradas sincronizadas {tocados if tocados else ''}")
    return tocados


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--solo", help="ficha_id exacto")
    a = ap.parse_args()

    vigentes = leer_csvs()
    plan, rollback = [], {}

    for evento, producto in OBJETIVO:
        ficha_id = f"{evento}::{evento}::{producto}"
        if a.solo and a.solo != ficha_id:
            continue
        nuevo = vigentes.get((evento, producto))
        if not nuevo:
            print(f"⚠️  {ficha_id}: sin texto vigente en el CURL — SALTEADA")
            continue
        rid, props = buscar_ficha(ficha_id)
        if not rid:
            print(f"⚠️  {ficha_id}: no existe en GHL — SALTEADA")
            continue
        viejo = (props or {}).get("descripcion") or ""
        if viejo.strip() == nuevo.strip():
            print(f"   • {ficha_id}: ya está al día")
            continue
        vp = re.findall(r"[$]\s?\d+", viejo)
        np_ = re.findall(r"[$]\s?\d+", nuevo)
        print(f"\n── {ficha_id}\n   record {rid}\n   precios {vp} → {np_}")
        plan.append((ficha_id, rid, viejo, nuevo))
        rollback[ficha_id] = {"record": rid, "campo": "descripcion", "valor_anterior": viejo}

    if not plan:
        print("\nnada que hacer.")
        return

    if a.dry_run:
        print(f"\n(dry-run: no escribo) — {len(plan)} fichas listas")
        for fid, rid, viejo, nuevo in plan:
            print(f"\n=== {fid} ===\n--- ANTES ---\n{viejo}\n--- DESPUÉS ---\n{nuevo}")
        return

    ROLLBACK.parent.mkdir(parents=True, exist_ok=True)
    ROLLBACK.write_text(json.dumps(rollback, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print(f"\n   + rollback en {ROLLBACK.relative_to(REPO)}")

    ok = {}
    for fid, rid, viejo, nuevo in plan:
        s, r = ghl("PUT", f"/objects/{OBJ}/records/{rid}?locationId={LOC}",
                   {"properties": {"descripcion": nuevo}})
        print(f"   ~ PUT {fid} → {s}")
        if s >= 300:
            sys.exit(f"❌ {r}")
        verif = leer_record(rid)
        if (verif or {}).get("descripcion", "").strip() != nuevo.strip():
            sys.exit(f"❌ read-back de {fid}: no coincide con lo enviado")
        print("   ✅ read-back OK")
        ok[fid] = nuevo

    sincronizar_registro(ok, dry=False)

    for evento in sorted({f.split("::")[0] for f in ok}):
        out = refrescar_cache(evento, ["pantuflas", "sandalias"])
        # W3 responde envuelto en lista cuando entra por webhook: sin este desempaque el
        # print decía "None cards" aunque el refresco hubiera andado perfecto.
        if isinstance(out, list) and out:
            out = out[0]
        n = out.get("cantidad") if isinstance(out, dict) else None
        print(f"   ~ refresh caché {evento}: {n} cards")

    print("\n✅ listo — probar en conversación real que el precio del texto coincide con la imagen")


if __name__ == "__main__":
    main()
