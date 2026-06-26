"""Per-request context propagated via ContextVars.

Lets any layer (audit logging, structured logs) read the current request id,
correlation id, client IP, and user agent without threading them through every
function signature.
"""

from __future__ import annotations

from contextvars import ContextVar

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)
client_ip_var: ContextVar[str | None] = ContextVar("client_ip", default=None)
user_agent_var: ContextVar[str | None] = ContextVar("user_agent", default=None)


def current_request_id() -> str | None:
    return request_id_var.get()


def current_correlation_id() -> str | None:
    return correlation_id_var.get()


def current_client_ip() -> str | None:
    return client_ip_var.get()


def current_user_agent() -> str | None:
    return user_agent_var.get()
