import Button from './Button';

function pageWindow(page, totalPages) {
  const start = Math.max(1, Math.min(page - 2, totalPages - 4));
  const end = Math.min(totalPages, start + 4);
  const pages = [];
  for (let p = start; p <= end; p += 1) pages.push(p);
  return pages;
}

export default function Pagination({ page, size, totalItems, totalPages, onPageChange, disabled = false }) {
  if (totalItems === 0) return null;
  const from = (page - 1) * size + 1;
  const to = Math.min(page * size, totalItems);
  return (
    <nav className="pagination" aria-label="Pagination">
      <span className="pagination__info">
        Showing {from}–{to} of {totalItems}
      </span>
      <div className="pagination__buttons">
        <Button variant="secondary" size="sm" disabled={disabled || page <= 1} onClick={() => onPageChange(page - 1)}>
          Previous
        </Button>
        {pageWindow(page, totalPages).map((p) => (
          <Button
            key={p}
            variant={p === page ? "primary" : "secondary"}
            size="sm"
            disabled={disabled}
            aria-current={p === page ? 'page' : undefined}
            onClick={() => onPageChange(p)}
          >
            {p}
          </Button>
        ))}
        <Button variant="secondary" size="sm" disabled={disabled || page >= totalPages} onClick={() => onPageChange(page + 1)}>
          Next
        </Button>
      </div>
    </nav>
  );
}
