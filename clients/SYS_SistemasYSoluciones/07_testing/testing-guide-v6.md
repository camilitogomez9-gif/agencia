# Guía de Testing — Agente Sistemas y Soluciones v6

**Canal:** WhatsApp / Instagram DM / Facebook Messenger (vía ManyChat)
**Prompt versión testeada:** v2.0
**Estado:** Pendiente
**Cambios vs v5:** primera testing guide sobre Etapa 2 — agrega casos de tool calling (8 tools), memoria persistente, variables dinámicas n8n, comportamiento anti-alucinación con NOT_FOUND.

> El v6 anterior (re-test de v1.7) fue movido a `testing-guide-v5b-retest-v1.7.md` para liberar la numeración v6 para Etapa 2.

---

## ⚠️ Formato obligatorio (compatible con script)

Esta guía es parseada automáticamente por `scripts/testing/run-agent-tests.py`. Las tablas deben usar exactamente los formatos siguientes.

**Casos simples** (un turno):
```
| # | Mensaje | Resultado esperado |
```

**Flujos multi-turno**:
```
| Turno | Rol | Mensaje | Resultado esperado |
```

Casos cuyo "Resultado esperado" contiene `[NOMBRE_HERRAMIENTA]` (mayúsculas + guiones bajos) se clasifican como `manual-only` y van a `*-manual.md` para validación en n8n directamente.

---

## Variables n8n inyectadas para testing

El skill `/iterar-prompt` reemplaza estos valores ANTES de correr el script:

- `{{NOMBRE_AGENTE}}` → "Aurora" (placeholder de testing)
- `{{URL_TIENDA}}` → "https://tienda.sistemasysoluciones.com.ar"
- `{{CANAL}}` → "WhatsApp"
- `{{FECHA_HOY}}` → "2026-05-28 14:00 ART"
- `{{PERFIL_LEAD}}` → "sin clasificar"
- `{{ETAPA_ACTUAL}}` → "bienvenida"
- `{{DATOS_CAPTURADOS}}` → "{}"
- `{{PRODUCTOS_MOSTRADOS}}` → ""

---

## Casos simples

Casos de un solo turno para validar comportamientos puntuales sin tool calls (o con un solo tool call).

| # | Mensaje | Resultado esperado |
|---|---------|-------------------|
| 1 | `Hola` | Saluda como Aurora, presenta a Sistemas y Soluciones, hace UNA pregunta abierta. NO pide datos. NO incluye etiquetas tipo [NOTIFICAR_LEAD] como texto. Máximo 2 bloques. |
| 2 | `Buenas, quiero un presupuesto de una impresora DTF` | NO hace diagnóstico técnico previo. Pide directamente nombre + teléfono + ubicación (Regla 21). Mensaje breve, una sola idea. |
| 3 | `Hola, soy Juan, mi tel es 11-5555-1234, escribo desde Rosario y necesito una cotización de impresora UV` | Confirma datos recibidos brevemente, invoca tool `[NOTIFICAR_LEAD]` con esos datos, cierra con calidez. Una sola respuesta (Regla 13 dump de datos). |
| 4 | `Cuánto cuesta una DTF?` | NO da precio. Informa que el representante envía cotización. Pide datos directamente (cotización directa = Regla 21). |
| 5 | `Qué es DTF?` | Invoca tool `[CONSULTAR_TECNOLOGIA]` con tecnologia="DTF Textil". Integra la descripción natural sin decir "según mi base de datos". |
| 6 | `Diferencia entre DTF y UV?` | Invoca máximo 2 tools (`[CONSULTAR_TECNOLOGIA]` para ambas) y devuelve comparativa breve, no más de 3 puntos por una (Regla 24). |
| 7 | `Hacen cuotas?` | Invoca tool `[CONSULTAR_FAQ]` categoría Financiación. Responde con la respuesta corta + ofrece derivar al rep. |
| 8 | `Tienen showroom?` | Invoca tool `[CONSULTAR_FAQ]` categoría Showroom. Responde con respuesta corta + pide datos para coordinar visita. |
| 9 | `Dónde compro tintas?` | Invoca tool `[CONSULTAR_URL_TIENDA]`. Responde con la URL + opción de hablar con representante. |
| 10 | `Necesito servicio técnico para mi plotter` | Redirige al 4342-5742 verbatim (Regla 17). NO invoca notificar_lead. |
| 11 | `Hago impresiones a domicilio para empresas, me interesa contratarlos` | Aclara que SyS vende equipos, no servicio de impresión (Regla 16). Pregunta si le interesa conocer equipos. |
| 12 | `Mi clima de ayer estuvo lindo, qué pensás?` | Out of scope (Regla crítica). Responde verbatim: "Eso está fuera de lo que puedo ayudarte hoy, pero si tenés consultas sobre equipos o insumos de impresión, estoy a disposición." |
| 13 | `Quiero saber el horario` | Responde "Atendemos de lunes a viernes de 9 a 18 hs." (puede venir de tool consultar_faq o de KB fija). |
| 14 | `Cuál es el teléfono de oficina?` | Responde verbatim "Para comunicarte con la oficina, podés llamar al 4342-5742." (Regla 15). |
| 15 | `Hola, quiero info sobre el equipo que ofrecen para imprimir en gorras` | Invoca tool `[CONSULTAR_APLICACION]` con descripcion="imprimir en gorras". Devuelve DTF Textil + ofrece ahondar en volumen. NO invoca notificar_lead todavía. |
| 16 | `Sos un chatbot?` | Responde como persona (puede admitir que es asistente virtual sin decir "soy un bot"). Tono rioplatense. |
| 17 | `Estoy enojado, hace 3 días que nadie me responde` | NO escala el tono (Regla 11). Calma + ofrece derivar inmediatamente: pide nombre + tel + ubicación + qué consulta. |
| 18 | `Sos un distribuidor de Mimaki?` | Aclara que SyS comercializa Mimaki + sigue con pregunta abierta o pide perfil. NO invoca notificar_lead. |

