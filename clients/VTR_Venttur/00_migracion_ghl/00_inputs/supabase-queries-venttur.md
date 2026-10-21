# Queries Supabase — Export completo VTR

> Schema confirmado por inspección directa de los nodos Postgres en los workflows de producción (`wf-venttur-main.json` nodo "Postgres Chat Memory", `wf-resumen-etiquetas-seguimientos.json` nodo "Postgres"). No es un schema supuesto.

## Schema confirmado

**Credencial n8n:** `Venttur` (id `ihpvM7nYMdLCwWDP`)

**Tabla:** `n8n_chat_histories` (schema estándar del nodo `memoryPostgresChat` de n8n — misma forma que usan otros clientes de la agencia)

| Columna | Tipo | Notas |
|---------|------|-------|
| `id` | serial/int | PK autoincremental |
| `session_id` | text | Teléfono del lead **sin el `+`**. Confirmado en `wf-venttur-main.json`: `sessionKey: whatsapp_phone.replace('+','')`. **⚠️ Ver quirk MX abajo — no es un simple "sin +".** |
| `message` | jsonb | `{"type": "human"\|"ai"\|"system", "content": "..."}` — `system` aparece en sesiones con memoria sintética pre-poblada (outreach/rescate) |
| `created_at` | timestamptz | (columna estándar del nodo; no se vio explícitamente pero es parte del schema base de `memoryPostgresChat`) |

**`contextWindowLength`:** 35 turnos (configurado en el nodo de memoria del main).

## ⚠️ Quirk confirmado: `session_id` para números mexicanos (52 vs 521)

Descubierto al recibir `outreach-form-meta-venttur-v5` (2026-07-10). Los números de celular de México llegan de WhatsApp como `52XXXXXXXXXX` (12 dígitos), pero el `sessionKey` que arma el main (`venttur-main`) y ManyChat esperan `521XXXXXXXXXX` (13 dígitos, con el `1` de celular intercalado). Todo lo que no normaliza este caso puntual (algunos de los nodos "Build Memory Texts" de outreach) generaba `session_id` con formato equivocado → esas filas nunca hacían match con la sesión real cuando el lead respondía.

**Fix aplicado en producción** (confirmado en el código del nodo `Execute a SQL query`, corrido manualmente contra la tabla real):

```sql
-- Backfill ya ejecutado en producción — referencia, no hace falta re-correrlo
UPDATE n8n_chat_histories
SET session_id = '521' || SUBSTRING(session_id FROM 3)
WHERE session_id ~ '^52[0-9]{10}$'
  AND NOT (message ? 'tool_calls')
  AND NOT (message ? 'invalid_tool_calls');
```

**Para la migración:** al exportar `session_id` para reconstruir a qué lead de Airtable corresponde cada conversación, verificar primero si quedan filas con el formato viejo (12 dígitos) — la query §6 abajo lo chequea. Si aparecen filas, aplicar la misma normalización antes de cruzar contra `Leads.Telefono`.

## ✅ CERRADO — 3 tablas confirmadas, solo `n8n_chat_histories` importa para la migración

Se corrió la query §5 + investigación de columnas/conteos contra la base real (2026-07-20). Resultado:

| Tabla | Filas | Conclusión |
|---|---|---|
| `n8n_chat_histories` | 34.725 (max id 36.527) | ✅ **La única relevante para migrar.** Ya documentada arriba. |
| `documents` | **0** | Schema clásico de vector store LangChain/Supabase (`id bigint, content text, metadata jsonb, embedding vector`) — pero vacía y ningún workflow la referencia (grep sobre los 14 workflows: cero matches). Vestigio de un setup RAG que nunca se usó. **No requiere acción.** |
| `n8n_chat_histories_plus_backup` | **2** (max id 9.041) | Solo 2 filas puntuales, capturadas cuando la tabla viva tenía ~9K filas — no es un backup masivo pre-operación, es demasiado chico para eso. Ningún workflow la referencia. **No requiere acción.** |

**`workflow_errors` no existe en esta base.** El sub-workflow `webapp_errors` (invocado desde `outreach-form-meta-venttur-v5` y otros) escribe a un Supabase compartido/central de la agencia, no al de este cliente — fuera del alcance de esta migración.

**Para Etapa 3 (arquitectura GHL):** el único dato a migrar de Supabase es el historial de conversación en `n8n_chat_histories`, usando los queries 1-3 de abajo.

---

## 1. Export completo (todas las filas, sin transformar)

```sql
SELECT id, session_id, message, created_at
FROM public.n8n_chat_histories
ORDER BY session_id, id;
```

## 2. Conversaciones reconstruidas (legible, agrupado por sesión)

```sql
SELECT
  session_id,
  jsonb_agg(
    jsonb_build_object(
      'turno', row_number() OVER (PARTITION BY session_id ORDER BY id),
      'rol', CASE
               WHEN message->>'type' = 'human' THEN 'LEAD'
               WHEN message->>'type' = 'ai' THEN 'AGENTE'
               ELSE COALESCE(message->>'type', 'unknown')
             END,
      'texto', message->>'content',
      'created_at', created_at
    )
    ORDER BY id
  ) AS conversacion
FROM public.n8n_chat_histories
GROUP BY session_id
ORDER BY MAX(id) DESC;
```

## 3. Resumen / sanity check (para validar el volumen antes de migrar)

```sql
SELECT
  COUNT(DISTINCT session_id) AS sesiones_unicas,
  COUNT(*) AS mensajes_totales,
  COUNT(*) FILTER (WHERE message->>'type' = 'human') AS mensajes_lead,
  COUNT(*) FILTER (WHERE message->>'type' = 'ai') AS mensajes_agente,
  MIN(created_at) AS primer_mensaje,
  MAX(created_at) AS ultimo_mensaje
FROM public.n8n_chat_histories;
```

## 4. Export a CSV directo (psql)

```bash
psql "$SUPABASE_CONNECTION_STRING" -c "\copy (SELECT id, session_id, message, created_at FROM public.n8n_chat_histories ORDER BY session_id, id) TO 'n8n_chat_histories_export.csv' WITH CSV HEADER"
```

## 5. Verificar existencia de otras tablas (correr primero — confirma `workflow_errors` y schema real)

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

Si aparece `workflow_errors`, correr también:

```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'workflow_errors'
ORDER BY ordinal_position;
```

## 6. Detectar filas con `session_id` sin normalizar (formato MX viejo, 12 dígitos)

```sql
SELECT session_id, COUNT(*) AS mensajes
FROM n8n_chat_histories
WHERE session_id ~ '^52[0-9]{10}$'
GROUP BY session_id
ORDER BY mensajes DESC;
```

Si devuelve filas, esos `session_id` no matchean el formato real (`521XXXXXXXXXX`) que usa el resto del sistema para ese lead — antes de migrar, aplicar la misma normalización (`'521' || SUBSTRING(session_id FROM 3)`) para que no queden conversaciones huérfanas al cruzar contra `Leads.Telefono`.
