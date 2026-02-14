FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    netcat \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Install Python deps
COPY requirements.txt /code/
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Copy project
COPY . /code/

# Entrypoint
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV WEB_CONCURRENCY=3

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
# Ensure the application module path matches the project layout (uses `src` package)
CMD ["sh", "-c", "gunicorn config.wsgi:application --chdir src --bind 0.0.0.0:${PORT} --workers ${WEB_CONCURRENCY}"]
