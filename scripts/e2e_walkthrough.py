"""Browser walkthrough through Nexora's real UI, API and PostgreSQL persistence."""
from __future__ import annotations
import asyncio, json, os, re, time, uuid
from email import message_from_string
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from sqlalchemy import select
from backend.core.security import get_password_hash
from backend.db.session import AsyncSessionLocal, engine
from backend.models.alert import AlertLogModel
from backend.models.client import UserModel
from backend.models.competitor import CompetitorModel, SourceModel
from backend.models.enums import RoleEnum
from backend.models.notification import NotificationOutboxModel
from backend.models.observation import JobModel, ObservationModel, SnapshotModel
from backend.models.offering import OfferingModel
from backend.workers.tasks import _dispatch_pending_notifications

BASE = os.getenv("NEXORA_FRONTEND_URL", "http://127.0.0.1:4173").rstrip("/")
API = os.getenv("NEXORA_API_URL", "http://127.0.0.1:8000").rstrip("/")
MAILBOX = Path(os.getenv("NEXORA_MAILBOX", "/tmp/nexora-mailbox.jsonl"))
SHOTS = Path("docs/walkthrough/screenshots")
EMAIL = "market-analyst@northstar.example.com"
PASSWORD = "Nexora-Strong!2026"
CHANGED_PASSWORD = "Nexora-Changed!2026"
RESET_PASSWORD = "Nexora-Final!2026"
ROLE_PASSWORD = "Nexora-Role!2026"
ORG = "Northstar Market Intelligence"
NAME = "Alex Morgan"
COMPETITOR = "Structured Retail Reference"
SOURCE = "Sony Market Pricing"
OFFERING = "Sony WH-1000XM5 Wireless Headphones"
DISCOVERED = "Sony WF-1000XM5 Truly Wireless Noise Canceling Earbuds"
HIGH = "https://cdn.jsdelivr.net/gh/faizansaiyed123/Nexora-backend@main/tests/fixtures/retail-price-high.html"
LOW = "https://cdn.jsdelivr.net/gh/faizansaiyed123/Nexora-backend@main/tests/fixtures/retail-price-low.html"
DISCOVERY = "https://cdn.jsdelivr.net/gh/faizansaiyed123/Nexora-backend@main/tests/fixtures/retail-discovery-product.html"
js_errors: list[str] = []


def shot(page, name):
    SHOTS.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(SHOTS / name), full_page=True, animations="disabled", caret="hide")
    print("Captured", name, flush=True)


def choose(page, label, option):
    field = page.locator("label.field").filter(has_text=label).last
    field.locator("button.select-trigger").click()
    page.get_by_role("option", name=option, exact=True).last.click()


def run_async(coro):
    async def run():
        try:
            return await coro
        finally:
            await engine.dispose()
    return asyncio.run(run())


def token(page):
    value = page.evaluate("() => localStorage.getItem('nexora.access')")
    assert value, "No authenticated access token in browser storage"
    return value


def api_get(page, path, status=200):
    response = page.request.get(API + path, headers={"Authorization": f"Bearer {token(page)}"})
    assert response.status == status, f"GET {path}: {response.status} {response.text()}"
    return response.json()


def mail_items():
    if not MAILBOX.exists():
        return []
    result = []
    for line in MAILBOX.read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
            if item.get("data"):
                result.append(item)
        except (ValueError, AttributeError):
            continue
    return result


def mail_parts(item):
    message = message_from_string(item["data"])
    if message.is_multipart():
        body = "\n".join(
            part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", "replace")
            for part in message.walk()
            if part.get_content_type() == "text/plain" and part.get_payload(decode=True)
        )
    else:
        raw = message.get_payload(decode=True)
        body = raw.decode(message.get_content_charset() or "utf-8", "replace") if raw else str(message.get_payload())
    return str(message.get("Subject", "")), body, [str(x).lower() for x in item.get("rcpt_tos", [])]


