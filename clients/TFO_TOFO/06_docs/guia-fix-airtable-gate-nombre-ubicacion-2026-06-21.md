# Guía de deploy — Fix Airtable Gate Nombre + Ubicación (2026-06-21)

**Objetivo:** dejar de generar registros vacíos ("contacto a redes sociales") en Airtable. A partir de este fix, un lead solo se crea en Airtable cuando **escribió en el chat su nombre + su ubicación** (criterio Mauricio reunión 18/6/26).

**Contexto:** Mauricio reportó que del renglón 488+ en adelante todos los leads en Airtable dicen "contacto a redes sociales" sin nombre ni ubicación. Causa raíz: el main workflow tenía un nodo `Crear contacto inicial` que escribía un record vacío automáticamente apenas un subscriber nuevo mandaba el primer mensaje, sin esperar a que la conversación cualificara nada. Este fix lo elimina y deja la responsabilidad de crear/actualizar el registro en manos de la tool `registrar` que los subagentes B2B y RRSS ya tenían cableada — pero ahora con un gate explícito que solo permite invocarla cuando hay nombre + ubicación.

**Artefactos generados:**
- `clients/TFO_TOFO/03_workflows/agente-tofo-web-b2b-rrss-v4.json` — snapshot final post-fix (47 nodos = 50 prod − 3 eliminados)
- `clients/TFO_TOFO/04_agents/agente-tofo-b2b-system-prompt.md` — v1.10 (vivo). Backup v1.9 preservado
- `clients/TFO_TOFO/04_agents/agente-tofo-rrss-system-prompt.md` — v1.6 (vivo). Backup v1.5 preservado

---

## Qué cambia exactamente

### En el workflow `Agente WEB B2B y RRSS` (n8n vivo)

**3 nodos eliminados:**
1. `Existe?` (Airtable search por `ID Manychat`)
2. `¿Existe?` (IF que routeaba según el resultado del search)
3. `Crear contacto inicial` (Airtable create con `Estado = "Contacto RRSS/WhatsApp"`) ← **el causante real del problema**

**1 conexión nueva:**
- `Code in JavaScript` → `Separamos en partes` (reemplaza la cadena `Existe? → ¿Existe? → Separamos en partes`)

**1 campo agregado al nodo `registrar`:**
- `Canal` con valor `={{ $('Code in JavaScript').first().json.canal }}` (determinístico, NO LLM). Antes este campo lo escribía `Crear contacto inicial` y se perdía al borrarlo; ahora lo escribe `registrar` cuando se activa.

**Topología final del entry path:**
```
Webhook → Responder rápido ManyChat → Code in JavaScript → Separamos en partes → ... (resto del flujo intacto)
```

### En los prompts (B2B y RRSS)

Ambos prompts ganan un **GATE** explícito al principio de la sección donde invocan `registrar`:

> **SOLO** invocá `registrar` cuando tengas los DOS datos confirmados (dichos por el lead en el chat):
> 1. **Nombre** que el lead escribió (NO el username/handle de ManyChat)
> 2. **Ubicación** que el lead mencionó (ciudad/zona/estado/país)
>
> Si tenés UNO solo → NO invoques. Seguí conversando.

---

## Pasos de deploy (en este orden)

### Paso 0 — Backup en n8n
1. Abrir el workflow `Agente WEB B2B y RRSS` en n8n.
2. Menú `...` arriba a la derecha → **Download** → guardar el JSON como `prod-snapshot-pre-fix-airtable-gate.json` localmente, por si necesitamos rollback rápido.

### Paso 1 — Editar el main workflow en n8n vivo (NO importar v4)
Hacemos los 3 cambios a mano para no pisar el systemMessage del AI Agent (que en producción tiene la última versión del prompt y queremos preservarlo intacto en este paso):

**EDIT 1.1 — Eliminar nodo `Crear contacto inicial`**
- Click derecho sobre el nodo `Crear contacto inicial` → Delete.

**EDIT 1.2 — Eliminar nodo `¿Existe?`**
- Click derecho sobre el nodo `¿Existe?` → Delete.

**EDIT 1.3 — Eliminar nodo `Existe?`**
- Click derecho sobre el nodo `Existe?` → Delete.

**EDIT 1.4 — Reconectar `Code in JavaScript` → `Separamos en partes`**
- Arrastrar una conexión desde la salida de `Code in JavaScript` hasta la entrada de `Separamos en partes`.
- Verificar que el flujo quede: `Webhook → Responder rápido ManyChat → Code in JavaScript → Separamos en partes`.

**EDIT 1.5 — Rehacer el nodo `registrar` con el mapeo final**

Click sobre el nodo `registrar`. En la sección **Columns → Fields to Send**, ajustar los 14 campos para que queden exactamente así (todos en modo Expression):

Reference snippet listo para copiar: [`06_docs/snippets/registrar-tool-config-v2.json`](snippets/registrar-tool-config-v2.json).

