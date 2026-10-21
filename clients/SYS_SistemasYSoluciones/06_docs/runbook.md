# Runbook — Agente SYS (operación Etapa 2)

> **Para:** Equipo la agencia on-call
> **Cliente:** SYS — Sistemas y Soluciones
> **Versión:** v1
> **Fecha:** 2026-05-28
> **Severidad SLA:** estándar (no es producto crítico 24/7, pero leads no atendidos = dinero perdido)

---

## Arquitectura en una pantalla

```
ManyChat (WA/IG/FB) → n8n webhook /sys-agent → AI Agent (gpt-4o)
                                                 ├─ Postgres Chat Memory (Supabase)
                                                 ├─ 7 tools de lectura → Airtable
                                                 └─ 1 tool de escritura → Airtable + Gmail + Telegram
                                                 ↓
                                              setCustomFields + sendFlow ManyChat
```

**Componentes y dueños:**
- n8n workflows: `[TU-INSTANCIA-N8N]` (la agencia)
- Supabase: `la agencia-sys` project (la agencia)
- Airtable `SyS Catalogo`: cliente (Edgardo + Gerente)
- ManyChat account: cliente

---

## Cuándo la agencia responde a una alerta

| Severidad | Síntoma | SLA respuesta | Acción |
|---|---|---|---|
| **P1** | Agente no responde a NINGÚN mensaje >15 min | 30 min | On-call investiga inmediato |
| **P2** | Tool específica falla >5 veces en 1h / mail al rep no llega | 2h | Investigación normal |
| **P3** | Errores aislados, NOT_FOUND recurrente, lead duplicado | 24h | Backlog |

---

## Diagnóstico rápido (los primeros 5 minutos)

### 1. ¿Está caído el agente?

Test manual desde una cuenta de WhatsApp/IG/FB conectada:
- Mandar "hola" → debería responder en <30s
- Si NO responde → P1

### 2. ¿Dónde es el problema?

```
[ManyChat → n8n] → [n8n → tools] → [tools → Airtable/Postgres] → [n8n → ManyChat]
```

Revisar:

#### a) ManyChat → n8n (¿llega el mensaje?)
- Ir a ManyChat Dashboard → Live Chat → buscar la conversación → ver si el flow Default Reply se ejecutó.
- Si NO se ejecutó: revisar el flow (¿está activo? ¿el External Request configurado bien?).
- Si SÍ se ejecutó: pasar a (b).

#### b) n8n recibió el webhook
- Ir a `[TU-INSTANCIA-N8N]` → Workflows → `sys-agente-principal-v1` → Executions.
- Filtrar por las últimas 15 min.
- Si NO hay ejecuciones reciente: el webhook no llegó. Verificar URL en ManyChat External Request + Auth header.
- Si hay ejecuciones con `error`: abrir la ejecución y ver en qué nodo falló.

#### c) AI Agent / OpenAI
- En la ejecución de n8n, buscar el nodo `AI Agent`.
- Si dio error: ver el error específico.
  - `rate_limit_exceeded` → estamos saturando OpenAI. Esperar 1 min y verificar.
  - `context_length_exceeded` → conversación muy larga, problema de memoria. Investigar `sys_session_state.productos_mostrados` (puede haberse llenado).
  - `model_not_found` → revisar credencial OpenAI (puede haber expirado).

#### d) Tools fallan
- Si el AI Agent llegó a invocar una tool y ésta falló:
- Revisar Supabase → query: `SELECT * FROM sys_tool_calls WHERE status != 'success' ORDER BY created_at DESC LIMIT 20;`
- Identificar la tool problemática y leer `error_message`.
- Causas comunes:
  - Airtable rate limit → ver §4
  - Airtable schema cambió → ver §5
  - Tool con bug → revertir a backup, escalar a dev