def wait_mail(subject, recipient, offset, timeout=40):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        for item in mail_items()[offset:]:
            title, body, recipients = mail_parts(item)
            if subject.lower() in title.lower() and recipient.lower() in recipients:
                return body
        time.sleep(0.25)
    raise AssertionError(f"Expected {subject!r} to reach {recipient}; got {[mail_parts(x)[0] for x in mail_items()[offset:] ]}")


def link_from_mail(body, route):
    match = re.search(rf"https?://[^\s<>]+/{re.escape(route)}\?token=[^\s<>]+", body)
    assert match, f"No /{route} one-time link found in the delivered message"
    return match.group(0).rstrip(".,);")


def login(page, email, password):
    page.get_by_label("Work email").fill(email)
    page.get_by_label("Password").fill(password)
    with page.expect_response(lambda r: r.url.endswith("/v1/auth/login") and r.request.method == "POST") as event:
        page.get_by_role("button", name=re.compile("Sign in")).click()
    assert event.value.status == 200, event.value.text()
    page.get_by_role("heading", name="Dashboard", exact=True).wait_for(timeout=20000)


def logout(page):
    page.locator("button.profile-trigger").click()
    page.get_by_text("Sign out", exact=True).click()
    page.get_by_label("Work email").wait_for()


async def create_roles(client_id, suffix):
    result = {}
    async with AsyncSessionLocal() as session:
        for role in (RoleEnum.ANALYST, RoleEnum.VIEWER):
            email = f"{role.value.lower()}-{suffix}@northstar.example.com"
            session.add(UserModel(
                client_id=client_id, email=email, full_name=f"Northstar {role.value.title()}",
                hashed_password=get_password_hash(ROLE_PASSWORD), role=role,
                is_active=True, email_verified=True,
            ))
            result[role.value] = email
        await session.commit()
    return result


async def check_database(client_id, offering_id, match_id, rule_id):
    async with AsyncSessionLocal() as session:
        observations = list((await session.scalars(
            select(ObservationModel).where(ObservationModel.offering_match_id == match_id)
            .order_by(ObservationModel.observed_at.asc())
        )).all())
        snapshot = await session.scalar(select(SnapshotModel).where(SnapshotModel.offering_match_id == match_id))
        logs = list((await session.scalars(select(AlertLogModel).where(AlertLogModel.alert_rule_id == rule_id))).all())
        offering = await session.get(OfferingModel, offering_id)
        discovered = await session.scalar(select(OfferingModel).where(
            OfferingModel.client_id == client_id, OfferingModel.sku == "WF1000XM5-BLK"
        ))
        jobs = list((await session.scalars(
            select(JobModel).join(SourceModel, SourceModel.id == JobModel.source_id)
            .join(CompetitorModel, CompetitorModel.id == SourceModel.competitor_id)
            .where(CompetitorModel.client_id == client_id)
        )).all())
        outbox = list((await session.scalars(
            select(NotificationOutboxModel).where(NotificationOutboxModel.client_id == client_id)
        )).all())
        assert len(observations) >= 2, [o.observed_price for o in observations]
        assert round(float(observations[0].observed_price), 2) == 399.99
        assert round(float(observations[1].observed_price), 2) == 349.99
        assert all(o.http_status_code == 200 for o in observations[:2])
        assert snapshot is not None and round(float(snapshot.current_price), 2) == 349.99
        assert round(float(snapshot.previous_price), 2) == 399.99
        assert round(float(snapshot.percentage_difference), 2) == -12.5
        assert any(row.title == "Competitor price dropped" and row.is_read for row in logs)
        assert offering is not None and offering.client_id == client_id
        assert discovered is not None and discovered.name == DISCOVERED
        assert sum(job.status.value == "COMPLETED" for job in jobs) >= 2
        assert any(row.status == "SENT" for row in outbox)
        return {
            "database": "PostgreSQL",
            "observations": len(observations),
            "current_price": str(snapshot.current_price),
            "previous_price": str(snapshot.previous_price),
            "change_percent": round(float(snapshot.percentage_difference), 2),
            "alert_events": len(logs),
            "collection_jobs": len(jobs),
            "emails_sent": sum(row.status == "SENT" for row in outbox),
            "discovered_offering": discovered.name,
        }


