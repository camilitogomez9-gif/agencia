# Fix drift de códigos entre meses + saturación quota Google Sheets

> **⚠ Update 2026-06-14:** este doc describe el fix v3.5 de drift por unión `xlsx ∪ snapshot` (snapshot v1 flat). Resolvía "código retirado", **pero NO** "código con clasificación distinta entre meses" → causó el incidente PERIODONCIA Mayo = $0 en el reporte de primera semana de junio. **El fix definitivo (snapshot v2 mes-aware + workflows v3.6 + v6) está en `cambios-flujo-facturacion-mesaware-2026-06-14.md`.**

**Fecha:** 2026-06-06
**Workflow:** `Sonrisas | Reporte Facturación v3.5` (id `XCO4kWeKbsvPnnzz`)
**Severidad:** ALTA — bloqueaba el reporte cada mes después de regenerar el Filtro1.
**Relacionado:** `06_docs/fix-filtro1-if-codigos-invalidos-2026-06-06.md` (mismo día, otro bug del Filtro1).

---

## 1. Síntomas

### Síntoma A — drift de códigos entre meses

Cada mes, después de que Cecilia entrega un nuevo Listado de Precios y la agencia regenera
Filtro1/Categoria/Clase con `update-sonrisas-nodes.py`, el reporte falla TODO el mes hasta
que la ventana `Histórico_2M` deja de incluir el mes anterior:

- `Get Histórico` lee de la pestaña `Histórico_2M` (Google Sheets con QUERY server-side
  que filtra a mes corriente + mes anterior).
- Algunas filas del mes anterior tienen códigos que ya no están en el Listado de Precios
  actual (Cecilia los retiró).
- `Filtro1` los marca como inválidos → emite `{ _error: true, codigos: ... }` → IF
  `Códigos inválidos?` rutea a `Respond Error` → el reporte aborta cada corrida.

### Síntoma B — saturación de quota Google Sheets API

- Cuando `Get Histórico` se ejecuta solo (manual desde n8n UI): OK.
- Cuando se ejecuta en cadena tras `Get row(s) in sheet` + `Keyear Histórico` + `Upsert
  Histórico`: error de quota → falla.

## 2. Causa raíz

**Síntoma A.** El script `scripts/utilities/update-sonrisas-nodes.py` regeneraba el Set
`CODIGOS_VALIDOS` desde cero con cada corrida, tomando SOLO los códigos vigentes en el xlsx
actual. El listado del mes corriente no incluye códigos retirados del mes anterior, pero el
flujo en n8n necesita validarlos porque `Histórico_2M` los sigue trayendo.

**Síntoma B.** Sin nodo de espera entre `Upsert Histórico` y `Get Histórico`:
- La QUERY server-side de la pestaña `Histórico_2M` necesita tiempo para recompute después
  del Upsert.
- El bucket de quota de Google Sheets API (60 reads/min y 60 writes/min por usuario) se
  agota cuando los nodos Get + Upsert + Get se ejecutan back-to-back, especialmente si el
  Upsert hace muchas operaciones individuales por fila.

## 3. Solución

### A — Snapshot cumulativo con pruning automático

Mantener `clients/SNR_Sonrisas/_snapshots/codigos-historico.json` versionado en git, con
todos los códigos vistos en xlsx anteriores. El script:

1. Carga el snapshot al arrancar.
2. Detecta conflictos `categoria` o `clase` entre snapshot y xlsx — si hay, aborta sin
   generar bloques.
3. Genera Filtro/Categoria/Clase con `union(xlsx_actual, snapshot)`. Los códigos retirados
   del xlsx pero presentes en el snapshot siguen siendo válidos para el flujo.
4. Actualiza el snapshot con `last_seen_xlsx = fecha_hoy` para los códigos del xlsx; agrega
   nuevos con `first_seen = fecha_hoy`; preserva los códigos solo del snapshot sin tocar.
5. Prunea automáticamente los códigos cuyo `last_seen_xlsx` esté fuera de los últimos 2
   meses calendario (cutoff = primer día del mes anterior al corriente). Alineado con la
   ventana `Histórico_2M`.

**Flag opcional `--no-snapshot`:** bypass para regeneraciones de debug.

### B — Migración a Data Tables nativas n8n (reemplaza el Wait 60s)

**Update 2026-06-06 PM — fix definitivo:** se reemplazaron los nodos `Upsert Histórico` +
`Get Histórico` (Google Sheets) por `Upsert Histórico tabla` + `Get Histórico tabla` (Data
Tables nativas de n8n, tabla `SNR | Histórico Pagos` id `tpb3Go26RuhK5cuN`). Esto elimina
de raíz el problema de quota Google Sheets API y la latencia del QUERY recompute. El nodo
`Wait QUERY recompute` (60s) se removió — ya no es necesario.

