-- =============================================================================
-- CLZ Collazo — Round-Robin manual cal.com → Google Calendar
-- =============================================================================
-- Ejecutar en la DB Postgres del cliente Collazo (credencial n8n `Collazo`,
-- id `HRV9xsfYlr934XEB`). Idempotente: usar `CREATE TABLE IF NOT EXISTS` y
-- `INSERT ... ON CONFLICT DO NOTHING` para poder re-correr sin error.
--
-- Tablas:
--   1) clz_round_robin_state    — singleton con el último asignado y pausas
--   2) clz_event_type_routing   — override por event-type (matias|fabian|round-robin)
--   3) clz_event_assignment     — mapping booking cal.com ↔ event_id Google Calendar
-- =============================================================================


-- -----------------------------------------------------------------------------
-- 1) Singleton state del round-robin
-- -----------------------------------------------------------------------------
-- Una sola fila (id = 1). El UPDATE atómico desde n8n alterna `last_assigned`
-- usando un CASE, y respeta los flags de pausa (vacaciones).

CREATE TABLE IF NOT EXISTS clz_round_robin_state (
  id              SMALLINT PRIMARY KEY DEFAULT 1,
  last_assigned   TEXT NOT NULL CHECK (last_assigned IN ('matias','fabian')),
  total_count     INTEGER NOT NULL DEFAULT 0,
  matias_paused   BOOLEAN NOT NULL DEFAULT FALSE,
  fabian_paused   BOOLEAN NOT NULL DEFAULT FALSE,
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT clz_rr_singleton CHECK (id = 1)
);

-- Seed: arrancamos con 'fabian' para que el PRIMER booking real alterne a 'matias'.
INSERT INTO clz_round_robin_state (id, last_assigned)
VALUES (1, 'fabian')
ON CONFLICT (id) DO NOTHING;


-- -----------------------------------------------------------------------------
-- 2) Routing por event-type (override del round-robin)
-- -----------------------------------------------------------------------------
-- Cada slug puede mapear a:
--   - 'matias'       → fuerza la asignación a Matías (skip RR)
--   - 'fabian'       → fuerza la asignación a Fabián (skip RR + move flow)
--   - 'round-robin'  → entra al UPDATE atómico
-- Cuando Matías confirme qué servicios son exclusivos, se hace `UPDATE` aquí
-- sin tocar n8n.

CREATE TABLE IF NOT EXISTS clz_event_type_routing (
  event_type_slug TEXT PRIMARY KEY,
  target          TEXT NOT NULL CHECK (target IN ('matias','fabian','round-robin')),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Seed con los 9 event-types del TEAM de cal.com (team id 256131, slug
-- 'collazo-servicio'), que son los links que entrega el agente desde 2026-08-05.
-- Routing confirmado con Matías (2026-06-10): todos round-robin EXCEPTO
-- 'servicio-electrico' y 'reparacion-de-calefon' que son exclusivos de Matías.
--
-- ⚠️ CORREGIDO 2026-08-05: el seed original usaba los slugs de los event-types
-- PERSONALES ('reparacion-calefon', 'instalacion-calefon'). Los del team llevan
-- "de" en el medio y no matcheaban -> caían al default 'round-robin'. El caso
-- grave era 'reparacion-de-calefon': se habría repartido con Fabián cuando debe
-- ser exclusivo de Matías. Verificado contra la API de cal.com; ver
-- 06_docs/diagnostico-round-robin-calcom-2026-08-05.md §6.
--
-- Se conservan además los 2 slugs personales viejos: durante meses las reservas
-- entraron por ahí (27 bookings de 'reparacion-calefon' en los últimos 180 días)
-- y podrían seguir llegando de links que el cliente tenga guardados.
INSERT INTO clz_event_type_routing (event_type_slug, target) VALUES
  -- Team (vigentes)
  ('instalacion-aire',                   'round-robin'),
  ('reparacion-aire-acondicionado',      'round-robin'),
  ('mantenimiento-aire-acondicionado',   'round-robin'),
  ('desmontaje-aire-acondicionado',      'round-robin'),
  ('instalacion-de-calefon',             'round-robin'),
  ('desmontaje-de-calefon',              'round-robin'),
  ('desmontaje-instalacion-de-calefon',  'round-robin'),
  ('reparacion-de-calefon',              'matias'),
  ('servicio-electrico',                 'matias'),
  -- Personales (legacy, por links viejos que sigan circulando)
  ('instalacion-calefon',                'round-robin'),
  ('reparacion-calefon',                 'matias')
ON CONFLICT (event_type_slug) DO NOTHING;


-- -----------------------------------------------------------------------------
-- 3) Mapping booking cal.com ↔ Google Calendar event
-- -----------------------------------------------------------------------------
-- PK por `cal_com_uid` garantiza idempotencia: si cal.com reintenta el webhook,
-- el INSERT cae a ON CONFLICT DO NOTHING y no se duplica el move.
--
-- `gcal_event_id_matias` se llena solo cuando se mueve a Fabián (es el id que
-- borramos del calendar de Matías; útil para forensics).
-- `gcal_event_id_fabian` se llena solo en el move (es el evento que creamos
-- en Fabián; lo necesitamos para update/delete en RESCHEDULED/CANCELLED).

CREATE TABLE IF NOT EXISTS clz_event_assignment (
  cal_com_uid          TEXT PRIMARY KEY,
  assigned_to          TEXT NOT NULL CHECK (assigned_to IN ('matias','fabian')),
  cal_com_event_type   TEXT,
  gcal_event_id_matias TEXT,
  gcal_event_id_fabian TEXT,
  start_time           TIMESTAMPTZ NOT NULL,
  end_time             TIMESTAMPTZ NOT NULL,
  attendee_name        TEXT,
  attendee_email       TEXT,
  attendee_phone       TEXT,
  status               TEXT NOT NULL DEFAULT 'created'
                       CHECK (status IN ('created','rescheduled','cancelled','error')),
  raw_payload          JSONB NOT NULL,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_clz_assignment_start  ON clz_event_assignment(start_time);
CREATE INDEX IF NOT EXISTS idx_clz_assignment_status ON clz_event_assignment(status);


-- =============================================================================
-- Queries operativas (referencia — pegar en Supabase Studio)
-- =============================================================================

-- Ver estado del round-robin:
--   SELECT * FROM clz_round_robin_state;

-- Pausar a Matías (vacaciones):
--   UPDATE clz_round_robin_state SET matias_paused = TRUE  WHERE id = 1;

-- Reanudar a Matías:
--   UPDATE clz_round_robin_state SET matias_paused = FALSE WHERE id = 1;

-- Forzar que un servicio sea solo de Fabián:
--   UPDATE clz_event_type_routing SET target = 'fabian' WHERE event_type_slug = 'servicio-electrico';

-- Volver un servicio a round-robin:
--   UPDATE clz_event_type_routing SET target = 'round-robin' WHERE event_type_slug = 'servicio-electrico';

-- Últimos 10 bookings procesados:
--   SELECT cal_com_uid, assigned_to, status, gcal_event_id_fabian IS NOT NULL AS moved,
--          start_time AT TIME ZONE 'America/Montevideo' AS inicio_mvd, created_at
--   FROM clz_event_assignment
--   ORDER BY created_at DESC
--   LIMIT 10;

-- Conteo por hermano en los últimos 30 días:
--   SELECT assigned_to, COUNT(*) AS bookings
--   FROM clz_event_assignment
--   WHERE created_at > NOW() - INTERVAL '30 days'
--   GROUP BY assigned_to;
