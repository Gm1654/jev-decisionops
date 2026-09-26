import os
from typing import Any

from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

from models import InvoiceInput, JevSignals

_MODEL = os.getenv("JEV_MODEL") or "jev-latest"
_client: TypeSafeClient | None = None


def get_client() -> TypeSafeClient:
    global _client
    if _client is None:
        _client = TypeSafeClient(model=_MODEL)
    return _client


def evaluate_invoice(invoice: InvoiceInput) -> tuple[JevSignals, bool]:
    """Call TypeSafe JEV once. On any failure, return empty signals and jev_failed=True."""
    try:
        client = get_client()
        response = client.system_one(
            state=_invoice_state(invoice),
            questions={
                "risk": Score(
                    instructions=(
                        "Score invoice payment risk from 0 (very low) to 9 (critical) "
                        "based on vendor history, amount, duplicates, blocked status, "
                        "late deliveries, payment issues, and missing purchase order."
                    ),
                    criteria=[
                        "Very low risk",
                        "Low risk",
                        "Low to moderate risk",
                        "Moderate risk",
                        "Elevated risk",
                        "High risk",
                        "Very high risk",
                        "Severe risk",
                        "Near-critical risk",
                        "Critical risk",
                    ],
                ),
                "needs_human_review": Noul(
                    instructions=(
                        "Should a human review this invoice before payment "
                        "because of risk, anomalies, or missing controls?"
                    ),
                ),
                "route": Choice(
                    instructions="Which team should handle this invoice?",
                    criteria={
                        "finance": "Standard finance processing",
                        "manager": "Needs manager attention",
                        "manual_review": "Needs manual review",
                    },
                ),
                "vendor_reliability": Score(
                    instructions="How reliable is this vendor based on the invoice state?",
                    criteria=[
                        "Unreliable",
                        "Poor reliability",
                        "Below average",
                        "Somewhat mixed",
                        "Average",
                        "Above average",
                        "Good",
                        "Strong",
                        "Very strong",
                        "Excellent reliability",
                    ],
                ),
                "priority": Choice(
                    instructions="What processing priority should this invoice have?",
                    criteria={
                        "low": "Can wait",
                        "medium": "Normal queue",
                        "high": "Handle promptly",
                    },
                ),
            },
        )
        return _normalize(response), False
    except Exception:
        return JevSignals(model=_MODEL), True


def _invoice_state(invoice: InvoiceInput) -> dict[str, Any]:
    return invoice.model_dump()


def _normalize(response: Any) -> JevSignals:
    risk = response.scores["risk"]
    review = response.nouls["needs_human_review"]
    route = response.choices["route"]
    reliability = response.scores["vendor_reliability"]
    priority = response.choices["priority"]

    required = [
        getattr(risk, "score", None),
        getattr(risk, "confidence", None),
        getattr(review, "noul", None),
        getattr(route, "choice", None),
        getattr(reliability, "score", None),
        getattr(priority, "choice", None),
    ]
    if any(value is None for value in required):
        raise ValueError("JEV response missing required values")

    model = getattr(response, "model", None) or _MODEL

    return JevSignals(
        risk_score=float(risk.score),
        confidence=float(risk.confidence),
        review_probability=float(review.noul),
        route=str(route.choice),
        route_confidence=float(getattr(route, "confidence", 0.0) or 0.0),
        vendor_reliability=float(reliability.score),
        priority=str(priority.choice),
        model=str(model),
    )
