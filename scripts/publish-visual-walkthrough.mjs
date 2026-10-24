import { createHash } from "node:crypto";
import { mkdir, readFile, readdir, stat, writeFile } from "node:fs/promises";
import { join, relative } from "node:path";

const root = process.cwd();
const screenshotDir = join(root, "docs/testing/screenshots");
const manifestDir = join(root, "docs/testing/visuals");
await mkdir(screenshotDir, { recursive: true });
await mkdir(manifestDir, { recursive: true });

const groups = [
  ["Public entry and account activation", [
    ["00-public-homepage.png", "Public homepage", "Visitor landing page and workspace entry points."],
    ["01-registration-form.png", "Workspace registration form", "Organization, identity, work email and password fields before submission."],
    ["02-verification-email-sent.png", "Verification email requested", "Registration ends in the verified-email-required state."],
    ["03-email-verification-page.png", "Email verification link", "Browser opened the one-time link from the delivered email."],
    ["04-email-verified.png", "Account activated", "The real verification endpoint accepted and consumed its token."],
    ["05-login.png", "Sign-in page", "Login form before authenticating against FastAPI."],
    ["06-dashboard-empty-workspace.png", "New workspace dashboard", "Dashboard is populated by real API responses for the new tenant."]
  ]],
  ["Competitors and collection sources", [
    ["07-competitors-empty.png", "Empty competitor list", "Fresh tenant starts with no competitor entries."],
    ["08-competitor-created.png", "Competitor created", "Competitor saved from the UI and returned by the actual API."],
    ["09-duplicate-domain-rejected.png", "Duplicate domain prevented", "Backend rejects a second competitor for the same tenant domain."],
    ["10-source-creation-form.png", "Source creation form", "Collection source is linked to the newly created competitor."],
    ["11-sources-created.png", "Source saved", "Source record appears in the real source list."],
    ["12-source-configuration.png", "Extraction configuration form", "Rate, delay, timeout, retries, request headers and selectors are configured."],
    ["13-source-configuration-saved.png", "Configuration read-back", "Source and collection configuration remain saved after a fresh API read."]
  ]],
  ["Catalog management", [
    ["14-offering-creation-form.png", "Offering form", "Product identity, SKU, price, market, category and dynamic attributes."],
    ["15-catalog-offering-created.png", "Catalog offering saved", "The canonical offering is persisted and shown in the catalog."],
    ["16-offering-detail-and-history.png", "Offering detail and history", "Detail view shows catalog values and competitive metrics/history."],
    ["17-catalog-monitoring-active.png", "Monitoring toggle round trip", "Monitoring is paused then resumed and both states are checked by API reads."],
    ["18-dynamic-fields.png", "Dynamic field registry", "Tenant attribute schema, including inferred product attributes."],
    ["19-dynamic-field-form.png", "Dynamic field creation form", "A new comparable commercial attribute is configured before save."],
    ["20-dynamic-field-created.png", "Dynamic field saved", "Created field is visible and subsequently removed through the UI."],
    ["21-bulk-import-form.png", "Bulk import payload", "Two catalog offerings are submitted through the bulk endpoint."],
    ["22-bulk-imported-catalog.png", "Bulk import results", "Both imported offerings are persisted and displayed."],
    ["23-catalog-import-export-and-archive.png", "Export, filter and archive", "CSV/JSON downloads, search and soft archive are verified end to end."]
  ]],
  ["Matching and collection", [
    ["24-offering-match-form.png", "Offering-to-source mapping", "Catalog offering is mapped to a specific external source URL."],
    ["25-offering-match-created.png", "Match saved", "The match is listed from PostgreSQL-backed API data."],
    ["26-first-price-observation.png", "First collected price", "Real HTTPS collector fetches the structured HTML page and records 399.99 USD."]
  ]],
  ["Alerts and execution history", [
    ["27-alert-rule-form.png", "Alert rule configuration", "Price-drop threshold is scoped to the Sony offering."],
    ["28-alert-rule-created.png", "Alert rule saved", "Active rule is visible in the tenant rule list."],
    ["29-alert-generated-and-read.png", "Price-drop alert lifecycle", "Second price, snapshot delta, persistent alert log and read-state transition are checked."],
    ["30-collection-job-history.png", "Collection job list", "Real on-demand jobs, status and processed counts."],
    ["31-collection-job-detail.png", "Collection job detail", "Persisted job ID, source and execution metadata."]
  ]],
  ["Website discovery and security boundary", [
    ["32-private-target-blocked.png", "Private network target rejected", "Discovery cannot fetch loopback/internal endpoints requested through the UI."],
    ["33-discovery-product-created.png", "Structured product discovered", "Schema.org data is fetched over HTTPS and becomes a catalog offering."],
    ["34-discovery-upsert-history.png", "Discovery update without duplicate", "Repeated discovery updates a known SKU rather than duplicating it."]
  ]],
  ["Workspace and account security", [
    ["35-workspace-settings.png", "Workspace profile and security", "Tenant profile, account role and password controls."],
    ["36-workspace-profile-updated.png", "Saved workspace profile", "Company, market, currency, industry and timezone changes are read back."],
    ["37-password-changed.png", "Password change", "Authenticated password change works and the previous password stops authenticating."],
    ["38-password-reset-requested.png", "Reset requested", "Generic account-recovery confirmation follows a real request."],
    ["39-password-reset-form.png", "One-time reset form", "Reset screen is opened from the actual delivered SMTP email."],
    ["40-password-reset-complete.png", "Password reset complete", "One-time reset token is accepted and the password is updated."],
    ["41-dashboard-after-password-reset.png", "Re-authenticated dashboard", "A fresh sign-in with the reset password succeeds."]
  ]],
  ["Role-based access and responsive experience", [
    ["42-analyst-workspace.png", "Analyst experience", "Analyst can inspect/run analysis but cannot create competitors."],
    ["43-viewer-read-only-workspace.png", "Viewer read-only experience", "Viewer can read permitted catalog data but cannot use admin UI or write APIs."],
    ["44-super-admin-workspace.png", "Super-admin experience", "Platform super-admin role is visible; server-side competitor create/delete checks pass."],
    ["45-mobile-homepage.png", "Mobile homepage", "390px visitor landing page has no horizontal overflow."]
  ]]
];

