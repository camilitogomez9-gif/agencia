# Testing Guide v5 — TOFO Pizza (Zoom auto-agendamiento)

**Fecha:** 2026-06-15
**Versiones cubiertas:** Derivación v1.4 · B2B **v1.7** · Servicio v1.5 · Reposición v1.4 · RRSS v1.5 · Sub-workflow `Chequear disponibilidad | Tofo v3` (`vpLmZ299yXJrOSBv`, active)
**Objetivo:** validar el bump v1.7 del agente B2B + el sub-workflow v3 que crea automáticamente una meeting de Zoom por cada cita y devuelve `zoom_link` + `zoom_status` al agente. Hereda **completo** §A/§B/§C/§D/§G de v4 con ajustes en A6/A8 (shape ampliado) + agrega A9/A10 (Zoom happy + fallback) + B16 (E2E con join_url).

---

## Estructura

- **§A** — Tests pin data del sub-workflow v3 (10 casos: A1-A8 heredados de v4 con A6/A8 actualizados + A9/A10 nuevos para Zoom)
- **§B** — Tests E2E con AI Agent (15 heredados de v4 + B16 nuevo para Zoom)
- **§C** — Regression tests v1.5 (Oscar Amaya, 12 casos — heredado de v4)
- **§D** — Checklist de promoción a LIVE (actualizado)
- **§G** — REGRESSION incidente 2026-06-08 (heredado de v4 sin cambios — 18 casos)
- **§Z — NUEVO: Verificación end-to-end de Zoom** (5 chequeos manuales en dashboard Zoom + Calendar)
- **§E/F/H** — Datos de test, referencias, notas operativas

Marcado de resultado: ⬜ pendiente · ✅ pasa · ❌ falla · 🟡 parcial

---

## §A — Tests pin data del sub-workflow v3 (10 casos)

### A1-A5 — Validación de entrada (heredados de v3, sin cambios)

(Idénticos a v3 §A1-A5. Probar fecha pasada, no laboral, fuera de ventana, minutos no redondos, formato inválido. El sub-workflow debe devolver `Respond NO VÁLIDO` con `motivo` correspondiente. **No invoca Get availability ni Crear meeting Zoom ni Crear evento.**)

| # | Input | Esperado |
|---|---|---|
| A1 | `fecha_hora: "ayer"` (string libre, no ISO) | `{libre:false, motivo:"formato_invalido"}` |
| A2 | `fecha_hora: "2025-01-01T11:00:00-06:00"` (pasada) | `{libre:false, motivo:"fecha_pasada"}` |
| A3 | `fecha_hora: "2026-06-20T11:00:00-06:00"` (sábado) | `{libre:false, motivo:"no_laboral"}` |
| A4 | `fecha_hora: "2026-06-16T09:00:00-06:00"` (martes 9 AM) | `{libre:false, motivo:"fuera_ventana"}` |
| A5 | `fecha_hora: "2026-06-16T10:30:00-06:00"` (martes 10:30) | `{libre:false, motivo:"minutos_no_redondos"}` |

**Resultado §A.1:** ⬜ / ⬜ / ⬜ / ⬜ / ⬜

### A6 — Happy path libre (SHAPE ACTUALIZADO) 🆕

| # | Input | Esperado |
|---|---|---|
| A6 | `fecha_hora: "2026-06-16T11:00:00-06:00"`, `nombre: "TestLead"`, `subscriber_id: "TEST_001"`, `canal: "wa"`, `telefono: "+521234567890"` | Output del `Respond LIBRE`: `{libre:true, evento_id:<string non-empty>, fecha:"2026-06-16T11:00:00.000-06:00", fecha_humana:"martes 16 de junio a las 11:00", zoom_link:<string con formato https://*.zoom.us/j/*?pwd=*>, zoom_status:"ok", mensaje:<string que contenga literal el zoom_link>}` |

