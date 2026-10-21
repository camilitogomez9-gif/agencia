# Workflows GHL — Happy Flops

> **Etapa 3.** Especificación de los 6 GHL Workflows que gobiernan la operación del agente. Cada workflow se documenta con trigger, filtros, branching y acciones.

> 🔒 **NOMBRES Y KEYS REALES en M2 (2026-06-19):** este doc usa stages en inglés (`Greeting Sent`, `Quoted`...) y Custom Value keys snake_case-inglés (`vacaciones_active`, `re_engagement_fase1_waves`...). La implementación real usa nombres en español + keys autogeneradas por GHL — ver `04_guia_migracion/02_pipeline_y_campos.md` §2.1 (stages) y §2.5 (mapeo CV keys). Al implementar, manda M2.

---

## §1. Resumen de workflows

| ID | Nombre | Trigger | Propósito |
|---|---|---|---|
| WF-01 | **Inbound Router** | Customer Replied (inbound message en cualquier canal) | Recibir mensaje, filtrar por stage/tag, enviar a n8n |
| WF-02 | **Re-engagement Dual** | Custom Field `last_outbound_at` actualizado | Fase 1 (waves cortas) + Fase 2 (campaña 7 días) |
| WF-03 | **Inactivity Sweep** | Schedule diario 03:00 AM México | Mueve `En espera` → `Ventas Perdidas Real` tras 6m |
| WF-04 | **Pago Detectado** | HTTP webhook desde n8n (Vision Classifier devuelve `payment_proof`) | Mueve stage según contexto + notifica Telegram |
| WF-05 | **Business Hours / Vacaciones** | Customer Replied + filter `business_hours = OFF` o `vacaciones_active = true` | Auto-reply fuera de horario |
| WF-06 | **Stage Transitions** | Custom Field actualizado / Outbound Message Sent con patterns | Mueve stage del Opportunity según señales del Vendedor |

> **Nota arquitectónica:** GHL Workflows tiene primitivas limitadas comparado con n8n. Lo que no se pueda hacer "nativo" se delega a un endpoint n8n vía HTTP action. **No metemos lógica de IA en GHL** — GHL solo orquesta CRM y comunicación.

---

## §2. WF-01 — Inbound Router

**Propósito:** punto de entrada de todo mensaje del lead. Decide si enrutar al Vendedor o al humano.

### §2.1 Trigger

`Customer Replied` (cualquier canal — WhatsApp, IG, FB)

### §2.2 Filtros iniciales

```
IF Pipeline = "Pipeline IA"  (auto, el workflow vive en este pipeline)
AND Opportunity.tag NOT CONTAINS "human_takeover"
AND Opportunity.stage IN ["New Lead", "Greeted", "Event Identified",
                          "Products Shown", "Quoted", "En espera"]
AND Custom Value vacaciones_active = false
```

Si NO cumple: workflow termina (mensaje queda en inbox para humano).

### §2.3 Branching por stage

```
Section A — stage = "New Lead":
    Apply Tag: greeted
    Send Message (WhatsApp): mensaje de saludo fijo (Custom Value mensaje_saludo)
    Wait 2s
    Send Message: parte 2 del saludo
    Wait 2s
    Send Message: parte 3 del saludo
    Update Custom Field: last_outbound_at = now()
    Move Stage: Greeted
    (NO se llama a n8n — el saludo es 100% determinístico)

Section B — stage IN ["Greeted", "Event Identified", "Products Shown",
                       "Quoted", "En espera"]:
    HTTP Action: POST a webhook n8n /inbound
      Body: {
        opportunity_id, contact_id, phone, message: {type, content, media_url},
        stage, custom_fields: {...todos los del Opportunity},
        custom_values: {...los relevantes para el Vendedor}
      }
    (n8n procesa, llama LLM, envía respuesta vía GHL Conversations API)
```

### §2.4 Caso especial: imagen recibida en stage de pago

```
IF message.type = "image"
AND stage IN ["Awaiting Payment", "In Production", "Awaiting Final Payment"]
THEN:
    HTTP Action: POST a webhook n8n /vision-only
      Body: { opportunity_id, contact_id, image_url, stage }
    (n8n solo clasifica con Vision Classifier; si es payment_proof, dispara WF-04)
    (NO llama al Vendedor conversacional — IA está pausada en esas stages)
```

---

## §3. WF-02 — Re-engagement Dual

**Propósito:** sistema unificado de seguimientos. Reemplaza los 4 sub-workflows actuales.

### §3.1 Trigger

