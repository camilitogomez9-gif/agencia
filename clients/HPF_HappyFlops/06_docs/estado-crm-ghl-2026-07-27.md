# Estado del CRM — Happy Flops

Reporte completo de dónde vive el CRM, cómo está estructurado, cómo se maneja un lead de punta a punta, qué falta, y qué hay que revisar a mano en cada plataforma.

**Fecha:** 27 de julio de 2026
**Alcance:** la migración Kommo → GoHighLevel. El bot de Kommo sigue siendo el sistema en producción.

---

## 1. Resumen ejecutivo

- **El CRM vive en GoHighLevel**, en una sub-cuenta dedicada a Happy Flops. La estructura (pipeline, etapas, campos, tags, valores globales) **está creada y es correcta**. Eso ya está hecho.
- **El agente todavía no escribe en ese CRM.** Corre en n8n y hoy entra por Telegram, un canal que no tiene contacto ni oportunidad en GHL, así que cada intento de escritura falla. No es un problema de estructura: es de conexión.
- **La conexión de la WABA resuelve la mitad del problema** — hace que el lead llegue con su contacto y su oportunidad reales. Pero **no alcanza sola**: falta construir el workflow de GHL que le avisa a n8n que llegó un mensaje. Sin eso, conectar el número no dispara nada.
- Hay **tres cosas que hay que verificar a mano en GHL** antes de dar por buena la estructura: las claves reales de los campos personalizados, el tipo exacto de los campos de checkbox, y la configuración de deduplicación de contactos. Detalle en la sección 8.

---

## 2. Mapa de sistemas — dónde vive cada dato

| Dato | Vive en | Identificador | Estado |
|---|---|---|---|
| Identidad del lead (nombre, teléfono, tags) | GoHighLevel · Contact | sub-cuenta `onRwi0ZF4uYi0Lp6GAbE` | Estructura lista |
| Estado de la venta (etapa, evento, cantidades, cotización) | GoHighLevel · Opportunity | pipeline "Happy Flops IA" | Estructura lista, sin datos reales |
| Configuración editable por el cliente (precios, horarios, promo) | GoHighLevel · Custom Values | sub-cuenta | Creados, **nadie los lee todavía** |
| Historial completo de la conversación | Postgres / Supabase · tabla `messages` | credencial n8n `H.F` | En uso |
| Agrupado de mensajes en ráfaga | Postgres / Supabase · tabla `debounce_buffer` | idem | En uso |
| Catálogo de productos con fotos | Airtable `Productos \| Happy Flops` | base `appMHtUN9zKYODufC` | En uso **solo por el bot de Kommo** |
| Orquestación (el agente) | n8n | workflow `HPF Inbound Handler`, id `IPO1c36NLzkXrBh9` | Activo |
| CRM en producción hoy | Kommo / AmoCRM | pipeline `IA` (11622596) | Vivo, se apaga en el cutover |

> El catálogo de Airtable y el CRM de Kommo son del sistema viejo. La migración **no los reemplaza todavía**: conviven hasta el cutover.

---

## 3. La estructura del CRM en GoHighLevel

### 3.1 Sub-cuenta y accesos

| Ítem | Valor | Confianza |
|---|---|---|
| Sub-account / locationId | `onRwi0ZF4uYi0Lp6GAbE` | **Inferido**, no confirmado — ver 8.1 |
| Zona horaria | `America/Mexico_City` | Documentado |
| Teléfono del negocio | +52 331 594 8670 | Documentado |
| Autenticación de n8n hacia GHL | Private Integration Token (PIT) | Confirmado |
| Credencial en n8n | `GHL PIT HPF` (id `Zz21t1RdLIMvud4j`) | Confirmado |
| Versión de API | `2021-07-28` (header `Version` en cada request) | Confirmado |

El valor del token no está en ningún archivo del repositorio: vive solo en el almacén de credenciales de n8n.

### 3.2 Pipeline y etapas

Un solo pipeline automatizado: **"Happy Flops IA"**, con 13 etapas en español.

