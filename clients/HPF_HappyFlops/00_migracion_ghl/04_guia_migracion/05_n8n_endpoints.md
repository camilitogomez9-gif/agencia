# M5 — n8n: Endpoints y Lógica IA

> **Referencia:** `03_arquitectura_ghl/04_agentes_llm.md`, `03_arquitectura_ghl/06_integraciones.md`  
> **Tiempo estimado:** 8-10 horas  
> **Prerequisito:** M2 y M4 completos (Custom Fields y Workflows GHL creados)

---

## 5.0 Variables de entorno n8n

Antes de crear los workflows, configurar en n8n → **Settings → Environment Variables** (o `.env` de la instancia):

```env
# GHL
GHL_API_KEY=Bearer [key de M1]
GHL_LOCATION_ID=[sub_account_id de M1]
GHL_BASE_URL=https://services.leadconnectorhq.com
WF04_WEBHOOK_URL=[URL del webhook WF-04 de M4]

# OpenAI
OPENAI_API_KEY=[key de Oscar o la agencia]

# Supabase
SUPABASE_DB_URL=postgresql://postgres:[password]@[host]:5432/postgres
SUPABASE_ANON_KEY=[anon key]

# Redis (debouncing)
REDIS_URL=redis://:[password]@[host]:6379

# Telegram (notificaciones Oscar)
TELEGRAM_BOT_TOKEN=[token del bot]
TELEGRAM_CHAT_ID_OSCAR=[chat_id de Oscar]

# Auth interna
HPF_WEBHOOK_SECRET=[string random 32 chars — inventar ahora]
```

---

## 5.1 Workflow: HPF Inbound Handler

**Name:** `HPF Inbound Handler`

### 5.1.1 Trigger: Webhook `/webhook/hpf-inbound`

GHL WF-01 llama a este endpoint. Schema del body (GHL lo arma automáticamente si se configura así en WF-01):

```json
{
  "contact_id": "ghl_contact_abc123",
  "opportunity_id": "ghl_opp_xyz789",
  "phone": "+523312345678",
  "message": {
    "type": "text|audio|image",
    "text": "Hola quiero sandalias para mi XV",
    "media_url": "https://storage.googleapis.com/...",
    "media_type": "image/jpeg"
  },
  "stage": "Evento Identificado",
  "custom_fields": {
    "evento_detectado": "XV",
    "imagen_input": false,
    "productos_mostrados": "[]",
    "cotizacion_emitida": false,
    "monto_cotizado_mxn": 0,
    "cp_entrega": "",
    "had_information": false,
    "had_image": false,
    "had_quote": false,
    "last_outbound_at": "2026-07-15T14:30:00Z"
  }
}
```

### 5.1.2 Nodo: Autenticación

```javascript
// Code node
const authHeader = $input.first().headers['authorization'];
const expectedToken = `Bearer ${$env.HPF_WEBHOOK_SECRET}`;
if (authHeader !== expectedToken) {
  throw new Error('Unauthorized');
}
return $input.all();
```

### 5.1.3 Nodo: Debounce Redis

Antes de procesar, verificar que no hay un mensaje más reciente en los últimos 30-45 segundos del mismo contacto.

```javascript
// Code node — Check debounce
const contactId = $json.contact_id;
const redisKey = `hpf_debounce_${contactId}`;

// Via HTTP Request a Redis REST API (Upstash) o módulo Redis nativo
// Si hay valor en Redis → retornar { skip: true }
// Si no hay valor → SET con EX 40 → retornar { skip: false }
```

**Si `skip: true`:** IF node → Stop execution.

### 5.1.4 Nodo: Branch por tipo de mensaje

**Switch node** según `message.type`:

- `audio` → **Subflow: Transcripción**
- `image` → **Subflow: Vision Classifier**
- `text` → **Subflow: Vendedor** (directo)

### 5.1.5 Subflow: Transcripción de audio

```
HTTP Request: POST https://api.openai.com/v1/audio/transcriptions
Headers: Authorization: Bearer {{$env.OPENAI_API_KEY}}
Body (multipart/form-data):
  file: [descargar media_url y pasar como buffer]
  model: whisper-1
  language: es
  response_format: text

→ Merge resultado como texto → continuar a Vendedor
```

Para descargar el archivo antes: nodo HTTP Request GET a `media_url` con output `Binary`.

### 5.1.6 Subflow: Vision Classifier

```
HTTP Request: POST https://api.openai.com/v1/chat/completions
Headers: Authorization: Bearer {{$env.OPENAI_API_KEY}}
Body:
{
  "model": "gpt-4.1",
  "temperature": 0,
  "response_format": { "type": "json_object" },
  "messages": [
    {
      "role": "system",
      "content": "[VISION CLASSIFIER SYSTEM PROMPT — ver 04_agentes_llm.md §2]"
    },
    {
      "role": "user",
      "content": [
        {
          "type": "image_url",
          "image_url": { "url": "{{$json.message.media_url}}" }
        }
      ]
    }
  ]
}

→ Parsear response.choices[0].message.content (JSON)
→ Campos: { "producto": "...", "confianza": 0.0-1.0, "razon": "...", "payment_proof": true|false }
```

