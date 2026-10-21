"""
Helper compartido para la ejecución de la migración VTR → GHL (Etapa 5).
- Carga credenciales desde el archivo GITIGNORED `06_docs/ghl-credentials.md` (nunca hardcodear).
- Manda el User-Agent browser-like OBLIGATORIO (la API de GHL da Cloudflare 1010 al UA por defecto).
- Solo stdlib (urllib) — sin dependencias externas.
- NUNCA loguea el token.

Uso:
    from _ghl_client import GHL, load_n8n
    g = GHL()
    data = g.get("/contacts/", params={"locationId": g.location_id, "limit": 100})
    g.post("/contacts/upsert", {"phone": "+521...", ...})
"""
import json, os, re, time, urllib.request, urllib.parse, urllib.error

REPO = "/Users/camilo/Downloads/camilo-workspace"
CREDS_GHL = f"{REPO}/clients/VTR_Venttur/06_docs/ghl-credentials.md"
DOTENV = f"{REPO}/.env"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")


def _parse_kv(path, key):
    """Extrae `KEY = value` de un archivo tipo credenciales/.env (primer match)."""
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(rf"\s*(?:export\s+)?{re.escape(key)}\s*=\s*(.+?)\s*(?:#.*)?$", line)
            if m:
                return m.group(1).strip().strip('"').strip("'")
    return None


def load_n8n():
    base = _parse_kv(DOTENV, "N8N_BASE_URL")
    key = _parse_kv(DOTENV, "N8N_API_KEY")
    return base, key


class GHL:
    BASE = "https://services.leadconnectorhq.com"
    VERSION = "2021-07-28"

    def __init__(self):
        self.token = _parse_kv(CREDS_GHL, "PIT_TOKEN")
        self.location_id = _parse_kv(CREDS_GHL, "LOCATION_ID")
        if not self.token or not self.location_id:
            raise RuntimeError("No pude leer PIT_TOKEN/LOCATION_ID de ghl-credentials.md")

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Version": self.VERSION,
            "Content-Type": "application/json",
            "User-Agent": UA,
            "Accept": "application/json",
        }

    def _req(self, method, path, params=None, body=None, retries=6):
        url = self.BASE + path
        if params:
            url += "?" + urllib.parse.urlencode(params, doseq=True)
        data = json.dumps(body).encode() if body is not None else None
        last = None
        for attempt in range(retries):
            req = urllib.request.Request(url, data=data, method=method, headers=self._headers())
            try:
                with urllib.request.urlopen(req, timeout=40) as r:
                    raw = r.read().decode()
                    return r.status, (json.loads(raw) if raw else {})
            except urllib.error.HTTPError as e:
                raw = e.read().decode()
                last = (e.code, _safe_json(raw))
                if e.code == 429:
                    # Si el cap DIARIO está en 0 → no reintentar (es inútil y quema el burst cuando resetee)
                    daily = None
                    try: daily = e.headers.get("X-RateLimit-Daily-Remaining")
                    except Exception: pass
                    if daily is not None and str(daily).strip() == "0":
                        return (429, {"error": "daily_cap_exhausted", "daily_remaining": 0})
                    time.sleep(min(12, 3 * (attempt + 1)))   # burst 429 transitorio (25/10s)
                    continue
                if e.code in (500, 502, 503, 504):
                    time.sleep(min(20, 3 * (2 ** attempt)))
                    continue
                return last
            except urllib.error.URLError as e:
                last = (0, {"error": str(e)})
                time.sleep(1.5 * (attempt + 1))
        return last

    def get(self, path, params=None):
        return self._req("GET", path, params=params)

    def post(self, path, body, params=None):
        return self._req("POST", path, params=params, body=body)

    def put(self, path, body, params=None):
        return self._req("PUT", path, params=params, body=body)

    def delete(self, path, params=None):
        return self._req("DELETE", path, params=params)


def _safe_json(raw):
    try:
        return json.loads(raw)
    except Exception:
        return {"_raw": raw[:500]}


if __name__ == "__main__":
    g = GHL()
    st, d = g.get(f"/locations/{g.location_id}")
    loc = d.get("location", d)
    print("PIT OK" if st == 200 else f"PIT FALLA {st}",
          "· location:", loc.get("name"), loc.get("id"))
