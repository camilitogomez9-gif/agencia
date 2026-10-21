# devn8n vivo — 2026-08-24, snapshot post-fix cobertura pantuflas (peluche video + satín catálogo)

Snapshot pre-cambios tomado después del fix cobertura pantuflas (peluche→video, satín/normal→catálogo) (Pantuflas Normales Satín) y R6 (media
error humano + no-fatal en Telegram). Rollback base para esta sesión.

**Este es el estado real. Los generadores siguen estando atrás — no regenerar y deployar.**

| workflow | id | nodos | activo | sha256 |
|---|---|---:|---|---|
| W0 | `VK4M7VQm8CMefbty` | 9 | True | `f7c19e97b93b` |
| W1 | `nA14dNwJ7VS3YMYr` | 59 | True | `b10298feae20` |
| W2 | `MdbOREN56lfQTYlM` | 21 | True | `9051c1f13e5d` |
| W3 | `vSLHOawn2bFVXyOK` | 13 | True | `e8f89670426b` |
| W4 | `psGRDByGNjHQ2DVT` | 8 | True | `1941c29473b6` |
| W5 | `mmo29FTvIquxksWV` | 10 | True | `69a3898e88bd` |
| W6 | `cNmJCP2qVhdtfCH0` | 42 | True | `a9271b7fe92e` |
| W7 | `m8KhaZV3nSjJ55ci` | 31 | True | `bd1d925bd80a` |
| W8 | `Ki7IRFYQn1mqOh5p` | 15 | True | `a9d3c53e79b4` |
| W9 | `2Govwp16YAcpgJ2C` | 4 | True | `8961dcd78e2b` |
| W10 | `fpKvo0ECWIhFcckE` | 22 | True | `74e7358801c0` |
| W11 Puente Telegram (inactivo) | `aPZ71r7IVZTJ0iP5` | 13 | False | `2ae2a46ec99d` |
| HPF Inbound Handler (desactivado) | `IPO1c36NLzkXrBh9` | 71 | False | `8b8924a459e7` |

Rollback: `hpf-deploy-workflow.py --restore <este_dir>/W1.json` (o el que corresponda).
Snapshot previo: `../ghl-live-2026-08-18-adjuntos-telegram/`.