**Verificación adicional A6:**
- En el calendar de `mauriciogarciadelav@gmail.com` aparece evento "Reunión TOFO con TestLead (wa)" el 2026-06-16 11:00–12:00 CDMX.
- El `description` del evento contiene una línea `🎥 Zoom: https://...` con el link literal y `Meeting ID: …` y `Start URL (host): …`.
- En el dashboard de Zoom (`zoom.us/meeting`) aparece una meeting programada para 2026-06-16 11:00 CDMX con topic `Reunión TOFO con TestLead`.

**Resultado A6:** ⬜

### A7 — Slot ocupado (sin cambios)

| # | Input | Esperado |
|---|---|---|
| A7 | Mismo slot que A6 (después de A6, mismo horario) | `{libre:false, motivo:"ocupado", alternativas:["10:00","12:00"], mensaje:"Ese horario está ocupado..."}` |

**Verificación:** Ni `Crear meeting Zoom` ni `Crear evento` deben haberse ejecutado. La rama OCUPADO los salta.

**Resultado A7:** ⬜

### A8 — Happy path con canal IG (SHAPE ACTUALIZADO) 🆕

| # | Input | Esperado |
|---|---|---|
| A8 | `fecha_hora: "2026-06-17T10:00:00-06:00"`, `nombre: "AnaIG"`, `canal: "ig"`, `subscriber_id: "TEST_002"`, `telefono: ""` | Mismo shape ampliado que A6 con `fecha_humana: "miércoles 17 de junio a las 10:00"`, summary del Calendar: "Reunión TOFO con AnaIG (ig)". |

**Resultado A8:** ⬜

### A9 — NUEVO: Zoom happy path explícito 🆕

| # | Input | Esperado | Verificación |
|---|---|---|---|
| A9 | Cualquier input válido futuro (ej: jueves 18-06 12:00) | `zoom_status === "ok"` y `zoom_link` matchea regex `^https://[a-z0-9.]+\.zoom\.us/j/\d+\?pwd=[A-Za-z0-9._-]+$` | Abrir `zoom_link` en navegador → debe llevar al lobby de Zoom (waiting room) sin pedir passcode (porque va embebido). El `mensaje` contiene el `zoom_link` literal. |

**Resultado A9:** ⬜

### A10 — NUEVO: Fallback Zoom failure 🆕

**Setup del test:** Forzar falla del nodo Zoom. Dos formas:
1. **Forma robusta**: en el nodo `Crear meeting Zoom`, cambiar temporalmente el `additionalFields.type` a un valor inválido (ej: `999`) — Zoom API responde 400. Recordar revertir.
2. **Forma rápida**: deshabilitar el nodo `Crear meeting Zoom` y manualmente pasar pin data al `Crear evento` simulando que Zoom no corrió.

| # | Input | Esperado | Verificación |
|---|---|---|---|
| A10 | Cualquier input válido futuro (ej: viernes 19-06 11:00) con nodo Zoom forzado a fallar | `{libre:true, evento_id:<string>, zoom_link:null, zoom_status:"fallback", mensaje:<string con "El link de Zoom te lo paso por acá un rato antes de la cita.">}` | El sub-workflow **NO aborta** (continueOnFail=true en Zoom). El evento de Calendar SÍ se crea, con `description` que dice `🎥 Zoom: PENDIENTE — crear meeting manualmente y enviar link al lead`. |

**Resultado A10:** ⬜

**Resultado §A:** ⬜ / ⬜ / ⬜ / ⬜ / ⬜ / ⬜ / ⬜ / ⬜ / ⬜ / ⬜ (10 casos)

---

## §B — Tests E2E con AI Agent

(B1-B15 idénticos a v4. Referenciar `testing-guide-v3.md` §B y `testing-guide-v4.md` §G.5 para casos heredados.)

**Resultado §B.1 (RRSS):** ⬜ / ⬜ / ⬜ / ⬜ / ⬜ / ⬜ / ⬜
**Resultado §B.2 (B2B base):** ⬜ / ⬜ / ⬜ / ⬜ / ⬜
**Resultado §B.3 (sub-workflow E2E):** ⬜ / ⬜ / ⬜

### B16 — NUEVO: conversación B2B con confirmación que incluye Zoom link 🆕

