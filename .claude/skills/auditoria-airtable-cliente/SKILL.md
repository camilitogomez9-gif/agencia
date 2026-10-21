---
name: auditoria-airtable-cliente
description: >
  Usar este skill cuando hay que auditar exhaustivamente la base Airtable de un
  cliente antes de una reunión, tras un reporte de bug de linkeo/data, o como
  chequeo periódico de salud. Se activa con frases como "auditar el Airtable de X",
  "el cliente reportó que el linkeo está roto", "necesito preparar una reunión
  sobre la base de datos", "revisar inconsistencias del Airtable antes de hablar
  con el cliente", "detectar drift entre el schema documentado y la base real".
  Requiere ultracode (workflow multi-agente) — pedirle al usuario que lo invoque
  explícitamente o confirmar que ultracode está activo en la sesión antes de correr.
---

# Skill: Auditoría Airtable Cliente (multi-agente adversarial)

## Descripción

Detecta con precisión inconsistencias de schema, linkeo, data quality y contrato
tool↔Airtable en la base Airtable de un cliente. Produce 3 entregables listos
para llevar a una reunión: reporte técnico con fixes propuestos, guía operativa
para quien edita la base, y diagrama Mermaid (`erDiagram`) del schema real listo
para pegar en Figma/FigJam (la agencia usa Figma como visualizador principal de
diagramas, no draw.io — ver nota de formato más abajo).

**Origen:** validado en SYS (Sistemas y Soluciones) el 2026-07-01, disparado por
un audio de Edgardo reportando confusión en el linkeo Equipos↔Sustratos. La
auditoría confirmó el bug reportado (37/53 records de Sustratos contaminados,
77 links apuntando a fantasmas) y además encontró 6 bugs P0 más que estaban
rotos en silencio desde la migración inicial — ninguno visible desde la UI de
Airtable, solo desde el contrato de campos que leen las tools de n8n.

**Por qué multi-agente y no un solo agente leyendo todo:** un solo pase lineal
tiende a fijarse en el bug reportado y dar por bueno el resto. Cada dimensión
adversarial mira la base desde un ángulo ciego distinto (primary fields, links,
data quality, drift vs docs, contrato con las tools, reverse links, vistas) —
en la corrida real, el bug reportado por el cliente fue solo 1 de 65 findings.

## Cuándo invocarlo

- El cliente reporta confusión o un bug concreto de linkeo/datos en su Airtable.
- Antes de una reunión donde se va a repasar o refrescar el modelo de datos.
- Después de una migración (Excel→Airtable, cambio de schema) para validar que
  no quedó drift.
- Chequeo periódico de salud si la base lleva meses sin auditar y las tools
  vienen devolviendo NOT_FOUND con más frecuencia de la esperada.

## Cuándo NO invocarlo

- Bug puntual y ya diagnosticado (ir directo al fix, no hace falta el barrido completo).
- Cliente sin Airtable en Etapa 2 (bases chicas <5 tablas, mejor revisión manual directa).
- Sin ultracode activo en la sesión y el usuario no quiere pagar el costo — en
  ese caso, ofrecer una versión liviana (1 solo agent general-purpose leyendo
  el snapshot) en vez de este skill.

---

## Inputs requeridos

1. **Código de cliente** (ej: SYS, VTR, TFO) → determina `clients/{XXX}_*/`.
2. **Token de Airtable con scope `schema.bases:read` + `data.records:read`** —
   normalmente ya existe en `clients/{XXX}_*/06_docs/airtable-credentials.md`
   (archivo gitignored). Si no está, pedírselo al usuario o generar uno nuevo
   de solo-lectura en https://airtable.com/create/tokens.
3. **Base ID** (`appXXXXXXXXXXXXXX`) — también en `airtable-credentials.md`.
4. **Confirmación de que ultracode está activo** (el usuario dijo la palabra
   "ultracode" o hay reminder de sesión confirmándolo). Si no, preguntarlo antes
   de lanzar — el workflow gasta ~1-2M tokens en una corrida típica de 7-11 tablas.

---

## Proceso

### Paso 1 — Reunir contexto del cliente

