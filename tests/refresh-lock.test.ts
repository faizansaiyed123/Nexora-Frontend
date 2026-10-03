import test from "node:test";
import assert from "node:assert/strict";
import {
  readRefreshLease,
  releaseRefreshLease,
  tryAcquireRefreshLease,
} from "../src/refreshLock.ts";

class MemoryStorage implements Pick<Storage, "getItem" | "setItem" | "removeItem"> {
  private data = new Map<string, string>();
  getItem(key: string) { return this.data.get(key) ?? null; }
  setItem(key: string, value: string) { this.data.set(key, value); }
  removeItem(key: string) { this.data.delete(key); }
}

test("refresh lease allows only one owner until expiry", () => {
  const storage = new MemoryStorage();
  assert.equal(tryAcquireRefreshLease(storage, "lock", "tab-a", 100, 8000), true);
  assert.equal(tryAcquireRefreshLease(storage, "lock", "tab-b", 101, 8000), false);
  assert.deepEqual(readRefreshLease(storage, "lock"), { owner: "tab-a", expiresAt: 8100 });
  assert.equal(tryAcquireRefreshLease(storage, "lock", "tab-b", 8200, 8000), true);
});

test("refresh lease release cannot remove another owner's lease", () => {
  const storage = new MemoryStorage();
  assert.equal(tryAcquireRefreshLease(storage, "lock", "tab-a", 100, 8000), true);
  releaseRefreshLease(storage, "lock", "tab-b");
  assert.equal(readRefreshLease(storage, "lock")?.owner, "tab-a");
  releaseRefreshLease(storage, "lock", "tab-a");
  assert.equal(readRefreshLease(storage, "lock"), null);
});
