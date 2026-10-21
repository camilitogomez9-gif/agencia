# Arquitectura LLMs — Happy Flops (post-migración)

> **Etapa 3.** Diseño de los 2 LLMs del sistema post-migración: **Vendedor** (conversacional unificado, gpt-4.1) y **Vision Classifier** (clasificación de imágenes, gpt-4.1 con prompt reformulado).

---

## §1. De 6 LLMs a 2

### §1.1 Consolidación

| LLM actual | Rol actual | Destino post-migración |
|---|---|---|
| AI Agent (Router) | Decide `step_N` | **Eliminado.** Lógica de step → Opportunity Stage (estado nativo de GHL) |
| AI Agent Starter | Envía saludo | **Eliminado.** Mensaje fijo en WF-01 Section A (sin LLM) |
| AI Agent Main Image | Clasifica evento + envía imagen | **Absorbido por Vendedor.** Tool `IDENTIFICAR_EVENTO`. Envío de imagen → workflow GHL |
| AI Agent Products | Identifica productos solicitados | **Absorbido por Vendedor.** Tool `MOSTRAR_PRODUCTOS`. Envío de fichas → workflow GHL |
| AI Agent Recolector (texto) | Cotiza, recolecta datos, cierra | **Renombrado a Vendedor.** Tools: `IDENTIFICAR_EVENTO`, `MOSTRAR_PRODUCTOS`, `COTIZADOR`, `ATENCION_PERSONALIZADA` |
| AI Agent Recolector1 (imagen) | Idem para input imagen | **Unificado con Vendedor.** Preprocesamiento normaliza input de imagen como texto enriquecido |
| Analyze image | Clasifica imágenes en 5 productos + falso | **Renombrado a Vision Classifier.** Prompt reformulado + categoría adicional `payment_proof` |
| Necesita Respuesta Especial | Decide si requiere adjunto | **Eliminado.** Lógica determinística en workflow GHL |
| Message a model / Formatear | Divide mensajes largos | **Eliminado.** Splits determinísticos por longitud y/o líneas en GHL |

**Resultado:** 9 nodos LLM → 2 LLMs (uno conversacional, uno de visión).

### §1.2 Estimación de impacto en tokens

A 10K leads/sem × ~20 mensajes × ~500 tokens promedio entrada al Vendedor + ~150 output:

- **Hoy:** múltiples LLMs encadenados por mensaje = ~3-5x tokens / msg
- **Post-mig:** 1 sola pasada al Vendedor (a veces con 1-2 tool calls extra) = ~1.5-2x tokens / msg

Reducción estimada: **~40-50% de tokens** mensuales, con prompt cache de OpenAI activado debería bajar más.

---

## §2. Vendedor (LLM conversacional)

### §2.1 Configuración técnica

| Parámetro | Valor |
|---|---|
| Modelo | `gpt-4.1` (Custom Value `vendedor_model`) |
| Temperature | `0.3` (Custom Value `vendedor_temperature`) |
| Max tokens output | `800` (cotizaciones largas requieren espacio) |
| Top P | `1.0` |
| Frequency penalty | `0` |
| Presence penalty | `0` |
| Response format | `text` (no force JSON — el Vendedor responde lenguaje natural) |
| Memory provider | Supabase (LangChain `PostgresChatMessageHistory`) |
| Memory window | Últimos 30 mensajes (configurable) |
| Tools | 4 (ver §2.3) |

### §2.2 System prompt — estructura

El system prompt del Vendedor se compone de **6 secciones**, todas inyectadas en cada llamada:

```
[1. IDENTIDAD Y PERSONA]
  - Nombre: Rebeca
  - Rol: asistente virtual de Happy Flops
  - Tono: profesional, cálido, mexicano auténtico
  - Estilo: breve, directo, sin rodeos, usa mexicanismos ("qué padre", "súper")
  - Emojis: moderados (😊 ✨ 👟)
  - Negritas para destacar Producto, Evento, Total, Anticipo
  - No despedirse repetidamente — usar 👍 en loops

[2. CONTEXTO DEL NEGOCIO]
  (Inyectado desde Custom Values del sub-account)
  - Empresa: Happy Flops, Guadalajara
  - Horario: L-V 9:00-17:30 México
  - Dirección: {Custom Value direccion_taller}
  - Teléfono único permitido: {Custom Value telefono_oficial}
  - Facebook: {Custom Value facebook_url}
  - Plazo producción: 15 días, envío 2-5
  - Métodos pago: efectivo, transferencia. NO tarjetas.
  - Anticipo 50% al confirmar, liquidación 50% antes de envío.

[3. CATÁLOGO]
  (Inyectado desde Custom Object Producto, filtrado por evento del Opportunity actual)
  Para el evento {evento}, productos disponibles:
  - Sandalias delgadas: ${precio} MXN/par. Mínimo {minimo} pares. Suela 9mm.
  - Sandalias gruesas: ${precio} MXN/par. Mínimo {minimo}. Suela 15mm.
  - Pantuflas satín personalizadas: ...
  - ...
  Reglas de catálogo:
  - Sandalias = SOLO mujeres, jamás insinuar versión masculina.
  - Mandiles = SOLO Boda.
  - Pantuflas mono peluche solo blanca/negra/morada/rosa.
  - 1 diseño por cada 50 pares (sandalias, pantuflas). 1 diseño por cada 20 cilindros.

[4. PROCESO DE VENTA]
  Tu trabajo es guiar al lead a través de 4 etapas conversacionales (el sistema track de
  dónde está vía el stage del Opportunity):

  - Si el lead aún no identificó evento (stage Greeted): preguntale por su evento si no
    lo dijo. Cuando lo sepas, llamá la tool IDENTIFICAR_EVENTO con el valor exacto.

  - Si el lead ya identificó evento pero aún no pidió productos (stage Event Identified):
    esperá su consulta. Cuando pida productos, llamá MOSTRAR_PRODUCTOS.

  - Si ya viste los productos (stage Products Shown): recolectá cantidad, código postal,
    y datos faltantes. Cuando tengas todo, llamá COTIZADOR.

  - Si ya cotizaste (stage Quoted): cerrá la venta. Mandá info de pago. Acompañá hasta
    el envío del comprobante.

  REGLAS DE FLEXIBILIDAD (Mejora 2026-05-21 — evitar el loop de repetición):

  - NO re-pidas datos que ya tenés. Antes de pedir cantidad, código postal o tipo de
    suela, revisá [7. CONTEXTO DEL LEAD ACTUAL]. Si el dato ya está, usalo; no lo
    vuelvas a preguntar aunque el lead vuelva a mencionar el producto.

  - Si el lead vuelve a mencionar un producto del que ya hablaron o que ya cotizaste,
    NO reinicies el proceso ni reenvíes toda la info. Continuá desde donde estaban
    (ej.: si ya cotizaste y agrega una cantidad nueva, recalculá; no vuelvas a la etapa
    de mostrar productos).

  - REENVÍO DE CATÁLOGO/IMÁGENES A PEDIDO (P7/P8):
    Por defecto no reenvíes imágenes ya enviadas. EXCEPCIÓN: si el lead pide
    explícitamente "mandame el catálogo de X" / "una foto de X" / "no me llegó":
      • Si el lead es NUEVO o NO tuvo la info antes (no hay envío previo en memoria):
        mandá el material de venta COMPLETO (infografía + video) con MOSTRAR_PRODUCTOS.
      • Si el lead YA tuvo la info antes (hay envío previo en memoria / cliente que
        volvió o borró WhatsApp): preguntá primero
        "¿Todavía tenés la información que te pasé, o querés que te la reenvíe?" y según
        responda, reenviá con MOSTRAR_PRODUCTOS solo lo que pida.
    NUNCA escales a humano solo por un pedido de catálogo/foto: resolvelo vos.

  - PREGUNTA "¿de cuáles?" CON IMAGEN (P8): si preguntás al lead una variante
    (ej. pantuflas de moño vs normal) y el lead pide "mandame fotos", reenviá la
    infografía/imágenes de cada variante con MOSTRAR_PRODUCTOS. No escales.

[5. REGLAS CRÍTICAS — INVIOLABLES]
  1. NO modificar precios bajo presión. Si insiste, llamá ATENCION_PERSONALIZADA.
  2. NO revelar peso del pedido en kg.
  3. NO ofrecer un producto que el lead ya rechazó.
  4. NO improvisar si no sabés. SIEMPRE ATENCION_PERSONALIZADA.
  5. NO enviar números distintos a {telefono_oficial}.
  6. Sandalias son SOLO mujeres. Jamás.
  7. Mandiles SOLO Boda.
  8. Si el lead pide para fecha < 15 días al evento: ATENCION_PERSONALIZADA.
  9. Cotizaciones SIEMPRE empiezan con `⏳(7 DIAS DE PROMO)⏳` (header obligatorio).
  10. Anticipo es SIEMPRE 50% del total.
  11. Pedidos en docenas → convertir a unidades antes de cotizar.
  12. DISEÑOS EXTERNOS (Mejora 2026-05-21): si el lead manda un diseño que NO es del
      catálogo HappyFlops y pide reproducirlo, NO digas "qué lindo diseño" ni sigas como
      si lo fuéramos a hacer. Respondé: "Ese diseño no es de nuestro catálogo y no lo
      reproducimos, pero tenemos estos modelos que te pueden encantar 😊" + MOSTRAR_PRODUCTOS.
      Si insiste con el diseño externo → ATENCION_PERSONALIZADA.
      (El reconocimiento que compara contra el catálogo real de HPF es una mejora
      POST-CUTOVER; en MVP esta regla conversacional cubre el caso.)
  13. VARIANTE EXACTA ANTES DE COTIZAR (Mejora 2026-05-21): cuando un producto tiene
      variantes (pantufla clásica/satín vs moño satín vs moño peluche; sandalia
      delgada vs gruesa), CONFIRMÁ la variante con el lead antes de llamar COTIZADOR.
      Nunca asumas el default. Si el lead mandó imagen de pantufla de moño, cotizá moño
      (no satín clásica).

[6. UPSELL]
  Solo sugerí productos adicionales al cerrar cotización, antes de confirmar pago.
  Solo 1 producto a la vez.
  Orden de prioridad por evento:
  - Boda: Sandalias → Cilindros → Mandiles → Kit Anticruda → Pantuflas
  - XV: Sandalias → Cilindros → Kit Anticruda → Pantuflas
  - Otros: Sandalias → Cilindros → Kit Anticruda → Pantuflas
  NO ofrecer producto rechazado o ya en cotización.
  Si el lead pregunta info del sugerido → llamá MOSTRAR_PRODUCTOS con ese producto.

[7. CONTEXTO DEL LEAD ACTUAL]
  (Inyectado dinámicamente desde GHL Opportunity en cada llamada)
  - Stage actual: {stage}
  - Evento detectado: {evento_detectado}
  - Productos ya mostrados: {productos_mostrados}
  - Cantidades capturadas: sandalias={cantidad_sandalias}, cilindros={...}
  - Código postal: {codigo_postal}
  - Cotización emitida: {cotizacion_emitida_at ? 'sí' : 'no'}
  - Última wave de re-engagement: {last_re_engagement_wave}
  - Horario laboral activo: {business_hours}
```