| # | Etapa | Quién la mueve | ¿El agente responde? |
|---|---|---|---|
| 1 | Lead Nuevo | Se crea con el lead | Sí — manda el saludo fijo |
| 2 | Saludo Enviado | El sistema, tras el saludo | Sí |
| 3 | Evento Identificado | Cuando se escribe `evento_detectado` | Sí |
| 4 | Productos Mostrados | Cuando se escribe `productos_mostrados` | Sí |
| 5 | Cotizado | La herramienta COTIZADOR | Sí |
| 6 | Esperando Pago | Al detectar un comprobante estando en Cotizado | Pausado (solo acusa recibo) |
| 7 | Pago Confirmado | Al detectar el segundo comprobante | Pausado |
| 8 | Diseño en Proceso | Manual (diseñadora) | Pausado |
| 9 | En Producción | Manual (equipo) | Pausado |
| 10 | Enviado | Manual | Pausado |
| 11 | En Espera | El reenganche, al agotar el ciclo sin respuesta | Sí, si el lead vuelve a escribir |
| — | Ganado | Manual | No |
| — | Ventas Perdidas | Barrido de inactividad a 180 días | No |

**IDs de etapa conocidos** (los únicos que hoy están escritos en algún lado):

| Etapa | Stage ID |
|---|---|
| Cotizado | `96fa0ade-c853-4db3-97f4-56d58d69af8c` |
| Esperando Pago | `843a06f1-1214-4baa-a3a0-f197cb240b5d` |
| Pago Confirmado | `96d760e5-f290-456c-a117-57e61ce6c27d` |

Los otros 10 nunca se anotaron. El ID del pipeline tampoco. Se obtienen los 14 de una sola llamada — ver 8.1.

### 3.3 Campos personalizados del Opportunity

Es donde vive el estado de la venta. Están creados los cinco bloques del diseño; lo que cambia es **cuáles se usan de verdad**.

**Se escriben hoy (o se escribirán apenas el CRM esté conectado):**

| Campo | Tipo | Quién lo escribe |
|---|---|---|
| `evento_detectado` | Dropdown (XV, Boda, Bautizo, Cumpleaños, Empresarial, Otro) | Herramienta IDENTIFICAR_EVENTO |
| `productos_mostrados` | Texto (lista separada por comas) | Herramienta MOSTRAR_PRODUCTOS |
| `monto_cotizado_mxn` | Número | Herramienta COTIZADOR |
| `cotizacion_anticipo_mxn` | Número | COTIZADOR |
| `cantidad_sandalias` · `cantidad_cilindros` · `cantidad_mandiles` · `cantidad_otros` | Número | COTIZADOR |
| `tipo_suela` | Dropdown (Delgada, Gruesa, Yute) | COTIZADOR |
| `cp_entrega` | Texto | COTIZADOR |
| `last_outbound_at` · `last_inbound_at` | Texto en formato ISO 8601 | n8n, al terminar cada turno |
| `imagen_input` | Checkbox | n8n, cuando el lead manda una imagen |
| `payment_proof_detectado` | Checkbox | n8n, cuando la imagen es un comprobante |
| `comprobante_anticipo_url` / `_at` · `comprobante_liquidacion_url` / `_at` | Texto | n8n, en la transición de pago |

**Creados pero que nadie escribe todavía:** `ultima_imagen_clasificada`, `cotizacion_generada_at`, `talla_sandalias`, `had_information`, `had_image`, `had_quote`, `last_re_engagement_wave`, `re_engagement_completed_at`, `diseno_aprobado_at`, `fecha_prometida_envio`, `tracking_number`, `paqueteria`, `notas_postventa`, `created_at_first_contact`, `time_to_quote_hours`, `time_to_close_hours`.

Los tres `had_*` los consume la segmentación del reenganche, que todavía no existe. Los de post-venta y métricas están reservados para cuando el equipo trabaje dentro de GHL.

> **Nota técnica sobre los checkbox.** La API de GoHighLevel exige que los campos de tipo checkbox se identifiquen por `id` (no por su clave) y que el valor sea una lista de textos. Como valida el bloque completo, **un campo mal formado rechaza toda la escritura**, incluidos los campos correctos que viajan en el mismo pedido. Por eso hoy las herramientas escriben únicamente campos de texto. Antes de sumar los `had_*` hay que mirar en la interfaz de GHL cómo quedaron definidos esos campos (ver 8.1).

