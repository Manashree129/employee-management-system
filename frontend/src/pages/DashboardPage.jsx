import { useCallback, useEffect, useState } from 'react';
import { dashboardApi } from '../api';
import Alert from '../components/Alert';
import EmptyState from '../components/EmptyState';
import Spinner from '../components/Spinner';

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = useCallback((signal) => {
    setLoading(true);
    setError('');
    dashboardApi
      .summary(signal)
      .then((d) => setData(d))
      .catch((err) => {
        if (err.name !== 'AbortError') setError(err.message);
      })
      .finally(() => {
        if (!signal || !signal.aborted) setLoading(false);
      });
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    load(controller.signal);
    return () => controller.abort();
  }, [load]);

  if (loading) return <Spinner label="Loading dashboard…" />;
  if (error) {
    return (
      <>
        <h1>Dashboard</h1>
        <Alert onRetry={() => load()}>{error}</Alert>
      </>
    );
  }

  const departments = data.employeesByDepartment || [];
  const max = Math.max(1, ...departments.map((d) => d.employeeCount));

  return (
    <>
      <h1>Dashboard</h1>
      <div className="cards">
        <div className="card stat">
          <span className="stat__label">Total employees</span>
          <span className="stat__value">{data.totalEmployees}</span>
        </div>
        <div className="card stat stat--active">
          <span className="stat__label">Active employees</span>
          <span className="stat__value">{data.activeEmployees}</span>
        </div>
        <div className="card stat stat--inactive">
          <span className="stat__label">Inactive employees</span>
          <span className="stat__value">{data.inactiveEmployees}</span>
        </div>
      </div>

      <section className="card">
        <h2>Employees by department</h2>
        {departments.length === 0 ? (
          <EmptyState title="No departments yet" message="Create a department to see employee counts here." />
        ) : (
          <ul className="bars">
            {departments.map((d) => (
              <li key={d.departmentId} className="bars__row">
                <span className="bars__label">
                  {d.departmentName}
                  {!d.isActive && <em className="muted"> (inactive)</em>}
                </span>
                <span className="bars__track" aria-hidden="true">
                  <span className="bars__fill" style={{ width: `${(d.employeeCount / max) * 100}%` }} />
                </span>
                <span className="bars__value">{d.employeeCount}</span>
              </li>
            ))}
          </ul>
        )}
        {data.totalEmployees === 0 && departments.length > 0 && <p className="muted">No employees have been added yet.</p>}
      </section>
    </>
  );
}
