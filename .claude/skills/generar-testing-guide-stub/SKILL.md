---
name: generar-testing-guide-stub
description: >
  Usar este skill cuando hay que generar el stub de testing-guide para un agente
  conversacional Etapa 2 (casos simples + flujos multi-turno cubriendo tool
  calling, memoria persistente, NOT_FOUND, multi-canal, reglas operativas
  críticas). Se activa con frases como "armar testing guide de X", "stub de
  testing para X", "casos de prueba para el agente X", "F7 testing cliente X".
  Genera plantilla en `07_testing/testing-guide-v{N}.md`.
---

# Skill: Generar Testing Guide Stub Agente Etapa 2

## Descripción

Genera el stub de testing-guide para validar end-to-end un agente Etapa 2 con tools, memoria y multi-canal. **No corre los tests** — solo arma la grilla. Para correr: `smoke-test-agente-webhook` (S5) sobre los casos simples + manual sobre los flujos.

**Estructura validada en SYS testing-guide-v6:**

1. **Casos simples (~18):** 1 turno, foco en una capacidad por caso (tool X funciona, memoria persiste, NOT_FOUND honesto, etc.)
2. **Flujos multi-turno (~16):** 3-6 turnos, simulan conversaciones reales (consulta inicial → ambiguity → resolución → propuesta de derivación)
3. **Cobertura:**
   - Tool calling (cada tool invocada al menos 1 vez)
   - Memoria persistente cross-turn (recordar nombre, preferencia, contexto)
   - NOT_FOUND anti-alucinación (tool dice NOT_FOUND → agente NO inventa)
   - Multi-canal (mensaje desde IG vs WA — comportamiento idéntico)
   - Reglas operativas críticas (las top 5-7 del prompt)

---

## Cuándo invocarlo

- F7 del Plan Maestro Etapa 2
- Antes de iterar el prompt v2.x (necesitamos una guía contra qué medir)
- Cuando se agrega una tool nueva (extender el guide)

## Cuándo NO invocarlo

- Cliente Etapa 1 sin tools — usar `testing-guide-template.md` simple, no este
- Solo se cambió 1 línea del prompt — re-correr casos existentes, no generar nuevos

---

## Inputs requeridos

1. **Cliente ID + nombre**
2. **Lista de tools** con su contrato (RESOLVED/AMBIGUOUS/NOT_FOUND/ERROR)
3. **Reglas operativas críticas** del system prompt (las top 5-7)
4. **Canales activos** (WA / IG / FB / Telegram)
5. **Catálogo / dominio** (productos, FAQs, etc.) para construir casos realistas

---

## Proceso

### Paso 1 — Generar el doc base

Path: `clients/{XXX}_{Nombre}/07_testing/testing-guide-v{N}.md`

Base: `_core/templates/agents/testing-guide-template.md` + cobertura SYS v6.

Si ya existe v{N-1}, leer y heredar los casos que sigan vigentes. **Versionar el archivo viejo antes de sobrescribir.**

### Paso 2 — Casos simples (18 típicos)

Estructura por caso:

```markdown
### Caso 1: Saludo inicial
- **Input:** "hola"
- **Resultado esperado:** Saludo cordial, presentación del rol del agente, pregunta abierta de cómo puede ayudar
- **Verificación:** ✓ Tono coincide con prompt, ✓ NO usa nombre del cliente al saludar genérico, ✓ NO pide datos antes de ofrecer ayuda
```

Plantilla de cobertura:

| # | Capacidad | Ejemplo |
|---|---|---|
| 1 | Saludo inicial | "hola" |
| 2 | Out-of-scope | "qué tiempo hace en Tokio" |
| 3 | Tool A resuelve | input que dispara tool A con argumento claro |
| 4 | Tool A AMBIGUOUS | input ambiguo que dispara tool A pero retorna AMBIGUOUS |
| 5 | Tool A NOT_FOUND anti-alucinación | input que dispara tool A con valor inexistente — agente NO inventa |
| 6 | Tool B resuelve | input que dispara tool B |
| 7 | Tool C resuelve | input que dispara tool C |
| 8 | Tool de notificación dispara | input claro de "quiero hablar con humano" |
| 9 | Memoria intra-turn | "soy Juan, quiero X" → en mismo turno, agente usa nombre |
| 10 | Pedido de precio sin datos | "cuánto sale?" sin contexto |
| 11 | Pedido con typo | "tengo intres en X" (typo intencional) |
| 12 | Mensaje muy largo | párrafo de 5 líneas con info dispersa |
| 13 | Mensaje muy corto | "?" |
| 14 | Idioma alternativo si aplica | "i need help in english" → respuesta en español según regla |
| 15 | Reglas operativas: regla 1 | input que prueba la regla 1 del prompt |
| 16 | Reglas operativas: regla 2 | input que prueba la regla 2 |
| 17 | Reglas operativas: regla 3 | input que prueba la regla 3 |
| 18 | NOT_FOUND retorna respuesta honesta | input que fuerza NOT_FOUND — verificar respuesta acorde |

