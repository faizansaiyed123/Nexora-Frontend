import { useEffect, useState } from "react";

const STORAGE_KEY = "nexora.rate-limits.v1";
const CHANGE_EVENT = "nexora:rate-limit-change";
const memoryDeadlines = new Map<string, number>();

type DeadlineMap = Record<string, number>;

function getStorage(): Storage | undefined {
  if (typeof window === "undefined") return undefined;
  try {
    return window.localStorage;
  } catch {
    return undefined;
  }
}

export function normalizeRateLimitKey(path: string): string {
  const pathname = path.split("?")[0].replace(/\/+$/, "");
  return pathname || "/";
}

function readDeadlines(): DeadlineMap {
  const now = Date.now();
  const result: DeadlineMap = {};
  for (const [key, deadline] of memoryDeadlines) {
    if (deadline > now) result[key] = deadline;
    else memoryDeadlines.delete(key);
  }

  const storage = getStorage();
  if (storage) {
    try {
      const raw = storage.getItem(STORAGE_KEY);
      if (raw) {
        const stored = JSON.parse(raw) as Record<string, unknown>;
        for (const [key, value] of Object.entries(stored)) {
          if (typeof value === "number" && Number.isFinite(value) && value > now) {
            result[key] = Math.max(result[key] ?? 0, value);
          }
        }
      }
    } catch {
    }
  }
  return result;
}

function writeDeadlines(deadlines: DeadlineMap): void {
  memoryDeadlines.clear();
  for (const [key, deadline] of Object.entries(deadlines)) memoryDeadlines.set(key, deadline);
  const storage = getStorage();
  if (storage) {
    try {
      storage.setItem(STORAGE_KEY, JSON.stringify(deadlines));
    } catch {
    }
  }
}

export function getRateLimitRemaining(path: string): number {
  const key = normalizeRateLimitKey(path);
  const deadline = readDeadlines()[key] ?? 0;
  return Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
}

export function reportRateLimit(path: string, retryAfterSeconds: number): void {
  const key = normalizeRateLimitKey(path);
  const seconds = Number.isFinite(retryAfterSeconds)
    ? Math.max(1, Math.ceil(retryAfterSeconds))
    : 60;
  const deadlines = readDeadlines();
  deadlines[key] = Math.max(deadlines[key] ?? 0, Date.now() + seconds * 1000);
  writeDeadlines(deadlines);
  if (typeof window !== "undefined") {
    window.dispatchEvent(new Event(CHANGE_EVENT));
  }
}

export function formatRateLimitCountdown(totalSeconds: number): string {
  const seconds = Math.max(0, Math.ceil(totalSeconds));
  const minutes = Math.floor(seconds / 60);
  const remainder = seconds % 60;
  return minutes > 0
    ? `${String(minutes).padStart(2, "0")}:${String(remainder).padStart(2, "0")}`
    : `00:${String(remainder).padStart(2, "0")}`;
}

export function useRateLimitCountdown(path?: string): number {
  const key = path ? normalizeRateLimitKey(path) : "";
  const [remaining, setRemaining] = useState(() => key ? getRateLimitRemaining(key) : 0);

  useEffect(() => {
    if (!key) {
      setRemaining(0);
      return;
    }
    const update = () => setRemaining(getRateLimitRemaining(key));
    const onStorage = (event: StorageEvent) => {
      if (event.key === STORAGE_KEY || event.key === null) update();
    };

    update();
    window.addEventListener(CHANGE_EVENT, update);
    window.addEventListener("storage", onStorage);
    const timer = window.setInterval(update, 250);
    return () => {
      window.clearInterval(timer);
      window.removeEventListener(CHANGE_EVENT, update);
      window.removeEventListener("storage", onStorage);
    };
  }, [key]);

  return remaining;
}
