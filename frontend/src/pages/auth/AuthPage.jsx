import React, { useState } from "react";
import { ArrowRight, ShieldCheck, AlertCircle } from "lucide-react";
import { useAuth } from "../../context/AuthContext";

export default function AuthPage() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState("login");

  const [role, setRole] = useState("doctor");
  const [email, setEmail] = useState("doctor@demo.com");
  const [password, setPassword] = useState("demo123");
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const fillDemo = (demoEmail, demoRole) => {
    setEmail(demoEmail);
    setPassword("demo123");
    setRole(demoRole);
    setError("");
  };

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        await register({
          name,
          email,
          password,
          role,
          phone,
        });
      }
    } catch (err) {
      setError(err.message || "Authentication failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth">
      <div className="auth-left">
        <div className="brand auth-brand">
          <span>RR</span>
          RuralRefLink
        </div>

        <div className="hero-copy">
          <div className="eyebrow">REAL-TIME EMERGENCY CARE COORDINATION</div>

          <h1>
            Right care.
            <br />
            <em>Right place.</em>
            <br />
            Right now.
          </h1>

          <p>
            Coordinate rural referrals, hospital capacity, and emergency transport
            from one unified command centre.
          </p>

          <div className="trust">
            <ShieldCheck size={18} />
            Explainable recommendations · Live resources · GPS ambulance tracking
          </div>
        </div>
      </div>

      <div className="auth-card">
        <div className="tabs">
          <button
            type="button"
            className={mode === "login" ? "active" : ""}
            onClick={() => {
              setMode("login");
              setError("");
            }}
          >
            Sign in
          </button>

          <button
            type="button"
            className={mode === "register" ? "active" : ""}
            onClick={() => {
              setMode("register");
              setError("");
            }}
          >
            Register
          </button>
        </div>

        <h2>
          {mode === "login" ? "Welcome back" : "Create your care account"}
        </h2>

        <p className="muted">
          {mode === "login"
            ? "Access your emergency referral workspace."
            : "Choose your role to get started."}
        </p>

        <form onSubmit={handleSubmit}>
          {mode === "register" && (
            <>
              <label>
                Full name
                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Dr. Priya Sharma"
                  required
                />
              </label>

              <label>
                Phone
                <input
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+91-9876543210"
                />
              </label>

              <label>
                Role
                <select value={role} onChange={(e) => setRole(e.target.value)}>
                  <option value="doctor">PHC Doctor (Primary Health Centre)</option>
                  <option value="hospital">Hospital Admin / Critical Care Team</option>
                  <option value="patient">Patient</option>
                </select>
              </label>
            </>
          )}

          <label>
            Email
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              type="email"
              placeholder="name@ruralreflink.gov"
              required
            />
          </label>

          <label>
            Password
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              type="password"
              placeholder="••••••••"
              required
            />
          </label>

          {error && (
            <div className="error">
              <AlertCircle size={15} />
              {error}
            </div>
          )}

          <button className="primary full" type="submit" disabled={loading}>
            {loading ? "Please wait..." : mode === "login" ? "Sign in" : "Create account"}
            {!loading && <ArrowRight size={17} />}
          </button>
        </form>

        {mode === "login" && (
          <div className="demo-box" style={{ marginTop: "24px" }}>
            <b style={{ display: "block", marginBottom: "8px" }}>Quick Demo Accounts (Password: demo123)</b>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "6px" }}>
              <button
                type="button"
                className="secondary"
                style={{ fontSize: "11px", padding: "6px 8px" }}
                onClick={() => fillDemo("doctor@demo.com", "doctor")}
              >
                🩺 PHC Doctor
              </button>
              <button
                type="button"
                className="secondary"
                style={{ fontSize: "11px", padding: "6px 8px" }}
                onClick={() => fillDemo("hospital@demo.com", "hospital")}
              >
                🏥 Hospital Admin
              </button>
              <button
                type="button"
                className="secondary"
                style={{ fontSize: "11px", padding: "6px 8px" }}
                onClick={() => fillDemo("admin@demo.com", "admin")}
              >
                ⚙️ System Admin
              </button>
              <button
                type="button"
                className="secondary"
                style={{ fontSize: "11px", padding: "6px 8px" }}
                onClick={() => fillDemo("patient@demo.com", "patient")}
              >
                👤 Patient
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
