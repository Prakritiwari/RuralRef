import React from "react";

export default function StatCard({ title, value, icon: Icon, type = "neutral" }) {
  return (
    <div className="stat">
      <div className={`stat-icon ${type}`}>
        <Icon size={19} />
      </div>
      <div>
        <span>{title}</span>
        <strong>{value ?? 0}</strong>
      </div>
    </div>
  );
}
