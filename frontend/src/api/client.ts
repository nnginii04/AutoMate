import axios, { AxiosError, type AxiosInstance } from 'axios';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
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
