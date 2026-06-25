# EOCC — API Specification

Base URL: `http://localhost:8000/api/v1`
Interactive docs: `/docs` (Swagger UI) · `/redoc` (ReDoc) · `/api/v1/openapi.json`

All endpoints except `POST /auth/login` require `Authorization: Bearer <token>`.

List endpoints support standard query params: `page`, `page_size`, `sort_by`,
`sort_dir` (`asc|desc`), `search`, plus module-specific filters.

---

## Auth & Users

| Method | Path | Role | Description |
| --- | --- | --- | --- |
| POST | `/auth/login` | public | OAuth2 password login → JWT + user |
| GET | `/auth/me` | any | Current user profile |
| GET | `/users` | admin | List users |
| POST | `/users` | admin | Create user |
| PATCH | `/users/{id}` | admin | Update user / reset password |
| DELETE | `/users/{id}` | admin | Deactivate user |

## Mission Control

| Method | Path | Description |
| --- | --- | --- |
| GET | `/mission-control/summary` | Metrics, recommended actions, critical alerts, SITREP |
| GET | `/mission-control/health` | Overall health score breakdown + explanation |

## Incidents

| Method | Path | Role | Description |
| --- | --- | --- | --- |
| GET | `/incidents` | any | List (filters: `incident_type`, `status`, `region`) |
| GET | `/incidents/{id}` | any | Detail + event timeline |
| GET | `/incidents/{id}/timeline` | any | Event history |
| POST | `/incidents` | manager | Create (auto-scores severity, logs event) |
| PATCH | `/incidents/{id}` | manager | Update (re-scores, records status changes) |
| DELETE | `/incidents/{id}` | manager | Delete |

## Resources

| Method | Path | Role | Description |
| --- | --- | --- | --- |
| GET | `/resources` | any | List (filters: `resource_type`, `status`, `region`) |
| GET | `/resources/utilization` | any | Availability/utilization analytics by type |
| GET | `/resources/{id}` | any | Detail |
| POST | `/resources` | manager | Create |
| PATCH | `/resources/{id}` | manager | Update status/location/readiness |
| POST | `/resources/assignments` | manager | Assign resource to incident |
| GET | `/resources/assignments/all` | any | List assignments |
| POST | `/resources/assignments/{id}/release` | manager | Release assignment |

## Hospitals / Shelters / Utilities

| Method | Path | Description |
| --- | --- | --- |
| GET/POST/PATCH | `/hospitals` | Capacity, ICU/ER load, stress score (`at_risk=true` filter) |
| GET/POST/PATCH | `/shelters` | Occupancy, supply buffers, strain score |
| GET/POST/PATCH | `/utilities` | Utility outages (filters: `utility_type`, `status`, `region`) |

## Geographic Operations

| Method | Path | Description |
| --- | --- | --- |
| GET | `/geo/features?layers=incidents,hospitals,shelters,resources,utilities` | Map-ready, color-coded feature collections per layer |

## Risk Intelligence

| Method | Path | Role | Description |
| --- | --- | --- | --- |
| GET | `/risk` | any | Current assessments (auto-generates if empty) |
| POST | `/risk/generate` | analyst | Regenerate all five category assessments |

## Alerts

| Method | Path | Role | Description |
| --- | --- | --- | --- |
| GET | `/alerts` | any | List (filters: `category`, `severity`, `status`) |
| POST | `/alerts/evaluate` | manager | Run threshold engine to raise new alerts |
| POST | `/alerts` | manager | Create manual alert |
| GET | `/alerts/{id}` | any | Detail |
| POST | `/alerts/{id}/acknowledge` | manager | Acknowledge |
| POST | `/alerts/{id}/resolve` | manager | Resolve |
| POST | `/alerts/{id}/actions` | manager | Append a response action |

## Simulation Center

| Method | Path | Role | Description |
| --- | --- | --- | --- |
| GET | `/simulations` | any | Recent simulations |
| GET | `/simulations/{id}` | any | Detail |
| POST | `/simulations/run` | analyst | Run a scenario (6 types) and store results |

## AI Copilot

| Method | Path | Description |
| --- | --- | --- |
| GET | `/copilot/status` | Active engine + suggested questions |
| POST | `/copilot/ask` | Ask a grounded operational question |
| GET | `/copilot/history` | Recent copilot queries |

## Executive Briefing

| Method | Path | Description |
| --- | --- | --- |
| POST | `/briefing/generate` | Structured briefing (summary + sections + Markdown) |
| GET | `/briefing/markdown` | Latest briefing as `text/markdown` |

## Data Integration

| Method | Path | Role | Description |
| --- | --- | --- | --- |
| GET | `/integration/overview` | any | Connected systems, health, last sync |
| GET | `/integration/sources` | any | Connector registry |
| POST | `/integration/sources` | manager | Register a connector |
| GET | `/integration/pipeline` | any | Pipeline monitor (jobs, records, health) |
| GET | `/integration/jobs` | any | Recent import jobs |
| POST | `/integration/import/csv` | manager | Import CSV content |
| POST | `/integration/import/excel` | manager | Import `.xlsx/.xls` upload |

## Audit

| Method | Path | Role | Description |
| --- | --- | --- | --- |
| GET | `/audit` | admin | Paginated audit log (filters: `action`, `entity_type`) |

## System

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health` | Liveness probe |
| GET | `/` | Service metadata + active AI engine |
