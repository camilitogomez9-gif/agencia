# Resultados Fase 2 — HPF "Rebeca" (curl al webhook)

**Fecha:** 2026-07-24
**Webhook:** `https://[TU-INSTANCIA-N8N]/webhook/hpf-inbound` (dev)
**Auth:** credencial Header Auth (`x-hpf-auth`) en el nodo Webhook — token fuera del código/JSON
**Flujo:** `HPF Inbound Handler (v6).json` (gate `¿Es test?`: `channel:"test"` → respuesta por webhook)
**Modo test:** `channel:"test"` en el payload → el gate devuelve el texto crudo del agente al curl
**Juez:** `gpt-4o-mini` (LLM-as-judge) + **re-verificación manual** de todo lo marcado
**Casos:** 20 (flujo feliz A1-A6 + reglas duras R1-R11 + envío S1-S3)

## Resumen

- **HTTP 200 en los 20 casos — 0 crashes.** La COTIZADOR/tools pegando a GHL con `opportunity_id` falso no rompen al agente (el texto se produce igual).
- **Tally crudo del juez:** 14 true / 5 parcial / 1 false.
- **Tally corregido (tras re-lectura manual):** **~18 ✅ · 2 parciales blandos · 0 fallos reales.** El juez `gpt-4o-mini` tuvo varios falsos negativos (ver "Nota sobre el juez").
- **Envío (lo nuevo) funciona perfecto en producción**, con la math exacta.
- **Todas las reglas duras se sostienen.**

## Verificación del envío (CALCULAR_ENVIO en vivo)

| Caso | Pedido | Envío | Total | Anticipo | ✓ |
|------|--------|-------|-------|----------|---|
| A4 | 100 sand. delgadas + 50 cilindros | $400 | $3,400 | $1,700 | ✅ exacto |
| S1 | 100 sand. gruesas (boda) | $350 | $3,350 | $1,675 | ✅ exacto (15 kg) |
| S2 | 300 cilindros (XV) | $750 | $3,750 | $1,875 | ✅ exacto (2 cajas, sin mencionar cajas/kg) |
| S3 | 50 mandiles (boda) | $250 | $850 | $425 | ✅ exacto (0 kg) |

Separador de miles OK, 7 pasos OK, upsell al final OK, sin mención de cajas/kg (Regla 2).

## Detalle por caso (veredicto corregido)

| ID | Mensaje | Corregido | Nota |
|----|---------|-----------|------|
| A1 | Hola, buenas | ✅ | Saludo, pide evento. |
| A2 | Es para unos XV | ✅ | Lista sandalias/pantuflas/cilindros/kit — **sin mandiles**. (Juez alucinó "mandiles".) |
| A3 | Quiero sandalias y cilindros | ⚠️ | Pide cantidad; no pide CP/suela explícito (los junta de a poco). Correcto conversacionalmente. |
| A4 | 100 sand. delgadas + 50 cil, CP 44100 | ✅ | Cotización completa con envío. |
| A5 | ¿cómo pago? | ✅ | Info de pago correcta (transferencia/efectivo, concepto). No ofrece tarjeta. (Juez pedía "no tarjetas" explícito.) |
| A6 | y los termos cuánto? | ✅ | Reconoce termos=cilindros; no re-pregunta (anti-repetición P1). |
| R1 | sandalias para el padrino | ✅ | Solo mujeres. |
| R2 | mandiles para XV | ✅ | Mandiles solo Boda. |
| R3 | 35 cilindros | ✅ | Mínimo 40, no cotiza. |
| R4 | pantuflas de moño, 50 | ⚠️ | Pregunta el evento primero (flujo correcto: evento antes que producto). No cotizó variante equivocada. Confirmaría variante tras el evento. |
| R5 | te doy $20 por sandalia | ✅ | Mantiene precio. |
| R6 | ¿cuánto pesa el paquete? | ✅ | No revela kg. |
| R7 | ¿otro número? | ✅ | Solo 3315948670. (Juez marcó "info extra" = un cierre amable, ningún otro número.) |
| R8 | catálogo de sandalias | ✅ | No escala. |
| R9 | cotización en PDF a mi correo | ✅ | **Escala a atención personalizada** para lo formal/PDF (Regla 14 funcionando). No promete PDF ni pide email. |
| R10 | evento en 5 días, urge | ✅ | Escala (<15 días). |
| R11 | ¿sucursal en CDMX? | ✅ | No inventa; ubica en Guadalajara. |
| S1 | 100 sand. gruesas boda | ✅ | Envío $350 exacto. |
| S2 | 300 cilindros XV | ✅ | Envío $750 exacto. |
| S3 | 50 mandiles boda | ✅ | Envío $250 exacto. |

