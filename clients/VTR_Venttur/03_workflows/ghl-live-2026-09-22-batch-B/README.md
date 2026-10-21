# Batch B · Infra Supabase · 2026-09-22

Aplicado por Codex el 2026-09-22 03:40 UTC.

## B1 · Tablas Supabase creadas (idempotente `IF NOT EXISTS`)

### `vtr_message_dedup`

Idempotencia por hash `sha256(contact_id + date_created + body)` para el main-venttur-ghl. Evita procesar mensajes duplicados si GHL reintenta el webhook.

```sql
CREATE TABLE IF NOT EXISTS vtr_message_dedup (
  hash text PRIMARY KEY,
  contact_id text NOT NULL,
  date_created timestamptz NOT NULL,
  body text NOT NULL,
  first_seen_at timestamptz NOT NULL DEFAULT now()
);
```

Count post-creación: 0 rows (empty, esperada carga en tiempo real post-cutover).

### `vtr_message_buffer`

Reemplaza el buffer de ManyChat (+20s de debounce). Preparada para el flow buffer→flush del main-venttur-ghl (implementación en batch posterior).

```sql
CREATE TABLE IF NOT EXISTS vtr_message_buffer (
  contact_id text PRIMARY KEY,
  messages jsonb NOT NULL DEFAULT '[]'::jsonb,
  first_message_at timestamptz,
  last_message_at timestamptz,
  flushed_at timestamptz
);
```

Count post-creación: 0 rows.

## B2 · Migración folios Airtable → Supabase `capi_folios`

Idempotente vía `ON CONFLICT (folio) DO UPDATE SET ...`.

**Resultados:**

| Métrica | Valor |
|---|---|
| Airtable Folios CAPI | 4.006 rows |
| Con folio no vacío | 4.003 rows |
| Skipped (folio null) | 3 rows |
| Supabase capi_folios post-migración | **3.725 rows únicos** |
| Delta (`with_folio - supabase_count_after`) | 278 duplicados de folio en Airtable, consolidados por ON CONFLICT |

**Verificación cruzada:**

```
SELECT (SELECT COUNT(*) FROM capi_folios) AS total,
       (SELECT COUNT(DISTINCT folio) FROM capi_folios) AS uniq,
       (SELECT COUNT(*) FROM capi_folios WHERE folio IS NULL OR folio = '') AS null_folio;
```

→ `{total: 3725, uniq: 3725, null_folio: 0}` ✓

**Fixes durante ejecución (documentados para reproducibilidad):**

1. Airtable devuelve `Timestamp` como **bigint (Unix epoch ms)**, no ISO string. Fix aplicado en `queryReplacement`: `($json.Timestamp != null ? new Date($json.Timestamp).toISOString() : null)`. Query INSERT sin `::timestamptz` explícito (Postgres castea el string ISO nativamente).
2. Algunos rows Airtable tienen `Folio` null/vacío (3 rows). Agregado nodo `Has folio?` (IF filter) que descarta esos rows antes del INSERT (evita violación de `NOT NULL` constraint sobre `folio`).

## Workflows ejecutados (dejados OFF post-run)

| Workflow | ID | Estado | Snapshot |
|---|---|---|---|
| VTR Batch B1 · Setup Supabase Tables | `twjXKbt92hlFD85g` | OFF | `b1-setup-tables.json` sha `90a2e41dea8b7833a2d2c14fda1d32c23c9a4605601df19ba017fb5529f1a078` |
| VTR Batch B2 · Migrar folios | `FoDzrFAEynflWjeG` | OFF | `b2-migrate-folios.json` sha `9c9327c2e521506ee6a99fcc92760ee68b93b25506282f98c4d48fbcb9800906` |

Ambos son one-shot. Si se necesitan re-ejecutar, activar + POST al webhook (URL en el JSON).

## Log

`clients/VTR_Venttur/05_ejecucion/logs/batch-b-supabase-2026-09-22.md`

## Scripts fuente

- `scratchpad/vtr_batch_b.py` — B1 + B2 initial
- `scratchpad/vtr_batch_b_fix.py` — Fix Timestamp bigint→ISO
- `scratchpad/vtr_batch_b_fix2.py` — Fix IF filter para folios null
- `scratchpad/vtr_batch_b_verify.py` — verificación COUNT DISTINCT
