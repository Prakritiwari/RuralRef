-- ============================================================================
-- RuralRefLink - idempotent PostgreSQL bootstrap
-- Creates the application role and database if they do not already exist.
-- Safe to run multiple times.
--
-- Manual usage:
--   "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d postgres \
--       -f scripts/bootstrap_database.sql
-- ============================================================================

-- 1) Application role -------------------------------------------------------
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = 'ruralref') THEN
        CREATE ROLE ruralref WITH LOGIN PASSWORD 'ruralref';
        RAISE NOTICE 'Created role: ruralref';
    ELSE
        RAISE NOTICE 'Role already exists: ruralref (left unchanged)';
    END IF;
END
$$;

-- 2) Application database ---------------------------------------------------
--    CREATE DATABASE cannot run inside a transaction or a DO block, so the
--    statement is generated on the fly and executed via psql's \gexec.
SELECT 'CREATE DATABASE ruralref OWNER ruralref'
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'ruralref')
\gexec
