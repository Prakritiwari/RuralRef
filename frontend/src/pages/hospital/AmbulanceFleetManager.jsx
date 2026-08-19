import React, { useState, useEffect } from "react";
import {
  AlertCircle,
  Ambulance,
  CheckCircle2,
  MapPin,
  Navigation,
  Phone,
  RefreshCw,
  UserRound,
} from "lucide-react";
import { ambulancesApi } from "../../api/ambulances";
import { useRealtime } from "../../hooks/useRealtime";
import Loader from "../../components/common/Loader";

export default function AmbulanceFleetManager() {
  const [ambulances, setAmbulances] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function loadAmbulances() {
    try {
      setError("");
      const result = await ambulancesApi.getAmbulances();
      setAmbulances(Array.isArray(result) ? result : []);
    } catch (err) {
      console.error("Failed to load ambulances:", err);
      setError(err.message || "Failed to load ambulance fleet");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAmbulances();
  }, []);

  useRealtime("ambulances", loadAmbulances, 3000);

  const handleSimulateGPS = async (amb) => {
    try {
      setError("");
      // Add slight progressive GPS offset
      const newLat = amb.current_latitude + (Math.random() - 0.48) * 0.008;
      const newLng = amb.current_longitude + (Math.random() - 0.48) * 0.008;

      await ambulancesApi.updateLocation(amb.id, newLat, newLng, 45.0);
      await loadAmbulances();
      setSuccess(`GPS coordinate broadcasted for ${amb.vehicle_number}`);
    } catch (err) {
      setError(err.message || "Failed to update GPS location");
    }
  };

  const handleCompleteTrip = async (ambId) => {
    try {
      setError("");
      await ambulancesApi.completeTrip(ambId);
      await loadAmbulances();
      setSuccess("Ambulance transport marked completed and vehicle returned to available pool.");
    } catch (err) {
      setError(err.message || "Failed to complete trip");
    }
  };

  return (
    <section className="page">
      <div className="section-head">
        <div>
          <div className="eyebrow">EMERGENCY LOGISTICS FLEET</div>
          <h3>Ambulance Fleet & GPS Telemetry</h3>
          <p>Monitor real-time positioning, driver assignments, and active transport transfers.</p>
        </div>

        <button type="button" className="icon-btn" onClick={loadAmbulances} title="Refresh">
          <RefreshCw size={17} className={loading ? "spin" : ""} />
        </button>
      </div>

      {error && (
        <div className="error page-error" style={{ marginBottom: "16px" }}>
          <AlertCircle size={15} />
          {error}
        </div>
      )}

      {success && (
        <div className="success page-success" style={{ marginBottom: "16px" }}>
          <CheckCircle2 size={15} />
          {success}
        </div>
      )}

      <div className="info-banner" style={{ marginBottom: "24px" }}>
        <MapPin size={22} />
        <div>
          <b>Live GPS Telemetry Active</b>
          <span>
            Ambulances push live coordinates every few seconds during active emergency runs.
            You can also simulate position updates below to test the full real-time flow without physical GPS hardware.
          </span>
        </div>
      </div>

      {loading && !ambulances.length ? (
        <Loader text="Loading ambulance fleet..." />
      ) : (
        <div className="ambulance-grid">
          {ambulances.map((ambulance) => {
            const hasActiveTrip = !!ambulance.active_referral_id;

            return (
              <div className="amb-card" key={ambulance.id}>
                <div className="amb-top">
                  <div className="amb-icon">
                    <Ambulance size={23} />
                  </div>

                  <div>
                    <b>{ambulance.vehicle_number}</b>
                    <small>
                      {ambulance.driver_name} · {ambulance.driver_phone}
                    </small>
                  </div>

                  <i className={`status ${ambulance.status}`}>
                    {ambulance.status.replace(/_/g, " ")}
                  </i>
                </div>

                <div className="coords">
                  <Navigation size={15} />
                  <span>
                    Lat: {Number(ambulance.current_latitude).toFixed(5)}, Lng: {Number(ambulance.current_longitude).toFixed(5)}
                  </span>
                </div>

                <div className="tracking-label">
                  <span>Hospital Base</span>
                  <b>{ambulance.hospital_name || "Assigned Base"}</b>
                </div>

                {hasActiveTrip ? (
                  <div className="tracking-label" style={{ background: "#eff6ff", padding: "6px 10px", borderRadius: "6px" }}>
                    <span style={{ color: "#2563eb" }}>Active Referral</span>
                    <b style={{ color: "#1e40af" }}>#{ambulance.active_referral_id.slice(0, 8)}</b>
                  </div>
                ) : (
                  <div className="tracking-label">
                    <span>Readiness</span>
                    <b style={{ color: "#16a34a" }}>Available on Station</b>
                  </div>
                )}

                <div className="amb-actions" style={{ display: "flex", gap: "8px", flexDirection: "column" }}>
                  {hasActiveTrip ? (
                    <>
                      <button
                        type="button"
                        className="secondary full-secondary"
                        onClick={() => handleSimulateGPS(ambulance)}
                      >
                        <MapPin size={15} />
                        Simulate Next GPS Ping
                      </button>

                      {ambulance.status === "ARRIVED" && (
                        <button
                          type="button"
                          className="primary full"
                          onClick={() => handleCompleteTrip(ambulance.id)}
                          style={{ background: "#16a34a" }}
                        >
                          Complete Transfer & Release
                        </button>
                      )}
                    </>
                  ) : (
                    <span className="muted" style={{ textAlign: "center", display: "block" }}>
                      Ready for assignment
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
