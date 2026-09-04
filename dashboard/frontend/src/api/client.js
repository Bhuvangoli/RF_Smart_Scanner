/**
 * Thin client for the Dashboard backend HTTP API
 * (Dashboard_PRD.md section 31). All calls are relative to /api and
 * proxied to the backend by Vite in dev (see vite.config.js) or by
 * whatever reverse proxy fronts the app in a deployed build.
 */
const BASE = "/api/v1";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || body.error || detail;
    } catch {
      /* ignore parse errors */
    }
    throw new Error(`${path} failed: ${detail}`);
  }
  return res.json();
}

export const api = {
  getDashboardState: () => request("/dashboard/state"),
  getHistory: (limit = 200) => request(`/history?limit=${limit}`),
  getHealth: () => request("/health"),

  startSimulation: (scenario, seed) =>
    request(
      `/simulation/start?scenario=${encodeURIComponent(scenario)}${
        seed !== undefined ? `&seed=${seed}` : ""
      }`,
      { method: "POST" }
    ),
  pauseSimulation: () => request("/simulation/pause", { method: "POST" }),
  resumeSimulation: () => request("/simulation/resume", { method: "POST" }),
  resetSimulation: () => request("/simulation/reset", { method: "POST" }),
};
