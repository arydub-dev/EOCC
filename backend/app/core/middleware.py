"""HTTP security middleware: request context, headers, size limits, rate limiting.

Designed for defense in depth and secure-by-default behavior. The rate limiter is
an in-memory fixed window suitable for a single instance; multi-instance
deployments should back it with Redis (documented in SECURITY.md).
"""

from __future__ import annotations

import logging
import time
import uuid
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import settings
from app.core.context import (
    client_ip_var,
    correlation_id_var,
    request_id_var,
    user_agent_var,
)

logger = logging.getLogger("eocc.access")


def _client_ip(request: Request) -> str:
    # Honor X-Forwarded-For only for the left-most hop (set by trusted proxy).
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Assign request/correlation IDs, capture client info, emit access logs."""

    async def dispatch(self, request: Request, call_next):  # noqa: ANN001
        request_id = str(uuid.uuid4())
        correlation_id = request.headers.get("x-correlation-id") or request_id
        ip = _client_ip(request)
        ua = request.headers.get("user-agent", "")[:400]

        rid_token = request_id_var.set(request_id)
        cid_token = correlation_id_var.set(correlation_id)
        ip_token = client_ip_var.set(ip)
        ua_token = user_agent_var.set(ua)

        request.state.request_id = request_id
        request.state.correlation_id = correlation_id
        request.state.client_ip = ip

        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "request_error path=%s method=%s request_id=%s ip=%s",
                request.url.path,
                request.method,
                request_id,
                ip,
            )
            raise
        finally:
            request_id_var.reset(rid_token)
            correlation_id_var.reset(cid_token)
            client_ip_var.reset(ip_token)
            user_agent_var.reset(ua_token)

        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Correlation-ID"] = correlation_id
        logger.info(
            "method=%s path=%s status=%s duration_ms=%.1f ip=%s request_id=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            ip,
            request_id,
        )
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Apply a strict set of security response headers (secure by default)."""

    async def dispatch(self, request: Request, call_next):  # noqa: ANN001
        response: Response = await call_next(request)
        h = response.headers
        h.setdefault("X-Content-Type-Options", "nosniff")
        h.setdefault("X-Frame-Options", "DENY")
        h.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        h.setdefault(
            "Permissions-Policy",
            "geolocation=(), camera=(), microphone=(), payment=(), usb=()",
        )
        h.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        h.setdefault("Cross-Origin-Resource-Policy", "same-site")
        # API responses are JSON; a tight CSP prevents any accidental rendering.
        h.setdefault(
            "Content-Security-Policy",
            "default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
        )
        if settings.is_production:
            h.setdefault(
                "Strict-Transport-Security",
                "max-age=63072000; includeSubDomains; preload",
            )
        # Remove server fingerprinting.
        if "server" in h:
            del h["server"]
        return response


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests whose declared body exceeds the configured cap."""

    async def dispatch(self, request: Request, call_next):  # noqa: ANN001
        content_length = request.headers.get("content-length")
        # Uploads have their own (larger) cap enforced in the import layer.
        is_upload = request.url.path.endswith("/import/excel")
        limit = settings.MAX_UPLOAD_BYTES if is_upload else settings.MAX_REQUEST_BYTES
        if content_length and content_length.isdigit() and int(content_length) > limit:
            return JSONResponse(
                status_code=413,
                content={"error": "payload_too_large", "detail": "Request body exceeds limit."},
            )
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Fixed-window per-IP rate limiting with a stricter bucket for auth routes."""

    # Sensitive credential endpoints get a much stricter bucket (brute-force).
    _SENSITIVE = (
        "/auth/login",
        "/auth/login-json",
        "/auth/register",
        "/auth/refresh",
        "/auth/forgot-password",
        "/auth/reset-password",
        "/auth/mfa/",
    )

    def __init__(self, app) -> None:  # noqa: ANN001
        super().__init__(app)
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def _is_sensitive(self, path: str) -> bool:
        return any(s in path for s in self._SENSITIVE)

    async def dispatch(self, request: Request, call_next):  # noqa: ANN001
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)
        path = request.url.path
        # Don't rate-limit health/monitoring probes.
        if path.startswith(("/health", "/metrics", "/live", "/ready")):
            return await call_next(request)

        ip = _client_ip(request)
        sensitive = self._is_sensitive(path)
        bucket = "auth" if sensitive else "default"
        key = f"{ip}:{bucket}"
        limit = (
            settings.RATE_LIMIT_AUTH_PER_MINUTE
            if sensitive
            else settings.RATE_LIMIT_DEFAULT_PER_MINUTE
        )
        now = time.time()
        window_start = now - 60.0

        hits = self._hits[key]
        while hits and hits[0] < window_start:
            hits.popleft()
        if len(hits) >= limit:
            retry = max(1, int(60 - (now - hits[0])))
            return JSONResponse(
                status_code=429,
                content={"error": "rate_limited", "detail": "Too many requests."},
                headers={"Retry-After": str(retry)},
            )
        hits.append(now)
        return await call_next(request)
