# Runbook — Actualización mensual de códigos en Sonrisas

**Cuándo:** cada vez que Cecilia envía el Listado de Precios actualizado (mensual).
**Quién:** la agencia (operador principal). Edgardo como backup.
**Tiempo estimado:** 10-15 min (inspección rigurosa) o 5 min si no hay cambios entre meses.

---

## Pre-requisitos

- El snapshot debe estar en **v2** (mes-aware). Si todavía está en v1, correr una sola vez:
  ```bash
  python3 scripts/utilities/migrate-snapshot-mesaware.py
  ```
  Es idempotente. Crea backup automático.

- Confirmar con Cecilia el mes al que corresponde el xlsx (debe ir etiquetado en el mensaje, p.ej. "Listado de julio 2026").

---

## Paso 1 — Recibir el xlsx

Cecilia manda por WhatsApp/email el archivo `Listado de Precios Completo.xlsx` (o nombre similar).

**Confirmación con Cecilia:**
- Mes que cubre el listado (ej. "este es el de julio").
- Si reclasificó algún código vs el mes anterior, pedirle la lista. Esto acelera la inspección del paso 3.

Si Cecilia no especificó el mes, **preguntarle antes de seguir**. No asumir.

Guardar el archivo en `~/Downloads/` o donde sea cómodo.

---

## Paso 2 — Correr el script

```bash
cd ~/Downloads/camilo-workspace
python3 scripts/utilities/update-sonrisas-nodes.py \
    ~/Downloads/"Listado de Precios Completo.xlsx" \
    --mes 2026-07
```

**Reemplazar `2026-07` por el mes correspondiente (YYYY-MM).**

### Qué hace el script

1. Valida unicidad de códigos y Rubros conocidos. Aborta si hay error.
2. Carga el snapshot v2 actual.
3. Detecta cambios de categoría/clase vs el último mes anterior registrado para los mismos códigos.
4. Mergea el xlsx en `meses[--mes]` del snapshot.
5. Aplica pruning (borra entradas `meses[YYYY-MM]` con YYYY-MM > 6 meses atrás).
6. Imprime 3 bloques JS (Filtro / Categoria / Clase) listos para copy-paste.
7. Al final, imprime bloque **"REVISIÓN REQUERIDA"** si detectó cambios.

### Flags útiles

- Sin `--mes`: usa default = mes actual. Imprime banner amarillo pidiendo confirmación. **Mejor SIEMPRE pasar `--mes` explícito.**
- `--no-snapshot`: bypass del snapshot (solo usar para debug; pierde la tabla multi-mes).
- `--force-mes`: bypass de validación de rango (solo para backfill > 6 meses atrás o futuro > 1 mes).

---

## Paso 3 — Inspeccionar "REVISIÓN REQUERIDA"

Si el script imprimió un bloque tipo:

```
══════════════════════════════════════════════════════════════════════
⚠  REVISIÓN REQUERIDA — N cambio(s) de clasificación detectado(s)
   (2026-07 vs último mes registrado anterior)
══════════════════════════════════════════════════════════════════════
   Verificar con Cecilia si los cambios son intencionales antes de pegar
   los nodos en n8n. Cada cambio queda registrado en snapshot.changelog.

   OA001     | clase            | 2026-06 → 2026-07 : 'AJUSTE' → 'RETIRO'
   ...
══════════════════════════════════════════════════════════════════════
```

**Hay que decidir caso por caso si el cambio es legítimo:**

- Cecilia avisó del cambio en el mensaje → confirmar y seguir.
- Cecilia NO avisó pero el cambio tiene sentido (ej. la marca de un código pasó de AJUSTE a COMBO por un reagrupamiento conocido) → seguir.
- Cecilia NO avisó y el cambio es sospechoso (ej. medio listado cambió de categoría) → **PARAR, preguntarle a Cecilia antes de pegar nada en n8n**. Probable que mandó el xlsx equivocado.

Si todo OK, seguir al paso 4.

---

## Paso 4 — Verificar el snapshot

```bash
git diff clients/SNR_Sonrisas/_snapshots/codigos-historico.json
```

Esperado:
- `last_updated` actualizado.
- Nuevas entradas en `codigos[X].meses[<mes_arg>]`.
- Posibles entradas en `changelog`.
- Posibles `codigos[X]` borrados completos (si todas sus entradas se prunnearon — solo si el mes_arg está cerca del cutoff).

Si algo se ve mal (ej. desaparecen muchos códigos), **NO commitear**. Investigar.

---

## Paso 5 — Correr verifier

Si tenés casos custom para este mes (ej. códigos que sospechás que pueden estar mal), creá un `casos.json` y corré:

```bash
python3 scripts/utilities/verify-sonrisas-codigos-mesaware.py --casos casos.json
```

