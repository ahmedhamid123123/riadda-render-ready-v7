# Riadda (refactored)

## Quick start
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Settings
- Dev: `config.settings.dev` (default in manage.py)
- Prod: `config.settings.prod` (set `DJANGO_SETTINGS_MODULE=config.settings.prod`)

## Docker (optional)
Run the application and a Postgres database using Docker Compose (recommended for local development):

1. Copy the example env and edit if needed:

```
copy .env.example .env
# edit .env to set DJANGO_SECRET_KEY and DJANGO_DEBUG
```

2. Build and start services:

```
docker compose up --build -d
```

3. View logs and interact:

```
docker compose logs -f web
docker compose run --rm web python manage.py createsuperuser
```

4. Stop and remove:

```
docker compose down
```

Notes:
- The project includes a `Dockerfile`, `docker-entrypoint.sh`, and `docker-compose.yml`.
- For production, set `DJANGO_DEBUG=False` and provide a strong `DJANGO_SECRET_KEY` via environment variables rather than committing it.

