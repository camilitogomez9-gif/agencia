# Incidente — PERIODONCIA Mayo aparece en $0 (reporte primera semana de junio)

**Fecha del reporte erróneo:** primera semana de junio 2026 (sábado pre-fix).
**Fecha del postmortem:** 2026-06-14.
**Fecha del cierre:** 2026-06-15.
**Severidad:** alta (reporte de facturación visible al cliente con cifra incorrecta).
**Estado:** ✅ **RESUELTO**. Smoke tests v3.6 + v6 OK. Cutover a producción.

---

## ⚠ CAUSA RAÍZ REAL — descubierta 2026-06-15 (corrige diagnóstico inicial)

El postmortem inicial (sección "Audit del Histórico_2M" abajo) identificó como causa el **drift de códigos PERIODONCIA↔PROTESIS entre meses**. Eso resultó ser un **diagnóstico parcial / incorrecto**. La causa raíz real fue otra:

### Bug 1 — Upsert Histórico tabla sin matching column configurado
Desde la migración a Data Tables nativas n8n (2026-06-06), el nodo `Upsert Histórico tabla` quedó con `filters.conditions: [{}]` vacío y `matchingColumns: []`. La UI mostraba `id (number) Equals (vacío)` como condition. **Sin matching real, cada corrida del workflow insertaba TODAS las filas como nuevas** (sin dedup por `_key`). Acumulamos **50.422 filas duplicadas en ~9 días** (13x el volumen real).

### Bug 2 — Fan-out implícito post-fix Upsert
Al corregir el Upsert (matching column = `key`), el nodo pasó a emitir N items downstream (uno por fila procesada). El `Get Histórico tabla` se ejecuta UNA VEZ POR CADA INPUT ITEM (confirmado en código fuente n8n `selectMany.ts`). Con N ≈ 3000 items × 3920 filas materializadas en RAM cada una → SIGKILL del worker → mensaje "may have run out of memory".

### Bug 3 — CODIGO_A_CATEGORIA desactualizado en v3.5
El v3.5 vigente tenía CODIGO_A_CATEGORIA con códigos faltantes: `PE1000`, `PE1005`, `OR127`, `OA049`, `RD008` (~$35.060 en junio, ~13 filas). Estos caían en `OTRO` → se descartaban del reporte. Esto **NO era drift** — era simplemente que Cecilia agregó códigos al catálogo después de la última regeneración manual del nodo.

### Bug 4 — Filtro de campos del Correos no propagaba la fecha
Mi v6 inicial asumió que `_fechaISO` estaría disponible (como en el Reporte), pero el Correos no tiene `Parsear y validar fecha` upstream y el `Filtro de campos` con `includeFields: "id"` solo propagaba el `id`. Mi `derivarMesKey` no encontraba la fecha → `_error: true` para todas las filas.

### Por qué el incidente PERIODONCIA Mayo = $0 ocurrió
**Combinación de Bug 1 + Bug 3**: la duplicación 13x sobre datos que el v3.5 mapeaba a `OTRO` (códigos PE* nuevos) más anomalías de SQLite con fragmentación post-DELETE pueden haber causado un comportamiento errático puntual. Lo importante: el sistema mes-aware (snapshot v2 + lookup por mes) **NO era el fix correcto** para este caso. Lo que sí resolvió el incidente:

1. Setear matching column `key` en Upsert Histórico tabla.
2. Setear `executeOnce: true` en Get Histórico tabla.
3. Purgar y repoblar la Data Table.
4. Actualizar CODIGO_A_CATEGORIA con los códigos nuevos (v3.6 ya los tiene del snapshot v2).

### El sistema mes-aware sigue siendo útil
Aunque no era el fix del incidente puntual, el snapshot mes-aware + `CODIGOS_AMBIGUOS` (réplica del v3.5 viejo) + el runbook operativo dejan el sistema preparado para futuros casos reales de drift (cuando un código cambie de Rubro entre meses) sin requerir intervención manual sobre el JSON del workflow.

---

## Fixes aplicados y validados con smoke test (2026-06-15)

