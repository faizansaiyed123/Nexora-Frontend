# Nexora — Product Walkthrough

Nexora is a private market-intelligence workspace for teams who need to understand catalog coverage, competitor pricing, product availability, and changes in the market.

This walkthrough follows one connected journey: create a workspace, map a competitor, configure a source, organise an offering catalogue, collect market observations, turn a price movement into an alert, discover new catalogue items, and manage access and account security.

## 1. A private workspace

The public entry introduces Nexora's market-intelligence capabilities. An organisation creates its workspace and verifies its email before signing in. Workspace data belongs to that organisation, while role-based access controls which actions each team member can take.

![Nexora public homepage](screenshots/00-public-homepage.png)

![Account registration](screenshots/01-registration-form.png)

![Verification message](screenshots/02-verification-email-sent.png)

![Email verification](screenshots/03-email-verification-page.png)

![Verified account](screenshots/04-email-verified.png)

![Nexora sign-in](screenshots/05-login.png)

![Workspace dashboard](screenshots/06-dashboard-empty-workspace.png)

## 2. Map the competitive landscape

Competitors represent the businesses being monitored. Sources describe the public pages Nexora can collect from, including the source type, retrieval method, request limits, retry behavior, and extraction selectors. Duplicate competitor domains are rejected so the workspace does not accidentally create duplicate market entities.

![Competitor directory](screenshots/07-competitors-empty.png)

![Competitor created](screenshots/08-competitor-created.png)

![Duplicate-domain protection](screenshots/09-duplicate-domain-rejected.png)

![Create a source](screenshots/10-source-creation-form.png)

![Source created](screenshots/11-sources-created.png)

![Source collection configuration](screenshots/12-source-configuration.png)

![Configured source](screenshots/13-source-configuration-saved.png)

![JavaScript rendering enabled for a source](screenshots/13b-source-js-rendering-enabled.png)

Nexora can use a fast HTTP fetch for ordinary public pages or a browser-rendered page when a source requires JavaScript.

## 3. Build the canonical catalogue

The catalogue stores the team's own products, services, plans, and other offerings. Core commercial data sits alongside dynamic attributes such as brand, category-specific specifications, and other comparable properties. Teams can review an offering's detail and history, change its monitored state, manage dynamic field definitions, bulk import catalog entries, export CSV or JSON, and archive items that are no longer active.

![Offering editor](screenshots/14-offering-creation-form.png)

![Catalogue offering](screenshots/15-catalog-offering-created.png)

![Offering detail and price history](screenshots/16-offering-detail-and-history.png)

![Monitoring controls](screenshots/17-catalog-monitoring-active.png)

![Dynamic field definitions](screenshots/18-dynamic-fields.png)

![Dynamic field editor](screenshots/19-dynamic-field-form.png)

![Dynamic field created](screenshots/20-dynamic-field-created.png)

![Bulk import form](screenshots/21-bulk-import-form.png)

![Imported catalogue items](screenshots/22-bulk-imported-catalog.png)

When an import contains a mix of valid and invalid records, Nexora keeps successful rows and shows the rejected row numbers with their reasons so the operator can correct the input.

![Bulk import row-level results](screenshots/22b-bulk-import-row-errors.png)

![Bulk catalogue operations](screenshots/23-catalog-import-export-and-archive.png)

![Archive an individual catalogue item](screenshots/23b-single-offering-archived.png)

With larger catalogues, the offering list is paginated. The page controls let the team move through the full set while keeping each page manageable.

![Catalogue pagination](screenshots/23c-catalog-pagination.png)

Teams can also filter by offering type, for example separating service entries from products while keeping the rest of the catalog searchable.

![Catalogue filtered by offering type](screenshots/23d-catalog-type-filter.png)

## 4. Connect offers to market observations

An offering match connects one catalogue entry to a competitor's specific product or pricing page. From that connection, Nexora retrieves the page, extracts available price and availability data, and records an observation and current snapshot. Repeated collections establish a history, including the direction and percentage of price movement.

![Offering match editor](screenshots/24-offering-match-form.png)

![Offering match created](screenshots/25-offering-match-created.png)

![First collected price observation](screenshots/26-first-price-observation.png)

## 5. Turn market movements into signals

Alert rules describe which events matter to the team, such as a percentage price drop, a fixed price change, availability changes, or a source circuit breaker. Matching observations produce persistent alert history. Team members can review an event and mark it as read, while email delivery uses the notification outbox so delivery status remains traceable.

![Alert centre](screenshots/27-alert-rule-form.png)

![Alert rule editor](screenshots/28-alert-rule-created.png)

![Price movement and alert acknowledgement](screenshots/29-alert-generated-and-read.png)

A source that keeps failing is handled as an operational event, not just a failed job. After repeated unsuccessful collections, Nexora opens the source circuit, prevents immediate repeat requests, and records a circuit-breaker alert for the team to review.

![Circuit-breaker alert rule](screenshots/29b-circuit-breaker-rule-form.png)

![Source health after the circuit opens](screenshots/29c-source-circuit-open.png)

![Persistent circuit-breaker alert](screenshots/29d-circuit-breaker-alert.png)

## 6. Follow execution and discover new catalogue items

Collection and discovery jobs retain execution status, counts, timestamps, and useful failure context. Website discovery checks public pages for structured product data and can add new offerings or update matching records. Private and loopback destinations are blocked rather than fetched.

![Job history](screenshots/30-collection-job-history.png)

![Job detail](screenshots/31-collection-job-detail.png)

![Private discovery destination blocked](screenshots/32-private-target-blocked.png)

![Discovered product](screenshots/33-discovery-product-created.png)

![Discovery history and catalogue update](screenshots/34-discovery-upsert-history.png)

## 7. Workspace controls and account recovery

Workspace settings hold organisation details such as company, country, currency, market, industry, and timezone. Account security includes changing the current password and a one-time email-based reset flow. These controls help teams keep the workspace details and access credentials current.

![Workspace settings](screenshots/35-workspace-settings.png)

![Updated workspace profile](screenshots/36-workspace-profile-updated.png)

![Password changed](screenshots/37-password-changed.png)

![Password reset request](screenshots/38-password-reset-requested.png)

![Password reset form](screenshots/39-password-reset-form.png)

![Password reset complete](screenshots/40-password-reset-complete.png)

![Dashboard after recovery](screenshots/41-dashboard-after-password-reset.png)

## 8. Access appropriate to each role

The same workspace can support analysts who inspect market data and initiate discovery, alongside viewers who can inspect permitted data without being able to create catalogue or competitor records. The API enforces these permission boundaries even when requests bypass the interface.

![Analyst workspace](screenshots/42-analyst-workspace.png)

![Viewer workspace](screenshots/43-viewer-read-only-workspace.png)

![Super Admin workspace](screenshots/44-super-admin-workspace.png)

## 9. Live public price reference

The connected example also reads the [Sony Center retail listing](https://shopatsc.com/collections/all/products/wh1000xm5-pmin) at run time rather than assigning a fixed price, because retail prices can change by date and market.

![Live Sony Center retail source](screenshots/45-live-retail-source.png)

![Live retail price in the offering comparison](screenshots/46-live-retail-price-comparison.png)

## 10. Designed for smaller screens

The public entry adapts to a mobile viewport while retaining the key route into the workspace.

![Nexora on mobile](screenshots/47-mobile-homepage.png)

---

Nexora connects account security, tenant-aware access, catalogue management, competitor sources, collection, discovery, job history, alerts, and notification delivery into one operating workflow.
