#!/usr/bin/env python3
"""
HPF · L4 — Extrae el catálogo vivo de Airtable (sólo lectura) y lo canonicaliza.

Salida: clients/HPF_HappyFlops/00_migracion_ghl/06_registro/catalogo-airtable.json
Es la fuente para poblar el custom object `custom_objects.productos` en GHL.

Regla 0: sólo GET contra Airtable. No escribe nada allá.
"""
import json
import os
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "clients/HPF_HappyFlops/00_migracion_ghl/06_registro"

TABLAS = {
    "tblV3ULnD5O6650xK": ("Boda", "evento"),
    "tblxd3j0b5cdLHTIl": ("XV", "evento"),
    "tbl2kg4m8LeHjNk7m": ("Otros", "evento"),
    "tblsDWUQbfANNWMeK": ("Imagen Principal", "imagen_principal"),
    "tblp2FQHozTQKFtsz": ("Métodos de Pago", "pago"),
    "tbl8oRU3ApdEuLcgs": ("Foto Vacaciones", "vacaciones"),
}


def load_env():
    env = {}
    for line in (REPO / ".env").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


ENV = load_env()
BASE = ENV["AIRTABLE_BASE_HPF"]
HDR = {"Authorization": f"Bearer {ENV['AIRTABLE_PAT_HPF']}", "User-Agent": "curl/8.7.1"}


def fetch_all(tid):
    """Trae todos los records paginando por offset."""
    recs, offset = [], None
    while True:
        url = f"https://api.airtable.com/v0/{BASE}/{tid}?pageSize=100"
        if offset:
            url += f"&offset={offset}"
        req = urllib.request.Request(url, headers=HDR)
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.load(r)
        recs.extend(d.get("records", []))
        offset = d.get("offset")
        if not offset:
            return recs


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    catalogo, resumen = [], []

    for tid, (nombre, tipo) in TABLAS.items():
        recs = fetch_all(tid)
        vacios = 0
        for r in recs:
            f = r.get("fields", {})
            # nombre del producto según la tabla
            prod = f.get("productos") or f.get("titulo") or f.get("Título") or ""
            if not str(prod).strip():
                vacios += 1
                continue
            adj = f.get("archivo") or f.get("Imagen") or f.get("Métodos(pdf)") or []
            adj0 = adj[0] if isinstance(adj, list) and adj else {}
            catalogo.append({
                "record_id": r["id"],
                "tabla": nombre,
                "tabla_id": tid,
                "tipo": tipo,
                "evento": f.get("evento") or (nombre if tipo == "evento" else None),
                "producto": str(prod).strip(),
                "subcategoria": f.get("subcategoria"),
                "descripcion": f.get("descripcion") or f.get("Descripcion") or "",
                "bot_id": f.get("bot_id"),
                "url_ibb": f.get("URL"),
                "adjunto_nombre": adj0.get("filename"),
                "adjunto_tipo": adj0.get("type"),
                "adjunto_size": adj0.get("size"),
                "adjunto_url_firmada": adj0.get("url"),  # expira: no usable como destino
                "tiene_curl": bool(f.get("CURL") or f.get("curl")),
            })
        resumen.append((nombre, tid, len(recs), len(recs) - vacios, vacios))

    (OUT / "catalogo-airtable.json").write_text(
        json.dumps(catalogo, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"{'tabla':20s} {'id':22s} {'filas':>6s} {'útiles':>7s} {'vacías':>7s}")
    for n, t, tot, ut, vac in resumen:
        print(f"{n:20s} {t:22s} {tot:6d} {ut:7d} {vac:7d}")

    print(f"\nTotal de fichas útiles: {len(catalogo)}")
    con_url = sum(1 for c in catalogo if c["url_ibb"])
    con_adj = sum(1 for c in catalogo if c["adjunto_nombre"])
    sin_media = [c for c in catalogo if not c["url_ibb"] and not c["adjunto_nombre"]]
    print(f"  con URL i.ibb.co : {con_url}")
    print(f"  con adjunto      : {con_adj}")
    print(f"  SIN media alguna : {len(sin_media)}  ← el asset vive sólo en el salesbot de Kommo")
    for c in sin_media:
        print(f"      {c['tabla']:6s} · {c['producto'][:42]:42s} bot_id={c['bot_id']}")
    print(f"\n→ {(OUT / 'catalogo-airtable.json').relative_to(REPO)}")


if __name__ == "__main__":
    main()
