# Nexora — Visual Product Walkthrough

Nexora brings catalogue management, competitive-source mapping, price collection, website discovery, and alerting into one private market-intelligence workspace. This walkthrough follows a retail-pricing scenario from account creation through a competitor price change.

The example catalogue uses Sony headphone listings. The collection pages contain structured product data so the price and product identity are read from an actual HTTP response rather than invented in the interface.

## 1. Enter the workspace

The public page introduces Nexora and the workspace entry points. New customers create an organization, verify the email sent to their address, and sign in to a tenant-scoped workspace.

![Nexora public homepage](screenshots/00-public-homepage.png)

![Workspace registration form](screenshots/01-registration-form.png)

![Verification email sent](screenshots/02-verification-email-sent.png)

![Email verification page](screenshots/03-email-verification.png)

![Sign-in page](screenshots/04-login.png)

![Workspace dashboard](screenshots/05-dashboard.png)

## 2. Map the competitive landscape

Competitors identify the businesses or domains being tracked. Nexora prevents duplicate competitor domains within a workspace. Sources define where collection starts and which method, request limits, timeout, retry behavior, headers, and extraction settings apply.

![Competitor directory](screenshots/06-competitors.png)

![Duplicate competitor domain is rejected](screenshots/07-duplicate-domain-prevented.png)

![Create a collection source](screenshots/08-source-form.png)

![Source collection configuration](screenshots/09-source-configuration.png)

![Saved source configuration](screenshots/10-source-configuration-saved.png)

## 3. Build and maintain the catalogue

The catalogue stores the canonical item, SKU, price, currency, market, category, and dynamic attributes used for comparison. Item detail combines the offering with matching and price-history information. Monitoring can be paused or resumed. Teams can define additional comparable fields, bulk-import records, export CSV or JSON, and archive items without deleting their history.

![Add a catalogue offering](screenshots/11-catalog-offering-form.png)

![New catalogue offering](screenshots/12-catalog-offering-created.png)

![Offering detail and competitive context](screenshots/13-offering-detail.png)

![Monitoring controls](screenshots/14-monitoring-toggle.png)

![Additional catalogue field](screenshots/15-dynamic-field-created.png)

![Bulk catalogue import](screenshots/16-bulk-import-form.png)

![Imported catalogue records](screenshots/17-bulk-imported.png)

![Catalogue export and archive workflow](screenshots/18-catalog-export-and-archive.png)

## 4. Collect competitor prices and react to changes

An offering match connects a catalogue item to a specific competitor URL. A collection fetches the source page and extracts its structured product fields. The observation and snapshot establish the current price and its previous value. Alert rules turn a configured percentage change into a persistent event, and eligible email notifications are delivered through the notification outbox.

In this example, the price changes from $399.99 to $349.99—about a 12.50% decrease—crossing a 10% alert threshold.

![Map an offering to a competitor URL](screenshots/19-match-form.png)

![Offering match connected to a source](screenshots/20-offering-match.png)

![First saved price observation](screenshots/21-first-price-observation.png)

![Configure a price-drop rule](screenshots/22-alert-rule-form.png)

![Price alert rule in the workspace](screenshots/23-alert-rule-created.png)

![Price-drop alert and read state](screenshots/24-alert-triggered-and-read.png)

## 5. Follow collection and discovery activity

The jobs view provides execution history and job details. Website discovery checks public URLs and extracts supported, evidence-backed product details into the same catalogue. Private or loopback destinations are rejected to prevent the collector from reaching internal services. Running discovery again updates the matching record rather than creating a duplicate.

![Collection job history](screenshots/25-job-history.png)

![Collection job details](screenshots/26-job-details.png)

![Private target rejected](screenshots/27-private-target-blocked.png)

![Discovered offering in the catalogue](screenshots/28-discovery-created.png)

![Discovery updates the existing matching offering](screenshots/29-discovery-upsert.png)

## 6. Workspace ownership and access

Workspace administrators can update organization settings and account credentials. Email-based recovery uses a one-time reset link. Analyst access supports investigation and discovery while keeping administrative mutations restricted; Viewer access is read-only for catalogue data. These boundaries are enforced by the API as well as reflected in the interface.

![Workspace settings](screenshots/30-workspace-settings.png)

![Password changed from account settings](screenshots/31-password-changed.png)

![Password recovery request](screenshots/32-password-reset-requested.png)

![Password reset form from the email link](screenshots/33-password-reset-form.png)

![Password reset confirmation](screenshots/34-password-reset-complete.png)

![Sign in after password recovery](screenshots/35-dashboard-after-reset.png)

![Analyst role workspace](screenshots/36-analyst-permissions.png)

![Viewer read-only workspace](screenshots/37-viewer-read-only.png)

## 7. Responsive entry point

The public entry page remains usable on a narrow mobile viewport as well as desktop.

![Nexora homepage on mobile](screenshots/38-mobile-homepage.png)

---

*Walkthrough data belongs to an isolated review workspace. It is not production customer data, and these screens should not be read as certification of a live production deployment.*