`Custom Field changed: last_outbound_at` (es decir, cada vez que el sistema le manda algo al lead, se reinicia el timer de re-engagement)

### §3.2 Filtros iniciales

```
IF Opportunity.stage IN ["Greeted", "Event Identified", "Products Shown", "Quoted"]
AND Opportunity.tag NOT CONTAINS "human_takeover"
AND Custom Field re_engagement_paused = false
```

### §3.3 Fase 1 — Waves cortas (1h / 3h / 5h)

```
[wait 1h]
  IF last_inbound_at > last_outbound_at   (lead respondió antes del wave)
    THEN: exit workflow (el siguiente mensaje del sistema reseteará el timer)
  ELSE:
    IF Custom Value re_engagement_fase1_active = true
    AND "P1_W1" IN Custom Value re_engagement_fase1_waves  (CSV "1h,3h,5h" → presencia de "1h" = "P1_W1" activo)
      THEN:
        HTTP Action: POST a n8n /generate-reengagement-message
          Body: { opportunity_id, wave: "P1_W1", context: {productos, evento, cotizacion} }
        Send Message (WhatsApp): response.text
        Update Custom Field: last_outbound_at = now()
        Update Custom Field: last_re_engagement_wave = "P1_W1"
        Apply Tag: re_engagement_phase_1
        HTTP Action: log a Supabase followups_log

[wait 2h]  (total 3h desde last_outbound_at original)
  Mismo patrón, wave = "P1_W2"

[wait 2h]  (total 5h)
  Mismo patrón, wave = "P1_W3"
```

### §3.4 Fase 2 — Campaña 7 días (configurable)

Después de los 5h sin respuesta, arranca la campaña:

```
[wait 19h]  (total 24h)
  IF last_inbound_at > last_outbound_at → exit
  ELSE:
    IF "R1" IN Custom Value re_engagement_fase2_active_days
      Generate + Send wave "P2_W1" (idem)
      Remove Tag: re_engagement_phase_1
      Apply Tag: re_engagement_phase_2

[wait 24h]  (total 48h, día 2)
  IF "R2" IN active_days → generate + send "P2_W2"

[wait 72h]  (total 120h, día 5)
  IF "R3" IN active_days → generate + send "P2_W3"

[wait 48h]  (total 168h, día 7 — ÚLTIMO DÍA)
  IF "R4" IN active_days → generate + send "P2_W4"
      (mensaje especial: "ÚLTIMO DÍA APROVECHA LA PROMO")

[wait 24h]  (total ~192h)
  IF lead siguió sin responder:
    Move Stage: En espera
    Update Custom Field: last_re_engagement_wave = "completed"
```

> **Flexibilidad clave:** Oscar edita `re_engagement_fase2_active_days = "R1,R2,R4"` (por ejemplo) → el workflow lee la lista cada vez que llega un wave y decide si dispararlo o saltarlo. No requiere editar el workflow.

### §3.5 Cancelación de waves pendientes

GHL no permite cancelar nativamente un workflow corriendo. Estrategia:

- Cada wave verifica `last_inbound_at > last_outbound_at_at_workflow_start` antes de enviar. Si el lead respondió, hace `exit` y no envía.
- El nuevo mensaje del Vendedor (cuando el lead responde) actualiza `last_outbound_at`, lo que dispara una nueva instancia del workflow (los waves viejos siguen en espera pero todos exitearán por la verificación).

---

## §4. WF-03 — Inactivity Sweep

**Propósito:** mover automáticamente leads a `Ventas Perdidas Real` tras 6 meses de inactividad.

### §4.1 Trigger

Schedule: diariamente a las 03:00 AM México (low-traffic window).

### §4.2 Lógica

```
Action: Search Opportunities WHERE
  pipeline = "Pipeline IA"
  AND stage = "En espera"
  AND last_inbound_at < (now() - 180 days)
  AND last_outbound_at < (now() - 180 days)

FOR EACH matched opportunity:
  Move Stage: Ventas Perdidas Real
  Apply Tag: lost_due_to_inactivity
  Log: HTTP a Supabase / o nota interna en el Opportunity

(NO se envía ningún mensaje. El lead ya está silencioso.)
```

---

## §5. WF-04 — Pago Detectado

**Propósito:** transicionar stages cuando se detecta comprobante de pago.

### §5.1 Trigger

HTTP webhook entrante desde n8n (Vision Classifier devuelve `payment_proof: true`).

Endpoint: `https://hook.gohighlevel.com/.../pago-detectado` (Inbound Webhook trigger configurado en GHL).

