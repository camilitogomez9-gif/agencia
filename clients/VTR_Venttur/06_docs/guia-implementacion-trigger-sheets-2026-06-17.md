# Guía de Implementación — Trigger Google Sheets + Auditoría de Campos

> **Cliente:** VTR — Venttur · **Fecha:** 2026-06-17 · **Status:** Pre-implementación
> **Owner:** la agencia (la agencia) · **Workflow afectado:** `outreach-form-meta-venttur-v1` (`CUuFxbst3iHpgeXS`)
> **Resumen:** Reemplazar webhook del Flujo A por `googleSheetsTrigger` que poolea el sheet sincronizado por Meta Lead Ads + agregar 8 campos a Airtable Leads para cualificación y tracking + reutilizar 4 campos existentes con valores dinámicos derivados del sheet.

---

## 0. Convenciones

- 🟦 lo configura **Max** · 🟩 lo configura **la agencia** · ⚠️ decisión pendiente · ✅ listo
- Las menciones a workflowId, tabla, credenciales son las reales de la cuenta de Venttur

---

## 1. Decisiones de scope (qué SÍ, qué NO)

### ✅ Campos NUEVOS a crear en Airtable Leads (`[AIRTABLE_TABLE_ID]`)

| # | Campo | Tipo | Valores / Default | Justificación |
|---|-------|------|-------------------|---------------|
| 1 | `Grado Escolar` | Single-select | `primaria` / `secundaria` / `preparatoria` | Cualificación ORO #1 — discrimina edad estudiante + ticket promedio |
| 2 | `Inicio Deseado` | Single-select | `agosto_2026` / `enero_2027` / `agosto_2027` | Cualificación ORO #2 — dimensión #1 de urgencia |
| 3 | `Nivel Inglés` | Single-select | `básico` / `intermedio` / `avanzado` | Cualificación ORO #3 — discrimina viabilidad boarding US/UK |
| 4 | `Ad Name` | Single-select | `BS_PAPAS_TEST1` / `BS_MAMAS_TEST1` (agregar nuevos según aparezcan) | A/B PAPAS vs MAMAS, agrupador funnel |
| 5 | `Platform` | Single-select | `ig` / `fb` | Filtro analítico directo IG vs FB |
| 6 | `Touch 1 programado at` | Date with time (con hora) | seteado por n8n a `NOW()` (sin offset desde v4 — 2026-06-27) | **Crítico** — Cron pickea en el próximo ciclo de 5 min post-creación |
| 7 | `Lead Score` | Formula (number) | ver fórmula §2.2 | Routing diferenciado leads hot |
| 8 | `Tipo lead` | Formula (single-select-like) | `hot` / `warm` / `cold` derivado de Lead Score | Filtro para alerta Telegram + vista "Leads Calientes" |

### ✅ Campos EXISTENTES que cambian de uso (sin tocar schema)

| # | Campo | Antes | Ahora |
|---|-------|-------|-------|
| 9 | `Folio` | Hardcoded `"N/A (Form)"` | **`meta_lead_id` limpio** (sin prefijo `l:`) → dedup robusto + edge case fila 119 |
| 10 | `Fuente lead` | Hardcoded `"Facebook - Instagram"` | Derivado del `platform`: `"Instagram"` o `"Facebook"` (granularidad real) |
| 11 | `Tipo` | Hardcoded `"No especificado"` | Derivado del `ad_name`: `"Padre"` si contiene `PAPAS`, `"Madre"` si `MAMAS`, sino `"No especificado"` |
| 12 | `fbclid` | Hardcoded `"-"` | **BLANK** (fbclid no aplica a Form Meta, era ruido) |

### ✅ Vistas Airtable a crear (2)

| Vista | Filtro / Grouping | Para qué |
|-------|-------------------|----------|
| `Funnel Performance` | Group by `Ad Name` × `Platform`, todos los leads `Origen = Form Meta` | Reporting diario Max — tasa respuesta/cita por ad |
| `Leads Calientes` | Filter `Tipo lead = "hot"` AND `Agendan cita = false`, sort `Creada` DESC | Intervención manual + alerta Telegram |

### ✅ Alerta a crear (1)

| Alerta | Cuándo | A quién |
|--------|--------|---------|
| Lead hot entrante | Lead nuevo con `Tipo lead = "hot"` | Telegram Max < 1h |

### ❌ Cortes vs propuesta original (justificación en encabezado)

