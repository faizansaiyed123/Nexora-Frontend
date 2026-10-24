# Nexora | Product Walkthrough

Nexora brings catalog management, competitor coverage, price collection, website discovery and actionable alerts into one private market-intelligence workspace. This guide follows one connected journey: a workspace is created, competitors and collection sources are configured, products are tracked, a price movement is captured, and the resulting signal is reviewed.

The walkthrough shows a retail-product scenario with representative catalog records. The price-collection journey fetches public, structured product pages over HTTP; those pages provide deliberately controlled values so a decrease can be followed from collection through snapshot and alert history. These example prices are not live retail quotes.

## 1. Start with a private workspace

Create an organization workspace, verify the work email, and sign in. The organization establishes a private boundary for the catalog and market intelligence.

![Nexora public homepage](screenshots/00-public-homepage.png)

![Create a workspace](screenshots/01-registration-form.png)

![Workspace created and verification email sent](screenshots/02-verification-email-sent.png)

![Email verification page](screenshots/03-email-verification.png)

![Email address verified](screenshots/04-email-verified.png)

![Sign in to Nexora](screenshots/05-login.png)

![Starting workspace dashboard](screenshots/06-dashboard-empty-workspace.png)

## 2. Configure market coverage

Competitors identify the businesses being benchmarked. Sources define the public pages Nexora retrieves and the request pacing, timeout, retry, header and extraction-selector settings used for collection. A domain cannot be registered twice inside the same workspace.

![Competitor directory](screenshots/07-competitors.png)

![Create a competitor](screenshots/08-competitor-form.png)

![Competitor added to the workspace](screenshots/09-competitor-created.png)

![Duplicate competitor domain is prevented](screenshots/10-duplicate-competitor-rejected.png)

![Create a collection source](screenshots/11-source-form.png)

![Collection source in the directory](screenshots/12-source-created.png)

![Source collection settings](screenshots/13-source-configuration-form.png)

![Saved source configuration](screenshots/14-source-configuration-saved.png)

## 3. Build and maintain the catalog

The catalog holds the offering name, SKU, price, currency, market, category, description and dynamic attributes. Teams can inspect details, update prices, control monitoring, add workspace-specific fields, import multiple offerings, export CSV or JSON, and archive selected records.

![Create a catalog offering](screenshots/15-offering-form.png)

![Offering added to the catalog](screenshots/16-offering-created.png)

![Offering details and price context](screenshots/17-offering-details.png)

![Monitoring controls](screenshots/18-offering-monitoring.png)

![Dynamic field definitions](screenshots/19-dynamic-fields.png)

![Create a custom catalog field](screenshots/20-dynamic-field-form.png)

![Custom field saved](screenshots/21-dynamic-field-created.png)

![Prepare a bulk catalog import](screenshots/22-bulk-import-form.png)

![Imported offerings in the catalog](screenshots/23-bulk-imported-catalog.png)

![Catalog export and selective archive](screenshots/24-catalog-import-export-archive.png)

## 4. Connect an offering to market prices

An offering match connects one of your catalog entries to a specific source URL. Collecting that URL retrieves the page, extracts the available price and product signals, and stores an observation, current snapshot and execution record.

![Map a catalog offering to a competitor page](screenshots/25-match-form.png)

![Offering and competitor URL connected](screenshots/26-match-created.png)

![First collected price observation](screenshots/27-first-price-observation.png)

## 5. Turn market movement into an alert

Alert rules define which price changes matter. When a later collection records a qualifying decrease, the alert appears in the workspace, can be marked as read, and sends an email notification through the configured delivery queue.

![Create a price-drop alert](screenshots/28-alert-rule-form.png)

![Alert rule in the workspace](screenshots/29-alert-rule-created.png)

![Price-drop alert reviewed and marked as read](screenshots/30-alert-triggered-and-read.png)

![Competitive alert email delivered](screenshots/31-alert-email-delivered.png)

## 6. Review execution and discover offerings

Jobs shows the outcome and details of collection runs. Website discovery extracts structured product evidence, adds a previously unseen offering, and updates it in place when the same product is found again. Private and loopback destinations are rejected.

![Collection job history](screenshots/32-job-history.png)

![Collection job details](screenshots/33-job-detail.png)

![Private discovery target rejected](screenshots/34-private-discovery-target-blocked.png)

![A discovered product in the catalog](screenshots/35-discovery-created.png)

![Discovery history after a repeat scan](screenshots/36-discovery-upsert.png)

## 7. Workspace identity and account security

Settings hold organization details and market defaults. A signed-in user can update their password; if access is lost, a one-time email link restores access without creating a new workspace.

![Workspace settings](screenshots/37-workspace-settings.png)

![Workspace profile saved](screenshots/38-workspace-profile-saved.png)

![Password changed](screenshots/39-password-changed.png)

![Password reset requested](screenshots/40-reset-requested.png)

![Choose a new password from the recovery link](screenshots/41-reset-form.png)

![Password reset completed](screenshots/42-reset-completed.png)

![Workspace after password recovery](screenshots/43-dashboard-after-reset.png)

## 8. Role-aware workspaces

Nexora exposes management actions according to the signed-in role. Analysts can use intelligence features without organization-administration controls; viewers can review permitted information without catalog or competitor write access.

![Analyst workspace](screenshots/44-analyst-workspace.png)

![Viewer read-only workspace](screenshots/45-viewer-read-only.png)

## 9. Responsive experience

The signed-in workspace and public entry point adapt to a narrow mobile viewport.

![Nexora dashboard on a mobile viewport](screenshots/46-mobile-dashboard.png)

![Nexora homepage on a mobile viewport](screenshots/47-mobile-homepage.png)

## Feature map

| Workspace area | What it brings together |
|---|---|
| Dashboard | Catalog coverage, competitors, source health, and recent execution activity |
| Competitors | Competitor records, domain uniqueness, editing, and workspace-scoped administration |
| Sources | Collection methods, source health, circuit state, request pacing, timeouts, retries, headers, and selectors |
| Offerings | Product/service catalog, dynamic attributes, search, filtering, price updates, monitoring, details, and archive |
| Bulk catalog tools | Multi-offering import, bulk archive, CSV export, and JSON export |
| Offering matches | Catalog-to-source URL mapping, match confidence, and match status |
| Collections | Public page retrieval, price extraction, observations, snapshots, price movement, and job records |
| Discovery | Public website crawling, structured data extraction, target validation, merge, and update history |
| Jobs | Collection/discovery run status, outcome counts, and execution details |
| Alerts | Price thresholds, event history, read state, and email notification delivery |
| Settings | Organization profile, country, market, currency, industry, timezone, and password controls |
| Access boundaries | Role-aware management actions and tenant-scoped records |

---

The examples are designed to show how the parts of Nexora connect together. A deployed workspace uses its own catalog, competitors, sources, alert rules, and market data.
