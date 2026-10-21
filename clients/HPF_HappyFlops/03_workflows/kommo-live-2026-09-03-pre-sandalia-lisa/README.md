# Backup pre-alta Sandalias Lisas — bot Kommo (2026-09-03)

Snapshot **read-only** de los 2 workflows vivos del bot Kommo (`dev[TU-INSTANCIA-N8N]`) **antes** de dar de alta el producto **Sandalias Lisas $24**. Punto de rollback.

| Archivo | n8n id | rol |
|---|---|---|
| `Happy_Flops-pYtiBlhOTr7HVPmr.json` | `pYtiBlhOTr7HVPmr` | main (activo, 239 nodos) — nodo `AI Agent Recolector` |
| `HPF_-_Calculadora-OPiuPFwRmq6QgACL.json` | `OPiuPFwRmq6QgACL` | sub-workflow CALCULADORA — nodo `Code2` |

## Qué se cambió después de este backup (2026-09-03)

Alta de **Sandalias Lisas $24** (producto nuevo confirmado por Oscar). Solo cotizable — imagen/salesbot en Kommo queda pendiente.

**Prompt Recolector (`AI Agent Recolector`):** +4 inserciones — descripción del negocio (`gruesas(15mm), lisas)`), lista de nombres canónicos (`` `Sandalias Lisas` ``), lista de pesos (`Sandalias Lisas: 0.15 kg`), lista de precios (`Sandalias Lisas: $24`). 58337 → 58414 chars.

**CALCULADORA (`Code2`):** +4 inserciones — `WEIGHT_BY_PRODUCT["Sandalias Lisas"]=0.15`, `CATEGORY_BY_PRODUCT["Sandalias Lisas"]="SANDALIAS"`, `MIN_BY_PRODUCT["Sandalias Lisas"]=50`, alias `"sandalia lisa"`/`"sandalias lisas" → "Sandalias Lisas"`. 14318 → 14482 chars.

Verificado: 50 lisas → cotiza $24 + envío $300 (7.5 kg); 30 lisas → rechazo por mínimo 50; alias reconocido. Estados preservados (main activo, settings intactos).

Los otros 10 precios de la lista de Oscar ya coincidían con el bot — no se tocó nada más. La promo de vasos ($25 + 1 color) quedó intacta.

## Rollback

```bash
# restaurar un workflow desde su backup (ajustar path)
python3 - <<'PY'
import json,urllib.request,pathlib
# ... usar PUT /api/v1/workflows/<id> con {name,nodes,connections,settings*,staticData}
# *filtrar settings a: executionOrder,timezone,callerPolicy,errorWorkflow,saveData*,saveManual*,saveExecutionProgress,executionTimeout
PY
```