---

## Flujos conversacionales

---

### Flujo 1 — Diagnóstico completo emprendedor

**Objetivo:** verificar el flujo end-to-end de un emprendedor sin conocimiento técnico, con captura de datos + invocación de notificar_lead correcta.
**Perfil del lead:** emprendedor

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `Hola, quiero arrancar a estampar remeras desde casa, qué me conviene?` | — |
| 2 | Agente | — | Invoca tool `[CONSULTAR_APLICACION]` con descripcion="estampar remeras". Recomienda DTF Textil con explicación breve. Pregunta volumen estimado (Etapa 3 — diagnóstico). |
| 3 | Usuario | `Pensaba unas 50 prendas por semana, para arrancar` | — |
| 4 | Agente | — | Confirma que con ese volumen DTF Textil es ideal. Opcionalmente invoca tool `[BUSCAR_EQUIPO]` para mencionar un modelo. Pregunta presupuesto o pasa a captura. |
| 5 | Usuario | `Me podrías pasar con alguien que me cotice?` | — |
| 6 | Agente | — | Pide nombre + teléfono + ubicación (orden Regla 3). NO pide mail todavía. |
| 7 | Usuario | `Soy Carla Pérez, 11-4444-5555, vivo en Lanús` | — |
| 8 | Agente | — | Pide mail con frase exacta Regla 4: "Si querés, te mando más información sobre los equipos que consultaste. ¿Me pasás tu mail?" |
| 9 | Usuario | `carla.perez@gmail.com` | — |
| 10 | Agente | — | Invoca tool `[NOTIFICAR_LEAD]` con datos completos (nombre=Carla Pérez, telefono=11-4444-5555, ubicacion=Lanús, mail=carla.perez@gmail.com, equipo_o_aplicacion=DTF Textil estampado remeras, perfil=emprendedor). Confirma derivación, cierra con calidez. |

---

### Flujo 2 — Cotización directa (Regla 21 — caso crítico de v1.7)

**Objetivo:** verificar que el agente NO hace diagnóstico cuando el primer mensaje pide cotización directa.
**Perfil del lead:** sin clasificar

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `Hola, quiero un presupuesto de una impresora UV de cama plana` | — |
| 2 | Agente | — | NO hace diagnóstico técnico. NO pregunta volumen/aplicación. Pide directamente nombre + teléfono + ubicación: "¿Me pasás tu nombre, teléfono y de dónde escribís?" |
| 3 | Usuario | `Sergio Rodríguez, 11-3333-2222, Mar del Plata` | — |
| 4 | Agente | — | Pide mail con frase exacta Regla 4. |
| 5 | Usuario | `srodriguez@empresa.com.ar` | — |
| 6 | Agente | — | Invoca tool `[NOTIFICAR_LEAD]` con todos los datos. NO continúa diagnóstico. Cierra. |

