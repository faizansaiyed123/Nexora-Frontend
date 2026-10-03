import test from "node:test";
import assert from "node:assert/strict";
import { validateApiUrl } from "../scripts/validate-api-url.mjs";

test("production API URL requires explicit HTTPS public endpoint", () => {
  assert.equal(validateApiUrl("https://api.example.com").startsWith("https://"), true);
  assert.throws(() => validateApiUrl(undefined), /explicitly set/);
  assert.throws(() => validateApiUrl("http://localhost:8000"), /local\/internal/);
  assert.throws(() => validateApiUrl("http://api.example.com"), /HTTPS/);
});
