/**
 * Centralized HTTP Client for RuralRefLink
 */
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export async function apiClient(endpoint, options = {}) {
  const token = localStorage.getItem("token");

  const headers = {
    ...(options.body && !(options.body instanceof FormData)
      ? { "Content-Type": "application/json" }
      : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  const url = endpoint.startsWith("http") ? endpoint : `${API_BASE}${endpoint.startsWith("/") ? "" : "/"}${endpoint}`;

  let response;
  try {
    response = await fetch(url, {
      ...options,
      headers,
    });
  } catch (err) {
    throw new Error(
      "Cannot connect to the backend server. Please verify FastAPI is running on port 8000."
    );
  }

  // Parse response
  let data = {};
  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    data = await response.json().catch(() => ({}));
  }

  if (!response.ok) {
    const errorMsg =
      data.detail ||
      data.message ||
      `Request failed with status code ${response.status}`;
    const error = new Error(errorMsg);
    error.status = response.status;
    error.data = data;
    throw error;
  }

  return data;
}