- ❌ Campo `Campaign Name` (1 campaña activa, estático)
- ❌ Campo `Form Name` (1 form activo, estático)
- ❌ Campo `Lead Status Meta` (no se usa operativamente)
- ❌ Campo `Form Meta created_time` (polling 1min → < 1min de diferencia con `Creada`)
- ❌ Campo `Veces reprocesado por sheet trigger` (con `rowAdded` no debería pasar)
- ❌ Tabla nueva `Ads Meta` (alcanza una vista con groupBy)
- ❌ Tabla nueva `Leads_Errores` (reusar sub-flujo Supabase `workflow_errors`)
- ❌ Alerta "ad < 10%" + alerta "> 5 leads sin outreach" (posponer 4 semanas)

---

## 2. Fórmulas Airtable listas para copiar

### 2.1. `Lead Score` (formula → number)

```
({Inicio Deseado} = 'agosto_2026') * 50 +
({Inicio Deseado} = 'enero_2027') * 30 +
({Inicio Deseado} = 'agosto_2027') * 10 +
({Nivel Inglés} = 'avanzado') * 30 +
({Nivel Inglés} = 'intermedio') * 20 +
({Nivel Inglés} = 'básico') * 10 +
({Grado Escolar} = 'preparatoria') * 20 +
({Grado Escolar} = 'secundaria') * 15 +
({Grado Escolar} = 'primaria') * 10
```

Output range: 0–100. Hipótesis inicial de pesos — recalibrar a 4-8 semanas con data real de conversión.

### 2.2. `Tipo lead` (formula → string)

```
IF({Lead Score} >= 70, 'hot', IF({Lead Score} >= 50, 'warm', 'cold'))
```

---

## 3. Roadmap por fases

### Fase 0 — Pre-flight (~1h) 🟦🟩

- 🔲 🟦 **Max:** confirmar que la cuenta Google que tiene acceso al sheet sincronizado por Meta es **OWNER** (no editor). El sync de Meta a veces invalida acceso a colaboradores en pushes grandes.
- 🔲 🟦 **Max:** confirmar **Document ID** del sheet (URL `docs.google.com/spreadsheets/d/<ID>/edit`) y **Sheet Name** (el tab name, probable `Boarding_Schools_Venttur_2026-test-2` según filename del CSV).
- 🔲 🟦 **Max:** confirmar si quiere conservar `Programa interés = "Boarding School"` hardcoded por ahora (solo hay 1 form). Si lanza 2do form, esto mappea desde `form_name`.
- 🔲 🟩 **la agencia:** duplicar el workflow `CUuFxbst3iHpgeXS` como backup `"Outreach Form Meta - Venttur v1 PRE-TRIGGER-CHANGE"`.
- 🔲 🟩 **la agencia:** snapshot del JSON actual al repo como `outreach-form-meta-venttur-v1-pre-trigger-backup.json`.
- 🔲 🟩 **la agencia:** verificar header literal del Google Sheet (las 20 columnas exactas, sin asumir).

---

### Fase 1 — Setup Airtable (~1.5h) 🟩

#### 1.1. Crear los 6 single-selects + 1 datetime

En tabla `Leads` (`[AIRTABLE_TABLE_ID]`), agregar:

| Campo | Tipo | Opciones |
|-------|------|----------|
| `Grado Escolar` | Single-select | `primaria`, `secundaria`, `preparatoria` |
| `Inicio Deseado` | Single-select | `agosto_2026`, `enero_2027`, `agosto_2027` |
| `Nivel Inglés` | Single-select | `básico`, `intermedio`, `avanzado` (con acento) |
| `Ad Name` | Single-select | `BS_PAPAS_TEST1`, `BS_MAMAS_TEST1` (activar "Allow new options" para que n8n cree los nuevos automáticamente con typecast) |
| `Platform` | Single-select | `ig`, `fb` |
| `Touch 1 programado at` | Date with time | — |

#### 1.2. Crear las 2 fórmulas

| Campo | Tipo | Fórmula |
|-------|------|---------|
| `Lead Score` | Formula (number) | ver §2.1 |
| `Tipo lead` | Formula | ver §2.2 |

#### 1.3. Verificar las opciones del select `Origen`

Ya tiene `Form Meta` ✅, sin cambios.

#### 1.4. Verificar las opciones del select `Fuente lead`

Debe existir `Instagram` y `Facebook` como opciones del select (hoy hay `Facebook - Instagram` que es la mezcla). Si no existen, agregarlas. NO eliminar `Facebook - Instagram` (leads históricos lo usan).

