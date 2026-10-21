# Diagnóstico: ¿el round-robin nativo de cal.com reparte o no? (CLZ Collazo)

**Fecha:** 2026-08-05
**Disparador:** antes de deployar `collazo-round-robin-v1.json` (35 nodos + 3 tablas Postgres), verificar que la premisa de junio siga siendo cierta.
**Método:** lectura por API v2 de cal.com — 249 bookings de los últimos 180 días, config de los 9 event types del team, y medición de slots disponibles.
**Veredicto:** el round-robin nativo **no reparte**. El workflow de n8n tiene razón de ser. Queda una causa raíz sin confirmar que, si se resuelve, lo haría innecesario.

---

## 1. Por qué se revisó

El diseño de junio (`round-robin-design.md`) arranca con: *"El round-robin nativo de cal.com no está funcionando en la cuenta de Collazo (causa desconocida — no la vamos a debuggear)"*.

Esa premisa nunca se verificó con datos. Y desde entonces cambiaron dos cosas:

- Se crearon **9 event types de team** (`cal.com/team/collazo-servicio/…`, team id `256131`) y el bot entrega esos links, no los personales.
- El 2026-08-04 Matías reportó un error de reserva (`400 — "El tipo de reunión no se puede reservar en este momento"`), sugiriendo que algo del lado de cal.com no estaba sano.

Deployar 35 nodos sobre una premisa sin verificar era el riesgo que motivó este diagnóstico.

---

## 2. Configuración actual en cal.com

Los **9 event types del team están en `schedulingType: roundRobin`**, y la asignación de hosts ya replica exactamente la regla de negocio que Matías dio en junio:

| Event type | Hosts | Coincide con la regla |
|---|---|---|
| `servicio-electrico` | solo Matías | ✅ |
| `reparacion-de-calefon` | solo Matías | ✅ |
| `instalacion-aire` | Matías + Fabián | ✅ |
| `reparacion-aire-acondicionado` | Matías + Fabián | ✅ |
| `mantenimiento-aire-acondicionado` | Matías + Fabián | ✅ |
| `desmontaje-aire-acondicionado` | Matías + Fabián | ✅ |
| `instalacion-de-calefon` | Matías + Fabián | ✅ |
| `desmontaje-de-calefon` | Matías + Fabián | ✅ |
| `desmontaje-instalacion-de-calefon` | Matías + Fabián | ✅ |

**Los dos hosts tienen `priority: medium`** — o sea, ninguno está despriorizado por config.

`instalacion-de-calefon` es el único con `assignAllTeamMembers: true`; los otros 8 tienen los hosts asignados explícitamente. Diferencia menor, sin impacto conocido.

Miembros del team: Matías (`collazoservicio4@gmail.com`) y Fabián (`fabiancollazo15@gmail.com`), ambos **Owner y aceptados**. La membresía no es el problema.

---

## 3. El reparto real (el dato que decide)

249 bookings, 2026-02-07 → 2026-08-07:

| | Reservas | % |
|---|---|---|
| Matías | 241 | 96,8% |
| Fabián | 8 | 3,2% |

Desglose mensual por fecha de creación:

```
2026-02:  45 reservas  →  Fabián  0
2026-03:  38           →  Fabián  0
2026-04:  40           →  Fabián  8   ← ver abajo
2026-05:  63           →  Fabián  0
2026-06:  30           →  Fabián  0
2026-07:  27           →  Fabián  0
2026-08:   6           →  Fabián  0
```

**Las 8 de Fabián son pruebas de setup, no reservas reales:** todas creadas entre el 29 y el 30 de abril, **todas canceladas**, varias con fecha de visita el mismo día de creación. Coinciden exactamente con la última actividad registrada de Fabián en cal.com (29/4/2026).

> **Desde el 1° de mayo: 126 reservas reales, 0 asignadas a Fabián.**

