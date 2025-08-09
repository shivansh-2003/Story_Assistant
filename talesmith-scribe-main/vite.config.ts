import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig({
  server: {
    host: "::",
    port: 8080,
  },
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  define: {
    // Ensure environment variables are available
    'import.meta.env.VITE_API_URL': JSON.stringify(process.env.VITE_API_URL || 'https://story-assistant.onrender.com'),
  },
});