**Setup:** lead nuevo WhatsApp, número de prueba.
1. Lead: `"Hola, vi su publicidad. Estoy en CDMX, quiero saber el precio."`
2. Agente: da precio en USD + MXN, ofrece llamada con director.
3. Lead: `"Sí dale, mañana a las 11."`
4. Agente: invoca `check_disponibilidad` con `fecha_hora: "2026-06-16T11:00:00-06:00"` (asumiendo hoy lunes 2026-06-15).
5. Sub-workflow: `{libre: true, zoom_link: "https://us05web.zoom.us/j/...", zoom_status: "ok", ...}`
6. Agente: invoca `elevar_conversacion` con `tipo='b2b'`.
7. Agente al lead: `"Listo, [nombre]. Te agendé para el martes 16 de junio a las 11:00 hs (hora México). Te conectás por este link de Zoom el día de la cita: https://us05web.zoom.us/j/..."`

**Esperado:**
- El mensaje al lead contiene el `join_url` literal (sin acortar, sin reescribir, idéntico al que vino del sub-workflow).
- Logueado en `sys_tool_calls` (o equivalente): 1 row `check_disponibilidad` con `output.zoom_status === 'ok'` + 1 row `elevar_conversacion` con `tipo='b2b'`.
- El evento del Calendar tiene el link en el `description`.

**Falla si:**
- El agente acorta el link (ej: dice "te paso por DM" sin el link literal).
- El agente inventa un link distinto al que vino en el sub-workflow.
- El agente confirma SIN incluir el link (omite el `zoom_link` cuando `zoom_status === 'ok'`).
- El agente menciona el `start_url` (eso es solo para Mauricio).

**Resultado B16:** ⬜

### B17 — NUEVO: conversación B2B con Zoom fallback 🆕

**Setup:** mismo flujo que B16 pero con Zoom desconectado (simular `zoom_status === 'fallback'`).

**Esperado:**
- Agente al lead: `"Listo, [nombre]. Te agendé para el martes 16 de junio a las 11:00 hs (hora México). El link de Zoom te lo paso por acá un rato antes de la cita."`
- El evento del Calendar se creó igual con `description` que dice `🎥 Zoom: PENDIENTE`.
- Sin invención de link ni de PMI personal.

**Falla si:**
- El agente inventa un link.
- El agente dice "te paso un link de Zoom genérico" o algo similar.
- El agente le dice al lead que la cita no se agendó (porque sí se agendó — solo falta el link).

**Resultado B17:** ⬜

---

## §C — Regression v1.5 (Oscar Amaya, 12 casos heredados)

(Idéntico a v3/v4. 12 casos C1-C12. Críticos: si alguno falla, NO promover a LIVE.)

**Resultado §C.1 (protocolo moneda):** ⬜ / ⬜ / ⬜
**Resultado §C.2 (financiamiento):** ⬜ / ⬜ / ⬜
**Resultado §C.3 (equivalencias):** ⬜ / ⬜ / ⬜
**Resultado §C.4 (tabla decisión):** ⬜ / ⬜ / ⬜

---

## §G — Regression incidente Mauricio 2026-06-08 (18 casos heredados)

(Idéntico a v4. NO se modifica con el cambio de Zoom — las prohibiciones de "cita sin tool call" + "horario fuera ventana" + "anti info-inventada" siguen vigentes. Si algún caso §G falla en v5, indica regresión por el bump a v1.7.)

**Resultado §G.1:** ⬜ / ⬜ / ⬜ / ⬜ / ⬜ / ⬜
**Resultado §G.2:** ⬜
**Resultado §G.3:** ⬜ / ⬜ / ⬜ / ⬜ / ⬜ / ⬜
**Resultado §G.4:** ⬜ / ⬜ / ⬜
**Resultado §G.5:** ⬜ / ⬜

---

## §Z — Verificación end-to-end Zoom + Calendar (5 chequeos manuales)

Después de ejecutar A6, A8, A9 (y eventualmente B16) sobre el sub-workflow vivo, hacer **estos 5 chequeos en el ambiente real**:

