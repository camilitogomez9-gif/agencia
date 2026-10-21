# Incidente — Confusión de moneda (MXN vs USD) en cotización B2B

**Fecha:** 2026-06-05
**Reportado por:** Mauricio García de la Vega (grupo)
**Lead afectado:** Oscar Amaya
**Prompt vigente al momento del incidente:** B2B v1.4 (recién bumpeado)
**Severidad:** Alta — el agente prometió Opción B (puesta en México) a un lead cuyo presupuesto no la cubría.

---

## §1 — Mensajes verbatim de Mauricio (WhatsApp del grupo)

```
[5/6/26, 16:41:31] ~ Mauricio: Excelente, Oscar. Con un presupuesto de $250,000 pesos
                                entras justo en el rango para la opción de máquina lista
                                para operar en México, con todo incluido y soporte local.
                                Esta opción te permite tener el negocio funcionando desde
                                el primer día y puedes operar bajo tu propia marca

[5/6/26, 16:41:35] ~ Mauricio: contesto esto el agente
[5/6/26, 16:41:43] ~ Mauricio: ya me meti en un problema!
[5/6/26, 16:41:44] ~ Mauricio: jajaja
[5/6/26, 16:41:49] ~ Mauricio: como se ajusta esto?

[5/6/26, 16:44:13] ~ Mauricio: revisa el chat de oscar amaya
[5/6/26, 16:44:20] ~ Mauricio: ahi se ve el contexto
[5/6/26, 16:44:37] ~ Mauricio: La máquina vale $26,300 que son alrededor de 460,000 pesos

[5/6/26, 16:45:20] ~ Mauricio: Entonces si esta persona tiene presupuesto de 250,000, pues
                                no le alcanza para comprar la máquina, sólo podría comprarla
                                puesta en China y que él se encargue de hacer todos los
                                trámites, pero seguro no le va a alcanzar por la cantidad
                                de impuestos y aranceles, etc. entonces me gustaría que se
                                le ofreciera financiamiento que puede buscar a través de
                                una arrendadora o una financiera nosotros nos damos
                                financiamiento directo, pero las máquinas se les entrega
                                factura y pueden obtener financiamiento a través de un
                                banco, un arrendadora o una financiera
```

> Nota: leyendo entre líneas el mensaje de las 16:45, Mauricio dice "**no** damos financiamiento directo" (hay un typo, pero el sentido es claro: TOFO no financia, el cliente busca financiamiento externo con la factura como aval).

---

## §2 — Diagnóstico del incidente

### 2.1 Lo que dijo el lead
Oscar habría declarado un presupuesto de **$250,000** (sin especificar moneda).

### 2.2 Lo que asumió el agente
El agente asumió que $250,000 era una cifra en **USD**, comparó con los precios USD oficiales ($9,300 A / $26,300 B) y respondió que "entra justo" en Opción B.

### 2.3 Lo que era correcto
- $250,000 en contexto mexicano casi siempre = **pesos mexicanos**.
- $250,000 MXN ≈ $14,300 USD (al cambio de referencia ~17.5 MXN/USD).
- **NO cubre Opción B** ($26,300 USD ≈ $460,000 MXN).
- **Sí cubriría el sticker de Opción A** ($9,300 USD ≈ $165,000 MXN), pero después no le quedaría margen para arancel 40% + flete + seguro + aduana — **probablemente tampoco le alcanza para Opción A end-to-end**.

### 2.4 Falla técnica
El prompt v1.4 **no obliga al agente a validar la moneda** del presupuesto antes de cotizar. Asume que cualquier número es USD (la moneda nativa de las opciones).

### 2.5 Falla operativa
El prompt v1.4 **no menciona financiamiento como opción**. Cuando el lead no cubre el sticker, el agente no tiene una vía alternativa que ofrecer — termina cerrando la conversación o (peor) prometiendo algo que no se va a sostener.

---

## §3 — Reglas nuevas para B2B v1.5

### 3.1 Protocolo de moneda (regla absoluta)

**Antes** de mencionar cualquier opción o "te alcanza", el agente DEBE:

1. **Detectar ambigüedad**: si el lead dice un número (presupuesto, inversión disponible, capacidad de pago) sin especificar moneda, NO asumir. Preguntar:
   > "¿Tu presupuesto es en pesos mexicanos o en dólares?"

2. **Asumir MXN por default si el lead está en México** y no responde de inmediato (no especular en USD).

3. **Convertir mentalmente** usando referencia: **~17.5 MXN/USD** (TC referencial 2026; el TC final lo confirma el director en la llamada).
   - Para convertir USD → MXN: multiplicar por 17.5.
   - Para convertir MXN → USD: dividir entre 17.5.

4. **Comunicar siempre los precios en ambas monedas** cuando hable de opciones:
   - Opción A: $9,300 USD + IVA (~$165,000 MXN aproximado al TC de referencia)
   - Opción B: $26,300 USD + IVA (~$460,000 MXN aproximado al TC de referencia)
   - Disclaimer: "el tipo de cambio final lo confirma el director en la llamada".

5. **No prometer elegibilidad sin confirmar moneda**.

### 3.2 Equivalencias canónicas (datos autorizados)

| Concepto | USD | MXN (referencia ~17.5) |
|---|---|---|
| Opción A — Máquina puesta en China | $9,300 + IVA | ~$165,000 + IVA |
| Opción B — Máquina puesta en México | $26,300 + IVA | ~$460,000 + IVA |
| TC de referencia | — | ~17–18 MXN/USD |

Disclaimer obligatorio cuando se cite la equivalencia en MXN:
> "La cifra en pesos es referencial — el tipo de cambio final lo confirma el director en la llamada."

