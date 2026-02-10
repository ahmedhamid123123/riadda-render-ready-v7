-- scripts/create_riadda_db.sql
-- Creates the database and application role with least privileges.
-- Edit the password before running, or pass via psql -v

BEGIN;

-- Create application role (no superuser, no createdb)
CREATE ROLE :app_user LOGIN PASSWORD ':app_pass' NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;

-- Create the database owned by the default postgres role (administrator)
CREATE DATABASE :db_name OWNER postgres;

\connect :db_name

-- Harden the public schema and grant minimal rights to the app role
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO :app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO :app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO :app_user;

COMMIT;

-- Notes:
-- Use psql -v to substitute :app_user, :app_pass, :db_name, e.g.:
-- psql -U postgres -v db_name=riadda -v app_user=riadda_app -v app_pass='StrongPwd123!' -f scripts/create_riadda_db.sql
