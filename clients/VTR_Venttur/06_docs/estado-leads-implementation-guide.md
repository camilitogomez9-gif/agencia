# Guía de implementación — Estado automático de leads (Venttur)

**Fecha:** 2026-05-26
**Objetivo:** reportar automáticamente en Airtable el estado de cada lead (`Contestó` / `Cita confirmada` / `Conversación interrumpida`) sin revisar conversación por conversación, usando **n8n** (no MAXIMUS ni un sistema externo).

---

## 1. Resumen de la solución

Arquitectura **n8n-centric**: los 3 eventos se resuelven dentro de n8n aprovechando lo que ya existe. **No se modifican los flujos de ManyChat.**

| Evento | De dónde sale | Cómo se implementa |
|--------|---------------|--------------------|
| **Contestó** | Cada mensaje del lead ya llega al webhook de `venttur-main` | Sub-workflow `wf-estado-lead` estampa `Estado conversación = Contestó` + `Última actividad` |
| **Cita confirmada** | Google Calendar (ya detectado por `confirmacion-agenda`) | Se agrega `Estado conversación = Cita confirmada` donde ya se setea `Agendan cita = true` |
| **Conversación interrumpida** | Silencio ≥ 24 h sin cita | Workflow programado `wf-estado-interrumpida` (barrido cada hora) |

Solo aplica a **leads nuevos/futuros**. Los históricos quedan como están (no hay forma automática de reconstruirlos).

### Máquina de estados (forward-only, con guardas)

```
(alta del lead) ──► Contestó ──────────────► Cita confirmada   [terminal de éxito]
                       │  ▲                          ▲
        24h silencio   │  │ vuelve a escribir        │ siempre gana
                       ▼  │                          │
              Conversación interrumpida ─────────────┘
```

Reglas (clave para que sea 100% correcto):
- **Contestó** nunca pisa a **Cita confirmada** (si `Agendan cita = true` o el estado ya es `Cita confirmada`, solo se actualiza `Última actividad`).
- **Cita confirmada** siempre gana.
- **Conversación interrumpida** solo se marca si pasó >24 h sin actividad y el lead no agendó. No se re-marca (idempotente).
- Re-enganche: un lead `Conversación interrumpida` que vuelve a escribir pasa a `Contestó`.

> **Clave de cruce = `Telefono`** (sin `+`). Se eligió `Telefono` y no `id_2` porque `Telefono` está poblado por **todos** los flujos de alta de lead (`crear-contacto` y `confirmacion-agenda`), mientras que `id_2` puede quedar vacío en leads que no pasaron por el flujo CAPI.

---

## 2. Orden de implementación

> Hacer los pasos **en este orden**. Activar el barrido (`wf-estado-interrumpida`) recién al final.

### Paso 0 — Crear 2 campos en Airtable (tabla **Leads**, base `[AIRTABLE_BASE_ID]` / `[AIRTABLE_TABLE_ID]`)

1. **`Estado conversación`** — tipo **Single select**. Crear estas 4 opciones (respetar tildes y mayúsculas exactas):
   - `Activa`
   - `Contestó`
   - `Cita confirmada`
   - `Conversación interrumpida`
2. **`Última actividad`** — tipo **Date**, con la opción **"Include time"** activada.

> Los nombres deben coincidir **exactamente** con los de los nodos. Hacer esto **antes** de importar/editar.

### Paso 1 — Importar `wf-estado-lead-venttur-v1.json`

- n8n → **Import from File** → `03_workflows/wf-estado-lead-venttur-v1.json`.
- Abrir los 2 nodos Airtable (`Buscar lead`, `Actualizar estado`) y confirmar que la credencial sea **Venttur Dashboard** (`[N8N_CREDENTIAL_ID]`).
- **Dejar inactivo** (es un sub-workflow, se ejecuta desde `venttur-main`).
- Qué hace: recibe `telefono`, busca el lead por `Telefono`, aplica la guarda y setea `Estado conversación` + `Última actividad`. Si no encuentra el lead, no hace nada (no-op).

### Paso 2 — Importar `wf-estado-interrumpida-venttur-v1.json`

- n8n → **Import from File** → `03_workflows/wf-estado-interrumpida-venttur-v1.json`.
- Confirmar credencial **Venttur Dashboard** en los 2 nodos Airtable (`Buscar inactivos`, `Marcar interrumpida`).
- El trigger `Cada hora` corre cada 1 h (ajustable). **No activar todavía** (se activa en el Paso 6).
- Qué hace: busca leads con `Última actividad` > 24 h, sin cita y no ya interrumpidos, y los marca `Conversación interrumpida`.

---

## 3. EDITs sobre workflows en vivo (a mano en n8n)

> Estos 3 workflows ya están en producción. Se editan **a mano** en n8n (no re-importar, para no duplicar ni perder credenciales). Después de cada cambio: **Save**.

### EDIT A — `venttur-main` (agente conversacional)
**Cubre "Contestó" en cada mensaje (a partir del 2º mensaje del lead).**

