"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { DecisionResult, InvoicePayload, evaluateInvoice, listDecisions } from "@/lib/api";
import { InvoiceForm } from "@/components/InvoiceForm";
import { DecisionResultCard } from "@/components/DecisionResultCard";
import { MetricsRow } from "@/components/MetricsRow";
import { RecentDecisions } from "@/components/RecentDecisions";

const defaultForm: InvoicePayload = {
  vendor_name: "Acme Office Supplies",
  invoice_number: "INV-001",
  invoice_amount: 850,
  currency: "USD",
  vendor_age_months: 24,
  previous_invoices: 20,
  late_deliveries: 0,
  previous_payment_issues: 0,
  duplicate_invoice: false,
  purchase_order_exists: true,
  blocked_vendor: false,
  department: "Operations",
  country: "US",
};

export default function HomePage() {
  const [ready, setReady] = useState(false);
  const [form, setForm] = useState<InvoicePayload>(defaultForm);
  const [latest, setLatest] = useState<DecisionResult | null>(null);
  const [history, setHistory] = useState<DecisionResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const metrics = useMemo(() => {
    const decisions = history.length;
    return {
      decisions,
      auto: history.filter((item) => item.decision === "AUTO_APPROVE").length,
      review: history.filter((item) => item.decision === "HUMAN_REVIEW").length,
      rejected: history.filter((item) => item.decision === "REJECT").length,
    };
  }, [history]);

  useEffect(() => {
    setReady(true);
    listDecisions()
      .then(setHistory)
      .catch(() => undefined);
  }, []);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (loading) return;
    setLoading(true);
    setError(null);
    try {
      const result = await evaluateInvoice(form);
      setLatest(result);
      setHistory((prev) => [result, ...prev].slice(0, 20));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  if (!ready) {
    return <div className="min-h-screen bg-slate-50" />;
  }

  return (
    <div className="min-h-screen">
      <header className="bg-navy-900 text-white">
        <div className="mx-auto max-w-7xl px-6 py-6">
          <h1 className="text-2xl font-semibold tracking-tight">JEV DecisionOps</h1>
          <p className="mt-1 text-sm text-slate-300">Structured Business Decision Engine</p>
        </div>
      </header>

      <main className="mx-auto max-w-7xl space-y-6 px-6 py-8">
        <MetricsRow metrics={metrics} />

        <div className="grid gap-6 lg:grid-cols-2">
          <InvoiceForm
            form={form}
            setForm={setForm}
            loading={loading}
            error={error}
            onSubmit={onSubmit}
          />
          <DecisionResultCard result={latest} />
        </div>

        <RecentDecisions items={history} />
      </main>
    </div>
  );
}
