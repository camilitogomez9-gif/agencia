# Catálogo de Mensajes — Sistema actual Happy Flops

> **Etapa 1.** Inventario completo de mensajes salientes que el sistema puede enviar al lead, agrupados por origen y disparador. Esta es la base de paridad funcional para la migración: todo mensaje aquí debe poder reproducirse en GHL.

---

## 1. Categorías de mensajes

| Categoría | Origen | Modificable por IA |
|-----------|--------|--------------------|
| **A. Hardcodeados literales** | System prompts (n8n) | ❌ Prohibido modificar |
| **B. Templates con variables** | System prompts | ✅ Llena slots |
| **C. Catálogo Airtable** | Tablas Airtable | ❌ Salesbot envía tal cual |
| **D. Generados por LLM** | Recolector + Recolector1 | ✅ Texto libre dentro de reglas |
| **E. Seguimientos automáticos** | Sub-workflows (salesbots) | ❌ Pre-configurados en Kommo |
| **F. Notificaciones operativas** | Telegram | ❌ Mensajes fijos al equipo |

---

## 2. Categoría A — Mensajes hardcodeados literales

### A.1 Saludo de bienvenida (Starter)

**Disparador:** primer contacto del lead (`Exist_Interaction == false`).

**Mensaje (split en 3 partes con waits 2s):**

```
Hola! gracias por escribir a Happy Flops, me llamo Rebeca soy un asistente virtual, yo le estaré atendiendo con gusto ☺️🙋‍♀

Me podría decir de que es su evento? 

🤵👰 - Boda
🎂🥳 - XV Años
👼🏢 - Otros
```

**Restricción:** "El mensaje no puede ser modificado bajo ninguna circumstancia. El mensaje tampoco puede ser adaptado a ningún contexto ni modificado."

### A.2 Mensaje promo de 7 días (Main Image)

**Disparador:** lead identificó evento → step_2.

**Mensaje fijo (acompaña a la imagen del catálogo):**

```
Qué padre! 😊  
🎉 *¡SEMANA LOCA DE PROMOS! SOLO 7 DÍAS PARA LLEVARTE TUS RECUERDITOS PERSONALIZADOS CON DESCUENTAZO* 🎉
*(Pedidos solo para eventos 2026 por tema de tiempos)*
```

**Restricción:** "Incluye DE FORMA FIJA EL SIGUIENTE MENSAJE".

### A.3 Mensaje de los 7 pasos (Recolector)

**Disparador:** Recolector emite cotización por primera vez.

**Mensaje fijo:**

```
*¡HAZ TU PEDIDO EN 7 SENCILLOS PASOS!*🚀
 
1. *COTIZACION de los PRODUCTOS que requiere para su PEDIDO*
2. Se requiere del *50% de ANTICIPO* para desarrollar los diseños.
3. *Elige tu DISEÑO favorito* 🎨 y proporciona los *DATOS* que deseas incluir.
4. Mandamos la *MUESTRA DIGITAL* para tu aprobación o cambios ✏️.
5. Una vez *AUTORIZADO, COMENZAMOS LA PRODUCCION*, son *15 DIAS EN PRODUCCION*. 🛠️.
6. Al terminar, te enviamos una *FOTO DEL PRODUCTO* para que confirmes que todo está perfecto 📸.
7. Hace el *PAGO FINAL* y te enviamos tu pedido 🚚 (tiempo de paquetería: 2 a 5 días).
```

**Restricción:** "Este mensaje envialo completo y una vez por conversación, sin informacion faltante."

### A.4 Mensaje sustituto post-7-pasos

**Disparador:** Recolector emite cotización N+1 (ya envió los 7 pasos antes).

**Mensaje fijo:**

```
Le gustaría avanzar con el pedido? Así le paso los números de cuenta para que pagues el anticipo.
```

### A.5 Mensaje de upsell (Recolector)

**Template:**

```
Mira, ya que pides [producto pedido], ¿le gustaría agregar [producto prioritario] para su evento? ¡Son un hit en [evento elegido]! ✨
```

