# Deploy: `guardar_email` → `registrar_datos_lead` (v1)

**Fecha:** 2026-06-24
**Autor:** la agencia · la agencia
**Disparador:** Audio Edgardo 2026-06-24 — el bot debe registrar todos los leads que dejen al menos un dato (no solo los que dejen email).

## Cambios en alto nivel

| Antes (v5 `guardar_email`) | Después (v1 `registrar_datos_lead`) |
|---|---|
| Activación: solo cuando hay email explícito | Activación: apenas hay nombre. Re-invocación con email/telefono. |
| Validate Input rechaza si falta email | Validate Input acepta input parcial (≥1 de nombre/email/telefono) |
| Lookup por columna `email` | Lookup por columna `subscriber_id` |
| Si existe → solo devuelve "already_exists" | Si existe → Merge + Update Sheets (enriquece la fila) |
| `Update datos_capturados` solo escribe `mail` al Supabase | Escribe `nombre + mail + telefono` cuando vengan |
| Notif Gmail dispara en cada captura de email | Notif Gmail solo dispara en INSERT (lead nuevo), updates son silenciosos |
| Mensaje al agente en "already_exists": genérico | Mensaje al agente: diff explícito (`agregados` / `actualizados` / `ya_existentes`) |

**Idempotencia preservada**: misma sesión/lead puede invocar la tool N veces sin duplicar filas en el sheet ni datos en Supabase.

## Pre-flight

- [ ] Sheet `SYS - Leads (Captura Emails)` tiene la columna `subscriber_id` poblada en todas las filas activas (verificado el 2026-06-24 sobre `Ayer.csv` — todas tienen `subscriber_id`).
- [ ] `versionId` del workflow vivo `v9HD7P2uroG4Ni3A` exportado a `sys-tool-guardar-email-v5.json` como respaldo (ya en repo).
- [ ] `sys-agente-principal-v0.9.json` exportado como respaldo (ya en repo).

## Paso 1 — Importar el nuevo sub-workflow

1. Abrir n8n → Workflows → buscar `sys-tool-guardar-email-v1` (id `v9HD7P2uroG4Ni3A`).
2. Pausar (`active: false`) si no lo está ya. El main hoy llama por `workflowId` aún si está pausado — vamos a hacer una pausa más amplia con el siguiente paso (rename del nodo en el main).
3. Menú `…` → Import from File → seleccionar `clients/SYS_SistemasYSoluciones/03_workflows/sys-tool-registrar-datos-lead-v1.json`.
4. n8n debería detectar el `id` `v9HD7P2uroG4Ni3A` y proponer overwrite — confirmar.
5. Verificar que las dos credenciales se vincularon:
   - `la agencia` (Google Sheets) → id `2a5f0S7mTtvH5XH2`
   - `Supabase SYS` (Postgres) → id `cQLxF5deDtmo4HTV`
   - `Gmail | la agencia®` (Gmail) → id `5R0ScEVqcfjKYanp`
6. Confirmar que el workflow ahora se llama `sys-tool-registrar-datos-lead-v1` en n8n.
7. Test execute con el pin data del Trigger (`{nombre: "Test la agencia", subscriber_id: "smoke_v1_001", session_id: "smoke_v1_001"}`) → debería ir por rama `Append` → notif Gmail + escribir fila nueva en el sheet.
8. Volver a activar (`active: true`).
9. Limpiar la fila de smoke (`subscriber_id = smoke_v1_001`) del sheet.

## Paso 2 — Edits en `sys-agente-principal` (n8n vivo)

El main workflow tiene un nodo `toolWorkflow` que cablea esta tool al AI Agent. Hay que actualizarlo IN-PLACE para que el LLM lea el nuevo nombre + descripción.

**EDIT 2.1 — Renombrar el nodo**
- Buscar el nodo `guardar_email` (canvas posición aprox `[2192, 160]`, type `@n8n/n8n-nodes-langchain.toolWorkflow`).
- Doble click → `Name` → cambiar `guardar_email` → `registrar_datos_lead`.

**EDIT 2.2 — Actualizar el `description` (LLM-facing)**

Reemplazar el texto actual por:

```
Registra o actualiza los datos del lead (nombre, email, teléfono) en la base de captura. Invocala apenas el cliente comparta su nombre. Re-invocala cuando el cliente comparta datos adicionales (email y/o teléfono) — la tool hace upsert por subscriber_id y mergea sin pisar lo previo. Requiere AL MENOS UNO de: nombre, email o telefono. Pasá TODOS los args con la información que hayas recolectado de la conversación (si no tenés un dato, pasalo como string vacío, no omitas argumentos). Si already_exists=true en el output, no lo menciones al cliente: seguí natural sin re-confirmar datos ya capturados.
```

