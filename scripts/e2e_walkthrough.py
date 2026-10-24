"""Real browser walkthrough: actual React UI, FastAPI HTTP endpoints and PostgreSQL."""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
from email import message_from_string
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

BASE = os.getenv("NEXORA_FRONTEND_URL", "http://127.0.0.1:4173").rstrip("/")
API = os.getenv("NEXORA_API_URL", "http://127.0.0.1:8000").rstrip("/")
BACKEND_ROOT = Path(os.getenv("NEXORA_BACKEND_ROOT", "../nexora-backend")).resolve()
SHOTS = Path(os.getenv("NEXORA_SCREENSHOTS", "docs/walkthrough/screenshots"))
MAILBOX = Path(os.getenv("NEXORA_MAILBOX", "/tmp/nexora-mailbox.jsonl"))
EMAIL = "market-analyst@northstar.example.com"
PASSWORD = "Nexora-Strong!2026"
CHANGED_PASSWORD = "Nexora-Updated!2026"
RESET_PASSWORD = "Nexora-Final!2026"
ROLE_PASSWORD = "Nexora-Role!2026"
ORG = "Northstar Market Intelligence"
NAME = "Sony Retail Reference"
SOURCE = "Sony Product Listing"
OFFERING = "Sony WH-1000XM5 Wireless Headphones"
DISCOVERED = "Sony WF-1000XM5 Truly Wireless Noise Canceling Earbuds"
HIGH = "https://cdn.jsdelivr.net/gh/faizansaiyed123/Nexora-backend@main/tests/fixtures/retail-price-high.html"
LOW = "https://cdn.jsdelivr.net/gh/faizansaiyed123/Nexora-backend@main/tests/fixtures/retail-price-low.html"
DISCOVERY = "https://cdn.jsdelivr.net/gh/faizansaiyed123/Nexora-backend@main/tests/fixtures/retail-discovery-product.html"
js_errors: list[str] = []
captures: list[str] = []


def path_is(response, path: str, method: str | None = None) -> bool:
    return urlparse(response.url).path.endswith(path) and (method is None or response.request.method == method)


def shot(page, filename: str) -> None:
    SHOTS.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(SHOTS / filename), full_page=True, animations="disabled", caret="hide")
    captures.append(filename)
    print("Captured " + filename, flush=True)


def select_option(page, label: str, option: str) -> None:
    field = page.locator("label.field").filter(has_text=label).last
    field.locator("button.select-trigger").click()
    page.get_by_role("option", name=option, exact=True).last.click()


def access_token(page) -> str:
    value = page.evaluate("() => localStorage.getItem('nexora.access')")
    assert value, "Browser session did not save an access token."
    return str(value)


def api_get(page, path: str):
    response = page.request.get(API + path, headers={"Authorization": "Bearer " + access_token(page)})
    assert response.status == 200, f"GET {path}: {response.status} {response.text()}"
    return response.json()


def helper(*args: str) -> str:
    result = subprocess.run(
        [os.sys.executable, str(Path(__file__).with_name("e2e_support.py")), *args],
        cwd=BACKEND_ROOT, capture_output=True, text=True, check=True, timeout=30,
    )
    return result.stdout.strip()


def messages() -> list[dict]:
    if not MAILBOX.exists():
        return []
    found = []
    for line in MAILBOX.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
            if row.get("data"):
                found.append(row)
        except (json.JSONDecodeError, AttributeError):
            pass
    return found


def mail_parts(row: dict) -> tuple[str, str, list[str]]:
    msg = message_from_string(str(row["data"]))
    if msg.is_multipart():
        body_parts = []
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                raw = part.get_payload(decode=True)
                if raw:
                    body_parts.append(raw.decode(part.get_content_charset() or "utf-8", "replace"))
        body = "\n".join(body_parts)
    else:
        raw = msg.get_payload(decode=True)
        body = raw.decode(msg.get_content_charset() or "utf-8", "replace") if raw else str(msg.get_payload())
    return str(msg.get("Subject", "")), body, [str(x).lower() for x in row.get("rcpt_tos", [])]