### §5.2 Payload esperado

```json
{
  "opportunity_id": "abc123",
  "contact_id": "xyz789",
  "image_url": "https://...",
  "current_stage": "Quoted",
  "detected_at": "2026-05-12T19:00:00-06:00"
}
```

### §5.3 Branching por stage actual

```
Section A — current_stage IN ["Quoted", "En espera"]:
  Update Custom Field: comprobante_anticipo_url = image_url
  Update Custom Field: comprobante_anticipo_at = detected_at
  Move Stage: Awaiting Payment
  IF business_hours = ON:
    Send Message: "Recibimos tu comprobante 🙌 Lo confirmamos en un momento."
  ELSE:
    Send Message: Custom Value vacaciones_pago_mensaje
      ("Gracias por tu pago, lo recibimos. Estamos fuera de horario por receso,
       lo confirmaremos a la brevedad.")
  HTTP Action: notify Telegram (chat_id Custom Value)
    Body: "🟢 Pago detectado | Lead: {phone} | Stage previa: {current_stage}"

Section B — current_stage = "In Production":
  Update Custom Field: comprobante_liquidacion_url = image_url
  Update Custom Field: comprobante_liquidacion_at = detected_at
  Move Stage: Awaiting Final Payment
  Send Message: "Recibimos el pago de liquidación 🙌 Procedemos a tu envío."
  HTTP Action: notify Telegram
    Body: "🟢 Pago de liquidación | Lead: {phone}"

Section C — fallback (otras stages):
  Send Message: "Recibimos tu mensaje. Lo revisamos."
  HTTP Action: notify Telegram (caso raro, marcar para revisión humana)
    Body: "⚠️ Imagen clasificada como pago en stage inesperada: {current_stage}"
  Apply Tag: needs_review
```

---

## §6. WF-05 — Business Hours / Vacaciones

**Propósito:** auto-reply cuando el sistema NO debería operar normalmente.

### §6.1 Trigger

Customer Replied + Filter:

```
(Custom Value vacaciones_active = true)
OR
(NOT business_hours(Custom Value business_hours_*))
```

### §6.2 Lógica

```
IF Custom Value vacaciones_active = true:
  Send Message: Custom Value vacaciones_mensaje
  Update Custom Field: last_outbound_at = now()
  Exit (NO se llama al Vendedor)

ELSE IF outside business hours:
  IF message.type = "image":
    (Caso: lead manda comprobante de pago fuera de horario)
    Forward to n8n /vision-only (sin conversación)
    IF Vision dice payment_proof:
      WF-04 dispara normalmente con el flag "fuera de horario"
      → el mensaje al lead será "Foto Vacaciones" (vacaciones_pago_mensaje)
    ELSE:
      Send Message: "Hola! Te respondemos en horario laboral L-V 9-17:30 México."
  ELSE:
    (Texto fuera de horario)
    No-op: el mensaje queda en inbox; el Vendedor lo procesará al volver el horario
    (o lo procesa igual el Vendedor — TBD, decisión a tomar en implementación)
```

> **Decisión pendiente para implementación:** ¿el Vendedor opera fuera de horario laboral? La lógica actual de Kommo procesa siempre pero solo envía mensajes especiales si detecta pago. Recomendación: **mantener Vendedor activo 24/7** — los clientes responden en cualquier momento, no perdamos esos prospectos. El "fuera de horario" solo afecta el mensaje específico de "recibimos tu pago" para gestionar expectativas de validación humana.

---

## §7. WF-06 — Stage Transitions

**Propósito:** mover stages cuando el Vendedor emite señales específicas, sin que n8n tenga que hacerlo directamente.

### §7.1 Trigger A: Custom Field actualizado

```
Trigger: Custom Field "evento_detectado" changed (not empty)
Filter: stage = "Greeted"
Action: Move Stage to "Event Identified"
```

```
Trigger: Custom Field "productos_mostrados" changed (not empty)
Filter: stage = "Event Identified"
Action: Move Stage to "Products Shown"
```

### §7.2 Trigger B: Outbound message contiene pattern

```
Trigger: Outbound Message Sent (WhatsApp)
Filter: Message body contains "⏳(7 DIAS DE PROMO)⏳"
        AND stage = "Products Shown"
Action: Move Stage to "Quoted"
        Update Custom Field: cotizacion_emitida_at = now()
```

### §7.3 Trigger C: Tag aplicado

```
Trigger: Tag added: "human_takeover"
Action: (no se mueve stage)
        HTTP Action: notify Telegram
        Update Custom Field: attention_motive = (extraído del mensaje del Vendedor que llamó la tool)
```

