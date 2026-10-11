export default function Alert({ type = 'error', children, onRetry, onClose }) {
  return (
    <div className={`alert alert--${type}`} role={type === 'error' ? 'alert' : 'status'}>
      <div className="alert__body">{children}</div>
      {onRetry && (
        <button type="button" className="btn btn--secondary btn--sm" onClick={onRetry}>
          Retry
        </button>
      )}
      {onClose && (
        <button type="button" className="toast__close" onClick={onClose} aria-label="Dismiss">
          ×
        </button>
      )}
    </div>
  );
}