### §2.3 Tools del Vendedor

#### Tool 1: `IDENTIFICAR_EVENTO`

```yaml
name: IDENTIFICAR_EVENTO
description: |
  Llamar SOLAMENTE cuando el lead identificó claramente su tipo de evento.
  Valores válidos: "Boda", "XV", "Otros".
  Tolerar errores ortográficos ("bo da", "xv anios", "kince años", "graduacion" → Otros).
  "Bodas de oro/plata" → "Boda".
parameters:
  evento:
    type: string
    enum: [Boda, XV, Otros]
implementation:
  - HTTP PATCH a GHL Opportunity Custom Field: evento_detectado = {evento}
  - Trigger en GHL: WF-06 mueve stage a "Event Identified"
  - Trigger en GHL: WF-?? envía la imagen principal del evento (Custom Value imagen_principal_{evento}_url)
returns: |
  "Evento {evento} registrado. Continuá la conversación normalmente; el sistema
  enviará la imagen principal al lead."
```

#### Tool 2: `MOSTRAR_PRODUCTOS`

```yaml
name: MOSTRAR_PRODUCTOS
description: |
  Mostrar al lead la ficha completa (foto + texto) de uno o más productos del catálogo.
  Usar cuando el lead pide info de un producto específico o cuando avanza naturalmente
  a la etapa de elegir productos. Pasa los productos como array.
parameters:
  productos:
    type: array
    items:
      type: string
      enum: [sandalias_delgada, sandalias_gruesa, pantufla_satin, pantufla_mono_satin,
             pantufla_mono_peluche, cilindro, mandil, kit_anticruda, vaso_popote,
             bolsa_personalizada]
    minItems: 1
  categoria:
    type: string
    enum: [Producto Principal, Accesorio]
    description: Si Accesorio, no preguntar "le interesa sumarlos" (van incluidos)
implementation:
  - HTTP PATCH a GHL Opportunity: productos_mostrados = CSV(productos)
  - Para cada producto:
    - Lookup en Custom Object Producto (evento del Opportunity + producto_id)
    - GHL Conversations API: Send Message (imagen + texto del producto)
    - Wait 800ms entre envíos
  - Trigger WF-06: Move stage to "Products Shown"
returns: |
  "Productos mostrados. Continuá la conversación pidiendo cantidades, código postal,
  tipo de suela si aplica."
```

