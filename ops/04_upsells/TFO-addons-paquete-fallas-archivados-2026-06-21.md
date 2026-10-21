# TFO — Add-ons archivados del paquete agente de fallas v2

**Fecha:** 2026-06-21
**Cliente:** TFO — TOFO Pizza · Mauricio García de la Vega
**Estado:** archivados (no en la propuesta v2 actual, disponibles para reactivar si Mauricio los pide)
**Contexto:** la propuesta v1 (USD 1.798, 14/6/26) listaba 4 add-ons explícitos. La v2 (USD 360, 21/6/26) los quitó del menú para simplificar la conversación con Mauricio. Este doc los preserva con sus números y argumentos por si en algún momento Mauricio los pregunta o aparece una necesidad concreta.

---

## Cuándo reactivar cada add-on

| Add-on | Trigger que justifica re-proponerlo |
|---|---|
| Tool de escalamiento real (Telegram o WhatsApp template al técnico) | Mauricio o un cliente final pide que el agente no solo instruya por texto sino que dispare notificación directa al técnico humano. **Nuevo en v2** — se quitó del paquete base. |
| Implementación llave en mano | Mauricio dice "tengo un cliente que necesita arrancar ya y no tengo tiempo para implementar yo" — la agencia hace el setup completo en la infra de ese cliente final puntual y Mauricio mira para replicar después. |
| Mantenimiento mensual | Mauricio ya tiene 2-3 clientes finales en producción y quiere tener una sola línea de fixes/mejoras transversales para todos a la vez en lugar de cotizar puntual cada vez que surge algo. |
| Multi-idioma (inglés / portugués) | Mauricio cierra un cliente final fuera de México (Brasil, USA, etc.) y necesita el prompt + testing guide + diagrama adaptado al idioma local. |
| Capacitación profunda en plataformas | Mauricio o el implementador del lado del cliente final quieren un curso 1:1 sobre n8n o sobre WhatsApp Cloud API porque van a operar varios clientes finales y necesitan dominio técnico real, no solo seguir el README. |

---

## 0. Tool de escalamiento real (Telegram / WhatsApp template al técnico)

**Qué es:** sumar al workflow un nodo de escalamiento que dispare notificación directa al técnico humano cuando el agente detecta caso fuera de scope o el cliente exige humano. 2 variantes:
- **Variante A — Telegram:** nodo HTTP a bot Telegram del técnico, con resumen estructurado de la conversación. Gratis para el cliente final.
- **Variante B — WhatsApp template al técnico:** template MARKETING o UTILITY aprobado en Meta, disparado vía WhatsApp Cloud API al número del técnico. Costo ~USD 0.01-0.10/mensaje según país.

**Cuándo conviene:** cliente final con volumen alto de fallas donde "instruir al cliente final por texto" no escala, o donde el técnico necesita pull notification proactiva en lugar de esperar que el cliente lo llame.

**Precio sugerido:**
- **USD 80** Variante A (Telegram)
- **USD 120** Variante B (WhatsApp template — incluye guía para aprobar el template en Meta)

**Tiempo la agencia estimado:** 1 hora (A) / 1.5 horas (B, suma armado de template).

**Lo que NO incluye:** crear el bot Telegram del técnico (Mauricio o el cliente final lo crean en 5 min), aprobación del template en Meta (Mauricio espera la aprobación, suele tardar 24-48h).

---

## 1. Implementación llave en mano (por cliente final)

**Qué es:** la agencia hace el setup completo del agente contra la infraestructura de UN cliente final específico. Incluye: configuración WhatsApp Cloud API + verificación número Meta + import del JSON al n8n del cliente final + reconexión de credenciales + llenar placeholders del prompt con datos reales + smoke test E2E + handoff de 30 min con el dueño del cliente final.

**Cuándo conviene:** primer cliente final (Mauricio quiere ver cómo se hace para replicar después solo), o cliente final con cero capacidad técnica donde Mauricio no quiere meterse, o cliente final con urgencia y Mauricio no tiene bandwidth.

