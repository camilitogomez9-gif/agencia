# ¿Se saca ManyChat del stack? — análisis feature-por-feature

**Fecha:** 2026-08-26 · **Contexto:** Max preguntó explícitamente si podemos "centralizar en GHL sin perder capacidades importantes" y expresó preferencia por simplificar el stack. Mauricio abrió la duda al mencionar "auto-DM a nuevos seguidores" como algo que hoy no tienen activo pero les interesaría.

> **Veredicto:** Sí, se saca. Stack final: **n8n + GoHighLevel**. Cero pérdida de capacidad respecto de lo que Venttur usa hoy. Se recomienda comunicárselo a Mauricio y Max **antes** de que arranquen a jugar con GHL, para que no configuren duplicado.

---

## 1. Lo que ManyChat hace hoy en Venttur (inventariado desde el repo)

Fuentes: `00_migracion_ghl/00_inputs/vtr-data-snapshot-2026-07-24.json` (auditoría de la cuenta ManyChat vía API) + `00_migracion_ghl/00_inputs/manychat-flows-inventario-2026-08-17.md` (contenido de los 17 flows).

**Inventario completo:**

| # | Feature | Estado en Venttur |
|---|---|---|
| 1 | Canal WhatsApp con WABA conectada | Activo. Es el único canal productivo del bot |
| 2 | 17 flows (contenedores de plantillas Meta) | Activos. **Todos con `When... [vacío]`** — no tienen trigger propio, se disparan sólo por `sendFlow` desde n8n |
| 3 | 13 custom fields de contact | Activos (`agendan_cita`, `programa_wpp`, `parte1/2/3`, `ctwa_clid`, `ad_source_id`, etc.) |
| 4 | 5 tags | Activos (`seguimiento_agenda`, `wpp`, `seguimiento`, `RESCATE_PROGRAMA_NO_MAPEADO`, `LINK_ABANDONADO_FRIO`) — 1 huérfano (`wpp` no lo aplica nadie) |
| 5 | External Request (Default Reply) → n8n | Activo. Es el punto de entrada del agente conversacional |
| 6 | Live Chat / Inbox del equipo | Activo (asumido — no verificado por API, pero se usa para elevar) |
| 7 | Handoff manual (pausar bot, asignar a humano) | Activo vía flow "Elevar" |
| 8 | Persistent menu / Welcome message / Bienvenida | No usados |

**Features de ManyChat que Venttur NO usa** (verificado):

- ❌ **Growth Tools** — la cuenta tiene `widgets: []`
- ❌ **Keyword triggers** — los 17 flows tienen `When... [vacío]`; sólo se disparan por API
- ❌ **Default Reply propia** — la reemplaza el External Request que lleva todo a n8n
- ❌ **Comment reply automation** en Facebook/Instagram
- ❌ **Auto-DM triggers** (por follower, por post, por keyword)
- ❌ **Broadcasts nativos** — todos los envíos son 1:1 disparados por n8n
- ❌ **Follow-to-DM** — nunca se activó

**Conclusión:** en Venttur, ManyChat es un **caño para mandar templates de WhatsApp** — no una plataforma de flujos conversacionales. Se aprovecha ~20% de sus capacidades.

---

## 2. Mapeo feature-por-feature ManyChat → GHL

