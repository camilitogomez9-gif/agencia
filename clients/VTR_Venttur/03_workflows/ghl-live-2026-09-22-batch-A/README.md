# Batch A · Seguridad e higiene · 2026-09-22

Aplicado por Codex el 2026-09-22 03:34 UTC.

## Cambios al workflow `k3aivKSP67S97IHn` ([Venttur] main)

### A1 · Rotar OpenAI key hardcoded en `Transcribir audio/s`

- **Antes:** header `Authorization: Bearer sk-proj-OpKR...` hardcodeado en el nodo (secreto committeado al repo).
- **Después:** `authentication: predefinedCredentialType` + `nodeCredentialType: openAiApi` + `credentials.openAiApi.id: 4mYcYoPAC42ngJYz` (credencial n8n con la key nueva rotada el 21/9).
- Header `Authorization` removido del array de headers custom. `Content-Type: multipart/form-data` preservado.

**⚠️ Pendiente de la agencia en OpenAI dashboard:** rotar / desactivar la key vieja `sk-proj-OpKR…CuH9UCq…` para bloquearla definitivamente (el nodo ya no la usa, pero sigue activa en OpenAI hasta que la revoques).

### A2 · Fix nodo `Hay audios?`

- **Antes:** `and` de 3 conditions — `$json.audio` notEmpty, `$json.audio[0]` notContains "jpeg", `$json.audio[0]` notContains "webp". Blacklist incompleta (fallaba con `.png`, `.gif`, `.jpg`, `.avif`, `.heic`).
- **Después:** `and` de 2 conditions — `$json.audio` notEmpty + `$json.audio[0]` regex `\.(ogg|oga|mp3|m4a|wav|amr|opus)($|\?)`. Whitelist positiva de extensiones de audio válidas.

## Snapshots

| Archivo | sha256 | Descripción |
|---|---|---|
| `../ghl-live-2026-09-21-batch-A/pre/vtr-main.json` | `21bee653dc475312765300fcf083d6c307ee8fe0b40515ce2cb2d6b114d1487e` | Pre-batch (GET vivo del 21/9 20:06 UTC) |
| `mid/vtr-main-patched.json` | `678e5e01064d9cea8067c1d9c5845b0d57a5901cdc02534af52e532075614041` | Post-patch local, pre-PUT |
| `post/vtr-main.json` | `57b9492e4ecd71ac76eb21b23699a4b350518409d42b3d76ddd944293e47355e` | GET vivo post-PUT (2026-09-22 03:34 UTC) |

## Verificación

- Nodo `Transcribir audio/s`: `authentication = predefinedCredentialType` · `credentials.openAiApi.id = 4mYcYoPAC42ngJYz` · sin `Authorization` header hardcoded.
- Nodo `Hay audios?`: 2 conditions · segunda con operator regex y pattern audio whitelist.
- Workflow updatedAt: 2026-09-22T03:34:39.893Z · active=true (sigue en producción atendiendo leads).

## Rollback

Si algo falla:

```bash
python3 -c "
import json, requests
with open('/Users/camilo/Downloads/camilo-workspace/clients/VTR_Venttur/03_workflows/ghl-live-2026-09-21-batch-A/pre/vtr-main.json') as f:
    wf = json.load(f)
put_body = {'name': wf['name'], 'nodes': wf['nodes'], 'connections': wf['connections'], 'settings': wf.get('settings', {})}
# ... PUT a /api/v1/workflows/k3aivKSP67S97IHn con put_body
"
```

O usar el script `scratchpad/vtr_batch_a.py` invertido (aplicar los cambios inversos desde el snapshot pre).

## Script fuente

`scratchpad/vtr_batch_a.py` — script Python idempotente + verificaciones.
