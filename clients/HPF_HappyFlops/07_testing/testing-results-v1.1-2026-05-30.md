# Resultados de testing — Pantufla Mono v1.1

**Fecha:** 2026-05-30
**Prompt probado:** v1.1 (con 3 EDITs aplicados: precios desglosados + ⚠️ línea Pantuflas + REGLA CRÍTICA Material y modelo)
**Casos definidos en:** [guia-fix-pantuflas-mono-2026-05-30.md](../06_docs/guia-fix-pantuflas-mono-2026-05-30.md) §7

## Resultados

| Caso | Esperado | Obtenido | Veredicto |
|---|---|---|---|
| **A** — solo "pantuflas" → pedir modelo | Pregunta normales vs mono | "Las prefiere pantuflas normales o pantuflas mono (con moñito)?" | ✅ PASA |
| **B** — "pantufla de moño" sin material → pedir material | Pregunta peluche vs satín | "Las prefiere con moño de peluche o con moño de satín?" | ✅ PASA |
| **C** — "pantufla mono satín" cotización directa | Cotiza 50 Pantuflas Mono Satín × $30 | Error `Received tool input did not match expected schema` en nodo `AI Agent Recolector` | ❌ ERROR DE TOOL (no del prompt) |
| **D** — multi-producto "pantufla satín + pantufla moño satín" | Dos líneas distintas con productos correctos del catálogo | Cotizó "Pantuflas **Normales** Satín × $30" + "Pantuflas Mono Satín × $30" → inventó un producto que no existe | ⚠️ PARCIAL |
| **E** — "pantufla normales" cotización directa | Cotiza Pantuflas × $30 | "50 Pantuflas Normales x $30 = $1,500" | ✅ PASA |

## Diagnóstico

- **A, B, E**: el refuerzo v1.1 funciona — el agente sí pregunta cuando corresponde y cotiza directo cuando ya tiene la info.
- **D**: el agente interpretó "pantufla satín" del primer ítem como un producto distinto inexistente ("Pantuflas Normales Satín"). El árbol modelo→material no preveía que el material implica el modelo. Fix: agregar tabla de mapeo en la REGLA CRÍTICA — "satín/peluche sin mono ni normal" → Pantufla Mono [material] automáticamente. Aplicado en v1.2 (ver `06_docs/delta-fix-pantuflas-v1.2-2026-05-30.md`).
- **C**: el error es de schema entre el AI Agent y la tool CALCULADORA. **Causa raíz identificada (2026-05-30 — vía inspección del JSON de la calculadora):** el sub-workflow `OPiuPFwRmq6QgACL` (`HPF - Calculadora`) fue actualizado para preferir un nuevo input `items` con `{producto, cantidad}` y nombres canónicos; el trigger expone schema con AMBOS campos (`cuentas` Y `items`) requeridos. El prompt nunca documentó `items` → el LLM solo manda `cuentas` → falla schema en langchain antes de ejecutar el JS. Fix en v1.3 (ver `06_docs/delta-fix-calculadora-v1.3-2026-05-30.md`).

## Acciones

1. ~~Aplicar v1.2 (delta-fix-pantuflas-v1.2-2026-05-30.md) — fix de D.~~ ✅ ya está en producción (verificado contra `happyflops-main-v3.json`).
2. ~~Aplicar v1.3 (delta-fix-calculadora-v1.3-2026-05-30.md) — fix del schema de CALCULADORA.~~ ✅ aplicado.
3. ~~Re-correr C + D + A con v1.3.~~ ✅ ejecutado: A pasa, C pasa, **D sigue fallando** con "Pantuflas Normales Satín" inventado.

## Resultados re-test v1.3

| Caso | Esperado v1.3 | Obtenido | Veredicto |
|---|---|---|---|
| A | Pregunta modelo | "Las prefiere pantuflas normales o pantuflas mono (con moñito)?" | ✅ PASA |
| C | Cotiza Pantufla Mono Satín × $30 sin error de schema | "50 Pantuflas Mono Satín x $30 = $1,500 + Envío $300 + Total $1,800 + Anticipo $900" | ✅ PASA — el fix de CALCULADORA funciona |
| D | Una línea Pantufla Mono Satín 100 unidades, o pregunta de aclaración | "50 Pantuflas **Normales** Satín × $30 + 50 Pantuflas Mono Satín × $30" | ❌ FALLA — sigue inventando producto inexistente |

**Diagnóstico de D en v1.3**: la tabla de mapeo de v1.2 mapea correctamente "pantufla satin" → Pantufla Mono Satín, PERO cuando hay dos descripciones similares en el mismo mensaje, el LLM aplica inferencia de contraste lingüístico ("están escritas distinto → son productos distintos") que gana contra el mapeo. El "caso especial multi-producto" de v1.2 incluso refuerza esa inferencia al decir "tratá cada variante como producto distinto". Fix posterior pendiente de definir.
