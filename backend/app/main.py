"""EOCC FastAPI application entrypoint."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import api_router
from app.config import settings
from app.core.audit_guard import register_audit_guard
from app.core.context import current_correlation_id, current_request_id
from app.core.middleware import (
    BodySizeLimitMiddleware,
    RateLimitMiddleware,
    RequestContextMiddleware,
    SecurityHeadersMiddleware,
)
from app.core.tenancy import register_tenancy
from app.database import Base, SessionLocal, engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
logger = logging.getLogger("eocc")

# Register ORM event listeners (tenant scoping + immutable audit).
register_tenancy()
register_audit_guard()

# Lightweight in-process counters for the /metrics endpoint.
_METRICS = {"requests_total": 0, "errors_total": 0, "auth_failures_total": 0}


@asynccontextmanager
async def lifespan(app: FastAPI):
    import app.models  # noqa: F401  (register models before create_all)

    logger.info("Creating database schema if needed...")
    Base.metadata.create_all(bind=engine)

    if settings.SEED_ON_STARTUP:
        from app.seed import seed_database

        db = SessionLocal()
        try:
            logger.info("Seeding database (if empty)...")
            result = seed_database(db)
            logger.info("Seed result: %s", result)
        except Exception:  # noqa: BLE001
            logger.exception("Seeding failed")
            db.rollback()
        finally:
            db.close()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Emergency Operations Command Center — a security-hardened decision-support "
        "platform that transforms fragmented emergency data into coordinated action."
    ),
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Middleware order matters: the last added runs first (outermost).
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(BodySizeLimitMiddleware)
app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origin_regex=r"https?://localhost(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Correlation-ID"],
)


def _error_body(code: str, detail: object) -> dict:
    return {
        "error": code,
        "detail": detail,
        "request_id": current_request_id(),
        "correlation_id": current_correlation_id(),
    }


@app.middleware("http")
async def _count_requests(request: Request, call_next):  # noqa: ANN001
    _METRICS["requests_total"] += 1
    response = await call_next(request)
    if response.status_code >= 500:
        _METRICS["errors_total"] += 1
    if response.status_code in (401, 403) and "/auth/" in request.url.path:
        _METRICS["auth_failures_total"] += 1
    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:  # noqa: ARG001
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body("http_error", exc.detail),
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:  # noqa: ARG001
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_error_body("validation_error", exc.errors()),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:  # noqa: ARG001
    # Never leak internals/stack traces to clients.
    logger.exception("Unhandled error processing %s", request.url.path)
    return JSONResponse(
        status_code=500, content=_error_body("internal_error", "Internal server error")
    )


# ── Monitoring / health probes ──
@app.get("/health", tags=["System"])
def health() -> dict:
    return {"status": "ok", "service": settings.PROJECT_NAME, "version": settings.VERSION}


@app.get("/live", tags=["System"])
def liveness() -> dict:
    return {"status": "alive"}


@app.get("/ready", tags=["System"])
def readiness() -> JSONResponse:
    """Readiness probe — verifies database connectivity."""
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return JSONResponse({"status": "ready", "database": "ok"})
    except Exception:  # noqa: BLE001
        logger.exception("Readiness check failed")
        return JSONResponse(status_code=503, content={"status": "not_ready", "database": "error"})
    finally:
        db.close()


@app.get("/metrics", tags=["System"], response_class=PlainTextResponse)
def metrics() -> str:
    """Minimal Prometheus-style metrics (text exposition format)."""
    lines = [
        "# HELP eocc_requests_total Total HTTP requests handled.",
        "# TYPE eocc_requests_total counter",
        f"eocc_requests_total {_METRICS['requests_total']}",
        "# HELP eocc_errors_total Total 5xx responses.",
        "# TYPE eocc_errors_total counter",
        f"eocc_errors_total {_METRICS['errors_total']}",
        "# HELP eocc_auth_failures_total Total authentication failures.",
        "# TYPE eocc_auth_failures_total counter",
        f"eocc_auth_failures_total {_METRICS['auth_failures_total']}",
    ]
    return "\n".join(lines) + "\n"


@app.get("/", tags=["System"])
def root() -> dict:
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "api": settings.API_V1_PREFIX,
        "ai_engine": "openai" if settings.ai_enabled else "deterministic",
    }


app.include_router(api_router, prefix=settings.API_V1_PREFIX)
