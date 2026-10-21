# Guía de Testing — Agente Sistemas y Soluciones v1.2

**Versión:** v1.2
**Fecha:** 2026-04-20
**Canal de prueba:** Telegram
**Estado:** Completado por el equipo — listo para pruebas del cliente

---

## Cómo usar esta guía

Hay dos tipos de casos:

- **Caso simple**: un mensaje → una respuesta. Se testea enviando el texto exacto indicado en una conversación nueva.
- **Flujo conversacional**: secuencia de varios turnos. Se testea siguiendo los pasos en orden dentro de la misma conversación. Si el flujo tiene ramas, cada rama se testea en una conversación separada.

---

## Casos simples

| # | Mensaje a enviar | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|-------------------|-------------------|----|
| 1 | `Hola, buenos días` | Se presenta, da bienvenida, hace pregunta abierta | "Hola, buenos días. Bienvenido a Sistemas y Soluciones. ¿En qué te puedo ayudar hoy?" | ✅ |
| 2 | `¿Cuánto sale una DTF?` | No da precios; informa que el representante envía cotización formal; redirige al diagnóstico | "Los precios los maneja nuestro equipo comercial. Contame, ¿qué tipo de remeras querés estampar? Así puedo asesorarte mejor." | ✅ |
| 3 | `¿Venden heladeras?` | Responde que está fuera de scope; ofrece ayuda con equipos de impresión | Usó el texto exacto de la regla crítica | ✅ |
| 4 | `¿Cuál es la diferencia entre DTF y UV?` | Explica simple, con ejemplo concreto, sin tecnicismos; luego pregunta por el proyecto del cliente | Explicación clara en dos bloques + pregunta de apertura | ✅ |

---

## Flujos conversacionales

---

### Flujo 1: Diagnóstico y derivación — cliente que no sabe qué quiere

**Objetivo:** el agente guía al cliente desde una consulta vaga hasta capturar sus datos y derivar.

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Quiero una máquina para estampar remeras` | Pregunta sobre sustratos o tipo de trabajo — UNA sola pregunta, sin dar precios | "¿En qué sustratos pensás trabajar?" | ✅ |
| 2 | Usuario | `Telas, algodón principalmente` | Orienta hacia DTF; pregunta sobre volumen o tamaño — UNA sola pregunta | — | |
| 3 | Usuario | `Unas 50 prendas por día` | Recomienda tecnología concreta; ofrece conectar con comercial | — | |
| 4 | Usuario | `Sí, me interesa, ¿cómo avanzo?` | Pide datos de contacto (nombre, teléfono) para derivar | — | |
| 5 | Usuario | `Juan García, 11-9999-8888` | Agradece, pide mail si no lo tiene; confirma que el equipo se va a contactar | — | |

---

### Flujo 2: Distribuidor

**Objetivo:** el agente reconoce el perfil, califica brevemente y deriva con datos completos.

**Nota:** en el testing interno (caso 2) el agente saltó directo a pedir datos sin calificar. El flujo esperado incluye al menos una pregunta de contexto antes.

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Soy distribuidor y quiero agregar equipos a mi catálogo` | Reconoce el perfil; pregunta por líneas de interés o zona — UNA pregunta | "¡Genial! Trabajamos con distribuidores. ¿Qué líneas de productos te interesan incorporar?" | ⚠️ Saltó directo a pedir datos |
| 2 | Usuario | `Equipos DTF, opero en Córdoba` | Toma nota del contexto; pide datos de contacto para derivar al comercial | — | |
| 3 | Usuario | `Roberto Díaz, Gráfica Norte, roberto@graficanorte.com, 351-555-0000` | Confirma datos; informa que el equipo comercial se va a contactar | — | |

---

### Flujo 3: Cliente que pide hablar con alguien

**Objetivo:** el agente recolecta los datos mínimos de forma natural y escalonada.

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Quiero que me llame alguien` | Pide nombre, teléfono y ubicación | Pidió nombre, teléfono y ubicación | ✅ |
| 2 | Usuario | `Juan Perez, 59899000001, Montevideo` | Agradece; pide mail con la propuesta estándar | Pidió mail con propuesta correcta | ✅ |
| 3 | Usuario | `juan@mail.com` | Confirma que el equipo se va a contactar; cierra con calidez | — | |

---

### Flujo 4: Usuario hostil

**Objetivo:** el agente mantiene el tono calmado y ofrece derivar sin implicar activación de herramientas.

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Esto es una pérdida de tiempo` | Tono calmado, no escala, ofrece conectar con representante sin decir "estoy derivando" | Tono correcto pero usó "ya estoy derivando tu consulta" (implica tool) | ⚠️ Menor |
| 2 | Usuario | `Dale, que me llame alguien` | Pide datos de contacto | — | |

