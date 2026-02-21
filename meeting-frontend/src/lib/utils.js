import { format, formatDistanceToNow, isToday, isTomorrow, isPast } from "date-fns";

export function formatDateTime(dateStr) {
  if (!dateStr) return "—";
  return format(new Date(dateStr), "MMM d, yyyy • h:mm a");
}

export function formatDate(dateStr) {
  if (!dateStr) return "—";
  return format(new Date(dateStr), "MMM d, yyyy");
}

export function formatTime(dateStr) {
  if (!dateStr) return "—";
  return format(new Date(dateStr), "h:mm a");
}

export function formatRelative(dateStr) {
  if (!dateStr) return "—";
  return formatDistanceToNow(new Date(dateStr), { addSuffix: true });
}

export function getMeetingDayLabel(dateStr) {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  if (isToday(d)) return "Today";
  if (isTomorrow(d)) return "Tomorrow";
  return format(d, "EEEE, MMM d");
}

export function toLocalInputValue(dateStr) {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  return format(d, "yyyy-MM-dd'T'HH:mm");
}

export function getMeetingStatusColor(status) {
  switch (status) {
    case "scheduled": return "bg-emerald-100 text-emerald-700";
    case "cancelled": return "bg-red-100 text-red-700";
    case "completed": return "bg-gray-100 text-gray-600";
    default: return "bg-gray-100 text-gray-600";
  }
}

export function getParticipantStatusColor(status) {
  switch (status) {
    case "accepted": return "bg-emerald-100 text-emerald-700";
    case "declined": return "bg-red-100 text-red-700";
    case "tentative": return "bg-yellow-100 text-yellow-700";
    default: return "bg-blue-100 text-blue-600";
  }
}

export function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(url);
}

export function extractErrorMessage(error) {
  const data = error?.response?.data;
  if (!data) return error?.message || "An unexpected error occurred.";
  if (typeof data === "string") return data;
  if (data.detail) return data.detail;
  const messages = Object.entries(data)
    .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`)
    .join(" | ");
  return messages || "An unexpected error occurred.";
}
