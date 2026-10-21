# F3 — Workflow Principal v0.1 — Setup & Smoke Test

> **Workflow:** `clients/SYS_SistemasYSoluciones/03_workflows/sys-agente-principal-v0.1.json`
> **Fecha generación:** 2026-05-29
> **Alcance v0.1:** webhook → normalize → AI Agent (gpt-4o) + memoria Postgres → split → respond.
> **Fuera de alcance v0.1:** tools (F4), integración ManyChat real (F6), tabla Leads (CRM pausado).

---

## Qué tiene este workflow

```
[Webhook]
   ↓
[Normalize Payload]
   ↓
[IF skip?] ──(true)──→ [Respond Skip]
   ↓ (false)
[Build User Message Context]
   ↓
[AI Agent] ←─── [OpenAI Chat Model (gpt-4o)]
   ↓        ←─── [Postgres Chat Memory] (Supabase, sessionKey=canal_subId, window=20)
[Split Respuesta] (parte1/2/3 por separador "---")
   ↓
[Respond to Webhook] (devuelve JSON con raw + partes)
```

**System prompt:** v2.1 inline (23.9 KB embebidos en el nodo AI Agent).
**Modelo:** gpt-4o, temperature 0.4, max tokens 1500.
**Memoria:** 20 turnos en `n8n_chat_histories` de Supabase.

---

## Paso 1 — Importar en n8n

1. [TU-INSTANCIA-N8N] → sidebar izquierda → **Workflows** → botón **"Import from File"** (o **"Add Workflow → Import"**).
2. Seleccionar `sys-agente-principal-v0.1.json` (descargado o accesible localmente).
3. n8n importa el workflow con todos los nodos y conexiones.

> Si n8n se queja por credentials inválidos al importar, **es esperado** — el JSON trae placeholders `<<<COMPLETAR_*_CRED_ID>>>` para que vos los cablees en el siguiente paso.

---

## Paso 2 — Cablear credentials (2 nodos)

### 2.1 — Nodo `OpenAI Chat Model (gpt-4o)`

1. Click sobre el nodo → panel derecho.
2. Sección **"Credential for OpenAI API"** → dropdown → seleccionar la credencial existente (`OpenAI la agencia` o como se llame en tu n8n).
3. Si no existe: crear una nueva con la API key compartida de la agencia.
4. **Save**.

### 2.2 — Nodo `Postgres Chat Memory`

1. Click sobre el nodo → panel derecho.
2. Sección **"Credential for Postgres"** → dropdown → seleccionar **`Supabase SYS`** (la que creamos en F2, ID `<<<el-tuyo>>>`).
3. Verificar parámetros:
   - **Session ID type:** `customKey`
   - **Session Key:** `={{ $('Normalize Payload').item.json.leadIdentifier }}`
   - **Table Name:** `n8n_chat_histories`
   - **Context Window Length:** `20`
4. **Save**.

---

## Paso 3 — Activar el workflow

Toggle **"Active"** arriba a la derecha. El webhook queda disponible en:

```
https://[TU-INSTANCIA-N8N]/webhook/sys-agent
```

---

## Paso 4 — Smoke test desde curl

### 4.1 — Mensaje "Hola" (apertura)

```bash
curl -X POST https://[TU-INSTANCIA-N8N]/webhook/sys-agent \
  -H "Content-Type: application/json" \
  -d '{
    "canal": "test",
    "subscriber_id": "test-001",
    "mensaje": "Hola"
  }'
```

**Respuesta esperada (JSON):**
```json
{
  "ok": true,
  "raw": "Hola, soy el asistente virtual de Sistemas y Soluciones. ¿En qué te puedo ayudar?\n\n---\n\n¿Buscás info sobre algún equipo o tecnología en particular?",
  "parte1": "Hola, soy el asistente virtual de Sistemas y Soluciones. ¿En qué te puedo ayudar?",
  "parte2": "¿Buscás info sobre algún equipo o tecnología en particular?",
  "parte3": "",
  "partes_count": 2
}
```

(El texto exacto puede variar — el modelo es probabilístico — pero debe respetar el tono del prompt y dividir con `---`.)

### 4.2 — Cotización directa (Regla 21)

```bash
curl -X POST https://[TU-INSTANCIA-N8N]/webhook/sys-agent \
  -H "Content-Type: application/json" \
  -d '{
    "canal": "test",
    "subscriber_id": "test-001",
    "mensaje": "Hola, quiero un presupuesto de una impresora DTF"
  }'
```

**Esperado:** el agente pide directamente nombre + teléfono + ubicación (NO hace diagnóstico). Verificar Regla 21 del prompt.

### 4.3 — Memoria persistente (turno 2 con mismo subscriber_id)

```bash
curl -X POST https://[TU-INSTANCIA-N8N]/webhook/sys-agent \
  -H "Content-Type: application/json" \
  -d '{
    "canal": "test",
    "subscriber_id": "test-001",
    "mensaje": "Soy Juan, 11-5555-1234, de Rosario"
  }'
```

**Esperado:** el agente RECUERDA que vino de una cotización directa de DTF (test 4.2) y procede a pedir el mail con la frase exacta de Regla 4.

### 4.4 — Verificar memoria en Supabase

En el SQL Editor de Supabase:

```sql
SELECT id, session_id, message->>'type' AS rol, message->>'content' AS contenido, created_at
FROM n8n_chat_histories
WHERE session_id = 'test_test-001'
ORDER BY id ASC;
```

**Esperado:** ver 6 filas (3 human + 3 ai), todas con session_id = `test_test-001`, en orden temporal.

### 4.5 — Sesión distinta (memoria aislada)

```bash
curl -X POST https://[TU-INSTANCIA-N8N]/webhook/sys-agent \
  -H "Content-Type: application/json" \
  -d '{
    "canal": "test",
    "subscriber_id": "test-002",
    "mensaje": "Te acordás de mí?"
  }'
```

**Esperado:** el agente NO recuerda nada (es un sub_id nuevo). Responde como conversación nueva (saluda, pregunta abierta).

---

## Limitaciones conocidas v0.1

1. **Sin tools.** El agente no puede `buscar_equipo`, `consultar_tecnologia`, `notificar_lead`, etc. Si el cliente pregunta por specs, el agente va a decir "no tengo esa info, te paso con el equipo comercial" (o algo similar). Es esperable — F4 agrega las 9 tools.

2. **Sin integración ManyChat.** El webhook responde JSON al curl. En F6 se cablea desde ManyChat External Request, y la respuesta cambia a `setCustomFields + sendFlow`.

3. **Sin lookup de session state.** El `[CONTEXTO TURNO]` siempre dice "perfil: sin clasificar / etapa: bienvenida / datos: {}". En F4-F5 se agrega un SELECT a `sys_session_state` para que el contexto refleje el progreso real del lead.

4. **Sin notificación a `info@`.** Si el LLM "decide" notificar un lead, lo hace en su respuesta como texto (no real). En F4 se agrega la tool `notificar_lead`.

5. **Sin log a `sys_tool_calls`.** No hay tools que loguear todavía.

---

## Troubleshooting

### "Credential not found" al ejecutar
Pasaste el paso 2 de cableo? Verificá que ambos nodos (OpenAI + Postgres Memory) tengan credenciales seleccionadas.

### "Error: connect ECONNREFUSED" en Postgres Memory
Verificá que la credencial `Supabase SYS` use Session Pooler (`aws-0-sa-east-1.pooler.supabase.com:5432`) y NO Direct Connection. Ver `supabase-credentials.md`.

### "Error: invalid_api_key" en OpenAI
La credencial `OpenAI la agencia` está vencida o mal configurada. Revisar en n8n credentials.

### El agente responde con `[NOTIFICAR_LEAD] ...` como texto
Esperable en v0.1: el system prompt v2.1 menciona las tools pero como NO están conectadas, el LLM las "imagina" como output de texto. Se resuelve en F4.

### Respuesta tarda >15s
El primer request con sesión nueva tarda más (cold start LangChain). Subsecuentes deberían ser <8s. Si tarda >20s seguido, revisar logs OpenAI rate limits.

### `partes_count: 1`
El LLM no usó el separador `---`. Puede pasar si la respuesta es corta (una sola oración). NO es un error, solo significa que parte2 y parte3 quedan vacíos.

---

## Validación final F3 (checklist)

- [x] Workflow importado y activo en n8n
- [x] Credenciales OpenAI + Supabase cableadas
- [x] Smoke test 4.1 (Hola) → respuesta humana con `---` ✅
- [x] Smoke test 4.2 (cotización directa) → pide datos directo (Regla 21) ✅
- [x] Smoke test 4.3 (turno 2 mismo sub_id) → memoria funciona ✅
- [x] Smoke test 4.4 (Supabase SELECT) → 6+ filas en `n8n_chat_histories` ✅
- [x] Smoke test 4.5 (sub_id distinto) → memoria aislada por sesión ✅

**F3 COMPLETADA — 2026-05-29.** Smoke tests OK. Arrancamos F4 (9 tools sub-workflows).

### Nits menores observados (revisar en F7 — testing E2E, no bloqueantes para F4-F6)

1. **Test 1 — saludo:** agente dice "Hola, bienvenido a Sistemas y Soluciones" en vez de "Soy el asistente virtual de Sistemas y Soluciones" como prescribe v2.1. Variante aceptable de tono. Si en F7 aparece consistentemente, reforzar la sección ROL E IDENTIDAD del prompt con un ejemplo verbatim.
2. **Test 3 — frase Regla 4 (mail):** agente usó "¿Te gustaría que te envíe más información sobre las impresoras DTF a tu mail? Si es así, ¿me lo pasás?" en vez de la frase exacta "Si querés, te mando más información sobre los equipos que consultaste. ¿Me pasás tu mail?". Misma intención, distinto wording. Si en F7 se repite, considerar reforzar Regla 4 con bullet "FRASE EXACTA OBLIGATORIA".

Ambos nits van al backlog de calibración del prompt — se revisan después de F7 con 20-50 conversaciones reales.

---

## Próximo: F4 — Tools build (3-5 días)

Para F4 vamos a crear 9 sub-workflows (uno por tool). Patrón base:

```
Execute Workflow Trigger → Code (validate) → Airtable Search/Create → Code (format output) → Postgres Insert (log) → Return
```

Cada sub-workflow exportado a `03_workflows/sys-tool-{nombre}-v1.json`.

Spec completa de las 9 tools: `06_docs/tools-spec-v1.md`.
