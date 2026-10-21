#!/usr/bin/env python3
"""
Landings de Venttur en GHL: datos + cargador.

Cómo funciona (decisión 22/9, después de probar el editor visual de GHL página por página):
  · Las 50 landings viven como DATOS en un JSON en la biblioteca de medios de GHL (se sube por API).
  · El funnel `LP · Calendarios` lleva en "Código de seguimiento del cuerpo" un CARGADOR de ~1,5 KB que GHL
    inyecta en todas las páginas del funnel: lee la ruta, busca la landing en el JSON y la dibuja.
  · Cada página de GHL sólo tiene que existir (vacía) con su ruta. Ruta desconocida (raíz del dominio o 404)
    → página "Programas".
  · Cambiar una landing = regenerar, subir el JSON nuevo y actualizar la URL en el cargador. Nada de editor.

Fidelidad: el JSON guarda los fragmentos de landings-ghl/_ghl/ comprimidos (estilos y bloques repetidos una
sola vez). Antes de escribir, este script reconstruye cada página en Node con la MISMA función que usa el
cargador y compara byte a byte contra el fragmento; si una sola difiere, aborta.

Salida: landings-ghl/_ghl/landings-data.json   (se sube a GHL con --publicar)
        landings-ghl/_ghl/cargador.html         (se pega en el funnel; lleva la URL del JSON publicado)
Uso:
  python3 generar-renderer-ghl.py               # genera y verifica
  python3 generar-renderer-ghl.py --publicar    # además sube el JSON a GHL y escribe el cargador con su URL
"""
import json, re, subprocess, collections, tempfile, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
GHL = BASE / "landings-ghl/_ghl"
CREDS = Path("/Users/camilo/Downloads/camilo-workspace/clients/VTR_Venttur/06_docs/ghl-credentials.md")
DEFAULT = "programas"

# Función de armado: la misma en Node (verificación) y en el navegador (cargador).
BUILD_JS = (
    "function vtrBuild(D,k){var p=D.p[k]||D.p[D.def];"
    "var b=p.b.map(function(x){return typeof x==='number'?D.d[x]:x}).join('');"
    "return {k:D.p[k]?k:D.def,t:p.t,html:D.s[p.h]+b,v:p.v||{}};}"
    "function vtrScript(D,i,v){return D.x[i].replace(/__EID__/g,v.E||'').replace(/__PROG__/g,v.P||'');}"
)


def cargar():
    paginas = {}
    for line in (GHL / "MANIFEST.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| \[.\] \| (.+?) \| `/([^`]+)` \| (.+?) \| .*? \| `_ghl/(.+?)` \|", line)
        if m:
            _, path, title, arch = m.groups()
            # misma normalización que el cargador: minúsculas y "_" → "-" (GHL no admite "_" en rutas de step)
            paginas[path.lower().replace("_", "-")] = {"t": title.strip(), "frag": (GHL / arch).read_text(encoding="utf-8")}
    return paginas


def comprimir(paginas):
    S, X, DICT = [], [], []
    idx = lambda arr, v: arr.index(v) if v in arr else (arr.append(v) or len(arr) - 1)
    seg_count, pre = collections.Counter(), {}
    for k, p in paginas.items():
        frag = p["frag"]
        i = frag.index('<div class="vtr-lp">')
        cab, cuerpo = frag[:i], frag[i:]
        vars_ = {}

        def tok(m):
            code = m.group(1)
            m1 = re.search(r'getElementById\("([^"]+)"\)', code)
            if m1:
                vars_["E"] = m1.group(1)
                code = code.replace(m1.group(1), "__EID__")
            m2 = re.search(r'var PROGRAMA = ("(?:[^"\\]|\\.)*");', code)
            if m2:
                vars_["P"] = m2.group(1)
                code = code.replace(m2.group(1), "__PROG__")
            return f'<script data-x="{idx(X, code)}"></script>'

        cuerpo_t = re.sub(r"<script>(.*?)</script>", tok, cuerpo, flags=re.S)
        segs = re.findall(r"[^>]*>|[^>]+$", cuerpo_t)
        seg_count.update(segs)
        pre[k] = (idx(S, cab), segs, vars_)
    DICT = [s_ for s_, c in seg_count.items() if c >= 2 and len(s_) >= 24]
    dset = {s_: i for i, s_ in enumerate(DICT)}
    P = {}
    for k, (h, segs, vars_) in pre.items():
        b, lit = [], ""
        for s_ in segs:
            if s_ in dset:
                if lit:
                    b.append(lit)
                    lit = ""
                b.append(dset[s_])
            else:
                lit += s_
        if lit:
            b.append(lit)
        P[k] = {"t": paginas[k]["t"], "h": h, "b": b}
        if vars_:
            P[k]["v"] = vars_
    return {"s": S, "x": X, "d": DICT, "p": P, "def": DEFAULT}


