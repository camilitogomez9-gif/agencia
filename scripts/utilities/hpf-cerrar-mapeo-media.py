#!/usr/bin/env python3
"""
HPF · L4 — Cierra el mapeo ficha de catálogo → asset en la Media Library de GHL.

1. Aplica los mapeos que resolvimos contra archivos YA existentes en GHL
   (evita subir duplicados: 7 de las 8 "re-hosteables" ya estaban, con otro nombre).
2. Sube a la Media Library lo que genuinamente no existe, tomándolo de la URL
   firmada del adjunto de Airtable.
3. Verifica cada asset con un Range 0-1023 → debe dar 206 (regla del protocolo:
   la evidencia es el read-back, no el 2xx del POST).

Regla 0: Airtable se lee, nunca se escribe. En GHL sólo se AGREGA.
"""
import json
import mimetypes
import re
import unicodedata
import urllib.error
import urllib.request
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CAT = REPO / "clients/HPF_HappyFlops/00_migracion_ghl/06_registro/catalogo-airtable.json"
GHL = "https://services.leadconnectorhq.com"
UA = "curl/8.7.1"

# ficha (tabla, producto) → nombre EXACTO del archivo ya presente en la Media Library.
# Resuelto por nombre de producto y por nombre del adjunto de Airtable; los nombres con
# "╠ü" son acentos descompuestos que rompían el match automático.
MAPEO_EXISTENTES = {
    ("Boda", "Catalogo de Mandiles"): "Cata╠ülogo de Mandiles.jpeg",
    ("Boda", "Pantuflas boda"): "INFOGRAFI╠üA final 2-11 (1).png",
    ("Boda", "Kit anticruda principal"): "INFOGRAFI╠üA final 2-10 (1).png",
    ("XV", "Pantuflas XV"): "Pantuflas XV-2.jpeg",
    ("XV", "Vasos popote 24 oz"): "vaso popote 24 oz XV.jpeg",
    ("XV", "Comparativa sandalias suelas delgadas y gruesas"):
        "Comparativa sandalias suelas delgadas y gruesas-2.jpeg",
    ("Otros", "Catalogo pantuflas"): "Cata╠ülogo pantuflas.pdf",
}

# ficha → hay que subirla; no existe nada equivalente en GHL.
A_SUBIR = {("Foto Vacaciones", "vaca"): "hpf-foto-vacaciones.jpeg"}


def load_env():
    env = {}
    for line in (REPO / ".env").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


ENV = load_env()
LOC = ENV["GHL_LOCATION_ID"]
H_GHL = {"Authorization": f"Bearer {ENV['GHL_API_KEY']}", "Version": "2021-07-28",
         "User-Agent": UA}


def listar_media():
    u = (f"{GHL}/medias/files?altId={LOC}&altType=location&limit=100"
         f"&type=file&sortBy=createdAt&sortOrder=desc")
    r = urllib.request.Request(u, headers=H_GHL)
    return json.load(urllib.request.urlopen(r, timeout=60))["files"]


def airtable_adjunto(record_id, tabla_id):
    """Re-lee el record para obtener una URL firmada fresca (las viejas expiran)."""
    u = f"https://api.airtable.com/v0/{ENV['AIRTABLE_BASE_HPF']}/{tabla_id}/{record_id}"
    r = urllib.request.Request(
        u, headers={"Authorization": f"Bearer {ENV['AIRTABLE_PAT_HPF']}", "User-Agent": UA})
    f = json.load(urllib.request.urlopen(r, timeout=60))["fields"]
    adj = f.get("archivo") or f.get("Imagen") or f.get("Métodos(pdf)") or []
    return adj[0] if adj else None


def subir(nombre, data, content_type):
    """POST multipart a /medias/upload-file. Devuelve el JSON de respuesta."""
    b = uuid.uuid4().hex
    partes = []
    for k, v in (("hosted", "false"), ("name", nombre), ("altId", LOC), ("altType", "location")):
        partes.append(
            f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    partes.append(
        f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="{nombre}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n".encode())
    partes.append(data)
    partes.append(f"\r\n--{b}--\r\n".encode())
    body = b"".join(partes)
    req = urllib.request.Request(
        f"{GHL}/medias/upload-file", data=body, method="POST",
        headers={**H_GHL, "Content-Type": f"multipart/form-data; boundary={b}"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, {"_raw": e.read().decode()[:400]}


def range_206(url):
    req = urllib.request.Request(url, headers={"Range": "bytes=0-1023", "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, r.headers.get("Content-Type")
    except urllib.error.HTTPError as e:
        return e.code, None


def main():
    cat = json.loads(CAT.read_text())
    media = {m["name"]: m for m in listar_media()}

    print("── Mapeando a archivos ya existentes (sin subir duplicados)")
    for c in cat:
        k = (c["tabla"], c["producto"])
        if k in MAPEO_EXISTENTES and not c.get("ghl_media"):
            nombre = MAPEO_EXISTENTES[k]
            m = media.get(nombre)
            if not m:
                print(f"  ❌ {k[1][:38]:38s} → no encontré {nombre!r} en la Media Library")
                continue
            c["ghl_media"] = {"name": m["name"], "url": m["url"], "match": "existente-resuelto"}
            print(f"  ✅ {k[1][:38]:38s} → {m['name']}")

    print("\n── Subiendo lo que no existe")
    for c in cat:
        k = (c["tabla"], c["producto"])
        if k not in A_SUBIR or c.get("ghl_media"):
            continue
        adj = airtable_adjunto(c["record_id"], c["tabla_id"])
        if not adj:
            print(f"  ❌ {k[1]}: el record ya no tiene adjunto")
            continue
        req = urllib.request.Request(adj["url"], headers={"User-Agent": UA})
        data = urllib.request.urlopen(req, timeout=120).read()
        nombre = A_SUBIR[k]
        ct = adj.get("type") or mimetypes.guess_type(nombre)[0] or "application/octet-stream"
        st, resp = subir(nombre, data, ct)
        url = resp.get("url") or (resp.get("file") or {}).get("url")
        print(f"  {'✅' if st < 300 else '❌'} {k[1]}: http={st} bytes={len(data)} → {url or resp}")
        if st < 300 and url:
            c["ghl_media"] = {"name": nombre, "url": url, "match": "subido-desde-airtable"}

    CAT.write_text(json.dumps(cat, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n── Verificación: cada asset mapeado debe servir 206")
    malos = []
    vistos = {}
    for c in cat:
        g = c.get("ghl_media")
        if not g:
            continue
        if g["url"] in vistos:
            continue
        st, ct = range_206(g["url"])
        vistos[g["url"]] = st
        if st != 206:
            malos.append((c["producto"], g["url"], st))
    con = sum(1 for c in cat if c.get("ghl_media"))
    print(f"  {len(vistos)} assets distintos · {sum(1 for v in vistos.values() if v == 206)} sirven 206")
    for p, u, s in malos:
        print(f"  ❌ {p}: http={s} {u}")

    print(f"\nCobertura del catálogo: {con}/{len(cat)} fichas con asset")
    sin = [c for c in cat if not c.get("ghl_media")]
    if sin:
        print("Sin asset (viven sólo en el salesbot de Kommo):")
        for c in sin:
            print(f"  · {c['tabla']:6s} {c['producto'][:38]:38s} bot_id={c['bot_id']}")


if __name__ == "__main__":
    main()