**Base:** documentación oficial de HighLevel Support ([Workflow Action WhatsApp](https://help.gohighlevel.com/support/solutions/articles/155000001624-whatsapp-workflow-integration), [WhatsApp Templates](https://help.gohighlevel.com/support/solutions/articles/155000003069-whatsapp-send-message-templates-snippets-), [Instagram Interactive Messenger](https://help.gohighlevel.com/support/solutions/articles/155000004662-workflow-action-instagram-interactive-messenger), [Comment Automation Guide](https://help.gohighlevel.com/support/solutions/articles/155000002055-guide-to-facebook-instagram-comment-automation-ai)) más análisis independientes.

### 2.1 Los 8 casilleros activos hoy

| # | ManyChat (Venttur, hoy) | GHL (equivalente) | Notas |
|---|---|---|---|
| 1 | **Canal WhatsApp (WABA)** | ✅ **Conversations + WhatsApp Business Platform via LeadConnector** | La WABA se conecta al Business Manager de Venttur como en cualquier BSP. Aparece en el mismo Inbox que IG/FB/SMS/Email |
| 2 | **17 flows = templates enviados por API** | ✅ **Message Templates + Workflow Send Action** | Se importan las plantillas ya aprobadas por Meta (no hay que re-aprobar si se migra el WABA vía BSP migration). Cada flow se colapsa a una template + un workflow que la envía |
| 3 | **13 custom fields de contact** | ✅ **Contact Custom Fields** (más tipos disponibles) | Migración 1:1. `agendan_cita` (bool), `programa_wpp` (dropdown), `parte1/2/3` (text), etc. En GHL se pueden tipar mejor (dropdown vs texto libre) |
| 4 | **5 tags** | ✅ **Contact Tags** (nativos) | Migración 1:1. El tag huérfano `wpp` se descarta |
| 5 | **External Request → n8n** en cada mensaje entrante | ✅ **Contact Reply trigger → HTTP Request al webhook n8n** | Reemplazo directo. Menos hops (hoy es lead→MC→n8n; queda lead→GHL→n8n) |
| 6 | **Live Chat / Inbox** | ✅ **Conversations Inbox** (unificado con IG/FB/SMS/Email) | Superior: hoy Venttur no tiene un único lugar para atender leads de todos los canales |
| 7 | **Handoff via flow "Elevar"** | ✅ **Assign to User + Manual Message notification** | Reemplazo directo. En GHL además hay OpportunityStage automations |
| 8 | **Variables en mensajes** (`{{first_name}}`) | ✅ **Merge Fields** | Sintaxis distinta (`{{contact.first_name}}`) pero mismo poder |

**Verdad clave:** cada uno de los 8 casilleros tiene un equivalente exacto o superior en GHL. Cero funcionalidad activa se pierde.

### 2.2 Lo nuevo que Max/Mauricio quieren agregar

| Pedido | ¿ManyChat lo hace hoy? | ¿GHL lo hace? | Comentario |
|---|---|---|---|
| **Auto-DM a nuevos followers IG/FB** | ❌ No (Mauricio: "no lo tenemos activo") | ❌ No | **Es una limitación de la API de Meta, no de la plataforma.** El "Follow Trigger" de Meta está en beta cerrado. ManyChat lo ofrece pero requiere cuenta elegible (1000+ followers + engagement + verificación); no está garantizado. GHL tiene la feature request abierta. **Ninguna de las dos plataformas te asegura esto.** |
| **Comment reply automation IG/FB (keyword → DM)** | ✅ Sí (no activado en Venttur) | ✅ Sí (con IA nativa) | **GHL lo hace mejor** — soporta AI-powered replies. Es la alternativa realista al auto-DM a followers |
| **Comunidades** | ❌ No tiene | ✅ Sí (GHL Communities es un producto) | Nuevo scope. GHL nativo |
| **Formularios** | Limitado (dentro de Growth Tools) | ✅ Sí (GHL Forms + Surveys) | Superior |
| **Landing pages** | ❌ No | ✅ Sí (GHL Sites) | Nuevo scope. Reemplaza Lovable si el cliente quiere consolidar |
| **Calendarios / agendamiento** | ❌ No | ✅ Sí (GHL Calendars, decisión ya tomada — 8 calendarios por programa) | Ya decidido en Etapa 2 |

**Conclusión:** GHL cubre TODO lo que ManyChat cubre, cubre TODO lo que Venttur quiere agregar (excepto lo que Meta no permite a nadie), y encima trae piezas nuevas (Communities, Sites, Auto-DM por comentarios con IA).

---

## 3. Detalle sobre el auto-DM a nuevos followers

Es el único punto que abre duda razonable, así que amerita separarlo del resto.

**Los datos duros de Meta:**

- El "Follow Trigger" de la Instagram Messaging API está en **beta cerrado, sin GA (General Availability)**.
- Meta puede revocar el acceso a cualquier herramienta que use métodos no oficiales para simular el trigger.
- Requisitos típicos para acceder al beta (cuando se abre): **1000+ followers**, engagement significativo, cuenta Business/Creator con verificación aprobada, región habilitada.

**Consecuencia práctica:**

- **Mantener ManyChat "por si acaso"** no elimina el riesgo — ManyChat tampoco te garantiza que la cuenta de Venttur califique al beta.
- Si el día de mañana Meta abre el trigger públicamente, GHL probablemente lo incorpora (ya tiene la feature request abierta).
- Mientras tanto, **la alternativa que funciona en ambas plataformas** es auto-DM a **comentarios** en posts/reels con keyword. Esto es lo que la industria recomienda y lo que hace la mayoría de creators.

**Recomendación al cliente:** activar comment→DM automation en GHL apenas se migre el canal. Cubre el 80% de la intención ("engancho al que interactúa con mi contenido") sin depender de un beta cerrado.

---

## 4. Beneficios netos de sacar ManyChat

Estos son medibles, no marketing:

1. **Una plataforma menos** — 1 cuenta menos, 1 API key menos, 1 costo mensual menos, 1 superficie de bugs menos. Menos onboarding para Max/Mauricio.
2. **Inbox unificado** — hoy WhatsApp está en ManyChat, IG/FB en otro lado. GHL Conversations los agrupa. Esto le importa a Max, que gestiona el operativo.
3. **Un hop menos en cada mensaje** — hoy: `lead → MC → n8n → LLM → n8n → MC → lead`. Después: `lead → GHL → n8n → LLM → n8n → GHL → lead`. Un webhook menos donde puede fallar.
4. **CRM + canal en la misma capa** — hoy el contact vive en Clientify/Airtable, los custom fields del canal en ManyChat, la memoria en Supabase. Con GHL: contact + fields + tags + pipeline en un solo lugar (la memoria conversacional del bot se queda en Supabase, sin cambios).
5. **Comment reply IG/FB con IA nativa** — Venttur podría prender esto sin agregar herramientas.
6. **Auditoría más limpia** — al eliminar la capa ManyChat, se acaba el pattern "pero eso se hace en ManyChat" que hoy dispersa la lógica en dos plataformas.

---

## 5. Costos operativos de la decisión

Todo cambio tiene fricción. Los enumero para que la decisión sea informada:

1. **Migración de 13 custom fields** — mapping 1:1, un CSV bulk create en GHL. Bajo esfuerzo.
2. **Migración de 5 tags** — creación manual en GHL, luego se aplican vía workflows. Bajo esfuerzo.
3. **Re-creación de flows como GHL Message Templates + Workflows** — mediano. Los 17 flows probablemente se colapsen a ~10 (varios son variantes de la misma template para distintos programas).
4. **Meta Business Verification / WABA migration** — depende de la desambiguación del WABA (punto abierto de Etapa 0, ver `06_docs/portabilidad-numero-whatsapp-2026-08-18.md`). Si el WABA está bajo Business Manager de Venttur, migración BSP nativa preserva número, calidad, límites y templates. Si está bajo Business Manager de ManyChat, número nuevo obligado.
5. **El External Request se recablea a GHL** — la URL que hoy escucha n8n cambia de "disparada por MC External Request" a "disparada por GHL Contact Reply → HTTP Request". Es un cambio en un solo workflow n8n.
6. **Capacitación del equipo Venttur** — Andrés/Diego/Rodrigo pasan de mirar chats en ManyChat a mirarlos en GHL Conversations. Es la misma UX general (bandeja de conversaciones), pero cambia. GHL ofrece onboarding gratis con el trial de 7 días — coincide con lo que la agencia ya les comentó.

**El costo #4 es el único que puede complicar el 15/9.** El resto es trabajo directo de migración, ya contemplado.

---

## 6. Riesgos residuales

**Ninguno que impida la decisión.** Los que están:

- **Si Meta abre el Follow Trigger públicamente y Venttur califica:** GHL probablemente lo tenga en el roadmap. Si no, se agrega una herramienta puntual (ej. Inrō) solo para esa función, sin volver a un stack híbrido completo.
- **Un flow "escondido" de ManyChat que no encontramos:** el inventario es exhaustivo (17 flows, 13 fields, 5 tags, 0 widgets), pero si aparece algo del lado del cliente que use ManyChat de forma no documentada, se maneja en el momento. Probabilidad baja.
- **La cuenta ManyChat sigue teniendo el WABA**: importante — hasta que resolvamos la desambiguación del WABA (Etapa 0), el número **está** en la infraestructura ManyChat. Sacar ManyChat como plataforma NO significa desconectar el WABA a la ligera. La desconexión sucede en el cutover, coordinada con la migración BSP a GHL.
