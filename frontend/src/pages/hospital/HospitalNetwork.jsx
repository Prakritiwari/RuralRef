import React, { useState, useEffect } from "react";
import { AlertCircle, Building2, Hospital, RefreshCw } from "lucide-react";
import { hospitalsApi } from "../../api/hospitals";
import { useRealtime } from "../../hooks/useRealtime";
import Loader from "../../components/common/Loader";

export default function HospitalNetwork() {
  const [hospitals, setHospitals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadHospitals() {
    try {
      setError("");
      const result = await hospitalsApi.getHospitals();
      setHospitals(Array.isArray(result) ? result : []);
    } catch (err) {
      console.error("Failed to load hospital network:", err);
      setError(err.message || "Failed to load hospital network");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadHospitals();
  }, []);

  useRealtime("hospital_resources", loadHospitals, 4000);

  if (loading && !hospitals.length) {
    return <Loader text="Loading regional hospital network..." />;
  }

  return (
    <section className="page">
      <div className="section-head">
        <div>
          <div className="eyebrow">DISTRICT & TERTIARY NETWORK</div>
          <h3>Hospital Resource & Capacity Network</h3>
          <p>Real-time visibility across participating public and tertiary medical facilities.</p>
        </div>

        <button type="button" className="icon-btn" onClick={loadHospitals} title="Refresh">
          <RefreshCw size={17} className={loading ? "spin" : ""} />
        </button>
      </div>

      {error && (
        <div className="error page-error" style={{ marginBottom: "16px" }}>
          <AlertCircle size={15} />
          {error}
        </div>
      )}

      <div className="hospital-grid">
        {hospitals.map((hospital) => {
          const invMap = {};
          (hospital.resources || []).forEach((r) => {
            invMap[r.resource_id] = r.available_quantity;
          });

          return (
            <div className="capacity large" key={hospital.id}>
              <div className="cap-top">
                <div className="hospital-mark">
                  <Hospital size={20} />
                </div>

                <div className="hospital-name">
                  <b>{hospital.name}</b>
                  <small>
                    {hospital.level} · {hospital.district}
                  </small>
                </div>

                <span className="online-dot">
                  {hospital.emergency_available ? "LIVE" : "LIMITED"}
                </span>
              </div>

              <div className="resources">
                <div>
                  <span>ICU</span>
                  <b style={{ color: (invMap.ICU || 0) > 0 ? "#16a34a" : "#dc2626" }}>
                    {invMap.ICU ?? 0}
                  </b>
                </div>
                <div>
                  <span>O₂</span>
                  <b style={{ color: (invMap.OXYGEN || 0) > 0 ? "#2563eb" : "#dc2626" }}>
                    {invMap.OXYGEN ?? 0}
                  </b>
                </div>
                <div>
                  <span>Ventilators</span>
                  <b style={{ color: (invMap.VENTILATOR || 0) > 0 ? "#16a34a" : "#dc2626" }}>
                    {invMap.VENTILATOR ?? 0}
                  </b>
                </div>
              </div>

              <div className="specialists" style={{ marginTop: "14px" }}>
                <span>Available Resources & Specialties</span>
                <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginTop: "6px" }}>
                  {(hospital.resources || [])
                    .filter((r) => r.available_quantity > 0)
                    .slice(0, 5)
                    .map((r) => (
                      <i key={r.id}>
                        {r.resource_name || r.resource_id} ({r.available_quantity})
                      </i>
                    ))}
                </div>
              </div>

              <div style={{ marginTop: "12px", borderTop: "1px solid var(--line)", paddingTop: "10px", display: "flex", justifyContent: "space-between", fontSize: "11.5px", color: "#64748b" }}>
                <span>Phone: {hospital.phone}</span>
                <span>Ambulances: <b>{hospital.available_ambulances_count || 0} ready</b></span>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