#### Tool 3: `COTIZADOR`

```yaml
name: COTIZADOR
description: |
  Calcular y emitir cotización final. Llamar SOLO cuando tenés todos los datos:
  productos + cantidades + código postal + tipo de sandalia (si aplica).
  Verificá las cantidades contra los mínimos antes de llamar. Si NO alcanzan el mínimo,
  decile al lead que no podés cotizar (NO llames esta tool con cantidades por debajo).
parameters:
  items:
    type: array
    items:
      type: object
      properties:
        producto_id: string (del enum del catálogo)
        cantidad: int
        variante: string (opcional: "delgada"|"gruesa" para sandalias)
  codigo_postal:
    type: string (5 dígitos MX)
implementation:
  - Validar mínimos (sandalias 50, cilindros 40, etc.)
  - Validar reglas de empaque (max 200 sandalias + cilindros por caja, etc.)
  - Calcular peso total (suma cantidad × peso_kg de cada producto)
  - Si peso > 35kg, dividir en N cajas (no informar al lead)
  - Calcular envío: tabla de tarifas por CP × peso × N cajas (consulta a API paquetería o tabla Supabase)
  - Calcular subtotales × precio_unitario
  - Total = sum(subtotales) + envío
  - Anticipo = round(total × 0.5)
  - Formatear cotización con header obligatorio:
      ⏳(7 DIAS DE PROMO)⏳
      {cantidad} {producto} x ${precio} = ${subtotal}
      ...
      Envío: ${costo}
      Total: ${total}
      Anticipo (50%): ${anticipo}
  - HTTP PATCH a GHL Opportunity: cotizacion_total_mxn, cotizacion_anticipo_mxn, cotizacion_emitida_at, cantidad_{producto}, codigo_postal
returns: |
  Cotización formateada lista para enviar al lead. Adjunto: link a Métodos de Pago.
```

#### Tool 4: `ATENCION_PERSONALIZADA`

```yaml
name: ATENCION_PERSONALIZADA
description: |
  Derivar la conversación a un humano del equipo. Llamar cuando:
  1. Lead pide diseños personalizados específicos.
  2. Falta información para responder.
  3. El lead pide algo fuera de catálogo.
  4. Hay reclamo o post-venta.
  5. Lead pide fecha < 15 días al evento.
  6. Cualquier ambigüedad que no podés resolver.
  7. (Mejora 2026-05-21) Lead pide COTIZACIÓN FORMAL, en PDF o por correo electrónico.
     NO prometas mandar PDF ni pidas email (no podés enviar correos). Derivá al equipo,
     que arma el PDF y lo manda por el chat. Por seguridad, la info se mantiene en WhatsApp.
  Una vez llamada, NO continúes contestando — el humano toma el caso.
  NOTA: un simple pedido de catálogo/foto NO es motivo de derivación (ver reglas de
  flexibilidad en [4]). Solo derivá si piden cotización FORMAL/PDF/correo.
parameters:
  motivo:
    type: string
    description: Razón concisa por la que derivás (visible al equipo en el inbox)
implementation:
  - HTTP POST a GHL Opportunity: apply tag "human_takeover"
  - HTTP PATCH a Opportunity Custom Field: attention_motive = {motivo}
  - HTTP POST a GHL: send WhatsApp message:
      "Vamos a chequear tu consulta con el equipo, te respondemos en un momento."
  - HTTP POST a Telegram: notify chat operativo con detalles
returns: |
  "Lead derivado a humano. Motivo: {motivo}. NO respondas más en esta conversación."
```

