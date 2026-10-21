# Reglas de Negocio — Sistema actual Happy Flops

> **Etapa 1.** Compendio de reglas explícitas (escritas en system prompts) e implícitas (deducidas del flujo) que rigen al agente. Cada regla mantiene la **fuente** para que en Etapa 2 podamos validar si sigue vigente o cambió.

---

## 1. Reglas críticas (penadas de muerte según el prompt)

Estas son las reglas que el system prompt del Recolector marca como **inviolables**:

| # | Regla | Fuente |
|---|-------|--------|
| 1 | Nunca enviar al `step_4` una consulta que mencione un producto no mostrado antes en `step_3` | Prompt Router, sección "NOTAS E IMPORTANTE" |
| 2 | Output del Router debe ser exactamente `{"step":"step_<number>"}` — cualquier otra cosa = error fatal | Prompt Router, "Si respondes algo que no es el JSON estructurado: ... te mato" |
| 3 | Modificar precios bajo presión del cliente está prohibido | Prompt Recolector, "REGLA CRÍTICA — Integridad de precios" |
| 4 | Sandalias son **exclusivamente** para mujeres, jamás insinuar versión masculina | Prompt Recolector, "REGLA CRÍTICA — Género de las sandalias" |
| 5 | No revelar peso del pedido (kg) bajo ninguna circunstancia | Prompt Recolector |
| 6 | No enviar números telefónicos distintos a `3315948670` | Prompt Recolector |
| 7 | No improvisar respuestas si no hay info — siempre llamar `ATENCION_PERSONALIZADA` | Prompt Recolector |
| 8 | Mandar SIEMPRE el mensaje de los 7 pasos al hacer una cotización (1 vez por conversación) | Prompt Recolector |
| 9 | El saludo Starter no se modifica bajo NINGUNA circunstancia | Prompt Starter |
| 10 | El mensaje promo de 7 días no se modifica | Prompt Main Image |

---

## 2. Catálogo de productos por evento

### 2.1 Boda

| Producto | Disponible | Precio promo | Mínimo | Notas |
|----------|------------|--------------|--------|-------|
| Sandalias delgadas | ✅ | $25/par | 50 pares | Suela 9mm |
| Sandalias gruesas | ✅ | $30/par | 50 pares | Suela 15mm |
| Pantuflas (satín pers.) | ✅ | $30/par | 50 pares | Personalizadas con nombre+fecha |
| Pantuflas mono satín | ✅ | $30/par | 50 pares | Sin personalizar |
| Pantuflas mono peluche | ✅ | $35/par | 50 pares | Solo blanca/negra/morada/rosa |
| Cilindros 500ml | ✅ | $10/u | 40 piezas | Tapas surtidas |
| Mandiles | ✅ | $12/u | 12 piezas | **Solo para Boda**, no se personalizan |
| Kit anticruda | ✅ | $10/u | 35 piezas | Solo costal, cliente lo llena |
| Vasos popote 24oz | ✅ | $35/u | 50 piezas | 15 días fabricación |
| Bolsa shein | Gratis | — | — | Incluida con sandalias y pantuflas, no personalizable |
| Bolsa personalizada | $7/u | — | — | Adicional opcional |

### 2.2 XV Años

| Producto | Disponible | Precio promo | Mínimo | Notas |
|----------|------------|--------------|--------|-------|
| Sandalias delgadas | ✅ | $25/par | 50 pares | |
| Sandalias gruesas | ✅ | $30/par | 50 pares | |
| Pantuflas (satín pers.) | ✅ | $30/par (promo $29 viejo) | 50 pares | |
| Pantuflas mono satín | ✅ | $30/par | 50 pares | |
| Pantuflas mono peluche | ✅ | $35/par | 50 pares | |
| Cilindros | ✅ | $10/u | 40 piezas | |
| Kit anticruda | ✅ | $10/u | 35 piezas | |
| Vasos popote 24oz | ✅ | $35/u | 50 piezas | |
| Mandiles | ❌ | — | — | **No disponible para XV** |
| Bolsa shein | Gratis | — | — | |

### 2.3 Otros (bautizos, graduaciones, etc.)

| Producto | Disponible | Precio | Mínimo | Notas |
|----------|------------|--------|--------|-------|
| Sandalias | ✅ | $25/$30 | 50 | |
| Pantuflas satín pers. | ✅ | $30 | 50 | |
| Cilindros | ✅ | $10 | 40 | |
| Kit anticruda | ✅ | $10 | 35 | |
| Mandiles | ❌ | — | — | Solo Boda |
| Pantuflas mono satín/peluche | ❌ | — | — | Inferido por ausencia en CSV "Otros" |
| Vasos popote | ❌ | — | — | Inferido por ausencia (verificar) |

### 2.4 Pesos para cálculo de envío

