# Zoom Credencial Fix — TOFO B2B Sub-workflow `chequear-disponibilidad-tofo-v3`

**Prioridad:** P0 (bloqueante para cierre del feedback Mauricio 18/6/26)
**Fecha:** 2026-06-19 · **Update:** 2026-06-21 PM (confirmado real post-cirugía tools rogue)
**Status:** `CONFIRMADO_BUG_REAL` — `ESPERANDO_CREDENCIALES_MAURICIO`

> **Update 2026-06-21 PM** — post-cirugía de tools rogue del Agente de B2B (ver `incidente-calendar-overlaps-2026-06-21.md`), el smoke test ejecutado por la agencia confirmó: con el agente forzado a invocar `check_disponibilidad`, el evento Calendar se crea OK ✅ pero el output del nodo `Crear meeting Zoom` del sub-workflow es `[{}]` — fallback silencioso de `continueOnFail: true`. El bug Zoom **es real e independiente** del bug de tools rogue. La hipótesis "tool rogue era la causa única" queda descartada. Este plan de migración OAuth queda vigente y bloqueante.

---
**Owner técnico:** la agencia · **Decisor/cuenta:** Mauricio García de la Vega (mauriciogarciadelav@gmail.com)
**Cliente:** TFO_TOFO
**Workflow afectado:** `clients/TFO_TOFO/03_workflows/chequear-disponibilidad-tofo-v3.json` (id n8n `vpLmZ299yXJrOSBv`)

---

## 1. Síntoma reportado

Mauricio reportó el problema en la reunión del **18/6/26** (28 min). Cita textual:

> "No está haciendo las citas en Zoom aún. Les dice al cliente que le hizo la cita en Zoom, pero no la hace."

Lectura operativa:
- El agente confirma al lead que la cita quedó agendada con link de Zoom.
- El evento de Google Calendar **sí se crea** correctamente y Mauricio lo ve en su calendar.
- La meeting de Zoom **no aparece** en el dashboard de Zoom de Mauricio (`zoom.us/meeting`).
- Resultado: el lead recibe un `join_url` que apunta a una meeting que Mauricio no controla y no ve, generando fricción real el día de la cita.

Mauricio explícitamente pidió cerrar este punto antes de cualquier otro deploy.

---

## 2. Estado actual del sub-workflow `chequear-disponibilidad-tofo-v3`

- Nodo **`Crear meeting Zoom`** ya está creado e integrado al flujo entre el switch `LIBRE` y `Crear evento`.
- Está cableado con la credencial `zoomOAuth2Api` id **`TllmBz0re6WGmTw2`** (label `"Zoom account"`).
- Configuración del nodo: `meeting.create`, duración 30 min, `waitingRoom=true`, `muteUponEntry=true`, `joinBeforeHost=false`, `type=2` (scheduled), `timezone=America/Mexico_City`, `continueOnFail=true`.
- La credencial fue creada en una sesión de desarrollo de la agencia durante el build del v3 — **no hay evidencia de que pertenezca a la cuenta Zoom de Mauricio**. Probablemente fue una cuenta pre-creada por la agencia para destrabar el desarrollo sin depender de credenciales del cliente.
- El nodo **`Crear evento`** (Google Calendar) usa credencial `Google Calendar account 2` id `CVeDywE8Gb5JgEjC` — esta sí funciona contra el calendar de Mauricio (confirmado por Mauricio: las citas aparecen en su calendar).
- `continueOnFail: true` en el nodo Zoom hace que cualquier falla de la integración degrade silenciosamente: el output del `Respond LIBRE` sale con `zoom_status: 'fallback'` y `zoom_link: null`, pero el evento Calendar se crea igual con `description: 🎥 Zoom: PENDIENTE`.

---

## 3. Hipótesis diagnóstica

La credencial Zoom configurada en n8n **existe y es válida** (el flujo no crashea, no aparece error en logs), pero apunta a una cuenta Zoom que **no es la de Mauricio**. Esto explica por qué:
- El flujo no falla.
- El lead recibe un `join_url` real (la meeting sí se crea).
- Mauricio no la ve en su dashboard (la meeting vive en otra cuenta).

Sub-hipótesis a descartar durante el fix:

**(a) Cuenta cruzada (probabilidad alta):** la credencial es de una cuenta Zoom de la agencia (o de otro proyecto) y las meetings creadas existen en esa cuenta. Mauricio no las ve porque no es dueño de esa cuenta. **Síntoma esperado si es esto:** loguearse a `zoom.us/meeting` con las credenciales actualmente configuradas mostraría las meetings de prueba históricas que el agente generó durante smoke tests.

**(b) Token OAuth expirado silenciosamente (probabilidad baja):** la credencial OAuth fue revocada o expiró, y el nodo devuelve sin crear meeting pero no propaga error porque `continueOnFail` está activo. **Síntoma esperado si es esto:** logs de n8n del nodo Zoom mostrarían response 401/403 silenciado. Las meetings no existirían en ninguna cuenta.

Diagnóstico rápido pre-fix (opcional, no bloqueante): revisar 1-2 ejecuciones recientes del sub-workflow en n8n donde `zoom_status` haya dado `'ok'` y leer el response del nodo Zoom para confirmar cuál de las dos sub-hipótesis aplica. El fix es el mismo en ambos casos.

---

## 4. Plan de fix — paso a paso

Aplicar cuando Mauricio envíe sus credenciales Zoom.

### Step 1 — Mauricio envía credenciales

Mauricio manda por **WhatsApp privado** (NO grupo, NO email):
- Usuario Zoom (email asociado a la cuenta).
- Contraseña.
- Confirmación de que esa es la cuenta donde quiere ver las meetings del agente.

Si tiene 2FA activado: indicar a Mauricio que lo desactive temporariamente para hacer el OAuth flow en n8n, o tener disponible el dispositivo del segundo factor durante el setup.

### Step 2 — Verificación manual de la cuenta

- Loguear a `zoom.us` con las credenciales que mandó Mauricio.
- Confirmar visualmente:
  - Email del perfil = email que Mauricio confirmó.
  - Plan de la cuenta (Free / Pro / Business). **Importante:** Free tier limita meetings a 40 min — el sub-workflow agenda 30 min, queda dentro del límite, pero registrar el plan para tener el dato.
  - Dashboard `Meetings` accesible.

### Step 3 — Crear nueva credencial OAuth2 en n8n

- En n8n: `Credentials` → `New` → `Zoom OAuth2 API`.
- Label sugerido: `Zoom account Mauricio TOFO` (claro y discriminable de la vieja).
- Completar el OAuth flow loguéandose con las credenciales del Step 1.
- Verificar que la credencial guarda OK y queda `connected`.

### Step 4 — Re-bindear el nodo `Crear meeting Zoom` del sub-workflow v3

- Abrir el sub-workflow `Chequear disponibilidad | Tofo` (id `vpLmZ299yXJrOSBv`) en n8n.
- Localizar el nodo `Crear meeting Zoom`.
- En el campo `Credential to connect with`, cambiar de `Zoom account` (id `TllmBz0re6WGmTw2`) a la nueva credencial creada en Step 3.
- Guardar el workflow.
- Verificar que el workflow sigue `active: true` post-save.

### Step 5 — (Opcional, hacer post-smoke test) limpieza de credencial vieja

- Una vez confirmado por Z1-Z5 que la nueva credencial funciona, eliminar la credencial `zoomOAuth2Api` id `TllmBz0re6WGmTw2` desde el panel `Credentials` de n8n.
- Esto evita confusión futura y elimina la posibilidad de que otro workflow la use por error.
- **No hacer antes del smoke test** — necesitamos la credencial vieja disponible por si el rollback del Step 7 aplica.

### Step 6 — Smoke test (ver §5).

### Step 7 — Documentar en `CLAUDE.md` y archivar este doc

- Actualizar el bloque TFO en `CLAUDE.md` raíz reflejando la nueva credencial y eliminando la mención al fix pendiente.
- Mover este doc a status `RESUELTO` en el header.

---

## 5. Smoke test post-fix (5 casos — todos deben pasar)

Ejecutar contra el sub-workflow vivo en n8n con un sessionKey de prueba (no contaminar leads reales).

