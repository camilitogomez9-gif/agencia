# Propuesta: Migración Bot de Confirmación a GoHighLevel

**Cliente:** Cereza Invest — Maxi Robles
**Fecha:** 2026-05-16
**Proyecto:** Bot de confirmación de agendas (migración Calendly → GHL)

---

## Contexto

Cereza Invest tiene un bot de confirmación de agendas operativo en n8n que actualmente se dispara desde Calendly y envía mensajes vía Evolution API. Tras la migración a GoHighLevel (GHL), necesitan que el bot funcione dentro del ecosistema GHL + AppLevel, donde los mensajes salen desde el número de cada Closer asignado.

**Sistema actual (construido por la agencia):**
- Trigger: Calendly (invitee.created)
- IA: GPT-4.1 + PostgreSQL (memoria conversacional)
- WhatsApp: Evolution API (instancia única)
- CRM: Chatwoot (etiquetas, pausas, búsqueda de contactos)
- Lógica: segmentación horaria, 4 tipos de sesión, pausa manual, reagendas
- Sub-workflows: Caso 1, Caso 2, Esperar y Alertar

**Lo que cambia:**
- Trigger: GHL reemplaza a Calendly
- Canal: AppLevel (vía "Send SMS" en GHL) reemplaza a Evolution API
- CRM: GHL Custom Fields reemplazan a Chatwoot
- Nuevo: Recordatorio 24h (no existe hoy)

---

## Alcance técnico detallado

### Lo que implica la migración:

