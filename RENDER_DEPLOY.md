# Deploy Riadda on Render (Docker)

This project is prepared to run on Render using Docker + Gunicorn + WhiteNoise.

## Create the services
1) Create a **PostgreSQL** database on Render.
2) Create a **Web Service** → choose **Docker**.

## Environment variables (Web Service)
Minimum required:
- `DJANGO_ENV=production`
- `DJANGO_SETTINGS_MODULE=config.settings.prod`
- `DJANGO_DEBUG=False`
- `DJANGO_SECRET_KEY=<long random value>`
- `DJANGO_RECEIPT_HMAC_KEY=<long random value>`
- `DJANGO_ALLOWED_HOSTS=<your-service>.onrender.com`
- `DJANGO_CSRF_TRUSTED_ORIGINS=https://<your-service>.onrender.com`

Database:
- Use Render's provided `DATABASE_URL` (recommended). If you use it, you do **not** need `DJANGO_DB_*`.

Optional:
- `WEB_CONCURRENCY=3` (scale with instance size)
- `DJANGO_DB_CONN_MAX_AGE=600`

## Start command
If you deploy using Docker, Render will run the image CMD which already starts Gunicorn.

## Notes
- Migrations + `collectstatic` run automatically on container startup.
- Static files are served by WhiteNoise.

## Troubleshooting
- **400 Bad Request**: `DJANGO_ALLOWED_HOSTS` doesn't include your Render domain.
- **CSRF failures**: Add your full Render URL to `DJANGO_CSRF_TRUSTED_ORIGINS`.