#### e) Respuesta no llega al usuario
- En n8n, ver si el nodo `setCustomFields ManyChat` y `sendFlow ManyChat` fueron exitosos.
- Si NO: revisar credenciales ManyChat (token vence cada N meses).
- Si SÍ pero el cliente dice que no le llegó: revisar en ManyChat Live Chat si el Flow "Responder Multi-Parte" se ejecutó.

---

## Incidentes comunes y resolución

### Incidente 1: Agente no responde a ningún mensaje (P1)

**Síntomas:** 0 ejecuciones en n8n en últimos 15 min + clientes reportan que el agente no responde.

**Pasos:**

1. **Verificar que el workflow está activo**: n8n → `sys-agente-principal-v1` → toggle "Active" arriba a la derecha. Si está OFF → activar.

2. **Verificar webhook URL en ManyChat**: ManyChat → Default Reply → External Request → URL debe ser `https://[TU-INSTANCIA-N8N]/webhook/sys-agent` (sin -test).

3. **Test webhook directo con curl**:
   ```bash
   curl -X POST https://[TU-INSTANCIA-N8N]/webhook/sys-agent \
     -H "Authorization: Bearer $MANYCHAT_AUTH_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"canal":"whatsapp","subscriber_id":"test123","mensaje":"hola test runbook"}'
   ```
   - Si devuelve `{ "ok": true }` → n8n OK, problema en ManyChat.
   - Si devuelve 401 → token mal configurado.
   - Si devuelve 500 → bug en workflow, ver Executions.
   - Si timeout → workflow corriendo pero MUY lento o colgado.

4. **Si todo lo anterior pasa pero el agente sigue sin responder a clientes reales**:
   - Mirar Telegram alerts si llegaron warnings de timeout LLM o tool errors.
   - Revisar status OpenAI: https://status.openai.com
   - Revisar status Supabase: https://status.supabase.com

5. **Rollback (último recurso)**:
   - n8n → `sys-agente-principal-v1` → History → restaurar versión anterior.
   - Marcar el workflow viejo como activo.
   - Notificar al cliente que estamos en modo degradado.

---

### Incidente 2: Tool `notificar_lead` falla repetidamente

**Síntoma:** clientes terminan la conversación con datos completos pero los reps no reciben mails. Telegram alerts mencionan ERROR en `notificar_lead`.

**Diagnóstico:**

1. Supabase query:
   ```sql
   SELECT input_payload, error_message, created_at
   FROM sys_tool_calls
   WHERE tool_name = 'notificar_lead'
     AND status = 'error'
     AND created_at >= NOW() - INTERVAL '2 hours'
   ORDER BY created_at DESC;
   ```

2. Causas posibles + acción:

| `error_message` contiene | Causa | Acción |
|---|---|---|
| "Faltó capturar" | El LLM invocó la tool sin todos los campos. Bug en system prompt. | Revisar prompt v2.0; ajustar regla 22; iterar con `/iterar-prompt` |
| "INVALID_RECORD_FIELDS" | Airtable schema cambió (Edgardo renombró campo) | Revisar Airtable; restaurar el nombre original o ajustar el sub-workflow |
| "Rate limit" Airtable | Demasiados leads en poco tiempo | Esperar; verificar con cliente si esperaban pico |
| "Gmail send failed" | Credencial Gmail expiró | Renovar credencial en n8n; reintentar el mail manualmente desde Airtable |

3. **Backfill manual de leads perdidos** (si hubo errores >5):
   - Ir a Airtable Leads → filtrar `Status = "En conversación" AND Notificación enviada = false`
   - Para cada uno: revisar la conversación, validar datos, marcar manual al rep + actualizar status.

---

### Incidente 3: Cliente reporta que el agente "inventa" información

**Síntoma:** rep recibe queja del cliente: el agente le dijo que un equipo X tiene tal especificación, y no es así.

**Diagnóstico:**

1. **Recuperar la conversación:**
   ```sql
   SELECT message FROM n8n_chat_histories
   WHERE session_id = '<<<canal_subId del lead>>>'
   ORDER BY id ASC;
   ```