Mínimo: correrlo sin flags (built-in golden cases) y revisar que no haya FAILs no esperados.

---

## Paso 6 — Pegar los 3 bloques en n8n

Los bloques que imprimió el script van a estos nodos:

### Workflow `Sonrisas | Reporte Facturación` (v3.6)
- **Bloque Filtro** → nodo `Filtro1`
- **Bloque Categoria** → nodo `Categoria`
- **Bloque Clase** → nodo `Clase1`

### Workflow `Sonrisas | Correos Reportes Facturación` (v6)
- **Bloque Filtro** → nodos `Filtro` y `Filtro3` (los dos, son las ramas Semanal y Mensual)
- **Bloque Categoria** → nodos `Categoria` y `Categoria1`
- **Bloque Clase** → nodos `Clase` y `Clase1`

**Total: 9 pasteos.** El script imprime cada bloque con un separador `─────` claro y headers indicando dónde pegarlo.

Después de cada paste, guardar el workflow (`Ctrl+S`).

---

## Paso 7 — Smoke test en n8n

Antes de dejar los workflows productivos corriendo automáticamente:

1. Reporte v3.6: correr manualmente sobre datos reales (botón "Test workflow"). Comparar Sheet output con la corrida del último sábado.
   - **Diferencias esperadas**: solo en categorías donde Cecilia cambió clasificación entre meses.
   - Si NO hay diferencias esperadas, mirar más cuidadoso.
2. Correos v6: correr manualmente con email redirigido a inbox propio (cambiar destinatario temporalmente en el nodo Gmail). Verificar HTML.

---

## Paso 8 — Commit

```bash
git add clients/SNR_Sonrisas/_snapshots/codigos-historico.json
git add clients/SNR_Sonrisas/03_workflows/sonrisas-reporte-facturacion-v3.6.json
git add clients/SNR_Sonrisas/03_workflows/sonrisas-correos-reportes-facturacion-v6.json
git commit -m "snr: update codigos $(date +%Y-%m) - <breve descripcion>"
git push
```

Mensaje sugerido del commit:
```
snr: update codigos 2026-07 (listado de cecilia)

3 cambios de clasificación documentados en changelog (OA001 clase,
PE1005 categoria, etc). Snapshot v2 actualizado, 9 nodos n8n pegados,
smoke test OK.
```

---

## Troubleshooting

### El script aborta con "código DUPLICADO"
Cecilia mandó un xlsx con un código que aparece en >1 fila con Rubros distintos. Pedirle que lo corrija. El script no genera nada hasta entonces.

### El script aborta con "Rubro DESCONOCIDO"
Cecilia agregó un Rubro nuevo que no está en `RUBRO_A_CATEGORIA`. Dos opciones:
- Pedirle que use uno existente.
- Agregar el Rubro nuevo a `RUBRO_A_CATEGORIA` en `scripts/utilities/update-sonrisas-nodes.py` (mapearlo a una categoría de display existente).

### El script aborta con "Snapshot está en v1"
Correr `migrate-snapshot-mesaware.py` una sola vez. Idempotente.

### El bloque "REVISIÓN REQUERIDA" muestra demasiados cambios
Probable que Cecilia mandó el xlsx equivocado (ej. de otro mes) o un xlsx muy desactualizado. **NO seguir.** Preguntarle.

### El reporte productivo tira `_error: true` con códigos desconocidos
Los códigos en la Data Table están en una versión que no aparece en ningún mes del snapshot. Probables causas:
- Cecilia cambió radicalmente el nombre de los códigos sin avisar.
- Backfill de datos viejos (>6 meses) cuya clasificación fue prunneada del snapshot.

Solución temporal: ampliar `VENTANA_MESES_DEFAULT` en el script o usar `--force-mes` con un mes histórico para re-cargar.

### El reporte muestra `_warning_fallback` para muchas filas
Esperado en estos casos:
- Códigos retirados en el mes en curso pero presentes en data del mes anterior: `_warning_fallback: atras:<mes_anterior>`.
- Códigos nuevos del mes en curso aparecen retroactivamente en data del mes anterior: `_warning_fallback: adelante:<mes_actual>`.

No es error, solo info. Si la cantidad de fallbacks es muy alta (>10% de filas), revisar con Cecilia.

---

## Referencias

- Plan completo: `/Users/camilo/.claude/plans/en-base-al-ltimo-velvety-starlight.md`
- Cambios técnicos: `clients/SNR_Sonrisas/06_docs/cambios-flujo-facturacion-mesaware-2026-06-14.md`
- Postmortem original: `clients/SNR_Sonrisas/06_docs/incidente-periodoncia-mayo-2026-06-14.md`
- Cambios drift codigos (migración Data Tables anterior): `clients/SNR_Sonrisas/06_docs/cambios-flujo-facturacion-drift-codigos-2026-06-06.md`
