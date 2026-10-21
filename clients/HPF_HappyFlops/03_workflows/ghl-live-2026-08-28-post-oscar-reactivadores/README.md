# devn8n vivo — 2026-08-28, snapshot post reunión Oscar + reactivadores R1

Estado del vivo tras aplicar los 10 puntos de la reunión con Oscar (P1-P10: fuera de horario, vocabulario mexicano, colores no-producto, imagen COLORES DE CORREAS, upsell, precios, fichas Otros, datos de pago determinístico, Mono→Moño) **y** el sistema de reactivadores R1 (W10 tag→etapa R1 SIN/CON, W0 STAGES +3 etapas, W5 → R1 AP condicional). Las etapas R2 se borraron del pipeline GHL (muertas). **Rollback base para la próxima sesión.**

**Este es el estado real. Los generadores siguen atrás — no regenerar y deployar.**

| workflow | id | nodos | activo | sha256 |
|---|---|---:|---|---|
| W0 | `VK4M7VQm8CMefbty` | 9 | True | `33d7b604d64b` |
| W1 | `nA14dNwJ7VS3YMYr` | 59 | True | `6f4e617ce609` |
| W2 | `MdbOREN56lfQTYlM` | 22 | True | `58d47d5dfdce` |
| W3 | `vSLHOawn2bFVXyOK` | 13 | True | `6b4072b95e09` |
| W4 | `psGRDByGNjHQ2DVT` | 8 | True | `46ad53779955` |
| W5 | `mmo29FTvIquxksWV` | 11 | True | `cb7f9eb4762b` |
| W6 | `cNmJCP2qVhdtfCH0` | 42 | True | `6c6571b6501b` |
| W7 | `m8KhaZV3nSjJ55ci` | 31 | True | `0ac420e12c68` |
| W8 | `Ki7IRFYQn1mqOh5p` | 15 | True | `28fa38188fff` |
| W9 | `2Govwp16YAcpgJ2C` | 4 | True | `cce57531ee20` |
| W10 | `fpKvo0ECWIhFcckE` | 22 | True | `e91ab2619834` |
| W11 Puente Telegram (inactivo) | `aPZ71r7IVZTJ0iP5` | 13 | False | `54f17d3c34f5` |
| HPF Inbound Handler (desactivado) | `IPO1c36NLzkXrBh9` | 71 | False | `7b1adc37aedc` |

Rollback: `hpf-deploy-workflow.py --restore <este_dir>/W1.json` (o el que corresponda).
Snapshot previo: `../ghl-live-2026-08-27-pre-fixes-oscar/` (antes de los cambios de hoy).
