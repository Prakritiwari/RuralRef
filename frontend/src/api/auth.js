import { apiClient } from "./client";

export const authApi = {
  login: async (email, password) => {
    return apiClient("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },

  register: async (userData) => {
    return apiClient("/auth/register", {
      method: "POST",
      body: JSON.stringify(userData),
    });
  },

  getMe: async () => {
    return apiClient("/auth/me");
  },
};
