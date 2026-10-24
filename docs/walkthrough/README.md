# Nexora — Visual Product Walkthrough

Nexora brings catalogue management, competitor coverage, price collection, website discovery, and market alerts into one workspace. This guide follows a sample Northstar team from workspace setup through a connected market-intelligence journey, including account security, administration, and organization boundaries.

The retail names and prices are controlled examples that make the price-comparison journey easy to follow; they are not presented as current market offers. The guide follows the same connected workflow a team uses—from creating a private workspace, through competitor collection and alert review, to account and tenant controls. It describes the product experience and does not certify a separately deployed production environment.

## 1. Start a workspace

An organization creates a private workspace, verifies its email, and signs in. Account recovery follows the same one-time-link pattern so access remains tied to the account owner.

![Nexora public homepage](screenshots/00-public-homepage.png)

![Create a workspace](screenshots/01-registration-form.png)

![Verification message sent](screenshots/02-verification-email-sent.png)

![Request another verification message](screenshots/02b-verification-email-resent.png)

![Open the verification link](screenshots/03-email-verification-page.png)

![Email address verified](screenshots/04-email-verified.png)

![Sign in to the workspace](screenshots/05-login.png)

![Your workspace overview](screenshots/06-dashboard-starting-workspace.png)

## 2. Connect the market

Competitors describe the businesses being benchmarked. A collection source identifies the public page to read, with request limits, retries, headers, extraction selectors, and optional JavaScript rendering.

![Competitor directory](screenshots/07-competitors.png)

![A competitor added to the workspace](screenshots/08-competitor-created.png)

![Duplicate competitor domains are rejected](screenshots/09-duplicate-domain-protection.png)

![Add a collection source](screenshots/10-source-form.png)

![Connected source](screenshots/11-source-created.png)

![Source request and extraction settings](screenshots/12-source-settings.png)

![Saved source configuration](screenshots/13-source-settings-saved.png)

![JavaScript rendering option](screenshots/13b-source-js-rendering-enabled.png)

## 3. Build and maintain the catalogue

Offerings carry the attributes used for comparison: name, type, SKU, price, currency, market, category, and flexible fields. Catalogue management includes record detail, monitoring, bulk import/export, filters, pagination, and archive workflows.

![Create an offering](screenshots/14-offering-form.png)

![Offering added to the catalogue](screenshots/15-catalog-offering-created.png)

![Offering details and history](screenshots/16-offering-details.png)

![Turn monitoring on or off](screenshots/17-monitoring-controls.png)

![Dynamic field definitions](screenshots/18-dynamic-fields.png)

![Define a catalogue field](screenshots/19-dynamic-field-form.png)

![Saved dynamic field](screenshots/20-dynamic-field-created.png)

![Import multiple catalogue records](screenshots/21-bulk-import-form.png)

![Imported catalogue items](screenshots/22-bulk-import-results.png)

![Row-level import feedback](screenshots/22b-bulk-import-row-errors.png)

![Export data and bulk-archive selected offerings](screenshots/23-catalog-import-export-archive.png)

![Archive an individual offering](screenshots/23b-single-offering-archived.png)

![Navigate through catalogue pages](screenshots/23c-catalog-pagination.png)

![Filter offerings by type](screenshots/23d-catalog-type-filter.png)

## 4. Map offerings to competitor listings

An offering match connects an internal catalogue item to a particular competitor URL. Each collection creates an observation and updates the current snapshot, giving the team a history of the market price it has seen.

![Map an offering to a competitor URL](screenshots/24-offering-match-form.png)

![Saved offering match](screenshots/25-offering-match-created.png)

![Add an alternate match](screenshots/25b-temporary-match-created.png)

![Remove an alternate match](screenshots/25c-temporary-match-deleted.png)

![First collected price observation](screenshots/26-first-price-observation.png)

![Dashboard with market data](screenshots/27-dashboard-with-market-data.png)

## 5. Turn market movement into an alert

Alert rules can watch for price changes, percentage drops, undercut thresholds, stock changes, and source-health events. A later lower-price observation creates a persistent alert that the team can review and mark as read. Repeated source failures are surfaced through circuit-breaker status.

![Configure a price-drop rule](screenshots/28-alert-rule-form.png)

![Saved price alert](screenshots/29-alert-rule-created.png)

![Configure a source-health alert](screenshots/29b-circuit-breaker-rule-form.png)

![A source is temporarily paused after repeated failures](screenshots/29c-source-circuit-open.png)

![Source-health alert in the event log](screenshots/29d-circuit-breaker-alert.png)

![Price-drop alert reviewed and marked as read](screenshots/30-alert-generated-and-read.png)

## 6. Follow execution and discover offerings

The job history connects collection activity to its outcome. Website discovery follows structured product information from public pages, adds a new catalogue item when appropriate, and updates the matching record when the same offering is found again. Private-network destinations are not accepted as discovery targets.

![Collection job history](screenshots/31-collection-job-history.png)

![Details of a collection run](screenshots/32-collection-job-details.png)

![Private network target rejected](screenshots/33-private-target-blocked.png)

![A discovered product added to the catalogue](screenshots/34-discovery-product-created.png)

![Repeat discovery updates the matching item](screenshots/35-discovery-update-history.png)

## 7. Manage workspace and account settings

Workspace owners can maintain organization details and change a password from an authenticated session. Password recovery sends a time-limited link and returns the person to the same workspace after sign-in.

![Workspace and account settings](screenshots/36-workspace-settings.png)

![Updated workspace profile](screenshots/37-workspace-profile-saved.png)

![Password changed from settings](screenshots/38-password-changed.png)

![Request a password reset](screenshots/39-password-reset-requested.png)

![Choose a new password](screenshots/40-password-reset-form.png)

![Password reset completed](screenshots/41-password-reset-complete.png)

![Return to the workspace](screenshots/42-dashboard-after-reset.png)

## 8. Role permissions, tenant isolation, and mobile

The workspace changes available controls according to the signed-in role. Analysts can work with intelligence, viewers retain read-only access, and authorized super administrators can perform management actions. A second organization receives its own empty data boundary, while the public homepage and authenticated workspace adapt to a phone-sized screen.

![Analyst workspace](screenshots/43-analyst-workspace.png)

![Viewer read-only workspace](screenshots/44-viewer-read-only-workspace.png)

![Super Admin workspace](screenshots/45-super-admin-workspace.png)

![Super Admin adds a collection source](screenshots/45b-super-admin-source-created.png)

![Super Admin removes the temporary source](screenshots/45c-super-admin-source-deleted.png)

![Super Admin removes a competitor](screenshots/45d-super-admin-competitor-deleted.png)

![Super Admin removes an alert rule](screenshots/45e-super-admin-alert-rule-deleted.png)

![A separate organization's dashboard](screenshots/46-isolated-tenant-dashboard.png)

![The separate competitor directory starts empty](screenshots/47-isolated-tenant-competitors.png)

![The separate catalogue starts empty](screenshots/48-isolated-tenant-catalog.png)

![The separate alert workspace starts empty](screenshots/49-isolated-tenant-alerts.png)

![Authenticated workspace on mobile](screenshots/50-mobile-dashboard.png)

![Public homepage on mobile](screenshots/51-mobile-homepage.png)
