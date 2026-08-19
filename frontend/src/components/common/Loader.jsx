import React from "react";
import { RefreshCw } from "lucide-react";

export default function Loader({ text = "Loading live data..." }) {
  return (
    <div className="loader">
      <RefreshCw size={22} className="spin" />
      <span>{text}</span>
    </div>
  );
}
