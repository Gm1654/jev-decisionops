import { FormEvent, ReactNode } from "react";
import { InvoicePayload } from "@/lib/api";

type Props = {
  form: InvoicePayload;
  setForm: (next: InvoicePayload) => void;
  loading: boolean;
  error: string | null;
  onSubmit: (event: FormEvent) => void;
  submitLabel: string;
};

export function InvoiceForm({ form, setForm, loading, error, onSubmit, submitLabel }: Props) {
  function update<K extends keyof InvoicePayload>(key: K, value: InvoicePayload[K]) {
    setForm({ ...form, [key]: value });
  }

  return (
    <form onSubmit={onSubmit} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-navy-900">Invoice</h2>
      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <Field label="Vendor name">
          <input className={inputClass} value={form.vendor_name} onChange={(e) => update("vendor_name", e.target.value)} required />
        </Field>
        <Field label="Invoice number">
          <input className={inputClass} value={form.invoice_number} onChange={(e) => update("invoice_number", e.target.value)} required />
        </Field>
        <Field label="Amount">
          <input
            className={inputClass}
            type="number"
            step="0.01"
            value={form.invoice_amount}
            onChange={(e) => update("invoice_amount", Number(e.target.value))}
            required
          />
        </Field>
        <Field label="Currency">
          <input className={inputClass} value={form.currency} onChange={(e) => update("currency", e.target.value)} required />
        </Field>
        <Field label="Department">
          <input className={inputClass} value={form.department} onChange={(e) => update("department", e.target.value)} required />
        </Field>
        <Field label="Country">
          <input className={inputClass} value={form.country} onChange={(e) => update("country", e.target.value)} required />
        </Field>
        <Field label="Vendor age (months)">
          <input className={inputClass} type="number" value={form.vendor_age_months} onChange={(e) => update("vendor_age_months", Number(e.target.value))} />
        </Field>
        <Field label="Previous invoices">
          <input className={inputClass} type="number" value={form.previous_invoices} onChange={(e) => update("previous_invoices", Number(e.target.value))} />
        </Field>
        <Field label="Late deliveries">
          <input className={inputClass} type="number" value={form.late_deliveries} onChange={(e) => update("late_deliveries", Number(e.target.value))} />
        </Field>
        <Field label="Previous payment issues">
          <input className={inputClass} type="number" value={form.previous_payment_issues} onChange={(e) => update("previous_payment_issues", Number(e.target.value))} />
        </Field>
        <Checkbox label="Duplicate invoice" checked={form.duplicate_invoice} onChange={(v) => update("duplicate_invoice", v)} />
        <Checkbox label="Purchase order exists" checked={form.purchase_order_exists} onChange={(v) => update("purchase_order_exists", v)} />
        <Checkbox label="Blocked vendor" checked={form.blocked_vendor} onChange={(v) => update("blocked_vendor", v)} />
      </div>
      {error ? <p className="mt-4 text-sm text-red-600">{error}</p> : null}
      <button
        type="submit"
        disabled={loading}
        className="mt-6 w-full rounded-lg bg-navy-800 px-4 py-2.5 text-sm font-medium text-white hover:bg-navy-700 disabled:opacity-60"
      >
        {loading ? "Evaluating..." : submitLabel}
      </button>
    </form>
  );
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block text-sm">
      <span className="mb-1 block text-slate-600">{label}</span>
      {children}
    </label>
  );
}

function Checkbox({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: (value: boolean) => void;
}) {
  return (
    <label className="flex items-center gap-2 text-sm text-slate-700">
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} />
      {label}
    </label>
  );
}

const inputClass =
  "w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-navy-700";
