# Handoff · conectar Cloud Code a GHL con PIT

**Para Camilo.** Cómo conectar tu sesión de Claude Code a la sub-cuenta GHL de Venttur usando un Personal Internal Token (PIT). Es el patrón que ya usamos en este workspace y desbloquea la mayoría de las operaciones sobre GHL desde Cloud Code.

## Qué es un PIT

Personal Internal Token de GHL. Reemplaza al OAuth API para uso interno propio. Se crea desde la UI de GHL con el scope mínimo necesario, se guarda en un `.env` gitignoreado, y se manda como header en cada llamada a la API de GHL.

Alcance mínimo recomendado para VTR: **Contacts (read + write), Opportunities (read + write), Custom Fields (read), Tags (read + write), Calendars (read + write si vas a tocar calendarios).**

## 1. Crear el PIT

1. Entrá a la sub-cuenta GHL de Venttur (`7aXb4JCKsWV5nUyBXeSF`, nombre "Venttur").
2. Settings → Business Profile → Private Integrations (o el equivalente del menú).
3. New Token → seleccionar los scopes de arriba → generar.
4. Copiá el token completo. Solo se muestra una vez.

Nombralo algo como `Camilo · Cloud Code · VTR` así podés revocarlo/re-generarlo puntual sin tocar los demás.

## 2. Guardar el token localmente

En tu workspace de Claude Code, agregá el token a un `.env` en la raíz del proyecto:

```bash
# .env (gitignoreado)
GHL_PIT_VTR=pit-XXXXXXXXXXXXXXXXXXXXXXXX
GHL_LOCATION_ID=7aXb4JCKsWV5nUyBXeSF
GHL_COMPANY_ID=WbuYAfjKqOU9k7R5t9RL
```

Verificá que tu `.gitignore` incluye `.env`. Si no, agregalo:

```
# .gitignore
.env
.env.*
```

## 3. Patrón de uso desde Cloud Code

En cualquier script de Bash o Python:

```bash
set -a; source .env; set +a
curl -s "https://services.leadconnectorhq.com/contacts/search" \
  -H "Authorization: Bearer $GHL_PIT_VTR" \
  -H "Version: 2021-07-28" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36" \
  -d "{\"locationId\":\"$GHL_LOCATION_ID\", \"pageLimit\":1, \"filters\":[{\"group\":\"OR\",\"filters\":[{\"field\":\"phone\",\"operator\":\"eq\",\"value\":\"+521<10>\"}]}]}"
```

**⚠️ User-Agent obligatorio.** La API de GHL responde `Cloudflare 1010` si el UA es el default de curl o de Node. Copiar el UA de arriba en TODA llamada HTTP a GHL (verificado en el sandbox 2026-09-03; también documentado en `04_guia_migracion/07_n8n_agente_canal.md §7.7`).

Python equivalente:

```python
import os, urllib.request, json
HEADERS = {
    "Authorization": f"Bearer {os.environ['GHL_PIT_VTR']}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 ..."
}
req = urllib.request.Request(
    "https://services.leadconnectorhq.com/contacts/search",
    data=json.dumps({"locationId": os.environ["GHL_LOCATION_ID"], "pageLimit": 1, ...}).encode(),
    headers=HEADERS
)
with urllib.request.urlopen(req) as r:
    print(json.load(r))
```

## 4. Endpoints útiles para arrancar

Todos con `Authorization: Bearer $GHL_PIT_VTR` + Version 2021-07-28 + UA normal.

| Qué | Endpoint |
|---|---|
| Buscar contact por teléfono | `POST /contacts/search` con `filters: [{field: phone, operator: eq, value: +521...}]` |
| Upsert contact (dedup por phone) | `POST /contacts/upsert` con `locationId`, `phone`, `firstName`, etc. |
| Get contact by ID | `GET /contacts/{contactId}` |
| Update contact (assign, DND, custom fields) | `PUT /contacts/{contactId}` |
| Listar custom fields | `GET /locations/{locationId}/customFields?model=contact` |
| Listar tags | `GET /locations/{locationId}/tags` |
| Listar pipelines/stages | `GET /opportunities/pipelines?locationId={locationId}` |
| Get opportunity by ID | `GET /opportunities/{oppId}` |
| Update opportunity (stage, custom fields) | `PUT /opportunities/{oppId}` |

Docs oficiales de GHL: https://highlevel.stoplight.io/docs/integrations/

## 5. Lo que NO se puede hacer con PIT

Algunas cosas requieren OAuth de app o el Marketplace API:

- Crear/editar workflows GHL (UI-only)
- Crear/editar formularios
- Editar la conexión de Google Calendar de un usuario (necesita OAuth con ese usuario)

Para esas cosas, la política sigue siendo: **Claude Code te guía paso a paso pero vos las hacés en la UI** (consistente con el patrón que usamos en este WS).

## 6. Sub-cuenta VTR — IDs canónicos

| Qué | ID |
|---|---|
| Sub-cuenta GHL prod ("Venttur") | `7aXb4JCKsWV5nUyBXeSF` |
| Company GHL | `WbuYAfjKqOU9k7R5t9RL` |
| Country | MX · Timezone: `America/Mexico_City` · Currency: MXN |
| Custom field `programa_interes` | `xK2NFqtz1DYUw3gYdn8I` |
| Custom field `link_enviado` | `rHzGNiesWuESPmSZyviJ` |
| Custom field `estado_conversacion` | `Omg1BvHmpXR0MMGsrpFh` |
| Custom field `toques_enviados` | `ez934lu03v7nC4ZRS7LJ` |
| Custom field `origen` | `BEhJWnXS9SQovJTLSA2W` |
| Custom field `fuente_lead` | `2hv0GovhSzZO3hj9cFqm` |
| Custom field `grado_escolar` | `HjNeRtIv6XHHMgFbtsaR` |
| Custom field `inicio_deseado` | `dUvMI4NaamfRPOF1p95q` |
| Custom field `nivel_ingles` | `uOecQsOv9i3uwMeSgEkX` |
| Tag `cualificado` | `SAf2PNSjPNNYJisUSAFq` |

## 7. Cómo probar que todo funciona

Este one-liner debería devolverte `{"contacts": [...], "total": N, ...}` con al menos 1 contact:

```bash
set -a; source .env; set +a
curl -s "https://services.leadconnectorhq.com/contacts/?locationId=$GHL_LOCATION_ID&limit=1" \
  -H "Authorization: Bearer $GHL_PIT_VTR" \
  -H "Version: 2021-07-28" \
  -H "Accept: application/json" \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36" | python3 -m json.tool | head -30
```

Si te devuelve JSON con el contact, andás. Si te devuelve HTML de Cloudflare 1010, chequeá el User-Agent.

## 8. Referencias

- El staging n8n `3sLd7KY3o8I7NvXi` usa este patrón. Ver los nodos `Buscar Contact GHL` (POST /contacts/search) y el sub-workflow con `crear_contacto` (POST /contacts/upsert) y `elevar` (PUT /contacts/{id}) — sirven como muestras funcionales.
- Sandbox de validación de la API GHL: `04_guia_migracion/01_sandbox_validacion.md`.
- Bandera del UA obligatorio: `04_guia_migracion/07_n8n_agente_canal.md §7.7`.
- Rotación de secretos (si se compromete el PIT): `06_docs/plan-rotacion-secretos-2026-09-11.md`.
