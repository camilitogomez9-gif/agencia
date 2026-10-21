# devn8n vivo — 2026-08-18, con adjuntos de Telegram cableados

W1 pasa de 52 a **59 nodos**: el carril de prueba de Telegram ahora canjea el `file_id`
por una URL pública (baja el binario y lo sube a la Media Library de GHL), así que
fotos, notas de voz, PDFs y documentos llegan a W7 y a la rama de audio. Sin esto, seis
familias de la matriz de paridad sólo existían del lado del bot viejo.

**Este es el estado real. Los generadores siguen estando atrás — no regenerar y deployar.**

| workflow | id | nodos | activo | sha256 |
|---|---|---:|---|---|
| W0 | `VK4M7VQm8CMefbty` | 9 | True | `576f7b107bfe` |
| W1 | `nA14dNwJ7VS3YMYr` | 59 | True | `f3ce508a538a` |
| W2 | `MdbOREN56lfQTYlM` | 21 | True | `de8f20d415d7` |
| W3 | `vSLHOawn2bFVXyOK` | 13 | True | `291e10aad018` |
| W4 | `psGRDByGNjHQ2DVT` | 8 | True | `2467f638f424` |
| W5 | `mmo29FTvIquxksWV` | 10 | True | `63f758b37ff9` |
| W6 | `cNmJCP2qVhdtfCH0` | 41 | True | `57ae96669245` |
| W7 | `m8KhaZV3nSjJ55ci` | 31 | True | `dffe7bda088d` |
| W8 | `Ki7IRFYQn1mqOh5p` | 15 | True | `e80b9817317c` |
| W9 | `2Govwp16YAcpgJ2C` | 4 | True | `0690fe43a967` |
| W10 | `fpKvo0ECWIhFcckE` | 22 | True | `4a89f9d2f5f9` |
| W11 Puente Telegram (inactivo) | `aPZ71r7IVZTJ0iP5` | 13 | False | `1ea72384d668` |
| HPF Inbound Handler (desactivado) | `IPO1c36NLzkXrBh9` | 71 | False | `d0575d4485b1` |

Rollback: `hpf-deploy-workflow.py --restore <este_dir>/W1.json`
Snapshot previo (52 nodos, sin adjuntos): `../ghl-live-2026-08-17-post-paridad/`.
