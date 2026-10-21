# Round-Robin manual cal.com → Google Calendar (CLZ Collazo)

**Versión:** v1
**Workflow:** `03_workflows/collazo-round-robin-v1.json`
**Schema:** `05_crm/clz-round-robin-schema.sql`
**Testing:** `07_testing/testing-guide-round-robin-v1.md`
**Estado al 2026-06-10:** diseñado y listo para deploy. Bloqueantes operativos al final del doc.

> ## ⚠️ Leer antes que nada: `06_docs/diagnostico-round-robin-calcom-2026-08-05.md`
>
> El 2026-08-05 se verificó con datos la premisa del §1, que hasta entonces era una suposición. **Se confirmó: el round-robin nativo no reparte** — desde el 1° de mayo, 126 reservas reales y 0 asignadas a Fabián. Este diseño sigue siendo válido y su premisa central (*"todos los eventos caen en el calendar de Matías"*) se cumple en la práctica (241 de 249).
>
> Pero el diagnóstico cambió 3 cosas de este doc:
>
> 1. **Los slugs del §6 y del seed SQL estaban mal.** Eran los de los event types *personales*; los del team llevan "de" en el medio (`reparacion-de-calefon`, `instalacion-de-calefon`) y hay 2 que no existían. Ya corregido en `05_crm/clz-round-robin-schema.sql`.
> 2. **Hay un paso previo que no estaba acá:** sacar a Fabián como host de los 7 event types del team. Si no, cal.com y este workflow reparten en paralelo y se pisan. Costo medido: ~6% de disponibilidad (2 slots por semana).
> 3. **Queda una causa raíz abierta** que podría volver innecesario todo este workflow: verificar si Fabián tiene destination calendar en cal.com. Si no lo tiene, conectarlo podría hacer funcionar el round-robin nativo.
>
> No deployar sin leer ese doc.

---

## 1) Por qué existe esto

El round-robin nativo de cal.com no está funcionando en la cuenta de Collazo (**confirmado con datos el 2026-08-05** — ver el banner de arriba; en junio era una suposición sin verificar). Matías y Fabián son hermanos y cada uno tiene su propio Google Calendar; queremos que las visitas técnicas se repartan equitativamente entre los dos sin tener que esperar a que cal.com lo resuelva.

**Aproximación:** dejamos que cal.com siga creando los eventos como hasta hoy (todos en el calendar de Matías, que es la cuenta conectada) y reaccionamos al webhook `BOOKING_CREATED` para, en caso de que le toque a Fabián, mover el evento al calendar de él. Si le toca a Matías, no hacemos nada. También escuchamos `BOOKING_RESCHEDULED` y `BOOKING_CANCELLED` para no dejar zombies en el calendar de Fabián cuando el lead cancela o reagenda.

---

## 2) Decisiones de diseño (de la sesión 2026-06-10)

