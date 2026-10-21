# Oraculo observado — sample_6

Fuente: `00_migracion_ghl/00_inputs/conversation_samples.json` (transcript real de produccion del bot legacy en Kommo).
session_hash: `74c2858b18f874eb5f85e2b06a15b94c` · turnos: 28

- `LEAD` = lo que escribio el cliente (ya saneado, listo para usar como input de test).
- `RECIBE` = lo que el bot original le mando al lead. **Esto es el esperado.**
- `DECIDE` = decision interna del Router/agente de productos. No la ve el lead.

---

**T1 · LEAD**
```
Hola buen dia! quiero mas informacion sobre Happy Flops sobre los vasos Que precio tienen
```

**T2 · RECIBE**
```
Hola! gracias por escribir a Happy Flops, me llamo Rebeca soy un asistente virtual, yo le estaré atendiendo con gusto ☺️🙋‍♀ Me podría decir de que es su evento? 🤵👰 - Boda 🎂🥳 - XV Años 👼🏢 - Otros
```

**T3 · LEAD**
```
xv años
```

**T4 · DECIDE**
```json
{
  "step": "step_2"
}
```

**T5 · LEAD**
```
xv años
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
Vasos Y sandalias
```

**T8 · DECIDE**
```json
{
  "step": "step_3"
}
```

**T9 · LEAD**
```
Vasos Y sandalias
```

**T10 · DECIDE**
```json
{
  "evento": "XV",
  "subcategoria": "Producto Principal",
  "productos": [
    "cilindros",
    "sandalias"
  ],
  "texto_dinamico": "¿Le interesa sumarlos a la cotización?\nDígame:\n- Cantidad\n- Código postal\n¡Gracias!"
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
Buenos días Quisiera saber el precio de paquetes de sandalias y pantunflas
```

**T15 · DECIDE**
```json
{
  "step": "step_3"
}
```

**T16 · LEAD**
```
Buenos días Quisiera saber el precio de paquetes de sandalias y pantunflas
```

**T17 · RECIBE**
```
{}
```

**T18 · LEAD**
```
Buenos días Quisiera saber el precio de paquetes de sandalias y pantunflas
```

**T19 · RECIBE**
```
{}
```

**T20 · LEAD**
```
Buenos días Quisiera saber el precio de paquetes de sandalias y pantunflas
```

**T21 · RECIBE**
```
{}
```

**T22 · LEAD**
```
Buenos días Quisiera saber el precio de paquetes de sandalias y pantunflas
```

**T23 · RECIBE**
```
{}
```

**T24 · LEAD**
```
Buenos días Quisiera saber el precio de paquetes de sandalias y pantunflas
```

**T25 · RECIBE**
```
{}
```

**T26 · LEAD**
```
Buenos días Quisiera saber el precio de paquetes de sandalias y pantunflas
```

**T27 · DECIDE**
```json
{
  "evento": "XV",
  "subcategoria": "Producto Principal",
  "productos": [
    "sandalias",
    "pantuflas"
  ],
  "texto_dinamico": "¿Le interesa sumarlos a la cotización?\nDígame:\n- Cantidad\n- Código postal\n¡Gracias!"
}
```

**T28 · RECIBE**
```
Hola 😄, para poder enviarte la cotización necesito que me compartas la cantidad y el código postal 📦
```
