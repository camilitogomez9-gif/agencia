# Resultados Fase 1 — Agente HPF "Rebeca" (Vendedor §4)

**Fecha:** 2026-07-22
**Canal:** Telegram (rig cerebro n8n · Vendedor §4)
**Insumo:** `testing-guide-fase1-v1.md` (respuestas pegadas por la agencia)
**Criterios:** `criterios-fase1-v1.md`

> 🚨 **ADVERTENCIA (agregada 2026-07-24) — estos resultados están CONFUNDIDOS por un bug del debounce.** Se descubrió que el `debounce_buffer` nunca reseteaba: el agente recibía en CADA turno **todos los mensajes acumulados de la sesión** como input, no el mensaje suelto (RCA en `cambios-pre-fase2-2026-07-22.md` §0 / B5). Por lo tanto: lo atribuido a "memoria/anti-loop P1 funcionando" pudo ser el buffer; F1·t4/t5 y las contaminaciones de los C se explican por el input-blob; y las reglas duras (C2/C4/C7/C8…) aguantaron pese al input sucio pero deben re-confirmarse. **Válido igual:** tono, H1 (`\n`). **Acción: re-correr Fase 1 con el debounce arreglado (B5) antes de sacar conclusiones o aplicar fixes de prompt derivados de estos casos.**

## Resumen

| Veredicto | Casos | Total |
|-----------|-------|-------|
| ✅ pasa | F1·t1, F1·t2, F1·t3, C2, C3, C4, C5, C6, C7, C8, C9 | 11 |
| ⚠️ parcial | F1·t5, C1 | 2 |
| ❌ falla | F1·t4, C10 | 2 |

**Lectura:** el tono y **todas las reglas conversacionales duras pasaron** (género, mandiles-solo-boda, mínimo cilindros 40, variante pantufla, integridad de precio, no-peso, teléfono único, catálogo-sin-escalar). Los fallos NO son de reglas de negocio — son de **(a) timing/completitud de la cotización, (b) render del output, (c) la promesa de PDF**. La migración preservó el "core" del agente original; falta ajustar cotización + pipeline.

---

## Hallazgos transversales (lo importante)

### H1 · [ALTO] Saltos de línea literales `\n` en el output
Toda respuesta multi-línea llega con `\n` **literal** en vez de salto de línea real: F1·t5 (la cotización entera), C1, C2, C3, C4, C5. Las respuestas de un solo párrafo (t1–t4, C6–C10) no lo muestran → confirma que aparece **solo cuando hay estructura de varias líneas**.
- **Causa probable:** output del Vendedor sin sanitizar/escapado en el pipeline n8n→Telegram (es exactamente el pendiente §9 "Post-procesado del output" de `guia-correccion-integral`, que todavía no está implementado). El texto llega escapado (`\n` como caracteres) en lugar de renderizado.
- **Impacto:** en producción, **la cotización y los 7 pasos se ven rotos** para el cliente. P0 visual.
- **A confirmar con la agencia:** ¿en Telegram lo ves con `\n` literal, o se ve con saltos reales y el `\n` es artefacto del copiar/pegar? Si es lo primero → es bug real de pipeline.
- **Fix:** implementar la sanitización + split del §9 (quitar escapes, `**`→`*`, dividir por `\n\n` con Wait 1.5s).

### H2 · [ALTO] La cotización no calcula el envío y llega tarde
Dos síntomas de la misma raíz:
- **F1·t4:** el lead dio TODO (100 sandalias delgadas + 50 cilindros + CP) y el bot **no cotizó** — dijo "dame un momento para armarte la cotización" + hizo upsell. La cotización debía salir en ese turno.
- **F1·t5:** recién ahí aparece la cotización, pero **sin envío calculado**: `Envío: se cotiza aparte según código postal, un asesor te lo confirma`. Por eso el `Total: $3000` **excluye el envío** y el `Anticipo: $1500` está mal (con envío ~$400, Total sería ~$3400 y anticipo ~$1700).
- **Causa probable:** la tool `COTIZADOR` **no está funcionando / no dispara** en el rig de Telegram (o dispara y no devuelve envío) → el agente improvisa una cotización con los precios que sabe del prompt, pero no puede calcular el envío y lo terceriza a un humano. El envío determinístico es justamente lo que aporta `COTIZADOR` (CALCULADORA).
- **Impacto:** el corazón de la venta. Sin envío correcto no hay cotización válida.
- **A confirmar con la agencia:** en la ejecución de n8n de t4/t5, ¿se invocó `COTIZADOR`? ¿devolvió `costo_total_envio`? Esto decide si es bug de tool-wiring (probable) o de prompt.

