# Guía de Testing — Fase 1 · Agente HPF "Rebeca" (Vendedor)

**Canal:** Telegram (rig de prueba del cerebro n8n · Vendedor §4)
**Fecha:** 2026-07-21
**Objetivo:** básicos — tono, saludo y flujo de conversación.

---

## Cómo usar

1. **Flujo 1** es una **conversación continua**: enviá los 5 mensajes en orden, en el mismo chat.
2. Los **casos C1–C10** son independientes. Si podés, arrancá cada uno en un **chat/sesión nueva** (o reiniciá la memoria) para que no arrastren contexto del anterior. Si no se puede, corré igual y avisá — lo tengo en cuenta al analizar.
3. Enviá el texto (está en `código` para copiar de un toque) y **pegá la respuesta del bot** reemplazando el `_(pegar acá)_`. Si el bot manda varios mensajes, pegalos todos.
4. Cuando termines, mandame el archivo (o pegámelo) y lo contrasto contra lo esperado.

> **Nota sobre el saludo:** el saludo fijo de 3 partes lo dispara GHL, no el cerebro de n8n. Por Telegram es posible que el bot arranque preguntando directamente el evento en vez del saludo textual — **es esperado**, el saludo literal se valida en Fase 2. Acá miramos que el arranque tenga buen tono y pida el evento.

---

## Flujo 1 — Feliz (conversación continua, en orden)

### F1 · t1 — enviar:
`Hola, buenas`

**Respuesta del bot:**

¡Hola! 😊 Soy Rebeca, asistente virtual de Happy Flops. Para ayudarte mejor, ¿me puedes decir qué tipo de evento estás organizando? (Boda, XV, bautizo, cumpleaños, empresarial, etc.)

---

### F1 · t2 — enviar:
`Es para unos XV`

**Respuesta del bot:**

¡Qué padre que estés planeando tus XV! 🎉 Cuéntame, ¿qué recuerditos te interesan para tu evento? Tenemos sandalias, pantuflas, cilindros, kit anticruda y más. Dime qué te gustaría ver y te paso opciones y precios.

---

### F1 · t3 — enviar:
`Quiero sandalias y cilindros`

**Respuesta del bot:**

```
¡Súper elección! Las sandalias y los cilindros son un hit en XV. Te paso rapidísimo la info:


- Sandalias: Suela delgada ($25/par) o gruesa ($30/par), mínimo 50 pares. Solo para mujer.
- Cilindros: 500ml, $10 cada uno, mínimo 40 piezas. Tapas surtidas.


¿Me puedes decir cuántos pares de sandalias y cuántos cilindros necesitas? Y para las sandalias, ¿prefieres suela delgada o gruesa? Así te hago la cotización exacta.
```

---

### F1 · t4 — enviar:
`100 sandalias delgadas y 50 cilindros, CP 44100`

**Respuesta del bot:**

```
⏳(7 DIAS DE PROMO)⏳
100 sandalias delgadas x $25 = $2500
50 cilindros x $10 = $500
Total: $3000
Anticipo (50%): $1500


Envío: se cotiza aparte según código postal, un asesor te lo confirma.


¡HAZ TU PEDIDO EN 7 SENCILLOS PASOS!🚀


1. COTIZACION de los PRODUCTOS que requiere para su PEDIDO
2. Se requiere del 50% de ANTICIPO para desarrollar los diseños.
3. Elige tu DISEÑO favorito 🎨 y proporciona los DATOS que deseas incluir.
4. Mandamos la MUESTRA DIGITAL para tu aprobación o cambios ✏️.
5. Una vez AUTORIZADO, COMENZAMOS LA PRODUCCION, son 15 DIAS EN PRODUCCION. 🛠️.
6. Al terminar, te enviamos una FOTO DEL PRODUCTO para que confirmes que todo está perfecto 📸.
7. Hace el PAGO FINAL y te enviamos tu pedido 🚚 (tiempo de paquetería: 2 a 5 días).


Mira, ya que pides sandalias y cilindros, ¿te gustaría agregar el Kit Anticruda para tu evento? ¡Son un hit en XV! ✨ ¿Te interesa que te pase info?_
```

---

### F1 · t5 — enviar:
`Va, ¿cómo pago?`

**Respuesta del bot:**