### 3.4 Campos personalizados del Contact

Cinco creados: `re_engagement_paused`, `is_test_lead`, `preferred_language`, `total_orders`, `lifetime_value_mxn`. Más `customer_status` que figura como pendiente de crear.

**Ninguno se escribe ni se lee hoy.** El agente solo aplica tags al contacto.

### 3.5 Tags

Ocho tags predefinidos: `atencion_humana`, `reenganche_fase_1`, `reenganche_fase_2`, `reenganche_completado`, `pausado`, `lead_prueba`, `pago_detectado`.

**Solo se usa `atencion_humana`**, que aplica la herramienta ATENCION_PERSONALIZADA cuando el agente deriva a un humano. Los de reenganche los aplicaría el workflow WF-02, que no existe.

### 3.6 Custom Values (la configuración global)

Alrededor de 24 valores creados para que el cliente pueda cambiar cosas sin tocar workflows: precios por producto, horario laboral, días laborales, mensaje de fuera de horario, textos de promo, cadencias de reenganche, modelo y temperatura de la IA, teléfono oficial.

> ⚠️ **Hoy no los lee nadie.** Los precios, el teléfono oficial, los mínimos de compra y el texto de la promo están escritos dentro del prompt del agente y dentro de la herramienta de cálculo de envío. Si Oscar edita `precio_cilindros` en GoHighLevel, **el agente sigue cotizando el precio viejo**. Es una diferencia importante entre lo diseñado y lo implementado, y hay que decidir si se cablea o si se le avisa al cliente que esos valores son decorativos por ahora.

Además quedaron tres valores con datos de relleno desde junio: `precio_cilindros`, `precio_mandiles` y `telegram_chat_id_oscar`.

---

## 4. Cómo se maneja un lead, paso a paso

Este es el recorrido **objetivo**, el que va a correr una vez conectada la WABA. Entre paréntesis, lo que hoy hace n8n en el canal de prueba por Telegram.

| Momento | Qué pasa | Qué queda registrado en el CRM |
|---|---|---|
| Llega el primer mensaje | GHL recibe el WhatsApp, crea el contacto y la oportunidad en **Lead Nuevo** y dispara el workflow de entrada | Contact + Opportunity creados |
| Saludo | Se manda el saludo fijo de tres partes (texto no modificable) y se pasa a **Saludo Enviado** | Etapa + `last_outbound_at` |
| El lead dice su evento | El agente llama a IDENTIFICAR_EVENTO; el sistema manda automáticamente la imagen del catálogo del evento y el texto de la promo, y pasa a **Evento Identificado** | `evento_detectado` + etapa |
| El lead pide productos | El agente llama a MOSTRAR_PRODUCTOS, describe los productos en texto y el sistema manda las fichas que tengan foto cargada. Pasa a **Productos Mostrados** | `productos_mostrados` + etapa |
| Se junta la información para cotizar | El agente pide en un solo mensaje todo lo que falta: cantidades, código postal, tipo de suela y variantes | — |
| Cotización | La herramienta de envío calcula el costo de forma determinística (pesos, límites de empaque, mínimos de compra); el agente arma la cotización con el formato fijo y llama a COTIZADOR. Pasa a **Cotizado** | Monto, anticipo, cantidades, CP, etapa |
| Llega el comprobante | El clasificador de imágenes lo detecta y mueve a **Esperando Pago**; el agente acusa recibo y se calla | `payment_proof_detectado`, URL del comprobante, etapa |
| Segundo comprobante | Mueve a **Pago Confirmado** | idem liquidación |
| Diseño, producción y envío | Manual, del equipo, dentro de GHL | Etapas manuales |
| El lead no contesta | El reenganche manda olas a 1h/3h/5h y después a 24h/48h/5d/7d; si nunca responde, cae en **En Espera** | Tags + `last_re_engagement_wave` |
| El lead pide un humano | El agente aplica el tag `atencion_humana`, avisa al equipo y **deja de responder** hasta que le saquen el tag | Tag en el contacto |

