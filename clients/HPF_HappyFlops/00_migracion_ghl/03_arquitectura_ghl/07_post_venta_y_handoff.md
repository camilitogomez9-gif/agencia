# Post-venta y Handoff a Humano — Happy Flops

> **Etapa 3.** Diseño detallado de las stages post-cotización (pagos, diseño, producción, envío), atención personalizada, "En espera" y "Ventas Perdidas Real".

> 🔒 **NOMBRES Y KEYS REALES en M2 (2026-06-19):** este doc usa stages en inglés y Custom Value keys snake_case-inglés (`vacaciones_active`, `re_engagement_fase2_active_days`, etc.). La implementación real usa español + keys autogeneradas por GHL — ver `04_guia_migracion/02_pipeline_y_campos.md` §2.1 (stages) y §2.5 (mapeo CV keys). Al implementar, manda M2.

---

## §1. Mapa post-cotización

```
            Quoted
              │
              │ comprobante anticipo detectado (Vision)
              ▼
     Awaiting Payment ─────────────────────────┐
              │                                 │
              │ humano valida                   │ IA pausada conversacionalmente
              ▼                                 │ (Vision sí corre por si llega 2do comprobante)
   Payment Confirmed (no design)                │
              │                                 │
              │ diseñadora inicia diseño        │
              ▼                                 │
     Design In Progress                         │
              │                                 │
              │ lead aprueba diseño             │
              ▼                                 │
       In Production ◄─────────────────────────┤
              │                                 │
              │ comprobante liquidación detectado (Vision)
              ▼                                 │
     Awaiting Final Payment                     │
              │                                 │
              │ humano valida                   │
              ▼                                 │
              Won
```

Las stages "Payment Confirmed", "Design In Progress" e "In Production" **no son automáticas** — el equipo humano las mueve manualmente desde el Kanban de GHL.

---

## §2. Awaiting Payment (anticipo)

### §2.1 Cómo se llega

- Vendedor en stage `Quoted` recibe imagen del lead.
- Vision Classifier devuelve `payment_proof: true`.
- n8n → POST a webhook GHL `/pago-detectado`.
- WF-04 Section A se ejecuta: Move stage → `Awaiting Payment`.

### §2.2 Comportamiento del sistema

- **Vendedor conversacional:** ❌ PAUSADO. Si el lead escribe texto en esta stage, el mensaje queda en inbox sin respuesta automática.
- **Vision Classifier:** ✅ ACTIVO. Si el lead manda otra imagen (corrección del comprobante, comprobante claro, etc.), se procesa.
- **Mensaje automático al lead** (al detectar el pago):
  - Si business hours = ON: "Recibimos tu comprobante 🙌 Lo confirmamos en un momento."
  - Si business hours = OFF: "Gracias por tu pago, lo recibimos. Estamos fuera de horario; te confirmamos a la brevedad. ⏰"
- **Notificación al equipo:** Telegram al chat operativo de HPF con el link al Opportunity.
- **Custom Fields actualizados:** `comprobante_anticipo_url`, `comprobante_anticipo_at`.

### §2.3 Cuándo sale de esta stage

- **Humano (equipo de pagos):** valida transferencia → mueve manualmente a `Payment Confirmed (no design)` desde el Kanban.
- **Caso especial:** si el equipo detecta que el comprobante es falso/inválido, mueve manualmente a una stage previa (probablemente `Quoted` o aplica tag `human_takeover` para resolver con el lead).

### §2.4 ¿Y si el lead pregunta "ya confirmaron?" mientras está en Awaiting Payment?

El mensaje queda en el inbox de GHL. El equipo lo ve y responde manualmente. Si Oscar/Rebeca quieren un auto-reply para esto, agregar a WF-01:

```
IF stage = "Awaiting Payment" AND message NO es imagen:
  Send auto-reply: "Tu comprobante está en revisión. Te avisamos en cuanto se confirme."
  (NO llamar al Vendedor)
```

**Decisión MVP:** **NO** auto-reply. El inbox queda para humano. Post-MVP evaluar.

---

## §3. Payment Confirmed (no design)

### §3.1 Quién la maneja

100% humano. La diseñadora y/o equipo de Oscar.

### §3.2 Acción esperada

- La diseñadora ve los Opportunities en esta stage como "cola de trabajo".
- Toma uno, prepara el diseño, lo sube como adjunto en la conversación del lead vía inbox de GHL, mueve manualmente a `Design In Progress`.

### §3.3 Si el lead pregunta algo

Mismo comportamiento que `Awaiting Payment`: humano responde desde el inbox. IA pausada.