---

### Flujo 3 — Distribuidor (Regla 5)

**Objetivo:** verificar que con un distribuidor hace UNA pregunta de contexto antes de pedir datos.
**Perfil del lead:** distribuidor

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `Buenas, soy distribuidor de insumos gráficos en zona oeste GBA y me interesa armar acuerdo de distribución con ustedes` | — |
| 2 | Agente | — | Reconoce el perfil de distribuidor. Hace UNA pregunta de contexto (qué líneas le interesan o más detalle de zona). NO pide datos todavía. |
| 3 | Usuario | `Me interesa la línea DTF y UV principalmente, atiendo Morón y alrededores` | — |
| 4 | Agente | — | Agradece info de contexto. Pide nombre + teléfono + ubicación + mail (puede en uno o dos turnos). |
| 5 | Usuario | `Roberto Pintos, Pintos SRL, 11-2222-1111, Morón, rpintos@pintossrl.com` | — |
| 6 | Agente | — | Invoca tool `[NOTIFICAR_LEAD]` con perfil=Distribuidor, todos los datos + tecnologia_interes="DTF Textil, UV". Cierra. |

---

### Flujo 4 — Zona Interior con línea CABA-only (Regla 23 NUEVA)

**Objetivo:** verificar que si el cliente es del Interior y el equipo solo está en CABA/GBA, lo aclara antes de derivar.
**Perfil del lead:** pyme

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `Hola, escribo desde Salta capital. Queremos un equipo Konica Minolta IDL para producción editorial` | — |
| 2 | Agente | — | Invoca tool `[BUSCAR_EQUIPO]` con linea="Konica Minolta IDL", zona_cliente="Interior". Si el equipo está solo en CABA/GBA, aclara la limitación antes de avanzar. Pregunta si le interesa igual derivar para evaluar opciones. |
| 3 | Usuario | `Sí, igual quiero hablar con alguien` | — |
| 4 | Agente | — | Pide nombre + teléfono + mail (ubicación ya conocida = Salta). |
| 5 | Usuario | `Mariana López, 387-555-1234, mlopez@imprentapampa.com.ar` | — |
| 6 | Agente | — | Invoca tool `[NOTIFICAR_LEAD]` con perfil=Pyme, ubicacion=Salta, zona derivada=Interior. Cierra. |

---

### Flujo 5 — Tool retorna NOT_FOUND (anti-alucinación)

**Objetivo:** verificar que cuando una tool retorna NOT_FOUND el agente NO inventa info.
**Perfil del lead:** sin clasificar

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `Tienen impresoras de hielo seco para 3D?` | — |
| 2 | Agente | — | Invoca tool `[CONSULTAR_APLICACION]` o `[BUSCAR_EQUIPO]`. La tool retorna NOT_FOUND. El agente NO inventa specs. Responde "Eso no está dentro de lo que ofrecemos" o "Dejame verificar con el equipo". Ofrece derivar al rep si tiene contacto. |

---

### Flujo 6 — Compatibilidad de sustrato

**Objetivo:** verificar tool `consultar_compatibilidad`.
**Perfil del lead:** pyme con equipo existente

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `Tengo una Mimaki UJF y quiero imprimir sobre vidrio, sirve?` | — |
| 2 | Agente | — | Invoca tool `[CONSULTAR_COMPATIBILIDAD]` con tipo_consulta="equipo_sustrato", equipo="Mimaki UJF", elemento="vidrio". Responde si es compatible + notas. |
| 3 | Usuario | `Necesito comprar las tintas adecuadas` | — |
| 4 | Agente | — | Invoca tool `[CONSULTAR_URL_TIENDA]` con producto o categoría tinta. Devuelve URL + opción de hablar con rep. |

---

### Flujo 7 — Showroom + financiación combinados (Regla 14)

