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


def test_health_ok():
    from main import app

    response = TestClient(app).get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_post_duplicate_rejects_without_jev(monkeypatch):
    from main import app

    monkeypatch.setattr("main.evaluate_invoice", lambda invoice: (_ for _ in ()).throw(AssertionError("JEV should not run")))
    response = TestClient(app).post("/api/decisions", json=sample_invoice(duplicate_invoice=True).model_dump())
    body = response.json()
    assert response.status_code == 200
    assert body["decision"] == "REJECT"
    assert body["fallback_used"] is False


def test_post_blocked_rejects_without_jev(monkeypatch):
    from main import app

    monkeypatch.setattr("main.evaluate_invoice", lambda invoice: (_ for _ in ()).throw(AssertionError("JEV should not run")))
    response = TestClient(app).post("/api/decisions", json=sample_invoice(blocked_vendor=True).model_dump())
    body = response.json()
    assert response.status_code == 200
    assert body["decision"] == "REJECT"
    assert body["fallback_used"] is False


def test_post_low_risk_auto_approves(monkeypatch):
    from models import JevSignals
    from main import app

    monkeypatch.setattr(
        "main.evaluate_invoice",
        lambda invoice: (JevSignals(risk_score=1.2, confidence=0.95, review_probability=0.1, route="finance", vendor_reliability=8.0, priority="low", model="mock-policy"), False),
    )
    response = TestClient(app).post("/api/decisions", json=sample_invoice().model_dump())
    body = response.json()
    assert body["decision"] == "AUTO_APPROVE"
    assert body["fallback_used"] is False
    assert body["signals"]["model"] == "mock-policy"


def test_post_high_risk_human_review(monkeypatch):
    from models import JevSignals
    from main import app

    monkeypatch.setattr(
        "main.evaluate_invoice",
        lambda invoice: (JevSignals(risk_score=8.6, confidence=0.94, review_probability=0.2, route="manual_review", vendor_reliability=1.0, priority="high", model="mock-policy"), False),
    )
    response = TestClient(app).post("/api/decisions", json=sample_invoice().model_dump())
    body = response.json()
    assert body["decision"] == "HUMAN_REVIEW"
    assert body["fallback_used"] is False


def test_post_jev_failure_uses_fallback(monkeypatch):
    from models import JevSignals
    from main import app

    monkeypatch.setattr("main.evaluate_invoice", lambda invoice: (JevSignals(), True))
    response = TestClient(app).post("/api/decisions", json=sample_invoice().model_dump())
    body = response.json()
    assert body["decision"] == "HUMAN_REVIEW"
    assert body["fallback_used"] is True


def test_invalid_payload_returns_422():
    from main import app

    response = TestClient(app).post("/api/decisions", json={"vendor_name": "Acme"})
    assert response.status_code == 422


def test_list_decisions_includes_created(monkeypatch):
    from models import JevSignals
    from main import app, _history

    _history.clear()
    monkeypatch.setattr(
        "main.evaluate_invoice",
        lambda invoice: (JevSignals(risk_score=1.0, confidence=0.99, review_probability=0.05, model="mock-policy"), False),
    )
    client = TestClient(app)
    client.post("/api/decisions", json=sample_invoice(invoice_number="INV-LIST").model_dump())
    listed = client.get("/api/decisions").json()
    assert len(listed) >= 1
    assert listed[0]["invoice"]["invoice_number"] == "INV-LIST"


def test_update_and_delete_decision(monkeypatch):
    from models import JevSignals
    from main import app, _history

    _history.clear()
    monkeypatch.setattr(
        "main.evaluate_invoice",
        lambda invoice: (JevSignals(risk_score=1.0, confidence=0.99, review_probability=0.05, model="mock-policy"), False),
    )
    client = TestClient(app)
    created = client.post("/api/decisions", json=sample_invoice(invoice_number="INV-EDIT").model_dump()).json()
    decision_id = created["id"]

    updated = client.put(
        f"/api/decisions/{decision_id}",
        json=sample_invoice(invoice_number="INV-EDIT-2", invoice_amount=900).model_dump(),
    )
    body = updated.json()
    assert updated.status_code == 200
    assert body["id"] == decision_id
    assert body["invoice"]["invoice_number"] == "INV-EDIT-2"
    assert len(client.get("/api/decisions").json()) == 1

    missing = client.put("/api/decisions/missing", json=sample_invoice().model_dump())
    assert missing.status_code == 404

    deleted = client.delete(f"/api/decisions/{decision_id}")
    assert deleted.status_code == 200
    assert client.get("/api/decisions").json() == []

    gone = client.delete(f"/api/decisions/{decision_id}")
    assert gone.status_code == 404
