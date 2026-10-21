// TEMPLATE — Workflow de auditoría Airtable adversarial multi-dimensión.
// Basado en la corrida real de SYS (2026-07-01, run wf_50bdd6fd-c96): 7 agents
// paralelos + 3 synthesizers en paralelo, 76 findings crudos → 65 únicos, 13 min.
//
// CÓMO USAR: copiar este script, reemplazar todos los {{PLACEHOLDER}} con los
// valores del cliente actual, y pasarlo al tool Workflow (param `script`).
// NO es ejecutable tal cual — es un molde para que Claude lo complete por cliente.
//
// Placeholders a reemplazar:
//   {{CLIENT_CODE}}       — ej: SYS, VTR, TFO
//   {{CLIENT_NAME}}       — ej: Sistemas y Soluciones
//   {{BASE_NAME}}         — ej: SyS Catalogo
//   {{BASE_ID}}           — ej: appMD3g2HWxzBaZAM
//   {{SNAP_DIR}}          — ruta absoluta al snapshot (ver scripts/fetch-airtable-snapshot.sh)
//   {{CLIENT_DIR}}        — ruta absoluta a clients/{{CLIENT_CODE}}_{{CLIENT_NAME}}
//   {{SCHEMA_DOC_PATH}}   — ruta al doc de schema documentado (si existe)
//   {{TOOL_FILES_LIST}}   — lista de los .json de 03_workflows/ que leen Airtable
//   {{KNOWN_BUG_QUOTE}}   — cita textual del cliente si hay un reporte disparador (opcional)
//   {{REPORT_OUT_PATH}}   — ej: clients/SYS_.../06_docs/airtable-auditoria-{{FECHA}}.md
//   {{GUIA_OUT_PATH}}     — ej: clients/SYS_.../06_docs/airtable-guia-{{PERSONA}}-{{FECHA}}.md
//   {{MERMAID_OUT_PATH}}  — ej: salidas/diagramas/{{CLIENT_CODE}}-airtable-schema-real-{{FECHA}}.mmd
//                           (archivo .mmd PURO — sin fences ``` — para copy/paste directo a FigJam)

export const meta = {
  name: '{{CLIENT_CODE_LOWER}}-airtable-audit',
  description: 'Auditoría exhaustiva de la base {{CLIENT_CODE}} Airtable. Detecta bugs de linkeo/data/schema en 7 dimensiones adversariales y produce reporte + guía operativa + diagrama Mermaid (erDiagram) listo para importar a Figma/FigJam.',
  phases: [
    { title: 'Analyze', detail: '7 agents adversariales revisan el snapshot desde ángulos distintos' },
    { title: 'Synthesize', detail: 'Dedup + ranking severidad + 3 deliverables (reporte, guía, diagrama Mermaid)' },
  ],
}

const SNAP = '{{SNAP_DIR}}'
const REPO = '/Users/camilo/Downloads/camilo-workspace'
const CLIENT = '{{CLIENT_DIR}}'

// Ajustar este bloque de contexto por cliente: qué base es, qué tools la
// consumen, qué bug disparó la auditoría (si hay), qué contrato de campos
// existe entre las tools de n8n y los nombres de field de Airtable.
const CONTEXT = `
# CONTEXTO — Auditoría Airtable {{CLIENT_CODE}}

**Cliente:** {{CLIENT_CODE}} — {{CLIENT_NAME}}
**Base viva:** \`{{BASE_NAME}}\` — {{BASE_ID}}
**Fuente de datos:** snapshot completo API Airtable, guardado en \`${SNAP}\`
  - \`00-schema.json\` — schema completo (tablas, campos, tipos, linked-record targets)
  - resto de archivos \`.json\` — records reales por tabla

**Schema documentado (referencia para detectar divergencia):**
- {{SCHEMA_DOC_PATH}}

**Contrato con las tools del agente (crítico — si cambió un field name, se rompe silente):**
{{TOOL_FILES_LIST}}

**Bug conocido (si aplica):**
{{KNOWN_BUG_QUOTE}}

**Objetivo:** ver la base con ojos frescos, encontrar problemas de linkeo/data/schema,
y producir 3 entregables:
1. Reporte con inconsistencias rankeadas P0/P1/P2 + fixes propuestos (API calls, NO aplicados).
2. Guía operativa "cómo editar cada tabla" para quien edita el catálogo.
3. Diagrama Mermaid (erDiagram) del schema real (no del documentado), listo para pegar en Figma/FigJam.

**Restricciones:**
- NUNCA aplicar cambios en la base viva (solo diagnóstico + fixes propuestos con curl --dry-run).
- Español rioplatense.
- Fixes P0 con API call EXACTA lista para correr tras revisión humana.
- Priorizar por impacto real (rompe tool viva > confunde al cliente > cosmético).
`

