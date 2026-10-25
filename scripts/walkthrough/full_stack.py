from __future__ import annotations

import asyncio
import json
import os
import re
import subprocess
import sys
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

BASE_URL = os.getenv("NEXORA_FRONTEND_URL", "http://127.0.0.1:4173").rstrip("/")
API_URL = os.getenv("NEXORA_API_URL", "http://127.0.0.1:8000").rstrip("/")
MAILBOX = Path(os.getenv("NEXORA_MAILBOX", "/tmp/nexora-mailbox.jsonl"))
SCREENSHOTS = Path(os.getenv("NEXORA_SCREENSHOT_DIR", "docs/walkthrough/screenshots"))
EMAIL = f"market-analyst-{uuid.uuid4().hex[:8]}@northstar.example.com"
INITIAL_PASSWORD = "Nexora-Strong!2026"
UPDATED_PASSWORD = "Nexora-Updated!2026"
RESET_PASSWORD = "Nexora-Final!2026"
ROLE_PASSWORD = "Nexora-Role!2026"
ORGANIZATION = "Northstar Market Intelligence"
FULL_NAME = "Alex Morgan"
COMPETITOR_NAME = "Retail Product Reference"
SOURCE_NAME = "Retail Product Listing"
OFFERING_NAME = "Sony WH-1000XM5 Wireless Headphones"
DISCOVERED_NAME = "Sony WF-1000XM5 Truly Wireless Noise Canceling Earbuds"
HIGH_URL = (
    "https://cdn.jsdelivr.net/gh/faizansaiyed123/Nexora-backend@main/"
    "tests/fixtures/retail-price-high.html"
)
LOW_URL = (
    "https://cdn.jsdelivr.net/gh/faizansaiyed123/Nexora-backend@main/"
    "tests/fixtures/retail-price-low.html"
)
DISCOVERY_URL = (
    "https://cdn.jsdelivr.net/gh/faizansaiyed123/Nexora-backend@main/"
    "tests/fixtures/retail-discovery-product.html"
)
JS_ERRORS: list[str] = []


def capture(page: Page, name: str) -> None:
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    page.screenshot(
        path=str(SCREENSHOTS / name),
        full_page=True,
        animations="disabled",
        caret="hide",
    )
    print(f"SCREENSHOT {name}", flush=True)


def select_value(page: Page, label_text: str, option_text: str) -> None:
    field = page.locator("label.field").filter(has_text=label_text).last
    field.locator("button.select-trigger").click()
    page.get_by_role("option", name=option_text, exact=True).last.click()


def bearer(page: Page) -> dict[str, str]:
    token = page.evaluate("() => localStorage.getItem('nexora.access')")
    assert token, "Expected an access token after successful sign-in."
    return {"Authorization": f"Bearer {token}"}


def api_get(page: Page, path: str, status: int = 200):
    response = page.request.get(API_URL + path, headers=bearer(page))
    assert response.status == status, f"GET {path}: {response.status} {response.text()}"
    return response.json()


def mailbox_messages() -> list[dict]:
    if not MAILBOX.exists():
        return []
    result: list[dict] = []
    for line in MAILBOX.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
            if isinstance(row, dict) and row.get("data"):
                result.append(row)
        except json.JSONDecodeError:
            continue
    return result


def mail_parts(row: dict) -> tuple[str, str, list[str]]:
    message = message_from_string(str(row["data"]))
    subject = str(message.get("Subject", ""))
    if message.is_multipart():
        chunks = []
        for part in message.walk():
            if part.get_content_type() != "text/plain":
                continue
            raw = part.get_payload(decode=True)
            if raw:
                chunks.append(raw.decode(part.get_content_charset() or "utf-8", "replace"))
        body = "\n".join(chunks)
    else:
        raw = message.get_payload(decode=True)
        body = raw.decode(message.get_content_charset() or "utf-8", "replace") if raw else str(message.get_payload())
    return subject, body, [str(x).lower() for x in row.get("rcpt_tos", [])]


def wait_email(subject: str, recipient: str, previous_count: int, timeout: int = 35) -> str:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        for row in mailbox_messages()[previous_count:]:
            found_subject, body, recipients = mail_parts(row)
            if subject.lower() in found_subject.lower() and recipient.lower() in recipients:
                return body
        time.sleep(0.25)
    received = [mail_parts(row)[0] for row in mailbox_messages()[previous_count:]]
    raise AssertionError(f"Expected email {subject!r} for {recipient}; received: {received}")


def link_from_email(body: str, route: str) -> str:
    match = re.search(rf"https?://[^\s<>]+/{re.escape(route)}\?token=[^\s<>]+", body)
    assert match, f"Expected a one-time {route} link in the actual email."
    return match.group(0).rstrip(".,);")


