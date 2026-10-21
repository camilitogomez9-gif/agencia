# Testing Guide — Round-Robin cal.com → Google Calendar (CLZ Collazo)

**Versión:** v1
**Workflow:** `03_workflows/collazo-round-robin-v1.json`
**Última actualización:** 2026-06-10

---

## Pre-requisitos antes de testear

1. Schema SQL aplicado en Postgres Collazo (3 tablas + seeds). Verificar:
   ```sql
   SELECT * FROM clz_round_robin_state;       -- 1 fila con last_assigned='fabian'
   SELECT count(*) FROM clz_event_type_routing; -- 7 filas, todas en 'round-robin'
   SELECT count(*) FROM clz_event_assignment;   -- 0
   ```
2. Workflow importado, **active = true**, calendars y credenciales reemplazados.
3. Endpoint del webhook accesible: `https://[TU-INSTANCIA-N8N]/webhook/clz-calcom`.
4. Fixtures disponibles en `07_testing/fixtures/`.
5. Acceso visual al Google Calendar de Matías y al de Fabián (para verificación).

> **Importante:** los fixtures usan `iCalUID` ficticio. En smoke test contra cal.com real, el `getAll` por iCalUID encontrará el evento solo si efectivamente lo creaste con un booking real. Para fixtures sintéticos, el move flow caerá a la rama "no encontrado" → `GCal Fabian create` corre igual (continueOnFail está activo en el delete).

---

## Reset entre tests

Antes de cada bloque de tests (no por cada caso):

```sql
-- Limpiar mapping
TRUNCATE clz_event_assignment;

-- Resetear singleton
UPDATE clz_round_robin_state
SET last_assigned = 'fabian', total_count = 0,
    matias_paused = FALSE, fabian_paused = FALSE,
    updated_at = NOW()
WHERE id = 1;

-- Resetear routing a default
UPDATE clz_event_type_routing SET target = 'round-robin';
```

En Google Calendar de Matías y Fabián: borrar manualmente cualquier evento que haya quedado de tests anteriores con título "Instalación Aire — Juan Pérez con Collazo" (o usar otro título único por sesión de testing).

---

## Casos de testing

### C1 — Primer booking real → Matías

**Setup:** estado fresco (reset arriba).
**Acción** (correr desde la raíz del workspace `/Users/camilo/Downloads/camilo-workspace`, o usar path absoluto):
```bash
cd /Users/camilo/Downloads/camilo-workspace
curl -X POST https://[TU-INSTANCIA-N8N]/webhook/clz-calcom \
  -H "Content-Type: application/json" \
  -d @clients/CLZ_Collazo/07_testing/fixtures/created.json
```
**Resultado esperado:**
- Response: `{ "ok": true, "branch": "created-matias-rr", "assigned_to": "matias", "uid": "test-create-001-abc" }`
- `clz_round_robin_state.last_assigned = 'matias'`, `total_count = 1`.
- `clz_event_assignment` tiene 1 fila con `cal_com_uid='test-create-001-abc'`, `assigned_to='matias'`, `gcal_event_id_fabian IS NULL`.
- Google Calendar de Matías: sin cambios (el evento, si existió por booking real, sigue ahí).
- Google Calendar de Fabián: sin cambios.

---

### C2 — Segundo booking → Fabián (move flow)

**Setup:** post C1.
**Acción:** modificar `uid` e `iCalUID` del fixture a `test-create-002-def` (`created.json` con `sed` o pegar en otro archivo). Enviar.
**Resultado esperado:**
- Response: `{ "ok": true, "branch": "created-matias", ..., "assigned_to": "matias", "uid": "test-create-002-def" }`. **Nota:** el `branch` en el response del move flow dice `"created-matias"` por hardcode, pero el `assigned_to` real está en la DB.

  ⚠️ **Cosmético:** el response del `Respond (move done)` tiene el label `created-matias` por error de copia. No afecta funcionalidad. Issue de v1.1.

- `clz_round_robin_state.last_assigned = 'fabian'`, `total_count = 2`.
- `clz_event_assignment` tiene 2 filas. La nueva con `assigned_to='fabian'`, `gcal_event_id_fabian` populado.
- Google Calendar de Matías: evento del booking original eliminado (si existía por booking real).
- Google Calendar de Fabián: evento nuevo idéntico (mismo summary, start, end, location).