Leer en paralelo:
- `clients/{XXX}_*/06_docs/airtable-credentials.md` (token, base ID, table IDs).
- `clients/{XXX}_*/05_crm/airtable-*-schema.md` (schema documentado, si existe).
- `clients/{XXX}_*/03_workflows/*.json` — identificar cuáles leen Airtable
  (buscar nodos `n8n-nodes-base.airtable`, `filterByFormula`, o Format Output
  con referencias `f['Campo']`). Estos son el "contrato" que la dimensión
  `tool-contract` va a verificar.
- Si hay un reporte/audio/mensaje disparador del cliente, transcribirlo primero
  (ver `_core/standards/` o convención de markitdown del workspace para audio)
  y extraer la cita textual — va al bloque `KNOWN_BUG_QUOTE` del contexto.

### Paso 2 — Fetch del snapshot (barato, sin LLM)

```bash
export AIRTABLE_TOKEN="<token del paso 1>"
export AIRTABLE_BASE_ID="<base id del paso 1>"
bash .claude/skills/auditoria-airtable-cliente/scripts/fetch-airtable-snapshot.sh \
  /ruta/scratchpad/airtable-snapshot-{{XXX}}
```

Este script:
- Descarga el schema completo (`00-schema.json`) — tablas, campos, tipos, linked-record targets.
- Descarga TODOS los records de TODAS las tablas con paginación completa.
- Usa `python3` (no `jq`) para el parseo — más tolerante a control chars en
  campos de texto largo que rompen `jq` silenciosamente.

**Antes de lanzar el workflow completo, vale la pena un spot-check manual de
2-3 curl calls sobre la hipótesis más probable** (como se hizo en SYS: 1 curl
al schema de la tabla sospechosa + 1 a una muestra de records confirmó el bug
en 30 segundos, antes de gastar el presupuesto del workflow). No es obligatorio
pero acelera y da una primera señal de si la auditoría completa vale la pena.

### Paso 3 — Adaptar y lanzar el workflow

Copiar `references/workflow-template.js`, reemplazar los placeholders
(`{{CLIENT_CODE}}`, `{{BASE_ID}}`, `{{SNAP_DIR}}`, `{{TOOL_FILES_LIST}}`, rutas
de output, etc.) con los valores reales del cliente, y lanzarlo con el tool
`Workflow` (parámetro `script`, NO `scriptPath` en el primer run).

**Las 7 dimensiones del template son un punto de partida, no un contrato
rígido** — agregar o quitar dimensiones según lo que tenga la base del cliente
(ej: si no hay campos linked complejos, saltear `reverse-links`; si el cliente
tiene un CRM de Leads activo con muchos records, agregar una dimensión
`leads-integrity` específica).

Estructura de la corrida (fase Analyze → fase Synthesize):
- **Analyze**: N agents en `parallel()`, cada uno con su propio prompt de
  dimensión + mismo `FINDING_SCHEMA` de salida estructurada.
- **Synthesize**: 3 agents en `parallel()` (reporte / guía / diagrama Mermaid),
  cada uno recibe el JSON completo de findings crudos y produce su deliverable.

No usar `pipeline()` acá — las 3 dimensiones de síntesis son independientes
entre sí (no hay dependencia secuencial), así que `parallel()` es correcto y
más rápido.

