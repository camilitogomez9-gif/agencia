# Oraculo observado — sample_3

Fuente: `00_migracion_ghl/00_inputs/conversation_samples.json` (transcript real de produccion del bot legacy en Kommo).
session_hash: `fe36446fcfceef841a4745cb777d765f` · turnos: 14

- `LEAD` = lo que escribio el cliente (ya saneado, listo para usar como input de test).
- `RECIBE` = lo que el bot original le mando al lead. **Esto es el esperado.**
- `DECIDE` = decision interna del Router/agente de productos. No la ve el lead.

---

**T1 · LEAD**
```
¡Hola! Quiero más información. Precios por favor
```

**T2 · RECIBE**
```
Hola! gracias por escribir a Happy Flops, me llamo Rebeca soy un asistente virtual, yo le estaré atendiendo con gusto ☺️🙋‍♀" Me podría decir de que es su evento? 🤵👰 - Boda 🎂🥳 - XV Años 👼🏢 - Otros
```

**T3 · LEAD**
```
Son 50 años
```

**T4 · DECIDE**
```json
{
  "step": "step_2"
}
```

**T5 · LEAD**
```
Son 50 años
```

**T6 · DECIDE**
```json
{
  "evento": "Boda",
  "texto_dinamico": "Qué padre! 😊 \n🎉 *¡SEMANA LOCA DE PROMOS! SOLO 7 DÍAS PARA LLEVARTE TUS RECUERDITOS PERSONALIZADOS CON DESCUENTAZO* 🎉\n*(Pedidos solo para eventos 2026 por tema de tiempos)*"
}
```

**T7 · LEAD**
```
Precio de los termos Pantuflas Sandalias Vasos por favor
```

**T8 · DECIDE**
```json
{
  "step": "step_3"
}
```

**T9 · LEAD**
```
Precio de los termos Pantuflas Sandalias Vasos por favor
```

**T10 · DECIDE**
```json
{
  "evento": "Boda",
  "subcategoria": "Producto Principal",
  "productos": [
    "cilindros",
    "pantuflas",
    "sandalias",
    "vasos"
  ],
  "texto_dinamico": "¿Le interesa sumarlos a la cotización?\nDígame:\n- Cantidad\n- Código postal\n¡Gracias!"
}
```

**T11 · LEAD**
```
Veo que son 15 días de anticipo
```

**T12 · DECIDE**
```json
{
  "step": "step_4"
}
```

**T13 · LEAD**
```
Veo que son 15 días de anticipo
```

**T14 · RECIBE**
```
Así es, el tiempo de producción es de 15 días naturales para productos personalizados. ¿Le gustaría que le cotice alguno de los productos? Si es así, por favor indíqueme la cantidad de cada producto y su código postal para calcular el envío. 😊
```
