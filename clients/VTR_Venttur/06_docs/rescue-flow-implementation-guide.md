# Guía de Implementación — Rescate de Agendamiento Incompleto

> **Cliente:** VTR Venttur
> **Actualizada:** 2026-05-26
> **Workflow nuevo:** `wf-rescate-post-link.json`
> **Archivo de mensajes:** `rescue-flow-message-templates.md`

---

## Arquitectura

El trigger del rescate **no viene de ManyChat** — viene de n8n. El agente IA en `wf-venttur-main.json` detecta cuando su respuesta contiene un link de agendamiento y activa la cadena.

```
wf-venttur-main.json
  AI responde con promo.venttur.com/...
  "Envió link?" = YES
  │  ejecuta subworkflow con { id_airtable: telefono, mensaje: texto }
  ▼
wf-actualizar-link-enviado.json  [ya existe — modificar]
  1. Tag Clientify: {programa}_link_enviado
  2. Airtable: Link asesoría enviado = true
  3. Llama wf-seguimiento-agenda.json  ← confirmación (ya existe, no tocar)
  4. [NUEVO] Llama wf-rescate-post-link.json con { telefono }
  │
  ▼
wf-rescate-post-link.json  [CREAR]
  Input: telefono
  │
  ├── Wait 45 min
  ├── Airtable: buscar {Telefono} = telefono
  │   → obtener: Agendan cita, Programa interés, ID Manychat, Nombre
  ├── IF Agendan cita = true → STOP
  ├── Code: armar mensaje Fase 1 + mcBody (parte1=msg, parte2=null, parte3=null)
  ├── IF programa mapeado?
  │   └── NO → addTag RESCATE_PROGRAMA_NO_MAPEADO → STOP
  ├── setCustomFields (batch, JSON.stringify(mcBody))
  ├── sendFlow content20250617172539_850988 ("Enviar mensajes")
  │
  ├── Wait 24 hrs
  ├── Airtable: 2do check (consulta fresca)
  ├── IF Agendan cita = true → STOP
  ├── Code: armar mensaje Fase 2 + mcBody
  ├── setCustomFields (batch, JSON.stringify(mcBody))
  ├── sendFlow content20250617172539_850988
  └── addTag LINK_ABANDONADO_FRIO → FIN
```

**Por qué no hay trigger en ManyChat:** el link lo envía el agente IA desde n8n (no desde un flujo ManyChat). `wf-venttur-main.json` detecta `promo.venttur.com/` en el output del agente y activa la cadena. No hay que agregar External Requests ni modificar flujos de Seguimientos en ManyChat.

**subscriber_id:** no se pasa desde ManyChat. Se obtiene de Airtable campo `ID Manychat` al hacer el lookup por teléfono.

---

## Paso 0 — Pre-requisitos

- [ ] `MANYCHAT_API_KEY` disponible como variable de entorno en n8n
- [ ] Acceso al workflow `wf-actualizar-link-enviado.json` en n8n para agregar el Execute Workflow

> **Infraestructura ya existente — no crear:**
> Custom fields `parte1` [13337279], `parte2` [13337280], `parte3` [13337281] ✅
> Tags `LINK_ABANDONADO_FRIO` [87501917] y `RESCATE_PROGRAMA_NO_MAPEADO` [87501935] ✅
> Flow "Enviar mensajes" `content20250617172539_850988` ✅

---

## Paso 1 — Desactivar el rescate antiguo en ManyChat

Abrir ManyChat → carpeta **Reactivación** → flow **"Rescate Post-Link"**
(`content20260513183625_644743`)

Desactivarlo (no eliminar). Este flow es el rescate genérico actual — al activar el nuevo en n8n, este quedaría duplicado.

No hay que tocar ningún otro flujo de ManyChat.

---

## Paso 2 — Modificar `wf-actualizar-link-enviado.json`

