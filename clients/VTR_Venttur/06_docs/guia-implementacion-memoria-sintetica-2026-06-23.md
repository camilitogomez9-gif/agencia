# Guía de implementación — Memoria sintética del agente VTR

> **Fecha:** 2026-06-23
> **Plan de referencia:** `/Users/camilo/.claude/plans/lexical-zooming-pond.md`
> **Outcome esperado:** lead recibe Touch 1 (o Touch 2/3, o Rescate) y luego responde. El agente lo trata reconociendo nombre, programa y contexto previo, SIN saludo inicial ni re-pregunta de datos.

---

## Contexto técnico (lectura rápida)

- `venttur-main-v1.json` líneas 33-34 usa `sessionKey = whatsapp_phone.replace('+','')` para el nodo `memoryPostgresChat` v1.3, contextWindow=35.
- Credencial Postgres: `Venttur` id `ihpvM7nYMdLCwWDP`.
- Tabla `n8n_chat_histories` shape `{id BIGSERIAL, session_id TEXT, message JSONB, created_at TIMESTAMP DEFAULT NOW()}`.
- La columna `message` es JSONB libre — soporta `{"type": "system"|"ai"|"human", "content": "..."}` sin restricción de schema.
- Pre-cargando 1 mensaje `system` (datos del form) + 1 mensaje `ai` (texto del template enviado) por cada Touch/Rescate, el `memoryPostgresChat` del main los carga automáticamente como turnos anteriores cuando el lead responde.

---

## Workflows a modificar

| Workflow | Status | Entrega |
|---|---|---|
| `outreach-form-meta-backfill-v2.json` | NUEVO en repo, NO desplegado | JSON listo para import — `clients/VTR_Venttur/03_workflows/outreach-form-meta-backfill-v2.json` |
| `Outreach Form Meta - Venttur` (workflowId `CUuFxbst3iHpgeXS`) | LIVE en n8n | EDITs paso a paso abajo |
| `Rescate Post-Link` (workflowId `mkEP1qFN7MVb9qP0`) | LIVE en n8n | EDITs paso a paso abajo |

---

## SQL DDL — preparación

**No es estrictamente necesario** ejecutar nada manualmente porque la tabla `n8n_chat_histories` ya existe (la creó el nodo `memoryPostgresChat` del main). Pero conviene verificar:

```sql
-- 1. Confirmar que la tabla existe
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' AND table_name = 'n8n_chat_histories';

-- 2. Inspeccionar el shape de message JSONB (ejemplos)
SELECT id, session_id, message, created_at
FROM n8n_chat_histories
ORDER BY id DESC LIMIT 5;

-- 3. Agregar índice para queries de "type" si los hay muchos
CREATE INDEX IF NOT EXISTS idx_n8n_chat_histories_session_type
ON n8n_chat_histories (session_id, ((message->>'type')));
```

Si el índice ya existe (creado por una migración previa) el `IF NOT EXISTS` lo skipea.

---

## EDIT #1 — `Outreach Form Meta - Venttur` (workflowId `CUuFxbst3iHpgeXS`)

### Estado actual del workflow

Topología relevante de Flujo B (cron):
```
Cron 5min → Get Leads Pendientes → Split In Batches (1) → Switch (por Toques enviados)
  ├── rama 0 (Toques < 1) → createSubscriber ManyChat → ¿Subscriber OK? (true) → sendFlow Outreach Boarding Form → Marcar Enviado
  ├── rama 1 (Toques = 1) → sendFlow Touch 2 → Marcar Enviado
  └── rama 2 (Toques = 2) → sendFlow Touch 3 → Marcar Enviado
```

Cada rama termina en `Marcar Enviado`. Hoy ese es el último nodo de cada rama.

### Cambio: insertar nodos Postgres DESPUÉS de cada `Marcar Enviado`

**Para la rama 0 (Touch 1):** 3 nodos nuevos en cadena.

**Para las ramas 1 y 2 (Touch 2/3):** 1 nodo nuevo cada una.

### Paso 1 — Crear nodo `Build Memory Texts (Touch 1)`

Insertarlo **después de Marcar Enviado** en la rama 0.

- **Type:** `n8n-nodes-base.code` v2
- **Notes:** "Construye system message (datos del form en prosa) + ai message (texto del Touch 1)."
- **JS code:**