const expected = groups.flatMap(([section, shots]) => shots.map(([file, title, description]) => ({ section, file, title, description })));
const available = await readdir(screenshotDir);
const missing = expected.filter(item => !available.includes(item.file));
if (missing.length) throw new Error("Cannot publish an incomplete walkthrough: " + missing.map(x => x.file).join(", "));

const screenshots = [];
for (const item of expected) {
  const path = join(screenshotDir, item.file);
  const bytes = await readFile(path);
  screenshots.push({
    ...item,
    path: relative(root, path).replaceAll("\\", "/"),
    bytes: (await stat(path)).size,
    sha256: createHash("sha256").update(bytes).digest("hex")
  });
}

const manifest = {
  schema_version: 1,
  result: "passed",
  generated_at_utc: new Date().toISOString(),
  frontend_commit_tested: process.env.NEXORA_TESTED_SHA || process.env.GITHUB_SHA || "unknown",
  backend_commit_tested: process.env.NEXORA_BACKEND_SHA || "unknown",
  workflow_run: process.env.GITHUB_RUN_ID || "local",
  workflow_run_url: process.env.NEXORA_WORKFLOW_URL || "",
  runtime: "Playwright Chromium + real Nexora React app + FastAPI + disposable PostgreSQL + disposable Redis + loopback STARTTLS email sink",
  fixtures: "Versioned Schema.org HTML pages are fetched over HTTPS by real collection/discovery services; application API responses are not mocked.",
  screenshot_count: screenshots.length,
  screenshots
};

