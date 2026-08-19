import { useEffect, useRef } from "react";
import { subscribeToTable, supabase } from "../api/supabase";

/**
 * Custom hook for live data synchronization.
 * If Supabase credentials are configured, subscribes to Postgres change events.
 * Additionally maintains a light polling fallback (every pollIntervalMs) so the app
 * always stays synchronized during demo simulations even without external cloud setup.
 */
export function useRealtime(tableName, onUpdate, pollIntervalMs = 4000) {
  const onUpdateRef = useRef(onUpdate);
  onUpdateRef.current = onUpdate;

  useEffect(() => {
    // 1. Supabase Realtime channel subscription
    let unsubscribe = () => {};
    if (supabase && tableName) {
      unsubscribe = subscribeToTable(tableName, (payload) => {
        if (onUpdateRef.current) {
          onUpdateRef.current(payload);
        }
      });
    }

    // 2. Light polling fallback to guarantee live updates during local simulations
    let intervalId = null;
    if (pollIntervalMs && pollIntervalMs > 0) {
      intervalId = setInterval(() => {
        if (onUpdateRef.current) {
          onUpdateRef.current({ eventType: "POLL" });
        }
      }, pollIntervalMs);
    }

    return () => {
      unsubscribe();
      if (intervalId) clearInterval(intervalId);
    };
  }, [tableName, pollIntervalMs]);
}
