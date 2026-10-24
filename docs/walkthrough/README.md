# Nexora | Product Walkthrough

Nexora brings catalog management, competitor coverage, price collection, website discovery and actionable alerts into one private market-intelligence workspace. This guide follows the journey from creating a workspace to turning a competitor price movement into a useful signal.

The screenshots show the product's visible screens and the connected workflow behind them. Values and examples use a retail-product scenario; the same catalog model supports other offering types, including services, subscriptions, rooms, rentals and plans.

## 1. Start with a private workspace

Create an organization workspace, verify the work email, and sign in. Account verification and recovery links are delivered by email, and the workspace opens with a dashboard suited to the signed-in role.

![Nexora public homepage](screenshots/00-public-homepage.png)

![Create a workspace](screenshots/01-registration-form.png)

![Workspace created and verification email sent](screenshots/02-verification-email-sent.png)

![Email verification page](screenshots/03-email-verification-page.png)

![Email address verified](screenshots/04-email-verified.png)

![Sign in to Nexora](screenshots/05-login.png)

![A new workspace dashboard](screenshots/06-dashboard-starting-workspace.png)

## 2. Configure market coverage

Competitors identify the businesses being benchmarked. Sources define the public pages Nexora can collect from and include request pacing, timeout, retry, header and extraction-selector settings. A domain cannot be registered twice in the same workspace.

![Competitor directory](screenshots/07-competitors.png)

![Competitor added to the workspace](screenshots/08-competitor-created.png)

![Duplicate competitor domain is prevented](screenshots/09-duplicate-domain-protection.png)

![Create a collection source](screenshots/10-source-form.png)

![Collection source in the source directory](screenshots/11-source-created.png)

![Source collection settings](screenshots/12-source-settings.png)

![Saved source configuration](screenshots/13-source-settings-saved.png)

## 3. Build and maintain the catalog

The catalog holds the canonical offering name, SKU, price, currency, market, category, description and dynamic attributes. Open an offering to view its details and market comparison, change whether it is monitored, add workspace-specific fields, import multiple offerings, export CSV or JSON, and archive items that should no longer appear in the active catalogue.

![Create a catalog offering](screenshots/14-offering-form.png)

![Catalog offering in the workspace](screenshots/15-catalog-offering-created.png)

![Offering detail and market context](screenshots/16-offering-details.png)

![Monitoring controls](screenshots/17-monitoring-controls.png)

![Dynamic field definitions](screenshots/18-dynamic-fields.png)

![Define a custom catalog field](screenshots/19-dynamic-field-form.png)

![Custom field added](screenshots/20-dynamic-field-created.png)

![Prepare a bulk catalog import](screenshots/21-bulk-import-form.png)

![Imported offerings in the catalog](screenshots/22-bulk-import-results.png)

![Catalog export and archive workflow](screenshots/23-catalog-import-export-archive.png)

## 4. Connect an offering to competitor prices

An offering match connects one of your catalog entries to a specific source URL. Running a collection fetches that public page, extracts the available price and product signals, and stores the observation, the current snapshot, and execution details.

![Map a catalog offering to a competitor page](screenshots/24-offering-match-form.png)

![Offering and competitor URL connected](screenshots/25-offering-match-created.png)

![A collected price observation](screenshots/26-first-price-observation.png)

Once market observations exist, the dashboard brings catalog coverage, competitors, source health and collection activity into one view.

![Dashboard with market data](screenshots/27-dashboard-with-market-data.png)

## 5. Turn market movements into alerts

Alert rules can watch for price movement, percentage drops, undercut thresholds, stock changes and source circuit-breaker events. Events remain in the alert history so a team member can review and acknowledge them. Email notifications use a delivery outbox so the workspace retains delivery status.

![Create a percentage-drop alert](screenshots/28-alert-rule-form.png)

![Alert rule in the workspace](screenshots/29-alert-rule-created.png)

![A price-drop alert and its read state](screenshots/30-alert-generated-and-read.png)

Collection and discovery history help the team understand the outcome of each run and inspect its saved details.

![Collection job history](screenshots/31-collection-job-history.png)

![Collection job details](screenshots/32-collection-job-details.png)

## 6. Discover catalog items from a website

Website discovery can inspect a public storefront for structured product data and merge evidence-backed findings into the catalog. Nexora rejects private or loopback targets, and a repeat scan updates a matching offering rather than duplicating it.

![Private-network target rejected](screenshots/33-private-target-blocked.png)

![Product discovered and added to the catalog](screenshots/34-discovery-product-created.png)

![Discovery history after an update](screenshots/35-discovery-update-history.png)

## 7. Workspace identity and account security

Workspace settings hold the organization profile and market defaults. Users can update their password while signed in or use a one-time recovery link if they lose access.

![Workspace profile and security settings](screenshots/36-workspace-settings.png)

![Updated workspace profile](screenshots/37-workspace-profile-saved.png)

![Password updated from account settings](screenshots/38-password-changed.png)

![Password-recovery request](screenshots/39-password-reset-requested.png)

![Choose a new password from the recovery link](screenshots/40-password-reset-form.png)

![Password reset completed](screenshots/41-password-reset-complete.png)

![Dashboard after signing back in](screenshots/42-dashboard-after-reset.png)

## 8. Role-aware workspace views

The interface exposes actions according to the user's role, and the backend enforces the same permissions. Analysts can work with intelligence and discovery without changing administrative configuration; viewers can inspect permitted workspace data without gaining catalog or competitor write access.

![Analyst workspace](screenshots/43-analyst-workspace.png)

![Viewer read-only workspace](screenshots/44-viewer-read-only-workspace.png)

Nexora's public entry point also adapts to smaller screens.

![Nexora homepage on a mobile viewport](screenshots/45-mobile-homepage.png)

## Feature map

| Workspace area | What it brings together |
|---|---|
| Dashboard | Catalog coverage, competitors, source health, recent collection and discovery activity |
| Competitors | Competitor records, domain uniqueness and workspace-scoped administration |
| Sources | Source type, collection method, health, circuit state, retry policy, request pacing and selectors |
| Offerings | Product and service catalog, dynamic attributes, search, filtering, pagination, monitoring, detail, history and archive |
| Bulk catalog tools | Multi-offering import, bulk archive, CSV export and JSON export |
| Offering matches | Catalog-to-source URL mappings, match confidence and approved/suggested/rejected states |
| Collections | Public page retrieval, price and availability extraction, observations, snapshots and price movement |
| Discovery | Public website crawling, structured data extraction, target validation, merge and update history |
| Jobs | Collection/discovery run status, outcome counts and execution details |
| Alerts | Rule thresholds, cooldowns, rule activation, event history, read state and email notification delivery |
| Settings | Organization profile, country, market, currency, industry, timezone and password controls |
| Access boundaries | Tenant-level data separation and role-aware read/write permissions |

---

*The workflow and example data in this walkthrough are illustrative of how the Nexora product fits together; your workspace reflects its own catalog, competitors, sources and permissions.*