---

### Flujo 5: Datos completos de golpe

**Objetivo:** cuando el usuario envía todos sus datos juntos, el agente debe reconocerlo y derivar sin continuar con diagnóstico.

**Nota:** issue identificado en testing interno — el agente continuó haciendo diagnóstico en lugar de derivar.

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Soy María López, de Imprenta Rápida, maria@imprentarapida.com, 11-1234-5678, CABA, me interesa una mesa de corte` | Confirma los datos recibidos e informa que el equipo comercial se va a contactar | Hizo diagnóstico adicional en lugar de confirmar y derivar | ⚠️ Notable |

---

### Flujo 6: Consulta de insumos

**Objetivo:** el agente dirige a tienda online y ofrece la alternativa de hablar con un representante.

**Rama A — solo insumos:**

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `¿Tienen insumos para DTF?` | Menciona tienda online; ofrece hablar con representante | Mencionó tienda online (sin URL, esperado); ofreció representante | ✅ |
| 2 | Usuario | `No gracias, voy a la tienda` | Cierra con calidez; deja la puerta abierta | — | |

**Rama B — prefiere hablar con alguien:**

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `¿Tienen insumos para DTF?` | Menciona tienda online; ofrece hablar con representante | ✅ (mismo que rama A) | ✅ |
| 2 | Usuario | `Sí, prefiero hablar con alguien` | Pide datos de contacto para derivar | — | |

---

### Flujo 7: Cierre sin decisión

**Objetivo:** el agente cierra sin presionar y deja abierta la posibilidad de retomar.

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Bueno, gracias, lo pienso` | Cierra con calidez; ofrece enviar info si no tiene el mail aún; no presiona | "¡Perfecto! Cuando lo decidas, estamos acá para ayudarte." | ✅ |

---

## Resumen de resultados internos

| Estado | Cantidad |
|--------|----------|
| ✅ Aprobado | 9 |
| ⚠️ Issue menor | 2 |
| ⚠️ Issue notable | 1 |

**Issues a monitorear en pruebas del cliente:**
- **Flujo 2 (Distribuidor):** tiende a pedir datos sin hacer una pregunta de contexto previa. No bloquea el flujo pero pierde info útil para el comercial.
- **Flujo 4 (Usuario hostil):** usa lenguaje que implica activación de herramienta ("ya estoy derivando"). Mejorar en V2 cuando se agreguen las tools reales.
- **Flujo 5 (Datos completos de golpe):** no reconoce el dump de datos como señal de derivación inmediata. Es un edge case poco frecuente.

---

---

## Casos nuevos — v1.2 (showroom, financiación, nuevas tecnologías, placeholders)

---

### Casos simples — v1.2

| # | Mensaje a enviar | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|-------------------|-------------------|----|
| S5 | `¿Tienen showroom?` | Confirma que sí tienen showroom y hacen demos; pide nombre y teléfono para coordinar | | |
| S6 | `¿Tienen financiación?` | Confirma que sí ofrecen; aclara que se coordina personalmente; pide nombre y teléfono | | |
| S7 | `¿Qué es la sublimación?` | Explica correctamente (papel transfer, calor, fibras sintéticas); menciona la restricción de superficies blancas/poliéster | | |
| S8 | `¿Tienen algo para vinilos y publicidad exterior?` | Orienta hacia Eco-Solvente o Gran Formato; explica resistencia a la intemperie | | |
| S9 | `¿Qué diferencia hay entre DTF textil y DTF UV?` | Distingue claramente: DTF textil para telas (plancha de calor), DTF UV para rígidos (presión manual, sin calor, relieve+brillo) | | |

---

### Flujo 8: Solicitud de demo / visita al showroom

