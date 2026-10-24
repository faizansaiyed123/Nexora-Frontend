# Nexora — Product Walkthrough

Nexora brings a team's product catalogue, competitor coverage, source configuration, collection activity, discovery, and market alerts into one private workspace.

Use this walkthrough to follow the product from first account access through a complete pricing signal. The screenshots show the real application screens connected to a running API and a dedicated example workspace.

## 1. Start with a workspace

Create an organization workspace, verify the work email, sign in, and arrive at a dashboard scoped to that organization. Workspace boundaries and role-aware access keep each team's catalogue and competitive intelligence separate.

![Nexora public homepage](screenshots/01-public-home.png)

![Workspace registration](screenshots/02-registration-form.png)

![Verification email confirmation](screenshots/03-verification-email-sent.png)

![Email verification page](screenshots/04-email-verification-page.png)

![Email verification completed](screenshots/05-email-verified.png)

![New workspace dashboard](screenshots/06-empty-dashboard.png)

## 2. Build market coverage

Register the competitors to follow, then connect the public pages that contain their commercial information. Each source can carry its own collection method, request limits, timeout, retry policy, headers, and extraction selectors.

![Competitor directory](screenshots/07-competitors.png)

![Competitor added to the workspace](screenshots/08-competitor-created.png)

![Duplicate-domain protection](screenshots/09-duplicate-domain-guard.png)

![Source setup](screenshots/10-source-form.png)

![Source request and extraction settings](screenshots/11-source-configuration.png)

![Configured source in the workspace](screenshots/12-source-configured.png)

## 3. Curate the catalogue

Keep an internal catalogue with product identifiers, market, currency, price, product pages, and domain-specific attributes. Open a product for details and history, pause or resume monitoring, define comparable dynamic fields, or bulk-import and export the catalogue.

![Offering details form](screenshots/13-offering-form.png)

![Product in the catalogue](screenshots/14-catalog-created.png)

![Offering detail and market context](screenshots/15-offering-detail.png)

![Monitoring enabled](screenshots/16-monitoring-enabled.png)

![Dynamic catalogue fields](screenshots/17-dynamic-fields.png)

![A dynamic field added](screenshots/18-dynamic-field-created.png)

![Bulk catalogue import](screenshots/19-bulk-import-form.png)

![Catalogue import, export and archive actions](screenshots/20-catalog-import-export-archive.png)

## 4. Connect products to competitor pages

An offering match links an internal catalogue entry to a specific competitor page. It gives the collection service a clear target and allows Nexora to build observations, a latest snapshot, and a price history over time.

![Map an internal offering to a source](screenshots/21-offering-match-form.png)

![Saved offering match](screenshots/22-offering-match-created.png)

![First collected price observation](screenshots/23-first-price-observation.png)

## 5. Turn movement into an alert

Create a rule for a price drop, price change, stock change, or source health event. When a later collection crosses the configured threshold, Nexora stores the alert, makes it available in the workspace, and queues the configured notification channel.

![Create a price-drop alert](screenshots/24-alert-rule-form.png)

![Saved alert rule](screenshots/25-alert-rule-created.png)

![Alert generated from a price movement](screenshots/26-alert-triggered-and-read.png)

## 6. Understand execution and discover new offerings

The Jobs area shows collection and discovery activity with status, processing counts, failure context, and job details. Website discovery checks public pages for structured product evidence and merges matching items into the catalogue rather than creating a duplicate on every run.

![Collection job history](screenshots/27-job-history.png)

![Collection job detail](screenshots/28-job-detail.png)

![Nexora blocks private or loopback discovery targets](screenshots/29-private-target-blocked.png)

![Discovered offering from structured product information](screenshots/30-discovery-product-created.png)

![Discovery updates the existing matching offering](screenshots/31-discovery-upsert.png)

## 7. Workspace, account security, and team access

Update the organization profile, change or recover a password through one-time email links, and use the appropriate workspace role for each task. Administrators manage configuration, analysts can review intelligence and run discovery, and viewer accounts remain read-only.

![Workspace settings](screenshots/32-workspace-settings.png)

![Updated workspace profile and password](screenshots/33-workspace-profile-and-password.png)

![Password reset requested](screenshots/34-password-reset-requested.png)

![Password reset completed](screenshots/35-password-reset-complete.png)

![Dashboard after account recovery](screenshots/36-dashboard-after-reset.png)

![Analyst access](screenshots/37-analyst-permissions.png)

![Viewer read-only access](screenshots/38-viewer-read-only.png)

![Nexora on a narrow mobile viewport](screenshots/39-mobile-home.png)

## Notes about the example journey

The price-change example uses structured retail product information hosted as a public HTML page so the extraction path remains repeatable. The UI actions, backend HTTP requests, database writes, alert generation, and email delivery still use the actual Nexora application services; the API responses are not substituted with browser mocks. Your own workspace results depend on the sources, catalogue, market, and access permissions you configure.
