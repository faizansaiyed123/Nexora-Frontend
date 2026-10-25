#!/usr/bin/env python3
"""Build a visitor- and interviewer-friendly guide from successful browser captures."""
from __future__ import annotations
import os
from pathlib import Path

root = Path(os.getenv("NEXORA_SCREENSHOT_DIR", "docs/walkthrough/screenshots"))
target = Path("docs/walkthrough/NEXORA-PRODUCT-WALKTHROUGH.md")
screens = [
("01-public-homepage.png","The public homepage","Nexora introduces a focused workspace for catalog intelligence, competitor coverage, website discovery, collection activity and alerts."),
("02-registration-form.png","Create a workspace","An organization starts with its own tenant boundary, named operator and work email."),
("03-verification-requested.png","Verify account ownership","Registration requires confirmation of the work email before the account can enter the workspace."),
("04-verification-link.png","Use the email verification link","The one-time link brings the operator to the account activation page."),
("05-account-verified.png","Account activation complete","Once the server accepts the verification token, the operator can sign in."),
("06-sign-in.png","Secure sign-in","The sign-in screen provides access to the private workspace."),
("07-workspace-dashboard.png","The operating picture","The dashboard summarizes tracked offerings, competitors, collection sources and recent execution activity for the current tenant."),
("08-workspace-profile.png","Workspace profile and account security","Organization identity, market, currency, industry, timezone and password controls live in Settings."),
("09-competitors.png","Competitor landscape","Competitors identify the public businesses against which a team benchmarks its catalog."),
("10-competitor-created.png","Add a competitor","A competitor is connected to the current workspace and becomes available when defining sources."),
("11-duplicate-competitor-blocked.png","Keep the competitor set clean","Duplicate domains are rejected within a workspace so the same business is not registered twice by accident."),
("12-sources.png","Collection sources","Sources identify the page or endpoint Nexora will retrieve and the collection approach used."),
("13-source-created.png","Connect a public source","A source belongs to a competitor and is ready to be configured."),
("14-source-configuration.png","Collection controls","Rate limits, delays, timeout, retries, request headers and extraction selectors can be tuned for a source."),
("15-source-settings-saved.png","Save source configuration","The saved configuration remains attached to its source and informs subsequent collection runs."),
("16-catalog.png","Catalog intelligence","Offerings are the canonical catalog items used for comparison and monitoring."),
("17-offering-created.png","Create a tracked offering","The catalog stores a product's name, SKU, current price, currency, market, category, description and dynamic attributes."),
("18-offering-detail.png","Offering detail and comparison","The detail view brings together current price, monitoring state, match coverage and historical context."),
("19-catalog-edit-and-monitoring.png","Manage monitoring","Teams can amend catalog details and explicitly pause or resume monitoring."),
("20-dynamic-fields.png","Flexible domain attributes","Dynamic fields let a workspace describe values that vary by product vertical without changing the core offering model."),
("21-dynamic-field-created.png","Define a new field","Field definitions have a machine key, display name, data type, unit and category."),
("22-bulk-import-form.png","Bulk catalog intake","The importer accepts multiple offering objects in a single structured payload."),
("23-catalog-import-export-archive.png","Import, export and archive","CSV and JSON exports support downstream analysis; archive actions keep removed items out of the active catalog."),
("24-offering-matches.png","Map competitor listings","A match connects an internal offering to the exact public URL where a competitor lists a comparable item."),
("25-offering-match-created.png","Review a mapped listing","Match status and confidence help distinguish accepted comparisons from candidates needing attention."),
("26-first-collection-observation.png","Collect an observation","Nexora retrieves the connected page, extracts price and availability signals, and persists an observation and current snapshot."),
("27-alerts.png","Manage market signals","Alert rules and the event log bring important price and availability changes into one place."),
("28-alert-rule-form.png","Configure a threshold","Rules can target a specific offering or the wider catalog, apply a threshold, and define a cooldown."),
("29-alert-rule-created.png","Activate a price-drop rule","The configured rule becomes part of the workspace's monitoring logic."),
("30-price-drop-alert.png","Turn a price movement into an alert","A new collection shows a 12.50% price reduction; the rule creates a persistent alert and the operator can mark it as read."),
("31-collection-job-history.png","Execution history","Jobs capture when collections and discovery runs execute and whether they complete or fail."),
("32-collection-job-detail.png","Inspect a job","Job details preserve identifiers, status and operational metadata for an individual execution."),
("33-website-discovery.png","Discover catalog candidates","Website discovery reads public structured product data and turns evidence-backed products into catalog items."),
("34-private-target-blocked.png","Protect internal network boundaries","Nexora blocks private crawl destinations; the backend validates targets independently of the interface."),
("35-product-discovered.png","Bring a discovered item into the catalog","Structured product evidence supplies name, SKU, category and price for the new catalog entry."),
("36-discovery-upsert.png","Update instead of duplicate","Repeating discovery updates the existing item by URL or SKU rather than creating a second copy."),
("37-password-reset-requested.png","Recover account access","The recovery form acknowledges a reset request without exposing whether an email belongs to an account."),
("38-password-reset-form.png","Set a replacement password","The one-time reset link leads to the password update screen."),
("39-password-reset-complete.png","Finish password recovery","A successful reset consumes the token, changes the password and returns the operator to sign-in."),
("40-return-to-workspace.png","Return to the workspace","The operator can enter Nexora again with the replacement credentials."),
("41-analyst-role.png","Analyst workspace","Analysts can review intelligence and run discovery, while administrative changes remain restricted."),
("42-viewer-read-only-role.png","Viewer workspace","Viewer permissions are read-only and the API independently rejects forbidden writes."),
("43-mobile-homepage.png","Responsive public entry point","The landing page remains usable at a narrow mobile viewport."),
]
missing = [name for name, _, _ in screens if not (root / name).is_file()]
if missing:
    raise SystemExit("Cannot build walkthrough; missing captures: " + ", ".join(missing))