### H3 · [MEDIO] Los casos C se corrieron con memoria contaminada
C1–C5 arrastran el contexto del Flujo 1 (todos mencionan "100 sandalias / 50 cilindros / XV"). No se corrieron en sesión limpia.
- **Lado bueno:** demuestra que la **memoria persistente funciona** y que el **anti-loop (P1) se cumple** — el agente no re-pregunta datos ya dados. Eso es exactamente lo que la arquitectura nueva debía resolver. ✅
- **Lado malo:** invalida C1 como test de "arranque en frío" y ensucia el resto (aunque las reglas duras aguantaron igual).
- **Acción:** re-correr al menos C1 (idealmente C1–C10) en sesión limpia usando la query `2b` (`DELETE ... WHERE session_id LIKE '%\_2131'`) entre casos.

---

## Detalle por caso

| Caso | Veredicto | Qué pasó |
|------|-----------|----------|
| F1·t1 | ✅ | Tono cálido, se presenta, pide evento con opciones. Bien. |
| F1·t2 | ✅ | Reconoce XV con frase de conexión, invita a productos, **no ofrece mandiles** (correcto para XV). |
| F1·t3 | ✅ | Pide cantidad + suela (9mm/15mm) + CP. (typo cosmético del modelo: falta cerrar paréntesis en "15mm".) |
| F1·t4 | ❌ | **No cotizó teniendo todos los datos.** Difirió ("dame un momento") + upsell prematuro. Ver H2. |
| F1·t5 | ⚠️ | Cotización con header ✅ + líneas ✅ + 7 pasos ✅, pero **sin envío**, Total y Anticipo mal (excluyen envío), + bug `\n` (H1). Info de pago OK. |
| C1 | ⚠️ | Contaminado (H3): no testea arranque en frío. Volcó precios con mínimos proactivamente (menor). |
| C2 | ✅ | "Sandalias solo para mujeres, no manejamos versión masculina ni para padrino." Recupera con cilindros unisex. |
| C3 | ✅ | "Mandiles solo para Boda, no para XV." Ofrece alternativas de XV. |
| C4 | ✅ | **Caso crítico del incidente:** "cilindros mínimo 40 piezas, pides 35, necesitamos al menos 40" → **NO cotiza**, pide ajustar. |
| C5 | ✅ | Pide variante antes de cotizar: "¿satín o peluche? Si peluche: blanco/negro/morado/rosa." |
| C6 | ✅ | "Los precios son fijos, no podemos modificarlos." No baja de $25. |
| C7 | ✅ | "No puedo compartir el peso del paquete." No da kg ni menciona cajas. |
| C8 | ✅ | "Solo manejamos el número oficial: 3315948670." |
| C9 | ✅ | **No escala:** "¿Todavía tienes la info o quieres que te la reenvíe?" (comportamiento P7/P8 exacto). |
| C10 | ❌ | **Promete PDF por correo** ("después de tu anticipo... un asesor te lo puede enviar por correo"). La regla P5 es no prometer PDF ni derivar a mail → debía escalar. No pidió email (bien), pero rompe el "no prometer PDF". |

---

## Acciones priorizadas

**Pipeline / tools (bloqueantes, requieren revisar n8n):**
1. **[ALTO] H2 — COTIZADOR:** verificar en n8n si la tool dispara y devuelve envío. Objetivo: que el agente cotice **apenas tiene datos completos** (t4) y que la cotización incluya `Envío: $[número]`, `Total` con envío y `Anticipo` = 50% del total con envío.
2. **[ALTO] H1 — `\n`:** confirmar el síntoma en Telegram e implementar la sanitización/split del §9.

**Prompt (fixes puntuales, con backup previo):**
3. **[MEDIO] C10:** endurecer la regla anti-PDF/email (§5.4 / P5) — nunca prometer PDF, ni "por asesor por correo"; ofrecer la cotización inline y, si insisten en formal, `ATENCION_PERSONALIZADA`.
4. **[BAJO] Orden del upsell:** que el upsell salga **después** de la cotización, no antes (pasó en t4).
5. **[BAJO] Formato:** separador de miles en la cotización (`$2,500` en vez de `$2500`).

**Testing hygiene:**
6. **[MEDIO] H3:** re-correr C1 (y preferentemente C1–C10) en sesión limpia (SQL `2b` entre casos).

---

## Próximos pasos
- Confirmaciones de la agencia (H1 render en Telegram + H2 si COTIZADOR dispara) → definen si 1/2 son fix de pipeline o de prompt.
- Con eso: aplicar fixes de prompt (3–5, con backup del §4), coordinar los de pipeline (1–2), re-test rápido de F1·t4/t5 + C10 + C1 limpio.
- Cuando los básicos queden limpios → armar **Fase 2** (webhook + respond-to-webhook, harness curl, matriz completa + paridad vs. las 10 transcripciones golden).
