# Nexora — Visual Product Walkthrough

Nexora is a private competitive-intelligence workspace for teams that track their catalogue against market pricing and availability. This walkthrough follows a realistic retail-electronics journey from account setup to a price signal that deserves a decision.

The examples use a disposable workspace and public product-page fixtures with structured retail data. The screens follow actions taken through the Nexora interface, connected to the real API and PostgreSQL in an isolated environment. No production account, database, or customer data is used.

## Start with a private workspace

The public landing page introduces Nexora's market-intelligence workflow. A workspace is created with organization and account details, then activated through a one-time email verification link. Password recovery uses a separate expiring link, and changing credentials invalidates previous sessions.

![Nexora public homepage](screenshots/00-public-homepage.png)
![Create a workspace](screenshots/01-registration-form.png)
![Verification email sent](screenshots/02-verification-email-sent.png)
![Email verification](screenshots/03-email-verification-page.png)
![Verified account](screenshots/04-email-verified.png)
![Sign in](screenshots/05-login.png)
![New workspace dashboard](screenshots/06-dashboard-empty-workspace.png)

## Map the competitive landscape

A competitor identifies a market business; a source describes the public endpoint from which Nexora can collect pricing signals. Source configuration controls request pacing, retry behavior, headers, and extraction selectors. A duplicate competitor domain is rejected rather than creating redundant market entities.

![Competitor directory](screenshots/07-competitors-empty.png)
![Competitor added](screenshots/08-competitor-created.png)
![Duplicate domain validation](screenshots/09-duplicate-domain-rejected.png)
![Source creation](screenshots/10-source-creation-form.png)
![Connected source](screenshots/11-sources-created.png)
![Source collection configuration](screenshots/12-source-configuration.png)
![Saved source configuration](screenshots/13-source-configuration-saved.png)

## Build a catalogue worth monitoring

The catalogue stores canonical offerings, product identifiers, market, currency, pricing, categories, and dynamic attributes. Teams can open detail and history views, change catalogue data, pause and resume monitoring, register custom fields, bulk import records, export CSV/JSON, and archive records without deleting their history.

![Create an offering](screenshots/14-offering-creation-form.png)
![Offering in the catalogue](screenshots/15-catalog-offering-created.png)
![Offering detail and price history](screenshots/16-offering-detail-and-history.png)
![Monitoring enabled](screenshots/17-catalog-monitoring-active.png)
![Dynamic field definitions](screenshots/18-dynamic-fields.png)
![Create a dynamic field](screenshots/19-dynamic-field-form.png)
![Dynamic field saved](screenshots/20-dynamic-field-created.png)
![Bulk catalogue import](screenshots/21-bulk-import-form.png)
![Imported product catalogue](screenshots/22-bulk-imported-catalog.png)
![CSV and JSON export with archive workflow](screenshots/23-catalog-import-export-and-archive.png)

## Collect market prices and create a signal

An offering match connects a tracked item with its competitor source URL. Collection retrieves the page over HTTP, extracts structured product data, writes an observation and snapshot, and updates history. The example starts at $399.99 and then moves to $349.99. A configured 10% drop rule receives a price-change event; the team can review the alert, mark it as read, and see the notification history.

![Map a catalogue offering to a competitor page](screenshots/24-offering-match-form.png)
![Offering match saved](screenshots/25-offering-match-created.png)
![First price observation](screenshots/26-first-price-observation.png)
![Configure a price-drop rule](screenshots/27-alert-rule-form.png)
![Price-drop rule enabled](screenshots/28-alert-rule-created.png)
![Generated price alert](screenshots/29-alert-generated-and-read.png)
![Collection execution history](screenshots/30-collection-job-history.png)
![Collection job details](screenshots/31-collection-job-detail.png)

## Discover offerings from a public website

Website discovery follows public links, uses structured product evidence, and merges discovered records into the tenant's catalogue. Private or loopback destinations are rejected by the server. Repeating the same discovery updates the existing item rather than creating a duplicate.

![Private target blocked](screenshots/32-private-target-blocked.png)
![Discovered catalogue item](screenshots/33-discovery-product-created.png)
![Discovery update and history](screenshots/34-discovery-upsert-history.png)

## Workspace settings and account security

Workspace administrators can update organization metadata and change their password. The journey also covers a fresh password-reset email, its one-time reset form, and successful sign-in with the new credential.

![Workspace settings](screenshots/35-workspace-settings.png)
![Updated workspace profile](screenshots/36-workspace-profile-updated.png)
![Password changed](screenshots/37-password-changed.png)
![Password reset requested](screenshots/38-password-reset-requested.png)
![Password reset form](screenshots/39-password-reset-form.png)
![Password reset complete](screenshots/40-password-reset-complete.png)
![Dashboard after password recovery](screenshots/41-dashboard-after-password-reset.png)

## Access shaped by role

The same workspace is presented differently to an analyst and a viewer. Analysts can inspect offerings and start discovery but cannot manage competitors. Viewers can read catalogue information, while administrative creation and bulk tools remain unavailable in the interface and are rejected by the API when called directly.

![Analyst workspace](screenshots/42-analyst-workspace.png)
![Viewer read-only workspace](screenshots/43-viewer-read-only-workspace.png)
![Responsive mobile entry page](screenshots/44-mobile-homepage.png)

---

*The screenshots illustrate a connected product journey in an isolated CI environment. They are a guide to Nexora's workflows, not a certification of the production deployment.*