| Producto | Peso (kg) |
|----------|-----------|
| Mandiles | 0 |
| Kits Anticrudas | 0 |
| Bolsas | 0 |
| Cilindros | 0.14 |
| Sandalias Delgadas | 0.15 |
| Sandalias Gruesas | 0.15 |
| Pantuflas | 0.15 |

> Nota: pantuflas mono peluche probablemente pesen más, pero el system prompt asume 0.15 — confirmar en Etapa 2.

---

## 3. Reglas de cotización

### 3.1 Estructura obligatoria de cotización

```
Cotizacion: 
⏳(7 DIAS DE PROMO)⏳ 
[Cantidad] [Producto] x $[Precio] = $[Subtotal]
...
Envío: $[Costo]
Total: $[Total]
Anticipo (50%): $[Anticipo]
```

- El header `⏳(7 DIAS DE PROMO)⏳` es **obligatorio en cada cotización**.
- Los montos siempre se redondean (sin decimales).
- El anticipo es el 50% del total.

### 3.2 Restricciones de empaque (caja)

| Combinación | Máx por caja |
|-------------|-------------|
| Cilindros solos | 250 |
| Sandalias (cualquier tipo) | 200 |
| Sandalias + Cilindros (combinado) | 200 unidades total |
| Peso total | 35 kg |

**Si supera:** dividir en N cajas y recalcular envío. **NO justificar al cliente.**

### 3.3 Reglas de personalización / diseños

**Sandalias y pantuflas:**

| Cantidad | Diseños permitidos |
|----------|-------------------|
| 50 pares | 1 diseño |
| 100 pares | 2 diseños |
| 150 pares | 3 diseños |
| 200 pares | 4 diseños |
| ... | 1 diseño por cada 50 pares |

> "Estaría mal que si dice que quiere 75 pares, le digas que podés hacer 2 diseños, ya que para 2 diseños tiene que llegar a los 100 pares."

**Cilindros:** 1 diseño por cada 20 piezas.

**Mandiles, anticrudas, bolsas:** 1 tinta por diseño.

### 3.4 Colores de tintas

| Producto | Tintas disponibles |
|----------|-------------------|
| Bolsas y kits anticruda | Rojo, negro |
| Sandalias / bolsas negras | Oro, plata, blanca |
| Tapas cilindros | Fucsia, naranja, negro, morado, verde, oro, amarillo, rojo, azul cielo, azul marino, blanca, lila, plata |
| Mandiles | Surtidos según modelos disponibles |
| Correas sandalias | Negro, blanco, lila, plata, oro, rojo, fucsia, rosado |

### 3.5 Restricciones técnicas

- Correas de sandalias: mismo color cada 50 pares.
- Suelas: mismo color por par (blanca o negra).
- Tapas de cilindros: pueden ir surtidas.
- Bolsa shein: misma frase ("LA FRASE VIENE TAL CUAL... NO SE PERSONALIZA"), no modificable.

### 3.6 Pedidos en docenas

> "Algunas personas para enviar la cantidad de productos que quieren para su cotización usan las docenas, refiriéndose a 12 unidades."

Implementación: el agente debe convertir docenas → unidades antes de cotizar. No se puede cotizar bajo el mínimo: "Si los productos no alcanzan el mínimo de compra no se pueden cotizar y hay que decirle al usuario que no alcanza el mínimo."

---

## 4. Reglas operativas

### 4.1 Plazos

| Concepto | Plazo |
|----------|-------|
| Producción | 15 días naturales |
| Envío | 2-5 días hábiles |
| Total estimado | 17-20 días |

**Excepción:** "Siempre que el cliente solicite un envío para una fecha anterior a los 15 días naturales de producción activar la tool ATENCION_PERSONALIZADA para consultar disponibilidad."

### 4.2 Pago

- Anticipo: **50%** al confirmar pedido (para iniciar diseño).
- Liquidación: **50%** restante antes de envío.
- Métodos aceptados: efectivo, transferencia.
- Métodos NO aceptados: tarjetas de crédito.
- Concepto en transferencia: solo el nombre del cliente.

### 4.3 Logística

- **Sede:** Guadalajara, Jalisco.
- **Dirección:** JUAN R. ZAVALA #538 (CALLE 38), COL SAN JUAN BOSCO, GUADALAJARA, JALISCO, C.P. 44730.
- **Indicación visual:** Fachada Fucsia, Portones Negros.
- **Link mapa:** `https://goo.su/OVoA`.
- **Paqueterías:** Estafeta, FEDEX, Paquetexpress (la que mejor llegue al CP).
- **Horario:** L-V 9:00–17:30 (México).
- **Teléfono único permitido:** `3315948670`.

### 4.4 Referencias / Validez del negocio