#### 1.5. Crear las 2 vistas

**Vista `Funnel Performance`:**
- Type: Grid view
- Group by 1: `Ad Name`
- Group by 2: `Platform`
- Filter: `Origen = Form Meta`
- Mostrar columnas: Ad Name, Platform, Nombre, Telefono, Outreach Form Meta enviado, Contestan 1er mensaje, Agendan cita, Creada
- Summary bar: count en cada columna boolean

**Vista `Leads Calientes`:**
- Type: Grid view
- Filter: `Tipo lead = "hot"` AND `Agendan cita = false` AND `Estado conversación` ≠ `Cita confirmada`
- Sort: `Creada` DESC
- Mostrar columnas: Nombre, Telefono, Email, Grado Escolar, Inicio Deseado, Nivel Inglés, Lead Score, Ad Name, Platform, Creada

#### 1.6. Smoke test manual de fórmulas

Insertar 1 record manual con:
- `Grado Escolar` = preparatoria
- `Inicio Deseado` = agosto_2026
- `Nivel Inglés` = avanzado

→ verificar `Lead Score = 100` y `Tipo lead = "hot"`.

Otro record con grado primaria + agosto_2027 + básico → `Lead Score = 30` y `Tipo lead = "cold"`. Confirmar ambos antes de seguir.

---

### Fase 2 — Credencial Google Sheets OAuth2 + nodo trigger (~1h) 🟩

#### 2.1. Habilitar APIs

En Google Cloud Console del proyecto la agencia:
- Habilitar **Google Sheets API**
- Habilitar **Google Drive API** (necesario para el dropdown __rl del nodo)

#### 2.2. Crear OAuth2 Client (si no existe ya)

- Tipo: Web application
- Authorized redirect URI: `https://[TU-INSTANCIA-N8N]/rest/oauth2-credential/callback`

#### 2.3. Crear credencial en n8n

- New Credential → **Google Sheets OAuth2 API**
- Nombre: `Google Sheets - Venttur Meta Sync`
- Client ID + Secret del paso 2.2
- Autorizar con la cuenta Google **OWNER** del sheet
- Validar que el dropdown "Document" liste el sheet de Meta

#### 2.4. Agregar el nodo trigger al workflow

Bloque JSON listo para copiar/pegar (reemplazar `__REEMPLAZAR_DOCUMENT_ID__` con el ID real del sheet):

```json
{
  "parameters": {
    "pollTimes": {
      "item": [
        {
          "mode": "everyMinute"
        }
      ]
    },
    "documentId": {
      "__rl": true,
      "value": "__REEMPLAZAR_DOCUMENT_ID__",
      "mode": "list"
    },
    "sheetName": {
      "__rl": true,
      "value": "Boarding_Schools_Venttur_2026-test-2",
      "mode": "list"
    },
    "event": "rowAdded",
    "options": {
      "valueRender": "UNFORMATTED_VALUE",
      "dataLocationOnSheet": {
        "values": {
          "rangeDefinition": "detectAutomatically",
          "headerRow": 1
        }
      }
    }
  },
  "id": "c1111111-1111-1111-1111-111111111111",
  "name": "Sheets Trigger - Form Meta Sync",
  "type": "n8n-nodes-base.googleSheetsTrigger",
  "typeVersion": 1,
  "position": [-128, 384],
  "credentials": {
    "googleSheetsTriggerOAuth2Api": {
      "id": "__REEMPLAZAR_CREDENCIAL_ID__",
      "name": "Google Sheets - Venttur Meta Sync"
    }
  }
}
```

**No conectar todavía** — solo agregar el nodo. La conexión va en Fase 4.

#### 2.5. Sticky note explicativa

Al lado del nodo, agregar sticky con:

> ⚠️ **Event=rowAdded INTENCIONAL.** El sheet muta `lead_status` CREATED→contacted post-inserción. Usar `rowAddedOrUpdated` causaría duplicados/resets en Airtable. Si se necesita capturar updates en el futuro, abrir workflow separado con dedup por `meta_lead_id`.

---

### Fase 3 — Refactor Normalize Payload + nodos Airtable (~2-3h) 🟩

#### 3.1. Reescribir `Normalize Payload` (Code node)

Reemplazar el `jsCode` actual con esto (listo para pegar):