**EDIT 2.3 — Actualizar las descripciones de los `$fromAI` fields**

En la sección `Workflow Inputs`, doble click en cada uno y reemplazar el segundo arg (la descripción):

| Field | Descripción nueva |
|---|---|
| `nombre` | `Nombre del cliente. Activador principal — invocá apenas el lead lo comparta.` |
| `email` | `Email del cliente en formato xxx@xxx.xxx. Opcional.` |
| `telefono` | `Teléfono del cliente. Opcional.` |
| `origen` | `Motivo del registro. Valores: newsletter, derivacion, descuento_insumos, otro` |
| `aplicacion_interes` | `Aplicación o equipo que el cliente consulta. Opcional.` |
| `canal` / `subscriber_id` / `session_id` | (sin cambios — vienen del Normalize Payload, no del LLM) |

**EDIT 2.4 — Reordenar el orden de los fields en la UI (cosmético, opcional)**

Mover `nombre` al primer lugar (arriba de email) — los LLMs leen los schemas en orden y priorizan los primeros campos. n8n permite drag-and-drop en la sección Workflow Inputs.

## Paso 3 — Actualizar el system prompt

El prompt vive en 2 lugares: el Google Doc (fuente principal) y el set-node `backup` del main (fallback inline).

**EDIT 3.1 — Google Doc**
- Abrir: https://docs.google.com/document/d/1Obn0xzfAAUGs4oMpoh99dFXPfGuG9d6uBWglKNuPY5I/edit
- **Recomendación:** copy-paste del prompt v2.3 completo (entre los backticks del local `agente-sistemasysoluciones-system-prompt.md`, líneas 50-405) reemplazando todo el contenido actual del Google Doc. El local ya tiene mergeados los deltas que el cliente había editado directamente en producción ("y alquilan", bullet Alquiler en Datos fijos, Flujo de alquiler, Flujo de demo) — por eso la sobreescritura completa es segura.
- Si preferís edits puntuales en vez de overwrite total: bumpear header `Versión: v2.3` · `Fecha: 2026-06-24`, reemplazar el bloque `**guardar_email**` por `**registrar_datos_lead**` (líneas 215-220 del local), reemplazar Regla 26 (líneas 307-313 del local), cambiar preámbulo de HERRAMIENTAS ("persistir el email" → "capturar datos de contacto").

**EDIT 3.2 — Set node `backup` del main**

El set node `backup` (id `e5ac3d80-...`) tiene la copia completa del prompt inline para usar si Google Docs falla. Hay que actualizarlo:
- Reemplazar todo el valor del field `backup` con el contenido actualizado del prompt v2.3 (copy-paste del archivo local `agente-sistemasysoluciones-system-prompt.md`).

## Paso 4 — Smoke tests E2E

Ejecutar contra el webhook productivo (o staging si está cableado). Verificar en cada caso:
- Output del agente al cliente (mensaje correcto, sin re-pregunta de datos ya dados).
- Sheet `SYS - Leads (Captura Emails)` (fila correcta, sin duplicados).
- Tabla `sys_session_state` en Supabase (`datos_capturados` mergeado).
- Tabla `sys_tool_calls` (entrada con `tool_name = 'registrar-datos-lead'`).
- Inbox emarti@/marketing@ (solo en S1 y S4, NO en S2 ni S3).

### S1 — Lead nuevo da solo nombre
- Mensaje cliente: `"Hola, soy Federico"`
- Esperado: agente invoca `registrar_datos_lead({nombre: "Federico", ...})`. Sub-workflow va por rama `Append` (no existía subscriber_id). Notif Gmail SÍ dispara. Sheet tiene 1 fila nueva con `nombre="Federico"`, resto vacío salvo subscriber_id/canal/session_id.

### S2 — Mismo lead da teléfono después
- Mensaje cliente (siguiente turno): `"Mi teléfono es 1131345321"`
- Esperado: agente invoca `registrar_datos_lead({nombre: "Federico", telefono: "1131345321", ...})` (debe tener nombre en contexto por la Capa 2 del fix). Sub-workflow va por rama `Lookup found` → Merge → Update Sheets. **Notif Gmail NO dispara** (silencioso en updates). Sheet sigue con 1 fila, ahora con `telefono` poblado. `message_to_agent` incluye "Datos agregados: telefono · ya estaban: nombre".