2. **Recuperar las tool calls:**
   ```sql
   SELECT tool_name, input_payload, output_payload, created_at
   FROM sys_tool_calls
   WHERE session_id = '<<<canal_subId>>>'
   ORDER BY created_at ASC;
   ```

3. **Analizar:**
   - ¿El LLM invocó `buscar_equipo` o `consultar_tecnologia`? Si NO, agente alucinó (problema de prompt).
   - Si SÍ: ¿la tool devolvió la info incorrecta? Verificar el record en Airtable.
   - Si Airtable tiene info incorrecta: corregir + notificar a Edgardo.
   - Si el LLM alucinó a pesar de tool calling: reforzar regla anti-alucinación en prompt, iterar.

4. **Si el cliente reporta varias veces el mismo tipo de error**:
   - Cancelar producción del agente temporalmente.
   - Revisar el system prompt completo.
   - Iterar con `/iterar-prompt` modo B.

---

### Incidente 4: Lead duplicado (mismo cliente, 2 records en Airtable)

**Síntoma:** rep ve dos records del mismo cliente en Airtable Leads.

**Causa probable:** la idempotencia falló (LLM invocó `notificar_lead` 2 veces fuera de la ventana de 30 min).

**Resolución:**

1. Identificar los dos records (mismo Subscriber ID + Canal).
2. Combinar manualmente: dejar el más reciente, copiar notas al activo.
3. Marcar el viejo como `Status = "Duplicado"` (agregar opción al campo si no existe).

**Prevención:** ajustar la ventana de idempotencia en el sub-workflow `notificar_lead` de 30 min a 60 min.

---

### Incidente 5: Latencia alta (>15s para responder)

**Síntoma:** clientes reportan que el agente tarda mucho en contestar. Algunas conversaciones tienen timeout.

**Diagnóstico:**

1. Métricas de tools:
   ```sql
   SELECT * FROM sys_tool_metrics_24h
   WHERE avg_duration_ms > 1500
   ORDER BY avg_duration_ms DESC;
   ```

2. Causas:
   - **Airtable lenta** (Edgardo cargó muchas filas o filterByFormula compleja): considerar agregar vistas Airtable pre-filtradas.
   - **OpenAI lenta**: ver https://status.openai.com
   - **Sub-workflows con LLM internos** (gpt-4.1-mini en buscar_equipo/consultar_aplicacion): mucha latencia. Optimizar el prompt interno o degradar a algoritmo determinista.

3. Mitigación temporal: reducir `contextWindowLength` de Postgres Memory de 20 a 10 (menos contexto = LLM más rápido).

---

### Incidente 6: Edgardo cargó un equipo nuevo y el agente "no lo encuentra"

**Diagnóstico rápido**:

1. Verificar en Airtable que el record tiene:
   - `Status = "Activo"` (NO Próximamente)
   - `Tecnología` linkeada (al menos una)
   - `Descripción corta` no vacía
   - `Disponibilidad zona` con al menos una opción

2. Test directo de la tool:
   - n8n → `sys-tool-buscar-equipo-v1` → Execute Workflow → input con `{ tecnologia: "Esa tecnología" }` → ver si retorna el nuevo equipo.

3. Si la tool sí lo encuentra pero el agente no: problema de prompt (LLM no invoca la tool). Considerar reforzar instrucción.

---

## Mantenimiento periódico (lo que hacemos sin que pase nada)

### Diario (cron automático)

- Check de leads abandonados:
  ```sql
  SELECT * FROM sys_leads_abandonados WHERE horas_inactivo > 24;
  ```
  Si hay >5 con datos completos → seguimiento manual.

- Check de errores de tools (Telegram alert si hay >10 en 24h):
  ```sql
  SELECT tool_name, COUNT(*) AS errores
  FROM sys_tool_calls
  WHERE status = 'error' AND created_at >= NOW() - INTERVAL '24 hours'
  GROUP BY tool_name HAVING COUNT(*) > 10;
  ```

### Semanal (manual)

