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
| 3 | `Hola, soy Pedro Gómez, tel 11-9876-5432, escribo desde Córdoba, necesito DTF, mi mail es pedro@empresa.com.uy` | Tiene los 4 datos + email en un solo mensaje. Invoca `[NOTIFICAR_LEAD]` Y `[GUARDAR_EMAIL]` en el mismo turno (regla operativa 7 + 13). NO continúa diagnóstico (Regla 13). Cierra con calidez. | `NOTIFICAR_LEAD`, `GUARDAR_EMAIL` | | | |
| 4 | `Mi mail es juan arroba gmail punto com` | Pide al cliente que lo confirme escrito (formato estándar). NO invoca `[GUARDAR_EMAIL]` con esa string mal formateada (la tool la rechazaría con `ERROR: formato inválido`). | `GUARDAR_EMAIL` | | | |
| 6 | `Quiero comprar tinta, podés mandarme un humano?` | Invoca `[CONSULTAR_URL_TIENDA]` para insumos online + ofrece alternativa de hablar con representante (Regla "tienda online" del prompt §286). | `CONSULTAR_URL_TIENDA` | | | |
| 13 | `Estoy interesada en la HANRUN HP3204 para etiquetas` | Invoca `[BUSCAR_EQUIPO]` con marca="HANRUN" + query="HP3204" + tecnologia="DTF UV" (asumiendo HANRUN es DTF UV). Devuelve la ficha del equipo + pregunta volumen o pasa a Etapa 4. | `BUSCAR_EQUIPO` | | | |
| 15 | `Quiero ver la Konica Minolta usada` | Invoca `[CONSULTAR_INVENTARIO_USADOS]` con tipo="" (cualquier) o si el cliente especificó BN/Color, con ese filtro. NO ofrece precio (la tool no devuelve precio). | `CONSULTAR_INVENTARIO_USADOS` | | | |
| 20 | `Cuánto sale 1 kg de tinta DTF?` | Para insumos invoca `[CONSULTAR_URL_TIENDA]` (§286). NO inventa precio. | `CONSULTAR_URL_TIENDA` | | | |

## Flujo C1 — Notificar_lead correcto + email después (regla op. 7)

| Turno | Rol | Mensaje | Resultado esperado | Tool requerida | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|----------------|-------------------|----|-------|
| 2 | Agente | `—` | Invoca `[NOTIFICAR_LEAD]` con los 4 datos + equipo="UV cama plana gran formato". Pide mail con frase Regla 4 ("Si querés, te mando más información..."). | `NOTIFICAR_LEAD` | | | |
| 4 | Agente | `—` | Invoca `[GUARDAR_EMAIL]` SOLO (no re-notifica). Cierre con calidez (Regla 19 + post-derivación). | `GUARDAR_EMAIL` | | | |

## Flujo C2 — Email espontáneo en medio de diagnóstico (regla op. 7)

| Turno | Rol | Mensaje | Resultado esperado | Tool requerida | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|----------------|-------------------|----|-------|
| 2 | Agente | `—` | Pregunta UNA cosa de contexto (Regla 5 distribuidor): qué zona o qué clientes atiende. Puede invocar `[CONSULTAR_LINEAS_PRIORIZADAS]`. | `CONSULTAR_LINEAS_PRIORIZADAS` | | | |
| 4 | Agente | `—` | Invoca `[GUARDAR_EMAIL]` en el MISMO turno (regla op. 7). Confirma brevemente sin sonar robótico. NO invoca notificar_lead todavía (faltan tel + ubicación). Sigue la conversación natural. | `GUARDAR_EMAIL` | | | |

## Flujo C3 — Mail mal formateado, reintento

| Turno | Rol | Mensaje | Resultado esperado | Tool requerida | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|----------------|-------------------|----|-------|
| 4 | Agente | `—` | Invoca `[GUARDAR_EMAIL]` con email="juanperez@hotmail.com". Confirma brevemente. | `GUARDAR_EMAIL` | | | |

## Flujo C4 — Mismo email guardado dos veces (already_exists)

| Turno | Rol | Mensaje | Resultado esperado | Tool requerida | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|----------------|-------------------|----|-------|
| 2 | Agente | `—` | Invoca `[GUARDAR_EMAIL]`. La tool devuelve `already_exists: true`. El agente sigue natural — NO menciona explícitamente "ya estabas registrado". Continúa con la conversación normal. | `GUARDAR_EMAIL` | | | |

## Flujo C5 — Cliente cambia de tecnología en el medio

| Turno | Rol | Mensaje | Resultado esperado | Tool requerida | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|----------------|-------------------|----|-------|
| 2 | Agente | `—` | Invoca `[CONSULTAR_APLICACION]` con descripcion="imprimir remeras". Recomienda DTF Textil. Pregunta volumen. | `CONSULTAR_APLICACION` | | | |
| 4 | Agente | `—` | Se adapta. NO insiste con DTF. Invoca `[CONSULTAR_APLICACION]` con descripcion="UV acrílicos" o `[CONSULTAR_TECNOLOGIA]` UV. Recomienda equipos. | `CONSULTAR_APLICACION`, `CONSULTAR_TECNOLOGIA` | | | |

## Flujo C6 — Tool NOT_FOUND (anti-alucinación)

| Turno | Rol | Mensaje | Resultado esperado | Tool requerida | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|----------------|-------------------|----|-------|
| 2 | Agente | `—` | Invoca `[BUSCAR_EQUIPO]` con query="Mimaki CJV30". La tool devuelve NOT_FOUND (Mimaki no está en catálogo). Aclara que no comercializa Mimaki + ofrece alternativa real del catálogo (UV/Eco-Solvente de HUENU). NO inventa. | `BUSCAR_EQUIPO` | | | |

## Flujo C7 — Cliente acepta novedades sin haber sido derivado

| Turno | Rol | Mensaje | Resultado esperado | Tool requerida | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|----------------|-------------------|----|-------|
| 2 | Agente | `—` | Saluda, pregunta qué aplicación o tecnología le interesa. Puede invocar `[CONSULTAR_LINEAS_PRIORIZADAS]` para destacar líneas del mes. | `CONSULTAR_LINEAS_PRIORIZADAS` | | | |
| 6 | Agente | `—` | Invoca `[GUARDAR_EMAIL]`. Confirma brevemente. Cierre limpio. | `GUARDAR_EMAIL` | | | |

## Flujo C8 — Conflicto: cliente da datos pero también pide algo técnico

| Turno | Rol | Mensaje | Resultado esperado | Tool requerida | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|----------------|-------------------|----|-------|
| 2 | Agente | `—` | Responde la pregunta técnica brevemente (sí, DTF UV imprime sobre rígidos como madera/MDF). Confirma datos recibidos. Pide mail (Regla 4) o invoca `[NOTIFICAR_LEAD]` con los 4 datos (Pablo + tel + La Plata + DTF UV madera). | `NOTIFICAR_LEAD` | | | |

## Flujo C10 — Cliente pide marca que sí está pero modelo que no

| Turno | Rol | Mensaje | Resultado esperado | Tool requerida | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|----------------|-------------------|----|-------|
| 2 | Agente | `—` | Invoca `[BUSCAR_EQUIPO]` con query="HUENU FT9999". Si devuelve NOT_FOUND/AMBIGUOUS, aclara que ese modelo específico no está y ofrece alternativas reales de HUENU. NO inventa specs del FT9999. | `BUSCAR_EQUIPO` | | | |
