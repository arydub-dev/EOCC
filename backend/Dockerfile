FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies as root, then drop privileges to run.
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Create an unprivileged user and own the app directory.
RUN addgroup --system --gid 1001 eocc \
    && adduser --system --uid 1001 --ingroup eocc eocc \
    && chown -R eocc:eocc /app

USER eocc

EXPOSE 8000

# Health check uses Python (no curl) so the image stays minimal. Honors $PORT
# (managed hosts inject it) and falls back to 8000 for local/compose runs.
HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=5 \
    CMD sh -c 'python -c "import os,urllib.request,sys; sys.exit(0 if urllib.request.urlopen(\"http://localhost:%s/health\" % os.getenv(\"PORT\",\"8000\"), timeout=4).status==200 else 1)"'

# Shell form so ${PORT} is expanded at runtime (Render/Heroku set it).
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
