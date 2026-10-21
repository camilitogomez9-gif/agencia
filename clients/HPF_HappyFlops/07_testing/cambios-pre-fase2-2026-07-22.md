# Cambios a implementar antes de Fase 2 — Agente HPF "Rebeca" (Vendedor §4)

**Fecha:** 2026-07-22
**Origen:** hallazgos de `resultados-fase1-2026-07-22.md` + issue de memoria de testing.
**Convención:** cambios de prompt → los prepara Claude (con backup del §4). Cambios en n8n vivo → guía paso a paso (no se pre-edita producción).

---

## ✅ Implementado — `HPF Inbound Handler (v2 - fixes).json` (2026-07-24)

Fixes **estructurales/de flujo** aplicados al workflow de producción (verificados: JSON válido, integridad de conexiones, unit-test del sanitizer, review adversarial 4 agentes). **NO se tocó el system prompt ni el cálculo de envío** — a propósito, para que el re-run de Fase 1 dé lectura limpia del prompt real.

| # | Fix | Nodo(s) |
|---|-----|---------|
| 1 | Debounce time-aware (reemplaza buffer si gap >50s) | `Debounce - Insert` |
| 2 | Reset scopeado (`AND last_message_id=$2`) | `Debounce - Reset Buffer` |
| 3 | Output Telegram ahora sanitiza+divide (arregla `\n` literal) | `Vendedor→Sanitize+Split→Loop`, router `Es Origen Telegram?` + nuevo `Es Origen Telegram? (Post)`, `Send a text message1` |
| 4 | Sanitizer preserva saltos de línea (antes aplanaba todo a 1 línea) | `Sanitize + Split Output` |
| 5 | `/borrar` funciona (parametrizado) y limpia `messages` **+** `debounce_buffer`; acepta `/b /borrar /reset /clear` | `If`, `borrar memoria` |

**Residuales conocidos (aceptables para el re-run, documentados):**
- **Envío no calculado** (COTIZADOR es escritor de campos GHL; el LLM calcula el total sin envío, sin CALCULADORA). → F1·t4/t5 mostrarán cotización sin envío. **Es esperado.** Fix real = cablear CALCULADORA + prompt (cambio aparte).
- **Debounce**: garantía = "limpio si el próximo mensaje llega >50s después del anterior" (el tester secuencial siempre cumple). Un race de concurrencia angosto puede reprocesar (no perder) un mensaje — mejora neta vs. el original.
- **Fuera de scope (pre-existentes, no afectan Fase 1 texto):** `Respond to Webhook` deshabilitado con `responseMode: responseNode` en el path prod (riesgo timeout GHL); imagen de producto no-comprobante con stage no-pausado no llega al Vendedor (bot mudo ante foto — solo importa si Fase 1 testea imágenes); `Send a text message` del path pago aún usa `JSON.stringify` (comillas cosméticas).

### 🔎 Validado por el re-run limpio de Fase 1 (2026-07-24)

`resultados-fase1-rerun-2026-07-24.md`: **13/15 ✅, 0 ❌**. t4 cotiza a tiempo, C1 sin contaminación, output limpio, C7 completo, `/borrar` resetea. Los fixes de comportamiento **A1 (cotizar a tiempo)** y **A3 (orden del upsell)** quedan confirmados como resueltos por el flujo. Todas las reglas duras pasan.

**Remanente antes de Fase 2:**
1. ~~**[ALTO] Envío no calculado**~~ → ✅ **RESUELTO en `HPF Inbound Handler (v3 - envio).json` (2026-07-24).** Ver bloque "✅ Envío cableado (v3)" abajo.
2. ~~**[BAJO] C10 — PDF/escalamiento**~~ → ✅ hecho en v3 (regla 14: no prometer PDF/email → ATENCION_PERSONALIZADA).
3. **[BAJO] `_` suelto en t4** — confirmar si el agente emite markdown `_` suelto; vigilar en Fase 2.

---

### ✅ Envío cableado — `HPF Inbound Handler (v3 - envio).json` (2026-07-24)

Restaura la paridad con el agente original (que sí cotizaba envío). **55 nodos** (v2 + 1). Verificado: JSON válido, integridad, unit-test del tool, review adversarial 4 agentes (veredicto **go**, sin blockers; 1 mayor + 5 menores corregidos).

- **Tool nuevo `CALCULAR_ENVIO`** (`@n8n/n8n-nodes-langchain.toolCode` 1.3, cableado por `ai_tool` al Vendedor). Porta la lógica de `happyflops-calculadora-v2.json` (pesos + brackets + empaque con límite combinado 200 + mínimos). Input por `query` (JSON de `[{producto,cantidad}]`), matching robusto por keyword (tolera las grafías del catálogo), parseo de objeto suelto y formatos de fallback. Devuelve solo el costo (sin mencionar cajas/kg → respeta Regla 2). Validado: 100 sand+50 cil=$400, 300 cil=$750, 35 cil=mínimo.
- **Prompt** (systemMessage del Vendedor): [4] ahora CALCULAR_ENVIO → sumar → COTIZADOR; regla 13 revertida (Total = productos + envío); regla 9 anticipo = 50% del Total con envío; [8] con línea `Envío:` + separador de miles (solo texto); regla 14 (C10). Backup: el prompt vivo actual es el de v2 (idéntico salvo estos deltas).
- **COTIZADOR**: `monto_total_mxn` = productos + envío, `monto_anticipo_mxn` = 50%; ambos con instrucción "número PURO sin separador de miles" (evita romper la coerción a number con "3,400"). Precio de pantufla peluche corregido a $35.

