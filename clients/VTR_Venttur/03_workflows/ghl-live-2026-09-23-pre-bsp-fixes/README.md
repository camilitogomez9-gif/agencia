# Parches pre-BSP · 2026-09-23 tarde

Script: `00_migracion_ghl/05_ejecucion/scripts/batches-2026-09-23/vtr_pre_bsp_fixes.py` (idempotente, marca
`PRE-BSP-0923`; sin `--execute` es dry-run). Detalle de cada cambio y motivo: guía raíz, sección **A11**.

- `pre/` — los 7 workflows tal como estaban antes del parche (rollback: PUT de ese JSON).
- `post/` — cómo quedaron.
- `sha256.txt` — hashes pre/post.

Todos quedaron **OFF** (ninguno estaba prendido). Pendiente: prueba E2E del main (guía, A12).
