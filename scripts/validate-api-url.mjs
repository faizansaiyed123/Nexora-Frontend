function validateApiUrl(value = process.env.VITE_API_URL, { production = true, allowInsecure = process.env.VITE_ALLOW_INSECURE_API === "true" } = {}) {
  const raw = String(value || "").trim();
  if (!raw) throw new Error("VITE_API_URL must be explicitly set.");
  let parsed;
  try { parsed = new URL(raw); } catch { throw new Error("VITE_API_URL must be a valid absolute URL."); }
  if (!["https:", "http:"].includes(parsed.protocol)) throw new Error("VITE_API_URL must use HTTP(S).");
  if (parsed.username || parsed.password) throw new Error("VITE_API_URL must not contain embedded credentials.");
  const host = parsed.hostname.toLowerCase();
  const forbidden = ["localhost", "127.0.0.1", "0.0.0.0", "::1", "[::1]"];
  if (production && (forbidden.includes(host) || host.endsWith(".localhost") || host.endsWith(".local") || host.endsWith(".internal"))) {
    throw new Error("Production VITE_API_URL must not point to a local/internal hostname.");
  }
  if (production && parsed.protocol === "http:" && !allowInsecure) throw new Error("Production VITE_API_URL must use HTTPS.");
  return parsed.href.replace(/\/$/, "");
}

if (import.meta.url === `file://${process.argv[1]}`) {
  validateApiUrl();
}

export { validateApiUrl };