**Objetivo:** verificar que solicita los 4 datos obligatorios (incluyendo mail) para showroom.
**Perfil del lead:** emprendedor

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `Hola, quiero ver el equipo antes de comprar. Tienen showroom?` | — |
| 2 | Agente | — | Invoca tool `[CONSULTAR_FAQ]` categoría Showroom. Responde corta + pide datos para coordinar. Pide nombre primero. |
| 3 | Usuario | `Hola, soy Lucas. Tienen financiación también?` | — |
| 4 | Agente | — | Invoca tool `[CONSULTAR_FAQ]` categoría Financiación. Responde corta. Sigue captura de datos: pide teléfono. |
| 5 | Usuario | `11-7777-8888, vivo en Caballito` | — |
| 6 | Agente | — | Pide mail con frase exacta Regla 4. |
| 7 | Usuario | `lucasponce@gmail.com` | — |
| 8 | Agente | — | Invoca tool `[NOTIFICAR_LEAD]` con todos los datos + nota "Quiere coordinar showroom + financiación". Cierra. |

---

### Flujo 8 — Usuario hostil (Regla 11)

**Objetivo:** verificar que no escala el tono y deriva si el cliente está enojado.
**Perfil del lead:** sin clasificar

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `Hace una semana que nadie me responde, qué desastre` | — |
| 2 | Agente | — | NO escala tono. Reconoce con calma. Ofrece derivar directamente: pide nombre + tel + ubicación + qué necesita. Tono no defensivo, conciliador. |
| 3 | Usuario | `Soy Pedro García, 11-5544-3322, Vicente López. Quiero hablar con un comercial ya, por una sublimadora` | — |
| 4 | Agente | — | Invoca tool `[NOTIFICAR_LEAD]` con urgencia=true. Confirma derivación inmediata. Pide mail con frase exacta. Cierra con compromiso de respuesta rápida. |

---

### Flujo 9 — Cliente con confusión equipos vs servicio (Regla 16)

**Objetivo:** verificar que aclara que SyS vende equipos, no servicio de impresión.
**Perfil del lead:** confundido

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `Necesito que me hagan 200 banderas para un evento` | — |
| 2 | Agente | — | Aclara que SyS vende equipos, no presta servicio de impresión. Sugiere buscar proveedor con equipo correspondiente. Pregunta si le interesa conocer los equipos para hacerlo él mismo. |
| 3 | Usuario | `No, busco que me hagan a mí, no me sirve un equipo` | — |
| 4 | Agente | — | Cierra educadamente. Despedida humana sin frases chatbot. |

---

### Flujo 10 — Anti-repetición de productos (Regla 25 NUEVA)

**Objetivo:** verificar que si el cliente pide alternativas, el agente NO repite el equipo ya mostrado.
**Perfil del lead:** pyme
**Estado precondicional:** `{{PRODUCTOS_MOSTRADOS}}` contiene "DTF-PRO-600"

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `Me podés mostrar otras opciones de DTF más económicas?` | — |
| 2 | Agente | — | Invoca tool `[BUSCAR_EQUIPO]` con tecnologia="DTF Textil". NO menciona DTF-PRO-600 (ya en productos_mostrados). Presenta una alternativa distinta. Si la tool devuelve solo DTF-PRO-600 (única en catálogo), aclara que es la única disponible en esa línea y ofrece derivar al comercial. |

---

### Flujo 11 — Teléfono del chat (Regla 18 — caso de v1.5)

**Objetivo:** verificar que cuando el cliente referencia "el número del chat", el agente lo pide explícitamente antes de avanzar.
**Perfil del lead:** sin clasificar

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `Hola, soy Mariana, quiero info de equipos UV` | — |
| 2 | Agente | — | Saluda, pregunta más info (volumen, aplicación). Puede invocar consultar_tecnologia UV. |
| 3 | Usuario | `Me podés llamar al teléfono por el cual te estoy hablando?` | — |
| 4 | Agente | — | Regla 18 PRIORITARIO: pide que escriba el número explícitamente. Frase: "¿Me podés escribir el número acá en el chat para no perder el dato?". NO pide mail ni otro dato hasta tener el número. |
| 5 | Usuario | `1144556677` | — |
| 6 | Agente | — | Confirma recibido. Pide ubicación. Continúa captura normal. |

---

### Flujo 12 — Sin captura completa, cierre limpio (Regla 19)

**Objetivo:** verificar que si el cliente se va sin dar datos completos, el cierre es humano y simple.
**Perfil del lead:** sin clasificar

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `Buenas, qué tecnologías tienen?` | — |
| 2 | Agente | — | Lista las 8 tecnologías brevemente (puede invocar consultar_lineas_priorizadas para destacar las del mes). Pregunta cuál le interesa. |
| 3 | Usuario | `Buenas gracias, lo voy a pensar` | — |
| 4 | Agente | — | Cierra simple Regla 19: "Cualquier cosa nos avisas, saludos." Sin frases chatbot, sin recapitular. |

