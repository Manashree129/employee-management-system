// Single place that talks to the backend. Every API call goes through request().
const BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(/\/+$/, '');

export class ApiError extends Error {
  constructor(message, { status = 0, code = 'ERROR', errors = {} } = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.errors = errors; // { fieldName: [messages] } from the backend
  }
}

function buildUrl(path, params) {
  const url = new URL(BASE_URL + path);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== '' && value !== null && value !== undefined) {
        url.searchParams.set(key, String(value));
      }
    });
  }
  return url.toString();
}

/** Returns `data` from the backend envelope, or throws ApiError. */
export async function request(path, { method = 'GET', body, params, signal } = {}) {
  let response;
  try {
    response = await fetch(buildUrl(path, params), {
      method,
      signal,
      headers: body !== undefined ? { 'Content-Type': 'application/json' } : undefined,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch (err) {
    if (err.name === 'AbortError') throw err;
    throw new ApiError(
      'Cannot reach the server. Check that the backend is running and VITE_API_BASE_URL is correct.',
      { code: 'NETWORK_ERROR' },
    );
  }

  let payload = null;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok || !payload || payload.success === false) {
    throw new ApiError(payload?.message || `Request failed with status ${response.status}.`, {
      status: response.status,
      code: payload?.code || 'ERROR',
      errors: payload?.errors || {},
    });
  }
  return payload.data;
}

/** Downloads a file (e.g. CSV). Returns a Blob or throws ApiError. */
export async function requestFile(path, { params, signal } = {}) {
  let response;

  try {
    response = await fetch(buildUrl(path, params), { signal });
  } catch (err) {
    if (err.name === 'AbortError') throw err;

    throw new ApiError(
      'Cannot reach the server. Check that the backend is running and VITE_API_BASE_URL is correct.',
      { code: 'NETWORK_ERROR' },
    );
  }

  if (!response.ok) {
    let payload = null;

    try {
      payload = await response.json();
    } catch {
      payload = null;
    }

    throw new ApiError(
      payload?.message || `Export failed with status ${response.status}.`,
      {
        status: response.status,
        code: payload?.code || 'ERROR',
        errors: payload?.errors || {},
      },
    );
  }

  return response.blob();
}