| Fix | Workflow | Verificado |
|---|---|---|
| Upsert: matching column `key` + condition `key = {{ $json._key }}` | v3.6 Reporte | ✅ |
| Get Histórico tabla: `executeOnce: true` | v3.6 Reporte | ✅ |
| Get row(s) in sheet × 2: `executeOnce: true` (defensivo) | v6 Correos | ✅ |
| Categoria/Filtro/Clase: TABLA_MES_AWARE + CODIGOS_AMBIGUOS + resolverAmbiguo | v3.6 + v6 | ✅ |
| Filtro de campos del Correos: `includeFields: "id, Fecha_de_recepcion_del_pago"` | v6 Correos | ✅ |
| Data Table purgada de duplicados (50.422 → ~3920) | Storage | ✅ |

**Smoke v3.6 (corrida 2026-06-15):**
- Mayo: $4.219.997 (coincide histórico exacto)
- Junio: $943.280 (recupera los $35.060 perdidos en v3.5 por códigos no mapeados)
- PERIODONCIA Mayo: $31.370 (resolverAmbiguo correcto)
- PERIODONCIA Junio: $4.680 (incluye PE1000 + PE1005 que v3.5 perdía)

---

---

## Audit del Histórico_2M (2026-06-14)

El export del Histórico Mayo+Junio confirmó la causa raíz con números concretos:

| Mes | Códigos P* viejos (clasificados como PROTESIS) | Códigos PE* nuevos (clasificados como PERIODONCIA) |
|---|---|---|
| 2026-05 | **20 filas / $52.300** | 0 filas / $0 |
| 2026-06 | 3 filas / $10.770 | 2 filas / $4.680 |

**Diagnóstico cuantificado:**
- En mayo, el **100% de las prestaciones PERIODONCIA** del mes se cobraron con códigos `P*` viejos. El reporte erróneo perdió $52.300 que cayeron en PROTESIS.
- En junio, la transición a códigos `PE*` está en curso (40% migrados). Aún hay $10.770 con códigos P* viejos.
- Códigos efectivamente usados con P* en mayo: P1000, P1001, P1002, P2000, P2001. En junio: P1002, P2000.

## Override del snapshot — DESCARTADO 2026-06-15

**Primer intento (2026-06-14):** se aplicó override manual mapeando los 9 P* a PERIODONCIA en mayo+junio. Esto era INCORRECTO: las 20 filas P* de mayo se dividen en 12 con `Nombre categoría = PERIODONCIA` ($31.370) y 8 con `Nombre categoría = REHABILITACION CON PROTESIS` ($20.930). El override metía las 8 PROTESIS en PERIODONCIA por error.

**Corrección (2026-06-15):** override eliminado vía `scripts/utilities/clear-overrides-snapshot.py`. Snapshot restaurado a los valores naturales del xlsx (P* = PROTESIS en mayo y junio).

**Patrón correcto** (replica del v3.5 viejo): los códigos ambiguos (P0000, P1000-P1004, P2000-P2002) se resuelven en runtime por el `Nombre categoría` original de cada fila, NO por lookup mes-aware. Implementado en los nodos JS del v3.6 con:

```js
const CODIGOS_AMBIGUOS = new Set(["P0000","P1000",...,"P2002"]);
function resolverAmbiguo(nombreCat) {
  const n = String(nombreCat || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toUpperCase().trim();
  if (n.includes("PERIODONCIA")) return "PERIODONCIA";
  if (n.includes("REHABILITACION CON PROTESIS")) return "PROTESIS";
  return "OTRO";
}
```

En el nodo Categoria: si el código es ambiguo → `resolverAmbiguo(row.Categoria)`. En el nodo Clase: si es ambiguo → descartar (no es ortodoncia). En el nodo Filtro: siempre válido.

**Resultado esperado** para mayo según simulación: PERIODONCIA = $31.370 (12 filas), PROTESIS = $325.811 (8 P* + 27 PROTESIS regulares). Esto replica fielmente el comportamiento del v3.5 viejo.

---

## 1. Resumen ejecutivo

El reporte automático de facturación de Sonrisas correspondiente a la primera semana de junio 2026 mostró el campo **PERIODONCIA — Mayo** con valor `$0` cuando en realidad esa categoría tenía facturación real en mayo. La data no estaba perdida; estaba en la Data Table `SNR | Histórico Pagos` con sus códigos originales de mayo, pero el clasificador del workflow (nodos `Filtro/Categoria/Clase`) aplicaba el **listado de códigos de junio** sobre filas cuyo `Mes_de_recepcion_del_pago` era `"Mayo"`. Como Cecilia modificó/recategorizó códigos de PERIODONCIA entre el listado de mayo y el de junio, las filas de mayo cayeron en otra categoría (o quedaron como `OTRO`) y la celda `PERIODONCIA — Mayo` agregada quedó vacía.

