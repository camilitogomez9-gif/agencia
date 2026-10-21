# Mapa Funcional — Sistema actual Happy Flops (HPF)

> **Etapa 1 — Deducción de lógica.** Documento maestro reconstruido a partir de:
> - `happyflops-main-v2.json` (225 nodos)
> - 5 sub-workflows
> - Export Kommo (`kommo_export.json`, 13 pipelines)
> - Catálogo Airtable (6 tablas)
> - 7 system prompts LangChain
> - Conversation samples (golden tests)

---

## 0. Cómo leer este documento

Cada sección reconstruye una pieza del sistema **desde el comportamiento externo** (lo que el lead ve) hacia adentro (cómo está implementado). Cuando hay decisiones críticas tomadas en n8n con IF/Switch/Code, se citan los nombres exactos de nodos para trazabilidad.

Los identificadores hardcodeados que aparecen en el sistema:

| ID | Significado | Origen |
|----|------------|--------|
| `11622596` | Pipeline "IA" — único pipeline procesado por el agente | Kommo |
| `89263340..89263344` | Incoming leads → ETAPA 1 | Kommo |
| `93616832` | ETAPA 2 (imagen principal enviada) | Kommo |
| `93616836` | ETAPA 3 (productos mostrados) | Kommo |
| `93616840` | ETAPA 4 (cotización/recolección) | Kommo |
| `89263348` | COTIZACION | Kommo |
| `91266100` | atencion personalizada | Kommo |
| `91450360` | confirmar pago | Kommo |
| `100395519` | en produccion | Kommo |
| `100395523` | pago liquidacion | Kommo |
| `89263760..91622920` | r1..r5 sin/con info / ap | Kommo (sub-pipeline de seguimientos) |
| `142` / `143` | Logrado con éxito / Ventas Perdidos | Kommo |
| `appMHtUN9zKYODufC` | Base Airtable "Productos \| Happy Flops" | Airtable |
| `tbl8oRU3ApdEuLcgs` | Tabla "Foto Vacaciones" / mensajes fuera de horario | Airtable |
| `tblsDWUQbfANNWMeK` | Tabla "Imagen Principal" | Airtable |
| `-4925599962` | Chat Telegram operativo (notificaciones equipo) | Telegram |

---

## 1. Visión externa del sistema

Happy Flops opera un agente conversacional llamado **Rebeca** (asistente virtual) que atiende DMs entrantes en WhatsApp. Funciona dentro del CRM Kommo: los mensajes entran y salen vía Kommo (subdomain `happyflopss.kommo.com`), Kommo dispara webhooks a n8n cada vez que llega un mensaje al lead, y n8n responde mediante dos APIs distintas:

1. **API moderna Kommo v4** — para mover etapas del pipeline (`PATCH /api/v4/leads/{id}`).
2. **API legacy AmoCRM (`amojo.kommo.com/v2`)** — para enviar mensajes (texto, imagen, PDF, audio) a la conversación del lead. Esta es la única vía de envío de contenido conversacional. **No hay envío directo a WhatsApp**: todo pasa por Kommo.

El agente sigue un **proceso fijo de 4 pasos** ("steps") gestionado por un Router que evalúa el estado de la conversación contra la memoria. Cada paso tiene un agente especializado. Cuando el lead avanza, se mueve la etapa Kommo correspondiente. Cuando el lead se queda sin responder, sub-workflows asíncronos disparan recordatorios temporizados.

**Canales:** WhatsApp (canal único confirmado por el cliente). Los CURLs de Airtable apuntan a `amojo.kommo.com` (la pasarela que Kommo usa para todos los canales — WA es el canal real conectado).

---

## 2. Pipeline activo y entrypoint

### 2.1 Webhook de entrada

- **Nodo:** `New_Message` (`POST /webhook/1bfb19eb-2157-42d0-84d7-23ea334699ec`)
- **Origen:** Kommo dispara este webhook cuando hay un evento `message[add][0]` en la cuenta `happyflopss`.
- **Payload clave:** `body['message[add][0][entity_id]']`, `body['account[subdomain]']`, datos del mensaje (texto / media URL).

### 2.2 Filtros de entrada

Antes de procesar, el sistema chequea:

