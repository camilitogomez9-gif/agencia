# Catálogo de Intents — Sistema actual Happy Flops

> **Etapa 1.** Lista cerrada de los casos que el agente Rebeca sabe manejar. Cada intent define: qué dice el lead, qué step lo dispara, qué agente lo procesa, y qué output produce.

---

## 0. Modelo de intents

El agente HPF actual **no tiene un modelo formal de intents** sino una **máquina de pasos** decidida por el Router (AI Agent) con base en memoria + última interacción. Lo que reconstruyo aquí son los "intents efectivos" que el sistema discrimina, derivados de:

- System prompt del Router (357 líneas con casos y ejemplos explícitos)
- System prompts de los 4 agentes especializados
- Conversation samples reales
- Lógica de IFs/Switches en el main workflow

---

## 1. Intents primarios (driven by Router)

### 1.1 `intent.greeting_first_contact`

- **Trigger conversacional:** primer mensaje del lead, sin importar contenido.
- **Detección técnica:** `Exist_Interaction? == false` (no hay historial AI en Postgres).
- **Bypassa al Router** (va directo al Starter).
- **Agente:** `AI Agent Starter`.
- **Output del agente:** mensaje hardcodeado de saludo (3 partes con waits 2s).
- **Ejemplo lead:** `"Hola"`, `"Cuánto cuestan?"`, `"Información"`, `"Buenas"`, *cualquier texto inicial*.

### 1.2 `intent.identify_event`

- **Trigger conversacional:** lead responde con un tipo de evento (Boda / XV / Otros) — eventualmente con typos.
- **Detección técnica:** Router emite `step_2`. Aplica cuando ya se envió saludo (step_1) Y el último mensaje del lead identifica un evento, sin mencionar productos específicos.
- **Agente:** `AI Agent Main Image`.
- **Output:** `{"evento":"<Boda|XV|Otros>", "texto_dinamico":"Qué padre!... 🎉 SEMANA LOCA..."}`.
- **Side-effect:** envía imagen principal del evento + activa Seg. Imagen + mueve a ETAPA 2.

**Variantes de input que clasifica como Boda:**
- `"boda"`, `"bida"`, `"bodda"`, `"bodas de oro"`, `"bodas de plata"`, `"boda en agosto"`.

**Variantes XV:**
- `"XV"`, `"15"`, `"quince"`, `"cumpleaños de 15"`, `"15 años"`, `"cumple de 15"`, `"quinceañera"`.

**Variantes Otros:**
- `"bautizo"`, `"graduación"`, `"primera comunión"`, `"empresarial"`, `"cumpleaños"` (que no sea XV), `"presentación"`, `"fiesta"`, `"ninguno"`, `"otro"`.

**Edge case:** lead responde con evento + producto en el mismo turno (`"XV años, quiero saber el costo de cilindros"`) → Router salta directo a `step_3` (no pasa por step_2).

### 1.3 `intent.request_product_info`

- **Trigger conversacional:** lead menciona uno o más productos por nombre o sinónimo, sin haber visto ese producto antes.
- **Detección técnica:** Router emite `step_3`.
- **Aplica cuando:**
  - Ya hay evento detectado (memoria) **Y**
  - Mensaje contiene nombre de producto válido **Y**
  - Producto no fue mostrado antes (memoria).
- **Agente:** `AI Agent Products`.
- **Output:** `{"evento":..., "subcategoria":..., "productos":[...], "texto_dinamico":"¿Le interesa sumarlos a la cotización?..."}`.
- **Side-effect:** consulta Airtable, envía ficha de cada producto solicitado (loop con waits), mueve a ETAPA 3.

**Productos reconocidos (con sinónimos):**

| Producto canónico | Sinónimos del system prompt |
|-------------------|----------------------------|
| `sandalias` | chanclas, huaraches, chancletas, ojotas |
| `cilindros` | termos, bules, vasos (¡ojo! "vasos" puede confundir con vasos popote) |
| `pantuflas` | satin (porque son pantuflas de satín) |
| `mandiles` | (solo Boda) |
| `anticrudas` | costalitos, costales, kit anticruda |
| `tintas` | colores (cuando se refiere a tintas/diseños) |
| `correas 9` | correas 9MM, correas delgadas |
| `correas 15` | correas 15MM, correas gruesas |
| `tapas termos` | tapas de cilindros |
| `shein` | bolsa shein, bolsa de regalo, bolsa que viene con sandalias |

**Edge cases de step_3:**

- Lead pregunta `"todos"` o `"quiero todos"` después de imagen principal → mostrar todos los productos del evento.
- Lead pregunta sobre un producto que ya se mostró + un producto nuevo → mostrar solo el nuevo.
- Después de upsell, lead responde `"cuanto cuestan?"`/`"como son?"` → mostrar el producto sugerido.
- Lead pregunta `"colores"` solo → step_3 con producto = `tintas` (subcategoria=Accesorios).
- Lead pregunta sobre la bolsita (que mensaje trae) → step_3 con producto = `shein`.