**Precio sugerido:**
- **USD 400** primer cliente final (descuento "vení mirá cómo se hace")
- **USD 500** cliente final segundo en adelante

**Tiempo la agencia estimado:** 4-6 horas reales por cliente final.

**Lo que NO incluye:** soporte post-launch al cliente final (eso lo hace Mauricio), capacitación al dueño/personal del cliente final, garantía permanente.

---

## 2. Mantenimiento mensual del paquete

**Qué es:** retainer mensual fijo que cubre:
- Fixes ilimitados de bugs reproducibles del paquete original
- 2 horas/mes de mejoras menores transversales (cambios al prompt, ajustes al workflow, nueva tool simple) que aprovechan TODOS los clientes finales de Mauricio a la vez
- Canal preferente WhatsApp para reportar issues
- 1 sync mensual de 30 min Zoom para revisar evolución

**Cuándo conviene:** cuando Mauricio tiene 2-3 clientes finales en producción y quiere centralizar el soporte técnico en la agencia en lugar de pedirle cosas a su dev de forma puntual.

**Precio sugerido:** **USD 120/mes** (compromiso mínimo 3 meses, después mes a mes).

**Lo que NO incluye:** features nuevas grandes (cotizables aparte), implementación por cliente final, soporte directo al cliente final de Mauricio.

---

## 3. Adaptación multi-idioma

**Qué es:** versión del paquete completo (prompt + README + 3 casos de smoke) adaptada a otro idioma. Incluye revisión de modismos del idioma destino, no traducción literal.

**Cuándo conviene:** Mauricio cierra un cliente final fuera de México que opera en inglés (USA) o portugués (Brasil).

**Precio sugerido:** **USD 400/idioma**. Si se piden 2 idiomas juntos, USD 700 los dos.

**Tiempo la agencia estimado:** 4-5 horas por idioma.

**Lo que NO incluye:** localización de la infra de WhatsApp Cloud API (eso es trabajo del cliente final), validación contra hablantes nativos profesionales.

---

## 4. Capacitación profunda en plataformas

**Qué es:** sesión 1:1 Zoom de 90 min con Mauricio o su dev sobre alguna plataforma específica del stack (n8n, WhatsApp Cloud API, OpenAI tooling, Telegram bots). Incluye grabación + Loom complementario si quedan dudas no resueltas.

**Cuándo conviene:** Mauricio o su dev quieren dominio real para operar 5+ clientes finales sin depender de la agencia para cada duda técnica.

**Precio sugerido:** **USD 250/sesión 90 min** (incluye grabación + Loom de seguimiento si hace falta).

**Lo que NO incluye:** curso estructurado de muchas horas (eso ya existe en plataformas como Academy de n8n o docs de Meta — la agencia no compite con eso), certificación.

---

## Notas comerciales internas

- Estos add-ons NO van listados en la propuesta v2 para no diluir el SÍ a USD 360. La conversación se mantiene simple: "esto es lo que entregamos por USD 360, todo lo demás se cotiza puntual."
- Si Mauricio pregunta por alguno espontáneamente, le doy el número de acá directo sin nueva ronda de discovery.
- Estos números son **referencia 2026-06-21** — si pasan 6 meses sin reactivarse, revisar tarifas antes de reusarlos.
- El add-on más probable de aparecer primero es **tool de escalamiento real** — Mauricio o el primer cliente final implementador van a notar rápido que "instruir por texto al cliente final que llame al técnico" no escala. USD 80-120 sale natural en esa primera semana post-implementación.
- El segundo más probable es **implementación llave en mano para el primer cliente final** — Mauricio mencionó en la llamada del 12/6 que tiene 1-2 clientes en pipeline concreto. Si activa el paquete v2 y luego pide "hacelo vos al primero", ese USD 400 sale natural.
- El tercero más probable es **mantenimiento mensual** una vez que tenga ≥2 clientes finales operando.
