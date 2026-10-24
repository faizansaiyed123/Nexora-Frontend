# Nexora — Visual Product Walkthrough

Nexora is a private market-intelligence workspace for catalog owners and analysts. It connects tracked offerings with competitor websites, price observations, discovery activity, and alerts that explain when the market moves.

This walkthrough follows a sample Northstar workspace from account setup through catalog management, collection, market signals, discovery, and account controls.

## 1. Enter the workspace

Start at the public page, create a workspace, verify the email address, and sign in.

![Nexora public homepage](visuals/00-public-homepage.png)

![Create a workspace](visuals/01-registration-form.png)

![Verification message](visuals/02-verification-email-sent.png)

![Email verification page](visuals/03-email-verification.png)

![Email verified](visuals/04-email-verified.png)

![Sign in](visuals/05-login.png)

![Workspace dashboard](visuals/06-dashboard-empty-workspace.png)

## 2. Map the competitive landscape

Competitors define the businesses to watch. Sources specify the public pages Nexora reads and the request, timing, retry, header, and extraction controls.

![Competitors before setup](visuals/07-competitors.png)

![Create a competitor](visuals/08-competitor-form.png)

![Competitor added](visuals/09-competitor-created.png)

![Duplicate domain handled](visuals/10-duplicate-competitor-rejected.png)

![Add a source](visuals/11-source-form.png)

![Source connected](visuals/12-source-created.png)

![Source configuration](visuals/13-source-configuration-form.png)

![Saved source configuration](visuals/14-source-configuration-saved.png)

## 3. Build and maintain the catalog

Each offering can include its SKU, price, market, category, description, and flexible attributes. The catalog supports detail views, editing, monitoring controls, shared dynamic fields, bulk import, export, and archive.

![Add a catalog offering](visuals/15-offering-form.png)

![Offering in the catalog](visuals/16-offering-created.png)

![Offering detail and history](visuals/17-offering-details.png)

![Catalog monitoring active](visuals/18-offering-monitoring.png)

![Dynamic field definitions](visuals/19-dynamic-fields.png)

![Create a reusable field](visuals/20-dynamic-field-form.png)

![Dynamic field saved](visuals/21-dynamic-field-created.png)

![Bulk import](visuals/22-bulk-import-form.png)

![Imported catalog entries](visuals/23-bulk-imported-catalog.png)

![Export and selective archive](visuals/24-catalog-import-export-archive.png)

## 4. Turn a match into a market signal

A match connects an internal offering to a competitor URL. Collection saves the price observation and snapshot. Alert rules turn meaningful movements into event history and notifications.

![Map an offering to a competitor page](visuals/25-match-form.png)

![Offering match created](visuals/26-match-created.png)

![First price observation](visuals/27-first-price-observation.png)

![Configure a price-drop alert](visuals/28-alert-rule-form.png)

![Alert rule saved](visuals/29-alert-rule-created.png)

![Price-drop alert](visuals/30-alert-triggered-and-read.png)

![Alert notification delivered by email](visuals/31-alert-email-delivered.png)

![Collection job history](visuals/32-job-history.png)

![Collection job details](visuals/33-job-detail.png)

## 5. Discover public offerings

Website discovery reads structured product evidence and merges eligible records into the catalog. Private network targets are rejected, and repeat scans update an existing matching offering.

![Private target rejected](visuals/34-private-discovery-target-blocked.png)

![Product discovered](visuals/35-discovery-created.png)

![Discovery history](visuals/36-discovery-upsert.png)

## 6. Workspace and account controls

Settings hold organization details and account security. One-time email links support account verification and password recovery. Roles shape the available actions: analysts can work with intelligence features, while viewers have read-only catalog access.

![Workspace settings](visuals/37-workspace-settings.png)

![Profile updated](visuals/38-workspace-profile-saved.png)

![Password updated](visuals/39-password-changed.png)

![Password reset request](visuals/40-reset-requested.png)

![Password reset form](visuals/41-reset-form.png)

![Password reset completed](visuals/42-reset-completed.png)

![Dashboard after password recovery](visuals/43-dashboard-after-reset.png)

![Analyst view](visuals/44-analyst-workspace.png)

![Viewer read-only view](visuals/45-viewer-read-only.png)

## 7. Mobile workspace and public entry point

![Nexora dashboard at a phone-sized viewport](visuals/46-mobile-dashboard.png)

![Nexora homepage at a phone-sized viewport](visuals/47-mobile-homepage.png)

---

The walkthrough uses an isolated review workspace and sample product data to illustrate Nexora's screens and connected workflow.