| # | Decisión | Por qué |
|---|----------|---------|
| 1 | **Webhook genérico** (no Cal.com Trigger nativo) configurado a mano en cal.com → Settings → Developer → Webhooks | El Trigger nativo registra el webhook automáticamente al activar el workflow, oculta la configuración y se duplica al re-importar. El manual queda inspeccionable en cal.com UI y es el patrón ya validado en CLZ con Chatrace. |
| 2 | **Routing por servicio** vía tabla `clz_event_type_routing` con valores `matias` / `fabian` / `round-robin` | Cliente confirmó que algunos servicios los hace solo uno. Mantenemos config en DB → un UPDATE manual cambia el routing sin tocar n8n ni el workflow. **Routing confirmado con Matías (2026-06-10):** 5 servicios en `round-robin` (instalación/reparación/mantenimiento/desmontaje de aire + instalación de calefón); 2 exclusivos de Matías (`servicio-electrico` + `reparacion-calefon`). |
| 3 | **Movimiento silencioso** (`sendUpdates=none` en delete + create de GCal) | El lead nunca ve nombres propios; siempre ve "Collazo Servicio Técnico". Decisión explícita del cliente para no exponer la lógica interna. |
| 4 | **v1 cubre los 3 eventos cal.com** (`BOOKING_CREATED` + `BOOKING_CANCELLED` + `BOOKING_RESCHEDULED`) | Sin los últimos dos, el calendar de Fabián queda con eventos zombies en cuanto el lead cancela o reagenda. El costo extra de implementación es bajo (~3 nodos por lane). |
| 5 | **UPDATE atómico con CASE** sobre `clz_round_robin_state` | Garantiza serialización de webhooks concurrentes en una sola query (`UPDATE … RETURNING`) sin race conditions. Idiomático Postgres. |
| 6 | **PK por `cal_com_uid`** en `clz_event_assignment` + `ON CONFLICT DO NOTHING` | Idempotencia ante reintentos de cal.com. Si llega el mismo webhook 2 veces, la 2° vez no duplica el move. |
| 7 | **Wait 5s** previo a la búsqueda del evento en Matías | El evento de cal.com puede tardar en sincronizar a Google Calendar. Sin la espera, `getAll` por `iCalUID` puede devolver 0 y el move falla. |
| 8 | **`continueOnFail` en GCal Matias delete** | Si el evento ya no está (por whatever razón), igual queremos crear el evento en Fabián. Es preferible "Matías tiene un hueco y Fabián tiene el evento" a "ninguno tiene nada". |
| 9 | **Calendar IDs hardcoded** en placeholders (`MATIAS_CALENDAR_ID_REPLACE` / `FABIAN_CALENDAR_ID_REPLACE`) | El plan free de n8n no soporta Variables UI; los IDs viven inline. Documentados en el sticky note del workflow. |
| 10 | **Sin Telegram alerting en v1** | Mantener el alcance acotado. Si en producción aparece el caso "evento no encontrado en Matías", se agrega en v1.1. |

---

## 3) Arquitectura del workflow

### Nodos por lane

```
[Webhook cal.com] ─┐
                   ▼
              [Parse Payload]
                   ▼
              [Switch by triggerEvent] ─────────┐
                   │                            │
   ┌───────────────┴──────────────┐      ┌──────┴────────┐
   ▼              ▼               ▼      ▼               ▼
CREATED      RESCHEDULED     CANCELLED  default → Respond (ignored)
```

#### Lane CREATED (`y ≈ 0`)
```
Get routing → Switch by routing
                  ├── matias       → Insert assignment (matias forced) → Respond (matias forced)
                  ├── fabian       → ┐                                          (MOVE flow, abajo)
                  ├── round-robin  → Asignar RR atómico → IF assigned_to=fabian
                  │                                          ├── TRUE  → ┘
                  │                                          └── FALSE → Insert assignment (matias RR) → Respond (matias RR)
                  └── default      → Asignar RR atómico (fallback al RR si la tabla no tiene el slug)
```

MOVE flow (compartido por `Switch:fabian` y `IF:TRUE`):
```
Insert assignment (fabian) → Wait 5s → GCal Matias getAll → IF evento encontrado?
                                                              ├── TRUE  → GCal Matias delete → GCal Fabian create
                                                              └── FALSE                       → GCal Fabian create
                                                                                                     ▼
                                                                                              Update mapping → Respond (move done)
```

#### Lane RESCHEDULED (`y ≈ 700`)
```
Lookup booking (RESCHEDULED) → IF estaba en Fabián?
                                  ├── TRUE  → GCal Fabian update → Update DB (rescheduled) → Respond (rescheduled fabian)
                                  └── FALSE → Respond (rescheduled noop)
```
- El lookup matchea por `cal_com_uid IN ($uid, $rescheduleUid)` porque cal.com **cambia el uid** cuando se reagenda. El SQL `UPDATE` después escribe el nuevo uid en la fila.