1. **`If25`**: `entity_id == 8075544` — uso interno (este lead específico parece ser un sandbox o lead-ancla para algunas verificaciones; ambas ramas del IF siguen al mismo nodo `Get_Contact`, así que el IF funciona como un toggle de tracking, no de filtrado).
2. **`Get_Contact` → `Clear_Contact_Data` → `All_Data`**: enriquecen el payload con info del contacto y normalizan los datos del lead (chat_id, contact_id, entity_id, account_link_self, numero_telefono).
3. **`Get_Entity`**: trae el lead completo desde Kommo v4 — su `status_id` actual.
4. **`No es IA`** (`if data notContains 11622596`): si el lead **NO** está en el pipeline IA (11622596) o un status descendiente, **no procesa con el agente**. Esto significa que los otros 12 pipelines (SANDALIAS BODAS, Cilindros, etc.) son **manuales o legacy** y el agente IA **solo opera dentro del pipeline `IA`**.
5. **`If23`** (`data contains 100395519`): si el lead está "en produccion" (post-cotización/diseño aprobado), bifurca a un flujo distinto. Si es imagen, va por `Es PDF?` (manejo de comprobante de pago de liquidación).
6. **`If21` y `If20`**: filtran etapas activas del agente. `89263344` (ETAPA 1) | `93616832` (ETAPA 2) | `93616836` (ETAPA 3) y `91266100` (atencion personalizada) | `92033296` (r1 ap) | `92033300` (r2 ap). Si está en una etapa "ap" (atención personalizada), el agente **no responde** — el humano tomó el caso.

---

## 3. Topología de procesamiento por tipo de input

El nodo `checkType` (Switch) bifurca según el tipo de mensaje:

| Tipo | Detección | Procesamiento |
|------|-----------|---------------|
| **Texto** | branch 0 → `Get_Text` | El texto se asigna a la variable `text` y sigue al pipeline conversacional normal |
| **Audio** | branch 1 → `Get_Audio` | Descarga audio (`GET data_url`) → `transcribe voice` (OpenAI Whisper) → `Get_Text` |
| **Imagen / PDF** | branch 2 → `Es PDF?` | Bifurca: si extensión `.pdf` → notificar Telegram + `Analyze image3`; si NO → `Analyze image3` directo |

### 3.1 Análisis de imágenes

`Analyze image3` (modelo `gpt-4o`) clasifica la imagen como:

- `Sandalias` / `Pantuflas` / `Cilindros` / `Mandiles` / `kit anti cruda` (reconocido como producto)
- `falso` (no clasificable o múltiples productos juntos)
- En paralelo, el sistema verifica si **es comprobante de pago** mediante un segundo prompt (boolean `true/false`).

**Reglas internas del clasificador (system prompt `Analyze image1`):**
- Output exacto: `"Te envio una imagen del producto que quiero: [producto]"` o `"falso"`.
- Si la imagen contiene varios productos mezclados → `falso` (salvo predominio ≥90%).
- Cilindros vs Vasos: cilindros = transparente con tapa; vasos con popote → `falso`.

### 3.2 Bifurcación tras análisis de imagen

```
Analyze image3 → Es Pago?
  ├── true  → En prod? (¿lead está en 100395519?)
  │            ├── sí  → PAGO_LIQUIDACION (mover a 100395523) + Telegram "captura de pago liquidación"
  │            └── no  → Confirmar Pago (mover a 91450360) + Telegram "captura de pago"
  └── false → "Es producto?" (¿el producto detectado != "falso"?)
              ├── sí  → AI Agent Recolector1 (atiende como input "Te envio una imagen..." en step_4)
              └── no  → Telegram "imagen no categorizable" + ATENCION_PERSONALIZADA4 (mueve a 91266100)
```

---

## 4. Anti-ráfaga (debouncing) y horario laboral

### 4.1 Anti-ráfaga (15s / 50s)

El sistema **acumula mensajes** del lead durante una ventana de espera para evitar responder pieza por pieza si el lead manda varios mensajes seguidos:

```
Get_Text → Guardar (Redis push key=contact_id)
         → Wait_35 (50s)
         → Get_Messages (Redis get)
         → Ultimo? (¿el último guardado coincide con el más reciente del array?)
              ├── sí → Date & Time → Message & Date → continúa
              └── no → No Operation (descarta este turno; ya fue procesado por el último mensaje)
```

Hay **dos rutas paralelas con esta lógica**:
- Una usa key=`contact_id` con wait de 50s (`Wait_35`)
- Otra usa key=`numero_telefono` con wait de 15s (`Wait_15s`) — esta segunda es para procesar imágenes (la branch que viene de `Borrar almacenamiento1 → Memory_ID1 → Wait_15s`).

### 4.2 Horario laboral

