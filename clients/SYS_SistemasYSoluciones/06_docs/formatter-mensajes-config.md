# Formatter de Mensajes — Configuración Productiva

**Fecha implementación:** 2026-06-03
**Workflow:** `sys-agente-principal` (post-nuclear, F7 cierre)
**Status:** LIVE
**Patrón:** validado en NPR/NVJ/HBV/STK previo a SYS

---

## Propósito

El AI Agent (gpt-4o) en SYS genera respuestas que a veces no incluyen el separador `---` esperado entre bloques lógicos. Sin separador, el nodo `Split Respuesta` lumpea toda la respuesta en `ai_msg_1` y ManyChat termina enviando UN solo mensaje largo, perdiendo la cadencia natural de WhatsApp.

**Solución:** un nodo LLM dedicado (`gpt-4o-mini`, `temperature=0`, `jsonOutput=true`) entre el AI Agent y el Split Respuesta, especializado únicamente en dividir el output en 1–3 bloques estructurados.

---

## Arquitectura del flujo (post-formatter)

```
Webhook (ManyChat) → Normalize Payload → IF skip? → Build User Msg Ctx
  → AI Agent (gpt-4o + 10 toolWorkflow nodes + Postgres Memory)
  → Formatear mensaje (gpt-4o-mini, jsonOutput, temperature=0)        ← NUEVO
  → Split Respuesta (parsea JSON → ai_msg_1/2/3 con compactación)     ← MODIFICADO
  → IF channel test?
      ├─ true  → Respond Test (con body)
      └─ false → setCustomFields ManyChat → sendFlow ManyChat → Respond to Webhook
```

---

## Nodo "Formatear mensaje" — config completa

**Tipo:** `@n8n/n8n-nodes-langchain.openAi`
**Modelo:** `gpt-4o-mini`
**Credencial:** `OpenAI la agencia®` (cred ID `Fa3aaCsYTBS79y3Y` — reutilizada del AI Agent)
**Options:** `temperature: 0` + `jsonOutput: true`
**Input upstream:** `$json.output` del AI Agent

### System message del formatter (paste-ready)

```text
# Tarea

Formatear el siguiente mensaje del agente de Sistemas y Soluciones (industria gráfica argentina) para envío por WhatsApp/Instagram/Facebook. Mensaje a formatear:

"{{ $json.output.replaceAll("¿","").replaceAll("¡","").replaceAll("'", "").replaceAll("\"","") }}"

## 1: Dividir el mensaje en partes

Para simular un diálogo humano y dinámico, dividí el mensaje principal en hasta tres partes más pequeñas, sin omitir ningún contenido. Cada parte debe tener sentido por sí misma y no puede cortarse en medio de una oración (esperá a que haya un punto, coma o símbolo que cierre la idea). Si el mensaje es breve y no requiere tres partes, dejá las partes innecesarias vacías (como ""). Si el mensaje es extenso, dividilo en tres partes sin perder ningún contenido, permitiendo que las partes sean más largas si es necesario para incluir todo el texto. Asegurate de que ninguna parte termine con un punto final, ya que esto hace que la conversación se sienta más real y fluida.

Devolvé las partes en un formato JSON con esta estructura:
{
  "parte1": "Texto de la primera parte",
  "parte2": "Texto de la segunda parte",
  "parte3": "Texto de la tercera parte"
}

## 2: Formateo de mensajes

En caso de que el mensaje principal sea apto para listados con saltos de línea y guiones (por ejemplo estás presentando modelos de equipos, especificaciones técnicas o datos a recolectar del cliente), formatealo para sumar claridad. Presentá cada elemento con viñetas usando un guión al inicio. Ejemplo: si el mensaje menciona varios modelos HUENU, listalos con guiones y un modelo por línea.

## 3: Preservación de nombres técnicos

Preservá EXACTAMENTE los nombres de marcas, modelos y tecnologías del catálogo. No los reformatees, no los traduzcas, no les cambies mayúsculas/minúsculas. Ejemplos: HUENU, DLICAN, TENETH, HANRUN, XENONS, RISO, Sinajet, Konica Minolta, BIZHUB C450i, HR 6004 DU, DTF Textil, DTF UV, Sublimación, Eco-Solvente.

# Reglas críticas

- Jamás dejes ningún contenido del mensaje principal sin incluir en las partes. No podemos perder información.
- Siempre rellená las variables en orden: primero parte1, luego parte2, luego parte3. Nunca te saltees una parte ni cambies el orden.
- Siempre incluí las 3 variables (parte1, parte2, parte3) en el JSON, aunque algunas estén vacías.
- Las partes divididas deben tener coherencia por sí solas.
- NUNCA agregues comillas dobles dentro del texto de las partes (las comillas del JSON son distintas y necesarias).
- NUNCA agregues frases tipo "perfecto", "genial", "entendido" que no estaban en el mensaje original.
- Preservá el tono rioplatense (vos, contame, mirá) si el original lo tiene.
```

### Adaptaciones vs. el patrón base de RCA Automóviles

| Cambio | Por qué |
|---|---|
| Contexto inicial menciona "agente de Sistemas y Soluciones (industria gráfica argentina)" | Da al formatter cluecabeza para no inventar tono |
| Sección 2 cita explícita "modelos HUENU" como ejemplo de listado | El formatter sabe qué espera listar |
| **Sección 3 nueva — Preservación de nombres técnicos** | Lista marcas + modelos exactos (HUENU, BIZHUB C450i, HR 6004 DU, etc.); le pide preservarlos EXACTAMENTE sin retocar mayúsculas |
| Regla "NUNCA agregues `perfecto/genial/entendido`" | Refuerzo defensivo del tono del prompt principal |
| Credencial: `OpenAI la agencia®` (no RCA Automóviles) | Cred reutilizada del AI Agent, misma cuenta OpenAI |