**Branch post-Vision:**

```
If payment_proof = true:
  → POST {{$env.WF04_WEBHOOK_URL}} con opportunity_id y datos
  → Update GHL CF payment_proof_detectado = true
  → STOP (WF-04 toma el control)

If confianza >= 0.7:
  → Update GHL CF ultima_imagen_clasificada = producto
  → Continuar a Vendedor con contexto de imagen
  → Update GHL CF imagen_input = true

If confianza < 0.7:
  → Continuar a Vendedor con contexto "imagen no identificada"
```

### 5.1.7 Subflow: Vendedor (LLM principal)

**Paso A: Obtener historial de Supabase (LangChain Memory)**

```sql
SELECT message FROM messages
WHERE session_id = '{{phone}}_2131'
ORDER BY id ASC
LIMIT 30
```

Construir el array `messages` para la API:
```javascript
const history = supabaseResult.map(row => {
  const msg = JSON.parse(row.message); // formato LangChain
  return {
    role: msg.type === 'human' ? 'user' : 'assistant',
    content: msg.data.content
  };
});
```

**Paso B: Construir system prompt**

El system prompt del Vendedor se almacena en el nodo (no en GHL). Ver `03_arquitectura_ghl/04_agentes_llm.md §1` para la estructura completa de las 7 secciones.

Valores dinámicos que el system prompt recibe via `custom_values` inyectados como parte del contexto:

```javascript
const systemPrompt = `[VENDEDOR SYSTEM PROMPT]

--- CONTEXTO ACTUAL DEL LEAD ---
Stage: ${stage}
Evento detectado: ${custom_fields.evento_detectado || 'No detectado aún'}
Cotización emitida: ${custom_fields.cotizacion_emitida}
Monto cotizado: $${custom_fields.monto_cotizado_mxn} MXN
CP entrega: ${custom_fields.cp_entrega || 'No informado'}
Imagen recibida: ${custom_fields.imagen_input}
Producto imagen: ${custom_fields.ultima_imagen_clasificada || 'N/A'}

--- PRECIOS VIGENTES ---
Sandalia delgada: $[precio_sandalias_delgadas] MXN
Sandalia gruesa: $[precio_sandalias_gruesas] MXN
Sandalia yute: $[precio_sandalias_yute] MXN
[completar con otros productos]
`;
```

**Paso C: Llamada a OpenAI con tools**

```json
{
  "model": "gpt-4.1",
  "temperature": 0.3,
  "max_tokens": 800,
  "messages": [
    { "role": "system", "content": "[system prompt completo]" },
    ...history,
    { "role": "user", "content": "[mensaje actual del lead]" }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "IDENTIFICAR_EVENTO",
        "description": "Registrar el evento detectado del lead",
        "parameters": {
          "type": "object",
          "properties": {
            "evento": { "type": "string", "enum": ["XV", "Boda", "Bautizo", "Cumpleaños", "Empresarial", "Otro"] }
          },
          "required": ["evento"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "MOSTRAR_PRODUCTOS",
        "description": "Marcar que se mostraron productos al lead",
        "parameters": {
          "type": "object",
          "properties": {
            "productos": {
              "type": "array",
              "items": { "type": "string" },
              "description": "Lista de IDs de productos mostrados"
            },
            "imagen_evento": { "type": "string", "description": "URL de imagen del evento a enviar" }
          },
          "required": ["productos"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "COTIZADOR",
        "description": "Calcular y emitir cotización al lead",
        "parameters": {
          "type": "object",
          "properties": {
            "cantidad_sandalias": { "type": "number" },
            "tipo_suela": { "type": "string", "enum": ["Delgada", "Gruesa", "Yute"] },
            "cantidad_cilindros": { "type": "number" },
            "cantidad_mandiles": { "type": "number" },
            "cantidad_otros": { "type": "number" },
            "cp_entrega": { "type": "string" }
          }
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "ATENCION_PERSONALIZADA",
        "description": "Transferir al equipo humano. Usar cuando: precio regateo extremo, caso muy complejo, lead pide hablar con persona.",
        "parameters": {
          "type": "object",
          "properties": {
            "razon": { "type": "string" },
            "resumen_conversacion": { "type": "string" }
          },
          "required": ["razon", "resumen_conversacion"]
        }
      }
    }
  ],
  "tool_choice": "auto"
}
```

**Paso D: Procesar tool calls**

