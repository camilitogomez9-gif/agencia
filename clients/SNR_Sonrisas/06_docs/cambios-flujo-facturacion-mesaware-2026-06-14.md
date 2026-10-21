# Cambios técnicos — Clasificación mes-aware (v3.6 + v6 + snapshot v2)

**Fecha:** 2026-06-14.
**Workflows:** `sonrisas-reporte-facturacion-v3.5` → **v3.6** · `sonrisas-correos-reportes-facturacion-v5` → **v6**.
**Snapshot:** `codigos-historico.json` v1 (flat) → **v2** (mes-aware) con backup automático.
**Scripts:** `update-sonrisas-nodes.py` refactor + 2 scripts nuevos.
**Plan:** `/Users/camilo/.claude/plans/en-base-al-ltimo-velvety-starlight.md`.
**Postmortem:** `incidente-periodoncia-mayo-2026-06-14.md`.

---

## 1. Resumen del cambio

Los workflows clasificaban todas las filas del Histórico (2 meses) con UN solo juego de códigos hardcodeado (el del último xlsx). Ahora cada fila se clasifica con los códigos vigentes EN SU MES de recepción del pago. El snapshot persiste la clasificación por mes. Los 9 nodos JS (3 únicos × 3 instancias: Reporte v3.6 + 2 ramas de Correos v6) embeben una `TABLA_MES_AWARE` con la ventana de meses persistida.

Sin Data Tables nuevas. Sin rotación manual. Sin cambio operativo significativo para Cecilia (solo etiquetar el mes en el mensaje).

---

## 2. Snapshot v1 → v2

### Estructura v1 (flat)

```json
{
  "version": 1,
  "codigos": {
    "OA001": {
      "categoria": "ORTODONCIA",
      "clase": "AJUSTE",
      "first_seen": "2026-06-06",
      "last_seen_xlsx": "2026-06-06"
    }
  }
}
```

### Estructura v2 (mes-aware)

```json
{
  "version": 2,
  "last_updated": "2026-06-14",
  "ventana_meses": 6,
  "codigos": {
    "OA001": {
      "meses": {
        "2026-05": {"categoria": "ORTODONCIA", "clase": "AJUSTE", "computaImporte": true, "computaCantidad": true},
        "2026-06": {"categoria": "ORTODONCIA", "clase": "RETIRO", "computaImporte": true, "computaCantidad": true}
      },
      "first_seen": "2026-05-01",
      "last_seen_xlsx": "2026-06-15"
    }
  },
  "changelog": [
    {"fecha_corrida": "2026-06-15", "mes_arg": "2026-06", "cod": "OA001", "campo": "clase", "antes": "AJUSTE", "ahora": "RETIRO"}
  ]
}
```

Cambios:
- `meses[YYYY-MM]` reemplaza los campos flat. Cada entrada de mes guarda `categoria`, `clase`, `computaImporte`, `computaCantidad`.
- `ventana_meses` controla el pruning (default 6, antes 2).
- `changelog` append-only: cada cambio detectado por el script queda registrado con fecha + diff. Auditable vía git diff.

### Migración (one-shot)

`scripts/utilities/migrate-snapshot-mesaware.py`:
- Lee snapshot v1.
- Crea backup en `_snapshots/codigos-historico.v1-backup.json` (no sobreescribe si ya existe).
- Genera v2: cada código pasa a `meses[YYYY-MM]` donde YYYY-MM = `last_seen_xlsx[:7]` (o `last_updated[:7]` global como fallback).
- `computaImporte` y `computaCantidad` por defecto `true` (el v1 no los persistía; política conservadora coherente con el comportamiento previo: códigos legacy se asumían computables).
- Idempotente: si ya es v2, no toca.

---

## 3. Cambios al script `update-sonrisas-nodes.py`

### Constantes
- `SNAPSHOT_VERSION = 2`
- `VENTANA_MESES_DEFAULT = 6`
- `TZ_OPERATIVA = "America/Montevideo"`

