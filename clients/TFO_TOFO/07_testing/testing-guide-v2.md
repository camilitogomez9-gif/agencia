# Testing Guide — TOFO Pizza Agente Multi-canal
**Versión:** v2
**Prompt base:** B2B v1.2 / Servicio v1.1 / Reposición v1.1 / Derivación v1.1 / RRSS v1.1
**Fecha:** 2026-05-06

**Correcciones aplicadas en v1.2 del prompt B2B:** caso #10 (estimaciones — PASO 1 ahora pide costo de insumos, luz, internet)
**Casos nuevos agregados en v2 de la guía:** #37, #38

---

## Instrucciones para el tester

- Ejecutar cada caso en el canal indicado (WhatsApp, Instagram, o Facebook)
- Completar la columna **Resultado obtenido** con lo que respondió el agente (textual o parafraseo)
- Completar **OK** con: `true` / `false` / `parcial`
- Si es `false` o `parcial`, anotar qué falló en **Notas**

---

## BLOQUE 1 — Agente de Derivación: routing y siempre responder

| # | Mensaje de prueba | Resultado esperado | Resultado obtenido | OK | Notas |
|---|-------------------|-------------------|-------------------|----|----|
| 1 | (primer mensaje) "Hola" | Audio obligatorio activado + mensaje de bienvenida: nombre + ciudad. NO más preguntas. | | | |
| 2 | "Quiero una pizza" | Derivado a Agente RRSS. Respuesta sobre sabores/precios/ubicaciones. | | | |
| 3 | "La máquina no me dio mi pizza" | Derivado a Servicio al Cliente. Empatía + solicitar evidencia. NO silencio. | | | |
| 4 | "Quiero poner una máquina en mi negocio" | Derivado a Agente B2B. Saludo profesional + pedir nombre si no se tiene. | | | |
| 5 | (enviar un mensaje ininteligible o muy corto, ej: "sjdfkls") | Siempre responde algo. NO silencio. Pregunta qué necesita el usuario. | | | |

---

## BLOQUE 2 — Agente B2B: modelos de venta y objetivo llamada

| # | Mensaje de prueba | Resultado esperado | Resultado obtenido | OK | Notas |
|---|-------------------|-------------------|-------------------|----|----|
| 6 | "¿Cuánto cuesta la máquina?" | Menciona Opción A ($9,300 USD China) y Opción B ($26,300 USD México). NO menciona concesión ni franquicia. | | | |
| 7 | "¿Tienen franquicias?" | Responde que no hay franquicias ni concesiones. Solo venta directa (Opción A o B). | | | |
| 8 | "¿Venden los insumos?" | Responde que NO venden insumos pero asesoran sobre proveedores. | | | |
| 9 | "¿Me pueden mandar un brochure / PDF / dossier?" | NO promete ningún documento ni envío por correo. Redirige a llamada con director. Frase obligatoria presente: "Lo mejor es una llamada directa con el director para darte números reales según tu caso." | | | |
| 10 | "¿Cuánto puedo ganar con una máquina?" | Pide datos antes de dar números (ubicación, renta, tráfico, precio). NO da cifras sin contexto. | | | |
| 11 | "No tengo datos exactos" | Usa modelo base ($70 costo, $129 venta, 50 pizzas/día, renta $2,000). SIEMPRE incluye disclaimer: "Es un escenario general, puede variar…" y redirige a llamada con director. | | | |
| 12 | "Vi máquinas en Alibaba más baratas" | Menciona diferenciación: aranceles 40%, software en mandarín, sin soporte local. Explica que Opción B resuelve todo. | | | |
| 13 | "¿Cuáles son las condiciones de pago?" | Responde 50% al ordenar, 50% antes del envío. | | | |
| 14 | "¿Qué tan urgente es comprar?" | Menciona: aranceles subieron 40% desde enero, máquinas con arancel anterior disponibles, tipo de cambio favorable. | | | |
| 15 | "¿Necesito hacer instalación eléctrica?" | Responde: 220V/35A, internet. Nosotros NO hacemos instalación eléctrica. Sí hacemos configuración completa. | | | |
| 16 | "¿Cómo se controla la máquina?" | Responde: desde el celular. Nosotros acompañamos toda la configuración. | | | |
| 17 | "Quiero agendar una reunión" (desde Instagram) | Primero pide WhatsApp antes de agendar. NO agenda sin WhatsApp. | | | |
| 18 | "Quiero agendar una reunión" (desde WhatsApp) | NO pide WhatsApp (ya está ahí). Va directo a proponer día/hora. Horario: Lun-Vie 10:00-13:00. | | | |
| 19 | "Quiero reunión el sábado a las 3pm" | Responde que solo hay horarios Lun-Vie 10:00-13:00. Pide horario dentro del rango. | | | |

---

## BLOQUE 3 — Agente Servicio al Cliente: fallas, reset, validación

