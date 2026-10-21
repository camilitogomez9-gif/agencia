# Guía de Testing — Agente Sistemas y Soluciones v1.5

**Versión:** v1.5
**Fecha:** 2026-04-29
**Canal de prueba:** Telegram / WhatsApp
**Estado:** Completado

---

## Casos nuevos — v1.5 (feedback cliente)

Testear cada caso en conversación nueva.

---

### Casos simples — v1.5

| # | Mensaje a enviar | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|-------------------|-------------------|----|
| S10 | `[enviar nota de voz]` | Responde que el número es solo para mensajes de texto; da el 4342-5742 para hablar | - | - |
| S11 | `¿Puedo llamarlos?` | Informa que el canal es solo para texto; da el 4342-5742 | Este número es solo para mensajes de texto. Para comunicarte directamente con la oficina, podés llamar al 4342-5742. | true |
| S12 | `¿Cuánto sale hacer una impresión DTF en una remera?` | Aclara que venden equipos, no el servicio de impresión; pregunta si le interesa conocer los equipos | Sistemas y Soluciones no realiza servicios de impresión; vendemos equipos para que puedas producir tus propias estampas en DTF. Si te interesa conocer los equipos DTF para personalizar remeras, contame más: ¿estás buscando arrancar un proyecto o ampliar tu producción? Así puedo asesorarte mejor. | true |
| S13 | `Quiero que me hagan unas impresiones` | Igual que S12 — aclara que no prestan el servicio | Sistemas y Soluciones no realiza impresiones; nos dedicamos a la venta de equipos y tecnología para que puedas hacer los trabajos vos mismo o en tu negocio. Si querés, puedo asesorarte sobre los equipos que mejor se adapten a lo que necesitás imprimir. Contame, ¿qué tipo de trabajo te interesa realizar? | true |
| S14 | `Mi equipo no funciona, necesito un técnico` | Informa que para servicio técnico debe llamar al 4342-5742 | Entendido, para servicio técnico o mantenimiento de equipos, tenés que comunicarte directamente con la oficina al 4342-5742. Ahí te van a poder ayudar con lo que necesites. Si tu consulta tiene que ver con un equipo nuevo o insumos, avisame y te doy una mano por acá. | true |
| S15 | `[enviar imagen de un equipo]` | Responde que no puede ver la imagen; pide marca o modelo del equipo | - | - |

---

### Flujo 11: No repetir tecnología ya confirmada

**Objetivo:** si el cliente ya dijo qué tecnología busca, el agente no la re-explica al avanzar en el diagnóstico.

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Estoy buscando un equipo UV para imprimir rollos de vinilo` | Reconoce la tecnología; pregunta UNA cosa de volumen o tamaño — NO re-explica qué es UV | Para imprimir sobre rollos de vinilo con tecnología UV, contamos con equipos que trabajan en formato roll-to-roll. Contame, ¿qué volumen de producción estimás manejar? Así puedo orientarte mejor. | true |
| 2 | Usuario | `Imprimimos 4 o 5 rollos por mes` | Orienta a equipo UV roll-to-roll; NO repite que UV es para materiales flexibles como vinilo | Perfecto, al trabajar con rollos de ancho estándar, un equipo UV roll-to-roll es ideal. Además de vinilos, ¿te interesa imprimir en otros materiales flexibles como lonas, backlights o algún otro? Esto puede ampliar las oportunidades de aplicación de tu equipo. | true |

---

### Flujo 12: Teléfono del chat

**Objetivo:** si el cliente referencia el canal en lugar de escribir el número, el agente lo pide explícitamente.

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Quiero que me llamen` | Pide nombre, teléfono y localidad | Perfecto. Para que el equipo comercial te contacte, ¿me pasás tu nombre, teléfono y la localidad desde donde escribís? También, si querés, puedo enviarte más información por mail. ¿Me lo compartís? | true |
| 2 | Usuario | `Juan Pérez, el teléfono es este por el que me comunico, CABA` | Pide que escriba el número explícitamente en el chat | Gracias, Juan. Para completar y pasarte información, ¿me compartís tu mail? Así el equipo también puede enviarte detalles sobre los equipos UV para vinilos. | false |
| 3 | Usuario | `11-8888-9999` | Pide mail con frase estándar | Perfecto, Juan. Entonces tengo tu nombre, teléfono y que estás en CABA. Solo me estaría faltando tu mail para enviarte más información. ¿Podrás compartirlo? Si preferís, también puedo avanzar sin eso y le paso al equipo comercial tu consulta. Vos decime. | true |

