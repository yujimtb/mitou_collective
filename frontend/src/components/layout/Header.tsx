export function Header({
  title,
  subtitle,
  action,
}: {
  title: string;
  subtitle: string;
  action?: React.ReactNode;
}) {
  return (
    <header className="panel header-row">
      <div>
        <p className="eyebrow">Research Surface</p>
        <h1 className="header-title">{title}</h1>
        <p className="hero-subtitle" style={{ marginBottom: 0 }}>{subtitle}</p>
      </div>
      {action ? <div>{action}</div> : null}
    </header>
  );
}
