# ESTADO — protocolo de paridad HPF

**Se actualiza después de CADA caso.** Lo que no está en este archivo no existe: tiene que sobrevivir
a que se corte la sesión.

**Build bajo test:** `hpf-inbound-handler-testbuild-nodebounce-2026-08-05.json`
`sha256 f92ceb1c422e6f7614a5ef75a7dfa3410cbbc03f60e9b16c5cc1b7ef945159d1` · `versionId 4fc5b0c7-0ef0-4a7b-b5fd-1dc5e8033b45`

---

## Fase actual

| Fase | Estado | Gate |
|---|---|---|
| F0 · Pre-flight | ✅ **cerrada** | G0 ✅ |
| F1 · Congelar oráculo y matriz | ✅ **cerrada** | G1 ✅ |
| F2 · Observar sin arreglar | ✅ **cerrada** — 32 PASA · 2 PARCIAL · 1 FALLA · 0 SIN-EVIDENCIA | G2 ✅ |
| F3 · Arreglar por familias | ✅ **cerrada** — 35/35 PASA · S1 20/20 · núcleo 8/8 en 2 corridas · gate de mutación 4/5 · deuda en cero | G3 ✅ |
| F4 · Campaña exhaustiva | ⏸ no iniciada | G4 |

## Gate G1 — checklist

- [x] `MATRIZ.md` existe, con el cálculo de N escrito (`3 × 4 × 11 = 132`)
- [x] Una justificación por celda excluida (agrupada por causa, 115 celdas)
- [x] 100 % de los casos con `intención` y puntero al doc que la firma
- [x] 100 % de los casos con `oráculo` y fuente citada `ruta:línea`
- [x] 0 casos con `oráculo: INFERIDO` en el set contable
- [x] Matriz B: `aristas_cubiertas / aristas_totales` = **26 / 34** reportado
- [x] Las 7 filas `NO-REPLICAR` precargadas, + una octava encontrada en el oráculo
- [x] `decisiones-abiertas.md` escrito
- [x] `git diff` sobre `03_workflows/` y `04_agents/` sin cambios de lógica
- [x] `decisiones-abiertas.md` v2 reescrito en lenguaje llano (la v1 no se entendió)
- [ ] **`decisiones-abiertas.md` v2 enviado a Juanpi**
- [ ] **Matriz aprobada por la agencia antes de ejecutar** ← único control que no depende de mi autoevaluación

---

## Casos

Estados cerrados: `PASA` · `FALLA` · `PARCIAL` · `SIN-EVIDENCIA` · `BLOQUEADO-POR-CANAL`. **No existe `PENDIENTE` al cerrar.**