#### Lane CANCELLED (`y ≈ 1100`)
```
Lookup booking (CANCELLED) → IF estaba en Fabián? (cancel)
                                ├── TRUE  → GCal Fabian delete → Update DB (cancelled fabian) → Respond (cancelled fabian)
                                └── FALSE → Update DB (cancelled matias) → Respond (cancelled matias)
```
- Cuando el booking estaba en Matías, cal.com ya borró el evento del calendar de Matías solo. Solo marcamos el row como cancelled.

---

## 4) Tablas Postgres

Ver `05_crm/clz-round-robin-schema.sql` para DDL completo. Resumen:

| Tabla | Filas esperadas | Propósito |
|-------|-----------------|-----------|
| `clz_round_robin_state` | 1 (singleton, id=1) | Estado del round-robin: `last_assigned`, `total_count`, `matias_paused`, `fabian_paused` |
| `clz_event_type_routing` | 7 (uno por event-type) | Override por servicio: `matias` / `fabian` / `round-robin` |
| `clz_event_assignment` | 1 por booking | Mapping `cal_com_uid` ↔ `gcal_event_id_matias` + `gcal_event_id_fabian`; status; raw_payload |

Queries operativas habituales viven al final del archivo SQL como comentarios.

---

## 5) Payload esperado de cal.com (referencia)

`BOOKING_CREATED`:
```json
{
  "triggerEvent": "BOOKING_CREATED",
  "payload": {
    "uid": "abc123-xyz",
    "bookingId": 9876,
    "iCalUID": "abc123-xyz@cal.com",
    "type": "instalacion-aire",
    "title": "Instalación Aire entre Juan Pérez y Collazo",
    "description": "Notas del lead…",
    "startTime": "2026-06-12T14:00:00Z",
    "endTime":   "2026-06-12T15:00:00Z",
    "organizer": { "email": "matias@collazo.uy", "timeZone": "America/Montevideo" },
    "attendees": [
      { "email": "juanp@gmail.com", "name": "Juan Pérez", "timeZone": "America/Montevideo" }
    ],
    "location": "Av. Italia 1234, Montevideo",
    "eventTypeId": 123,
    "eventType": { "slug": "instalacion-aire", "title": "Instalación Aire" },
    "responses": { "phone": "+598 99 999 999" },
    "metadata": {}
  }
}
```

`BOOKING_RESCHEDULED` incluye `payload.rescheduleUid` (uid viejo) además del nuevo `payload.uid`.
`BOOKING_CANCELLED` incluye `payload.uid` y `payload.cancellationReason`.

Fixtures completos en `07_testing/fixtures/`.

---

## 6) Setup paso a paso (orden estricto)

### Pre-flight — destrabar con el cliente

1. **Calendar IDs.** Pedirle a Matías el ID de su calendar y el de Fabián (formato `email@gmail.com` para el primary, `c_xxxxxxxxx@group.calendar.google.com` para uno secundario).
2. **OAuth.** Coordinar una sesión de 15 min con cada hermano para autenticar la cuenta en n8n → Credentials → New → Google Calendar OAuth2. Una credencial por hermano.
3. ~~**Plan cal.com.**~~ **Resuelto 2026-08-05:** la cuenta tiene un team (`collazo-servicio`, id `256131`), o sea plan pago → **webhook global**, no hace falta uno por event-type.
4. **Destination calendar de cal.com.** Confirmar en cal.com → Settings → Apps → Conferencing/Destination que el "destination calendar" es el de Matías y no uno compartido. Si es compartido, este diseño no aplica y hay que rediseñar. **Además (2026-08-05): verificar el destination calendar de FABIÁN** — es la hipótesis principal de por qué el RR nativo nunca le asigna, y si resolverlo lo arregla, este workflow no hace falta.
5. ~~**Routing por servicio.**~~ **Resuelto 2026-06-10 y verificado contra cal.com 2026-08-05:** `reparacion-de-calefon` + `servicio-electrico` solo Matías; los otros 7 round-robin. La config de hosts del team ya replica exactamente esta regla.
6. **Sacar a Fabián como host** de los 7 event types del team (dejarlos con host fijo = Matías). Sin esto, cal.com reparte por su cuenta y compite con este workflow. Costo medido: ~6% de disponibilidad. Paso nuevo, no estaba en el diseño de junio.