```javascript
// Code node
const response = $json.choices[0];
const toolCalls = response.message.tool_calls || [];

const actions = [];

for (const tc of toolCalls) {
  const args = JSON.parse(tc.function.arguments);
  
  if (tc.function.name === 'IDENTIFICAR_EVENTO') {
    actions.push({ type: 'update_cf', field: 'evento_detectado', value: args.evento });
    actions.push({ type: 'update_cf', field: 'had_information', value: true });
  }
  
  if (tc.function.name === 'MOSTRAR_PRODUCTOS') {
    actions.push({ type: 'update_cf', field: 'productos_mostrados', value: JSON.stringify(args.productos) });
    actions.push({ type: 'update_cf', field: 'had_image', value: !!args.imagen_evento });
    if (args.imagen_evento) {
      actions.push({ type: 'send_media', url: args.imagen_evento });
    }
  }
  
  if (tc.function.name === 'COTIZADOR') {
    // Calcular total
    const precios = { Delgada: 25, Gruesa: 30, Yute: 35 }; // usar Custom Values reales
    const totalSandalias = (args.cantidad_sandalias || 0) * (precios[args.tipo_suela] || 25);
    // + cilindros, mandiles, otros
    const total = totalSandalias; // simplificado
    
    actions.push({ type: 'update_cf', field: 'cotizacion_emitida', value: true });
    actions.push({ type: 'update_cf', field: 'monto_cotizado_mxn', value: total });
    actions.push({ type: 'update_cf', field: 'had_quote', value: true });
    actions.push({ type: 'update_cf', field: 'cotizacion_generada_at', value: new Date().toISOString() });
    
    // Guardar datos de cotización
    Object.entries(args).forEach(([k, v]) => {
      actions.push({ type: 'update_cf', field: k, value: v });
    });
    
    actions.push({ type: 'move_stage', stage: 'Cotizado' });
  }
  
  if (tc.function.name === 'ATENCION_PERSONALIZADA') {
    actions.push({ type: 'apply_tag', tag: 'atencion_humana' });
    actions.push({ type: 'notify_telegram', message: `🚨 Lead ${phone} necesita atención humana.\nRazón: ${args.razon}\nResumen: ${args.resumen_conversacion}` });
    actions.push({ type: 'move_stage', stage: 'Esperando Pago' }); // stage de atención personalizada
  }
}

// El texto de respuesta del Vendedor
const vendedorText = response.message.content;

return [{ actions, vendedorText, contactId, opportunityId, phone }];
```

**Paso E: Ejecutar acciones en GHL**

Para cada `action` del array:

- `update_cf` → `PATCH https://services.leadconnectorhq.com/opportunities/[opp_id]`  
  Body: `{ "customFields": [{ "key": "[field_key]", "value": "[value]" }] }`

- `move_stage` → `PUT https://services.leadconnectorhq.com/opportunities/[opp_id]`  
  Body: `{ "pipelineStageId": "[stage_id]" }` — los stage IDs se obtienen via `GET /opportunities/pipelines`

- `apply_tag` → `POST https://services.leadconnectorhq.com/contacts/[contact_id]/tags`  
  Body: `{ "tags": ["atencion_humana"] }`

- `send_media` → ver §5.1.8

- `notify_telegram` → HTTP Request al bot de Telegram

**Paso F: Enviar respuesta del Vendedor al lead**

```
POST https://services.leadconnectorhq.com/conversations/messages
Authorization: Bearer [GHL_API_KEY]
{
  "type": "WhatsApp",
  "contactId": "[contact_id]",
  "message": "[vendedorText]"
}
```

**Paso G: Guardar en Supabase (LangChain Memory)**

```sql
-- Insertar mensaje del lead (human)
INSERT INTO messages (session_id, message) VALUES (
  '{{phone}}_2131',
  '{"type": "human", "data": {"content": "{{message_text}}"}}'
);

-- Insertar respuesta del Vendedor (ai)
INSERT INTO messages (session_id, message) VALUES (
  '{{phone}}_2131',
  '{"type": "ai", "data": {"content": "{{vendedorText}}"}}'
);
```

**Paso H: Actualizar `last_outbound_at`**

⏱️ `last_outbound_at` y `last_inbound_at` son **Single line text en GHL** (GHL no soporta Date/Time). n8n los escribe como **string ISO 8601** con `$now.toISO()` — NO como objeto Date ni token `{{now}}` crudo, así el valor queda parseable de vuelta.

```
PATCH /opportunities/[opp_id]
{
  "customFields": [
    { "key": "last_outbound_at", "value": "{{ $now.toISO() }}" },
    { "key": "last_inbound_at", "value": "{{ $now.toISO() }}" }
  ]
}
```

---

## 5.2 Workflow: HPF Generate Re-engagement Message

**Name:** `HPF Re-engagement Generator`  
**Trigger:** Webhook `/webhook/hpf-reengagement`