Los nodos `Code6/7/10/11/12` calculan `isWithinBusinessHoursMx` en zona horaria `America/Mexico_City`. Los IF subsiguientes (`If10/11/18/19/22`) bifurcan:

- **Dentro de horario:** procesa normalmente, hace `actualizar` (PATCH legacy) y envía mensaje (`Envio Mensaje`).
- **Fuera de horario:** envía un mensaje distinto vía `Envio Mensaje` (con bot_id de salesbot diferente) — probablemente el "Foto Vacaciones" de Airtable que dice *"Gracias por tu pago, lo recibimos. Estamos fuera de horario por receso, lo confirmaremos a la brevedad."*

Horario laboral declarado en system prompt: **L-V 9:00–17:30 (México)**.

---

## 5. Detección de "lead nuevo" vs "interacción existente"

### 5.1 GET_PREVIOUS_INTERACTION → Exist_Interaction?

Después de `Memory_ID` (set `id` y `window_length` para LangChain Memory), el sistema:

1. Hace una query Postgres a `n8n_chat_histories` para traer el último mensaje AI guardado para este `session_id`.
2. `Exist_Interaction?` verifica si `$json?.message?.content` no existe.
3. Bifurca:
   - **Lead nuevo** (`branch 0`) → `AI Agent Starter` (envía el saludo de bienvenida)
   - **Lead con historial** (`branch 1`) → `AI Agent` (Router maestro decide step)

Esta es la **lógica de primera vs reincidente**: el Starter solo se activa la primera vez.

### 5.2 Switch1 después del Router

El `AI Agent` (Router maestro) emite `{"output":{"step":"step_N"}}`. El nodo `Switch1` despacha:

| Branch | Step | Agente despachado |
|--------|------|-------------------|
| 0 | `step_1` | `AI Agent Starter` (saludo) |
| 1 | `step_2` | `AI Agent Main Image` (imagen principal del evento + promo) |
| 2 | `step_3` | `GET_LAST_INTERACTION` → `AI Agent Products` (info productos específicos) |
| 3 | `step_4` | `AI Agent Recolector` (cotización, datos, cierre) |

> Observación: `step_1` puede emitirse después del lead-nuevo (es un fallback explícito si el router decide que no se identificó evento, aunque ya haya historia).

---

## 6. Los 7 componentes LLM del sistema

### 6.1 AI Agent (Router maestro)

- **Modelo:** OpenAI Chat Model (configurado por nodo, sin override visible)
- **Memoria:** Postgres Chat Memory (mismo session_id que los demás agentes)
- **Tools:** ninguna (solo retorna JSON)
- **Output Parser:** Structured Output Parser (`{"step":"step_N"}`)
- **Function:** Decide step en base a memoria + último mensaje. Reglas detalladas en `02_intents.md` y system prompt embebido (357 líneas).

**Restricción CRÍTICA del prompt:** "Si respondes algo que no es el JSON estructurado: `{step:step_<number>}`, te mato."

### 6.2 AI Agent Starter

- **Cuándo:** Lead nuevo (no existe interacción previa) o Router devuelve `step_1`.
- **Función:** Emite el saludo. **Mensaje hardcodeado, prohibido modificar:**
  > *"Hola! gracias por escribir a Happy Flops, me llamo Rebeca soy un asistente virtual, yo le estaré atendiendo con gusto ☺️🙋‍♀  Me podría decir de que es su evento? 🤵👰 - Boda  🎂🥳 - XV Años  👼🏢 - Otros"*

- **Particularidad:** Después del agente, n8n llama a sub-workflow `Seg. Rebeca` (timer de re-engagement) y luego al check `If24` (¿el output contiene `👼🏢`? → si sí, divide el mensaje en 3 partes: `Saludo PTE 1` → wait 2s → `Saludo PTE 2` → wait 2s → `Saludo PTE 3`). Si NO contiene el emoji, despacha a `Message a model1` (formateo distinto).

### 6.3 AI Agent Main Image

- **Cuándo:** Router devuelve `step_2`.
- **Función:** Identifica el evento (Boda / XV / Otros) tolerando errores ortográficos. Retorna:
  ```json
  {
    "evento": "<Boda|XV|Otros>",
    "texto_dinamico": "Qué padre! 😊  🎉 *¡SEMANA LOCA DE PROMOS!...*"
  }
  ```
- **Output flow:** `Formula` (calcula filtro Airtable) → `Search_Main_Image` (Airtable tabla `Imagen Principal`) → `Envio Mensaje8` (envía imagen + texto).
- **Side effect:** En paralelo, dispara `Detect_Evento → Execute Workflow2` (Seg. Imagen sub-workflow), que mueve a ETAPA 2 (93616832) y arma timers de seguimiento por imagen.

