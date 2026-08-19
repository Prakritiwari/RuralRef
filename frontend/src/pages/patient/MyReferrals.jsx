import React, { useState, useEffect } from "react";
import { AlertCircle, HeartPulse, RefreshCw, Ambulance, MapPin } from "lucide-react";
import { referralsApi } from "../../api/referrals";
import { useRealtime } from "../../hooks/useRealtime";
import Loader from "../../components/common/Loader";
import InteractiveTrackingMap from "../../components/map/InteractiveTrackingMap";

export default function MyReferrals() {
  const [referrals, setReferrals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadReferrals() {
    try {
      setError("");
      const result = await referralsApi.getReferrals();
      setReferrals(Array.isArray(result) ? result : []);
    } catch (err) {
      console.error("Failed to load patient referrals:", err);
      setError(err.message || "Failed to load your referrals");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadReferrals();
  }, []);

  useRealtime("referrals", loadReferrals, 3000);
  useRealtime("ambulances", loadReferrals, 3000);

  if (loading && !referrals.length) {
    return <Loader text="Loading your emergency referral journey..." />;
  }

  return (
    <section className="page">
      <div className="welcome">
        <div>
          <div className="eyebrow">PATIENT EMERGENCY PORTAL</div>
          <h2>Your Care & Transfer Journey</h2>
          <p>Track your medical referral status, destination hospital readiness, and approaching ambulance transport.</p>
        </div>

        <button type="button" className="icon-btn" onClick={loadReferrals} title="Refresh">
          <RefreshCw size={17} className={loading ? "spin" : ""} />
        </button>
      </div>

      {error && (
        <div className="error page-error" style={{ marginBottom: "16px" }}>
          <AlertCircle size={15} />
          {error}
        </div>
      )}

      <div className="timeline">
        {referrals.map((referral) => {
          const hasAmbulance = !!referral.ambulance;
          const isInTransit =
            referral.status === "AMBULANCE_EN_ROUTE" ||
            referral.status === "PATIENT_PICKED_UP" ||
            referral.status === "PATIENT_IN_TRANSIT";

          return (
            <div className="timeline-card" key={referral.id} style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              <div style={{ display: "flex", gap: "14px", alignItems: "flex-start" }}>
                <div className="tl-icon">
                  <HeartPulse size={19} />
                </div>

                <div className="timeline-content" style={{ flex: 1 }}>
                  <b>Referral #{referral.referral_number || referral.id.slice(0, 8)}</b>
                  <span>
                    Destination: <b>{referral.hospital_name || "Coordinating with district facilities..."}</b>
                  </span>

                  <div style={{ margin: "6px 0" }}>
                    <i className={`status ${referral.status}`}>
                      {String(referral.status || "").replace(/_/g, " ")}
                    </i>
                  </div>

                  {referral.ambulance && (
                    <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#2563eb", fontSize: "12px", marginTop: "4px" }}>
                      <Ambulance size={15} />
                      <span>
                        Assigned Vehicle: <b>{referral.ambulance.vehicle_number}</b> (Driver: {referral.ambulance.driver_name})
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Show Live Map to patient when vehicle is en route */}
              {hasAmbulance && isInTransit && (
                <div style={{ borderTop: "1px solid var(--line)", paddingTop: "12px" }}>
                  <div style={{ fontSize: "12px", fontWeight: "700", marginBottom: "8px", color: "#334155" }}>
                    🚑 Live Ambulance Position
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
                    ambulanceLocation={{
                      latitude: referral.ambulance.current_latitude,
                      longitude: referral.ambulance.current_longitude,
                      vehicle_number: referral.ambulance.vehicle_number,
                      status: referral.ambulance.status,
                    }}
                    height="240px"
                  />
                </div>
              )}
            </div>
          );
        })}

        {!referrals.length && (
          <div className="empty big-empty">
            <HeartPulse size={35} />
            <b>No active referrals found</b>
            <span>Emergency referral journeys initiated by your Primary Health Centre will appear here.</span>
          </div>
        )}
      </div>
    </section>
  );
}