**Variables:** `[producto pedido]`, `[producto prioritario]`, `[evento elegido]`. La selección de producto prioritario sigue la lista del prompt:
- Boda: Sandalias → Cilindros → Mandiles → Kit Anticruda → Pantuflas
- XV: Sandalias → Cilindros → Kit Anticruda → Pantuflas
- Otros: Sandalias → Cilindros → Kit Anticruda → Pantuflas

### A.6 Pregunta sobre pago (Recolector)

**Disparador:** lead pregunta cómo pagar / "avancemos" / "confirmé pedido".

**Mensaje:**

```
url1234.com123, Súper fácil! 😊 Aquí tienes toda la info para el pago. Por favor, envíanos el comprobante del 50% de anticipo cuando lo tengas. Cualquier duda, me dices! ✨
```

**Side-effect:** la presencia de `.com123` en el output dispara `File_Not_Required` → envío de PDF Métodos de Pago.

### A.7 Cierre de venta (Recolector)

**Mensaje:**

```
url1234.com123, Genial! 😊 Por favor, envíanos el comprobante del 50% de anticipo para seguir con el proceso. Aquí estoy para cualquier duda! ✨
```

### A.8 Respuesta a "ok" / silencio del lead

**Disparador:** después de cierre, lead responde con frases vacías.

**Mensaje:**

```
Cualquier duda o cambio, aquí estoy para ayudarte. Gracias por confiar en Happy Flops! ✨
```

### A.9 Respuesta a referencias / "es estafa?"

**Mensaje:**

```
Estamos ubicados en Guadalajara y hacemos envíos a todo México 📦
Contamos con referencias de confianza. ¡No dudes en preguntar!

Visítanos en Facebook
https://www.facebook.com/happyflops
```

### A.10 Respuesta a "qué paquetería usan?"

**Mensaje:**

```
Depende de la dirección, pero, trabajamos con ESTAFETA, FEDEX y PAQUETEXPRESS, la que llegue sin problema al domicilio y sea las más económica
```

### A.11 Pregunta por número telefónico

**Mensaje:**

```
3315948670
```

**Restricción:** "Tienes terminantemente prohibido enviar cualquier número de contacto que no sean exactamente los previamente indicados."

### A.12 Loop de despedida (👍)

**Disparador:** lead se despide repetidamente después que el agente ya despidió.

**Mensaje:** un solo emoji `👍`.

### A.13 Mensaje de Foto Vacaciones (fuera de horario / pago recibido fuera de horario)

**Origen:** Airtable tabla `Foto Vacaciones` (`tbl8oRU3ApdEuLcgs`).

**Mensaje:**

```
✨ Gracias por tu pago! ✨
Lo recibimos correctamente 💳

Nos encontramos momentáneamente fuera de horario por receso, pero tu pago ya quedó registrado.
Apenas retomemos la actividad, lo revisaremos y confirmaremos a la brevedad, respetando el orden de llegada.

Gracias por tu confianza 💛
```

**Acompaña una imagen** (foto de "vacaciones" — vaca decorativa).

---

## 3. Categoría B — Templates con variables (cotizaciones)

### B.1 Cotización 1 caja

**Disparador:** Recolector calcula cotización con 1 sola caja.

**Template:**

```
Cotizacion: 
⏳(7 DIAS DE PROMO)⏳ 
[Cantidad] [Producto] x $[Precio] = $[Subtotal]
[Cantidad] [Producto] x $[Precio] = $[Subtotal]
...
Envío: $[Costo Envío]
Total: $[Total]
Anticipo: $[Anticipo 50%]
```

**Ejemplo real (sample 50 sandalias gruesas + 50 cilindros):**

```
Cotizacion:  
⏳(7 DIAS DE PROMO)⏳ 
50 Sandalias Gruesas x $30 = $1,500  
50 Cilindros x $10 = $500  
Envío: $300  
Total: $2,300  
Anticipo: $1,150
```

### B.2 Cotización 2 cajas

**Disparador:** lead pide cantidad que requiere división por restricciones de empaque.