| ID | Caso | Verificación | Pass criteria |
|----|------|--------------|---------------|
| **Z1** | Agendar cita de prueba: trigger el sub-workflow con un slot futuro válido (martes 11:00 CDMX próximo). | Loguear a `zoom.us/meeting` con la cuenta de Mauricio (la del Step 2). | La meeting aparece en el dashboard con el `topic` esperado, fecha/hora correcta en TZ CDMX, duración 30 min. |
| **Z2** | Tomar el `join_url` devuelto por `Respond LIBRE` (el campo `zoom_link`). | Abrir el link en navegador incógnito (sin sesión Zoom). | Lleva al lobby/waiting room de la meeting de Z1 — **NO** a una meeting de otra cuenta, NO a un PMI, NO a un 404. |
| **Z3** | Tomar el `start_url` del `description` del Calendar event. | Abrir el link logueado como Mauricio. | Arranca la meeting como host (Mauricio tiene controles de host: mute all, end meeting, etc.). |
| **Z4** | Email de invitación de Zoom. | Revisar `mauriciogarciadelav@gmail.com` (o el email asociado a la cuenta Zoom). | Llegó email automático de Zoom con los detalles de la meeting de Z1. |
| **Z5** | Limpieza post-test. | Cancelar las 1-2 meetings de prueba desde el dashboard Zoom de Mauricio + eliminar los eventos correspondientes del Google Calendar. | Dashboard Zoom y Calendar quedan limpios sin restos del smoke test. |

**Bloqueante:** los 5 deben pasar antes de marcar el fix como resuelto. Si Z2 falla pero Z1/Z3/Z4 pasan, hay sub-hipótesis nueva (¿el sub-workflow devuelve `join_url` de meeting vieja cacheada?) — investigar antes de promover.

---

## 6. Rollback plan

Si después del Step 4 el sub-workflow crashea, devuelve responses raros, o los smoke tests Z1-Z5 fallan de forma no-recuperable:

1. **No eliminar la credencial vieja durante el fix** (Step 5 es post-smoke test deliberadamente).
2. Re-bindear el nodo `Crear meeting Zoom` a la credencial vieja `zoomOAuth2Api` id `TllmBz0re6WGmTw2`.
3. Guardar el sub-workflow.
4. Volver al estado degradado conocido: el agente sigue creando meetings en la cuenta equivocada pero el flujo no crashea, el Calendar sigue funcionando, el agente sigue agendando citas. Mauricio sigue sin verlas en su dashboard pero el lead no recibe un error visible.
5. Re-diagnosticar antes de reintentar (revisar logs del nodo Zoom de los smoke tests fallidos, verificar el OAuth flow del Step 3, verificar que Mauricio realmente confirmó esa cuenta como destino).

**Justificación:** el estado degradado actual (meetings en cuenta cruzada) es preferible a un crash del sub-workflow que rompa el agendamiento por completo. El agente al menos sigue agendando citas en Calendar; el problema Zoom es resoluble manualmente por Mauricio durante el lapso entre el rollback y el siguiente intento de fix (puede recrear la meeting a mano en su Zoom y pasarle el link al lead por el chat de Live Chat).

---

## 7. Notas operativas

- Este fix **no requiere cambios en el prompt B2B v1.8** — el prompt ya documenta el shape del `Respond LIBRE` con `zoom_status: 'ok' | 'fallback'` y tiene respuestas modelo para ambos casos. Una vez que la credencial nueva esté en su lugar, el agente naturalmente empezará a devolver `zoom_status: 'ok'` con un `join_url` real de la cuenta de Mauricio.
- Este fix **no requiere re-export de v3 a v4** — el cambio es solo en la credencial bindeada al nodo, no en la topología ni en parámetros del workflow. El JSON exportado conserva referencias a credenciales por id, así que si en algún momento se vuelve a importar el JSON del repo, el id de credencial nuevo va a venir cableado correctamente (asumiendo que el id queda registrado en el JSON post-fix). **Recomendado:** re-exportar el sub-workflow post-Z5 OK y commitear como `chequear-disponibilidad-tofo-v3.json` reemplazando el actual, para que el repo refleje el binding correcto.
- Si Mauricio tarda más de 1 semana en mandar credenciales: considerar respuesta intermedia en el prompt B2B para que el agente diga explícitamente "te paso el link de Zoom por aquí en unos minutos" en lugar de afirmar que ya quedó agendada en Zoom — evita la promesa rota que generó el feedback original. Reevaluar si el delay se extiende.