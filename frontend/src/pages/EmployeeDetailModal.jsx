import { useEffect, useState } from 'react';
import { employeeApi } from '../api';
import Alert from '../components/Alert';
import Button from '../components/Button';
import Modal from '../components/Modal';
import Spinner from '../components/Spinner';
import StatusBadge from '../components/StatusBadge';
import { formatCurrency, formatDate } from '../utils/format';

export default function EmployeeDetailModal({ id, onClose }) {
  const [employee, setEmployee] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const controller = new AbortController();
    employeeApi
      .get(id, controller.signal)
      .then(setEmployee)
      .catch((err) => err.name !== 'AbortError' && setError(err.message));
    return () => controller.abort();
  }, [id]);

  const rows = employee
    ? [
        ['Employee code', employee.employeeCode],
        ['Full name', employee.fullName],
        ['Email', employee.email],
        ['Mobile', employee.mobileNumber],
        ['Date of birth', formatDate(employee.dateOfBirth)],
        ['Gender', employee.gender],
        ['Department', employee.departmentName],
        ['Designation', employee.designationName],
        ['Employment type', employee.employmentType],
        ['Joining date', formatDate(employee.joiningDate)],
        ['Contract end date', formatDate(employee.contractEndDate)],
        ['Salary', formatCurrency(employee.salary)],
        ['Address', employee.address || '—'],
      ]
    : [];

  return (
    <Modal title="Employee details" onClose={onClose} footer={<Button variant="secondary" onClick={onClose}>Close</Button>}>
      {error && <Alert>{error}</Alert>}
      {!employee && !error && <Spinner />}
      {employee && (
        <dl className="details">
          {rows.map(([label, value]) => (
            <div key={label} className="details__row">
              <dt>{label}</dt>
              <dd>{value}</dd>
            </div>
          ))}
          <div className="details__row">
            <dt>Status</dt>
            <dd>
              <StatusBadge active={employee.isActive} />
            </dd>
          </div>
        </dl>
      )}
    </Modal>
  );
}
