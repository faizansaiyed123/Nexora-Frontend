# Nexora — Visual Product Walkthrough

Nexora is a competitive price-intelligence workspace for teams that connect their product catalogue with external market sources. This walkthrough follows the product journey from workspace creation through catalogue management, source configuration, price collection, alerts, website discovery, account security and role-aware access.

The focus is the connected product experience: a user takes an action in the interface, the Nexora API applies domain rules, and the resulting record can be revisited from the appropriate workspace screens.

## 1. Public entry and account security

Nexora begins with a public introduction, then moves a new workspace through email verification and authenticated sign-in. The browser follows one-time links from messages delivered to a local STARTTLS inbox.

### Public homepage

The public product entry point.

![Public homepage](screenshots/00-public-homepage.png)

### Workspace registration

Organization, user and password fields.

![Workspace registration](screenshots/01-registration-form.png)

### Verification requested

The account awaits email confirmation.

![Verification requested](screenshots/02-verification-email-sent.png)

### Verify email

The delivered one-time verification link.

![Verify email](screenshots/03-email-verification-page.png)

### Email verified

Successful activation before sign-in.

![Email verified](screenshots/04-email-verified.png)

### Sign in

Workspace sign-in.

![Sign in](screenshots/05-login.png)

### New workspace dashboard

Dashboard from the authenticated API.

![New workspace dashboard](screenshots/06-dashboard-empty-workspace.png)

## 2. Competitor network and collection sources

A workspace owner defines competitors, handles duplicate-domain protection, adds collection endpoints and configures request limits, timeout, retries, headers and extraction settings.

### Competitor directory

An unconfigured market network.

![Competitor directory](screenshots/07-competitors-empty.png)

### Competitor saved

A persisted competitor row.

![Competitor saved](screenshots/08-competitor-created.png)

### Duplicate domain guard

The server rejects a duplicate competitor domain.

![Duplicate domain guard](screenshots/09-duplicate-domain-rejected.png)

### Add collection source

Connect a competitor to a page.

![Add collection source](screenshots/10-source-creation-form.png)

### Source connected

Saved collection source and health information.

![Source connected](screenshots/11-sources-created.png)

### Source configuration

Rate, delay, timeout, retries, headers and selectors.

![Source configuration](screenshots/12-source-configuration.png)

### Configured source

Configuration read back after saving.

![Configured source](screenshots/13-source-configuration-saved.png)

## 3. Product catalogue and dynamic schema

The catalogue supports product creation, detail/history, price changes, monitoring controls, tenant-specific fields, bulk import, CSV/JSON export, and soft archival.

### Add catalog offering

Product data and attributes.

![Add catalog offering](screenshots/14-offering-creation-form.png)

### Catalog record

The offering appears in the catalog.

![Catalog record](screenshots/15-catalog-offering-created.png)

### Offering detail

Details, match metrics and price-history surface.

![Offering detail](screenshots/16-offering-detail-and-history.png)

### Monitoring enabled

Monitoring is paused and resumed.

![Monitoring enabled](screenshots/17-catalog-monitoring-active.png)

### Dynamic field definitions

Tenant-specific catalog schema.

![Dynamic field definitions](screenshots/18-dynamic-fields.png)

### Create dynamic field

Field key, type, unit and category.

![Create dynamic field](screenshots/19-dynamic-field-form.png)

### Dynamic field saved

Saved definition.

![Dynamic field saved](screenshots/20-dynamic-field-created.png)

### Bulk catalog import

Structured JSON multi-item import.

![Bulk catalog import](screenshots/21-bulk-import-form.png)

### Imported catalog

Imported offerings available to search.

![Imported catalog](screenshots/22-bulk-imported-catalog.png)

### Export and archive

CSV/JSON downloads and soft archive.

![Export and archive](screenshots/23-catalog-import-export-and-archive.png)

## 4. Market mapping, price observations and alerts

An offering is mapped to a competitor page. Nexora fetches it over HTTP, persists a collection job, observation and snapshot, then compares a second lower price against a threshold and records an alert with email delivery.

### Map an offering

Link an offering to a competitor URL.

![Map an offering](screenshots/24-offering-match-form.png)

### Offering match

The persisted mapping and confidence.

![Offering match](screenshots/25-offering-match-created.png)

### First price observation

HTTP collection creates an observation and snapshot.

![First price observation](screenshots/26-first-price-observation.png)

### Configure an alert

Price-drop threshold and cooldown.

![Configure an alert](screenshots/27-alert-rule-form.png)

### Alert rule saved

Rule bound to a catalog offering.

![Alert rule saved](screenshots/28-alert-rule-created.png)

### Alert event lifecycle

A lower observed price generates an alert.

