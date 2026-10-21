# Integraciones — Happy Flops (post-migración)

> **Etapa 3.** Cableado entre GHL, n8n, Supabase, OpenAI, WhatsApp (Meta WABA) y Telegram. Define endpoints, payloads, autenticación y manejo de errores.

---

## §1. Diagrama de integración

```
       ┌────────────┐                                 ┌────────────────┐
       │   Lead     │ ── WhatsApp message ─────────► │  Meta WABA     │
       │ (cellphone)│                                 │  Cloud API     │
       └────────────┘                                 └───────┬────────┘
                                                              │
                                                              │ webhook (mensajes)
                                                              ▼
                                                     ┌────────────────────┐
                                                     │   GoHighLevel      │
                                                     │  (sub-account HPF) │
                                                     │  • WA channel      │
                                                     │  • Workflows 01-06 │
                                                     │  • Opportunities   │
                                                     │  • Inbox           │
                                                     └────┬───────────────┘
                                                          │
                       ┌──────────────────────────────────┤ HTTP POST (webhook outbound)
                       │                                  │ a /inbound o /vision-only
                       │                                  │
                       │ ◄────────────────── HTTP POST ───┤
                       │ (Send Message vía Conversations API)
                       │                                  │ HTTP POST a /pago-detectado
                       │                                  │ (desde n8n a GHL webhook entrante)
                       ▼                                  │
              ┌────────────────────────────────────────┐  │
              │                  n8n                   │  │
              │  • POST /inbound (conversación)        │──┘
              │  • POST /vision-only (solo imagen)     │
              │  • POST /generate-reengagement-message │──┐
              │                                        │  │
              │  ┌──────────────────────────────────┐  │  │ HTTP a OpenAI API
              │  │ Memory (LangChain Postgres)      │──┼──┼─────────────────┐
              │  │ Session ID: {phone}_2131         │  │  │                 │
              │  └──────────────────────────────────┘  │  │                 ▼
              │  ┌──────────────────────────────────┐  │  │       ┌────────────────┐
              │  │ Tools del Vendedor               │  │  │       │   OpenAI API   │
              │  │  - IDENTIFICAR_EVENTO            │──┼──┼──────►│ gpt-4.1        │
              │  │  - MOSTRAR_PRODUCTOS             │  │  │       │ whisper-1      │
              │  │  - COTIZADOR                     │  │  │       └────────────────┘
              │  │  - ATENCION_PERSONALIZADA        │  │  │
              │  └──────────────────────────────────┘  │  │
              └────────────┬───────────────────────────┘  │
                           │                              │
                           │ SQL (LangChain Memory)       │
                           ▼                              │
                  ┌────────────────────┐                  │
                  │     Supabase Pro   │                  │
                  │  • messages        │                  │
                  │  • followups_log   │                  │
                  │  • leads_metrics   │                  │
                  └────────────────────┘                  │
                                                          │
                  ┌────────────────────┐                  │
                  │  Telegram Bot      │ ◄── HTTP POST ───┤
                  │  (la agencia operacional)│   (notificación)│
                  └────────────────────┘                  │
                                                          │
                  ┌────────────────────┐                  │
                  │  Redis (debouncing)│ ◄── n8n connector ┘
                  └────────────────────┘
```

---

## §2. Conexión GHL ↔ Meta WABA

### §2.1 Provisionamiento

- Crear sub-account dedicado en GHL para HPF.
- Conectar WhatsApp via GHL Marketplace (Conversations → WhatsApp → Connect).
- Authenticar con Meta Business Manager de HPF (acceso a la cuenta de Oscar).
- Mover el número actual de HPF (que hoy está en Kommo) al BSP de GHL.

**⚠️ Punto crítico de cutover:** el número de WA NO puede estar conectado a Kommo y GHL simultáneamente. El switch es atómico — se hace en una ventana corta de mantenimiento, idealmente fuera de horario laboral mexicano (sábado madrugada).

### §2.2 Mensajes outbound (GHL → lead)

GHL Conversations API:
- `POST /conversations/messages`
- Body: `{ type: "WhatsApp", contactId, message: "...", attachments: [...] }`
- Auth: API key del sub-account

Para mensajes de plantillas (HSM) — necesarios para iniciar conversación >24h tras último inbound — GHL maneja la aprobación con Meta. Las plantillas viven en Meta Business Manager.

### §2.3 Plantillas necesarias