> Hacer este paso **después** de importar el workflow del Paso 3 y obtener su n8n ID.

Agregar un nodo **Execute Workflow** al final del workflow (después del nodo "Ejecutar seguimiento agendamiento" existente o en paralelo con él):

| Campo | Valor |
|-------|-------|
| Workflow | Seleccionar "Rescate Post-Link - Venttur" (el recién importado) |
| Mode | Run Once for Each Item |
| Input campo `telefono` | `={{ $('When Executed by Another Workflow').item.json.id_airtable }}` |

> El nodo puede correr en paralelo con "Ejecutar seguimiento agendamiento" — ambos reciben el mismo teléfono y hacen cosas distintas (uno confirma si agendaron, el otro rescata si no).

---

## Paso 3 — Importar workflow `wf-rescate-post-link.json`

El JSON listo para importar está en `clients/VTR_Venttur/03_workflows/wf-rescate-post-link.json`.

En n8n: **Workflows → Import from file** → seleccionar ese archivo. Después de importar, anotar el ID del workflow que n8n asigna (visible en la URL: `/workflow/XXXXXXXX`). Ese ID es el que se usa en Paso 2 para el nodo Execute Workflow.

---

### Nodo 1 — When Executed by Another Workflow (trigger)

| Campo | Valor |
|-------|-------|
| Type | Execute Workflow Trigger |
| Input | `telefono` (string, ej: `"59899999999"`) |

---

### Nodo 2 — Wait: 45 minutos

| Campo | Valor |
|-------|-------|
| Type | Wait |
| Resume | After time interval |
| Amount | 45 |
| Unit | Minutes |

---

### Nodo 3 — Airtable: 1er check

| Campo | Valor |
|-------|-------|
| Type | Airtable — Search Records |
| Credentials | `[N8N_CREDENTIAL_ID]` |
| Base | `[AIRTABLE_BASE_ID]` |
| Table | `[AIRTABLE_TABLE_ID]` (Leads) |
| Filter formula | `{Telefono} = '{{ $('When Executed by Another Workflow').item.json.telefono }}'` |
| Fields | `Agendan cita`, `Programa interés`, `ID Manychat`, `Nombre` |
| Max records | 1 |

---

### Nodo 4 — IF: ¿ya agendó? (1er check)

| Campo | Valor |
|-------|-------|
| Condition | `{{ $json['Agendan cita'] }}` **is** `true` (boolean) |
| TRUE branch | → Stop (agendó antes de los 45 min) |
| FALSE branch | → continuar al Nodo 5 |

> **Nota:** Airtable devuelve campos al nivel raíz del JSON (sin wrapper `.fields`) en n8n v2.1 del nodo Airtable.

---

### Nodo 5 — Code: seleccionar mensaje Fase 1

```javascript
const telefono = $('When Executed by Another Workflow').first().json.telefono;
const id_manychat = $('Airtable: 1er check').first().json['ID Manychat'];
const first_name = $('Airtable: 1er check').first().json.Nombre;
const programa = $('Airtable: 1er check').first().json['Programa interés'];

const FASE1 = {
  boarding: `Hola ${first_name}. Noté que solicitaste el enlace para platicar sobre Boarding School, pero el registro quedó pendiente.

Si no encontraste un horario que se ajuste a tu agenda, avísame y reviso disponibilidad manual.

¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/agendar-ema`,

  aa_familia: `Hola ${first_name}. Vi que pediste el enlace para la asesoría de Año Académico, pero la cita quedó en pausa.

Si tuviste problemas con la plataforma o los horarios no te cuadran, escríbeme y lo resolvemos.

¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/AAFamilia-Agendar`,

  summer: `Hola ${first_name}. Solicitaste el acceso a la agenda para Summer Camp hace un momento.

Si el calendario no te mostró horarios convenientes, dímelo y buscamos un espacio que te funcione.

¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/SummerCamp-Agendar`,

  pathway: `Hola ${first_name}. Noté que pediste el enlace para la sesión de Pathway en Alemania.

Si la plataforma te dio error o no encontraste disponibilidad, avísame por aquí para coordinarlo directo.

¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/PW_Alemania_Agendar`,

  gap_year: `Hola ${first_name}. Solicitaste el enlace de asesoría para tu Gap Year en Australia.

Si no encontraste un hueco en la agenda o se cerró el enlace, escríbeme y te ayudo a reservarlo.

¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/Estudiar-y-Trabajar-en-Australia`,
};

let parte1 = null;

if (programa.includes('Boarding')) parte1 = FASE1.boarding;
else if (programa.includes('AA Familiar') || programa.includes('Francia')) parte1 = FASE1.aa_familia;
else if (programa.includes('Summer Camp')) parte1 = FASE1.summer;
else if (programa.includes('Pathway')) parte1 = FASE1.pathway;
else if (programa.includes('Gap Year')) parte1 = FASE1.gap_year;

// mcBody para setCustomFields batch — parte2/parte3 en null para limpiarlos
const mcBody = {
  subscriber_id: Number(id_manychat),
  fields: [
    { field_id: 13337279, field_value: parte1 },
    { field_id: 13337280, field_value: null },
    { field_id: 13337281, field_value: null }
  ]
};

return [{ json: { matched: !!parte1, id_manychat, telefono, mcBody } }];
```

> **Por qué `mcBody` se arma en el Code node:** ManyChat API rechaza `""` (string vacío) en `field_value` con error "Field with invalid value". Para limpiar parte2/parte3 hay que enviar JSON `null`. Pero la interpolación de templates n8n (`{{ expr }}`) convierte `null` a string `"null"`. Solución: armar el body completo en el Code node como objeto JS (que preserva `null` real) y serializarlo en el HTTP node con `JSON.stringify()`.

---

### Nodo 6 — IF: ¿programa mapeado?

| Campo | Valor |
|-------|-------|
| Condition | `{{ $json.matched }}` **is** `true` |
| TRUE branch | → continuar al Nodo 7 |
| FALSE branch | → Nodo 6b: addTag RESCATE_PROGRAMA_NO_MAPEADO → Stop |

**Nodo 6b — HTTP Request: addTag RESCATE_PROGRAMA_NO_MAPEADO**

| Campo | Valor |
|-------|-------|
| Method | POST |
| URL | `https://api.manychat.com/fb/subscriber/addTag` |
| Header | `Authorization: Bearer {{ $env.MANYCHAT_API_KEY }}` |
| Body (JSON) | `{ "subscriber_id": {{ $('Code: Fase 1').first().json.id_manychat }}, "tag_id": 87501935 }` |

---

### Nodo 7 — Set Custom Fields: Fase 1

Un solo nodo HTTP que setea los 3 custom fields via el endpoint batch `setCustomFields`.

| Campo | Valor |
|-------|-------|
| Method | POST |
| URL | `https://api.manychat.com/fb/subscriber/setCustomFields` |
| Header | `Authorization: Bearer {{ $env.MANYCHAT_API_KEY }}` |
| Body (JSON) | `={{ JSON.stringify($('Code: Fase 1').first().json.mcBody) }}` |

> **Importante:** el body NO se escribe como template interpolado — se usa `JSON.stringify()` sobre el objeto `mcBody` construido en el Code node. Esto preserva los `null` reales para parte2/parte3 (ver nota en Nodo 5).

El body resultante en runtime es:
```json
{
  "subscriber_id": 12345678,
  "fields": [
    { "field_id": 13337279, "field_value": "Hola Nombre. Noté que..." },
    { "field_id": 13337280, "field_value": null },
    { "field_id": 13337281, "field_value": null }
  ]
}
```

---

### Nodo 8 — HTTP Request: sendFlow Fase 1

