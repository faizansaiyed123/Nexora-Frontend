# Nexora end-to-end browser journey

The browser-to-API-to-PostgreSQL runner lives in the paired [backend repository](https://github.com/faizansaiyed123/Nexora-backend/tree/main/tests/e2e).

The full-stack GitHub Actions workflow checks out both repositories, provisions a disposable PostgreSQL and Redis environment, starts FastAPI plus the built frontend, and uses Playwright to follow the visible product journey. Email verification and password-reset messages go to a local STARTTLS capture inbox. The suite does not mock Nexora API responses.

The runner captures screenshots under `docs/testing/visuals/` and writes `postgres-evidence.json` only after independent database queries confirm the key records and state transitions. The walkthrough uses a controlled public HTML source for deterministic price movement; it is not a statement of live retail prices or production deployment certification.

To run the browser journey locally, follow the setup and environment values in `.github/workflows/ci.yml` and execute `uv run --python 3.12 python tests/e2e/run_ui_journey.py` from the backend repository after starting the API, built frontend, PostgreSQL, Redis, and isolated STARTTLS inbox.
