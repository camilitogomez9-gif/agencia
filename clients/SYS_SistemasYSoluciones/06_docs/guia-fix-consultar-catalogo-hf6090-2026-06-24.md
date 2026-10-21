# Guía de fix — `consultar_catalogo` no encuentra Cama Plana Huenú HF6090

**Fecha:** 2026-06-24
**Cliente:** SYS (Sistemas y Soluciones)
**Severidad:** P1 — bloquea campaña Meta activa
**Workflow target:** `sys-tool-consultar-catalogo` · workflowId `oQtLMujJBHlxZTTJ`

---

## 1. Contexto del incidente

**Reporte de Jipi (2026-06-24 11:45–16:38):**

> "Hola buen día les dejo una captura de un chat que vino de una campaña de la cama plana huenú y el agente no reconoce el producto … urge corregirlo pq la gente viene del aviso y el agente no les sabe dar información."

- Campaña Meta activa promocionando la **Cama Plana Huenú HF 6090**.
- Los leads escriben (literal): *"Hola! Quiero más información sobre la Cama Plana Huenú HF6090"*.
- El agente invoca correctamente `consultar_catalogo` pero el sub-workflow devuelve NOT_FOUND y responde *"No encontré información sobre la Cama Plana Huenú HF6090 en nuestro catálogo. Te gustaría que te derive a un representante comercial para obtener más detalles"*.
- El producto **SÍ existe en Airtable** `Equipos`, activo, vista "Para agente":

| Modelo | Marca | Tecnología | Formato | Ancho | Cabezales | Estado |
|---|---|---|---|---|---|---|
| HF 6090 | HUENU | UV | Cama Plana | 60*90 | 3× EPSON I3200U | Activo |

Cada lead que entra por la campaña paga queda mal atendido.

## 2. Diagnóstico

En la ejecución n8n el nodo `Airtable: Equipos` del sub-workflow devolvió `[ {} ]`. Causas confirmadas leyendo `03_workflows/sys-tool-consultar-catalogo-v2.json`:

1. **El `Classify Intent` no normaliza acentos.** `"Huenú".toLowerCase()` → `"huenú"`. El array `['huenu', 'dlican', …]` se busca con `q.includes('huenu')` → no matchea por la tilde. Resultado: `marca=""`.
2. **El JS solo extrae `marca` y `tecnologia`.** No reconoce `formato` (Cama Plana / Rollo a Rollo / Híbrido…) ni `modelo` (HF6090 / HR 1602 / DLI-1688).
3. **La query no contiene "UV" como palabra suelta** → `tecnologia=""`.
4. **Cae al fallback malo:** con `marca=""` y `tecnologia=""`, la fórmula final es
   ```
   AND(OR(SEARCH(LOWER("cama plana huenú hf6090"), LOWER({Modelo})),
          SEARCH(LOWER("cama plana huenú hf6090"), LOWER({Marca}))))
   ```
   busca el string completo en campos cortos (`"hf 6090"`, `"huenu"`) → 0 matches.
5. **Aún si extrajera modelo="HF6090", el campo Airtable es `"HF 6090"` con espacio** → SEARCH directo no matchea sin normalizar.

## 3. Solución implementada

**Fix quirúrgico**: 2 Code nodes + 3 expressions Airtable. Mantiene `workflowId` `oQtLMujJBHlxZTTJ`.

### Cambios concretos

| Nodo | Cambio |
|---|---|
| `Classify Intent` (`vld-001`) | Reemplazo completo del `jsCode`: normaliza acentos con `String.prototype.normalize('NFD')`, agrega extracción de `formato` y `modelo_hint` (regex), arma 3 fórmulas `filterByFormula` listas para downstream. |
| `Airtable: Equipos` (`atb-eqp`) | `filterByFormula` ahora lee `={{ '=' + $('Classify Intent').first().json.filterByFormula_equipos }}`. |
| `Airtable: Aplicaciones` (`atb-apl`) | Idem `filterByFormula_aplicaciones`. Tokeniza la query en lugar de buscar string completo. |
| `Airtable: Inventario Konica` (`atb-inv`) | Idem `filterByFormula_inventario`. Ya NO devuelve `TRUE()` por default (evita traer 21 records refurbished irrelevantes al LLM). |
| `Format Output` (`fmt-001`) | Agrega al output items: `formato`, `linea_producto`, `velocidad`, `cabezales_incluidos`, `cabezales_tipo`, `datos_extra`, `tipo_uso`. NO incluye Precio (política cliente). |

### Lógica nueva del builder de fórmulas (Equipos)

Orden de prioridad (primer match gana):