### Fase 1 — Backend

6. Ejecutar `05_crm/clz-round-robin-schema.sql` en Postgres Collazo desde Supabase Studio o psql.
   ```sql
   \i /Users/camilo/Downloads/camilo-workspace/clients/CLZ_Collazo/05_crm/clz-round-robin-schema.sql
   ```
   Verificar:
   ```sql
   SELECT * FROM clz_round_robin_state;       -- 1 fila, last_assigned='fabian'
   SELECT count(*) FROM clz_event_type_routing; -- 7
   ```
7. Crear las 2 credenciales en n8n UI:
   - Nombre: `Google Calendar | Collazo Matías` — OAuth de Matías.
   - Nombre: `Google Calendar | Collazo Fabián` — OAuth de Fabián.
8. Importar `03_workflows/collazo-round-robin-v1.json` en n8n. Dejar el workflow en `active: false`.
9. En cada nodo Google Calendar del workflow:
   - **GCal Matias getAll**, **GCal Matias delete** → asociar credencial `Google Calendar | Collazo Matías`. Reemplazar `MATIAS_CALENDAR_ID_REPLACE` por el ID real.
   - **GCal Fabian create**, **GCal Fabian update**, **GCal Fabian delete** → asociar credencial `Google Calendar | Collazo Fabián`. Reemplazar `FABIAN_CALENDAR_ID_REPLACE` por el ID real.
10. Verificar que todos los nodos Postgres usan la credencial `Collazo` (id `HRV9xsfYlr934XEB`) — vienen así por default pero conviene revisar uno por uno.

### Fase 2 — Configurar cal.com

11. Generar un HMAC secret aleatorio (`openssl rand -hex 32`).
12. En cal.com → Settings → Developer → Webhooks (o si es Free: por cada event-type → Webhooks):
    - URL: `https://[TU-INSTANCIA-N8N]/webhook/clz-calcom`
    - Subscriptions: `BOOKING_CREATED`, `BOOKING_RESCHEDULED`, `BOOKING_CANCELLED`
    - Secret: pegar el HMAC generado
13. Si plan cal.com es Free, repetir el paso 12 para cada uno de los 7 event-types listados en el system prompt v1.5 del agente Collazo.

### Fase 3 — Smoke test

14. Crear booking de prueba en cal.com con tu cuenta personal como lead. Esperar 5s y verificar:
    - Webhook llega a n8n (Executions con status `Success` y 200 OK).
    - Fila nueva en `clz_event_assignment`.
    - `clz_round_robin_state.last_assigned` cambió al hermano correspondiente.
    - Si tocó Fabián: evento desaparece de su calendar y aparece en el de Fabián con horarios idénticos.
15. Reagendar la cita en cal.com → verificar lane B-flow.
16. Cancelar → verificar lane C-flow.
17. Ejecutar la suite completa en `07_testing/testing-guide-round-robin-v1.md`.

### Fase 4 — Activación

18. Activar el workflow.
19. Monitorear primeros 5 bookings reales. Si todo OK, dejar correr.
20. Correr `/cliente-sync` en este workspace para que CLAUDE.md + contexto queden actualizados.

---

## 7) Operación día a día

### Pausar a un hermano (vacaciones)

```sql
UPDATE clz_round_robin_state SET matias_paused = TRUE  WHERE id = 1;  -- pausar Matías
UPDATE clz_round_robin_state SET matias_paused = FALSE WHERE id = 1;  -- reanudar
```
Mientras un hermano está pausado, todos los nuevos bookings van al otro.