---

### C3 — Tercer booking → Matías (vuelve a alternar)

**Setup:** post C2.
**Acción:** modificar `uid` a `test-create-003-ghi`. Enviar.
**Resultado esperado:**
- `last_assigned = 'matias'`, `total_count = 3`.
- Nueva fila con `assigned_to='matias'`, `gcal_event_id_fabian IS NULL`.

---

### C4 — Cancelar booking que estaba en Fabián

**Setup:** post C2 (booking `test-create-002-def` en Fabián).
**Acción:** copiar `cancelled.json` cambiando `payload.uid` a `test-create-002-def`. Enviar.
**Resultado esperado:**
- Response: `{ "ok": true, "branch": "cancelled-fabian", "uid": "test-create-002-def" }`.
- `clz_event_assignment` para ese uid: `status='cancelled'`.
- Google Calendar de Fabián: evento eliminado.

---

### C5 — Reagendar booking que estaba en Fabián

**Setup:** post C2 sin cancelar.
**Acción:** enviar `rescheduled.json` (que ya trae `rescheduleUid='test-create-001-abc'` y nuevo `uid='test-create-001-resched-NEW'` con nuevo horario). Cambiar el `rescheduleUid` al uid de C2 (`test-create-002-def`).
**Resultado esperado:**
- Response: `{ "ok": true, "branch": "rescheduled-fabian", ... }`.
- `clz_event_assignment` para el booking: `cal_com_uid` actualizado al nuevo uid, `start_time` y `end_time` con los nuevos valores, `status='rescheduled'`.
- Google Calendar de Fabián: evento updateado (mismo eventId, nuevo horario).

---

### C6 — Cancelar booking que estaba en Matías

**Setup:** post C1.
**Acción:** copiar `cancelled.json` cambiando `payload.uid` a `test-create-001-abc`. Enviar.
**Resultado esperado:**
- Response: `{ "ok": true, "branch": "cancelled-matias", "uid": "test-create-001-abc" }`.
- `clz_event_assignment`: `status='cancelled'` para esa fila.
- Google Calendar de Matías y Fabián: sin cambios desde n8n (cal.com ya borró el evento original de Matías si existía por booking real).

---

### C7 — Concurrencia (UPDATE atómico)

**Setup:** reset completo.
**Acción:** mandar 2 webhooks simultáneamente con uids distintos:
```bash
curl -X POST https://[TU-INSTANCIA-N8N]/webhook/clz-calcom -H "Content-Type: application/json" -d @fixtures/created.json &
curl -X POST https://[TU-INSTANCIA-N8N]/webhook/clz-calcom -H "Content-Type: application/json" -d @fixtures/created-2.json &
wait
```
(crear `created-2.json` cambiando `uid` e `iCalUID` para que no choque con C1)
**Resultado esperado:**
- 2 ejecuciones en n8n, ambas 200 OK.
- `clz_round_robin_state.total_count = 2`.
- `clz_event_assignment`: 2 filas, una con `assigned_to='matias'` y otra con `assigned_to='fabian'`. **Nunca 2 con el mismo `assigned_to`.**

---

### C8 — Retry de cal.com (idempotencia)

**Setup:** reset.
**Acción:** mandar el mismo `created.json` 2 veces seguidas.
**Resultado esperado:**
- Primera ejecución: insert OK, fila creada.
- Segunda ejecución: `ON CONFLICT DO NOTHING` evita duplicar la fila. `last_assigned` cambia 2 veces (de fabian→matias en la primera, de matias→fabian en la segunda — **bug potencial:** el RR alterna 2 veces aunque el booking es el mismo).

  ⚠️ **Limitación conocida v1:** el UPDATE atómico corre antes del INSERT y no chequea si el uid ya existe. Si el webhook se repite, el contador avanza una posición extra.

  **Mitigación a futuro:** mover el INSERT antes del UPDATE atómico y solo alternar si el INSERT escribió fila (RETURNING). Queda para v1.1.

- Solo 1 fila en `clz_event_assignment`. Google Calendar no se ve afectado en la 2da pasada (Fabián ya tiene el evento; el create silencioso crearía un duplicado — TODO chequear si esto pasa).

---

### C9 — Matías pausado

