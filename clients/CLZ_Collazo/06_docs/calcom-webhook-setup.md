# Guía rápida: configurar el webhook de cal.com → n8n (CLZ Collazo)

**Objetivo:** registrar en la cuenta cal.com de Collazo un webhook que dispare el workflow `CLZ | Round-Robin cal.com → Google Calendar` cada vez que se crea, reagenda o cancela un booking.

**Pre-requisitos:** workflow `collazo-round-robin-v1.json` importado en n8n con todas las credenciales y calendar IDs ya reemplazados. Schema SQL ya corrido en Postgres. Ver `round-robin-design.md` § 6 para el orden completo.

---

## Datos a tener a mano

| Campo | Valor |
|-------|-------|
| URL del webhook | `https://[TU-INSTANCIA-N8N]/webhook/clz-calcom` |
| Secret (HMAC) | Generar con `openssl rand -hex 32` y guardar en credencial n8n Header Auth |
| Eventos a suscribir | `BOOKING_CREATED`, `BOOKING_RESCHEDULED`, `BOOKING_CANCELLED` |
| Payload format | JSON (default de cal.com) |
| Method | POST (default) |

---

## Pasos en cal.com (plan Team / paga — webhook global)

1. Loguearse en cal.com con la cuenta de Collazo (ver Matías por las credenciales).
2. Ir a **Settings → Developer → Webhooks**.
3. Click en **New Webhook** o **+ Add webhook**.
4. Completar:
   - **Subscriber URL**: `https://[TU-INSTANCIA-N8N]/webhook/clz-calcom`
   - **Event Triggers** (checkboxes): marcar los 3
     - ☑️ `Booking created` (`BOOKING_CREATED`)
     - ☑️ `Booking rescheduled` (`BOOKING_RESCHEDULED`)
     - ☑️ `Booking cancelled` (`BOOKING_CANCELLED`)
   - **Payload Template**: dejar el default (cal.com envía todo el payload completo)
   - **Secret**: pegar el HMAC generado
   - **Active**: ON
5. **Save**.
6. Click en **Ping** desde la UI del webhook para mandar un payload de prueba a n8n. Verificar que el Execution en n8n llegó con 200 OK (entra por la rama `default → Respond (ignored)` porque `Ping` no es uno de los 3 eventos suscritos).

---

## Pasos en cal.com (plan Free — un webhook por event-type)

El plan Free no tiene la opción global. Hay que repetir el procedimiento para cada uno de los 7 event-types del agente Collazo.

Por cada event-type:

1. Ir a **Event Types** → click en el event-type específico (ej. `instalacion-aire`).
2. Tab **Webhooks** → **+ Add webhook**.
3. Completar lo mismo que arriba (URL, eventos, secret).
4. Save.

Event-types a configurar (todos):

- `instalacion-aire`
- `reparacion-aire-acondicionado`
- `mantenimiento-aire-acondicionado`
- `desmontaje-aire-acondicionado`
- `instalacion-calefon`
- `reparacion-calefon`
- `servicio-electrico`

**Importante:** el mismo secret HMAC en los 7. Así una sola credencial n8n los valida a todos.

---

## Verificar el ping

Después del paso 6 (o de un test booking real), abrir el workflow en n8n → tab **Executions** → buscar la ejecución más reciente. Debe:

- Haberse disparado por el nodo `Webhook cal.com`.
- Pasar por `Parse Payload` (ver que `triggerEvent`, `uid`, etc. están seteados).
- Pasar por `Switch by triggerEvent` y caer en una rama o en `Respond (ignored)`.
- Terminar con status `Success` (verde) y devolver 200 OK al webhook de cal.com.

Si en cal.com **Settings → Developer → Webhooks → Delivery history** aparece la entrega como `Failed` con un 4xx/5xx, revisar:

| Error | Causa probable |
|-------|----------------|
| 404 | URL del webhook mal pegada o workflow no activado en n8n |
| 401/403 | Credencial Header Auth del nodo Webhook con secret distinto al de cal.com |
| 500 | Error en algún nodo downstream. Abrir la ejecución en n8n y leer el error rojo |
| Timeout | El flow tardó >10s. Causa rara dado el diseño — chequear si Postgres está caído |

---

## Probar localmente sin booking real

Usar los fixtures de `07_testing/fixtures/`. **Importante:** correr desde la raíz del workspace o usar path absoluto, sino curl da `option -d: error encountered when reading a file`.

```bash
cd /Users/camilo/Downloads/camilo-workspace

# Simular BOOKING_CREATED
curl -X POST https://[TU-INSTANCIA-N8N]/webhook/clz-calcom \
  -H "Content-Type: application/json" \
  -d @clients/CLZ_Collazo/07_testing/fixtures/created.json

# Simular BOOKING_RESCHEDULED
curl -X POST https://[TU-INSTANCIA-N8N]/webhook/clz-calcom \
  -H "Content-Type: application/json" \
  -d @clients/CLZ_Collazo/07_testing/fixtures/rescheduled.json

# Simular BOOKING_CANCELLED
curl -X POST https://[TU-INSTANCIA-N8N]/webhook/clz-calcom \
  -H "Content-Type: application/json" \
  -d @clients/CLZ_Collazo/07_testing/fixtures/cancelled.json
```

Cada uno debe devolver `{ "ok": true, "branch": "..." }`. Ver `07_testing/testing-guide-round-robin-v1.md` § casos C1–C11 para los resultados esperados detallados.

---

## Notas

- **Secret HMAC en v1:** la verificación de la firma `X-Cal-Signature-256` NO está implementada en este workflow (queda como TODO de v1.1). El secret se setea en cal.com solo para tener trazabilidad si alguien llega a postear contra el endpoint desde fuera de cal.com.
- **No exponer la URL del webhook públicamente.** No es secreta per se (la podés ver en cal.com Settings), pero no la pongas en docs públicos del cliente.
- **Re-importar el workflow no rompe el webhook**, porque el `webhookId` (`clz-calcom-rr-v1`) y el `path` (`clz-calcom`) están fijos en el JSON. La URL no cambia.
