import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dashboard frontend (Dashboard_PRD.md section 2: Vite + React).
// Dev server proxies /api calls to the Dashboard backend so the
// frontend never needs to hardcode a backend host.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