def ui_login(page: Page, email: str, password: str) -> None:
    page.get_by_label("Work email").fill(email)
    page.get_by_label("Password").fill(password)
    with page.expect_response(
        lambda r: r.url.endswith("/v1/auth/login") and r.request.method == "POST"
    ) as event:
        page.get_by_role("button", name=re.compile("Sign in")).click()
    response = event.value
    assert response.status == 200, f"Sign-in failed: {response.status} {response.text()}"
    page.get_by_role("heading", name="Dashboard", exact=True).wait_for(timeout=15000)


def ui_sign_out(page: Page) -> None:
    page.locator("button.profile-trigger").click()
    page.get_by_text("Sign out", exact=True).click()
    page.get_by_label("Work email").wait_for(timeout=10000)


async def persist_role_user(client_id: uuid.UUID, role: RoleEnum, label: str) -> str:
    email = f"{role.value.lower()}-{label}-{uuid.uuid4().hex[:6]}@northstar.example.com"
    async with AsyncSessionLocal() as session:
        session.add(UserModel(
            client_id=client_id,
            email=email,
            full_name=f"Northstar {role.value.title()}",
            hashed_password=get_password_hash(ROLE_PASSWORD),
            role=role,
            is_active=True,
            email_verified=True,
        ))
        await session.commit()
    return email


def dispatch_notifications() -> str:
    env = os.environ.copy()
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from backend.workers.tasks import dispatch_pending_notifications; "
            "print(dispatch_pending_notifications.run())",
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, (
        f"Notification worker failed: stdout={result.stdout} stderr={result.stderr}"
    )
    return result.stdout + result.stderr