Schema del body (enviado por WF-02):

```json
{
  "opportunity_id": "...",
  "contact_id": "...",
  "phone": "+52...",
  "wave": "P1_W1",
  "stage": "Productos Mostrados",
  "context": {
    "evento_detectado": "XV",
    "productos_mostrados": "sandalias,cilindros",
    "cantidad_sandalias": 100,
    "cantidad_cilindros": 50,
    "cotizacion_emitida": false,
    "last_outbound_summary": "...",
    "tiempo_desde_outbound": "1 hora"
  }
}
```

**Flujo:**

1. Auth check (mismo que 5.1.2)
2. Obtener últimos 5 mensajes de Supabase (para no repetir)
3. Llamar a OpenAI gpt-4.1-mini con el prompt de re-engagement (ver `05_reengagement.md §3.3`)
4. Responder al webhook con `{ "message": "[texto generado]" }`
5. WF-02 en GHL recibe el texto y lo envía al lead

---

## 5.3 Workflow: HPF Vision Only

**Name:** `HPF Vision Only`  
**Trigger:** Webhook `/webhook/hpf-vision`

Para casos donde GHL detecta una imagen antes de tener un opportunity activo (lead muy nuevo).  
Schema: mismo que `hpf-inbound` pero solo campos de imagen.

Devuelve:
```json
{
  "producto": "sandalias",
  "confianza": 0.85,
  "payment_proof": false
}
```

---

## 5.4 Workflow: HPF Inactivity Sweep (n8n)

**Name:** `HPF Inactivity Sweep`  
**Trigger:** Schedule — todos los días 08:00 CST

```javascript
// 1. Query a GHL API para oportunidades en stage "En Espera"
// GET /opportunities?pipelineStageId=[EN_ESPERA_STAGE_ID]&limit=100

// 2. Para cada oportunidad:
const cutoffDate = new Date();
cutoffDate.setDate(cutoffDate.getDate() - 180);

for (const opp of opportunities) {
  const completedAt = new Date(opp.customFields.re_engagement_completed_at);
  const lastInbound = new Date(opp.customFields.last_inbound_at || 0);
  
  if (completedAt < cutoffDate && lastInbound < cutoffDate) {
    // Mover a "Ventas Perdidas"
    await updateOpportunityStage(opp.id, VENTAS_PERDIDAS_STAGE_ID);
  }
}
```

---

## 5.5 Obtener Stage IDs de GHL

⚠️ Los workflow de n8n necesitan los IDs internos de cada stage para hacer llamadas a la API. Hacer esto UNA VEZ y guardar los IDs en las variables de entorno o en un nodo de configuración.

```bash
# Llamada para obtener el pipeline con sus stages
curl -X GET "https://services.leadconnectorhq.com/opportunities/pipelines?locationId=[LOCATION_ID]" \
  -H "Authorization: Bearer [GHL_API_KEY]" \
  -H "Version: 2021-07-28"
```

Guardar el resultado y mapear:

```javascript
// Las keys deben coincidir EXACTO con los nombres de stage creados en GHL (español).
const STAGE_IDS = {
  'Lead Nuevo': 'stage_id_1',
  'Saludo Enviado': 'stage_id_2',
  'Evento Identificado': 'stage_id_3',
  'Productos Mostrados': 'stage_id_4',
  'Cotizado': 'stage_id_5',
  'Esperando Pago': 'stage_id_6',
  'Pago Confirmado': 'stage_id_7',
  'Diseño en Proceso': 'stage_id_8',
  'En Producción': 'stage_id_9',
  'Enviado': 'stage_id_10',
  'En Espera': 'stage_id_11',
  'Ganado': 'stage_id_12',
  'Ventas Perdidas': 'stage_id_13',
};
```

Agregar esto como variables de entorno en n8n o como un nodo de configuración al inicio de cada workflow.

---

## ✅ Checklist M5

- [ ] Variables de entorno configuradas en n8n
- [ ] Stage IDs de GHL obtenidos y guardados
- [ ] WF `HPF Inbound Handler` creado:
  - [ ] Auth check
  - [ ] Debounce Redis
  - [ ] Branch audio/imagen/texto
  - [ ] Transcripción Whisper
  - [ ] Vision Classifier con branch payment_proof
  - [ ] Vendedor con tools y system prompt
  - [ ] Acciones GHL ejecutadas (update CF, move stage, apply tags)
  - [ ] Mensaje enviado via GHL API
  - [ ] Guardado en Supabase
- [ ] WF `HPF Re-engagement Generator` creado
- [ ] WF `HPF Inactivity Sweep` creado
- [ ] Test de cada endpoint con Postman/Insomnia antes de conectar con GHL

**Siguiente:** M6 → Supabase: tablas y conexión
