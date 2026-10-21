# Base congelada — solución pre-migración HPF · PRODUCCIÓN (2026-08-06)

**Ésta es la fuente de verdad** para reconstruir la migración a GHL.
Instancia: **`dev[TU-INSTANCIA-N8N]`** (no la de agencia).
Exportado read-only vía `GET`; ningún workflow fue modificado (Regla 0).

```bash
python3 scripts/utilities/hpf-congelar-base.py --verificar   # detecta drift
```

## Contenido — 8 workflows, 403 nodos

| Archivo | n8n id | nodos | active | rol |
|---|---|---|---|---|
| `main-happy-flops.json` | `pYtiBlhOTr7HVPmr` | 239 | ✅ | main; webhook `1bfb19eb-2157-42d0-84d7-23ea334699ec` + `executeWorkflowTrigger` |
| `seg-rebeca.json` | `YR8yBPNdgVl0TxT1` | 31 | — | reenganche post-saludo |
| `seg-imagen.json` | `D04kO8VPKoAKL004` | 38 | — | reenganche post-evento + CF 1099424 |
| `seg-cotizacion.json` | `dNzLtCZFJnIqjlZx` | 42 | — | reenganche post-fichas + clasificador de desinterés |
| `seg-7pasos.json` | `xo1sLt9cAhFAC6k3` | 20 | — | ola única 24 h, sólo mueve etapa |
| `atencion-personalizada.json` | `SUgT7UPYyQ3NDgRp` | 3 | — | Telegram + PATCH etapa |
| `tool-calculadora.json` | `OPiuPFwRmq6QgACL` | 5 | — | CALCULADORA (envío + empaque + mínimos) |
| `kommo-salesbot-text-capture-runner.json` | `bYMfYToYsZMFpVDw` | 25 | — | captura de texto de salesbots |

Los ids **coinciden con los del repo** (`happyflops-main-v3.json` y hermanos). La confusión previa
venía de una copia vieja homónima en la instancia de agencia — ver
[`../base-2026-08-06/README.md`](../base-2026-08-06/README.md).

`BASELINE.json` guarda `versionId`, `updatedAt` y `sha256` (calculado sobre
`{name, nodes, connections, settings}`).

## Arquitectura de envío: salesbots

El main manda mensajes en dos pasos, no uno:

1. `PATCH https://happyflopss.amocrm.com/api/v4/leads/{entity_id}` escribiendo el texto en el
   **campo custom `1099420`** del lead.
2. `POST https://happyflopss.amocrm.com/api/v2/salesbot/run` con `{bot_id, entity_id, entity_type: 2}`.
   El template del salesbot, configurado **dentro de Kommo**, lee `{{lead.cf.1099420}}` y lo envía.

Los `bot_id` de catálogo salen de la columna `bot_id` de Airtable — un salesbot por producto por evento.
**El contenido de esos salesbots no está en este JSON**: vive en Kommo. Para las fichas de producto se
recupera desde Airtable (`descripcion` + `URL`/`archivo`); para los videos, desde la Media Library de GHL.

Censo del main: 66 `httpRequest` · 46 `if` · 13 `code` · 11 `set` · 10 `wait` · 9 `openAi` ·
9 `telegram` · 8 `agent` · 7 `lmChatOpenAi` · 7 `memoryPostgresChat` · 6 `redis` · 6 `executeWorkflow` ·
4 `postgres` · 3 `airtable` · 3 `switch` · 3 `toolWorkflow` · 1 `webhook` · 1 `executeWorkflowTrigger`.

## Hallazgos sobre este build

### 1. ⚠️ Referencia rota en producción
`Execute Workflow4` (rama imagen del seguimiento de 7 pasos) apunta a
`nkRBXbc4G0Cn67gY` — **ese workflow no existe en la instancia** (`GET` → HTTPError). Su gemelo de la
rama texto, `Execute Workflow3`, sí resuelve (`xo1sLt9cAhFAC6k3`). O sea: **el seguimiento de 7 pasos
nunca se dispara para conversaciones que entraron por imagen.**

### 2. ✅ La CALCULADORA con mínimos SÍ está deployada
El sub-workflow tiene dos nodos de código y el trigger va a **`Code2`** (14.318 chars, con
`MIN_BY_PRODUCT` y `MINIMO_NO_ALCANZADO`) → `Edit Fields1`. `Code1` (11.846 chars, sin mínimos) quedó
huérfano, sin conexión de entrada.

*(Corrige una afirmación previa de este repo: el fix de mínimos del 2026-07-15 sí llegó a producción.)*

### 3. ⚠️ Pero el rechazo por mínimo nunca le llega al agente
`Edit Fields1` mapea un solo campo:
`"Cantidad de cajas necesarias y costo de envio" = {{ $json.resumen_cajas }}`.

Cuando `Code2` rechaza por mínimo devuelve `{error, detalle_violaciones, message_to_agent}` —
**sin `resumen_cajas`**. El LLM recibe ese campo vacío y no ve el `message_to_agent` que le explica
qué mínimo se violó. La validación corta el cálculo pero no comunica el motivo.

### 4. El trigger extra
Además del webhook hay un `executeWorkflowTrigger` ("When Executed by Another Workflow") cableado a
`If25`, para poder correr el flujo a mano. Explica por qué la pantalla de n8n muestra ese nodo y el
export del repo (más viejo) no.