| Campo | Valor |
|-------|-------|
| Method | POST |
| URL | `https://api.manychat.com/fb/sending/sendFlow` |
| Header | `Authorization: Bearer {{ $env.MANYCHAT_API_KEY }}` |
| Body (JSON) | `{ "subscriber_id": "{{ $('Code: Fase 1').first().json.id_manychat }}", "flow_ns": "content20250617172539_850988" }` |

---

### Nodo 9 — Wait: 24 horas

| Campo | Valor |
|-------|-------|
| Type | Wait |
| Resume | After time interval |
| Amount | 24 |
| Unit | Hours |

---

### Nodo 10 — Airtable: 2do check

Configuración **idéntica** al Nodo 3. Consulta fresca para capturar si el lead agendó después de Fase 1.

---

### Nodo 11 — IF: ¿ya agendó? (2do check)

| Campo | Valor |
|-------|-------|
| Condition | `{{ $json['Agendan cita'] }}` **is** `true` (boolean) |
| TRUE branch | → Stop (agendó tras Fase 1) |
| FALSE branch | → continuar al Nodo 12 |

---

### Nodo 12 — Code: seleccionar mensaje Fase 2

```javascript
const record = $('Airtable: 2do check').first().json.fields || {};
const id_manychat = record['ID Manychat'] ? String(record['ID Manychat']) : $('Code: Fase 1').first().json.id_manychat;
const first_name = record['Nombre'] || '';
const programa = record['Programa interés'] || '';

const FASE2 = {
  boarding: `Hola ${first_name} 👋. Noté que tu registro quedó en pausa ayer.

Mandar a un hijo a un internado es un gran paso y es súper normal dudar si 'ya está listo'. En la sesión validamos su perfil y vemos los pocos cupos que quedan para la temporada.

¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/agendar-ema`,

  aa_familia: `Hola ${first_name} 👋. Seguro entre tantas cosas ayer se te pasó agendar.

La mayor preocupación de los papás siempre es: '¿Se adaptará bien si no domina el idioma?'. En la llamada armamos un plan de inmersión seguro para evitar frustraciones.

¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/AAFamilia-Agendar`,

  summer: `Hola ${first_name} 👋. Vi que tu registro quedó a medias ayer.

Es súper común dudar si un Summer Camp será seguro y realmente formativo, o solo un paseo. En 45 min aterrizamos la opción ideal antes de que cierren los grupos de temporada.

¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/SummerCamp-Agendar`,

  pathway: `Hola ${first_name} 👋. Noté que pausaste el registro ayer. Muchos creen que necesitan alemán perfecto para empezar, pero el secreto es armar la ruta ya mismo para no perder la admisión en las universidades públicas. En 45 min les damos el mapa completo. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/PW_Alemania_Agendar`,

  gap_year: `Hola ${first_name} 👋. Vi que dejaste el registro a medias.

Irse a Australia es un gran paso y la mayor duda siempre es: '¿Encontrará trabajo rápido?'. El secreto está en irse con una ruta clara y no improvisar. Nos quedan pocos espacios esta semana.

¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/Estudiar-y-Trabajar-en-Australia`,
};

let parte1 = null;

if (programa.includes('Boarding')) parte1 = FASE2.boarding;
else if (programa.includes('AA Familiar') || programa.includes('Francia')) parte1 = FASE2.aa_familia;
else if (programa.includes('Summer Camp')) parte1 = FASE2.summer;
else if (programa.includes('Pathway')) parte1 = FASE2.pathway;
else if (programa.includes('Gap Year')) parte1 = FASE2.gap_year;

const mcBody = {
  subscriber_id: Number(id_manychat),
  fields: [
    { field_id: 13337279, field_value: parte1 },
    { field_id: 13337280, field_value: null },
    { field_id: 13337281, field_value: null }
  ]
};

return [{ json: { id_manychat, mcBody } }];
```

