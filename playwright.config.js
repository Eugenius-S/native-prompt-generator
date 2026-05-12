const { defineConfig } = require("@playwright/test");
const promptGeneratorPort = "8766";
const baseUrl = `http://127.0.0.1:${promptGeneratorPort}`;

module.exports = defineConfig({
  testDir: "./tests/e2e",
  timeout: 30_000,
  expect: {
    timeout: 10_000,
  },
  fullyParallel: false,
  reporter: "line",
  use: {
    baseURL: baseUrl,
    headless: true,
  },
  webServer: {
    command: "python app.py",
    env: {
      ...process.env,
      PROMPT_GENERATOR_PORT: promptGeneratorPort,
    },
    url: baseUrl,
    reuseExistingServer: false,
    timeout: 120_000,
  },
});
