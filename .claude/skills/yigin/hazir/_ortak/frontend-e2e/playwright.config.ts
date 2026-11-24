import { defineConfig, devices } from "@playwright/test";

// e2e eki. Çalıştırma: docker compose -f compose.local.yaml --profile e2e run --rm e2e
// e2e servisi Traefik'in ağını paylaşır; tarayıcıdaki app.localhost doğrudan projenin Traefik'ine gider.
export default defineConfig({
  testDir: "./e2e",
  outputDir: "./e2e/sonuclar",
  reporter: [["list"]],
  use: {
    baseURL: process.env.E2E_ADRES ?? "http://app.localhost",
    trace: "retain-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