| # | Verificación | Cómo | Esperado |
|---|---|---|---|
| Z1 | El meeting de Zoom aparece en el dashboard de Mauricio | Login en `zoom.us/meeting` con la cuenta cuyo OAuth está en la credencial `TllmBz0re6WGmTw2` | Las meetings de A6/A8/A9 aparecen en "Upcoming Meetings" con topic "Reunión TOFO con TestLead", fecha/hora correcta CDMX, duración 30 min, waiting room habilitado |
| Z2 | El `join_url` funciona | Abrir el link en navegador incógnito | Lleva a la pantalla de "Waiting for the host to start..." (waiting room). No pide passcode manual (va embebido en `?pwd=`) |
| Z3 | El `start_url` deja entrar como host | Abrir el `start_url` (del description del Calendar event) en navegador | Arranca la meeting como host sin pedir credenciales |
| Z4 | El evento del Calendar tiene los 3 campos Zoom | En el Calendar de Mauricio, abrir el evento creado | El `description` contiene 3 líneas: `🎥 Zoom: ...join_url...`, `Meeting ID: ...`, `Start URL (host): ...` |
| Z5 | Limpieza opcional post-test | Borrar manualmente las meetings/eventos de test en Zoom + Calendar | Sin huérfanos consumiendo cuota o ensuciando el calendar real de Mauricio |

**Resultado §Z:** ⬜ / ⬜ / ⬜ / ⬜ / ⬜

---

## §D — Checklist de promoción a LIVE (actualizado v5)

Solo marcar después de §A + §B + §C + §G + §Z pasados.

- [ ] §A.1 — 5 tests validación entrada OK (A1-A5)
- [ ] §A — A6 happy path con shape ampliado OK
- [ ] §A — A7 ocupado OK
- [ ] §A — A8 happy path canal IG con shape ampliado OK
- [ ] **§A — A9 Zoom happy path OK** (NUEVO)
- [ ] **§A — A10 Zoom fallback OK** (NUEVO)
- [ ] §B.1 — 7 tests RRSS OK
- [ ] §B.2 — 5 tests B2B base OK
- [ ] §B.3 — 3 tests E2E check_disponibilidad OK
- [ ] **§B — B16 E2E con join_url literal OK** (NUEVO)
- [ ] **§B — B17 E2E con fallback OK** (NUEVO)
- [ ] §C.1/2/3/4 — 12 regression Oscar Amaya OK
- [ ] §G.1/2/3/4/5 — 18 regression incidente Mauricio OK (heredado v4)
- [ ] **§Z.1-Z5 — 5 verificaciones Zoom/Calendar end-to-end OK** (NUEVO)
- [ ] Prompt B2B v1.7 copiado a Google Doc vivo
- [ ] Sub-workflow v3 importado a n8n con workflowId `vpLmZ299yXJrOSBv` (reemplaza v2 in-place)
- [ ] Main v3 importado (sin nodo Zoom huérfano) — id del workflow conservado
- [ ] Status TFO en CLAUDE.md → LIVE
- [ ] Status TFO en CLIENT_INFO.md → live
- [ ] Anuncio a Mauricio: Zoom auto-agendamiento vivo

**Tras 1 semana sin issues en LIVE:**
- [ ] Confirmar en `sys_tool_calls`: 0 casos donde el agente dijo "te paso link" pero `zoom_status` era `'ok'` (debería haber usado el link)
- [ ] Confirmar en Zoom dashboard: 0 meetings huérfanas (creadas por test que se olvidaron)
- [ ] Confirmar con Mauricio: 0 quejas de "me llegó link pero no funcionó"

---

## §E — Datos para test

**Hoy (referencia):** 2026-06-15 (lunes)
**Mañana hábil:** 2026-06-16 (martes)
**Sábado próximo:** 2026-06-20
**TC referencial:** ~17.5 MXN/USD
**ID del sub-workflow vivo:** `vpLmZ299yXJrOSBv` (v3 reemplaza v2 in-place)
**Calendar de availability:** `mauriciogarciadelav@gmail.com` (credential `z0IngCgigP1wgAux`)
**Calendar de evento creado:** `Google Calendar account 2` (credential `CVeDywE8Gb5JgEjC`)
**Credencial Zoom:** `Zoom account` (id `TllmBz0re6WGmTw2`)

