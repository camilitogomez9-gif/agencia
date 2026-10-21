# devn8n vivo — 2026-08-24, snapshot pre-cambios (R9 + R6)

Snapshot pre-cambios tomado antes de aplicar R9 (Pantuflas Normales Satín) y R6 (media
error humano + no-fatal en Telegram). Rollback base para esta sesión.

**Este es el estado real. Los generadores siguen estando atrás — no regenerar y deployar.**

| workflow | id | nodos | activo | sha256 |
|---|---|---:|---|---|
| W0 | `VK4M7VQm8CMefbty` | 9 | True | `4dbfcc31cff6` |
| W1 | `nA14dNwJ7VS3YMYr` | 59 | True | `b22edbd555f2` |
| W2 | `MdbOREN56lfQTYlM` | 21 | True | `34288594b3f2` |
| W3 | `vSLHOawn2bFVXyOK` | 13 | True | `016e0ebee309` |
| W4 | `psGRDByGNjHQ2DVT` | 8 | True | `6b511e07ac43` |
| W5 | `mmo29FTvIquxksWV` | 10 | True | `317ea80480a4` |
| W6 | `cNmJCP2qVhdtfCH0` | 42 | True | `1efd7de99f82` |
| W7 | `m8KhaZV3nSjJ55ci` | 31 | True | `0484118e0046` |
| W8 | `Ki7IRFYQn1mqOh5p` | 15 | True | `b1e6559ef7a3` |
| W9 | `2Govwp16YAcpgJ2C` | 4 | True | `c8fe1f0b6922` |
| W10 | `fpKvo0ECWIhFcckE` | 22 | True | `f0104b456250` |
| W11 Puente Telegram (inactivo) | `aPZ71r7IVZTJ0iP5` | 13 | False | `eb1ffbe63d41` |
| HPF Inbound Handler (desactivado) | `IPO1c36NLzkXrBh9` | 71 | False | `677c6e3e6b08` |

Rollback: `hpf-deploy-workflow.py --restore <este_dir>/W1.json` (o el que corresponda).
Snapshot previo: `../ghl-live-2026-08-18-adjuntos-telegram/`.
