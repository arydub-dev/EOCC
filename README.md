# Emergency Operations Command Center (EOCC)

> A decision-support platform that transforms fragmented emergency data into coordinated action.

EOCC is **not** a dashboard, a CRUD app, or a disaster tracker. It is an operational
intelligence platform for governments, emergency-management agencies, hospitals,
utilities, and humanitarian organizations. It exists to answer three questions —
continuously, and with explainable reasoning:

1. **What is happening?**
2. **Why is it happening?**
3. **What should we do next?**

Every feature maps to one or more of those questions.

---

## Highlights

- **12 operational modules** — Mission Control, Incident Management, Resource Operations,
  Hospital Operations, Shelter Operations, a Geographic Operations Map, Risk Intelligence,
  Alert Management, a Simulation Center, an AI Operations Copilot, an Executive Briefing
  Center, and a Data Integration Center.
- **Deterministic decision engines** — Incident Severity, Population Impact, Hospital Stress,
  Resource Readiness, Shelter Strain, and an Overall Emergency Health score. Every number
  ships with the weighted factors and a human-readable explanation that produced it.
- **Explainable risk intelligence** across five categories (population, infrastructure,
  healthcare, resource, environmental).
- **What-if simulation engine** for hurricane track shifts, flood expansion, shelter
  closures, hospital outages, resource depletion, and utility-grid failure.
- **AI Operations Copilot** grounded in live operational data, with a **deterministic local
  fallback** so the platform stays fully functional with no external AI dependency.
- **Demo Mode out of the box** — the database self-seeds with 100 incidents, 50 hospitals,
  200 shelters, 1,000 resources, 500 utility outages, and 1,000 alerts, with historical
  event timelines and realistic geographic distribution.
- **Connected Mode** — CSV/Excel import, connector registry, and a pipeline monitor.
- **Enterprise architecture** — thin API routers, a rich service layer, reusable domain
  engines, strong typing, JWT auth + RBAC, audit logging, pagination/filtering/search/sort,
  and full OpenAPI docs.

---

## Tech Stack

| Layer        | Technology                                                              |
| ------------ | ----------------------------------------------------------------------- |
| Frontend     | Next.js 15 (App Router), TypeScript, Tailwind CSS, React Query, Recharts, React-Leaflet |
| Backend      | FastAPI, Python 3.12, SQLAlchemy 2.0, Pydantic v2                        |
| Database     | PostgreSQL 16 (SQLite supported for lightweight local dev)              |
| Auth         | JWT (OAuth2 password flow) + role-based access control                  |
| AI           | OpenAI (optional) + deterministic local fallback engine                 |
| Deployment   | Docker Compose                                                          |

---

## Quick Start (Docker — recommended)

```bash
git clone <this-repo> eocc && cd eocc
cp .env.example .env          # optional: add OPENAI_API_KEY to enable the LLM copilot
docker compose up --build
```

Then open:

| Service            | URL                                 |
| ------------------ | ----------------------------------- |
| Frontend           | http://localhost:3000               |
| API docs (Swagger) | http://localhost:8000/docs          |
| API (ReDoc)        | http://localhost:8000/redoc         |
| Health check       | http://localhost:8000/health        |

The backend creates the schema and seeds synthetic demo data on first boot, so the
platform **feels alive immediately**.

### Demo accounts

| Role               | Email               | Password     |
| ------------------ | ------------------- | ------------ |
| Admin              | `admin@eocc.gov`    | `admin123`   |
| Emergency Manager  | `manager@eocc.gov`  | `manager123` |
| Analyst            | `analyst@eocc.gov`  | `analyst123` |
| Executive          | `exec@eocc.gov`     | `exec123`    |

---

## Local Development (without Docker)

### Backend

```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Use SQLite for zero-infra local dev:
export DATABASE_URL="sqlite:///./eocc.db"
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
export NEXT_PUBLIC_API_BASE_URL="http://localhost:8000/api/v1"
npm run dev   # http://localhost:3000
```

---

## User Roles (RBAC)

| Role               | Capabilities                                                        |
| ------------------ | ------------------------------------------------------------------- |
| **Admin**          | Full access, user management, integration config, audit & security. |
| **Emergency Manager** | Incident response, resource assignment, alert lifecycle, imports. |
| **Analyst**        | Risk analysis, simulations, incident updates, exports.              |
| **Executive**      | Read-only command view, briefings, security visibility.            |
| **Viewer**         | Read-only access to operational data.                               |

Authorization is **permission-first**: endpoints require fine-grained
permissions (e.g. `Incident.Update`, `Simulation.Run`, `Audit.View`), and roles
map to permission sets in `app/core/permissions.py`. Enforcement is server-side
via `require_permission(...)` in `app/core/deps.py`; the frontend never makes
access decisions.

---

## Security

Security is a core architectural property of EOCC, designed for government/
enterprise deployment. Highlights (full details in [`SECURITY.md`](SECURITY.md)):