**Template:**

```
Cotizacion:
⏳(7 DIAS DE PROMO⏳ 
[Cantidad] [Producto] x $[Precio] = $[Subtotal]
...
Envío 2 cajas: $[CostoCaja1] + $[CostoCaja2]= $[CostoTotal]
Total: $[Total]
Anticipo (50%): $[Anticipo]
```

**Restricción:** "No le justifiques a la persona por qué se tiene que dividir en dos cajas ni el peso, simplemente dale la cotización con el valor de las 2 cajas."

### B.3 Pedir datos para cotización

**Template (Products + Recolector):**

```
¿Le interesa sumarlos a la cotización?
Dígame:
- Cantidad
- Código postal
¡Gracias!
```

(Si son sandalias, agregar: "- ¿Delgadas o gruesas?")

### B.4 Pedido por debajo del mínimo

**Template (Recolector):**

Ej. para sandalias:

```
Disculpa, el pedido mínimo de Sandalias es de 50 pares del mismo grosor.
¿Te interesaría hacer la cotización con el mínimo o ajustamos las cantidades? ✨
```

(Variable: cantidad mínima por producto.)

### B.5 Pregunta tipo de sandalia

**Template:**

```
Para poder cotizarle las sandalias necesitaría que me diga si son delgadas ($25) o gruesas ($30), cantidad y código postal. ¡Gracias! ✨
```

---

## 4. Categoría C — Mensajes desde catálogo Airtable

Cada producto en Airtable tiene 3 campos relevantes para el envío:
- `archivo` — imagen/PDF del producto (URL Airtable)
- `URL` — versión pública en imgbb.com
- `descripcion` — texto que acompaña la imagen
- `bot_id` — ID del salesbot Kommo que envía el contenido pre-cargado
- `CURL` — plantilla de request a sendMessage (modificada en runtime con datos del lead)

### C.1 Imagen Principal por evento

**Tabla:** `Imagen Principal` (`tblsDWUQbfANNWMeK`)

| Evento | Título | URL imagen | Mensaje acompañante |
|--------|--------|-----------|--------------------|
| Boda | Todos los productos | i.ibb.co/SGdcy2K/684358c9dea5b.jpg | "TENEMOS ESTOS PRODUCTOS PARA TU EVENTO: *Sandalias* *Cilindros* *Mandiles para Boda* *Kit anti cruda* *Pantuflas*. Cuáles te interesan?" |
| XV | Todos los productos | i.ibb.co/pvsW9s7D/684358d8cddbd.jpg | "TENEMOS ESTOS PRODUCTOS PARA TU EVENTO: *Sandalias* *Cilindros* *Kit anti cruda* *Pantuflas*. Cuáles te interesan?" |
| Otros | Todos los productos | i.ibb.co/qYpxkqcP/5f983f64604b.jpg | "TENEMOS ESTOS PRODUCTOS PARA TU EVENTO: *Sandalias* *Cilindros* *Kit anti cruda* *Pantuflas*. Cuáles te interesan?" |

> **Observación:** la versión real enviada vía CURL agrega "Dime cuales te interesan, así te mostramos toda su información 😊". El campo `descripcion` y el texto del CURL difieren ligeramente — el CURL es la fuente de verdad final.

### C.2 Productos por evento

**Tablas:** `Boda`, `XV`, `Otros` (CSVs adjuntos).

**Estructura por producto:**
- Imagen + descripción explicativa con precios y mínimos.
- Algunos productos tienen solo bot_id (sin texto/imagen en n8n) — los gestiona el salesbot Kommo internamente.

#### C.2.1 Sandalias (S1, S3, S4)

**S1 — Comparativa de suelas (Boda)** — descripción:

```
✨ Sandalias personalizadas
💕 Un detalle que todos van a agradecer en tu evento
👡 Súper cómodas y personalizadas

💡 Disponibles en suela delgada ($25) o suela gruesa ($30), según la comodidad que estés buscando.
📦 Pedido mínimo de 50 pares.
```