El filtrado a "mes corriente + mes anterior" ahora vive en el nodo `Get Histórico tabla`
vía `filters.conditions` sobre la columna `Mes_de_recepcion_del_pago`, calculando los
nombres de meses en Montevideo con `$now.setZone('America/Montevideo').month`. Reemplaza
la pestaña `Histórico_2M` con fórmula QUERY del Google Sheet (que queda abandonada por si
se vuelve a Sheets en el futuro).

Cambios colaterales en los nodos `Parsear y validar fecha`, `Filtro de campos` y `Filtro1`
para contemplar los nuevos nombres de campos de la Data Table (snake_case sin tildes:
`Fecha_de_recepcion_del_pago`, `Pagado_Prestacion`, `Codigo_Prestacion`, `Nombre_Sucursal`,
`Nombre_categoria`, `Mes_de_recepcion_del_pago`, `Abono_Libre`, `id` en lugar de
`row_number`). `Filtro de campos` actúa como capa de normalización: lee los nombres nuevos
y reescribe a los nombres viejos para que el resto del flujo downstream (Categoria, Clase1,
Pagado Mes/Semana, etc.) NO necesite cambiar.

## 4. Cambios aplicados

### Archivos modificados/creados en este commit

- `scripts/utilities/update-sonrisas-nodes.py`:
  - 7 funciones nuevas (`cargar_snapshot`, `validar_conflictos`, `unir_con_snapshot`,
    `actualizar_snapshot`, `cutoff_pruning`, `prunear_snapshot`, `guardar_snapshot`,
    `snapshot_path_from_script`).
  - `main()` orquesta cargar → validar conflictos → unir → generar → actualizar → prunear
    → guardar.
  - Resumen ampliado: agrega bloque SNAPSHOT con counts (del xlsx, nuevos, solo snapshot,
    prunneados) + cutoff de pruning.
  - Flag `--no-snapshot`.
- `clients/SNR_Sonrisas/_snapshots/codigos-historico.json` (creado): bootstrap con los 340
  códigos vigentes hoy.
- `clients/SNR_Sonrisas/03_workflows/sonrisas-reporte-facturacion-v3.5.json` (sincronizado
  con producción 2026-06-06 PM):
  - **Migrado a Data Tables**: nodos `Upsert Histórico tabla` + `Get Histórico tabla`
    (`n8n-nodes-base.dataTable`) reemplazan los 2 nodos viejos de Google Sheets. Tabla
    `SNR | Histórico Pagos` id `tpb3Go26RuhK5cuN` (proyecto `OZub3m3DGqbZefcZ`).
  - `Get Histórico tabla` filtra por `Mes_de_recepcion_del_pago` igual al mes corriente o
    mes anterior (calculados con `$now.setZone('America/Montevideo').month`).
  - Nodo `Wait QUERY recompute` (60s) REMOVIDO — ya no necesario sin Google Sheets API.
  - `Parsear y validar fecha`: parsea `Fecha_de_recepcion_del_pago` (ISO 8601 con `Z`).
  - `Filtro de campos` (Set): lee nombres nuevos de la Data Table y los normaliza a los
    nombres viejos del flujo para que el resto del workflow no cambie. Assignments nuevos
    para `Pagado Prestación` y `Fecha de recepción del pago`. `includeFields: "id, _fechaValida,
    _fechaISO, _mesDerivado"`.
  - `Filtro1`: detección de `fechas_invalidas` ahora lee `Fecha_de_recepcion_del_pago` y `r.id`
    (en lugar de `Fecha de recepción del pago` y `r.row_number`). Tolerante a ambos nombres.

### Estado en n8n vivo

**Aplicado 2026-06-06 PM** (re-importado por la agencia desde el repo). Cadena Histórico final:

```
Webhook → Get row(s) in sheet → Keyear Histórico → Upsert Histórico tabla
       → Get Histórico tabla → Parsear y validar fecha → Filtro de campos → Filtro1 → …
```

JSON del repo (`sonrisas-reporte-facturacion-v3.5.json`) sincronizado con n8n vivo.

**Notas operativas:**
- La pestaña `Histórico_2M` del Google Sheet queda abandonada. Conservar la fórmula QUERY
  en A1 por si se vuelve a Sheets en el futuro (documentada en `CLAUDE.md` y en
  `fix-filtro1-if-codigos-invalidos-2026-06-06.md` §4).
