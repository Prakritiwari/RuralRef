import { apiClient } from "./client";

export const resourcesApi = {
  getCatalog: async () => {
    return apiClient("/resources/catalog");
  },
};
