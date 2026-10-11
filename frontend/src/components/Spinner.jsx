export default function Spinner({ label = 'Loading…' }) {
  return (
    <div className="center-block" role="status">
      <span className="spinner" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}