**Dos reglas que definen todo el diseño:**

1. **El estado del lead es la etapa del Opportunity**, no una variable del agente. Cualquier pieza del sistema puede leer en qué punto está un lead mirando el pipeline.
2. **Un contacto puede tener varias oportunidades.** Si el mismo lead vuelve meses después, se abre una oportunidad nueva y la historia anterior queda intacta.

---

## 5. Qué escribe cada pieza

| Pieza | Dónde corre | Qué toca del CRM |
|---|---|---|
| IDENTIFICAR_EVENTO | Herramienta del agente | `evento_detectado` |
| MOSTRAR_PRODUCTOS | Herramienta del agente | `productos_mostrados` |
| COTIZADOR | Herramienta del agente | Los campos de la cotización (monto, anticipo, cantidades, suela, CP) + mueve a **Cotizado** |
| ATENCION_PERSONALIZADA | Herramienta del agente | Tag `atencion_humana` en el contacto |
| CALCULAR_ENVIO | Herramienta del agente | Nada — es cálculo puro, no toca el CRM |
| Clasificador de imágenes | Nodo de n8n | `imagen_input`, `payment_proof_detectado`, comprobantes, etapa de pago |
| Cierre de turno | Nodo de n8n | `last_outbound_at`, `last_inbound_at` |
| Workflows de GHL (WF-01 a WF-06) | GoHighLevel | **No existen** — ver sección 7 |

---

## 6. Estado real hoy

| Componente | Estado |
|---|---|
| Sub-cuenta, pipeline, etapas, campos, tags, valores globales | ✅ Creados |
| Agente conversacional (tono, reglas de negocio, cotización, mínimos) | ✅ Probado en dos rondas: 13/15 y ~18/20 casos |
| Cálculo de envío determinístico | ✅ Verificado con cuatro cotizaciones exactas |
| Memoria persistente por lead | ✅ En uso |
| Envío de imágenes | ✅ Resuelto (27/7) |
| Clasificación de imágenes y transcripción de audios | ✅ Implementado |
| **Escritura en el CRM** | ❌ **No escribe.** El canal de prueba no tiene contacto ni oportunidad reales, así que cada intento devuelve error |
| **Workflows de GoHighLevel** | ❌ **Ninguno construido** |
| **Canal de WhatsApp (WABA)** | 🔄 En traspaso |
| Reenganche / seguimientos | ❌ No construido |
| Guardia de horario laboral | ❌ No construida |
| Reportes y métricas | ❌ Fuera del alcance inicial |

---

## 7. Lo que falta hacer

### 7.1 Bloqueante — conectar el CRM de verdad

El agente ya tiene las cuatro herramientas apuntando a GoHighLevel, pero el canal de prueba les pasa identificadores inventados, así que todas fallan. Peor: cuando una herramienta falla, el agente recibe el texto del error **como si fuera un resultado válido**, y puede terminar mencionándoselo al lead.

Dos caminos, y hay que elegir uno:

- **Esperar a la WABA.** Con el canal conectado, el lead llega desde GoHighLevel con su contacto y su oportunidad reales, y todo funciona sin tocar nada. Es lo natural si el traspaso es inminente.
- **Desconectar las herramientas mientras tanto.** Devolverlas a modo "registrado y sigo" para que la demo no arrastre errores.

Lo que no conviene es dejarlo como está: pega, falla, y el error circula.

### 7.2 Bloqueante — los workflows de GoHighLevel

**Conectar la WABA no alcanza por sí solo.** Falta construir, dentro de GHL, la automatización que reacciona a un mensaje entrante y le avisa a n8n. Sin eso, el número queda conectado y no pasa nada: los mensajes llegan a la bandeja de GHL y ahí se quedan.

Los seis workflows del diseño:

| ID | Nombre | Qué hace | Prioridad |
|---|---|---|---|
| WF-01 | Enrutador de Entrada | Recibe el mensaje, aplica las guardas (horario, atención humana), manda el saludo fijo si es lead nuevo, y llama a n8n para todo lo demás | **Imprescindible** |
| WF-04 | Pago Detectado | Transiciones de etapa al recibir comprobantes | Alta |
| WF-06 | Monitor de Transición de Etapas | Mueve las etapas según los campos que escribe el agente | Alta |
| WF-05 | Guardia de Horario | Responde fuera de horario y pausa el procesamiento | Media |
| WF-02 | Reenganche Dual | Las olas de seguimiento | Media |
| WF-03 | Barrido de Inactividad | Mueve a Ventas Perdidas a los 180 días | Baja |

> Nota: WF-01, WF-04 y WF-06 son justamente lo que la versión alternativa del workflow de n8n (`v16`) implementa del lado de n8n para el canal de prueba. Si se decide construirlos en GHL, esa lógica se apaga; si no, se puede dejar viviendo en n8n. Es una decisión de arquitectura, no una duplicación necesaria.

### 7.3 Depende de Oscar

- **Fotos de producto que faltan.** El bot de Kommo mandaba las fichas adjuntando archivos guardados dentro del propio Kommo, no por enlace. Las copias en Airtable ya vencieron y las de Drive piden inicio de sesión. Sobreviven once enlaces públicos que cubren cilindros, kit anticruda, bolsa, tintas, correas y tapas. **Sandalias, pantuflas, mandiles y vasos popote no tienen ninguna copia recuperable fuera de Kommo.** Hay que bajarlas de ahí antes del cutover y subirlas a la biblioteca de GoHighLevel.
- **Datos bancarios.** El agente ofrece pasarlos y no los tiene. El sistema viejo mandaba un PDF con los números de cuenta que también vive solo dentro de Kommo.

### 7.4 Decisiones abiertas

- **¿Los precios se leen de GoHighLevel o quedan en el prompt?** Hoy están en el prompt. Si se quiere que Oscar los edite desde la interfaz, hay que cablearlos.
- **¿Los `had_*` se escriben?** Solo hacen falta cuando exista el reenganche.
- **¿El catálogo se muda a GoHighLevel?** El diseño contemplaba un objeto personalizado "Producto"; la decisión de julio fue dejarlo en Airtable. Conviene confirmarla.

---

## 8. Revisión manual — qué hay que mirar en cada plataforma

Esta sección es para hacerla con las plataformas abiertas. Cada ítem incluye qué mirar y qué significa si está mal.

### 8.1 GoHighLevel

**Identidad de la cuenta**

- [ ] Confirmar que la sub-cuenta es `onRwi0ZF4uYi0Lp6GAbE`. Se ve en la URL al entrar: `app.gohighlevel.com/location/<ESTE_ES_EL_ID>/`. Está inferido de las URLs de las imágenes; nunca se anotó en ningún documento.
- [ ] Anotarlo en `04_guia_migracion/01_setup_ghl.md`, que tiene el campo en blanco desde junio.

**Pipeline y etapas**

- [ ] CRM → Pipelines: que exista **"Happy Flops IA"** y que tenga las 13 etapas en el orden de la sección 3.2, con los nombres exactos. *El código compara por nombre en varios lugares: una tilde o una mayúscula de más rompen la comparación.*
- [ ] Anotar el ID del pipeline y los 13 IDs de etapa. La forma rápida es una sola llamada a la API:

```bash
PIT="pit-....."   # valor de la credencial "GHL PIT HPF" en n8n
LOC="onRwi0ZF4uYi0Lp6GAbE"
curl -s -H "Authorization: Bearer $PIT" -H "Version: 2021-07-28" \
  "https://services.leadconnectorhq.com/opportunities/pipelines?locationId=$LOC"
```

- [ ] Verificar que los tres IDs que ya usamos siguen siendo los de la sección 3.2. *Si cambiaron, las transiciones de pago y de cotización se rompen en silencio.*

**Campos personalizados — el punto más delicado**

