import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./e2e",
  workers: 1,
  timeout: 120000,
  use: {
    baseURL: process.env.DOJO_WEB_URL || "http://127.0.0.1:5173",
    headless: true,
    channel: "chrome",
    screenshot: "only-on-failure",
  },
  reporter: "list",
});
