# Nexora Frontend

Nexora is a B2B competitive price-intelligence workspace. This frontend provides authentication, tenant-aware catalog management, competitor/source administration, product matching, website discovery, live collection runs, job visibility, alerts, and account settings.

## Run locally

```bash
npm install
cp .env.example .env
npm run dev
```

Set `VITE_API_URL` to the Nexora backend origin, for example `http://localhost:8000`.

The production build is served as a static SPA and is container-ready through the included Dockerfile. Pass `--build-arg VITE_API_URL=https://your-api.example.com` when building for production. Production builds reject missing, local, or plain-HTTP API origins; development with `npm run dev` continues to default to `http://localhost:8000` when no environment override is supplied.

## Authentication storage

The SPA currently stores the short-lived access token and rotating refresh token in `localStorage` to preserve the existing browser session architecture. This intentionally trades some XSS blast-radius resistance for the current client-only deployment model. The application avoids direct HTML injection sinks, and production Nginx applies a restrictive CSP, frame isolation, and related security headers.