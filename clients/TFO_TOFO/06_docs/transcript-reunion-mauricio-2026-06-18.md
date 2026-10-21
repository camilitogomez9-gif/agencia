```markdown
# Reunión Mauricio (TOFO) — 18/06/2026

**Fecha:** 2026-06-18
**Duración:** 28 min
**Modalidad:** Zoom
**Participantes:**
- la agencia (la agencia)
- Mauricio García de la Vega (dueño TOFO Pizza)
**Link Fathom:** https://fathom.video/share/PLjoHChjCF9nQKpHvyzZU9WHfhbm53zr

---

## Puntos relevantes detectados

### 1. Citas de Zoom no se están creando realmente (P0 — URGENTE)
El agente le dice al lead "te agendé Zoom" pero la meeting nunca se crea en la cuenta Zoom de Mauricio. Solo aparece en Google Calendar. Mauricio ha tenido que crear cada meeting a mano y reenviar el link al lead. Hipótesis: la credencial Zoom OAuth2 configurada en n8n (`zoomOAuth2Api` id `TllmBz0re6WGmTw2`) no es la cuenta real de Mauricio — probablemente fue una cuenta pre-creada que la agencia asumió que era la correcta. Mauricio se comprometió a pasar credenciales Zoom por WhatsApp.

### 2. Refinamiento de la regla de precio (P0 — CONTRADICE plan v1)
La regla implementada en el bump v1.8 (soltar precio proactivamente al detectar intención de compra) NO es lo que Mauricio quiere. El flujo correcto según Mauricio: el agente captura nombre + ubicación → pregunta al lead si quiere saber el precio → si dice sí, da el precio → ahí se evalúa interés. Razón: de 1063 contactos en 2 semanas, el 90% pregunta precio y se va. Capturar primero permite mantener data del lead para Airtable y cualificación posterior. Requiere bump v1.8 → v1.9 con reescritura de §9 (Escenario 2 + eliminar Escenario 3).

### 3. Airtable no captura datos del lead (P1)
Del registro 488 en adelante, todos los leads en Airtable dicen "contacto a redes sociales" porque solo se está escribiendo la info inicial (subscriber_id + canal). El nombre, ubicación y demás datos que el agente captura en la conversación no se persisten. Antes sí funcionaba — algún cambio en el workflow rompió la captura post-cualificación. Requiere diagnóstico del main workflow vivo y probablemente agregar nodo/tool de "Update Lead Airtable" que el agente invoque cuando tenga nombre + ubicación. Mauricio sigue haciendo el backfill manual con Claude.

### 4. Diferencia 1494 ManyChat vs 1113 Airtable = ~400 leads faltantes (P1)
Mauricio detectó que faltan ~400 leads en Airtable vs ManyChat. Criterio que define Mauricio para considerar un lead "de interés" digno de estar en Airtable: lead que dejó **nombre + ubicación**. Probablemente el mismo nodo de write/update soluciona este y el punto 3. Mauricio quiere subir los 1494 de inmediato — bloqueo es el límite del plan free Airtable (ver punto 5).

### 5. Límite Airtable plan free (1000 records) bloqueante operativo (P2)
Mauricio ya superó los 1000 records y Airtable empezó a cobrar / borrar. Pregunta directa: "¿Tú qué piensas que me conviene?". Opciones a analizar: upgrade plan Team (~$20-24 USD/mes), auto-cleanup de records antiguos via workflow n8n, o híbrido (upgrade temporal + auto-archive a Google Sheets cada 3 meses). Recomendación por defecto: upgrade plan, con confirmación del monto exacto a Mauricio. Doc a crear: `airtable-plan-decision-2026-06-19.md`.

### 6. Envío automático de ficha técnica + video de funcionamiento (P2)
Mauricio quiere que el agente B2B envíe automáticamente: (a) la ficha técnica de la máquina (PDF) cuando el lead pregunte por el costo, (b) el video de funcionamiento cuando pregunten cómo funciona la máquina. Mauricio mandó los 2 archivos (PDF + video). Hay que: localizar los archivos y publicarlos en URL pública, crear 2 sub-workflows / tools (`enviar_ficha_tecnica` + `enviar_video_funcionamiento`), **eliminar la regla anti-archivos genérica** del prompt B2B que dice "prohibido mandar PDFs/videos" — esa regla está haciendo que el agente diga "tenemos prohibido mandar videos", lo cual es falso y frena ventas.

### 7. Scope reducido del paquete fallas — re-presupuestar (P3)
La propuesta original del paquete de fallas (USD ~1000+) le pareció cara a Mauricio. Pide reducir el alcance: sin ManyChat, WhatsApp Business directo a n8n, sin memoria, conversaciones cortas de un día sin seguimiento. Mantener sub-workflow elevación al técnico (solo Telegram), guías cortas, sesión handoff 60 min. Requiere análisis de cómo conectar WhatsApp → n8n sin ManyChat (WhatsApp Business API directa vs Evolution API vs whatsapp-web.js — tradeoffs costo/complejidad/fragilidad). Recalcular esfuerzo (probablemente 30-40% menos). Mauricio acepta escalonar pago.

---

## Citas verbatim relevantes

### Sobre citas Zoom no creadas
> "No está haciendo las citas en Zoom aún. Les dice al cliente que le hizo la cita en Zoom, pero no la hace. Entonces no me aparece en mi calendario de Zoom ni nada. Yo he tenido que ir uno por uno revisando."

### Sobre regla de precio (CONTRADICE plan v1)
> "Yo lo que pensaba era, cuando le diga el nombre y dónde está, entonces le da el precio. Cuando le diga el nombre y dónde está, le pregunta si quiere saber el precio de la máquina, la TOFO pizza, y si dice que sí, le da el precio. Y después ahí vemos si la persona está interesada o no."

### Sobre Airtable no captura datos
> "Inertable [Airtable] no está llenando los campos como los llenaba antes. Yo lo estoy teniendo que hacer con Cloud."

> "Del renglón 488 para arriba, todos dicen 'contacto a redes sociales' porque no cogieron nada más de información, solo cogieron la información inicial, no cogieron ni el nombre ni nada."

> "Antes sí me daba toda la información que tú ya ves después, antes sí la metía directamente el N8N y ahora ya no lo hace."

### Sobre diferencia ManyChat vs Airtable
> "¿Por qué tengo 1113 records en Airtable y tengo en ManyChat 1494? Me faltan 400 leads."

> "Yo creo que se tienen que registrar todos los que dejen nombre y lugar de donde están ubicados — esa ya es una señal de interés para mí."

### Sobre límite Airtable
> "Ya pasé los mil records y ya me borró todo. Y ahora qué? Request of Raid. Estos cabrones ya me van a cobrar."

> "¿Tú qué piensas que me conviene?"

### Sobre ficha técnica + video
> "Tengo una ficha técnica porque muchos preguntan, '¿tienes una ficha técnica de la máquina?'. Tú, cuando te pregunta el costo, inmediatamente manda la ficha técnica. Pregunta costo, ficha técnica. ¿Cómo funciona la máquina? Le pasas el video."

> "Porque ahora la gente está contestando '¿tenemos prohibido mandar videos?' No es cierto."

### Sobre scope reducido paquete fallas
> "Me pareció muy cara tu herramienta. Está mucho más caro que lo que me cobraste a mí por hacerlo. Me cobraste 500. Ahora me estás cobrando mil y tantos. Joder, esto es muchísimo."

> "No necesitamos ni siquiera meterle ManyChat a este cliente. Va a tener un número de WhatsApp que va a abrir con WhatsApp Business. Y ese número de WhatsApp lo va a tener ahí él en su máquina."

> "Yo inicialmente no tenía ManyChat. Yo tenía solamente el WhatsApp. Y me contestaban en el WhatsApp directo."

### Sobre propuestas manuales (NO automatizar)
> "Yo a varios, en las pláticas, he mandado en las conversaciones de ManyChat varias propuestas. A mí me gustaría que eso poder ver, aquí les he mandado propuestas, ya en mi listado de Airtable."

> "Yo hago una curación en Cloud para que me diga cuál es ya recibida [propuesta] y me los cambio. Más fácil para no iniciar la cantidad."

### Sobre pago escalonado
> "Lo vamos escalando y te voy pagando."

---

## Decisiones tomadas en la llamada

| # | Decisión | Quién | Estado |
|---|----------|-------|--------|
| 1 | Mauricio pasa credenciales Zoom OAuth2 (cuenta real TOFO) por WhatsApp | Mauricio | ⏳ Pendiente envío |
| 2 | Mauricio acepta scope reducido para paquete fallas (sin ManyChat, sin memoria, WhatsApp Business directo) | Mauricio | ✅ Aceptado |
| 3 | Mauricio NO quiere automatización de propuestas manuales — las cura él con Claude | Mauricio | ✅ Cerrado, NO automatizar |
| 4 | Mauricio quiere envío automático de ficha técnica + video — ya mandó los 2 archivos | Mauricio + la agencia | 🟢 En implementación |
| 5 | Mauricio reportó síntomas Airtable (488+ registros parciales, faltan 400 leads vs ManyChat) — diagnóstico técnico pendiente | la agencia | ⏳ Pendiente diagnóstico |
| 6 | Mauricio acepta upgrade Airtable como recomendación, pendiente confirmación del monto exacto del plan | la agencia → Mauricio | ⏳ Pendiente mensaje con número |
| 7 | Revertir regla de precio del bump v1.8 — escenario correcto es "preguntar consentimiento después de capturar nombre + ubicación" | la agencia | 🟢 En implementación (bump v1.9) |
| 8 | Mauricio acepta pago escalonado del paquete fallas | Mauricio | ✅ Aceptado |
| 9 | Backfill manual de los ~580 registros viejos de Airtable lo sigue haciendo Mauricio con Claude — fuera de scope técnico | Mauricio | ✅ Cerrado |

---

## Pendientes abiertos

### Mauricio
- [ ] Enviar credenciales Zoom OAuth2 (cuenta real TOFO) por WhatsApp.
- [ ] Confirmar decisión sobre plan Airtable cuando llegue el mensaje con monto exacto.
- [ ] Confirmar decisión sobre nueva propuesta paquete fallas (alcance reducido) cuando llegue re-presupuesto.

### la agencia (la agencia)
- [ ] Bump prompt B2B v1.8 → v1.9 (regla precio reescrita + ficha técnica + video autorizados + tools nuevas).
- [ ] Bump testing-guide v6 → v7 (§J reescrito + §M ficha/video + §N Airtable captura + §Zoom esqueleto).
- [ ] Reconfigurar credencial Zoom en n8n cuando Mauricio mande credenciales.
- [ ] Smoke test E2E Zoom (verificar meeting aparece en dashboard Mauricio real).
- [ ] Diagnosticar nodo Airtable del main workflow vivo (causa del bug de captura 488+).
- [ ] Implementar nodo/tool `Update Lead Airtable` invocable por el agente al capturar nombre + ubicación.
- [ ] Localizar los 2 archivos (ficha técnica PDF + video) y publicar en URLs públicas.
- [ ] Crear sub-workflows `enviar_ficha_tecnica` + `enviar_video_funcionamiento`.
- [ ] Cablear las 2 tools nuevas al main del agente B2B.
- [ ] Crear doc `airtable-plan-decision-2026-06-19.md` con análisis A/B/C + mensaje a Mauricio.
- [ ] Crear doc `airtable-diagnostico-captura-datos-2026-06-19.md` con plan técnico de fix.
- [ ] Crear doc `zoom-credencial-fix-2026-06-19.md` con registro del incidente + plan de fix.
- [ ] Analizar alternativas WhatsApp → n8n sin ManyChat (WhatsApp Business API directa vs Evolution API vs whatsapp-web.js) para paquete fallas.
- [ ] Recalcular esfuerzo la agencia para paquete fallas (probablemente 30-40% menos vs original).
- [ ] Crear `propuesta-paquete-agente-fallas-mauricio-2026-06-19.md` con scope reducido + nuevo presupuesto.
- [ ] Actualizar CLAUDE.md raíz con bloques P0/P1/P2/P3 nuevos.
- [ ] Mandar mensaje WhatsApp TikTok ManyChat (plan v1, sigue pendiente).
```