| # | Mensaje de prueba | Resultado esperado | Resultado obtenido | OK | Notas |
|---|-------------------|-------------------|-------------------|----|----|
| 20 | "La máquina no me dio la pizza y ya pagué" | Empatía + intento de reset primero (triángulo amarillo). NO escala directo a reposición. | | | |
| 21 | (tras intentar reset) "Ya reinicié y no funcionó" | Pide dos fotos: pantalla con error + comprobante de pago. NO genera código. NO ofrece reembolso. | | | |
| 22 | (envía solo una foto del error, sin ticket) | Pide también el comprobante de pago. NO avanza sin ambas fotos. | | | |
| 23 | (envía fotos) | Describe al cliente qué ve en la imagen del error + qué datos lee en el comprobante. NO asume que son válidas. | | | |
| 24 | "¡Estoy muy enojado! Cobró doble y no salió nada" | Empatía en 1 línea. POCAS preguntas (máximo pedir foto de error y ticket juntos). NO hacer flujo largo de preguntas. | | | |
| 25 | "¿Dónde están ubicados?" | Responde: Flex Norte, Flex Sur, UAG, Plaza Patria, Estación Juárez. NO menciona The Landmark ni La Gran Plaza. | | | |
| 26 | (silencio o mensaje sin sentido tras una consulta activa) | SIEMPRE responde algo. Nunca queda sin respuesta. | | | |

---

## BLOQUE 4 — Agente Reposición: validación y anti-fraude

| # | Mensaje de prueba | Resultado esperado | Resultado obtenido | OK | Notas |
|---|-------------------|-------------------|-------------------|----|----|
| 27 | (llega sin evidencia previa) "Dame un código de reposición" | Pide evidencia obligatoria: foto pantalla + foto ticket. NO genera código sin fotos. NO inventa código. | | | |
| 28 | (envía imagen de una captura de pantalla claramente genérica / de otra app) | Detecta que no es un comprobante real. NO genera código. Pide comprobante correcto. | | | |
| 29 | (envía foto de un ticket real) | Describe los datos que lee: monto, fecha, método de pago. Confirma coherencia con la falla reportada. | | | |
| 30 | "Dame un reembolso / quiero que me devuelvan el dinero" | Responde que solo se ofrecen códigos de reposición, no reembolsos. Tono empático pero firme. | | | |
| 31 | (datos coherentes, fotos válidas) | Genera código usando herramienta 'codigo_reposicion'. NO inventa código. Entrega en formato estándar con vencimiento 3 días. | | | |

---

## BLOQUE 5 — Agente RRSS: ubicaciones y geo

| # | Mensaje de prueba | Resultado esperado | Resultado obtenido | OK | Notas |
|---|-------------------|-------------------|-------------------|----|----|
| 32 | "¿Dónde están?" | Primero pregunta zona para orientar al punto más cercano. | | | |
| 33 | "Estoy en Zapopan norte" | Menciona Flex Norte. NO menciona The Landmark. | | | |
| 34 | "Estoy en el centro" | Menciona Estación Juárez. | | | |
| 35 | "Estoy en Monterrey" | NO envía ubicaciones. Responde que por ahora solo están en Guadalajara. Ofrece info de negocio B2B. | | | |
| 36 | "Quiero poner una máquina en mi ciudad" | Deriva al área B2B. Frase: "con gusto te cuento cómo funciona" o similar. | | | |

---

---

## BLOQUE 6 — Agente B2B: estimaciones con variables completas (nuevo en v2)

| # | Mensaje de prueba | Resultado esperado | Resultado obtenido | OK | Notas |
|---|-------------------|-------------------|-------------------|----|----|
| 37 | "¿Cuánto puedo ganar si tengo el local en un mall de CDMX, renta $8,000, tráfico de 2,000 personas?" | Pide también: precio de venta, costo de insumos, costo de luz, costo de internet — antes de dar proyección. NO da cifras con solo 3 datos. | | | |
| 38 | "No tengo los datos de luz ni internet todavía" | Usa el modelo base para esos ítems y aclara que el cliente debe cotizarlos localmente. SIEMPRE incluye disclaimer de escenario general + redirige a llamada con director. | | | |

---

## Resumen de cobertura

| Agente | Casos | Críticos |
|--------|-------|---------|
| Derivación | 1–5 | #5 (siempre responder) |
| B2B | 6–19, 37–38 | #7 (no franquicias), #9 (no dossier), #10-11 (estimaciones), #17-18 (canal WA), #37-38 (variables completas) |
| Servicio al Cliente | 20–26 | #20 (reset primero), #21-22 (validación fotos), #24 (cliente molesto) |
| Reposición | 27–31 | #27 (no código sin fotos), #28 (anti-fraude), #30 (no reembolso) |
| RRSS | 32–36 | #33-34 (ubicaciones actualizadas), #35 (fuera de GDL) |
