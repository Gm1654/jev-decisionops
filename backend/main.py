import uuid
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

from decision_policy import apply_policy
from jev_service import evaluate_invoice
from models import DecisionResult, InvoiceInput, JevSignals

app = FastAPI(title="JEV DecisionOps")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_history: deque[DecisionResult] = deque(maxlen=20)


def _run_decision(invoice: InvoiceInput) -> tuple[str, bool, JevSignals]:
    if invoice.invoice_amount <= 0:
        raise HTTPException(status_code=400, detail="invoice_amount must be greater than 0")

    jev_failed = False
    signals = JevSignals()
    if not invoice.duplicate_invoice and not invoice.blocked_vendor:
        signals, jev_failed = evaluate_invoice(invoice)
    decision, fallback_used = apply_policy(invoice, signals, jev_failed)
    return decision, fallback_used, signals


def _get_decision(decision_id: str) -> tuple[int, DecisionResult]:
    for index, item in enumerate(_history):
        if item.id == decision_id:
            return index, item
    raise HTTPException(status_code=404, detail="Decision not found")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/decisions", response_model=DecisionResult)
def create_decision(invoice: InvoiceInput) -> DecisionResult:
    decision, fallback_used, signals = _run_decision(invoice)
    result = DecisionResult(
        id=str(uuid.uuid4()),
        created_at=datetime.now(timezone.utc).isoformat(),
        invoice=invoice,
        decision=decision,
        fallback_used=fallback_used,
        signals=signals,
    )
    _history.appendleft(result)
    return result


@app.put("/api/decisions/{decision_id}", response_model=DecisionResult)
def update_decision(decision_id: str, invoice: InvoiceInput) -> DecisionResult:
    index, existing = _get_decision(decision_id)
    decision, fallback_used, signals = _run_decision(invoice)
    result = DecisionResult(
        id=existing.id,
        created_at=datetime.now(timezone.utc).isoformat(),
        invoice=invoice,
        decision=decision,
        fallback_used=fallback_used,
        signals=signals,
    )
    items = list(_history)
    items[index] = result
    _history.clear()
    _history.extend(items)
    return result


@app.delete("/api/decisions/{decision_id}")
def delete_decision(decision_id: str) -> dict[str, str]:
    index, _existing = _get_decision(decision_id)
    items = list(_history)
    items.pop(index)
    _history.clear()
    _history.extend(items)
    return {"status": "deleted"}


@app.get("/api/decisions", response_model=list[DecisionResult])
def list_decisions() -> list[DecisionResult]:
    return list(_history)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
