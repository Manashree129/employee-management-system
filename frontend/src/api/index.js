import { request, requestFile } from './http';

export const EMPLOYEE_FORM = 'employee';

export const dashboardApi = {
  summary: (signal) => request('/dashboard/summary', { signal }),
};

export const employeeApi = {
  list: (params, signal) => request('/employees', { params, signal }),
  get: (id, signal) => request(`/employees/${id}`, { signal }),
  create: (body) => request('/employees', { method: 'POST', body }),
  update: (id, body) => request(`/employees/${id}`, { method: 'PUT', body }),
  remove: (id) => request(`/employees/${id}`, { method: 'DELETE' }),
  exportCsv: (params, signal) =>
    requestFile('/employees/export', { params, signal }),
};

export const departmentApi = {
  list: (params, signal) => request('/departments', { params, signal }),
  create: (body) => request('/departments', { method: 'POST', body }),
  update: (id, body) => request(`/departments/${id}`, { method: 'PUT', body }),
  remove: (id) => request(`/departments/${id}`, { method: 'DELETE' }),
  designations: (id, signal) => request(`/departments/${id}/designations`, { signal }),
};

export const lookupApi = {
  get: (category, signal) => request(`/lookups/${encodeURIComponent(category)}`, { signal }),
};

export const formConfigApi = {
  get: (formName, signal) => request(`/form-config/${encodeURIComponent(formName)}`, { signal }),
};