**S3 — Catálogo PDF** — solo PDF (sin texto).
**S4 — Video** — solo bot_id (probablemente envía video desde Kommo).

#### C.2.2 Pantuflas (P1, P3/P4, P5, P6, P7)

**P1 — Pantuflas satin personalizadas:**

```
✨ Pantuflas de satín personalizadas
💖 Un detalle elegante y cómodo para tu evento
🥿 Suela y esponja más gruesa
🎨 Personalizadas con nombre y fecha

📏 Unitalla (les queda del 23 al 26)
💰 Precio promo: $30 el par
📦 Pedido mínimo de 50 pares

🎁 Opción de bolsa:
* Bolsa de tela personalizada (+$7 c/u)
* Bolsa tipo SHEIN no personalizada (tal cual la imagen)
```

**P6 — Pantuflas mono satin:**

```
✨ Pantufla de moño de satín para [evento]
🥿 Suela y esponja más gruesa
📏 Es unitalla, les queda desde el 23 al 26
🎨 1 diseño cada 50 pares
🌈 Colores disponibles: blanca, negra, morada, rosa, cielo y beige

💰 Precio promo: $30 el par
📦 Pedido mínimo: 50 pares

🎁 Elige entre:
* Bolsa tipo SHEIN no personalizada, tal cual como en la imagen
* Bolsa de tela personalizada (+$7 c/u)
```

**P7 — Pantuflas mono peluche:** mismo formato que P6 pero precio $35 y colores blanco/negro/morado/rosa.

**P3/P4 — Catálogo PDF** — sin texto.
**P5 — Video** — solo bot_id.

#### C.2.3 Cilindros (C1, C2, C3, C4)

**C1 — Cilindros personalizados (Boda):**

```
✨ Cilindros personalizados
🎉 Ideales para todo tipo de evento

🎨 Por cada 20 piezas se realiza un diseño diferente.

💰 Precio promo: $10 c/u
📦 Pedido mínimo de 40 piezas
```

**C2 — Catálogo:**

```
Te comparto el *catalogo de diseños* que tenemos para *Cilindros*
```
(+ imagen catálogo)

**C3 — Video** — solo bot_id.

#### C.2.4 Kit Anticruda (K1, K2, K3)

**K1 — Kit anticruda personalizado:**

```
✨ Kit anticruda personalizado
🎉 Ideal para cualquier tipo de evento
🛍️ Costal de tela personalizado a 1 tinta
📏 Medidas: 16 x 22 cm

💡 Solo incluye el costal, tú lo llenas con los productos que prefieras.

💰 Precio promo: $10 c/u
📦 Pedido mínimo de 35 piezas.
```

**K2 — Catálogo de frases:**

```
Te dejo el catalogo de frases que tenemos para los *ANTICRUDAS*
```
(+ imagen)

**K3 — Video** — solo bot_id.

#### C.2.5 Mandiles (M1, M2, M3) — solo Boda

**M1 — Mandiles para boda:**

```
✨ Mandiles para boda
🍾 Ideales para el novio y sus amigos
🖤 Diseño divertido para la fiesta

ℹ️ No se personalizan.

💰 Precio promo: $12 c/u
📦 Pedido mínimo de 12 piezas.
```

**M2 — Catálogo de mandiles** — texto + imagen.
**M3 — Video** — solo bot_id.

#### C.2.6 Vasos popote 24oz (V1)

**V1 — Vasos popote 24oz:**

```
✨ Vaso con popote 24 oz para [evento]
🖨️ Diseño en serigrafía
🥤 Vasos personalizados
🎨 Mismo diseño y tinta para todas las piezas
🎨 1 diseño cada 50 vasos

🌈 Tenemos varios colores de vasos
🥤 Puede escoger 1 color de vaso por cada 20 vasos

💰 Precio promo: $35
📦 Pedido mínimo: 50 piezas
⏳ Tiempo de fabricación: 15 días
```

#### C.2.7 Accesorios

**Bolsa shein de regalo:**