// Las 7 dimensiones cubren ángulos independientes. Se pueden agregar/quitar
// según la base del cliente (ej: si no hay linked records complejos, se puede
// saltear reverse-links). El schema JSON de cada dimensión es idéntico —
// reusarlo tal cual, solo cambia el prompt.

const FINDING_SCHEMA = {
  type: 'object',
  properties: {
    dimension: { type: 'string' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          table: { type: 'string' },
          issue: { type: 'string' },
          severity: { type: 'string', enum: ['P0', 'P1', 'P2'] },
          evidence: { type: 'string' },
          root_cause_hypothesis: { type: 'string' },
          proposed_fix: { type: 'string' },
          impact_on_tool: { type: 'string' },
        },
        required: ['table', 'issue', 'severity', 'evidence'],
      },
    },
    notes: { type: 'string' },
  },
  required: ['dimension', 'findings'],
}

const DIMENSIONS = [
  {
    key: 'primary-fields',
    prompt: `${CONTEXT}

# Tu misión (dimensión: PRIMARY FIELDS)

Auditor adversarial. ¿Están los primary fields de cada tabla semánticamente correctos?
(ej: el primary de una tabla "Sustratos" debe ser un nombre de sustrato, no un ancho ni un ID).

1. Leé \`${SNAP}/00-schema.json\`. Identificá primaryFieldId de cada tabla.
2. Cargá muestra de records reales y verificá si el valor del primary es semánticamente
   "el nombre del entity" que la tabla representa.
3. Reportá cada anomalía: tabla, primary actual, ejemplos anómalos vs esperados,
   causa raíz probable, fix propuesto (curl --dry-run).

Output: JSON con schema {dimension, findings[], notes}. Si 0 anomalías, findings: [].`,
    schema: FINDING_SCHEMA,
  },
  {
    key: 'linked-records',
    prompt: `${CONTEXT}

# Tu misión (dimensión: LINKED RECORDS)

Auditor adversarial. ¿Cada linked field apunta a la tabla que su nombre implica?

1. Leé \`${SNAP}/00-schema.json\`. Recorré todos los fields \`multipleRecordLinks\`.
2. Para cada uno: nombre del field, \`options.linkedTableId\` resuelto a tabla, ¿coincide
   el nombre con la tabla apuntada?
3. Cargá muestras y verificá si los recIDs referenciados existen en la tabla target (orphans).
4. Detectá contradicciones \`prefersSingleRecordLink: true\` con múltiples valores reales.

Output: mismo formato JSON.`,
    schema: FINDING_SCHEMA,
  },
  {
    key: 'data-quality',
    prompt: `${CONTEXT}

# Tu misión (dimensión: DATA QUALITY)

Auditor adversarial. Contaminación, duplicados, primary vacíos, campos obligatorios ausentes,
valores fuera del enum permitido.

1. Leé el schema para conocer campos/tipos/choices de singleSelect.
2. Para cada tabla, cargá TODOS los records y auditá: primary vacío/nulo, primary duplicado,
   valores fuera de enum, campos obligatorios (según schema-doc) vacíos, tablas con 0 records
   cuando se esperaban N (migración fallida).
3. Contá y listá TODOS los problemas — no solo ejemplos. Sé preciso con conteos.

Output: mismo formato JSON.`,
    schema: FINDING_SCHEMA,
  },
  {
    key: 'schema-vs-docs',
    prompt: `${CONTEXT}

# Tu misión (dimensión: SCHEMA VS DOCS)

Auditor adversarial. Divergencia entre schema documentado y schema vivo.

1. Leé {{SCHEMA_DOC_PATH}} (si existe).
2. Leé \`${SNAP}/00-schema.json\`.
3. Comparar tabla por tabla, campo por campo: tablas/campos faltantes o de más,
   renombrados, cambios de tipo, choices divergentes.
4. Marcar P1 lo que confunde al cliente (lee doc, ve otra cosa), P0 lo que rompe tool.

Output: mismo formato JSON.`,
    schema: FINDING_SCHEMA,
  },
  {
    key: 'tool-contract',
    prompt: `${CONTEXT}

# Tu misión (dimensión: TOOL CONTRACT)

Auditor adversarial. ¿Los field names que las tools de n8n leen todavía existen con el
nombre exacto en la base viva? Si cambió, la tool devuelve null silencioso — cero errores,
cero warnings, pero el LLM del agente recibe basura o vacío.

1. Leé el jsCode de los nodos Format Output / Validate Input / filterByFormula en:
   {{TOOL_FILES_LIST}}
2. Enumerá TODOS los field names referenciados (\`f['Campo']\`, \`{Campo}\` en fórmulas).
3. Verificá contra \`${SNAP}/00-schema.json\` que existen. Reportá field faltante,
   tool afectada, síntoma esperado.
4. Bonus: diferencias sutiles de tildes/mayúsculas que rompen matching silenciosamente.

Output: mismo formato JSON. Default severity P0 (rompen tool viva) salvo field opcional/legacy.`,
    schema: FINDING_SCHEMA,
  },
  {
    key: 'reverse-links',
    prompt: `${CONTEXT}

# Tu misión (dimensión: REVERSE LINKS + INTEGRIDAD BIDIRECCIONAL)

Auditor adversarial. ¿Los reverse links están configurados y consistentes?

1. Leé \`${SNAP}/00-schema.json\`. Para cada \`multipleRecordLinks\`, extraé
   \`options.inverseLinkFieldId\` y confirmá que existe en la tabla target con nombre descriptivo.
2. Verificá integridad bidireccional con muestras: si A→B incluye recID X, B.record(X)→A
   debe incluir el recID de A. Reportar asimetrías.
3. Reportar reverse fields con nombres genéricos/pobres que dificultan la operación manual.

Output: mismo formato JSON.`,
    schema: FINDING_SCHEMA,
  },
  {
    key: 'vistas',
    prompt: `${CONTEXT}

# Tu misión (dimensión: VISTAS)

Auditor adversarial. ¿Las vistas críticas que consumen las tools siguen existiendo
con el filtro correcto?

1. Identificá vistas críticas documentadas (ej: "Para agente" con filtro Status=Activo).
2. Si el schema fetcheado no incluye views expandidas, marcar como P1 abierto para
   validación manual (la agencia/el operador abre la base y confirma).

Output: mismo formato JSON.`,
    schema: FINDING_SCHEMA,
  },
]