def main():
    global COMPETITOR, SOURCE
    SHOTS.mkdir(parents=True, exist_ok=True)
    for old in SHOTS.glob("*.png"):
        old.unlink()
    MAILBOX.parent.mkdir(parents=True, exist_ok=True)
    if MAILBOX.exists():
        MAILBOX.unlink()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1440, "height": 1000}, accept_downloads=True)
        page = context.new_page()
        page.set_default_timeout(15000)
        page.on("pageerror", lambda error: js_errors.append(str(error)))
        page.on("dialog", lambda dialog: dialog.accept())

        # Account creation, verified mailbox link and login.
        page.goto(BASE + "/welcome", wait_until="networkidle")
        page.get_by_role("heading", name=re.compile("Understand the market")).wait_for()
        shot(page, "00-public-homepage.png")
        page.get_by_role("link", name="Create workspace", exact=True).click()
        page.get_by_label("Organization name").wait_for()
        shot(page, "01-create-workspace.png")
        page.get_by_label("Organization name").fill(ORG)
        page.get_by_label("Your full name").fill(NAME)
        page.get_by_label("Work email").fill(EMAIL)
        page.get_by_label("Password").fill(PASSWORD)
        before_mail = len(mail_items())
        with page.expect_response(lambda r: r.url.endswith("/v1/auth/register") and r.request.method == "POST") as event:
            page.get_by_role("button", name=re.compile("Create workspace")).click()
        assert event.value.status == 201, event.value.text()
        assert event.value.json()["email_verification_required"] is True
        page.get_by_role("heading", name="Verification required", exact=True).wait_for()
        shot(page, "02-verification-email-sent.png")
        verification_url = link_from_mail(wait_mail("Verify your Nexora account", EMAIL, before_mail), "verify-email")
        assert urlparse(verification_url).path.endswith("/verify-email")
        page.goto(verification_url, wait_until="networkidle")
        shot(page, "03-verify-email.png")
        with page.expect_response(lambda r: "/v1/auth/verify-email" in r.url and r.request.method == "GET") as event:
            page.get_by_role("button", name=re.compile("Verify email")).click()
        assert event.value.status == 200, event.value.text()
        shot(page, "04-email-verified.png")
        page.get_by_role("link", name="Continue to sign in", exact=True).click()
        login(page, EMAIL, PASSWORD)
        shot(page, "05-dashboard.png")
        me = api_get(page, "/v1/auth/me")
        client_id = uuid.UUID(me["client_id"])
        assert me["role"] == "ORG_ADMIN"

        # Competitor add, duplicate-domain rejection and edit.
        page.get_by_role("link", name="Competitors", exact=True).click()
        page.get_by_role("heading", name="Competitors", exact=True).wait_for()
        shot(page, "06-competitors.png")
        page.get_by_role("button", name="Add competitor", exact=True).click()
        page.get_by_label("Name").fill("Sony Official Store")
        page.get_by_label("Domain").fill("cdn.jsdelivr.net")
        shot(page, "07-competitor-form.png")
        with page.expect_response(lambda r: r.url.endswith("/v1/competitors") and r.request.method == "POST") as event:
            page.get_by_role("button", name="Save competitor", exact=True).click()
        assert event.value.status == 201, event.value.text()
        competitor_id = event.value.json()["id"]
        page.get_by_role("button", name="Add competitor", exact=True).click()
        page.get_by_label("Name").fill("Duplicate Store")
        page.get_by_label("Domain").fill("cdn.jsdelivr.net")
        with page.expect_response(lambda r: r.url.endswith("/v1/competitors") and r.request.method == "POST") as event:
            page.get_by_role("button", name="Save competitor", exact=True).click()
        assert event.value.status == 403, event.value.text()
        page.get_by_text("A competitor with this domain already exists.").wait_for()
        shot(page, "08-duplicate-domain-protection.png")
        page.get_by_role("button", name="Cancel", exact=True).click()
        page.locator("tbody tr").filter(has_text="Sony Official Store").first.locator("button").first.click()
        page.get_by_label("Name").fill(COMPETITOR)
        with page.expect_response(lambda r: r.url.endswith(f"/v1/competitors/{competitor_id}") and r.request.method == "PATCH") as event:
            page.get_by_role("button", name="Save competitor", exact=True).click()
        assert event.value.status == 200, event.value.text()
        assert any(row["id"] == competitor_id and row["name"] == COMPETITOR for row in api_get(page, "/v1/competitors"))
        shot(page, "09-competitor-created.png")

        # Source configuration including request pacing, retry policy and selectors.
        page.get_by_role("link", name="Sources", exact=True).click()
        page.get_by_role("button", name="Add source", exact=True).click()
        choose(page, "Competitor", COMPETITOR)
        page.get_by_label("Source name").fill(SOURCE)
        page.get_by_label("Base URL").fill(HIGH)
        choose(page, "Source type", "OFFICIAL_STORE")
        choose(page, "Collection method", "HTTP_FAST")
        shot(page, "10-source-form.png")
        with page.expect_response(lambda r: r.url.endswith("/v1/sources") and r.request.method == "POST") as event:
            page.get_by_role("button", name="Create source", exact=True).click()
        assert event.value.status == 201, event.value.text()
        source_id = event.value.json()["id"]
        page.get_by_title("Configuration", exact=True).click()
        page.get_by_label("Rate / minute").fill("60")
        page.get_by_label("Delay seconds").fill("0.1")
        page.get_by_label("Timeout seconds").fill("25")
        page.get_by_label("Max retries").fill("1")
        page.get_by_label("Custom headers (JSON)").fill('{"Accept-Language":"en-US,en;q=0.9"}')
        page.get_by_label("Extraction selectors (JSON)").fill("{}")
        shot(page, "11-source-configuration.png")
        with page.expect_response(lambda r: r.url.endswith(f"/v1/sources/{source_id}/configuration") and r.request.method == "PATCH") as event:
            page.get_by_role("button", name="Save configuration", exact=True).click()
        assert event.value.status == 200, event.value.text()
        src = api_get(page, f"/v1/sources/{source_id}")
        assert src["configuration"]["rate_limit_rpm"] == 60 and src["configuration"]["max_retries"] == 1
        page.get_by_title("Edit source", exact=True).click()
        SOURCE += " (Structured)"
        page.get_by_label("Source name").fill(SOURCE)
        with page.expect_response(lambda r: r.url.endswith(f"/v1/sources/{source_id}") and r.request.method == "PATCH") as event:
            page.get_by_role("button", name="Save changes", exact=True).click()
        assert event.value.status == 200, event.value.text()
        shot(page, "12-source-configured.png")

        # Catalog entry, detail view, edit, monitoring, dynamic schema and bulk tools.
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
        shot(page, "13-offering-form.png")
        with page.expect_response(lambda r: r.url.endswith("/v1/offerings") and r.request.method == "POST") as event:
            page.get_by_role("button", name="Create offering", exact=True).click()
        assert event.value.status == 201, event.value.text()
        offering_id = event.value.json()["id"]
        page.get_by_text(OFFERING, exact=True).wait_for()
        shot(page, "14-offering-created.png")
        page.locator("tbody tr").filter(has_text=OFFERING).first.get_by_role("button", name=OFFERING, exact=True).click()
        page.get_by_text("CURRENT PRICE", exact=True).wait_for()
        shot(page, "15-offering-detail.png")
        page.keyboard.press("Escape")
        row = page.locator("tbody tr").filter(has_text=OFFERING).first
        row.get_by_title("Edit", exact=True).click()
        page.get_by_label("Current price").fill("429.99")
        with page.expect_response(lambda r: r.url.endswith(f"/v1/offerings/{offering_id}") and r.request.method == "PATCH") as event:
            page.get_by_role("button", name="Save changes", exact=True).click()
        assert event.value.status == 200, event.value.text()
        assert float(api_get(page, f"/v1/offerings/{offering_id}")["current_price"]) == 429.99
        page.locator("tbody tr").filter(has_text=OFFERING).first.get_by_title("Toggle monitoring", exact=True).click()
        assert api_get(page, f"/v1/offerings/{offering_id}")["is_monitored"] is False
        page.locator("tbody tr").filter(has_text=OFFERING).first.get_by_title("Toggle monitoring", exact=True).click()
        assert api_get(page, f"/v1/offerings/{offering_id}")["is_monitored"] is True
        shot(page, "16-offering-monitoring.png")

        page.get_by_role("button", name="Dynamic fields", exact=True).click()
        page.get_by_text("Dynamic field definitions", exact=True).wait_for()
        shot(page, "17-dynamic-fields.png")
        page.get_by_role("button", name="Add field", exact=True).click()
        page.get_by_label("Machine name").fill("review_cycle_months")
        page.get_by_label("Display name").fill("Review Cycle")
        page.get_by_label("Data type").fill("NUMBER")
        page.get_by_label("Unit").fill("months")
        page.get_by_label("Category").fill("Commercial")
        with page.expect_response(lambda r: r.url.endswith("/v1/offerings/fields") and r.request.method == "POST") as event:
            page.get_by_role("button", name="Create field", exact=True).click()
        assert event.value.status == 201, event.value.text()
        shot(page, "18-dynamic-field-created.png")
        field = page.locator("div.list-row").filter(has_text="Review Cycle").last
        with page.expect_response(lambda r: "/v1/offerings/fields/" in r.url and r.request.method == "DELETE") as event:
            field.locator("button.danger-icon").click()
        assert event.value.status == 204, event.value.text()
        page.keyboard.press("Escape")

        page.get_by_role("button", name="Bulk import", exact=True).click()
        bulk = [
            {"name":"Sony ULT WEAR Wireless Headphones","offering_type":"PRODUCT","sku":"ULTWEAR-BLK","current_price":"199.99","currency":"USD","market":"US","url":"https://www.sony.com/electronics/headband-headphones/ult-wear","category":"Electronics > Audio","attributes":{"brand":"Sony","color":"Black"}},
            {"name":"Sony LinkBuds S","offering_type":"PRODUCT","sku":"LINKBUDS-S-BLK","current_price":"199.99","currency":"USD","market":"US","url":"https://www.sony.com/electronics/truly-wireless/linkbuds-s","category":"Electronics > Audio","attributes":{"brand":"Sony","fit":"In-ear"}},
        ]
        page.get_by_label("Offering JSON").fill(json.dumps(bulk))
        shot(page, "19-bulk-import.png")
        with page.expect_response(lambda r: r.url.endswith("/v1/offerings/bulk") and r.request.method == "POST") as event:
            page.get_by_role("button", name="Import offerings", exact=True).click()
        assert event.value.status == 200 and event.value.json()["successful_count"] == 2, event.value.text()
        page.get_by_text("Sony ULT WEAR Wireless Headphones", exact=True).wait_for()
        with page.expect_download(timeout=20000) as event:
            page.get_by_role("button", name="CSV", exact=True).click()
        event.value.save_as("/tmp/nexora-catalog.csv")
        assert Path("/tmp/nexora-catalog.csv").stat().st_size > 0
        with page.expect_download(timeout=20000) as event:
            page.get_by_role("button", name="JSON", exact=True).click()
        event.value.save_as("/tmp/nexora-catalog.json")
        assert Path("/tmp/nexora-catalog.json").stat().st_size > 0
        page.get_by_placeholder("Search name, SKU, category…").fill("Sony ULT WEAR")
        page.get_by_text("Sony ULT WEAR Wireless Headphones", exact=True).wait_for()
        page.get_by_label("Select Sony ULT WEAR Wireless Headphones", exact=True).check()
        with page.expect_response(lambda r: r.url.endswith("/v1/offerings/bulk-archive") and r.request.method == "POST") as event:
            page.get_by_role("button", name="Archive 1", exact=True).click()
        assert event.value.status == 200, event.value.text()
        archived = api_get(page, "/v1/offerings?q=Sony%20ULT%20WEAR&include_archived=true&page=1&page_size=20")
        assert any(row["is_archived"] for row in archived["items"])
        page.get_by_placeholder("Search name, SKU, category…").fill("")
        page.get_by_text(OFFERING, exact=True).wait_for()
        shot(page, "20-bulk-import-export-archive.png")

        # Match creation and two live HTTP collection runs.
        page.get_by_role("link", name="Matches", exact=True).click()
        page.get_by_role("button", name="Add match", exact=True).click()
        choose(page, "Offering", OFFERING)
        choose(page, "Source", SOURCE)
        page.get_by_label("Competitor target URL").fill(HIGH)
        choose(page, "Status", "APPROVED")
        page.get_by_label("Confidence (0–1)").fill("0.98")
        shot(page, "21-match-form.png")
        with page.expect_response(lambda r: r.url.endswith("/v1/offering-matches") and r.request.method == "POST") as event:
            page.get_by_role("button", name="Create match", exact=True).click()
        assert event.value.status == 201, event.value.text()
        match_id = event.value.json()["id"]
        row = page.locator("tbody tr").filter(has_text=OFFERING).first
        shot(page, "22-offering-match.png")
        with page.expect_response(lambda r: "/v1/collections/run" in r.url and r.request.method == "POST") as event:
            row.get_by_title("Run collection", exact=True).click()
        first = event.value
        assert first.status in (200,201), first.text()
        assert first.json()["status"] == "COMPLETED" and first.json()["observation"]["price"] == "399.99", first.json()
        assert len(api_get(page, f"/v1/offerings/{offering_id}/history")) >= 1
        shot(page, "23-first-price-observation.png")

        page.get_by_role("link", name="Alerts", exact=True).click()
        page.get_by_role("button", name="New rule", exact=True).click()
        page.get_by_label("Rule name").fill("Sony retail price drop")
        choose(page, "Alert type", "PERCENTAGE_DROP")
        choose(page, "Offering scope", OFFERING)
        page.get_by_label("Threshold").fill("10")
        page.get_by_label("Cooldown (minutes)").fill("60")
        shot(page, "24-alert-rule-form.png")
        with page.expect_response(lambda r: r.url.endswith("/v1/alerts/rules") and r.request.method == "POST") as event:
            page.get_by_role("button", name="Create rule", exact=True).click()
        assert event.value.status == 201, event.value.text()
        rule_id = event.value.json()["id"]
        shot(page, "25-alert-rule-created.png")

        page.get_by_role("link", name="Matches", exact=True).click()
        page.locator("tbody tr").filter(has_text=OFFERING).first.get_by_title("Edit", exact=True).click()
        page.get_by_label("Competitor target URL").fill(LOW)
        with page.expect_response(lambda r: r.url.endswith(f"/v1/offering-matches/{match_id}") and r.request.method == "PATCH") as event:
            page.get_by_role("button", name="Save changes", exact=True).click()
        assert event.value.status == 200, event.value.text()
        with page.expect_response(lambda r: "/v1/collections/run" in r.url and r.request.method == "POST") as event:
            page.locator("tbody tr").filter(has_text=OFFERING).first.get_by_title("Run collection", exact=True).click()
        second = event.value
        assert second.status in (200,201), second.text()
        payload = second.json()
        assert payload["observation"]["price"] == "349.99", payload
        assert payload["snapshot"]["previous_price"] == "399.99" and payload["snapshot"]["percentage_difference"].startswith("-12.50%"), payload

        page.get_by_role("link", name="Alerts", exact=True).click()
        page.get_by_text("Competitor price dropped", exact=True).wait_for(timeout=20000)
        alert = next((item for item in api_get(page, "/v1/alerts/logs") if item["title"] == "Competitor price dropped"), None)
        assert alert and alert["is_read"] is False
        page.get_by_title("Mark as read", exact=True).click()
        page.get_by_title("Read", exact=True).wait_for()
        assert any(item["id"] == alert["id"] and item["is_read"] for item in api_get(page, "/v1/alerts/logs"))
        shot(page, "26-price-alert-and-read-state.png")
        before_alert_mail = len(mail_items())
        assert run_async(_dispatch_pending_notifications()) >= 1
        alert_body = wait_mail("Nexora Competitive Alert: Competitor price dropped", EMAIL, before_alert_mail)
        assert "Nexora detected a competitive intelligence event" in alert_body

        page.get_by_role("link", name="Jobs", exact=True).click()
        page.get_by_text("ON DEMAND REFRESH", exact=False).wait_for(timeout=20000)
        shot(page, "27-collection-jobs.png")
        page.get_by_role("button", name="Details", exact=True).first.click()
        page.get_by_text("Job ID", exact=True).wait_for()
        shot(page, "28-collection-job-detail.png")
        page.keyboard.press("Escape")

        # Discovery blocks private addresses and performs real structured extraction/upsert.
        page.get_by_role("link", name="Discovery", exact=True).click()
        page.get_by_label("Website URL").fill("http://127.0.0.1:8000/v1/health")
        page.get_by_label("Max pages").fill("1")
        with page.expect_response(lambda r: r.url.endswith("/v1/discovery/run") and r.request.method == "POST") as event:
            page.get_by_role("button", name="Run discovery", exact=True).click()
        assert event.value.status == 422, event.value.text()
        shot(page, "29-private-target-blocked.png")
        page.get_by_label("Website URL").fill(DISCOVERY)
        choose(page, "Default type", "PRODUCT")
        with page.expect_response(lambda r: r.url.endswith("/v1/discovery/run") and r.request.method == "POST") as event:
            page.get_by_role("button", name="Run discovery", exact=True).click()
        result = event.value
        assert result.status == 200, result.text()
        job = result.json()
        assert job["status"] == "COMPLETED" and job["created_offerings_count"] == 1, job
        assert job["items"][0]["name"] == DISCOVERED, job
        page.get_by_text(DISCOVERED, exact=True).wait_for(timeout=15000)
        shot(page, "30-discovery-created.png")
        assert api_get(page, f"/v1/discovery/jobs/{job['job_id']}")["items"][0]["sku"] == "WF1000XM5-BLK"
        with page.expect_response(lambda r: r.url.endswith("/v1/discovery/run") and r.request.method == "POST") as event:
            page.get_by_role("button", name="Run discovery", exact=True).click()
        again = event.value
        assert again.status == 200 and again.json()["created_offerings_count"] == 0 and again.json()["updated_offerings_count"] == 1, again.text()
        catalog = api_get(page, "/v1/offerings?q=Sony%20WF-1000XM5&page=1&page_size=20")
        assert sum(item["sku"] == "WF1000XM5-BLK" for item in catalog["items"]) == 1
        shot(page, "31-discovery-update-history.png")

        # Profile update and password change/reset through actual email links.
        page.locator("button.profile-trigger").click()
        page.get_by_role("button", name="Account settings", exact=True).click()
        page.get_by_label("Company name").fill("Northstar Analytics")
        page.get_by_label("Country").fill("US")
        page.get_by_label("Default currency").fill("USD")
        page.get_by_label("Market").fill("US")
        page.get_by_label("Industry").fill("Consumer Electronics")
        page.get_by_label("Timezone").fill("America/New_York")
        shot(page, "32-workspace-settings.png")
        with page.expect_response(lambda r: r.url.endswith("/v1/auth/profile") and r.request.method == "PATCH") as event:
            page.get_by_role("button", name="Save profile", exact=True).click()
        assert event.value.status == 200 and api_get(page, "/v1/auth/profile")["company_name"] == "Northstar Analytics"
        shot(page, "33-workspace-profile-updated.png")
        page.get_by_label("Current password").fill(PASSWORD)
        page.get_by_label("New password").fill(CHANGED_PASSWORD)
        with page.expect_response(lambda r: r.url.endswith("/v1/auth/change-password") and r.request.method == "POST") as event:
            page.get_by_role("button", name="Update password", exact=True).click()
        assert event.value.status == 200, event.value.text()
        assert page.request.post(API + "/v1/auth/login", json={"email":EMAIL,"password":PASSWORD}).status == 401
        assert page.request.post(API + "/v1/auth/login", json={"email":EMAIL,"password":CHANGED_PASSWORD}).status == 200
        shot(page, "34-password-change.png")
        logout(page)
        page.get_by_role("link", name="Forgot password?", exact=True).click()
        page.get_by_label("Work email").fill(EMAIL)
        before_reset_mail = len(mail_items())
        with page.expect_response(lambda r: r.url.endswith("/v1/auth/forgot-password") and r.request.method == "POST") as event:
            page.get_by_role("button", name="Send reset link", exact=True).click()
        assert event.value.status == 200, event.value.text()
        shot(page, "35-password-reset-requested.png")
        reset_url = link_from_mail(wait_mail("Reset your Nexora password", EMAIL, before_reset_mail), "reset-password")
        page.goto(reset_url, wait_until="networkidle")
        page.get_by_label("New password").wait_for()
        shot(page, "36-password-reset-form.png")
        page.get_by_label("New password").fill(RESET_PASSWORD)
        with page.expect_response(lambda r: r.url.endswith("/v1/auth/reset-password") and r.request.method == "POST") as event:
            page.get_by_role("button", name="Update password", exact=True).click()
        assert event.value.status == 200, event.value.text()
        page.get_by_role("heading", name="Password updated", exact=True).wait_for()
        shot(page, "37-password-reset-complete.png")
        page.get_by_role("link", name="Continue to sign in", exact=True).click()
        login(page, EMAIL, RESET_PASSWORD)
        shot(page, "38-dashboard-after-recovery.png")

        # Assert the persisted records by opening PostgreSQL directly, not just UI messages.
        evidence = run_async(check_database(client_id, uuid.UUID(offering_id), uuid.UUID(match_id), uuid.UUID(rule_id)))
        Path("artifacts/e2e").mkdir(parents=True, exist_ok=True)
        Path("artifacts/e2e/database-evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
        print("Direct PostgreSQL read-back:", json.dumps(evidence, sort_keys=True), flush=True)

        roles = run_async(create_roles(client_id, uuid.uuid4().hex[:8]))
        logout(page)
        login(page, roles["ANALYST"], ROLE_PASSWORD)
        page.get_by_role("link", name="Competitors", exact=True).click()
        assert page.get_by_role("button", name="Add competitor", exact=True).count() == 0
        denied = page.request.post(API + "/v1/competitors", headers={"Authorization":f"Bearer {token(page)}"}, json={"name":"Denied","domain":"analyst-forbidden.example"})
        assert denied.status == 403, denied.text()
        page.get_by_role("link", name="Discovery", exact=True).click()
        assert page.get_by_role("button", name="Run discovery", exact=True).is_visible()
        shot(page, "39-analyst-access.png")

        logout(page)
        login(page, roles["VIEWER"], ROLE_PASSWORD)
        page.get_by_role("link", name="Offerings", exact=True).click()
        assert page.get_by_role("button", name="Add offering", exact=True).count() == 0
        assert page.get_by_role("button", name="Bulk import", exact=True).count() == 0
        assert page.get_by_role("button", name="Dynamic fields", exact=True).count() == 0
        assert page.request.get(API + "/v1/offerings", headers={"Authorization":f"Bearer {token(page)}"}).status == 200
        denied = page.request.post(API + "/v1/competitors", headers={"Authorization":f"Bearer {token(page)}"}, json={"name":"Denied","domain":"viewer-forbidden.example"})
        assert denied.status == 403, denied.text()
        shot(page, "40-viewer-read-only-access.png")

        mobile = context.new_page()
        mobile.set_viewport_size({"width":390,"height":844})
        mobile.goto(BASE + "/welcome", wait_until="networkidle")
        dimensions = mobile.evaluate("() => ({viewport:document.documentElement.clientWidth,content:document.documentElement.scrollWidth})")
        assert dimensions["content"] <= dimensions["viewport"], dimensions
        shot(mobile, "41-mobile-homepage.png")
        assert not js_errors, "Browser JavaScript errors: " + " | ".join(js_errors)
        images = list(SHOTS.glob("*.png"))
        assert len(images) == 42, f"Expected 42 screenshots, found {len(images)}"
        print(f"Complete UI-to-API-to-PostgreSQL journey finished with {len(images)} screenshots.", flush=True)
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
