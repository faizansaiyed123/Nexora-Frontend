const value = process.env.VITE_API_URL || "";
const mode = process.env.VITE_API_BUILD_MODE || "production";

if (!value) {
  if (mode === "development") process.exit(0);
  console.error("VITE_API_URL is required for production builds.");
  process.exit(1);
}

let parsed;
try {
  parsed = new URL(value);
} catch {
  console.error("VITE_API_URL must be an absolute HTTP(S) URL.");
  process.exit(1);
}

if (!["http:", "https:"].includes(parsed.protocol)) {
  console.error("VITE_API_URL must use HTTP or HTTPS.");
  process.exit(1);
}

const blockedHosts = new Set(["localhost", "127.0.0.1", "::1"]);
if (mode === "production" && blockedHosts.has(parsed.hostname.toLowerCase())) {
  console.error("Production builds may not use localhost/loopback as VITE_API_URL.");
  process.exit(1);
}