> **Nota sobre `.fields`:** En producción, Code: Fase 2 accede a los datos del 2do check via `$json.fields['...']` mientras que Code: Fase 1 accede directo via `$json['...']`. Ambos patrones funcionan — depende de cómo n8n formatea la respuesta de Airtable en cada instancia. El fallback `|| {}` en Fase 2 protege contra ambos casos.

---

### Nodo 13 — Set Custom Fields: Fase 2

Idéntico al Nodo 7, referenciando `$('Code: Fase 2')` en lugar de `$('Code: Fase 1')`:

| Campo | Valor |
|-------|-------|
| Method | POST |
| URL | `https://api.manychat.com/fb/subscriber/setCustomFields` |
| Header | `Authorization: Bearer {{ $env.MANYCHAT_API_KEY }}` |
| Body (JSON) | `={{ JSON.stringify($('Code: Fase 2').first().json.mcBody) }}` |

---

### Nodo 14 — HTTP Request: sendFlow Fase 2

Idéntico al Nodo 8, con `subscriber_id` de `$('Code: Fase 2').first().json.id_manychat`.

---

### Nodo 15 — HTTP Request: addTag LINK_ABANDONADO_FRIO

| Campo | Valor |
|-------|-------|
| Method | POST |
| URL | `https://api.manychat.com/fb/subscriber/addTag` |
| Header | `Authorization: Bearer {{ $env.MANYCHAT_API_KEY }}` |
| Body (JSON) | `{ "subscriber_id": {{ $('Code: Fase 2').first().json.id_manychat }}, "tag_id": 87501917 }` |

Después de este nodo: fin del workflow.

---

## Paso 4 — Testing

Reducir los Wait temporalmente:
- Nodo 2: 45 min → **1 min**
- Nodo 11: 24 hrs → **2 min**

| # | Test | Setup | Resultado esperado |
|---|------|-------|--------------------|
| 1 | Trigger manual desde `wf-actualizar-link-enviado` | Ejecutar `wf-actualizar-link-enviado` con `id_airtable` = teléfono real, `mensaje` con un link de prueba | Ejecución de `wf-rescate-post-link` visible en n8n |
| 2 | Airtable lookup funciona | Lead de prueba con `Telefono` = teléfono sin `+`, `Agendan cita` = false, `Programa interés` = "Boarding IA" | Nodo 3 devuelve campos correctos incluyendo `ID Manychat` |
| 3 | Stop por agendamiento previo | Lead con `Agendan cita` = true antes del Wait | Flujo se detiene en Nodo 4 |
| 4 | Routing Fase 1 (×5 programas) | Cambiar `Programa interés` en Airtable para cada programa | `parte1` seteado con el mensaje correcto del programa |
| 5 | Mensaje llega por WhatsApp | Lead real, verificar que el flow "Enviar mensajes" envía `parte1` | Lead recibe el mensaje de rescate |
| 6 | Stop entre fases | Dejar que Wait reducido termine, luego setear `Agendan cita` = true antes del 2do Wait | Fase 2 no se envía |
| 7 | Routing Fase 2 (×5 programas) | Esperar el Wait reducido sin agendar | `parte1` seteado con el mensaje correcto de Fase 2 |
| 8 | Tag cierre | Completar ambas fases sin agendar | Tag `LINK_ABANDONADO_FRIO` aplicado en ManyChat |
| 9 | Programa desconocido | `Programa interés` = "No definido" | Tag `RESCATE_PROGRAMA_NO_MAPEADO`, sin mensaje |
| 10 | Flujo completo end-to-end | Enviar un link desde el bot (en conversación real o forzado con Postman al webhook de `wf-venttur-main`) | Cadena completa se activa automáticamente |

Restaurar los Wait reales antes de activar en producción.

---

## Referencia — ManyChat API v2: quirks descubiertos durante testing

