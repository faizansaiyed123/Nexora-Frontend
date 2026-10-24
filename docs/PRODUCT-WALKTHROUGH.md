# Nexora — Product Walkthrough

Nexora brings catalog intelligence, competitor coverage, website discovery, collection jobs and alerts into one private workspace. This guide follows a representative journey from account creation through a price-change signal and website discovery.

**Sample-data note:** the price movement in this walkthrough uses controlled structured pages maintained for this demonstration. The amounts are not claims about current Sony retail prices or live market conditions. Screenshots show application behavior and do not certify a production deployment.

## 1. Enter Nexora

Nexora starts with a private workspace for each organization. Registration establishes that workspace, email verification activates access, and the dashboard anchors the market workflow.

### Public homepage

![Public homepage](walkthrough/screenshots/00-public-homepage.png)

Nexora introduces a private competitive-intelligence workspace.

### Create a workspace

![Create a workspace](walkthrough/screenshots/01-registration-form.png)

Organization and first user are registered together.

### Email verification requested

![Email verification requested](walkthrough/screenshots/02-verification-email-sent.png)

Account activation requires a one-time email link.

### Email verified

![Email verified](walkthrough/screenshots/03-email-verified.png)

Successful verification returns the user to sign-in.

### Workspace dashboard

![Workspace dashboard](walkthrough/screenshots/04-workspace-dashboard.png)

The dashboard is the operating overview for catalog, market and collection activity.

## 2. Define competitors and sources

Competitors represent the businesses being watched. Sources point to public pages that can be collected; configuration allows request rate, delay, timeout, retries, headers and extraction rules to be adjusted per source.

### Competitor created

![Competitor created](walkthrough/screenshots/05-competitor-created.png)

A competitor can be associated with sources and tracked offerings.

### Duplicate domain prevented

![Duplicate domain prevented](walkthrough/screenshots/06-duplicate-domain-blocked.png)

The server rejects a second competitor with the same tenant domain.

### Configured collection source

![Configured collection source](walkthrough/screenshots/07-source-config-saved.png)

A source ties a competitor to a page and stores request/extraction settings.

## 3. Build a catalog

The canonical catalog stores the products and services the organization cares about. Its workflow includes editable attributes, monitoring controls, organization-specific fields, bulk imports, exports and archive actions.

### Catalog offering created

![Catalog offering created](walkthrough/screenshots/08-offering-created.png)

The record is available for searching, monitoring and competitive mapping.

### Offering detail

![Offering detail](walkthrough/screenshots/09-offering-detail.png)

Current price, dynamic attributes, matches and observation history are in one view.

### Monitoring controls

![Monitoring controls](walkthrough/screenshots/10-monitoring-control.png)

Tracking can be paused and resumed while preserving the offering.

### Dynamic catalog fields

![Dynamic catalog fields](walkthrough/screenshots/11-dynamic-fields.png)

Organization-specific data fields can be added and managed.

### Catalog import, export and archive

![Catalog import, export and archive](walkthrough/screenshots/12-bulk-import-export-archive.png)

Bulk JSON import and CSV/JSON export sit alongside archive controls.

## 4. Match and collect

A match connects an internal offering to an exact competitor page. Collection retrieves that page and records its extracted price, the HTTP outcome and a historical observation.

### Offering match created

![Offering match created](walkthrough/screenshots/13-offering-match-created.png)

A saved match links the internal offering to a competitor page.

### First price observation

![First price observation](walkthrough/screenshots/14-first-price-observation.png)

The collector retrieves the structured public page and persists a price snapshot.

## 5. Turn changes into signals

Alert rules define meaningful price movement. A later collection crossing the configured threshold creates an event, updates alert history and queues an email notification. Collection jobs remain available for context.

### Price-drop rule

![Price-drop rule](walkthrough/screenshots/15-alert-rule-created.png)

A rule defines the monitored item and threshold for market movement.

### Price alert and event history

![Price alert and event history](walkthrough/screenshots/16-price-alert-triggered.png)

A second lower observation creates a persistent alert that can be marked read.

### Collection job history

![Collection job history](walkthrough/screenshots/17-collection-jobs.png)

Execution status and outcome details remain available to the workspace.

## 6. Discover additional offerings

Website discovery looks for structured data on public pages and merges discovered products into the catalog. Private targets are rejected, and repeat scans update a matching record instead of adding a duplicate.

### Private discovery target blocked

![Private discovery target blocked](walkthrough/screenshots/18-private-target-rejected.png)

Server-side URL validation refuses loopback and private targets.

### Website discovery

![Website discovery](walkthrough/screenshots/19-discovery-created.png)

Structured product information is turned into a catalog candidate.

### Discovery updates an existing item

![Discovery updates an existing item](walkthrough/screenshots/20-discovery-upsert.png)

A repeated scan updates a matching record rather than duplicating it.

## 7. Workspace, credentials and roles

Organization settings and account security are part of the same workspace. Administrator, analyst, viewer and super-admin roles receive the relevant controls exposed by the application.

### Workspace profile

![Workspace profile](walkthrough/screenshots/21-workspace-profile.png)

Company identity, market, currency, industry and timezone are configurable.

### Password changed

![Password changed](walkthrough/screenshots/22-password-changed.png)

The new credential works, and the previous password is rejected.

### Password reset requested

![Password reset requested](walkthrough/screenshots/23-password-reset-requested.png)

A one-time recovery link is sent through the email path.

### Password recovery complete

![Password recovery complete](walkthrough/screenshots/24-password-reset-completed.png)

The reset token is consumed and cannot be replayed.

### Return to the workspace

![Return to the workspace](walkthrough/screenshots/25-dashboard-after-recovery.png)

The account signs into the same tenant after recovery.

### Analyst role

![Analyst role](walkthrough/screenshots/26-analyst-access.png)

Analysts can explore data and run allowed intelligence tasks without admin write controls.

### Viewer role

![Viewer role](walkthrough/screenshots/27-viewer-read-only.png)

Viewers can inspect permitted records but cannot create or edit protected resources.

### Super-admin role

![Super-admin role](walkthrough/screenshots/28-super-admin-access.png)

The administrative controls implemented by the product are available to super-admins.

### Mobile homepage

![Mobile homepage](walkthrough/screenshots/29-mobile-homepage.png)

The public introduction remains usable on a narrow viewport.

## Product areas covered

- **Workspace access:** registration, email verification, sign-in, password change and recovery.
- **Market workspace:** competitor and source management, catalog attributes, dynamic fields, import/export, archive and offering matches.
- **Intelligence:** public-page collection, price observations, discovery, job history, persistent alerts and email notifications.
- **Access:** organization administrator, analyst, viewer and super-admin views.
