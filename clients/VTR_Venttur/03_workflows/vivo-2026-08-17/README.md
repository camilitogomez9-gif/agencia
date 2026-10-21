# Export vivo — Venttur — 2026-08-17

Snapshot de los 14 workflows de Venttur tal como corren en `[TU-INSTANCIA-N8N]`, tomado por API
antes de aplicar las correcciones del **Reporte la agencia 1 (Agosto 2026)**.

**Es la fuente de verdad.** El repo estaba desactualizado: el main tenía 37 nodos en
`venttur-main-v1.json` y en vivo tiene 38; el dispatcher tenía 27 y en vivo tiene 30;
`actualizar-link-enviado` tenía 6 en `03_workflows/` y 7 en `00_migracion_ghl/00_inputs/` (esta
última era la correcta). **No parchear contra el repo viejo.**

Punto de rollback de todas las Olas del plan.

| workflow | id | active | nodos (sin sticky) | sha256[:16] | updatedAt |
|---|---|---|---|---|---|
| `main-venttur.json` | `k3aivKSP67S97IHn` | True | 35 | `df90ce053e84b495` | 2026-07-20T07:23:15 |
| `outreach-form-meta.json` | `CUuFxbst3iHpgeXS` | True | 37 | `39f922d365f0106a` | 2026-08-13T19:52:17 |
| `rescate-post-link.json` | `mkEP1qFN7MVb9qP0` | False | 23 | `d698fb5acb5bd94e` | 2026-07-23T06:54:02 |
| `confirmacion-agenda.json` | `2PSekVBxarsrnVBu` | True | 22 | `0f699a4c442e966a` | 2026-05-26T17:35:02 |
| `actualizar-link-enviado.json` | `gRSMjzxggA4UePjz` | False | 7 | `72bcad8c39c7eed9` | 2026-05-26T16:17:25 |
| `seguimiento-agenda.json` | `DZlSEQS5qzX1Y01K` | False | 5 | `8424c5e68eccdd84` | 2026-05-26T16:16:53 |
| `estado-lead-contesto.json` | `b52CUYEkI2Ah3Xj6` | False | 4 | `dab964dabe6cd585` | 2026-05-26T17:27:47 |
| `estado-interrumpida.json` | `H6qYB3Oj97bxaTCX` | True | 3 | `c06e5b8728191dd0` | 2026-05-26T17:35:30 |
| `resumen-etiquetas-seguimientos.json` | `DyrDumQgb6S4zHsS` | False | 27 | `3910b758e41e555b` | 2026-04-15T15:30:37 |
| `meta-capi.json` | `z98w2yWVEMOfifMl` | False | 19 | `b23c0192eaf8f398` | 2026-06-24T00:27:24 |
| `capi-registro-folio.json` | `9yCbynoKDt9hgiBq` | True | 5 | `e76bc2ed0fd2080d` | 2026-05-21T21:44:43 |
| `crear-contacto-clientify-airtable.json` | `cZUNKQyZNOHy5twQ` | False | 4 | `8e091e43c3b52087` | 2026-07-20T07:29:32 |
| `formulario-clientify.json` | `ZB6erhWicZmDfC4I` | True | 11 | `06ed56b14365a3d2` | 2026-06-07T00:56:07 |
| `primer-contacto-OUTDATED.json` | `gyMROURqhLlYtJJU` | False | 8 | `a10abdcadf5a4e3f` | 2026-04-15T15:31:01 |
