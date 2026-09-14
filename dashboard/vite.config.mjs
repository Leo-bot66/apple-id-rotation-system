import { realpathSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Keep Vite and Rollup on the same canonical path when Windows redirects the
// Documents folder through a junction or symlink.
const projectRoot = realpathSync(fileURLToPath(new URL(".", import.meta.url)));

export default defineConfig({
  root: projectRoot,
  // The local public folder contains private prototype reference material and
  // must never be copied into public builds.
  publicDir: false,
  // Relative asset paths allow the same build to work on a GitHub Pages project URL.
  base: "./",
  build: {
    outDir: "dist/client",
  },
  optimizeDeps: {
    include: ["react", "react-dom/client"],
  },
  server: {
    host: "0.0.0.0",
    allowedHosts: ["terminal.local"],
    warmup: {
      clientFiles: ["./src/main.jsx"],
    },
  },
  plugins: [react()],
});
