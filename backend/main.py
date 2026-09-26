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
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_history: deque[DecisionResult] = deque(maxlen=20)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/decisions", response_model=DecisionResult)
def create_decision(invoice: InvoiceInput) -> DecisionResult:
    if invoice.invoice_amount <= 0:
        raise HTTPException(status_code=400, detail="invoice_amount must be greater than 0")

    jev_failed = False
    signals = JevSignals()

    if not invoice.duplicate_invoice and not invoice.blocked_vendor:
        signals, jev_failed = evaluate_invoice(invoice)

    decision, fallback_used = apply_policy(invoice, signals, jev_failed)
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


@app.get("/api/decisions", response_model=list[DecisionResult])
def list_decisions() -> list[DecisionResult]:
    return list(_history)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
