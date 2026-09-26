from models import InvoiceInput, JevSignals

MIN_CONFIDENCE = 0.70
HIGH_RISK_THRESHOLD = 8.0
REVIEW_THRESHOLD = 0.80
AUTO_APPROVE_THRESHOLD = 3.0


def apply_policy(
    invoice: InvoiceInput,
    signals: JevSignals,
    jev_failed: bool,
) -> tuple[str, bool]:
    if invoice.duplicate_invoice or invoice.blocked_vendor:
        return "REJECT", False

    if jev_failed:
        return "HUMAN_REVIEW", True

    if (
        signals.confidence is None
        or signals.risk_score is None
        or signals.review_probability is None
    ):
        return "HUMAN_REVIEW", True

    if signals.confidence < MIN_CONFIDENCE:
        return "HUMAN_REVIEW", False

    if signals.risk_score >= HIGH_RISK_THRESHOLD:
        return "HUMAN_REVIEW", False

    if signals.review_probability >= REVIEW_THRESHOLD:
        return "HUMAN_REVIEW", False

    if signals.risk_score <= AUTO_APPROVE_THRESHOLD:
        return "AUTO_APPROVE", False

    return "HUMAN_REVIEW", False