| # | Tarea | Detalle |
|---|---|---|
| 1 | Nuevo trigger GHL | Workflow en GHL: Customer Reply → Webhook a n8n con datos del lead + closer |
| 2 | Remapeo de data model | El workflow actual extrae datos de payload Calendly (~15+ referencias). Hay que remapear cada una al formato GHL |
| 3 | Migración CRM | Reemplazar llamadas a API de Chatwoot por GHL API (etiquetas `ya_agendo`, `reagenda`, atributo de pausa) |
| 4 | Canal de salida | Reemplazar Evolution API por GHL API "Send SMS" (AppLevel convierte a WhatsApp desde el # del closer) |
| 5 | Recordatorio 24h | Nuevo workflow de reminder que no existe actualmente |
| 6 | Adaptación sub-workflows | Los flujos de IA (Caso 1, Caso 2) necesitan recibir y devolver datos en formato GHL |
| 7 | Lógica de pausa | Migrar de Chatwoot custom_attribute a GHL Custom Field (checkbox "Pausar Bot") |
| 8 | Testing | Pruebas end-to-end con datos reales, verificación de ruteo por closer |
| 9 | Documentación | Video Loom: cómo dar de alta un nuevo Closer |

---

## Opciones de presupuesto

### Opción A — Migración completa (recomendada)

Todo lo que pide el documento de Notion, ejecutado sobre la infraestructura existente en n8n.

| Componente | Horas est. |
|---|---|
| Setup GHL + webhook trigger | 0.5h |
| Remapeo data model (main + subs) | 1-1.5h |
| Migración CRM (Chatwoot → GHL API) | 1.5h |
| Canal de salida (EVO → GHL/AppLevel) | 0.5-1h |
| Recordatorio 24h | 0.5h |
| Testing end-to-end | 2-3h |
| Loom tutorial | 0.5h |
| **Total estimado** | **7-9h** |

**Precio cerrado: USD $1,200**

**Incluye:**
- Todo el alcance del documento de Notion
- Bot funcionando con IA + memoria (ya existe, se adapta)
- Segmentación horaria (ya existe, se adapta)
- Pausa manual vía checkbox en GHL
- Anti-falso-positivo (ya existe en prompt)
- Mensajes desde el número de cada Closer vía AppLevel
- Recordatorio 24h (nuevo)
- Video tutorial Loom para alta de nuevos Closers
- 30 días de soporte post-lanzamiento (corrección de bugs)

**No incluye:**
- Cambios en el prompt de la IA (se mantiene el actual validado)
- Costos de APIs (OpenAI, n8n hosting, AppLevel)
- Soporte extendido más allá de 30 días

---

### Opción B — Integración mínima

Solo se conecta el trigger de GHL al bot existente y se configura la respuesta vía GHL API. Se mantiene la mayor parte de la infraestructura actual.

| Componente | Horas est. |
|---|---|
| GHL webhook → n8n (trigger) | 0.5h |
| Remapeo data model mínimo | 0.5h |
| Respuesta vía GHL API (AppLevel) | 0.5-1h |
| Recordatorio 24h | 0.5h |
| Testing básico | 1.5-2h |
| **Total estimado** | **3.5-4.5h** |

**Precio cerrado: USD $600**

**Incluye:**
- Bot disparado desde GHL (Customer Reply trigger)
- Respuestas enviadas vía AppLevel desde el # del Closer
- Recordatorio 24h
- IA + memoria conversacional (ya existente)
- 15 días de soporte post-lanzamiento

**No incluye:**
- Migración completa de Chatwoot a GHL (se mantiene Chatwoot para tracking interno)
- Video tutorial Loom
- Segmentación por tipo de sesión en GHL (se mantiene lógica actual)
- Soporte extendido

---

## Comparación rápida

| | Opción A | Opción B |
|---|---|---|
| Precio | USD $1,200 | USD $600 |
| Tiempo de entrega | 1-2 semanas | 1 semana |
| Todo centralizado en GHL | Si | Parcial |
| Loom tutorial | Si | No |
| Soporte post-lanzamiento | 30 días | 15 días |
| Reminder 24h | Si | Si |
| Requiere Chatwoot activo | No | Si |

---

## Sobre los 90 días de soporte

El documento de Notion menciona 90 días de soporte post-lanzamiento. Esto excede lo estándar para un proyecto de integración. Si se requiere soporte extendido, se ofrece como **retainer mensual aparte:**

**Retainer de estabilización: USD $200/mes** (incluye hasta 2h de ajustes mensuales — corrección de alucinaciones, ajustes de ruteo, revisión de edge cases).

---

## Tiempos de entrega

- Inicio: dentro de los 5 días hábiles posteriores a la confirmación
- Entrega Opción A: 1-2 semanas desde inicio
- Entrega Opción B: 1 semana desde inicio
- Prerequisito: accesos a GHL, API Key OpenAI, y documentación del prompt maestro

---

## Condiciones

1. **Accesos completos** a GHL (sub-account) antes de iniciar
2. **AppLevel** debe estar configurado y operativo — los problemas derivados de AppLevel no son responsabilidad de la agencia
3. **Prompt maestro** se mantiene el actual (cambios de prompt son scope adicional)
4. **Volumen:** el presupuesto está pensado para la operación actual. Si se escala significativamente (>100 agendas/mes), podrían requerirse ajustes de infraestructura

---

## Sobre la cotización de USD $400

Entendemos que tenés una cotización de referencia de $400. Nuestra propuesta parte de una realidad concreta: **ya construimos este sistema**, conocemos la lógica de negocio, los edge cases y la arquitectura de memoria conversacional. Eso nos permite estimar las horas reales sin padding y entregar más rápido que un proveedor que arranca de cero.

La diferencia de precio se explica en lo que cada opción incluye:

- **Opción B ($600)** se acerca al alcance de una integración mínima — bot disparado desde GHL, respuestas vía AppLevel, reminder 24h. Es lo más parecido a "vincular las herramientas" y la opción más eficiente si el objetivo es volver a poner el bot operativo rápido.
- **Opción A ($1,200)** entrega el alcance completo del documento de Notion: centralización en GHL, migración de CRM, Loom tutorial, mayor soporte post-lanzamiento.

Cualquiera de las dos opciones está pensada para entregar valor en horas reales, sin inflar el alcance. Si preferís otra estructura (por ejemplo, arrancar con Opción B y migrar a A más adelante), lo conversamos.
