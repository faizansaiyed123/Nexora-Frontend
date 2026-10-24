# Nexora — Visual Product Walkthrough

Nexora connects a team's product catalogue to competitor pages, collects observable market prices, records price history, and turns meaningful changes into alerts. This walkthrough follows a single Northstar workspace from account creation through monitoring and review.

The screenshots are captured from the browser running the actual frontend against the FastAPI service and a dedicated PostgreSQL database. The example catalogue and competitor pages are repeatable review data; collection still uses real HTTP requests, and resulting observations, jobs, settings, and alert records are persisted by the application. The disposable review environment is separate from any production deployment.

## 1. Enter the workspace

The public site introduces the market-intelligence workflow. An organization can register, receive an email verification link, activate the account, and sign in. Account recovery uses a one-time reset link delivered through the isolated review inbox.

![Nexora public homepage](./screenshots/00-public-homepage.png)

![Workspace registration](./screenshots/01-registration-form.png)

![Verification email requested](./screenshots/02-verification-email-sent.png)

![Email verification page](./screenshots/03-email-verification-page.png)

![Email verified](./screenshots/04-email-verified.png)

![Sign in](./screenshots/05-login.png)

![New workspace dashboard](./screenshots/06-dashboard-empty-workspace.png)

## 2. Define the competitive landscape

Competitors identify the external businesses being monitored. Source records describe the pages Nexora reads, while each source can be configured with request pacing, timeout and retry settings, headers, and extraction selectors. Duplicate competitor domains are rejected rather than silently creating duplicate entities.

![Competitor list before setup](./screenshots/07-competitors-empty.png)

![Competitor created](./screenshots/08-competitor-created.png)

![Duplicate competitor domain handled](./screenshots/09-duplicate-domain-rejected.png)

![New collection source](./screenshots/10-source-creation-form.png)

![Source connected to competitor](./screenshots/11-sources-created.png)

![Collection source configuration](./screenshots/12-source-configuration.png)

![Saved source configuration](./screenshots/13-source-configuration-saved.png)

## 3. Build and maintain the catalogue

The catalogue stores an offering's canonical name, type, SKU, price, market, category, description, and dynamic attributes. Teams can inspect details and history, edit product information, pause or resume monitoring, define their own comparable attributes, import several entries together, export CSV or JSON, and archive selected entries.

![New catalogue offering](./screenshots/14-offering-creation-form.png)

![Offering in the catalogue](./screenshots/15-catalog-offering-created.png)

![Offering details and price history](./screenshots/16-offering-detail-and-history.png)

![Monitoring state](./screenshots/17-catalog-monitoring-active.png)

![Dynamic field definitions](./screenshots/18-dynamic-fields.png)

![Create a dynamic field](./screenshots/19-dynamic-field-form.png)

![Dynamic field saved](./screenshots/20-dynamic-field-created.png)

![Bulk catalogue import](./screenshots/21-bulk-import-form.png)

![Imported catalogue entries](./screenshots/22-bulk-imported-catalog.png)

![Catalogue export and archiving](./screenshots/23-catalog-import-export-and-archive.png)

## 4. Connect pages and collect market observations

An offering match connects a catalogue item to a specific competitor URL. A collection run requests that page, extracts price and availability signals, records an observation, updates the latest snapshot, and creates a job record. This example observes a price of $399.99 and then a lower $349.99 value so the price-history and alert paths can be followed reliably.

![Map an offering to a source URL](./screenshots/24-offering-match-form.png)

![Created offering match](./screenshots/25-offering-match-created.png)

![First market-price observation](./screenshots/26-first-price-observation.png)

## 5. Turn changes into alerts

Alert rules define the kind of market movement worth surfacing, the threshold, and the cooldown. When the second collection records a 12.5% drop, Nexora persists an alert, delivers a notification through the isolated STARTTLS mail sink, and lets an analyst mark the alert as read.

![Alert rule configuration](./screenshots/27-alert-rule-form.png)

![Saved alert rule](./screenshots/28-alert-rule-created.png)

![Price-drop alert in the activity log](./screenshots/29-alert-generated-and-read.png)

## 6. Review execution and discover new offerings

The Jobs area exposes collection and discovery runs, outcomes, and job metadata. Website discovery can extract a product when the page contains explicit structured data, adds or updates matching catalogue records, and retains a run history. Private or loopback targets are rejected by server-side URL validation.

![Collection jobs](./screenshots/30-collection-job-history.png)

![Collection job details](./screenshots/31-collection-job-detail.png)

![Blocked private destination](./screenshots/32-private-target-blocked.png)

![Discovered product added to the catalogue](./screenshots/33-discovery-product-created.png)

![Discovery history and repeat-run update](./screenshots/34-discovery-upsert-history.png)

## 7. Workspace settings, access, and recovery

Administrators can update their organization's profile and change passwords. The review flow also requests a reset email, follows its one-time link, and signs in with the new password. The same data model is exercised with analyst and viewer roles so the interface and server enforce different write permissions.

![Workspace settings](./screenshots/35-workspace-settings.png)

![Updated workspace profile](./screenshots/36-workspace-profile-updated.png)

![Password changed from settings](./screenshots/37-password-changed.png)

![Password reset requested](./screenshots/38-password-reset-requested.png)

![Password reset form](./screenshots/39-password-reset-form.png)

![Password reset complete](./screenshots/40-password-reset-complete.png)

![Dashboard after password reset](./screenshots/41-dashboard-after-password-reset.png)

![Analyst workspace and permissions](./screenshots/42-analyst-workspace.png)

![Viewer read-only workspace](./screenshots/43-viewer-read-only-workspace.png)

![Responsive layout on a mobile viewport](./screenshots/44-mobile-homepage.png)

## What this walkthrough demonstrates

- Organization registration, email verification, sign-in, password change, and one-time password reset.
- Competitor and collection-source management, including persisted source configuration and duplicate-domain handling.
- Catalogue create/update/detail/history, monitoring toggles, dynamic fields, bulk import/archive, and CSV/JSON export.
- Offering-to-source matching, live HTTP collection, persisted observations and snapshots, job history, and threshold-triggered alerts.
- Structured website discovery, create-versus-update behavior, and blocking of private network destinations.
- Role-aware interface and API permissions for administrator, analyst, and viewer accounts.
- Data read-back from fresh API requests and the PostgreSQL records created by the same UI actions.

The example pages are stable review fixtures so price-extraction and alert outcomes are repeatable. They do not represent a statement that any production domain, production account, or production deployment has been certified.
