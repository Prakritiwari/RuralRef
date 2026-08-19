import React, { useState, useEffect } from "react";
import {
  Activity,
  AlertCircle,
  ArrowRight,
  Brain,
  CheckCircle2,
  HeartPulse,
  Plus,
  RefreshCw,
  Wind,
  ShieldCheck,
  Building2,
  Clock,
  MapPin,
} from "lucide-react";
import { phcApi } from "../../api/phc";
import { resourcesApi } from "../../api/resources";
import { referralsApi } from "../../api/referrals";
import Modal from "../../components/common/Modal";

export default function NewReferralWizard({ onReferralCreated }) {
  const [patients, setPatients] = useState([]);
  const [patientId, setPatientId] = useState("");
  const [resourceCatalog, setResourceCatalog] = useState([]);
  
  // Selected resource requirement map: { 'ICU': 1, 'VENTILATOR': 1, 'OXYGEN': 1 }
  const [selectedResources, setSelectedResources] = useState({
    ICU: 1,
    OXYGEN: 1,
  });

  const [symptoms, setSymptoms] = useState("");
  const [urgency, setUrgency] = useState("CRITICAL");
  const [specialist, setSpecialist] = useState("");
  const [notes, setNotes] = useState("");

  const [referralId, setReferralId] = useState(null);
  const [recommendations, setRecommendations] = useState(null);

  const [loadingPatients, setLoadingPatients] = useState(true);
  const [loadingRecommendation, setLoadingRecommendation] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // New Patient Modal State
  const [showPatientModal, setShowPatientModal] = useState(false);
  const [newPatientName, setNewPatientName] = useState("");
  const [newPatientAge, setNewPatientAge] = useState("");
  const [newPatientGender, setNewPatientGender] = useState("Male");
  const [newPatientPhone, setNewPatientPhone] = useState("");
  const [newPatientBlood, setNewPatientBlood] = useState("O+");
  const [newPatientSummary, setNewPatientSummary] = useState("");
  const [creatingPatient, setCreatingPatient] = useState(false);

  useEffect(() => {
    async function loadInitialData() {
      try {
        setLoadingPatients(true);
        const [patientsData, catalogData] = await Promise.all([
          phcApi.getPatients(),
          resourcesApi.getCatalog(),
        ]);
        setPatients(Array.isArray(patientsData) ? patientsData : []);
        setResourceCatalog(Array.isArray(catalogData) ? catalogData : []);
        if (patientsData && patientsData.length > 0) {
          setPatientId(patientsData[0].id);
          setSymptoms(patientsData[0].emergency_summary || "");
        }
      } catch (err) {
        console.error("Failed to load intake data:", err);
        setError(err.message || "Failed to load intake data");
      } finally {
        setLoadingPatients(false);
      }
    }
    loadInitialData();
  }, []);

  const handlePatientChange = (pId) => {
    setPatientId(pId);
    const selected = patients.find((p) => p.id === pId);
    if (selected && selected.emergency_summary) {
      setSymptoms(selected.emergency_summary);
    }
  };

  const toggleResource = (resId) => {
    setSelectedResources((prev) => {
      const next = { ...prev };
      if (next[resId]) {
        delete next[resId];
      } else {
        next[resId] = 1;
      }
      return next;
    });
  };

  const updateQuantity = (resId, delta) => {
    setSelectedResources((prev) => {
      const currentQty = prev[resId] || 1;
      const newQty = Math.max(1, currentQty + delta);
      return { ...prev, [resId]: newQty };
    });
  };

  const handleCreatePatient = async (e) => {
    e.preventDefault();
    if (!newPatientName.trim() || !newPatientAge) return;

    setCreatingPatient(true);
    setError("");
    try {
      const created = await phcApi.createPatient({
        name: newPatientName.trim(),
        age: parseInt(newPatientAge, 10),
        gender: newPatientGender,
        phone: newPatientPhone,
        blood_group: newPatientBlood,
        emergency_summary: newPatientSummary,
      });

      setPatients((prev) => [created, ...prev]);
      setPatientId(created.id);
      setSymptoms(created.emergency_summary || "");
      setShowPatientModal(false);
      setSuccess(`Patient ${created.name} registered successfully.`);
    } catch (err) {
      setError(err.message || "Failed to register patient");
    } finally {
      setCreatingPatient(false);
    }
  };

  async function handleFindHospitals() {
    setError("");
    setSuccess("");
    setRecommendations(null);

    if (!patientId) {
      setError("Please select or register a patient.");
      return;
    }
    if (!symptoms.trim()) {
      setError("Please enter the patient's presenting symptoms / clinical summary.");
      return;
    }

    const requiredResourcesPayload = Object.entries(selectedResources).map(
      ([resource_id, quantity]) => ({
        resource_id,
        quantity,
        is_critical: true,
      })
    );

    try {
      setLoadingRecommendation(true);

      // 1. Create Referral in DB
      const ref = await referralsApi.createReferral({
        patient_id: patientId,
        urgency,
        clinical_summary: symptoms,
        specialist_needed: specialist,
        notes,
        required_resources: requiredResourcesPayload,
      });

      setReferralId(ref.id);

      // 2. Fetch explainable recommendations
      const recs = await referralsApi.getRecommendations(ref.id);
      setRecommendations(Array.isArray(recs) ? recs : []);
      setSuccess(`Referral #${ref.referral_number || ref.id} created. Best destination hospitals ranked below.`);
    } catch (err) {
      console.error("Referral creation error:", err);
      setError(err.message || "Failed to create referral");
    } finally {
      setLoadingRecommendation(false);
    }
  }

  async function handleSendReferral(hospitalId) {
    if (!referralId) {
      setError("Please find hospitals before sending a referral request.");
      return;
    }

    try {
      setError("");
      await referralsApi.sendReferral(referralId, hospitalId);

      setRecommendations((prev) =>
        prev.map((item) =>
          item.hospital_id === hospitalId ? { ...item, sent: true } : item
        )
      );

      setSuccess("Referral request successfully transmitted to the hospital. Awaiting acceptance.");
      if (onReferralCreated) onReferralCreated();
    } catch (err) {
      console.error("Send referral error:", err);
      setError(err.message || "Failed to dispatch referral to the hospital");
    }
  }

  return (
    <section className="page">
      <div className="form-layout">
        {/* CLINICAL INTAKE FORM */}
        <div className="panel form-panel">
          <div className="panel-title">
            <div>
              <div className="eyebrow">STEP 01 · CLINICAL TRIAGE</div>
              <h3>Emergency Referral Intake</h3>
              <p>Capture required medical resources and urgency for logistical destination matching.</p>
            </div>
            <span className="step">PHC WORKSPACE</span>
          </div>

          {/* PATIENT SELECTION */}
          <div style={{ display: "flex", gap: "10px", alignItems: "flex-end" }}>
            <label style={{ flex: 1 }}>
              Patient
              <select
                value={patientId}
                onChange={(e) => handlePatientChange(e.target.value)}
              >
                <option value="">
                  {loadingPatients
                    ? "Loading patient registry..."
                    : patients.length
                    ? "Select patient"
                    : "No patients available"}
                </option>
                {patients.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} ({p.age}y, {p.gender}) · {p.blood_group || "Blood Group N/A"}
                  </option>
                ))}
              </select>
            </label>

            <button
              type="button"
              className="secondary"
              style={{ marginBottom: "16px", height: "42px", whiteSpace: "nowrap" }}
              onClick={() => setShowPatientModal(true)}
            >
              <Plus size={16} />
              New Patient
            </button>
          </div>

          {/* SYMPTOMS */}
          <label>
            Presenting symptoms / Clinical Summary
            <textarea
              value={symptoms}
              onChange={(e) => setSymptoms(e.target.value)}
              placeholder="e.g. Acute chest pain, respiratory distress, SpO2 80%..."
              rows={3}
            />
          </label>

          {/* URGENCY & SPECIALIST */}
          <div className="two">
            <label>
              Urgency Level
              <select value={urgency} onChange={(e) => setUrgency(e.target.value)}>
                <option value="CRITICAL">Critical (Immediate life threat)</option>
                <option value="HIGH">High (Urgent transfer within 1 hr)</option>
                <option value="MEDIUM">Medium (Stable / semi-urgent)</option>
                <option value="LOW">Low (Elective transfer)</option>
              </select>
            </label>

            <label>
              Specialist / Service Needed
              <select value={specialist} onChange={(e) => setSpecialist(e.target.value)}>
                <option value="">No specific specialty</option>
                <option value="Emergency Medicine">Emergency Medicine</option>
                <option value="Cardiology">Cardiology / STEMI</option>
                <option value="Pulmonology">Pulmonology / ARDS</option>
                <option value="Neurology">Neurosurgery / Stroke</option>
                <option value="Trauma Care">Polytrauma Response</option>
              </select>
            </label>
          </div>

          {/* DYNAMIC RESOURCE PICKER */}
          <div className="check-title" style={{ marginTop: "16px" }}>
            Required Medical Resources & Units
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "10px", marginTop: "8px" }}>
            {resourceCatalog.map((res) => {
              const isSelected = !!selectedResources[res.id];
              const qty = selectedResources[res.id] || 1;

              return (
                <div
                  key={res.id}
                  style={{
                    border: isSelected ? "2px solid #2563eb" : "1px solid var(--line)",
                    background: isSelected ? "#f0f7ff" : "#ffffff",
                    borderRadius: "10px",
                    padding: "10px 12px",
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "space-between",
                    gap: "8px",
                  }}
                >
                  <div
                    onClick={() => toggleResource(res.id)}
                    style={{ cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "space-between" }}
                  >
                    <span style={{ fontSize: "12.5px", fontWeight: isSelected ? "700" : "500", color: isSelected ? "#1e40af" : "#1e293b" }}>
                      {res.name}
                    </span>
                    {isSelected ? <CheckCircle2 size={16} color="#2563eb" /> : <div style={{ width: 16, height: 16, border: "1px solid #cbd5e1", borderRadius: "4px" }} />}
                  </div>

                  {isSelected && (
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", borderTop: "1px solid #dbeafe", paddingTop: "6px" }}>
                      <span style={{ fontSize: "11px", color: "#64748b" }}>Qty ({res.unit || "unit"}):</span>
                      <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                        <button
                          type="button"
                          className="secondary"
                          style={{ padding: "2px 8px", fontSize: "12px", height: "24px" }}
                          onClick={() => updateQuantity(res.id, -1)}
                        >
                          -
                        </button>
                        <b style={{ fontSize: "13px", minWidth: "16px", textAlign: "center" }}>{qty}</b>
                        <button
                          type="button"
                          className="secondary"
                          style={{ padding: "2px 8px", fontSize: "12px", height: "24px" }}
                          onClick={() => updateQuantity(res.id, 1)}
                        >
                          +
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* NOTES */}
          <label style={{ marginTop: "16px" }}>
            Transport & Clinical Considerations
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g. Oxygen mask attached, IV cannula secured, companion travelling..."
              rows={2}
            />
          </label>

          {error && (
            <div className="error" style={{ marginTop: "12px" }}>
              <AlertCircle size={15} />
              {error}
            </div>
          )}

          {success && (
            <div className="success" style={{ marginTop: "12px" }}>
              <CheckCircle2 size={15} />
              {success}
            </div>
          )}

          <button
            type="button"
            className="primary full"
            disabled={!patientId || loadingRecommendation}
            onClick={handleFindHospitals}
            style={{ marginTop: "18px" }}
          >
            {loadingRecommendation ? (
              <>
                <RefreshCw size={17} className="spin" />
                Matching nearby hospitals...
              </>
            ) : (
              <>
                <Brain size={17} />
                Find Suitable Hospitals
              </>
            )}
          </button>
        </div>

        {/* RECOMMENDATION RESULTS PANEL */}
        <div className="panel recommendation">
          <div className="panel-title">
            <div>
              <div className="ai-label">
                <Brain size={15} />
                EXPLAINABLE LOGISTICS MATCH
              </div>
              <h3>Hospital Matching & Dispatch</h3>
              <p>Ranked by verified resource availability, distance, and fleet status.</p>
            </div>
          </div>

          {!recommendations ? (
            <div className="empty">
              <Brain size={38} />
              <b>Ready to match facilities</b>
              <span>Submit the referral requirements to rank eligible destination hospitals.</span>
            </div>
          ) : recommendations.length === 0 ? (
            <div className="empty">
              <AlertCircle size={35} />
              <b>No matching hospitals found</b>
              <span>No facilities in the network currently satisfy the required emergency criteria.</span>
            </div>
          ) : (
            recommendations.map((hospital, index) => {
              const isBest = hospital.is_eligible && index === 0;

              return (
                <div
                  className={isBest ? "rec best" : "rec"}
                  key={hospital.hospital_id}
                  style={{
                    opacity: hospital.is_eligible ? 1 : 0.7,
                    border: !hospital.is_eligible ? "1px dashed #cbd5e1" : undefined,
                  }}
                >
                  <div className="rec-head">
                    <div className="rank">{index + 1}</div>
                    <div style={{ flex: 1 }}>
                      <b>{hospital.hospital_name}</b>
                      <small>
                        {hospital.district} · {hospital.level}
                        {" · "}
                        <span style={{ color: hospital.is_eligible ? "#16a34a" : "#dc2626", fontWeight: "700" }}>
                          {hospital.is_eligible ? "Eligible" : "Resource Shortage"}
                        </span>
                      </small>
                    </div>
                    <strong>{hospital.recommendation_score}</strong>
                  </div>

                  <div className="score-label">MATCH SCORE</div>
                  <div className="score-track">
                    <div
                      style={{
                        width: `${Math.min(Number(hospital.recommendation_score) || 0, 100)}%`,
                        background: hospital.is_eligible ? undefined : "#ef4444",
                      }}
                    />
                  </div>

                  {/* Resource Breakdown Badges */}
                  <div className="rec-bars">
                    {hospital.resource_breakdown.slice(0, 3).map((res) => (
                      <div key={res.resource_id}>
                        <span>{res.resource_id}</span>
                        <b style={{ color: res.available_quantity > 0 ? "#16a34a" : "#dc2626" }}>
                          {res.available_quantity} avail
                        </b>
                      </div>
                    ))}
                  </div>

                  {/* Explainable reasons */}
                  <div className="reasons">
                    {hospital.match_reasons.map((reason, i) => (
                      <span key={i}>✓ {reason}</span>
                    ))}
                    {hospital.missing_resources.map((missing, i) => (
                      <span key={`m-${i}`} style={{ color: "#dc2626", background: "#fef2f2" }}>
                        ✗ {missing}
                      </span>
                    ))}
                  </div>

                  <button
                    type="button"
                    className="secondary full-secondary"
                    disabled={!hospital.is_eligible || hospital.sent}
                    onClick={() => handleSendReferral(hospital.hospital_id)}
                    style={{ marginTop: "14px" }}
                  >
                    {hospital.sent ? (
                      "Referral Request Sent ✓"
                    ) : (
                      <>
                        Send Referral Request
                        <ArrowRight size={15} />
                      </>
                    )}
                  </button>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* NEW PATIENT MODAL */}
      <Modal
        isOpen={showPatientModal}
        onClose={() => setShowPatientModal(false)}
        title="Register New PHC Patient"
      >
        <form onSubmit={handleCreatePatient}>
          <label>
            Full Name
            <input
              value={newPatientName}
              onChange={(e) => setNewPatientName(e.target.value)}
              placeholder="e.g. Anand Shankar Patil"
              required
            />
          </label>

          <div className="two">
            <label>
              Age (Years)
              <input
                type="number"
                value={newPatientAge}
                onChange={(e) => setNewPatientAge(e.target.value)}
                placeholder="45"
                min="0"
                max="130"
                required
              />
            </label>

            <label>
              Gender
              <select value={newPatientGender} onChange={(e) => setNewPatientGender(e.target.value)}>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </label>
          </div>

          <div className="two">
            <label>
              Phone Number
              <input
                value={newPatientPhone}
                onChange={(e) => setNewPatientPhone(e.target.value)}
                placeholder="+91-9876543210"
              />
            </label>

            <label>
              Blood Group
              <select value={newPatientBlood} onChange={(e) => setNewPatientBlood(e.target.value)}>
                <option value="O+">O+</option>
                <option value="O-">O-</option>
                <option value="A+">A+</option>
                <option value="A-">A-</option>
                <option value="B+">B+</option>
                <option value="B-">B-</option>
                <option value="AB+">AB+</option>
                <option value="AB-">AB-</option>
              </select>
            </label>
          </div>

          <label>
            Emergency Summary / Chief Complaint
            <textarea
              value={newPatientSummary}
              onChange={(e) => setNewPatientSummary(e.target.value)}
              placeholder="Describe acute condition..."
              rows={3}
            />
          </label>

          <button
            type="submit"
            className="primary full"
            disabled={creatingPatient}
            style={{ marginTop: "16px" }}
          >
            {creatingPatient ? "Saving..." : "Save & Select Patient"}
          </button>
        </form>
      </Modal>
    </section>
  );
}
