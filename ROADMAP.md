# Roadmap

This roadmap communicates direction and priorities. It is a statement of intent, not a commitment to dates; scope and sequencing may change based on operational feedback and contributions. Items are grouped by target release and ordered roughly by priority.

Releases follow [Semantic Versioning](https://semver.org/). See [CHANGELOG.md](CHANGELOG.md) for shipped work.

---

## v1.1 — Performance, Integrations, and Simulation Depth

Focus: harden and accelerate the v1.0 foundation, broaden data ingestion, and deepen simulation fidelity.

**Performance improvements**
- Query and index tuning for large operating pictures; add per-tenant composite indexes for hot paths.
- Snapshot caching with short TTLs to reduce repeated aggregation cost on Mission Control and Risk.
- Move rate limiting and metrics to a shared backing store (Redis) to support horizontal scaling.

**Additional integrations**
- Expand the connector registry with configurable polling for REST sources.
- Standardized field-mapping UI for CSV/Excel imports (column → domain field).
- Webhook ingestion endpoint for push-based sources.

**Improved simulations**
- Multi-factor scenarios (combine flood expansion with utility-grid failure).
- Sensitivity analysis: show how outcomes change as parameters vary.
- Save, compare, and share scenario runs across a team.

---

## v1.2 — Automation, Live Feeds, and Forecasting

Focus: shift from reactive to anticipatory operations.

**Advanced workflow automation**
- Rule-based automation: when an alert of a given category and severity opens, trigger a defined response action or escalation.
- Configurable alert thresholds per organization.
- Assignment recommendations that propose resource-to-incident matches for operator approval.

**Live weather feeds**
- First-class weather connector with severe-weather watch/warning ingestion.
- Weather overlays on the operations map and weather-aware risk scoring.

**Incident forecasting**
- Short-horizon projection of incident severity and population impact from event-timeline trends.
- Hospital and shelter capacity forecasting to surface bottlenecks before they occur.

---

## v2.0 — Scale, Autonomy, and Resilience

Focus: multi-region operation, deeper analytical autonomy, and continuity of operations.

**Multi-region deployment**
- Region-aware data residency and deployment topology.
- Cross-region read replicas and failover guidance.

**AI investigation agents**
- Agents that assemble an evidence-backed situation analysis by querying the snapshot and audit trail, always with citations and within tenant boundaries.
- Human-in-the-loop review for any agent-proposed action.

**Advanced GIS analytics**
- Evacuation-zone modeling and routing.
- Spatial clustering of incidents and lifelines; isochrone (drive-time) analysis for resource reach.

**Offline operations**
- Degraded-mode operation for field deployments with intermittent connectivity.
- Local-first data capture with reconciliation on reconnect.

---

## Continuous

These run across all releases rather than belonging to one:

- Test coverage expansion across services and engines.
- Accessibility (WCAG) improvements in the console.
- Dependency and supply-chain hygiene (automated audits, SBOMs, image scanning).
- Documentation accuracy and operator runbooks.

---

Have a need that is not represented here? Open a [feature request](.github/ISSUE_TEMPLATE) — operational feedback directly shapes prioritization.
