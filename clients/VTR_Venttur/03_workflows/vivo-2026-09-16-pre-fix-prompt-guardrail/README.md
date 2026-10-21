# Snapshot pre-fix · 2026-09-16 14:49 UTC (Fase 3 del plan Nahe)

Estado del `main-venttur` (`k3aivKSP67S97IHn`) **inmediatamente antes** de aplicar el fix del incidente Nahe. Sirve como rollback y evidencia del estado que causó el bug.

## Estado

- nodos: 39
- active: true
- updatedAt: 2026-09-15T10:16:44Z (nótese: workflow fue tocado el 15/9 antes de que Max reportara el caso)
- versionId anterior al fix (registrado en el PUT del post-fix)

Idéntico en shape al snapshot `vivo-2026-09-15-pre-fix-nahe/` — sha256 del `main-venttur.json` **puede diferir** si n8n serializa de forma no-canónica entre dos GETs consecutivos, pero el contenido del prompt y las conexiones son las mismas del 2026-09-15.

## Bug que este snapshot exhibe

`options.systemMessage` del nodo `Agente IA WPP` contiene el prompt v2.0 con dos instrucciones catastróficas cuando `[ESTADO DEL LEAD] = Link YA ENVIADO`:

1. Bloque `[ESTADO DEL LEAD]`, línea ~24: *"ofrecé coordinar el horario a mano"*.
2. Sección `Ya le mandaste el link y no agendó`, líneas ~656-661: *"dime qué día te viene bien y **lo coordino contigo directo**"*.

El agente no tiene tool de calendar. Estas instrucciones lo llevan a alucinar citas — es el mecanismo del incidente Nahe (`06_docs/incidente-nahe-2026-09-15.md`).

## Rollback

Si el fix del post-fix genera regresión: importar este JSON por API con `PUT /api/v1/workflows/k3aivKSP67S97IHn` (payload = `{name, nodes, connections, settings}`).

## Post-fix

Ver `vivo-2026-09-16-post-fix-prompt-guardrail/` — 40 nodos, prompt v2.1 aplicado, guardrail estructural intercalado.
04718659208a611d346faf4ef384550e7d88d8a235196250f9d3a814e2d448d0  /Users/camilo/Downloads/camilo-workspace/clients/VTR_Venttur/03_workflows/vivo-2026-09-16-pre-fix-prompt-guardrail/main-venttur.json

