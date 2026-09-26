export function DecisionBadge({ decision }: { decision: string }) {
  const styles =
    decision === "AUTO_APPROVE"
      ? "bg-green-100 text-green-800"
      : decision === "REJECT"
        ? "bg-red-100 text-red-800"
        : "bg-orange-100 text-orange-800";

  return <span className={`rounded-full px-3 py-1 text-xs font-semibold ${styles}`}>{decision}</span>;
}
