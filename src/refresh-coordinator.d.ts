declare module "./refresh-coordinator.mjs" {
  export function withStorageRefreshLock<T>(
    fn: () => Promise<T>,
    options?: {
      storage?: Storage;
      owner?: string;
      now?: () => number;
      sleep?: (ms: number) => Promise<void>;
      leaseMs?: number;
    },
  ): Promise<T>;
}
