# Nexora — Product Walkthrough

Nexora is a private market-intelligence workspace for teams who need to understand catalog coverage, competitor pricing, product availability, and changes in the market.

This walkthrough follows one connected journey: create a workspace, map a competitor, configure a source, organise an offering catalogue, collect market observations, turn a price movement into an alert, discover new catalogue items, and manage access and account security.

## 1. A private workspace

The public entry introduces Nexora's market-intelligence capabilities. An organisation creates its workspace and verifies its email before signing in. Workspace data belongs to that organisation, while role-based access controls which actions each team member can take.

![Nexora public homepage](screenshots/00-public-homepage.png)

![Account registration](screenshots/01-registration-form.png)

![Verification message](screenshots/02-verification-email-sent.png)

![Email verification](screenshots/03-email-verification.png)

![Verified account](screenshots/04-email-verified.png)

![Workspace dashboard](screenshots/05-workspace-dashboard.png)

## 2. Map the competitive landscape

Competitors represent the businesses being monitored. Sources describe the public pages Nexora can collect from, including the source type, retrieval method, request limits, retry behavior, and extraction selectors. Duplicate competitor domains are rejected so the workspace does not accidentally create duplicate market entities.

![Competitor directory](screenshots/06-competitor-directory.png)

![Competitor created](screenshots/07-competitor-created.png)

![Duplicate-domain protection](screenshots/08-duplicate-domain-blocked.png)

![Create a source](screenshots/09-source-creation-form.png)

![Source collection configuration](screenshots/10-source-configuration.png)

![Configured source](screenshots/11-source-ready.png)

## 3. Build the canonical catalogue

The catalogue stores the team's own products, services, plans, and other offerings. Core commercial data sits alongside dynamic attributes such as brand, category-specific specifications, and other comparable properties. Teams can review an offering's detail and history, change its monitored state, manage dynamic field definitions, bulk import catalog entries, export CSV or JSON, and archive items that are no longer active.

![Offering editor](screenshots/12-offering-editor.png)

![Catalogue offering](screenshots/13-catalog-offering.png)

![Offering detail and price history](screenshots/14-offering-detail.png)

![Monitoring controls](screenshots/15-monitoring-controls.png)

![Dynamic field definitions](screenshots/16-dynamic-fields.png)

![Dynamic field editor](screenshots/17-dynamic-field-editor.png)

![Bulk import](screenshots/18-bulk-import-form.png)

![Bulk catalogue operations](screenshots/19-catalog-bulk-export-archive.png)

## 4. Connect offers to market observations

An offering match connects one catalogue entry to a competitor's specific product or pricing page. From that connection, Nexora retrieves the page, extracts available price and availability data, and records an observation and current snapshot. Repeated collections establish a history, including the direction and percentage of price movement.

![Offering match editor](screenshots/20-offering-match-editor.png)

![Offering match created](screenshots/21-offering-match-created.png)

![First collected price observation](screenshots/22-first-live-price-observation.png)

## 5. Turn market movements into signals

Alert rules describe which events matter to the team, such as a percentage price drop, a fixed price change, availability changes, or a source circuit breaker. Matching observations produce persistent alert history. Team members can review an event and mark it as read, while email delivery uses the notification outbox so delivery status remains traceable.

![Alert centre](screenshots/23-alert-center.png)

![Alert rule editor](screenshots/24-alert-rule-editor.png)

![Price movement and alert acknowledgement](screenshots/25-alert-event-and-read-state.png)

## 6. Follow execution and discover new catalogue items

Collection and discovery jobs retain execution status, counts, timestamps, and useful failure context. Website discovery checks public pages for structured product data and can add new offerings or update matching records. Private and loopback destinations are blocked rather than fetched.

![Job history](screenshots/26-job-history.png)

![Job detail](screenshots/27-job-detail.png)

![Private discovery destination blocked](screenshots/28-private-discovery-target-blocked.png)

![Discovered product](screenshots/29-discovered-product.png)

![Discovery history and catalogue update](screenshots/30-discovery-history-and-upsert.png)

## 7. Workspace controls and account recovery

Workspace settings hold organisation details such as company, country, currency, market, industry, and timezone. Account security includes changing the current password and a one-time email-based reset flow. These controls help teams keep the workspace details and access credentials current.

![Workspace settings](screenshots/31-workspace-settings.png)

![Updated workspace profile](screenshots/32-workspace-profile-updated.png)

![Password changed](screenshots/33-password-changed.png)

![Password reset request](screenshots/34-password-reset-requested.png)

![Password reset form](screenshots/35-password-reset-form.png)

![Password reset complete](screenshots/36-password-reset-complete.png)

![Dashboard after recovery](screenshots/37-dashboard-after-reset.png)

## 8. Access appropriate to each role

The same workspace can support analysts who inspect market data and initiate discovery, alongside viewers who can inspect permitted data without being able to create catalogue or competitor records. The API enforces these permission boundaries even when requests bypass the interface.

![Analyst workspace](screenshots/38-analyst-workspace.png)

![Viewer workspace](screenshots/39-viewer-read-only-workspace.png)

## 9. Designed for smaller screens

The public entry adapts to a mobile viewport while retaining the key route into the workspace.

![Nexora on mobile](screenshots/40-mobile-homepage.png)

---

Nexora connects account security, tenant-aware access, catalogue management, competitor sources, collection, discovery, job history, alerts, and notification delivery into one operating workflow.
