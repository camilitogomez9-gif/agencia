# devn8n vivo — 2026-08-27, snapshot pre-fixes reunión Oscar

Rollback base antes de aplicar las correcciones de la reunión de Oscar (P1-P10).
Estado real del vivo hoy (divergió incluso del 08-26). Tomado con GET, sin modificar nada.

| workflow | id | nodos | activo | sha256 |
|---|---|---:|---|---|
| W0 | `VK4M7VQm8CMefbty` | 9 | True | `03373ff36472` |
| W1 | `nA14dNwJ7VS3YMYr` | 59 | True | `bfa429df6bfc` |
| W2 | `MdbOREN56lfQTYlM` | 22 | True | `4696b4c0555e` |
| W3 | `vSLHOawn2bFVXyOK` | 13 | True | `eef3d057196f` |
| W4 | `psGRDByGNjHQ2DVT` | 8 | True | `16f6514cb590` |
| W5 | `mmo29FTvIquxksWV` | 10 | True | `60269d967ae8` |
| W6 | `cNmJCP2qVhdtfCH0` | 42 | True | `f4d0411f8076` |
| W7 | `m8KhaZV3nSjJ55ci` | 31 | True | `933cf90f0741` |
| W8 | `Ki7IRFYQn1mqOh5p` | 15 | True | `55241adedba3` |
| W9 | `2Govwp16YAcpgJ2C` | 4 | True | `48d5321bcceb` |
| W10 | `fpKvo0ECWIhFcckE` | 22 | True | `87ca800ceffe` |
| W11 Puente Telegram (inactivo) | `aPZ71r7IVZTJ0iP5` | 13 | False | `93906bbd11b9` |
| HPF Inbound Handler (desactivado) | `IPO1c36NLzkXrBh9` | 71 | False | `55b564beecdf` |

Rollback: `hpf-deploy-workflow.py --restore <este_dir>/W1.json` (o el que corresponda).
Snapshot previo: `../ghl-live-2026-08-26-cobertura-pantuflas/`.
