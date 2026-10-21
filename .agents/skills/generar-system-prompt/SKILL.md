---
name: generar-system-prompt
description: >
  Usar este skill cuando el usuario quiera crear o mejorar un system prompt para un agente
  de IA en n8n. Se activa con frases como "crear system prompt", "generar prompt para el
  agente de X", "necesito el prompt para el bot de Y", "escribir instrucciones para el agente",
  o cuando el usuario comparte un archivo CSV del formulario de onboarding de Typeform.
  También se activa cuando el usuario indica que el cliente ya respondió los datos faltantes
  y hay que completar el prompt.
  Produce el prompt completo en bloque de código, listo para copiar y pegar.
---

# Skill: Generar System Prompt

## Descripción

Toma la información del proyecto (del formulario de onboarding en CSV, del cliente, o
provista directamente) y genera un system prompt completo y optimizado para un agente
conversacional en n8n.

La salida es siempre un bloque de código markdown listo para copiar y pegar directamente
en el nodo de IA de n8n.

---

## Recursos de Referencia

- **Template base:** `_core/templates/agents/SYSTEM_PROMPT_TEMPLATE.md`
- **Guía de principios:** `_core/standards/system-prompt-engineering.md`
- **Ejemplos de prompts producción:** `_core/prompts/agents/`
- **Template workflow Telegram v1:** `_core/templates/workflows/agente-telegram/`

---

## Flujo Normal: CSV del Formulario Typeform

El flujo estándar de onboarding es:
1. El cliente realiza el pago del 50%
2. Se le envía el formulario por Typeform
3. Una vez respondido, se descarga el CSV y se comparte con Codex
4. **Fase 1** — se genera el System Prompt v1 + mensaje de datos faltantes para el cliente
5. El cliente responde con los datos faltantes
6. **Fase 2** — se completa el prompt a v1.1 + se genera la guía de testing

---

## FASE 1 — Recepción del CSV

Se activa cuando el usuario comparte el CSV del formulario.

### Paso 1.1 — Leer el CSV y detectar gaps

Leer y parsear el CSV completo. Identificar qué información está presente y qué falta.

**Siempre disponible en el CSV** (estructura y comportamiento del agente):
- Nombre comercial, perfil del cliente, tono y personalidad
- Proceso de consulta, preguntas de calificación, cuándo derivar
- Horarios, zonas geográficas, datos a recolectar
- Canal de notificación al equipo

**Frecuentemente faltante** (contenido de la base de conocimiento):
- Listado detallado de productos/equipos con características
- Precios o rangos de precios
- URL de tienda online / links relevantes
- FAQs específicas que no están en el formulario
- Detalles de showroom, financiación, garantía, servicio técnico

### Paso 1.2 — Leer recursos de referencia

Leer:
- `_core/templates/agents/SYSTEM_PROMPT_TEMPLATE.md` → estructura
- `_core/standards/system-prompt-engineering.md` → principios

Si hay archivos adicionales adjuntos (guion de ventas, catálogo, etc.), leerlos también.

### Paso 1.3 — Redactar el System Prompt v1

Redactar el prompt completo con lo que hay. Reglas:

- **Español rioplatense** salvo que el CSV/cliente indique otro estilo
- **Secciones obligatorias**: Rol e Identidad, Personalidad y Tono, Objetivo Principal,
  Flujo de Conversación, Instrucciones Operativas, Base de Conocimiento, Reglas Críticas
- **Secciones opcionales**: incluirlas solo si aplican (Calificación, Formato, Escalada)
- **Sin placeholders no vitales**: si un dato no es esencial para que el agente funcione
  (ej: nombre del agente, URL de tienda), omitir esa parte completamente. Solo usar
  `[PENDIENTE: descripción]` para datos que bloquean el funcionamiento real.
- **Reglas críticas**: usar "NUNCA" y "SIEMPRE" explícitamente
- **Tono**: incluir ejemplos concretos de mensajes correctos e incorrectos

#### V1: siempre sin tools reales

La primera versión del prompt es **solo conversacional**. No incluir herramientas
(`notificar_lead`, `registrar_lead`, etc.) en el nodo de IA.

Si el flujo requiere escalada, usar un **mensaje de texto proxy**:

```
Cuando necesites derivar la conversación a un representante humano, enviá exactamente
este mensaje: "[texto acordado]"
```

Las tools reales se agregan en versiones posteriores una vez validado el comportamiento.

### Paso 1.4 — Output Fase 1: System Prompt v1

Presentar el prompt dentro de un bloque de código:

````markdown
```
[PROMPT COMPLETO AQUÍ]
```
````

### Paso 1.5 — Output Fase 1: Mensaje para el cliente con datos faltantes

Inmediatamente después del prompt, generar el mensaje para enviarle al cliente por WhatsApp
pidiendo los datos que faltan para completar la base de conocimiento del agente.

**Formato**: bullets cortos, tono informal, listos para copiar y pegar.
**Criterio**: solo incluir lo que realmente enriquece o bloquea el agente — no sobrecargar al cliente.

```
Hola [Nombre]! Ya tenemos el borrador del agente armado con las respuestas del formulario.
Para dejarlo completo, necesitamos algunos datos más:

• [Dato faltante 1 — ser específico: ej. "Listado de equipos con nombre, tecnología y aplicación principal"]
• [Dato faltante 2]
• [Dato faltante 3]

Con eso ya podemos dejarlo listo para las primeras pruebas.
```

Adaptar al proyecto. Mencionar al responsable si el CSV lo indica (ej: "esto lo tiene Edgardo").

