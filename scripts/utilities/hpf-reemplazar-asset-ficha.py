#!/usr/bin/env python3
"""
HPF · reemplaza el ASSET de una ficha del catálogo, en las 3 superficies + el registro.

Generaliza `hpf-actualizar-catalogo-mandiles.py`, que hacía lo mismo para una ficha sola y
hardcodeada. Sirve para cualquier ficha: la de mandiles que hay que recomprimir, y las que
lleguen de Oscar (pantuflas de Boda con $30, cilindros de "Otros", el PDF de cuentas).

LAS 3 SUPERFICIES — cambiar el record en GHL NO alcanza
  1. Media Library de GHL: subir el archivo.
  2. El record del custom object: PUT con `?locationId=` en la QUERY (en el body da 422, sin
     él 404). Devuelve 2xx aunque no escriba, así que se relee por GET DIRECTO — nunca por
     `records/search`, que tiene lag de indexación.
  3. La caché Postgres `hpf_fichas`: el bot lee de AHÍ, no de GHL. TTL 900 s; se fuerza con
     el webhook de W3 y `ttl_seg: 0`.
Y además `00_migracion_ghl/06_registro/catalogo-airtable.json`, que NO es documentación: lo
lee `hpf-crear-objeto-fichas.py --poblar`. Sin sincronizarlo, un `--poblar` revierte esto.

TECHO DE 5 MB
Telegram rechaza fotos por URL de más de 5 MB y `TG · foto` (W2) muere con ellas, llevándose
el turno entero. El script ABORTA si el archivo lo supera. Es el bug que dejaba la ficha de
mandiles sin enviarse en 6 de 6 corridas.

Uso:
    hpf-reemplazar-asset-ficha.py --ficha 'Boda::Boda::Mandiles' --archivo ruta.jpg [--dry-run]
"""
import argparse
import importlib.util
import json
import pathlib
import sys
import urllib.error
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[2]
CLIENTE = REPO / "clients/HPF_HappyFlops"
REGISTRO = CLIENTE / "00_migracion_ghl/06_registro/catalogo-airtable.json"
ROLLBACK_DIR = CLIENTE / "03_workflows/parches-2026-08-20"
API = "https://services.leadconnectorhq.com"
OBJ = "custom_objects.fichas"
TECHO_TELEGRAM = 5 * 1024 * 1024

_spec = importlib.util.spec_from_file_location(
    "subirmedia", pathlib.Path(__file__).parent / "hpf-subir-media-ghl.py")
SUBIR = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SUBIR)


def env():
    e = {}
    for line in (REPO / ".env").read_text().splitlines():
        if line.strip() and not line.strip().startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            e[k.strip()] = v.strip().strip('"').strip("'")
    return e


E = env()
LOC = E["GHL_LOCATION_ID"]
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
H = {"Authorization": f"Bearer {E['GHL_API_KEY']}", "Version": "2021-07-28",
     "Content-Type": "application/json", "User-Agent": UA}


def ghl(metodo, path, body=None):
    req = urllib.request.Request(
        API + path, data=json.dumps(body).encode() if body is not None else None,
        headers=H, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw.strip().startswith(("{", "[")) else raw)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:400]


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
    s, r = ghl("GET", f"/objects/{OBJ}/records/{rid}?locationId={LOC}")
    if s >= 300 or not isinstance(r, dict):
        return None
    return ((r.get("record") or r).get("properties")) or {}