**Objetivo:** el agente confirma que tienen showroom, toma los datos y no intenta derivar al comercial por cotización (es una visita, no una compra inminente).

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Quisiera ver los equipos funcionando antes de decidir` | Confirma que tienen showroom y hacen demos; pide nombre y teléfono para coordinar | | |
| 2 | Usuario | `Soy Carlos Mendez, 11-8888-7777` | Agradece; confirma que el equipo se va a contactar para coordinar la visita; no presiona con cotización | | |

---

### Flujo 9: Consulta de financiación

**Objetivo:** el agente confirma que existe, no da condiciones ni montos, y captura datos para que el equipo contacte al cliente.

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `¿Cómo funciona la financiación?` | Confirma que ofrecen; aclara que las condiciones se definen personalmente; pide nombre y teléfono | | |
| 2 | Usuario | `Ana Flores, 351-444-3333` | Agradece; confirma que un representante se contacta; no inventa condiciones de pago | | |

---

### Flujo 10: Verificación de placeholders de herramientas

**Objetivo:** verificar que el agente incluye las etiquetas correctas en el output cuando corresponde activar cada herramienta.

**Nota:** estos tests verifican el contenido de la respuesta del agente, no solo el flujo conversacional.

**Rama A — NOTIFICAR_LEAD + REGISTRAR_LEAD:**

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Soy Laura García, de Imprenta Central, laura@central.com, 11-5555-4444, CABA, quiero cotizar una DTF` | Confirma los datos; respuesta incluye `[NOTIFICAR_LEAD]` y `[REGISTRAR_LEAD]` con todos los datos en el formato correcto | | |

**Rama B — CONSULTAR_CATALOGO:**

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `¿Qué modelos de impresoras DTF tienen disponibles?` | Respuesta incluye `[CONSULTAR_CATALOGO] equipo: DTF` (o similar) | | |
| 2 | Usuario | `¿Y las mesas de corte Sinajet, qué modelos manejan?` | Respuesta incluye `[CONSULTAR_CATALOGO] equipo: mesa de corte Sinajet` (o similar) | | |

---

**Correcciones aplicadas en v1.2:** FAQs showroom (#S5) y financiación (#S6) completadas. Nuevas tecnologías Sublimación (#S7) y Eco-Solvente (#S8). Herramienta consultar_catalogo con placeholder.

> Guía de testing v1.2 — agrega casos para información nueva (showroom, financiación, tecnologías) y verificación de placeholders de herramientas.

---

## Mini guía — Tools Google Sheets (v1.3)

**Cómo leer los resultados:** en el execution log de n8n vas a ver qué tool llamó el agente y qué devolvió el sheet. Verificar dos cosas: (1) llamó a la tool correcta, (2) usó los datos devueltos en la respuesta (no inventó nada).

---

### Tool: Equipos

**Mensaje disparador:** `¿Qué equipos de impresión tienen disponibles?`

**Qué verificar:**
- Tool llamada: `Equipos`
- El agente lista o menciona equipos con datos reales del sheet (no genéricos)
- No inventa modelos ni precios

---

### Tool: Sinajet

**Mensaje disparador:** `Me interesa una mesa de corte, ¿qué tienen?`

**Qué verificar:**
- Tool llamada: `Sinajet`
- El agente menciona modelos o especificaciones reales del sheet
- Si el sheet no tiene datos aún, el agente lo aclara y ofrece derivar

---

### Tool: Cabezales

**Mensaje disparador:** `Necesito un cabezal de repuesto para mi plotter, ¿tienen?`

**Qué verificar:**
- Tool llamada: `Cabezales`
- El agente usa datos del sheet para orientar (compatibilidad, modelos disponibles)
- No confirma stock — ofrece derivar al comercial para eso

---

### Tool: Tintas y DTF

**Mensaje disparador:** `¿Qué tintas tienen para DTF? También necesito film`

**Qué verificar:**
- Tool llamada: `Tintas y DTF`
- El agente menciona productos del sheet
- Ofrece también la tienda online ([URL_TIENDA]) para compra directa

---

### Tool: RISO

**Mensaje disparador:** `¿Tienen equipos para impresión inkjet de alto volumen?`

**Qué verificar:**
- Tool llamada: `RISO` (no `Equipos`)
- El agente usa datos del sheet de RISO específicamente
- Si hay ambigüedad, puede llamar `Equipos` primero — es aceptable

---

### Tool: IDL

**Mensaje disparador:** `Busco una Konica Minolta para mi imprenta`

**Qué verificar:**
- Tool llamada: `IDL`
- El agente menciona modelos de la línea Konica Minolta del sheet
- No da precios — ofrece derivar al comercial

---

### Test de selección correcta (caso ambiguo)

**Mensaje disparador:** `¿Qué tienen para impresión digital?`

**Qué verificar:**
- El agente hace una pregunta de diagnóstico antes de llamar a cualquier tool (¿inkjet o láser? ¿qué volumen? ¿qué sustrato?)
- Recién llama la tool después de entender la necesidad
- No llama múltiples tools a la vez innecesariamente

---

### Qué hacer si una tool no devuelve datos

Si el sheet está vacío o devuelve un error, el agente debería:
- No inventar información
- Decir que va a consultar con el equipo comercial
- Ofrecer derivar con los datos del cliente

Si el agente inventa datos → corregir en el próximo ciclo de `/iterar-prompt`.