def wait_mail(subject_part: str, recipient: str, start: int, timeout: float = 40) -> str:
    until = time.monotonic() + timeout
    while time.monotonic() < until:
        for row in messages()[start:]:
            subject, body, recipients = mail_parts(row)
            if subject_part.lower() in subject.lower() and recipient.lower() in recipients:
                return body
        time.sleep(0.25)
    subjects = [mail_parts(row)[0] for row in messages()[start:]]
    raise AssertionError(f"Email {subject_part!r} not delivered to {recipient}; received {subjects}")


def link_from_email(body: str, route: str) -> str:
    found = re.search(rf"https?://[^\s<>]+/{re.escape(route)}\?token=[^\s<>]+", body)
    assert found, f"Email did not contain a one-time {route} URL."
    return found.group(0).rstrip(".,);")


def login(page, email: str, password: str) -> None:
    page.get_by_label("Work email").fill(email)
    page.get_by_label("Password").fill(password)
    with page.expect_response(lambda r: path_is(r, "/v1/auth/login", "POST")) as evt:
        page.get_by_role("button", name=re.compile("Sign in")).click()
    assert evt.value.status == 200, evt.value.text()
    page.get_by_role("heading", name="Dashboard", exact=True).wait_for(timeout=15000)


def logout(page) -> None:
    page.locator("button.profile-trigger").click()
    page.get_by_text("Sign out", exact=True).click()
    page.get_by_label("Work email").wait_for(timeout=10000)