**Reglas críticas del prompt:**
- "bodas de oro / bodas de plata" → evento = `Boda` (NO Otros).
- Output vacío está prohibido.
- Mensaje promo es FIJO, no se modifica.

### 6.4 AI Agent Products

- **Cuándo:** Router devuelve `step_3` (lead menciona productos).
- **Función:** Identifica productos del catálogo solicitados, retorna:
  ```json
  {
    "evento": "<Boda|XV|Otros>",
    "subcategoria": "<Producto Principal|Accesorios>",
    "productos": ["sandalias","cilindros","anticrudas",...],
    "texto_dinamico": "<pregunta de cantidad+CP, o vacío si subcategoria=Accesorios>"
  }
  ```
- **Output flow:** `Is_Products_Empty` (¿array productos no vacío?) → si sí, `Return_Formula` → `Search_Products` (Airtable Boda/XV/Otros) → `Loop Over Items` → por cada producto, `Wait3` → `Envio Mensaje7` (envía ficha producto). Si vacío, salta a `Message a model` → `Data` → `Detect_Evento`.
- **Restricciones de prompt:**
  - Mínimo 1 producto en el array.
  - Si subcategoria=Accesorios, NO mandar mensaje "le interesa sumarlos a la cotización" (los accesorios van incluidos).
  - "costalitos/costal" → kit anticruda; "bolsa/bolsita" → otro producto (shein).
  - Sandalias = solo mujeres, jamás ofrecer para varones.
  - Si el agente está respondiendo upsell, identificar producto sugerido en `{{ $json.message.content }}` (memoria) y mandar el correcto.

### 6.5 AI Agent Recolector (entrada texto)

- **Cuándo:** Router devuelve `step_4` (cotización, recolección, cierre).
- **Modelo principal:** OpenAI Chat Model (gpt-4.1-mini en otros lugares; aquí no override visible)
- **Tools disponibles:**
  - **`CALCULADORA`** (`lc.toolWorkflow`): subworkflow externo que recibe variable `cuentas` con multiplicaciones (ej: `"75 x 0.15, 50 x 0.15"`) y devuelve costo de envío en pesos mexicanos.
  - **`ATENCION_PERSONALIZADA`** (`lc.toolWorkflow`): mueve el lead a etapa 91266100 (atencion personalizada) + notifica Telegram. Se invoca cuando el agente no puede resolver (diseño personalizado, queja, post-venta, fecha < 15 días, ambigüedad).
  - **`Think`** (`lc.toolThink`): scratchpad para razonamiento del agente.
- **Output Parser:** Auto-fixing Output Parser (corrige JSON malformado).

**Función:** vendedor completo. Cotiza, recolecta datos, gestiona cierre, hace upsell. Reglas detalladas en `05_reglas_negocio.md`.

### 6.6 AI Agent Recolector1 (entrada imagen)

- **Cuándo:** Lead envió imagen clasificada como producto (no es comprobante).
- **Función:** Idéntica al Recolector pero recibe input formateado como `"Te envio una imagen del producto que quiero: [producto]"`.
- **Comportamiento:** Reconoce ese mensaje y responde elogiando el diseño + invitando a continuar el proceso. Tiene los mismos tools (`CALCULADORA1`, `ATENCION_PERSONALIZADA6`, `Think1`).

### 6.7 Analyze image (gpt-4o, clasificador)

- **Cuándo:** Lead envía imagen (no PDF).
- **Función:** Clasifica imagen → uno de 5 productos o `falso`. (Detalles en sección 3.1).

### 6.8 Necesita Respuesta Especial / Message a model / Formatear mensaje1

- **Necesita Respuesta Especial** (`lc.openAi gpt-5-mini`): meta-evaluador. Recibe el output del Recolector y decide si requiere envío de adjunto. Output → `If1`: si `response == "sí"` → reanaliza con AI Agent Recolector con flag de especial.
- **Message a model / Message a model1** (`gpt-4.1-mini`): formateadores. Toman texto largo y lo dividen en `parte1`, `parte2`, `parte3` para enviar como múltiples mensajes con waits intermedios (efecto humano).
- **Formatear mensaje1**: variante para la rama de imagen.

---

## 7. Mecánica de envío de mensajes

El sistema usa **dos canales paralelos** para enviar contenido al lead, ambos a través de Kommo/AmoCRM:

### 7.1 Canal A: salesbot legacy AmoCRM

