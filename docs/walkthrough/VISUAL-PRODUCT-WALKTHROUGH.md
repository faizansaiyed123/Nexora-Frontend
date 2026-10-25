# Nexora — Visual Product Walkthrough

Nexora brings catalog management, competitor coverage, market collection, website discovery, and alerts into one private market-intelligence workspace. This guide follows the product from account setup through a connected price-monitoring journey, with separate views for workspace administrators, analysts, and read-only users.

## 1. Start a workspace

Create an organization workspace, verify the account email, and sign in to reach the dashboard. The workspace becomes the data boundary for catalog items, competitors, collection history, and alert activity.

### Public Homepage

The public product introduction and entry points.

![The public product introduction and entry points.](screenshots/00-public-homepage.png)

### Registration Form

Workspace registration for the organization and its first administrator.

![Workspace registration for the organization and its first administrator.](screenshots/01-registration-form.png)

### Verification Email Sent

The next step after account registration.

![The next step after account registration.](screenshots/02-verification-email-sent.png)

### Email Verification Page

The one-time email confirmation step.

![The one-time email confirmation step.](screenshots/03-email-verification-page.png)

### Email Verified

Confirmation after the email address is activated.

![Confirmation after the email address is activated.](screenshots/04-email-verified.png)

### Sign In

Secure sign-in to a private workspace.

![Secure sign-in to a private workspace.](screenshots/05-sign-in.png)

### Empty Workspace Dashboard

The starting operating picture before market entities are added.

![The starting operating picture before market entities are added.](screenshots/06-empty-workspace-dashboard.png)

## 2. Establish the competitive landscape

A competitor represents a business to benchmark. A source describes where and how Nexora collects its information; its request limits, retry policy, headers, selectors, health, and circuit state are configurable independently.

### Competitors

Competitor management and the initial market network.

![Competitor management and the initial market network.](screenshots/07-competitors.png)

### Competitor Created

A saved competitor with its domain and status.

![A saved competitor with its domain and status.](screenshots/08-competitor-created.png)

### Duplicate Domain Protection

Duplicate competitor domains are rejected rather than added twice.

![Duplicate competitor domains are rejected rather than added twice.](screenshots/09-duplicate-domain-protection.png)

### Source Create Form

Mapping a collection source to a competitor.

![Mapping a collection source to a competitor.](screenshots/10-source-create-form.png)

### Source Created

The source appears in the workspace with health and circuit state.

![The source appears in the workspace with health and circuit state.](screenshots/11-source-created.png)

### Source Configuration

Rate limits, delays, timeouts, retries, headers, and extraction settings.

![Rate limits, delays, timeouts, retries, headers, and extraction settings.](screenshots/12-source-configuration.png)

### Source Configuration Saved

The saved source configuration and updated source name.

![The saved source configuration and updated source name.](screenshots/13-source-configuration-saved.png)

## 3. Build and maintain the catalog

Offerings are Nexora's canonical records. Each can carry identifiers, price and market context, category, a product URL, and structured attributes. Administrators can edit catalog data, control monitoring, define custom fields, import in bulk, export CSV or JSON, and archive items.

### Offering Create Form

A catalog offering with SKU, price, market, category, and dynamic attributes.

![A catalog offering with SKU, price, market, category, and dynamic attributes.](screenshots/14-offering-create-form.png)

### Catalog Offering Created

The new offering in the searchable catalog.

![The new offering in the searchable catalog.](screenshots/15-catalog-offering-created.png)

### Offering Detail And History

Offering details, match summaries, and price history.

![Offering details, match summaries, and price history.](screenshots/16-offering-detail-and-history.png)

### Catalog Monitoring

Monitoring can be paused and resumed for a catalog offering.

![Monitoring can be paused and resumed for a catalog offering.](screenshots/17-catalog-monitoring.png)

### Dynamic Field Registry

Workspace-specific dynamic catalogue field definitions.

![Workspace-specific dynamic catalogue field definitions.](screenshots/18-dynamic-field-registry.png)

### Dynamic Field Form

Adding a typed, categorized dynamic attribute.

![Adding a typed, categorized dynamic attribute.](screenshots/19-dynamic-field-form.png)

### Dynamic Field Created

The saved dynamic field definition.

![The saved dynamic field definition.](screenshots/20-dynamic-field-created.png)

### Bulk Import Form

Importing multiple offerings with a structured JSON payload.

![Importing multiple offerings with a structured JSON payload.](screenshots/21-bulk-import-form.png)

### Bulk Imported Catalog

Bulk-imported product records in the same catalog.

![Bulk-imported product records in the same catalog.](screenshots/22-bulk-imported-catalog.png)

## 4. Connect offerings and collect market observations