| Plantilla | Categoría Meta | Uso | Variables |
|---|---|---|---|
| `hpf_re_engagement_v1` | Marketing | Reactivadores P1 y P2 | `{{1}}` = mensaje generado por LLM |
| `hpf_pago_confirmado` | Utility | Notificar al lead que su pago fue validado | — |
| `hpf_diseno_aprobado` | Utility | Notificar al lead que el diseño está aprobado | — |
| `hpf_envio` | Utility | Notificar tracking de envío | `{{1}}` = guía |

> Las plantillas se aprueban con Meta antes del go-live (puede tomar 24-72h por plantilla).

---

## §3. Conexión GHL ↔ n8n

### §3.1 Webhooks salientes desde GHL

3 endpoints n8n que GHL llama:

#### Endpoint `/inbound`

- **Quién llama:** WF-01 Section B (mensaje del lead que requiere conversación con el Vendedor).
- **Método:** POST.
- **Auth:** Bearer token (compartido en variables de n8n y Custom Value de GHL).
- **Payload:**

```json
{
  "opportunity_id": "abc123",
  "contact_id": "ct_xyz",
  "phone": "5233xxxxxxxx",
  "stage": "Products Shown",
  "message": {
    "type": "text|audio|image",
    "content": "Quiero info de las sandalias",
    "media_url": null
  },
  "custom_fields": {
    "evento_detectado": "XV",
    "productos_mostrados": "sandalias,cilindros",
    "cantidad_sandalias": 100,
    "codigo_postal": "44730",
    "had_information": true,
    "last_re_engagement_wave": "P2_W2"
  },
  "custom_values": {
    "vendedor_model": "gpt-4.1",
    "promo_activa": "7 DIAS DE PROMO",
    "telefono_oficial": "3315948670"
  }
}
```

- **Respuesta esperada:** 200 OK (n8n procesa async, no devuelve la respuesta del Vendedor en este HTTP).
- **n8n envía la respuesta vía GHL Conversations API (out-of-band).**

#### Endpoint `/vision-only`

- **Quién llama:** WF-01 Section B caso imagen + stage IA-pausada, o WF-05 caso imagen fuera de horario.
- **Método:** POST.
- **Payload:**

```json
{
  "opportunity_id": "abc123",
  "contact_id": "ct_xyz",
  "image_url": "https://...",
  "current_stage": "In Production"
}
```

- **Respuesta esperada:** 200 OK con el resultado de la clasificación (síncrono — GHL puede actuar inmediatamente).

```json
{
  "producto": "NINGUNO",
  "confianza": 0.95,
  "razon": "captura de pantalla de transferencia bancaria visible",
  "payment_proof": true
}
```

- Si `payment_proof: true`, n8n también hace POST a `/pago-detectado` (ver §3.2) para gatillar WF-04.

#### Endpoint `/generate-reengagement-message`

- **Quién llama:** WF-02 antes de enviar cada wave.
- **Método:** POST.
- **Payload:**

```json
{
  "opportunity_id": "abc123",
  "wave": "P1_W2",
  "context": {
    "stage": "Products Shown",
    "evento_detectado": "XV",
    "productos_mostrados": "sandalias,cilindros",
    "cantidad_sandalias": 100,
    "cotizacion_emitida": false,
    "tiempo_desde_outbound": "3 horas"
  }
}
```

- **Respuesta esperada:**

```json
{
  "message": "Hola de nuevo! Te leí pero capaz quedaste con dudas con las 100 sandalias para tu XV. Si me confirmás CP y tipo de suela termino tu cotización ✨"
}
```

### §3.2 Webhooks entrantes a GHL (desde n8n)

#### Webhook `/pago-detectado` (en GHL)

- **Quién llama:** n8n cuando Vision Classifier devuelve `payment_proof: true`.
- **Trigger en GHL:** Inbound Webhook trigger en WF-04.
- **Auth:** Bearer token.
- **Payload:** ver §5.2 de `03_workflows_ghl.md`.

### §3.3 n8n usa la API REST de GHL para:

| Acción | Endpoint GHL |
|---|---|
| Enviar mensaje WhatsApp al lead | `POST /conversations/messages` |
| Actualizar Custom Field del Opportunity | `PUT /opportunities/{id}` |
| Aplicar/remover tag | `PUT /opportunities/{id}/tags` o `DELETE /opportunities/{id}/tags/{tag}` |
| Lookup de Custom Object Producto | `GET /objects/{schemaId}/records?query=...` |
| Lookup de Custom Values | `GET /locations/{locationId}/customValues` |

Auth: API key (PIT — Private Integration Token) del sub-account. **Vive como variable de entorno en n8n**, no en código.

---

