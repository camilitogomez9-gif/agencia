#!/usr/bin/env python3
"""
HPF · L5/W3 — Crea el custom object `fichas` en GHL y lo puebla desde el catálogo.

Por qué un objeto nuevo y no `productos`: son dos entidades de granularidad distinta.
`productos` tiene 15 SKUs con precio/mínimo/peso (para cotizar). Las `fichas` son las
~65 tarjetas que el bot manda por WhatsApp (texto + imagen), una por producto por evento.
Mezclarlas dejaría dos significados en la misma tabla.

Fases (idempotentes, se pueden correr por separado):
    --scope     sólo verifica si el PIT puede crear schema (no crea nada)
    --crear     crea el objeto + sus campos
    --poblar    inserta/actualiza los registros desde catalogo-airtable.json
    --verificar relee por API y compara contra el catálogo

Regla 0: sólo AGREGA en GHL. No toca Airtable, Kommo ni los workflows vivos.
"""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CAT = REPO / "clients/HPF_HappyFlops/00_migracion_ghl/06_registro/catalogo-airtable.json"
API = "https://services.leadconnectorhq.com"
CLAVE = "fichas"
OBJ = f"custom_objects.{CLAVE}"

# Campos de la ficha. `nombre` es el display primario (lo exige GHL al crear).
CAMPOS = [
    ("ficha_id", "Ficha ID", "TEXT"),
    ("evento", "Evento", "TEXT"),
    ("subcategoria", "Subcategoría", "TEXT"),
    ("descripcion", "Descripción", "LARGE_TEXT"),
    ("media_url", "URL del asset", "TEXT"),
    ("media_tipo", "Tipo de asset", "TEXT"),
    ("bot_id_kommo", "bot_id Kommo (histórico)", "TEXT"),
    ("activo", "Activo", "TEXT"),
]


def load_env():
    e = {}
    for line in (REPO / ".env").read_text().splitlines():
        if line.strip() and not line.strip().startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            e[k.strip()] = v.strip().strip('"').strip("'")
    return e


E = load_env()
LOC = E["GHL_LOCATION_ID"]
HDR = {"Authorization": f"Bearer {E['GHL_API_KEY']}", "Version": "2021-07-28",
       "Content-Type": "application/json", "User-Agent": "curl/8.7.1"}


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, headers=HDR, method=method)
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw.strip() else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, {"_raw": raw[:400]}


def existe_objeto():
    s, r = call("GET", f"/objects/?locationId={LOC}")
    if s >= 300:
        return None
    return next((o for o in r.get("objects", []) if o.get("key") == OBJ), None)


def cmd_scope():
    """Probe no destructivo: pide el schema del objeto. Un 404 = no existe (scope de
    lectura OK). Para saber si podemos ESCRIBIR schema hay que intentar el POST."""
    s, r = call("GET", f"/objects/{OBJ}?locationId={LOC}&fetchProperties=true")
    print(f"GET  /objects/{OBJ} → {s}")
    ya = existe_objeto()
    print("¿ya existe el objeto?", "sí" if ya else "no")
    if ya:
        print("   id:", ya.get("id"))
        return True
    print("\nPara verificar el scope de escritura hay que intentar el POST.")
    print("Corré con --crear (es aditivo: si falta scope, falla sin efecto).")
    return False


def cmd_crear():
    ya = existe_objeto()
    if ya:
        print(f"✅ el objeto ya existe: {ya['id']} — nada que crear")
        return True
    body = {
        "labels": {"singular": "Ficha", "plural": "Fichas"},
        "key": CLAVE,
        "description": "Tarjetas de catálogo que el agente envía por WhatsApp "
                       "(texto + asset). Migrado desde Airtable appMHtUN9zKYODufC.",
        "locationId": LOC,
        "primaryDisplayPropertyDetails": {
            "key": "nombre", "name": "Nombre de la ficha", "dataType": "TEXT"},
    }
    s, r = call("POST", "/objects/", body)
    if s >= 300:
        print(f"❌ POST /objects/ → {s}")
        print("   ", json.dumps(r, ensure_ascii=False)[:400])
        if s in (401, 403):
            print("\n   → el PIT NO tiene scope de escritura de schema "
                  "(objects/schema.write). Hay que regenerarlo con ese permiso "
                  "o crear el objeto a mano en la UI.")
        return False
    print(f"✅ objeto creado: {r.get('object', {}).get('id')}")
    return cmd_campos()


def folder_id():
    """GHL crea un folder por defecto al crear el objeto; los campos van adentro
    y el POST exige su id como `parentId` (si falta, 422)."""
    s, r = call("GET", f"/custom-fields/object-key/{OBJ}?locationId={LOC}")
    if s >= 300:
        return None, {}
    fol = (r.get("folders") or [{}])[0].get("id")
    ya = {f.get("fieldKey"): f.get("id") for f in (r.get("fields") or [])}
    return fol, ya


def cmd_campos():
    fol, ya = folder_id()
    if not fol:
        print("❌ no pude resolver el folder del objeto")
        return False
    print(f"   folder: {fol} · campos ya presentes: {len(ya)}")
    errores = 0
    for i, (clave, nombre, tipo) in enumerate(CAMPOS):
        fk = f"{OBJ}.{clave}"
        if fk in ya:
            print(f"   ⏭  campo {clave:16s} ya existe")
            continue
        sc, rc = call("POST", "/custom-fields/", {
            "locationId": LOC, "name": nombre, "dataType": tipo,
            "fieldKey": fk, "objectKey": OBJ, "parentId": fol,
            "position": 100 + i * 50, "showInForms": False})
        if sc >= 300:
            errores += 1
        print(f"   {'✅' if sc < 300 else '❌'} campo {clave:16s} {tipo:12s} http={sc}"
              + ("" if sc < 300 else f" {json.dumps(rc, ensure_ascii=False)[:180]}"))
    return errores == 0


