# Fathom Webhook — Payload de Referencia

Documentación del payload que envía Fathom al disparar el evento `call.completed`.

---

## Estructura esperada

```json
{
  "event": "call.completed",
  "data": {
    "id": "call_abc123",
    "title": "Discovery call — Empresa XYZ",
    "date": "2026-03-17T15:30:00Z",
    "duration": 2340,
    "transcript": "Agustín: Hola, gracias por tu tiempo...\nProspecto: Claro, estaba viendo...",
    "summary": "Resumen generado por Fathom...",
    "attendees": [
      { "name": "Agustín", "email": "agustin@[TU-DOMINIO]" },
      { "name": "Juan Pérez", "email": "juan@empresa.com" }
    ]
  }
}
```

## Campos usados en el workflow n8n

| Campo | Ruta en payload | Uso |
|---|---|---|
| `call_id` | `data.id` | Deduplicación en Notion, ID en Pinecone |
| `titulo` | `data.title` | Campo "Nombre" en Notion |
| `fecha` | `data.date` | Campo "Fecha" en Notion |
| `duracion_min` | `Math.round(data.duration / 60)` | Campo "Duración" en Notion |
| `transcripcion` | `data.transcript` | Campo "Transcripción" en Notion, texto para Groq y Pinecone |
| `cliente` | `data.attendees[1].name` | Campo "Cliente" en Notion (índice 1 = prospecto) |
| `vendedor` | `data.attendees[0].name` | Campo "Vendedor" en Notion (índice 0 = el que agenda) |

**Nota:** el índice de attendees depende de cómo Fathom ordena los participantes. Verificar en el primer webhook real y ajustar el nodo "Parse Fathom Payload" si es necesario.

---

## Verificar payload real

Para ver el payload exacto que envía Fathom:
1. Activar el workflow n8n
2. En Fathom: Settings → Webhooks → Send Test Webhook
3. En n8n: abrir la ejecución → ver el output del nodo Webhook
4. Ajustar el nodo "Parse Fathom Payload" según los campos reales
