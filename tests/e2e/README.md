# Nexora end-to-end browser journey

The canonical full-stack browser runner is in the paired [backend repository](https://github.com/faizansaiyed123/Nexora-backend/blob/main/tests/browser_walkthrough.py). The workflow checks out both repositories, starts the built React frontend and FastAPI service, applies PostgreSQL migrations, and connects real Redis and PostgreSQL services. It does not stub or intercept Nexora API responses.

Account verification, resend verification, and password recovery use a local STARTTLS email capture inbox. The browser journey follows the visible product UI, checks actual HTTP results, and reads the important records back from PostgreSQL. It also verifies tenant boundaries and role permissions with persisted users and issued access tokens.

The security-sensitive account paths include invalid verification-token rejection and replaying a consumed verification or password-reset token. A reused one-time token must fail without changing the verified account state or replacing the successfully reset password.

The workflow captures 67 visitor-oriented screenshots in `docs/testing/visuals/`, validates that every documented image exists, writes `postgres-evidence.json` from independent database queries, synchronizes the same images into `docs/walkthrough/screenshots/`, and publishes the visitor-facing [product walkthrough](https://github.com/faizansaiyed123/Nexora-Frontend/blob/main/docs/walkthrough/README.md) only after the full journey succeeds.

The source-management journey starts with `HTTP_FAST`, changes the existing source to `PLAYWRIGHT_BROWSER` in the visible edit form, and verifies the saved collection method plus `requires_javascript` setting through fresh API reads. Before the product flow, a renderer probe checks the returned document for the JavaScript-updated price marker; the browser test does not accept a successful HTTP fetch of only the static HTML as proof of JavaScript rendering. It then collects a controlled page whose initial HTML advertises `$349.99` while page JavaScript changes the rendered product price to `$399.99`; the observation must contain the rendered value, not the initial value. A later collection returns `$349.99`, allowing the real collection pipeline to update the snapshot and trigger the price-drop alert. The discovery and collection pages are fetched by Nexora's actual backend code, not fake API responses. Their example prices are controlled fixtures, not current market offers. The browser run also checks that confidence `0` survives a match edit and database read-back. The walkthrough is product documentation, not a certification of the production deployment.

## Local execution

Run from the backend repository after setting the environment and starting PostgreSQL, Redis, the FastAPI service, the built frontend, and the isolated STARTTLS inbox as shown in the frontend repository's `.github/workflows/ci.yml`:

```bash
uv run --python 3.12 playwright install chromium
uv run --python 3.12 python tests/browser_walkthrough.py
```

Set `NEXORA_SCREENSHOT_DIR` to the frontend repository's `docs/testing/visuals` directory to write images in the same location used by CI. The browser journey finishes only after its PostgreSQL read-back assertions succeed.


Collection and discovery use controlled product HTML served only inside CI. The visitor screenshots display the reserved example hostname `retail.northstar.example` rather than a loopback address; CI maps that host to the isolated fixture server. The backend permits the fixed fixture paths only with its test-only environment setting, which production rejects.
