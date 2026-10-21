# Oraculo observado — sample_10

Fuente: `00_migracion_ghl/00_inputs/conversation_samples.json` (transcript real de produccion del bot legacy en Kommo).
session_hash: `1da0a6b7a01116fdd8c005319cbf7489` · turnos: 16

- `LEAD` = lo que escribio el cliente (ya saneado, listo para usar como input de test).
- `RECIBE` = lo que el bot original le mando al lead. **Esto es el esperado.**
- `DECIDE` = decision interna del Router/agente de productos. No la ve el lead.

---

**T1 · LEAD**
```
¡Hola! Quiero más información. Precios !!!
```

**T2 · RECIBE**
```
Hola! gracias por escribir a Happy Flops, me llamo Rebeca soy un asistente virtual, yo le estaré atendiendo con gusto ☺️🙋‍♀ Me podría decir de que es su evento? 🤵👰 - Boda 🎂🥳 - XV Años 👼🏢 - Otros
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
Me manda cotización de los vasos y sandalias
```

**T8 · DECIDE**
```json
{
  "step": "step_3"
}
```

**T9 · LEAD**
```
Me manda cotización de los vasos y sandalias
```

**T10 · DECIDE**
```json
{
  "evento": "XV",
  "subcategoria": "Producto Principal",
  "productos": [
    "vasos",
    "sandalias"
  ],
  "texto_dinamico": "¿Le interesa sumarlos a la cotización?\nDígame:\n- Cantidad\n- Código postal\n¡Gracias!"
}
```

**T11 · LEAD**
```
Me manda cotización de los vasos y sandalias
```

**T12 · RECIBE**
```
Para poder cotizarle las sandalias y los vasos, necesitaría que me diga la cantidad de cada uno, el código postal para el envío, y si las sandalias son delgadas o gruesas. 😊
```

**T13 · LEAD**
```
Son los unicos diseños de vasos que tiene ?
```

**T14 · DECIDE**
```json
{
  "step": "step_4"
}
```

**T15 · LEAD**
```
Son los unicos diseños de vasos que tiene ?
```

**T16 · RECIBE**
```
He consultado con nuestro equipo sobre los diseños de vasos. Pronto te responderemos con más detalles. ¿Te gustaría que te cotice algo más mientras tanto? 😊
```
