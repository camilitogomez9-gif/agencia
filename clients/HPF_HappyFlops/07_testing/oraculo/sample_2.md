# Oraculo observado — sample_2

Fuente: `00_migracion_ghl/00_inputs/conversation_samples.json` (transcript real de produccion del bot legacy en Kommo).
session_hash: `45ad66a86a7d57ec95831edbd5c746e8` · turnos: 39

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

**T3 · RECIBE**
```
Hola 👋, sigues por aquí? Solo necesito que me cuentes qué tipo de evento tienes para poder ayudarte a elegir lo mejor para ti 🎉
```

**T4 · RECIBE**
```
Hola! 😄 Cuéntame, es para boda, XV años u otro evento? Así puedo enviarte las opciones de productos 💡
```

**T5 · RECIBE**
```
Hola 😊, no quiero que se te pase la oportunidad de encontrar los recuerdos perfectos para tu evento. De que es tu evento? 💍🎂🎈
```

**T6 · LEAD**
```
Q dueño tiene de chanclas Para 15 años 50 pzas Temática tiana
```

**T7 · DECIDE**
```json
{
  "step": "step_3"
}
```

**T8 · LEAD**
```
Q dueño tiene de chanclas Para 15 años 50 pzas Temática tiana
```

**T9 · DECIDE**
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

**T10 · LEAD**
```
Q dueño tiene de chanclas Para 15 años 50 pzas Temática tiana
```

**T11 · RECIBE**
```
Para poder cotizarle las sandalias necesitaría que me diga si las quiere delgadas o gruesas, además de su código postal para calcular el envío. 😊
```

**T12 · LEAD**
```
Con envío Cp. 30700
```

**T13 · DECIDE**
```json
{
  "step": "step_4"
}
```

**T14 · LEAD**
```
Con envío Cp. 30700
```

**T15 · RECIBE**
```
Para poder cotizarle las sandalias necesitaría que me diga si las quiere delgadas o gruesas. 😊
```

**T16 · LEAD**
```
Suela delgada
```

**T17 · DECIDE**
```json
{
  "step": "step_4"
}
```

**T18 · LEAD**
```
Suela delgada
```

**T19 · RECIBE**
```
¡Qué buena elección! Aquí está la cotización para tus sandalias delgadas: ⏳(7 DIAS DE PROMO)⏳ - 50 Sandalias Delgadas x $25 = $1,250 - Envío: $300 - **Total**: $1,550 - **Anticipo (50%)**: $775 *¡HAZ TU PEDIDO EN 7 SENCILLOS PASOS!*🚀 1. *COTIZACION de los PRODUCTOS que requiere para su PEDIDO* 2. Se requiere del *50% de ANTICIPO* para desarrollar los diseños. 3. *Elige tu DISEÑO favorito* 🎨 y proporciona los *DATOS* que deseas incluir. 4. Mandamos la *MUESTRA DIGITAL* para tu aprobación o cambios ✏️. 5. Una vez *AUTORIZADO, COMENZAMOS LA PRODUCCION*, son *15 DIAS EN PRODUCCION*. 🛠️. 6. Al terminar, te enviamos una *FOTO DEL PRODUCTO* para que confirmes que todo está perfecto 📸. 7. Hace el *PAGO FINAL* y te enviamos tu pedido 🚚 (tiempo de paquetería: 2 a 5 días). ¿Te gustaría avanzar con el pedido? Así te paso los números de cuenta para que pagues el anticipo. 😊
```

**T20 · LEAD**
```
Te envio una imagen del producto que quiero: Sandalias
```

**T21 · RECIBE**
```
¡Qué diseño tan bonito! 😊 ¿Quieres que continuemos con el proceso para tu pedido de sandalias delgadas?
```

**T22 · LEAD**
```
Si por favor
```

**T23 · DECIDE**
```json
{
  "step": "step_4"
}
```

**T24 · LEAD**
```
Si por favor
```

**T25 · RECIBE**
```
¡Perfecto! Para continuar, por favor envíame el diseño que deseas para las sandalias, y procederemos con el siguiente paso. 😊
```

**T26 · LEAD**
```
Voy
```

**T27 · DECIDE**
```json
{
  "step": "step_4"
}
```

**T28 · LEAD**
```
Voy
```

**T29 · RECIBE**
```
¡Perfecto! Espero tu diseño para continuar con el proceso. Si tienes alguna otra pregunta o necesitas ayuda, aquí estoy para ayudarte. 😊
```

**T30 · LEAD**
```
La chanclas quiero 50 pza .
```

**T31 · DECIDE**
```json
{
  "step": "step_4"
}
```

**T32 · LEAD**
```
La chanclas quiero 50 pza .
```

**T33 · RECIBE**
```
¡Entendido! Ya tengo la información para tu pedido de 50 sandalias delgadas. Si ya tienes el diseño listo, por favor envíamelo para que podamos avanzar con el proceso. 😊
```

**T34 · LEAD**
```
Te envio una imagen del producto que quiero: Sandalias
```

**T35 · RECIBE**
```
¡Qué diseño tan bonito! 😊 ¿Quieres que continuemos con el proceso para tu pedido de 50 sandalias delgadas?
```

**T36 · LEAD**
```
Si Por favor
```

**T37 · DECIDE**
```json
{
  "step": "step_4"
}
```

**T38 · LEAD**
```
Si Por favor
```

**T39 · RECIBE**
```
¡Perfecto! Para continuar, por favor envíame el diseño que deseas para las sandalias, y procederemos con el siguiente paso. 😊
```
