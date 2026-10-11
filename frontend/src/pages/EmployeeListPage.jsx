import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { departmentApi, employeeApi, lookupApi } from '../api';
import Alert from '../components/Alert';
import Button from '../components/Button';
import ConfirmDialog from '../components/ConfirmDialog';
import EmptyState from '../components/EmptyState';
import Pagination from '../components/Pagination';
import Spinner from '../components/Spinner';
import StatusBadge from '../components/StatusBadge';
import { useToast } from '../context/ToastContext';
import { formatDate } from '../utils/format';
import EmployeeDetailModal from './EmployeeDetailModal';

const DEFAULT_QUERY = { page: 1, size: 10, search: '', departmentId: '', status: '', sortBy: 'name', sortDir: 'asc' };

function useDebounced(value, delay = 400) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

export default function EmployeeListPage() {
  const navigate = useNavigate();
  const { notify } = useToast();

  const [query, setQuery] = useState(DEFAULT_QUERY);
  const [searchInput, setSearchInput] = useState('');
  const debouncedSearch = useDebounced(searchInput);

  const [result, setResult] = useState(null); // { items, pagination }
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshKey, setRefreshKey] = useState(0);

  const [departments, setDepartments] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [filterError, setFilterError] = useState('');

  const [viewId, setViewId] = useState(null);
  const [toDelete, setToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);

  // Filter dropdown options come from the backend.
  useEffect(() => {
    const controller = new AbortController();
    Promise.all([departmentApi.list({}, controller.signal), lookupApi.get('employee_status', controller.signal)])
      .then(([depts, status]) => {
        setDepartments(depts);
        setStatuses(status);
      })
      .catch((err) => err.name !== 'AbortError' && setFilterError(`Filters could not be loaded: ${err.message}`));
    return () => controller.abort();
  }, []);

  // A new search term always returns to page 1.
  useEffect(() => {
    setQuery((q) => (q.search === debouncedSearch.trim() ? q : { ...q, search: debouncedSearch.trim(), page: 1 }));
  }, [debouncedSearch]);

  // Server-side pagination, filtering and sorting: the browser never holds more than one page.
  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError('');
    employeeApi
      .list(query, controller.signal)
      .then((data) => {
        const { totalPages } = data.pagination;
        if (data.items.length === 0 && query.page > 1 && totalPages > 0) {
          setQuery((q) => ({ ...q, page: totalPages })); // e.g. last row of the last page was deleted
          return;
        }
        setResult(data);
        setLoading(false);
      })
      .catch((err) => {
        if (err.name === 'AbortError') return;
        setError(err.message);
        setLoading(false);
      });
    return () => controller.abort();
  }, [query, refreshKey]);

  const updateFilter = (name, value) => setQuery((q) => ({ ...q, [name]: value, page: 1 }));

  const toggleSort = (column) =>
    setQuery((q) => ({
      ...q,
      sortBy: column,
      sortDir: q.sortBy === column && q.sortDir === 'asc' ? 'desc' : 'asc',
      page: 1,
    }));

  const sortIndicator = (column) => (query.sortBy === column ? (query.sortDir === 'asc' ? ' ▲' : ' ▼') : '');
  const ariaSort = (column) => (query.sortBy === column ? (query.sortDir === 'asc' ? 'ascending' : 'descending') : 'none');

  const clearFilters = () => {
    setSearchInput('');
    setQuery(DEFAULT_QUERY);
  };

  const confirmDelete = async () => {
    setDeleting(true);
    try {
      await employeeApi.remove(toDelete.id);
      notify('success', `Employee ${toDelete.employeeCode} (${toDelete.fullName}) was deleted.`);
      setToDelete(null);
      setRefreshKey((k) => k + 1);
    } catch (err) {
      notify('error', err.message);
      setToDelete(null);
      setRefreshKey((k) => k + 1);
    } finally {
      setDeleting(false);
    }
  };

  const filtersActive = query.search || query.departmentId || query.status;
  const items = result?.items || [];
  const pagination = result?.pagination;

  return (
    <>
      <div className="page-header">
        <h1>Employees</h1>
        <Link to="/employees/new" className="btn btn--primary">
          Add Employee
        </Link>
      </div>

      {filterError && <Alert type="warning">{filterError}</Alert>}

      <div className="card filters">
        <div className="field">
          <label htmlFor="search">Search</label>
          <input
            id="search"
            type="search"
            value={searchInput}
            placeholder="Name, email or employee code"
            onChange={(e) => setSearchInput(e.target.value)}
          />
        </div>
        <div className="field">
          <label htmlFor="filter-department">Department</label>
          <select id="filter-department" value={query.departmentId} onChange={(e) => updateFilter('departmentId', e.target.value)}>
            <option value="">All departments</option>
            {departments.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="filter-status">Status</label>
          <select id="filter-status" value={query.status} onChange={(e) => updateFilter('status', e.target.value)}>
            <option value="">All statuses</option>
            {statuses.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        </div>
        <div className="filters__actions">
          <Button variant="secondary" onClick={clearFilters} disabled={!filtersActive && query.sortBy === 'name' && query.sortDir === 'asc'}>
            Clear
          </Button>
        </div>
      </div>

      {error && <Alert onRetry={() => setRefreshKey((k) => k + 1)}>{error}</Alert>}

      {loading && !result && <Spinner label="Loading employees…" />}

      {result && !error && (
        <div className="card card--table" aria-busy={loading}>
          {loading && <div className="table-loading"><span className="spinner spinner--inline" /> Updating…</div>}
          {items.length === 0 ? (
            <EmptyState
              title={filtersActive ? 'No employees match your filters' : 'No employees yet'}
              message={filtersActive ? 'Try a different search or clear the filters.' : 'Add your first employee to get started.'}
              action={
                filtersActive ? (
                  <Button variant="secondary" onClick={clearFilters}>
                    Clear filters
                  </Button>
                ) : (
                  <Link to="/employees/new" className="btn btn--primary">
                    Add Employee
                  </Link>
                )
              }
            />
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Employee Code</th>
                    <th aria-sort={ariaSort('name')}>
                      <button type="button" className="sort" onClick={() => toggleSort('name')}>
                        Full Name{sortIndicator('name')}
                      </button>
                    </th>
                    <th>Email</th>
                    <th>Department</th>
                    <th>Designation</th>
                    <th aria-sort={ariaSort('joiningDate')}>
                      <button type="button" className="sort" onClick={() => toggleSort('joiningDate')}>
                        Joining Date{sortIndicator('joiningDate')}
                      </button>
                    </th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((e) => (
                    <tr key={e.id}>
                      <td>{e.employeeCode}</td>
                      <td>{e.fullName}</td>
                      <td>{e.email}</td>
                      <td>{e.departmentName}</td>
                      <td>{e.designationName}</td>
                      <td>{formatDate(e.joiningDate)}</td>
                      <td>
                        <StatusBadge active={e.isActive} />
                      </td>
                      <td>
                        <div className="row-actions">
                          <Button variant="secondary" size="sm" onClick={() => setViewId(e.id)}>
                            View
                          </Button>
                          <Button variant="secondary" size="sm" onClick={() => navigate(`/employees/${e.id}/edit`)}>
                            Edit
                          </Button>
                          <Button variant="danger" size="sm" onClick={() => setToDelete(e)}>
                            Delete
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {pagination && (
            <Pagination
              page={pagination.page}
              size={pagination.size}
              totalItems={pagination.totalItems}
              totalPages={pagination.totalPages}
              disabled={loading}
              onPageChange={(page) => setQuery((q) => ({ ...q, page }))}
            />
          )}
        </div>
      )}

      {viewId && <EmployeeDetailModal id={viewId} onClose={() => setViewId(null)} />}
      {toDelete && (
        <ConfirmDialog
          title="Delete employee?"
          message={`Delete ${toDelete.fullName} (${toDelete.employeeCode})? The employee will be removed from the list.`}
          busy={deleting}
          onConfirm={confirmDelete}
          onCancel={() => setToDelete(null)}
        />
      )}
    </>
  );
}
