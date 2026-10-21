# Sistema de Re-engagement — Happy Flops (post-migración)

> **Etapa 3.** Especificación detallada del sistema dual de re-engagement: Fase 1 (waves cortas) + Fase 2 (campaña 7 días) + flexibilidad configurable + personalización con contexto.

> 🔒 **CUSTOM VALUE KEYS REALES en M2 (2026-06-19):** este doc usa keys de Custom Values en estilo snake_case-inglés (`re_engagement_fase1_active`, `re_engagement_fase2_active_days`, `vacaciones_active`...). GHL las autogenera en español desde el Name y no las deja editar — ver mapeo `vieja → real` en `04_guia_migracion/02_pipeline_y_campos.md` §2.5. Al implementar, usar las reales.

---

## §1. Filosofía del sistema

Dos objetivos distintos, dos cadencias distintas, un solo workflow:

| Fase | Objetivo | Cuándo | Cadencia | Tipo de mensaje |
|---|---|---|---|---|
| **Fase 1** | "Obligar" a responder con alta frecuencia tras inactividad inmediata | Después de cada mensaje del Vendedor que no recibe respuesta | 1h → 3h → 5h | Personalizado con LLM, contextualizado |
| **Fase 2** | Aprovechar la "semana de promo" para empujar el cierre | Después de cerrar Fase 1 sin respuesta | 24h → 48h → 120h → 168h | Personalizado con LLM, urgencia creciente |

Total ventana: ~8 días.

Al cerrar Fase 2 sin respuesta → stage `En espera` (IA sigue activa pero deja de empujar). Si el lead vuelve a escribir en algún momento dentro de los 6 meses siguientes, el Vendedor lo retoma con contexto histórico completo. Pasados 6 meses sin actividad → `Ventas Perdidas Real`.

---

## §2. Eventos que disparan / cancelan re-engagement

### §2.1 Dispara

| Evento | Acción | Reset de timer? |
|---|---|---|
| Vendedor envía mensaje al lead (cualquier stage activa) | Trigger WF-02 (nueva instancia) | Sí — `last_outbound_at` se actualiza, los waves se cuentan desde aquí |
| Lead avanza al siguiente stage del pipeline | (no dispara directamente, pero el siguiente outbound del Vendedor sí) | Implícito |

### §2.2 Cancela

| Evento | Cómo se cancela |
|---|---|
| Lead responde con un mensaje | `last_inbound_at` se actualiza. Cada wave verifica `last_inbound_at < workflow_started_at` antes de enviar. Si el lead respondió, hace `exit` y no envía. |
| Lead avanza a stage donde IA está pausada (Awaiting Payment, In Production, etc.) | Filter inicial del workflow: `stage IN [stages elegibles]`. Si cambió, exit. |
| Tag `human_takeover` aplicado | Filter inicial. Exit. |
| Oscar setea Custom Field `re_engagement_paused = true` manualmente | Filter inicial. Exit. |
| Custom Value global `vacaciones_active = true` | Filter inicial. Exit (durante vacaciones no enviamos reactivadores). |

---

## §3. Fase 1 — Waves cortas

### §3.1 Cadencias

| Wave | Delay desde `last_outbound_at` | Wave ID |
|---|---|---|
| 1ª | **1h** | `P1_W1` |
| 2ª | **3h** (2h después de la 1ª) | `P1_W2` |
| 3ª | **5h** (2h después de la 2ª) | `P1_W3` |

### §3.2 Activación condicional

```
IF Custom Value re_engagement_fase1_active = false:
  Skip TODA Fase 1 → arranca directo Fase 2 con timer 24h desde last_outbound_at.

ELSE:
  Verificar cada wave individualmente contra Custom Value re_engagement_fase1_waves:
  - Default: "1h,3h,5h" → todas activas.
  - Si Oscar edita a "1h,5h": solo dispara W1 y W3, salta W2.
```

### §3.3 Contenido de los mensajes (personalización con LLM)