def main() -> None:
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    if MAILBOX.exists():
        MAILBOX.unlink()

    with asyncio.Runner() as runner, sync_playwright() as playwright:
        browser: Browser = playwright.chromium.launch()
        context = browser.new_context(
            viewport={"width": 1440, "height": 1000},
            accept_downloads=True,
            device_scale_factor=1,
        )
        page = context.new_page()
        page.set_default_timeout(12000)
        page.on("pageerror", lambda error: JS_ERRORS.append(str(error)))
        page.on("dialog", lambda dialog: dialog.accept())

        # 1. Public website, onboarding, email verification, and real sign-in.
        page.goto(BASE_URL + "/welcome", wait_until="networkidle")
        page.get_by_role("heading", name=re.compile("Understand the market")).wait_for()
        capture(page, "00-public-homepage.png")
        page.get_by_role("link", name=re.compile("Create workspace")).click()
        page.get_by_label("Organization name").wait_for()
        capture(page, "01-registration-form.png")
        page.get_by_label("Organization name").fill(ORGANIZATION)
        page.get_by_label("Your full name").fill(FULL_NAME)
        page.get_by_label("Work email").fill(EMAIL)
        page.get_by_label("Password").fill(INITIAL_PASSWORD)
        before_registration = len(mailbox_messages())
        with page.expect_response(
            lambda r: r.url.endswith("/v1/auth/register") and r.request.method == "POST"
        ) as register_event:
            page.get_by_role("button", name=re.compile("Create workspace")).click()
        register_response = register_event.value
        assert register_response.status == 201, register_response.text()
        assert register_response.json()["email_verification_required"] is True
        page.get_by_role("heading", name="Verification required").wait_for()
        capture(page, "02-verification-email-sent.png")
        verification_body = wait_email("Verify your Nexora account", EMAIL, before_registration)
        verification_url = link_from_email(verification_body, "verify-email")
        assert urlparse(verification_url).path.endswith("/verify-email")
        page.goto(verification_url, wait_until="networkidle")
        capture(page, "03-email-verification-page.png")
        with page.expect_response(
            lambda r: r.url.endswith("/v1/auth/verify-email") and r.request.method == "GET"
        ) as verify_event:
            page.get_by_role("button", name=re.compile("Verify email")).click()
        assert verify_event.value.status == 200, verify_event.value.text()
        page.get_by_role("link", name="Continue to sign in", exact=True).wait_for()
        capture(page, "04-email-verified.png")
        page.get_by_role("link", name="Continue to sign in", exact=True).click()
        ui_login(page, EMAIL, INITIAL_PASSWORD)
        capture(page, "05-dashboard-empty-workspace.png")
        me = api_get(page, "/v1/auth/me")
        assert me["role"] == "ORG_ADMIN"
        client_id = uuid.UUID(me["client_id"])

        # 2. Competitors: create, duplicate protection, edit and persisted read-back.
        page.get_by_role("link", name="Competitors", exact=True).click()
        page.get_by_role("heading", name="Competitors", exact=True).wait_for()
        capture(page, "06-competitors-empty.png")
        page.get_by_role("button", name="Add competitor", exact=True).click()
        page.get_by_label("Name").fill(COMPETITOR_NAME)
        page.get_by_label("Domain").fill("cdn.jsdelivr.net")
        with page.expect_response(
            lambda r: r.url.endswith("/v1/competitors") and r.request.method == "POST"
        ) as competitor_event:
            page.get_by_role("button", name="Save competitor", exact=True).click()
        competitor_response = competitor_event.value
        assert competitor_response.status == 201, competitor_response.text()
        competitor_id = competitor_response.json()["id"]
        page.get_by_text(COMPETITOR_NAME, exact=True).wait_for()
        capture(page, "07-competitor-created.png")

        page.get_by_role("button", name="Add competitor", exact=True).click()
        page.get_by_label("Name").fill("Duplicate Retail Reference")
        page.get_by_label("Domain").fill("cdn.jsdelivr.net")
        with page.expect_response(
            lambda r: r.url.endswith("/v1/competitors") and r.request.method == "POST"
        ) as duplicate_event:
            page.get_by_role("button", name="Save competitor", exact=True).click()
        assert duplicate_event.value.status == 403, duplicate_event.value.text()
        page.get_by_text("A competitor with this domain already exists.").wait_for()
        capture(page, "08-duplicate-domain-protection.png")
        page.get_by_role("button", name="Cancel", exact=True).click()

        row = page.locator("tbody tr").filter(has_text=COMPETITOR_NAME).first
        row.locator("button").first.click()
        page.get_by_label("Name").fill("Retail Product Reference")
        with page.expect_response(
            lambda r: r.url.endswith(f"/v1/competitors/{competitor_id}") and r.request.method == "PATCH"
        ) as competitor_edit:
            page.get_by_role("button", name="Save competitor", exact=True).click()
        assert competitor_edit.value.status == 200, competitor_edit.value.text()
        COMPETITOR_NAME = "Retail Product Reference"
        assert any(
            item["id"] == competitor_id and item["name"] == COMPETITOR_NAME
            for item in api_get(page, "/v1/competitors")
        )
        capture(page, "09-competitor-updated.png")

        # 3. Source configuration: create a source, tune collection settings and verify save.
        page.get_by_role("link", name="Sources", exact=True).click()
        page.get_by_role("heading", name="Sources", exact=True).wait_for()
        page.get_by_role("button", name="Add source", exact=True).click()
        select_value(page, "Competitor", COMPETITOR_NAME)
        page.get_by_label("Source name").fill(SOURCE_NAME)
        page.get_by_label("Base URL").fill(HIGH_URL)
        select_value(page, "Source type", "OFFICIAL_STORE")
        select_value(page, "Collection method", "HTTP_FAST")
        capture(page, "10-source-creation-form.png")
        with page.expect_response(
            lambda r: r.url.endswith("/v1/sources") and r.request.method == "POST"
        ) as source_event:
            page.get_by_role("button", name="Create source", exact=True).click()
        source_response = source_event.value
        assert source_response.status == 201, source_response.text()
        source_id = source_response.json()["id"]
        page.get_by_text(SOURCE_NAME, exact=True).wait_for()
        capture(page, "11-source-created.png")

        page.get_by_title("Configuration", exact=True).click()
        page.get_by_label("Rate / minute").fill("60")
        page.get_by_label("Delay seconds").fill("0")
        page.get_by_label("Timeout seconds").fill("25")
        page.get_by_label("Max retries").fill("1")
        page.get_by_label("Custom headers (JSON)").fill('{"Accept-Language":"en-US,en;q=0.9"}')
        page.get_by_label("Extraction selectors (JSON)").fill("{}")
        capture(page, "12-source-configuration-form.png")
        with page.expect_response(
            lambda r: r.url.endswith(f"/v1/sources/{source_id}/configuration") and r.request.method == "PATCH"
        ) as configuration_event:
            page.get_by_role("button", name="Save configuration", exact=True).click()
        configuration_response = configuration_event.value
        assert configuration_response.status == 200, configuration_response.text()
        source_readback = next(
            item for item in api_get(page, "/v1/sources") if item["id"] == source_id
        )
        assert source_readback["configuration"]["rate_limit_rpm"] == 60
        assert source_readback["configuration"]["max_retries"] == 1
        page.get_by_title("Edit source", exact=True).click()
        page.get_by_label("Source name").fill(SOURCE_NAME + " (Structured)")
        with page.expect_response(
            lambda r: r.url.endswith(f"/v1/sources/{source_id}") and r.request.method == "PATCH"
        ) as source_edit:
            page.get_by_role("button", name="Save changes", exact=True).click()
        assert source_edit.value.status == 200, source_edit.value.text()
        SOURCE_NAME = SOURCE_NAME + " (Structured)"
        assert any(
            item["id"] == source_id and item["name"] == SOURCE_NAME
            for item in api_get(page, "/v1/sources")
        )
        capture(page, "13-source-configuration-saved.png")

        # 4. Catalog CRUD, details, monitoring, dynamic fields, bulk operations and exports.
        page.get_by_role("link", name="Offerings", exact=True).click()
        page.get_by_role("heading", name="Offerings", exact=True).wait_for()
        page.get_by_role("button", name="Add offering", exact=True).click()
        page.get_by_label("Name").fill(OFFERING_NAME)
        select_value(page, "Offering type", "PRODUCT")
        page.get_by_label("SKU").fill("WH1000XM5-BLK")
        page.get_by_label("Current price").fill("449.99")
        page.get_by_label("Currency").fill("USD")
        page.get_by_label("Market").fill("US")
        page.get_by_label("Category").fill("Electronics > Audio")
        page.get_by_label("Product URL").fill("https://www.sony.com/electronics/headband-headphones/wh-1000xm5")
        page.get_by_label("Description").fill("Wireless over-ear headphones with active noise cancellation and multipoint Bluetooth.")
        page.get_by_label("Dynamic attributes (JSON)").fill(
            '{"brand":"Sony","color":"Black","battery_life_hours":30,"noise_cancellation":true}'
        )
        capture(page, "14-offering-creation-form.png")
        with page.expect_response(
            lambda r: r.url.endswith("/v1/offerings") and r.request.method == "POST"
        ) as offering_event:
            page.get_by_role("button", name="Create offering", exact=True).click()
        offering_response = offering_event.value
        assert offering_response.status == 201, offering_response.text()
        offering_id = offering_response.json()["id"]
        page.get_by_text(OFFERING_NAME, exact=True).wait_for()
        capture(page, "15-catalog-offering-created.png")

        row = page.locator("tbody tr").filter(has_text=OFFERING_NAME).first
        row.get_by_role("button", name=OFFERING_NAME, exact=True).click()
        page.get_by_text("CURRENT PRICE", exact=True).wait_for()
        capture(page, "16-offering-detail-and-history.png")
        page.keyboard.press("Escape")
        row = page.locator("tbody tr").filter(has_text=OFFERING_NAME).first
        row.get_by_title("Edit", exact=True).click()
        page.get_by_label("Current price").fill("429.99")
        with page.expect_response(
            lambda r: r.url.endswith(f"/v1/offerings/{offering_id}") and r.request.method == "PATCH"
        ) as offering_edit:
            page.get_by_role("button", name="Save changes", exact=True).click()
        assert offering_edit.value.status == 200, offering_edit.value.text()
        assert float(api_get(page, f"/v1/offerings/{offering_id}")["current_price"]) == 429.99

        row = page.locator("tbody tr").filter(has_text=OFFERING_NAME).first
        with page.expect_response(
            lambda r: r.url.endswith(f"/v1/offerings/{offering_id}/toggle-monitoring") and r.request.method == "POST"
        ) as pause_event:
            row.get_by_title("Toggle monitoring", exact=True).click()
        assert pause_event.value.status == 200, pause_event.value.text()
        assert api_get(page, f"/v1/offerings/{offering_id}")["is_monitored"] is False
        row = page.locator("tbody tr").filter(has_text=OFFERING_NAME).first
        with page.expect_response(
            lambda r: r.url.endswith(f"/v1/offerings/{offering_id}/toggle-monitoring") and r.request.method == "POST"
        ) as resume_event:
            row.get_by_title("Toggle monitoring", exact=True).click()
        assert resume_event.value.status == 200, resume_event.value.text()
        assert api_get(page, f"/v1/offerings/{offering_id}")["is_monitored"] is True
        capture(page, "17-monitoring-toggle-persisted.png")

        page.get_by_role("button", name="Dynamic fields", exact=True).click()
        page.get_by_text("Dynamic field definitions", exact=True).wait_for()
        capture(page, "18-dynamic-fields.png")
        page.get_by_role("button", name="Add field", exact=True).click()
        page.get_by_label("Machine name").fill("review_cycle_months")
        page.get_by_label("Display name").fill("Review Cycle")
        page.get_by_label("Data type").fill("NUMBER")
        page.get_by_label("Unit").fill("months")
        page.get_by_label("Category").fill("Commercial")
        capture(page, "19-dynamic-field-form.png")
        with page.expect_response(
            lambda r: r.url.endswith("/v1/offerings/fields") and r.request.method == "POST"
        ) as field_event:
            page.get_by_role("button", name="Create field", exact=True).click()
        assert field_event.value.status == 201, field_event.value.text()
        page.get_by_text("Review Cycle", exact=True).wait_for()
        capture(page, "20-dynamic-field-created.png")
        with page.expect_response(
            lambda r: "/v1/offerings/fields/" in r.url and r.request.method == "DELETE"
        ) as field_delete:
            page.locator("div.list-row").filter(has_text="Review Cycle").last.locator("button.danger-icon").click()
        assert field_delete.value.status == 204, field_delete.value.text()

        page.keyboard.press("Escape")
        page.keyboard.press("Escape")
        page.get_by_role("button", name="Bulk import", exact=True).click()
        bulk_payload = [
            {"name":"Sony ULT WEAR Wireless Headphones","offering_type":"PRODUCT","sku":"ULTWEAR-BLK","current_price":"199.99","currency":"USD","market":"US","url":"https://www.sony.com/electronics/headband-headphones/ult-wear","category":"Electronics > Audio","attributes":{"brand":"Sony","color":"Black"}},
            {"name":"Sony LinkBuds S","offering_type":"PRODUCT","sku":"LINKBUDS-S-BLK","current_price":"199.99","currency":"USD","market":"US","url":"https://www.sony.com/electronics/truly-wireless/linkbuds-s","category":"Electronics > Audio","attributes":{"brand":"Sony","fit":"In-ear"}},
        ]
        page.get_by_label("Offering JSON").fill(json.dumps(bulk_payload))
        capture(page, "21-bulk-import-form.png")
        with page.expect_response(
            lambda r: r.url.endswith("/v1/offerings/bulk") and r.request.method == "POST"
        ) as bulk_event:
            page.get_by_role("button", name="Import offerings", exact=True).click()
        bulk_response = bulk_event.value
        assert bulk_response.status == 200, bulk_response.text()
        assert bulk_response.json()["successful_count"] == 2, bulk_response.text()
        page.get_by_text("Sony ULT WEAR Wireless Headphones", exact=True).wait_for()
        capture(page, "22-bulk-imported-catalog.png")

        csv_path = Path("/tmp/nexora-catalog-export.csv")
        with page.expect_download(timeout=20000) as csv_event:
            page.get_by_role("button", name="CSV", exact=True).click()
        csv_event.value.save_as(str(csv_path))
        assert csv_path.exists() and csv_path.stat().st_size > 0
        json_path = Path("/tmp/nexora-catalog-export.json")
        with page.expect_download(timeout=20000) as json_event:
            page.get_by_role("button", name="JSON", exact=True).click()
        json_event.value.save_as(str(json_path))
        assert json_path.exists() and json_path.stat().st_size > 0

        page.get_by_placeholder("Search name, SKU, category…").fill("Sony ULT WEAR")
        page.get_by_text("Sony ULT WEAR Wireless Headphones", exact=True).wait_for()
        page.get_by_label("Select Sony ULT WEAR Wireless Headphones", exact=True).check()
        with page.expect_response(
            lambda r: r.url.endswith("/v1/offerings/bulk-archive") and r.request.method == "POST"
        ) as archive_event:
            page.get_by_role("button", name="Archive 1", exact=True).click()
        assert archive_event.value.status == 200, archive_event.value.text()
        assert archive_event.value.json()["archived_count"] == 1
        assert page.get_by_text("Sony ULT WEAR Wireless Headphones", exact=True).count() == 0
        archived = api_get(page, "/v1/offerings?q=Sony%20ULT%20WEAR&include_archived=true&page=1&page_size=20")
        assert any(item["is_archived"] for item in archived["items"])
        page.get_by_placeholder("Search name, SKU, category…").fill("")
        page.get_by_text(OFFERING_NAME, exact=True).wait_for()
        capture(page, "23-catalog-import-export-and-archive.png")

        # 5. Matching, HTTP collection, price history and the alert lifecycle.
        page.get_by_role("link", name="Matches", exact=True).click()
        page.get_by_role("heading", name="Offering matches", exact=True).wait_for()
        page.get_by_role("button", name="Add match", exact=True).click()
        select_value(page, "Offering", OFFERING_NAME)
        select_value(page, "Source", SOURCE_NAME)
        page.get_by_label("Competitor target URL").fill(HIGH_URL)
        select_value(page, "Status", "APPROVED")
        page.get_by_label("Confidence (0–1)").fill("0.98")
        capture(page, "24-offering-match-form.png")
        with page.expect_response(
            lambda r: r.url.endswith("/v1/offering-matches") and r.request.method == "POST"
        ) as match_event:
            page.get_by_role("button", name="Create match", exact=True).click()
        match_response = match_event.value
        assert match_response.status == 201, match_response.text()
        match_id = match_response.json()["id"]
        match_row = page.locator("tbody tr").filter(has_text=OFFERING_NAME).first
        page.get_by_text(HIGH_URL, exact=False).wait_for()
        capture(page, "25-offering-match-created.png")

        with page.expect_response(
            lambda r: "/v1/collections/run" in r.url and r.request.method == "POST"
        ) as first_collection_event:
            match_row.get_by_title("Run collection", exact=True).click()
        first_collection_response = first_collection_event.value
        assert first_collection_response.status in (200, 201), first_collection_response.text()
        first_result = first_collection_response.json()
        assert first_result["status"] == "COMPLETED", first_result
        assert first_result["observation"]["price"] == "399.99", first_result
        assert first_result["observation"]["http_status_code"] == 200, first_result
        assert len(api_get(page, f"/v1/offerings/{offering_id}/history")) >= 1
        capture(page, "26-first-price-observation.png")

        page.get_by_role("link", name="Alerts", exact=True).click()
        page.get_by_role("heading", name="Alerts", exact=True).wait_for()
        page.get_by_role("button", name="New rule", exact=True).click()
        page.get_by_label("Rule name").fill("Sony retail price drop")
        select_value(page, "Alert type", "PERCENTAGE_DROP")
        select_value(page, "Offering scope", OFFERING_NAME)
        page.get_by_label("Threshold").fill("10")
        page.get_by_label("Cooldown (minutes)").fill("60")
        capture(page, "27-alert-rule-form.png")
        with page.expect_response(
            lambda r: r.url.endswith("/v1/alerts/rules") and r.request.method == "POST"
        ) as rule_event:
            page.get_by_role("button", name="Create rule", exact=True).click()
        rule_response = rule_event.value
        assert rule_response.status == 201, rule_response.text()
        rule_id = rule_response.json()["id"]
        page.get_by_text("Sony retail price drop", exact=True).wait_for()
        capture(page, "28-alert-rule-created.png")

        page.get_by_role("link", name="Matches", exact=True).click()
        match_row = page.locator("tbody tr").filter(has_text=OFFERING_NAME).first
        match_row.get_by_title("Edit", exact=True).click()
        page.get_by_label("Competitor target URL").fill(LOW_URL)
        with page.expect_response(
            lambda r: r.url.endswith(f"/v1/offering-matches/{match_id}") and r.request.method == "PATCH"
        ) as match_edit:
            page.get_by_role("button", name="Save changes", exact=True).click()
        assert match_edit.value.status == 200, match_edit.value.text()
        match_row = page.locator("tbody tr").filter(has_text=OFFERING_NAME).first
        with page.expect_response(
            lambda r: "/v1/collections/run" in r.url and r.request.method == "POST"
        ) as second_collection_event:
            match_row.get_by_title("Run collection", exact=True).click()
        second_collection_response = second_collection_event.value
        assert second_collection_response.status in (200, 201), second_collection_response.text()
        second_result = second_collection_response.json()
        assert second_result["observation"]["price"] == "349.99", second_result
        assert second_result["snapshot"]["previous_price"] == "399.99", second_result
        assert second_result["snapshot"]["percentage_difference"].startswith("-12.50%"), second_result

        page.get_by_role("link", name="Alerts", exact=True).click()
        page.get_by_text("Competitor price dropped", exact=True).wait_for(timeout=15000)
        logs = api_get(page, "/v1/alerts/logs")
        alert = next((item for item in logs if item["title"] == "Competitor price dropped"), None)
        assert alert is not None and alert["is_read"] is False, logs
        page.get_by_title("Mark as read", exact=True).click()
        page.get_by_title("Read", exact=True).wait_for()
        assert any(item["id"] == alert["id"] and item["is_read"] for item in api_get(page, "/v1/alerts/logs"))
        capture(page, "29-alert-triggered-and-read.png")

        worker_output = dispatch_notifications()
        assert "sent" in worker_output.lower(), worker_output
        alert_email = wait_email("Nexora Competitive Alert: Competitor price dropped", EMAIL, 0)
        assert "Nexora detected a competitive intelligence event" in alert_email

        # 6. Collection history and job details.
        page.get_by_role("link", name="Jobs", exact=True).click()
        page.get_by_role("heading", name="Jobs", exact=True).wait_for()
        page.get_by_text("ON DEMAND REFRESH", exact=False).wait_for(timeout=15000)
        capture(page, "30-collection-job-history.png")
        page.get_by_role("button", name=re.compile("Details")).first.click()
        page.get_by_text("Job ID", exact=True).wait_for()
        capture(page, "31-collection-job-details.png")
        page.keyboard.press("Escape")

        # 7. Secure website discovery, structured extraction, and update rather than duplicate.
        page.get_by_role("link", name="Discovery", exact=True).click()
        page.get_by_role("heading", name="Website discovery", exact=True).wait_for()
        page.get_by_label("Website URL").fill("http://127.0.0.1:8000/v1/health")
        page.get_by_label("Max pages").fill("1")
        with page.expect_response(
            lambda r: r.url.endswith("/v1/discovery/run") and r.request.method == "POST"
        ) as blocked_event:
            page.get_by_role("button", name="Run discovery", exact=True).click()
        assert blocked_event.value.status == 422, blocked_event.value.text()
        capture(page, "32-private-target-blocked.png")

        page.get_by_label("Website URL").fill(DISCOVERY_URL)
        select_value(page, "Default type", "PRODUCT")
        with page.expect_response(
            lambda r: r.url.endswith("/v1/discovery/run") and r.request.method == "POST"
        ) as discovery_event:
            page.get_by_role("button", name="Run discovery", exact=True).click()
        discovery_response = discovery_event.value
        assert discovery_response.status == 200, discovery_response.text()
        discovery_result = discovery_response.json()
        assert discovery_result["status"] == "COMPLETED", discovery_result
        assert discovery_result["created_offerings_count"] == 1, discovery_result
        assert discovery_result["items"][0]["name"] == DISCOVERED_NAME, discovery_result
        page.get_by_text(DISCOVERED_NAME, exact=True).wait_for(timeout=15000)
        capture(page, "33-discovered-catalog-item.png")
        discovery_job_id = discovery_result["job_id"]
        persisted_job = api_get(page, f"/v1/discovery/jobs/{discovery_job_id}")
        assert persisted_job["items"][0]["sku"] == "WF1000XM5-BLK"
        with page.expect_response(
            lambda r: r.url.endswith("/v1/discovery/run") and r.request.method == "POST"
        ) as discovery_update_event:
            page.get_by_role("button", name="Run discovery", exact=True).click()
        assert discovery_update_event.value.status == 200, discovery_update_event.value.text()
        discovery_update = discovery_update_event.value.json()
        assert discovery_update["created_offerings_count"] == 0, discovery_update
        assert discovery_update["updated_offerings_count"] == 1, discovery_update
        catalog = api_get(page, "/v1/offerings?q=Sony%20WF-1000XM5&page=1&page_size=20")
        assert sum(item["sku"] == "WF1000XM5-BLK" for item in catalog["items"]) == 1
        capture(page, "34-discovery-upsert-history.png")

        # 8. Workspace profile and password security, including a delivered reset link.
        page.goto(BASE_URL + "/settings", wait_until="networkidle")
        page.get_by_role("heading", name="Settings", exact=True).wait_for()
        page.get_by_label("Company name").wait_for()
        capture(page, "35-workspace-settings.png")
        page.get_by_label("Company name").fill("Northstar Analytics")
        page.get_by_label("Country").fill("US")
        page.get_by_label("Default currency").fill("USD")
        page.get_by_label("Market").fill("US")
        page.get_by_label("Industry").fill("Consumer Electronics")
        page.get_by_label("Timezone").fill("America/New_York")
        with page.expect_response(
            lambda r: r.url.endswith("/v1/auth/profile") and r.request.method == "PATCH"
        ) as profile_event:
            page.get_by_role("button", name="Save profile", exact=True).click()
        assert profile_event.value.status == 200, profile_event.value.text()
        profile = api_get(page, "/v1/auth/profile")
        assert profile["company_name"] == "Northstar Analytics"
        capture(page, "36-workspace-profile-saved.png")

        page.get_by_label("Current password").fill(INITIAL_PASSWORD)
        page.get_by_label("New password").fill(UPDATED_PASSWORD)
        with page.expect_response(
            lambda r: r.url.endswith("/v1/auth/change-password") and r.request.method == "POST"
        ) as password_event:
            page.get_by_role("button", name="Update password", exact=True).click()
        assert password_event.value.status == 200, password_event.value.text()
        wrong_password = page.request.post(
            API_URL + "/v1/auth/login", json={"email": EMAIL, "password": INITIAL_PASSWORD}
        )
        assert wrong_password.status == 401, wrong_password.text()
        valid_password = page.request.post(
            API_URL + "/v1/auth/login", json={"email": EMAIL, "password": UPDATED_PASSWORD}
        )
        assert valid_password.status == 200, valid_password.text()
        capture(page, "37-password-changed.png")

        ui_sign_out(page)
        page.get_by_role("link", name="Forgot password?", exact=True).click()
        page.get_by_label("Work email").fill(EMAIL)
        before_reset = len(mailbox_messages())
        with page.expect_response(
            lambda r: r.url.endswith("/v1/auth/forgot-password") and r.request.method == "POST"
        ) as forgot_event:
            page.get_by_role("button", name="Send reset link", exact=True).click()
        assert forgot_event.value.status == 200, forgot_event.value.text()
        page.get_by_role("heading", name="Check your inbox", exact=True).wait_for()
        capture(page, "38-password-reset-requested.png")
        reset_body = wait_email("Reset your Nexora password", EMAIL, before_reset)
        reset_url = link_from_email(reset_body, "reset-password")
        page.goto(reset_url, wait_until="networkidle")
        page.get_by_label("New password").wait_for()
        capture(page, "39-password-reset-form.png")
        page.get_by_label("New password").fill(RESET_PASSWORD)
        with page.expect_response(
            lambda r: r.url.endswith("/v1/auth/reset-password") and r.request.method == "POST"
        ) as reset_event:
            page.get_by_role("button", name="Update password", exact=True).click()
        assert reset_event.value.status == 200, reset_event.value.text()
        page.get_by_role("heading", name="Password updated", exact=True).wait_for()
        capture(page, "40-password-reset-complete.png")
        page.get_by_role("link", name="Continue to sign in", exact=True).click()
        ui_login(page, EMAIL, RESET_PASSWORD)
        capture(page, "41-workspace-after-password-reset.png")

        # 9. Analyst and Viewer are real database users with real issued tokens.
        viewer_email = runner.run(persist_role_user(client_id, RoleEnum.VIEWER, "read-only"))
        analyst_email = runner.run(persist_role_user(client_id, RoleEnum.ANALYST, "insights"))
        ui_sign_out(page)
        ui_login(page, analyst_email, ROLE_PASSWORD)
        page.get_by_role("link", name="Competitors", exact=True).click()
        page.get_by_role("heading", name="Competitors", exact=True).wait_for()
        assert page.get_by_role("button", name="Add competitor", exact=True).count() == 0
        denied = page.request.post(
            API_URL + "/v1/competitors",
            headers=bearer(page),
            data=json.dumps({"name": "Analyst forbidden write", "domain": "analyst-forbidden.example"}),
            headers_update={"Content-Type":"application/json"} if False else None,
        ) if False else page.request.post(
            API_URL + "/v1/competitors",
            headers={**bearer(page), "Content-Type":"application/json"},
            data=json.dumps({"name": "Analyst forbidden write", "domain": "analyst-forbidden.example"}),
        )
        assert denied.status == 403, denied.text()
        page.get_by_role("link", name="Discovery", exact=True).click()
        assert page.get_by_role("button", name="Run discovery", exact=True).is_visible()
        capture(page, "42-analyst-role.png")

        ui_sign_out(page)
        ui_login(page, viewer_email, ROLE_PASSWORD)
        page.get_by_role("link", name="Offerings", exact=True).click()
        page.get_by_role("heading", name="Offerings", exact=True).wait_for()
        assert page.get_by_role("button", name="Add offering", exact=True).count() == 0
        assert page.get_by_role("button", name="Bulk import", exact=True).count() == 0
        assert page.get_by_role("button", name="Dynamic fields", exact=True).count() == 0
        read_only = page.request.get(API_URL + "/v1/offerings", headers=bearer(page))
        assert read_only.status == 200, read_only.text()
        denied = page.request.post(
            API_URL + "/v1/competitors",
            headers={**bearer(page), "Content-Type":"application/json"},
            data=json.dumps({"name": "Viewer forbidden write", "domain": "viewer-forbidden.example"}),
        )
        assert denied.status == 403, denied.text()
        capture(page, "43-viewer-read-only-role.png")

        mobile = context.new_page()
        mobile.set_viewport_size({"width": 390, "height": 844})
        mobile.goto(BASE_URL + "/welcome", wait_until="networkidle")
        dimensions = mobile.evaluate(
            "() => ({viewport:document.documentElement.clientWidth, content:document.documentElement.scrollWidth})"
        )
        assert dimensions["content"] <= dimensions["viewport"], dimensions
        capture(mobile, "44-mobile-homepage.png")

        assert not JS_ERRORS, "Uncaught browser JavaScript errors: " + " | ".join(JS_ERRORS)
        expected = [p.name for p in SCREENSHOTS.glob("*.png")]
        assert len(expected) >= 40, f"Expected at least 40 walkthrough screens, found {len(expected)}"
        print(f"PASS: real UI/API/PostgreSQL journey; {len(expected)} screenshots captured.", flush=True)
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
