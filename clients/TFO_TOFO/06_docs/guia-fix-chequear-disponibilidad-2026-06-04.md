# Guía: fix sub-workflow `Chequear disponibilidad | Tofo`

**Fecha:** 2026-06-04
**Workflow vivo (v1):** `vpLmZ299yXJrOSBv` — `Chequear disponibilidad | Tofo`
**Snapshot pre-fix:** [`chequear-disponibilidad-tofo-prod-snapshot-2026-06-04.json`](../03_workflows/chequear-disponibilidad-tofo-prod-snapshot-2026-06-04.json)
**Workflow v2 (nuevo):** [`chequear-disponibilidad-tofo-v2.json`](../03_workflows/chequear-disponibilidad-tofo-v2.json) — listo para importar

---

## 1. Bugs detectados en el v1

| # | Bug | Impacto |
|---|-----|---------|
| B1.1 | `timeMin: T00:00:00` y `timeMax: T23:59:00` sin offset CDMX | Drift potencial: si el server n8n está en UTC, busca el día equivocado |
| B1.2 | Nodo `Crear mensaje` (gpt-4.1-mini) evalúa solapamiento con LLM | No determinista, costoso por cita, propenso a alucinación |
| B1.3 | Prompt LLM tiene 3 reglas contradictorias sobre la ventana laboral (10–13, 10–12, último bloque 12–13) | El LLM puede aceptar/rechazar inconsistentemente |
| B1.4 | Sin validación de día de semana (Lun–Vie) | Permite agendar sábados/domingos |
| B1.5 | Sin validación de fecha pasada | Permite agendar para "ayer" |
| B1.6 | Sin validación de minutos redondos | Permite agendar 11:30 |
| B1.7 | Evento `Crear evento` no especifica `timeZone` | Google Calendar puede crear en TZ del calendario o UTC según versión API |
| B1.8 | `Disponible` y `No disponible` devuelven solo `{mensaje}` plano | El AI Agent no recibe shape estable para decisión post-agendamiento |
| B1.9 | `summary` del evento no incluye canal / subscriber_id / teléfono | Cuando Mauricio ve el evento en su calendar, no sabe por dónde vino el lead ni cómo contactarlo si el agente lo derivó mal |
| B1.10 | No hay patrón Napier (`fecha_contexto`) en el main workflow | El AI Agent calcula fechas relativas por su cuenta con riesgo de drift |

---

## 2. Patrón aplicado en el v2

- **Cero LLM** — toda la lógica (validación + solapamiento + alternativas) es JS determinista usando Luxon (built-in en n8n Code node).
- **TZ explícito** — todos los parseos y comparaciones usan `zone: 'America/Mexico_City'`. El evento se crea con `timeZone: 'America/Mexico_City'`.
- **Ventana laboral única** — inicios válidos `{10, 11, 12}` minutos `== 0`, Lun–Vie, último bloque 12:00–13:00. Fuente: prompt B2B v1.3 línea 336.
- **Retorno estructurado** — 3 ramas devuelven JSON con shape estable que el AI Agent puede parsear: `{libre: bool, motivo, mensaje, alternativas}` + en caso libre `{evento_id, fecha, fecha_humana}`.
- **Patrón Napier complementario** — el main workflow expone `fecha_contexto` al AI Agent (ver [guia-fix-fecha-contexto-main-2026-06-04.md](guia-fix-fecha-contexto-main-2026-06-04.md)).

---

## 3. Pasos para aplicar

### Paso 1 — Snapshot del v1 (ya hecho)
Snapshot en repo: [`chequear-disponibilidad-tofo-prod-snapshot-2026-06-04.json`](../03_workflows/chequear-disponibilidad-tofo-prod-snapshot-2026-06-04.json). El workflow vivo `vpLmZ299yXJrOSBv` queda intacto hasta el Paso 5.

