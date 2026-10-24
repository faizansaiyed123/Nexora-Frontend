# Nexora — Product Walkthrough

Nexora is a multi-tenant competitive price-intelligence workspace. It brings a company's tracked catalog together with competitor websites, collection sources, product matching, observed prices, discovery runs and alert history.

This guide follows a realistic retail workflow from workspace creation to a competitor price change. The screenshots are captured from the running React application; interactions call the FastAPI service, and write/read steps use the application's PostgreSQL database.

## 1. Create a private workspace

Start at the public homepage, register a workspace, verify the email using its one-time link, and sign in. A new workspace begins with its own tenant boundary and an empty catalog.

![Nexora public homepage](screenshots/00-public-homepage.png)

![Workspace registration](screenshots/01-registration-form.png)

![Verification email sent](screenshots/02-verification-email-sent.png)

![Email verification page](screenshots/03-email-verification-page.png)

![Email verification complete](screenshots/04-email-verified.png)

![Sign in](screenshots/05-login.png)

![New workspace dashboard](screenshots/06-dashboard-empty-workspace.png)

## 2. Map the market

Create a competitor, connect an official product source, and configure collection behavior such as request rate, retries, headers, and extraction selectors. Duplicate domains are rejected within the same workspace.

![Competitor directory](screenshots/07-competitors-empty.png)

![Competitor added](screenshots/08-competitor-created.png)

![Duplicate competitor domain rejected](screenshots/09-duplicate-domain-rejected.png)

![Add collection source](screenshots/10-source-creation-form.png)

![Configured source directory](screenshots/11-sources-created.png)

![Source configuration](screenshots/12-source-configuration.png)

![Saved source configuration](screenshots/13-source-configuration-saved.png)

## 3. Build and govern the catalog

Create a catalog offering with a SKU, market, currency, price, category and structured attributes. Open the offering detail to see its competitive context and price history, update the price, and pause or resume monitoring. Dynamic fields extend the catalog schema; bulk import, CSV/JSON export, filters and soft archive help manage larger catalogs.

![Create catalog offering](screenshots/14-offering-creation-form.png)

![Offering created](screenshots/15-catalog-offering-created.png)

![Offering details and history](screenshots/16-offering-detail-and-history.png)

![Monitoring enabled](screenshots/17-catalog-monitoring-active.png)

![Dynamic field definitions](screenshots/18-dynamic-fields.png)

![Create dynamic field](screenshots/19-dynamic-field-form.png)

![Dynamic field added](screenshots/20-dynamic-field-created.png)

![Bulk catalog import](screenshots/21-bulk-import-form.png)

![Imported catalog entries](screenshots/22-bulk-imported-catalog.png)

![Catalog export and archive](screenshots/23-catalog-import-export-and-archive.png)

## 4. Collect competitor prices

Connect the internal offering to a precise competitor listing. Nexora fetches the public page and records an observation and current snapshot. A second collection uses a lower listed price, so the comparison and alert are driven by changing page data rather than a fabricated API response.

![Map an offering to a competitor URL](screenshots/24-offering-match-form.png)

![Offering match created](screenshots/25-offering-match-created.png)

![First price observation](screenshots/26-first-price-observation.png)

## 5. Turn market movement into a signal

Set a percentage-drop threshold for the offering. When the next observation records a 12.5% price decrease, Nexora records the alert, places an email in its transactional notification outbox, and presents the event in the alert history. Opening the event persists its read state.

![Create a price-drop alert](screenshots/27-alert-rule-form.png)

![Price-drop alert configured](screenshots/28-alert-rule-created.png)

![Generated alert and its read state](screenshots/29-alert-generated-and-read.png)

## 6. Review activity and discover new offerings

Collection jobs preserve execution outcome and diagnostic context. Website discovery rejects private-network destinations, scans structured product data from a public page, adds evidence-backed catalog entries, and updates an existing entry on a repeated run rather than creating a duplicate.

![Collection job history](screenshots/30-collection-job-history.png)

![Collection job detail](screenshots/31-collection-job-detail.png)

![Private-network discovery target blocked](screenshots/32-private-target-blocked.png)

![Discovered offering added](screenshots/33-discovery-product-created.png)

![Discovery upsert and history](screenshots/34-discovery-upsert-history.png)

## 7. Workspace identity and account security

Workspace settings store organization details. Changing the password invalidates the old credential; password recovery issues a one-time link, allows a new password to be set, and returns the user to the workspace.

![Workspace settings](screenshots/35-workspace-settings.png)

![Updated workspace profile](screenshots/36-workspace-profile-updated.png)

![Password changed](screenshots/37-password-changed.png)

![Password reset requested](screenshots/38-password-reset-requested.png)

![Password reset form](screenshots/39-password-reset-form.png)

![Password reset completed](screenshots/40-password-reset-complete.png)

![Dashboard after account recovery](screenshots/41-dashboard-after-password-reset.png)

## 8. Role-aware access

The same persisted workspace supports different roles. Analysts can inspect and analyze catalog data and run discovery, while viewers have read access without catalog-management controls. Backend authorization enforces write permissions independently of the controls shown in the browser.

![Analyst workspace](screenshots/42-analyst-workspace.png)

![Viewer read-only workspace](screenshots/43-viewer-read-only-workspace.png)

## 9. Responsive entry point

The public site remains usable on a narrow mobile viewport without horizontal overflow.

![Mobile homepage](screenshots/44-mobile-homepage.png)

## What this walkthrough demonstrates

The browser journey connects real UI actions to HTTP endpoints and persisted PostgreSQL records, including collection history, catalog discovery, alert read state, SMTP verification/recovery links and role-aware access.

The walkthrough is produced against a disposable PostgreSQL database, isolated Redis, and a local STARTTLS SMTP sink. It does not write to a production workspace or certify the live production deployment.
