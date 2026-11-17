# Nexora Frontend

Nexora is a B2B competitive price-intelligence workspace. This frontend provides authentication, tenant-aware catalog management, competitor/source administration, product matching, website discovery, live collection runs, job visibility, alerts, and account settings.

## Run locally

```bash
npm install
cp .env.example .env
npm run dev
```

Set `VITE_API_URL` to the Nexora backend origin, for example `http://localhost:8000`.

The production build is served as a static SPA and is container-ready through the included Dockerfile. Pass `--build-arg VITE_API_URL=https://your-api.example.com` when building for a non-local backend.

## Product walkthrough

Explore Nexora through the [screen-by-screen visual product walkthrough](docs/walkthrough/README.md). It follows workspace setup, competitor and source configuration, catalogue management, price collection, alerts, discovery, account recovery, role permissions, tenant isolation, and mobile layouts.

The central workflow is to register an offering, link it to a competitor listing, collect a price observation, compare a later observation, and review the resulting alert and job history. Workspace owners manage the market configuration; analysts can work with intelligence and discovery; viewers have read-only access.

The walkthrough uses an example workspace and repeatable structured product pages to illustrate price movement. The displayed prices are examples, not current retail quotes.


## Recruiter demo (`demo` branch)

This branch is an isolated, browser-safe product walkthrough. It defaults to `VITE_DEMO_MODE=true`, so the frontend uses seeded in-memory Nexora data instead of PostgreSQL, Redis, Celery, SMTP, Gemini, or outbound competitor scraping. The production API path remains available by setting `VITE_DEMO_MODE=false`.

### Demo sign-in

- `demo@nexora.app` — ORG_ADMIN
- `analyst@nexora.app` — ANALYST
- `viewer@nexora.app` — VIEWER
- Any password is accepted in demo mode.

The seeded workspace covers offerings, competitors, sources, matches, collection jobs, price movement, alerts, discovery, and role-aware navigation. Running a collection changes the simulated competitor price and creates a fresh job/alert so the workflow is interactive rather than a static mockup.
