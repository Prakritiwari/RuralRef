import React from "react";
import { Menu } from "lucide-react";

export default function Header({ title, mobileOpen, setMobileOpen, roleLabel }) {
  return (
    <header>
      <div className="header-left">
        <button
          type="button"
          className="menu"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Toggle Navigation Menu"
        >
          <Menu size={22} />
        </button>

        <div>
          <div className="live">
            <span></span>
            SYSTEM LIVE {roleLabel ? `· ${roleLabel}` : ""}
          </div>
          <h1>{title || "Command Center"}</h1>
        </div>
      </div>

      <div className="header-right">
        <div className="header-date">
          {new Date().toLocaleDateString("en-IN", {
            weekday: "short",
            day: "2-digit",
            month: "short",
            year: "numeric",
          })}
        </div>
      </div>
    </header>
  );
}
