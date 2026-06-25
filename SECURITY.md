# EOCC Security Architecture

This document describes the security design of the Emergency Operations Command
Center (EOCC). It is written for engineers, operators, and reviewers evaluating
the platform for deployment in government or enterprise environments handling
operationally sensitive information.

Security is treated as a core architectural property, not a feature bolt-on. The
design follows **Zero Trust**, **Least Privilege**, **Defense in Depth**,
**Secure by Default**, and **Explicit Access**.

> Scope note: this is a reference implementation. Email verification and password
> reset use mock delivery (tokens are returned by the API for evaluation). Items
> intended for production wiring are called out under "Known limitations".

---

## 1. Authentication

- **Password hashing:** Argon2id (memory-hard, 64 MiB / 3 iterations / parallelism 2)
  via `passlib`. Legacy bcrypt hashes are still verified and **transparently
  upgraded** to Argon2id on the user's next successful login. Plaintext passwords
  are never stored or logged.
- **Configurable password policy:** minimum length (default 12) plus
  upper/lower/digit/symbol requirements, enforced on registration, password
  reset, password change, and admin-created users.
- **Account lockout:** after `MAX_FAILED_LOGINS` (default 5) failures an account
  is locked for `LOCKOUT_MINUTES` (default 15). Every attempt is recorded in an
  append-only `login_attempts` table.
- **Access tokens:** short-lived JWTs (default 15 min) carrying `sub`, `role`,
  `org`, `type`, `iat`, `nbf`, `exp`, and a unique `jti`. Token `type` is checked
  on every request so refresh tokens cannot be used as access tokens.
- **Refresh tokens:** opaque 384-bit random strings. Only a **keyed HMAC-SHA-256
  hash** is stored server-side (`user_sessions`), so a database leak alone cannot
  reconstruct valid tokens.
- **Token rotation + theft detection:** every refresh issues a new token and
  revokes the old one. Presenting an already-rotated token revokes the entire
  session *family* — the canonical refresh-token replay defense.
- **MFA (TOTP):** optional time-based one-time passwords (RFC 6238). Per-user
  secrets are encrypted at rest. Self-service enroll / confirm / disable flow.
- **Email verification & password reset:** token-based flows (mock delivery).

## 2. Sessions

- Server-side session store enables **logout (current)**, **logout-all**, a
  **device/session list**, and per-session **revocation**.
- Each session records IP address, user agent, derived device label, issue/expiry
  and last-used timestamps for visibility and forensics.
- Refresh tokens are delivered as an **httpOnly cookie** (`Secure` + `SameSite`
  configurable, secure-by-default in production) and additionally returned in the
  body to support cross-origin SPA development. Production should rely on the
  cookie. Access tokens are sent as `Authorization: Bearer`.
- Password change / reset and account deactivation **revoke all other sessions**.

## 3. Authorization (RBAC + permissions)

- Roles: **Administrator, Emergency Manager, Analyst, Executive, Viewer**.
- Authorization is **permission-first**. Endpoints declare a required permission
  (e.g. `Incident.Update`, `Hospital.Manage`, `Simulation.Run`,
  `Integration.Configure`, `Report.Export`, `Audit.View`, `Security.View`).
  Roles map to permission sets in `app/core/permissions.py`.
- Enforcement is **server-side only** via the `require_permission(...)` FastAPI
  dependency. The frontend reads the user's permissions (from `/auth/me`) purely
  to shape the UI; it is never trusted for access decisions.
- Least privilege by construction: Viewer is read-only; Executive adds reporting
  and security visibility; Manager adds operational mutation; Admin holds all.

## 4. Multi-tenant isolation

- Every operational entity carries an `organization_id`.
- A SQLAlchemy `do_orm_execute` listener (`app/core/tenancy.py`) injects a
  `WHERE organization_id = <current org>` predicate into **every** ORM `SELECT`,
  scoped from the authenticated user's organization bound to the session. This
  makes cross-tenant reads impossible by default rather than by remembering to
  filter.
- Writes set `organization_id` from the authenticated user's context — clients
  cannot assign records to another tenant.
- Session and login-attempt queries that fall outside the auto-filter set are
  explicitly scoped by `organization_id` in the Security Center service.

## 5. API hardening

- **Request/correlation IDs:** every request gets an `X-Request-ID`; an incoming
  `X-Correlation-ID` is honored and echoed. Both are propagated to logs and audit
  records via ContextVars.
- **Security headers** (middleware + edge proxy): CSP, `X-Frame-Options: DENY`,
  `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy`,
  COOP/CORP, and HSTS in production. Server identification headers are removed.
- **Rate limiting:** in-memory fixed-window limiter, with a stricter bucket for
  sensitive credential endpoints (login/register/refresh/reset/MFA). The bundled
  nginx proxy adds an independent edge limit. (Use Redis for multi-instance.)
- **Request size limits** and **pagination caps** (`page_size <= 200`).
- **Structured errors:** uniform JSON `{error, detail, request_id, correlation_id}`.
  Stack traces are never returned to clients; unhandled errors log server-side.
- **API versioning:** all routes under `/api/v1`.

## 6. File-upload security

