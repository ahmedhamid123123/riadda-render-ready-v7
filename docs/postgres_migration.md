PostgreSQL migration and secure setup

This document explains how to migrate from the local SQLite (`db.sqlite3`) to PostgreSQL and how to secure the database.

1) Install PostgreSQL (OS-specific). On Windows, use the installer from https://www.postgresql.org/download/windows/.

2) Create database and a restricted user (recommended):

- Connect to `psql` as a postgres/sysadmin user and run:

```sql
-- create a database owned by an admin role (optional)
CREATE DATABASE riadda;

-- create a dedicated application user with a strong password
CREATE USER riadda_app WITH PASSWORD 'STRONG_RANDOM_PASSWORD';

-- grant only the necessary privileges to the app user
GRANT CONNECT ON DATABASE riadda TO riadda_app;
\c riadda
GRANT USAGE ON SCHEMA public TO riadda_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO riadda_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO riadda_app;
```

Notes:
- Avoid `GRANT ALL` unless you intentionally want the application to be a DBA. Restricting to DML (SELECT/INSERT/UPDATE/DELETE) is safer.
- Use a strong, unique password. Do not commit it to source control.

3) Install the Python driver and dotenv loader in your virtualenv:

```bash
pip install psycopg2-binary python-dotenv
pip freeze > requirements.txt
```

4) Configure environment variables for Django. Recommended variables:

- DJANGO_DB_ENGINE=django.db.backends.postgresql
- DJANGO_DB_NAME=riadda
- DJANGO_DB_USER=riadda_app
- DJANGO_DB_PASS=<your-strong-password>
- DJANGO_DB_HOST=127.0.0.1
- DJANGO_DB_PORT=5432
- DJANGO_SECRET_KEY=<change-this>
- DJANGO_DEBUG=False (in production)

You can put these in a `.env` file (development only) at the project root (same dir as `manage.py`) and the project will load them automatically (the repository includes python-dotenv usage). Example `.env` (DO NOT commit):

```
DJANGO_DB_ENGINE=django.db.backends.postgresql
DJANGO_DB_NAME=riadda
DJANGO_DB_USER=riadda_app
DJANGO_DB_PASS=VeryStrongPassword123!
DJANGO_DB_HOST=127.0.0.1
DJANGO_DB_PORT=5432
DJANGO_SECRET_KEY=replace_with_secure_key
DJANGO_DEBUG=False
```

5) Dump and load data (option A: fixtures)

```bash
# backup current data
python manage.py dumpdata --natural-primary --natural-foreign --exclude auth.permission --exclude contenttypes --exclude sessions > data.json

# create DB tables
python manage.py migrate

# load data
python manage.py loaddata data.json
```

Option B: use `pgloader` or specialized tools for faster/safer migration of large datasets.

6) Secure PostgreSQL (quick checklist):
- Bind PostgreSQL only to localhost or the app server IP (postgresql.conf `listen_addresses`).
- Use `pg_hba.conf` to restrict allowed hosts and authentication methods.
- Enable SSL between app and DB (set `sslmode=require` in your DB connection if needed).
- Use firewall rules to block external access to the DB port (5432).
- Rotate credentials and use a secrets manager (Azure Key Vault, AWS Secrets Manager, or environment variables managed by the host).
- Regular backups and monitoring (pg_basebackup, logical backups, or cloud-managed DB snapshots).

7) After migration, test the app thoroughly (login, create agents, adjust balances, reports, file export).

Questions / I can do for you
- I can update `settings/base.py` (already done) and add `psycopg2-binary` to `requirements.txt` (already done).
- I can create an example `.env.example` with recommended variable names.
- I can generate the SQL for creating a least-privilege user (done above).

If you want, I can also run `python manage.py migrate` here (not possible from the agent), but I can produce the exact commands and files you need to run locally. Let me know if you want an `.env.example` file added.
