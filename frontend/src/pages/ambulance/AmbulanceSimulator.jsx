import React, { useState, useEffect, useRef } from "react";
import {
  Ambulance,
  MapPin,
  Navigation,
  Play,
  Square,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  ArrowRight,
} from "lucide-react";
import { ambulancesApi } from "../../api/ambulances";
import { referralsApi } from "../../api/referrals";
import { useRealtime } from "../../hooks/useRealtime";
import Loader from "../../components/common/Loader";
import InteractiveTrackingMap from "../../components/map/InteractiveTrackingMap";

export default function AmbulanceSimulator() {
  const [ambulances, setAmbulances] = useState([]);
  const [selectedAmbulanceId, setSelectedAmbulanceId] = useState("");
  const [activeReferral, setActiveReferral] = useState(null);
  const [trail, setTrail] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Auto GPS streaming state
  const [isStreaming, setIsStreaming] = useState(false);
  const streamIntervalRef = useRef(null);

  async function loadData() {
    try {
      setError("");
      const ambList = await ambulancesApi.getAmbulances();
      setAmbulances(Array.isArray(ambList) ? ambList : []);

      if (!selectedAmbulanceId && ambList && ambList.length > 0) {
        // Prefer one with an active referral, else first
        const activeOne = ambList.find((a) => a.active_referral_id) || ambList[0];
        setSelectedAmbulanceId(activeOne.id);
      }
    } catch (err) {
      console.error("Failed to load ambulances for simulator:", err);
      setError(err.message || "Failed to load simulator");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  useRealtime("ambulances", loadData, 3000);

  const currentAmbulance = ambulances.find((a) => a.id === selectedAmbulanceId);

  // Load active referral details & trail for selected ambulance
  useEffect(() => {
    async function loadDetails() {
      if (!currentAmbulance) return;

      if (currentAmbulance.active_referral_id) {
        try {
          const ref = await referralsApi.getReferralById(currentAmbulance.active_referral_id);
          setActiveReferral(ref);
        } catch (err) {
          console.warn("Could not load active referral:", err);
        }
      } else {
        setActiveReferral(null);
      }

      try {
        const trailData = await ambulancesApi.getAmbulanceTrail(currentAmbulance.id, 40);
        setTrail(trailData.trail || []);
      } catch (err) {
        console.warn("Could not load trail:", err);
      }
    }
    loadDetails();
  }, [currentAmbulance?.id, currentAmbulance?.active_referral_id, currentAmbulance?.last_location_update]);

  // Handle manual status transition
  const handleTransitionStatus = async (newStatus) => {
    if (!currentAmbulance) return;
    try {
      setError("");
      await ambulancesApi.updateStatus(currentAmbulance.id, newStatus);
      await loadData();
      setSuccess(`Ambulance status updated to '${newStatus}'.`);
    } catch (err) {
      setError(err.message || "Status transition rejected");
    }
  };

  // Step GPS location toward destination
  const handleStepGPS = async () => {
    if (!currentAmbulance) return;

    try {
      setError("");
      // Target destination coordinates (PHC if en route, Hospital if transporting)
      let targetLat = 19.6967;
      let targetLng = 72.7699;

      if (activeReferral) {
        if (currentAmbulance.status === "TRANSPORTING") {
          targetLat = activeReferral.hospital_latitude || 19.6980;
          targetLng = activeReferral.hospital_longitude || 72.7750;
        } else {
          targetLat = activeReferral.phc_latitude || 19.6967;
          targetLng = activeReferral.phc_longitude || 72.7699;
        }
      }

      // Calculate step towards target with slight jitter
      const dLat = targetLat - currentAmbulance.current_latitude;
      const dLng = targetLng - currentAmbulance.current_longitude;
      const stepFactor = 0.25;

      const newLat = currentAmbulance.current_latitude + dLat * stepFactor + (Math.random() - 0.5) * 0.002;
      const newLng = currentAmbulance.current_longitude + dLng * stepFactor + (Math.random() - 0.5) * 0.002;

      await ambulancesApi.updateLocation(currentAmbulance.id, newLat, newLng, 52.0);
      await loadData();
    } catch (err) {
      setError(err.message || "Failed to update GPS step");
    }
  };

  // Toggle Auto-streaming
  const toggleAutoStream = () => {
    if (isStreaming) {
      clearInterval(streamIntervalRef.current);
      setIsStreaming(false);
    } else {
      setIsStreaming(true);
      streamIntervalRef.current = setInterval(() => {
        handleStepGPS();
      }, 3000);
    }
  };

  useEffect(() => {
    return () => {
      if (streamIntervalRef.current) clearInterval(streamIntervalRef.current);
    };
  }, []);

  if (loading && !ambulances.length) {
    return <Loader text="Loading GPS telemetry simulator..." />;
  }

  return (
    <section className="page">
      <div className="section-head">
        <div>
          <div className="eyebrow">DRIVER & GPS TELEMETRY SIMULATOR</div>
          <h3>Ambulance Live Journey Controller</h3>
          <p>Simulate vehicle journey state transitions and continuous GPS coordinate broadcasts.</p>
        </div>

        <button type="button" className="icon-btn" onClick={loadData} title="Refresh">
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

      <div className="form-layout">
        {/* Left Control Panel */}
        <div className="panel form-panel">
          <div className="panel-title">
            <div>
              <div className="eyebrow">VEHICLE CONTROLS</div>
              <h3>Active Ambulance Unit</h3>
            </div>
          </div>

          <label>
            Select Ambulance Unit
            <select
              value={selectedAmbulanceId}
              onChange={(e) => setSelectedAmbulanceId(e.target.value)}
            >
              {ambulances.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.vehicle_number} ({a.driver_name}) · {a.status}
                </option>
              ))}
            </select>
          </label>

          {currentAmbulance && (
            <div style={{ display: "flex", flexDirection: "column", gap: "16px", marginTop: "14px" }}>
              <div style={{ background: "#f8fafc", padding: "14px", borderRadius: "10px", border: "1px solid var(--line)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
                  <span style={{ fontSize: "12px", color: "#64748b" }}>Current Status:</span>
                  <i className={`status ${currentAmbulance.status}`}>{currentAmbulance.status.replace(/_/g, " ")}</i>
                </div>

                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
                  <span style={{ fontSize: "12px", color: "#64748b" }}>Active Referral:</span>
                  <b>{activeReferral ? `#${activeReferral.referral_number || activeReferral.id.slice(0, 8)} (${activeReferral.patient_name})` : "None"}</b>
                </div>

                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ fontSize: "12px", color: "#64748b" }}>Coordinates:</span>
                  <span style={{ fontSize: "12px", fontFamily: "monospace" }}>
                    {Number(currentAmbulance.current_latitude).toFixed(5)}, {Number(currentAmbulance.current_longitude).toFixed(5)}
                  </span>
                </div>
              </div>

              {/* Lifecycle Transitions */}
              <div>
                <div style={{ fontSize: "12px", fontWeight: "700", color: "#475569", marginBottom: "8px" }}>
                  Step-by-Step Journey Progression:
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
                  <button
                    type="button"
                    className="secondary"
                    onClick={() => handleTransitionStatus("EN_ROUTE_TO_PHC")}
                  >
                    1. En Route to PHC
                  </button>

                  <button
                    type="button"
                    className="secondary"
                    onClick={() => handleTransitionStatus("PATIENT_PICKED_UP")}
                  >
                    2. Patient Picked Up
                  </button>

                  <button
                    type="button"
                    className="secondary"
                    onClick={() => handleTransitionStatus("TRANSPORTING")}
                  >
                    3. Transporting to Hosp
                  </button>

                  <button
                    type="button"
                    className="secondary"
                    onClick={() => handleTransitionStatus("ARRIVED")}
                  >
                    4. Arrived at Hospital
                  </button>
                </div>

                <button
                  type="button"
                  className="primary full"
                  onClick={() => handleTransitionStatus("AVAILABLE")}
                  style={{ marginTop: "10px", background: "#16a34a" }}
                >
                  5. Complete Run & Return Available
                </button>
              </div>

              {/* GPS Stream Controls */}
              <div style={{ borderTop: "1px solid var(--line)", paddingTop: "16px" }}>
                <div style={{ fontSize: "12px", fontWeight: "700", color: "#475569", marginBottom: "8px" }}>
                  GPS Telemetry Stream:
                </div>

                <div style={{ display: "flex", gap: "10px" }}>
                  <button
                    type="button"
                    className="secondary"
                    style={{ flex: 1 }}
                    onClick={handleStepGPS}
                  >
                    <Navigation size={15} />
                    Step Next Ping
                  </button>

                  <button
                    type="button"
                    className="primary"
                    style={{ flex: 1, background: isStreaming ? "#dc2626" : "#2563eb" }}
                    onClick={toggleAutoStream}
                  >
                    {isStreaming ? <Square size={15} /> : <Play size={15} />}
                    {isStreaming ? "Stop Stream" : "Auto Broadcast (3s)"}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Map Preview */}
        <div className="panel" style={{ padding: "18px" }}>
          <div className="panel-title" style={{ marginBottom: "14px" }}>
            <div>
              <div className="eyebrow">LIVE TELEMETRY CANVAS</div>
              <h3>Real-Time Geospatial Visualizer</h3>
            </div>
          </div>

          <InteractiveTrackingMap
            phcLocation={{
              latitude: activeReferral?.phc_latitude || 19.6967,
              longitude: activeReferral?.phc_longitude || 72.7699,
              name: activeReferral?.phc_name || "Palghar Rural Health Centre",
            }}
            hospitalLocation={{
              latitude: activeReferral?.hospital_latitude || 19.6980,
              longitude: activeReferral?.hospital_longitude || 72.7750,
              name: activeReferral?.hospital_name || "Sahyadri District Care Hospital",
            }}
            ambulanceLocation={
              currentAmbulance
                ? {
                    latitude: currentAmbulance.current_latitude,
                    longitude: currentAmbulance.current_longitude,
                    vehicle_number: currentAmbulance.vehicle_number,
                    status: currentAmbulance.status,
                  }
                : null
            }
            trail={trail}
            height="440px"
          />
        </div>
      </div>
    </section>
  );
}