For CSV/Excel imports (`app/services/file_security.py`):
- Extension and content-type (MIME) allow-lists; xlsx magic-byte check.
- Hard size cap (`MAX_UPLOAD_BYTES`) and row cap (`MAX_IMPORT_ROWS`).
- **ZIP-bomb protection** for xlsx: entry count, total decompressed size, and
  per-entry compression-ratio limits.
- **Schema validation** of required columns before any row is imported.
- **CSV-injection neutralization:** cells beginning with `= + - @` (or control
  chars) are prefixed with `'` on import and on export.
- Uploads are processed in memory / `tmpfs`; no untrusted file persists to disk.
  A virus-scanning hook is the documented extension point.

## 7. Secrets management

- No secrets are hardcoded. All come from the environment / `.env`.
- **Fail-closed in production:** the app refuses to start if `SECRET_KEY` is the
  default or `< 32` chars, or if `ENCRYPTION_KEY` is unset.
- Distinct secrets for JWT signing, refresh-token HMAC, and field encryption.
- Secrets are never logged; audit detail is redacted for password/secret/token
  keys.

## 8. Database security

- Parameterized queries via SQLAlchemy ORM (no string-built SQL) → no SQLi.
- **Field encryption at rest** (Fernet / AES-128-CBC + HMAC) for connector
  secrets and MFA seeds. Secret values are never serialized back to clients
  (`has_secret` boolean only).
- **Audit columns** on every table: `created_at`, `updated_at`, `created_by_id`,
  `updated_by_id`.
- **Soft delete** for critical entities (incidents, data sources) — rows are
  hidden from all reads but retained for forensics.
- **Optimistic locking** on incidents via a `version` column; conflicting
  concurrent updates return `409` instead of silently overwriting.

## 9. Audit logging

- **Immutable / append-only:** an ORM `before_flush` guard rejects any UPDATE or
  DELETE of `audit_logs` / `login_attempts`.
- Each entry captures timestamp, actor, organization, IP, user agent, action,
  category, entity type/id, **old/new values**, and correlation id.
- Logged events include authentication (login/logout/failed/locked), password
  reset/change, MFA changes, role/user management, incident changes, data
  imports, configuration changes, and exports.
- The **Audit Center** UI supports filtering and CSV export (injection-safe).

## 10. Security Center

`/app/security` (permission `Security.View`) surfaces an organization security
**score + grade**, MFA adoption, active sessions, failed/successful logins (24h),
audit/security event counts, the enforced password policy, and prioritized
**recommendations**. Users manage their own sessions and MFA; admins
(`Security.Manage`) can revoke any organization session.

## 11. Data classification

Entities support a classification (`public`, `internal`, `confidential`,
`restricted`); incidents default to `confidential`. This provides the hook for
differentiated handling/retention policies.

## 12. Logging & monitoring

- Structured logs with a dedicated **SECURITY** logger for security-category
  events. Passwords, secrets, tokens, and API keys are never logged.
- Probes: `/health`, `/live`, `/ready` (verifies DB connectivity).
- `/metrics` exposes request, error, and auth-failure counters in Prometheus
  text format.

## 13. Deployment security

- Containers run as **non-root**; minimal base images.
- `read_only` root filesystem + `tmpfs` for backend/frontend; `no-new-privileges`
  on all services.
- **Tier separation:** only the reverse proxy is published. The database has no
  host port and lives on an internal network. The proxy applies edge rate limits
  and security headers and is the single ingress (TLS-terminating in production).
- Health checks use Python/`pg_isready` (no extra tooling in images).

## 14. Dependency management

- All Python and Node dependencies are version-pinned.
- Recommended supply-chain workflow:
  - `pip-audit` (Python) and `npm audit` (Node) in CI.
  - SBOM generation, e.g. `pip install cyclonedx-bom && cyclonedx-py` and
    `npx @cyclonedx/cyclonedx-npm`.
  - Container image scanning (e.g. Trivy/Grype) in the build pipeline.

## 15. Incident response (operational)

1. **Contain:** disable the affected account (revokes sessions) and/or use
   admin session revocation in the Security Center.
2. **Investigate:** pivot on `correlation_id` across audit logs and structured
   logs; review `login_attempts` and active sessions.
3. **Rotate:** rotate `SECRET_KEY` / `REFRESH_TOKEN_SECRET` (invalidates tokens)
   and `ENCRYPTION_KEY` (with re-encryption) as needed.
4. **Recover & review:** restore from backups if required; capture findings via
   the (immutable) audit trail.

## 16. Security assumptions

- TLS is terminated at the proxy/load balancer in production (`COOKIE_SECURE`,
  HSTS enabled).
- The reverse proxy is the only public ingress; backend/db are not exposed.
- A single trusted proxy sets `X-Forwarded-For` (left-most hop is used for IPs).
- Operators supply strong, unique secrets and rotate them per policy.

## 17. Known limitations

- Email verification and password reset use **mock delivery** (no SMTP); reset
  tokens are returned by the API for evaluation. Wire a mailer for production.
- Rate limiting and metrics are **in-process**; use Redis + a metrics backend in
  multi-instance deployments.
- Field encryption uses a single active key; key-rotation re-encryption is a
  documented operational step, not yet automated.
- MFA does not yet include backup/recovery codes.
- No automated AV scanning of uploads (hook provided).
