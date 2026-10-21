# Data Model GHL — Happy Flops

> **Etapa 3.** Schema completo de Custom Fields (Contact + Opportunity), Custom Values (sub-account), Custom Object "Producto" (catálogo) y tablas Supabase complementarias.

> 🔒 **CUSTOM VALUE KEYS — fuente de verdad en M2 (2026-06-19):** este doc usa keys de Custom Values en estilo snake_case-inglés (`re_engagement_fase1_active`, `vacaciones_active`, `business_hours_start`, etc.). En la implementación real **GHL autogenera la key desde el Name (en español) y no permite editarla** → las keys reales son las que muestra `04_guia_migracion/02_pipeline_y_campos.md` §2.5 ("Mapeo de Custom Value keys — vieja → real"). Al cablear workflows o n8n, usar SIEMPRE las keys reales de M2. Este doc queda como referencia conceptual.

---

## §1. Principio organizador

| Tipo de dato | Vive en | Razón |
|---|---|---|
| Identidad del lead (nombre, teléfono, etc.) | GHL Contact (campos nativos) | Datos del **contacto** = persona, no transacción |
| Estado y datos de UNA conversación de venta | GHL Opportunity (Custom Fields) | Un mismo contacto puede tener varios negocios — preserva separación |
| Configuración global editable por Oscar | GHL Custom Values del sub-account | Lo que cambia "para todos los leads" |
| Catálogo de productos | GHL Custom Object "Producto" | Editable desde UI, asociable a Opportunity |
| Historial conversacional completo | Supabase `messages` | Ya existente, no migrar, sigue alimentándose desde n8n |
| Tracking de seguimientos enviados | Supabase `followups_log` (nuevo) | Auditar qué wave se envió cuándo a cada lead |
| Métricas (post-MVP) | Supabase `leads_metrics` (nuevo, post-cutover) | Tiempo de cierre, conversiones, etc. |

---

## §2. Contact (campos nativos + custom)

### §2.1 Nativos de GHL (usar tal cual)

- `firstName`, `lastName` (puede venir vacío si el lead no se identifica)
- `phone` (E.164, sin `+`)
- `email` (raro, opcional)
- `tags` (multi-valor)
- `dateAdded`, `lastActivity`
- `attribution` (canal de entrada — WhatsApp en este caso)

### §2.2 Custom Fields del Contact

Solo lo que es **del individuo**, no de una transacción específica.

| Custom Field | Tipo | Valores / formato | Propósito |
|---|---|---|---|
| `customer_status` | Dropdown | `prospect`, `customer`, `repeat_customer` | Marca si la persona ya compró. Se actualiza al llegar a `Won` por primera vez. |
| `preferred_language` | Dropdown | `es-MX` | Reservado para futuro multi-idioma. Default es-MX. |
| `total_purchases` | Number | 0+ | Auto-incrementa con cada `Won`. Útil para reportes. |
| `lifetime_value_mxn` | Number | 0+ | Suma de cotizaciones finales aceptadas. |
| `is_test_lead` | Checkbox | true/false | Manual. Sandbox / lead de Oscar. |

---

## §3. Opportunity (custom fields)

El Opportunity (una transacción / un "negocio") es donde vive **el estado de venta y los datos de la conversación**. Si el mismo lead vuelve después de meses, se crea un nuevo Opportunity en `New Lead`.

### §3.1 Datos del evento

| Custom Field | Tipo | Valores | Propósito |
|---|---|---|---|
| `evento_detectado` | Dropdown | `Boda`, `XV`, `Otros`, _vacío_ | Lo setea el Vendedor con tool `IDENTIFICAR_EVENTO`. WF-06 lo escucha para mover a `Event Identified`. |
| `fecha_evento` | Date | YYYY-MM-DD | Opcional, lo setea el Vendedor si el lead lo menciona |
| `dias_hasta_evento` | Number | computed (fecha_evento - today) | Para detectar pedidos <15 días → ATENCION_PERSONALIZADA |

### §3.2 Datos de cotización

