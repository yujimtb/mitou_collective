import Link from "next/link";

export function StatsCard({
  label,
  value,
  note,
  href,
}: {
  label: string;
  value: number;
  note: string;
  href?: string;
}) {
  const content = (
    <div className="card stat-card">
      <div>
        <p className="eyebrow">{label}</p>
        <div className="stat-value">{value}</div>
      </div>
      <p className="supporting-text" style={{ margin: 0 }}>{note}</p>
    </div>
  );

  return href ? <Link href={href}>{content}</Link> : content;
}
