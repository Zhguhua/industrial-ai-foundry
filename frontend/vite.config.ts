import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => ({
  plugins: [react()],
  base: mode === "pages" ? "/industrial-ai-foundry/" : "/",
  server: {
    port: 5173,
    proxy: {
      "/api": "http://api:8000",
      "/health": "http://api:8000"
    }
  }
}));
