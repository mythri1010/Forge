import axios from "axios";

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "/api";

export const api = axios.create({ baseURL: BASE });

// Attach JWT from localStorage on every request
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const raw = localStorage.getItem("auth");
    if (raw) {
      try {
        const { access_token } = JSON.parse(raw);
        if (access_token) {
          config.headers.Authorization = `Bearer ${access_token}`;
        }
      } catch {
        // malformed — ignore
      }
    }
  }
  return config;
});

// On 401, clear auth and redirect to login
api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("auth");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

// ── typed helpers ─────────────────────────────────────────────────────────────

export function getErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    return (
      err.response?.data?.error ??
      err.response?.data?.message ??
      err.message
    );
  }
  return String(err);
}