**Determinísticos (NO LLM):**
| Field | Value |
|---|---|
| `ID Manychat` | `{{ $('Webhook').first().json.body.id }}` (matching column, sin cambio) |
| `Canal` | `{{ $('Code in JavaScript').first().json.canal }}` |
| `Nombre / Usuario` | `{{ $('Webhook').first().json.body.name }}` ← **CAMBIO**: antes era $fromAI, ahora es el display name de la plataforma directo del webhook |
| `Whatsapp` | `{{ $('Code in JavaScript').first().json.canal === 'WhatsApp' ? ($('Webhook').first().json.body.whatsapp_phone \|\| '') : '' }}` ← **NUEVO**. ⚠️ Validar nombre del campo del payload — si ManyChat manda el teléfono con otro nombre (`phone`, `cel`, etc.), reemplazar. Probar con un mensaje real de WPP. |
| `Fecha captado` | `{{ $now }}` |
| `Ultimo contacto` | `{{ $now }}` ← **NUEVO** |

**$fromAI (LLM) con descripciones non-empty (anti bug Zod):**
| Field | Value |
|---|---|
| `Nombre completo` | `{{ $fromAI('Nombre_completo', 'Nombre del lead tal como lo escribio en el chat', 'string') }}` ← **NUEVO**, es el campo que cuenta para el gate |
| `Ubicación Mencionada` | `{{ $fromAI('Ubicacion', 'Ciudad zona o pais que el lead menciono en el chat', 'string') }}` |
| `Intento / Tipo de Lead` | `{{ $fromAI('Intento', 'Uno de: Curioso solo informacion / Evaluando opciones / Listo para operar', 'string') }}` |
| `Mensaje Original` | `{{ $fromAI('Mensaje_Original', 'Primer mensaje textual del lead', 'string') }}` |
| `Resumen del Mensaje` | `{{ $fromAI('Resumen', 'Una o dos oraciones de que quiere el lead', 'string') }}` |
| `Emoción / Tono Detectado` | `{{ $fromAI('Emocion', 'Uno de: Entusiasta / Dudoso / Interesado pero cauteloso / Urgente / Frio', 'string') }}` |
| `Respuesta Enviada` | `{{ $fromAI('Respuesta', 'Resumen breve de la ultima respuesta del agente', 'string') }}` |
| `Estado` | `{{ $fromAI('Estado', 'Estado del lead segun lista de opciones del single select', 'string') }}` ← **fix bug Zod**: antes `$fromAI("estado")` con descripción vacía. Era un bug latente. |

**Quitar de la tool:**
- `Dias de proceso` ← borrarlo de los Fields to Send. Ahora se calcula como fórmula Airtable (ver Paso 1.6).

Guardar el nodo (botón ☑ arriba derecha del panel).

**EDIT 1.6 — Convertir `Dias de proceso` en fórmula Airtable**

En Airtable (no en n8n):
1. Tabla Leads → click sobre el header del campo `Dias de proceso`.
2. **Customize field type**.
3. Cambiar tipo de `Number` a `Formula`.
4. Fórmula: `DATETIME_DIFF(NOW(), {Fecha captado}, 'days')`
5. Format: integer.
6. Save.

Ahora se actualiza solo a partir de `Fecha captado`. Si Airtable se queja porque hay valores existentes (0 en todos los rows), confirmar overwrite.

**EDIT 1.7 — Save workflow en n8n** (botón arriba a la derecha).

### Paso 2 — Subir prompts al Google Doc vivo

Los prompts en n8n los toma desde Google Docs (hay un nodo `Get a document` upstream del AI Agent — verificar topología actual). Si están inline, editar el systemMessage directamente.

**B2B v1.10:**
1. Abrir el Google Doc del prompt B2B.
2. Reemplazar el contenido del Doc por el de `clients/TFO_TOFO/04_agents/agente-tofo-b2b-system-prompt.md` (la sección bajo `## System Prompt`).
3. Cambios respecto a v1.9:
   - Header `**Versión:** v1.10` + nueva entrada en changelog.
   - Sección `# IMPORTANTE: REGISTRO EN AIRTABLE` ahora arranca con un bloque `🚦 GATE — CUÁNDO invocar registrar`.
   - Texto `"Una vez completada la cualificación..."` pasa a `"Una vez pasado el gate de arriba..."`.

**RRSS v1.6:**
1. Abrir el Google Doc del prompt RRSS.
2. Reemplazar igual.
3. Cambios respecto a v1.5:
   - Header `**Versión:** v1.6` + nueva entrada en changelog.
   - PASO 3 reescrito con el GATE.

### Paso 3 — Smoke tests E2E (4 casos)

Después de guardar todo, correr estos 4 casos contra un chat real (o un subscriber de testing) y verificar el resultado en Airtable.

#### Smoke 1 — Lead nuevo, sin nombre ni ubicación → NO debe crear record
**Mensaje del lead** (IG/WA): `"hola, info por favor"`
**Esperado:**
- Agente responde con saludo + pregunta de cualificación.
- **Airtable Leads**: cero rows nuevas con el `ID Manychat` de este subscriber. ✅