```javascript
// Build Memory Texts — outreach v2 Touch 1
const lead = $('Split In Batches (1)').item.json;
const sessionKey = (lead.Telefono || '').toString();

// === System message: datos del form en prosa natural ===
function buildSystemMessage(d) {
  const nombreCompleto = [d.Nombre, d.Apellido].filter(Boolean).join(' ').trim() || 'el lead';
  const email = d.Email ? d.Email : null;
  const tel = d.Telefono ? `tel +${d.Telefono}` : null;
  const contact = [email, tel].filter(Boolean).join(', ');
  const contactStr = contact ? ` (${contact})` : '';

  const origenMap = {
    'Form Meta': 'completó un formulario de Meta',
    'Form Landing': 'completó el formulario de nuestra landing',
    'CTWA': 'vino por un anuncio de WhatsApp',
  };
  const accion = origenMap[d.Origen] || 'mostró interés';

  const programa = d['Programa interés']
    ? ` interesado/a en ${d['Programa interés']}`
    : ' interesado/a en uno de nuestros programas';

  const cualif = [
    d['Grado Escolar'] && `para ${d['Grado Escolar']}`,
    d['Inicio Deseado'] && `con inicio deseado en ${d['Inicio Deseado']}`,
    d['Nivel Inglés'] && `y nivel de inglés ${d['Nivel Inglés']}`,
  ].filter(Boolean).join(' ');
  const cualifStr = cualif ? ` ${cualif}` : '';

  const campania = d['Ad Name']
    ? ` Vino por la campaña ${d['Ad Name']}${d.Platform ? ' en ' + d.Platform : ''}.`
    : '';

  return `El lead ${nombreCompleto}${contactStr} ${accion}${programa}${cualifStr}.${campania}`;
}

const systemText = buildSystemMessage(lead);

// === AI message: texto del Touch 1 renderizado ===
// TODO: reemplazar con texto literal copiado desde ManyChat Flow editor del template `boarding_form_followup`.
// Ver clients/VTR_Venttur/06_docs/template-texts-canonical.md §1
const TOUCH_1_TEXT = `Hola {{first_name}}, soy Mauricio de Venttur. Vi tu interés en uno de nuestros programas educativos y me gustaría conocer más sobre lo que buscás para tu hijo/a. ¿Querés que te cuente las opciones que tenemos disponibles o agendamos una llamada de orientación de 15 minutos?`;

const firstName = (lead.Nombre || '').toString();
const aiText = TOUCH_1_TEXT.replace(/\{\{first_name\}\}/g, firstName || 'hola');

return [{ json: {
  session_key: sessionKey,
  system_message: { type: 'system', content: systemText },
  ai_message: { type: 'ai', content: aiText },
}}];
```

### Paso 2 — Crear nodo `Insert system FORM (idempotent)` (rama 0)

- **Type:** `n8n-nodes-base.postgres` v2.5
- **Credential:** `Venttur` (id `ihpvM7nYMdLCwWDP`)
- **Operation:** `Execute Query`
- **Query:**

```sql
INSERT INTO n8n_chat_histories (session_id, message)
SELECT $1, $2::jsonb
WHERE NOT EXISTS (
  SELECT 1 FROM n8n_chat_histories
  WHERE session_id = $1 AND message->>'type' = 'system'
)
RETURNING id;
```

- **Query Parameters:**
```
={{ [$json.session_key, JSON.stringify($json.system_message)] }}
```

- **On Error:** `continueRegularOutput`
- **Notes:** "Idempotente: solo inserta si no existe ya un system para este session_id. WHERE NOT EXISTS cubre re-envíos del cron."

### Paso 3 — Crear nodo `Insert ai Touch 1` (rama 0)

- **Type:** `n8n-nodes-base.postgres` v2.5
- **Credential:** `Venttur`
- **Operation:** `Execute Query`
- **Query:**

```sql
INSERT INTO n8n_chat_histories (session_id, message)
VALUES ($1, $2::jsonb)
RETURNING id;
```

- **Query Parameters:**
```
={{ [$('Build Memory Texts (Touch 1)').item.json.session_key, JSON.stringify($('Build Memory Texts (Touch 1)').item.json.ai_message)] }}
```

- **On Error:** `continueRegularOutput`
- **Notes:** "Insert directo. NO idempotente — el cron solo lo invoca una vez por lead (rama 0 solo dispara con Toques=0)."

### Paso 4 — Conectar (rama 0)

Después de los pasos 1-3, la cadena debe verse así:

```
Marcar Enviado (rama 0)
   ↓
Build Memory Texts (Touch 1)
   ↓
Insert system FORM (idempotent)
   ↓
Insert ai Touch 1
   ↓
[FIN DE RAMA 0]
```