| Endpoint | Quirk | Solución |
|----------|-------|----------|
| `addTag` | Requiere `tag_id` (numérico), NO `tag_name`. Con `tag_name` da "tag_id cannot be blank" | Usar `"tag_id": 87501935` |
| `setCustomFields` | Rechaza `""` (string vacío) en `field_value` con "Field with invalid value" | Enviar JSON `null` para limpiar un campo |
| `setCustomFields` | Acepta `field_id` (numérico) y `field_name` (string), pero `field_id` es más confiable | Usar `field_id` siempre |
| n8n + ManyChat | Templates n8n (`{{ expr }}`) convierten `null` JS a string `"null"` — ManyChat lo guarda como texto literal | Armar body completo en Code node como objeto JS, serializar con `JSON.stringify()` en el HTTP node |

---

## Referencia — Programas mapeados

| Valor en Airtable | Condición en Code node | Fase 1 y 2 |
|-------------------|------------------------|------------|
| `Boarding IA` | `includes('Boarding')` | ✅ |
| `AA Familiar IA` | `includes('AA Familiar')` | ✅ |
| `Francia IA` | `includes('Francia')` | ✅ (mismos mensajes que AA Familiar) |
| `Summer Camp IA` | `includes('Summer Camp')` | ✅ |
| `Pathway IA` | `includes('Pathway')` | ✅ |
| `Gap Year IA` | `includes('Gap Year')` | ✅ |
| `No definido` | — | → tag RESCATE_PROGRAMA_NO_MAPEADO |
| `Automatización - Comentarios` | — | → tag RESCATE_PROGRAMA_NO_MAPEADO |

> Valores confirmados en Airtable (2026-05-26). Los 8 valores activos están cubiertos por la lógica actual sin necesidad de cambios.

---

## Referencia — Infraestructura ManyChat (existente al 2026-05-13)

### Custom fields relevantes

| ID | Nombre | Tipo |
|----|--------|------|
| 13337279 | `parte1` | text |
| 13337280 | `parte2` | text |
| 13337281 | `parte3` | text |

### Tags relevantes

| ID | Nombre |
|----|--------|
| 87501917 | `LINK_ABANDONADO_FRIO` |
| 87501935 | `RESCATE_PROGRAMA_NO_MAPEADO` |

### Flows relevantes

| ns | Nombre | Rol |
|----|--------|-----|
| `content20250617172539_850988` | Enviar mensajes | Envía parte1/parte2/parte3 (carpeta: Agente IA Principal) |
| `content20260513183625_644743` | Rescate Post-Link | Rescate ANTIGUO — desactivar en Paso 1 (carpeta: Reactivación) |

---

## Referencia — Consideraciones operativas

- **Ventana 24 hrs WhatsApp:** Fase 1 (45 min) está dentro de la ventana. Fase 2 (~25 hrs desde la última interacción del lead) puede estar fuera si el lead no respondió a Fase 1. n8n ejecutará igual; si ManyChat no puede entregar, lo registrará como error. Aceptable para v1.
- **Fuente de `Agendan cita`:** lo setea `wf-confirmacion-agenda.json` al detectar un evento nuevo en los calendarios de Diego/Andres/Rodrigo en Google Calendar. Es la fuente de verdad.
- **Fuente de `ID Manychat`:** Airtable campo `ID Manychat`. Se popula cuando el lead interactúa con el bot (el main workflow crea el registro). Si está vacío, el rescue no podrá enviar el mensaje por ManyChat — el nodo fallará. Monitorear en las primeras ejecuciones.
- **Nuevo programa:** agregar entrada en `FASE1` y `FASE2` del Code node + condición `includes()` correspondiente. Actualizar tabla de programas mapeados de esta guía.
- **Futuro — mensajes desde Airtable:** crear tabla `Mensajes Rescate` en Airtable con columnas `programa`, `fase`, `texto`. Reemplazar los objetos `FASE1`/`FASE2` por una consulta Airtable al inicio del workflow.
