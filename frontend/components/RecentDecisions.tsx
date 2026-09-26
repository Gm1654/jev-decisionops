import { DecisionResult, formatJevModel } from "@/lib/api";
import { DecisionBadge } from "@/components/DecisionBadge";

type Props = {
  items: DecisionResult[];
  onEdit: (item: DecisionResult) => void;
  onDelete: (item: DecisionResult) => void;
};

export function RecentDecisions({ items, onEdit, onDelete }: Props) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-navy-900">Recent Decisions</h2>
      {items.length === 0 ? (
        <p className="mt-4 text-sm text-slate-500">No decisions yet.</p>
      ) : (
        <div className="mt-4 overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="text-slate-500">
              <tr>
                <th className="pb-3 font-medium">Invoice</th>
                <th className="pb-3 font-medium">Vendor</th>
                <th className="pb-3 font-medium">Amount</th>
                <th className="pb-3 font-medium">Decision</th>
                <th className="pb-3 font-medium">Risk</th>
                <th className="pb-3 font-medium">JEV Model</th>
                <th className="pb-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id} className="border-t border-slate-100">
                  <td className="py-3">{item.invoice.invoice_number}</td>
                  <td className="py-3">{item.invoice.vendor_name}</td>
                  <td className="py-3">
                    {item.invoice.currency} {item.invoice.invoice_amount}
                  </td>
                  <td className="py-3">
                    <DecisionBadge decision={item.decision} />
                  </td>
                  <td className="py-3">{item.signals.risk_score?.toFixed(2) ?? "—"}</td>
                  <td className="py-3">{formatJevModel(item)}</td>
                  <td className="py-3">
                    <div className="flex gap-3">
                      <button type="button" className="text-navy-800 hover:underline" onClick={() => onEdit(item)}>
                        Edit
                      </button>
                      <button type="button" className="text-red-700 hover:underline" onClick={() => onDelete(item)}>
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