---

## 2. Detección

Reporte detectado por el equipo de Sonrisas (Cecilia) al revisar el reporte del sábado. Reportado a la agencia durante la semana del 2026-06-08.

---

## 3. Impacto

- Reporte de facturación con valor incorrecto en celda `PERIODONCIA — Mayo` → cliente recibe número errado.
- Total del mes de Mayo subreportado por el monto de las filas que cambiaron de categoría.
- Otras categorías que NO tuvieron cambio de códigos entre meses se mantuvieron correctas.

Decisión del usuario: **NO se re-emite el reporte corregido al cliente.** Solo se asegura que el próximo (post-deploy del fix) salga correcto.

---

## 4. Causa raíz

**Clasificación mes-agnóstica sobre data de 2 meses.**

El nodo `Get Histórico tabla` filtra server-side por `Mes_de_recepcion_del_pago` ∈ {mes corriente, mes anterior} y trae las filas de ambos. Después, los nodos `Filtro1`, `Categoria` y `Clase1` (en Reporte v3.5) y sus equivalentes en Correos v5 aplican el listado de códigos del mes corriente sobre TODAS las filas:

- `CODIGOS_VALIDOS` (Set) — del Filtro: ~358 códigos del último xlsx de Cecilia.
- `CODIGO_A_CATEGORIA` (Object) — del Categoria: lookup código → categoría del último xlsx.
- `CLASES_ORTODONCIA` (Object) — del Clase1: AJUSTE/RETIRO/COMBO del último xlsx.

Si Cecilia entre mayo y junio:
- **Renombró un código** (ej. `P1005` → `PE1005`): la fila de mayo con `P1005` no matchea ninguna entrada de junio → cae en `OTRO` (Categoría) o es descartada (Filtro lanza error).
- **Recategorizó** (ej. `P0000`: PERIODONCIA en mayo → PROTESIS en junio): la fila de mayo se clasifica como PROTESIS — incorrecto para el período mayo.
- **Retiró el código**: el snapshot lo preservaba (union xlsx ∪ snapshot), pero usaba la categoría persistida — y el script `update-sonrisas-nodes.py` aborta ante conflicto de categoría entre snapshot y xlsx, forzando intervención manual (que no ocurrió a tiempo en este caso, o que se resolvió con flag `--no-snapshot` perdiendo histórico).

Para el caso PERIODONCIA específicamente, hay evidencia en la migración a Data Tables del 2026-06-06 (`cambios-flujo-facturacion-drift-codigos-2026-06-06.md`) de que el xlsx tenía **11 códigos duplicados con conflicto `PERIODONCIA↔PROTESIS`** (`P0000, P1000–P1004, P2000–P2002`). El snapshot vigente al momento del reporte de junio reflejaba la decisión de junio para esos códigos, no la de mayo.

---

## 5. Por qué no se detectó antes

1. El sistema de snapshot (v1, flat) **acumula 1 sola entrada por código**: `{categoria, clase, first_seen, last_seen_xlsx}`. No tiene noción de "este código tenía OTRA categoría el mes pasado".
2. El script `update-sonrisas-nodes.py` aborta ante conflicto categoría/clase entre snapshot y xlsx. Eso fuerza una resolución manual cuando Cecilia cambia algo. Pero el flujo previsto (`--no-snapshot` para regenerar) **descarta el histórico**, lo cual es exactamente el bug.
3. El diseño asumía estabilidad mensual de la tabla código→categoría. Esa hipótesis nunca fue cierta del todo, pero se hizo visible con la migración masiva de PERIODONCIA en mayo→junio.

---

## 6. Fix aplicado

### Solución: clasificación mes-aware con snapshot v2

**Snapshot v2 reestructura `codigos[X]`** de flat a mes-aware:

```json
"codigos": {
  "OA001": {
    "meses": {
      "2026-05": {"categoria": "ORTODONCIA", "clase": "AJUSTE", ...},
      "2026-06": {"categoria": "ORTODONCIA", "clase": "RETIRO", ...}
    },
    "first_seen": "2026-05-01",
    "last_seen_xlsx": "2026-06-15"
  }
}
```

