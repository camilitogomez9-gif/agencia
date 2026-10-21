# Criterios Fase 1 (referencia interna) — Agente HPF "Rebeca" (Vendedor §4)

> **Uso:** vara con la que Claude contrasta lo que la agencia pega en `testing-guide-fase1-v1.md`. No es para el cliente ni para pegar en Telegram. Cada caso: **Requerido** (debe cumplir) + **Prohibido** (NO debe hacer) + **Regla** (mapeo al prompt §4 / Test Plans D–E).
>
> **Fuente de verdad del prompt:** `00_migracion_ghl/05_ejecucion/guia-correccion-integral-2026-07-13.md` §4.
>
> **Recordatorio de arquitectura:** las tools con side-effect (`MOSTRAR_PRODUCTOS` manda fichas por GHL Conversations API; `IDENTIFICAR_EVENTO` manda imagen principal + promo; `ATENCION_PERSONALIZADA` notifica) pueden **no** verse por Telegram. En Fase 1 juzgamos la **respuesta conversacional**, no el side-effect. La verificación de que la tool efectivamente se invocó es de Fase 2 (vía `intermediateSteps`).

## Datos canónicos (para chequear precios/mínimos)

| Producto | Precio | Mínimo | Notas |
|---|---|---|---|
| Sandalias delgadas (9mm) | $25/par | 50 | solo mujeres |
| Sandalias gruesas (15mm) | $30/par | 50 | solo mujeres |
| Pantuflas satín | $30/par | 50 | |
| Pantuflas moño satín | $30/par | 50 | |
| Pantuflas moño peluche | $35/par | 50 | solo blanca/negra/morada/rosa |
| Cilindros 500ml | $10/u | **40** | |
| Kit anticruda | $10/u | 35 | solo el costal |
| Mandiles | $12/u | 12 | **solo Boda**, no se personalizan |
| Vasos popote 24oz | $35/u | 50 | |

- Teléfono ÚNICO permitido: **3315948670**. Header de cotización EXACTO: **⏳(7 DIAS DE PROMO)⏳**. Anticipo = **50%** del total, sin decimales. Pago: 50% anticipo, efectivo/transferencia, **no tarjetas**, concepto = nombre del cliente. Producción 15 días, envío 2–5 días. Disponibilidad: Boda = todos; XV = todos menos Mandiles; Otros = Sandalias/Pantuflas satín/Cilindros/Kit.

---

## Flujo 1 — Feliz

### F1 · t1 — `Hola, buenas`
- **Requerido:** tono cálido y breve, mexicano; pide el **evento** (idealmente ofrece Boda / XV / Otros).
- **Prohibido:** párrafo largo/robótico; arrancar a cotizar o pedir datos sin saber el evento.
- **Regla:** §4 [1] tono; [4] stage "Saludo Enviado" → preguntar evento. (El saludo fijo de 3 partes es de GHL; su ausencia por Telegram NO es falla.)

### F1 · t2 — `Es para unos XV`
- **Requerido:** reconoce el evento con frase de conexión ("¡Qué padre…!"); invita a decir qué productos le interesan. Idealmente dispara `IDENTIFICAR_EVENTO`.
- **Prohibido:** volver a preguntar el evento; ofrecer **Mandiles** (no van en XV).
- **Regla:** §4 [4] Evento Identificado; disponibilidad por evento; [1] no repetir.

### F1 · t3 — `Quiero sandalias y cilindros`
- **Requerido:** reconoce ambos productos; pide lo que falta para cotizar: **cantidad** (por producto), **CP**, y **tipo de suela** (delgada 9mm vs gruesa 15mm). Idealmente dispara `MOSTRAR_PRODUCTOS`.
- **Prohibido:** cotizar ya (faltan datos); asumir suela sin preguntar.
- **Regla:** §4 [4] Productos Mostrados → recolectar; [5].11 confirmar variante.

### F1 · t4 — `100 sandalias delgadas y 50 cilindros, CP 44100`
- **Requerido:** cotización con **header exacto** `⏳(7 DIAS DE PROMO)⏳`; líneas `100 Sandalias delgadas x $25 = $2,500` y `50 Cilindros x $10 = $500`; línea **Envío**; **Total**; **Anticipo (50%)**; montos **sin decimales**; luego el bloque **7 pasos** (una sola vez).
- **Referencia de math (para sanity check, no pass/fail estricto en Fase 1):** subtotal productos $3,000; peso ≈ 22 kg (100×0.15 + 50×0.14) → 1 caja, rango 20–35 kg → envío **$400**; Total **$3,400**; Anticipo **$1,700**. Si el envío/Total difiere, marcarlo como observación (la math exacta del `COTIZADOR` se valida en Fase 2).
- **Prohibido:** revelar kg/peso o mencionar cajas; anticipo ≠ 50%; decimales; omitir el header; repetir 7 pasos si ya salió.
- **Regla:** §4 [8] formato; [5].8 header; [5].9 anticipo; [5].2 no kg/cajas.

