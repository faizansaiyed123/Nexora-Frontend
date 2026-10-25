"""Browser-driven Nexora workflow using the real FastAPI service and PostgreSQL."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from email import message_from_string
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

from playwright.sync_api import Page, sync_playwright

FRONTEND_URL = os.getenv("NEXORA_FRONTEND_URL", "http://127.0.0.1:5173").rstrip("/")
API_URL = os.getenv("NEXORA_API_URL", "http://127.0.0.1:8000").rstrip("/")
SCREENSHOTS = Path(os.getenv("NEXORA_SCREENSHOT_DIR", "docs/walkthrough/screenshots"))
MAILBOX = Path(os.getenv("NEXORA_MAILBOX", "/tmp/nexora-mailbox.jsonl"))
RUN_ID = os.getenv("GITHUB_RUN_ID", uuid4().hex[:8])
EMAIL = os.getenv("NEXORA_E2E_EMAIL", f"market-analyst-{RUN_ID}@northstar.example.com")
ORG_NAME = f"Northstar Market Intelligence {RUN_ID}"
FULL_NAME = "Alex Morgan"
PASSWORD = "Nexora-Strong!2026"
CHANGED_PASSWORD = "Nexora-Changed!2026"
RESET_PASSWORD = "Nexora-Reset!2026"
ROLE_PASSWORD = "Nexora-Role!2026"
HIGH_URL = "https://cdn.jsdelivr.net/gh/faizansaiyed123/Nexora-backend@main/tests/fixtures/retail-price-high.html"
LOW_URL = "https://cdn.jsdelivr.net/gh/faizansaiyed123/Nexora-backend@main/tests/fixtures/retail-price-low.html"
DISCOVERY_URL = "https://cdn.jsdelivr.net/gh/faizansaiyed123/Nexora-backend@main/tests/fixtures/retail-discovery-product.html"
OFFERING = "Sony WH-1000XM5 Wireless Headphones"
DISCOVERED = "Sony WF-1000XM5 Truly Wireless Noise Canceling Earbuds"
js_errors: list[str] = []


def shot(page: Page, filename: str, description: str) -> None:
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(SCREENSHOTS / filename), full_page=True, animations="disabled", caret="hide")
    print(f"Screenshot: {filename} — {description}", flush=True)


def choose(page: Page, field: str, option: str) -> None:
    container = page.locator("label.field").filter(has_text=field).last
    container.locator("button.select-trigger").click()
    page.get_by_role("option", name=option, exact=True).last.click()


def bearer(page: Page) -> dict[str, str]:
    access = page.evaluate("() => localStorage.getItem('nexora.access')")
    assert access, "Expected an authenticated Nexora browser session."
    return {"Authorization": f"Bearer {access}"}


def api_get(page: Page, path: str, status: int = 200):
    response = page.request.get(API_URL + path, headers=bearer(page))
    assert response.status == status, f"GET {path}: {response.status}: {response.text()}"
    return response.json()


def click_api(page: Page, action, path_suffix: str, method: str, expected: int):
    with page.expect_response(
        lambda r: path_suffix in r.url and r.request.method == method
    ) as event:
        action()
    response = event.value
    assert response.status == expected, (
        f"{method} {path_suffix}: expected {expected}, got {response.status}: {response.text()}"
    )
    return response


def mail_rows() -> list[dict]:
    if not MAILBOX.exists():
        return []
    rows = []
    for line in MAILBOX.read_text(encoding="utf-8").splitlines():
        try:
            value = json.loads(line)
            if isinstance(value, dict) and value.get("data"):
                rows.append(value)
        except json.JSONDecodeError:
            pass
    return rows


def mail_parts(row: dict) -> tuple[str, str, list[str]]:
    message = message_from_string(str(row["data"]))
    if message.is_multipart():
        bodies = []
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                raw = part.get_payload(decode=True)
                if raw:
                    bodies.append(raw.decode(part.get_content_charset() or "utf-8", "replace"))
        body = "\n".join(bodies)
    else:
        raw = message.get_payload(decode=True)
        body = raw.decode(message.get_content_charset() or "utf-8", "replace") if raw else str(message.get_payload())
    return str(message.get("Subject", "")), body, [str(x).lower() for x in row.get("rcpt_tos", [])]


def wait_mail(subject: str, recipient: str, start: int, timeout: float = 35) -> str:
    until = time.monotonic() + timeout
    while time.monotonic() < until:
        for row in mail_rows()[start:]:
            actual_subject, body, recipients = mail_parts(row)
            if subject.lower() in actual_subject.lower() and recipient.lower() in recipients:
                return body
        time.sleep(0.25)
    raise AssertionError(f"No {subject!r} message arrived for {recipient!r} in the isolated inbox.")


def email_link(body: str, route: str) -> str:
    match = re.search(rf"https?://[^\s<>]+/{re.escape(route)}\?token=[^\s<>]+", body)
    assert match, f"Email did not contain the expected {route} link."
    return match.group(0).rstrip(".,);")


def backend_python(code: str) -> str:
    result = subprocess.run([sys.executable, "-c", code], check=True, text=True, capture_output=True)
    return result.stdout.strip()


def sign_in(page: Page, email: str, password: str) -> None:
    page.get_by_label("Work email").fill(email)
    page.get_by_label("Password").fill(password)
    response = click_api(page, lambda: page.get_by_role("button", name=re.compile("Sign in")).click(), "/v1/auth/login", "POST", 200)
    assert response.json()["access_token"]
    page.get_by_role("heading", name="Dashboard", exact=True).wait_for(timeout=15000)


def sign_out(page: Page) -> None:
    page.locator("button.profile-trigger").click()
    page.get_by_text("Sign out", exact=True).click()
    page.get_by_label("Work email").wait_for(timeout=10000)


def main() -> None:
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    if MAILBOX.exists():
        MAILBOX.unlink()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(viewport={"width": 1440, "height": 1000}, accept_downloads=True)
        page = context.new_page()
        page.set_default_timeout(12000)
        page.on("pageerror", lambda error: js_errors.append(str(error)))
        page.on("dialog", lambda dialog: dialog.accept())

        # Account creation, real SMTP delivery, verification and authenticated landing.
        page.goto(FRONTEND_URL + "/welcome", wait_until="networkidle")
        page.get_by_role("heading", name=re.compile("Understand the market")).wait_for()
        shot(page, "01-public-homepage.png", "Public introduction to Nexora.")
        page.get_by_role("link", name="Create workspace", exact=True).click()
        page.get_by_label("Organization name").wait_for()
        shot(page, "02-registration-form.png", "Organization, operator and credential entry.")
        page.get_by_label("Organization name").fill(ORG_NAME)
        page.get_by_label("Your full name").fill(FULL_NAME)
        page.get_by_label("Work email").fill(EMAIL)
        page.get_by_label("Password").fill(PASSWORD)
        registered = click_api(
            page, lambda: page.get_by_role("button", name=re.compile("Create workspace")).click(),
            "/v1/auth/register", "POST", 201,
        )
        assert registered.json()["email_verification_required"] is True
        page.get_by_role("heading", name="Verification required").wait_for()
        shot(page, "03-verification-requested.png", "Registration awaits email confirmation.")
        verify_body = wait_mail("Verify your Nexora account", EMAIL, 0)
        verify_url = email_link(verify_body, "verify-email")
        assert urlparse(verify_url).path.endswith("/verify-email")
        page.goto(verify_url, wait_until="networkidle")
        shot(page, "04-verification-link.png", "One-time email link opens account activation.")
        verify = click_api(page, lambda: page.get_by_role("button", name=re.compile("Verify email")).click(), "/v1/auth/verify-email", "GET", 200)
        assert verify.json().get("message")
        page.get_by_role("link", name="Continue to sign in", exact=True).wait_for()
        shot(page, "05-account-verified.png", "Server confirms account activation.")
        page.get_by_role("link", name="Continue to sign in", exact=True).click()
        page.get_by_label("Work email").wait_for()
        shot(page, "06-sign-in.png", "Workspace sign-in.")
        sign_in(page, EMAIL, PASSWORD)
        shot(page, "07-workspace-dashboard.png", "Tenant dashboard with tracked offerings, competitors, sources and job activity.")

        me = page.request.get(API_URL + "/v1/auth/me", headers=bearer(page))
        assert me.status == 200, me.text()
        assert me.json()["role"] == "ORG_ADMIN"
        client_id = me.json()["client_id"]

        # Workspace profile.
        page.get_by_role("link", name="Settings", exact=True).click()
        page.get_by_label("Company name").wait_for()
        page.get_by_label("Company name").fill("Northstar Analytics")
        page.get_by_label("Country").fill("US")
        page.get_by_label("Default currency").fill("USD")
        page.get_by_label("Market").fill("US")
        page.get_by_label("Industry").fill("Consumer Electronics")
        page.get_by_label("Timezone").fill("America/New_York")
        click_api(page, lambda: page.get_by_role("button", name="Save profile", exact=True).click(), "/v1/auth/profile", "PATCH", 200)
        assert api_get(page, "/v1/auth/profile")["company_name"] == "Northstar Analytics"
        shot(page, "08-workspace-profile.png", "Workspace identity and account settings.")

        # Competitor domain creation and duplicate prevention.
        page.get_by_role("link", name="Competitors", exact=True).click()
        page.get_by_role("heading", name="Competitors", exact=True).wait_for()
        shot(page, "09-competitors.png", "Competitor landscape.")
        page.get_by_role("button", name="Add competitor", exact=True).click()
        page.get_by_label("Name").fill("Retail Product Reference")
        page.get_by_label("Domain").fill("cdn.jsdelivr.net")
        competitor_res = click_api(page, lambda: page.get_by_role("button", name="Save competitor", exact=True).click(), "/v1/competitors", "POST", 201)
        competitor_id = competitor_res.json()["id"]
        page.get_by_text("Retail Product Reference", exact=True).wait_for()
        shot(page, "10-competitor-created.png", "Competitor stored in the current tenant.")
        page.get_by_role("button", name="Add competitor", exact=True).click()
        page.get_by_label("Name").fill("Duplicate retail reference")
        page.get_by_label("Domain").fill("cdn.jsdelivr.net")
        duplicate = click_api(page, lambda: page.get_by_role("button", name="Save competitor", exact=True).click(), "/v1/competitors", "POST", 403)
        page.get_by_text("A competitor with this domain already exists.").wait_for()
        shot(page, "11-duplicate-competitor-blocked.png", "Duplicate competitor domains are rejected.")
        page.get_by_role("button", name="Cancel", exact=True).click()

        # Source configuration.
        page.get_by_role("link", name="Sources", exact=True).click()
        page.get_by_role("heading", name="Sources", exact=True).wait_for()
        shot(page, "12-sources.png", "Source endpoints and health.")
        page.get_by_role("button", name="Add source", exact=True).click()
        choose(page, "Competitor", "Retail Product Reference")
        page.get_by_label("Source name").fill("Retail Product Listing")
        page.get_by_label("Base URL").fill(HIGH_URL)
        choose(page, "Source type", "OFFICIAL_STORE")
        choose(page, "Collection method", "HTTP_FAST")
        source_res = click_api(page, lambda: page.get_by_role("button", name="Create source", exact=True).click(), "/v1/sources", "POST", 201)
        source_id = source_res.json()["id"]
        page.get_by_text("Retail Product Listing", exact=True).wait_for()
        shot(page, "13-source-created.png", "A source is attached to a competitor.")
        page.get_by_title("Configuration", exact=True).click()
        page.get_by_label("Rate / minute").fill("60")
        page.get_by_label("Delay seconds").fill("0.1")
        page.get_by_label("Timeout seconds").fill("25")
        page.get_by_label("Max retries").fill("1")
        page.get_by_label("Custom headers (JSON)").fill('{"Accept-Language":"en-US,en;q=0.9"}')
        page.get_by_label("Extraction selectors (JSON)").fill("{}")
        shot(page, "14-source-configuration.png", "Rate, delay, timeout, retries and extraction settings.")
        click_api(page, lambda: page.get_by_role("button", name="Save configuration", exact=True).click(), f"/v1/sources/{source_id}/configuration", "PATCH", 200)
        source_cfg = api_get(page, f"/v1/sources/{source_id}")["configuration"]
        assert source_cfg["rate_limit_rpm"] == 60 and source_cfg["max_retries"] == 1
        page.get_by_title("Edit source", exact=True).click()
        page.get_by_label("Source name").fill("Retail Product Listing (Structured)")
        click_api(page, lambda: page.get_by_role("button", name="Save changes", exact=True).click(), f"/v1/sources/{source_id}", "PATCH", 200)
        source_name = "Retail Product Listing (Structured)"
        page.get_by_text(source_name, exact=True).wait_for()
        shot(page, "15-source-settings-saved.png", "Saved configuration remains attached to the source.")

        # Catalog lifecycle, details and dynamic field schema.
        page.get_by_role("link", name="Offerings", exact=True).click()
        page.get_by_role("heading", name="Offerings", exact=True).wait_for()
        shot(page, "16-catalog.png", "Canonical catalog for tracked products and dynamic attributes.")
        page.get_by_role("button", name="Add offering", exact=True).click()
        page.get_by_label("Name").fill(OFFERING)
        choose(page, "Offering type", "PRODUCT")
        page.get_by_label("SKU").fill("WH1000XM5-BLK")
        page.get_by_label("Current price").fill("449.99")
        page.get_by_label("Currency").fill("USD")
        page.get_by_label("Market").fill("US")
        page.get_by_label("Category").fill("Electronics > Audio")
        page.get_by_label("Product URL").fill("https://www.sony.com/electronics/headband-headphones/wh-1000xm5")
        page.get_by_label("Description").fill("Wireless over-ear headphones with active noise cancellation and multipoint Bluetooth.")
        page.get_by_label("Dynamic attributes (JSON)").fill('{"brand":"Sony","color":"Black","battery_life_hours":30,"noise_cancellation":true}')
        offering_res = click_api(page, lambda: page.get_by_role("button", name="Create offering", exact=True).click(), "/v1/offerings", "POST", 201)
        offering_id = offering_res.json()["id"]
        page.get_by_text(OFFERING, exact=True).wait_for()
        shot(page, "17-offering-created.png", "Sony product saved with SKU, price, market and structured attributes.")
        row = page.locator("tbody tr").filter(has_text=OFFERING).first
        row.get_by_role("button", name=OFFERING, exact=True).click()
        page.get_by_text("CURRENT PRICE", exact=True).wait_for()
        shot(page, "18-offering-detail.png", "Offering detail and competitor comparison.")
        page.keyboard.press("Escape")
        page.locator("tbody tr").filter(has_text=OFFERING).first.get_by_title("Edit", exact=True).click()
        page.get_by_label("Current price").fill("429.99")
        click_api(page, lambda: page.get_by_role("button", name="Save changes", exact=True).click(), f"/v1/offerings/{offering_id}", "PATCH", 200)
        assert float(api_get(page, f"/v1/offerings/{offering_id}")["current_price"]) == 429.99
        row = page.locator("tbody tr").filter(has_text=OFFERING).first
        click_api(page, lambda: row.get_by_title("Toggle monitoring", exact=True).click(), f"/v1/offerings/{offering_id}/toggle-monitoring", "POST", 200)
        assert api_get(page, f"/v1/offerings/{offering_id}")["is_monitored"] is False
        row = page.locator("tbody tr").filter(has_text=OFFERING).first
        click_api(page, lambda: row.get_by_title("Toggle monitoring", exact=True).click(), f"/v1/offerings/{offering_id}/toggle-monitoring", "POST", 200)
        assert api_get(page, f"/v1/offerings/{offering_id}")["is_monitored"] is True
        shot(page, "19-catalog-edit-and-monitoring.png", "Edit and monitoring controls update persisted catalog data.")
        page.get_by_role("button", name="Dynamic fields", exact=True).click()
        page.get_by_text("Dynamic field definitions", exact=True).wait_for()
        shot(page, "20-dynamic-fields.png", "Workspace-specific field definitions.")
        page.get_by_role("button", name="Add field", exact=True).click()
        page.get_by_label("Machine name").fill("review_cycle_months")
        page.get_by_label("Display name").fill("Review Cycle")
        page.get_by_label("Data type").fill("NUMBER")
        page.get_by_label("Unit").fill("months")
        page.get_by_label("Category").fill("Commercial")
        field_res = click_api(page, lambda: page.get_by_role("button", name="Create field", exact=True).click(), "/v1/offerings/fields", "POST", 201)
        page.get_by_text("Review Cycle", exact=True).wait_for()
        shot(page, "21-dynamic-field-created.png", "Custom field is saved and visible.")
        field_row = page.locator("div.list-row").filter(has_text="Review Cycle").last
        click_api(page, lambda: field_row.locator("button.danger-icon").click(), "/v1/offerings/fields/", "DELETE", 204)
        page.keyboard.press("Escape")
        page.keyboard.press("Escape")

        # Bulk intake, exports and archive semantics.
        page.get_by_role("button", name="Bulk import", exact=True).click()
        bulk = [
            {"name":"Sony ULT WEAR Wireless Headphones","offering_type":"PRODUCT","sku":"ULTWEAR-BLK","current_price":"199.99","currency":"USD","market":"US","url":"https://www.sony.com/electronics/headband-headphones/ult-wear","category":"Electronics > Audio","attributes":{"brand":"Sony","color":"Black"}},
            {"name":"Sony LinkBuds S","offering_type":"PRODUCT","sku":"LINKBUDS-S-BLK","current_price":"199.99","currency":"USD","market":"US","url":"https://www.sony.com/electronics/truly-wireless/linkbuds-s","category":"Electronics > Audio","attributes":{"brand":"Sony","fit":"In-ear"}},
        ]
        page.get_by_label("Offering JSON").fill(json.dumps(bulk))
        shot(page, "22-bulk-import-form.png", "Bulk import accepts a structured catalog payload.")
        bulk_response = click_api(page, lambda: page.get_by_role("button", name="Import offerings", exact=True).click(), "/v1/offerings/bulk", "POST", 200)
        assert bulk_response.json()["successful_count"] == 2
        page.get_by_text("Sony ULT WEAR Wireless Headphones", exact=True).wait_for()
        with page.expect_download(timeout=15000) as csv_event:
            page.get_by_role("button", name="CSV", exact=True).click()
        csv_file = Path("/tmp/nexora-export.csv")
        csv_event.value.save_as(str(csv_file))
        assert csv_file.is_file() and csv_file.stat().st_size > 0
        with page.expect_download(timeout=15000) as json_event:
            page.get_by_role("button", name="JSON", exact=True).click()
        json_file = Path("/tmp/nexora-export.json")
        json_event.value.save_as(str(json_file))
        assert json_file.is_file() and json_file.stat().st_size > 0
        page.get_by_placeholder("Search name, SKU, category…").fill("Sony ULT WEAR")
        page.get_by_text("Sony ULT WEAR Wireless Headphones", exact=True).wait_for()
        page.get_by_label("Select Sony ULT WEAR Wireless Headphones", exact=True).check()
        archived = click_api(page, lambda: page.get_by_role("button", name="Archive 1", exact=True).click(), "/v1/offerings/bulk-archive", "POST", 200)
        assert archived.json()["archived_count"] == 1
        assert page.get_by_text("Sony ULT WEAR Wireless Headphones", exact=True).count() == 0
        archived_readback = api_get(page, "/v1/offerings?q=Sony%20ULT%20WEAR&include_archived=true&page=1&page_size=20")
        assert any(item["is_archived"] for item in archived_readback["items"])
        page.get_by_placeholder("Search name, SKU, category…").fill("")
        page.get_by_text(OFFERING, exact=True).wait_for()
        shot(page, "23-catalog-import-export-archive.png", "Bulk import, export and archive preserve catalog lifecycle.")

        # Match a competitor listing and record actual observations.
        page.get_by_role("link", name="Matches", exact=True).click()
        page.get_by_role("heading", name="Offering matches", exact=True).wait_for()
        shot(page, "24-offering-matches.png", "Map catalog offerings to exact competitor URLs.")
        page.get_by_role("button", name="Add match", exact=True).click()
        choose(page, "Offering", OFFERING)
        choose(page, "Source", source_name)
        page.get_by_label("Competitor target URL").fill(HIGH_URL)
        choose(page, "Status", "APPROVED")
        page.get_by_label("Confidence (0–1)").fill("0.98")
        match_res = click_api(page, lambda: page.get_by_role("button", name="Create match", exact=True).click(), "/v1/offering-matches", "POST", 201)
        match_id = match_res.json()["id"]
        page.get_by_text(HIGH_URL, exact=False).wait_for()
        shot(page, "25-offering-match-created.png", "An approved match connects the catalog item to a source listing.")
        row = page.locator("tbody tr").filter(has_text=OFFERING).first
        collection_one = click_api(page, lambda: row.get_by_title("Run collection", exact=True).click(), "/v1/collections/run", "POST", 201)
        collected = collection_one.json()
        assert collected["status"] == "COMPLETED", collected
        assert collected["observation"]["price"] == "399.99" and collected["observation"]["http_status_code"] == 200, collected
        assert len(api_get(page, f"/v1/offerings/{offering_id}/history")) >= 1
        shot(page, "26-first-collection-observation.png", "The real collector fetches page content and persists an observation and snapshot.")

        # Trigger a price-drop alert with a second distinct public page.
        page.get_by_role("link", name="Alerts", exact=True).click()
        page.get_by_role("heading", name="Alerts", exact=True).wait_for()
        shot(page, "27-alerts.png", "Alert rules and persistent event history.")
        page.get_by_role("button", name="New rule", exact=True).click()
        page.get_by_label("Rule name").fill("Sony retail price drop")
        choose(page, "Alert type", "PERCENTAGE_DROP")
        choose(page, "Offering scope", OFFERING)
        page.get_by_label("Threshold").fill("10")
        page.get_by_label("Cooldown (minutes)").fill("60")
        shot(page, "28-alert-rule-form.png", "Configure the offering-specific alert threshold.")
        rule_res = click_api(page, lambda: page.get_by_role("button", name="Create rule", exact=True).click(), "/v1/alerts/rules", "POST", 201)
        page.get_by_text("Sony retail price drop", exact=True).wait_for()
        shot(page, "29-alert-rule-created.png", "Price-drop rule is saved.")
        page.get_by_role("link", name="Matches", exact=True).click()
        page.locator("tbody tr").filter(has_text=OFFERING).first.get_by_title("Edit", exact=True).click()
        page.get_by_label("Competitor target URL").fill(LOW_URL)
        click_api(page, lambda: page.get_by_role("button", name="Save changes", exact=True).click(), f"/v1/offering-matches/{match_id}", "PATCH", 200)
        row = page.locator("tbody tr").filter(has_text=OFFERING).first
        collection_two = click_api(page, lambda: row.get_by_title("Run collection", exact=True).click(), "/v1/collections/run", "POST", 201)
        changed = collection_two.json()
        assert changed["observation"]["price"] == "349.99", changed
        assert changed["snapshot"]["previous_price"] == "399.99", changed
        assert changed["snapshot"]["percentage_difference"].startswith("-12.50%"), changed

        page.get_by_role("link", name="Alerts", exact=True).click()
        page.get_by_text("Competitor price dropped", exact=True).wait_for(timeout=15000)
        logs = api_get(page, "/v1/alerts/logs")
        alert_log = next((x for x in logs if x["title"] == "Competitor price dropped"), None)
        assert alert_log and alert_log["is_read"] is False, logs
        page.get_by_title("Mark as read", exact=True).click()
        page.get_by_title("Read", exact=True).wait_for()
        assert any(x["id"] == alert_log["id"] and x["is_read"] for x in api_get(page, "/v1/alerts/logs"))
        shot(page, "30-price-drop-alert.png", "A 12.50% reduction creates a durable alert that can be marked read.")
        dispatched = backend_python(
            "import json; from backend.workers.tasks import dispatch_pending_notifications; "
            "print('NEXORA_RESULT=' + json.dumps(dispatch_pending_notifications.run()))"
        )
        dispatch_line = next((x for x in dispatched.splitlines() if x.startswith("NEXORA_RESULT=")), "")
        assert dispatch_line, dispatched
        assert json.loads(dispatch_line.split("=", 1)[1]).get("sent", 0) >= 1
        alert_email = wait_mail("Nexora Competitive Alert: Competitor price dropped", EMAIL, 0)
        assert "Nexora detected a competitive intelligence event" in alert_email

        # Build genuine analyst/viewer accounts in the disposable database and verify saved outbox state.
        setup = f"""
