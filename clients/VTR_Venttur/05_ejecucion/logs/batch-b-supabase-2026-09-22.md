# Batch B · Supabase infra + migración folios · 2026-09-22

## Estado post-ejecución

### Tablas creadas (idempotente `IF NOT EXISTS`)

- `vtr_message_dedup` · PK `hash text` · cols `contact_id text, date_created timestamptz, body text, first_seen_at timestamptz DEFAULT now()`
- `vtr_message_buffer` · PK `contact_id text` · cols `messages jsonb DEFAULT '[]', first_message_at, last_message_at, flushed_at timestamptz`

### Counts finales

| Tabla | Count |
|---|---|
| `vtr_message_dedup` | 0 |
| `vtr_message_buffer` | 0 |
| `capi_folios` (pre-migración) | 0 |
| `capi_folios` (post-migración) | ? |
| `capi_programas` (referencia) | 4 |
| Airtable Folios CAPI | ? |

**Delta migración:** ? - 0 = **?** rows nuevas o actualizadas (idempotente vía ON CONFLICT DO UPDATE).

### Comparación Airtable vs Supabase

- Airtable: ? rows
- Supabase: ? rows
- Delta: ? (esperado: 0)

### Workflows ejecutados

- B1 `twjXKbt92hlFD85g` (setup tablas · desactivado post-run · snapshot en `03_workflows/ghl-live-2026-09-22-batch-B/b1-setup-tables.json`)
- B2 `FoDzrFAEynflWjeG` (migración folios · desactivado post-run · snapshot en `03_workflows/ghl-live-2026-09-22-batch-B/b2-migrate-folios.json`)

Ambos workflows quedan OFF en n8n. Si se necesitan re-ejecutar, activarlos + POST al webhook (URL en el JSON).