- Sample 10 conversaciones random + revisión cualitativa
- Métricas de tool calling:
  ```sql
  SELECT * FROM sys_tool_metrics_24h;
  ```
- Revisar Airtable Leads cerrados-ganados vs descalificados → ratio de conversión

### Mensual

- Sync con cliente: ¿cómo va el agente? ¿qué FAQ faltan? ¿hubo casos raros?
- Revisar volumen de OpenAI (cost) → ajustar si necesario
- Actualizar `Config Mensual` con líneas priorizadas del mes

---

## Contactos

| Rol | Nombre | Contacto |
|---|---|---|
| Cliente decisor | Edgardo | (pendiente) |
| Cliente gerente | (pendiente) | (pendiente) |
| Cliente técnico operativo | Edgardo | (pendiente) |
| la agencia responsable | la agencia | [EMAIL-AGENCIA] |
| la agencia on-call | la agencia | WhatsApp interno |

---

## Decisiones arquitectónicas críticas para producción

### ⚠ Patrón Respond-First para webhooks ManyChat (a aplicar en F6 — v0.3)

**Insight 2026-05-29 (la agencia):** ManyChat tiene **timeout muy corto** en sus External Requests. Si el webhook tarda más de ~5–10 segundos en responder, ManyChat marca el request como fallido y NO procesa la respuesta. Como el AI Agent + tools puede tardar 5–15s, el patrón sincrónico actual (webhook → ... → Respond al final) **NO funciona en producción ManyChat**.

**Patrón correcto para F6 v0.3:**

```
[Webhook] → [Respond to Webhook 200 OK]  ← responde inmediato a ManyChat
              ↓ (en paralelo, desacoplado)
           [Normalize] → [AI Agent] → [Tools] → [Split]
              → [setCustomFields ManyChat] → [sendFlow ManyChat]
```

El **Respond to Webhook va PRIMERO** (segundo nodo, justo después del Webhook). Devuelve `{ok: true}` instantáneamente. ManyChat queda contenta. El resto del procesamiento sigue en background y cuando termina, **empuja la respuesta a ManyChat via API** (`setCustomFields` + `sendFlow`).

**Por qué el v0.2 actual NO usa este patrón:** estamos en testing E2E con curl directo. El curl puede esperar 25s sin problema, así que el patrón sincrónico (Respond al final) sirve para diagnóstico. Cuando arranquemos F6, cambiamos a Respond-First.

**Implementación en v0.3 (futuro):**
- Mover el nodo `Respond to Webhook` justo después del `Webhook` (devolver `{ok: true}` inmediato).
- Eliminar el `Respond to Webhook` del final del flow.
- Reemplazar por `setCustomFields ManyChat` + `sendFlow ManyChat` que pushean la respuesta real al chat.

---

## Incidentes resueltos (lecciones aprendidas)

### 2026-05-29 — Log a `sys_tool_calls` no escribía (queryReplacement bug)

**Síntoma:** `sys_tool_calls` vacía a pesar de invocar tools desde el AI Agent. Las tools respondían bien al cliente pero el log fallaba silenciosamente (por `continueOnFail: true`).

**Causa raíz:** sintaxis incorrecta de `queryReplacement` en los nodos Postgres de los 9 sub-workflows. Se usaba `={{ A }}, ={{ B }}, ...` (5 expresiones separadas por comas). n8n trata todo el string como una expresión cuando empieza con `=`, y las comas internas del `JSON.stringify()` rompían el parsing CSV → error `"invalid input syntax for type json"`.

**Fix aplicado:** cambiar a UNA sola expresión que evalúe a un array JS: `={{ [A, B, C, D, E] }}`. n8n mapea el array a `$1, $2, $3, $4, $5` correctamente.

**Aplicado en:** los 9 sub-workflows `sys-tool-*-v1.json` (nodo `Log to sys_tool_calls`) + 1 nodo extra `Update session_state` en `notificar-lead`.

