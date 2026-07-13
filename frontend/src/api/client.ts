import axios, { AxiosError, type AxiosInstance } from 'axios';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

const SESSION_STORAGE_KEY = 'automate.sessionId';

/**
 * A stable per-browser session id so each client gets its own isolated vehicle
 * state on the backend. Persisted in localStorage; regenerated only if missing.
 */
function getSessionId(): string {
  try {
    const existing = localStorage.getItem(SESSION_STORAGE_KEY);
    if (existing) return existing;
    const generated =
      typeof crypto !== 'undefined' && 'randomUUID' in crypto
        ? crypto.randomUUID()
        : `sess-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    localStorage.setItem(SESSION_STORAGE_KEY, generated);
    return generated;
  } catch {
    // localStorage unavailable (e.g. SSR/tests) — fall back to an ephemeral id
    return 'default';
  }
}

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'X-Session-Id': getSessionId(),
  },
  timeout: 30000,
});

export type ApiError = {
  message: string;
  status?: number;
  detail?: unknown;
};

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: unknown }>) => {
    const apiError: ApiError = {
      message: 'An unexpected error occurred.',
      status: error.response?.status,
      detail: error.response?.data?.detail,
    };

    if (error.code === 'ECONNABORTED') {
      apiError.message = 'Request timed out. Please try again.';
    } else if (error.response) {
      const detail = error.response.data?.detail;
      if (typeof detail === 'string') {
        apiError.message = detail;
      } else if (Array.isArray(detail)) {
        apiError.message = detail
          .map((item) =>
            typeof item === 'object' && item !== null && 'msg' in item
              ? String((item as { msg: string }).msg)
              : String(item),
          )
          .join(', ');
      } else {
        apiError.message = `Request failed with status ${error.response.status}.`;
      }
    } else if (error.request) {
      apiError.message = 'Unable to reach the server. Check your connection.';
    } else {
      apiError.message = error.message;
    }

    return Promise.reject(apiError);
  },
);

export async function safeApiCall<T>(
  fn: () => Promise<T>,
  fallback?: T,
): Promise<{ data: T | null; error: ApiError | null }> {
  try {
    const data = await fn();
    return { data, error: null };
  } catch (err) {
    const apiError = err as ApiError;
    return {
      data: fallback ?? null,
      error: {
        message: apiError.message ?? 'An unexpected error occurred.',
        status: apiError.status,
        detail: apiError.detail,
      },
    };
  }
}
