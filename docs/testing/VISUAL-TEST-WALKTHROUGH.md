# Nexora — Product Walkthrough

Nexora is a private competitive-intelligence workspace that connects a company's own catalog to competitor offerings, public pricing sources, collection history, discovery, and actionable alerts.

This guide follows a market analyst's workspace from first sign-in to a price movement that becomes a saved alert. Each screen belongs to the same service journey: the interface sends requests to the Nexora API, and the resulting records are stored in the workspace database.

## 1. Create a private workspace

Start at the public homepage, create an organization, verify the email address, and sign in. Account verification and password recovery use one-time links delivered to the mailbox configured for the workspace.

![Nexora public homepage](visuals/00-public-homepage.png)

![Create a workspace](visuals/01-registration-form.png)

![Workspace verification email sent](visuals/02-verification-email-sent.png)

![Open the verification link](visuals/03-email-verification-page.png)

![Email address verified](visuals/04-email-verified.png)

![Sign in to Nexora](visuals/05-login.png)

The dashboard is the entry point to the workspace. It brings tracked offerings, competitors, collection sources, and current jobs into one operating picture.

![New workspace dashboard](visuals/06-dashboard-empty-workspace.png)

## 2. Define the competitive landscape

A competitor is a business or market entity Nexora should monitor. The domain is unique inside the workspace, helping the team avoid duplicate entries.

![Competitor directory](visuals/07-competitors-empty.png)

![Competitor added to the workspace](visuals/08-competitor-created.png)

![Duplicate competitor domain is rejected](visuals/09-duplicate-domain-rejected.png)

Sources describe where pricing or availability information is collected and how Nexora should access the page. The configuration holds request pacing, timeouts, retry policy, headers, and extraction selectors.

![Create a collection source](visuals/10-source-creation-form.png)

![Competitor source directory](visuals/11-sources-created.png)

![Collection settings](visuals/12-source-configuration.png)

![Saved source configuration](visuals/13-source-configuration-saved.png)

## 3. Build and maintain the catalog

The catalog is the internal reference for the products, plans, or services the organization cares about. Core fields such as SKU, price, currency, market, and category sit alongside flexible attributes such as brand, color, battery life, or vertical-specific specifications.

![Add a catalog offering](visuals/14-offering-creation-form.png)

![Catalog offering saved](visuals/15-catalog-offering-created.png)

Opening an offering reveals its details and history. Monitoring can be paused or resumed without removing the catalog record.

![Offering detail and price history](visuals/16-offering-detail-and-history.png)

![Monitoring enabled](visuals/17-catalog-monitoring-active.png)

Dynamic fields give a workspace control over attributes that are specific to its business domain.

![Dynamic field definitions](visuals/18-dynamic-fields.png)

![Define a new catalog field](visuals/19-dynamic-field-form.png)

![Dynamic field added](visuals/20-dynamic-field-created.png)

For larger catalogs, bulk import creates multiple offerings in one operation. CSV and JSON exports support downstream analysis; archived items can be retained for history without appearing in the active catalog.

![Bulk import catalog data](visuals/21-bulk-import-form.png)

![Catalog after bulk import](visuals/22-bulk-imported-catalog.png)

![Search, export, and archive catalog items](visuals/23-catalog-import-export-and-archive.png)

## 4. Connect an offering to a competitor and collect a price

An offering match ties an internal catalog record to a particular competitor URL. It records the match state and confidence, so the team can review which competitive comparisons are ready for monitoring.

![Map an internal offering to a source URL](visuals/24-offering-match-form.png)

![Saved offering match](visuals/25-offering-match-created.png)

Running a collection fetches the public page using Nexora's collection pipeline. Extracted price, currency, availability, and page attributes become an observation; the latest snapshot preserves the previous price for comparison.

![First price observation recorded](visuals/26-first-price-observation.png)

## 5. Turn price movement into an alert

Rules can watch for percentage drops, price changes, undercutting, stock changes, or source-health events. Rules can be scoped to one offering or applied across the workspace, with configurable thresholds and cooldowns.

![Configure a price-drop alert](visuals/27-alert-rule-form.png)

![Price-drop alert rule saved](visuals/28-alert-rule-created.png)

When the next collection observes a drop from $399.99 to $349.99, Nexora stores the change in its snapshot history and creates an alert because the movement crosses the configured 10% threshold. Alert events remain in the workspace, can be marked read, and can be delivered through the notification outbox.

![Price-drop alert and read state](visuals/29-alert-generated-and-read.png)

## 6. Follow collection and discovery activity

Jobs provide the operational history behind collection and discovery. Each entry shows its status and processing outcome, and its detail view keeps the run identifier, source, and metadata together.

![Collection job history](visuals/30-collection-job-history.png)

![Collection job details](visuals/31-collection-job-detail.png)

Website discovery walks a public site, looks for structured product evidence, and merges valid candidates into the catalog. Requests to private or loopback destinations are rejected by the server-side URL security boundary.

![A private target is blocked](visuals/32-private-target-blocked.png)

![Product discovered from structured page data](visuals/33-discovery-product-created.png)

A later scan updates the existing catalog item when its identity matches; it does not create another copy of the same discovered SKU.

![Discovery history and catalog upsert](visuals/34-discovery-upsert-history.png)

## 7. Workspace administration and account security

Organization administrators can maintain the workspace profile, including company identity, market, currency, industry, and timezone.

![Workspace settings](visuals/35-workspace-settings.png)

![Updated organization profile](visuals/36-workspace-profile-updated.png)

Signed-in users can change a password, and account recovery uses a separate expiring reset link. A reset invalidates the previous refresh sessions before the user signs in again.

![Password changed](visuals/37-password-changed.png)

![Request password recovery](visuals/38-password-reset-requested.png)

![Choose a new password](visuals/39-password-reset-form.png)

![Password reset completed](visuals/40-password-reset-complete.png)

![Dashboard after account recovery](visuals/41-dashboard-after-password-reset.png)

Access is role-aware. Analysts can work with read and analysis features while administrator-only controls are withheld; viewers can browse permitted information without catalog or competitor write controls.

![Analyst workspace permissions](visuals/42-analyst-workspace.png)

![Viewer read-only workspace](visuals/43-viewer-read-only-workspace.png)

## 8. Responsive entry point

The public entry page adapts to a narrow viewport so a visitor can understand the product and reach account creation without a horizontally overflowing layout.

![Nexora homepage on a mobile viewport](visuals/44-mobile-homepage.png)

---

The walkthrough uses a dedicated review workspace and public structured-data pages. It is a guide to how Nexora's core customer journey fits together, not a certification of a separately deployed production environment.
