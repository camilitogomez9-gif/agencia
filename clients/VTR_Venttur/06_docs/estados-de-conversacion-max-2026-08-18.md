# Estados de conversación — definición de Max (2026-08-18)

> Cierra el Hallazgo 5 del Reporte la agencia 1, que era el único punto que no se podía resolver sin el
> cliente. Fuente: WhatsApp de Max Almonte, 2026-08-18 13:11.

## Lo que definió Max

**Conversaciones positivas → cierre**
1. Cuando **agenda**, después del mensaje de confirmación de cita.
2. Cuando el usuario, después del remarketing, **dice que por el momento no le es posible**.
3. Cuando recibió el link de agendamiento y **después de 3 intentos de remarketing no contesta ni agenda**.

**Conversaciones interrumpidas**
- Después de **2 o 3 intentos de rescate** sin respuesta.

**Conversaciones perdidas**
- Cuando tras **2 intentos de remarketing** no hay respuesta.

**Reapertura** (decisión de la agencia, misma conversación): el lead se marca `cerrada` / `interrumpida` /
`perdida`, y **si en el futuro se le hace remarketing se cambia el estado a `remarketing`** o similar.
O sea: la reapertura es **un cambio de estado explícito y deliberado**, nunca un efecto colateral de
que entre un mensaje.

---

## ✅ Contradicción resuelta — el tope es 2 (la agencia, 2026-08-18)

Se confirmó **2**. Las reglas de cierre de Max que hablaban de "3 intentos" se ajustan a 2: el
positivo caso 3 y "perdida" comparten disparador (link enviado + tope agotado sin respuesta), y lo
que los distingue es **si el lead respondió alguna vez**, no el número de toques. En la práctica, un
lead que respondió pasa a `Contestó` y sale del pool antes de agotar el tope, así que la salida
terminal desde el despachador es siempre **`Perdida`**.

<details>
<summary>Detalle de la contradicción original (referencia)</summary>

### Contradicción con el tope de toques

Max define dos de los cierres contando **3 intentos** de remarketing (positivo caso 3) y **2 o 3**
intentos de rescate (interrumpida). Pero el 2026-08-18 se deployó el **tope global de 2 toques
proactivos por contacto** — que sale de la recomendación explícita del propio reporte
(*"limitar la secuencia de remarketing a un máximo de 2 intentos sin respuesta"*) y de la decisión de
la agencia de aplicarlo de forma global.

**Con el tope en 2, el estado "3 intentos" nunca se alcanza.** Hay que elegir:

| Opción | Qué implica |
|---|---|
| **A — Ajustar las reglas de cierre a 2 (recomendada)** | Positivo caso 3 y "perdida" colapsan en el mismo disparador: link enviado + 2 toques agotados sin respuesta. Coherente con el tope y con el reporte. La distinción positivo/perdido pasa a depender de si hubo o no alguna respuesta previa del lead, no del número de toques. |
| **B — Subir el tope a 3** | Contradice la recomendación del reporte y vuelve a exponer la cuenta de WhatsApp: los 34 fallos de entrega crecían justamente con cada toque adicional, y `boarding_form_followup_touch3` fue el segundo peor con 11. |

**Elegida: A.**

</details>

---

## Qué falta construir

`Estado conversación` (single-select de Airtable) tiene ahora **7 valores**: los 4 originales
(`Activa` · `Contestó` · `Cita confirmada` · `Conversación interrumpida`) más los 3 que agregó la agencia el
2026-08-18 (`Cerrada` · `Perdida` · `Remarketing`).

| Estado | Cuándo se escribe | Quién lo escribiría | ¿Existe hoy? |
|---|---|---|---|
| `Activa` | alta del lead | alta | ✅ |
| `Contestó` | cada mensaje entrante | `Estampar estado (Contestó)` — **ya vivo**, 18 ejecuciones OK | ✅ |
| `Cita confirmada` | **después** del envío de la confirmación | `confirmacion-agenda` | ✅ (el marcado se movió a después del envío el 2026-08-18) |
| **`Cerrada`** | lead dice "por ahora no puedo" | agente — **requiere desarrollo nuevo** | ⚠️ valor creado, sin escritor |
| **`Perdida`** | tope de 2 toques agotado sin respuesta | **despachador — ✅ implementado** | ✅ |
| **`Remarketing`** | reactivación deliberada | acción manual o campaña futura | ⚠️ valor creado, sin escritor |

### Pasos, en orden

1. ✅ **Los 3 valores agregados** al single-select `Estado conversación` (la agencia, 2026-08-18), con la
   grafía **`Cerrada` · `Perdida` · `Remarketing`** — confirmada por la agencia, es exactamente la que
   escribe el código. (El schema que cachea n8n sigue mostrando sólo los 4 valores viejos porque se
   cachea al configurar cada nodo; no es un indicador del estado real de la base.)
2. ✅ **`confirmacion-agenda`**: `Agendan cita = true` movido a **después** del envío. La cadena pasó
   de `If → marcado → Switch → … → Enviar*` a `If → Switch → … → Enviar* → marcado`. Ese nodo ya
   escribía `Estado conversación = Cita confirmada`. Ahora "agendó" y "se lo confirmamos" son el
   mismo hecho: si el envío falla, el lead **no** queda marcado, sigue recibiendo seguimiento y salta
   la alerta de Telegram.
3. ✅ **Despachador**: al agotar el tope escribe `Estado conversación = Perdida`, y excluye del pool
   `Cerrada`, `Perdida` y `Conversación interrumpida` (ya excluía `Cita confirmada` y `Contestó`).
   Nunca borra el estado: si el lead no llegó al tope, reescribe el que ya tenía. Probado con 4 casos.
4. ⏳ **Detectar "por ahora no puedo"**: es intención del lead, no un contador. Necesita regla en el
   prompt + una tool que escriba `Cerrada`. **Es el único punto del modelo de Max que queda sin
   implementar**, y requiere desarrollo nuevo.
5. ✅ Hecho como parte del punto 3.

### Sobre el "Cerrado" de ManyChat

El estado que Max vio en el caso Benjamin Dozal vive **sólo en el inbox de ManyChat** y ManyChat
**reabre la conversación automáticamente** ante cualquier mensaje entrante — eso no se puede evitar
desde afuera. Por eso el estado tiene que vivir en Airtable: es la única capa donde podemos decidir
que un mensaje entrante **no** reinicie el ciclo comercial.

Mientras eso no exista, lo que ya está mitigado del Hallazgo 5 es la parte que hacía daño real:
el guard `¿Programa ya definido?` (deployado el 2026-08-18) impide que un mensaje fuera de tema
**reasigne el programa de interés** y, por esa vía, dispare el drip.