![Alert event lifecycle](screenshots/29-alert-generated-and-read.png)

### Collection jobs

Persisted execution history.

![Collection jobs](screenshots/30-collection-job-history.png)

### Collection job details

Job ID and collection metadata.

![Collection job details](screenshots/31-collection-job-detail.png)

## 5. Website discovery and catalog enrichment

Discovery rejects internal targets, reads structured product data from a public HTTP page, saves the discovered offering and job, then updates the same record on a repeat scan.

### Private target protection

Loopback discovery is rejected.

![Private target protection](screenshots/32-private-target-blocked.png)

### Website discovery

Structured evidence becomes a saved offering.

![Website discovery](screenshots/33-discovery-product-created.png)

### Discovery update

A repeat scan updates instead of duplicating.

![Discovery update](screenshots/34-discovery-upsert-history.png)

## 6. Workspace preferences and recovery

Workspace identity can be updated. Password changes reject the old credential, while recovery uses a one-time email link and returns the user to the live dashboard.

### Workspace settings

Organization and account controls.

![Workspace settings](screenshots/35-workspace-settings.png)

### Updated profile

Changes verified through a fresh read.

![Updated profile](screenshots/36-workspace-profile-updated.png)

### Password changed

The previous credential no longer works.

![Password changed](screenshots/37-password-changed.png)

### Recovery requested

A one-time reset email is sent.

![Recovery requested](screenshots/38-password-reset-requested.png)

### Reset password

One-time reset link opens the form.

![Reset password](screenshots/39-password-reset-form.png)

### Password reset complete

The credential is changed.

![Password reset complete](screenshots/40-password-reset-complete.png)

### Sign in after recovery

The new password reaches the dashboard.

![Sign in after recovery](screenshots/41-dashboard-after-password-reset.png)

## 7. Role-aware workspace access

Analyst and viewer sessions use persisted user records and real tokens. The interface adapts to each role, and backend authorization rejects prohibited writes.

### Analyst role

Read access with restricted admin controls.

![Analyst role](screenshots/42-analyst-workspace.png)

### Viewer role

Read-only UI and backend-enforced writes.

![Viewer role](screenshots/43-viewer-read-only-workspace.png)

## 8. Responsive layout and record lifecycle

The last screens cover the public mobile layout and owner-only lifecycle actions: pause/reactivate/delete alert rules, delete matches/sources/competitors and archive an offering.

### Mobile homepage

Responsive public entry point.

![Mobile homepage](screenshots/44-mobile-homepage.png)

### Alert-rule administration

Pause, reactivate and remove an alert rule.

![Alert-rule administration](screenshots/45-alert-rule-lifecycle.png)

### Match removed

Remove a market mapping through the UI.

![Match removed](screenshots/46-match-removed.png)

### Source removed

Delete the collection source.

![Source removed](screenshots/47-source-removed.png)

### Competitor removed

Remove the competitor and dependent data.

![Competitor removed](screenshots/48-competitor-removed.png)

### Offering archived

Retain an archived catalogue record.

![Offering archived](screenshots/49-offering-archived.png)

## Feature coverage at a glance

| Product area | What the journey covers |
|---|---|
| Account onboarding | Workspace registration, email verification, sign-in, password change and one-time reset |
| Competitor network | Competitor create/edit, duplicate-domain prevention, source create/configure/edit and deletion |
| Catalogue | Offering create/edit/detail, dynamic attributes, monitoring, multi-item import, CSV/JSON export, bulk archive and archived-record retrieval |
| Market mapping | Offering-to-source mapping, mapping update/deletion and real HTTP collection |
| Collection operations | Persisted jobs, observations, snapshots, price history and extraction attributes |
| Alerts | Threshold rules, triggered event, read state and queued email delivery |
| Website discovery | Private-target protection, structured extraction, job history and update-without-duplicate behavior |
| Workspace and roles | Profile, password management, analyst restrictions and viewer read-only permissions |
| Responsive design | Public homepage at desktop and mobile viewport sizes |

## Evidence scope

The journey runs the real Nexora frontend against the actual FastAPI application, backed by an isolated PostgreSQL database and Redis service. Collection and discovery make outbound HTTP requests to versioned, publicly served product-page fixtures containing structured retail data. The prices in those fixture pages are repeatable workflow inputs; they are **not** a claim about a vendor's current live price.

Verification, password-reset and alert emails travel through a local STARTTLS inbox inside the isolated workflow. No production account, production database, production SMTP credential or production deployment is used. These screenshots demonstrate the controlled workspace flow and should not be interpreted as certification of the deployed production service.

The screenshot inventory is in [manifest.json](screenshots/manifest.json). Every screenshot is stored as a separate PNG so that individual product states can be reviewed directly.
