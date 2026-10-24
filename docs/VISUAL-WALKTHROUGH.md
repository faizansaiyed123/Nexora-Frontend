# Nexora — Visual Product Walkthrough

Nexora brings a team's catalog, competitor coverage, collection activity, website discovery, and market alerts into one private workspace. This walkthrough follows the product from creating a workspace to turning a detected price movement into an actionable signal.

The screenshots use an isolated review workspace with illustrative product records. Account and business records flow through Nexora's API and PostgreSQL; structured product pages provide repeatable retail data for the collection journey.

## 1. Enter the workspace

Create an organization, verify the email address, and sign in. The organization establishes the boundary for its catalog and market intelligence.

![Nexora public homepage](walkthrough/screenshots/00-public-homepage.png)

![Create a workspace](walkthrough/screenshots/01-registration-form.png)

![Verification message sent](walkthrough/screenshots/02-verification-email-sent.png)

![Email verification page](walkthrough/screenshots/03-email-verification-page.png)

![Verified account](walkthrough/screenshots/04-email-verified.png)

![Sign in](walkthrough/screenshots/05-login.png)

![Starting workspace dashboard](walkthrough/screenshots/06-dashboard-starting-workspace.png)

## 2. Define the competitive landscape

Add the businesses to monitor, confirm their domain, and configure collection sources and the request settings used to retrieve market information.

![Competitor directory](walkthrough/screenshots/07-competitors.png)

![Competitor created](walkthrough/screenshots/08-competitor-created.png)

![Duplicate domain protection](walkthrough/screenshots/09-duplicate-domain-protection.png)

![Create a collection source](walkthrough/screenshots/10-source-form.png)

![Source created](walkthrough/screenshots/11-source-created.png)

![Source collection settings](walkthrough/screenshots/12-source-settings.png)

![Saved source settings](walkthrough/screenshots/13-source-settings-saved.png)

## 3. Build the catalog

Offerings carry price, currency, market, SKU, category, description, and flexible attributes. Teams can inspect details, control monitoring, define custom fields, bulk import, archive selected records, and export the catalog.

![Create an offering](walkthrough/screenshots/14-offering-form.png)

![Offering created](walkthrough/screenshots/15-catalog-offering-created.png)

![Offering details](walkthrough/screenshots/16-offering-details.png)

![Monitoring controls](walkthrough/screenshots/17-monitoring-controls.png)

![Dynamic field definitions](walkthrough/screenshots/18-dynamic-fields.png)

![Create a dynamic field](walkthrough/screenshots/19-dynamic-field-form.png)

![Dynamic field saved](walkthrough/screenshots/20-dynamic-field-created.png)

![Bulk import](walkthrough/screenshots/21-bulk-import-form.png)

![Bulk import results](walkthrough/screenshots/22-bulk-import-results.png)

![Catalog export and archive](walkthrough/screenshots/23-catalog-import-export-archive.png)

## 4. Connect a competitor listing

A match links an internal offering to a specific source URL. Collecting that URL creates an observation and a price snapshot, with an execution record available for review.

![Map an offering to a listing](walkthrough/screenshots/24-offering-match-form.png)

![Configured offering match](walkthrough/screenshots/25-offering-match-created.png)

![First price observation](walkthrough/screenshots/26-first-price-observation.png)

![Dashboard with market data](walkthrough/screenshots/27-dashboard-with-market-data.png)

## 5. Turn price movement into a signal

Alert rules define which market events matter. When a later collection detects a meaningful price decrease, Nexora stores the alert, queues an email notification, and lets the team mark the event as read.

![Create a price-drop alert](walkthrough/screenshots/28-alert-rule-form.png)

![Saved alert rule](walkthrough/screenshots/29-alert-rule-created.png)

![Generated price-drop alert](walkthrough/screenshots/30-alert-generated-and-read.png)

## 6. Follow execution and discover more offerings

Jobs displays collection history and run details. Website discovery extracts structured product data, updates an existing catalog item when the same product is found again, and blocks private network targets.

![Collection job history](walkthrough/screenshots/31-collection-job-history.png)

![Collection job details](walkthrough/screenshots/32-collection-job-details.png)

![Private network target blocked](walkthrough/screenshots/33-private-target-blocked.png)

![A discovered catalog item](walkthrough/screenshots/34-discovery-product-created.png)

![Discovery history and repeat scan](walkthrough/screenshots/35-discovery-update-history.png)

## 7. Workspace settings and account security

Workspace owners can update organization information and change a password. Password recovery uses a one-time email link to restore access to the same workspace.

![Workspace settings](walkthrough/screenshots/36-workspace-settings.png)

![Workspace profile saved](walkthrough/screenshots/37-workspace-profile-saved.png)

![Password changed](walkthrough/screenshots/38-password-changed.png)

![Password reset requested](walkthrough/screenshots/39-password-reset-requested.png)

![Password reset form](walkthrough/screenshots/40-password-reset-form.png)

![Password reset complete](walkthrough/screenshots/41-password-reset-complete.png)

![Workspace after recovery](walkthrough/screenshots/42-dashboard-after-reset.png)

## 8. Role-aware workspaces

The Analyst role can work with intelligence and discovery without receiving organization-administration privileges. The Viewer role can inspect workspace data while management actions remain unavailable.

![Analyst workspace](walkthrough/screenshots/43-analyst-workspace.png)

![Viewer read-only workspace](walkthrough/screenshots/44-viewer-read-only-workspace.png)

## 9. Responsive experience

The signed-in workspace and public entry point adapt to a narrow mobile viewport.

![Mobile dashboard](walkthrough/screenshots/45-mobile-dashboard.png)

![Mobile homepage](walkthrough/screenshots/46-mobile-homepage.png)
