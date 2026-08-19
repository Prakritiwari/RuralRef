import React, { useState, useEffect } from "react";
import {
  Activity,
  Ambulance,
  Brain,
  CheckCircle2,
  Clock3,
  Hospital,
  RefreshCw,
  Stethoscope,
  Users,
} from "lucide-react";
import { dashboardApi } from "../../api/dashboard";
import { useRealtime } from "../../hooks/useRealtime";
import StatCard from "../../components/common/StatCard";
import Loader from "../../components/common/Loader";
import ErrorState from "../../components/common/ErrorState";

export default function PHCDashboard({ setPage }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadDashboard() {
    try {
      setError("");
      const result = await dashboardApi.getDashboard();
      setData(result);
    } catch (err) {
      console.error("Dashboard load error:", err);
      setError(err.message || "Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  // Realtime update on resource changes & referrals
  useRealtime("hospital_resources", loadDashboard);
  useRealtime("referrals", loadDashboard);

  if (loading && !data) {
    return <Loader text="Loading command center..." />;
  }

  if (error && !data) {
    return (
      <section className="page">
        <ErrorState message={error} retry={loadDashboard} />
      </section>
    );
  }

  return (
    <section className="page">
      <div className="welcome">
        <div>
          <div className="eyebrow">REGIONAL OPERATIONS & TRIAGE</div>
          <h2>Primary Health Centre Command</h2>
          <p>Monitor real-time bed capacity and coordinate emergency patient transfers.</p>
        </div>

        <button
          type="button"
          className="primary"
          onClick={() => setPage("new")}
        >
          <Stethoscope size={17} />
          New Referral
        </button>
      </div>

      {/* STATS */}
      <div className="stat-grid">
        <StatCard
          title="Patients registered"
          value={data?.patients ?? data?.stats?.patients_count}
          icon={Users}
          type="neutral"
        />
        <StatCard
          title="Pending referrals"
          value={data?.pending_referrals ?? data?.stats?.pending_referrals_count}
          icon={Clock3}
          type="amber"
        />
        <StatCard
          title="Active transfers"
          value={data?.active_transfers ?? data?.stats?.active_transfers_count}
          icon={Ambulance}
          type="blue"
        />
        <StatCard
          title="Ambulances ready"
          value={data?.available_ambulances ?? data?.stats?.available_ambulances_count}
          icon={CheckCircle2}
          type="green"
        />
      </div>

      {/* HOSPITAL CAPACITY */}
      <div className="section-head">
        <div>
          <h3>Live Hospital Resource Capacity</h3>
          <p>Live resource availability across district & tertiary care centres</p>
        </div>

        <button
          type="button"
          className="icon-btn"
          onClick={loadDashboard}
          title="Refresh Data"
        >
          <RefreshCw size={17} className={loading ? "spin" : ""} />
        </button>
      </div>

      <div className="hospital-grid">
        {(data?.hospital_capacities || data?.resources || []).map((hospital, index) => (
          <div className="capacity" key={hospital.hospital_id || index}>
            <div className="cap-top">
              <div className="hospital-mark">
                <Hospital size={20} />
              </div>

              <div className="hospital-name">
                <b>{hospital.hospital_name || hospital.hospital}</b>
                <small>{hospital.district}</small>
              </div>

              <span className="online-dot">LIVE</span>
            </div>

            <div className="resources">
              <div>
                <span>ICU</span>
                <b style={{ color: (hospital.icu_available ?? hospital.icu) > 0 ? "#16a34a" : "#dc2626" }}>
                  {hospital.icu_available ?? hospital.icu ?? 0}
                </b>
              </div>
              <div>
                <span>O₂</span>
                <b style={{ color: (hospital.oxygen_available ?? hospital.oxygen) > 0 ? "#2563eb" : "#dc2626" }}>
                  {hospital.oxygen_available ?? hospital.oxygen ?? 0}
                </b>
              </div>
              <div>
                <span>Ventilators</span>
                <b style={{ color: (hospital.ventilators_available ?? hospital.ventilators) > 0 ? "#16a34a" : "#dc2626" }}>
                  {hospital.ventilators_available ?? hospital.ventilators ?? 0}
                </b>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* AI BANNER */}
      <div className="info-banner" style={{ marginTop: "32px" }}>
        <Brain size={23} />
        <div>
          <b>Explainable Decision-Support Matching Active</b>
          <span>
            Hospital recommendations are ranked using verified resource availability,
            travel distance, emergency readiness, and ambulance fleet availability.
            The attending clinician always makes the final referral choice.
          </span>
        </div>
      </div>
    </section>
  );
}
