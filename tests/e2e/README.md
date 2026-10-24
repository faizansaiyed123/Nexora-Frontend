# Nexora end-to-end browser journey

The browser-to-API-to-PostgreSQL runner lives in the paired [backend repository](https://github.com/faizansaiyed123/Nexora-backend/tree/main/tests/e2e).

The full-stack GitHub Actions workflow checks out both repositories, provisions a disposable PostgreSQL and Redis environment, starts FastAPI plus the built frontend, and uses Playwright to follow the visible product journey. Email verification and password-reset messages go to a local STARTTLS capture inbox. The suite does not mock Nexora API responses.

The runner captures screenshots under `docs/testing/visuals/` and writes `postgres-evidence.json` only after independent database queries confirm the key records and state transitions. The walkthrough uses a controlled public HTML source for deterministic price movement; it is not a statement of live retail prices or production deployment certification.

To run the browser journey locally, follow the setup and environment values in `.github/workflows/ci.yml` and execute `uv run --python 3.12 python tests/e2e/run_ui_journey.py` from the backend repository after starting the API, built frontend, PostgreSQL, Redis, and isolated STARTTLS inbox.

Each run also records browser screenshots at each workflow checkpoint and validates the final collection snapshot and notification state directly in PostgreSQL.

The automation is exercised in CI against the current backend main branch; screenshots are committed only after the connected browser journey and PostgreSQL read-back complete successfully.

The verification watcher deliberately accepts the `?token=` query string on the actual API request so it observes the real one-time-token response.

The sign-in step locates the email and current-password inputs by their explicit autocomplete purpose, avoiding ambiguity from nested password visibility controls.

The latest browser run also waits for page-level headings when the application shell repeats a title in its global header.