- **Endpoint:** `POST https://happyflopss.amocrm.com/api/v2/salesbot/run`
- **Cantidad:** ~30 nodos `Envio Mensaje*` en main + más en sub-workflows.
- **Cómo funciona:** dispara un salesbot pre-configurado en Kommo (cada salesbot tiene un `bot_id` único; ej: `60810`, `60814`, `60816`, etc. visibles en los CSVs Airtable). El salesbot envía el mensaje + adjunto (imagen/PDF) al chat del lead. El contenido del mensaje está **dentro del salesbot**, no en n8n.
- **Cuándo se usa:** envíos pre-configurados desde Airtable. Cada producto en Airtable tiene un `bot_id` que apunta a un salesbot que envía la imagen + texto del producto.

### 7.2 Canal B: sendMessage directo (amojo)

- **Endpoint:** `POST https://amojo.kommo.com/v2/{chat_id}/sendMessage`
- **Nodo único:** `Send_Attachment6`
- **Cómo funciona:** envía mensaje + attachment (imagen) directamente al chat. Necesita un token de sesión (`Get token25` → `POST /ajax/v1/chats/session`).
- **Cuándo se usa:** parece ser fallback / casos específicos (Foto Vacaciones según observación de `Search_Main_Image1` con `tbl8oRU3ApdEuLcgs`).

### 7.3 Construcción del CURL desde Airtable

Los CURLs en las tablas Airtable son **plantillas**. El `Code3` y `Code5/9` reciben el `curl` de Airtable y lo modifican en runtime:

```js
// Ejemplo de Code5 (extracto inferido)
const curl = `curl 'https://amojo.kommo.com/v2/8d.../sendMessage?stand=v16' ...`;
// ... reemplaza chat_id, recipient_id, contact_id, entity_id por los del lead actual
// ... ejecuta la request
```

**Conclusión:** los CURLs hardcodeados en Airtable (con IDs de contactos de prueba) se reescriben dinámicamente. Los IDs reales en cada envío vienen de `All_Data` (datos del lead actual extraídos del webhook).

### 7.4 Movimiento de etapas Kommo

- **Endpoint:** `PATCH https://happyflopss.kommo.com/api/v4/leads/{entity_id}` (moderna)
- **Endpoint legacy paralelo:** `PATCH https://happyflopss.amocrm.com/api/v4/leads/{entity_id}` (los nodos `actualizar*` lo usan; aparentemente AmoCRM y Kommo son la misma cuenta con dos URLs alternativas — `amocrm.com` es el dominio histórico, `kommo.com` es el rebrand. Mismo backend.)
- **Operación:** envía `{"status_id": <ID>, "pipeline_id": 11622596}` para mover la etapa.

Hay nodos específicos por etapa-destino:
- `ATENCION_PERSONALIZADA1`, `ATENCION_PERSONALIZADA4` → mueve a 91266100
- `Confirmar Pago`, `Confirmar Pago1`, `Confirmar pago` → mueve a 91450360 (3 nodos duplicados — **redundancia**)
- `PAGO_LIQUIDACION` → mueve a 100395523
- ETAPA 2 (sub-workflow Imagen) → 93616832
- ETAPA 3 (sub-workflows Cotización y 7pasos) → 93616836
- R1 SIN INFO / R1 CON INFO / PERDIDOS1 → r1 sin info / r1 con info / 143

---

## 8. Sub-workflows de seguimiento

Los 4 sub-workflows asíncronos (Rebeca / Imagen / Cotización / 7 pasos) implementan **timers de re-engagement**. Cada uno se invoca desde el main workflow después de momentos clave y queda corriendo en paralelo, despertando a intervalos para:

1. Hacer query Postgres al `n8n_chat_histories` y obtener el último mensaje AI.
2. Verificar si ese mensaje contiene un patrón específico (texto del paso anterior).
3. Verificar el `status_id` actual del lead.
4. Si lead respondió o avanzó → no hace nada (NoOp).
5. Si lead no respondió → enviar mensaje de re-engagement (salesbot run con bot_id específico) + actualizar etapa Kommo.
6. INSERT en Postgres (tabla custom) para tracking del seguimiento.

### 8.1 Seg. Rebeca