Verificar que no hay nodos huérfanos colgando de `Marcar Enviado` rama 0.

### Paso 5 — Crear nodo `Insert ai Touch 2` (rama 1)

Después del `Marcar Enviado` de la **rama 1** del Switch.

- **Type:** `n8n-nodes-base.postgres` v2.5
- **Credential:** `Venttur`
- **Operation:** `Execute Query`
- **Query:**

```sql
INSERT INTO n8n_chat_histories (session_id, message)
VALUES ($1, $2::jsonb)
RETURNING id;
```

- **Query Parameters:**
```
={{ [
  ($('Split In Batches (1)').item.json.Telefono || '').toString(),
  JSON.stringify({
    type: 'ai',
    content: `[REEMPLAZAR_TOUCH_2_TEXT]`.replace(/\{\{first_name\}\}/g, ($('Split In Batches (1)').item.json.Nombre || 'hola').toString())
  })
] }}
```

> **Importante:** reemplazar `[REEMPLAZAR_TOUCH_2_TEXT]` con el texto literal del Touch 2 copiado desde ManyChat Flow editor (template aprobado `flow_ns content20260616231914_193459`). Ver `template-texts-canonical.md` §2.

- **On Error:** `continueRegularOutput`
- **Notes:** "Touch 2 fue enviado por sendFlow Touch 2. Insertamos solo el ai message; el system ya existe del Touch 1."

### Paso 6 — Crear nodo `Insert ai Touch 3` (rama 2)

Idéntico al paso 5 pero con `flow_ns content20260616231947_185709` y texto del Touch 3. Conectar después del `Marcar Enviado` de la **rama 2**.

### Verificación post-EDIT outreach v2

1. Crear lead test en Google Sheet con un teléfono trackeable.
2. Esperar Sheets Trigger del v2 (~1 min) + cron Touch 1 (~5 min).
3. Verificar:
   ```sql
   SELECT id, message->>'type' as type, LEFT(message->>'content', 80) as preview, created_at
   FROM n8n_chat_histories
   WHERE session_id = '<telefono sin +>'
   ORDER BY created_at;
   ```
4. Esperado: 2 rows — 1 system con datos del form, 1 ai con texto Touch 1.
5. Como el lead, responder por WhatsApp.
6. Esperado: agente responde sin "Hola, soy Mauricio de Venttur" y usa el nombre directo.

---

## EDIT #2 — `Rescate Post-Link` (workflowId `mkEP1qFN7MVb9qP0`)

### Estado actual

El workflow tiene 2 fases (45 min + 24 hrs) y routing por programa (6 programas × 2 fases = 12 sendFlows posibles). Cada sendFlow se ejecuta cuando el `Programa interés` matchea Y el lead no agendó cita.

### Cambio: insertar 1 Code + 2 Postgres después de cada sendFlow Fase 1 y solo 1 Code + 1 Postgres después de cada sendFlow Fase 2

Por simplicidad, recomiendo **consolidar el routing**: hacer que las 6 ramas de programa converjan en UN sub-flujo común que (a) detecte el programa y (b) inserte el ai message correspondiente. Pero esto requiere refactor del workflow.

**Versión MVP simple** (sin refactor): replicar los 3 nodos por cada uno de los 6 programas en Fase 1 (= 18 nodos nuevos) y 1 nodo por cada uno de los 6 programas en Fase 2 (= 6 nodos nuevos). Total: **24 nodos nuevos**. Tedioso pero directo.

**Versión preferida** (con Code centralizado):

#### Paso 1 — Crear nodo central `Build Rescate Memory (Fase 1)`

Insertar UNA sola vez, conectar las 6 salidas de los `sendFlow Fase 1` (uno por programa) a ESTE nodo.

- **Type:** `n8n-nodes-base.code` v2
- **JS:**