```javascript
// Normalize Payload — versión Google Sheets Trigger
// Input shape: cada item es una fila del sheet sincronizado por Meta
// El trigger emite N items por poll si entran N filas → procesar TODOS

const items = $input.all();
const results = [];

// --- Helpers ---

const stripMetaPrefix = (v) => (v || '').toString().replace(/^[a-z]+:/, '').trim();

const titleCase = (s) => (s || '')
  .toString()
  .toLowerCase()
  .replace(/(^|\s|-)\p{L}/gu, c => c.toUpperCase());

const splitName = (full) => {
  const trimmed = (full || '').toString().trim();
  if (!trimmed) return { nombre: 'Lead', apellido: '' };
  const parts = trimmed.split(/\s+/);
  return {
    nombre: titleCase(parts[0]),
    apellido: parts.length > 1 ? titleCase(parts.slice(1).join(' ')) : ''
  };
};

// parsePhone: maneja 3 formatos del sheet
//   1) "p:+5215512345678" (con prefijo p:+)
//   2) "5215512345678"   (raw sin prefijo)
//   3) "p:MX" o basura   → invalid
const parsePhone = (raw) => {
  if (!raw) return { valid: false };
  const cleaned = raw.toString().replace(/^p:\+?/, '').replace(/[^0-9]/g, '');
  if (cleaned.length < 10 || cleaned.length > 15) {
    return { valid: false };
  }
  return { valid: true, phoneNoPlus: cleaned, phoneWithPlus: '+' + cleaned };
};

const deriveTipo = (adName) => {
  const upper = (adName || '').toString().toUpperCase();
  if (upper.includes('PAPAS') || upper.includes('PAPÁS')) return 'Padre';
  if (upper.includes('MAMAS') || upper.includes('MAMÁS')) return 'Madre';
  return 'No especificado';
};

const deriveFuente = (platform) => {
  const p = (platform || '').toString().toLowerCase();
  if (p === 'ig' || p === 'instagram') return 'Instagram';
  if (p === 'fb' || p === 'facebook') return 'Facebook';
  return 'Facebook - Instagram';
};

// --- Loop principal ---

for (const item of items) {
  const row = item.json;

  // Phone: priorizar `whatsapp` (más limpio en el sheet), fallback `phone_number`
  let phoneResult = parsePhone(row.whatsapp);
  if (!phoneResult.valid) {
    phoneResult = parsePhone(row.phone_number);
  }

  // Si phone inválido (ej. fila 119 con whatsapp='' y phone_number='p:MX'),
  // marcar para rama _error en lugar de throw (no abortar el batch entero)
  if (!phoneResult.valid) {
    results.push({
      json: {
        _error: true,
        _error_reason: 'Phone inválido: whatsapp="' + (row.whatsapp || '') +
                       '" phone_number="' + (row.phone_number || '') + '"',
        _meta_lead_id: stripMetaPrefix(row.id),
        _row_number: row.row_number,
        _raw_row: row
      }
    });
    continue;
  }

  const { nombre, apellido } = splitName(row.full_name);

  // Touch 1 programado at = NOW() — el Cron pickea en el próximo ciclo de 5 min
  // (desde v4 — 2026-06-27 — antes era NOW() + 1h y bloqueaba al lead 1h post-creación)
  const touch1At = new Date().toISOString();

  results.push({
    json: {
      _error: false,

      // Identificación
      meta_lead_id: stripMetaPrefix(row.id), // → Folio en Airtable

      // Datos del lead
      telefono: phoneResult.phoneNoPlus, // sin +, como en Airtable
      telefono_con_plus: phoneResult.phoneWithPlus, // con + para ManyChat
      nombre,
      apellido,
      email: (row.email || '').toString().trim().toLowerCase(),

      // Tracking Meta (campos nuevos)
      ad_name: (row.ad_name || '').toString(),
      platform: (row.platform || '').toString().toLowerCase(),

      // Cualificación ORO (campos nuevos)
      grado_escolar: (row.grado_escolar || '').toString(),
      inicio_deseado: (row.cuando_iniciar || '').toString(),
      nivel_ingles: (row.nivel_ingles || '').toString(),

      // Derivados (reutilizan campos existentes, no se crean nuevos)
      tipo: deriveTipo(row.ad_name),
      fuente_lead: deriveFuente(row.platform),

      // Cadencia
      touch_1_programado_at: touch1At,

      // Defaults / origen
      origen: 'Form Meta',
      received_at: new Date().toISOString()
    }
  });
}

return results;
```

#### 3.2. Agregar nodo IF post-Normalize para rutear errores