### Paso 2 — Importar v2 a n8n
1. En n8n: **Workflows → Import from File** → seleccionar `chequear-disponibilidad-tofo-v2.json`.
2. n8n asigna un `workflowId` nuevo (algo como `xY99abc123...`). **Anotarlo** — se usa en el Paso 5.
3. Verificar que los 10 nodos importaron sin warnings rojos.
4. **No activar todavía.**

### Paso 3 — Conectar credenciales
- En `Get availability in a calendar` y `Crear evento`, verificar que `credentials.googleCalendarOAuth2Api` apunte a la cuenta de Mauricio (`mauriciogarciadelav@gmail.com`). El JSON ya viene pre-cableado al credential id `z0IngCgigP1wgAux` (el mismo que usa el v1), pero confirmá visualmente.
- El v2 **NO usa OpenAI** — eliminar cualquier credential OpenAI que el import haya creado por reflejo.

### Paso 4 — Aplicar guía del nodo `Fechas` al main workflow
Seguir [`guia-fix-fecha-contexto-main-2026-06-04.md`](guia-fix-fecha-contexto-main-2026-06-04.md) (5 edits sobre `Agente WEB B2B y RRSS`):
- Edit 1: agregar nodo `Fechas` entre `Juntar mensajes` y `Agente de derivacion de Lead`.
- Edit 2: reemplazar el User Message del `Agente de derivacion de Lead` (cambiar `Fecha de hoy: {{ $now }}` por el bloque `# Contexto temporal`).
- Edit 3: agregar bloque `# Contexto temporal` al campo `text` del subagente `Agente de B2B`.
- Edit 4: cablear los 3 inputs nuevos (`subscriber_id`, `canal`, `telefono`) al `toolWorkflow check_disponibilidad`, reusando `Code in JavaScript` para `canal`.
- Edit 5: cambiar el `workflowId.value` del `check_disponibilidad` al ID del v2 (Paso 2 de este doc).

⚠ **Nota:** en el JSON vivo el `cachedResultName` del `check_disponibilidad` ya dice `Chequear disponibilidad | Tofo v2`, pero el `value` sigue siendo `vpLmZ299yXJrOSBv` (id del v1). El toolWorkflow ejecuta lo que dice el `value`, NO el label. Verificar después del Paso 5 que el `value` quedó con el ID nuevo.

### Paso 6 — Activar v2, probar, desactivar v1
1. Activar el v2 en su pestaña de workflow.
2. Correr los 8 tests de la sección 4 (abajo) con pin data del trigger.
3. Si los 8 pasan: hacer smoke E2E (sección 5).
4. Si el smoke E2E pasa: desactivar el v1 (`vpLmZ299yXJrOSBv`). **No borrarlo** — mantenerlo desactivado por 1 semana como rollback.
5. Pasada la semana sin issues: borrar v1.

---

## 4. Plan de testing (pin data en el trigger del v2)

Calcular fechas en base al día actual (ejemplo del 2026-06-04 jueves; próximo lunes = 2026-06-08).

| # | Pin data en `When Executed by Another Workflow` | Resultado esperado | Verifica |
|---|---|---|---|
| 1 | `{"fecha_hora":"2026-06-03T11:00:00-06:00","nombre":"X"}` (ayer) | `{valid:false, motivo:"fecha_pasada", ...}` por nodo `Respond NO VÁLIDO` | B1.5 |
| 2 | `{"fecha_hora":"2026-06-06T11:00:00-06:00","nombre":"X"}` (sábado) | `{motivo:"no_laboral", ...}` | B1.4 |
| 3 | `{"fecha_hora":"2026-06-08T09:00:00-06:00","nombre":"X"}` (lun 9am) | `{motivo:"fuera_ventana", ...}` | B1.3 |
| 4 | `{"fecha_hora":"2026-06-08T13:00:00-06:00","nombre":"X"}` (lun 1pm) | `{motivo:"fuera_ventana", ...}` | B1.3 |
| 5 | `{"fecha_hora":"2026-06-08T11:30:00-06:00","nombre":"X"}` | `{motivo:"minutos_no_redondos", ...}` | B1.6 |
| 6 | `{"fecha_hora":"2026-06-08T11:00:00-06:00","nombre":"Test"}` con calendario VACÍO | `{libre:true, evento_id:"...", fecha_humana:"lunes 8 de junio a las 11:00"}` + evento creado en CDMX 11:00 | B1.1, B1.7, B1.8 |
| 7 | Mismo que #6 pero con 11:00-12:00 ya ocupado en el calendar | `{libre:false, motivo:"ocupado", alternativas:["10:00","12:00"]}` | B1.2 (solapamiento determinista) |
| 8 | Pin actual del v2 (`2026-06-08T13:00:00-06:00`, "Bally Hoo") | Mismo que test #4 | regression del pin del v1 |