**Formato del diagrama — Mermaid `erDiagram`, no draw.io.** El visualizador
principal de la agencia es Figma/FigJam, que tiene paste-to-diagram nativo para
Mermaid (seleccionás el texto y lo pegás en un board FigJam → se convierte en
shapes editables). Por eso el deliverable #3 es un archivo `.mmd` **puro**
(sin fences ``` ni texto markdown alrededor — el archivo entero se selecciona
y pega tal cual). `erDiagram` es el tipo de diagrama Mermaid pensado para
entidades+atributos+relaciones, el fit natural para un schema Airtable: cada
tabla es una entidad, cada campo un atributo (primary marcado `PK`), cada
linked field una relación con cardinalidad y etiqueta. Los findings P0/P1 se
anotan directo como comentario del atributo afectado (tercera columna entre
comillas) — es lo primero que se ve al abrir el board. El template completo
de esta instrucción está en `references/workflow-template.js`, tercer agent
del bloque Synthesize.

### Paso 4 — Verificar deliverables

```bash
ls -la clients/{XXX}_*/06_docs/airtable-auditoria-*.md \
       clients/{XXX}_*/06_docs/airtable-guia-*.md \
       salidas/diagramas/{xxx}-airtable-schema-real-*.mmd

# Validación de sintaxis Mermaid (requiere red; si no hay, ver fallback abajo)
npx --yes @mermaid-js/mermaid-cli@latest \
  -i salidas/diagramas/{xxx}-airtable-schema-real-*.mmd \
  -o /tmp/mermaid-check.svg && echo OK

# Fallback sin red: chequeo estructural — toda línea de relación matchea
# "ENTIDAD (cardinalidad)--(cardinalidad) ENTIDAD : "etiqueta"" y las llaves
# de cada bloque de entidad están balanceadas. El agent de síntesis ya corre
# esto durante la generación; repetirlo acá es solo doble chequeo manual.
```

Leer el resumen ejecutivo del reporte (primeras ~50 líneas) y reportarle al
usuario: total de findings por severidad, los P0 más urgentes, y las
preguntas abiertas para la reunión.

### Paso 5 — Fixes P0 (fuera de este skill, manual)

Este skill **nunca aplica fixes en la base viva** — solo diagnostica y propone
(cada finding P0/P1 en el reporte trae el curl exacto marcado `--dry-run`).
Aplicar fixes es responsabilidad del operador humano después de revisar el
reporte, idealmente con smoke test post-fix contra la tool afectada.

---

## Composición

**Requiere:** ultracode activo (tool `Workflow`).
**Invoca:** `Workflow` (script inline con `parallel()` de 2 niveles).
**Complementa:** `comparador-real-vs-config-toolworkflow` (ese compara n8n vivo
vs doc esperado; este compara Airtable vivo vs doc esperado + data quality +
contrato con las tools — no se solapan, se pueden correr ambos en la misma
sesión de prep pre-reunión).
**Genera output para:** `/cliente-sync` (los 2 docs nuevos entran al historial
del cliente). El `.mmd` queda en `salidas/diagramas/` — misma carpeta que usa
`/diagramar`, aunque ese comando es específico de draw.io y no genera ni lee
este formato; comparten carpeta, no herramienta. Si en algún momento se
necesita el mismo diagrama embebido en un doc legible (no solo para pegar en
Figma), usar el patrón de `generar-uml` (Mermaid dentro de fences ``` en un
`.md` autocontenido) en vez de duplicar la generación acá.

---

## Notas operativas

- **Tiempo:** ~10-15 min de ejecución del workflow (corrida real SYS: 13 min,
  10 agents, ~1.6M tokens, 97 tool calls). Lanzar en background si hay otra
  cosa que hacer mientras corre.
- **Costo:** alto (multi-agente + Opus). Solo justificado cuando el usuario
  confirmó ultracode. Para chequeos rápidos sin ese presupuesto, usar 1 agent
  general-purpose leyendo el snapshot con una sola pasada (menos exhaustivo,
  pero cero costo de orquestación).
- **Los findings vienen deduplicados en la fase Synthesize**, no en Analyze —
  es normal y esperado que 2-3 dimensiones distintas reporten el mismo bug
  desde ángulos distintos (ej: `primary-fields` y `data-quality` ambos
  detectan la tabla Sustratos contaminada). El agent de síntesis del reporte
  se encarga de consolidar.
- **El snapshot es un punto-en-el-tiempo.** Si pasan varios días entre el
  fetch y la reunión, y el cliente sigue editando la base, re-correr el fetch
  (Paso 2) antes de aplicar cualquier fix — no confiar en un snapshot viejo
  para decisiones de escritura.
- **Nunca mandar el token de Airtable en el prompt de un agent.** El workflow
  lee el snapshot local (JSON en disco), no hace llamadas API él mismo — así
  el token nunca circula por el contexto de los subagentes.
- **Import a Figma:** abrir el `.mmd` (no como código, como texto plano — un
  editor simple alcanza), seleccionar todo, copiar, y pegar directo en un
  board de FigJam. Si Figma no lo detecta como diagrama (pega como texto
  suelto), confirmar que el archivo no tiene fences ``` colgando al
  principio/final — es el error más común y el agent de síntesis ya está
  instruido para no agregarlos, pero vale doble-chequear antes de la reunión.
  Una vez importado queda 100% editable como shapes nativos de FigJam — se
  puede reacomodar, recolorear o resumir tablas ahí mismo sin tocar el `.mmd`.
