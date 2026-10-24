# Nexora | Product Walkthrough

Nexora brings product catalog management, competitor coverage, price collection, website discovery, and market alerts into one workspace. This walkthrough follows a Northstar market-intelligence team from creating its workspace to collecting competitor prices, reacting to a change, and keeping access separated across organizations and roles.

The review workspace and named catalogue records are illustrative. Account and workspace actions flow through the application API and a disposable PostgreSQL database; the price and discovery steps use structured product pages that can be fetched repeatedly. This walkthrough explains the product and does not certify a production deployment.

## 1. Create and secure a workspace

An organization starts at the public homepage, creates a workspace, verifies its email, and signs in. Verification and password recovery use one-time links delivered to the account's email address.

![Nexora public homepage](screenshots/00-public-homepage.png)

![Create a workspace](screenshots/01-registration-form.png)

![Verification message sent](screenshots/02-verification-email-sent.png)

![Email verification page](screenshots/03-email-verification-page.png)

![Email verified](screenshots/04-email-verified.png)

![Sign in to Nexora](screenshots/05-login.png)

![Starting workspace dashboard](screenshots/06-dashboard-starting-workspace.png)

## 2. Define the market and data sources

Competitors represent the businesses to benchmark. A source identifies the public page Nexora should read. Duplicate competitor domains are prevented, and source settings control request rate, delay, timeout, retry behavior, headers, extraction selectors, and JavaScript rendering.

![Competitor directory](screenshots/07-competitors.png)

![Competitor created](screenshots/08-competitor-created.png)

![Duplicate domain protection](screenshots/09-duplicate-domain-protection.png)

![Create a collection source](screenshots/10-source-form.png)

![Source connected](screenshots/11-source-created.png)

![Source configuration](screenshots/12-source-settings.png)

![Saved source configuration](screenshots/13-source-settings-saved.png)

![JavaScript rendering option](screenshots/13b-source-js-rendering-enabled.png)

## 3. Build and maintain the product catalog

Offerings carry the information needed for comparison: name, type, SKU, price, currency, market, category, description, and flexible attributes. The catalog supports editing, detail/history views, monitoring controls, custom field definitions, bulk import, row-level feedback, export, archive, filtering, and pagination.

![Create an offering](screenshots/14-offering-form.png)

![Offering added to the catalog](screenshots/15-catalog-offering-created.png)

![Offering detail and history](screenshots/16-offering-details.png)

![Monitoring controls](screenshots/17-monitoring-controls.png)

![Dynamic field definitions](screenshots/18-dynamic-fields.png)

![Create a dynamic field](screenshots/19-dynamic-field-form.png)

![Dynamic field saved](screenshots/20-dynamic-field-created.png)

![Bulk catalog import](screenshots/21-bulk-import-form.png)

![Imported catalog records](screenshots/22-bulk-import-results.png)

![Row-level feedback for a rejected import record](screenshots/22b-bulk-import-row-errors.png)

![Export the catalog and bulk-archive a selection](screenshots/23-catalog-import-export-archive.png)

![Archive one offering](screenshots/23b-single-offering-archived.png)

![Navigate across catalog pages](screenshots/23c-catalog-pagination.png)

![Filter offerings by type](screenshots/23d-catalog-type-filter.png)

## 4. Connect an offering to a competitor listing

A match connects an internal offering with a specific competitor source URL. Collecting that listing fetches the page, extracts the observed price and availability, and writes an observation and snapshot that can be reviewed in the offering history and dashboard.

![Map an offering to a competitor listing](screenshots/24-offering-match-form.png)

![Offering match created](screenshots/25-offering-match-created.png)

![First collected price observation](screenshots/26-first-price-observation.png)

![Dashboard with market data](screenshots/27-dashboard-with-market-data.png)

## 5. Turn market movement into an alert

Alert rules scope a signal to one offering or the wider catalog. When a later collection sees the example price move from $399.99 to $349.99, the price-drop rule records the event and queues a notification. The event can be reviewed and marked as read.

![Configure a price-drop rule](screenshots/28-alert-rule-form.png)

![Saved price-drop rule](screenshots/29-alert-rule-created.png)

![Price-drop alert in the event log](screenshots/30-alert-generated-and-read.png)

## 6. Monitor source health and circuit breaking

A source that repeatedly fails is opened by the circuit breaker to stop further requests during its cooldown. The source list exposes the health and circuit states, and an operational alert records the transition so the team can investigate rather than repeatedly retry an unavailable endpoint.

![Configure a source circuit-breaker alert](screenshots/29b-circuit-breaker-rule-form.png)

![Source circuit open after repeated failures](screenshots/29c-source-circuit-open.png)

![Circuit-breaker alert in the event log](screenshots/29d-circuit-breaker-alert.png)

## 7. Follow execution and discover additional offerings

Jobs exposes collection history and run details. Website discovery extracts structured public product information, merges a matching offering when a product is found again, and rejects private-network targets rather than crawling them.

![Collection job history](screenshots/31-collection-job-history.png)

![Collection job details](screenshots/32-collection-job-details.png)

![Private network target rejected](screenshots/33-private-target-blocked.png)

![Product discovered and added to the catalog](screenshots/34-discovery-product-created.png)

![Repeat discovery updates the matching record](screenshots/35-discovery-update-history.png)

## 8. Keep workspace and account controls current

Workspace owners can update organization details and change the account password. Password recovery sends a one-time reset link, invalidates old credentials, and returns the user to the same workspace after sign-in.

![Workspace and account settings](screenshots/36-workspace-settings.png)

![Workspace profile updated](screenshots/37-workspace-profile-saved.png)

![Password changed](screenshots/38-password-changed.png)

![Password reset requested](screenshots/39-password-reset-requested.png)

![Enter a new password](screenshots/40-password-reset-form.png)

![Password reset completed](screenshots/41-password-reset-complete.png)

![Return to the workspace](screenshots/42-dashboard-after-reset.png)

## 9. Match capabilities to the user's role

Analysts can work with intelligence, inspect records, and start discovery without receiving organization-management permissions. Viewers can read workspace data while write actions remain unavailable. Super Admin access is exercised separately and can perform an authorized management action.

![Analyst workspace](screenshots/43-analyst-workspace.png)

![Viewer read-only workspace](screenshots/44-viewer-read-only-workspace.png)

![Super Admin management workspace](screenshots/45-super-admin-workspace.png)

## 10. Keep organizations isolated and the interface responsive

A separately registered organization receives a different tenant boundary. Its dashboard, competitors, catalog, and alerts start empty, and it cannot fetch another organization's records by ID. Nexora also adapts to phone-sized viewports for both the authenticated workspace and public homepage.

![Second organization's empty dashboard](screenshots/46-isolated-tenant-dashboard.png)

![Second organization's competitor directory](screenshots/47-isolated-tenant-competitors.png)

![Second organization's empty catalog](screenshots/48-isolated-tenant-catalog.png)

![Second organization's alert view](screenshots/49-isolated-tenant-alerts.png)

![Nexora dashboard at a mobile viewport](screenshots/50-mobile-dashboard.png)

![Nexora public homepage at a mobile viewport](screenshots/51-mobile-homepage.png)