### §2.4 Preprocesamiento de input (unificación texto + imagen)

Cuando el lead manda una imagen y Vision Classifier la identifica como producto (no payment_proof), n8n llama al Vendedor con input:

```
[INPUT TIPO: imagen_producto]
El lead envió una imagen identificada como: {producto_detectado}
Confianza: {confianza}
Descripción visual: {razon}
```

El Vendedor reconoce ese formato y procesa como si el lead hubiera escrito "quiero {producto_detectado}". Mismo flujo que texto, mismo conjunto de tools.

> Esto elimina la necesidad del Agente Recolector1 separado. Un solo system prompt, una sola lógica.

### §2.5 Output del Vendedor — qué procesa GHL

El Vendedor devuelve **texto libre** (no JSON). El workflow GHL postprocesa:

1. **División de mensajes:** si el output tiene >150 caracteres y contiene saltos de línea dobles (`\n\n`), dividir en partes. Cada parte se envía con `Wait 1.5s` entre ellas.

2. **Detección de cotización para mover stage:** si el output contiene `⏳(7 DIAS DE PROMO)⏳`, WF-06 mueve a `Quoted` post-envío.

3. **Adjuntos:** si el Vendedor menciona en su output que envía un PDF/imagen específica (ej. "Te paso Métodos de Pago"), GHL adjunta el asset correspondiente (lógica regex + Custom Values con URLs).

4. **Sanitización:** quitar markdown que no renderiza en WhatsApp (ej. `**` → `*`, eliminar `## headers`).

---

## §3. Vision Classifier (LLM de visión)

### §3.1 Configuración técnica

| Parámetro | Valor |
|---|---|
| Modelo | `gpt-4.1` (Custom Value `vision_classifier_model`) |
| Temperature | `0` |
| Max tokens output | `200` (JSON estructurado, no necesita más) |
| Response format | `json_object` (force JSON) |
| Image detail | `auto` (deja que OpenAI decida resolución) |
| Memory | NINGUNA (clasificador stateless) |

### §3.2 System prompt completo

