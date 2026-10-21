# Resultados de Testing Automatizado

**Modelo testeado:** `gpt-4o`
**Modelo juez:** `gpt-4o-mini`
**Temperatura:** 0.2

---

## Casos Simples

| # | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|---|---------|-------------------|-------------------|----|-------|
| 2 | `Buenas, quiero un presupuesto de una impresora DTF` | NO hace diagnóstico técnico previo. Pide directamente nombre + teléfono + ubicac… | Para conectarte con nuestro equipo comercial y obtener un presupuesto, ¿me pasás tu nombre, teléfono… | true | La respuesta del agente solicita directamente el nombre, teléfono y ubicación, cumpliendo con el comportamiento esperado. |
| 4 | `Cuánto cuesta una DTF?` | NO da precio. Informa que el representante envía cotización. Pide datos directam… | No doy precios directamente. Un representante comercial te envía la cotización formal con todos los … | true | La respuesta del agente cumple con el comportamiento esperado al no dar precios, informar que un representante enviará la cotización y solicitar los datos necesarios. |
| 10 | `Necesito servicio técnico para mi plotter` | Redirige al 4342-5742 verbatim (Regla 17). NO invoca notificar_lead. | Para servicio técnico, comunicate directamente con nuestra oficina al 4342-5742. Ellos te van a pode… | true | La respuesta real redirige correctamente al número 4342-5742 verbatim y no invoca notificar_lead. |
| 11 | `Hago impresiones a domicilio para empresas, me interesa cont…` | Aclara que SyS vende equipos, no servicio de impresión (Regla 16). Pregunta si l… | Hola, bienvenido a Sistemas y Soluciones. Nosotros vendemos equipos de impresión, no ofrecemos el se… | true | La respuesta del agente aclara que venden equipos de impresión y no servicios, y además pregunta si le interesa conocer los equipos, cumpliendo con el comportamiento esperado. |
| 12 | `Mi clima de ayer estuvo lindo, qué pensás?` | Out of scope (Regla crítica). Responde verbatim: "Eso está fuera de lo que puedo… | Eso está fuera de lo que puedo ayudarte hoy, pero si tenés consultas sobre equipos o insumos de impr… | true | La respuesta real del agente coincide exactamente con el comportamiento esperado, cumpliendo con todos los elementos clave requeridos. |
| 13 | `Quiero saber el horario` | Responde "Atendemos de lunes a viernes de 9 a 18 hs." (puede venir de tool consu… | El horario de atención del equipo humano de Sistemas y Soluciones es de lunes a viernes de 9 a 18 hs… | true | La respuesta real incluye el horario de atención solicitado y mantiene un tono adecuado y útil. |
| 14 | `Cuál es el teléfono de oficina?` | Responde verbatim "Para comunicarte con la oficina, podés llamar al 4342-5742." … | Para comunicarte con la oficina, podés llamar al 4342-5742. | true | La respuesta real del agente coincide exactamente con el comportamiento esperado, cumpliendo con todos los elementos clave requeridos. |
| 16 | `Sos un chatbot?` | Responde como persona (puede admitir que es asistente virtual sin decir "soy un … | Soy el asistente virtual de Sistemas y Soluciones. ¿En qué te puedo ayudar? | false | El agente se identifica como asistente virtual, lo cual no cumple con el comportamiento esperado de responder como una persona. |
| 17 | `Estoy enojado, hace 3 días que nadie me responde` | NO escala el tono (Regla 11). Calma + ofrece derivar inmediatamente: pide nombre… | Lamento mucho la demora. Estoy acá para ayudarte. Contame, ¿en qué te puedo asistir hoy? | false | La respuesta no solicita el nombre, teléfono, ubicación ni la consulta específica del usuario, lo que no cumple con el comportamiento esperado. |
| 18 | `Sos un distribuidor de Mimaki?` | Aclara que SyS comercializa Mimaki + sigue con pregunta abierta o pide perfil. N… | No, no trabajamos directamente con Mimaki. En Sistemas y Soluciones ofrecemos equipos de marcas como… | false | El agente afirma que no trabaja con Mimaki, lo cual contradice el comportamiento esperado que indica que SyS comercializa Mimaki. |

## Flujo 1 — Diagnóstico completo emprendedor

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `Hola, quiero arrancar a estampar remeras desde casa, qué me …` | — |  |  |  |
| 3 | Usuario | `Pensaba unas 50 prendas por semana, para arrancar` | — |  |  |  |
| 5 | Usuario | `Me podrías pasar con alguien que me cotice?` | — |  |  |  |
| 6 | Agente | `—` | Pide nombre + teléfono + ubicación (orden Regla 3). NO pide mail todavía. | Claro, para eso necesito algunos datos. ¿Me pasás tu nombre, teléfono y de dónde escribís? | true | La respuesta del agente cubre todos los elementos clave requeridos: pide el nombre, teléfono y ubicación, y no solicita el correo electrónico. |
| 7 | Usuario | `Soy Carla Pérez, 11-4444-5555, vivo en Lanús` | — |  |  |  |
| 8 | Agente | `—` | Pide mail con frase exacta Regla 4: "Si querés, te mando más información sobre l… | Perfecto, Carla. Ahora, ¿me pasás tu mail para enviarte más información sobre los equipos? | true | La respuesta del agente incluye la frase solicitada y mantiene un tono adecuado, cumpliendo con el comportamiento esperado. |
| 9 | Usuario | `carla.perez@gmail.com` | — |  |  |  |

## Flujo 2 — Cotización directa (Regla 21 — caso crítico de v1.7)

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `Hola, quiero un presupuesto de una impresora UV de cama plan…` | — |  |  |  |
| 2 | Agente | `—` | NO hace diagnóstico técnico. NO pregunta volumen/aplicación. Pide directamente n… | Para pasarte un presupuesto formal, necesito algunos datos. ¿Me pasás tu nombre, teléfono y de dónde… | true | La respuesta del agente cubre todos los elementos clave requeridos y evita comportamientos prohibidos, manteniendo un tono adecuado. |
| 3 | Usuario | `Sergio Rodríguez, 11-3333-2222, Mar del Plata` | — |  |  |  |
| 4 | Agente | `—` | Pide mail con frase exacta Regla 4. | Gracias, Sergio. ¿Querés que te mande más información sobre los equipos por correo? Si es así, pasam… | true | La respuesta del agente solicita el correo electrónico de manera clara y directa, cumpliendo con la frase exacta requerida. |
| 5 | Usuario | `srodriguez@empresa.com.ar` | — |  |  |  |

## Flujo 3 — Distribuidor (Regla 5)

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `Buenas, soy distribuidor de insumos gráficos en zona oeste G…` | — |  |  |  |
| 2 | Agente | `—` | Reconoce el perfil de distribuidor. Hace UNA pregunta de contexto (qué líneas le… | Hola, bienvenido a Sistemas y Soluciones.   ---  ¿Qué líneas de producto te interesan para la distri… | true | La respuesta del agente reconoce el perfil de distribuidor y hace una pregunta de contexto adecuada sobre las líneas de producto. |
| 3 | Usuario | `Me interesa la línea DTF y UV principalmente, atiendo Morón …` | — |  |  |  |
| 4 | Agente | `—` | Agradece info de contexto. Pide nombre + teléfono + ubicación + mail (puede en u… | Perfecto, gracias por la info.   ---  ¿Me pasás tu nombre, teléfono y correo para que el equipo come… | true | La respuesta del agente agradece la información y solicita el nombre, teléfono y correo, cumpliendo con los elementos clave requeridos. |
| 5 | Usuario | `Roberto Pintos, Pintos SRL, 11-2222-1111, Morón, rpintos@pin…` | — |  |  |  |

## Flujo 4 — Zona Interior con línea CABA-only (Regla 23 NUEVA)

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `Hola, escribo desde Salta capital. Queremos un equipo Konica…` | — |  |  |  |
| 3 | Usuario | `Sí, igual quiero hablar con alguien` | — |  |  |  |
| 4 | Agente | `—` | Pide nombre + teléfono + mail (ubicación ya conocida = Salta). | Perfecto. Para conectarte con nuestro equipo comercial, ¿me confirmás tu nombre, teléfono y desde dó… | parcial | El agente solicita el nombre y el teléfono, pero no menciona explícitamente el correo electrónico que se requiere. |
| 5 | Usuario | `Mariana López, 387-555-1234, mlopez@imprentapampa.com.ar` | — |  |  |  |

## Flujo 5 — Tool retorna NOT_FOUND (anti-alucinación)

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `Tienen impresoras de hielo seco para 3D?` | — |  |  |  |

## Flujo 6 — Compatibilidad de sustrato

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `Tengo una Mimaki UJF y quiero imprimir sobre vidrio, sirve?` | — |  |  |  |
| 3 | Usuario | `Necesito comprar las tintas adecuadas` | — |  |  |  |

## Flujo 7 — Showroom + financiación combinados (Regla 14)

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `Hola, quiero ver el equipo antes de comprar. Tienen showroom…` | — |  |  |  |
| 3 | Usuario | `Hola, soy Lucas. Tienen financiación también?` | — |  |  |  |
| 5 | Usuario | `11-7777-8888, vivo en Caballito` | — |  |  |  |
| 6 | Agente | `—` | Pide mail con frase exacta Regla 4. | Perfecto, Lucas. ¿Me pasás tu mail así te mando más información sobre los equipos y las opciones de … | false | El agente no utiliza la frase exacta requerida para pedir el mail. |
| 7 | Usuario | `lucasponce@gmail.com` | — |  |  |  |

## Flujo 8 — Usuario hostil (Regla 11)

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `Hace una semana que nadie me responde, qué desastre` | — |  |  |  |
| 2 | Agente | `—` | NO escala tono. Reconoce con calma. Ofrece derivar directamente: pide nombre + t… | Lamento mucho la demora. Estoy acá para ayudarte. Contame, ¿en qué puedo asistirte hoy? | parcial | La respuesta del agente es conciliadora y ofrece ayuda, pero no solicita el nombre, teléfono, ubicación ni qué necesita el usuario, lo cual es necesario para cumplir completamente con el comportamiento esperado. |
| 3 | Usuario | `Soy Pedro García, 11-5544-3322, Vicente López. Quiero hablar…` | — |  |  |  |

## Flujo 9 — Cliente con confusión equipos vs servicio (Regla 16)

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `Necesito que me hagan 200 banderas para un evento` | — |  |  |  |
| 2 | Agente | `—` | Aclara que SyS vende equipos, no presta servicio de impresión. Sugiere buscar pr… | Sistemas y Soluciones vende equipos de impresión, no el servicio de impresión. Si necesitás a alguie… | true | La respuesta real aclara que SyS vende equipos y no presta servicio de impresión, sugiere buscar un proveedor adecuado y pregunta si le interesa conocer los equipos. |
| 3 | Usuario | `No, busco que me hagan a mí, no me sirve un equipo` | — |  |  |  |
| 4 | Agente | `—` | Cierra educadamente. Despedida humana sin frases chatbot. | Entiendo, en ese caso te recomiendo buscar un proveedor que ofrezca servicios de impresión. Si en el… | false | La respuesta no cierra de manera educada y humana, ya que incluye una oferta de ayuda adicional y no se despide de forma directa. |

## Flujo 10 — Anti-repetición de productos (Regla 25 NUEVA)

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `Me podés mostrar otras opciones de DTF más económicas?` | — |  |  |  |

## Flujo 11 — Teléfono del chat (Regla 18 — caso de v1.5)

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `Hola, soy Mariana, quiero info de equipos UV` | — |  |  |  |
| 2 | Agente | `—` | Saluda, pregunta más info (volumen, aplicación). Puede invocar consultar_tecnolo… | Hola, Mariana. Bienvenida a Sistemas y Soluciones.  ---  ¿Qué tipo de trabajo pensás realizar con lo… | true | La respuesta del agente saluda y pregunta sobre el tipo de trabajo, lo que cumple con el comportamiento esperado. |
| 3 | Usuario | `Me podés llamar al teléfono por el cual te estoy hablando?` | — |  |  |  |
| 4 | Agente | `—` | Regla 18 PRIORITARIO: pide que escriba el número explícitamente. Frase: "¿Me pod… | Para comunicarte con la oficina, podés llamar al 4342-5742.   ---  Si querés que un representante te… | false | El agente pide el número de teléfono, pero también menciona la opción de llamar a la oficina, lo que no se alinea con la regla de no solicitar otros datos hasta tener el número. |
| 5 | Usuario | `1144556677` | — |  |  |  |
| 6 | Agente | `—` | Confirma recibido. Pide ubicación. Continúa captura normal. | Gracias, Mariana. Ahora, ¿me podrías decir de dónde nos escribís? Así puedo derivarte al representan… | true | La respuesta del agente confirma la recepción del mensaje y solicita la ubicación, cumpliendo con el comportamiento esperado. |

## Flujo 12 — Sin captura completa, cierre limpio (Regla 19)

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `Buenas, qué tecnologías tienen?` | — |  |  |  |
| 2 | Agente | `—` | Lista las 8 tecnologías brevemente (puede invocar consultar_lineas_priorizadas p… | Hola, bienvenido a Sistemas y Soluciones.  ---  Trabajamos con varias tecnologías de impresión, como… | parcial | El agente lista varias tecnologías, pero no menciona que puede consultar líneas priorizadas ni pregunta cuál le interesa de manera clara. |
| 3 | Usuario | `Buenas gracias, lo voy a pensar` | — |  |  |  |
| 4 | Agente | `—` | Cierra simple Regla 19: "Cualquier cosa nos avisas, saludos." Sin frases chatbot… | De nada. Cualquier cosa que necesites, estoy acá para ayudarte. Saludos. | parcial | La respuesta incluye un comportamiento adicional al ofrecer ayuda, lo cual no se alinea completamente con la regla esperada de cerrar con un simple saludo. |

## Flujo 13 — Notificar_lead falla por dato faltante (validación)

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `Soy Diego Sosa, mi tel es 11-9988-7766. Quiero un comercial.` | — |  |  |  |
| 2 | Agente | `—` | Tiene nombre y tel pero NO tiene ubicación NI equipo/aplicación. NO invoca notif… | Hola, Diego. Para conectarte con nuestro equipo comercial, ¿me confirmás desde dónde nos escribís y … | false | El agente solicita información sobre el equipo o aplicación, lo cual no está permitido según el comportamiento esperado. |
| 3 | Usuario | `Buenos Aires capital. UV de cama plana` | — |  |  |  |

## Flujo 14 — Líneas priorizadas del mes (Regla 23 + tool nueva)

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `Hola, qué nos pueden recomendar para imprimir alto volumen e…` | — |  |  |  |
| 3 | Usuario | `Unas 5000 impresiones diarias` | — |  |  |  |

## Flujo 15 — Multi-canal: misma persona pero sesiones distintas

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `Hola, ayer te escribí por WhatsApp por una DTF para textil. …` | — |  |  |  |
| 2 | Agente | `—` | NO tiene memoria de la conversación previa (sesión diferente). Trata como conver… | Hola, bienvenido a Sistemas y Soluciones. ¿En qué te puedo ayudar hoy con la DTF para textil? | false | El agente no menciona que no tiene el historial de la conversación previa ni pregunta al usuario sobre sus necesidades específicas. |

## Flujo 16 — Memoria persistente intraturno (Regla 25 + memoria)

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `Hola, busco DTF para textil` (turno 1)` | — |  |  |  |
| 2 | Agente | `—` | Recomienda DTF Textil. Pregunta volumen. | Hola, bienvenido a Sistemas y Soluciones.  ---  ¿Qué tipo de trabajo pensás realizar con la DTF text… | parcial | El agente no recomienda directamente DTF Textil ni pregunta sobre el volumen, aunque sí indaga sobre el tipo de trabajo, lo que es relevante. |
| 3 | Usuario | `Soy Laura, te respondo después` (cierre temporal)` | — |  |  |  |
| 4 | Agente | `—` | Cierre limpio. | Perfecto, Laura. Cuando estés lista, acá estoy para ayudarte. Cualquier cosa nos avisas, saludos. | parcial | La respuesta muestra disposición para ayudar, pero no cierra la conversación de manera definitiva. |
| 5 | Usuario | `Hola, soy Laura otra vez. Te decía que necesito 100 prendas/…` | — |  |  |  |
| 6 | Agente | `—` | RECUERDA el contexto: que es Laura, que busca DTF Textil. NO vuelve a saludar co… | Gracias por volver, Laura. Con ese volumen, la DTF textil es una buena opción. ¿Tenés algún requerim… | parcial | El agente recuerda a Laura y confirma que DTF es una buena opción, pero vuelve a saludarla, lo cual no se esperaba. |

---

## Resumen

| Resultado | Cantidad |
|-----------|----------|
| true | 16 |
| false | 8 |
| parcial | 7 |
| error | 0 |
| manual-only | 26 |

### Casos fallidos

- **#16:** El agente se identifica como asistente virtual, lo cual no cumple con el comportamiento esperado de responder como una persona.
- **#17:** La respuesta no solicita el nombre, teléfono, ubicación ni la consulta específica del usuario, lo que no cumple con el comportamiento esperado.
- **#18:** El agente afirma que no trabaja con Mimaki, lo cual contradice el comportamiento esperado que indica que SyS comercializa Mimaki.
- **Turno 4:** El agente solicita el nombre y el teléfono, pero no menciona explícitamente el correo electrónico que se requiere.
- **Turno 6:** El agente no utiliza la frase exacta requerida para pedir el mail.
- **Turno 2:** La respuesta del agente es conciliadora y ofrece ayuda, pero no solicita el nombre, teléfono, ubicación ni qué necesita el usuario, lo cual es necesario para cumplir completamente con el comportamiento esperado.
- **Turno 4:** La respuesta no cierra de manera educada y humana, ya que incluye una oferta de ayuda adicional y no se despide de forma directa.
- **Turno 4:** El agente pide el número de teléfono, pero también menciona la opción de llamar a la oficina, lo que no se alinea con la regla de no solicitar otros datos hasta tener el número.
- **Turno 2:** El agente lista varias tecnologías, pero no menciona que puede consultar líneas priorizadas ni pregunta cuál le interesa de manera clara.
- **Turno 4:** La respuesta incluye un comportamiento adicional al ofrecer ayuda, lo cual no se alinea completamente con la regla esperada de cerrar con un simple saludo.
- **Turno 2:** El agente solicita información sobre el equipo o aplicación, lo cual no está permitido según el comportamiento esperado.
- **Turno 2:** El agente no menciona que no tiene el historial de la conversación previa ni pregunta al usuario sobre sus necesidades específicas.
- **Turno 2:** El agente no recomienda directamente DTF Textil ni pregunta sobre el volumen, aunque sí indaga sobre el tipo de trabajo, lo que es relevante.
- **Turno 4:** La respuesta muestra disposición para ayudar, pero no cierra la conversación de manera definitiva.
- **Turno 6:** El agente recuerda a Laura y confirma que DTF es una buena opción, pero vuelve a saludarla, lo cual no se esperaba.

---

## Apéndice: Respuestas Completas

### Caso #2
**Mensaje:** Buenas, quiero un presupuesto de una impresora DTF
**Respuesta:**
Para conectarte con nuestro equipo comercial y obtener un presupuesto, ¿me pasás tu nombre, teléfono y de dónde escribís?

### Caso #4
**Mensaje:** Cuánto cuesta una DTF?
**Respuesta:**
No doy precios directamente. Un representante comercial te envía la cotización formal con todos los detalles. ¿Me pasás tu nombre, teléfono y de dónde escribís para que te contacten?

### Caso #10
**Mensaje:** Necesito servicio técnico para mi plotter
**Respuesta:**
Para servicio técnico, comunicate directamente con nuestra oficina al 4342-5742. Ellos te van a poder ayudar con lo que necesites.

### Caso #11
**Mensaje:** Hago impresiones a domicilio para empresas, me interesa contratarlos
**Respuesta:**
Hola, bienvenido a Sistemas y Soluciones. Nosotros vendemos equipos de impresión, no ofrecemos el servicio de impresión a domicilio. 

---

Si te interesa conocer los equipos que tenemos para mejorar tu negocio, contame un poco más sobre qué tipo de trabajos hacés y qué estás buscando.

### Caso #12
**Mensaje:** Mi clima de ayer estuvo lindo, qué pensás?
**Respuesta:**
Eso está fuera de lo que puedo ayudarte hoy, pero si tenés consultas sobre equipos o insumos de impresión, estoy a disposición.

### Caso #13
**Mensaje:** Quiero saber el horario
**Respuesta:**
El horario de atención del equipo humano de Sistemas y Soluciones es de lunes a viernes de 9 a 18 hs. ¿En qué te puedo ayudar?

### Caso #14
**Mensaje:** Cuál es el teléfono de oficina?
**Respuesta:**
Para comunicarte con la oficina, podés llamar al 4342-5742.

### Caso #16
**Mensaje:** Sos un chatbot?
**Respuesta:**
Soy el asistente virtual de Sistemas y Soluciones. ¿En qué te puedo ayudar?

### Caso #17
**Mensaje:** Estoy enojado, hace 3 días que nadie me responde
**Respuesta:**
Lamento mucho la demora. Estoy acá para ayudarte. Contame, ¿en qué te puedo asistir hoy?

### Caso #18
**Mensaje:** Sos un distribuidor de Mimaki?
**Respuesta:**
No, no trabajamos directamente con Mimaki. En Sistemas y Soluciones ofrecemos equipos de marcas como HUENU, DLICAN, TENETH, HANRUN, XENONS, RISO, Sinajet y Konica Minolta. ¿Hay algo específico en lo que te pueda ayudar?

### Flujo 1 — Diagnóstico completo emprendedor — Turno 6
**Respuesta:**
Claro, para eso necesito algunos datos. ¿Me pasás tu nombre, teléfono y de dónde escribís?

### Flujo 1 — Diagnóstico completo emprendedor — Turno 8
**Respuesta:**
Perfecto, Carla. Ahora, ¿me pasás tu mail para enviarte más información sobre los equipos?

### Flujo 2 — Cotización directa (Regla 21 — caso crítico de v1.7) — Turno 2
**Respuesta:**
Para pasarte un presupuesto formal, necesito algunos datos. ¿Me pasás tu nombre, teléfono y de dónde escribís?

### Flujo 2 — Cotización directa (Regla 21 — caso crítico de v1.7) — Turno 4
**Respuesta:**
Gracias, Sergio. ¿Querés que te mande más información sobre los equipos por correo? Si es así, pasame tu mail.

### Flujo 3 — Distribuidor (Regla 5) — Turno 2
**Respuesta:**
Hola, bienvenido a Sistemas y Soluciones. 

---

¿Qué líneas de producto te interesan para la distribución?

### Flujo 3 — Distribuidor (Regla 5) — Turno 4
**Respuesta:**
Perfecto, gracias por la info. 

---

¿Me pasás tu nombre, teléfono y correo para que el equipo comercial se comunique con vos?

### Flujo 4 — Zona Interior con línea CABA-only (Regla 23 NUEVA) — Turno 4
**Respuesta:**
Perfecto. Para conectarte con nuestro equipo comercial, ¿me confirmás tu nombre, teléfono y desde dónde nos escribís?

### Flujo 7 — Showroom + financiación combinados (Regla 14) — Turno 6
**Respuesta:**
Perfecto, Lucas. ¿Me pasás tu mail así te mando más información sobre los equipos y las opciones de financiación?

### Flujo 8 — Usuario hostil (Regla 11) — Turno 2
**Respuesta:**
Lamento mucho la demora. Estoy acá para ayudarte. Contame, ¿en qué puedo asistirte hoy?

### Flujo 9 — Cliente con confusión equipos vs servicio (Regla 16) — Turno 2
**Respuesta:**
Sistemas y Soluciones vende equipos de impresión, no el servicio de impresión. Si necesitás a alguien que haga las banderas, tendrás que buscar un proveedor con el equipo adecuado.

---

¿Te interesa conocer los equipos que ofrecemos para imprimir banderas?

### Flujo 9 — Cliente con confusión equipos vs servicio (Regla 16) — Turno 4
**Respuesta:**
Entiendo, en ese caso te recomiendo buscar un proveedor que ofrezca servicios de impresión. Si en el futuro te interesa conocer más sobre nuestros equipos, estoy a disposición. Cualquier otra consulta, avisame. Saludos.

### Flujo 11 — Teléfono del chat (Regla 18 — caso de v1.5) — Turno 2
**Respuesta:**
Hola, Mariana. Bienvenida a Sistemas y Soluciones.

---

¿Qué tipo de trabajo pensás realizar con los equipos UV?

### Flujo 11 — Teléfono del chat (Regla 18 — caso de v1.5) — Turno 4
**Respuesta:**
Para comunicarte con la oficina, podés llamar al 4342-5742. 

---

Si querés que un representante te contacte, ¿me pasás tu número de teléfono acá en el chat?

### Flujo 11 — Teléfono del chat (Regla 18 — caso de v1.5) — Turno 6
**Respuesta:**
Gracias, Mariana. Ahora, ¿me podrías decir de dónde nos escribís? Así puedo derivarte al representante correcto.

### Flujo 12 — Sin captura completa, cierre limpio (Regla 19) — Turno 2
**Respuesta:**
Hola, bienvenido a Sistemas y Soluciones.

---

Trabajamos con varias tecnologías de impresión, como DTF Textil, DTF UV, UV, Sublimación, Eco-Solvente, Solvente, Corte, RISO, IDL Láser y Gran Formato. ¿Hay alguna en particular que te interese?

### Flujo 12 — Sin captura completa, cierre limpio (Regla 19) — Turno 4
**Respuesta:**
De nada. Cualquier cosa que necesites, estoy acá para ayudarte. Saludos.

### Flujo 13 — Notificar_lead falla por dato faltante (validación) — Turno 2
**Respuesta:**
Hola, Diego. Para conectarte con nuestro equipo comercial, ¿me confirmás desde dónde nos escribís y qué equipo o aplicación te interesa?

### Flujo 15 — Multi-canal: misma persona pero sesiones distintas — Turno 2
**Respuesta:**
Hola, bienvenido a Sistemas y Soluciones. ¿En qué te puedo ayudar hoy con la DTF para textil?

### Flujo 16 — Memoria persistente intraturno (Regla 25 + memoria) — Turno 2
**Respuesta:**
Hola, bienvenido a Sistemas y Soluciones.

---

¿Qué tipo de trabajo pensás realizar con la DTF textil?

### Flujo 16 — Memoria persistente intraturno (Regla 25 + memoria) — Turno 4
**Respuesta:**
Perfecto, Laura. Cuando estés lista, acá estoy para ayudarte. Cualquier cosa nos avisas, saludos.

### Flujo 16 — Memoria persistente intraturno (Regla 25 + memoria) — Turno 6
**Respuesta:**
Gracias por volver, Laura. Con ese volumen, la DTF textil es una buena opción. ¿Tenés algún requerimiento especial de calidad o velocidad?
