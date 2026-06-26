#!/usr/bin/env bash
#
# EOCC local development bootstrapper.
#
# Starts the FastAPI backend (SQLite, hot reload) and the Next.js frontend
# (hot reload) together, wires the frontend to the local API, and seeds demo
# data on first run. Press Ctrl-C to stop both.
#
# Usage:  ./scripts/dev.sh
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"

log() { printf "\033[1;36m[dev]\033[0m %s\n" "$*"; }

cleanup() {
  log "Shutting down..."
  [[ -n "${BACKEND_PID:-}" ]] && kill "$BACKEND_PID" 2>/dev/null || true
  [[ -n "${FRONTEND_PID:-}" ]] && kill "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# ── Backend ──
log "Preparing backend (Python)..."
cd "$ROOT/backend"
if [[ ! -d .venv ]]; then
  log "Creating virtualenv (.venv)..."
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

export ENVIRONMENT="${ENVIRONMENT:-development}"
export DATABASE_URL="${DATABASE_URL:-sqlite:///./eocc.db}"
export SEED_ON_STARTUP="${SEED_ON_STARTUP:-true}"
export COOKIE_SECURE="${COOKIE_SECURE:-false}"

log "Starting backend on http://localhost:${BACKEND_PORT} (docs at /docs)"
uvicorn app.main:app --reload --port "$BACKEND_PORT" &
BACKEND_PID=$!

# ── Frontend ──
log "Preparing frontend (Node)..."
cd "$ROOT/frontend"
if [[ ! -d node_modules ]]; then
  log "Installing npm dependencies..."
  npm install
fi
echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:${BACKEND_PORT}/api/v1" > .env.local

log "Starting frontend on http://localhost:${FRONTEND_PORT}"
npm run dev -- --port "$FRONTEND_PORT" &
FRONTEND_PID=$!

log "EOCC is starting. Frontend: http://localhost:${FRONTEND_PORT}  API: http://localhost:${BACKEND_PORT}/docs"
wait
