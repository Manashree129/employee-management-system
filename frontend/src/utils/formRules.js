// Helpers that interpret the form configuration returned by GET /api/form-config/{formName}.
// Nothing here knows about specific employee fields: it only reads rule keys.

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function todayISO() {
  const now = new Date();
  const m = String(now.getMonth() + 1).padStart(2, '0');
  const d = String(now.getDate()).padStart(2, '0');
  return `${now.getFullYear()}-${m}-${d}`;
}

function ageOn(isoDob, isoToday) {
  const [by, bm, bd] = isoDob.split('-').map(Number);
  const [ty, tm, td] = isoToday.split('-').map(Number);
  return ty - by - (tm > bm || (tm === bm && td >= bd) ? 0 : 1);
}

/** conditionalRules: null = always visible; otherwise show when field <operator> value. */
export function isVisible(rule, values) {
  if (!rule) return true;
  const actual = String(values[rule.field] ?? '');
  const expected = Array.isArray(rule.value) ? rule.value.map(String) : [String(rule.value)];
  switch (rule.operator) {
    case 'equals':
      return actual === expected[0];
    case 'notEquals':
      return actual !== expected[0];
    case 'in':
      return expected.includes(actual);
    case 'notIn':
      return !expected.includes(actual);
    default:
      return true;
  }
}

export function isReadOnly(field) {
  return Boolean(field.validationRules?.readOnly);
}

export function validateField(field, values, allFields = []) {
  const { fieldName, label, inputType, isRequired } = field;
  const rules = field.validationRules || {};
  if (inputType === 'checkbox' || isReadOnly(field)) return '';

  const raw = values[fieldName];
  const value = typeof raw === 'string' ? raw.trim() : raw;
  if (value === '' || value === null || value === undefined) {
    return isRequired ? `${label} is required.` : '';
  }
  const text = String(value);

  if (rules.minLength != null && text.length < rules.minLength) {
    return `${label} must be at least ${rules.minLength} characters.`;
  }
  if (rules.maxLength != null && text.length > rules.maxLength) {
    return `${label} must be at most ${rules.maxLength} characters.`;
  }
  if (rules.pattern && !new RegExp(rules.pattern).test(text)) {
    return rules.patternMessage || `${label} format is invalid.`;
  }
  if (inputType === 'email' && !EMAIL_RE.test(text)) {
    return 'Enter a valid email address.';
  }
  if (inputType === 'number') {
    const n = Number(text);
    if (Number.isNaN(n)) return `${label} must be a number.`;
    if (rules.greaterThan != null && !(n > rules.greaterThan)) {
      return `${label} must be greater than ${rules.greaterThan}.`;
    }
  }
  if (inputType === 'date') {
    const today = todayISO();
    if (rules.notFuture && text > today) return `${label} cannot be in the future.`;
    if (rules.minAge != null && ageOn(text, today) < rules.minAge) {
      return `Employee must be at least ${rules.minAge} years old.`;
    }
    if (rules.laterThanField) {
      const other = values[rules.laterThanField];
      if (other && text <= other) {
        const otherLabel =
          allFields.find((f) => f.fieldName === rules.laterThanField)?.label || rules.laterThanField;
        return `${label} must be later than ${otherLabel}.`;
      }
    }
  }
  return '';
}

/** Validates every visible, editable field. Returns { fieldName: message }. */
export function validateForm(fields, values) {
  const errors = {};
  fields.forEach((field) => {
    if (!isVisible(field.conditionalRules, values)) return;
    const message = validateField(field, values, fields);
    if (message) errors[field.fieldName] = message;
  });
  return errors;
}

/** Initial form values: from an existing record (edit) or the configured defaults (new). */
export function buildInitialValues(fields, record) {
  const values = {};
  fields.forEach((field) => {
    const { fieldName, inputType, defaultValue } = field;
    if (record) {
      const v = record[fieldName];
      values[fieldName] = inputType === 'checkbox' ? Boolean(v) : v === null || v === undefined ? '' : String(v);
    } else if (inputType === 'checkbox') {
      values[fieldName] = defaultValue === null || defaultValue === undefined ? false : Boolean(defaultValue);
    } else {
      values[fieldName] = defaultValue === null || defaultValue === undefined ? '' : String(defaultValue);
    }
  });
  return values;
}

/** Request body: only visible, editable fields, converted to the types the API expects. */
export function buildPayload(fields, values) {
  const payload = {};
  fields.forEach((field) => {
    if (isReadOnly(field) || !isVisible(field.conditionalRules, values)) return;
    const { fieldName, inputType, optionsSource } = field;
    const raw = values[fieldName];
    if (inputType === 'checkbox') {
      payload[fieldName] = Boolean(raw);
    } else if (inputType === 'number') {
      payload[fieldName] = raw === '' ? null : Number(raw);
    } else if (inputType === 'select' && (optionsSource === 'departments' || optionsSource === 'designations')) {
      payload[fieldName] = raw === '' ? null : Number(raw);
    } else if (inputType === 'date') {
      payload[fieldName] = raw === '' ? null : raw;
    } else {
      payload[fieldName] = String(raw ?? '').trim();
    }
  });
  return payload;
}
