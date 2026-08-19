import { apiClient } from "./client";

export const hospitalsApi = {
  getHospitals: async () => {
    return apiClient("/hospitals");
  },

  getHospitalById: async (id) => {
    return apiClient(`/hospitals/${id}`);
  },

  getHospitalResources: async (hospitalId) => {
    return apiClient(`/hospitals/${hospitalId}/resources`);
  },

  updateResource: async (hospitalId, resourceId, updateData) => {
    return apiClient(`/hospitals/${hospitalId}/resources/${resourceId}`, {
      method: "PATCH",
      body: JSON.stringify(updateData),
    });
  },

  adjustResource: async (hospitalId, resourceId, delta) => {
    return apiClient(`/hospitals/${hospitalId}/resources/adjust`, {
      method: "POST",
      body: JSON.stringify({ resource_id: resourceId, delta_available: delta }),
    });
  },

  updateResourcesBulk: async (hospitalId, bulkData) => {
    return apiClient(`/hospitals/${hospitalId}/resources`, {
      method: "PATCH",
      body: JSON.stringify(bulkData),
    });
  },
};