await writeFile(join(manifestDir, "manifest.json"), JSON.stringify(manifest, null, 2) + "\n", "utf8");

let markdown = "# Nexora visual end-to-end testing walkthrough\n\n";
markdown += "**Result:** Passed  \n";
markdown += "**Screenshots:** " + screenshots.length + " full-page browser captures  \n";
markdown += "**Frontend commit tested:** " + manifest.frontend_commit_tested + "  \n";
markdown += "**Backend commit tested:** " + manifest.backend_commit_tested + "  \n";
markdown += "**Workflow run:** " + (manifest.workflow_run_url ? "[Open the exact CI run](" + manifest.workflow_run_url + ")" : manifest.workflow_run) + "  \n";
markdown += "**Generated (UTC):** " + manifest.generated_at_utc + "\n\n";
markdown += "## What this proves\n\n";
markdown += "This walkthrough is generated from a successful Chromium run against the actual Nexora React UI and FastAPI endpoints. PostgreSQL and Redis are disposable CI instances, not production. Registration verification, password reset and competitive alert mail are delivered through a loopback STARTTLS inbox; the browser follows real one-time links. No application API response is stubbed or intercepted.\n\n";
markdown += "The collection and discovery engines fetch versioned public HTML fixtures over HTTPS. They contain realistic product details in Schema.org markup and intentionally different prices, letting the production extractor, persistence, snapshot, threshold evaluator and notification-outbox path be checked repeatably. These controlled fixtures are not represented as live retailer quotes.\n\n";
markdown += "## Verified workflow coverage\n\n";
markdown += "- Registration, actual email verification, login, password change, reset-token delivery and password reset.\n";
markdown += "- Tenant-scoped competitor/source/catalog operations, duplicate-domain rejection, source settings, dynamic fields, monitoring toggles and fresh API read-back.\n";
markdown += "- Catalog filtering, JSON bulk import, CSV/JSON downloads, soft archive and read-back.\n";
markdown += "- Match creation, two collection requests, observations/snapshots, percentage-drop alert, read state and email outbox delivery.\n";
markdown += "- SSRF denial, structured-data discovery, catalog upsert and deduplication.\n";
markdown += "- Organization admin, analyst and viewer UI controls plus server-side authorization; mobile visitor layout and browser error detection.\n\n";
markdown += "## Evidence screenshots\n\n";
markdown += "Each image is captured during the test sequence described below. File sizes and SHA-256 digests are recorded in the [machine-readable screenshot manifest](visuals/manifest.json).\n";
for (const [section, shots] of groups) {
  markdown += "\n## " + section + "\n";
  for (const [file, title, description] of shots) {
    markdown += "\n### " + title + "\n\n" + description + "\n\n";
    markdown += "![" + title + "](screenshots/" + file + ")\n\n";
    markdown += "[Open full-size screenshot](screenshots/" + file + ")\n";
  }
}
markdown += "\n## Environment boundaries\n\n";
markdown += "- The browser uses the freshly built frontend; every application mutation is sent to the running FastAPI process backed by the workflow PostgreSQL database.\n";
markdown += "- Migrations run before the test. Database queries seed explicit role accounts and verify notification outbox state; business record mutations use UI/API flows.\n";
markdown += "- The STARTTLS inbox binds to loopback, with per-run credentials and a temporary trusted certificate. Test email is not sent to an external address.\n";
markdown += "- Public controlled HTML fixtures make extraction results deterministic; the production collector/discovery implementation is not replaced. External anti-bot or layout changes therefore do not masquerade as Nexora failures.\n";
markdown += "- This evidence does not certify the deployed production site, production database, billing, external third-party integrations, or scheduled production workers.\n\n";
markdown += "See [manifest.json](visuals/manifest.json) for exact tested revisions and per-image hashes.\n";

await writeFile(join(root, "docs/testing/VISUAL-TEST-WALKTHROUGH.md"), markdown, "utf8");
console.log("Published " + screenshots.length + " screenshots and the visual walkthrough.");