> **Prioridad alta operativa:** Oscar mencionó que esta es la stage donde el cliente se siente "más inseguro" porque ya pagó pero no ve diseño. Recomendación post-MVP: agregar auto-mensaje opcional al pasar a `Payment Confirmed`: "Tu pago está confirmado ✅ La diseñadora va a empezar con tu diseño en las próximas X horas."

---

## §4. Design In Progress

### §4.1 Quién la maneja

100% humano (diseñadora).

### §4.2 Acción esperada

- Diseñadora envió el diseño al lead vía inbox.
- Espera respuesta del lead (aprobado / cambios).
- Si lead aprueba: mover a `In Production`.
- Si pide cambios: la diseñadora itera; el Opportunity puede quedar acá varios días.

### §4.3 Custom Fields involucrados

- `diseño_enviado_at` (datetime, manual por diseñadora o por workflow al pasar stage).
- `diseño_aprobado_at` (datetime, manual al pasar a In Production).

---

## §5. In Production — IA reactivada (parcialmente)

### §5.1 Comportamiento clave

- **Vendedor conversacional:** ❌ PAUSADO. El lead no debería escribir mucho acá; si lo hace, queda en inbox para humano.
- **Vision Classifier:** ✅ ACTIVO — **esta es la diferencia clave**. Permite detectar automáticamente cuando el lead manda el comprobante de liquidación.

### §5.2 Cómo se detecta el 2do pago

```
1. Lead manda imagen estando en stage "In Production".
2. WF-01 → caso especial: stage en lista IA-pausada + msg.type=image → POST a n8n /vision-only.
3. n8n: Vision Classifier corre, devuelve {payment_proof: true}.
4. n8n: POST a WF-04 con current_stage="In Production".
5. WF-04 Section B: Move stage → "Awaiting Final Payment", send "Recibimos liquidación, procedemos al envío", notify Telegram.
```

### §5.3 ¿Y si el lead pregunta cosas conversacionales?

Queda en inbox para humano. No es un caso frecuente (típicamente el lead solo manda el pago).

Si Oscar quiere auto-reply tipo "Tu pedido está en producción, te avisamos cuando esté listo", agregar a WF-01 una rama similar a §2.4. **Decisión MVP:** NO auto-reply.

---

## §6. Awaiting Final Payment

### §6.1 Comportamiento

Idéntico a `Awaiting Payment` pero por el 2do comprobante:
- IA pausada.
- Vision activo (por si el lead manda comprobante mejorado).
- Mensaje automático: "Recibimos el pago de liquidación 🙌 Procedemos a tu envío."
- Notificación Telegram.

### §6.2 Salida

- Humano valida → mueve a `Won`.
- Si comprobante inválido: humano resuelve manualmente.

---

## §7. Won

### §7.1 Quién la mueve

Humano. Después de validar liquidación, agendar paquetería, generar guía.

### §7.2 Efectos automáticos al llegar a Won (WF-06 Trigger D)

- Update Contact: `customer_status = "customer"` (o `"repeat_customer"` si ya tenía `total_purchases > 0`).
- Increment Contact: `total_purchases += 1`.
- Add to Contact: `lifetime_value_mxn += cotizacion_total_mxn`.
- Log a `leads_metrics` (post-MVP).

### §7.3 ¿Qué pasa con la conversación post-Won?

- IA pausada para siempre (en esta Opportunity).
- Si el lead vuelve a escribir en el futuro, GHL crea (o no, según config) un nuevo Opportunity en `New Lead`. Si la convención es "1 contacto = 1 opportunity activa", el sistema espera que el equipo cree manualmente el nuevo Opp.

> **Decisión MVP:** auto-crear nuevo Opportunity al recibir mensaje del lead si su última Opp está en `Won` o `Ventas Perdidas Real`. Configurable post-MVP.

---

## §8. Atención Personalizada (tag `human_takeover`)

### §8.1 Cómo se activa

3 caminos:

| Camino | Trigger |
|---|---|
| **A) Vendedor lo decide** | Tool `ATENCION_PERSONALIZADA(motivo)` invocada |
| **B) Humano lo decide** | Equipo aplica el tag desde el inbox de GHL |
| **C) Sistema lo decide** | Tras 3 reintentos fallidos del Vendedor (`ai_failed_needs_human`) |

### §8.2 Efectos

- Tag `human_takeover` aplicado al Opportunity.
- Custom Field `attention_motive` (sólo si camino A) con la razón.
- Notificación Telegram al chat operativo.
- WF-01 filter: detiene cualquier procesamiento por el Vendedor.
- WF-02 filter: detiene reactivadores.

