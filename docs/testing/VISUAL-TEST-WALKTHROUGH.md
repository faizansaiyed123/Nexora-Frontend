# Nexora — Visual Product Walkthrough

Nexora brings catalogue intelligence, competitor coverage, website discovery, price collection, and alerts into one workspace. This walkthrough follows the same market journey from the public entry point to a saved observation and an actionable signal.

## Start with a private workspace

From account creation and email verification, the user enters a tenant-scoped workspace. Workspace data and actions are presented according to the signed-in user's role.

### Public homepage

The public entry point introduces Nexora's competitive market intelligence workspace.

![Public homepage](visuals/nexora/00-public-homepage.png)

### Create a workspace

Organization identity and an account are created before the team enters its private workspace.

![Create a workspace](visuals/nexora/01-registration-form.png)

### Email verification

The registration flow prompts the new user to verify their work email.

![Email verification](visuals/nexora/02-verification-email-sent.png)

### Verification link

A secure one-time link opens the account verification screen.

![Verification link](visuals/nexora/03-email-verification-page.png)

### Identity confirmed

The account is ready for sign-in after its verification link is accepted.

![Identity confirmed](visuals/nexora/04-email-verified.png)

## Build the market map

Competitors describe the market entities being watched. Sources connect those competitors to pages Nexora can collect, while source settings tune rate, retries, timeout, headers, and extraction behaviour.

### Workspace overview

The dashboard presents the operating picture for the current tenant.

![Workspace overview](visuals/nexora/05-dashboard-empty-workspace.png)

### Competitor network

The competitor directory organises market entities being benchmarked.

![Competitor network](visuals/nexora/06-competitors.png)

### Competitor profile

A saved competitor becomes available to source and offering workflows.

![Competitor profile](visuals/nexora/07-competitor-created.png)

### Duplicate guard

Nexora prevents a duplicate domain from being added to the same workspace.

![Duplicate guard](visuals/nexora/08-duplicate-domain-rejected.png)

### Connect a source

A source associates a competitor with a public page used for market collection.

![Connect a source](visuals/nexora/09-source-creation-form.png)

### Source directory

Configured sources display their collection method, health, and circuit state.

![Source directory](visuals/nexora/10-source-created.png)

### Collection settings

Rate limits, timeouts, retries, headers, and selectors can be tuned for a source.

![Collection settings](visuals/nexora/11-source-configuration.png)

## Create and maintain the catalogue

Offerings represent the products, services, plans, or other items a workspace wants to track. Dynamic fields, bulk import/export, search, monitoring, and archival keep the catalogue adaptable as it grows.

### Saved configuration

The source's persisted configuration is reflected in its workspace record.

![Saved configuration](visuals/nexora/12-source-configuration-saved.png)

### Add a catalog offering

Products can be recorded with SKU, currency, market, category, price, and dynamic attributes.

![Add a catalog offering](visuals/nexora/13-offering-create-form.png)

### Tracked catalog

The canonical offering appears in the workspace catalog.

![Tracked catalog](visuals/nexora/14-offering-created.png)

### Offering detail

The detail view combines price, monitoring state, match coverage, and historical information.

![Offering detail](visuals/nexora/15-offering-detail.png)

### Dynamic attributes

Teams can define comparable, domain-specific fields to enrich catalog records.

![Dynamic attributes](visuals/nexora/16-dynamic-field-definitions.png)

### Custom field

A new attribute definition becomes part of the workspace's catalog schema.

![Custom field](visuals/nexora/17-dynamic-field-created.png)

### Bulk catalog import

Multiple product records can be introduced together using structured JSON.

![Bulk catalog import](visuals/nexora/18-bulk-import-form.png)

### Imported offerings

Imported catalogue rows join the same search and monitoring workspace.

![Imported offerings](visuals/nexora/19-bulk-import-complete.png)

## Turn sources into price intelligence

