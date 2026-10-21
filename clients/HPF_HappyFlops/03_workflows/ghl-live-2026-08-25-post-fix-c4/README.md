# devn8n vivo — 2026-08-24, snapshot post-fix-C4 (convención satín→Mono aplicada)

Snapshot pre-cambios tomado después de aplicar fix C4 (convención satín→Mono explícita) (Pantuflas Normales Satín) y R6 (media
error humano + no-fatal en Telegram). Rollback base para esta sesión.

**Este es el estado real. Los generadores siguen estando atrás — no regenerar y deployar.**

| workflow | id | nodos | activo | sha256 |
|---|---|---:|---|---|
| W0 | `VK4M7VQm8CMefbty` | 9 | True | `47450bafe241` |
| W1 | `nA14dNwJ7VS3YMYr` | 59 | True | `a81b66108b5f` |
| W2 | `MdbOREN56lfQTYlM` | 21 | True | `95ec0fd6f65f` |
| W3 | `vSLHOawn2bFVXyOK` | 13 | True | `d55965b972f1` |
| W4 | `psGRDByGNjHQ2DVT` | 8 | True | `653c503433b5` |
| W5 | `mmo29FTvIquxksWV` | 10 | True | `fc17ff33caf5` |
| W6 | `cNmJCP2qVhdtfCH0` | 42 | True | `1b30cdea370b` |
| W7 | `m8KhaZV3nSjJ55ci` | 31 | True | `eb0b443caac0` |
| W8 | `Ki7IRFYQn1mqOh5p` | 15 | True | `b58d8d9d755f` |
| W9 | `2Govwp16YAcpgJ2C` | 4 | True | `c53abc3d83e9` |
| W10 | `fpKvo0ECWIhFcckE` | 22 | True | `6aa031c47bda` |
| W11 Puente Telegram (inactivo) | `aPZ71r7IVZTJ0iP5` | 13 | False | `fced9a6fe292` |
| HPF Inbound Handler (desactivado) | `IPO1c36NLzkXrBh9` | 71 | False | `bb4e58676833` |

Rollback: `hpf-deploy-workflow.py --restore <este_dir>/W1.json` (o el que corresponda).
Snapshot previo: `../ghl-live-2026-08-18-adjuntos-telegram/`.