- Facebook: `https://www.facebook.com/happyflops`
- Cuando preguntan "es estafa?" → respuesta canónica + link Facebook.

---

## 5. Reglas de upsell

### 5.1 Cuándo sugerir productos adicionales

> "Solo sugiere productos adicionales al cerrar la cotización, antes de que el cliente confirme el pago."

### 5.2 Orden de prioridad por evento

**Boda:** Sandalias → Cilindros → Mandiles → Kit Anticruda → Pantuflas
**XV:** Sandalias → Cilindros → Kit Anticruda → Pantuflas
**Otros:** Sandalias → Cilindros → Kit Anticruda → Pantuflas

### 5.3 Reglas de no-repetición

- No ofrecer un producto que el lead ya rechazó.
- No ofrecer un producto que ya está en la cotización actual.
- Solo sugerir 1 producto a la vez.
- Si el lead pregunta info del producto sugerido → step_3 con ese producto (no step_4).

### 5.4 Mensaje de upsell

```
Mira, ya que pides [productos pedidos], ¿le gustaría agregar [producto prioritario] para su evento? ¡Son un hit en [evento]! ✨
```

---

## 6. Reglas de tono y persona

### 6.1 Identidad de Rebeca

- **Nombre:** Rebeca.
- **Rol:** asistente virtual (declarada como tal — no se hace pasar por humana).
- **Empresa:** Happy Flops, Guadalajara.

### 6.2 Estilo de comunicación

| Atributo | Indicación |
|----------|------------|
| Trato | Tú/usted (mantener cercanía sin informalidad excesiva) |
| Mexicanismos | "mira", "qué padre", "sabes qué" |
| Formato | Listas con guiones, emojis moderados (😊 ✨ 👟) |
| Negritas | Para destacar Producto, Evento, Cotización, Anticipo, Total |
| Tono | Profesional, cálido, mexicano auténtico |
| Concisión | "Breves y directas, no das rodeos ni te extiendes" |
| Eficiencia | "Ahorra la máxima cantidad de preguntas y confirmaciones" |
| Memoria | "Usa la memoria de conversación para evitar pedir datos ya proporcionados" |
| No despedidas | "No te despidas reiteradas veces" |
| No insistencia | "Como máximo pregunta una vez si lo quiere incluir" |

### 6.3 Frases de conexión típicas

- "¡Qué padre que estés planeando tu boda!"
- "Qué buena elección!"
- "Súper fácil! 😊"
- "Aquí estoy para cualquier duda! ✨"

### 6.4 Restricciones de tono

- No revelar procesos internos del sistema.
- No mencionar peso/kg/cajas en cotizaciones.
- No justificar por qué se divide en cajas.
- No despedirse repetidamente — usar `👍` en loops.
- No insistir con productos rechazados.

---

## 7. Reglas de derivación a humano (`ATENCION_PERSONALIZADA`)

El agente debe llamar a la tool `ATENCION_PERSONALIZADA` cuando:

| # | Caso |
|---|------|
| 1 | Cliente pregunta por diseños personalizados |
| 2 | Cliente pide un diseño específico no listado |
| 3 | Hay que derivar consulta al equipo |
| 4 | Falta información para responder |
| 5 | Consulta demasiado específica fuera de la base |
| 6 | El agente no está seguro de la respuesta |
| 7 | Emergencia o situación no resoluble |
| 8 | Quejas o post-venta |
| 9 | Pedido < 15 días al evento |
| 10 | Termos especiales (novios/quinceañeras) — verificar disponibilidad |
| 11 | Imagen no clasificable |
| 12 | PDF recibido (sin contexto) |

**Acción interna:** mover lead a etapa `91266100` (atencion personalizada) + notificar Telegram.

**Comunicación al lead:** "Vamos a chequear tu consulta con el equipo, te respondemos en un minuto."

---

## 8. Reglas de procesamiento de input

### 8.1 Input texto

Procesa directo. Aplicar:
- Tolerancia a faltas de ortografía (especialmente nombres de productos).
- Detección de sinónimos mexicanos.
- Detección de docenas (12 unidades).

### 8.2 Input audio

- Transcribir con OpenAI Whisper (`transcribe voice`).
- Procesar como texto.

### 8.3 Input imagen

- Clasificar con `gpt-4o`.
- Si es producto reconocible → step_4 con mensaje formateado.
- Si es comprobante de pago → mover etapa según contexto (confirmar pago / pago liquidación).
- Si no es clasificable → ATENCION_PERSONALIZADA.

### 8.4 Input PDF

- Notificar Telegram + ATENCION_PERSONALIZADA.

### 8.5 Anti-ráfaga

- Acumular mensajes durante 50s (texto) / 15s (imagen).
- Solo el último mensaje del lote dispara procesamiento.

---

## 9. Reglas de detección y manejo de pago