| Custom Field | Tipo | Valores | Propósito |
|---|---|---|---|
| `productos_solicitados` | Multi-select | nombres de productos del catálogo | Lo setea el Vendedor con tool `MOSTRAR_PRODUCTOS`. WF-06 escucha. |
| `productos_mostrados` | Text (CSV) | `sandalias,cilindros,anticrudas` | Para no re-mostrar lo mismo. WF-06 escucha y mueve a `Products Shown`. |
| `cantidad_sandalias` | Number | 0+ | Recolectada durante la conversación |
| `cantidad_cilindros` | Number | 0+ | |
| `cantidad_pantuflas` | Number | 0+ | |
| `cantidad_mandiles` | Number | 0+ | (Solo Boda) |
| `cantidad_anticruda` | Number | 0+ | |
| `cantidad_vasos_popote` | Number | 0+ | |
| `cantidad_bolsa_personalizada` | Number | 0+ | |
| `tipo_sandalia` | Dropdown | `delgada`, `gruesa` | Necesario antes de cotizar |
| `codigo_postal` | Text | 5 dígitos MX | Para cálculo de envío |
| `cotizacion_total_mxn` | Number | 0+ | Total cotizado |
| `cotizacion_anticipo_mxn` | Number | 0+ | 50% del total |
| `cotizacion_emitida_at` | Datetime | ISO | Cuándo se emitió la cotización completa |

### §3.3 Datos de re-engagement

| Custom Field | Tipo | Valores | Propósito |
|---|---|---|---|
| `last_re_engagement_wave` | Text | `P1_W1`, `P1_W2`, `P1_W3`, `P2_W1`, `P2_W2`, `P2_W3`, `P2_W4` | Última wave enviada. WF-02 lee y actualiza. |
| `re_engagement_started_at` | Datetime | ISO | Cuándo arrancó el ciclo |
| `re_engagement_paused` | Checkbox | true/false | Oscar pausa manualmente desde el inbox si quiere |
| `had_information` | Checkbox | true/false | true si el lead avanzó a `Products Shown` o más (sustituye distinción sin/con info) |

### §3.4 Datos de pago y producción (post-cotización)

| Custom Field | Tipo | Valores | Propósito |
|---|---|---|---|
| `comprobante_anticipo_url` | File | URL | Imagen del comprobante del 50% inicial |
| `comprobante_anticipo_at` | Datetime | ISO | Cuándo se recibió |
| `comprobante_anticipo_confirmado_at` | Datetime | ISO | Cuándo el humano lo validó |
| `diseño_enviado_at` | Datetime | ISO | Diseñadora lo setea al enviar |
| `diseño_aprobado_at` | Datetime | ISO | Cuándo el lead aprobó |
| `produccion_inicio_at` | Datetime | ISO | Auto al pasar a stage `In Production` |
| `comprobante_liquidacion_url` | File | URL | |
| `comprobante_liquidacion_at` | Datetime | ISO | |
| `envio_paqueteria` | Dropdown | `Estafeta`, `FEDEX`, `Paquetexpress` | |
| `envio_guia` | Text | Tracking number | |

### §3.5 Datos auxiliares (tracking interno)

| Custom Field | Tipo | Valores | Propósito |
|---|---|---|---|
| `current_step` | Dropdown | `step_1`, `step_2`, `step_3`, `step_4` | Reservado por si Vendedor lo necesita. **Probablemente innecesario** ya que el stage del Opportunity es la fuente de verdad. Mantener solo si el Vendedor necesita un override granular. |
| `last_inbound_at` | Datetime | ISO | Última vez que el lead escribió. Útil para WF-02 (no enviar reactivador si el lead acaba de responder) y WF-03 (inactivity sweep). |
| `last_outbound_at` | Datetime | ISO | Última vez que el sistema le escribió |
| `attention_motive` | Text | Razón por la que se aplicó `human_takeover` | Para que el equipo vea contexto en el inbox |

> ⏱️ **Implementación en GHL (2026-06-19):** GHL **no soporta el tipo Date/Time** en custom fields, solo **Date** (sin hora). Por eso, los campos marcados arriba como `Datetime | ISO`:
> - **Time-críticos** (`last_inbound_at`, `last_outbound_at`) → se crean como **Single line text** y se guardan en **ISO 8601**; n8n hace el parseo/comparación. Son los que el reenganche compara dentro del mismo día.
> - **Day-granularidad suficiente** (`re_engagement_completed_at`, `diseño_aprobado_at`, `produccion_inicio_at`, `comprobante_*_at`, etc.) → **Date** nativo.
>
> El **mapeo de tipos canónico y final está en `04_guia_migracion/02_pipeline_y_campos.md`** (sección "GHL NO soporta Date/Time"). Ante discrepancia, manda M2.

---

## §4. Custom Values del sub-account (configuración global)

Estos son los "settings" que Oscar y Rebeca pueden editar **desde la UI de GHL** sin tocar ningún workflow. Cambian comportamiento del sistema en runtime.

### §4.1 Configuración de re-engagement

