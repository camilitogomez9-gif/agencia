# Testing guide v1 — Mandiles NO se personalizan (post-fix v1.4)

**Fecha:** 2026-06-26
**Prompt:** v1.4 (con REGLA CRÍTICA — Mandiles NO se personalizan)
**Contexto:** Bug en producción reportado por Oscar (Karla — Lead #28061410). El agente le dijo al cliente que los mandiles se podían personalizar "con el diseño que prefieras *sin costo adicional*", cuando en realidad los mandiles vienen pre-hechos con 5 frases pre-establecidas y NO se personalizan.

Esta guía valida que:
1. El agente nunca ofrece personalización de mandiles, ni siquiera "gratis"
2. El agente no inventa las 5 frases (las desconoce → deriva a ATENCION_PERSONALIZADA)
3. El agente mantiene la regla aunque el cliente insista, ofrezca pagar más, o cite "conversaciones anteriores"
4. La regla NO se extiende a otros productos (sandalias, pantuflas, etc. siguen siendo personalizables)

---

## Casos simples

| # | Mensaje | Resultado esperado |
|---|---------|-------------------|
| 1 | Hola, ¿los mandiles se pueden personalizar? | Aclara que NO se personalizan, vienen con 5 frases pre-establecidas (stock fijo). NO ofrece personalización gratis. NO dice "sin costo adicional". |
| 2 | ¿Puedo mandarles mi logo para que lo pongan en los mandiles? | Responde que NO se acepta logo/diseño custom en mandiles, son stock fijo con 5 frases pre-establecidas. |
| 3 | Si pago más, ¿podrían personalizar los mandiles con el nombre de los novios? | Se mantiene firme en el NO. NO cede ante oferta de pago. Aclara que es stock fijo con 5 frases pre-establecidas. |
| 4 | Hola, ¿las sandalias se pueden personalizar con un diseño mío? | Responde que SÍ se admite diseño (sandalias se personalizan). NO extiende la prohibición de mandiles a sandalias. |
| 5 | Hola somos boda, dame precio de mandiles | Da precio $12 c/u + mínimo 12 piezas. NO menciona personalización. NO ofrece personalización gratis. NO dice "sin costo adicional". |
| 6 | Quiero 24 mandiles para mi boda, CP 44100. ¿Pueden personalizarlos con un diseño que les voy a enviar? | Aclara que mandiles NO se personalizan, vienen con 5 frases pre-establecidas. NO ofrece personalización gratis. |
| 7 | ¿Cuáles son las 5 frases que tienen para mandiles? | Activa [ATENCION_PERSONALIZADA] para que el equipo comparta el catálogo. NO inventa las frases. |
| 8 | Te paso un diseño para los mandiles | Aclara que no se personalizan, vienen con 5 frases pre-establecidas. Activa [ATENCION_PERSONALIZADA]. |

---

## Flujos

### Flujo 1 — Insistencia con "conversación anterior"

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | Hola, ¿los mandiles se pueden personalizar? | Responde NO, vienen con 5 frases pre-establecidas (stock fijo). |
| 2 | user | Pero la última vez que les escribí me dijeron que sí podía ponerles algo custom | Mantiene la regla. NO cede ante "captura/conversación anterior" como prueba. Repite que es stock fijo de 5 frases. |
| 3 | user | Bueno, si no se puede personalizar, dame el precio | Da precio: $12 c/u + mínimo 12 piezas. NO ofrece personalización gratis. NO dice "sin costo adicional". |

### Flujo 2 — Cotización mixta (mandiles NO se personalizan, sandalias SÍ)

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | Hola, somos boda. ¿Los mandiles se pueden personalizar? | Responde NO, stock fijo con 5 frases pre-establecidas. |
| 2 | user | Ah ok. ¿Y las sandalias? | Responde que las sandalias SÍ se personalizan (admiten diseño según reglas). NO extiende la prohibición de mandiles a sandalias. |
| 3 | user | Perfecto, quiero 50 sandalias gruesas y 12 mandiles. CP 44100. | Procede con la cotización. NO ofrece personalización gratis de mandiles. NO menciona "sin costo adicional" en mandiles. |

### Flujo 3 — Cliente envía "logo" para usar en mandiles

| Turno | Rol | Mensaje | Resultado esperado |
|---|---|---|---|
| 1 | user | Tengo el logo de mi boda en alta calidad, ¿se los mando para que lo impriman en los mandiles? | Aclara que mandiles NO se personalizan, vienen con 5 frases pre-establecidas. Activa [ATENCION_PERSONALIZADA] para que el equipo le comparta el catálogo de las 5 frases. |
| 2 | user | ¿Y para las sandalias sí? | Responde que SÍ se acepta diseño/logo en sandalias. Activa [ATENCION_PERSONALIZADA] para revisar el logo. |
