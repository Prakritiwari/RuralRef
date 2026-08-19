import { createClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

export const supabase = (supabaseUrl && supabaseAnonKey)
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null;

/**
 * Helper to subscribe to realtime events on any table.
 * If Supabase is not configured, returns an empty unsubscribe function safely.
 */
export function subscribeToTable(table, onEvent) {
  if (!supabase) {
    return () => {};
  }

  const channel = supabase
    .channel(`public:${table}`)
    .on(
      "postgres_changes",
      { event: "*", schema: "public", table: table },
      (payload) => {
        if (onEvent) onEvent(payload);
      }
    )
    .subscribe();

  return () => {
    supabase.removeChannel(channel);
  };
}
