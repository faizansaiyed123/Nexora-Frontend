# Nexora — Product Walkthrough

Nexora brings catalog management, competitor coverage, price collection, discovery, and alerts together in one private market-intelligence workspace.

Follow an example workspace from account setup through a price change detected on a monitored product. The same product record connects competitor sources, collection history, alert rules, and discovery results.

## Start here: account and workspace

### Public homepage
![Nexora public homepage](./screenshots/00-public-homepage.png)

### Create a workspace
![Create a workspace](./screenshots/01-create-workspace.png)

### Verification message and one-time link
![Verification email sent](./screenshots/02-verification-email-sent.png)

![Verify the account](./screenshots/03-verify-email.png)

![Email verified](./screenshots/04-email-verified.png)

### The workspace dashboard
![Nexora dashboard](./screenshots/05-dashboard.png)

## Build the competitive picture

### Competitors

Add a market entity, protect against duplicate domains, then edit the record while preserving its identity.

![Competitors](./screenshots/06-competitors.png)

![Add a competitor](./screenshots/07-competitor-form.png)

![Duplicate domain protection](./screenshots/08-duplicate-domain-protection.png)

![Competitor created](./screenshots/09-competitor-created.png)

### Sources and collection settings

Associate a collection source with its competitor. Control request rate, delay, timeout, retry policy, headers, and extraction selectors.

![Create a source](./screenshots/10-source-form.png)

![Configure source collection](./screenshots/11-source-configuration.png)

![Source configuration saved](./screenshots/12-source-configured.png)

## Manage the catalog

Offerings carry a canonical product identity, SKU, price, market, category, monitoring preference, and domain-specific attributes. The catalog also supports detail/history views, dynamic fields, bulk imports, CSV/JSON export, and archiving.

![New catalog offering](./screenshots/13-offering-form.png)

![Catalog listing](./screenshots/14-offering-created.png)

![Offering detail](./screenshots/15-offering-detail.png)

![Monitoring controls](./screenshots/16-offering-monitoring.png)

![Dynamic catalog fields](./screenshots/17-dynamic-fields.png)

![Create a dynamic field](./screenshots/18-dynamic-field-created.png)

![Bulk import](./screenshots/19-bulk-import-form.png)

![Import, export and archive](./screenshots/20-bulk-import-export-archive.png)

## Collect prices and act on a signal

Connect an offering to a competitor URL, collect the first observation, and compare a later price. When a monitored price falls beyond the configured threshold, Nexora keeps a historical alert that can be reviewed and marked as read.

![Map an offering to a competitor](./screenshots/21-match-form.png)

![Offering match](./screenshots/22-offering-match.png)

![First observed price](./screenshots/23-first-price-observation.png)

![Configure a price alert](./screenshots/24-alert-rule-form.png)

![Price alert rule](./screenshots/25-alert-rule-created.png)

![Price alert and read state](./screenshots/26-price-alert-and-read-state.png)

### Collection history

The job stream provides a navigable record of collection activity and its outcome.

![Collection jobs](./screenshots/27-collection-jobs.png)

![Collection job detail](./screenshots/28-collection-job-detail.png)

## Discover new catalog items

Nexora can examine public pages for structured product evidence and merge discoveries into the existing catalog. Requests targeting private or loopback addresses are blocked. Repeat discoveries update a matched item rather than creating a duplicate.

![Private targets are blocked](./screenshots/29-private-target-blocked.png)

![Discovered product](./screenshots/30-discovery-created.png)

![Discovery update history](./screenshots/31-discovery-update-history.png)

## Workspace settings and account security

![Workspace settings](./screenshots/32-workspace-settings.png)

![Workspace profile saved](./screenshots/33-workspace-profile-updated.png)

![Password changed](./screenshots/34-password-change.png)

![Request a password reset](./screenshots/35-password-reset-requested.png)

![One-time password reset form](./screenshots/36-password-reset-form.png)

![Password reset complete](./screenshots/37-password-reset-complete.png)

![Return to the workspace](./screenshots/38-dashboard-after-password-reset.png)

## Different roles, appropriate access

Analysts can inspect intelligence and run discovery while administrative catalog changes remain restricted. Viewer accounts can read the catalog without receiving write controls.

![Analyst workspace](./screenshots/39-analyst-access.png)

![Read-only viewer workspace](./screenshots/40-viewer-read-only-access.png)

## Responsive public experience

![Nexora homepage on a narrow screen](./screenshots/41-mobile-homepage.png)

---

The example uses a dedicated review workspace and representative retail product-page data. It does not include customer records or production workspace data.