lines = [
"# Nexora — Product Walkthrough", "",
"Nexora is a multi-tenant competitive price-intelligence workspace. This guide follows a realistic retail-product journey from workspace creation to competitor observation, a price-movement alert and catalog discovery. Screens show the application with data created during the walkthrough.", "",
"## 1. Start a private workspace", "",
"Create an organization, verify the work email, and sign in to the workspace.", "",
]
for name, heading, description in screens[:8]:
    lines.extend([f"### {heading}", "", description, "", f"![{heading}](screenshots/{name})", ""])
lines.extend(["## 2. Connect the market", "", "Add competitor businesses, configure collection sources and create the catalog that the team intends to benchmark.", ""])
for name, heading, description in screens[8:23]:
    lines.extend([f"### {heading}", "", description, "", f"![{heading}](screenshots/{name})", ""])
lines.extend(["## 3. Collect competitive intelligence", "", "Map a catalog item to its competitor listing, collect page content, compare observations, and surface meaningful movement through an alert rule.", ""])
for name, heading, description in screens[23:32]:
    lines.extend([f"### {heading}", "", description, "", f"![{heading}](screenshots/{name})", ""])
lines.extend(["## 4. Discover and maintain catalog coverage", "", "Use public structured product data to find catalog candidates. Nexora blocks private targets and updates known items rather than blindly duplicating them.", ""])
for name, heading, description in screens[32:40]:
    lines.extend([f"### {heading}", "", description, "", f"![{heading}](screenshots/{name})", ""])
lines.extend(["## 5. Roles and responsive access", "", "Workspace roles tailor the available controls, and server-side permissions enforce those boundaries even when requests bypass the interface.", ""])
for name, heading, description in screens[40:]:
    lines.extend([f"### {heading}", "", description, "", f"![{heading}](screenshots/{name})", ""])
lines.extend([
"## Connected product journey", "",
"1. An organization creates its private workspace and verifies its account.",
"2. An administrator records competitor businesses and the sources used to observe them.",
"3. The team maintains its offering catalog and maps selected items to competitor URLs.",
"4. Collection jobs fetch public pages and persist observations and snapshots.",
"5. Alert rules convert material price changes into durable events and email notifications.",
"6. Website discovery adds evidence-backed candidates and updates known items when a URL or SKU matches.",
"7. Analysts and viewers use the same workspace through role-appropriate controls.", "",
"**Environment note:** the captured journey runs against an isolated CI PostgreSQL database, Redis, a local STARTTLS inbox and public structured HTML fixtures. It demonstrates real UI-to-API behavior and database persistence for these flows; it does not certify the production deployment or claim that every external website can be collected successfully.", ""
])
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text("\n".join(lines), encoding="utf-8")
print(f"Generated {target} with {len(screens)} screenshots.")