A diferencia del sistema actual (mensajes hardcoded en salesbots Kommo), los reactivadores **se generan con LLM** con contexto del Opportunity. Esto fue requisito explícito de Oscar en la reunión.

**Endpoint n8n:** `POST /generate-reengagement-message`

**Payload:**
```json
{
  "opportunity_id": "...",
  "wave": "P1_W1",
  "stage": "Products Shown",
  "context": {
    "evento_detectado": "XV",
    "productos_mostrados": "sandalias,cilindros",
    "cantidad_sandalias": 100,
    "cantidad_cilindros": 50,
    "cotizacion_emitida": false,
    "last_outbound_summary": "Te envié las fichas de sandalias y cilindros para XV...",
    "tiempo_desde_outbound": "1 hora"
  }
}
```

**System prompt del generador de re-engagement:**

```
Sos Rebeca, asistente virtual de Happy Flops. Estás generando un mensaje breve de
re-engagement para un lead que dejó de responder. El sistema te da contexto;
tu trabajo es producir UN mensaje conciso y natural.

REGLAS:

1. Brevedad: máximo 2 oraciones + 1 emoji.

2. Referenciar el contexto específico SIEMPRE. NO mandes mensajes genéricos
   tipo "¿sigues por ahí?". Mencioná el evento o los productos concretos
   que el lead consultó.

3. Tonalidad por wave:
   - P1_W1 (1h): suave, casual, como "te recordé". Ej:
     "Hola! Te leí pero capaz quedaste con dudas con las sandalias para tu XV.
     Si querés te ayudo a definir cantidades 😊"
   - P1_W2 (3h): un poco más directo, recordá la promo si aplica. Ej:
     "Hola de nuevo! ⏳ Aprovechá la promo de 7 días para tus 100 sandalias y
     50 cilindros, vale super la pena para tu evento."
   - P1_W3 (5h): ligera urgencia + invitación clara a continuar. Ej:
     "Hola! Si me confirmás CP y tipo de suela termino tu cotización
     y arrancamos con tus recuerditos. ✨"

   - P2_W1 (24h): retomar amablemente. Ej:
     "Hola! ¿Te quedó alguna duda con la cotización? Estoy aquí para
     ayudarte a definir todo."
   - P2_W2 (48h): mostrar valor. Ej:
     "Acordate que la promo de 7 días incluye envío gratis para Guadalajara.
     ¿Avanzamos con tu pedido?"
   - P2_W3 (120h, día 5): urgencia. Ej:
     "Quedan pocos días para aprovechar la promo. ¿Cerramos tu pedido?"
   - P2_W4 (168h, día 7, ÚLTIMO DÍA): urgencia máxima. Ej:
     "📣 Hoy es el ÚLTIMO DÍA de la promo. Si querés tus recuerditos
     personalizados a precio especial, este es el momento 🎊."

4. NUNCA repetir un mensaje previo. La memoria del lead tiene los reactivadores
   anteriores; reformulá variando el ángulo.

5. NO ofrecer descuentos extra ni modificar precios.

6. Si el lead NO tiene cotización emitida aún: enfocate en avanzar la conversación
   (preguntá CP, cantidad, etc.).
   Si SÍ tiene cotización emitida: enfocate en el cierre del pago.

7. Formato: texto plano, emojis moderados, sin asteriscos de markdown.

8. Output: SOLO el texto del mensaje. Sin explicaciones, sin metadata, sin JSON.
```

**Modelo:** `gpt-4.1-mini` (suficiente para esta tarea, ahorro de tokens vs gpt-4.1).
**Temperature:** `0.7` (queremos variabilidad para no repetir).
**Max tokens:** `150`.

---

## §4. Fase 2 — Campaña 7 días

### §4.1 Cadencias

| Wave | Delay total desde `last_outbound_at` inicial | Wave ID |
|---|---|---|
| Día 1 | **24h** | `P2_W1` |
| Día 2 | **48h** | `P2_W2` |
| Día 5 | **120h** | `P2_W3` |
| Día 7 (ÚLTIMO DÍA) | **168h** | `P2_W4` |