**Cómo correr:**
1. Editar el `pinData` del trigger en n8n con cada caso.
2. Click `Execute Workflow`.
3. Inspeccionar el output del último nodo de cada rama (`Respond LIBRE` / `Respond OCUPADO` / `Respond NO VÁLIDO`).

**Para el test 6**, además de la respuesta:
- Abrir Google Calendar de Mauricio.
- Verificar que el evento aparezca en `lunes 8 de junio 11:00 hora México` (NO 17:00 ni 5:00 ni otro día).
- Verificar que el summary diga `Reunión TOFO con Test (canal_X)` y que la description tenga teléfono + subscriber_id + canal.

**Para el test 7**, antes de ejecutar:
- Crear manualmente en Google Calendar de Mauricio un evento `lunes 8 de junio 11:00-12:00` con cualquier título.
- Después de ejecutar y validar, borrar ese evento.

---

## 5. Smoke E2E (después de los 8 tests OK)

Disparar el flujo completo desde un ManyChat de prueba o desde el AI Agent en modo testing:

1. Lead simulado: "Hola, quiero agendar una llamada con Mauricio el próximo martes a las 11."
2. El agente B2B debería:
   - Pedir WhatsApp si viene de IG/FB/TT (o saltar si ya está en WPP).
   - Calcular `2026-06-09T11:00:00-06:00` usando `fecha_contexto` del User Message.
   - Llamar `check_disponibilidad` con esos inputs.
   - Recibir `{libre: true, ...}`.
   - Activar `elevar_conversacion` con `tipo='b2b'` (interno).
   - Responder al lead confirmando la cita (sin mencionar la elevación).
3. Verificar en el log de n8n: el sub-workflow se ejecutó, el evento aparece en Google Calendar de Mauricio, el flow `content20260526142445_613819` se disparó en ManyChat.

---

## 6. Rollback

Si algo falla en producción:
1. En el main workflow, nodo `check_disponibilidad`, restaurar `workflowId.value` a `vpLmZ299yXJrOSBv`.
2. Reactivar el v1 (sigue desactivado pero no eliminado).
3. Documentar el fallo en una nota para iteración.

---

## 7. Pendientes post-fix (próximo turno)

- **Bump prompt B2B a v1.4** con:
  - Mención explícita de la ventana laboral única (Lun–Vie 10/11/12 hora México).
  - Instrucción de leer `fecha_contexto` del User Message como fuente de verdad.
  - Manejo del shape estable del retorno: cómo reaccionar a `{libre:false, motivo, alternativas}` (proponer alternativas), `{libre:false, motivo:"fecha_pasada"}` (pedir nueva fecha), etc.
- **Verificar que `elevar_conversacion` no se dispara si la cita falló** — el prompt B2B vigente dice "Siempre antes de mandar el mensaje de confirmación de la cita, guardar 'b2b' + activar elevar_conversacion". Hoy el agente puede activar la elevación aunque el sub-workflow devuelva `{libre:false}`. Refinamiento del prompt v1.4: solo activar `elevar_conversacion` si `libre==true`.
- **Copy-paste prompt B2B v1.4 al Google Doc vivo** + snippet del nodo Fechas al main workflow en n8n.
