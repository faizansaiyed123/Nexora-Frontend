# Nexora Product Walkthrough

Nexora brings catalogue management, competitor coverage, website discovery, collection activity and price-change alerts into one workspace. This guide follows the product from the first visit through a connected market-intelligence workflow.

All screenshots below come from the same connected application journey, using real screens and persisted workspace records.

## Start with a workspace

The public page explains the product's focus. Workspace creation and account recovery use one-time email links before account access is granted.

![Nexora public homepage](./screenshots/00-public-homepage.png)

![Create a workspace](./screenshots/01-registration-form.png)

![Verification email sent](./screenshots/02-verification-email-sent.png)

![Open the verification link](./screenshots/03-email-verification-page.png)

![Email verified](./screenshots/04-email-verified.png)

![Sign in](./screenshots/05-login.png)

## Your operating picture

The dashboard brings the workspace's tracked catalogue, competitors, connected sources and recent activity together.

![New workspace dashboard](./screenshots/06-dashboard-empty-workspace.png)

## Map the market

Competitors define the businesses being benchmarked. Sources specify the public pages Nexora can collect from, together with request limits, retries, headers and extraction settings.

![Competitor directory](./screenshots/07-competitors-empty.png)

![A competitor in the workspace](./screenshots/08-competitor-created.png)

![Duplicate competitor domain protection](./screenshots/09-duplicate-domain-rejected.png)

![New source details](./screenshots/10-source-creation-form.png)

![Connected collection source](./screenshots/11-source-created.png)

![Source request and extraction configuration](./screenshots/12-source-configuration.png)

![Saved source configuration](./screenshots/13-source-configuration-saved.png)

## Build the catalogue

The catalogue stores each offering's name, SKU, price, market, category and structured attributes. Teams can view details, update records, turn monitoring on or off, define dynamic fields, import multiple offerings, export data, and archive items without erasing the record of past work.

![Create an offering](./screenshots/14-offering-form.png)

![Offering in the catalogue](./screenshots/15-offering-created.png)

![Offering details and history](./screenshots/16-offering-detail-and-history.png)

![Monitoring controls](./screenshots/17-offering-monitoring.png)

![Dynamic field definitions](./screenshots/18-dynamic-fields.png)

![Define an additional catalogue field](./screenshots/19-dynamic-field-form.png)

![Saved dynamic field](./screenshots/20-dynamic-field-created.png)

![Bulk catalogue import](./screenshots/21-bulk-import-form.png)

![Imported catalogue items](./screenshots/22-bulk-imported-catalog.png)

![Catalogue export and archive workflow](./screenshots/23-catalog-import-export-archive.png)

## Connect an offering to the market

An offering match maps an internal catalogue record to a competitor's specific listing URL. Running a collection retrieves the current page, extracts price and availability data, and updates the observation history and current snapshot.

![Map an offering to a competitor URL](./screenshots/24-match-form.png)

![Saved offering match](./screenshots/25-match-created.png)

![First market price observation](./screenshots/26-first-price-observation.png)

## Turn market movement into a signal

Alert rules can watch for price movement at a selected threshold. When a subsequent collection records a sufficiently large decrease, Nexora creates an alert history item that the team can review and mark as read.

![Create a price-change alert](./screenshots/27-alert-rule-form.png)

![Saved price-change alert rule](./screenshots/28-alert-rule-created.png)

![Triggered alert and read state](./screenshots/29-alert-generated-and-read.png)

## Follow execution and discover new offerings

Jobs make collection activity and its outcome visible. Website discovery accepts a public URL, follows structured product evidence, and adds new offerings to the same catalogue. Private network destinations are not accepted as discovery targets.

![Collection job history](./screenshots/30-job-history.png)

![Details of a collection run](./screenshots/31-job-detail.png)

![A private destination is blocked](./screenshots/32-private-target-blocked.png)

![New offering discovered from structured product data](./screenshots/33-discovery-product-created.png)

![Discovery history and catalogue update](./screenshots/34-discovery-upsert-history.png)

## Workspace and account settings

Workspace settings keep organization identity and account security in one place. Passwords can be changed from an authenticated session or reset using a one-time email link.

![Workspace settings](./screenshots/35-settings.png)

![Updated workspace profile](./screenshots/36-settings-profile-updated.png)

![Password changed from settings](./screenshots/37-password-changed.png)

![Request a password reset](./screenshots/38-password-reset-requested.png)

![Set a new password](./screenshots/39-password-reset-form.png)

![Password reset completed](./screenshots/40-password-reset-complete.png)

![Return to the workspace](./screenshots/41-dashboard-after-reset.png)

## Access for different roles

The workspace presents different controls based on the signed-in role. Analysts can review market information and run discovery, while viewer accounts can inspect information without catalogue or competitor administration actions.

![Analyst workspace](./screenshots/42-analyst-permissions.png)

![Viewer's read-only workspace](./screenshots/43-viewer-read-only.png)

## Responsive entry point

The public homepage adapts to a narrow viewport as well as a desktop screen.

![Nexora on a mobile viewport](./screenshots/44-mobile-homepage.png)

---

Nexora's screens connect to the API and workspace database during this walkthrough. The guide illustrates the product's current flows; it is not a certification of a separately deployed production environment.
