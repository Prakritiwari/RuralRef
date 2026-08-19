import { apiClient } from "./client";

export const referralsApi = {
  createReferral: async (referralData) => {
    return apiClient("/referrals", {
      method: "POST",
      body: JSON.stringify(referralData),
    });
  },

  getReferrals: async (statusFilter = null) => {
    const query = statusFilter ? `?status=${encodeURIComponent(statusFilter)}` : "";
    return apiClient(`/referrals${query}`);
  },

  getReferralById: async (id) => {
    return apiClient(`/referrals/${id}`);
  },

  getRecommendations: async (referralId) => {
    return apiClient(`/referrals/${referralId}/recommendations`);
  },

  sendReferral: async (referralId, hospitalId) => {
    return apiClient(`/referrals/${referralId}/send?hospital_id=${hospitalId}`, {
      method: "POST",
      body: JSON.stringify({ hospital_id: hospitalId }),
    });
  },

  acceptReferral: async (referralId) => {
    return apiClient(`/referrals/${referralId}/accept`, {
      method: "POST",
    });
  },

  rejectReferral: async (referralId, reason = "Insufficient resource capacity") => {
    return apiClient(`/referrals/${referralId}/reject`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    });
  },

  cancelReferral: async (referralId, reason = "Cancelled by PHC") => {
    return apiClient(`/referrals/${referralId}/cancel`, {
      method: "POST",
    });
  },

  allocateAmbulance: async (referralId) => {
    return apiClient(`/referrals/${referralId}/ambulance`, {
      method: "POST",
    });
  },
};
