import { useCallback, useEffect, useState } from 'react';
import { departmentApi } from '../api';
import Alert from '../components/Alert';
import Button from '../components/Button';
import ConfirmDialog from '../components/ConfirmDialog';
import EmptyState from '../components/EmptyState';
import Modal from '../components/Modal';
import Spinner from '../components/Spinner';
import StatusBadge from '../components/StatusBadge';
import { useToast } from '../context/ToastContext';

const CODE_RE = /^[A-Za-z0-9_-]+$/;

function validate({ name, code }) {
  const errors = {};
  const n = name.trim();
  const c = code.trim();
  if (!n) errors.name = 'Department name is required.';
  else if (n.length < 2) errors.name = 'Department name must be at least 2 characters.';
  else if (n.length > 100) errors.name = 'Department name must be at most 100 characters.';
  if (!c) errors.code = 'Department code is required.';
  else if (c.length < 2) errors.code = 'Department code must be at least 2 characters.';
  else if (c.length > 20) errors.code = 'Department code must be at most 20 characters.';
  else if (!CODE_RE.test(c)) errors.code = "Department code may contain only letters, digits, '-' and '_'.";
  return errors;
}

function DepartmentFormModal({ department, onClose, onSaved }) {
  const isEdit = Boolean(department);
  const [form, setForm] = useState({
    name: department?.name || '',
    code: department?.code || '',
    isActive: department ? department.isActive : true,
  });
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const set = (name, value) => {
    setForm((f) => ({ ...f, [name]: value }));
    setErrors((e) => ({ ...e, [name]: undefined }));
  };

  const submit = async (event) => {
    event.preventDefault();
    if (submitting) return;
    const clientErrors = validate(form);
    if (Object.keys(clientErrors).length) {
      setErrors(clientErrors);
      return;
    }
    setSubmitting(true);
    setFormError('');
    const body = { name: form.name.trim(), code: form.code.trim(), isActive: form.isActive };
    try {
      const saved = isEdit ? await departmentApi.update(department.id, body) : await departmentApi.create(body);
      onSaved(saved, isEdit);
    } catch (err) {
      const fieldErrors = {};
      ['name', 'code', 'isActive'].forEach((k) => {
        if (err.errors?.[k]) fieldErrors[k] = err.errors[k].join(' ');
      });
      setErrors(fieldErrors);
      setFormError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      title={isEdit ? 'Edit department' : 'Add department'}
      onClose={onClose}
      busy={submitting}
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={submitting}>
            Cancel
          </Button>
          <Button type="submit" form="department-form" loading={submitting}>
            {submitting ? 'Saving…' : 'Save'}
          </Button>
        </>
      }
    >
      <form id="department-form" onSubmit={submit} noValidate>
        {formError && <Alert>{formError}</Alert>}
        <div className={`field${errors.name ? ' field--error' : ''}`}>
          <label htmlFor="dept-name">
            Name<span className="required"> *</span>
          </label>
          <input id="dept-name" value={form.name} maxLength={100} disabled={submitting} onChange={(e) => set('name', e.target.value)} />
          {errors.name && <small className="field__error">{errors.name}</small>}
        </div>
        <div className={`field${errors.code ? ' field--error' : ''}`}>
          <label htmlFor="dept-code">
            Code<span className="required"> *</span>
          </label>
          <input id="dept-code" value={form.code} maxLength={20} disabled={submitting} onChange={(e) => set('code', e.target.value)} />
          {errors.code && <small className="field__error">{errors.code}</small>}
        </div>
        <div className="field">
          <label className="checkbox">
            <input type="checkbox" checked={form.isActive} disabled={submitting} onChange={(e) => set('isActive', e.target.checked)} />
            <span>Active</span>
          </label>
        </div>
      </form>
    </Modal>
  );
}

export default function DepartmentsPage() {
  const { notify } = useToast();
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [pageError, setPageError] = useState(''); // e.g. delete blocked (409)
  const [editing, setEditing] = useState(null); // null | 'new' | department
  const [toDelete, setToDelete] = useState(null);
  const [busyId, setBusyId] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const load = useCallback((signal) => {
    setLoading(true);
    setError('');
    departmentApi
      .list({}, signal)
      .then(setDepartments)
      .catch((err) => err.name !== 'AbortError' && setError(err.message))
      .finally(() => {
        if (!signal || !signal.aborted) setLoading(false);
      });
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    load(controller.signal);
    return () => controller.abort();
  }, [load]);

  const toggleActive = async (d) => {
    setBusyId(d.id);
    setPageError('');
    try {
      await departmentApi.update(d.id, { name: d.name, code: d.code, isActive: !d.isActive });
      notify('success', `${d.name} was ${d.isActive ? 'deactivated' : 'activated'}.`);
      load();
    } catch (err) {
      setPageError(err.message);
    } finally {
      setBusyId(null);
    }
  };

  const confirmDelete = async () => {
    setDeleting(true);
    setPageError('');
    try {
      await departmentApi.remove(toDelete.id);
      notify('success', `Department ${toDelete.name} was deleted.`);
      setToDelete(null);
      load();
    } catch (err) {
      // 409: the department still has employees; show the backend's explanation.
      setPageError(err.message);
      setToDelete(null);
    } finally {
      setDeleting(false);
    }
  };

  const onSaved = (saved, wasEdit) => {
    notify('success', `Department ${saved.name} was ${wasEdit ? 'updated' : 'created'}.`);
    setEditing(null);
    load();
  };

  return (
    <>
      <div className="page-header">
        <h1>Departments</h1>
        <Button onClick={() => { setPageError(''); setEditing('new'); }}>Add Department</Button>
      </div>

      {pageError && <Alert onClose={() => setPageError('')}>{pageError}</Alert>}
      {error && <Alert onRetry={() => load()}>{error}</Alert>}
      {loading && departments.length === 0 && !error && <Spinner label="Loading departments…" />}

      {!error && !(loading && departments.length === 0) && (
        <div className="card card--table" aria-busy={loading}>
          {departments.length === 0 ? (
            <EmptyState title="No departments yet" message="Add a department to start organising employees." />
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Code</th>
                    <th>Status</th>
                    <th>Employees</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {departments.map((d) => (
                    <tr key={d.id}>
                      <td>{d.name}</td>
                      <td>{d.code}</td>
                      <td>
                        <StatusBadge active={d.isActive} />
                      </td>
                      <td>{d.employeeCount}</td>
                      <td>
                        <div className="row-actions">
                          <Button variant="secondary" size="sm" onClick={() => { setPageError(''); setEditing(d); }}>
                            Edit
                          </Button>
                          <Button variant="secondary" size="sm" loading={busyId === d.id} disabled={busyId !== null} onClick={() => toggleActive(d)}>
                            {d.isActive ? 'Deactivate' : 'Activate'}
                          </Button>
                          <Button variant="danger" size="sm" disabled={busyId !== null} onClick={() => { setPageError(''); setToDelete(d); }}>
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
        </div>
      )}

      {editing && (
        <DepartmentFormModal department={editing === 'new' ? null : editing} onClose={() => setEditing(null)} onSaved={onSaved} />
      )}
      {toDelete && (
        <ConfirmDialog
          title="Delete department?"
          message={`Delete the ${toDelete.name} department? This cannot be undone. Departments that have employees cannot be deleted.`}
          busy={deleting}
          onConfirm={confirmDelete}
          onCancel={() => setToDelete(null)}
        />
      )}
    </>
  );
}
