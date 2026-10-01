-- ============================================================================
-- RuralRefLink - drops the application database
-- Used by:  setup_database.bat --reset
--
-- WITH (FORCE) disconnects any open sessions and requires PostgreSQL 13+.
-- ============================================================================
DROP DATABASE IF EXISTS ruralref WITH (FORCE);
