# Guía de Testing — [Nombre del Agente] v[N]

**Canal:** [WhatsApp / Instagram DM / Telegram / etc.]
**Prompt versión testeada:** v[X.Y]
**Estado:** Pendiente

---

## ⚠️ Formato obligatorio (compatible con script)

Esta guía es parseada automáticamente por `scripts/testing/run-agent-tests.py`. Las tablas deben usar **exactamente** los formatos siguientes — sin columnas adicionales, sin columnas faltantes:

**Casos simples** (un solo turno):
```
| # | Mensaje | Resultado esperado |
|---|---------|-------------------|
| 1 | `mensaje del lead` | qué debe responder el agente |
```

**Flujos multi-turno** (conversación de N turnos):
```
| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `mensaje` | — |
| 2 | Agente | — | qué debe responder |
| 3 | Usuario | `mensaje` | — |
| 4 | Agente | — | qué debe responder |
```

**Reglas de formato:**
- Columnas permitidas: SOLO las que aparecen en los formatos arriba. No agregar `Área`, `Flujo`, `OK`, `Resultado obtenido`, `{{ORIGEN}}` ni ninguna otra.
- `—` en "Resultado esperado" de turno Agente: cualquier respuesta es aceptable (no se evalúa con criterio estricto).
- `—` en "Mensaje" de turno Agente: el agente responde al historial acumulado (no enviar mensaje adicional).
- El script genera `*-auto-results.md` con los resultados. No completar manualmente las columnas de resultados.
- Si una herramienta n8n aparece en "Resultado esperado" como `[NOMBRE_HERRAMIENTA]` (mayúsculas + guiones bajos), el caso se clasifica como `manual-only` y va a `*-manual.md`.

---

## Criterios de calidad del resultado esperado

- **Reglas absolutas (SIEMPRE / NUNCA):** incluir al menos 1 caso con un trigger no-canónico (el mensaje que podría hacer que el agente interprete la regla como opcional) + al menos 1 ítem negativo ("NO hace X", "la frase Y NO aparece").
- **Ítems de contenido obligatorio:** listar el ítem exacto que debe aparecer, no la categoría. Correcto: `menciona "clases en vivo" textualmente`. Incorrecto: `menciona los pilares del programa`.
- **Variables n8n:** si el system prompt contiene variables como `{{ORIGEN}}`, el skill las reemplaza con valores de testing antes de ejecutar el script (ej. `{{ORIGEN}}` → `directo`). No incluir columnas de variables en las tablas.

---

## Casos simples

Casos de un solo turno para validar comportamientos puntuales.

| # | Mensaje | Resultado esperado |
|---|---------|-------------------|
| 1 | `` | |
| 2 | `` | |
| 3 | `` | |
| 4 | `` | |

> Casos simples sugeridos por categoría:
> - Saludo y apertura (trigger canónico: "Hola")
> - Apertura con mensaje no-canónico — si el agente tiene regla de apertura, agregar un caso donde el primer mensaje del lead es una pregunta directa (precio, info, urgencia) para verificar que la regla se respeta igual
> - Consulta directa sobre precio
> - Pregunta fuera de scope
> - FAQ específica del negocio (con datos reales del cliente)
> - Garantía de resultados o promesas exageradas

---

## Flujos conversacionales

Secuencias de varios turnos. Cada flujo va con su propio heading `### Flujo X — [nombre]` para que el parser lo identifique como un caso separado.

---

### Flujo 1 — [nombre descriptivo]

**Objetivo:** [Qué comportamiento se valida]
**Perfil del lead:** [nunca_emprendo / ya_vende / etc.]

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `` | — |
| 2 | Agente | — | [qué debe responder] |
| 3 | Usuario | `` | — |
| 4 | Agente | — | [qué debe responder] |

---

### Flujo 2 — [nombre descriptivo]

**Objetivo:** [Qué comportamiento se valida]
**Perfil del lead:** [nunca_emprendo / ya_vende / etc.]

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `` | — |
| 2 | Agente | — | [qué debe responder] |
| 3 | Usuario | `` | — |
| 4 | Agente | — | [qué debe responder] |

---

> Flujos sugeridos por categoría — incluir mínimo uno por cada uno que aplique al agente:
>
> - Diagnóstico completo: de consulta vaga a captura de datos + propuesta
> - Derivación directa: usuario que pide hablar con alguien desde el inicio
> - Lead muy verde: no está listo para comprar → nutrir
> - Cierre sin decisión: lead que necesita tiempo → follow up
> - Objeción "no tengo plata"
> - Objeción "lo tengo que pensar"
> - Usuario hostil o impaciente
> - Descalificación: lead que no aplica al perfil
> - Flujo por segmento especial (si el negocio tiene perfiles distintos)

---

> Guía de testing v[N] para [Nombre del Agente]. Correcciones aplicadas en el prompt v[X.Y].
