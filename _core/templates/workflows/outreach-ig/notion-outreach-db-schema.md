# Notion — DB Outreach SetterPerfecto

> Esquema de la base de datos de Notion que actúa como registro de prospectos de outreach.
> El Agente Outreach IG consulta esta DB para discriminar outreach vs. inbound, personalizar las respuestas y actualizar el estado de cada conversación.

---

## Campos Requeridos por el Agente

| Campo | Tipo Notion | Descripción | Requerido |
|-------|-------------|-------------|-----------|
| `ig_handle` | **Title** | Handle de Instagram sin @ (ej: `coach_fitness_mx`). Es el campo de lookup principal del agente — debe ser el campo Title de la DB. | ✅ Sí |
| `nicho` | **Select** | Nicho del prospecto. Opciones sugeridas: `finanzas`, `fitness`, `coaching`, `ecommerce`, `real_estate`, `marketing`, `negocios`, `otro`. Se usa para personalizar el prompt. | ✅ Sí |
| `estado_outreach` | **Select** | Estado actual en el pipeline. Opciones: `pendiente_contactar` / `contactado` / `respondio` / `en_conversacion` / `calificado` / `llamada_agendada` / `no_interesado`. | ✅ Sí |
| `score_mql` | **Number** | Score de calificación 1-5 del módulo de Prospección. Indica qué tan buen fit es el prospecto para SetterPerfecto. | ✅ Sí |
| `historial` | **Text** (Rich Text) | Historial de conversación acumulado. El agente lee y escribe en este campo en cada interacción. Formato: `[PROSPECTO]: mensaje\n[LA AGENCIA AI]: respuesta`. | ✅ Sí |
| `nombre` | **Text** | Nombre del prospecto (si se tiene). Opcional pero mejora la personalización. | ❌ Opcional |
| `followers` | **Number** | Número de seguidores (viene del módulo de Prospección). | ❌ Opcional |
| `notas` | **Text** | Notas manuales del usuario. No es leído por el agente. | ❌ Opcional |

---

## Variables de Entorno en n8n

```
NOTION_OUTREACH_DB_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
NOTION_API_TOKEN={{NOTION_API_TOKEN}}
```

**Dónde encontrar el Database ID:**
La URL de la DB en Notion es: `https://www.notion.so/[WORKSPACE]/[DATABASE_ID]?v=...`
El DATABASE_ID es el string alfanumérico de 32 caracteres antes del `?v=`.

**Cómo crear el API Token:**
1. Ir a `https://www.notion.so/my-integrations`
2. Crear una nueva integración
3. Copiar el `Internal Integration Token` (comienza con `secret_`)
4. En la DB de Notion: `···` → `Connections` → agregar la integración

---

## Cómo se Alimenta Esta DB

```
1. PROSPECTAR    → la agencia-tools /prospeccion → CSV con handles calificados
                   (campos exportados: ig_handle, nicho, score_mql, followers)
                          ↓
2. IMPORTAR      → usuario importa CSV a esta DB de Notion
                   (Notion tiene import de CSV nativo: ··· → Merge with CSV)
                          ↓
3. CONTACTAR     → usuario envía DM manual desde su cuenta de Instagram
                          ↓
4. REGISTRAR     → usuario actualiza `estado_outreach` → "contactado"
                   (esto le dice al agente que puede tomar el control)
                          ↓
5. RESPONDER     → el agente detecta el reply, lee la DB y responde automáticamente
                   El agente actualiza: `estado_outreach` → "en_conversacion"
                                        `historial` → appends cada mensaje
```

---

## Mapeo de Campos del CSV del Módulo de Prospección

El módulo de Prospección exporta un CSV con 16 columnas. Los campos que van directo a esta DB:

| Campo CSV | Campo Notion | Notas |
|-----------|-------------|-------|
| `Handle` | `ig_handle` (Title) | Sin @ |
| `Nicho` | `nicho` | |
| `Score` | `score_mql` | |
| `Seguidores` | `followers` | |

Los demás campos del CSV (nombre completo, bio, etc.) se pueden importar como campos adicionales opcionales.

---

## Notas de Configuración

- **El campo `ig_handle` DEBE ser el campo Title** (el primero de la DB). El filtro del nodo Notion en n8n busca por `ig_handle|title`. Si usás otro nombre para el campo Title, actualizar el parámetro `key` en el nodo de búsqueda del workflow.

- **El campo `historial` puede crecer mucho** en conversaciones largas. Notion tiene un límite de 2000 caracteres por celda de Rich Text en la API. Si la conversación es larga, considerar truncar el historial a los últimos N mensajes en el Code node del workflow.

- **El campo `estado_outreach`**: el agente solo responde cuando el estado es `contactado`, `respondio`, o `en_conversacion`. Si el estado es `pendiente_contactar`, el agente no actúa (asume que aún no se envió el primer mensaje).
