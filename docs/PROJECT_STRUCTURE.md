# Project Structure

This document is a map of the repository so a new contributor can find their way around in minutes. For *how* the pieces fit together at runtime, read [ARCHITECTURE.md](../ARCHITECTURE.md).

## Top level

```
EOCC/
├── backend/              FastAPI application (Python 3.12)
├── frontend/             Next.js 15 application (TypeScript, React 19)
├── deploy/               Deployment assets (nginx.conf)
├── docs/                 Extended documentation
├── docker-compose.yml    Hardened multi-service deployment
├── .env.example          Annotated environment template
├── README.md             Project homepage
├── ARCHITECTURE.md       System design and data flow
├── SECURITY.md           Security architecture & disclosure policy
├── CONTRIBUTING.md       Contributor guide
├── ROADMAP.md            Forward-looking plan
├── CHANGELOG.md          Versioned history
├── CODE_OF_CONDUCT.md    Community standards
├── LICENSE               Apache License 2.0
└── NOTICE                Copyright attribution
```

## Backend (`backend/`)

```
backend/
├── Dockerfile            Non-root, slim production image
├── requirements.txt      Python dependencies
└── app/
    ├── main.py           App factory: middleware, routers, exception handlers, probes
    ├── config.py         Pydantic settings (env-driven), secret enforcement
    ├── database.py       Engine/session setup, Base, session dependency
    ├── api/
    │   ├── router.py     Aggregates all v1 routers under /api/v1
    │   └── routes/       One module per domain (see below)
    ├── core/             Cross-cutting infrastructure (see below)
    ├── engines/          Deterministic decision logic (pure, testable)
    ├── services/         Use-case orchestration between routes and the DB
    ├── models/           SQLAlchemy ORM models and enums
    ├── schemas/          Pydantic request/response models
    └── seed/             Synthetic demo data generation
```

### `app/api/routes/`

One router per module — the HTTP surface of the platform:

`auth` · `workspace` · `mission` · `incidents` · `hospitals` · `shelters` · `resources` · `utilities` · `geo` · `risk` · `alerts` · `simulations` · `copilot` · `briefing` · `integration` · `audit` · `security`.

Routes stay thin: they declare the required permission, validate input via `schemas/`, and delegate to `services/`.

### `app/core/`

| File | Responsibility |
| --- | --- |
| `security.py` | Argon2id hashing, JWT issue/verify, Fernet encryption, TOTP MFA. |
| `permissions.py` | `Permission` catalog and the `ROLE_PERMISSIONS` map. |
| `deps.py` | FastAPI dependencies: current user, permission requirements. |
| `tenancy.py` | ORM event listener that auto-scopes queries by `organization_id` and hides soft-deleted rows. |
| `middleware.py` | Request context, security headers, body-size limit, rate limiting. |
| `context.py` | `ContextVar` propagation of request/correlation IDs, IP, user agent. |
| `audit_guard.py` | `before_flush` guard enforcing append-only audit/login tables. |

### `app/engines/` (deterministic core)

| File | Responsibility |
| --- | --- |
| `scoring.py` | Hospital stress, shelter utilization, resource readiness scoring. |
| `risk_engine.py` | Multi-factor risk assessment by category. |
| `recommendations.py` | Resource-to-incident recommendation logic. |
| `simulation_engine.py` | What-if scenario projection. |
| `snapshot.py` | Operational snapshot/aggregation for Mission Control. |
| `copilot.py` / `briefing.py` | Grounded prompt assembly and local fallback generation. |

These modules are pure functions over inputs — no I/O — which makes them straightforward to unit-test.

### `app/services/`

Orchestration layer (`alert_service`, `mission_service`, `risk_service`, `simulation_service`, `integration_service`, `session_service`, `security_service`, `audit_service`, `provisioning`, `file_security`, `analytics`, `scoring_service`, `copilot_service`, `briefing_service`, `common`). Services compose engines, models, and the database to fulfill a use case, and own side effects (persistence, audit writes, encryption).

### `app/models/` and `app/schemas/`

- `models/models.py` + `models/enums.py` — the 19 ORM entities and shared enums.
- `schemas/` — Pydantic models grouped by area (`auth`, `entities`, `ops`, `mission`, `ai`, `integration`, `audit`, `security`, `common`). These define the API contract and validation rules.

## Frontend (`frontend/`)

```
frontend/
├── Dockerfile            Standalone Next.js production image
├── next.config.mjs       Next.js config
├── tailwind.config.ts    Design tokens / theme
├── public/               Static assets
└── src/
    ├── app/              App Router routes (see below)
    ├── components/       Reusable UI and feature components
    └── lib/              Client utilities and data layer
```

### `src/app/`

| Path | Purpose |
| --- | --- |
| `layout.tsx`, `providers.tsx`, `globals.css` | Root layout, context providers, global styles. |
| `(marketing)/` | Public marketing site (route group, no app chrome). |
| `app/` | Authenticated console: the operational modules. |
| `login/`, `register/`, `onboarding/` | Auth and workspace provisioning flows. |
| `forgot-password/`, `reset-password/` | Password recovery flows. |

### `src/components/`

Feature and UI building blocks: `shell.tsx`, `topbar.tsx`, `toolbar.tsx`, `page-header.tsx`, `data-table.tsx`, `score-ring.tsx`, `operations-map.tsx`, `command-palette.tsx`, `demo-banner.tsx`, `data-source-badge.tsx`, `connected-onboarding.tsx`, plus `ui/` (primitives) and `marketing/` (landing-page sections).

### `src/lib/`

| File | Responsibility |
| --- | --- |
| `api.ts` | Typed fetch client, auth header injection, error normalization. |
| `auth.tsx` | Auth/workspace context and token handling. |
| `hooks.ts` | React Query hooks per module. |
| `types.ts` | Shared TypeScript types mirroring API schemas. |
| `nav.ts` | Navigation/module registry. |
| `utils.ts` | Formatting and helper utilities. |

## Deployment (`deploy/`)

- `nginx.conf` — reverse-proxy config used by the `proxy` service: routes `/` to the frontend and `/api/v1` to the backend, and is the only externally published surface. See [DEPLOYMENT.md](DEPLOYMENT.md).

## Documentation (`docs/`)

| File | Contents |
| --- | --- |
| [API.md](API.md) | REST conventions, auth, and endpoint catalog. |
| [DATABASE.md](DATABASE.md) | ER diagram, entities, indexes, tenant isolation. |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Evaluation, dev, and hardened production deployment. |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | This document. |
| [SCREENSHOTS.md](SCREENSHOTS.md) | Visual tour of the console. |
