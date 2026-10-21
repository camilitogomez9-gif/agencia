#!/usr/bin/env python3
"""
Verifica las landings publicadas en GHL contra landings-ghl/_ghl/MANIFEST.md.

Por página: HTTP 200 y que sirva el cargador del funnel (páginas de plantilla: el contenido sale del JSON,
verificado byte a byte al generarlo). Páginas viejas con código pegado a mano: título + huellas del fragmento.

Uso:
  python3 verificar-landings-ghl.py                          # contra vtr.[TU-DOMINIO] (pruebas)
  python3 verificar-landings-ghl.py --dominio promo.venttur.com
  python3 verificar-landings-ghl.py --solo Campamentos-Calendario,agendar-ema
  python3 verificar-landings-ghl.py --redirects --dominio promo.venttur.com   # los redirects de redirects.json
"""
import re, sys, json, random, html as H, urllib.request, urllib.error
from pathlib import Path

GHL = Path(__file__).resolve().parent.parent / "landings-ghl/_ghl"


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def huellas(frag):
    """Strings que tienen que aparecer tal cual en la página servida."""
    h = set(re.findall(r'id="([A-Za-z0-9]{20}_\d+)"', frag))                     # iframe de calendario
    h |= set(re.findall(r'href="(https://promo\.venttur\.com/[^"]+)"', frag))   # botones de aventurera
    h |= set(re.findall(r'href="(/[A-Za-z]+-Calendario)"', frag))               # botones de Programas
    m = re.search(r"<p>([^<]{12,})</p>", frag)                                   # subtítulo del hero
    if m:
        h.add(m.group(1))
    if "location.search" in frag:
        h.add("location.search.replace(")
    return h


class _SinSeguir(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def verificar_redirects(dom):
    """Cada path viejo tiene que responder 301/302 con Location = el destino de redirects.json (el destino se
    escribe con promo.venttur.com: en otro dominio se compara sólo ruta + query)."""
    opener = urllib.request.build_opener(_SinSeguir)
    ok = mal = 0
    for r in json.loads((GHL / "redirects.json").read_text(encoding="utf-8")):
        url = f"https://{dom}{r['path']}"
        try:
            resp = opener.open(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 verificador-vtr"}), timeout=30)
            code, loc = resp.getcode(), resp.headers.get("Location", "")
        except urllib.error.HTTPError as e:
            code, loc = e.code, e.headers.get("Location", "")
        except Exception as e:
            code, loc = str(e)[:40], ""
        esperado = r["target"]
        if dom != "promo.venttur.com":
            esperado = re.sub(r"^https://promo\.venttur\.com", "", esperado)
            loc = re.sub(rf"^https://{re.escape(dom)}(?=/|$)", "", loc, flags=re.I)   # sólo el dominio probado
        if code in (301, 302, 307, 308) and loc.rstrip("/").lower() == esperado.rstrip("/").lower():
            ok += 1
        else:
            mal += 1
            print(f"  ✗ {r['path']:45} {code} → {loc or '—'}  (esperado {esperado})")
    print(f"\n{ok} redirects OK · {mal} con problemas · dominio {dom}")
    sys.exit(1 if mal else 0)


def main():
    dom = arg("--dominio", "vtr.[TU-DOMINIO]")
    if "--redirects" in sys.argv:
        return verificar_redirects(dom)
    solo = set(filter(None, (arg("--solo", "") or "").split(",")))
    filas = []
    for line in (GHL / "MANIFEST.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| \[.\] \| (.+?) \| `(/[^`]+)` \| (.+?) \| .*? \| `_ghl/(.+?)` \|", line)
        if m:
            filas.append(m.groups())
    ok = mal = 0
    for name, path, title, arch in filas:
        if solo and name not in solo:
            continue
        url = f"https://{dom}{path}?_v={random.randint(1, 10**9)}"  # esquiva la caché de 60 s del CDN de GHL
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 verificador-vtr"})
            # sin seguir redirects: una ruta sin step cae en /programas (que tiene el cargador) y daría OK falso
            with urllib.request.build_opener(_SinSeguir).open(req, timeout=30) as r:
                code, body = r.getcode(), r.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            code, body = e.code, ""
        except Exception as e:
            code, body = str(e)[:40], ""
        problemas = []
        # GHL incrusta el código del funnel escapado (\u002F): se busca sólo el nombre del archivo del JSON
        url_json = (GHL / "cargador-url.txt").read_text().split()[0].rsplit("/", 1)[-1] if (GHL / "cargador-url.txt").exists() else None
        if code != 200:
            problemas.append(f"HTTP {code}")
        elif url_json and url_json in body and 'class="vtr-lp"' not in body:
            pass  # página de plantilla publicada con el cargador: el contenido sale del JSON (verificado byte a byte al generarlo)
        elif 'class="vtr-lp"' not in body:
            problemas.append("página sin publicar o sin el cargador del funnel")
        else:
            t = re.search(r"<title[^>]*>(.*?)</title>", body, re.S)
            tt = H.unescape(t.group(1)).strip() if t else ""
            if tt != title.strip():
                problemas.append(f"título «{tt}» ≠ «{title.strip()}»")
            cuerpo = H.unescape(body)
            faltan = [x for x in huellas((GHL / arch).read_text(encoding="utf-8")) if H.unescape(x) not in cuerpo]
            if faltan:
                problemas.append("falta: " + ", ".join(f[:45] for f in faltan[:3]))
        if problemas:
            mal += 1
            print(f"  ✗ {path:38} {' · '.join(problemas)}")
        else:
            ok += 1
            print(f"  ✓ {path}")
    print(f"\n{ok} OK · {mal} con problemas · dominio {dom}")
    sys.exit(1 if mal else 0)


if __name__ == "__main__":
    main()