**Para evitar en futuro:** todo `queryReplacement` con valores que puedan contener comas (JSON, strings con descripciones, etc.) debe usar el patrón array `={{ [...] }}`, NO la sintaxis CSV concatenada.

---

## Comandos útiles (Supabase SQL Editor)

```sql
-- Última conversación de un lead
SELECT id, created_at, message->>'type' AS rol, message->>'content' AS contenido
FROM n8n_chat_histories
WHERE session_id = 'whatsapp_549112345678'
ORDER BY id ASC;

-- Todos los tool calls de un session
SELECT tool_name, status, input_payload, output_payload, created_at
FROM sys_tool_calls
WHERE session_id = 'whatsapp_549112345678'
ORDER BY created_at ASC;

-- Top 10 leads más recientes
SELECT session_id, perfil, etapa, datos_capturados, ultima_actividad
FROM sys_session_state
ORDER BY ultima_actividad DESC
LIMIT 10;

-- Tools que más NOT_FOUND devuelven (gaps de catálogo)
SELECT tool_name, COUNT(*) AS not_found_count
FROM sys_tool_calls
WHERE status = 'not_found' AND created_at >= NOW() - INTERVAL '7 days'
GROUP BY tool_name
ORDER BY not_found_count DESC;

-- Sesiones que invocaron notificar_lead exitosamente
SELECT session_id, output_payload->>'lead_id' AS lead_id, created_at
FROM sys_tool_calls
WHERE tool_name = 'notificar_lead' AND status = 'success'
ORDER BY created_at DESC
LIMIT 50;

-- Limpieza emergencia: si una sesión queda colgada en un estado raro
UPDATE sys_session_state
SET etapa = 'cerrado', ultima_actividad = NOW()
WHERE session_id = 'whatsapp_549112345678';
```

---

## Variables y credenciales clave (referencia, NO commitear valores)

> **Configuración 2026-05-29 — Opción C (hardcoded):** los 4 valores no-secretos van hardcoded en los workflows. Catálogo: `06_docs/airtable-credentials.md`. Solo secrets (API tokens) van en credentials de n8n.

| Item | Dónde está |
|---|---|
| MANYCHAT_API_KEY_SYS (secret) | n8n credentials → "ManyChat SYS" (pendiente F6) |
| MANYCHAT_AUTH_TOKEN (secret) | hardcoded en webhook Header Auth + en ManyChat External Request |
| AIRTABLE_TOKEN_SYS (secret) | n8n credentials → "Airtable SYS" (ID `3zohdTBWzW8UUN6P`) ✅ |
| **AIRTABLE_BASE_ID_SYS** (no-secret) | **hardcoded** en nodos Airtable → `appMD3g2HWxzBaZAM` |
| **URL_TIENDA_SYS** (no-secret) | **hardcoded** en tool `consultar_url_tienda` → `https://www.sistemasysoluciones.com` |
| **GMAIL_TO_LEAD_SYS** (no-secret) | **hardcoded** en tool `notificar_lead` → `info@sistemasysoluciones.com` |
| **GMAIL_FROM_SYS** (no-secret) | **hardcoded** en credencial Gmail SYS → `info@sistemasysoluciones.com` |
| OPENAI_API_KEY (secret) | n8n credentials → "OpenAI la agencia" (compartido) |
| Supabase connection (secret) | n8n credentials → "Supabase SYS" (pendiente F2) |
| Gmail (envío al rep) | n8n credentials → "Gmail la agencia SYS" (pendiente) |
| Telegram bot (secret) | n8n credentials → "Telegram Bot Interno" (compartido) |

---

## Escalamiento

Si el incidente excede capacidades del on-call:

1. **Severidad P1 + sin resolución en 30 min** → la agencia
2. **Cliente furioso, riesgo de churn** → la agencia + plan de comunicación al cliente
3. **Bug crítico que requiere refactor** → planning con dev senior (próxima ventana)

---

**Documento vivo. Actualizar después de cada incidente con learning + acción tomada.**
