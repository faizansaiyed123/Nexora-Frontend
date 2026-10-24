# Nexora — Visual Product Walkthrough

For the visitor-facing introduction, start with the [Nexora product walkthrough](../walkthrough/NEXORA-PRODUCT-WALKTHROUGH.md). This page adds a screenshot-led view of the connected workspace journey, from account setup through market observations and alerts.

The browser journey follows real frontend actions and actual FastAPI responses with a disposable PostgreSQL database and Redis service. The collected product-page HTML is fetched over HTTP and its extracted values are stored through the real collection pipeline. Price values in that controlled source are for repeatable demonstration of a price decrease; they are not presented as current retail prices.

## Workspace and account entry

![Public homepage](visuals/00-public-homepage.png)

![Workspace registration](visuals/01-registration-form.png)

![Verification email sent](visuals/02-verification-email-sent.png)

![Email verification](visuals/03-email-verification.png)

![Account verified](visuals/04-email-verified.png)

![Sign in](visuals/05-login.png)

![New workspace dashboard](visuals/06-dashboard-empty-workspace.png)

## Competitors and source configuration

![Competitor directory](visuals/07-competitors.png)

![Competitor form](visuals/08-competitor-form.png)

![Competitor created](visuals/09-competitor-created.png)

![Duplicate competitor domain rejected](visuals/10-duplicate-competitor-rejected.png)

![Source creation form](visuals/11-source-form.png)

![Source created](visuals/12-source-created.png)

![Source configuration form](visuals/13-source-configuration-form.png)

![Saved source configuration](visuals/14-source-configuration-saved.png)

## Catalog and bulk operations

![Offering form](visuals/15-offering-form.png)

![Offering added](visuals/16-offering-created.png)

![Offering details and price history](visuals/17-offering-details.png)

![Monitoring status](visuals/18-offering-monitoring.png)

![Dynamic field definitions](visuals/19-dynamic-fields.png)

![Dynamic field editor](visuals/20-dynamic-field-form.png)

![Dynamic field created](visuals/21-dynamic-field-created.png)

![Bulk import form](visuals/22-bulk-import-form.png)

![Bulk imported catalog](visuals/23-bulk-imported-catalog.png)

![Catalog export and archive](visuals/24-catalog-import-export-archive.png)

## Collection, alerts, and job history

![Offering match form](visuals/25-match-form.png)

![Offering match created](visuals/26-match-created.png)

![First collected price observation](visuals/27-first-price-observation.png)

![Alert rule form](visuals/28-alert-rule-form.png)

![Alert rule created](visuals/29-alert-rule-created.png)

![Price-drop alert acknowledged](visuals/30-alert-triggered-and-read.png)

![Alert email delivered](visuals/31-alert-email-delivered.png)

![Job history](visuals/32-job-history.png)

![Job detail](visuals/33-job-detail.png)

## Website discovery and catalogue enrichment

![Private discovery target blocked](visuals/34-private-discovery-target-blocked.png)

![Product discovered](visuals/35-discovery-created.png)

![Discovery updated the existing record](visuals/36-discovery-upsert.png)

## Workspace settings and account security

![Workspace settings](visuals/37-workspace-settings.png)

![Workspace profile saved](visuals/38-workspace-profile-saved.png)

![Password changed](visuals/39-password-changed.png)

![Password reset requested](visuals/40-reset-requested.png)

![Password reset form](visuals/41-reset-form.png)

![Password reset complete](visuals/42-reset-completed.png)

![Dashboard after account recovery](visuals/43-dashboard-after-reset.png)

## Role-specific access and responsive layout

![Analyst workspace](visuals/44-analyst-workspace.png)

![Viewer read-only workspace](visuals/45-viewer-read-only.png)

![Mobile homepage](visuals/46-mobile-homepage.png)

## Persisted data summary

The walkthrough runner emits [PostgreSQL evidence](visuals/postgres-evidence.json) after independently reading the tenant, competitor, source, offering, match, latest snapshot, observation count, job count, discovered SKU, and notification delivery state from PostgreSQL.

These captures reflect the connected flows in an isolated test environment. They do not certify the deployed production frontend, API, or database.