```
De *REGALO* Cada par viene en *BOLSA TIPO SHEIN* para meter los tacones.

*LA FRASE VIENE TAL CUAL COMO EN LA IMAGEN Y NO SE MODIFICA*
*NO SE PERSONALIZA*

Si quiere el *COSTALITO PERSONALIZADO $7C/U*
```

**Colores de tintas:**

```
Aqui te muestro los *colores disponibles* para las *TINTAS*
```
(+ imagen)

**Correas 15MM (suela gruesa):**

```
CORREAS DE SUELA GRUESA
```
(+ imagen)

**Correas 9MM (suela delgada):**

```
CORREAS DE SUELA DELGADA
```
(+ imagen)

**Tapas termos:**

```
Colores de *tapas* disponibles, puede ir surtido en los *colores* que gustes
```
(+ imagen)

### C.3 Métodos de Pago (PDF)

**Tabla:** `Métodos de Pago`

**Contenido:** PDF `NUMEROS DE CUENTA.pdf` (cuentas bancarias).
**Texto acompañante:** vacío (solo el PDF).
**Disparador:** lead pide pago / Recolector incluye `.com123` en output.

---

## 5. Categoría D — Generados por LLM (Recolector)

Estos no son fijos, pero sí siguen patrones aprendidos por el agente:

### D.1 Información de productos (Q&A)