**Follow-ups (no bloquean Fase 1, documentados):**
- `happyflops-calculadora-v2.json` (Code1) tiene huecos en `costoPorPeso` que facturan $0 en pesos 7.01–7.10 y 12.01–12.10 kg (el tool nuevo los cerró). Si esa calculadora sigue en uso en otro flujo, conviene portar los brackets corregidos.
- `Respond to Webhook` deshabilitado con `responseMode: responseNode` en el path prod (pre-existente, no afecta Telegram/Fase 1).

> Nota: el `_` suelto de t4 (punto 3) sigue como observación menor para Fase 2.

---

## 0. Reset de conversación de test — RESUELTO (RCA multi-agente 2026-07-24)

**El `DELETE FROM messages` NO alcanza para resetear.** El estado del lead vive repartido en varios stores cross-turn; borrar solo la memoria conversacional deja los otros intactos. El incidente "sigue diciendo XV" lo probó: con `messages` en 0 filas, el agente seguía afirmando XV.

**Causa raíz del XV persistente (confirmada empíricamente 2026-07-24):** residuo en **`debounce_buffer`** (tabla del ensamblado del INPUT, key = `contact_id`, misma DB `H.F`). El input real del agente es `Combine Messages = pending_messages.join('\n')`; el `Debounce - Insert` appendea monotónicamente y el `Reset Buffer` debía limpiar. **La query reveló los 23 mensajes de TODA la sesión acumulados (`n=23`) — el reset NO se disparó ni una vez.** Al vaciar el buffer (`SET pending_messages='[]'`) el agente respondió limpio. No es "residuo ocasional": es una **falla sistemática del reset**.

> 🚨 **Agravante — rompe producción, no solo testing:** con el reset roto, cada lead acumula toda su conversación y **en cada turno el agente recibe el historial completo como "mensaje actual"** → responde a contexto viejo, re-cotiza, se degrada. Además **confunde los resultados de Fase 1** (el input de cada caso fue el blob acumulado, no el mensaje suelto) → **re-correr Fase 1 con el debounce arreglado** (ver `resultados-fase1-2026-07-22.md`).

**Los 4 stores a limpiar para un reset REAL (checklist):**
| Store | Tabla / fuente | Key | Nota |
|-------|----------------|-----|------|
| Memoria conversacional | `messages` (DB `H.F`) | `phone` **plano** = `6390727286` | sin sufijo `_2131` (desvía del §11) |
| **Buffer de input** | `debounce_buffer` (DB `H.F`) | `contact_id` | **el olvidado — causa del incidente** |
| Contexto `[7]` | en prod = CFs del Opportunity GHL | — | muerto en el rig Telegram-only (sin store local) |
| Legacy | `n8n_chat_histories` | `+52…2131` | data vieja, otro esquema — ignorar/limpiar |

**Clear manual correcto (DB `H.F`):**
```sql
DELETE FROM messages        WHERE session_id = '6390727286';
UPDATE debounce_buffer SET pending_messages = '[]'::jsonb WHERE contact_id = '6390727286';
```

> ⚠️ Nunca borrar por sufijo/`LIKE` amplio — `messages` y `debounce_buffer` tienen conversaciones de leads reales (`+52…`). Scopeá siempre a la key exacta del chat de test.
>
> ✅ **La solución definitiva es B4 (namespace de test descartable):** usar `session_id`/`contact_id` = `test_<caso>` por caso → "resetear" = usar una key nueva, cubre memoria + buffer de una, sin queries manuales ni riesgo sobre leads reales.

**Fix estructural del debounce (aplica también a producción — un error del agente deja el buffer sucio):** ver B5.

---

## A. Fixes de agente (prompt §4) — los prepara Claude

| # | Cambio | Prioridad | Detalle |
|---|--------|-----------|---------|
| A1 | Cotizar a tiempo + prohibir tercerizar el envío | ALTO | El prompt debe forzar: con cantidad + CP + variante de TODOS los productos → invocar `COTIZADOR` **en ese turno** (F1·t4 lo difirió). Y prohibir "el envío lo cotiza un asesor" — el envío SIEMPRE sale de la tool (§8 formato exige `Envío: $[número]`). |
| A2 | C10 — anti PDF/email | MEDIO | Regla §5.4 / P5: nunca prometer PDF (ni "por asesor por correo"); ofrecer cotización inline; si insisten en formal → `ATENCION_PERSONALIZADA`. |
| A3 | Orden del upsell | BAJO | Upsell solo **después** de la cotización, no antes (pasó en F1·t4). Ya está en §6 — reforzar. |
| A4 | Formato de miles | BAJO | Cotización con separador: `$2,500` no `$2500`. |