### Paso 3 — Flujos multi-turno (16 típicos)

Estructura por flujo:

```markdown
### Flujo 1: Discovery + Tool A + Propuesta
- **Turno 1 (usuario):** "hola, busco X"
- **Turno 1 (esperado):** Saludo + pregunta de detalle
- **Turno 2 (usuario):** "es para [contexto]"
- **Turno 2 (esperado):** Tool A invocada → respuesta con resultados
- **Turno 3 (usuario):** "y tienen [variante]?"
- **Turno 3 (esperado):** Tool A invocada con nuevo arg → resultado o NOT_FOUND honesto
- **Turno 4 (usuario):** "quiero hablar con alguien"
- **Turno 4 (esperado):** Tool de notificación invocada → mensaje de confirmación
```

Plantilla de cobertura:

| # | Foco |
|---|---|
| 1 | Discovery + Tool A + Propuesta |
| 2 | Memoria cross-turn (turno 1 dice nombre → turno 4 lo usa) |
| 3 | Cambio de tema mid-conversación (de producto X a producto Y) |
| 4 | Ambigüedad → repregunta → resolución |
| 5 | NOT_FOUND mid-flow → agente NO inventa, propone alternativas |
| 6 | Compatibilidad / cross-sell (tool de compatibilidad) |
| 7 | Multi-canal: mismo flow en WA vs IG (comportamiento idéntico) |
| 8 | Mensaje fuera de scope a mitad de flow → vuelve al foco |
| 9 | Lead frio → progresa a tibio → cálido (regla del prompt) |
| 10 | Lead que da info muy desordenada → agente organiza |
| 11 | Lead que pide derivación directa sin discovery → agente honra |
| 12 | Lead que rechaza una propuesta → agente ofrece alternativa |
| 13 | Lead que pregunta "y si esto otro?" → tool con nuevo arg |
| 14 | Lead que pide info que NO está en KB → NOT_FOUND honesto + sugerir derivar |
| 15 | Lead silencioso (mensajes de 1-2 palabras) → agente sostiene engagement |
| 16 | Lead que da datos completos en turno 1 → agente NO pide redundancia |

### Paso 4 — Tabla de cobertura

Al final del doc, tabla de qué cubre cada caso/flujo:

```markdown
## Cobertura

| Capacidad | Casos | Flujos |
|---|---|---|
| Tool A | 3, 4, 5 | 1, 3, 12 |
| Tool B | 6 | 4 |
| Tool C | 7 | 6 |
| Tool notificación | 8 | 11 |
| Memoria persistente | 9 | 2, 9 |
| NOT_FOUND anti-alucinación | 5, 18 | 5, 14 |
| Multi-canal | — | 7 |
| Reglas operativas | 15-17 | varias |
```

### Paso 5 — Sección "Cómo correr"

```markdown
## Cómo correr

**Casos simples:** automatizables con `scripts/testing/test-{cliente_id_lower}-webhook-quick.py`
**Flujos multi-turno:** manuales en n8n con `manualChatTrigger` o via webhook test mode

**Criterio de pase:** ≥90% true (los casos `[NOMBRE_HERRAMIENTA]` requieren verificación manual de invocación de tool).
```

### Paso 6 — Reportar al usuario

Output:
- Path del testing-guide
- N casos + N flujos
- Cobertura por capacidad (tabla)
- Sugerir: correr `smoke-test-agente-webhook` (S5) sobre los simples primero

---

## Composición

**Invoca:** ninguno.
**Es invocado por:** F7 del Plan Maestro.
**Complementa:** `smoke-test-agente-webhook` (S5), `iterar-prompt`.

---

## Notas operativas

- **Tiempo:** 15-25 min del skill.
- **Versionar el guide** con `v{N}.md`. Cada vez que se agregan capacidades, nuevo número.
- **Heredar lo que sigue siendo válido** de v{N-1} — no generar de cero si ya hay base.
- **Los casos deben ser realistas al cliente** — usar productos, marcas, lenguaje del Excel/catálogo real, no genéricos.