---

## §F — Referencias

- [Sub-workflow v3 — Zoom integrado](../03_workflows/chequear-disponibilidad-tofo-v3.json)
- [Sub-workflow v2 (referencia histórica)](../03_workflows/chequear-disponibilidad-tofo-v2.json)
- [Main v3 — sin nodo Zoom huérfano](../03_workflows/agente-tofo-web-b2b-rrss-v3.json)
- [B2B v1.7](../04_agents/agente-tofo-b2b-system-prompt.md)
- [B2B v1.6 backup](../04_agents/agente-tofo-b2b-system-prompt-v1.6.md)
- [Testing guide v4 (heredada)](testing-guide-v4.md)
- [Plan de implementación](/Users/camilo/.claude/plans/mauricio-de-tofo-quiere-reflective-hare.md)

---

## §H — Notas operativas

### Cómo ejecutar A9 (happy path Zoom)

1. Abrir n8n → workflow `Chequear disponibilidad | Tofo v3` (id `vpLmZ299yXJrOSBv`).
2. Click derecho en el Trigger → "Pin data" → pegar input válido (ej: jueves 18-06-26 12:00).
3. Click "Execute Workflow".
4. Verificar el output del nodo `Crear meeting Zoom`: debe tener `join_url`, `id`, `password`, `start_url`.
5. Verificar el output del nodo `Respond LIBRE`: `zoom_status: 'ok'` + `zoom_link` con el join_url.
6. Hacer chequeos §Z1-Z4.

### Cómo ejecutar A10 (fallback)

**Opción 1 — Type inválido (recomendada):**
1. Editar nodo `Crear meeting Zoom`: cambiar `additionalFields.type` de `2` a `999`. Guardar.
2. Ejecutar el workflow con input válido.
3. Verificar que el nodo Zoom falla pero el sub-workflow sigue (gracias a `continueOnFail`).
4. Verificar `Respond LIBRE.zoom_status === 'fallback'` + `zoom_link === null` + `mensaje` con texto de fallback.
5. Verificar que el Calendar event SÍ se creó con description `🎥 Zoom: PENDIENTE`.
6. **Revertir** el `type` a `2` antes de cerrar.

**Opción 2 — Deshabilitar Zoom temporalmente:**
1. Click derecho en `Crear meeting Zoom` → "Deactivate node".
2. Ejecutar.
3. Reactivar al terminar.

### Triage en caso de fallo

| Falla | Causa probable | Acción |
|---|---|---|
| A9 → Zoom devuelve 401/403 | OAuth expirado | Reconectar credencial `TllmBz0re6WGmTw2` en n8n |
| A9 → Zoom devuelve 429 | Cuota de meetings excedida | Verificar plan Zoom de Mauricio (free vs Pro). Free permite ~100/día. |
| A9 → `join_url` sin `?pwd=` | Configuración de Zoom requiere passcode manual | Revisar settings Zoom — habilitar "Embed passcode in invite link" |
| A10 → `zoom_status === 'ok'` aún con falla | `continueOnFail` no está activo o la lógica condicional del Respond LIBRE falla | Inspeccionar el nodo `Crear meeting Zoom` → tab "Settings" → "Continue On Fail" debe estar en true |
| B16 → agente menciona `start_url` al lead | Filtro de output del sub-workflow falló | El output del Respond LIBRE NUNCA debe incluir `start_url`. Verificar que los assignments solo exponen `zoom_link` (que es `join_url`). |
| B16 → agente acorta o reescribe el link | Prompt v1.7 no copiado al Google Doc vivo | Re-copiar el bloque del paso 5 del prompt + la regla añadida v1.7 |
| B17 → agente inventa link | Falla la regla "NUNCA inventes" del prompt v1.7 | Re-verificar prompt vivo + considerar bajar temperature del agente |
