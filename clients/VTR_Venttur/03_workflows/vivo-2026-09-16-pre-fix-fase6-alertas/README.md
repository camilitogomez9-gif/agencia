# Snapshot pre-fix · Fase 6 alertas · 2026-09-16

Estado del `main-venttur` (`k3aivKSP67S97IHn`) inmediatamente **antes** del deploy de Fase 6. Sirve como rollback y como referencia del estado post-Fase 3 + pre-monitoreo.

## Estado

- nodos: 40 (post-Fase 3, sin los 3 nodos nuevos de Fase 6: IF, Telegram, Postgres INSERT)
- active: true
- Prompt v2.1 y guardrail ya aplicados (Fase 3 vigente en este snapshot)

Es idéntico a `vivo-2026-09-16-post-fix-prompt-guardrail/main-venttur.json` — el hash puede diferir por serialización, pero el shape estructural (40 nodos, mismas conexiones) es el mismo.

## Rollback

Para revertir Fase 6 preservando Fase 3, importar este JSON por API con
`PUT /api/v1/workflows/k3aivKSP67S97IHn` y luego borrar el workflow
`BzBCMGxEdJy6zmA9` (digest diario).

08e1c3da8387ffb14f5a593527093ff73d8001be5bfaf378b8bb5bb21b03c6ad  /Users/camilo/Downloads/camilo-workspace/clients/VTR_Venttur/03_workflows/vivo-2026-09-16-pre-fix-fase6-alertas/main-venttur.json

