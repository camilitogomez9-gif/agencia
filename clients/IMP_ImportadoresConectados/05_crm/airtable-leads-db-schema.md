# Airtable — Base Leads Diego Labores

> Esquema de la base de Airtable que actúa como CRM de leads del agente de ventas de Diego Labores.
> El agente consulta esta base para leer el historial de conversación, detectar el perfil del lead y actualizar el estado del pipeline en cada interacción.

---

## Campos de la Tabla `Leads`

| Campo | Tipo Airtable | Descripción | Requerido |
|---|---|---|---|
| `nombre` | **Single line text** (campo primary) | Identificador del lead. Si no se conoce el nombre real, usar prefijo de canal: `ig_usuario123`, `wa_59891234567`, `fb_12345`. | ✅ |
| `telefono_whatsapp` | **Phone number** | Número de WhatsApp. Con código de país sin +: `59891234567` (UY), `541112345678` (AR). | ❌ Opcional |
| `email` | **Email** | Email del lead si lo comparte en la conversación. | ❌ Opcional |
| `pais` | **Single select** | Opciones: `Uruguay`, `Argentina`, `Otro`, `sin_definir`. | ✅ |
| `canal_ingreso` | **Single select** | Opciones: `instagram_dm`, `whatsapp`, `facebook`, `formulario_ads`, `telegram_test`. | ✅ |
| `fuente` | **Single select** | Opciones: `ads`, `organico`, `referido`, `desconocido`. | ✅ |
| `perfil_lead` | **Single select** | Opciones: `nunca_emprendo`, `intento_fracaso`, `ya_vende`, `solo_precio`, `sin_clasificar`. | ✅ |
| `etapa_conversion` | **Single select** | Ver tabla de estados abajo. | ✅ |
| `producto_interes` | **Single select** | Opciones: `importadores_conectados`, `asesoria_1a1`, `mentoria`, `consultoria`, `sin_definir`. | ✅ |
| `califica` | **Single select** | Opciones: `pendiente`, `si`, `no`. | ✅ |
| `historial` | **Long text** | Historial de conversación. Formato: `[LEAD]: mensaje\n[ASESOR]: respuesta`. Máx. 20 intercambios. | ✅ |
| `fecha_primer_contacto` | **Date** | Fecha del primer mensaje. Se setea al crear el registro. | ✅ |
| `fecha_ultima_interaccion` | **Date** | Fecha del último mensaje. Se actualiza en cada interacción. | ✅ |
| `record_id` | **Auto** | ID único generado por Airtable. Lo usa n8n para actualizar el registro. | Auto |
| `notas` | **Long text** | Notas manuales del equipo. No leído por el agente. | ❌ |

---

## Estados del Pipeline (`etapa_conversion`)

| Estado | Descripción | Quién lo setea |
|---|---|---|
| `apertura` | Primer intercambio | Agente (al crear el registro) |
| `diagnostico` | Preguntas de calificación en curso | Agente |
| `propuesta` | Se presentó el producto con precio | Agente |
| `cierre` | El lead mostró interés en comprar | Agente |
| `ganado` | Compra confirmada | Agente (detecta `[NOTIFICAR_CIERRE]`) |
| `perdido` | Rechazó o dejó de responder | Equipo (manual) |
| `descalificado` | Lead no aplica al perfil | Agente (detecta `[NOTIFICAR_DESCALIFICADO]`) |
| `pendiente_followup` | No cerró hoy, seguimiento pendiente | Agente (detecta `[NOTIFICAR_FOLLOWUP]`) |
| `agenda_solicitada` | Derivado a meet 30min con Diego | Agente (detecta `[NOTIFICAR_AGENDA]`) |

---

## Variables de Entorno en n8n

```
AIRTABLE_API_TOKEN=patXXXXXXXXXXXXXX.XXXXXXXX...
AIRTABLE_BASE_ID_DIEGOLABORES=appXXXXXXXXXXXXXX
AIRTABLE_TABLE_LEADS=Leads
GEMINI_API_KEY=AIzaSy...
MANYCHAT_API_KEY=XXXXXXXX...
WHATSAPP_PHONE_NUMBER_ID=XXXXXXXX         # solo si usa Meta Cloud API directa
WHATSAPP_ACCESS_TOKEN=XXXXXXXX            # solo si usa Meta Cloud API directa
TELEGRAM_BOT_TOKEN=xxxxxxxxx:xxxx...      # bot de notificaciones al equipo
TELEGRAM_CHAT_ID_EQUIPO=xxxxxxxxx
```

### Cómo obtener las credenciales de Airtable

**API Token:**
1. Ir a `https://airtable.com/create/tokens`
2. Crear un Personal Access Token
3. Scopes requeridos: `data.records:read`, `data.records:write`
4. Acceso: seleccionar la base de Diego Labores

**Base ID:**
La URL de la base en Airtable es: `https://airtable.com/appXXXXXXXXXXXXXX/...`
El Base ID es el string que empieza con `app`.

---

## Cómo el Agente Busca y Crea Leads en n8n

### Identificador por canal

| Canal | Campo `nombre` en Airtable |
|---|---|
| Instagram DM | `ig_` + username |
| WhatsApp | `wa_` + número sin + |
| Facebook DM | `fb_` + subscriber_id ManyChat |
| Telegram (prueba) | `tg_` + username |

### Operación de búsqueda (nodo Airtable en n8n)

- **Operación:** Search Records
- **Filter by formula:** `{nombre} = "ig_usuario123"` (se construye dinámicamente)
- Si no encuentra ningún resultado → crear registro nuevo con los datos iniciales

### Límite del historial

Airtable soporta hasta 100,000 caracteres en campos Long text, pero el historial se trunca en el Code node a los últimos ~3,000 caracteres para no sobrecargar el contexto del modelo.

---

## Vistas Recomendadas en Airtable

| Vista | Filtro | Orden |
|---|---|---|
| Pipeline activo | `etapa_conversion` ≠ ganado, perdido, descalificado | `fecha_ultima_interaccion` DESC |
| Follow-ups pendientes | `etapa_conversion` = pendiente_followup | `fecha_ultima_interaccion` ASC |
| Ventas cerradas | `etapa_conversion` = ganado | `fecha_ultima_interaccion` DESC |
| Por canal | Agrupar por `canal_ingreso` | — |
| Por producto | Agrupar por `producto_interes` | — |