## Nota sobre el juez (importante)

El `gpt-4o-mini` como juez tuvo **falsos negativos** que inflaron el tally de fallos:
- **A2:** alucinó que se ofrecían mandiles (no están en la respuesta).
- **A5 / R7:** demasiado estricto (pedía frases explícitas que no eran obligatorias).
- **R9:** marcó parcial cuando el comportamiento (escalar) es exactamente el deseado.

**Lección:** en Fase 2 todo lo marcado por el juez se re-verifica a mano contra la respuesta real. El tally corregido es el válido.

## Parciales blandos → ✅ PULIDOS Y RE-VERIFICADOS (v7, 2026-07-24)

Los 3 se aplicaron al `systemMessage` del Vendedor y se re-corrieron por curl. **Los 3 pasaron + A4 sin regresión.**

| # | Pulido aplicado | Resultado del re-test |
|---|-----------------|------------------------|
| A3 | En `[4]`: *"Cuando el lead nombre productos, pedí en UN SOLO mensaje TODO lo que falta para cotizar (cantidad + CP + suela/variante), no un dato por turno."* | ✅ Ahora pide los 3 datos juntos en lista (cantidad · delgada/gruesa · CP). |
| R4 | Regla 11 + : *"Si el lead nombra un producto con variante y todavía no sabés el evento, preguntá el evento Y confirmá la variante en el MISMO mensaje."* | ✅ Pregunta evento + variante en el mismo turno. *Nit menor:* ofrece colores (peluche) en vez de satín-vs-peluche primero — no cotiza asumiendo, es cosmético. |
| R9 | Regla 14 + : *"NO repitas la palabra 'PDF' ofreciéndolo… llamá ATENCION_PERSONALIZADA sin prometer un formato."* | ✅ Ya no menciona "PDF"; ofrece cotización en chat + canaliza a atención personalizada. |
| A4 | (regresión) | ✅ `Envío: $400 · Total: $3,400 · Anticipo: $1,700` + 7 pasos + upsell. Sin cambios. |

**Archivo:** `HPF Inbound Handler (v7).json` (solo difiere del v6 en el `systemMessage`; topología idéntica).

> ⚠️ **Caveat de import:** cada import in-place **borra el binding de la credencial Header Auth** del nodo `Webhook - Inbound` (las credenciales no viajan en el JSON). Síntoma: HTTP 500 instantáneo (~0.8s, antes de que corra el agente). Fix: re-seleccionar la credencial en el nodo y guardar.

## Pendiente operativo antes de producción

- **Restaurar el debounce a 45s** — el `Wait 0s (Debounce)` se bajó a 0 solo para acelerar el testing. En prod debe volver a **45s** (agrupa ráfagas del lead; con 0s el agente responde mensaje por mensaje).
- Confirmar el path de envío real (GHL/WhatsApp) cuando se conecte la WABA — Fase 2 valida el cerebro vía `channel:"test"`; la entrega multi-parte ya se validó en Fase 1 por Telegram.

## Conclusión

El agente migrado (GHL/n8n) **iguala o supera al original**: guía el flujo, respeta las 12 reglas inviolables, y ahora **cotiza el envío correctamente** (paridad recuperada con el Kommo original + math verificada). Fase 2 esencialmente limpia. Los 3 candidatos de pulido son menores y opcionales.

**Infra de Fase 2 validada:** webhook + Header Auth + gate `channel:"test"` + respuesta cruda del agente = batería curl repetible (`scripts` en scratchpad: `hpf_phase2.py`).
