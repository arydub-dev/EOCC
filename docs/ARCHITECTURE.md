# EOCC — System Architecture

## 1. High-level architecture

```mermaid
flowchart LR
  subgraph Client["Browser — Next.js 15 (App Router)"]
    UI[12 Module UIs]
    RQ[React Query cache]
    UI --> RQ
  end

  subgraph API["FastAPI (Python 3.12)"]
    R[Thin Routers]
    S[Service Layer]
    E[Decision Engines]
    R --> S --> E
  end

  DB[(PostgreSQL 16)]
  OAI{{OpenAI API\n(optional)}}

  RQ -->|JWT / REST| R
  S <-->|SQLAlchemy 2.0| DB
  E -. grounded context .-> OAI
  OAI -. fallback .-> E

  classDef opt stroke-dasharray: 5 5;
  class OAI opt;
```

**Design principle:** routers are thin and only handle HTTP concerns (validation, auth,
status codes). All logic lives in the **service layer**, which composes **pure decision
engines**. The engines never touch the database — they consume a computed
`OperationalSnapshot`, which keeps them deterministic and unit-testable.

## 2. Request lifecycle (e.g. Mission Control)

```mermaid
sequenceDiagram
  participant B as Browser
  participant R as mission router
  participant A as analytics.build_snapshot
  participant DB as PostgreSQL
  participant M as mission_service
  participant Eng as engines (scoring/recs)

  B->>R: GET /mission-control/summary (Bearer JWT)
  R->>A: build operational snapshot
  A->>DB: aggregate incidents/hospitals/shelters/resources/alerts
  DB-->>A: rows
  A-->>R: OperationalSnapshot
  R->>M: build_mission_control(snapshot)
  M->>Eng: recommend_actions / situation_report / health
  Eng-->>M: explainable results
  M-->>R: MissionControlSummary
  R-->>B: JSON (metrics, actions, SITREP, critical alerts)
```

## 3. Data model (ER overview)

```mermaid
erDiagram
  USER ||--o{ RESOURCE_ASSIGNMENT : assigns
  USER ||--o{ SIMULATION : creates
  USER ||--o{ AUDIT_LOG : acts

  INCIDENT ||--o{ INCIDENT_EVENT : has
  INCIDENT ||--o{ ALERT : raises
  INCIDENT ||--o{ RESOURCE_ASSIGNMENT : staffed_by
  INCIDENT ||--o{ RISK_ASSESSMENT : scored_by
  INCIDENT ||--o{ UTILITY_OUTAGE : linked

  RESOURCE ||--o{ RESOURCE_ASSIGNMENT : deployed_in
  HOSPITAL ||--o{ ALERT : triggers
  SHELTER  ||--o{ ALERT : triggers

  DATA_SOURCE ||--o{ IMPORT_JOB : runs

  USER {
    int id PK
    string email
    enum role
  }
  INCIDENT {
    int id PK
    enum incident_type
    enum status
    float severity_score
    int population_impacted
  }
  HOSPITAL {
    int id PK
    int total_beds
    float stress_score
    enum status
  }
  SHELTER {
    int id PK
    int capacity
    float utilization_score
  }
  RESOURCE {
    int id PK
    enum resource_type
    enum status
    float readiness
  }
  ALERT {
    int id PK
    enum category
    enum severity
    enum status
  }
```

### Full entity list (16)

`User`, `Incident`, `IncidentEvent`, `Hospital`, `Shelter`, `Resource`,
`ResourceAssignment`, `UtilityOutage`, `RiskAssessment`, `Alert`, `Simulation`,
`AIReport`, `DataSource`, `ImportJob`, `AuditLog`, `AppSetting`.

## 4. Scoring model (summary)

| Score | Inputs | Weighting |
| --- | --- | --- |
| Incident Severity | base severity, hazard type, population (log), footprint, status | severity 45 / pop 30 / footprint 25, × type weight × status multiplier |
| Hospital Stress | ICU, ER, bed, ventilator loads, staffing gap | ICU 32 / ER 28 / bed 18 / vent 12 / staffing 10 |
| Shelter Strain | occupancy, food/water scarcity | occupancy 70 / food 15 / water 15 |
| Resource Readiness | availability, utilization balance, mean readiness | availability 45 / readiness 40 / balance 15 |
| Overall Health | inverted incident/hospital/shelter strain + readiness − alert penalty | 30 / 25 / 20 / 25, − up to 20 |

Every engine returns a `ScoreResult { score, band, factors, explanation }` so the UI and
audit trail can always show *why* a number is what it is.

## 5. Security & governance

- **JWT** bearer tokens (OAuth2 password flow); bcrypt-hashed passwords.
- **RBAC** via `require_roles(...)` dependency factory; Admin supersedes all roles.
- **Audit logging** on every mutating action (`audit_service.log`).
- **Global error handling** returns sanitized 500s; validation handled by Pydantic v2.
- **Pagination / filtering / search / sorting** standardized via `PaginationParams` +
  `services/common.paginate`.

## 6. Deployment topology

```mermaid
flowchart TB
  subgraph compose["docker compose"]
    fe["frontend :3000 (Next standalone)"]
    be["backend :8000 (uvicorn)"]
    db[("db :5432 postgres:16")]
  end
  fe --> be --> db
```