An offering match links an internal catalogue item to a competitor URL. Nexora fetches that page, records an observation and snapshot, and compares a later observation with the prior price. Alert rules turn configured changes into a persistent signal; the job pages provide context on collection and discovery activity.

### Export and archive

CSV/JSON exports and bulk archival support catalog maintenance.

![Export and archive](visuals/nexora/20-catalog-import-export-archive.png)

### Map an offering

A catalog item is associated with a specific competitor source URL and confidence score.

![Map an offering](visuals/nexora/21-match-create-form.png)

### Competitive mapping

The match links the internal catalog item to a source that can be collected.

![Competitive mapping](visuals/nexora/22-offering-match-created.png)

### First price observation

The collector fetches a real page and records the extracted price and observation history.

![First price observation](visuals/nexora/23-first-real-price-observation.png)

### Configure a market signal

A rule describes which price movement should become an actionable alert.

![Configure a market signal](visuals/nexora/24-alert-rule-form.png)

### Alert rule

The workspace keeps the selected threshold and offering scope for future comparisons.

![Alert rule](visuals/nexora/25-alert-rule-created.png)

### Price-drop alert

A lower second observation triggers an alert, which can be marked as read.

![Price-drop alert](visuals/nexora/26-alert-triggered-and-acknowledged.png)

### Execution history

Collection and discovery jobs appear with their outcome and processing counts.

![Execution history](visuals/nexora/27-job-history.png)

## Discover and secure the workspace

Website discovery extracts structured product information into the catalogue and updates matching existing records. Account settings, password recovery, and role-specific access keep workspace administration in context.

### Job details

Individual job records provide IDs, status, timestamps, and execution metadata.

![Job details](visuals/nexora/28-job-detail.png)

### Safe discovery boundary

Private or loopback destinations are rejected before an external crawl can run.

![Safe discovery boundary](visuals/nexora/29-private-target-blocked.png)

### Website discovery

Structured product information is discovered and added to the catalog.

![Website discovery](visuals/nexora/30-discovered-product.png)

### Discovery history

A repeat scan updates the existing offering instead of creating a duplicate.

![Discovery history](visuals/nexora/31-discovery-upsert.png)

### Workspace settings

Organization identity, industry, timezone, default currency, and account security are managed together.

![Workspace settings](visuals/nexora/32-workspace-settings.png)

### Password change

A signed-in user can rotate their credential from workspace settings.

![Password change](visuals/nexora/33-password-changed.png)

### Password recovery

The recovery flow confirms a reset request without disclosing whether an account exists.

![Password recovery](visuals/nexora/34-password-reset-requested.png)

### Reset link

A one-time reset link opens the new-password form.

![Reset link](visuals/nexora/35-password-reset-form.png)

### Password updated

A successfully redeemed reset token returns the user to sign-in.

![Password updated](visuals/nexora/36-password-reset-complete.png)

### Return to workspace

The user can sign in again after completing the reset flow.

![Return to workspace](visuals/nexora/37-dashboard-after-reset.png)

### Analyst workspace

Analysts can investigate market signals and discover offerings without administrator-only controls.

![Analyst workspace](visuals/nexora/38-analyst-role.png)

### Viewer workspace

Viewer access is read-oriented; catalogue mutations and administrator actions are unavailable.

![Viewer workspace](visuals/nexora/39-viewer-read-only.png)

### Mobile entry point

The public experience adapts to a narrow viewport without horizontal overflow.

![Mobile entry point](visuals/nexora/40-mobile-homepage.png)

## The connected journey

1. Create a workspace and verify the account.
2. Add competitors and public sources.
3. Build or discover a catalogue and define the attributes that matter.
4. Map an offering to a competitor page and collect an observation.
5. Compare the next observation with the saved snapshot.
6. Use alert history and job detail to understand the signal and the operation that produced it.

The screenshots in this guide are captured from the running browser experience. The full-stack workflow uses an isolated PostgreSQL database, Redis, and a local email inbox so it does not create or modify production customer data.
