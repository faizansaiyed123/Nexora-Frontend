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

Explore Nexora through the [screenshot-led product walkthrough](docs/walkthrough/NEXORA-PRODUCT-WALKTHROUGH.md). It follows workspace setup, competitor and source configuration, catalogue management, live price collection, alerts, website discovery, account recovery, and role-specific access.

The walkthrough includes a live public Sony Center retail page alongside controlled structured pages used to make repeatable price-change scenarios possible. Live amounts can change by market and date.
