# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- See [ROADMAP.md](ROADMAP.md) for planned work.

## [1.0.0] — 2026-06-26

Initial public release of the Emergency Operations Command Center.

### Added

**Operational modules**
- **Mission Control** — composite Emergency Health score, headline metrics, prioritized recommended actions, critical-alert feed, and an auto-generated situation report.
- **Incident Management** — full lifecycle tracking across eight hazard types, event timelines, computed severity scoring, and optimistic-concurrency updates.
- **Resource Coordination** — resource registry, availability/utilization analytics, and an incident-assignment workflow.
- **Hospital Operations** — bed/ICU/ED/ventilator/staffing tracking with a weighted Hospital Stress score.
- **Shelter Operations** — occupancy and supply-buffer tracking with a Shelter Strain score.
- **Risk Intelligence** — explainable assessments across population, infrastructure, healthcare, resource, and environmental categories.
- **Simulation Center** — six what-if scenario types with projected impact and mitigation recommendations.
- **Operations Copilot** — operational Q&A grounded in the live snapshot, with a deterministic local engine and an optional OpenAI path.
- **Executive Briefings** — structured executive summary with Markdown export.
- **Integration Framework** — connector registry, CSV/Excel import with schema validation, and a pipeline monitor.
- **Geographic Operations Map** — color-coded situational map of incidents and lifelines.

**Decision engines**
- Deterministic, explainable scoring engines (incident severity, hospital stress, shelter strain, resource readiness, overall health) that return factors and explanations alongside every score.

**Security**
- Argon2id password hashing with transparent bcrypt upgrade; configurable password policy; account lockout.
- Short-lived JWT access tokens and rotating server-side refresh tokens with reuse/theft detection.
- Optional TOTP multi-factor authentication.
- Permission-first RBAC across five roles, enforced server-side.
- Automatic multi-tenant isolation via ORM-level organization scoping.
- API hardening: request/correlation IDs, security headers, rate limiting, request-size and pagination caps, and structured errors.
- File-upload security: extension/MIME/size validation, ZIP-bomb protection, schema validation, and CSV-injection neutralization.
- Field encryption (Fernet) for connector secrets and MFA seeds; fail-closed secret validation in production.
- Immutable, append-only audit log with old/new values and correlation IDs; Audit Center UI with CSV export.
- Security Center with an organization security-posture score and recommendations.

**Enterprise architecture**
- Layered design: thin routers, a rich service layer, and pure deterministic engines.
- FastAPI / Python 3.12 / SQLAlchemy 2.0 / Pydantic v2 backend; Next.js 15 / TypeScript console.
- PostgreSQL system of record (SQLite supported for local development).
- Self-seeding demo workspace and a connected mode for real data.

**Operations & deployment**
- Hardened Docker Compose stack with tier separation, non-root containers, read-only filesystems, and a TLS-terminating Nginx reverse proxy.
- Health/liveness/readiness probes and Prometheus-style metrics.
- Full OpenAPI documentation, versioned under `/api/v1`.

[Unreleased]: https://github.com/arydub-dev/EOCC/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/arydub-dev/EOCC/releases/tag/v1.0.0
