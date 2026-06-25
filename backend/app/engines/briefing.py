"""Executive briefing generation (deterministic).

Produces a leadership-ready briefing with an executive summary, current
situation, resource status, emerging risks and recommended actions, plus a
Markdown rendering for export.
"""
from __future__ import annotations

from datetime import datetime, timezone

from app.engines.recommendations import recommend_actions
from app.engines.risk_engine import assess_all
from app.engines.snapshot import OperationalSnapshot


def _executive_summary(s: OperationalSnapshot) -> str:
    posture = {
        "stable": "The operational picture is stable.",
        "watch": "Conditions warrant heightened monitoring.",
        "elevated": "The situation is elevated and trending toward strain.",
        "severe": "Conditions are severe; decisive resource action is required.",
        "critical": "The system is in a critical state requiring immediate executive intervention.",
    }.get(s.health_status, "Status under assessment.")
    return (
        f"{posture} Overall system health stands at {s.overall_health_score:.0f}/100. "
        f"{s.active_incidents} active incident(s) are impacting an estimated "
        f"{s.total_population_impacted:,} people, with {s.escalating_incidents} escalating. "
        f"{s.hospitals_at_risk} hospital(s) are at risk and the shelter network is at "
        f"{s.shelter_utilization_pct:.0f}% utilization. {s.critical_alerts} critical alert(s) are open."
    )


def build_briefing(s: OperationalSnapshot) -> dict:
    now = datetime.now(timezone.utc)
    summary = _executive_summary(s)

    risks = assess_all(s)
    emerging = sorted(risks, key=lambda r: r.score, reverse=True)[:3]
    actions = recommend_actions(s)[:5]

    sections = [
        {
            "heading": "Current Situation",
            "body": (
                f"{s.active_incidents} active incident(s) ({s.escalating_incidents} escalating); "
                f"peak severity {s.incident_severity_score:.0f}/100."
            ),
            "bullets": [
                f"{i.name} — {i.incident_type} ({i.status}), severity {i.severity_score:.0f}, "
                f"{i.population_impacted:,} impacted"
                for i in sorted(s.incidents, key=lambda x: x.severity_score, reverse=True)[:5]
            ],
        },
        {
            "heading": "Resource Status",
            "body": (
                f"{s.resource_available}/{s.resource_total} assets available "
                f"({s.resource_availability_pct:.0f}%), mean readiness {s.resource_readiness_pct:.0f}%."
            ),
            "bullets": (
                [f"Depleted: {c}" for c in s.depleted_resource_types]
                or ["All resource categories within adequate posture."]
            ),
        },
        {
            "heading": "Healthcare & Mass Care",
            "body": (
                f"{s.hospitals_at_risk}/{s.hospital_count} hospitals at risk (ICU "
                f"{s.icu_occupancy_pct:.0f}%); {s.shelters_overcrowded} shelter(s) overcrowded."
            ),
            "bullets": [
                f"{h.name} — stress {h.stress_score:.0f}/100 ({h.status})"
                for h in s.top_stressed_hospitals[:3]
            ],
        },
        {
            "heading": "Emerging Risks",
            "body": "Top risk categories by score:",
            "bullets": [f"{r.title}: {r.score:.0f}/100 ({r.severity.value}) — {r.explanation}" for r in emerging],
        },
        {
            "heading": "Recommended Actions",
            "body": "Prioritized actions for the next operational period:",
            "bullets": [f"P{a.priority}: {a.title} — {a.impact}" for a in actions],
        },
    ]

    markdown = _to_markdown(now, summary, sections)
    return {
        "title": "EOCC Executive Briefing",
        "generated_at": now,
        "executive_summary": summary,
        "sections": sections,
        "markdown": markdown,
    }


def _to_markdown(now: datetime, summary: str, sections: list[dict]) -> str:
    out = [
        "# EOCC Executive Briefing",
        f"_Generated {now.strftime('%Y-%m-%d %H:%M UTC')}_",
        "",
        "## Executive Summary",
        summary,
        "",
    ]
    for sec in sections:
        out.append(f"## {sec['heading']}")
        if sec.get("body"):
            out.append(sec["body"])
        for bullet in sec.get("bullets", []):
            out.append(f"- {bullet}")
        out.append("")
    return "\n".join(out)
