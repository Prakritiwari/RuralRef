import React from "react";
import { X } from "lucide-react";

export default function Modal({ isOpen, onClose, title, children }) {
  if (!isOpen) return null;

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        backgroundColor: "rgba(15, 23, 42, 0.6)",
        backdropFilter: "blur(4px)",
        display: "grid",
        placeItems: "center",
        zIndex: 9999,
        padding: "16px",
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: "#ffffff",
          borderRadius: "14px",
          width: "100%",
          maxWidth: "540px",
          boxShadow: "0 20px 60px rgba(0, 0, 0, 0.2)",
          border: "1px solid var(--line)",
          overflow: "hidden",
          animation: "modalFadeIn 0.2s ease-out",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "18px 24px",
            borderBottom: "1px solid var(--line)",
          }}
        >
          <h3 style={{ margin: 0, fontSize: "16px", fontWeight: "700" }}>{title}</h3>
          <button
            type="button"
            onClick={onClose}
            style={{
              background: "transparent",
              padding: "6px",
              borderRadius: "6px",
              color: "#64748b",
              display: "flex",
              alignItems: "center",
            }}
          >
            <X size={18} />
          </button>
        </div>

        <div style={{ padding: "24px", maxHeight: "80vh", overflowY: "auto" }}>
          {children}
        </div>
      </div>
    </div>
  );
}
