"""AI Operations Copilot service.

Defaults to the deterministic local engine. If an OpenAI API key is configured,
it augments the deterministic answer with an LLM response grounded in the same
snapshot context. The platform remains fully functional without OpenAI.
"""
from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.config import settings
from app.engines import copilot
from app.engines.snapshot import OperationalSnapshot
from app.models import AIReport
from app.schemas.ai import CopilotResponse

SYSTEM_PROMPT = (
    "You are the EOCC Operations Copilot for an emergency command center. "
    "Answer ONLY using the provided operational JSON context. Be concise, "
    "operational, and decisive. Never invent data not present in the context."
)


def _try_openai(question: str, context: dict) -> str | None:
    if not settings.ai_enabled:
        return None
    try:  # pragma: no cover - network path
        import httpx

        resp = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
            json={
                "model": settings.OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Operational context:\n{json.dumps(context)}\n\nQuestion: {question}",
                    },
                ],
                "temperature": 0.2,
            },
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def ask(
    db: Session,
    question: str,
    snap: OperationalSnapshot,
    user_id: int | None,
    org_id: int | None = None,
) -> CopilotResponse:
    deterministic = copilot.answer_question(question, snap)
    context = copilot.grounding_context(snap)

    llm_answer = _try_openai(question, context)
    if llm_answer:
        answer, engine, confidence = llm_answer, "openai", 0.9
    else:
        answer, engine, confidence = deterministic.answer, "deterministic", deterministic.confidence

    report = AIReport(
        organization_id=org_id,
        report_type="copilot",
        title=question[:240],
        prompt=question,
        content=answer,
        structured=deterministic.grounding,
        grounding=context,
        engine=engine,
        created_by_id=user_id,
    )
    db.add(report)
    db.commit()

    return CopilotResponse(
        answer=answer,
        engine=engine,
        confidence=confidence,
        grounding=deterministic.grounding,
        suggested_actions=deterministic.suggested_actions,
        citations=deterministic.citations,
        follow_ups=deterministic.follow_ups,
    )
