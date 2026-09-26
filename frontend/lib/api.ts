export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type InvoicePayload = {
  vendor_name: string;
  invoice_number: string;
  invoice_amount: number;
  currency: string;
  vendor_age_months: number;
  previous_invoices: number;
  late_deliveries: number;
  previous_payment_issues: number;
  duplicate_invoice: boolean;
  purchase_order_exists: boolean;
  blocked_vendor: boolean;
  department: string;
  country: string;
};

export type DecisionResult = {
  id: string;
  created_at: string;
  invoice: InvoicePayload;
  decision: "AUTO_APPROVE" | "HUMAN_REVIEW" | "REJECT";
  fallback_used: boolean;
  signals: {
    risk_score: number | null;
    confidence: number | null;
    review_probability: number | null;
    route: string | null;
    route_confidence: number | null;
    vendor_reliability: number | null;
    priority: string | null;
    model: string | null;
  };
};

function apiErrorMessage(body: unknown, fallback: string): string {
  if (!body || typeof body !== "object" || !("detail" in body)) {
    return fallback;
  }
  const detail = (body as { detail: unknown }).detail;
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    const parts = detail.map((item) => {
      if (typeof item === "string") return item;
      if (item && typeof item === "object" && "msg" in item) {
        return String((item as { msg: unknown }).msg);
      }
      return "";
    });
    const message = parts.filter(Boolean).join("; ");
    return message || fallback;
  }
  return fallback;
}

export async function evaluateInvoice(payload: InvoicePayload): Promise<DecisionResult> {
  const response = await fetch(`${API_BASE}/api/decisions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(apiErrorMessage(body, "Decision request failed"));
  }
  return response.json();
}

export async function listDecisions(): Promise<DecisionResult[]> {
  const response = await fetch(`${API_BASE}/api/decisions`);
  if (!response.ok) {
    throw new Error("Failed to load decisions");
  }
  return response.json();
}