def fichas_del_catalogo():
    cat = json.loads(CAT.read_text())
    out = []
    for c in cat:
        g = c.get("ghl_media") or {}
        url = g.get("url")
        tipo = None
        if url:
            ext = url.rsplit(".", 1)[-1].lower()
            tipo = {"mp4": "video", "pdf": "pdf"}.get(ext, "imagen")
        out.append({
            # el evento es parte de la identidad: "Imagen Principal" tiene 3 filas
            # homónimas ("Todos los productos"), una por evento
            "ficha_id": f"{c['tabla']}::{c.get('evento') or c['tabla']}::{c['producto']}"[:180],
            "nombre": c["producto"],
            "evento": c.get("evento") or c["tabla"],
            "subcategoria": c.get("subcategoria") or "",
            "descripcion": c.get("descripcion") or "",
            "media_url": url or "",
            "media_tipo": tipo or "",
            "bot_id_kommo": str(c.get("bot_id") or ""),
            "activo": "true" if url else "false",
        })
    return out


def leer_todos():
    """Pagina el search completo. pageLimit >20 dispara 403 de Cloudflare."""
    vistos, page = {}, 1
    while page <= 20:
        s, r = call("POST", f"/objects/{OBJ}/records/search",
                    {"locationId": LOC, "page": page, "pageLimit": 20,
                     "query": "", "searchAfter": []})
        if s >= 300:
            break
        recs = r.get("records", [])
        if not recs:
            break
        for rec in recs:
            fid = (rec.get("properties") or {}).get("ficha_id")
            if fid:
                vistos[fid] = rec["id"]
        page += 1
    return vistos


def cmd_limpiar():
    """Borra registros cuyo ficha_id ya no está en el catálogo (p. ej. los que quedaron
    de una clave anterior). Es la única operación destructiva del script y sólo toca
    el objeto `fichas`, que creamos nosotros."""
    esperados = {f["ficha_id"] for f in fichas_del_catalogo()}
    ya = leer_todos()
    sobra = {k: v for k, v in ya.items() if k not in esperados}
    print(f"en GHL {len(ya)} · esperados {len(esperados)} · a borrar {len(sobra)}")
    for fid, rid in sobra.items():
        s, _ = call("DELETE", f"/objects/{OBJ}/records/{rid}")
        print(f"   {'✅' if s < 300 else '❌'} borrado {fid[:60]} http={s}")
    return True


def cmd_poblar():
    if not existe_objeto():
        print("❌ el objeto no existe; corré --crear primero")
        return False
    fichas = fichas_del_catalogo()
    ya = leer_todos()
    print(f"registros existentes: {len(ya)} · fichas a cargar: {len(fichas)}")
    okc = err = 0
    for f in fichas:
        props = {k: v for k, v in f.items() if v != ""}
        if f["ficha_id"] in ya:
            # locationId va en la QUERY, no en el body: en el body devuelve
            # 422 "property locationId should not exist", y sin él 404.
            sc, rc = call("PUT",
                          f"/objects/{OBJ}/records/{ya[f['ficha_id']]}?locationId={LOC}",
                          {"properties": props})
        else:
            sc, rc = call("POST", f"/objects/{OBJ}/records",
                          {"locationId": LOC, "properties": props})
        if sc < 300:
            okc += 1
        else:
            err += 1
            if err <= 3:
                print(f"   ❌ {f['nombre'][:40]}: http={sc} "
                      f"{json.dumps(rc, ensure_ascii=False)[:200]}")
    print(f"✅ {okc} ok · ❌ {err} con error")
    return err == 0


def cmd_verificar():
    fichas = {f["ficha_id"]: f for f in fichas_del_catalogo()}
    vistos = {}
    page = 1
    while page <= 20:
        s, r = call("POST", f"/objects/{OBJ}/records/search",
                    {"locationId": LOC, "page": page, "pageLimit": 20,
                     "query": "", "searchAfter": []})
        if s >= 300:
            print(f"❌ search http={s} {json.dumps(r, ensure_ascii=False)[:200]}")
            return False
        recs = r.get("records", [])
        if not recs:
            break
        for rec in recs:
            pr = rec.get("properties") or {}
            if pr.get("ficha_id"):
                vistos[pr["ficha_id"]] = pr
        page += 1
    faltan = [k for k in fichas if k not in vistos]
    con_media = sum(1 for p in vistos.values() if p.get("media_url"))
    print(f"en GHL: {len(vistos)} fichas · con media_url: {con_media}")
    print(f"esperadas: {len(fichas)} · faltantes: {len(faltan)}")
    for k in faltan[:8]:
        print("   falta:", k)
    return not faltan


if __name__ == "__main__":
    cmds = {"--scope": cmd_scope, "--crear": cmd_crear, "--campos": cmd_campos,
            "--poblar": cmd_poblar, "--limpiar": cmd_limpiar, "--verificar": cmd_verificar}
    pedidos = [a for a in sys.argv[1:] if a in cmds] or ["--scope"]
    for c in pedidos:
        print(f"\n=== {c} ===")
        cmds[c]()