Con priority igual y siendo host de 7 event types, el round-robin debería haberle dado ~la mitad. No le dio ninguna.

---

## 4. Fabián sí tiene disponibilidad configurada

Comparación limpia entre dos event types del **mismo rubro** (para no confundir duraciones ni schedules distintos), ventana de 7 días:

| Event type | Hosts | Slots totales |
|---|---|---|
| `reparacion-de-calefon` | solo Matías | 34 |
| `desmontaje-de-calefon` | Matías + Fabián | 36 |

Día por día son **idénticos salvo el 2026-08-06** (4 vs 6). La lectura: la agenda de Matías ya satura el día (máximo 6 slots de 1h30 en la ventana horaria), así que Fabián solo aporta cuando Matías está ocupado.

**Conclusión:** Fabián tiene un schedule configurado en cal.com y su disponibilidad se computa. El problema no es que sea invisible para cal.com — es que nunca lo elige.

> ⚠️ Una comparación previa entre `instalacion-aire` (ambos) y `reparacion-de-calefon` (solo Matías) dio 6 vs 4 slots en un día y llevó a concluir erróneamente que Fabián aportaba mucha disponibilidad. Esa comparación era inválida: son event types distintos, con posible config distinta. La comparación válida es la de arriba, entre los dos de calefón.

---

## 5. Costo de sacar a Fabián como host

Si se decide volver determinístico el reparto (host fijo = Matías) para que cal.com y n8n no compitan, la disponibilidad que se pierde es **2 slots por semana sobre 36 (~6%)**, concentrados en los días en que Matías está ocupado.

Es un costo bajo y medido. La estimación inicial de "un tercio de la disponibilidad" salía de la comparación inválida del §4 y era incorrecta.

---

## 6. Mismatch de slugs — bug latente en la tabla de routing

`clz_event_type_routing` se sembró en junio con los slugs de los **event types personales**. Los del team llevan "de" en el medio:

| Seed original | Slug real del team | Efecto si se deploya sin corregir |
|---|---|---|
| `reparacion-calefon` | `reparacion-de-calefon` | 🔴 no matchea → cae al default `round-robin` → **iría a Fabián la mitad de las veces cuando debe ser solo de Matías** |
| `instalacion-calefon` | `instalacion-de-calefon` | 🟡 no matchea → default `round-robin` → coincide por casualidad con lo correcto |
| *(ausente)* | `desmontaje-de-calefon` | 🟡 default `round-robin` → correcto por casualidad |
| *(ausente)* | `desmontaje-instalacion-de-calefon` | 🟡 default `round-robin` → correcto por casualidad |

Los otros 5 slugs sí coinciden.

**Corregido en `05_crm/clz-round-robin-schema.sql` el 2026-08-05** (el schema todavía no se había corrido, así que se arregló el seed en vez de agregar una migración).

Nota: los bookings históricos muestran **ambas familias de slugs** (`reparacion-calefon` n=27 y `reparacion-de-calefon`), porque durante meses las reservas entraron por los event types personales y desde el 2026-08-05 entran por los del team.

---

## 7. La premisa del diseño se sostiene

El workflow asume: *"cal.com crea todos los eventos en el calendar de Matías; nosotros movemos al de Fabián los que corresponda"*.

Empíricamente **241 de 249 (96,8%) cayeron en Matías**, y los 8 restantes fueron tests cancelados. La arquitectura sirve tal cual — no hay que rediseñarla, solo corregir los slugs.

⚠️ Con la salvedad de que si cal.com alguna vez empieza a asignarle a Fabián, las dos lógicas se pisarían. Por eso conviene sacarlo como host antes de activar el workflow (§5).

---

## 8. Causa raíz abierta

Falta explicar **por qué** cal.com nunca le asigna, teniendo priority igual y disponibilidad configurada.

**Hipótesis principal: Fabián no tiene destination calendar en cal.com.** Eso explicaría el patrón completo — cal.com le lee la agenda (por eso aporta los 2 slots del §4) pero no puede crearle eventos, así que lo saltea al momento de asignar.

