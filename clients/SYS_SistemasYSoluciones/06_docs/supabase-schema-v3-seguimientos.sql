-- ===========================================================================
-- SYS — Supabase schema v3 — Seguimientos a 4 días (1 toque)
-- Fecha: 2026-06-23
-- Hereda: supabase-schema-v2-seguimientos.sql (columna seguimientos_enviados ya existe)
--
-- Cambio vs v2:
--   - Antes: 2 toques (24h + 7d) con tracking 0→1→2
--   - Ahora: 1 toque único a los 4 días (pedido Edgardo, mail 2026-06-23)
--
-- Idempotente: se puede correr múltiples veces sin error.
-- ===========================================================================


-- ---------------------------------------------------------------------------
-- 1) Reemplazar la vista sys_leads_para_seguimiento
-- ---------------------------------------------------------------------------
-- Devuelve solo leads que cumplen:
--   - etapa NO terminal ('derivado' o 'cerrado')
--   - seguimientos_enviados = 0  (idempotente: nunca dos toques)
--   - ultima_actividad < NOW() - 4 días
--
-- DROP necesario porque la v2 tenía columna toque_a_enviar que la v3 elimina.
-- Postgres no permite quitar columnas vía CREATE OR REPLACE VIEW (ERROR 42P16).

DROP VIEW IF EXISTS sys_leads_para_seguimiento;

CREATE VIEW sys_leads_para_seguimiento AS
SELECT
  session_id,
  perfil,
  etapa,
  datos_capturados,
  productos_mostrados,
  ultima_actividad,
  seguimientos_enviados
FROM sys_session_state
WHERE
  etapa NOT IN ('derivado', 'cerrado')
  AND seguimientos_enviados = 0
  AND ultima_actividad < NOW() - INTERVAL '4 days';

COMMENT ON VIEW sys_leads_para_seguimiento IS
  'v3 (2026-06-23): leads listos para el ÚNICO toque de seguimiento a los 4 días. Idempotente vía seguimientos_enviados = 0.';


-- ---------------------------------------------------------------------------
-- 2) Verificación rápida (Supabase Studio SQL Editor)
-- ---------------------------------------------------------------------------
-- SELECT * FROM sys_leads_para_seguimiento LIMIT 5;
--
-- -- Crear lead de prueba (cumple condición: 5 días sin actividad):
-- INSERT INTO sys_session_state (session_id, etapa, datos_capturados, ultima_actividad, seguimientos_enviados)
-- VALUES (
--   'wa_smoke_seguimiento_4d_001',
--   'diagnostico',
--   '{"nombre":"Juan Carlos","equipo":"DTF textil"}'::jsonb,
--   NOW() - INTERVAL '5 days',
--   0
-- )
-- ON CONFLICT (session_id) DO UPDATE
--   SET ultima_actividad = EXCLUDED.ultima_actividad,
--       seguimientos_enviados = 0,
--       etapa = EXCLUDED.etapa;
--
-- SELECT * FROM sys_leads_para_seguimiento WHERE session_id = 'wa_smoke_seguimiento_4d_001';
-- -- Debe devolver 1 fila.
--
-- -- Tras correr el workflow v2 (Execute manual), verificar:
-- SELECT session_id, seguimientos_enviados, etapa, ultima_actividad
-- FROM sys_session_state WHERE session_id = 'wa_smoke_seguimiento_4d_001';
-- -- Debe estar seguimientos_enviados = 1, etapa = 'cerrado', ultima_actividad = NOW().
-- -- Y NO debe volver a aparecer en sys_leads_para_seguimiento.
--
-- -- Cleanup:
-- DELETE FROM sys_session_state WHERE session_id LIKE 'wa_smoke_seguimiento_4d_%';
