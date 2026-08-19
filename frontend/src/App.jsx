import React, { useState } from "react";
import { useAuth } from "./context/AuthContext";
import Header from "./components/common/Header";
import Sidebar from "./components/common/Sidebar";
import AuthPage from "./pages/auth/AuthPage";
import PHCDashboard from "./pages/phc/PHCDashboard";
import NewReferralWizard from "./pages/phc/NewReferralWizard";
import ReferralQueue from "./pages/phc/ReferralQueue";
import ResourceInventoryManager from "./pages/hospital/ResourceInventoryManager";
import HospitalNetwork from "./pages/hospital/HospitalNetwork";
import AmbulanceFleetManager from "./pages/hospital/AmbulanceFleetManager";
import AmbulanceSimulator from "./pages/ambulance/AmbulanceSimulator";
import MyReferrals from "./pages/patient/MyReferrals";

export default function App() {
  const { user, loading, isAuthenticated, isPatient, isHospital } = useAuth();
  
  // Set default page based on role
  const [currentPage, setPage] = useState("overview");
  const [mobileOpen, setMobileOpen] = useState(false);

  if (loading) {
    return (
      <div className="splash">
        <div className="splash-logo">RR</div>
        <h2>RuralRefLink</h2>
        <p>Connecting care beyond city limits.</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AuthPage />;
  }

  // Titles for Header
  const titleMap = {
    overview: isHospital ? "Hospital Operations Command" : "PHC Command Center",
    new: "Create Emergency Referral",
    referrals: "Emergency Referral Queue",
    inventory: "Resource Inventory & Capacity",
    hospitals: "Hospital Capacity Network",
    ambulances: "Ambulance Fleet & Positioning",
    simulator: "GPS Driver Telemetry Simulator",
    myreferrals: "Your Care Journey",
  };

  const currentTitle = titleMap[currentPage] || "Emergency Coordination";

  return (
    <div className="app">
      {/* SIDEBAR NAVIGATION */}
      <Sidebar
        currentPage={currentPage}
        setPage={setPage}
        mobileOpen={mobileOpen}
        setMobileOpen={setMobileOpen}
      />

      {/* MAIN CONTENT AREA */}
      <main>
        <Header
          title={currentTitle}
          mobileOpen={mobileOpen}
          setMobileOpen={setMobileOpen}
          roleLabel={user?.organization_name}
        />

        {/* ACTIVE MODULE VIEW */}
        {currentPage === "overview" && <PHCDashboard setPage={setPage} />}
        {currentPage === "new" && (
          <NewReferralWizard onReferralCreated={() => setPage("referrals")} />
        )}
        {currentPage === "referrals" && <ReferralQueue />}
        {currentPage === "inventory" && <ResourceInventoryManager />}
        {currentPage === "hospitals" && <HospitalNetwork />}
        {currentPage === "ambulances" && <AmbulanceFleetManager />}
        {currentPage === "simulator" && <AmbulanceSimulator />}
        {currentPage === "myreferrals" && <MyReferrals />}
      </main>
    </div>
  );
}