### Paso 1.6 — Guardar Fase 1 (si hay cliente asociado)

```
clients/[CLT###_Nombre]/04_agents/[nombre-agente]-system-prompt.md  ← prompt v1
```

Usar el formato de `_core/prompts/agents/outreach-ig-system-prompt.md` como referencia
(incluir versión v1.0, fecha, notas de calibración, sección "Pendientes para v1.1").

Ejecutar `cliente-sync`.

---

## FASE 2 — Recepción de datos faltantes del cliente

Se activa cuando el usuario indica que el cliente respondió con los datos faltantes.

### Paso 2.1 — Leer el prompt v1 existente

Leer `clients/[CLT###_Nombre]/04_agents/[nombre-agente]-system-prompt.md`.

### Paso 2.2 — Actualizar la base de conocimiento

Incorporar los datos nuevos del cliente en las secciones correspondientes del prompt.
**No reescribir el prompt completo** — solo actualizar las secciones que tenían gaps
o `[PENDIENTE: ...]`. El comportamiento, tono y flujo del v1 se mantienen intactos.

### Paso 2.3 — Output Fase 2: System Prompt v1.1

Presentar el prompt actualizado completo en bloque de código, con el header de versión
actualizado a `v1.1`.

### Paso 2.4 — Output Fase 2: Guía de Testing

Generar la guía de testing ahora que la base de conocimiento está completa.
Los casos deben ser concretos y específicos al negocio — no genéricos.

**Presentar dentro de un bloque ```markdown```** para pegar directamente en Notion.

Hay dos tipos de casos:

#### Tipo A — Caso simple
Un mensaje → una respuesta. Para validar comportamientos puntuales.

```markdown
## Guía de Testing — [Nombre del Agente] v1.1

**Canal:** Telegram
**Estado:** Pendiente

---

## Casos simples

| # | Mensaje a enviar | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|-------------------|-------------------|----|
| 1 | `[texto exacto]` | [qué debe responder el agente] | | |
```

#### Tipo B — Flujo conversacional
Secuencia de varios turnos. Si el flujo tiene ramas, cada rama va en su propia tabla.

```markdown
### Flujo [N]: [Nombre del flujo]
**Objetivo:** [qué comportamiento se valida]

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `[texto]` | — | | |
| 2 | Agente | — | [qué debe responder] | | |

**Rama A — [nombre]:**

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 3 | Usuario | `[variante A]` | — | | |
| 4 | Agente | — | [resultado esperado] | | |
```

**Qué cubrir** — mínimo un caso por categoría:

Casos simples:
1. Saludo y apertura
2. Consulta sobre precio (según cómo lo maneja el agente)
3. Pregunta fuera de scope
4. FAQ específica del negocio (con datos reales)

Flujos conversacionales:
5. Diagnóstico completo — de consulta vaga a captura de datos
6. Derivación directa — usuario que pide hablar con alguien desde el inicio
7. Usuario hostil o impaciente
8. Cierre sin decisión
9. Flujos con ramas — puntos donde la respuesta del usuario bifurca el comportamiento del agente

Si el CSV menciona segmentos especiales (distribuidores, zonas, tipos de cliente), agregar
un flujo por cada uno.

> Guía de testing inicial (v1.1). Las iteraciones posteriores se gestionan en la fase de testing del cliente.

### Paso 2.5 — Guardar Fase 2

```
clients/[CLT###_Nombre]/04_agents/[nombre-agente]-system-prompt.md  ← actualizar a v1.1
clients/[CLT###_Nombre]/07_testing/testing-guide-v1.md              ← guía de testing
```

Ejecutar `cliente-sync`.

---

## Modo alternativo: sin CSV

Si el usuario describe el proyecto directamente (sin CSV), preguntar en este orden,
una pregunta a la vez:

1. ¿Para qué cliente / proyecto es?
2. ¿Cuál es el objetivo principal del agente?
3. ¿En qué canal opera?
4. ¿Qué tono debe tener?
5. ¿Qué servicios o productos ofrece la empresa?
6. ¿Qué herramientas tiene disponibles en n8n?
7. ¿Hay FAQs o situaciones especiales que el agente debe manejar?

Si el usuario solo da un nombre de cliente, leer `CLIENT_INFO.md` y los archivos en
`04_agents/` del cliente antes de preguntar.

En este modo el flujo de dos fases no aplica — generar prompt + guía de testing en una sola
instancia si hay información suficiente.

---

## Reglas del Skill

- **Fase 1 con CSV**: entregar prompt v1 + mensaje para el cliente. No generar guía de testing todavía.
- **Fase 2 con datos del cliente**: actualizar prompt a v1.1 + generar guía de testing. No reescribir el prompt completo, solo las secciones con gaps.
- **V1 = solo conversacional**: nunca incluir tools reales en la primera versión del prompt.
- **Sin placeholders no vitales**: omitir secciones incompletas del prompt — no dejar `[PLACEHOLDER]` en el texto salvo que bloquee el funcionamiento.
- **Guía de testing en bloque ```markdown```**: para pegar directamente en Notion.
- **Con CSV**: no re-preguntar lo que ya está en el archivo.
- **Sin datos**: preguntar antes de inventar. Nunca inventar precios, productos ni datos del negocio.
- Si hay materiales de referencia adjuntos: leerlos antes de redactar.
- Si el usuario pide "mejorar" un prompt existente: leerlo, identificar brechas según la guía de principios, y proponer la versión mejorada completa.
- Responder en español.
