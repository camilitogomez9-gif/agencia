# Call Audit — Endpoint de Auditoría de Llamadas

Endpoint serverless (Modal) que analiza transcripciones de llamadas de ventas y devuelve un scorecard objetivo en JSON.

## Setup

### 1. Prerrequisitos

- Cuenta en [modal.com](https://modal.com) (free tier suficiente, incluye $30 de créditos)
- API key de OpenAI (platform.openai.com)
- Python 3.11+

### 2. Instalar dependencias

```bash
pip install modal openai pydantic
```

### 3. Configurar Modal

```bash
# Autenticar con tu token de Modal
modal token set --token-id $MODAL_TOKEN_ID --token-secret $MODAL_TOKEN_SECRET
```

Luego crear un Secret en el dashboard de Modal llamado `call-audit-secrets` con:
- `OPENAI_API_KEY` — tu API key de OpenAI
- `CALL_AUDIT_API_KEY` — cualquier string seguro (funciona como password del endpoint)

### 4. Deployar

```bash
cd salidas/call-audit
modal deploy main.py
```

Modal devuelve una URL del estilo:
```
https://[tu-org]--call-audit-analyze.modal.run
```

Guardá esa URL — es la que vas a pegar en el nodo HTTP Request de n8n.

### 5. Testear localmente (sin deploy)

```bash
modal run main.py
```

Esto ejecuta el transcript de ejemplo incluido en `test_local()` y muestra el JSON de output.

### 6. Testear el endpoint en producción

```bash
curl -X POST https://TU-URL.modal.run \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Closer: Hola, ¿cómo estás?...",
    "closer_name": "Juan García",
    "call_date": "2026-02-18",
    "call_outcome": "cerrado",
    "duration_minutes": 45,
    "_api_key": "tu-CALL_AUDIT_API_KEY"
  }'
```

## Campos del request

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `transcript` | string | Sí | Transcripción completa de la llamada |
| `_api_key` | string | Sí | Password del endpoint (CALL_AUDIT_API_KEY) |
| `closer_name` | string | No | Nombre del closer |
| `call_date` | string | No | Fecha de la llamada (YYYY-MM-DD) |
| `call_outcome` | string | No | cerrado / no_cerrado / pendiente / no_calificado |
| `duration_minutes` | int | No | Duración en minutos |
| `business_context` | string | No | Contexto del negocio (ver sección Customización) |

## Customización por cliente

Pasar el campo `business_context` con la estructura de la llamada, avatar y oferta del cliente:

```json
{
  "transcript": "...",
  "business_context": "Vendemos servicio X a emprendedores con equipos de ventas de 2-10 personas. Estructura de la llamada: 1) Apertura y rapport (5 min) 2) Discovery: preguntar por situación actual, dolor, urgencia (15 min) 3) Presentación de la solución conectada al caso (10 min) 4) Manejo de objeciones 5) Cierre y CTA. Objeciones típicas: precio, tiempo, necesito consultarlo.",
  "_api_key": "..."
}
```

El mismo endpoint sirve para múltiples clientes — solo cambia el `business_context`.

## Estructura de archivos

- `main.py` — Endpoint Modal principal
- `prompt.py` — System prompt y construcción del prompt de análisis
- `schema.py` — Modelos Pydantic de input/output
- `CLAUDE.md` — Instrucciones para Claude Code al trabajar en este proyecto
- `.env.example` — Variables de entorno necesarias

## Schema de output

Ver `referencia/auditoria-llamadas-esquema-json.md` para el JSON completo de output con ejemplo.

## Integración con n8n y Airtable

Ver `referencia/auditoria-llamadas-flujo-n8n.json` para el workflow n8n importable.
Ver `referencia/auditoria-llamadas-esquema-airtable.md` para la estructura de la base de Airtable.
