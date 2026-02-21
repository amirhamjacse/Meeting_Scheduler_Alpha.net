import axios from "axios";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// ── Attach access token to every request ──────────────────────────────────
api.interceptors.request.use((config) => {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ── Auto-refresh on 401 ───────────────────────────────────────────────────
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((p) => (error ? p.reject(error) : p.resolve(token)));
  failedQueue = [];
};

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            original.headers.Authorization = `Bearer ${token}`;
            return api(original);
          })
          .catch((err) => Promise.reject(err));
      }

      original._retry = true;
      isRefreshing = true;

      const refresh = localStorage.getItem("refresh_token");
      if (!refresh) {
        isRefreshing = false;
        window.location.href = "/login";
        return Promise.reject(error);
      }

      try {
        const { data } = await axios.post(`${BASE_URL}/api/auth/token/refresh/`, {
          refresh,
        });
        localStorage.setItem("access_token", data.access);
        api.defaults.headers.common.Authorization = `Bearer ${data.access}`;
        processQueue(null, data.access);
        original.headers.Authorization = `Bearer ${data.access}`;
        return api(original);
      } catch (err) {
        processQueue(err, null);
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  }
);

// ── Auth ──────────────────────────────────────────────────────────────────
export const authApi = {
  register: (data) => api.post("/api/auth/register/", data),
  login: (data) => api.post("/api/auth/login/", data),
  logout: (refresh) => api.post("/api/auth/logout/", { refresh }),
  me: () => api.get("/api/auth/me/"),
  changePassword: (data) => api.post("/api/auth/change-password/", data),
};

// ── Meetings ──────────────────────────────────────────────────────────────
export const meetingsApi = {
  list: (params) => api.get("/api/meetings/", { params }),
  create: (data) => api.post("/api/meetings/", data),
  get: (id) => api.get(`/api/meetings/${id}/`),
  update: (id, data) => api.patch(`/api/meetings/${id}/`, data),
  delete: (id) => api.delete(`/api/meetings/${id}/`),
  cancel: (id) => api.post(`/api/meetings/${id}/cancel/`),
  exportIcs: (id) =>
    api.get(`/api/meetings/${id}/export-ics/`, { responseType: "blob" }),
  myCalendar: () =>
    api.get("/api/meetings/my-calendar/", { responseType: "blob" }),
  checkConflicts: (data) => api.post("/api/meetings/check-conflicts/", data),
  notify: (id, type) => api.post(`/api/meetings/${id}/notify/`, { type }),
};

// ── Participants ──────────────────────────────────────────────────────────
export const participantsApi = {
  list: (meetingId) => api.get(`/api/meetings/${meetingId}/participants/`),
  add: (meetingId, data) =>
    api.post(`/api/meetings/${meetingId}/participants/`, data),
  remove: (meetingId, participantId) =>
    api.delete(`/api/meetings/${meetingId}/participants/${participantId}/`),
  updateStatus: (meetingId, participantId, status) =>
    api.patch(
      `/api/meetings/${meetingId}/participants/${participantId}/status/`,
      { status }
    ),
};

export default api;