### 1.4 `intent.request_quote_or_business_info`

- **Trigger conversacional:** lead da datos de pedido (cantidad, CP), pregunta sobre negocio (dirección, horarios, métodos de pago, plazos), o avanza con la compra. Producto ya mostrado.
- **Detección técnica:** Router emite `step_4`.
- **Agente:** `AI Agent Recolector` (texto) o `AI Agent Recolector1` (imagen).

**Sub-intents dentro de step_4:** (manejados por el agente vendedor en lenguaje natural, no estructurado)

| Sub-intent | Ejemplo lead | Acción de Recolector |
|------------|--------------|---------------------|
| `quote.calculate` | `"Quiero 50 sandalias gruesas y 50 cilindros, CP 44100"` | Llama tool `CALCULADORA`, devuelve cotización formateada + 7 pasos + upsell |
| `quote.modify_quantity` | `"mejor que sean 100"` | Recalcula cotización (CALCULADORA con nuevas cantidades) |
| `quote.unclear_quantity` | `"Quiero algunas pantuflas"` | Pide cantidad mínima |
| `quote.below_minimum` | `"30 sandalias"` | Recuerda mínimo (50 pares) |
| `payment.request_methods` | `"Cómo pago?"`, `"avancemos"` | Envía URL `url1234.com123` + PDF Métodos de Pago |
| `payment.confirm_advance` | `"Listo, ya pagué"` | Pide comprobante 50% anticipo |
| `business.location` | `"Dónde están?"` | Da dirección Guadalajara + link mapa |
| `business.hours` | `"A qué hora atienden?"` | L-V 9:00–17:30 |
| `business.shipping_company` | `"Por qué paquetería envían?"` | Estafeta / FEDEX / Paquetexpress |
| `business.references` | `"Es estafa? Tienen referencias?"` | Frase fija + link Facebook |
| `business.phone_call` | `"Puedo llamar?"`, `"Tienen un número?"` | Solo `3315948670` (prohibido otros) |
| `business.payment_method` | `"Acepto tarjeta?"` | Solo efectivo/transferencia |
| `product.qa_unitalla` | `"Qué talla?"` | Sandalias unitalla 23-26 mx |
| `product.qa_kit` | `"Qué incluye el kit anticruda?"` | Solo el costal, lo llenan ellos |
| `product.qa_design` | `"Cuántos diseños puedo hacer?"` | 50 pares = 1 diseño, 100 = 2, etc. |
| `product.qa_packaging` | `"Las sandalias vienen en bolsa?"` | Bolsa shein gratis o personalizada $7 |
| `product.qa_concept_transfer` | `"Qué pongo en concepto al transferir?"` | Solo el nombre, nada extra |
| `product.qa_durability` | `"¿Me duran hasta noviembre?"` | Sí, 15 días producción + 2-5 envío |
| `intent.upsell_followup` | (después de cotización) | Sugiere siguiente producto prioritario por evento |
| `intent.silence_response` | `"ok"`, `"gracias"`, `"muy bien"` | "Cualquier duda aquí estoy. Gracias por confiar en HF! ✨" |
| `intent.farewell_loop` | (lead se despide repetidamente) | Responde solo con 👍 |

### 1.5 `intent.product_image_input`

- **Trigger conversacional:** lead envía una imagen.
- **Detección técnica:** `checkType` → `Es PDF?` (no) → `Analyze image3` (clasificar) → `Es Pago?` (no) → `Es producto?` (sí, no es `falso`).
- **Agente:** `AI Agent Recolector1`.
- **Input formateado:** `"Te envio una imagen del producto que quiero: <producto detectado>"`.
- **Output esperado:** elogio del diseño + invita a continuar (`"Es un diseño muy bonito! ¿Quiere continuar con el proceso?"`).

### 1.6 `intent.payment_proof_image`

- **Trigger conversacional:** lead envía imagen que es comprobante de pago.
- **Detección técnica:** `Analyze image` → `Es Pago? == true`.
- **Side-effect:**
  - Si lead en `100395519` (en producción) → mover a `100395523` (pago liquidación) + Telegram.
  - Si lead NO en producción → mover a `91450360` (confirmar pago) + Telegram.
- **No invoca agente conversacional.** El sistema confía en una respuesta automática (presumiblemente la "Foto Vacaciones" si es fuera de horario, o pasa al humano).

### 1.7 `intent.unclassifiable_image`

- **Trigger conversacional:** imagen que no es producto reconocible ni comprobante.
- **Detección técnica:** `Analyze image == falso`, `Es Pago? == false`.
- **Side-effect:** Telegram "imagen no categorizable" + `ATENCION_PERSONALIZADA4` (mover a 91266100, derivar a humano).

### 1.8 `intent.pdf_input`

- **Trigger conversacional:** lead envía un PDF.
- **Detección técnica:** `Es PDF? == true`.
- **Side-effect:** Telegram "Usr. envió PDF" + ATENCION_PERSONALIZADA4 (derivar a humano). _(Inferencia: los PDFs son comprobantes de pago habitualmente.)_