```
¡Súper fácil! 😊


Puedes hacer el anticipo de $1500 por transferencia bancaria o en efectivo en nuestro local.
- Si eliges transferencia, en el concepto solo pon tu nombre.
- Una vez hecho el pago, mándame tu comprobante aquí para avanzar con tus diseños.


Si prefieres venir, estamos en JUAN R. ZAVALA #538 (CALLE 38), COL SAN JUAN BOSCO, GUADALAJARA, JALISCO, C.P. 44730. Fachada fucsia, portones negros.
Aquí está el mapa: https://goo.su/OVoA


¿Te paso los datos bancarios para la transferencia?
```

---

## Casos simples (cada uno en sesión nueva, si se puede)

### C1 — enviar:
`hola, me pasás info?`

**Respuesta del bot:**

```
¡Hola! Soy Rebeca, asistente virtual de Happy Flops en Guadalajara. 😊


¿Para qué tipo de evento buscas recuerditos personalizados? (Boda, XV, Bautizo, Cumpleaños, Empresarial, etc.) Así te paso las opciones ideales para ti.
```

---

### C2 — enviar:
`quiero sandalias para el padrino`

**Respuesta del bot:**

_¡Gracias por tu mensaje! Te comento que nuestras sandalias son solo para mujeres, no manejamos versión masculina ni para padrinos. Si buscas algún otro recuerdito para hombre, tenemos cilindros o kit anticruda que son súper prácticos para cualquier invitado. ¿Te gustaría ver esas opciones? 😊_

---

### C3 — enviar:
`me interesan mandiles para unos XV`

**Respuesta del bot:**

_¡Gracias por tu interés! Mira, los mandiles solo los manejamos para Boda. Para XV, tengo otras opciones súper padres como sandalias, pantuflas, cilindros y kit anticruda. ¿Te gustaría ver alguno de esos para tu evento? 😊_

---

### C4 — enviar:
`dame 35 cilindros para una boda, CP 44730`

**Respuesta del bot:**

_¡Gracias por tu mensaje! Mira, el mínimo para los cilindros es de 40 piezas, así que con 35 no llegamos al mínimo para cotizar. Si gustas, puedes ajustar tu pedido a 40 cilindros y con gusto te hago la cotización. ¿Te gustaría aumentar la cantidad? 😊_

---

### C5 — enviar:
`quiero pantuflas de moño, 50, CP 44100`

**Respuesta del bot:**

_¡Súper elección! Las pantuflas de moño pueden ser de satín o de peluche (colores: blanca, negra, morada o rosa). ¿Cuál prefieres para tus 50 pares? Así te hago la cotización exacta para el CP 44100._

---

### C6 — enviar:
`te doy $20 por sandalia si me llevo 100`

**Respuesta del bot:**

_¡Gracias por tu interés! Los precios ya tienen promo y no podemos bajarlos más: la sandalia delgada está en $25/par y la gruesa en $30/par, mínimo 50 pares. Si quieres cotizar, dime el tipo de suela que te interesa (Delgada o Gruesa) y tu código postal para calcular tu pedido. ¿Te gustaría seguir con la cotización? 😊_

---

### C7 — enviar:
`¿cuánto pesa el paquete de 100 sandalias?`

**Respuesta del bot:**

_¡Hola! No puedo compartir el peso del paquete, pero si necesitas cotización o detalles de envío, dime tu código postal y te ayudo a calcularlo. ¿Te gustaría cotizar 100 sandalias? ¿Prefieres suela Delgada o Gruesa? 😊_

---

### C8 — enviar:
`¿tenés otro whatsapp o número para llamar?`

**Respuesta del bot:**

_¡Gracias por preguntar! Solo tenemos un número oficial de contacto: 3315948670. Cualquier duda o pedido, aquí te atiendo con gusto 😊._

---

### C9 — enviar:
`mandame el catálogo de sandalias`

**Respuesta del bot:**

_¡Claro! Te paso la info de nuestras sandalias personalizadas para eventos. ¿Para qué tipo de evento las quieres? (Boda, XV, bautizo, etc.) Así te muestro las opciones que aplican para tu evento._

---

### C10 — enviar:
`¿me hacés la cotización formal en PDF a mi correo?`

**Respuesta del bot:**

_¡Súper! Te puedo enviar aquí la cotización formal con todos los detalles y pasos para tu pedido. Por el momento, la cotización en PDF solo la genera nuestro equipo después de que avances con el anticipo y el diseño. ¿Te gustaría que te mande la cotización aquí mismo para que la revises y me confirmes cantidades y productos? 😊


Cuéntame, ¿qué productos te interesan y para qué evento son?_

---

_Fin de la Fase 1 (15 turnos: 5 del flujo feliz + 10 casos simples)._
