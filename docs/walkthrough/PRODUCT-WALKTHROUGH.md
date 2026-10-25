# Nexora — Product Walkthrough

Nexora is a private market-intelligence workspace for teams that need to understand how their offerings compare with the market. This walkthrough follows one connected journey—from account setup and catalog management to source collection, price movement, alerts, discovery and workspace access.

The screenshots are captured from the running application using a disposable PostgreSQL database, the real FastAPI service, and an isolated email inbox. All business actions shown use the product's actual API and persistence layer. This is a guide to the product and its exercised workflows, not a certification of the live production deployment.

## 1. Discover Nexora and create a workspace

The public homepage introduces the platform. Organization signup creates the tenant boundary. Email verification and password recovery use one-time links delivered through email, and sign-in establishes a real account session.

![Nexora public homepage](screenshots/00-public-homepage.png)

![Create a workspace](screenshots/01-registration-form.png)

![Verification message sent](screenshots/02-verification-email-sent.png)

![Email verification page](screenshots/03-email-verification-page.png)

![Verified account](screenshots/04-email-verified.png)

![New workspace dashboard](screenshots/05-dashboard-empty-workspace.png)

## 2. Map the competitive landscape

Competitors identify the businesses being monitored. Sources define the public endpoints and collection settings used to retrieve their intelligence. Duplicate domains are rejected, and saved configuration can be revisited and changed.

![Competitor directory](screenshots/06-competitors-empty.png)

![Competitor created](screenshots/07-competitor-created.png)

![Duplicate domain protection](screenshots/08-duplicate-domain-protection.png)

![Updated competitor](screenshots/09-competitor-updated.png)

![Create a source](screenshots/10-source-creation-form.png)

![Source directory](screenshots/11-source-created.png)

![Source collection configuration](screenshots/12-source-configuration-form.png)

![Saved source configuration](screenshots/13-source-configuration-saved.png)

## 3. Build and manage the catalog

The catalog is the canonical record of the offerings a team cares about. Each entry can include price, market, currency, category, SKU, description and dynamic attributes. Teams can open details and price history, pause and resume monitoring, define fields, import groups of offerings, export CSV or JSON, and archive items without erasing their history.

![New catalog entry](screenshots/14-offering-creation-form.png)

![Catalog entry saved](screenshots/15-catalog-offering-created.png)

![Offering details and history](screenshots/16-offering-detail-and-history.png)

![Monitoring state saved](screenshots/17-monitoring-toggle-persisted.png)

![Dynamic field definitions](screenshots/18-dynamic-fields.png)

![Create a dynamic field](screenshots/19-dynamic-field-form.png)

![Dynamic field saved](screenshots/20-dynamic-field-created.png)

![Bulk catalog import](screenshots/21-bulk-import-form.png)

![Imported catalog records](screenshots/22-bulk-imported-catalog.png)

![Catalog exports and archive workflow](screenshots/23-catalog-import-export-and-archive.png)

## 4. Connect offerings to market sources

An offering match connects an internal catalog record to a specific competitor product URL. A collection reads the public page, extracts structured price and availability information, records an observation, and updates the current snapshot and historical comparison.

![Configure an offering match](screenshots/24-offering-match-form.png)

![Saved offering match](screenshots/25-offering-match-created.png)

![First price observation](screenshots/26-first-price-observation.png)

## 5. Turn market movement into alerts

Alert rules can be scoped to an offering and use thresholds and cooldowns. When the second collection observes a meaningful price drop, Nexora stores an alert event; a reviewer can mark it as read, and configured notification delivery moves through the email outbox.

![Create a price-movement alert](screenshots/27-alert-rule-form.png)

![Saved alert rule](screenshots/28-alert-rule-created.png)

![Triggered alert and read state](screenshots/29-alert-triggered-and-read.png)

## 6. Review execution history

Collection and discovery jobs retain their status, timestamps, outcomes and contextual details so teams can understand what ran and what the collector returned.

![Collection job history](screenshots/30-collection-job-history.png)

![Collection job details](screenshots/31-collection-job-details.png)

## 7. Discover offerings from a public website

Website discovery examines public pages for explicit product evidence and structured metadata. Private and loopback URLs are blocked by server-side URL validation. Existing products are updated by their identifiers rather than duplicated on each run.

![Private-target protection](screenshots/32-private-target-blocked.png)

![Product discovered into the catalog](screenshots/33-discovered-catalog-item.png)

![Discovery history and updated product](screenshots/34-discovery-upsert-history.png)

## 8. Workspace identity and account security

Workspace administrators can update organization details and change a password. Password changes invalidate old credentials, and account recovery uses a one-time email link before the user signs in again.

![Workspace settings](screenshots/35-workspace-settings.png)

![Updated workspace profile](screenshots/36-workspace-profile-saved.png)

![Password changed](screenshots/37-password-changed.png)

![Password reset requested](screenshots/38-password-reset-requested.png)

![Password reset form](screenshots/39-password-reset-form.png)

![Password reset completed](screenshots/40-password-reset-complete.png)

![Workspace after account recovery](screenshots/41-workspace-after-password-reset.png)

## 9. Role-aware access

Nexora's organization roles present different capabilities. Analysts can inspect intelligence and initiate discovery while administrative changes stay with workspace admins. Viewers have read access to catalog information without create, import or configuration controls.

![Analyst workspace](screenshots/42-analyst-role.png)

![Viewer workspace](screenshots/43-viewer-read-only-role.png)

## 10. Responsive public entry

The public experience remains usable at a narrow mobile viewport.

![Mobile homepage](screenshots/44-mobile-homepage.png)