| id | sev | canal | estado | evidencia | nota |
|---|---|---|---|---|---|
| HPF-SAL-001 | S2 | telegram | **PASA** | `evidencia/HPF-SAL-001/` |  |
| HPF-SAL-002 | S1 | telegram | **PASA** | `evidencia/HPF-SAL-002/` |  |
| HPF-EVT-003 | S1 | telegram | **PASA** | `evidencia/HPF-EVT-003/` |  |
| HPF-EVT-004 | S1 | telegram | **PASA** | `evidencia/HPF-EVT-004/` |  |
| HPF-EVT-005 | S2 | telegram | **PASA** | `evidencia/HPF-EVT-005/` |  |
| HPF-EVT-006 | S3 | telegram | **PASA** | `evidencia/HPF-EVT-006/` |  |
| HPF-FIC-007 | S1 | telegram | **PASA** | `evidencia/HPF-FIC-007/` |  |
| HPF-FIC-008 | S1 | telegram | **PASA** | `evidencia/HPF-FIC-008/` |  |
| HPF-FIC-009 | S1 | telegram | **PASA** | `evidencia/HPF-FIC-009/` |  |
| HPF-FIC-010 | S1 | telegram | **PASA** | `evidencia/HPF-FIC-010/` |  |
| HPF-FIC-011 | S2 | telegram | **PASA** | `evidencia/HPF-FIC-011/` |  |
| HPF-FIC-012 | S3 | telegram | **PASA** | `evidencia/HPF-FIC-012/` |  |
| HPF-COT-013 | S1 | telegram | **PASA** | `evidencia/HPF-COT-013/` |  |
| HPF-COT-014 | S1 | telegram | **PASA** | `evidencia/HPF-COT-014/` | incidente cilindros 35/40 |
| HPF-COT-015 | S2 | telegram | **PASA** | `evidencia/HPF-COT-015/` |  |
| HPF-COT-016 | S1 | telegram | **PASA** | `evidencia/HPF-COT-016/` |  |
| HPF-COT-017 | S2 | telegram | **PASA** | `evidencia/HPF-COT-017/` |  |
| HPF-NRP-020 | S1 | telegram | **PASA** | `evidencia/HPF-NRP-020/` |  |
| HPF-NRP-021 | S2 | telegram | **PASA** | `evidencia/HPF-NRP-021/` |  |
| HPF-NRP-022 | S1 | telegram | **PASA** | `evidencia/HPF-NRP-022/` |  |
| HPF-NRP-023 | S2 | telegram | **PASA** | `evidencia/HPF-NRP-023/` |  |
| HPF-NRP-025 | S1 | telegram | **PASA** | `evidencia/HPF-NRP-025/` | fila #8, no estaba en el protocolo |
| HPF-COT-026 | S1 | telegram | **PASA** | `evidencia/HPF-COT-026/` |  |
| HPF-FIC-027 | S1 | telegram | **PASA** | `evidencia/HPF-FIC-027/` |  |
| HPF-NRP-028 | S1 | telegram | **PASA** | `evidencia/HPF-NRP-028/` |  |
| HPF-EVT-029 | S1 | telegram | **PASA** | `evidencia/HPF-EVT-029/` |  |
| HPF-FIC-030 | S1 | telegram | **PASA** | `evidencia/HPF-FIC-030/` |  |
| HPF-FIC-031 | S2 | telegram | **PASA** | `evidencia/HPF-FIC-031/` |  |
| HPF-FIC-032 | S2 | telegram | **PASA** | `evidencia/HPF-FIC-032/` | familia F-1 · variantes de más |
| HPF-FIC-033 | S2 | telegram | **PASA** | `evidencia/HPF-FIC-033/` |  |
| HPF-FIC-034 | S2 | telegram | **PASA** | `evidencia/HPF-FIC-034/` |  |
| HPF-FIC-035 | S1 | telegram | **PASA** | `evidencia/HPF-FIC-035/` | familia F-2 · corrección de Oscar del 3/8 |
| HPF-TOP-018b | S2 | telegram | **PASA** | `evidencia/HPF-TOP-018b/` | familia F-3 · sumidero, el lead no recibe nada |
| HPF-CAN-023 | S2 | telegram | **PASA** | `evidencia/HPF-CAN-023/` |  |
| HPF-CAN-025 | S1 | ghl | **PASA** | `evidencia/HPF-CAN-025/` | rama GHL verificada |

### Fuera del denominador, listados aparte

| id | motivo |
|---|---|
| HPF-TOP-018b | sumidero `Switch[fallback]` — se mide y se reporta |
| HPF-TOP-019 | requiere los `Wait` reactivados |
| HPF-TOP-020 | topológico |
| HPF-TOP-021 | topológico |
| HPF-CAN-022 · 023 · 024 | canal/media |
| HPF-CAN-025 | rama GHL |

---

## Deuda de test — a revertir al cerrar, verificado por re-export

- [x] Reactivar `Wait 1.5s Between Parts`
- [x] Debounce **en 50 s** y nodo renombrado a `Wait 50s (Debounce)` — ya no miente sobre su valor
- [x] Ningún nodo deshabilitado
- [x] Verificado por re-export: `python3 scripts/testing/hpf-verificar-deuda.py` → **deuda en cero**
- [x] **Gate de mutación G2-bis corrido**: 4/5 detectadas + 1 redundancia documentada. Las 5 reversiones verificadas por re-export