### 3.3 Sección de financiamiento (nuevo dato canónico)

**TOFO Pizza NO da financiamiento directo.**

Las máquinas se entregan **con factura**. Con esa factura, el cliente puede buscar financiamiento externo en:

- **Bancos** (tarjetas, líneas de crédito empresarial)
- **Arrendadoras** (leasing financiero/operativo)
- **Financieras** (créditos específicos para equipo)

Caso de uso típico: el lead tiene parte del capital pero no lo cubre completo → ofrecer la vía de financiamiento + agendar llamada con director para que él oriente sobre qué opción le conviene según su perfil.

### 3.4 Reacción cuando el presupuesto NO alcanza

Tres ramas según diferencia:

| Presupuesto vs Opción | Reacción del agente |
|---|---|
| **Cubre Opción B** ($26.3k USD / ~$460k MXN) | Cotizar Opción B directamente |
| **Cubre Opción A** ($9.3k USD / ~$165k MXN) pero NO B | Aclarar que la Opción A "puesta en China" tiene **costos adicionales** (arancel 40%, flete, seguro, aduana) que NO están incluidos en el precio base. Probablemente NO le va a alcanzar end-to-end. Ofrecer financiamiento + agendar llamada con director. |
| **NO cubre ni A** | Explicar de inmediato que el monto no cubre el sticker base. Ofrecer **financiamiento externo** como vía (banco / arrendadora / financiera, con la factura de TOFO como aval). Agendar llamada con director para que oriente qué camino conviene. |

🚫 **NO** prometer Opción B si el presupuesto en MXN no llega a ~$460,000.
🚫 **NO** prometer Opción A end-to-end si el presupuesto en MXN es menor a ~$200,000-$250,000 (deja muy poco margen para impuestos/flete).
🚫 **NO** decir "te alcanza" sin haber confirmado moneda primero.

### 3.5 Respuestas modelo nuevas

➤ Si menciona presupuesto en cifra ambigua:
> "Antes de aterrizar la opción ideal, ¿ese presupuesto es en pesos mexicanos o en dólares? Es solo para no confundirnos con el tipo de cambio 😊"

➤ Si el presupuesto cubre Opción B:
> "Con ese presupuesto entras en la Opción B (puesta en México, ~$460,000 MXN o $26,300 USD + IVA), que llega lista para operar con tu marca desde el primer día. El director te aterriza los detalles en la llamada."

➤ Si el presupuesto cubre solo el sticker de A pero no B:
> "Con ese monto cubres el precio base de la Opción A (~$165,000 MXN o $9,300 USD), pero ten en cuenta que esa opción es 'puesta en China' — después se le suman aranceles del 40%, flete, seguro y aduana, y termina arriba. Lo más probable es que necesites apoyo de financiamiento para llegar a la Opción B, que sí queda lista para operar. ¿Te interesa que veamos esa opción?"

➤ Si NO cubre ni A:
> "Con ese monto directo no cubres el precio base ni de la Opción A. La buena noticia: las máquinas se entregan con factura, así que puedes buscar financiamiento con un banco, una arrendadora o una financiera y aterrizar la opción que te convenga. El director te ayuda en la llamada a definir qué vía te conviene. ¿Agendamos?"

➤ Si pregunta por financiamiento directo de TOFO:
> "Nosotros no damos financiamiento directo, pero las máquinas se entregan con factura. Con esa factura puedes buscar financiamiento con un banco, una arrendadora o una financiera. El director te puede orientar en la llamada sobre cuál de esas vías encaja mejor con tu perfil."

➤ Si pregunta cómo es la diferencia precio China vs México con números:
> "El precio base de la Opción A son $9,300 USD (~$165,000 MXN). Pero a eso se le suma el arancel del 40%, flete, seguro, aduana y el software queda en mandarín sin soporte local. La Opción B son $26,300 USD (~$460,000 MXN) con todo resuelto en México: software en español, refacciones en Guadalajara, soporte real. Por eso muchos terminan en la B aunque parezca más caro al inicio. El tipo de cambio final lo confirma el director."

---

## §4 — Aplicación

- Bumpear **solo B2B** v1.4 → v1.5 (los otros 4 prompts no manejan presupuesto B2B).
- Backup del v1.4 actual → `agente-tofo-b2b-system-prompt-v1.4.md`.
- Actualizar §1.5 (Modelos B2B), §5 (Información oficial), §7 (Cualificación capacidad financiera), §10 (Respuestas modelo) y agregar **sección nueva ⁉️ Protocolo de moneda + 💼 Financiamiento**.
- Actualizar `respuestas-mauricio-datos-fijos-2026-06-05.md` (sección §1 - respuestas + §3 - datos autorizados).
- Actualizar `datos-fijos-auditoria-2026-06-04.md` para reflejar que el financiamiento + protocolo de moneda son ahora datos canónicos.
- Copy-paste prompt v1.5 al Google Doc vivo en n8n.

## §5 — Cierre con Oscar

Para el caso puntual de Oscar (lead actual), Mauricio debe **redirigir manualmente**: aclarar la confusión, ofrecer financiamiento, agendar llamada. El prompt v1.5 evita el problema **a futuro** pero no resuelve la conversación ya rota — eso lo maneja Mauricio en vivo.

---

## §6 — Referencias

- [Respuestas Mauricio (2026-06-05)](respuestas-mauricio-datos-fijos-2026-06-05.md)
- [Auditoría datos fijos (2026-06-04)](datos-fijos-auditoria-2026-06-04.md)
- Prompt B2B v1.4 (vigente al momento del incidente, será reemplazado por v1.5)