| # | Hints disponibles | filterByFormula generada |
|---|---|---|
| 1 | `modelo_hint` (+ marca si la hay) | `AND(FIND("HF6090", UPPER(SUBSTITUTE(SUBSTITUTE(SUBSTITUTE({Modelo}," ",""),"-",""),"/","")))>0, {Marca}="HUENU")` |
| 2 | `marca` + `tecnologia` | `AND({Marca}="HUENU", FIND("UV", ARRAYJOIN({Tecnología}))>0)` |
| 3 | `marca` + `formato` | `AND({Marca}="HUENU", {Formato}="Cama Plana")` |
| 4 | `formato` + `tecnologia` | `AND({Formato}="Cama Plana", FIND("UV", ARRAYJOIN({Tecnología}))>0)` |
| 5 | solo `marca` | `{Marca}="HUENU"` |
| 6 | solo `formato` | `{Formato}="Cama Plana"` |
| 7 | solo `tecnologia` | `FIND("UV", ARRAYJOIN({Tecnología}))>0` |
| 8 | fallback tokens | `OR(SEARCH("tok1", LOWER({Modelo})), SEARCH("tok1", LOWER({Marca})), SEARCH("tok1", LOWER({Formato})), …)` por token útil (3+ chars, máx 6) |

## 4. Deploy

### Opción A — Importar JSON v4 (recomendada · cero copy-paste)

El archivo `clients/SYS_SistemasYSoluciones/03_workflows/sys-tool-consultar-catalogo-v4.json` ya está en repo, **preserva el workflowId** `oQtLMujJBHlxZTTJ`, así que al importarlo en n8n **sobrescribe el workflow vivo in-place** sin necesidad de recablear al main.

1. En n8n UI abrir el workflow `consultar_catalogo` (workflowId `oQtLMujJBHlxZTTJ`).
2. Menú "…" → **Import from File** → seleccionar `sys-tool-consultar-catalogo-v4.json`.
3. n8n detecta el workflowId existente y pregunta overwrite → confirmar.
4. Verificar que el workflow quede `active: true` (n8n a veces lo apaga al importar).

### Opción B — Edición in-place node por node

Si preferís editar nodo por nodo en la UI:

#### Paso 1 — `Classify Intent`

Doble click en el node → reemplazar el `jsCode` completo por el contenido de `v4.json` campo `nodes[].parameters.jsCode` para `id=vld-001` (~180 líneas).

#### Paso 2 — `Airtable: Equipos`

Campo `filterByFormula`:
```
={{ '=' + $('Classify Intent').first().json.filterByFormula_equipos }}
```

#### Paso 3 — `Airtable: Aplicaciones`

Campo `filterByFormula`:
```
={{ '=' + $('Classify Intent').first().json.filterByFormula_aplicaciones }}
```

#### Paso 4 — `Airtable: Inventario Konica`

Campo `filterByFormula`:
```
={{ '=' + $('Classify Intent').first().json.filterByFormula_inventario }}
```

#### Paso 5 — `Format Output`

Doble click → reemplazar `jsCode` por el contenido de `v4.json` campo `nodes[].parameters.jsCode` para `id=fmt-001`.

## 5. Tests pin-data

Pinear input en `Execute Workflow Trigger` con cada query → execute step.

| # | Input `query` | intent esperado | marca | tec | formato | modelo_hint | Rows esperadas |
|---|---|---|---|---|---|---|---|
| **1** ⚠ | `Hola! Quiero más información sobre la Cama Plana Huenú HF6090` | equipo | HUENU | (vacío) | Cama Plana | HF6090 | **1 → HF 6090** |
| 2 | `HF 6090` | equipo | — | — | — | HF6090 | 1 → HF 6090 |
| 3 | `hf6090` | equipo | — | — | — | HF6090 | 1 → HF 6090 |
| 4 | `Huenú UV` | equipo | HUENU | UV | — | — | varios HUENU UV |
| 5 | `Cama plana` | equipo | — | — | Cama Plana | — | varios Cama Plana |
| 6 | `Plotter de corte 130cm` | equipo | — | Corte | Plotter | — | TN48CCD u otros |
| 7 | `DTF Textil HUENU 60cm` | equipo | HUENU | DTF Textil | — | — | varios HUENU DTF |
| 8 | `BIZHUB usado` | inventario | Konica Minolta | — | — | — | refurbished |
| 9 | `Estampar gorras` | aplicacion | — | — | — | — | "Estampado de gorras" |
| 10 | `Sinajet DG 2516` | equipo | Sinajet | — | — | DG2516 | 1 Sinajet |
| 11 | `necesito imprimir banderas` | aplicacion | — | — | — | — | banderas |
| 12 | `DLI-1688` | equipo | — | — | — | DLI1688 | 1 DLICAN |

**Criterio de éxito:** Test 1 pasa de NOT_FOUND a RESOLVED con `data.items[0].modelo === "HF 6090"`, sin campo `precio` en el output.

Tests 1–12 ya fueron simulados localmente con node — los hints extraídos y `filterByFormula` generadas son las esperadas. La validación final es contra Airtable vivo.

## 6. Smoke E2E contra webhook live

Una vez deployado:

1. Enviar al webhook del main agente (o por WhatsApp test) el mensaje literal:
   ```
   Hola! Quiero más información sobre la Cama Plana Huenú HF6090
   ```
