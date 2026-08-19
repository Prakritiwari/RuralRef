import React, { createContext, useContext, useState, useEffect } from "react";
import { authApi } from "../api/auth";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadUser() {
      const token = localStorage.getItem("token");
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const profile = await authApi.getMe();
        setUser(profile);
      } catch (err) {
        console.warn("Session expired or invalid, signing out:", err.message);
        localStorage.removeItem("token");
        setUser(null);
      } finally {
        setLoading(false);
      }
    }

    loadUser();
  }, []);

  const login = async (email, password) => {
    setError("");
    const res = await authApi.login(email, password);
    localStorage.setItem("token", res.token);
    setUser(res.user);
    return res.user;
  };

  const register = async (userData) => {
    setError("");
    const res = await authApi.register(userData);
    localStorage.setItem("token", res.token);
    setUser(res.user);
    return res.user;
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        setUser,
        loading,
        error,
        setError,
        login,
        register,
        logout,
        isAuthenticated: !!user,
        isPHC: user?.role === "PHC" || user?.role === "doctor",
        isHospital: user?.role === "HOSPITAL" || user?.role === "admin",
        isAdmin: user?.role === "ADMIN",
        isPatient: user?.role === "PATIENT" || user?.role === "patient",
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
