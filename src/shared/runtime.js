export function configureRuntime() {
  const apiBase = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");
  globalThis.SIMULATION_API_BASE = apiBase;
}
