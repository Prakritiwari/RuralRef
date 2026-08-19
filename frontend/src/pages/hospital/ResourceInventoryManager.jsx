import React, { useState, useEffect } from "react";
import { AlertCircle, CheckCircle2, RefreshCw, Boxes, Plus, Minus, Edit3, ShieldAlert } from "lucide-react";
import { hospitalsApi } from "../../api/hospitals";
import { useAuth } from "../../context/AuthContext";
import { useRealtime } from "../../hooks/useRealtime";
import Loader from "../../components/common/Loader";
import Modal from "../../components/common/Modal";

export default function ResourceInventoryManager() {
  const { user, isHospital, isAdmin } = useAuth();
  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Edit Modal State
  const [editingResource, setEditingResource] = useState(null);
  const [editTotal, setEditTotal] = useState(0);
  const [editAvailable, setEditAvailable] = useState(0);
  const [editReserved, setEditReserved] = useState(0);
  const [saving, setSaving] = useState(false);

  // Target Hospital ID
  const hospitalId = user?.organization_id || "b0000001-0000-0000-0000-000000000001";

  async function loadInventory() {
    try {
      setError("");
      const result = await hospitalsApi.getHospitalResources(hospitalId);
      setResources(Array.isArray(result) ? result : []);
    } catch (err) {
      console.error("Failed to load hospital inventory:", err);
      setError(err.message || "Failed to load hospital resource inventory");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadInventory();
  }, [hospitalId]);

  useRealtime("hospital_resources", loadInventory, 3000);

  const handleAdjust = async (resourceId, delta) => {
    try {
      setError("");
      setSuccess("");
      await hospitalsApi.adjustResource(hospitalId, resourceId, delta);
      await loadInventory();
      setSuccess(`Resource ${resourceId} quantity updated.`);
    } catch (err) {
      setError(err.message || "Failed to adjust resource count");
    }
  };

  const openEditModal = (res) => {
    setEditingResource(res);
    setEditTotal(res.total_quantity);
    setEditAvailable(res.available_quantity);
    setEditReserved(res.reserved_quantity);
  };

  const handleSaveEdit = async (e) => {
    e.preventDefault();
    if (!editingResource) return;

    if (editAvailable < 0 || editReserved < 0 || editTotal < 0) {
      setError("Resource quantities cannot be negative");
      return;
    }

    if (editAvailable + editReserved > editTotal) {
      setError(`Available (${editAvailable}) + Reserved (${editReserved}) cannot exceed Total capacity (${editTotal})`);
      return;
    }

    setSaving(true);
    setError("");
    try {
      await hospitalsApi.updateResource(hospitalId, editingResource.resource_id, {
        total_quantity: editTotal,
        available_quantity: editAvailable,
        reserved_quantity: editReserved,
      });

      setEditingResource(null);
      await loadInventory();
      setSuccess(`Inventory for ${editingResource.resource_name || editingResource.resource_id} saved successfully.`);
    } catch (err) {
      setError(err.message || "Failed to save resource update");
    } finally {
      setSaving(false);
    }
  };

  return (
    <section className="page">
      <div className="section-head">
        <div>
          <div className="eyebrow">HOSPITAL CAPACITY MANAGEMENT</div>
          <h3>Emergency Resource Inventory</h3>
          <p>Maintain live operational capacity for ICU beds, ventilators, oxygen, and emergency trauma units.</p>
        </div>

        <button type="button" className="icon-btn" onClick={loadInventory} title="Refresh">
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

      {loading && !resources.length ? (
        <Loader text="Loading hospital inventory..." />
      ) : (
        <div className="table" style={{ background: "#ffffff", borderRadius: "12px", border: "1px solid var(--line)", overflow: "hidden" }}>
          <div className="tr th">
            <span>Medical Resource</span>
            <span>Category</span>
            <span>Available</span>
            <span>Reserved</span>
            <span>Total Capacity</span>
            <span>Status</span>
            <span>Quick Adjust</span>
          </div>

          {resources.map((res) => {
            const statusClass = res.status === "AVAILABLE" ? "AVAILABLE" : res.status === "LIMITED" ? "LIMITED" : "UNAVAILABLE";

            return (
              <div className="tr" key={res.id}>
                <span>
                  <b>{res.resource_name || res.resource_id}</b>
                  <small>{res.resource_unit || "Unit"}</small>
                </span>

                <span>
                  <span style={{ fontSize: "11px", background: "#f1f5f9", padding: "3px 8px", borderRadius: "4px", color: "#475569", fontWeight: "600" }}>
                    {res.resource_category || "EQUIPMENT"}
                  </span>
                </span>

                <span>
                  <b style={{ fontSize: "15px", color: res.available_quantity > 0 ? "#16a34a" : "#dc2626" }}>
                    {res.available_quantity}
                  </b>
                </span>

                <span>
                  <b style={{ fontSize: "14px", color: "#2563eb" }}>{res.reserved_quantity}</b>
                </span>

                <span>
                  <b>{res.total_quantity}</b>
                </span>

                <span>
                  <i
                    className="status"
                    style={{
                      background: res.available_quantity > 2 ? "#dcfce7" : res.available_quantity > 0 ? "#fef3c7" : "#fee2e2",
                      color: res.available_quantity > 2 ? "#15803d" : res.available_quantity > 0 ? "#b45309" : "#b91c1c",
                    }}
                  >
                    {res.status}
                  </i>
                </span>

                <span className="actions" style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  <button
                    type="button"
                    className="tiny red"
                    disabled={res.available_quantity <= 0}
                    onClick={() => handleAdjust(res.resource_id, -1)}
                    title="Decrease available count"
                  >
                    <Minus size={13} />
                  </button>

                  <button
                    type="button"
                    className="tiny green"
                    disabled={res.available_quantity + res.reserved_quantity >= res.total_quantity}
                    onClick={() => handleAdjust(res.resource_id, 1)}
                    title="Increase available count"
                  >
                    <Plus size={13} />
                  </button>

                  <button
                    type="button"
                    className="tiny blue"
                    onClick={() => openEditModal(res)}
                    title="Edit capacity details"
                  >
                    <Edit3 size={13} />
                  </button>
                </span>
              </div>
            );
          })}
        </div>
      )}

      {/* EDIT MODAL */}
      <Modal
        isOpen={!!editingResource}
        onClose={() => setEditingResource(null)}
        title={`Edit Capacity: ${editingResource?.resource_name || editingResource?.resource_id}`}
      >
        <form onSubmit={handleSaveEdit}>
          <label>
            Total Physical Capacity
            <input
              type="number"
              min="0"
              value={editTotal}
              onChange={(e) => setEditTotal(parseInt(e.target.value, 10) || 0)}
              required
            />
          </label>

          <div className="two">
            <label>
              Available (Unoccupied)
              <input
                type="number"
                min="0"
                value={editAvailable}
                onChange={(e) => setEditAvailable(parseInt(e.target.value, 10) || 0)}
                required
              />
            </label>

            <label>
              Reserved (Referrals in transit)
              <input
                type="number"
                min="0"
                value={editReserved}
                onChange={(e) => setEditReserved(parseInt(e.target.value, 10) || 0)}
                required
              />
            </label>
          </div>

          <div style={{ background: "#f8fafc", padding: "10px", borderRadius: "6px", fontSize: "11.5px", color: "#64748b", margin: "10px 0" }}>
            Consistency check: Available ({editAvailable}) + Reserved ({editReserved}) = {editAvailable + editReserved} / Total {editTotal}
          </div>

          <button
            type="submit"
            className="primary full"
            disabled={saving || editAvailable + editReserved > editTotal}
            style={{ marginTop: "12px" }}
          >
            {saving ? "Saving Changes..." : "Save Resource Capacity"}
          </button>
        </form>
      </Modal>
    </section>
  );
}
