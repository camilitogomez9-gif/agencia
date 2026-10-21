# M6 — Supabase: Tablas y Conexión

> **Referencia:** `03_arquitectura_ghl/02_data_model.md §5`, `03_arquitectura_ghl/06_integraciones.md §4`  
> **Tiempo estimado:** 1-2 horas  
> **Prerequisito:** Acceso al proyecto Supabase Pro de Oscar

---

## 6.1 Verificar tabla `messages` existente

Oscar ya tiene Supabase Pro con una tabla de mensajes activa. Conectarse al proyecto y verificar el schema:

```sql
-- En Supabase SQL Editor
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'messages' 
ORDER BY ordinal_position;
```

El schema esperado (según análisis Etapa 1):

| Columna | Tipo | Notas |
|---------|------|-------|
| `id` | bigint (serial) | PK |
| `session_id` | text | formato `<telefono>_2131` |
| `message` | jsonb | LangChain schema `{type: "human"|"ai", data: {content: "..."}}` |

Si hay columnas adicionales (timestamp, etc.) está bien. Si el schema es diferente, adaptar los queries de M5.

✅ Verificar que hay filas existentes y que el format de `session_id` es `+52XXXXXXXXXX_2131`.

---

## 6.2 Crear tabla `followups_log`

Esta tabla registra cada wave de re-engagement enviado para análisis posterior.

```sql
CREATE TABLE IF NOT EXISTS followups_log (
  id           bigserial PRIMARY KEY,
  opportunity_id text NOT NULL,
  contact_id   text NOT NULL,
  phone        text NOT NULL,
  wave         text NOT NULL,        -- "P1_W1", "P2_W3", etc.
  sent_at      timestamptz NOT NULL DEFAULT now(),
  message_content text,
  responded    boolean DEFAULT false,
  responded_at timestamptz
);

CREATE INDEX idx_followups_opportunity ON followups_log(opportunity_id);
CREATE INDEX idx_followups_wave ON followups_log(wave);
CREATE INDEX idx_followups_sent_at ON followups_log(sent_at);
```

---

## 6.3 Crear tabla `leads_metrics` (post-MVP)

Crear ahora aunque no se use hasta post-cutover:

```sql
CREATE TABLE IF NOT EXISTS leads_metrics (
  id                    bigserial PRIMARY KEY,
  opportunity_id        text UNIQUE NOT NULL,
  contact_id            text NOT NULL,
  phone                 text,
  evento                text,
  created_at            timestamptz,
  quoted_at             timestamptz,
  payment_confirmed_at  timestamptz,
  closed_at             timestamptz,
  final_stage           text,
  monto_mxn             numeric(10,2),
  time_to_quote_hours   numeric(6,2),
  time_to_close_hours   numeric(6,2),
  total_waves_sent      int DEFAULT 0,
  wave_that_converted   text,
  updated_at            timestamptz DEFAULT now()
);
```

---

## 6.4 Row Level Security (RLS)

Desactivar RLS en las tablas que n8n accede via Service Key (o configurar política que lo permita):

```sql
-- Opción A: desactivar RLS (ok para uso interno sin acceso público)
ALTER TABLE messages DISABLE ROW LEVEL SECURITY;
ALTER TABLE followups_log DISABLE ROW LEVEL SECURITY;
ALTER TABLE leads_metrics DISABLE ROW LEVEL SECURITY;
```

Si Oscar prefiere mantener RLS activo:
```sql
-- Opción B: política permisiva para service role
CREATE POLICY "service_role_full_access" ON messages
  FOR ALL USING (auth.role() = 'service_role');
```

---

## 6.5 Obtener credenciales de conexión

En Supabase → **Settings → Database**:

| Credencial | Dónde encontrarla | Variable de entorno |
|-----------|------------------|---------------------|
| Connection String (Postgres) | Settings → Database → Connection string | `SUPABASE_DB_URL` |
| Project URL | Settings → API → Project URL | `SUPABASE_URL` |
| anon key | Settings → API → Project API keys → anon | `SUPABASE_ANON_KEY` |
| service_role key | Settings → API → Project API keys → service_role | `SUPABASE_SERVICE_KEY` |

⚠️ n8n se conecta a Supabase via **PostgreSQL directo** (Postgres node), no via REST API. Usar el Connection String de Postgres, no el anon key.

El connection string tiene este formato:
```
postgresql://postgres.[project_ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

> Usar el **Transaction pooler** (puerto 6543) en lugar de Direct (5432) para mejor compatibilidad con n8n en instancias serverless o con muchas conexiones concurrentes.

---

## 6.6 Verificar conexión desde n8n

En n8n → **Credentials → PostgreSQL → New**:

- **Host:** `aws-0-[region].pooler.supabase.com`
- **Port:** `6543`
- **Database:** `postgres`
- **User:** `postgres.[project_ref]`
- **Password:** [la de Supabase]
- **SSL:** Enable (requerido por Supabase)

Test connection → debe dar verde.

---

## 6.7 Query de prueba

Desde n8n, correr este query para verificar que la tabla `messages` es accesible y tiene el formato correcto:

```sql
SELECT session_id, message->>'type' as msg_type, 
       message->'data'->>'content' as content
FROM messages 
ORDER BY id DESC 
LIMIT 5;
```

---

## ✅ Checklist M6

- [ ] Schema de tabla `messages` verificado y compatible
- [ ] Tabla `followups_log` creada
- [ ] Tabla `leads_metrics` creada (post-MVP)
- [ ] RLS configurado (desactivado o con política service_role)
- [ ] Credenciales de Supabase en variables de entorno de n8n
- [ ] Conexión PostgreSQL desde n8n funcionando (test verde)
- [ ] Query de prueba sobre `messages` devuelve resultados correctos

**Siguiente:** M7 → WhatsApp WABA y plantillas Meta
