# Nexora — Product Walkthrough

Nexora brings catalog management, competitor coverage, price collection, discovery, and alerts together in one private market-intelligence workspace.

Follow an example workspace from account setup through a price movement on a monitored product. One catalog record connects its competitor sources, collection history, alert rules, and discovery results.

## Account and workspace

### Public homepage
![Nexora public homepage](./screenshots/00-public-homepage.png)

### Create a workspace
![Registration form](./screenshots/01-registration-form.png)

### Verify the account
![Verification email sent](./screenshots/02-verification-email-sent.png)

![Email verification page](./screenshots/03-email-verification-page.png)

![Email verified](./screenshots/04-email-verified.png)

### Sign in and open the workspace
![Sign-in page](./screenshots/05-login.png)

![Initial dashboard](./screenshots/06-dashboard-empty-workspace.png)

## Competitors and collection sources

Track the businesses whose prices matter. Nexora protects against duplicate domains and lets authorised staff edit competitor details and configure public sources.

![Competitor directory](./screenshots/07-competitors-empty.png)

![Competitor created](./screenshots/08-competitor-created.png)

![Duplicate-domain rejection](./screenshots/09-duplicate-domain-rejected.png)

![Create a collection source](./screenshots/10-source-creation-form.png)

![Configured sources](./screenshots/11-sources-created.png)

![Source collection settings](./screenshots/12-source-configuration.png)

![Source settings saved](./screenshots/13-source-configuration-saved.png)

![JavaScript-rendered source option](./screenshots/13b-source-js-rendering-enabled.png)

Nexora can use a fast HTTP fetch for ordinary public pages or a browser-rendered page when a source requires JavaScript.

## Catalog management

Offerings bring product identity, SKU, pricing, market, category, and flexible attributes into a consistent catalog. Staff can inspect detail and price history, pause or resume monitoring, add dynamic fields, bulk-import records, export CSV/JSON, and archive items without confusing catalog edits with inventory or observation history.

![Create an offering](./screenshots/14-offering-creation-form.png)

![Catalog listing](./screenshots/15-catalog-offering-created.png)

![Offering detail and history](./screenshots/16-offering-detail-and-history.png)

![Monitoring control](./screenshots/17-catalog-monitoring-active.png)

![Dynamic fields](./screenshots/18-dynamic-fields.png)

![Create a dynamic field](./screenshots/19-dynamic-field-form.png)

![Dynamic field saved](./screenshots/20-dynamic-field-created.png)

![Bulk import](./screenshots/21-bulk-import-form.png)

![Imported catalog records](./screenshots/22-bulk-imported-catalog.png)

A mixed import keeps successful records and shows the exact rejected row and reason, so users can resolve input issues without losing valid catalogue work.

![Bulk import row-level results](./screenshots/22b-bulk-import-row-errors.png)

![Import, export and archive](./screenshots/23-catalog-import-export-and-archive.png)

![Archive an individual catalogue item](./screenshots/23b-single-offering-archived.png)

Larger catalogues are split into pages; the controls let the team navigate through the full set without loading every row into one view. The catalogue can also be narrowed by offering type.

![Catalogue pagination](./screenshots/23c-catalog-pagination.png)

![Catalogue filtered by offering type](./screenshots/23d-catalog-type-filter.png)

## Price intelligence and alerts

Map a catalog offering to a competitor URL, collect a first price observation, and compare the next observation. Alert rules turn a meaningful movement into a persistent signal that the team can review and mark as read.

![Create an offering match](./screenshots/24-offering-match-form.png)

![Offering match details](./screenshots/25-offering-match-created.png)

![First price observation](./screenshots/26-first-price-observation.png)

![Create a price alert](./screenshots/27-alert-rule-form.png)

![Price alert rule](./screenshots/28-alert-rule-created.png)

![Generated price alert and read state](./screenshots/29-alert-generated-and-read.png)

### Execution history

The job list provides an understandable record of collection and discovery activity, status, outcomes, and relevant details.

![Collection job history](./screenshots/30-collection-job-history.png)

![Collection job detail](./screenshots/31-collection-job-detail.png)

## Website discovery and network safeguards

Nexora can examine public pages for structured product information and merge discovered candidates into the existing catalog. Private and loopback addresses are blocked, and repeat discovery updates a matched record rather than duplicating it.

![Private target blocked](./screenshots/32-private-target-blocked.png)

![Product discovered](./screenshots/33-discovery-product-created.png)

![Discovery updates existing catalog record](./screenshots/34-discovery-upsert-history.png)

## Workspace settings and account recovery

![Workspace settings](./screenshots/35-workspace-settings.png)

![Workspace profile updated](./screenshots/36-workspace-profile-updated.png)

![Password changed](./screenshots/37-password-changed.png)

![Password reset requested](./screenshots/38-password-reset-requested.png)

![One-time password reset form](./screenshots/39-password-reset-form.png)

![Password reset complete](./screenshots/40-password-reset-complete.png)

![Dashboard after account recovery](./screenshots/41-dashboard-after-password-reset.png)

## Role-specific access

Analysts can inspect intelligence and run discovery while administrative changes remain restricted. Viewers receive read-only catalog access. The platform Super Admin view also follows the server-issued role and permission rules.

![Analyst workspace](./screenshots/42-analyst-workspace.png)

![Viewer read-only workspace](./screenshots/43-viewer-read-only-workspace.png)

![Platform Super Admin workspace](./screenshots/44-super-admin-workspace.png)

## Live public price reference

The same workflow can collect a live product page from the [Sony Center retail store](https://shopatsc.com/collections/all/products/wh1000xm5-pmin). Unlike the controlled retail pages used to make alert scenarios reproducible, this observation reads the public storefront at run time, so the price can vary by date and region.

![Live Sony Center retail source](./screenshots/45-live-retail-source.png)

![Live retail price in Nexora's offering comparison](./screenshots/46-live-retail-price-comparison.png)

## Responsive public experience

![Nexora homepage on mobile](./screenshots/47-mobile-homepage.png)

---

The example uses a dedicated review workspace and representative retail product-page data. It does not include customer records or production workspace data.