```javascript
// Build Rescate Memory Fase 1 — centralizado por programa
const lead = $('Get Lead').first().json;  // ajustar al nombre real del nodo Airtable que trae el lead
const sessionKey = (lead.Telefono || '').toString();
const programa = (lead['Programa interés'] || '').toString();
const firstName = (lead.Nombre || '').toString();

// === Builder de system message (mismo que outreach v2) ===
function buildSystemMessage(d) {
  const nombreCompleto = [d.Nombre, d.Apellido].filter(Boolean).join(' ').trim() || 'el lead';
  const email = d.Email ? d.Email : null;
  const tel = d.Telefono ? `tel +${d.Telefono}` : null;
  const contact = [email, tel].filter(Boolean).join(', ');
  const contactStr = contact ? ` (${contact})` : '';
  const origenMap = {
    'Form Meta': 'completó un formulario de Meta',
    'Form Landing': 'completó el formulario de nuestra landing',
    'CTWA': 'vino por un anuncio de WhatsApp',
  };
  const accion = origenMap[d.Origen] || 'mostró interés';
  const prog = d['Programa interés'] ? ` interesado/a en ${d['Programa interés']}` : ' interesado/a en uno de nuestros programas';
  const cualif = [
    d['Grado Escolar'] && `para ${d['Grado Escolar']}`,
    d['Inicio Deseado'] && `con inicio deseado en ${d['Inicio Deseado']}`,
    d['Nivel Inglés'] && `y nivel de inglés ${d['Nivel Inglés']}`,
  ].filter(Boolean).join(' ');
  const cualifStr = cualif ? ` ${cualif}` : '';
  const campania = d['Ad Name'] ? ` Vino por la campaña ${d['Ad Name']}${d.Platform ? ' en ' + d.Platform : ''}.` : '';
  return `El lead ${nombreCompleto}${contactStr} ${accion}${prog}${cualifStr}.${campania}`;
}

// === Texto Rescate Fase 1 por programa (de template-texts-canonical.md §4-9) ===
const RESCATE_F1 = {
  'Boarding School': `Hola {{first_name}}. Noté que solicitaste el enlace para platicar sobre Boarding School, pero el registro quedó pendiente. Si no encontraste un horario que se ajuste a tu agenda, avísame y reviso disponibilidad manual. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/agendar-ema`,
  'AA Familiar': `Hola {{first_name}}. Vi que pediste el enlace para la asesoría de Año Académico, pero la cita quedó en pausa. Si tuviste problemas con la plataforma o los horarios no te cuadran, escríbeme y lo resolvemos. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/AAFamilia-Agendar`,
  'Summer Camp': `Hola {{first_name}}. Solicitaste el acceso a la agenda para Summer Camp hace un momento. Si el calendario no te mostró horarios convenientes, dímelo y buscamos un espacio que te funcione. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/SummerCamp-Agendar`,
  'Pathway': `Hola {{first_name}}. Noté que pediste el enlace para la sesión de Pathway en Alemania. Si la plataforma te dio error o no encontraste disponibilidad, avísame por aquí para coordinarlo directo. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/PW_Alemania_Agendar`,
  'Estudio y Trabajo': `Hola {{first_name}}. Vi que solicitaste el calendario para Estudio y Trabajo. Si tuviste algún inconveniente técnico al intentar agendar o no te acomodan las horas, dime y lo reviso. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/EstudiaryTrabajar_Agendar`,
  'Gap Year': `Hola {{first_name}}. Solicitaste el enlace de asesoría para tu Gap Year en Australia. Si no encontraste un hueco en la agenda o se cerró el enlace, escríbeme y te ayudo a reservarlo. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/Estudiar-y-Trabajar-en-Australia`,
};

// Match por substring del programa
let template = '';
for (const key of Object.keys(RESCATE_F1)) {
  if (programa.includes(key)) {
    template = RESCATE_F1[key];
    break;
  }
}
// Fallback genérico
if (!template) {
  template = `Hola {{first_name}}. Vi que solicitaste el enlace de asesoría pero el registro quedó pendiente. Si tuviste algún inconveniente con la plataforma o los horarios, escríbeme y lo resolvemos.`;
}

const aiText = template.replace(/\{\{first_name\}\}/g, firstName || 'hola');

return [{ json: {
  session_key: sessionKey,
  system_message: { type: 'system', content: buildSystemMessage(lead) },
  ai_message: { type: 'ai', content: aiText },
}}];
```

#### Paso 2 — Crear `Insert system FORM (idempotent)` (Fase 1)

