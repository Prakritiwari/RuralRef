import React from "react";
import {
  Activity,
  Ambulance,
  Building2,
  Clock3,
  HeartPulse,
  LogOut,
  MapPin,
  Stethoscope,
  ChevronRight,
  Boxes,
  Navigation,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";

export default function Sidebar({ currentPage, setPage, mobileOpen, setMobileOpen }) {
  const { user, logout, isPHC, isHospital, isAdmin, isPatient } = useAuth();

  const handleNav = (pageId) => {
    setPage(pageId);
    setMobileOpen(false);
  };

  // Build navigation items based on user role
  let navItems = [];
  if (isPatient) {
    navItems = [["myreferrals", "My Referrals", HeartPulse]];
  } else if (isPHC) {
    navItems = [
      ["overview", "Command Center", Activity],
      ["new", "Create Referral", Stethoscope],
      ["referrals", "Referral Queue", Clock3],
      ["hospitals", "Hospital Capacity", Building2],
      ["ambulances", "Ambulance Network", Ambulance],
      ["simulator", "GPS Driver Simulator", Navigation],
    ];
  } else if (isHospital) {
    navItems = [
      ["overview", "Hospital Command", Activity],
      ["referrals", "Incoming Referrals", Clock3],
      ["inventory", "Resource Inventory", Boxes],
      ["ambulances", "Ambulance Fleet", Ambulance],
      ["hospitals", "Hospital Network", Building2],
      ["simulator", "GPS Driver Simulator", Navigation],
    ];
  } else {
    // Admin
    navItems = [
      ["overview", "Command Center", Activity],
      ["new", "Create Referral", Stethoscope],
      ["referrals", "Referral Queue", Clock3],
      ["inventory", "Resource Management", Boxes],
      ["hospitals", "Hospital Network", Building2],
      ["ambulances", "Ambulance Fleet", Ambulance],
      ["simulator", "GPS Driver Simulator", Navigation],
    ];
  }

  const roleDisplay = isPHC
    ? "PHC DOCTOR"
    : isHospital
    ? "HOSPITAL ADMIN"
    : isAdmin
    ? "SYSTEM ADMIN"
    : "PATIENT";

  return (
    <aside className={mobileOpen ? "open" : ""}>
      <div className="brand">
        <span>RR</span>
        RuralRefLink
      </div>

      <div className="role-pill">
        {roleDisplay}
        {user?.organization_name && (
          <div style={{ fontSize: "10px", color: "#93c5fd", marginTop: "3px", textTransform: "none", fontWeight: "600" }}>
            {user.organization_name}
          </div>
        )}
      </div>

      <nav>
        {navItems.map(([id, label, Icon]) => (
          <button
            type="button"
            key={id}
            className={currentPage === id ? "nav active" : "nav"}
            onClick={() => handleNav(id)}
          >
            <Icon size={18} />
            <span>{label}</span>
            {currentPage === id && <ChevronRight size={15} className="nav-arrow" />}
          </button>
        ))}
      </nav>

      <div className="side-bottom">
        <div className="user-mini">
          <div className="avatar">{user?.name?.charAt(0)?.toUpperCase() || "U"}</div>
          <div className="user-details">
            <b>{user?.name}</b>
            <small>{user?.email}</small>
          </div>
        </div>

        <button type="button" className="logout" onClick={logout}>
          <LogOut size={16} />
          Sign out
        </button>
      </div>
    </aside>
  );
}
