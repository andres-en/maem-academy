import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  // Extra hostnames (besides localhost/IPs) allowed to reach the dev server,
  // comma-separated, e.g. "my-pc.lan.example.com".
  const allowedHosts = (env.VITE_ALLOWED_HOSTS ?? "")
    .split(",")
    .map((host) => host.trim())
    .filter(Boolean);

  return {
    plugins: [react()],
    server: {
      host: true,
      port: 2309,
      allowedHosts,
      watch: {
        usePolling: true,
      },
    },
  };
});