Gaps de 3 días (W2 → W3) y 2 días (W3 → W4), intencionales según Oscar (no saturar).

### §4.2 Flexibilidad por presupuesto (requisito de Oscar)

Custom Value `re_engagement_fase2_active_days` controla qué waves de Fase 2 están activas. Default: `"R1,R2,R3,R4"` (todas).

**Casos típicos:**

| Configuración | Comportamiento | Cuándo usar |
|---|---|---|
| `R1,R2,R3,R4` | Todas activas — 4 waves en 7 días | Promo full presupuesto |
| `R1,R2,R4` | 3 waves: día 1, día 2, día 7 (skip día 5) | Bajar costo, mantener urgencia día 7 |
| `R1,R4` | 2 waves: día 1 y día 7 (recordatorio inicial + último día) | Presupuesto mínimo, mantener punta y cierre |
| `R4` | Solo el último día | Caso extremo, solo aprovechar ÚLTIMO DÍA |

Oscar/Rebeca editan este Custom Value desde la UI de GHL → toma efecto en la siguiente instancia del workflow (no en las que ya están corriendo).

> **Nota técnica:** el workflow GHL verifica el Custom Value en cada wave (no al inicio), así que un cambio mid-instance también aplica. Lo único que no se puede cambiar son los delays (1h/3h/5h/24h/48h/120h/168h hardcodeados en los waits del workflow).

### §4.3 Mensajes — mismo generador LLM que Fase 1

Mismo endpoint `/generate-reengagement-message`, mismo prompt, distinto contexto:

- `wave: "P2_W1"` (vs `P1_*`).
- El generador adapta tono según la lista de tonalidades por wave del prompt.

### §4.4 Activación condicional global

```
IF Custom Value re_engagement_fase2_active = false:
  Termina el workflow al cerrar Fase 1 sin respuesta.
  Move stage to "En espera" inmediatamente (skip Fase 2 entera).
```

---

## §5. Transición a "En espera"

Al cumplir ~192h (7 días + 24h post-último wave) sin respuesta:

```
Wait 24h post-P2_W4
IF last_inbound_at < workflow_started_at  (sigue sin responder):
  Move Stage: En espera
  Apply Tag: re_engagement_completed
  Remove Tag: re_engagement_phase_2
  Update Custom Field: last_re_engagement_wave = "completed"
  Update Custom Field: re_engagement_completed_at = now()
  (NO se envía ningún mensaje al lead)
```

> **Implicación:** el sistema NO le dice al lead "te paso a en espera". Es transparente. El lead simplemente deja de recibir reactivadores. Si vuelve a escribir, la IA lo retoma con su contexto histórico.

---

## §6. Casos especiales

### §6.1 Lead responde en medio de la campaña

```
Caso: wave P2_W2 (48h) está en cola; el lead responde a las 30h.

Flujo:
1. Mensaje entrante → WF-01 → n8n → Vendedor responde.
2. Send Message del Vendedor → `last_outbound_at` actualizado → dispara nueva instancia WF-02.
3. Instancia vieja: wave P2_W2 sigue en wait. Al despertar, verifica
   `last_inbound_at > workflow_started_at` → true → exit.
4. Instancia nueva: arranca con `Fase 1 W1 (1h)` desde el nuevo outbound.
```

### §6.2 Lead avanza de stage durante la campaña

```
Caso: lead en stage "Products Shown" recibió P2_W1, responde algo, Vendedor cotiza,
mueve a "Quoted". Lead vuelve a desaparecer.

Flujo:
1. Nuevo outbound (cotización) → nueva instancia WF-02 desde stage "Quoted".
2. Las waves se cuentan desde el outbound de cotización, no desde el de productos.
3. El mensaje del wave se adapta automáticamente al contexto nuevo
   (el LLM ve `cotizacion_emitida=true`, `cantidad_sandalias=100`, etc.).
```