def main() -> None:
    SHOTS.mkdir(parents=True, exist_ok=True)
    if MAILBOX.exists():
        MAILBOX.unlink()
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context(viewport={"width": 1440, "height": 1000}, accept_downloads=True)
        page = context.new_page()
        page.set_default_timeout(12000)
        page.on("pageerror", lambda error: js_errors.append(str(error)))
        page.on("dialog", lambda dialog: dialog.accept())

        # Registration and mail-based verification.
        page.goto(BASE + "/welcome", wait_until="networkidle")
        assert page.get_by_role("heading", name=re.compile("Understand the market")).is_visible()
        shot(page, "00-public-homepage.png")
        page.locator(".landing-nav-actions").get_by_role("link", name="Create workspace").click()
        page.get_by_label("Organization name").wait_for()
        shot(page, "01-registration-form.png")
        page.get_by_label("Organization name").fill(ORG)
        page.get_by_label("Your full name").fill("Alex Morgan")
        page.get_by_label("Work email").fill(EMAIL)
        page.get_by_label("Password").fill(PASSWORD)
        mail_start = len(messages())
        with page.expect_response(lambda r: path_is(r, "/v1/auth/register", "POST")) as evt:
            page.get_by_role("button", name=re.compile("Create workspace")).click()
        assert evt.value.status == 201, evt.value.text()
        assert evt.value.json()["email_verification_required"] is True
        page.get_by_role("heading", name="Verification required").wait_for()
        shot(page, "02-verification-email-sent.png")
        verify_link = link_from_email(wait_mail("Verify your Nexora account", EMAIL, mail_start), "verify-email")
        page.goto(verify_link, wait_until="networkidle")
        shot(page, "03-email-verification-page.png")
        with page.expect_response(lambda r: path_is(r, "/v1/auth/verify-email", "GET")) as evt:
            page.get_by_role("button", name=re.compile("Verify email")).click()
        assert evt.value.status == 200, evt.value.text()
        shot(page, "04-email-verified.png")
        page.get_by_role("link", name="Continue to sign in", exact=True).click()
        shot(page, "05-login.png")
        login(page, EMAIL, PASSWORD)
        shot(page, "06-dashboard-empty-workspace.png")
        me = api_get(page, "/v1/auth/me")
        assert me["role"] == "ORG_ADMIN"
        client_id = me["client_id"]

        # Competitor management and duplicate-domain business rule.
        page.get_by_role("link", name="Competitors", exact=True).click()
        page.get_by_role("heading", name="Competitors", exact=True).wait_for()
        shot(page, "07-competitors-empty.png")
        page.get_by_role("button", name="Add competitor", exact=True).click()
        page.get_by_label("Name").fill(NAME)
        page.get_by_label("Domain").fill("cdn.jsdelivr.net")
        with page.expect_response(lambda r: path_is(r, "/v1/competitors", "POST")) as evt:
            page.get_by_role("button", name="Save competitor", exact=True).click()
        assert evt.value.status == 201, evt.value.text()
        competitor_id = evt.value.json()["id"]
        shot(page, "08-competitor-created.png")
        page.get_by_role("button", name="Add competitor", exact=True).click()
        page.get_by_label("Name").fill("Duplicate retail product source")
        page.get_by_label("Domain").fill("cdn.jsdelivr.net")
        with page.expect_response(lambda r: path_is(r, "/v1/competitors", "POST")) as evt:
            page.get_by_role("button", name="Save competitor", exact=True).click()
        assert evt.value.status == 403, evt.value.text()
        page.get_by_text("A competitor with this domain already exists.").wait_for()
        shot(page, "09-duplicate-domain-rejected.png")
        page.get_by_role("button", name="Cancel", exact=True).click()
        page.locator("tbody tr").filter(has_text=NAME).first.locator("button").first.click()
        page.get_by_label("Name").fill("Sony Retail Reference")
        with page.expect_response(lambda r: path_is(r, f"/v1/competitors/{competitor_id}", "PATCH")) as evt:
            page.get_by_role("button", name="Save competitor", exact=True).click()
        assert evt.value.status == 200, evt.value.text()
        competitor_name = "Sony Retail Reference"
        assert any(row["id"] == competitor_id and row["name"] == competitor_name for row in api_get(page, "/v1/competitors"))

        # Configure the real source and read back its persisted settings.
        page.get_by_role("link", name="Sources", exact=True).click()
        page.get_by_role("button", name="Add source", exact=True).click()
        select_option(page, "Competitor", competitor_name)
        page.get_by_label("Source name").fill(SOURCE)
        page.get_by_label("Base URL").fill(HIGH)
        select_option(page, "Source type", "OFFICIAL_STORE")
        select_option(page, "Collection method", "HTTP_FAST")
        shot(page, "10-source-creation-form.png")
        with page.expect_response(lambda r: path_is(r, "/v1/sources", "POST")) as evt:
            page.get_by_role("button", name="Create source", exact=True).click()
        assert evt.value.status == 201, evt.value.text()
        source_id = evt.value.json()["id"]
        source_name = SOURCE
        shot(page, "11-sources-created.png")
        page.get_by_title("Configuration", exact=True).click()
        page.get_by_label("Rate / minute").fill("60")
        page.get_by_label("Delay seconds").fill("0.1")
        page.get_by_label("Timeout seconds").fill("25")
        page.get_by_label("Max retries").fill("1")
        page.get_by_label("Custom headers (JSON)").fill('{"Accept-Language":"en-US,en;q=0.9"}')
        page.get_by_label("Extraction selectors (JSON)").fill("{}")
        shot(page, "12-source-configuration.png")
        with page.expect_response(lambda r: path_is(r, f"/v1/sources/{source_id}/configuration", "PATCH")) as evt:
            page.get_by_role("button", name="Save configuration", exact=True).click()
        assert evt.value.status == 200, evt.value.text()
        source_saved = api_get(page, f"/v1/sources/{source_id}")
        assert source_saved["configuration"]["rate_limit_rpm"] == 60
        assert source_saved["configuration"]["max_retries"] == 1
        page.get_by_title("Edit source", exact=True).click()
        page.get_by_label("Source name").fill(source_name + " (Structured)")
        with page.expect_response(lambda r: path_is(r, f"/v1/sources/{source_id}", "PATCH")) as evt:
            page.get_by_role("button", name="Save changes", exact=True).click()
        assert evt.value.status == 200, evt.value.text()
        source_name += " (Structured)"
        shot(page, "13-source-configuration-saved.png")

        # Catalog creation, detail and history, update, monitoring, dynamic schema,
        # bulk import/export, filters and safe archive.
        page.get_by_role("link", name="Offerings", exact=True).click()
        page.get_by_role("button", name="Add offering", exact=True).click()
        page.get_by_label("Name").fill(OFFERING)
        select_option(page, "Offering type", "PRODUCT")
        page.get_by_label("SKU").fill("WH1000XM5-BLK")
        page.get_by_label("Current price").fill("449.99")
        page.get_by_label("Currency").fill("USD")
        page.get_by_label("Market").fill("US")
        page.get_by_label("Category").fill("Electronics > Audio")
        page.get_by_label("Product URL").fill("https://www.sony.com/electronics/headband-headphones/wh-1000xm5")
        page.get_by_label("Description").fill("Wireless over-ear headphones with active noise cancellation and multipoint Bluetooth.")
        page.get_by_label("Dynamic attributes (JSON)").fill('{"brand":"Sony","color":"Black","battery_life_hours":30,"noise_cancellation":true}')
        shot(page, "14-offering-creation-form.png")
        with page.expect_response(lambda r: path_is(r, "/v1/offerings", "POST")) as evt:
            page.get_by_role("button", name="Create offering", exact=True).click()
        assert evt.value.status == 201, evt.value.text()
        offering_id = evt.value.json()["id"]
        shot(page, "15-catalog-offering-created.png")
        page.locator("tbody tr").filter(has_text=OFFERING).first.get_by_role("button", name=OFFERING, exact=True).click()
        page.get_by_text("CURRENT PRICE", exact=True).wait_for()
        shot(page, "16-offering-detail-and-history.png")
        page.get_by_role("button", name="Close dialog", exact=True).click()
        row = page.locator("tbody tr").filter(has_text=OFFERING).first
        row.get_by_title("Edit", exact=True).click()
        page.get_by_label("Current price").fill("429.99")
        with page.expect_response(lambda r: path_is(r, f"/v1/offerings/{offering_id}", "PATCH")) as evt:
            page.get_by_role("button", name="Save changes", exact=True).click()
        assert evt.value.status == 200, evt.value.text()
        assert float(api_get(page, f"/v1/offerings/{offering_id}")["current_price"]) == 429.99
        row = page.locator("tbody tr").filter(has_text=OFFERING).first
        with page.expect_response(lambda r: path_is(r, f"/v1/offerings/{offering_id}/toggle-monitoring", "POST")) as evt:
            row.get_by_title("Toggle monitoring", exact=True).click()
        assert evt.value.status == 200
        assert api_get(page, f"/v1/offerings/{offering_id}")["is_monitored"] is False
        row = page.locator("tbody tr").filter(has_text=OFFERING).first
        with page.expect_response(lambda r: path_is(r, f"/v1/offerings/{offering_id}/toggle-monitoring", "POST")) as evt:
            row.get_by_title("Toggle monitoring", exact=True).click()
        assert evt.value.status == 200
        assert api_get(page, f"/v1/offerings/{offering_id}")["is_monitored"] is True
        shot(page, "17-catalog-monitoring-active.png")

        page.get_by_role("button", name="Dynamic fields", exact=True).click()
        page.get_by_text("Dynamic field definitions", exact=True).wait_for()
        shot(page, "18-dynamic-fields.png")
        page.get_by_role("button", name="Add field", exact=True).click()
        page.get_by_label("Machine name").fill("review_cycle_months")
        page.get_by_label("Display name").fill("Review Cycle")
        page.get_by_label("Data type").fill("NUMBER")
        page.get_by_label("Unit").fill("months")
        page.get_by_label("Category").fill("Commercial")
        shot(page, "19-dynamic-field-form.png")
        with page.expect_response(lambda r: path_is(r, "/v1/offerings/fields", "POST")) as evt:
            page.get_by_role("button", name="Create field", exact=True).click()
        assert evt.value.status == 201, evt.value.text()
        shot(page, "20-dynamic-field-created.png")
        field_row = page.locator("div.list-row").filter(has_text="Review Cycle").last
        with page.expect_response(lambda r: "/v1/offerings/fields/" in urlparse(r.url).path and r.request.method == "DELETE") as evt:
            field_row.locator("button.danger-icon").click()
        assert evt.value.status == 204, evt.value.text()
        page.get_by_role("button", name="Close dialog", exact=True).click()
        page.get_by_role("button", name="Close dialog", exact=True).click()
        page.get_by_role("button", name="Bulk import", exact=True).click()
        bulk = [
          {"name":"Sony ULT WEAR Wireless Headphones","offering_type":"PRODUCT","sku":"ULTWEAR-BLK","current_price":"199.99","currency":"USD","market":"US","url":"https://www.sony.com/electronics/headband-headphones/ult-wear","category":"Electronics > Audio","attributes":{"brand":"Sony","color":"Black"}},
          {"name":"Sony LinkBuds S","offering_type":"PRODUCT","sku":"LINKBUDS-S-BLK","current_price":"199.99","currency":"USD","market":"US","url":"https://www.sony.com/electronics/truly-wireless/linkbuds-s","category":"Electronics > Audio","attributes":{"brand":"Sony","fit":"In-ear"}},
        ]
        page.get_by_label("Offering JSON").fill(json.dumps(bulk))
        shot(page, "21-bulk-import-form.png")
        with page.expect_response(lambda r: path_is(r, "/v1/offerings/bulk", "POST")) as evt:
            page.get_by_role("button", name="Import offerings", exact=True).click()
        assert evt.value.status == 200 and evt.value.json()["successful_count"] == 2, evt.value.text()
        shot(page, "22-bulk-imported-catalog.png")
        for fmt, filename in [("CSV", "nexora-export.csv"), ("JSON", "nexora-export.json")]:
            with page.expect_download(timeout=15000) as download_event:
                page.get_by_role("button", name=fmt, exact=True).click()
            download_event.value.save_as("/tmp/" + filename)
            assert Path("/tmp/" + filename).stat().st_size > 0
        page.get_by_placeholder("Search name, SKU, category…").fill("Sony ULT WEAR")
        page.get_by_text("Sony ULT WEAR Wireless Headphones", exact=True).wait_for()
        page.get_by_label("Select Sony ULT WEAR Wireless Headphones", exact=True).check()
        with page.expect_response(lambda r: path_is(r, "/v1/offerings/bulk-archive", "POST")) as evt:
            page.get_by_role("button", name="Archive 1", exact=True).click()
        assert evt.value.status == 200 and evt.value.json()["archived_count"] == 1, evt.value.text()
        archived = api_get(page, "/v1/offerings?q=Sony%20ULT%20WEAR&include_archived=true&page=1&page_size=20")
        assert any(item["is_archived"] for item in archived["items"])
        page.get_by_placeholder("Search name, SKU, category…").fill("")
        shot(page, "23-catalog-import-export-and-archive.png")

        # Match the offering to a public product page and collect its current price.
        page.get_by_role("link", name="Matches", exact=True).click()
        page.get_by_role("button", name="Add match", exact=True).click()
        select_option(page, "Offering", OFFERING)
        select_option(page, "Source", source_name)
        page.get_by_label("Competitor target URL").fill(HIGH)
        select_option(page, "Status", "APPROVED")
        page.get_by_label("Confidence (0–1)").fill("0.98")
        shot(page, "24-offering-match-form.png")
        with page.expect_response(lambda r: path_is(r, "/v1/offering-matches", "POST")) as evt:
            page.get_by_role("button", name="Create match", exact=True).click()
        assert evt.value.status == 201, evt.value.text()
        match_id = evt.value.json()["id"]
        row = page.locator("tbody tr").filter(has_text=OFFERING).first
        shot(page, "25-offering-match-created.png")
        with page.expect_response(lambda r: path_is(r, "/v1/collections/run", "POST")) as evt:
            row.get_by_title("Run collection", exact=True).click()
        first = evt.value
        assert first.status in (200, 201), first.text()
        first_data = first.json()
        assert first_data["status"] == "COMPLETED", first_data
        assert first_data["observation"]["price"] == "399.99", first_data
        assert len(api_get(page, f"/v1/offerings/{offering_id}/history")) >= 1
        shot(page, "26-first-price-observation.png")

        # A 12.5% price drop generates a database-backed alert and transactional email.
        page.get_by_role("link", name="Alerts", exact=True).click()
        page.get_by_role("button", name="New rule", exact=True).click()
        page.get_by_label("Rule name").fill("Sony retail price drop")
        select_option(page, "Alert type", "PERCENTAGE_DROP")
        select_option(page, "Offering scope", OFFERING)
        page.get_by_label("Threshold").fill("10")
        page.get_by_label("Cooldown (minutes)").fill("60")
        shot(page, "27-alert-rule-form.png")
        with page.expect_response(lambda r: path_is(r, "/v1/alerts/rules", "POST")) as evt:
            page.get_by_role("button", name="Create rule", exact=True).click()
        assert evt.value.status == 201, evt.value.text()
        shot(page, "28-alert-rule-created.png")
        page.get_by_role("link", name="Matches", exact=True).click()
        page.locator("tbody tr").filter(has_text=OFFERING).first.get_by_title("Edit", exact=True).click()
        page.get_by_label("Competitor target URL").fill(LOW)
        with page.expect_response(lambda r: path_is(r, f"/v1/offering-matches/{match_id}", "PATCH")) as evt:
            page.get_by_role("button", name="Save changes", exact=True).click()
        assert evt.value.status == 200, evt.value.text()
        with page.expect_response(lambda r: path_is(r, "/v1/collections/run", "POST")) as evt:
            page.locator("tbody tr").filter(has_text=OFFERING).first.get_by_title("Run collection", exact=True).click()
        second = evt.value
        assert second.status in (200, 201), second.text()
        second_data = second.json()
        assert second_data["observation"]["price"] == "349.99", second_data
        assert second_data["snapshot"]["previous_price"] == "399.99", second_data
        assert str(second_data["snapshot"]["percentage_difference"]).startswith("-12.50"), second_data
        page.get_by_role("link", name="Alerts", exact=True).click()
        page.get_by_text("Competitor price dropped", exact=True).wait_for(timeout=15000)
        logs = api_get(page, "/v1/alerts/logs")
        alert_log = next((item for item in logs if item["title"] == "Competitor price dropped"), None)
        assert alert_log and not alert_log["is_read"], logs
        page.get_by_title("Mark as read", exact=True).click()
        page.get_by_title("Read", exact=True).wait_for()
        assert any(item["id"] == alert_log["id"] and item["is_read"] for item in api_get(page, "/v1/alerts/logs"))
        shot(page, "29-alert-generated-and-read.png")
        dispatch = json.loads(helper("dispatch-notifications"))
        assert dispatch["sent"] >= 1, dispatch
        alert_body = wait_mail("Nexora Competitive Alert: Competitor price dropped", EMAIL, 0)
        assert "Nexora detected a competitive intelligence event" in alert_body
        assert "SENT" in json.loads(helper("notification-statuses", client_id))

        page.get_by_role("link", name="Jobs", exact=True).click()
        page.get_by_role("heading", name="Jobs", exact=True).wait_for()
        page.get_by_text("COLLECTION", exact=False).wait_for(timeout=15000)
        shot(page, "30-collection-job-history.png")
        page.get_by_role("button", name="Details", exact=True).first.click()
        page.get_by_text("Job ID", exact=True).wait_for()
        shot(page, "31-collection-job-detail.png")
        page.get_by_role("button", name="Close dialog", exact=True).click()

        # Website discovery demonstrates private-target rejection and evidence-based upsert.
        page.get_by_role("link", name="Discovery", exact=True).click()
        page.get_by_label("Website URL").fill("http://127.0.0.1:8000/v1/health")
        page.get_by_label("Max pages").fill("1")
        with page.expect_response(lambda r: path_is(r, "/v1/discovery/run", "POST")) as evt:
            page.get_by_role("button", name="Run discovery", exact=True).click()
        assert evt.value.status == 422, evt.value.text()
        shot(page, "32-private-target-blocked.png")
        page.get_by_label("Website URL").fill(DISCOVERY)
        select_option(page, "Default type", "PRODUCT")
        with page.expect_response(lambda r: path_is(r, "/v1/discovery/run", "POST")) as evt:
            page.get_by_role("button", name="Run discovery", exact=True).click()
        discovered = evt.value
        assert discovered.status == 200, discovered.text()
        data = discovered.json()
        assert data["status"] == "COMPLETED" and data["created_offerings_count"] == 1, data
        assert data["items"][0]["name"] == DISCOVERED, data
        shot(page, "33-discovery-product-created.png")
        assert api_get(page, f"/v1/discovery/jobs/{data['job_id']}")["items"][0]["sku"] == "WF1000XM5-BLK"
        with page.expect_response(lambda r: path_is(r, "/v1/discovery/run", "POST")) as evt:
            page.get_by_role("button", name="Run discovery", exact=True).click()
        upsert = evt.value.json()
        assert upsert["created_offerings_count"] == 0 and upsert["updated_offerings_count"] == 1, upsert
        all_found = api_get(page, "/v1/offerings?q=Sony%20WF-1000XM5&page=1&page_size=20")["items"]
        assert sum(item["sku"] == "WF1000XM5-BLK" for item in all_found) == 1
        shot(page, "34-discovery-upsert-history.png")

        # Profile update, password change and one-time password recovery.
        page.get_by_role("link", name="Settings", exact=True).click()
        page.get_by_label("Company name").wait_for()
        shot(page, "35-workspace-settings.png")
        page.get_by_label("Company name").fill("Northstar Analytics")
        page.get_by_label("Country").fill("US")
        page.get_by_label("Default currency").fill("USD")
        page.get_by_label("Market").fill("US")
        page.get_by_label("Industry").fill("Consumer Electronics")
        page.get_by_label("Timezone").fill("America/New_York")
        with page.expect_response(lambda r: path_is(r, "/v1/auth/profile", "PATCH")) as evt:
            page.get_by_role("button", name="Save profile", exact=True).click()
        assert evt.value.status == 200, evt.value.text()
        assert api_get(page, "/v1/auth/profile")["company_name"] == "Northstar Analytics"
        shot(page, "36-workspace-profile-updated.png")
        page.get_by_label("Current password").fill(PASSWORD)
        page.get_by_label("New password").fill(CHANGED_PASSWORD)
        with page.expect_response(lambda r: path_is(r, "/v1/auth/change-password", "POST")) as evt:
            page.get_by_role("button", name="Update password", exact=True).click()
        assert evt.value.status == 200, evt.value.text()
        assert page.request.post(API + "/v1/auth/login", json={"email": EMAIL, "password": PASSWORD}).status == 401
        assert page.request.post(API + "/v1/auth/login", json={"email": EMAIL, "password": CHANGED_PASSWORD}).status == 200
        shot(page, "37-password-changed.png")
        logout(page)
        page.get_by_role("link", name="Forgot password?", exact=True).click()
        page.get_by_label("Work email").fill(EMAIL)
        reset_mail_start = len(messages())
        with page.expect_response(lambda r: path_is(r, "/v1/auth/forgot-password", "POST")) as evt:
            page.get_by_role("button", name="Send reset link", exact=True).click()
        assert evt.value.status == 200, evt.value.text()
        shot(page, "38-password-reset-requested.png")
        reset_link = link_from_email(wait_mail("Reset your Nexora password", EMAIL, reset_mail_start), "reset-password")
        page.goto(reset_link, wait_until="networkidle")
        page.get_by_label("New password").wait_for()
        shot(page, "39-password-reset-form.png")
        page.get_by_label("New password").fill(RESET_PASSWORD)
        with page.expect_response(lambda r: path_is(r, "/v1/auth/reset-password", "POST")) as evt:
            page.get_by_role("button", name="Update password", exact=True).click()
        assert evt.value.status == 200, evt.value.text()
        page.get_by_role("heading", name="Password updated", exact=True).wait_for()
        shot(page, "40-password-reset-complete.png")
        page.get_by_role("link", name="Continue to sign in", exact=True).click()
        login(page, EMAIL, RESET_PASSWORD)
        shot(page, "41-dashboard-after-password-reset.png")

        # Real persisted analyst/viewer accounts exercise UI and API authorization.
        suffix = str(int(time.time()))
        analyst = f"analyst-{suffix}@northstar.example.com"
        viewer = f"viewer-{suffix}@northstar.example.com"
        helper("seed-role", client_id, "ANALYST", analyst, ROLE_PASSWORD)
        helper("seed-role", client_id, "VIEWER", viewer, ROLE_PASSWORD)
        logout(page)
        login(page, analyst, ROLE_PASSWORD)
        page.get_by_role("link", name="Competitors", exact=True).click()
        assert page.get_by_role("button", name="Add competitor", exact=True).count() == 0
        denied = page.request.post(API + "/v1/competitors", headers={"Authorization":"Bearer " + access_token(page)}, json={"name":"Not Allowed","domain":"forbidden.example"})
        assert denied.status == 403, denied.text()
        page.get_by_role("link", name="Discovery", exact=True).click()
        assert page.get_by_role("button", name="Run discovery", exact=True).is_visible()
        shot(page, "42-analyst-workspace.png")
        logout(page)
        login(page, viewer, ROLE_PASSWORD)
        page.get_by_role("link", name="Offerings", exact=True).click()
        assert page.get_by_role("button", name="Add offering", exact=True).count() == 0
        assert page.get_by_role("button", name="Bulk import", exact=True).count() == 0
        assert page.get_by_role("button", name="Dynamic fields", exact=True).count() == 0
        response = page.request.get(API + "/v1/offerings", headers={"Authorization":"Bearer " + access_token(page)})
        assert response.status == 200, response.text()
        denied = page.request.post(API + "/v1/competitors", headers={"Authorization":"Bearer " + access_token(page)}, json={"name":"Viewer Write Attempt","domain":"viewer-write.example"})
        assert denied.status == 403, denied.text()
        shot(page, "43-viewer-read-only-workspace.png")

        mobile = context.new_page()
        mobile.set_viewport_size({"width":390,"height":844})
        mobile.goto(BASE + "/welcome", wait_until="networkidle")
        dimensions = mobile.evaluate("() => ({viewport:document.documentElement.clientWidth,content:document.documentElement.scrollWidth})")
        assert dimensions["content"] <= dimensions["viewport"], dimensions
        shot(mobile, "44-mobile-homepage.png")
        assert not js_errors, "Browser JavaScript errors: " + " | ".join(js_errors)

        (SHOTS.parent / "manifest.json").write_text(json.dumps({
            "product":"Nexora","base_commit":os.getenv("GITHUB_SHA","local"),
            "captured_screenshots":captures,"count":len(captures),
            "scope":"real browser UI, FastAPI HTTP requests, PostgreSQL persistence and isolated SMTP delivery",
        }, indent=2) + "\n", encoding="utf-8")
        (SHOTS.parent / "run-summary.json").write_text(json.dumps({
            "status":"passed","browser":"Chromium","screenshots":len(captures),
            "database":"disposable PostgreSQL","api":API,"frontend":BASE,
        }, indent=2) + "\n", encoding="utf-8")
        print(f"Full Nexora UI-to-API-to-PostgreSQL journey passed: {len(captures)} screenshots.", flush=True)
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
