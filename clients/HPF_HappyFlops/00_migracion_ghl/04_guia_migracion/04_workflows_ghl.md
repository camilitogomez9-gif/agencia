# M4 — Workflows GHL (WF-01 a WF-06)

> **Referencia:** `03_arquitectura_ghl/03_workflows_ghl.md`  
> **Tiempo estimado:** 6-8 horas  
> **Prerequisito:** M2 completo (pipeline y custom fields existen)

---

## Visión general de los 6 workflows

> Los nombres de workflow van en español (visibles en Automation). Se conserva el prefijo `WF-0X` como ID operativo estable.

| ID | Nombre (UI, español) | Trigger | Propósito |
|----|----------------------|---------|-----------|
| WF-01 | Enrutador de Entrada | Customer replied / Inbound message | Rutear mensaje al handler correcto (saludo fijo vs n8n) |
| WF-02 | Reenganche Dual | Interno (llamado por WF-01 post-outbound) | Orquestar olas Fase 1 + Fase 2 |
| WF-03 | Barrido de Inactividad | Schedule (diario) | Mover leads a "Ventas Perdidas" tras 6 meses en "En Espera" |
| WF-04 | Pago Detectado | Inbound Webhook (n8n → GHL) | Transicionar lead cuando Vision Classifier detecta comprobante |
| WF-05 | Guardia de Horario | Customer replied | Responder fuera de horario y pausar procesamiento |
| WF-06 | Monitor de Transición de Etapas | Custom Field changed / Message sent | Mover leads automáticamente según señales del Vendedor |

---

## 4.1 WF-01 — Enrutador de Entrada

**Automation → Workflows → Create Workflow → Start from scratch**  
**Name:** `WF-01 Enrutador de Entrada`

### Trigger
- **Trigger:** Customer Replied (o "Inbound Message")
- **Filter:** Contact Tag NOT contains `lead_prueba` (para separar tests en paralelo)

### Paso 1: Verificar horario (Branch)

**Branch condition:** Custom Value `vacaciones_activas` = `true`  
→ Si true: Go to WF-05 (fuera de horario/vacaciones). Fin.  
→ Si false: continuar.

**Branch condition 2:** Hora actual fuera de rango `horario_inicio_hora_local` / `horario_fin_hora_local`  
→ Si fuera: Go to WF-05. Fin.  
→ Si dentro: continuar.

> GHL no tiene nodo de "hora actual" nativo. Workaround: usar un webhook a n8n que devuelva `in_hours: true/false`, o usar el nodo "Date/Time" de GHL con comparaciones.  
> **Alternativa simple MVP:** hardcodear las horas en una condición If/Else del workflow directamente.

### Paso 2: Verificar tag `atencion_humana`

**If/Else:** Contact Tag contains `atencion_humana`  
→ Si true: **Stop** (no procesar, el humano tiene control). Fin.  
→ Si false: continuar.

### Paso 3: Verificar que el opportunity está en un stage activo para IA

**If/Else:** Opportunity Stage IN [`Lead Nuevo`, `Saludo Enviado`, `Evento Identificado`, `Productos Mostrados`, `Cotizado`]  
→ Si false (stage post-cotización o En Espera): enviar a n8n igual (la IA sigue activa pero con instrucciones diferentes). Continuar.  
→ Si true: continuar normal.

### Paso 4: Branch — ¿Es un lead nuevo?

**If/Else:** Opportunity Stage = `Lead Nuevo` AND Contact Created At < 5 minutos  

**Rama A — Lead nuevo (saludo fijo):**
1. **Wait:** 2 segundos
2. **Send Message:** `¡Hola! 👋 Soy Rebeca, asistente de Happy Flops. ¿En qué puedo ayudarte hoy? 😊`
3. **Wait:** 2 segundos  
4. **Send Message:** [texto de promo — usar Custom Value `texto_promo_activa`]  
   📋 `{{custom_values.texto_promo_activa}}`