## §4. Conexión n8n ↔ Supabase

### §4.1 Driver

n8n usa el nodo **Postgres** (no Supabase SDK) configurado con las credenciales de la conexión Postgres de Supabase (las mismas que ya usa hoy LangChain Memory).

Variables:
- `SUPABASE_PG_HOST`, `SUPABASE_PG_PORT`, `SUPABASE_PG_USER`, `SUPABASE_PG_PASSWORD`, `SUPABASE_PG_DB`.

### §4.2 LangChain Memory en n8n

El nodo `Postgres Chat Memory` de n8n (LangChain integration) se configura con:

```
Session ID: {{ $json.phone }}_2131
Table: messages
Window length: 30
```

Sin cambios respecto al stack actual — solo apuntando al mismo Supabase.

### §4.3 Tablas adicionales que n8n escribe

- `followups_log`: cada wave de re-engagement enviada (escribe desde WF-02 vía HTTP a un endpoint n8n `/log-followup`, o directamente vía Supabase REST API desde GHL HTTP Action).
- `leads_metrics`: post-MVP, escritura en transiciones clave del Opportunity.

---

## §5. Conexión n8n ↔ OpenAI

### §5.1 Modelos usados

| Llamada | Modelo | Endpoint |
|---|---|---|
| Vendedor (conversacional + tool calling) | `gpt-4.1` | `POST /v1/chat/completions` |
| Vision Classifier | `gpt-4.1` (con `image_url` en messages) | `POST /v1/chat/completions` |
| Re-engagement generator | `gpt-4.1-mini` | `POST /v1/chat/completions` |
| Transcripción audio | `whisper-1` | `POST /v1/audio/transcriptions` |

### §5.2 Auth y manejo de errores

- API key en variable de entorno n8n (`OPENAI_API_KEY`).
- Retry policy: 3 reintentos con backoff exponencial (1s, 3s, 9s).
- Timeout: 60s para conversacional, 30s para Vision, 60s para Whisper.
- Si los 3 reintentos fallan: fallback mensaje genérico al lead + apply tag `ai_failed_needs_human` + notify Telegram.

### §5.3 Prompt caching de OpenAI

Habilitar `prompt_cache_key` en las llamadas al Vendedor (system prompt es grande y se repite por mensaje). Reducción esperada de costos: 40-60% del input tokens cacheable.

```python
# n8n: configurar headers/parámetros en la llamada
extra_body = {
  "prompt_cache_key": "hpf-vendedor-v1"  # mismo cache key para todas las llamadas
}
```

---

## §6. Conexión GHL ↔ Telegram (notificaciones)

GHL Workflow ejecuta HTTP Action al Bot de Telegram de la agencia (no requiere n8n intermediario para esto):

- **Endpoint:** `https://api.telegram.org/bot{TOKEN}/sendMessage`
- **Auth:** token del bot la agencia (Custom Value `telegram_bot_token` en GHL).
- **Payload:**

```json
{
  "chat_id": "{telegram_chat_id_hpf}",
  "text": "🟢 Pago detectado | Lead: 5233xxxxx | Stage previa: Quoted | Opportunity: https://app.gohighlevel.com/...",
  "parse_mode": "Markdown"
}
```

`telegram_chat_id_hpf` viene de Custom Value del sub-account (el grupo de Telegram del equipo HPF).

### §6.1 Eventos que notifican Telegram

| Evento | Mensaje |
|---|---|
| Pago detectado (Vision Classifier) | `🟢 Pago detectado | {phone} | Stage previa: {stage} | Opp: {url}` |
| Pago de liquidación detectado | `🟢 Pago liquidación | {phone} | Opp: {url}` |
| Lead derivado a humano (tool ATENCION_PERSONALIZADA) | `🟡 Atención humana | {phone} | Motivo: {motivo} | Opp: {url}` |
| Imagen no clasificable | `🟠 Imagen no clasificable | {phone} | Opp: {url}` |
| PDF recibido | `🟠 PDF recibido | {phone} | Opp: {url}` |
| Vendedor falló (ai_failed_needs_human) | `🔴 IA falló | {phone} | Opp: {url}` |
| Lead en stage inesperada con imagen pago | `⚠️ Pago en stage rara: {stage} | {phone}` |

---

## §7. Conexión n8n ↔ Redis (debouncing)

Reutilización del Redis actual:
- Key: `debounce:{phone}` con TTL 45s.
- Push al recibir mensaje, get tras Wait, comparar timestamp último.

Sin cambios respecto al stack actual.

---

## §8. Resumen de variables de entorno y credenciales