- **Disparado por:** `AI Agent Starter` cuando se manda el saludo (lead nuevo).
- **Timeline:** 1h → 3h → 24h → (extra)
- **Detecciones por nivel:**
  - 1h: ¿último mensaje AI contiene `"gracias por escribir a Happy Flops, me l..."`? → si lead no avanzó, enviar PTE 1 (recordar elegir evento) + INSERT seguimiento.
  - 3h: ¿contiene `"sigues por aquí?"`? → si no avanzó, enviar PTE 2.
  - X (¿4h?): ¿contiene `"Cuéntame, es para boda, XV años u otro e..."`? → si no avanzó, enviar PTE 3.
  - 24h: ¿contiene `"no quiero que se te pase la oportunidad..."`? → si no avanzó, mover a **Ventas Perdidos (143)** (`PERDIDOS1`).
- **Filtro común:** antes de cada envío, GET lead status. Si `status_id == 91266100` (atencion personalizada), saltar (humano tomó el caso).

### 8.2 Seg. Imagen

- **Disparado por:** `AI Agent Main Image` cuando se mostró imagen principal del evento → mueve a ETAPA 2.
- **Timeline:** 1h → 3h → X → 24h
- **Detecciones:**
  - 1h: ¿contiene `"Qué padre!"`? → si no avanzó, mensaje de seguimiento.
  - 3h: ¿contiene `"para esa linda ocasión?"`? → seguimiento.
  - X: ¿contiene `"De lo que te compartí, hay algún..."`? → seguimiento.
  - 24h: ¿contiene `"puedo ayudarte a elegir lo más bonito y..."`? → si no avanzó y status==89263344 (ETAPA 1) → mover a perdidos (143).
- **Particularidad:** los seguimientos pasan por `actualizar22 → Envio Mensaje6` (formato distinto a Rebeca: actualiza etapa antes de enviar mensaje).

### 8.3 Seg. Cotización

- **Disparado por:** `AI Agent Products` cuando se mostraron productos → mueve a ETAPA 3 (93616836).
- **Timeline:** 1h → 3h → X → 24h
- **Detecciones:**
  - 1h: ¿contiene `"Producto Principal"`? → seguimiento.
  - 3h: ¿contiene `"necesito que me compartas la cantidad y..."`? → seguimiento.
  - X: ¿contiene `"solo me falta saber cuántas piezas neces..."`? → seguimiento.
  - 24h: ¿contiene `"para apartar y cotizar tus productos nec..."`? → bifurca a `Execute a SQL query4` + `Aggregate` + `Message a model` (gpt-4.1-mini que decide "respondió No?") → si "No" → mueve a 143; si != No → R1 SIN INFO.
- **Lógica adicional:** un agente LLM analiza la última respuesta del lead para decidir si abandonó o no, en lugar de simple match de texto.

### 8.4 Seg. 7 pasos

- **Disparado por:** `AI Agent Recolector` cuando se envió el mensaje de los 7 pasos → mueve a ETAPA 3 (93616836). _(Nota: el mismo destino que Cotización, raro — ver redundancias.)_
- **Timeline:** 24h
- **Detecciones:**
  - 24h: ¿contiene `"6. Al terminar, te enviamos..."` (mensaje de los 7 pasos)? → si sí, mueve a R1 CON INFO. Si no → query LLM (decide "No?") → si No, perdidos.
- **Bifurcación adicional:** chequea si lead llegó a `100395519` (en producción) → terminar; si llegó a `93616840` (ETAPA 4) → R1 CON INFO.

### 8.5 ATENCION_PERSONALIZADA (sub-workflow)

- **3 nodos:** trigger → Telegram "Usr. Se encuentra en etapa de cotización" → PATCH lead a 91266100.
- **Invocado como tool por:** AI Agent Recolector (`ATENCION_PERSONALIZADA` y `ATENCION_PERSONALIZADA6`).

---

## 9. Persistencia (3 capas)

### 9.1 Redis (memoria de sesión / debouncing)

- **Keys:** `contact_id` (numérico) y `numero_telefono` (string, segunda branch).
- **Operaciones:** `push` (agregar mensaje al array), `get` (recuperar array), `delete` (limpiar al iniciar nuevo turno).
- **Función:** Acumular mensajes en ráfaga durante la ventana de espera (15s/50s) y descartar turnos obsoletos.

### 9.2 PostgreSQL (memoria conversacional + tracking)

- **Tabla principal:** `n8n_chat_histories` (LangChain Memory) — 6 instancias (`Postgres Chat Memory` ... `6`), todas con el mismo `session_id` (= entity_id del lead).
- **Window length:** configurable por nodo (visible en `Memory_ID` y `Memory_ID1`).
- **Tablas custom:** los `Insert rows in a table*` en sub-workflows escriben a tablas auxiliares de tracking (no nombradas explícitamente en el extracto, pero existen — uso: registrar "envié seguimiento N a lead X a las HH:MM").

