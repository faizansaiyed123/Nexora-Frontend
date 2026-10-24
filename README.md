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