- **Authentication** — Argon2id password hashing (legacy bcrypt auto-upgraded),
  configurable password policy, account lockout, short-lived JWT access tokens,
  rotating server-side refresh tokens with **theft detection**, and optional
  **TOTP MFA**.
- **Sessions** — server-side store with device list, per-session and global
  revocation, httpOnly/`Secure`/`SameSite` refresh cookie (secure by default),
  and IP/device tracking. Credential changes revoke other sessions.
- **Authorization** — fine-grained, permission-based RBAC across five roles,
  enforced only on the server.
- **Multi-tenancy** — automatic `organization_id` scoping on every query makes
  cross-tenant access impossible by default.
- **API hardening** — request/correlation IDs, strict security headers, rate
  limiting (stricter on auth), request-size and pagination caps, and structured
  errors that never leak stack traces.
- **File uploads** — extension/MIME/size validation, schema checks, CSV-injection
  neutralization, and ZIP-bomb protection.
- **Secrets & data** — env-only secrets with fail-closed production validation,
  Fernet field encryption for connector secrets and MFA seeds, parameterized
  queries, soft deletes, optimistic locking, and `created_by`/`updated_by` stamps.
- **Audit & observability** — immutable, append-only audit log with old/new
  values and correlation IDs (Audit Center UI + CSV export), a **Security Center**
  with an org security score, and `/health` `/ready` `/live` `/metrics` probes.
- **Deployment** — non-root containers, read-only filesystems,
  `no-new-privileges`, an internal-only database, and a single TLS-terminating
  reverse proxy with edge rate limits and security headers.

Run a dependency/vulnerability scan before deploying:

```bash
pip install pip-audit && pip-audit -r backend/requirements.txt   # Python
cd frontend && npm audit                                          # Node
```

---

## Decision Engines

All engines are **pure, deterministic, and explainable** (see `backend/app/engines/`).

| Engine                      | Output                                          | Where |
| --------------------------- | ----------------------------------------------- | ----- |
| Incident Severity Score     | 0–100, blends severity, hazard, population, footprint, status | `scoring.py` |
| Hospital Stress Score       | 0–100, weighted ICU/ER/bed/ventilator/staffing  | `scoring.py` |
| Shelter Strain Score        | 0–100, occupancy + supply scarcity              | `scoring.py` |
| Resource Readiness Score    | 0–100, availability + utilization + readiness   | `scoring.py` |
| Overall Emergency Health    | 0–100 composite + status band + alert penalty   | `scoring.py` |
| Risk Intelligence (×5)      | category score, severity, explanation, recs     | `risk_engine.py` |
| Recommended Actions / SITREP| prioritized actions + narrative report          | `recommendations.py` |
| Simulation Engine (×6)      | projected impact + mitigation recommendations   | `simulation_engine.py` |
| AI Copilot                  | grounded answer + suggested actions + citations | `copilot.py` |
| Executive Briefing          | summary + sections + Markdown export            | `briefing.py` |

---

## Project Structure

```
EOCC/
├── docker-compose.yml          # db + backend + frontend
├── .env.example
├── docs/                       # architecture, API, screenshots plan
├── backend/
│   ├── app/
│   │   ├── main.py             # app + lifespan (schema create + seed)
│   │   ├── config.py           # pydantic-settings config
│   │   ├── database.py         # engine, session, declarative base
│   │   ├── core/               # security (JWT/bcrypt) + RBAC deps
│   │   ├── models/             # 16 SQLAlchemy entities + enums
│   │   ├── schemas/            # Pydantic v2 request/response models
│   │   ├── engines/            # deterministic decision-support engines
│   │   ├── services/           # rich domain/service layer
│   │   ├── api/routes/         # thin routers (one per module)
│   │   └── seed/               # synthetic data generator
│   └── requirements.txt
└── frontend/
    └── src/
        ├── app/(dashboard)/    # one route per module
        ├── components/         # shell, map, tables, primitives
        └── lib/                # api client, hooks, auth, types
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for diagrams and data model,
[`docs/API.md`](docs/API.md) for the endpoint catalog, and
[`docs/SCREENSHOTS.md`](docs/SCREENSHOTS.md) for the screenshot capture plan.

---

## AI Copilot Modes

- **Deterministic (default):** intent is resolved with transparent keyword matching and
  answered from the live operational snapshot. No external calls. Always available.
- **OpenAI (optional):** set `OPENAI_API_KEY` in `.env`. The same snapshot is passed as
  grounding context to the model; if the call fails, EOCC silently falls back to the
  deterministic engine.

---

## Operating Modes

- **Demo Mode (default):** synthetic incidents, hospitals, shelters, resources, utility
  outages, weather-driven events, and alerts. No integrations required.
- **Connected Mode:** register data sources, import CSV/Excel, and monitor pipeline health
  in the Data Integration Center. Imported records become first-class platform data.

---

## License

Provided as a reference implementation for demonstration purposes.