### §6.3 Lead pide ATENCION_PERSONALIZADA durante la campaña

```
Caso: Vendedor invoca tool ATENCION_PERSONALIZADA → tag `human_takeover` aplicado.

Flujo:
1. Filter inicial WF-02 (verificado en cada wave): tag `human_takeover` aplicado → exit.
2. Waves pendientes se descartan.
3. Si el humano resuelve y quita el tag, el lead vuelve a stage activo;
   el siguiente mensaje del Vendedor disparará nueva instancia.
```

### §6.4 Oscar pausa manualmente al lead

```
Caso: Oscar ve en el inbox un lead VIP que no quiere bombardear y setea
Custom Field re_engagement_paused = true.

Flujo:
1. Filter inicial WF-02: re_engagement_paused = true → exit.
2. Waves pendientes se descartan.
3. Oscar puede quitar el pause cuando quiera; la próxima instancia respetará.
```

### §6.5 Vacaciones globales

```
Caso: HPF está de vacaciones (Custom Value vacaciones_active = true).

Flujo:
1. Filter inicial WF-02 verifica vacaciones_active.
2. Si true → exit en TODOS los waves (no enviamos reactivadores durante vacaciones).
3. Cuando Oscar quita vacaciones_active, los waves pendientes ya se descartaron,
   pero el próximo outbound del Vendedor dispara nueva instancia normal.
```

---

## §7. Tracking en Supabase

Cada wave enviada se loguea en `followups_log` (definido en §6.2 de `02_data_model.md`):

```sql
INSERT INTO followups_log (
  opportunity_id, contact_id, phone, wave, sent_at, message_content
) VALUES (
  'opp_abc', 'ct_xyz', '52333...', 'P2_W3', now(),
  'Quedan pocos días para aprovechar la promo...'
);
```

Cuando el lead responde después de un wave, opcionalmente actualizar:

```sql
UPDATE followups_log
SET responded = true, responded_at = now()
WHERE opportunity_id = 'opp_abc'
  AND wave = 'P2_W3'
  AND responded = false;
```

> Esto permite reportes post-MVP: tasa de respuesta por wave, wave que mejor convierte, comparación de configuraciones de `active_days`.

---

## §8. Métricas post-MVP

(No se implementan en cutover, pero quedan diseñadas:)

| Métrica | Cómo se calcula | Para qué |
|---|---|---|
| Tasa de respuesta por wave | `COUNT(WHERE responded) / COUNT(*)` agrupado por `wave` | Identificar qué waves convierten más |
| Tiempo a la primera respuesta tras wave | `responded_at - sent_at` median por `wave` | Optimizar cadencias |
| Conversión post-wave | % de leads que pasaron a `Won` después de recibir wave | ROI por wave |
| Comparación de `active_days` configurations | Agrupar por mes según configuración usada | A/B testing de cadencias |
| Costo de plantillas Meta por wave | Multiplicar count × tarifa Meta del momento | Justificar inversión |

Dashboard sugerido (post-MVP): Looker Studio conectado a Supabase, o tabla en Notion alimentada por n8n diario.

---

## §9. Resumen ejecutivo

- **Sistema dual** con 2 fases configurables (Fase 1: 1h/3h/5h; Fase 2: 24h/48h/120h/168h).
- **Cadencias fijas** (delays hardcoded en workflow) + **selección de waves configurable** (Custom Values editables por Oscar).
- **Personalización del texto** con LLM dedicado (`gpt-4.1-mini` con prompt específico) usando contexto del Opportunity.
- **Cancelación automática** vía verificación de `last_inbound_at` en cada wave (no requiere kill explícito).
- **Tracking completo** en Supabase para análisis posterior.
- **Transición a "En espera"** sin mensaje al lead (transparente, IA sigue activa si vuelve).
- **6 meses post-En espera sin actividad** → WF-03 mueve a `Ventas Perdidas Real`.