### §8.1 En n8n

```
OPENAI_API_KEY               # Cuenta OpenAI la agencia
GHL_API_KEY_HPF              # PIT del sub-account HPF
GHL_LOCATION_ID_HPF          # Location ID del sub-account
SUPABASE_PG_HOST
SUPABASE_PG_PORT
SUPABASE_PG_USER
SUPABASE_PG_PASSWORD
SUPABASE_PG_DB
REDIS_HOST
REDIS_PORT
TELEGRAM_BOT_TOKEN           # Bot la agencia
TELEGRAM_CHAT_ID_HPF         # Grupo de operaciones HPF
```

### §8.2 En GHL (Custom Values del sub-account)

```
n8n_webhook_inbound_url       # https://[TU-INSTANCIA-N8N]/webhook/hpf-inbound
n8n_webhook_vision_url        # https://[TU-INSTANCIA-N8N]/webhook/hpf-vision-only
n8n_webhook_reengagement_url  # https://[TU-INSTANCIA-N8N]/webhook/hpf-reengagement
n8n_webhook_auth_token        # Bearer token compartido
telegram_bot_token            # Token Bot la agencia
telegram_chat_id_hpf          # Chat ID grupo HPF
... + todos los Custom Values funcionales definidos en 02_data_model.md
```

---

## §9. Esquemas de payloads — referencia rápida

| Conexión | Endpoint | Direction | Payload schema en |
|---|---|---|---|
| GHL → n8n | `/inbound` | outbound de GHL | §3.1 |
| GHL → n8n | `/vision-only` | outbound de GHL | §3.1 |
| GHL → n8n | `/generate-reengagement-message` | outbound de GHL | §3.1 |
| n8n → GHL | `/pago-detectado` | inbound a GHL | §3.2 (cuerpo en `03_workflows_ghl.md §5.2`) |
| n8n → GHL | API REST `/conversations/messages` | outbound de n8n | §3.3 |
| n8n → Supabase | SQL via Postgres connector | bidireccional | §4 |
| n8n → OpenAI | `/v1/chat/completions` | outbound de n8n | §5 |
| GHL → Telegram | `/bot/sendMessage` | outbound de GHL | §6 |

---

## §10. Manejo de errores cross-system

| Falla | Detección | Acción |
|---|---|---|
| n8n inaccesible (downtime, hot reload) | GHL HTTP Action retorna >500 | Retry 3 veces; si todos fallan, apply tag `ai_failed_needs_human` + notify Telegram |
| GHL API rate limit (200K/día por location) | n8n recibe 429 | Backoff exponencial, log a Supabase, alerta cuando se acerca el límite |
| Supabase caído | n8n LangChain Memory falla | Vendedor opera sin memoria (degraded), pero responde — notify Telegram con alerta de severidad |
| OpenAI caído | n8n recibe 503 | Fallback mensaje + tag `ai_failed_needs_human` |
| Meta WABA caído | GHL no recibe inbound | Notificación de GHL native; no hay nada que hacer hasta que Meta vuelva |
| Token GHL expira | n8n recibe 401 | Alerta inmediata Telegram a el equipo |

---

## §11. Seguridad

- **TLS obligatorio** en todos los webhooks (HTTPS-only).
- **Bearer tokens** compartidos entre GHL Custom Values y n8n env, rotación cada 90 días.
- **Variables sensibles** nunca en código — solo env vars (n8n) o Custom Values protegidos (GHL).
- **Logs** sanitizan PII (números de teléfono parcialmente enmascarados en logs no operacionales).
- **Supabase** RLS activado en tablas que el frontend (post-MVP dashboard) consuma. `messages` queda accesible solo desde service role (n8n).

---

## §12. Observabilidad (mínima MVP)

| Qué se monitorea | Cómo |
|---|---|
| Mensajes inbound procesados por minuto | n8n built-in execution log + dashboard |
| Latencia del Vendedor (p50, p95, p99) | n8n execution duration + alerta si p95 > 10s |
| Tasa de fallos del Vendedor | Conteo de tag `ai_failed_needs_human` aplicados por día |
| Volumen de uso de tools | Log a Supabase: cada tool call con metadata |
| Costos OpenAI mensuales | Dashboard OpenAI nativo + alerta si supera budget mensual |
| Tasa de respuesta del lead post-wave | Query a `followups_log` (manual o dashboard) |
| Conversiones Won/Lost | Query a GHL Opportunities por stage |

Post-MVP: integrar a un dashboard unificado (Looker Studio sobre Supabase).