2. Verificar:
   - **Logs n8n del main**: nodo `consultar_catalogo` (toolWorkflow) invocado con `query` conteniendo "HF6090".
   - **Postgres `sys_tool_calls`** (cred `Supabase SYS` id `cQLxF5deDtmo4HTV`):
     ```sql
     SELECT input_payload->>'query' AS query,
            output_payload->>'status' AS status,
            output_payload->'data'->>'total' AS total,
            output_payload->'data'->'items'->0->>'modelo' AS modelo,
            output_payload->'data'->'items'->0->>'formato' AS formato,
            output_payload->'data'->'items'->0->>'marca' AS marca
     FROM sys_tool_calls
     WHERE tool_name='consultar-catalogo'
     ORDER BY created_at DESC LIMIT 1;
     ```
     Esperado: `status='RESOLVED', total=1, modelo='HF 6090', formato='Cama Plana', marca='HUENU'`.
   - **Respuesta del agente al lead**: menciona HF 6090, formato Cama Plana, tecnología UV, cabezales (EPSON I3200U), ancho 60×90 cm. **NO menciona precio**. Cierra con propuesta de derivar a comercial para cotización.

## 7. Monitoreo (24–48 hs post-deploy)

Ratio NOT_FOUND/RESOLVED de la tool:

```sql
SELECT date_trunc('hour', created_at) AS hr,
       output_payload->>'status' AS status,
       count(*) AS n
FROM sys_tool_calls
WHERE tool_name='consultar-catalogo'
  AND created_at > now() - interval '48 hours'
GROUP BY 1, 2 ORDER BY 1 DESC;
```

Si el ratio NOT_FOUND sigue alto, revisar las queries que cayeron:

```sql
SELECT input_payload->>'query' AS query,
       output_payload->>'message_to_agent' AS msg
FROM sys_tool_calls
WHERE tool_name='consultar-catalogo'
  AND output_payload->>'status'='NOT_FOUND'
  AND created_at > now() - interval '24 hours'
ORDER BY created_at DESC;
```

El `message_to_agent` ahora incluye los hints extraídos (`intent`, `marca`, `formato`, `tec`, `modelo_hint`) → permite diagnosticar por qué cayó a NOT_FOUND sin re-ejecutar.

## 8. Rollback

Si algo rompe post-deploy:

1. En n8n UI abrir `consultar_catalogo` (`oQtLMujJBHlxZTTJ`).
2. Menú "…" → Import from File → `sys-tool-consultar-catalogo-v2.json`.
3. Confirmar overwrite. Activar si quedó inactivo.

Tiempo objetivo: <5 min. El v2 está versionado en repo.

## 9. Riesgos conocidos (no bloqueantes, follow-up)

- **Falso positivo `modelo_hint`** con nombres de cabezales: si un lead pregunta *"necesito el cabezal I3200"*, el regex captura `modelo_hint=I3200` y busca un equipo con ese modelo. Hoy retorna NOT_FOUND (no hay equipo modelo I3200). Follow-up: blacklist de tokens de cabezales (`I3200`, `I1600`, `XP600`, `TX800`) en el JS.
- **Modelos con patrón letra-dígito-letra-guion-dígitos** (ej: `X4E-7703` de XENONS): la regex actual `[A-Z]{1,4}\d{2,5}` requiere letra-luego-dígito, no captura este patrón. Hoy en la base hay 1 solo modelo así. Follow-up: ampliar regex a `[A-Z][A-Z0-9]{0,3}` si Jipi reporta el caso.
- **`consultar_catalogo` no está documentada en el system prompt v2.3** (sección HERRAMIENTAS solo documenta las 9 tools viejas + `registrar_datos_lead`). Follow-up v2.4: documentarla para que el LLM tenga guidance explícito sobre qué query pasar (mensaje literal del lead — el sub-workflow normaliza internamente) y qué hacer con cada `status`.
- **`ARRAYJOIN({Tecnología})`**: el campo Tecnología es linked record. Si ARRAYJOIN devuelve recIDs en lugar de los nombres legibles, los filtros por tec fallarían silenciosamente. Verificar al primer test 4 ("Huenú UV") que devuelva equipos. Si falla, agregar lookup field "Tecnología (texto)" o usar `{Tecnología} & ""` con join nativo.

## 10. Archivos relacionados

- `clients/SYS_SistemasYSoluciones/03_workflows/sys-tool-consultar-catalogo-v4.json` — workflow nuevo importable.
- `clients/SYS_SistemasYSoluciones/03_workflows/sys-tool-consultar-catalogo-v2.json` — versión anterior (rollback).
- `clients/SYS_SistemasYSoluciones/05_crm/airtable-syscatalogo-schema.md` — schema canónico.
- `clients/SYS_SistemasYSoluciones/06_docs/incidente-bug-zod-langchain-2026-06-03.md` — postmortem del refactor nuclear que originó esta arquitectura.
- `/Users/camilo/.claude/plans/users-la agencia-downloads-equipos-grid-view-transient-llama.md` — plan aprobado de este fix.
