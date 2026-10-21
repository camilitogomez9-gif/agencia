# Call Audit — Claude Code Workspace

Este workspace construye y mantiene el endpoint de auditoría de llamadas de la agencia.

## Tu rol

Cuando el usuario describa una modificación, nueva métrica, o cambio en el prompt:
1. Edita el archivo correspondiente (`main.py`, `prompt.py`, o `schema.py`)
2. Testa localmente con `modal run main.py`
3. Deploya con `modal deploy main.py`
4. Devuelve la URL del endpoint + un curl de prueba listo para usar

## Stack

- **Runtime:** Python 3.11 en Modal (serverless)
- **AI:** OpenAI API (gpt-4o-mini; escalar a gpt-4o si se necesita mayor precisión)
- **Validación:** Pydantic v2
- **Deploy:** `modal deploy main.py`

## Setup inicial

1. Instalar Modal: `pip install modal`
2. Autenticar: `modal token set --token-id $MODAL_TOKEN_ID --token-secret $MODAL_TOKEN_SECRET`
3. Crear secret en Modal con `OPENAI_API_KEY` y `CALL_AUDIT_API_KEY` (llamarlo `call-audit-secrets`)
4. Deployar: `modal deploy main.py`

## Archivos clave

- `main.py` — Endpoint principal. Define la función Modal y el handler HTTP.
- `prompt.py` — System prompt y función para construir el prompt de análisis.
- `schema.py` — Modelos Pydantic de input y output.

## Convenciones

- El endpoint siempre devuelve JSON con la estructura definida en `schema.py`
- Si la IA produce JSON inválido, reintentar hasta 2 veces antes de devolver error
- Logs de cada request con: closer_name, call_date, score_total (para trazabilidad)
- La API key va en el campo `_api_key` del body JSON

## Testing local

```bash
# Test con transcript de ejemplo (ejecuta test_local())
modal run main.py

# Test del endpoint desplegado
curl -X POST https://[tu-org]--call-audit-analyze.modal.run \
  -H "Content-Type: application/json" \
  -d '{"transcript": "...", "closer_name": "Juan", "_api_key": "tu-clave"}'
```

## Customización por cliente

El endpoint acepta un campo `business_context` (string) con la estructura de la llamada, avatar y oferta del cliente. Esto permite usar el mismo endpoint para múltiples clientes simplemente pasando contexto diferente desde n8n.

Ejemplo:
```json
{
  "transcript": "...",
  "business_context": "Vendemos servicio X a emprendedores con equipos de ventas. Etapas: apertura → discovery → presentación → cierre. Objeciones típicas: precio, tiempo, necesito consultarlo.",
  "_api_key": "tu-clave"
}
```