| Custom Value | Tipo | Valor por defecto | Propósito |
|---|---|---|---|
| `re_engagement_fase1_waves` | Text (CSV) | `1h,3h,5h` | Cadencias de Fase 1. Editable si Oscar quiere ajustar. |
| `re_engagement_fase1_active` | Boolean | `true` | Si está activa Fase 1 |
| `re_engagement_fase2_waves` | Text (CSV) | `24h,48h,120h,168h` | Cadencias de Fase 2 (en horas) |
| `re_engagement_fase2_active_days` | Text (CSV) | `R1,R2,R3,R4` | Qué waves de Fase 2 están activas (Oscar puede sacar `R3` y `R4` para bajar volumen de plantillas Meta) |

### §4.2 Configuración de horario laboral

| Custom Value | Tipo | Valor por defecto | Propósito |
|---|---|---|---|
| `business_hours_timezone` | Text | `America/Mexico_City` | TZ del negocio |
| `business_hours_days` | Text (CSV) | `Mon,Tue,Wed,Thu,Fri` | Días laborales |
| `business_hours_start` | Text | `09:00` | Inicio jornada |
| `business_hours_end` | Text | `17:30` | Fin jornada |
| `vacaciones_active` | Boolean | `false` | Si están de vacaciones extensas (override de business hours) |
| `vacaciones_mensaje` | Long Text | "Gracias por escribir. Estamos de vacaciones del [fecha] al [fecha]. Volvemos a responder cuando regresemos. ☀️" | Mensaje que se envía si `vacaciones_active = true` |

### §4.3 Configuración de catálogo y promo

| Custom Value | Tipo | Valor por defecto | Propósito |
|---|---|---|---|
| `promo_activa` | Text | `7 DIAS DE PROMO` | Nombre de la promo actual. Puede rotar (post-MVP) para A/B testing |
| `promo_duracion_dias` | Number | `7` | Duración de la promo en días |
| `promo_descripcion` | Long Text | Mensaje fijo de "SEMANA LOCA DE PROMOS!" | Texto que se envía con la imagen principal |
| `precio_sandalia_delgada` | Number | `25` | Precios editables sin redeploy |
| `precio_sandalia_gruesa` | Number | `30` | |
| `precio_pantufla_satin` | Number | `30` | |
| `precio_pantufla_mono_satin` | Number | `30` | |
| `precio_pantufla_mono_peluche` | Number | `35` | |
| `precio_cilindro` | Number | `10` | |
| `precio_mandil` | Number | `12` | |
| `precio_kit_anticruda` | Number | `10` | |
| `precio_vaso_popote` | Number | `35` | |
| `precio_bolsa_personalizada` | Number | `7` | |

> **Nota:** los precios también viven en el Custom Object Producto (§5). Mantener consistencia: el Custom Object es el source of truth; los Custom Values son atajos para que el Vendedor tenga acceso rápido sin tener que listar el Custom Object completo en cada llamada. **Decisión a validar en implementación:** si el Vendedor lee siempre del Custom Object, podemos eliminar los Custom Values de precios.

### §4.4 Configuración de contacto / negocio

| Custom Value | Tipo | Valor | Propósito |
|---|---|---|---|
| `telefono_oficial` | Text | `3315948670` | Único número permitido — chequeado por Vendedor |
| `direccion_taller` | Long Text | "JUAN R. ZAVALA #538 (CALLE 38), COL SAN JUAN BOSCO, GUADALAJARA, JALISCO, C.P. 44730" | Para responder consultas |
| `mapa_url` | URL | `https://goo.su/OVoA` | |
| `facebook_url` | URL | `https://www.facebook.com/happyflops` | |
| `facebook_reviews_url` | URL | `https://www.facebook.com/happyflops/reviews` | Si el lead pregunta "es estafa?" |

### §4.5 Configuración de IA (operativa, no producto)

| Custom Value | Tipo | Valor por defecto | Propósito |
|---|---|---|---|
| `vendedor_model` | Text | `gpt-4.1` | Modelo del Vendedor (editable si la agencia decide cambiar) |
| `vision_classifier_model` | Text | `gpt-4.1` | Modelo del Vision Classifier |
| `vendedor_temperature` | Number | `0.3` | Temperatura del Vendedor |
| `vision_temperature` | Number | `0` | Temperatura del Vision (debe ser 0) |
| `agente_nombre` | Text | `Rebeca` | Nombre con el que se presenta el agente |

---

## §5. Custom Object "Producto"

Reemplaza el catálogo Airtable (6 tablas). Una entrada por **producto × evento** (algunas combinaciones — ver matriz).