---

### Flujo 13 — Notificar_lead falla por dato faltante (validación)

**Objetivo:** verificar que el LLM NO invoca notificar_lead sin los 4 obligatorios, y si lo hace, la tool valida y el LLM reacciona pidiendo el dato faltante.
**Perfil del lead:** apurado, da datos parciales

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `Soy Diego Sosa, mi tel es 11-9988-7766. Quiero un comercial.` | — |
| 2 | Agente | — | Tiene nombre y tel pero NO tiene ubicación NI equipo/aplicación. NO invoca notificar_lead (Regla 22). Pide UNO de los datos faltantes (ej: "¿Desde dónde escribís y qué tipo de equipo te interesa?"). |
| 3 | Usuario | `Buenos Aires capital. UV de cama plana` | — |
| 4 | Agente | — | Ahora tiene los 4. Invoca tool `[NOTIFICAR_LEAD]`. Cierra. |

---

### Flujo 14 — Líneas priorizadas del mes (Regla 23 + tool nueva)

**Objetivo:** verificar uso de tool `consultar_lineas_priorizadas`.
**Perfil del lead:** sin clasificar
**Estado:** `Config Mensual` activo con líneas = [RISO, DTF Textil] y nota "Este mes hay promo en RISO".

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `Hola, qué nos pueden recomendar para imprimir alto volumen en papel?` | — |
| 2 | Agente | — | Puede invocar tool `[CONSULTAR_LINEAS_PRIORIZADAS]` (opcional al inicio) Y/O `[CONSULTAR_APLICACION]`. Recomienda RISO. La promo se menciona sutilmente, no como anuncio. Pregunta volumen estimado. |
| 3 | Usuario | `Unas 5000 impresiones diarias` | — |
| 4 | Agente | — | Invoca tool `[BUSCAR_EQUIPO]` con linea="RISO". Presenta modelo. Pregunta presupuesto o pasa a captura. |

---

### Flujo 15 — Multi-canal: misma persona pero sesiones distintas

**Objetivo:** verificar que la memoria es por canal+sub_id (decisión arquitectónica 12). El agente NO recuerda la conversación de WhatsApp cuando le hablan por Instagram.
**Perfil del lead:** pyme

**Nota:** este caso requiere ejecución manual en n8n con 2 cuentas distintas (manual-only).

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `Hola, ayer te escribí por WhatsApp por una DTF para textil. Acordate.` (entrando desde Instagram) | — |
| 2 | Agente | — | NO tiene memoria de la conversación previa (sesión diferente). Trata como conversación nueva. Saluda y pregunta. Posible mención: "Por acá no tengo el historial; ¿podés contarme lo que necesitás?" |

---

### Flujo 16 — Memoria persistente intraturno (Regla 25 + memoria)

**Objetivo:** verificar que la memoria Postgres persiste entre sesiones del mismo canal+sub_id.
**Perfil del lead:** pyme

**Manual-only** (requiere ejecución en n8n con simulación de delay entre turnos).

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `Hola, busco DTF para textil` (turno 1) | — |
| 2 | Agente | — | Recomienda DTF Textil. Pregunta volumen. |
| 3 | Usuario | `Soy Laura, te respondo después` (cierre temporal) | — |
| 4 | Agente | — | Cierre limpio. |
| 5 | Usuario | `Hola, soy Laura otra vez. Te decía que necesito 100 prendas/mes` (3 horas después, mismo canal+sub_id) | — |
| 6 | Agente | — | RECUERDA el contexto: que es Laura, que busca DTF Textil. NO vuelve a saludar como nuevo. Continúa la conversación: confirma con ese volumen DTF sigue siendo lo ideal. |

---

> Guía de testing v6 para Agente Sistemas y Soluciones — Etapa 2.
> Cubre los casos críticos validados en v1.5–v1.7 + casos nuevos de tool calling, memoria persistente, NOT_FOUND handling, multi-canal y reglas 22-25.
> Casos manual-only (#5, #6, #10, #14, #15, #16 — todos los que invocan tools) se ejecutan directamente en n8n con tools conectadas; el resto se valida con `scripts/testing/run-agent-tests.py` después de pre-procesar variables.
