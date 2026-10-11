export default function StatusBadge({ active, activeLabel = 'Active', inactiveLabel = 'Inactive' }) {
  return (
    <span className={`badge ${active ? 'badge--active' : 'badge--inactive'}`}>
      {active ? activeLabel : inactiveLabel}
    </span>
  );
}