---

## Tripwire

> Corridos los primeros **20** casos, si el pase está bajo el **60 %**: parar y darle a la agencia el número
> crudo **antes** de escribir un solo fix. Renegociar el alcance no es decisión mía.

Estado: **no disparado.** A los 20 casos el pase iba 18/20 (90 %), muy por encima del 60 %.

---

## Bitácora

| Fecha | Qué |
|---|---|
| 2026-08-05 | F0: baseline congelado `6fd48492…` (`versionId 52bb53fc`), 71 nodos |
| 2026-08-05 | F0: probe de pre-flight — POST devuelve 200 con body vacío a los 43,7 s; skew de reloj +0,9 s; correlación por `_probe_id` validada |
| 2026-08-05 16:07 | la agencia deshabilitó los 2 `Wait`. Build de test congelado aparte: `f92ceb1c…` (`versionId 4fc5b0c7`) |
| 2026-08-05 | F0: entrega real verificada — saludo 3/3 (`msg_id` 1537-1539) y multiparte 9/9 (`msg_id` 1540-1548, 3 fotos + 1 PDF + 2 videos + 3 textos), orden preservado, sin 429 |
| 2026-08-05 | F1: matriz derivada y congelada. 17/132 celdas con oráculo observado, 26/34 aristas cubiertas |
| 2026-08-05 | **F3**: 4 fixes escritos en el vivo (F-1 variantes · F-2 colores · F-3 sumidero · H-1 SMS→WhatsApp). Diff verificado nodo por nodo, JS validado con `node --check`, 32 credenciales preservadas |
| 2026-08-05 | F3: el corpus era **order-dependent** — el memo de staticData es por chat y acumula. Warm-up `hola` (marcador 👼🏢, jsCode:280) agregado a los 11 casos que afirman sobre fichas |
| 2026-08-05 | F3: `HPF-FIC-033` era un **falso verde** del baseline: pasaba exhibiendo el defecto F-1 porque no chequeaba ausencias. Assert reforzado |
| 2026-08-05 | **Gate de mutación G2-bis**: 5 defectos inyectados en el vivo, 5 reversiones verificadas por re-export. M1 y M3 detectadas de entrada; M2 y M5 revelaron huecos reales (nadie afirmaba el precio cotizado ni el header de promo) → asserts agregados y re-corridas: detectadas. M4 no se detecta porque el prompt bloquea antes que el gate del Sanitize: es redundancia, no hueco |
| 2026-08-05 | Los 5 casos que tocó el gate quedaron con artefactos de un build mutado. Re-corridos sobre el build limpio: 6/6 PASA |
| 2026-08-05 | **G3**: núcleo de regresión 8/8 verde en 2 corridas consecutivas sobre el flujo final (debounce 50 s) |
| 2026-08-05 | Entrega escrita: `entrega-juanpi-2026-08-05.md` — 7 transcripts renderizados desde los artefactos, no pegados a mano |
| 2026-08-05 | **F3 cerrada: 35/35 PASA · S1 20/20.** Deuda en cero verificada por re-export. Build final `hpf-inbound-handler-final-2026-08-05.json` |
| 2026-08-05 | **F2 corrida completa**: 35 casos · 32 PASA · 2 PARCIAL · 1 FALLA · 0 SIN-EVIDENCIA · S1 19/20 · 93 artefactos |
| 2026-08-05 | F2: 4 de los 7 no-verdes del primer baseline eran defectos de mis asserts, no del bot. Corregidos y re-corridos: los 4 pasan |
| 2026-08-05 | D-02/D-03/D-05 resueltas por la agencia. Debounce a 50 s (no 15). Hallazgo nuevo: corrección de colores de peluche del 3/8 sin aplicar → FIC-035 |
| 2026-08-05 | F1+: ampliación por el chat con Oscar (jul/ago) y el audio de Juanpi. +8 casos → denominador 33. D-01 y D-04 resueltas |
