# Oraculo observado — sample_9

Fuente: `00_migracion_ghl/00_inputs/conversation_samples.json` (transcript real de produccion del bot legacy en Kommo).
session_hash: `b1d8aa5455bb3012122a959ba8172051` · turnos: 11

- `LEAD` = lo que escribio el cliente (ya saneado, listo para usar como input de test).
- `RECIBE` = lo que el bot original le mando al lead. **Esto es el esperado.**
- `DECIDE` = decision interna del Router/agente de productos. No la ve el lead.

---

**T1 · LEAD**
```
Hola buenos días me puedes dar información acerca del precio de sandalias
```

**T2 · RECIBE**
```
Hola! gracias por escribir a Happy Flops, me llamo Rebeca soy un asistente virtual, yo le estaré atendiendo con gusto ☺️🙋‍♀ Me podría decir de que es su evento? 🤵👰 - Boda 🎂🥳 - XV Años 👼🏢 - Otros
```

**T3 · LEAD**
```
Xv años
```

**T4 · DECIDE**
```json
{
  "step": "step_2"
}
```

**T5 · LEAD**
```
Xv años
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
Precio de todos
```

**T8 · DECIDE**
```json
{
  "step": "step_3"
}
```

**T9 · LEAD**
```
Precio de todos
```

**T10 · DECIDE**
```json
{
  "evento": "XV",
  "subcategoria": "Producto Principal",
  "productos": [
    "pantuflas",
    "sandalias",
    "cilindros",
    "mandiles",
    "anticrudas",
    "vasos"
  ],
  "texto_dinamico": "¿Le interesa sumarlos a la cotización?\nDígame:\n- Cantidad\n- Código postal\n¡Gracias!"
}
```

**T11 · RECIBE**
```
Hola 😄, para poder enviarte la cotización necesito que me compartas la cantidad y el código postal 📦
```