phase('Analyze')
log(`Lanzando ${DIMENSIONS.length} auditores adversariales en paralelo`)

const dimResults = await parallel(
  DIMENSIONS.map((d) => () =>
    agent(d.prompt, { label: `audit:${d.key}`, phase: 'Analyze', schema: d.schema, effort: 'high' })
  )
)

const validResults = dimResults.filter(Boolean)
const allFindings = validResults.flatMap((r) => (r.findings || []).map((f) => ({ ...f, dimension: r.dimension })))

log(`Auditoría terminada: ${validResults.length}/${DIMENSIONS.length} dimensiones, ${allFindings.length} findings crudos`)

const counts = allFindings.reduce((acc, f) => {
  acc[f.severity] = (acc[f.severity] || 0) + 1
  return acc
}, {})
log(`Severidad: P0=${counts.P0 || 0}, P1=${counts.P1 || 0}, P2=${counts.P2 || 0}`)

phase('Synthesize')

const SYNTH_CONTEXT = `
# Findings crudos de los ${DIMENSIONS.length} auditores adversariales

Total: ${allFindings.length}. Distribución: P0=${counts.P0 || 0}, P1=${counts.P1 || 0}, P2=${counts.P2 || 0}.

\`\`\`json
${JSON.stringify(allFindings, null, 2)}
\`\`\`

${CONTEXT}
`

