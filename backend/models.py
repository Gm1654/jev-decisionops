from typing import Literal, Optional

from pydantic import BaseModel, Field

Decision = Literal["AUTO_APPROVE", "HUMAN_REVIEW", "REJECT"]


class InvoiceInput(BaseModel):
    vendor_name: str
    invoice_number: str
    invoice_amount: float
    currency: str = "USD"
    vendor_age_months: int = Field(ge=0)
    previous_invoices: int = Field(ge=0)
    late_deliveries: int = Field(ge=0)
    previous_payment_issues: int = Field(ge=0)
    duplicate_invoice: bool
    purchase_order_exists: bool
    blocked_vendor: bool
    department: str
    country: str


class JevSignals(BaseModel):
    risk_score: Optional[float] = None
    confidence: Optional[float] = None
    review_probability: Optional[float] = None
    route: Optional[str] = None
    route_confidence: Optional[float] = None
    vendor_reliability: Optional[float] = None
    priority: Optional[str] = None
    model: Optional[str] = None


class DecisionResult(BaseModel):
    id: str
    created_at: str
    invoice: InvoiceInput
    decision: Decision
    fallback_used: bool
    signals: JevSignals
