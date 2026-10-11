import { useEffect, useMemo, useRef, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { EMPLOYEE_FORM, departmentApi, employeeApi, formConfigApi, lookupApi } from '../api';
import Alert from '../components/Alert';
import Button from '../components/Button';
import FormField from '../components/FormField';
import Spinner from '../components/Spinner';
import { useToast } from '../context/ToastContext';
import { buildInitialValues, buildPayload, isReadOnly, isVisible, validateField, validateForm } from '../utils/formRules';

/**
 * Add / edit employee. The field list, labels, types, order, required flags, validation rules and
 * conditional visibility all come from GET /api/form-config/employee: nothing about individual
 * employee fields is hardcoded here.
 */
export default function EmployeeFormPage() {
  const { id } = useParams();
  const isEdit = id !== undefined;
  const navigate = useNavigate();
  const { notify } = useToast();

  const [status, setStatus] = useState('loading'); // loading | ready | error
  const [loadError, setLoadError] = useState('');
  const [reloadKey, setReloadKey] = useState(0);

  const [fields, setFields] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [lookups, setLookups] = useState({});
  const [employee, setEmployee] = useState(null);

  const [values, setValues] = useState({});
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const initialValues = useRef({});

  const [designations, setDesignations] = useState([]);
  const [designationsLoading, setDesignationsLoading] = useState(false);
  const [designationsError, setDesignationsError] = useState('');

  // ---- load configuration, dropdown data and (when editing) the employee --------------------
  useEffect(() => {
    const controller = new AbortController();
    const { signal } = controller;
    async function load() {
      setStatus('loading');
      setLoadError('');
      try {
        const [config, deptList, record] = await Promise.all([
          formConfigApi.get(EMPLOYEE_FORM, signal),
          departmentApi.list({ active: true }, signal),
          isEdit ? employeeApi.get(id, signal) : Promise.resolve(null),
        ]);
        const sorted = [...config.fields].sort((a, b) => a.displayOrder - b.displayOrder);

        const categories = [
          ...new Set(
            sorted
              .map((f) => f.optionsSource)
              .filter((s) => s && s.startsWith('lookup:'))
              .map((s) => s.slice('lookup:'.length)),
          ),
        ];
        const lookupResults = await Promise.all(categories.map((c) => lookupApi.get(c, signal)));
        const lookupMap = {};
        categories.forEach((c, i) => {
          lookupMap[c] = lookupResults[i].map((l) => ({ value: l.value, label: l.label }));
        });

        const initial = buildInitialValues(sorted, record);
        initialValues.current = initial;
        setFields(sorted);
        setDepartments(deptList);
        setLookups(lookupMap);
        setEmployee(record);
        setValues(initial);
        setErrors({});
        setFormError('');
        setStatus('ready');
      } catch (err) {
        if (err.name === 'AbortError') return;
        setLoadError(err.message);
        setStatus('error');
      }
    }
    load();
    return () => controller.abort();
  }, [id, isEdit, reloadKey]);

  // ---- designations depend on the department chosen --------------------------------------
  const designationField = useMemo(() => fields.find((f) => f.optionsSource === 'designations'), [fields]);
  const parentName = designationField ? designationField.dependsOn : '';
  const parentValue = parentName ? values[parentName] : '';

  useEffect(() => {
    if (!designationField) return undefined;
    if (!parentValue) {
      setDesignations([]);
      setDesignationsError('');
      return undefined;
    }
    const controller = new AbortController();
    setDesignationsLoading(true);
    setDesignationsError('');
    departmentApi
      .designations(parentValue, controller.signal)
      .then((list) => setDesignations(list.map((d) => ({ value: String(d.id), label: d.name }))))
      .catch((err) => {
        if (err.name === 'AbortError') return;
        setDesignations([]);
        setDesignationsError(`Designations could not be loaded: ${err.message}`);
      })
      .finally(() => {
        if (!controller.signal.aborted) setDesignationsLoading(false);
      });
    return () => controller.abort();
  }, [designationField, parentValue]);

  // ---- helpers -----------------------------------------------------------------------------
  const labelOf = (name) => fields.find((f) => f.fieldName === name)?.label || name;

  const optionsFor = (field) => {
    const source = field.optionsSource || '';
    if (source === 'departments') {
      const options = departments.map((d) => ({ value: String(d.id), label: d.name }));
      // Keep the saved department selectable when it has since been deactivated.
      if (employee && !options.some((o) => o.value === String(employee.departmentId))) {
        options.push({ value: String(employee.departmentId), label: `${employee.departmentName} (inactive)` });
      }
      return options;
    }
    if (source === 'designations') return designations;
    if (source.startsWith('lookup:')) return lookups[source.slice('lookup:'.length)] || [];
    return [];
  };

  const handleChange = (name, value) => {
    const next = { ...values, [name]: value };
    const nextErrors = { ...errors };
    delete nextErrors[name];

    // Clear dependent fields (e.g. the designation when the department changes).
    fields.forEach((f) => {
      if (f.dependsOn === name) {
        next[f.fieldName] = '';
        delete nextErrors[f.fieldName];
      }
    });
    // Clear fields that just became hidden (e.g. contract end date for Permanent).
    fields.forEach((f) => {
      if (!isVisible(f.conditionalRules, next)) {
        next[f.fieldName] = f.inputType === 'checkbox' ? false : '';
        delete nextErrors[f.fieldName];
      }
    });

    setValues(next);
    setErrors(nextErrors);
    setFormError('');
  };

  const handleBlur = (name) => {
    const field = fields.find((f) => f.fieldName === name);
    if (!field || !isVisible(field.conditionalRules, values)) return;
    const message = validateField(field, values, fields);
    setErrors((prev) => {
      const next = { ...prev };
      if (message) next[name] = message;
      else delete next[name];
      return next;
    });
  };

  const handleReset = () => {
    setValues(initialValues.current);
    setErrors({});
    setFormError('');
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (submitting) return;

    const clientErrors = validateForm(fields, values);
    if (Object.keys(clientErrors).length > 0) {
      setErrors(clientErrors);
      setFormError('Please correct the highlighted fields.');
      const first = fields.find((f) => clientErrors[f.fieldName]);
      if (first) document.getElementById(`field-${first.fieldName}`)?.focus();
      return;
    }

    setSubmitting(true);
    setFormError('');
    try {
      const payload = buildPayload(fields, values);
      if (isEdit) {
        const saved = await employeeApi.update(id, payload);
        notify('success', `Employee ${saved.employeeCode} was updated.`);
      } else {
        const saved = await employeeApi.create(payload);
        notify('success', `Employee ${saved.employeeCode} (${saved.fullName}) was created.`);
      }
      navigate('/employees');
    } catch (err) {
      const fieldNames = new Set(fields.map((f) => f.fieldName));
      const fieldErrors = {};
      const otherMessages = [];
      Object.entries(err.errors || {}).forEach(([key, messages]) => {
        if (fieldNames.has(key)) fieldErrors[key] = Array.isArray(messages) ? messages.join(' ') : String(messages);
        else otherMessages.push(Array.isArray(messages) ? messages.join(' ') : String(messages));
      });
      setErrors(fieldErrors);
      if (Object.keys(fieldErrors).length > 0) {
        setFormError([err.message, ...otherMessages].join(' '));
        const first = fields.find((f) => fieldErrors[f.fieldName]);
        if (first) document.getElementById(`field-${first.fieldName}`)?.focus();
      } else {
        setFormError([err.message, ...otherMessages].join(' '));
      }
    } finally {
      setSubmitting(false);
    }
  };

  // ---- render --------------------------------------------------------------------------------
  const title = isEdit ? `Edit Employee${employee ? ` ${employee.employeeCode}` : ''}` : 'Add Employee';

  if (status === 'loading') return <Spinner label="Loading form…" />;
  if (status === 'error') {
    return (
      <>
        <h1>{isEdit ? 'Edit Employee' : 'Add Employee'}</h1>
        <Alert onRetry={() => setReloadKey((k) => k + 1)}>{loadError}</Alert>
        <Link to="/employees" className="btn btn--secondary">
          Back to employees
        </Link>
      </>
    );
  }

  const visibleFields = fields.filter((f) => isVisible(f.conditionalRules, values));

  return (
    <>
      <div className="page-header">
        <h1>{title}</h1>
      </div>

      <form className="card form" onSubmit={handleSubmit} noValidate>
        {formError && <Alert>{formError}</Alert>}
        {designationsError && <Alert type="warning">{designationsError}</Alert>}

        <div className="form__grid">
          {visibleFields.map((field) => {
            const dependsOn = field.dependsOn;
            const waitingForParent = Boolean(dependsOn) && !values[dependsOn];
            let hint = '';
            if (waitingForParent) hint = `Select ${labelOf(dependsOn).toLowerCase()} first`;
            else if (field.optionsSource === 'designations' && designationsLoading) hint = 'Loading…';
            return (
              <FormField
                key={field.fieldName}
                field={field}
                value={values[field.fieldName] ?? ''}
                error={errors[field.fieldName]}
                options={optionsFor(field)}
                hint={hint}
                disabled={submitting || (field.inputType === 'select' && (waitingForParent || (field.optionsSource === 'designations' && designationsLoading)))}
                onChange={handleChange}
                onBlur={handleBlur}
              />
            );
          })}
        </div>

        <div className="form__footer">
          <Button type="submit" loading={submitting}>
            {submitting ? 'Saving…' : isEdit ? 'Save Changes' : 'Create Employee'}
          </Button>
          <Button variant="secondary" onClick={handleReset} disabled={submitting}>
            Reset
          </Button>
          <Link to="/employees" className="btn btn--secondary" aria-disabled={submitting}>
            Cancel
          </Link>
        </div>
      </form>
    </>
  );
}
