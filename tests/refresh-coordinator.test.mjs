import test from "node:test";
import assert from "node:assert/strict";
import { tryAcquireRefreshLease, releaseRefreshLease } from "../src/refresh-coordinator.mjs";

function memoryStorage() {
  const map = new Map();
  return {
    getItem: key => map.has(key) ? map.get(key) : null,
    setItem: (key, value) => map.set(key, String(value)),
    removeItem: key => map.delete(key),
  };
}

test("only one tab owner may hold the refresh lease", () => {
  const storage = memoryStorage();
  assert.equal(tryAcquireRefreshLease(storage, "tab-a", 1000, 15000), true);
  assert.equal(tryAcquireRefreshLease(storage, "tab-b", 1001, 15000), false);
  releaseRefreshLease(storage, "tab-a");
  assert.equal(tryAcquireRefreshLease(storage, "tab-b", 1002, 15000), true);
});

test("expired refresh lease can be reclaimed", () => {
  const storage = memoryStorage();
  assert.equal(tryAcquireRefreshLease(storage, "tab-a", 1000, 100), true);
  assert.equal(tryAcquireRefreshLease(storage, "tab-b", 1200, 100), true);
});

test("storage refresh lock serializes concurrent callers", async () => {
  const storage = memoryStorage();
  const events = [];
  let release;
  const held = new Promise(resolve => { release = resolve; });

  const first = import("../src/refresh-coordinator.mjs").then(({ withStorageRefreshLock }) =>
    withStorageRefreshLock(async () => {
      events.push("a-start");
      await held;
      events.push("a-end");
    }, {
      storage,
      owner: "tab-a",
      sleep: async () => {},
    })
  );

  await new Promise(resolve => setTimeout(resolve, 10));

  const second = import("../src/refresh-coordinator.mjs").then(({ withStorageRefreshLock }) =>
    withStorageRefreshLock(async () => {
      events.push("b-run");
    }, {
      storage,
      owner: "tab-b",
      sleep: async () => new Promise(resolve => setTimeout(resolve, 1)),
    })
  );

  await new Promise(resolve => setTimeout(resolve, 10));
  assert.deepEqual(events, ["a-start"]);
  release();
  await Promise.all([first, second]);
  assert.deepEqual(events, ["a-start", "a-end", "b-run"]);
});
