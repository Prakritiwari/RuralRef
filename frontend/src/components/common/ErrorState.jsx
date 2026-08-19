import React from "react";
import { AlertCircle, RefreshCw } from "lucide-react";

export default function ErrorState({ message, retry }) {
  return (
    <div className="error-state">
      <AlertCircle size={32} />
      <h3>Unable to load this module</h3>
      <p>{message}</p>
      {retry && (
        <button type="button" className="secondary" onClick={retry}>
          <RefreshCw size={15} />
          Retry
        </button>
      )}
    </div>
  );
}
