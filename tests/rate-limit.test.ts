import assert from "node:assert/strict";
import { test } from "node:test";

import {
  formatRateLimitCountdown,
  getRateLimitRemaining,
  normalizeRateLimitKey,
  reportRateLimit,
} from "../src/rateLimit.ts";

test("query variants share their endpoint cooldown", () => {
  assert.equal(
    normalizeRateLimitKey("/v1/collections/run?offering_match_id=abc"),
    "/v1/collections/run",
  );
});

test("rate-limit countdown is persisted and formatted as mm:ss", () => {
  reportRateLimit("/v1/auth/login", 37);
  const remaining = getRateLimitRemaining("/v1/auth/login");
  assert.ok(remaining >= 36 && remaining <= 37);
  assert.equal(formatRateLimitCountdown(37), "00:37");
  assert.equal(formatRateLimitCountdown(125), "02:05");
});
