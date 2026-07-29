import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  retries: 0,
  reporter: "line",
  use: { baseURL: "http://127.0.0.1:8020", trace: "retain-on-failure" },
  webServer: { command: "./.venv/bin/python -m uvicorn web.backend.main:app --host 127.0.0.1 --port 8020", cwd: "../..", url: "http://127.0.0.1:8020/api/health", reuseExistingServer: false, timeout: 30_000 },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"], viewport: { width: 1440, height: 900 } } },
    { name: "mobile", use: { ...devices["Pixel 7"] } },
  ],
});