### §7.4 Trigger D: Won transition (manual)

```
Trigger: stage changed to "Won"
Action: Update Contact Custom Field: customer_status = "customer" (o "repeat_customer")
        Increment Contact Custom Field: total_purchases
        Add to Contact Custom Field: lifetime_value_mxn (sumar cotizacion_total_mxn)
        HTTP Action: log a Supabase leads_metrics (post-MVP)
```

---

## §8. Flujo end-to-end (caso típico)

Para validar que los 6 workflows juntos cubren el caso real:

### §8.1 Lead nuevo escribe `"Hola! Quiero info"`

1. **Meta WABA → GHL** recibe el mensaje. GHL crea Contact si no existe + Opportunity en `New Lead`.
2. **WF-06 Trigger A no aplica** (no hay Custom Field cambio aún).
3. **WF-01 dispara** (Customer Replied).
4. Filtros: pipeline IA ✅, stage `New Lead` ✅, no tag `human_takeover` ✅, no vacaciones ✅.
5. **WF-01 Section A** se ejecuta: envía saludo en 3 partes, mueve a `Greeted`.
6. **WF-02 dispara** (`last_outbound_at` cambió). Empieza Fase 1: wait 1h.

### §8.2 Lead responde `"XV años"` (a los 10 minutos)

1. WF-01 dispara. Stage = `Greeted` → Section B → POST a n8n /inbound con todo el contexto.
2. n8n: lee memoria Supabase (vacía en este lead), llama Vendedor con prompt + tools.
3. Vendedor entiende "XV" → llama tool `IDENTIFICAR_EVENTO(evento="XV")` → tool actualiza Custom Field via GHL API → responde texto `"Qué padre! 😊 🎉 SEMANA LOCA DE PROMOS..."` y solicita imagen al workflow.
4. n8n hace 2 cosas:
   - POST a GHL Conversations API: envía el texto del Vendedor.
   - POST a GHL Conversations API: envía la imagen principal del evento (URL del Custom Value `imagen_principal_xv_url`).
5. WF-06 Trigger A dispara: `evento_detectado` cambió → Move stage to `Event Identified`.
6. WF-02 vieja instancia: al checkear `last_inbound_at > last_outbound_at_at_start`, hace exit.
7. WF-02 nueva instancia arranca con timer 1h desde el nuevo `last_outbound_at`.

### §8.3 Lead pide productos `"Sandalias y cilindros"`

1. WF-01 → n8n → Vendedor entiende → llama tool `MOSTRAR_PRODUCTOS(evento="XV", productos=["sandalias","cilindros"])`.
2. Tool actualiza Custom Field `productos_mostrados = "sandalias,cilindros"` + devuelve los assets (URLs e info del Custom Object).
3. n8n envía las fichas vía Conversations API (una imagen + texto por producto, separadas por waits de ~1s).
4. WF-06 Trigger A: stage → `Products Shown`.
5. WF-02 timers reseteados.

### §8.4 Lead cotiza `"100 sandalias delgadas, CP 44730"`

1. WF-01 → n8n → Vendedor llama tool `COTIZADOR(producto="sandalia_delgada", cantidad=100, cp="44730")` → tool calcula envío + total + anticipo → devuelve cotización formateada con header `⏳(7 DIAS DE PROMO)⏳`.
2. n8n envía vía Conversations API.
3. WF-06 Trigger B: outbound message contiene `⏳(7 DIAS DE PROMO)⏳` → Move stage to `Quoted`.

### §8.5 Lead manda comprobante de pago

1. WF-01 dispara. stage = `Quoted`, message.type = `image`.
2. Section B aplica (no es stage de IA pausada): POST a n8n /inbound con `media_url`.
3. n8n: Vision Classifier corre → devuelve `{product: "NINGUNO", payment_proof: true}`.
4. n8n: hace HTTP POST a WF-04 endpoint con `opportunity_id`, `image_url`, `current_stage="Quoted"`.
5. WF-04 Section A: Move stage to `Awaiting Payment`, send "Recibimos tu comprobante", notify Telegram.
6. WF-02 timers exitearán automáticamente (stage no es elegible).

### §8.6 Humano valida pago (días después)

1. Equipo de pagos abre el Opportunity en GHL Kanban, ve el comprobante en `comprobante_anticipo_url`, lo valida, mueve stage manualmente a `Payment Confirmed (no design)`.
2. WF-06 no tiene trigger especial para esto (es manual).
3. Diseñadora ve los Opportunities en `Payment Confirmed`, toma uno, hace diseño, lo envía al lead vía inbox, mueve manualmente a `Design In Progress`.
4. Lead aprueba diseño, diseñadora mueve a `In Production`.

