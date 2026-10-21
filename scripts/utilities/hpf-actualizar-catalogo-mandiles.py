#!/usr/bin/env python3
"""
HPF · reemplaza el catálogo de mandiles y deja el registro de assets sincronizado.

QUÉ CAMBIA
El catálogo que sirve el bot muestra 6 diseños (Club de los mandilones, Spiderman, Batman,
Superman, Chapulín, Game Over). El vigente son 5 y sólo 2 sobreviven: cambió la línea de
producto, no la foto. Que el nuevo es el correcto lo confirma la ficha `Mandiles Video`,
que ya se llama internamente "V5 · mandiles 'EL MANDILÓN', 5 diseños".

TRES SUPERFICIES, NO UNA
Cambiar la ficha en GHL no alcanza:
  1. Media Library de GHL — subir el archivo.
  2. El record del custom object — PUT con `?locationId=` en la QUERY (en el body da 422,
     sin él 404). Devuelve 2xx aunque no escriba, así que se relee para confirmar.
  3. La caché Postgres `hpf_fichas` — el bot lee de ahí, no de GHL. TTL 900 s con refresco
     perezoso; se fuerza llamando al webhook de W3 con `ttl_seg: 0`.

Y UNA BOMBA DE TIEMPO QUE SE DESACTIVA DE PASO
`00_migracion_ghl/06_registro/catalogo-airtable.json` NO es documentación: lo lee
`hpf-crear-objeto-fichas.py --poblar` para hacer PUT a GHL. Quedó desincronizado — todavía
tiene la URL vieja de la sandalia XV que se reemplazó el 14/08, así que correr `--poblar`
hoy revertiría ese cambio en silencio. Se actualizan las dos entradas.

NO SE TOCA EL PROMPT. El catálogo nuevo está numerado 1 a 5, lo que invita a "quiero el 3",
pero la REGLA CRÍTICA de `agente-recolector.md:751-789` dice que los mandiles NO se eligen
(vienen del stock con 5 frases fijas). Eso queda pendiente de consultar con Oscar.

Uso:  hpf-actualizar-catalogo-mandiles.py [--dry-run] [--archivo RUTA]
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
ROLLBACK = CLIENTE / "03_workflows/parches-2026-08-14/ficha-mandiles-catalogo-rollback.json"
DEFAULT_ARCHIVO = pathlib.Path.home() / "Downloads/mandiles-catalogo.jpeg"

API = "https://services.leadconnectorhq.com"
OBJ = "custom_objects.fichas"
RECORD_MANDILES = "6a750720e1739d785915e6d2"
FICHA_MANDILES = "Boda::Boda::Catalogo de Mandiles"
# La sandalia XV se reemplazó en GHL el 14/08 pero el registro nunca se actualizó.
RECORD_SANDALIA = "6a750736ba12e25112dcf25f"
NOMBRE_EN_GHL = "Catalogo de Mandiles 2026-08.jpeg"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# se carga a mano porque el nombre del archivo tiene guiones
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


def buscar_ficha(ficha_id):
    """Devuelve (record_id, properties) buscando por ficha_id en todas las páginas."""
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


def leer_record(record_id):
    """GET directo del record. NO usar `records/search` para el read-back: tiene lag de
    indexación —el mismo que está documentado para /opportunities/search— y devuelve el
    valor viejo durante un rato después de un PUT que sí escribió. Costó un falso negativo
    el 2026-08-17."""
    s, r = ghl("GET", f"/objects/{OBJ}/records/{record_id}?locationId={LOC}")
    if s >= 300 or not isinstance(r, dict):
        return None
    return ((r.get("record") or r).get("properties")) or {}


def refrescar_cache():
    """W3 cachea las fichas en Postgres con TTL 900 s. Con ttl_seg=0 el refresh es inmediato."""
    url = "https://[TU-INSTANCIA-N8N]/webhook/hpf-w3-catalogo"
    h = {"Content-Type": "application/json",
         E["HPF_WEBHOOK_AUTH_HEADER_NAME"]: E["HPF_WEBHOOK_AUTH_HEADER_VALUE"]}
    body = {"evento": "Boda", "productos": ["mandiles"], "ttl_seg": 0}
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=h, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.loads(r.read().decode() or "null")
    except urllib.error.HTTPError as e:
        return {"_http": e.code, "_raw": e.read().decode()[:300]}


def sincronizar_registro(cambios, dry):
    """cambios: {ficha_id_o_producto: url_nueva}. Reescribe ghl_media.url en el registro."""
    datos = json.loads(REGISTRO.read_text(encoding="utf-8"))
    tocados = []
    for f in datos:
        rid = f"{f.get('tabla')}::{f.get('evento') or f.get('tabla')}::{f.get('producto')}"
        if rid in cambios:
            actual = (f.get("ghl_media") or {}).get("url")
            if actual == cambios[rid]:
                continue
            f.setdefault("ghl_media", {})["url"] = cambios[rid]
            tocados.append((rid, actual, cambios[rid]))
    for rid, viejo, nuevo in tocados:
        print(f"   ~ registro · {rid}\n       {viejo}\n     → {nuevo}")
    if tocados and not dry:
        REGISTRO.write_text(json.dumps(datos, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")
    if not tocados:
        print("   • registro: ya sincronizado")
    return tocados


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--archivo", default=str(DEFAULT_ARCHIVO))
    a = ap.parse_args()
    arch = pathlib.Path(a.archivo)
    if not arch.exists():
        sys.exit(f"❌ no existe {arch}")

    # ── 0. estado actual, leído del vivo
    rid, props = buscar_ficha(FICHA_MANDILES)
    if not rid:
        sys.exit(f"❌ no encuentro la ficha {FICHA_MANDILES!r} en GHL")
    if rid != RECORD_MANDILES:
        print(f"   ⚠️  el record id cambió: {RECORD_MANDILES} → {rid}")
    vieja = props.get("media_url")
    print(f"ficha  : {FICHA_MANDILES}\nrecord : {rid}\nactual : {vieja}")
    print(f"archivo: {arch} ({arch.stat().st_size // 1024} KB)")

    # la sandalia XV: qué dice GHL vs qué dice el registro
    _, ps = buscar_ficha("XV::XV::Comparativa sandalias suelas delgadas y gruesas")
    url_sandalia = (ps or {}).get("media_url")

    if a.dry_run:
        print("\n(dry-run: no subo ni escribo)")
        print(f"   → subiría {arch.name} como {NOMBRE_EN_GHL!r}")
        print(f"   → PUT /objects/{OBJ}/records/{rid}?locationId=…  media_url=<nueva>")
        sincronizar_registro({FICHA_MANDILES: "<url nueva>",
                              "XV::XV::Comparativa sandalias suelas delgadas y gruesas":
                                  url_sandalia}, dry=True)
        print("   → refrescaría hpf_fichas por el webhook de W3 con ttl_seg=0")
        return

    # ── 1. Media Library
    resp = SUBIR.subir(arch, NOMBRE_EN_GHL)
    nueva = resp.get("url") or (resp.get("file") or {}).get("url")
    if not nueva:
        sys.exit(f"❌ la subida no devolvió url: {json.dumps(resp)[:300]}")
    print(f"\n   + subido: {nueva}")

    # ── 2. rollback ANTES de escribir
    ROLLBACK.write_text(json.dumps({
        "record": rid,
        "campo": "media_url",
        "valor_anterior": vieja,
        "valor_nuevo": nueva,
        "nota": ("Catálogo nuevo de mandiles que pasó Oscar (5 diseños numerados). El viejo "
                 "mostraba 6, de los cuales sólo 2 siguen existiendo. Para revertir: PUT con "
                 "valor_anterior + refrescar la caché de W3 con ttl_seg=0."),
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"   + rollback en {ROLLBACK.relative_to(REPO)}")

    # ── 3. el record. locationId va en la QUERY.
    s, r = ghl("PUT", f"/objects/{OBJ}/records/{rid}?locationId={LOC}",
               {"properties": {"media_url": nueva}})
    print(f"   ~ PUT record → {s}")
    if s >= 300:
        sys.exit(f"❌ {r}")

    # ── 4. read-back: el PUT devuelve 2xx aunque no escriba, así que hay que releer.
    #      Por GET directo, no por search (ver leer_record).
    verif = leer_record(rid)
    if (verif or {}).get("media_url") != nueva:
        sys.exit(f"❌ read-back: quedó {(verif or {}).get('media_url')!r}, esperaba {nueva!r}")
    print("   ✅ read-back OK")

    # ── 5. registro de assets (mandiles + el drift de la sandalia XV)
    sincronizar_registro({FICHA_MANDILES: nueva,
                          "XV::XV::Comparativa sandalias suelas delgadas y gruesas":
                              url_sandalia}, dry=False)

    # ── 6. caché
    out = refrescar_cache()
    cards = out if isinstance(out, list) else (out or {}).get("cards", out)
    print(f"   ~ refresh de hpf_fichas: {json.dumps(cards, ensure_ascii=False)[:200]}")
    print("\n✅ listo — probar en una conversación real: 'es para una boda' → 'que tienen de mandiles?'")


if __name__ == "__main__":
    main()
