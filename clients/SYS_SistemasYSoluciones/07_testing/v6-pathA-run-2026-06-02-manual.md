# Testing Manual — Casos con Tool Calls

> ⚠️ Estos casos requieren verificación humana porque dependen de herramientas
> reales de n8n que no se pueden simular via API.

---

## Instrucciones
1. Ejecutar cada caso en n8n o en el canal real
2. Completar **Resultado obtenido** con la respuesta del agente
3. Marcar **OK** como `true`, `false` o `parcial`
4. Verificar que la tool call se activó correctamente (ver logs de n8n)

---

## Casos Simples

| # | Mensaje | Resultado esperado | Tool requerida | Resultado obtenido | OK | Notas |
|---|---------|-------------------|----------------|-------------------|----|-------|
| 1 | `Hola` | Saluda como Aurora, presenta a Sistemas y Soluciones, hace UNA pregunta abierta. NO pide datos. NO incluye etiquetas tipo [NOTIFICAR_LEAD] como texto. Máximo 2 bloques. | `NOTIFICAR_LEAD` | | | |
| 3 | `Hola, soy Juan, mi tel es 11-5555-1234, escribo desde Rosario y necesito una cotización de impresora UV` | Confirma datos recibidos brevemente, invoca tool `[NOTIFICAR_LEAD]` con esos datos, cierra con calidez. Una sola respuesta (Regla 13 dump de datos). | `NOTIFICAR_LEAD` | | | |
| 5 | `Qué es DTF?` | Invoca tool `[CONSULTAR_TECNOLOGIA]` con tecnologia="DTF Textil". Integra la descripción natural sin decir "según mi base de datos". | `CONSULTAR_TECNOLOGIA` | | | |
| 6 | `Diferencia entre DTF y UV?` | Invoca máximo 2 tools (`[CONSULTAR_TECNOLOGIA]` para ambas) y devuelve comparativa breve, no más de 3 puntos por una (Regla 24). | `CONSULTAR_TECNOLOGIA` | | | |
| 7 | `Hacen cuotas?` | Invoca tool `[CONSULTAR_FAQ]` categoría Financiación. Responde con la respuesta corta + ofrece derivar al rep. | `CONSULTAR_FAQ` | | | |
| 8 | `Tienen showroom?` | Invoca tool `[CONSULTAR_FAQ]` categoría Showroom. Responde con respuesta corta + pide datos para coordinar visita. | `CONSULTAR_FAQ` | | | |
| 9 | `Dónde compro tintas?` | Invoca tool `[CONSULTAR_URL_TIENDA]`. Responde con la URL + opción de hablar con representante. | `CONSULTAR_URL_TIENDA` | | | |
| 15 | `Hola, quiero info sobre el equipo que ofrecen para imprimir en gorras` | Invoca tool `[CONSULTAR_APLICACION]` con descripcion="imprimir en gorras". Devuelve DTF Textil + ofrece ahondar en volumen. NO invoca notificar_lead todavía. | `CONSULTAR_APLICACION` | | | |

## Flujo 1 — Diagnóstico completo emprendedor

| Turno | Rol | Mensaje | Resultado esperado | Tool requerida | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|----------------|-------------------|----|-------|
| 2 | Agente | `—` | Invoca tool `[CONSULTAR_APLICACION]` con descripcion="estampar remeras". Recomienda DTF Textil con explicación breve. Pregunta volumen estimado (Etapa 3 — diagnóstico). | `CONSULTAR_APLICACION` | | | |
| 4 | Agente | `—` | Confirma que con ese volumen DTF Textil es ideal. Opcionalmente invoca tool `[BUSCAR_EQUIPO]` para mencionar un modelo. Pregunta presupuesto o pasa a captura. | `BUSCAR_EQUIPO` | | | |
| 10 | Agente | `—` | Invoca tool `[NOTIFICAR_LEAD]` con datos completos (nombre=Carla Pérez, telefono=11-4444-5555, ubicacion=Lanús, mail=carla.perez@gmail.com, equipo_o_aplicacion=DTF Textil estampado remeras, perfil=emprendedor). Confirma derivación, cierra con calidez. | `NOTIFICAR_LEAD` | | | |

## Flujo 2 — Cotización directa (Regla 21 — caso crítico de v1.7)

| Turno | Rol | Mensaje | Resultado esperado | Tool requerida | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|----------------|-------------------|----|-------|
| 6 | Agente | `—` | Invoca tool `[NOTIFICAR_LEAD]` con todos los datos. NO continúa diagnóstico. Cierra. | `NOTIFICAR_LEAD` | | | |

## Flujo 3 — Distribuidor (Regla 5)

| Turno | Rol | Mensaje | Resultado esperado | Tool requerida | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|----------------|-------------------|----|-------|
| 6 | Agente | `—` | Invoca tool `[NOTIFICAR_LEAD]` con perfil=Distribuidor, todos los datos + tecnologia_interes="DTF Textil, UV". Cierra. | `NOTIFICAR_LEAD` | | | |

## Flujo 4 — Zona Interior con línea CABA-only (Regla 23 NUEVA)

