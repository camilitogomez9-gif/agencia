# WF_AGENTE_TELEGRAM_v1 — Template Agente Conversacional (Canal Telegram)

Template base para agentes IA de versión 1, canal Telegram. Originado en el proyecto
Sistemas & Soluciones (SYS). Se usa como punto de partida para nuevos clientes cuyo
canal principal de atención es Telegram.

---

## Arquitectura del Flujo

```
Telegram Trigger
  → Normalizar Payload           (extraer chatId, username, texto; ignorar comandos)
  → ¿Ignorar?                    (IF: comandos / skip)
      ↓ No skip
  → Buscar Lead en Airtable      (lookup por leadIdentifier)
  → ¿Lead Existe?                (IF)
      ↓ No          ↓ Sí
  → Crear Lead    → (merge)
  → Preparar Datos del Lead      (consolida historial + mensaje actual)
  → AI Agent                     (recibe mensajeActual + system prompt)
  → Parsear Respuesta            (split por ---, delays, etiquetas de notificación)
  → Loop de envío (Delay + Telegram Send) × hasta 4 mensajes
  → Actualizar Lead en Airtable  (historial, etapa, perfil)
  → ¿Notificar?                  (IF: [NOTIFICAR_*] tags)
      ↓ Sí
  → Enviar Notificación Telegram al equipo
```

---

## Cómo Usar Este Template

1. **Importar** `WF_AGENTE_TELEGRAM_v1.json` en n8n
2. **Renombrar** el workflow: `[NombreCliente] — Agente Telegram`
3. **Reconectar credenciales** en todos los nodos que lo requieran:
   - `Recibir Mensaje Telegram` → credential del bot del cliente
   - `Buscar Lead en Airtable` / `Crear Lead` / `Actualizar Lead` → base del cliente
   - `Enviar Notificación` → chat ID del canal de notificación del cliente
4. **Conectar el modelo** en el nodo `AI Agent` → Google Gemini o el modelo elegido
5. **Pegar el system prompt** generado con `/generar-system-prompt` en el campo `systemMessage` del nodo AI Agent
6. **Configurar variables de entorno** si aplica (ver sección Variables)

---

## Variables a Personalizar

| Nodo | Campo | Qué cambiar |
|------|-------|-------------|
| `Recibir Mensaje Telegram` | Credential | Bot de Telegram del cliente |
| `Normalizar Payload` | `canal` / `fuente` | Nombre identificador del canal |
| `Buscar Lead en Airtable` | `base` + `table` | Base y tabla Leads del cliente |
| `Crear Lead en Airtable` | `base` + `table` + campos | Misma base; ajustar campos si el schema del cliente difiere |
| `Actualizar Lead en Airtable` | `base` + `table` | Misma base |
| `AI Agent` | `systemMessage` | System prompt generado con `/generar-system-prompt` |
| `Enviar Notificación` | `chatId` | Chat ID del grupo/canal de notificación del cliente |

---

## Etiquetas de Notificación del System Prompt

El nodo `Parsear Respuesta` detecta estas etiquetas en el output del AI Agent para
disparar notificaciones al equipo y actualizar la etapa del pipeline:

| Etiqueta | Significado | Etapa resultante en Airtable |
|----------|-------------|------------------------------|
| `[NOTIFICAR_CIERRE]` | Lead listo para cierre | `ganado` |
| `[NOTIFICAR_AGENDA]` | Solicita llamada/visita | `agenda_solicitada` |
| `[NOTIFICAR_DESCALIFICADO]` | Lead no califica | `descalificado` |
| `[NOTIFICAR_FOLLOWUP]` | Requiere seguimiento | `pendiente_followup` |

Para agregar nuevas etiquetas: modificar el nodo `Parsear Respuesta` y agregar la lógica
en el bloque de `nuevaEtapa`.

---

## Schema Airtable Esperado (Tabla: Leads)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `nombre` | Text | leadIdentifier (ej: `tg_username`) |
| `canal_ingreso` | Text | Canal de origen |
| `fuente` | Text | Fuente específica |
| `historial` | Long text | Historial completo de la conversación |
| `perfil_lead` | Text | Clasificación del lead |
| `etapa_conversion` | Text | Etapa actual en el pipeline |
| `producto_interes` | Text | Producto/servicio consultado |
| `califica` | Text | `pendiente` / `si` / `no` |
| `fecha_primer_contacto` | Date | Fecha de primera interacción |
| `fecha_ultima_interaccion` | Date | Última actualización |

Campos adicionales según el cliente (ej: nombre_real, mail, empresa, telefono) se agregan
al nodo `Crear Lead` y al nodo `Actualizar Lead`.

---

## Extensibilidad: Agregar Tools al AI Agent

El nodo `AI Agent` soporta tools adicionales conectadas por la entrada `tool`. Ejemplos útiles:

- **Buscar en catálogo**: HTTP Request Tool → endpoint de productos
- **Registrar datos del lead**: Airtable Tool → actualización directa desde el agente
- **Consultar calendario**: Google Calendar Tool
- **Enviar link de pago**: HTTP Request Tool

Para agregar: crear el nodo tool correspondiente y conectarlo al AI Agent por la entrada `tool`.
El agente decide cuándo llamarlo automáticamente.

---

## Historial de Versiones

| Versión | Fecha | Cambio |
|---------|-------|--------|
| v1.0 | 2026-04-11 | Template inicial basado en Sistemas & Soluciones |