- [ ] Settings → Custom Fields → Opportunities: revisar la **clave** (no la etiqueta) de cada campo. GoHighLevel la autogenera a partir de la etiqueta en español, así que "Código Postal de Entrega" pudo haber quedado como `cdigo_postal_de_entrega` en vez de `cp_entrega`. La guía de junio avisaba de corregirlas a mano una por una; **no hay constancia de que se haya hecho para todos**. La única clave probada es `evento_detectado`.
- [ ] Anotar cuáles no coinciden con la sección 3.3. *Cada clave que no coincida es un campo que el agente cree estar escribiendo y no escribe.*
- [ ] Para los campos de checkbox (`imagen_input`, `payment_proof_detectado`, `had_information`, `had_image`, `had_quote`, `cotizacion_emitida`): mirar **cómo quedaron definidos**. Si tienen opciones, anotar el texto exacto de cada opción. *Ese texto es el valor que hay que escribir; un checkbox mal escrito rechaza el pedido completo, incluidos los campos correctos que van en el mismo envío.*
- [ ] Settings → Custom Fields → Contacts: confirmar los cinco campos y si `customer_status` llegó a crearse.

**Tags y valores globales**

- [ ] Settings → Tags: los ocho tags con el nombre exacto, especialmente `atencion_humana` (es el único en uso y se escribe por nombre).
- [ ] Settings → Custom Values: anotar la **clave real autogenerada** de cada uno. GoHighLevel quita acentos y no deja editarlas después, así que "Días Laborales" quedó como `das_laborales` y "Pedido Mínimo Sandalias" como `pedido_mnimo_sandalias`.
- [ ] Completar los tres que quedaron con relleno: `precio_cilindros`, `precio_mandiles`, `telegram_chat_id_oscar`.
- [ ] Decidir qué hacer con el desfase de precios: hoy los valores de GHL no los lee nadie (ver 3.6).

**Deduplicación de contactos**

- [ ] Settings → Business Profile → Contact Deduplication Preferences: mirar cuál es el **campo primario**. *Si es Teléfono y el canal de prueba entra sin teléfono, GoHighLevel crea un contacto nuevo por cada mensaje. El síntoma es inconfundible: el bot saluda de cero cada vez y la lista de contactos se llena de duplicados.*

**Permisos del token**

- [ ] Settings → Integrations (o Private Integrations): confirmar que el PIT tiene permisos de lectura y escritura de contactos y oportunidades, y lectura de campos personalizados y pipelines. Prueba rápida:

```bash
curl -s -o /dev/null -w "%{http_code}\n" -H "Authorization: Bearer $PIT" -H "Version: 2021-07-28" \
  "https://services.leadconnectorhq.com/locations/$LOC/customFields?model=opportunity"
```

*200 está bien. 401 o 403 es un permiso faltante.*

**Automatizaciones y conversaciones**

- [ ] Automation → Workflows: confirmar qué hay construido. La expectativa es que **no haya nada**; si aparece algo a medio hacer, hay que revisarlo antes de sumar los nuevos.
- [ ] Conversations: confirmar si el canal de WhatsApp figura conectado y con qué número.
- [ ] Media Library: confirmar que están las tres imágenes de catálogo por evento (Boda, XV y la genérica).
- [ ] Settings → Team: que Oscar tenga acceso con permisos suficientes para editar los Custom Values.

### 8.2 n8n

- [ ] Que el workflow `HPF Inbound Handler` (id `IPO1c36NLzkXrBh9`) esté activo y sea **el único** escuchando el bot de Telegram. *Dos workflows activos sobre el mismo bot hacen que el lead reciba todo duplicado.*
- [ ] Credenciales conectadas y sin errores: `GHL PIT HPF`, `HPF GHL Webhook Auth`, `HPF` (Telegram), `H.F` (OpenAI), `H.F` (Postgres).
- [ ] Confirmar el arreglo del envío de fotos: el nodo `Send Photo (Telegram)` tiene que tener el campo **Photo** cargado. *Es el parámetro que se había perdido.*
- [ ] Nodo `Wait 15s (Debounce)`: que el valor sea **15**, no 0. *En 0 el agente contesta cada globito por separado en vez de agrupar la ráfaga.*
- [ ] Revisar las ejecuciones de los últimos días y mirar cuántas terminaron en error y por qué.
- [ ] Confirmar que el workflow de errores (`ug3m3dSDijXgWZIR`) existe y notifica a alguien. *Si no, las fallas pasan desapercibidas.*
- [ ] Anotar la URL pública del webhook de entrada — hace falta para configurar el workflow de GoHighLevel.