def verificar(data, paginas):
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / "d.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        (Path(td) / "t.js").write_text(
            BUILD_JS + "\nvar D=JSON.parse(require('fs').readFileSync(process.argv[2],'utf8'));var out={};"
            "Object.keys(D.p).forEach(function(k){var r=vtrBuild(D,k);"
            "out[k]={t:r.t,html:r.html.replace(/<script data-x=\"(\\d+)\"><\\/script>/g,"
            "function(_,i){return '<script>'+vtrScript(D,+i,r.v)+'<\\/script>'})};});"
            "out.__fallback=vtrBuild(D,'ruta-que-no-existe').k;"
            "require('fs').writeFileSync(process.argv[3],JSON.stringify(out));", encoding="utf-8")
        subprocess.run(["node", str(Path(td) / "t.js"), str(Path(td) / "d.json"), str(Path(td) / "o.json")], check=True)
        out = json.loads((Path(td) / "o.json").read_text(encoding="utf-8"))
    mal = [k for k, p in paginas.items() if out[k]["html"] != p["frag"] or out[k]["t"] != p["t"]]
    if mal or out["__fallback"] != DEFAULT:
        raise SystemExit(f"❌ reconstrucción distinta al fragmento en: {mal[:5]} — no se escribe nada")


def cargador(url):
    return (
        "<script>(function(){try{"
        "if(document.querySelector('.vtr-lp'))return;"   # páginas armadas antes a mano con el código pegado
        "var k=(location.pathname.replace(/\\/+$/,'').split('/').pop()||'').toLowerCase().replace(/_/g,'-');"
        + BUILD_JS +
        f"fetch({json.dumps(url)}).then(function(r){{return r.json()}}).then(function(D){{"
        "var r=vtrBuild(D,k),host=document.createElement('div');host.className='vtr-host';"
        "host.innerHTML=r.html;document.body.insertBefore(host,document.body.firstChild);document.title=r.t;"
        "var sc=[].slice.call(host.querySelectorAll('script'));"
        "(function run(i){if(i>=sc.length)return;var o=sc[i],n=document.createElement('script');"
        "if(o.getAttribute('src')){n.src=o.getAttribute('src');n.onload=n.onerror=function(){run(i+1)};o.parentNode.replaceChild(n,o);}"
        "else{var xi=o.getAttribute('data-x');n.text=xi!==null?vtrScript(D,+xi,r.v):o.text;o.parentNode.replaceChild(n,o);run(i+1);}"
        "})(0);}).catch(function(e){console.error('vtr-landings',e)});"
        "}catch(e){console.error('vtr-landings',e)}})();</script>"
    )


def publicar(path_json):
    creds = CREDS.read_text()
    pit = re.search(r"PIT_TOKEN\s*=\s*(\S+)", creds).group(1)
    r = subprocess.run(["curl", "-s", "-X", "POST", "https://services.leadconnectorhq.com/medias/upload-file",
                        "-H", f"Authorization: Bearer {pit}", "-H", "Version: 2021-07-28", "-H", "User-Agent: curl/8.4.0",
                        "-F", f"file=@{path_json};type=application/json", "-F", f"name={path_json.name}"],
                       capture_output=True, text=True, check=True)
    d = json.loads(r.stdout)
    if "url" not in d:
        raise SystemExit(f"❌ no se pudo subir el JSON: {r.stdout[:300]}")
    return d["url"], d.get("fileId")


def main():
    paginas = cargar()
    data = comprimir(paginas)
    verificar(data, paginas)
    pj = GHL / "landings-data.json"
    pj.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"✓ {len(paginas)} páginas reconstruidas idénticas (byte a byte) en Node · fallback → /{DEFAULT}")
    print(f"✓ landings-data.json: {pj.stat().st_size:,} bytes")
    if "--publicar" in sys.argv:
        url, fid = publicar(pj)
        (GHL / "cargador.html").write_text(cargador(url), encoding="utf-8")
        (GHL / "cargador-url.txt").write_text(f"{url}\n{fid}\n", encoding="utf-8")
        print(f"✓ JSON publicado en GHL: {url}")
        print(f"✓ cargador.html ({len(cargador(url))} bytes) → pegar en el funnel (Código de seguimiento del cuerpo)")


if __name__ == "__main__":
    main()