Nuevo nodo `IF` después de Normalize:
- Condición: `{{ $json._error }} === true`
- Rama TRUE → nodo Execute Workflow al sub-flujo `webapp_errors` (`OBkUyb8fuo30DzA9`) con shape plano:
  - `workflow_id`: `={{ $workflow.id }}`
  - `workflow_name`: `={{ $workflow.name }}`
  - `execution_id`: `={{ $execution.id }}`
  - `execution_url`: `={{ 'https://[TU-INSTANCIA-N8N]/workflow/' + $workflow.id + '/executions/' + $execution.id }}`
  - `error_message`: `={{ $json._error_reason }}`
  - `error_stack`: `={{ JSON.stringify($json._raw_row, null, 2) }}`
- Rama FALSE → continúa al Split In Batches

#### 3.3. Agregar `Split In Batches` post-Normalize (anti-flood)

Entre el IF (rama FALSE) y `Buscar Lead Existente`, agregar:

```json
{
  "parameters": {
    "batchSize": 1,
    "options": {
      "reset": false,
      "batchInterval": 12000
    }
  },
  "type": "n8n-nodes-base.splitInBatches",
  "typeVersion": 3,
  "name": "Split In Batches Flujo A (anti-flood)"
}
```

`batchInterval: 12000` = espera 12s entre items. Protege contra burst si el workflow estuvo desactivado y se acumularon 50+ filas (rate limit Airtable 5 req/s).

#### 3.4. Modificar `Buscar Lead Existente`

Cambiar el `filterByFormula` para priorizar match por `Folio` (lead_id Meta, inmutable) sobre `Telefono`:

```
=OR({Folio} = '{{ $json.meta_lead_id }}', {Telefono} = '{{ $json.telefono }}')
```

Y agregar al array `fields`: `Folio`.

#### 3.5. Cambiar `Crear Lead Nuevo` a `performUpsert`

En el nodo `Crear Lead Nuevo`:
- `operation`: `upsert` (n8n typeVersion 2.1)
- `columns.matchingColumns`: `["Folio"]` (primary match por meta_lead_id)
- Mapping actualizado:

```json
{
  "Nombre": "={{ $('Normalize Payload').item.json.nombre }}",
  "Apellido": "={{ $('Normalize Payload').item.json.apellido }}",
  "Telefono": "={{ $('Normalize Payload').item.json.telefono }}",
  "Email": "={{ $('Normalize Payload').item.json.email }}",
  "Programa interés": "Boarding School",
  "Origen": "Form Meta",
  "Outreach Form Meta enviado": false,
  "Contestan 1er mensaje": false,
  "Folio": "={{ $('Normalize Payload').item.json.meta_lead_id }}",
  "Fuente lead": "={{ $('Normalize Payload').item.json.fuente_lead }}",
  "Tipo": "={{ $('Normalize Payload').item.json.tipo }}",
  "Ad Name": "={{ $('Normalize Payload').item.json.ad_name }}",
  "Platform": "={{ $('Normalize Payload').item.json.platform }}",
  "Grado Escolar": "={{ $('Normalize Payload').item.json.grado_escolar }}",
  "Inicio Deseado": "={{ $('Normalize Payload').item.json.inicio_deseado }}",
  "Nivel Inglés": "={{ $('Normalize Payload').item.json.nivel_ingles }}",
  "Toques enviados": 0,
  "Touch 1 programado at": "={{ $('Normalize Payload').item.json.touch_1_programado_at }}"
}
```

**Eliminar del mapping**: `Meta lead_id` (ahora vive en `Folio`), `Meta form_id`, `fbclid: "-"`.

#### 3.6. Modificar `Actualizar Lead Existente` con IF gate

**Antes del `Actualizar Lead Existente`**, agregar IF que solo permita update si el lead NO está en proceso:

```json
{
  "conditions": {
    "options": { "typeValidation": "loose", "version": 2 },
    "conditions": [
      {
        "leftValue": "={{ $json['Outreach Form Meta enviado'] }}",
        "rightValue": false,
        "operator": { "type": "boolean", "operation": "equals" }
      },
      {
        "leftValue": "={{ $json['Toques enviados'] || 0 }}",
        "rightValue": 0,
        "operator": { "type": "number", "operation": "equals" }
      }
    ],
    "combinator": "and"
  },
  "name": "¿Lead seguro de actualizar?"
}
```

Mapping del `Actualizar Lead Existente` **solo campos inmutables/seguros** (NUNCA tocar `Toques enviados`, `Outreach Form Meta enviado`, `Última actividad`, `Estado conversación`):

