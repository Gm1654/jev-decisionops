import { DecisionResult, formatJevModel } from "@/lib/api";
import { DecisionBadge } from "@/components/DecisionBadge";

export function DecisionResultCard({ result }: { result: DecisionResult | null }) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-navy-900">Latest Decision</h2>
      {!result ? (
        <p className="mt-6 text-sm text-slate-500">Submit an invoice to see the decision.</p>
      ) : (
        <div className="mt-5 space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-500">Final Decision</p>
            <DecisionBadge decision={result.decision} />
          </div>
          <Row label="Risk Score" value={fmt(result.signals.risk_score)} />
          <Row label="Confidence" value={pct(result.signals.confidence)} />
          <Row label="Review Probability" value={pct(result.signals.review_probability)} />
          <Row label="Route" value={result.signals.route} />
          <Row label="Vendor Reliability" value={fmt(result.signals.vendor_reliability)} />
          <Row label="Priority" value={result.signals.priority} />
          <Row label="JEV Model" value={formatJevModel(result)} />
          <Row label="Fallback Used" value={result.fallback_used ? "true" : "false"} />
        </div>
      )}
    </section>
  );
}

function Row({ label, value }: { label: string; value: string | null | undefined }) {
  return (
    <div className="flex items-center justify-between border-t border-slate-100 pt-3 text-sm">
      <span className="text-slate-500">{label}</span>
      <span className="font-medium text-navy-900">{value || "—"}</span>
    </div>
  );
}

function fmt(value: number | null) {
  return value === null || value === undefined ? "—" : value.toFixed(2);
}

function pct(value: number | null) {
  return value === null || value === undefined ? "—" : `${(value * 100).toFixed(1)}%`;
}
