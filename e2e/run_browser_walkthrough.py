"""Playwright UI → FastAPI → PostgreSQL journey for Nexora.

Application API calls are real; this script does not route, mock, or stub them.
The workflow uses isolated CI-only PostgreSQL/Redis services and a local STARTTLS
SMTP sink. Screenshots are generated only after the corresponding UI state is reached.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import time
import uuid
from email import message_from_string
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import Browser, Page, sync_playwright
from sqlalchemy import select

from backend.core.security import get_password_hash
from backend.db.session import AsyncSessionLocal
from backend.models.client import UserModel
from backend.models.enums import RoleEnum
from backend.models.notification import NotificationOutboxModel
from backend.workers.tasks import dispatch_pending_notifications

BASE_URL = os.getenv("NEXORA_FRONTEND_URL", "http://127.0.0.1:4173").rstrip("/")
API_URL = os.getenv("NEXORA_API_URL", "http://127.0.0.1:8000").rstrip("/")
MAILBOX = Path(os.getenv("NEXORA_MAILBOX", "/tmp/nexora-mailbox.jsonl"))
SHOTS = Path("docs/testing/visuals/nexora")
RUN_ID = os.getenv("GITHUB_RUN_ID", uuid.uuid4().hex[:10])
RUN_ATTEMPT = os.getenv("GITHUB_RUN_ATTEMPT", "1")
EMAIL = f"market-analyst-{RUN_ID}-{RUN_ATTEMPT}@northstar.example.com"
PASSWORD = "Nexora-Strong!2026"
UPDATED_PASSWORD = "Nexora-Updated!2026"
RESET_PASSWORD = "Nexora-Final!2026"
ROLE_PASSWORD = "Nexora-Role!2026"
ORG = f"Northstar Market Intelligence {RUN_ID}-{RUN_ATTEMPT}"
NAME = "Alex Morgan"
COMPETITOR = "Retail Product Reference"
SOURCE = "Sony Retail Price Listing"
OFFERING = "Sony WH-1000XM5 Wireless Headphones"
DISCOVERED = "Sony WF-1000XM5 Truly Wireless Noise Canceling Earbuds"
HIGH_URL = "https://cdn.jsdelivr.net/gh/faizansaiyed123/Nexora-backend@main/tests/fixtures/retail-price-high.html"
LOW_URL = "https://cdn.jsdelivr.net/gh/faizansaiyed123/Nexora-backend@main/tests/fixtures/retail-price-low.html"
DISCOVERY_URL = "https://cdn.jsdelivr.net/gh/faizansaiyed123/Nexora-backend@main/tests/fixtures/retail-discovery-product.html"
js_errors: list[str] = []


def shot(page: Page, filename: str) -> None:
    SHOTS.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(SHOTS / filename), full_page=True, animations="disabled", caret="hide")
    print(f"SCREENSHOT {filename}", flush=True)


def choose(page: Page, label: str, value: str) -> None:
    field = page.locator("label.field").filter(has_text=label).last
    field.locator("button.select-trigger").click()
    page.get_by_role("option", name=value, exact=False).last.click()


def token(page: Page) -> str:
    value = page.evaluate("() => localStorage.getItem('nexora.access')")
    assert value, "No browser access token was saved after sign-in."
    return str(value)


def api_get(page: Page, path: str, expected: int = 200):
    response = page.request.get(API_URL + path, headers={"Authorization": f"Bearer {token(page)}"})
    assert response.status == expected, f"GET {path}: {response.status} {response.text()}"
    return response.json()


def mailbox() -> list[dict]:
    if not MAILBOX.exists():
        return []
    rows = []
    for line in MAILBOX.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
            if isinstance(row, dict) and row.get("data"):
                rows.append(row)
        except json.JSONDecodeError:
            pass
    return rows


def parsed_email(row: dict) -> tuple[str, str, list[str]]:
    msg = message_from_string(str(row["data"]))
    subject = str(msg.get("Subject", ""))
    if msg.is_multipart():
        bodies = []
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                raw = part.get_payload(decode=True)
                if raw:
                    bodies.append(raw.decode(part.get_content_charset() or "utf-8", "replace"))
        body = "\n".join(bodies)
    else:
        raw = msg.get_payload(decode=True)
        body = raw.decode(msg.get_content_charset() or "utf-8", "replace") if raw else str(msg.get_payload())
    return subject, body, [str(x).lower() for x in row.get("rcpt_tos", [])]


def wait_email(subject_part: str, recipient: str, offset: int, timeout: int = 35) -> tuple[dict, str]:
    until = time.monotonic() + timeout
    while time.monotonic() < until:
        for row in mailbox()[offset:]:
            subject, body, recipients = parsed_email(row)
            if subject_part.lower() in subject.lower() and recipient.lower() in recipients:
                return row, body
        time.sleep(0.25)
    observed = [parsed_email(row)[0] for row in mailbox()[offset:]]
    raise AssertionError(f"Expected {subject_part!r} to {recipient}; received {observed!r}")


def link_from_email(body: str, route: str) -> str:
    match = re.search(rf"https?://[^\s<>]+/{re.escape(route)}\?token=[^\s<>]+", body)
    assert match, f"No {route} one-time link found in the delivered message."
    return match.group(0).rstrip(".,);")


def login_ui(page: Page, email: str, password: str) -> None:
    page.get_by_label("Work email").fill(email)
    page.get_by_label("Password").fill(password)
    with page.expect_response(lambda r: r.url.endswith("/v1/auth/login") and r.request.method == "POST") as event:
        page.get_by_role("button", name=re.compile("Sign in")).click()
    response = event.value
    assert response.status == 200, f"Login failed: {response.status} {response.text()}"
    page.get_by_role("heading", name="Dashboard", exact=True).wait_for(timeout=15000)


def open_menu_item(page: Page, item: str) -> None:
    page.locator("button.profile-trigger").click()
    page.get_by_role("menuitem", name=item, exact=True).click()


def sign_out(page: Page) -> None:
    open_menu_item(page, "Sign out")
    page.get_by_label("Work email").wait_for(timeout=10000)


async def create_role_user(client_id: uuid.UUID, role: RoleEnum) -> str:
    email = f"{role.value.lower()}-{RUN_ID}-{RUN_ATTEMPT}@northstar.example.com"
    async with AsyncSessionLocal() as db:
        old = await db.scalar(select(UserModel).where(UserModel.email == email))
        if old:
            return email
        db.add(UserModel(
            client_id=client_id,
            email=email,
            full_name=f"Northstar {role.value.title()}",
            hashed_password=get_password_hash(ROLE_PASSWORD),
            role=role,
            is_active=True,
            email_verified=True,
        ))
        await db.commit()
    return email


async def outbox_states(client_id: uuid.UUID) -> list[str]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(NotificationOutboxModel.status).where(
            NotificationOutboxModel.client_id == client_id,
            NotificationOutboxModel.channel == "email",
        ))
        return list(result.scalars().all())


def main() -> None:
    SHOTS.mkdir(parents=True, exist_ok=True)
    MAILBOX.unlink(missing_ok=True)

    with sync_playwright() as pw:
        browser: Browser = pw.chromium.launch()
        context = browser.new_context(viewport={"width": 1440, "height": 1000}, accept_downloads=True, device_scale_factor=1)
        page = context.new_page()
        page.set_default_timeout(12000)
        page.on("pageerror", lambda err: js_errors.append(str(err)))
        page.on("dialog", lambda dialog: dialog.accept())

        # Public entry, signup, actual STARTTLS email, verification, and login.
        page.goto(BASE_URL + "/welcome", wait_until="networkidle")
        page.get_by_role("heading", name=re.compile("Understand the market")).wait_for()
        shot(page, "00-public-homepage.png")
        page.get_by_role("link", name=re.compile("Create workspace")).first.click()
        page.get_by_label("Organization name").wait_for()
        shot(page, "01-registration-form.png")
        page.get_by_label("Organization name").fill(ORG)
        page.get_by_label("Your full name").fill(NAME)
        page.get_by_label("Work email").fill(EMAIL)
        page.get_by_label("Password").fill(PASSWORD)
        mail_offset = len(mailbox())
        with page.expect_response(lambda r: r.url.endswith("/v1/auth/register") and r.request.method == "POST") as event:
            page.get_by_role("button", name=re.compile("Create workspace")).click()
        assert event.value.status == 201, event.value.text()
        assert event.value.json()["email_verification_required"] is True
        page.get_by_role("heading", name="Verification required").wait_for()
        shot(page, "02-verification-email-sent.png")
        _, mail_body = wait_email("Verify your Nexora account", EMAIL, mail_offset)
        verify_url = link_from_email(mail_body, "verify-email")
        assert urlparse(verify_url).path.endswith("/verify-email")
        page.goto(verify_url, wait_until="networkidle")
        shot(page, "03-email-verification-page.png")
        with page.expect_response(lambda r: r.url.endswith("/v1/auth/verify-email") and r.request.method == "GET") as verify:
            page.get_by_role("button", name=re.compile("Verify email")).click()
        assert verify.value.status == 200, verify.value.text()
        page.get_by_role("link", name="Continue to sign in", exact=True).wait_for()
        shot(page, "04-email-verified.png")
        page.get_by_role("link", name="Continue to sign in", exact=True).click()
        login_ui(page, EMAIL, PASSWORD)
        shot(page, "05-dashboard-empty-workspace.png")
        me = api_get(page, "/v1/auth/me")
        client_id = uuid.UUID(me["client_id"])
        assert me["role"] == "ORG_ADMIN"

        # Competitor management and duplicate-domain validation.
        page.get_by_role("link", name="Competitors", exact=True).click()
        page.get_by_role("heading", name="Competitors", exact=True).wait_for()
        shot(page, "06-competitors.png")
        page.get_by_role("button", name="Add competitor", exact=True).click()
        page.get_by_label("Name").fill(COMPETITOR)
        page.get_by_label("Domain").fill("cdn.jsdelivr.net")
        with page.expect_response(lambda r: r.url.endswith("/v1/competitors") and r.request.method == "POST") as comp_event:
            page.get_by_role("button", name="Save competitor", exact=True).click()
        assert comp_event.value.status == 201, comp_event.value.text()
        competitor_id = comp_event.value.json()["id"]
        page.get_by_text(COMPETITOR, exact=True).wait_for()
        shot(page, "07-competitor-created.png")
        page.get_by_role("button", name="Add competitor", exact=True).click()
        page.get_by_label("Name").fill("Duplicate Retail Reference")
        page.get_by_label("Domain").fill("cdn.jsdelivr.net")
        with page.expect_response(lambda r: r.url.endswith("/v1/competitors") and r.request.method == "POST") as dup_event:
            page.get_by_role("button", name="Save competitor", exact=True).click()
        assert dup_event.value.status == 403, dup_event.value.text()
        page.get_by_text("A competitor with this domain already exists.").wait_for()
        shot(page, "08-duplicate-domain-rejected.png")
        page.get_by_role("button", name="Cancel", exact=True).click()
        assert any(x["id"] == competitor_id for x in api_get(page, "/v1/competitors"))

        # Source + collection configuration.
        page.get_by_role("link", name="Sources", exact=True).click()
        page.get_by_role("button", name="Add source", exact=True).click()
        choose(page, "Competitor", COMPETITOR)
        page.get_by_label("Source name").fill(SOURCE)
        page.get_by_label("Base URL").fill(HIGH_URL)
        choose(page, "Source type", "OFFICIAL_STORE")
        choose(page, "Collection method", "HTTP_FAST")
        shot(page, "09-source-creation-form.png")
        with page.expect_response(lambda r: r.url.endswith("/v1/sources") and r.request.method == "POST") as src_event:
            page.get_by_role("button", name="Create source", exact=True).click()
        assert src_event.value.status == 201, src_event.value.text()
        source_id = src_event.value.json()["id"]
        page.get_by_text(SOURCE, exact=True).wait_for()
        shot(page, "10-source-created.png")
        page.get_by_title("Configuration", exact=True).click()
        page.get_by_label("Rate / minute").fill("60")
        page.get_by_label("Delay seconds").fill("0.1")
        page.get_by_label("Timeout seconds").fill("25")
        page.get_by_label("Max retries").fill("1")
        page.get_by_label("Custom headers (JSON)").fill('{"Accept-Language":"en-US,en;q=0.9"}')
        page.get_by_label("Extraction selectors (JSON)").fill("{}")
        shot(page, "11-source-configuration.png")
        with page.expect_response(lambda r: r.url.endswith(f"/v1/sources/{source_id}/configuration") and r.request.method == "PATCH") as cfg_event:
            page.get_by_role("button", name="Save configuration", exact=True).click()
        assert cfg_event.value.status == 200, cfg_event.value.text()
        source_data = api_get(page, f"/v1/sources/{source_id}")
        assert source_data["configuration"]["rate_limit_rpm"] == 60
        assert source_data["configuration"]["max_retries"] == 1
        shot(page, "12-source-configuration-saved.png")

        # Offering create/edit/detail, dynamic fields, bulk import/export/archive.
        page.get_by_role("link", name="Offerings", exact=True).click()
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
        shot(page, "13-offering-create-form.png")
        with page.expect_response(lambda r: r.url.endswith("/v1/offerings") and r.request.method == "POST") as off_event:
            page.get_by_role("button", name="Create offering", exact=True).click()
        assert off_event.value.status == 201, off_event.value.text()
        offering_id = off_event.value.json()["id"]
        page.get_by_text(OFFERING, exact=True).wait_for()
        shot(page, "14-offering-created.png")
        row = page.locator("tbody tr").filter(has_text=OFFERING).first
        row.get_by_role("button", name=OFFERING, exact=True).click()
        page.get_by_text("CURRENT PRICE", exact=True).wait_for()
        shot(page, "15-offering-detail.png")
        page.keyboard.press("Escape")
        row = page.locator("tbody tr").filter(has_text=OFFERING).first
        row.get_by_title("Edit", exact=True).click()
        page.get_by_label("Current price").fill("429.99")
        with page.expect_response(lambda r: r.url.endswith(f"/v1/offerings/{offering_id}") and r.request.method == "PATCH") as edit_off:
            page.get_by_role("button", name="Save changes", exact=True).click()
        assert edit_off.value.status == 200, edit_off.value.text()
        assert float(api_get(page, f"/v1/offerings/{offering_id}")["current_price"]) == 429.99
        row = page.locator("tbody tr").filter(has_text=OFFERING).first
        with page.expect_response(lambda r: r.url.endswith(f"/v1/offerings/{offering_id}/toggle-monitoring") and r.request.method == "POST") as monitor:
            row.get_by_title("Toggle monitoring", exact=True).click()
        assert monitor.value.status == 200
        assert api_get(page, f"/v1/offerings/{offering_id}")["is_monitored"] is False
        row = page.locator("tbody tr").filter(has_text=OFFERING).first
        with page.expect_response(lambda r: r.url.endswith(f"/v1/offerings/{offering_id}/toggle-monitoring") and r.request.method == "POST") as restore:
            row.get_by_title("Toggle monitoring", exact=True).click()
        assert restore.value.status == 200
        assert api_get(page, f"/v1/offerings/{offering_id}")["is_monitored"] is True

        page.get_by_role("button", name="Dynamic fields", exact=True).click()
        page.get_by_text("Dynamic field definitions", exact=True).wait_for()
        shot(page, "16-dynamic-field-definitions.png")
        page.get_by_role("button", name="Add field", exact=True).click()
        page.get_by_label("Machine name").fill("review_cycle_months")
        page.get_by_label("Display name").fill("Review Cycle")
        page.get_by_label("Data type").fill("NUMBER")
        page.get_by_label("Unit").fill("months")
        page.get_by_label("Category").fill("Commercial")
        with page.expect_response(lambda r: r.url.endswith("/v1/offerings/fields") and r.request.method == "POST") as field_event:
            page.get_by_role("button", name="Create field", exact=True).click()
        assert field_event.value.status == 201, field_event.value.text()
        page.get_by_text("Review Cycle", exact=True).wait_for()
        shot(page, "17-dynamic-field-created.png")
        field_row = page.locator("div.list-row").filter(has_text="Review Cycle").last
        with page.expect_response(lambda r: "/v1/offerings/fields/" in r.url and r.request.method == "DELETE") as field_del:
            field_row.locator("button.danger-icon").click()
        assert field_del.value.status == 204, field_del.value.text()
        page.keyboard.press("Escape")

        bulk_data = [
            {"name": "Sony ULT WEAR Wireless Headphones", "offering_type": "PRODUCT", "sku": "ULTWEAR-BLK", "current_price": "199.99", "currency": "USD", "market": "US", "url": "https://www.sony.com/electronics/headband-headphones/ult-wear", "category": "Electronics > Audio", "attributes": {"brand": "Sony", "color": "Black"}},
            {"name": "Sony LinkBuds S", "offering_type": "PRODUCT", "sku": "LINKBUDS-S-BLK", "current_price": "199.99", "currency": "USD", "market": "US", "url": "https://www.sony.com/electronics/truly-wireless/linkbuds-s", "category": "Electronics > Audio", "attributes": {"brand": "Sony", "fit": "In-ear"}},
        ]
        page.get_by_role("button", name="Bulk import", exact=True).click()
        page.get_by_label("Offering JSON").fill(json.dumps(bulk_data))
        shot(page, "18-bulk-import-form.png")
        with page.expect_response(lambda r: r.url.endswith("/v1/offerings/bulk") and r.request.method == "POST") as bulk_event:
            page.get_by_role("button", name="Import offerings", exact=True).click()
        assert bulk_event.value.status == 200, bulk_event.value.text()
        assert bulk_event.value.json()["successful_count"] == 2, bulk_event.value.text()
        page.get_by_text("Sony ULT WEAR Wireless Headphones", exact=True).wait_for()
        shot(page, "19-bulk-import-complete.png")
        for label in ("CSV", "JSON"):
            with page.expect_download(timeout=15000) as download_event:
                page.get_by_role("button", name=label, exact=True).click()
            download = download_event.value
            target = Path("/tmp") / f"nexora-{label.lower()}-export"
            download.save_as(str(target))
            assert target.exists() and target.stat().st_size > 0
        page.get_by_placeholder("Search name, SKU, category…").fill("Sony ULT WEAR")
        page.get_by_text("Sony ULT WEAR Wireless Headphones", exact=True).wait_for()
        page.get_by_label("Select Sony ULT WEAR Wireless Headphones", exact=True).check()
        with page.expect_response(lambda r: r.url.endswith("/v1/offerings/bulk-archive") and r.request.method == "POST") as archive_event:
            page.get_by_role("button", name="Archive 1", exact=True).click()
        assert archive_event.value.status == 200, archive_event.value.text()
        assert archive_event.value.json()["archived_count"] == 1
        archived = api_get(page, "/v1/offerings?q=Sony%20ULT%20WEAR&include_archived=true&page=1&page_size=20")
        assert any(item["is_archived"] for item in archived["items"])
        page.get_by_placeholder("Search name, SKU, category…").fill("")
        page.get_by_text(OFFERING, exact=True).wait_for()
        shot(page, "20-catalog-import-export-archive.png")

        # Map the internal offering and create real price observations.
        page.get_by_role("link", name="Matches", exact=True).click()
        page.get_by_role("button", name="Add match", exact=True).click()
        choose(page, "Offering", OFFERING)
        choose(page, "Source", SOURCE)
        page.get_by_label("Competitor target URL").fill(HIGH_URL)
        choose(page, "Status", "APPROVED")
        page.get_by_label("Confidence (0–1)").fill("0.98")
        shot(page, "21-match-create-form.png")
        with page.expect_response(lambda r: r.url.endswith("/v1/offering-matches") and r.request.method == "POST") as match_event:
            page.get_by_role("button", name="Create match", exact=True).click()
        assert match_event.value.status == 201, match_event.value.text()
        match_id = match_event.value.json()["id"]
        page.get_by_text(HIGH_URL, exact=False).wait_for()
        shot(page, "22-offering-match-created.png")
        match_row = page.locator("tbody tr").filter(has_text=OFFERING).first
        with page.expect_response(lambda r: "/v1/collections/run" in r.url and r.request.method == "POST") as collect1:
            match_row.get_by_title("Run collection", exact=True).click()
        first = collect1.value
        assert first.status in (200, 201), first.text()
        one = first.json()
        assert one["status"] == "COMPLETED", one
        assert one["observation"]["price"] == "399.99", one
        assert one["observation"]["http_status_code"] == 200, one
        assert len(api_get(page, f"/v1/offerings/{offering_id}/history")) >= 1
        shot(page, "23-first-real-price-observation.png")

        # Alert rule, second lower collection, persistent acknowledgement and email outbox.
        page.get_by_role("link", name="Alerts", exact=True).click()
        page.get_by_role("button", name="New rule", exact=True).click()
        page.get_by_label("Rule name").fill("Sony retail price drop")
        choose(page, "Alert type", "PERCENTAGE_DROP")
        choose(page, "Offering scope", OFFERING)
        page.get_by_label("Threshold").fill("10")
        page.get_by_label("Cooldown (minutes)").fill("60")
        shot(page, "24-alert-rule-form.png")
        with page.expect_response(lambda r: r.url.endswith("/v1/alerts/rules") and r.request.method == "POST") as rule_event:
            page.get_by_role("button", name="Create rule", exact=True).click()
        assert rule_event.value.status == 201, rule_event.value.text()
        page.get_by_text("Sony retail price drop", exact=True).wait_for()
        shot(page, "25-alert-rule-created.png")
        page.get_by_role("link", name="Matches", exact=True).click()
        match_row = page.locator("tbody tr").filter(has_text=OFFERING).first
        match_row.get_by_title("Edit", exact=True).click()
        page.get_by_label("Competitor target URL").fill(LOW_URL)
        with page.expect_response(lambda r: r.url.endswith(f"/v1/offering-matches/{match_id}") and r.request.method == "PATCH") as edit_match:
            page.get_by_role("button", name="Save changes", exact=True).click()
        assert edit_match.value.status == 200, edit_match.value.text()
        match_row = page.locator("tbody tr").filter(has_text=OFFERING).first
        with page.expect_response(lambda r: "/v1/collections/run" in r.url and r.request.method == "POST") as collect2:
            match_row.get_by_title("Run collection", exact=True).click()
        second = collect2.value
        assert second.status in (200, 201), second.text()
        two = second.json()
        assert two["observation"]["price"] == "349.99", two
        assert two["snapshot"]["previous_price"] == "399.99", two
        assert str(two["snapshot"]["percentage_difference"]).startswith("-12.50%"), two
        page.get_by_role("link", name="Alerts", exact=True).click()
        page.get_by_text("Competitor price dropped", exact=True).wait_for(timeout=15000)
        alert = next((item for item in api_get(page, "/v1/alerts/logs") if item["title"] == "Competitor price dropped"), None)
        assert alert and not alert["is_read"]
        page.get_by_title("Mark as read", exact=True).click()
        page.get_by_title("Read", exact=True).wait_for()
        assert any(item["id"] == alert["id"] and item["is_read"] for item in api_get(page, "/v1/alerts/logs"))
        shot(page, "26-alert-triggered-and-acknowledged.png")
        mail_offset = len(mailbox())
        sent = dispatch_pending_notifications.run()
        assert int(sent.get("sent", 0)) >= 1, sent
        _, alert_body = wait_email("Nexora Competitive Alert: Competitor price dropped", EMAIL, mail_offset)
        assert "Nexora detected a competitive intelligence event" in alert_body
        assert "SENT" in asyncio.run(outbox_states(client_id))

        # Execution history and job detail.
        page.get_by_role("link", name="Jobs", exact=True).click()
        page.get_by_role("heading", name="Jobs", exact=True).wait_for()
        page.get_by_text("ON DEMAND REFRESH", exact=False).wait_for()
        shot(page, "27-job-history.png")
        page.get_by_role("button", name="Details", exact=True).first.click()
        page.get_by_text("Job ID", exact=True).wait_for()
        shot(page, "28-job-detail.png")
        page.keyboard.press("Escape")

        # Discovery blocks local/loopback addresses, then upserts structured product data.
        page.get_by_role("link", name="Discovery", exact=True).click()
        page.get_by_label("Website URL").fill("http://127.0.0.1:8000/v1/health")
        page.get_by_label("Max pages").fill("1")
        with page.expect_response(lambda r: r.url.endswith("/v1/discovery/run") and r.request.method == "POST") as blocked:
            page.get_by_role("button", name="Run discovery", exact=True).click()
        assert blocked.value.status == 422, blocked.value.text()
        shot(page, "29-private-target-blocked.png")
        page.get_by_label("Website URL").fill(DISCOVERY_URL)
        choose(page, "Default type", "PRODUCT")
        with page.expect_response(lambda r: r.url.endswith("/v1/discovery/run") and r.request.method == "POST") as discovery_event:
            page.get_by_role("button", name="Run discovery", exact=True).click()
        assert discovery_event.value.status == 200, discovery_event.value.text()
        discovered = discovery_event.value.json()
        assert discovered["status"] == "COMPLETED", discovered
        assert discovered["created_offerings_count"] == 1, discovered
        assert discovered["items"][0]["name"] == DISCOVERED, discovered
        page.get_by_text(DISCOVERED, exact=True).wait_for()
        shot(page, "30-discovered-product.png")
        saved_job = api_get(page, f"/v1/discovery/jobs/{discovered['job_id']}")
        assert saved_job["items"][0]["sku"] == "WF1000XM5-BLK"
        with page.expect_response(lambda r: r.url.endswith("/v1/discovery/run") and r.request.method == "POST") as discovery_again:
            page.get_by_role("button", name="Run discovery", exact=True).click()
        assert discovery_again.value.status == 200, discovery_again.value.text()
        assert discovery_again.value.json()["created_offerings_count"] == 0
        assert discovery_again.value.json()["updated_offerings_count"] == 1
        catalog = api_get(page, "/v1/offerings?q=Sony%20WF-1000XM5&page=1&page_size=20")
        assert sum(item["sku"] == "WF1000XM5-BLK" for item in catalog["items"]) == 1
        shot(page, "31-discovery-upsert.png")

        # Workspace profile and password change.
        open_menu_item(page, "Account settings")
        page.get_by_label("Company name").wait_for()
        shot(page, "32-workspace-settings.png")
        page.get_by_label("Company name").fill("Northstar Analytics")
        page.get_by_label("Country").fill("US")
        page.get_by_label("Default currency").fill("USD")
        page.get_by_label("Market").fill("US")
        page.get_by_label("Industry").fill("Consumer Electronics")
        page.get_by_label("Timezone").fill("America/New_York")
        with page.expect_response(lambda r: r.url.endswith("/v1/auth/profile") and r.request.method == "PATCH") as profile_event:
            page.get_by_role("button", name="Save profile", exact=True).click()
        assert profile_event.value.status == 200, profile_event.value.text()
        assert api_get(page, "/v1/auth/profile")["company_name"] == "Northstar Analytics"
        page.get_by_label("Current password").fill(PASSWORD)
        page.get_by_label("New password").fill(UPDATED_PASSWORD)
        with page.expect_response(lambda r: r.url.endswith("/v1/auth/change-password") and r.request.method == "POST") as pw_change:
            page.get_by_role("button", name="Update password", exact=True).click()
        assert pw_change.value.status == 200, pw_change.value.text()
        assert page.request.post(API_URL + "/v1/auth/login", json={"email": EMAIL, "password": PASSWORD}).status == 401
        assert page.request.post(API_URL + "/v1/auth/login", json={"email": EMAIL, "password": UPDATED_PASSWORD}).status == 200
        shot(page, "33-password-changed.png")

        # Password reset through the actual email and one-time token.
        sign_out(page)
        page.get_by_role("link", name="Forgot password?", exact=True).click()
        page.get_by_label("Work email").fill(EMAIL)
        reset_offset = len(mailbox())
        with page.expect_response(lambda r: r.url.endswith("/v1/auth/forgot-password") and r.request.method == "POST") as forgot:
            page.get_by_role("button", name="Send reset link", exact=True).click()
        assert forgot.value.status == 200, forgot.value.text()
        page.get_by_role("heading", name="Check your inbox", exact=True).wait_for()
        shot(page, "34-password-reset-requested.png")
        _, reset_body = wait_email("Reset your Nexora password", EMAIL, reset_offset)
        page.goto(link_from_email(reset_body, "reset-password"), wait_until="networkidle")
        page.get_by_label("New password").wait_for()
        shot(page, "35-password-reset-form.png")
        page.get_by_label("New password").fill(RESET_PASSWORD)
        with page.expect_response(lambda r: r.url.endswith("/v1/auth/reset-password") and r.request.method == "POST") as reset:
            page.get_by_role("button", name="Update password", exact=True).click()
        assert reset.value.status == 200, reset.value.text()
        page.get_by_role("heading", name="Password updated", exact=True).wait_for()
        shot(page, "36-password-reset-complete.png")
        page.get_by_role("link", name="Continue to sign in", exact=True).click()
        login_ui(page, EMAIL, RESET_PASSWORD)
        shot(page, "37-dashboard-after-reset.png")

        # Persisted roles confirm UI visibility and backend authorization.
        viewer_email = asyncio.run(create_role_user(client_id, RoleEnum.VIEWER))
        analyst_email = asyncio.run(create_role_user(client_id, RoleEnum.ANALYST))
        sign_out(page)
        login_ui(page, analyst_email, ROLE_PASSWORD)
        page.get_by_role("link", name="Competitors", exact=True).click()
        assert page.get_by_role("button", name="Add competitor", exact=True).count() == 0
        analyst_token = token(page)
        denied = page.request.post(API_URL + "/v1/competitors",
            headers={"Authorization": f"Bearer {analyst_token}"},
            json={"name": "Forbidden Analyst Write", "domain": "analyst-forbidden.example"})
        assert denied.status == 403, denied.text()
        page.get_by_role("link", name="Discovery", exact=True).click()
        assert page.get_by_role("button", name="Run discovery", exact=True).is_visible()
        shot(page, "38-analyst-role.png")
        sign_out(page)
        login_ui(page, viewer_email, ROLE_PASSWORD)
        page.get_by_role("link", name="Offerings", exact=True).click()
        assert page.get_by_role("button", name="Add offering", exact=True).count() == 0
        assert page.get_by_role("button", name="Bulk import", exact=True).count() == 0
        assert page.get_by_role("button", name="Dynamic fields", exact=True).count() == 0
        viewer_token = token(page)
        reader = page.request.get(API_URL + "/v1/offerings", headers={"Authorization": f"Bearer {viewer_token}"})
        assert reader.status == 200, reader.text()
        denied = page.request.post(API_URL + "/v1/competitors",
            headers={"Authorization": f"Bearer {viewer_token}"},
            json={"name": "Forbidden Viewer Write", "domain": "viewer-forbidden.example"})
        assert denied.status == 403, denied.text()
        shot(page, "39-viewer-read-only.png")

        mobile = context.new_page()
        mobile.set_viewport_size({"width": 390, "height": 844})
        mobile.goto(BASE_URL + "/welcome", wait_until="networkidle")
        sizes = mobile.evaluate("() => ({viewport: document.documentElement.clientWidth, content: document.documentElement.scrollWidth})")
        assert sizes["content"] <= sizes["viewport"], sizes
        shot(mobile, "40-mobile-homepage.png")

        assert not js_errors, "Browser JavaScript errors: " + " | ".join(js_errors)
        assert len(list(SHOTS.glob("*.png"))) >= 41
        print("NEXORA E2E PASSED: UI/API/PostgreSQL/email/role flows and 41 screenshots.", flush=True)
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