### §5.1 Schema del Custom Object

| Campo | Tipo | Ejemplo | Propósito |
|---|---|---|---|
| `producto_id` | Text (primary) | `sandalia_delgada_boda` | Identificador único |
| `producto_nombre` | Text | `Sandalias Delgadas` | Nombre humano |
| `evento` | Dropdown | `Boda`, `XV`, `Otros` | A qué evento aplica esta entrada |
| `categoria` | Dropdown | `Producto Principal`, `Accesorio` | Para reglas de upsell |
| `precio_unitario_mxn` | Number | 25 | Precio en MXN |
| `pedido_minimo` | Number | 50 | Cantidad mínima para cotizar |
| `peso_kg` | Number | 0.15 | Para cálculo de envío |
| `descripcion` | Long Text | "Sandalia delgada de 9mm..." | Texto que va con la ficha |
| `imagen_url` | File (asset) | URL al asset en GHL Files | Foto del producto |
| `pdf_catalogo_url` | File (opcional) | URL al PDF | Para algunos productos hay catálogo PDF |
| `disenos_permitidos_por_50_unidades` | Number | 1 | Para regla de personalización |
| `tintas_disponibles` | Text (CSV) | `oro,plata,blanca,fucsia,...` | Para responder consultas de color |
| `notas_especiales` | Long Text | "Pantuflas mono peluche solo blanca/negra/morada/rosa" | Notas adicionales |
| `activo` | Boolean | true | Para desactivar productos sin borrar la entrada |

### §5.2 Matriz de entradas del Custom Object

| Producto | Boda | XV | Otros | Total entradas |
|---|---|---|---|---|
| Sandalias delgadas | ✅ | ✅ | ✅ | 3 |
| Sandalias gruesas | ✅ | ✅ | ✅ | 3 |
| Pantuflas satín personalizadas | ✅ | ✅ | ✅ | 3 |
| Pantuflas mono satín | ✅ | ✅ | ❌ | 2 |
| Pantuflas mono peluche | ✅ | ✅ | ❌ | 2 |
| Cilindros 500ml | ✅ | ✅ | ✅ | 3 |
| Mandiles | ✅ | ❌ | ❌ | 1 |
| Kit anticruda | ✅ | ✅ | ✅ | 3 |
| Vasos popote | ✅ | ✅ | ❌ | 2 |
| Bolsa personalizada | ✅ | ✅ | ✅ | 3 |
| Bolsa shein (gratis) | ✅ | ✅ | ✅ | 3 |

Total: ~28 entradas en el Custom Object. Manejable manualmente, fácil de auditar.

### §5.3 Imagen principal por evento (otro objeto o entrada especial)

Hoy en Airtable hay una tabla "Imagen Principal" con la promo de cada evento. En GHL podemos:

- **Opción A:** Otro Custom Object "Imagen Principal" con 3 entradas (una por evento).
- **Opción B:** Custom Values `imagen_principal_boda_url`, `imagen_principal_xv_url`, `imagen_principal_otros_url`.

Recomendación: **Opción B** — son solo 3 valores, no justifican un Custom Object adicional.

### §5.4 Foto de vacaciones

`Custom Value vacaciones_imagen_url` apunta a un asset de GHL Files. WF-05 lo envía cuando `vacaciones_active = true`.

---

## §6. Tablas Supabase (memoria + tracking)

### §6.1 `messages` (existente, sin migración)

Schema actual (ya en uso):

```sql
CREATE TABLE messages (
  id          int4 PRIMARY KEY,
  session_id  varchar NOT NULL,     -- "<telefono_lead>_2131"
  message     jsonb NOT NULL        -- { type: "ai"|"human", content: "...", tool_calls: [], ... }
);
CREATE INDEX idx_messages_session ON messages(session_id);
CREATE INDEX idx_messages_created ON messages((message->>'created_at'));  -- si lo agregamos
```

**No requiere cambios.** El `session_id` puede seguir siendo `<telefono>_2131` (independiente de Kommo vs GHL).

> ⚠️ **Verificar antes de cutover:** que el `session_id` que use n8n en GHL siga generándose desde el teléfono del contacto, no desde el `contactId` interno de GHL (que es UUID y rompería continuidad con conversaciones previas en Kommo).

### §6.2 `followups_log` (nueva)

Tracking de qué wave de re-engagement se envió a qué lead y cuándo. Sustituye los `INSERT rows in a table` de los 4 sub-workflows actuales.

