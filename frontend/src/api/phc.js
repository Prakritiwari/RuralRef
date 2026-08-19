import { apiClient } from "./client";

export const phcApi = {
  getPHCs: async () => {
    return apiClient("/phcs");
  },

  getMyPHC: async () => {
    return apiClient("/phcs/me");
  },

  getPHCById: async (id) => {
    return apiClient(`/phcs/${id}`);
  },

  getPatients: async () => {
    return apiClient("/patients");
  },

  createPatient: async (patientData) => {
    return apiClient("/patients", {
      method: "POST",
      body: JSON.stringify(patientData),
    });
  },
};