**Nodos JS** (`Filtro/Categoria/Clase`) regenerados con tabla multi-mes embebida + función `lookupMesAware(codigo, mes_key)` que:
1. Busca match directo en `tabla[mes_key]`.
2. Si no hay, fallback hacia atrás (mes más reciente ≤ `mes_key`).
3. Si no hay, fallback hacia adelante (último recurso, mes más antiguo > `mes_key`).
4. Si no hay en ningún mes, `_error: true` (igual que hoy: `Filtro` emite error y el IF `Códigos inválidos?` branchea a `Respond Error`).

**`mes_key` se deriva** de `_fechaISO` (poblado aguas arriba por el nodo `Parsear y validar fecha`) tomando `.substring(0, 7)`. Esto sortea la ambigüedad del nombre del mes en español (no necesitamos parsear `"Mayo"` a `2026-05`, el año ya está en la fecha original).

**Script `update-sonrisas-nodes.py`** acepta flag `--mes YYYY-MM` y mergea el xlsx solo en `meses[mes_arg]`, sin tocar meses anteriores. Cambios de categoría/clase respecto al último mes registrado **NO abortan** — se reportan en un bloque "REVISIÓN REQUERIDA" al final del run para que el operador confirme.

### Archivos del fix

- `scripts/utilities/migrate-snapshot-mesaware.py` — one-shot v1 → v2 con backup automático.
- `scripts/utilities/update-sonrisas-nodes.py` — refactor mes-aware (`SNAPSHOT_VERSION = 2`).
- `scripts/utilities/verify-sonrisas-codigos-mesaware.py` — 10 casos golden.
- `clients/SNR_Sonrisas/03_workflows/sonrisas-reporte-facturacion-v3.6.json` — pendiente.
- `clients/SNR_Sonrisas/03_workflows/sonrisas-correos-reportes-facturacion-v6.json` — pendiente.

---

## 7. Plan de prevención

1. **Verificación golden** (`verify-sonrisas-codigos-mesaware.py`) — 10 casos cubriendo cambios entre meses, fallbacks, códigos retirados/nuevos. Se ejecuta antes de cada deploy.
2. **Bloque "REVISIÓN REQUERIDA"** al final de cada corrida de `update-sonrisas-nodes.py` — lista todos los cambios de categoría/clase entre el xlsx actual y el último mes registrado. Operador inspecciona antes de pegar nodos. **Atrapa errores tipo "Cecilia mandó el listado equivocado" o "reclasificó por accidente".**
3. **Changelog persistido en snapshot** — cada cambio queda registrado con `{fecha_corrida, mes_arg, cod, campo, antes, ahora}`. Auditable vía `git log` sobre el JSON.
4. **Pedido a Cecilia** — etiquetar el mes en el mensaje de envío del xlsx. Si reclasificó algún código vs el mes anterior, avisar cuáles.
5. **Ventana de pruning ampliada** — pasa de 2 meses a 6, dando holgura para backfills y re-procesos retroactivos.

---

## 8. Timeline

| Fecha | Evento |
|---|---|
| Pre 2026-05 | xlsx de Cecilia previos. Categoria del listado mayo persistida en nodos v3.5. |
| 2026-05-XX | Cecilia envía xlsx de mayo con códigos de PERIODONCIA vigentes ese mes. |
| 2026-06-06 | Migración a Data Tables. Snapshot v1 inicializado con códigos del último xlsx (junio). `last_updated: 2026-06-06`. Códigos PERIODONCIA refactorizados (`P*` → `PE*` o recategorizados). |
| Primera semana de junio | Reporte automático se ejecuta. Trae filas de mayo (con códigos viejos) + junio (códigos nuevos). Clasifica todas con códigos de junio. **PERIODONCIA Mayo agregada = $0.** |
| 2026-06-08 (~) | Cecilia detecta el error y lo reporta. |
| 2026-06-14 | Diagnóstico + diseño + implementación del fix en repo (scripts + plan). Bootstrap pendiente de xlsx de mayo. |
| Pendiente | Bootstrap (xlsx mayo + junio) → workflows v3.6 + v6 → smoke test → cutover. |

---

## 9. Comunicación al cliente

**Decisión del usuario:** NO se comunica el bug al cliente. El postmortem queda interno (la agencia). El próximo reporte (post-deploy) saldrá correcto y se asume continuidad.
