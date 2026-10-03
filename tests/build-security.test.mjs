import test from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const script = resolve(root, "scripts/validate-api-config.mjs");

function run(env) {
  return spawnSync(process.execPath, [script], {
    cwd: root,
    env: { ...process.env, ...env },
    encoding: "utf8",
  });
}

test("production builds reject missing API URL", () => {
  const result = run({ VITE_API_BUILD_MODE: "production", VITE_API_URL: "" });
  assert.notEqual(result.status, 0);
});

test("production builds reject localhost API URL", () => {
  const result = run({ VITE_API_BUILD_MODE: "production", VITE_API_URL: "http://localhost:8000" });
  assert.notEqual(result.status, 0);
});

test("production builds reject non-HTTPS API URL", () => {
  const result = run({ VITE_API_BUILD_MODE: "production", VITE_API_URL: "http://api.example.com" });
  assert.notEqual(result.status, 0);
});

test("production builds accept a valid HTTPS API URL", () => {
  const result = run({ VITE_API_BUILD_MODE: "production", VITE_API_URL: "https://api.example.com" });
  assert.equal(result.status, 0, result.stderr);
});

test("development can omit the API URL", () => {
  const result = run({ VITE_API_BUILD_MODE: "development", VITE_API_URL: "" });
  assert.equal(result.status, 0, result.stderr);
});
