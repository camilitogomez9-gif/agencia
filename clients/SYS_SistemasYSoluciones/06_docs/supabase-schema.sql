-- ============================================================
-- SCHEMA SYS — Memoria persistente + Observabilidad
-- Proyecto Supabase: la agencia-sys (región sa-east-1)
-- Fecha: 2026-05-28
-- Versión: v1
-- ============================================================
--
-- Cómo aplicar:
-- 1. Crear proyecto en https://supabase.com (free tier, region sa-east-1).
-- 2. SQL Editor → New query → pegar este archivo → Run.
-- 3. Verificar que todas las tablas e índices aparezcan en Table Editor.
-- 4. Copiar connection string de Settings → Database → Connection string (URI mode).
-- 5. Crear credencial n8n "Supabase SYS" con esa connection string.
--
-- Rollback: ver final del archivo (sección DROP).
-- ============================================================


-- ----- Tabla 1: n8n_chat_histories (creada automáticamente por n8n) -----
-- El nodo Postgres Chat Memory de n8n LangChain crea esta tabla en el primer
-- INSERT. La definimos manualmente acá para garantizar la estructura y los
-- índices óptimos antes del primer uso.

CREATE TABLE IF NOT EXISTS n8n_chat_histories (
  id SERIAL PRIMARY KEY,
  session_id TEXT NOT NULL,
  message JSONB NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Índices para performance (n8n NO los crea por default)
CREATE INDEX IF NOT EXISTS idx_chat_session
  ON n8n_chat_histories(session_id);

CREATE INDEX IF NOT EXISTS idx_chat_session_id_desc
  ON n8n_chat_histories(session_id, id DESC);

-- Comentarios
COMMENT ON TABLE n8n_chat_histories IS 'Historial conversacional persistente. Lo gestiona el nodo Postgres Chat Memory de n8n LangChain.';
COMMENT ON COLUMN n8n_chat_histories.session_id IS 'leadIdentifier = canal + "_" + subscriber_id (ej: whatsapp_549112345678)';
COMMENT ON COLUMN n8n_chat_histories.message IS 'JSON con shape { type: "human"|"ai"|"system", content: "..." }';


-- ----- Tabla 2: sys_tool_calls (observabilidad de tool calling) -----
-- Toda invocación a una tool del agente registra una fila acá.
-- Útil para debugging, métricas, detección de NOT_FOUND recurrentes, etc.

CREATE TABLE IF NOT EXISTS sys_tool_calls (
  id SERIAL PRIMARY KEY,
  session_id TEXT NOT NULL,
  lead_airtable_id TEXT,
  tool_name TEXT NOT NULL,
  input_payload JSONB,
  output_payload JSONB,
  status TEXT NOT NULL,
  error_message TEXT,
  duration_ms INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_tool_calls_session
  ON sys_tool_calls(session_id);

CREATE INDEX idx_tool_calls_tool
  ON sys_tool_calls(tool_name);

CREATE INDEX idx_tool_calls_created
  ON sys_tool_calls(created_at DESC);

-- Índice parcial: solo errores y not-found (queries de monitoreo son chiquitas)
CREATE INDEX idx_tool_calls_problems
  ON sys_tool_calls(status, tool_name, created_at DESC)
  WHERE status IN ('error', 'not_found', 'timeout');

-- Comentarios
COMMENT ON TABLE sys_tool_calls IS 'Log de cada invocación a tool del agente. NO se loguea en el contexto del LLM.';
COMMENT ON COLUMN sys_tool_calls.tool_name IS 'buscar_equipo | consultar_tecnologia | consultar_aplicacion | consultar_compatibilidad | consultar_faq | consultar_lineas_priorizadas | consultar_url_tienda | notificar_lead';
COMMENT ON COLUMN sys_tool_calls.status IS 'success | error | not_found | timeout | ambiguous';
COMMENT ON COLUMN sys_tool_calls.lead_airtable_id IS 'Record ID de la tabla Leads en Airtable (recXXXXX), nullable si lead no creado todavía';


-- ----- Tabla 3: sys_session_state (cache cross-turn) -----
-- Variables del lead que el agente necesita ver en cada turno: perfil, etapa,
-- datos capturados parcialmente, productos ya mostrados.
-- Permite inyectar contexto fresco al [CONTEXTO TURNO] del User Message sin
-- recorrer todo el historial.

CREATE TABLE IF NOT EXISTS sys_session_state (
  session_id TEXT PRIMARY KEY,
  lead_airtable_id TEXT,
  perfil TEXT,
  etapa TEXT NOT NULL DEFAULT 'bienvenida',
  datos_capturados JSONB NOT NULL DEFAULT '{}'::jsonb,
  productos_mostrados TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
  ultima_actividad TIMESTAMP NOT NULL DEFAULT NOW(),
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Índice para query de leads abandonados
CREATE INDEX idx_session_state_actividad
  ON sys_session_state(ultima_actividad DESC);

CREATE INDEX idx_session_state_etapa
  ON sys_session_state(etapa)
  WHERE etapa NOT IN ('derivado', 'cerrado');

-- Comentarios
COMMENT ON TABLE sys_session_state IS 'Cache rápido de estado de la sesión por leadIdentifier. Permite inyectar contexto al LLM sin tokens extra.';
COMMENT ON COLUMN sys_session_state.perfil IS 'distribuidor | pyme | emprendedor | sin clasificar | NULL';
COMMENT ON COLUMN sys_session_state.etapa IS 'bienvenida | identificacion | diagnostico | asesoramiento | captura | derivado | cerrado';
COMMENT ON COLUMN sys_session_state.datos_capturados IS 'JSON: { nombre, telefono, mail, ubicacion, equipo_interes, empresa, tecnologia_interes }';
COMMENT ON COLUMN sys_session_state.productos_mostrados IS 'Array de modelos ya mencionados al lead (anti-repetición)';


-- ----- Tabla 4: sys_conversations_summary (opcional, v2.1) -----
-- Resumen LLM-generado cuando una conversación supera 100 turnos.
-- NO se implementa en v2.0. Tabla pre-creada para futuro.

CREATE TABLE IF NOT EXISTS sys_conversations_summary (
  session_id TEXT PRIMARY KEY,
  summary TEXT NOT NULL,
  key_facts JSONB NOT NULL DEFAULT '{}'::jsonb,
  last_message_id INTEGER NOT NULL,
  generated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE sys_conversations_summary IS 'Resúmenes LLM de conversaciones largas. RESERVADO para v2.1, no usar todavía.';


-- ============================================================
-- VISTAS ÚTILES
-- ============================================================

-- Vista 1: Leads abandonados (>24h sin actividad, no derivados)
CREATE OR REPLACE VIEW sys_leads_abandonados AS
SELECT
  s.session_id,
  s.lead_airtable_id,
  s.perfil,
  s.etapa,
  s.datos_capturados,
  s.ultima_actividad,
  EXTRACT(EPOCH FROM (NOW() - s.ultima_actividad))/3600 AS horas_inactivo,
  s.created_at
FROM sys_session_state s
WHERE s.etapa NOT IN ('derivado', 'cerrado')
  AND s.ultima_actividad < NOW() - INTERVAL '24 hours'
ORDER BY s.ultima_actividad ASC;

COMMENT ON VIEW sys_leads_abandonados IS 'Leads activos sin actividad en >24h. Útil para follow-up manual o automation.';


-- Vista 2: Métricas de tool calling (últimas 24h)
CREATE OR REPLACE VIEW sys_tool_metrics_24h AS
SELECT
  tool_name,
  COUNT(*) AS invocaciones_total,
  COUNT(*) FILTER (WHERE status = 'success') AS success,
  COUNT(*) FILTER (WHERE status = 'not_found') AS not_found,
  COUNT(*) FILTER (WHERE status = 'error') AS error,
  COUNT(*) FILTER (WHERE status = 'timeout') AS timeout,
  ROUND(AVG(duration_ms)::numeric, 2) AS avg_duration_ms,
  ROUND(MAX(duration_ms)::numeric, 2) AS max_duration_ms,
  ROUND(
    100.0 * COUNT(*) FILTER (WHERE status = 'success') / NULLIF(COUNT(*), 0),
    2
  ) AS success_rate_pct
FROM sys_tool_calls
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY tool_name
ORDER BY invocaciones_total DESC;

COMMENT ON VIEW sys_tool_metrics_24h IS 'Métricas de uso y salud de cada tool en las últimas 24h.';


-- Vista 3: Sesiones activas hoy
CREATE OR REPLACE VIEW sys_sesiones_activas_hoy AS
SELECT
  s.session_id,
  s.perfil,
  s.etapa,
  s.datos_capturados,
  s.ultima_actividad,
  COUNT(c.id) AS mensajes_total
FROM sys_session_state s
LEFT JOIN n8n_chat_histories c ON c.session_id = s.session_id
WHERE s.ultima_actividad::date = CURRENT_DATE
GROUP BY s.session_id, s.perfil, s.etapa, s.datos_capturados, s.ultima_actividad
ORDER BY s.ultima_actividad DESC;


-- ============================================================
-- FUNCIÓN: upsert_session_state
-- ============================================================
-- Helper para que n8n actualice el estado del lead sin escribir SQL manual.

CREATE OR REPLACE FUNCTION upsert_session_state(
  p_session_id TEXT,
  p_lead_airtable_id TEXT,
  p_perfil TEXT,
  p_etapa TEXT,
  p_datos_capturados JSONB,
  p_productos_mostrados TEXT[]
) RETURNS sys_session_state AS $$
DECLARE
  result sys_session_state;
BEGIN
  INSERT INTO sys_session_state (
    session_id, lead_airtable_id, perfil, etapa,
    datos_capturados, productos_mostrados, ultima_actividad
  ) VALUES (
    p_session_id, p_lead_airtable_id, p_perfil, p_etapa,
    p_datos_capturados, p_productos_mostrados, NOW()
  )
  ON CONFLICT (session_id) DO UPDATE SET
    lead_airtable_id    = COALESCE(EXCLUDED.lead_airtable_id, sys_session_state.lead_airtable_id),
    perfil              = COALESCE(EXCLUDED.perfil, sys_session_state.perfil),
    etapa               = EXCLUDED.etapa,
    datos_capturados    = sys_session_state.datos_capturados || EXCLUDED.datos_capturados,
    productos_mostrados = ARRAY(SELECT DISTINCT UNNEST(sys_session_state.productos_mostrados || EXCLUDED.productos_mostrados)),
    ultima_actividad    = NOW()
  RETURNING * INTO result;

  RETURN result;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION upsert_session_state IS 'Upsert del state. Hace merge de datos_capturados y union de productos_mostrados.';


-- ============================================================
-- VERIFICACIÓN POST-DEPLOY
-- ============================================================
-- Ejecutar estos SELECT después del setup para confirmar que todo está OK.

-- SELECT 'n8n_chat_histories' AS tabla, COUNT(*) AS filas FROM n8n_chat_histories
-- UNION ALL SELECT 'sys_tool_calls', COUNT(*) FROM sys_tool_calls
-- UNION ALL SELECT 'sys_session_state', COUNT(*) FROM sys_session_state
-- UNION ALL SELECT 'sys_conversations_summary', COUNT(*) FROM sys_conversations_summary;

-- SELECT * FROM sys_tool_metrics_24h;
-- SELECT * FROM sys_leads_abandonados;
-- SELECT * FROM sys_sesiones_activas_hoy;


-- ============================================================
-- ROLLBACK (uncomment si necesitás desinstalar)
-- ============================================================

-- DROP VIEW IF EXISTS sys_sesiones_activas_hoy;
-- DROP VIEW IF EXISTS sys_tool_metrics_24h;
-- DROP VIEW IF EXISTS sys_leads_abandonados;
-- DROP FUNCTION IF EXISTS upsert_session_state;
-- DROP TABLE IF EXISTS sys_conversations_summary;
-- DROP TABLE IF EXISTS sys_session_state;
-- DROP TABLE IF EXISTS sys_tool_calls;
-- DROP TABLE IF EXISTS n8n_chat_histories;