def refrescar_cache(evento, productos):
    url = "https://[TU-INSTANCIA-N8N]/webhook/hpf-w3-catalogo"
    h = {"Content-Type": "application/json",
         E["HPF_WEBHOOK_AUTH_HEADER_NAME"]: E["HPF_WEBHOOK_AUTH_HEADER_VALUE"]}
    req = urllib.request.Request(
        url, data=json.dumps({"evento": evento, "productos": productos,
                              "ttl_seg": 0}).encode(), headers=h, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            out = json.loads(r.read().decode() or "null")
    except urllib.error.HTTPError as e:
        return {"_http": e.code, "_raw": e.read().decode()[:300]}
    # W3 responde envuelto en lista cuando entra por webhook
    return out[0] if isinstance(out, list) and out else out


def sincronizar_registro(ficha_id, url_nueva, nombre_nuevo, dry):
    datos = json.loads(REGISTRO.read_text(encoding="utf-8"))
    for f in datos:
        fid = f"{f.get('tabla')}::{f.get('evento') or f.get('tabla')}::{f.get('producto')}"
        if fid == ficha_id:
            antes = (f.get("ghl_media") or {}).get("url")
            f.setdefault("ghl_media", {})["url"] = url_nueva
            f["ghl_media"]["name"] = nombre_nuevo
            print(f"   ~ registro · {fid}\n       {antes}\n     → {url_nueva}")
            if not dry:
                REGISTRO.write_text(json.dumps(datos, indent=2, ensure_ascii=False) + "\n",
                                    encoding="utf-8")
            return True
    print(f"   ⚠️ {ficha_id} no está en el registro local")
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ficha", required=True, help="ficha_id, ej 'Boda::Boda::Mandiles'")
    ap.add_argument("--archivo", required=True)
    ap.add_argument("--nombre", help="nombre en GHL (default: el del archivo)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    arch = pathlib.Path(a.archivo)
    if not arch.exists():
        sys.exit(f"❌ no existe {arch}")
    tam = arch.stat().st_size
    if tam > TECHO_TELEGRAM:
        sys.exit(f"❌ {arch.name} pesa {tam:,} bytes y supera el techo de Telegram "
                 f"({TECHO_TELEGRAM:,}). Recomprimir antes: una foto por URL más grande "
                 f"que eso mata el turno entero en `TG · foto`.")

    rid, props = buscar_ficha(a.ficha)
    if not rid:
        sys.exit(f"❌ no encuentro la ficha {a.ficha!r} en GHL")
    vieja = props.get("media_url")
    nombre = a.nombre or arch.name
    print(f"ficha  : {a.ficha}\nrecord : {rid}")
    print(f"actual : {vieja}")
    print(f"nuevo  : {arch} ({tam:,} bytes) como {nombre!r}")

    if a.dry_run:
        print("\n(dry-run: no subo ni escribo)")
        sincronizar_registro(a.ficha, "<url nueva>", nombre, dry=True)
        return

    resp = SUBIR.subir(arch, nombre)
    nueva = resp.get("url") or (resp.get("file") or {}).get("url")
    if not nueva:
        sys.exit(f"❌ la subida no devolvió url: {json.dumps(resp)[:300]}")
    print(f"\n   + subido: {nueva}")

    ROLLBACK_DIR.mkdir(parents=True, exist_ok=True)
    slug = a.ficha.replace("::", "-").replace(" ", "_").lower()
    rb = ROLLBACK_DIR / f"asset-{slug}-rollback.json"
    rb.write_text(json.dumps({
        "ficha_id": a.ficha, "record": rid, "campo": "media_url",
        "valor_anterior": vieja, "valor_nuevo": nueva,
        "nota": "Para revertir: PUT con valor_anterior + refrescar la caché de W3 con ttl_seg 0 "
                "+ sincronizar catalogo-airtable.json.",
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"   + rollback en {rb.relative_to(REPO)}")

    s, r = ghl("PUT", f"/objects/{OBJ}/records/{rid}?locationId={LOC}",
               {"properties": {"media_url": nueva}})
    print(f"   ~ PUT record → {s}")
    if s >= 300:
        sys.exit(f"❌ {r}")

    verif = leer_record(rid)
    if (verif or {}).get("media_url") != nueva:
        sys.exit(f"❌ read-back: quedó {(verif or {}).get('media_url')!r}")
    print("   ✅ read-back OK")

    sincronizar_registro(a.ficha, nueva, nombre, dry=False)

    evento = props.get("evento") or a.ficha.split("::")[1]
    prod = (props.get("nombre") or "").lower()
    out = refrescar_cache(evento, [prod])
    print(f"   ~ refresh caché {evento} · {prod!r}: "
          f"{(out or {}).get('cantidad')} cards")
    print("\n✅ listo")


if __name__ == "__main__":
    main()