```json
{
  "id_2": "={{ $json.id_2 }}",
  "Folio": "={{ $('Normalize Payload').item.json.meta_lead_id }}",
  "Origen": "Form Meta",
  "Ad Name": "={{ $('Normalize Payload').item.json.ad_name }}",
  "Platform": "={{ $('Normalize Payload').item.json.platform }}",
  "Grado Escolar": "={{ $('Normalize Payload').item.json.grado_escolar }}",
  "Inicio Deseado": "={{ $('Normalize Payload').item.json.inicio_deseado }}",
  "Nivel Inglés": "={{ $('Normalize Payload').item.json.nivel_ingles }}"
}
```

#### 3.7. Modificar `filterByFormula` del Cron (Flujo B)

Reemplazar el filtro actual (que usa `CREATED_TIME()`) con uno que usa `Touch 1 programado at`:

```
=AND({Origen} = 'Form Meta', NOT({Agendan cita}), {Última actividad} = BLANK(), {Toques enviados} < 3, {Touch 1 programado at}, OR(AND({Toques enviados} = 0, IS_AFTER(NOW(), {Touch 1 programado at})), AND({Toques enviados} = 1, IS_AFTER(NOW(), DATEADD({Touch 1 programado at}, 24, 'hours'))), AND({Toques enviados} = 2, IS_AFTER(NOW(), DATEADD({Touch 1 programado at}, 72, 'hours')))))
```

Cambios:
- `CREATED_TIME()` → `{Touch 1 programado at}`
- `IS_BEFORE(X, DATEADD(NOW(), -N, ...))` → `IS_AFTER(NOW(), DATEADD({Touch 1 programado at}, N, ...))` (más limpio, mismo significado)
- Para Touch 1: simplificado a `IS_AFTER(NOW(), {Touch 1 programado at})` directamente (`Touch 1 programado at` = NOW() en v4 → el Cron pickea en el próximo ciclo de 5 min)
- Agregada guarda `{Touch 1 programado at}` (no-blank) para excluir leads viejos pre-migración

Agregar `Touch 1 programado at` al array `fields` del Get Leads Pendientes.

---

### Fase 4 — Cablear + smoke test pre-deploy (~1.5h) 🟩

#### 4.1. Topología nueva del Flujo A

```
Sheets Trigger ──► Normalize Payload ──► IF (_error?)
                                            │
                                          FALSE
                                            │
                                            ▼
                                       Split In Batches (anti-flood)
                                            │
                                            ▼
                                       Buscar Lead Existente
                                            │
                                            ▼
                                       ¿Lead Existe?
                                          │   │
                                       TRUE   FALSE
                                          ▼      ▼
                                  ¿Lead seguro   Crear Lead Nuevo (upsert)
                                  actualizar?
                                       │ TRUE
                                       ▼
                              Actualizar Lead Existente

                                            ▲
IF (_error?) ──TRUE──► Execute Workflow ── webapp_errors (sub-flujo)
```

#### 4.2. Eliminar nodos viejos

- 🔲 Eliminar nodo `Webhook Form Meta` (id `24c152b4-8077-4151-a114-389c34a46d5f`)
- 🔲 Eliminar nodo `Respond rápido (200)` (id `9aae6a66-3c70-4666-a53b-afff4fc4d3d3`)

> Renombrar el `path` del webhook viejo a `vtr-form-meta-outreach-LEGACY-DO-NOT-USE` **NO aplica** porque eliminamos el webhook entero. Si Max conserva alguna integración apuntando al path viejo, se rompe explícitamente (cosa deseada — exposes reconfig pendiente).

#### 4.3. 3 casos de smoke test

**Caso A — Happy path (lead típico)**

Insertar manualmente esta fila en el sheet de Meta (o esperar a un lead real):

| Columna | Valor |
|---------|-------|
| id | `l:9999999999999999` |
| created_time | `2026-06-17T10:00:00-05:00` |
| ad_name | `BS_PAPAS_TEST1` |
| platform | `ig` |
| grado_escolar | `preparatoria` |
| cuando_iniciar | `agosto_2026` |
| nivel_ingles | `avanzado` |
| email | `smoke.a@test.com` |
| full_name | `la agencia Test Smoke` |
| phone_number | `p:59899999999` (tu teléfono) |
| whatsapp | `59899999999` |
| lead_status | `CREATED` |