### Flags CLI nuevos
- `--mes YYYY-MM` (recomendado) — explicita a qué mes corresponde el xlsx que se está procesando. Sin flag, default = mes actual TZ Montevideo + banner de advertencia.
- `--force-mes` — bypass para casos extremos (backfill > 6 meses atrás, futuro > 1 mes).
- `--no-snapshot` — modo bypass: tabla mes-aware solo con datos del xlsx (sin fallback útil). Para debug.

### Funciones renombradas / refactorizadas

| Antes | Ahora | Cambio |
|---|---|---|
| `validar_conflictos` | `detectar_cambios_clasificacion` | **NO aborta**. Compara xlsx vs último mes anterior registrado. Devuelve cambios para reportar al final. |
| `unir_con_snapshot` | `materializar_tabla_mes_aware` | Output cambia: `{tabla_por_mes, todos_codigos_union, meses_ordenados}`. Combina snapshot + xlsx mes_arg. |
| `actualizar_snapshot` | (sig. nueva) | Recibe `mes_arg`, mergea xlsx en `meses[mes_arg]` sin tocar otros meses. Appendea `changelog`. |
| `cutoff_pruning` | `cutoff_pruning_yyyymm` | Devuelve YYYY-MM (no `date`). Default `meses=6`. |
| `prunear_snapshot` | (mismo nombre) | Itera `meses[]` borrando entradas con YYYY-MM < cutoff. Si todas se borran, borra el código entero. |
| `generar_filtro` | `generar_filtro_mesaware` | Embebe `TABLA_MES_AWARE` + lookup con fallback. Elimina `CODIGOS_VALIDOS` Set. |
| `generar_categoria` | `generar_categoria_mesaware` | Idem. Elimina `CODIGOS_AMBIGUOS` y `resolverAmbiguo` (no aplican más). |
| `generar_clase` | `generar_clase_mesaware` | Idem. `cantidadComputable` deriva de `entrada.computaCantidad` mes-aware. |

### Funciones nuevas
- `derivar_mes_arg(args)` — parsea `--mes` o usa default. Valida rango (±VENTANA_MESES vs hoy). Aborta sin `--force-mes` si fuera de rango.
- `imprimir_resumen_cambios(cambios)` — imprime bloque "REVISIÓN REQUERIDA" al final del run.

### Funciones eliminadas
- `validar_conflictos` (reemplazada por `detectar_cambios_clasificacion`).
- `unir_con_snapshot` (reemplazada por `materializar_tabla_mes_aware`).

### Funciones intactas
- `leer_excel`, `validar_codigos_unicos` (aborta si códigos duplicados internos al xlsx), `validar_rubros_conocidos` (aborta si Rubro desconocido).

---

## 4. Cambios a los 9 nodos n8n

### Patrón embebido en cada nodo

```js
const TABLA_MES_AWARE = {
  "2026-05": { "OA001": {categoria:"ORTODONCIA",clase:"AJUSTE",computaImporte:true,computaCantidad:true}, ... },
  "2026-06": { ... }
};

const MESES_ORDENADOS = ["2026-05", "2026-06"];

function lookupMesAware(codigo, mes_key) {
  // match directo
  let entrada = (TABLA_MES_AWARE[mes_key] || {})[codigo];
  if (entrada) return { entrada, fallback: null };
  // hacia atrás: mes más reciente <= mes_key
  for (let i = MESES_ORDENADOS.length - 1; i >= 0; i--) {
    const m = MESES_ORDENADOS[i];
    if (m > mes_key) continue;
    if ((TABLA_MES_AWARE[m] || {})[codigo]) {
      return { entrada: TABLA_MES_AWARE[m][codigo], fallback: "atras:" + m };
    }
  }
  // hacia adelante: mes más antiguo > mes_key (último recurso)
  for (let i = 0; i < MESES_ORDENADOS.length; i++) {
    const m = MESES_ORDENADOS[i];
    if (m <= mes_key) continue;
    if ((TABLA_MES_AWARE[m] || {})[codigo]) {
      return { entrada: TABLA_MES_AWARE[m][codigo], fallback: "adelante:" + m };
    }
  }
  return { entrada: null, fallback: null };
}

function derivarMesKey(row) {
  // Prioriza _fechaISO; fallback a Fecha_de_recepcion_del_pago (string o Luxon)
  const candidatos = [row._fechaISO, row.Fecha_de_recepcion_del_pago, row["Fecha de recepción del pago"]];
  for (const c of candidatos) {
    if (!c) continue;
    if (typeof c === "string" && c.length >= 7 && c[4] === "-") return c.substring(0, 7);
    if (c && typeof c === "object" && typeof c.toISO === "function") {
      const iso = c.toISO();
      if (iso && iso.length >= 7) return iso.substring(0, 7);
    }
  }
  return null;
}
```