> El **stage del Opportunity NO se mueve** — el tag es paralelo. Si el lead estaba en `Quoted`, sigue en `Quoted` con el tag. Esto preserva el contexto del funnel.

### §8.3 Cuándo se desactiva

Humano remueve el tag manualmente desde el inbox cuando termina de gestionar el caso.

Al remover el tag:
- WF-01 vuelve a procesar mensajes del lead via Vendedor.
- WF-02 — los próximos outbound del Vendedor disparan nueva instancia de re-engagement.

### §8.4 Motivos típicos (mapeo desde reglas actuales)

| Trigger | Camino | Motivo (Custom Field) |
|---|---|---|
| Lead pide diseño no listado | A | `diseno_no_listado` |
| Lead pide algo fuera de catálogo | A | `fuera_de_catalogo` |
| Reclamo o post-venta | A | `reclamo` |
| Lead pide para fecha <15 días | A | `fecha_urgente` |
| Lead pregunta por termos especiales novios/quinceañeras | A | `termo_especial` |
| Imagen no clasificable | (A vía Vision Classifier) | `imagen_no_clasificable` |
| PDF recibido | (A vía sistema) | `pdf_recibido` |
| Vendedor falla técnicamente | C | `ai_failure` |
| Humano interviene proactivamente | B | (sin motivo automático; humano agrega manualmente) |

---

## §9. En espera

### §9.1 Cómo se llega

- Final de Fase 2 del WF-02 sin respuesta del lead.
- WF-02 wait 24h post-P2_W4 → si sigue sin responder → Move stage to `En espera`.

(Y eventualmente, leads en `Ventas Perdidas Real` que vuelven a escribir y el equipo decide reactivar, mueven manualmente a `En espera` o a stage activa.)

### §9.2 Comportamiento del sistema

- **Vendedor conversacional:** ✅ ACTIVO. Si el lead vuelve a escribir, lo procesa con contexto histórico completo (memoria Supabase tiene toda la conversación previa).
- **Vision Classifier:** ✅ ACTIVO.
- **Re-engagement (WF-02):** Inactivo. NO se envían más reactivadores. El lead solo recibe respuesta si escribe primero.
- **WF-03 Inactivity Sweep:** corre diariamente, mueve a `Ventas Perdidas Real` si `last_inbound_at < now - 6 meses`.

### §9.3 Si el lead vuelve a escribir

1. WF-01 dispara. Stage = `En espera` (elegible) → procesa normalmente.
2. n8n llama Vendedor con contexto completo + flag `customer_status` (prospect / customer).
3. Vendedor lee memoria, ve la conversación previa, retoma. Si la cotización todavía aplica (precios no cambiaron mucho, evento aún válido), continúa el cierre. Si pasó mucho tiempo, posiblemente re-cotiza.
4. El Vendedor mueve naturalmente el flujo: si menciona productos o cantidades, llama `MOSTRAR_PRODUCTOS` o `COTIZADOR` y el WF-06 lo lleva back a la stage que corresponda (no hay un movimiento manual obligatorio fuera de "En espera").

### §9.4 Casos a manejar en el prompt del Vendedor

Agregar al system prompt una sección específica:

```
[CONTEXTO LEAD RECURRENTE — solo si stage actual = "En espera"]

Este lead había avanzado en la conversación previamente pero dejó de responder.
Ahora volvió. Estrategia:

1. NO reiniciar el saludo desde cero.
2. Reconocé que vuelve: "Hola de nuevo! Qué bueno tenerte de vuelta 😊"
3. Revisá la memoria: ¿qué evento tenía? ¿qué productos consultó? ¿se cotizó?
4. Preguntá si la cotización anterior sigue aplicando o si cambiaron necesidades.
5. Si pasaron >60 días desde la última cotización: ofrecé re-cotizar (precios
   pueden haber cambiado).
6. NO repitas envío de imagen principal ni catálogo si ya los vio.
```

---

## §10. Ventas Perdidas Real

### §10.1 Cómo se llega

- **Vía automática:** WF-03 mueve `En espera` → `Ventas Perdidas Real` cuando `last_inbound_at < now - 180 days` Y `last_outbound_at < now - 180 days`.
- **Vía manual:** humano lo decide (ej. lead dijo "no compro más").

### §10.2 Comportamiento del sistema

- **Vendedor:** ❌ PAUSADO.
- **Vision Classifier:** ❌ PAUSADO.
- **WF-02:** No aplica (stage no elegible).
- **WF-03:** No relevante (ya está acá).

### §10.3 Si el lead vuelve a escribir después de meses

Como Vendedor y Vision están pausados, el mensaje queda en inbox para humano.

