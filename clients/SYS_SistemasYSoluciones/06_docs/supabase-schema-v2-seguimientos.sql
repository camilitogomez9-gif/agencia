-- ===========================================================================
-- SYS — Supabase schema v2 — Seguimientos automáticos
-- Fecha: 2026-06-05
-- Hereda: supabase-schema.sql (4 tablas + 3 vistas + función upsert_session_state)
--
-- Este script agrega lo necesario para implementar el workflow
-- sys-seguimientos-leads-v1 (cron de follow-ups a 24h y 7d).
--
-- Idempotente: se puede correr múltiples veces sin error.
-- ===========================================================================


-- ---------------------------------------------------------------------------
-- 1) Columna seguimientos_enviados en sys_session_state
-- ---------------------------------------------------------------------------
-- Contador de cuántos toques de seguimiento se enviaron a esa sesión.
-- 0 = ninguno, 1 = ya se envió el de 24h, 2 = ya se envió el de 7d (cerrado).

ALTER TABLE sys_session_state
  ADD COLUMN IF NOT EXISTS seguimientos_enviados INTEGER NOT NULL DEFAULT 0;

COMMENT ON COLUMN sys_session_state.seguimientos_enviados IS
  'Toques de seguimiento ya enviados al lead (0=ninguno, 1=24h, 2=7d). Usado por sys-seguimientos-leads-v1 para idempotencia.';


-- ---------------------------------------------------------------------------
-- 2) Vista sys_leads_para_seguimiento
-- ---------------------------------------------------------------------------
-- Devuelve los leads listos para recibir un seguimiento, junto con el número
-- de toque que corresponde (1 = 24h, 2 = 7d).
--
-- Reglas:
--   - Solo sesiones que NO estén en estado terminal ('derivado' o 'cerrado').
--   - Toque 1: ultima_actividad > 24h y aún no se envió ninguno.
--   - Toque 2: ultima_actividad > 7d y ya se envió el toque 1.
--
-- El workflow sys-seguimientos-leads-v1 hace SELECT * FROM esta vista y
-- procesa cada fila.

CREATE OR REPLACE VIEW sys_leads_para_seguimiento AS
SELECT
  session_id,
  perfil,
  etapa,
  datos_capturados,
  productos_mostrados,
  ultima_actividad,
  seguimientos_enviados,
  CASE
    WHEN seguimientos_enviados = 0 AND ultima_actividad < NOW() - INTERVAL '24 hours' THEN 1
    WHEN seguimientos_enviados = 1 AND ultima_actividad < NOW() - INTERVAL '7 days'  THEN 2
    ELSE NULL
  END AS toque_a_enviar
FROM sys_session_state
WHERE
  etapa NOT IN ('derivado', 'cerrado')
  AND (
    (seguimientos_enviados = 0 AND ultima_actividad < NOW() - INTERVAL '24 hours')
    OR
    (seguimientos_enviados = 1 AND ultima_actividad < NOW() - INTERVAL '7 days')
  );

COMMENT ON VIEW sys_leads_para_seguimiento IS
  'Leads listos para recibir un follow-up. Columna toque_a_enviar indica 1 (24h) o 2 (7d). Idempotente vía seguimientos_enviados.';


-- ---------------------------------------------------------------------------
-- 3) Índice para acelerar la vista cuando crezca el dataset
-- ---------------------------------------------------------------------------
-- Acelera el filtro por etapa + ultima_actividad. Para ~10k sesiones ya
-- ayuda; bajo eso es opcional.

CREATE INDEX IF NOT EXISTS idx_sys_session_state_seguimientos
  ON sys_session_state (etapa, ultima_actividad)
  WHERE etapa NOT IN ('derivado', 'cerrado');


-- ---------------------------------------------------------------------------
-- Verificación rápida (ejecutar manualmente en Supabase Studio SQL Editor)
-- ---------------------------------------------------------------------------
-- SELECT column_name, data_type, column_default
--   FROM information_schema.columns
--   WHERE table_name = 'sys_session_state' AND column_name = 'seguimientos_enviados';
--
-- SELECT * FROM sys_leads_para_seguimiento LIMIT 5;
--
-- -- Crear lead de prueba para smoke test:
-- INSERT INTO sys_session_state (session_id, etapa, datos_capturados, ultima_actividad, seguimientos_enviados)
-- VALUES (
--   'wa_smoke_seguimiento_001',
--   'diagnostico',
--   '{"nombre":"Smoke Test","equipo":"DTF textil"}'::jsonb,
--   NOW() - INTERVAL '25 hours',
--   0
-- );
--
-- SELECT * FROM sys_leads_para_seguimiento WHERE session_id = 'wa_smoke_seguimiento_001';
-- -- Debe devolver 1 fila con toque_a_enviar = 1.