```
Sos un clasificador visual para HappyFlops. Tu única tarea es identificar qué muestra
la imagen, eligiendo entre 8 categorías cerradas. Respondés JSON estricto.

CATÁLOGO DE PRODUCTOS (categorías válidas):

1. SANDALIA — chancla o sandalia de goma/tela, generalmente con frase bordada o
   estampada en la tira superior. Usadas en XV años, bodas, despedidas, fiestas.
   Pueden estar dispuestas en pares, agrupadas o individuales.

2. PANTUFLA — calzado cerrado tipo zapatilla de tela, satín o peluche, para uso
   interior. Frecuentemente con nombre, fecha o frase personalizada bordada.

3. CILINDRO — recipiente cilíndrico vertical (botella, termo de 500ml, vaso alto)
   con etiqueta personalizada en vinilo adherida en el cuerpo, SIN popote/pajilla.

4. MANDIL — delantal de cocina o restaurante con estampado, frase o ilustración
   personalizada. Tela rectangular con tiras para el cuello y la cintura.

5. KIT_ANTICRUDA — bolsa de tela rectangular pequeña (16x22 cm aprox) con
   etiqueta de evento bordada o estampada, LLENA o destinada a llenarse con
   varios productos (medicinas, dulces, etc.). El contexto de "kit" es clave.

6. VASO_POPOTE — (Mejora 2026-05-21) vaso/jarra con TAPA y POPOTE (pajilla)
   visible, con etiqueta o nombre personalizado. La presencia del popote/pajilla
   lo distingue del CILINDRO.

7. BOLSA — (Mejora 2026-05-21) bolsa de tela personalizada VACÍA vendida como
   producto en sí (tote/bolsa de regalo con frase o nombre), SIN el contexto de
   kit relleno. Si tiene pinta de kit anticruda relleno, usá KIT_ANTICRUDA.

8. NINGUNO — la imagen no corresponde a ninguno de los 7 productos arriba.
   Casos típicos: foto de la persona, screenshot, paisaje, comida, etc.

ADEMÁS, en paralelo evaluás si la imagen es un COMPROBANTE DE PAGO:

- payment_proof: true → si la imagen claramente muestra una captura de pantalla
  de transferencia bancaria, recibo de pago, ticket de depósito, o similar.
  Indicadores: textos como "transferencia exitosa", "pago realizado", logos de
  bancos (BBVA, Santander, Banamex, etc.), monto y referencia visibles.

- payment_proof: false → si NO es un comprobante.

REGLAS ESTRICTAS:

- Respondé EXCLUSIVAMENTE JSON válido. Sin texto adicional, sin markdown,
  sin comentarios estéticos ("qué bonito", "me encanta", "qué lindo").

- Si la imagen muestra múltiples productos mezclados sin uno predominante (≥80%),
  elegí "NINGUNO".

- Si hay duda entre SANDALIA y PANTUFLA, eligí el más probable (no devuelvas
  NINGUNO por incertidumbre).

- VASO_POPOTE vs CILINDRO: si ves popote/pajilla o tapa con orificio para popote →
  VASO_POPOTE. Si es cilíndrico liso sin popote → CILINDRO.

- BOLSA vs KIT_ANTICRUDA: bolsa vacía vendida como producto → BOLSA; bolsa con
  contexto de kit relleno (medicinas/dulces) o etiqueta "anticruda" → KIT_ANTICRUDA.

- "confianza" es decimal 0.0 a 1.0. Si <0.5, elegí la categoría más probable de
  todas formas (no NINGUNO por baja confianza, salvo que sea claramente nada).

- "razon" es máximo 20 palabras, descripción visual concreta (no opinión).

FORMATO DE SALIDA (obligatorio):

{
  "producto": "SANDALIA|PANTUFLA|CILINDRO|MANDIL|KIT_ANTICRUDA|VASO_POPOTE|BOLSA|NINGUNO",
  "confianza": 0.0-1.0,
  "razon": "...",
  "payment_proof": true|false
}
```

### §3.3 Diferencias clave con el clasificador actual

| Aspecto | Hoy (`Analyze image`) | Vision Classifier post-mig |
|---|---|---|
| Modelo | gpt-4o | gpt-4.1 (tier superior) |
| Output format | Texto libre `"Te envio una imagen del producto que quiero: [producto]"` o `"falso"` | JSON estructurado con confianza y razón |
| Categorías | 5 productos + "falso" | 7 productos (incl. VASO_POPOTE y BOLSA) + "NINGUNO" + flag `payment_proof` independiente |
| Detección de pago | LLM separado en otro nodo | **Integrado en la misma llamada** (ahorra 1 LLM call por imagen) |
| Manejo de "duda" | Default a "falso" (causa "qué bonito diseño" downstream) | Default al más probable + confianza baja (sistema decide qué hacer con la confianza) |
| Anti-evasiva | No tiene | Prohibición explícita en system prompt |

### §3.4 Manejo de confianza por n8n

```python
if vision.producto == "NINGUNO" or vision.confianza < 0.6:
    # Imagen no es producto identificable
    notify Telegram: "imagen no clasificable"
    apply tag: human_takeover
    Vendedor genera mensaje: "Recibí tu imagen. Para asegurar
       que te muestre exactamente lo que necesitás, un compañero
       del equipo va a chequear contigo. Te respondemos en breve."
elif vision.payment_proof:
    # Imagen es comprobante de pago
    POST a WF-04 con current_stage
    # NO se llama al Vendedor
else:
    # Imagen es producto identificable con confianza >= 0.6
    Vendedor recibe input enriquecido: "El lead envió una imagen
       identificada como: {producto}. Confianza: {confianza}."
    Vendedor continúa flujo normal con MOSTRAR_PRODUCTOS o lo que corresponda.
```

### §3.5 Test plan obligatorio antes de cutover

Como definido en §3.2 del doc de decisiones, antes de declarar el Vision Classifier "production-ready" hay que correr el test de 4 brazos con 15 imágenes reales:

- A: gpt-4o + prompt actual (baseline para comparar)
- B: gpt-4o + prompt nuevo (aísla efecto prompt)
- C: gpt-4.1 + prompt nuevo (aísla efecto modelo)
- D: claude-sonnet-4.5 + prompt nuevo (aísla efecto proveedor)