### 9.3 Kommo (estado del lead)

- Pipeline IA con 30+ etapas. La etapa actual es la fuente de verdad sobre dónde está el lead en el funnel.

### 9.4 Airtable (catálogo, no estado)

- Source of truth de productos y mensajes preparametrizados. No cambia durante una conversación.

---

## 10. Flujo end-to-end (caso típico — sample_1)

Lead nuevo escribe `"Hola! Quiero más información. Buenos días k precio tienen?!?"`:

1. `New_Message` recibe webhook.
2. `If25` → `Get_Contact` → `Clear_Contact_Data` → `All_Data`: enriquece datos.
3. `Get_Entity` → `No es IA`: lead está en pipeline 11622596 → continúa.
4. `If23 → If21 → If20`: lead en `89263340` (Incoming) → continúa.
5. `checkType`: tipo=texto → `Get_Text` → `Guardar` (Redis push) → `Wait_35` (50s) → `Get_Messages` → `Ultimo?` → es el último → `Date & Time` → `Message & Date`.
6. `Borrar almacenamiento` → `Memory_ID` → `Get_Entity2` → `If9` (status=91266100? no) → `GET_PREVIOUS_INTERACTION` (consulta Postgres).
7. `Exist_Interaction?`: vacío (lead nuevo) → `AI Agent Starter`.
8. AI Agent Starter responde con mensaje de saludo. Output → `Call 'HappyFlops - Seg. Rebeca'` (dispara timer asíncrono).
9. `If24` (¿output contiene `👼🏢`?): SÍ (porque el saludo incluye `👼🏢 - Otros`) → `Saludo PTE 1` (envía primera parte vía salesbot).
10. `Wait6` (2s) → `Saludo PTE 2` → `Wait7` (2s) → `Saludo PTE 3`.

Lead responde `"XV años"`:

11. Mismo flujo hasta `Exist_Interaction?`: ya hay interacción → `AI Agent` (Router maestro).
12. Router lee memoria, ve que ya enviamos saludo → emite `{"step":"step_2"}`.
13. `Switch1` → branch 1 → `AI Agent Main Image`.
14. AI Agent Main Image emite `{"evento":"XV","texto_dinamico":"Qué padre!..."}`.
15. Output → `Formula` (calcula `formula="evento=XV"`) → `Search_Main_Image` (Airtable, evento=XV) → `Envio Mensaje8` (salesbot envía imagen+texto).
16. En paralelo: `AI Agent Main Image → Envio Mensaje9 → Wait2 → Execute Workflow1` _(probablemente un seg adicional)_.
17. `Detect_Evento → Execute Workflow2`: arranca Seg. Imagen sub-workflow → mueve a ETAPA 2 (93616832).

Lead responde `"Kiero de sandalias y cilindros Y k es kit anti cruda?!? Ya vi"`:

18. Router emite `{"step":"step_3"}`.
19. `Switch1` → branch 2 → `GET_LAST_INTERACTION` → `AI Agent Products`.
20. AI Agent Products emite `{"evento":"XV","subcategoria":"Producto Principal","productos":["sandalias","cilindros","anticrudas"],"texto_dinamico":"¿Le interesa sumarlos a la cotización?..."}`.
21. `Is_Products_Empty`: array no vacío → `Message a model → Data → Return_Formula → Search_Products` (Airtable XV con productos solicitados).
22. `Loop Over Items`: por cada producto en results → `Wait3` → `Envio Mensaje7` (envía ficha producto vía salesbot).
23. Después del loop, mueve a ETAPA 3 (93616836) y arma Seg. Cotización.

Lead responde `"Buenas tardes disculpe será k me duren de AKI hasta noviembre"`:

24. Router emite `{"step":"step_4"}` (no menciona producto nuevo, ya se mostraron, pregunta del negocio).
25. `Switch1` → branch 3 → `AI Agent Recolector`.
26. Recolector responde con texto natural (sin JSON estructurado).
27. Output va por `Get_Entity1 → If7` (¿status==91266100 || 91450360? no) → `File_Not_Required` (¿NO contiene `.com123`? sí) → `Message a model1` (formatea para envío).
28. `Character_Cleaner → Wait → If2 → If26 → Envio Mensaje14` (envía respuesta vía salesbot).
29. En paralelo: `If3` (¿contiene `[Facebook Reviews]` o `#538`? no) → NoOp; `If4`/`If6` (¿contiene `7 DIAS DE PROMO` o `HAZ TU PEDIDO`? no, no es cotización) → NoOp.