### 1.9 `intent.audio_input`

- **Trigger conversacional:** lead envía audio.
- **Detección técnica:** `checkType` branch 1 → `Get_Audio` → `transcribe voice` (OpenAI Whisper).
- **Procesamiento:** se trata como texto y entra al flujo normal con el contenido transcripto.

---

## 2. Intents secundarios (manejados explícitamente por agentes)

### 2.1 Intents que disparan herramienta `ATENCION_PERSONALIZADA` (deriva a humano)

Definidos en system prompt del Recolector:

| Sub-intent | Trigger |
|------------|---------|
| `personalization.custom_design` | "tengo un diseño propio", "puedo enviar mi logo?" |
| `personalization.specific_character` | "diseño de Frozen", "tema princesa" (excepto si está en catálogo) |
| `delivery.urgent_request` | Fecha del evento < 15 días naturales |
| `quote.special_product` | Termos especiales (novios/quinceañera) |
| `complaint.post_sale` | "no me llegó", "está mal el diseño" |
| `info.unclear_question` | Pregunta que el agente no puede responder con su base |
| `emergency.unknown_situation` | Cualquier consulta fuera de scope |

### 2.2 Intents que disparan herramienta `CALCULADORA` (cálculo de envío)

- Cada vez que se hace una cotización con productos válidos (mínimos cumplidos, cantidad clara, CP claro).
- Variable `cuentas`: string con multiplicaciones `"<cant> x <peso>, <cant> x <peso>,..."`.

**Pesos hardcodeados en system prompt Recolector:**
- Mandiles: 0 kg
- Kits Anticrudas: 0 kg
- Bolsas: 0 kg
- Cilindros: 0.14 kg
- Sandalias Delgadas: 0.15 kg
- Sandalias Gruesas: 0.15 kg
- Pantuflas: 0.15 kg

**Restricciones de empaque:**
- Cilindros: max 250/caja.
- Sandalias: max 200/caja.
- Sandalias + Cilindros: max 200 unid combinadas/caja.
- Peso máximo por caja: 35kg → si supera, dividir en N cajas.

---

## 3. Reglas de prioridad cuando hay ambigüedad

El system prompt del Router define una jerarquía estricta:

1. **Antes que nada, evento.** Si no hay evento detectado (memoria vacía o "Otros" no resuelto), forzar step_1 incluso si el lead pregunta precios.
2. **Después de evento, mostrar imagen principal.** Si lead identificó evento + pidió producto en el mismo turno → step_2 antes (sí, pasa step_2 antes que step_3).  ⚠️ _(Pero los ejemplos del prompt contradicen esto: si lead identifica evento + producto, va directo a step_3 saltando step_2. Esto es ambigüedad — ver 06_redundancias_y_ambiguedades.md.)_
3. **Producto no mostrado antes que cotización.** "Está completamente prohibido y penado de muerte enviar al step_4 una consulta que mencione un producto y no se haya enviado antes al step_3" (literal del prompt).
4. **Múltiples productos en consulta:** mostrar solo los no mostrados.
5. **Upsell:** si el agente acaba de sugerir un producto y el lead pregunta info, identificar el producto sugerido en memoria y mandar al step_3 con ese producto.

---

## 4. Intents NO soportados (por design)

El sistema **no maneja** los siguientes intents, todos van al humano:

- Diseños personalizados con archivo (logo del cliente).
- Modificación de pedido ya pagado.
- Reclamos / quejas.
- Consultas técnicas específicas no incluidas en la base de conocimiento.
- Pedidos urgentes (< 15 días producción).
- Consultas de productos fuera del catálogo (ej. "¿venden tazas?").
- Negociación de precios (regla crítica: no ceder).

---

## 5. Mapping rápido intent → componente n8n

| Intent | Disparador en n8n | Resultado |
|--------|-------------------|-----------|
| greeting_first_contact | `Exist_Interaction? == false` | AI Agent Starter |
| identify_event | Router → `step_2` | AI Agent Main Image |
| request_product_info | Router → `step_3` | AI Agent Products |
| request_quote_or_business_info | Router → `step_4` | AI Agent Recolector |
| product_image_input | `Es producto? == sí` | AI Agent Recolector1 |
| payment_proof_image | `Es Pago? == true` | PATCH Kommo + Telegram |
| unclassifiable_image | `Es producto? == no` && `Es Pago? == false` | ATENCION_PERSONALIZADA4 + Telegram |
| pdf_input | `Es PDF? == true` | ATENCION_PERSONALIZADA1 + Telegram |
| audio_input | `checkType` branch 1 | Whisper + flujo de texto |
| custom_design / urgent / etc. | Tool call dentro de Recolector | Sub-workflow ATENCION_PERSONALIZADA |
| calculate_quote | Tool call dentro de Recolector | Tool CALCULADORA (sub-workflow) |