### 8.3 Base de datos (Postgres / Supabase)

- [ ] Que existan las tablas `messages` y `debounce_buffer`.
- [ ] Mirar qué formato tiene el `session_id` de las conversaciones recientes. *Es la llave de la memoria: si cambia entre el canal de prueba y el de producción, los leads que vengan de Kommo pierden su historial.*
- [ ] Limpiar las conversaciones de prueba. **Cuidado:** hay conversaciones de leads reales en la misma tabla. Borrar siempre por la llave exacta del chat de prueba, nunca por prefijo ni por rango de fechas.
- [ ] Mirar el tamaño de las dos tablas y si hace falta purgar.

### 8.4 Meta / WhatsApp — el día del traspaso

- [ ] Confirmar **qué número** se conecta. El de producción (+52 331 594 8670) está activo en Kommo: mientras siga ahí no se puede migrar sin cortar el servicio. Lo recomendado es usar un número secundario para probar y migrar el definitivo recién en el cutover.
- [ ] Que el Business Manager de Happy Flops esté verificado. *Sin verificación hay límites de envío más bajos.*
- [ ] Estado de las plantillas de mensaje: cuáles están cargadas y cuáles aprobadas. **Tardan entre 24 y 72 horas**, así que conviene mandarlas a aprobar cuanto antes: sin plantillas aprobadas no se puede escribir a un lead fuera de la ventana de 24 horas, que es exactamente lo que necesita el reenganche.
- [ ] Nombre para mostrar y foto del perfil de WhatsApp Business.
- [ ] Calificación de calidad del número, si ya tenía historial.
- [ ] **Confirmar que el número no queda conectado en Kommo y en GoHighLevel a la vez.** *Un número solo puede estar en un proveedor; si se migra sin apagar el otro, se cortan los mensajes.*
- [ ] Después de conectar: mandar un mensaje de prueba desde un teléfono cualquiera y confirmar que aparece en Conversations de GoHighLevel. *Si aparece pero el bot no contesta, es porque falta el workflow WF-01 — no es un problema del agente.*

### 8.5 Telegram (el canal de prueba)

- [ ] Confirmar a nombre de quién está el bot y quién tiene el token.
- [ ] Decidir si el canal de prueba se apaga al conectar la WABA o se deja como sandbox. *Si se deja, conviene que apunte a la misma sub-cuenta de GHL o a una de prueba, pero no a las dos a la vez.*

### 8.6 Airtable y Kommo (el sistema que se apaga)

- [ ] **Bajar todos los archivos de los salesbots de Kommo antes de apagar la cuenta.** Fotos de producto, catálogos en PDF, los videos y el PDF con los números de cuenta. **No existen en ningún otro lado.** Es lo más urgente de esta lista: el día que se apague Kommo, se pierden.
- [ ] Confirmar que el catálogo de Airtable (`Productos | Happy Flops`) sigue siendo la fuente del bot viejo y que nadie lo edita esperando que cambie el agente nuevo.
- [ ] Anotar qué queda vivo en Kommo el día del cutover y qué se archiva.

---

## 9. Riesgos conocidos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Los archivos del catálogo viven solo dentro de Kommo | Se pierden todas las fichas de producto al dar de baja la cuenta | Bajarlos ahora, antes de cualquier otra cosa |
| Las claves de los campos personalizados pueden no coincidir | El agente cree que escribe y no escribe, sin ningún error visible | Revisión de 8.1 |
| La deduplicación de contactos puede estar por teléfono | Un contacto nuevo por mensaje | Revisión de 8.1 |
| Conectar la WABA sin construir WF-01 | El número queda conectado y el bot no responde | Construir WF-01 antes o inmediatamente después |
| Los precios del prompt y los de GoHighLevel pueden divergir | El cliente cambia un precio en la interfaz y el agente sigue con el viejo | Decidir si se cablea o se avisa |
| Las plantillas de Meta tardan hasta 72 horas | El reenganche no puede salir hasta tenerlas | Mandarlas a aprobación cuanto antes |
