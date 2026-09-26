type Metrics = {
  decisions: number;
  auto: number;
  review: number;
  rejected: number;
};

export function MetricsRow({ metrics }: { metrics: Metrics }) {
  const cards = [
    { label: "Decisions This Session", value: metrics.decisions },
    { label: "Auto Approved", value: metrics.auto },
    { label: "Human Review", value: metrics.review },
    { label: "Rejected", value: metrics.rejected },
  ];

  return (
    <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => (
        <div key={card.label} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <p className="text-sm text-slate-500">{card.label}</p>
          <p className="mt-2 text-2xl font-semibold text-navy-900">{card.value}</p>
        </div>
      ))}
    </section>
  );
}
