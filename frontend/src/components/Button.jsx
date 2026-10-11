export default function Button({
  variant = 'primary',
  size,
  type = 'button',
  loading = false,
  disabled = false,
  children,
  ...rest
}) {
  const classes = `btn btn--${variant}${size === 'sm' ? ' btn--sm' : ''}`;
  return (
    <button type={type} className={classes} disabled={disabled || loading} {...rest}>
      {loading && <span className="spinner spinner--inline" aria-hidden="true" />}
      {children}
    </button>
  );
}
