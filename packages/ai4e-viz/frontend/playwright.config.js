import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  outputDir: 'test-results/playwright',
  timeout: 45_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  // The local Trame process owns one shared VTK scene.  Serial browser
  // projects mirror the supported local deployment and prevent desktop and
  // mobile tests from racing the same animation clock.
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI
    ? [['line'], ['junit', { outputFile: 'test-results/playwright-junit.xml' }], ['html', { outputFolder: 'test-results/playwright-html', open: 'never' }]]
    : [['list']],
  use: {
    baseURL: 'http://127.0.0.1:15275',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    { name: 'desktop-chromium', use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 960 } } },
    { name: 'mobile-chromium', use: { ...devices['Pixel 7'], viewport: { width: 390, height: 844 } } },
  ],
  webServer: [
    {
      command: 'QODER_FRONTEND_BASE=http://127.0.0.1:15275 QODER_TRAME_BASE=http://127.0.0.1:18090 ../backend/.venv/bin/python ../backend/scripts/run_isolated_api.py --port 18091',
      url: 'http://127.0.0.1:18091/api/health',
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      command: 'QODER_API_PROXY_TARGET=http://127.0.0.1:18091 npm run dev -- --host 127.0.0.1 --port 15275',
      url: 'http://127.0.0.1:15275',
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      command: 'cd ../backend && .venv/bin/python -m modules.visPhysField.trameServer --port 18090',
      url: 'http://127.0.0.1:18090',
      reuseExistingServer: false,
      timeout: 120_000,
    },
  ],
});
