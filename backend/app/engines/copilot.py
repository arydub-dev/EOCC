"""Deterministic AI Operations Copilot.

Grounds every answer in the live operational snapshot. Used directly as the
local fallback engine, and also supplies the grounding context for the optional
OpenAI-backed path. Intent is resolved with transparent keyword matching so the
platform stays fully functional with no external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.engines.snapshot import OperationalSnapshot


@dataclass
class CopilotAnswer:
    answer: str
    confidence: float
    grounding: dict
    suggested_actions: list[str] = field(default_factory=list)
    citations: list[str] = field(default_factory=list)
    follow_ups: list[str] = field(default_factory=list)


def _hospital_stress_answer(s: OperationalSnapshot) -> CopilotAnswer:
    top = s.top_stressed_hospitals[:5]
    if not top:
        return CopilotAnswer("No hospital data is currently available.", 0.5, {})
    lines = [
        f"{i+1}. {h.name} — stress {h.stress_score:.0f}/100 ({h.status}), "
        f"ICU {h.icu_occupancy_pct:.0f}%" + (f", {h.region}" if h.region else "")
        for i, h in enumerate(top)
    ]
    answer = (
        f"{s.hospitals_at_risk} of {s.hospital_count} hospitals are at risk. "
        f"System ICU occupancy is {s.icu_occupancy_pct:.0f}%. Most stressed:\n" + "\n".join(lines)
    )
    return CopilotAnswer(
        answer,
        0.92,
        {
            "top_stressed_hospitals": [h.__dict__ for h in top],
            "hospitals_at_risk": s.hospitals_at_risk,
        },
        [
            "Activate diversion for the top-stressed facilities.",
            "Deploy medical strike teams to ICU surge sites.",
        ],
        [f"hospital:{h.id}" for h in top],
        [
            "Where should we deploy additional medical teams?",
            "Which shelters will reach capacity first?",
        ],
    )


def _resource_deploy_answer(s: OperationalSnapshot) -> CopilotAnswer:
    targets = [i for i in s.incidents if i.status in ("active", "escalating")]
    targets.sort(key=lambda i: i.severity_score, reverse=True)
    top = targets[:3]
    lines = [
        f"{i+1}. {t.name} ({t.incident_type}) — severity {t.severity_score:.0f}/100, "
        f"{t.population_impacted:,} impacted" + (f", {t.region}" if t.region else "")
        for i, t in enumerate(top)
    ]
    answer = (
        f"Prioritize deployment to the highest-severity active incidents. "
        f"{s.resource_available}/{s.resource_total} assets are available "
        f"({s.resource_availability_pct:.0f}%).\n" + "\n".join(lines)
    )
    if s.depleted_resource_types:
        answer += (
            "\nDepleted categories needing resupply: " + ", ".join(s.depleted_resource_types) + "."
        )
    return CopilotAnswer(
        answer,
        0.88,
        {"priority_incidents": [t.__dict__ for t in top], "depleted": s.depleted_resource_types},
        [
            "Rebalance idle units toward the top incident.",
            "Request mutual aid for depleted categories.",
        ],
        [f"incident:{t.id}" for t in top],
        ["What incidents pose the highest risk?", "Which hospitals are under the most stress?"],
    )


def _shelter_capacity_answer(s: OperationalSnapshot) -> CopilotAnswer:
    top = s.top_strained_shelters[:5]
    if not top:
        return CopilotAnswer("No shelter data is currently available.", 0.5, {})
    lines = [
        f"{i+1}. {sh.name} — {sh.occupancy_pct:.0f}% occupied, food {sh.food_supply_days:.1f}d"
        + (f", {sh.region}" if sh.region else "")
        for i, sh in enumerate(top)
    ]
    answer = (
        f"Shelter network is at {s.shelter_utilization_pct:.0f}% utilization with "
        f"{s.shelters_overcrowded} overcrowded. Closest to capacity:\n" + "\n".join(lines)
    )
    return CopilotAnswer(
        answer,
        0.9,
        {"top_strained_shelters": [sh.__dict__ for sh in top]},
        [
            "Open overflow capacity near the most strained shelters.",
            "Resupply shelters below 2 days of food.",
        ],
        [f"shelter:{sh.id}" for sh in top],
        [
            "Which hospitals are under the most stress?",
            "Where should we deploy additional resources?",
        ],
    )


def _incident_risk_answer(s: OperationalSnapshot) -> CopilotAnswer:
    incidents = sorted(s.incidents, key=lambda i: i.severity_score, reverse=True)[:5]
    if not incidents:
        return CopilotAnswer("No active incidents are currently tracked.", 0.5, {})
    lines = [
        f"{i+1}. {t.name} ({t.incident_type}, {t.status}) — severity {t.severity_score:.0f}/100, "
        f"{t.population_impacted:,} impacted"
        for i, t in enumerate(incidents)
    ]
    answer = (
        f"Peak incident severity is {s.incident_severity_score:.0f}/100 across "
        f"{s.active_incidents} active incident(s) ({s.escalating_incidents} escalating). "
        f"Highest risk:\n" + "\n".join(lines)
    )
    return CopilotAnswer(
        answer,
        0.91,
        {"top_incidents": [t.__dict__ for t in incidents]},
        [
            "Escalate command posture for worsening incidents.",
            "Concentrate resources on the top incident.",
        ],
        [f"incident:{t.id}" for t in incidents],
        [
            "Where should we deploy additional resources?",
            "Which hospitals are under the most stress?",
        ],
    )


def _overview_answer(s: OperationalSnapshot) -> CopilotAnswer:
    answer = (
        f"Overall system health is {s.overall_health_score:.0f}/100 ({s.health_status}). "
        f"{s.active_incidents} active incident(s) impacting {s.total_population_impacted:,} people. "
        f"{s.hospitals_at_risk} hospital(s) at risk, {s.shelters_overcrowded} shelter(s) overcrowded, "
        f"{s.resource_availability_pct:.0f}% of resources available, "
        f"{s.open_alerts} open alert(s) ({s.critical_alerts} critical)."
    )
    return CopilotAnswer(
        answer,
        0.8,
        {
            "overall_health_score": s.overall_health_score,
            "active_incidents": s.active_incidents,
            "open_alerts": s.open_alerts,
        },
        ["Review the recommended actions on Mission Control."],
        [],
        [
            "Which hospitals are under the most stress?",
            "Where should we deploy additional resources?",
            "What incidents pose the highest risk?",
        ],
    )


# Ordered intent table: (keywords, handler). First match wins.
_INTENTS = [
    (("hospital", "icu", "stress", "medical capacity", "er"), _hospital_stress_answer),
    (("deploy", "where should", "send resource", "allocate", "dispatch"), _resource_deploy_answer),
    (("shelter", "capacity first", "overcrowd", "evacuee"), _shelter_capacity_answer),
    (("incident", "highest risk", "worst", "escalat", "hazard"), _incident_risk_answer),
]


def answer_question(question: str, s: OperationalSnapshot) -> CopilotAnswer:
    q = question.lower()
    for keywords, handler in _INTENTS:
        if any(k in q for k in keywords):
            return handler(s)
    return _overview_answer(s)


def grounding_context(s: OperationalSnapshot) -> dict:
    """Compact, structured context handed to an LLM when OpenAI is enabled."""
    return {
        "overall_health_score": s.overall_health_score,
        "health_status": s.health_status,
        "active_incidents": s.active_incidents,
        "escalating_incidents": s.escalating_incidents,
        "incident_severity_score": s.incident_severity_score,
        "population_impacted": s.total_population_impacted,
        "hospitals_at_risk": s.hospitals_at_risk,
        "icu_occupancy_pct": s.icu_occupancy_pct,
        "shelters_overcrowded": s.shelters_overcrowded,
        "shelter_utilization_pct": s.shelter_utilization_pct,
        "resource_availability_pct": s.resource_availability_pct,
        "open_alerts": s.open_alerts,
        "critical_alerts": s.critical_alerts,
        "top_stressed_hospitals": [h.__dict__ for h in s.top_stressed_hospitals[:5]],
        "top_strained_shelters": [sh.__dict__ for sh in s.top_strained_shelters[:5]],
        "top_incidents": [
            i.__dict__
            for i in sorted(s.incidents, key=lambda x: x.severity_score, reverse=True)[:5]
        ],
        "depleted_resource_types": s.depleted_resource_types,
    }