```sql
CREATE TABLE followups_log (
  id              serial PRIMARY KEY,
  opportunity_id  text NOT NULL,        -- GHL Opportunity ID
  contact_id      text NOT NULL,        -- GHL Contact ID
  phone           text,                 -- para lookup rápido
  wave            text NOT NULL,        -- P1_W1, P2_W3, etc.
  sent_at         timestamptz NOT NULL DEFAULT now(),
  message_content text,                 -- el texto que se envió (para auditar personalización)
  responded       boolean DEFAULT false,-- update cuando el lead responde
  responded_at    timestamptz
);
CREATE INDEX idx_followups_opp ON followups_log(opportunity_id);
CREATE INDEX idx_followups_wave ON followups_log(wave, sent_at);
```

Quién escribe: WF-02 vía HTTP action a un endpoint de n8n (o directo a Supabase REST API).

### §6.3 `leads_metrics` (nueva, post-MVP)

Para tracking de tiempo de cierre y análisis. **NO se construye en MVP** — se diseña ahora pero se implementa post-cutover.

```sql
CREATE TABLE leads_metrics (
  opportunity_id    text PRIMARY KEY,
  contact_id        text NOT NULL,
  phone             text NOT NULL,
  channel           text DEFAULT 'whatsapp',
  evento            text,
  first_contact_at  timestamptz NOT NULL,
  greeted_at        timestamptz,
  event_id_at       timestamptz,
  products_shown_at timestamptz,
  quoted_at         timestamptz,
  payment_at        timestamptz,
  won_at            timestamptz,
  lost_at           timestamptz,
  human_takeover_at timestamptz,
  total_messages_in int,
  total_messages_out int,
  total_re_eng_waves_sent int,
  cotizacion_total_mxn numeric,
  promo_asignada    text,                -- para A/B post-MVP
  outcome           text                 -- 'won', 'lost', 'in_progress', 'en_espera'
);
```

### §6.4 `catalogo_cache` (opcional, performance)

Si el Vendedor consulta el catálogo en cada cotización, en lugar de pegarle a la API de GHL cada vez podemos cachear en Supabase y sincronizar cuando Oscar edite el Custom Object.

**Decisión:** **NO** en MVP. El Vendedor recibe el catálogo precargado en el system prompt (es chico, 28 entradas). Si crece, evaluar caché.

---

## §7. Asociaciones entre objetos GHL

```
Contact ──┐ 1:N
          ├──► Opportunity (Pipeline IA)
          │       │
          │       │ 1:N (Custom Object "Producto" via association)
          │       └──► Productos cotizados (opcional, ver §7.1)
          │
          └──► Messages (Conversations nativo — todos los mensajes del contact)

Sub-account ──► Custom Values (1:N, globales)
            ──► Custom Object Producto (N entradas, no asociadas a Contact)
            ──► Custom Object Imagen Principal (3 entradas si Opción A, o Custom Values si Opción B)
```

### §7.1 ¿Asociar productos cotizados al Opportunity?

GHL permite asociar registros de Custom Object a Opportunities. Podemos asociar los productos cotizados al Opportunity para que en la vista del Kanban el equipo vea "este lead cotizó: sandalias delgadas, cilindros". Útil para reportes.

**Decisión MVP:** **NO asociar.** Usamos `productos_solicitados` (Multi-select Custom Field) — más simple, mismo resultado visible. Post-MVP evaluar si la asociación abre features de reportes.

---

## §8. Resumen — qué cambia para Oscar / Rebeca operativamente

| Acción que hace Oscar/Rebeca hoy | Dónde lo va a hacer post-migración |
|---|---|
| Cambiar precio de sandalia gruesa | Custom Value `precio_sandalia_gruesa` (UI GHL) — toma efecto en el próximo mensaje del Vendedor |
| Quitar 2 días de la promo de 7 días | Custom Value `re_engagement_fase2_active_days` (sacar `R3` y `R4` del CSV) |
| Activar mensaje de vacaciones | Custom Value `vacaciones_active = true` |
| Agregar un producto nuevo al catálogo | Custom Object Producto → New Record |
| Cambiar la foto de un producto | Custom Object Producto → editar registro, subir nueva imagen |
| Ver historia completa de un lead | GHL Conversations (los últimos N mensajes) + (post-MVP) dashboard con link al historial Supabase |
| Tomar control de una conversación (atención humana) | Inbox GHL: aplicar tag `human_takeover` o el sistema lo aplica automáticamente cuando el Vendedor llama ATENCION_PERSONALIZADA |
| Liberar la conversación (devolver a la IA) | Inbox GHL: quitar tag `human_takeover` |
