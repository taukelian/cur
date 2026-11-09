FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./
RUN useradd --create-home appuser \
    && mkdir -p /app/uploads \
    && chown -R appuser:appuser /app

USER appuser
EXPOSE 8000

# Migrations and seeding are idempotent.  The API is deliberately bound only
# to the Docker network; Caddy is the public HTTPS entry point.
CMD ["sh", "-c", "alembic upgrade head && python seed.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
