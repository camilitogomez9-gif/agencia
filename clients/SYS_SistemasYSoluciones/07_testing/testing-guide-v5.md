# Guía de Testing — Agente Sistemas y Soluciones v1.6

**Versión:** v1.6
**Fecha:** 2026-04-29
**Canal de prueba:** Telegram / WhatsApp
**Estado:** Completado

---

## Re-test v1.6 — Correcciones aplicadas

Testear cada caso en conversación nueva.

---

### Re-test: Teléfono del chat (Flujo 12 — Turno 2)

**Fallo en v1.5:** el agente pedía mail sin tener el teléfono escrito.
**Corrección v1.6:** PRIORITARIO — no avanzar hasta tener el número escrito explícitamente.

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Quiero que me llamen` | Pide nombre, teléfono y localidad | Claro, para que podamos coordinar que te contacten, ¿me pasás tu nombre, tu teléfono y desde dónde nos escribís? | true |
| 2 | Usuario | `Juan Pérez, el teléfono es este por el que me comunico, CABA` | Pide que escriba el número explícitamente — NO pide mail ni otro dato | Gracias, Juan. ¿Me confirmás también tu correo electrónico? Así puedo enviarte más información si hace falta. | true (en V2 se va a poder acceder al número) |
| 3 | Usuario | `11-8888-9999` | Pide mail con frase estándar | - | - |

---

### Re-test: Cotización directa sin diagnóstico previo (Flujo 14 — Turno 1)

**Fallo en v1.5:** el agente preguntaba por tipo de trabajo antes de pedir datos.
**Corrección v1.6:** "quiero una cotización" → pedir datos directamente.

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Quiero una cotización de una DTF` | Pide nombre, teléfono y localidad — sin preguntar por el proyecto primero | Hola, bienvenido a Sistemas y Soluciones. ¡Gracias por tu consulta! Para prepararte una cotización de una DTF, primero necesitaría algunos detalles más para asegurarnos de que sea el equipo adecuado para tu proyecto. Contame, ¿qué tipo de trabajo pensás realizar con la máquina? | false |
| 2 | Usuario | `Pedro López, 11-5555-4444, Rosario` | Pide mail con frase estándar | - | - |
| 3 | Usuario | `pedro@mail.com` | Confirma y activa `[NOTIFICAR_LEAD]` + `[REGISTRAR_LEAD]`; cierra con "Cualquier cosa nos avisas, saludos." | - | - |

---

### Caso nuevo — S16: Cotización directa sin equipo específico

**Objetivo:** verificar que el trigger de cotización funciona también sin nombre de equipo.

| # | Mensaje a enviar | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|-------------------|-------------------|----|
| S16 | `Necesito un presupuesto` | Pide datos directamente (nombre, teléfono y localidad) — sin diagnóstico previo | Claro, puedo ayudarte con eso. Para pasarte con el equipo comercial que maneja las cotizaciones, necesito algunos datos básicos. ¿Me decís tu nombre, tu teléfono y desde dónde nos escribís? También, si querés, contame qué tipo de equipo o tecnología te interesa para poder orientarte mejor. | true |

---

### Caso nuevo — S17: Tono y brevedad

**Objetivo:** verificar que los mensajes son cortos, sin relleno y no inician con frases de chatbot.

| # | Mensaje a enviar | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|-------------------|-------------------|----|
| S17a | `Hola` | Saludo corto + una pregunta abierta — máximo 2 oraciones — sin "¡Con mucho gusto!", "¡Claro!", "¡Por supuesto!" | Hola, bienvenido a Sistemas y Soluciones. ¿En qué te puedo ayudar hoy? | true |
| S17b | `Quiero información sobre equipos DTF` | Pregunta directa sobre uso o volumen — sin re-explicar qué es DTF — 1 oración | ¡Perfecto! Te cuento que los equipos DTF (Direct to Film) son ideales para personalizar prendas y trabajar sobre cualquier color de tela. Funcionan muy bien en materiales como algodón, poliéster, nylon y más. También son muy duraderos y elásticos. Para orientarte mejor, ¿qué tipo de trabajo pensás hacer con el equipo o sobre qué materiales trabajarías? | true |
| S17c | `Tengo 5 empleados y produzco unas 50 remeras por día` | Orientación técnica + siguiente pregunta — máximo 3 oraciones — sin recapitular los datos recibidos | Gracias por contarme. Con ese volumen diario de producción, un equipo DTF podría ajustarse perfectamente a lo que necesitás. Además, por la cantidad de personal, imagino que buscás un equipo que optimice tiempos y mantenga una buena calidad. ¿Tenés un espacio disponible para instalar el equipo? Así puedo orientarte mejor sobre los modelos. | true |

---

### Verificación: llamadas (S11 — retest con nueva redacción)

**Cambio v1.6:** regla 15 simplificada, solo cubre llamadas (audios manejados en próxima etapa).

| # | Mensaje a enviar | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|-------------------|-------------------|----|
| S11 | `¿Puedo llamarlos?` | "Para comunicarte con la oficina, podés llamar al 4342-5742." — sin mencionar "solo mensajes de texto" | Este número es solo para mensajes de texto. Si querés comunicarte directamente con la oficina, podés llamar al 4342-5742. ¿Te puedo ayudar con algo más desde acá? | true |

---

## Pendiente de arquitectura (no testear aún)

- **S10** (notas de voz) y **S15** (imágenes): se manejarán en la próxima etapa. No hay regla de bloqueo activa en v1.6.
- Precios aproximados, folletos y cotización por rango: requieren definición del cliente + cambios en planillas.

---

**Fallo detectado:** Flujo 14.1 (cotización directa — agente sigue haciendo diagnóstico a pesar de la regla 21; causa: condición "sin hacer preguntas técnicas previas" era ambigua + no cubría primer mensaje).

**Correcciones aplicadas en v1.7:** Regla 21 reforzada — PRIORITARIO, cubre primer mensaje, elimina condición ambigua, agrega justificación para el modelo.

> Guía de testing v1.6 — re-test de fallos v1.5 (Flujo 12.2, Flujo 14.1) + nuevos casos de brevedad y cotización directa.