Esperar < 2min (polling 1min). Verificar en Airtable Leads:
- ✅ Row creada con `Folio = "9999999999999999"`, `Telefono = "59899999999"`, `Origen = "Form Meta"`
- ✅ `Tipo = "Padre"` (derivado de PAPAS), `Fuente lead = "Instagram"` (derivado de ig)
- ✅ `Ad Name = "BS_PAPAS_TEST1"`, `Platform = "ig"`
- ✅ `Grado Escolar = "preparatoria"`, `Inicio Deseado = "agosto_2026"`, `Nivel Inglés = "avanzado"`
- ✅ `Lead Score = 100`, `Tipo lead = "hot"`
- ✅ `Touch 1 programado at` = aproximadamente `NOW() + 1h`
- ✅ `Toques enviados = 0`, `Outreach Form Meta enviado = false`

**Caso B — Edge case (fila 119 simulada)**

Insertar fila con `phone_number = "p:MX"` y `whatsapp = ""` (vacío).

Verificar:
- ✅ El IF de error dispara → Execute Workflow al sub-flujo `webapp_errors`
- ✅ NO se crea fila en Airtable Leads
- ✅ Aparece registro en Supabase `workflow_errors` con `error_message` = "Phone inválido: whatsapp=\"\" phone_number=\"p:MX\""
- ✅ El batch sigue procesando los demás items sin abortar

**Caso C — Lead duplicado (dedup por Folio)**

Insertar la MISMA fila del Caso A otra vez (mismo `id`).

Verificar:
- ✅ `Buscar Lead Existente` matchea por `Folio`
- ✅ `¿Lead seguro actualizar?` evalúa `Outreach Form Meta enviado = false AND Toques enviados = 0` → TRUE
- ✅ `Actualizar Lead Existente` NO toca `Toques enviados` ni `Outreach Form Meta enviado`
- ✅ Sigue habiendo 1 sola row para ese lead

**Caso D — Lead duplicado pero ya procesado**

Manualmente en Airtable setear `Outreach Form Meta enviado = true` en el lead del Caso A. Insertar la fila otra vez en el sheet.

Verificar:
- ✅ `Buscar Lead Existente` matchea
- ✅ `¿Lead seguro actualizar?` evalúa FALSE (porque `Outreach Form Meta enviado = true`)
- ✅ NO se ejecuta el Actualizar → estado del lead protegido

#### 4.4. Bumpear versión

- 🔲 Exportar workflow → guardar como `clients/VTR_Venttur/03_workflows/outreach-form-meta-venttur-v2.json`
- 🔲 Commit: `sync(VTR): v2 con trigger Google Sheets + 8 campos nuevos + dedup Folio`

---

### Fase 5 — Activación + monitoreo 48h (~1h setup + pasivo) 🟩

#### 5.1. Pre-activación checklist

- 🔲 Backup del workflow existente confirmado en n8n + repo
- 🔲 Campos Airtable creados, fórmulas validadas con smoke manual
- 🔲 Credencial Google Sheets autorizada
- 🔲 Workflow nuevo con todos los nodos cableados
- 🔲 Smoke A/B/C/D pasaron

#### 5.2. Activación

1. Desactivar el workflow viejo (mantener para rollback rápido — NO eliminar)
2. Activar el workflow nuevo `outreach-form-meta-venttur-v2`
3. Notificar a Max que el switch está hecho

#### 5.3. Monitoreo primeras 24h

Query Airtable diario:
- Count leads nuevos `Origen = Form Meta` últimas 24h
- Comparar contra count filas sheet en mismo periodo
- **Alertar si difieren > 5%** → hueco de procesamiento

Query Airtable a las 48h:
- Para leads creados últimas 48h con `Outreach Form Meta enviado = true`:
  - Calcular DIFF = `Outreach Form Meta enviado at` − `Creada`
  - **p95 debe estar en [60min, 70min]**
  - Si está en [5min, 15min] → race condition NO resuelto (revisar filterByFormula)

#### 5.4. Quota Sheets API

En Google Cloud Console:
- Verificar % de uso de read requests
- Polling 1min = 1440 reads/día — bien bajo del límite (60/min usuario, 300/min proyecto)
- Alertar si > 70% → reducir polling a everyXMinutes con value 2

---

### Fase 6 — Alerta Telegram lead hot (post-validación 48h) 🟩

Crear workflow nuevo `venttur-alerta-lead-hot`:

- Trigger: Airtable Trigger (record updated) en tabla Leads
- Filter: `Tipo lead = "hot"` AND `Notificacion lead hot enviada = false`
- Action 1: Telegram a Max con datos del lead + link al record en Airtable
- Action 2: Update Airtable → `Notificacion lead hot enviada = true`

Requiere agregar **1 campo más** en Leads: `Notificacion lead hot enviada` (boolean, default false). Justifica sumarlo solo si Max confirma que quiere la alerta.

⚠️ **Decisión de Max:** ¿quiere la alerta para v1 o esperar a tener data de cuántos leads "hot" entran por día?

---

## 4. Resumen de cambios consolidado

### Airtable Leads (`[AIRTABLE_TABLE_ID]`)

| Acción | Campo | Tipo |
|--------|-------|------|
| NUEVO | `Grado Escolar` | Single-select |
| NUEVO | `Inicio Deseado` | Single-select |
| NUEVO | `Nivel Inglés` | Single-select |
| NUEVO | `Ad Name` | Single-select |
| NUEVO | `Platform` | Single-select |
| NUEVO | `Touch 1 programado at` | Date with time |
| NUEVO | `Lead Score` | Formula (number) |
| NUEVO | `Tipo lead` | Formula |
| CAMBIO USO | `Folio` | text → guarda `meta_lead_id` |
| CAMBIO USO | `Fuente lead` | derivado de `platform` |
| CAMBIO USO | `Tipo` | derivado de `ad_name` |
| CAMBIO USO | `fbclid` | dejar BLANK |
| NUEVA VISTA | `Funnel Performance` | groupBy Ad Name × Platform |
| NUEVA VISTA | `Leads Calientes` | filter Tipo lead = hot |

### n8n Workflow `outreach-form-meta-venttur` (v1 → v2)

| Nodo | Acción |
|------|--------|
| `Webhook Form Meta` | ELIMINAR |
| `Respond rápido (200)` | ELIMINAR |
| `Sheets Trigger - Form Meta Sync` | NUEVO |
| `Normalize Payload` | REESCRIBIR jsCode completo |
| `IF (_error?)` | NUEVO |
| `Execute Workflow webapp_errors` | NUEVO (rama TRUE del IF) |
| `Split In Batches Flujo A` | NUEVO (anti-flood) |
| `Buscar Lead Existente` | MODIFICAR filterByFormula (match por Folio OR Telefono) |
| `Crear Lead Nuevo` | CAMBIAR a `upsert` + mapping nuevo con 8 campos |
| `¿Lead seguro actualizar?` | NUEVO IF gate |
| `Actualizar Lead Existente` | MODIFICAR mapping (solo inmutables) |
| `Get Leads Pendientes` (Flujo B) | MODIFICAR filterByFormula a usar `Touch 1 programado at` |

---

## 5. Riesgos consolidados — top 5

| Riesgo | Severidad | Mitigación |
|--------|-----------|------------|
| Race condition trigger vs cron | 🟢 mitigada en v4 | `Touch 1 programado at` = NOW() — el Cron pickea recién en el próximo ciclo de 5 min, no hay carrera con la inserción |
| Modo `rowAddedOrUpdated` reprocesa mutación lead_status | 🔴 critical | `event='rowAdded'` estricto + IF gate en Actualizar Lead + mapping sin campos volátiles |
| Webhook viejo recibe tráfico | 🟠 high | Eliminar físicamente del JSON (no dejar huérfano desactivado) |
| Drift schema del sheet (Meta agrega columna) | 🟠 high | Bracket-notation con keys literales (ya implementado en jsCode) — fallará gracioso si key no existe |
| Flood en reactivación (50 filas acumuladas) | 🟠 high | `Split In Batches` batchSize=1 wait=12s + `upsert` por Folio (idempotencia) |

---

## 6. Effort total estimado

| Fase | Effort |
|------|--------|
| 0 — Pre-flight | 1h |
| 1 — Airtable | 1.5h |
| 2 — OAuth2 + trigger | 1h |
| 3 — Refactor n8n | 2-3h |
| 4 — Cablear + smoke | 1.5h |
| 5 — Activación + monitoreo | 1h setup + 48h pasivo |
| 6 — Alerta Telegram (opcional v1) | 1h |
| **Total** | **8-10h activas + 48h monitoreo pasivo** |

---

## 7. Historial

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-06-17 | Guía inicial — audit adversarial de campos (8 nuevos vs 12 originales) + plan de implementación en 6 fases | la agencia + Claude |