### Strip de caracteres en el input

El formatter strippea `¿`, `¡`, `'`, `"` del input del AI Agent antes de procesarlo (línea `replaceAll(...)` en el template). Razón histórica del patrón RCA: ciertos caracteres pueden romper el JSON output del LLM. Trade-off aceptado: los signos `¿/¡` no aparecen en la conversación final, pero el tono rioplatense sigue siendo natural (es como mucha gente escribe en WhatsApp).

---

## Nodo "Split Respuesta" — config actualizada

**Cambio vs. el código anterior** (que splitteaba por regex `/^---\s*$/m` sobre el output crudo del AI Agent): ahora **parsea el JSON output del formatter** y compacta las partes no-vacías en orden, evitando que ManyChat haga skip de un mensaje del medio si gpt-4o-mini llenara `parte1+parte3` saltando `parte2`.

### jsCode paste-ready

```javascript
// ManyChat Standard interno 2026 — naming ai_msg_*
// v3 — Lee output JSON del Formatter (gpt-4o-mini) + COMPACTA partes no-vacías
//
// Diferencia vs v2: si el formatter llena parte1+parte3 saltando parte2,
// compactamos las partes no-vacías y las asignamos sequencialmente a ai_msg_1/2/3.
// Eso evita que ManyChat haga skip del mensaje del medio.

const inp = $input.first().json;

// El output del nodo OpenAI Chat puede venir en:
//   - .message.content (string JSON)
//   - .content (string JSON)
//   - directamente como objeto parseado
let parsed = {};
const raw = inp.message?.content ?? inp.content ?? inp;

try {
  parsed = typeof raw === 'string' ? JSON.parse(raw) : (raw && typeof raw === 'object' ? raw : {});
} catch (e) {
  // Fallback: si el formatter devuelve mal el JSON, asignar todo a parte1
  parsed = { parte1: typeof raw === 'string' ? raw : String(raw), parte2: '', parte3: '' };
}

// Compactar partes no-vacías en orden (descartar empties intermedios)
const allParts = [parsed.parte1, parsed.parte2, parsed.parte3]
                   .map(p => String(p || '').trim())
                   .filter(p => p.length > 0);

const ai_msg_1 = allParts[0] || '';
const ai_msg_2 = allParts[1] || '';
const ai_msg_3 = allParts[2] || '';
const ai_msg_count = allParts.length || 1;

// Conservar el output crudo del AI Agent (pre-formatter) para auditoría
const rawOriginal = $('AI Agent').first().json.output || '';

return [{
  json: {
    raw: rawOriginal,
    ai_msg_1,
    ai_msg_2,
    ai_msg_3,
    ai_msg_count,
    subscriber_id: $('Normalize Payload').first().json.subId
  }
}];
```

### Notas sobre el fallback

Si el formatter devuelve JSON inválido (poco probable con `jsonOutput=true`, pero posible si la red falla o la cred expira), el `try/catch` redirige todo el output al `ai_msg_1` (comportamiento legacy). El agente nunca queda mudo.

El campo `raw` siempre conserva el output original del AI Agent (`$('AI Agent').first().json.output`) para auditoría y debug downstream.

---

## Verificación post-aplicación

### Curl directo

```bash
curl -s -X POST https://[TU-INSTANCIA-N8N]/webhook/sys-agent \
  -H "Content-Type: application/json" \
  -H "key: <TOKEN>" \
  -d '{"channel":"test","subscriber_id":"verify-001","last_input_text":"Hola","first_name":"Test"}' \
  | python3 -m json.tool
```

### Esperado

```json
{
  "ok": true,
  "raw": "Hola, bienvenido a Sistemas y Soluciones.\n\n---\n\n¿En qué te puedo ayudar hoy?",
  "ai_msg_1": "Hola, bienvenido a Sistemas y Soluciones",
  "ai_msg_2": "En qué te puedo ayudar hoy?",
  "ai_msg_3": "",
  "ai_msg_count": 2
}
```

Si `ai_msg_count >= 2` cuando el mensaje original tiene 2+ ideas → el formatter funciona correctamente.

---

## Costo y latencia

- **Latencia adicional:** ~250–400 ms por turno (gpt-4o-mini es rápido)
- **Costo adicional:** ~$0.0003–0.0008 USD por turno (negligible vs. el gpt-4o del AI Agent)
- **Cero impacto en lógica de tools:** el AI Agent ejecuta normalmente, el formatter solo reformatea su output final

---

## Pendientes

- [ ] Re-exportar el `sys-agente-principal` post-formatter de n8n como `sys-agente-principal-v0.5.json` en `03_workflows/`. La v0.4 del repo NO refleja el estado vivo (le falta el nodo Formatter + el jsCode actualizado del Split Respuesta).
- [ ] Smoke test con respuestas que naturalmente requieran 3 bloques (saludo + recomendación + pregunta de seguimiento). Confirmar que `ai_msg_count == 3` en esos casos.
- [ ] Monitorear en producción la tasa de fallback (cuándo el `catch` se activa). Si > 1% de los turnos, revisar.
