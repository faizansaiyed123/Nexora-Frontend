export type RefreshStorage = Pick<Storage, "getItem" | "setItem" | "removeItem">;

export interface RefreshLease {
  owner: string;
  expiresAt: number;
}

export function readRefreshLease(
  storage: RefreshStorage,
  key: string,
): RefreshLease | null {
  try {
    const raw = storage.getItem(key);
    if (!raw) return null;
    const value = JSON.parse(raw) as Partial<RefreshLease>;
    return typeof value.owner === "string" && typeof value.expiresAt === "number"
      ? { owner: value.owner, expiresAt: value.expiresAt }
      : null;
  } catch {
    return null;
  }
}

export function tryAcquireRefreshLease(
  storage: RefreshStorage,
  key: string,
  owner: string,
  now: number,
  leaseMs: number,
): boolean {
  const existing = readRefreshLease(storage, key);
  if (existing && existing.expiresAt > now && existing.owner !== owner) {
    return false;
  }

  try {
    storage.setItem(
      key,
      JSON.stringify({ owner, expiresAt: now + leaseMs }),
    );
    return readRefreshLease(storage, key)?.owner === owner;
  } catch {
    return false;
  }
}

export function releaseRefreshLease(
  storage: RefreshStorage,
  key: string,
  owner: string,
): void {
  try {
    if (readRefreshLease(storage, key)?.owner === owner) {
      storage.removeItem(key);
    }
  } catch {
    // Best effort. The lease will expire naturally.
  }
}
