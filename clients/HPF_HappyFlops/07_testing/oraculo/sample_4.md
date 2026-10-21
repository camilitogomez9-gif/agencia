# Oraculo observado — sample_4

Fuente: `00_migracion_ghl/00_inputs/conversation_samples.json` (transcript real de produccion del bot legacy en Kommo).
session_hash: `61f60803cabd5c3d0ac8c4f7bc7cbf67` · turnos: 67

- `LEAD` = lo que escribio el cliente (ya saneado, listo para usar como input de test).
- `RECIBE` = lo que el bot original le mando al lead. **Esto es el esperado.**
- `DECIDE` = decision interna del Router/agente de productos. No la ve el lead.

---

**T1 · LEAD**
```
¡Hola! Quiero más información. ¡Hola! Quiero más información
```

**T2 · RECIBE**
```
Hola! gracias por escribir a Happy Flops, me llamo Rebeca soy un asistente virtual, yo le estaré atendiendo con gusto ☺️🙋‍♀ Me podría decir de que es su evento? 🤵👰 - Boda 🎂🥳 - XV Años 👼🏢 - Otros
```

**T3 · LEAD**
```
15 años
```

**T4 · DECIDE**
```json
{
  "step": "step_2"
}
```

**T5 · LEAD**
```
15 años
```

**T6 · DECIDE**
```json
{
  "evento": "XV",
  "texto_dinamico": "Qué padre! 😊 \n🎉 *¡SEMANA LOCA DE PROMOS! SOLO 7 DÍAS PARA LLEVARTE TUS RECUERDITOS PERSONALIZADOS CON DESCUENTAZO* 🎉\n*(Pedidos solo para eventos 2026 por tema de tiempos)*"
}
```

**T7 · LEAD**
```
Sandalias
```

**T8 · DECIDE**
```json
{
  "step": "step_3"
}
```

**T9 · LEAD**
```
Sandalias
```

**T10 · DECIDE**
```json
{
  "evento": "XV",
  "subcategoria": "Producto Principal",
  "productos": [
    "sandalias"
  ],
  "texto_dinamico": "¿Le interesa sumarlas a la cotización?\nDígame:\n- Cantidad\n- Código postal\n¡Gracias!"
}
```

**T11 · RECIBE**
```
Hola 😄, para poder enviarte la cotización necesito que me compartas la cantidad y el código postal 📦
```

**T12 · RECIBE**
```
Hola! 👋 Ya tengo tus productos seleccionados, solo me falta saber cuántas piezas necesitas y tu código postal para calcular el envío 🚚
```

**T13 · RECIBE**
```
Hola 😊, para apartar y cotizar tus productos necesito esos dos datos: cantidad y código postal. Así puedo enviarte tu cotización 📄
```

**T14 · LEAD**
```
50 piezas y 61800 Hola buen día
```

**T15 · DECIDE**
```json
{
  "step": "step_4"
}
```

**T16 · LEAD**
```
50 piezas y 61800 Hola buen día
```

**T17 · RECIBE**
```
Gracias por la información. ¿Las sandalias que deseas son delgadas o gruesas? Esto me ayudará a calcular el costo exacto para ti. 😊
```

**T18 · LEAD**
```
Delgadas
```

**T19 · DECIDE**
```json
{
  "step": "step_4"
}
```

**T20 · LEAD**
```
Delgadas
```

**T21 · RECIBE**
```
¡Qué buena elección! Aquí tienes la cotización: ⏳(7 DIAS DE PROMO)⏳ 50 Sandalias Delgadas x $25 = $1,250 Envío: $300 Total: $1,550 Anticipo (50%): $775 *¡HAZ TU PEDIDO EN 7 SENCILLOS PASOS!*🚀 1. *COTIZACION de los PRODUCTOS que requiere para su PEDIDO* 2. Se requiere del *50% de ANTICIPO* para desarrollar los diseños. 3. *Elige tu DISEÑO favorito* 🎨 y proporciona los *DATOS* que deseas incluir. 4. Mandamos la *MUESTRA DIGITAL* para tu aprobación o cambios ✏️. 5. Una vez *AUTORIZADO, COMENZAMOS LA PRODUCCION*, son *15 DIAS EN PRODUCCION*. 🛠️ 6. Al terminar, te enviamos una *FOTO DEL PRODUCTO* para que confirmes que todo está perfecto 📸. 7. Hace el *PAGO FINAL* y te enviamos tu pedido 🚚 (tiempo de paquetería: 2 a 5 días). Mira, ya que pides sandalias, ¿le gustaría agregar cilindros o kits anticrudas para su evento? ¡Son un hit en XV Años! ✨ ¿Le gustaría avanzar con el pedido? Así le paso los números de cuenta para que pague el anticipo.
```

**T22 · LEAD**
```
Hola si me párese bien
```

**T23 · DECIDE**
```json
{
  "step": "step_4"
}
```

**T24 · LEAD**
```
Hola si me párese bien
```

**T25 · RECIBE**
```
¡Perfecto! 😊 Aquí tienes el enlace para realizar el pago del anticipo: [url1234.com123](url1234.com123). Por favor, envíame el comprobante del 50% de anticipo para seguir con el proceso. Cualquier duda, aquí estoy para ayudarte. ¡Gracias por elegir Happy Flops! ✨
```

**T26 · LEAD**
```
Disculpe sería de la de suela gruesa
```

**T27 · DECIDE**
```json
{
  "step": "step_3"
}
```

**T28 · LEAD**
```
Disculpe sería de la de suela gruesa
```

**T29 · RECIBE**
```
{}
```

**T30 · LEAD**
```
Disculpe sería de la de suela gruesa
```

**T31 · RECIBE**
```
{}
```

