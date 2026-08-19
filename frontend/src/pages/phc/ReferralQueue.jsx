import React, { useState, useEffect } from "react";
import {
  AlertCircle,
  Ambulance,
  CheckCircle2,
  Clock3,
  Database,
  MapPin,
  Navigation,
  RefreshCw,
  XCircle,
  Eye,
  EyeOff,
} from "lucide-react";
import { referralsApi } from "../../api/referrals";
import { useAuth } from "../../context/AuthContext";
import { useRealtime } from "../../hooks/useRealtime";
import Loader from "../../components/common/Loader";
import InteractiveTrackingMap from "../../components/map/InteractiveTrackingMap";

export default function ReferralQueue() {
  const { isHospital, isPHC, isAdmin } = useAuth();
  const [referrals, setReferrals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTrackingId, setActiveTrackingId] = useState(null);
  const [filter, setFilter] = useState("ALL");

  async function loadReferrals() {
    try {
      setError("");
      const result = await referralsApi.getReferrals();
      setReferrals(Array.isArray(result) ? result : []);
    } catch (err) {
      console.error("Failed to load referrals:", err);
      setError(err.message || "Failed to load referrals");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadReferrals();
  }, []);

  // Realtime synchronization
  useRealtime("referrals", loadReferrals, 3000);
  useRealtime("ambulances", loadReferrals, 3000);

  async function handleAccept(id) {
    try {
      setError("");
      await referralsApi.acceptReferral(id);
      await loadReferrals();
    } catch (err) {
      setError(err.message || "Failed to accept referral");
    }
  }

  async function handleReject(id) {
    try {
      setError("");
      await referralsApi.rejectReferral(id, "Hospital beds / ventilators currently occupied");
      await loadReferrals();
    } catch (err) {
      setError(err.message || "Failed to reject referral");
    }
  }

  async function handleAllocateAmbulance(id) {
    try {
      setError("");
      await referralsApi.allocateAmbulance(id);
      await loadReferrals();
    } catch (err) {
      setError(err.message || "Failed to allocate ambulance");
    }
  }

  async function handleCancel(id) {
    if (!window.confirm("Are you sure you want to cancel this referral? Any reserved capacity will be released.")) {
      return;
    }
    try {
      setError("");
      await referralsApi.cancelReferral(id);
      await loadReferrals();
    } catch (err) {
      setError(err.message || "Failed to cancel referral");
    }
  }

  const filteredReferrals = referrals.filter((r) => {
    if (filter === "ALL") return true;
    if (filter === "PENDING") return r.status === "PENDING";
    if (filter === "ACCEPTED") return r.status === "ACCEPTED" || r.status === "AMBULANCE_ASSIGNED";
    if (filter === "TRANSIT") return r.status === "AMBULANCE_EN_ROUTE" || r.status === "PATIENT_PICKED_UP" || r.status === "PATIENT_IN_TRANSIT";
    if (filter === "COMPLETED") return r.status === "ARRIVED" || r.status === "COMPLETED";
    return true;
  });

  return (
    <section className="page">
      <div className="section-head">
        <div>
          <div className="eyebrow">OPERATIONS QUEUE</div>
          <h3>Emergency Referral Stream</h3>
          <p>Review incoming requests, manage atomic bed reservations, and dispatch emergency transport.</p>
        </div>

        <button type="button" className="icon-btn" onClick={loadReferrals} title="Refresh">
          <RefreshCw size={17} className={loading ? "spin" : ""} />
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="tabs" style={{ marginBottom: "20px", maxWidth: "600px" }}>
        {["ALL", "PENDING", "ACCEPTED", "TRANSIT", "COMPLETED"].map((f) => (
          <button
            type="button"
            key={f}
            className={filter === f ? "active" : ""}
            onClick={() => setFilter(f)}
          >
            {f === "ALL" ? "All Cases" : f.charAt(0) + f.slice(1).toLowerCase()}
          </button>
        ))}
      </div>

      {error && (
        <div className="error page-error" style={{ marginBottom: "20px" }}>
          <AlertCircle size={15} />
          {error}
        </div>
      )}

      {loading && !referrals.length ? (
        <Loader text="Loading live referral stream..." />
      ) : filteredReferrals.length === 0 ? (
        <div className="empty big-empty">
          <Database size={35} />
          <b>No referrals in this view</b>
          <span>Referral records will appear here as they are triaged.</span>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {filteredReferrals.map((referral) => {
            const hasAmbulance = !!referral.ambulance;
            const isTracking = activeTrackingId === referral.id;

            return (
              <div
                key={referral.id}
                style={{
                  background: "#ffffff",
                  border: "1px solid var(--line)",
                  borderRadius: "12px",
                  padding: "20px",
                  boxShadow: "var(--shadow)",
                  display: "flex",
                  flexDirection: "column",
                  gap: "14px",
                }}
              >
                {/* Header row */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "10px" }}>
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                      <b style={{ fontSize: "16px" }}>{referral.patient_name}</b>
                      <span style={{ fontSize: "12px", color: "#64748b" }}>
                        #{referral.referral_number || referral.id.slice(0, 8)}
                      </span>
                      <i className={`urg ${referral.urgency?.toLowerCase()}`}>
                        {referral.urgency}
                      </i>
                    </div>

                    <div style={{ fontSize: "13px", color: "#475569", marginTop: "4px" }}>
                      Origin: <b>{referral.phc_name}</b> → Destination:{" "}
                      <b>{referral.hospital_name || "Awaiting Selection"}</b>
                    </div>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    <i className={`status ${referral.status}`}>
                      {String(referral.status || "").replace(/_/g, " ")}
                    </i>

                    {referral.status !== "COMPLETED" && referral.status !== "CANCELLED" && referral.status !== "REJECTED" && (
                      <button
                        type="button"
                        className="secondary"
                        style={{ padding: "6px 10px", fontSize: "11.5px" }}
                        onClick={() => setActiveTrackingId(isTracking ? null : referral.id)}
                      >
                        {isTracking ? <EyeOff size={14} /> : <Eye size={14} />}
                        {isTracking ? "Hide Map" : "Live Map"}
                      </button>
                    )}
                  </div>
                </div>

                {/* Clinical summary & requirements */}
                <div style={{ background: "#f8fafc", padding: "10px 14px", borderRadius: "8px", fontSize: "12.5px" }}>
                  <span style={{ color: "#64748b", fontWeight: "600" }}>Clinical Summary: </span>
                  <span>{referral.clinical_summary}</span>

                  {referral.requirements && referral.requirements.length > 0 && (
                    <div style={{ marginTop: "6px", display: "flex", gap: "8px", flexWrap: "wrap" }}>
                      <span style={{ color: "#64748b", fontWeight: "600", fontSize: "12px" }}>Demanded:</span>
                      {referral.requirements.map((req, i) => (
                        <span
                          key={i}
                          style={{
                            background: "#e2e8f0",
                            color: "#1e293b",
                            padding: "2px 8px",
                            borderRadius: "4px",
                            fontSize: "11px",
                            fontWeight: "600",
                          }}
                        >
                          {req.resource_name || req.resource_id} (×{req.quantity})
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Actions & Ambulance footer */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid var(--line)", paddingTop: "12px", flexWrap: "wrap", gap: "10px" }}>
                  <div>
                    {referral.ambulance ? (
                      <div style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "12.5px", color: "#1e40af" }}>
                        <Ambulance size={17} />
                        <b>{referral.ambulance.vehicle_number}</b>
                        <span style={{ color: "#64748b" }}>· Driver: {referral.ambulance.driver_name} ({referral.ambulance.driver_phone})</span>
                        <span style={{ background: "#dbeafe", padding: "2px 6px", borderRadius: "4px", fontSize: "11px", fontWeight: "700" }}>
                          {referral.ambulance.status.replace(/_/g, " ")}
                        </span>
                      </div>
                    ) : (
                      <span style={{ fontSize: "12px", color: "#94a3b8" }}>No ambulance currently assigned</span>
                    )}
                  </div>

                  <div className="actions" style={{ display: "flex", gap: "8px" }}>
                    {/* Hospital Actions */}
                    {(isHospital || isAdmin) && referral.status === "PENDING" && (
                      <>
                        <button
                          type="button"
                          className="primary"
                          style={{ padding: "7px 14px", fontSize: "12px", background: "#16a34a" }}
                          onClick={() => handleAccept(referral.id)}
                        >
                          <CheckCircle2 size={15} />
                          Accept & Reserve Resources
                        </button>
                        <button
                          type="button"
                          className="secondary"
                          style={{ padding: "7px 14px", fontSize: "12px", color: "#dc2626" }}
                          onClick={() => handleReject(referral.id)}
                        >
                          <XCircle size={15} />
                          Reject
                        </button>
                      </>
                    )}

                    {(isHospital || isAdmin) && referral.status === "ACCEPTED" && (
                      <button
                        type="button"
                        className="primary"
                        style={{ padding: "7px 14px", fontSize: "12px" }}
                        onClick={() => handleAllocateAmbulance(referral.id)}
                      >
                        <Ambulance size={15} />
                        Allocate Hospital Ambulance
                      </button>
                    )}

                    {/* PHC Actions */}
                    {(isPHC || isAdmin) && referral.status === "PENDING" && (
                      <button
                        type="button"
                        className="secondary"
                        style={{ padding: "7px 14px", fontSize: "12px", color: "#dc2626" }}
                        onClick={() => handleCancel(referral.id)}
                      >
                        Cancel
                      </button>
                    )}
                  </div>
                </div>

                {/* Embedded Interactive Map on Expand */}
                {isTracking && (
                  <div style={{ marginTop: "8px" }}>
                    <div style={{ marginBottom: "8px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                      <span style={{ fontSize: "12px", fontWeight: "700", color: "#334155" }}>
                        📍 Live GPS Route & Transport Map
                      </span>
                      <span style={{ fontSize: "11px", color: "#64748b" }}>
                        Auto-updates via telemetry stream
                      </span>
                    </div>

                    <InteractiveTrackingMap
                      phcLocation={{
                        latitude: referral.phc_latitude || 19.6967,
                        longitude: referral.phc_longitude || 72.7699,
                        name: referral.phc_name,
                      }}
                      hospitalLocation={{
                        latitude: referral.hospital_latitude || 19.6980,
                        longitude: referral.hospital_longitude || 72.7750,
                        name: referral.hospital_name,
                      }}
                      ambulanceLocation={
                        referral.ambulance
                          ? {
                              latitude: referral.ambulance.current_latitude,
                              longitude: referral.ambulance.current_longitude,
                              vehicle_number: referral.ambulance.vehicle_number,
                              status: referral.ambulance.status,
                            }
                          : null
                      }
                      height="300px"
                    />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
