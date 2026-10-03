const LOCK_KEY = "nexora.refresh.lock";
const DEFAULT_LEASE_MS = 15000;

export function tryAcquireRefreshLease(storage, owner, now = Date.now(), leaseMs = DEFAULT_LEASE_MS) {
  const raw = storage.getItem(LOCK_KEY);
  if (raw) {
    try {
      const current = JSON.parse(raw);
      if (current.owner !== owner && Number(current.expiresAt) > now) return false;
    } catch {
      storage.removeItem(LOCK_KEY);
    }
  }
  storage.setItem(LOCK_KEY, JSON.stringify({ owner, expiresAt: now + leaseMs }));
  const verify = storage.getItem(LOCK_KEY);
  try {
    return Boolean(verify && JSON.parse(verify).owner === owner);
  } catch {
    return false;
  }
}

export function releaseRefreshLease(storage, owner) {
  const raw = storage.getItem(LOCK_KEY);
  if (!raw) return;
  try {
    if (JSON.parse(raw).owner === owner) storage.removeItem(LOCK_KEY);
  } catch {
    storage.removeItem(LOCK_KEY);
  }
}

export function ownsRefreshLease(storage, owner, now = Date.now()) {
  const raw = storage.getItem(LOCK_KEY);
  if (!raw) return false;
  try {
    const current = JSON.parse(raw);
    return current.owner === owner && Number(current.expiresAt) > now;
  } catch {
    return false;
  }
}

export async function withStorageRefreshLock(fn, {
  storage,
  owner,
  now = () => Date.now(),
  sleep = ms => new Promise(resolve => setTimeout(resolve, ms)),
  leaseMs = DEFAULT_LEASE_MS,
} = {}) {
  const effectiveStorage = storage || globalThis.localStorage;
  const effectiveOwner = owner || `${now()}:${Math.random()}`;
  for (let attempt = 0; attempt < 80; attempt += 1) {
    if (tryAcquireRefreshLease(effectiveStorage, effectiveOwner, now(), leaseMs)) {
      await sleep(50);
      if (!ownsRefreshLease(effectiveStorage, effectiveOwner, now())) continue;
      try {
        return await fn();
      } finally {
        releaseRefreshLease(effectiveStorage, effectiveOwner);
      }
    }
    await sleep(Math.min(250, 25 + attempt * 5));
  }
  throw new Error("Could not acquire refresh coordination lock.");
}
