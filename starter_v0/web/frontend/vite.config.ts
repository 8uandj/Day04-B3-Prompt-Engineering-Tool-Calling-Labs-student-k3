import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: { proxy: { "/api": "http://127.0.0.1:8000" } },
  build: { rollupOptions: { output: { manualChunks(id) {
    if (id.includes("react-markdown") || id.includes("remark") || id.includes("rehype") || id.includes("unified")) return "markdown";
    return undefined;
  } } } },
  test: { environment: "jsdom", setupFiles: "./src/test/setup.ts", include: ["src/**/*.test.ts", "src/**/*.test.tsx"] },
});
