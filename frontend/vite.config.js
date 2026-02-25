import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Proxy za API zahtjeve – izbjegava CORS probleme u razvoju.
// Svaki poziv na /api/* se preusmjerava na FastAPI server (port 8000).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