1. **Crear un nodo nuevo** `Execute Workflow`:
   - **Nombre:** `Estampar estado (Contestó)`
   - **Workflow:** seleccionar `Estado lead (Contestó) - Venttur` (el importado en el Paso 1).
   - **Options → Wait For Sub-Workflow Completion:** **OFF** (no bloqueante; la respuesta al lead ya se envió, no agrega latencia).
   - **Workflow Inputs → `telefono`:**
     ```
     {{ $('Responder rápido ManyChat').item.json.body.whatsapp_phone.replace('+','') }}
     ```
2. **Conectar:** arrastrar una conexión **desde** `Responder rápido ManyChat` **hacia** `Estampar estado (Contestó)`.
   - `Responder rápido ManyChat` ya tiene 2 salidas (`Buscar registro` y `Meta CAPI`); esto agrega una **3ª salida en paralelo**. **No borrar las existentes.**
3. **Save.**

### EDIT B — `crear-contacto-clientify-airtable` (alta de lead nuevo)
**Cubre "Contestó" en el primer mensaje** (cuando el lead todavía no existía en Airtable).

1. Abrir el nodo **`Crear o actualizar contacto`** (Airtable, upsert por `Telefono`, ya tiene `typecast` activo y setea `Contestan 1er mensaje`).
2. En **Fields to Send**, agregar 2 campos (sin tocar los existentes):
   - `Estado conversación` = `Contestó`
   - `Última actividad` = `{{ $now.toISO() }}`
3. **Save.**

### EDIT C — `confirmacion-agenda` (cita detectada por Google Calendar)
**Cubre "Cita confirmada".** Hay **2 nodos** Airtable que setean `Agendan cita = true` (uno para lead existente, otro para lead nuevo). Editar **ambos**:

1. Nodo **`Agendan cita = true`** (operation *update*, matchea por `ID Clientify`):
   - Agregar campo `Estado conversación` = `Cita confirmada`.
2. Nodo **`Crear contacto`** (operation *create*):
   - Agregar campo `Estado conversación` = `Cita confirmada`.
3. **Save.**

> Si alguno de estos 2 nodos no tiene `typecast` activo, igual funciona porque la opción `Cita confirmada` ya existe en el single-select (creada en el Paso 0).

---

## 4. Paso 6 — Activar el barrido

- Activar (toggle **Active**) el workflow `Estado interrumpida (barrido) - Venttur`.
- A partir de ahí, cada hora marcará como `Conversación interrumpida` los leads inactivos > 24 h sin cita.

---

## 5. Matriz de pruebas (validar antes de dar por cerrado)

Ejecutar en n8n con **"Execute workflow"** (pinned data) o con leads de prueba en Airtable.

| # | Caso | Cómo probar | Resultado esperado |
|---|------|-------------|--------------------|
| 1 | **Contestó** | Ejecutar `wf-estado-lead` con `{ "telefono": "<lead existente>" }` | `Estado conversación = Contestó`, `Última actividad` = ahora |
| 2 | **Guarda anti-downgrade** | Lead con `Agendan cita = true`; ejecutar `wf-estado-lead` con su teléfono | `Estado conversación` queda `Cita confirmada`; solo cambia `Última actividad` |
| 3 | **Cita confirmada (existente)** | Crear evento de prueba en el Calendar de un asesor para un lead que ya está en Airtable | `Agendan cita = true` **y** `Estado conversación = Cita confirmada` |
| 4 | **Cita confirmada (nuevo)** | Evento en Calendar para alguien que no estaba en Airtable | Se crea el lead con `Estado conversación = Cita confirmada` |
| 5 | **Interrumpida** | Lead con `Última actividad` > 24 h y sin cita; correr `wf-estado-interrumpida` manual | `Estado conversación = Conversación interrumpida` |
| 6 | **Idempotencia** | Volver a correr `wf-estado-interrumpida` | El lead del caso 5 no se vuelve a tocar; no aparecen duplicados |
| 7 | **Re-enganche** | Lead `Conversación interrumpida` → ejecutar `wf-estado-lead` con su teléfono | `Estado conversación = Contestó` |
| 8 | **E2E lead nuevo** | Enviar un WhatsApp real desde un número nuevo al bot | `Crear o actualizar contacto` deja `Estado = Contestó` + `Última actividad`; un 2º mensaje refresca `Última actividad` vía EDIT A |

---

## 6. Archivos relacionados

- `03_workflows/wf-estado-lead-venttur-v1.json` — sub-workflow "Contestó" (nuevo)
- `03_workflows/wf-estado-interrumpida-venttur-v1.json` — barrido de silencio (nuevo)
- `03_workflows/venttur-main-v1.json` — EDIT A
- `03_workflows/crear-contacto-clientify-airtable-venttur-v1.json` — EDIT B
- `03_workflows/confirmacion-agenda-venttur-v1.json` — EDIT C

---

## 7. Notas

- **Cero cambios en ManyChat.** Si más adelante se quiere un estado que solo ManyChat conoce, se agrega un webhook puntual hacia un sub-workflow nuevo.
- **Históricos:** quedan como están. El sistema empieza a poblar `Estado conversación` desde su activación, hacia adelante.
- El umbral de 24 h vive en el `filterByFormula` de `wf-estado-interrumpida` (`DATEADD(NOW(), -24, 'hours')`). Para cambiarlo, editar ese número.
