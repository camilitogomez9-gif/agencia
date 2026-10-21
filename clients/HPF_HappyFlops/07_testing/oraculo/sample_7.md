# Oraculo observado — sample_7

Fuente: `00_migracion_ghl/00_inputs/conversation_samples.json` (transcript real de produccion del bot legacy en Kommo).
session_hash: `38ba1bce67f338918b31ad206bec99b9` · turnos: 26

- `LEAD` = lo que escribio el cliente (ya saneado, listo para usar como input de test).
- `RECIBE` = lo que el bot original le mando al lead. **Esto es el esperado.**
- `DECIDE` = decision interna del Router/agente de productos. No la ve el lead.

---

**T1 · LEAD**
```
¡Hola! Quiero más información.
```

**T2 · RECIBE**
```
Hola! gracias por escribir a Happy Flops, me llamo Rebeca soy un asistente virtual, yo le estaré atendiendo con gusto ☺️🙋‍♀ Me podría decir de que es su evento? 🤵👰 - Boda 🎂🥳 - XV Años 👼🏢 - Otros
```

**T3 · LEAD**
```
Hola XV
```

**T4 · DECIDE**
```json
{
  "step": "step_2"
}
```

**T5 · LEAD**
```
Hola XV
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
Pantuflas
```

**T8 · DECIDE**
```json
{
  "step": "step_3"
}
```

**T9 · LEAD**
```
Pantuflas
```

**T10 · DECIDE**
```json
{
  "evento": "XV",
  "subcategoria": "Producto Principal",
  "productos": [
    "pantuflas"
  ],
  "texto_dinamico": "¿Le interesa sumarlos a la cotización?\nDígame:\n- Cantidad\n- Código postal\n¡Gracias!"
}
```

**T11 · LEAD**
```
Me interesa esta Cuando termina la oferta ???
```

**T12 · DECIDE**
```json
{
  "step": "step_4"
}
```

**T13 · LEAD**
```
Me interesa esta Cuando termina la oferta ???
```

**T14 · RECIBE**
```
La oferta termina en 7 días, así que tienes hasta el 10 de mayo para aprovecharla. 😊 Para poder cotizarle las pantuflas, necesitaría que me diga la cantidad que desea y su código postal.
```

**T15 · LEAD**
```
Podrían ser 60 piezas ??? El código postal es 59230
```

**T16 · DECIDE**
```json
{
  "step": "step_4"
}
```

**T17 · LEAD**
```
Podrían ser 60 piezas ??? El código postal es 59230
```

**T18 · RECIBE**
```
¡Qué buena elección! Aquí tienes la cotización: ⏳(7 DIAS DE PROMO)⏳ 60 Pantuflas x $30 = $1,800 Envío: $300 Total: $2,100 Anticipo (50%): $1,050 *¡HAZ TU PEDIDO EN 7 SENCILLOS PASOS!*🚀 1. *COTIZACION de los PRODUCTOS que requiere para su PEDIDO* 2. Se requiere del *50% de ANTICIPO* para desarrollar los diseños. 3. *Elige tu DISEÑO favorito* 🎨 y proporciona los *DATOS* que deseas incluir. 4. Mandamos la *MUESTRA DIGITAL* para tu aprobación o cambios ✏️. 5. Una vez *AUTORIZADO, COMENZAMOS LA PRODUCCION*, son *15 DIAS EN PRODUCCION*. 🛠️ 6. Al terminar, te enviamos una *FOTO DEL PRODUCTO* para que confirmes que todo está perfecto 📸. 7. Hace el *PAGO FINAL* y te enviamos tu pedido 🚚 (tiempo de paquetería: 2 a 5 días). ¿Le gustaría avanzar con el pedido? Así le paso los números de cuenta para que pague el anticipo.
```

**T19 · LEAD**
```
La verdad si lo haré pero en un par de días más 🙏🏻
```

**T20 · DECIDE**
```json
{
  "step": "step_4"
}
```

**T21 · LEAD**
```
La verdad si lo haré pero en un par de días más 🙏🏻
```

**T22 · RECIBE**
```
¡Perfecto! 😊 No hay problema, aquí estaré para ayudarte cuando estés listo para avanzar con el pedido. Recuerda que la oferta es válida hasta el 10 de mayo. Si tienes alguna otra pregunta o necesitas más información, no dudes en escribirme. ¡Gracias por considerar Happy Flops para tu evento! ✨
```

**T23 · LEAD**
```
Sii te agradezco!!!
```

**T24 · DECIDE**
```json
{
  "step": "step_4"
}
```

**T25 · LEAD**
```
Sii te agradezco!!!
```

**T26 · RECIBE**
```
¡De nada! Aquí estaré para cualquier cosa que necesites. ¡Que tengas un excelente día! 😊✨
```
