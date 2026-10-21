# Oraculo observado — sample_1

Fuente: `00_migracion_ghl/00_inputs/conversation_samples.json` (transcript real de produccion del bot legacy en Kommo).
session_hash: `90ca0b3809efffad65b9ea6829292bff` · turnos: 14

- `LEAD` = lo que escribio el cliente (ya saneado, listo para usar como input de test).
- `RECIBE` = lo que el bot original le mando al lead. **Esto es el esperado.**
- `DECIDE` = decision interna del Router/agente de productos. No la ve el lead.

---

**T1 · LEAD**
```
¡Hola! Quiero más información. Buenos días k precio tienen?!?
```

**T2 · RECIBE**
```
Hola! gracias por escribir a Happy Flops, me llamo Rebeca soy un asistente virtual, yo le estaré atendiendo con gusto ☺️🙋‍♀" Me podría decir de que es su evento? 🤵👰 - Boda 🎂🥳 - XV Años 👼🏢 - Otros
```

**T3 · LEAD**
```
XV años
```

**T4 · DECIDE**
```json
{
  "step": "step_2"
}
```

**T5 · LEAD**
```
XV años
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
Kiero de sandalias y cilindros Y k es kit anti cruda?!? Ya vi
```

**T8 · DECIDE**
```json
{
  "step": "step_3"
}
```

**T9 · LEAD**
```
Kiero de sandalias y cilindros Y k es kit anti cruda?!? Ya vi
```

**T10 · DECIDE**
```json
{
  "evento": "XV",
  "subcategoria": "Producto Principal",
  "productos": [
    "sandalias",
    "cilindros",
    "anticrudas"
  ],
  "texto_dinamico": "¿Le interesa sumarlos a la cotización?\nDígame:\n- Cantidad\n- Código postal\n¡Gracias!"
}
```

**T11 · LEAD**
```
Buenas tardes disculpe será k me duren de AKI hasta noviembre
```

**T12 · DECIDE**
```json
{
  "step": "step_4"
}
```

**T13 · LEAD**
```
Buenas tardes disculpe será k me duren de AKI hasta noviembre
```

**T14 · RECIBE**
```
Claro, nuestros productos están diseñados para durar y ser de alta calidad. Si realiza su pedido ahora, tendrá suficiente tiempo para recibirlos y almacenarlos hasta su evento en noviembre. 😊 Para poder cotizarle las sandalias y cilindros, necesitaría que me diga la cantidad de cada uno y su código postal. Además, si las sandalias son delgadas o gruesas. ¡Gracias!
```