5. **Update Opportunity Stage:** `Saludo Enviado`
6. **Update Custom Field** `last_outbound_at`: timestamp ISO 8601 (ver nota ⏱️)
7. **Trigger WF-02** (via Internal trigger o webhook interno)

> ⏱️ **`last_outbound_at` es Single line text ISO 8601** (GHL no soporta Date/Time). En este path el saludo lo manda GHL, así que GHL escribe el timestamp: usar un token de fecha que produzca ISO (formato `yyyy-MM-dd'T'HH:mm:ss`). Si GHL no logra ISO limpio, no es bloqueante — `last_outbound_at` es un marcador (las olas de WF-02 usan nodos **Wait** relativos, no este campo). El campo crítico para el check "¿respondió?" es **`last_inbound_at`, que SIEMPRE lo escribe n8n** en ISO (nunca GHL).

**Rama B — Lead existente (rutear a n8n):**
1. **Send Webhook:** POST a `{{env.N8N_BASE_URL}}/webhook/hpf-inbound`  
   Body: ver M5 §5.1 para el schema completo.
2. **Wait:** respuesta de n8n (usar webhook síncrono o action con timeout 30s)
3. Si n8n devuelve `action: send_message`: **Send Message** con el texto de respuesta
4. Si n8n devuelve `action: human_takeover`: **Apply Tag** `atencion_humana` + notificar Oscar
5. **Update Custom Field** `last_outbound_at`: `{{now}}` (si hubo outbound)
6. **Trigger WF-02** (si hubo outbound y lead sigue en stage activo)

> ⚠️ GHL no tiene nodo nativo de "esperar respuesta de webhook". Opciones:  
> **Opción 1 (recomendada):** n8n llama de vuelta a GHL via API para enviar el mensaje directamente (`POST /conversations/messages`). WF-01 solo dispara n8n y no espera respuesta.  
> **Opción 2:** Usar el nodo GHL "Custom Webhook" como trigger separado que n8n activa.  
> En M5 se define que n8n envía el mensaje directamente via GHL API. Por eso WF-01 solo necesita disparar n8n, no esperar.

### Versión simplificada del WF-01 (recomendada para MVP):

```
Trigger: Customer Replied
  ↓
If vacaciones OR fuera de horario → WF-05 → STOP
  ↓
If atencion_humana tag → STOP
  ↓
If stage = Lead Nuevo (nuevo) →
  Send saludo fijo (2 msgs) → Update stage a Saludo Enviado → Update last_outbound_at → Trigger WF-02
  ↓
Else →
  Send Webhook a n8n (fire and forget)
  (n8n maneja el resto via GHL API directa)
```

---

## 4.2 WF-02 — Reenganche Dual

**Name:** `WF-02 Reenganche Dual`

### Trigger
- **Internal Trigger** (llamado por WF-01 al final de cada outbound exitoso)
- O alternativamente: Trigger via Webhook interno desde n8n después de cada Send Message

### Variables de entrada necesarias:
- `opportunity_id`
- `contact_id`  
- `last_outbound_at` (ya actualizado en CF antes de triggerear)

### Estructura del workflow:

```
START
  ↓
Wait 0s (inmediato al inicio — registrar workflow_started_at)
  ↓
──── FASE 1 ────
If reenganche_fase_1_activa = false → Skip a Fase 2 (Wait 24h)
  ↓
[WAVE P1_W1 — 1h]
Wait 1 hour
Check: last_inbound_at < workflow_started_at? (lead no respondió)
Check: stage IN stages_activos_ia?
Check: atencion_humana tag?
Check: re_engagement_paused = true?
Check: vacaciones_activas = true?
If ANY check fails → EXIT
  ↓
Check: "1h" IN reenganche_fase_1_olas (Custom Value)?
If yes → Send Webhook n8n /generate-reengagement-message (wave: P1_W1)
         Esperar respuesta → Send Message con texto generado
         Update CF last_re_engagement_wave = "P1_W1"
         Update CF last_outbound_at = now
         Insert followup_log en Supabase (via n8n webhook)
  ↓
[WAVE P1_W2 — 3h]
Wait 2 hours (3h total desde inicio)
[mismas verificaciones]
If "3h" IN reenganche_fase_1_olas → Send P1_W2
  ↓
[WAVE P1_W3 — 5h]
Wait 2 hours (5h total desde inicio)
[mismas verificaciones]
If "5h" IN reenganche_fase_1_olas → Send P1_W3
  ↓
──── FASE 2 ────
If reenganche_fase_2_activa = false → Move stage "En Espera" → EXIT
  ↓
Apply Tag: reenganche_fase_2
  ↓
[WAVE P2_W1 — 24h]
Wait 19h (24h desde inicio, o 19h desde fin de Fase 1)
[mismas verificaciones]
If "R1" IN reenganche_fase_2_das_activos → Send P2_W1
  ↓
[WAVE P2_W2 — 48h]
Wait 24h
[mismas verificaciones]
If "R2" IN reenganche_fase_2_das_activos → Send P2_W2
  ↓
[WAVE P2_W3 — 120h]
Wait 72h (5 días total)
[mismas verificaciones]
If "R3" IN reenganche_fase_2_das_activos → Send P2_W3
  ↓
[WAVE P2_W4 — 168h]
Wait 48h (7 días total)
[mismas verificaciones]
If "R4" IN reenganche_fase_2_das_activos → Send P2_W4
  ↓
Wait 24h (post último wave)
[verificación final]
If last_inbound_at < workflow_started_at:
  Move stage: "En Espera"
  Apply Tag: reenganche_completado
  Remove Tag: reenganche_fase_1, reenganche_fase_2
  Update CF: re_engagement_completed_at = now
  Update CF: last_re_engagement_wave = "completed"
EXIT
```

> **Nota sobre los "checks" en cada wave:** en GHL, cada bloque de verificación es un nodo **If/Else** que al detectar condición adversa hace **Exit Workflow** (Exit from this workflow).

> La verificación de `last_inbound_at < workflow_started_at` requiere comparar dos fechas. En GHL se puede hacer con el nodo **If/Else → Date comparison** o via webhook a n8n que devuelva el resultado.

---

## 4.3 WF-03 — Barrido de Inactividad (diario)

**Name:** `WF-03 Barrido de Inactividad`  
**Trigger:** Schedule — todos los días a las 08:00 CST

```
START (Schedule)
  ↓
For each Opportunity WHERE:
  Stage = "En Espera"
  AND re_engagement_completed_at < (now - 180 days)
  AND (last_inbound_at IS NULL OR last_inbound_at < (now - 180 days))
  ↓
Move Stage: "Ventas Perdidas"
Remove Tag: reenganche_completado
Update CF: last_re_engagement_wave = "lost_180d"
(NO enviar mensaje al lead)
```

> En GHL, el trigger Schedule no tiene nativo un "for each filtered opportunity". Opciones:  
> **Opción A:** Usar webhook a n8n que ejecute la query en Supabase y llame a GHL API para mover stages.  
> **Opción B:** Usar el nodo GHL "Find Contact/Opportunity" si el plan lo soporta.  
> **Recomendación MVP:** Opción A — más control, ya tenemos n8n.

**Alternativa (workflow n8n puro):**  
Crear un Schedule node en n8n que corra diariamente a las 8:00 CST, consulte Supabase o GHL API para encontrar opportunities con las condiciones, y llame a GHL API para mover stages. Más simple que configurar GHL Schedule.

---

## 4.4 WF-04 — Pago Detectado

**Name:** `WF-04 Pago Detectado`  
**Trigger:** Inbound Webhook (GHL expone un endpoint que n8n llama)

```
POST /webhook/pago-detectado
{
  "opportunity_id": "...",
  "contact_id": "...",
  "current_stage": "Cotizado",
  "payment_amount_mxn": 500,
  "nota": "Comprobante detectado por Vision Classifier"
}
```