**Cómo verificarlo:** entrar a cal.com con la cuenta de Fabián → **Settings → Calendars** → ver si hay un calendario conectado y cuál figura como destination.

**Por qué importa:** si es eso, se arregla con un clic y el round-robin nativo empieza a funcionar. Se evitaría deployar y mantener 35 nodos + 3 tablas + un webhook. Es la misma conversación que hay que tener con Fabián por el 2FA del OAuth de n8n, así que no agrega fricción.

Hipótesis secundarias, no exploradas: schedule de Fabián con muy poca superposición real con el horario comercial; bug del algoritmo de RR de cal.com en esta cuenta.

---

## 9. Decisión pendiente

```
┌─ Fabián NO tiene destination calendar
│    → conectarlo, monitorear 2 semanas
│    → si el reparto arranca: ARCHIVAR el workflow de n8n
│
└─ Fabián SÍ lo tiene (o conectarlo no cambia nada)
     → seguir con el deploy de n8n:
        1. sacar a Fabián como host de los 7 event types (costo: ~6% de slots)
        2. correr el schema SQL (ya con los slugs corregidos)
        3. Calendar IDs + 2 credenciales OAuth
        4. importar workflow + reemplazar placeholders
        5. webhook en cal.com + smoke tests C1-C11
```

El error 400 que reportó Matías el 2026-08-04 **queda sin explicar** por este diagnóstico. No se reprodujo. Si vuelve a aparecer, capturar el `ID de referencia de rastreo` que muestra la pantalla y revisar contra el soporte de cal.com.

---

## Apéndice — comandos y gotchas

Las credenciales viven en `.env` (gitignored): `CLZ_CALCOM_API_KEY`, `CLZ_CALCOM_TEAM_ID`, `CLZ_CALCOM_TEAM_SLUG`.

**Gotcha 1 — Cloudflare bloquea el User-Agent de Python.** `urllib` manda `Python-urllib/3.x` y la API devuelve `403 error code: 1010` (que es de Cloudflare, no de cal.com). Hay que mandar un UA normal:

```python
headers={"Authorization": f"Bearer {KEY}", "cal-api-version": "...", "User-Agent": "curl/8.7.1"}
```

**Gotcha 2 — `skip` / `page` / `cursor` no funcionan en esta cuenta.** Ya estaba documentado en `03_workflows/clz-recuperar-contactos-calcom-v1.json`. La paginación se hace por fecha: pedir con `afterStart` + `sortStart=asc` y usar como cursor el `start` más alto del batch + 1 ms.

**Versiones de API por endpoint** (header `cal-api-version`):

| Endpoint | Versión |
|---|---|
| `/v2/bookings` | `2024-08-13` |
| `/v2/teams/{id}/event-types` | `2024-06-14` |
| `/v2/slots` | `2024-09-04` |

```bash
# reparto por host (últimos N bookings)
curl -s -H "Authorization: Bearer $CLZ_CALCOM_API_KEY" -H "cal-api-version: 2024-08-13" \
  "https://api.cal.com/v2/bookings?take=100&sortStart=desc"

# config y hosts de los event types del team
curl -s -H "Authorization: Bearer $CLZ_CALCOM_API_KEY" -H "cal-api-version: 2024-06-14" \
  "https://api.cal.com/v2/teams/$CLZ_CALCOM_TEAM_ID/event-types"

# disponibilidad de un event type
curl -s -H "Authorization: Bearer $CLZ_CALCOM_API_KEY" -H "cal-api-version: 2024-09-04" \
  "https://api.cal.com/v2/slots?eventTypeSlug=desmontaje-de-calefon&teamSlug=$CLZ_CALCOM_TEAM_SLUG&start=2026-08-06&end=2026-08-13&timeZone=America/Montevideo"
```