---

## B. Fixes de pipeline / n8n — guía paso a paso (los aplica la agencia)

| # | Cambio | Prioridad | Detalle |
|---|--------|-----------|---------|
| B1 | Verificar/cablear `COTIZADOR` | ALTO | Confirmar en una ejecución si la tool **dispara** y devuelve `costo_total_envio`. Síntoma actual (F1·t5 sin envío) sugiere que no corre en el rig. Si está stub → cablear la CALCULADORA. Sin esto no hay cotización válida y A1 no alcanza. |
| B2 | Sanitización de output `\n` + split (§9) | ALTO | El output llega con `\n` literal (cotización y 7 pasos rotos). Implementar §9: quitar escapes, `**`→`*`, split por `\n\n` con `Wait 1.5s`. |
| B3 | Documentar el session key | BAJO | Confirmado: `tableName: messages`, `sessionKey: {{ phone }}` (plano, sin `2131`). Desvía del §11 (`<telefono>_2131`). Decidir si se deja plano o se alinea al spec, y documentarlo. Limpiar/ignorar la data legacy `+52…2131` en `n8n_chat_histories`. |
| B4 | Namespace de test aislado de leads reales | **ALTO** | `messages` y `debounce_buffer` tienen conversaciones reales (`+52…`). Para Fase 2 automatizada, usar `session_id`/`contact_id` = `test_<caso>` por caso (o DB/tabla aparte). "Resetear" = usar una key nueva → cubre memoria **y** buffer de una, sin queries manuales ni riesgo sobre leads reales. **Subido a ALTO:** el RCA del 2026-07-24 probó que sin esto el reset manual es error-prone (borrás `messages` pero no `debounce_buffer` → el estado persiste). |
| B5 | Robustez del debounce (reset a prueba de fallos) | **ALTO** | **Confirmado 2026-07-24: el reset NO dispara (23/23 mensajes retenidos).** Rompe producción (cada turno = historial completo como input). Diagnóstico: mandar 1 msg → tras la respuesta `SELECT jsonb_array_length(pending_messages) FROM debounce_buffer WHERE contact_id='6390727286'` → si `>0` el reset falla; abrir la ejecución y revisar el nodo `Reset Buffer` (¿ejecutó? ¿contact_id? ¿filas afectadas?). (1) Reset idempotente scopeado: `UPDATE debounce_buffer SET pending_messages='[]' WHERE contact_id=$1 AND last_message_id=$2`. (2) En `Insert`, si `now()-updated_at > interval '2 minutes'` → reemplazar en vez de appendear (descarta residuo de ráfagas truncas). (3) Cron de barrido: `DELETE FROM debounce_buffer WHERE updated_at < now() - interval '10 minutes'`. (4) Garantizar que el Reset corra ante error downstream (moverlo antes del AI Agent o `errorWorkflow`) — un fallo del Vendedor/COTIZADOR hoy deja el buffer sucio. (5) Verificar que `Insert` (`$json.contact_id`) y `Reset/Check` (contact_id de `Auth + Normalize`) usan el MISMO `contact_id`. |

---

## C. Setup de Fase 2 (infraestructura de testing)

| # | Cambio | Detalle |
|---|--------|---------|
| C1 | Webhook + respond-to-webhook | Agregar entrada `Webhook` (`responseMode: responseNode`) **en paralelo** al trigger de Telegram + `respondToWebhook` que serialice `{ reply, intermediateSteps, session_id }`. Patrón: `test-hpf-webhook.py` / rama `channel:"test"` de SYS. |
| C2 | Harness curl + reset por caso | Adaptar `scripts/testing/test-hpf-webhook.py`: casos en JSON, juez `gpt-4o-mini`, verificación de tool calls por `intermediateSteps`, y **session_id único por caso** (o reset previo) para aislamiento total. |

---

## Orden sugerido

1. **§0** memoria (encontrar la DB/tabla real) — sin esto no se puede re-testear limpio.
2. **B1 + B2** (COTIZADOR + `\n`) — los dos problemas funcionales/visuales de fondo.
3. **A1–A4** (prompt, con backup del §4).
4. **Re-test rápido** del delta: F1·t4/t5 (cotización a tiempo + con envío + bien renderizada), C10, y C1 en sesión limpia.
5. **B3 + B4** (session key + namespace de test).
6. **C1 + C2** (webhook + harness) → arrancar **Fase 2**.

**Criterio para pasar a Fase 2:** F1 cotiza en el turno correcto, con envío calculado y bien renderizada; C10 no promete PDF; y la memoria de test se puede resetear de forma confiable y aislada de la data real.
