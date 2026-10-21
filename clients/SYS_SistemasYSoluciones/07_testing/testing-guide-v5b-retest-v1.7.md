# Guía de Testing — Agente Sistemas y Soluciones v1.7

**Versión:** v1.7
**Fecha:** 2026-04-29
**Canal de prueba:** Telegram / WhatsApp
**Estado:** Pendiente de prueba

---

## Re-test v1.7 — Corrección aplicada

Testear en conversación nueva.

---

### Re-test: Cotización directa como primer mensaje (Flujo 14 — Turno 1)

**Fallo en v1.6:** el agente preguntaba por tipo de trabajo antes de pedir datos, incluso cuando el primer mensaje del cliente era una solicitud de cotización.
**Corrección v1.7:** Regla 21 marcada PRIORITARIO — pedir datos directamente incluso en el primer mensaje.

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Quiero una cotización de una DTF` | Pide nombre, teléfono y localidad — sin preguntar por el proyecto — sin "¡Gracias por tu consulta!" | | |
| 2 | Usuario | `Pedro López, 11-5555-4444, Rosario` | Pide mail con frase estándar | | |
| 3 | Usuario | `pedro@mail.com` | Confirma y activa `[NOTIFICAR_LEAD]` + `[REGISTRAR_LEAD]`; cierra con "Cualquier cosa nos avisas, saludos." | | |

---

### Re-test adicional: Cotización con frase diferente

**Objetivo:** verificar que el trigger aplica a variantes de la solicitud.

| # | Mensaje a enviar | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|-------------------|-------------------|----|
| R1 | `¿Cuánto sale un equipo UV?` | Pide nombre, teléfono y localidad — sin diagnóstico previo | | |
| R2 | `Quiero comprar una impresora DTF` | Pide nombre, teléfono y localidad — sin diagnóstico previo | | |

---

**Corrección aplicada en v1.7:** Regla 21 reforzada — PRIORITARIO, cubre primer mensaje, elimina condición "sin hacer preguntas técnicas previas" que generaba ambigüedad.

> Guía de testing v1.7 — re-test del único fallo de v1.6 (Flujo 14.1: cotización directa).