| Turno | Rol | Mensaje | Resultado esperado | Tool requerida | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|----------------|-------------------|----|-------|
| 2 | Agente | `—` | Invoca tool `[BUSCAR_EQUIPO]` con linea="Konica Minolta IDL", zona_cliente="Interior". Si el equipo está solo en CABA/GBA, aclara la limitación antes de avanzar. Pregunta si le interesa igual derivar para evaluar opciones. | `BUSCAR_EQUIPO` | | | |
| 6 | Agente | `—` | Invoca tool `[NOTIFICAR_LEAD]` con perfil=Pyme, ubicacion=Salta, zona derivada=Interior. Cierra. | `NOTIFICAR_LEAD` | | | |

## Flujo 5 — Tool retorna NOT_FOUND (anti-alucinación)

| Turno | Rol | Mensaje | Resultado esperado | Tool requerida | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|----------------|-------------------|----|-------|
| 2 | Agente | `—` | Invoca tool `[CONSULTAR_APLICACION]` o `[BUSCAR_EQUIPO]`. La tool retorna NOT_FOUND. El agente NO inventa specs. Responde "Eso no está dentro de lo que ofrecemos" o "Dejame verificar con el equipo". Ofrece derivar al rep si tiene contacto. | `CONSULTAR_APLICACION`, `BUSCAR_EQUIPO` | | | |

## Flujo 6 — Compatibilidad de sustrato

| Turno | Rol | Mensaje | Resultado esperado | Tool requerida | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|----------------|-------------------|----|-------|
| 2 | Agente | `—` | Invoca tool `[CONSULTAR_COMPATIBILIDAD]` con tipo_consulta="equipo_sustrato", equipo="Mimaki UJF", elemento="vidrio". Responde si es compatible + notas. | `CONSULTAR_COMPATIBILIDAD` | | | |
| 4 | Agente | `—` | Invoca tool `[CONSULTAR_URL_TIENDA]` con producto o categoría tinta. Devuelve URL + opción de hablar con rep. | `CONSULTAR_URL_TIENDA` | | | |

## Flujo 7 — Showroom + financiación combinados (Regla 14)

| Turno | Rol | Mensaje | Resultado esperado | Tool requerida | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|----------------|-------------------|----|-------|
| 2 | Agente | `—` | Invoca tool `[CONSULTAR_FAQ]` categoría Showroom. Responde corta + pide datos para coordinar. Pide nombre primero. | `CONSULTAR_FAQ` | | | |
| 4 | Agente | `—` | Invoca tool `[CONSULTAR_FAQ]` categoría Financiación. Responde corta. Sigue captura de datos: pide teléfono. | `CONSULTAR_FAQ` | | | |
| 8 | Agente | `—` | Invoca tool `[NOTIFICAR_LEAD]` con todos los datos + nota "Quiere coordinar showroom + financiación". Cierra. | `NOTIFICAR_LEAD` | | | |

## Flujo 8 — Usuario hostil (Regla 11)

| Turno | Rol | Mensaje | Resultado esperado | Tool requerida | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|----------------|-------------------|----|-------|
| 4 | Agente | `—` | Invoca tool `[NOTIFICAR_LEAD]` con urgencia=true. Confirma derivación inmediata. Pide mail con frase exacta. Cierra con compromiso de respuesta rápida. | `NOTIFICAR_LEAD` | | | |

## Flujo 10 — Anti-repetición de productos (Regla 25 NUEVA)

| Turno | Rol | Mensaje | Resultado esperado | Tool requerida | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|----------------|-------------------|----|-------|
| 2 | Agente | `—` | Invoca tool `[BUSCAR_EQUIPO]` con tecnologia="DTF Textil". NO menciona DTF-PRO-600 (ya en productos_mostrados). Presenta una alternativa distinta. Si la tool devuelve solo DTF-PRO-600 (única en catálogo), aclara que es la única disponible en esa línea y ofrece derivar al comercial. | `BUSCAR_EQUIPO` | | | |

## Flujo 13 — Notificar_lead falla por dato faltante (validación)

| Turno | Rol | Mensaje | Resultado esperado | Tool requerida | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|----------------|-------------------|----|-------|
| 4 | Agente | `—` | Ahora tiene los 4. Invoca tool `[NOTIFICAR_LEAD]`. Cierra. | `NOTIFICAR_LEAD` | | | |

## Flujo 14 — Líneas priorizadas del mes (Regla 23 + tool nueva)

| Turno | Rol | Mensaje | Resultado esperado | Tool requerida | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|----------------|-------------------|----|-------|
| 2 | Agente | `—` | Puede invocar tool `[CONSULTAR_LINEAS_PRIORIZADAS]` (opcional al inicio) Y/O `[CONSULTAR_APLICACION]`. Recomienda RISO. La promo se menciona sutilmente, no como anuncio. Pregunta volumen estimado. | `CONSULTAR_LINEAS_PRIORIZADAS`, `CONSULTAR_APLICACION` | | | |
| 4 | Agente | `—` | Invoca tool `[BUSCAR_EQUIPO]` con linea="RISO". Presenta modelo. Pregunta presupuesto o pasa a captura. | `BUSCAR_EQUIPO` | | | |