| Pregunta | Respuesta canónica |
|----------|-------------------|
| Qué incluye el kit anticruda? | "El kit anticruda es solo el costal, usted lo llena con los productos." |
| Talla de las sandalias? | "Todas nuestras sandalias son UNITALLA, miden 25.5 cm de largo y les quedan desde la talla 23 mx a la 26 mx." |
| Aceptan tarjeta? | "No aceptamos pagos con tarjetas de crédito, solo efectivo o transferencia." |
| Qué pongo en concepto al transferir? | "Solo el nombre, no es necesario nada extra." |
| Dónde están? | (dirección Guadalajara JUAN R. ZAVALA #538 + link goo.su/OVoA) |

### D.2 Negativas a presión sobre precios

**Trigger:** lead dice "antes era más barato" / "tengo otro precio".

**Respuesta canónica:**

```
Los precios que te cotizo son los vigentes al día de hoy, ya incluyen el descuento aplicado.
```

### D.3 Negativa a sandalias para varones

**Respuesta canónica:**

```
[Aclara amablemente que las sandalias se fabrican exclusivamente para mujeres]
```

(Texto exacto a discreción del LLM.)

### D.4 Confirmación de cantidades antes de cotizar

**Template:**

```
Solo para confirmar, sería [cantidad1] [producto1] y [cantidad2] [producto2] para [evento]. ¿Es correcto? Así le hago la cotización exacta. ✨
```

---

## 6. Categoría E — Mensajes de seguimiento automáticos

Los sub-workflows envían mensajes pre-configurados en salesbots Kommo. Detectamos los **patrones de texto** que el sistema busca en la memoria para decidir si el lead respondió:

### E.1 Sub-workflow Seg. Rebeca (después del saludo)

| Wave | Espera | Patrón a detectar | Mensaje aproximado (inferido) |
|------|--------|-------------------|------------------------------|
| 1 | 1h | `"gracias por escribir a Happy Flops, me l..."` | Recordatorio: "Hola 👋, sigues por aquí?" |
| 2 | +3h | `"sigues por aquí?"` | "Solo necesito saber qué tipo de evento tienes para ayudarte..." |
| 3 | +Xh | `"Cuéntame, es para boda, XV años u otro e..."` | Mensaje insistente |
| 4 | +24h (final) | `"no quiero que se te pase la oportunidad..."` | "No quiero que se te pase la oportunidad..." → si no responde, **Ventas Perdidos** |

> Los textos exactos de los mensajes de re-engagement están **en los salesbots Kommo**, no en n8n. n8n solo detecta el patrón anterior y dispara el siguiente salesbot.

### E.2 Sub-workflow Seg. Imagen

| Wave | Espera | Patrón a detectar | Función |
|------|--------|-------------------|---------|
| 1 | 1h | `"Qué padre!"` | Reactivar interés |
| 2 | +3h | `"para esa linda ocasión?"` | Reactivar |
| 3 | +Xh | `"De lo que te compartí, hay algún..."` | Pregunta directa |
| 4 | +24h | `"puedo ayudarte a elegir lo más bonito y..."` | Última intentona → Perdidos |

### E.3 Sub-workflow Seg. Cotización

| Wave | Espera | Patrón a detectar | Función |
|------|--------|-------------------|---------|
| 1 | 1h | `"Producto Principal"` (tracking de ETAPA 3) | Reactivar |
| 2 | +3h | `"necesito que me compartas la cantidad y..."` | Pedir datos |
| 3 | +Xh | `"solo me falta saber cuántas piezas neces..."` | Insistir |
| 4 | +24h | `"para apartar y cotizar tus productos nec..."` | LLM evalúa "No?" → Perdidos / R1 SIN INFO |

### E.4 Sub-workflow Seg. 7pasos

| Wave | Espera | Patrón a detectar | Función |
|------|--------|-------------------|---------|
| 1 | 24h | `"6. Al terminar, te enviamos..."` (mensaje 7 pasos enviado) | LLM evalúa → R1 CON INFO o Perdidos |

---

## 7. Categoría F — Notificaciones operativas (Telegram)

Chat: `-4925599962`

| Disparador | Mensaje (nombre del nodo, contenido inferido) |
|------------|----------------------------------------------|
| PDF detectado en input lead | "Usr. envió PDF" + adjunto |
| Imagen producto válida | "Usr. envió imagen producto: [tipo]" |
| Imagen no clasificable | "Usr. envió imagen no categorizable" + imagen |
| Captura de pago (no producción) | "Usr. envió captura de pago" + imagen |
| Captura de pago (producción) | "Usr. envió captura de pago liquidación" + imagen |
| Lead derivado a humano | "Usr. Se encuentra en etapa de cotización" (sub-workflow ATENCION_PERSONALIZADA) |
| Lead activo en perdidos | "Usr. activo en perdidos" |

---

## 8. Reglas de orden y combinación

### 8.1 Orden de envío típico para una cotización

1. Cotización formateada (template B.1 o B.2).
2. Mensaje 7 pasos (A.3) — solo primera vez.
3. Mensaje upsell (A.5).
4. Pregunta avance al pago.

### 8.2 Mensajes que se envían split en N partes con waits

- Saludo Starter → 3 partes (`Saludo PTE 1`, `2`, `3`) con 2s wait.
- Mensajes largos del Recolector → `Message a model1` los divide en `parte1/2/3` con waits.

### 8.3 Mensajes que NO se envían si el lead ya los recibió

- Mensaje de los 7 pasos (A.3) — máximo 1 vez por conversación.
- Productos del catálogo — si ya se mostró ese producto en esa conversación, no se reenvía.
- Saludo Starter — solo si `Exist_Interaction == false`.

### 8.4 Mensajes prohibidos (regla crítica del prompt)

El agente NO puede enviar:

- Cualquier número telefónico que no sea `3315948670`.
- Información sobre peso del pedido (kg, kilos).
- Justificaciones de por qué hay 2 cajas.
- Precios distintos a los del prompt o devueltos por CALCULADORA.
- Cualquier sugerencia de sandalias para varones.
- "Despedidas" insistentes — usar 👍 en loops.

---

## 9. Total inventariado

| Categoría | Mensajes únicos |
|-----------|----------------|
| A — Hardcodeados | 13 mensajes literales |
| B — Templates con variables | 5 templates |
| C — Catálogo Airtable | ~40 productos × 3 eventos + accesorios + métodos pago + Foto Vacaciones |
| D — Generados LLM (Q&A canónicos) | ~10 patrones |
| E — Seguimientos automáticos | ~12 mensajes (4 waves × 3 sub-workflows + 1 wave Seg.7pasos) |
| F — Telegram operativo | 7 notificaciones |

**Total estimado:** ~120 mensajes/templates únicos a reproducir en GHL.