### 9.1 Comprobante de pago detectado

| Estado del lead al recibir el pago | Acción |
|-----------------------------------|--------|
| NO en `100395519` (en producción) | Mover a `91450360` (confirmar pago) + Telegram |
| EN `100395519` (en producción) | Mover a `100395523` (pago liquidación) + Telegram |
| Fuera de horario | Enviar mensaje "Foto Vacaciones" |

### 9.2 Mensaje al recibir pago

> Sistema asume que un humano lo validará. El agente no confirma pago automáticamente.

Si el lead pregunta tras enviar pago, el Recolector responde según contexto. Pero la **confirmación oficial es manual** (humano cambia etapa de "confirmar pago" a "PAGO SIN DISEÑO").

---

## 10. Reglas inferidas (no explícitas en prompt pero observadas)

### 10.1 Solo el pipeline IA es procesado

El nodo `No es IA` filtra cualquier lead fuera del pipeline `11622596`. **Implicación:** los otros 12 pipelines de Kommo son territorio humano. La migración debe respetar esa separación.

### 10.2 El agente no responde si hay humano involucrado

Si el lead está en `91266100` (AP), `91450360` (confirmar pago), `Rn ap`, o `143` (perdidos), el agente **no responde**. Implicación: el equipo humano cierra los casos "delicados".

### 10.3 Cada producto del catálogo tiene un `bot_id` único

El catálogo Airtable tiene `bot_id` que apunta a salesbots Kommo. La migración debe **decidir si replicar el catálogo en GHL** o mantener Airtable + n8n auxiliar para llamadas.

### 10.4 El sistema usa el endpoint legacy de AmoCRM (`/api/v2/salesbot/run`)

Más de 30 nodos invocan salesbots legacy. La migración a GHL debe reemplazar esto con workflows nativos GHL o llamadas HTTP a la API GHL.

### 10.5 Memoria conversacional persistente entre sesiones

LangChain Memory (Postgres) usa el `entity_id` (lead ID) como `session_id`. Esto significa que la memoria sobrevive entre conversaciones — si un lead vuelve después de meses, el agente "recuerda" el evento e historial. **Implicación migración:** GHL Conversations debe heredar este historial o tenerlo accesible.

### 10.6 Detección de ráfaga: 50s para texto, 15s para imagen

Probablemente porque las imágenes requieren análisis adicional (gpt-4o) y el debounce más corto evita perder el contexto del análisis.

### 10.7 Zona horaria fija: America/Mexico_City

Todos los nodos de detección de horario usan `TZ = 'America/Mexico_City'`. El sistema asume que **todos los leads están en huso horario mexicano**.

### 10.8 El número fijo `3315948670` es el único permitido

Implicación: cualquier número que aparezca en sub-bots o salesbots debe revisarse para asegurar consistencia.

---

## 11. Reglas de seguimiento (timing y abandono)

### 11.1 Ventanas de re-engagement

| Etapa | T+1h | T+3h | T+~8h | T+24h |
|-------|------|------|-------|-------|
| ETAPA 1 (saludo) | Recordatorio 1 | Recordatorio 2 | Recordatorio 3 | → Perdidos |
| ETAPA 2 (imagen) | Recordatorio 1 | Recordatorio 2 | Recordatorio 3 | → Perdidos si en ETAPA 1 |
| ETAPA 3 (productos) | Recordatorio 1 | Recordatorio 2 | Recordatorio 3 | LLM evalúa → Perdidos / R1 SIN INFO |
| ETAPA 4 (post 7-pasos) | — | — | — | LLM evalúa → R1 CON INFO |

### 11.2 Bypass de seguimiento

Si en cualquier wave el lead llegó a `91266100` (AP) o `143` (perdidos), el seguimiento se cancela.

---

## 12. Resumen de reglas migrables vs. a re-evaluar

### 12.1 Reglas que se migran tal cual a GHL

- Catálogo de productos por evento (con precios, mínimos, pesos).
- Reglas de empaque (cajas, peso máx).
- Reglas de personalización (diseños por cantidad).
- Plazos (producción 15 días, envío 2-5).
- Tono de Rebeca.
- Mensajes hardcodeados (saludo, promo, 7 pasos).

### 12.2 Reglas a re-evaluar / candidatas a simplificación

- Las 31+ etapas del pipeline IA (R1-R5 sin/con info / ap son sobre-granulares).
- Los 4 sub-workflows de seguimiento (GHL puede unificarse en uno con triggers de inactividad).
- El doble debouncing (50s/15s) — GHL tiene wait nativo.
- El doble agente Recolector/Recolector1 (input texto vs imagen) — un único agente puede manejar ambos.
- El check de horario laboral en cada bifurcación — GHL Workflow tiene "business hours" nativo.