El equipo evalúa caso por caso:
- Si quiere reactivar: aplica un tag (ej. `reactivate_lead`) o mueve manualmente la stage de vuelta a `En espera` o a stage activa.
- Si no: deja el mensaje en inbox sin acción.

> **Mejora opcional post-MVP:** workflow que detecta mensajes entrantes en `Ventas Perdidas Real` y los marca con tag `lost_lead_resurfaced` + notifica Telegram para que el equipo lo vea rápido.

---

## §11. Vacaciones (cierre temporal de operaciones)

### §11.1 Configuración

Oscar setea Custom Value `vacaciones_active = true` desde la UI cuando HPF cierra por feriados.

### §11.2 Comportamiento

- **WF-01:** ningún mensaje entrante se procesa con el Vendedor.
- **WF-02:** ninguna instancia nueva arranca; las existentes hacen exit en el filter.
- **WF-05:** dispara para cada mensaje entrante con el mensaje de Custom Value `vacaciones_mensaje`.

### §11.3 Casos especiales

- **Imagen recibida durante vacaciones:** Vision Classifier corre normalmente (para no perder comprobantes de pago). Si es payment_proof → WF-04 envía el mensaje de "Foto Vacaciones" en lugar del de "recibimos tu pago".

### §11.4 Salida de vacaciones

Oscar setea `vacaciones_active = false` → todos los workflows vuelven a operar normalmente al siguiente mensaje recibido.

---

## §12. Resumen de tabla: stage × IA × responsable

| Stage | Vendedor | Vision | Responsable principal | Acción esperada del responsable |
|---|---|---|---|---|
| New Lead | ✅ auto | ✅ | Sistema | (auto: saludo) |
| Greeted | ✅ | ✅ | Vendedor | Identificar evento |
| Event Identified | ✅ | ✅ | Vendedor | Mostrar productos |
| Products Shown | ✅ | ✅ | Vendedor | Recolectar cantidades + cotizar |
| Quoted | ✅ | ✅ | Vendedor | Esperar comprobante |
| Awaiting Payment | ❌ | ✅ | Equipo pagos | Validar comprobante manualmente |
| Payment Confirmed | ❌ | ❌ | Diseñadora | Iniciar diseño |
| Design In Progress | ❌ | ❌ | Diseñadora | Iterar diseño con lead |
| In Production | ❌ | ✅ | Equipo producción | Producir físicamente |
| Awaiting Final Payment | ❌ | ✅ | Equipo pagos | Validar liquidación |
| Won | ❌ | ❌ | Equipo | Envío + cierre |
| En espera | ✅ (si vuelve) | ✅ | Vendedor | (esperar reactivación del lead) |
| Ventas Perdidas Real | ❌ | ❌ | Humano (opcional) | (caso por caso) |
| `human_takeover` (tag) | ❌ | ❌ | Humano | Resolver y quitar tag |

---

## §13. Checklist operativo para Oscar y el equipo

Acciones del equipo humano post-migración:

**Diariamente:**
- Revisar inbox GHL por mensajes en Opportunities con stage `Awaiting Payment` / `Awaiting Final Payment` (pagos a validar).
- Revisar Telegram por notificaciones de derivación a humano (`human_takeover`).
- Mover Opportunities validados a la siguiente stage manual.

**Semanalmente:**
- Revisar reportes (post-MVP): conversiones, leads en `En espera`, tasa de respuesta a waves.
- Validar que la configuración de `re_engagement_fase2_active_days` sigue siendo la deseada.

**Cuando aplica:**
- Activar/desactivar vacaciones (Custom Value).
- Editar precios en Custom Object Producto.
- Ajustar mensaje de vacaciones / promo si cambia.

---

## §14. Decisiones que quedan por confirmar en implementación

| Decisión | Quién la confirma | Propuesta default |
|---|---|---|
| ¿Auto-reply en stages de pago si lead pregunta? | Oscar | NO en MVP |
| ¿Auto-mensaje al pasar a `Payment Confirmed`? | Oscar | NO en MVP (post-MVP "Tu pago confirmado, diseñadora arranca") |
| ¿Notificar Telegram al pasar a `Design In Progress` (lead aprobó)? | Oscar | NO en MVP |
| ¿Crear nuevo Opportunity automáticamente cuando lead vuelve post-Won o post-Ventas Perdidas Real? | Oscar | SÍ en MVP (1 contacto puede tener varias Opps históricas + 1 activa) |
| ¿Mostrar al lead un mensaje de tipo "te asignamos a un especialista" al activar `human_takeover`? | Oscar | SÍ (Vendedor envía un mensaje genérico al invocar la tool) |
