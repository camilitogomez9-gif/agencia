# Snapshot de devn8n vivo — 2026-08-14 (previo al ciclo de cierre)

Estado del que se parte: **prompts revertidos a `base-prod-2026-08-06`, parches de nodo del 12/8
vivos**. Es el punto de rollback de este ciclo.

| wf | id | nodos | activo | sha256 |
|---|---|---:|---|---|
| W0 | `VK4M7VQm8CMefbty` | 9 | True | `0a33b0bafb703064` |
| W1 | `nA14dNwJ7VS3YMYr` | 39 | True | `06e326388a49f79d` |
| W2 | `MdbOREN56lfQTYlM` | 12 | True | `c403cc0f356f5a6b` |
| W3 | `vSLHOawn2bFVXyOK` | 13 | True | `e650f3a3f315beff` |
| W4 | `psGRDByGNjHQ2DVT` | 8 | True | `e7acbbbc7d3b37c9` |
| W5 | `mmo29FTvIquxksWV` | 10 | True | `1c964ea99f1139f8` |
| W6 | `cNmJCP2qVhdtfCH0` | 41 | True | `fe09a5b8a09d196f` |
| W7 | `m8KhaZV3nSjJ55ci` | 31 | True | `04c4197b66db691e` |
| W8 | `Ki7IRFYQn1mqOh5p` | 15 | True | `5cf572d67cceefe9` |
| W9 | `2Govwp16YAcpgJ2C` | 4 | True | `e774fe4141dd77a0` |
| W10 | `fpKvo0ECWIhFcckE` | 22 | True | `b4afefda65d5ea1a` |

## Rollback

```bash
python3 scripts/utilities/hpf-deploy-workflow.py --restore clients/HPF_HappyFlops/03_workflows/ghl-live-2026-08-14/W6.json
```