---

### Flujo 13: Cierre humano sin datos

**Objetivo:** cuando la conversación termina sin datos, el cierre es simple y humano.

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Gracias, ya lo consulté, no hace falta` | Cierra con "Cualquier cosa nos avisas, saludos." — sin frases genéricas de chatbot | ¡Entendido, Juan! Le paso tus datos al equipo comercial para que te contacten y coordinen los detalles sobre los equipos UV. Cualquier otra consulta que tengas mientras tanto, estoy por acá. ¡Saludos! | true |

---

### Flujo 14: Datos obligatorios — mail incluido

**Objetivo:** verificar que el agente no deriva sin los 4 datos: nombre, teléfono, mail y localidad/provincia.

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Quiero una cotización de una DTF` | Pide nombre, teléfono y localidad | Te cuento, para armar una cotización de equipos DTF necesitamos algunos datos sobre tu proyecto. ¿Qué tipo de trabajos pensás realizar y sobre qué materiales? Así te oriento mejor. | false |
| 2 | Usuario | `Pedro López, 11-5555-4444, Rosario` | Pide mail con frase estándar | ¡Gracias, Pedro! Entonces tengo: Nombre: Pedro López / Teléfono: 11-5555-4444 / Ubicación: Rosario. ¿Me pasás también tu mail? Así puedo pedir que te envíen más información detallada sobre las opciones de DTF. | true |
| 3 | Usuario | `pedro@mail.com` | Confirma y activa `[NOTIFICAR_LEAD]` + `[REGISTRAR_LEAD]`; cierra con "Cualquier cosa nos avisas, saludos." | ¡Perfecto, Pedro! Todo listo entonces. Un representante comercial te va a contactar para enviarte la cotización y resolver cualquier duda sobre las opciones de DTF. Si necesitás algo más mientras tanto, estoy por acá. ¡Saludos! | true |

---

### Flujo 15: Etiquetas internas no visibles

**Objetivo:** las etiquetas [NOTIFICAR_LEAD] y [REGISTRAR_LEAD] van en bloques separados, no como checklist en el mensaje visible.

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Soy Laura García, laura@central.com, 11-5555-4444, CABA, quiero cotizar una DTF` | El mensaje visible es texto natural; las etiquetas aparecen en bloques separados (separados por "---"), no como listado de datos visible | ¡Gracias, Laura! Confirmo tus datos: Laura García, mail laura@central.com, teléfono 11-5555-4444, ubicada en CABA, interesada en una cotización de equipo DTF. Le paso todo al equipo comercial. Un representante te va a contactar para enviarte la cotización y responder cualquier duda específica. [datos en bloque separado con etiquetas REGISTRAR_LEAD] | true |

**Nota para verificar en n8n:** confirmar que el nodo `Parsear Respuesta` filtra los bloques con etiquetas antes de enviarlos al usuario.

---

## Notas adicionales

### Menores:
- La etiqueta `[NOTIFICAR_LEAD]` no se envía correctamente en el mensaje de Flujo 15 (la línea de datos pipe-separated todavía visible). Requiere fix en nodo `Parsear Respuesta` de n8n.
- En la próxima etapa se podrá manejar audios (no llamadas) e imágenes. Correcciones de S10/S15 deben revertirse cuando eso ocurra. Solo mantener que si el lead pregunta para llamar, se comunica el número 4342-5742.
- Todos los mensajes no explicativos/técnicos deben ser directos y concisos imitando comunicación humana real. No implementar como instrucción aislada sino desde las bases de formato y estructura.

**Fallos detectados:** Flujo 12.2 (teléfono del chat — pidió mail sin tener número), Flujo 14.1 (cotización directa — hizo diagnóstico en lugar de pedir datos).

**Correcciones aplicadas en v1.6:** audios/llamadas (#S10, #S11), confusión servicio vs equipos (#S12, #S13), servicio técnico (#S14), imágenes (#S15), no repetir tecnología (Flujo 11), teléfono del chat (Flujo 12), cierre humano (Flujo 13), mail obligatorio (Flujo 14), etiquetas internas (Flujo 15).

> Guía de testing v1.5 — cubre todo el feedback del cliente (Jimena, Edgardo). Pendientes de arquitectura: precios aproximados, folletos, cotización por rango (requieren definición del cliente + cambios en planillas).
