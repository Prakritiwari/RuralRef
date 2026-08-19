import { apiClient } from "./client";

export const dashboardApi = {
  getDashboard: async () => {
    return apiClient("/dashboard");
  },
};
