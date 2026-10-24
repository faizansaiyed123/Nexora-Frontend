# Nexora — Visual Product Walkthrough & Full-Stack Evidence

This document follows the same screens captured by the full-stack browser journey and is also suitable for reviewers who want to understand the product. CI opens the built React frontend in a browser, calls the live FastAPI process, and verifies saved records in a disposable PostgreSQL database with Redis-backed sessions/rate limits. Email verification, password recovery and alert delivery use an isolated STARTTLS inbox.

The collection/discovery fixture pages are public structured HTML pages with deliberate values so a price change can be reproduced. The values illustrate the flow and are not claimed to be current live retail quotes. This evidence does not certify the production deployment.

[**Visitor-facing product walkthrough**](../walkthrough/README.md)

Nexora brings product catalog management, competitor coverage, price collection, website discovery, and market alerts into one workspace. This walkthrough follows a Northstar market-intelligence team from creating its workspace to collecting competitor prices, reacting to a change, and keeping access separated across organizations and roles.

The review workspace and named catalogue records are illustrative. Account and workspace actions flow through the application API and a disposable PostgreSQL database; the price and discovery steps use structured product pages that can be fetched repeatedly. This walkthrough explains the product and does not certify a production deployment.

## 1. Create and secure a workspace

An organization starts at the public homepage, creates a workspace, verifies its email, and signs in. Verification and password recovery use one-time links delivered to the account's email address.

![Nexora public homepage](visuals/00-public-homepage.png)

![Create a workspace](visuals/01-registration-form.png)

![Verification message sent](visuals/02-verification-email-sent.png)

![Verification email resent successfully](visuals/02b-verification-email-resent.png)

![Email verification page](visuals/03-email-verification-page.png)

![Email verified](visuals/04-email-verified.png)

![Sign in to Nexora](visuals/05-login.png)

![Starting workspace dashboard](visuals/06-dashboard-starting-workspace.png)

## 2. Define the market and data sources

Competitors represent the businesses to benchmark. A source identifies the public page Nexora should read. Duplicate competitor domains are prevented, and source settings control request rate, delay, timeout, retry behavior, headers, extraction selectors, and JavaScript rendering.

![Competitor directory](visuals/07-competitors.png)

![Competitor created](visuals/08-competitor-created.png)

![Duplicate domain protection](visuals/09-duplicate-domain-protection.png)

![Create a collection source](visuals/10-source-form.png)

![Source connected](visuals/11-source-created.png)

![Source configuration](visuals/12-source-settings.png)

![Saved source configuration](visuals/13-source-settings-saved.png)

![JavaScript rendering option](visuals/13b-source-js-rendering-enabled.png)

## 3. Build and maintain the product catalog

Offerings carry the information needed for comparison: name, type, SKU, price, currency, market, category, description, and flexible attributes. The catalog supports editing, detail/history views, monitoring controls, custom field definitions, bulk import, row-level feedback, export, archive, filtering, and pagination. When the catalog spans multiple pages, Next and Previous show the remaining saved records without changing catalog data.

![Create an offering](visuals/14-offering-form.png)

![Offering added to the catalog](visuals/15-catalog-offering-created.png)

![Offering detail and history](visuals/16-offering-details.png)

![Monitoring controls](visuals/17-monitoring-controls.png)

![Dynamic field definitions](visuals/18-dynamic-fields.png)

![Create a dynamic field](visuals/19-dynamic-field-form.png)

![Dynamic field saved](visuals/20-dynamic-field-created.png)

![Bulk catalog import](visuals/21-bulk-import-form.png)

![Imported catalog records](visuals/22-bulk-import-results.png)

![Row-level feedback for a rejected import record](visuals/22b-bulk-import-row-errors.png)

![Export the catalog and bulk-archive a selection](visuals/23-catalog-import-export-archive.png)

![Archive one offering](visuals/23b-single-offering-archived.png)

![Navigate across catalog pages](visuals/23c-catalog-pagination.png)

![Filter offerings by type](visuals/23d-catalog-type-filter.png)

## 4. Connect an offering to a competitor listing

A match connects an internal offering with a specific competitor source URL. Collecting that listing fetches the page, extracts the observed price and availability, and writes an observation and snapshot that can be reviewed in the offering history and dashboard.