#### Smoke 2 — Lead da solo nombre → NO debe crear record
**Mensaje 1**: `"hola"`
**Respuesta agente**: saludo + pide qué necesita.
**Mensaje 2**: `"me llamo Federico, me interesa una máquina"`
**Esperado:**
- Agente sigue conversando, pregunta ubicación.
- **Airtable Leads**: cero rows con este `ID Manychat`. ✅ (tiene nombre pero no ubicación)

#### Smoke 3 — Lead da nombre + ubicación → DEBE crear record con todos los campos
**Mensaje 1**: `"hola, soy Ana, estoy en Monterrey y quiero saber sobre las máquinas TOFO"`
**Esperado:**
- Agente responde con info B2B / RRSS según contexto.
- En el mismo turno o el siguiente, agente invoca `registrar`.
- **Airtable Leads**: 1 row nueva con:
  - `ID Manychat` = subscriber id
  - `Nombre / Usuario` = "Ana" (NO el handle de ManyChat)
  - `Canal` = `Instagram` / `WhatsApp` / `Facebook` según corresponda ← **verificar que este campo se haya escrito**
  - `Ubicación Mencionada` = "Monterrey" o similar
  - `Estado` = el que el LLM eligió (probablemente "4. Pide más información" o "3. Vio precios")
  - `Fecha captado` = ahora ✅

#### Smoke 4 — Lead del Smoke 3 vuelve al día siguiente → upsert sin duplicar
**Mensaje (mismo `ID Manychat` que Smoke 3)**: `"sigo interesada, ¿cuánto sale?"`
**Esperado:**
- Agente reacciona usando memoria (Postgres Chat Memory) — sabe que es Ana de Monterrey.
- Agente puede invocar `registrar` de nuevo (es upsert).
- **Airtable Leads**: **sigue habiendo 1 sola row** con ese `ID Manychat`. Algunos campos pueden haberse actualizado (Estado, Respuesta Enviada, etc.). ✅ NO debe haber 2 rows.

### Paso 4 — Si los 4 smoke tests pasan
- Marcar el fix como vivo.
- Pasar al próximo punto de la lista (#2: limpieza de los ~580 registros vacíos existentes).

### Paso 5 — Si algún smoke test falla → rollback
- En n8n: subir el `prod-snapshot-pre-fix-airtable-gate.json` del Paso 0 (Import workflow → Overwrite).
- Restaurar los prompts en Google Doc desde los backups:
  - `clients/TFO_TOFO/04_agents/agente-tofo-b2b-system-prompt-v1.9.md`
  - `clients/TFO_TOFO/04_agents/agente-tofo-rrss-system-prompt-v1.5.md`
- Reportar acá qué falló para diagnosticar.

---

## Riesgos conocidos

1. **Leads de la última semana sin nombre/ubicación NO van a quedar en Airtable.** Esto es intencional (criterio Mauricio), pero significa que la métrica "leads nuevos por semana" va a bajar visiblemente. Es esperado — Mauricio quiere distinguir "lead real" de "conversación curiosa".

2. **Si el LLM se confunde y NO invoca `registrar` aunque tenga nombre + ubicación**, vamos a tener falsos negativos. Mitigación: el prompt es explícito sobre el gate, y el `registrar` ya estaba siendo invocado correctamente en la mayoría de casos pre-fix. Validamos esto en Smoke 3.

3. **Borrar `Existe?` significa que perdemos la capacidad de saber si un subscriber ya fue contactado antes sin consultar Airtable.** Hoy no hay lógica de negocio que dependa de eso (el IF solo routeaba al create), así que es seguro borrarlo. Si más adelante necesitamos esa info, se puede reintroducir el lookup sin reintroducir el create.

4. **Records ya existentes (los ~580 vacíos del renglón 488+) NO se tocan con este fix.** Quedan tal cual están — son parte del punto #2 de la lista de tareas (cleanup retroactivo).

---

## Próximos pasos (después de validar este fix)

Una vez que los 4 smoke tests pasen y veamos 24-48 hs de operación normal:

- **Punto #2 — Cleanup retroactivo**: query Airtable para identificar los records con `Estado IN ("1. Contacto RRSS", "2. Contacto WhatsApp")` AND `Ubicación Mencionada IS BLANK`, confirmar con Mauricio, bulk-delete.
- **Punto #1 — Muestreo del gap ManyChat vs Airtable**: una vez que el fix está vivo, el gap real (no contaminado por basura) se puede medir limpio. Tomar 50 conversaciones ManyChat sin lead en Airtable y clasificar: curiosas / capturó pero no escribió (regression).
- **Punto #3 — Decisión plan/límite Airtable**: con records limpios, el dato de "estamos cerca del límite" se vuelve más confiable. Mauricio decide upgrade Team / purga periódica / migración.
