# Resultados Fase 1 — RE-RUN limpio (post fixes de flujo) — Agente HPF "Rebeca"

**Fecha:** 2026-07-24
**Canal:** Telegram (rig cerebro n8n · Vendedor §4)
**Workflow:** `HPF Inbound Handler (v2 - fixes).json` (debounce + sanitizer + /borrar corregidos)
**Insumo:** `testing-guide-fase1-v1.md` (respuestas del re-run)
**Supersede:** `resultados-fase1-2026-07-22.md` (aquel estaba confundido por el bug del debounce)

## Resumen

| Veredicto | Casos | Total |
|-----------|-------|-------|
| ✅ pasa | F1·t1, F1·t2, F1·t3, F1·t5, C1, C2, C3, C4, C5, C6, C7, C8, C9 | 13 |
| ⚠️ parcial | F1·t4 (gap de envío — conocido), C10 (menciona PDF, no escala) | 2 |
| ❌ falla | — | 0 |

**Lectura ahora es válida** (input = mensaje suelto, output sanitizado). Los fixes de flujo quedan **validados por evidencia**.

## Los fixes de flujo funcionaron (comparación vs. run confundido)

| Síntoma anterior | Ahora |
|------------------|-------|
| F1·t4 NO cotizaba (difería + upsell) | **Cotiza en el turno**, con header, ítems, total, anticipo, 7 pasos y upsell al final ✅ |
| C1 arrastraba "XV" del Flujo 1 | **C1 limpio**, pregunta el evento en frío ✅ (reset `/borrar` + buffer OK) |
| `\n` literales en la cotización | **Formato correcto**, saltos de línea reales ✅ |
| C7 salía vacío (sanitizer) | **C7 completo** — niega el peso sin borrar el mensaje ✅ |

## Detalle

| Caso | Veredicto | Nota |
|------|-----------|------|
| F1·t1 | ✅ | Tono cálido, se presenta, pide evento con opciones. |
| F1·t2 | ✅ | Reconoce XV con frase de conexión, invita a productos, **sin mandiles**. |
| F1·t3 | ✅ | Reconoce ambos, pide cantidad + suela + CP. (menciona mínimos proactivamente — informativo, ok.) |
| F1·t4 | ⚠️ | **Cotiza bien y a tiempo** (header ✅, ítems ✅, anticipo 50% ✅, 7 pasos ✅, upsell al final ✅). Único faltante: **envío no calculado** → "se cotiza aparte, un asesor confirma" (gap conocido de COTIZADOR). Menor: un `_` colgado al final del mensaje (posible markdown suelto del agente). |
| F1·t5 | ✅ | Info de pago completa (anticipo, transferencia/efectivo, concepto, comprobante) + dirección/mapa. Sin tarjetas. |
| C1 | ✅ | Arranque en frío limpio, pide evento. Sin contaminación. |
| C2 | ✅ | "Sandalias solo para mujeres, no manejamos versión masculina ni para padrinos." |
| C3 | ✅ | "Mandiles solo para Boda." Ofrece alternativas de XV. |
| C4 | ✅ | "Mínimo 40 cilindros, con 35 no llegamos" → NO cotiza, pide ajustar. (caso del incidente real ✅) |
| C5 | ✅ | Pide variante (satín/peluche + colores) antes de cotizar. |
| C6 | ✅ | Mantiene precio, no regatea. |
| C7 | ✅ | "No puedo compartir el peso del paquete." Sin kg. (fix sanitizer validado) |
| C8 | ✅ | Solo el número oficial 3315948670. |
| C9 | ✅ | No escala; pide el evento para mostrar el catálogo correcto. |
| C10 | ⚠️ | No pide email y ofrece cotización inline (bien), pero **menciona que el equipo genera un PDF post-anticipo** y **no escala** a atención personalizada. Mejoró vs. run anterior (ya no promete mandarlo por correo). Candidato a tweak de prompt. |

## Pendientes que salen de la Fase 1 limpia

1. **[ALTO] Envío no calculado (COTIZADOR)** — es el único faltante de una cotización completa. El total ($3000) y el anticipo ($1500) son solo de productos; el envío se difiere a humano. Requiere cablear un cálculo de envío (la lógica existe en `03_workflows/happyflops-calculadora-v2.json`) + ajuste de prompt. **Es ahora el ítem #1 antes de dar la cotización por buena.**
2. **[BAJO] C10 — PDF/escalamiento** — endurecer levemente el prompt: no mencionar generación de PDF; ofrecer cotización inline y, si insisten en "formal", derivar. Aplicar ahora que la lectura es limpia.
3. **[BAJO] `_` colgado en t4** — confirmar si el agente emite markdown `_` suelto (el `_..._` de los casos C es formato del pegado, no del bot). Vigilar en Fase 2; si aparece, sumar `_` al normalizado del sanitizer o nota en prompt.

## Estado

Con la Fase 1 limpia, los básicos (tono, saludo, flujo, reglas duras) están **sólidos**. El camino a Fase 2 depende de la decisión sobre el envío (ítem 1).