**Setup:** reset + `UPDATE clz_round_robin_state SET matias_paused=TRUE WHERE id=1;`.
**Acción:** mandar 3 webhooks con uids distintos.
**Resultado esperado:**
- Los 3 van a Fabián. `last_assigned` queda en `fabian`, `total_count = 3`.
- 3 filas en `clz_event_assignment`, todas con `assigned_to='fabian'`.

---

### C10 — Override por servicio (routing forzado)

**Setup:** reset + `UPDATE clz_event_type_routing SET target='fabian' WHERE event_type_slug='servicio-electrico';`.
**Acción:** mandar webhook con `eventType.slug='servicio-electrico'` (modificar `created.json`).
**Resultado esperado:**
- Response: branch del move flow.
- `last_assigned` NO cambia (no se llamó el UPDATE atómico).
- Fila con `assigned_to='fabian'`.

---

### C11 — Evento no encontrado en Matías (simulación de lag)

**Setup:** post C1 (sin haber creado el evento manualmente en Google Calendar de Matías) + RR ya posicionado en Matías así el siguiente va a Fabián.
**Acción:** mandar webhook con uid ficticio (que NO existe en GCal). `GCal Matias getAll` no encuentra nada.
**Resultado esperado:**
- `IF evento encontrado?` → branch FALSE.
- Skip de delete. `GCal Fabian create` corre igual.
- Fila con `assigned_to='fabian'`, `gcal_event_id_matias IS NULL` (no se pudo capturar), `gcal_event_id_fabian` populado.
- **Visualmente:** Matías queda con "hueco" para ese slot (no tenía el evento → no hay nada que borrar), Fabián tiene el evento creado.
- TODO de v1.1: Telegram alert "no se encontró evento en Matías para uid X — Matías queda libre, Fabián recibe el evento".

---

## Triage por tipo de fallo

| Síntoma | Probable causa | Cómo verificar |
|---------|----------------|----------------|
| 404 en el webhook | URL mal pegada en cal.com o workflow inactivo | Click "Ping" en cal.com → ver Execution en n8n |
| Execution 500 en el primer Postgres | Schema no aplicado | `SELECT * FROM clz_round_robin_state;` desde Supabase |
| `last_assigned` no cambia | Sentencia UPDATE no entró por algún `combinator` mal armado en switch | Abrir nodo Postgres, ver `queryReplacement` evaluado |
| Evento creado en ambos calendars | El move flow corrió pero el delete falló silenciosamente | Revisar log del nodo `GCal Matias delete` |
| Fabián recibe email/popup de invitación | `sendUpdates` no está en `none` | Inspeccionar nodo `GCal Fabian create` parámetros |
| Doble fila en `clz_event_assignment` para mismo uid | El `ON CONFLICT` no está actuando | Verificar que la PK existe: `\d clz_event_assignment` |

---

## Métricas a monitorear (primera semana en prod)

```sql
-- Distribución de assignment por día
SELECT date_trunc('day', created_at) AS dia,
       assigned_to,
       count(*) AS bookings
FROM clz_event_assignment
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY 1, 2
ORDER BY 1, 2;

-- Tasa de moves vs no-ops (cuántos realmente cambiaron calendar)
SELECT
  count(*) FILTER (WHERE assigned_to = 'fabian')  AS moves,
  count(*) FILTER (WHERE assigned_to = 'matias')  AS noops,
  round(100.0 * count(*) FILTER (WHERE assigned_to = 'fabian') / NULLIF(count(*), 0), 1) AS pct_fabian
FROM clz_event_assignment
WHERE created_at > NOW() - INTERVAL '7 days';

-- Si pct_fabian ≠ ~50%, hay sesgo (routing forzado o pausa activa)

-- Errores
SELECT cal_com_uid, raw_payload
FROM clz_event_assignment
WHERE status = 'error'
ORDER BY created_at DESC;
```

---

## Pendientes de v1.1 detectados en este testing

1. Label del response `Respond (move done)` dice `"created-matias"` — debería decir `"created-fabian-moved"`.
2. UPDATE atómico se ejecuta antes que el INSERT idempotente → reintentos avanzan el contador 2 veces.
3. Sin alerta cuando `getAll` no encuentra el evento de Matías.
4. Sin verificación de firma HMAC del webhook.
