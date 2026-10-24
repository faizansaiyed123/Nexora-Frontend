# Nexora — Visual Product Walkthrough

Nexora brings a team's catalog, competitor coverage, collection activity, discovery, and market alerts into one private workspace. This walkthrough follows the product from workspace creation to a price movement that becomes an actionable signal.

Screenshots use an isolated review workspace with illustrative product records. Account and business records flow through Nexora's API and PostgreSQL; structured retail pages provide repeatable source data for the collection journey.

## 1. Enter the workspace

Create an organization, verify the email address, and sign in. The organization establishes the boundary for its catalog and market intelligence.

![Nexora public homepage](walkthrough/screenshots/01-public-homepage.png)

![Account creation](walkthrough/screenshots/02-account-created-verification-required.png)

![Email verification](walkthrough/screenshots/03-email-verification.png)

![Verified account](walkthrough/screenshots/04-email-verified.png)

![Workspace dashboard](walkthrough/screenshots/05-first-workspace-dashboard.png)

## 2. Define the competitive landscape

Add the businesses to monitor, then configure collection sources and their request settings.

![Competitor directory](walkthrough/screenshots/06-competitors.png)

![Competitor created](walkthrough/screenshots/07-competitor-created.png)

![Competitor updated](walkthrough/screenshots/08-competitor-edited.png)

![Create a collection source](walkthrough/screenshots/09-source-creation-form.png)

![Source configuration](walkthrough/screenshots/10-source-configuration-form.png)

![Configured source](walkthrough/screenshots/11-source-created-configured.png)

## 3. Build the catalog

Offerings carry price, currency, market, SKU, category, description, and flexible attributes. Teams can inspect detail, control monitoring, define dynamic fields, bulk import, archive, and export records.

![Create an offering](walkthrough/screenshots/12-offering-creation-form.png)

![Offering detail](walkthrough/screenshots/13-offering-details.png)

![Edit offering and monitoring](walkthrough/screenshots/14-offering-edited-and-monitoring.png)

![Dynamic fields](walkthrough/screenshots/15-dynamic-fields.png)

![A custom catalog field](walkthrough/screenshots/16-dynamic-field-created.png)

![Bulk import](walkthrough/screenshots/17-bulk-import-form.png)

![Imported offerings](walkthrough/screenshots/18-bulk-imported-catalog.png)

![Catalog exports and archive](walkthrough/screenshots/19-catalog-import-export-and-archive.png)

## 4. Connect a competitor listing

A match links one internal offering to a specific source URL. Collecting that URL produces observations and price snapshots that can be reviewed later.

![Map an offering to a listing](walkthrough/screenshots/20-offering-match-form.png)

![Configured offering match](walkthrough/screenshots/21-offering-match-created.png)

![First price observation](walkthrough/screenshots/22-first-price-observation.png)

## 5. Turn movement into a signal

Alert rules define which market events matter. When a later collection finds a meaningful price drop, Nexora stores the alert, queues an email notification, and lets the team mark the event as read.

![Create a price-drop alert](walkthrough/screenshots/23-alert-rule-form.png)

![Saved alert rule](walkthrough/screenshots/24-alert-rule-created.png)

![Generated price-drop alert](walkthrough/screenshots/25-alert-triggered-and-read.png)

## 6. Follow execution and discover offerings

Jobs provides collection history and run details. Website discovery extracts structured product data, merges repeated discoveries, and blocks private network targets.

![Collection job history](walkthrough/screenshots/26-collection-job-history.png)

![Collection job detail](walkthrough/screenshots/27-collection-job-detail.png)

![Private target rejected](walkthrough/screenshots/28-private-target-blocked.png)

![Discovered catalog item](walkthrough/screenshots/29-discovered-catalog-item.png)

![Discovery history](walkthrough/screenshots/30-discovery-history-and-upsert.png)

## 7. Workspace settings and account security

Workspace owners can update organization information, change their password, and recover access through a one-time email link.

![Workspace profile](walkthrough/screenshots/31-workspace-profile.png)

![Password changed](walkthrough/screenshots/32-password-changed.png)

![Password reset requested](walkthrough/screenshots/33-password-reset-requested.png)

![Password reset form](walkthrough/screenshots/34-password-reset-form.png)

![Password reset complete](walkthrough/screenshots/35-password-reset-complete.png)

![Workspace after account recovery](walkthrough/screenshots/36-dashboard-after-recovery.png)

## 8. Role-aware workspaces

Analysts can work with intelligence while administration stays restricted. Viewers can inspect workspace data while management actions remain unavailable.

![Analyst workspace](walkthrough/screenshots/37-analyst-workspace.png)

![Viewer workspace](walkthrough/screenshots/38-viewer-read-only-workspace.png)

## 9. Responsive entry point

The public experience adapts to a narrow mobile viewport.

![Mobile homepage](walkthrough/screenshots/39-mobile-homepage.png)