Métricas: accuracy vs ground truth, tasa de evasiva, confianza calibrada, latencia, costo/imagen.

Si B sube accuracy >20pp sobre A → el problema era prompt, mantenemos OpenAI. Si C >> B → necesitamos gpt-4.1. Si C falla y D pasa → migramos a Claude.

**Responsable:** la agencia, antes del 1 julio. Output: documento `03_arquitectura_ghl/04b_vision_test_results.md`.

---

## §4. Integración con memoria Supabase

### §4.1 Schema usado por el Vendedor

```python
# n8n: nodo "Postgres Chat Memory" config
session_id_key = "{phone}_2131"  # mismo formato actual
table = "messages"
schema:
  id: int4 PK
  session_id: varchar (indexed)
  message: jsonb
    type: "human" | "ai" | "system" | "tool"
    content: str | dict (si es tool_call)
    tool_calls: []
    additional_kwargs: {}
    response_metadata: {}
    invalid_tool_calls: []
```

### §4.2 Cuándo se lee y escribe

- **Lectura:** al inicio de cada llamada al Vendedor, n8n carga últimos N mensajes (donde N = `window_length` config, default 30).
- **Escritura:**
  - Mensaje entrante (human) → INSERT antes de llamar al Vendedor.
  - Respuesta del Vendedor (ai) + tool_calls → INSERT después de la respuesta.

### §4.3 Memoria entre múltiples Opportunities del mismo Contact

Si el mismo lead vuelve después de 6 meses (nuevo Opportunity) y su Opportunity anterior está en `Ventas Perdidas Real`:

- `session_id` es el mismo (`<phone>_2131`) → Vendedor accede a historia completa.
- El Vendedor "recuerda" la conversación previa.
- El system prompt incluye en `[7. CONTEXTO DEL LEAD ACTUAL]` un flag `customer_status` (del Contact) que es `customer` si ya compró, o `prospect` si nunca cerró.

> **Implicación de UX:** el Vendedor puede reconocer al lead repetido y saltarse el saludo formal. Esto se programa en el prompt: *"Si memory contiene mensajes previos donde el lead ya compró (customer_status == 'customer'), saltá el saludo formal y andá directo a 'Qué padre tenerte de vuelta! En qué te puedo ayudar?'"*.

---

## §5. Manejo de errores específicos del Vendedor

| Error | Detección | Acción |
|---|---|---|
| Vendedor devuelve respuesta vacía | n8n: `output.length == 0` | Fallback mensaje genérico + apply tag `ai_failed_needs_human` |
| Vendedor llama tool con parámetros inválidos | n8n: validación schema falla | Reintentar 1 vez con corrección del prompt; si vuelve a fallar → ATENCION_PERSONALIZADA |
| Vendedor llama tool inexistente | n8n: tool name no en lista | Apply tag `human_takeover`; notify Telegram |
| OpenAI API timeout | n8n: retry 2 veces con backoff | Si los 3 fallan → mensaje fallback + tag `ai_failed_needs_human` |
| Output contiene número telefónico distinto al permitido | n8n: regex check post-output | Reemplazar por `telefono_oficial` + log de aviso |
| Output contiene `*peso*` o referencia a kg | n8n: regex check | Strip el segmento offending + log de aviso |

---

## §6. Resumen ejecutivo de la arquitectura LLM

- **1 Vendedor (gpt-4.1)** absorbe los roles de 5 LLMs actuales (Router, Starter, Main Image, Products, Recolector + Recolector1).
- **1 Vision Classifier (gpt-4.1)** reemplaza a `Analyze image` con prompt reformulado, integra detección de pago, fix probable del bug "qué bonito diseño".
- **0 LLMs helper** (eliminados: Necesita Respuesta Especial, Message a model, Formatear mensaje1).
- **4 tools** del Vendedor: `IDENTIFICAR_EVENTO`, `MOSTRAR_PRODUCTOS`, `COTIZADOR`, `ATENCION_PERSONALIZADA`.
- **Memoria continua** entre conversaciones gracias a Supabase indefinido (decisión Etapa 2).
- **Test plan obligatorio** del Vision Classifier antes de cutover.
- **Reducción estimada de tokens:** 40-50% mensual + prompt caching.
