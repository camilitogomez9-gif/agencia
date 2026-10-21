---
name: smoke-test-agente-webhook
description: >
  Usar este skill cuando hay que ejecutar smoke tests E2E contra el webhook
  productivo de un agente conversacional + evaluar con LLM-as-judge + generar
  reporte. Se activa con frases como "smoke test del agente X", "probar el
  agente en producción", "diagnóstico rápido del webhook", "validar N casos contra
  el webhook". Stack: Python + OpenAI judge. Generaliza el script
  test-sys-webhook-quick.py validado en SYS F7.
---

# Skill: Smoke Test Agente Webhook + LLM Judge

## Descripción

Ejecuta N casos focalizados contra el webhook productivo de un agente, evalúa cada respuesta con LLM-as-judge (`gpt-4o-mini`) y produce un reporte markdown con `% pass | parcial | fail | error` + detalle por caso.

Cada caso es:
- 1 o más turnos (mismo `subscriber_id` = memoria compartida; distinto = aislada)
- Criterio de evaluación en lenguaje natural ("debe recomendar DTF", "NO debe pedir datos", etc.)

El judge devuelve `{verdict: true|false|parcial, reason}`. Errores de transporte (HTTP 5xx, respuesta vacía `{}`) se reportan separados.

---

## Cuándo invocarlo

- Después de cualquier cambio significativo en el agente productivo
- Como gate antes de F8 (GO LIVE)
- Después de iterar el prompt (`/iterar-prompt`) para validar
- Cuando aparecen quejas de usuarios o errores en `sys_tool_calls`

## Cuándo NO invocarlo

- Para testing exhaustivo del prompt en aislado (usar `run-agent-tests.py` existente)
- Para validar 1 tool específica (usar Execute Workflow en n8n directo)

---

## Inputs requeridos

1. **Webhook URL** (default si no se da: `https://[TU-INSTANCIA-N8N]/webhook/{cliente_lower}-agent`)
2. **Lista de casos** (en `06_docs/` del cliente o inline). Por cada caso:
   - `id` (slug corto)
   - `desc` (descripción breve)
   - `turnos`: lista de `(subscriber_id, mensaje)`
   - `expected`: criterio de evaluación en lenguaje natural
3. **`OPENAI_API_KEY`** en el ambiente (`.env`)

Si no hay casos predefinidos, generar 10 casos genéricos focalizados:
- Apertura simple
- Cotización directa
- Tool de KB (consultar_categoria, consultar_faq)
- Tool nueva (si la hay)
- Encadenamiento de 2 tools
- Tool de notificación / write
- Out of scope
- Memoria persistente (2 turnos mismo sub_id)
- Memoria aislada (sub_id distinto)
- Caso límite (datos parciales, ambiguo, etc.)

---

## Proceso

### Paso 1 — Cargar/generar lista de casos

Si existe `clients/{XXX}_{Nombre}/07_testing/smoke-cases.json`: cargarlo.
Si no: generar 10 casos genéricos adaptados al niche del cliente (leído de CLIENT_INFO).

### Paso 2 — Script Python

Base: `scripts/testing/test-sys-webhook-quick.py` (validado en SYS).

Estructura:
```python
import os, sys, json, time, requests
from openai import OpenAI

JUDGE_MODEL = "gpt-4o-mini"
DELAY = 1.5  # segundos entre calls

JUDGE_PROMPT = """Evaluá si la respuesta real del agente cumple el comportamiento esperado.

## Comportamiento esperado:
{expected}

## Respuesta real del agente:
{actual}

Considerá: ¿cubre lo esencial? ¿evita lo prohibido (frases con "NO", "sin", "NUNCA")?
NO penalices: diferencias menores de redacción, contenido adicional útil que no contradice.

Respondé EXACTAMENTE con un JSON: {{"verdict": "true"|"false"|"parcial", "reason": "una oración breve"}}"""

def call_webhook(url, canal, sub_id, mensaje):
    try:
        r = requests.post(url, json={"canal": canal, "subscriber_id": sub_id, "mensaje": mensaje}, timeout=60)
        if r.status_code != 200:
            return f"[HTTP {r.status_code}]: {r.text[:200]}"
        data = r.json() if r.text else {}
        raw = data.get("raw") or " | ".join(p for p in (data.get(f"parte{i}", "") for i in (1,2,3)) if p)
        return raw or f"[Respuesta vacía: {json.dumps(data)[:200]}]"
    except Exception as e:
        return f"[ERROR: {e}]"

def judge(client, expected, actual):
    if actual.startswith("["):
        return ("error", f"Error transporte: {actual[:120]}")
    prompt = JUDGE_PROMPT.format(expected=expected, actual=actual)
    r = client.chat.completions.create(model=JUDGE_MODEL, messages=[{"role":"user","content":prompt}], temperature=0)
    raw = r.choices[0].message.content or ""
    import re
    m = re.search(r'\{.*?\}', raw, re.DOTALL)
    if m:
        d = json.loads(m.group())
        return d.get("verdict","parcial"), d.get("reason","")
    return "parcial", f"No se pudo parsear: {raw[:80]}"

# Loop principal
client = OpenAI()
results = []
for case in cases:
    actual_responses = []
    for sub_id, mensaje in case["turnos"]:
        actual = call_webhook(WEBHOOK, "test", sub_id, mensaje)
        actual_responses.append(actual)
        time.sleep(DELAY)
    # Evaluar la ÚLTIMA respuesta
    verdict, reason = judge(client, case["expected"], actual_responses[-1])
    results.append({...})
```

### Paso 3 — Reporte markdown

Generar `clients/{XXX}_{Nombre}/07_testing/smoke-results-{YYYY-MM-DD-HH-MM}.md` con:
- Resumen: % pass, parcial, fail, error
- Tabla por caso (id, descripción, veredicto, razón truncada, respuesta truncada)
- Detalle completo por caso (mensajes, esperado, obtenido, veredicto)

### Paso 4 — Reportar al usuario

Output en chat:
- Resumen 1 línea: `5/10 OK (50%) | Parcial: 2 | Fail: 1 | Error: 2`
- Si hay errores `[Respuesta vacía: {}]`: sugerir invocar `inspector-bugs-toolworkflow-n8n`
- Si hay parciales sobre criterio subjetivo (tono, brevedad): sugerir iterar prompt con `/iterar-prompt`
- Path del reporte completo

---

## Composición

**Invoca:** ninguno.
**Es invocado por:** F7 del Plan Maestro, después de cada iteración de F5.
**Si falla:** sugerir `inspector-bugs-toolworkflow-n8n` (S6) o `/iterar-prompt`.

---

## Notas operativas

- **Tiempo de ejecución:** ~3 min para 10 casos (delay 1.5s entre calls + latencia LLM judge).
- **Costos:** ~$0.01 por corrida (gpt-4o-mini judge + invocaciones agent).
- **NO usar gpt-4o como judge** — overkill y caro. gpt-4o-mini es suficiente para clasificación binaria/ternaria.
- **El criterio `expected` puede mencionar tools** (ej. "debe invocar `consultar_faq`") — el judge NO valida tool calls, solo respuesta textual. Para validar tool calls usar query a `sys_tool_calls` post-corrida.
- **Casos manual-only** (que requieren tool calls reales o setup complejo) marcar separado y no incluir en el smoke automatizado.