### S3 — Mismo lead da email
- Mensaje cliente: `"mi mail es federico@gmail.com"`
- Esperado: igual a S2 pero con email. Sheet mantiene 1 fila, ahora con `email` poblado. Notif Gmail NO dispara.

### S4 — Lead totalmente nuevo da los 3 datos juntos
- Mensaje cliente (subscriber distinto): `"Hola, soy Marcela, tel 1199998888, mail marcela@empresa.com"`
- Esperado: agente invoca `registrar_datos_lead` con los 3 datos. Rama `Append`. 1 fila nueva, los 3 campos poblados de entrada. Notif Gmail SÍ dispara.

### S5 (negativo) — Cliente solo dice "hola"
- Mensaje cliente: `"hola"`
- Esperado: agente NO invoca la tool (Regla 26 — sin nombre/email/telefono no se dispara). El agente saluda y pregunta cómo ayudar.

### S6 (negativo) — Cliente da nombre con email inválido
- Mensaje cliente: `"Soy Ana, mail anaarrobagmailpuntocom"`
- Esperado: agente invoca con `nombre="Ana"` y `email="anaarrobagmailpuntocom"`. Validate Input rechaza por regex de email → status ERROR → `message_to_agent: "El email ... no tiene formato válido. Pedile al cliente que lo confirme y volvé a llamar la tool."` El agente le pide al cliente que confirme el mail.

## Paso 5 — Verificación post-deploy (primeras 24h)

Query en Supabase para auditar:
```sql
-- Distribución de invocaciones en las últimas 24h
SELECT
  status,
  COUNT(*) AS calls,
  COUNT(DISTINCT session_id) AS sessions_distintas
FROM sys_tool_calls
WHERE tool_name = 'registrar-datos-lead'
  AND created_at > NOW() - INTERVAL '24 hours'
GROUP BY status;
```

```sql
-- Leads nuevos vs updates en las últimas 24h
SELECT
  (output_payload->'data'->>'already_exists')::boolean AS already_exists,
  COUNT(*) AS calls
FROM sys_tool_calls
WHERE tool_name = 'registrar-datos-lead'
  AND status = 'RESOLVED'
  AND created_at > NOW() - INTERVAL '24 hours'
GROUP BY already_exists;
```

Si en 24h ves >0 calls con status=ERROR cuyo `message_to_agent` contiene "Faltan datos", es señal de que el LLM está intentando invocar sin contexto suficiente → revisar prompt + descripción de la tool.

## Rollback

Si en 24h aparece comportamiento inesperado (filas duplicadas, agente confundido, ruido de notifs):

1. Re-importar `sys-tool-guardar-email-v5.json` en n8n (overwrite del mismo workflowId).
2. En el main, renombrar el nodo `registrar_datos_lead` → `guardar_email`, revertir description + $fromAI descs.
3. En el Google Doc, revertir header a v2.2, restaurar bloque `**guardar_email**` + Regla 26 vieja (commit anterior en repo).
4. Set node `backup`: pegar contenido de `agente-sistemasysoluciones-system-prompt-v2.2.md`.

El sheet no necesita rollback — las columnas y filas existentes son retrocompatibles. Cualquier fila enriquecida en el período de v1 queda con datos adicionales válidos.

---

## Checklist final

- [ ] Sub-workflow `sys-tool-registrar-datos-lead-v1.json` importado en n8n
- [ ] 3 credenciales verificadas (Sheets, Supabase, Gmail)
- [ ] Workflow activado (active=true)
- [ ] Smoke test pin data del Trigger pasó
- [ ] Fila de smoke limpiada
- [ ] EDIT 2.1: Nodo `guardar_email` renombrado → `registrar_datos_lead`
- [ ] EDIT 2.2: Description del toolWorkflow actualizada
- [ ] EDIT 2.3: 5 `$fromAI` descriptions actualizadas
- [ ] EDIT 2.4 (opcional): `nombre` movido al primer lugar en Workflow Inputs
- [ ] EDIT 3.1: Google Doc actualizado a v2.3 (header + Tool 9 + Regla 26 + preámbulo)
- [ ] EDIT 3.2: Set node `backup` actualizado con prompt v2.3
- [ ] S1 (lead nuevo solo nombre) pasó
- [ ] S2 (mismo lead da teléfono) pasó
- [ ] S3 (mismo lead da email) pasó
- [ ] S4 (lead nuevo con 3 datos juntos) pasó
- [ ] S5 (solo "hola" — no invoca) pasó
- [ ] S6 (email inválido — error claro al agente) pasó
- [ ] Verificación 24h: queries SQL ejecutadas, sin ratio anormal de errors