- La pestaña `Histórico` del Sheet **ya no se actualiza** — `Upsert Histórico` (Sheet) fue
  reemplazado por `Upsert Histórico tabla` (Data Table). Todo el histórico nuevo vive en la
  Data Table de n8n. Para preservar los datos viejos del Sheet, hacer un export del Sheet
  `Histórico` → import a la Data Table `SNR | Histórico Pagos` (preservando `_key` como
  `key`, `# Pago` como columna explícita).
- **⚠ Impacto en el flujo de Correos (`sonrisas-correos-reportes-facturacion-v4.json`):**
  hoy lee del Sheet `Histórico` que ya no se actualiza → los emails Semanal y Mensual van a
  quedar con datos congelados a la última escritura de la cadena vieja. Acciones posibles:
  (a) migrar también el flujo de Correos a leer de la Data Table `SNR | Histórico Pagos`,
  (b) mantener el `Upsert Histórico` viejo en el Reporte hasta migrar Correos, o
  (c) duplicar el upsert (Data Table + Sheet) hasta migrar Correos. Decisión pendiente.

## 5. Guía operativa post-fix

### Cómo regenerar los nodos cuando Cecilia entrega un xlsx nuevo

```bash
python3 scripts/utilities/update-sonrisas-nodes.py ~/Downloads/"Listado de Precios Completo.xlsx"
```

El script:
- Valida el xlsx (códigos únicos + Rubros conocidos). Aborta si hay duplicados/desconocidos.
- Lee `_snapshots/codigos-historico.json` (si no existe, arranca vacío).
- Detecta conflictos categoría/clase snapshot vs xlsx. Aborta si los hay (ver §6).
- Imprime los 3 bloques JS listos para pegar.
- Actualiza el snapshot + prunea códigos no vistos en >2 meses.
- Imprime resumen detallado.

Pegar los 3 bloques en n8n + commit el snapshot actualizado.

### Cómo verificar manualmente qué códigos legacy retiene el snapshot

```bash
python3 -c "
import json
snap = json.load(open('clients/SNR_Sonrisas/_snapshots/codigos-historico.json'))
print(f'Total: {len(snap[\"codigos\"])} códigos')
for cod, info in sorted(snap['codigos'].items(), key=lambda x: x[1]['last_seen_xlsx']):
    print(f'  {cod:8s}  last_seen={info[\"last_seen_xlsx\"]}  cat={info[\"categoria\"]}')
" | head -30
```

## 6. Casos especiales

### Conflicto categoría/clase

Si Cecilia recategoriza un código a propósito (ej. mueve `OG045` de GENERAL a ORTODONCIA),
el script aborta:

```
ABORTADO — conflictos entre snapshot y xlsx. NO se generó ningún nodo.
❌ Código OG045 | categoria: xlsx='ORTODONCIA' vs snapshot='GENERAL'
```

Resoluciones posibles:
- **Editar el snapshot manualmente** (cambiar `categoria` de `OG045` a `ORTODONCIA`) y
  commit con mensaje explicativo. La próxima corrida ya no detecta conflicto.
- **Usar `--no-snapshot`** para regenerar ignorando el snapshot. Aceptar pérdida temporal
  del histórico de ese código (volverá la próxima corrida normal).

### Pruning de zombies

Si un código sigue siendo facturado en n8n pero Cecilia lo retiró del xlsx, el snapshot lo
conserva mientras siga apareciendo en la ventana de 2 meses. Una vez fuera de la ventana
(2 meses sin ver el xlsx), se prunea automáticamente. El resumen del script lista los
prunneados de cada corrida.

## 7. Riesgos conocidos

- **Acumulación zombie indefinida**: si el script no se corre durante un mes, el snapshot
  no se actualiza ni se prunea. Mitigación: la cadencia normal es mensual (junto a la
  entrega del listado de Cecilia).
- **Wait de 60s enmascara regresión de quota**: si Google cambia el comportamiento de
  QUERY recompute, podríamos no detectar degradación hasta que 60s también falle. Mitigación:
  monitorear duración del workflow en n8n; si sube de forma sostenida sin explicación,
  investigar antes de aumentar el Wait.
- **Workflow de Correos no actualizado**: `sonrisas-correos-reportes-facturacion-v4.json`
  comparte la lógica Filtro/Categoria/Clase. Por ahora se asume estable (no presentó este
  bug en producción). Si aparece, aplicar el mismo Wait + pegar bloques con snapshot
  aplicado.