### Comportamiento por tipo de nodo

| Nodo | Reporte v3.6 | Correos v6 Semanal | Correos v6 Mensual | Output |
|---|---|---|---|---|
| Filtro | `Filtro1` | `Filtro` | `Filtro3` | `_error: true` si código no existe en ningún mes, o si `_fechaISO` ausente. Agrega `computaImporte`, `computaCantidad`, `_warning_fallback`. |
| Categoria | `Categoria` | `Categoria` | `Categoria1` | `Categoria: entrada.categoria` o `"OTRO"` si nada. |
| Clase | `Clase1` | `Clase` | `Clase1` | Descarta filas sin clase (no-ortodoncia). `cantidadComputable: entrada.computaCantidad ? 1 : 0`. |

### Verificación pre-deploy en n8n

**Orden topológico crítico:** los nodos Filtro deben recibir filas con `_fechaISO` ya derivado. En Reporte v3.5, el flujo es `Get Histórico tabla → Parsear y validar fecha → Filtro de campos → Filtro1`. En Correos v5, hay 2 ramas (Semanal y Mensual). Antes de aplicar v6, **verificar que ambas pasen por `Parsear y validar fecha`** (o equivalente que provea `_fechaISO`) antes de su Filtro respectivo.

---

## 5. Bootstrap inicial (requisitos del usuario)

1. Conseguir xlsx de **mayo 2026** archivado de Cecilia (decisión cerrada con el operador).
2. Conseguir xlsx de **junio 2026** (debería ser el último que mandó).

Pasos del bootstrap (ver `runbook-actualizacion-codigos-mes.md`):

```bash
# 1. Migrar snapshot v1 → v2 (one-shot, idempotente)
python3 scripts/utilities/migrate-snapshot-mesaware.py

# 2. Cargar mayo
python3 scripts/utilities/update-sonrisas-nodes.py ~/Downloads/listado-mayo.xlsx --mes 2026-05

# 3. Cargar junio (re-corrida)
python3 scripts/utilities/update-sonrisas-nodes.py ~/Downloads/listado-junio.xlsx --mes 2026-06

# 4. Inspeccionar diff del snapshot
git diff clients/SNR_Sonrisas/_snapshots/codigos-historico.json
```

El bloque "REVISIÓN REQUERIDA" del paso 2 listará exactamente los códigos PERIODONCIA que cambiaron entre mayo y junio — esto es la **confirmación de la causa raíz** del incidente.

Plan B si no aparece el xlsx de mayo: parsear el JS embebido en los nodos `Filtro1/Categoria/Clase1` del workflow v3.5 productivo (que reflejaba el listado de Cecilia anterior al 2026-06-06) con un script auxiliar `bootstrap-snapshot-desde-nodos.py`. Menos preciso pero suficiente.

---

## 6. Deploy

### Versionado
- Reporte: v3.5 → **v3.6**
- Correos: v5 → **v6**
- Snapshot: v1 → **v2** (+ `codigos-historico.v1-backup.json`)

### Cutover (sábado mañana, pre-trigger nocturno)
1. Importar v3.6 y v6 como workflows nuevos en n8n.
2. Smoke test manual: correr v3.6 sobre datos reales y comparar Sheet output con la corrida de v3.5 del sábado pasado. **Diferencia esperada: PERIODONCIA Mayo > 0.**
3. Smoke test v6 con email redirigido al inbox de la agencia.
4. Correr `verify-sonrisas-codigos-mesaware.py` con casos custom basados en el incidente real.
5. Desactivar trigger v3.5 + v5. Activar trigger v3.6 + v6.
6. Renombrar v3.5/v5 con sufijo `[DEPRECATED 2026-06-DD]`.