const [reporte, guia, mermaid] = await parallel([
  () =>
    agent(
      `${SYNTH_CONTEXT}

# Tu misión: reporte de auditoría

Producí el reporte completo en Markdown. Va a quedar en \`{{REPORT_OUT_PATH}}\`.

Estructura: Resumen ejecutivo → Findings P0/P1 (deduplicados, con título/tabla/qué está
mal/evidencia verbatim/causa raíz/impacto/fix propuesto con curl --dry-run/riesgo del fix)
→ tabla compacta P2 → preguntas abiertas para el cliente → plan de fixes ordenado →
anexo schema-doc-vs-vivo → anexo matriz tool↔field.

Tono: profesional, breve, rioplatense donde sea natural, sin emojis. 400-800 líneas.
Guardar y confirmar "Reporte grabado en <path>".`,
      { label: 'synth:reporte', phase: 'Synthesize', effort: 'high' }
    ),
  () =>
    agent(
      `${SYNTH_CONTEXT}

# Tu misión: guía operativa

Producí guía Markdown para quien edita la base día a día. Va a quedar en \`{{GUIA_OUT_PATH}}\`.

Estructura: cómo pensar la base (Airtable ≠ Excel, columnas = punteros) → tablas y para qué
sirven → cómo editar cada tabla (paso a paso, qué NO tocar) → recetas comunes → qué está
roto ahora y qué se va a hacer → contacto de soporte.

Tono: cordial, breve, sin tecnicismos innecesarios. 200-400 líneas.
Guardar y confirmar "Guía grabada en <path>".`,
      { label: 'synth:guia', phase: 'Synthesize', effort: 'high' }
    ),
  () =>
    agent(
      `${SYNTH_CONTEXT}

# Tu misión: diagrama Mermaid (erDiagram) del schema REAL, listo para Figma

Producí un archivo \`.mmd\` **PURO** (sin fences \\\`\\\`\\\`, sin encabezado markdown, solo
sintaxis Mermaid arrancando en \`erDiagram\`) del schema real. Va a quedar en
\`{{MERMAID_OUT_PATH}}\`.

**Por qué .mmd puro:** el destino es Figma/FigJam — el flujo de uso es seleccionar TODO
el contenido del archivo y pegarlo directo en un tablero FigJam, que lo auto-detecta como
Mermaid y lo convierte en shapes editables nativos. Si el archivo tiene fences o texto
markdown alrededor, el paste-to-diagram de Figma puede fallar o traer el fence como texto.

**Sintaxis \`erDiagram\` (elegí esta, no \`graph\`/\`classDiagram\`)** — es el tipo de diagrama
Mermaid pensado para entidades + atributos + relaciones, el fit natural para un schema
Airtable (tablas = entidades, campos = atributos, linked records = relaciones):

\`\`\`
erDiagram
    EQUIPOS {
        string Modelo PK
        string Marca
        string Formato
    }
    SUSTRATOS {
        string Sustrato PK "37/53 records contaminados - ver P0 S-01"
        string Tipo
    }
    EQUIPOS ||--o{ SUSTRATOS : "Sustratos compatibles"
\`\`\`

Reglas de construcción:
- Un bloque de entidad por tabla real (nombre de tabla en MAYÚSCULAS, sin espacios ni
  tildes en el identificador de entidad — Mermaid no las tolera bien ahí; el nombre real
  con tildes va como comentario o en el reporte, no en el ID de la entidad).
- Marcá el primary field de cada tabla con \`PK\` en la columna key.
- No hace falta listar TODOS los campos de tablas con muchos fields (ej: Equipos con 20)
  — priorizá: primary field, campos linked (son los que arman las relaciones), y campos
  con findings P0/P1 asociados. El resto se puede resumir con una fila
  \`string _otros_campos "N campos adicionales, ver reporte"\`.
- Una línea de relación por cada linked field real, con cardinalidad correcta según el
  tipo (\`||--o{\` para 1-a-muchos, \`}o--o{\` para muchos-a-muchos si ambos lados son
  multipleRecordLinks). La etiqueta de la relación = nombre del field en Airtable.
- **Anotá los findings P0/P1 directo en el diagrama** usando el tercer campo (comentario
  entre comillas) del atributo afectado — es lo que un lector va a ver primero al abrir
  el board en Figma. No uses colores/estilos (erDiagram no los soporta bien); el texto
  del comentario es la señal.
- Layout: Mermaid arma el layout automático, no hace falta posicionar manualmente. Solo
  asegurate de que el orden de declaración de entidades ponga primero las tablas centrales
  (más relaciones entrantes/salientes) para que el layout automático las centre.

Fuente: \`${SNAP}/00-schema.json\`.

**Validación** (Bash): intentá
\`npx --yes @mermaid-js/mermaid-cli@latest -i <path> -o /tmp/mermaid-check.svg\`
con timeout corto. Si no hay red o el comando no está disponible, hacé un chequeo
estructural manual en su lugar: cada línea de relación matchea el patrón
\`ENTIDAD (\\|\\||\\}o|o\\{)--(o\\{|\\|\\||o\\|) ENTIDAD : "etiqueta"\`, cada bloque de entidad
abre y cierra \`{ }\` balanceado, y no hay IDs de entidad duplicados. Iterá si algo falla.

Guardar con Write. Confirmar "Diagrama Mermaid grabado en <path> (N entidades, M relaciones)".`,
      { label: 'synth:mermaid', phase: 'Synthesize', effort: 'high' }
    ),
])

log('Deliverables generados. Auditoría cerrada.')

return {
  findings_count: allFindings.length,
  severities: counts,
  dimensions_completed: validResults.length,
  deliverables: {
    reporte: '{{REPORT_OUT_PATH}}',
    guia: '{{GUIA_OUT_PATH}}',
    mermaid: '{{MERMAID_OUT_PATH}}',
  },
}