import asyncio, json
from sqlalchemy import select
from backend.core.security import get_password_hash
from backend.db.session import AsyncSessionLocal
from backend.models.client import UserModel
from backend.models.enums import RoleEnum
from backend.models.notification import NotificationOutboxModel
async def run():
    async with AsyncSessionLocal() as session:
        for role in (RoleEnum.ANALYST, RoleEnum.VIEWER):
            address = f"{{role.value.lower()}}-{RUN_ID}@northstar.example.com"
            user = await session.scalar(select(UserModel).where(UserModel.email == address))
            if user is None:
                session.add(UserModel(client_id="{client_id}", email=address, full_name="Northstar " + role.value.title(), hashed_password=get_password_hash("{ROLE_PASSWORD}"), role=role, is_active=True, email_verified=True))
        await session.commit()
    async with AsyncSessionLocal() as session:
        statuses = list((await session.execute(select(NotificationOutboxModel.status).where(NotificationOutboxModel.client_id == "{client_id}", NotificationOutboxModel.channel == "email"))).scalars().all())
        print(json.dumps({{"analyst":"analyst-{RUN_ID}@northstar.example.com","viewer":"viewer-{RUN_ID}@northstar.example.com","statuses":statuses}}))
asyncio.run(run())
"""
        role_info = json.loads(backend_python(setup).splitlines()[-1])
        assert "SENT" in role_info["statuses"], role_info["statuses"]

        # Execution history and job details.
        page.get_by_role("link", name="Jobs", exact=True).click()
        page.get_by_role("heading", name="Jobs", exact=True).wait_for()
        page.get_by_text("ON DEMAND REFRESH", exact=False).wait_for()
        shot(page, "31-collection-job-history.png", "Completed collection jobs remain in execution history.")
        page.get_by_role("button", name="Details", exact=True).first.click()
        page.get_by_text("Job ID", exact=True).wait_for()
        shot(page, "32-collection-job-detail.png", "A job detail panel exposes identifiers, status and execution metadata.")
        page.keyboard.press("Escape")

        # Discovery rejects loopback, fetches public structured data, and upserts by SKU/URL.
        page.get_by_role("link", name="Discovery", exact=True).click()
        page.get_by_role("heading", name="Website discovery", exact=True).wait_for()
        shot(page, "33-website-discovery.png", "Analyze a public storefront and import evidence-backed offerings.")
        page.get_by_label("Website URL").fill("http://127.0.0.1:8000/v1/health")
        page.get_by_label("Max pages").fill("1")
        blocked = click_api(page, lambda: page.get_by_role("button", name="Run discovery", exact=True).click(), "/v1/discovery/run", "POST", 422)
        shot(page, "34-private-target-blocked.png", "The service rejects private and loopback crawl targets.")
        page.get_by_label("Website URL").fill(DISCOVERY_URL)
        choose(page, "Default type", "PRODUCT")
        discovered_res = click_api(page, lambda: page.get_by_role("button", name="Run discovery", exact=True).click(), "/v1/discovery/run", "POST", 200)
        discovered = discovered_res.json()
        assert discovered["status"] == "COMPLETED" and discovered["created_offerings_count"] == 1, discovered
        assert discovered["items"][0]["name"] == DISCOVERED, discovered
        page.get_by_text(DISCOVERED, exact=True).wait_for()
        shot(page, "35-product-discovered.png", "Structured product data is translated into a persisted catalog offering.")
        assert api_get(page, f"/v1/discovery/jobs/{discovered['job_id']}")["items"][0]["sku"] == "WF1000XM5-BLK"
        repeated_res = click_api(page, lambda: page.get_by_role("button", name="Run discovery", exact=True).click(), "/v1/discovery/run", "POST", 200)
        repeated = repeated_res.json()
        assert repeated["created_offerings_count"] == 0 and repeated["updated_offerings_count"] == 1, repeated
        offer_list = api_get(page, "/v1/offerings?q=Sony%20WF-1000XM5&page=1&page_size=20")
        assert sum(x["sku"] == "WF1000XM5-BLK" for x in offer_list["items"]) == 1
        shot(page, "36-discovery-upsert.png", "Repeated discovery updates a known item rather than duplicating its SKU.")

        # Password change invalidation and reset email.
        page.get_by_role("link", name="Settings", exact=True).click()
        page.get_by_label("Current password").fill(PASSWORD)
        page.get_by_label("New password").fill(CHANGED_PASSWORD)
        click_api(page, lambda: page.get_by_role("button", name="Update password", exact=True).click(), "/v1/auth/change-password", "POST", 200)
        old = page.request.post(API_URL + "/v1/auth/login", json={"email": EMAIL, "password": PASSWORD})
        assert old.status == 401, old.text()
        sign_out(page)
        page.get_by_role("link", name="Forgot password?", exact=True).click()
        page.get_by_label("Work email").fill(EMAIL)
        reset_start = len(mail_rows())
        click_api(page, lambda: page.get_by_role("button", name="Send reset link", exact=True).click(), "/v1/auth/forgot-password", "POST", 200)
        page.get_by_role("heading", name="Check your inbox", exact=True).wait_for()
        shot(page, "37-password-reset-requested.png", "Recovery acknowledges the request without revealing account existence.")
        reset_email = wait_mail("Reset your Nexora password", EMAIL, reset_start)
        page.goto(email_link(reset_email, "reset-password"), wait_until="networkidle")
        page.get_by_label("New password").wait_for()
        shot(page, "38-password-reset-form.png", "A one-time link opens the password replacement page.")
        page.get_by_label("New password").fill(RESET_PASSWORD)
        click_api(page, lambda: page.get_by_role("button", name="Update password", exact=True).click(), "/v1/auth/reset-password", "POST", 200)
        page.get_by_role("heading", name="Password updated", exact=True).wait_for()
        shot(page, "39-password-reset-complete.png", "The reset token is consumed and the password changes.")
        page.get_by_role("link", name="Continue to sign in", exact=True).click()
        sign_in(page, EMAIL, RESET_PASSWORD)
        shot(page, "40-return-to-workspace.png", "The owner can return after resetting account access.")

        # Server-enforced permissions for issued analyst and viewer sessions.
        sign_out(page)
        sign_in(page, role_info["analyst"], ROLE_PASSWORD)
        page.get_by_role("link", name="Competitors", exact=True).click()
        assert page.get_by_role("button", name="Add competitor", exact=True).count() == 0
        analyst_write = page.request.post(
            API_URL + "/v1/competitors", headers=bearer(page),
            json={"name":"Forbidden analyst write","domain":f"analyst-{RUN_ID}.example"},
        )
        assert analyst_write.status == 403, analyst_write.text()
        page.get_by_role("link", name="Discovery", exact=True).click()
        assert page.get_by_role("button", name="Run discovery", exact=True).is_visible()
        shot(page, "41-analyst-role.png", "Analysts can review intelligence and run discovery but not administer competitors.")

        sign_out(page)
        sign_in(page, role_info["viewer"], ROLE_PASSWORD)
        page.get_by_role("link", name="Offerings", exact=True).click()
        assert page.get_by_role("button", name="Add offering", exact=True).count() == 0
        assert page.get_by_role("button", name="Bulk import", exact=True).count() == 0
        assert page.get_by_role("button", name="Dynamic fields", exact=True).count() == 0
        viewer_write = page.request.post(
            API_URL + "/v1/competitors", headers=bearer(page),
            json={"name":"Forbidden viewer write","domain":f"viewer-{RUN_ID}.example"},
        )
        assert viewer_write.status == 403, viewer_write.text()
        shot(page, "42-viewer-read-only-role.png", "Viewer permissions are read-only in the UI and API.")

        mobile = context.new_page()
        mobile.set_viewport_size({"width": 390, "height": 844})
        mobile.goto(FRONTEND_URL + "/welcome", wait_until="networkidle")
        widths = mobile.evaluate("() => ({viewport: document.documentElement.clientWidth, content: document.documentElement.scrollWidth})")
        assert widths["content"] <= widths["viewport"], widths
        shot(mobile, "43-mobile-homepage.png", "The public entry point fits a narrow screen without horizontal overflow.")

        assert not js_errors, "Browser JavaScript errors: " + " | ".join(js_errors)
        expected = [
            "01-public-homepage.png","02-registration-form.png","03-verification-requested.png","04-verification-link.png",
            "05-account-verified.png","06-sign-in.png","07-workspace-dashboard.png","08-workspace-profile.png",
            "09-competitors.png","10-competitor-created.png","11-duplicate-competitor-blocked.png","12-sources.png",
            "13-source-created.png","14-source-configuration.png","15-source-settings-saved.png","16-catalog.png",
            "17-offering-created.png","18-offering-detail.png","19-catalog-edit-and-monitoring.png","20-dynamic-fields.png",
            "21-dynamic-field-created.png","22-bulk-import-form.png","23-catalog-import-export-archive.png",
            "24-offering-matches.png","25-offering-match-created.png","26-first-collection-observation.png","27-alerts.png",
            "28-alert-rule-form.png","29-alert-rule-created.png","30-price-drop-alert.png","31-collection-job-history.png",
            "32-collection-job-detail.png","33-website-discovery.png","34-private-target-blocked.png","35-product-discovered.png",
            "36-discovery-upsert.png","37-password-reset-requested.png","38-password-reset-form.png",
            "39-password-reset-complete.png","40-return-to-workspace.png","41-analyst-role.png",
            "42-viewer-read-only-role.png","43-mobile-homepage.png",
        ]
        missing = [name for name in expected if not (SCREENSHOTS / name).is_file()]
        assert not missing, f"Missing walkthrough captures: {missing}"
        print(f"NEXORA_JOURNEY_SUCCESS screenshots={len(expected)}", flush=True)
        browser.close()
        context.close()


if __name__ == "__main__":
    main()
