import { apiClient } from "./client";

export const ambulancesApi = {
  getAmbulances: async (statusFilter = null) => {
    const query = statusFilter ? `?status_filter=${encodeURIComponent(statusFilter)}` : "";
    return apiClient(`/ambulances${query}`);
  },

  getAmbulanceById: async (id) => {
    return apiClient(`/ambulances/${id}`);
  },

  assignAmbulance: async (ambulanceId, referralId) => {
    return apiClient(`/ambulances/${ambulanceId}/assign`, {
      method: "POST",
      body: JSON.stringify({ referral_id: referralId }),
    });
  },

  updateStatus: async (ambulanceId, status, notes = "") => {
    return apiClient(`/ambulances/${ambulanceId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status, notes }),
    });
  },

  updateLocation: async (ambulanceId, latitude, longitude, speed = 40.0, heading = 0.0) => {
    return apiClient(`/ambulances/${ambulanceId}/location`, {
      method: "POST",
      body: JSON.stringify({ latitude, longitude, speed, heading }),
    });
  },

  completeTrip: async (ambulanceId) => {
    return apiClient(`/ambulances/${ambulanceId}/complete`, {
      method: "POST",
    });
  },

  getAmbulanceTrail: async (ambulanceId, limit = 50) => {
    return apiClient(`/tracking/ambulance/${ambulanceId}/trail?limit=${limit}`);
  },
};
