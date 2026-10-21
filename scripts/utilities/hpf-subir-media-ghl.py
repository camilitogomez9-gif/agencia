#!/usr/bin/env python3
"""
HPF · subir un archivo a la librería de medios de GHL.

Los assets del bot (fichas de producto, videos, el PDF de números de cuenta) viven en la
librería de medios de la location de GHL y se sirven desde `assets.cdn.filesafe.space`.
Este script sube uno nuevo y devuelve su URL pública.

Notas que cuestan tiempo si no están escritas:
  · La API de GHL está detrás de Cloudflare con la regla 1010, que rechaza el user-agent
    por defecto de urllib con un 403 que NO parece un problema de auth. Hay que mandar un
    user-agent de navegador.
  · `medias/files` exige el parámetro `type`; sin él devuelve 422, no 400.

Uso:
    hpf-subir-media-ghl.py <archivo> [--nombre nombre-en-ghl.mp4]
    hpf-subir-media-ghl.py --listar [patrón]
"""
import argparse
import json
import mimetypes
import pathlib
import sys
import urllib.error
import urllib.request
import uuid

REPO = pathlib.Path(__file__).resolve().parents[2]
API = "https://services.leadconnectorhq.com"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def env():
    e = {}
    for line in (REPO / ".env").read_text().splitlines():
        if line.strip() and not line.strip().startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            e[k.strip()] = v.strip().strip('"').strip("'")
    return e


E = env()
TOK, LOC = E["GHL_API_KEY"], E["GHL_LOCATION_ID"]
H = {"Authorization": f"Bearer {TOK}", "Version": "2021-07-28",
     "Accept": "application/json", "User-Agent": UA}


def pedir(path, data=None, headers=None, method=None):
    # La barra va acá y no en cada llamada: sin ella el host queda
    # "services.leadconnectorhq.commedias/..." y el error que sale es un fallo de DNS
    # ("nodename nor servname provided"), que parece de red y no de código. Costó dos
    # intentos y una escalación de sandbox innecesaria el 14/08.
    url = API + "/" + path.lstrip("/")
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={**H, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            body = r.read().decode()
            return r.status, (json.loads(body) if body.strip().startswith(("{", "[")) else body)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:600]


def listar(patron=""):
    q = f"medias/files?altId={LOC}&altType=location&type=file&limit=100"
    if patron:
        q += f"&query={urllib.parse.quote(patron)}"
    s, d = pedir(q)
    if s != 200:
        sys.exit(f"❌ {s} {d}")
    for f in (d.get("files") or []):
        print(f"  {str(f.get('name'))[:46]:48} {f.get('url')}")


def subir(ruta, nombre=None):
    p = pathlib.Path(ruta)
    if not p.exists():
        sys.exit(f"❌ no existe: {p}")
    nombre = nombre or p.name
    tipo = mimetypes.guess_type(nombre)[0] or "application/octet-stream"
    frontera = "----hpf" + uuid.uuid4().hex

    def campo(k, v):
        return (f'--{frontera}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n'
                f'{v}\r\n').encode()

    cuerpo = b"".join([
        campo("name", nombre),
        campo("hosted", "false"),
        campo("altId", LOC),
        campo("altType", "location"),
        (f'--{frontera}\r\nContent-Disposition: form-data; name="file"; '
         f'filename="{nombre}"\r\nContent-Type: {tipo}\r\n\r\n').encode(),
        p.read_bytes(),
        f"\r\n--{frontera}--\r\n".encode(),
    ])
    print(f"subiendo {p.name} ({len(p.read_bytes())/1024:.0f} KB, {tipo}) como {nombre!r}…")
    s, d = pedir("medias/upload-file", data=cuerpo,
                 headers={"Content-Type": f"multipart/form-data; boundary={frontera}"})
    print(f"  -> {s}")
    if s not in (200, 201):
        sys.exit(f"❌ {d}")
    print(json.dumps(d, ensure_ascii=False, indent=2)[:700])
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("archivo", nargs="?")
    ap.add_argument("--nombre")
    ap.add_argument("--listar", nargs="?", const="", default=None)
    a = ap.parse_args()
    if a.listar is not None:
        listar(a.listar)
    elif a.archivo:
        subir(a.archivo, a.nombre)
    else:
        ap.print_help()


if __name__ == "__main__":
    import urllib.parse  # noqa: E402  (lo usa listar)
    main()