![Map an offering to a competitor listing](visuals/24-offering-match-form.png)

![Offering match created](visuals/25-offering-match-created.png)

![Temporary alternative match created](visuals/25b-temporary-match-created.png)

![Temporary match deleted and removed from the list](visuals/25c-temporary-match-deleted.png)

![First collected price observation](visuals/26-first-price-observation.png)

![Dashboard with market data](visuals/27-dashboard-with-market-data.png)

## 5. Turn market movement into an alert

Alert rules scope a signal to one offering or the wider catalog. When a later collection sees the example price move from $399.99 to $349.99, the price-drop rule records the event and queues a notification. The event can be reviewed and marked as read.

![Configure a price-drop rule](visuals/28-alert-rule-form.png)

![Saved price-drop rule](visuals/29-alert-rule-created.png)

![Price-drop alert in the event log](visuals/30-alert-generated-and-read.png)

## 6. Monitor source health and circuit breaking

A source that repeatedly fails is opened by the circuit breaker to stop further requests during its cooldown. The source list exposes the health and circuit states, and an operational alert records the transition so the team can investigate rather than repeatedly retry an unavailable endpoint.

![Configure a source circuit-breaker alert](visuals/29b-circuit-breaker-rule-form.png)

![Source circuit open after repeated failures](visuals/29c-source-circuit-open.png)

![Circuit-breaker alert in the event log](visuals/29d-circuit-breaker-alert.png)

## 7. Follow execution and discover additional offerings

Jobs exposes collection history and run details. Website discovery extracts structured public product information, merges a matching offering when a product is found again, and rejects private-network targets rather than crawling them.

![Collection job history](visuals/31-collection-job-history.png)

![Collection job details](visuals/32-collection-job-details.png)

![Private network target rejected](visuals/33-private-target-blocked.png)

![Product discovered and added to the catalog](visuals/34-discovery-product-created.png)

![Repeat discovery updates the matching record](visuals/35-discovery-update-history.png)

## 8. Keep workspace and account controls current

Workspace owners can update organization details and change the account password. Password recovery sends a one-time reset link, invalidates old credentials, and returns the user to the same workspace after sign-in.

![Workspace and account settings](visuals/36-workspace-settings.png)

![Workspace profile updated](visuals/37-workspace-profile-saved.png)

![Password changed](visuals/38-password-changed.png)

![Password reset requested](visuals/39-password-reset-requested.png)

![Enter a new password](visuals/40-password-reset-form.png)

![Password reset completed](visuals/41-password-reset-complete.png)

![Return to the workspace](visuals/42-dashboard-after-reset.png)

## 9. Match capabilities to the user's role

Analysts can work with intelligence, inspect records, and start discovery without receiving organization-management permissions. Viewers can read workspace data while write actions remain unavailable. Super Admin access is exercised separately and can perform an authorized management action.

![Analyst workspace](visuals/43-analyst-workspace.png)

![Viewer read-only workspace](visuals/44-viewer-read-only-workspace.png)

![Super Admin management workspace](visuals/45-super-admin-workspace.png)

![Super Admin creates an additional collection source](visuals/45b-super-admin-source-created.png)

![Super Admin deletes the temporary collection source](visuals/45c-super-admin-source-deleted.png)

![Super Admin deletes the temporary competitor](visuals/45d-super-admin-competitor-deleted.png)

![Super Admin deletes the temporary alert rule](visuals/45e-super-admin-alert-rule-deleted.png)

## 10. Keep organizations isolated and the interface responsive

A separately registered organization receives a different tenant boundary. Its dashboard, competitors, catalog, and alerts start empty, and it cannot fetch another organization's records by ID. Nexora also adapts to phone-sized viewports for both the authenticated workspace and public homepage.

![Second organization's empty dashboard](visuals/46-isolated-tenant-dashboard.png)

![Second organization's competitor directory](visuals/47-isolated-tenant-competitors.png)

![Second organization's empty catalog](visuals/48-isolated-tenant-catalog.png)

![Second organization's alert view](visuals/49-isolated-tenant-alerts.png)

![Nexora dashboard at a mobile viewport](visuals/50-mobile-dashboard.png)

![Nexora public homepage at a mobile viewport](visuals/51-mobile-homepage.png)