An offering match connects an internal catalog item to a specific competitor source URL. Running a collection makes an HTTP request to the selected page, extracts available price and product signals, and records an observation and current snapshot. This history gives the rest of the workspace something concrete to compare.

The visual example follows structured product pages with reproducible price points, so the progression from the first observation to a later price movement is clear.

### Catalog Import Export Archive

CSV/JSON export, search, and reversible catalog archiving.

![CSV/JSON export, search, and reversible catalog archiving.](screenshots/23-catalog-import-export-archive.png)

### Offering Match Form

Connecting an internal offering to a competitor source URL.

![Connecting an internal offering to a competitor source URL.](screenshots/24-offering-match-form.png)

### Offering Match Created

The saved match and its confidence/status.

![The saved match and its confidence/status.](screenshots/25-offering-match-created.png)

### First Price Observation

The first collected price and saved observation.

![The first collected price and saved observation.](screenshots/26-first-price-observation.png)

## 5. Turn changes into signals

Alert rules define the events worth surfacing. When a later observation meets the threshold, Nexora records an alert and queues the configured notification. Users can review alerts and inspect the execution history behind collection or discovery jobs.

### Alert Rule Form

An alert threshold and scope for a monitored offering.

![An alert threshold and scope for a monitored offering.](screenshots/27-alert-rule-form.png)

### Alert Rule Created

The rule saved in the workspace.

![The rule saved in the workspace.](screenshots/28-alert-rule-created.png)

### Alert Triggered And Read

A price movement becomes an alert that can be marked as read.

![A price movement becomes an alert that can be marked as read.](screenshots/29-alert-triggered-and-read.png)

### Collection Job History

Collection job history and outcome counts.

![Collection job history and outcome counts.](screenshots/30-collection-job-history.png)

### Collection Job Detail

A job's identifiers, processed counts, and run metadata.

![A job's identifiers, processed counts, and run metadata.](screenshots/31-collection-job-detail.png)

## 6. Discover offerings from a public website

Website discovery checks public pages for structured product evidence and can create or update records in the catalog. Nexora also rejects private or loopback destinations before fetching, helping protect the application's network boundary. Re-running the same scan updates a matching record rather than creating an unnecessary duplicate.

### Private Target Blocked

Server-side protection against private/loopback discovery targets.

![Server-side protection against private/loopback discovery targets.](screenshots/32-private-target-blocked.png)

### Discovered Catalog Item

A product found from structured public-page information.

![A product found from structured public-page information.](screenshots/33-discovered-catalog-item.png)

### Discovery Upsert History

Re-running discovery updates a matching offering instead of duplicating it.

![Re-running discovery updates a matching offering instead of duplicating it.](screenshots/34-discovery-upsert-history.png)

## 7. Maintain the workspace and account

Workspace settings keep organization identity and market defaults current. Account settings also support changing a password and recovering access through a one-time email link.

### Workspace Settings

Organization profile and account security settings.

![Organization profile and account security settings.](screenshots/35-workspace-settings.png)

### Workspace Profile Saved

The updated workspace profile.

![The updated workspace profile.](screenshots/36-workspace-profile-saved.png)

### Password Changed

Password change with the old credential no longer accepted.

![Password change with the old credential no longer accepted.](screenshots/37-password-changed.png)

### Password Reset Requested

Password recovery requested from the sign-in screen.

![Password recovery requested from the sign-in screen.](screenshots/38-password-reset-requested.png)

### Password Reset Form

The one-time reset link opens the password replacement form.

![The one-time reset link opens the password replacement form.](screenshots/39-password-reset-form.png)

### Password Reset Complete

Confirmation that password recovery completed.

![Confirmation that password recovery completed.](screenshots/40-password-reset-complete.png)

### Dashboard After Reset

Signing in again after password recovery.

![Signing in again after password recovery.](screenshots/41-dashboard-after-reset.png)

## 8. Access follows the user's role

Administrators configure the market network and workspace; analysts can investigate data and run discovery; viewers can inspect available information without administrator-only write controls.

### Analyst Workspace

Analyst access to review data and run discovery without administrator-only setup controls.

![Analyst access to review data and run discovery without administrator-only setup controls.](screenshots/42-analyst-workspace.png)

### Viewer Read Only Workspace

Viewer access: data remains available while write controls are withheld.

![Viewer access: data remains available while write controls are withheld.](screenshots/43-viewer-read-only-workspace.png)

### Mobile Homepage

The public entry point at a narrow mobile viewport.

![The public entry point at a narrow mobile viewport.](screenshots/44-mobile-homepage.png)

## Product flow at a glance

**Workspace → Competitors → Sources → Catalog → Offering matches → Collection → Observations and snapshots → Alert rules and notifications → Discovery and ongoing catalog maintenance.**

Each step contributes to the same tenant-scoped workspace, so operators can move from source configuration to price history and back to the event that needs their attention.
