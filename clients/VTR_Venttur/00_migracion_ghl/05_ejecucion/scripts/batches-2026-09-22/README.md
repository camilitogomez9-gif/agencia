# Scripts de batches VTR — sesión 2026-09-22

Scripts Python idempotentes usados para aplicar los batches A/B/C.1/D/F del cutover. Todos usan el patrón:

- Lectura de `.env` con `grep|cut` (NUNCA `source .env` — expone secrets si hay valores con caracteres especiales sin escapar).
- API n8n vía `curl` con header `X-N8N-API-KEY` (nunca imprime el key).
- Snapshots pre/post con sha256 en `clients/VTR_Venttur/03_workflows/ghl-live-2026-09-22-batch-<letra>/`.

## Índice

| Script | Batch | Qué hace |
|---|---|---|
| `vtr_batch_a.py` | A | Rota OpenAI cred + fix `Hay audios?` regex en `k3aivKSP67S97IHn` |
| `vtr_batch_b.py` | B (initial) | Crea `vtr_message_dedup` + `vtr_message_buffer` + migra folios Airtable → `capi_folios` |
| `vtr_batch_b_fix.py` | B (fix 1) | Cast Timestamp bigint → ISO en migración |
| `vtr_batch_b_fix2.py` | B (fix 2) | IF filter para descartar folios null |
| `vtr_batch_b_verify.py` | B (verify) | COUNT(*) + COUNT(DISTINCT folio) post-migración |
| `vtr_batch_c_main.py` | C.1 | Construye `main-venttur-ghl` v0.1 (id `1eS1Z5k898c3ATnf`) |
| `vtr_batch_c_elevar.py` | C.1 | Construye sub-workflow `vtr-tool-elevar-ghl` (id `v9XkOfL9dQtY2wyv`) + linkea al main |
| `vtr_batch_f_investigate.py` | F.2 (recon) | Descarga rescate + despachador + staging para inspeccionar sessionKey |
| `vtr_batch_f_sessionkey.py` | F.2 | Reconcilia sessionKey `+`/sin-`+` en rescate y despachador |
| `vtr_batch_f1.py` | F.1 | Cablea mapping programa → templateId en despachador |
| `vtr_f1_hapy_year_confirmed.py` | F.1 (fix) | Actualiza comment "Hapy Year" a "confirmado Gap Year" |

## Cómo re-correr uno

Todos son idempotentes. Ejemplo:

```bash
cd /Users/camilo/Downloads/camilo-workspace
python3 clients/VTR_Venttur/00_migracion_ghl/05_ejecucion/scripts/batches-2026-09-22/vtr_batch_a.py
```

Los que crean workflows (Batch C, B one-shot) devuelven nuevos IDs cada corrida — verificar que no queden duplicados en n8n si se re-corren.

Los que patchean workflows existentes (A, F.1, F.2) son safe re-correr — detectan si el patch ya está aplicado.

## Orden histórico de ejecución

1. `vtr_batch_a.py` — 2026-09-22 03:34 UTC
2. `vtr_batch_b.py` → `vtr_batch_b_fix.py` (Timestamp bigint) → `vtr_batch_b_fix2.py` (IF folio null) → `vtr_batch_b_verify.py` (chequeo counts) — 2026-09-22 03:36-03:45 UTC
3. `vtr_batch_c_main.py` → `vtr_batch_c_elevar.py` — 2026-09-22 03:50 UTC
4. `vtr_batch_f_investigate.py` → `vtr_batch_f_sessionkey.py` — 2026-09-22 04:00 UTC
5. `vtr_batch_f1.py` → `vtr_f1_hapy_year_confirmed.py` — 2026-09-22 04:20 UTC
