# Oraculo observado — sample_8

Fuente: `00_migracion_ghl/00_inputs/conversation_samples.json` (transcript real de produccion del bot legacy en Kommo).
session_hash: `10c76886521c006d824ac9ebc85e91c7` · turnos: 42

- `LEAD` = lo que escribio el cliente (ya saneado, listo para usar como input de test).
- `RECIBE` = lo que el bot original le mando al lead. **Esto es el esperado.**
- `DECIDE` = decision interna del Router/agente de productos. No la ve el lead.

---

**T1 · LEAD**
```
Precio de sandalias ?
```

**T2 · RECIBE**
```
Hola! gracias por escribir a Happy Flops, me llamo Rebeca soy un asistente virtual, yo le estaré atendiendo con gusto ☺️🙋‍♀ Me podría decir de que es su evento? 🤵👰 - Boda 🎂🥳 - XV Años 👼🏢 - Otros
```

**T3 · LEAD**
```
XV
```

**T4 · DECIDE**
```json
{
  "step": "step_2"
}
```

**T5 · LEAD**
```
XV
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
Sandalias 🩴
```

**T8 · DECIDE**
```json
{
  "step": "step_3"
}
```

**T9 · LEAD**
```
Sandalias 🩴
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
Te envio una imagen del producto que quiero: Pantuflas
```

**T15 · RECIBE**
```
Qué diseño tan bonito de pantuflas! 😊 ¿Quieres que continuemos con el proceso para cotizar y hacer tu pedido?
```

**T16 · LEAD**
```
Si
```

**T17 · DECIDE**
```json
{
  "step": "step_3"
}
```

**T18 · LEAD**
```
Si
```

**T19 · RECIBE**
```
{}
```

**T20 · LEAD**
```
Si
```

**T21 · RECIBE**
```
{}
```

**T22 · LEAD**
```
Si
```

**T23 · RECIBE**
```
{}
```

**T24 · LEAD**
```
Si
```

**T25 · DECIDE**
```json
{
  "evento": "XV",
  "subcategoria": "Producto Principal",
  "productos": [
    "pantuflas"
  ],
  "texto_dinamico": "¿Le interesa sumarlas a la cotización?\nDígame:\n- Cantidad\n- Código postal\n¡Gracias!"
}
```

**T26 · RECIBE**
```
Hola 😄, para poder enviarte la cotización necesito que me compartas la cantidad y el código postal 📦
```

**T27 · RECIBE**
```
Hola! 👋 Ya tengo tus productos seleccionados, solo me falta saber cuántas piezas necesitas y tu código postal para calcular el envío 🚚
```

**T28 · RECIBE**
```
Hola 😊, para apartar y cotizar tus productos necesito esos dos datos: cantidad y código postal. Así puedo enviarte tu cotización 📄
```

**T29 · LEAD**
```
XV
```

**T30 · DECIDE**
```json
{
  "step": "step_2"
}
```

**T31 · LEAD**
```
XV
```

**T32 · DECIDE**
```json
{
  "evento": "XV",
  "texto_dinamico": "Qué padre! 😊 \n🎉 *¡SEMANA LOCA DE PROMOS! SOLO 7 DÍAS PARA LLEVARTE TUS RECUERDITOS PERSONALIZADOS CON DESCUENTAZO* 🎉\n*(Pedidos solo para eventos 2026 por tema de tiempos)*"
}
```

**T33 · LEAD**
```
Te envio una imagen del producto que quiero: Sandalias
```

**T34 · RECIBE**
```
Qué diseño muy bonito de sandalias! 😊 ¿Quieres que continuemos con el proceso para cotizar y hacer tu pedido?
```

**T35 · LEAD**
```
Quiero de estas? Si haré pedido de 50 pzas solo puedo escoger un modelo? Si
```

**T36 · DECIDE**
```json
{
  "step": "step_4"
}
```

**T37 · LEAD**
```
Quiero de estas? Si haré pedido de 50 pzas solo puedo escoger un modelo? Si
```

**T38 · RECIBE**
```
Sí, para un pedido de 50 pares de sandalias, puedes elegir un solo diseño. 😊 Ahora, para poder cotizarte, ¿me podrías confirmar si las sandalias que deseas son delgadas o gruesas y tu código postal para calcular el envío? 📦
```

**T39 · LEAD**
```
Delgadas 84063
```

**T40 · DECIDE**
```json
{
  "step": "step_4"
}
```

**T41 · LEAD**
```
Delgadas 84063
```

**T42 · RECIBE**
```
¡Perfecto! Aquí tienes la cotización para tu pedido de **50 Sandalias Delgadas**: ⏳(7 DIAS DE PROMO)⏳ 50 Sandalias Delgadas x $25 = $1,250 Envío: $300 Total: $1,550 Anticipo (50%): $775 *¡HAZ TU PEDIDO EN 7 SENCILLOS PASOS!*🚀 1. *COTIZACION de los PRODUCTOS que requiere para su PEDIDO* 2. Se requiere del *50% de ANTICIPO* para desarrollar los diseños. 3. *Elige tu DISEÑO favorito* 🎨 y proporciona los *DATOS* que deseas incluir. 4. Mandamos la *MUESTRA DIGITAL* para tu aprobación o cambios ✏️. 5. Una vez *AUTORIZADO, COMENZAMOS LA PRODUCCION*, son *15 DIAS EN PRODUCCION*. 🛠️ 6. Al terminar, te enviamos una *FOTO DEL PRODUCTO* para que confirmes que todo está perfecto 📸. 7. Hace el *PAGO FINAL* y te enviamos tu pedido 🚚 (tiempo de paquetería: 2 a 5 días). ¿Te gustaría avanzar con el pedido? Así te paso los números de cuenta para que pagues el anticipo.
```
