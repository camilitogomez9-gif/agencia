# Cierre de paridad HPF nuevo-vs-viejo — 2026-08-24

**Objetivo de la sesión**: cerrar los 2 fixes accionables (R9 · falsa premisa "Pantuflas
Normales Satín" + R6 · fugas de error técnico y rama fatal en Telegram) y el re-run
selectivo de 19 casos abiertos de la corrida manual del 18/8, antes de mandar a Oscar
para testing final y traspasar la WABA a producción (< 24 h de ventana).

**Criterio**: no "perfecto", sino **"cerrado con evidencia"** — GET-back verificado por
edición, baseline diff limpio, W1 gate 8/8, y snapshots pre/post con sha256.

**Resultado**: los 2 fixes aplicados y verificados, W1 gate estable, 0 regresiones
funcionales, 1 hallazgo nuevo no crítico. **Listo para mandar a Oscar.**

## 1. Fixes aplicados

### R9 · corregir falsa premisa "Pantuflas Normales Satín"

- **Parche**: [`03_workflows/parches-2026-08-24/w6-r9-pantuflas-normales-satin.json`](../03_workflows/parches-2026-08-24/w6-r9-pantuflas-normales-satin.json) — 1 edición sobre `Recolector.parameters.options.systemMessage` (62.785 → 62.893 chars).
- **Anchor**: la frase completa *"El material (satín / peluche) es una característica EXCLUSIVA de Pantuflas Mono. NO existen 'Pantuflas Normales Satín' ni 'Pantuflas Normales Peluche'…"* — anchor único (count = 1).
- **Reemplazo**: *"Las Pantuflas (normales) son de satín por defecto — ese es su material intrínseco… Lo que NO existe es 'Pantuflas Normales Peluche': el peluche solo aplica al modelo Mono…"* — preserva la mitad verdadera, corrige la falsa.
- **Aplicación**: `hpf-deploy-workflow.py --apply` con GET-back interno automático del runner ✓.
- **Verificación manual post-fix**:
  - `grep -c 'NO existen "Pantuflas Normales Satín" ni "Pantuflas Normales Peluche"'` → **0** ✓ (frase falsa removida)
  - `grep -c 'Las Pantuflas (normales) son de satín por defecto'` → **1** ✓ (frase nueva presente)
  - `grep -c 'NO existe.*Pantuflas Normales Peluche'` → **1** ✓ (mitad verdadera preservada)
  - Tabla de mapeo cliente→producto (líneas 850-856): sin tocar ✓.
- **Sub-workflow**: `Recolector1` en W7 ya no tenía la afirmación falsa (asimetría pre-existente); R9 alineó W6 con W7.
- **Justificación factual**: la descripción literal del catálogo (`catalogo-airtable.json`, records `Pantuflas boda` y `Pantuflas XV`) dice *"Pantuflas de satín personalizadas"*. Las Pantuflas normales SÍ son de satín — la premisa negada era factualmente falsa.

### R6 · sanear error de media + hacer no-fatal la rama de Telegram

- **Parche jsCode**: [`03_workflows/parches-2026-08-24/w1-r6-media-error-humano-no-fatal.json`](../03_workflows/parches-2026-08-24/w1-r6-media-error-humano-no-fatal.json) — 3 ediciones encadenadas sobre `TG · adjuntar media.parameters.jsCode` (3.038 → 3.109 → 3.239 → 3.308 chars).
  - Edit 1: closure `fallar(m)` → `fallar(m, debug)` (agrega field `_media_error_debug` opcional, para logging técnico).
  - Edit 2: llamada `fallar('GHL rechazo la subida (HTTP ' + st + ')…')` → mensaje humano `"No pude procesar tu archivo. Escribime lo que necesitás en texto y seguimos."` con debug `'GHL rechazo HTTP ' + st + '. ' + txt.slice(0, 140)`.
  - Edit 3: llamada `fallar('GHL acepto el archivo pero no devolvio URL…')` → mismo mensaje humano + debug técnico separado.
- **Verificación manual post-fix jsCode**:
  - `grep -c 'const fallar = (m, debug)'` → **1** ✓
  - `grep -c 'GHL rechazo la subida (HTTP'` (texto viejo, no debe estar) → **0** ✓
  - `grep -c "'GHL rechazo HTTP '"` (nuevo debug técnico) → **1** ✓
  - `grep -c "No pude procesar tu archivo"` (mensaje humano nuevo) → **2** ✓ (las 2 llamadas)
  - `grep -c "_media_error_debug"` → **1** ✓ (field disponible)
- **Script one-shot para bifurcar la conexión** (no se pudo hacer con parche estándar porque `hpf-deploy-workflow.py` sólo edita campos de nodos, no `connections`): [`scratchpad/hpf-r6-bifurcar-conexion.py`](https://placeholder-scratchpad) — bajar W1 → agregar `Normalizar entrada` como target adicional en `connections["TG · ¿media ok?"]["main"][1]` → PUT con las 5 keys canónicas → GET-back verificando el nuevo edge + que el resto de connections no cambió.
- **Verificación post-fix connections**:
  - Antes: `main[1]` = `[TG · aviso media]` (terminal)
  - Después: `main[1]` = `[TG · aviso media, Normalizar entrada]` (bifurcado ✓)
  - Resto de connections del IF y del resto del workflow: sin cambios ✓
- **Racional del diseño (documentado en el plan)**: NO separar `_media_error` en dos campos (los otros 3 writers ya escriben lead-safe, sólo `TG · adjuntar media` mezclaba). NO hacer que `TG · aviso media` deje de ser terminal (tiene 2 entradas: media fail Y no_soportado; volverlo no-terminal cambia también la rama de stickers/>20MB — fuera del scope R6). Bifurcar desde el IF es la solución más quirúrgica.
- **R6 vive en el path Telegram (test)**. El path productivo (WhatsApp vía W8 relay) no toca esta rama, así que este fix cierra la paridad en el carril donde Oscar testea; no es un fix "de producción".

## 2. Re-run selectivo (19 casos)

Detalle completo: [`07_testing/paridad-rerun-2026-08-24.md`](../07_testing/paridad-rerun-2026-08-24.md).

| Veredicto | Cantidad | Casos |
|---|---:|---|
| PARIDAD | 16 | A1, A3, B5, B8, B10, C1, C2, C6, C8, D1, D2, E2, E3, E4, H2, H3 |
| DIFERENCIA_ESPERADA | 0 | — |
| REGRESIÓN | 0 | — |
| HALLAZGO_NUEVO | 1 | **C4** — comportamiento nuevo post-R9, no crítico |
| BLOCKED_MANUAL | 2 | G3 (nota de voz), G5 (3 fotos juntas) — requieren Telegram real |
| **Total** | **19** | |

**El hallazgo C4** (pantuflas de satín 50 al CP): post-R9 el bot **pide aclaración** (normales vs Mono) en vez de cotizar Mono Satín directo por convención. Es una zona ambigua legítima introducida por corregir la premisa falsa. NO es regresión funcional (no rechaza, no rompe, el precio final es $30 en ambos casos). Se documenta como decisión abierta: preservar el comportamiento actual (pedir aclaración es más honesto ante ambigüedad genuina) o agregar una regla explícita que fuerce la convención "satín sin más = Mono Satín". Recomendación: **no fixear en esta sesión**, dejar la decisión para iteración menor v1.7.x según feedback de producción.

**G3 · nota de voz** (BLOCKED_MANUAL): no se pudo simular desde el runner sin infra adicional (requiere audio real corrupto desde Telegram). R6 se validó estructuralmente vía GET-back del jsCode + connections + W1 gate 8/8 post. Para verificación end-to-end funcional, la corrida de Oscar en Telegram con audio real bueno + malo cerrará el loop.

## 3. Baseline de regresión (pre vs post)

- Pre: [`03_workflows/ghl-live-2026-08-24/_baseline-pre.json`](../03_workflows/ghl-live-2026-08-24/_baseline-pre.json) (12 escenarios, 1 corrida c/u).
- Post: [`03_workflows/ghl-live-2026-08-24/_baseline-post.json`](../03_workflows/ghl-live-2026-08-24/_baseline-post.json) (idem).
- Diff: [`_baseline-diff.txt`](../03_workflows/ghl-live-2026-08-24/_baseline-diff.txt).

**2 diferencias detectadas, ninguna causada por R9/R6**:

1. **`oferta_precio` T4**: cambió `etapa_destino: null → "Cotizado"` y texto ligeramente distinto. Es variancia LLM sobre el mismo escenario que la guía ya documenta como *"falla ~2/5 veces"* (B4). El escenario es sobre sandalias (no toca R9) y no involucra Telegram media (no toca R6).
2. **`xv_cilindros` T3**: campo `nodos` pasó de lista larga a `[]`. Verificado: los hechos funcionales (`step`, `etapa_destino`, `n_burbujas`, `n_adjuntos`, `fichas`) son **idénticos** pre y post. Es artefacto de timing del script de baseline (la API de ejecuciones no había listado la ejecución cuando el script la consultó). No es una regresión.

**Conclusión**: **0 regresiones funcionales.** La memoria compartida entre los 5 agentes de W6 (`n8n_chat_histories`) no propagó efectos colaterales inesperados de R9.

## 4. W1 gate (topología crítica)

| Corrida | Resultado |
|---|---|
| Pre-cambios | `L6·W1: 8/8 corroborados` + `aristas cubiertas: 7/7` ✓ |
| Post-cambios | `L6·W1: 8/8 corroborados` + `aristas cubiertas: 7/7` ✓ |

Los 8 casos: I-01 camino feliz · I-02 idempotencia por messageId · I-03 etapa bloqueante → silencio · I-04 cliente que vuelve → aviso al equipo · I-05 debounce gana el último · I-06 relay sin contactId rompe · I-07 ruteo por tipo (imagen/audio/pdf) · I-08 sessionKey compatible con Kommo.

Las 7 aristas: `nuevo`, `duplicado`, `bloqueado`, `cliente_vuelve`, `seguir`, `gana_ultimo`, `pierde_debounce`.

**R6 no rompió W1 topológicamente** (era el riesgo principal — bifurcar la conexión del IF podía haber alterado ramas críticas).

## 5. Snapshots

- **Pre** (base rollback): [`03_workflows/ghl-live-2026-08-24/`](../03_workflows/ghl-live-2026-08-24/) — 13 workflows + README con sha256 (`ghl-live-2026-08-24/README.md`).
- **Post** (estado actual): [`03_workflows/ghl-live-2026-08-24-post-fixes/`](../03_workflows/ghl-live-2026-08-24-post-fixes/) — 13 workflows + README con sha256.

**Diff sha256 pre → post**:

| Workflow | Pre | Post | ¿Cambió? |
|---|---|---|---|
| W0 | `4dbfcc31cff6` | `4dbfcc31cff6` | — |
| **W1** | `b22edbd555f2` | **`9edb4c4900db`** | ✓ R6 (jsCode + connections) |
| W2 | `34288594b3f2` | `34288594b3f2` | — |
| W3 | `016e0ebee309` | `016e0ebee309` | — |
| W4 | `6b511e07ac43` | `6b511e07ac43` | — |
| W5 | `317ea80480a4` | `317ea80480a4` | — |
| **W6** | `1efd7de99f82` | **`ccb5359514d2`** | ✓ R9 (systemMessage del Recolector) |
| W7 | `0484118e0046` | `0484118e0046` | — |
| W8 | `b1e6559ef7a3` | `b1e6559ef7a3` | — |
| W9 | `c8fe1f0b6922` | `c8fe1f0b6922` | — |
| W10 | `f0104b456250` | `f0104b456250` | — |
| W11 | `eb1ffbe63d41` | `eb1ffbe63d41` | — |
| HPF (inactive) | `677c6e3e6b08` | `677c6e3e6b08` | — |

**Exactamente W6 y W1 cambiaron, y sólo esos**. Cero cambios inesperados en otros workflows durante la sesión ✓.

## 6. Items NO cerrados (transparencia)

### Bloqueados en Oscar (assets)

`clients/HPF_HappyFlops/06_docs/pedido-oscar-assets-2026-08-20.md`: pendientes de recibir del cliente. NO se persiguen en esta sesión.

### Fuera del scope autoimpuesto

- **R8** (cross-sell) — mecanismo probado previamente; cerrar necesita muestra grande, no cambios.
- **R5** (image classification en debounce window) — fuera de scope.
- **B10** (event persistence 4to turno) — corrido en el re-run (PARIDAD sobre 4 turnos observables); verificación de persistencia post-turno-5 requeriría casos adicionales fuera de la lista.

### Hallazgos posteriores (no bloqueantes para producción)

- **C4** (pantuflas de satín pide aclaración post-R9): ver §2 arriba. Decisión abierta.
- **Discrepancia menor de precio** en el prompt del Recolector: dice *"Pantuflas (normales) — $30"* pero el catálogo tiene $29 Boda / $30 XV. No bloqueante para producción; iteración menor si Oscar lo señala.
- **W6 tenía +1 nodo** vs el snapshot 08-18 (`Leer sugerencia anterior`, +1 nodo pre-sesión): cambio previo a esta sesión, presumiblemente de parches del 20/8. No afectó R9. Anotado.
- **`_media_error_debug`** creado por R6 no tiene logger persistente (Postgres/Sentry). Para diagnóstico post-cutover hay que ir al `executionData` de la ejecución específica en n8n. Suficiente para esta ventana; loggeo persistente queda para futura iteración.

### Higiene técnica (sin acción esta sesión)

- **Constante `SNAP`** en `hpf-deploy-workflow.py` apunta a `ghl-live-2026-08-12` (desactualizada). No se usa dentro del código; queda como referencia stale.
- **W11 vive en producción** (`aPZ71r7IVZTJ0iP5`) pero NO está en el dict `IDS` del runner. Si alguna vez hay que patchearlo con parche estándar, agregar la entrada.

## 7. Riesgo residual para producción

Ninguna regresión funcional detectada y los 2 gates críticos (baseline de regresión + W1 topological) pasaron limpios. El único cambio de comportamiento medible (C4) es una zona ambigua legítima donde el bot pide aclaración de más — en el peor caso el lead escribe una línea extra aclarando. R6 se validó estructuralmente pero **la corrida end-to-end con audio real en Telegram queda como verificación pendiente para la sesión de Oscar** — si un audio corrupto llegara a fallar antes del cutover WABA, el impacto es menor (el path productivo WABA no pasa por esta rama).

Aptitud para producción: **listo para mandar a Oscar y traspasar la WABA**, con la nota de que si en el testing él reporta que "pantuflas de satín" pide aclaración cuando antes cotizaba directo, esa es la conducta esperada post-R9 y se puede iterar en v1.7.x si genera fricción medible.

---

**Sesión cerrada.**