Mismo nodo Postgres que en outreach v2 (paso 2 de EDIT #1). Conectar después del `Build Rescate Memory (Fase 1)`.

#### Paso 3 — Crear `Insert ai Rescate Fase 1`

Idéntico al `Insert ai Touch 1` pero usando el `ai_message` del Build Rescate Memory.

#### Paso 4 — Repetir para Fase 2

Nodo `Build Rescate Memory (Fase 2)` con los 6 textos de Fase 2 (§10-15 del canonical doc) + `Insert ai Rescate Fase 2`. **No** hace falta repetir el `Insert system FORM` (ya se hizo en Fase 1 o en Touch 1 previo).

---

## Smoke tests

### S1 — Lead nuevo Form Meta, primer contacto

1. Crear row test en Google Sheet `Boarding_Schools_Venttur_2026-test-2`:
   - `phone`: `+5215555000001` (un número de prueba real al que podás recibir WA)
   - `full_name`: `Test Smoke Uno`
   - `grado_escolar`: `preparatoria`
   - `cuando_iniciar`: `agosto_2026`
   - `nivel_ingles`: `intermedio`
   - `lead_status`: vacío (Meta lo dejará en `CREATED` automáticamente)
2. Esperar Sheets Trigger del outreach v2 (~1 min) + cron Touch 1 (~5 min).
3. Verificar Postgres:
   ```sql
   SELECT id, message->>'type' as type, LEFT(message->>'content', 80) as preview
   FROM n8n_chat_histories
   WHERE session_id='5215555000001'
   ORDER BY created_at;
   ```
   Esperado: 2 rows — `system` con prosa del form, `ai` con texto Touch 1.
4. Como el lead, responder por WhatsApp: "Hola, sí me interesa".
5. **PASS si:** respuesta del agente NO incluye "Hola, soy Mauricio de Venttur", NO pide nombre, usa "Test Smoke Uno" directo y referencia Boarding School.

### S2 — Lead post-Touch 2

1. Setup: lead test con Touch 1 y Touch 2 ya enviados. Forzar via Airtable: `Toques enviados=2`, `Touch 1 programado at = NOW() - 25h`.
2. Esperar siguiente ciclo cron Outreach v2 (Touch 3 no debe disparar — falta tiempo).
3. Verificar Postgres: debe haber 3 rows (system + ai Touch 1 + ai Touch 2). Si solo hay 2, el EDIT del Touch 2 no se aplicó correctamente.
4. Responder al lead: "Sí, quiero info".
5. **PASS si:** agente NO re-saluda, retoma desde donde Touch 2 lo dejó.

### S3 — Lead rescate sin haber respondido al link

1. Setup: lead test con `Link asesoría enviado=true` hace 50 minutos, `Agendan cita=false`.
2. Esperar Fase 1 rescate (~5 min hasta que el workflow tick).
3. Verificar Postgres: rows del outreach previo + 1 nueva row `ai` con texto Rescate Fase 1.
4. Responder al rescate.
5. **PASS si:** agente reconoce que ya envió link, no re-presenta.

### S4 — Lead del backfill manual de hoy responde (post script Python)

1. Correr `python3 scripts/utilities/backfill-vtr-chat-memory.py --dry-run` y verificar el conteo.
2. Correr sin flag.
3. Tomar uno de los teléfonos contactados esta tarde, verificar en Postgres que tiene 2+ rows.
4. Coordinar con uno de esos leads para que responda (o usar un test phone que hayamos pasado a `contacted`).
5. **PASS si:** agente responde sin re-saludo.

---

## Rollback

Si algo sale mal:

```sql
-- Borrar todas las rows insertadas hoy por los nuevos nodos
DELETE FROM n8n_chat_histories
WHERE created_at > '2026-06-23 00:00:00'
  AND message->>'type' IN ('system', 'ai')
  AND id NOT IN (
    -- Excluir las que vinieron del agente directo (no son del backfill)
    SELECT id FROM n8n_chat_histories
    WHERE message->>'content' LIKE '%respondió el lead%'  -- ajustar según patrón identificable
  );
```

Y en n8n: desconectar (sin eliminar) los nodos nuevos en outreach v2 y rescate.

---

## Checklist de implementación

- [ ] Reemplazar `TOUCH_1_TEXT` en `Build Memory Texts (Touch 1)` con texto literal de ManyChat
- [ ] Reemplazar `[REEMPLAZAR_TOUCH_2_TEXT]` en `Insert ai Touch 2`
- [ ] Reemplazar `[REEMPLAZAR_TOUCH_3_TEXT]` en `Insert ai Touch 3`
- [ ] Verificar nodo `Get Lead` en rescate-post-link (nombre exacto puede variar) y ajustar referencia en `Build Rescate Memory`
- [ ] Import del `outreach-form-meta-backfill-v2.json` en n8n
- [ ] Correr S1 (smoke nuevo lead)
- [ ] Correr `backfill-vtr-chat-memory.py --dry-run` y verificar conteo
- [ ] Correr `backfill-vtr-chat-memory.py` para leads históricos
- [ ] Correr S2 (post-Touch 2)
- [ ] Correr S3 (rescate)
- [ ] Correr S4 (lead del backfill manual responde)
- [ ] Monitorear chats vivos durante 24h post-deploy para detectar re-saludos