### Rollback
- Antes del cutover: nada que hacer, productivos siguen activos.
- Post-cutover si falla: reactivar v3.5/v5, desactivar v3.6/v6 antes del siguiente trigger. El snapshot v2 puede coexistir con v3.5/v5 (estos embeben su propio JSON, no leen el snapshot).
- Si corrupción del snapshot v2: `codigos-historico.v1-backup.json` permite revertir.

---

## 7. Pedidos a Cecilia (operativos, mínimos)

- En cada mensaje de envío del listado mensual, etiquetar a qué mes corresponde ("Listado de junio 2026").
- Si reclasificó un código vs el mes anterior, avisar cuáles (ayuda a priorizar la inspección del bloque "REVISIÓN REQUERIDA" del script).
- Lo que NO cambia: sigue mandando el mismo xlsx con la misma columna Rubro. No accede a n8n ni a snapshots.

---

## 8. Archivos modificados / nuevos

### Nuevos
- `scripts/utilities/migrate-snapshot-mesaware.py` — one-shot v1→v2
- `scripts/utilities/verify-sonrisas-codigos-mesaware.py` — golden tests
- `scripts/utilities/audit-sonrisas-historico-codigos.py` — audita export del Histórico (CSV/JSON/XLSX) → P* vs PE* por mes
- `scripts/utilities/override-snapshot-codigos.py` — aplica overrides manuales (caso PERIODONCIA P*) + changelog
- `scripts/utilities/regen-bloques-js-from-snapshot.py` — re-emite los 3 bloques JS desde el snapshot sin tocar update-sonrisas-nodes ni el snapshot
- `clients/SNR_Sonrisas/_snapshots/codigos-historico.v1-backup.json` — backup del v1 pre-migrate
- `clients/SNR_Sonrisas/_snapshots/nodos-js-2026-06-14/` — 3 archivos JS (filtro/categoria/clase) listos para pegar
- `clients/SNR_Sonrisas/03_workflows/sonrisas-reporte-facturacion-v3.6.json` — generado (45 nodos, 0.28 MB)
- `clients/SNR_Sonrisas/03_workflows/sonrisas-correos-reportes-facturacion-v6.json` — generado (44 nodos, 0.46 MB)
- `clients/SNR_Sonrisas/06_docs/incidente-periodoncia-mayo-2026-06-14.md` — postmortem con audit + override
- `clients/SNR_Sonrisas/06_docs/cambios-flujo-facturacion-mesaware-2026-06-14.md` (este doc)
- `clients/SNR_Sonrisas/06_docs/runbook-actualizacion-codigos-mes.md`

### Modificados
- `scripts/utilities/update-sonrisas-nodes.py` (refactor mes-aware)
- `clients/SNR_Sonrisas/_snapshots/codigos-historico.json` (v1 → v2)
- `clients/SNR_Sonrisas/CLIENT_INFO.md` (nueva sección)
- `CLAUDE.md` raíz (status SNR + workflows + runbook)

### Mantenidos (deprecados post-cutover)
- `clients/SNR_Sonrisas/03_workflows/sonrisas-reporte-facturacion-v3.5.json` (referencia 2 meses)
- `clients/SNR_Sonrisas/03_workflows/sonrisas-correos-reportes-facturacion-v5.json` (referencia 2 meses)

---

## 9. Riesgos residuales

1. **Pegado manual de 9 nodos en n8n.** Sin cambio respecto al flujo previo. Mitigado por el runbook.
2. **Cecilia podría mandar xlsx con etiqueta de mes equivocada.** Mitigado por el bloque "REVISIÓN REQUERIDA" que muestra cambios sospechosos antes de pegar.
3. **Corrupción del snapshot v2.** Mitigado por backup v1 + commits git + posible reconstrucción via JS embebido en workflow productivo.
4. **Cecilia no manda listado un mes.** Sistema sigue funcionando: filas de ese mes hacen fallback hacia atrás al mes registrado anterior. Warning loggable. No es ruptura.
