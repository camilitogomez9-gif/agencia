# Snapshot de devn8n vivo — 2026-08-12

Export por API de los 11 workflows `HPF·GHL` antes de aplicar los cambios pedidos por Oscar
en la reunión del 2026-08-11. Es el punto de rollback.

**Por qué existe:** los generadores `scripts/generators/hpf-gen-w*.py` quedaron atrás del vivo.
Regenerar y deployar BORRARÍA nodos que solo existen en producción (14 en W1, 9 en W6), y W7/W8/W9/W10
no están en el repo en absoluto. Cualquier cambio se aplica como edición dirigida de nodos sobre el
vivo, no regenerando.

| wf | id | nodos | activo | sha256 |
|---|---|---|---|---|
| W0 | `VK4M7VQm8CMefbty` | 9 | True | `1c754cbc3592a5a4` |
| W1 | `nA14dNwJ7VS3YMYr` | 39 | True | `bb255fa6c2de5a85` |
| W2 | `MdbOREN56lfQTYlM` | 12 | True | `9477a175887e37ed` |
| W3 | `vSLHOawn2bFVXyOK` | 13 | True | `654861123d98c68d` |
| W4 | `psGRDByGNjHQ2DVT` | 8 | True | `56ee76ccd26aed19` |
| W5 | `mmo29FTvIquxksWV` | 10 | True | `789b42934dd3fd30` |
| W6 | `cNmJCP2qVhdtfCH0` | 39 | True | `c777af6ae608739a` |
| W7 | `m8KhaZV3nSjJ55ci` | 31 | True | `729275d36188b56b` |
| W8 | `Ki7IRFYQn1mqOh5p` | 15 | True | `ecea36cb05ea8eb0` |
| W9 | `2Govwp16YAcpgJ2C` | 4 | True | `1cbe929404b8ec02` |
| W10 | `fpKvo0ECWIhFcckE` | 22 | True | `4088af180e34b0f7` |

## Rollback

```bash
# restaurar un workflow al estado de este snapshot
python3 scripts/utilities/hpf-deploy-workflow.py --restore clients/HPF_HappyFlops/03_workflows/ghl-live-2026-08-12/W6.json
```