### §8.7 Lead manda 2do comprobante (liquidación)

1. WF-01 dispara. stage = `In Production`, message.type = `image`.
2. Section caso especial: stage en lista de IA-pausada → POST a n8n /vision-only.
3. n8n: Vision Classifier corre → `payment_proof: true`.
4. n8n → WF-04 endpoint con `current_stage="In Production"`.
5. WF-04 Section B: Move stage to `Awaiting Final Payment`, send "Recibimos liquidación, procedemos al envío", notify Telegram.
6. Humano valida, mueve a `Won`.

### §8.8 Lead no responde en ningún punto del ciclo

1. WF-02 envía wave P1_W1 (1h), P1_W2 (3h), P1_W3 (5h), P2_W1 (24h), P2_W2 (48h), P2_W3 (120h), P2_W4 (168h).
2. Después del wave 4 sin respuesta: Move stage a `En espera`.
3. Pasan 6 meses sin actividad → WF-03 (Inactivity Sweep) mueve a `Ventas Perdidas Real`.

---

## §9. Manejo de errores y edge cases

### §9.1 Falla de n8n (timeout en `/inbound`)

GHL Workflow HTTP action tiene retry policy configurable (default 3 retries con backoff exponencial).

Si después de 3 retries falla:
- Apply Tag: `ai_failed_needs_human`
- HTTP Action: notify Telegram con alerta
- (Mensaje del lead queda en inbox sin respuesta automática — humano revisa)

### §9.2 Vendedor devuelve mensaje vacío

n8n debe validar y, si vacío, enviar mensaje fallback genérico vía Conversations API: "Disculpa, estoy procesando tu mensaje. Un momento..."  + escalar a `human_takeover`.

### §9.3 Lead manda 10 mensajes en 5 segundos

Debouncing (Redis o n8n Wait) acumula. Solo el último dispara el Vendedor. WF-01 envía cada uno a n8n, n8n descarta los anteriores (verificación del `latest_message_id` antes de procesar).

### §9.4 Custom Object Producto cae / asset URL roto

n8n debe hacer fallback: enviar solo el texto del producto sin la imagen, y agregar al output del Vendedor un flag `asset_missing=true` → notificar Telegram.

### §9.5 GHL API rate limit (100 req / 10s, 200K / día por location)

Audit estimado: ~10K leads/sem × 20 mensajes promedio = ~200K msgs/sem inbound/outbound. Quedamos al borde del límite diario. **Mitigación:** consolidar updates de Custom Fields en menos calls (batch updates donde se pueda), usar webhook events en lugar de polling.

### §9.6 Lead cambia de número de teléfono

Si Oscar lo nota, puede actualizar el `phone` del Contact en GHL. El `session_id` de Supabase **no se actualiza automáticamente** (porque sigue siendo `<telefono_viejo>_2131`). Decisión: post-MVP, si esto pasa frecuentemente, agregar lógica de "merge sessions". MVP: aceptar que un cambio de teléfono crea un session_id nuevo y el agente pierde contexto.

---

## §10. Resumen de acciones GHL nativas usadas

| Acción GHL | Cuándo se usa | Dónde |
|---|---|---|
| Send Message (WhatsApp) | Saludo, respuestas del Vendedor (vía API), waves de re-engagement, mensaje de pago, mensaje de vacaciones | WF-01, WF-02, WF-04, WF-05 |
| Move Opportunity Stage | Transiciones automáticas | WF-01 (Greeted), WF-04 (pago), WF-06 (resto), WF-03 (inactivity) |
| Apply Tag / Remove Tag | Marcadores operativos | WF-01 (greeted), WF-02 (re_engagement_phase_N), WF-06 (lost_due_to_inactivity) |
| Update Contact Field | customer_status, total_purchases, lifetime_value | WF-06 (Won) |
| Update Opportunity Field | Custom Fields del Opportunity | Vendedor desde n8n vía API, WF-04 (pago), WF-06 |
| HTTP Action | Llamar a n8n, notificar Telegram, log a Supabase | WF-01, WF-02, WF-04, WF-06 |
| Wait | Cadencias de re-engagement, división de mensajes | WF-02, WF-01 Section A (saludo) |
| Search Opportunities | Inactivity sweep | WF-03 |
| Conditional (IF/ELSE) | Branching por stage / Custom Value / business hours | Todos |