---

## 11. Mensajes especiales que disparan side-effects

| Patrón en output del agente | Side-effect |
|------------------------------|-------------|
| Contiene `7 DIAS DE PROMO` | Trigger `Execute Workflow3` (Seg. 7 pasos) |
| Contiene `HAZ TU PEDIDO EN 7 SENCILLOS PASOS!` | Cambia formato de envío (mensaje + tracking 7 pasos) |
| Contiene `[Facebook Reviews]` o `#538` | Trigger `Code5/9` (envío de imagen Facebook reviews / mapa ubicación) |
| Contiene `.com123` (URL pago) | NO va por formato normal — flag `File_Not_Required` activa envío con adjunto Métodos de Pago |
| Contiene emoji `👼🏢` | Es saludo inicial → split en 3 partes con waits |

---

## 12. Operatividad humana (Telegram)

Notificaciones al chat `-4925599962`:

- `Usr. Envia Imágenes/Documentos1` — PDF detectado.
- `Usr. Envia Imágenes/Documentos2` — captura de pago (no producción).
- `Usr. Envia Imágenes/Documentos3` — imagen producto (clasificable).
- `Usr. Envia Imágenes/Documentos4` — PDF en branch alternativa.
- `Usr. Envia Imágenes/Documentos5` — captura pago alternativa.
- `Usr. Envia Imágenes/Documentos6` — captura pago liquidación.
- `Usr. Envia Imágenes/Documentos7` — lead en perdidos con actividad nueva.
- `Usr. Envia Imágenes/Documentos8` — captura pago liquidación alternativa.
- `Usr. Se encuentra en etapa de cotización` (sub-workflow ATENCION_PERSONALIZADA) — agente derivó al humano.
- `Usr. Envia Imágenes/Documentos` — imagen "no clasificable" (`falso`) → notifica + ATENCION_PERSONALIZADA4.

---

## 13. Mapa de dependencias

```
Lead WhatsApp
   │
   ▼
Kommo (canal WA conectado, pipeline IA 11622596)
   │ webhook on message
   ▼
n8n main workflow (225 nodos)
   ├── Filtros: pipeline IA, status válido, no AP
   ├── Tipo: texto/audio/imagen/PDF
   ├── Anti-ráfaga: Redis 15-50s
   ├── Memoria: Postgres LangChain
   ├── Router (AI Agent) decide step
   ├── Agente despachado (Starter|MainImage|Products|Recolector|Recolector1)
   │      ├── Tools: CALCULADORA (sub-wf), ATENCION_PERSONALIZADA (sub-wf), Think
   │      └── Output: JSON o texto
   ├── Envío: salesbot v2 (predominante) o sendMessage v2 (Send_Attachment6)
   ├── Mover etapa Kommo (PATCH v4)
   └── Disparar sub-workflows asíncronos:
          ├── Seg. Rebeca (timers 1h/3h/24h)
          ├── Seg. Imagen (timers + ETAPA 2)
          ├── Seg. Cotización (timers + LLM evaluador + ETAPA 3)
          └── Seg. 7 pasos (timer 24h + LLM evaluador + ETAPA 3)
   │
   ▼
Telegram (notificaciones operativas al equipo)
```

---

## 14. Resumen ejecutivo del sistema

1. **Único punto de entrada productivo:** webhook desde Kommo, pipeline `IA` (11622596). Otros 12 pipelines son legacy/manuales.
2. **Agente Rebeca = 4 pasos en cascada:** Saludo → Imagen del evento → Ficha de productos → Cotización + cierre.
3. **6 LLMs orquestados:** 1 Router + 4 agentes especializados + 1 clasificador de imagen + ≥2 helpers (formato/respuesta especial).
4. **Catálogo en Airtable:** 1 base con 6 tablas. Cada producto tiene `bot_id` que apunta a un salesbot Kommo que ya tiene la imagen+texto cargados.
5. **Envío de mensajes vía salesbot legacy** (predominantemente) — n8n NO compone los mensajes finales del producto, solo dispara el salesbot por ID.
6. **Persistencia en 3 capas:** Redis (debounce), Postgres (memoria conversacional + tracking de seguimientos), Kommo (estado del lead).
7. **Re-engagement automático:** 4 sub-workflows que esperan, leen memoria, deciden si reactivar y mueven etapas.
8. **Operatividad humana:** Telegram notifica al equipo en 9 escenarios (PDF, pago, imagen no clasificable, derivación a humano, etc.).