### Cambiar routing de un servicio

```sql
UPDATE clz_event_type_routing
SET target = 'fabian'
WHERE event_type_slug = 'servicio-electrico';
```
El cambio toma efecto desde el siguiente booking. No se reasignan bookings pasados.

### Ver estado actual

```sql
SELECT * FROM clz_round_robin_state;
SELECT event_type_slug, target FROM clz_event_type_routing;
SELECT assigned_to, COUNT(*) FROM clz_event_assignment
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY assigned_to;
```

---

## 8) Riesgos conocidos y mitigaciones

| Riesgo | Mitigación |
|--------|-----------|
| Lag de cal.com → Google Calendar (webhook llega antes que el evento aparezca) | `Wait 5s` previo al getAll. Si igual no aparece, `continueOnFail` en delete + create en Fabián crea el evento "huérfano" (Matías queda con un hueco). |
| Webhook reintentado por cal.com | `cal_com_uid` PK + `ON CONFLICT DO NOTHING` en los inserts. Reintento es idempotente. |
| RESCHEDULE cambia el `uid` | Lookup busca por `uid OR rescheduleUid`. UPDATE escribe el nuevo uid en la fila. |
| Ambos hermanos pausados | El UPDATE no alterna → mantiene el último asignado. **Nota:** no hay alerta automática; queda como TODO de v1.1 si pasa en producción. |
| HMAC secret expuesto | Vive en credencial Header Auth de n8n, no inline en el JSON del workflow. |
| OAuth de Google Calendar expira | n8n refresca automáticamente. Si falla, ejecución da error → cal.com reintenta. |
| Multi-attendee (cal.com Group booking) | Tomamos el primer attendee no-organizer. Todo el payload queda en `raw_payload` para forensics. |
| Mismatch routing vs estado real | Si Matías dice "el de electricidad es solo mío" después de un booking de un mes que ya fue a Fabián, no se reasigna. Aplica desde el siguiente. |

---

## 9) Pendientes operativos (post-implementación)

1. ~~Conseguir de Matías el mapping definitivo event-type → técnico.~~ **Resuelto 2026-06-10:** `reparacion-calefon` + `servicio-electrico` → solo Matías; los otros 5 → round-robin.
2. **v1.1 candidates:** alerta Telegram cuando `getAll` no encuentra el evento de Matías; panel admin (skill Telegram `/pausar matias`, `/estado collazo`); ponderación por días trabajados; webhook de cal.com con HMAC verificado (n8n Webhook node soporta Header Auth).
3. Monitorear delivery de webhooks en cal.com → Settings → Developer → Webhooks → Delivery history durante la primer semana.

---

## 10) Patrones del workspace reusados

| Patrón | Fuente | Aplicación aquí |
|--------|--------|-----------------|
| `n8n-nodes-base.googleCalendar` v1.3 create/delete | `clients/TFO_TOFO/03_workflows/chequear-disponibilidad-tofo-v2.json` | Todos los nodos GCal (create / delete / update / getAll) |
| Postgres `UPDATE … RETURNING` atómico con CASE | `clients/SYS_SistemasYSoluciones/06_docs/supabase-schema.sql` (función `upsert_session_state`) | `Asignar RR atómico` |
| Webhook genérico + Respond to Webhook | `clients/CLZ_Collazo/03_workflows/agente-collazo-main.json` (Chatrace) | `Webhook cal.com` + los 8 Respond nodes |
| `queryReplacement` con array + `$('Node').item.json.X` | `_core/standards/n8n-data-references.md` | Todos los Postgres nodes |
| Switch con `outputKey` nombrado + fallback | `clients/TFO_TOFO/03_workflows/chequear-disponibilidad-tofo-v2.json` | `Switch by triggerEvent` + `Switch by routing` |