**Workflow:**

```
START (Inbound Webhook)
  ↓
Verificar Bearer token en headers (seguridad)
  ↓
Update CF: payment_proof_detectado = true
  ↓
If current_stage = "Cotizado":
  Move Stage → "Esperando Pago"
  (Vendedor ya cotizó, ahora el lead envió comprobante → confirmar)
  Send Message: "¡Recibí tu comprobante! 🎉 Lo verificamos en breve y te confirmamos."
  ↓
If current_stage = "Esperando Pago":
  Move Stage → "Pago Confirmado"
  Send Message: "¡Pago confirmado! ✅ Ahora pasamos al diseño de tus recuerditos 🎨"
  Notify Oscar via Telegram (webhook n8n)
```

> El texto exacto de los mensajes va a ser definido por Oscar antes de go-live. Estos son placeholders que funcionan.

---

## 4.5 WF-05 — Guardia de Horario

**Name:** `WF-05 Guardia de Horario`  
**Trigger:** (llamado por WF-01 cuando detecta fuera de horario)

```
START
  ↓
If vacaciones_activas = true:
  Send Message: [mensaje de vacaciones — Custom Value o hardcodeado]
  EXIT
  ↓
If fuera de horario laboral:
  Send Message: {{custom_values.mensaje_fuera_de_horario}}
  EXIT
```

> Este workflow es simple. Lo importante es no llamarlo dos veces (WF-01 solo lo llama si la condición aplica).

---

## 4.6 WF-06 — Monitor de Transición de Etapas

**Name:** `WF-06 Monitor de Transición de Etapas`  
**Trigger:** Outbound Message Sent (o Custom Field Changed para `last_outbound_at`)

Este workflow detecta señales en los mensajes del Vendedor (devueltos por n8n) para avanzar stages automáticamente.

```
START (Outbound message sent)
  ↓
If message contains "⏳(7 DIAS DE PROMO)⏳" AND stage = "Saludo Enviado":
  Move Stage → "Evento Identificado" (el Vendedor envió la imagen de promo, implica evento detectado)
  ↓
If CF cotizacion_emitida changed to true AND stage IN ["Evento Identificado", "Productos Mostrados"]:
  Move Stage → "Cotizado"
  Update CF: cotizacion_generada_at = now
  ↓
If CF had_information = true AND stage = "Saludo Enviado":
  Move Stage → "Evento Identificado"
  ↓
If CF had_image = true AND stage IN ["Saludo Enviado", "Evento Identificado"]:
  (no cambiar stage — la imagen es parte del flujo normal)
```

> **Nota:** WF-06 es el más complejo de mantener porque depende de señales indirectas. En MVP podés simplificarlo dejando que n8n llame directamente a GHL API para mover stages cuando corresponde, y usar WF-06 solo como fallback. Ver M5 para cómo n8n actualiza stages via API.

---

## 4.7 Orden de creación de workflows

```
1. WF-05 (más simple, no depende de otros)
2. WF-04 (independiente)
3. WF-03 (independiente)
4. WF-02 (depende de Custom Values de M2)
5. WF-06 (depende de Custom Fields)
6. WF-01 (depende de todos los anteriores)
```

---

## ✅ Checklist M4

- [ ] WF-05 creado y probado (enviar mensaje fuera de horario → respuesta automática)
- [ ] WF-04 creado con webhook URL anotada para M5
- [ ] WF-03 creado (schedule diario o equivalente en n8n)
- [ ] WF-02 creado con toda la cadena de waves
- [ ] WF-06 creado (aunque sea versión simplificada)
- [ ] WF-01 creado — trigger + rama saludo fijo + rama n8n
- [ ] URLs de webhooks de entrada de WF-04 anotadas para M5

```
WF-04 Webhook URL = ________________________
```

**Siguiente:** M5 → n8n: endpoints y lógica IA