### F1 · t5 — `Va, ¿cómo pago?`
- **Requerido:** da la info de pago (50% de anticipo para arrancar; efectivo o transferencia; concepto = nombre); pide el comprobante del 50%. Cierre cordial.
- **Prohibido:** ofrecer pago con **tarjeta**; despedidas repetidas/largas; dar otro número/dato de pago inventado.
- **Regla:** §4 [2] pago; [4] stage Cotizado → cerrar.

---

## Casos simples

### C1 — `hola, me pasás info?`
- **Requerido:** arranque cálido; reconduce pidiendo el **evento** (no puede dar "info" genérica sin evento).
- **Prohibido:** volcar catálogo/precios completos sin saber el evento; tono seco.
- **Regla:** §4 [1]/[4].

### C2 — `quiero sandalias para el padrino`
- **Requerido:** aclara amablemente que las sandalias son **solo para mujeres**; reorienta.
- **Prohibido:** insinuar/ofrecer versión masculina; seguir como si hubiera sandalias de hombre.
- **Regla:** §4 [3] regla inviolable + [5].6. (Test Plan D-05.)

### C3 — `me interesan mandiles para unos XV`
- **Requerido:** aclara que los **mandiles son solo para Boda**; ofrece alternativas válidas de XV si corresponde.
- **Prohibido:** cotizar/ofrecer mandiles para XV.
- **Regla:** §4 [3]/[5].6. (Test Plan D-06.)

### C4 — `dame 35 cilindros para una boda, CP 44730`
- **Requerido:** NO cotiza; avisa que el **mínimo de cilindros es 40** y pide ajustar la cantidad. (Cilindros SÍ van en Boda — el bloqueo es solo el mínimo.)
- **Prohibido:** emitir una cotización por 35; inventar otro mínimo; ignorar el mínimo y seguir.
- **Regla:** §4 [3] "si no alcanza el mínimo, decilo y NO cotices". (Incidente real Cilindros 35/40.)

### C5 — `quiero pantuflas de moño, 50, CP 44100`
- **Requerido:** confirma la **variante** antes de cotizar: **moño satín ($30)** vs **moño peluche ($35)**; no asume.
- **Prohibido:** cotizar directo asumiendo una variante (sobre todo peluche por default); inventar "Pantuflas Normales Satín".
- **Regla:** §4 [5].11 confirmar variante. (Bug histórico P4.)

### C6 — `te doy $20 por sandalia si me llevo 100`
- **Requerido:** mantiene el precio ("los precios vigentes ya son los promocionales"); no regatea. Si el lead insistiera fuerte → `ATENCION_PERSONALIZADA`.
- **Prohibido:** bajar el precio; aceptar los $20; prometer un descuento.
- **Regla:** §4 [5].1 no modificar precios. (Test Plan D-04/D-08.)

### C7 — `¿cuánto pesa el paquete de 100 sandalias?`
- **Requerido:** responde sin revelar kg (puede hablar de tiempos de envío / que se calcula en la cotización).
- **Prohibido:** dar el peso en kg; mencionar cajas / lógica de empaque.
- **Regla:** §4 [5].2 nunca revelar peso/cajas. (Test Plan D-01.)

### C8 — `¿tenés otro whatsapp o número para llamar?`
- **Requerido:** da únicamente **3315948670**.
- **Prohibido:** dar cualquier otro número; inventar uno.
- **Regla:** §4 [5].5 único teléfono permitido. (Test Plan D-02.)

### C9 — `mandame el catálogo de sandalias`
- **Requerido:** reenvía el material / lo ofrece (idealmente dispara `MOSTRAR_PRODUCTOS`); si ya se lo había pasado, pregunta "¿todavía tenés la info o te la reenvío?".
- **Prohibido:** **derivar a humano** solo por pedir catálogo/foto; responder que no puede.
- **Regla:** §4 [4] reenvío de catálogo. (Mejoras P7/P8, Test Plan E-07/E-08/E-09.)

### C10 — `¿me hacés la cotización formal en PDF a mi correo?`
- **Requerido:** NO promete PDF ni pide email; deriva a atención personalizada (`ATENCION_PERSONALIZADA`) o indica que el equipo lo sigue.
- **Prohibido:** prometer un PDF; pedir el correo; inventar que se manda por mail.
- **Regla:** §4 [5].4 no improvisar → escalar. (Mejora P5, Test Plan E-05.)

---

## Escala de veredicto (para el doc de resultados)

- ✅ **pasa** — cumple todos los Requerido y ningún Prohibido.
- ⚠️ **parcial** — cumple lo esencial pero con un defecto menor (tono/omite un dato/no dispara la tool ideal pero conversa bien).
- ❌ **falla** — viola un Prohibido o incumple un Requerido central.

Cada fallo → diagnóstico de causa raíz + acción (fix de prompt §4 puntual, con backup previo antes de tocar).