**T32 · LEAD**
```
Disculpe sería de la de suela gruesa
```

**T33 · RECIBE**
```
{}
```

**T34 · LEAD**
```
Disculpe sería de la de suela gruesa
```

**T35 · RECIBE**
```
{}
```

**T36 · LEAD**
```
Disculpe sería de la de suela gruesa
```

**T37 · RECIBE**
```
{}
```

**T38 · LEAD**
```
Disculpe sería de la de suela gruesa
```

**T39 · DECIDE**
```json
{
  "evento": "XV",
  "subcategoria": "Producto Principal",
  "productos": [
    "sandalias"
  ],
  "texto_dinamico": "¿Le interesa sumarlas a la cotización?\nDígame:\n- Cantidad\n- Código postal\n¡Gracias!"
}
```

**T40 · LEAD**
```
Disculpe no se resbalan al pisar en piso ? ? Son antiderapante
```

**T41 · DECIDE**
```json
{
  "step": "step_3"
}
```

**T42 · LEAD**
```
Disculpe no se resbalan al pisar en piso ? ? Son antiderapante
```

**T43 · DECIDE**
```json
{
  "evento": "XV",
  "subcategoria": "Producto Principal",
  "productos": [
    "sandalias"
  ],
  "texto_dinamico": ""
}
```

**T44 · LEAD**
```
50 piezas de la gruesa número 61800
```

**T45 · DECIDE**
```json
{
  "step": "step_4"
}
```

**T46 · LEAD**
```
50 piezas de la gruesa número 61800
```

**T47 · RECIBE**
```
¡Gracias por la corrección! Aquí tienes la cotización actualizada para las sandalias gruesas: ⏳(7 DIAS DE PROMO)⏳ 50 Sandalias Gruesas x $30 = $1,500 Envío: $300 Total: $1,800 Anticipo (50%): $900 *¡HAZ TU PEDIDO EN 7 SENCILLOS PASOS!*🚀 1. *COTIZACION de los PRODUCTOS que requiere para su PEDIDO* 2. Se requiere del *50% de ANTICIPO* para desarrollar los diseños. 3. *Elige tu DISEÑO favorito* 🎨 y proporciona los *DATOS* que deseas incluir. 4. Mandamos la *MUESTRA DIGITAL* para tu aprobación o cambios ✏️. 5. Una vez *AUTORIZADO, COMENZAMOS LA PRODUCCION*, son *15 DIAS EN PRODUCCION*. 🛠️ 6. Al terminar, te enviamos una *FOTO DEL PRODUCTO* para que confirmes que todo está perfecto 📸. 7. Hace el *PAGO FINAL* y te enviamos tu pedido 🚚 (tiempo de paquetería: 2 a 5 días). ¿Te gustaría avanzar con el pedido? Así te paso los números de cuenta para que pagues el anticipo.
```

**T48 · LEAD**
```
Hola si le encargo 50 pares de la de 30 pesos X favor
```

**T49 · DECIDE**
```json
{
  "step": "step_4"
}
```

**T50 · LEAD**
```
Hola si le encargo 50 pares de la de 30 pesos X favor
```

**T51 · RECIBE**
```
¡Perfecto! 😊 Aquí tienes el enlace para realizar el pago del anticipo: [url1234.com123](url1234.com123). Por favor, envíame el comprobante del 50% de anticipo para seguir con el proceso. Cualquier duda, aquí estoy para ayudarte. ¡Gracias por elegir Happy Flops! ✨
```

**T52 · LEAD**
```
Cuánto sería el anticipo ? Más tardesito le envío el anticipo cuantos días tarda en llegar disculpe
```

**T53 · DECIDE**
```json
{
  "step": "step_4"
}
```

**T54 · LEAD**
```
Cuánto sería el anticipo ? Más tardesito le envío el anticipo cuantos días tarda en llegar disculpe
```

**T55 · RECIBE**
```
El **anticipo** sería de **$900**. Una vez que recibamos el anticipo, la producción tarda 15 días naturales. Después, el envío toma de 2 a 5 días hábiles. Espero tu comprobante de anticipo para comenzar con el proceso. ¡Gracias por elegirnos! 😊
```

**T56 · LEAD**
```
Ok En un ratito se los envío
```

**T57 · DECIDE**
```json
{
  "step": "step_4"
}
```

**T58 · LEAD**
```
Ok En un ratito se los envío
```

**T59 · RECIBE**
```
¡Perfecto! Aguardamos el comprobante del anticipo para avanzar con tu pedido. Cualquier duda, aquí estoy para ayudarte. ¡Gracias por confiar en Happy Flops! ✨
```

**T60 · LEAD**
```
Hola no alcanse a depositar ayer por lo de mi trabajo Pero en un rato le deposito
```

**T61 · DECIDE**
```json
{
  "step": "step_4"
}
```

**T62 · LEAD**
```
Hola no alcanse a depositar ayer por lo de mi trabajo Pero en un rato le deposito
```

**T63 · RECIBE**
```
No te preocupes, está bien. 😊 Aguardamos tu depósito cuando puedas realizarlo. Cualquier cosa, aquí estoy para ayudarte. ¡Gracias por elegir Happy Flops! ✨
```

**T64 · LEAD**
```
Ahí mil gracias en un ratito le ago el deposito
```

**T65 · DECIDE**
```json
{
  "step": "step_4"
}
```

**T66 · LEAD**
```
Ahí mil gracias en un ratito le ago el deposito
```

**T67 · RECIBE**
```
¡Perfecto! Aguardamos tu depósito. Cualquier duda o consulta, aquí estoy para ayudarte. ¡Gracias por confiar en Happy Flops! 😊✨
```
