# API Reference

The EOCC API is a versioned REST API served by the FastAPI backend. This document describes authentication, conventions, and the endpoint catalog. The API is fully described by an OpenAPI schema and interactive documentation:

| Resource | Path |
| --- | --- |
| OpenAPI schema | `/api/v1/openapi.json` |
| Swagger UI | `/docs` |
| ReDoc | `/redoc` |

All application endpoints are mounted under the `/api/v1` prefix. System probes (`/health`, `/live`, `/ready`, `/metrics`, `/`) are served at the root.

## Conventions

- **Format.** Requests and responses are JSON (`Content-Type: application/json`), except file uploads (`multipart/form-data`) and a few text/CSV responses.
- **Timestamps.** ISO 8601 / RFC 3339, UTC.
- **IDs.** Integer primary keys.
- **Tenancy.** Every request is automatically scoped to the authenticated user's organization. Endpoints never expose another tenant's data.

## Authentication

EOCC uses the OAuth2 password flow with JWT access tokens and rotating refresh tokens.

1. Obtain tokens:

   ```http
   POST /api/v1/auth/login-json
   Content-Type: application/json

   { "email": "admin@eocc.gov", "password": "admin123", "remember_me": true }
   ```

   Response:

   ```json
   {
     "access_token": "<jwt>",
     "refresh_token": "<opaque>",
     "token_type": "bearer",
     "expires_in": 900,
     "user": { "id": 1, "email": "admin@eocc.gov", "role": "admin", "...": "..." },
     "permissions": ["Incident.Read", "..."],
     "organization": { "id": 1, "name": "..." },
     "needs_onboarding": false,
     "mfa_required": false
   }
   ```

2. Call protected endpoints with the access token:

   ```http
   GET /api/v1/incidents
   Authorization: Bearer <access_token>
   ```

3. When the access token expires, exchange the refresh token for a new pair:

   ```http
   POST /api/v1/auth/refresh
   Content-Type: application/json

   { "refresh_token": "<opaque>" }
   ```

The refresh token is also delivered as an httpOnly cookie. Refresh rotates the token and revokes the previous one; presenting an already-rotated token revokes the entire session family (theft detection). If a login requires MFA, the response indicates `mfa_required` and the client resubmits with an `mfa_code`.

### `OPTIONS` / form login

`POST /api/v1/auth/login` accepts the standard OAuth2 `application/x-www-form-urlencoded` body (`username`, `password`) for compatibility with the Swagger "Authorize" button.

## Authorization

Authorization is permission-first. Each endpoint requires a specific permission (for example `Incident.Update`), and roles map to permission sets. A request lacking the required permission returns `403`. The caller's permission set is available from `GET /api/v1/auth/me` and is used by the console only to shape the UI. See [SECURITY.md](../SECURITY.md#3-authorization-rbac--permissions).

## Pagination, Filtering, Search, and Sorting

List endpoints that return a `Page<T>` accept a common set of query parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| `page` | int (≥1) | Page number (default 1). |
| `page_size` | int (1–200) | Items per page (default 20). |
| `search` | string | Free-text search over the entity's primary text fields. |
| `sort` | string | Sort field; prefix with `-` for descending (e.g. `-triggered_at`). |
| *(entity filters)* | varies | E.g. `status`, `incident_type`, `severity`, `region`. |

Paginated response envelope:

```json
{
  "items": [ /* ... */ ],
  "total": 128,
  "page": 1,
  "page_size": 20,
  "pages": 7
}
```

## Error Handling

Errors use a consistent JSON envelope and never include stack traces:

```json
{
  "error": "validation_error",
  "detail": "String should have at least 12 characters",
  "request_id": "b1d9…",
  "correlation_id": "9f3a…"
}
```

`detail` is a string for most errors and an array of field errors for request-validation failures. Common status codes:

| Status | Meaning |
| --- | --- |
| `400` | Malformed request. |
| `401` | Missing/invalid/expired credentials. |
| `403` | Authenticated but lacking the required permission. |
| `404` | Resource not found (or outside the caller's tenant). |
| `409` | Conflict (e.g. optimistic-lock version mismatch, duplicate email). |
| `413` | Request or upload exceeds the configured size limit. |
| `422` | Request body/query failed validation. |
| `429` | Rate limit exceeded. |
| `5xx` | Server error (generic; details are logged server-side). |

Every response carries `X-Request-ID` and (if provided) `X-Correlation-ID` headers for tracing.

## Versioning

The API is versioned in the path (`/api/v1`). Backwards-incompatible changes will be introduced under a new version prefix; additive changes (new fields, new endpoints) are made within a version. See [CHANGELOG.md](../CHANGELOG.md).

## Endpoint Catalog

### System (unversioned)

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health` | Service liveness summary and version. |
| GET | `/live` | Liveness probe. |
| GET | `/ready` | Readiness probe (verifies database connectivity). |
| GET | `/metrics` | Prometheus text metrics. |

### Authentication — `/api/v1/auth`

| Method | Path | Permission | Description |
| --- | --- | --- | --- |
| POST | `/auth/login` | — | OAuth2 form login. |
| POST | `/auth/login-json` | — | JSON login (remember-me, MFA). |
| POST | `/auth/register` | — | Register a user/organization. |
| POST | `/auth/refresh` | — | Rotate refresh token, issue new access token. |
| POST | `/auth/logout` | auth | Revoke the current session. |
| POST | `/auth/logout-all` | auth | Revoke all of the caller's sessions. |
| GET | `/auth/sessions` | auth | List the caller's active sessions. |
| DELETE | `/auth/sessions/{id}` | auth | Revoke one of the caller's sessions. |
| POST | `/auth/mfa/setup` | auth | Begin TOTP enrollment (returns secret/URI). |
| POST | `/auth/mfa/enable` | auth | Confirm and enable TOTP. |
| POST | `/auth/mfa/disable` | auth | Disable TOTP. |
| POST | `/auth/change-password` | auth | Change password (revokes other sessions). |
| POST | `/auth/verify-email` | — | Verify email with a token. |
| POST | `/auth/resend-verification` | — | Resend verification token. |
| POST | `/auth/forgot-password` | — | Request a reset token (mock delivery). |
| POST | `/auth/reset-password` | — | Reset password with a token. |
| GET | `/auth/me` | auth | Current user, role, and permissions. |

### Users — `/api/v1/users`

| Method | Path | Permission | Description |
| --- | --- | --- | --- |
| GET | `/users` | `User.Manage` | List users in the organization. |
| POST | `/users` | `User.Manage` | Create a user. |
| PATCH | `/users/{id}` | `User.Manage` | Update a user. |
| *(deactivate)* | `/users/{id}` | `User.Manage` | Deactivate a user (revokes sessions). |

### Workspace — `/api/v1`

| Method | Path | Description |
| --- | --- | --- |
| POST | `/onboarding` | Provision the organization workspace. |
| POST | `/workspace/launch-demo` | Launch a demo workspace. |
| GET | `/workspace` | Current workspace info. |

### Operations

| Module | Base | Representative endpoints |
| --- | --- | --- |
| Mission Control | `/mission-control` | `GET /summary`, `GET /health` |
| Incidents | `/incidents` | `GET ""`, `GET /{id}`, `GET /{id}/timeline`, `POST ""`, `PATCH /{id}`, `DELETE /{id}` |
| Hospitals | `/hospitals` | `GET ""`, `GET /{id}`, `POST ""`, `PATCH /{id}` |
| Shelters | `/shelters` | `GET ""`, `GET /{id}`, `POST ""`, `PATCH /{id}` |
| Resources | `/resources` | `GET ""`, `GET /utilization`, `POST /assignments`, `POST /assignments/{id}/release` |
| Utilities | `/utilities` | `GET ""`, `POST ""`, `PATCH /{id}` |
| Geo | `/geo` | `GET /features` |
| Risk Intelligence | `/risk` | `GET ""`, `POST /generate` |
| Alerts | `/alerts` | `GET ""`, `POST /evaluate`, `POST /{id}/acknowledge`, `POST /{id}/resolve`, `POST /{id}/actions` |
| Simulation Center | `/simulations` | `GET ""`, `GET /{id}`, `POST /run` |
| AI Copilot | `/copilot` | `GET /status`, `POST /ask`, `GET /history` |
| Executive Briefing | `/briefing` | `POST /generate`, `GET /markdown` |
| Data Integration | `/integration` | `GET /overview`, `GET /sources`, `POST /sources`, `POST /import/csv`, `POST /import/excel`, `GET /pipeline`, `GET /jobs` |

### Governance

| Module | Base | Endpoints | Permission |
| --- | --- | --- | --- |
| Audit Center | `/audit` | `GET ""`, `GET /export` | `Audit.View` |
| Security Center | `/security` | `GET /overview`, `GET /login-activity`, `GET /sessions`, `DELETE /sessions/{id}` | `Security.View` / `Security.Manage` |

> Read endpoints require the corresponding `*.Read` permission; mutating endpoints require the corresponding `*.Update`, `*.Manage`, `*.Assign`, `*.Run`, `*.Import`, or `*.Configure` permission. The authoritative mapping lives in `backend/app/core/permissions.py`. For the complete, always-current request/response schemas, consult the OpenAPI docs at `/docs`.
