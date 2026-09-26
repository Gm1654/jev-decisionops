from fastapi.testclient import TestClient

from decision_policy import apply_policy
from models import InvoiceInput, JevSignals


def sample_invoice(**overrides) -> InvoiceInput:
    data = {
        "vendor_name": "Acme Office Supplies",
        "invoice_number": "INV-001",
        "invoice_amount": 850,
        "currency": "USD",
        "vendor_age_months": 24,
        "previous_invoices": 20,
        "late_deliveries": 0,
        "previous_payment_issues": 0,
        "duplicate_invoice": False,
        "purchase_order_exists": True,
        "blocked_vendor": False,
        "department": "Operations",
        "country": "US",
    }
    data.update(overrides)
    return InvoiceInput(**data)


def test_duplicate_invoice_rejects():
    decision, fallback = apply_policy(
        sample_invoice(duplicate_invoice=True),
        JevSignals(),
        jev_failed=False,
    )
    assert decision == "REJECT"
    assert fallback is False


def test_blocked_vendor_rejects():
    decision, fallback = apply_policy(
        sample_invoice(blocked_vendor=True),
        JevSignals(),
        jev_failed=False,
    )
    assert decision == "REJECT"
    assert fallback is False


def test_low_risk_auto_approves():
    decision, fallback = apply_policy(
        sample_invoice(),
        JevSignals(risk_score=2.1, confidence=0.91, review_probability=0.12),
        jev_failed=False,
    )
    assert decision == "AUTO_APPROVE"
    assert fallback is False


def test_high_risk_human_review():
    decision, fallback = apply_policy(
        sample_invoice(),
        JevSignals(risk_score=8.4, confidence=0.92, review_probability=0.20),
        jev_failed=False,
    )
    assert decision == "HUMAN_REVIEW"
    assert fallback is False


def test_low_confidence_human_review():
    decision, fallback = apply_policy(
        sample_invoice(),
        JevSignals(risk_score=1.5, confidence=0.40, review_probability=0.10),
        jev_failed=False,
    )
    assert decision == "HUMAN_REVIEW"
    assert fallback is False


def test_jev_failure_human_review():
    decision, fallback = apply_policy(
        sample_invoice(),
        JevSignals(),
        jev_failed=True,
    )
    assert decision == "HUMAN_REVIEW"
    assert fallback is True


def test_invalid_amount_returns_400():
    from main import app

    client = TestClient(app)
    payload = sample_invoice(invoice_amount=0).model_dump()
    response = client.post("/api/decisions", json=payload)
    assert response.status_code == 400
